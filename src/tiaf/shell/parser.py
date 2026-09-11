"""Small explicit argparse/shlex grammar for TI Shell v0.1."""

import argparse
import re
import shlex
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Never

from pydantic import TypeAdapter, ValidationError

from tiaf.context import AnalysisPurpose
from tiaf.contracts import Horizon
from tiaf.contracts.common import TiafDateTime

from .commands import (
    CapabilitiesDescribeCommand,
    CapabilitiesListCommand,
    ClearContextCommand,
    ContextField,
    ExitCommand,
    ExplainLastCommand,
    HelpCommand,
    LastView,
    OperationCommand,
    OperationKind,
    ParsedCommand,
    RefreshLastCommand,
    ScopeOptions,
    SetCommand,
    ShellCommand,
    ShellOutputMode,
    ShowContextCommand,
    ShowLastCommand,
    TraceLastCommand,
    TraceView,
    UnsetCommand,
    UseCommand,
)
from .errors import ShellError, ShellErrorCode, shell_error

_DATETIME_ADAPTER = TypeAdapter(TiafDateTime)


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> Never:
        raise shell_error(ShellErrorCode.SYNTAX_ERROR, message)


def _enum_value(enum_type: type[AnalysisPurpose], value: str) -> AnalysisPurpose:
    try:
        return enum_type(value.upper())
    except ValueError as exc:
        choices = ", ".join(item.value.casefold() for item in enum_type)
        raise argparse.ArgumentTypeError(f"expected one of: {choices}") from exc


def _objective(value: str) -> AnalysisPurpose:
    return _enum_value(AnalysisPurpose, value)


def _horizon(value: str) -> Horizon:
    if not value.strip():
        raise argparse.ArgumentTypeError("horizon must not be empty")
    return Horizon(label=value.strip().upper())


def _as_of(value: str) -> datetime:
    try:
        return _DATETIME_ADAPTER.validate_python(value)
    except ValidationError as exc:
        raise argparse.ArgumentTypeError("as-of must be an aware ISO-8601 timestamp") from exc


def _symbol(value: str) -> str:
    symbol = value.strip().upper()
    if re.fullmatch(r"[A-Z0-9][A-Z0-9_&-]*", symbol) is None:
        raise argparse.ArgumentTypeError("subject must be a provider-neutral symbol")
    return symbol


def _safe_token(value: str) -> str:
    token = value.strip()
    if (
        not token
        or "://" in token
        or "/" in token
        or "\\" in token
        or token.startswith(("~", ".."))
    ):
        raise argparse.ArgumentTypeError("expected a non-path logical identifier")
    return token


def _add_scope(parser: argparse.ArgumentParser, *, baseline: bool = False) -> None:
    parser.add_argument("--subject", type=_symbol)
    parser.add_argument("--objective", type=_objective)
    parser.add_argument("--horizon", type=_horizon)
    parser.add_argument("--as-of", type=_as_of)
    parser.add_argument("--profile-ref", type=_safe_token)
    parser.add_argument("--authority-ref", type=_safe_token)
    parser.add_argument("--position-context-ref", type=_safe_token)
    if baseline:
        parser.add_argument("--request-file", required=True, type=Path)
    else:
        parser.add_argument("--artifact-ref", required=True, type=_safe_token)


