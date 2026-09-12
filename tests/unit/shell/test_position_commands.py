"""A5.2 bounded position command and structured inspection acceptance."""

import json
from pathlib import Path

import pytest

from tiaf.a3_hardening import canonical_json
from tiaf.a5 import (
    PositionFreshness,
    PositionIntelligenceRequest,
    PositionRecommendation,
    PositionSignalKind,
)
from tiaf.context import AnalysisPurpose
from tiaf.facade import (
    ArtifactKind,
    PositionAssessResult,
    RecordedReplayResult,
    create_local_facade,
)
from tiaf.shell import SessionDefaults, ShellDispatcher, ShellError, ShellRuntime, parse_tokens
from tiaf.shell.cli import main

from ..a5._support import request as make_a5_request
from ..a5._support import signal, snapshot
from ..facade._support import (
    AUTHORITY,
    ENTITLEMENT,
    POSITION_ENTITLEMENT,
    artifact,
    captured_artifacts,
    config,
    owner,
)
from ._support import artifact_content, position_defaults, position_runtime


def authorized_request(value: PositionIntelligenceRequest) -> PositionIntelligenceRequest:
    return value.model_copy(
        update={
            "snapshot": value.snapshot.model_copy(
                update={"authority_refs": (AUTHORITY,)}
            ),
            "authority_refs": (AUTHORITY,),
        }
    )


def runtime_for(root: Path, value: PositionIntelligenceRequest, ref: str) -> ShellRuntime:
    item = artifact(
        ref,
        ArtifactKind.A5_POSITION_REQUEST,
        canonical_json(value),
        entitlement_refs=(POSITION_ENTITLEMENT,),
    )
    facade = create_local_facade(
        config().model_copy(update={"artifacts": (*captured_artifacts(), item)})
    )
    defaults = SessionDefaults(
        subject=value.snapshot.underlying,
        objective=AnalysisPurpose.POSITION,
        horizon=value.horizon,
        as_of=value.as_of,
        profile_ref="profile:deterministic",
        authority_ref=AUTHORITY,
    )
    return ShellRuntime(
        ShellDispatcher(
            facade.client("caller:test"),
            baseline_request_root=root,
            defaults=defaults,
        )
    )


def test_position_assess_uses_exact_facade_result_and_safe_human_summary(
    tmp_path: Path,
) -> None:
    shell = position_runtime(tmp_path)
    result = shell.execute_tokens(
        ["position", "assess", "--snapshot", "artifact:position-request"]
    )
    assert result.exit_code == 0
    assert result.outcome is not None
    facade_result = result.outcome.facade_result
    assert isinstance(facade_result, PositionAssessResult)
    assert facade_result.metadata.effect.value == "CAPTURED_READ"
    assert facade_result.metadata.usage.tool_calls == 0
    assert facade_result.metadata.usage.model_calls == 0
    assert "Position Id: position:synthetic-one" in result.stdout
    assert "Freshness: CURRENT" in result.stdout
    assert "Recommendation:" in result.stdout
    assert "ADVISORY_MONITORING_INTENT_ONLY_NOT_SCHEDULED" in result.stdout
    assert "ADVISORY_ONLY_TRADEMONITOR_DECIDES_BROKER_EXECUTION" in result.stdout


