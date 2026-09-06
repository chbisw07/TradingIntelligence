# TIAF Detailed Implementation Targets

This document is the detailed, evolving engineering continuation map beneath
the stable project roadmap. Status must describe repository reality.

- `MILESTONES.md` is the concise status view.
- `TRADINGINTELLIGENCE_ROADMAP.md` is the canonical major roadmap.
- `TIAF_IMPLEMENTATION_TARGETS.md` is the detailed evolving engineering
  continuation map.

## Accepted foundation

### TIAF_A1 — Complete / Baselined

TIAF_A1.1 through TIAF_A1.7 form the accepted Data Foundation at baseline tag
`tiaf-a1-baseline`. The canonical contract and evidence record are
[`TIAF_A1_FOUNDATION_BASELINE.md`](TIAF_A1_FOUNDATION_BASELINE.md) and
[`TIAF_A1_ACCEPTANCE_REPORT.md`](TIAF_A1_ACCEPTANCE_REPORT.md).

### TIAF_TGT0 — Complete / Frozen

- Purpose: establish the Python repository, package layout, configuration,
  documentation, and quality tooling.
- Acceptance: importable baseline with passing compile, test, lint, type, and
  diff checks.
- Tag: `tiaf-tgt0`.

### TIAF_A0 — Complete / Frozen

- Purpose: establish immutable versioned domain contracts, shared enums,
  identifiers, evidence and assessment language, and Asia/Kolkata time policy.
- Acceptance: strict validated contracts with JSON round trips and immutable
  semantic collections.
- Tag: `tiaf-a0`.

### TIAF_A1.1 — Complete

- Purpose: provider-neutral instrument, quote, OHLCV, historical-series,
  capability, normalization, and typed-error contracts.
- Acceptance: adapters can satisfy stable factual interfaces without leaking
  provider payloads.
- Tag: `tiaf-a1.1`.

### TIAF_A1.2 — Complete / Live Validated

- Purpose: direct read-only Dhan transport, full quotes, and daily/intraday
  historical OHLCV.
- Acceptance: deterministic mocked coverage plus successful live data
  validation with safe credentials.
- Tag: `tiaf-a1.2`.

### TIAF_A1.3 — Complete / Live Validated

- Purpose: Dhan active-expiry discovery and normalized complete live option
  chains with prices, depth, OI, volume, IV, and provider Greeks.
- Acceptance: provider-neutral immutable chains pass mocked validation and the
  read-only adapter is live-validated.
- Tag: `tiaf-a1.3`.

### TIAF_A1.4 — Complete / Live Validated

- Purpose: provider-neutral rolling historical/expired-option data without
  expired contract IDs.
- Scope: Dhan rolling expiry and ATM-relative requests, complete factual arrays,
  endpoint-specific live-validated expiry codes (`1/2/3`), 30-day chunking,
  safe merging, typed failures, tests, and read-only smoke.
- Non-goals: replay engines, option choice, strategies, Agents, and execution.
- Dependency: accepted A1.1 contracts and A1.2 transport/mappings.
- Acceptance concept: long half-open date ranges become validated chronological
  historical-option series with no boundary gaps or silent array truncation.
- Live semantics note: older/general Dhan annexure values may show `0/1/2`, but
  the rolling expired-options endpoint is live-validated as `1/2/3`; A1.4 uses
  a dedicated type and does not change other expiry-code consumers.

### TIAF_A1.5 — Complete / Live Validated

- Purpose: resolve human-facing instrument inputs to explicit canonical and
  provider identities without guessing.
- Scope: frozen provider-neutral query/results, Dhan detailed-master ingestion,
  narrow local file caching, exact indexed matching, ambiguity visibility,
  configurable primary-exchange policy, inactive-ID inspection, batch
  resolution, symbol/ID integrity guards for diagnostics, and exchange-scoped
  unique eligible F&O underlyings excluding provider diagnostic identities.
- Non-goals: fuzzy preferences, nearest-contract choice, recommendations,
  Agents, orders, accounts, execution, and spreadsheet integration.
