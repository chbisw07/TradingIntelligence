"""Deterministic, non-intelligent AnalysisContext diagnostics."""

from tiaf.context.models import AnalysisContext, ContextSummary


def summarize_context(context: AnalysisContext) -> ContextSummary:
    """Reduce context size for consoles without deriving a market opinion."""
    return ContextSummary(
        symbol=context.subject.symbol,
        quote_ltp=context.quote.ltp if context.quote is not None else None,
        history_bar_count=len(context.history.bars) if context.history is not None else 0,
        option_chain_strike_count=(
            len(context.option_chain.strikes) if context.option_chain is not None else 0
        ),
        option_expiry=context.option_chain.expiry if context.option_chain is not None else None,
        historical_option_series_count=(
            len(context.historical_options)
            if context.historical_options is not None
            else 0
        ),
        overall_quality=context.overall_quality,
        overall_retrieval_freshness=context.overall_retrieval_freshness,
        complete=context.complete,
        missing_required_evidence=context.missing_required_evidence,
        warnings=context.warnings,
    )
