# TradingIntelligence System Architecture

## Status and scope

**Authoritative top-level architecture, post-A3 design pass 1, 2026-09-11
(Asia/Kolkata).** Adopted with the revisions and evidence recorded in the
[capability-boundary review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md).
Accepted runtime baseline: `tiaf-a3-baseline` at
`e690da2ce0a1dc0d3eb263c3b9e8e59ad52b6212`.

This document governs future boundary decisions. Its narrow same-process facade
and static capability catalog are now implemented by
[POST_A3_PRE_A4_LOCAL_FACADE](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md); no Shell,
Web service or A4 implementation exists. Accepted
A1-A3 milestone contracts, formulas, policies and capture formats remain binding
for current behavior. A conflict requiring runtime change needs a separately
accepted implementation/version transition, not reinterpretation of old captures.
[ARCHITECTURE.md](ARCHITECTURE.md) remains the implementation-layer overview;
the [roadmap](TRADINGINTELLIGENCE_ROADMAP.md) owns delivery sequence and the
[deferral register](TIAF_DEFERRAL_REGISTER.md) owns deferred scope.

Post-A3 pass 2 promotes the companion
[source authority/provenance/contradiction architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md).
Its bounded semantics are implemented by the additive
[pre-A4 foundation](TIAF_POST_A3_PRE_A4_FOUNDATION.md), which changes no frozen
A3 records and does not implement citation UX, source adapters or A4 runtime.

The approved [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md) governs
hosting beneath these logical semantics: local Python first, isolated requests,
filesystem replay and conditional operational boundaries. The local facade
implements that in-process admission/lifecycle slice; no service or speculative
production infrastructure is introduced.

## 1. Purpose and system ownership

The [post-A3 consolidation](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md) owns
the current transition plan: bounded source foundation, narrow local facade,
then deterministic A4. The first two steps are now implemented by the additive
[pre-A4 foundation](TIAF_POST_A3_PRE_A4_FOUNDATION.md) and
[local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md); A4 runtime remains
unimplemented.

TI serves the user's economic interest through risk-adjusted expected utility:
evidence, understandable deterministic computation, bounded interpretation,
later challenged conclusions and measured outcomes. This is an objective, not
a claim of demonstrated profitability. Preserve `WAIT`, `NO_TRADE`, `ABSTAIN`,
conflict and insufficient evidence. No attractive output justifies hiding
uncertainty, fitting the benchmark, inventing probabilities or erasing dissent.

- Scanners discover candidates; manual and external sources may do the same.
- TI supplies attributable intelligence and later advice.
- TradeMonitor owns operational risk authority, position lifecycle and execution
  coordination. TI's risk assessments constrain its advice, not TM's authority.
- The broker remains final truth for live broker state. TI has no order path.

## 2. Logical architecture, not a deployment mandate

```text
TI_SHELL   TI_WEB   scripts   scanners   TradeMonitor   external Agents/apps
    \        |        |         |            |                  /
          curated public capabilities (Python first, transport later)
          trusted invocation admission / bounded runtime composition
                                 |
                            TI_CORE
             evidence / A2 / A3 / replay and audit semantics
             future A4 challenge / A5 positions / A6 expression / A7 learning
                                 |
                  controlled provider/model/storage ports
                                 |
                 replaceable infrastructure adapters

Authorized developer tools --> selected engineering capabilities
                              (not unrestricted private objects)
```

Arrows show logical invocation/dependency boundaries, not processes or HTTP
endpoints. Core-side Agents operate inside the kernel through scoped internal
ports; the external-Agent box is not their mandatory execution route. One
repository and ordinary in-process calls remain appropriate. A capability may
compose several modules; a module may serve several capabilities.

## 3. TI_CORE and its perimeter

TI_CORE is the logical intelligence kernel: provider-neutral domain semantics
and application use cases that create, interpret, validate and preserve TI
evidence and intelligence. It is not a new `ti_core` package or a rename of
`tiaf`. It includes:

- canonical identity, timezone, point-in-time eligibility, factual contracts,
  semantic normalization rules, quality, missingness and provenance;
