# TIAF_A4.1 — Deterministic Challenge and Arbitration

## Status and scope

TIAF_A4.1 implements the first bounded L6 runtime under `tiaf.a4`. It consumes
one integrity-validated `A4SemanticInputProjection`, constructs an attributable
primary thesis and at most one supported counter-thesis, applies eight
deterministic challenge families, and resolves the result through an explicit
versioned arbitration policy.

This is the no-LLM benchmark for future A4 work. It does not acquire evidence,
call a provider or model, rerun A2/A3, choose a trade expression, manage a
position, forecast a probability, or exercise broker authority. `SUPPORTIVE`
means only that a supplied underlying thesis survived this bounded review.

The accepted [A4 architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md),
[source-semantic foundation](TIAF_POST_A3_PRE_A4_FOUNDATION.md), and
[local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) remain the governing
boundaries.

## Runtime package

The package is deliberately small and provider-neutral:

| Module | Responsibility |
| --- | --- |
| `contracts.py` | Immutable thesis, premise, finding, uncertainty, result, usage, failure, capture, replay, verification and comparison contracts |
| `enums.py` | Closed challenge, support, arbitration, disposition, status and failure vocabularies |
| `thesis.py` | Admitted-reference validation, dependency-cycle rejection and bounded primary/counter construction |
| `challenges.py` | Deterministic challenges and provider-neutral evidence needs consumed by the separate A4.2 bridge |
| `arbitration.py` | Finding-by-finding decisions and ordered domain disposition |
| `policy.py` | Exact supported policy identities and rule order |
| `evaluation.py` | Integrity gate, deterministic pipeline, output validation and semantic/run fingerprints |
| `replay.py` | Captured recorded replay, deterministic verification and policy comparison |

No A4 module imports provider, model, broker, remote-service, A5, A6 or A7
runtime code.

## Contracts and explainability

`ArgumentPremise` records role (`FACT`, `INFERENCE`, `ASSUMPTION`), polarity,
support state, scope/horizon relevance and typed references to admitted claims,
evidence, reasons, propositions, comparisons, source qualifications and premise
dependencies. Fact premises must resolve to factual admitted assertions; every
claim/proposition/evidence edge is cross-checked. Unknown hypotheses cannot be
promoted to facts, and dependency cycles fail closed.

`InvestmentThesis` preserves its role, parent A2/A3/A3.9 identities,
subject/objective/horizon, supplied directional interpretation, premise and
assumption references, support/opposition, gaps, risks, invalidation conditions,
conclusion relation and construction policy. Exactly one primary thesis exists.
A counter-thesis exists only when captured material opposition, risk dominance,
or an explicit timing alternative supplies its basis; there is never more than
one.

`ChallengeFinding`, `ArbitrationFinding`, and `ResidualUncertainty` retain what
was challenged, cited inputs/disputes, materiality/severity, finding status,
decisive rule/evidence, dissent, consequence and what would resolve the issue.
`A4Result` retains both theses, all premises/findings/uncertainties, original
A2/A3 identities, invalidation conditions, policy identities, execution status,
domain disposition, zero-model usage, failures, and its semantic fingerprint.
It contains no universal confidence, probability or trade-action field.

All contracts are frozen. Semantic collections are tuples in Python and arrays
in JSON. Datetimes reject naive values, normalize with
`ZoneInfo("Asia/Kolkata")`, and serialize with `+05:30`.

## Challenge taxonomy

The closed A4 taxonomy is:

1. `EVIDENCE_COVERAGE`
2. `SOURCE_BASIS`
3. `FRESHNESS`
4. `ASSUMPTION_SUPPORT`
5. `THESIS_TENSION`
6. `RISK_CONSTRAINT`
7. `TIMING_MATURITY`
8. `BASELINE_DIVERGENCE`

The Challenger consumes, without recalculation, projection gaps, A3.9 gaps,
A2 projection availability/class, scoped authority limitations, source
independence, comparability, dispute state, evidence freshness/quality,
epistemic roles, and captured A3.9 state/reasons. Original child reason and
dispute IDs remain cited. Resolved scope differences remain non-material and do
not become artificial conflict.

A material unresolved question may create an `A4EvidenceNeed`. A4.2 finalizes
that domain message with parent run/projection identity, semantic capability,
claim/predicate/field scope, evidence characteristics, authority/source-role,
budget/deadline, dedupe and policy lineage. It still has no route, provider
preference, transport, tool, model, broker or execution method. The separate
[A4.2 application bridge](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md)
may admit and execute it through A3.8.

## Arbitration policy

