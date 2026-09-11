# Post-A3 Deployment Architecture Review

## 1. Decision, scope and baseline

**Decision: `READY_FOR_POST_A3_CONSOLIDATION`.**

Promote the bounded [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md):
local Python first, isolated invocation state, portable filesystem replay and
conditional service/worker/storage adoption gates. No runtime foundation is
needed to proceed to consolidation. The separate `POST_A3_PRE_A4_FOUNDATION`
remains mandatory before A4 runtime, not before further design.

Review date: **2026-09-11, Asia/Kolkata**. Entry HEAD:
`ad5e7a9fedea6efc7a3b9287a6ad1610421c92a9`. Accepted runtime/closure base remains
`tiaf-a3-baseline` at `e690da2ce0a1dc0d3eb263c3b9e8e59ad52b6212`.
Entry worktree already contained the pass-3 A4 architecture/review and seven
documentation integrations, plus an unrelated document lock file. Those changes
were preserved; this review advances the integration documents without changing
the historical pass-3 review or its normative A4 design.

The supplied deployment brief defines requested design scope, not evidence that
its illustrative services, databases or queues exist. Repository source and
accepted milestone records establish current behavior. No runtime, configuration,
dependency, test or script changes; no credentials read or live calls; no commit,
tag or push. This is not a production security certification or live acceptance.

## 2. Inputs and implementation evidence

Reviewed the [system architecture](TIAF_SYSTEM_ARCHITECTURE.md),
[pass 1](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md),
[source architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md),
[pass 2](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md),
[A4 architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md)
and [pass 3](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md).
Also reviewed [A3.8](TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md),
[A3.10](TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md),
[capability map](TIAF_CAPABILITY_MAP.md), [targets](TIAF_IMPLEMENTATION_TARGETS.md),
[roadmap](TRADINGINTELLIGENCE_ROADMAP.md) and [deferrals](TIAF_DEFERRAL_REGISTER.md).

Read the [deployment TBD](TBD_TI_DEPLOYMENT_ARCHITECTURE.md) section-by-section.
Selected session/authority/placement sections of the
[Shell thesis](TBD_TI_SHELL_THESIS.md), async/security sections of
[CLI/Web interaction](TBD_TI_CLI_WEB_UI_INTERACTION_ARCHITECTURE.md),
shared evidence/scheduling/TM/failure sections of
[monitoring](TBD_TI_MONITORING_ARCHITECTURE.md), and headless/cost/placement
sections of [forecasting](TBD_TI_FORECASTING_ENSEMBLE_LEARNING_ARCHITECTURE.md)
were considered as hypotheses only. Their product/workflow details are not promoted.

| Repository evidence | Finding and deployment consequence |
|---|---|
| [Package metadata](../pyproject.toml), [app bootstrap](../src/tiaf/app.py), [service namespace](../src/tiaf/service/__init__.py) | Python package plus static app metadata, not a running public API or lifecycle/composition root. A logical TI_CORE does not require package relocation. |
| [A3.9 assembly](../src/tiaf/service/opportunity_intelligence/assembly.py), [exports](../src/tiaf/service/opportunity_intelligence/__init__.py) | Pure captured-input assembly is a useful typed seam. Package exports do not implement consumer identity, grants or a curated catalog. |
| [Workflow exports](../src/tiaf/workflows/__init__.py), [coordinator](../src/tiaf/workflows/coordinator.py) | Direct Python orchestration with bounded threads/deadlines and reservations. Not durable jobs or force-killable execution. Keep in-process initially. |
| [ControlledServices](../src/tiaf/workflows/services.py) | Mutable router/graph/acquisition composition and RLock/Future single-flight belong to a trusted owner. One object's lock is not global quota control, multi-tenant isolation or a distributed cache. |
| [Agent registry](../src/tiaf/agents/registry.py), [gateway cache](../src/tiaf/agents/gateways/cache.py) | Mutable registry/dict cache; semantic keys exclude budget/authority bookkeeping. Do not claim general concurrent sharing, size bounds or permission-safe multi-user caching from these alone. |
| [LangGraph adapter](../src/tiaf/workflows/langgraph_adapter.py) | Optional framework wiring around the same coordinator; tracing disabled, no durable checkpoint configuration. Framework presence does not supply restart/resume. |
| [Yahoo connector](../src/tiaf/market_intelligence/providers/yahoo_mcp.py), [Tapetide connector](../src/tiaf/market_intelligence/providers/tapetide_mcp.py) | Existing stdio subprocesses and connector lifecycle threads. "Single-process TI" must mean one Core application runtime, not deny those processes or treat them as isolated TI services. |
| [A3.10 store](../src/tiaf/a3_hardening/store.py) | Check-then-write and check-then-append, no cross-process transaction/locking/atomic publication guarantee. Restrict to single writer per root; stronger hosting needs explicit recovery/publication acceptance. |
| [Package integrity](../src/tiaf/a3_hardening/package.py), [replay](../src/tiaf/a3_hardening/replay.py) | Portable manifest/blobs and provider-free reconstruction already exist. Use this boundary across topology changes; do not fetch live artifacts to repair exact replay. |

