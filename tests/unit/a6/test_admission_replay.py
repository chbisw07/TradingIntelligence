from datetime import timedelta

import pytest

from tiaf.a4 import (
    A4ExecutionStatus,
    A4Result,
    evaluate_projection,
    result_semantic_payload,
)
from tiaf.planner.digests import digest
from tiaf.source_semantics import A4SemanticInputProjection
from tiaf.trade_expression import (
    A6ReplayIntegrityError,
    AdmissionOutcome,
    CoverageState,
    ExpirationQualification,
    ExpressionDirection,
    FreshnessBasis,
    MarketTimingQualification,
    TimingQualification,
    admit_request,
    deterministic_policy,
    validate_admission_result,
    verify_admission_replay,
)

from ..a4._support import with_gap, with_state, with_unresolved_conflict
from ._support import NOW, a4_result, bundle, derivatives_capture, request


def _evaluated(projection: A4SemanticInputProjection) -> A4Result:
    return evaluate_projection(
        projection,
        evaluated_at=projection.header.evidence_as_of,
    ).result


def _reseal_a4(result: A4Result, **updates: object) -> A4Result:
    provisional = result.model_copy(
        update={
            **updates,
            "result_id": "a4-result:pending",
            "semantic_fingerprint": "0" * 64,
        }
    )
    fingerprint = digest(result_semantic_payload(provisional))
    return provisional.model_copy(
        update={
            "result_id": f"a4-result:{fingerprint[:24]}",
            "semantic_fingerprint": fingerprint,
        }
    )


def test_complete_supportive_supported_primary_is_admitted() -> None:
    a4 = a4_result()
    evidence = bundle(a4)
    result = admit_request(request(a4, evidence=evidence), a4, evidence, deterministic_policy())
    assert result.outcome is AdmissionOutcome.ADMITTED
    assert result.resolved_direction is ExpressionDirection.BULLISH
    assert result.provider_calls == result.model_calls == 0
    assert result.input_tokens == result.output_tokens == result.model_cost_units == 0
    assert validate_admission_result(result) == result


@pytest.mark.parametrize(
    "a4,expected",
    [
        (
            _evaluated(with_state("OPPORTUNITY", a2_class="NO_TRADE")),
            AdmissionOutcome.REJECTED_UPSTREAM,
        ),
        (_evaluated(with_state("AVOID")), AdmissionOutcome.REJECTED_UPSTREAM),
        (_evaluated(with_state("WAIT")), AdmissionOutcome.REJECTED_UPSTREAM),
        (_evaluated(with_unresolved_conflict()), AdmissionOutcome.REJECTED_UPSTREAM),
        (_evaluated(with_gap()), AdmissionOutcome.INSUFFICIENT_EVIDENCE),
        (_evaluated(with_state("WATCH")), AdmissionOutcome.REJECTED_UPSTREAM),
        (
            _evaluated(with_state("OPPORTUNITY", a2_direction=None)),
            AdmissionOutcome.REJECTED_UPSTREAM,
        ),
    ],
)
def test_a4_gate_rejects_non_admissible_states(a4: A4Result, expected: AdmissionOutcome) -> None:
    evidence = bundle(a4)
    result = admit_request(request(a4, evidence=evidence), a4, evidence, deterministic_policy())
    assert result.outcome is expected


def test_a4_rejection_precedes_horizon_policy_checks() -> None:
    a4 = _evaluated(with_state("OPPORTUNITY", a2_class="NO_TRADE"))
    evidence = bundle(a4)
    value = request(a4, evidence=evidence)
    target = value.evaluation_cutoff + timedelta(days=91)
    changed = value.model_dump(mode="python")
    changed["horizon"] = {
        **value.horizon.model_dump(mode="python"),
        "target_end_at": target,
        "exact_duration_seconds": 91 * 24 * 60 * 60,
    }
    outside_horizon = type(value).model_validate(changed)

    result = admit_request(outside_horizon, a4, evidence, deterministic_policy())

    assert result.outcome is AdmissionOutcome.REJECTED_UPSTREAM
    assert result.reason_codes == ("A4_NO_TRADE",)


def test_partial_a4_execution_is_insufficient() -> None:
    a4 = _reseal_a4(a4_result(), execution_status=A4ExecutionStatus.PARTIAL)
    evidence = bundle(a4)
    result = admit_request(request(a4, evidence=evidence), a4, evidence, deterministic_policy())
    assert result.outcome is AdmissionOutcome.INSUFFICIENT_EVIDENCE


def test_tampered_a4_result_is_invalid_request() -> None:
    a4 = a4_result().model_copy(update={"execution_status": A4ExecutionStatus.PARTIAL})
    evidence = bundle(a4)
    result = admit_request(request(a4, evidence=evidence), a4, evidence, deterministic_policy())
    assert result.outcome is AdmissionOutcome.INVALID_REQUEST
    assert result.reason_codes == ("A4_RESULT_INTEGRITY_FAILED",)


def test_direction_conflict_is_invalid_request() -> None:
    a4 = a4_result()
    evidence = bundle(a4)
    result = admit_request(
        request(a4, evidence=evidence, direction=ExpressionDirection.BEARISH),
        a4,
        evidence,
        deterministic_policy(),
    )
    assert result.outcome is AdmissionOutcome.INVALID_REQUEST


