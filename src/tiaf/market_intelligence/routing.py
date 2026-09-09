"""Deterministic capability routing and bounded progressive enrichment."""

import hashlib
import json
from datetime import datetime

from tiaf.agents import AgentUsage
from tiaf.contracts import DataQuality, FreshnessState
from tiaf.contracts.common import TIAF_TIMEZONE

from .enums import (
    CapabilitySupport,
    ContradictionResolution,
    EnrichmentAction,
    PointInTimeQuality,
    ProviderFailureKind,
    ProviderResultStatus,
    RoutingMode,
    SemanticMappingQuality,
    SourceAuthority,
)
from .models import (
    CapabilityRoutePolicy,
    ContradictionGroup,
    EnrichmentDecision,
    EvidenceCoverageAssessment,
    MarketIntelligenceRequest,
    MarketIntelligenceResearchPolicy,
    MarketIntelligenceResearchRequest,
    MarketIntelligenceResearchRun,
    MarketIntelligenceRun,
    NormalizedEvidenceBatch,
    ProviderCallAudit,
    ProviderCapabilityConstraints,
    ProviderFailure,
    ProviderFetchResult,
)
from .registry import MarketIntelligenceRegistry


class MarketIntelligenceRouter:
    def __init__(self, registry: MarketIntelligenceRegistry) -> None:
        self._registry = registry

    def execute(
        self,
        request: MarketIntelligenceRequest,
        policy: CapabilityRoutePolicy,
        *,
        run_id: str,
    ) -> MarketIntelligenceRun:
        if policy.capability is not request.capability:
            raise ValueError("route policy does not match request capability")
        required = policy.required_canonical_metrics or request.required_canonical_metrics
        if (
            policy.required_canonical_metrics
            and request.required_canonical_metrics
            and policy.required_canonical_metrics != request.required_canonical_metrics
        ):
            raise ValueError("policy and request required metrics disagree")

        started_at = datetime.now(TIAF_TIMEZONE)
        batches: list[NormalizedEvidenceBatch] = []
        audits: list[ProviderCallAudit] = []
        decisions: list[EnrichmentDecision] = []
        failures: list[ProviderFailure] = []
        successful = 0
        total_cost = 0.0
        total_elapsed = 0.0

        for provider_id in policy.provider_ids:
            if len(audits) >= policy.maximum_provider_calls:
                failures.append(
                    ProviderFailure(
                        kind=ProviderFailureKind.BUDGET_EXCEEDED,
                        provider_id="routing-policy",
                        capability=request.capability,
                        message="route maximum provider calls reached",
                    )
                )
                decisions.append(
                    EnrichmentDecision(
                        sequence=len(decisions),
                        action=EnrichmentAction.STOP_BUDGET,
                        reason="route maximum provider calls reached",
                    )
                )
                break
            if len(audits) >= request.budget.max_tool_calls:
                failures.append(
                    ProviderFailure(
                        kind=ProviderFailureKind.BUDGET_EXCEEDED,
                        provider_id="request-budget",
                        capability=request.capability,
                        message="request tool-call budget reached",
                    )
                )
                decisions.append(
                    EnrichmentDecision(
                        sequence=len(decisions),
                        action=EnrichmentAction.STOP_BUDGET,
                        reason="request tool-call budget reached",
                    )
                )
                break
            try:
                provider = self._registry.provider(provider_id)
            except LookupError:
                failures.append(
                    ProviderFailure(
                        kind=ProviderFailureKind.PROVIDER_UNAVAILABLE,
                        provider_id=provider_id,
                        capability=request.capability,
                        message=f"configured provider is not registered: {provider_id}",
                    )
                )
                decisions.append(
                    EnrichmentDecision(
                        sequence=len(decisions),
                        action=EnrichmentAction.CONTINUE,
                        reason=f"{provider_id} is disabled or unregistered",
                        next_provider_id=_next_provider(policy.provider_ids, provider_id),
                    )
                )
                continue
            declaration = provider.manifest.declaration_for(request.capability)
            if declaration is None or declaration.support is CapabilitySupport.UNSUPPORTED:
                failures.append(
                    ProviderFailure(
                        kind=ProviderFailureKind.UNSUPPORTED_CAPABILITY,
                        provider_id=provider_id,
                        capability=request.capability,
                        message=f"{provider_id} does not support requested capability",
                    )
                )
                decisions.append(
                    EnrichmentDecision(
                        sequence=len(decisions),
                        action=EnrichmentAction.CONTINUE,
                        reason=f"{provider_id} does not support requested capability",
                        next_provider_id=_next_provider(policy.provider_ids, provider_id),
                    )
                )
                continue
            assert declaration.constraints is not None
            if not _meets_route_quality(policy, declaration.constraints):
                failures.append(
                    ProviderFailure(
                        kind=ProviderFailureKind.OUT_OF_COVERAGE,
                        provider_id=provider_id,
                        capability=request.capability,
                        message="provider declaration does not meet route quality constraints",
                    )
                )
                decisions.append(
                    EnrichmentDecision(
                        sequence=len(decisions),
                        action=EnrichmentAction.CONTINUE,
                        reason=f"{provider_id} fails route authority/PIT constraints",
                        next_provider_id=_next_provider(policy.provider_ids, provider_id),
                    )
                )
                continue
            call_cost = declaration.constraints.cost_units_per_call
            route_cost_limit = policy.maximum_cost_units
            if total_cost + call_cost > request.budget.max_cost_units or (
                route_cost_limit is not None and total_cost + call_cost > route_cost_limit
            ):
                failures.append(
                    ProviderFailure(
                        kind=ProviderFailureKind.BUDGET_EXCEEDED,
                        provider_id=provider_id,
                        capability=request.capability,
                        message="next provider would exceed request cost budget",
                    )
                )
                decisions.append(
                    EnrichmentDecision(
                        sequence=len(decisions),
                        action=EnrichmentAction.STOP_BUDGET,
                        reason="next provider would exceed request cost budget",
                    )
                )
                break
            result = provider.fetch(request)
            result = _apply_freshness_constraint(request, declaration.constraints, result)
            failures.extend(result.failures)
            total_cost += result.cost_units
            total_elapsed += result.elapsed_seconds
            audit = ProviderCallAudit(
                sequence=len(audits) + 1,
                provider_id=provider_id,
                capability=request.capability,
                status=result.status,
                observation_ids=tuple(item.observation_id for item in result.observations),
                failure_kinds=tuple(item.kind for item in result.failures),
                cost_units=result.cost_units,
                elapsed_seconds=result.elapsed_seconds,
            )
            audits.append(audit)
            if (
                result.status
                not in {ProviderResultStatus.SUCCESS, ProviderResultStatus.PARTIAL}
                and result.status not in policy.fallback_statuses
            ):
                decisions.append(
                    EnrichmentDecision(
                        sequence=len(decisions),
                        action=EnrichmentAction.STOP_NO_ELIGIBLE_PROVIDER,
                        reason=(
                            f"{result.status} is not configured to permit provider fallback"
                        ),
                    )
                )
                break
            if result.status in {ProviderResultStatus.SUCCESS, ProviderResultStatus.PARTIAL}:
                successful += 1
                batches.append(self._registry.normalizer(provider_id).normalize(request, result))

            contradictions = _find_contradictions(request.subject, tuple(batches))
            coverage = _assess_coverage(
                required,
                tuple(batches),
                successful,
                contradictions,
                request.required_freshness,
            )
            if self._should_stop(policy, provider_id, successful, coverage, contradictions):
                decisions.append(
                    EnrichmentDecision(
                        sequence=len(decisions),
                        action=EnrichmentAction.STOP_SUFFICIENT,
                        reason="configured sufficiency and routing conditions met",
                    )
                )
                break
            decisions.append(
                EnrichmentDecision(
                    sequence=len(decisions),
                    action=EnrichmentAction.CONTINUE,
                    reason="evidence insufficient, conflicted, or route requires another source",
                    next_provider_id=_next_provider(policy.provider_ids, provider_id),
                )
            )
            if total_cost > request.budget.max_cost_units:
                break
            if total_elapsed > request.budget.max_elapsed_seconds or (
                policy.maximum_elapsed_seconds is not None
                and total_elapsed > policy.maximum_elapsed_seconds
            ):
                break
        else:
            decisions.append(
                EnrichmentDecision(
                    sequence=len(decisions),
                    action=EnrichmentAction.STOP_NO_ELIGIBLE_PROVIDER,
                    reason="configured provider route exhausted",
                )
            )

        contradictions = _find_contradictions(request.subject, tuple(batches))
        coverage = _assess_coverage(
            required,
            tuple(batches),
            successful,
            contradictions,
            request.required_freshness,
        )
        completed_at = datetime.now(TIAF_TIMEZONE)
        usage = AgentUsage(
            tool_calls=len(audits),
            cost_units=total_cost,
            elapsed_seconds=total_elapsed,
            metadata={"provider_successes": successful},
        )
        violations = request.budget.violations(usage)
        if violations:
            failures.append(
                ProviderFailure(
                    kind=ProviderFailureKind.BUDGET_EXCEEDED,
                    provider_id="request-budget",
                    capability=request.capability,
                    message=f"observed usage exceeded: {', '.join(violations)}",
                )
            )
        final_batches = tuple(batches)
        final_audits = tuple(audits)
        final_decisions = tuple(decisions)
        fingerprint = MarketIntelligenceRun.fingerprint_for(
            run_id=run_id,
            request=request,
            policy=policy,
            batches=final_batches,
            contradictions=contradictions,
            audits=final_audits,
            decisions=final_decisions,
            coverage=coverage,
            usage=usage,
            failures=tuple(failures),
            started_at=started_at,
            completed_at=completed_at,
        )
        return MarketIntelligenceRun(
            run_id=run_id,
            request=request,
            policy=policy,
            batches=final_batches,
            contradictions=contradictions,
            audits=final_audits,
            decisions=final_decisions,
            coverage=coverage,
            usage=usage,
            failures=tuple(failures),
            started_at=started_at,
            completed_at=completed_at,
            fingerprint=fingerprint,
        )

    @staticmethod
    def _should_stop(
        policy: CapabilityRoutePolicy,
        provider_id: str,
        successful: int,
        coverage: EvidenceCoverageAssessment,
        contradictions: tuple[ContradictionGroup, ...],
    ) -> bool:
        sufficient = coverage.sufficient and successful >= policy.minimum_successful_providers
        if policy.mode in {RoutingMode.FIRST_SUCCESS, RoutingMode.PRIMARY_WITH_FALLBACK}:
            return sufficient
        if policy.mode is RoutingMode.MULTI_SOURCE:
            return sufficient
        if policy.mode is RoutingMode.AUTHORITATIVE_CONFIRMATION:
            ambiguous = policy.require_authoritative_on_ambiguity and bool(
                coverage.ambiguous_metrics or contradictions
            )
            authority_seen = provider_id in policy.authoritative_provider_ids
            return sufficient and (not ambiguous or authority_seen)
        return False


