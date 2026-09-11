# Milestones

The canonical roadmap is maintained in `TRADINGINTELLIGENCE_ROADMAP.md`. The
repository also retains the original companion
`TradingIntelligence_TIAF_Implementation_Roadmap.docx`; milestone status follows
the Markdown source and the closure records below.

The initial repository bootstrap milestone `TIAF_TGT0` is complete and frozen. The active development sequence now proceeds through the TIAF implementation roadmap.

## Current Development Position

**TIAF_TGT0 — Initial Project Baseline: COMPLETE / FROZEN**

- Professional Python project skeleton created
- `tiaf` package established
- baseline configuration, documentation, tests, linting and typing checks added
- no trading logic, broker integration, LLM calls, or agent workflows introduced
- tag: `tiaf-tgt0`

**TIAF_A1 — Data Foundation: COMPLETE / BASELINED** at tag `tiaf-a1-baseline`.

**TIAF_A2 — Deterministic Baseline: COMPLETE / BASELINED** at tag
`tiaf-a2-baseline`. Final accepted sub-milestone tag: `tiaf-a2.10`.

**TIAF_A2.1:** COMPLETE / LIVE VALIDATED at tag `tiaf-a2.1`.

**TIAF_A2.2:** COMPLETE / LIVE VALIDATED at tag `tiaf-a2.2`.

**TIAF_A2.3:** COMPLETE / LIVE VALIDATED at tag `tiaf-a2.3`.

**TIAF_A2.4:** COMPLETE / LIVE VALIDATED at tag `tiaf-a2.4`.

**TIAF_A2.5:** COMPLETE / LIVE VALIDATED at tag `tiaf-a2.5`.

**TIAF_A2.6:** COMPLETE / LIVE VALIDATED at tag `tiaf-a2.6`.

**TIAF_A2.7:** COMPLETE / LIVE VALIDATED at tag `tiaf-a2.7`.

**TIAF_A2.8:** COMPLETE / LIVE VALIDATED at tag `tiaf-a2.8`.

**TIAF_A2.9:** COMPLETE / LIVE VALIDATED at tag `tiaf-a2.9`.

**TIAF_A2.10:** COMPLETE / LIVE VALIDATED at tag `tiaf-a2.10`.

**TIAF_A3_ARCH — COMPLETE / ACCEPTED** at tag `tiaf-a3-arch`.

**TIAF_A3.1 — Agent Contracts and Runtime Foundation: COMPLETE / ACCEPTED** at
tag `tiaf-a3.1`.

**TIAF_A3.2 — Controlled Gateways and Budgets: COMPLETE / ACCEPTED** at tag
`tiaf-a3.2`.

**TIAF_A3.3 — Technical / Market-Structure Specialist: COMPLETE / ACCEPTED** at
tag `tiaf-a3.3`.

**TIAF_A3.4 — Fundamental / Company-Quality Intelligence: COMPLETE / ACCEPTED**
at tag `tiaf-a3.4`.

**TIAF_A3.5 — News / Catalyst / Event Intelligence: COMPLETE / ACCEPTED** at
tag `tiaf-a3.5`.

**TIAF_A3.6 — Relative / Sector / Macro Context Intelligence: COMPLETE /
ACCEPTED** at tag `tiaf-a3.6`.

**TIAF_A3.6.1 — Market Intelligence Provider Fabric + Deep Research
Foundation: COMPLETE / ACCEPTED** at tag `tiaf-a3.6.1`. The standalone
exact-current Tapetide matrix retained a provider-quota `HOLD`; separate Yahoo
fallback and A3.6.2 integrated bounded-live matrices passed.

**TIAF_A3.6.2 — Market Intelligence / Deep Research Integration: COMPLETE /
ACCEPTED** at tag `tiaf-a3.6.2`.

**TIAF_A3.7 — Derivatives / Opportunity Quality / Opportunity Risk: COMPLETE /
ACCEPTED** at tag `tiaf-a3.7`; bounded Dhan live acquisition failed before
option-chain evidence, so no live specialist result is claimed.

