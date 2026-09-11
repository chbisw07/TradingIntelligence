# Post-A3 Deep Architecture Pass 3 — A4 Challenge / Arbitration Agents

## 1. Decision and scope

**Decision: `READY_FOR_DEPLOYMENT_ARCH_REVIEW`.**

The A4 architecture is approved in
[TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md).
No implementation foundation blocks deployment/consolidation design. The
pass-2 semantic foundation **must still precede A4 runtime implementation**.

Review date: **2026-09-11, Asia/Kolkata**. Entry worktree was clean. HEAD is
`ad5e7a9fedea6efc7a3b9287a6ad1610421c92a9`, the documentation commit establishing
passes 1/2. Accepted runtime/closure remains `tiaf-a3-baseline` at `e690da2`.
`tiaf.arbitration` is still a reserved namespace. No A4/source-foundation runtime,
Shell, provider/model adapter or unrelated TBD capability is implemented here.

The attachment defines this requested design scope, not evidence that proposed
contracts already exist. Repository code and accepted documentation establish
current behavior. No commit, tag, push, live provider/model call or credential
read was performed.

## 2. Inputs reviewed and integration findings

Reviewed [system architecture](TIAF_SYSTEM_ARCHITECTURE.md),
[pass 1](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md),
[source semantics](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md)
and [pass 2](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md);
[A2 baseline](TIAF_A2_FOUNDATION_BASELINE.md) and
[evaluation](TIAF_A2_10_REPLAY_VALIDATION_EVALUATION.md);
[A3 Agent/runtime](TIAF_A3_1_AGENT_FOUNDATION.md),
[gateways](TIAF_A3_2_GATEWAYS_BUDGETS.md),
[Quality/Risk](TIAF_A3_7_DERIVATIVES_OPPORTUNITY_RISK.md),
[Planner](TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md),
[opportunity intelligence](TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md),
[replay/cost/failure](TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md),
[confirmation gateway](TIAF_AUTHORITATIVE_CONFIRMATION_GATEWAY.md),
[deferrals](TIAF_DEFERRAL_REGISTER.md), [roadmap](TRADINGINTELLIGENCE_ROADMAP.md),
[capabilities](TIAF_CAPABILITY_MAP.md) and [targets](TIAF_IMPLEMENTATION_TARGETS.md).

The deployment TBD was inspected only to identify the next review. Its process,
storage and service proposals are not adopted here; other TBDs remain hypotheses.

| Code evidence | Architectural finding |
|---|---|
| [BaselineEngine](../src/tiaf/baseline/engine.py), [A2 replay](../src/tiaf/evaluation/replay.py) | Typed immutable evidence/policy benchmark; A4 must consume it, not rescore or fit it. |
| [Agent protocols](../src/tiaf/agents/protocols.py), [models](../src/tiaf/agents/models.py) | SpecialistAgent and AgentOpinionV2 describe A3 specialist work. Do not force A4 multi-argument arbitration into those result semantics. |
| [Budget](../src/tiaf/agents/budget.py), [reasoning gateway](../src/tiaf/agents/gateways/reasoning.py), [request contracts](../src/tiaf/agents/gateways/contracts.py) | Reusable policy, usage and provider-neutral gateway machinery; request currently requires SpecialistId. A role-aware additive bridge is needed before optional A4 calls, not fake specialist identity. |
| [Opportunity reason/risk enums](../src/tiaf/agents/specialists/opportunity/enums.py) | Existing risk/maturity labels are useful inputs, not automatic hard vetoes or new A4 calculations. |
| [Planner request](../src/tiaf/planner/models.py), [workflow services](../src/tiaf/workflows/services.py) | Current A3.8 enforces no-LLM and captured as-of eligibility. It is not an existing generic A4 model executor; A4-need integration requires a narrow trusted bridge. |
| [A3.9 policy](../src/tiaf/service/opportunity_intelligence/policy.py), [contracts](../src/tiaf/service/opportunity_intelligence/contracts.py) | Observation rules, confidence separation, source locators and dissent already exist. A4 needs distinct challenged-thesis/disposition records, not new fields in the frozen product. |
| [A3.10 replay](../src/tiaf/a3_hardening/replay.py), [cost](../src/tiaf/a3_hardening/cost.py) | Recorded/deterministic/comparison paths and leaf accounting are reusable patterns; no replay re-inference or double-counted nested usage. |
| [Arbitration namespace](../src/tiaf/arbitration/__init__.py) | Placeholder only; architectural approval does not mean runtime exists. |

