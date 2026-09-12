# TI Pluggability Architecture

## Status, authority and boundary

Authoritative cross-cutting architecture, 2026-09-12 (Asia/Kolkata).
Original architecture decision: **READY_FOR_PLUGGABILITY_COMPLIANCE_AUDIT**.

**Current post-R1 status:** the [audit](TIAF_PLUGGABILITY_A1_A5_COMPLIANCE_AUDIT.md)
and [R1 acceptance](TIAF_PLUGGABILITY_R1_ACCEPTANCE_AND_A5_FREEZE_READINESS.md)
are complete. Required scope/explicit absence is implemented; R2–R5 remain pending
pre-A6 and are not A5 freeze blockers. The
[documentation consolidation](TIAF_POST_R1_DOCUMENTATION_CONSOLIDATION_AND_SYNCHRONIZATION.md)
is complete, with final A5 freeze/tag-readiness next. Sections 16–18 retain the
original audit brief/delivery decision, not an instruction to rerun completed R1.
[Monitoring architecture](TIAF_MONITORING_ARCHITECTURE.md) applies these future
composition constraints without implementing a scheduler, new registry or HOT.

Review entry: clean tree at `5d31a9d`, following A5 closure `e19059c`.
A1–A4 remain frozen; A5.1/A5.2 and the A5 closure are accepted, but no
`tiaf-a5-baseline` tag exists at this review. The earlier
[A5 closure decision](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md) remains its
historical runtime finding, not permission to skip the new cross-cutting gate.

This document governs future composition under the
[system architecture](TIAF_SYSTEM_ARCHITECTURE.md) and
[deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md). It promotes selected
ideas from the [pluggability idea cache](TBD_TI_PLUGGABILITY_ARCHITECTURE.md).
It does not implement descriptors, availability resolution, a new manifest,
discovery APIs or plugin loading; nor does it certify current A1–A5 compliance.
Existing contracts, capture formats, policies and runtime behavior remain binding.
Any implementation change requires a separately approved, versioned transition.

## 1. First-order invariant

TI provides a stable baseline that remains valid when optional capabilities are
absent. Compatible capabilities, Agents, intelligence contributors, providers,
policies and adapters compose through explicit contracts and governance without
redesigning unrelated domains.

This preserves authority, provenance, determinism where promised, replay,
explainability, failure isolation, bounded cost, backward compatibility and
baseline comparison. It does not promise a meaningful assessment without its
required evidence: an honest insufficient-evidence result is valid baseline
behavior. Preserve `NO_TRADE`, `WAIT`, `ABSTAIN`, uncertainty and disagreement.
Unavailable or failed intelligence is never a negative market opinion.

Pluggability is not arbitrary code loading, a marketplace, an installation
service, a service mesh, a universal dependency-injection framework or an excuse
to make every component optional. No profitability or improved accuracy is
established by adding a contributor.

## 2. Canonical hierarchy and lifecycle

```text
HOT ⇒ COLD ⇒ STRUCTURAL
```

| Strongest supported level | Guarantee | Change mechanism |
|---|---|---|
| STRUCTURAL | Replacement, omission where permitted, or composition behind stable contracts does not redesign unrelated domains. | Reviewed code/wiring change may be necessary; no configuration or live-switch guarantee. |
| COLD | All STRUCTURAL guarantees plus selection, enablement, disablement, replacement or permitted omission through trusted pre-start configuration. | Validate before startup; changing composition may require restart. |
| HOT | All COLD guarantees plus safe runtime composition transitions. | Versioned activation/quiescence under §14; every HOT component must have the equivalent COLD startup path. |

These are nested guarantees, not three unrelated peer labels. Declare only the
strongest demonstrated level. No HOT exception to the COLD implication is adopted.
An explicit contract boundary, not Python importability, establishes STRUCTURAL.
An inseparable private helper need not receive a pluggability designation.

There is no fourth `STATIC` enum. “Static” is informal shorthand for pinned,
structural-only composition, not another role or availability state. A fixed
implementation without a substitution contract must not be labeled STRUCTURAL
merely to fit the vocabulary. The audit may mark that internal detail not
applicable, or identify a missing boundary where a boundary is actually needed.

Lifecycle transitions are separate from level: a composition is validated,
started, admitting work, draining and stopped. COLD does not permit live
registry mutation. A selection among already pinned provider routes during a
request is routing, not HOT installation or replacement.

