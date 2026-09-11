# TI Deployment Architecture

## Status, authority and scope

**Approved deployment design, 2026-09-11 (Asia/Kolkata). Not a deployed service.**
The [deployment review](TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md) records
repository evidence, alternatives, TBD dispositions and delivery gates.
This document governs hosting beneath the authoritative
[system boundary](TIAF_SYSTEM_ARCHITECTURE.md),
[source semantics](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md)
and [A4 design](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md).
Those documents own intelligence meaning; deployment cannot override them.
Frozen A1/A2/A3 behavior, schemas and fingerprints remain unchanged.

The local target and promotion gates are approved architecture. Level 2/3
components are conditional options, not approved procurement, infrastructure or
implementation. No facade, Shell, Web, pre-A4 foundation or A4 runtime is added.

## 1. Deployment thesis and near-term target

**One trusted Python application runtime, direct typed capabilities, isolated
invocations and filesystem replay. Split processes only for demonstrated needs.**
One logical box is not one process. Moving Python calls to IPC or a remote
transport must preserve admitted inputs, source/authority meaning, A2 baseline,
A3 opinions, A4 dissent/dispositions, budgets, provenance and replay identity.
Operational latency and availability may differ; explicit failures/partial
results must report that difference instead of silently changing intelligence.

```text
Now: trusted scripts / direct package calls + local replay files (Level 0)
  -> separately authorized local composition + small Python facade (Level 1)
       Shell, trusted Python consumers -> governed admission -> TI_CORE
       request-local Planner/specialists; later foundation and A4 in-process
       controlled provider/model/storage adapters; single owner of corpus writes
  -> local service only for an actual isolation/multi-app requirement (Level 2)
       independent Shell / Web backend / TM / scanners -> same capabilities
  -> production service, workers and durable coordination only as justified (Level 3)
```

"One runtime" does not mean exactly one OS process: current Yahoo/Tapetide MCP
connectors already launch stdio subprocesses. Preserve those adapter-local
lifecycles; they are not TI microservices or security sandboxes. No new Core,
specialist, Planner or Arbitrator process is needed. Initial A4 deterministic
runtime should be in-process after its semantic foundation is accepted.

Immediate useful infrastructure abstraction: a small trusted **composition and
invocation-lifecycle owner** behind the curated Python facade. It resolves
configuration/grants, constructs existing registries/gateways, creates isolated
request state, owns shutdown and controlled storage access. This is planned work,
not a new container/DI framework, universal dispatcher or `ti_core` package.
`tiaf.app.create_app_context()` remains bootstrap metadata, not that owner.

## 2. Stages, prerequisites and exit criteria

| Level / verdict | Supported meaning / prerequisites | Trigger and exit gate to next stage |
|---|---|---|
| 0 current development — VALID with limitations | Trusted local repository callers, bounded scripts, captured offline replay. No public service or restart guarantee. Existing adapter subprocesses allowed. | A real reusable consumer needs stable admission/composition. Before Level 1 consumer use: reviewed narrow capability catalog, typed facade, entitlement/effect checks, lifecycle and isolated-request tests. |
| 1 local engineering — REVISE / recommended target | Same-process Core and facade, later Shell as mediator; one admitted top-level live analysis at a time initially, existing bounded inner concurrency; one writer per corpus. Foundation can start internally without waiting for Shell/facade. | Independently operated consumers, trust separation or overlapping load cannot be safely supported by this ownership model. Level 2 requires transport/security/compatibility, quota ownership and multi-client isolation tests. Multiple consumers alone do not force a service. |
| 2 multi-app local/service — REVISE / conditional | Trusted Python clients may still link directly. A local TI host is preferred for an operational TM or independent/non-Python clients needing failure/credential isolation. No arbitrary internal RPC. | Measured remote/multi-user demand, recovery requirements or resource bottlenecks. Level 3 requires threat model, retention, concurrency/transaction design, admission/load limits and restore/operational acceptance. |
| 3 production — KEEP conditional, distribution optional | A single well-operated service may suffice. Add only necessary workers, durable job records, shared stores and scheduling under an approved operating model. | No mandatory next level. Scale or split only against measured SLO/resource/failure evidence; preserve offline export and rollback. HA, service discovery, queues and distributed caches are not an automatic bundle. |

