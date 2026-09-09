"""Run the A3.6 Relative Strength Specialist over live or captured A2 evidence."""

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
    SpecialistId,
)
from tiaf.agents.specialists import (
    RelativeStrengthSpecialist,
    baseline_facts,
    relative_assessment_from_opinion,
    relative_evidence_reference,
)
from tiaf.baseline import BaselineEngine, BaselineEvidenceSource, default_policy
from tiaf.context import AnalysisContextBuilder, AnalysisPurpose, EvidenceStatus
from tiaf.contracts import DataQuality, EvidenceSource, EvidenceType, FreshnessState, TradeStyle
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import InstrumentType, TIAFDataError, normalize_interval, normalize_symbol
from tiaf.data.providers.dhan import (
    DhanInstrumentResolver,
    DhanMarketDataProvider,
    dhan_rate_policy_registry,
)
from tiaf.data.runtime import DataFetchCoordinator, ProviderScheduler
from tiaf.evaluation import CorpusError, create_evidence_snapshot, load_case
from tiaf.features import BenchmarkReference, BenchmarkRole


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--symbol")
    source.add_argument("--input", type=Path, help="captured A2.10 snapshot/run file")
    parser.add_argument("--benchmark")
    parser.add_argument(
        "--benchmark-role",
        choices=tuple(item.value for item in BenchmarkRole),
        default=BenchmarkRole.MARKET.value,
    )
    parser.add_argument(
        "--horizon",
        choices=tuple(item.value for item in TradeStyle),
        default=TradeStyle.POSITIONAL.value,
    )
    parser.add_argument("--timeframes", default="1d,1h,15m")
    parser.add_argument("--lookback-days", type=int, default=180)
    args = parser.parse_args()
    args.symbol = normalize_symbol(args.symbol or "RELIANCE")
    args.benchmark = normalize_symbol(args.benchmark) if args.benchmark else None
    args.horizon = TradeStyle(args.horizon)
    args.timeframes = tuple(
        dict.fromkeys(
            normalize_interval(item) for item in args.timeframes.split(",") if item.strip()
        )
    )
    if not args.timeframes or args.lookback_days <= 0:
        parser.error("timeframes must be non-empty and lookback-days must be positive")
    if args.input is None and args.benchmark is None:
        parser.error("--benchmark is required for live acquisition")
    return args


def _baseline_reference(
    assessment, freshness: FreshnessState, created_at: datetime
) -> AgentEvidenceReference:
    facts = baseline_facts(assessment, freshness=freshness)
    canonical = json.dumps(
        [item.model_dump(mode="json") for item in facts], sort_keys=True, separators=(",", ":")
    )
    return AgentEvidenceReference(
        evidence_id="a2-baseline",
        evidence_type=EvidenceType.OTHER,
        subject=assessment.subject,
        producer_id="tiaf.a2.baseline",
        producer_version=__version__,
        source=EvidenceSource.DERIVED,
        availability=EvidenceStatus.AVAILABLE,
        quality=assessment.market_state.quality,
        freshness=freshness,
        observed_at=max(item.as_of for item in facts),
        acquired_at=created_at,
        checksum=hashlib.sha256(canonical.encode()).hexdigest(),
        facts=facts,
    )


