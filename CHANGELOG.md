# Changelog

All notable changes to this project will be documented here.

## Unreleased

- Added 15 TIAF_A2.6 completed-history prior-boundary, signed-distance,
  close/wick excursion, prior-range geometry, compression, and latest-range
  comparison features with strict current-bar exclusion.
- Added shared anti-lookahead range helpers, ATR/range reuse, a `--levels`
  read-only smoke pack, numerical/provenance safeguards, regression tests, and
  detailed placement/deferral documentation.
- Added 17 TIAF_A2.5 completed-history raw, relative, dispersion, slope,
  persistence, close-transition participation, signed-balance, and transparent
  price/range correlation features.
- Added strict exact-window and destination-volume alignment semantics,
  zero-denominator/variance guards, inherited history quality and market-time
  provenance, a `--volume` read-only smoke pack, tests, and architecture docs.
- Added the first-class TIAF_A2.4 indicator contracts, explicit registry, and
  indicator-agnostic deterministic engine.
- Added completed-history SuperTrend, Wilder RSI, MACD, Wilder ADX/+DI/-DI,
  population Bollinger Bands, and Donchian Channel calculations with a
  dedicated read-only smoke CLI.
- Added indicator architecture documentation, extension guidance, revised A2
  numbering, and a platform capability-placement map; HalfTrend is explicitly
  deferred pending selection of a stable canonical variant.
- Added 23 TIAF_A2.3 completed-history moving-average, regression,
  directional-efficiency, persistence, adjacent-structure, rolling-range, and
  ATR-normalized extension measurements.
- Added strict A2.3 window/warm-up semantics, shared pure calculations,
  inherited history quality, latest-bar market timestamps, numerical guards,
  a `--trend` smoke view, and architecture documentation.
- Preserved safe provider/operation diagnostics for failed AnalysisContext
  evidence and exposed them in the read-only context smoke without leaking
  credentials or untyped exception details.
- Corrected Dhan REST quote `previous_close` normalization to derive it from
  `last_price - net_change`; raw OHLC close remains diagnostic metadata rather
  than being mislabeled as the prior-session close.
- Corrected A2.2 previous-close semantics after live validation: normalized
  quote `previous_close` is canonical, with a session-aware daily-history
  fallback shared by price change and move/ATR calculations.
- Clarified that `price.open`, `price.high`, `price.low`, and day-range position
  use current-session quote facts rather than latest historical-bar OHLC.
- Added 23 TIAF_A2.2 price-location, log-return, candle-range, Wilder ATR,
  realized-volatility, rolling-extrema, drawdown/run-up, and signed move/ATR
  measurements to the deterministic feature registry.
- Added strict exact-window and numerical-safety behavior, worst-source quality
  propagation, and explicit market-time versus acquisition-time provenance.
- Extended the read-only feature smoke with `--extended` and explicit intraday
  annualization, plus deterministic A2.2 tests and architecture documentation.
- Added the TIAF_A2.1 provider-neutral immutable feature contracts, explicit
  calculator registry, deterministic context-only engine, and factual bundle
  summary.
- Added seven small baseline price/history/return/range features with exact
  lookback, insufficient-data, source-quality, timestamp, and provenance
  semantics.
- Added a read-only A1-to-A2 feature smoke utility, focused test coverage, and
  the A2.1 architecture/handoff record.
- Added the canonical A1 architectural baseline and engineering acceptance
  report, and closed milestone/roadmap status for the A2 handoff.

## TIAF_A1.7 — Complete / Live Validated

- Added immutable, provider-neutral AnalysisContext requirements, subjects,
  evidence descriptors, aggregate context, ordered batch outcomes, and factual
  diagnostic summaries.
- Added a dependency-injected builder that resolves through A1.5 and routes
  quote, history, option-chain, and exact historical-option requests through
  the A1.6 coordinator.
- Added deterministic completeness, quality, retrieval freshness,
  partial/failure, and dual retrieval/source-observation provenance semantics.
- Hardened the read-only utility with explicit required-versus-optional
  derivatives and sequential, order-preserving batch inspection.
- Preserved A1.6 provider-scheduler blocks as typed A1.7 deferrals with gate
  provenance, partial-context retention, truthful `UNKNOWN` required freshness,
  and explicit completed/partial/deferred/error batch statuses.