No deployment profile selects a different score policy or relaxes `NO_LLM`.
Capability availability, semantic intelligence profile and deployment profile are
separate. Any deliberate policy change is versioned and captured, not implicit
in a host name or transport.

## 3. Consumer placement and process criteria

**TI_SHELL:** initially in the same trusted application process as facade/Core,
when separately implemented. Session context is application-owned memory:
current symbol, last-result reference, preferences and interaction history.
Each invocation materializes a fresh typed subject/objective/horizon/as-of and
rechecks grants. Session defaults and an Interaction Agent cannot self-grant
live/model/admin access. User/developer modes are presentation, not authorization.
Engineering trace/replay is an explicitly admitted subset. Optional persisted
preferences must not restore expired grants or promote an old result to fresh
evidence. Shell crash may lose the session/in-flight request; completed captures
survive if successfully stored. A later remote Shell keeps the same semantics.

**TradeMonitor:** trusted offline prototypes may use the Python facade, accepting
shared crash/GIL/dependency lifetime. For an operational TM process, prefer a
separate local TI host when integration is authorized: provider/parser stalls
must not block its lifecycle/execution loop and broker secrets should stay in
TM's process. Remote service is justified only by separate hosts/operators or
security/availability needs. Local IPC vs HTTP is not chosen now. TM sends a
versioned position snapshot/reference with observation time and freshness basis,
not broker handles. TI returns advice; TM owns freshness checks, risk policy,
position lifecycle, restart reconciliation and whether advice can be used.
Broker remains execution truth. TI/TM outage never creates an order, inferred
position or "last known is current" state. A service is not a pre-A4 prerequisite.

**Web/scanners/external apps:** trusted local Python consumers use the same facade
factory, not independent reconstruction of `ControlledServices`/registries.
A Python Web backend may host it when one trust/lifecycle boundary is acceptable;
browser code uses an authenticated backend and never gets provider credentials.
Use a local TI service for independent releases/lifecycles, non-Python clients or
centralized quotas; remote service for authorized cross-host access. Web never
calls Shell, Shell never calls Web. Scanners remain candidate discovery/sensors;
A9 integrates their inputs, not a parallel intelligence engine. External untrusted
Agents/plugins cannot be loaded into a privileged in-process runtime.

Process split requires a documented reason and an acceptance test: credentials
or untrusted-code isolation; independent failure/restart domain; measured CPU/GPU
or memory pressure; incompatible dependency/release lifetime; multi-user access;
long-running work beyond caller lifetime; or measured scaling needs. Record
which risk a process actually mitigates. A same-user subprocess with inherited
environment/filesystem access is not a secret boundary. Separate roles, nine
specialists or an architecture diagram are not sufficient reasons to split.

## 4. State ownership and durability

| State | Owner and lifetime | Durability / sharing rule |
|---|---|---|
| Objective, horizon, as-of, subject, position snapshot, policy/profile, authority reference | Invocation | Record admitted values with run; no mutable global current analysis. Credentials excluded. |
| Plan, budgets/reservations, attempts, active/superseded opinions, later A4 theses/challenges | Request coordinator | In-memory working state; accepted audit captured. Current reservations do not survive restart. Never reuse as another request's mutable state. |
| Shell symbol, last-result reference, preferences, interaction context; Web session | Consumer session | Memory initially; optional separate preferences store later. Not canonical evidence or durable authority. |
| Eligible evidence/content and immutable graph snapshots | Controlled runtime/store | Reusable only under §6. Captured versions retained for replay; cache entries disposable. Graph object does not imply graph DB. |
| Single-flight futures, provider cooldown/health signals, bounded caches | Runtime owner / credential scope | Process-local and reconstructible now. No cross-process coordination guarantee. Mutable registry composition is startup-only by policy. |
| Captures, hashes, original source/provenance lineage, policies and semantic usage/audit | Canonical artifact store | Persist now for accepted captures/replay; one writer per root, verified reads/backups. No promise that ordinary writes survive every crash. |
| Future monitoring mandates, durable job attempts, forecast/outcome records | Separately authorized monitoring/evaluation/job owners | Durable once those workflows require survival/recovery. Not Shell state; not implemented by A3 or this design. |
| Broker positions/orders/fills | Broker and TM reconciliation boundary | Never TI storage truth. Captured context is historical input only. |

