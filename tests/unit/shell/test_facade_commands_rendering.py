"""Facade parity, last-result, rendering, replay and engineering acceptance."""

import json
from pathlib import Path

import pytest

from tiaf.baseline import BaselineEngine, CandidateClass
from tiaf.facade import (
    A4EvaluateResult,
    A4InputProjectResult,
    BaselineAssessResult,
    CapabilityListResult,
    OpportunityAssembleResult,
    RecordedReplayResult,
    ReplayVerifyResult,
)
from tiaf.shell import SessionDefaults, ShellDispatcher, ShellErrorCode, ShellRuntime

from ..facade._support import ALL_CAPABILITIES, AUTHORITY, PROFILE, owner
from ._support import a4_state_runtime, runtime, write_baseline


def test_capability_discovery_and_describe_use_filtered_facade_result(
    tmp_path: Path,
) -> None:
    shell = runtime(tmp_path)
    listed = shell.execute_tokens(["capabilities", "list"])
    assert listed.exit_code == 0
    assert listed.outcome is not None
    assert isinstance(listed.outcome.facade_result, CapabilityListResult)
    assert tuple(
        item.capability_id for item in listed.outcome.facade_result.capabilities
    ) == ALL_CAPABILITIES

    described = shell.execute_tokens(["capabilities", "describe", "a4.evaluate"])
    assert described.exit_code == 0
    assert "a4.evaluate" in described.stdout
    assert "CAPTURED_READ" in described.stdout


def test_describe_cannot_reveal_filtered_engineering_capability(tmp_path: Path) -> None:
    facade_owner = owner(engineering=False)
    shell = ShellRuntime(
        ShellDispatcher(
            facade_owner.client("caller:test"),
            baseline_request_root=tmp_path,
            defaults=SessionDefaults(profile_ref=PROFILE, authority_ref=AUTHORITY),
        )
    )
    result = shell.execute_tokens(["capabilities", "describe", "replay.verify"])
    assert result.exit_code == 4
    assert "unavailable" in result.stderr


def test_baseline_has_direct_engine_parity_and_no_trade_is_success(tmp_path: Path) -> None:
    request = write_baseline(tmp_path)
    shell = runtime(tmp_path, full_context=False)
    result = shell.execute_tokens(
        ["--output", "json", "baseline", "assess", "--request-file", "baseline.json"]
    )
    assert result.exit_code == 0
    assert result.outcome is not None
    facade_result = result.outcome.facade_result
    assert isinstance(facade_result, BaselineAssessResult)
    assert facade_result.assessment == BaselineEngine().assess(request)
    assert facade_result.assessment.candidate_class is CandidateClass.NO_TRADE
    assert facade_result.metadata.usage.model_calls == 0
    assert facade_result.metadata.usage.tool_calls == 0

    payload = json.loads(result.stdout)
    reconstructed = BaselineAssessResult.model_validate(payload["result"])
    assert reconstructed == facade_result
    assert payload["effect"] == "PURE"


@pytest.mark.parametrize(
    ("package_name", "expected_disposition"),
    (("poor_timing", "WAIT"), ("unsupported_assumption", "ABSTAIN")),
)
def test_non_action_a4_dispositions_are_successful_shell_outcomes(
    tmp_path: Path,
    package_name: str,
    expected_disposition: str,
) -> None:
    shell, artifact_ref = a4_state_runtime(tmp_path, package_name)
    result = shell.execute_tokens(["a4", "evaluate", "--artifact-ref", artifact_ref])
    assert result.exit_code == 0
    assert f"Disposition: {expected_disposition}" in result.stdout


@pytest.mark.parametrize("unsafe", (Path("/tmp/baseline.json"), Path("../baseline.json")))
def test_baseline_rejects_absolute_and_traversal_paths(
    tmp_path: Path,
    unsafe: Path,
) -> None:
    shell = runtime(tmp_path, full_context=False)
    result = shell.execute_tokens(
        ["baseline", "assess", "--request-file", str(unsafe)]
    )
    assert result.exit_code == 5
    assert result.error is not None
    assert result.error.record.code is ShellErrorCode.INPUT_SAFETY_ERROR


