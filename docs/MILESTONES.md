# Milestones

The canonical roadmap is maintained in:

- `TRADINGINTELLIGENCE_ROADMAP.md`
- `TradingIntelligence_TIAF_Implementation_Roadmap.docx`

The initial repository bootstrap milestone `TIAF_TGT0` is complete and frozen. The active development sequence now proceeds through the TIAF implementation roadmap.

## Current Development Position

**TIAF_TGT0 — Initial Project Baseline: COMPLETE / FROZEN**

- Professional Python project skeleton created
- `tiaf` package established
- baseline configuration, documentation, tests, linting and typing checks added
- no trading logic, broker integration, LLM calls, or agent workflows introduced
- tag: `tiaf-tgt0`

**Active:** TIAF_A1 — Data Foundation. Current sub-target: **TIAF_A1.6 —
Cache, Freshness & Provider Scheduling**.

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

## TIAF_A1 — Data Foundation — ACTIVE

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

**Current:** TIAF_A1.6 — Cache, Freshness & Provider Scheduling

- provider-neutral in-process factual cache and deterministic cache keys
- caller-relative freshness with visible `FRESH` / `AGING` / `STALE` / `UNKNOWN`
- monotonic provider scheduling with explicit non-sleeping eligibility decisions
- key-scoped request coalescing and opt-in bounded stale-on-error fallback
- documented Dhan quote and option-chain constraints outside generic runtime
- no background queues, Intelligence OS, Agents, recommendations, or execution

Later A1 sub-targets add provider adapters, resolution, caching, shared context,
and fallback behavior.

- provider-neutral market-data interfaces
- Dhan and/or Zerodha adapters as appropriate
- quote and historical OHLCV acquisition
- instrument/symbol resolution
- normalized timestamps/time zones
- shared cache and freshness/TTL
- optional enrichment ingestion
- `AnalysisContext` construction
- provider fallbacks and stale/partial-data visibility

**Acceptance:** a watchlist alone can be converted into timestamp-consistent analysis contexts or clearly marked missing/stale evidence.

## TIAF_A2 — Deterministic Baseline

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

## TIAF_A3 — Planner + Specialist Agent MVP

Initial specialist set:

- Technical Structure
- Relative Strength
- Sector / Rotation
- News / Catalyst
- Risk
- Contrarian

The Planner decides which evidence and specialists are needed for the requested horizon and task. Agents consume shared normalized data rather than independently calling broker/data APIs.

**Acceptance:** a 10–20 symbol universe can produce structured 0–5 opportunity assessments with CE/PE/WAIT/NO-TRADE conclusions, confidence, expected remaining move, invalidation and evidence.

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

## TIAF_A7 — Evaluation and Learning Harness

- store recommendation before outcome
- subsequent price-path capture
- MFE / MAE
- entry quality
- exit efficiency
- confidence calibration
- deterministic baseline comparison
- human/expert comparison
- specialist performance by horizon and regime

**Acceptance:** Agent value is measured rather than assumed.

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