Arbitrary legacy metadata remains shallow-mutable despite frozen models. Copy
and validate canonical serialization at admission/publication before hashing;
never share a caller's mutable dict or composition object across requests.

## 5. Persistence, consistency and recovery

Keep A2 snapshot/JSONL and A3.10 content-addressed package stores now. They are
distinct existing layouts, not one new database schema. Portable packages are
the offline transfer seam. A3.10 stores `blobs/sha256/<digest>.json`, package
manifests, `corpus_records.jsonl`, `evaluation_records.jsonl` and
`closure_records.jsonl`. Do not replace originals with cache refreshes.

Current check-then-write and check-then-append operations are not atomic
transactions across threads/processes; no multi-writer, fsync, crash-recovery or
exactly-once claim is justified. Initial operation must serialize writers per
root (or use separate roots), avoid readers consuming incomplete publications,
verify integrity after restart and preserve/quarantine damaged artifacts rather
than silently repair them with new live evidence. A failed write cannot be
reported as a durably captured result. Tests establish integrity semantics, not
a production durability SLO.

Before service-side publication or stronger durability promises, implement and
test atomic publication/completion boundaries, collision/uniqueness behavior,
interrupted-write detection, safe identifiers/root containment, recovery and
backup/restore. A content hash does not confer path safety or authorization.
These are bounded operational gates, not changes to canonical record meaning.

An embedded relational store (SQLite-like) becomes justified by transactional
local job/index updates or concurrent query/write needs that exceed serialized
files. A shared relational store (Postgres-like) is conditional on multiple
writers/hosts and recovery/availability requirements. Shared cache is optional
acceleration; distributed stores need measured volume/replication requirements.
No vendor or infrastructure dependency is selected.

Transactional candidates: job claim/attempt transitions, idempotency uniqueness,
reservation settlement, manifest publication/index updates and mandate version
changes. Semantic history remains append-only: corrections, supersession,
comparison, audit and outcomes create linked records rather than overwritten
decisions. Mutable indexes/current pointers are rebuildable projections.
Retention/deletion rights and license constraints require an explicit policy;
if an artifact expires or must be removed, record unavailability and do not
promise exact replay. Do not retain source content beyond permitted rights.

## 6. Evidence/cache reuse across consumers

**Shared Evidence != Shared Analysis State.** Resolve permission before lookup
and again before return/export. Partition private data by entitlement/security
scope; possession of a digest or cache hit is not permission. A later revoked
grant is not restored by an old capture's authority reference.

Reuse needs canonical subject/venue/instrument identity, evidence family,
timeframe/window, adjustment/period/consolidation/currency/expiry/basis where
applicable, source document/version/revision and adapter/normalizer identity,
availability/PIT cutoff, freshness policy and compatible entitlement. Unknown
dimensions are not wildcards. Never use a symbol-only cache. Preserve provider
neutrality, provider-defined ambiguity, source-scoped authority, dependence and
contradictions; transport proximity or shared storage grants no source authority.
Later acquisitions/revisions cannot enter an earlier as-of run. Refresh creates
a successor capture with honest acquisition time.

Current cache hashes and `ControlledServices` single-flight are not a complete
multi-tenant security key or a universally bounded cache. Initially scope mutable
services to the invocation and trusted configuration. Wider shared acquisition
requires explicit admission/expiry/size policy and ownership tests. Coalesce
only compatible, authorized requests; record the acquisition once and link
reuse for each consumer. Consumers retain their own deadlines/budgets and do
not inherit the owner's grants or mutable result. One consumer cancelling must
not cancel work still authorized for another. Cached reads record reuse, not
another live provider charge. Do not double-debit shared calls or reset budgets.

Separate processes do not share Python locks/futures. Initially use separate
caches or a single acquisition owner; do not introduce distributed locks to
pretend an in-memory single-flight table coordinates them. Any future shared
acquisition/accounting scheme needs explicit credential-quota ownership and
durable attempt identity before claiming cross-process deduplication.

