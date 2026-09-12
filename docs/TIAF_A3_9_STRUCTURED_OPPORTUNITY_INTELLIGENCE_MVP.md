# TIAF A3.9 — Structured Opportunity Intelligence MVP

## Status and authority

Implementation pass, 2026-09-10. **Accepted/frozen at `tiaf-a3.9`**
(`ca71087`). The implementation was built above accepted/frozen `tiaf-a3.8`
(`eb96879`). The prior architecture-only changes were preserved. A1/A2 and
A3.1–A3.8 remain unchanged accepted inputs. Runtime, tests and offline acceptance
are now implemented; no dependencies, specialist policies or live calls changed.
See [implementation results and limitations](STUDY_A3_9_USER_LEVEL_ACCEPTANCE.md).

This is the implementation design under the [A3 architecture](TIAF_A3_ARCHITECTURE.md)
and [detailed roadmap](TIAF_A3_DETAILED_ROADMAP.md). New contract, enum and function
names below describe the approved design; concrete exports are listed in the study. A3.10 hardening is
implemented after A3.9; the later separate A3 closure review concludes
`READY_TO_FREEZE_A3`. No architectural detour into TI
Shell or the post-A3 Source/Provenance/Citation Fabric is introduced.

Post-A5 compatibility addendum: bounded
[Pluggability R1](TIAF_PLUGGABILITY_R1_REQUIRED_SCOPE_EXPLICIT_ABSENCE.md)
projects Planner `1.1` required absence as applicable-but-unusable, so an absent
required binding remains in A3.9's required denominator and missing set. Optional
absence remains visible without entering that denominator. Captured Planner
`1.0` runs retain their historical projection and fingerprint semantics; the
A3.9 synthesis policy itself remains `1.0`.

## 1. Ownership: classification, not arbitration

A3.8 owns **which evidence/specialists run**. A3.9 owns a **structured description
of the resulting opportunity**, including what prevents a stronger description.
A4 owns challenge, thesis arbitration and final recommendation policy.

A3.9 assembles independent opinions, interpretable state, qualified bias,
quality/risk/maturity, supporting/opposing reasons, contradictions, coverage and
baseline comparison. It does not select a winning specialist, change confidence
weights, suppress opposition, or return an execution recommendation. Rule
precedence below concerns reporting restrictions, not whose market thesis wins.

MVP scope is one caller-selected **underlying equity or index per captured A3.8
run**. A derivative-origin request may identify its explicit underlying; its
contract selection is not an output. Unknown identity/applicability stays unknown.
There is no candidate generation, ranking, top-N guarantee or batch scheduler.
The earlier roadmap allowed A2-order-preserving batches; this narrower MVP does
not need them. A future batch wrapper can preserve input order without assigning
an A3 rank, but is not an A3.9 implementation prerequisite.

Prohibited outputs: ENTER/BUY/SELL, specialist winner, position HOLD/BOOK/EXIT/
PROTECT, CE/PE, selected contract/expiry/strike/quantity, stop-loss/target,
expected return/distribution, calibrated success probability, learned weights,
broker operation or TM lifecycle decision. Existing source records may contain
instrument dates or quoted technical levels; retaining their original audit is
not permission to promote them into public expression/target fields.

## 2. Existing contracts: reuse and avoid naming collisions

| Current seam | A3.9 decision |
|---|---|
| `tiaf.planner.OrchestrationResult` | Source of active independent opinions, A2 identity, gaps/conflicts, outcomes/skips, stops, context IDs and known/held usage. Alone it lacks the complete request and captured artifacts. |
| `tiaf.workflows.OrchestrationRunRecord` | Required captured handoff envelope: request, plans/registry, inventories, attempts, projections, artifacts and result. Do not redesign or mutate it. |
| `replay_recorded` | Read/validate an existing portable A3.8 capture without execution. Do **not** call `verify_deterministic` during A3.9 assembly: that API reruns specialists. |
| `AgentOpinionV2`, `AgentConfidence`, `EvidenceClaim`, `MissingEvidenceRequest` | Preserve the original typed objects/identities and their differing meanings. Opinion stance is not a trading action. |
| Nine `*_assessment_from_opinion` extractors in `tiaf.agents.specialists` | Decode accepted typed detail, including Quality/Risk detail not present in the upstream-only A3.8 projection allowlist. Never call `.analyze`, parse prose or retune policies. |
| `tiaf.baseline.OpportunityAssessment` | Actual A2.9 benchmark: direction, score, class, components/context references and policy. Preserve when captured/resolvable; never recompute it. |
| `tiaf.contracts.OpportunityAssessment` | A0 consumer contract with `OpportunityAction.ENTER`, scalar score/confidence and expected-move fields: **not** a safe A3.9 output container. Leave unchanged. |
| Existing `CandidateClass`, `AgentStance`, quality/risk/maturity/extension enums | Reuse within their declared semantics. No second A2 class, price score or confidence scale. |
| Authoritative confirmation / deep-research / graph artifacts | Read canonical typed outcomes and lineage through the captured envelope; no raw provider payload interpretation or new gateway call. |

