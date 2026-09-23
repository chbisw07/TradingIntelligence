"""Seven bounded claim values and pinned resolution instructions; no resolver."""

from typing import Annotated, Literal, Self

from pydantic import Field, StrictBool, model_validator

from tiaf.forecasting.enums import ForecastRealizationMode
from tiaf.forecasting.identity import ArtifactReference, ForecastDateTime, LogicalId
from tiaf.forecasting.identity import semantic_fingerprint as fingerprint

from .common import ClaimKind, Finite, IntelligenceContract, Probability, Text, unique
from .identity import ProducerIdentity


class AbsoluteMaturity(IntelligenceContract):
    kind: Literal["ABSOLUTE"] = "ABSOLUTE"
    at: ForecastDateTime


class TradingDayMaturity(IntelligenceContract):
    kind: Literal["TRADING_DAYS"] = "TRADING_DAYS"
    sessions: int = Field(strict=True, gt=0)
    calendar: ArtifactReference


class DurationMaturity(IntelligenceContract):
    kind: Literal["CALENDAR_DURATION"] = "CALENDAR_DURATION"
    seconds: int = Field(strict=True, gt=0)


class EventMaturity(IntelligenceContract):
    kind: Literal["EVENT"] = "EVENT"
    event_id: LogicalId
    policy: ArtifactReference
    deadline: ForecastDateTime | None = None


Maturity = Annotated[
    AbsoluteMaturity | TradingDayMaturity | DurationMaturity | EventMaturity,
    Field(discriminator="kind"),
]


class ResolutionContract(IntelligenceContract):
    resolution_id: LogicalId
    claim_kind: ClaimKind
    target: ArtifactReference
    target_semantics: Text
    resolver: ArtifactReference
    subject: LogicalId
    reference_at: ForecastDateTime
    reference_evidence: tuple[ArtifactReference, ...] = Field(min_length=1, max_length=64)
    maturity: Maturity
    mode: Literal["ENDPOINT", "WINDOW_EVENT", "MEASUREMENT", "EVENT"]

    @model_validator(mode="after")
    def check_maturity(self) -> Self:
        unique(self.reference_evidence, "REFERENCE_EVIDENCE")
        end = None
        if isinstance(self.maturity, AbsoluteMaturity):
            end = self.maturity.at
        elif isinstance(self.maturity, EventMaturity):
            end = self.maturity.deadline
        if end is not None and end <= self.reference_at:
            raise ValueError("MATURITY_MUST_FOLLOW_REFERENCE")
        return self


class BinaryValue(IntelligenceContract):
    kind: Literal[ClaimKind.BINARY] = ClaimKind.BINARY
    probability: Probability | None = None
    assertion: StrictBool | None = None
    calibration: Literal["RAW", "CALIBRATED", "NOT_APPLICABLE"] = "RAW"
    calibration_reference: ArtifactReference | None = None

    @model_validator(mode="after")
    def representation(self) -> Self:
        if (self.probability is None) == (self.assertion is None):
            raise ValueError("EXACTLY_ONE_BINARY_REPRESENTATION")
        if (self.calibration == "NOT_APPLICABLE") != (self.assertion is not None):
            raise ValueError("BINARY_CALIBRATION_REPRESENTATION_MISMATCH")
        if (self.calibration == "CALIBRATED") != (self.calibration_reference is not None):
            raise ValueError("CALIBRATION_REFERENCE_MISMATCH")
        return self


class NumericValue(IntelligenceContract):
    kind: Literal[ClaimKind.NUMERIC] = ClaimKind.NUMERIC
    value: Finite
    unit: Text


class CategoricalValue(IntelligenceContract):
    kind: Literal[ClaimKind.CATEGORICAL] = ClaimKind.CATEGORICAL
    value: Text
    vocabulary: tuple[Text, ...] = Field(min_length=2, max_length=64)

    @model_validator(mode="after")
    def membership(self) -> Self:
        unique(self.vocabulary, "CATEGORY")
        if self.value not in self.vocabulary:
            raise ValueError("CATEGORY_OUTSIDE_VOCABULARY")
        return self


