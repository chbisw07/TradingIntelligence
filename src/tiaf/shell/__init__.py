"""Command-first local engineering Shell over the governed TIAF facade."""

from .cli import ShellBootstrapConfig, load_bootstrap
from .commands import ParsedCommand, ShellOutputMode
from .dispatcher import DispatchOutcome, ShellDispatcher
from .errors import ShellError, ShellErrorCode, ShellErrorRecord
from .parser import parse_line, parse_tokens
from .renderers import render, render_error
from .runtime import ShellRunResult, ShellRuntime, run_repl
from .session import SessionDefaults, ShellSession

__all__ = [
    "DispatchOutcome",
    "ParsedCommand",
    "SessionDefaults",
    "ShellBootstrapConfig",
    "ShellDispatcher",
    "ShellError",
    "ShellErrorCode",
    "ShellErrorRecord",
    "ShellOutputMode",
    "ShellRunResult",
    "ShellRuntime",
    "ShellSession",
    "load_bootstrap",
    "parse_line",
    "parse_tokens",
    "render",
    "render_error",
    "run_repl",
]