Source anchors: `src/tiaf/planner/models.py`, `src/tiaf/workflows/{records,replay}.py`,
`src/tiaf/agents/{models,evidence,enums}.py`,
`src/tiaf/agents/specialists/{technical,fundamental,news_event,relative,sector,macro,opportunity}/`,
`src/tiaf/baseline/models.py`, `src/tiaf/contracts/assessments.py`, and MI
authoritative/deep-research models.

## 3. Input and handoff validation

Propose `OpportunityIntelligenceRequest` as a small assembly envelope: request ID,
captured `OrchestrationRunRecord` (or locally resolved capture plus digest), and
an explicit `OpportunitySynthesisPolicy` snapshot. Derive subject, underlying,
purpose, style, horizon and as-of from the A3.8 request. Do not accept replacement
opinions, new evidence, conflicting horizon overrides or provider payloads beside
that run. An optional persisted A2 assessment may be resolved only through its
captured reference; it is not a new analysis input.

Validation before synthesis must:

1. Reconstruct/validate the capture and its checksums, artifact IDs, request/run
   identity, plans, registry versions and original A2 pack/fingerprint.
2. Match active result opinions to nonsuperseded attempts and node outcomes.
   Require at most one active opinion per selected specialist. Preserve previous
   attempts solely in audit, never union them into active support.
3. Check symbol/underlying, instrument, horizon, baseline reference, detail schema,
   specialist/policy versions, evidence fingerprint, citations and input packs.
   Reused opinions are validated against their **original invocation pack**,
   not stamped with the latest run or inventory identity.
4. Resolve every claimed evidence/claim/confirmation/research/graph reference
   inside the capture package. Distinguish missing evidence reported by a valid
   run from a missing artifact the package claims to contain. The latter is a
   capture-integrity error, not an ordinary market-evidence gap.
5. Respect the captured as-of, evidence availability, observed/effective dates,
   opinion validity and source-declared freshness. No new wall-clock aging or
   provider fetch occurs during replay. Later evidence needs a new A3.8 request.
6. Decode only supported typed schemas and fail clearly on incompatible versions;
   never reconstruct typed claims from summary text. An absent optional detail
   creates an unusable contribution/gap, not a guessed label.

Corrupt/inconsistent captures return typed validation errors and no market
classification. Valid partial/failed/abstaining orchestration yields an ordinary
intelligence object with gaps, source outcomes and insufficient classification
where appropriate. If new orchestration is needed, return an inert typed
prerequisite request referencing the existing missing request/requirement IDs;
the caller decides whether to invoke A3.8. No automatic loop or budget is added.

### A2 content versus A2 identity

A3.8 guarantees a baseline reference and evidence fingerprint, but not necessarily
the full A2 `OpportunityAssessment` object. Use an immutable `BaselineView`:
assessment ID, original A2 evidence fingerprint, availability, optional complete
direction/class/score projection, original assessment/capture reference and
projection evidence IDs. Prefer the resolved captured A2 object; otherwise read
the complete `baseline.direction`, `baseline.candidate_class`,
`baseline.opportunity_score` tuple in the preserved A2 pack. Never take a majority
of specialist copies of that tuple. Missing tuple -> absent values plus explicit
baseline-content gap; contradictory copies -> integrity error.

A2 `eligible`, components, weights, warnings, NO_TRADE and fingerprints remain
unchanged. A reference is not proof that full component content is available;
show this distinction. A3.9 does not overwrite A2 eligibility or submit WATCH
items into an A2 eligible/ranking list.

## 4. Composable public output

Propose `StructuredOpportunityIntelligence`, distinct from both existing
`OpportunityAssessment` classes. Compose small immutable sub-records:

