"""Yahoo/yfinance secondary provider behind the provider-neutral MI boundary."""

import hashlib
import json
import math
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, time
from time import monotonic
from typing import Protocol, cast

from pydantic import JsonValue

from tiaf.contracts import DataQuality, FreshnessState
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.events import (
    EntityKind,
    EntityMappingStatus,
    EventEntity,
    EventFamily,
    EventMateriality,
    EventNovelty,
    EventRelevance,
    EventSource,
    EventSourceClass,
    EventStatus,
    EventType,
    NormalizedEvent,
    StructuredEventFact,
    StructuredFactKind,
)

from ..enums import (
    AvailabilityBasis,
    CapabilitySupport,
    DerivationClass,
    EvidenceOutputType,
    MarketIntelligenceCapability,
    PointInTimeQuality,
    ProviderFailureKind,
    ProviderResultStatus,
    SemanticMappingQuality,
    SourceAuthority,
)
from ..models import (
    MarketIntelligenceRequest,
    NormalizedEvidenceBatch,
    ProviderCapabilityConstraints,
    ProviderCapabilityDeclaration,
    ProviderFailure,
    ProviderFetchResult,
    ProviderIdentity,
    ProviderManifest,
    ProviderNativeObservation,
)
from ..normalization import RuleBasedNormalizer, SemanticRule


class YahooToolClient(Protocol):
    """Small injection seam; MCP SDK types remain in the connector module."""

    def call_tool(
        self, tool_name: str, arguments: Mapping[str, JsonValue]
    ) -> Mapping[str, object]: ...


@dataclass(frozen=True, slots=True)
class YahooSymbolMapper:
    """Explicit canonical-to-Yahoo ticker mapping; no search or suffix guessing."""

    mappings: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        canonical = tuple(item[0].strip().upper() for item in self.mappings)
        yahoo = tuple(item[1].strip().upper() for item in self.mappings)
        if any(not item for item in (*canonical, *yahoo)):
            raise ValueError("Yahoo symbol mappings must be non-empty")
        if len(canonical) != len(set(canonical)):
            raise ValueError("Yahoo canonical symbols must be unique")
        if len(yahoo) != len(set(yahoo)):
            raise ValueError("Yahoo tickers must be unique")
        object.__setattr__(self, "mappings", tuple(zip(canonical, yahoo, strict=True)))

    def resolve(self, canonical_symbol: str) -> str | None:
        requested = canonical_symbol.strip().upper()
        return next(
            (yahoo for canonical, yahoo in self.mappings if canonical == requested),
            None,
        )


def india_yahoo_symbol_mapper() -> YahooSymbolMapper:
    """Return only the India symbols explicitly validated for this integration."""
    return YahooSymbolMapper(
        (
            ("RELIANCE", "RELIANCE.NS"),
            ("HDFCBANK", "HDFCBANK.NS"),
            ("KAYNES", "KAYNES.NS"),
            ("ATHERENERG", "ATHERENERG.NS"),
        )
    )


_TOOL_FOR_CAPABILITY = {
    MarketIntelligenceCapability.READ_COMPANY_PROFILE: "yfinance_get_stock_info",
    MarketIntelligenceCapability.READ_COMPANY_IDENTITY: "yfinance_get_stock_info",
    MarketIntelligenceCapability.READ_FINANCIALS: "yfinance_get_stock_financials",
    MarketIntelligenceCapability.READ_VALUATION_CONTEXT: "yfinance_get_stock_info",
    MarketIntelligenceCapability.READ_EARNINGS_CALENDAR: "yfinance_get_earnings_dates",
    MarketIntelligenceCapability.READ_NEWS: "yfinance_get_stock_news",
    MarketIntelligenceCapability.READ_ANALYST_FORECASTS: (
        "yfinance_get_stock_recommendations"
    ),
}


