"""Acquire read-only A2 evidence and inspect the deterministic A3.3 specialist."""

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

from baseline_opportunity_smoke import _build_request
from pydantic import ValidationError

from tiaf import __version__
from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentEvidencePack,
    AgentEvidenceReference,
    AgentRegistry,
    AgentRequest,
    AgentRuntime,
    AnalysisMode,
    EvidenceFact,
    SpecialistId,
)
from tiaf.agents.specialists.technical import (
    TechnicalSpecialist,
    baseline_facts,
    feature_fact,
    indicator_facts,
    multi_timeframe_constituent_facts,
    technical_assessment_from_opinion,
)
from tiaf.baseline import (
    BaselineEngine,
    BaselineEvidenceSource,
    DeterministicBaselineRequest,
    EvidenceFreshness,
    OpportunityAssessment,
    default_policy,
)
from tiaf.context import AnalysisContextBuilder, AnalysisPurpose, EvidenceStatus
from tiaf.contracts import (
    DataQuality,
    EvidenceSource,
    EvidenceType,
    FreshnessState,
    TradeStyle,
)
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import InstrumentType, TIAFDataError, normalize_interval, normalize_symbol
from tiaf.data.providers.dhan import (
    DhanInstrumentResolver,
    DhanMarketDataProvider,
    dhan_rate_policy_registry,
)
from tiaf.data.runtime import DataFetchCoordinator, ProviderScheduler
from tiaf.evaluation import CorpusError, create_evidence_snapshot, load_case
from tiaf.features import FeatureResult, FeatureStatus