## 3. Architectural role and optionality

Use two independent role dimensions, not one overlapping enum:

- Presence requirement: exactly one of `REQUIRED` or `OPTIONAL` in a named
  operation/profile. A request may strengthen OPTIONAL to REQUIRED; it cannot
  weaken a required safety dependency.
- Composition traits: independent `REPLACEABLE` and `COMPOSABLE` flags. A
  required slot can be replaceable but cannot be empty. A composable contributor
  can coexist with compatible peers; this does not imply voting or averaging.

Requirements are scoped. A5 is not necessary for `baseline.assess`, but a
current supported position snapshot and the accepted A4 input are necessary for
the existing position-assessment semantics. The A2 deterministic control path
is REQUIRED in baseline-bearing TI analysis; it is not executed for every
profile lookup, news read, catalog listing or recorded replay. Its accepted
formulas/policy stay pinned. Replacing that benchmark is a comparison/versioning
decision, never transparent substitution.

Illustrative target classifications, not present-code audit findings:

| Component/slot | Level target | Role in the relevant operation |
|---|---|---|
| A2 deterministic benchmark boundary | STRUCTURAL, pinned implementation | REQUIRED; no runtime benchmark selector implied |
| `sector.rotation` contributor | COLD | OPTIONAL + COMPOSABLE |
| Market-data provider slot for a live data requirement | COLD | REQUIRED + REPLACEABLE; optional individual routes |
| Model engine for an optionally enabled reasoning lane | COLD | OPTIONAL + REPLACEABLE globally; required only if that admitted lane specifically needs it |
| A4 arbitration / A5 position policy slot | STRUCTURAL; approved COLD selection target | REQUIRED + REPLACEABLE by compatible operator-approved policy, never absent safety policy |

## 4. Existence, readiness, availability and execution

A static descriptor declares supported semantics. A separate request-scoped
availability snapshot records the evaluation of those declarations. Do not put
mutable health or caller grants inside a static semantic descriptor.

Track each dimension independently with a value, safe reason and scope:

| Dimension | Question |
|---|---|
| Implemented | Does a compatible implementation exist? |
| Installed | Is its reviewed package/build present in this deployment? |
| Registered | Is it bound in the trusted composition? |
| Configured | Are the required trusted settings complete and valid? |
| Enabled | Has the operator enabled this capability for this profile? |
| Authorized | Do caller, operator, entitlement and effect/model constraints intersect permissibly? |
| Data-ready | Do admitted inputs satisfy coverage, freshness, PIT and semantic predicates? |
| Dependency-ready | Are the resolved required dependencies usable? |
| Policy-compatible | Are contracts, policy versions, instruments and execution mode compatible? |
| Healthy | Is the selected implementation operationally fit to attempt work? |

Dimensions may be true, false or unevaluated/unknown; unknown is not true.
Each snapshot binds capability/version, request or discovery scope, composition
identity, evaluation time and safe reason codes. Historical readiness is not
today's readiness. Data readiness concerns evidence, not service uptime.

Effective availability vocabulary for the future contract:

- `AVAILABLE`: all required predicates passed for this scope.
- `DEGRADED`: required predicates passed, but an explicitly permitted optional
  gap or limitation remains and is disclosed.
- `NOT_IMPLEMENTED`, `NOT_INSTALLED`, `NOT_REGISTERED`: distinct absence causes.
- `DISABLED`, `UNCONFIGURED`, `UNAUTHORIZED`, `UNSUPPORTED`: enablement,
  configuration, permission or semantic incompatibility blocks execution.
- `DEPENDENCY_UNAVAILABLE`, `INSUFFICIENT_DATA`: required prerequisite missing.
- `FAILED`: evaluated operational failure/unhealthy implementation.
- `UNKNOWN`: a necessary check remains unevaluated; not runnable assurance.

Retain all applicable reasons. For a single summary use a versioned resolver:
first apply permission-filtered visibility; for visible entries, denied authority
dominates, then absence (implementation/install/registration), disabled,
configuration, semantic support, required dependency, required data, operational
failure, unknown, and finally DEGRADED/AVAILABLE. Evaluate this precedence only
over applicable checks; do not issue live calls to discover lower-priority
reasons after admission is already blocked. Missing optional evidence does not
mask a failed required dependency. Health checks requiring effects are separately
governed, not a side effect of catalog discovery.

