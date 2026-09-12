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

## TIAF_A3 sequence — A3.1-A3.10 Accepted / Major Closure Ready

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
7. **A3.6.1 — Market Intelligence Provider Fabric + Deep Research Foundation — ACCEPTED / PROVIDER-SPECIFIC LIVE LIMIT RECORDED**
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
11. **A3.9 — Structured Opportunity Intelligence MVP — ACCEPTED / FROZEN AT `tiaf-a3.9`**
   Assemble a captured A3.8 run into a single-underlying immutable product with
   typed contributions, qualified bias, deterministic observation state, cited
   reasons, visible contradictions/gaps, separated confidence and unchanged A2
   comparison. No ranking, hidden voting/arbitration, provider acquisition or
   specialist rerun; A4–A10 authority remains absent. Nine internal packages and
   replay/user-level acceptance gates are implemented; results are recorded in
   [the acceptance study](STUDY_A3_9_USER_LEVEL_ACCEPTANCE.md). Design:
   [`TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md`](TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md).
12. **A3.10 — Agent Replay, Baseline Comparison, Cost, and Failure Hardening — COMPLETE / ACCEPTED AT `tiaf-a3.10`**
    Adds content-addressed A3 packages, recorded/deterministic/comparison replay,
    observational A2/A3 axes, exact-versus-unknown cost accounting, lossless
    failure/degradation summaries, a 22-case fault matrix, 14-case synthetic
    acceptance corpus, and a later closure-readiness seam. It does not alter
    A3.9 or perform A3 closure. [Acceptance study](STUDY_A3_10_USER_LEVEL_ACCEPTANCE.md). Detail:
    [`TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md`](TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md).

