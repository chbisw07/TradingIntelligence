# TradingIntelligence Development Roadmap

**Status:** Canonical development map  
**Architecture reference:** TIAF — Trading Intelligence Agent Fabric Thesis  
**Purpose:** Preserve the implementation sequence, milestone boundaries, acceptance gates, integration contracts, and evidence-first progression for TradingIntelligence.

The post-A3 [system architecture](TIAF_SYSTEM_ARCHITECTURE.md) now governs the
logical TI_CORE and curated capability boundary. Its
[pass-1 review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md)
is followed by the approved
[source semantic architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md).
[Pass 2](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md)
is followed by the approved [A4 architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md).
[Pass 3](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md)
is followed by the completed [deployment review](TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md)
and approved [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md).
The [completed consolidation](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md)
selects bounded source foundation -> narrow local facade/lifecycle -> deterministic
A4. Its open-world amendment permits model-prior hypotheses and governed evidence
needs, never fabricated factual evidence or unbounded research. Use local Python and filesystem
replay initially; service/worker/shared-store adoption requires concrete triggers,
not a logical diagram. The separate bounded
POST_A3_PRE_A4_FOUNDATION and the subsequent narrow local facade/lifecycle were
accepted before A4 runtime; neither adds a numbered major milestone. Citation UX
remains DEF-054, not part of either prerequisite.
A3 is frozen at `tiaf-a3-baseline`; the first deterministic A4.1 slice is now an
implementation acceptance candidate. This sequence does not add or renumber an
A-milestone.

---

## 1. Roadmap Philosophy

TradingIntelligence will be developed through staged **A-milestones**. Each milestone is capability-based, independently testable, and suitable for freezing/tagging before the next stage.

The progression is deliberate:

- **TIAF_A0 — Speak Clearly**
- **TIAF_A1 — Know the Data**
- **TIAF_A2 — Establish the Baseline**
- **TIAF_A3 — Add Specialist Intelligence**
- **TIAF_A4 — Challenge and Arbitrate**
- **TIAF_A5 — Manage Positions Intelligently**
- **TIAF_A6 — Express the Trade through Options**
- **TIAF_A7 — Forecast and Prove Value**
- **TIAF_A8 — Integrate with TradeMonitor**
- **TIAF_A9 — Enrich Scanners**
- **TIAF_A10 — Harden for Production**

This order reflects the architecture:

> First establish stable contracts and factual evidence, then deterministic baselines, then AI reasoning, then measurement, and only then operational integration.

### Governing principles

- Scanners = sensors/discovery.
- Agents = intelligence/interpretation.
- TradeMonitor = governor/risk/authority/execution.
- Broker = final truth.
- Intelligence is pluggable; authority is centralized.
- Agents never place broker orders.
- Deterministic calculations remain deterministic.
- AI is reserved for ambiguity, synthesis, judgment, competing hypotheses and contextual reasoning.
- Time horizon is first-class.
- `WAIT` and `NO_TRADE` are valid.
- A supplied F&O watchlist alone must eventually be sufficient input.
- Spreadsheet features, OHLC, Greeks and scores are optional enrichment.
- Underlying selection and option selection are separate problems.
- Adopted-position management is forward-looking; original entry rationale is optional.
- Every recommendation must be timestamped, attributable, freshness-bounded and evaluable.
- AI may improve profitability; deterministic systems must preserve safety if AI fails.

---

## 2. Milestone Overview

| Milestone | Purpose | Primary Outcome |
|---|---|---|
| **TIAF_TGT0** | Initial Project Baseline | Clean professional repository skeleton |
| **TIAF_A0** | Domain Contracts + Foundation | Stable language for all future components |
| **TIAF_A1** | Data Foundation | Watchlist becomes sufficient input |
| **TIAF_A2** | Deterministic Baseline | Reproducible non-AI benchmark |
| **TIAF_A3** | Specialist Intelligence | Structured, cited underlying opportunity intelligence |
| **TIAF_A4** | Arbitration + Adversarial Review | Challenged, disagreement-aware conclusions |
| **TIAF_A5** | Position Intelligence MVP | Forward-looking adopted-position management |
| **TIAF_A6** | Option Expression Intelligence | Underlying view translated into suitable CE/PE contract |
| **TIAF_A7** | Evaluation, Forecasting + Learning | Calibrated forecasts and intelligence value measured empirically |
| **TIAF_A8** | TradeMonitor Integration | TIAF advice safely consumed operationally |
| **TIAF_A9** | Scanner Integration | Day/Pos scanners enriched with forward intelligence |
| **TIAF_A10** | Production Hardening | Long-running reliable intelligence service |

