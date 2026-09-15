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
its bounded A5.1 runtime is implemented, and A5.2 adds governed local
facade/Shell publication. The
[A5 major closure](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md) concludes
`READY_TO_FREEZE_A5` and recommends `tiaf-a5-baseline` without creating it. A7 later informs a separately
versioned forecast-enhanced A6 follow-up; no major milestone is renumbered.

Statuses describe repository reality:

- **IMPLEMENTED** — accepted code/contracts exist;
- **PLANNED** — placed on an explicit future roadmap milestone;
- **DEFERRED** — recorded with an unresolved prerequisite in the
  [deferral register](TIAF_DEFERRAL_REGISTER.md);
- **FUTURE** — recognized capability without a committed near-term milestone;
- **ARCHITECTURE ONLY** — authoritative design, not an implemented runtime;
- **EXTERNAL/INTEGRATION** — owned by or dependent on another system boundary.

The [TI Pluggability Architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md) now
governs first-order composition. Its nine-family target matrix (§13) is not
an A1–A5 compliance classification. The [completed audit](TIAF_PLUGGABILITY_A1_A5_COMPLIANCE_AUDIT.md)
provides the evidence-backed 43-row classification. The bounded
[R1 correction](TIAF_PLUGGABILITY_R1_REQUIRED_SCOPE_EXPLICIT_ABSENCE.md) now
implements stable required scope and explicit absence. Descriptor/readiness,
R2 discovery metadata and the R3 per-run composition envelope/pinned verifier are
implemented; R4 adapter import isolation and R5 COLD ownership are accepted/done.
Neither added a public operation at the time; A6.3 now adds the separately
governed ninth operation.
HOT transitions remain deferred (DEF-057). Future `sector.rotation`,
`signal.qualify` and historical `forecast.return` discovery examples are not implemented
public capabilities. Their typed publication/projection readiness is DEF-058.
The [R1 acceptance closure](TIAF_PLUGGABILITY_R1_ACCEPTANCE_AND_A5_FREEZE_READINESS.md)
finds R2–R5 unnecessary for A5 freeze and A5 ready for final documentation and
freeze. Documentation consolidation, the
[final readiness check](TIAF_A5_FINAL_FREEZE_TAG_READINESS_CHECK.md), documentation
commit `167c51d` and annotated tag `tiaf-a5-baseline` are complete. A5 is
FROZEN; [R2 Discovery Metadata](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA.md) is
[ACCEPTED / DONE](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA_ACCEPTANCE.md). The
[milestone ledger](MILESTONES.md)
owns current project status. R2 now adds typed, non-binding discovery metadata
without changing facade operation IDs or invocation behavior. The
[R3 implementation](TIAF_PLUGGABILITY_R3_COMPOSITION_ENVELOPE_PINNED_VERIFIER.md)
adds versioned run participation to A3.8 captures and exact pinned deterministic
verification without granting authority or adding LIVE_READ; its
[acceptance](TIAF_PLUGGABILITY_R3_COMPOSITION_ENVELOPE_PINNED_VERIFIER_ACCEPTANCE.md)
is complete. The
[R4 implementation](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION.md)
and [acceptance](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION_ACCEPTANCE.md)
isolate optional implementation imports without adding a capability;
[R5](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md) adds trusted COLD
startup selection and binding freeze; its
[acceptance](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION_ACCEPTANCE.md)
closes the R1–R5 track. The detailed
[A4](TIAF_A4_DETAILED_ROADMAP.md) and [A5](TIAF_A5_DETAILED_ROADMAP.md) roadmaps
link implementation, acceptance and outstanding boundaries.

## Current public/engineering catalog versus future designs

This exact nine-operation inventory mirrors the static local facade catalog;
it is not a new registry or permission grant. All reads remain captured/local.
`REQUIRES_RUNTIME_CHECK` means discovery does not assert request readiness,
authority, dependency availability, health or fresh data.

