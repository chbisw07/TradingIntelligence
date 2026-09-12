# TIAF Capability Map

This is an architectural placement inventory, not an implementation schedule.
It is also not an executable public capability registry. Public, engineering
and private interface rules are defined in the
[system architecture](TIAF_SYSTEM_ARCHITECTURE.md), with current code seams
classified in the [post-A3 pass-1 review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md).
The [consolidated transition plan](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md)
selected foundation -> narrow local facade/lifecycle -> deterministic A4. All
three are implemented, and the
[A4 major closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) finds the combined
A4.1/A4.2 layer frozen at `tiaf-a4-baseline`. The approved
[TI_SHELL architecture](TIAF_TI_SHELL_ARCHITECTURE.md) is implemented as the
current local consumer boundary. The
[A5 architecture](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md) is approved,
and its bounded A5.1 internal runtime is implemented without facade/Shell
publication. A7 later informs a separately
versioned forecast-enhanced A6 follow-up; no major milestone is renumbered.

Statuses describe repository reality:

- **IMPLEMENTED** — accepted code/contracts exist;
- **PLANNED** — placed on an explicit future roadmap milestone;
- **DEFERRED** — recorded with an unresolved prerequisite in the
  [deferral register](TIAF_DEFERRAL_REGISTER.md);
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
| Option-chain bid/ask liquidity primitives | IMPLEMENTED | A2.7 factual ATM spreads |
| News / filings | IMPLEMENTED | A3.5 point-in-time event contracts, deterministic clustering, bounded caller-supplied/test adapter, and controlled reads; production licensed adapter remains DEF-012 |
| Fundamentals | IMPLEMENTED | A3.4 point-in-time contracts, deterministic metrics, bounded caller-supplied/test adapter and controlled gateway; production licensed adapter remains in DEF-012 |
| Corporate actions | DEFERRED | Adjustment evidence/policy; DEF-013 |
| Sector / index / macro context | IMPLEMENTED | A3.6 explicit point-in-time contracts, test/caller adapters, controlled reads, and shared source reuse; production adapters remain DEF-012 and automatic mapping remains DEF-047 |
| Market-calendar recency | DEFERRED | Session/calendar contract; DEF-007 |
| Primary quote/OHLCV/F&O secondary-provider fallback | DEFERRED | Dhan data surface identity, health, and conflict policy; DEF-008. MI evidence fallback is separately implemented |
| Persistent/distributed cache | DEFERRED | Operational storage and consistency; DEF-009 |
| Provider health arbitration | DEFERRED | Health/fallback policy; DEF-011 |

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
| Swing pivots / fractals | DEFERRED | Confirmation-time semantics; DEF-020 |
| Classic floor pivots | DEFERRED | Session-aware level/Indicator extension; DEF-036 |
| Multi-timeframe levels | DEFERRED | Explicit level-context extension; DEF-038 |
| Structural remaining-room scoring | IMPLEMENTED | A2.9 direction-specific prior-boundary room |
| Breakout/readiness scoring | IMPLEMENTED | A2.9 transparent geometry/compression synthesis |
| Failed-breakout classification | DEFERRED | Event-state/replay semantics; DEF-035 |
| Derivatives deterministic features | IMPLEMENTED | A2.7 single-expiry facts |
| Option-chain deterministic features | IMPLEMENTED | A2.7 single-expiry facts |
| ATM / strike geometry | IMPLEMENTED | A2.7 chain-consistent listed strikes |
| ATM premium / IV / Greeks | IMPLEMENTED | A2.7 provider-supplied facts |
| OI / option-volume ratios | IMPLEMENTED | A2.7 exact strike windows |
| OI concentration / weighted strike | IMPLEMENTED | A2.7 exact strike windows |
| Bid/ask spread primitives | IMPLEMENTED | A2.7 ATM contract facts |
| Explicit-benchmark relative strength | IMPLEMENTED | A2.8 exact aligned returns/ATR facts |
| Automatic benchmark / sector mapping | DEFERRED | Classification evidence; DEF-047 |
| Sector rotation | IMPLEMENTED | A3.6 cautious multi-period interpretation over explicit mapping/evidence; automatic mapping remains DEF-047 |
| Ordered multi-timeframe context | IMPLEMENTED | A2.8 independent FeatureBundle evidence |
| Multi-timeframe factual fractions | IMPLEMENTED | A2.8 valid-contributor aggregation |
| Multi-timeframe indicator aggregation | DEFERRED | Explicit indicator-context contract; DEF-048 |
| Market-state summary | IMPLEMENTED | A2.9 deterministic baseline |
| Horizon-aware opportunity scoring | IMPLEMENTED | A2.9 versioned DAY/POSITIONAL policy |
| Candidate classification / ranking | IMPLEMENTED | A2.9 eligible-only stable ranking |
| Evidence snapshot / exact offline replay | IMPLEMENTED | A2.10 provider-neutral foundation |
| Baseline outcome / MFE / MAE evaluation | IMPLEMENTED | A2.10 raw factual metrics, no execution model |
| Replay regression corpus | IMPLEMENTED | A2.10 persisted JSON/JSONL snapshot/run collections |
| Synthetic golden regression | IMPLEMENTED | A2.10 pytest-built deterministic fixtures |
| Arbitrary historical reconstruction | DEFERRED | Point-in-time data-vintage boundary; DEF-049 |
| Scheduled subsequent-outcome acquisition | DEFERRED | Calendar/queue/retention boundary; DEF-051 |
| Calibrated forecast evidence contract | IMPLEMENTED | A3.1 consumer seam; no forecast generation |
| Forecast generation / calibration | PLANNED | A7 Evaluation, Forecasting and Learning |