Two important design repairs are explicit: live escalation must create a later
as-of successor, not violate A3.8's captured-time check; and A4 optional reasoning
must not disable A3.8's no-LLM validator or impersonate a SpecialistId.

## 3. Role disposition

**Two roles are sufficient initially.** An Agent is a bounded actor, not a
required LLM or separately deployed process.

| Candidate role | Decision | Result |
|---|---|---|
| Thesis Challenger | `KEEP` | One unified Challenger, deterministic first, optional model proposals. |
| Counter-Thesis Agent | `MERGE` | Counter-thesis is a typed output/objective of the Challenger, not another default model invocation. |
| Evidence / Assumption Critic | `MERGE` | Deterministic evidence/premise checks and optional assumption discovery inside the Challenger; pass-2 projection owns source semantics. |
| Risk Challenger | `MERGE` | Challenge supplied A3.7 risk premises and asymmetries; do not recreate the specialist. |
| Arbitrator | `KEEP` | Explicit accountable role with deterministic rules, preserved dissent and separate result. No model required. |
| Research Escalation Decider | `MERGE` | Materiality/evidence-need policy plus existing Planner authorization/execution. Reject a standalone research-manager Agent. |

No split is needed. A mandatory bullish/bearish cast, debate moderator,
multi-model voting panel and recursive supervisor hierarchy are rejected for
the initial A4 scope. A counter-thesis need not recommend an opposite trade.

## 4. Reasoning-pattern comparison

These are engineering judgments, not measured claims of model performance.

| Pattern | Quality/explainability | Cost/correlation | Determinism, replay and failure isolation | Verdict |
|---|---|---|---|---|
| A: challenge then arbitrate | Clear argument sequence; risks unnecessary calls if unconditional | Moderate; Challenger/Arbitrator can echo premises | Good with typed captures and separate stages | Useful sequence inside chosen pattern, not mandatory model calls |
| B: multi-thesis debate | Potential breadth, but discussion can obscure decisive evidence | High; repeated models/roles still share evidence and can amplify errors | Recorded replay possible; many failure/termination paths | Reject as default; no evidence here justifies the complexity |
| C: skeptic gate then selective model challenge | Explicit deterministic checks plus optional new hypotheses | Low default, bounded extra cost; argument/source lineage remains explicit | Strong no-LLM control, isolated optional failure, simple replay | **Chosen primary pattern**, ending with explicit arbitration |
| D: hierarchical coordinator/challengers/arbitrator | Clear sounding ownership but duplicates workflow management | Highest role/coordination overhead and correlation risk | More state, failures and replay surface without current benefit | Reject initial hierarchy; reuse existing Planner instead |

The chosen deterministic Arbitrator handles declared structured argument rules.
It does not pretend to prove arbitrary prose. Unsupported novel arguments remain
unevaluated; material unresolved reasoning may require ABSTAIN/CONFLICTED rather
than an artificial winner. No average, majority, prestige or universal source rank.

## 5. Contracts, challenge and arbitration summary

Input is the pass-2 `A4SemanticInputProjection`: unchanged A3.9/A3.8/A3.10 and A2
refs, opinions, typed evidence/claims, scoped authority, independence, disputes,
confirmation, revisions, missingness, usage/cost and policy/as-of/grants.
Required integrity failures stop admission; missing optional facts stay gaps.

The minimal typed set is ArgumentPremise, InvestmentThesis (also used for the
counter-thesis), ChallengeFinding, ArbitrationFinding, ResidualUncertainty,
A4EvidenceNeed and A4Result/run record. References resolve to exact typed values
and scope; merely citing a real ID cannot validate a fabricated claim about it.
Assumptions, support/opposition, invalidation conditions and provenance remain
structured. Proposed types are not yet code.

Eight challenge families cover evidence coverage, source basis (with authority/
dependence/ambiguity/confirmation qualifiers), freshness, assumption support,
thesis tension, risk constraint, timing/maturity and baseline divergence. Original
A3 reason codes and pass-2 relation categories remain referenced, not overwritten.

Arbitration separates deterministic hard-stops from reasoning judgment. Compare
material premises, domain/horizon applicability, scoped evidence and explicit
argument defeat, not role counts. A supported counter-thesis must be answered or
preserved. Lowest risk does not automatically win; risk veto requires an explicit
applicable constraint. Model confidence cannot clear that constraint.