---

# TIAF_TGT0 — Initial Project Baseline

## Goal

Create a clean, professional Python project foundation without prematurely implementing trading logic or agents.

### Scope

- `tiaf` Python package
- Python 3.12+ project
- `pyproject.toml`
- baseline configuration
- `.env.example`
- `.gitignore`
- README and architecture documentation
- test structure
- lint/type-check setup
- smoke tests
- no broker SDK
- no LangGraph
- no LLM call
- no trade recommendation logic

### Acceptance

> The project installs, compiles, tests, lints and type-checks successfully, while containing no live trading or agent behavior.

**Status: COMPLETE / FROZEN**  
**Tag:** `tiaf-tgt0`

---

# TIAF_A0 — Domain Contracts and Foundation

## Goal

Define the stable domain language that Planner, Agents, Data Service, TradeMonitor, scanners and third parties will use.

### Scope

Core contracts should include:

- `OpportunityRequest`
- `PositionRequest`
- `EvidenceItem`
- `DataSnapshot`
- `AgentOpinion`
- `AgentDecisionBundle`
- `OpportunityAssessment`
- `PositionAssessment`
- `OptionExpression`

Core enums should include concepts for:

- trade style
- flexible time-horizon semantics
- direction policy
- trade direction
- opportunity action
- position-management action
- action strength
- confidence band
- evidence type
- evidence source
- freshness state
- data quality / availability

Foundation should also include:

- request/assessment/snapshot identifiers
- timezone-aware timestamps normalized to canonical `Asia/Kolkata`
- schema versioning
- serialization/deserialization
- validation
- backward-compatibility policy
- error taxonomy

### Non-goals

- no LangGraph workflow
- no LLM call
- no Dhan/Zerodha integration
- no market prediction
- no broker execution

### Acceptance

> All contracts are versioned, validated and serializable; invalid inputs fail clearly; the contracts depend on neither TradeMonitor internals nor Google Sheet layout.

---

# TIAF_A1 — Data Foundation

**Status: COMPLETE / BASELINED**

**Baseline tag: `tiaf-a1.7`**

## Goal

Make a watchlist sufficient input by centralizing factual data acquisition, normalization and derived context.

### Scope

- provider-neutral interfaces
- Dhan and/or Zerodha provider adapters
- quote retrieval
- historical OHLCV
- intraday candles
- instrument master / symbol resolution
- derivatives metadata
- market/index context
- sector/peer context
- option-chain/OI/IV data where available
- public news/filings/event sources
- canonical `Asia/Kolkata` timezone and aware timestamps
- cache with explicit TTL
- freshness and stale-data state
- optional user enrichment ingestion
- provider fallback
- partial-data behavior
- `AnalysisContext`

### Architectural rule

Agents do not independently hammer provider APIs. The Data Service obtains evidence once and shares a consistent snapshot.

### Acceptance

> Given only a list of F&O symbols, TradingIntelligence can build internally
> consistent, timestamped factual contexts or explicitly return
> partial/deferred/error outcomes.

The accepted A1 implementation covers provider-neutral contracts, Dhan
quote/history/live and historical-option facts, symbol-first resolution, the
in-process data runtime, and `AnalysisContext`. Broader items in the original
scope—secondary-provider fallback, news/filings, fundamentals, sector/peer
context, persistent caching, and retry orchestration—remain intentionally
deferred. See `TIAF_A1_FOUNDATION_BASELINE.md` for the binding A1 boundary.

---

# TIAF_A2 — Deterministic Baseline

**Status: COMPLETE / BASELINED** at tag `tiaf-a2-baseline`

## Goal

Build a transparent non-AI benchmark that future Agents must beat.

### Scope

