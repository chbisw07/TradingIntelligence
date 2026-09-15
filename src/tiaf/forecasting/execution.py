"""Lean immutable execution facts; no registry, implementation or clock discovery."""

from typing import Annotated, Literal, Self

from pydantic import Field, StrictFloat, StrictInt, model_validator

from tiaf.planner.models import Sha256

from .identity import ArtifactReference, ForecastContract, ForecastDateTime, LogicalId

Zero = Annotated[StrictInt, Field(ge=0, le=0)]
Count = Annotated[StrictInt, Field(ge=0, le=20)]


class InvocationUsage(ForecastContract):
    schema_id: Literal["tiaf.ff.invocation-usage"] = "tiaf.ff.invocation-usage"
    attempt_id: LogicalId | None
    attempts: Annotated[StrictInt, Field(ge=0, le=1)]
    started_at: ForecastDateTime | None
    completed_at: ForecastDateTime | None
    duration_seconds: Annotated[StrictFloat, Field(ge=0, allow_inf_nan=False)]
    external_provider_calls: Zero = 0
    external_model_calls: Zero = 0
    input_model_tokens: Zero = 0
    output_model_tokens: Zero = 0
    external_model_cost: Zero = 0
    local_cost: Literal["UNPRICED"] = "UNPRICED"

    @model_validator(mode="after")
    def honest_attempt(self) -> Self:
        if self.attempts == 0:
            if any(x is not None for x in (self.attempt_id, self.started_at, self.completed_at)):
                raise ValueError("UNINVOKED_HAS_NO_ATTEMPT_CLOCKS")
            if self.duration_seconds != 0:
                raise ValueError("UNINVOKED_HAS_NO_INFERENCE_DURATION")
        elif self.attempt_id is None or self.started_at is None or self.completed_at is None:
            raise ValueError("ATTEMPT_REQUIRES_ID_AND_CLOCKS")
        elif self.started_at > self.completed_at:
            raise ValueError("ATTEMPT_CLOCK_REVERSED")
        return self


class SupportSummary(ForecastContract):
    artifact_ref: ArtifactReference
    positive_count: Count
    qualified_count: Count
    outcome_refs: tuple[ArtifactReference, ...] = Field(max_length=20)

    @model_validator(mode="after")
    def count_basis(self) -> Self:
        if (
            self.positive_count > self.qualified_count
            or len(self.outcome_refs) != self.qualified_count
        ):
            raise ValueError("SUPPORT_SUMMARY_COUNT_MISMATCH")
        if len(set(self.outcome_refs)) != len(self.outcome_refs):
            raise ValueError("SUPPORT_SUMMARY_DUPLICATE_OUTCOME")
        return self


class ForecastExecution(ForecastContract):
    schema_id: Literal["tiaf.ff.execution"] = "tiaf.ff.execution"
    descriptor_ref: ArtifactReference
    configuration_ref: ArtifactReference
    composition_ref: ArtifactReference
    support: SupportSummary | None
    usage: InvocationUsage


class PinnedVerification(ForecastContract):
    schema_id: Literal["tiaf.ff.pinned-verification"] = "tiaf.ff.pinned-verification"
    capture_ref: ArtifactReference
    status: Literal["VERIFIED", "MISMATCH", "UNVERIFIABLE"]
    reason: LogicalId
    verified_at: ForecastDateTime
    usage: InvocationUsage
    original_result_fingerprint: Sha256
    reconstructed_result_fingerprint: Sha256 | None = None

    @model_validator(mode="after")
    def verification_clocks(self) -> Self:
        if self.usage.completed_at is not None and self.usage.completed_at > self.verified_at:
            raise ValueError("VERIFICATION_PREDATES_ATTEMPT")
        if self.status == "VERIFIED" and (
            self.original_result_fingerprint != self.reconstructed_result_fingerprint
            or self.usage.attempts != 1
        ):
            raise ValueError("EXACT_VERIFICATION_REQUIRES_IDENTICAL_FINGERPRINT")
        return self