**TIAF_A3.8 — Planner / Specialist Orchestration: COMPLETE / ACCEPTED** at tag
`tiaf-a3.8`.

**TIAF_A3.9 — Structured Opportunity Intelligence: COMPLETE / ACCEPTED** at
tag `tiaf-a3.9`.

**TIAF_A3.10 — Replay / Baseline Comparison / Cost / Failure Hardening:
COMPLETE / ACCEPTED** at tag `tiaf-a3.10`.

**TIAF_A3 major closure: COMPLETE / BASELINED** at tag `tiaf-a3-baseline`.

**POST_A3_PRE_A4_FOUNDATION: COMPLETE / ACCEPTED.** Deterministic source
semantics, A4 input projection and replay integrity; no A4 runtime.

**POST_A3_PRE_A4_LOCAL_FACADE: COMPLETE / ACCEPTED.** Narrow same-process
capability catalog, trusted admission/lifecycle and captured replay; no live
operation, transport or Shell.

**TIAF_A4.1 — Deterministic Challenge / Arbitration: IMPLEMENTED / ACCEPTANCE
CANDIDATE.** Typed premises/theses/findings, deterministic Challenger and
Arbitrator, seven non-action dispositions, offline replay/verification and the
captured-read `a4.evaluate` facade capability. No live/model/acquisition,
position, expression, forecast or execution authority.

## Deferral governance

Intentional deferrals are retained under stable IDs in
[`TIAF_DEFERRAL_REGISTER.md`](TIAF_DEFERRAL_REGISTER.md). They are recorded when
discovered but reviewed as a group only at each **major milestone closure**
(A2, A3, A4, and so on), not after every sub-milestone.

Each major closure reports deferrals introduced, implemented, rejected,
superseded, carried forward with rationale, and remaining high-priority items.
Satisfied dependencies should trigger an implementation attempt; unresolved
items remain visible rather than silently rolling forward.

## TIAF_A0 — Domain Contracts and Foundation — COMPLETE / FROZEN

Purpose: establish the stable language every future Planner, Agent, Scanner and TradeMonitor integration will use.

Planned scope:

- `OpportunityRequest`
- `PositionRequest`
- `EvidenceItem`
- `DataSnapshot`
- `AgentOpinion`
- `AgentDecisionBundle`
- `OpportunityAssessment`
- `PositionAssessment`
- `OptionExpression`
- stable identifiers and timestamps
- schema/version compatibility rules
- domain enums for style, horizon, direction, action, strength, freshness, evidence and confidence
- serialization/validation tests

No LangGraph workflow, LLM call, broker API, market prediction, or execution capability belongs in A0.

## TIAF_A1 — Data Foundation — COMPLETE / BASELINED

Canonical closure records:

- `TIAF_A1_FOUNDATION_BASELINE.md`
- `TIAF_A1_ACCEPTANCE_REPORT.md`
- baseline tag: `tiaf-a1-baseline`

**Complete / frozen:** TIAF_A1.1 — Provider Contracts + Normalized Market Models

- normalized instrument, quote, OHLCV, historical-series, and instrument-master models
- provider capability protocol
- typed data/provider failures
- canonical timestamp, identity, interval, and freshness normalization helpers
- no live provider adapter

**Complete / live-validated:** TIAF_A1.2 — Dhan Core Market Data Adapter

- authenticated, read-only DhanHQ v2 HTTP transport
- ordered and chunked full market quotes
- daily and supported intraday OHLCV
- typed Dhan error translation
- explicit security-ID and derivative-instrument mapping boundaries
- no orders, portfolio access, WebSocket, or trading behavior

**Complete / live-validated:** TIAF_A1.3 — Dhan Derivatives & Live Option Intelligence Data

- provider-neutral frozen expiry-list and live option-chain contracts
- read-only Dhan expiry discovery and complete option-chain normalization
- contract IDs, spot, prices, top-of-book, OI, volume, IV, and reported Greeks
- separate `DerivativesDataProvider` protocol
- no expired history, selection, analytics, recommendations, or execution

