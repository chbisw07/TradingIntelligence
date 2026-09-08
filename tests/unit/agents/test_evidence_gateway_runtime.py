"""A3.2 evidence authorization, A2 preservation, reuse, and failure tests."""

from datetime import timedelta
from time import sleep
from typing import cast

from tiaf.agents import (
    A2EvidenceEntry,
    A2EvidenceGateway,
    AgentBudget,
    AgentCapability,
    AgentEvidencePack,
    AuthorizationDecision,
    EvidenceGateway,
    EvidenceGatewayContext,
    EvidenceGatewayPolicy,
    EvidenceGatewayRegistry,
    EvidenceGatewayRequest,
    EvidenceGatewayResult,
    EvidenceGatewayRuntime,
    EvidenceGatewayStatus,
    GatewayCacheStatus,
    GatewayIdentity,
    InMemoryEvidenceGatewayCache,
)
from tiaf.context import EvidenceStatus
from tiaf.contracts import DataQuality, FreshnessState

from ._gateway_support import a2_entry, evidence_policy, evidence_request, gateway_budget
from ._support import NOW, evidence_pack, evidence_reference


def runtime_for(gateway: EvidenceGateway) -> EvidenceGatewayRuntime:
    return EvidenceGatewayRuntime(
        EvidenceGatewayRegistry((gateway,)),
        evidence_policy(),
        wall_clock=lambda: NOW,
        elapsed_clock=lambda: 0.0,
    )


def test_authorized_a2_read_preserves_pack_fingerprint_and_provenance() -> None:
    original = evidence_pack()
    run = runtime_for(A2EvidenceGateway((a2_entry(pack=original),))).fetch(
        evidence_request()
    )
    assert run.result.status is EvidenceGatewayStatus.SUCCESS
    assert run.result.evidence_pack == original
    assert run.result.evidence_fingerprint == original.evidence_fingerprint
    assert run.result.evidence_pack.references[0].producer_id == "tiaf.baseline"
    assert run.audit.authorization is AuthorizationDecision.ALLOWED
    assert run.audit.usage.tool_calls == 1


def test_a2_gateway_never_mutates_baseline_pack() -> None:
    original = evidence_pack()
    before = original.model_dump(mode="json")
    runtime_for(A2EvidenceGateway((a2_entry(pack=original),))).fetch(evidence_request())
    assert original.model_dump(mode="json") == before


def test_missing_a2_evidence_is_explicit() -> None:
    run = runtime_for(A2EvidenceGateway(())).fetch(evidence_request())
    assert run.result.status is EvidenceGatewayStatus.MISSING
    assert run.result.evidence_pack is None
    assert run.result.warnings == ("Requested A2 evidence is not present",)


def test_missing_requested_family_is_explicit() -> None:
    run = runtime_for(A2EvidenceGateway((a2_entry(),))).fetch(
        evidence_request(evidence_type="NEWS")
    )
    assert run.result.status is EvidenceGatewayStatus.MISSING
    assert "family" in run.result.warnings[0]


def test_partial_a2_evidence_remains_partial() -> None:
    reference = evidence_reference(availability=EvidenceStatus.PARTIAL).model_copy(
        update={"quality": DataQuality.PARTIAL}
    )
    pack = evidence_pack().model_copy(
        update={"references": (reference,), "overall_quality": DataQuality.PARTIAL}
    )
    run = runtime_for(A2EvidenceGateway((a2_entry(pack=pack),))).fetch(evidence_request())
    assert run.result.status is EvidenceGatewayStatus.PARTIAL
    assert run.result.quality is DataQuality.PARTIAL


def test_stale_pack_and_expired_validity_are_not_reused_as_fresh() -> None:
    stale_reference = evidence_reference(availability=EvidenceStatus.STALE)
    stale_pack = evidence_pack().model_copy(
        update={
            "references": (stale_reference,),
            "overall_freshness": FreshnessState.STALE,
        }
    )
    stale_entry = A2EvidenceEntry(
        evidence_pack=stale_pack,
        valid_until=NOW + timedelta(hours=1),
    )
    stale = runtime_for(A2EvidenceGateway((stale_entry,))).fetch(evidence_request())
    assert stale.result.status is EvidenceGatewayStatus.STALE
    assert stale.result.freshness is FreshnessState.STALE


def test_evidence_worse_than_required_freshness_is_explicitly_stale() -> None:
    aging_reference = evidence_reference().model_copy(
        update={"freshness": FreshnessState.AGING}
    )
    aging_pack = evidence_pack().model_copy(
        update={
            "references": (aging_reference,),
            "overall_freshness": FreshnessState.AGING,
        }
    )
    run = runtime_for(A2EvidenceGateway((a2_entry(pack=aging_pack),))).fetch(
        evidence_request(required_freshness=FreshnessState.FRESH)
    )
    assert run.result.status is EvidenceGatewayStatus.STALE


def test_authorization_denied_before_gateway_invocation() -> None:
    gateway = CountingGateway()
    run = runtime_for(gateway).fetch(evidence_request(allowed_capabilities=()))
    assert run.result.status is EvidenceGatewayStatus.UNAUTHORIZED_CAPABILITY
    assert run.audit.authorization is AuthorizationDecision.DENIED
    assert gateway.calls == 0


def test_global_policy_can_deny_request_granted_capability() -> None:
    gateway = CountingGateway()
    runtime = EvidenceGatewayRuntime(
        EvidenceGatewayRegistry((gateway,)),
        EvidenceGatewayPolicy(enabled_capabilities=(AgentCapability.READ_NEWS,)),
        wall_clock=lambda: NOW,
        elapsed_clock=lambda: 0.0,
    )
    run = runtime.fetch(evidence_request())
    assert run.result.status is EvidenceGatewayStatus.UNAUTHORIZED_CAPABILITY
    assert gateway.calls == 0


