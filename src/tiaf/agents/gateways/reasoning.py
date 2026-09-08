"""Optional provider-neutral reasoning gateway with central budget authority."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from datetime import datetime
from time import monotonic

from pydantic import ValidationError

from tiaf.agents.budget import AgentUsage
from tiaf.agents.enums import ReasoningStatus
from tiaf.agents.models import (
    AgentFailure,
    ReasoningField,
    ReasoningModelIdentity,
    ReasoningRequest,
    ReasoningResponse,
)
from tiaf.contracts.common import TIAF_TIMEZONE

from .cache import reasoning_cache_key
from .contracts import (
    GatewayIdentity,
    ReasoningGatewayAuditRecord,
    ReasoningGatewayRequest,
    ReasoningGatewayResult,
    ReasoningGatewayRun,
)
from .enums import (
    DowngradePolicy,
    ModelCapability,
    ModelTier,
    ReasoningGatewayStatus,
    model_tier_rank,
)
from .errors import GatewayNotFoundError, GatewayOutputValidationError
from .policy import ModelTierMapping, ReasoningGatewayPolicy, budget_within
from .registry import ReasoningProviderRegistry

WallClock = Callable[[], datetime]
ElapsedClock = Callable[[], float]
OutputValidator = Callable[[tuple[ReasoningField, ...]], bool]


def _now() -> datetime:
    return datetime.now(TIAF_TIMEZONE)


class ReasoningGateway:
    """Select and invoke an optional model only through configured policy."""

    def __init__(
        self,
        registry: ReasoningProviderRegistry,
        policy: ReasoningGatewayPolicy,
        *,
        output_validators: dict[str, OutputValidator] | None = None,
        gateway_id: str = "tiaf.reasoning-gateway",
        gateway_version: str = "1.0",
        wall_clock: WallClock = _now,
        elapsed_clock: ElapsedClock = monotonic,
    ) -> None:
        self._registry = registry
        self._policy = policy
        self._validators = dict(output_validators or {})
        self._identity = GatewayIdentity(
            gateway_id=gateway_id,
            gateway_version=gateway_version,
        )
        self._wall_clock = wall_clock
        self._elapsed_clock = elapsed_clock

    def reason(self, request: ReasoningGatewayRequest) -> ReasoningGatewayRun:
        """Apply authorization, mapping, budget, timeout, validation, and audit."""
        started_at = self._wall_clock()
        elapsed_start = self._elapsed_clock()
        if not self._policy.enabled or request.requested_model_tier is ModelTier.NONE:
            reason = (
                None
                if request.requested_model_tier is ModelTier.NONE
                else "reasoning is globally disabled"
            )
            return self._finish(
                request,
                status=ReasoningGatewayStatus.MODEL_DISABLED,
                actual_tier=ModelTier.NONE,
                identity=None,
                usage=AgentUsage(),
                started_at=started_at,
                elapsed_start=elapsed_start,
                downgrade_reason=reason,
                warnings=("No model call was attempted",),
            )
        if (
            ModelCapability.STRUCTURED_REASONING
            not in request.allowed_model_capabilities
            or not set(request.allowed_model_capabilities)
            <= set(self._policy.allowed_model_capabilities)
        ):
            return self._failure(
                request,
                status=ReasoningGatewayStatus.UNAUTHORIZED_CAPABILITY,
                actual_tier=ModelTier.NONE,
                identity=None,
                error_type="GatewayAuthorizationError",
                detail="structured reasoning capability is not authorized",
                started_at=started_at,
                elapsed_start=elapsed_start,
                downgrade_reason="authorization denied",
            )
        if not budget_within(request.budget, self._policy.budget):
            return self._failure(
                request,
                status=ReasoningGatewayStatus.INVALID_REQUEST,
                actual_tier=ModelTier.NONE,
                identity=None,
                error_type="GatewayBudgetPolicyError",
                detail="request budget exceeds global reasoning policy",
                started_at=started_at,
                elapsed_start=elapsed_start,
                downgrade_reason="request exceeds policy authority",
            )
        selected = self._select_mapping(request.requested_model_tier)
        if selected is None:
            if self._policy.downgrade_policy is DowngradePolicy.NO_LLM_FALLBACK:
                return self._finish(
                    request,
                    status=ReasoningGatewayStatus.MODEL_DISABLED,
                    actual_tier=ModelTier.NONE,
                    identity=None,
                    usage=AgentUsage(),
                    started_at=started_at,
                    elapsed_start=elapsed_start,
                    downgrade_reason="requested model tier unavailable; no-LLM fallback",
                    warnings=("No model call was attempted",),
                )
            return self._failure(
                request,
                status=ReasoningGatewayStatus.UNAVAILABLE,
                actual_tier=request.requested_model_tier,
                identity=None,
                error_type="GatewayNotFoundError",
                detail="requested model tier is unavailable under current policy",
                started_at=started_at,
                elapsed_start=elapsed_start,
            )
        mapping, downgrade_reason = selected
        try:
            registration = self._registry.get(mapping.provider_id)
        except GatewayNotFoundError as exc:
            return self._failure(
                request,
                status=ReasoningGatewayStatus.UNAVAILABLE,
                actual_tier=mapping.tier,
                identity=None,
                error_type=type(exc).__name__,
                detail=str(exc),
                started_at=started_at,
                elapsed_start=elapsed_start,
                downgrade_reason=downgrade_reason,
            )
        identity = registration.identity
        if mapping.tier not in registration.supported_tiers or (
            mapping.model_id != identity.model_id
            or mapping.model_version != identity.model_version
            or mapping.configuration_id != identity.configuration_id
        ):
            return self._failure(
                request,
                status=ReasoningGatewayStatus.INVALID_REQUEST,
                actual_tier=mapping.tier,
                identity=identity,
                error_type="ModelMappingError",
                detail="configured model mapping does not match provider identity/tier",
                started_at=started_at,
                elapsed_start=elapsed_start,
                downgrade_reason=downgrade_reason,
            )
        precheck = self._budget_precheck(request, mapping.tier)
        if precheck is not None:
            return self._failure(
                request,
                status=ReasoningGatewayStatus.BUDGET_EXCEEDED,
                actual_tier=mapping.tier,
                identity=identity,
                error_type="AgentBudgetExceededError",
                detail=precheck,
                started_at=started_at,
                elapsed_start=elapsed_start,
                downgrade_reason=downgrade_reason,
            )
        if request.output_schema_id not in self._validators:
            return self._failure(
                request,
                status=ReasoningGatewayStatus.INVALID_REQUEST,
                actual_tier=mapping.tier,
                identity=identity,
                error_type="OutputSchemaNotRegisteredError",
                detail=f"output schema {request.output_schema_id!r} is not registered",
                started_at=started_at,
                elapsed_start=elapsed_start,
                downgrade_reason=downgrade_reason,
            )
        provider_request = ReasoningRequest(
            reasoning_request_id=request.reasoning_request_id,
            run_id=request.run_id,
            specialist=request.specialist,
            model_identity=identity,
            prompt_version=request.prompt_version,
            evidence_fingerprint=request.evidence_fingerprint,
            output_schema_id=request.output_schema_id,
            max_input_tokens=request.budget.max_input_tokens,
            max_output_tokens=request.budget.max_output_tokens,
            timeout_seconds=request.timeout_seconds,
            created_at=request.created_at,
            subject=request.subject,
            horizon=request.horizon,
            task=request.task,
            structured_instructions=request.instructions,
            model_tier=mapping.tier.name,
            allowed_model_capabilities=tuple(
                item.value for item in request.allowed_model_capabilities
            ),
            policy_version=request.policy_version,
            specialist_version=request.specialist_version,
            temperature=request.temperature,
            correlation_id=request.correlation_id,
        )
        try:
            raw = self._invoke_with_timeout(
                lambda: registration.provider.reason(provider_request),
                request.timeout_seconds,
            )
            if not isinstance(raw, ReasoningResponse):
                raise GatewayOutputValidationError(
                    "provider must return ReasoningResponse"
                )
            response = ReasoningResponse.model_validate(raw.model_dump(mode="python"))
            if (
                response.reasoning_request_id != request.reasoning_request_id
                or response.provider_id != identity.provider_id
                or response.model_id != identity.model_id
            ):
                raise GatewayOutputValidationError(
                    "provider response does not preserve request/model identity"
                )
            usage = self._observed_usage(
                response.usage,
                elapsed_start,
                model_call=model_tier_rank(mapping.tier)
                > model_tier_rank(ModelTier.DETERMINISTIC),
            )
            violations = tuple(
                sorted(
                    set(request.budget.violations(usage))
                    | set(self._policy.budget.violations(usage))
                )
            )
            if violations:
                return self._failure(
                    request,
                    status=(
                        ReasoningGatewayStatus.TIMEOUT
                        if "elapsed_seconds" in violations
                        else ReasoningGatewayStatus.BUDGET_EXCEEDED
                    ),
                    actual_tier=mapping.tier,
                    identity=identity,
                    error_type=(
                        "AgentTimeoutError"
                        if "elapsed_seconds" in violations
                        else "AgentBudgetExceededError"
                    ),
                    detail=f"reasoning usage exceeded: {', '.join(violations)}",
                    started_at=started_at,
                    elapsed_start=elapsed_start,
                    usage=usage,
                    downgrade_reason=downgrade_reason,
                )
            if response.status is not ReasoningStatus.SUCCESS:
                failure = response.failure or AgentFailure(
                    error_type="ReasoningProviderError",
                    detail="provider returned a non-success status",
                )
                return self._failure(
                    request,
                    status=(
                        ReasoningGatewayStatus.TIMEOUT
                        if response.status is ReasoningStatus.TIMEOUT
                        else ReasoningGatewayStatus.PROVIDER_FAILURE
                    ),
                    actual_tier=mapping.tier,
                    identity=identity,
                    error_type=failure.error_type,
                    detail=failure.detail,
                    started_at=started_at,
                    elapsed_start=elapsed_start,
                    usage=usage,
                    downgrade_reason=downgrade_reason,
                )
            if not self._validators[request.output_schema_id](response.fields):
                return self._failure(
                    request,
                    status=ReasoningGatewayStatus.MODEL_OUTPUT_INVALID,
                    actual_tier=mapping.tier,
                    identity=identity,
                    error_type="GatewayOutputValidationError",
                    detail="model output failed registered schema validation",
                    started_at=started_at,
                    elapsed_start=elapsed_start,
                    usage=usage,
                    downgrade_reason=downgrade_reason,
                )
            cache_key = reasoning_cache_key(
                task=request.task,
                evidence_fingerprint=request.evidence_fingerprint,
                model_identity=identity,
                model_tier=mapping.tier,
                prompt_version=request.prompt_version,
                policy_version=request.policy_version,
                specialist_version=request.specialist_version,
                output_schema_id=request.output_schema_id,
                model_configuration=mapping.configuration,
            )
            return self._finish(
                request,
                status=ReasoningGatewayStatus.SUCCESS,
                actual_tier=mapping.tier,
                identity=identity,
                fields=response.fields,
                usage=usage,
                finish_reason=response.finish_reason,
                model_configuration=mapping.configuration,
                downgrade_reason=downgrade_reason,
                cache_key=cache_key,
                started_at=started_at,
                elapsed_start=elapsed_start,
            )
        except FutureTimeoutError:
            return self._failure(
                request,
                status=ReasoningGatewayStatus.TIMEOUT,
                actual_tier=mapping.tier,
                identity=identity,
                error_type="AgentTimeoutError",
                detail="reasoning provider timed out",
                started_at=started_at,
                elapsed_start=elapsed_start,
                usage=self._observed_usage(
                    AgentUsage(),
                    elapsed_start,
                    model_call=model_tier_rank(mapping.tier)
                    > model_tier_rank(ModelTier.DETERMINISTIC),
                ),
                downgrade_reason=downgrade_reason,
            )
        except (GatewayOutputValidationError, ValidationError) as exc:
            return self._failure(
                request,
                status=ReasoningGatewayStatus.MODEL_OUTPUT_INVALID,
                actual_tier=mapping.tier,
                identity=identity,
                error_type="GatewayOutputValidationError",
                detail=str(exc),
                started_at=started_at,
                elapsed_start=elapsed_start,
                usage=self._observed_usage(
                    AgentUsage(),
                    elapsed_start,
                    model_call=model_tier_rank(mapping.tier)
                    > model_tier_rank(ModelTier.DETERMINISTIC),
                ),
                downgrade_reason=downgrade_reason,
            )
        except Exception as exc:
            return self._failure(
                request,
                status=ReasoningGatewayStatus.PROVIDER_FAILURE,
                actual_tier=mapping.tier,
                identity=identity,
                error_type="ReasoningProviderError",
                detail=f"provider raised unexpected {type(exc).__name__}",
                started_at=started_at,
                elapsed_start=elapsed_start,
                usage=self._observed_usage(
                    AgentUsage(),
                    elapsed_start,
                    model_call=model_tier_rank(mapping.tier)
                    > model_tier_rank(ModelTier.DETERMINISTIC),
                ),
                downgrade_reason=downgrade_reason,
            )

    def _select_mapping(
        self,
        requested: ModelTier,
    ) -> tuple[ModelTierMapping, str | None] | None:
        direct = (
            self._policy.mapping(requested)
            if requested in self._policy.allowed_model_tiers
            and model_tier_rank(requested) <= model_tier_rank(self._policy.max_model_tier)
            else None
        )
        if direct is not None:
            return direct, None
        if self._policy.downgrade_policy is not DowngradePolicy.DOWNGRADE:
            return None
        candidates = tuple(
            tier
            for tier in self._policy.allowed_model_tiers
            if model_tier_rank(ModelTier.NONE)
            < model_tier_rank(tier)
            < model_tier_rank(requested)
            and model_tier_rank(tier) <= model_tier_rank(self._policy.max_model_tier)
            and self._policy.mapping(tier) is not None
        )
        if not candidates:
            return None
        selected = max(candidates, key=model_tier_rank)
        mapping = self._policy.mapping(selected)
        assert mapping is not None
        return mapping, f"requested {requested.name}; downgraded to {selected.name} by policy"

    def _budget_precheck(
        self,
        request: ReasoningGatewayRequest,
        tier: ModelTier,
    ) -> str | None:
        if (
            model_tier_rank(tier) > model_tier_rank(ModelTier.DETERMINISTIC)
            and request.budget.max_llm_calls < 1
        ):
            return "LLM call budget is exhausted before invocation"
        if request.estimated_input_tokens > request.budget.max_input_tokens:
            return "estimated input tokens exceed request budget"
        if request.budget.max_output_tokens < 1:
            return "output-token budget is exhausted before invocation"
        if (
            request.budget.max_total_tokens is not None
            and request.estimated_input_tokens >= request.budget.max_total_tokens
        ):
            return "estimated input leaves no total-token budget for output"
        if request.timeout_seconds > request.budget.max_elapsed_seconds:
            return "request timeout exceeds elapsed-time budget"
        return None

    @staticmethod
    def _invoke_with_timeout(
        operation: Callable[[], ReasoningResponse],
        timeout_seconds: float,
    ) -> ReasoningResponse:
        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tiaf-reasoning")
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
        model_call: bool,
    ) -> AgentUsage:
        return usage.model_copy(
            update={
                "llm_calls": max(1 if model_call else 0, usage.llm_calls),
                "elapsed_seconds": max(
                    usage.elapsed_seconds,
                    self._elapsed_clock() - elapsed_start,
                    0.0,
                ),
            }
        )

    def _finish(
        self,
        request: ReasoningGatewayRequest,
        *,
        status: ReasoningGatewayStatus,
        actual_tier: ModelTier,
        identity: ReasoningModelIdentity | None,
        usage: AgentUsage,
        started_at: datetime,
        elapsed_start: float,
        fields: tuple[ReasoningField, ...] = (),
        finish_reason: str | None = None,
        model_configuration: tuple[ReasoningField, ...] = (),
        downgrade_reason: str | None = None,
        cache_key: str | None = None,
        warnings: tuple[str, ...] = (),
        failure: AgentFailure | None = None,
    ) -> ReasoningGatewayRun:
        completed = self._wall_clock()
        latency = max(usage.elapsed_seconds, self._elapsed_clock() - elapsed_start, 0.0)
        result = ReasoningGatewayResult(
            response_id=f"{request.reasoning_request_id}:response",
            reasoning_request_id=request.reasoning_request_id,
            status=status,
            requested_model_tier=request.requested_model_tier,
            actual_model_tier=actual_tier,
            provider_identity=identity,
            fields=fields,
            usage=usage,
            finish_reason=finish_reason,
            prompt_version=request.prompt_version,
            policy_version=request.policy_version,
            specialist_version=request.specialist_version,
            model_configuration=model_configuration,
            downgrade_reason=downgrade_reason,
            cache_key=cache_key,
            warnings=warnings,
            failure=failure,
            produced_at=completed,
        )
        return ReasoningGatewayRun(
            result=result,
            audit=ReasoningGatewayAuditRecord(
                gateway_run_id=f"{request.reasoning_request_id}:reasoning-run",
                gateway_identity=self._identity,
                reasoning_request_id=request.reasoning_request_id,
                provider_id=identity.provider_id if identity else None,
                model_id=identity.model_id if identity else None,
                model_version=identity.model_version if identity else None,
                requested_model_tier=request.requested_model_tier,
                actual_model_tier=actual_tier,
                prompt_version=request.prompt_version,
                policy_version=request.policy_version,
                specialist_version=request.specialist_version,
                evidence_fingerprint=request.evidence_fingerprint,
                status=status,
                usage=usage,
                latency_seconds=latency,
                started_at=started_at,
                completed_at=completed,
                failure=failure,
                correlation_id=request.correlation_id,
            ),
        )

    def _failure(
        self,
        request: ReasoningGatewayRequest,
        *,
        status: ReasoningGatewayStatus,
        actual_tier: ModelTier,
        identity: ReasoningModelIdentity | None,
        error_type: str,
        detail: str,
        started_at: datetime,
        elapsed_start: float,
        usage: AgentUsage | None = None,
        downgrade_reason: str | None = None,
    ) -> ReasoningGatewayRun:
        return self._finish(
            request,
            status=status,
            actual_tier=actual_tier,
            identity=identity,
            usage=usage or AgentUsage(),
            failure=AgentFailure(error_type=error_type, detail=detail),
            downgrade_reason=downgrade_reason,
            started_at=started_at,
            elapsed_start=elapsed_start,
        )
