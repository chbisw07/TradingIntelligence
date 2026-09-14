# TBD TI Design Notes — Idea Cache and Promotion Index

TBD documents preserve unfinished, non-authoritative thinking. They can contain
speculation, rejected/revised concepts, design questions and historical rationale.
Promotion of selected principles does not approve the entire note or implement
its product. Accepted Markdown architecture/contracts remain normative; studies
and milestone reviews describe their historical scope.

The table is the current post-R1/post-monitoring disposition, superseding this
index's older post-A3-only status summary. It does not rewrite original notes.
PROMOTED/PARTIALLY_PROMOTED below refers to design, with implementation stated
separately. ACTIVE_TBD and REVISIT_LATER do not create callable capabilities.

## Complete major-note inventory

| Note | Current classification | Authority / delivered subset / residual scope |
|---|---|---|
| [System thesis](TBD_TI_SYSTEM_ARCHITECTURE_THESIS.md) | SUPERSEDED / HISTORICAL_IDEA_CACHE | Revised kernel/capability decisions governed by [system architecture](TIAF_SYSTEM_ARCHITECTURE.md) and [pass 1](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md); preserve original rationale. |
| [Shell thesis](TBD_TI_SHELL_THESIS.md) | PARTIALLY_PROMOTED / HISTORICAL_IDEA_CACHE | [Shell review](TIAF_POST_A4_PRE_A5_TI_SHELL_ARCHITECTURE_REVIEW.md) classifies all 33 sections. Command-first local [v0.1](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md) and A5.2 position exposure are implemented; NLP/mixed/model/product ideas remain TBD. |
| [CLI/Web interaction](TBD_TI_CLI_WEB_UI_INTERACTION_ARCHITECTURE.md) | PARTIALLY_PROMOTED / REVISIT_LATER | Governed local commands implemented through [Shell architecture](TIAF_TI_SHELL_ARCHITECTURE.md); Web/remote transport needs an actual consumer and DEF-003/054 gates. |
| [Source/provenance/citation](TBD_TI_SOURCE_PROVENANCE_CITATION_FABRIC.md) | PARTIALLY_PROMOTED / HISTORICAL_IDEA_CACHE | [Source architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md) and [pass 2](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md) govern Core semantics, implemented by the foundation. Bounded Shell rendering exists; rich citation/bibliography/Web remains DEF-054. |
| [Deployment](TBD_TI_DEPLOYMENT_ARCHITECTURE.md) | PARTIALLY_PROMOTED / HISTORICAL_IDEA_CACHE | [Deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md) and [review](TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md) govern local hosting and conditional adoption gates; no service/queue/DB rollout is implied. |
| [Original monitoring](TBD_TI_MONITORING_ARCHITECTURE.md) | PARTIALLY_PROMOTED / HISTORICAL_IDEA_CACHE | [Monitoring architecture](TIAF_MONITORING_ARCHITECTURE.md) reconciles all 25 sections. A5 advisory intent is implemented; future subscriber mandates, lifecycle and scheduling design do not deliver runtime. |
| [Subscriber monitoring v2](TBD_TI_MONITORING_ARCHITECTURE_V2.md) | PARTIALLY_PROMOTED / HISTORICAL_IDEA_CACHE | All 49 sections classified under the same authoritative monitoring design. Required subscription hierarchy and scope-erasing availability intersection rejected/revised; leases/adaptive/event mechanisms remain gated. |
| [Pluggability](TBD_TI_PLUGGABILITY_ARCHITECTURE.md) | PARTIALLY_PROMOTED / HISTORICAL_IDEA_CACHE | [Pluggability architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md) governs HOT ⇒ COLD ⇒ STRUCTURAL. Audit/R1–R5 accepted/done; HOT remains DEF-057. No universal registry delivered. |
| [Forecasting/ensemble/learning](TBD_TI_FORECASTING_ENSEMBLE_LEARNING_ARCHITECTURE.md) | RECONCILED_IN_A7_DESIGN / RESIDUAL_TBD | [A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md), [original dispositions](TIAF_A7_RECONCILIATION_RECORD.md#forecasting-idea-note-disposition) and [thesis reconciliation](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md) now link the [FF integration](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md); historical findings remain preserved. Intervening [FF platform ACCEPTED](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md), miniature DEFINED; FM/LFDE advanced family and thesis retained. FF THESIS RECONCILED; FF ARCHITECTURE ACCEPTED; FFA-B01 CLOSED; A7 integration RECONCILED; A7 ARCHITECTURE ACCEPTED; IMPLEMENTATION NOT_STARTED; RUNTIME NOT_IMPLEMENTED. Broad families remain gated; no autonomous activation. |
| [Sector Rotation](TBD_TI_SECTOR_ROTATION_INTELLIGENCE_ARCHITECTURE.md) | ACTIVE_TBD / REVISIT_LATER | Future cross-sectional engine, not existing A3.6 sector-context interpretation. Exact milestone placement remains TBD; proposed A7.0/A7.x/SR labels are not authoritative. |
| [Signal Qualification](TBD_TI_SIGNAL_QUALIFICATION_FALSE_SIGNAL_SUPPRESSION_ARCHITECTURE.md) | ACTIVE_TBD / REVISIT_LATER | Intended revisit after Sector Rotation review unless explicitly reordered. Proposed thresholds/probability objectives are unvalidated; signal.qualify is not callable. |

## Revisit and authority rules

Reopen a note at its owning milestone or a separately approved bounded review.
Reconcile it with current contracts, architecture, source rights, replay, budgets,
authority and implementation evidence. Record promoted, revised, rejected and
remaining ideas explicitly; retain historical bodies and acceptance findings.

The post-A3 [consolidation](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md),
[pass 3](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md)
and later A4/A5 closures remain historical transition records, not instructions
to restart completed work. Current scheduling belongs to the
[implementation roadmap](IMPLEMENTATION_ROADMAP.md), with details in the
[A4](TIAF_A4_DETAILED_ROADMAP.md) and [A5](TIAF_A5_DETAILED_ROADMAP.md) roadmaps.
Stable obligations remain in the [deferral register](TIAF_DEFERRAL_REGISTER.md);
a non-authoritative idea alone does not justify a duplicate DEF record.

No idea-cache body or DOCX companion is deleted or rewritten by this index
refresh. The [architecture index](ARCHITECTURE.md) leads to normative documents.

<a id="forecasting-framework--a7-integrated-architecture-acceptance-next"></a>

## Forecasting Framework and A7 — architecture accepted; sequencing next

The [A7 acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) records
**A7_ARCHITECTURE_ACCEPTED** on **2026-09-15 (Asia/Kolkata)**:
A6 FROZEN; FF ARCHITECTURE ACCEPTED; A7 ARCHITECTURE ACCEPTED;
A7 THESIS RECONCILED AS NEEDED; A7 / FF IMPLEMENTATION NOT_STARTED;
RUNTIME NOT_IMPLEMENTED. FM/LFDE remains an optional advanced Forecaster family.

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

Exact next prompt: **TIAF A7 — IMPLEMENTATION SEQUENCING AND FF-0 MINIATURE REALIZATION PLAN**.
This is a planning gate, not implementation readiness or authorization to train,
approve models, publish capabilities, change frozen A6 or begin A8.
