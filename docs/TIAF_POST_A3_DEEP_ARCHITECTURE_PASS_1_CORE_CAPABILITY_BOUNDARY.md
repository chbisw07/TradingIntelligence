# Post-A3 Deep Architecture Pass 1 — TI_CORE and Capability Boundary

## 1. Decision and verified baseline

**Decision: `READY_FOR_DEEP_ARCH_PASS_2`.**

**Architecture verdict: `APPROVE_WITH_REVISIONS`.** The revised top-level design
is promoted to [TIAF_SYSTEM_ARCHITECTURE.md](TIAF_SYSTEM_ARCHITECTURE.md).
This is a documentation-only architectural decision, not a runtime acceptance
claim for a new capability facade. No implementation foundation is needed to
proceed to the next design pass. A4 implementation remains unopened.

Review date: **2026-09-11, Asia/Kolkata**. The entry worktree was clean. HEAD is
`e690da2ce0a1dc0d3eb263c3b9e8e59ad52b6212`, tagged `tiaf-a3-baseline`;
its parent implementation baseline is `68134f6` (`tiaf-a3.10`). A1/A2 major
baseline tags also exist. The closure/deferral documentation is committed in
that starting baseline; this review creates no commit, tag or push. Historical
closure statements recommending a tag describe their review-time state, not a
reason to recreate it. The register has stable IDs DEF-001 through DEF-055.

The attachment is the requested scope, not proof of implemented behavior.
Repository code, tags and accepted records substantiate the findings below.

## 2. Evidence examined and authority

The review inspected the foundation roles and public contracts in the
[A1 baseline](TIAF_A1_FOUNDATION_BASELINE.md) and
[A2 baseline](TIAF_A2_FOUNDATION_BASELINE.md); the
[A3 architecture](TIAF_A3_ARCHITECTURE.md),
[detailed roadmap](TIAF_A3_DETAILED_ROADMAP.md),
[A3.8 design](TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md),
[A3.9 design](TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md),
[A3.10 design](TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md),
[major closure](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md) and
[deferral discovery audit](STUDY_A3_SUBMILESTONE_DEFERRAL_DISCOVERY_AUDIT.md).
It checked the [register](TIAF_DEFERRAL_REGISTER.md),
[capability map](TIAF_CAPABILITY_MAP.md),
[implementation targets](TIAF_IMPLEMENTATION_TARGETS.md),
[canonical roadmap](TRADINGINTELLIGENCE_ROADMAP.md),
[README](../README.md) and [CHANGELOG](../CHANGELOG.md) for status/scope alignment.

The six [TBD notes](README_TBD_DESIGN_NOTES.md) were reviewed as hypotheses,
especially their boundary, authority, sharing and sequencing claims. Runtime
inspection covered `tiaf.app`, `service`, A1 context, A2 baseline/evaluation,
Agent contracts and A3.2 gateways, MI routing/confirmation/research, A3.8
planner/workflows, A3.9 assembly/replay, A3.10 hardening, and acceptance scripts.
Concrete anchors appear in section 5. This is not an exhaustive new code audit
or a rerun of the previous live-acceptance studies.

The promoted document governs top-level future architecture, not retroactive
runtime semantics. Milestone records govern accepted implementations; roadmap
and register govern delivery. Remaining TBD content is non-authoritative.

## 3. What is approved, revised and not promoted

The kernel/boundary proposal fits existing code because A2 computation, A3
interpretation, structured assembly and replay already have distinct roles.
Consumers currently face heterogeneous package APIs and trusted composition,
so the future coupling problem is concrete, not merely speculative.