class OrdinalValue(IntelligenceContract):
    kind: Literal[ClaimKind.ORDINAL] = ClaimKind.ORDINAL
    value: Text
    ordered_scale: tuple[Text, ...] = Field(min_length=2, max_length=64)

    @model_validator(mode="after")
    def membership(self) -> Self:
        unique(self.ordered_scale, "ORDINAL")
        if self.value not in self.ordered_scale:
            raise ValueError("ORDINAL_OUTSIDE_SCALE")
        return self


class RankingValue(IntelligenceContract):
    """Strict total ranking only; tied/partial rankings need a future schema."""

    kind: Literal[ClaimKind.RANKING] = ClaimKind.RANKING
    universe: tuple[LogicalId, ...] = Field(min_length=2, max_length=128)
    ordered_subjects: tuple[LogicalId, ...] = Field(min_length=2, max_length=128)

    @model_validator(mode="after")
    def permutation(self) -> Self:
        unique(self.universe, "UNIVERSE_MEMBER")
        unique(self.ordered_subjects, "RANKED_MEMBER")
        if set(self.universe) != set(self.ordered_subjects):
            raise ValueError("RANKING_UNIVERSE_MISMATCH")
        return self


class IntervalValue(IntelligenceContract):
    kind: Literal[ClaimKind.INTERVAL] = ClaimKind.INTERVAL
    lower: Finite
    upper: Finite
    unit: Text
    nominal_coverage: Annotated[Finite, Field(gt=0, lt=1)]
    interpretation: Literal["PREDICTIVE"] = "PREDICTIVE"

    @model_validator(mode="after")
    def bounds(self) -> Self:
        if self.lower > self.upper:
            raise ValueError("REVERSED_INTERVAL")
        return self


class EventTimeValue(IntelligenceContract):
    """Point estimate of event time, not an observed outcome or survival distribution."""

    kind: Literal[ClaimKind.EVENT_TIME] = ClaimKind.EVENT_TIME
    at: ForecastDateTime


ClaimValue = Annotated[
    BinaryValue
    | NumericValue
    | CategoricalValue
    | OrdinalValue
    | RankingValue
    | IntervalValue
    | EventTimeValue,
    Field(discriminator="kind"),
]


class EvaluableClaim(IntelligenceContract):
    claim_id: LogicalId
    request_id: LogicalId
    producer: ProducerIdentity
    information_cutoff: ForecastDateTime
    as_of: ForecastDateTime
    created_at: ForecastDateTime
    realization: ForecastRealizationMode
    value: ClaimValue
    resolution: ResolutionContract

    @model_validator(mode="after")
    def semantics(self) -> Self:
        if not self.information_cutoff <= self.as_of <= self.created_at:
            raise ValueError("CLAIM_CLOCK_ORDER")
        if self.resolution.reference_at > self.as_of:
            raise ValueError("REFERENCE_AFTER_AS_OF")
        maturity = self.resolution.maturity
        absolute_end = maturity.at if isinstance(maturity, AbsoluteMaturity) else None
        if absolute_end is not None:
            if absolute_end <= self.as_of:
                raise ValueError("ABSOLUTE_MATURITY_MUST_FOLLOW_AS_OF")
            if (
                self.realization is ForecastRealizationMode.ACTUAL_ISSUANCE
                and absolute_end <= self.created_at
            ):
                raise ValueError("ACTUAL_CLAIM_CANNOT_BE_ISSUED_AFTER_MATURITY")
        if self.value.kind != self.resolution.claim_kind:
            raise ValueError("CLAIM_RESOLUTION_KIND_MISMATCH")
        if self.value.kind not in self.producer.capability.claim_kinds:
            raise ValueError("CLAIM_KIND_NOT_DECLARED")
        if isinstance(self.value, EventTimeValue) and self.value.at <= self.resolution.reference_at:
            raise ValueError("EVENT_ESTIMATE_MUST_FOLLOW_REFERENCE")
        return self

    def semantic_fingerprint(self) -> str:
        admitted = EvaluableClaim.model_validate(self.model_dump())
        return fingerprint({"profile": "tiaf.ifl.claim/1.0", "claim": admitted})
