"""Lossless failure-lineage and degradation projections over captured A3 records."""

from tiaf.agents import AgentRunStatus, SpecialistId
from tiaf.market_intelligence import MarketIntelligenceRun, ProviderFailureKind
from tiaf.planner.digests import digest
from tiaf.planner.models import NodeStatus, StopReason
from tiaf.service.opportunity_intelligence import OpportunityState, replay_intelligence
from tiaf.workflows.replay import replay_recorded

from .contracts import (
    A3FailureEvent,
    A3FailureSummary,
    BlobKind,
    CaptureStatus,
    DegradationStatus,
    DegradationSummary,
    FailureCategory,
    FailureCode,
    PortableA3ReplayPackage,
)
from .package import package_blob, validate_package

_PROVIDER_CODES = {
    ProviderFailureKind.RATE_LIMIT: FailureCode.RATE_LIMITED,
    ProviderFailureKind.TIMEOUT: FailureCode.TIMEOUT,
    ProviderFailureKind.MALFORMED_PAYLOAD: FailureCode.MALFORMED,
    ProviderFailureKind.AMBIGUOUS_MAPPING: FailureCode.AMBIGUOUS,
    ProviderFailureKind.OUT_OF_COVERAGE: FailureCode.OUT_OF_COVERAGE,
    ProviderFailureKind.UNAUTHORIZED: FailureCode.PERMISSION_DENIED,
    ProviderFailureKind.ACCESS_RESTRICTED: FailureCode.PERMISSION_DENIED,
    ProviderFailureKind.ANTI_BOT_DENIED: FailureCode.PERMISSION_DENIED,
    ProviderFailureKind.BUDGET_EXCEEDED: FailureCode.BUDGET_BLOCKED,
    ProviderFailureKind.PROVIDER_UNAVAILABLE: FailureCode.UNAVAILABLE,
    ProviderFailureKind.NETWORK: FailureCode.UNAVAILABLE,
    ProviderFailureKind.PARSE_FAILURE: FailureCode.MALFORMED,
    ProviderFailureKind.UNSUPPORTED_CAPABILITY: FailureCode.UNSUPPORTED,
}

_AGENT_CODES = {
    AgentRunStatus.BUDGET_EXCEEDED: FailureCode.BUDGET_BLOCKED,
    AgentRunStatus.TIMEOUT: FailureCode.TIMEOUT,
    AgentRunStatus.FAILED: FailureCode.EXCEPTION,
    AgentRunStatus.ABSTAINED: FailureCode.ABSTAIN,
    AgentRunStatus.INSUFFICIENT_EVIDENCE: FailureCode.INSUFFICIENT_EVIDENCE,
}

_NODE_CODES = {
    NodeStatus.FAILED: FailureCode.EXCEPTION,
    NodeStatus.TIMED_OUT: FailureCode.TIMEOUT,
    NodeStatus.BLOCKED: FailureCode.BUDGET_BLOCKED,
}

_STOP_CODES = {
    StopReason.TERMINAL_FAILURE: FailureCode.TERMINAL_FAILURE,
    StopReason.DEADLINE_EXCEEDED: FailureCode.DEADLINE_EXCEEDED,
    StopReason.BUDGET_EXHAUSTED: FailureCode.BUDGET_EXHAUSTED,
}


def failure_event(
    *,
    category: FailureCategory,
    code: FailureCode,
    phase: str,
    original_type: str,
    original_code: str,
    original_message: str,
    terminal: bool,
    artifact_ids: tuple[str, ...] = (),
    attempt_id: str | None = None,
    node_id: str | None = None,
    provider_id: str | None = None,
    specialist: SpecialistId | None = None,
    retry_of: str | None = None,
    fallback_for: str | None = None,
    usage_refs: tuple[str, ...] = (),
    affected_capabilities: tuple[str, ...] = (),
    affected_predicates: tuple[str, ...] = (),
) -> A3FailureEvent:
    """Normalize a captured failure while retaining its original typed identity."""
    payload = {
        "category": category,
        "code": code,
        "phase": phase,
        "original_type": original_type,
        "original_code": original_code,
        "original_message_ref": digest(original_message),
        "artifact_ids": artifact_ids,
        "attempt_id": attempt_id,
        "node_id": node_id,
        "provider_id": provider_id,
        "specialist": specialist,
        "retry_of": retry_of,
        "fallback_for": fallback_for,
        "terminal": terminal,
        "usage_refs": usage_refs,
        "affected_capabilities": affected_capabilities,
        "affected_predicates": affected_predicates,
    }
    return A3FailureEvent(
        failure_id=f"failure:{digest(payload)[:24]}",
        category=category,
        code=code,
        phase=phase,
        original_type=original_type,
        original_code=original_code,
        original_message_ref=digest(original_message),
        artifact_ids=artifact_ids,
        attempt_id=attempt_id,
        node_id=node_id,
        provider_id=provider_id,
        specialist=specialist,
        retry_of=retry_of,
        fallback_for=fallback_for,
        terminal=terminal,
        usage_refs=usage_refs,
        affected_capabilities=affected_capabilities,
        affected_predicates=affected_predicates,
    )