## Indicators

| Capability | Status | Placement |
|---|---|---|
| SuperTrend | IMPLEMENTED | A2.4 library |
| RSI | IMPLEMENTED | A2.4 library |
| MACD | IMPLEMENTED | A2.4 library |
| ADX / +DI / -DI | IMPLEMENTED | A2.4 library |
| Bollinger Bands | IMPLEMENTED | A2.4 library |
| Donchian Channel | IMPLEMENTED | A2.4 library |
| OBV | DEFERRED | Named Indicator-library variant; DEF-030 |
| MFI | DEFERRED | Named Indicator-library variant; DEF-030 |
| Chaikin / Accumulation-Distribution | DEFERRED | Named Indicator-library variant; DEF-030 |
| Session VWAP | DEFERRED | Explicit intraday sessions; DEF-027 |
| Anchored VWAP | DEFERRED | Explicit anchor contract; DEF-028 |
| Volume profile | DEFERRED | Explicit binning semantics; DEF-029 |
| Market profile | DEFERRED | Explicit session/binning semantics; DEF-029 |
| Delivery / participant statistics | DEFERRED | Normalized provider evidence; DEF-032 |
| HalfTrend | DEFERRED | Named canonical variant; DEF-021 |
| Future / proprietary indicators | DEFERRED | Named/versioned registry extensions; DEF-026 |

## Derivatives intelligence

| Capability | Status | Placement |
|---|---|---|
| Option-chain factual structure | IMPLEMENTED | A1 evidence |
| Greeks / IV / OI facts | IMPLEMENTED | A1 evidence |
| Single-expiry deterministic features | IMPLEMENTED | A2.7 |
| ATM bid/ask spread measurements | IMPLEMENTED | A2.7 |
| Historical option feature library | DEFERRED | Historical-options extension; DEF-040 |
| Cross-expiry / term structure | DEFERRED | Multi-chain evidence; DEF-042 |
| IV surface / skew surface | DEFERRED | Explicit surface model; DEF-043 |
| OI-change regime interpretation | DEFERRED | Temporal derivative model; DEF-041 |
| Gamma exposure / dealer positioning | DEFERRED | Positioning assumptions; DEF-046 |
| Max pain | DEFERRED | Explicit payoff/OI convention; DEF-045 |
| Probability of profit | DEFERRED | Explicit model/evaluation; DEF-044 |
| Expected move model | DEFERRED | Explicit model/evaluation; DEF-044 |
| Derivative liquidity measurements | IMPLEMENTED | A2.7 factual ATM spread primitive |
| Expiry-effect analysis | DEFERRED | Historical derivative evidence; DEF-041 |

