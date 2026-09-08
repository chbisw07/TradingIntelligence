"""A3.3 registry/runtime, confidence, no-LLM, and authority acceptance."""

import ast
from datetime import timedelta
from pathlib import Path

from tiaf.agents import (
    A2EvidenceEntry,
    A2EvidenceGateway,
    AgentRegistry,
    AgentRunStatus,
    AgentRuntime,
    EvidenceGatewayPolicy,
    EvidenceGatewayRegistry,
    EvidenceGatewayRuntime,
    EvidenceGatewayStatus,
    SpecialistId,
    agent_record_json,
    load_agent_record_json,
)
from tiaf.agents.specialists.technical import (
    TechnicalSpecialist,
    technical_assessment_from_opinion,
)
from tiaf.contracts import DataQuality, FreshnessState, TradeStyle
from tiaf.data import InstrumentType

from ._gateway_support import evidence_request
from ._technical_support import technical_pack, technical_request


def test_registry_runtime_runs_no_llm_technical_specialist() -> None:
    registry = AgentRegistry((TechnicalSpecialist(),))
    record = AgentRuntime(registry).run(technical_request(), technical_pack())

    assert registry.get(SpecialistId.TECHNICAL).capability().supports_no_llm
    assert record.status is AgentRunStatus.SUCCESS
    assert record.opinion is not None
    assert record.opinion.evidence_claims
    assert record.opinion.deterministic_baseline_reference == "a2-assessment-technical"
    assert record.opinion.evidence_fingerprint == "3" * 64
    assert record.usage.llm_calls == 0
    assert record.usage.input_tokens == 0
    assert record.usage.output_tokens == 0
    assert record.usage.cost_units == 0
    assert record.opinion.model_identity is None
    assert registry.capabilities()[0].supported_instrument_types == (
        InstrumentType.EQUITY,
        InstrumentType.INDEX,
    )
    reconstructed = load_agent_record_json(agent_record_json(record))
    assert reconstructed == record
    assert reconstructed.opinion is not None
    assert reconstructed.opinion.policy_version == "1.0"


def test_authorized_a2_gateway_pack_flows_unchanged_into_specialist_runtime() -> None:
    original = technical_pack()
    gateway = A2EvidenceGateway(
        (
            A2EvidenceEntry(
                evidence_pack=original,
                valid_until=original.created_at + timedelta(hours=1),
            ),
        )
    )
    gateway_runtime = EvidenceGatewayRuntime(
        EvidenceGatewayRegistry((gateway,)),
        EvidenceGatewayPolicy(
            enabled_capabilities=(technical_request().allowed_capabilities[0],)
        ),
        wall_clock=lambda: original.created_at,
        elapsed_clock=lambda: 0.0,
    )
    gateway_run = gateway_runtime.fetch(
        evidence_request(
            request_id="gateway-technical",
            context_references=original.analysis_context_ids,
            evidence_fingerprint=original.evidence_fingerprint,
            deterministic_baseline_reference=original.deterministic_assessment_id,
        )
    )

    assert gateway_run.result.status is EvidenceGatewayStatus.SUCCESS
    assert gateway_run.result.evidence_pack == original
    record = AgentRuntime(AgentRegistry((TechnicalSpecialist(),))).run(
        technical_request(), gateway_run.result.evidence_pack
    )
    assert record.status is AgentRunStatus.SUCCESS
    assert record.opinion is not None
    assert record.opinion.evidence_fingerprint == original.evidence_fingerprint


