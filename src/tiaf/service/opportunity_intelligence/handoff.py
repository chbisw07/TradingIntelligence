"""Read-only captured handoff validation and typed detail extraction."""

import json
from collections.abc import Callable
from typing import Any

from tiaf.agents import AgentOpinionV2, SpecialistId
from tiaf.agents.specialists import (
    derivatives_context_assessment_from_opinion,
    fundamental_assessment_from_opinion,
    macro_assessment_from_opinion,
    news_event_assessment_from_opinion,
    opportunity_quality_assessment_from_opinion,
    opportunity_risk_assessment_from_opinion,
    relative_assessment_from_opinion,
    sector_assessment_from_opinion,
    technical_assessment_from_opinion,
)
from tiaf.baseline.enums import BaselineDirection, CandidateClass
from tiaf.baseline.models import OpportunityAssessment as BaselineAssessment
from tiaf.contracts import ContractModel
from tiaf.data import InstrumentType
from tiaf.planner.digests import digest
from tiaf.planner.policy import consumption_digest, invocation_digest
from tiaf.workflows.records import OrchestrationRunRecord
from tiaf.workflows.replay import replay_recorded

from .contracts import BaselineView, CaptureIntegrityError, OpportunityIntelligenceRequest

EXTRACTORS: dict[SpecialistId, Callable[[AgentOpinionV2], ContractModel]] = {
    SpecialistId.TECHNICAL: technical_assessment_from_opinion,
    SpecialistId.FUNDAMENTAL: fundamental_assessment_from_opinion,
    SpecialistId.NEWS_EVENT: news_event_assessment_from_opinion,
    SpecialistId.RELATIVE_STRENGTH: relative_assessment_from_opinion,
    SpecialistId.SECTOR: sector_assessment_from_opinion,
    SpecialistId.MACRO: macro_assessment_from_opinion,
    SpecialistId.DERIVATIVES_CONTEXT: derivatives_context_assessment_from_opinion,
    SpecialistId.OPPORTUNITY_QUALITY: opportunity_quality_assessment_from_opinion,
    SpecialistId.OPPORTUNITY_RISK: opportunity_risk_assessment_from_opinion,
}


def detail(opinion: AgentOpinionV2) -> dict[str, Any]:
    if opinion.specialist_detail_schema_id is None:
        return {}
    if opinion.specialist not in EXTRACTORS:
        raise CaptureIntegrityError("unsupported specialist detail")
    result = EXTRACTORS[opinion.specialist](opinion)
    data = result.model_dump(mode="json")
    expected_policy = {
        "DERIVATIVES_CONTEXT": "tiaf.a3-7-opportunity-context",
        "OPPORTUNITY_QUALITY": "tiaf.a3-7-opportunity-context",
        "OPPORTUNITY_RISK": "tiaf.a3-7-opportunity-context",
    }.get(
        opinion.specialist.value,
        f"tiaf.{opinion.specialist.value.lower().replace('_', '-')}-specialist",
    )
    if opinion.specialist is SpecialistId.RELATIVE_STRENGTH:
        expected_policy = "tiaf.relative-specialist"
    if data.get("policy_id") != expected_policy or data.get("schema_version") != "1.0":
        raise CaptureIntegrityError("unsupported typed detail policy/schema")
    if (
        data.get("policy_version") != "1.0"
        or data.get("specialist_version") != "1.0"
        or data.get("stance") != opinion.stance.value
    ):
        raise CaptureIntegrityError("unsupported or inconsistent typed detail version/stance")
    return data