| Capability ID | Interface / effect | Semantic role | Pluggability | Monitoring | Readiness |
|---|---|---|---|---|---|
| `a4.evaluate` | PUBLIC / CAPTURED_READ | CHALLENGE_ARBITRATION | STRUCTURAL | SEMANTICALLY_REPEATABLE | REQUIRES_RUNTIME_CHECK |
| `a4_input.project` | PUBLIC / CAPTURED_READ | CHALLENGE_ARBITRATION | STRUCTURAL | SEMANTICALLY_REPEATABLE | REQUIRES_RUNTIME_CHECK |
| `baseline.assess` | PUBLIC / PURE | BASELINE | STRUCTURAL | SEMANTICALLY_REPEATABLE | REQUIRES_RUNTIME_CHECK |
| `capabilities.list` | PUBLIC / PURE | CAPABILITY_DISCOVERY | STRUCTURAL | NOT_MONITORABLE | REQUIRES_RUNTIME_CHECK |
| `expression.assess` | PUBLIC / CAPTURED_READ | TRADE_EXPRESSION_INTELLIGENCE | STRUCTURAL | MONITORING_FUTURE | REQUIRES_RUNTIME_CHECK |
| `opportunity.assemble` | PUBLIC / CAPTURED_READ | OPPORTUNITY_INTELLIGENCE | STRUCTURAL | SEMANTICALLY_REPEATABLE | REQUIRES_RUNTIME_CHECK |
| `position.assess` | PUBLIC / CAPTURED_READ | POSITION_INTELLIGENCE | STRUCTURAL | MONITORING_FUTURE | REQUIRES_RUNTIME_CHECK |
| `replay.recorded` | PUBLIC / CAPTURED_READ | REPLAY | STRUCTURAL | NOT_MONITORABLE | REQUIRES_RUNTIME_CHECK |
| `replay.verify` | ENGINEERING / CAPTURED_READ | ENGINEERING | STRUCTURAL | NOT_MONITORABLE | REQUIRES_RUNTIME_CHECK |

No LIVE_READ facade operation exists. A4.2's governed internal acquisition bridge
is not a public endpoint. Future `sector.rotation`, `signal.qualify` and
the reconciled A7 design's `forecast.assess` are proposals only; the earlier
`forecast.return` example reserves no ID or alias. Recurring monitoring, TM/scanner
runtime and remote transport are not callable capabilities.

A6 is **FROZEN at `tiaf-a6-baseline`; A6.1–A6.4 ACCEPTED / DONE;
`expression.assess` PUBLISHED. A7 is ARCHITECTURE ACCEPTED / IMPLEMENTATION IN_PROGRESS (FF-0.1 ONLY) / RUNTIME NOT_IMPLEMENTED**. The
[A6 draft](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md) defines the
advisory, captured-input, deterministic long single-leg CE/PE assessment now
published by [A6.3](TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE.md) and closed by its
[independent acceptance](TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE_ACCEPTANCE.md).
The [independent architecture acceptance is complete](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md).
The [A6.1 implementation](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION.md)
and [acceptance](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION_ACCEPTANCE.md)
add no operation; facade/Shell publication remains A6.3.
The [A6.2 internal evaluator](TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY.md)
is [accepted](TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY_ACCEPTANCE.md); A6.3
publishes it without adding live acquisition and is accepted/done.
The [A6.4 closure](TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md)
records the explicit 93-case corpus, public disposition goldens and final
freeze-readiness result without adding another capability.

