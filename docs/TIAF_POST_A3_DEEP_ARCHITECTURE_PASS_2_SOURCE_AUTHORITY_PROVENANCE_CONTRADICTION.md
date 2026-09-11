# Post-A3 Deep Architecture Pass 2 — Source Authority / Provenance / Contradiction

## 1. Decision, baseline and scope

**Decision: `READY_FOR_DEEP_ARCH_PASS_3`.**

The semantic design is approved with bounded, additive implementation work
required **before A4 runtime implementation**, not before its architecture pass.
[TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md)
is promoted as the authoritative semantic companion to the system architecture.
It does not assert that the proposed projection/contracts already exist.

Review date: **2026-09-11, Asia/Kolkata**. HEAD remains
`e690da2ce0a1dc0d3eb263c3b9e8e59ad52b6212` / `tiaf-a3-baseline`.
The worktree already contained the nine pass-1 documentation changes plus a
user-created `TBD_TI_DEPLOYMENT_ARCHITECTURE.md`. Those changes were preserved;
the deployment note and pass-1 review were not edited. No source, script, test,
dependency, credential or configuration changes were made. A4, Shell and new
website/media/model-research adapters remain unimplemented by this pass.

The attached brief is the requested work scope. Repository contracts and
accepted records establish current implementation facts; TBD proposals do not.

## 2. Documents and code reviewed

Reviewed authoritative design/status material:

- [System architecture](TIAF_SYSTEM_ARCHITECTURE.md) and
  [pass 1](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md).
- [A3 architecture](TIAF_A3_ARCHITECTURE.md),
  [A3.5 events](TIAF_A3_5_NEWS_EVENT_INTELLIGENCE.md),
  [A3.6.1 provider fabric](TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md),
  [A3.6.2 integration](TIAF_A3_6_2_MARKET_INTELLIGENCE_DEEP_RESEARCH_INTEGRATION.md)
  and [confirmation gateway](TIAF_AUTHORITATIVE_CONFIRMATION_GATEWAY.md).
- [A3.8 orchestration](TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md),
  [A3.9 intelligence](TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md),
  [A3.10 replay](TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md)
  and [A3 closure](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md).
- [Deferrals](TIAF_DEFERRAL_REGISTER.md),
  [capabilities](TIAF_CAPABILITY_MAP.md) and
  [implementation targets](TIAF_IMPLEMENTATION_TARGETS.md).

The [source-fabric TBD](TBD_TI_SOURCE_PROVENANCE_CITATION_FABRIC.md) was read
section-by-section. System/Shell hypotheses informed the consumer boundary;
the deployment TBD was inspected only for source-reuse, authority and persistence
implications, not promoted or edited. Pass 1's logical boundary remains binding.

Code inspection followed original claim/citation IDs through event/native
observations, normalizers, canonical evidence, contradiction detection, document
confirmation, sparse graph/research, A3.9 locators and A3.10 capture/replay.
This review is not a new provider certification or full live/production audit.

## 3. Existing substrate and specific gaps