**Complete / live-validated:** TIAF_A1.4 — Dhan Historical / Expired Options Data

- provider-neutral rolling historical-option bars and series
- read-only Dhan expired-options endpoint using underlying security IDs
- explicit weekly/monthly expiry code and ATM-relative strike context
- complete factual OHLC, IV, volume, OI, actual-strike, and spot arrays
- adjacent half-open 30-day chunking and deterministic merge semantics
- no replay strategy, option selection, recommendation, or execution

**Complete / live-validated:** TIAF_A1.5 — Instrument Resolver

- frozen provider-neutral exact query and explicit result contracts
- Dhan detailed instrument-master load/download and narrow atomic file cache
- indexed security-ID, trading-symbol, and symbol-plus-filter resolution
- explicit configurable primary-exchange selection with visible policy metadata
- generic ambiguity preservation and no first-row selection
- deterministic exchange-scoped F&O-underlying universe from derivative identity
- symbol-first smoke diagnostics with hard symbol/security-ID consistency checks
- provider diagnostic/test identities excluded from canonical F&O universes
- no recommendation, ranking, Agent, order, account, or spreadsheet behavior

**Complete / live-validated:** TIAF_A1.6 — Cache, Freshness & Provider Scheduling

- provider-neutral in-process factual cache and deterministic cache keys
- caller-relative freshness with visible `FRESH` / `AGING` / `STALE` / `UNKNOWN`
- monotonic provider scheduling with explicit non-sleeping eligibility decisions
- key-scoped request coalescing and opt-in bounded stale-on-error fallback
- documented Dhan quote and option-chain constraints outside generic runtime
- no background queues, Intelligence OS, Agents, recommendations, or execution

**Complete / live-validated:** TIAF_A1.7 — AnalysisContext Builder

- immutable provider-neutral analysis subject, requirements, evidence slots,
  aggregate context, ordered batch outcomes, and factual summary
- A1.5 resolution plus A1.6-coordinated quote, history, explicit option-chain,
  and exact historical-options acquisition
- deterministic required-only retrieval freshness, completeness, quality, and
  partial/failure semantics with separate retrieval/source-observation
  provenance
- ordered batch statuses distinguish completed/partial contexts, temporary
  provider-scheduler deferral, and errors without hidden sleeps or retries
- no indicators, scoring, recommendation, Agent, queue, broker, or execution

**Acceptance:** a watchlist can be converted into timestamp-consistent factual
contexts or explicit partial/deferred/error outcomes. Provider fallback,
external evidence, persistent caching, and retry orchestration remain future
work rather than hidden A1 behavior.

## TIAF_A2 — Deterministic Baseline — COMPLETE / LIVE VALIDATED

**TIAF_A2.1 — Feature Contracts + Engine Foundation: COMPLETE / LIVE VALIDATED**

- immutable provider-neutral feature definitions, requests, results, and bundles
- explicit deterministic calculator registry and context-only engine
- exact baseline price, history, return, and high/low range measurements
- source quality, provenance, timestamp, and insufficient-data preservation
- no interpretation, recommendation, Agent, broker, or execution behavior

**TIAF_A2.2 — Price / Return / Volatility Features: COMPLETE / LIVE VALIDATED**

- exact price-location, logarithmic return, candle-range, drawdown, and run-up
  measurements
- strict Wilder ATR, explicit-factor realized volatility, rolling extrema, and
  signed move/ATR
- worst-source quality aggregation and market-observation `as_of` semantics
- no trend classification, score, recommendation, Agent, or execution behavior

**TIAF_A2.3 — Trend & Structure Features: COMPLETE / LIVE VALIDATED**

- completed-history moving averages, distance/spread, OLS slope, and R-squared
- directional efficiency, close-transition fractions, and trailing runs
- deterministic adjacent high/low fractions and rolling-range position
- ATR-normalized distance from SMA/EMA without interpretation or signals

