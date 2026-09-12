"""Shared grammar, context isolation and restricted-surface acceptance."""

from datetime import timedelta
from pathlib import Path

import pytest

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.shell import ShellError, ShellOutputMode, parse_line, parse_tokens
from tiaf.shell.commands import OperationCommand, UseCommand

from ._support import runtime


def test_empty_tokens_are_safe_local_help() -> None:
    parsed = parse_tokens([])
    assert parsed.output_override is None
    assert type(parsed.command).__name__ == "HelpCommand"


def test_quoted_repl_subject_uses_same_parser_and_normalizes() -> None:
    line = parse_line('use "kaynes"')
    tokens = parse_tokens(["use", "kaynes"])
    assert line == tokens
    assert isinstance(line.command, UseCommand)
    assert line.command.subject == "KAYNES"


@pytest.mark.parametrize(
    "subject",
    ("RELIANCE.NS", "https://example.test", "/tmp/x", "RELIANCE NSE"),
)
def test_provider_specific_or_path_subject_is_rejected(subject: str) -> None:
    with pytest.raises(ShellError):
        parse_tokens(["use", subject])


@pytest.mark.parametrize(
    "tokens",
    (
        ["cap"],
        ["eval", "1+1"],
        ["exec", "code"],
        ["import", "os"],
        ["!ls"],
        ["help", "$(id)"],
        ["help", "`id`"],
        ["help", "|"],
        ["set", "profile-ref", "api_key=do-not-store"],
        ["broker", "order"],
        ["order", "buy"],
        ["ask", "analyze"],
        ["option", "select"],
        ["rank", "all"],
    ),
)
def test_unknown_code_shell_broker_model_and_future_commands_are_rejected(
    tokens: list[str],
) -> None:
    with pytest.raises(ShellError):
        parse_tokens(tokens)


def test_repeated_and_equals_style_options_are_rejected() -> None:
    with pytest.raises(ShellError, match="repeated option"):
        parse_tokens(["--output", "json", "--output", "human", "help"])
    with pytest.raises(ShellError, match="--option value"):
        parse_tokens(["--output=json", "help"])


def test_artifact_reference_rejects_relative_filesystem_shape() -> None:
    with pytest.raises(ShellError):
        parse_tokens(
            [
                "opportunity",
                "assemble",
                "--artifact-ref",
                "captures/a38.json",
            ]
        )


def test_aware_datetime_normalizes_to_canonical_timezone() -> None:
    parsed = parse_tokens(
        [
            "a4",
            "evaluate",
            "--artifact-ref",
            "artifact:foundation-capture",
            "--as-of",
            "2026-09-06T06:30:00+00:00",
        ]
    )
    assert isinstance(parsed.command, OperationCommand)
    assert parsed.command.scope.as_of is not None
    assert parsed.command.scope.as_of.tzinfo == TIAF_TIMEZONE
    assert parsed.command.scope.as_of.utcoffset() == timedelta(hours=5, minutes=30)


@pytest.mark.parametrize("value", ("2026-09-06T12:00:00", "not-a-time"))
def test_naive_and_invalid_datetime_are_rejected(value: str) -> None:
    with pytest.raises(ShellError):
        parse_tokens(
            [
                "a4",
                "evaluate",
                "--artifact-ref",
                "artifact:foundation-capture",
                "--as-of",
                value,
            ]
        )


def test_session_starts_empty_and_two_sessions_are_isolated(tmp_path: Path) -> None:
    first = runtime(tmp_path, full_context=False)
    second = runtime(tmp_path, full_context=False)
    assert first.dispatcher.session.defaults.subject is None
    assert second.dispatcher.session.defaults.subject is None
    result = first.execute_tokens(["use", "KAYNES"])
    assert result.exit_code == 0
    assert first.dispatcher.session.defaults.subject == "KAYNES"
    assert second.dispatcher.session.defaults.subject is None


def test_set_show_unset_and_clear_context_are_typed_and_non_authorizing(
    tmp_path: Path,
) -> None:
    shell = runtime(tmp_path, full_context=False)
    assert shell.execute_tokens(["use", "KAYNES"]).exit_code == 0
    assert shell.execute_tokens(["set", "subject", "reliance"]).exit_code == 0
    assert shell.dispatcher.session.defaults.subject == "RELIANCE"
    assert shell.execute_tokens(["set", "objective", "opportunity"]).exit_code == 0
    assert shell.execute_tokens(["set", "horizon", "positional"]).exit_code == 0
    assert shell.execute_tokens(["set", "output", "json"]).exit_code == 0
    shown = shell.execute_tokens(["show", "context"])
    assert shown.exit_code == 0
    assert shown.stdout.startswith("{")
    assert shell.dispatcher.session.defaults.output is ShellOutputMode.JSON
    assert shell.execute_tokens(["unset", "horizon"]).exit_code == 0
    assert shell.dispatcher.session.defaults.horizon is None
    assert shell.execute_tokens(["clear", "context"]).exit_code == 0
    defaults = shell.dispatcher.session.defaults
    assert defaults.subject is None
    assert defaults.profile_ref is not None
    assert defaults.authority_ref is not None


def test_set_subject_rejects_provider_suffix_without_mutating_context(
    tmp_path: Path,
) -> None:
    shell = runtime(tmp_path, full_context=False)
    assert shell.execute_tokens(["use", "KAYNES"]).exit_code == 0
    result = shell.execute_tokens(["set", "subject", "RELIANCE.NS"])
    assert result.exit_code == 2
    assert shell.dispatcher.session.defaults.subject == "KAYNES"


def test_missing_context_fails_without_guessing(tmp_path: Path) -> None:
    shell = runtime(tmp_path, full_context=False)
    result = shell.execute_tokens(
        ["opportunity", "assemble", "--artifact-ref", "artifact:a38"]
    )
    assert result.exit_code == 2
    assert "missing required context" in result.stderr
    assert shell.dispatcher.session.last is None
