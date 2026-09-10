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

### TIAF_A2 — Complete / Baselined

TIAF_A2.1 through TIAF_A2.10 form the accepted deterministic platform. The
final sub-milestone tag is `tiaf-a2.10`; the accepted major tag is
`tiaf-a2-baseline`. Canonical closure
records are [`TIAF_A2_FOUNDATION_BASELINE.md`](TIAF_A2_FOUNDATION_BASELINE.md)
and [`TIAF_A2_ACCEPTANCE_REPORT.md`](TIAF_A2_ACCEPTANCE_REPORT.md).

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

## Accepted deterministic foundation

### TIAF_A2 — Deterministic Analysis / Feature Foundation — Complete / Live Validated

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

### TIAF_A2.9 — Deterministic Market-State & Opportunity Baseline — Complete / Live Validated

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

### TIAF_A2.10 — Replay / Validation / Baseline Evaluation — Complete / Live Validated

- Purpose: freeze normalized decision-time evidence and A2.9 output, prove exact
  provider-free replay, and attach later factual outcomes without lookahead.
- Scope: SHA-256 content identity, immutable run records, policy comparison,
  raw return/MFE/MAE, frozen-ranking statistics, append-only JSON/JSONL corpus,
  golden fixtures, and field-level regression diagnostics.
- Non-goals: policy tuning, arbitrary point-in-time reconstruction, execution
  simulation/P&L, database/replay farm, Agents, or human evaluation.
- Detail:
  [`TIAF_A2_10_REPLAY_VALIDATION_EVALUATION.md`](TIAF_A2_10_REPLAY_VALIDATION_EVALUATION.md).

## Accepted A2 sequence

1. **A2.1 — Feature Contracts + Engine Foundation** — Complete / Live Validated
2. **A2.2 — Price / Return / Volatility Features** — Complete / Live Validated
3. **A2.3 — Trend & Structure Features** — Complete / Live Validated
4. **A2.4 — Indicator Framework + Initial Indicator Library** — Complete / Live Validated
5. **A2.5 — Volume / Participation Features** — Complete / Live Validated
6. **A2.6 — Support / Resistance / Breakout Structure** — Complete / Live Validated
7. **A2.7 — Derivatives / Option-Chain Features** — Complete / Live Validated
8. **A2.8 — Relative Strength, Benchmark & Multi-Timeframe Context** — Complete / Live Validated
9. **A2.9 — Deterministic Market-State / Feature Summary** — Complete / Live Validated
10. **A2.10 — Replay / Validation / Baseline Evaluation** — Complete / Live Validated

Provider fallback/Zerodha, persistent caching, deferred-work orchestration,
provider health, and external news/fundamental evidence remain intentionally
deferred under stable `DEF-*` records. They are not unimplemented promises
inside the accepted A1 or A2 baseline. The A2 closure disposition for every
record is authoritative in `TIAF_DEFERRAL_REGISTER.md`.

Major phases A2 through A10 remain defined by the canonical
`TRADINGINTELLIGENCE_ROADMAP.md`; this continuation map does not replace it.

## TIAF_A3 sequence — A3.8 Accepted / A3.9 Implemented, Acceptance Pending

The authoritative design is
[`TIAF_A3_ARCHITECTURE.md`](TIAF_A3_ARCHITECTURE.md), and full goals,
non-goals, dependencies, contracts, deliverables, tests, live gates,
acceptance, deferrals, and handoffs are in
[`TIAF_A3_DETAILED_ROADMAP.md`](TIAF_A3_DETAILED_ROADMAP.md). No item below is
implemented merely by being documented.

1. **A3.1 — Agent Contracts and Provider-Neutral Runtime Foundation — COMPLETE / ACCEPTED**
   Freeze immutable requests, evidence references/packs, claims/citations,
   opinions, missing-evidence requests, budgets/usage, run records,
   capabilities, the calibrated-forecast consumer seam, typed failures, and
   `SpecialistAgent`/`ReasoningProvider` protocols, registry, deterministic
   serialization, and bounded single-specialist runtime. No tool/model
   execution. Detail:
   [`TIAF_A3_1_AGENT_FOUNDATION.md`](TIAF_A3_1_AGENT_FOUNDATION.md).
2. **A3.2 — Controlled Evidence, Reasoning, and Budget Gateways — COMPLETE / ACCEPTED**
   Enforce allow-listed read capabilities, schema-constrained optional
   reasoning, fingerprints/cache, least privilege, and complete budget/usage
   accounting with a first-class no-LLM mode.
   Detail: [`TIAF_A3_2_GATEWAYS_BUDGETS.md`](TIAF_A3_2_GATEWAYS_BUDGETS.md).
3. **A3.3 — Technical and Market Structure Specialist — COMPLETE / ACCEPTED**
   Interpret and cite A2 evidence without recalculating it; preserve the A2.9
   benchmark and all conflict. Detail:
   [`TIAF_A3_3_TECHNICAL_SPECIALIST.md`](TIAF_A3_3_TECHNICAL_SPECIALIST.md).
4. **A3.4 — Fundamental Evidence and Company Quality Specialist — COMPLETE / ACCEPTED**
   Adds provider-neutral point-in-time contracts, deterministic preprocessing,
   a bounded read-only caller-supplied/test source path, and long-horizon company
   interpretation. Detail:
   [`TIAF_A3_4_FUNDAMENTAL_INTELLIGENCE.md`](TIAF_A3_4_FUNDAMENTAL_INTELLIGENCE.md).