def main() -> int:
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
                DataFetchCoordinator(scheduler=ProviderScheduler(dhan_rate_policy_registry())),
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
        decision = snapshot.decision_request
        relative_bundle = decision.relative_features
        if relative_bundle is None:
            raise ValueError("captured/live A2 request has no relative-strength evidence")
        relative_freshness = next(
            (
                item.state
                for item in decision.evidence_freshness
                if item.source is BaselineEvidenceSource.RELATIVE
            ),
            FreshnessState.UNKNOWN,
        )
        first = relative_bundle.results[0]
        benchmark_symbol = args.benchmark or str(
            first.metadata.get("benchmark_symbol") or snapshot.benchmark_symbol or ""
        )
        if not benchmark_symbol:
            raise ValueError("explicit benchmark identity is unavailable")
        benchmark_role = (
            BenchmarkRole(args.benchmark_role)
            if args.input is None
            else BenchmarkRole(str(first.metadata.get("benchmark_role") or args.benchmark_role))
        )
        relative_reference = relative_evidence_reference(
            evidence_id="a2-relative",
            subject=assessment.subject,
            benchmark=BenchmarkReference(
                symbol=benchmark_symbol,
                role=benchmark_role,
                exchange=first.metadata.get("benchmark_exchange")
                if isinstance(first.metadata.get("benchmark_exchange"), str)
                else None,
            ),
            results=relative_bundle.results,
            freshness=relative_freshness,
        )
        created_at = datetime.now(TIAF_TIMEZONE)
        baseline_reference = _baseline_reference(assessment, relative_freshness, created_at)
        pack = AgentEvidencePack(
            pack_id=f"{assessment.assessment_id}:relative-pack",
            request_id=f"{assessment.assessment_id}:relative-request",
            subject=assessment.subject,
            evidence_fingerprint=snapshot.fingerprint,
            references=(relative_reference, baseline_reference),
            analysis_context_ids=assessment.evidence_context_ids,
            feature_bundle_ids=(relative_bundle.bundle_id,),
            relative_strength_evidence_ids=(relative_reference.evidence_id,),
            deterministic_assessment_id=assessment.assessment_id,
            overall_quality=relative_reference.quality or DataQuality.UNAVAILABLE,
            overall_freshness=relative_reference.freshness or FreshnessState.UNKNOWN,
            evidence_coverage=1.0,
            created_at=created_at,
        )
        agent_request = AgentRequest(
            request_id=pack.request_id,
            run_id=f"{assessment.assessment_id}:relative-run",
            subject=assessment.subject,
            instrument_type=InstrumentType.EQUITY,
            horizon=assessment.horizon,
            specialist=SpecialistId.RELATIVE_STRENGTH,
            purpose=AnalysisPurpose.OPPORTUNITY,
            trade_style=assessment.trade_style,
            analysis_mode=AnalysisMode.DETERMINISTIC_ONLY,
            task="Interpret supplied explicit-benchmark A2.8 evidence without recalculation.",
            a2_context_ids=assessment.evidence_context_ids,
            a2_evidence_ids=tuple(item.evidence_id for item in pack.references),
            deterministic_baseline_reference=assessment.assessment_id,
            evidence_fingerprint=snapshot.fingerprint,
            allowed_capabilities=(AgentCapability.READ_A2_EVIDENCE,),
            budget=AgentBudget(),
            created_at=created_at,
        )
        record = AgentRuntime(AgentRegistry((RelativeStrengthSpecialist(),))).run(
            agent_request, pack
        )
        if record.opinion is None:
            raise ValueError(record.failure.detail if record.failure else record.status.value)
        opinion = record.opinion
        detail = relative_assessment_from_opinion(opinion)
        print(
            "Symbol / benchmark        : "
            f"{opinion.subject} / {detail.benchmark_symbol} ({detail.benchmark_role.value})"
        )
        print(
            "A2 direction/class/score : "
            f"{assessment.market_state.direction.value} / "
            f"{assessment.candidate_class.value} / {assessment.opportunity_score}"
        )
        print(
            f"Relative stance/state     : {opinion.stance.value} / {detail.relative_strength.value}"
        )
        print(
            "Subject/benchmark/excess  : "
            f"{detail.subject_return_percent} / {detail.benchmark_return_percent} / "
            f"{detail.excess_return_percent}"
        )
        print(
            "Consistency / MTF         : "
            f"{detail.relative_consistency.value} / {detail.mtf_alignment.value}"
        )
        print(
            "Leadership / extreme      : "
            f"{detail.leadership_state.value} / {detail.extreme_state.value}"
        )
        print(f"Baseline agreement        : {opinion.baseline_agreement.value}")
        print(
            "Confidence / basis        : "
            f"{opinion.confidence.policy_derived.value} / "
            f"{', '.join(detail.confidence_basis)}"
        )
        print(
            "Quality / freshness       : "
            f"{opinion.evidence_quality.value} / {opinion.evidence_freshness.value}"
        )
        print(
            "Contradictions / missing  : "
            f"{len(detail.contradictions)} / {len(opinion.missing_evidence)}"
        )
        print(f"Reasons                   : {', '.join(opinion.reason_codes) or 'none'}")
        print(f"Evidence fingerprint      : {opinion.evidence_fingerprint}")
        print(
            "LLM calls/tokens/cost     : "
            f"{record.usage.llm_calls} / "
            f"{record.usage.input_tokens + record.usage.output_tokens} / "
            f"{record.usage.cost_units}"
        )
    except (CorpusError, TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Read-only relative-specialist inspection failed: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
