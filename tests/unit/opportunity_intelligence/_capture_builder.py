"""Offline fixture authoring only, NOT imported by the public acceptance helper.

Uses explicit synthetic specialist doubles to author hypothetical typed outputs.
They do not assert production specialist interpretation or live market truth.
"""

import json
from typing import Any

from scripts._a3_8_fixtures import request

from tiaf.agents import AgentOpinionV2, AgentRegistry, AgentRunStatus, AgentStance
from tiaf.agents.enums import CitationRole, ClaimKind
from tiaf.agents.evidence import EvidenceCitation, EvidenceClaim
from tiaf.context import EvidenceStatus
from tiaf.contracts import DataQuality, FreshnessState
from tiaf.data import InstrumentType
from tiaf.planner.digests import digest
from tiaf.service.opportunity_intelligence.handoff import detail
from tiaf.workflows import capture_json, default_registry, run_serial

DEFAULTS: dict[str, dict[str, Any]] = {
    "TECHNICAL": {
        "stance": "POSITIVE",
        "structure_state": "BULLISH_STRUCTURE",
        "momentum_state": "POSITIVE",
        "mtf_state": "ALIGNED_POSITIVE",
        "extension_state": "DEVELOPING",
        "remaining_room": "LARGE",
    },
    "FUNDAMENTAL": {
        "stance": "POSITIVE",
        "company_quality": "GOOD_QUALITY",
        "balance_sheet_state": "STRONG",
        "valuation_state": "FAIR",
    },
    "NEWS_EVENT": {
        "stance": "NEUTRAL",
        "materiality": "LOW",
        "execution_risk": "LOW",
        "contradiction_state": "NONE",
    },
    "RELATIVE_STRENGTH": {"stance": "POSITIVE", "relative_strength": "OUTPERFORMING"},
    "SECTOR": {"stance": "POSITIVE", "sector_state": "SUPPORTIVE"},
    "DERIVATIVES_CONTEXT": {
        "stance": "NEUTRAL",
        "volatility_state": "MODERATE",
        "liquidity_state": "ADEQUATE",
    },
    "OPPORTUNITY_QUALITY": {
        "stance": "POSITIVE",
        "quality_state": "GOOD",
        "maturity_state": "DEVELOPING",
        "remaining_room": "SUFFICIENT",
    },
    "OPPORTUNITY_RISK": {"stance": "NEUTRAL", "risk_level": "MODERATE"},
}


