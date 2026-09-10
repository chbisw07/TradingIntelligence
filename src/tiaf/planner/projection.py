"""Typed output-to-input projection: quotes interpretations, never invents raw facts."""

from collections.abc import Callable
from typing import Literal, Self

from pydantic import model_validator

from tiaf.agents import AgentEvidenceReference, AgentOpinionV2, AgentStance, SpecialistId
from tiaf.agents.evidence import EvidenceFact, EvidenceFactKind
from tiaf.agents.specialists import (
    derivatives_context_assessment_from_opinion,
    fundamental_assessment_from_opinion,
    macro_assessment_from_opinion,
    news_event_assessment_from_opinion,
    relative_assessment_from_opinion,
    sector_assessment_from_opinion,
    technical_assessment_from_opinion,
)
from tiaf.context import EvidenceStatus
from tiaf.contracts import ContractModel, EvidenceSource, EvidenceType, FreshnessState

from .digests import digest
from .models import Sha256

EXTRACTORS: dict[SpecialistId, Callable[[AgentOpinionV2], ContractModel]] = {
    SpecialistId.TECHNICAL: technical_assessment_from_opinion,
    SpecialistId.FUNDAMENTAL: fundamental_assessment_from_opinion,
    SpecialistId.NEWS_EVENT: news_event_assessment_from_opinion,
    SpecialistId.RELATIVE_STRENGTH: relative_assessment_from_opinion,
    SpecialistId.SECTOR: sector_assessment_from_opinion,
    SpecialistId.MACRO: macro_assessment_from_opinion,
    SpecialistId.DERIVATIVES_CONTEXT: derivatives_context_assessment_from_opinion,
}
FIELDS: dict[SpecialistId, tuple[EvidenceType, str, tuple[tuple[str, str], ...]]] = {
    SpecialistId.TECHNICAL: (
        EvidenceType.TECHNICAL,
        "technical",
        (
            ("trend_state", "trend"),
            ("momentum_state", "momentum"),
            ("structure_state", "structure"),
            ("breakout_state", "breakout"),
            ("participation_state", "participation"),
            ("volatility_state", "volatility"),
            ("mtf_state", "mtf"),
            ("extension_state", "extension"),
            ("remaining_room", "remaining_room"),
        ),
    ),
    SpecialistId.FUNDAMENTAL: (
        EvidenceType.FUNDAMENTAL,
        "fundamental",
        (
            ("stance", "stance"),
            ("balance_sheet_state", "balance_sheet"),
            ("cash_flow_state", "cash_flow"),
        ),
    ),
    SpecialistId.NEWS_EVENT: (
        EvidenceType.NEWS,
        "news_event",
        (
            ("stance", "stance"),
            ("materiality", "materiality"),
            ("execution_risk", "execution_risk"),
            ("catalyst_direction", "direction"),
        ),
    ),
    SpecialistId.RELATIVE_STRENGTH: (
        EvidenceType.RELATIVE_STRENGTH,
        "relative",
        (
            ("stance", "stance"),
            ("mtf_alignment", "mtf"),
        ),
    ),
    SpecialistId.SECTOR: (EvidenceType.SECTOR, "sector", (("stance", "stance"),)),
    SpecialistId.MACRO: (EvidenceType.MACRO, "macro", (("stance", "stance"),)),
    SpecialistId.DERIVATIVES_CONTEXT: (
        EvidenceType.DERIVATIVES,
        "derivatives_context",
        (
            ("stance", "stance"),
            ("volatility_state", "volatility"),
            ("crowding_state", "crowding"),
            ("expiry_proximity", "expiry"),
            ("liquidity_state", "liquidity"),
        ),
    ),
}


class ProjectedField(ContractModel):
    locator: str
    metric: str
    value: str
    source_evidence_ids: tuple[str, ...]
    epistemic: Literal["INFERENCE"] = "INFERENCE"


