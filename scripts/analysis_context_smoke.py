"""Build and inspect one read-only Dhan-backed factual AnalysisContext."""

import argparse
from datetime import date, datetime

from pydantic import ValidationError

from tiaf.context import (
    AnalysisContext,
    AnalysisContextBatchItem,
    AnalysisContextBuilder,
    AnalysisContextError,
    AnalysisContextRequirement,
    AnalysisPurpose,
    BatchItemStatus,
    EvidenceDescriptor,
    summarize_context,
)
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import InstrumentQuery, InstrumentType, TIAFDataError
from tiaf.data.providers.dhan import (
    DhanInstrumentResolver,
    DhanMarketDataProvider,
    dhan_rate_policy_registry,
)
from tiaf.data.runtime import DataFetchCoordinator, FreshnessRequirement, ProviderScheduler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subjects = parser.add_mutually_exclusive_group()
    subjects.add_argument("--symbol")
    subjects.add_argument("--symbols", help="comma-separated symbols for ordered batch mode")
    parser.add_argument("--exchange", type=str.upper, choices=("NSE", "BSE"))
    parser.add_argument(
        "--purpose",
        default=AnalysisPurpose.RESEARCH.value,
        choices=[purpose.value for purpose in AnalysisPurpose],
    )
    parser.add_argument("--history-interval", default="1d")
    parser.add_argument("--lookback-days", type=int, default=90)
    derivatives = parser.add_mutually_exclusive_group()
    derivatives.add_argument(
        "--include-derivatives",
        action="store_true",
        help="request and require an explicit-expiry option chain",
    )
    derivatives.add_argument(
        "--optional-derivatives",
        action="store_true",
        help="request an explicit-expiry option chain without requiring it",
    )
    parser.add_argument("--expiry", type=date.fromisoformat)
    parser.add_argument("--repeat", action="store_true")
    return parser.parse_args()


def _slot(context: AnalysisContext, name: str) -> EvidenceDescriptor:
    return next(item for item in context.evidence if item.evidence_name == name)


def _source(slot: EvidenceDescriptor) -> str:
    return slot.fetch_disposition.value if slot.fetch_disposition is not None else "-"


def _print_context(context: AnalysisContext, label: str | None = None) -> None:
    summary = summarize_context(context)
    resolved = context.subject.resolved_instrument
    quote_slot = _slot(context, "quote")
    history_slot = _slot(context, "history")
    chain_slot = _slot(context, "option_chain")

    if label is not None:
        print(label)
    print("TRADINGINTELLIGENCE ANALYSIS CONTEXT")
    print("=" * 48)
    print(f"Symbol          : {summary.symbol}")
    print(f"Provider        : {resolved.provider_name}")
    print(f"Security ID     : {resolved.provider_instrument_id}")
    print(f"Created         : {context.created_at.isoformat()}")
    print(f"Purpose         : {context.requirements.purpose.value}")

    print("\nQuote")
    print("-" * 48)
    print(f"Requested       : {'YES' if quote_slot.requested else 'NO'}")
    print(f"Required        : {'YES' if quote_slot.required else 'NO'}")
    print(f"Status          : {quote_slot.status.value}")
    print(f"LTP             : {summary.quote_ltp if summary.quote_ltp is not None else '-'}")
    print(
        f"Retrieval Fresh.: "
        f"{quote_slot.retrieval_freshness.value if quote_slot.retrieval_freshness else '-'}"
    )
    print(f"Retrieval Age   : {quote_slot.retrieval_age_seconds}")
    print(f"Market Observed : {quote_slot.source_observed_at or '-'}")
    print(f"Observation Age : {quote_slot.observation_age_seconds}")
    print(f"Source          : {_source(quote_slot)}")

    print("\nHistory")
    print("-" * 48)
    print(f"Requested       : {'YES' if history_slot.requested else 'NO'}")
    print(f"Required        : {'YES' if history_slot.required else 'NO'}")
    print(f"Status          : {history_slot.status.value}")
    print(f"Interval        : {context.requirements.history_interval}")
    print(f"Bars            : {summary.history_bar_count}")
    if context.history is not None:
        print(
            f"From / To       : {context.history.requested_from} / "
            f"{context.history.requested_to}"
        )
    print(
        f"Retrieval Fresh.: "
        f"{history_slot.retrieval_freshness.value if history_slot.retrieval_freshness else '-'}"
    )
    print(f"Source Observed : {history_slot.source_observed_at or '-'}")
    print(f"Observation Age : {history_slot.observation_age_seconds}")
    print(f"Source          : {_source(history_slot)}")

    print("\nOption Chain")
    print("-" * 48)
    print(f"Requested       : {'YES' if chain_slot.requested else 'NO'}")
    print(f"Required        : {'YES' if chain_slot.required else 'NO'}")
    print(f"Status          : {chain_slot.status.value}")
    if context.option_chain is not None:
        print(f"Underlying LTP  : {context.option_chain.underlying_ltp}")
        print(f"Expiry          : {context.option_chain.expiry}")
        print(f"Strike Count    : {summary.option_chain_strike_count}")
        print(f"Source Observed : {chain_slot.source_observed_at}")
        print(f"Observation Age : {chain_slot.observation_age_seconds}")
        print(
            f"Retrieval Fresh.: "
            f"{chain_slot.retrieval_freshness.value if chain_slot.retrieval_freshness else '-'}"
        )
        print(f"Time Semantics  : {chain_slot.source_observation_semantics}")
        print(f"Source          : {_source(chain_slot)}")

    print("\nOverall")
    print("-" * 48)
    print(f"Complete        : {'YES' if context.complete else 'NO'}")
    print(f"Quality         : {context.overall_quality.value}")
    print(f"Retrieval Fresh.: {context.overall_retrieval_freshness.value}")
    print(f"Warnings        : {', '.join(context.warnings) if context.warnings else '-'}")


