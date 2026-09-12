# TI Monitoring Architecture

## 1. Authority, scope and current implementation

**Architecture promoted: 2026-09-12. Runtime not implemented.** This is the
authoritative future monitoring design following A5 and accepted pluggability
R1. It reconciles the two historical
[original](TBD_TI_MONITORING_ARCHITECTURE.md) and
[subscriber-driven v2](TBD_TI_MONITORING_ARCHITECTURE_V2.md) notes; their
disposition tables preserve both promoted principles and rejected suggestions.
Promotion is not runtime acceptance or permission to start implementation.

Monitoring Runtime is a governed recurring/event-driven consumer of TI
capabilities on behalf of authorized subscriber applications. It is not a
specialist, a second Planner, a watchlist product, or an execution authority.

The accepted [A5 baseline](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md)
constructs immutable `MonitoringNeed` and position-linked `WatchMandate` advice.
The [A5 facade](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md) publishes
`position.assess` over a captured complete request. Neither schedules work.
No scheduler, queue, persistence engine, API, lease engine, notification
transport, adaptive cadence, event bus, R2–R5 implementation, Sector Rotation,
Signal Qualification or A6 work is delivered here. Existing contracts, policies,
hashes and captured replay remain unchanged.

## 2. Ownership and watchlists

| Owner | Authority |
|---|---|
| Subscriber application | Business purpose, selected instruments, horizon intent, conceptual watchlists, requested profile, lifetime and cancellation intent. |
| TI | Admission and normalized mandates; scheduling/triggers, scoped dedupe, evidence/freshness, budget enforcement, capability invocation, audit/replay, result lineage and failure isolation. |
| TM | Operational position truth, action governance and execution. TI advice cannot close or modify a position. |

The thesis is coherent only with renewed admission at dispatch/access: neither a
subscriber label nor an old mandate grants authority, entitlements or live/model
permission. Apps express intent; TI may reject intent it cannot safely honor.

| Option | Consequences | Decision |
|---|---|---|
| A: TI owns watchlist CRUD | Duplicates TM/scanner/UI business state, adds synchronization and deletion semantics, couples a service API to intelligence. A list still cannot grant position authority. | REJECTED as the core monitoring model. |
| B: Subscriber-owned optional refs and admitted mandates | External/internal apps use the same contract; TM links positions, scanners link candidates, Shell/Web supply their own group refs. Replay needs admitted immutable context, not a live list lookup. Smallest authority surface. | SELECTED. |
| C: Hybrid ownership | A TI-hosted watchlist product could help a future UI but introduces two owners, reconciliation and CRUD persistence; useful only as a separately governed subscriber application. | Deferred application possibility, not a second core mandate model. |

Watchlist/group refs are optional, opaque and namespaced by subscriber. No
watchlist is required for one instrument or one position. Store the admitted
group/item revision or immutable membership context needed to explain a run.
Renaming, deleting or editing an external list does not rewrite old runs or
silently revoke mandates. A subscriber sends an authorized cancel/amend command;
an explicit previously admitted group-expiry rule may also end its mandates.
No implicit cascading CRUD is promised.

## 3. Fundamental object, identity and isolation

The fundamental future object is a **MonitoringMandate**, an immutable normalized
instruction revision for one principal instrument, purpose and horizon scope.
A request can mention benchmarks/peers without merging their independent
mandates. A WatchlistItem is only app membership; a scheduled invocation is one
execution; an A5 WatchMandate is source advice, not admission.

**No separate MonitoringSubscription contract in the first version.** Trusted
subscriber identity/configuration supplies grants, aggregate limits and approved
delivery references. There is no independently renewed subscription resource
whose lifecycle justifies another domain layer. Reconsider only if a concrete
shared contractual lifetime requires one; do not introduce a duplicate budget,
authority or lifecycle ledger.

Minimum logical identities are subscriber/caller authority binding, optional
subscriber group/item refs, mandate ID/revision/predecessor, instrument, purpose,
canonical horizon and label/profile provenance, logical run ID, attempt ID and
decision `as_of`. The same instrument may have different subscribers, objectives,
horizons, priorities, profiles and lifetimes simultaneously. Never dedupe away a
mandate merely because its symbol matches another.

Internal tools, TM, scanners, external apps and eventual Shell/Web commands use
the same conceptual admission/invocation contract. Internal callers do not get
privileged bypasses. Current Shell has no monitoring commands. This is logical
isolation in the local deployment model, not an implemented multi-tenant SaaS,
remote authentication system or shared-live-hosting claim. Recheck authority and
artifact/data rights before dispatch, lookup, result access and notification;
cross-subscriber enumeration and raw credentials/paths are not public metadata.

