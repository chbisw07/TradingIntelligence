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
| DEF-003 | TIAF service/API surface | A0 | CAPABILITY_DEFERRAL | Foundation milestones intentionally expose packages and diagnostics, not a service boundary. | Stable intelligence contracts and operational requirements | MEDIUM | FUTURE | PLANNED | Roadmap A8 includes the local service/API boundary. |
| DEF-004 | TradeMonitor intelligence integration | A0 | DEPENDENCY_DEFERRAL | Integration must preserve TradeMonitor risk, lifecycle, and authority. | Stable assessments, freshness/degradation, and evaluation feedback | HIGH | FUTURE | PLANNED | Roadmap A8 owns structured advice integration without authority transfer. |
| DEF-005 | Broker order placement/modification/cancellation by TIAF | A0; reaffirmed A1-A2.8 | INTENTIONAL_NON_GOAL | TIAF intelligence never owns broker execution authority. | None; TradeMonitor remains authority owner | HIGH | FUTURE | REJECTED | Rejected from TIAF scope; A8 integrates advice only. |
| DEF-006 | Option-expression selection and strategy templates | A0; reaffirmed A2.7/A2.8 | CAPABILITY_DEFERRAL | Factual underlying/chain evidence must precede contract and strategy choice. | Accepted opportunity view, option evidence, risk and liquidity policy | HIGH | A6 CLOSURE | PLANNED | Roadmap A6 owns expiry/strike/strategy comparison and may return no option trade. |
| DEF-007 | Market-calendar-aware source-observation recency | A1 | DEPENDENCY_DEFERRAL | Wall-time age alone cannot determine closed-market observation acceptability. | Exchange calendar/session contract | HIGH | A3 CLOSURE | DEFERRED | A1 preserves observation/retrieval time separately and makes no calendar claim. |
| DEF-008 | Provider fallback and Zerodha integration | A1/A1.5/A1.6 | CAPABILITY_DEFERRAL | Accepted A1 has one live provider and no fallback arbitration. | Second provider adapter, identity mapping, health and conflict policy | HIGH | FUTURE | DEFERRED | Dhan remains the only live adapter; fallback must not silently change provenance. |
| DEF-009 | Persistent/distributed cache and telemetry | A1/A1.6 | CAPABILITY_DEFERRAL | Current cache, metrics, scheduler, and single-flight state are process-local. | Operational evidence, storage/retention model, distributed consistency | MEDIUM | FUTURE | DEFERRED | Includes Redis/database/distributed-lock and Prometheus-style concerns only if justified. |
| DEF-010 | Deferred-work retry orchestration and continuous runtime queues | A1/A1.7 | CAPABILITY_DEFERRAL | A1 reports scheduler deferral truthfully but never sleeps, retries, or owns work order. | Runtime queue, retry/backoff, idempotency and restart policy | HIGH | FUTURE | DEFERRED | Roadmap A10 contains scheduler/queue and reliable long-running operation. |
| DEF-011 | Provider health/degradation arbitration | A1/A1.6 | CAPABILITY_DEFERRAL | Enable/disable and cooldown hooks exist without a full health model. | Health signals, thresholds, fallback and circuit-breaker policy | HIGH | FUTURE | DEFERRED | Must drive existing runtime boundaries without rewriting factual evidence. |
| DEF-012 | News, filings, fundamentals, macro, sector, and peer evidence adapters | A1 | DEPENDENCY_DEFERRAL | Production acquisition needs explicit source rights, identity, time, and quality semantics. | Source selection, licensing, identity, time and quality contracts | HIGH | A3 CLOSURE | DEFERRED | A3.4 implements fundamental contracts, deterministic normalization, a controlled gateway, and bounded caller-supplied/test adapter. A licensed production fundamental adapter plus news/macro/sector/peer acquisition remain; acquisition stays outside Agents. |
| DEF-013 | Corporate-action normalization and adjusted history policy | A1 capability map | DEPENDENCY_DEFERRAL | Historical comparisons need explicit split/dividend adjustment semantics. | Authoritative corporate-action evidence and adjustment contract | HIGH | A3 CLOSURE | DEFERRED | No calculator may infer adjustments from price discontinuities. |
| DEF-014 | Authoritative option-chain market-event timestamp | A1/A2.7 | DEPENDENCY_DEFERRAL | Dhan currently exposes acquisition time but no authoritative event time. | Provider field or independently accepted timestamp source | MEDIUM | FUTURE | DEFERRED | A1/A2.7 explicitly label acquisition-time semantics instead of fabricating market time. |
| DEF-015 | Request-sized coordination for adapter-internal HTTP chunks | A1.6 | CAPABILITY_DEFERRAL | One coordinator callback may currently contain several adapter HTTP requests. | Per-request work decomposition and exact endpoint gating | MEDIUM | FUTURE | DEFERRED | Required only where strict per-call scheduling must cover internal chunks. |
| DEF-016 | Fuzzy symbol aliases and liquidity-based resolution preferences | A1.5 | CAPABILITY_DEFERRAL | Resolver deliberately performs exact/policy-visible identity selection only. | Authoritative alias source and explicit liquidity/preference policy | LOW | FUTURE | DEFERRED | Nearest-contract and option choice remain separate from identity resolution. |
| DEF-017 | First-class indicator framework/library | A2.1 | CAPABILITY_DEFERRAL | A2.1 established primitive feature contracts before named indicators. | Stable feature/context foundation | HIGH | A2 CLOSURE | IMPLEMENTED | Delivered in A2.4 with SuperTrend, RSI, MACD, ADX/DI, Bollinger, and Donchian. |
| DEF-018 | ADX and directional-indicator family | A2.3 | CAPABILITY_DEFERRAL | Multi-output Wilder semantics belonged in the indicator subsystem. | First-class indicator contracts | MEDIUM | A2 CLOSURE | IMPLEMENTED | Delivered and live-validated in A2.4. |
| DEF-019 | Redundant public structure-count aliases | A2.3 | INTENTIONAL_NON_GOAL | Duplicates would add names without distinct semantics. | A proven distinct consumer meaning | LOW | A2 CLOSURE | REJECTED | Existing transition fractions remain canonical unless a distinct contract is justified. |
| DEF-020 | Swing pivots and fractals | A2.3; reaffirmed A2.6 | DEPENDENCY_DEFERRAL | Right-side confirmation uses later bars and needs explicit availability time. | Confirmation/event-state and anti-lookahead contract | HIGH | A3 CLOSURE | DEFERRED | No hindsight pivot is registered. |
| DEF-021 | HalfTrend exact variant | A2.4 | DEPENDENCY_DEFERRAL | Public variants disagree on amplitude, ATR, channel, initialization, and reversal timing. | Named authoritative algorithm and known-fixture transition tests | MEDIUM | FUTURE | DEFERRED | Do not canonize an unreferenced variant by guesswork. |
| DEF-022 | Live-forming-bar indicator semantics | A2.4 | DEPENDENCY_DEFERRAL | Accepted indicators consume completed bars and never synthesize a current bar. | Event-time/current-bar lifecycle and revision contract | HIGH | A3 CLOSURE | DEFERRED | Live quote insertion remains forbidden until this contract exists. |
| DEF-023 | Alternate-timeframe indicator acquisition or resampling | A2.4; reaffirmed A2.8 | DEPENDENCY_DEFERRAL | Engines do not fetch or fabricate another interval. | Accepted resampling/session-boundary or explicit provider-acquisition contract | HIGH | A2 CLOSURE | SUPERSEDED | A2.8 independently acquires each requested timeframe without resampling; first-class MTF indicator aggregation remains separately tracked by DEF-048. |
| DEF-024 | Indicator parameter comparison and optimization | A2.4 | CAPABILITY_DEFERRAL | Calculation contracts intentionally contain no search or optimization policy. | Replay/evaluation data, objective function and leakage controls | MEDIUM | FUTURE | DEFERRED | A2.10 supplies baseline replay; broader learning/evaluation belongs to A7. |
| DEF-025 | Indicator strategy transitions and SigmaDSL rule integration | A2.4 | CAPABILITY_DEFERRAL | Factual indicator state is separate from entry/exit strategy interpretation. | Accepted strategy/rule contracts and evaluation boundary | HIGH | A6 CLOSURE | DEFERRED | Strategy transitions must consume, not redefine, indicator facts. |
| DEF-026 | Additional custom/proprietary built-in indicators | A2.4 capability map | CAPABILITY_DEFERRAL | Framework extensibility exists, but no unnamed algorithm should enter the built-in registry. | Named versioned formula, provenance and fixtures per indicator | LOW | FUTURE | DEFERRED | External calculators can already implement the protocol without engine changes. |
| DEF-027 | Session VWAP | A2.5 | DEPENDENCY_DEFERRAL | Correct calculation needs explicit intraday session boundaries. | Exchange calendar/session and completed-bar policy | HIGH | A3 CLOSURE | DEFERRED | Must not infer sessions from arbitrary lookback boundaries. |
| DEF-028 | Anchored VWAP | A2.5/A2.6 | DEPENDENCY_DEFERRAL | Anchor selection and information-time semantics are not yet contracted. | Explicit caller/event anchor contract | MEDIUM | A3 CLOSURE | DEFERRED | Separate from session VWAP. |
| DEF-029 | Volume profile, market profile, and profile-based levels | A2.5/A2.6 | DEPENDENCY_DEFERRAL | Binning, sessions, price allocation, and anchor rules need explicit variants. | Profile specification and session/binning contracts | MEDIUM | FUTURE | DEFERRED | Profile-based support/resistance must reuse the accepted profile evidence. |
| DEF-030 | OBV, MFI, Chaikin, and Accumulation/Distribution indicators | A2.5 | CAPABILITY_DEFERRAL | These are convention-bearing indicators, not primitive volume facts. | Named variants, warm-up semantics and indicator fixtures | MEDIUM | A3 CLOSURE | DEFERRED | Add through the A2.4 indicator registry, not the primitive feature engine. |
| DEF-031 | Percentile/rank participation features | A2.5 | DEPENDENCY_DEFERRAL | Empirical tie and reference-sample conventions are unspecified. | Explicit ranking/tie/window convention | LOW | FUTURE | DEFERRED | Existing range position is the unambiguous primitive. |
| DEF-032 | Delivery and participant statistics | A2.5 | DEPENDENCY_DEFERRAL | No normalized provider evidence currently exists. | Provider data source and normalized factual contracts | MEDIUM | A3 CLOSURE | DEFERRED | Missing evidence must not be inferred from OHLCV. |
| DEF-033 | Redundant above-average volume flags | A2.5 | INTENTIONAL_NON_GOAL | A boolean would duplicate the sign of an existing relative measurement. | A distinct, documented semantic need | LOW | A2 CLOSURE | REJECTED | Keep raw relative volume rather than proliferating aliases. |
| DEF-034 | Support/resistance touch counts | A2.6 | DEPENDENCY_DEFERRAL | Leakage-free counts need a boundary fixed before a distinct inspection window. | Two-window information-time contract and minimum-history rule | HIGH | A3 CLOSURE | DEFERRED | Ambiguous rolling-boundary shortcuts remain forbidden. |
| DEF-035 | Breakout persistence, re-entry, and failed-break event classification | A2.6 | DEPENDENCY_DEFERRAL | Correct run semantics require a frozen discovery/event boundary. | Event-state and replay foundation | HIGH | A3 CLOSURE | DEFERRED | Retrospectively moving rolling boundaries cannot define the event. |
| DEF-036 | Classic floor pivots | A2.6 | DEPENDENCY_DEFERRAL | Prior-session/calendar semantics must be explicit. | Exchange session/calendar and named formula variant | MEDIUM | A3 CLOSURE | DEFERRED | Belongs in a later level/indicator library. |
| DEF-037 | Volume-confirmed breakout and structural quality interpretation | A2.6 | CAPABILITY_DEFERRAL | A2.6 deliberately does not convert excursion plus volume into quality or action. | Accepted synthesis/scoring semantics and evaluation | MEDIUM | A2 CLOSURE | SUPERSEDED | A2.9 transparently synthesizes separate participation and structural-readiness evidence; stateful breakout events remain DEF-035. |
| DEF-038 | Multi-timeframe support/resistance levels | A2.6; reaffirmed A2.8 | DEPENDENCY_DEFERRAL | Level identity and per-timeframe evidence must remain first-class before synthesis. | Explicit multi-timeframe level/indicator context | HIGH | A3 CLOSURE | DEFERRED | A2.8 aggregates selected FeatureBundle facts only. |
| DEF-039 | Delta-50 and richer strike-selection abstractions | A2.7 | CAPABILITY_DEFERRAL | Optional selection semantics require independent live validation. | Explicit selection convention and chain coverage evidence | MEDIUM | A6 CLOSURE | DEFERRED | A2.7 retains factual ATM/listed-strike geometry only. |
| DEF-040 | Historical option-bar feature library | A2.7 | CAPABILITY_DEFERRAL | A1.4 facts should feed a dedicated library rather than a second A2.7 subsystem. | Accepted historical-options feature contracts and replay use cases | HIGH | A6 CLOSURE | DEFERRED | Reuse A1.4 normalized rolling history. |
| DEF-041 | OI-change temporal regimes and expiry-effect analysis | A2.7 | DEPENDENCY_DEFERRAL | One live snapshot cannot establish temporal change or expiry behavior. | Historical chain/option evidence aligned across observations | HIGH | A6 CLOSURE | DEFERRED | No long/short buildup regime is inferred from static OI. |
| DEF-042 | Cross-expiry and term-structure analysis | A2.7 | DEPENDENCY_DEFERRAL | A2.7 intentionally consumes one explicit expiry. | Multi-chain evidence contract with simultaneous provenance | HIGH | A6 CLOSURE | DEFERRED | Expiries must never be silently mixed. |
| DEF-043 | IV skew, smile, and surface models | A2.7 | DEPENDENCY_DEFERRAL | Surface interpolation and cross-strike/expiry conventions are unspecified. | Multi-strike/expiry surface contract and model versioning | MEDIUM | A6 CLOSURE | DEFERRED | Provider IV facts remain unmodeled inputs. |
| DEF-044 | Expected-move and probability-of-profit models | A2.7 | DEPENDENCY_DEFERRAL | These require explicit probabilistic/model assumptions. | Named model, calibration, horizon and evaluation policy | MEDIUM | A6 CLOSURE | DEFERRED | ATM premium percentage is deliberately not labeled expected move. |
| DEF-045 | Max-pain variants | A2.7 | DEPENDENCY_DEFERRAL | Payoff, OI snapshot, expiry, and settlement conventions differ. | Named payoff/OI convention and validation | LOW | A6 CLOSURE | DEFERRED | No implicit max-pain formula is accepted. |
| DEF-046 | Gamma exposure and dealer positioning | A2.7 | DEPENDENCY_DEFERRAL | Raw gamma/OI do not establish dealer sign or positioning assumptions. | Positioning source or explicit sign/model assumptions | MEDIUM | A6 CLOSURE | DEFERRED | Provider gamma remains factual; dealer exposure is not inferred. |
| DEF-047 | Automatic benchmark and sector mapping | A2.8 | DEPENDENCY_DEFERRAL | No accepted provider-neutral sector/classification source exists. | Normalized classification evidence, versioning and mapping policy | HIGH | A3 CLOSURE | DEFERRED | A2.8 requires an explicit caller-supplied benchmark and role. |
| DEF-048 | Multi-timeframe SuperTrend aggregation | A2.8 | DEPENDENCY_DEFERRAL | SuperTrend lives in `IndicatorBundle`, separate from A2.8 `FeatureBundle` aggregation. | Explicit multi-timeframe indicator-context contract | MEDIUM | A3 CLOSURE | DEFERRED | Do not copy indicator state into feature bundles merely to aggregate it. |
| DEF-049 | Exact arbitrary historical point-in-time reconstruction | A2.10 | DEPENDENCY_DEFERRAL | Replay of captured evidence cannot prove what data, instruments, or revisions were available on an uncaptured historical date. | Point-in-time universe, corporate-action, data-vintage, and availability-time contracts | HIGH | FUTURE | DEFERRED | A2.10 prioritizes captured-snapshot replay and makes no synthetic historical-fidelity claim. |
| DEF-050 | Persistent database and distributed/large-scale replay farm | A2.10 | CAPABILITY_DEFERRAL | A filesystem JSON/JSONL corpus is sufficient for deterministic foundation and audit tests. | Retention, licensing, concurrency, job-control, and operational scale evidence | MEDIUM | FUTURE | DEFERRED | Content-addressed JSON and append-only local logs remain the accepted small-scale substrate. |
| DEF-051 | Scheduled provider-backed subsequent-outcome acquisition | A2.10 | DEPENDENCY_DEFERRAL | A2.10 defines provider-neutral later paths but does not wait, schedule, or backfill unfrozen decisions. | Exchange calendar, outcome acquisition policy, runtime queue, and data-retention rules | HIGH | FUTURE | DEFERRED | Tests use explicit historical fixtures; no newly captured assessment is given fabricated future data. |