def _build_parser() -> _Parser:
    parser = _Parser(prog="ti", add_help=False, allow_abbrev=False, exit_on_error=False)
    parser.add_argument("--output", choices=tuple(ShellOutputMode))
    commands = parser.add_subparsers(dest="verb", required=True)

    help_parser = commands.add_parser("help", add_help=False, allow_abbrev=False)
    help_parser.add_argument("topic", nargs="?")

    use = commands.add_parser("use", add_help=False, allow_abbrev=False)
    use.add_argument("subject", type=_symbol)

    set_parser = commands.add_parser("set", add_help=False, allow_abbrev=False)
    set_parser.add_argument("field", choices=tuple(ContextField))
    set_parser.add_argument("value")

    unset = commands.add_parser("unset", add_help=False, allow_abbrev=False)
    unset.add_argument("field", choices=tuple(ContextField))

    clear = commands.add_parser("clear", add_help=False, allow_abbrev=False)
    clear.add_argument("target", choices=("context",))

    show = commands.add_parser("show", add_help=False, allow_abbrev=False)
    show_sub = show.add_subparsers(dest="show_target", required=True)
    show_sub.add_parser("context", add_help=False, allow_abbrev=False)
    last = show_sub.add_parser("last", add_help=False, allow_abbrev=False)
    views = last.add_mutually_exclusive_group()
    views.add_argument("--json", action="store_true")
    views.add_argument("--reasons", action="store_true")
    views.add_argument("--gaps", action="store_true")
    views.add_argument("--contradictions", action="store_true")
    views.add_argument("--evidence", action="store_true")

    capabilities = commands.add_parser("capabilities", add_help=False, allow_abbrev=False)
    cap_sub = capabilities.add_subparsers(dest="capability_action", required=True)
    cap_sub.add_parser("list", add_help=False, allow_abbrev=False)
    describe = cap_sub.add_parser("describe", add_help=False, allow_abbrev=False)
    describe.add_argument("capability_id", type=_safe_token)

    baseline = commands.add_parser("baseline", add_help=False, allow_abbrev=False)
    baseline_sub = baseline.add_subparsers(dest="baseline_action", required=True)
    baseline_assess = baseline_sub.add_parser("assess", add_help=False, allow_abbrev=False)
    _add_scope(baseline_assess, baseline=True)

    opportunity = commands.add_parser("opportunity", add_help=False, allow_abbrev=False)
    opportunity_sub = opportunity.add_subparsers(dest="opportunity_action", required=True)
    opportunity_assemble = opportunity_sub.add_parser(
        "assemble", add_help=False, allow_abbrev=False
    )
    _add_scope(opportunity_assemble)

    a4 = commands.add_parser("a4", add_help=False, allow_abbrev=False)
    a4_sub = a4.add_subparsers(dest="a4_action", required=True)
    a4_project = a4_sub.add_parser("project", add_help=False, allow_abbrev=False)
    _add_scope(a4_project)
    a4_evaluate = a4_sub.add_parser("evaluate", add_help=False, allow_abbrev=False)
    _add_scope(a4_evaluate)

    replay = commands.add_parser("replay", add_help=False, allow_abbrev=False)
    replay_sub = replay.add_subparsers(dest="replay_action", required=True)
    replay_recorded = replay_sub.add_parser("recorded", add_help=False, allow_abbrev=False)
    _add_scope(replay_recorded)
    replay_verify = replay_sub.add_parser("verify", add_help=False, allow_abbrev=False)
    _add_scope(replay_verify)

    explain = commands.add_parser("explain", add_help=False, allow_abbrev=False)
    explain.add_argument("target", choices=("last",))

    trace = commands.add_parser("trace", add_help=False, allow_abbrev=False)
    trace.add_argument("target", choices=("last",))
    trace_views = trace.add_mutually_exclusive_group()
    trace_views.add_argument("--cost", action="store_true")
    trace_views.add_argument("--evidence", action="store_true")
    trace_views.add_argument("--timing", action="store_true")

    refresh = commands.add_parser("refresh", add_help=False, allow_abbrev=False)
    refresh.add_argument("target", choices=("last",))

    commands.add_parser("exit", add_help=False, allow_abbrev=False)
    commands.add_parser("quit", add_help=False, allow_abbrev=False)
    return parser


def _reject_unsafe_or_repeated_options(tokens: Sequence[str]) -> None:
    seen: set[str] = set()
    for token in tokens:
        lowered = token.casefold()
        credential_markers = (
            "api_key",
            "api-key",
            "apikey",
            "access_token",
            "access-token",
            "authorization:",
            "authorization=",
            "bearer ",
            "password=",
            "secret=",
        )
        if (
            any(fragment in token for fragment in ("$(", "`"))
            or token.startswith("!")
            or token in {"|", "||", "&&", ";", ">", ">>", "<"}
        ):
            raise shell_error(ShellErrorCode.SYNTAX_ERROR, "shell/code expansion is not supported")
        if any(marker in lowered for marker in credential_markers):
            raise shell_error(
                ShellErrorCode.SYNTAX_ERROR,
                "credential-looking command arguments are not supported",
            )
        if token.startswith("--"):
            if "=" in token:
                raise shell_error(ShellErrorCode.SYNTAX_ERROR, "use '--option value' syntax")
            if token in seen:
                raise shell_error(ShellErrorCode.SYNTAX_ERROR, f"repeated option: {token}")
            seen.add(token)


