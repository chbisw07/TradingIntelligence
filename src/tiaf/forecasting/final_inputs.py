"""Forecasting-owned final-year causal capture/inference; never fit or select a model.

The sealed development reader remains unchanged. This additive reader requires a
durable final-attempt claim. It normalizes only the frozen causal bar union and
target closes (the terminal 2026 row is close-only). Source bytes are hash checked.
"""

import csv
import io
from datetime import date, datetime, timedelta
from hashlib import sha256
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from tiaf.data.models import OHLCVBar
from tiaf.evaluation.forecast_final_custody import FinalAttempt
from tiaf.evaluation.forecast_final_protocol import FinalProtocol, FinalSlot
from tiaf.evaluation.forecast_retrospective import _perturb, _project
from tiaf.evaluation.forecast_retrospective_contracts import RetrospectiveDataset
from tiaf.forecasting.identity import ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.research_contracts import (
    AdjustedFF1FeatureSchema,
    AdjustedResearchProfile,
    FeatureVector,
    ResearchDate,
)
from tiaf.learning.forecast_artifacts import (
    Finite,
    Five,
    LogisticArtifact,
    SealedResearch,
    reconstruct,
)
from tiaf.learning.forecast_fifth_preparation import FifthBaseRateState
from tiaf.planner.models import Sha256


class FinalSourceRow(SealedResearch):
    session_date: ResearchDate
    bar: OHLCVBar | None
    close: Finite

    @model_validator(mode="after")
    def consistent(self) -> Self:
        if self.close <= 0 or (
            self.bar is not None
            and (self.bar.close != self.close or self.bar.end_at.date() != self.session_date)
        ):
            raise ValueError("FINAL_SOURCE_ROW_IDENTITY")
        return self


class FinalSource(SealedResearch):
    protocol_fingerprint: Sha256
    attempt_fingerprint: Sha256
    execution_fingerprint: Sha256
    source_context_fingerprint: Sha256
    # Thin metadata projection, not a re-qualified or newly admitted dataset.
    context: RetrospectiveDataset
    rows: tuple[FinalSourceRow, ...] = Field(max_length=8192)
    captured_at: ForecastDateTime


def windows(protocol: FinalProtocol, context: RetrospectiveDataset) -> tuple[tuple[date, ...], ...]:
    sessions = context.calendar.sessions()
    indices = {s[0]: i for i, s in enumerate(sessions)}
    result = []
    for slot in protocol.population.slots:
        if slot.reference_date not in indices:
            raise ValueError("FINAL_REFERENCE_NOT_IN_CALENDAR")
        i = indices[slot.reference_date]
        target = sessions[i + 1][0] if i + 1 < len(sessions) else None
        if slot.target_date != target:
            raise ValueError("FINAL_TARGET_NOT_NEXT_SESSION")
        result.append(tuple(s[0] for s in sessions[max(0, i - 20) : i + 1]))
    return tuple(result)


def capture_source(
    raw: bytes,
    protocol: FinalProtocol,
    claim: FinalAttempt,
    execution: str,
    context: RetrospectiveDataset,
    captured_at: datetime,
) -> FinalSource:
    """Bootstrap invokes only after consume_once and durable opening record.

    Date/string tokenization is not numeric access. All out-of-scope numeric
    fields, including unused terminal OHLCV fields, remain uninterpreted.
    """
    if (
        claim.protocol_fingerprint != protocol.fingerprint
        or sha256(raw).hexdigest() != protocol.dataset_fingerprint
        or context.dataset_sha256 != protocol.dataset_fingerprint
        or context.acquired_at > captured_at
    ):
        raise ValueError("FINAL_SOURCE_OR_AUTHORITY_PIN")
    wanted_bars = {d for window in windows(protocol, context) for d in window}
    wanted_closes = {s.target_date for s in protocol.population.slots if s.target_date is not None}
    sessions = {d: (opens, closes) for d, opens, closes in context.calendar.sessions()}
    rows = []
    dates = []
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8"))):
        day = date.fromisoformat(row["date"])
        dates.append(day)
        if day not in wanted_bars | wanted_closes:
            continue
        close = float(row["close"])
        bar = None
        if day in wanted_bars:
            opens, closes = sessions[day]
            bar = OHLCVBar(
                instrument=context.resolved.instrument,
                interval="1d",
                start_at=opens,
                end_at=closes,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=close,
                volume=int(row["volume"]),
                source_provider=context.resolved.provider_name,
            )
            if min(bar.open, bar.high, bar.low, bar.close) <= 0:
                raise ValueError("FINAL_SOURCE_PRICE_IDENTITY")
        rows.append(FinalSourceRow(session_date=day, bar=bar, close=close))
    if dates != sorted(set(dates)) or len(dates) > 8192:
        raise ValueError("FINAL_SOURCE_ORDER_OR_BOUND")
    source = FinalSource(
        protocol_fingerprint=protocol.fingerprint,
        attempt_fingerprint=cast(str, claim.fingerprint),
        execution_fingerprint=execution,
        source_context_fingerprint=protocol.population.context_fingerprint,
        context=context,
        rows=tuple(rows),
        captured_at=captured_at,
    )
    validate_source(protocol, source)
    return source