| Evidence anchor | Current behavior | Consequence for future A4 |
|---|---|---|
| [Agent evidence](../src/tiaf/agents/evidence.py) | EvidenceClaim has mandatory cited evidence, kind, statement, as-of, quality/freshness; EvidenceCitation has role/locator. | Good occurrence lineage; not a universal typed proposition key. Do not infer comparability by parsing statements. |
| [Event contracts](../src/tiaf/events/models.py), [dedupe](../src/tiaf/events/dedupe.py), [revision handling](../src/tiaf/events/normalization.py) | Publisher/provider/source/document identities, strict structured facts, timestamps, exact/conservative clusters and explicit revisions; retains active/superseded IDs. | Reuse immutable records. Clustering a shared event is not independence or agreement; scope/temporal comparison needs an explicit projection. |
| [MI models](../src/tiaf/market_intelligence/models.py), [normalization](../src/tiaf/market_intelligence/normalization.py) | Native observations retain adapter/endpoint/tool, source refs, availability basis, derivation and lineage. Only EXACT/WELL_SUPPORTED mappings emit canonical projections. | Preserve ambiguous/provider-defined records without promoting them. Canonical projection alone may lack the full statement basis; resolve original typed context or mark unknown. |
| [MI routing](../src/tiaf/market_intelligence/routing.py), `_find_contradictions` | Groups emitted records by metric and native period, compares native values, excludes explicit linked derivations and requires distinct providers. | Candidate discrepancy detector, not full same-proposition proof. Unit/basis/scope, same-provider conflicts and transitive origin relationships need A4 comparison rules. Local variable `independent` is not demonstrated source independence. |
| [Authority enums](../src/tiaf/market_intelligence/enums.py), route eligibility and gateway `_strongest_authority` | Coarse source ordering is used for route constraints and strongest-class result summary. | Preserve recorded policy. It must not become A4's universal authority ordering or adjudicate field truth. |
| [Official document/confirmation contracts](../src/tiaf/market_intelligence/authoritative_models.py) | Validated domains, content hashes, parser identities, revision refs, document period/basis, matching facts and discrepancies. | Strong starting lineage; source metadata lacks a general per-field authority scope/independence contract. Authenticity and domain validation are not universal truth guarantees. |
| [Confirmation execution](../src/tiaf/market_intelligence/authoritative.py), `execute` | Builds one field entry per ID from documents and one canonical entry per metric; compares field values for equality. Later entries can replace earlier entries in those lookup maps. | A4 must inspect all captured documents and verify scope/units/basis and competing values. A legacy CONFIRMED result is not sufficient proof of scoped confirmation. No last-write-wins preference is approved. |
| Same gateway, `_classify` | A mix of confirmed fields and discrepancies yields PARTIALLY_CONFIRMED; discrepancies may include actual opposing values. | Preserve field details, not just aggregate status/reason labels. A partial result is not simply "some fields missing." |
| [Research contracts](../src/tiaf/market_intelligence/research.py), [deep research](../src/tiaf/market_intelligence/deep_research.py) | FACT/INFERENCE/HYPOTHESIS and lineage rules, derivation retained, normalized context with ambiguity/gaps, no provider payload in reasoning context. | Retain these axes; add projected claim role/mapping status rather than invent a new universal epistemic hierarchy. |
| [Sparse graph](../src/tiaf/market_intelligence/graph.py) and GraphRelation enums | Versioned material company/context edges with evidence/PIT provenance. Not a universal document/claim/source-origin graph. | Reuse references and flat semantic relations. Do not claim current graph enums already support SAME_ROOT or CORRECTS; no second graph/database. |
| [A3.9 contracts](../src/tiaf/service/opportunity_intelligence/contracts.py) | Typed reasons/SourceLocator, five summary contradiction kinds and LineageGroup independence fixed to UNKNOWN. | Preserve original summary and unknown; add a deterministic A4 input projection over resolvable captures, not fields in frozen A3.9. |
| [A3.10 package](../src/tiaf/a3_hardening/package.py), [replay](../src/tiaf/a3_hardening/replay.py) | Immutable captured A2/A3.8/A3.9 artifacts, exact/semantic fingerprints, recorded replay and selected deterministic verification/comparison. | Reuse capture pattern; future A4 parent pins new semantic policies/relations without altering the A3 package or pretending old captures contain later knowledge. |

These are concrete limits of using accepted A3 as a **general A4 source-arbitration
input**, not a claim that this pass tested/fixed new live failures. The bounded
A3 behavior is preserved. Before A4 reliance, the narrow projection must refuse
unjustified comparison/confirmation instead of treating existing labels as proof.

## 4. Approved semantic decisions

The normative detail is in the promoted architecture; this is the decision summary.

