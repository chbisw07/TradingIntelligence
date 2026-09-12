# TIAF A5 Major Milestone Closure Review

## Status, scope, and decision

This review closes the implemented TIAF A5 major milestone on 2026-09-12
(Asia/Kolkata). It reviews the accepted A5.1 deterministic single-position
runtime and A5.2 governed facade/Shell publication as one position-intelligence
layer.

Review entry was clean at A5.2 commit `ef4bc2c`; its accepted A5.1 parent is
`247c4a0` and the architecture commit is `760dbd6`. The accepted upstream base
remains `tiaf-a4-baseline`. This closure changes documentation/governance and
removes a fixed wall-clock deadline from one synthetic A4.2 support fixture; it
does not alter A5 or any production runtime semantics.

**Closure decision: `READY_TO_FREEZE_A5`.**

The recommended major tag is `tiaf-a5-baseline`. This pass does not create the
tag. Its meaning is deliberately bounded: deterministic single-position advice,
governed captured-read facade/Python/Shell exposure, replay, failure, and
authority boundaries are accepted; multi-leg interpretation, live TM/broker
integration, and monitoring runtime remain deferred.

## 1. North-star alignment and delivered scope

A5 acts in the user's economic interest by making current-position truth a hard
input, preserving the accepted A4 thesis and contradictions, failing closed when
truth is stale or incomplete, and separating analytical advice from execution.
It provides:

- immutable, versioned single-equity, single-future, and single-leg-option
  snapshot/request/result contracts;
- strict identity, signed-quantity, instrument, expiry, authority, and aware-time
  validation;
- deterministic analytical posture, thesis health, recommendation, remaining
  opportunity, and non-executable protection intent;
- immutable monitoring needs and a minimal position-linked `WatchMandate`;
- content-addressed capture, recorded replay, deterministic verification, and
  policy comparison;
- authority-scoped `position.assess@1.0` captured-read publication; and
- bounded Python-facade and `position assess` Shell consumption with structured
  explain/trace projection.

A5 does not acquire broker state, place or modify orders, select a replacement
option expression, generate forecasts, rerun A4, schedule monitoring, or claim
profitability. Known deterministic usage is zero provider/model calls, zero
tokens, and zero model cost.

## 2. Integrated A5.1/A5.2 flow and ownership

The audited path is:

```text
authorized TM/broker position snapshot supplied in a trusted artifact
  -> A5 identity/freshness/A4-lineage validation
  -> deterministic posture and thesis health
  -> recommendation and non-executable protection intent
  -> monitoring need / optional expression-refresh hint
  -> position.assess captured-read facade
  -> trusted Python client or bounded TI_SHELL projection
```

`tiaf.a5` owns contracts, deterministic evaluation, monitoring-intent
construction, capture, and replay. Trusted facade composition owns grants,
logical artifacts, lifecycle, and invocation. The Shell is a command adapter
over that facade. TM/broker owns operational position truth and action; A6 will
own expression construction; A7 owns calibrated forecast/evaluation evidence.

No hidden broker lookup, provider/model call, live execution, multi-leg
flattening, A6 invocation, A7 probability, or scheduler side effect exists in
the path. A5.2 delegates to the unchanged A5.1 evaluator and preserves the
canonical result and run fingerprint.

## 3. Position truth, identity, and freshness

The supplied versioned snapshot is the only operational truth. It retains
position/snapshot/TM references, operational source and state, snapshot time,
declared freshness and basis, signed quantity, contract identity, and authority
references. Snapshot time after `as_of`, entry/snapshot inversion, side/quantity
incoherence, instrument/expiry mismatch, malformed shape, or missing authority
fails validation.

Freshness policy is explicit and sufficient for captured/on-demand A5: the
caller declaration and a versioned 900-second wall-clock ceiling produce
`CURRENT`, `STALE`, `UNKNOWN`, or `INVALID`. Stale/unknown/invalid or non-open
truth precedes all favorable rules and yields `ABSTAIN`; no last-known snapshot
is promoted to current. Exchange-session awareness remains DEF-007 and must be
resolved before unattended calendar-sensitive monitoring or live TM policy.

Contracts and captures reject credential-shaped content. No broker handle,
credential, account client, or live session enters an A5 result or replay.