- deterministic feature and first-class indicator contracts/engines
- change %
- gap
- ATR / ATR%
- Move/ATR
- daily/weekly range consumption
- relative volume
- VWAP context where applicable
- trend
- momentum
- volatility regime
- support/resistance
- relative strength vs NIFTY/index
- relative strength vs sector
- multi-timeframe features
- horizon-specific bullish/bearish baseline scoring
- candidate classes: `TOP_MOVER`, `EARLY_OPPORTUNITY`, `MATURE_AVOID_CHASE`, `NO_TRADE`

### Detailed implementation sequence

1. **A2.1 — Feature Contracts + Engine Foundation** — COMPLETE / LIVE VALIDATED
2. **A2.2 — Price / Return / Volatility Features** — COMPLETE / LIVE VALIDATED
3. **A2.3 — Trend & Structure Features** — COMPLETE / LIVE VALIDATED
4. **A2.4 — Indicator Framework + Initial Indicator Library** — COMPLETE / LIVE VALIDATED
5. **A2.5 — Volume / Participation Features** — COMPLETE / LIVE VALIDATED
6. **A2.6 — Support / Resistance / Breakout Structure** — COMPLETE / LIVE VALIDATED
7. **A2.7 — Derivatives / Option-Chain Features** — COMPLETE / LIVE VALIDATED
8. **A2.8 — Relative Strength, Benchmark & Multi-Timeframe Context** — COMPLETE / LIVE VALIDATED
9. **A2.9 — Deterministic Market-State / Feature Summary** — COMPLETE / LIVE VALIDATED
10. **A2.10 — Replay / Validation / Baseline Evaluation** — COMPLETE / LIVE VALIDATED

A2.4 was inserted before the previously planned feature families because
indicators need a stable reusable abstraction for scanners, strategy engines,
Agents, replay/backtesting, parameter optimization, UI/dashboard applications,
and proprietary extensions. Indicators do not replace A2.3 primitives: the
two are complementary deterministic evidence layers. This insertion shifts
the former A2.4–A2.9 detailed targets to A2.5–A2.10; major phases A3 through
A10 are unchanged.

### Important objective

The baseline should be able to distinguish a stock already +4.5% but with limited remaining opportunity from a stock only +0.5% to +2% with evidence that a larger move may still be ahead.

### Acceptance

> The same market snapshot produces the same ranking; the baseline can surface early-opportunity candidates and can return NO TRADE.

**A2.9 result:** the version 1.0 reproducible non-AI ranking benchmark is now
implemented and live-validated. A2.10 adds replay/evaluation rather than
replacing or silently recalibrating it.

**A2.10 implementation:** complete normalized evidence snapshots and immutable
decision records now support exact provider-free replay, same-evidence policy
comparison, later raw outcome/MFE/MAE measurement, frozen-ranking statistics,
append-only filesystem corpora, and deterministic regressions. User-level live
capture/replay validation succeeded. The governed A2 closure is recorded in
`TIAF_A2_FOUNDATION_BASELINE.md` and `TIAF_A2_ACCEPTANCE_REPORT.md`; the accepted
major tag is `tiaf-a2-baseline`.

---

# TIAF_A3 — Specialist Intelligence

**Status: A3.1-A3.10 ACCEPTED THROUGH `tiaf-a3.10`; MAJOR CLOSURE
`READY_TO_FREEZE_A3`**

## Goal

Introduce evidence-grounded, cost-disciplined specialist interpretation after
factual data and deterministic judgment are dependable, without weakening or
replacing the A2 benchmark.

### Specialist capabilities

- Technical / Market Structure
- Fundamental / Company Quality
- News / Catalyst / Event
- Relative Context
- Sector / Rotation Context
- Macro Context
- Derivatives Context
- Opportunity Risk
- Contrarian Hypothesis Challenger
- Forecast Interpretation, only when calibrated forecast evidence exists

### Planner responsibilities

- understand requested instrument, purpose, style, and horizon
- decide what evidence is necessary
- choose which specialist capabilities to invoke
- request missing evidence through controlled, least-privilege gateways
- control analysis, model, token, tool, latency, specialist, and cost budgets
- allow insufficient-evidence and abstaining conclusions
- avoid unnecessary deep research on every symbol
- preserve separate opinions, citations, A2 comparison, and run/usage records
- leave conflict resolution to A4

