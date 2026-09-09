"""Read-only stdio MCP connector for the Tapetide provider adapter."""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from typing import Final, TextIO

from dotenv import dotenv_values, find_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult
from pydantic import JsonValue

TAPETIDE_READ_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "get_company_profile",
        "get_credit_ratings",
        "get_earnings_call_summary",
        "get_financials",
        "get_forecasts",
        "get_index_membership_asof",
        "get_promoter_pledge",
        "get_shareholding",
        "get_stock_events",
    }
)


class TapetideConnectorError(RuntimeError):
    """Base for sanitized connector failures safe to cross the adapter boundary."""


class TapetideCredentialError(TapetideConnectorError):
    """The explicitly requested live connector has no usable credential."""


class TapetideProcessLaunchError(TapetideConnectorError):
    """The local MCP stdio process could not be launched."""


class TapetideInitializationError(TapetideConnectorError):
    """The MCP session could not initialize or advertise its tools."""


class TapetideToolNotAllowedError(TapetideConnectorError):
    """A caller attempted to escape the connector's read-only allowlist."""


class TapetideSchemaDriftError(TapetideConnectorError):
    """An allowlisted tool is no longer advertised by the live server."""


class TapetideCallTimeoutError(TimeoutError, TapetideConnectorError):
    """A bounded MCP call exceeded its configured timeout."""


class TapetideProviderCallError(TapetideConnectorError):
    """The MCP layer rejected a tool invocation before returning a tool result."""


class TapetideMalformedResultError(TapetideConnectorError):
    """A tool result could not be represented as provider-native JSON/text."""


class TapetideConnectionClosedError(TapetideConnectorError):
    """The reusable MCP connection closed unexpectedly or did not stop cleanly."""


@dataclass(slots=True)
class _PendingCall:
    tool_name: str
    arguments: dict[str, JsonValue]
    completed: threading.Event
    response: Mapping[str, object] | None = None
    error: BaseException | None = None


