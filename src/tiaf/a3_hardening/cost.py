"""Leaf-level A3 usage attribution with explicit monetary knowledge states."""

from collections import defaultdict

from tiaf.agents import AgentUsage, SpecialistId
from tiaf.market_intelligence import MarketIntelligenceRun
from tiaf.planner.digests import digest
from tiaf.workflows.ledger import reserved_usage
from tiaf.workflows.replay import replay_recorded

from .contracts import (
    A3CostSummary,
    BlobKind,
    CostKnowledge,
    CostMeasure,
    PortableA3ReplayPackage,
    UsageAttribution,
    UsageDisposition,
    UsageGroupSummary,
)
from .package import package_blob, validate_package


def _sum_usage(items: tuple[AgentUsage, ...], *, elapsed_seconds: float = 0) -> AgentUsage:
    return AgentUsage(
        llm_calls=sum(item.llm_calls for item in items),
        tool_calls=sum(item.tool_calls for item in items),
        input_tokens=sum(item.input_tokens for item in items),
        output_tokens=sum(item.output_tokens for item in items),
        cost_units=sum(item.cost_units for item in items),
        elapsed_seconds=elapsed_seconds,
    )


def _monetary_measure(
    calls: int,
    refs: tuple[str, ...],
    *,
    configured_units: float | None = None,
) -> CostMeasure:
    if calls == 0:
        return CostMeasure(
            knowledge=CostKnowledge.KNOWN_ZERO,
            amount=0,
            currency="USD",
            configured_units=configured_units,
            source_refs=refs,
        )
    return CostMeasure(
        knowledge=CostKnowledge.UNPRICED,
        configured_units=configured_units,
        source_refs=refs,
    )


def _specialist(accounting_id: str) -> SpecialistId | None:
    parts = accounting_id.split(":")
    if len(parts) >= 2 and parts[0] == "specialist":
        try:
            return SpecialistId(parts[1])
        except ValueError:
            return None
    return None


def _group(
    attributions: tuple[UsageAttribution, ...], *, by_provider: bool
) -> tuple[UsageGroupSummary, ...]:
    grouped: dict[str, list[UsageAttribution]] = defaultdict(list)
    for item in attributions:
        key = (
            item.provider_id
            if by_provider
            else (item.specialist.value if item.specialist else None)
        )
        if key:
            grouped[key].append(item)
    return tuple(
        UsageGroupSummary(
            key=key,
            attempts=len(items),
            provider_calls=sum(item.provider_calls for item in items),
            model_calls=sum(item.usage.llm_calls for item in items),
            failures=0,
            reused=sum(item.disposition is UsageDisposition.REUSED for item in items),
            service_times=tuple(item.usage.elapsed_seconds for item in items),
        )
        for key, items in sorted(grouped.items())
    )


def _market_intelligence_attributions(
    package: PortableA3ReplayPackage,
) -> tuple[UsageAttribution, ...]:
    record = replay_recorded(package_blob(package, BlobKind.A38_CAPTURE).content)
    parent_by_artifact = {
        reference.evidence_id: attempt.node_id
        for attempt in record.attempts
        if attempt.record is not None
        for reference in attempt.record.evidence_pack.references
    }
    items: list[UsageAttribution] = []
    for artifact in record.artifacts:
        if artifact.kind != "MarketIntelligenceRun":
            continue
        run = MarketIntelligenceRun.model_validate_json(artifact.canonical_json)
        parent = parent_by_artifact.get(artifact.artifact_id)
        for audit in run.audits:
            refs = (artifact.artifact_id, *audit.observation_ids)
            disposition = (
                UsageDisposition.REUSED
                if audit.cache_reused
                else UsageDisposition.FALLBACK
                if audit.sequence > 1
                else UsageDisposition.FRESH
            )
            calls = 0 if audit.cache_reused or audit.skip_reason else 1
            items.append(
                UsageAttribution(
                    attribution_id=(f"provider:{run.run_id}:{audit.sequence}:{audit.provider_id}"),
                    phase="MARKET_INTELLIGENCE_PROVIDER_ATTEMPT",
                    capability=audit.capability.value,
                    specialist=_specialist(f"specialist:{parent}" if parent else ""),
                    provider_id=audit.provider_id,
                    attempt_id=f"{run.run_id}:{audit.sequence}",
                    parent_accounting_id=(f"specialist:{parent}" if parent else None),
                    disposition=disposition,
                    usage=AgentUsage(
                        tool_calls=calls,
                        cost_units=audit.cost_units,
                        elapsed_seconds=audit.elapsed_seconds,
                    ),
                    provider_calls=calls,
                    monetary_cost=_monetary_measure(
                        calls,
                        refs,
                        configured_units=audit.cost_units,
                    ),
                    included_in_original_total=False,
                )
            )
    return tuple(items)