def test_confidence_reflects_agreement_coverage_quality_and_freshness() -> None:
    specialist = TechnicalSpecialist()
    full = specialist.analyze(technical_request(), technical_pack())
    mixed = specialist.analyze(
        technical_request(),
        technical_pack(
            overrides={
                "indicator.rsi": 40.0,
                "indicator.macd": -0.4,
                "return.percent": -1.0,
                "participation.signed_volume_balance": -0.3,
            }
        ),
    )
    missing = specialist.analyze(technical_request(), technical_pack(core_only=True))
    degraded = specialist.analyze(
        technical_request(),
        technical_pack(optional_quality=DataQuality.DEGRADED),
    )
    stale = specialist.analyze(
        technical_request(),
        technical_pack(optional_freshness=FreshnessState.STALE),
    )
    insufficient = specialist.analyze(
        technical_request(),
        technical_pack(
            omit=(
                "trend.linear_slope_percent",
                "trend.signed_efficiency",
                "trend.linear_r2",
                "structure.higher_high_fraction",
                "structure.higher_low_fraction",
                "structure.lower_high_fraction",
                "structure.lower_low_fraction",
                "structure.position_in_rolling_range",
                "structure.range_compression_ratio",
                "structure.latest_bar_range_vs_average",
                "breakout.above_prior_high_percent",
                "breakout.high_above_prior_high_percent",
                "breakdown.below_prior_low_percent",
                "breakdown.low_below_prior_low_percent",
                "support.prior_low",
                "resistance.prior_high",
                "resistance.distance_atr",
                "support.distance_atr",
            )
        ),
    )

    assert full.confidence.policy_derived is not None
    assert mixed.confidence.policy_derived is not None
    assert missing.confidence.policy_derived is not None
    assert degraded.confidence.policy_derived is not None
    assert stale.confidence.policy_derived is not None
    assert insufficient.confidence.policy_derived is not None
    assert full.confidence.policy_derived.value > mixed.confidence.policy_derived.value
    assert full.confidence.policy_derived.value > missing.confidence.policy_derived.value
    assert full.confidence.policy_derived.value > degraded.confidence.policy_derived.value
    assert full.confidence.policy_derived.value > stale.confidence.policy_derived.value
    assert insufficient.confidence.policy_derived.value == 0
    assert full.confidence.self_reported is None
    assert full.confidence.empirically_calibrated is None


def test_horizon_policy_selects_supplied_timeframe_without_reconstruction() -> None:
    pack = technical_pack()
    core = pack.references[0]
    daily = core.facts[0].model_copy(
        update={"fact_id": "fact:ema:daily", "interval": "1d", "value": 2.0}
    )
    intraday = core.facts[0].model_copy(
        update={"fact_id": "fact:ema:intraday", "interval": "15m", "value": -2.0}
    )
    revised_core = core.model_copy(update={"facts": (*core.facts[1:], daily, intraday)})
    momentum = pack.references[1]
    return_fact = next(
        item for item in momentum.facts if item.metric_id == "return.percent"
    )
    intraday_return = return_fact.model_copy(
        update={"fact_id": "fact:return:intraday", "interval": "15m", "value": -1.0}
    )
    revised_momentum = momentum.model_copy(
        update={"facts": (*momentum.facts, intraday_return)}
    )
    revised_pack = pack.model_copy(
        update={
            "references": (
                revised_core,
                revised_momentum,
                *pack.references[2:],
            )
        }
    )

    positional = TechnicalSpecialist().analyze(technical_request(), revised_pack)
    day = TechnicalSpecialist().analyze(
        technical_request(trade_style=TradeStyle.DAY),
        revised_pack,
    )

    positional_detail = technical_assessment_from_opinion(positional)
    day_detail = technical_assessment_from_opinion(day)
    assert positional_detail.trend_state.value == "STRONG_UPTREND"
    assert day_detail.trend_state.value == "MIXED"
    assert "1d" in positional_detail.positive_timeframes
    assert "15m" in positional_detail.negative_timeframes


def test_technical_package_has_no_forbidden_authority_imports() -> None:
    root = Path("src/tiaf/agents/specialists/technical")
    forbidden = (
        "dhan",
        "httpx",
        "requests",
        "subprocess",
        "browser",
        "orders",
        "positions",
        "trade_monitor",
        "openai",
        "anthropic",
    )
    imported: set[str] = set()
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.casefold() for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.casefold())

    assert not any(term in module for term in forbidden for module in imported)


def test_interpreter_has_no_a2_calculator_or_clock_access() -> None:
    path = Path("src/tiaf/agents/specialists/technical/specialist.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert not any(module.startswith("tiaf.features") for module in modules)
    assert "tiaf.baseline.engine" not in modules
    assert "tiaf.baseline.scoring" not in modules
    assert "datetime.now" not in source