These are scope limitations, not newly discovered scoring defects requiring an
A3 patch. No measured load/SLO or independent consumer requirement establishes
a need for services, database, queue or cloud now. Production adoption must be
justified by future operational evidence, not this design's illustrative levels.

## 3. Decisions by concern

The linked normative architecture contains the enforceable details. This table
records the review outcome, including the deferred portions.

| Concern | Decision |
|---|---|
| Near-term topology | One trusted Core application runtime, direct typed Python, request-local composition and a single corpus writer. Small curated facade/lifecycle owner is the next consumer-boundary target, not already implemented. |
| Levels | L0 valid with limits; L1 revised local engineering target; L2 revised conditional multi-app service; L3 conditional production, not mandatory distribution. Each promotion needs the prerequisites/exit tests in architecture §2. |
| Shell | Same process initially, session memory outside Core, fresh typed invocation and grants every time. Remote placement later changes transport only. Engineering access is separately admitted. |
| TM | Library acceptable for trusted prototypes; separate local TI host preferred for operational TM failure/credential isolation at A8. Remote only when required. Broker/TM authority and restart reconciliation never migrate into TI. |
| Web/scanners/apps | Trusted Python facade, local service for independent/non-Python consumers, remote for cross-host demand. Shared factory, not copied composition. Browser through backend; neither Web nor Shell calls the other. |
| Process boundaries | Split for demonstrated trust/credential, failure, resource, lifetime/release, concurrency or scaling need, never to mirror logical boxes. Existing MCP subprocesses remain adapter-local. |
| State | Invocation owns analysis/grants/budget/A4 work; session owns UI context; runtime owns eligible caches/single-flight; artifact store owns canonical captures/lineage. Future mandates/jobs/outcomes need explicit durable owners. TM/broker own live positions. |
| Storage | Filesystem now, one writer/root. Embedded DB for actual transactional local needs; shared DB for multi-host/writer requirements; distributed only with evidence. Immutable history, rebuildable indexes, explicit retention/restore. |
| Reuse | Semantic/source-version/PIT/freshness compatibility plus current entitlement on reads. No symbol-only key, shared mutable analysis or future-as-of leakage; shared call accounting is not duplicate billing. |
| Secrets | Adapter host configuration, minimized process propagation, no canonical/prompt/replay/log credentials. Broker secrets stay with TM. Authn, invocation authz, data entitlement and epistemic source authority remain distinct. |
| Concurrency | Initially one top-level live request, accepted bounded inner waves; startup-only registry composition, request-local mutable services, serialized writes. Cross-process quotas and durable reservations are not current capabilities. |
| Long-running work | Defer workers/queues/scheduler until survival, backpressure or scheduled outcome/mandate requirements exist. Durable attempts, idempotency, budgets and cancellation semantics precede reliable background work. DEF-010/051 remain. |
| Failure isolation | Typed provider/parser/model failures now; held unknown usage after timeout. Core exceptions are not market opinions. Separate workers only for concrete impact; no fake cancellation/recovery or automatic live replay repair. |
| Observability | Semantic captures separate from redacted operational timing/health/pressure/resource metrics; link IDs only. Increase operational telemetry with exposure; no telemetry vendor or billing catalog invented. |
| Network | Wrap curated capabilities, not internals. Protocol unselected; bounded sync first, async/streaming only with real job lifecycle. Versioned admission, authorized artifacts, scoped idempotency and outcome-unknown handling. |
| Containers/cloud | Docker optional later packaging; cloud requires target/security/rights/restore/cost justification. Kubernetes and distributed component bundle premature. None needed now. |
| Models | Optional gateway API client in-process; heavy/unstable/private inference may need workers. Location never raises authority or alters no-LLM/evidence semantics; A3.8 remains no-LLM. |
| Replay | Local portable offline remains reference; service export must support authorized offline reconstruction. Missing artifacts/version mismatch explicit, no provider/model live fallback; distributed evaluation stays deferred. |
| Versions | Package, schema, capability, policy, adapter, transport and command versions separate. Reject mismatch before effects, preserve original records, explicit conversions/comparisons; rolling upgrades not required now. |
| Security levels | Trusted Python is not a sandbox; same-user processes not automatically isolated; localhost requires auth; LAN needs authenticated protected transport; remote adds tenant/object/entitlement, privacy, abuse and recovery controls. |
| Foundation | Internal, deployment-neutral, in-process source projection first. No mandatory public export/service; later narrow facade can expose approved operations. Do not delay semantic work for hosting. |
| A8/A9/A10 | TM/conditional service at A8, scanner integration A9, operational durability/health/SLOs A10. Early facade/admission/lifecycle slices accompany actual consumers without advancing all infrastructure. |

