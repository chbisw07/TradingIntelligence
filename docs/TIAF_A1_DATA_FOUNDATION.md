# TIAF_A1 Data Foundation

## A1.1 purpose

TIAF_A1.1 defines the provider-neutral factual market-data boundary that future
adapters must implement. It establishes normalized instrument identity, quotes,
OHLCV series, instrument records, provider capabilities, typed failures, and
pure normalization helpers. It does not connect to a live provider.

The package version remains `0.1.0`, while these versioned models use contract
schema version `1.0`; package and wire-schema versions remain independent.

## Architecture

```text
Future provider adapters
        |
        v
MarketDataProvider protocol
        |
        v
Normalized A1 market models
        |
        v
Future shared Data Service / AnalysisContext
```

Provider-native response dictionaries stop at the future adapter boundary.
Downstream components receive only validated normalized models. A future shared
Data Service will acquire facts once and distribute a consistent context.
Agents must never call providers directly: direct access would duplicate calls,
create inconsistent snapshots, leak provider details, and bypass shared
freshness and failure handling.

## Normalized models

- `InstrumentKey` identifies an equity, index, future, or CE/PE option without
  prescribing an exchange's symbol syntax.
- `QuoteSnapshot` holds normalized quote fields, attribution, receipt time,
  freshness, quality, and field availability.
- `OHLCVBar` validates one interval's time and price envelope.
- `HistoricalSeries` holds chronological immutable bars for one instrument and
  interval.
- `InstrumentRecord` represents normalized instrument-master information.

All models are frozen at the attribute level and reject unknown fields. Bars
are stored as tuples, while Python lists and JSON arrays remain accepted inputs
and JSON serialization continues to emit arrays. Metadata is JSON-compatible
extension space, not a location for raw provider payloads or secrets.

An empty `HistoricalSeries` is valid only when quality is `UNAVAILABLE` or
`PARTIAL`; `GOOD` and `DEGRADED` series must contain at least one bar.

## Timestamp and freshness policy

All datetime inputs must be timezone-aware. UTC and other aware zones are
accepted and normalized using `ZoneInfo("Asia/Kolkata")`, the canonical TIAF
timezone. JSON output therefore uses ISO-8601 timestamps with the `+05:30`
offset. No model or helper calls a naive `datetime.now()`.

`age_seconds` compares explicit aware timestamps. `classify_freshness` accepts
`fresh_for` and `aging_for` thresholds from its caller and returns `FRESH`,
`AGING`, or `STALE`; A1.1 contains no market-specific TTL policy. Quote receipt
validation permits normal clock skew but rejects an observation more than 24
hours ahead of its receipt as structurally implausible. This sanity bound is
not a freshness TTL.

## Interval normalization

The normalizer maps a deliberately small group of common minute, hour, and day
spellings to `1m`, `5m`, `15m`, `1h`, and `1d`. Unknown non-empty labels are
trimmed and case-normalized rather than assigned invented semantics. Numeric
uppercase-`M` forms such as `1M` are rejected because they are ambiguous between
minutes and months; a future adapter must disambiguate them explicitly.

## Provider capability model

`MarketDataProvider` is a synchronous, runtime-checkable protocol with:

- `provider_name()` and `capabilities()`
- `get_quote()` and first-class ordered `get_quotes()`
- `get_historical()`
- `search_instruments()`

Capabilities are advertised as an immutable `frozenset` of `QUOTES`,
`HISTORICAL_OHLCV`, `INSTRUMENT_MASTER`, `DERIVATIVES_METADATA`, `OPTION_CHAIN`,
`MARKET_DEPTH`, `FUNDAMENTALS`, and `NEWS`. An adapter must raise
`UnsupportedCapabilityError` instead of fabricating success for an unsupported
operation. Partial batch-result semantics are intentionally deferred.

## Error model

`TIAFDataError` is the base, with `ProviderError` beneath it and typed subclasses
for authentication, rate limiting, timeout, network, bad response, instrument
not found, unsupported capability, stale data, and unusable partial data.
Errors carry normalized provider attribution, a stable `DataFailureKind`, a
retryable flag, detail, and extensible metadata. `to_dict()` produces a
log-friendly representation without requiring a logging framework.

## Non-goals

A1.1 includes no live adapter, credentials, network call, broker/order behavior,
market-data fetch, cache, persistence, fallback orchestration, agent, LLM,
LangGraph workflow, ranking, signal, trade action, Google Sheet integration, or
`AnalysisContext` construction.

## Planned A1 steps

- **A1.2:** Dhan adapter
- **A1.3:** Zerodha adapter
- **A1.4:** instrument resolver
- **A1.5:** cache and caller-configured freshness policy
- **A1.6:** `AnalysisContext` builder
- **A1.7:** fallback and partial-data semantics