Discovery usually lacks request inputs. Return supported modes, known readiness
and explicit unevaluated request predicates, not “all requests will work.”
Admission and artifact access recheck current authority; discovery grants
nothing. Unauthorized inventory may be omitted entirely. A known future ID can
appear as NOT_INSTALLED only in an authorized design/discovery view, never as an
implicitly registered runnable capability.

Execution outcomes are a different axis: succeeded, partial, failed, skipped,
cancelled or not requested, with reasons such as budget/deadline/sufficiency.
An AVAILABLE capability can be skipped or fail on execution. A successful
capability can return bearish evidence, `NO_TRADE` or insufficient evidence.
Do not collapse these distinctions or replace existing subsystem enums; future
facade mappings retain namespaced child codes and require compatible versions.

## 5. Minimum semantic capability descriptor

The future descriptor is a small immutable declaration, not a runtime binding:

| Field group | Minimum meaning |
|---|---|
| Identity | Namespaced capability ID, semantic version and descriptor-schema version; component family and public/engineering/private interface level |
| Role/lifecycle | Scoped presence requirement, replaceable/composable traits, strongest supported level |
| Contracts | Input/output schema IDs and supported versions; subject/horizon/instrument/mode constraints |
| Dependencies | Required and optional capability/contract requirements, compatibility constraints and any request-specific requirement predicate identity |
| Authority/data | Required scopes, entitlements, allowed effects, evidence coverage/freshness/PIT requirements; no credentials |
| Computation | Deterministic or model-backed behavior, permitted modes and replay support; an Agent role is not a model vendor |
| Policy/cost | Compatible policy families/versions, cost class and required accounting/budget dimensions; not a fabricated currency estimate |
| Availability | Identity of the evaluation rule/contract and reference to scoped snapshots, not mutable health in the descriptor |
| Compatibility | Deprecation, replacement ID/version, supported-reader window and explicit migration strategy |

Private trusted bindings resolve descriptors to code. No callable, module path,
provider session, mutable registry, filesystem path or secret is exposed. A
published capability, internal specialist and provider fine-capability remain
distinct namespaces with explicit mappings; do not create one universal registry.

Package `0.1.0`, base contract schema `1.0`, capability semantics, descriptor
schema, composition schema, policy, normalizer, model configuration and transport
versions remain separate concepts. Architecture does not assign a new runtime
schema version. Contracts will retain frozen semantic tuples/JSON arrays and
aware `ZoneInfo("Asia/Kolkata")` timestamps with `+05:30`; reject naive values.
Safe extensible metadata is not a hidden policy/authority channel or assumed
deeply immutable. Validate/copy admitted canonical content before fingerprinting.

## 6. Dependency resolution and request-specific requirements

Resolve reviewed declarations into a bounded acyclic graph before effects.
Required edges block dependent execution if unresolved, unauthorized, disabled,
incompatible or insufficient. Optional edges permit omission only under the
declared valid reduced contract, with explicit gaps. A missing optional dependency
need not degrade a request to which it is irrelevant; record non-applicability.

Resolve compatibility constraints to exact identities/versions, detect duplicate
or ambiguous bindings and cycles, and capture the resolution. A cycle in the
required baseline prevents startup/admission. An invalid optional subgraph can
be quarantined with a disclosed reason if baseline integrity is independent.
Optional dependency requests never auto-install packages, widen authority, or
trigger unbounded recursive work.

A globally optional capability becomes mandatory when the admitted request or
governance policy requires it. Cash-equity analysis may omit derivatives;
option-spread analysis cannot claim completion without its required derivative
contracts/evidence. This example does not implement option spreads or override
A5's current rejection of multi-leg shape. Required absence yields explicit
insufficient-capability/fail-closed behavior, not an answer to a weaker question.

For future Sector Rotation, `sector.membership` and `market.price` are required;
`institutional.flows` and `analyst.revisions` can be optional only under a policy
that defines the reduced evidence meaning. Optional does not mean impute zero.

## 7. Peer intelligence composition

Opportunity Intelligence, Sector Rotation, Signal Qualification, Market Regime,
Relative Leadership and Forecast Evidence can be peer contributors where there
is no genuine dependency. These are conceptual examples, not new public APIs.