class SpecialistOutputProjection(ContractModel):
    version: Literal["1.0"] = "1.0"
    source_opinion: AgentOpinionV2
    input_digest: Sha256
    detail_schema: str | None
    fields: tuple[ProjectedField, ...]
    reference: AgentEvidenceReference | None
    gaps: tuple[str, ...] = ()

    @model_validator(mode="after")
    def attributed(self) -> Self:
        if self.source_opinion.evidence_fingerprint != self.input_digest:
            raise ValueError("projection input lineage mismatch")
        cited = {
            c.evidence_id for claim in self.source_opinion.evidence_claims for c in claim.citations
        }
        if any(not set(f.source_evidence_ids) <= cited for f in self.fields):
            raise ValueError("projection cites evidence outside source opinion")
        if self.reference is not None and self.reference.source is not EvidenceSource.DERIVED:
            raise ValueError("projection must declare derived source")
        return self

    def field_digest(self) -> str:
        return digest([f.model_dump(mode="json") for f in self.fields])


def project_opinion(opinion: AgentOpinionV2) -> SpecialistOutputProjection:
    fields: list[ProjectedField] = []
    gaps: list[str] = []
    reference: AgentEvidenceReference | None = None
    cited = tuple(
        sorted({c.evidence_id for claim in opinion.evidence_claims for c in claim.citations})
    )
    if opinion.specialist not in EXTRACTORS:
        gaps.append("NO_DOWNSTREAM_PROJECTION")
    elif opinion.stance in {AgentStance.ABSTAIN, AgentStance.INSUFFICIENT_EVIDENCE} or not cited:
        gaps.append("NON_SUBSTANTIVE_OPINION")
    else:
        try:
            detail = EXTRACTORS[opinion.specialist](opinion).model_dump(mode="json")
        except (ValueError, TypeError):
            gaps.append("INCOMPATIBLE_DETAIL_SCHEMA")
        else:
            evidence_type, prefix, mapping = FIELDS[opinion.specialist]
            for field, metric in mapping:
                value = detail.get(field)
                if not isinstance(value, str) or value in {
                    "UNKNOWN",
                    "INSUFFICIENT_EVIDENCE",
                    "ABSTAIN",
                    "NOT_APPLICABLE",
                }:
                    gaps.append(f"UNAVAILABLE_FIELD:{field}")
                    continue
                fields.append(
                    ProjectedField(
                        locator=field,
                        metric=f"{prefix}.{metric}",
                        value=value,
                        source_evidence_ids=cited,
                    )
                )
            if fields:
                # Content identity deliberately excludes a newly minted opinion/run ID.
                checksum = digest(
                    {
                        "fields": [f.model_dump(mode="json") for f in fields],
                        "quality": opinion.evidence_quality,
                        "freshness": opinion.evidence_freshness,
                        "as_of": opinion.produced_at.isoformat(),
                        "version": "1.0",
                    }
                )
                reference_id = f"projection:{opinion.specialist.value}:{checksum}"
                facts = tuple(
                    EvidenceFact(
                        fact_id=f"{reference_id}:{f.locator}",
                        kind=EvidenceFactKind.FEATURE,
                        metric_id=f.metric,
                        value=f.value,
                        as_of=opinion.produced_at,
                        quality=opinion.evidence_quality,
                        freshness=opinion.evidence_freshness,
                        source_evidence=f.source_evidence_ids,
                    )
                    for f in fields
                )
                reference = AgentEvidenceReference(
                    evidence_id=reference_id,
                    evidence_type=evidence_type,
                    subject=opinion.subject,
                    producer_id="tiaf.specialist-output-projection",
                    producer_version="1.0",
                    source=EvidenceSource.DERIVED,
                    availability=EvidenceStatus.STALE
                    if opinion.evidence_freshness is FreshnessState.STALE
                    else EvidenceStatus.PARTIAL,
                    quality=opinion.evidence_quality,
                    freshness=opinion.evidence_freshness,
                    observed_at=opinion.produced_at,
                    acquired_at=opinion.produced_at,
                    checksum=checksum,
                    facts=facts,
                    metadata={
                        "epistemic": "INFERENCE",
                        "detail_schema": opinion.specialist_detail_schema_id,
                        "projection_version": "1.0",
                        "origin": "RECORDED_SPECIALIST_LABEL",
                    },
                )
    return SpecialistOutputProjection(
        source_opinion=opinion,
        input_digest=opinion.evidence_fingerprint,
        detail_schema=opinion.specialist_detail_schema_id,
        fields=tuple(fields),
        reference=reference,
        gaps=tuple(gaps),
    )