## Option strategy library

All are **PLANNED** under Option Expression Intelligence (DEF-006) rather than A2.4:
long call, long put, bull call spread, bear put spread, bull put spread, bear
call spread, straddle, strangle, iron condor, iron butterfly, butterflies,
calendars, diagonals, ratio spreads, and defined-risk variants.

## Rule and policy layer

| Capability | Status | Placement |
|---|---|---|
| SigmaDSL integration | DEFERRED | Rule/strategy policy boundary; DEF-025 |
| Strategy entry/exit rules | DEFERRED | Separate from indicator evidence; DEF-025 |
| Parameter optimization | DEFERRED | Replay/evaluation boundary; DEF-024 |

## Agent intelligence

The architecture is accepted in
[`TIAF_A3_ARCHITECTURE.md`](TIAF_A3_ARCHITECTURE.md). A3.1 contracts and the
bounded single-specialist runtime and A3.2 controlled evidence/reasoning/budget
gateways are complete/accepted. A3.3 through A3.6 are complete/accepted. The
A3.6.1 provider-fabric and deep-research-foundation contracts, routing,
normalization, evidence memory, and read-only adapter boundary are implemented.
The isolated Tapetide stdio connector and adapter-to-replay path are frozen at
`tiaf-a3.6.1`. A post-freeze Yahoo/yfinance MCP adapter now provides bounded
profile, financial, earnings-event, and news fallback/corroboration. Its
deterministic path passes; its corrected ten-call live-acceptance matrix,
rate-limit fallback, and exact offline replay passed on 2026-09-10. Agents
consume controlled evidence and do not belong inside deterministic calculators.

The bounded authoritative-confirmation follow-up is implemented and
live-validated. It reuses A3.6.1 routing and A3.5 event clustering to link
material discovery claims to exchange, regulator, company-IR, rating, or other
official document evidence without exposing source transports to specialists.

A3.6.2 end-to-end deep-research integration is complete and bounded-live-
validated. It composes the existing sources into normalized context, explicit
gaps/contradictions, sparse graph memory, deterministic epistemically separated
research output, and exact provider-free replay with zero model usage.

The Yahoo earnings adapter uses the additive provider-neutral
`READ_EARNINGS_CALENDAR` capability under the existing `READ_FILINGS` authority;
it does not overload corporate-action or earnings-call semantics.