def _print_batch(
    results: tuple[AnalysisContextBatchItem, ...], label: str | None = None
) -> None:
    if label is not None:
        print(label)
    print("TRADINGINTELLIGENCE ANALYSIS CONTEXT BATCH")
    print("=" * 48)
    for index, item in enumerate(results, start=1):
        print(f"{index}. {item.symbol}")
        print(f"   Status          : {item.status.value}")
        if item.status is BatchItemStatus.DEFERRED:
            retry = (
                "unknown"
                if item.retry_after_seconds is None
                else f"{item.retry_after_seconds:.2f} sec"
            )
            print("   Reason          : PROVIDER_SCHEDULE_BLOCKED")
            print(f"   Detail          : {item.reason}")
            print(f"   Provider        : {item.provider}")
            print(f"   Operation       : {item.operation}")
            print(f"   Gate State      : {item.gate_state.value if item.gate_state else '-'}")
            print(f"   Retry After     : {retry}")
            print()
            continue
        if item.status is BatchItemStatus.ERROR:
            print(f"   Error Type      : {item.error_type}")
            print(f"   Error Detail    : {item.error_detail}")
            print()
            continue
        assert item.context is not None
        context = item.context
        print(f"   Complete        : {'YES' if context.complete else 'NO'}")
        print(f"   Quality         : {context.overall_quality.value}")
        print(f"   Retrieval Fresh.: {context.overall_retrieval_freshness.value}")
        print()


def main() -> int:
    """Resolve and build factual context without any market recommendation."""
    args = parse_args()
    try:
        derivatives_requested = args.include_derivatives or args.optional_derivatives
        if derivatives_requested and args.expiry is None:
            raise ValueError(
                "--expiry is required with --include-derivatives or --optional-derivatives"
            )
        if args.symbols and args.exchange:
            raise ValueError("--exchange is only supported with single-symbol mode")
        symbols = (
            tuple(item.strip() for item in args.symbols.split(",") if item.strip())
            if args.symbols
            else (args.symbol or "RELIANCE",)
        )
        if not symbols:
            raise ValueError("--symbols requires at least one symbol")
        requested_at = datetime.now(TIAF_TIMEZONE)
        provider = DhanMarketDataProvider()
        builder = AnalysisContextBuilder(
            DhanInstrumentResolver(),
            provider,
            DataFetchCoordinator(
                scheduler=ProviderScheduler(dhan_rate_policy_registry())
            ),
            derivatives_provider=provider,
            historical_options_provider=provider,
            clock=lambda: requested_at,
        )
        requirements = AnalysisContextRequirement(
            purpose=AnalysisPurpose(args.purpose),
            history_interval=args.history_interval,
            history_lookback_days=args.lookback_days,
            include_derivatives=derivatives_requested,
            require_derivatives=args.include_derivatives,
            option_expiry=args.expiry,
            quote_freshness=FreshnessRequirement(
                fresh_for_seconds=5,
                aging_for_seconds=30,
            ),
            history_freshness=FreshnessRequirement(
                fresh_for_seconds=3600,
                aging_for_seconds=86_400,
            ),
            derivatives_freshness=(
                FreshnessRequirement(fresh_for_seconds=5, aging_for_seconds=30)
                if derivatives_requested
                else None
            ),
        )
        if args.symbols:
            first_batch = builder.build_many(
                symbols, requirements, source_system="analysis_context_smoke"
            )
            _print_batch(first_batch, "FIRST BATCH" if args.repeat else None)
            if args.repeat:
                second_batch = builder.build_many(
                    symbols, requirements, source_system="analysis_context_smoke"
                )
                print()
                _print_batch(second_batch, "SECOND BATCH")
        else:
            query = InstrumentQuery(
                symbol=symbols[0],
                exchange=args.exchange,
                instrument_type=InstrumentType.EQUITY,
                provider="dhan",
            )
            first = builder.build(
                query, requirements, source_system="analysis_context_smoke"
            )
            _print_context(first, "FIRST BUILD" if args.repeat else None)
            if args.repeat:
                second = builder.build(
                    query, requirements, source_system="analysis_context_smoke"
                )
                print()
                _print_context(second, "SECOND BUILD")
    except (AnalysisContextError, TIAFDataError, ValidationError, ValueError) as exc:
        print(f"Dhan read-only AnalysisContext smoke failed: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