```text
immutable admitted context + unchanged baseline
                   ↓
      compatible peer contributions
                   ↓
  typed collection + gaps + conflicts + lineage
                   ↓
  versioned higher-order reasoning / arbitration
```

The minimum peer contribution contract identifies contributor/capability/version,
input and baseline fingerprints, subject/objective/horizon/as-of, semantic axes
and units, typed output schema/reference/digest, cited claims and provenance,
limitations/uncertainty/conflicts, execution status, policy, usage and run ID.
Reuse child contracts rather than converting every output to a universal score
or a giant untyped payload. Contributions cannot rewrite inputs or each other.

Use dependency-topological scheduling; independent peers have no meaning-bearing
execution order. Stable identifier order makes serialization reproducible,
not a priority rule. Serial and concurrent engines must preserve the same
admitted set, selection decisions and canonical aggregation under the promised
deterministic mode. Where deadlines/budgets or data dependencies affect selection,
record the policy order and actual set; different sets are not exact-equivalent
runs. Sequential execution alone does not establish a semantic dependency.

Compare only compatible propositions, horizons, units, cutoffs and source bases
under the [source semantics](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md).
Retain contradictory contributions; correlated source reuse is not independent
confirmation. Non-comparable outputs stay non-comparable, not disagreement or
neutral votes. Missing peers have typed absence/status, no synthetic stance.
Only an admitted, versioned downstream policy may interpret conflicts or change
a successor conclusion. Composition itself does not decide BUY/SELL, targets,
probabilities, final A4 disposition or A5 advice.

If a future qualifier explicitly consumes Sector Rotation, add that real
dependency to the qualifier's request graph; do not force unrelated peers into
`A → B → C → D`. No A4/A5 inputs are extended in this pass.

## 8. Stable baseline and enrichment lineage

Preserve the original A2 assessment, component evidence, policy, scores/classes,
`NO_TRADE` and fingerprint byte-for-byte/semantically according to its accepted
capture rules. No reweighting to make enriched examples look attractive.
For a baseline-bearing result retain:

- baseline run/capture and assessment identity, input fingerprint and policy;
- parent enriched run(s), capability/policy changes and admitted evidence deltas;
- contributor input/output identities, conflicts, missingness and participation;
- higher-order composition policy, result fingerprint and comparison scope.

“Baseline” in a comparison must name its control: A2 itself, or a pinned
deterministic A3/A4/A5 path supported by that A2 evidence. Never silently switch
the control between runs. A2 is not recalculated by a contributor. If no complete
A2 evidence was captured, disclose partial comparison/verification rather than
reconstructing evidence from a score.

Run A (baseline), B (baseline + Sector Rotation), and C (baseline with Sector
Rotation and Forecast Evidence) retain separate records and a common control/input-cutoff
where comparable. If new evidence changes that information set, label a
successor run and disclose the confound; do not attribute every delta to a
plugin. A7 can later evaluate incremental coverage, outcomes and cost against
this lineage; observational differences alone prove no causal economic benefit.

## 9. Composition manifest and fingerprints

Design a versioned immutable semantic manifest as an additive parent of existing
captures, not a rewrite of A1–A5 child records. This is not a storage/transport
selection. Capture the relevant dependency closure, not an unrestricted machine
inventory or secrets. Resolve referenced content for authorized offline replay.

| Content | Required meaning |
|---|---|
| Request/control | Request semantic digest, objective/horizon/as-of, execution mode and baseline references/digests |
| Membership | Requested, eligible, selected, attempted and used capabilities; disabled, unavailable, failed and skipped entries with reason/status records |
| Pinning | Exact capability/implementation/descriptor, policy, provider/normalizer and model/configuration identities where applicable |
| Resolution | Required/optional dependency graph, request requirement overrides, exact binding choices and compatibility decisions |
| Availability | Scoped admission snapshots, unevaluated predicates, relevant transitions, failures and partial-data conditions |
| Contributions | Input/output and evidence digests, provenance, active/superseded results, gaps, conflicts and successor references |
| Governance/cost | Safe effective-authority reference, budget ceilings, selection/stop decisions, child attempt/usage references and cost knowledge |
| Identity | Manifest schema, canonicalization/fingerprint policy, composition fingerprint, run semantic fingerprint and exact capture checksum |