class TapetideMcpClient:
    """Synchronous adapter client backed by one reusable asynchronous MCP session.

    The existing provider runtime is synchronous. A single private worker owns the
    asynchronous stdio lifecycle so initialization, calls, and shutdown all occur
    in the same task. Normal calls are serialized through that worker.
    """

    def __init__(
        self,
        token: str,
        *,
        debug: str | None = None,
        mcp_url: str | None = None,
        command: str = "npx",
        args: tuple[str, ...] = ("-y", "tapetide-mcp"),
        startup_timeout_seconds: float = 45.0,
        call_timeout_seconds: float = 30.0,
    ) -> None:
        if not token.strip():
            raise TapetideCredentialError("TAPETIDE_TOKEN is required for live Tapetide access")
        if startup_timeout_seconds <= 0 or call_timeout_seconds <= 0:
            raise ValueError("Tapetide MCP timeouts must be positive")
        self._token = token
        self._debug = debug
        self._mcp_url = mcp_url
        self._command = command
        self._args = args
        self._startup_timeout_seconds = startup_timeout_seconds
        self._call_timeout_seconds = call_timeout_seconds
        self._requests: Queue[_PendingCall | None] = Queue()
        self._ready = threading.Event()
        self._stopped = threading.Event()
        self._lifecycle_lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._startup_error: BaseException | None = None
        self._fatal_error: BaseException | None = None
        self._advertised_tools: frozenset[str] = frozenset()
        self._server_name: str | None = None
        self._server_version: str | None = None
        self._closed = False

    @classmethod
    def from_environment(
        cls,
        *,
        environment: Mapping[str, str] | None = None,
        env_file: str | Path | None = None,
        load_repository_env: bool = True,
        startup_timeout_seconds: float = 45.0,
        call_timeout_seconds: float = 30.0,
    ) -> TapetideMcpClient:
        """Construct from process settings, falling back to the repository `.env`."""
        values = dict(os.environ if environment is None else environment)
        if load_repository_env and not values.get("TAPETIDE_TOKEN"):
            dotenv_path = str(env_file) if env_file is not None else find_dotenv(usecwd=True)
            if dotenv_path:
                file_values = dotenv_values(dotenv_path)
                for name in ("TAPETIDE_TOKEN", "TAPETIDE_DEBUG", "TAPETIDE_MCP_URL"):
                    value = file_values.get(name)
                    if value is not None:
                        values.setdefault(name, value)
        return cls(
            values.get("TAPETIDE_TOKEN", ""),
            debug=values.get("TAPETIDE_DEBUG") or None,
            mcp_url=values.get("TAPETIDE_MCP_URL") or None,
            startup_timeout_seconds=startup_timeout_seconds,
            call_timeout_seconds=call_timeout_seconds,
        )

    @property
    def server_name(self) -> str | None:
        return self._server_name

    @property
    def server_version(self) -> str | None:
        return self._server_version

    @property
    def advertised_tools(self) -> tuple[str, ...]:
        return tuple(sorted(self._advertised_tools))

    def __enter__(self) -> TapetideMcpClient:
        self.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def start(self) -> None:
        """Start and initialize the reusable MCP session once."""
        with self._lifecycle_lock:
            if self._closed:
                raise TapetideConnectionClosedError("Tapetide MCP client is closed")
            if self._thread is None:
                if shutil.which(self._command) is None:
                    raise TapetideProcessLaunchError(
                        "Tapetide MCP command is not installed"
                    )
                self._thread = threading.Thread(
                    target=self._worker_main,
                    name="tiaf-tapetide-mcp",
                    daemon=True,
                )
                self._thread.start()
        if not self._ready.wait(self._startup_timeout_seconds + 1.0):
            raise TapetideInitializationError("Tapetide MCP initialization timed out")
        if self._startup_error is not None:
            raise self._startup_error from None
        if self._fatal_error is not None:
            raise self._fatal_error from None
        if self._thread is None or not self._thread.is_alive():
            raise TapetideConnectionClosedError("Tapetide MCP connection is not running")

    def close(self) -> None:
        """Close the MCP session and its subprocess without exposing child stderr."""
        with self._lifecycle_lock:
            if self._closed:
                return
            self._closed = True
            thread = self._thread
            if thread is None:
                return
            self._requests.put(None)
        thread.join(self._call_timeout_seconds + 5.0)
        if thread.is_alive():
            raise TapetideConnectionClosedError("Tapetide MCP connection did not close cleanly")

    def call_tool(
        self, tool_name: str, arguments: Mapping[str, JsonValue]
    ) -> Mapping[str, object]:
        """Invoke one advertised read tool and return provider-native content."""
        if tool_name not in TAPETIDE_READ_TOOLS:
            raise TapetideToolNotAllowedError("Tapetide tool is outside the read-only allowlist")
        self.start()
        if tool_name not in self._advertised_tools:
            raise TapetideSchemaDriftError("Allowlisted Tapetide tool is not advertised")
        pending = _PendingCall(tool_name, dict(arguments), threading.Event())
        self._requests.put(pending)
        if not pending.completed.wait(self._call_timeout_seconds + 1.0):
            raise TapetideCallTimeoutError("Tapetide MCP tool call timed out")
        if pending.error is not None:
            raise pending.error from None
        if pending.response is None:
            raise TapetideMalformedResultError("Tapetide MCP returned no provider-native result")
        return pending.response

    def _worker_main(self) -> None:
        try:
            asyncio.run(self._serve())
        except BaseException:
            error = TapetideConnectionClosedError("Tapetide MCP connection closed unexpectedly")
            if not self._ready.is_set():
                self._startup_error = TapetideInitializationError(
                    "Tapetide MCP initialization failed"
                )
                self._ready.set()
            self._fatal_error = error
            self._fail_pending(error)
        finally:
            self._stopped.set()

    async def _serve(self) -> None:
        child_env = {"TAPETIDE_TOKEN": self._token}
        if self._debug is not None:
            child_env["TAPETIDE_DEBUG"] = self._debug
        if self._mcp_url is not None:
            child_env["TAPETIDE_MCP_URL"] = self._mcp_url
        parameters = StdioServerParameters(
            command=self._command,
            args=list(self._args),
            env=child_env,
        )
        try:
            with open(os.devnull, "w", encoding="utf-8") as errlog:
                await self._serve_session(parameters, errlog)
        except BaseException:
            if not self._ready.is_set():
                self._startup_error = TapetideInitializationError(
                    "Tapetide MCP initialization failed"
                )
                self._ready.set()
                return
            raise

    async def _serve_session(
        self, parameters: StdioServerParameters, errlog: TextIO
    ) -> None:
        async with stdio_client(parameters, errlog=errlog) as streams:
            async with ClientSession(*streams) as session:
                initialized = await asyncio.wait_for(
                    session.initialize(), timeout=self._startup_timeout_seconds
                )
                listed = await asyncio.wait_for(
                    session.list_tools(), timeout=self._startup_timeout_seconds
                )
                self._server_name = initialized.serverInfo.name
                self._server_version = initialized.serverInfo.version
                self._advertised_tools = frozenset(tool.name for tool in listed.tools)
                self._ready.set()
                while True:
                    pending = await asyncio.to_thread(self._requests.get)
                    if pending is None:
                        return
                    await self._perform_call(session, pending)

    async def _perform_call(self, session: ClientSession, pending: _PendingCall) -> None:
        try:
            result = await asyncio.wait_for(
                session.call_tool(pending.tool_name, arguments=pending.arguments),
                timeout=self._call_timeout_seconds,
            )
            pending.response = _provider_native_payload(result, secret=self._token)
        except TimeoutError:
            pending.error = TapetideCallTimeoutError("Tapetide MCP tool call timed out")
        except TapetideConnectorError as exc:
            pending.error = exc
        except BaseException:
            pending.error = TapetideProviderCallError("Tapetide MCP tool invocation failed")
        finally:
            pending.completed.set()

    def _fail_pending(self, error: BaseException) -> None:
        while not self._requests.empty():
            pending = self._requests.get_nowait()
            if pending is not None:
                pending.error = error
                pending.completed.set()


