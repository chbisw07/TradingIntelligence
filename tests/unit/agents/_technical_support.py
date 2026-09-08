"""Synthetic A3.3 evidence assembled from supplied scalar A2 facts."""

from datetime import datetime
from zoneinfo import ZoneInfo

from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentEvidencePack,
    AgentEvidenceReference,
    AgentRequest,
    AnalysisMode,
    EvidenceFact,
    EvidenceFactKind,
    SpecialistId,
)
from tiaf.context import AnalysisPurpose, EvidenceStatus
from tiaf.contracts import (
    DataQuality,
    EvidenceSource,
    EvidenceType,
    FreshnessState,
    Horizon,
    TradeStyle,
)
from tiaf.data import InstrumentType

NOW = datetime(2026, 9, 8, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
FINGERPRINT = "3" * 64
BASELINE_ID = "a2-assessment-technical"


def fact(
    metric_id: str,
    value: str | int | float | bool,
    *,
    interval: str = "1d",
    suffix: str | None = None,
    output_name: str | None = None,
    quality: DataQuality = DataQuality.GOOD,
    freshness: FreshnessState = FreshnessState.FRESH,
) -> EvidenceFact:
    kind = EvidenceFactKind.INDICATOR if output_name else EvidenceFactKind.FEATURE
    if metric_id.startswith("baseline."):
        kind = EvidenceFactKind.BASELINE
    return EvidenceFact(
        fact_id=f"fact:{metric_id}:{suffix or output_name or interval}",
        kind=kind,
        metric_id=metric_id,
        value=value,
        output_name=output_name,
        interval=interval,
        as_of=NOW,
        quality=quality,
        freshness=freshness,
        source_evidence=(f"a2:{metric_id}",),
    )


def reference(
    evidence_id: str,
    evidence_type: EvidenceType,
    facts: tuple[EvidenceFact, ...],
    *,
    quality: DataQuality = DataQuality.GOOD,
    freshness: FreshnessState = FreshnessState.FRESH,
) -> AgentEvidenceReference:
    availability = (
        EvidenceStatus.STALE
        if freshness is FreshnessState.STALE
        else EvidenceStatus.PARTIAL
        if quality is not DataQuality.GOOD
        else EvidenceStatus.AVAILABLE
    )
    return AgentEvidenceReference(
        evidence_id=evidence_id,
        evidence_type=evidence_type,
        subject="RELIANCE",
        producer_id="tiaf.a2",
        producer_version="1.0",
        source=EvidenceSource.DERIVED,
        availability=availability,
        quality=quality,
        freshness=freshness,
        observed_at=NOW,
        acquired_at=NOW,
        checksum=f"checksum:{evidence_id}",
        source_reference=f"a2://{evidence_id}",
        facts=facts,
    )


def technical_request(
    *,
    trade_style: TradeStyle = TradeStyle.POSITIONAL,
    budget: AgentBudget | None = None,
) -> AgentRequest:
    return AgentRequest(
        request_id="request-technical",
        run_id="run-technical",
        subject="RELIANCE",
        instrument_type=InstrumentType.EQUITY,
        horizon=Horizon(label=trade_style.value.casefold(), min_days=1, max_days=20),
        specialist=SpecialistId.TECHNICAL,
        purpose=AnalysisPurpose.OPPORTUNITY,
        trade_style=trade_style,
        analysis_mode=AnalysisMode.DETERMINISTIC_ONLY,
        task="Interpret only the supplied A2 technical evidence.",
        a2_context_ids=("context-1",),
        a2_evidence_ids=("technical-core",),
        deterministic_baseline_reference=BASELINE_ID,
        evidence_fingerprint=FINGERPRINT,
        allowed_capabilities=(AgentCapability.READ_A2_EVIDENCE,),
        budget=budget or AgentBudget(),
        created_at=NOW,
    )


def technical_pack(
    *,
    overrides: dict[str, str | int | float | bool] | None = None,
    omit: tuple[str, ...] = (),
    core_only: bool = False,
    optional_quality: DataQuality = DataQuality.GOOD,
    optional_freshness: FreshnessState = FreshnessState.FRESH,
) -> AgentEvidencePack:
    values: dict[str, str | int | float | bool] = {
        "trend.distance_from_ema_percent": 2.0,
        "trend.linear_slope_percent": 0.2,
        "trend.signed_efficiency": 0.5,
        "trend.linear_r2": 0.8,
        "trend.distance_from_ema_atr": 1.0,
        "structure.higher_high_fraction": 0.7,
        "structure.higher_low_fraction": 0.7,
        "structure.lower_high_fraction": 0.2,
        "structure.lower_low_fraction": 0.2,
        "structure.position_in_rolling_range": 80.0,
        "structure.range_compression_ratio": 1.0,
        "structure.latest_bar_range_vs_average": 1.0,
        "breakout.above_prior_high_percent": 0.0,
        "breakout.high_above_prior_high_percent": 0.0,
        "breakdown.below_prior_low_percent": 0.0,
        "breakdown.low_below_prior_low_percent": 0.0,
        "support.prior_low": 95.0,
        "resistance.prior_high": 110.0,
        "resistance.distance_atr": -2.0,
        "support.distance_atr": 3.0,
        "indicator.rsi": 62.0,
        "indicator.macd": 0.5,
        "return.percent": 3.0,
        "range.move_over_atr": 1.0,
        "participation.signed_volume_balance": 0.3,
        "volume.relative": 1.2,
        "volatility.atr_percent": 2.0,
        "volatility.realized": 18.0,
        "mtf.positive_return_fraction": 0.8,
        "mtf.negative_return_fraction": 0.2,
        "mtf.price_above_ema_fraction": 0.8,
        "mtf.price_below_ema_fraction": 0.2,
        "mtf.positive_slope_fraction": 0.8,
        "mtf.negative_slope_fraction": 0.2,
        "mtf.disagreement_fraction": 0.2,
        "baseline.direction": "POSITIVE",
        "baseline.opportunity_score": 72.0,
        "baseline.candidate_class": "EARLY_OPPORTUNITY",
    }
    values.update(overrides or {})
    for key in omit:
        values.pop(key, None)

    groups = {
        "technical-core": (
            EvidenceType.TECHNICAL,
            tuple(
                fact(name, value)
                for name, value in values.items()
                if name.startswith(
                    (
                        "trend.",
                        "structure.",
                        "breakout.",
                        "breakdown.",
                        "support.",
                        "resistance.",
                    )
                )
            ),
        ),
        "technical-momentum": (
            EvidenceType.TECHNICAL,
            tuple(
                fact(
                    name,
                    value,
                    output_name=("rsi" if name == "indicator.rsi" else "histogram")
                    if name.startswith("indicator.")
                    else None,
                )
                for name, value in values.items()
                if name.startswith("indicator.")
                or name in {"return.percent", "range.move_over_atr"}
            ),
        ),
        "technical-participation": (
            EvidenceType.VOLUME,
            tuple(
                fact(name, value)
                for name, value in values.items()
                if name.startswith(("participation.", "volume."))
            ),
        ),
        "technical-volatility": (
            EvidenceType.VOLATILITY,
            tuple(
                fact(name, value)
                for name, value in values.items()
                if name.startswith("volatility.")
            ),
        ),
        "technical-mtf": (
            EvidenceType.TECHNICAL,
            tuple(
                fact(name, value)
                for name, value in values.items()
                if name.startswith("mtf.")
            ),
        ),
        "a2-baseline": (
            EvidenceType.OTHER,
            tuple(
                fact(name, value)
                for name, value in values.items()
                if name.startswith("baseline.")
            ),
        ),
    }
    selected_groups = ("technical-core",) if core_only else tuple(groups)
    references = tuple(
        reference(
            evidence_id,
            groups[evidence_id][0],
            groups[evidence_id][1],
            quality=(
                DataQuality.GOOD
                if evidence_id == "technical-core"
                else optional_quality
            ),
            freshness=(
                FreshnessState.FRESH
                if evidence_id == "technical-core"
                else optional_freshness
            ),
        )
        for evidence_id in selected_groups
        if groups[evidence_id][1]
    )
    return AgentEvidencePack(
        pack_id="pack-technical",
        request_id="request-technical",
        subject="RELIANCE",
        evidence_fingerprint=FINGERPRINT,
        references=references,
        analysis_context_ids=("context-1",),
        feature_bundle_ids=("features-1",),
        indicator_bundle_ids=("indicators-1",) if not core_only else (),
        multi_timeframe_context_ids=("mtf-1",) if not core_only else (),
        deterministic_assessment_id=BASELINE_ID,
        overall_quality=(DataQuality.GOOD if core_only else optional_quality),
        overall_freshness=(FreshnessState.FRESH if core_only else optional_freshness),
        evidence_coverage=0.45 if core_only else 1.0,
        created_at=NOW,
    )