class MarketIntelligenceResearchController:
    """Runs an authorized multi-capability plan through independent capability routes."""

    def __init__(self, router: MarketIntelligenceRouter) -> None:
        self._router = router

    def execute(
        self,
        request: MarketIntelligenceResearchRequest,
        policy: MarketIntelligenceResearchPolicy,
        *,
        research_run_id: str,
    ) -> MarketIntelligenceResearchRun:
        runs: list[MarketIntelligenceRun] = []
        for index, capability_request in enumerate(request.capability_requests, start=1):
            current_usage = _combined_usage(tuple(runs))
            if current_usage.tool_calls >= request.budget.max_tool_calls:
                break
            if current_usage.cost_units >= request.budget.max_cost_units:
                break
            run = self._router.execute(
                capability_request,
                policy.route_for(capability_request.capability),
                run_id=f"{research_run_id}:{index}:{capability_request.capability.value}",
            )
            runs.append(run)
            request.budget.ensure_within(_combined_usage(tuple(runs)))
        if len(runs) != len(request.capability_requests):
            raise ValueError("research budget exhausted before all requested capabilities ran")
        capability_runs = tuple(runs)
        usage = _combined_usage(capability_runs)
        return MarketIntelligenceResearchRun(
            research_run_id=research_run_id,
            request=request,
            policy=policy,
            capability_runs=capability_runs,
            usage=usage,
            fingerprint=MarketIntelligenceResearchRun.fingerprint_for(
                request, policy, capability_runs
            ),
        )