def test_tool_budget_precheck_prevents_invocation() -> None:
    gateway = CountingGateway()
    request = evidence_request(budget=AgentBudget(max_elapsed_seconds=1))
    run = runtime_for(gateway).fetch(request)
    assert run.result.status is EvidenceGatewayStatus.BUDGET_EXCEEDED
    assert gateway.calls == 0


def test_cache_hit_reuses_same_semantic_fingerprint_without_tool_call() -> None:
    gateway = CountingGateway()
    runtime = runtime_for(gateway)
    first = runtime.fetch(evidence_request())
    second = runtime.fetch(evidence_request(request_id="gateway-request-2"))
    assert first.result.cache_status is GatewayCacheStatus.MISS
    assert second.result.cache_status is GatewayCacheStatus.HIT
    assert second.result.usage.tool_calls == 0
    assert second.result.evidence_fingerprint == first.result.evidence_fingerprint
    assert gateway.calls == 1


def test_cache_expiry_and_gateway_version_invalidate_entry() -> None:
    cache = InMemoryEvidenceGatewayCache()
    result = CountingGateway().fetch(
        evidence_request(),
        EvidenceGatewayContext(
            authorized_capabilities=(AgentCapability.READ_A2_EVIDENCE,),
            remaining_budget=gateway_budget(),
            invoked_at=NOW,
            deadline_at=NOW + timedelta(seconds=1),
        ),
    )
    cache.put("key", result, now=NOW)
    assert (
        cache.get(
            "key",
            request_id="new",
            gateway_identity=result.gateway_identity,
            now=NOW + timedelta(hours=2),
        )
        is None
    )
    cache.put("key", result, now=NOW)
    assert (
        cache.get(
            "key",
            request_id="new",
            gateway_identity=GatewayIdentity(gateway_id="counting", gateway_version="2"),
            now=NOW,
        )
        is None
    )


def test_timeout_is_infrastructure_status_not_market_stance() -> None:
    gateway = CountingGateway(delay=0.05)
    run = runtime_for(gateway).fetch(evidence_request(timeout_seconds=0.001))
    assert run.result.status is EvidenceGatewayStatus.TIMEOUT
    assert run.result.evidence_pack is None
    assert run.result.failure is not None


def test_gateway_exception_is_sanitized_and_isolated() -> None:
    gateway = CountingGateway(error=RuntimeError("internal detail"))
    run = runtime_for(gateway).fetch(evidence_request())
    assert run.result.status is EvidenceGatewayStatus.FAILED
    assert run.result.failure is not None
    assert run.result.failure.detail == "gateway raised unexpected RuntimeError"


def test_invalid_gateway_output_is_rejected() -> None:
    gateway = CountingGateway(invalid=True)
    run = runtime_for(gateway).fetch(evidence_request())
    assert run.result.status is EvidenceGatewayStatus.INVALID_OUTPUT
    assert run.result.evidence_pack is None


def test_deferred_result_preserves_retry_time_and_audit() -> None:
    gateway = CountingGateway(deferred=True)
    run = runtime_for(gateway).fetch(evidence_request())
    assert run.result.status is EvidenceGatewayStatus.DEFERRED
    assert run.result.retry_after == NOW + timedelta(minutes=5)
    assert run.audit.status is EvidenceGatewayStatus.DEFERRED


class CountingGateway:
    def __init__(
        self,
        *,
        delay: float = 0.0,
        error: Exception | None = None,
        invalid: bool = False,
        deferred: bool = False,
    ) -> None:
        self.calls = 0
        self.delay = delay
        self.error = error
        self.invalid = invalid
        self.deferred = deferred

    def identity(self) -> GatewayIdentity:
        return GatewayIdentity(gateway_id="counting", gateway_version="1")

    def capabilities(self) -> tuple[AgentCapability, ...]:
        return (AgentCapability.READ_A2_EVIDENCE,)

    def can_handle(self, request: object) -> bool:
        return True

    def fetch(
        self,
        request: EvidenceGatewayRequest,
        context: EvidenceGatewayContext,
    ) -> EvidenceGatewayResult:
        del context
        self.calls += 1
        if self.delay:
            sleep(self.delay)
        if self.error:
            raise self.error
        if self.invalid:
            return cast(EvidenceGatewayResult, object())
        request_id = request.request_id
        capability = request.capability
        subject = request.subject
        if self.deferred:
            return EvidenceGatewayResult(
                request_id=request_id,
                capability=capability,
                subject=subject,
                status=EvidenceGatewayStatus.DEFERRED,
                gateway_identity=self.identity(),
                produced_at=NOW,
                retry_after=NOW + timedelta(minutes=5),
            )
        pack: AgentEvidencePack = evidence_pack()
        return EvidenceGatewayResult(
            request_id=request_id,
            capability=capability,
            subject=subject,
            status=EvidenceGatewayStatus.SUCCESS,
            gateway_identity=self.identity(),
            evidence_pack=pack,
            evidence_fingerprint=pack.evidence_fingerprint,
            source_timestamps=(NOW,),
            acquired_at=NOW,
            produced_at=NOW,
            valid_until=NOW + timedelta(hours=1),
            freshness=FreshnessState.FRESH,
            quality=DataQuality.GOOD,
            cache_status=GatewayCacheStatus.MISS,
        )
