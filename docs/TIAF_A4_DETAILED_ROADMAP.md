# TIAF A4 Detailed Roadmap

## 1. Status and document map

**A4.1/A4.2 accepted and frozen at `tiaf-a4-baseline` (`494d968`).** This is
the post-R1 consolidated roadmap, not a new A4 implementation or acceptance run.
Historical studies retain their then-current capabilities and test counts.

| Stage | Governing record | Delivery / acceptance |
|---|---|---|
| Architecture | [A4 design](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md), [pass-3 decisions](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md) | Approved bounded L6 roles; optional model lane remains deferred. |
| Prerequisites | [Source foundation](TIAF_POST_A3_PRE_A4_FOUNDATION.md), [local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) | Implemented before A4; source comparability and trusted captured-read admission. |
| A4.1 | [Implementation](TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md) | [Acceptance](STUDY_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION_ACCEPTANCE.md): deterministic thesis/Challenger/Arbitrator, dispositions, replay and facade. |
| A4.2 | [Implementation](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md) | [Acceptance](STUDY_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE_ACCEPTANCE.md): one-round governed Planner bridge and successor lineage. |
| Closure | [A4 major closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) | Historical READY_TO_FREEZE_A4, followed by the baseline tag. |
| Later consumers | [Shell v0.1](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md), [A5 roadmap](TIAF_A5_DETAILED_ROADMAP.md) | Separate accepted slices, not retroactive A4 features. |

## 2. Architecture basis

A4 consumes integrity-validated semantic projections over frozen A2/A3 captures.
[Source semantics](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md)
govern field-level authority, proposition comparability, source independence,
PIT availability, revisions and preserved disputes. A4 interprets these records;
it never invents facts, recalculates indicators or repairs A2/A3 inputs.

The deterministic implementation is the benchmark for future higher-order/model
work. Challenger identifies supported critique; Arbitrator resolves findings
under explicit rules. No voting, averaged confidence, model prestige or
source-brand score substitutes for evidence.

## 3. A4.1 delivered deterministic slice

`tiaf.a4` constructs one primary thesis and at most one supported counter-thesis.
Premises distinguish FACT, INFERENCE and ASSUMPTION with validated references
and acyclic dependencies. Findings retain opposition, materiality, dissent,
invalidation conditions and residual uncertainty.

Eight challenge families cover evidence coverage, source basis, freshness,
assumption support, thesis tension, risk constraint, timing/maturity and baseline
divergence. Baseline policy `1.0` checks A2 NO_TRADE first, followed by risk veto,
required evidence, incomplete review, material conflict, timing, surviving thesis
and no-supported-thesis rules. No retuning occurs in this roadmap.

| Domain disposition | Meaning |
|---|---|
| NO_TRADE | Applicable deterministic prohibition; captured A2 NO_TRADE retained. |
| AVOID | Explicit risk veto/invalidation, not a sell instruction. |
| INSUFFICIENT_EVIDENCE | Required scope/source/evidence support unavailable. |
| ABSTAIN | Incomplete, unsupported or out-of-policy review. |
| CONFLICTED | Material opposed supported theses remain unresolved. |
| WAIT | Plausible thesis with a remediable timing/freshness condition. |
| SUPPORTIVE | Supplied thesis survived bounded checks; not permission to trade. |

Execution COMPLETE/PARTIAL/FAILED and per-finding ADMITTED/REJECTED/QUALIFIED/
UNRESOLVED remain separate. Failure never improves a market opinion. A4.1 uses
zero provider/model calls and known-zero leaf model cost, retaining parent usage.
`a4.evaluate@1.0` validates one authorized FOUNDATION_CAPTURE and its subject/
objective/horizon/`as_of`, then delegates unchanged logic. It is CAPTURED_READ,
not public live enrichment.

## 4. A4.2 delivered governed open-world slice

Immutable A4EvidenceNeed describes a material semantic question, parent identity,
scope/PIT/authority requirements, dedupe and remaining budget/deadline—not a
provider preference, URL, tool command or trade instruction. Six closed semantic
capabilities cover confirmation, fundamentals, events/news, sector/macro,
derivatives and bounded no-model research.

`tiaf.a4_enrichment` is an application bridge outside A4 domain contracts.
Deterministic admission may admit or explicitly deny authority/budget/policy,
duplicate, unsupported, immaterial, late or already-resolved needs. Existing
A3.8 Planner/controlled services own execution. The bridge forces no-LLM and at
most one enrichment/replan/attempt/provider call; it neither resets remaining
parent budget nor refunds unknown usage.

Model priors may motivate hypotheses under the architecture, but this delivered
bridge is no-model. Research must be sourced, normalized, provenance-linked,
authority-qualified and PIT-admitted before becoming canonical evidence. No
unbounded research loop or public/live facade operation exists.

## 5. Successors and conservative stops

Workflow-side SuccessorEvidenceCapture supplies typed normalization crosswalks,
new/reused evidence references and exact workflow/cost lineage. A valid successor
has a later cutoff and new projection/run identity, retaining frozen A2/A3
parents, old evidence and dissent. Finding lineage distinguishes preserved,
recomputed, resolved and new findings; arbitration examines the full successor.

NO_NEW_INFORMATION creates no successor. Missing/ambiguous evidence, denial and
failed acquisition remain conservative stops. Changed price/market-state or
specialist inputs produce UPSTREAM_REFRESH_REQUIRED: refresh upstream separately,
never patch old A2/A3 facts. No backdating or erasure of disagreement is permitted.

## 6. Replay and acceptance evidence

A4Capture and A4EnrichmentCapture retain exact inputs/policies/results, checksums,
semantic fingerprints and admission/successor chains. Recorded replay reconstructs
captured output; deterministic verification reruns captured logic; policy
comparison creates a distinct labeled evaluation. Corrupt/incompatible captures
fail without live repair. Tuple collections/JSON arrays and aware Asia/Kolkata
timestamps remain unchanged.

The linked studies and major closure cover dispositions, source/PIT scope,
no-model behavior, bounded enrichment, facade admission and replay/failure
integrity. They are synthetic/captured evidence, not live-market calibration or
profitability validation. Their original counts are not fresh results for this
documentation pass.

## 7. Pluggability, downstream seams and deferrals

[R1 acceptance](TIAF_PLUGGABILITY_R1_ACCEPTANCE_AND_A5_FREEZE_READINESS.md)
fixes upstream required-scope omission under Planner `1.1`, preserving legacy
`1.0` replay. It neither revises A4 policy nor recomputes historical projections.
New captures expose required absence; presence never grants authority.
[Pluggability architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md) governs future
descriptor/pinning/COLD improvements without claiming R2–R5 implemented.

A5 consumes A4 lineage with supplied position truth. A6 will separately construct
and select valid expressions. Future A7 calibrated evidence may inform a versioned
comparison of valid candidates, not move expression/forecast authority into A4.
TM retains operational actions.

DEF-052/055 retain optional model challenge/pricing. That lane requires role-aware
admission, approved adapter, privacy/egress, versioned structured prompts, ID/value
checks, budgets, no-LLM control, replay and evaluation. It is not an A4/A5 freeze
prerequisite. DEF-003 retains remote/live publication; DEF-054 retains rich reports
beyond the separately delivered Shell; DEF-049/050/051 retain historical PIT,
durable replay and scheduled outcomes. No deferral closes here.

**A4 documentation set: complete** across design, prerequisites, A4.1/A4.2,
acceptance, closure and this roadmap. The
[implementation roadmap](IMPLEMENTATION_ROADMAP.md) owns today's next task;
historical next-step text remains historical.
