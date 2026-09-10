"""Composable A3.10 hardening evaluation and later-closure evidence seam."""

from datetime import datetime

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest

from .comparison import compare_a2_a3
from .contracts import (
    A3ClosureReadinessRecord,
    A3CorpusManifest,
    A3HardeningResult,
    CaptureOrigin,
    ClosureReadiness,
    CorpusCase,
    EvidenceStatus,
    HardeningCheck,
    MilestoneEvidence,
    PortableA3ReplayPackage,
)
from .cost import summarize_a3_cost
from .failures import summarize_a3_failures
from .replay import replay_a3_package, verify_a3_package


def evaluate_a3_hardening(
    package: PortableA3ReplayPackage,
    *,
    evaluated_at: datetime | None = None,
) -> A3HardeningResult:
    replay = replay_a3_package(package, replayed_at=evaluated_at)
    verification = verify_a3_package(package, verified_at=evaluated_at)
    comparison = compare_a2_a3(package, compared_at=evaluated_at)
    cost = summarize_a3_cost(package, replay_execution_usage=replay.replay_usage)
    failures = summarize_a3_failures(package)
    checks = (
        HardeningCheck(
            check_id="PACKAGE_AND_RECORDED_REPLAY",
            status=EvidenceStatus.PASS if replay.semantic_match else EvidenceStatus.FAIL,
            evidence_refs=(replay.replay_id, replay.fingerprint),
        ),
        HardeningCheck(
            check_id="DETERMINISTIC_COMPONENT_VERIFICATION",
            status=EvidenceStatus.PASS if verification.passed else EvidenceStatus.FAIL,
            evidence_refs=(verification.verification_id, verification.fingerprint),
        ),
        HardeningCheck(
            check_id="A2_A3_OBSERVATIONAL_COMPARISON",
            status=EvidenceStatus.PASS,
            evidence_refs=(comparison.comparison_id, comparison.fingerprint),
        ),
        HardeningCheck(
            check_id="LEAF_USAGE_RECONCILIATION",
            status=EvidenceStatus.PASS,
            evidence_refs=(cost.fingerprint,),
        ),
        HardeningCheck(
            check_id="FAILURE_AND_DEGRADATION_PROJECTION",
            status=EvidenceStatus.PASS,
            evidence_refs=(failures.fingerprint,),
        ),
    )
    passed = all(item.status is EvidenceStatus.PASS for item in checks if item.required)
    payload = {
        "replay_fingerprint": replay.fingerprint,
        "verification_fingerprint": verification.fingerprint,
        "comparison_fingerprint": comparison.fingerprint,
        "cost_fingerprint": cost.fingerprint,
        "failure_fingerprint": failures.fingerprint,
        "checks": [item.model_dump(mode="json") for item in checks],
        "passed": passed,
    }
    fingerprint = digest(payload)
    return A3HardeningResult(
        evaluation_id=f"a3-hardening:{fingerprint[:24]}",
        package_id=package.manifest.package_id,
        replay_fingerprint=replay.fingerprint,
        verification_fingerprint=verification.fingerprint,
        comparison_fingerprint=comparison.fingerprint,
        cost_fingerprint=cost.fingerprint,
        failure_fingerprint=failures.fingerprint,
        checks=checks,
        passed=passed,
        evaluated_at=evaluated_at or datetime.now(TIAF_TIMEZONE),
        fingerprint=fingerprint,
    )


def corpus_manifest(
    corpus_id: str,
    cases: tuple[CorpusCase, ...],
    *,
    created_at: datetime | None = None,
) -> A3CorpusManifest:
    fingerprint = digest(
        {
            "corpus_id": corpus_id,
            "cases": [item.model_dump(mode="json") for item in cases],
        }
    )
    return A3CorpusManifest(
        corpus_id=corpus_id,
        cases=cases,
        created_at=created_at or datetime.now(TIAF_TIMEZONE),
        fingerprint=fingerprint,
    )


def synthetic_corpus_case(
    case_id: str,
    package: PortableA3ReplayPackage,
    *,
    strata: tuple[str, ...],
    source_reference: str,
    fixture_builder_version: str,
) -> CorpusCase:
    return CorpusCase(
        case_id=case_id,
        package_id=package.manifest.package_id,
        origin=CaptureOrigin.SYNTHETIC,
        strata=strata,
        source_reference=source_reference,
        fixture_builder_version=fixture_builder_version,
    )


def closure_readiness_record(
    evidence: tuple[MilestoneEvidence, ...],
    *,
    unresolved_deferrals: tuple[str, ...],
    known_risks: tuple[str, ...],
    assessed_at: datetime | None = None,
) -> A3ClosureReadinessRecord:
    readiness = (
        ClosureReadiness.READY_FOR_CLOSURE_REVIEW
        if all(item.status is EvidenceStatus.PASS for item in evidence if item.required)
        else ClosureReadiness.NOT_READY
    )
    payload = {
        "baseline_tag": "tiaf-a3.9",
        "evidence": [item.model_dump(mode="json") for item in evidence],
        "unresolved_deferrals": unresolved_deferrals,
        "known_risks": known_risks,
    }
    fingerprint = digest(payload)
    return A3ClosureReadinessRecord(
        closure_record_id=f"a3-closure:{fingerprint[:24]}",
        evidence=evidence,
        unresolved_deferrals=unresolved_deferrals,
        known_risks=known_risks,
        readiness=readiness,
        assessed_at=assessed_at or datetime.now(TIAF_TIMEZONE),
        fingerprint=fingerprint,
    )
