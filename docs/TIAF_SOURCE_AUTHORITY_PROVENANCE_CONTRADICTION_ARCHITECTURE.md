# Source Authority, Provenance and Contradiction Architecture

## Status and authority

**Approved semantic architecture, post-A3 pass 2, 2026-09-11 (Asia/Kolkata).**
This is the source-semantics companion to
[TIAF_SYSTEM_ARCHITECTURE.md](TIAF_SYSTEM_ARCHITECTURE.md). The
[pass-2 review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md)
records code findings, hypothesis dispositions and implementation prerequisites.

Normative requirements below apply to the future A4 admission/projection boundary;
they are not claims that new contracts or algorithms already exist. Accepted A3
records, enums, hashes, routing policies and specialist outputs remain unchanged.
Current package/schema versions remain separate (`0.1.0` package, A0 `1.0`
contract). Proposed names are design roles, not importable classes or assigned
schema versions. No A4 reasoning, new provider, model or citation UI is implemented.

## 1. Two distinct problems

Core semantics identify the proposition, evidence, publisher/origin, scope of
authority, derivation, availability, independence, revisions and unresolved
disputes. A4 needs these to challenge a thesis without rewriting evidence.

Citation presentation selects labels, numbering, links, bibliography, concise
views and expanded reports. It consumes the semantic record; it must not decide
truth by citation count, remove contradictory observations from canonical data,
or research new sources while formatting. Presentation remains DEF-054.

Source authority is evidential competence, **not invocation permission**. Neither
an official source nor a model's confidence grants tool/data/broker authority.
TI remains intelligence; TradeMonitor retains governance/lifecycle/execution;
the broker remains live-state truth. No majority vote or universal SourceScore.

## 2. Source and provenance identity

Use composable identities rather than a single overloaded `source_id`:

| Identity | Meaning and minimum provenance |
|---|---|
| Source entity | Publisher, issuing entity, measuring organization or attributed speaker; stable namespace-qualified identity and role. A dissemination venue need not be the issuer. |
| Provider/adapter | Acquisition intermediary and adapter/parser/normalizer version; native record ID, endpoint/tool and capture reference are provenance, not semantic predicates. |
| Upstream origin | Original filing, statement, wire dispatch, dataset/measurement or analysis from which this record derives. Preserve known parents; otherwise explicitly UNKNOWN. |
| Document/publication family | Source-qualified filing/publication ID where supplied; one family can have several versions and support many claims. A URL is a locator, not sufficient identity. |
| Document/content version | Immutable content digest plus source/document/revision identity, publication/availability/acquisition times and authenticity evidence. Identical bytes establish content equivalence, not independent authorship. |
| Evidence/assertion occurrence | Existing evidence, observation, fact, event, claim, opinion and run IDs with artifact references; never renumber originals to deduplicate a view. |

`provider != source`, `adapter != publisher`, and multiple providers may relay
one upstream origin. An exchange-hosted company filing can establish official
dissemination of the company's report without making the exchange its auditor
or the company's forecast realized truth. An official rating disclosure can be
direct evidence of the rating assigned, not proof of future solvency.

Unknown publisher/origin identities remain explicit per occurrence; do not merge
all unknowns under one root. Alias resolution requires an attributable mapping,
never brand/string similarity alone. Keep publisher, hosting/distribution and
speaker roles distinct. Capture locator/section/table/field references whenever
available. Native payloads stay in authorized audit artifacts; A4 receives only
bounded typed semantic projections and resolvable references.

## 3. Authority is claim-, field- and time-scoped

An `AuthorityAssessment` design role binds a source/document version to an
authority domain, covered subject/jurisdiction, predicate/field, period/effective
interval and statement basis. It records source role, authority basis evidence,
authenticity result, policy ID/version, assessment time, limitations and one of
`APPLICABLE`, `NOT_APPLICABLE`, `UNKNOWN`. These are proposed scoped statuses,
not replacements for A3 `SourceAuthority`.

Assess authority only after identity, comparability and PIT checks. Authority is
a scoped relation, not a global ranking or numerical probability. A policy may
designate a field authority for the same proposition; it must cite why that
source is competent and what it does not establish. Two applicable authorities
can still conflict: preserve that conflict rather than use provider order.

Illustrative policy cases (not legal determinations or live observations):

- An official filing is direct evidence of an announced corporate action and
  its disclosed terms, within that filing's subject and revision scope.