def validate_handoff(request: OpportunityIntelligenceRequest) -> OrchestrationRunRecord:
    try:
        capture = json.loads(request.capture_json)
        if request.capture_checksum != capture["checksum"]:
            raise ValueError("request/capture checksum mismatch")
        record = replay_recorded(request.capture_json)
        if record.schema_version != "1.0" or record.result.schema_version != "1.0":
            raise ValueError("unsupported orchestration schema")
        subject = record.request.subject
        instrument = (
            record.request.instrument.underlying_type or record.request.instrument.instrument_type
        )
        if instrument not in {InstrumentType.EQUITY, InstrumentType.INDEX}:
            raise ValueError("unsupported underlying instrument")
        if len({o.specialist for o in record.result.opinions}) != len(record.result.opinions):
            raise ValueError("multiple active opinions for a specialist")
        nodes = {n.node_id: n for n in record.plans[-1].nodes}
        specs = {s.capability.specialist: s for s in record.plans[-1].registry}
        a2_refs = {r.evidence_id: r for r in record.request.inventory.a2_pack.references}
        if any(s.capability.specialist_version != "1.0" for s in specs.values()):
            raise ValueError("unsupported captured registry version")
        for attempt in record.attempts:
            if attempt.node_id not in nodes:
                raise ValueError("attempt has no selected node")
            run = attempt.record
            if run is None:
                continue
            if (
                run.specialist != nodes[attempt.node_id].specialist
                or run.request.subject != subject
                or run.request.horizon != record.request.horizon
                or run.request.created_at > record.request.as_of
                or run.request.instrument_type != instrument
                or run.request.deterministic_baseline_reference != record.result.a2_reference
            ):
                raise ValueError("invocation context identity mismatch")
            spec = specs[run.specialist]
            if (
                invocation_digest(record.request, spec, run.evidence_pack.references)
                != attempt.input_digest
            ):
                raise ValueError("original invocation pack digest mismatch")
            if (
                consumption_digest(record.request, spec, run.evidence_pack.references)
                != attempt.consumed_digest
            ):
                raise ValueError("consumed input digest mismatch")
            if run.request.evidence_fingerprint != attempt.input_digest:
                raise ValueError("request input fingerprint mismatch")
            refs = {r.evidence_id: r for r in run.evidence_pack.references}
            for ref in refs.values():
                if ref.evidence_id in a2_refs and ref != a2_refs[ref.evidence_id]:
                    raise ValueError("invocation changed original A2 evidence")
                if any(
                    t is not None and t > record.request.as_of
                    for t in (ref.observed_at, ref.acquired_at)
                ):
                    raise ValueError("future captured evidence")
                if any(f.as_of > record.request.as_of for f in ref.facts):
                    raise ValueError("future factual evidence")
            opinion = run.opinion
            if opinion is None:
                continue
            if (
                opinion.evidence_quality != run.evidence_pack.overall_quality
                or opinion.evidence_freshness != run.evidence_pack.overall_freshness
                or opinion.confidence.evidence_coverage != run.evidence_pack.evidence_coverage
            ):
                raise ValueError("opinion quality/coverage differs from original pack")
            for claim in opinion.evidence_claims:
                if claim.as_of > record.request.as_of:
                    raise ValueError("future opinion claim")
                for citation in claim.citations:
                    if (
                        citation.evidence_id not in refs
                        or refs[citation.evidence_id].evidence_type != claim.evidence_type
                    ):
                        raise ValueError("unresolved or semantically mismatched citation")
            if opinion.produced_at > record.request.as_of or opinion.policy_version != "1.0":
                raise ValueError("unsupported opinion time/policy")
            ids = set(opinion.supporting_evidence_ids) | set(opinion.contradictory_evidence_ids)
            ids |= {c.evidence_id for claim in opinion.evidence_claims for c in claim.citations}
            if not ids <= set(refs):
                raise ValueError("unresolved opinion citation")
            decoded = detail(opinion)
            for group_name in ("evidence_ids_by_dimension", "evidence_ids_by_family"):
                for _, evidence_ids in decoded.get(group_name, []):
                    if not set(evidence_ids) <= set(refs):
                        raise ValueError("unresolved typed detail evidence")
            for conflict in decoded.get("contradictions", ()):
                if not set(conflict.get("evidence_ids", ())) <= set(refs):
                    raise ValueError("unresolved typed contradiction citation")
        for outcome in record.result.outcomes:
            latest = next(a for a in reversed(record.attempts) if a.node_id == outcome.node_id)
            if (
                outcome.run_record_id != (latest.record.record_id if latest.record else None)
                or outcome.status != latest.status
                or outcome.required != nodes[outcome.node_id].required
            ):
                raise ValueError("outcome points to wrong invocation")
        opinions = {
            a.record.opinion.opinion_id: a.record.opinion
            for a in record.attempts
            if a.record is not None and a.record.opinion is not None
        }
        for projection in record.projections:
            opinion = opinions.get(projection.source_opinion.opinion_id)
            if opinion != projection.source_opinion:
                raise ValueError("projection lost original opinion lineage")
            decoded = detail(projection.source_opinion)
            if any(decoded.get(f.locator) != f.value for f in projection.fields):
                raise ValueError("projection changed typed source meaning")
            if projection.reference is not None:
                expected = {f.metric: f.value for f in projection.fields}
                if any(expected.get(f.metric_id) != f.value for f in projection.reference.facts):
                    raise ValueError("projection reference differs from typed fields")
        identity_fields = {
            "MarketIntelligenceRun": "run_id",
            "AuthoritativeConfirmationResult": "confirmation_id",
            "DeepResearchResult": "research_id",
            "SparseEvidenceGraph": "graph_id",
            "AgentRunRecord": "record_id",
        }
        for artifact in record.artifacts:
            data = json.loads(artifact.canonical_json)
            if (
                data.get(identity_fields[artifact.kind]) != artifact.artifact_id
                or data.get("schema_version") != "1.0"
            ):
                raise ValueError("artifact identity/schema mismatch")
            context = (
                data.get("context", {})
                if artifact.kind == "DeepResearchResult"
                else data.get("request", {})
            )
            artifact_subject = context.get("subject", context.get("claim", {}).get("subject"))
            if artifact_subject is not None and artifact_subject != subject:
                raise ValueError("artifact subject mismatch")
            if context.get("horizon") is not None and (
                context["horizon"] != record.request.horizon.model_dump(mode="json")
            ):
                raise ValueError("artifact horizon mismatch")
        artifact_ids = {a.artifact_id for a in record.artifacts}
        if (
            not set(
                (
                    *record.result.confirmation_ids,
                    *record.result.research_ids,
                    *record.result.graph_ids,
                )
            )
            <= artifact_ids
        ):
            raise ValueError("unresolved result artifact")
        return record
    except (ValueError, TypeError, KeyError, StopIteration) as exc:
        raise CaptureIntegrityError(str(exc)) from exc


