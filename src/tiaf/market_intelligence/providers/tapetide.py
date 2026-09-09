"""Read-only Tapetide adapter isolated behind a tiny injected transport protocol."""

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time
from time import monotonic
from typing import Protocol, cast

from pydantic import JsonValue

from tiaf.contracts import DataQuality
from tiaf.contracts.common import TIAF_TIMEZONE

from ..enums import (
    AvailabilityBasis,
    CapabilitySupport,
    DerivationClass,
    EvidenceOutputType,
    MarketIntelligenceCapability,
    PointInTimeQuality,
    ProviderFailureKind,
    ProviderResultStatus,
    SourceAuthority,
)
from ..models import (
    MarketIntelligenceRequest,
    ProviderCapabilityConstraints,
    ProviderCapabilityDeclaration,
    ProviderFailure,
    ProviderFetchResult,
    ProviderIdentity,
    ProviderManifest,
    ProviderNativeObservation,
)


class TapetideToolClient(Protocol):
    """Injection seam for an installed MCP/app client; no SDK dependency in TIAF."""

    def call_tool(
        self, tool_name: str, arguments: Mapping[str, JsonValue]
    ) -> Mapping[str, object]: ...


@dataclass(frozen=True, slots=True)
class _ClassifiedProviderFailure:
    kind: ProviderFailureKind
    retryable: bool
    message: str
    metadata: dict[str, JsonValue]


_TOOL_FOR_CAPABILITY: dict[MarketIntelligenceCapability, tuple[str, Mapping[str, JsonValue]]] = {
    MarketIntelligenceCapability.READ_COMPANY_PROFILE: ("get_company_profile", {}),
    MarketIntelligenceCapability.READ_COMPANY_IDENTITY: ("get_company_profile", {}),
    MarketIntelligenceCapability.READ_FINANCIALS: ("get_financials", {"section": "profit_loss"}),
    MarketIntelligenceCapability.READ_POINT_IN_TIME_FINANCIALS: (
        "get_financials",
        {"section": "profit_loss"},
    ),
    MarketIntelligenceCapability.READ_FINANCIAL_RATIOS: ("get_financials", {"section": "ratios"}),
    MarketIntelligenceCapability.READ_VALUATION_CONTEXT: ("get_financials", {"section": "ratios"}),
    MarketIntelligenceCapability.READ_SHAREHOLDING: (
        "get_shareholding",
        {"type": "quarterly"},
    ),
    MarketIntelligenceCapability.READ_PROMOTER_PLEDGE: ("get_promoter_pledge", {}),
    MarketIntelligenceCapability.READ_CREDIT_RATINGS: ("get_credit_ratings", {}),
    MarketIntelligenceCapability.READ_ANALYST_FORECASTS: ("get_forecasts", {}),
    MarketIntelligenceCapability.READ_FILINGS: ("get_stock_events", {"type": "filings"}),
    MarketIntelligenceCapability.READ_NEWS: ("get_stock_events", {"type": "news"}),
    MarketIntelligenceCapability.READ_EARNINGS_CALL_CONTEXT: (
        "get_earnings_call_summary",
        {},
    ),
    MarketIntelligenceCapability.READ_MANAGEMENT_EVIDENCE: (
        "get_earnings_call_summary",
        {},
    ),
    MarketIntelligenceCapability.READ_INDEX_MEMBERSHIP_ASOF: (
        "get_index_membership_asof",
        {},
    ),
}


def _tapetide_manifest(identity: ProviderIdentity) -> ProviderManifest:
    supported = tuple(
        ProviderCapabilityDeclaration(
            capability=capability,
            support=(
                CapabilitySupport.PARTIAL
                if capability
                in {
                    MarketIntelligenceCapability.READ_POINT_IN_TIME_FINANCIALS,
                    MarketIntelligenceCapability.READ_MANAGEMENT_EVIDENCE,
                    MarketIntelligenceCapability.READ_FINANCIALS,
                    MarketIntelligenceCapability.READ_INDEX_MEMBERSHIP_ASOF,
                }
                else CapabilitySupport.FULL
            ),
            constraints=_constraints_for(capability),
        )
        for capability in _TOOL_FOR_CAPABILITY
    )
    unsupported = tuple(
        ProviderCapabilityDeclaration(
            capability=capability,
            support=CapabilitySupport.UNSUPPORTED,
            notes=("no Phase-1 validated read tool for this capability",),
        )
        for capability in MarketIntelligenceCapability
        if capability not in _TOOL_FOR_CAPABILITY
    )
    return ProviderManifest(
        identity=identity,
        source_authority=SourceAuthority.AGGREGATOR,
        capabilities=(*supported, *unsupported),
        metadata={
            "validated_read_tools": cast(
                JsonValue,
                sorted({item[0] for item in _TOOL_FOR_CAPABILITY.values()}),
            )
        },
    )