- deterministic features, indicators, A2 baseline scoring/ranking and its
  component evidence, policy identity and unchanged comparison role;
- A3 specialist contracts/interpretation, workflow policy, structured opportunity
  assembly, controlled research and confirmation semantics;
- replay validation, semantic fingerprints, audit lineage, contradictions,
  confidence basis and usage/cost meaning;
- TI-owned intelligence admissibility and risk policy, and optional authorized
  model reasoning through replaceable gateways;
- later A4/A5/A6/A7 intelligence, only when separately implemented and accepted.

Acquisition use cases and permission/budget rules belong to the controlled TI
application boundary. Vendor field parsing belongs to provider adapters; the
meaning and validation of their canonical output belong to Core. Likewise
workflow policy is Core-side, while LangGraph execution wiring is infrastructure.
Store contracts and integrity rules are Core-side; concrete persistence is an
adapter. Adapters may live next to Core code in this repository without becoming
canonical semantics. No broad package move is required.

Outside Core: CLI grammar, Shell sessions/NLP interaction, Web layout, transport
authentication mechanisms, HTTP/gRPC endpoints, vendor UX/SDKs, infrastructure
secrets, colors, formatting and display preferences, broker execution and TM
lifecycle truth. An accepted analysis horizon/objective or risk constraint is
semantic input, not a disposable UI preference; its effect must be recorded.

## 4. Curated capability boundary

A capability is an intentional consumer operation with typed inputs/results,
defined authority, versioned meaning, usage/failure behavior and replay rules.
Python importability or membership in `__all__` alone does not publish it to
external consumers. Existing documented package APIs remain available to trusted
repository callers; this architecture does not silently withdraw them.

| Interface | Intended consumers and promise |
|---|---|
| Public | Shell, Web, TM, scripts, scanners and approved external Agents/apps. Small stable contract surface, documented compatibility, authorized data access and bounded effects. |
| Engineering | Authorized diagnosis, trace, replay verification, comparison, graph/ledger and normalization inspection. Explicit experimental/versioned status, sanitized projections, no authority bypass. |
| Private | Nodes, reducers, caches, projections, provider SDK objects, mutable registries, calculators' helpers and composition handles. No consumer compatibility promise. |

Public families are evidence/context, deterministic baseline, specialist/company
research and structured opportunity intelligence, plus bounded recorded replay.
They are candidate publication families, not newly available APIs. A3.9 assembly
already supplies a useful captured-input seam. A3.8 live composition needs a
facade that retains service configuration on the trusted side. Verification,
policy comparison and raw lineage inspection default to engineering; a public
replay operation must state whether it reconstructs records or recomputes them.
Future arbitration, position intelligence, option expression and forecasting
remain unavailable until their own milestones. A2 ranking does not imply A3
cross-candidate ranking (DEF-053).

A small reviewed catalog is useful; automatic export/reflection is not.
Descriptors should identify capability ID/version, interface level, request and
result schemas, effects, required authority/data scope, execution modes, replay
support, cost class and availability. Bindings to implementation adapters stay
trusted/private. Discovery is filtered by caller permissions and configuration;
availability never grants permission or guarantees evidence coverage. Provider
capabilities and Agent registries retain their existing distinct jobs.

## 5. Admission, authority and cost

The trusted application/runtime facade resolves caller identity and grants;
callers submit requested scope, not self-authorizing grants. In-process code
shares a trust boundary: Python imports are not a sandbox. Untrusted plugins
must not run in the privileged process; remote isolation/authentication belongs
to later transport work. A developer-mode flag alone grants nothing.

Effective permission is the intersection of caller grant, operation scope,
operator policy, data entitlement, requested scope, profile and model policy.
Budgets cannot exceed any applicable ceiling. The facade validates that request,
reserves aggregate resources and composes existing gateways; gateways continue
enforcing their own limits. Do not create a second conflicting budget ledger.

An invocation records subject, objective, horizon, `as_of`, profile/version,
effective authority reference, approved policy/model constraints, budget,
position-context identity when applicable, request/run/correlation identity and
admitted evidence. Credentials and raw tokens are not canonical fields.
Natural language cannot raise authority. Agents receive capability-scoped tools,
not arbitrary browser, shell, SQL, router or broker handles.

