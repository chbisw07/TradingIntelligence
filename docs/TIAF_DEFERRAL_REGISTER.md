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

The [post-A3 consolidation](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md) §6
classifies every stable ID and supplies the current delivery/revisit decisions.
Planning dispositions (for example SPLIT_WITHIN_SAME_STABLE_ID) are not register
status enums. Source foundation and the bounded local facade are completed
prerequisites, not new deferrals. DEF-003 remains `PLANNED` for its remote
service/API track; historical closure tables remain snapshots.
The [A4 major closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) keeps the
optional model/pricing and operational deferrals open, splits DEF-054 into a
planned minimal Shell renderer plus richer later report/Web work, and changes
only DEF-054's register status from `DEFERRED` to `PLANNED`.
The subsequent [Shell architecture review](TIAF_POST_A4_PRE_A5_TI_SHELL_ARCHITECTURE_REVIEW.md)
defined that bounded implementation candidate. The later
[Shell v0.1 implementation](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md) delivers the
minimal allowlisted local renderer. DEF-054 remains `PLANNED` because its richer
bibliography, hyperlink, report and Web portion is still open.
The [A5 architecture review](TIAF_A5_ARCHITECTURE_REVIEW.md) completes the
bounded monitoring-contract review without closing a deferral: it promotes only
immutable mandate/refresh intent. TM integration, calendars, scheduler/queue,
retry/recovery, operational telemetry and durable state retain their existing
IDs and later milestones.
The subsequent [A5.1 implementation](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md)
delivers that immutable intent plus local capture/replay. This is not a runtime
scheduler, TM integration, market calendar, durable store, or closure of the
operational deferrals.
The additive [A5.2 publication slice](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md)
adds governed local facade/Shell access and allowlisted A5 explanation/trace.
It changes no deferral status: rich reports remain under DEF-054, TM transport
under DEF-004, scheduling under DEF-010, and broker execution is still rejected
under DEF-005.
The [A5 major closure review](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
classifies the combined implementation as ready to freeze. It adds DEF-056 for
the explicit multi-leg interpretation deferral that previously existed only in
A5 scope prose. No new record is created solely for the exploratory Sector
Rotation note; existing TM, calendar, monitoring, storage and remote-service IDs
continue to govern those boundaries.

| ID | Capability | Deferred From | Category | Reason | Dependency / prerequisite | Priority | Suggested Revisit | Status | Resolution Notes |
|---|---|---|---|---|---|---|---|---|---|
| DEF-001 | Market-data adapters and factual fetch | A0 | CAPABILITY_DEFERRAL | Contracts preceded provider integration. | Stable provider-neutral data contracts | HIGH | A1 CLOSURE | IMPLEMENTED | Delivered through A1.1-A1.7, including Dhan and `AnalysisContext`. |
| DEF-002 | Agent and workflow reasoning layer | A0; reaffirmed A2.4/A2.8 | INTENTIONAL_NON_GOAL | Deterministic contracts/calculators must not contain judgment-oriented orchestration. | Accepted A2 factual baseline and evidence boundaries | HIGH | A3 CLOSURE | IMPLEMENTED | A3.1-A3.10 deliver bounded specialists, optional model-gateway contracts, Planner/orchestration, structured opportunity intelligence, and replay/cost/failure hardening. The accepted A3 path remains deterministic/no-LLM; A4 arbitration remains separate. Production model-backed reasoning is the distinct later capability in DEF-052. |
| DEF-003 | Governed TIAF public capability/service/API surface | A0; clarified A3 closure audit and post-A3 pass 1 | CAPABILITY_DEFERRAL | The governed same-process facade now exists, but no authenticated remote service/API surface exists. | Concrete remote consumer/isolation need, transport authentication/authorization, data rights and operations | MEDIUM | A8 / JUSTIFIED REMOTE NEED | PLANNED | [Local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) completes the selected bounded local track; A4.1 and A5.2 extend it to eight curated capabilities with trusted admission/lifecycle and no live operation. Remote service/API and TM integration remain A8 as required, with A10 operations. Both tracks retain this stable ID; completing the local slice does not claim the remote slice or close DEF-003. |
| DEF-004 | TradeMonitor intelligence integration | A0; clarified A5 architecture/A5 closure | DEPENDENCY_DEFERRAL | Integration must preserve TradeMonitor risk, lifecycle, and authority. | Stable assessments, freshness/degradation, and evaluation feedback | HIGH | A8 | PLANNED | A5 implements the versioned immutable snapshot/advice result and governed local publication but no TM transport or action. Roadmap A8 owns real integration without authority transfer. |
| DEF-005 | Broker order placement/modification/cancellation by TIAF | A0; reaffirmed A1-A2.8 and A5/A5.1 | INTENTIONAL_NON_GOAL | TIAF intelligence never owns broker execution authority. | None; TradeMonitor remains authority owner | HIGH | FUTURE | REJECTED | A5.1 emits `executable=false` advice/reference levels and no broker import. Rejected from TIAF scope; TM retains action authority. |
| DEF-006 | Option-expression selection and strategy templates | A0; reaffirmed A2.7/A2.8 | CAPABILITY_DEFERRAL | Factual underlying/chain evidence must precede contract and strategy choice. | Accepted opportunity view, option evidence, risk and liquidity policy | HIGH | A6 / A7 FOLLOW-UP | PLANNED | A6 first delivers deterministic valid candidates and explicit constraints; forecast-enhanced expression/comparison follows admitted A7 evidence. A6 retains contract selection and may return no option trade; higher-order comparison cannot invent candidates or bypass TM. |
| DEF-007 | Market-calendar-aware source-observation recency | A1; reviewed A5 architecture | DEPENDENCY_DEFERRAL | Wall-time age alone cannot determine closed-market observation acceptability. | Exchange calendar/session contract | HIGH | BEFORE SCHEDULED MONITORING | DEFERRED | A5 may evaluate an explicit age policy and emit freshness intent, but preserves observation/acquisition time separately and makes no calendar/session claim. |
| DEF-008 | Primary market-data fallback and Zerodha integration | A1/A1.5/A1.6 | CAPABILITY_DEFERRAL | Accepted A1 has one live quote/OHLCV/derivatives provider and no fallback arbitration for that surface. | Second primary market-data adapter, identity mapping, health and conflict policy | HIGH | FUTURE | DEFERRED | Dhan remains the only live primary market-data adapter. A3.6.1 separately implements Tapetide/Yahoo market-intelligence evidence fallback; that does not supply quote/OHLCV/F&O fallback and must not be reported as closing this record. |
| DEF-009 | Persistent/distributed cache and telemetry | A1/A1.6; reviewed A5 architecture | CAPABILITY_DEFERRAL | Current cache, metrics, scheduler, and single-flight state are process-local. | Operational evidence, storage/retention model, distributed consistency | MEDIUM | OPERATIONAL NEED / A10 | DEFERRED | A5 mandate/result contracts add no mutable or durable runtime state. Redis/database/distributed-lock, durable sparse Evidence Graph storage, and Prometheus-style concerns remain conditional on justified operations. |
| DEF-010 | Deferred-work retry orchestration and continuous runtime queues | A1/A1.7; clarified A3.8 and A5 closure | CAPABILITY_DEFERRAL | A1 reports scheduler deferral truthfully and A3.8 is bounded in-process orchestration; neither owns durable long-running work. | Runtime queue, retry/backoff, idempotency, checkpoint/resume, restart and late-work/preemption policy | HIGH | A10 RUNTIME | DEFERRED | A5 implements immutable mandate/trigger/next-due intent and remains on-demand. Dispatch, durable scheduling, retry, checkpoint/resume, adaptive cadence and triggered jobs remain A10 or an explicitly gated operational slice. A due hint is not a job guarantee. |
| DEF-011 | Provider health/degradation arbitration | A1/A1.6 | CAPABILITY_DEFERRAL | Enable/disable and cooldown hooks exist without a full health model. | Health signals, thresholds, fallback and circuit-breaker policy | HIGH | HOSTING NEED / A10 | DEFERRED | Must drive existing runtime boundaries without rewriting factual evidence. |
| DEF-012 | Broad production news, filing, fundamental, macro, sector, and peer acquisition | A1 | DEPENDENCY_DEFERRAL | Bounded adapters now exist, but production acquisition still needs explicit source rights, coverage, identity, time, quality, and operations semantics. | Licensed source selection, coverage policy, monitoring, and operational governance | HIGH | PRODUCTION SOURCE REVIEW | DEFERRED | A3.4-A3.6 provide canonical contracts/gateways. A3.6.1 implements provider declarations, routing, normalization, progressive enrichment, and read-only Tapetide/Yahoo paths. The authoritative-confirmation follow-up implements bounded configured NSE/BSE/company-IR acquisition, source validation, document provenance, and replay. These close the bounded A3 need, not broad production discovery/coverage or licensing; acquisition stays outside Agents. |
| DEF-013 | Corporate-action normalization and adjusted history policy | A1 capability map | DEPENDENCY_DEFERRAL | Historical comparisons need explicit split/dividend adjustment semantics. | Authoritative corporate-action evidence and adjustment contract | HIGH | BEFORE ADJUSTMENT-DEPENDENT A7 | DEFERRED | The authoritative-confirmation implementation can acquire and reconcile official corporate-action documents. Adjusted-history policy remains separate and deferred; no calculator may infer adjustments from price discontinuities. |
| DEF-014 | Authoritative option-chain market-event timestamp | A1/A2.7 | DEPENDENCY_DEFERRAL | Dhan currently exposes acquisition time but no authoritative event time. | Provider field or independently accepted timestamp source | MEDIUM | FUTURE | DEFERRED | A1/A2.7 explicitly label acquisition-time semantics instead of fabricating market time. |
| DEF-015 | Request-sized coordination for adapter-internal HTTP chunks | A1.6 | CAPABILITY_DEFERRAL | One coordinator callback may currently contain several adapter HTTP requests. | Per-request work decomposition and exact endpoint gating | MEDIUM | FUTURE | DEFERRED | Required only where strict per-call scheduling must cover internal chunks. |
| DEF-016 | Fuzzy symbol aliases and liquidity-based resolution preferences | A1.5 | CAPABILITY_DEFERRAL | Resolver deliberately performs exact/policy-visible identity selection only. | Authoritative alias source and explicit liquidity/preference policy | LOW | FUTURE | DEFERRED | Nearest-contract and option choice remain separate from identity resolution. |
| DEF-017 | First-class indicator framework/library | A2.1 | CAPABILITY_DEFERRAL | A2.1 established primitive feature contracts before named indicators. | Stable feature/context foundation | HIGH | A2 CLOSURE | IMPLEMENTED | Delivered in A2.4 with SuperTrend, RSI, MACD, ADX/DI, Bollinger, and Donchian. |
| DEF-018 | ADX and directional-indicator family | A2.3 | CAPABILITY_DEFERRAL | Multi-output Wilder semantics belonged in the indicator subsystem. | First-class indicator contracts | MEDIUM | A2 CLOSURE | IMPLEMENTED | Delivered and live-validated in A2.4. |
| DEF-019 | Redundant public structure-count aliases | A2.3 | INTENTIONAL_NON_GOAL | Duplicates would add names without distinct semantics. | A proven distinct consumer meaning | LOW | A2 CLOSURE | REJECTED | Existing transition fractions remain canonical unless a distinct contract is justified. |
| DEF-020 | Swing pivots and fractals | A2.3; reaffirmed A2.6 | DEPENDENCY_DEFERRAL | Right-side confirmation uses later bars and needs explicit availability time. | Confirmation/event-state and anti-lookahead contract | HIGH | FUTURE A2 EVENT CONTRACT | DEFERRED | No hindsight pivot is registered. |
| DEF-021 | HalfTrend exact variant | A2.4 | DEPENDENCY_DEFERRAL | Public variants disagree on amplitude, ATR, channel, initialization, and reversal timing. | Named authoritative algorithm and known-fixture transition tests | MEDIUM | FUTURE | DEFERRED | Do not canonize an unreferenced variant by guesswork. |
| DEF-022 | Live-forming-bar indicator semantics | A2.4 | DEPENDENCY_DEFERRAL | Accepted indicators consume completed bars and never synthesize a current bar. | Event-time/current-bar lifecycle and revision contract | HIGH | BEFORE FORMING-BAR FEATURES | DEFERRED | Live quote insertion remains forbidden until this contract exists. |
| DEF-023 | Alternate-timeframe indicator acquisition or resampling | A2.4; reaffirmed A2.8 | DEPENDENCY_DEFERRAL | Engines do not fetch or fabricate another interval. | Accepted resampling/session-boundary or explicit provider-acquisition contract | HIGH | A2 CLOSURE | SUPERSEDED | A2.8 independently acquires each requested timeframe without resampling; first-class MTF indicator aggregation remains separately tracked by DEF-048. |
| DEF-024 | Indicator parameter comparison and optimization | A2.4 | CAPABILITY_DEFERRAL | Calculation contracts intentionally contain no search or optimization policy. | Replay/evaluation data, objective function and leakage controls | MEDIUM | A7 | DEFERRED | A2.10 supplies baseline replay; broader learning/evaluation belongs to A7. |
| DEF-025 | Indicator strategy transitions and SigmaDSL rule integration | A2.4 | CAPABILITY_DEFERRAL | Factual indicator state is separate from entry/exit strategy interpretation. | Accepted strategy/rule contracts and evaluation boundary | HIGH | A6 CLOSURE | DEFERRED | Strategy transitions must consume, not redefine, indicator facts. |
| DEF-026 | Additional custom/proprietary built-in indicators | A2.4 capability map | CAPABILITY_DEFERRAL | Framework extensibility exists, but no unnamed algorithm should enter the built-in registry. | Named versioned formula, provenance and fixtures per indicator | LOW | FUTURE | DEFERRED | External calculators can already implement the protocol without engine changes. |
| DEF-027 | Session VWAP | A2.5 | DEPENDENCY_DEFERRAL | Correct calculation needs explicit intraday session boundaries. | Exchange calendar/session and completed-bar policy | HIGH | AFTER SESSION CONTRACT | DEFERRED | Must not infer sessions from arbitrary lookback boundaries. |
| DEF-028 | Anchored VWAP | A2.5/A2.6 | DEPENDENCY_DEFERRAL | Anchor selection and information-time semantics are not yet contracted. | Explicit caller/event anchor contract | MEDIUM | FUTURE A2 ANCHOR CONTRACT | DEFERRED | Separate from session VWAP. |
| DEF-029 | Volume profile, market profile, and profile-based levels | A2.5/A2.6 | DEPENDENCY_DEFERRAL | Binning, sessions, price allocation, and anchor rules need explicit variants. | Profile specification and session/binning contracts | MEDIUM | FUTURE | DEFERRED | Profile-based support/resistance must reuse the accepted profile evidence. |
| DEF-030 | OBV, MFI, Chaikin, and Accumulation/Distribution indicators | A2.5 | CAPABILITY_DEFERRAL | These are convention-bearing indicators, not primitive volume facts. | Named variants, warm-up semantics and indicator fixtures | MEDIUM | FUTURE A2 CONSUMER NEED | DEFERRED | Add through the A2.4 indicator registry, not the primitive feature engine. |
| DEF-031 | Percentile/rank participation features | A2.5 | DEPENDENCY_DEFERRAL | Empirical tie and reference-sample conventions are unspecified. | Explicit ranking/tie/window convention | LOW | FUTURE | DEFERRED | Existing range position is the unambiguous primitive. |
| DEF-032 | Delivery and participant statistics | A2.5 | DEPENDENCY_DEFERRAL | No normalized provider evidence currently exists. | Provider data source and normalized factual contracts | MEDIUM | PROVIDER EVIDENCE REVIEW | DEFERRED | Missing evidence must not be inferred from OHLCV. |
| DEF-033 | Redundant above-average volume flags | A2.5 | INTENTIONAL_NON_GOAL | A boolean would duplicate the sign of an existing relative measurement. | A distinct, documented semantic need | LOW | A2 CLOSURE | REJECTED | Keep raw relative volume rather than proliferating aliases. |
| DEF-034 | Support/resistance touch counts | A2.6 | DEPENDENCY_DEFERRAL | Leakage-free counts need a boundary fixed before a distinct inspection window. | Two-window information-time contract and minimum-history rule | HIGH | FUTURE A2 WINDOW CONTRACT | DEFERRED | Ambiguous rolling-boundary shortcuts remain forbidden. |
| DEF-035 | Breakout persistence, re-entry, and failed-break event classification | A2.6 | DEPENDENCY_DEFERRAL | Correct run semantics require a frozen discovery/event boundary. | Event-state and replay foundation | HIGH | EVENT/MONITORING REVIEW | DEFERRED | Retrospectively moving rolling boundaries cannot define the event. |
| DEF-036 | Classic floor pivots | A2.6 | DEPENDENCY_DEFERRAL | Prior-session/calendar semantics must be explicit. | Exchange session/calendar and named formula variant | MEDIUM | AFTER SESSION CONTRACT | DEFERRED | Belongs in a later level/indicator library. |
| DEF-037 | Volume-confirmed breakout and structural quality interpretation | A2.6 | CAPABILITY_DEFERRAL | A2.6 deliberately does not convert excursion plus volume into quality or action. | Accepted synthesis/scoring semantics and evaluation | MEDIUM | A2 CLOSURE | SUPERSEDED | A2.9 transparently synthesizes separate participation and structural-readiness evidence; stateful breakout events remain DEF-035. |
| DEF-038 | Multi-timeframe support/resistance levels | A2.6; reaffirmed A2.8 | DEPENDENCY_DEFERRAL | Level identity and per-timeframe evidence must remain first-class before synthesis. | Explicit multi-timeframe level/indicator context | HIGH | FUTURE A2 MTF LEVELS | DEFERRED | A2.8 aggregates selected FeatureBundle facts only. |
| DEF-039 | Delta-50 and richer strike-selection abstractions | A2.7 | CAPABILITY_DEFERRAL | Optional selection semantics require independent live validation. | Explicit selection convention and chain coverage evidence | MEDIUM | A6 CLOSURE | DEFERRED | A2.7 retains factual ATM/listed-strike geometry only. |
| DEF-040 | Historical option-bar feature library | A2.7 | CAPABILITY_DEFERRAL | A1.4 facts should feed a dedicated library rather than a second A2.7 subsystem. | Accepted historical-options feature contracts and replay use cases | HIGH | A6 CLOSURE | DEFERRED | Reuse A1.4 normalized rolling history. |
| DEF-041 | OI-change temporal regimes and expiry-effect analysis | A2.7 | DEPENDENCY_DEFERRAL | One live snapshot cannot establish temporal change or expiry behavior. | Historical chain/option evidence aligned across observations | HIGH | A6 CLOSURE | DEFERRED | No long/short buildup regime is inferred from static OI. |
| DEF-042 | Cross-expiry and term-structure analysis | A2.7 | DEPENDENCY_DEFERRAL | A2.7 intentionally consumes one explicit expiry. | Multi-chain evidence contract with simultaneous provenance | HIGH | A6 CLOSURE | DEFERRED | Expiries must never be silently mixed. |
| DEF-043 | IV skew, smile, and surface models | A2.7 | DEPENDENCY_DEFERRAL | Surface interpolation and cross-strike/expiry conventions are unspecified. | Multi-strike/expiry surface contract and model versioning | MEDIUM | A6 CLOSURE | DEFERRED | Provider IV facts remain unmodeled inputs. |
| DEF-044 | Expected-move and probability-of-profit models | A2.7 | DEPENDENCY_DEFERRAL | These require explicit probabilistic/model assumptions. | Named model, calibration, horizon and evaluation policy | MEDIUM | A6 / A7 | DEFERRED | Initial deterministic A6 cannot claim expected move or POP. Forecast-enhanced expression requires named model assumptions, horizon/availability/calibration provenance and A7 empirical evidence; ATM premium percentage is not expected move. |
| DEF-045 | Max-pain variants | A2.7 | DEPENDENCY_DEFERRAL | Payoff, OI snapshot, expiry, and settlement conventions differ. | Named payoff/OI convention and validation | LOW | A6 CLOSURE | DEFERRED | No implicit max-pain formula is accepted. |
| DEF-046 | Gamma exposure and dealer positioning | A2.7 | DEPENDENCY_DEFERRAL | Raw gamma/OI do not establish dealer sign or positioning assumptions. | Positioning source or explicit sign/model assumptions | MEDIUM | A6 CLOSURE | DEFERRED | Provider gamma remains factual; dealer exposure is not inferred. |
| DEF-047 | Automatic benchmark and sector mapping | A2.8 | DEPENDENCY_DEFERRAL | No accepted provider-neutral sector/classification source exists. | Normalized classification evidence, versioning and mapping policy | HIGH | CLASSIFICATION / A9 NEED | DEFERRED | A2.8 and A3.6 require explicit caller/provider-supplied benchmark/sector identity. A3.6 adds versioned effective-time mapping contracts but no automatic mapper. |
| DEF-048 | Multi-timeframe SuperTrend aggregation | A2.8 | DEPENDENCY_DEFERRAL | SuperTrend lives in `IndicatorBundle`, separate from A2.8 `FeatureBundle` aggregation. | Explicit multi-timeframe indicator-context contract | MEDIUM | FUTURE A2 MTF INDICATORS | DEFERRED | Do not copy indicator state into feature bundles merely to aggregate it. |
| DEF-049 | Exact arbitrary historical point-in-time reconstruction | A2.10; reviewed A5 architecture | DEPENDENCY_DEFERRAL | Replay of captured evidence cannot prove what data, instruments, or revisions were available on an uncaptured historical date. | Point-in-time universe, corporate-action, data-vintage, and availability-time contracts | HIGH | A7 HISTORICAL-DATA REVIEW | DEFERRED | A5 continues captured snapshot/A4/evidence replay only. A3.6.1 preserves availability/revision/PIT quality, but no exact uncaptured historical-fidelity claim is added. |
| DEF-050 | Persistent database and distributed/large-scale replay farm | A2.10; reviewed A5 architecture/A5.1 | CAPABILITY_DEFERRAL | A filesystem JSON/JSONL corpus is sufficient for deterministic foundation and audit tests. | Retention, licensing, concurrency, job-control, and operational scale evidence | MEDIUM | REPLAY SCALE / A10 | DEFERRED | A5.1 implements in-memory/content-addressed JSON capture and exact replay without a store service. Distributed persistence remains unjustified until scale/retention/concurrency evidence exists. |
| DEF-051 | Scheduled provider-backed subsequent-outcome acquisition | A2.10; reviewed A5 architecture | DEPENDENCY_DEFERRAL | A2.10 defines provider-neutral later paths but does not wait, schedule, or backfill unfrozen decisions. | Exchange calendar, outcome acquisition policy, runtime queue, and data-retention rules | HIGH | A7 POLICY / A10 RUNTIME | DEFERRED | A5 may emit a typed refresh/outcome need but does not schedule acquisition. A7 owns outcome definition/admission; calendars, durable dispatch and recovery remain A10 or an explicitly gated operational slice. |
| DEF-052 | Production model-backed specialist/reasoning integration | A3.2; reaffirmed A3.8-A3.10 and A4 closure | CAPABILITY_DEFERRAL | A3 defines a provider-neutral reasoning gateway and model provenance, while the accepted A4 baseline is deliberately deterministic/no-LLM and has no production model adapter or policy. | Role-aware gateway/adapter, privacy/egress, structured ID/value validation, governed tools, prompt/config versions, bounded usage/pricing, no-LLM control, replay and evaluation | MEDIUM | OPTIONAL A4 ENHANCEMENT / A7 / A10 | DEFERRED | A4 closure explicitly keeps model-backed challenge deferred: deterministic A4 is complete without it. Any later optional Challenger requires an additive role-aware gateway, approved adapter, versioned prompts/config, privacy/egress, structured ID/path/value validation, governed research scope, pricing/usage, no-LLM control, recorded replay and evaluation against the deterministic benchmark. Model priors motivate hypotheses only, never canonical facts. Broader production integration remains deferred. |
| DEF-053 | Cross-candidate A3 opportunity analysis and ranking | A3.9 | CAPABILITY_DEFERRAL | A3.9 intentionally emits one captured-underlying product and does not provide batch comparison, top-N selection or an A3 rank. | Stable single-subject products, explicit comparison objective, applicability policy, A4 arbitration boundary and A7 evaluation evidence | MEDIUM | A7 | DEFERRED | A2 ranking remains the deterministic benchmark. A future batch wrapper must preserve input order and must not turn A3 observations into an unexplained scalar leaderboard. |
| DEF-054 | User-facing explanation, source-citation and report rendering fabric | A3.9; reaffirmed A3 closure; clarified post-A3 pass 2, A4 closure, Shell implementation and A5.2 | CAPABILITY_DEFERRAL | The bounded Shell now renders admitted identifiers, reasons, gaps, contradictions plus A4/A5 lineage, but citation numbering, hyperlinks, bibliography, compression, source labels and Web/rich-report projection remain separate presentation work. | Accepted Core source semantics, A4/A5 lineage, governed local facade, and a bounded redaction/presentation policy | HIGH | LATER REPORT / WEB | PLANNED | Split within this stable ID. [Shell v0.1](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md) and [A5.2](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md) implement only deterministic allowlisted human/JSON, explain and trace projection without re-research. Rich bibliography/hyperlinks/report/Web work stays deferred; preserve scoped authority and original lineage. |
| DEF-055 | Provider/model monetary pricing catalog and cost attribution | A3.10 | DEPENDENCY_DEFERRAL | A3.10 correctly represents absent price knowledge as UNKNOWN/UNPRICED; configured cost units cannot establish billed monetary cost. | Versioned provider/model price sources, currency/effective-time semantics, billable-unit mapping and auditable attribution policy | MEDIUM | OPTIONAL MODEL GATE / A10 | DEFERRED | A bounded auditable price/currency/effective-time and billable-unit slice is required before claiming strict monetary caps for optional models; production catalog/attribution remains A10. UNKNOWN/UNPRICED is not zero or an invented nonzero estimate. Original billed usage, held unknown and replay usage stay separate; no pricing integration is implemented. |
| DEF-056 | Multi-leg A5 position interpretation | A5 architecture/A5 closure | CAPABILITY_DEFERRAL | A5.1/A5.2 deliberately preserve and reject multi-leg shape rather than flattening it; combined-premium, hedge, leg-dependency, partial-fill and aggregate-risk semantics are not accepted. | Concrete multi-leg consumer need; immutable leg/relationship truth; versioned combined-risk, invalidation and protection policy; replay corpus | MEDIUM | BOUNDED A5 EXTENSION / BEFORE MULTI-LEG CONSUMPTION | DEFERRED | The accepted A5 baseline remains single equity, future or single-leg option. Multi-leg input returns `UNSUPPORTED_SHAPE` and is never partially assessed. A later additive A5 policy may implement it without blocking A6 architecture, TM integration, or the single-position freeze. |

## Immediate milestone work deliberately not registered

The following was not a deferral because the accepted roadmap placed it in the
immediate A2 sequence:

- replay and deterministic baseline evaluation in A2.10 (now implemented;
  live capture/replay validated and accepted at tag `tiaf-a2.10`).

Deterministic market-state summary, horizon-aware baseline scoring, ranking,
and candidate classes were delivered by A2.9 and therefore are neither open
deferrals nor additions to this register.

At A2 closure, recommendation-bearing Agent conclusions were represented by
DEF-002, option expression/strategy selection by DEF-006, and execution
authority by DEF-005. The later A3 closure marks DEF-002 implemented while
leaving A4 arbitration separate; DEF-006 remains deferred and DEF-005 remains
rejected. None was A2.9 calculator work.

## Inventory summary

At A2 closure the register contained 51 stable records: A0 (6), A1 (10), A2.1
(1), A2.3 (3), A2.4 (6), A2.5 (7), A2.6 (5), A2.7 (8), A2.8 (2), and A2.10
(3). A2.2 and A2.9 added no distinct records. Before the A2 closure review,
statuses were 41
DEFERRED, 4 PLANNED, 3 IMPLEMENTED, and 3 REJECTED. After review, statuses are
39 DEFERRED, 4 PLANNED, 3 IMPLEMENTED, 3 REJECTED, and 2 SUPERSEDED. The A3
closure review changes DEF-002 from PLANNED to IMPLEMENTED, producing 39
DEFERRED, 3 PLANNED, 4 IMPLEMENTED, 3 REJECTED, and 2 SUPERSEDED. The later A3
sub-milestone discovery audit adds DEF-052 through DEF-055, and the A5 major
closure adds DEF-056. A4 subsequently moved DEF-054 from `DEFERRED` to
`PLANNED`. Current totals are therefore 56 records: 43 DEFERRED, 4 PLANNED, 4
IMPLEMENTED, 3 REJECTED, and 2 SUPERSEDED.

The A2 closure disposition is: 0 IMPLEMENT NOW, 3 IMPLEMENTED ALREADY, 43
CARRY TO A3+, 3 REJECT, and 2 SUPERSEDE. `PLANNED` remains the register status
for four roadmap-owned later layers, but their closure disposition is still
`CARRY TO A3+` because they are not A2 work.

## A2 closure burn-down disposition

Every record introduced in A0, A1, or A2 received exactly one closure decision:

> **Historical snapshot:** this table records the A2-closure decision as made
> at that time. Language such as “begin A3” or “A3 closure” is historical; the
> authoritative current disposition appears in the A3 closure and post-closure
> audit sections below, followed by the post-A3 consolidation linked above.

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

## A3 closure burn-down disposition

The 2026-09-11 A3 major closure review considered every record that was active
at the start of the review. `CLOSE_NOW` means the accepted A3 implementation
fully satisfies the recorded capability. `PROMOTE_TO_POST_A3_ARCH_REVIEW`
means architecture must be reconciled after the A3 freeze, not that runtime is
authorized now. `NEEDS_REWORDING` records were clarified in place and remain
deferred. No record is `MUST_FIX_BEFORE_A3_FREEZE`.

| ID | A3 closure classification | Evidence / reason | Owner or next review |
|---|---|---|---|
| DEF-002 | CLOSE_NOW | A3.1-A3.10 implement bounded specialist reasoning, Planner orchestration, structured opportunity intelligence and hardening over unchanged A2. Optional live LLM adapters and A4 arbitration are not part of this original record. | IMPLEMENTED in A3 |
| DEF-003 | PROMOTE_TO_POST_A3_ARCH_REVIEW | A3.9 exposes a typed in-process service seam, but `tiaf.app` is still bootstrap metadata and no governed public capability surface exists. | Post-A3 TI_CORE/public-capability consolidation; later A8 delivery |
| DEF-004 | KEEP_DEFERRED | No TradeMonitor integration or authority transfer was added. | A8 |
| DEF-006 | KEEP_DEFERRED | A3.7 interprets derivative context but deliberately selects no CE/PE, strike, expiry, strategy or quantity. | A6 closure |
| DEF-007 | PROMOTE_TO_POST_A3_ARCH_REVIEW | Aware timestamps and PIT rules exist, but no exchange-session/calendar recency contract does. | Post-A3 time/monitoring architecture; implementation later |
| DEF-008 | NEEDS_REWORDING | Tapetide/Yahoo fallback exists only for market-intelligence evidence; Dhan still has no primary quote/OHLCV/F&O fallback and Zerodha is absent. The register wording now makes that scope explicit. | Provider-operations review; later A10/A1 extension |
| DEF-009 | PROMOTE_TO_POST_A3_ARCH_REVIEW | A3 adds local caches, sparse graph state and a local corpus, not durable/distributed storage or telemetry. | Post-A3 system/monitoring architecture; A10 implementation |
| DEF-010 | PROMOTE_TO_POST_A3_ARCH_REVIEW | A3.8 has bounded in-request replans, not a durable retry queue, scheduler or restart policy. | Post-A3 monitoring architecture; A10 implementation |
| DEF-011 | PROMOTE_TO_POST_A3_ARCH_REVIEW | Typed provider failures and policy fallback exist, but health signals, circuit breaking and operational arbitration do not. | Post-A3 monitoring/provider-operations architecture; A10 implementation |
| DEF-012 | NEEDS_REWORDING | Bounded Tapetide, Yahoo and official-source adapters satisfy A3 evidence exercises; broad licensed discovery, production coverage and source governance do not. The record now says broad production acquisition. | Source/provenance architecture; later provider work |
| DEF-013 | PROMOTE_TO_POST_A3_ARCH_REVIEW | Official corporate-action documents can be acquired, but no adjusted-history contract or normalization policy exists. | Post-A3 source/PIT architecture; later A1/A2 extension |
| DEF-014 | KEEP_DEFERRED | Dhan option-chain evidence still has acquisition-time rather than authoritative market-event-time semantics. | Provider/data-contract review |
| DEF-015 | KEEP_DEFERRED | Strict per-HTTP-call scheduling inside adapter chunks is still an operational refinement without a demonstrated A3 defect. | A10/provider operations |
| DEF-016 | KEEP_DEFERRED | Fuzzy aliases and liquidity preference still lack an authoritative alias source and explicit policy. | Future identity-resolution work |
| DEF-020 | KEEP_DEFERRED | A3 replay does not supply the right-side-confirmation availability contract required for leakage-free pivots. | Future A2 indicator/structure work |
| DEF-021 | KEEP_DEFERRED | No authoritative HalfTrend variant or transition fixtures were selected. | Future indicator library |
| DEF-022 | PROMOTE_TO_POST_A3_ARCH_REVIEW | A3 uses completed evidence; it does not define live-forming-bar revision/event lifecycle semantics. | Post-A3 event/monitoring architecture; later A2 extension |
| DEF-024 | PROMOTE_TO_POST_A3_ARCH_REVIEW | Replay/evaluation substrates now exist, but objective, leakage controls and promotion policy remain A7 concerns. | Post-A3 forecasting/evaluation architecture; A7 |
| DEF-025 | KEEP_DEFERRED | No strategy transition or SigmaDSL interpretation was added. | A6 closure |
| DEF-026 | KEEP_DEFERRED | Extensibility exists; no named, versioned new indicator is justified. | Future indicator library |
| DEF-027 | KEEP_DEFERRED | Session VWAP still requires the missing exchange-session contract. | Future A2 indicator work after calendar contract |
| DEF-028 | KEEP_DEFERRED | Event records exist, but a caller/event anchor contract for VWAP does not. | Future A2 indicator work |
| DEF-029 | KEEP_DEFERRED | Profile binning, session and allocation variants remain unspecified. | Future indicator/level library |
| DEF-030 | KEEP_DEFERRED | No concrete consumer requirement selected named OBV/MFI/Chaikin/A-D variants and warm-up rules. | Future indicator library |
| DEF-031 | KEEP_DEFERRED | Ranking population, tie and window semantics remain unspecified. | Future deterministic feature work |
| DEF-032 | KEEP_DEFERRED | A3 market-intelligence sources do not provide an accepted normalized delivery/participant-statistics contract. | Future provider/evidence work |
| DEF-034 | KEEP_DEFERRED | A3 capture does not create the two-window information boundary required for leakage-free touch counts. | Future A2 structure work |
| DEF-035 | PROMOTE_TO_POST_A3_ARCH_REVIEW | Replay and event evidence now exist, but no canonical price-event state lifecycle fixes discovery, persistence and re-entry boundaries. | Post-A3 event/provenance architecture; later A2 extension |
| DEF-036 | KEEP_DEFERRED | Named floor-pivot formula and prior-session/calendar semantics remain absent. | Future level library after calendar contract |
| DEF-038 | KEEP_DEFERRED | A3 opinions consume scalar projections; no first-class timeframe-specific level identity was added. | Future A2 MTF-level work |
| DEF-039 | KEEP_DEFERRED | Delta-based strike selection remains an option-expression policy, not A3 derivatives context. | A6 closure |
| DEF-040 | KEEP_DEFERRED | A1.4 history exists, but no accepted historical-option feature contract/use case was added. | A6 closure |
| DEF-041 | KEEP_DEFERRED | Static/synthetic A3.7 cases do not establish aligned temporal OI or expiry regimes. | A6 closure |
| DEF-042 | KEEP_DEFERRED | A3.7 consumes one explicit expiry; simultaneous cross-expiry provenance remains absent. | A6 closure |
| DEF-043 | KEEP_DEFERRED | No named, versioned IV-surface model or interpolation policy exists. | A6 closure |
| DEF-044 | KEEP_DEFERRED | A3 explicitly forbids invented expected move or probability; calibration/model assumptions remain absent. | A6/A7 boundary review |
| DEF-045 | KEEP_DEFERRED | Max-pain convention remains ambiguous and A3 does not use it as a target/oracle. | A6 closure |
| DEF-046 | KEEP_DEFERRED | Provider gamma/OI still cannot prove dealer sign or positioning. | A6 closure |
| DEF-047 | PROMOTE_TO_POST_A3_ARCH_REVIEW | A3.6 adds explicit versioned mappings, not an automatic provider-neutral benchmark/sector classifier. | Post-A3 source/classification architecture |
| DEF-048 | KEEP_DEFERRED | A3 does not introduce a first-class MTF `IndicatorBundle` context. | Future A2 MTF-indicator work |
| DEF-049 | PROMOTE_TO_POST_A3_ARCH_REVIEW | Content-addressed captured replay is accepted; uncaptured historical truth still lacks universes, revisions, corporate actions and availability vintages. | Post-A3 provenance/PIT architecture; A7/A10 implementation as justified |
| DEF-050 | PROMOTE_TO_POST_A3_ARCH_REVIEW | A3.10 deliberately proves only a filesystem-scale append-only corpus. | Post-A3 system/storage architecture; A10 implementation |
| DEF-051 | PROMOTE_TO_POST_A3_ARCH_REVIEW | Outcome contracts exist, but no calendar-aware scheduled acquisition, queue or retention policy does. | Post-A3 monitoring/evaluation architecture; A7/A10 implementation |

The eight unavailable/richer derivatives families remain individually governed
by DEF-039 through DEF-046. A3.7's 2026-09-10 Dhan attempt failed before active
expiry evidence was acquired; synthetic specialist acceptance therefore does
not close live acquisition, historical-derivative, cross-expiry, surface,
probability, max-pain or dealer-positioning work.

### A3 closure totals

At review entry, 43 records were active: 39 DEFERRED and 4 PLANNED. The
disposition is 1 CLOSE_NOW, 27 KEEP_DEFERRED, 13
PROMOTE_TO_POST_A3_ARCH_REVIEW, 2 NEEDS_REWORDING, 0
MUST_FIX_BEFORE_A3_FREEZE and 0 newly obsolete/superseded. The two wording
corrections remain deferred. Register status after closure is 39 DEFERRED, 3
PLANNED, 4 IMPLEMENTED, 3 REJECTED and 2 SUPERSEDED.

The already resolved records remain explicit: DEF-001, DEF-017, DEF-018 and
DEF-002 are IMPLEMENTED; DEF-005, DEF-019 and DEF-033 are REJECTED; DEF-023
and DEF-037 are SUPERSEDED. No record was deleted or silently absorbed.

### Post-closure A3 sub-milestone discovery audit

The subsequent focused audit found four concrete A3-era omissions and added
DEF-052 through DEF-055. This does not rewrite the 43-record A3-closure-entry
snapshot above: those IDs were absent when that classification was performed.
All four are DEFERRED and none is a pre-freeze blocker. Corrected totals at that
post-A3 point were 55 records: 43 DEFERRED, 3 PLANNED, 4 IMPLEMENTED, 3
REJECTED, and 2 SUPERSEDED. The evidence and candidate matrix are in
[`STUDY_A3_SUBMILESTONE_DEFERRAL_DISCOVERY_AUDIT.md`](STUDY_A3_SUBMILESTONE_DEFERRAL_DISCOVERY_AUDIT.md).

## A5 closure burn-down disposition

The 2026-09-12 A5 major closure reviews the combined A5.1/A5.2 implementation.
Planning classifications refine, but do not replace, the stable register status.

| ID | A5 closure classification | Evidence / reason | Owner or next review |
|---|---|---|---|
| DEF-003 | SPLIT_WITHIN_STABLE_ID | Governed same-process facade/Python/Shell exposure is implemented; authenticated remote transport is not. | A8 / justified remote need |
| DEF-004 | KEEP_DEFERRED | A5 provides an immutable advisory handoff shape, not TM transport or action-time governance. | A8 |
| DEF-005 | REJECT | Broker order authority remains permanently outside TIAF. | TradeMonitor/broker |
| DEF-006 | PLANNED_NEXT | A5 emits only expression-refresh intent; deterministic option-expression candidates remain A6 work. | A6 |
| DEF-007 | KEEP_DEFERRED | Explicit wall-time freshness does not establish exchange-session/calendar recency. | Before scheduled monitoring/live TM policy |
| DEF-009 | KEEP_DEFERRED | Local immutable capture is sufficient; no durable/distributed operational trigger is proven. | A10 / operational need |
| DEF-010 | PARTIALLY_IMPLEMENTED / SPLIT_WITHIN_STABLE_ID | Immutable monitoring needs/mandates are implemented; queue, daemon, dispatch, retry and recovery remain absent. | A10 |
| DEF-011 | KEEP_DEFERRED | A5 makes no provider call and does not need to absorb provider-health operations. | A10 / hosting need |
| DEF-049 | KEEP_DEFERRED | Captured replay cannot reconstruct an uncaptured historical information set. | A7 historical-data review |
| DEF-050 | KEEP_DEFERRED | Exact local content-addressed replay is adequate until retention/concurrency/scale evidence exists. | A10 / replay scale |
| DEF-051 | KEEP_DEFERRED | Monitoring/outcome needs remain advisory and unscheduled. | A7 policy / A10 runtime |
| DEF-054 | PARTIALLY_IMPLEMENTED / SPLIT_WITHIN_STABLE_ID | Bounded A5 explain/trace is implemented; rich citation/report/Web output remains open. | Later report/Web |
| DEF-056 | KEEP_DEFERRED | Multi-leg shape is preserved and explicitly unsupported; combined-risk and hedge semantics need a separate versioned extension. | Bounded A5 extension when justified |

No existing status changes. DEF-056 adds one `DEFERRED` record. Current totals
are 56 records: 43 `DEFERRED`, 4 `PLANNED`, 4 `IMPLEMENTED`, 3 `REJECTED`, and
2 `SUPERSEDED`. None is `MUST_FIX_BEFORE_A5_FREEZE`.