def _constraints_for(
    capability: MarketIntelligenceCapability,
) -> ProviderCapabilityConstraints:
    interpreted = capability in {
        MarketIntelligenceCapability.READ_EARNINGS_CALL_CONTEXT,
        MarketIntelligenceCapability.READ_MANAGEMENT_EVIDENCE,
    }
    return ProviderCapabilityConstraints(
        supports_historical_as_of=capability
        in {
            MarketIntelligenceCapability.READ_FINANCIALS,
            MarketIntelligenceCapability.READ_POINT_IN_TIME_FINANCIALS,
            MarketIntelligenceCapability.READ_INDEX_MEMBERSHIP_ASOF,
        },
        output_types=(
            EvidenceOutputType.INTERPRETED_AI
            if interpreted
            else EvidenceOutputType.SECONDARY_STRUCTURED,
        ),
        source_authority=SourceAuthority.AGGREGATOR,
        point_in_time_quality=PointInTimeQuality.CONSERVATIVE,
        maximum_records=100,
        cost_units_per_call=1,
        rate_limit_description="externally enforced by Tapetide transport",
        expected_latency_class="REMOTE_INTERACTIVE",
        normalizer_id="tapetide-conservative",
        normalizer_version="1.0",
        native_schema_version="phase1-live-validated",
        revision_limitations=("historical values may reflect later restatements",),
        limitations=(
            "publication time may be date-only or absent",
            "native financial labels require conservative semantic mapping",
            "index-membership historical coverage may be limited",
        ),
    )