| Concern | Decision |
|---|---|
| Source identity | Separate publisher/issuer/speaker, distribution venue, provider/adapter, upstream root, document family/version and evidence occurrence. Preserve locators, hashes and original IDs. Unknown is explicit, not a shared synthetic root. |
| Authority | Claim/field/domain/subject/time-scoped applicability with captured basis, role, authenticity and policy/version. No global total order, source-brand shortcut or implication of invocation permission. |
| Claim identity | Proposition key excludes opposing value/provider/acquisition identity; assertion identity retains them. Subject, predicate, basis, scope, period/effective time, units and forecast/actual role determine comparability. |
| Comparability | EXACT, COMPARABLE_WITH_TRANSFORM, NOT_COMPARABLE or UNDETERMINED; explicit conversions only, unknown is never wildcard. No tuned numeric tolerance. |
| Dispute taxonomy | Factual conflict, semantic mismatch, temporal difference, scope mismatch, interpretive disagreement, cross-domain tension, forecast disagreement and confirmation discrepancy. Missingness is a gap. |
| Lifecycle | Append-only detected/review/conflict/unresolved/not-comparable states, evidence-backed scope/revision/field-authority resolutions and linked supersession. No resolution deletes claims or retroactively rewrites history. |
| Independence | SAME_ROOT, directed DERIVED_FROM, LIKELY_DEPENDENT, justified INDEPENDENT or UNKNOWN, scoped to publication/measurement/analysis dimension. Provider count is not corroboration. |
| Revisions | Document/field-scoped correction/restatement/clarification/supersession with explicit lineage. Changed webpage bytes alone do not prove correction; current and historical views can legitimately differ. |
| Epistemic status | Keep FACT/INFERENCE/HYPOTHESIS and separate derivation. Add a projected attributed-statement/forecast/metric/interpretation role and mapping status; preserve original enums. |
| Confirmation | Recorded gateway status plus a distinct field-level A4 admission/comparability view. Document existence != field confirmation; NOT_FOUND != FALSE; confirmed fact != confirmed thesis. |
| Materiality | Request/horizon/risk-sensitive attention and bounded escalation, not probability or trust. Unknown magnitude/basis remains unknown; budgets may leave a material dispute unresolved. |
| Quality | Authority, authenticity, quality, freshness, relevance, independence, directness and completeness remain separate. |

## 5. Minimal A4 bundle, A3 compatibility and replay

Recommend `A4SemanticInputProjection` as a design role, built deterministically
from validated A3.9 plus its captured A3.8/A3.10 substrate. It composes:

1. subject/objective/horizon/as-of, projection creation time, run identity,
   approved authority/budget/profile and schema/policy identities;
2. unchanged A3.9 result and complete resolvable capture refs, including active/
   superseded opinions and full-versus-projection A2 identity;
3. typed claim/evidence/source/document indexes with semantic mapping and
   authority/independence metadata;
4. field-level confirmation, revision and dispute records and lifecycle snapshot;
5. missing/partial/stale evidence and excluded-evidence reasons, usage/cost
   knowledge and integrity/semantic fingerprints.

References are preferred to copying every artifact. A4 receives no arbitrary
native provider payload, router, parser, credentials or source-URL execution
handle. Unresolvable required identity/integrity fails admission; optional missing
scope/lineage produces qualified gaps and blocks only unsupported claims.

This lets A4 challenge same-label semantic errors, false independence, stale
theses and unsupported inferences, and request authorized bounded confirmation
for material disputes. It does not define challenger roles, a winner algorithm,
recommendation actions, calibrated probabilities or model prompts.

A3.9 keeps its original IDs, states, reasons and hashes; projected classifications
are separately attributable, not corrections to history. A3.10's existing schema
does not gain fields in place. A future A4 parent capture pins the projection,
source policies, independence assumptions, contradiction/confirmation states and
eligible revisions alongside the unchanged A3 package. A policy comparison is a
new record; later source discoveries cannot appear in original replay. Missing
retained content is a verification limitation, never a trigger to fetch it live.

## 6. Model and citation boundaries

Future models may cite only admitted, resolvable evidence and structured
provenance. They may challenge or propose hypotheses with premises, but may not
invent sources, infer independence from brands, resolve conflict by intuition,
upgrade self-confidence to authority or execute instructions inside source text.
Reject unsupported claim IDs; preserve opposing evidence and unknowns. Scoped
authoritative field evidence can be challenged only with explicit relevant
counter-evidence/limitation and governed review, not prestige or prose. No grants
increase through a model or natural-language request. DEF-052 remains deferred.

DEF-054 remains **user-facing explanation/citation/report rendering**, separate
from Core's new semantic foundation. Numbering, hyperlinks, bibliography,
compression, source labels, media-link display and CLI/Web layouts can wait.
Core supplies source/document/field locators so future rendering does not require
re-research. Redaction/filtering must be explicit and cannot pass a partial view
off as the original full capture.

Reword DEF-054 to clarify this dependency split, but do not create a new deferral
ID: the immediate pre-A4 semantic projection is planned prerequisite work, not a
new deferred A3 deliverable. Keep all 55 IDs/status totals unchanged. Existing
official-source/provider registries are reused; no new generic registry or
source-scoring subsystem is justified.