## 7. Credentials and security by exposure

Market-data, MI and future model credentials belong to trusted infrastructure
configuration at the adapter host. Do not send them through Shell commands,
canonical inputs/evidence, model prompts, replay, URLs, logs or exported traces.
Operator-managed local configuration may supply them now; separate secret stores
and rotation procedures become necessary with service operation. Avoid unnecessary
environment inheritance into connector processes. Future hard isolation requires
OS identity/access controls and explicit secret/egress scope, not just `fork`.

Broker credentials stay with TM. TI must not receive them absent separately
approved read-only state integration; that exception would still confer no
execution authority. Model adapters receive only entitled, minimized evidence,
never secret-bearing runtime objects. Model output is untrusted input, not a
capability grant or authoritative fact.

| Exposure | Required boundary (not a claim it exists now) |
|---|---|
| Trusted local process | Trusted code/user, restrictive local files/config, bounded effects, explicit admission. Python imports provide no sandbox. |
| Trusted local multi-process | Explicit IPC peer/OS identity, filesystem/socket permissions, separate secret scopes and lifetime ownership; shared user identity is not isolation. |
| Localhost service | Authenticate clients, authorize each capability/artifact, request/body/rate limits and safe binding; loopback is not inherently trusted. Browser-facing endpoints need origin/CSRF controls appropriate to their authentication, not CORS as authorization. |
| LAN/private network | Authenticated protected transport, service identity, least-privilege firewall/egress, rotation, request limits, audit and replay access controls. Private network does not imply trust. |
| Remote/multi-user service | Threat model, tenant/data-entitlement isolation, secure transport, object-level authorization, quotas, redaction, retention/privacy and abuse/incident/restore procedures before exposure. |

Authentication establishes caller identity; authorization permits an operation;
data entitlement permits source use/redistribution. All intersect with operator
policy and request scope at admission. Source authority is epistemic and separate
from all three. Recheck on artifact reads, job polling and exports; engineering
endpoints are separately restricted, not a developer query flag.

## 8. Concurrency, budgets and lifecycle

Initially one top-level live invocation per runtime, serial orchestration by
default; retain accepted bounded specialist waves where explicitly selected.
This is a recommended host policy, not a new lock or reduction of existing
`run_langgraph` behavior. Multiple concurrent analyses need separate coordinators,
ledgers, inventories and mutable service instances. Startup registers adapters
and snapshots configuration; do not mutate registries during admitted work.
Audit actual thread safety before sharing SDK clients or unsynchronized caches.
Async IO is an execution choice, not permission to multiply quotas or spawn
unbounded tasks. One writer per corpus applies even to otherwise independent runs.

Use existing reservation/gateway machinery for per-invocation limits, with an
explicit outer ownership plan for shared provider-account quotas before enabling
concurrent hosts. A mutex or per-request budget alone cannot enforce an account's
global limit. Keep actual call/attempt IDs, unknown/held usage, nested consumption
and reuse distinct. Opaque provider callbacks may make several HTTP calls
(DEF-015); no host may claim a strict wire-call cap until leaf accounting proves
it. A3.10 monetary UNKNOWN/UNPRICED is not zero or configured cost-unit currency.

Deadlines bound admission/waiting, not guaranteed termination of synchronous
threads or remote work. Stop further dispatch, reject late admission, retain
unsettled reservations; do not free quota merely because a client disconnected.
Shutdown stops admissions, bounds drain and records incomplete work where
possible. Current process death can lose in-memory state; after restart do not
claim recovered attempts/cost or automatically resubmit uncertain live work.
Recoverable spending across restarts requires future durable attempt/reservation
records and provider reconciliation. No second conflicting budget ledger.

## 9. Long-running jobs and failure isolation

Current bounded research/model timeouts are not a durable queue. Workers/job
records become necessary when work must outlive a caller, resume after restart,
support independent cancellation, backpressure, scheduled due times or repeated
monitoring/outcome acquisition. A bounded local worker may precede any remote
queue if sufficient. Durable admission needs job/attempt IDs, pinned request and
policy, idempotency scope, quota reservations, deadline, cancellation state and
authorized result references. Define at-least-once attempts with deduplicated
effects; do not promise exactly-once external calls.