| Capability | Status | Placement |
|---|---|---|
| Agent contracts / provider-neutral protocols | IMPLEMENTED | A3.1 complete/accepted; A3 closure marks DEF-002 implemented by the complete A3.1-A3.10 layer |
| Single-specialist registry/runtime foundation | IMPLEMENTED | A3.1; no tools, model calls, or orchestration |
| Controlled evidence/reasoning/budget gateways | IMPLEMENTED | A3.2 complete/accepted; production model-backed reasoning remains DEF-052 |
| Technical / market-structure interpretation | IMPLEMENTED | A3.3 complete/accepted; deterministic/cited/no-LLM path |
| Fundamental / company-quality interpretation | IMPLEMENTED | A3.4 complete/accepted; point-in-time, deterministic/cited/no-LLM path |
| News / catalyst / event interpretation | IMPLEMENTED | A3.5 complete/accepted; PIT, deduplicated, cited/no-LLM path |
| Relative / sector / macro interpretation | IMPLEMENTED | A3.6 complete/accepted; three separate cited/no-LLM specialists, explicit mappings, PIT and reusable context |
| Multi-provider market-intelligence routing | IMPLEMENTED | A3.6.1 per-capability declarations, four routing modes, progressive enrichment, secondary fixture, and no global provider |
| Provider-native semantic normalization / contradiction journal | IMPLEMENTED | A3.6.1 conservative mapping journal and canonical provenance projection; A3.4–A3.6 outputs remain unchanged |
| Sparse Evidence Graph / structured deep-research foundation | IMPLEMENTED | A3.6.1 materiality-driven point-in-time graph and composable FACT/INFERENCE/HYPOTHESIS-separated research contracts |
| Authoritative primary-source claim confirmation | IMPLEMENTED / LIVE VALIDATED | Bounded post-A3.6.1 NSE/BSE/company-IR adapters; source/domain validation, document/revision lineage, field-level confirmation, content cache, event/graph integration, and replay; no crawler |
| Integrated deterministic company research | IMPLEMENTED / LIVE VALIDATED | A3.6.2 multi-capability enrichment, normalized quality/PIT context, authoritative linkage, sparse graph, FACT/INFERENCE/HYPOTHESIS enforcement, explicit gaps, no-LLM baseline, and exact replay |
| Derivatives context interpretation | IMPLEMENTED | A3.7 cited deterministic/no-LLM interpretation over supplied A2.7 families; live acquisition unavailable |
| Opportunity quality interpretation | IMPLEMENTED | A3.7 A2.9 maturity/room and grouped A3 evidence; no recommendation authority |
| Opportunity risk interpretation | IMPLEMENTED | A3.7 grouped pre-arbitration downside context; no position action |
| Instrument-aware Planner / orchestration | ACCEPTED / `tiaf-a3.8` | [A3.8 implementation](TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md): capability/dependency policy, bounded parallelism, shared evidence/budget reservations, selective enrichment/confirmation/research and reruns, partial stops, isolated LangGraph and replay; [offline acceptance](STUDY_A3_8_USER_LEVEL_ACCEPTANCE.md); no investment-decision authority |
| Structured underlying opportunity intelligence | ACCEPTED / `tiaf-a3.9` | [A3.9 design](TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md): captured A3.8 input, typed contributions and qualified bias, explicit observation state, preserved A2/conflicts/gaps, separate confidence, cited reasons and pure assembly replay; cross-candidate analysis/ranking remains DEF-053 and report rendering DEF-054 |
| Agent replay / A2 comparison / cost/failure hardening | ACCEPTED / `tiaf-a3.10` | [A3.10 implementation](TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md): content-addressed capture, explicit replay modes, observational comparison, unknown-cost semantics, lossless failures, 14-case synthetic corpus and closure-readiness seam; monetary pricing knowledge remains DEF-055; [study](STUDY_A3_10_USER_LEVEL_ACCEPTANCE.md) |
| A4 source/comparability/independence input projection | IMPLEMENTED / ACCEPTED | [POST_A3_PRE_A4_FOUNDATION](TIAF_POST_A3_PRE_A4_FOUNDATION.md) adds immutable source/proposition/authority/dispute/independence contracts, field confirmation, deterministic projection, successor semantics and offline replay over unchanged A2/A3; citation rendering remains absent |
| Narrow local capability facade and lifecycle | IMPLEMENTED / ACCEPTED | [POST_A3_PRE_A4_LOCAL_FACADE](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) now exposes seven explicit same-process capabilities, including A4.1 `a4.evaluate`, with trusted admission, budget/authority intersection, frozen composition, safe logical artifact refs and offline replay; no live operation, remote transport or broker authority |
| Deterministic arbitration / adversarial resolution | IMPLEMENTED / A4 FREEZE READY | [A4.1](TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md) implements bounded primary/counter theses and deterministic arbitration; [A4.2](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md) adds governed one-round evidence admission, A3.8 execution, later successor projection and offline chain replay; [major closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) accepts the combined no-model boundary |
| Position intelligence | IMPLEMENTED / A5.1 ACCEPTANCE READY | [A5.1](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md): captured supplied position truth, deterministic single-position posture/thesis/recommendation, monitoring intent and exact replay; no facade/TM/broker/multi-leg runtime |
| Option strategy comparison/selection | PLANNED | A6/DEF-006 deterministic valid candidates first; forecast-enhanced higher-order comparison after admitted A7 evidence; no initial A4 contract selection |
| Forecast interpretation | PLANNED | Conditional A3 consumer of calibrated A7 evidence |
| Scanner intelligence | EXTERNAL/INTEGRATION | A9 scanner boundary |