- Company IR is primary for **what guidance the company issued**; it does not
  confirm that the guided result will occur.
- An authenticated central-bank publication can establish its policy-rate
  announcement. A company filing has no corresponding macro authority.
- A suitable market-data record concerns price/volume for the specified venue,
  instrument and event time; an annual report is not authoritative for that tick.
- An exchange reference does not validate a provider's valuation percentile,
  forecast, free-cash-flow formula or inferred sentiment.

The current route's minimum `SourceAuthority` ordering and gateway strongest-
authority summary remain recorded acquisition/reporting policy. They are not
A4's winner function, proof of field coverage or source independence. Higher
source class cannot cure missing units, stale evidence or a mismatched period.

## 4. Proposition identity and comparability

Separate three identities:

1. **Proposition key:** the question being asserted—canonical entity/instrument,
   predicate definition/version, qualifiers/negation, unit/currency convention,
   reporting period or effective interval, consolidation/segment/accounting basis,
   measure type (stock/flow, actual/estimate/guidance), and applicable horizon/
   target interval. Explicit NOT_APPLICABLE differs from UNKNOWN.
2. **Assertion identity:** a particular value, interval or directional proposition,
   epistemic/derivation role and its original claim/evidence/source occurrence.
   Opposing values do not change the proposition key; repeated assertions do
   not become a single source-independent observation.
3. **Admission identity:** capture/run, decision `as_of`, availability and acquisition
   evidence, semantic mapping/projection policy/version and qualified source refs.
   Availability gates comparison; different acquisition timestamps alone must
   not disguise a same-proposition conflict as two different questions.

Keys are derived only from supplied typed facts and explicit versioned mappings.
No NLP similarity, headline parsing, guessed FY boundaries or provider-label
synonyms may invent comparability. Original IDs survive alongside new keys.

A `ClaimComparison` design role records both assertions and:

- `EXACT`: required semantic dimensions match explicitly;
- `COMPARABLE_WITH_TRANSFORM`: a documented dimension-preserving conversion
  (for example scale normalization) and its inputs/rule are captured;
- `NOT_COMPARABLE`: a known meaning, scope or time difference;
- `UNDETERMINED`: one or more required dimensions/lineage are missing or ambiguous.

UNKNOWN is not a wildcard; two missing bases do not establish equality. In an
inapplicable dimension both sides must be explicitly inapplicable. Never convert
currency, fiscal periods, adjusted/unadjusted prices or standalone/consolidated
results without the necessary factual conversion/definition contract.

Only the first two comparison states permit factual agreement/incompatibility.
Compare typed normalized values, not raw Python truthiness or string resemblance.
Zero is valid; missing is not zero; booleans are not numeric substitutes. Retain
reported precision and any explicit tolerance rule/version. No new global numeric
tolerance or tuned threshold is selected here. Without a justified conversion or
tolerance, qualify the comparison instead of fabricating exact agreement.

| Pair | Required treatment |
|---|---|
| Revenue from operations versus total income, same FY | Semantic mismatch, not factual conflict. |
| Standalone versus consolidated revenue | Scope mismatch, not two votes on the same proposition. |
| Same metric/basis/period, known lakh versus crore scale | Compare only after an explicit unit transform; preserve raw assertions. |
| Positive benchmark-relative strength versus negative absolute trend | Cross-domain tension, not same-proposition contradiction. |
| Identical label/value but missing statement basis | UNDETERMINED, not confirmed just because values match. |
| Two incompatible values for fully matched factual scope | Factual conflict even if both came from one provider or one document. |
| Old actual and new actual at different effective times | Temporal change; not automatically correction or error. |

## 5. Governed dispute taxonomy

Use a small closed/versioned taxonomy of **relations/disputes**, not an assertion
that every row is a factual contradiction. Existing A3 labels remain in
`original_kind`/original record references. New kinds require schema/consumer
review; unrecognized legacy detail is retained as unclassified, not guessed.

