"""Canonical snapshot identity, serialization, and secret hygiene."""

import hashlib
import json
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from pydantic import ValidationError

from tiaf.baseline import DeterministicBaselineRequest

from .errors import SnapshotIntegrityError
from .models import EvidenceSnapshot, SnapshotContextReference

_FORBIDDEN_KEY_PARTS = (
    "access_token",
    "account_id",
    "api_key",
    "apikey",
    "authorization",
    "broker_account",
    "client_id",
    "credential",
    "password",
    "secret",
)


def validate_no_secrets(value: object) -> None:
    """Reject obvious credential-bearing keys anywhere in a persisted artifact."""
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                normalized = str(key).casefold().replace("-", "_")
                if any(part in normalized for part in _FORBIDDEN_KEY_PARTS):
                    raise ValueError(f"secret-bearing field is not permitted: {key}")
                pending.append(item)
        elif isinstance(current, (list, tuple)):
            pending.extend(current)


def canonical_json(value: object) -> str:
    """Serialize a JSON-compatible semantic payload with stable keys and separators."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _source_as_of(bundle: object) -> Any:
    results = getattr(bundle, "results", ())
    return min((item.as_of for item in results), default=None)


def context_references(
    request: DeterministicBaselineRequest,
) -> tuple[SnapshotContextReference, ...]:
    """Project replay-relevant normalized context identities from the evidence request."""
    references = [
        SnapshotContextReference(
            context_id=request.primary_features.context_id,
            role="PRIMARY_FEATURES",
            subject=request.subject,
            interval=request.primary_timeframe,
            created_at=request.primary_features.created_at,
            source_as_of=_source_as_of(request.primary_features),
        )
    ]
    bundles = (
        ("INDICATORS", request.indicators, request.primary_timeframe),
        ("RELATIVE_FEATURES", request.relative_features, request.primary_timeframe),
        ("MULTI_TIMEFRAME_FEATURES", request.multi_timeframe_features, None),
        ("DERIVATIVES_FEATURES", request.derivatives_features, None),
    )
    references.extend(
        SnapshotContextReference(
            context_id=bundle.context_id,
            role=role,
            subject=request.subject,
            interval=interval,
            created_at=bundle.created_at,
            source_as_of=_source_as_of(bundle),
        )
        for role, bundle, interval in bundles
        if bundle is not None
    )
    if request.multi_timeframe_context is not None:
        references.append(
            SnapshotContextReference(
                context_id=request.multi_timeframe_context.context_id,
                role="MULTI_TIMEFRAME_CONTEXT",
                subject=request.subject,
                created_at=request.multi_timeframe_context.created_at,
                source_as_of=min(
                    (
                        item.as_of
                        for item in request.multi_timeframe_context.timeframes
                        if item.as_of is not None
                    ),
                    default=None,
                ),
            )
        )
    return tuple(sorted(references, key=lambda item: (item.role, item.context_id)))


def _semantic_payload(
    request: DeterministicBaselineRequest,
    *,
    policy_id: str,
    producer_id: str,
    producer_version: str,
    benchmark_symbol: str | None,
    context_references: tuple[SnapshotContextReference, ...],
    fingerprint_schema_version: str,
) -> dict[str, object]:
    return {
        "fingerprint_schema_version": fingerprint_schema_version,
        "producer_id": producer_id,
        "producer_version": producer_version,
        "policy_id": policy_id,
        "policy_version": request.policy_version,
        "benchmark_symbol": benchmark_symbol,
        "context_references": [
            item.model_dump(mode="json")
            for item in sorted(context_references, key=lambda item: (item.role, item.context_id))
        ],
        "decision_request": request.model_dump(mode="json"),
    }


def semantic_fingerprint(
    request: DeterministicBaselineRequest,
    *,
    policy_id: str,
    producer_id: str,
    producer_version: str,
    benchmark_symbol: str | None,
    context_references: tuple[SnapshotContextReference, ...],
    fingerprint_schema_version: str = "1.0",
) -> str:
    """Hash only semantic evidence; exclude archive creation time and metadata."""
    payload = _semantic_payload(
        request,
        policy_id=policy_id,
        producer_id=producer_id,
        producer_version=producer_version,
        benchmark_symbol=benchmark_symbol,
        context_references=context_references,
        fingerprint_schema_version=fingerprint_schema_version,
    )
    validate_no_secrets(payload)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def expected_snapshot_id(fingerprint: str) -> str:
    """Return a stable snapshot ID derived only from its semantic fingerprint."""
    return str(uuid5(NAMESPACE_URL, f"tiaf:evidence-snapshot:{fingerprint}"))


def create_evidence_snapshot(
    request: DeterministicBaselineRequest,
    *,
    policy_id: str,
    producer_version: str,
    snapshot_created_at: Any,
    benchmark_symbol: str | None = None,
    producer_id: str = "tiaf.baseline",
    metadata: dict[str, Any] | None = None,
) -> EvidenceSnapshot:
    """Freeze actual normalized evidence without fetching or recalculating it."""
    references = context_references(request)
    fingerprint = semantic_fingerprint(
        request,
        policy_id=policy_id,
        producer_id=producer_id,
        producer_version=producer_version,
        benchmark_symbol=benchmark_symbol,
        context_references=references,
    )
    return EvidenceSnapshot(
        snapshot_id=expected_snapshot_id(fingerprint),
        fingerprint=fingerprint,
        producer_id=producer_id,
        producer_version=producer_version,
        subject=request.subject,
        benchmark_symbol=benchmark_symbol,
        trade_style=request.trade_style,
        horizon=request.horizon,
        requested_timeframes=(request.primary_timeframe, *request.supporting_timeframes),
        policy_id=policy_id,
        policy_version=request.policy_version,
        decision_time=request.requested_at,
        snapshot_created_at=snapshot_created_at,
        context_references=references,
        decision_request=request,
        metadata=metadata or {},
    )


def snapshot_json(snapshot: EvidenceSnapshot, *, indent: int | None = 2) -> str:
    """Return deterministic JSON with canonical field ordering and timestamps."""
    validate_no_secrets(snapshot.model_dump(mode="json"))
    return json.dumps(
        snapshot.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        indent=indent,
        ensure_ascii=False,
    )


def load_snapshot_json(value: str) -> EvidenceSnapshot:
    """Deserialize and integrity-check one snapshot."""
    try:
        raw = json.loads(value)
        validate_no_secrets(raw)
        return EvidenceSnapshot.model_validate(raw)
    except (ValueError, TypeError, ValidationError) as exc:
        raise SnapshotIntegrityError(str(exc)) from exc
