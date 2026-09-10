"""Bounded offline user-level acceptance for A3.10 hardening."""

import json

from _a3_10_cases import (
    BUILDER,
    CASES,
    NOW,
    AcceptanceCase,
    package_for,
    parity_packages,
)

from tiaf.a3_hardening import (
    CaptureOrigin,
    CorpusCase,
    DirectionAxis,
    FailureCategory,
    FailureCode,
    PackageIntegrityError,
    PolicyComparisonError,
    compare_a2_a3,
    compare_a3_policy,
    corpus_manifest,
    direction_axis,
    failure_event,
    replay_a3_package,
    summarize_a3_cost,
    summarize_a3_failures,
)
from tiaf.agents import AgentStance
from tiaf.baseline import BaselineDirection
from tiaf.service.opportunity_intelligence import default_policy


def _run_case(case: AcceptanceCase) -> tuple[dict[str, object], CorpusCase]:
    package = package_for(case)
    replay = replay_a3_package(package, replayed_at=NOW)
    comparison = compare_a2_a3(package, compared_at=NOW)
    cost = summarize_a3_cost(package, replay_execution_usage=replay.replay_usage)
    failures = summarize_a3_failures(package)
    probe = "PASS"
    injected_failure_codes: tuple[FailureCode, ...] = ()
    case_id = case.case_id
    if case_id == "A":
        assert comparison.direction_axis is DirectionAxis.ALIGNED
        probe = comparison.direction_axis.value
    elif case_id in {"B", "C"}:
        probe = comparison.opportunity_axis.value
    elif case_id == "D":
        assert DirectionAxis.NON_COMPARABLE is direction_axis(
            BaselineDirection.NEUTRAL, AgentStance.MIXED
        )
        probe = "NEUTRAL_AXIS_NON_COMPARABLE"
    elif case_id == "J":
        first = package.blobs[0].model_copy(update={"content": package.blobs[0].content + " "})
        tampered = package.model_copy(update={"blobs": (first, *package.blobs[1:])})
        try:
            replay_a3_package(tampered)
        except PackageIntegrityError:
            probe = "TAMPER_REJECTED"
        else:
            raise AssertionError("tampered package replayed")
    elif case_id == "K":
        unsupported = default_policy().model_copy(update={"version": "99.0"})
        try:
            compare_a3_policy(package, unsupported)
        except PolicyComparisonError:
            probe = "POLICY_MISMATCH_REJECTED"
        else:
            raise AssertionError("unsupported policy was accepted")
    elif case_id == "L":
        serial, graph = parity_packages()
        left, right = compare_a2_a3(serial), compare_a2_a3(graph)
        assert serial.manifest.package_id == graph.manifest.package_id
        assert serial.manifest.exact_package_checksum != graph.manifest.exact_package_checksum
        assert left.fingerprint == right.fingerprint
        probe = "SEMANTIC_PARITY"
    elif case_id == "F":
        assert FailureCode.RATE_LIMITED in {item.code for item in failures.events}
        assert cost.fallback_attempts == 1
        probe = "RATE_LIMITED_FALLBACK_CAPTURED"
    elif case_id == "G":
        injected = failure_event(
            category=FailureCategory.SPECIALIST,
            code=FailureCode.EXCEPTION,
            phase="DETERMINISTIC_OPTIONAL_FAILURE_PROBE",
            original_type="SyntheticOptionalSpecialistFailure",
            original_code="OPTIONAL_FIXTURE_FAILURE",
            original_message="offline optional failure fixture",
            terminal=False,
            affected_capabilities=("OPTIONAL_SPECIALIST",),
        )
        assert injected.original_code == "OPTIONAL_FIXTURE_FAILURE"
        injected_failure_codes = (injected.code,)
        probe = "OPTIONAL_FAILURE_ISOLATED"
    elif case_id in {"E", "H"}:
        probe = comparison.a3.state.value
    elif case_id == "I":
        assert FailureCode.BUDGET_EXHAUSTED in {item.code for item in failures.events}
        probe = "BUDGET_EXHAUSTED_CAPTURED"
    elif case_id == "M":
        assert cost.provider_monetary_cost.knowledge.value == "UNPRICED"
        probe = "UNPRICED_NOT_ZERO"
    elif case_id == "N":
        assert cost.model_monetary_cost.knowledge.value == "KNOWN_ZERO"
        assert cost.original_captured_usage.llm_calls == 0
        probe = "NO_LLM_KNOWN_ZERO"
    assert probe == case.expected_probe
    assert replay.semantic_match
    row = {
        "case": case_id,
        "name": case.name,
        "package_id": package.manifest.package_id,
        "replay": f"{replay.mode.value}/{replay.status}",
        "a2": {
            "direction": comparison.a2.direction,
            "class": comparison.a2.candidate_class,
            "score": comparison.a2.opportunity_score,
            "eligibility_basis": comparison.a2.eligibility_basis,
        },
        "a3": {
            "state": comparison.a3.state,
            "direction": comparison.a3.price_direction,
        },
        "axes": [comparison.direction_axis, comparison.opportunity_axis],
        "disagreements": comparison.disagreements,
        "additions": [
            [item.category, item.status, item.source_refs]
            for item in comparison.information_additions
        ],
        "failure_codes": [
            *(item.code for item in failures.events),
            *injected_failure_codes,
        ],
        "degradation": failures.degradation.status,
        "original_usage": cost.original_captured_usage.model_dump(mode="json"),
        "replay_usage": cost.replay_execution_usage.model_dump(mode="json"),
        "cost_knowledge": [
            cost.provider_monetary_cost.knowledge,
            cost.model_monetary_cost.knowledge,
        ],
        "semantic_fingerprint": package.manifest.package_semantic_fingerprint,
        "exact_checksum": package.manifest.exact_package_checksum,
        "gaps": comparison.a3.gaps,
        "probe": probe,
        "status": "PASS",
    }
    corpus_case = CorpusCase(
        case_id=case_id,
        package_id=package.manifest.package_id,
        origin=CaptureOrigin.SYNTHETIC,
        strata=case.strata,
        fixture_builder_version=BUILDER,
        source_reference=package.manifest.source_reference,
    )
    return row, corpus_case


def main() -> int:
    print("A3.10 OFFLINE ACCEPTANCE — synthetic/captured evidence, no market recommendation")
    rows_and_cases = tuple(_run_case(case) for case in CASES)
    for row, _case in rows_and_cases:
        print(json.dumps(row, sort_keys=True, default=str))
    manifest = corpus_manifest(
        "tiaf-a3.10-public-acceptance-v1",
        tuple(case for _row, case in rows_and_cases),
        created_at=NOW,
    )
    print(
        json.dumps(
            {
                "corpus_id": manifest.corpus_id,
                "cases": len(manifest.cases),
                "fingerprint": manifest.fingerprint,
                "origin": "SYNTHETIC",
            },
            sort_keys=True,
        )
    )
    print(f"PASS: {len(rows_and_cases)} / FAIL: 0 — offline, no live/provider/model calls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