Membership lists are projections, not a disjoint partition. Requested can
overlap eligible and used. “Used” means admitted into the result, not merely
called. An optional successful output may be unused; a failed attempt followed
by permitted fallback retains both attempts. Every selected capability has a
terminal disposition or explicit incomplete/unknown outcome. Skipped records
explain cost, deadline, sufficiency, non-applicability or policy denial.

Define two distinct hashes: the **composition fingerprint** binds the resolved
descriptor/dependency/policy set, request-specific requirements and selection
policy before dispatch; the **run semantic fingerprint** additionally binds the
admitted input/baseline, availability affecting execution, actual participation,
failures, outputs, provenance and meaningful usage/stop decisions. Same
composition can produce different runs. Unknown cost/status remains semantic
unknown, not zero. This distinction prevents a failed and successful run from
being mislabeled equivalent merely because they share installed components.

Canonicalization must sort true sets by stable identity, retain meaningful
policy/attempt order, normalize typed values and hash transitively referenced
semantic identities. Exact bytes/checksums also preserve serialization and
operational timing. Pure logging/write time or elapsed measurement may be
excluded from semantic hashes under an explicit versioned rule; evidence time,
as-of, deadline and budget consequences may not. No new algorithm replaces
existing child hash exclusions. No credentials or unrestricted grants enter a
fingerprint input; use safe immutable authority/configuration identities.

Legacy captures retain their original supported replay guarantees. Absence of a
new manifest means composition completeness is unknown under this new design,
not historical evidence that an optional capability did not exist. A derived
legacy wrapper must name derivation/version and limitations; never invent a
complete manifest from today's installation.

## 10. Replay and comparisons

| Mode | Meaning / preservation |
|---|---|
| Exact recorded replay | Integrity-check and reconstruct the original captured records/manifest. No provider/model calls, no new optional components, no historical recomputation claim. |
| Semantic verification replay | Recompute only supported deterministic parts with pinned compatible code, contracts, policies, composition and captured inputs; compare under named semantic hashes. Capture bytes/timings need not match. |
| Policy comparison | New run changes a declared approved policy, preserves original input/control and records both policies and outputs; never relabel as exact replay. |
| Capability comparison | New run changes a declared compatible capability set/implementation, preserves comparable input/control and records additions/removals plus confounds; not historical replay. |

Recorded model output is replay evidence; another model call is neither required
nor permitted during offline replay. Unavailable pinned code may still allow
recorded reconstruction, but not a deterministic verification claim. Unsupported
schema, missing artifact, corruption or incomplete legacy lineage produces an
explicit limitation/error, not live repair. Current access rights still gate
reads; historical authorization is not a present-day grant.

Offline comparison can use only captured admissible data. Additional live
acquisition creates a successor with its own cutoff/usage and cannot silently
backfill historical truth (DEF-049). Original-run consumption, replay execution
and comparison consumption remain separately attributable. No distributed
replay farm or persistent database is introduced (DEF-050).

## 11. Failure isolation and authority

| Situation | Required behavior |
|---|---|
| Optional peer absent/disabled | Run the valid baseline; disclose absence and omit the peer's opinion. |
| Optional peer fails or times out | Preserve attempt/failure/uncertain usage; continue or return a permitted partial result without that contribution. |
| Required capability/dependency absent | Do not claim the requested operation completed. Return insufficient capability, abstention or a typed operation failure as its existing contract allows. |
| Required facts stale/insufficient | Preserve evidence quality and domain-specific non-action result; no invented facts or positive fallback conclusion. |
| Authority, integrity or unsupported mandatory semantics fail | Fail closed for the affected request/artifact; quarantine unsafe optional output only if baseline integrity remains provable. |
| Baseline itself invalid/fails | Typed failure or the existing valid insufficient-evidence contract; never manufacture a baseline score or disguise an exception as NO_TRADE. |

Failure isolation here is semantic/request isolation, not a claim that a Python
exception boundary survives process death or hostile code. Hard crash/termination
isolation needs justified deployment work. No arbitrary retries; late work
cannot publish into finalized results. Existing domain safety rules dominate:
optional absence cannot make mandatory source/position truth irrelevant.