| Proposed category | Predicate and consequence |
|---|---|
| `FACTUAL_CONFLICT` | Comparable same proposition, incompatible factual values; cannot be resolved by count, brand or averaging. |
| `SEMANTIC_MISMATCH` | Similar label, different definition/derivation or units without valid conversion. Qualify comparability, do not adjudicate numerical truth. |
| `TEMPORAL_DIFFERENCE` | Different effective/revision scope; determine change versus correction only from explicit lineage. |
| `SCOPE_MISMATCH` | Different subject, segment, period, consolidation or horizon scope. Preserve both statements. |
| `INTERPRETIVE_DISAGREEMENT` | Compatible/shared evidence but competing specialist reasoning or conclusions on a comparable question. |
| `CROSS_DOMAIN_TENSION` | Distinct questions whose implications compete, such as fundamental quality versus technical timing. |
| `FORECAST_DISAGREEMENT` | Future/forecast propositions; model, target, issue time and horizon matter. Preserve supplied forecasts; A7 owns generation/calibration. |
| `CONFIRMATION_DISCREPANCY` | A captured discovery/confirmation disagreement; comparability and field authority must still be evaluated. It is not automatically a resolved factual conflict. |

Separate comparison result, relation category and origin/qualifiers. A confirmation
discrepancy may also carry a same-proposition factual-conflict qualifier; it is
one referenced dispute, not two independent corroborating events. A3 baseline
disagreement is interpreted by matched axes, not automatically a factual conflict.
Missing/unknown evidence is a gap, **not a ninth contradiction kind**.

Dispute identity references ordered/canonicalized assertion IDs plus the relation
definition, proposition/comparison identity and policy version. Preserve original
group IDs. A case/family ID links later revisions; immutable record versions and
content hashes distinguish each evolving membership/state. IDs need not depend
on arrival/provider order; repeat projection is idempotent, not a new vote.

## 6. Append-only contradiction lifecycle

Each transition retains original claims, prior record ID/state, new state,
reason, comparison and resolving evidence refs, actor/policy/version, effective
scope, availability and recorded timestamp. Never edit or delete an observation
to mark a conflict resolved. Membership changes create a new record version.

| State / transition | Required evidence or meaning |
|---|---|
| `DETECTED` | Candidate relation with cited assertions; not proof of conflict. |
| `UNDER_REVIEW` | Bounded comparison/confirmation work admitted; a request is not a resolution. |
| `CONFIRMED_CONFLICT` | Comparability established and incompatible values/conclusions remain, including equally applicable authorities. |
| `UNRESOLVED` | No justified disposition; may follow detection/review/conflict when evidence or budget is insufficient. |
| `NOT_COMPARABLE` | No defensible comparison; identify missing or mismatched dimensions, retaining the candidate. |
| `RESOLVED_BY_SCOPE` | Captured scope/semantic clarification explains the apparent conflict; neither original statement is declared false. |
| `RESOLVED_BY_REVISION` | An eligible explicit correction/restatement supersedes the relevant assertion for this view, not for earlier historical runs. |
| `RESOLVED_BY_AUTHORITATIVE_FIELD` | Comparable eligible field, applicable authority basis and resolving evidence justify a preferred factual assertion; other observations and any remaining disagreement persist. |
| `SUPERSEDED` | A successor dispute record replaces this view; exact successor/reason required. Not a synonym for "winner selected". |

Detection can move to review, a qualified scope/non-comparable disposition or
confirmed conflict without fabricating a review call. Unresolved/reviewed cases
can advance only with referenced evidence. A resolved case reopened by a later
revision produces a new case version in DETECTED/UNDER_REVIEW, not a rewritten
past state. Validate acyclic predecessor/supersession links and referential
integrity. Semantic scope resolution need not acquire a new provider if the
required facts are already captured. A model's confidence is never resolving
evidence. Resolution of interpretation belongs to A4, not this factual lifecycle.

## 7. Source independence is a qualified relationship

An `IndependenceAssessment` binds two assertion/source-root sets, the dimension
being assessed, scope/as-of, status, basis evidence and policy/version:

- `SAME_ROOT`: same upstream document, wire story, statement or measurement;
- `DERIVED_FROM`: directed transformation/republication of the other root;
- `LIKELY_DEPENDENT`: positive evidence of likely shared origin, explicitly
  qualified, not a numerical dependence estimate;
- `INDEPENDENT`: affirmative captured evidence supports separate origin for
  the specified dimension; absence of a link does not suffice;
- `UNKNOWN`: insufficient lineage; never silently upgraded.

Dimensions distinguish publication lineage, measurement origin and analytical
derivation. Two analysts can independently analyze the same filing but do not
provide two independent measurements of its revenue. Different provider names,
URLs, domains or paraphrases do not prove independent sourcing. A common wire
story or company statement remains one root even through several wrappers.