_QUALITY_ORDER = {
    DataQuality.GOOD: 0,
    DataQuality.PARTIAL: 1,
    DataQuality.DEGRADED: 2,
    DataQuality.UNAVAILABLE: 3,
}
_FRESHNESS_ORDER = {
    FreshnessState.FRESH: 0,
    FreshnessState.AGING: 1,
    FreshnessState.STALE: 2,
    FreshnessState.UNKNOWN: 3,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--symbol")
    source.add_argument(
        "--input",
        type=Path,
        help="captured A2.10 snapshot/run file; performs no provider access",
    )
    parser.add_argument(
        "--horizon",
        choices=tuple(item.value for item in TradeStyle),
        default=TradeStyle.POSITIONAL.value,
    )
    parser.add_argument("--benchmark")
    parser.add_argument("--timeframes", default="1d,1h,15m")
    parser.add_argument("--lookback-days", type=int, default=180)
    parser.add_argument("--mode", choices=("deterministic",), default="deterministic")
    args = parser.parse_args()
    args.symbol = normalize_symbol(args.symbol or "RELIANCE")
    args.benchmark = normalize_symbol(args.benchmark) if args.benchmark else None
    args.horizon = TradeStyle(args.horizon)
    args.timeframes = tuple(
        dict.fromkeys(
            normalize_interval(item)
            for item in args.timeframes.split(",")
            if item.strip()
        )
    )
    if not args.timeframes or args.lookback_days <= 0:
        parser.error("timeframes must be non-empty and lookback-days must be positive")
    return args


def _source_freshness(
    request_freshness: tuple[EvidenceFreshness, ...],
    source: BaselineEvidenceSource,
) -> FreshnessState:
    return next(
        (
            item.state
            for item in request_freshness
            if getattr(item, "source", None) is source
        ),
        FreshnessState.UNKNOWN,
    )


def _feature_facts(
    results: tuple[FeatureResult, ...],
    freshness: FreshnessState,
) -> tuple[EvidenceFact, ...]:
    return tuple(
        feature_fact(item, freshness=freshness)
        for item in results
        if item.status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
        and item.value is not None
        and not isinstance(item.value, tuple)
    )


def _reference(
    evidence_id: str,
    evidence_type: EvidenceType,
    subject: str,
    facts: tuple[EvidenceFact, ...],
    acquired_at: datetime,
) -> AgentEvidenceReference:
    quality = max((item.quality for item in facts), key=_QUALITY_ORDER.__getitem__)
    freshness = max(
        (item.freshness for item in facts), key=_FRESHNESS_ORDER.__getitem__
    )
    availability = (
        EvidenceStatus.STALE
        if freshness is FreshnessState.STALE
        else EvidenceStatus.PARTIAL
        if quality is not DataQuality.GOOD
        else EvidenceStatus.AVAILABLE
    )
    canonical = json.dumps(
        [item.model_dump(mode="json") for item in facts],
        sort_keys=True,
        separators=(",", ":"),
    )
    return AgentEvidenceReference(
        evidence_id=evidence_id,
        evidence_type=evidence_type,
        subject=subject,
        producer_id="tiaf.a2",
        producer_version=__version__,
        source=EvidenceSource.DERIVED,
        availability=availability,
        quality=quality,
        freshness=freshness,
        observed_at=max(item.as_of for item in facts),
        acquired_at=acquired_at,
        checksum=hashlib.sha256(canonical.encode()).hexdigest(),
        facts=facts,
    )


def _technical_evidence_pack(
    baseline_request: DeterministicBaselineRequest,
    assessment: OpportunityAssessment,
    fingerprint: str,
    created_at: datetime,
) -> AgentEvidencePack:
    primary_freshness = _source_freshness(
        baseline_request.evidence_freshness, BaselineEvidenceSource.PRIMARY
    )
    primary = _feature_facts(baseline_request.primary_features.results, primary_freshness)
    core_prefixes = (
        "trend.",
        "structure.",
        "breakout.",
        "breakdown.",
        "support.",
        "resistance.",
    )
    core = tuple(item for item in primary if item.metric_id.startswith(core_prefixes))
    momentum = tuple(
        item
        for item in primary
        if item.metric_id in {"return.percent", "range.move_over_atr"}
    )
    if baseline_request.indicators is not None:
        indicator_freshness = _source_freshness(
            baseline_request.evidence_freshness,
            BaselineEvidenceSource.INDICATOR,
        )
        momentum = (
            *momentum,
            *(
                fact
                for result in baseline_request.indicators.results
                if result.status in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}
                for fact in indicator_facts(result, freshness=indicator_freshness)
            ),
        )
    participation = tuple(
        item
        for item in primary
        if item.metric_id.startswith(("participation.", "volume."))
    )
    volatility = tuple(
        item for item in primary if item.metric_id.startswith("volatility.")
    )
    mtf_freshness = _source_freshness(
        baseline_request.evidence_freshness,
        BaselineEvidenceSource.MULTI_TIMEFRAME,
    )
    mtf = (
        _feature_facts(
            baseline_request.multi_timeframe_features.results,
            mtf_freshness,
        )
        if baseline_request.multi_timeframe_features is not None
        else ()
    )
    constituent_facts = (
        multi_timeframe_constituent_facts(
            baseline_request.multi_timeframe_context,
            freshness=mtf_freshness,
        )
        if baseline_request.multi_timeframe_context is not None
        else ()
    )
    mtf = (
        *mtf,
        *(
            item
            for item in constituent_facts
            if item.interval != baseline_request.primary_timeframe
        ),
    )
    baseline = baseline_facts(assessment, freshness=primary_freshness)
    groups = (
        ("a2-technical-core", EvidenceType.TECHNICAL, core),
        ("a2-technical-momentum", EvidenceType.TECHNICAL, momentum),
        ("a2-participation", EvidenceType.VOLUME, participation),
        ("a2-volatility", EvidenceType.VOLATILITY, volatility),
        ("a2-mtf", EvidenceType.TECHNICAL, mtf),
        ("a2-baseline", EvidenceType.OTHER, baseline),
    )
    references = tuple(
        _reference(evidence_id, evidence_type, assessment.subject, facts, created_at)
        for evidence_id, evidence_type, facts in groups
        if facts
    )
    quality = max(
        (item.quality for item in references if item.quality is not None),
        key=_QUALITY_ORDER.__getitem__,
    )
    freshness = max(
        (item.freshness for item in references if item.freshness is not None),
        key=_FRESHNESS_ORDER.__getitem__,
    )
    return AgentEvidencePack(
        pack_id=f"{assessment.assessment_id}:technical-pack",
        request_id=f"{assessment.assessment_id}:technical-request",
        subject=assessment.subject,
        evidence_fingerprint=fingerprint,
        references=references,
        analysis_context_ids=assessment.evidence_context_ids,
        feature_bundle_ids=(baseline_request.primary_features.bundle_id,),
        indicator_bundle_ids=(
            (baseline_request.indicators.bundle_id,)
            if baseline_request.indicators is not None
            else ()
        ),
        multi_timeframe_context_ids=(
            (baseline_request.multi_timeframe_context.context_id,)
            if baseline_request.multi_timeframe_context is not None
            else ()
        ),
        deterministic_assessment_id=assessment.assessment_id,
        overall_quality=quality,
        overall_freshness=freshness,
        evidence_coverage=round(len(references) / len(groups), 4),
        created_at=created_at,
    )