## Immediate milestone work deliberately not registered

The following was not a deferral because the accepted roadmap placed it in the
immediate A2 sequence:

- replay and deterministic baseline evaluation in A2.10 (now implemented;
  live capture/replay validated and accepted at tag `tiaf-a2.10`).

Deterministic market-state summary, horizon-aware baseline scoring, ranking,
and candidate classes were delivered by A2.9 and therefore are neither open
deferrals nor additions to this register.

Recommendation-bearing Agent conclusions remain represented by DEF-002, option
expression/strategy selection by DEF-006, and execution authority by DEF-005.
Those are later-layer boundaries, not A2.9 calculator work.

## Inventory summary

The register contains 51 stable records: A0 (6), A1 (10), A2.1 (1), A2.3 (3),
A2.4 (6), A2.5 (7), A2.6 (5), A2.7 (8), A2.8 (2), and A2.10 (3). A2.2 and
A2.9 added no distinct records. Before the A2 closure review, statuses were 41
DEFERRED, 4 PLANNED, 3 IMPLEMENTED, and 3 REJECTED. After review, statuses are
39 DEFERRED, 4 PLANNED, 3 IMPLEMENTED, 3 REJECTED, and 2 SUPERSEDED.

The A2 closure disposition is: 0 IMPLEMENT NOW, 3 IMPLEMENTED ALREADY, 43
CARRY TO A3+, 3 REJECT, and 2 SUPERSEDE. `PLANNED` remains the register status
for four roadmap-owned later layers, but their closure disposition is still
`CARRY TO A3+` because they are not A2 work.