## 7. Source-fabric TBD section dispositions

Every numbered section is covered. PROMOTE means the **revised principle** is
adopted in the companion document, not that the whole original section or its
proposed API names become implemented authority.

| Original section(s) | Disposition | Exact boundary |
|---|---|---|
| 1 — purpose | `REVISE` | Split A4 semantic trust from report presentation; source list is possible coverage, not delivered integrations. |
| 2 — traceability invariant | `PROMOTE_TO_CORE_ARCHITECTURE` | Every material claim and inference premise keeps attributable evidence/lineage. |
| 3 — why defer | `SUPERSEDE` | A3 is frozen; retain as historical rationale, replace current sequence with passes 2/3. |
| 4 — source categories | `REVISE` | Roles remain useful, but publisher/host/provider/origin and claim authority are separate; no brand ladder. |
| 5 — source registry | `REVISE` | Reuse existing registries and versioned scope entries; speculative multi-provider YAML is not accepted executable config. |
| 6 — capability source selection | `PROMOTE_TO_CORE_ARCHITECTURE` | Selection is semantic and capability-scoped; illustrative source names do not grant access. |
| 7 — bounded multi-source routing | `PROMOTE_TO_CORE_ARCHITECTURE` | Reuse existing inspect/enrich/stop and budget policy, not fan-out to every source. |
| 8 — global source hierarchy | `REJECT` | Replace universal rank with claim/field/time authority; existing route-class preference is not A4 truth ordering. |
| 9 — claim/source traceability | `PROMOTE_TO_CORE_ARCHITECTURE` | Add proposition/assertion/admission identity and source-version/field refs; no free-text identity matching. |
| 10 — numbered report citations | `KEEP_FOR_LATER_CITATION_UX` | DEF-054. |
| 11 — concise/expanded views | `KEEP_FOR_LATER_CITATION_UX` | Permission-aware projections; full source record remains canonical. |
| 12 — compression | `KEEP_FOR_LATER_CITATION_UX` | Rendering cannot choose truth by source brand or silently hide material unresolved conflict. |
| 13 — dedupe/clusters | `REVISE` | Reuse NormalizedEvent/EventCluster; shared event is not independent sourcing and observations are not collapsed/deleted. |
| 14 — conflicts | `PROMOTE_TO_CORE_ARCHITECTURE` | Comparability/taxonomy/lifecycle preserve unresolved disagreement. |
| 15 — website sources | `REVISE` | Keep read-only/access/retention safeguards; no new adapter or crawler approved, DEF-012 remains. |
| 16 — financial media | `REVISE` | Discovery/context/direct reporting are scoped roles; not an unconditional inferior rank and not a new integration. |
| 17 — model research | `REVISE` | Optional gateway-bound future provider; structured provenance/epistemic rules, no fact shortcut or adapter implementation. |
| 18 — provider neutrality | `PROMOTE_TO_CORE_ARCHITECTURE` | Canonical semantics independent of SDK/native response shapes; provider retained as provenance. |
| 19 — PIT/replay | `PROMOTE_TO_CORE_ARCHITECTURE` | Capture knowledge cutoff, content versions, policy/assumption snapshots; no live replay fallback. |
| 20 — cost/materiality | `PROMOTE_TO_CORE_ARCHITECTURE` | Attention/permission/budget remain separate from evidential truth; no new economic probability. |
| 21 — Evidence Graph | `PROMOTE_TO_CORE_ARCHITECTURE` | Existing graph plus typed refs/relations; no duplicate graph or claim all relations already exist. |
| 22 — journal | `REVISE` | Reuse append-only capture records; do not imply a general Market Intelligence Journal service is implemented. Exports are projections. |
| 23 — A4/A7 | `PROMOTE_TO_CORE_ARCHITECTURE` | A4 challenges evidence/interpretation; A7 measures reliability/value, not current SourceScore tuning. |
| 24 — acceptance principle | `PROMOTE_TO_CORE_ARCHITECTURE` | Facts need attribution; inferences/hypotheses need attributable premises, not an exemption from evidence. |
| 25 — open questions | `REVISE` | Minimal source/comparability/independence semantics settled; detailed UI, deployment, adapters and reliability scoring remain later. |
| 26 — non-goals | `REVISE` | Keep no implementation/adapters/UX; do not continue deferring the now-approved semantic design. |
| 27 — revisit sequence | `SUPERSEDE` | Pass 2 -> pass 3 A4 architecture -> bounded prerequisite implementation -> A4 runtime; citation UX later. |
| 28 — readability/audit success | `KEEP_FOR_LATER_CITATION_UX` | Core auditability is required now; human-facing presentation remains DEF-054. |