class TapetideMarketIntelligenceProvider:
    """A bounded adapter for Phase-1 validated Tapetide read operations only."""

    def __init__(self, client: TapetideToolClient) -> None:
        self._client = client
        self._identity = ProviderIdentity(
            provider_id="tapetide",
            display_name="Tapetide",
            adapter_version="1.0",
        )
        self._manifest = _tapetide_manifest(self._identity)

    @property
    def identity(self) -> ProviderIdentity:
        return self._identity

    @property
    def manifest(self) -> ProviderManifest:
        return self._manifest

    def fetch(self, request: MarketIntelligenceRequest) -> ProviderFetchResult:
        selection = _TOOL_FOR_CAPABILITY.get(request.capability)
        if selection is None:
            return self._failure(request, ProviderFailureKind.UNSUPPORTED_CAPABILITY, False)
        tool_name, defaults = selection
        arguments: dict[str, JsonValue] = {"symbol": request.subject, **defaults}
        if tool_name == "get_financials":
            section = request.attributes.get("section")
            if isinstance(section, str) and section in {
                "profit_loss",
                "balance_sheet",
                "cash_flow",
                "ratios",
            }:
                arguments["section"] = section
        if tool_name == "get_stock_events":
            limit = request.attributes.get("limit", 20)
            if isinstance(limit, int) and not isinstance(limit, bool) and 1 <= limit <= 100:
                arguments["limit"] = limit
        if tool_name == "get_index_membership_asof":
            arguments["date"] = request.as_of.date().isoformat()
        acquired_at = datetime.now(TIAF_TIMEZONE)
        call_started = monotonic()
        try:
            response = self._client.call_tool(tool_name, arguments)
            classified_failure = _classify_provider_failure(response, acquired_at)
            if classified_failure is not None:
                return self._failure(
                    request,
                    classified_failure.kind,
                    classified_failure.retryable,
                    elapsed_seconds=monotonic() - call_started,
                    message=classified_failure.message,
                    metadata=classified_failure.metadata,
                )
            payload = _unwrap_payload(response)
            observations = tuple(
                _observation_from_leaf(
                    request=request,
                    path=path,
                    value=value,
                    payload=payload,
                    acquired_at=acquired_at,
                )
                for path, value in _scalar_leaves(payload)
                if not _is_auxiliary_path(path)
            )
            if not observations:
                return self._failure(
                    request,
                    ProviderFailureKind.MALFORMED_PAYLOAD,
                    False,
                    elapsed_seconds=monotonic() - call_started,
                )
            visible = tuple(item for item in observations if item.available_from <= request.as_of)
            if not visible:
                return self._failure(
                    request,
                    ProviderFailureKind.OUT_OF_COVERAGE,
                    False,
                    elapsed_seconds=monotonic() - call_started,
                )
            stale = _find_bool(payload, "stale") is True
            null_failures = tuple(
                ProviderFailure(
                    kind=ProviderFailureKind.OUT_OF_COVERAGE,
                    provider_id=self.identity.provider_id,
                    capability=request.capability,
                    message=f"Tapetide returned no value for native field: {path}",
                    metadata={"native_path": path},
                )
                for path in _null_leaves(payload)
                if not _is_auxiliary_path(path)
            )
            status = (
                ProviderResultStatus.SUCCESS
                if len(visible) == len(observations) and not stale and not null_failures
                else ProviderResultStatus.PARTIAL
            )
            failures = null_failures + (
                (
                    ProviderFailure(
                        kind=ProviderFailureKind.STALE,
                        provider_id=self.identity.provider_id,
                        capability=request.capability,
                        message="Tapetide explicitly marked the response stale",
                    ),
                )
                if stale
                else ()
            )
            return ProviderFetchResult(
                provider_id=self.identity.provider_id,
                capability=request.capability,
                status=status,
                observations=visible,
                failures=failures,
                cost_units=1,
                elapsed_seconds=monotonic() - call_started,
            )
        except TimeoutError:
            return self._failure(
                request,
                ProviderFailureKind.TIMEOUT,
                True,
                elapsed_seconds=monotonic() - call_started,
            )
        except (TypeError, ValueError, json.JSONDecodeError):
            return self._failure(
                request,
                ProviderFailureKind.MALFORMED_PAYLOAD,
                False,
                elapsed_seconds=monotonic() - call_started,
            )
        except Exception:  # transport implementations vary; expose only a typed boundary failure
            return self._failure(
                request,
                ProviderFailureKind.PROVIDER_UNAVAILABLE,
                True,
                elapsed_seconds=monotonic() - call_started,
            )

    def _failure(
        self,
        request: MarketIntelligenceRequest,
        kind: ProviderFailureKind,
        retryable: bool,
        *,
        elapsed_seconds: float = 0,
        message: str | None = None,
        metadata: dict[str, JsonValue] | None = None,
    ) -> ProviderFetchResult:
        statuses = {
            ProviderFailureKind.UNSUPPORTED_CAPABILITY: ProviderResultStatus.UNSUPPORTED,
            ProviderFailureKind.TIMEOUT: ProviderResultStatus.TIMEOUT,
            ProviderFailureKind.OUT_OF_COVERAGE: ProviderResultStatus.OUT_OF_COVERAGE,
            ProviderFailureKind.MALFORMED_PAYLOAD: ProviderResultStatus.INVALID_OUTPUT,
            ProviderFailureKind.RATE_LIMIT: ProviderResultStatus.RATE_LIMITED,
            ProviderFailureKind.UNKNOWN_SYMBOL: ProviderResultStatus.OUT_OF_COVERAGE,
        }
        return ProviderFetchResult(
            provider_id=self.identity.provider_id,
            capability=request.capability,
            status=statuses.get(kind, ProviderResultStatus.UNAVAILABLE),
            failures=(
                ProviderFailure(
                    kind=kind,
                    provider_id=self.identity.provider_id,
                    capability=request.capability,
                    message=message or f"Tapetide {request.capability} failed: {kind}",
                    retryable=retryable,
                    metadata=metadata or {},
                ),
            ),
            elapsed_seconds=elapsed_seconds,
        )


def _unwrap_payload(response: Mapping[str, object]) -> Mapping[str, object] | list[object]:
    structured = response.get("structuredContent")
    if isinstance(structured, (Mapping, list)):
        return structured
    content = response.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, Mapping) and isinstance(block.get("text"), str):
                parsed = json.loads(block["text"])
                if isinstance(parsed, (dict, list)):
                    return parsed
    return response