| Sub-record / field | Meaning |
|---|---|
| Identity | Intelligence/request IDs; canonical subject and underlying instrument type, objective/style/horizon, captured as-of, schema and policy identity. |
| `OpportunitySummary` | One observation state, primary/all matching rule IDs, qualified `BiasSummary`, cited Quality/Risk views and maturity/extension/remaining-room facets. No new opportunity score. |
| `SpecialistContribution` tuple | Original opinion/run/version refs, role, applicability, usability, typed facets, source confidence, reasons and evidence lineage. |
| `BaselineView` | Original A2 reference/fingerprint and available class/direction/score, plus comparison statements. |
| `ContradictionSummary` | Separate benchmark disagreement, cross-specialist tension, same-proposition conflict, provider/semantic disputes and authoritative field outcomes. |
| `CompletenessProfile` | Required/optional/applicable sets, usable/missing/blocked/unknown facets, quality/freshness and separate confidence bases. |
| `IntelligenceReason` tuples | Supporting/opposing/risk/gap reasons with code, source opinion/claim/detail-field/evidence refs, epistemic kind and relevance; no uncited generated market assertions. |
| Context summaries | Confirmation IDs/statuses/field scopes/unresolved discrepancies; canonical research IDs/gaps; graph refs/epistemics. References, not another research report. |
| `OrchestrationAuditLink` | Input run ID/semantic fingerprint, exact capture reference/checksum, active/superseded IDs, stops and original known/held usage. |
| `IntelligenceRunRecord` | Captured input, full policy snapshot, deterministic rule trace, output semantic fingerprint and separate operational assembly timing/usage. |

Return source `OpportunityQualityState`, `OpportunityRiskLevel`,
`OpportunityMaturityState`, Technical `ExtensionState` and remaining-room enums
with their source locators. Missing or unusable details retain their existing
UNKNOWN/INSUFFICIENT vocabulary (or an absent value with reason). Do not invent
`EARLY_TO_MID`, average maturity, transform remaining room into a price target,
or turn a missing Risk opinion into LOW risk. Preserve disagreeing facet values.

Use `ContractModel`, frozen fields and `tuple[...]` semantic collections; accept
Python/JSON lists and serialize ordinary JSON arrays. Metadata stays safe/simple
extension data, not a hidden policy channel. Revalidate at boundaries; shallow
freezing is not deep metadata immutability. Use `TiafDateTime` and
`ZoneInfo("Asia/Kolkata")`: reject naive datetimes, normalize aware timestamps,
emit `+05:30`, never naive `datetime.now()` or manual offset arithmetic.

Package `0.1.0`, base schema `1.0`, opinion schema `2.0`, proposed intelligence
schema `1.0` and synthesis policy `a3.9-observation-v1` are separate identities.
Do not change existing versions merely to introduce this new product.

## 5. Specialist contribution and applicability

Reuse the captured A3.8 selected/skipped/required policy as the execution truth.
Add a versioned **contribution-role table**, not a replacement planner. Missing
required execution cannot be relabeled optional to make a result attractive.
Unsupported and permission/budget-blocked are not the same as not applicable.

| Specialist | Contribution role and field semantics | Applicability / limit |
|---|---|---|
| Technical | Price-structure direction, momentum, timing, extension, remaining room, MTF and invalidation concepts. | Underlying equity/index; no new MA/RSI/ATR or breakout calculation. |
| Fundamental | Company quality, valuation/fragility, financial dimensions and supplied horizon relevance. | Positional company context; DAY skip/index exclusion preserved. Good company quality is not automatically bullish price direction. |
| News/Event | Catalyst direction, materiality, execution/event risk, clusters and source conflicts. | Preserve event horizon and availability; no news is not evidence of no event risk. |
| Relative Strength | Benchmark-relative leadership/consistency and supplied mapping. | Positive relative return is not necessarily positive absolute return. No automatic benchmark discovery. |
| Sector | Sector/rotation/subject-relative context and mapping confidence. | Missing mapping stays missing; no inferred membership. |
| Macro | Regime, subject sensitivity and relevance. | Conditional on A3.8 selection/exposure; not selecting it is not negative evidence. |
| Derivatives Context | Positioning, volatility, crowding, liquidity and expiry proximity context. | Verified F&O or applicable index/underlying context; non-F&O skip neutral, unknown eligibility unresolved. Never chooses a derivative expression. |
| Opportunity Quality | Quoted quality, maturity, remaining room, supportive/adverse families. | Downstream synthesis, not another independent vote for the upstream evidence. |
| Opportunity Risk | Quoted risk level, active risk families and restriction explanations. | Required coverage attempt; failed/missing Risk must block an unrestricted opportunity classification. Not a position risk manager. |

Preserve each opinion's exact horizon; use explicit DAY/POSITIONAL style and
captured selection plus specialist-declared relevance. Do not invent a 20-day
weight crossover, infer financial-policy support from a symbol, or promote
longer horizon alone into mandatory deep research. A3.9 neither spends A3.8
budget nor changes its selection to satisfy the contribution table.

### Direction/bias without a hidden winner

`BiasSummary` retains a typed view per domain, not one vote per opinion.
Use `AgentStance` for the qualified headline and record its semantic scope:
**underlying price-structure bias, subject to separately reported context**.