## 4. Orthogonal analytical dimensions

### Posture

`CAPITAL_AT_RISK`, `RISK_REDUCED`, `PROFIT_PROTECTION_ACTIVE`, and
`UNDETERMINED` are analytical classifications, not broker/order states.
`RISK_REDUCED` does not prove a protective order, and
`PROFIT_PROTECTION_ACTIVE` describes a cited analytical protection mode, not an
active trailing order. Exact action remains outside A5. `FREE` remains rejected
because it would overstate residual risk. Posture is not redundant with
recommendation: it describes present analytical exposure, while recommendation
describes the next advisory response.

### Thesis health

`INTACT`, `STRENGTHENED`, `WEAKENED`, `INVALIDATED`, and `UNDETERMINED` are
derived only from validated linked A4 results and supplied cited signals. The
original A4 object and fingerprint remain immutable. A comparable successor A4
result is explicit, lineage-checked, and may change A5 health without rewriting
history. A5 neither invokes nor reconstructs A4.

### Recommendation

The nine outcomes remain distinct:

| Recommendation | Audited meaning |
| --- | --- |
| `MAINTAIN` | Current truth and a supported intact thesis permit continued exposure; no execution instruction. |
| `WATCH_CLOSELY` | Heightened review/refresh is warranted. |
| `PROTECT` | Seek stronger protection under downstream policy; no order or exact stop. |
| `REDUCE_RISK` | Semantically reduce exposure; quantity and method remain TM-owned. |
| `TRAIL_PROTECTION` | Preserve gains dynamically as advice, not a broker trailing order. |
| `EXIT_RECOMMENDED` | Consider full exit; successful advice, never order submission. |
| `WAIT_FOR_CONFIRMATION` | A material, potentially resolvable conflict remains. |
| `ABSTAIN` | Current position truth/state is unsafe for an action recommendation. |
| `INSUFFICIENT_EVIDENCE` | Position truth may be usable, but required thesis/evidence is absent. |

The ordered policy evaluates unsupported shape, operational state, and
freshness before thesis/recommendation logic. Failure cannot default to
`MAINTAIN`. No taxonomy item requires a pre-freeze rename.

## 5. Protection, shape, horizon, and time risk

`ProtectionIntent` is typed and always `executable=false`. It may preserve only
caller-supplied, cited structural levels; run validation rejects an invented
level. It contains no tick rounding, option-premium conversion, order type,
quantity, broker payload, or fabricated stop/target. It is sufficient as an
advisory handoff because A6/TM can consume the semantic intent and references
without treating them as executable.

A5 supports a single equity, future, call, or put. A declared multi-leg shape
returns `UNSUPPORTED_SHAPE` plus an insufficient outcome before any leg is
evaluated; it is never flattened, partly assessed, or converted to aggregate
premium truth.

**Multi-leg closure recommendation: `KEEP_DEFERRED`.** The current baseline is a
complete useful single-position capability. Combined-premium, hedge,
leg-dependency, partial-fill, and aggregate-risk semantics need a separate
versioned A5 extension after a concrete consumer requirement; they do not block
the honest single-leg baseline freeze.

Horizon is first-class in requests, needs, and mandates. Derivative expiry must
match instrument identity. Aware `as_of` supplies deterministic calendar-day
expiry pressure; expired positions get conservative `EXIT_RECOMMENDED`, and
near-expiry positions get `WATCH_CLOSELY` plus time-risk intent. A supplied
intraday exit window is handled similarly. No roll, strike, expiry, hedge, or
replacement is selected.

## 6. Monitoring contract and TBD disposition

`MonitoringNeed` preserves position, objective/horizon, evidence family, typed
trigger/reference, priority, freshness/cadence hints, optional `next_due_at`,
reason/materiality, and policy/budget references. `WatchMandate` adds immutable
identity/revision/predecessor, instrument/position linkage,
`ACTIVE_POSITION`/`INACTIVE`, authority, and the need tuple.

These values are advisory only. A need is not active work, `next_due_at` is not
a job guarantee, priority is not queue order, and mandate inactivation neither
closes nor changes the supplied position. Future dispatch must re-check position
truth and authority.

The exploratory monitoring note is classified as follows:

