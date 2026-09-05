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
spellings to `1m`, `5m`, `15m`, `25m`, `1h`, and `1d`. Unknown non-empty labels are
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
`HISTORICAL_OPTIONS`, `MARKET_DEPTH`, `FUNDAMENTALS`, and `NEWS`. An adapter must raise
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

## A1.2 — Dhan core market-data adapter

Dhan is the first concrete factual provider because it supplies the project's
required batched quotes and daily/intraday OHLCV behind explicit security IDs.
The A1.2 adapter implements only `QUOTES` and `HISTORICAL_OHLCV`; instrument
master and resolver work remains deferred. Credentials come from
`DHAN_CLIENT_ID` and `DHAN_ACCESS_TOKEN`, and the adapter never logs or exposes
the token.

The adapter uses Dhan's full quote endpoint, preserves ordered all-success batch
semantics, and chunks requests at the documented 1,000-instrument boundary. It
does not sleep or enforce the documented one-quote-request-per-second policy;
call scheduling belongs to the future Data Service. Historical support covers
daily bars and Dhan's `1`, `5`, `15`, `25`, and `60` minute intervals. Intraday
ranges over Dhan's documented 90-day per-request maximum fail explicitly
instead of being silently changed or automatically rate-limited.

An explicit `provider_instrument_id` is required as Dhan `securityId`.
Index-versus-stock derivative terminology cannot be inferred safely from A1.1
identity alone, so derivative historical requests require injected
`FUTIDX`/`FUTSTK` or `OPTIDX`/`OPTSTK` mapping. A1.6 will own full resolution.

See [the Dhan adapter design](TIAF_A1_2_DHAN_CORE_ADAPTER.md) for endpoint,
mapping, security, testing, and smoke-test details.

## A1.3 — Dhan derivatives-data extension

Dhan expiry discovery and complete live option chains now cross a separate
`DerivativesDataProvider` boundary into frozen provider-neutral models. The
adapter preserves contract security IDs, spot LTP, CE/PE prices, top-of-book,
volume/OI current and previous values, IV, and provider-reported Greeks. It does
not calculate, rank, recommend, select contracts, or schedule provider calls.

Successful provider results must contain data. Normalized unavailable models
can represent an explicitly unavailable chain/list, but malformed or empty Dhan
success responses raise `ProviderBadResponseError`. Chain strikes and expiry
dates are immutable tuples, while JSON uses ordinary arrays.

Dhan does not return a chain timestamp, so acquisition time is both observed
and received time. It remains aware and canonicalized to `Asia/Kolkata`.
See [the A1.3 design](TIAF_A1_3_DHAN_DERIVATIVES.md).

## A1.4 — Dhan historical / expired options

Rolling expired-option facts now cross a separate
`HistoricalOptionsDataProvider` boundary. `HistoricalOptionSeries` preserves
the underlying, CE/PE side, weekly/monthly cadence, relative expiry, ATM-relative
strike, interval, request range, quality, acquisition time, and immutable bars.

Dhan requests use only the underlying security ID. All documented factual
arrays are requested and length-validated before indexing. Half-open ranges are
split into adjacent requests of at most 30 days, then sorted and deduplicated by
timestamp without hidden sleeps. IV remains in provider units and epochs become
aware `Asia/Kolkata` timestamps.

See [the A1.4 design](TIAF_A1_4_DHAN_HISTORICAL_OPTIONS.md) and the
[detailed continuation map](TIAF_IMPLEMENTATION_TARGETS.md).

## Planned A1 steps

- **A1.2:** Dhan core adapter (complete and live-validated)
- **A1.3:** Dhan derivatives-data extension (complete and live-validated)
- **A1.4:** Dhan historical/expired options (current)
- **A1.5:** Zerodha secondary/fallback provider
- **A1.6:** instrument resolver
- **A1.7:** cache, freshness, and provider scheduling
- **A1.8:** `AnalysisContext` builder
- **A1.9:** fallback and partial-data semantics
- **A1.10:** news, filings, and external-evidence foundation
- **A1.11:** fundamentals and macro evidence foundation
