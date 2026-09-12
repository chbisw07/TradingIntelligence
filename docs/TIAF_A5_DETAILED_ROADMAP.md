# TIAF A5 Detailed Roadmap

## 1. Status and document map

**A5.1/A5.2 accepted; R1 accepted; documentation ready for final freeze check.**
The intended tag is `tiaf-a5-baseline`; it does not exist at review entry and is
not created here. A1–A4 remain frozen. This consolidates delivered scope and
future seams without changing accepted policy or historical acceptance records.

| Stage | Governing record | Acceptance / disposition |
|---|---|---|
| Architecture | [Position Intelligence](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md), [review](TIAF_A5_ARCHITECTURE_REVIEW.md) | Approved single-position advisory boundary. |
| A5.1 | [Baseline](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md) | [Acceptance](STUDY_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE_ACCEPTANCE.md): captured-input contracts, deterministic advice, replay. |
| A5.2 | [Facade/Shell publication](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md) | [Acceptance](STUDY_A5_2_GOVERNED_POSITION_FACADE_SHELL_ACCEPTANCE.md): authorized captured reads and parity. |
| Closure | [A5 major closure](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md) | Historical READY_TO_FREEZE_A5; no tag created by that review. |
| R1 | [Implementation](TIAF_PLUGGABILITY_R1_REQUIRED_SCOPE_EXPLICIT_ABSENCE.md), [acceptance](TIAF_PLUGGABILITY_R1_ACCEPTANCE_AND_A5_FREEZE_READINESS.md) | Required-scope blocker closed; R2–R5 not required for A5 freeze. |
| Monitoring | [Authoritative architecture](TIAF_MONITORING_ARCHITECTURE.md) | Future admitted runtime mandate, not an A5 scheduler. |

## 2. Entry, identity and freshness

A5 assesses an existing position prospectively. Original entry rationale is
optional, but the baseline never invents an A4 thesis: missing linked A4 yields
INSUFFICIENT_EVIDENCE. Inputs are an authorized versioned snapshot, optional A4
result, explicit objective/horizon/`as_of`, cited normalized signals and optional
comparable predecessor/successor records.

Identity checks cover exact instrument/underlying/expiry, signed quantity/side,
position/snapshot identity, authority, source/version and timestamps. Snapshot
time cannot exceed decision `as_of` or precede entry. A4 IDs/fingerprints and
successor comparability must validate. Incoherent or forged contracts fail closed;
missing facts are never fetched or guessed.

Effective freshness uses wall-clock age and supplied basis. Stale/unknown truth
cannot yield MAINTAIN. Naive datetimes are rejected; timestamps normalize with
`ZoneInfo("Asia/Kolkata")` and JSON emits `+05:30`. Exchange-session recency is
DEF-007, not an implied holiday/calendar feature.

## 3. A5.1 delivered single-position baseline

`tiaf.a5` evaluates one open single-leg equity, future, call or put. Closed,
closing or unknown operational state abstains. Multi-leg input preserves shape
and returns UNSUPPORTED_SHAPE/insufficient evidence; legs are not flattened or
partially assessed.

Baseline `a5-policy:deterministic-single-position@1.0` checks shape, state,
freshness and missing A4 before expiry/time risk, invalidation, conflict,
weakening/risk, continuation, protection milestones, A4 disposition and supported
maintain. Rules are generic and versioned, not tuned to live examples.

| Dimension | Implemented meaning |
|---|---|
| Operational state | Supplied TM/broker truth, never changed by an analytical result. |
| Posture | CAPITAL_AT_RISK, RISK_REDUCED, PROFIT_PROTECTION_ACTIVE, UNDETERMINED. |
| Thesis health | INTACT, STRENGTHENED, WEAKENED, INVALIDATED, UNDETERMINED. |
| Recommendation | MAINTAIN, WATCH_CLOSELY, PROTECT, REDUCE_RISK, TRAIL_PROTECTION, EXIT_RECOMMENDED, WAIT_FOR_CONFIRMATION, ABSTAIN, INSUFFICIENT_EVIDENCE. |
| Remaining opportunity | Explicit supplied cited signal or UNKNOWN; not a probability. |

FREE is absent. TRAIL_PROTECTION is advice, not broker lifecycle or a trailing
order. A5 recomputes its whole small baseline; predecessor change references do
not imply incremental execution.

## 4. Protection and time/expiry risk

ProtectionIntent is non-executable and may reference only supplied cited levels.
A5 fabricates no stop, target, tick rounding, quantity, order type or hedge.
EXPRESSION_REFRESH_REQUIRED can flag a supplied unsuitable expression, but cannot
select a replacement, strike, expiry or roll.