def _constraints_for(
    capability: MarketIntelligenceCapability,
) -> ProviderCapabilityConstraints:
    supports_periods = capability is MarketIntelligenceCapability.READ_FINANCIALS
    return ProviderCapabilityConstraints(
        supported_markets=("INDIA",),
        supported_exchanges=("NSE",),
        supported_instrument_types=("EQUITY",),
        supported_periods=(("quarterly", "annual") if supports_periods else ()),
        output_types=(EvidenceOutputType.SECONDARY_STRUCTURED,),
        source_authority=SourceAuthority.AGGREGATOR,
        point_in_time_quality=PointInTimeQuality.LIMITED,
        maximum_records=50,
        cost_units_per_call=0,
        rate_limit_description="unofficial Yahoo endpoints may rate-limit without notice",
        expected_latency_class="REMOTE_INTERACTIVE",
        normalizer_id="yahoo-conservative",
        normalizer_version="1.0",
        native_schema_version="yfinance-mcp-0.1.0",
        revision_limitations=(
            "historical statements may reflect later Yahoo/yfinance revisions",
        ),
        limitations=(
            "unofficial endpoint behavior and coverage may vary",
            "not an authoritative Indian filing source",
            "financial publication time is not supplied",
        ),
    )


def _yahoo_manifest(identity: ProviderIdentity) -> ProviderManifest:
    supported = tuple(
        ProviderCapabilityDeclaration(
            capability=capability,
            support=(
                CapabilitySupport.FULL
                if capability
                in {
                    MarketIntelligenceCapability.READ_COMPANY_PROFILE,
                    MarketIntelligenceCapability.READ_COMPANY_IDENTITY,
                    MarketIntelligenceCapability.READ_NEWS,
                }
                else CapabilitySupport.PARTIAL
            ),
            constraints=_constraints_for(capability),
        )
        for capability in _TOOL_FOR_CAPABILITY
    )
    unsupported = tuple(
        ProviderCapabilityDeclaration(
            capability=capability,
            support=CapabilitySupport.UNSUPPORTED,
            notes=("not implemented by the bounded Yahoo secondary adapter",),
        )
        for capability in MarketIntelligenceCapability
        if capability not in _TOOL_FOR_CAPABILITY
    )
    return ProviderManifest(
        identity=identity,
        source_authority=SourceAuthority.AGGREGATOR,
        capabilities=(*supported, *unsupported),
        metadata={
            "provider_role": "SECONDARY_FALLBACK",
            "upstream": "Yahoo Finance via yfinance MCP",
            "allowlisted_tools": cast(JsonValue, sorted(set(_TOOL_FOR_CAPABILITY.values()))),
        },
    )