- Dependency: accepted A1 identity contracts and Dhan's public master source.
- Acceptance concept: representative equity, index, future, and exact option
  inputs resolve uniquely or return explicit policy-selected,
  ambiguous/not-found outcomes without first-row guessing.

### TIAF_A1.6 — Complete / Live Validated

- Purpose: centralize reusable data acquisition and rate-aware coordination.
- Scope: deterministic immutable keys, in-memory optional-LRU caching,
  caller-visible freshness/age, operation policy registry, monotonic endpoint
  scheduling, provider disable/cooldown controls, key-scoped request
  coalescing, explicit bounded stale fallback, invalidation, and metrics.
- Non-goals: Agent judgment, recommendation caching, or hidden adapter sleeps.
- Dependency: stable provider operations and normalized snapshot identities.
- Acceptance concept: repeated workloads reuse factual results while freshness,
  expiry, and provider rate constraints stay visible and deterministic.

### TIAF_A1.7 — Complete / Live Validated

- Purpose: assemble a timestamp-consistent provider-neutral factual context for
  downstream deterministic and Agent consumers.
- Scope: explicit requirements, canonical subject, A1.6-coordinated quote,
  history, option-chain, and bounded historical-option retrieval, evidence
  requirement roles, separate retrieval/source-observation provenance,
  deterministic quality/retrieval-freshness/completeness, ordered batch
  outcomes with explicit scheduler deferral, and factual summaries.
- Non-goals: indicators, scoring, recommendations, prompts, Agents, queues,
  TradeMonitor, broker/account access, or execution authority.
- Dependency: accepted A1.5 resolution, A1.6 runtime, and normalized A1 facts.
- Acceptance concept: a symbol or watchlist yields coherent immutable contexts
  or explicit partial/deferred/error outcomes without conflating provider gate
  blocks with factual unavailability or retrieval freshness with source-
  observation age. A1.7 does not schedule retries for deferred work.

## Current target

### TIAF_A2 — Deterministic Analysis / Feature Foundation — Current

- Purpose: consume `AnalysisContext` and compute reproducible, non-AI derived
  features without bypassing A1 identity, acquisition, quality, freshness, or
  provenance boundaries.
- Dependency: the accepted `tiaf-a1-baseline` Data Foundation baseline.

### TIAF_A2.1 — Feature Contracts + Engine Foundation — Current

- Purpose: establish immutable feature definitions, requests, results and
  bundles; an explicit calculator registry; and deterministic context-only
  orchestration.
- Scope: seven small baseline measurements proving exact windows, source
  quality/provenance inheritance, insufficient-data behavior, deterministic
  summaries, and a read-only A1-to-A2 smoke path.
- Non-goals: an indicator library, scoring, ranking, market direction,
  recommendations, Agents, brokers, or execution.
- Detail: [`TIAF_A2_1_FEATURE_FOUNDATION.md`](TIAF_A2_1_FEATURE_FOUNDATION.md).

## Near-term A2 sequence

1. **A2.1 — Feature Contracts + Engine Foundation** — Current
2. **A2.2 — Price / Return / Volatility Features**
3. **A2.3 — Trend & Structure Features**
4. **A2.4 — Volume / Participation Features**
5. **A2.5 — Support / Resistance / Breakout Structure**
6. **A2.6 — Derivatives / Option-Chain Features**
7. **A2.7 — Multi-Timeframe Feature Context**
8. **A2.8 — Deterministic Market-State / Feature Summary**
9. **A2.9 — Replay / Validation / Baseline Evaluation**

Provider fallback/Zerodha, persistent caching, deferred-work orchestration,
provider health, and external news/fundamental evidence remain intentionally
deferred. They are not unimplemented promises inside the accepted A1 baseline;
their eventual milestone placement will be decided when scoped.

Major phases A2 through A10 remain defined by the canonical
`TRADINGINTELLIGENCE_ROADMAP.md`; this continuation map does not replace it.
