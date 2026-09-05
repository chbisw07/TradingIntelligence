# TradingIntelligence Development Roadmap

**Status:** Canonical development map  
**Architecture reference:** TIAF — Trading Intelligence Agent Fabric Thesis  
**Purpose:** Preserve the implementation sequence, milestone boundaries, acceptance gates, integration contracts, and evidence-first progression for TradingIntelligence.

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
- **TIAF_A7 — Prove Value**
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
| **TIAF_A3** | Planner + Specialist Agent MVP | Structured opportunity intelligence |
| **TIAF_A4** | Arbitration + Adversarial Review | Challenged, disagreement-aware conclusions |
| **TIAF_A5** | Position Intelligence MVP | Forward-looking adopted-position management |
| **TIAF_A6** | Option Expression Intelligence | Underlying view translated into suitable CE/PE contract |
| **TIAF_A7** | Evaluation + Learning Harness | Intelligence value measured empirically |
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

> Given only a list of F&O symbols, TradingIntelligence can build internally consistent, timestamped analysis contexts or explicitly state what evidence is missing/stale.

---

# TIAF_A2 — Deterministic Baseline

## Goal

Build a transparent non-AI benchmark that future Agents must beat.

### Scope

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

### Important objective

The baseline should be able to distinguish a stock already +4.5% but with limited remaining opportunity from a stock only +0.5% to +2% with evidence that a larger move may still be ahead.

### Acceptance

> The same market snapshot produces the same ranking; the baseline can surface early-opportunity candidates and can return NO TRADE.

---

# TIAF_A3 — Planner + Specialist Agent MVP

## Goal

Introduce contextual reasoning after factual data and deterministic features are dependable.

### Initial Agent set

- Technical Structure Agent
- Relative Strength Agent
- Sector / Rotation Agent
- News / Catalyst Agent
- Risk Agent
- Contrarian Agent

### Planner responsibilities

- understand requested trading style and horizon
- decide what evidence is necessary
- choose which specialist Agents to invoke
- request missing evidence through the Data Service
- control analysis budget and latency
- allow insufficient-evidence conclusions
- avoid unnecessary deep research on every symbol

### Output

For a 10–20 stock input set, produce 0–5 ranked opportunities containing symbol, CE/PE/WAIT/NO_TRADE, horizon, opportunity score, confidence, expected remaining move, preferred entry state, invalidation, evidence summary, specialist opinions and disagreement.

### Acceptance

> TIAF produces structured opportunity intelligence with evidence and no broker execution.

---

# TIAF_A4 — Arbitration and Adversarial Review

## Goal

Prevent a single Agent from becoming an oracle and make disagreement explicit.

### Scope

- independent bullish case
- independent bearish/contrarian case
- risk challenge
- evidence-quality weighting
- horizon relevance
- freshness weighting
- confidence formation
- disagreement metric
- `WAIT` / `NO_TRADE`
- persistence of specialist opinions
- unsupported factual-claim downgrading

### Principle

Strong disagreement is itself information. A nominally bullish candidate may be downgraded to WAIT rather than forced into CE.

### Acceptance

> Every final recommendation exposes the evidence, dissent, confidence and freshness behind the decision.

---

# TIAF_A5 — Position Intelligence MVP

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
- expected underlying move vs option cost
- reject unattractive option expression

### Important separation

`Is KAYNES bullish?` and `Which KAYNES CE should express that view?` are separate analytical questions.

### Acceptance

> TIAF can recommend a preferred CE/PE option, alternatives, and reasons—or return `NO_OPTION_TRADE`.

---

# TIAF_A7 — Evaluation and Learning Harness

## Goal

Prove whether TIAF improves decisions instead of merely producing convincing explanations.

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

### Acceptance

> TIAF's contribution can be quantified and compared against deterministic and human benchmarks.

---

# TIAF_A8 — TradeMonitor Integration

## Goal

Connect intelligence to TradeMonitor without transferring authority.

### Flow

`TIAF → structured advice → TradeMonitor → freshness → RM → authority → lifecycle → execution → broker → reconciliation`

### Scope

- local service/API boundary
- opportunity assessment requests
- adopted-position assessment requests
- TTL/freshness validation
- structured degradation state
- health reporting
- no direct broker order capability
- TM outcome/execution feedback to evaluation harness
- source/provenance preservation

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

### Acceptance

> TIAF can run continuously, degrade safely, recover predictably, and explain what evidence/services are unavailable.

---

## 3. Progressive Analysis Strategy

Deep AI research on every F&O stock every minute is neither necessary nor desirable.

The intended funnel is:

`F&O universe → deterministic screening → candidate pool → fast specialist pass → serious candidates → deep research/debate → final 0–5`

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

**A7 — PROVE VALUE**  
Measure whether the Agents actually improve decisions.

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