def test_negative_supported_thesis_resolves_to_bearish() -> None:
    a4 = _evaluated(with_state("OPPORTUNITY", a2_direction="NEGATIVE"))
    evidence = bundle(a4)
    result = admit_request(
        request(a4, evidence=evidence, direction=ExpressionDirection.BEARISH),
        a4,
        evidence,
        deterministic_policy(),
    )
    assert result.outcome is AdmissionOutcome.ADMITTED
    assert result.resolved_direction is ExpressionDirection.BEARISH


def test_partial_derivatives_coverage_is_insufficient() -> None:
    a4 = a4_result()
    evidence = bundle(a4, capture=derivatives_capture(capture_coverage=CoverageState.PARTIAL))
    result = admit_request(request(a4, evidence=evidence), a4, evidence, deterministic_policy())
    assert result.outcome is AdmissionOutcome.INSUFFICIENT_EVIDENCE


def test_confirmed_empty_derivatives_scope_is_admissible_evidence() -> None:
    a4 = a4_result()
    evidence = bundle(
        a4,
        capture=derivatives_capture(capture_coverage=CoverageState.CONFIRMED_EMPTY),
    )
    result = admit_request(request(a4, evidence=evidence), a4, evidence, deterministic_policy())
    assert result.outcome is AdmissionOutcome.ADMITTED


def test_date_only_expiry_is_insufficient_for_admission() -> None:
    a4 = a4_result()
    evidence = bundle(a4)
    chain = evidence.derivatives.chains[0]
    changed_chain = chain.model_copy(
        update={
            "expiration": chain.expiration.model_copy(
                update={
                    "expiration_at": None,
                    "qualification": ExpirationQualification.DATE_ONLY,
                    "qualification_source_ref": None,
                }
            )
        }
    )
    changed_capture = evidence.derivatives.model_copy(update={"chains": (changed_chain,)})
    changed_evidence = evidence.model_copy(update={"derivatives": changed_capture})
    result = admit_request(
        request(a4, evidence=changed_evidence),
        a4,
        changed_evidence,
        deterministic_policy(),
    )
    assert result.outcome is AdmissionOutcome.INSUFFICIENT_EVIDENCE
    assert result.reason_codes == ("EXPIRATION_INSTANT_UNQUALIFIED",)


def test_acquisition_only_quote_time_is_insufficient_for_admission() -> None:
    a4 = a4_result()
    evidence = bundle(a4)
    chain = evidence.derivatives.chains[0]
    quote = chain.quotes[0].model_copy(
        update={
            "timing": MarketTimingQualification(
                acquired_at=NOW,
                qualification=TimingQualification.UNQUALIFIED,
                freshness_basis=FreshnessBasis.ACQUISITION_TIME_ONLY,
            )
        }
    )
    changed_chain = chain.model_copy(update={"quotes": (quote, *chain.quotes[1:])})
    changed_capture = evidence.derivatives.model_copy(update={"chains": (changed_chain,)})
    changed_evidence = evidence.model_copy(update={"derivatives": changed_capture})
    result = admit_request(
        request(a4, evidence=changed_evidence),
        a4,
        changed_evidence,
        deterministic_policy(),
    )
    assert result.outcome is AdmissionOutcome.INSUFFICIENT_EVIDENCE
    assert result.reason_codes == ("QUOTE_TIMING_UNQUALIFIED_OR_STALE",)


def test_stale_upstream_is_insufficient_and_uses_explicit_cutoff() -> None:
    a4 = a4_result()
    evidence = bundle(a4)
    stale = evidence.model_copy(
        update={
            "upstream_a4": evidence.upstream_a4.model_copy(
                update={"evidence_as_of": NOW - timedelta(days=2)}
            )
        }
    )
    result = admit_request(request(a4, evidence=stale), a4, stale, deterministic_policy())
    assert result.outcome is AdmissionOutcome.INSUFFICIENT_EVIDENCE
    assert result.reason_codes == ("A4_EVIDENCE_STALE_OR_FUTURE",)


def test_same_captured_inputs_replay_exactly_without_current_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import socket

    def fail_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("A6.1 replay attempted network access")

    monkeypatch.setattr(socket, "socket", fail_network)
    a4 = a4_result()
    evidence = bundle(a4)
    value = request(a4, evidence=evidence)
    recorded = admit_request(value, a4, evidence, deterministic_policy())
    replayed = verify_admission_replay(recorded, value, a4, evidence, deterministic_policy())
    assert replayed == recorded


def test_semantic_change_changes_identity_and_tamper_fails_replay() -> None:
    a4 = a4_result()
    evidence = bundle(a4)
    value = request(a4, evidence=evidence)
    recorded = admit_request(value, a4, evidence, deterministic_policy())
    changed = value.model_copy(update={"authority_refs": ("authority:a6-different",)})
    changed_result = admit_request(changed, a4, evidence, deterministic_policy())
    assert changed_result.semantic_fingerprint != recorded.semantic_fingerprint
    tampered = recorded.model_copy(update={"reason_codes": ("TAMPERED",)})
    with pytest.raises(A6ReplayIntegrityError):
        verify_admission_replay(tampered, value, a4, evidence, deterministic_policy())


def test_fingerprint_rejects_secret_and_local_path_content() -> None:
    from tiaf.trade_expression import semantic_fingerprint

    with pytest.raises(ValueError):
        semantic_fingerprint({"api_key": "not-permitted"})
    with pytest.raises(ValueError):
        semantic_fingerprint({"artifact": "/tmp/private.json"})