| Hypothesis | Disposition and reason |
|---|---|
| TI_CORE plus a curated capability boundary | Adopt. Core is logical domain/application behavior, not a new package, process or wholesale relocation. |
| All Agents sit outside Core as clients | Revise the thesis diagram: specialists, governed research and future arbitration can be Core-side; interaction/external Agents are application-side consumers. Model identity does not determine placement. |
| Everything under A1-A3 is Core | Revise. Canonical semantics/use cases are Core-side; provider SDKs, MCP transports, framework execution wiring and concrete persistence are replaceable infrastructure even when co-located. |
| A3.9 is already the whole public API | Reject that inference. Its captured-input assembler is useful; it is not an authenticated live orchestration/data-entitlement facade. |
| Exhaustive CLI, selective Web | Adopt selective UI coverage; reject exhaustive access to internals. Shell exposes only curated public and authorized engineering capabilities. |
| Shell v0.1 immediately after A3, including NLP/models | Defer feature list. Its prerequisite is the small governed capability subset it consumes, not a full catalog or model integration. No Shell implementation here. |
| Shared immutable evidence | Adopt with identity, freshness, PIT and permission checks; do not promote global caches or shared mutable request/session state. |
| A universal source hierarchy resolves conflicts | Do not adopt. Existing confirmation/lineage remains valid, but field/time/claim-specific authority and contradiction semantics require pass 2. Source class alone is not a winner. |
| Monitoring, event-driven updates, ensembles and learning | Preserve placement hypotheses only. A5/A7/A10 prerequisites are not delivered by naming capabilities; confidence is not calibrated probability. |

These revisions prevent the top-level thesis from silently approving adjacent
Shell, source-citation, forecasting or monitoring proposals. They preserve the
economic-interest north star, bounded costs and explicit non-action outcomes.

## 4. Capability publication candidates

Names below are **design IDs**, not callable functions, assigned versions or
current discovery results. Curate at publication with a demonstrated consumer;
do not generate a registry from `__all__` or publish every calculator method.

| Family / illustrative operation | Existing substrate | Publication limit |
|---|---|---|
| Evidence: `evidence.context` | A1 resolver/runtime/AnalysisContext and canonical MI facts | Bounded read through governed acquisition; caller cannot supply SDK objects or arbitrary source URLs. Preserve native provenance by reference. |
| Evidence: `evidence.company_research` | A3.6.2 integrated research and confirmation | Gate costly enrichment, data scope and depth; do not imply full source coverage or general browsing. |
| Intelligence: `baseline.assess` | A2 feature/indicator/relative/MTF/baseline path | Deterministic typed inputs/policy; acquisition is a distinct explicit stage. A2 rank remains its own operation. |
| Intelligence: `specialist.inspect` | AgentRuntime plus registered specialists | Publish only justified specialist views with supplied evidence and scoped authority, not arbitrary `.analyze` injection. |
| Intelligence: `opportunity.assemble` | A3.9 captured-input assembler | Best initial narrow public seam: one underlying, no acquisition/rerun, preserves opinions and A2. |
| Intelligence: `opportunity.orchestrate` | A3.8 planner/workflows then A3.9 | Needs trusted facade; explicit execution intent, registry/services hidden, bounded acquisition and capture. Not investment arbitration. |
| Replay: `replay.recorded` | A2.10, A3.8/9 recorded readers, A3.10 packages | Public candidate for authorized persisted records; distinguish capture format/scope, no fallback to live. |
| Engineering: verification/comparison/trace/graph/ledger/normalization | A3.10, workflow captures and MI audits | Named bounded diagnostics, sanitized typed projections and explicit execution effects. No arbitrary object graph or filesystem access. |
| Later intelligence | A4 challenge, A5 position advice, A6 expression, A7 forecasting/evaluation | Roadmap-owned, unavailable now. A3.9 observation states are not future actions; DEF-053 still owns cross-candidate A3 work. |

Evidence access and canonical intelligence are useful capabilities; cache
eviction functions, reducer steps and policy helpers are not. A public read of
an authorized replay record and engineering deterministic verification are
different operations, even if they share underlying parsers.

## 5. Current code seam classification

These are boundary recommendations, not removals of existing documented Python
exports. Where two concerns share a module, classify the operations separately.