Only a field explicitly describing that same subject's price direction over the
requested horizon can supply a directional sign. In the current inventory that
is principally the Technical interpretation; A2 direction is a separate benchmark,
not another specialist vote. Relative outperformance, company quality, catalyst
direction and risk severity cannot be silently converted to absolute price signs.
The exact eligible field allowlist is part of the policy snapshot.

If usable comparable direction fields disagree, the headline is MIXED; if all
agree it may quote POSITIVE/NEGATIVE/NEUTRAL. With no usable direction field it
is INSUFFICIENT_EVIDENCE (ABSTAIN only when the relevant sources abstain).
Material opposing contextual evidence makes the **qualified** headline MIXED
while retaining the unmodified price-direction facet. This is an intersection
of compatible claims, never majority voting. A single quote carries its source
scope and does not imply independent corroboration or overall opportunity quality.

Technical therefore owns its price-structure label, not the opportunity verdict:
company/event/risk gaps and opposing facets can block OPPORTUNITY, require WAIT,
or expose conflict. No domain can erase another domain's contrary claim.
Negative price bias is not a sell/short/PE instruction, nor is weak company quality
automatically support for a bearish trade.

### Correlation and lineage

Group evidence by captured family and shared canonical fact/event lineage. Same
evidence repeated in Technical, Quality, Risk, research and graph context remains
one underlying support lineage with multiple interpretations. Keep all opinion
references, not multiple corroboration credits. Quality/Risk are labelled
`DOWNSTREAM_SUMMARY`; do not add their support count to upstream counts.

Reuse source observation/claim/event cluster IDs and A3.8 projections' original
opinion/field/citation links. Do not treat matching prose as proof of duplication
or differing providers as proof of independence. If lineage cannot establish
independence, mark it unknown and make no independence claim. Family coverage
can be reported as an explicit set/count; it is not a statistical sample size.

## 6. State model and deterministic synthesis policy

Introduce only an observation-level `OpportunityState` with:
`OPPORTUNITY`, `WATCH`, `WAIT`, `AVOID`, `NO_TRADE`, `CONFLICTED`,
`INSUFFICIENT_EVIDENCE`. Do not reuse `OpportunityAction`, which permits ENTER.

- **OPPORTUNITY:** current evidence supports a well-described underlying setup
  without a known blocking qualification; still no recommendation or execution.
- **WATCH:** identifiable support worth observing, but completeness/context/baseline
  prevents an unrestricted description. No implication that evidence is improving
  unless an actual earlier captured comparison is supplied.
- **WAIT:** a specifically cited timing/event/chase condition currently prevents
  an otherwise interpretable setup; record the condition, not an invented date.
- **AVOID:** a supported CRITICAL opportunity-risk restriction for this snapshot,
  not a sell command or permanent company judgment.
- **NO_TRADE:** no sufficiently supported setup under this observation policy;
  preserve the distinction from A2's identically named benchmark class.
- **CONFLICTED:** unresolved decision-relevant opposing claims prevent a single
  unqualified description. Nobody wins.
- **INSUFFICIENT_EVIDENCE:** minimum classification evidence is unavailable or
  unusable. It is not NEUTRAL, low risk or NO_TRADE by default.

Do not add `STRONG_OPPORTUNITY`: source `OpportunityQualityState.STRONG` already
expresses strength. `AVOID_CHASE` is a WAIT reason backed by extension/room fields,
not another overlapping state. No additional action or scalar strength field.

### Predicate definitions for v1

Predicates use a reviewed finite field/enum allowlist, not new scoring thresholds.
Record every predicate's input locators, TRUE/FALSE/UNKNOWN and reason codes.

- **Usable facet:** supported typed detail and resolved citations; source run
  SUCCESS/PARTIAL; quality GOOD/PARTIAL; freshness FRESH/AGING; no expiry at as-of
  and no unresolved factual dispute affecting that field. UNKNOWN, stale,
  degraded or uncited content remains visible but cannot satisfy a positive gate.
- **Core available:** readable complete A2 baseline tuple and usable Technical,
  Opportunity Quality and Opportunity Risk facets. This enables classification,
  not complete company/event coverage. Missing core -> insufficiency; severe
  risk/conflict flags are still exposed independently.
- **Support present:** cited supportive factors from first-order typed fields or
  Quality supportive families with resolved upstream lineage. Quoted bullishness
  alone or duplicate Quality/Risk counts do not establish additional support.
- **Blocking conflict:** an unresolved same-proposition conflict, material adverse
  first-order context opposing the setup, or a material source/confirmation
  discrepancy affecting a state gate. A2 disagreement alone is comparative, not
  an automatic blocker. Neutral/noncomparable domain views are not opposition.