def _next_provider(provider_ids: tuple[str, ...], current: str) -> str | None:
    position = provider_ids.index(current) + 1
    return provider_ids[position] if position < len(provider_ids) else None


_SOURCE_AUTHORITY_RANK = {
    SourceAuthority.UNKNOWN: 0,
    SourceAuthority.AGGREGATOR: 1,
    SourceAuthority.TRUSTED_SECONDARY: 2,
    SourceAuthority.PRIMARY: 3,
    SourceAuthority.AUTHORITATIVE: 4,
}
_PIT_QUALITY_RANK = {
    PointInTimeQuality.UNKNOWN: 0,
    PointInTimeQuality.LIMITED: 1,
    PointInTimeQuality.CONSERVATIVE: 2,
    PointInTimeQuality.EXACT: 3,
}


def _meets_route_quality(
    policy: CapabilityRoutePolicy, constraints: ProviderCapabilityConstraints
) -> bool:
    return (
        _SOURCE_AUTHORITY_RANK[constraints.source_authority]
        >= _SOURCE_AUTHORITY_RANK[policy.minimum_source_authority]
        and _PIT_QUALITY_RANK[constraints.point_in_time_quality]
        >= _PIT_QUALITY_RANK[policy.minimum_point_in_time_quality]
    )


def _apply_freshness_constraint(
    request: MarketIntelligenceRequest,
    constraints: ProviderCapabilityConstraints,
    result: ProviderFetchResult,
) -> ProviderFetchResult:
    if constraints.maximum_age is None or not result.observations:
        return result
    boundary = request.as_of - constraints.maximum_age
    stale = tuple(
        item for item in result.observations if (item.observed_at or item.available_from) < boundary
    )
    if not stale:
        return result
    failure = ProviderFailure(
        kind=ProviderFailureKind.STALE,
        provider_id=result.provider_id,
        capability=result.capability,
        message="provider observations exceed the declared maximum age",
    )
    return result.model_copy(
        update={
            "status": ProviderResultStatus.PARTIAL,
            "failures": (*result.failures, failure),
        }
    )