No configuration profile may silently change A2 policy, A3/A4 meaning or model
permission. All datetimes retain `ZoneInfo("Asia/Kolkata")`, reject naive values
and emit `+05:30`. Tuple semantics/JSON arrays remain. Package `0.1.0` and A0
contract schema `1.0` remain separate unchanged concepts.

## 4. Complete deployment TBD disposition

The original numbered sections remain historical text beneath a new disposition
notice. This table is the section-by-section interpretation; the promoted
architecture wins over obsolete "future review" wording in that note.

| Original section | Disposition | Rationale / destination |
|---|---|---|
| 1 Why this document exists | PROMOTE | Logical ownership versus hosting distinction retained; architecture §1 now answers near-term placement. |
| 2 Hard invariant | PROMOTE | Semantic/authority/replay invariance governs every topology. |
| 3 Deployment stages | SPLIT | L0 valid, L1 revised with absent-facade and MCP qualifications; L2 conditional; L3 menu KEEP_TBD rather than automatically promoting a distributed stack. Architecture §2. |
| 4 Questions to answer | SUPERSEDE | Replaced by concrete decisions, state/security tables and promotion gates in architecture §§3–13; operational sizing/protocol specifics remain open. |
| 5 Shell deployment questions | REVISE | In-process local mediator chosen initially, no privilege shortcut; remote possible later. No Shell feature/grammar promotion. |
| 6 Web deployment questions | REVISE | Independent consumer/backend, conditional service, session separation. UI, job product design and transport selection remain TBD. |
| 7 TradeMonitor relationship | PROMOTE | Authority invariant retained; architecture §3 adds prototype/library versus operational/local-host recommendation. |
| 8 Shared evidence vs state | PROMOTE | Add complete reuse eligibility, reauthorization and multi-process ownership limits (§§4/6/8). |
| 9 Adapter deployment | REVISE | Preserve existing MCP processes, ordinary API clients in-process; isolate only when justified, no sandbox claim. |
| 10 Persistence | SPLIT | Filesystem/single-writer now and transactional triggers promoted; DB/vendor/shared/distributed deployment and production retention values KEEP_TBD. |
| 11 Microservices non-goal | PROMOTE | No service mesh/event bus/locks merely to mirror diagrams. Mandatory per-Agent/service splitting REJECTED. |
| 12 Deployment profiles | KEEP_TBD | Profile names are illustrative, not a new runtime enum. Separation of topology and intelligence/model policy is promoted. |
| 13 Deferral relationship | REVISE | Existing IDs remain; architecture §13 reconciles local facade, A8/A9 delivery and A10 operational gates without duplicate IDs. |
| 14 Planned revisit | SUPERSEDE | Three passes and this review complete; full post-A3 consolidation is next, implementation separately authorized. |
| 15 Promotion criteria | SPLIT | Local target and gating/security/replay criteria satisfied as design. Actual Level 2/3 recovery/SLO/capacity acceptance must be demonstrated later. |
| 16 Current decision | SUPERSEDE | Capture-only replaced by approved bounded deployment architecture and readiness for consolidation; still no runtime implementation. |

Unrelated Shell commands, Web UX, monitoring mandates/schedules and forecasting
algorithms remain hypotheses. No separate TBD is silently upgraded into an
implementation directive. Historical pass reviews remain historical.

## 5. Mandatory complexity audit

1. **Service needed now? No.** A library/facade supports the next trusted local
   work. An operational TM or independent consumer can justify a local host later.
2. **Database needed now? No.** Existing filesystem captures suffice for bounded,
   single-writer use. Transactional jobs/concurrent writers change that premise.
3. **Queue needed now? No.** Bounded in-request work is not a daemon. Add durable
   admission/jobs only when work must outlive the caller or be scheduled.
4. **Docker needed now? No.** No concrete deployable host target requires it.
5. **Kubernetes needed now? No.** No measured orchestration/HA requirement exists.
6. **Multi-process needed now? No new Core split.** Existing MCP connector
   subprocesses remain; do not collapse/reimplement them to claim one OS process.
7. **What remains direct Python?** Admission/facade to Core, normalization,
   Planner/specialists, captured assembly/replay, foundation and initial A4.
