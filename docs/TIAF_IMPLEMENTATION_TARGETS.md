# TIAF Detailed Implementation Targets

This document is the detailed, evolving engineering continuation map beneath
the stable project roadmap. Status must describe repository reality.

- `MILESTONES.md` is the concise status view.
- `TRADINGINTELLIGENCE_ROADMAP.md` is the canonical major roadmap.
- `TIAF_IMPLEMENTATION_TARGETS.md` is the detailed evolving engineering
  continuation map.
- `TIAF_DEFERRAL_REGISTER.md` owns stable deferred-capability IDs and their
  resolution history.

Deferrals are captured when they arise and reviewed at major milestone closure
(A2, A3, A4, and so on), not after each sub-milestone. The closure review must
report introduced, implemented, rejected, superseded, carried-forward, and
remaining high-priority deferrals. See
[`TIAF_DEFERRAL_REGISTER.md`](TIAF_DEFERRAL_REGISTER.md) for the binding policy.

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

### TIAF_A2.1 — Feature Contracts + Engine Foundation — Complete / Live Validated

- Purpose: establish immutable feature definitions, requests, results and
  bundles; an explicit calculator registry; and deterministic context-only
  orchestration.
- Scope: seven small baseline measurements proving exact windows, source
  quality/provenance inheritance, insufficient-data behavior, deterministic
  summaries, and a read-only A1-to-A2 smoke path.
- Non-goals: an indicator library, scoring, ranking, market direction,
  recommendations, Agents, brokers, or execution.
- Detail: [`TIAF_A2_1_FEATURE_FOUNDATION.md`](TIAF_A2_1_FEATURE_FOUNDATION.md).

### TIAF_A2.2 — Price / Return / Volatility Features — Complete / Live Validated

- Purpose: extend the stable A2.1 engine with exact price-location, return,
  candle-range, Wilder ATR, realized-volatility, rolling-extrema, drawdown,
  run-up, and normalized-movement measurements.
- Scope: deterministic exact-window calculations, worst-source quality,
  market-time `as_of`, numerical safety, and an optional extended smoke view.
- Non-goals: trend classification, scoring, ranking, recommendations, Agents,
  brokers, or execution.
- Detail:
  [`TIAF_A2_2_PRICE_RETURN_VOLATILITY.md`](TIAF_A2_2_PRICE_RETURN_VOLATILITY.md).

### TIAF_A2.3 — Trend & Structure Features — Complete / Live Validated

- Purpose: add reusable completed-history moving averages, slope, linearity,
  directional-efficiency, close-persistence, adjacent high/low structure,
  rolling-range location, and ATR-normalized extension measurements.
- Scope: strict windows and warm-ups, shared pure calculations, inherited
  history quality, latest-bar market timestamps, and a read-only trend smoke.
- Non-goals: signals, directional recommendations, subjective swing points,
  scoring, ADX, Agents, brokers, or execution.
- Detail: [`TIAF_A2_3_TREND_STRUCTURE.md`](TIAF_A2_3_TREND_STRUCTURE.md).

### TIAF_A2.4 — Indicator Framework + Initial Indicator Library — Complete / Live Validated

- Purpose: establish indicators as a first-class, versioned, discoverable
  evidence subsystem complementary to primitive A2 features.
- Scope: immutable contracts, explicit registry, indicator-agnostic engine,
  SuperTrend, RSI, MACD, ADX/DI, Bollinger, Donchian, and a dedicated read-only
  smoke path.
- Non-goals: strategy signals, recommendations, parameter optimization,
  HalfTrend guesswork, Agents, brokers, or execution.
- Why inserted: scanners, strategy engines, Agents, replay/backtesting,
  optimization, UI/dashboard consumers, and custom indicators need one stable
  reusable abstraction before later feature families build on them.
- Detail: [`TIAF_A2_4_INDICATOR_FRAMEWORK.md`](TIAF_A2_4_INDICATOR_FRAMEWORK.md).

### TIAF_A2.5 — Volume / Participation Features — Complete / Live Validated

- Purpose: add deterministic completed-history measurements of volume level,
  variation, persistence, and alignment with price movement.
- Scope: raw and relative volume, exact-window dispersion and slope,
  close-transition participation fractions/balance, and transparent Pearson
  alignment primitives.
- Non-goals: accumulation/distribution claims, confirmation signals,
  option-chain OI, session VWAP, OBV-family indicators, Agents, or execution.
- Detail:
  [`TIAF_A2_5_VOLUME_PARTICIPATION.md`](TIAF_A2_5_VOLUME_PARTICIPATION.md).