class YahooMarketIntelligenceProvider:
    """Bounded Yahoo provider for profile, financial, earnings, and news evidence."""

    def __init__(
        self,
        client: YahooToolClient,
        symbol_mapper: YahooSymbolMapper | None = None,
        *,
        wall_clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._client = client
        self._symbol_mapper = symbol_mapper or india_yahoo_symbol_mapper()
        self._wall_clock = wall_clock or (lambda: datetime.now(TIAF_TIMEZONE))
        self._identity = ProviderIdentity(
            provider_id="yahoo",
            display_name="Yahoo Finance via yfinance MCP",
            adapter_version="1.0",
        )
        self._manifest = _yahoo_manifest(self._identity)

    @property
    def identity(self) -> ProviderIdentity:
        return self._identity

    @property
    def manifest(self) -> ProviderManifest:
        return self._manifest

    def fetch(self, request: MarketIntelligenceRequest) -> ProviderFetchResult:
        tool_name = _TOOL_FOR_CAPABILITY.get(request.capability)
        if tool_name is None:
            return self._failure(request, ProviderFailureKind.UNSUPPORTED_CAPABILITY, False)
        yahoo_ticker = self._symbol_mapper.resolve(request.subject)
        if yahoo_ticker is None:
            return self._failure(
                request,
                ProviderFailureKind.UNKNOWN_SYMBOL,
                False,
                message=f"No explicit Yahoo ticker mapping for {request.subject}",
            )
        acquired_at = self._acquired_at()
        arguments = _arguments_for(request, yahoo_ticker, tool_name)
        started = monotonic()
        try:
            response = self._client.call_tool(tool_name, arguments)
            payload = _unwrap_payload(response)
            error = _provider_error(response, payload)
            if error is not None:
                if _is_valid_empty_response(request.capability, error):
                    return self._empty_result(request, monotonic() - started)
                kind, retryable = _classify_error(error)
                return self._failure(
                    request,
                    kind,
                    retryable,
                    elapsed_seconds=monotonic() - started,
                    message=error,
                    metadata={"yahoo_ticker": yahoo_ticker, "provider_tool": tool_name},
                )
            observations, _missing_paths = _observations_for(
                request=request,
                tool_name=tool_name,
                yahoo_ticker=yahoo_ticker,
                payload=payload,
                acquired_at=acquired_at,
            )
            visible = tuple(item for item in observations if item.available_from <= request.as_of)
            if not visible:
                return self._empty_result(request, monotonic() - started)
            status = (
                ProviderResultStatus.SUCCESS
                if len(visible) == len(observations)
                else ProviderResultStatus.PARTIAL
            )
            return ProviderFetchResult(
                provider_id=self.identity.provider_id,
                capability=request.capability,
                status=status,
                observations=visible,
                elapsed_seconds=monotonic() - started,
            )
        except TimeoutError:
            return self._failure(
                request,
                ProviderFailureKind.TIMEOUT,
                True,
                elapsed_seconds=monotonic() - started,
            )
        except (TypeError, ValueError, json.JSONDecodeError):
            return self._failure(
                request,
                ProviderFailureKind.MALFORMED_PAYLOAD,
                False,
                elapsed_seconds=monotonic() - started,
            )
        except Exception:
            return self._failure(
                request,
                ProviderFailureKind.PROVIDER_UNAVAILABLE,
                True,
                elapsed_seconds=monotonic() - started,
            )

    def _acquired_at(self) -> datetime:
        acquired = self._wall_clock()
        if acquired.tzinfo is None or acquired.utcoffset() is None:
            raise ValueError("Yahoo provider wall clock must be timezone-aware")
        return acquired.astimezone(TIAF_TIMEZONE)

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
            ProviderFailureKind.UNKNOWN_SYMBOL: ProviderResultStatus.OUT_OF_COVERAGE,
            ProviderFailureKind.OUT_OF_COVERAGE: ProviderResultStatus.OUT_OF_COVERAGE,
            ProviderFailureKind.RATE_LIMIT: ProviderResultStatus.RATE_LIMITED,
            ProviderFailureKind.TIMEOUT: ProviderResultStatus.TIMEOUT,
            ProviderFailureKind.MALFORMED_PAYLOAD: ProviderResultStatus.INVALID_OUTPUT,
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
                    message=message or f"Yahoo {request.capability} failed: {kind}",
                    retryable=retryable,
                    metadata=metadata or {},
                ),
            ),
            elapsed_seconds=elapsed_seconds,
        )

    def _empty_result(
        self,
        request: MarketIntelligenceRequest,
        elapsed_seconds: float,
    ) -> ProviderFetchResult:
        return ProviderFetchResult(
            provider_id=self.identity.provider_id,
            capability=request.capability,
            status=ProviderResultStatus.PARTIAL,
            elapsed_seconds=elapsed_seconds,
        )


def _arguments_for(
    request: MarketIntelligenceRequest,
    yahoo_ticker: str,
    tool_name: str,
) -> dict[str, JsonValue]:
    arguments: dict[str, JsonValue] = {
        "ticker": yahoo_ticker,
        "response_format": "json",
    }
    if tool_name == "yfinance_get_stock_financials":
        statement = request.attributes.get("statement_type", "income")
        period = request.attributes.get("period", "quarterly")
        limit = request.attributes.get("limit", 4)
        if isinstance(statement, str) and statement in {"income", "balance", "cashflow"}:
            arguments["statement_type"] = statement
        if isinstance(period, str) and period in {"quarterly", "annual"}:
            arguments["period"] = period
        if isinstance(limit, int) and not isinstance(limit, bool) and 1 <= limit <= 20:
            arguments["limit"] = limit
    elif tool_name == "yfinance_get_earnings_dates":
        limit = request.attributes.get("limit", 12)
        future_only = request.attributes.get("future_only", False)
        if isinstance(limit, int) and not isinstance(limit, bool) and 1 <= limit <= 24:
            arguments["limit"] = limit
        if isinstance(future_only, bool):
            arguments["future_only"] = future_only
    elif tool_name == "yfinance_get_stock_news":
        limit = request.attributes.get("limit", 10)
        if isinstance(limit, int) and not isinstance(limit, bool) and 1 <= limit <= 50:
            arguments["limit"] = limit
    elif tool_name == "yfinance_get_stock_recommendations":
        limit = request.attributes.get("limit", 20)
        if isinstance(limit, int) and not isinstance(limit, bool) and 1 <= limit <= 50:
            arguments["limit"] = limit
    return arguments