8. **Immediate useful operational abstraction?** Trusted composition/invocation
   lifecycle, scoped resources and single-writer ownership. Small and testable,
   no general runtime framework or second ledger.
9. **What stays reversible?** Transport, process placement, cache backend,
   concrete store, packaging/cloud and worker topology. Evidence meaning,
   authority boundaries, original captures and honest cost/PIT are not negotiable.

## 6. Staged delivery and governance

Recommended sequence:

1. Full post-A3 consolidation/replanning reconciles the four completed design
   passes, remaining TBDs, deferrals and bounded implementation acceptance gates.
2. Separately authorize in-process POST_A3_PRE_A4_FOUNDATION; no hosting dependency.
3. Implement a narrow local capability/lifecycle slice under DEF-003 before actual
   Shell/public consumer use (recommended before A4). Internal foundation/A4 work
   need not wait for an exhaustive catalog or remote service.
4. Separately accept deterministic A4 and later local consumers. Existing A4
   Planner bridge and optional model prerequisites remain intact.
5. Introduce local service for demonstrated multi-app/TM isolation; remote
   deployment and durable workers/storage only at their explicit security,
   transaction, quota and operational gates.

No milestone renumbering or DEF status changes are needed. Preserve all 55
records: 43 DEFERRED, 3 PLANNED, 4 IMPLEMENTED, 3 REJECTED, 2 SUPERSEDED.
DEF-003 local/remote tracks and DEF-004 TM remain planned; 009/010/011/049/050/051,
052 and 055 are not closed by architecture. Proposed deployment acceptance
tests in architecture §13 are future gates, not executed service tests.

## 7. Files, validation and next prompt

Created this review and [TIAF_DEPLOYMENT_ARCHITECTURE.md](TIAF_DEPLOYMENT_ARCHITECTURE.md).
Updated deployment TBD status/disposition, README, architecture overview,
system architecture, TBD index, roadmap, capability map and implementation targets.
No deferral-register edit was justified. Source/A4 semantic architecture and
prior pass reviews remain unchanged from turn entry.

Exact turn-local changes (distinct from the pre-existing pass-3 diff):

- Created `docs/TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md`.
- Created `docs/TIAF_DEPLOYMENT_ARCHITECTURE.md`.
- Updated `README.md`.
- Updated `docs/ARCHITECTURE.md`.
- Updated `docs/TIAF_SYSTEM_ARCHITECTURE.md`.
- Updated `docs/README_TBD_DESIGN_NOTES.md`.
- Updated `docs/TBD_TI_DEPLOYMENT_ARCHITECTURE.md`.
- Updated `docs/TIAF_CAPABILITY_MAP.md`.
- Updated `docs/TIAF_IMPLEMENTATION_TARGETS.md`.
- Updated `docs/TRADINGINTELLIGENCE_ROADMAP.md`.

Executed focused offline regression:

```bash
.venv/bin/pytest -q \
  tests/unit/workflows \
  tests/unit/a3_hardening \
  tests/unit/agents/test_gateway_architecture_security.py \
  tests/unit/agents/test_evidence_gateway_runtime.py \
  tests/unit/opportunity_intelligence/test_integrity_boundaries.py
```

**145 passed in 89.68s.** Includes existing single-flight/reservation/timeout,
captured replay, package-store integrity, public acceptance and import/authority
boundary tests. These support the description of existing local behavior, not
new multi-user/service/durability guarantees.

Additional checks:

- `git diff --check`: PASS.
- 187 local Markdown link targets across the 10 turn-edited documents: all resolve.
- Final newlines and paired fenced blocks: PASS; both new documents have no
  trailing whitespace (checked separately because untracked files are not in
  ordinary `git diff --check`).
- All 16 original deployment sections have explicit dispositions.
- Entry-file hash comparison: only the eight listed existing Markdown files
  changed; two new Markdown files, no deletion. Prior source/A4 architectures,
  all three pass reviews, deferral register and unrelated lock file unchanged.
- Deferral inventory: 55 IDs, unchanged status counts recorded in §6.
- No runtime/source/script/test/dependency edits. Full pytest/compile/lint/type
  gates were not rerun for this documentation-only pass. No live or production
  deployment validation is claimed.

Exact next Codex prompt title:

**Post-A3 Consolidation and Replanning — Accepted Architecture, TBD Dispositions,
Deferral Reconciliation and Bounded Implementation Plan**

That pass should consolidate, not silently implement: retain frozen A1/A2/A3,
the pre-A4 semantic gate, the small local facade track and conditional deployment
triggers. It should not add services/cloud/queues or begin A4 without separate
implementation authority.