The [reconciled A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md)
and [roadmap](TIAF_A7_DETAILED_ROADMAP.md) propose separate forecasting,
evaluation and learning, with one exact equity endpoint target and no v1
automatic influence on A4/A5/A6. The [reconciliation](TIAF_A7_RECONCILIATION_RECORD.md)
retains the existing A3 forecast placeholder without claiming an implementation.
The [A7 thesis creation edition](TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md)
is unchanged; all [17 findings are RECONCILED](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md).
A7 ARCHITECTURE is ACCEPTED; FF-0 planning is COMPLETE; FF-0.1 is ACCEPTED; separately authorized FF-0.2 is NEXT. The intervening
[FF architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md) is ACCEPTED;
FF MINIATURE REALIZATION is DEFINED; FF THESIS RECONCILED; FF ARCHITECTURE
ACCEPTANCE COMPLETE; FFA-B01 CLOSED; A7 integration RECONCILED; A7 architecture ACCEPTED; FF-0 plan COMPLETE; FF-0.1 ACCEPTED; separately authorized FF-0.2 NEXT; IMPLEMENTATION IN_PROGRESS (FF-0.1 ONLY);
RUNTIME NOT_IMPLEMENTED. FM/LFDE is its advanced family; its existing thesis is retained.
The completed [FF/A7 integration](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md)
is now independently [accepted](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md).
It adds no capability IDs; A7's documentation
now owns the integrated stage crosswalk. The Evaluation-owned population
report is a proposed internal artifact, not another capability. Explanatory
examples and registry mockups add no model, callable operation or acceptance claim.

| A7 design surface | Proposed placement | Current status |
|---|---|---|
| `forecast.assess` | Future public captured/local shadow/advisory inference | ARCHITECTURE RECONCILED / NOT_IMPLEMENTED; not in catalog |
| `forecast.evaluate` | Future engineering persisted-corpus evaluation | ARCHITECTURE RECONCILED / NOT_IMPLEMENTED; not in catalog |
| `model.list` / `model.describe` | Engineering registry inspection initially, not new public operations | PROPOSED / NOT_IMPLEMENTED |
| A7 recorded replay / pinned verification | Future additive artifact-kind support through existing replay seam | PROPOSED / NOT_IMPLEMENTED; old replay unchanged |
| Training / calibration / promotion | Governed engineering lifecycle, no public training command | PROPOSED / NOT_IMPLEMENTED |

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
| Sector-context interpretation | IMPLEMENTED | A3.6 cautious multi-period interpretation over explicit mapping/evidence; not the future Sector Rotation engine; automatic mapping remains DEF-047 |
| Sector Rotation engine / `sector.rotation` | FUTURE | Non-authoritative idea cache; cross-sectional rotation/ranking and publication need separate architecture/PIT/DEF-058 acceptance; ordering relative to A7/A8 TBD |
| Signal Qualification / `signal.qualify` | FUTURE | Intended after Sector Rotation review; no qualified-signal engine, probability guarantee or public operation implemented |
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