## 6. Dispositions and downstream ownership

A4 can downgrade A3 OPPORTUNITY or qualify/upgrade WATCH with supported resolution
of its barriers, while preserving the original product. Its seven proposed
dispositions are SUPPORTIVE, WAIT, NO_TRADE, AVOID, CONFLICTED, ABSTAIN and
INSUFFICIENT_EVIDENCE. They are decision-intelligence states, not order actions.

NO_TRADE retains a known applicable deterministic prohibition, including A2
NO_TRADE in the initial policy. Contextual support can remain in the result but
cannot override it. AVOID needs supported adverse invalidation or a true risk
veto, not merely missing data. WAIT names a remediable condition. CONFLICTED
means materially opposed supported views; INSUFFICIENT_EVIDENCE lacks required
premises; ABSTAIN means a scope/process/rule limitation prevents adjudication.
Fatal integrity/arbiter failure yields no valid domain result, not supportive
fallback. All coexisting reasons remain visible beside the primary disposition.

A5/A6 receive surviving thesis, disposition, risks, invalidation, uncertainty,
evidence state, horizon/objective and audit refs. No position action, chosen
option or execution instruction is supplied by A4. A7 forecasts may later be
admitted with calibration/model/target/PIT provenance; A4 does not create or
calibrate probabilities. L0 sources -> L1 normalized evidence -> L2 features ->
L3 A2 baseline -> L4 specialists -> L5 opportunity -> **L6 A4** -> L7 A5/A6;
A7 is an overlay and TM/broker authority stays outside TI's intelligence ladder.

## 7. Escalation, modes, replay, failure and cost

Default: no live escalation, no model calls. Explicitly granted initial policy:
at most one evidence escalation round/two review cycles, one optional Challenger
model call per cycle/two total, zero Arbitrator model calls. Parent token/tool/
cost/deadline ceilings remain finite and binding across child work. These are
transparent engineering caps, not tuned market thresholds.

A4 asks a semantic question; Planner/gateways own acquisition/normalization and
affected reruns. The bridge must not create another planner or nested budget
reset. Stop on no useful semantic information, duplicate needs, unavailable
capability, denial, deadline, budget or round limit. No evidence is no resolution.
New live evidence requires a new as-of capture; upstream A1/A2 own any necessary
baseline refresh. A4 cannot retroactively edit A2 or backdate an acquisition.

NO_LLM is the hard model prohibition, DETERMINISTIC_ONLY the supported default
profile; SELECTIVE_REASONING requires grants and a configured gateway;
DEEP_REASONING remains unavailable initially. Actual prompt/model/config/schema/
policy identities, outputs, validation and usage are captured. No production
adapter is supplied here and DEF-052 is not closed.

Model outputs replay as recorded artifacts. Deterministic verification checks
surrounding rules/projections; model/prompt/policy changes are explicit new
comparison runs, never silent re-inference. Keep original-run and replay usage,
leaf calls and parent reservations separate. Unknown monetary/late usage is not
zero. A timeout does not prove a synchronous worker stopped or release all holds.

Required challenge failures block favorable conclusions; Arbitrator failure is
terminal. Optional model failure may return an independently complete pre-model
deterministic result only under declared fallback policy, with degradation and
unchanged disposition, never by removing dissent. Invalid IDs/schema/value claims
are rejected, not evidence. Partial required coverage cannot count as agreement.
The authoritative architecture contains the full failure/disposition table.

Evidence quality, specialist confidence basis, ordinal thesis support, challenge
severity, residual arbitration uncertainty and future calibrated probability
remain separate. Structured findings explain thesis survival, rejected arguments,
evidence, remaining assumptions and what would change the result. Shell explain/
trace can later render them; DEF-054 remains a presentation boundary.

No Agent gets credentials, provider/registry/URL/browser/shell/SQL/broker handles.
Source text is untrusted data. Natural language/model output cannot raise grants
or override hard constraints. One logical result path serves future consumers.

## 8. Designed acceptance corpus

These are **proposed future A4 fixtures**, not implemented or executed A4 tests.
Pin source policies, A2/A3 captures, model fixtures, budgets and clocks. Every
case must preserve originals and expose an attributable decision trace; all
model/provider behaviors should be deterministic fixtures before bounded live
acceptance is separately authorized. Do not fit thresholds to named stocks.