def baseline_view(record: OrchestrationRunRecord) -> BaselineView:
    pack = record.request.inventory.a2_pack
    values: dict[str, object] = {}
    ids: set[str] = set()
    for ref in pack.references:
        for fact in ref.facts:
            if fact.metric_id not in {
                "baseline.direction",
                "baseline.candidate_class",
                "baseline.opportunity_score",
                "baseline.eligible",
            }:
                continue
            if fact.metric_id in values and values[fact.metric_id] != fact.value:
                raise CaptureIntegrityError("contradictory captured baseline copies")
            values[fact.metric_id] = fact.value
            ids.add(ref.evidence_id)
    full = pack.metadata.get("baseline_assessment")
    assessment = BaselineAssessment.model_validate(full) if full is not None else None
    if assessment is not None:
        if (
            assessment.assessment_id != record.result.a2_reference
            or assessment.subject != record.request.subject
            or assessment.horizon != record.request.horizon
            or assessment.created_at > record.request.as_of
        ):
            raise CaptureIntegrityError("captured full baseline context mismatch")
        expected = {
            "baseline.direction": assessment.market_state.direction.value,
            "baseline.candidate_class": assessment.candidate_class.value,
            "baseline.opportunity_score": assessment.opportunity_score,
            "baseline.eligible": assessment.eligible,
        }
        if any(key in values and values[key] != value for key, value in expected.items()):
            raise CaptureIntegrityError("full baseline and pack projection disagree")
        values.update(expected)
    common: dict[str, Any] = dict(
        assessment_id=record.result.a2_reference,
        evidence_fingerprint=record.result.a2_fingerprint,
        evidence_ids=tuple(sorted(ids)),
        content_source=f"a2-pack:{pack.pack_id}",
        pack_checksum=digest(pack),
        full_assessment_available=assessment is not None,
        captured_assessment=assessment,
    )
    if (
        not {"baseline.direction", "baseline.candidate_class", "baseline.opportunity_score"}
        <= values.keys()
    ):
        return BaselineView(**common, availability="MISSING_CONTENT")
    try:
        direction = BaselineDirection(str(values["baseline.direction"]))
        candidate = CandidateClass(str(values["baseline.candidate_class"]))
        score = values["baseline.opportunity_score"]
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError("invalid baseline score")
        eligible = values.get("baseline.eligible")
        if eligible is not None and (
            not isinstance(eligible, bool) or eligible != (candidate != CandidateClass.NO_TRADE)
        ):
            raise ValueError("invalid captured baseline eligibility")
        return BaselineView(
            **common,
            availability="CAPTURED_PROJECTION",
            direction=direction,
            candidate_class=candidate,
            opportunity_score=score,
            eligible=eligible,
            eligibility_basis="CAPTURED" if eligible is not None else "NOT_CAPTURED",
        )
    except ValueError as exc:
        raise CaptureIntegrityError(str(exc)) from exc


def request_from_capture(
    content: str, *, request_id: str, policy: object
) -> OpportunityIntelligenceRequest:
    try:
        return OpportunityIntelligenceRequest.model_validate(
            {
                "request_id": request_id,
                "capture_json": content,
                "capture_checksum": json.loads(content)["checksum"],
                "policy": policy,
            }
        )
    except (ValueError, TypeError, KeyError) as exc:
        raise CaptureIntegrityError(str(exc)) from exc