## 4. One-shot and time semantics

One-shot EvaluationRequest means the existing family of typed capability
requests, not a newly implemented generic request schema. It evaluates once and
ends. A recurring mandate authorizes multiple separately admitted runs within
bounds. `max_runs=1` can be explicitly requested, but is not a universal default
and does not turn every mandate into a one-shot request.

| Dimension | Subscriber intent / profile default | Normalized TI meaning / runtime responsibility |
|---|---|---|
| Analytical horizon | Duration/target interval plus optional app label such as DAY/POSITIONAL | Canonical duration or explicit target interval with unit/basis and mapping version; does not set polling frequency. |
| Evaluation cadence | Requested interval, bounded by versioned profile minimum/maximum | Accepted cadence and clock anchor; runtime owns due slots, not the immutable intent. |
| Evidence freshness | Family-specific acceptable age/profile | Independent max-age and availability policy for each family; freshness does not imply reanalysis on every fetch. |
| Lifetime | Requested start/end, purpose/cancel intent | Required finite `valid_from` inclusive and `valid_until` exclusive; runtime refuses new dispatch outside the interval. |
| Maximum evaluations | Optional positive `max_runs` | Logical evaluation-slot limit, not number of successful results; retries consume attempt budgets under the same run. |
| Event termination | Requested typed condition | Approved source/event semantics; cannot infer TM closure from TI recommendations. |
| Lease | Not part of first-version admission | Explicit expiry/cancel suffices; renewal is an admitted new revision. |

All timestamps reject naive datetimes, accept aware inputs from any zone and
normalize with `zoneinfo.ZoneInfo("Asia/Kolkata")`; JSON uses ISO-8601 `+05:30`.
No naive `datetime.now()` or manual offset arithmetic. Preserve original evidence
time/availability semantics alongside canonical timestamps.

Preserve app labels, but do not guess a universal DAY/POSITIONAL/SWING duration.
A versioned accepted mapping supplies an unambiguous duration (for example
elapsed seconds or calendar days) or explicit interval. Trading-session/day
durations require an approved calendar ID/version and session definition;
otherwise reject that unresolved scheduling intent. DEF-007 remains open. A
fixed wall-clock interval does not promise exchange sessions or holiday safety.
The existing A5 `Horizon` enum is not changed by this future normalization.

Each dispatch captures its own `as_of` and exact input refs; intent horizon,
evidence acquisition time and lifetime must not be substituted for that cutoff.
Limits end at the earliest applicable expiry, cancellation, run bound or admitted
termination event. An already admitted slot consumes its logical-run bound even
if blocked/failed; abandoned attempts cannot yield unbounded free retries.
Completion after expiry is recorded as such, not presented as another eligible
dispatch. Cancellation suppresses new work and requests bounded in-flight stop;
it cannot unsend an already issued read or erase its cost/audit record.

## 5. A5 and lifecycle reconciliation

Keep the implemented A5 `WatchMandate` name, schema `1.0`, hash and meaning.
Future admission **normalizes source advice into a distinct MonitoringMandate**,
retaining source capture/hash, mandate ID/revision/predecessor, needs, position,
authority, policy and budget refs. It is neither a schema alias nor a rename.
The caller supplies missing subscriber/lifetime/profile intent; TI explicitly
accepts or rejects it. A5 `cadence_hint_seconds`, `freshness_intent_seconds` and
need-level `next_due_at` remain hints, not jobs, guaranteed deadlines or grants.

An A5 assessment never auto-registers or auto-renews work. Later A5 advice is
recorded as output; changing normalized scope requires a new admitted revision,
not a self-expanding feedback loop. `ACTIVE_POSITION` requires appropriate
position truth/authority; `INACTIVE` cannot by itself be treated as active work.

| Separate dimension | Future meaning |
|---|---|
| Runtime mandate lifecycle | ADMITTED, PAUSED, ENDED; time eligibility/readiness are separate. Rejected admission is not an active mandate. End reason distinguishes expiry, cancellation, run limit, verified position closure and authority termination. |
| Purpose/linkage | Passive observation, candidate watch or position-linked purpose; the old PASSIVE/ACTIVE_WATCH/ACTIVE_POSITION ideas are not scheduler lifecycle states. |
| Accepted A5 lifecycle | ACTIVE_POSITION / INACTIVE stays advisory and unchanged; neither modifies operational position truth. |
| Run/health state | Due, running, blocked, partial, failed, outcome-unknown or completed belongs to execution records, not immutable mandate intent. |