Read-only acquisition may spend quota/money and create audit/cache artifacts;
it is not effect-free. Live access is explicit. No-LLM is a complete supported
mode; the accepted A3.8 path currently requires it. A future profile named DEEP
does not unlock a model or future milestone. Unknown monetary cost is unknown,
not zero; configured cost units are not currency. Original usage, held unknown
usage and replay execution remain distinct and are not double-counted.

## 6. Agents and consumer applications

**Agent = bounded architectural actor. Model = optional replaceable reasoning
engine.** Specialist Agents and future A4 challenge/arbitration Agents are
Core-side. Research Agents may be Core-side when governed evidence use cases
own their work. Interaction Agents belong to Shell/Web applications and only
translate/compose permitted capabilities; external Agents are consumers. Model
choice does not determine an Agent's layer or give it evidence authority.

TI_SHELL is a stateful interactive mediator over the curated boundary. It owns
session context, command interpretation and rendering, not canonical analysis.
Its optional Interaction Agent has the caller's bounded authority. Selected
engineering operations require developer authorization. The small capability
boundary needed by Shell must exist before Shell v0.1; an exhaustive facade and
remote service need not. Primary integration must not shell out to smoke scripts.

TI_WEB calls capabilities directly; it does not call Shell. Shell does not
call Web. TM, scanners and external apps need neither. Scripts can use a Python
facade. Later HTTP/gRPC is another adapter over the same admitted use cases,
not another intelligence implementation. UI parity is not required. “Exhaustive
CLI” means, at most, broad coverage of approved capabilities, never all internals.

## 7. Shared evidence, isolated analysis

### Bounded open-world reasoning

A4 is not permanently closed over the first captured bundle. A model/Agent may
identify a material information gap, formulate a research hypothesis and request
additional evidence through governed capabilities. Model prior knowledge may
motivate that inquiry; it is not canonical factual evidence. An unverified
hypothesis does not need fabricated claim/source IDs and cannot substitute for
an evidence-backed factual premise or upgrade a disposition by itself.
New information becomes decision evidence only after normal acquisition,
provenance, semantic normalization, authority, entitlement, PIT and admission
checks. A4 emits typed needs; the future bridge to A3.8/gateways/MI research owns
controlled acquisition, then a successor projection permits selective challenge.
No direct model tools, source instructions, permission increase or recursive
unbounded loop. Live acquisition after the original cutoff needs a successor
run/new as-of; replay never acquires. Existing A4 limits and A3 no-LLM controls
remain binding; this is architecture support, not delivered model integration.

### Reuse boundaries

**Shared Evidence != Shared Analysis State.** Core validates evidence identity,
source/adapter version, information availability, freshness, PIT eligibility and
quality. The runtime enforces entitlement/security scope before lookup and
return, including cached reads. Evidence reuse also requires compatible semantic
dimensions (timeframe, adjustment convention, period/expiry, mapping and revision).
No symbol-only cross-user cache or future-as-of leakage is permitted by design.

Each invocation retains its own objective, horizon, profile, approved authority,
budget, position context and run identity. Shared acquisition does not share a
mutable plan, opinions or session. Runtime owns reservation/single-flight state;
Core owns analysis meaning and captured lineage; applications own session state;
TM owns live position truth. Results can only be reused under complete semantic
and permission compatibility, with explicit reuse lineage and separate usage.

Existing frozen models/tuple collections do not imply deep-frozen arbitrary
metadata. Admission must defensively validate/copy canonical serialized inputs
before hashing/publication, as A3.9 already does. Captured replay must not fall
back to live acquisition. A checksum proves integrity, not source authenticity,
permission, historical availability or calibrated truth.

## 8. Versions, failures and result meaning

Version identities stay separate: package release (`0.1.0` currently), domain
contract (A0 `1.0`), capability semantics, request/result schema, policy,
provider adapter/normalizer, Shell command grammar and later remote protocol.
Existing child schema/policy versions and hashes are retained. New capability
IDs/versions will be assigned at publication, not retroactively to old records.

