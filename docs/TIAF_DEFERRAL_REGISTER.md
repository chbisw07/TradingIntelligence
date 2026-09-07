# TIAF Deferral Register

## Purpose

This register preserves decisions that would otherwise be easy to lose between
milestones. It is a governance memory, not a scheduling engine. A `DEF-*` ID is
stable: later reviews update status and resolution notes without renumbering or
deleting the historical record.

Only capabilities explicitly deferred, described as future, or declared an
intentional milestone non-goal in accepted TIAF documentation are included.
Work already placed in the immediately following A2.9 or A2.10 target is not
misrepresented as a deferral.

Allowed categories are `CAPABILITY_DEFERRAL`, `DEPENDENCY_DEFERRAL`, and
`INTENTIONAL_NON_GOAL`. Allowed statuses are `DEFERRED`, `PLANNED`,
`IN_PROGRESS`, `IMPLEMENTED`, `REJECTED`, and `SUPERSEDED`.

Priority means architectural importance when prerequisites are satisfied; it
does not override the roadmap sequence.

## Revisit policy

Deferrals are recorded when they arise, without interrupting each A2.x, A3.x,
or later sub-milestone to pursue them. At every **major milestone closure**—A2,
A3, A4, and so on—the closure record must:

1. review every deferral introduced in or before that major milestone;
2. attempt work whose dependencies are now satisfied;
3. mark unjustified items `REJECTED` or replaced items `SUPERSEDED`;
4. carry forward only genuinely unresolved items with a written rationale; and
5. report introduced, implemented, rejected, superseded, carried-forward, and
   remaining high-priority deferrals.

This review occurs once at major milestone closure, not after every numbered
sub-milestone.

## Register

