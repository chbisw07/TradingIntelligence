"""Synthetic factual bundles for isolated A2.9 policy tests."""

from datetime import datetime
from zoneinfo import ZoneInfo

from tiaf.baseline import (
    BaselineEvidenceSource,
    BaselinePolicy,
    DeterministicBaselineRequest,
    EvidenceFreshness,
    EvidenceRule,
)
from tiaf.contracts import DataQuality, FreshnessState, Horizon
from tiaf.features import (
    FeatureBundle,
    FeatureCategory,
    FeatureDefinition,
    FeatureRequest,
    FeatureResult,
    FeatureSourceKind,
    FeatureStatus,
    FeatureValueType,
    multi_timeframe_context,
    timeframe_feature_context,
)
from tiaf.indicators import IndicatorBundle, IndicatorResult, IndicatorValue

NOW = datetime(2026, 9, 7, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))


POSITIVE_VALUES = {
    "structure.hh": 0.82,
    "structure.hl": 0.78,
    "structure.lh": 0.18,
    "structure.ll": 0.20,
    "trend.efficiency": 0.62,
    "trend.slope": 1.40,
    "trend.ema_spread": 3.50,
    "momentum.return_5": 2.40,
    "momentum.return_20": 7.00,
    "relative.spread": 4.00,
    "relative.consistency": 0.72,
    "participation.balance": 0.48,
    "participation.relative_volume": 1.60,
    "readiness.position": 82.0,
    "readiness.compression": 0.65,
    "readiness.breakout": 0.20,
    "readiness.breakdown": 0.0,
    "volatility.atr": 2.50,
    "room.positive": -2.20,
    "room.negative": 3.50,
    "extension.ema": 0.55,
    "extension.range": 1.20,
    "mtf.positive": 0.75,
    "mtf.negative": 0.25,
    "mtf.agreement": 0.75,
    "mtf.disagreement": 0.25,
    "derivatives.ce_spread": 1.0,
    "derivatives.pe_spread": 1.2,
}


def values_for(profile: str) -> dict[str, float]:
    values = dict(POSITIVE_VALUES)
    if profile == "positive":
        return values
    if profile == "negative":
        swaps = (
            ("structure.hh", "structure.lh"),
            ("structure.hl", "structure.ll"),
            ("mtf.positive", "mtf.negative"),
        )
        for left, right in swaps:
            values[left], values[right] = values[right], values[left]
        for key in (
            "trend.efficiency",
            "trend.slope",
            "trend.ema_spread",
            "momentum.return_5",
            "momentum.return_20",
            "relative.spread",
            "participation.balance",
            "extension.ema",
        ):
            values[key] *= -1
        values["relative.consistency"] = 0.28
        values["readiness.position"] = 18.0
        values["readiness.breakout"], values["readiness.breakdown"] = 0.0, 0.2
        return values
    if profile == "neutral":
        for key in values:
            if key.startswith(("structure.", "trend.", "momentum.", "relative.", "mtf.")):
                values[key] = 0.5 if key.endswith("consistency") else 0.0
        values["participation.balance"] = 0.0
        values["readiness.position"] = 50.0
        return values
    if profile == "conflicted":
        values.update(
            {
                "structure.hh": 1.0,
                "structure.hl": 1.0,
                "structure.lh": 1.0,
                "structure.ll": 1.0,
                "trend.efficiency": 1.0,
                "trend.slope": 5.0,
                "trend.ema_spread": 10.0,
                "momentum.return_5": -20.0,
                "momentum.return_20": -30.0,
                "relative.spread": -20.0,
                "relative.consistency": 0.0,
                "participation.balance": 1.0,
                "readiness.position": 100.0,
                "readiness.breakdown": 2.0,
                "mtf.positive": 0.8,
                "mtf.negative": 0.8,
            }
        )
        return values
    raise ValueError(profile)