def validate_source(protocol: FinalProtocol, source: FinalSource) -> None:
    wanted_bars = {d for window in windows(protocol, source.context) for d in window}
    wanted_closes = {s.target_date for s in protocol.population.slots if s.target_date is not None}
    dates = tuple(r.session_date for r in source.rows)
    sessions = {d: (a, b) for d, a, b in source.context.calendar.sessions()}
    if (
        source.protocol_fingerprint != protocol.fingerprint
        or source.source_context_fingerprint != protocol.population.context_fingerprint
        or source.context.dataset_sha256 != protocol.dataset_fingerprint
        or dates != tuple(sorted(set(dates)))
        or set(dates) - (wanted_bars | wanted_closes)
        or source.captured_at < source.context.acquired_at
    ):
        raise ValueError("FINAL_SOURCE_SCOPE_OR_LINEAGE")
    for row in source.rows:
        b = row.bar
        if (b is not None) != (row.session_date in wanted_bars) or (
            b is not None
            and (
                b.instrument != source.context.resolved.instrument
                or b.source_provider != source.context.resolved.provider_name
                or b.interval != "1d"
                or (b.start_at, b.end_at) != sessions[row.session_date]
                or min(b.open, b.high, b.low, b.close) <= 0
            )
        ):
            raise ValueError("FINAL_BAR_IDENTITY_OR_SCOPE")


class FinalInput(SealedResearch):
    """Forecast boundary: no target values, labels or aggregate class information."""

    protocol_fingerprint: Sha256
    execution_fingerprint: Sha256
    source_context_fingerprint: Sha256
    slot: FinalSlot
    reference_closes_at: ForecastDateTime
    information_cutoff: ForecastDateTime
    simulation_as_of: ForecastDateTime
    target_opens_at: ForecastDateTime | None
    target_closes_at: ForecastDateTime | None
    window_dates: tuple[ResearchDate, ...] = Field(min_length=1, max_length=21)
    bars: tuple[OHLCVBar | None, ...] = Field(min_length=1, max_length=21)
    input_fingerprint: Sha256
    captured_at: ForecastDateTime

    @model_validator(mode="after")
    def causal(self) -> Self:
        if (
            len(self.bars) != len(self.window_dates)
            or self.window_dates != tuple(sorted(set(self.window_dates)))
            or self.window_dates[-1] != self.slot.reference_date
            or self.reference_closes_at.date() != self.slot.reference_date
            or self.information_cutoff != self.reference_closes_at + timedelta(minutes=30)
            or self.simulation_as_of != self.information_cutoff + timedelta(minutes=5)
            or (self.slot.target_date is None)
            != (self.target_opens_at is None and self.target_closes_at is None)
            or (
                self.target_opens_at is not None
                and (
                    self.target_closes_at is None
                    or self.target_opens_at.date() != self.slot.target_date
                    or self.target_closes_at.date() != self.slot.target_date
                    or not self.simulation_as_of < self.target_opens_at < self.target_closes_at
                )
            )
            or any(
                b is not None and b.end_at.date() != d
                for d, b in zip(self.window_dates, self.bars, strict=True)
            )
            or self.input_fingerprint
            != semantic_fingerprint(
                (
                    self.source_context_fingerprint,
                    self.slot.reference_date.isoformat(),
                    tuple(
                        (d.isoformat(), b)
                        for d, b in zip(self.window_dates, self.bars, strict=True)
                    ),
                )
            )
        ):
            raise ValueError("FINAL_INPUT_CAUSAL_IDENTITY")
        return self


def final_inputs(protocol: FinalProtocol, source: FinalSource) -> tuple[FinalInput, ...]:
    validate_source(protocol, source)
    rows = {r.session_date: r.bar for r in source.rows}
    sessions = {d: (opens, closes) for d, opens, closes in source.context.calendar.sessions()}
    result = []
    for slot, window in zip(
        protocol.population.slots, windows(protocol, source.context), strict=True
    ):
        bars = tuple(rows.get(d) for d in window)
        close = sessions[slot.reference_date][1]
        target = None if slot.target_date is None else sessions[slot.target_date]
        result.append(
            FinalInput(
                protocol_fingerprint=cast(str, protocol.fingerprint),
                execution_fingerprint=source.execution_fingerprint,
                source_context_fingerprint=source.source_context_fingerprint,
                slot=slot,
                reference_closes_at=close,
                information_cutoff=close + timedelta(minutes=30),
                simulation_as_of=close + timedelta(minutes=35),
                target_opens_at=None if target is None else target[0],
                target_closes_at=None if target is None else target[1],
                window_dates=window,
                bars=bars,
                input_fingerprint=semantic_fingerprint(
                    (
                        source.source_context_fingerprint,
                        slot.reference_date.isoformat(),
                        tuple((d.isoformat(), b) for d, b in zip(window, bars, strict=True)),
                    )
                ),
                captured_at=source.captured_at,
            )
        )
    return tuple(result)