def test_baseline_rejects_symlink_escape(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-baseline.json"
    outside.write_text("{}", encoding="utf-8")
    (tmp_path / "escape.json").symlink_to(outside)
    shell = runtime(tmp_path, full_context=False)
    result = shell.execute_tokens(
        ["baseline", "assess", "--request-file", "escape.json"]
    )
    assert result.exit_code == 5


def test_baseline_rejects_invalid_typed_json_without_losing_last(
    tmp_path: Path,
) -> None:
    write_baseline(tmp_path)
    (tmp_path / "invalid.json").write_text("{}", encoding="utf-8")
    shell = runtime(tmp_path, full_context=False)
    good = shell.execute_tokens(
        ["baseline", "assess", "--request-file", "baseline.json"]
    )
    assert good.exit_code == 0
    last = shell.dispatcher.session.last
    failed = shell.execute_tokens(
        ["baseline", "assess", "--request-file", "invalid.json"]
    )
    assert failed.exit_code == 2
    assert shell.dispatcher.session.last is last


@pytest.mark.parametrize(
    ("tokens", "result_type", "capability_id"),
    (
        (
            ["opportunity", "assemble", "--artifact-ref", "artifact:a38"],
            OpportunityAssembleResult,
            "opportunity.assemble",
        ),
        (
            ["a4", "project", "--artifact-ref", "artifact:foundation-input"],
            A4InputProjectResult,
            "a4_input.project",
        ),
        (
            ["a4", "evaluate", "--artifact-ref", "artifact:foundation-capture"],
            A4EvaluateResult,
            "a4.evaluate",
        ),
        (
            ["replay", "recorded", "--artifact-ref", "artifact:a3-package"],
            RecordedReplayResult,
            "replay.recorded",
        ),
        (
            ["replay", "verify", "--artifact-ref", "artifact:a3-package"],
            ReplayVerifyResult,
            "replay.verify",
        ),
    ),
)
def test_all_captured_and_engineering_commands_use_exact_facade_results(
    tmp_path: Path,
    tokens: list[str],
    result_type: type[object],
    capability_id: str,
) -> None:
    shell = runtime(tmp_path)
    result = shell.execute_tokens(["--output", "json", *tokens])
    assert result.exit_code == 0
    assert result.outcome is not None
    outcome = result.outcome
    assert isinstance(outcome.facade_result, result_type)
    assert shell.dispatcher.session.last is not None
    assert outcome.facade_result is shell.dispatcher.session.last.result
    assert outcome.facade_result.metadata.capability_id == capability_id
    assert outcome.facade_result.metadata.usage.model_calls == 0
    assert outcome.facade_result.metadata.usage.tool_calls == 0
    payload = json.loads(result.stdout)
    assert payload["result"] == outcome.facade_result.model_dump(mode="json")


def test_show_last_is_identity_preserving_inspection_and_stable_json(
    tmp_path: Path,
) -> None:
    shell = runtime(tmp_path)
    invoked = shell.execute_tokens(
        ["a4", "evaluate", "--artifact-ref", "artifact:foundation-capture"]
    )
    assert invoked.exit_code == 0
    last = shell.dispatcher.session.last
    assert last is not None
    history = shell.dispatcher.session.history
    shown = shell.execute_tokens(["show", "last", "--json"])
    assert shown.exit_code == 0
    assert shown.outcome is not None
    assert shown.outcome.facade_result is last.result
    assert shell.dispatcher.session.last is last
    assert shell.dispatcher.session.history == history
    first = json.loads(shown.stdout)
    second = json.loads(shell.execute_tokens(["show", "last", "--json"]).stdout)
    assert first == second


def test_refresh_is_new_run_with_same_semantics_and_rechecks_admission(
    tmp_path: Path,
) -> None:
    shell = runtime(tmp_path)
    original = shell.execute_tokens(
        ["a4", "evaluate", "--artifact-ref", "artifact:foundation-capture"]
    )
    assert original.outcome is not None
    old = shell.dispatcher.session.last
    refreshed = shell.execute_tokens(["refresh", "last"])
    assert refreshed.exit_code == 0
    assert refreshed.outcome is not None
    new = shell.dispatcher.session.last
    assert new is not None and old is not None
    assert new.record.request_id != old.record.request_id
    assert new.record.facade_run_id != old.record.facade_run_id
    assert new.record.parent_shell_invocation_id == old.record.shell_invocation_id
    assert isinstance(new.result, A4EvaluateResult)
    assert isinstance(old.result, A4EvaluateResult)
    assert new.result.evaluation == old.result.evaluation
    assert new.result.run_fingerprint == old.result.run_fingerprint
    assert new.result.metadata.usage.model_calls == 0


@pytest.mark.parametrize(
    "flag",
    ("--reasons", "--gaps", "--contradictions", "--evidence"),
)
def test_last_views_use_only_structured_a4_data(tmp_path: Path, flag: str) -> None:
    shell = runtime(tmp_path)
    shell.execute_tokens(
        ["a4", "evaluate", "--artifact-ref", "artifact:foundation-capture"]
    )
    before = shell.dispatcher.session.history
    rendered = shell.execute_tokens(["show", "last", flag])
    assert rendered.exit_code == 0
    assert rendered.stdout
    assert shell.dispatcher.session.history == before


def test_explain_preserves_a4_theses_findings_uncertainty_and_evidence(
    tmp_path: Path,
) -> None:
    shell = runtime(tmp_path)
    shell.execute_tokens(
        [
            "--output",
            "json",
            "a4",
            "evaluate",
            "--artifact-ref",
            "artifact:foundation-capture",
        ]
    )
    explained = shell.execute_tokens(["--output", "json", "explain", "last"])
    assert explained.exit_code == 0
    payload = json.loads(explained.stdout)
    last = shell.dispatcher.session.last
    assert last is not None
    assert isinstance(last.result, A4EvaluateResult)
    evaluation = last.result.evaluation
    assert payload["primary_thesis"] == evaluation.primary_thesis.model_dump(mode="json")
    assert payload["challenge_findings"] == [
        item.model_dump(mode="json") for item in evaluation.challenge_findings
    ]
    assert payload["arbitration_findings"] == [
        item.model_dump(mode="json") for item in evaluation.arbitration_findings
    ]
    assert payload["residual_uncertainties"] == [
        item.model_dump(mode="json") for item in evaluation.residual_uncertainties
    ]


@pytest.mark.parametrize("flag", (None, "--cost", "--evidence", "--timing"))
def test_trace_is_safe_allowlisted_facade_metadata(
    tmp_path: Path,
    flag: str | None,
) -> None:
    shell = runtime(tmp_path)
    shell.execute_tokens(
        ["a4", "evaluate", "--artifact-ref", "artifact:foundation-capture"]
    )
    tokens = ["--output", "json", "trace", "last"]
    if flag is not None:
        tokens.append(flag)
    traced = shell.execute_tokens(tokens)
    assert traced.exit_code == 0
    payload = json.loads(traced.stdout)
    serialized = traced.stdout.casefold()
    assert payload["capability_id"] == "a4.evaluate"
    assert "access_token" not in serialized
    assert "api_key" not in serialized
    assert "authorization" not in serialized
    assert "filesystem" not in serialized
    assert "object at 0x" not in serialized
    assert "traceback" not in serialized


def test_recorded_replay_is_offline_and_identity_is_distinct(tmp_path: Path) -> None:
    shell = runtime(tmp_path)
    original = shell.execute_tokens(
        ["a4", "evaluate", "--artifact-ref", "artifact:foundation-capture"]
    )
    replayed = shell.execute_tokens(
        ["replay", "recorded", "--artifact-ref", "artifact:foundation-capture"]
    )
    assert original.exit_code == replayed.exit_code == 0
    assert replayed.outcome is not None
    result = replayed.outcome.facade_result
    assert isinstance(result, RecordedReplayResult)
    assert result.kind.value == "FOUNDATION_RECORDED"
    assert result.metadata.usage.model_calls == result.metadata.usage.tool_calls == 0
    assert original.outcome is not None
    original_result = original.outcome.facade_result
    assert original_result is not None
    assert result.metadata.run_id != original_result.metadata.run_id


def test_verify_is_denied_without_engineering_grant_and_last_is_preserved(
    tmp_path: Path,
) -> None:
    shell = runtime(tmp_path, engineering=False)
    good = shell.execute_tokens(
        ["replay", "recorded", "--artifact-ref", "artifact:a3-package"]
    )
    assert good.exit_code == 0
    previous = shell.dispatcher.session.last
    denied = shell.execute_tokens(
        ["replay", "verify", "--artifact-ref", "artifact:a3-package"]
    )
    assert denied.exit_code == 3
    assert denied.error is not None
    assert denied.error.record.code is ShellErrorCode.PERMISSION_DENIED
    assert shell.dispatcher.session.last is previous


def test_explicit_subject_override_is_request_local_and_mismatch_fails(
    tmp_path: Path,
) -> None:
    shell = runtime(tmp_path)
    original_subject = shell.dispatcher.session.defaults.subject
    failed = shell.execute_tokens(
        [
            "a4",
            "evaluate",
            "--artifact-ref",
            "artifact:foundation-capture",
            "--subject",
            "KAYNES",
        ]
    )
    assert failed.exit_code == 6
    assert shell.dispatcher.session.defaults.subject == original_subject
    assert shell.dispatcher.session.last is None