Preserve all observations, including copies. Do not calculate confidence from
provider/citation count. Corroboration language must identify demonstrated roots
and scope; unknown lineage cannot inflate it. Independence is not generally
transitive: A independent of B and B independent of C does not establish A/C.
Root equivalence may be grouped when established; derivation edges must be
acyclic, and multiple-parent derivations retain every parent. If lineage checks
fail, expose a gap and withhold the independence claim.

## 8. Revisions, corrections and time

Retain each immutable source version and asserted value, with explicit links for
`CORRECTS`, `RESTATES`, `CLARIFIES` or `SUPERSEDES` where evidence supplies that
relationship. These are proposed relation semantics, not new A3 enums. A changed
webpage/hash proves new captured content, not an issuer-declared correction.
A clarification may add detail without superseding the whole publication.
Supersession can be field/period-scoped; a corrected figure does not erase all
claims in the old document. Cross-publisher reports cannot supersede an issuer's
record merely by asserting that it was wrong.

Preserve event/effective time, publication time, source availability/basis,
acquisition time and TI's later assessment/recorded time separately. For a view
at decision T, only evidence captured/admitted by T and eligible under its
availability policy can affect the decision. A later-acquired old publication
is not silently inserted into the original run. Date-only/conservative/unknown
availability retains that limitation. No arbitrary historical PIT claim is added.

New projections over old captures may be computed today, but must identify
their modern policy/creation time and original evidence cutoff. They are not
historical A4 outputs that never existed. Later lineage discoveries or source-
authority changes create explicit new comparisons/views, never affect recorded
replay. Future outcomes must not enter decision-time evidence.

All application timestamps are aware, normalized using
`zoneinfo.ZoneInfo("Asia/Kolkata")`, and serialize with `+05:30`; reject naive
values. Semantic collections use immutable tuples/JSON arrays. Mutable legacy
metadata must be defensively reconstructed before projection/fingerprinting.

## 9. Epistemic kind and derivation are orthogonal

Retain A3 `FACT`, `INFERENCE`, `HYPOTHESIS`, and the existing
`REPORTED`, `PROVIDER_DERIVED`, `TI_DERIVED` derivation axis. Do not add
`PROVIDER_DERIVED_METRIC` as a competing epistemic truth level. FACT means an
attributed supported assertion, not guaranteed world truth or an authority grant.

A4's minimal projection needs an explicit claim-role qualifier—observed/reported
value, attributed statement, derived metric, interpretation or forecast—and
epistemic mapping status. These qualifiers are a bounded design extension;
old enums and records do not change. Ambiguous mappings remain UNMAPPED/UNKNOWN
rather than default FACT. Preserve the original kind alongside projected meaning.

| Existing input | Safe A4 meaning |
|---|---|
| Accepted canonical reported fact | Attributed FACT with mapping/quality/PIT and source refs retained; still challengeable. |
| Provider-derived metric | Derivation remains PROVIDER_DERIVED; missing formula/basis prevents promotion into a differently defined reported fact. |
| `EvidenceClaim` FACTUAL / INTERPRETIVE | Retain original kind and citations; map only through a declared typed rule, not by parsing its prose. |
| Research INFERENCE / HYPOTHESIS | Cited premises and reasoning; hypotheses retain assumptions/invalidation. Neither may be recycled into a new reported fact. |
| Quoted management guidance / analyst estimate | FACT that the source issued the statement, if evidenced; future proposition remains forecast/attributed expectation, not realized outcome. |
| Specialist opinion / FORECAST_INTERPRETATION | Interpretation of supplied evidence; not a newly calibrated forecast. |
| A3.9 WORKFLOW / QUOTED_SOURCE reason | Operational record or quotation with original epistemic meaning; not automatically a market FACT. |

No additional global OPINION or FORECAST enum is needed before A4. Typed forecast
target/horizon/model/calibration provenance can be referenced where already
supplied; A7 owns generation and calibration. Every interpretation or hypothesis
must expose premises and gaps. Source/model prestige cannot alter epistemic kind.

## 10. Confirmation is scoped evidence reconciliation

Consume the captured gateway result **and** its requested fields, claim facts,
documents, confirmed fields, discrepancies and route/parser/source provenance.
A `ConfirmationProjection` retains `recorded_status` unchanged and separately
records each field's A4 admissibility/comparability, authority assessment and gaps.