- **Timing restriction:** Technical EXTENDED/EXHAUSTION_RISK, LIMITED/MINIMAL
  room, a cited weak/mixed timing condition with existing support, or material
  HIGH/CRITICAL event plus HIGH event execution risk. Directional downtrend alone
  is not poor timing for every possible underlying view.
- **Complete for opportunity:** every applicable A3.8-required specialist/facet
  has usable evidence; no unresolved required/material gap or unknown
  applicability; required quality GOOD and freshness FRESH; source Quality
  STRONG/GOOD, Risk LOW/MODERATE; usable POSITIVE/NEGATIVE qualified bias; no
  blocking conflict/timing restriction. Optional unavailable work stays visible
  but does not itself make this predicate false. Optional adverse evidence does.

These are conservative engineering defaults, not calibrated predictors. A3.8
COMPLETE does not by itself prove these gates; PARTIAL likewise does not erase
all useful interpretation. Requested but absent required specialists continue
to restrict classification. A3.9 must not require nine opinions on every request.

The first policy snapshot must carry finite, testable field mappings, including
these initial contextual restrictions; no implementation-time prose classifier
may decide what "material opposing context" means:

| Captured typed input | Restriction interpretation |
|---|---|
| Positional Fundamental `company_quality` WEAK/DETERIORATING or `balance_sheet_state` DISTRESSED_RISK, against a source-supported constructive setup | Material company-quality tension; retain both domain assessments and block an unqualified constructive opportunity. Do not infer negative price direction or a short opportunity. |
| Fundamental valuation EXPENSIVE/VERY_EXPENSIVE alone | Opposing valuation qualification, not automatically a same-proposition conflict or CRITICAL risk; source Risk/other typed gates still decide restrictions. |
| News materiality HIGH/CRITICAL plus `execution_risk` HIGH | Material event/timing restriction; source dispute affecting that event remains a conflict instead of silently accepting the headline. |
| Source typed contradiction referencing a required gate, or captured unresolved discrepancy in its same field/period/semantic basis | Blocking unresolved conflict; keep original codes and evidence, do not select a provider winner. |
| Technical mixed timing facets with source-cited support, or its explicit extension/room restriction | WAIT condition, not an inferred future entry time or price. A MIXED label on an unrelated context facet is not automatically this timing predicate. |
| Sector/relative/macro/derivatives adverse facet without an explicit gate-relevant contradiction | Qualification, not an independent negative price vote; existing Quality/Risk restriction and completeness gates remain visible. |

Unlisted or unknown enum meanings remain quoted/unknown, not guessed into a
restriction. WP2–3 must freeze exact field locators and enumerate the cited
Technical timing combinations in the policy snapshot with boundary tests; no
new numerical indicator thresholds, weights or source interpretation changes
are authorized. Qualification must prevent OPPORTUNITY when its affected
required gate cannot be established, even when it does not justify CONFLICTED.

### Ordered state rules

Evaluate **all** predicates and keep all matched rules. First matching row supplies
the headline; lower-priority constraints/reasons never disappear. UNKNOWN cannot
be treated as FALSE to pass an affirmative gate.

| Order / rule | Predicate | Headline |
|---|---|---|
| 1 `CORE_UNUSABLE` | Core unavailable, including all-abstain/no usable core. | INSUFFICIENT_EVIDENCE |
| 2 `UNRESOLVED_CONFLICT` | Blocking conflict. | CONFLICTED |
| 3 `CRITICAL_RISK` | Usable Risk CRITICAL, without a dispute invalidating that finding. | AVOID |
| 4 `TIMING_RESTRICTION` | Timing restriction or usable Risk HIGH. | WAIT |
| 5 `BASELINE_NO_TRADE` | A2 NO_TRADE. | WATCH if support present and qualified bias is directional with Risk LOW/MODERATE; otherwise NO_TRADE. |
| 6 `SUPPORTED_SETUP` | Complete for opportunity, support present, A2 class not NO_TRADE. | OPPORTUNITY |
| 7 `QUALIFIED_SUPPORT` | Support present but incomplete/qualified. | WATCH |
| 8 `NO_SUPPORTED_SETUP` | Core available with no affirmative supported setup. | NO_TRADE |

Conflict precedence over a contested risk label avoids silently adjudicating the
dispute; core insufficiency does not hide independently observed risk warnings.
Why WAIT versus WATCH must cite the specific restriction. AVOID is deliberately
narrow, not an inferred bearish view. Preserve A2 MATURE_AVOID_CHASE as a benchmark
caution even when current specialist timing differs; if it asserts the same
current unresolved timing proposition, record that conflict rather than erase it.

