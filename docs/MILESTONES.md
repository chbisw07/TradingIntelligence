# Milestones

This is the **canonical historical and current milestone ledger**. The
[README](../README.md) is the executive dashboard; the
[major roadmap](TRADINGINTELLIGENCE_ROADMAP.md) owns intended milestone order,
the [forward queue](IMPLEMENTATION_ROADMAP.md) owns near-term gates, and
[engineering targets](TIAF_IMPLEMENTATION_TARGETS.md) carry detailed scope.
DOCX/PDF companions are non-normative.

## Current Development Position

**Current checkpoint — 2026-09-23 (Asia/Kolkata):** FF-0 COMPLETE / FROZEN at
`tiaf-a7-ff0-baseline`; FF-1 COMPLETE / FROZEN at `tiaf-a7-ff1-baseline`
(`21783ea31d4ce3b54fbcc6fcce6ef7e641bd5bec`). FF-1 scientific outcome remains
**INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE**; infrastructure accepted,
Logistic CHALLENGER / EXPERIMENTAL, promotion eligible NO; BaseRate BENCHMARK.
2025 is CONSUMED, executions used 1, post-holdout refit allowed NO.

**FLC COMPLETE / FROZEN** at `tiaf-a7-flc-baseline`,
commit `5f1e80c7e0614233b5670ca3acf9229edd0ea0db`; local/remote tag and
`main` verified synchronized from a clean tree on 2026-09-23.
The [FLC closure report](TIAF_A7_FLC_8_REFERENCE_IMPLEMENTATION_CLOSURE_AND_FLC_ACCEPTANCE.md#13-authorized-family-neutral-inference-reconciliation)
is preserved as historical evidence; the later Git freeze is now verified.

**FF-2 CURRENT — FF-2.1 GOVERNANCE COMPLETE; CALIBRATION NOT_IMPLEMENTED.**
The [calibrated Logistic research protocol](TIAF_A7_FF2_0_CALIBRATED_LOGISTIC_RESEARCH_PROTOCOL.md)
and [data-rights/readiness record](TIAF_A7_FF2_0_BASELINE_DATA_RIGHTS_AND_READINESS.md)
remain the unchanged scientific design and historical HOLD record.
[FF-2.1 governance](TIAF_A7_FF2_1_DATA_USE_AUTHORITY_AND_PROSPECTIVE_EVIDENCE_QUALIFICATION.md) now defines
historical-use boundaries, prospective qualification and the fixed one-shot trigger.
**GO_FF2_SYNTHETIC_IMPLEMENTATION_ONLY** for FF-2.2: implementation readiness YES;
empirical development and final evaluation readiness NO. No empirical grant,
calibration fit, live accrual, runtime promotion or public capability is added.

See [FF lifecycle architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#22-forecaster-lifecycle-completion-flc)
and [FLC gaps/packages](TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md).
See the [FLC-1 implementation and validation](TIAF_A7_FLC_1_FORECASTER_CONTRACT_AND_LIFECYCLE_SEAM_NORMALIZATION.md).
See the [FLC-2 implementation and validation](TIAF_A7_FLC_2_TRAINING_MODEL_IDENTITY_PERSISTENCE_AND_LIFECYCLE_NORMALIZATION.md).
See the [FLC-3 synthetic-only optimization and validation](TIAF_A7_FLC_3_BOUNDED_DEVELOPMENT_ONLY_OPTIMIZATION.md).
See the [FLC-4 model-specific diagnostics and validation](TIAF_A7_FLC_4_MODEL_SPECIFIC_DIAGNOSTICS_NORMALIZATION.md).
See the [FLC-5 calibration composition and validation](TIAF_A7_FLC_5_CALIBRATION_COMPOSITION_READINESS.md).
See the [FLC-6 reusable independent Evaluation and validation](TIAF_A7_FLC_6_REUSABLE_INDEPENDENT_EVALUATION_NORMALIZATION.md).
See the [FLC-7 integration, provenance and replay hardening](TIAF_A7_FLC_7_INTEGRATION_PROVENANCE_AND_REPLAY_HARDENING.md).
Next gate: FF-2.2 calibration implementation with authored synthetic evidence only.
Empirical fitting and protected evaluation require separate grants. No commit, tag or push.

The execution checkpoint below retains its historical then-next task.

2026-09-22 execution checkpoint: [one-shot protected 2025 final-holdout evaluation](TIAF_A7_FF1_ONE_SHOT_PROTECTED_2025_FINAL_HOLDOUT_EVALUATION.md)
returns **FF1_FINAL_HOLDOUT_ACCEPTED**, scientific **INSUFFICIENT_EVIDENCE**
(`CONFIDENCE_NONDECISIVE`). 249/249 pairs, 128 positive / 121 zero, coverage 100%,
49 complete blocks, no exclusions. Captured replay MATCH; **3,445** full-suite
tests pass. Holdout **CONSUMED**, final evidence **COMPLETE**, executions used **1**.
The lower Logistic point losses do not override the Brier interval crossing zero.
No refit, retry, automatic promotion, commit, tag or push. Exact next task:
**TIAF A7 / FF-1 — INDEPENDENT FINAL SCIENTIFIC CLOSURE AND BASELINE DECISION**.

The following checkpoints retain their historical as-of-review states, not
current permission to open or reuse 2025.

2026-09-22 freeze checkpoint: [final-holdout protocol freeze review](TIAF_A7_FF1_FINAL_HOLDOUT_PROTOCOL_FREEZE_REVIEW_WITH_FIFTH_FOLD_HANDOFF.md)
returns **FF1_READY_FOR_FINAL_HOLDOUT**. Fifth-fold blocker RESOLVED; final
evaluation authorized YES, decision protocol frozen YES. Both closures replay
MATCH; **3,414** tests pass. Protocol
`2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814`.
Protected evidence remains NOT_RUN and 2025 SEALED; execution slot unused.
No new fit or post-holdout refit, no commit/tag/push. Next separately requested:
**TIAF A7 / FF-1 — ONE-SHOT PROTECTED 2025 FINAL-HOLDOUT EVALUATION**.
Prior preparation and review checkpoints below retain their historical decisions.

2026-09-22 preparation checkpoint: [pre-holdout fifth-fold artifact preparation](TIAF_A7_FF1_PRE_HOLDOUT_FIFTH_FOLD_ARTIFACT_PREPARATION_AND_AUTHORITY_RECONCILIATION.md)
completed one empirical scaler/model fit and the BaseRate freeze at
2024-12-31T09:15:00+05:30. 1,690 TRAIN rows (878/812), 11 iterations,
reconstruction MATCH; **FIFTH_FOLD_PREPARATION_COMPLETE**, **3,351** tests pass. Handoff
`c40148f60e985c83fe8bca027a3722583ed8c1999ecfc86e4959c4fe6166ce54`.
2025 remains SEALED; no protected forecasts/metrics, no final protocol freeze
or opening authority. Next separately requested:
**TIAF A7 / FF-1 — FINAL-HOLDOUT PROTOCOL FREEZE REVIEW (WITH FIFTH-FOLD HANDOFF)**.
The prior review below is unchanged historical evidence; no commit/tag/push.

2026-09-22 review checkpoint (began September 21): [independent FF-1 scientific review](TIAF_A7_FF1_INDEPENDENT_SCIENTIFIC_ACCEPTANCE_AND_FINAL_HOLDOUT_DECISION_DESIGN.md)
returns **HOLD_FF1_BEFORE_FINAL_HOLDOUT**. No development-gate failure or protected
outcome violation found; the accepted handoff has only four development models
and BaseRate artifacts, not the planned fifth-fold final artifacts. Opening
authorization **NO**, final protocol frozen **NO**, holdout **SEALED**, final
evidence **NOT_RUN**. Next separately requested:
**TIAF A7 / FF-1 — PRE-HOLDOUT FIFTH-FOLD ARTIFACT PREPARATION AND NO-REFIT AUTHORITY RECONCILIATION**.
No runtime changes, model fitting, holdout opening, commit/tag/push.

2026-09-21 FF-1.4 checkpoint: [development-only paired evaluation](TIAF_A7_FF1_4_DEVELOPMENT_ONLY_PAIRED_BASERATE_VS_LOGISTIC_EVALUATION.md)
completed 969 exact pairs across 2021–2024, 22 explicit unpaired slots and full
offline reconstruction MATCH. All preregistered development gates pass;
scientific classification **INSUFFICIENT_EVIDENCE**. Protected 2025 **SEALED**;
final evidence **NOT_RUN**. **FF1_4_ACCEPTED**; all **3,327** repository tests pass.
No refit, tuning, calibration, promotion or public activation. Next separately
requested: **TIAF A7 / FF-1 — INDEPENDENT SCIENTIFIC ACCEPTANCE AND FINAL-HOLDOUT DECISION DESIGN**.
The following earlier checkpoints retain their then-current queue.

2026-09-21 FF-1.3 checkpoint: [FF-1.2](TIAF_A7_FF1_2_LOGISTIC_CANDIDATE_TRAINING_ARTIFACT_IMPLEMENTATION.md)
is ACCEPTED after explicit dependency-stack approval and four completed,
converged empirical fits. [FF-1.3](TIAF_A7_FF1_3_LOGISTIC_WALK_FORWARD_FORECAST_GENERATION.md)
has generated 969 SIMULATED Logistic forecasts; 991 origins are accounted for
and replay MATCH. **FF-1.3 is ACCEPTED**; all 3,295 repository tests pass. 2025 remains
SEALED; no public forecast runtime or performance evaluation. Next:
separately requested FF-1.4 paired evaluation. The FF-1.1A “current
next” checkpoint below is historical, not the present queue.

2026-09-21: **FF1_1A_QUALIFICATION_COMPLETE** under the explicit
[adjusted retrospective research profile](TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md).
`ADJUSTED_DATA_RESEARCH_PROFILE_ACCEPTED = YES`;
`EMPIRICAL_FITTING_AUTHORIZED = YES` for the pinned RELIANCE dataset only.
1,694 feature-eligible / 1,731 label-eligible / 1,691 paired-ready potential;
2025 holdout SEALED. No fit, scaler, learned forecast or paired performance metric.
Current next: **TIAF A7 / FF-1.2 — LOGISTIC CANDIDATE TRAINING ARTIFACT IMPLEMENTATION**.
No commit/tag/push; A6 and FF-0 tags unchanged. Earlier HOLD records below are
historical, not the current queue.

2026-09-20 follow-up at HEAD `2eb522c`: [FF-1.1A rights-policy
revision](TIAF_A7_FF1_1A_RIGHTS_POLICY_REVISION_AND_DATA_PROVISIONING.md) is accepted.
COLD WARN_ONLY separates unverified rights from research admission; explicit
denial and all scientific gates still block. Provisioning remains
**HOLD_NO_EMPIRICAL_DATASET; EMPIRICAL_FITTING_AUTHORIZED = NO**. The preceding
HOLD audit is unchanged. Then-next: **TIAF A7 / FF-1.1A — LOCAL RELIANCE
EMPIRICAL DATASET PROVISIONING**. No commit/tag/push; baseline tags unchanged.

The following entry-state details describe the original FF-1.1 pass:

Reverified on 2026-09-19 (Asia/Kolkata): FF-1.1 entry HEAD is `8bd1a72`
(completed FF-1 plan); `tiaf-a7-ff0-baseline` remains
`e5283c9eaa4294bd236186d663335efdf7dab236` (accepted FF-0 miniature);
`tiaf-a6-baseline` remains `6dc2ff304aae0e87540260b092919bb91e4d4189`;
A5 remains at `167c51d`. Entry worktree was clean. FF-1.1 adds offline qualification
and feature-schema tooling only; no learned fit, new commit or tag. A7 as a whole is not frozen.
FROZEN means an existing tag; ACCEPTED means reviewed scope; DONE means the
bounded remediation is closed.
ACTIVE is current work; PENDING is the queue; DEFERRED is registered postponed
work; FUTURE/TBD indicate later/unresolved scope; NOT_IMPLEMENTED means no runtime.

| Milestone | State | Existing tag / pending action | Closure / scope record |
|---|---|---|---|
| TGT0 | FROZEN | `tiaf-tgt0` | Python repository bootstrap |
| A0 | FROZEN | `tiaf-a0` | Immutable contracts; aware Asia/Kolkata timestamps |
| A1 | FROZEN | `tiaf-a1-baseline` | [Foundation](TIAF_A1_FOUNDATION_BASELINE.md), [acceptance](TIAF_A1_ACCEPTANCE_REPORT.md) |
| A2 | FROZEN | `tiaf-a2-baseline` | [Foundation](TIAF_A2_FOUNDATION_BASELINE.md), [acceptance](TIAF_A2_ACCEPTANCE_REPORT.md) |
| A3 | FROZEN | `tiaf-a3-baseline` | [Closure: READY_TO_FREEZE_A3](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md) |
| A4 | FROZEN | `tiaf-a4-baseline` | [Closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md); [slice map](TIAF_A4_DETAILED_ROADMAP.md) |
| TI_SHELL v0.1 | FROZEN | `tiaf-a4.91-shell-v0.1` | [Local command implementation](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md) |
| A5 | FROZEN | `tiaf-a5-baseline` | [Closure: READY_TO_FREEZE_A5](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md); [final check: READY_TO_TAG_A5](TIAF_A5_FINAL_FREEZE_TAG_READINESS_CHECK.md) |
| A6 | FROZEN | `tiaf-a6-baseline` | [A6.4 freeze readiness](TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md); final tag closure verified |
| A7 | ARCHITECTURE ACCEPTED / THESIS RECONCILED / IMPLEMENTATION IN_PROGRESS (FF-0 ACCEPTED; FF-1 SCIENTIFICALLY CLOSED INCONCLUSIVE) / INTERNAL SYNTHETIC RUNTIME IMPLEMENTED | FF architecture ACCEPTED and A7 integration RECONCILED; A7 architecture ACCEPTED; FF-0 plan COMPLETE; FF-0 ACCEPTED; FF-1 plan COMPLETE; FF-1.1 qualification/schema ACCEPTED; FF-1 final closure ACCEPTED / SCIENTIFICALLY CLOSED INCONCLUSIVE; FLC FROZEN; FF-2.1 GOVERNANCE COMPLETE; no overall A7 baseline tag | [FF-integrated architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md), [17-finding reconciliation](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md), [thesis record](TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md), [integrated stage crosswalk](TIAF_A7_DETAILED_ROADMAP.md) |

### Current FF baseline and completion track

| Track | Current state | Evidence / next gate |
| --- | --- | --- |
| FF-0 | COMPLETE / FROZEN | `tiaf-a7-ff0-baseline`; preserve runtime |
| FF-1 | COMPLETE / FROZEN | `tiaf-a7-ff1-baseline` at `21783ea`; INSUFFICIENT_EVIDENCE, no promotion |
| FLC | COMPLETE / FROZEN | `tiaf-a7-flc-baseline` → `5f1e80c7e0614233b5670ca3acf9229edd0ea0db`; local/remote verified; [closure](TIAF_A7_FLC_8_REFERENCE_IMPLEMENTATION_CLOSURE_AND_FLC_ACCEPTANCE.md#13-authorized-family-neutral-inference-reconciliation) preserved |
| FF-2 | CURRENT — FF-2.1 GOVERNANCE COMPLETE | [Data-use and qualification](TIAF_A7_FF2_1_DATA_USE_AUTHORITY_AND_PROSPECTIVE_EVIDENCE_QUALIFICATION.md); FF-2.2 synthetic-only implementation next; empirical/final readiness NO |

### Accepted submilestones and intervening gates

The slice rows below preserve their historical as-of-acceptance scope and gates,
including superseded qualification HOLDs; they are not the current queue.
Current FF-1 closure and tag readiness are recorded above and in the renewed review.

| Track | Accepted slices / actual tags | Evidence index / qualification |
|---|---|---|
| A1 | `tiaf-a1.1`, `tiaf-a1.2`, `tiaf-a1.3`, `tiaf-a1.4`, `tiaf-a1.5`, `tiaf-a1.6`, `tiaf-a1.7` | [Acceptance](TIAF_A1_ACCEPTANCE_REPORT.md); scope below |
| A2 | `tiaf-a2.1`, `tiaf-a2.2`, `tiaf-a2.3`, `tiaf-a2.4`, `tiaf-a2.5`, `tiaf-a2.6`, `tiaf-a2.7`, `tiaf-a2.8`, `tiaf-a2.9`, `tiaf-a2.10` | [Acceptance](TIAF_A2_ACCEPTANCE_REPORT.md); deterministic benchmark, not final recommendation engine |
| A3 | `tiaf-a3.1`, `tiaf-a3.2`, `tiaf-a3.3`, `tiaf-a3.4`, `tiaf-a3.5`, `tiaf-a3.6`, `tiaf-a3.6.1`, `tiaf-a3.6.2`, `tiaf-a3.7`, `tiaf-a3.8`, `tiaf-a3.9`, `tiaf-a3.10` | [Detailed roadmap](TIAF_A3_DETAILED_ROADMAP.md) and dated live/offline evidence |
| Architecture checkpoints | `tiaf-a3-arch`, `tiaf-a3.6.1-arch`, `tiaf-a3.10-arch`, `tiaf-post-a3-architecture` | Accepted design checkpoints, not standalone runtime claims |
| Pre-A4 foundation / facade | ACCEPTED; no standalone tag | [Source foundation](TIAF_POST_A3_PRE_A4_FOUNDATION.md), [local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) |
| A4.1 / A4.2 | ACCEPTED within A4 baseline; no standalone slice tags | [Detailed roadmap](TIAF_A4_DETAILED_ROADMAP.md): deterministic arbitration / bounded internal evidence bridge |
| A5.1 / A5.2 | ACCEPTED; no standalone slice tags | [Detailed roadmap](TIAF_A5_DETAILED_ROADMAP.md): deterministic single-position advice / governed captured-read facade and Shell |
| A7 / FF-0.1 | ACCEPTED foundation at `7be1726`; no separate tag | [Contracts, target and clock implementation](TIAF_A7_FF0_1_CONTRACTS_TARGET_CLOCK_IMPLEMENTATION.md); that slice alone did not complete FF-0 |
| A7 / FF-0.2 | ACCEPTED capture/truth/recorded replay at `79c9726`; no separate tag | [Capture store, truth and recorded replay](TIAF_A7_FF0_2_CAPTURE_STORE_TRUTH_RECORDED_REPLAY_IMPLEMENTATION.md); that slice did not implement execution |
| A7 / FF-0.3 | ACCEPTED internal synthetic BaseRate/runtime/verification at `1a61cb7`; no separate tag | [BaseRate, COLD runtime and pinned verification](TIAF_A7_FF0_3_BASERATE_COLD_RUNTIME_PINNED_VERIFICATION_IMPLEMENTATION.md) |
| A7 / FF-0.4 and overall FF-0 | FROZEN internal engineering miniature at `e5283c9`; `tiaf-a7-ff0-baseline` | [CLI implementation](TIAF_A7_FF0_4_ENGINEERING_CLI_ACCEPTANCE_HARDENING_IMPLEMENTATION.md), [28-case final acceptance](TIAF_A7_FF0_ACCEPTANCE.md); original pre-commit acceptance record retained |
| A7 / FF-1 planning | COMPLETE; READY_FOR_FF1_IMPLEMENTATION means planning readiness only; runtime NOT_IMPLEMENTED | [Logistic / paired evaluation plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md); FF-1.1 qualification accepted; FF-1.1A empirical qualification next; empirical fitting HOLD, no trained model or publication |
| A7 / FF-1.1 | FF1_1_ACCEPTED; no tag or learned fit | [Qualification and feature-schema implementation](TIAF_A7_FF1_1_DATA_QUALIFICATION_FEATURE_SCHEMA_IMPLEMENTATION.md); 102 targeted tests, 3,023 full-suite tests; EMPIRICAL_FITTING_AUTHORIZED = NO; FF-1.1A next |
| A7 / FF-1.1A | HOLD_FF1_1A_QUALIFICATION; empirical fitting remains unauthorized | [Empirical qualification preflight](TIAF_A7_FF1_1A_EMPIRICAL_DATA_RIGHTS_QUALIFICATION_EXECUTION.md): no local empirical daily dataset or rights evidence supplied/identified; provide dataset and rights/PIT evidence before resuming; no fit, acquisition or semantic change |
| A7 / FF-1.1A rights revision | FF1_1A_RIGHTS_POLICY_REVISION_ACCEPTED; provisioning HOLD_NO_EMPIRICAL_DATASET | [Policy/provisioning follow-up](TIAF_A7_FF1_1A_RIGHTS_POLICY_REVISION_AND_DATA_PROVISIONING.md): COLD WARN_ONLY default; evidence/status/admission pinned separately; no empirical data, fit or scientific-gate relaxation; previous HOLD retained |

Acceptance is bounded, not universal live-provider certification. A3.6.1's
standalone exact-current Tapetide matrix retained a quota HOLD; separate Yahoo
and A3.6.2 integrated matrices passed. A3.7 Dhan acquisition failed before
option-chain evidence, so no live specialist result is claimed there.
Historical descriptions below retain milestone-local live/offline qualifications.

## Cross-Cutting Pluggability Remediation Track (R1–R5)

This is a **cross-cutting pluggability remediation / hardening track** across
A1–A5, never A5.3/A5.4. The audit's SHOULD_FIX_BEFORE_A6 classification is the
current BEFORE_A6 queue, not a new A5 freeze requirement. R2–R5 do not block A5
freeze; R2, R3, R4 and R5 are accepted/done. The pre-A6 R-series is closed.

| Item | Purpose | Status | Blocks A5 freeze? | Required before A6? | Key doc |
|---|---|---|---|---|---|
| R1 | Policy-owned required scope and explicit absence | ACCEPTED / DONE | No — former blocker resolved | Yes — satisfied | [Acceptance](TIAF_PLUGGABILITY_R1_ACCEPTANCE_AND_A5_FREEZE_READINESS.md) |
| R2 | Versioned discovery / dependency metadata | ACCEPTED / DONE | No | Yes — satisfied | [Acceptance](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA_ACCEPTANCE.md) |
| R3 | Additive composition envelope / pinned verifier | ACCEPTED / DONE | No | Yes — satisfied | [Implementation](TIAF_PLUGGABILITY_R3_COMPOSITION_ENVELOPE_PINNED_VERIFIER.md), [acceptance](TIAF_PLUGGABILITY_R3_COMPOSITION_ENVELOPE_PINNED_VERIFIER_ACCEPTANCE.md) |
| R4 | Optional adapter import isolation | ACCEPTED / DONE — BEFORE_A6 | No | Yes — satisfied | [Implementation](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION.md), [acceptance](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION_ACCEPTANCE.md) |
| R5 | Trusted COLD ownership / configuration | ACCEPTED / DONE — BEFORE_A6 | No | Yes — satisfied | [Implementation](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md), [acceptance](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION_ACCEPTANCE.md) |

R2–R5 retain their audit identities; the
[deferral register](TIAF_DEFERRAL_REGISTER.md) cross-references them without
duplicate DEF IDs. HOT and future peer publication remain DEF-057/058.

## A5 closure chronology and current gate

1. A5.1 and A5.2 accepted; major closure: `READY_TO_FREEZE_A5`.
2. First-order pluggability promoted before tagging; audit introduced R1 as a
   temporary pre-freeze blocker.
3. R1 resolved and accepted; R2–R5 classified as non-blocking for A5, before A6.
4. [Documentation consolidated](TIAF_POST_R1_DOCUMENTATION_CONSOLIDATION_AND_SYNCHRONIZATION.md);
   monitoring and ecosystem ownership designs accepted without runtime expansion.
5. [Final readiness](TIAF_A5_FINAL_FREEZE_TAG_READINESS_CHECK.md), 2026-09-13:
   `READY_TO_TAG_A5`.
6. Final documentation was committed at `167c51d`; annotated tag
   `tiaf-a5-baseline` was created and pushed on that exact commit.
7. R2 Discovery Metadata is accepted and `READY_TO_CLOSE_PLUGGABILITY_R2`.
8. R3 Composition Envelope / Pinned Verifier is accepted and
   `READY_TO_CLOSE_PLUGGABILITY_R3`.
9. R4 Optional Adapter Import Isolation is accepted and
   `READY_TO_CLOSE_PLUGGABILITY_R4`.
10. R5 COLD Ownership / Configuration is accepted/done; the R1–R5 track is closed.

```text
A5 FROZEN (`tiaf-a5-baseline`)
  → R2 ACCEPTED → R3 ACCEPTED → R4 ACCEPTED → R5 ACCEPTED
  → A6 ARCHITECTURE ACCEPTED / THESIS ACCEPTED
  → A6.1 CONTRACTS / ADMISSION / POLICY ACCEPTED / DONE
  → A6.2 EVALUATION / RANKING / REPLAY ACCEPTED / DONE
  → A6.3 ACCEPTED / DONE → A6.4 ACCEPTED / DONE
  → A6 FROZEN (`tiaf-a6-baseline`) → A7 ARCHITECTURE ACCEPTED / IMPLEMENTATION IN_PROGRESS (FF-0 ACCEPTED; FF-1 SCIENTIFICALLY CLOSED INCONCLUSIVE) → A8 → A9 → A10
```

## Future / parallel workstreams

| Workstream | Design versus runtime | Intended placement |
|---|---|---|
| Monitoring | ACCEPTED design; recurring runtime NOT_IMPLEMENTED | A8 TM, A9 scanner intake, A10 operations |
| Trading Ecosystem | ACCEPTED ownership design; integration NOT_IMPLEMENTED | A8/A9/A10 |
| A6 | FROZEN; A6.1–A6.4 ACCEPTED / DONE | `tiaf-a6-baseline`; [A6.4](TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md) closes the 93-case corpus; `expression.assess` PUBLISHED |
| A7 forecasting / evaluation | Architecture ACCEPTED / thesis RECONCILED; IMPLEMENTATION IN_PROGRESS (FF-0 ACCEPTED; FF-1 SCIENTIFICALLY CLOSED INCONCLUSIVE); INTERNAL SYNTHETIC RUNTIME IMPLEMENTED | Completed FF integration; old A7.1–A7.5 mapped to canonical FF stages, no automatic A6 overlay |
| Forecasting Framework | ARCHITECTURE ACCEPTED / THESIS RECONCILED / IMPLEMENTATION IN_PROGRESS (FF-0 ACCEPTED; FF-1 SCIENTIFICALLY CLOSED INCONCLUSIVE) / FF-0 MINIATURE ACCEPTED; FF-1 TRAINING/EVALUATION IMPLEMENTED / FF-2 NOT_IMPLEMENTED / INTERNAL SYNTHETIC RUNTIME IMPLEMENTED | FF-0 accepted (all four steps); FF-1 plan COMPLETE; FF-1.1 qualification/schema ACCEPTED; FF-1 final closure ACCEPTED / SCIENTIFICALLY CLOSED INCONCLUSIVE; FLC FROZEN; FF-2.1 GOVERNANCE COMPLETE; public exposure still absent |
| FM / LFDE design track | ADVANCED FORECASTER FAMILY IN FF / THESIS RETAINED / NOT_IMPLEMENTED | Conditional internal research; not abandoned or required before a simple FF |
| Sector Rotation | FUTURE / TBD design, NOT_IMPLEMENTED | Relative to A7/A8 explicitly TBD |
| Signal Qualification | FUTURE / TBD design, NOT_IMPLEMENTED | Intended after Sector Rotation review unless reordered; A7/A8 placement TBD |
| A8 TM / A9 Scanner | FUTURE; runtime integration NOT_IMPLEMENTED | Existing major milestone ownership retained |
| A10 production hardening | FUTURE; full operational runtime NOT_IMPLEMENTED | Admission, budgets, recovery and durability gates |
| Web / multi-console Cockpit | Accepted ecosystem ownership; detailed UI TBD, NOT_IMPLEMENTED | FUTURE; delivery placement TBD |

Navigation continues through [ROADMAP](TRADINGINTELLIGENCE_ROADMAP.md) →
[THESIS](TIAF_THESIS.md) → [SYSTEM](TIAF_SYSTEM_ARCHITECTURE.md) →
[PLUGGABILITY](TIAF_PLUGGABILITY_ARCHITECTURE.md) →
[MONITORING](TIAF_MONITORING_ARCHITECTURE.md) →
[ECOSYSTEM](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md) →
[A4](TIAF_A4_DETAILED_ROADMAP.md) / [A5](TIAF_A5_DETAILED_ROADMAP.md).
The remaining sections retain detailed delivered scope and future milestone
charters; a charter is not an implementation claim.

## Deferral governance

Intentional deferrals are retained under stable IDs in
[`TIAF_DEFERRAL_REGISTER.md`](TIAF_DEFERRAL_REGISTER.md). They are recorded when
discovered but reviewed as a group only at each **major milestone closure**
(A2, A3, A4, and so on), not after every sub-milestone.

Each major closure reports deferrals introduced, implemented, rejected,
superseded, carried forward with rationale, and remaining high-priority items.
Satisfied dependencies should trigger an implementation attempt; unresolved
items remain visible rather than silently rolling forward.

## TIAF_A0 — Domain Contracts and Foundation — COMPLETE / FROZEN

Purpose: establish the stable language every future Planner, Agent, Scanner and TradeMonitor integration will use.

Planned scope:

- `OpportunityRequest`
- `PositionRequest`
- `EvidenceItem`
- `DataSnapshot`
- `AgentOpinion`
- `AgentDecisionBundle`
- `OpportunityAssessment`
- `PositionAssessment`
- `OptionExpression`
- stable identifiers and timestamps
- schema/version compatibility rules
- domain enums for style, horizon, direction, action, strength, freshness, evidence and confidence
- serialization/validation tests

No LangGraph workflow, LLM call, broker API, market prediction, or execution capability belongs in A0.

## TIAF_A1 — Data Foundation — COMPLETE / BASELINED

Canonical closure records:

- `TIAF_A1_FOUNDATION_BASELINE.md`
- `TIAF_A1_ACCEPTANCE_REPORT.md`
- baseline tag: `tiaf-a1-baseline`

**Complete / frozen:** TIAF_A1.1 — Provider Contracts + Normalized Market Models

- normalized instrument, quote, OHLCV, historical-series, and instrument-master models
- provider capability protocol
- typed data/provider failures
- canonical timestamp, identity, interval, and freshness normalization helpers
- no live provider adapter

**Complete / live-validated:** TIAF_A1.2 — Dhan Core Market Data Adapter

- authenticated, read-only DhanHQ v2 HTTP transport
- ordered and chunked full market quotes
- daily and supported intraday OHLCV
- typed Dhan error translation
- explicit security-ID and derivative-instrument mapping boundaries
- no orders, portfolio access, WebSocket, or trading behavior

**Complete / live-validated:** TIAF_A1.3 — Dhan Derivatives & Live Option Intelligence Data

- provider-neutral frozen expiry-list and live option-chain contracts
- read-only Dhan expiry discovery and complete option-chain normalization
- contract IDs, spot, prices, top-of-book, OI, volume, IV, and reported Greeks
- separate `DerivativesDataProvider` protocol
- no expired history, selection, analytics, recommendations, or execution

**Complete / live-validated:** TIAF_A1.4 — Dhan Historical / Expired Options Data

- provider-neutral rolling historical-option bars and series
- read-only Dhan expired-options endpoint using underlying security IDs
- explicit weekly/monthly expiry code and ATM-relative strike context
- complete factual OHLC, IV, volume, OI, actual-strike, and spot arrays
- adjacent half-open 30-day chunking and deterministic merge semantics
- no replay strategy, option selection, recommendation, or execution

**Complete / live-validated:** TIAF_A1.5 — Instrument Resolver

- frozen provider-neutral exact query and explicit result contracts
- Dhan detailed instrument-master load/download and narrow atomic file cache
- indexed security-ID, trading-symbol, and symbol-plus-filter resolution
- explicit configurable primary-exchange selection with visible policy metadata
- generic ambiguity preservation and no first-row selection
- deterministic exchange-scoped F&O-underlying universe from derivative identity
- symbol-first smoke diagnostics with hard symbol/security-ID consistency checks
- provider diagnostic/test identities excluded from canonical F&O universes
- no recommendation, ranking, Agent, order, account, or spreadsheet behavior

**Complete / live-validated:** TIAF_A1.6 — Cache, Freshness & Provider Scheduling

- provider-neutral in-process factual cache and deterministic cache keys
- caller-relative freshness with visible `FRESH` / `AGING` / `STALE` / `UNKNOWN`
- monotonic provider scheduling with explicit non-sleeping eligibility decisions
- key-scoped request coalescing and opt-in bounded stale-on-error fallback
- documented Dhan quote and option-chain constraints outside generic runtime
- no background queues, Intelligence OS, Agents, recommendations, or execution

**Complete / live-validated:** TIAF_A1.7 — AnalysisContext Builder

- immutable provider-neutral analysis subject, requirements, evidence slots,
  aggregate context, ordered batch outcomes, and factual summary
- A1.5 resolution plus A1.6-coordinated quote, history, explicit option-chain,
  and exact historical-options acquisition
- deterministic required-only retrieval freshness, completeness, quality, and
  partial/failure semantics with separate retrieval/source-observation
  provenance
- ordered batch statuses distinguish completed/partial contexts, temporary
  provider-scheduler deferral, and errors without hidden sleeps or retries
- no indicators, scoring, recommendation, Agent, queue, broker, or execution

**Acceptance:** a watchlist can be converted into timestamp-consistent factual
contexts or explicit partial/deferred/error outcomes. Provider fallback,
external evidence, persistent caching, and retry orchestration remain future
work rather than hidden A1 behavior.

## TIAF_A2 — Deterministic Baseline — COMPLETE / LIVE VALIDATED

**TIAF_A2.1 — Feature Contracts + Engine Foundation: COMPLETE / LIVE VALIDATED**

- immutable provider-neutral feature definitions, requests, results, and bundles
- explicit deterministic calculator registry and context-only engine
- exact baseline price, history, return, and high/low range measurements
- source quality, provenance, timestamp, and insufficient-data preservation
- no interpretation, recommendation, Agent, broker, or execution behavior

**TIAF_A2.2 — Price / Return / Volatility Features: COMPLETE / LIVE VALIDATED**

- exact price-location, logarithmic return, candle-range, drawdown, and run-up
  measurements
- strict Wilder ATR, explicit-factor realized volatility, rolling extrema, and
  signed move/ATR
- worst-source quality aggregation and market-observation `as_of` semantics
- no trend classification, score, recommendation, Agent, or execution behavior

**TIAF_A2.3 — Trend & Structure Features: COMPLETE / LIVE VALIDATED**

- completed-history moving averages, distance/spread, OLS slope, and R-squared
- directional efficiency, close-transition fractions, and trailing runs
- deterministic adjacent high/low fractions and rolling-range position
- ATR-normalized distance from SMA/EMA without interpretation or signals

**TIAF_A2.4 — Indicator Framework + Initial Indicator Library: COMPLETE / LIVE VALIDATED**

- first-class immutable definitions, requests, results, bundles, and explicit
  extensible calculator registry
- indicator-agnostic deterministic engine over completed `AnalysisContext`
  history
- SuperTrend, RSI, MACD, ADX/DI, Bollinger, and Donchian factual outputs
- no strategy signals, recommendations, optimization, Agent, or execution

A2.4 was inserted because scanners, strategy engines, Agents, replay systems,
parameter optimization, dashboards, and custom indicators need one reusable
versioned abstraction. Indicators complement rather than replace A2.3
primitive measurements.

**TIAF_A2.5 — Volume / Participation Features: COMPLETE / LIVE VALIDATED**

- completed-history raw, average, median, relative, change, dispersion, and
  volume-slope measurements
- deterministic close-transition participation and price/range alignment
- no accumulation/distribution claims, confirmation, signal, or Agent logic

**TIAF_A2.6 — Support / Resistance / Breakout Structure: COMPLETE / LIVE VALIDATED**

- prior rolling boundaries that explicitly exclude the current completed bar
- close/wick excursion, prior-range position, and normalized range geometry
- no subjective pivots, confirmation, score, recommendation, or Agent logic

**TIAF_A2.7 — Derivatives / Option-Chain Features: COMPLETE / LIVE VALIDATED**

- explicit-expiry option-chain geometry and factual derivative measurements
- ATM premiums/IV/Greeks, exact-window OI/volume/spread/concentration primitives
- no option selection, strategy model, recommendation, or execution

**TIAF_A2.8 — Relative Strength, Benchmark & Multi-Timeframe Context: COMPLETE / LIVE VALIDATED**

- explicit caller-supplied benchmark identity and exact aligned-bar comparisons
- ordered per-timeframe feature contexts and factual cross-timeframe fractions
- no scoring, ranking, recommendation, Agent, or execution logic
- implementation and read-only Dhan validation accepted at tag `tiaf-a2.8`

**TIAF_A2.9 — Deterministic Market-State & Opportunity Baseline: COMPLETE / LIVE VALIDATED**

- immutable policy, request, component, contribution, assessment, and ranking contracts
- separate positive/negative direction, alignment/conflict, quality, room, and maturity
- horizon-specific version 1.0 DAY/POSITIONAL engineering policies
- transparent `TOP_MOVER`, `EARLY_OPPORTUNITY`, `MATURE_AVOID_CHASE`, and `NO_TRADE`
- eligible-only score/quality/symbol ranking with stable ties and complete audit retention
- no providers, Agents, LLMs, strategies, order logic, or execution inside the subsystem

**TIAF_A2.10 — Replay / Validation / Baseline Evaluation: COMPLETE / LIVE VALIDATED**

- content-addressed normalized evidence snapshots and immutable run records
- exact provider-free replay and policy comparison over unchanged evidence
- later factual outcome paths, MFE/MAE, and frozen-ranking statistics
- append-only filesystem corpus and deterministic field-level regression checks
- no policy optimization, historical reconstruction claim, simulated execution, or Agents

The A2 closure and governed deferral burn-down are complete. Canonical closure
records are `TIAF_A2_FOUNDATION_BASELINE.md` and
`TIAF_A2_ACCEPTANCE_REPORT.md`; the accepted major baseline tag is
`tiaf-a2-baseline`.

- deterministic feature engine
- multi-timeframe price/volume features
- ATR / ATR%
- Move/ATR / range-consumption
- trend and momentum
- relative volume
- relative strength vs index/sector
- volatility regime
- basic support/resistance context
- horizon-specific bullish/bearish scoring
- candidate classes such as `TOP_MOVER`, `EARLY_OPPORTUNITY`, `MATURE_AVOID_CHASE`, `NO_TRADE`

**Acceptance:** reproducible non-AI rankings exist as a benchmark the Agent system must later beat.

## TIAF_A3 — Specialist Intelligence — Complete / Baselined

Accepted bounded capabilities include Technical/Market Structure,
Fundamental/Company Quality, News/Catalyst/Event, Relative, Sector/Rotation,
Macro, Derivatives Context, Opportunity Risk, Contrarian Hypothesis, and
conditional Forecast Interpretation. An instrument-aware Planner selects only
the evidence and specialists justified by the horizon, purpose, candidate
stage, and explicit budget. Agents consume shared evidence through controlled
gateways and cannot call brokers, arbitrary providers, browsers, or shell tools.

The implemented and accepted sequence is A3.1 contracts; A3.2 evidence/reasoning/budget
gateways; A3.3 technical specialist; A3.4 fundamentals; A3.5 news/events; A3.6
relative/sector/macro; A3.6.1 provider fabric/research foundation; A3.7
derivatives/risk; A3.8 Planner; A3.9 structured
underlying intelligence; and A3.10 replay/cost/failure hardening. See
[`TIAF_A3_ARCHITECTURE.md`](TIAF_A3_ARCHITECTURE.md) and
[`TIAF_A3_DETAILED_ROADMAP.md`](TIAF_A3_DETAILED_ROADMAP.md).

**A3.1 implementation:** immutable Agent/evidence/claim/confidence/budget/run
contracts, AgentOpinion v2 with frozen A0-v1 compatibility, runtime-checkable
protocols, extensible registry, deterministic serialization, and an exactly-one-
specialist failure-isolating runtime. See
[`TIAF_A3_1_AGENT_FOUNDATION.md`](TIAF_A3_1_AGENT_FOUNDATION.md). Status is
complete/accepted. A3.2 adds controlled evidence/reasoning registries and
runtimes, A2 evidence reuse, capability policy, model-tier mapping, no-LLM
mode, structured-output validation, budgets, cache keys, and audit records; it
is complete/accepted. See
[`TIAF_A3_2_GATEWAYS_BUDGETS.md`](TIAF_A3_2_GATEWAYS_BUDGETS.md). A3.3 adds the
first deterministic, cited technical specialist and is complete/accepted; see
[`TIAF_A3_3_TECHNICAL_SPECIALIST.md`](TIAF_A3_3_TECHNICAL_SPECIALIST.md). A3.4
adds provider-neutral point-in-time company evidence and the deterministic,
cited Fundamental Specialist; see
[`TIAF_A3_4_FUNDAMENTAL_INTELLIGENCE.md`](TIAF_A3_4_FUNDAMENTAL_INTELLIGENCE.md).
A3.5 is complete/accepted at `tiaf-a3.5`. A3.6 adds three separate contextual
specialists, explicit mapping/sensitivity evidence, controlled sector/macro
gateways, and shared source-context reuse; see
[`TIAF_A3_6_RELATIVE_SECTOR_MACRO_INTELLIGENCE.md`](TIAF_A3_6_RELATIVE_SECTOR_MACRO_INTELLIGENCE.md).
A3.6.1 implements provider-neutral fine capabilities, per-capability routing,
semantic normalization/conflicts, a read-only Tapetide adapter boundary, a
secondary fixture, sparse evidence memory, and composable research contracts;
see [`TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md`](TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md).

A3.6.2 through A3.10 are accepted at their corresponding tags. The separate
[A3 major closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md) reconciles
the full inventory, live/non-live evidence and all active deferrals, and
concludes `READY_TO_FREEZE_A3`. The major baseline is frozen at
`tiaf-a3-baseline`; later foundation, facade and A4 work remain additive.

**Acceptance:** a bounded A2-screened set can produce zero or more replayable,
cited underlying-opportunity records with separate specialist opinions,
disagreement, quality/freshness, missing evidence, budgets, and A2 comparison.
`WAIT`, `NO_TRADE`, `ABSTAIN`, and insufficient evidence are valid. A3 does not
emit `CE`/`PE`; A6 owns option expression.

## TIAF_A4 — Arbitration and Adversarial Review

- deterministic primary/counter thesis construction
- evidence-linked challenge and non-voting arbitration
- preserved disagreement, gaps and residual uncertainty
- explicit non-action dispositions
- governed one-round A3.8 evidence enrichment and successor projection
- exact offline replay, fingerprints and known-zero model usage

**Acceptance:** A4.1/A4.2 are complete and frozen at `tiaf-a4-baseline`; no
single fluent Agent becomes an oracle, and dispositions expose surviving
theses, disagreement and evidence. Optional model challenge remains deferred.
The approved pre-A5 [TI_SHELL architecture](TIAF_TI_SHELL_ARCHITECTURE.md) is an
unnumbered consumer slice, not A4 expansion or an A5 dependency.

## TIAF_A5 — Position Intelligence MVP

Architecture, the bounded A5.1 implementation and A5.2 publication are complete
and jointly reviewed as `READY_TO_FREEZE_A5`. A5 consumes an
explicitly supplied current TM/broker snapshot and linked accepted A4 result,
then emits evidence-linked advice without operational authority. Operational
state, analytical risk posture, thesis health, recommendation and monitoring
lifecycle stay separate. A5.1 is restricted to deterministic single-open-
position assessment, immutable monitoring intent, capture and offline replay.
Multi-leg policy, scheduler/runtime monitoring, TM integration and A6/A7 remain
later work. A5.2 now provides only governed local facade/Shell exposure.

**Acceptance:** the accepted
[A5 architecture](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md) and
[review](TIAF_A5_ARCHITECTURE_REVIEW.md) define the boundary, while
[A5.1](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md) implements and tests
fail-closed freshness/identity semantics, preserved A4 lineage and exact offline
replay with no external call. The
[closure review](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md) records the full
semantic, monitoring, deferral, live-truth and quality-gate audit.

## TIAF_A6 — Option Expression Intelligence

**2026-09-14 (Asia/Kolkata): FROZEN at `tiaf-a6-baseline`;
A6.1–A6.4 ACCEPTED / DONE; `expression.assess` PUBLISHED.** The [architecture](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md),
[reconciliation](TIAF_A6_RECONCILIATION_RECORD.md) and
[detailed roadmap](TIAF_A6_DETAILED_ROADMAP.md) preserve A5 and accepted R1–R5.

Proposed initial scope is deterministic advisory long single-leg CE/PE:
admitted A4 thesis, listed ATM/ITM1/OTM1 candidates, explicit expiry/horizon fit,
qualified quote freshness/liquidity, optional IV/Greek/premium context, event
constraints, transparent ranking and replay. No SigmaDSL, A7 prerequisite,
multi-leg/short-option strategy engine, account sizing or execution authority.

**A6.2 acceptance:** suitable expression/alternatives or explicit no-trade,
wait, insufficient-evidence or unsupported outcome are deterministic and
attributable. The internal evaluator is accepted. A6.3 now publishes that
evaluator through a governed captured-read facade/Shell path. The
[complete user-reference thesis](TI_Trade_Expression_Intelligence_Thesis.docx)
is created; its [fourteen findings are reconciled](TIAF_A6_THESIS_ARCHITECTURE_RECONCILIATION.md).
The [independent architecture acceptance](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md)
records READY_TO_IMPLEMENT_A6_1. The [A6.1 implementation](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION.md)
is closed by its [independent acceptance](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION_ACCEPTANCE.md). Four bounded
slices are contracts/admission; evaluation/ranking/replay; facade/Shell; and
hardening/acceptance. No tag is created by this architecture pass.
The [A6.2 implementation](TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY.md)
delivers only the internal deterministic evaluation slice and is closed by its
[independent acceptance](TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY_ACCEPTANCE.md).

The [A6.3 implementation](TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE.md) is closed by
its [independent acceptance](TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE_ACCEPTANCE.md).
The [A6.4 closure](TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md)
records the explicit 93-case acceptance corpus and recommends the baseline.
The subsequent A7 architecture and thesis are RECONCILED. Their architecture acceptance was paused for FF review; FF acceptance and
A7 integration are complete. The [independent A7 acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md)
now accepts the architecture; FF-0 planning is complete; FF-0 is accepted; FF-1 planning is complete; FF-1.1 qualification/schema is accepted; FF-1 training and evaluation are complete; FF-1 is scientifically closed inconclusive. FLC completion precedes deferred FF-2.

## FM / LFDE — Intervening research architecture

**2026-09-14 (Asia/Kolkata): ADVANCED FORECASTER FAMILY IN FF; THESIS RETAINED;
RUNTIME NOT_IMPLEMENTED.** The family
[architecture](TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md),
[research reconciliation](TIAF_FM_LFDE_RESEARCH_RECONCILIATION.md),
[roadmap](TIAF_FM_LFDE_DETAILED_ROADMAP.md) and
[decision record](TIAF_FM_LFDE_DECISION_RECORD.md) define a bounded numeric
market-state/latent-representation research path. The non-normative
[thesis and record](TIAF_FM_LFDE_THESIS_RECORD.md) add 35 chapters, 32 figures,
10 worked scenarios, 29 FAQ answers and 24 originally unapplied findings. A6 remains FROZEN;
A7 ARCHITECTURE is ACCEPTED; FF-0 planning is COMPLETE; FF-0 is ACCEPTED; FF-1 planning is COMPLETE; FF-1.1 qualification/schema is ACCEPTED; FF-1.1A empirical qualification is NEXT. No new numbered A7 milestone, model fit,
runtime capability or deferral closure. The 24 findings are now dispositioned
in the [FF reconciliation](TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md), without
altering the thesis edition. Shared platform ownership moves to FF below.

## Forecasting Framework — Platform reconciliation

**FORECASTING FRAMEWORK ARCHITECTURE ACCEPTED; FF MINIATURE REALIZATION DEFINED;
FF THESIS RECONCILED; FF ARCHITECTURE ACCEPTED; FFA-B01 CLOSED; A7 integration RECONCILED; A7 architecture ACCEPTED; FF-0 plan COMPLETE; FF-0 ACCEPTED; FF-1 plan COMPLETE; FF-1.1 qualification/schema ACCEPTED; FF-1 final closure ACCEPTED / SCIENTIFICALLY CLOSED INCONCLUSIVE; FLC FROZEN; FF-2.1 GOVERNANCE COMPLETE; INTERNAL SYNTHETIC RUNTIME IMPLEMENTED.**
The [architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md),
[roadmap](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) and
[decision](TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md) define primitive and
composite forecasters, typed DAGs, shared truth/ledger, paired evaluation,
calibration and governed future COLD selection. No model family is the platform.
Retain the advanced FM/LFDE thesis and platform handbook. FF-1 is **FF1_FINAL_CLOSURE_ACCEPTED / FF1_SCIENTIFICALLY_CLOSED_INCONCLUSIVE**.
The outcome remains **INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE**;
infrastructure is accepted. BaseRate remains BENCHMARK and Logistic remains
CHALLENGER / EXPERIMENTAL, promotion eligible NO. 2025 is CONSUMED, executions
used 1, post-holdout refit allowed NO. FF-1 is frozen at `tiaf-a7-ff1-baseline`; FLC is frozen at `tiaf-a7-flc-baseline`.
FF-2.1 governance is complete; FF-2.2 is ready for synthetic-only implementation.
Empirical development/final evaluation remain on HOLD; no fit or activation is authorized. A7 remains
IN_PROGRESS; no public forecasting capability or automatic A4/A5/A6 influence.
See the [FLC lifecycle gap/work plan](TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md).

## TIAF_A7 — Evaluation, Forecasting and Learning

**Current state: ARCHITECTURE ACCEPTED / THESIS RECONCILED /
IMPLEMENTATION IN_PROGRESS (FF-0 ACCEPTED; FF-1 SCIENTIFICALLY CLOSED INCONCLUSIVE) / INTERNAL SYNTHETIC RUNTIME IMPLEMENTED.**
The [architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md)
separates forecasting, evaluation and governed learning. Initial proposal:
one precisely defined next-session-close cash-equity return probability,
captured PIT data, logistic/held-out calibration, walk-forward controls and
shadow/advisory-only evidence. A2/A4/A5/A6 stay unchanged and callable without A7.
The [integrated roadmap](TIAF_A7_DETAILED_ROADMAP.md) contains FF-0…FF-7 under
A7 and maps the historical five-slice proposal;
the [original architecture-pass reconciliation](TIAF_A7_RECONCILIATION_RECORD.md)
preserves its 30 historical findings.
The [thesis creation record](TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md)
links the unchanged 36-chapter reference. The
[thesis reconciliation](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md) resolves all
seventeen additional findings: eleven clarifications, one constrained population-
report addition, one implementation detail, three no-change decisions and one
retained deferral. Its then-recommended next gate was independent architecture
acceptance, not implementation. The intervening FF review and explicit
[A7 integration](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md)
are now completed; A7 architecture and FF-0 are accepted; FF-1 training/evaluation
is complete and scientifically closed inconclusive; FLC completion precedes deferred FF-2. Original findings and
thesis editions remain intact, with current ownership/stages in the integrated design.

The following is the broader long-term charter, **not mandatory initial v1**:

- store recommendation before outcome
- subsequent price-path capture
- MFE / MAE
- entry quality
- exit efficiency
- confidence calibration
- deterministic baseline comparison
- human/expert comparison
- specialist performance by horizon and regime
- versioned forecast distributions and threshold probabilities
- walk-forward/out-of-sample calibration
- candidate/champion promotion and rollback

**Eventual acceptance:** forecast calibration and any claimed Agent value
versus A2 require qualified subsequent outcomes, not Agent prose. Engineering
acceptance is separate from empirical model approval; rejection of all model
candidates is valid. No A7 acceptance or measured improvement is claimed now.

## TIAF_A8 — TradeMonitor Integration

- stable service/API boundary
- TM requests opportunity/position assessments
- TIAF returns timestamped advice with TTL/freshness
- TM owns risk, authority, lifecycle and execution
- TIAF never places broker orders
- degradation/health state visible to TM
- execution/outcome feedback returns to TIAF evaluation

**Acceptance:** TIAF intelligence can influence TM without crossing TM's authority boundary.

## TIAF_A9 — Scanner Integration

- Day Scanner remains a sensor/discovery system
- Positional Scanner remains a sensor/discovery system
- TIAF enriches shortlisted/full-universe candidates
- Day Scanner gains early-opportunity vs mature-mover intelligence
- Positional Scanner gains horizon-aware forward ranking
- Google Sheet can surface TIAF consensus, confidence, expected move, evidence, invalidation and timestamp
- TIAF remains independent of the user's private Sheet/bridge setup

## TIAF_A10 — Production Hardening

- provider rate-limit handling and retries
- model/provider fallbacks
- persistent cache and restart-safe assessment store
- circuit breakers for bad/stale data
- health reporting
- latency/cost telemetry
- reassessment queue/scheduler
- versioned prompts/policies
- replay tests
- load tests across realistic F&O universe sizes
- secrets/configuration hardening

## Governing Architectural Principles

- Scanners are sensors/discovery.
- Agents are interpreters/intelligence.
- TradeMonitor is governor/risk/authority/execution coordinator.
- Broker is final truth.
- Intelligence is pluggable; authority is centralized.
- Deterministic where possible, AI where judgment is valuable.
- Time horizon is a first-class input.
- `WAIT` and `NO_TRADE` are valid outcomes.
- Watchlist-only input must eventually be sufficient.
- Underlying selection and option selection are separate problems.
- For adopted positions, TIAF is forward-looking; original entry rationale is
  optional, while A5.1 requires a current accepted A4 thesis/result.
- TIAF may improve profitability, but account safety must never depend solely on AI.

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
is **FF1_1_ACCEPTED**. Subsequent training and paired evaluation are complete.
Rights remain UNVERIFIED/WARN_ONLY, not legally approved; the adjusted vintage
remains retrospective SIMULATED research, not CAPTURED_AS_KNOWN.
FF-1 is **FF1_FINAL_CLOSURE_ACCEPTED / FF1_SCIENTIFICALLY_CLOSED_INCONCLUSIVE**.
The outcome remains **INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE**;
infrastructure is accepted. BaseRate remains BENCHMARK and Logistic remains
CHALLENGER / EXPERIMENTAL, promotion eligible NO. 2025 is CONSUMED, executions
used 1, post-holdout refit allowed NO. FF-1 is frozen at `tiaf-a7-ff1-baseline`; FLC is frozen at `tiaf-a7-flc-baseline`.
FF-2.1 governance is complete; FF-2.2 is ready for synthetic-only implementation.
Empirical development/final evaluation remain on HOLD; no fit or activation is authorized. A7 remains
IN_PROGRESS; no public forecasting capability or automatic A4/A5/A6 influence.
See the [FLC lifecycle gap/work plan](TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md).

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

Proposed next task: **FF-2.2 CALIBRATION IMPLEMENTATION — SYNTHETIC ONLY**; empirical grants and final readiness remain separate.
No commit, tag or push is performed by this documentation pass. Historical
planning/acceptance records retain their then-current status.
