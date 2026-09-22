# Implementation Roadmap

This is the **near-term forward queue**, subordinate to the intended major order
in the [development roadmap](TRADINGINTELLIGENCE_ROADMAP.md). The
[milestone ledger](MILESTONES.md) owns actual status/tags and the
[README](../README.md) is the executive dashboard. Status: 2026-09-22
(Asia/Kolkata); historical reviews retain their original then-next decisions.

Current gate: [one-shot protected 2025 final-holdout evaluation](TIAF_A7_FF1_ONE_SHOT_PROTECTED_2025_FINAL_HOLDOUT_EVALUATION.md)
is **FF1_FINAL_HOLDOUT_ACCEPTED**; scientific result **INSUFFICIENT_EVIDENCE**
(`CONFIDENCE_NONDECISIVE`). All 249 intended origins paired, all support gates
passed, captured replay MATCH, **3,445** tests passed. 2025 is **CONSUMED**,
evidence **COMPLETE**, executions used **1**. No further opening, refit, retry,
threshold change or automatic promotion. Logistic remains CHALLENGER / EXPERIMENTAL.

Exact next separately requested task:
**TIAF A7 / FF-1 — INDEPENDENT FINAL SCIENTIFIC CLOSURE AND BASELINE DECISION**.

Historical checkpoints below retain their then-current SEALED/NOT_RUN states and
then-next tasks. They do not authorize reuse of the now-consumed holdout.

Development checkpoint: [FF-1.4 development-only paired evaluation](TIAF_A7_FF1_4_DEVELOPMENT_ONLY_PAIRED_BASERATE_VS_LOGISTIC_EVALUATION.md)
completed 969 paired 2021–2024 observations and offline reconstruction MATCH.
Development gates pass; classification **INSUFFICIENT_EVIDENCE**. Keep 2025
**SEALED**, final evidence **NOT_RUN**. **FF1_4_ACCEPTED**; its full-suite checkpoint
was **3,327 passed**, not a new full run in the subsequent documentation review.
The [fifth-fold preparation](TIAF_A7_FF1_PRE_HOLDOUT_FIFTH_FOLD_ARTIFACT_PREPARATION_AND_AUTHORITY_RECONCILIATION.md)
has now supplied the model/scaler/BaseRate handoff missing at the preserved
independent review: one empirical fit, 1,690 training rows, replay MATCH.
**FIFTH_FOLD_PREPARATION_COMPLETE**; **3,351** repository tests pass.
Preparation itself did not authorize opening or freeze the final protocol.
The [final-holdout freeze review](TIAF_A7_FF1_FINAL_HOLDOUT_PROTOCOL_FREEZE_REVIEW_WITH_FIFTH_FOLD_HANDOFF.md)
now returns **FF1_READY_FOR_FINAL_HOLDOUT**: handoff RESOLVED, final evaluation
authorized YES, protocol frozen YES; **3,414** tests pass and both closures
replay MATCH. 2025 remains SEALED, final evidence NOT_RUN, execution slot unused.
Next separately requested:
**TIAF A7 / FF-1 — ONE-SHOT PROTECTED 2025 FINAL-HOLDOUT EVALUATION**.
No second fit, post-holdout refit, holdout opening, tuning, calibration or promotion
is authorized by preparation. Execution must use the now-frozen protocol and
durably consume its single claim before any protected numeric access; no retry.
The earlier FF-1.1A queue below is historical.

```text
A5: FROZEN (`tiaf-a5-baseline`)
  → R2 (ACCEPTED / DONE)
  → R3 (ACCEPTED / DONE) → R4 (ACCEPTED / DONE)
  → R5 (ACCEPTED / DONE — BEFORE_A6)
  → A6 (ARCHITECTURE ACCEPTED / THESIS ACCEPTED)
  → A6.1 CONTRACTS / ADMISSION / POLICY ACCEPTED / DONE
  → A6.2 EVALUATION / RANKING / REPLAY ACCEPTED / DONE
  → A6.3 FACADE / SHELL ACCEPTED / DONE → A6.4 ACCEPTED / DONE
  → A6 FROZEN (`tiaf-a6-baseline`) → A7 ARCHITECTURE ACCEPTED / IMPLEMENTATION IN_PROGRESS (FF-0 AND FF-1.1 ACCEPTED) → A8 → A9 → A10
```