### Detailed implementation sequence

1. **A3.1 — Agent Contracts and Provider-Neutral Runtime Foundation** — COMPLETE / ACCEPTED
2. **A3.2 — Controlled Evidence, Reasoning, and Budget Gateways** — COMPLETE / ACCEPTED
3. **A3.3 — Technical and Market Structure Specialist** — COMPLETE / ACCEPTED
4. **A3.4 — Fundamental Evidence and Company Quality Specialist** — COMPLETE / ACCEPTED
5. **A3.5 — News, Filing, Catalyst, and Event Intelligence** — COMPLETE / ACCEPTED
6. **A3.6 — Relative, Sector, and Macro Context Specialists** — COMPLETE / ACCEPTED
7. **A3.6.1 — Market Intelligence Provider Fabric + Deep Research Foundation** — IMPLEMENTED / DETERMINISTIC ACCEPTANCE COMPLETE
8. **A3.6.2 — Market Intelligence / Deep Research Integration** — COMPLETE / ACCEPTED
9. **A3.7 — Derivatives Context and Opportunity Risk Specialists** — COMPLETE / ACCEPTED
10. **A3.8 — Instrument-Aware Planner and Specialist Orchestration** — COMPLETE / ACCEPTED
11. **A3.9 — Structured Underlying Opportunity Intelligence MVP** — COMPLETE / ACCEPTED
12. **A3.10 — Agent Replay, Baseline Comparison, Cost, and Failure Hardening** — COMPLETE / ACCEPTED

The authoritative decisions and milestone gates are in
`TIAF_A3_ARCHITECTURE.md` and `TIAF_A3_DETAILED_ROADMAP.md`.
The A3.1 implementation record is `TIAF_A3_1_AGENT_FOUNDATION.md`; the A3.2
gateway/budget record is `TIAF_A3_2_GATEWAYS_BUDGETS.md`; and the A3.3
specialist record is `TIAF_A3_3_TECHNICAL_SPECIALIST.md`. A3.6 implementation
and its explicit mapping/provider limits are recorded in
`TIAF_A3_6_RELATIVE_SECTOR_MACRO_INTELLIGENCE.md`.
The A3.4 implementation record is `TIAF_A3_4_FUNDAMENTAL_INTELLIGENCE.md`.
The A3.5 implementation record is `TIAF_A3_5_NEWS_EVENT_INTELLIGENCE.md`.
The A3.6.1 provider-fabric design and implementation record is
`TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md`; its isolated read-only
Tapetide connector is complete and the adapter-to-replay path was exercised.
Final live acceptance remains on HOLD because the daily Tapetide quota was
exhausted before the ATHERENERG financial diagnostic could observe a raw
response. Its Tapetide study is non-authoritative reference evidence, not
provider-defined architecture.

Yahoo's separate ten-call fallback matrix, the bounded authoritative gateway,
and A3.6.2's 12-call integrated matrix are live-validated. A3.7-A3.10 and their
limits are recorded in the detailed roadmap and the
[A3 major closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md). The
Tapetide `HOLD` remains a truthful provider-specific historical result.

### Output

For a bounded A2-screened candidate set, produce zero or more ranked,
structured underlying-opportunity records containing identity, horizon,
directional specialist stances, evidence-linked interpretations, entry-state
and invalidation concepts, missing evidence, quality/freshness, separated
confidence dimensions, specialist disagreement, run provenance, and explicit
A2 comparison. `WAIT`, `NO_TRADE`, `ABSTAIN`, and insufficient evidence remain
valid. A3 does not emit `CE`/`PE`; A6 owns option expression.
Any A3 ordering preserves A2 or another explicit non-arbitrating policy; A4
owns final intelligence-aware ranking and recommendation.

### Acceptance

> TIAF produces replayable, cited specialist and underlying-opportunity
> intelligence under explicit budgets, with no final arbitration, option
> expression, position action, or broker execution.

---

# TIAF_A4 — Arbitration and Adversarial Review