def _unwrap_payload(response: Mapping[str, object]) -> Mapping[str, object] | list[object]:
    structured = response.get("structuredContent")
    if isinstance(structured, (Mapping, list)):
        decoded = _decode_fastmcp_result(structured)
        if decoded is not None:
            return decoded
    content = response.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, Mapping) and isinstance(block.get("text"), str):
                parsed = json.loads(block["text"])
                if isinstance(parsed, (dict, list)):
                    return parsed
    raise ValueError("Yahoo response has no JSON payload")


def _decode_fastmcp_result(
    value: Mapping[str, object] | list[object],
) -> Mapping[str, object] | list[object] | None:
    if isinstance(value, Mapping) and set(value) == {"result"}:
        wrapped = value.get("result")
        if not isinstance(wrapped, str):
            return None
        parsed = json.loads(wrapped)
        return parsed if isinstance(parsed, (dict, list)) else None
    return value


def _provider_error(
    response: Mapping[str, object], payload: Mapping[str, object] | list[object]
) -> str | None:
    error = payload.get("error") if isinstance(payload, Mapping) else None
    if isinstance(error, str):
        return _safe_error_message(error)
    if response.get("isError") is True:
        return "Yahoo MCP returned an unstructured provider error"
    return None


def _safe_error_message(message: str) -> str:
    redacted = re.sub(
        r"(?i)((?:api[_-]?key|token|password)\s*[:=]\s*)[^\s,;]+",
        r"\1[REDACTED]",
        message,
    )
    redacted = re.sub(
        r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+",
        r"\1[REDACTED]",
        redacted,
    )
    return redacted[:2000]


def _is_valid_empty_response(
    capability: MarketIntelligenceCapability, message: str
) -> bool:
    normalized = message.casefold()
    markers = {
        MarketIntelligenceCapability.READ_ANALYST_FORECASTS: (
            "no recommendations found",
        ),
        MarketIntelligenceCapability.READ_FINANCIALS: (
            "no income statement data found",
            "no balance sheet data found",
            "no cash flow statement data found",
            "no financial data found",
        ),
        MarketIntelligenceCapability.READ_NEWS: ("no news found",),
        MarketIntelligenceCapability.READ_EARNINGS_CALENDAR: (
            "no earnings dates found",
            "no future earnings dates found",
        ),
    }
    return any(marker in normalized for marker in markers.get(capability, ()))


def _classify_error(message: str) -> tuple[ProviderFailureKind, bool]:
    normalized = message.casefold()
    if "rate limit" in normalized or "too many requests" in normalized:
        return ProviderFailureKind.RATE_LIMIT, True
    if any(
        marker in normalized
        for marker in ("out of coverage", "unknown symbol", "symbol not found")
    ):
        return ProviderFailureKind.OUT_OF_COVERAGE, False
    if "invalid" in normalized:
        return ProviderFailureKind.MALFORMED_PAYLOAD, False
    if "unauthorized" in normalized or "forbidden" in normalized:
        return ProviderFailureKind.UNAUTHORIZED, False
    if "failed to fetch" in normalized or "service unavailable" in normalized:
        return ProviderFailureKind.PROVIDER_UNAVAILABLE, True
    return ProviderFailureKind.UNKNOWN, False