The earlier broad library inventory is not an A6 v1 delivery commitment.
**PLANNED initial A6 / DEF-006:** long call and long put only, as bounded
single-leg CE/PE analytical expressions. See the
[reconciled scope](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md#3-bounded-v1-and-explicit-exclusions).

**Deferred beyond v1, requiring separate scope acceptance under DEF-006:** bull
call spread, bear put spread, bull put spread, bear call spread, straddle,
strangle, iron condor, iron butterfly, butterflies, calendars, diagonals, ratio
spreads and other defined-risk/multi-leg variants. Option writing and portfolio/
margin optimization are not initial A6 obligations. No strategy here is A2.4
indicator logic or authority to execute.

## Rule and policy layer

| Capability | Status | Placement |
|---|---|---|
| SigmaDSL integration | DEFERRED | Explicitly outside TI A6 v1; no parser/runtime/compatibility prerequisite. Separate future SigmaTrader programmable-product review; DEF-025 |
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
| Narrow local capability facade and lifecycle | IMPLEMENTED / ACCEPTED | [POST_A3_PRE_A4_LOCAL_FACADE](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) plus A4.1/A5.2/A6.3 now expose nine explicit same-process capabilities, including `a4.evaluate`, `position.assess` and `expression.assess`, with trusted admission, budget/authority intersection, frozen composition, safe logical artifact refs and offline replay; no live operation, remote transport or broker authority |
| Deterministic arbitration / adversarial resolution | IMPLEMENTED / FROZEN at `tiaf-a4-baseline` | [A4.1](TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md) implements bounded primary/counter theses and deterministic arbitration; [A4.2](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md) adds governed one-round evidence admission, A3.8 execution, later successor projection and offline chain replay; [major closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) accepts the combined no-model boundary |
| Position intelligence | IMPLEMENTED / FROZEN at `tiaf-a5-baseline` | [A5.1](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md) deterministic baseline plus [A5.2](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md) governed facade/Shell publication and [closure](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md); no live TM/broker/multi-leg runtime |
| Option strategy comparison/selection | BOUNDED A6 IMPLEMENTED; broader scope DEFERRED | Frozen captured-read long single-leg CE/PE selection; DEF-006 broader strategies and A7-enhanced comparison remain deferred; no initial A4 contract selection |
| Forecast interpretation | PLANNED | Conditional A3 consumer of calibrated A7 evidence |
| Scanner intelligence | EXTERNAL/INTEGRATION | A9 scanner boundary |

## Applications

| Capability | Status | Placement |
|---|---|---|
| Read-only console diagnostics | IMPLEMENTED | Milestone smoke scripts |
| Position monitoring-intent contract | IMPLEMENTED / A5.1 | Immutable `WatchMandate`/`MonitoringNeed` values only; no scheduling guarantee or runtime |
| Subscriber-driven monitoring design | ARCHITECTURE ONLY | [TI Monitoring Architecture](TIAF_MONITORING_ARCHITECTURE.md): optional subscriber-owned groups, normalized independent mandates, capability consumption, scoped evidence sharing and replay; no recurring runtime |
| Monitoring daemon / intelligence OS | DEFERRED | [Reconciled runtime boundary](TIAF_MONITORING_ARCHITECTURE.md): admission, periodic/event scheduling, retry/recovery and calendars; DEF-007/009/010/011/050/051, A10; A8 TM and A9 scanner intake remain separate |
| Persistent/distributed data runtime | DEFERRED | Storage and operations boundary; DEF-009 |
| Primary quote/OHLCV/F&O fallback and operational health arbitration | DEFERRED | Dhan data surface; DEF-008/DEF-011. Separate MI evidence fallback is implemented in A3.6.1 |
| Scanner | EXTERNAL/INTEGRATION | Future TIAF scanner boundary |
| UI / dashboard | FUTURE | Application layer; service dependency DEF-003 |
| Governed local capability facade/catalog | IMPLEMENTED / ACCEPTED | [Local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) with A4.1/A5.2/A6.3 additions: static nine-capability catalog, trusted same-process admission/lifecycle, request isolation, logical-ref captured reads and single-writer configuration; the facade itself owns no Shell or transport, while the separate Shell consumes it |
| Remote API / service delivery | PLANNED | DEF-003 delivery track; [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md) makes local/remote hosting conditional on real consumer/isolation needs; A8 integration, A10 operations; same intelligence path, no service now |
| Alerts | FUTURE | Application/policy layer; runtime dependency DEF-010 |
| Human-facing explanation/citation reports | PLANNED / BOUNDED SLICE | DEF-054 minimal captured-source rendering with command-first Shell after A4; richer report/Web UX remains deferred; no re-research |
| Cross-candidate A3 opportunity comparison/ranking | DEFERRED | DEF-053 A7 evaluation design after stable per-candidate A3/A4 products; A2 ranking remains benchmark |
| Bounded open-world A4 research loop | IMPLEMENTED / A4 FREEZE READY | [A4.2](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md) admits provider-neutral needs, executes at most one existing A3.8 enrichment round, requires normalized source-semantic crosswalk, creates at most one later successor, stops on no information/upstream refresh and replays offline; optional model challenge and public live facade remain absent |
| TI_SHELL command-first engineering v0.1 | IMPLEMENTED / A5.2 ADDITIVE EXPOSURE | [Implementation](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md): same-process command adapter over governed facade capabilities, including bounded `position assess`; transient isolated session, exact-result JSON, bounded explain/trace, offline replay and engineering-gated verification; no NLP/model/live/private/broker access or remote transport |
| Baseline replay / validation | IMPLEMENTED | A2.10 captured-snapshot foundation |
| Strategy backtest | DEFERRED | Requires strategy/execution model; DEF-025 |
| Optimization | DEFERRED | Evaluation layer; DEF-024 |
| Watchlists | EXTERNAL/INTEGRATION | Subscriber-owned optional business groups/input sources; future TI monitoring accepts governed mandates with opaque refs, not watchlist CRUD |

## Governance and execution

| Capability | Status | Placement |
|---|---|---|
| TradeMonitor intelligence contract | EXTERNAL/INTEGRATION | A8 boundary; DEF-004 |
| Risk, authority, lifecycle, execution | EXTERNAL/INTEGRATION | TradeMonitor owns; DEF-005 |
| Broker execution | EXTERNAL/INTEGRATION | Rejected from TIAF scope; DEF-005 |

TIAF indicators and features never place orders. Primitive features,
indicators, future strategies, Agent reasoning, and execution authority remain
distinct architectural layers.

<a id="forecasting-framework--a7-integrated-architecture-acceptance-next"></a>

## Forecasting Framework and A7 — architecture accepted; FF-0.1 foundation accepted

The [FF-0.1 implementation record](TIAF_A7_FF0_1_CONTRACTS_TARGET_CLOCK_IMPLEMENTATION.md)
records **FF0_1_ACCEPTED**: immutable contracts, one synthetic RELIANCE target,
clock/knowledge validation and deterministic identity primitives. A7 / FF is
**IMPLEMENTATION IN_PROGRESS; FORECAST EXECUTION RUNTIME NOT_IMPLEMENTED**.
Only the first of the [four planned FF-0 steps](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md)
is complete. Next is separately authorized **FF-0.2 — Capture store, truth and
recorded replay**. FF-0 overall is not accepted; no model, public capability or
empirical qualification is delivered. Calibration remains at FF-2.

The [A7 acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) records
**A7_ARCHITECTURE_ACCEPTED** on **2026-09-15 (Asia/Kolkata)**:
A6 FROZEN; FF ARCHITECTURE ACCEPTED; A7 ARCHITECTURE ACCEPTED;
A7 THESIS RECONCILED AS NEEDED; then A7 / FF IMPLEMENTATION NOT_STARTED;
RUNTIME NOT_IMPLEMENTED. The foundation-only update above supersedes that status.
FM/LFDE remains an optional advanced Forecaster family.

A7 is the lifecycle umbrella. FF owns forecasting contracts, typed DAG and
bounded runtime; Evaluation owns Ground Truth, Outcome Journal, joined Forecast
Ledger, benchmarks/metrics/calibration qualification/drift; Learning owns
candidate fits and the single artifact/lifecycle registry. Independent reviewer
approval and trusted COLD selection stay separate. The
[A7 roadmap](TIAF_A7_DETAILED_ROADMAP.md) contains FF-0…FF-7 unchanged,
with the old A7.1…A7.5 crosswalk. FF-0/1 raw research precedes FF-2's calibrated
miniature; publication is separately accepted, advanced families optional.

The [FF repeat review](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE_REPEAT.md)
closed FFA-B01; the [A7 integration](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md)
then reconciled all 17 A7 findings. Original HOLD, correction, repeat acceptance,
integration and all 28 FF findings remain historical evidence. Their then-next
language and the Deferral Register's dated A7.x notes are not the current queue.
All 58 canonical deferral rows and six thesis DOCX/PDF artifacts are unchanged.

Exact next prompt: **TIAF A7 / FF-0.2 — CAPTURE STORE, TRUTH AND RECORDED REPLAY**.
FF-0.1 acceptance is limited to the tested foundation. FF-0.2 needs a separate
request; no training, model approval, publication, frozen-A6 changes or A8 is
authorized. Historical planning/acceptance records retain their then-current status.
