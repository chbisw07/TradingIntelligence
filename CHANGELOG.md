# Changelog

All notable changes to this project will be documented here.

## Unreleased — TIAF_A1.4

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
