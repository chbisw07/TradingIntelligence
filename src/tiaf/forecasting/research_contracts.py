"""Additive FF-1 research contracts; no change to the synthetic FF-0 schema."""

from datetime import date, datetime
from typing import Annotated, Any, Literal, Self

from pydantic import (
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    SerializerFunctionWrapHandler,
    StrictFloat,
    model_serializer,
    model_validator,
)

from tiaf.contracts import ContractModel
from tiaf.features.enums import FeatureStatus
from tiaf.features.models import FeatureRequest, FeatureResult
from tiaf.forecasting.identity import semantic_fingerprint
from tiaf.planner.models import Sha256


def _source_date(value: object) -> object:
    if isinstance(value, datetime) or not isinstance(value, (date, str)):
        raise ValueError("ISO_SESSION_DATE_REQUIRED")
    return value


# Explicit new date-only serialization preserves FF-0's unchanged canonical hashing.
ResearchDate = Annotated[
    date,
    BeforeValidator(_source_date),
    PlainSerializer(lambda value: value.isoformat(), return_type=str),
]


class ResearchContract(ContractModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always", hide_input_in_errors=True
    )
    schema_version: Literal["2.0"] = "2.0"

    @model_serializer(mode="wrap")
    def serialize_dates(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        # Also cover dates in native nested contracts (e.g. a rejected derivative
        # identity). Preserve exact Decimal and datetime objects for FF canonical_json.
        def dates(value: Any) -> Any:
            if isinstance(value, datetime):
                return value
            if isinstance(value, date):
                return value.isoformat()
            if isinstance(value, dict):
                return {k: dates(v) for k, v in value.items()}
            if isinstance(value, (tuple, list)):
                return [dates(v) for v in value]
            return value

        return {key: dates(value) for key, value in handler(self).items()}


class FeatureSpec(ResearchContract):
    name: str
    request: FeatureRequest
    formula: str
    unit: str
    input_bars: int


_FEATURES = (
    FeatureSpec(
        name="ret_1",
        request=FeatureRequest(feature_id="return.log", parameters=(("bars", 1),), interval="1d"),
        formula="ln(C_t)-ln(C_t-1)",
        unit="log_ratio",
        input_bars=2,
    ),
    FeatureSpec(
        name="ret_5",
        request=FeatureRequest(feature_id="return.log", parameters=(("bars", 5),), interval="1d"),
        formula="ln(C_t)-ln(C_t-5)",
        unit="log_ratio",
        input_bars=6,
    ),
    FeatureSpec(
        name="sma20_distance",
        request=FeatureRequest(
            feature_id="trend.distance_from_sma_percent",
            parameters=(("period", 20),),
            interval="1d",
        ),
        formula="100*(C_t-mean(C_t-19..C_t))/mean(C_t-19..C_t)",
        unit="%",
        input_bars=20,
    ),
    FeatureSpec(
        name="realized_vol_20",
        request=FeatureRequest(
            feature_id="volatility.realized",
            parameters=(("annualization_factor", 252), ("bars", 20)),
            interval="1d",
        ),
        formula="100*sample_stdev(20_log_returns)*sqrt(252)",
        unit="%",
        input_bars=21,
    ),
    FeatureSpec(
        name="relative_volume",
        request=FeatureRequest(
            feature_id="volume.relative", parameters=(("bars", 20),), interval="1d"
        ),
        formula="V_t/mean(V_t-20..V_t-1)",
        unit="ratio",
        input_bars=21,
    ),
)


class FF1FeatureSchema(ResearchContract):
    schema_id: Literal["tiaf.ff1.feature-schema"] = "tiaf.ff1.feature-schema"
    feature_schema_id: Literal["ff1.reliance.a2_daily_five"] = "ff1.reliance.a2_daily_five"
    feature_schema_version: Literal["1.0"] = "1.0"
    features: tuple[FeatureSpec, ...] = _FEATURES
    missing_policy: Literal["NO_IMPUTATION"] = "NO_IMPUTATION"
    action_policy: Literal["EXCLUDE_AFFECTED_OR_UNKNOWN_UNADJUSTED"] = (
        "EXCLUDE_AFFECTED_OR_UNKNOWN_UNADJUSTED"
    )
    knowledge_policy: Literal["CAPTURED_AS_KNOWN"] = "CAPTURED_AS_KNOWN"
    preprocessing: Literal["NONE_FF1_1"] = "NONE_FF1_1"
    derivation_version: Literal["A2_PROJECTOR_1.0"] = "A2_PROJECTOR_1.0"

    @model_validator(mode="after")
    def fixed_schema(self) -> Self:
        if self.features != _FEATURES:
            raise ValueError("FF1_FEATURE_SCHEMA_MISMATCH")
        return self

    @property
    def fingerprint(self) -> str:
        return semantic_fingerprint(self)


class FeatureVector(ResearchContract):
    """Unscaled A2 values, not a probability or a data-use authorization."""

    feature_schema: FF1FeatureSchema
    input_fingerprint: Sha256
    values: tuple[Annotated[StrictFloat, Field(allow_inf_nan=False)], ...] = Field(
        min_length=5, max_length=5
    )
    results: tuple[FeatureResult, ...] = Field(min_length=5, max_length=5)

    @model_validator(mode="after")
    def exact_projection(self) -> Self:
        for spec, result, value in zip(
            self.feature_schema.features, self.results, self.values, strict=True
        ):
            if (
                result.request != spec.request
                or result.status is not FeatureStatus.AVAILABLE
                or result.value != value
                or result.unit != spec.unit
            ):
                raise ValueError("FF1_FEATURE_PROJECTION_MISMATCH")
        return self

    @property
    def fingerprint(self) -> str:
        return semantic_fingerprint(self)