The default policy identity is `a4-policy:deterministic-baseline` version `1.0`.
Challenge and arbitration policies are independently identified. Exact policy
objects are validated; an unknown or modified policy fails rather than silently
falling back.

The ordered rules are:

1. `A2_NO_TRADE`
2. `RISK_VETO`
3. `REQUIRED_EVIDENCE`
4. `INCOMPLETE_REVIEW`
5. `MATERIAL_CONFLICT`
6. `TIMING_CONDITION`
7. `SURVIVING_THESIS`
8. `NO_SUPPORTED_THESIS`

Arbitration records an explicit admitted, rejected, qualified or unresolved
decision for each challenge. It does not count votes, average confidence, score
source brands, or choose by model prestige. Material opposed theses that both
survive remain `CONFLICTED`.

Domain disposition and execution status are separate:

| Disposition | Meaning |
| --- | --- |
| `NO_TRADE` | An applicable deterministic prohibition, including captured A2 `NO_TRADE`; A4.1 cannot override it |
| `AVOID` | A known explicit risk veto or conclusive substantive invalidation; never a sell instruction |
| `INSUFFICIENT_EVIDENCE` | Required source/evidence/scope support is unavailable |
| `ABSTAIN` | Review is incomplete, unsupported, or outside the declared deterministic policy |
| `CONFLICTED` | Material opposed supported theses/disputes remain unresolved |
| `WAIT` | A plausible thesis retains an explicit remediable timing/freshness condition |
| `SUPPORTIVE` | Required deterministic checks completed and the primary thesis survived without a material blocker |

Execution status is separately `COMPLETE`, `PARTIAL`, or `FAILED`. A failed
input, thesis, or arbitration stage produces no valid favorable result. A
deterministic Challenger failure can return only a `PARTIAL`/`ABSTAIN` record
with a typed failure and residual uncertainty. A material unevaluated issue
outside the declared rule vocabulary likewise records
`UNRESOLVED_REQUIRED_RULE`, `PARTIAL`, and `ABSTAIN`; it cannot be treated as a
completed favorable review.

## A2/A3 preservation and usage

A4.1 validates and references the captured projection. It never writes to or
reconstructs frozen A2/A3 records. The original A2 assessment/evidence and A3
package/A3.9 fingerprints remain visible in the result and capture. A4 may
downgrade an A3 `OPPORTUNITY`; it may qualify a `WATCH` as `SUPPORTIVE` only if
no material blocker survives. A2 `NO_TRADE` remains the first hard gate.

Every A4.1 run records zero provider/model calls, zero input/output tokens and
known-zero model cost. Parent usage references and inherited cost-knowledge
entries are retained without another debit.

## Fingerprint and replay semantics

The result semantic fingerprint covers all semantic result fields except its
content-derived ID and the fingerprint itself. The stable run ID covers the
input projection fingerprint and exact policy, allowing emitted needs to cite
their parent before the result exists. The run fingerprint covers that ID, the
input projection fingerprint, exact policy and result fingerprint; operational
evaluation time is excluded, so an unchanged deterministic rerun has the same
identity.

`A4Capture` binds exact serialized projection and run checksums to their semantic
fingerprints and parent identities. Recorded replay reconstructs the accepted
run without executing logic. Deterministic verification reruns the captured
policy/input and compares run fingerprints. Policy comparison is explicitly a
successor evaluation, not replay; the comparison-only `1.1-comparison` identity
proves that policy changes create a different run even when the disposition is
unchanged. Missing or corrupt data fails closed, and no replay path has live or
model fallback.

## Facade integration

The stable local surface now includes `a4.evaluate`. Its typed request admits
exactly one authorized `FOUNDATION_CAPTURE` logical reference. The facade
replays and validates the captured projection, checks subject/objective/horizon/
`as_of`, delegates to the deterministic evaluator, and returns the A4 result and
run fingerprint. Callers cannot inject a policy. The descriptor declares
`CAPTURED_READ`, deterministic replay, no model support, known-zero cost and the
distinct `EVALUATE_A4` authority scope.

This remains local Python. It adds no transport, live acquisition, dynamic
dispatch, provider/model handle, or broker authority.

## Deferred boundaries

The following remain outside A4.1:

- public/live facade exposure of the internal A4.2 Planner bridge;
- optional role-aware/model-backed Challenger execution and DEF-052;
- Shell/report/citation presentation;
- position intelligence, option expression and forecasting/evaluation;
- remote services, persistence changes and operational deployment; and
- TradeMonitor/broker authority.

Acceptance evidence is recorded in
[the A4.1 acceptance study](STUDY_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION_ACCEPTANCE.md).