Checkpoint only validated semantic boundaries with captured evidence/cutoff.
Resume must recheck current authority and account for uncertain prior attempts;
new live evidence after cutoff needs a successor run. Progress is operational,
not a partial intelligence conclusion. Monitoring mandates, schedules and
forecast outcomes remain future owners (DEF-010/051), outside specialists and
Shell sessions. Monitoring/forecast TBD algorithms are not promoted here.

| Failure | Local response / boundary | Later isolation trigger |
|---|---|---|
| Provider unavailable/rate-limited | Existing typed failures and permitted fallback; preserve missing/partial/stale facts and attempt usage. No fabricated observation. | Shared quota/health policy and demonstrated failure impact (DEF-011). |
| Model crash/hang | Default no-LLM; authorized future stage follows A4 failure policy, held uncertain usage, no invented reply. | Resource-heavy runtime, unstable SDK, privacy or hard termination requirement justifies separate worker. |
| Parser failure | Adapter validation/quarantine, safe failure detail; not specialist guessing. | Untrusted/large content or memory/crash risk needs constrained parser worker. |
| Core exception | Fail the invocation safely; do not turn it into NO_TRADE or a valid A4 result. Preserve available audit. | Cross-request crash blast radius justifies host/worker separation. |
| Shell/Web crash | Lose session; do not claim in-flight cancellation or completion. Resolve only successfully persisted results. | Caller-independent work needs durable jobs, not inference from a dropped connection. |
| TM unavailable | Intelligence remains intelligence; no execution or automatic position reconciliation inside TI. | Integration delivery/retry policy belongs to A8/TM. |
| Corrupt/missing storage | Integrity error/quarantine, bounded restore of verified artifacts; no live refill masquerading as replay. | Durable publication, tested backup/restore and storage isolation before stronger availability promises. |

## 10. Observability and service wrapping

Semantic audit retains admitted evidence/lineage, source disputes, policy/version,
plans, model records/validation, dispositions, reservations and replay identity.
Operational telemetry measures latency/error rate/provider health, request rate,
resource pressure, queue depth when present and cost knowledge. Link with opaque
run/correlation/attempt IDs; do not turn log text into market evidence or copy
raw payloads/secrets into metrics. Model/reasoning records mean supported
structured outputs and validation, not hidden reasoning traces.

Level 0: existing captures/CLI summaries and test evidence. Level 1 host gate:
safe invocation/attempt timing, completion/failure/capture status, budget/held
usage and lifecycle diagnostics. Level 2: add client/authorization audit,
admission pressure, quota ownership and health/readiness distinct from semantic
capability availability. Level 3: measured SLOs, alerts, retention, recovery drills,
resource/queue dashboards and pricing attribution when supported (DEF-055).
No telemetry backend is selected; current `tiaf.app` metadata is not readiness.

Future network service wraps only the curated facade. HTTP is suitable for
broad application interoperability; gRPC may suit typed internal integrations.
Neither is selected now. Define operation-specific versioned schemas, supported
modes/effects, limits, deadline/correlation propagation and safe error mapping.
No arbitrary module/function/path RPC, pickle, caller router objects or ad-hoc
Shell subprocess protocol. Preserve domain non-action/partial/conflict states
inside successful transport responses; transport failure is not a market opinion.

Bounded synchronous calls initially; async handles only when job semantics are
implemented. Progress streaming carries sequenced operational events, not a
mutable canonical result. Lost reply is outcome-unknown: query by authorized run
identity before retry. Idempotency must bind caller/security scope, capability
version and canonical request digest; key reuse with a changed request is rejected.
Replay/refresh/recompute are distinct operations. Retry of live acquisition may
consume quota despite read-only data semantics; admission alone is not durable
exactly-once execution. Artifact/job identifiers require object-level checks.

## 11. Models, containers and cloud

Optional model API clients may stay in-process behind the reasoning gateway.
Local GPU/resource-heavy inference, crash-prone runtimes, dependency conflicts or
privacy/credential requirements can justify isolated workers/remote inference.
Location must not change Agent roles, evidence validation, tier limits, token
reservations or no-LLM policy. Existing A3.8 remains no-LLM; A4's optional gateway
bridge and DEF-052 production model prerequisites remain unimplemented.