def _observations_for(
    *,
    request: MarketIntelligenceRequest,
    tool_name: str,
    yahoo_ticker: str,
    payload: Mapping[str, object] | list[object],
    acquired_at: datetime,
) -> tuple[tuple[ProviderNativeObservation, ...], tuple[str, ...]]:
    if not isinstance(payload, Mapping):
        raise ValueError("Yahoo payload must be an object")
    if tool_name == "yfinance_get_stock_financials":
        leaves = _financial_leaves(payload)
    elif tool_name == "yfinance_get_stock_news":
        leaves = _record_leaves(payload, "news")
    elif tool_name == "yfinance_get_earnings_dates":
        leaves = _earnings_leaves(payload)
    elif tool_name == "yfinance_get_stock_recommendations":
        leaves = _record_leaves(payload, "recommendations")
    else:
        leaves = tuple((key, value, None) for key, value in payload.items())
    observations: list[ProviderNativeObservation] = []
    missing: list[str] = []
    for path, value, record_key in leaves:
        if _missing_value(value):
            missing.append(path)
            continue
        if not isinstance(value, (str, int, float, bool)):
            continue
        observation = _observation(
            request=request,
            tool_name=tool_name,
            yahoo_ticker=yahoo_ticker,
            path=path,
            value=value,
            record_key=record_key,
            payload=payload,
            acquired_at=acquired_at,
        )
        observations.append(observation)
    return tuple(observations), tuple(missing)


def _financial_leaves(
    payload: Mapping[str, object],
) -> tuple[tuple[str, object, str | None], ...]:
    data = payload.get("data")
    if not isinstance(data, Mapping):
        return ()
    leaves: list[tuple[str, object, str | None]] = []
    for period, record in data.items():
        if not isinstance(record, Mapping):
            continue
        for field, value in record.items():
            leaves.append((f"data.{period}.{field}", value, str(period)))
    return tuple(leaves)


def _record_leaves(
    payload: Mapping[str, object], key: str
) -> tuple[tuple[str, object, str | None], ...]:
    records = payload.get(key)
    if records is None:
        return ()
    if not isinstance(records, list):
        raise ValueError(f"Yahoo {key} must be a list")
    leaves: list[tuple[str, object, str | None]] = []
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            continue
        record_key = _record_key(key, index, record)
        for field, value in record.items():
            leaves.append((f"{key}[{index}].{field}", value, record_key))
    return tuple(leaves)


def _earnings_leaves(
    payload: Mapping[str, object],
) -> tuple[tuple[str, object, str | None], ...]:
    leaves = list(_record_leaves(payload, "earnings_history"))
    next_date = payload.get("next_earnings_date")
    if not _missing_value(next_date) and isinstance(next_date, str):
        leaves.append(
            (
                "next_earnings_date",
                next_date,
                f"earnings_history:{next_date}",
            )
        )
    return tuple(leaves)


def _record_key(key: str, index: int, record: Mapping[object, object]) -> str:
    identity = next(
        (
            str(record[name])
            for name in ("link", "date", "published", "id")
            if name in record and not _missing_value(record[name])
        ),
        str(index),
    )
    return f"{key}:{identity}"


def _missing_value(value: object) -> bool:
    return (
        value is None
        or (isinstance(value, str) and value.strip().upper() == "N/A")
        or (isinstance(value, float) and not math.isfinite(value))
    )


def _observation(
    *,
    request: MarketIntelligenceRequest,
    tool_name: str,
    yahoo_ticker: str,
    path: str,
    value: str | int | float | bool,
    record_key: str | None,
    payload: Mapping[str, object],
    acquired_at: datetime,
) -> ProviderNativeObservation:
    field = path.rsplit(".", 1)[-1]
    period = record_key if path.startswith("data.") else None
    published = _publication_for(path, payload)
    if published is not None and published > acquired_at:
        published = None
    available_from = published or acquired_at
    source_reference = _source_reference(tool_name, yahoo_ticker, path, payload)
    payload_checksum = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()
    observation_id = hashlib.sha256(
        json.dumps(
            [yahoo_ticker, tool_name, path, value, acquired_at.isoformat()],
            separators=(",", ":"),
            default=str,
        ).encode()
    ).hexdigest()
    metadata: dict[str, JsonValue] = {
        "yahoo_ticker": yahoo_ticker,
        "native_path": path,
    }
    if record_key is not None:
        metadata["record_key"] = record_key
    statement = payload.get("statement_type")
    period_type = payload.get("period_type")
    if isinstance(statement, str):
        metadata["statement_type"] = statement
    if isinstance(period_type, str):
        metadata["period_type"] = period_type
    return ProviderNativeObservation(
        observation_id=observation_id,
        provider_id="yahoo",
        provider_tool=tool_name,
        provider_endpoint="stdio:yfinance-mcp",
        native_record_id=record_key,
        native_schema_version="yfinance-mcp-0.1.0",
        capability=request.capability,
        subject=request.subject,
        native_field=field,
        native_label=field,
        value=value,
        currency=_currency_for(field, payload),
        period_label=period,
        native_semantics="Yahoo/yfinance provider-native field",
        observed_at=(acquired_at if field in {"current_price", "market_cap"} else None),
        published_at=published,
        available_from=available_from,
        acquired_at=acquired_at,
        availability_basis=(
            AvailabilityBasis.EXACT_PUBLICATION_TIME
            if published is not None
            else AvailabilityBasis.ACQUISITION_TIME
        ),
        point_in_time_quality=(
            PointInTimeQuality.CONSERVATIVE
            if published is not None
            else PointInTimeQuality.LIMITED
        ),
        point_in_time_limitation=(
            None
            if published is not None
            else "provider publication time absent; available only from acquisition"
        ),
        source_reference=source_reference,
        source_quality=DataQuality.PARTIAL,
        payload_checksum=payload_checksum,
        output_type=EvidenceOutputType.SECONDARY_STRUCTURED,
        derivation_class=(
            DerivationClass.PROVIDER_DERIVED
            if field in {"pe_ratio", "forward_pe", "surprise_percent"}
            else DerivationClass.REPORTED
        ),
        metadata=metadata,
    )