## A2 closure burn-down disposition

Every record introduced in A0, A1, or A2 received exactly one closure decision:

| ID | A2 closure decision | Revisit | Closure rationale |
|---|---|---|---|
| DEF-001 | IMPLEMENTED ALREADY | A1 CLOSURE | A1.1-A1.7 delivered provider-neutral factual acquisition and `AnalysisContext`. |
| DEF-002 | CARRY TO A3+ | A3 CLOSURE | Agent/LLM orchestration is the A3 purpose and must consume the frozen A2 substrate. |
| DEF-003 | CARRY TO A3+ | FUTURE | A service boundary needs later operational and integration requirements, not A2 calculators. |
| DEF-004 | CARRY TO A3+ | FUTURE | TradeMonitor integration remains an external A8 authority boundary. |
| DEF-005 | REJECT | FUTURE | TIAF never receives broker order authority; TradeMonitor remains the governor. |
| DEF-006 | CARRY TO A3+ | A6 CLOSURE | Option expression requires strategy, liquidity, and risk policy beyond factual A2 evidence. |
| DEF-007 | CARRY TO A3+ | A3 CLOSURE | No authoritative exchange-calendar/session contract exists; wall-time recency must not invent one. |
| DEF-008 | CARRY TO A3+ | FUTURE | A second provider, identity mapping, and conflict policy are still absent. |
| DEF-009 | CARRY TO A3+ | FUTURE | Distributed persistence and telemetry require demonstrated operational scale and retention policy. |
| DEF-010 | CARRY TO A3+ | FUTURE | Queue, retry, restart, and idempotency semantics belong to production operation. |
| DEF-011 | CARRY TO A3+ | FUTURE | Health arbitration needs signals, thresholds, circuit breaking, and provider fallback. |
| DEF-012 | CARRY TO A3+ | A3 CLOSURE | External evidence sources, licensing, identity, time, and quality contracts remain unselected. |
| DEF-013 | CARRY TO A3+ | A3 CLOSURE | No authoritative corporate-action feed or adjustment contract exists. |
| DEF-014 | CARRY TO A3+ | FUTURE | Dhan still provides acquisition time without an authoritative chain event timestamp. |
| DEF-015 | CARRY TO A3+ | FUTURE | Per-HTTP-call decomposition is an operational scheduler concern, not an A2 semantic gap. |
| DEF-016 | CARRY TO A3+ | FUTURE | Alias and liquidity preferences need authoritative data and explicit selection policy. |
| DEF-017 | IMPLEMENTED ALREADY | A2 CLOSURE | A2.4 delivered the extensible indicator contracts, registry, engine, and initial library. |
| DEF-018 | IMPLEMENTED ALREADY | A2 CLOSURE | A2.4 delivered live-validated Wilder ADX/+DI/-DI. |
| DEF-019 | REJECT | A2 CLOSURE | Public aliases would duplicate accepted transition-fraction semantics. |
| DEF-020 | CARRY TO A3+ | A3 CLOSURE | Right-side pivot confirmation still needs explicit event availability time. |
| DEF-021 | CARRY TO A3+ | FUTURE | No authoritative HalfTrend variant and transition fixture set has been selected. |
| DEF-022 | CARRY TO A3+ | A3 CLOSURE | Current-bar revision and event-time lifecycle contracts remain absent. |
| DEF-023 | SUPERSEDE | A2 CLOSURE | A2.8 supplies explicit independent provider acquisition per timeframe; DEF-048 retains the distinct indicator-aggregation need. |
| DEF-024 | CARRY TO A3+ | FUTURE | Optimization requires empirical objectives, leakage controls, and larger evaluation data. |
| DEF-025 | CARRY TO A3+ | A6 CLOSURE | Entry/exit transitions and SigmaDSL are strategy semantics, not indicator facts. |
| DEF-026 | CARRY TO A3+ | FUTURE | The protocol is extensible; no unnamed proprietary formula should be canonized. |
| DEF-027 | CARRY TO A3+ | A3 CLOSURE | Session VWAP remains blocked by explicit exchange-session semantics. |
| DEF-028 | CARRY TO A3+ | A3 CLOSURE | Anchored VWAP needs a caller/event anchor with information-time meaning. |
| DEF-029 | CARRY TO A3+ | FUTURE | Profile binning, allocation, session, and anchor variants remain unspecified. |
| DEF-030 | CARRY TO A3+ | A3 CLOSURE | Named formula and warm-up choices should be driven by a concrete consumer need. |
| DEF-031 | CARRY TO A3+ | FUTURE | Reference population, window, and tie conventions remain unspecified. |
| DEF-032 | CARRY TO A3+ | A3 CLOSURE | No normalized delivery/participant provider evidence exists. |
| DEF-033 | REJECT | A2 CLOSURE | A boolean above-average flag duplicates accepted relative-volume evidence. |
| DEF-034 | CARRY TO A3+ | A3 CLOSURE | Leakage-free touch counts still need a fixed boundary and separate inspection window. |
| DEF-035 | CARRY TO A3+ | A3 CLOSURE | Persistence/re-entry classification requires a frozen event boundary and state lifecycle. |
| DEF-036 | CARRY TO A3+ | A3 CLOSURE | Floor pivots require a named formula plus prior-session/calendar semantics. |
| DEF-037 | SUPERSEDE | A2 CLOSURE | A2.9 combines separate participation and structural-readiness contributions transparently; stateful events remain DEF-035. |
| DEF-038 | CARRY TO A3+ | A3 CLOSURE | First-class timeframe-specific level identity has not been contracted. |
| DEF-039 | CARRY TO A3+ | A6 CLOSURE | Delta-based strike selection is an option-expression policy decision. |
| DEF-040 | CARRY TO A3+ | A6 CLOSURE | A1.4 facts exist, but a historical-derivatives feature contract and use case do not. |
| DEF-041 | CARRY TO A3+ | A6 CLOSURE | OI change and expiry regimes require aligned temporal derivative observations. |
| DEF-042 | CARRY TO A3+ | A6 CLOSURE | Multi-expiry evidence and simultaneous provenance remain uncontracted. |
| DEF-043 | CARRY TO A3+ | A6 CLOSURE | Surface interpolation needs named, versioned cross-strike/expiry model semantics. |
| DEF-044 | CARRY TO A3+ | A6 CLOSURE | Expected-move/POP labels require explicit probabilistic assumptions and evaluation. |
| DEF-045 | CARRY TO A3+ | A6 CLOSURE | Max-pain payoff, snapshot, settlement, and expiry conventions remain ambiguous. |
| DEF-046 | CARRY TO A3+ | A6 CLOSURE | Dealer positioning cannot be inferred from unsigned provider gamma/OI facts. |
| DEF-047 | CARRY TO A3+ | A3 CLOSURE | No provider-neutral versioned classification source exists; benchmarks stay caller supplied. |
| DEF-048 | CARRY TO A3+ | A3 CLOSURE | An explicit MTF `IndicatorBundle` context is still needed; feature bundles must not impersonate it. |
| DEF-049 | CARRY TO A3+ | FUTURE | Point-in-time universes, revisions, corporate actions, and data-vintage contracts are absent. |
| DEF-050 | CARRY TO A3+ | FUTURE | The local content-addressed corpus is sufficient until retention, concurrency, and scale demand more. |
| DEF-051 | CARRY TO A3+ | FUTURE | Outcome scheduling needs calendars, queues, acquisition policy, and retention rules. |