def _result(
    rule: EvidenceRule,
    value: float,
    quality: DataQuality,
    status: FeatureStatus,
) -> FeatureResult:
    definition = FeatureDefinition(
        feature_id=rule.selector.evidence_id,
        name=rule.selector.evidence_id,
        category=FeatureCategory.META,
        description="Synthetic factual A2.9 fixture.",
        value_type=FeatureValueType.FLOAT,
        unit="value",
        required_sources=(FeatureSourceKind.DERIVED,),
    )
    return FeatureResult(
        definition=definition,
        request=FeatureRequest(
            feature_id=rule.selector.evidence_id,
            parameters=rule.selector.parameters,
            interval="1d"
            if rule.selector.source
            in {
                BaselineEvidenceSource.PRIMARY,
                BaselineEvidenceSource.RELATIVE,
            }
            else None,
            required=False,
        ),
        status=status,
        value=value if status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL} else None,
        unit="value",
        as_of=NOW,
        source_context_id=f"ctx-{rule.selector.source.value.casefold()}",
        subject_symbol="RELIANCE",
        source_evidence=(rule.selector.source.value.casefold(),),
        source_observed_at=NOW,
        quality=quality,
        metadata=(
            {
                "contributing_intervals": ["1d"],
                "excluded_intervals": [],
                "denominator_semantics": "valid_contributing_timeframes",
            }
            if rule.selector.source is BaselineEvidenceSource.MULTI_TIMEFRAME
            else {}
        ),
    )


def _bundle(
    policy: BaselinePolicy,
    source: BaselineEvidenceSource,
    values: dict[str, float],
    *,
    quality: DataQuality,
    status: FeatureStatus,
    omit: frozenset[str],
) -> FeatureBundle | None:
    rules = tuple(rule for rule in policy.evidence_rules if rule.selector.source is source)
    if source is not BaselineEvidenceSource.PRIMARY and not rules:
        return None
    unique: dict[tuple[str, tuple[tuple[str, object], ...]], EvidenceRule] = {}
    for rule in rules:
        if rule.rule_id not in omit:
            unique.setdefault((rule.selector.evidence_id, rule.selector.parameters), rule)
    results = tuple(
        _result(rule, values[rule.rule_id], quality, status) for rule in unique.values()
    )
    return FeatureBundle(
        bundle_id=f"bundle-{source.value.casefold()}",
        context_id=f"ctx-{source.value.casefold()}",
        subject_symbol="RELIANCE",
        created_at=NOW,
        results=results,
        overall_quality=quality,
        complete=True,
    )