The separate [A3 major closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
concluded `READY_TO_FREEZE_A3`. Accepted implementation and closure documentation
are frozen at `tiaf-a3-baseline` (`e690da2`). A4 had not started at that closure;
the later A4.1 implementation is additive and does not revise it.

The later
[A3 sub-milestone deferral-discovery audit](STUDY_A3_SUBMILESTONE_DEFERRAL_DISCOVERY_AUDIT.md)
adds stable governance records DEF-052 through DEF-055 for production
model-backed reasoning, cross-candidate A3 analysis, user-facing citation/report
rendering and monetary pricing knowledge. These are post-A3 deferrals and do
not change accepted runtime or freeze readiness.

### Post-A3 deep architecture continuation

[Pass 1 — TI_CORE and capability boundary](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md)
concludes `READY_FOR_DEEP_ARCH_PASS_2` with architecture verdict
`APPROVE_WITH_REVISIONS`. [TIAF_SYSTEM_ARCHITECTURE.md](TIAF_SYSTEM_ARCHITECTURE.md)
is authoritative for the logical kernel and curated public/engineering/private
boundary; this is not runtime implementation or a re-freeze of A3.

[Pass 2 — Source Authority / Provenance / Contradiction Semantics](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md)
concludes `READY_FOR_DEEP_ARCH_PASS_3` and promotes its
[semantic architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md).
[Pass 3 — A4 Challenge / Arbitration / Higher-Intelligence Agents](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md)
concludes `READY_FOR_DEPLOYMENT_ARCH_REVIEW` and approves the
[A4 architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md).
[Deployment review](TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md) concludes
`READY_FOR_POST_A3_CONSOLIDATION` and approves the bounded
[deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md): one trusted local
Python application runtime, request-local analysis and single-writer filesystem
replay. Existing adapter-local subprocesses remain; no new service is required.
The [completed consolidation](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md)
concludes `READY_FOR_POST_A3_FOUNDATION_IMPLEMENTATION` and design-only
`READY_TO_TAG_POST_A3_ARCHITECTURE` (no tag created).
Complete / accepted: **POST_A3_PRE_A4_FOUNDATION — Source Semantics,
A4 Input Projection and Replay Integrity**. See the
[implementation contract](TIAF_POST_A3_PRE_A4_FOUNDATION.md) and
[acceptance study](STUDY_POST_A3_PRE_A4_FOUNDATION_ACCEPTANCE.md). Frozen A2/A3
records remain unchanged; the later A4.1 runtime consumes the foundation
without editing those records.

Complete / accepted: **POST_A3_PRE_A4_LOCAL_FACADE — Narrow Local Capability
Facade and Invocation Lifecycle**. See the
[implementation record](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) and
[acceptance study](STUDY_POST_A3_PRE_A4_LOCAL_FACADE_ACCEPTANCE.md). The facade
now exposes five bounded public operations, permission-filtered discovery and
engineering replay verification after the additive A4.1 extension. It has no
live operation or remote transport;
`opportunity.orchestrate` and `trace.inspect` remain deliberately absent.

Deployment work must not delay the in-process semantic foundation. The separate
DEF-003 local facade/lifecycle slice precedes Shell/public consumers; operational
TM may later justify a separate local TI host. A8 owns TM/conditional service,
A9 scanners and A10 justified durable operations. Multi-writer storage, shared
quotas, background jobs and remote exposure require their own acceptance gates;
none is implemented or required for the next offline semantic package.

The accepted **POST_A3_PRE_A4_FOUNDATION** provides source identity/scoped
authority and bindings; comparability/dispute/independence; confirmation and
semantic input projection; and captured replay/contract tests. It is a bounded
prerequisite package, not a numbered major milestone or an A4 runtime
sub-milestone. Citation UX, Shell, adapters and another graph/store remain out of
scope. DEF-054 remains presentation work; no deferral ID/status changed.
That statement records the foundation gate. The later
[A4 closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) changes DEF-054 to
`PLANNED` for a minimal pre-A5 Shell renderer while leaving richer report/Web
presentation deferred.

**TIAF_A4.1 — Deterministic Challenge / Arbitration — IMPLEMENTED / ACCEPTED.**
The bounded [`tiaf.a4` implementation](TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md)
delivers typed thesis/challenge/result contracts, the deterministic Challenger
and Arbitrator, explicit dispositions/failures, cumulative replay/verification/
comparison and the 25-scenario acceptance matrix. Semantic-need execution through
the existing Planner is delivered by the separate A4.2 integration. Optional model execution
requires an additive role-aware gateway bridge and approved adapter/configuration,
privacy/pricing and validation policy; it is not mandatory for deterministic A4
or an implicit delivery of DEF-052.

**TIAF_A4.2 — Governed Evidence-Need / Planner Bridge — IMPLEMENTED / ACCEPTED.**
The internal
[`tiaf.a4_enrichment` implementation](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md)
finalizes provider-neutral evidence needs, deterministic admission, one-round
A3.8 execution, explicit normalized source-semantic capture, later successor
projection/A4 review and zero-live replay. It stops rather than patching A2/A3
when lower-layer refresh is required. The facade remains captured-read-only;
model-backed challenge, Shell, A5/A6/A7 and broker authority remain out of scope.
The [A4 major closure review](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) accepts
both slices as one baseline now frozen at `tiaf-a4-baseline` (`494d968`), and
keeps DEF-052/055 deferred. The selected
[POST_A4_PRE_A5 Shell review](TIAF_POST_A4_PRE_A5_TI_SHELL_ARCHITECTURE_REVIEW.md)
and [command-first local architecture](TIAF_TI_SHELL_ARCHITECTURE.md) now have a
bounded [v0.1 implementation](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md). It remains
an unnumbered facade consumer and is not an A5 hard dependency.
DEF-003 has separate local and remote delivery tracks under the same stable ID:
the selected order is foundation -> narrow local facade/lifecycle -> deterministic
A4. The facade is mandatory before Shell/public consumers, not a dependency of
internal foundation projection. Remote service/TM delivery remains A8 as required.
Microservices, package
relocation, universal envelopes and dynamic plugin loading are not approved.

A7 is minimally refined to **Evaluation, Forecasting and Learning**. A3 defines
and consumes calibrated forecast evidence but never asks an LLM to manufacture
probabilities; A7 owns forecast generation, out-of-sample calibration,
evaluation, promotion, and rollback.

### Completed foundation entry and exit

The consolidation §7 is the authoritative bounded work specification:
F1 source identity/scoped authority/policy bindings; F2 proposition/comparability,
independence and append-only disputes; F3 confirmation and A4 semantic input
projection; F4 additive capture/replay/integrity. Implement deterministic fixtures
F01–F16, list/JSON/tuple and aware Asia/Kolkata contracts, typed ID/value/scope
checks and unchanged parent captures. No live validation is required; no
acquisition/model/facade/A4 roles/UI/new graph/store are in scope. Run focused
foundation/current-boundary tests and full pytest/compile/ruff/mypy/diff gates.
The foundation gate completed as `READY_TO_ACCEPT_POST_A3_PRE_A4_FOUNDATION`.
The subsequent local facade/lifecycle gate completed as
`READY_TO_ACCEPT_POST_A3_PRE_A4_LOCAL_FACADE`; deterministic A4.1 contracts,
runtime and facade parity plus the A4.2 bridge are now implemented, accepted,
and jointly reviewed for the A4 baseline freeze.

### Subsequent planned tracks

- A4-D1 typed contracts/policies, D2 deterministic Challenger/Arbitrator and the
  bounded D4 replay/cost/failure acceptance are implemented by A4.1. D3 governed
  evidence-need/successor bridge is implemented by A4.2 with one round/cycle.
  Model priors motivate hypotheses only; admitted new evidence follows ordinary
  source/PIT/authority checks and does not alter an old cutoff.
- Optional model lane after deterministic A4/bridge: role-aware gateway, approved
  adapter, privacy/egress, pricing knowledge, versioned structured prompts/output,
  hypothesis-vs-fact and ID/value rejection, no-LLM control, replay and evaluation.
  DEF-052/055 remain deferred, no mandatory model for deterministic A4.
- Shell v0.1 is implemented after the approved architecture: command-first,
  same-process, facade-only and transient, before A5 implementation but not an
  A5 hard gate. Minimal captured-source/A4 rendering is delivered; NLP, Web and
  rich bibliography remain outside it under the open portion of DEF-054.
- A5 on-demand positions plus bounded monitoring-contract review; A6 deterministic
  valid candidates; A7 calibration/evaluation/ranking; forecast-enhanced A6 follow-up;
  A8 TM, A9 scanners, A10 production. No renumbering or infrastructure rollout.

### TIAF_A5 architecture, A5.1 and A5.2 — Complete / ready to freeze

The [authoritative A5 design](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md) and
[review](TIAF_A5_ARCHITECTURE_REVIEW.md) approve an additive position-intelligence
boundary. A5 consumes a current authorized TM/broker snapshot and immutable A4
result, keeps operational state separate from analytical posture/thesis health/
recommendation, emits non-executable advice and immutable monitoring intent, and
supports captured replay. `FREE` is rejected as ambiguous; trailing is advice,
not lifecycle. The bounded runtime is documented by
[A5.1](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md).

**Delivered A5.1 target.** Frozen input/result/mandate/capture contracts, strict
identity/freshness/A4-lineage checks, a transparent deterministic single-open-
position policy, monitoring-need output, exact offline replay/verification/
comparison and the architecture acceptance corpus.

**Delivered A5.2 target.** The governed `position.assess` captured-read facade
capability, position-specific artifact authorization, generic A5 recorded replay,
bounded `position assess` Shell command and structured explain/trace projections
are documented in
[A5.2](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md). Multi-leg interpretation,
TM/broker access, scheduling, A6, A7, providers/models and remote/durable
infrastructure remain out of scope.

The [A5 major closure review](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md) accepts
these slices as one coherent milestone, records the remaining boundaries under
stable deferral governance, and recommends—but does not create—the
`tiaf-a5-baseline` tag. The exact next architecture prompt is
`TIAF_A6 — OPTION EXPRESSION INTELLIGENCE ARCHITECTURE PASS`.