def main() -> int:
    """Run read-only A2 acquisition followed by a zero-LLM A3.3 interpretation."""
    args = parse_args()
    now = datetime.now(TIAF_TIMEZONE)
    try:
        if args.input is not None:
            case = load_case(args.input)
            snapshot = case.snapshot
            assessment = case.run_record.assessment
        else:
            builder = AnalysisContextBuilder(
                DhanInstrumentResolver(),
                DhanMarketDataProvider(),
                DataFetchCoordinator(
                    scheduler=ProviderScheduler(dhan_rate_policy_registry())
                ),
                clock=lambda: now,
            )
            baseline_request = _build_request(
                builder,
                args.symbol,
                args.benchmark,
                args.timeframes,
                args.lookback_days,
                args.horizon,
                now,
            )
            policy = default_policy(args.horizon)
            snapshot = create_evidence_snapshot(
                baseline_request,
                policy_id=policy.policy_id,
                producer_version=__version__,
                benchmark_symbol=args.benchmark,
                snapshot_created_at=now,
            )
            assessment = BaselineEngine((policy,)).assess(snapshot.decision_request)
        interpretation_time = datetime.now(TIAF_TIMEZONE)
        pack = _technical_evidence_pack(
            snapshot.decision_request,
            assessment,
            snapshot.fingerprint,
            interpretation_time,
        )
        request = AgentRequest(
            request_id=pack.request_id,
            run_id=f"{assessment.assessment_id}:technical-run",
            subject=assessment.subject,
            instrument_type=InstrumentType.EQUITY,
            horizon=assessment.horizon,
            specialist=SpecialistId.TECHNICAL,
            purpose=AnalysisPurpose.OPPORTUNITY,
            trade_style=assessment.trade_style,
            analysis_mode=AnalysisMode.DETERMINISTIC_ONLY,
            task="Interpret supplied A2 technical evidence without recalculation.",
            a2_context_ids=assessment.evidence_context_ids,
            a2_evidence_ids=tuple(item.evidence_id for item in pack.references),
            deterministic_baseline_reference=assessment.assessment_id,
            evidence_fingerprint=snapshot.fingerprint,
            allowed_capabilities=(AgentCapability.READ_A2_EVIDENCE,),
            budget=AgentBudget(),
            created_at=interpretation_time,
        )
        record = AgentRuntime(AgentRegistry((TechnicalSpecialist(),))).run(request, pack)
        if record.opinion is None:
            detail = record.failure.detail if record.failure else record.status.value
            raise ValueError(f"technical specialist did not produce an opinion: {detail}")
        opinion = record.opinion
        technical = technical_assessment_from_opinion(opinion)
        print(f"Symbol                      : {opinion.subject}")
        print(f"A2 direction                : {technical.baseline_direction}")
        print(
            "A2 opportunity/class        : "
            f"{technical.baseline_opportunity_score} / "
            f"{technical.baseline_candidate_class}"
        )
        print(f"Technical stance            : {opinion.stance.value}")
        print(
            "Trend / momentum            : "
            f"{technical.trend_state.value} / {technical.momentum_state.value}"
        )
        print(
            "Structure / breakout        : "
            f"{technical.structure_state.value} / {technical.breakout_state.value}"
        )
        print(
            "Participation / volatility  : "
            f"{technical.participation_state.value} / "
            f"{technical.volatility_state.value}"
        )
        print(
            "MTF / extension / room      : "
            f"{technical.mtf_state.value} / {technical.extension_state.value} / "
            f"{technical.remaining_room.value}"
        )
        print(f"Baseline agreement          : {opinion.baseline_agreement.value}")
        policy_confidence = opinion.confidence.policy_derived
        print(
            "Confidence basis/value      : "
            f"{', '.join(technical.confidence_basis)} / "
            f"{policy_confidence.value if policy_confidence else None}"
        )
        print(f"Reasons                     : {', '.join(opinion.reason_codes) or 'none'}")
        print(f"Contradictions              : {len(technical.contradictions)}")
        print(f"Missing evidence            : {len(opinion.missing_evidence)}")
        print(f"Evidence fingerprint        : {opinion.evidence_fingerprint}")
        total_tokens = record.usage.input_tokens + record.usage.output_tokens
        print(
            "LLM calls/tokens/cost units : "
            f"{record.usage.llm_calls} / {total_tokens} / {record.usage.cost_units}"
        )
    except (CorpusError, TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Read-only technical-specialist smoke failed: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