| # | Case | Expected result / assertion |
|---|---|---|
| 1 | Clean bullish thesis, eligible A2, complete applicable evidence, no material undefeated challenge | SUPPORTIVE; cite required premises and challenge coverage, no execution advice. |
| 2 | A3 OPPORTUNITY relies on a critical ambiguous source basis | INSUFFICIENT_EVIDENCE, with source/semantic challenge; original A3 state unchanged. |
| 3 | Copied news appears to supply multiple confirmations | SAME_ROOT/derived lineage, no support inflation; if independent confirmation is essential and absent, remain insufficient. |
| 4 | Positive fundamentals, poor technical timing, otherwise supported thesis | WAIT with timing condition and cross-domain tension, not majority-positive or automatic AVOID. |
| 5 | Two comparable equally applicable authoritative fields conflict materially | CONFLICTED; no source-brand winner, all assertions retained. |
| 6 | A2 NO_TRADE plus A3 contextual support | NO_TRADE, contextual thesis visible; no A2 override or history rewrite. |
| 7 | Essential catalyst is stale | INSUFFICIENT_EVIDENCE with freshness reason; stale evidence is not automatically negative. |
| 8 | Critical required evidence missing | INSUFFICIENT_EVIDENCE, explicit need/gap, no fabricated premise. |
| 9 | Supported counter-thesis refutes a substantive essential primary premise | AVOID with explicit defeat relation; not instruction to short. If neither defeats the other, CONFLICTED. |
| 10 | Optional model Challenger unavailable | Identical complete deterministic control with explicit degraded fallback if policy allows; required model-stage variant ABSTAIN. Failure cannot improve disposition or erase admitted dissent. |
| 11 | NO_LLM execution | Full challenge/arbitration path works, zero model calls/tokens/cost; retain known versus unknown provider cost distinction. |
| 12 | Escalation returns reordered/copy evidence, no useful information | Stop after the admitted round, preserve unresolved issues and cumulative usage, no repeated call loop. |
| 13 | Captured scope clarification removes an apparent mismatch | Resolve by scope without deleting originals; re-evaluate affected findings only. SUPPORTIVE requires all other gates and no A2 prohibition. |
| 14 | Model invents claim ID or cites valid ID with wrong value | Reject invalid proposal with validation lineage/cost, no admitted fact or supportive upgrade. |
| 15 | Conflicting rule/model Challenger findings | Treat as opposed arguments; apply scope/premise rules or retain CONFLICTED, never confidence/role voting. |
| 16 | Exact recorded replay | Same semantic result/fingerprints, no provider/model call; verify surrounding deterministic rules independently. |
| 17 | New policy/prompt/model comparison | New comparison identity, recorded old artifacts unchanged; no claim of exact original replay. |
| 18 | Budget stop before required challenge completes | ABSTAIN/PARTIAL or already established non-support constraint; preserve held/unknown usage and gaps, no positive consensus. |

Additional boundary cases: missing/corrupt projection and failed Arbitrator yield
no valid result; post-cutoff acquisition creates a successor; loop caps survive
nested Planner work; denied authority/source-text injection cannot invoke tools;
strict monetary caps cannot be claimed enforced against unknown prices; missing
full A2 evidence cannot be reconstructed from its score; output overflow preserves
incomplete status rather than silently truncating dissent. These should accompany
the 18-case core matrix at implementation acceptance.

## 9. Pre-A4 foundation governance

Recommend one named **POST_A3_PRE_A4_FOUNDATION** implementation package rather
than calling it the first reasoning sub-milestone of A4. This preserves pass 2's
"before A4 runtime" gate and keeps a reusable source foundation distinct from
Agent reasoning. It adds no new numbered major milestone and is not implemented.

| Foundation work package | Acceptance boundary |
|---|---|
| Identity and scoped authority | Source/document/claim identities and explicit policy bindings; no global source score. |
| Comparability, independence and dispute history | Typed deterministic relations with unknowns, lifecycle and immutable original refs; same-provider conflicts and source echoes covered. |
| Confirmation and A4 input projection | Scope-aware field reliance over all retained documents; preserves recorded gateway status and exposes limitations; no last-write-wins truth. |
| Capture/replay and contract validation | Deterministic projections, schema/policy fingerprints, all pass-2 proposed fixture cases, no live fallback or A3 hash changes. |