def test_position_one_shot_json_round_trips_facade_result(
    tmp_path: Path,
) -> None:
    shell = position_runtime(tmp_path)
    result = shell.execute_tokens(
        [
            "--output",
            "json",
            "position",
            "assess",
            "--snapshot",
            "artifact:position-request",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    reconstructed = PositionAssessResult.model_validate(payload["result"])
    assert result.outcome is not None
    assert reconstructed == result.outcome.facade_result
    assert payload["effect"] == "CAPTURED_READ"


def test_cli_main_position_one_shot_uses_shared_parser_and_dispatcher(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bootstrap = {
        "facade": config().model_dump(mode="json"),
        "caller_id": "caller:test",
        "baseline_request_root": str(tmp_path),
        "defaults": position_defaults().model_dump(mode="json"),
    }
    bootstrap_path = tmp_path / "shell.json"
    bootstrap_path.write_text(json.dumps(bootstrap), encoding="utf-8")
    exit_code = main(
        [
            "--config",
            str(bootstrap_path),
            "--output",
            "json",
            "position",
            "assess",
            "--snapshot",
            "artifact:position-request",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out)["capability_id"] == "position.assess"
    assert captured.err == ""


def test_explain_and_trace_use_only_structured_a5_and_allowlisted_lineage(
    tmp_path: Path,
) -> None:
    shell = position_runtime(tmp_path)
    shell.execute_tokens(
        ["position", "assess", "--snapshot", "artifact:position-request"]
    )
    explained = shell.execute_tokens(["--output", "json", "explain", "last"])
    traced = shell.execute_tokens(["--output", "json", "trace", "last"])
    assert explained.exit_code == traced.exit_code == 0
    explanation = json.loads(explained.stdout)
    trace = json.loads(traced.stdout)
    assert explanation["capability_id"] == "position.assess"
    assert explanation["monitoring_statement"] == (
        "ADVISORY_MONITORING_INTENT_ONLY_NOT_SCHEDULED"
    )
    assert explanation["authority_statement"] == (
        "ADVISORY_ONLY_TRADEMONITOR_DECIDES_BROKER_EXECUTION"
    )
    assert trace["position_request_ref"] == "artifact:position-request"
    assert trace["snapshot_id"]
    assert trace["linked_a4_result_id"]
    assert trace["a5_run_fingerprint"]
    serialized = traced.stdout.casefold()
    assert "entry_price" not in serialized
    assert "current_price" not in serialized
    assert "operational_source_id" not in serialized
    assert "access_token" not in serialized


def test_position_refresh_rereads_and_reauthorizes_without_changing_snapshot(
    tmp_path: Path,
) -> None:
    shell = position_runtime(tmp_path)
    first = shell.execute_tokens(
        ["position", "assess", "--snapshot", "artifact:position-request"]
    )
    assert first.exit_code == 0
    old = shell.dispatcher.session.last
    refreshed = shell.execute_tokens(["refresh", "last"])
    new = shell.dispatcher.session.last
    assert refreshed.exit_code == 0
    assert old is not None and new is not None
    assert isinstance(old.result, PositionAssessResult)
    assert isinstance(new.result, PositionAssessResult)
    assert new.record.facade_run_id != old.record.facade_run_id
    assert new.result.assessment.snapshot_at == old.result.assessment.snapshot_at
    assert new.result.assessment.semantic_fingerprint == old.result.assessment.semantic_fingerprint


def test_two_shell_sessions_do_not_share_position_or_last_result(tmp_path: Path) -> None:
    first = position_runtime(tmp_path)
    second = position_runtime(tmp_path)
    first.execute_tokens(
        ["position", "assess", "--snapshot", "artifact:position-request"]
    )
    assert first.dispatcher.session.last is not None
    assert second.dispatcher.session.last is None
    assert first.dispatcher.session.session_id != second.dispatcher.session.session_id


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (
            authorized_request(
                make_a5_request(
                    position_snapshot=snapshot(freshness=PositionFreshness.STALE)
                )
            ),
            PositionRecommendation.ABSTAIN,
        ),
        (
            authorized_request(
                make_a5_request(
                    signals=(
                        signal(
                            PositionSignalKind.THESIS_INVALIDATION,
                            a4=make_a5_request().a4_result,
                        ),
                    )
                )
            ),
            PositionRecommendation.EXIT_RECOMMENDED,
        ),
    ),
)
def test_position_domain_abstain_and_exit_are_successful_shell_results(
    tmp_path: Path,
    value: PositionIntelligenceRequest,
    expected: PositionRecommendation,
) -> None:
    ref = f"artifact:position-{expected.value.casefold()}"
    shell = runtime_for(tmp_path, value, ref)
    result = shell.execute_tokens(["position", "assess", "--snapshot", ref])
    assert result.exit_code == 0
    assert result.outcome is not None
    facade_result = result.outcome.facade_result
    assert isinstance(facade_result, PositionAssessResult)
    assert facade_result.assessment.recommendation is expected


def test_expression_refresh_is_rendered_without_selecting_replacement(
    tmp_path: Path,
) -> None:
    value = authorized_request(
        make_a5_request(signals=(signal(PositionSignalKind.EXPRESSION_UNSUITABLE),))
    )
    ref = "artifact:position-expression-refresh"
    shell = runtime_for(tmp_path, value, ref)
    result = shell.execute_tokens(["position", "assess", "--snapshot", ref])
    assert result.exit_code == 0
    assert "expression refresh required; no replacement selected" in result.stdout
    assert "roll to" not in result.stdout.casefold()


def test_generic_shell_replay_handles_a5_capture_offline(tmp_path: Path) -> None:
    request = PositionIntelligenceRequest.model_validate_json(
        artifact_content("artifact:position-request")
    )
    shell = ShellRuntime(
        ShellDispatcher(
            owner().client("caller:test"),
            baseline_request_root=tmp_path,
            defaults=SessionDefaults(
                subject=request.snapshot.underlying,
                objective=AnalysisPurpose.POSITION,
                horizon=request.horizon,
                as_of=request.as_of,
                profile_ref="profile:deterministic",
                authority_ref=AUTHORITY,
            ),
        )
    )
    result = shell.execute_tokens(
        ["replay", "recorded", "--artifact-ref", "artifact:a5-capture"]
    )
    assert result.exit_code == 0
    assert result.outcome is not None
    replay = result.outcome.facade_result
    assert isinstance(replay, RecordedReplayResult)
    assert replay.kind.value == "A5_RECORDED"
    assert replay.a5_replay is not None
    assert replay.a5_replay.provider_calls == replay.a5_replay.model_calls == 0


@pytest.mark.parametrize(
    "tokens",
    (
        ["position", "exit"],
        ["position", "modify"],
        ["position", "stop"],
        ["position", "trail"],
        ["position", "roll"],
        ["position", "hedge"],
        ["position", "squareoff"],
    ),
)
def test_execution_like_position_commands_remain_outside_grammar(
    tokens: list[str],
) -> None:
    with pytest.raises(ShellError):
        parse_tokens(tokens)


def test_position_context_default_cannot_redirect_snapshot_authority(tmp_path: Path) -> None:
    shell = position_runtime(tmp_path)
    shell.dispatcher.session.replace_default(
        "position_context_ref", "artifact:foreign-position"
    )
    result = shell.execute_tokens(
        ["position", "assess", "--snapshot", "artifact:position-request"]
    )
    assert result.exit_code == 2
    assert "must match" in result.stderr
    assert shell.dispatcher.session.last is None


def test_position_permission_failure_is_nonzero_and_not_saved_as_last(
    tmp_path: Path,
) -> None:
    facade = owner(caller_entitlements=(ENTITLEMENT,))
    shell = ShellRuntime(
        ShellDispatcher(
            facade.client("caller:test"),
            baseline_request_root=tmp_path,
            defaults=position_defaults(),
        )
    )
    result = shell.execute_tokens(
        ["position", "assess", "--snapshot", "artifact:position-request"]
    )
    assert result.exit_code == 3
    assert "PERMISSION_DENIED" in result.stderr
    assert shell.dispatcher.session.last is None


@pytest.mark.parametrize(
    "unsafe",
    ("../position.json", "/tmp/position.json", "https://example.test/position"),
)
def test_position_snapshot_reference_rejects_paths_and_urls(unsafe: str) -> None:
    with pytest.raises(ShellError):
        parse_tokens(["position", "assess", "--snapshot", unsafe])
