"""Offline baseline replay, decision records, and exact semantic diffing."""

import hashlib
from datetime import datetime
from typing import cast
from uuid import NAMESPACE_URL, uuid5

from pydantic import JsonValue

from tiaf.baseline import BaselineEngine, OpportunityAssessment, OpportunityRanking

from .errors import ReplayError, SnapshotIntegrityError
from .models import (
    BaselineRunRecord,
    ComponentScoreRecord,
    EvidenceSnapshot,
    FieldDifference,
    RankingContext,
    ReplayRequest,
    ReplayResult,
)
from .snapshot import canonical_json, semantic_fingerprint


def _json_value(value: object) -> JsonValue:
    return cast(JsonValue, value)


def field_differences(expected: JsonValue, actual: JsonValue) -> tuple[FieldDifference, ...]:
    """Return stable leaf-level differences for JSON-compatible values."""
    differences: list[FieldDifference] = []

    def visit(left: JsonValue, right: JsonValue, path: str) -> None:
        if isinstance(left, dict) and isinstance(right, dict):
            for key in sorted(set(left) | set(right)):
                child = f"{path}.{key}" if path else key
                if key not in left:
                    differences.append(
                        FieldDifference(path=child, expected=None, actual=right[key])
                    )
                elif key not in right:
                    differences.append(
                        FieldDifference(path=child, expected=left[key], actual=None)
                    )
                else:
                    visit(left[key], right[key], child)
            return
        if isinstance(left, list) and isinstance(right, list):
            for index in range(max(len(left), len(right))):
                child = f"{path}[{index}]"
                if index >= len(left):
                    differences.append(
                        FieldDifference(path=child, expected=None, actual=right[index])
                    )
                elif index >= len(right):
                    differences.append(
                        FieldDifference(path=child, expected=left[index], actual=None)
                    )
                else:
                    visit(left[index], right[index], child)
            return
        if left != right:
            differences.append(FieldDifference(path=path or "$", expected=left, actual=right))

    visit(expected, actual, "")
    return tuple(differences)


def _verify_snapshot(snapshot: EvidenceSnapshot) -> None:
    expected = semantic_fingerprint(
        snapshot.decision_request,
        policy_id=snapshot.policy_id,
        producer_id=snapshot.producer_id,
        producer_version=snapshot.producer_version,
        benchmark_symbol=snapshot.benchmark_symbol,
        context_references=snapshot.context_references,
        fingerprint_schema_version=snapshot.fingerprint_schema_version,
    )
    if expected != snapshot.fingerprint:
        raise SnapshotIntegrityError("snapshot evidence fingerprint mismatch")


def replay(request: ReplayRequest) -> ReplayResult:
    """Replay only frozen evidence; no provider, resolver, clock, or outcome is consulted."""
    snapshot = request.snapshot
    policy = request.policy
    _verify_snapshot(snapshot)
    if (
        policy.policy_id != snapshot.policy_id
        or policy.policy_version != snapshot.policy_version
        or policy.trade_style is not snapshot.trade_style
    ):
        raise ReplayError("replay policy identity/style does not match snapshot")
    assessment = BaselineEngine((policy,)).assess(snapshot.decision_request, policy=policy)
    expected_json = (
        request.expected_assessment.model_dump(mode="json")
        if request.expected_assessment is not None
        else None
    )
    actual_json = assessment.model_dump(mode="json")
    differences = (
        field_differences(_json_value(expected_json), _json_value(actual_json))
        if expected_json is not None
        else ()
    )
    policy_digest = hashlib.sha256(
        canonical_json(policy.model_dump(mode="json")).encode("utf-8")
    ).hexdigest()
    replay_id = str(
        uuid5(
            NAMESPACE_URL,
            f"tiaf:replay:{snapshot.fingerprint}:{policy_digest}",
        )
    )
    return ReplayResult(
        replay_id=replay_id,
        snapshot_id=snapshot.snapshot_id,
        evidence_fingerprint=snapshot.fingerprint,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        assessment=assessment,
        exact_match=None if expected_json is None else not differences,
        differences=differences,
        replay_time=request.replay_time,
    )


def create_run_record(
    snapshot: EvidenceSnapshot,
    assessment: OpportunityAssessment,
    *,
    recorded_at: datetime,
    ranking: OpportunityRanking | None = None,
) -> BaselineRunRecord:
    """Freeze an assessment projection separately from its evidence and later outcome."""
    if (
        assessment.request_id != snapshot.decision_request.request_id
        or assessment.subject != snapshot.subject
        or assessment.policy_id != snapshot.policy_id
        or assessment.policy_version != snapshot.policy_version
    ):
        raise ReplayError("assessment does not belong to evidence snapshot")
    ranking_context = None
    if ranking is not None:
        item = next(
            (
                candidate
                for candidate in ranking.items
                if candidate.assessment_id == assessment.assessment_id
            ),
            None,
        )
        if assessment.assessment_id not in {
            candidate.assessment_id for candidate in ranking.assessments
        }:
            raise ReplayError("ranking does not retain assessment")
        ranking_context = RankingContext(
            ranking_id=ranking.ranking_id,
            original_rank=item.rank if item is not None else None,
            requested_top_n=ranking.requested_top_n,
            input_universe=ranking.input_universe,
        )
    ranking_identity = ranking_context.model_dump_json() if ranking_context else "none"
    run_id = str(
        uuid5(
            NAMESPACE_URL,
            f"tiaf:baseline-run:{snapshot.fingerprint}:{assessment.assessment_id}:"
            f"{ranking_identity}",
        )
    )
    return BaselineRunRecord(
        run_id=run_id,
        producer_id=snapshot.producer_id,
        producer_version=snapshot.producer_version,
        evidence_snapshot_id=snapshot.snapshot_id,
        evidence_fingerprint=snapshot.fingerprint,
        subject=assessment.subject,
        horizon=assessment.horizon,
        trade_style=assessment.trade_style,
        policy_id=assessment.policy_id,
        policy_version=assessment.policy_version,
        assessment=assessment,
        candidate_class=assessment.candidate_class,
        direction=assessment.market_state.direction,
        opportunity_score=assessment.opportunity_score,
        component_scores=tuple(
            ComponentScoreRecord(component=item.component, score=item.score)
            for item in assessment.market_state.components
        ),
        reasons=assessment.explanation_codes,
        quality=assessment.market_state.quality,
        warnings=assessment.warnings,
        ranking_context=ranking_context,
        decision_at=assessment.created_at,
        recorded_at=recorded_at,
    )