def _combined_usage(runs: tuple[MarketIntelligenceRun, ...]) -> AgentUsage:
    return AgentUsage(
        llm_calls=sum(item.usage.llm_calls for item in runs),
        tool_calls=sum(item.usage.tool_calls for item in runs),
        input_tokens=sum(item.usage.input_tokens for item in runs),
        output_tokens=sum(item.usage.output_tokens for item in runs),
        cost_units=sum(item.usage.cost_units for item in runs),
        elapsed_seconds=sum(item.usage.elapsed_seconds for item in runs),
        metadata={"capability_runs": len(runs)},
    )


def _assess_coverage(
    required: tuple[str, ...],
    batches: tuple[NormalizedEvidenceBatch, ...],
    successful: int,
    contradictions: tuple[ContradictionGroup, ...],
    required_freshness: FreshnessState,
) -> EvidenceCoverageAssessment:
    covered = {
        record.canonical_metric
        for batch in batches
        for record in batch.normalization_records
        if record.emitted_evidence_id is not None and record.canonical_metric is not None
    }
    ambiguous = {
        record.native_field
        for batch in batches
        for record in batch.normalization_records
        if record.mapping_quality is SemanticMappingQuality.AMBIGUOUS
    }
    missing = set(required) - covered
    has_stale = any(
        gap.kind is ProviderFailureKind.STALE for batch in batches for gap in batch.gaps
    )
    stale_metrics = tuple(sorted(required)) if has_stale else ()
    quality_limitations = tuple(
        sorted(
            {
                f"{item.provider_id}:{item.source_quality.value}"
                for batch in batches
                for item in batch.native_observations
                if item.source_quality is not DataQuality.GOOD
            }
        )
    )
    ratio = len(covered & set(required)) / len(required) if required else float(successful > 0)
    return EvidenceCoverageAssessment(
        required_metrics=required,
        covered_metrics=tuple(sorted(covered)),
        missing_metrics=tuple(sorted(missing)),
        ambiguous_metrics=tuple(sorted(ambiguous)),
        stale_metrics=stale_metrics,
        quality_limitations=quality_limitations,
        point_in_time_limitations=tuple(
            sorted(
                {
                    item.point_in_time_limitation
                    for batch in batches
                    for item in batch.native_observations
                    if item.point_in_time_limitation is not None
                }
            )
        ),
        contradiction_ids=tuple(item.contradiction_id for item in contradictions),
        source_lineage_ids=tuple(
            sorted(
                {
                    lineage_id
                    for batch in batches
                    for item in batch.native_observations
                    for lineage_id in item.lineage_observation_ids
                }
            )
        ),
        coverage=ratio,
        sufficient=(
            successful > 0
            and not missing
            and not (
                has_stale and required_freshness in {FreshnessState.FRESH, FreshnessState.AGING}
            )
        ),
    )


