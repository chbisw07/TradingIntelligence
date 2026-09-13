"""A6.3 bounded TI Shell expression command and inspection acceptance."""

import json
from pathlib import Path

import pytest

from tiaf.facade import ExpressionAssessResult, RecordedReplayResult
from tiaf.shell import ShellError, parse_line, parse_tokens

from ._support import expression_runtime


@pytest.mark.parametrize(
    ("ref", "disposition"),
    (
        ("artifact:a6-available", "EXPRESSION_AVAILABLE"),
        ("artifact:a6-no-option-trade", "NO_OPTION_TRADE"),
        ("artifact:a6-wait", "WAIT_FOR_EXPRESSION"),
        ("artifact:a6-insufficient", "INSUFFICIENT_EVIDENCE"),
    ),
)
def test_expression_assess_renders_each_deterministic_disposition(
    tmp_path: Path,
    ref: str,
    disposition: str,
) -> None:
    result = expression_runtime(tmp_path, ref).execute_tokens(
        ["expression", "assess", "--input", ref]
    )
    assert result.exit_code == 0
    assert result.outcome is not None
    facade_result = result.outcome.facade_result
    assert isinstance(facade_result, ExpressionAssessResult)
    assert facade_result.assessment.disposition.value == disposition
    assert facade_result.metadata.usage.tool_calls == 0
    assert facade_result.metadata.usage.model_calls == 0
    assert f"Disposition: {disposition}" in result.stdout
    assert "Policy Refs:" in result.stdout
    assert len(facade_result.assessment.alternative_candidate_refs) <= 2
    assert "ADVISORY_ONLY_TM_RETAINS_ACTION_AUTHORITY" in result.stdout
    if disposition == "NO_OPTION_TRADE":
        assert "Rejected Candidates:" in result.stdout
        assert "NON_POSITIVE_TOP_QUANTITY" in result.stdout
    if disposition == "INSUFFICIENT_EVIDENCE":
        assert "Uncertain Candidates:" in result.stdout
        assert "MISSING_BID_OR_ASK" in result.stdout


def test_expression_json_is_complete_exact_facade_result(tmp_path: Path) -> None:
    result = expression_runtime(tmp_path).execute_tokens(
        ["--output", "json", "expression", "assess", "--input", "artifact:a6-available"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    reconstructed = ExpressionAssessResult.model_validate(payload["result"])
    assert result.outcome is not None
    assert reconstructed == result.outcome.facade_result
    assert payload["result"]["assessment"]["candidate_evaluations"]
    assert payload["effect"] == "CAPTURED_READ"


def test_shell_help_and_discovery_expose_expression_without_live_claim(
    tmp_path: Path,
) -> None:
    shell = expression_runtime(tmp_path)
    helped = shell.execute_tokens(["help", "expression"])
    described = shell.execute_tokens(
        ["--output", "json", "capabilities", "describe", "expression.assess"]
    )
    assert helped.exit_code == described.exit_code == 0
    assert "expression assess --input QUALIFIED_ID" in helped.stdout
    descriptor = json.loads(described.stdout)["selected_descriptor"]
    assert descriptor["effect"] == "CAPTURED_READ"
    assert descriptor["semantic_role"] == "TRADE_EXPRESSION_INTELLIGENCE"
    assert descriptor["readiness_state"] == "REQUIRES_RUNTIME_CHECK"
    assert "LIVE_READ" not in described.stdout


def test_expression_explain_trace_and_replay_preserve_lineage(tmp_path: Path) -> None:
    shell = expression_runtime(tmp_path)
    assessed = shell.execute_tokens(
        ["expression", "assess", "--input", "artifact:a6-available"]
    )
    assert assessed.exit_code == 0
    explained = shell.execute_tokens(["--output", "json", "explain", "last"])
    traced = shell.execute_tokens(["--output", "json", "trace", "last"])
    explanation = json.loads(explained.stdout)
    trace = json.loads(traced.stdout)
    assert explanation["capability_id"] == "expression.assess"
    assert explanation["candidate_evaluations"]
    assert explanation["invalidation_conditions"]
    assert trace["expression_input_ref"] == "artifact:a6-available"
    assert trace["input_integrity_verified"] is True
    assert trace["semantic_fingerprint"]
    assert trace["usage"]["model_calls"] == trace["usage"]["tool_calls"] == 0

    replayed = shell.execute_tokens(
        ["replay", "recorded", "--artifact-ref", "artifact:a6-available"]
    )
    assert replayed.exit_code == 0 and replayed.outcome is not None
    replay = replayed.outcome.facade_result
    assert isinstance(replay, RecordedReplayResult)
    assert replay.kind.value == "A6_RECORDED"
    assert replay.a6_assessment is not None


def test_expression_one_shot_and_repl_share_parser_and_semantics(tmp_path: Path) -> None:
    tokens = ["expression", "assess", "--input", "artifact:a6-available"]
    assert parse_tokens(tokens) == parse_line(" ".join(tokens))
    one_shot = expression_runtime(tmp_path).execute_tokens(tokens)
    repl_style = expression_runtime(tmp_path).execute_line(" ".join(tokens))
    assert one_shot.outcome is not None and repl_style.outcome is not None
    one_result = one_shot.outcome.facade_result
    repl_result = repl_style.outcome.facade_result
    assert isinstance(one_result, ExpressionAssessResult)
    assert isinstance(repl_result, ExpressionAssessResult)
    assert one_result.assessment.semantic_fingerprint == (
        repl_result.assessment.semantic_fingerprint
    )


@pytest.mark.parametrize(
    "unsafe",
    ("../capture.json", "/tmp/capture.json", "https://example.test/capture"),
)
def test_expression_input_rejects_paths_and_urls(unsafe: str) -> None:
    with pytest.raises(ShellError):
        parse_tokens(["expression", "assess", "--input", unsafe])


@pytest.mark.parametrize(
    "tokens",
    (
        ["expression", "execute"],
        ["expression", "buy"],
        ["expression", "order"],
        ["expression", "size"],
    ),
)
def test_execution_like_expression_commands_remain_outside_grammar(
    tokens: list[str],
) -> None:
    with pytest.raises(ShellError):
        parse_tokens(tokens)
