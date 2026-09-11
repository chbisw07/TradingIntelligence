"""Console/bootstrap adapter for the local TI Shell."""

import json
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from tiaf.facade import TrustedFacadeConfig, create_local_facade

from .commands import HelpCommand, ShellOutputMode
from .dispatcher import HELP_TEXT, ShellDispatcher
from .errors import ShellError, ShellErrorCode, shell_error
from .parser import parse_tokens
from .renderers import render_error
from .runtime import ShellRuntime, run_repl
from .session import SessionDefaults

_MAX_BOOTSTRAP_BYTES = 64 * 1024 * 1024


class ShellBootstrapConfig(BaseModel):
    """Frozen trusted local composition input; never accepted as a Shell command."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    facade: TrustedFacadeConfig
    caller_id: str
    baseline_request_root: str
    defaults: SessionDefaults = Field(default_factory=SessionDefaults)
    history_limit: int = Field(default=32, ge=1, le=64)


def load_bootstrap(path: Path) -> ShellBootstrapConfig:
    try:
        resolved = path.resolve(strict=True)
        if not resolved.is_file() or resolved.stat().st_size > _MAX_BOOTSTRAP_BYTES:
            raise OSError
        content = resolved.read_text(encoding="utf-8")
        return ShellBootstrapConfig.model_validate_json(content)
    except (OSError, UnicodeError, ValidationError) as exc:
        raise shell_error(
            ShellErrorCode.INPUT_SAFETY_ERROR,
            "Shell bootstrap failed safe validation",
        ) from exc


def _extract_bootstrap(argv: list[str]) -> tuple[Path | None, bool, list[str]]:
    config_path: Path | None = None
    version = False
    remaining: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--config":
            if config_path is not None or index + 1 >= len(argv):
                raise shell_error(ShellErrorCode.SYNTAX_ERROR, "--config requires one path")
            config_path = Path(argv[index + 1])
            index += 2
            continue
        if token == "--version":
            version = True
            index += 1
            continue
        if token.startswith("--config="):
            raise shell_error(ShellErrorCode.SYNTAX_ERROR, "use '--config PATH' syntax")
        remaining.append(token)
        index += 1
    return config_path, version, remaining


def _json_local_help() -> str:
    return json.dumps(
        {
            "schema_id": "tiaf.shell.local-result",
            "schema_version": "1.0",
            "command": "help",
            "message": HELP_TEXT,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _write(stream: Any, value: str) -> None:
    stream.write(value)
    if not value.endswith("\n"):
        stream.write("\n")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        config_path, version, command_tokens = _extract_bootstrap(args)
        if version:
            print("TIAF TI Shell 0.1 (package 0.1.0; output schema 1.0)")
            return 0
        parsed = parse_tokens(command_tokens)
        if config_path is None and isinstance(parsed.command, HelpCommand):
            if parsed.output_override is ShellOutputMode.JSON:
                print(_json_local_help())
            else:
                print(HELP_TEXT, end="")
            return 0
        if config_path is None:
            raise shell_error(
                ShellErrorCode.CONTEXT_ERROR,
                "--config is required for REPL or capability execution",
            )
        bootstrap = load_bootstrap(config_path)
        owner = create_local_facade(bootstrap.facade)
        try:
            root = Path(bootstrap.baseline_request_root)
            if not root.is_absolute():
                root = config_path.resolve().parent / root
            dispatcher = ShellDispatcher(
                owner.client(bootstrap.caller_id),
                baseline_request_root=root,
                defaults=bootstrap.defaults,
                history_limit=bootstrap.history_limit,
            )
            runtime = ShellRuntime(dispatcher)
            if not command_tokens:
                return run_repl(
                    runtime,
                    input_stream=sys.stdin,
                    output_stream=sys.stdout,
                    error_stream=sys.stderr,
                )
            result = runtime.execute_tokens_from_parsed(parsed)
            if result.stdout:
                _write(sys.stdout, result.stdout)
            if result.stderr:
                _write(sys.stderr, result.stderr)
            return result.exit_code
        finally:
            owner.shutdown()
    except ShellError as exc:
        json_mode = "--output" in args and "json" in args
        rendered = render_error(exc, json_mode=json_mode)
        _write(sys.stdout if json_mode else sys.stderr, rendered)
        return exc.exit_code
    except Exception:
        fallback = shell_error(ShellErrorCode.EXECUTION_FAILED, "Shell startup failed safely")
        _write(sys.stderr, render_error(fallback, json_mode=False))
        return fallback.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