def _find_contradictions(
    subject: str, batches: tuple[NormalizedEvidenceBatch, ...]
) -> tuple[ContradictionGroup, ...]:
    grouped: dict[
        tuple[str, str],
        list[
            tuple[
                str,
                str,
                str | int | float | bool,
                str,
                tuple[str, ...],
                SemanticMappingQuality,
            ]
        ],
    ] = {}
    for batch in batches:
        observations = {item.observation_id: item for item in batch.native_observations}
        for record in batch.normalization_records:
            if record.emitted_evidence_id is None or record.canonical_metric is None:
                continue
            observation = observations[record.observation_id]
            key = (record.canonical_metric, observation.period_label or "")
            grouped.setdefault(key, []).append(
                (
                    record.emitted_evidence_id,
                    batch.provider_id,
                    observation.value,
                    observation.observation_id,
                    observation.lineage_observation_ids,
                    record.mapping_quality,
                )
            )
    contradictions = []
    for (metric, period), entries in sorted(grouped.items()):
        independent = [
            entry for entry in entries if not any(other[3] in entry[4] for other in entries)
        ]
        if len({entry[2] for entry in independent}) <= 1:
            continue
        evidence_ids = tuple(entry[0] for entry in independent)
        providers = tuple(dict.fromkeys(entry[1] for entry in independent))
        if len(providers) < 2:
            continue
        digest = hashlib.sha256(
            json.dumps([subject, metric, period, evidence_ids], sort_keys=True).encode()
        ).hexdigest()
        contradictions.append(
            ContradictionGroup(
                contradiction_id=digest,
                subject=subject,
                canonical_metric=metric,
                period_label=period or None,
                observation_ids=tuple(entry[3] for entry in independent),
                normalization_record_ids=tuple(
                    record.record_id
                    for batch in batches
                    for record in batch.normalization_records
                    if record.emitted_evidence_id in evidence_ids
                ),
                evidence_ids=evidence_ids,
                values=tuple(entry[2] for entry in independent),
                mapping_qualities=tuple(entry[5] for entry in independent),
                provider_ids=providers,
                resolution=ContradictionResolution.UNRESOLVED,
                notes=(f"conflicting values for reporting period {period}",),
            )
        )
    return tuple(contradictions)