## Applications

| Capability | Status | Placement |
|---|---|---|
| Read-only console diagnostics | IMPLEMENTED | Milestone smoke scripts |
| Position monitoring-intent contract | IMPLEMENTED / A5.1 | Immutable `WatchMandate`/`MonitoringNeed` values only; no scheduling guarantee or runtime |
| Monitoring daemon / intelligence OS | DEFERRED | Runtime scheduling, queue, retry/recovery and calendars; DEF-007/010, A10 |
| Persistent/distributed data runtime | DEFERRED | Storage and operations boundary; DEF-009 |
| Primary quote/OHLCV/F&O fallback and operational health arbitration | DEFERRED | Dhan data surface; DEF-008/DEF-011. Separate MI evidence fallback is implemented in A3.6.1 |
| Scanner | EXTERNAL/INTEGRATION | Future TIAF scanner boundary |
| UI / dashboard | FUTURE | Application layer; service dependency DEF-003 |
| Governed local capability facade/catalog | IMPLEMENTED / ACCEPTED | [Local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md): static seven-capability catalog, trusted same-process admission/lifecycle, request isolation, logical-ref captured reads and single-writer configuration; the facade itself owns no Shell or transport, while the separate v0.1 Shell now consumes it |
| Remote API / service delivery | PLANNED | DEF-003 delivery track; [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md) makes local/remote hosting conditional on real consumer/isolation needs; A8 integration, A10 operations; same intelligence path, no service now |
| Alerts | FUTURE | Application/policy layer; runtime dependency DEF-010 |
| Human-facing explanation/citation reports | PLANNED / BOUNDED SLICE | DEF-054 minimal captured-source rendering with command-first Shell after A4; richer report/Web UX remains deferred; no re-research |
| Cross-candidate A3 opportunity comparison/ranking | DEFERRED | DEF-053 A7 evaluation design after stable per-candidate A3/A4 products; A2 ranking remains benchmark |
| Bounded open-world A4 research loop | IMPLEMENTED / A4 FREEZE READY | [A4.2](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md) admits provider-neutral needs, executes at most one existing A3.8 enrichment round, requires normalized source-semantic crosswalk, creates at most one later successor, stops on no information/upstream refresh and replays offline; optional model challenge and public live facade remain absent |
| TI_SHELL command-first engineering v0.1 | IMPLEMENTED / ACCEPTANCE READY | [Implementation](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md): same-process command adapter over the seven governed facade capabilities, transient isolated session, exact-result JSON, bounded explain/trace, offline replay and engineering-gated verification; no A5 dependency, NLP/model/live/private/broker access or remote transport |
| Baseline replay / validation | IMPLEMENTED | A2.10 captured-snapshot foundation |
| Strategy backtest | DEFERRED | Requires strategy/execution model; DEF-025 |
| Optimization | DEFERRED | Evaluation layer; DEF-024 |
| Watchlists | EXTERNAL/INTEGRATION | Input source consumed through A1 |

## Governance and execution

| Capability | Status | Placement |
|---|---|---|
| TradeMonitor intelligence contract | EXTERNAL/INTEGRATION | A8 boundary; DEF-004 |
| Risk, authority, lifecycle, execution | EXTERNAL/INTEGRATION | TradeMonitor owns; DEF-005 |
| Broker execution | EXTERNAL/INTEGRATION | Rejected from TIAF scope; DEF-005 |

TIAF indicators and features never place orders. Primitive features,
indicators, future strategies, Agent reasoning, and execution authority remain
distinct architectural layers.