Breaking meaning or required-field changes require a new supported version and
explicit migration. Optional additions are compatible only when declared reader
rules permit them; strict readers and closed enums cannot silently accept new
fields/states. Deprecation needs a replacement, notice, supported-version window
and replay strategy; old evidence is not rewritten. Policies are pinned in
captures; policy comparison creates a new record, not an “exact” old replay.

Capabilities should map failures to a small stable caller-facing vocabulary:
`INVALID_REQUEST`, `UNAVAILABLE`, `UNSUPPORTED`, `BUDGET_EXCEEDED`,
`MODEL_DISABLED`, `PERMISSION_DENIED`, `FAILED`, `REPLAY_INTEGRITY_ERROR`.
`PARTIAL`, `STALE` and `INSUFFICIENT_EVIDENCE` may describe usable but limited
results, not necessarily exceptions. `NO_TRADE` is an intelligence state, not a
transport error. Preserve namespaced child codes, source/run refs, safe detail,
retryability and integrity lineage. Do not merge all subsystem enums or expose
unsanitized provider exceptions. Future transport status mappings are separate.

Use small operation-specific request/results with shared typed components,
not one mega-envelope. Preserve applicable canonical state, evidence quality,
gaps, contradictions, reasons, provenance references, replay identity, usage/
cost knowledge, confidence basis and non-action/authority semantics. Rich detail
may be linked, but access-controlled references must remain resolvable for an
authorized audit. Rendering/redaction must not silently change fingerprints or
make a filtered projection look like the full evidence record.

All application datetimes remain aware and normalized with
`zoneinfo.ZoneInfo("Asia/Kolkata")`; naive values are rejected. JSON timestamps
emit `+05:30`. Canonical semantic collections remain immutable tuples with JSON
arrays. Provider-specific tickers/transport syntax do not replace canonical
instrument identity; provider identity remains legitimate provenance.

## 9. Delivery and A4 handoff

Pass 2 has settled source authority, provenance and contradiction semantics.
Its [review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md)
fed the now-approved [A4 challenge/arbitration architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md).
The [pass-3 review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md)
is followed by the completed [deployment review](TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md).
The completed [consolidation](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md)
selects the separate `POST_A3_PRE_A4_FOUNDATION` next, with its
semantic implementation gate still required before A4 runtime. A4 consumes
validated A3.9 intelligence with
references to the complete captured A3.8 bundle, active/superseded specialist
opinions, unchanged A2 assessment/evidence and canonical source/confirmation/
conflict summaries. A3.9 alone is not a substitute for its supporting audit.
Missing full A2 evidence remains explicit; never reconstruct it from a score.

DEF-003 is split into governed local capabilities and later external delivery
without changing its stable ID or claiming implementation. Architecture is
settled before A4; the selected delivery order is foundation, narrow local
facade/lifecycle, then deterministic A4. The facade is
mandatory before Shell v0.1 or untrusted/live external access. It need not block
internal semantic work or force A4 development through HTTP.
A8 retains TM integration and service/remote delivery as required; A10 retains
production operations. Current timing and bounded acceptance criteria are in
the consolidation; the [pass-1 review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md)
retains the original boundary rationale.

No microservices, generic plugin loader, new parallel source registry, universal
dispatcher, event bus, distributed graph/cache or runtime relocation is approved
by this architecture. Add a boundary only when it hides unstable composition or
enforces a real consumer contract.

Later A6 owns construction/validation of trade-expression candidates; A7 owns
forecast generation/calibration and admissible probability evidence. A separately
versioned higher-order comparison may assess A6 candidates against a surviving
thesis and admitted A7 evidence, preserving candidate IDs/assumptions and risk.
It cannot invent a contract, recalculate lower-level facts, fabricate probabilities
or bypass TM. This is not initial A4 contract selection. A5 remains position advice,
TM operational governor and broker execution/state truth. The A7 overlay is a
data dependency for forecast-enhanced A6, not a prerequisite for deterministic
candidate construction or a renumbering of the A5–A10 roadmap.