| Current seam / source anchor | Classification | Consumer rule / reason |
|---|---|---|
| [app.create_app_context](../src/tiaf/app.py) | `SHOULD_NOT_BE_EXPOSED` | Static bootstrap metadata still says TIAF_TGT0. Not a runtime capability catalog, health endpoint or current milestone oracle. Leave unchanged here. |
| [service namespace](../src/tiaf/service/__init__.py) | `NEEDS_CONTRACT_STABILIZATION` | Placeholder namespace text does not describe a governed service. Its A3.9 child is real; neither implies remote service availability. |
| [A1 context builder](../src/tiaf/context/builder.py), [resolver exports](../src/tiaf/data/resolution/__init__.py), [runtime exports](../src/tiaf/data/runtime/__init__.py) | `NEEDS_FACADE` | Preserve normalized contracts; hide coordinator/provider construction and privileged runtime settings from normal callers. |
| [BaselineEngine.assess](../src/tiaf/baseline/engine.py) and [baseline exports](../src/tiaf/baseline/__init__.py) | `ALREADY_GOOD_PUBLIC_SEAM` | Typed deterministic substrate; a published facade adds admission/version discovery, not a second scorer. |
| [A2 replay](../src/tiaf/evaluation/replay.py) | `GOOD_ENGINEERING_SEAM` | Existing typed replay/evaluation; distinguish recorded input, recomputation and policy comparison when curating operations. |
| [Agent contracts/runtime exports](../src/tiaf/agents/__init__.py) | `NEEDS_FACADE` | AgentOpinionV2 and evidence contracts are reusable; registry/runtime construction is trusted assembly, not a consumer injection hook. |
| [A3.2 gateway policy](../src/tiaf/agents/gateways/policy.py) and [gateway exports](../src/tiaf/agents/gateways/__init__.py) | `INTERNAL_ONLY` | Legitimate Core-side ports for Agents. EvidenceGatewayRuntime/ReasoningGateway are not end-user authentication, entitlement or remote APIs. |
| [MI router](../src/tiaf/market_intelligence/routing.py), [research controller](../src/tiaf/market_intelligence/deep_research.py), [confirmation gateway](../src/tiaf/market_intelligence/authoritative.py) | `NEEDS_FACADE` | Reuse acquisition/normalization rules; operator-owned route/source policies, parsers, registries and adapters stay trusted. |
| [MI provider exports](../src/tiaf/market_intelligence/providers/__init__.py), [Dhan adapters](../src/tiaf/data/providers/dhan/__init__.py) | `SHOULD_NOT_BE_EXPOSED` | Consumers must not depend on native transports/ticker conventions. Controlled native-observation debugging is a separate engineering projection. |
| [planner.build_plan and contracts](../src/tiaf/planner/__init__.py) | `GOOD_ENGINEERING_SEAM` | Useful plan inspection; no public dependency on PlanNode/reducer internals. A plan is not an execution grant or investment decision. |
| [run_serial](../src/tiaf/workflows/coordinator.py) and [ControlledServices](../src/tiaf/workflows/services.py) | `NEEDS_FACADE` | Portable output, but caller supplies AgentRegistry and potentially router/graph/research handles. Hide those before consumer publication. |
| [LangGraph adapter](../src/tiaf/workflows/langgraph_adapter.py) | `INTERNAL_ONLY` | Same coordinator semantics behind optional infrastructure; no framework objects in published results. |
| [A3.9 assemble_opportunity_intelligence](../src/tiaf/service/opportunity_intelligence/assembly.py), [contracts/exports](../src/tiaf/service/opportunity_intelligence/__init__.py) | `ALREADY_GOOD_PUBLIC_SEAM` | Typed captured-input run result; defensively reconstructs metadata-bearing models and validates policy/handoff without provider or specialist execution. Not yet the consolidated governed facade. |
| [A3.9 request_from_capture](../src/tiaf/service/opportunity_intelligence/handoff.py) | `NEEDS_CONTRACT_STABILIZATION` | Convenient validated builder, but `policy: object` and raw capture JSON are engineering conveniences; public policy selection should resolve an approved policy identity. Do not alter existing captures. |
| [A3.9 capture/replay/verify](../src/tiaf/service/opportunity_intelligence/replay.py) | `GOOD_ENGINEERING_SEAM` | Three distinct semantics: serialize, recorded reconstruction, pure assembly recomputation. Public replay must not collapse them. |
| [A3.10 exports](../src/tiaf/a3_hardening/__init__.py) | `GOOD_ENGINEERING_SEAM` | Package capture/replay/verification, observational comparison, accounting and failure tools. Do not expose all helpers as consumer capabilities. |
| Public name derived from `a3_hardening` | `NEEDS_RENAMING` | At publication choose semantic replay/audit operation names, not milestone names. No package rename or breaking import change is required. |
| [A3.10 corpus store](../src/tiaf/a3_hardening/store.py) | `INTERNAL_ONLY` | Local append-only filesystem adapter, not a multi-user storage API; public consumers must not supply arbitrary privileged paths. |
| [specialist projection](../src/tiaf/planner/projection.py), [handoff detail decoder](../src/tiaf/service/opportunity_intelligence/handoff.py), digest/cache helpers | `INTERNAL_ONLY` | Existing typed extraction and hashing remain implementation details. Consumers use cited result fields/refs, not parse specialist metadata or recompute hashes themselves. |
| [A3.8](../scripts/a3_8_user_acceptance.py), [A3.9](../scripts/a3_9_user_acceptance.py), [A3.10](../scripts/a3_10_user_acceptance.py) acceptance scripts and smoke scripts | `TEMPORARY_SCRIPT_ENTRYPOINT` | Valid diagnostic/test entrypoints, not stable external APIs. Synthetic fixture builders and printed tables must not become application dependencies. |