**Architecture approved; deterministic A4.1 implemented as an acceptance
candidate.** See the
[A4 challenge/arbitration architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md)
and [pass-3 decision](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md).
The separate [source-semantic foundation](TIAF_POST_A3_PRE_A4_FOUNDATION.md) is
implemented and accepted. The selected facade track is implemented and accepted as the
[narrow local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md). The bounded
[A4.1 implementation](TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md) adds the
deterministic roles, seven dispositions, replay and `a4.evaluate`; it adds no
live capability, model, evidence acquisition, Shell or service.

## Goal

Prevent a single Agent from becoming an oracle and make disagreement explicit.

### Scope

- unified Thesis Challenger: counter-thesis, evidence/assumption and risk critique
- explicit deterministic Arbitrator with optional selective model proposals
- scoped evidence admission, source independence, horizon and freshness checks
- argument-based resolution without voting, averaged confidence or source/model prestige
- separate evidence quality, thesis support, challenge severity and residual uncertainty
- `SUPPORTIVE`, `WAIT`, `NO_TRADE`, `AVOID`, `CONFLICTED`, `ABSTAIN`, `INSUFFICIENT_EVIDENCE`
- unchanged A2/A3 records, original A2 NO_TRADE and preserved dissent
- bounded semantic evidence needs through existing Planner/gateway boundaries
- recorded model replay, deterministic verification, cost/failure lineage

### Principle

Strong disagreement is itself information. A nominally bullish candidate may be downgraded to WAIT rather than forced into CE.

### Acceptance

> Every A4 disposition exposes its surviving or rejected thesis, evidence-linked
> challenges, dissent, invalidation conditions and residual uncertainty. No-LLM
> execution remains supported; no position/expression/execution authority moves
> into A4. A4.1 acceptance uses the explicit 25-scenario implementation matrix
> and failure/replay gates; governed evidence acquisition and optional model
> challenge remain later slices.

---

# TIAF_A5 — Position Intelligence MVP

Entry remains accepted A4 and versioned position context, not A6/A7 or a daemon.
Before implementation, review bounded WatchMandate/lifecycle, evidence-family
clocks and delta semantics; first delivery can be on-demand. TM owns actual
position state and operational priority. Durable scheduling remains gated
separately. Shell v0.1 is useful before A5 but not a hard dependency.

## Goal

Support TradeMonitor's most important generic use case: an existing broker position is adopted and needs intelligent forward-looking management.

### Core question

> If I owned this position right now, should I continue owning it?

### Scope

- position assessment request
- original entry rationale optional
- current-state analysis
- multi-timeframe technical structure
- market/sector/peer context
- momentum/volume/relative strength
- company/industry/news/event context
- volatility and expiry context
- current P&L and remaining opportunity
- action: `HOLD`, `WATCH_CLOSELY`, `PROTECT`, `PARTIAL_BOOK`, `BOOK`, `EXIT`
- strength: `MILD`, `MODERATE`, `STRONG`, `URGENT`
- confidence
- stateful reassessment
- changed-since-previous explanation

### Reassessment triggers

- elapsed time
- price milestone
- P&L milestone
- support/resistance break
- volatility change
- sector move
- material company/industry/policy/geopolitical news
- expiry proximity
- explicit TradeMonitor request

### Acceptance

> An adopted position can be monitored and re-evaluated without reconstructing the original thesis, and TIAF can provide structured HOLD/PROTECT/BOOK/EXIT advice.

---

# TIAF_A6 — Option Expression Intelligence

Two delivery tracks under A6/DEF-006: deterministic admissible candidates first;
forecast-enhanced comparison only after admitted A7 evidence. A5 still precedes
A6 because existing adopted positions need advice without new option selection.

## Goal

Translate a validated underlying opportunity into an appropriate option contract.

### Scope

- select expiry consistent with horizon
- compare ATM / ITM / OTM
- delta
- theta
- IV
- liquidity
- bid/ask spread
- OI / option volume
- event exposure
- expected underlying move vs option cost only in the A7-informed follow-up
- reject unattractive option expression

### Important separation

`Is KAYNES bullish?` and `Which KAYNES CE should express that view?` are separate analytical questions.

### Acceptance