class FinalForecast(SealedResearch):
    common_request_fingerprint: Sha256
    protocol_fingerprint: Sha256
    execution_fingerprint: Sha256
    arm: Literal["LOGISTIC", "BASERATE"]
    artifact_fingerprint: Sha256
    scaler_fingerprint: Sha256 | None
    features: FeatureVector | None
    precision_feature_drift: Finite | None
    probability: Finite | None
    reasons: tuple[str, ...]
    computed_at: ForecastDateTime

    @model_validator(mode="after")
    def valid(self) -> Self:
        if (
            (self.probability is None) != bool(self.reasons)
            or (self.probability is not None and not 0 <= self.probability <= 1)
            or (self.arm == "BASERATE" and (self.scaler_fingerprint or self.features))
        ):
            raise ValueError("FINAL_FORECAST_STATE")
        return self


def final_features(
    request: FinalInput, context: RetrospectiveDataset, at: datetime
) -> tuple[FeatureVector | None, float | None, tuple[str, ...]]:
    """Exact FF1.1A feature admission; same A2 implementation and perturbation test."""
    reasons = []
    if len(request.window_dates) != 21:
        reasons.append("INSUFFICIENT_LOOKBACK")
    if any(b is None for b in request.bars):
        reasons.append("MISSING_FEATURE_BAR")
    for action in context.actions:
        if not action.provider_adjustment_supported and (
            request.window_dates[0] < action.boundary <= request.slot.reference_date
        ):
            reasons.append("FEATURE_ACTION_" + action.kind)
    bars = tuple(b for b in request.bars if b is not None)
    if not reasons:
        if any(b.volume is None or b.volume > 2**53 for b in bars):
            reasons.append("VOLUME_NUMERIC_UNQUALIFIED")
        elif sum(b.volume or 0 for b in bars[:-1]) == 0:
            reasons.append("ZERO_VOLUME_BASELINE")
    features, drift = None, None
    if not reasons:
        schema = AdjustedFF1FeatureSchema(profile=AdjustedResearchProfile())
        try:
            features = _project(context, bars, schema, request.input_fingerprint, at)
            drift = max(
                abs(a - b)
                for sign in (-1, 1)
                for a, b in zip(
                    features.values,
                    _project(
                        context,
                        _perturb(bars, sign, schema.profile.near_tie_ulps),
                        schema,
                        request.input_fingerprint,
                        at,
                    ).values,
                    strict=True,
                )
            )
            if drift > schema.profile.feature_absolute_tolerance:
                features = None
                reasons.append("PRECISION_FEATURE_DRIFT")
        except ValueError:
            features = None
            reasons.append("FEATURE_UNAVAILABLE")
    return features, drift, tuple(reasons)


def infer_final(
    request: FinalInput,
    context: RetrospectiveDataset,
    model: LogisticArtifact,
    baseline: FifthBaseRateState,
    at: datetime,
) -> tuple[FinalForecast, FinalForecast]:
    """Outcome-blind function: only the causal request and frozen artifacts enter."""
    if at < request.captured_at or at < model.created_at or baseline.output is None:
        raise ValueError("FINAL_INFERENCE_CLOCK_OR_BASELINE")
    features, drift, reasons = final_features(request, context, at)
    common = {
        "common_request_fingerprint": request.fingerprint,
        "protocol_fingerprint": request.protocol_fingerprint,
        "execution_fingerprint": request.execution_fingerprint,
        "computed_at": at,
    }
    logistic = FinalForecast.model_validate(
        {
            **common,
            "arm": "LOGISTIC",
            "artifact_fingerprint": model.fingerprint,
            "scaler_fingerprint": model.reconstruction.scaler.fingerprint,
            "features": features,
            "precision_feature_drift": drift,
            "probability": None
            if features is None
            else reconstruct(model.reconstruction, cast(Five, features.values)),
            "reasons": reasons,
        }
    )
    benchmark = FinalForecast.model_validate(
        {
            **common,
            "arm": "BASERATE",
            "artifact_fingerprint": baseline.fingerprint,
            "scaler_fingerprint": None,
            "features": None,
            "precision_feature_drift": None,
            "probability": baseline.output.probability,
            "reasons": (),
        }
    )
    return logistic, benchmark
