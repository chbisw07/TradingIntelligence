"""Author captured upstream records, then test only the public downstream boundary."""

import json
from typing import Any

import pytest
from scripts._a3_8_fixtures import confirmation_services, financial_services, reference, request
from scripts._a3_9_cases import load_case

from tiaf.agents import AgentRuntime, SpecialistId
from tiaf.contracts import EvidenceType, FreshnessState
from tiaf.market_intelligence import (
    DeepResearchIntegrationController,
    MarketIntelligenceResearchController,
    ResearchDepth,
)
from tiaf.service.opportunity_intelligence import (
    OpportunityState,
    Truth,
    capture_intelligence,
    verify_intelligence,
)
from tiaf.service.opportunity_intelligence.contributions import (
    completeness,
    lineage_groups,
    project_contributions,
)
from tiaf.service.opportunity_intelligence.handoff import baseline_view
from tiaf.service.opportunity_intelligence.policy import evaluate
from tiaf.workflows import ControlledServices, EvidenceRevision, default_registry, run_serial
from tiaf.workflows.replay import capture_json, replay_recorded

from .test_acceptance import result
from .test_integrity_boundaries import assemble


@pytest.mark.parametrize("mode", ["reused", "superseded", "confirmation", "research"])
def test_original_packs_context_and_active_only(mode: str, monkeypatch: pytest.MonkeyPatch) -> None:
    req = request()
    services = ControlledServices()
    if mode == "reused":
        previous = run_serial(req, default_registry())
        prior = next(a.record for a in previous.attempts if a.node_id == "TECHNICAL")
        assert prior is not None
        services = ControlledServices(prior_runs=(prior,))
    elif mode == "superseded":
        revision = reference(
            req.subject,
            "chain",
            EvidenceType.DERIVATIVES,
            {"derivatives.atm_mean_iv": 60.0, "derivatives.days_to_expiry": 2},
        )
        services = ControlledServices(
            revisions=(
                EvidenceRevision(after_round=0, references=(revision,), reason="captured revision"),
            )
        )
    elif mode == "confirmation":
        req = req.model_copy(update={"permit_confirmation": True})
        services = confirmation_services(req)
    elif mode == "research":
        req = request(financials=False).model_copy(
            update={
                "permit_deep_research": True,
                "research_depth": ResearchDepth.L2_INVESTMENT_RESEARCH,
            }
        )
        services = financial_services(req)
        services.acquisitions = tuple(
            a.model_copy(update={"material": True}) for a in services.acquisitions
        )
        assert services.router is not None
        services.research_controller = DeepResearchIntegrationController(
            MarketIntelligenceResearchController(services.router)
        )
    upstream = run_serial(req, default_registry(), services)
    content = capture_json(upstream)

    def denied(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("A3.9 must never rerun a specialist")

    monkeypatch.setattr(AgentRuntime, "run", denied)
    run = assemble(content)
    assert verify_intelligence(capture_intelligence(run)).exact_match
    for contribution in run.result.contributions:
        if contribution.run_id:
            original = next(
                a.record
                for a in upstream.attempts
                if a.record and a.record.record_id == contribution.run_id
            )
            assert original is not None and original.opinion is not None
            assert contribution.input_digest == original.request.evidence_fingerprint
            assert contribution.confidence == original.opinion.confidence
    if mode == "reused":
        assert prior is not None
        tech = next(c for c in run.result.contributions if c.specialist is SpecialistId.TECHNICAL)
        assert tech.run_id == prior.record_id
        assert tech.outcome == "REUSED"
    elif mode == "superseded":
        assert run.result.audit.superseded_opinion_ids
        assert not set(run.result.audit.superseded_opinion_ids) & set(
            run.result.audit.active_opinion_ids
        )
    else:
        assert run.result.contexts
        assert run.result.audit.imported_provider_calls > 0
        assert run.assembly_usage.tool_calls == 0
        if mode == "confirmation":
            assert any(c.kind == "AUTHORITATIVE_FIELD" for c in run.result.contradictions)
        else:
            assert any(c.kind == "DeepResearchResult" for c in run.result.contexts)


@pytest.mark.parametrize("missing", [SpecialistId.OPPORTUNITY_RISK, SpecialistId.NEWS_EVENT])
def test_missing_required_facets_cannot_pass_positive_gates(missing: SpecialistId) -> None:
    run = result()
    contributions = tuple(
        c.model_copy(
            update={
                "usable": Truth.UNKNOWN,
                "facets": tuple(f.model_copy(update={"usable": Truth.UNKNOWN}) for f in c.facets),
            }
        )
        if c.specialist is missing
        else c
        for c in run.result.contributions
    )
    summary, _, _, _ = evaluate(
        run.request.policy,
        run.result.baseline,
        contributions,
        completeness(contributions, ()),
        (),
        run.result.trade_style,
    )
    assert summary.state is not OpportunityState.OPPORTUNITY
    if missing is SpecialistId.OPPORTUNITY_RISK:
        assert summary.state is OpportunityState.INSUFFICIENT_EVIDENCE


def test_optional_adverse_evidence_still_restricts() -> None:
    run = result("event_risk")
    contributions = tuple(
        c.model_copy(update={"required": False}) if c.specialist is SpecialistId.NEWS_EVENT else c
        for c in run.result.contributions
    )
    summary, _, _, _ = evaluate(
        run.request.policy,
        run.result.baseline,
        contributions,
        completeness(contributions, ()),
        (),
        run.result.trade_style,
    )
    assert summary.state is OpportunityState.WAIT


def test_shuffled_json_object_order_preserves_canonical_semantics() -> None:
    data = json.loads(load_case("aligned"))

    def reverse_keys(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: reverse_keys(v) for k, v in reversed(list(value.items()))}
        if isinstance(value, list):
            return [reverse_keys(v) for v in value]
        return value

    assert (
        assemble(json.dumps(reverse_keys(data))).fingerprint
        == assemble(json.dumps(data, indent=2)).fingerprint
    )


def test_provider_wrappers_with_shared_canonical_root_are_one_lineage() -> None:
    source = replay_recorded(load_case("aligned"))
    original = source.request.inventory.a2_pack.references[0]
    refs = tuple(
        original.model_copy(
            update={
                "evidence_id": provider,
                "facts": tuple(
                    f.model_copy(update={"source_evidence": ("same-canonical-root",)})
                    for f in original.facts
                ),
            }
        )
        for provider in ("provider-one", "provider-two")
    )
    inventory = source.inventories[-1].model_copy(update={"references": refs})
    source = source.model_copy(update={"inventories": (*source.inventories, inventory)})
    contribution = (
        result()
        .result.contributions[0]
        .model_copy(
            update={
                "evidence_ids": ("provider-one", "provider-two"),
            }
        )
    )
    groups = lineage_groups(source, (contribution,))
    assert len(groups) == 1 and groups[0].roots == ("same-canonical-root",)
    assert groups[0].independence == "UNKNOWN"


def test_stale_cited_fact_cannot_hide_behind_fresh_pack_summary() -> None:
    source = replay_recorded(load_case("aligned"))
    attempt = next(a for a in source.attempts if a.node_id == "TECHNICAL")
    assert attempt.record is not None
    pack = attempt.record.evidence_pack
    ref = pack.references[0]
    ref = ref.model_copy(
        update={
            "facts": tuple(
                f.model_copy(update={"freshness": FreshnessState.STALE}) for f in ref.facts
            )
        }
    )
    run = attempt.record.model_copy(
        update={
            "evidence_pack": pack.model_copy(
                update={
                    "references": (ref, *pack.references[1:]),
                }
            )
        }
    )
    changed = source.model_copy(
        update={
            "attempts": tuple(
                a.model_copy(update={"record": run}) if a.node_id == "TECHNICAL" else a
                for a in source.attempts
            )
        }
    )
    contributions, _ = project_contributions(changed, result().request.policy)
    tech = next(c for c in contributions if c.specialist is SpecialistId.TECHNICAL)
    assert tech.freshness is FreshnessState.FRESH
    assert tech.usable is Truth.UNKNOWN


def test_full_captured_baseline_is_preserved_without_calculation_during_view() -> None:
    from ..baseline.test_ranking_and_architecture import _assessment

    source = replay_recorded(load_case("aligned"))
    # Author a complete synthetic A2 record before calling the read-only view.
    full = _assessment(source.request.subject).model_copy(
        update={
            "assessment_id": source.result.a2_reference,
            "horizon": source.request.horizon,
            "created_at": source.request.as_of,
        }
    )
    pack = source.request.inventory.a2_pack
    refs = tuple(
        r.model_copy(
            update={"facts": tuple(f for f in r.facts if not f.metric_id.startswith("baseline."))}
        )
        for r in pack.references
    )
    changed = source.model_copy(
        update={
            "request": source.request.model_copy(
                update={
                    "inventory": source.request.inventory.model_copy(
                        update={
                            "a2_pack": pack.model_copy(
                                update={
                                    "references": refs,
                                    "metadata": {
                                        "baseline_assessment": full.model_dump(mode="json"),
                                    },
                                }
                            ),
                        }
                    ),
                }
            )
        }
    )
    view = baseline_view(changed)
    assert view.full_assessment_available
    assert view.captured_assessment == full
    assert view.opportunity_score == full.opportunity_score
    assert view.eligible == full.eligible