def _publication_for(path: str, payload: Mapping[str, object]) -> datetime | None:
    if not path.startswith("news["):
        return None
    index_text = path.split("[", 1)[1].split("]", 1)[0]
    if not index_text.isdigit():
        return None
    records = payload.get("news")
    if not isinstance(records, list) or int(index_text) >= len(records):
        return None
    record = records[int(index_text)]
    if not isinstance(record, Mapping) or not isinstance(record.get("published"), str):
        return None
    return _parse_aware_timestamp(record["published"])


def _currency_for(field: str, payload: Mapping[str, object]) -> str | None:
    if field not in {"current_price", "market_cap"}:
        return None
    currency = payload.get("currency")
    return currency if isinstance(currency, str) and currency.strip() else None


def _parse_aware_timestamp(value: str) -> datetime | None:
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(TIAF_TIMEZONE)


def _source_reference(
    tool_name: str,
    yahoo_ticker: str,
    path: str,
    payload: Mapping[str, object],
) -> str:
    if path.startswith("news["):
        index_text = path.split("[", 1)[1].split("]", 1)[0]
        records = payload.get("news")
        if isinstance(records, list) and index_text.isdigit() and int(index_text) < len(records):
            record = records[int(index_text)]
            link = record.get("link") if isinstance(record, Mapping) else None
            if isinstance(link, str):
                if link.strip().upper() != "N/A":
                    return link
    if tool_name == "yfinance_get_earnings_dates":
        return f"https://finance.yahoo.com/calendar/earnings?symbol={yahoo_ticker}"
    suffix = "financials" if tool_name == "yfinance_get_stock_financials" else ""
    return f"https://finance.yahoo.com/quote/{yahoo_ticker}/{suffix}"