No closure item qualified for `IMPLEMENT NOW`: every open candidate either has
an unresolved factual/session/event dependency, belongs to a later reasoning,
strategy, integration, evaluation, or operations layer, or lacks a precise
versioned specification. Adding one during closure would expand or destabilize
accepted A2 contracts without resolving a demonstrated acceptance defect.

### High-priority carry-forward rationale

Twenty-two HIGH-priority records are carried forward. Priority expresses their
importance once prerequisites exist; it is not permission to bypass layer order:

- **A3 evidence and event review:** DEF-007, DEF-012, DEF-013, DEF-020,
  DEF-022, DEF-027, DEF-034, DEF-035, DEF-038, and DEF-047. They were deferred
  because authoritative calendar, external-source, corporate-action,
  event-state, or MTF-level contracts are absent. Those dependencies remain
  unsatisfied. They could strengthen later consumers but are not required to
  make the accepted completed-bar A2 benchmark coherent, so revisit occurs at
  A3 closure rather than before A3 entry.
- **A3 reasoning boundary:** DEF-002. Its prerequisite—the accepted A2 evidence
  and replay baseline—is now satisfied, but implementing it would begin A3, so
  it is deliberately carried into A3 rather than pulled into closure.
- **A6 option/strategy boundary:** DEF-006, DEF-025, DEF-040, DEF-041, and
  DEF-042. A2 supplies factual indicator and single-expiry option evidence, but
  strategy policy, temporal derivatives, and multi-expiry contracts remain
  absent. These belong at or before the A6 closure, not in A2.