| ID | Capability | Deferred From | Category | Reason | Dependency / prerequisite | Priority | Suggested Revisit | Status | Resolution Notes |
|---|---|---|---|---|---|---|---|---|---|
| DEF-001 | Market-data adapters and factual fetch | A0 | CAPABILITY_DEFERRAL | Contracts preceded provider integration. | Stable provider-neutral data contracts | HIGH | A1 CLOSURE | IMPLEMENTED | Delivered through A1.1-A1.7, including Dhan and `AnalysisContext`. |
| DEF-002 | Agent, LLM, and workflow reasoning layer | A0; reaffirmed A2.4/A2.8 | INTENTIONAL_NON_GOAL | Deterministic contracts/calculators must not contain judgment-oriented orchestration. | Accepted A2 factual baseline and evidence boundaries | HIGH | A3 CLOSURE | PLANNED | Roadmap A3 introduces Planner and specialist Agents; A4 adds arbitration. |
| DEF-003 | TIAF service/API surface | A0 | CAPABILITY_DEFERRAL | Foundation milestones intentionally expose packages and diagnostics, not a service boundary. | Stable intelligence contracts and operational requirements | MEDIUM | A8 CLOSURE | PLANNED | Roadmap A8 includes the local service/API boundary. |
| DEF-004 | TradeMonitor intelligence integration | A0 | DEPENDENCY_DEFERRAL | Integration must preserve TradeMonitor risk, lifecycle, and authority. | Stable assessments, freshness/degradation, and evaluation feedback | HIGH | A8 CLOSURE | PLANNED | Roadmap A8 owns structured advice integration without authority transfer. |
| DEF-005 | Broker order placement/modification/cancellation by TIAF | A0; reaffirmed A1-A2.8 | INTENTIONAL_NON_GOAL | TIAF intelligence never owns broker execution authority. | None; TradeMonitor remains authority owner | HIGH | FUTURE / LOW PRIORITY | REJECTED | Rejected from TIAF scope; A8 integrates advice only. |
| DEF-006 | Option-expression selection and strategy templates | A0; reaffirmed A2.7/A2.8 | CAPABILITY_DEFERRAL | Factual underlying/chain evidence must precede contract and strategy choice. | Accepted opportunity view, option evidence, risk and liquidity policy | HIGH | A6 CLOSURE | PLANNED | Roadmap A6 owns expiry/strike/strategy comparison and may return no option trade. |
| DEF-007 | Market-calendar-aware source-observation recency | A1 | DEPENDENCY_DEFERRAL | Wall-time age alone cannot determine closed-market observation acceptability. | Exchange calendar/session contract | HIGH | A2 CLOSURE | DEFERRED | A1 preserves observation/retrieval time separately and makes no calendar claim. |
| DEF-008 | Provider fallback and Zerodha integration | A1/A1.5/A1.6 | CAPABILITY_DEFERRAL | Accepted A1 has one live provider and no fallback arbitration. | Second provider adapter, identity mapping, health and conflict policy | HIGH | A10 CLOSURE | DEFERRED | Dhan remains the only live adapter; fallback must not silently change provenance. |
| DEF-009 | Persistent/distributed cache and telemetry | A1/A1.6 | CAPABILITY_DEFERRAL | Current cache, metrics, scheduler, and single-flight state are process-local. | Operational evidence, storage/retention model, distributed consistency | MEDIUM | A10 CLOSURE | DEFERRED | Includes Redis/database/distributed-lock and Prometheus-style concerns only if justified. |
| DEF-010 | Deferred-work retry orchestration and continuous runtime queues | A1/A1.7 | CAPABILITY_DEFERRAL | A1 reports scheduler deferral truthfully but never sleeps, retries, or owns work order. | Runtime queue, retry/backoff, idempotency and restart policy | HIGH | A10 CLOSURE | DEFERRED | Roadmap A10 contains scheduler/queue and reliable long-running operation. |
| DEF-011 | Provider health/degradation arbitration | A1/A1.6 | CAPABILITY_DEFERRAL | Enable/disable and cooldown hooks exist without a full health model. | Health signals, thresholds, fallback and circuit-breaker policy | HIGH | A10 CLOSURE | DEFERRED | Must drive existing runtime boundaries without rewriting factual evidence. |
| DEF-012 | News, filings, fundamentals, macro, sector, and peer evidence adapters | A1 | DEPENDENCY_DEFERRAL | No accepted normalized source/provenance contracts exist for these evidence families. | Source selection, licensing, identity, time and quality contracts | HIGH | A3 CLOSURE | DEFERRED | A3 consumers may require these facts; acquisition stays outside Agents. |
| DEF-013 | Corporate-action normalization and adjusted history policy | A1 capability map | DEPENDENCY_DEFERRAL | Historical comparisons need explicit split/dividend adjustment semantics. | Authoritative corporate-action evidence and adjustment contract | HIGH | A2 CLOSURE | DEFERRED | No calculator may infer adjustments from price discontinuities. |
| DEF-014 | Authoritative option-chain market-event timestamp | A1/A2.7 | DEPENDENCY_DEFERRAL | Dhan currently exposes acquisition time but no authoritative event time. | Provider field or independently accepted timestamp source | MEDIUM | FUTURE / LOW PRIORITY | DEFERRED | A1/A2.7 explicitly label acquisition-time semantics instead of fabricating market time. |
| DEF-015 | Request-sized coordination for adapter-internal HTTP chunks | A1.6 | CAPABILITY_DEFERRAL | One coordinator callback may currently contain several adapter HTTP requests. | Per-request work decomposition and exact endpoint gating | MEDIUM | A10 CLOSURE | DEFERRED | Required only where strict per-call scheduling must cover internal chunks. |
| DEF-016 | Fuzzy symbol aliases and liquidity-based resolution preferences | A1.5 | CAPABILITY_DEFERRAL | Resolver deliberately performs exact/policy-visible identity selection only. | Authoritative alias source and explicit liquidity/preference policy | LOW | FUTURE / LOW PRIORITY | DEFERRED | Nearest-contract and option choice remain separate from identity resolution. |
| DEF-017 | First-class indicator framework/library | A2.1 | CAPABILITY_DEFERRAL | A2.1 established primitive feature contracts before named indicators. | Stable feature/context foundation | HIGH | A2 CLOSURE | IMPLEMENTED | Delivered in A2.4 with SuperTrend, RSI, MACD, ADX/DI, Bollinger, and Donchian. |
| DEF-018 | ADX and directional-indicator family | A2.3 | CAPABILITY_DEFERRAL | Multi-output Wilder semantics belonged in the indicator subsystem. | First-class indicator contracts | MEDIUM | A2 CLOSURE | IMPLEMENTED | Delivered and live-validated in A2.4. |
| DEF-019 | Redundant public structure-count aliases | A2.3 | INTENTIONAL_NON_GOAL | Duplicates would add names without distinct semantics. | A proven distinct consumer meaning | LOW | A2 CLOSURE | REJECTED | Existing transition fractions remain canonical unless a distinct contract is justified. |
| DEF-020 | Swing pivots and fractals | A2.3; reaffirmed A2.6 | DEPENDENCY_DEFERRAL | Right-side confirmation uses later bars and needs explicit availability time. | Confirmation/event-state and anti-lookahead contract | HIGH | AFTER EVENT-STATE FOUNDATION | DEFERRED | No hindsight pivot is registered. |
| DEF-021 | HalfTrend exact variant | A2.4 | DEPENDENCY_DEFERRAL | Public variants disagree on amplitude, ATR, channel, initialization, and reversal timing. | Named authoritative algorithm and known-fixture transition tests | MEDIUM | FUTURE / LOW PRIORITY | DEFERRED | Do not canonize an unreferenced variant by guesswork. |
| DEF-022 | Live-forming-bar indicator semantics | A2.4 | DEPENDENCY_DEFERRAL | Accepted indicators consume completed bars and never synthesize a current bar. | Event-time/current-bar lifecycle and revision contract | HIGH | AFTER EVENT-STATE FOUNDATION | DEFERRED | Live quote insertion remains forbidden until this contract exists. |
| DEF-023 | Alternate-timeframe indicator acquisition or resampling | A2.4; reaffirmed A2.8 | DEPENDENCY_DEFERRAL | Engines do not fetch or fabricate another interval. | Accepted resampling/session-boundary or explicit provider-acquisition contract | HIGH | A2 CLOSURE | DEFERRED | A2.8 obtains each timeframe independently; no resampling was added. |
| DEF-024 | Indicator parameter comparison and optimization | A2.4 | CAPABILITY_DEFERRAL | Calculation contracts intentionally contain no search or optimization policy. | Replay/evaluation data, objective function and leakage controls | MEDIUM | A7 CLOSURE | DEFERRED | A2.10 supplies baseline replay; broader learning/evaluation belongs to A7. |
| DEF-025 | Indicator strategy transitions and SigmaDSL rule integration | A2.4 | CAPABILITY_DEFERRAL | Factual indicator state is separate from entry/exit strategy interpretation. | Accepted strategy/rule contracts and evaluation boundary | HIGH | A6 CLOSURE | DEFERRED | Strategy transitions must consume, not redefine, indicator facts. |
| DEF-026 | Additional custom/proprietary built-in indicators | A2.4 capability map | CAPABILITY_DEFERRAL | Framework extensibility exists, but no unnamed algorithm should enter the built-in registry. | Named versioned formula, provenance and fixtures per indicator | LOW | FUTURE / LOW PRIORITY | DEFERRED | External calculators can already implement the protocol without engine changes. |
| DEF-027 | Session VWAP | A2.5 | DEPENDENCY_DEFERRAL | Correct calculation needs explicit intraday session boundaries. | Exchange calendar/session and completed-bar policy | HIGH | A2 CLOSURE | DEFERRED | Must not infer sessions from arbitrary lookback boundaries. |
| DEF-028 | Anchored VWAP | A2.5/A2.6 | DEPENDENCY_DEFERRAL | Anchor selection and information-time semantics are not yet contracted. | Explicit caller/event anchor contract | MEDIUM | AFTER EVENT-STATE FOUNDATION | DEFERRED | Separate from session VWAP. |
| DEF-029 | Volume profile, market profile, and profile-based levels | A2.5/A2.6 | DEPENDENCY_DEFERRAL | Binning, sessions, price allocation, and anchor rules need explicit variants. | Profile specification and session/binning contracts | MEDIUM | A2 CLOSURE | DEFERRED | Profile-based support/resistance must reuse the accepted profile evidence. |
| DEF-030 | OBV, MFI, Chaikin, and Accumulation/Distribution indicators | A2.5 | CAPABILITY_DEFERRAL | These are convention-bearing indicators, not primitive volume facts. | Named variants, warm-up semantics and indicator fixtures | MEDIUM | A2 CLOSURE | DEFERRED | Add through the A2.4 indicator registry, not the primitive feature engine. |
| DEF-031 | Percentile/rank participation features | A2.5 | DEPENDENCY_DEFERRAL | Empirical tie and reference-sample conventions are unspecified. | Explicit ranking/tie/window convention | LOW | A2 CLOSURE | DEFERRED | Existing range position is the unambiguous primitive. |
| DEF-032 | Delivery and participant statistics | A2.5 | DEPENDENCY_DEFERRAL | No normalized provider evidence currently exists. | Provider data source and normalized factual contracts | MEDIUM | A3 CLOSURE | DEFERRED | Missing evidence must not be inferred from OHLCV. |
| DEF-033 | Redundant above-average volume flags | A2.5 | INTENTIONAL_NON_GOAL | A boolean would duplicate the sign of an existing relative measurement. | A distinct, documented semantic need | LOW | A2 CLOSURE | REJECTED | Keep raw relative volume rather than proliferating aliases. |
| DEF-034 | Support/resistance touch counts | A2.6 | DEPENDENCY_DEFERRAL | Leakage-free counts need a boundary fixed before a distinct inspection window. | Two-window information-time contract and minimum-history rule | HIGH | AFTER EVENT-STATE FOUNDATION | DEFERRED | Ambiguous rolling-boundary shortcuts remain forbidden. |
| DEF-035 | Breakout persistence, re-entry, and failed-break event classification | A2.6 | DEPENDENCY_DEFERRAL | Correct run semantics require a frozen discovery/event boundary. | Event-state and replay foundation | HIGH | AFTER EVENT-STATE FOUNDATION | DEFERRED | Retrospectively moving rolling boundaries cannot define the event. |
| DEF-036 | Classic floor pivots | A2.6 | DEPENDENCY_DEFERRAL | Prior-session/calendar semantics must be explicit. | Exchange session/calendar and named formula variant | MEDIUM | A2 CLOSURE | DEFERRED | Belongs in a later level/indicator library. |
| DEF-037 | Volume-confirmed breakout and structural quality interpretation | A2.6 | CAPABILITY_DEFERRAL | A2.6 deliberately does not convert excursion plus volume into quality or action. | Accepted synthesis/scoring semantics and evaluation | MEDIUM | A3 CLOSURE | DEFERRED | Immediate A2.9 may use facts, but strategy interpretation remains later. |
| DEF-038 | Multi-timeframe support/resistance levels | A2.6; reaffirmed A2.8 | DEPENDENCY_DEFERRAL | Level identity and per-timeframe evidence must remain first-class before synthesis. | Explicit multi-timeframe level/indicator context | HIGH | A2 CLOSURE | DEFERRED | A2.8 aggregates selected FeatureBundle facts only. |
| DEF-039 | Delta-50 and richer strike-selection abstractions | A2.7 | CAPABILITY_DEFERRAL | Optional selection semantics require independent live validation. | Explicit selection convention and chain coverage evidence | MEDIUM | A6 CLOSURE | DEFERRED | A2.7 retains factual ATM/listed-strike geometry only. |
| DEF-040 | Historical option-bar feature library | A2.7 | CAPABILITY_DEFERRAL | A1.4 facts should feed a dedicated library rather than a second A2.7 subsystem. | Accepted historical-options feature contracts and replay use cases | HIGH | AFTER HISTORICAL DERIVATIVES FOUNDATION | DEFERRED | Reuse A1.4 normalized rolling history. |
| DEF-041 | OI-change temporal regimes and expiry-effect analysis | A2.7 | DEPENDENCY_DEFERRAL | One live snapshot cannot establish temporal change or expiry behavior. | Historical chain/option evidence aligned across observations | HIGH | AFTER HISTORICAL DERIVATIVES FOUNDATION | DEFERRED | No long/short buildup regime is inferred from static OI. |
| DEF-042 | Cross-expiry and term-structure analysis | A2.7 | DEPENDENCY_DEFERRAL | A2.7 intentionally consumes one explicit expiry. | Multi-chain evidence contract with simultaneous provenance | HIGH | AFTER HISTORICAL DERIVATIVES FOUNDATION | DEFERRED | Expiries must never be silently mixed. |
| DEF-043 | IV skew, smile, and surface models | A2.7 | DEPENDENCY_DEFERRAL | Surface interpolation and cross-strike/expiry conventions are unspecified. | Multi-strike/expiry surface contract and model versioning | MEDIUM | AFTER HISTORICAL DERIVATIVES FOUNDATION | DEFERRED | Provider IV facts remain unmodeled inputs. |
| DEF-044 | Expected-move and probability-of-profit models | A2.7 | DEPENDENCY_DEFERRAL | These require explicit probabilistic/model assumptions. | Named model, calibration, horizon and evaluation policy | MEDIUM | A6 CLOSURE | DEFERRED | ATM premium percentage is deliberately not labeled expected move. |
| DEF-045 | Max-pain variants | A2.7 | DEPENDENCY_DEFERRAL | Payoff, OI snapshot, expiry, and settlement conventions differ. | Named payoff/OI convention and validation | LOW | AFTER HISTORICAL DERIVATIVES FOUNDATION | DEFERRED | No implicit max-pain formula is accepted. |
| DEF-046 | Gamma exposure and dealer positioning | A2.7 | DEPENDENCY_DEFERRAL | Raw gamma/OI do not establish dealer sign or positioning assumptions. | Positioning source or explicit sign/model assumptions | MEDIUM | AFTER HISTORICAL DERIVATIVES FOUNDATION | DEFERRED | Provider gamma remains factual; dealer exposure is not inferred. |
| DEF-047 | Automatic benchmark and sector mapping | A2.8 | DEPENDENCY_DEFERRAL | No accepted provider-neutral sector/classification source exists. | Normalized classification evidence, versioning and mapping policy | HIGH | A3 CLOSURE | DEFERRED | A2.8 requires an explicit caller-supplied benchmark and role. |
| DEF-048 | Multi-timeframe SuperTrend aggregation | A2.8 | DEPENDENCY_DEFERRAL | SuperTrend lives in `IndicatorBundle`, separate from A2.8 `FeatureBundle` aggregation. | Explicit multi-timeframe indicator-context contract | MEDIUM | A2 CLOSURE | DEFERRED | Do not copy indicator state into feature bundles merely to aggregate it. |