After that gate, separately authorize A4 runtime contracts, deterministic roles,
bounded Planner-need bridge, failure/replay/cost acceptance. Optional model-backed
execution requires a role-aware gateway bridge and approved configured provider/
privacy/pricing/validation policy; no new adapter is bundled by implication.

DEF-003 local facade, DEF-052 production models, DEF-054 citation UX and DEF-055
pricing remain separate obligations. The immediate foundation and A4 reasoning
are planned work, not new deferred A3 capabilities. Do not change stable IDs,
close those records or renumber the A-roadmap for this design decision.

## 10. Mandatory complexity audit

1. **Too many Agents?** Two logical roles suffice; deterministic subchecks are
   functions/policy, not additional Agent services.
2. **Minimum useful roles?** One Challenger and one explicit Arbitrator preserve
   critique versus disposition accountability without six-person debate.
3. **Deterministic coverage?** Admission, source/scope checks, missingness,
   freshness, rule challenges, risk/authority gates, escalation, validation and
   conservative dispositions already cover the safety-critical baseline.
4. **Model value?** New structured counter-explanations and assumptions where
   typed rules alone cannot propose them. Value is a hypothesis to evaluate, not
   a reason for unconditional model calls or model-led truth selection.
5. **Duplicate specialists?** No: consume A3.7/A3.9 facts/reasons, test their
   premises and implications; do not recalculate indicators or reissue specialist
   opinions under different names.
6. **Duplicate Planner?** No: semantic evidence needs feed its existing boundary.
   A bounded use-case sequence is not a new scheduler, route engine or supervisor.
7. **Explicit Arbitrator needed?** Yes as a policy/result/accountability role,
   not necessarily a model, process or framework node.
8. **Would multiple models be theater?** Without incremental validated arguments,
   yes. Different model names and repeated answers are not independent evidence.
9. **What waits?** Debate ensembles, model Arbitrator, deep mode, calibrated
   weighting, public facade, Shell, citation UX, new adapters, databases, durable
   queues and deployment topology. Only small versioned records/bridges needed by
   actual A4 behavior should be implemented.

## 11. Validation and exact next prompt

Existing relevant regression command:

```bash
.venv/bin/pytest -q \
  tests/unit/agents/test_reasoning_gateway.py \
  tests/unit/agents/test_gateway_architecture_security.py \
  tests/unit/agents/test_opportunity_specialists_a37.py \
  tests/unit/workflows/test_orchestration.py \
  tests/unit/opportunity_intelligence/test_integrity_boundaries.py \
  tests/unit/a3_hardening/test_replay_comparison.py
```

**106 passed in 24.69s.** These validate existing A3 gates/contracts, not a new
A4 implementation or the proposed acceptance corpus. Documentation validation:

- **169 local Markdown link targets checked; none missing.**
- `git diff --check` passed; new files separately passed whitespace, final-newline
  and code-fence checks (ordinary git diff excludes untracked files).
- All nine changed files are Markdown: two new documents and seven index/roadmap
  updates. No runtime, script, test, dependency or configuration changed.
- Deferral register is byte-for-byte unchanged: 55 unique sequential IDs,
  43 DEFERRED, 3 PLANNED, 4 IMPLEMENTED, 3 REJECTED and 2 SUPERSEDED.
- Source semantic architecture, pass-1/pass-2 reviews and deployment TBD are
  unchanged against entry HEAD. HEAD and accepted-baseline ancestry are unchanged.

Created this review and
`docs/TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md`.
Updated `README.md`, `docs/ARCHITECTURE.md`, `docs/README_TBD_DESIGN_NOTES.md`,
`docs/TIAF_CAPABILITY_MAP.md`, `docs/TIAF_IMPLEMENTATION_TARGETS.md`,
`docs/TIAF_SYSTEM_ARCHITECTURE.md` and `docs/TRADINGINTELLIGENCE_ROADMAP.md`.
Full runtime gates/live tests were not rerun for this documentation-only pass.
No commit, tag or push was performed.

**Exact next Codex prompt title:**

**Post-A3 Deployment Architecture Review — Capability Hosting, State Isolation
and Operational Boundaries**

Review the deployment TBD before full post-A3 consolidation. Keep it architecture-
only, preserve logical source/authority/replay semantics, and do not assume this
pass implemented source foundations, A4 roles, models or Shell.