A2 NO_TRADE can **never become OPPORTUNITY** under v1. WATCH is an additional
observation, not reclassification, eligibility override or permission to trade.
An actual improvement statement requires linked earlier captured evidence;
single-snapshot support is described as support, not temporal improvement.
No thresholds or examples are fitted to KAYNES/RELIANCE/HDFCBANK.

## 7. Contradictions, confirmation and epistemics

Keep four independently addressable collections:

1. A2-to-specialist `BaselineAgreement` exactly as emitted, plus cited explanation
   of A3.9's observation state relative to the unchanged benchmark class.
2. Cross-specialist views: compare only same subject/horizon/proposition/semantic
   axis. Opposite price interpretations are direct conflict; constructive company
   quality and poor short-term timing are a cross-domain tension, not contradictory
   facts. Preserve both even if their combination simply produces WAIT.
3. Source/semantic conflicts: disputed values, units, periods, statement bases,
   and PROVIDER_DEFINED/AMBIGUOUS semantics from canonical captured artifacts.
   Do not reconcile raw financial records in A3.9 or merge unlike periods.
4. Authoritative field outcomes: quote existing status, exact confirmed fields,
   mapping quality and unresolved discrepancies. Confirmation of revenue does not
   confirm a thesis, catalyst price impact, full document or all related fields.

Summarize burden as typed flags/counts by class with source-assigned materiality
and affected predicates, not a new weighted severity score. If materiality or
comparability is absent, mark UNKNOWN and prevent unsupported OPPORTUNITY when
it affects a required gate. Do not infer resolution from recency, provider brand,
two agreeing opinions, or an official source's mere existence.

An already-confirmed field may be shown as confirmed, but earlier opposing
interpretations remain historical/active as captured. If active opinion meaning
is stale relative to confirmation and A3.8 did not rerun it, flag a prerequisite
for future orchestration; do not edit or re-infer that opinion. NOT_FOUND does
not prove falsehood. FACT/INFERENCE/HYPOTHESIS remain separate; neither a graph
edge nor a research narrative can independently satisfy factual completeness.

## 8. Completeness and confidence are separate

Expose required/applicable, optional, not-applicable, unknown-applicability,
usable, partial, stale, missing, failed and blocked sets with exact reasons.
If a coverage ratio is rendered, include its explicit numerator/denominator and
policy: usable required facets / applicable required facets. Unknown applicability
is a separate unresolved item, never quietly removed to reach 100%. An empty
required set yields absent coverage, not 100%. A count is not market confidence.

Keep source evidence quality/freshness by family, contradictory-family flags,
and each opinion's `AgentConfidence` and typed confidence basis. Do not average
self-reported, policy-derived and empirically calibrated confidence, or emit a
single synthesized confidence number in v1. Source policy confidence remains
interpretation confidence, not a success probability. Any future externally
calibrated claim remains separately tagged; A3.9 generates none.

Non-F&O derivatives absence and index Fundamental exclusion are not adverse
evidence. Missing Risk, unknown F&O eligibility, denied research and unsupported
financial semantics are different gaps. Optional research denial cannot suppress
existing useful evidence; unresolved material claims still restrict the product.

## 9. Explainability without a report fabric

`IntelligenceReason` carries reason ID/code, category, template ID/parameters,
source opinion/run/claim IDs, detail schema and field locator, cited evidence or
canonical fact IDs, epistemic kind, horizon relevance and matched rule IDs.
Pure workflow-gap reasons instead cite the plan/node/requirement and captured
outcome; they must not manufacture a market evidence citation.

Preserve original specialist reason codes and descriptions; additional A3.9 codes
explain assembly/state restrictions. Deterministic templates can render short
sentences from those fields. No free-form LLM reason generation, new fact,
unsourced top reason or sentiment inference. Sort by restriction category, rule
order and stable IDs; retain every reason in JSON. A view may truncate display
with an omitted count, never discard contrary evidence from the capture.

No web crawl, document retrieval, hyperlink resolver, bibliography service,
natural-language shell or UI in this milestone. Existing citation IDs/locators
are enough for audit and later rendering.

## 10. Public application seam and replay

Implemented placement: `tiaf.service.opportunity_intelligence` with small contract,
contribution, policy, assembly and replay modules. No framework dependencies
belong in the public contracts. Keep A3.8
planner/workflow policy and accepted specialist modules unchanged.

Public API (verification reads the explicit policy snapshot from the capture):

```text
assemble_opportunity_intelligence(validated_request) -> IntelligenceRunRecord
replay_intelligence(capture) -> recorded IntelligenceRunRecord
verify_intelligence(capture) -> DeterministicComparison
```

