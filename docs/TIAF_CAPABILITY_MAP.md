# TIAF Capability Map

This is an architectural placement inventory, not an implementation schedule.
Statuses describe repository reality:

- **IMPLEMENTED** — accepted code/contracts exist;
- **PLANNED** — placed on the current deterministic roadmap;
- **FUTURE** — recognized capability without a committed near-term milestone;
- **EXTERNAL/INTEGRATION** — owned by or dependent on another system boundary.

## Data and evidence

| Capability | Status | Placement |
|---|---|---|
| Quote / OHLC | IMPLEMENTED | A1 normalized data and context |
| Historical bars | IMPLEMENTED | A1 normalized data and context |
| Derivative identity / expiries | IMPLEMENTED | A1 data foundation |
| Live option chain | IMPLEMENTED | A1 data foundation |
| Historical options | IMPLEMENTED | A1 data foundation |
| Provider-reported Greeks | IMPLEMENTED | A1 live option-chain facts |
| IV / OI / option volume | IMPLEMENTED | A1 option facts |
| Cash-history volume | IMPLEMENTED | A1 OHLCV fact; analysis is A2.5 |
| Liquidity analysis | PLANNED | A2 derivatives/participation extensions |
| News / filings | FUTURE | External evidence adapters |
| Fundamentals | FUTURE | External evidence adapters |
| Corporate actions | FUTURE | Data normalization and adjustment policy |
| Sector / index / macro context | FUTURE | Shared contextual evidence |

## Deterministic analysis

| Capability | Status | Placement |
|---|---|---|
| Price / return / volatility | IMPLEMENTED | A2.1–A2.2 features |
| Trend / structure primitives | IMPLEMENTED | A2.3 features |
| Indicator framework and initial library | IMPLEMENTED | A2.4 |
| Volume / participation primitives | IMPLEMENTED | A2.5 completed-history features |
| Support / resistance primitives | IMPLEMENTED | A2.6 fixed prior boundaries |
| Prior-boundary breakout primitives | IMPLEMENTED | A2.6 close/wick excursions |
| Range compression / expansion | IMPLEMENTED | A2.6 prior/latest range geometry |
| Swing pivots / fractals | FUTURE | Requires confirmation-time semantics |
| Classic floor pivots | FUTURE | Level/Indicator extension with session semantics |
| Multi-timeframe levels | PLANNED | A2.8 |
| Support / resistance scoring | FUTURE | Later deterministic interpretation |
| Breakout quality scoring | FUTURE | A2.9 or later strategy layer |
| Failed-breakout classification | FUTURE | Market-state/replay event semantics |
| Derivatives deterministic features | PLANNED | A2.7 |
| Relative strength | FUTURE | Deterministic contextual analysis |
| Sector rotation | FUTURE | Deterministic contextual analysis |
| Multi-timeframe context | PLANNED | A2.8 |
| Market-state summary | PLANNED | A2.9 |
| Replay / baseline evaluation | PLANNED | A2.10 |

## Indicators

| Capability | Status | Placement |
|---|---|---|
| SuperTrend | IMPLEMENTED | A2.4 library |
| RSI | IMPLEMENTED | A2.4 library |
| MACD | IMPLEMENTED | A2.4 library |
| ADX / +DI / -DI | IMPLEMENTED | A2.4 library |
| Bollinger Bands | IMPLEMENTED | A2.4 library |
| Donchian Channel | IMPLEMENTED | A2.4 library |
| OBV | FUTURE | Indicator-library extension |
| MFI | FUTURE | Indicator-library extension |
| Chaikin / Accumulation-Distribution | FUTURE | Indicator-library extension with named variant |
| Session VWAP | FUTURE | Indicator extension with explicit intraday sessions |
| Anchored VWAP | FUTURE | Indicator extension with explicit anchor contract |
| Volume profile | FUTURE | Deterministic analysis with explicit binning semantics |
| Market profile | FUTURE | Deterministic analysis with explicit session/binning semantics |
| Delivery / participant statistics | FUTURE | Requires normalized provider evidence |
| HalfTrend | FUTURE | Deferred pending a named canonical variant |
| Future / proprietary indicators | FUTURE | Explicit registry extensions |

## Derivatives intelligence

| Capability | Status | Placement |
|---|---|---|
| Option-chain factual structure | IMPLEMENTED | A1 evidence |
| Greeks / IV / OI facts | IMPLEMENTED | A1 evidence |
| Skew / term structure | PLANNED | A2.7 |
| Expected move | PLANNED | A2.7 |
| Derivative liquidity measurements | PLANNED | A2.7 |
| Expiry-effect analysis | FUTURE | Later deterministic/Agent evidence |

## Option strategy library

All are **FUTURE** under Option Expression Intelligence rather than A2.4:
long call, long put, bull call spread, bear put spread, bull put spread, bear
call spread, straddle, strangle, iron condor, iron butterfly, butterflies,
calendars, diagonals, ratio spreads, and defined-risk variants.

## Rule and policy layer

| Capability | Status | Placement |
|---|---|---|
| SigmaDSL integration | FUTURE | Rule/strategy policy boundary |
| Strategy entry/exit rules | FUTURE | Separate from indicator evidence |
| Parameter optimization | FUTURE | Replay/evaluation boundary |

## Agent intelligence

Opportunity analysis, position management, strategy comparison/selection,
sector rotation, scanner intelligence, explanation, and scenario analysis are
all **FUTURE** Agent-layer capabilities beginning at A3. They consume evidence;
they do not belong inside deterministic calculators.

## Applications

| Capability | Status | Placement |
|---|---|---|
| Read-only console diagnostics | IMPLEMENTED | Milestone smoke scripts |
| Monitoring daemon / intelligence OS | FUTURE | Application/runtime layer |
| Scanner | EXTERNAL/INTEGRATION | Future TIAF scanner boundary |
| UI / dashboard | FUTURE | Application layer |
| API / service | FUTURE | Service boundary |
| Alerts | FUTURE | Application/policy layer |
| Replay / backtest | PLANNED | A2.10 foundation, later strategy use |
| Optimization | FUTURE | Evaluation layer |
| Watchlists | EXTERNAL/INTEGRATION | Input source consumed through A1 |

## Governance and execution

| Capability | Status | Placement |
|---|---|---|
| TradeMonitor intelligence contract | EXTERNAL/INTEGRATION | A8 integration boundary |
| Risk, authority, lifecycle, execution | EXTERNAL/INTEGRATION | TradeMonitor owns |
| Broker execution | EXTERNAL/INTEGRATION | Outside deterministic analysis |

TIAF indicators and features never place orders. Primitive features,
indicators, future strategies, Agent reasoning, and execution authority remain
distinct architectural layers.