The danger is not a demonstrated new runtime defect. It is treating trusted
composition APIs as if they already enforced a public caller boundary. Existing
in-repository imports and direct function calls remain appropriate inside their
declared layer; forcing them all through a dispatcher would add no safety.

## 6. Capability catalog verdict

**A small explicit catalog is useful; a formal executable registry is not an
immediate prerequisite.** Before A4, SHOULD prepare a reviewed static catalog
for the first actual consumer operations. Before any Shell/public publication,
its implemented subset must have stable typed descriptors and discovery tests.
Do not block pass 2 on this work. After A4, grow it only as real consumers need
additional operations. Near A8, add remote negotiation and deployment availability.
Dynamic plugin discovery/loading and a network registry are unnecessary now.

Proposed descriptor: semantic ID, capability version, interface level, request/
result schema identities, authority and data scope, effects (pure/captured-read/
live-read/persist), deterministic/model support, replay modes, cost class, current
availability and deprecation information. Operator-only configuration binds an
implementation adapter. Public discovery must not disclose secrets, private
source configuration or callable objects; it is not permission to invoke.

Reuse Agent and MI registries underneath. A public operation may compose several
Agent capabilities and fine provider capabilities; those are not interchangeable
IDs or a reason to unify the three registries.

## 7. Authority and invocation model

Caller identity is resolved by trusted embedding/runtime configuration now and
authenticated transport later. Do not trust an arbitrary request's role or
`allowed_capabilities` as a grant. The facade computes an effective intersection
of operator ceiling, caller grant, data rights, operation scope, requested scope,
profile and model policy; budget limits must fit all ceilings. No wildcard tools,
URL/shell execution passthrough, self-selected registries or model adapters.

A3.2 already supplies least-privilege gateways/budget vocabulary. A3.8 already
captures purpose, horizon, inventory, as-of, intent, bounds and permitted scope,
and rejects non-no-LLM execution. These are foundations, not implemented
multi-tenant identity/access control. New admission would retain the existing
reservation/accounting mechanism rather than debit it twice. Core enforces
semantic validity and scoped gateway policy; the facade owns authenticated
context and trusted composition; the transport owns credential verification.

Developer/operator roles may authorize extra diagnostics, not trading or data
rights by default. Profiles request depth, not authority. NL and an Interaction
Agent cannot expand grants. Core-side/external Agent tools are capability-scoped.
Recorded data reads still require entitlement checks. A read-only live request
can spend quota/money; its effect must be explicit and bounded. No TI role grants
broker operations or overrides TradeMonitor governance.

## 8. Agents, Shell, Web and other consumers

Agent means bounded actor; model means optional replaceable reasoning engine.
Specialists and later arbitration are Core-side. Research actors are Core-side
when implementing governed research use cases; a Shell research conversation is
application-side and invokes those capabilities. Interaction Agents and external
Agents are consumers. No mandatory model vendor, production model adapter or
new prompt path is approved; DEF-052 remains open.