def _scalar_leaves(
    value: object, prefix: str = ""
) -> tuple[tuple[str, str | int | float | bool], ...]:
    leaves: list[tuple[str, str | int | float | bool]] = []
    if isinstance(value, Mapping):
        for key in sorted(value, key=str):
            child = f"{prefix}.{key}" if prefix else str(key)
            leaves.extend(_scalar_leaves(value[key], child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = f"{prefix}[{index}]"
            leaves.extend(_scalar_leaves(item, child))
    elif isinstance(value, (str, int, float, bool)) and not (
        isinstance(value, float) and (value != value or abs(value) == float("inf"))
    ):
        leaves.append((prefix, value))
    return tuple(leaves)


def _null_leaves(value: object, prefix: str = "") -> tuple[str, ...]:
    paths: list[str] = []
    if isinstance(value, Mapping):
        for key in sorted(value, key=str):
            child = f"{prefix}.{key}" if prefix else str(key)
            paths.extend(_null_leaves(value[key], child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = f"{prefix}[{index}]"
            paths.extend(_null_leaves(item, child))
    elif value is None:
        paths.append(prefix)
    return tuple(paths)


def _is_auxiliary_path(path: str) -> bool:
    tokens = _path_tokens(path)
    return "availability" in tokens or tokens[-1] in {
        "source_reference",
        "source_url",
        "url",
        "published_at",
        "publication_date",
        "available_from",
        "stale",
        "error",
        "code",
        "message",
    }


def _path_tokens(path: str) -> tuple[str, ...]:
    return tuple(path.replace("[", ".").replace("]", "").split("."))


def _record_context(
    payload: Mapping[str, object] | list[object], path: str
) -> Mapping[str, object] | list[object]:
    current: object = payload
    candidates: list[Mapping[str, object]] = []
    for token in _path_tokens(path)[:-1]:
        if isinstance(current, Mapping):
            current = current.get(token)
        elif isinstance(current, list) and token.isdigit():
            index = int(token)
            current = current[index] if index < len(current) else None
        else:
            break
        if isinstance(current, Mapping):
            candidates.append(current)
    identity_keys = {
        "record_id",
        "id",
        "document_id",
        "source_reference",
        "source_url",
        "url",
        "availability",
        "available_from",
        "published_at",
        "publication_date",
        "date",
    }
    for candidate in reversed(candidates):
        if identity_keys.intersection(candidate):
            return candidate
    return payload


def _field_and_period(path: str) -> tuple[str, str | None]:
    tokens = _path_tokens(path)
    period = _period_from_path(path)
    if period is not None and tokens[-1] == period and len(tokens) >= 2:
        field = tokens[-2]
        if "pct_changes" in tokens:
            field = f"{field} pct_change"
        return field, period
    return tokens[-1], period


def _availability_for_period(value: object, period: str | None) -> str | None:
    if period is None:
        return None
    if isinstance(value, Mapping):
        if value.get("period") == period:
            available = value.get("available_from")
            if isinstance(available, str):
                return available
        for child in value.values():
            found = _availability_for_period(child, period)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _availability_for_period(child, period)
            if found is not None:
                return found
    return None


def _find_publication_outside_availability(
    value: object, names: tuple[str, ...]
) -> str | None:
    if isinstance(value, Mapping):
        for name in names:
            found = value.get(name)
            if isinstance(found, (str, int)) and not isinstance(found, bool):
                return str(found)
        for key, child in value.items():
            if key == "availability":
                continue
            found = _find_publication_outside_availability(child, names)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_publication_outside_availability(child, names)
            if found is not None:
                return found
    return None


def _observation_from_leaf(
    *,
    request: MarketIntelligenceRequest,
    path: str,
    value: str | int | float | bool,
    payload: Mapping[str, object] | list[object],
    acquired_at: datetime,
) -> ProviderNativeObservation:
    label, period_label = _field_and_period(path)
    context = _record_context(payload, path)
    record_id = _find_string(context, ("record_id", "id", "document_id"))
    source_reference = _find_string(
        context, ("source_reference", "source_url", "url")
    )
    if source_reference is None and record_id is not None:
        tool_name = _TOOL_FOR_CAPABILITY[request.capability][0]
        source_reference = f"tapetide:{tool_name}:{record_id}"
    available_text = _availability_for_period(
        context, period_label
    ) or _find_publication_outside_availability(
        context,
        (
            "available_from",
            "published_at",
            "publication_date",
            *(
                ("date",)
                if request.capability
                in {
                    MarketIntelligenceCapability.READ_FILINGS,
                    MarketIntelligenceCapability.READ_NEWS,
                }
                else ()
            ),
        ),
    )
    available_from, basis, pit = _availability(available_text, acquired_at)
    period_label = period_label or _find_string(
        context, ("period", "fiscal_year", "year")
    )
    observation_id = hashlib.sha256(
        f"tapetide|{request.subject}|{request.capability}|{path}|{value}|{available_from.isoformat()}".encode()
    ).hexdigest()
    derived = (
        label.casefold() in {"free cash flow", "fcf", "cagr"}
        or label.casefold().endswith(" pct_change")
    )
    return ProviderNativeObservation(
        observation_id=observation_id,
        provider_id="tapetide",
        adapter_version="1.0",
        provider_tool=_TOOL_FOR_CAPABILITY[request.capability][0],
        native_record_id=record_id,
        native_schema_version="phase1-live-validated",
        capability=request.capability,
        subject=request.subject,
        native_field=label,
        native_label=label,
        value=value,
        unit=_find_string(context, ("unit",)),
        scale=_find_string(context, ("scale",)),
        currency=_find_string(context, ("currency",)),
        period_label=period_label,
        native_semantics=_find_string(context, ("semantics", "definition")),
        published_at=available_from if available_text is not None else None,
        available_from=available_from,
        acquired_at=acquired_at,
        availability_basis=basis,
        point_in_time_quality=pit,
        point_in_time_limitation=(
            "date-only availability conservatively normalized to Asia/Kolkata end-of-day"
            if basis is AvailabilityBasis.ESTIMATED_DATE
            else None
        ),
        source_reference=source_reference,
        source_quality=(
            DataQuality.PARTIAL if source_reference is not None else DataQuality.DEGRADED
        ),
        output_type=EvidenceOutputType.SECONDARY_STRUCTURED,
        derivation_class=(
            DerivationClass.PROVIDER_DERIVED if derived else DerivationClass.REPORTED
        ),
        revision_id=_find_string(context, ("revision_id", "version_id")),
        restatement_semantics=_find_string(context, ("restatement", "revision_note")),
        payload_checksum=hashlib.sha256(
            json.dumps(context, sort_keys=True, default=str).encode()
        ).hexdigest(),
        metadata={"native_path": path},
    )


def _find_string(value: object, names: tuple[str, ...]) -> str | None:
    if isinstance(value, Mapping):
        for name in names:
            found = value.get(name)
            if isinstance(found, (str, int)) and not isinstance(found, bool):
                return str(found)
        for child in value.values():
            found = _find_string(child, names)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_string(child, names)
            if found is not None:
                return found
    return None


def _find_bool(value: object, name: str) -> bool | None:
    if isinstance(value, Mapping):
        found = value.get(name)
        if isinstance(found, bool):
            return found
        for child in value.values():
            nested = _find_bool(child, name)
            if nested is not None:
                return nested
    elif isinstance(value, list):
        for child in value:
            nested = _find_bool(child, name)
            if nested is not None:
                return nested
    return None


def _classify_provider_failure(
    response: Mapping[str, object], acquired_at: datetime
) -> _ClassifiedProviderFailure | None:
    marked_error = response.get("isError") is True
    structured = response.get("structuredContent")
    structured_error = (
        _find_string(structured, ("error", "message", "status", "code"))
        if isinstance(structured, (Mapping, list))
        else None
    )
    text_blocks = _plain_text_blocks(response)
    if not marked_error and structured_error is None and not text_blocks:
        return None
    message = _safe_provider_message(
        "\n".join(
            part for part in (structured_error, *text_blocks) if part is not None
        )
    )
    normalized = message.casefold()
    code = (
        _find_string(structured, ("code",))
        if isinstance(structured, (Mapping, list))
        else None
    )
    rate_limited = (
        "tapetide rate limit reached" in normalized
        or "free tier limit" in normalized
        or ("free plan" in normalized and "tool calls/day" in normalized)
        or (
            "rate limit" in normalized
            and ("request denied" in normalized or "retry in" in normalized)
        )
        or code == "429"
    )
    kind: ProviderFailureKind | None = None
    retryable = False
    if rate_limited:
        kind = ProviderFailureKind.RATE_LIMIT
        retryable = True
    elif any(
        marker in normalized
        for marker in (
            "authentication failed",
            "authorization failed",
            "unauthorized",
            "invalid token",
            "forbidden",
        )
    ) or code in {"401", "403"}:
        kind = ProviderFailureKind.UNAUTHORIZED
    elif "unknown symbol" in normalized or "not found" in normalized or code == "404":
        kind = ProviderFailureKind.UNKNOWN_SYMBOL
    elif "timeout" in normalized or "timed out" in normalized:
        kind = ProviderFailureKind.TIMEOUT
        retryable = True
    elif "out of coverage" in normalized:
        kind = ProviderFailureKind.OUT_OF_COVERAGE
    elif "unsupported" in normalized:
        kind = ProviderFailureKind.UNSUPPORTED_CAPABILITY
    elif "invalid request" in normalized or "bad request" in normalized:
        kind = ProviderFailureKind.MALFORMED_PAYLOAD
    elif any(
        marker in normalized
        for marker in (
            "service unavailable",
            "temporarily unavailable",
            "internal server error",
        )
    ):
        kind = ProviderFailureKind.PROVIDER_UNAVAILABLE
        retryable = True
    elif marked_error or any(
        marker in normalized
        for marker in ("request denied", "provider error", "error:", "failed to")
    ):
        kind = ProviderFailureKind.UNKNOWN
    if kind is None:
        return None

    metadata: dict[str, JsonValue] = {
        "acquired_at": acquired_at.isoformat(),
    }
    retry_match = re.search(r"\bretry\s+in\s+(\d+)\s*s\b", message, re.IGNORECASE)
    if retry_match is not None:
        metadata["retry_after_seconds"] = int(retry_match.group(1))
    reset_match = re.search(
        r"\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+IST\b",
        message,
        re.IGNORECASE,
    )
    if reset_match is not None:
        try:
            reset_at = datetime.strptime(
                reset_match.group(1), "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=TIAF_TIMEZONE)
        except ValueError:
            pass
        else:
            metadata["reset_at"] = reset_at.isoformat()
    if code is not None:
        metadata["provider_code"] = code
    return _ClassifiedProviderFailure(
        kind=kind,
        retryable=retryable,
        message=message or "Tapetide provider returned an error",
        metadata=metadata,
    )


def _plain_text_blocks(response: Mapping[str, object]) -> tuple[str, ...]:
    structured = response.get("structuredContent")
    marked_error = response.get("isError") is True
    content = response.get("content")
    if not isinstance(content, list):
        return ()
    texts: list[str] = []
    for block in content:
        if not isinstance(block, Mapping) or not isinstance(block.get("text"), str):
            continue
        text = block["text"]
        if marked_error or structured is None:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                texts.append(text)
            else:
                if marked_error and not isinstance(parsed, (dict, list)):
                    texts.append(text)
    return tuple(texts)


def _safe_provider_message(message: str) -> str:
    redacted = re.sub(
        r"(?i)(TAPETIDE_TOKEN\s*[:=]\s*)[^\s,;]+",
        r"\1[REDACTED]",
        message,
    )
    redacted = re.sub(
        r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+",
        r"\1[REDACTED]",
        redacted,
    )
    return redacted[:2000]


def _availability(
    raw: str | None, acquired_at: datetime
) -> tuple[datetime, AvailabilityBasis, PointInTimeQuality]:
    if raw is None:
        return acquired_at, AvailabilityBasis.ACQUISITION_TIME, PointInTimeQuality.UNKNOWN
    try:
        parsed = datetime.fromisoformat(raw)
        if parsed.tzinfo is not None and parsed.utcoffset() is not None:
            return (
                parsed.astimezone(TIAF_TIMEZONE),
                AvailabilityBasis.PROVIDER_AVAILABLE_FROM,
                PointInTimeQuality.EXACT,
            )
        parsed_date = parsed.date()
    except ValueError:
        try:
            parsed_date = date.fromisoformat(raw)
        except ValueError:
            return acquired_at, AvailabilityBasis.ACQUISITION_TIME, PointInTimeQuality.UNKNOWN
    conservative = datetime.combine(parsed_date, time.max, tzinfo=TIAF_TIMEZONE)
    return conservative, AvailabilityBasis.ESTIMATED_DATE, PointInTimeQuality.CONSERVATIVE


def _period_from_path(path: str) -> str | None:
    for token in _path_tokens(path):
        if token.isdigit() and 1900 <= int(token) <= 2200:
            return token
        if token.upper().startswith(("FY", "Q")) and any(char.isdigit() for char in token):
            return token.upper()
        if re.fullmatch(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}",
            token,
        ):
            return token
        if token.upper() == "TTM":
            return "TTM"
    return None