R1 is ACCEPTED. [R2 Discovery Metadata](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA.md)
is [accepted](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA_ACCEPTANCE.md). R1–R5 form the
**cross-cutting pluggability remediation / hardening track**, not A5.x. R2–R5
do not block A5 freeze. See the
[R-series ledger](MILESTONES.md#cross-cutting-pluggability-remediation-track-r1r5)
for scope and evidence. This queue is intended execution order, not a claim of
new technical dependencies between all R items.

TIAF evolves through small, gated increments. `TIAF_TGT0` establishes the
engineering baseline. `TIAF_A0` and `TIAF_A1` then define contracts and trusted
data before `TIAF_A2` supplies a deterministic reference implementation.

Interpretive capability arrives in `TIAF_A3`, followed by arbitration in
`TIAF_A4`. Position management and option expression are introduced separately
in `TIAF_A5` and `TIAF_A6`. Evaluation becomes a dedicated capability in
`TIAF_A7` before external integration with TradeMonitor (`TIAF_A8`) and scanners
(`TIAF_A9`). `TIAF_A10` completes production hardening.

After the frozen A4 baseline, the approved
[command-first TI_SHELL architecture](TIAF_TI_SHELL_ARCHITECTURE.md) is now
delivered by a
[small unnumbered local engineering interface](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md)
before A5. It is useful but not an A5 prerequisite and adds no NLP, Web, model,
live-acquisition or broker authority.

The [A5 architecture](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md) is now
implemented by the bounded
[A5.1 baseline](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md): immutable
additive contracts, deterministic single-open-position advice, monitoring intent
and captured replay. The additive
[A5.2 publication slice](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md) exposes it
through position-scoped logical-artifact admission and the bounded Shell. It
still does not include live TM/broker integration, multi-leg interpretation,
scheduling, A6/A7 or remote transport.
The [A5 major closure review](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md) reviews
both slices together and concludes `READY_TO_FREEZE_A5`; it recommends but does
not create `tiaf-a5-baseline`. The subsequent
[TI Pluggability Architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md) is complete
as architecture only. The [completed compliance audit](TIAF_PLUGGABILITY_A1_A5_COMPLIANCE_AUDIT.md)
found one pre-freeze issue: registry absence silently shrank required specialist
coverage. The bounded [R1 remediation](TIAF_PLUGGABILITY_R1_REQUIRED_SCOPE_EXPLICIT_ABSENCE.md)
now preserves stable declared scope, explicit absence, and old/new capture
compatibility. The subsequent
[acceptance closure](TIAF_PLUGGABILITY_R1_ACCEPTANCE_AND_A5_FREEZE_READINESS.md)
closes R1 and finds A5 ready for final documentation and freeze. The
[post-R1 consolidation](TIAF_POST_R1_DOCUMENTATION_CONSOLIDATION_AND_SYNCHRONIZATION.md)
now completes documentation synchronization. The subsequent
[final readiness check](TIAF_A5_FINAL_FREEZE_TAG_READINESS_CHECK.md) returned
`READY_TO_TAG_A5`; documentation commit `167c51d` and annotated tag
`tiaf-a5-baseline` were then pushed. A5 is FROZEN. No
A5 policy changed. R2–R5 are separately bounded pre-A6 work and are not A5
freeze requirements. A6.2 is internal only; this workstream does not renumber
milestones or implement a plugin framework. R4 is now
[implemented](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION.md) and
[accepted](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION_ACCEPTANCE.md);
R5 is [implemented](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md) and
[accepted](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION_ACCEPTANCE.md).
The R1–R5 hardening track is closed. The
[A6 architecture](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md)
and [reconciliation record](TIAF_A6_RECONCILIATION_RECORD.md) are independently
[accepted](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md);
A6.1 is [accepted and done](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION_ACCEPTANCE.md).
A6.2 is [accepted and done](TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY_ACCEPTANCE.md),
A6.3 is [ACCEPTED / DONE](TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE_ACCEPTANCE.md),
A6.4 is [ACCEPTED / DONE](TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md),
A6 is FROZEN at `tiaf-a6-baseline`, and `expression.assess` is PUBLISHED as captured-read only. See the
[A6.3 implementation](TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE.md).
The [thesis creation record](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_THESIS_RECORD.md)
preserves history; the [fourteen-finding reconciliation](TIAF_A6_THESIS_ARCHITECTURE_RECONCILIATION.md)
now updates the normative draft. Thesis artifacts remain unchanged.

The post-R1 [Monitoring Architecture](TIAF_MONITORING_ARCHITECTURE.md) reconciles
future subscriber-driven mandates without changing accepted A5 intent or
implementing a runtime. A8 retains TM integration, A9 scanner/candidate intake,
and A10 durable monitoring operationalization. A separately approved minimum
runtime slice may accompany earlier integration only with its admission/replay/
budget/recovery gates; it is not automatically next. Detailed milestone coverage
is now available for [A4](TIAF_A4_DETAILED_ROADMAP.md) and
[A5](TIAF_A5_DETAILED_ROADMAP.md). No runtime or R2–R5 work is added.

## Current forward sequence

1. **TIAF A7 / FF-1.2 — LOGISTIC CANDIDATE TRAINING ARTIFACT IMPLEMENTATION** after the accepted
   [FF-0 engineering miniature](TIAF_A7_FF0_ACCEPTANCE.md).
   FF and A7 architectures are independently accepted; the
   [A7 acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) records residual gates,
   not implementation readiness.
   The [FF-1.1A rights-policy revision](TIAF_A7_FF1_1A_RIGHTS_POLICY_REVISION_AND_DATA_PROVISIONING.md)
   is complete: COLD WARN_ONLY admits uncertain rights with a warning, never
   approval. The [adjusted-data research qualification](TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md)
   now passes on the existing Dhan dataset. Empirical fitting is authorized for
   that pinned research profile only; no fit was performed. 2025 remains sealed.
2. Preserve the [completed four-step FF-0 baseline](TIAF_A7_FF0_ACCEPTANCE.md).
   The [completed FF-1 plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md)
   specifies scientific/data/dependency/fit gates; independent protocol review
   remains distinct from model approval. The [A7 roadmap](TIAF_A7_DETAILED_ROADMAP.md)
   retains FF-0…FF-7; old A7.1…A7.5 labels are not a second active hierarchy.
3. FF-0/1 scientific mechanics precede FF-2 calibrated/lifecycle miniature.
   Later publication is a separate checkpoint; optional advanced stages need
   their own evidence/grants and are not all mandatory for scoped closure.
4. Then A8; A9; A10 under the unchanged major roadmap.

The [A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md)
is **ARCHITECTURE ACCEPTED; THESIS RECONCILED; IMPLEMENTATION IN_PROGRESS (FF-0 AND FF-1.1 ACCEPTED);
INTERNAL SYNTHETIC RUNTIME IMPLEMENTED; PUBLIC FORECAST CAPABILITY NOT_PUBLISHED**. The
[thesis record](TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md)
links the unchanged non-normative creation edition. The
[17-finding reconciliation](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md) preserves deterministic controls
and proposes one exact cash-equity endpoint target, separate calibration,
explicit approval and shadow/advisory-only use. It adopts a separate immutable
Evaluation-owned population-disposition report with constraints, not a new
journal or public operation. Qualified data and preregistered
empirical gates must precede real model readiness. No automatic A4/A5/A6 influence
or new public capability; current catalog remains nine.

Initial A6 is long single-leg CE/PE only, non-executable, with explicit absence.
SigmaDSL is not an A6 dependency. A6.2 acceptance covers the internal
deterministic evaluator, A6.3 publication is accepted, and A6.4 hardening is
accepted. The deterministic A6 baseline is frozen; A7 remains unimplemented.

R2–R5 are bounded pluggability hardening before A6: descriptors/dependencies,
additive composition/pinned verification, optional import isolation and trusted
COLD ownership. These remain SHOULD_FIX_BEFORE_A6, not A5 freeze requirements.
After initial A6, A7 forecasting/evaluation may supply calibrated inputs for a
separately versioned forecast-enhanced A6 follow-up.
A8 TM integration, A9 scanner/candidate intake, A10 monitoring operationalization
and production hardening retain their admission, authority and delivery gates.

**Adjacent workstream ordering remains explicit TBD:** Sector Rotation needs its
own architecture/acceptance after the relevant deterministic/PIT/evaluation seams;
Signal Qualification is intended after Sector Rotation review unless explicitly
reordered. Placement relative to A7/A8 is not yet authoritative. Do not promote
the exploratory A7.0/A7.x/SR labels or silently insert an implementation into the
numbered sequence. Neither workstream is an A5 freeze blocker or callable now.

## Acceptance philosophy

Every milestone should have explicit contracts, representative tests, and
observable acceptance criteria. Outputs must identify their timestamp,
provenance, horizon, and responsible component when those concepts become
applicable. A milestone is accepted for demonstrated behavior, not for the
presence of placeholders. External integrations must preserve the boundary
between pluggable intelligence and centralized authority.

<a id="forecasting-framework--a7-integrated-architecture-acceptance-next"></a>

## Forecasting Framework and A7 — architecture accepted; FF-0 miniature accepted; engineering-only CLI

The [FF-0.1 foundation](TIAF_A7_FF0_1_CONTRACTS_TARGET_CLOCK_IMPLEMENTATION.md)
and [FF-0.2 capture/truth/replay](TIAF_A7_FF0_2_CAPTURE_STORE_TRUTH_RECORDED_REPLAY_IMPLEMENTATION.md)
remain accepted. The [FF-0.3 implementation record](TIAF_A7_FF0_3_BASERATE_COLD_RUNTIME_PINNED_VERIFICATION_IMPLEMENTATION.md)
records **FF0_3_ACCEPTED**: deterministic synthetic BaseRate, an immutable internal
COLD owner, honest ACTUAL/SIMULATED execution, capture and separate exact pinned
verification. A7 / FF is **IMPLEMENTATION IN_PROGRESS; INTERNAL SYNTHETIC RUNTIME
IMPLEMENTED; PUBLIC FORECAST CAPABILITY NOT_PUBLISHED**.
All four [planned FF-0 steps](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md)
are complete. The [FF-0.4 engineering CLI](TIAF_A7_FF0_4_ENGINEERING_CLI_ACCEPTANCE_HARDENING_IMPLEMENTATION.md)
and [final FF-0 acceptance](TIAF_A7_FF0_ACCEPTANCE.md) record **FF0_ACCEPTED**:
28/28 semantic cases; **INTERNAL_ENGINEERING_CLI_ONLY**; frozen at `e5283c9`
(`tiaf-a7-ff0-baseline`). The [FF-1 plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md)
is complete. [FF-1.1 qualification/schema tooling](TIAF_A7_FF1_1_DATA_QUALIFICATION_FEATURE_SCHEMA_IMPLEMENTATION.md)
is **FF1_1_ACCEPTED**; learned FF-1 runtime remains **NOT_IMPLEMENTED**.
**EMPIRICAL_FITTING_AUTHORIZED = YES** for the pinned
[FF-1.1A adjusted retrospective qualification](TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md).
Rights remain UNVERIFIED/WARN_ONLY, not approved. The existing Dhan dataset
passes bounded research gates; 2025 remains sealed. No fitting, calibration,
trained model or new consumer authority is claimed.
Calibration remains at FF-2; recorded replay is not recomputation or new simulation.

The [A7 acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) records
**A7_ARCHITECTURE_ACCEPTED** on **2026-09-15 (Asia/Kolkata)**:
A6 FROZEN; FF ARCHITECTURE ACCEPTED; A7 ARCHITECTURE ACCEPTED;
A7 THESIS RECONCILED AS NEEDED; then A7 / FF IMPLEMENTATION NOT_STARTED;
RUNTIME NOT_IMPLEMENTED. The bounded implementation update above supersedes that status.
FM/LFDE remains an optional advanced Forecaster family.

A7 is the lifecycle umbrella. FF owns forecasting contracts, typed DAG and
bounded runtime; Evaluation owns Ground Truth, Outcome Journal, joined Forecast
Ledger, benchmarks/metrics/calibration qualification/drift; Learning owns
candidate fits and the single artifact/lifecycle registry. Independent reviewer
approval and trusted COLD selection stay separate. The
[A7 roadmap](TIAF_A7_DETAILED_ROADMAP.md) contains FF-0…FF-7 unchanged,
with the old A7.1…A7.5 crosswalk. FF-0/1 raw research precedes FF-2's calibrated
miniature; publication is separately accepted, advanced families optional.

The [FF repeat review](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE_REPEAT.md)
closed FFA-B01; the [A7 integration](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md)
then reconciled all 17 A7 findings. Original HOLD, correction, repeat acceptance,
integration and all 28 FF findings remain historical evidence. Their then-next
language and the Deferral Register's dated A7.x notes are not the current queue.
All 58 canonical deferral rows and six thesis DOCX/PDF artifacts are unchanged.

Exact next prompt: **TIAF A7 / FF-1.2 — LOGISTIC CANDIDATE TRAINING ARTIFACT IMPLEMENTATION**.
FF-0 acceptance is limited to internal synthetic engineering mechanics. The FF-1 plan
has accepted FF-1.1 tooling and the FF-1.1A adjusted research qualification.
No fit was performed; FF-1.2 implementation requires its own request. Model
approval, publication, frozen-A6 changes and A8 remain out of scope. Historical
planning/acceptance records retain their then-current status.