def _scope(namespace: argparse.Namespace) -> ScopeOptions:
    return ScopeOptions(
        subject=getattr(namespace, "subject", None),
        objective=getattr(namespace, "objective", None),
        horizon=getattr(namespace, "horizon", None),
        as_of=getattr(namespace, "as_of", None),
        profile_ref=getattr(namespace, "profile_ref", None),
        authority_ref=getattr(namespace, "authority_ref", None),
        position_context_ref=getattr(namespace, "position_context_ref", None),
    )


def parse_tokens(tokens: Sequence[str]) -> ParsedCommand:
    """Parse already-tokenized input without invoking any capability."""
    if not tokens or tuple(tokens) in (("-h",), ("--help",)):
        return ParsedCommand(HelpCommand())
    _reject_unsafe_or_repeated_options(tokens)
    try:
        namespace = _build_parser().parse_args(tuple(tokens))
    except ShellError:
        raise
    except (argparse.ArgumentError, ValueError) as exc:
        raise shell_error(ShellErrorCode.SYNTAX_ERROR, str(exc)) from exc

    output = ShellOutputMode(namespace.output) if namespace.output else None
    verb = namespace.verb
    command: ShellCommand
    if verb == "help":
        command = HelpCommand(namespace.topic)
    elif verb == "use":
        command = UseCommand(namespace.subject)
    elif verb == "set":
        command = SetCommand(ContextField(namespace.field), namespace.value)
    elif verb == "unset":
        command = UnsetCommand(ContextField(namespace.field))
    elif verb == "clear":
        command = ClearContextCommand()
    elif verb == "show" and namespace.show_target == "context":
        command = ShowContextCommand()
    elif verb == "show":
        view = LastView.SUMMARY
        for enabled, candidate in (
            (namespace.reasons, LastView.REASONS),
            (namespace.gaps, LastView.GAPS),
            (namespace.contradictions, LastView.CONTRADICTIONS),
            (namespace.evidence, LastView.EVIDENCE),
        ):
            if enabled:
                view = candidate
        command = ShowLastCommand(view=view, force_json=namespace.json)
    elif verb == "capabilities" and namespace.capability_action == "list":
        command = CapabilitiesListCommand()
    elif verb == "capabilities":
        command = CapabilitiesDescribeCommand(namespace.capability_id)
    elif verb == "baseline":
        command = OperationCommand(
            OperationKind.BASELINE_ASSESS,
            _scope(namespace),
            request_file=namespace.request_file,
        )
    elif verb == "opportunity":
        command = OperationCommand(
            OperationKind.OPPORTUNITY_ASSEMBLE,
            _scope(namespace),
            artifact_ref=namespace.artifact_ref,
        )
    elif verb == "a4":
        kind = (
            OperationKind.A4_INPUT_PROJECT
            if namespace.a4_action == "project"
            else OperationKind.A4_EVALUATE
        )
        command = OperationCommand(kind, _scope(namespace), artifact_ref=namespace.artifact_ref)
    elif verb == "replay":
        kind = (
            OperationKind.REPLAY_RECORDED
            if namespace.replay_action == "recorded"
            else OperationKind.REPLAY_VERIFY
        )
        command = OperationCommand(kind, _scope(namespace), artifact_ref=namespace.artifact_ref)
    elif verb == "explain":
        command = ExplainLastCommand()
    elif verb == "trace":
        trace_view: TraceView = TraceView.ALL
        for trace_enabled, trace_candidate in (
            (namespace.cost, TraceView.COST),
            (namespace.evidence, TraceView.EVIDENCE),
            (namespace.timing, TraceView.TIMING),
        ):
            if trace_enabled:
                trace_view = trace_candidate
        command = TraceLastCommand(trace_view)
    elif verb == "refresh":
        command = RefreshLastCommand()
    elif verb in {"exit", "quit"}:
        command = ExitCommand()
    else:  # pragma: no cover - argparse's closed grammar should make this unreachable.
        raise shell_error(ShellErrorCode.UNSUPPORTED, "command is not supported")
    return ParsedCommand(command=command, output_override=output)


def parse_line(line: str) -> ParsedCommand:
    """Tokenize a REPL line exactly once and use the shared token parser."""
    try:
        tokens = shlex.split(line, posix=True)
    except ValueError as exc:
        raise shell_error(ShellErrorCode.SYNTAX_ERROR, "malformed quoted command") from exc
    return parse_tokens(tokens)