- **Integration/operations:** DEF-004, DEF-008, DEF-010, DEF-011, and DEF-051.
  They require TradeMonitor, another provider, health/conflict policy, durable
  queues, calendars, or schedulers. None is an A2 deterministic-calculator
  responsibility; revisit remains FUTURE under the existing A7/A8/A10 roadmap.
- **Historical fidelity:** DEF-049. Captured replay is implemented, but exact
  uncaptured historical reconstruction still lacks point-in-time universe,
  corporate-action, revision, and availability data. Claiming it now would
  create lookahead risk, so it remains FUTURE.

## A2.8 deferral summary

A2.8 introduced DEF-047 and DEF-048 and reaffirmed DEF-002, DEF-005, DEF-006,
DEF-023, and DEF-038. Scoring/ranking and replay were not added because they are
already scheduled as A2.9 and A2.10. No runtime behavior changed during this
documentation pass.

## A2.9 deferral summary

A2.9 introduced no new `DEF-*` records. It implemented the already-planned
deterministic synthesis and ranking layer without closing unrelated later-layer
work. In particular, market-calendar recency (DEF-007), live-forming bars
(DEF-022), strategy transitions (DEF-025), automatic benchmark mapping
(DEF-047), and a first-class multi-timeframe indicator context (DEF-048) remain
outside policy 1.0. Agent reasoning, option-expression selection, and execution
remain governed by DEF-002, DEF-006, and DEF-005 respectively.

## A2.10 deferral summary

A2.10 introduced DEF-049 through DEF-051 for arbitrary point-in-time
reconstruction, database/distributed replay scale, and scheduled provider-backed
outcome acquisition. Parameter optimization remains DEF-024 rather than being
duplicated. Agent and human evaluation await their later producer layers. The
completed A2 closure disposition is recorded above; A2.10 did not silently
expand into those later capabilities.
