"""Read-only stdio MCP connector for the Yahoo/yfinance provider adapter."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from queue import Queue
from typing import Final, TextIO

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult
from pydantic import JsonValue

YAHOO_READ_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "yfinance_get_earnings_dates",
        "yfinance_get_stock_financials",
        "yfinance_get_stock_info",
        "yfinance_get_stock_news",
        "yfinance_get_stock_recommendations",
    }
)


class YahooConnectorError(RuntimeError):
    """Base for sanitized Yahoo connector failures."""


class YahooProcessLaunchError(YahooConnectorError):
    """The local Yahoo MCP process could not be launched."""


class YahooInitializationError(YahooConnectorError):
    """The Yahoo MCP session could not initialize."""


class YahooToolNotAllowedError(YahooConnectorError):
    """A caller attempted to escape the Yahoo read-only allowlist."""


class YahooSchemaDriftError(YahooConnectorError):
    """An allowlisted Yahoo tool is no longer advertised."""


class YahooCallTimeoutError(TimeoutError, YahooConnectorError):
    """A bounded Yahoo MCP call exceeded its timeout."""


class YahooProviderCallError(YahooConnectorError):
    """The MCP layer rejected a Yahoo tool invocation."""


class YahooMalformedResultError(YahooConnectorError):
    """A Yahoo MCP result could not be represented as JSON/text."""


class YahooConnectionClosedError(YahooConnectorError):
    """The reusable Yahoo MCP connection closed unexpectedly."""


@dataclass(slots=True)
class _PendingCall:
    tool_name: str
    arguments: dict[str, JsonValue]
    completed: threading.Event
    response: Mapping[str, object] | None = None
    error: BaseException | None = None


class YahooMcpClient:
    """Reusable synchronous facade over one asynchronous Yahoo MCP session."""

    def __init__(
        self,
        *,
        command: str = "uvx",
        args: tuple[str, ...] = (
            "--from",
            "git+https://github.com/mobatmedia/yfinance-mcp",
            "yfinance-mcp",
        ),
        startup_timeout_seconds: float = 60.0,
        call_timeout_seconds: float = 45.0,
    ) -> None:
        if startup_timeout_seconds <= 0 or call_timeout_seconds <= 0:
            raise ValueError("Yahoo MCP timeouts must be positive")
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

    @property
    def server_name(self) -> str | None:
        return self._server_name

    @property
    def server_version(self) -> str | None:
        return self._server_version

    @property
    def advertised_tools(self) -> tuple[str, ...]:
        return tuple(sorted(self._advertised_tools))

    def __enter__(self) -> YahooMcpClient:
        self.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def start(self) -> None:
        """Start and initialize the reusable MCP session once."""
        with self._lifecycle_lock:
            if self._closed:
                raise YahooConnectionClosedError("Yahoo MCP client is closed")
            if self._thread is None:
                if shutil.which(self._command) is None:
                    raise YahooProcessLaunchError("Yahoo MCP command is not installed")
                self._thread = threading.Thread(
                    target=self._worker_main,
                    name="tiaf-yahoo-mcp",
                    daemon=True,
                )
                self._thread.start()
        if not self._ready.wait(self._startup_timeout_seconds + 1.0):
            raise YahooInitializationError("Yahoo MCP initialization timed out")
        if self._startup_error is not None:
            raise self._startup_error from None
        if self._fatal_error is not None:
            raise self._fatal_error from None
        if self._thread is None or not self._thread.is_alive():
            raise YahooConnectionClosedError("Yahoo MCP connection is not running")

    def close(self) -> None:
        """Close the MCP subprocess without exposing child output."""
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
            raise YahooConnectionClosedError("Yahoo MCP connection did not close cleanly")

    def call_tool(
        self, tool_name: str, arguments: Mapping[str, JsonValue]
    ) -> Mapping[str, object]:
        """Invoke one advertised Yahoo read tool."""
        if tool_name not in YAHOO_READ_TOOLS:
            raise YahooToolNotAllowedError("Yahoo tool is outside the read-only allowlist")
        self.start()
        if tool_name not in self._advertised_tools:
            raise YahooSchemaDriftError("Allowlisted Yahoo tool is not advertised")
        pending = _PendingCall(tool_name, dict(arguments), threading.Event())
        self._requests.put(pending)
        if not pending.completed.wait(self._call_timeout_seconds + 1.0):
            raise YahooCallTimeoutError("Yahoo MCP tool call timed out")
        if pending.error is not None:
            raise pending.error from None
        if pending.response is None:
            raise YahooMalformedResultError("Yahoo MCP returned no provider-native result")
        return pending.response

    def _worker_main(self) -> None:
        try:
            asyncio.run(self._serve())
        except BaseException:
            error = YahooConnectionClosedError("Yahoo MCP connection closed unexpectedly")
            if not self._ready.is_set():
                self._startup_error = YahooInitializationError(
                    "Yahoo MCP initialization failed"
                )
                self._ready.set()
            self._fatal_error = error
            self._fail_pending(error)
        finally:
            self._stopped.set()

    async def _serve(self) -> None:
        parameters = StdioServerParameters(command=self._command, args=list(self._args))
        try:
            with open(os.devnull, "w", encoding="utf-8") as errlog:
                await self._serve_session(parameters, errlog)
        except BaseException:
            if not self._ready.is_set():
                self._startup_error = YahooInitializationError(
                    "Yahoo MCP initialization failed"
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
            pending.response = _provider_native_payload(result)
        except TimeoutError:
            pending.error = YahooCallTimeoutError("Yahoo MCP tool call timed out")
        except YahooConnectorError as exc:
            pending.error = exc
        except BaseException:
            pending.error = YahooProviderCallError("Yahoo MCP tool invocation failed")
        finally:
            pending.completed.set()

    def _fail_pending(self, error: BaseException) -> None:
        while not self._requests.empty():
            pending = self._requests.get_nowait()
            if pending is not None:
                pending.error = error
                pending.completed.set()


def _provider_native_payload(result: CallToolResult) -> Mapping[str, object]:
    """Convert an SDK result without adding canonical interpretation."""
    content: list[dict[str, str]] = []
    parsed_text: Mapping[str, object] | list[object] | None = None
    for block in result.content:
        if block.type != "text":
            continue
        content.append({"type": "text", "text": block.text})
        if parsed_text is None:
            try:
                candidate = json.loads(block.text)
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, (dict, list)):
                parsed_text = candidate
    native_structured = result.structuredContent
    structured: Mapping[str, object] | list[object] | None = (
        native_structured if isinstance(native_structured, (Mapping, list)) else None
    )
    if structured is None:
        structured = parsed_text
    if structured is None and result.isError and content:
        structured = {"error": content[0]["text"]}
    if structured is None and not content:
        raise YahooMalformedResultError("Yahoo MCP result has no JSON or text content")
    response: dict[str, object] = {"isError": result.isError, "content": content}
    if structured is not None:
        response["structuredContent"] = structured
    return response
