# Changelog

All notable changes to this project will be documented here.

## Unreleased — TIAF_A1.5

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