5. **A3.5 — News, Filing, Catalyst, and Event Intelligence — COMPLETE / ACCEPTED**
   Adds sourced/time-aware contracts, deterministic entity/revision/dedup/PIT
   processing, bounded caller-supplied/test reads, and cited no-LLM
   interpretation. Detail:
   [`TIAF_A3_5_NEWS_EVENT_INTELLIGENCE.md`](TIAF_A3_5_NEWS_EVENT_INTELLIGENCE.md).
6. **A3.6 — Relative, Sector, and Macro Context Specialists — COMPLETE / ACCEPTED**
   Implements three separate selectable, cited, deterministic/no-LLM
   capabilities; explicit benchmark/sector/sensitivity mappings; point-in-time
   sector/macro evidence contracts; controlled gateways; and shared source
   snapshot reuse. Production adapters and automatic mapping remain deferred.
   Detail:
   [`TIAF_A3_6_RELATIVE_SECTOR_MACRO_INTELLIGENCE.md`](TIAF_A3_6_RELATIVE_SECTOR_MACRO_INTELLIGENCE.md).
7. **A3.6.1 — Market Intelligence Provider Fabric + Deep Research Foundation — IMPLEMENTED / LIVE ACCEPTANCE HOLD**
   Implements provider declarations, per-capability routing, progressive
   enrichment, provider-native normalization, contradiction preservation,
   sparse evidence memory, structured research inputs, a read-only injected
   Tapetide adapter boundary, and a secondary fixture without making
   Tapetide/MCP a domain dependency. Its isolated read-only stdio connector is
   complete; the final live matrix is on HOLD because the daily provider quota
   was exhausted before the ATHERENERG financial diagnostic could observe a
   raw response. Detail:
   [`TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md`](TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md).
   **Bounded post-A3.6.1 follow-up — Authoritative Confirmation Gateway — IMPLEMENTED / LIVE VALIDATED.** Reuses the existing provider fabric to
   confirm selectively escalated material claims against official
   exchange, regulator, company-IR, or rating evidence. Preserve document
   identity/hash/revision, field-level confirmation status, event clustering,
   ambiguity, budgets, and replay without exposing source transports to
   specialists. This is an internal follow-up and does not renumber A3.7.
   Detail:
   [`TIAF_AUTHORITATIVE_CONFIRMATION_GATEWAY.md`](TIAF_AUTHORITATIVE_CONFIRMATION_GATEWAY.md).
8. **A3.6.2 — Market Intelligence / Deep Research Integration — COMPLETE / ACCEPTED**
   Integrates existing capability routing, Tapetide/Yahoo enrichment,
   authoritative confirmation, normalized evidence quality/PIT, sparse graph,
   deterministic epistemically constrained research output, explicit gaps,
   fingerprints, and provider-free replay. The bounded four-symbol live matrix
   passed with 12 read-only calls and zero model usage. Detail:
   [`TIAF_A3_6_2_MARKET_INTELLIGENCE_DEEP_RESEARCH_INTEGRATION.md`](TIAF_A3_6_2_MARKET_INTELLIGENCE_DEEP_RESEARCH_INTEGRATION.md).
9. **A3.7 — Derivatives Context, Opportunity Quality, and Opportunity Risk Specialists — IMPLEMENTED / USER-LEVEL ACCEPTANCE COMPLETE**
   Three separate AgentOpinionV2 specialists interpret supplied A2.7/current
   derivative evidence, A2.9 opportunity maturity/room, and grouped downside
   context without recomputation, contract selection, position management,
   arbitration, or unsupported probabilities. Deterministic fixtures, cited
   claims, grouped-confidence protection, zero-LLM operation, and exact replay
   pass. Bounded Dhan live acquisition was attempted on 2026-09-10 but returned
   `request failed`; no live output is claimed. Six black-box deterministic
   scenarios pass through the public registry/runtime composition. Detail:
   [`TIAF_A3_7_DERIVATIVES_OPPORTUNITY_RISK.md`](TIAF_A3_7_DERIVATIVES_OPPORTUNITY_RISK.md).
10. **A3.8 — Instrument-Aware Planner and Specialist Orchestration — ACCEPTED / FROZEN AT `tiaf-a3.8`**
   Coordinate accepted specialists from `tiaf-a3.7` using capability/dependency
   policy, deterministic bounded parallel waves, shared evidence and budget
   reservations, selective enrichment/confirmation/deep research, affected-node
   reruns and versioned replans, honest partial stops, and captured replay.
   LangGraph stays in an infrastructure adapter; the Planner owns workflow,
   not investment decisions. Ten internal work packages and the 14-case offline
   acceptance matrix are complete, without implementing A3.9 or later ownership. Detail:
   [`TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md`](TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md).
11. **A3.9 — Structured Opportunity Intelligence MVP — IMPLEMENTED / ACCEPTANCE PENDING**
   Assemble a captured A3.8 run into a single-underlying immutable product with
   typed contributions, qualified bias, deterministic observation state, cited
   reasons, visible contradictions/gaps, separated confidence and unchanged A2
   comparison. No ranking, hidden voting/arbitration, provider acquisition or
   specialist rerun; A4–A10 authority remains absent. Nine internal packages and
   replay/user-level acceptance gates are implemented; results are recorded in
   [the acceptance study](STUDY_A3_9_USER_LEVEL_ACCEPTANCE.md). Design:
   [`TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md`](TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md).
12. **A3.10 — Agent Replay, Baseline Comparison, Cost, and Failure Hardening — PLANNED**
    Freeze Agent records/corpora, offline replay/regression, scale/cost evidence,
    failure injection, security checks, and the A7 outcome linkage.

A7 is minimally refined to **Evaluation, Forecasting and Learning**. A3 defines
and consumes calibrated forecast evidence but never asks an LLM to manufacture
probabilities; A7 owns forecast generation, out-of-sample calibration,
evaluation, promotion, and rollback.