No deployment/Shell TBD was promoted. Topology cannot change provenance, source
permission or replay meaning; those are the only relevant deployment constraints.

## 8. Mandatory complexity audit

1. **Too complex?** Not if implemented as small immutable projection components.
   A universal knowledge ontology, automatic truth engine or full source platform
   would be excessive. Fields without supplied evidence remain unknown.
2. **Essential before A4 runtime:** source/origin/version refs, scoped authority,
   proposition comparison, epistemic/derivation distinction, typed unresolved
   disputes, field confirmation, PIT and captured policy/lineage assumptions.
3. **Can wait:** complete source registries, media/research adapters, citation UX,
   origin-discovery crawlers, databases, forecast generation and empirical scoring.
4. **Universal SourceScore?** Rejected. It would hide scope, correlations and
   missingness behind an unjustified scalar.
5. **Extend/project rather than redesign?** Yes: a deterministic A4 projection
   retains original IDs and versioned references, leaving A3 schemas unchanged.
6. **Duplicate graphs/replay?** No. Flat relation records over existing evidence
   and content-addressed captures are enough; graph materialization can wait.
7. **Minimum sufficient set?** For every material A4 claim, know what is asserted,
   which comparable evidence supports/opposes it, where it came from, why it is
   eligible/authoritative/independent or unknown, what changed and which unresolved
   qualifications existed at the captured decision time. Nothing here needs UI,
   live browsing, a model, statistical trust weights or another orchestration layer.

## 9. Pre-A4 implementation candidates

These classifications refer to **before A4 runtime implementation**, not before
pass 3 design. This pass authorizes no code changes. Pass 3 should incorporate
the bounded prerequisite acceptance gate, not reopen all A3 implementation.

| Candidate | Classification | Minimum bounded deliverable |
|---|---|---|
| Source identity/scoped-authority contract | `MUST_BEFORE_A4_IMPLEMENTATION` | Project existing IDs/document/role/time/basis with explicit unknowns and versioned field applicability; no global rank. |
| Claim comparability contract | `MUST_BEFORE_A4_IMPLEMENTATION` | Typed key/assertion separation and exact/transform/noncomparable/undetermined decisions; no prose extraction. |
| Contradiction taxonomy/lifecycle | `MUST_BEFORE_A4_IMPLEMENTATION` | Typed relation and append-only state record referencing originals; same-provider conflicts allowed, missing is gap. |
| Source independence lineage contract | `MUST_BEFORE_A4_IMPLEMENTATION` | Pair/root/dimension-scoped statuses, with UNKNOWN default and evidenced links; no requirement to discover every unknown root. |
| Confirmation projection | `MUST_BEFORE_A4_IMPLEMENTATION` | Separate recorded gateway status from A4 field reliance; inspect all candidates, qualify unknown basis and preserve opposing values. |
| Minimal A4 input projection/capture | `MUST_BEFORE_A4_IMPLEMENTATION` | Deterministic mapping, referential integrity, PIT, original IDs/hashes and replay-policy snapshot; reuse A3.10 substrate. |
| Richer lineage metadata extraction from existing retained artifacts | `SHOULD_BEFORE_A4_IMPLEMENTATION` | Only deterministic supported typed mappings; absence may remain UNKNOWN, no live re-research prerequisite. |
| Existing source registry's explicit scope-policy bindings | `MUST_BEFORE_A4_IMPLEMENTATION` | Only rules used by A4 field reliance need pinned entries; unknown authorities can be withheld. |
| General new source registry / automatic origin-discovery system | `REJECT` | No second registry/source truth. Revisit justified extensions to existing boundaries later. |
| User-facing citation renderer | `CAN_WAIT` | DEF-054, independently consumable semantic refs first. |
| Website/media/model research adapters | `CAN_WAIT` | DEF-012/052 and separate access/retention/budget acceptance; not required to design A4. |
| Universal SourceScore, model-autonomous conflict resolution | `REJECT` | No evidential/authority basis; source counts/confidence cannot replace recorded support. |