class YahooNormalizer:
    """Conservative Yahoo mappings plus provider-neutral news/earnings events."""

    def __init__(self) -> None:
        self._base = RuleBasedNormalizer(
            "yahoo",
            (
                SemanticRule(
                    "name",
                    "company.name",
                    SemanticMappingQuality.EXACT,
                    rule_id="yahoo-company-name",
                    requires_period=False,
                ),
                SemanticRule(
                    "currency",
                    "market.currency",
                    SemanticMappingQuality.EXACT,
                    rule_id="yahoo-currency",
                    requires_period=False,
                ),
                SemanticRule(
                    "current_price",
                    "market.last_price",
                    SemanticMappingQuality.WELL_SUPPORTED,
                    rule_id="yahoo-current-price",
                    requires_period=False,
                ),
                SemanticRule(
                    "market_cap",
                    "valuation.market_cap",
                    SemanticMappingQuality.WELL_SUPPORTED,
                    rule_id="yahoo-market-cap",
                    requires_period=False,
                ),
                SemanticRule(
                    "pe_ratio",
                    "valuation.trailing_pe",
                    SemanticMappingQuality.WELL_SUPPORTED,
                    rule_id="yahoo-trailing-pe",
                    derivation_class=DerivationClass.PROVIDER_DERIVED,
                    requires_period=False,
                ),
                SemanticRule(
                    "sector",
                    "company.sector",
                    SemanticMappingQuality.WELL_SUPPORTED,
                    rule_id="yahoo-sector",
                    requires_period=False,
                ),
                SemanticRule(
                    "industry",
                    "company.industry",
                    SemanticMappingQuality.WELL_SUPPORTED,
                    rule_id="yahoo-industry",
                    requires_period=False,
                ),
                SemanticRule(
                    "description",
                    "company.description",
                    SemanticMappingQuality.WELL_SUPPORTED,
                    rule_id="yahoo-company-description",
                    requires_period=False,
                ),
                SemanticRule(
                    "Total Revenue",
                    "fundamental.revenue",
                    SemanticMappingQuality.WELL_SUPPORTED,
                    rule_id="yahoo-total-revenue",
                ),
                SemanticRule(
                    "Net Income",
                    "fundamental.net_income",
                    SemanticMappingQuality.WELL_SUPPORTED,
                    rule_id="yahoo-net-income",
                ),
                SemanticRule(
                    "forward_pe",
                    None,
                    SemanticMappingQuality.PROVIDER_DEFINED,
                    rule_id="yahoo-forward-pe-native-only",
                    derivation_class=DerivationClass.PROVIDER_DERIVED,
                    requires_period=False,
                ),
            ),
        )

    @property
    def provider_id(self) -> str:
        return "yahoo"

    def normalize(
        self,
        request: MarketIntelligenceRequest,
        result: ProviderFetchResult,
    ) -> NormalizedEvidenceBatch:
        batch = self._base.normalize(request, result)
        events = (
            _normalized_events(request, result)
            if request.capability
            in {
                MarketIntelligenceCapability.READ_NEWS,
                MarketIntelligenceCapability.READ_EARNINGS_CALENDAR,
            }
            else ()
        )
        return batch.model_copy(update={"normalized_events": events})


def yahoo_normalizer() -> YahooNormalizer:
    return YahooNormalizer()


def _normalized_events(
    request: MarketIntelligenceRequest,
    result: ProviderFetchResult,
) -> tuple[NormalizedEvent, ...]:
    groups: dict[str, list[ProviderNativeObservation]] = {}
    for observation in result.observations:
        record_key = observation.metadata.get("record_key")
        if isinstance(record_key, str):
            groups.setdefault(record_key, []).append(observation)
    events: list[NormalizedEvent] = []
    for record_key in sorted(groups):
        observations = groups[record_key]
        by_field = {item.native_field: item for item in observations}
        event = (
            _news_event(request, record_key, by_field)
            if request.capability is MarketIntelligenceCapability.READ_NEWS
            else _earnings_event(request, record_key, by_field)
        )
        if event is not None:
            events.append(event)
    return tuple(events)


def _news_event(
    request: MarketIntelligenceRequest,
    record_key: str,
    fields: Mapping[str, ProviderNativeObservation],
) -> NormalizedEvent | None:
    title = _text_value(fields.get("title"))
    publisher = _text_value(fields.get("publisher"))
    link = _text_value(fields.get("link"))
    if title is None or publisher is None or link is None:
        return None
    anchor = fields["title"]
    publication = anchor.published_at or anchor.acquired_at
    description = _text_value(fields.get("description"))
    identity = _digest("news", link, publication.isoformat(), title)
    underlying = _digest(
        request.subject,
        title.casefold(),
        publication.date().isoformat(),
    )
    return NormalizedEvent(
        event_id=f"yahoo:news:{identity}",
        family=EventFamily.OTHER,
        event_type=EventType.OTHER,
        primary_entity=_entity(request.subject),
        source=EventSource(
            source_id=f"yahoo:news-source:{identity}",
            source_class=EventSourceClass.OTHER,
            publisher=publisher,
            provider_id="yahoo",
            source_reference=link,
            document_id=identity,
        ),
        publication_time=publication,
        acquisition_time=anchor.acquired_at,
        normalized_title=title[:500],
        content_reference=link,
        bounded_excerpt=(description[:1000] if description else None),
        relevance=EventRelevance.DIRECT,
        materiality=EventMateriality.UNKNOWN,
        novelty=EventNovelty.UNKNOWN,
        status=EventStatus.UNKNOWN,
        quality=DataQuality.PARTIAL,
        freshness=FreshnessState.UNKNOWN,
        underlying_event_key=f"news:{underlying}",
        metadata={
            "yahoo_ticker": anchor.metadata["yahoo_ticker"],
            "provider_tool": anchor.provider_tool or "unknown",
            "sentiment_available": False,
            "publication_time_basis": (
                "provider" if anchor.published_at is not None else "acquisition_time"
            ),
            "record_key": record_key,
        },
    )


