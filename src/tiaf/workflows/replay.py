"""Offline recorded replay and deterministic policy/specialist verification."""

import json
from typing import Never

from tiaf.agents import AgentRegistry, AgentRunRecord, AgentRuntime
from tiaf.contracts import ContractModel
from tiaf.market_intelligence import (
    AuthoritativeConfirmationResult,
    DeepResearchResult,
    MarketIntelligenceRun,
    SparseEvidenceGraph,
)
from tiaf.planner.digests import digest, semantic
from tiaf.planner.policy import build_plan, consumption_digest, dependencies, invocation_digest
from tiaf.planner.projection import project_opinion

from .composition import (
    CompositionRequiredness,
    PinnedVerificationError,
    PinnedVerificationFailure,
    specialist_capability_id,
)
from .ledger import ReservationLedger
from .records import OrchestrationRunRecord


def _fail_verification(
    record: OrchestrationRunRecord,
    failure: PinnedVerificationFailure,
    detail: str,
) -> Never:
    if record.composition is None:
        raise ValueError(detail)
    raise PinnedVerificationError(failure, detail)


def capture_json(record: OrchestrationRunRecord) -> str:
    record = OrchestrationRunRecord.model_validate_json(record.model_dump_json())
    payload = record.model_dump(mode="json")
    return json.dumps({"record": payload, "checksum": digest(payload)}, sort_keys=True)


def replay_recorded(content: str) -> OrchestrationRunRecord:
    captured = json.loads(content)
    if digest(captured["record"]) != captured["checksum"]:
        raise ValueError("capture checksum mismatch")
    record = OrchestrationRunRecord.model_validate(captured["record"])
    validators: dict[str, type[ContractModel]] = {
        "MarketIntelligenceRun": MarketIntelligenceRun,
        "AuthoritativeConfirmationResult": AuthoritativeConfirmationResult,
        "DeepResearchResult": DeepResearchResult,
        "SparseEvidenceGraph": SparseEvidenceGraph,
        "AgentRunRecord": AgentRunRecord,
    }
    for artifact in record.artifacts:
        validator = validators.get(artifact.kind)
        if validator is None:
            raise ValueError(f"unknown captured artifact schema: {artifact.kind}")
        validator.model_validate_json(artifact.canonical_json)
    artifact_ids = {a.artifact_id for a in record.artifacts}
    external_refs = (
        *record.request.inventory.normalized_run_ids,
        *record.request.inventory.confirmation_ids,
        *record.request.inventory.graph_ids,
        *record.request.inventory.prior_run_ids,
    )
    if not set(external_refs) <= artifact_ids:
        raise ValueError("missing captured external inventory reference")
    for decision in record.decisions:
        if (
            decision.action in {"ACQUIRE", "CONFIRM", "RESEARCH"}
            and not set(decision.trigger_ids) <= artifact_ids
        ):
            raise ValueError("missing captured child record")
    return record