| Recorded outcome | Safe interpretation |
|---|---|
| Document acquired/authenticity validated | Document existence/provenance, not confirmation of all its fields or the discovered claim. |
| CONFIRMED | Gateway reported matches for requested fields. A4 reliance additionally requires complete matching semantic scope, eligible time and field authority. Not downstream thesis confirmation. |
| PARTIALLY_CONFIRMED | Inspect all matching and discrepant fields; an unresolved field may contain a conflicting value, not merely absence. |
| CONTRADICTED | Explicit discrepant value recorded; establish comparability before calling it factual conflict. |
| NOT_FOUND | Bounded attempt did not locate evidence; NOT_FOUND != FALSE. |
| AMBIGUOUS | Missing/uncertain authenticity, parsing, mapping or scope; no claim of falsity or full confirmation. |
| UNAVAILABLE / OUT_OF_COVERAGE | Acquisition/coverage limitation, not an observation about the claim's truth. |

Multiple authoritative documents for one field must be examined separately.
No last-write-wins field map, strongest-document summary or equal raw value can
substitute for the scoped comparison. An A3 recorded match lacking enough basis
is **recorded match / A4 admission undetermined**, not retroactively changed to
an A3 failure. Missing supporting artifacts prevent verification and remain gaps.
If a supposedly resolved field has another equally applicable conflicting source,
preserve the unresolved conflict.

Confirmation neither makes a copied source independent nor establishes a
downstream inference, forecast or recommendation. Discovery observations survive
all dispositions. Selection of a source for a permitted route is distinct from
the semantic reason to prefer a field assertion after it returns.

## 11. Materiality without a trust score

Materiality is request/horizon-specific attention priority, not truth or calibrated
economic probability. Reuse existing EventMateriality and MaterialityTrigger
vocabulary; record reasons and policy/version, never substitute numeric brand
weights. Consider evidence-linked potential effects on opportunity state/risk,
A2/A3 disagreement, magnitude relative to a supplied basis, freshness and a
supplied position context. Unknown scale/effect stays unknown.

Priority can drive bounded confirmation/research requests or A4 challenge
attention under existing grants and budget. It does not silently raise a model
tier, obtain data permissions, change a source's authority or resolve conflict.
Budget exhaustion returns unresolved/material gaps with the partial result; it
does not force a winner. Low-materiality differences may be deferred from active
research, but remain in canonical lineage. Disclosure flags identify material
unresolved constraints for later rendering without designing the UI here.

Authority, authenticity, quality, freshness, relevance, independence, directness
and completeness remain distinct typed dimensions. A primary source can be stale,
partial or irrelevant; a secondary source can be timely, direct discovery evidence.
No scalar combines those dimensions in this pass. Existing numeric graph
materiality is not a source-trust or probability score.

## 12. Lineage and the existing Evidence Graph

The sparse graph describes material company/context relationships. Existing
claim citations, native-normalization-evidence links, event clusters, confirmation
records and replay references already form the authoritative lineage substrate.
Do not introduce a second graph engine, database or independently mutable truth.

```text
publisher / upstream document version
          -> provider observation -> normalization -> canonical evidence
                                                    -> claim/opinion -> A3.9
confirmation + revision + independence + dispute records reference those IDs
          -> deterministic A4 semantic projection
A3.10 package preserves originals; future A4 parent capture pins the projection
```

Minimal typed relation records may express SUPPORTS/CONTRADICTS, DERIVED_FROM,
SAME_ROOT, PUBLISHED_BY, CONFIRMS_FIELD, CORRECTS/RESTATES/CLARIFIES/SUPERSEDES.
Reuse existing citation/supersession fields first. New semantic relations can be
stored as flat immutable projection records with captured provenance; they need
not masquerade as current GraphRelation values. If graph traversal later needs
claim/document nodes, add a versioned projection into the **same** graph boundary,
not another store or new authoritative relation copy.

An event cluster means a shared event context, not proof of source independence
or agreement. Graph edges cite evidence; dispute records cite claims; the replay
manifest pins all referenced versions. Later citation renderers follow these
refs rather than re-research. Missing/cyclic/mismatched links remain visible and
cannot support fabricated corroboration or resolution.

## 13. Minimal A4 semantic input projection

Approve an additive, deterministic `A4SemanticInputProjection` design role.
A3.9 alone is too compact for general source-aware challenge; the complete A3.8/
A3.10 capture plus a typed projection avoids changing frozen A3.9. This is not
the universal public capability envelope and is not implemented now.

