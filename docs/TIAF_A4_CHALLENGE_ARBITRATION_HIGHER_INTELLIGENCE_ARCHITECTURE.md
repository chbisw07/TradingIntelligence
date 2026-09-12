# A4 Challenge, Arbitration and Higher-Intelligence Architecture

## Status and authority

The [A4 detailed roadmap](TIAF_A4_DETAILED_ROADMAP.md) is the consolidated
navigation for architecture, implemented A4.1/A4.2, acceptance and frozen closure.
Later A5/R1/monitoring work does not expand this deterministic A4 baseline.

**Approved architecture, post-A3 pass 3, 2026-09-11 (Asia/Kolkata).** Its first
runtime slice is now implemented by
[TIAF_A4.1](TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md). The prerequisite
[source-semantic foundation](TIAF_POST_A3_PRE_A4_FOUNDATION.md) remains a
separate accepted layer. The [pass-3 review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md)
records the alternatives, acceptance corpus and foundation gate. This design
operates beneath [TI_CORE/capability architecture](TIAF_SYSTEM_ARCHITECTURE.md)
and the approved [source semantics](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md).
It does not replace accepted A2/A3 policies or promote unrelated TBDs.

The deterministic contracts, taxonomy and default arbitration limits described
below are implemented in A4.1. The separately bounded
[A4.2 bridge](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md) implements the
no-model evidence-acquisition/successor passages; optional model execution
remains future architecture. Frozen A2/A3 enums are unchanged. No provider/model
adapter, Shell or execution path is delivered by this document or A4.1.
The [A4 major closure review](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
accepts these two runtime slices as one freeze-ready deterministic A4 baseline
while retaining the model lane as an optional separately gated enhancement.

## 1. Responsibility and intelligence hierarchy

A4 tests whether an underlying thesis survives evidence-linked challenge. It
adds assumption testing, counter-thesis, dispute prioritization, bounded evidence
needs, arbitration of supported interpretations and residual uncertainty. A3
still owns specialist interpretation and the opportunity observation product.
The objective remains understandable, replayable reasoning in the user's economic
interest, not attractive examples or a claim of demonstrated profitability.

| Level | Ownership | Boundary |
|---|---|---|
| L0 | Raw sources/providers | Native capture and access-controlled acquisition. |
| L1 | A1 and MI normalized evidence | Identity, source/provenance, time, quality and semantic admission. |
| L2 | A2 features/indicators and other deterministic evidence subsystems | Factual derivations, not new A4 calculations. |
| L3 | A2 deterministic market-state/baseline | Immutable benchmark score/class/direction and component evidence. |
| L4 | A3 specialists | Independent attributed interpretations, including Quality/Risk. |
| L5 | A3.9 opportunity intelligence | Structured observation, conflicts/gaps and original A2 relationship. |
| L6 | A4 challenge/arbitration | Auditable surviving/qualified/refuted theses and disposition. |
| L7 | Future A5/A6 | Position advice and trade expression; operational authority still belongs to TM, execution truth to broker. |

A7 forecasting/evaluation is an overlay feeding validated evidence and assessing
outcomes, not a replacement rung. A4 never calculates ATR/RSI/Greeks, rewrites A2,
reruns specialists itself, selects CE/PE/expiry/strike/quantity, sets execution
targets/stops, manages a position, generates forecasts or places orders.

## 2. Minimum Agent taxonomy and chosen pattern

Use **two logical roles**, not two required model calls:

- **Thesis Challenger:** unified evidence/assumption/risk critique and a bounded
  counter-thesis. Deterministic checks first; optional model proposals only where
  an unresolved interpretive question justifies them.
- **Arbitrator:** explicit accountable role consuming the input, all admitted
  arguments and dissent. Its initial implementation is deterministic, using
  versioned admissibility, defeat and disposition rules. It is not another market
  specialist and does not choose a source by brand or a thesis by confidence.

No separate evidence critic, risk challenger, counter-thesis model, research
decider or supervisor is needed initially. Research materiality/needs are policy
outputs; A3.8 retains planning, routing and execution scheduling.

Primary pattern: **skeptic gate then selective model challenge**, followed by
explicit arbitration. It has the useful sequence of challenge-then-arbitrate
without a mandatory multi-turn debate or a hierarchy of supervisor Agents.

```text
validated A4 semantic projection
  -> deterministic evidence/constraint checks + initial thesis/challenges
  -> complete deterministic arbitration result (preserved benchmark)
  -> optional bounded model challenge proposals, if authorized and useful
  -> schema/reference/premise validation -> deterministic arbitration
  -> final result, or typed material evidence need
       -> existing Planner/gateway boundary (at most one admitted round)
       -> successor capture/projection -> affected checks -> final result
```

Execution order is a small application use-case sequence, not a second Planner.
An initial deterministic result is retained even when a later enriched result
differs. It is an A4 no-LLM control, not a replacement for the immutable A2
benchmark. Two roles remain separately attributable even if hosted in one process.

## 3. Deterministic versus model-backed reasoning

Deterministic ownership includes source/PIT/integrity admission, comparison and
dispute projection, scoped authority, lineage qualification, missing/critical
evidence, materiality, rule-based challenges, budget/permission checks, hard
constraints, deterministic abstention, argument validation and final state rules.
It consumes pass-2 semantics; it must not implement a different source taxonomy.

Optional models can propose alternative explanations, hidden assumptions,
cross-domain counterarguments and semantic evidence needs; they may explain
structured comparisons. Models may not invent claim IDs/values, scope, sources,
independence, calibrated probability, thresholds, authority or resolving evidence.
Free prose is not enough to alter a disposition. Proposals must map to typed
premises/relations and declared challenge rules; unrepresentable novel arguments
remain explicitly unevaluated hypotheses or gaps, not accepted findings.

No role inherently requires a model. One Challenger may use a model while the
Arbitrator remains deterministic. An explicitly admitted request may require
completion of its selective reasoning stage; failure then cannot silently fall
back as if that requested stage completed. Such a request is incompatible with
NO_LLM and must be rejected at admission if it also prohibits models.
A future model-assisted arbitrator would be a separately
versioned, evaluated extension with the same hard gates; it is not approved as
the initial arbiter of disposition. No vendor/model prestige is a decision input.

## 4. Input contract and safe integration seams

Consume the approved conceptual `A4SemanticInputProjection`: A3.9 state/reasons,
resolvable A3.8/A3.10 captures, active/superseded opinions, unchanged A2 baseline,
typed claims/evidence, authority and independence relations, dispute/confirmation/
revision views, missing/stale/partial evidence, usage/cost and policy/profile/
authority/as-of identities. Capture source-policy versions and explicit unknowns.

Reject missing/corrupt mandatory integrity/identity before reasoning. Optional
missing content remains an attributed gap. A projection-only A2 capture cannot
support a premise requiring uncaptured facts. No raw provider payload, credentials,
router, parser, registry, browser, shell, SQL or arbitrary URL handle enters A4.

Reuse AgentBudget/AgentUsage, cited evidence and reasoning-provider ports; do not
force the entire A4 workflow into `SpecialistAgent.analyze`/AgentOpinionV2.
That protocol describes one A3 specialist, not challenged thesis arbitration.
A4 role IDs are distinct from A3 SpecialistId; do not impersonate TECHNICAL or
repurpose a reserved specialist ID to bypass validation.

Current `ReasoningGatewayRequest` requires a SpecialistId and A3.8 request
validation requires no-LLM mode. Before optional A4 model execution, a narrowly
versioned role-aware gateway request/adapter is needed, reusing the existing
authorization/accounting machinery and preserving A3 callers. The existing
gateway cannot be described as an already callable generic A4 actor API.
Likewise the A4-need-to-Planner bridge is future integration work, not a claim
that current A3.8 accepts arbitrary A4 nodes. No weakening of A3 validators.

## 5. Small structured argument/result contracts

Compose typed records; retain all original evidence/opinion/dispute IDs. A4 adds
its own IDs/schema/policy fingerprints instead of editing old records.

| Design role | Minimum content |
|---|---|
| `ArgumentPremise` | Premise ID; fact/inference/assumption role; admitted claim/evidence and typed field locator; polarity and proposition/comparison refs; source qualifications; support state TRUE/FALSE/UNKNOWN and reason. Values resolve from evidence, not model copies. |
| `InvestmentThesis` | Thesis ID/version; parent A3/A2 refs; subject/objective/horizon; underlying directional interpretation where supplied; premise IDs; conclusion relation/rule; support/opposition; assumptions, gaps, risks and invalidation conditions. |
| Counter-thesis | Same thesis type with `role=COUNTER` and opposed thesis/argument refs. No duplicate model class or forced bearish recommendation. A timing/WAIT alternative is valid. |
| `ChallengeFinding` | Finding ID; challenged premise/thesis; governed category; materiality/severity; cited support/opposition and dispute refs; affected conclusion/rule; finding disposition and evidence need/invalidation refs. |
| `ArbitrationFinding` | Issue/thesis/argument refs; admitted/rejected/qualified/unresolved decision; rule/policy ID; decisive evidence/conditions; reason and preserved dissent. Rejection requires more than a confidence comparison. |
| `ResidualUncertainty` | Affected thesis/premise; known limitation versus unknown; materiality; consequence for disposition; evidence/change that could resolve it; unresolved need refs. |
| `A4EvidenceNeed` | Subject, semantic attributes/claim/field, horizon and evidence cutoff; finding/dispute refs, purpose/materiality and expected resolvable question; dedupe key, permitted scope and remaining budget reference. No provider name preference or transport command. |
| `A4Result` / run record | Original and successor capture refs; run/projection/policy/model identities; disposition and execution status separately; primary/counter/surviving thesis refs; findings/dissent/uncertainties; invalidation conditions; original A2/A3 views; usage/failures, explanation trace and replay fingerprint. |

Use bounded typed invalidation predicates such as "supplied premise no longer
holds" or "eligible revision contradicts field X". A reference to a supplied
technical level is evidence, not an invented stop, target or execution trigger.
Unknown future values are not filled in. Hypothesis assumptions and invalidation
conditions are explicit. No universal confidence/score field is required.

Validation resolves every referenced ID/path in the admitted projection, checks
predicate/value meaning and scope, and validates support edges—not just whether
an ID string exists. An LLM citing a real RSI fact while misstating its value
fails validation. Argument dependency cycles and unsupported fact promotion are
rejected; typed inference remains inference. Repeated equivalent arguments have
one issue identity with all origin refs retained, not multiple votes.

## 6. Challenge taxonomy and correlation safeguards

Use eight A4 issue families with existing child reason codes preserved:

| Family | Included source/specialist findings |
|---|---|
| EVIDENCE_COVERAGE | Critical/optional missing evidence and insufficient comparison scope. |
| SOURCE_BASIS | Scoped authority weakness, dependence, semantic ambiguity and missing applicable confirmation; distinct qualifiers remain visible. |
| FRESHNESS | Stale catalyst, expired evidence or PIT/revision ineligibility. |
| ASSUMPTION_SUPPORT | Unsupported premise, hypothesis promoted to fact, or invalid inference dependency. |
| THESIS_TENSION | Cross-domain tension or a supported counter-thesis, using pass-2 relation kinds. |
| RISK_CONSTRAINT | Cited risk asymmetry/constraint; not automatically a veto because Risk says HIGH. |
| TIMING_MATURITY | Supplied extension/chase/room/maturity conditions, no recalculation. |
| BASELINE_DIVERGENCE | Matched A2/A3 axes; divergence is an issue for explanation, not automatic error. |

Family, severity, materiality and disposition are separate. Severity is an
ordinal policy label, not probability. Use actual A3.7 codes such as
EVIDENCE_STALE, EVIDENCE_INSUFFICIENT, RISK_ROOM_LIMITED and
OPPORTUNITY_BASELINE_NO_TRADE as original reason refs; do not reinterpret their
thresholds. Avoid one new category for every provider or market pattern.

Same/different model calls do not imply independent evidence or independent
truth. Give roles distinct objectives but one admitted evidence boundary. Preserve
their shared inputs/model identities and all opposing arguments. Arbitration uses
evidence-linked premises, applicability and explicit defeat reasons; neither
argument count, role count, average confidence nor model majority decides it.
Multiple copies can add explanation lineage, never support strength by counting.

## 7. Arbitration procedure: hard constraints versus judgment

1. Validate projection/capture, authority and policy. Resolve required source
   comparisons before accepting factual premises. Source class alone is not proof.
2. Record deterministic hard constraints and evidence coverage. A hard-stop must
   have an explicit rule ID, applicable predicate and cited input—not be inferred
   from the Risk specialist's label or a model adjective.
3. Build the primary thesis from admitted typed A3 propositions and the unchanged
   A2 view. Build at most one distinct supported counter-thesis for the bounded
   initial policy; all additional issues remain as findings/dissent, not votes.
4. Evaluate each material premise/attack: supported, refuted, qualified or unknown.
   Inspect whether it is required for that thesis and which scoped argument it
   actually defeats. Facts, assumptions and interpretation cannot substitute for
   each other. No generic scalar weighting of quality or risk.
5. A thesis survives only when required premises are supported, essential
   assumptions are justified or explicitly conditional, applicable hard gates
   pass and every material counterargument has a supported disposition. A
   material untested assumption cannot be waved away by the Arbitrator.
6. Prefer one thesis only with a specific defeat/qualification reason: invalid
   premise, inapplicable horizon/domain, resolved scope conflict or a declared
   argument rule supported by evidence. If two opposed theses remain supported
   and materially undefeated, record CONFLICTED. Do not choose by source brand,
   risk minimum, model prestige, statement length or arbitrary tie-break.
7. Emit the disposition and residual uncertainty, with all evaluated rule matches
   and dissent—not only the winning reason. A budget-driven stop is not victory.

The initial deterministic policy can only arbitrate argument forms with declared
rules. Material novel reasoning beyond those rules is UNEVALUATED and cannot
support an upgrade. This bounds explainability rather than pretending formal
checks prove every natural-language inference. A future rule expansion needs
versioning and regression cases, not tuning to live symbols.

## 8. Output/disposition semantics

A4 output is distinct from A3.9 observation state and A0 action-bearing
OpportunityAssessment. SUPPORTIVE means a thesis survived the bounded review,
not ENTER/BUY/SELL or execution approval. Record status (COMPLETE, PARTIAL,
FAILED) separately from domain disposition; fatal input/arbiter failure emits
no valid domain result. Preserve all concurrent constraints even when a single
primary disposition is selected.

Default disposition precedence, evaluated after input integrity checks:

| Condition | Disposition and meaning |
|---|---|
| Known applicable deterministic prohibition, including A2 NO_TRADE | NO_TRADE. Contextual thesis support may remain visible, but initial A4 policy cannot override the benchmark prohibition. |
| Known explicit risk-admissibility veto or conclusively invalidated substantive primary thesis (not merely a reversible timing premise) | AVOID. Adverse evidence for this candidate/horizon; not an instruction to sell or select the opposite trade. |
| Required source/evidence/scope premise unavailable | INSUFFICIENT_EVIDENCE. Cannot substantiate the required question; list missing evidence. |
| Required challenge stage incomplete or question outside supported arbitration rules | ABSTAIN. Deliberate inability to adjudicate; distinguish process/policy scope from lack of source data. |
| Material opposing supported theses or unresolved same-proposition conflict | CONFLICTED. Evidence exists, but no justified resolution; not consensus or averaged neutral. |
| Thesis plausible but an explicit remediable timing/readiness condition remains | WAIT. Cite the condition that would change the result; not a promise it will occur. |
| Required checks complete; supported thesis survives; no material undefeated blocker | SUPPORTIVE. Preserve qualifications and non-material residual uncertainty. |
| No supported thesis and no stronger justified disposition | ABSTAIN with explicit reason, never default SUPPORTIVE. |

Primary precedence is reporting policy, not deletion of findings. For example,
NO_TRADE with a critical gap retains both; the gap is not resolved by that label.
A confirmed scope mismatch is not automatically CONFLICTED. If A2 content is
missing, do not fabricate NO_TRADE or clearance; the result is insufficient unless
another independently supported restriction already establishes non-support.

A4 may downgrade A3 OPPORTUNITY when assumptions/source basis do not survive.
It may produce SUPPORTIVE from A3 WATCH only when all original material barriers
have an evidence-backed disposition, the A2 gate permits it and the new conclusion
is explicitly A4's versioned interpretation. More favorable prose, extra votes
or removal of failed challengers is insufficient. A3/A2 records never change.
If new evidence changes the A2 assessment, that is a linked new upstream run,
not an A4 override of the original A2 NO_TRADE.

## 9. Evidence escalation, budget and information time

**Bounded open-world reasoning:** a model/Agent may identify a material gap,
formulate a hypothesis and request evidence beyond the initial bundle. Model
prior knowledge can motivate a question but is not canonical factual evidence.
Unverified hypotheses must be marked as such, linked to a material question and
kept separate from premises claiming facts; never invent a source/claim ID to
make a new hypothesis look evidenced. Unknown/out-of-coverage questions remain
unmet, not answered from model memory. Existing factual premises still require
resolvable admitted IDs and typed value/scope validation.

Governed acquisition -> provenance/normalization/authority/entitlement/PIT
admission -> successor semantic projection -> selective re-challenge/arbitration
is the only route from newly found information to decision evidence. No model
or source text acquires directly, executes instructions or raises permissions.
This amendment makes the existing escalation intent explicit; it does not add
calls, loosen limits, implement a provider/model, or allow unbounded recursion.

A4 emits semantic needs; A3.8's Planner/application boundary determines whether
they are applicable, authorized, affordable, satisfiable and worth scheduling.
Existing gateways/MI choose routes, source validation and normalization. No A4
Agent knows provider transport or performs its own acquisition/planning loop.

Generic initial engineering bounds (not empirically optimized trading values):

- Default captured/no-LLM mode: **zero live escalation and zero model calls**.
- Explicitly authorized enrichment: **at most one escalation round**, yielding
  at most two projection/review cycles. No recursive A4-inside-A3-inside-A4 loop.
- Optional reasoning: at most **one Challenger call per cycle, two total**;
  zero Arbitrator model calls. Mode/grants/budget can only reduce those limits.
- At most two thesis roles (primary/counter). Finding/response size has an explicit
  finite schema/request bound; overflow is reported as incomplete review, never
  silently truncated dissent followed by SUPPORTIVE.
- Tool, token, configured cost-unit and elapsed/deadline ceilings must be finite
  and explicitly granted for enabled work; no unbounded default or implicit
  second budget after escalation. Existing stricter child limits still apply.

Deduplicate needs by subject, semantic question/comparison, projection fingerprint
and policy. Deduplicate challenges by affected premise/category/cited roots,
retaining origins. Repeated provider wrappers, reordered evidence or changed
wording are not useful new information. Stop on unchanged relevant semantic
evidence/qualification, no eligible capability, denial, insufficient budget,
deadline, settled material issues or the round cap. Reassess only affected
findings; preserve prior immutable versions and supersession links.

Do not reset A3.8's internal limits per successor to multiply the parent allowance.
Reserve nested calls against one parent allowance and count actual leaves once;
an A3 reservation and its contained MI calls are not two billed acquisitions.
Strict live-call limits must be enforced at the actual adapter-call boundary;
an opaque callback with internal calls is not evidence of a per-HTTP-call cap.
Unknown/late usage remains held/unknown; timeout does not prove a worker stopped.
No automatic retry or budget refund for an uncooperative synchronous worker.

**As-of rule:** reprojecting already captured eligible evidence can retain the
same cutoff. A live acquisition after the original cutoff requires a successor
analysis/capture with a new as-of and explicit parent link. Never backdate new
evidence into the original projection; A3.8 already rejects future acquisition.
If the successor needs refreshed A1/A2, approved upstream composition owns that
new run. A4 emits a rebase need or stops; it neither recalculates A2 nor silently
combines new facts with an invalid stale baseline. Wall-clock deadlines and
evidence cutoffs are different fields. Historical replay has no live escalation.

Unavailable/no-new evidence retains unresolved need/failure lineage and uses the
disposition rules, not a manufactured resolution. A costly source is not a more
authoritative one. Materiality determines attention, not a numerical truth score.

## 10. Model policy and failure/degradation

NO_LLM is an explicit prohibition; DETERMINISTIC_ONLY is the initial reasoning
profile. They are orthogonal controls, not competing permissions. SELECTIVE_REASONING
may use the Challenger gateway only after deterministic triggers and authorization.
DEEP_REASONING is reserved/unavailable in the initial A4 policy: no hidden extra
Agents/calls or stronger model merely because a caller chooses the word "deep".

Capture actual model/provider/config identity, prompt content reference and
version/digest, task/input/output schemas, tool schema where applicable, policies,
requested/actual tiers, role/version, supplied input fingerprint, full accepted
structured output, validation decisions, calls/tokens/cost knowledge and failures.
Operator configuration selects a permitted model, never the model itself.
Absent monetary prices remain UNKNOWN/UNPRICED, distinct from known-zero no-LLM
usage; a strict monetary ceiling cannot be claimed satisfied by unknown pricing.

| Failure/degradation | Required behavior |
|---|---|
| Missing/corrupt required projection/capture | Fail closed; no validated A4 result and no live reconstruction. Legitimate optional missing fields remain typed gaps. |
| Deterministic Challenger fails | Required stage incomplete: ABSTAIN/PARTIAL if a valid input/result envelope can be formed; no favorable result. Known independent hard restrictions may still produce non-support with failure retained. |
| Optional model unavailable, times out or exceeds budget | Use the already complete deterministic result only if the accepted policy declared that stage optional and no admitted material finding remains unhandled. Record degraded/partial model path. Otherwise ABSTAIN; never improve disposition because the call failed. |
| Invalid schema, fabricated ID/value or unsupported assertion | Quarantine rejected output, preserve safe validation/cost audit; no finding becomes evidence. No model repair/retry unless separately budgeted within the same fixed call cap. |
| Partial Challenger set or output overflow | Missing required coverage prevents SUPPORTIVE. Retain all admitted findings; no vote denominator shrinks. |
| Escalation unavailable/denied/no new evidence | Stop once, preserve gap and current conservative disposition; no presumed confirmation. |
| Deadline/unknown late usage | Stop admission, keep reservations/failure refs; no late result silently replaces finalized output. |
| Arbitrator exception/invalid output | Terminal failure with no validated disposition; do not promote a Challenger view or silently return A3 as "arbitrated." |

A complete NO_LLM result may independently be SUPPORTIVE; that is not positive
consensus inferred from a failed optional call. It must be identical to the
recorded pre-model baseline for that projection, explicitly labelled fallback,
with missing model coverage disclosed. Once a valid material model challenge is
admitted, its absence from later work cannot erase it. An optional model's failure
cannot be used to clear an existing WAIT/CONFLICTED/INSUFFICIENT/NO_TRADE condition.

## 11. Replay, confidence and explanation

Reuse A3.10 parent-manifest/content-addressed patterns with a future A4 schema,
not new fields injected into frozen A3 manifests. Persist all projection cycles,
theses, arguments, dispositions, escalation outcomes, rejected/accepted model
outputs and their lineage, policy identities and original A2/A3 refs.

Recorded replay reconstructs historical model outputs without model invocation.
Deterministic verification checks surrounding admission, argument/reference
validation, policy and disposition logic over captured outputs/inputs; it does
not prove the truth of free prose or regenerate it. New model/prompt/config/policy
comparison is an explicitly authorized new run referencing the original. Preserve
child hashes and separate original usage from replay usage. Missing content or
unsupported policy/schema remains an integrity/verification limitation, not a
live/model fallback. Equivalent graph/serial scheduling must not alter semantics.

Keep evidence quality, specialist confidence basis, ordinal thesis support,
challenge severity, arbitration uncertainty and later A7 calibrated probability
separate. Proposed support states are SUPPORTED/CONDITIONAL/REFUTED/UNDETERMINED;
they are not percentages. Residual uncertainty is an issue inventory with
consequences, not a probability. No averaged confidence or universal scalar.

Explainability is structured: which thesis survived; which was challenged; which
counter-thesis was considered; which premises/evidence mattered; which arguments
were rejected or qualified and by which rule; remaining disputes/assumptions;
invalidation conditions; and why the selected non-action/disposition applies.
Retain trace/claim/source locators for future Shell explain/trace without a new
citation renderer or hidden model-generated rationale replacing those records.

All contract times are aware Asia/Kolkata via ZoneInfo, reject naive input and
emit +05:30 JSON. Final semantic collections are tuples/JSON arrays; defensive
validation preserves safety around extensible legacy metadata. Schemas, policies,
package release, model/prompt and facade versions remain distinct.

## 12. Downstream seams and security

A5/A6 receive surviving thesis, disposition, risks, invalidation conditions,
uncertainty, evidence state, horizon/objective and replay identity. A4 conditions
are analytical predicates, not position commands or chosen option contracts.
TradeMonitor retains operational authority; broker state is not inferred from TI.

After A6 candidate contracts and A7 forecast admission/calibration exist, a
separately versioned higher-order comparison may assess which **A6-produced
valid candidate** expresses the surviving thesis under admitted forecast/risk
evidence. A6 retains candidate creation/validation and expression selection
contracts; A7 retains probabilistic models/calibration; A5/TM retain position
advice/operational governance. Comparison preserves candidate/forecast IDs,
assumptions, alternatives and non-action; it cannot synthesize missing contracts,
compute Greeks/payoffs or invent probabilities. This future A6/A7 seam is not
initial A4 scope and does not erase any owner or grant broker authority.

A4 can flag forecast-dependent uncertainty. Later A7-supplied forecasts require
admitted model/target/horizon/availability/calibration provenance and pass-2
epistemic roles. No A4-generated success probability, forecast distribution,
parameter learning or outcome leakage. A7 can evaluate A4 versus immutable A2
and deterministic A4 controls without retraining on A4's own prose as truth.

All Agents remain bounded actors. Caller grants intersect operation/policy/data
permissions and budget; no NL, model, source text or evidence need can increase
authority. Source/model text is untrusted data, never executable instructions.
No shell, SQL, arbitrary URL/browser, provider registry, credentials or broker
handles cross the boundary. Engineering access is explicit and sanitized, not
permission to rewrite captured evidence or bypass policy.

## 13. Governance and implementation gate

The [consolidated transition plan](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md)
now defines exact foundation work packages/acceptance and selects foundation ->
narrow local facade/lifecycle -> deterministic A4. Internal projection work has
no facade dependency; no remote service is required. Historical pass-3 next-step
wording is superseded by this transition plan, not rewritten retroactively.

The accepted [POST_A3_PRE_A4_FOUNDATION](TIAF_POST_A3_PRE_A4_FOUNDATION.md) is
the required package beneath A4 runtime, not an A4 reasoning sub-milestone. It
delivers only pass-2 source identity/authority, comparability, dispute lifecycle,
independence, confirmation projection, semantic input/capture and scoped policy
bindings with deterministic fixtures and replay tests. The separately accepted
[local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) exposes its bounded
projection/replay seam and now includes the additive A4.1 `a4.evaluate`
capability. Neither prerequisite itself implements A4 roles, Shell, adapters,
citation UX or source scoring.

The [A4.1 implementation](TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md)
completes deterministic contracts/challenge/arbitration and its bounded replay/
failure acceptance. [A4.2](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md)
adds the separately governed one-round Planner evidence-need bridge and later
successor replay. Optional model execution is conditional on a separately
approved role-aware gateway bridge,
configured adapter/privacy/pricing policy and evaluation; it is not required to
accept deterministic A4 and does not close DEF-052 merely by defining contracts.
The [review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md)
defines the original design corpus and complexity guardrails. This architecture
document itself authorizes no implementation or dependency.
The [major closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) is the current
freeze-readiness authority and recommends `tiaf-a4-baseline` only after the
reviewed implementation is committed; this architecture text does not create
that tag.