def verify_deterministic(content: str, registry: AgentRegistry) -> OrchestrationRunRecord:
    try:
        record = replay_recorded(content)
    except (KeyError, TypeError, ValueError) as exc:
        detail = str(exc)
        failure = (
            PinnedVerificationFailure.MISSING_ARTIFACT
            if "missing captured" in detail.casefold()
            else PinnedVerificationFailure.POLICY_MISMATCH
            if "composition policy mismatch" in detail.casefold()
            else PinnedVerificationFailure.OUTPUT_FINGERPRINT_MISMATCH
            if "output fingerprint mismatch" in detail.casefold()
            else PinnedVerificationFailure.CORRUPTED_ENVELOPE
        )
        raise PinnedVerificationError(failure, detail) from exc
    policy_version = record.plans[0].policy_version
    verification_registry = registry
    if record.composition is None:
        specs = dependencies(registry, policy_version=policy_version)
    else:
        if (
            record.composition.policy_version != policy_version
            or record.composition.planner_version != record.plans[0].planner_version
        ):
            raise PinnedVerificationError(
                PinnedVerificationFailure.POLICY_MISMATCH,
                "captured composition and plan policy versions differ",
            )
        available = {
            item.specialist: registry.get(item.specialist)
            for item in registry.capabilities()
        }
        pinned = []
        participants = {
            item.capability_id: item for item in record.composition.participants
        }
        for pinned_spec in record.plans[0].registry:
            specialist = pinned_spec.capability.specialist
            participant = participants[specialist_capability_id(specialist)]
            implementation = available.get(specialist)
            if implementation is None:
                failure = (
                    PinnedVerificationFailure.REQUIRED_PARTICIPANT_UNRESOLVED
                    if participant.requiredness is CompositionRequiredness.REQUIRED
                    else PinnedVerificationFailure.MISSING_PINNED_CAPABILITY
                )
                raise PinnedVerificationError(
                    failure,
                    f"{specialist.value} is absent from the supplied resolver",
                )
            actual_capability = implementation.capability()
            if actual_capability.specialist_version != participant.interface_version:
                raise PinnedVerificationError(
                    PinnedVerificationFailure.INCOMPATIBLE_CAPABILITY_VERSION,
                    (
                        f"{specialist.value} expected {participant.interface_version} "
                        f"but resolved {actual_capability.specialist_version}"
                    ),
                )
            if actual_capability != pinned_spec.capability:
                raise PinnedVerificationError(
                    PinnedVerificationFailure.PINNED_DEPENDENCY_MISMATCH,
                    f"{specialist.value} capability declaration changed",
                )
            pinned.append(implementation)
        pinned_registry = AgentRegistry(tuple(pinned))
        verification_registry = pinned_registry
        specs = dependencies(pinned_registry, policy_version=policy_version)
        if specs != record.plans[0].registry:
            raise PinnedVerificationError(
                PinnedVerificationFailure.PINNED_DEPENDENCY_MISMATCH,
                "resolved dependency specifications differ from the capture",
            )
    ledger = ReservationLedger(record.request.budget, record.request.bounds.max_provider_calls)
    for entry in record.reservations:
        if not ledger.reserve(entry.accounting_id, entry.budget, entry.provider_calls):
            _fail_verification(
                record,
                PinnedVerificationFailure.CORRUPTED_ENVELOPE,
                "recorded work could not have been reserved within aggregate budget",
            )
        if entry.state != "OUTSTANDING":
            ledger.settle(entry.accounting_id, entry.actual, entry.actual_provider_calls)
    if ledger.entries() != record.reservations:
        _fail_verification(
            record,
            PinnedVerificationFailure.CORRUPTED_ENVELOPE,
            "reservation reconciliation mismatch",
        )
    for plan in record.plans:
        if plan != build_plan(
            record.request,
            specs,
            version=plan.version,
            policy_version=policy_version,
        ):
            if record.composition is None:
                raise ValueError("planner/dependency version or deterministic plan mismatch")
            raise PinnedVerificationError(
                PinnedVerificationFailure.PINNED_DEPENDENCY_MISMATCH,
                "deterministic plan differs from the pinned composition",
            )
    for attempt in record.attempts:
        captured = attempt.record
        if captured is None:
            continue  # Recorded denial/timeout; do not invent or re-execute missing work.
        spec = next(s for s in specs if s.capability.specialist == captured.specialist)
        expected_digest = invocation_digest(
            record.request, spec, captured.evidence_pack.references
        )
        if (
            expected_digest != attempt.input_digest
            or expected_digest != captured.request.evidence_fingerprint
        ):
            _fail_verification(
                record,
                PinnedVerificationFailure.CORRUPTED_ENVELOPE,
                "invocation input digest mismatch",
            )
        if (
            consumption_digest(record.request, spec, captured.evidence_pack.references)
            != attempt.consumed_digest
        ):
            _fail_verification(
                record,
                PinnedVerificationFailure.CORRUPTED_ENVELOPE,
                "consumed dependency digest mismatch",
            )
        ticks = iter((0.0, captured.usage.elapsed_seconds))
        runtime = AgentRuntime(
            verification_registry,
            wall_clock=lambda: record.request.as_of,
            elapsed_clock=lambda: next(ticks, captured.usage.elapsed_seconds),
        )
        actual_record = runtime.run(captured.request, captured.evidence_pack)
        if semantic(actual_record) != semantic(captured):
            raise PinnedVerificationError(
                PinnedVerificationFailure.DETERMINISTIC_OUTPUT_MISMATCH,
                f"deterministic specialist output changed: {captured.specialist.value}",
            )
    for projection in record.projections:
        if project_opinion(projection.source_opinion) != projection:
            _fail_verification(
                record,
                PinnedVerificationFailure.DETERMINISTIC_OUTPUT_MISMATCH,
                "typed projection verification mismatch",
            )
    return record