Docker is not needed now; consider packaging reproducibility after an actual
host/worker contract and operating target exist. Containerization alone is not
a complete security boundary. Cloud requires justified remote demand, data/model
egress and license/privacy decisions, access controls, retention, cost and restore
tests. Kubernetes is premature without a demonstrated multi-workload operations
need and ability to operate it. No images, manifests, cloud resources, event bus,
service mesh or distributed locks are introduced by this review.

## 12. Replay and versioned upgrades

Local replay remains the baseline: portable manifest/content-addressed artifacts,
validated hashes and pinned schema/policy/component identities. Recorded replay
must work with provider/model credentials absent and outbound access disabled.
Deterministic verification needs compatible pinned code; recorded reconstruction
does not claim recomputation of an unavailable model. Model outputs are recorded
inputs to replay, not instructions to call a model. Missing/unsupported/corrupt
artifacts produce explicit failure/limited verification, never live replacement.

Service-hosted replay rechecks current access and resolves authorized immutable
artifacts. An authorized self-contained export can replay offline after the
service is down, subject to retained rights/artifacts; service availability is
not a semantic replay dependency. Distributed replay later uses isolated jobs
and immutable bundles, separate execution usage, bounded retries and independent
results. A3.10 exact-byte checksums and semantic fingerprints remain distinct;
new pass-2/A4 parent records cannot rewrite frozen children. Policy/model changes
create comparisons or successor runs, not retroactive exact-match claims.

Package release `0.1.0`, A0 schema `1.0`, child schemas, capability version,
policy/normalizer version, transport protocol and Shell grammar remain separate.
Negotiate/reject client-server mismatches before effects. Optional fields/enum
extensions are not automatically compatible with strict readers. Retain old
readers or explicit versioned conversion with original bytes/lineage preserved;
never in-place migrate historical evidence to make current code accept it.
Local upgrades can stop admission, drain known work and replace a pinned runtime.
Later rolling upgrade needs per-run version pinning, mixed-version read/write
compatibility, worker routing and rollback acceptance; it is not required now.

## 13. Foundation, delivery and acceptance gates

`POST_A3_PRE_A4_FOUNDATION` is deployment-neutral Core work implemented internally
in-process: source identity/scope, comparability/disputes/independence, confirmation
and A4 projection, capture/replay tests. It need not expose every helper publicly
or wait for a service. The separately accepted
[local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) now exposes a small approved
projection/replay subset without a second foundation implementation. It uses
trusted same-process configuration, frozen startup composition, request-local
state, logical artifact refs and an enforced single-writer marker. It has no
live capability or transport. DEF-003's remote delivery track remains separate.

The completed [consolidation](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md)
selects separately authorized bounded foundation -> narrow local facade/lifecycle
-> deterministic A4, then later consumers. This is a delivery choice, not a
technical dependency of internal projection work on a facade. Shell
is neither required to implement A4 nor permission to implement it now. A8 owns
TM integration and service transport when justified; A9 owns scanner integration;
A10 owns production recovery, health/SLOs and durable infrastructure. Minimal
admission/lifecycle/security/storage slices must accompany any earlier exposed
consumer, but do not move all A8/A10 infrastructure before A4.

No new DEF IDs/status changes are warranted. DEF-003/004 retain integration;
009/010/011/050/051 retain operational delivery; 049 still covers arbitrary PIT
reconstruction, not solved by backup; 052/055 remain model/pricing prerequisites.

Future implementation acceptance must prove: two incompatible requests cannot
share mutable analysis/grants; revoked entitlement blocks cached/artifact reads;
future-as-of data cannot leak backwards; duplicate/lost requests have honest
attempt/usage accounting; timeout does not release unknown work; corrupted or
missing artifacts fail offline; compatible direct/transport invocations preserve
semantic output; and no broker/model/live access occurs in recorded replay.
Multi-writer recovery, multi-user security and cross-process quota tests become
mandatory only before promising those capabilities. These are proposed gates,
not tests of a service that does not exist.
