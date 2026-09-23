"""Bounded immutable request/result and two-level provenance envelopes."""

from typing import Literal, Self

from pydantic import Field, model_validator

from tiaf.forecasting.enums import ForecastRealizationMode
from tiaf.forecasting.identity import ArtifactReference, ForecastDateTime, LogicalId
from tiaf.forecasting.identity import semantic_fingerprint as fingerprint

from .claims import EvaluableClaim, ResolutionContract
from .common import IntelligenceContract, Text, unique
from .identity import CapabilityDeclaration, ProducerIdentity, ServiceIdentity


class ContributorReference(IntelligenceContract):
    producer: ProducerIdentity
    output: ArtifactReference
    claim_ids: tuple[LogicalId, ...] = Field(default=(), max_length=64)

    @model_validator(mode="after")
    def distinct_claims(self) -> Self:
        unique(self.claim_ids, "CONTRIBUTOR_CLAIM")
        return self


class ResponseProvenance(IntelligenceContract):
    synthesizer: ProducerIdentity | None = None
    contributors: tuple[ContributorReference, ...] = Field(default=(), max_length=64)
    native_output: ArtifactReference | None = None

    @model_validator(mode="after")
    def unambiguous(self) -> Self:
        # One exact binding per producer ID in one response; conflicting versions reject too.
        unique(tuple(c.producer.producer_id for c in self.contributors), "CONTRIBUTOR_PRODUCER")
        ids = tuple(claim for c in self.contributors for claim in c.claim_ids)
        unique(ids, "CONTRIBUTOR_CLAIM")
        return self


class Explanation(IntelligenceContract):
    text: Text
    source: ArtifactReference | None = None


class Recommendation(IntelligenceContract):
    """Advisory text/reference only, never an executable instruction or grant."""

    text: Text
    source: ArtifactReference | None = None
    authority: Literal["ADVISORY_ONLY"] = "ADVISORY_ONLY"


class IntelligenceRequest(IntelligenceContract):
    schema_id: Literal["tiaf.ifl.request"] = "tiaf.ifl.request"
    request_id: LogicalId
    service: ServiceIdentity
    capability: CapabilityDeclaration
    expected_producer: ProducerIdentity
    information_cutoff: ForecastDateTime
    as_of: ForecastDateTime
    created_at: ForecastDateTime
    realization: ForecastRealizationMode
    style: Literal["EVALUABLE", "NON_EVALUABLE"]
    resolution: ResolutionContract | None = None
    inputs: tuple[ArtifactReference, ...] = Field(default=(), max_length=64)

    @model_validator(mode="after")
    def binding(self) -> Self:
        if (
            self.service != self.expected_producer.service
            or self.capability != self.expected_producer.capability
        ):
            raise ValueError("REQUEST_PRODUCER_BINDING_MISMATCH")
        if not self.information_cutoff <= self.as_of <= self.created_at:
            raise ValueError("REQUEST_CLOCK_ORDER")
        if (self.style == "EVALUABLE") != (self.resolution is not None):
            raise ValueError("REQUEST_RESOLUTION_REQUIRED_FOR_EVALUABLE")
        if self.resolution is not None:
            if self.resolution.claim_kind not in self.capability.claim_kinds:
                raise ValueError("REQUEST_KIND_NOT_DECLARED")
            if self.resolution.reference_at > self.as_of:
                raise ValueError("REQUEST_REFERENCE_AFTER_AS_OF")
        unique(self.inputs, "INPUT")
        return self


class IntelligenceResponse(IntelligenceContract):
    schema_id: Literal["tiaf.ifl.response"] = "tiaf.ifl.response"
    response_id: LogicalId
    request_id: LogicalId
    producer: ProducerIdentity
    created_at: ForecastDateTime
    style: Literal["EVALUABLE", "NON_EVALUABLE"]
    primary_claim: EvaluableClaim | None = None
    secondary_claims: tuple[EvaluableClaim, ...] = Field(default=(), max_length=64)
    evidence: tuple[ArtifactReference, ...] = Field(default=(), max_length=64)
    explanation: Explanation | None = None
    recommendations: tuple[Recommendation, ...] = Field(default=(), max_length=16)
    provenance: ResponseProvenance

    @model_validator(mode="after")
    def closure(self) -> Self:
        if (self.style == "EVALUABLE") != (self.primary_claim is not None):
            raise ValueError("EXACTLY_ONE_PRIMARY_REQUIRED_FOR_EVALUABLE")
        if self.style == "NON_EVALUABLE" and self.secondary_claims:
            raise ValueError("NON_EVALUABLE_CANNOT_HIDE_EVALUABLE_CLAIMS")
        synth = self.provenance.synthesizer
        if synth is not None and synth != self.producer:
            raise ValueError("SYNTHESIZER_MUST_BE_ACTUAL_PRODUCER")
        if self.provenance.contributors and synth is None:
            raise ValueError("CONTRIBUTORS_REQUIRE_SYNTHESIZER")
        contributors = {c.producer.producer_id: c for c in self.provenance.contributors}
        if self.producer.producer_id in contributors:
            raise ValueError("SYNTHESIZER_CANNOT_MASQUERADE_AS_CONTRIBUTOR")
        claims = self.secondary_claims
        if self.primary_claim is not None:
            if self.primary_claim.producer != self.producer:
                raise ValueError("PRIMARY_PRODUCER_MISMATCH")
            claims = (self.primary_claim, *claims)
        unique(tuple(c.claim_id for c in claims), "CLAIM_ID")
        unique(self.evidence, "EVIDENCE")
        contributor_claim_ids = {key for c in self.provenance.contributors for key in c.claim_ids}
        for claim in claims:
            if claim.request_id != self.request_id or claim.created_at > self.created_at:
                raise ValueError("CLAIM_RESPONSE_BINDING_MISMATCH")
            if claim.producer == self.producer and claim.claim_id in contributor_claim_ids:
                raise ValueError("CLAIM_ATTRIBUTED_TO_MULTIPLE_PRODUCERS")
            if claim.producer != self.producer:
                contributor = contributors.get(claim.producer.producer_id)
                if (
                    contributor is None
                    or contributor.producer != claim.producer
                    or claim.claim_id not in contributor.claim_ids
                ):
                    raise ValueError("CLAIM_CONTRIBUTOR_PROVENANCE_MISMATCH")
        return self

    def semantic_fingerprint(self) -> str:
        """Presentation text is excluded; complete serialization still preserves it."""
        admitted = IntelligenceResponse.model_validate(self.model_dump())
        return fingerprint(
            {
                "profile": "tiaf.ifl.response/1.0",
                "response": admitted.model_dump(exclude={"explanation", "recommendations"}),
            }
        )