| Component | Minimum content and admission rule |
|---|---|
| Identity/policy header | Projection schema and policy IDs/versions/digests; subject, objective, horizon, evidence as-of, creation time, caller authority reference, approved budget/profile/model constraints, run/correlation identity. No credentials. |
| Frozen parent references | A3.10 package exact checksum/semantic fingerprint; A3.8/A3.9 capture IDs/fingerprints; A2 assessment/evidence IDs, policy and full-versus-projection capture mode. All resolvable within approved capture scope. |
| Opportunity and opinion view | A3.9 structured state/reasons/gaps unchanged; active/superseded individual opinions and original baseline comparison, not a majority summary. |
| Claim/evidence index | Original claim/fact/evidence IDs; normalized typed assertions, proposition keys/comparisons, mapping status, epistemic and derivation roles; bounded ambiguity records, source and artifact locators. No raw provider payloads or invented scope. |
| Source and authority index | Source entity/provider/origin/document-version identities, authority scope/basis and assessment versions; quality, freshness, directness, completeness and PIT limitations kept separate. |
| Relation/admission views | Pair/root-scoped independence, typed disputes and state history, revision relations, field-level confirmation projections with recorded and A4 admissibility states distinguished. |
| Coverage/audit | Required/optional/material missing evidence, unresolved mapping/lineage, excluded evidence and reasons, usage/cost knowledge, projection semantic fingerprint and referenced content digests. |

Typed references plus small normalized records are sufficient; do not duplicate
all nested artifacts. Deterministic projection uses only captured typed data and
explicit versioned rules. Unknown semantics get named gaps, not LLM completion.
No A2 recomputation, specialist rerun, source acquisition or trading decision is
part of projection. Missing mandatory capture identity/integrity is a fail-closed
admission error; legitimately absent optional content creates a partial view.
Missing full A2 is explicitly projection-only and bars claims requiring uncaptured
facts. An empty source set may be valid for an inapplicable capability, not an
excuse to infer authoritative support.

## 14. Replay and policy comparison

Reuse A3.10 content-addressed capture/integrity and recorded-versus-deterministic-
verification patterns. A future A4 parent capture must reference the unchanged
A3 package and persist its own projection, authority/comparison/independence/
materiality policies, eligible revisions, confirmation and dispute-state snapshot.
Do not insert fields into frozen A3.10 schema `1.0` or alter child hashes. A4
schema/storage integration details belong to its implementation plan, not a
second replay engine.

Recorded replay reconstructs the recorded policy/assumptions and conclusions.
Deterministic projection verification uses captured inputs and pinned rules.
Changed source policy, later-origin knowledge or revised evidence yields an
explicit new comparison/run; never call that exact original replay. Hash inputs
include semantic assumptions, eligible source/document/claim IDs, original artifact
digests, comparison/transformation rules and unresolved states. Define hashing
canonically at implementation; do not recompute old child algorithms. Keep
original-run and replay usage distinct; unknown cost is not zero.

No live source or model fallback during replay. If a referenced blob is missing,
corrupt, unauthorized or a policy version is unavailable, expose the corresponding
failure/verification limitation. A URL alone cannot replay mutable content.
Retention restrictions may limit audit depth; state that explicitly. Integrity
does not prove authenticity, public availability, independent origin or truth.

## 15. A4 challenge and future model constraints

The projection enables A4 to question an ambiguous metric, detect a scope mismatch,
challenge stale/unsupported premises, identify copied-source echoes, retain
same-proposition conflict and request bounded confirmation for material gaps.
It does not specify A4 Agent roles, ranking weights, voting or arbitration policy.

Any future model must consume only admitted structured evidence; cite resolvable
claim/evidence IDs; keep facts, inference and hypotheses separate; expose opposing
evidence; and retain uncertainty. It may propose a challenge, not invent a source,
field, independence relation or resolving document. Source text is untrusted data,
not instructions or tool authority. Model confidence is not source authority or
calibrated probability. Preferring other evidence over an applicable authoritative
field requires a cited, explicit scope/recency/authenticity reason and governed
review, never intuition. No model can change capture history or increase grants.

Model-backed integration remains optional and deferred under DEF-052. Recorded
model outputs are not deterministically regenerated during historical replay.
No prompt, model policy tuning, website/media/research adapter or A4 implementation
is approved by this semantic design.