Shell is a stateful mediator: command/session/optional NL interpretation and
rendering, not canonical intelligence. Its small governed subset must precede
Shell v0.1. Developer operations require real grants. Web, TM, scanners, scripts
and external apps invoke capabilities independently; Web never invokes Shell,
and Shell never invokes Web. Python facade first; remote transport later. Do
not fork scoring or parse stdout to create an alternative intelligence path.

## 9. Shared evidence versus per-request analysis

Core owns canonical identity, quality, freshness, PIT rules and semantic
fingerprints; runtime owns eligible cache/single-flight reuse and reservations;
applications own session state. Every invocation retains subject, objective,
horizon, as-of, profile/version, authority reference, budget, position-context
identity and run identity. TM is still the source of operational position truth.

Allow evidence reuse only when source identity/revision, period/expiry/timeframe,
adjustment/mapping semantics, information availability and permission scopes are
compatible. A DAY analysis and a POSITIONAL analysis may share eligible company
facts, not each other's conclusions, plans, budgets or freshness decisions.
Same-symbol identity alone is insufficient. Cached access is re-authorized;
redacted views must not be passed off as an original full capture.

Frozen tuples protect finalized collections, but legacy metadata can remain
mutable. Preserve defensive reconstruction before fingerprinting/admission;
do not assert universal deep immutability. A semantic hash is neither source
authentication nor proof that evidence existed at a historical as-of. Reusing
evidence cannot solve DEF-049 arbitrary historical PIT reconstruction.

## 10. Versioning and compatibility

Keep separate package (`0.1.0`), A0 contract (`1.0`), capability semantic,
request/result schema, policy, provider/normalizer, Shell grammar and future
remote protocol versions. Existing A3 child versions remain independent.
No facade version is assigned by this pass.

At publication document supported schemas, effects and deprecation. Breaking
meaning/required fields needs a new version; “additive” fields/enum members are
not automatically safe for strict validated readers. Deprecation includes an
explicit supported window, replacement and archived replay strategy. Preserve
old bytes/hashes and pinned policies; migration is attributable and comparison
creates a new run. Private helpers have no external compatibility promise;
engineering exports must declare experimental versus supported status.

## 11. Stable failures without flattening domain meaning

Current evidence: [A1 typed errors](../src/tiaf/data/errors.py),
[A3.2 gateway statuses](../src/tiaf/agents/gateways/enums.py), MI provider
failure/status enums, [planner stops](../src/tiaf/planner/models.py), A3.9
`CaptureIntegrityError`, and [A3.10 failure lineage](../src/tiaf/a3_hardening/contracts.py).
They already distinguish missing data, unavailable services, budget/authority
denial and capture corruption. Do not replace them with a giant enum.

| Proposed capability-level handling | Preserve underneath |
|---|---|
| `INVALID_REQUEST`, `UNSUPPORTED` | Validation failure versus unsupported instrument, operation, schema or policy, with safe field/detail references. |
| `PERMISSION_DENIED`, `MODEL_DISABLED`, `BUDGET_EXCEEDED` | Which admission/gateway limit denied work; a provider credential failure is not automatically caller permission denial. |
| `UNAVAILABLE`, `FAILED` | Retryability and provider/transport/schema-drift cause. Rate-limit, timeout and terminal failure remain distinguishable child codes. |
| `STALE`, `PARTIAL`, `INSUFFICIENT_EVIDENCE` | Quality/coverage outcomes, potentially with a valid partial intelligence result; not proof of negative market direction. |
| `REPLAY_INTEGRITY_ERROR` | Missing blob, checksum/reference, schema/policy incompatibility with exact child lineage; fail closed, no live reconstruction fallback. |

This is a future mapping design, not implemented enum names or a change to
current exceptions. Keep namespaced child codes, safe messages and artifact/run
refs; preserve original cause in authorized audit storage, never leak secrets.
Do not map `NO_TRADE`/`ABSTAIN` to HTTP errors. Transport failures and valid
domain results remain separate. No automatic retries without budget/intent rules.

## 12. Result-contract philosophy