> TIAF can recommend a preferred CE/PE option, alternatives, and reasons—or return `NO_OPTION_TRADE`.

Initial deterministic acceptance proves candidate validity, explicit policy/risk/
liquidity/payoff assumptions and alternatives, not calibrated expected move, POP
or optimized utility. Later higher-order reasoning may compare only A6-produced
valid candidate IDs under admitted A7 forecasts; it neither manufactures
contracts nor moves A6 selection, A7 calibration or TM authority into initial A4.

---

# TIAF_A7 — Evaluation, Forecasting and Learning

Architecture entry requires stable deterministic A4 and A5/A6 records, outcome
definitions, permitted PIT datasets and baseline/null-model controls. Keep A7
after initial deterministic A6; its outputs enable a separately versioned A6
forecast-enhanced follow-up. Cross-candidate A3/A4 comparison/ranking (DEF-053)
belongs in this evaluated scope, not an earlier unexplained leaderboard.

## Goal

Produce and calibrate first-class probabilistic forecasts, and prove whether
TIAF improves decisions instead of merely producing convincing explanations.

### Scope

- persist recommendation before outcome
- capture subsequent underlying/option path
- MFE
- MAE
- realized/virtual outcome
- entry quality
- exit efficiency
- confidence calibration
- deterministic baseline comparison
- human/expert comparison
- performance by horizon
- performance by market regime
- specialist Agent scorecards
- future evidence-based arbitration weighting
- versioned forecast models and immutable forecast evidence
- return/price distributions and threshold probabilities with calibration
- walk-forward and out-of-sample validation
- candidate/champion promotion and rollback
- universe/horizon-compatible cross-candidate comparison with selection-bias,
  missing-candidate and tie policy; preserve A2 ranking as benchmark

Ensembles/optimization/learning remain conditional on out-of-sample evidence,
not a mandatory hierarchy. Captured prospective evaluation is valid within its
scope; it does not close arbitrary historical PIT reconstruction (DEF-049).
Model-backed Challenger engineering may precede A7 after separate role-aware
gateway/privacy/pricing/replay/evaluation gates (DEF-052/055); this does not
generate calibrated forecasts or require models for deterministic A4.

### Acceptance

> Forecasts are empirically calibrated and TIAF's contribution can be
> quantified against deterministic and human benchmarks without self-training
> from its own prose.

---

# TIAF_A8 — TradeMonitor Integration

## Goal

Connect intelligence to TradeMonitor without transferring authority.

### Flow

`TIAF → structured advice → TradeMonitor → freshness → RM → authority → lifecycle → execution → broker → reconciliation`

### Scope

- consumer integration through the governed capability boundary (DEF-003):
  local contracts/facade may be established post-A3 before Shell/public use;
  A8 delivers TM integration and remote service/API transport as required,
  without a second intelligence implementation
- opportunity assessment requests
- adopted-position assessment requests
- TTL/freshness validation
- structured degradation state
- health reporting
- no direct broker order capability
- TM outcome/execution feedback to evaluation harness
- source/provenance preservation

Hosting follows the [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md):
library calls suit trusted prototypes; a separate local TI host is preferred
for operational TM failure/credential isolation. Remote transport requires a
cross-host need and security/compatibility acceptance, not merely this milestone.
TM retains broker credentials and position/restart reconciliation.

### Authority rule

TIAF never places, modifies or cancels broker orders.

### Acceptance

> TradeMonitor can safely consume TIAF intelligence while preserving its own RM, User, lifecycle and execution authority.

---

# TIAF_A9 — Scanner Integration

## Goal

Enhance existing scanners without collapsing their identity into TIAF.

### Day Scanner

Add forward-looking views such as `TOP_MOVERS`, `EARLY_OPPORTUNITIES`, `MATURE_AVOID_CHASE`, CE/PE/WAIT/NO-TRADE, expected remaining move, confidence and key evidence.

### Positional Scanner

Add horizon-aware opportunity ranking, multi-day/multi-week structure, sector/cycle/fundamental context, catalyst/event intelligence and forward risk/reward.

### Google Sheet

May display TIAF consensus, confidence, expected move, invalidation, evidence summary, last assessment, assessment freshness and recommendation state.

### Independence rule