### Proposed foundation acceptance cases (not implemented tests)

- Revenue-from-operations versus total-income; standalone versus consolidated;
  and equal value with unknown basis remain noncomparable/undetermined.
- Explicit scale conversion preserves both assertions; zero stays zero; missing
  remains missing; incompatible fully comparable values create factual conflict.
- Same-provider conflicting assertions are preserved; provider names alone do
  not establish independence. Syndicated copies retain one demonstrated root.
- Two analyses of one filing may be independent in derivation but not measurement.
- Field confirmation cannot leak to an unconfirmed field, inferred thesis or
  forecast; NOT_FOUND cannot establish falsehood.
- Reordering multiple captured documents cannot change the preferred fact by
  lookup order. Equally applicable conflicting documents remain unresolved.
- Mixed confirmed/conflicting fields remain explicit under PARTIALLY_CONFIRMED.
- Later revision/root discovery or policy change creates a new view; original
  replay excludes it. Scope resolution preserves all original IDs and content.
- Unknown origin/basis, unavailable retained content and missing full A2 produce
  honest gaps or integrity errors, never live fallback or fabricated facts.
- Repeated deterministic projection matches its semantic fingerprint and leaves
  A2/A3.8/A3.9/A3.10 hashes unchanged. Models cannot fabricate admitted claim IDs,
  change authority or execute source text; zero-model mode remains valid.

## 10. Validation and exact next prompt

The relevant existing regression suite passed:

```bash
.venv/bin/pytest -q \
  tests/unit/market_intelligence/test_contracts_normalization.py \
  tests/unit/market_intelligence/test_routing.py \
  tests/unit/market_intelligence/test_authoritative_gateway.py \
  tests/unit/market_intelligence/test_graph_research.py \
  tests/unit/market_intelligence/test_deep_research_integration.py \
  tests/unit/events/test_contracts_point_in_time.py \
  tests/unit/opportunity_intelligence/test_integrity_boundaries.py \
  tests/unit/a3_hardening/test_contracts_package.py \
  tests/unit/a3_hardening/test_replay_comparison.py
```

**146 passed in 26.63s.** These tests verify the accepted substrate; they do not
prove implementation of the new architecture or the proposed acceptance cases.
Documentation validation also passed:

- 159 local Markdown link targets checked across all 12 pass-2 files; none missing.
- All 55 deferral IDs remain unique/sequential; 43 DEFERRED, 3 PLANNED,
  4 IMPLEMENTED, 3 REJECTED and 2 SUPERSEDED. DEF-054 remains DEFERRED.
- `git diff --check`, plus separate whitespace checks for new documents.
- SHA-256 comparison proves the pre-existing deployment TBD and pass-1 review
  were not changed. The whole worktree diff remains Markdown-only.

Files created: this review and
`TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md`.
Files updated: `README.md`, `docs/ARCHITECTURE.md`,
`docs/README_TBD_DESIGN_NOTES.md`,
`docs/TBD_TI_SOURCE_PROVENANCE_CITATION_FABRIC.md`,
`docs/TIAF_SYSTEM_ARCHITECTURE.md`,
`docs/TIAF_AUTHORITATIVE_CONFIRMATION_GATEWAY.md`,
`docs/TIAF_CAPABILITY_MAP.md`, `docs/TIAF_DEFERRAL_REGISTER.md`,
`docs/TIAF_IMPLEMENTATION_TARGETS.md` and `docs/TRADINGINTELLIGENCE_ROADMAP.md`.
The gateway note only clarifies the scope of historical route preference; it
does not rewrite accepted gateway behavior.

Full runtime gates/live acceptance were not rerun for this documentation-only
pass. No model/provider call, credential read, commit, tag or push was performed.

**Exact next Codex prompt title:**

**Post-A3 Deep Architecture Pass 3 — A4 Challenge / Arbitration / Higher-Intelligence
Agent Architecture**

Pass 3 should consume the approved semantic design, define A4's bounded reasoning
roles and handoff/acceptance gates, and schedule the minimal source-projection
foundation before runtime work. It must not assume new source models, adapters,
Shell or citation UX were implemented here.