**TIAF_A2.4 — Indicator Framework + Initial Indicator Library: COMPLETE / LIVE VALIDATED**

- first-class immutable definitions, requests, results, bundles, and explicit
  extensible calculator registry
- indicator-agnostic deterministic engine over completed `AnalysisContext`
  history
- SuperTrend, RSI, MACD, ADX/DI, Bollinger, and Donchian factual outputs
- no strategy signals, recommendations, optimization, Agent, or execution

A2.4 was inserted because scanners, strategy engines, Agents, replay systems,
parameter optimization, dashboards, and custom indicators need one reusable
versioned abstraction. Indicators complement rather than replace A2.3
primitive measurements.

**TIAF_A2.5 — Volume / Participation Features: COMPLETE / LIVE VALIDATED**

- completed-history raw, average, median, relative, change, dispersion, and
  volume-slope measurements
- deterministic close-transition participation and price/range alignment
- no accumulation/distribution claims, confirmation, signal, or Agent logic

**TIAF_A2.6 — Support / Resistance / Breakout Structure: COMPLETE / LIVE VALIDATED**

- prior rolling boundaries that explicitly exclude the current completed bar
- close/wick excursion, prior-range position, and normalized range geometry
- no subjective pivots, confirmation, score, recommendation, or Agent logic

**TIAF_A2.7 — Derivatives / Option-Chain Features: COMPLETE / LIVE VALIDATED**

- explicit-expiry option-chain geometry and factual derivative measurements
- ATM premiums/IV/Greeks, exact-window OI/volume/spread/concentration primitives
- no option selection, strategy model, recommendation, or execution

**TIAF_A2.8 — Relative Strength, Benchmark & Multi-Timeframe Context: COMPLETE / LIVE VALIDATED**

- explicit caller-supplied benchmark identity and exact aligned-bar comparisons
- ordered per-timeframe feature contexts and factual cross-timeframe fractions
- no scoring, ranking, recommendation, Agent, or execution logic
- implementation and read-only Dhan validation accepted at tag `tiaf-a2.8`

**TIAF_A2.9 — Deterministic Market-State & Opportunity Baseline: COMPLETE / LIVE VALIDATED**

- immutable policy, request, component, contribution, assessment, and ranking contracts
- separate positive/negative direction, alignment/conflict, quality, room, and maturity
- horizon-specific version 1.0 DAY/POSITIONAL engineering policies
- transparent `TOP_MOVER`, `EARLY_OPPORTUNITY`, `MATURE_AVOID_CHASE`, and `NO_TRADE`
- eligible-only score/quality/symbol ranking with stable ties and complete audit retention
- no providers, Agents, LLMs, strategies, order logic, or execution inside the subsystem

**TIAF_A2.10 — Replay / Validation / Baseline Evaluation: COMPLETE / LIVE VALIDATED**

- content-addressed normalized evidence snapshots and immutable run records
- exact provider-free replay and policy comparison over unchanged evidence
- later factual outcome paths, MFE/MAE, and frozen-ranking statistics
- append-only filesystem corpus and deterministic field-level regression checks
- no policy optimization, historical reconstruction claim, simulated execution, or Agents

The A2 closure and governed deferral burn-down are complete. Canonical closure
records are `TIAF_A2_FOUNDATION_BASELINE.md` and
`TIAF_A2_ACCEPTANCE_REPORT.md`; the accepted major baseline tag is
`tiaf-a2-baseline`.

- deterministic feature engine
- multi-timeframe price/volume features
- ATR / ATR%
- Move/ATR / range-consumption
- trend and momentum
- relative volume
- relative strength vs index/sector
- volatility regime
- basic support/resistance context
- horizon-specific bullish/bearish scoring
- candidate classes such as `TOP_MOVER`, `EARLY_OPPORTUNITY`, `MATURE_AVOID_CHASE`, `NO_TRADE`

**Acceptance:** reproducible non-AI rankings exist as a benchmark the Agent system must later beat.