def baseline_request(
    policy: BaselinePolicy,
    *,
    profile: str = "positive",
    quality: DataQuality = DataQuality.GOOD,
    status: FeatureStatus = FeatureStatus.AVAILABLE,
    include_relative: bool = True,
    include_derivatives: bool = False,
    include_mtf: bool = False,
    include_indicators: bool = False,
    omit: frozenset[str] = frozenset(),
    primary_freshness: FreshnessState = FreshnessState.FRESH,
    values: dict[str, float] | None = None,
    subject: str = "RELIANCE",
) -> DeterministicBaselineRequest:
    selected_values = values or values_for(profile)
    primary = _bundle(
        policy,
        BaselineEvidenceSource.PRIMARY,
        selected_values,
        quality=quality,
        status=status,
        omit=omit,
    )
    assert primary is not None
    indicators = None
    if include_indicators:
        indicator_results = tuple(
            IndicatorResult(
                result_id=f"indicator-{indicator_id}",
                indicator_id=indicator_id,
                definition_version="1.0",
                parameters=(("period", 14),),
                interval="1d",
                required=False,
                status=FeatureStatus.AVAILABLE,
                quality=quality,
                as_of=NOW,
                values=(IndicatorValue(name=output, value=value, unit="index_0_100"),),
                source_context_id=primary.context_id,
                subject_symbol=subject,
                source_evidence=("history",),
            )
            for indicator_id, output, value in (
                ("rsi", "rsi", 65.0),
                ("adx", "adx", 28.0),
            )
        )
        indicators = IndicatorBundle(
            bundle_id="bundle-indicators",
            registry_version="1.0",
            context_id=primary.context_id,
            subject_symbol=subject,
            created_at=NOW,
            results=indicator_results,
            overall_quality=quality,
            complete=True,
        )
    if subject != "RELIANCE":
        primary = primary.model_copy(
            update={
                "subject_symbol": subject,
                "results": tuple(
                    item.model_copy(update={"subject_symbol": subject}) for item in primary.results
                ),
            }
        )
        primary = FeatureBundle.model_validate(primary.model_dump())
    relative = (
        _bundle(
            policy,
            BaselineEvidenceSource.RELATIVE,
            selected_values,
            quality=quality,
            status=status,
            omit=omit,
        )
        if include_relative
        else None
    )
    derivatives = (
        _bundle(
            policy,
            BaselineEvidenceSource.DERIVATIVES,
            selected_values,
            quality=quality,
            status=status,
            omit=omit,
        )
        if include_derivatives
        else None
    )
    mtf_context = None
    mtf = None
    if include_mtf:
        timeframe = timeframe_feature_context("1d", primary)
        mtf_context = multi_timeframe_context(
            subject,
            (timeframe,),
            created_at=NOW,
        )
        raw_mtf = _bundle(
            policy,
            BaselineEvidenceSource.MULTI_TIMEFRAME,
            selected_values,
            quality=quality,
            status=status,
            omit=omit,
        )
        assert raw_mtf is not None
        mtf = FeatureBundle.model_validate(
            raw_mtf.model_copy(
                update={
                    "context_id": mtf_context.context_id,
                    "subject_symbol": subject,
                    "results": tuple(
                        item.model_copy(
                            update={
                                "source_context_id": mtf_context.context_id,
                                "subject_symbol": subject,
                            }
                        )
                        for item in raw_mtf.results
                    ),
                }
            ).model_dump()
        )
    if subject != "RELIANCE":
        if relative is not None:
            relative = FeatureBundle.model_validate(
                relative.model_copy(
                    update={
                        "subject_symbol": subject,
                        "results": tuple(
                            item.model_copy(update={"subject_symbol": subject})
                            for item in relative.results
                        ),
                    }
                ).model_dump()
            )
        if derivatives is not None:
            derivatives = FeatureBundle.model_validate(
                derivatives.model_copy(
                    update={
                        "subject_symbol": subject,
                        "results": tuple(
                            item.model_copy(update={"subject_symbol": subject})
                            for item in derivatives.results
                        ),
                    }
                ).model_dump()
            )
    freshness = [EvidenceFreshness(source=BaselineEvidenceSource.PRIMARY, state=primary_freshness)]
    if relative is not None:
        freshness.append(
            EvidenceFreshness(
                source=BaselineEvidenceSource.RELATIVE,
                state=FreshnessState.FRESH,
            )
        )
    if indicators is not None:
        freshness.append(
            EvidenceFreshness(
                source=BaselineEvidenceSource.INDICATOR,
                state=FreshnessState.FRESH,
            )
        )
    if derivatives is not None:
        freshness.append(
            EvidenceFreshness(
                source=BaselineEvidenceSource.DERIVATIVES,
                state=FreshnessState.FRESH,
            )
        )
    if mtf is not None:
        freshness.append(
            EvidenceFreshness(
                source=BaselineEvidenceSource.MULTI_TIMEFRAME,
                state=FreshnessState.FRESH,
            )
        )
    return DeterministicBaselineRequest(
        request_id=f"request-{subject}",
        subject=subject,
        trade_style=policy.trade_style,
        horizon=Horizon(label=policy.trade_style.value.casefold()),
        primary_timeframe="1d",
        primary_features=primary,
        indicators=indicators,
        relative_features=relative,
        derivatives_features=derivatives,
        multi_timeframe_context=mtf_context,
        multi_timeframe_features=mtf,
        evidence_freshness=tuple(freshness),
        policy_version=policy.policy_version,
        requested_at=NOW,
    )
