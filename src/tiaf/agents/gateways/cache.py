"""Minimal freshness-aware A3 evidence reuse and reasoning-key preparation."""

import hashlib
import json
from datetime import datetime

from tiaf.agents.models import ReasoningField, ReasoningModelIdentity

from .contracts import EvidenceGatewayRequest, EvidenceGatewayResult, GatewayIdentity
from .enums import EvidenceGatewayStatus, GatewayCacheStatus, ModelTier


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def evidence_cache_key(request: EvidenceGatewayRequest) -> str:
    """Hash semantic evidence identity, excluding run/auth/budget bookkeeping."""
    payload = request.model_dump(
        mode="json",
        exclude={
            "schema_version",
            "request_id",
            "allowed_capabilities",
            "requesting_specialist",
            "correlation_id",
            "budget",
            "timeout_seconds",
            "metadata",
        },
    )
    return _digest(payload)


def reasoning_cache_key(
    *,
    task: str,
    evidence_fingerprint: str,
    model_identity: ReasoningModelIdentity,
    model_tier: ModelTier,
    prompt_version: str,
    policy_version: str,
    specialist_version: str,
    output_schema_id: str,
    model_configuration: tuple[ReasoningField, ...],
) -> str:
    """Prepare a future-safe reasoning reuse key; A3.2 does not cache opinions."""
    return _digest(
        {
            "task": task,
            "evidence_fingerprint": evidence_fingerprint,
            "provider_id": model_identity.provider_id,
            "model_id": model_identity.model_id,
            "model_version": model_identity.model_version,
            "configuration_id": model_identity.configuration_id,
            "model_tier": model_tier.name,
            "prompt_version": prompt_version,
            "policy_version": policy_version,
            "specialist_version": specialist_version,
            "output_schema_id": output_schema_id,
            "model_configuration": [
                item.model_dump(mode="json") for item in model_configuration
            ],
        }
    )


class InMemoryEvidenceGatewayCache:
    """Process-local cache for validated gateway results, not provider transport."""

    def __init__(self) -> None:
        self._entries: dict[str, EvidenceGatewayResult] = {}

    def get(
        self,
        key: str,
        *,
        request_id: str,
        gateway_identity: GatewayIdentity,
        now: datetime,
    ) -> EvidenceGatewayResult | None:
        """Return a compatible fresh result and invalidate stale entries."""
        result = self._entries.get(key)
        if result is None:
            return None
        if (
            result.gateway_identity != gateway_identity
            or result.valid_until is None
            or now >= result.valid_until
            or result.status not in {
                EvidenceGatewayStatus.SUCCESS,
                EvidenceGatewayStatus.PARTIAL,
            }
        ):
            self._entries.pop(key, None)
            return None
        return result.model_copy(
            update={
                "request_id": request_id,
                "cache_status": GatewayCacheStatus.HIT,
                "usage": result.usage.model_copy(
                    update={"tool_calls": 0, "elapsed_seconds": 0.0}
                ),
                "produced_at": now,
            }
        )

    def put(self, key: str, result: EvidenceGatewayResult, *, now: datetime) -> None:
        """Cache only accepted factual results with an unexpired validity bound."""
        if (
            result.status in {EvidenceGatewayStatus.SUCCESS, EvidenceGatewayStatus.PARTIAL}
            and result.valid_until is not None
            and now < result.valid_until
        ):
            self._entries[key] = result.model_copy(
                update={"cache_status": GatewayCacheStatus.MISS}
            )

    def clear(self) -> None:
        """Invalidate every process-local entry."""
        self._entries.clear()