## TIAF_A3 — Specialist Intelligence — Ready to Freeze

Accepted bounded capabilities include Technical/Market Structure,
Fundamental/Company Quality, News/Catalyst/Event, Relative, Sector/Rotation,
Macro, Derivatives Context, Opportunity Risk, Contrarian Hypothesis, and
conditional Forecast Interpretation. An instrument-aware Planner selects only
the evidence and specialists justified by the horizon, purpose, candidate
stage, and explicit budget. Agents consume shared evidence through controlled
gateways and cannot call brokers, arbitrary providers, browsers, or shell tools.

The implemented and accepted sequence is A3.1 contracts; A3.2 evidence/reasoning/budget
gateways; A3.3 technical specialist; A3.4 fundamentals; A3.5 news/events; A3.6
relative/sector/macro; A3.6.1 provider fabric/research foundation; A3.7
derivatives/risk; A3.8 Planner; A3.9 structured
underlying intelligence; and A3.10 replay/cost/failure hardening. See
[`TIAF_A3_ARCHITECTURE.md`](TIAF_A3_ARCHITECTURE.md) and
[`TIAF_A3_DETAILED_ROADMAP.md`](TIAF_A3_DETAILED_ROADMAP.md).

**A3.1 implementation:** immutable Agent/evidence/claim/confidence/budget/run
contracts, AgentOpinion v2 with frozen A0-v1 compatibility, runtime-checkable
protocols, extensible registry, deterministic serialization, and an exactly-one-
specialist failure-isolating runtime. See
[`TIAF_A3_1_AGENT_FOUNDATION.md`](TIAF_A3_1_AGENT_FOUNDATION.md). Status is
complete/accepted. A3.2 adds controlled evidence/reasoning registries and
runtimes, A2 evidence reuse, capability policy, model-tier mapping, no-LLM
mode, structured-output validation, budgets, cache keys, and audit records; it
is complete/accepted. See
[`TIAF_A3_2_GATEWAYS_BUDGETS.md`](TIAF_A3_2_GATEWAYS_BUDGETS.md). A3.3 adds the
first deterministic, cited technical specialist and is complete/accepted; see
[`TIAF_A3_3_TECHNICAL_SPECIALIST.md`](TIAF_A3_3_TECHNICAL_SPECIALIST.md). A3.4
adds provider-neutral point-in-time company evidence and the deterministic,
cited Fundamental Specialist; see
[`TIAF_A3_4_FUNDAMENTAL_INTELLIGENCE.md`](TIAF_A3_4_FUNDAMENTAL_INTELLIGENCE.md).
A3.5 is complete/accepted at `tiaf-a3.5`. A3.6 adds three separate contextual
specialists, explicit mapping/sensitivity evidence, controlled sector/macro
gateways, and shared source-context reuse; see
[`TIAF_A3_6_RELATIVE_SECTOR_MACRO_INTELLIGENCE.md`](TIAF_A3_6_RELATIVE_SECTOR_MACRO_INTELLIGENCE.md).
A3.6.1 implements provider-neutral fine capabilities, per-capability routing,
semantic normalization/conflicts, a read-only Tapetide adapter boundary, a
secondary fixture, sparse evidence memory, and composable research contracts;
see [`TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md`](TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md).

A3.6.2 through A3.10 are accepted at their corresponding tags. The separate
[A3 major closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md) reconciles
the full inventory, live/non-live evidence and all active deferrals, and
concludes `READY_TO_FREEZE_A3`. The recommended major tag is
`tiaf-a3-baseline`; post-A3 architecture consolidation, not A4 implementation,
is the next review.

**Acceptance:** a bounded A2-screened set can produce zero or more replayable,
cited underlying-opportunity records with separate specialist opinions,
disagreement, quality/freshness, missing evidence, budgets, and A2 comparison.
`WAIT`, `NO_TRADE`, `ABSTAIN`, and insufficient evidence are valid. A3 does not
emit `CE`/`PE`; A6 owns option expression.