Derivative expiry uses calendar days from aware `as_of`; near expiry heightens
review. Expiry or reached supplied mandatory-exit time may produce advisory
EXIT_RECOMMENDED only after truth/freshness gates. TM decides whether and how to
act; a recommendation never authorizes TI to close/modify a position.

## 5. Monitoring intent

MonitoringNeed carries family, typed trigger/reference, priority, freshness/
cadence hints, optional next-due hint, materiality and policy/budget refs.
WatchMandate preserves position/instrument, revision/predecessor and advisory
ACTIVE_POSITION/INACTIVE state. Inactivation emits no needs and does not alter
operational truth.

The [Monitoring Architecture](TIAF_MONITORING_ARCHITECTURE.md) preserves this
schema and normalizes advice into a distinct admitted MonitoringMandate.
Subscriber-owned optional watchlists organize intent; TI would govern recurrence.
Runtime lifecycle is separate from A5 labels; A5 never auto-registers/renews work.
Schedulers, leases, event ingress, notifications and durable recovery remain absent.

## 6. A5.2 delivered facade/Shell slice

`position.assess@1.0` is public deterministic CAPTURED_READ, requiring
ASSESS_POSITION and position-specific authority/entitlements. One logical
`position_request_ref` resolves a trusted complete request artifact, not a raw
path, account selector, URL or broker handle. Admission/read-time checks enforce
grants, lifecycle, scope, checksums and versions.

The facade matches subject, POSITION purpose, horizon and `as_of`, then delegates
unchanged A5 logic. Shell exposes `position assess --snapshot QUALIFIED_ID`,
human/JSON and bounded explain/trace. Generic `replay.recorded` handles A5_CAPTURE;
there is no new `position.replay` engine. Shell refresh re-enters admission over
the captured artifact; it does not acquire new live truth or rewrite the cutoff.

Results state ADVISORY_ONLY_TRADEMONITOR_DECIDES_BROKER_EXECUTION and
ADVISORY_MONITORING_INTENT_ONLY_NOT_SCHEDULED. This slice adds no provider/model/
broker call, remote service or caller policy injection.

## 7. Replay and acceptance

A5Capture retains snapshot, linked A4 where present, request/policy/result,
predecessor and intent with checksums/fingerprints. Recorded replay reconstructs;
verification rebuilds deterministically; `1.1-comparison` creates a separate
comparison, never a replacement baseline. Corruption/unsupported versions fail
without live repair. Leaf usage is known zero and parent refs remain visible.

Both studies and closure cover shape, identity, time, orthogonal result states,
protection, missing/failing inputs, authority, publication parity and replay.
This is synthetic/captured acceptance, not live TM/broker validation, multi-leg
success or forecasting calibration. Historical test counts remain in the studies;
no runtime suite is run or claimed anew by this documentation pass.

## 8. R1 and deferred downstream seams

R1 separates upstream Planner `1.1` declared scope from bindings: eight default
required roles and optional Macro, retaining contextual applicability. Required
absence stays in completeness; optional absence is not a negative opinion.
Legacy `1.0` capture/hash meaning survives; replay never adds today's contributors.
A5 evaluator, schema, policy and result meaning are unchanged by R1.

R2 descriptors, R3 additive composition/pinned verification, R4 optional import
isolation and R5 trusted COLD ownership remain separate pre-A6 work, not A5 freeze
requirements. No generic plugin system is delivered.

DEF-056 retains multi-leg combined-risk/hedge/leg-truth policy and its corpus.
DEF-004 retains A8 TM integration; DEF-010 retains A10 monitoring runtime;
DEF-003 retains remote transport. DEF-006 owns initial deterministic A6 candidates;
A7-informed enhanced comparison follows calibrated evidence. A7 is an overlay,
not an A5 prerequisite. Sector Rotation/Signal Qualification are future work,
not hidden requirements for single-position advice.

## 9. Documentation readiness and next gate

**A5 documentation set: complete** across design/review, implementations/studies,
closure, R1 acceptance and monitoring reconciliation. Runtime remains
single-position, captured-input and advisory.

Next prompt: **`TIAF_A5 — FINAL FREEZE / TAG READINESS CHECK`**. Inspect the exact
candidate tree and acceptance evidence before any separately authorized tag.
Documentation readiness is not tag creation or permission to implement A6/R2–R5.
The [implementation roadmap](IMPLEMENTATION_ROADMAP.md) owns subsequent ordering.