| Area | Disposition | Closure meaning |
| --- | --- | --- |
| Position-linked mandate identity, immutable revision/lineage, shared-instrument separation | `PROMOTED` | Implemented by A5.1 contracts and pure construction. |
| Lifecycle, evidence-family needs, triggers, freshness/cadence/next-due intent, priority and budget/policy refs | `PARTIALLY_PROMOTED` | Only `ACTIVE_POSITION`/`INACTIVE` and advisory hints are implemented; no runtime semantics are implied. |
| Candidate `PASSIVE`/`ACTIVE_WATCH`, shared candidate mandates, full acquisition profiles, dependency graph/incremental execution, adaptive policies | `KEEP_TBD` | Requires later architecture and evidence. |
| Live position binding, TM admission/rejection, action-time truth/lifecycle | `REVISIT_A8` | A8 owns operational TM integration without authority transfer. |
| Candidate/watchlist population and scanner-created mandates | `REVISIT_A9` | A9 owns scanner/candidate intake. |
| Calendar-aware cadence, queue/worker/daemon, dispatch, retry/recovery, persistence, telemetry, load, and runtime audit | `REVISIT_A10` | Operationalization remains DEF-007/009/010/051. |
| UI color as domain state; mutable mandate as job state; due hint as service promise; scheduler inside specialists | `REJECT` | These meanings are incompatible with the accepted boundaries. |

The result is `PARTIALLY_PROMOTED`, not a monitoring-runtime claim.

## 7. Sector Rotation interaction

The Sector Rotation note remains a non-authoritative exploratory workstream and
is not part of A5 scope or acceptance. A future A5 policy may consume admitted,
versioned sector-tailwind health and deterioration evidence, but must preserve
stock-specific evidence and must not force an exit from sector state alone.
Mapping future weakening/deterioration to `WATCH_CLOSELY`, `PROTECT`,
`REDUCE_RISK`, or `EXIT_RECOMMENDED` requires a separately accepted versioned
policy. Its absence is not an A5 freeze blocker, and this closure promotes none
of that TBD design.

## 8. Facade and Shell publication

`position.assess@1.0` is typed, versioned, deterministic, `CAPTURED_READ`,
known-zero, and protected by `ASSESS_POSITION`, caller capability, operator
policy, authority, entitlement, budget/profile, and lifecycle intersection.
It accepts one qualified logical reference to a trusted complete A5 request;
paths, URLs, caller policy objects, providers, brokers, registries, and
self-granted authority are rejected. The artifact is reread after admission and
embedded authority/identity/fingerprint checks fail closed. Stale and multi-leg
domain results remain canonical rather than becoming opaque process failures.
Serializable request/results leave a future transport seam without authorizing
one now.

The one-shot and REPL Shell share one parser and dispatcher. `position assess`
returns the exact facade result; `explain last` projects existing structured
fields and `trace last` exposes allowlisted identities, lineage, timing, and
known-zero usage. Session `last`/refresh pointers grant no authority and refresh
performs a new admitted read without claiming a newer snapshot. Domain
`EXIT_RECOMMENDED`, `ABSTAIN`, and insufficient outcomes are successful command
executions. Execution-like position verbs are absent, and trace excludes prices,
quantities, broker payloads, credentials, private objects, and hidden reasoning.

## 9. Replay, integrity, and degradation

An `A5Capture` seals exact position snapshot bytes, linked current A4 result
when present, complete run/request/policy/result/monitoring content, checksums,
semantic/run fingerprints, and capture time. Successor requests carry previous
result/mandate lineage and explicit changed inputs.

- Recorded replay reconstructs the exact run with zero broker/provider/model/TM
  or network access.
- Deterministic verification reevaluates the captured request/policy and requires
  exact run and result-fingerprint parity.
- Policy comparison creates a distinct candidate run/comparison record and does
  not rewrite history.
- Missing/corrupt snapshot, A4, run, exact checksum, fingerprint, policy, version,
  kind, authority, or entitlement fails closed; no live repair occurs.

Stale snapshot, unknown freshness, non-open state, missing A4, expired contract,
unsupported shape, insufficient evidence, conflict, corruption, policy mismatch,
unsupported version, and foreign/unauthorized artifacts remain typed and
conservative. None becomes `MAINTAIN` by fallback.