## TIAF_A4 — Arbitration and Adversarial Review

- independent bull/bear challenge
- disagreement visibility
- evidence-quality weighting
- freshness-aware arbitration
- confidence calibration foundation
- explicit `WAIT` / `NO_TRADE`
- persistent specialist opinions for later scoring

**Acceptance:** no single fluent Agent becomes an oracle; final recommendations expose consensus, disagreement and evidence.

## TIAF_A5 — Position Intelligence MVP

Primary TradeMonitor use case:

- broker position is adopted in TM
- original entry rationale is optional and not required
- TIAF evaluates the position from the current moment forward
- actions: `HOLD`, `WATCH_CLOSELY`, `PROTECT`, `PARTIAL_BOOK`, `BOOK`, `EXIT`
- strengths: `MILD`, `MODERATE`, `STRONG`, `URGENT`
- stateful reassessment
- event/time/price/news/sector/volatility-triggered review

**Acceptance:** an adopted position can receive forward-looking management intelligence without manual conversational prompting.

## TIAF_A6 — Option Expression Intelligence

- separate underlying view from option-contract selection
- expiry selection
- ATM / ITM / OTM comparison
- delta / theta / IV
- liquidity / bid-ask spread
- OI / option volume
- event exposure
- reject bad option expressions even when the underlying view is good

**Acceptance:** TIAF can recommend a suitable CE/PE contract or explicitly return `NO_OPTION_TRADE`.

## TIAF_A7 — Evaluation, Forecasting and Learning

- store recommendation before outcome
- subsequent price-path capture
- MFE / MAE
- entry quality
- exit efficiency
- confidence calibration
- deterministic baseline comparison
- human/expert comparison
- specialist performance by horizon and regime
- versioned forecast distributions and threshold probabilities
- walk-forward/out-of-sample calibration
- candidate/champion promotion and rollback

**Acceptance:** forecast calibration and Agent value versus A2 are measured
from subsequent outcomes rather than assumed or learned from Agent prose.

## TIAF_A8 — TradeMonitor Integration

- stable service/API boundary
- TM requests opportunity/position assessments
- TIAF returns timestamped advice with TTL/freshness
- TM owns risk, authority, lifecycle and execution
- TIAF never places broker orders
- degradation/health state visible to TM
- execution/outcome feedback returns to TIAF evaluation

**Acceptance:** TIAF intelligence can influence TM without crossing TM's authority boundary.

## TIAF_A9 — Scanner Integration

- Day Scanner remains a sensor/discovery system
- Positional Scanner remains a sensor/discovery system
- TIAF enriches shortlisted/full-universe candidates
- Day Scanner gains early-opportunity vs mature-mover intelligence
- Positional Scanner gains horizon-aware forward ranking
- Google Sheet can surface TIAF consensus, confidence, expected move, evidence, invalidation and timestamp
- TIAF remains independent of the user's private Sheet/bridge setup

## TIAF_A10 — Production Hardening

- provider rate-limit handling and retries
- model/provider fallbacks
- persistent cache and restart-safe assessment store
- circuit breakers for bad/stale data
- health reporting
- latency/cost telemetry
- reassessment queue/scheduler
- versioned prompts/policies
- replay tests
- load tests across realistic F&O universe sizes
- secrets/configuration hardening

## Governing Architectural Principles

- Scanners are sensors/discovery.
- Agents are interpreters/intelligence.
- TradeMonitor is governor/risk/authority/execution coordinator.
- Broker is final truth.
- Intelligence is pluggable; authority is centralized.
- Deterministic where possible, AI where judgment is valuable.
- Time horizon is a first-class input.
- `WAIT` and `NO_TRADE` are valid outcomes.
- Watchlist-only input must eventually be sufficient.
- Underlying selection and option selection are separate problems.
- For adopted positions, TIAF is forward-looking; original entry rationale is optional.
- TIAF may improve profitability, but account safety must never depend solely on AI.