def build(case: str = "aligned") -> str:
    req = request(
        symbol="SYNTHETIC",
        fno=False if case == "non_fno" else None if case == "unknown_fno" else True,
    )
    if case == "sparse_kaynes":
        return capture_json(run_serial(request(), default_registry()))
    if case == "index":
        req = req.model_copy(
            update={
                "instrument": req.instrument.model_copy(
                    update={"instrument_type": InstrumentType.INDEX}
                )
            }
        )
    baseline = req.inventory.a2_pack.references[0]
    no_trade = case in {"baseline_watch", "baseline_no_trade"}
    changes = {
        "baseline.direction": "POSITIVE",
        "baseline.candidate_class": "NO_TRADE" if no_trade else "EARLY_OPPORTUNITY",
        "baseline.opportunity_score": 30.0 if no_trade else 70.0,
    }
    facts = tuple(f.model_copy(update={"value": changes[f.metric_id]}) for f in baseline.facts)
    baseline = baseline.model_copy(
        update={"facts": facts, "checksum": digest([f.model_dump(mode="json") for f in facts])}
    )
    pack = req.inventory.a2_pack.model_copy(
        update={"references": (baseline, *req.inventory.a2_pack.references[1:])}
    )
    req = req.model_copy(update={"inventory": req.inventory.model_copy(update={"a2_pack": pack})})
    if case == "stale":

        def stale_ref(ref: Any) -> Any:
            return ref.model_copy(
                update={"freshness": FreshnessState.STALE, "availability": EvidenceStatus.STALE}
            )

        pack = pack.model_copy(
            update={
                "references": tuple(stale_ref(r) for r in pack.references),
                "overall_freshness": FreshnessState.STALE,
            }
        )
        req = req.model_copy(
            update={
                "inventory": req.inventory.model_copy(
                    update={
                        "a2_pack": pack,
                        "references": tuple(stale_ref(r) for r in req.inventory.references),
                    }
                )
            }
        )
    overrides: dict[str, dict[str, Any]] = {}
    if case == "weak_company":
        overrides["FUNDAMENTAL"] = {"company_quality": "WEAK"}
    if case == "valuation":
        overrides["FUNDAMENTAL"] = {"valuation_state": "VERY_EXPENSIVE"}
    if case == "poor_timing":
        overrides["TECHNICAL"] = {"momentum_state": "FADING_POSITIVE"}
    if case == "extended":
        overrides["TECHNICAL"] = {"extension_state": "EXTENDED"}
    if case == "critical":
        overrides["OPPORTUNITY_RISK"] = {"risk_level": "CRITICAL"}
    if case in {"event_risk", "disputed_event"}:
        overrides["NEWS_EVENT"] = {
            "materiality": "HIGH",
            "execution_risk": "HIGH",
            "contradiction_state": "DISPUTED" if case == "disputed_event" else "NONE",
        }
    if case == "conflict":
        overrides["TECHNICAL"] = {"stance": "MIXED"}
    if case == "baseline_no_trade":
        overrides["TECHNICAL"] = {"stance": "NEUTRAL", "structure_state": "COMPRESSION"}
        overrides["FUNDAMENTAL"] = {"company_quality": "AVERAGE"}
    if case == "negative":
        overrides["TECHNICAL"] = {"stance": "NEGATIVE", "structure_state": "BEARISH_STRUCTURE"}

    class CapturedSpecialistDouble:
        def __init__(self, original: Any) -> None:
            self.original = original

        def capability(self) -> Any:
            return self.original.capability()

        def analyze(self, agent_request: Any, evidence: Any) -> AgentOpinionV2:
            source = self.original.analyze(agent_request, evidence)
            sid = source.specialist.value
            data = detail(source)
            data.update(DEFAULTS[sid])
            data.update(overrides.get(sid, {}))
            if "contradictions" in data:
                data["contradictions"] = []
            if case == "abstain" and sid in {
                "TECHNICAL",
                "OPPORTUNITY_QUALITY",
                "OPPORTUNITY_RISK",
            }:
                data["stance"] = "ABSTAIN"
            stance = AgentStance(data["stance"])
            status = (
                AgentRunStatus.ABSTAINED
                if stance is AgentStance.ABSTAIN
                else AgentRunStatus.SUCCESS
            )
            claims = tuple(
                EvidenceClaim(
                    claim_id=f"synthetic-claim:{source.specialist}:{r.evidence_id}",
                    kind=ClaimKind.INTERPRETIVE,
                    statement=(
                        "Explicitly synthetic precomputed specialist detail "
                        "for assembly acceptance only."
                    ),
                    evidence_type=r.evidence_type,
                    citations=(
                        EvidenceCitation(evidence_id=r.evidence_id, role=CitationRole.SUPPORTS),
                    ),
                    as_of=req.as_of,
                    provenance="synthetic-a39-fixture",
                    quality=DataQuality.GOOD,
                    freshness=FreshnessState.FRESH,
                )
                for r in evidence.references
            )
            result = source.model_copy(
                update={
                    "stance": stance,
                    "status": status,
                    "specialist_detail_json": json.dumps(data),
                    "evidence_claims": claims,
                    "supporting_evidence_ids": tuple(r.evidence_id for r in evidence.references),
                    "missing_evidence": (),
                    "reason_codes": ("SYNTHETIC_PRECOMPUTED_DETAIL",),
                    "contradictory_evidence_ids": (),
                    "risks": (),
                    "caveats": ("SYNTHETIC_ACCEPTANCE_ONLY",),
                }
            )
            return AgentOpinionV2.model_validate(result.model_dump())

    registry = default_registry()
    doubles = tuple(
        CapturedSpecialistDouble(registry.get(cap.specialist)) for cap in registry.capabilities()
    )
    record = run_serial(req, AgentRegistry(doubles))
    if not all(a.record is not None and a.record.opinion is not None for a in record.attempts):
        raise ValueError(
            [(a.node_id, a.record.failure if a.record else None) for a in record.attempts]
        )
    return capture_json(record)


if __name__ == "__main__":
    import sys

    print(build(sys.argv[1] if len(sys.argv) > 1 else "aligned"))