External authoritative position closure may end a position-linked mandate under
an admitted rule. Stale/unknown position state is not closure: suspend unsafe
evaluation or return the capability's explicit missing/stale result. Inactivation
does not close a position; EXIT_RECOMMENDED is advice, not a close event. A
cancelled position mandate can coexist with a separate authorized candidate
mandate for the same instrument. UI colors are presentation only.

## 6. Capabilities, profiles and dependency ownership

Monitoring invokes governed capabilities, not specialist/provider internals.
`position.assess`, `opportunity.assemble` and `a4.evaluate` are existing
capabilities. Their current public paths are **CAPTURED_READ**, not live refresh.
Repeating them on the same artifact does not acquire a new snapshot or advance
its `as_of`. A useful future live monitor needs separately accepted input
acquisition/admission and an authorized versioned input-binding path; it cannot
mislabel the existing facade or privately invoke the Planner as a workaround.
Future `sector.rotation` and `signal.qualify` are not registered implementations.

A future monitor-compatible declaration must identify capability/schema/version,
effect, supported scopes, typed input binding and freshness requirements, replay
support, authority, budget/cost knowledge, retry safety and runtime compatibility.
An installed capability is not automatically schedulable. R2 is the natural
metadata home; no new flag or registry is implemented here.

An intelligence profile chooses required and optional capabilities/evidence,
permitted depth and compatible versions. It uses the **same pluggability
dependency model and Planner**, not a monitoring-specific dependency graph.
Declared required scope is stable; availability is an observation. In particular
`requested ∩ available` must never silently erase required obligations. Preserve
R1 required/optional absence, dependency failures and completeness limitations.
Optional absence can degrade output; required absence prevents complete status.

Profiles are versioned, trusted **COLD configuration**: cadence/freshness bounds,
depth, triggers, lifetime/run ceilings, priorities, provider/model/attempt/time
budgets and missed-run policy. Subscriber preferences are intersected with grants
and ceilings, not treated as policy overrides. Profiles confer no authority.
Changing defaults does not mutate admitted revisions or their historical replay.

## 7. Admission, updates and liveness

Admission verifies caller/subscriber authority, instrument universe, purpose and
position scope, canonical horizon, lifetime/run bounds, active-mandate limits,
cadence floor, scheduler capacity, profile/compatibility, required capability
availability, data rights and budget ceilings. Safe rejection reasons do not
disclose another caller's artifacts or hidden catalog entries.

**First version: atomic admission per mandate, no batch partial-acceptance
protocol.** An optional gap is disclosed on an accepted scope; an unavailable
required capability rejects admission without shrinking the profile. Later
required loss records blocked/degraded obligations and bounded recovery, never
complete-by-omission. Transient provider failure does not invalidate otherwise
valid intent. Revocation, integrity failure, expiry and termination are different
conditions: deny execution/access, pause/quarantine or end with explicit reason.

Request idempotency is scoped by subscriber, operation and client key with a
canonical request digest. Same key/same intent returns the same admitted record;
same key/different intent conflicts. Admission persistence must precede success.
Amendment requires the expected predecessor and creates a new immutable revision;
cancel is idempotent with a retained terminal record. Unknown admission response
is retried with the same key, not a new mandate. No silent reactivation by retries.

**No mandatory lease/heartbeat in the first version.** Finite validity and explicit
cancel bound orphaned work. Extend lifetime through authorized revision/renewal
before expiry or a new admission after termination. Eventual remote disconnected
subscriber liveness may justify a separately versioned lease protocol; never
equate absence of heartbeat with operational position closure.

## 8. Scheduling and execution guarantees

Minimum first runtime slice: fixed periodic scheduling with bounded due scans,
concurrency, attempts and backoff. Default missed-run policy is
**COALESCE_TO_LATEST**, evaluating current eligible evidence once and recording
missed slots; explicit **SKIP_MISSED** is also supported by policy. Neither
backdates newly acquired evidence. **REPLAY_MISSED** remains deferred pending
historical inputs, PIT rights, explicit budget and evaluation semantics.

The architecture permits event/hybrid execution, but it is not a requirement for
the minimum periodic slice. An event-enabled slice must approve a bounded typed
ingress, authenticated source, stable event ID/time, scope matching, debounce and
coalescing rules. No arbitrary trigger expressions, event bus or live polling
inside specialists. A5 trigger hints are not implemented event detectors.