def _earnings_event(
    request: MarketIntelligenceRequest,
    record_key: str,
    fields: Mapping[str, ProviderNativeObservation],
) -> NormalizedEvent | None:
    anchor = fields.get("date")
    if anchor is None:
        anchor = fields.get("next_earnings_date")
    date_text = _text_value(anchor)
    if date_text is None or anchor is None:
        return None
    try:
        event_date = date.fromisoformat(date_text)
    except ValueError:
        return None
    event_time = datetime.combine(event_date, time.max, tzinfo=TIAF_TIMEZONE)
    reported = _number_value(fields.get("eps_reported"))
    estimate = _number_value(fields.get("eps_estimate"))
    surprise = _number_value(fields.get("surprise_percent"))
    is_reported = reported is not None and event_time <= anchor.acquired_at
    facts = [
        StructuredEventFact(
            field_id="earnings.date",
            kind=StructuredFactKind.DATE,
            value=event_date.isoformat(),
        )
    ]
    for field_id, value, unit in (
        ("earnings.eps_estimate", estimate, "EPS"),
        ("earnings.eps_reported", reported, "EPS"),
        ("earnings.surprise_percent", surprise, "PERCENT"),
    ):
        if value is not None:
            facts.append(
                StructuredEventFact(
                    field_id=field_id,
                    kind=StructuredFactKind.NUMBER,
                    value=value,
                    unit=unit,
                )
            )
    identity = _digest(request.subject, event_date.isoformat(), "earnings")
    reference = anchor.source_reference
    if reference is None:
        return None
    return NormalizedEvent(
        event_id=f"yahoo:earnings:{identity}",
        family=EventFamily.CORPORATE_RESULTS,
        event_type=(EventType.RESULTS_REPORTED if is_reported else EventType.OTHER),
        primary_entity=_entity(request.subject),
        source=EventSource(
            source_id=f"yahoo:earnings-source:{identity}",
            source_class=EventSourceClass.OTHER,
            publisher="Yahoo Finance via yfinance",
            provider_id="yahoo",
            source_reference=reference,
            document_id=identity,
        ),
        publication_time=anchor.acquired_at,
        event_time=event_time,
        acquisition_time=anchor.acquired_at,
        normalized_title=(
            f"Earnings reported for {request.subject}"
            if is_reported
            else f"Earnings scheduled for {request.subject}"
        ),
        structured_facts=tuple(facts),
        relevance=EventRelevance.DIRECT,
        materiality=EventMateriality.UNKNOWN,
        novelty=EventNovelty.UNKNOWN,
        status=(EventStatus.COMPLETED if is_reported else EventStatus.ANNOUNCED),
        quality=DataQuality.PARTIAL,
        freshness=FreshnessState.UNKNOWN,
        underlying_event_key=f"{request.subject}:EARNINGS:{event_date.isoformat()}",
        metadata={
            "yahoo_ticker": anchor.metadata["yahoo_ticker"],
            "provider_tool": anchor.provider_tool or "unknown",
            "publication_time_basis": "acquisition_time",
            "record_key": record_key,
        },
    )


def _entity(symbol: str) -> EventEntity:
    return EventEntity(
        entity_id=f"NSE:{symbol}",
        kind=EntityKind.COMPANY,
        name=symbol,
        canonical_symbol=symbol,
        mapping_status=EntityMappingStatus.EXACT,
    )


def _text_value(observation: ProviderNativeObservation | None) -> str | None:
    if observation is None or not isinstance(observation.value, str):
        return None
    return observation.value


def _number_value(observation: ProviderNativeObservation | None) -> float | None:
    if observation is None or isinstance(observation.value, (bool, str)):
        return None
    return float(observation.value)


def _digest(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()