## 10. TM, A6, and A7 seams

Every result repeats
`ADVISORY_ONLY_TRADEMONITOR_DECIDES_BROKER_EXECUTION`. Its result/advice ID,
position and snapshot identity/freshness, policy/schema, recommendation, and
fingerprints are sufficient for an idempotent future handoff. TM may accept,
reject, adapt, or ignore advice; none of those responses mutates A5 history.
Live TM transport is not required for freeze.

`EXPRESSION_REFRESH_REQUIRED` is the complete current A6 seam. It selects no
strike, expiry, hedge, quantity, roll, or replacement and invokes no A6 code.
The immutable result can be consumed later without changing A5 semantics.

A5 works with zero forecast evidence and emits no probability, expected return,
target-hit chance, or distribution. A7 remains the calibration/evaluation owner.

## 11. Deferral burn-down

Planning classifications below refine the register's stable statuses; they do
not invent a partial status. One omitted but explicit A5 capability is now
recorded as DEF-056 rather than remaining only in prose.

| ID / area | Closure classification | Result after A5 |
| --- | --- | --- |
| DEF-003 remote/public service | `SPLIT_WITHIN_STABLE_ID` | Local facade/Python/Shell is implemented; remote transport remains `PLANNED` for A8/justified isolation. |
| DEF-004 TM integration | `KEEP_DEFERRED` | Stable advisory seam exists; TM transport/action-time policy remains `PLANNED` for A8. |
| DEF-005 broker execution | `REJECT` | Remains permanently `REJECTED`; TIAF has no broker action authority. |
| DEF-006 option expression | `PLANNED_NEXT` | A6 owns deterministic valid expression candidates; A5 adds no selection. |
| DEF-007 market-calendar recency | `KEEP_DEFERRED` | Wall-time freshness is honest; session-aware policy is required before scheduling/live integration. |
| DEF-009 durable storage/telemetry | `KEEP_DEFERRED` | Local immutable capture is sufficient; no operational scale trigger exists. |
| DEF-010 monitoring queue/runtime | `PARTIALLY_IMPLEMENTED` / `SPLIT_WITHIN_STABLE_ID` | Immutable mandate/need intent is implemented; queue, dispatch, retry, recovery, and daemon remain `DEFERRED` for A10. |
| DEF-011 provider health | `KEEP_DEFERRED` | A5 makes no provider call; operational health arbitration remains later work. |
| DEF-049 arbitrary historical PIT | `KEEP_DEFERRED` | Captured replay does not reconstruct uncaptured historical truth. |
| DEF-050 persistent/distributed replay | `KEEP_DEFERRED` | Content-addressed local replay is sufficient until retention/concurrency/scale justify more. |
| DEF-051 scheduled outcome/refresh acquisition | `KEEP_DEFERRED` | Needs are advisory; A7 owns outcome policy and A10 owns durable scheduling. |
| DEF-054 rich reports | `PARTIALLY_IMPLEMENTED` / `SPLIT_WITHIN_STABLE_ID` | Bounded A5 Shell explain/trace exists; rich bibliography/Web remains `PLANNED`. |
| DEF-056 A5 multi-leg interpretation | `KEEP_DEFERRED` | Explicit unsupported behavior is accepted; later policy needs combined-risk and hedge semantics. |
| Sector Rotation TBD | `KEEP_TBD` | No register item is created solely for the exploratory note; future promotion must be separately reviewed. |

After adding DEF-056, the register contains 56 stable IDs: 43 `DEFERRED`, 4
`PLANNED`, 4 `IMPLEMENTED`, 3 `REJECTED`, and 2 `SUPERSEDED`.

## 12. Live-validation truth table