## Immediate planned work deliberately not registered

The following are not deferrals because the accepted roadmap already places
them in the immediate remaining A2 sequence:

- deterministic market-state summary, horizon-aware baseline scoring, ranking,
  and candidate classes in A2.9;
- replay and deterministic baseline evaluation in A2.10.

Recommendation-bearing Agent conclusions remain represented by DEF-002, option
expression/strategy selection by DEF-006, and execution authority by DEF-005.
Those are later-layer boundaries, not A2.9 calculator work.

## Inventory summary

The initial audit recovered 48 stable records: A0 (6), A1 (10), A2.1 (1),
A2.3 (3), A2.4 (6), A2.5 (7), A2.6 (5), A2.7 (8), and A2.8 (2). A2.2 added no
distinct deferral beyond already planned A2.3 work. Current statuses are 38
DEFERRED, 4 PLANNED, 3 IMPLEMENTED, and 3 REJECTED.

The unresolved HIGH-priority IDs are DEF-007, DEF-008, DEF-010 through DEF-013,
DEF-020, DEF-022, DEF-023, DEF-025, DEF-027, DEF-034, DEF-035, DEF-038,
DEF-040 through DEF-042, and DEF-047. High-priority planned layer boundaries
are DEF-002, DEF-004, and DEF-006. Every one remains subject to roadmap order
and prerequisite satisfaction.

## A2.8 deferral summary

A2.8 introduced DEF-047 and DEF-048 and reaffirmed DEF-002, DEF-005, DEF-006,
DEF-023, and DEF-038. Scoring/ranking and replay were not added because they are
already scheduled as A2.9 and A2.10. No runtime behavior changed during this
documentation pass.