Guarantee **at-least-once due delivery with idempotent logical run identity**,
not exactly-once execution. Run keys bind mandate revision plus scheduled slot
or admitted event/coalescing identity; attempts have separate IDs. Persist slot
reservation before dispatch; retries reuse the logical run, retaining attempt
outcomes and cost. Bound overlap and successor execution per mandate; no retry
storm after restart. Revalidate current authority at each attempt.

After an ambiguous timeout/crash, do not assume a provider/model call failed or
cost zero. Record outcome-unknown and reconcile the reservation before any
authorized retry. No exactly-once external read/billing claim is possible merely
because local result publication is idempotent. Cancellation of one consumer
must not cancel shared work still required by another authorized consumer.

## 9. Evidence sharing and scoped interpretation

Share compatible acquisition/cache work, not mandate identity or analytical
meaning. A dedupe decision must cover provider/account/data entitlements,
authorization, instrument/venue, requested fields and semantic basis, input and
adapter/schema/policy versions, effective/PIT cutoff, actual availability and
each consumer's freshness need. Unknown dimensions are not matching wildcards.
The strictest compatible freshness may justify one acquisition; incompatible
scope/rights requires separate work or rejection. Recheck rights on cache return.

Different horizons/purposes may produce opposite assessments without factual
contradiction. Apply [source comparability](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md):
match proposition, effective interval, horizon, basis and admitted availability
before labeling conflict. Different acquisition times alone do not hide a real
same-proposition conflict. Preserve disagreement and NO_TRADE; do not vote across
unlike questions. Evidence refresh, analytical evaluation and notifications are
separate activities. Full incremental invalidation/recalculation is deferred;
do not build a second dependency engine in the scheduler.

## 10. Persistence, restart and lineage

Follow the [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md): start
local/single-writer, not a queue cluster or mandatory DB. Before claiming durable
monitoring, persist admitted revisions/idempotency results, lifecycle changes,
due-slot reservations, attempts/unknown outcomes, budget references and published
run/result references. Use atomic publication and a recoverable journal/state
protocol with tested ordering, collision handling, interrupted writes and backup/
restore. Filesystem-first is acceptable **only when these guarantees are proven**;
today's JSON artifacts are not a transactional scheduler store. Select SQLite
only if demonstrated transactional requirements warrant it, not by default.

Restart reconstructs bounds/lifecycle and outstanding work, validates pinned
bindings and authority, quarantines corrupt/incomplete records, reconciles unknown
attempts and applies the recorded missed-run policy. Fail closed rather than
silently substitute latest config, resubmit ambiguous live work or lose active
mandate limits. Multi-process writers, distributed leases and DB migration remain
later operational gates. Retention cannot silently delete records still needed
for active idempotency, unknown costs or auditable replay.

Each monitoring capture links subscriber/optional group, mandate revision and
source intent, logical run/attempt/trigger, instrument/purpose/horizon/`as_of`,
capability request and result, evidence refs, completeness/absence, policy/profile/
schema versions, pinned composition, authority-decision refs and usage/reservation
lineage. Never serialize credentials. R3 supplies the additive composition
envelope/pinned verifier design: **existing child hashes remain unchanged**.

Recorded replay returns the captured result without live calls. Verification
uses captured inputs and exact compatible bindings; unavailable historical code
is explicitly unverifiable, never repaired by live acquisition or a latest-policy
substitution. Policy/composition comparisons create separate runs. A parent
monitoring capture is not a rewrite of accepted A2/A3/A4/A5 captures.

## 11. Cost, priority and failure isolation

Reuse existing run, attempt, reservation and leaf-usage ledgers. Enforce operator,
subscriber, mandate and run ceilings for calls, tokens, time and known money;
unknown cost remains unknown and reservations remain conservative pending
reconciliation. One shared provider attempt has one actual usage identity, with
explicit versioned allocation/beneficiary refs; never double-count physical cost
or treat shared work as free to all subscribers. Admission reserves conservatively
until a safe allocation is established. Subscriber limits must not exhaust other
subscribers' reserved capacity.

Priority is bounded policy-controlled scheduling preference, not authority,
guaranteed deadline, bypass of required scope, unlimited budget or silent
cross-subscriber preemption. Positions may receive an approved priority, not an
unconditional global rule that starves candidates. Backpressure, per-mandate
failure isolation and explicit blocked/partial/unknown outcomes are mandatory.
Notification delivery failure is not analytical failure; future transports need
their own authorized idempotent delivery attempts without re-evaluating a run.

## 12. Pluggability and dependency gates