Only the caller's earlier A3.8 execution can acquire or rerun evidence. The A3.9
assembler accepts no provider, model, AgentRuntime or LangGraph executor handle.
Default/full MVP is no-LLM: zero new provider/model calls, tokens and model cost.
Keep imported A3.8 known usage and held allowances separate from new assembly
usage; do not claim a historical run cost zero merely because synthesis does.

An implementation acceptance helper may load a local capture and print JSON/a
minimal deterministic summary. It is not a UI, live-fetch command, natural-language
interface, HTTP server, batch ranking feature or A8 integration. No `--live` path
is required. Stable consumers use fields, not parsed prose.

Capture input orchestration semantic fingerprint and exact capture checksum,
A2 identity/content availability/fingerprint, active opinion IDs/versions/digests,
all referenced artifacts, contradiction/gap/applicability state, contribution
mapping and complete synthesis-policy snapshot, rule trace and output fingerprint.

The intelligence semantic hash covers the source semantic identity, policy/schema
versions, relevant captured meaning, rule results and canonical output. Sort sets
and keyed collections by documented stable keys; preserve meaning-bearing order.
Exclude only explicitly named assembly operational timestamps/latency and the
self-hash, not nested evidence effective/availability times. Exact capture checksum
retains original bytes/timing independently. Do not change child fingerprint
algorithms to obtain equality or hash adapter-specific operational data into the
public semantic result.

Recorded replay validates/reconstructs input/output and all references. Verification
reruns **only A3.9 pure assembly**, not A3.8, providers or specialists. Missing
content/schema-policy mismatch fails explicitly; a new policy comparison gets
a new record, not a silent migration. Serial/LangGraph-equivalent A3.8 captures
must yield equal A3.9 semantic output even if their exact checksums differ.
Neither mode asserts arbitrary historical availability or fresh model inference.

## 11. Required scenarios and implementation tests

These are architecture acceptance expectations. Actual synthetic captured-input
results are recorded separately in the acceptance study; none are live market claims.
All assume valid captures; unspecified prerequisites are usable unless the case
intentionally removes them. Fixtures must test policy boundaries, not attractive
symbols. Every scenario asserts forbidden A4/A5/A6/A7 fields are absent.

| Case | Required result / retained evidence |
|---|---|
| A. Aligned supported setup | OPPORTUNITY with source quality STRONG/GOOD, complete required coverage, low/moderate Risk and non-NO_TRADE A2; no STRONG_OPPORTUNITY score/vote. |
| B. Strong Technical, weak company | Material adverse company conflict -> CONFLICTED; lesser qualified weakness -> WATCH. Same explicit materiality inputs select the same branch. |
| C. Strong company, poor timing | WAIT on cited timing restriction; company quality does not win over timing and is not discarded. |
| D. Extended/exhaustion risk | WAIT with AVOID_CHASE reason, regardless of a positive trend. CRITICAL Risk independently matches AVOID. |
| E. High material event risk | WAIT; disputed material gate -> CONFLICTED instead; unknown required event coverage prevents OPPORTUNITY. |
| F. Conflicted comparable views | CONFLICTED, both claims retained, qualified bias MIXED; no majority or source winner. |
| G. A2 NO_TRADE with selective support | WATCH only when row 5 conditions hold; A2 NO_TRADE/score/eligibility preserved. Without earlier evidence, do not call it improvement. |
| H. Missing/stale/all-abstaining core | INSUFFICIENT_EVIDENCE, with existing risks and abstention outcomes still shown. |
| I. Plain verified non-F&O equity | Derivatives NOT_APPLICABLE does not lower coverage; other gates decide state. Unknown eligibility is a different fixture. |
| J. Index | Fundamental not required solely because equities need it; supplied benchmark/sector/exposure applicability retained. |
| K. Exact offline replay | Equal output semantic fingerprint, no provider/model/AgentRuntime/framework execution; missing artifacts fail. |
| L. Source timing/adapter/order variation | Operational-only differences and shuffled input order preserve canonical output; changed evidence quality/meaning/policy changes identity. |

The KAYNES 2–6-week narrative in the request is an illustrative target layout,
not a promised WATCH/GOOD/MODERATE result. The accepted A3.8 sparse KAYNES fixture
contains insufficient company/news/relative/sector evidence and explicit Technical
partial coverage; A3.9 must retain those gaps. It cannot print four supportive
domains by borrowing the example. Whether that capture passes core usability
or returns insufficiency is established against the typed facets, not its name.