def _provider_events(record_json: str) -> tuple[A3FailureEvent, ...]:
    record = replay_recorded(record_json)
    events: list[A3FailureEvent] = []
    for artifact in record.artifacts:
        if artifact.kind != "MarketIntelligenceRun":
            continue
        run = MarketIntelligenceRun.model_validate_json(artifact.canonical_json)
        for index, item in enumerate(run.failures, 1):
            events.append(
                failure_event(
                    category=FailureCategory.EVIDENCE_PROVIDER,
                    code=_PROVIDER_CODES.get(item.kind, FailureCode.UNCLASSIFIED),
                    phase="MARKET_INTELLIGENCE_ROUTING",
                    original_type=type(item).__name__,
                    original_code=item.kind.value,
                    original_message=item.message,
                    terminal=not item.retryable,
                    artifact_ids=(artifact.artifact_id,),
                    attempt_id=f"{run.run_id}:failure:{index}",
                    provider_id=item.provider_id,
                    usage_refs=(f"provider:{run.run_id}:{index}:{item.provider_id}",),
                    affected_capabilities=(item.capability.value,),
                )
            )
    return tuple(events)


def summarize_a3_failures(package: PortableA3ReplayPackage) -> A3FailureSummary:
    package = validate_package(package)
    a38_json = package_blob(package, BlobKind.A38_CAPTURE).content
    a38 = replay_recorded(a38_json)
    a39 = replay_intelligence(package_blob(package, BlobKind.A39_CAPTURE).content)
    events = list(_provider_events(a38_json))

    for attempt in a38.attempts:
        if attempt.record is not None and attempt.record.status in _AGENT_CODES:
            run = attempt.record
            failure = run.failure
            original_type = failure.error_type if failure else "AgentOpinionState"
            detail = failure.detail if failure else (attempt.reason or run.status.value)
            events.append(
                failure_event(
                    category=FailureCategory.SPECIALIST,
                    code=_AGENT_CODES[run.status],
                    phase="SPECIALIST_INVOCATION",
                    original_type=original_type,
                    original_code=run.status.value,
                    original_message=detail,
                    terminal=run.status
                    in {
                        AgentRunStatus.BUDGET_EXCEEDED,
                        AgentRunStatus.TIMEOUT,
                        AgentRunStatus.FAILED,
                    },
                    attempt_id=run.record_id,
                    node_id=attempt.node_id,
                    specialist=run.specialist,
                    usage_refs=(f"reservation:specialist:{run.specialist.value}",),
                    affected_capabilities=(run.specialist.value,),
                )
            )
        elif attempt.status in _NODE_CODES:
            events.append(
                failure_event(
                    category=FailureCategory.ORCHESTRATION,
                    code=_NODE_CODES[attempt.status],
                    phase="NODE_OUTCOME",
                    original_type="NodeAttempt",
                    original_code=attempt.status.value,
                    original_message=attempt.reason or attempt.status.value,
                    terminal=attempt.status is not NodeStatus.BLOCKED,
                    attempt_id=f"{attempt.node_id}:{attempt.plan_version}",
                    node_id=attempt.node_id,
                    specialist=(
                        SpecialistId(attempt.node_id)
                        if attempt.node_id in {item.value for item in SpecialistId}
                        else None
                    ),
                    affected_capabilities=(attempt.node_id,),
                )
            )

    for stop in a38.result.stop_reasons:
        if stop not in _STOP_CODES:
            continue
        events.append(
            failure_event(
                category=FailureCategory.ORCHESTRATION,
                code=_STOP_CODES[stop],
                phase="ORCHESTRATION_STOP",
                original_type="StopReason",
                original_code=stop.value,
                original_message=stop.value,
                terminal=True,
                affected_capabilities=tuple(a38.result.gaps),
            )
        )

    result = a39.result
    required_impact = tuple(
        sorted(
            item.specialist.value
            for item in result.contributions
            if item.required and item.usable.value != "TRUE"
        )
    )
    optional_impact = tuple(
        sorted(
            item.specialist.value
            for item in result.contributions
            if not item.required
            and item.applicability == "APPLICABLE"
            and item.usable.value != "TRUE"
        )
    )
    if package.manifest.completeness.status is CaptureStatus.NON_REPLAYABLE:
        degradation_status = DegradationStatus.NON_REPLAYABLE
    elif result.summary.state is OpportunityState.INSUFFICIENT_EVIDENCE:
        degradation_status = DegradationStatus.INSUFFICIENT_EVIDENCE
    elif a38.result.status == "PARTIAL" or required_impact:
        degradation_status = DegradationStatus.PARTIAL
    elif events or optional_impact:
        degradation_status = DegradationStatus.DEGRADED_COMPLETE
    else:
        degradation_status = DegradationStatus.NONE
    degradation = DegradationSummary(
        status=degradation_status,
        surviving_capabilities=tuple(sorted(item.value for item in result.completeness.usable)),
        failed_capabilities=tuple(sorted(item.value for item in result.completeness.failed)),
        skipped_capabilities=tuple(
            sorted(
                item.specialist.value for item in result.contributions if item.outcome == "SKIPPED"
            )
        ),
        required_impact=required_impact,
        optional_impact=optional_impact,
        a38_status=a38.result.status,
        a39_state=result.summary.state,
        completeness_numerator=result.completeness.numerator,
        completeness_denominator=result.completeness.denominator,
        prerequisite_ids=tuple(sorted(item.requirement_id for item in result.prerequisites)),
    )
    ordered_events = tuple(sorted(events, key=lambda item: item.failure_id))
    fingerprint = digest(
        {
            "events": [item.model_dump(mode="json") for item in ordered_events],
            "degradation": degradation.model_dump(mode="json"),
        }
    )
    return A3FailureSummary(
        package_id=package.manifest.package_id,
        events=ordered_events,
        degradation=degradation,
        fingerprint=fingerprint,
    )