Prefer operation-specific contracts with shared components. Preserve applicable
canonical state, quality, gaps, contradictions, reasons, confidence basis,
provenance, replay identity, usage/cost knowledge and authority/non-action meaning.
An evidence read does not need an opportunity score; a replay verification does
not need a position envelope. Do not flatten A3.9 into the A0 action-bearing
OpportunityAssessment or collapse evidence/self-reported/calibrated confidence.

Full records can remain behind typed authorized references, with small consumer
projections that identify their source and filtering. Human prose is not canonical
truth. Citation resolution/compression remains DEF-054 and pass-2 input; internal
lineage already exists. Preserve Asia/Kolkata-aware timestamps, tuple semantics,
JSON arrays, original hashes and independent unknown-versus-zero cost states.

## 13. A4 handoff and DEF-003 disposition

A4 should receive validated A3.9 structured intelligence plus a resolvable A3.8
capture, individual opinions and active/superseded lineage, unchanged A2 baseline
and available evidence, and canonical provenance/confirmation/conflict summaries.
It must not arbitrate solely on compressed prose or majority stance. A3.10
provides packaging, integrity and accounting; it is not a new intelligence source.
Full A2 versus projection-only capture stays explicit. Missing content cannot
be reverse-engineered from score/class, and verification never calls providers.

Before A4 implementation settle these boundary rules and pass-2 claim/source/
contradiction semantics. A4-specific adversarial roles, recommendation policy and
acceptance design remain separate; this pass does not choose them. Internal A4
development may reuse typed A3 seams without waiting for a remote API or Shell.

**DEF-003: split delivery tracks within the existing stable record.**

- Local capability contracts/admission/catalog: architect before A4; a narrow
  facade is SHOULD before A4 and required before actual Shell/external consumer
  publication. This review settles design, not implementation.
- Service/remote transport and operational consumer integration: remain A8
  delivery as required, with production operation in A10. Do not pull those
  milestones forward or create a second intelligence service.

Keep DEF-003 `PLANNED`, retain all 55 stable IDs and the existing status totals.
No separate delivery or implementation is reported closed. A future foundation
pass must identify which local subset is delivered and what A8 obligations remain.

## 14. Mandatory complexity audit

1. **More complex than necessary?** Not as revised: a small admission/facade
   boundary addresses real trusted-construction leakage. A universal framework
   around every package would be excessive.
2. **Essential abstractions:** typed canonical contracts, curated interface
   levels, effective authority/budget, immutable evidence identity, explicit
   invocation/replay modes and existing provider/model ports.
3. **Do not add now:** universal operation envelope, dynamic plugin loader,
   duplicated capability/budget/source registries, microservices, remote schemas,
   event bus, distributed cache/queue, graph database or new model framework.
4. **Keep simple calls:** pure A2 engines, A3.9 assembly, recorded replay,
   typed specialist extractors and in-process composition. Public convenience
   must not turn every internal call into a dispatch or transport hop.
5. **Premature microservices:** separate provider, specialist, replay, catalog
   and facade servers merely to match diagram boxes. No scale/isolation evidence
   here justifies that deployment cost.
6. **Simplification candidates:** consolidate repeated consumer-side assembly
   behind a small facade when needed; keep the serial runner as a supported
   alternative to framework wiring; avoid duplicating typed detail decoding and
   proliferating re-exports. These are future candidates, not code changes or
   claims that existing internal reuse is a defect.
7. **Does the facade reduce complexity?** Yes only if it hides router/registry/
   policy/service construction and stabilizes a few real use cases. A layer that
   just forwards every function with different names is rejected. Require tests
   showing consumers need no private imports and unchanged canonical results.

## 15. Bounded pre-A4 foundation candidates

“Before A4” here means before A4 implementation, not before the next architecture
pass. No runtime work is authorized by this document.