Trusted composition chooses reviewed bindings from an explicit allowlist.
Reject caller-selected module paths, unrestricted entrypoint scanning, untrusted
package discovery, `eval`/`exec`, dynamic installation and arbitrary tool access.
Same-process Python is not a sandbox; untrusted code cannot run inside the
privileged TI host under the label “plugin.”

Installing or enabling a capability grants no data/model entitlement, engineering
privilege, broker permission, filesystem or network authority. Admission
intersects caller/operator/profile/effect/data/model constraints and budgets;
gateways enforce their own scoped bounds. Discovery, caches, artifacts and
replay recheck appropriate access. Policy selection is operator-controlled;
consumer preferences may select only already admitted options, never inject or
weaken governance policy. Preserve TI intelligence, TM governance and broker
execution truth. No execution operation is added.

## 12. Cost-aware bounded composition

AVAILABLE does not imply RUN. Reuse the Planner's bounded selection and existing
gateway/accounting ownership: baseline → inspect material gaps → select useful
eligible capabilities → collect admitted contributions → stop when sufficient.
Do not create a second planner, routing policy or competing budget ledger.

Versioned selection considers materiality, evidence sufficiency, expected
information value, provider/model usage, latency and deadline. Expected value
of information is a disclosed heuristic unless calibrated; it is not a trading
probability. Reserve against applicable ceilings before effects, account for
fallback/retries/shared evidence once by attempt lineage, and bound rounds,
fan-out, calls/tokens and time. Aggregate parent and child usage without double
counting. Unknown monetary prices/held work remain UNKNOWN, not zero or strict
currency-cap compliance (DEF-055). No-LLM paths retain zero model calls/tokens/
cost. A timeout stops further dispatch but does not prove external cancellation.

## 13. Component-family expectations and discovery

These are design targets, not claims that every existing component is COLD:

| Family | Boundary / default target | Constraints |
|---|---|---|
| Evidence/data providers | STRUCTURAL canonical contracts; COLD reviewed adapter/route configuration | Provider suffixes/transports local; source provenance, units, PIT and ambiguity survive substitution. A1 Dhan routes and A3 MI routes remain distinct. |
| Specialist Agents | STRUCTURAL bounded actor; COLD optional compatible registrations | Purpose, allowed capabilities, evidence contract, authority, budget, policy and version; absence explicit. No direct provider transport. |
| Higher-order Agents | STRUCTURAL; COLD optional challenge implementations | Required arbitration/safety role cannot vanish. No bypass of A4 policy or implicit model activation. |
| Model engines | STRUCTURAL reasoning gateway; COLD by default | No model, OpenAI, Anthropic, local or later engine are conceptual choices, not newly supported adapters. Model substitution never redefines domain meaning or grants authority. |
| Intelligence capabilities | STRUCTURAL; COLD optional contributors | Typed peer composition; current required operation semantics retained. |
| Feature families | STRUCTURAL; COLD only for independently supported optional families | Required A2 inputs/formulas pinned; omission never silently renormalizes the benchmark. |
| Policies | STRUCTURAL semantic components; COLD only among reviewed compatible versions | A4/A5, ranking, monitoring and future sector/qualification policy identities captured. Some accepted runtimes intentionally support one policy only. |
| Workflow adapters | STRUCTURAL; COLD trusted serial/reference or supported LangGraph binding | Framework stays outside domain contracts; parity for the promised execution/input set. No new intelligence priority. |
| Consumers/interfaces | STRUCTURAL facade clients; COLD host-selected Shell/Python adapters | Shell is optional to Core; no dynamic command export. Remote APIs require separate transport approval. |

Agent role is not model provider. Optional model absence must preserve already
promised deterministic operation, including the accepted no-LLM orchestration
path. Installing a model does not automatically replace a specialist.

The existing [local facade catalog](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) is the
natural public discovery seam. Future Shell, Python and remote consumers can
read permission-filtered descriptor/availability projections there; internal
provider and Agent registries retain their jobs. Current catalog behavior and
its eight capabilities are unchanged. Future examples such as `sector.rotation`
NOT_INSTALLED, `signal.qualify` DISABLED or `forecast.return` DEGRADED are not
claims about today's published API. A discovered capability need not have a
Shell grammar/rendering adapter; unsupported versions fail safely, never become
generic function dispatch.

## 14. HOT safety policy

