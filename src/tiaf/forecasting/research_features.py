"""Five fixed A2 calculations over an already qualified, time-local context."""

from datetime import datetime

from pydantic import TypeAdapter

from tiaf.context import AnalysisContext
from tiaf.features.engine import DeterministicFeatureEngine, builtin_feature_registry
from tiaf.features.enums import FeatureStatus
from tiaf.forecasting.identity import ForecastDateTime
from tiaf.forecasting.research_contracts import (
    AdjustedFF1FeatureSchema,
    FeatureVector,
    FF1FeatureSchema,
)


def derive_features(
    context: AnalysisContext,
    *,
    reference_close_at: datetime,
    information_cutoff: datetime,
    input_fingerprint: str,
    schema: FF1FeatureSchema | AdjustedFF1FeatureSchema | None = None,
) -> FeatureVector:
    """No formula duplication, scaling, acquisition, labels or learned model.

    This projection is not a source/rights qualification API. The Evaluation
    qualifier checks the complete per-row provenance before invoking it.
    """
    context = AnalysisContext.model_validate(context.model_dump(mode="python"))
    reference_close_at = TypeAdapter(ForecastDateTime).validate_python(reference_close_at)
    information_cutoff = TypeAdapter(ForecastDateTime).validate_python(information_cutoff)
    history = context.history
    if (
        history is None
        or len(history.bars) != 21
        or history.interval != "1d"
        or history.bars[-1].end_at != reference_close_at
        or any(bar.end_at > reference_close_at for bar in history.bars)
        or reference_close_at > information_cutoff
        or information_cutoff > context.created_at
    ):
        raise ValueError("FF1_FEATURE_WINDOW_OR_CUTOFF_INVALID")
    schema = (
        FF1FeatureSchema() if schema is None else type(schema).model_validate(schema.model_dump())
    )
    engine = DeterministicFeatureEngine(builtin_feature_registry())
    bundle = engine.compute(context, tuple(item.request for item in schema.features))
    values: list[float] = []
    for result in bundle.results:
        if (
            result.status is not FeatureStatus.AVAILABLE
            or not isinstance(result.value, (float, int))
            or isinstance(result.value, bool)
        ):
            raise ValueError("FF1_FEATURE_UNAVAILABLE")
        values.append(float(result.value))
    return FeatureVector(
        feature_schema=schema,
        input_fingerprint=input_fingerprint,
        values=tuple(values),
        results=bundle.results,
    )