Follow [HOT ⇒ COLD ⇒ STRUCTURAL](TIAF_PLUGGABILITY_ARCHITECTURE.md). Requirement
scope and replaceability are independent; required does not mean hard-wired.

| Component | Requirement | Replacement boundary |
|---|---|---|
| Mandate/run/lineage contracts | Required | STRUCTURAL versioned semantics; incompatible replacement requires migration/compatibility, not a runtime toggle. |
| Scheduler and persistence adapters | Required for runtime/durability claims | COLD replaceable behind typed interfaces and equivalent replay/restart guarantees. |
| Profiles and scheduling policy | Required | COLD versioned selection under trusted startup composition. |
| Event ingress and notification transport | Optional to periodic/pull-result slice | COLD replaceable, bounded and authorized; absence explicit for profiles that require them. |
| Adaptive cadence policy | Optional, deferred | Future COLD policy with captured decisions; not hidden mutable learning. |
| Operational telemetry backend | Optional replacement/export | COLD backend; minimum audit/cost/failure records remain required even without an exporter. |

No HOT capability is required or implemented. No universal plugin registry is
introduced. Concrete future implementation gates, not new A5 freeze blockers:

| Work | Monitoring dependency assessment |
|---|---|
| R1 required scope | Already accepted; preserve it in admission, every run and replay. |
| R2 descriptors/dependencies | Minimal explicit versioned monitor-compatibility and dependency metadata is prerequisite to generic admission. A bounded static allowlist may supply that minimum; completing every discovery feature is useful, not a dependency of all periodic scheduling. Reuse the same model. |
| R3 composition/replay | Captured pins and exact resolution-or-explicit-unverifiable are prerequisite to truthful restart/replay. The additive parent design is the route; a full historical resolver catalog is not required to display a recorded result. Never imply existing captures already contain a new manifest. |
| R4 optional import isolation | Useful; prerequisite only when the runtime promises to operate with uninstalled optional SDKs. It does not establish scheduling or admission semantics. |
| R5 COLD composition freeze | Immutable trusted startup bindings are prerequisite to reproducible runtime. Reuse the existing local owner where sufficient; broader registry remediation is not required just to review monitoring architecture. |
| R7 sharing/hosting | Scoped entitlement, reservation and lifecycle governance must be accepted before cross-subscriber shared live evidence. Existing per-run reuse is not proof of this runtime. |

R2–R5 remain separately bounded SHOULD_FIX_BEFORE_A6 work, **not A5 freeze
requirements**. None is implemented by this review. DEF-007 is prerequisite to
calendar-sensitive promises, not fixed wall-clock intervals; DEF-009/010/011/050
retain the relevant sharing/health/durable/distributed operational work. Remote
delivery is separately DEF-003; TM integration is DEF-004.

## 13. Roadmap, disposition and next action

| Milestone | Monitoring responsibility |
|---|---|
| A5 accepted | Advisory need/WatchMandate values, on-demand captured assessment and replay only. |
| A8 | TM subscriber integration, authoritative position lifecycle and admitted intent; no transfer of execution authority. |
| A9 | Scanner/candidate intake as another subscriber, optional external group refs, no TI-owned watchlist CRUD requirement. |
| A10 | Durable recurring runtime, operational scheduling/recovery, calendar/telemetry/load gates and delivery where approved. |

If A8/A9 acceptance demonstrably needs recurring execution earlier, approve a
separate bounded local periodic slice with the above minimum admission, pinning,
durability, budget and failure gates. This is not automatic acceleration of A10
or permission from this architecture. Historical/outcome replay remains separately
A7/DEF-049/051; live backfill cannot substitute for PIT evaluation.

Both TBD notes now have complete section dispositions. Their original bodies
remain historical, non-authoritative source material. Promoted means future
architecture unless explicitly identified as already implemented A5 behavior.
Adaptive policies, exchange calendars, distributed runtime, optional subscription/
lease semantics, notification transports and sector/signal capabilities remain
separately gated; no deferral is marked implemented here.

**Subsequent status:** the [post-R1 documentation consolidation](TIAF_POST_R1_DOCUMENTATION_CONSOLIDATION_AND_SYNCHRONIZATION.md)
has now synchronized accepted A4/A5 and top-level documentation. Its next prompt
is `TIAF_A5 — FINAL FREEZE / TAG READINESS CHECK`. This supersedes the monitoring
review's then-next consolidation prompt, not its architecture decisions. No A6,
monitoring runtime, R2–R5 implementation, commit, tag or push is performed here.