## TIAF_A1.6 — Complete / Live Validated

- Added a provider-neutral in-process factual cache with deterministic keys,
  optional LRU capacity, explicit invalidation, generation tracking, and local
  metrics.
- Added caller-relative freshness requirements and an explicit operation policy
  registry without universal TTL assumptions.
- Added a monotonic, non-sleeping provider scheduler with explicit rate blocks,
  cooldowns, provider disable/enable controls, and documented Dhan quote and
  option-chain policies.
- Added synchronous fetch coordination, key-scoped single flight, explicit
  bounded stale-on-error behavior, immutable acquisition results, tests, and a
  read-only Dhan quote demo.

## TIAF_A1.5 — Complete / Live Validated

- Added frozen provider-neutral instrument query, resolved identity, and
  explicit unique/ambiguous/not-found result contracts behind a synchronous
  resolver protocol and provider registry.
- Added header-driven Dhan detailed instrument-master ingestion with a narrow
  local file cache, absent/explicit-refresh downloads, atomic replacement,
  typed schema failures, and indexed exact lookup.
- Added exact provider-ID/trading-symbol lookup, filtered equity/index/future/
  option resolution, inactive-record visibility, order-preserving batches, a
  deterministic eligible F&O-underlying universe, tests, and read-only smoke.
- Added configurable primary cash/F&O exchange policy after live validation
  exposed legitimate NSE/BSE symbol duplication. Policy-selected results are
  explicit, query scope always overrides policy, and F&O universes are unique
  within their configured exchange scope.
- Hardened all Dhan factual smoke utilities with symbol-first master resolution
  and mandatory symbol/security-ID consistency before provider transport.
- Excluded Dhan `DUMMYSAN` diagnostic underlyings from canonical F&O universes
  using provider identity metadata rather than broad symbol substring matching.

## TIAF_A1.4 — Accepted / Live Validated

- Added frozen provider-neutral rolling historical-option bars, series,
  expiry context, and ATM-relative strike types behind a segregated protocol.
- Added Dhan expired-options requests with complete factual arrays, half-open
  30-day chunking, deterministic merging, and typed malformed-data handling.
- Corrected the rolling expired-options endpoint to its live-validated dedicated
  expiry-code mapping: `1` near, `2` next, and `3` far; `0` is rejected.
- Added mocked tests, a read-only smoke utility, and the detailed evolving TIAF
  implementation-target map.

## TIAF_A1.3 — Accepted / Live Validated

- Added provider-neutral immutable expiry, option-chain, strike, contract, and
  Greeks snapshots behind a segregated derivatives provider protocol.
- Extended the Dhan adapter with active-expiry discovery and complete live
  option-chain normalization, including contract IDs, spot, prices, depth, OI,
  volume, IV, Greeks, provenance, and typed failures.
- Added deterministic mocked coverage and an explicit-expiry read-only smoke
  utility.

## TIAF_A1.2 — Accepted / Live Validated

- Added a secret-safe, read-only DhanHQ v2 adapter using an injectable HTTPX
  transport.
- Added normalized full quotes, ordered 1,000-instrument batch chunking, daily
  and supported intraday OHLCV, explicit mappings, and typed error translation.
- Added mocked transport/provider tests and an optional one-quote smoke script.

## TIAF_A1.1 — Complete / Frozen

- Added provider-neutral market-data enums, normalized models, provider
  protocol, typed failures, and deterministic normalization/freshness helpers.
- Added A1.1 model, serialization, protocol, validation, and public-export tests.

## TIAF_A0 — Complete / Frozen

- Added immutable, versioned Pydantic domain contracts for requests, evidence,
  opinions, assessments, horizons, snapshots, and option expressions.
- Added contract validation, serialization, and public-export tests.
- Established `Asia/Kolkata` as the canonical timezone for contract timestamps.
- Made finalized semantic contract collections immutable tuples while retaining
  JSON-array and Python-list input compatibility.

## 0.1.0 - 2026-09-05

- Established the initial `TIAF_TGT0` repository baseline.
- Added packaging, configuration, documentation, namespace scaffolding, and
  smoke tests.
