"""Synthetic A3.4 evidence assembled through the fundamental gateway projection."""

from tiaf.agents import (
    AgentBudget,
    AgentCapability,
    AgentEvidencePack,
    AgentRequest,
    AnalysisMode,
    SpecialistId,
)
from tiaf.context import AnalysisPurpose
from tiaf.contracts import DataQuality, FreshnessState, Horizon, TradeStyle
from tiaf.data import InstrumentType
from tiaf.fundamentals import (
    FundamentalMetric,
    InMemoryFundamentalProvider,
    fundamental_evidence_pack,
)

from ..fundamentals._support import (
    NOW,
    facts,
    fundamental_request,
    gateway_request,
)


def fundamental_pack(
    *,
    overrides: dict[FundamentalMetric, float] | None = None,
    omit: tuple[FundamentalMetric, ...] = (),
    financial: bool = False,
    quality: DataQuality = DataQuality.GOOD,
    freshness: FreshnessState = FreshnessState.FRESH,
    source_conflict: bool = False,
) -> AgentEvidencePack:
    items = facts(
        overrides=overrides,
        omit=omit,
        financial=financial,
        quality=quality,
        freshness=freshness,
    )
    if source_conflict:
        roe = next(item for item in items if item.metric is FundamentalMetric.ROE)
        items = (
            *items,
            roe.model_copy(
                update={
                    "fact_id": "fact:roe:conflicting-source",
                    "value": roe.value + 10.0,
                    "source_provider": "fixture.exchange.alternate",
                    "source_reference": "fixture://alternate/roe",
                }
            ),
        )
    dataset = InMemoryFundamentalProvider(items).fetch(
        fundamental_request(financial=financial)
    )
    return fundamental_evidence_pack(
        gateway_request(financial=financial),
        dataset,
        created_at=NOW,
    )


def fundamental_agent_request(
    pack: AgentEvidencePack,
    *,
    trade_style: TradeStyle = TradeStyle.POSITIONAL,
    horizon: Horizon | None = None,
) -> AgentRequest:
    return AgentRequest(
        request_id=pack.request_id,
        run_id="run-fundamental",
        subject=pack.subject,
        instrument_type=InstrumentType.EQUITY,
        horizon=horizon or Horizon(label="six-month", min_days=90, max_days=180),
        specialist=SpecialistId.FUNDAMENTAL,
        purpose=AnalysisPurpose.OPPORTUNITY,
        trade_style=trade_style,
        analysis_mode=AnalysisMode.DETERMINISTIC_ONLY,
        task="Interpret only supplied normalized fundamental and A2 identity evidence.",
        a2_context_ids=pack.analysis_context_ids,
        a2_evidence_ids=("a2:evidence",),
        deterministic_baseline_reference=pack.deterministic_assessment_id,
        evidence_fingerprint=pack.evidence_fingerprint,
        allowed_capabilities=(
            AgentCapability.READ_A2_EVIDENCE,
            AgentCapability.READ_FUNDAMENTALS,
        ),
        budget=AgentBudget(),
        created_at=NOW,
    )