COLD is the default target for most TI intelligence modules unless HOT has
demonstrated operational value. No family is approved for HOT implementation
in this pass. Provider fallback between startup-pinned routes does not justify
HOT registry mutation. Track true HOT composition separately in DEF-057.

A future HOT proposal must prove all of the following before claiming HOT:

1. Equivalent COLD startup selection, compatibility validation and authority.
2. Staged registration/validation/health qualification; atomic activation of a
   new immutable composition generation, with admission bound to one generation.
3. Existing requests remain pinned to the old generation through completion;
   new requests use the admitted new generation. No mid-run implementation swap.
4. Quiescence stops new admissions to the retiring generation, tracks all active
   references and bounds drain. A timeout does not prove safe unload.
5. Explicit ownership for adapter resources, caches, sessions, reservations and
   state; version/entitlement-compatible reuse only, no shared mutable analysis.
6. Safe retirement after references settle; if unload cannot be proved safe,
   retain the generation or require restart, never claim in-place unload success.
7. Versioned state migration where applicable, failure quarantine, health
   transitions and rollback to an available compatible generation for new work.
   Rollback cannot erase results, undo calls/cost or assume lost grants return.
8. Captured generation/composition identity and availability transitions,
   supported old replay readers, rollback tests and bounded resource retention.

Operational value, concurrency ownership and recovery proof belong to a later
bounded proposal under deployment rules; no service mesh/queue is prerequisite
merely to satisfy this document.

## 15. Future conformance thought experiments

### Sector Rotation

Without installation, an otherwise valid baseline works and records absence.
Cold installation alone is insufficient: trusted registration/configuration,
enablement, compatible policy, caller authority, required membership/price data
and healthy dependencies must pass to yield AVAILABLE (or explicitly permitted
DEGRADED). Compatible consumers may select it when useful within budget.
Disabled or failed optional Sector Rotation leaves baseline usable with no
invented sector stance. A request explicitly requiring it cannot silently fall
back to ordinary baseline as if complete. Replay of the pre-installation run
does not acquire the new contributor. Existing A3.6 sector context is not this
future Sector Rotation capability. No A4/A5 redesign or sector implementation.

### Signal Qualification

Without `signal.qualify`, a candidate follows its accepted baseline path; absence
does not label a signal false or safe. With a separately accepted cold-pluggable
qualifier, output cites candidate/input/control identities, evidence and policy.
Optional sector/derivatives/forecast/ML meta-label dependencies may be absent
under a declared reduced contract; mandatory request predicates still block.
It may consume a genuine peer dependency without forcing all peers into a chain.
Disabled/failed qualification is not a rejection prediction. No invented
confidence/probability, automatic threshold, model, trading action or false-signal
guarantee follows. The
[Signal Qualification idea cache](TBD_TI_SIGNAL_QUALIFICATION_FALSE_SIGNAL_SUPPRESSION_ARCHITECTURE.md)
remains wholly non-authoritative as a capability design; only this pluggability
thought experiment is adopted.

## 16. Compatibility review and next audit requirements

This is a conceptual document-to-document compatibility review, not a detailed
A1–A5 source/test compliance audit. The following are inspection questions, not
certified defects or instructions to refactor now:

| Existing architecture/seam | Compatibility and tension to inspect next |
|---|---|
| System boundary / deployment | Trusted in-process composition and no generic loader align. Check frozen startup ownership and prevent claims that ordinary private helpers are plugins. |
| Local facade/catalog | Curated static descriptors, filtered discovery and grants align. Inspect mapping to scoped readiness/dependencies and legacy strict-reader compatibility; do not assume all optional slots are configurable today. |
| A1 data contracts / A3 provider fabric | Neutral adapters and per-capability routing align. Check optional SDK import isolation, separate route domains, provider semantics/PIT and selection capture; MI fallback is not proof of A1 fallback or HOT support. |
| Agent framework/registry | Bounded role versus model distinction aligns. Inspect closed specialist identities, registry freeze/duplicates, required evidence and absent specialist behavior without changing accepted enums by fiat. |
| A2 feature/baseline | Stable benchmark aligns. Distinguish required control inputs from truly optional feature families; determine whether any proposed omission would silently change scoring. |
| A3 Planner/workflow adapters | Existing plans, dependency policy, skips, budget ledger and captures are natural owners. Inspect hidden peer ordering, missing-agent handling and serial/LangGraph parity; avoid parallel composition machinery. |
| A4 Challenger/Arbitrator | Optional model challenge and required deterministic arbitration align. Inspect how future typed peers could be admitted without bypassing source semantics or changing closed accepted projections. |
| A5 Position Intelligence | Required snapshot/A4, non-action behavior, policy pins and replay align. Optional future sector/forecast presence must not weaken position truth or alter single-position semantics. |
| A3.10/A4/A5 replay | Existing layered captures/checksums and comparisons align. Inspect manifest coverage, transitive pins, legacy limitations and captured failures without rewriting child fingerprints. |
| TI_SHELL | Consumer-only command grammar aligns. Inspect how future discovery expresses absence without promising commands or exposing privileged bindings. |

