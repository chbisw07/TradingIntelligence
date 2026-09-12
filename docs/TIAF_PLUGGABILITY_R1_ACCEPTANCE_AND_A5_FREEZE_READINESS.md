# TI Pluggability R1 Acceptance and A5 Freeze Readiness

## Decisions and scope

Acceptance review: 2026-09-12 (Asia/Kolkata).

**R1 decision: `READY_TO_CLOSE_PLUGGABILITY_R1`.**

**A5 decision: `A5_READY_FOR_FINAL_DOCUMENTATION_AND_FREEZE`.**

**R2–R5 disposition: `R2_R5_NOT_REQUIRED_FOR_A5_FREEZE`.**

This closes the bounded
[R1 implementation](TIAF_PLUGGABILITY_R1_REQUIRED_SCOPE_EXPLICIT_ABSENCE.md)
against the defect demonstrated by the
[A1–A5 compliance audit](TIAF_PLUGGABILITY_A1_A5_COMPLIANCE_AUDIT.md). It is an
offline acceptance and documentation pass. It changes no runtime semantics,
A2/A4/A5 policy, capability binding, or milestone scope. It does not commit,
tag, push, begin A6, or implement R2–R5.

The canonical hierarchy remains `HOT ⇒ COLD ⇒ STRUCTURAL`.

## Acceptance findings

### Scope ownership and registry separation

Planner policy/schema `1.1` pins an explicit nine-role semantic profile. Eight
roles are required; `MACRO` is optional. Request context still controls existing
applicability such as Macro inclusion, DAY company scope, and attributed F&O
eligibility. The policy profile—not `AgentRegistry` membership—owns required and
optional scope.

The concepts are separated as follows:

| Concept | Owner / representation |
|---|---|
| Declared required scope | Pinned `REQUIRED_SPECIALISTS_V1_1` Planner policy |
| Declared optional scope | Pinned `OPTIONAL_SPECIALISTS_V1_1` Planner policy |
| Registered/bound implementations | `AgentRegistry.capabilities()` filtered to the declared IDs |
| Runtime-executable contributors | Planner applicability, authorization, no-LLM, and bound checks |
| Successful contributions | Captured attempts, outcomes, and attributable opinions |

The audit search found no remaining assignment equivalent to
`required_scope = registry.keys()`. Registry expansion with an undeclared role
does not expand the pinned scope or invoke that role.

### Denominator, absence, and optional behavior

The focused acceptance proves a required denominator of `8` both before and
after removing the Fundamental binding. The removed binding is captured as
`NOT_REGISTERED`, `unresolved=true`, `required=true`, with the namespaced gap
`FUNDAMENTAL:NOT_REGISTERED`; the result is partial and cannot appear more
complete through denominator shrinkage.

Existing supported conditions remain distinct:

- `NOT_REGISTERED` and `PERMISSION_DENIED` preserve required absence;
- invocation failure preserves the required node and `FAILED` outcome;
- supported contextual inapplicability remains non-applicable/unknown under its
  existing rule rather than being fabricated as a contribution; and
- missing requested Macro is visible as `OPTIONAL_NOT_REGISTERED` and excluded
  from required numerator/denominator.

There is no separate registry disabled-state facility. R1 does not introduce
one merely for acceptance; adding governed enablement belongs with later COLD
composition ownership if approved.

### Planner, replay, and tamper behavior

- Planner `1.0` reads and verifies historical captures using their recorded
  registry-derived scope and legacy fingerprint projection.
- Planner `1.1` captures all declared roles as selected or explicitly skipped,
  including nested requiredness and compatible schema/policy versions.
- Duplicate roles, omitted roles, schema/policy mismatches, and tampered
  required/optional classification fail closed.
- Recorded replay uses only captured data and never consults today's registry.
- Deterministic verification honors the captured Planner version. A different
  binding set produces a clear mismatch; it does not add or substitute a newly
  installed specialist.
- Old capture bytes and hashes are not rewritten.

### A2–A5 compatibility

- **A2:** no feature, scoring, ranking, policy, fixture meaning, assessment ID,
  or evidence fingerprint changed. A2 remains the deterministic benchmark.
- **A3.9:** Planner `1.1` required absence is applicable-but-unusable and remains
  in required/missing completeness. Optional absence is visible without entering
  the required denominator. Planner `1.0` retains historical projection.
- **A4:** the existing captured projection receives corrected upstream
  missing-required meaning. Challenger, Arbitrator, enrichment, budgets, model/
  provider authority, and replay are unchanged.
- **A5:** domain/evaluation/facade/Shell policies and dependencies are unchanged.
  A5 still consumes immutable A4 lineage and gains no specialist lookup,
  provider, model, broker, or execution dependency.

No substitute opinion, bullish/bearish stance, target, forecast, or evidence is
fabricated for an absent contributor.

## Residual-risk classification

| Residual | Classification | Disposition |
|---|---|---|
| No independent registry disabled-state mechanism | `ACCEPTABLE_FOR_A5_FREEZE` | Existing not-registered, permission, applicability, and failure states cover R1; do not invent configuration semantics during freeze. |
| R2 discovery/readiness metadata | `SHOULD_FIX_BEFORE_A6` | Useful for honest discovery, not required by bounded A5 runtime. |
| R3 composition envelope/pinned verifier | `SHOULD_FIX_BEFORE_A6` | Recorded replay is registry-free; current deterministic verification fails closed when a compatible registry is unavailable. |
| R4 optional adapter import isolation | `SHOULD_FIX_BEFORE_A6` | No A5 correctness dependency; remains bounded cleanup. |
| R5 trusted COLD ownership/configuration | `SHOULD_FIX_BEFORE_A6` | Needed before broader configured composition, not for current static A5 behavior. |
| A5 has not been tagged | `ACCEPTABLE_FOR_A5_FREEZE` | Expected process state; this pass is forbidden to tag. |

No residual is classified `MUST_FIX_BEFORE_A5_FREEZE`.

## Validation

The acceptance pass ran without live broker/provider/model calls:

- R1 focused tests: `8 passed`;
- A3 hardening: `61 passed`;
- A3.9 opportunity intelligence: `65 passed`;
- A4: `37 passed`;
- A4 enrichment: `44 passed`;
- A5: `52 passed`.

- complete repository suite: `2234 passed`;
- frozen A2 baseline/evaluation check: `75 passed`;
- replay, secret, public-boundary, and A5 boundary check: `39 passed`;
- `python -m compileall src scripts`: passed;
- Ruff: passed;
- mypy: passed across `530` source files;
- `python -m pip check`: no broken requirements;
- `git diff --check`: passed;
- documentation: `730` local Markdown links resolved;
- deferral register: `58` sequential records with the documented status totals;
  and
- six R1 runtime modules: zero forbidden provider/model/orchestration-
  framework imports.

## Required follow-on order

1. Save the R1 implementation and this acceptance record to Git.
2. Perform **Documentation Consolidation & Synchronization**:
   create `TIAF_A4_DETAILED_ROADMAP.md`, create
   `TIAF_A5_DETAILED_ROADMAP.md`, update `TIAF_THESIS.md`, and reconcile
   top-level documentation after the pluggability additions.
3. Run the final A5 freeze/tag readiness check.
4. Create `tiaf-a5-baseline` only after that check.
5. Proceed to the next major workstream.

Exact next Codex prompt title:

`TIAF POST-R1 — DOCUMENTATION CONSOLIDATION AND SYNCHRONIZATION`