### TIAF_A2.6 — Support / Resistance / Breakout Structure — Complete / Live Validated

- Purpose: add anti-lookahead measurements of prior price boundaries, current
  completed-bar distance/excursion, prior-range geometry, and range
  compression/expansion.
- Scope: prior rolling high/low excluding the current bar, close and wick
  excursion, unclamped prior-range position, ATR-normalized geometry, and
  strict exact-window comparisons.
- Non-goals: subjective levels, pivot hindsight, breakout confirmation or
  quality, volume confirmation, scoring, recommendations, Agents, or execution.
- Detail:
  [`TIAF_A2_6_SUPPORT_RESISTANCE_BREAKOUT.md`](TIAF_A2_6_SUPPORT_RESISTANCE_BREAKOUT.md).

### TIAF_A2.7 — Derivatives / Option-Chain Features — Complete / Live Validated

- Purpose: derive provider-neutral, deterministic strike geometry, premiums,
  IV, OI, option volume, spreads, Greeks, concentration, and expiry facts from
  one explicit normalized option-chain snapshot.
- Scope: chain-consistent ATM resolution, exact listed-strike windows,
  field-independent missingness, preserved provider IV/Greeks, and option-chain
  quality/time provenance.
- Non-goals: option selection, expected-move or probability models, max pain,
  dealer positioning, strategy templates/ranking, recommendations, or execution.
- Detail:
  [`TIAF_A2_7_DERIVATIVES_OPTION_CHAIN_FEATURES.md`](TIAF_A2_7_DERIVATIVES_OPTION_CHAIN_FEATURES.md).

### TIAF_A2.8 — Relative Strength, Benchmark & Multi-Timeframe Context — Complete / Live Validated

- Purpose: provide explicit-benchmark relative measurements and ordered
  multi-timeframe factual contexts for later deterministic synthesis.
- Scope: exact common-suffix bar alignment, relative return/ATR primitives,
  first-class timeframe bundle references, valid-contributor fractions, and
  weakest-source quality/time provenance.
- Non-goals: benchmark auto-mapping, scoring, ranking, signals,
  recommendations, Agents, strategies, or execution.
- Detail:
  [`TIAF_A2_8_RELATIVE_STRENGTH_MTF.md`](TIAF_A2_8_RELATIVE_STRENGTH_MTF.md).

### TIAF_A2.9 — Deterministic Market-State & Opportunity Baseline — Implemented / Live Validated

- Purpose: preserve a replayable, understandable non-AI benchmark that future
  Agents must beat rather than replace.
- Scope: explicit DAY/POSITIONAL policy 1.0, independent positive/negative
  direction, decomposable component evidence, opportunity/room/maturity and
  alignment scoring, quality/freshness gates, four candidate classes, and
  eligible-only stable ranking.
- Non-goals: LLM/Agent reasoning, provider acquisition inside the baseline,
  option/strategy selection, targets, probability claims, orders, position
  management, or execution.
- Detail:
  [`TIAF_A2_9_DETERMINISTIC_BASELINE.md`](TIAF_A2_9_DETERMINISTIC_BASELINE.md).

## Near-term A2 sequence

1. **A2.1 — Feature Contracts + Engine Foundation** — Complete / Live Validated
2. **A2.2 — Price / Return / Volatility Features** — Complete / Live Validated
3. **A2.3 — Trend & Structure Features** — Complete / Live Validated
4. **A2.4 — Indicator Framework + Initial Indicator Library** — Complete / Live Validated
5. **A2.5 — Volume / Participation Features** — Complete / Live Validated
6. **A2.6 — Support / Resistance / Breakout Structure** — Complete / Live Validated
7. **A2.7 — Derivatives / Option-Chain Features** — Complete / Live Validated
8. **A2.8 — Relative Strength, Benchmark & Multi-Timeframe Context** — Complete / Live Validated
9. **A2.9 — Deterministic Market-State / Feature Summary** — Implemented / Live Validated; acceptance freeze pending
10. **A2.10 — Replay / Validation / Baseline Evaluation**

Provider fallback/Zerodha, persistent caching, deferred-work orchestration,
provider health, and external news/fundamental evidence remain intentionally
deferred. They are not unimplemented promises inside the accepted A1 baseline;
their eventual milestone placement will be decided when scoped.

Major phases A2 through A10 remain defined by the canonical
`TRADINGINTELLIGENCE_ROADMAP.md`; this continuation map does not replace it.