The separate audit must inventory A1 data/runtime, A2 features/baseline, A3
Agents/gateways/provider fabric/planner, A4, A5, policy, replay, facade and Shell.
For every relevant boundary record actual contracts, consumers, code/test
anchors, strongest demonstrated level, scoped requirement/traits, coupling,
absence/failure behavior, authority, usage and capture coverage. Do not demand
optional omission of a genuinely required safety dependency.

Keep audit axes separate: compliance verdict (`COMPLIANT`,
`PARTIALLY_COMPLIANT`, `NON_COMPLIANT`, `NOT_APPLICABLE`); dependency finding
(`HARD_DEPENDENCY` where evidenced); and disposition (`MUST_REMAIN_REQUIRED`,
`SHOULD_BECOME_OPTIONAL` where justified, no change, or bounded remediation).
A hard dependency may be correct and compliant. The TBD's mixed classification
list is not adopted as one mutually exclusive enum.

The audit must specify later acceptance coverage for:

- baseline-only and optional absent/disabled/import-unavailable compositions;
- authorized/denied/unknown-readiness, incompatible versions and cyclic graphs;
- optional failure/timeout versus required failure, with unchanged baseline;
- peer order invariance where promised, conflicts and non-comparable evidence;
- no-LLM operation, bounded nested usage, unknown cost and skipped-work reasons;
- manifest reconstruction, mutation detection, legacy reads and no live replay;
- baseline/enriched/policy/capability comparisons and installation-after-capture;
- facade/Shell filtered discovery, grant revocation and private binding isolation.

Report gaps with risk, narrow remediation and acceptance evidence required;
distinguish an A5 freeze blocker from a future optional-module prerequisite and
from deliberately deferred HOT/remote operations. No component compliance
verdict, regression result or remediation implementation is claimed in this pass.

## 17. Delivery sequence and decision

P0 architecture is complete with **READY_FOR_PLUGGABILITY_COMPLIANCE_AUDIT**.
Next is P1 A1–A5 compliance audit; P2 is only approved bounded remediation
proved necessary by that audit; P3 is regression/composition/replay acceptance
of those changes, if any. Revisit A5 freeze readiness explicitly after the audit
and any required remediation. This is a cross-cutting workstream, not A5.x or A6.

Deferred: concrete descriptor/manifest schemas and migration/code changes until
audit; HOT engineering until demonstrated need (DEF-057); production model
integration (DEF-052); remote discovery/transport (DEF-003); monetary pricing
(DEF-055); distributed persistence/monitoring under existing deferrals. Sector
Rotation and Signal Qualification require separate architecture and acceptance.

Exact next Codex prompt title:

**TI PLUGGABILITY — A1–A5 COMPLIANCE AUDIT**

No runtime code, API behavior, A5 policy, provider/model integration, scheduler,
remote transport or A6 work is introduced. No commit, tag or push is performed.

## 18. Documentation validation

This architecture pass changes 14 Markdown files only (one new, 13 modified).
Validation: `git diff --check` passed; the new document's whitespace check
passed; 101 README/docs Markdown files yielded 621 relative file-link targets
with zero missing files. The register contains 57 unique IDs with 44 DEFERRED,
4 PLANNED, 4 IMPLEMENTED, 3 REJECTED and 2 SUPERSEDED records. No dedicated
documentation tests were found by filename/content search. Runtime tests were
not rerun for this documentation-only pass; no new runtime acceptance or
A1–A5 compliance test result is claimed.
