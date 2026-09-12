# TI Pluggability R1 — Required Scope and Explicit Absence

## Status and boundary

Implementation and offline acceptance pass, 2026-09-12 (Asia/Kolkata).

**Implementation decision: READY_TO_ACCEPT_PLUGGABILITY_R1**

**A5 impact: A5_FREEZE_BLOCKER_R1_RESOLVED**

The subsequent
[acceptance closure](TIAF_PLUGGABILITY_R1_ACCEPTANCE_AND_A5_FREEZE_READINESS.md)
returns `READY_TO_CLOSE_PLUGGABILITY_R1`,
`A5_READY_FOR_FINAL_DOCUMENTATION_AND_FREEZE`, and
`R2_R5_NOT_REQUIRED_FOR_A5_FREEZE`.

This is the bounded R1 correction identified by the
[A1–A5 pluggability compliance audit](TIAF_PLUGGABILITY_A1_A5_COMPLIANCE_AUDIT.md).
It does not tag A5, start A6, retune A5, introduce plugin loading, or implement
R2–R5. No provider, broker, network, or model call is part of this pass.

## Root cause and invariant

Planner policy previously built dependency specifications only by iterating the
active `AgentRegistry`. A missing binding therefore disappeared from the plan,
the result, and A3.9's required-completeness denominator. Registry membership
was accidentally answering both “what is bound?” and “what is required?”.

R1 establishes this invariant:

> Declared semantic scope comes from trusted versioned Planner policy; the
> registry reports implementation bindings only. Removing a required binding
> cannot remove it from the required denominator.

Planner policy `1.1` declares the nine currently supported specialist roles.
Eight are required by the stable default profile; `MACRO` is optional and is
applicable only when explicitly requested. Existing contextual rules remain:
for example DAY company scope and attributed non-F&O derivatives context can be
not applicable. No caller-controlled authority or new specialist role is added.

## Contracts and captured meaning

`AnalysisPlan`, `SpecialistDependencySpec`, and `SkippedSpecialist` accept
schema/policy versions `1.0` and `1.1`. New runs use `1.1`; the plan's schema,
Planner, policy, registry-spec, and skipped-entry versions must agree. Policy
`1.1` plans must account for every declared role exactly once as either a
selected node or a skipped role.

`SkippedSpecialist.required` is additive and optional for legacy input:

- `True` records a declared required role that could not execute;
- `False` records an optional or contextually skipped role;
- absent/`null` is accepted only as legacy `1.0` meaning.

New policy `1.1` plans reject an unclassified skip. The plan and final result
therefore capture required/optional scope and explicit absence without relying
on whichever registry happens to be installed during replay.

## Absence, failure, and completeness

The existing reason vocabulary is retained. A missing required binding is
captured as `NOT_REGISTERED`, `unresolved=true`, `required=true`, and creates a
namespaced gap such as `FUNDAMENTAL:NOT_REGISTERED`. Permission denial,
no-LLM incompatibility, and the existing specialist cap retain required absence
when they affect a required role. Invocation failure remains a selected required
node with a `FAILED` outcome. None of these cases fabricates an opinion.

An explicitly requested but unbound optional Macro role is recorded as
`OPTIONAL_NOT_REGISTERED`, `required=false`. It remains visible in A3.9 but does
not enter required completeness. A non-requested optional role and existing
contextual exclusions remain not applicable.

A3.9 projects policy `1.1` required absence as applicable-but-unusable. Thus a
missing required binding remains in `required`, `missing`, and the denominator.
Optional absence remains visible in `optional` without changing the required
fraction. Removing an implementation can only leave completeness unchanged or
degrade it; it cannot improve completeness by shrinking semantic scope.

## Replay and legacy compatibility

Recorded replay remains purely capture-driven and performs no registry lookup.
Deterministic verification reads the captured Planner policy version:

- `1.1` reconstructs declared scope and explicit absence;
- `1.0` reconstructs the historical registry-derived plan semantics.

The additive skipped-role field is omitted from the semantic fingerprint
projection of `1.0` records, matching the historical byte meaning. Existing
captures remain readable without rewriting their content or hashes. A3.9 also
uses the captured Planner version: `1.0` skips retain historical completeness,
while `1.1` skips use explicit scope. Expanding the current registry neither
changes recorded replay nor silently expands a new request's declared scope.

Deterministic verification still requires bindings capable of reproducing the
captured invocations. A different binding set causes a clear plan/dependency
mismatch rather than reinterpretation or a live/plugin self-heal.

## Downstream preservation

- A2 evidence pack, assessment reference, and evidence fingerprint pass through
  unchanged; no A2 feature, score, class, threshold, or ranking code changed.
- A4 receives the corrected A3.9 missing-required semantics through its existing
  captured input. Challenger/Arbitrator policies, budgets, and replay are
  unchanged and remain deterministic/provider-free.
- A5 continues to consume immutable A4 lineage. It gains no specialist lookup,
  provider/model dependency, policy change, or execution authority.

## Acceptance coverage

The focused R1 corpus covers:

1. required Fundamental binding removed, stable denominator `8`, explicit
   required absence, partial result, and namespaced gap;
2. optional Macro binding removed, visible optional absence and unchanged
   required numerator/denominator;
3. required invocation failure, stable scope and explicit `FAILED` outcome;
4. required permission denial, stable denominator and missing contribution;
5. undeclared registry expansion, unchanged scope and no invocation;
6. new `1.1` capture/replay/verification and registry-mismatch rejection;
7. legacy `1.0` capture/read/verification and historical denominator `7`;
8. unchanged A2 pack/reference/fingerprint.

There is no general enable/disable facility in the existing A3 registry, so R1
does not invent one merely to create a disabled test. The existing permission,
failure, not-registered, contextual-applicability, and optional-absence paths
exercise the available execution distinctions.

## Deferred work remains deferred

R1 does not implement discovery/readiness descriptors (R2), a cross-layer
composition manifest and pinned verifier resolver (R3), optional adapter import
isolation (R4), or trusted COLD composition ownership (R5). New peer publication
remains DEF-058 and HOT transitions remain DEF-057. Sector Rotation and Signal
Qualification remain thought experiments; A6 has not started.

## Validation

All checks ran offline:

- focused R1: `8 passed`;
- combined affected workflow/A3.9 regression: `112 passed`;
- A3 hardening: `61 passed`;
- A3.9 opportunity intelligence: `65 passed`;
- A4: `37 passed`;
- A4 enrichment: `44 passed`;
- complete repository suite: `2234 passed`;
- additional A2 baseline/evaluation check: `75 passed`;
- additional public-boundary/import/replay check: `32 passed`;
- targeted secret/provider/model/network/replay boundary selection: `2 passed`;
- `compileall`, Ruff, mypy (`530` source files), `pip check`, and
  `git diff --check`: passed;
- `718` local Markdown links resolved; and
- the six changed runtime modules contain zero forbidden provider/model/
  orchestration-framework imports.

No live services or secrets were used.

## Accepted follow-on order

The short R1 acceptance/closure pass is complete. The accepted order is to save
R1 implementation and acceptance to Git, perform the separately scoped
documentation consolidation, run the final A5 tag-readiness check, and only then
create `tiaf-a5-baseline`. Do not fold R2–R5 into that sequence.

Exact next prompt title:

`TIAF POST-R1 — DOCUMENTATION CONSOLIDATION AND SYNCHRONIZATION`
