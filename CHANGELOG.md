# Changelog

All notable changes to this project will be documented here.

## Unreleased — TIAF_A1.2

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