def _provider_native_payload(
    result: CallToolResult, *, secret: str | None = None
) -> Mapping[str, object]:
    """Convert an SDK result without adding any canonical interpretation."""
    content: list[dict[str, str]] = []
    parsed_text: Mapping[str, object] | list[object] | None = None
    for block in result.content:
        if block.type != "text":
            continue
        safe_text = _redact_provider_text(block.text, secret)
        content.append({"type": "text", "text": safe_text})
        if parsed_text is None:
            try:
                candidate = json.loads(safe_text)
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, (dict, list)):
                parsed_text = candidate
    safe_structured = _redact_provider_value(result.structuredContent, secret)
    structured = (
        safe_structured
        if isinstance(safe_structured, (Mapping, list))
        else None
    )
    if structured is None:
        structured = parsed_text
    if structured is None and result.isError and content:
        structured = {"error": content[0]["text"]}
    if structured is None and not content:
        raise TapetideMalformedResultError("Tapetide MCP result has no JSON or text content")
    response: dict[str, object] = {"isError": result.isError, "content": content}
    if structured is not None:
        response["structuredContent"] = structured
    return response


def _redact_provider_value(value: object, secret: str | None) -> object:
    if isinstance(value, str):
        return _redact_provider_text(value, secret)
    if isinstance(value, Mapping):
        return {
            str(key): _redact_provider_value(child, secret)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [_redact_provider_value(child, secret) for child in value]
    return value


def _redact_provider_text(value: str, secret: str | None) -> str:
    redacted = value.replace(secret, "[REDACTED]") if secret else value
    redacted = re.sub(
        r"(?i)(TAPETIDE_TOKEN\s*[:=]\s*)[^\s,;]+", r"\1[REDACTED]", redacted
    )
    return re.sub(
        r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+",
        r"\1[REDACTED]",
        redacted,
    )