| Surface | Status | Truthful scope |
| --- | --- | --- |
| A5 deterministic policy | `REPLAY_VALIDATED` | Synthetic/captured single-position scenarios, deterministic rerun, policy comparison, and exact fingerprints. |
| Facade/Python/Shell exposure | `SYNTHETIC_ONLY` | Authorized local captured artifacts prove direct/facade/Shell parity; no live broker snapshot was used. |
| A5 recorded replay | `REPLAY_VALIDATED` | Exact offline A5 replay with network/provider/model access disabled and zero calls. |
| Broker snapshot ingestion | `NOT_APPLICABLE` | No live ingestion adapter exists; snapshots are explicitly supplied trusted artifacts. |
| TradeMonitor integration | `NOT_APPLICABLE` | Advisory contract only; no transport or action-time integration. |
| Monitoring runtime | `NOT_APPLICABLE` | Immutable intent only; no scheduler/queue/daemon. |
| Multi-leg interpretation | `SYNTHETIC_ONLY` | Synthetic tests prove explicit `UNSUPPORTED_SHAPE`; no interpretation is implemented. |
| Forecasting | `NOT_APPLICABLE` | No A7 forecast generation or probability exists. |
| Profitability | `NOT_APPLICABLE` | A5 closure validates semantics and safety, not trading returns. |

No A5 path is described as live validated. Existing upstream provider studies do
not convert captured A5 acceptance into a live broker/TM claim.

## 13. Regression, residual risks, and freeze recommendation

The completed gate results are:

| Gate | Result |
| --- | --- |
| `pytest -q tests/unit/a5` | 52 passed |
| `pytest -q tests/unit/facade` | 57 passed |
| `pytest -q tests/unit/shell` | 88 passed |
| `pytest -q tests/unit/a4` | 37 passed |
| `pytest -q tests/unit/source_semantics` | 27 passed |
| `pytest -q tests/unit/opportunity_intelligence` | 65 passed |
| `pytest -q tests/unit/a3_hardening` | 61 passed |
| `pytest -q tests/unit/agents` | 270 passed |
| `pytest -q tests/unit/workflows` | 42 passed |
| A4.2 fixture regression after correction | 44 passed |
| A5 replay/facade/Shell boundary selection | 61 passed |
| `pytest -q` | 2,226 passed in 178.18 seconds |
| `python -m compileall src scripts` | passed |
| `ruff check src tests scripts` | passed |
| `mypy src tests` | passed across 529 source files |
| `python -m pip check` | no broken requirements; non-writable pip-cache warning only |
| Repository-relative Markdown links | 602 checked across 100 Markdown files; none missing |
| Secret-pattern review | zero matches in changed files; 12 repository identifier/validator candidates inspected, no credential value |
| A5/facade/Shell forbidden imports | zero provider/broker/model/A6/A7/remote dependency violations |
| Frozen/runtime diff check | no A2/A3/A4/A5/facade/Shell production file changed |
| Replay isolation | focused 61-case boundary selection and full suite passed with zero-call assertions |
| `git diff --check` | passed |

The repository virtual environment was not activated in the execution shell, so
the bare `pytest` executable was absent. The exact suites were run with the
equivalent repository-local `.venv/bin/pytest`; Python/Ruff/mypy commands used
the same environment.

The first full run exposed a hermeticity defect in an upstream A4.2 synthetic
fixture: its default deadline was fixed at 2026-09-12 12:00 Asia/Kolkata and had
therefore expired. The support fixture now defaults to no deadline, while tests
that exercise deadline behavior continue to supply one explicitly. This is a
test-only time-bomb correction; A4/A5 production behavior is unchanged.

Residual risks are explicit deferrals, not hidden acceptance claims:

- freshness is wall-clock rather than exchange-calendar aware;
- multi-leg combined-risk and hedge interpretation is unsupported;
- snapshots remain caller/TM-supplied rather than live-ingested;
- monitoring needs are not dispatched or made durable;
- local capture/facade/session ownership is not a remote multi-client service;
- A5 consumes normalized cited signals and does not independently recalculate
  upstream A2/A3/A4 evidence; and
- no empirical profitability or calibrated forecast claim is made.

None prevents freezing the bounded deterministic single-position baseline.
Recommendation: create `tiaf-a5-baseline` only in a separately authorized pass.

The roadmap has no smaller prerequisite that prevents A6 architecture. Multi-leg
position policy, monitoring runtime, Sector Rotation, and TM integration have
different owners and should not be pulled forward merely to expand A5.

Exact next Codex prompt title:

**`TIAF_A6 — OPTION EXPRESSION INTELLIGENCE ARCHITECTURE PASS`**