Test contracts (lists/tuples/JSON/naive-time rejection), wrong input identities,
superseded/reused lineage, stable ordering, applicability and required-gap
denominators, same-proposition versus cross-domain conflicts, source field
confirmation scope, every state rule and overlapping rules, adverse optional
evidence, all-abstain, unknown/stale quality, source confidence separation,
correlated duplicates and summary-only double counting. Negative price-direction
fixtures must not become a sell/PE action or mistake relative outperformance for
positive absolute return. Test A2 complete/absent projection and conflicting
copies, unchanged A2 bytes, reason traceability and deterministic explanations.

Boundary tests block provider/network/model/AgentRuntime execution during assembly
and both replay modes. Assert no new LangGraph/vendor imports in service contracts,
no new authority-bearing fields or metadata escape hatches, no forecast/position/
expression fields. Use full regression and future public local-capture scenarios;
live validation is optional, upstream-only, bounded and separately authorized.

## 12. Internal implementation packages

| Package | Deliverable / exit gate |
|---|---|
| WP1 — Contracts and handoff | Composable request/result/run records; resolve captured A3.8/A2 input, immutable/timezone/JSON validation, no A0 action-contract reuse. |
| WP2 — Contributions/applicability | Nine typed extractors, field/semantic-axis table, required versus optional rules, reused/superseded lineage and no double counting. |
| WP3 — Synthesis policy | Versioned three-valued predicates, ordered rules, qualified bias and all matched reasons; no weights/model dependency. |
| WP4 — Contradictions/completeness/confidence | Preserve all conflict classes and field confirmation scope; explicit coverage denominator; no aggregate probability. |
| WP5 — Explanation projection | Cited structured reason components and deterministic templates, including workflow-gap reasons; no prose inference. |
| WP6 — Replay/fingerprint | Exact capture plus stable semantic identity, recorded replay and pure assembly verification with external execution disabled. |
| WP7 — Public application seam | Small local assembly API and optional acceptance helper; no orchestration bypass, server, ranking or UI. |
| WP8 — User acceptance | Cases A–L, including NO_TRADE, non-F&O, index, qualified/negative bias, sparse KAYNES and replay. |
| WP9 — Hardening | Full regression, boundary/ownership/security checks, documentation and honest acceptance report; hand off to A3.10. |

## 13. Risks, deferrals and next step

Main risks are confusing an observation state with a recommendation; interpreting
different domain stances as votes; treating Quality/Risk as independent evidence;
missing baseline content behind a valid reference; shallow source immutability;
unsupported confidence/confirmation semantics; and tightening classification by
silently changing A3.8 applicability. The contract separations, traceable predicates
and explicit failure tests above are implementation gates for these risks.

The deliberately conservative v1 may return many WATCH/WAIT/INSUFFICIENT results.
Do not tune it to raise opportunity counts. No accuracy/profitability claim follows
from deterministic acceptance. A3.10 handles cumulative Agent replay/comparison/
cost/failure hardening; A4 arbitration, A5 positions, A6 expression, A7 calibrated
forecasting, A8 TM integration, A9 scanners and A10 production operations stay out.
Automatic mappings, arbitrary historical reconstruction and unavailable source
families remain existing deferrals. No deferral-register change is justified.

That was the A3.9 implementation-time disposition. The later focused
sub-milestone discovery audit assigns DEF-053 to cross-candidate A3 analysis and
ranking and DEF-054 to user-facing explanation/citation report rendering. Both
remain outside A3.9 and do not change its accepted single-subject semantics.

The immediate successor was **TIAF_A3.10 — Agent Replay / Baseline Comparison
/ Cost & Failure Hardening**, now accepted at `tiaf-a3.10`. The separate
[A3 closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md) follows without
changing A3.9 semantics.

## 14. Historical architecture-pass validation

The historical results below validate the pre-implementation runtime only.
Current implementation gates are recorded in the acceptance study.

| Command | Observed result |
|---|---|
| `.venv/bin/pytest -q tests/unit/agents tests/unit/market_intelligence tests/unit/planner tests/unit/workflows` | **489 passed** in 22.58s; includes architecture/security, gateway/no-LLM, provider/model/execution isolation, planner and workflow boundary tests. |
| `.venv/bin/pytest -q` | **1,795 passed** in 26.54s. |
| `.venv/bin/python -m compileall src scripts` | Passed. |
| `.venv/bin/ruff check src tests scripts` | All checks passed. |
| `.venv/bin/mypy src tests` | No issues in **418 source files**. |
| `git diff --check` | Passed; the new design file was also whitespace-checked against `/dev/null`. |

During that earlier architecture pass, only this design, README, CHANGELOG and
architecture/roadmap/capability/target indexes changed. Runtime, tests, dependencies, `.env`, accepted interpretation
policies and deferral register are unchanged. No live market/model calls, new
provider integration, A3.9 runtime, commits, tags or pushes were part of that earlier pass.