TIAF must also work for users who do not have the user's Google Sheet scanners or bridge.

### Acceptance

> Existing scanners can consume TIAF intelligence while remaining independently useful and loosely coupled.

---

# TIAF_A10 — Production Hardening

## Goal

Make TradingIntelligence a dependable long-running service.

### Scope

- provider rate limits
- retries/backoff
- data-source fallback
- stale-data circuit breakers
- model fallback
- agent timeout policy
- persistent cache
- restart-safe assessment memory
- assessment scheduler/queue
- structured health reporting
- latency/cost telemetry
- versioned prompts/policies
- secret hygiene
- load testing
- historical replay
- failure injection
- operational observability

Deliver durable jobs/storage, health/SLOs and recovery where operating requirements
justify them. Earlier exposed consumers need the minimal admission, lifecycle,
security and publication gates first; this does not move the entire A10 stack
before A4. No mandatory database vendor, distributed topology, Docker or
Kubernetes is selected by the deployment review.

### Acceptance

> TIAF can run continuously, degrade safely, recover predictably, and explain what evidence/services are unavailable.

---

## 3. Progressive Analysis Strategy

Deep AI research on every F&O stock every minute is neither necessary nor desirable.

The intended funnel is:

`bounded universe → deterministic screening → candidate pool → fast specialist pass → serious candidates → selective deep research → bounded eligible set`

The same principle applies to open positions:

`continuous deterministic monitoring → meaningful trigger → Agent reassessment`

This preserves cost, latency and provider limits while focusing AI effort where judgment adds value.

---

## 4. Preservation and Change Control

This roadmap is a canonical reference artifact and should live in the repository `docs/` folder.

Recommended files:

- `docs/TIAF_THESIS.md`
- `docs/TRADINGINTELLIGENCE_ROADMAP.md`
- `docs/MILESTONES.md`
- optionally polished Word copies for human review

Changes should be deliberate. If implementation reveals a genuine architectural need, update the roadmap and record why. Do not silently redefine an accepted milestone.

Each accepted target should be committed and tagged so the project always has a known-good return point.

Suggested tags:

- `tiaf-tgt0`
- `tiaf-a0`
- `tiaf-a1`
- ...
- `tiaf-a10`

### Major-milestone deferral review

Deferrals are recorded as they arise without interrupting every sub-milestone.
At closure of each **major milestone**—A2, A3, A4, and so on—the closure record
must review the stable IDs in `TIAF_DEFERRAL_REGISTER.md` and report:

- deferrals introduced;
- deferrals implemented;
- deferrals rejected;
- deferrals superseded;
- deferrals carried forward, with rationale;
- remaining high-priority deferrals.

The review must attempt items whose dependencies have become satisfied and
carry forward only genuinely unresolved work. It does not run after every
A2.x/A3.x sub-milestone, and the register does not override roadmap order.

---

## 5. Reference Summary

**TGT0 — ESTABLISH THE PROJECT**  
Create the clean repository and engineering baseline.

**A0 — SPEAK CLEARLY**  
Define stable domain contracts.

**A1 — KNOW THE DATA**  
Acquire and normalize the evidence.

**A2 — ESTABLISH THE BASELINE**  
Create deterministic benchmark intelligence.

**A3 — ADD SPECIALISTS**  
Introduce contextual AI reasoning.

**A4 — CHALLENGE THE ANSWER**  
Make disagreement and evidence explicit.

**A5 — MANAGE THE POSITION**  
Provide forward-looking adopted-position intelligence.

**A6 — EXPRESS THROUGH OPTIONS**  
Choose or reject the CE/PE contract.

**A7 — FORECAST AND PROVE VALUE**
Produce calibrated forecasts and measure whether intelligence improves decisions.

**A8 — SERVE TRADEMONITOR**  
Integrate intelligence without surrendering authority.

**A9 — ENRICH SCANNERS**  
Improve Day/Positional discovery with forward intelligence.

**A10 — HARDEN**  
Make the service reliable for continuous use.

---

> **Intelligence is pluggable; authority is centralized.**

> **Agents may improve profitability, but account safety must never depend solely on AI.**

This roadmap should always be read together with the TIAF architecture thesis.