def summarize_a3_cost(
    package: PortableA3ReplayPackage,
    *,
    replay_execution_usage: AgentUsage | None = None,
) -> A3CostSummary:
    """Project the accepted ledger once; nested provider detail is non-debited."""
    package = validate_package(package)
    record = replay_recorded(package_blob(package, BlobKind.A38_CAPTURE).content)
    leaves: list[UsageAttribution] = []
    for reservation in record.reservations:
        actual = reservation.actual or reserved_usage(reservation.budget)
        provider_calls = reservation.actual_provider_calls or 0
        refs = (reservation.accounting_id,)
        monetary = (
            CostMeasure(
                knowledge=CostKnowledge.UNKNOWN,
                configured_units=reservation.budget.max_cost_units,
                source_refs=refs,
            )
            if reservation.actual is None
            else _monetary_measure(
                provider_calls + actual.llm_calls,
                refs,
                configured_units=actual.cost_units,
            )
        )
        leaves.append(
            UsageAttribution(
                attribution_id=f"reservation:{reservation.accounting_id}",
                phase="ORCHESTRATION_RESERVATION",
                specialist=_specialist(reservation.accounting_id),
                accounting_id=reservation.accounting_id,
                reservation_id=reservation.accounting_id,
                disposition=UsageDisposition.FRESH,
                usage=actual,
                provider_calls=provider_calls,
                monetary_cost=monetary,
                included_in_original_total=reservation.actual is not None,
            )
        )
    details = _market_intelligence_attributions(package)
    attributions = (*leaves, *details)
    included = tuple(item.usage for item in leaves if item.included_in_original_total)
    reconciled = _sum_usage(included, elapsed_seconds=record.result.usage.elapsed_seconds)
    if reconciled != record.result.usage:
        raise ValueError("leaf usage does not reconcile to captured orchestration usage")
    replay_usage = replay_execution_usage or AgentUsage()
    provider_calls = record.result.provider_calls
    model_calls = record.result.usage.llm_calls
    provider_refs = tuple(item.attribution_id for item in details if item.provider_calls > 0)
    provider_cost = (
        CostMeasure(
            knowledge=CostKnowledge.UNKNOWN,
            configured_units=sum(item.usage.cost_units for item in details),
            source_refs=provider_refs,
        )
        if record.result.held_provider_calls
        else _monetary_measure(
            provider_calls,
            provider_refs,
            configured_units=sum(item.usage.cost_units for item in details),
        )
    )
    model_refs = tuple(
        opinion.opinion_id for opinion in record.result.opinions if opinion.usage.llm_calls
    )
    model_units = sum(
        opinion.usage.cost_units for opinion in record.result.opinions if opinion.usage.llm_calls
    )
    model_cost = (
        CostMeasure(
            knowledge=CostKnowledge.UNKNOWN,
            configured_units=model_units,
            source_refs=model_refs,
        )
        if record.result.held_usage.llm_calls
        else _monetary_measure(
            model_calls,
            model_refs,
            configured_units=model_units,
        )
    )
    unknown_count = sum(
        measure.knowledge in {CostKnowledge.UNKNOWN, CostKnowledge.UNPRICED}
        for measure in (provider_cost, model_cost)
    )
    unknown_count += sum(
        item.monetary_cost.knowledge in {CostKnowledge.UNKNOWN, CostKnowledge.UNPRICED}
        for item in attributions
    )
    reuse_count = sum(item.disposition is UsageDisposition.REUSED for item in details)
    reuse_eligible = len(details)
    payload = {
        "original_usage": record.result.usage.model_dump(mode="json", exclude={"elapsed_seconds"}),
        "held_usage": record.result.held_usage.model_dump(mode="json", exclude={"elapsed_seconds"}),
        "provider_cost": provider_cost.model_dump(mode="json"),
        "model_cost": model_cost.model_dump(mode="json"),
        "attributions": [
            item.model_dump(mode="json", exclude={"usage": {"elapsed_seconds"}})
            for item in attributions
        ],
        "fallback_attempts": sum(item.disposition is UsageDisposition.FALLBACK for item in details),
        "reuse_count": reuse_count,
        "reuse_eligible_count": reuse_eligible,
    }
    fingerprint = digest(payload)
    return A3CostSummary(
        package_id=package.manifest.package_id,
        original_captured_usage=record.result.usage,
        original_held_usage=record.result.held_usage,
        replay_execution_usage=replay_usage,
        provider_monetary_cost=provider_cost,
        model_monetary_cost=model_cost,
        unknown_or_unpriced_count=unknown_count,
        attributions=attributions,
        provider_mix=_group(details, by_provider=True),
        specialist_mix=_group(tuple(leaves), by_provider=False),
        fallback_attempts=sum(item.disposition is UsageDisposition.FALLBACK for item in details),
        reuse_count=reuse_count,
        reuse_eligible_count=reuse_eligible,
        reuse_ratio=(reuse_count / reuse_eligible if reuse_eligible else None),
        fingerprint=fingerprint,
    )
