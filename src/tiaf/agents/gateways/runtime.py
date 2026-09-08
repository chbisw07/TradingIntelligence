"""Bounded evidence runtime: authorization, cache, timeout, budget, and audit."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from datetime import datetime, timedelta
from time import monotonic

from pydantic import ValidationError

from tiaf.agents.budget import AgentUsage
from tiaf.agents.models import AgentFailure
from tiaf.contracts.common import TIAF_TIMEZONE

from .cache import InMemoryEvidenceGatewayCache, evidence_cache_key
from .contracts import (
    EvidenceGatewayAuditRecord,
    EvidenceGatewayContext,
    EvidenceGatewayRequest,
    EvidenceGatewayResult,
    EvidenceGatewayRun,
    GatewayIdentity,
)
from .enums import AuthorizationDecision, EvidenceGatewayStatus, GatewayCacheStatus
from .errors import GatewayNotFoundError, GatewayOutputValidationError
from .policy import EvidenceGatewayPolicy
from .registry import EvidenceGatewayRegistry

WallClock = Callable[[], datetime]
ElapsedClock = Callable[[], float]


def _now() -> datetime:
    return datetime.now(TIAF_TIMEZONE)


class EvidenceGatewayRuntime:
    """The sole execution authority for registered read-only evidence gateways."""

    def __init__(
        self,
        registry: EvidenceGatewayRegistry,
        policy: EvidenceGatewayPolicy,
        *,
        cache: InMemoryEvidenceGatewayCache | None = None,
        wall_clock: WallClock = _now,
        elapsed_clock: ElapsedClock = monotonic,
    ) -> None:
        self._registry = registry
        self._policy = policy
        self._cache = cache or InMemoryEvidenceGatewayCache()
        self._wall_clock = wall_clock
        self._elapsed_clock = elapsed_clock

    def fetch(
        self,
        request: EvidenceGatewayRequest,
        *,
        gateway_id: str | None = None,
    ) -> EvidenceGatewayRun:
        """Authorize and execute one request, always returning a typed audit record."""
        started_at = self._wall_clock()
        elapsed_start = self._elapsed_clock()
        unresolved = GatewayIdentity(gateway_id="UNRESOLVED", gateway_version="UNRESOLVED")
        if (
            request.capability not in request.allowed_capabilities
            or request.capability not in self._policy.enabled_capabilities
        ):
            return self._failed(
                request,
                identity=unresolved,
                status=EvidenceGatewayStatus.UNAUTHORIZED_CAPABILITY,
                error_type="GatewayAuthorizationError",
                detail=f"capability {request.capability.value} is not authorized",
                authorization=AuthorizationDecision.DENIED,
                started_at=started_at,
                elapsed_start=elapsed_start,
            )
        try:
            gateway = self._registry.resolve(request, gateway_id=gateway_id)
            identity = gateway.identity()
        except GatewayNotFoundError as exc:
            return self._failed(
                request,
                identity=unresolved,
                status=EvidenceGatewayStatus.UNAVAILABLE,
                error_type=type(exc).__name__,
                detail=str(exc),
                authorization=AuthorizationDecision.ALLOWED,
                started_at=started_at,
                elapsed_start=elapsed_start,
            )
        except Exception as exc:
            return self._failed(
                request,
                identity=unresolved,
                status=EvidenceGatewayStatus.INVALID_REQUEST,
                error_type=type(exc).__name__,
                detail=str(exc),
                authorization=AuthorizationDecision.ALLOWED,
                started_at=started_at,
                elapsed_start=elapsed_start,
            )

        key = evidence_cache_key(request)
        cached = self._cache.get(
            key,
            request_id=request.request_id,
            gateway_identity=identity,
            now=started_at,
        )
        if cached is not None:
            return self._run(
                request,
                cached,
                authorization=AuthorizationDecision.ALLOWED,
                started_at=started_at,
                elapsed_start=elapsed_start,
            )
        if request.budget.max_tool_calls < 1:
            return self._failed(
                request,
                identity=identity,
                status=EvidenceGatewayStatus.BUDGET_EXCEEDED,
                error_type="AgentBudgetExceededError",
                detail="tool-call budget is exhausted before invocation",
                authorization=AuthorizationDecision.ALLOWED,
                started_at=started_at,
                elapsed_start=elapsed_start,
                cache_status=GatewayCacheStatus.MISS,
            )
        if request.timeout_seconds > request.budget.max_elapsed_seconds:
            return self._failed(
                request,
                identity=identity,
                status=EvidenceGatewayStatus.INVALID_REQUEST,
                error_type="GatewayBudgetPolicyError",
                detail="request timeout exceeds request elapsed-time budget",
                authorization=AuthorizationDecision.ALLOWED,
                started_at=started_at,
                elapsed_start=elapsed_start,
                cache_status=GatewayCacheStatus.MISS,
            )
        context = EvidenceGatewayContext(
            authorized_capabilities=(request.capability,),
            remaining_budget=request.budget,
            invoked_at=started_at,
            deadline_at=started_at + timedelta(seconds=request.timeout_seconds),
        )
        try:
            raw = self._invoke_with_timeout(
                lambda: gateway.fetch(request, context),
                request.timeout_seconds,
            )
            if not isinstance(raw, EvidenceGatewayResult):
                raise GatewayOutputValidationError(
                    "gateway must return EvidenceGatewayResult"
                )
            result = EvidenceGatewayResult.model_validate(raw.model_dump(mode="python"))
            if (
                result.request_id != request.request_id
                or result.capability is not request.capability
                or result.subject != request.subject
                or result.gateway_identity != identity
            ):
                raise GatewayOutputValidationError(
                    "gateway result does not preserve request/gateway identity"
                )
            usage = self._observed_usage(result.usage, elapsed_start, tool_call=True)
            result = result.model_copy(update={"usage": usage})
            violations = request.budget.violations(usage)
            if violations:
                return self._failed(
                    request,
                    identity=identity,
                    status=(
                        EvidenceGatewayStatus.TIMEOUT
                        if "elapsed_seconds" in violations
                        else EvidenceGatewayStatus.BUDGET_EXCEEDED
                    ),
                    error_type=(
                        "AgentTimeoutError"
                        if "elapsed_seconds" in violations
                        else "AgentBudgetExceededError"
                    ),
                    detail=f"gateway usage exceeded: {', '.join(violations)}",
                    authorization=AuthorizationDecision.ALLOWED,
                    started_at=started_at,
                    elapsed_start=elapsed_start,
                    usage=usage,
                    cache_status=GatewayCacheStatus.MISS,
                    evidence_fingerprint=result.evidence_fingerprint,
                )
            self._cache.put(key, result, now=self._wall_clock())
            return self._run(
                request,
                result,
                authorization=AuthorizationDecision.ALLOWED,
                started_at=started_at,
                elapsed_start=elapsed_start,
            )
        except FutureTimeoutError:
            return self._failed(
                request,
                identity=identity,
                status=EvidenceGatewayStatus.TIMEOUT,
                error_type="AgentTimeoutError",
                detail="evidence gateway timed out",
                authorization=AuthorizationDecision.ALLOWED,
                started_at=started_at,
                elapsed_start=elapsed_start,
                usage=self._observed_usage(AgentUsage(), elapsed_start, tool_call=True),
                cache_status=GatewayCacheStatus.MISS,
            )
        except (GatewayOutputValidationError, ValidationError) as exc:
            return self._failed(
                request,
                identity=identity,
                status=EvidenceGatewayStatus.INVALID_OUTPUT,
                error_type="GatewayOutputValidationError",
                detail=str(exc),
                authorization=AuthorizationDecision.ALLOWED,
                started_at=started_at,
                elapsed_start=elapsed_start,
                usage=self._observed_usage(AgentUsage(), elapsed_start, tool_call=True),
                cache_status=GatewayCacheStatus.MISS,
            )
        except Exception as exc:
            return self._failed(
                request,
                identity=identity,
                status=EvidenceGatewayStatus.FAILED,
                error_type="GatewayExecutionError",
                detail=f"gateway raised unexpected {type(exc).__name__}",
                authorization=AuthorizationDecision.ALLOWED,
                started_at=started_at,
                elapsed_start=elapsed_start,
                usage=self._observed_usage(AgentUsage(), elapsed_start, tool_call=True),
                cache_status=GatewayCacheStatus.MISS,
            )

    @staticmethod
    def _invoke_with_timeout(
        operation: Callable[[], EvidenceGatewayResult],
        timeout_seconds: float,
    ) -> EvidenceGatewayResult:
        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tiaf-evidence")
        future = executor.submit(operation)
        try:
            return future.result(timeout=timeout_seconds)
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def _observed_usage(
        self,
        usage: AgentUsage,
        elapsed_start: float,
        *,
        tool_call: bool,
    ) -> AgentUsage:
        elapsed = max(0.0, self._elapsed_clock() - elapsed_start)
        return usage.model_copy(
            update={
                "tool_calls": max(1 if tool_call else 0, usage.tool_calls),
                "elapsed_seconds": max(elapsed, usage.elapsed_seconds),
            }
        )

    def _run(
        self,
        request: EvidenceGatewayRequest,
        result: EvidenceGatewayResult,
        *,
        authorization: AuthorizationDecision,
        started_at: datetime,
        elapsed_start: float,
    ) -> EvidenceGatewayRun:
        latency = max(result.usage.elapsed_seconds, self._elapsed_clock() - elapsed_start, 0.0)
        return EvidenceGatewayRun(
            result=result,
            audit=EvidenceGatewayAuditRecord(
                gateway_run_id=f"{request.request_id}:gateway-run",
                request_id=request.request_id,
                capability=request.capability,
                gateway_identity=result.gateway_identity,
                subject=request.subject,
                evidence_fingerprint=result.evidence_fingerprint,
                authorization=authorization,
                cache_status=result.cache_status,
                status=result.status,
                usage=result.usage,
                latency_seconds=latency,
                started_at=started_at,
                completed_at=self._wall_clock(),
                failure=result.failure,
                correlation_id=request.correlation_id,
            ),
        )

    def _failed(
        self,
        request: EvidenceGatewayRequest,
        *,
        identity: GatewayIdentity,
        status: EvidenceGatewayStatus,
        error_type: str,
        detail: str,
        authorization: AuthorizationDecision,
        started_at: datetime,
        elapsed_start: float,
        usage: AgentUsage | None = None,
        cache_status: GatewayCacheStatus = GatewayCacheStatus.NOT_CACHEABLE,
        evidence_fingerprint: str | None = None,
    ) -> EvidenceGatewayRun:
        actual = usage or self._observed_usage(AgentUsage(), elapsed_start, tool_call=False)
        failure = AgentFailure(error_type=error_type, detail=detail)
        result = EvidenceGatewayResult(
            request_id=request.request_id,
            capability=request.capability,
            subject=request.subject,
            status=status,
            gateway_identity=identity,
            evidence_fingerprint=evidence_fingerprint,
            produced_at=self._wall_clock(),
            cache_status=cache_status,
            usage=actual,
            failure=failure,
        )
        return self._run(
            request,
            result,
            authorization=authorization,
            started_at=started_at,
            elapsed_start=elapsed_start,
        )