| Candidate | Classification | Bounded completion / rationale |
|---|---|---|
| Core ownership, interface levels, capability admission/version/error/result rules | `MUST_BEFORE_A4` | Design settled by this pass; milestone-specific contracts still need review. No universal runtime rewrite. |
| Source authority/provenance/contradiction semantic contract | `MUST_BEFORE_A4` | Next architecture pass: clarify claim/time/field scope, source independence/revisions, confirmation and unresolved conflict. Decide there whether narrow contract code is needed. |
| First consumer capability request/result contracts | `SHOULD_BEFORE_A4` | Stabilize a small A3.9 captured assembly/replay subset by reusing existing types. Becomes mandatory before its public/Shell use. |
| Small Python facade/re-export module with trusted admission/composition | `SHOULD_BEFORE_A4` | Only justified operations; hide setup handles, pin policy, preserve hashes, deny excess grants and keep replay offline. Can follow pass 2; not an A4-internal-call prerequisite. |
| Small static capability catalog/descriptor skeleton | `SHOULD_BEFORE_A4` | Real supported operations only, matching contracts/effects/availability; no runtime reflection or service. Required with discoverable consumer publication. |
| Shared invocation context components | `SHOULD_BEFORE_A4` | Reuse subject/horizon/as-of/run/budget types and separate trusted authority from caller requests; introduce only fields needed by the first facade. |
| One stable universal application request/result mega-envelope | `REJECT` | Evidence, assembly, verification and later position operations have different semantics. Compose common components instead. |
| Shell v0.1, NLP Interaction Agent, Web | `CAN_WAIT` | Not required to design/arbitrate A4; a later small consumer uses the approved boundary. No exhaustive command rollout. |
| Remote API/authentication stack, deployment negotiation | `CAN_WAIT` | A8-driven integration/security requirements, not a prerequisite for trusted local A4 work. |
| Complete citation rendering, distributed stores/queues, forecasting/model rollout | `CAN_WAIT` | DEF-054/009/010/050/052 and A7/A10 remain distinct. Pass 2 does not imply shipping all source UX. |
| Package relocation, mandatory microservices or dynamic plugin dispatcher | `REJECT` | No demonstrated need; would introduce compatibility and operational cost without solving current semantics. |

A later bounded facade implementation should prove one captured A3.9 assembly
and one recorded A3 replay operation through only declared public imports;
canonical parity; no provider/model calls during replay; denied authority cannot
be raised by profile/NL; no public registry/router handles; explicit partial/
integrity/cost behavior; and preserved old capture hashes. A live orchestration
facade requires additional gateway/entitlement/budget tests before publication.
These are acceptance proposals, not tests executed by this design pass.

## 16. Validation and exact next prompt

Validation for this documentation-only pass:

```bash
.venv/bin/pytest -q \
  tests/unit/agents/test_architecture_exports.py \
  tests/unit/agents/test_gateway_architecture_security.py \
  tests/unit/market_intelligence/test_architecture.py \
  tests/unit/opportunity_intelligence/test_integrity_boundaries.py \
  tests/unit/a3_hardening/test_public_boundaries.py
git diff --check
```

- **44 passed in 39.66s** across those five existing boundary/security/integrity
  test modules. These exercise accepted runtime, not a newly implemented facade.
- `git diff --check`: passed; new documents also checked separately because
  ordinary `git diff` does not include untracked files.
- Local Markdown target check: **158 links, 0 missing**, across all nine changed
  Markdown files (including the two new documents).
- Register check: **55 unique sequential IDs**; 43 DEFERRED, 3 PLANNED,
  4 IMPLEMENTED, 3 REJECTED, 2 SUPERSEDED. DEF-003 remains PLANNED.
- Scope check: seven existing Markdown files updated and two Markdown files
  created; no runtime, test, dependency or configuration file changed. Full
  runtime gates and live acceptance were not rerun for this architecture pass.

No live provider/model call, policy retuning, A4 implementation, commit, tag or
push was performed. Credentials were not read.

**Exact next Codex prompt title:**

**Post-A3 Deep Architecture Pass 2 — Source Authority / Provenance / Contradiction
Semantics for A4**

Keep pass 2 architecture-only: reconcile the existing MI/confirmation/A3.9/A3.10
semantics and the source-fabric hypothesis, decide A4's minimal semantic input
contract, and separate mandatory semantic foundations from later citation UX.
It should not build Shell, tune A3, deploy models or implement A4 arbitration.
