# TIAF A7 — Architecture Reconciliation Record

## Current navigation — A7 architecture accepted

**2026-09-15 (Asia/Kolkata): A6 FROZEN; FF ARCHITECTURE ACCEPTED;
A7 ARCHITECTURE ACCEPTED; A7 THESIS RECONCILED AS NEEDED;
A7 / FF IMPLEMENTATION NOT_STARTED; RUNTIME NOT_IMPLEMENTED.**

The [independent A7 acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) follows the
[FF integration reconciliation](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md).
The [A7 roadmap](TIAF_A7_DETAILED_ROADMAP.md) maps the old five-slice proposal
to FF-0…FF-7 within A7. FF owns forecasting contracts/runtime/composition;
Evaluation owns truth/qualification/linkage; Learning owns candidate artifacts
and lifecycle history. Independent approval and trusted COLD selection remain
separate. FM/LFDE remains an optional advanced Forecaster family.

The [bounded FF-0 implementation plan](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md) is complete
(**READY_FOR_FF0_IMPLEMENTATION**, planning only). It chooses synthetic captured-input
BaseRate mechanics, four FF-0 steps and a 28-case acceptance corpus. FF-0.1 is
next only under a separate implementation request; calibration stays at FF-2,
public capability publication stays separate, and runtime remains NOT_IMPLEMENTED.

Exact next prompt: **TIAF A7 / FF-0.1 — CONTRACTS, TARGET AND CLOCK FOUNDATION IMPLEMENTATION**.
Everything below is the preserved earlier record, including then-current status,
stage labels, findings and validation counts. Neither those historical labels
nor this navigation update authorize implementation, training, live work or A8.
No thesis DOCX/PDF, authoring assets or original finding disposition is rewritten.

## Subsequent thesis reconciliation — current navigation

The [17-finding thesis reconciliation](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md)
now updates the [proposed normative architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md).
Current status: **A6 FROZEN; A7 ARCHITECTURE RECONCILED; THESIS RECONCILED;
ARCHITECTURE ACCEPTANCE NEXT; RUNTIME NOT_IMPLEMENTED**. It adopts TF-09's
Evaluation-owned population report with constraints and clarifies the calendar,
PIT, calibration, approval, health and replay boundaries. This is not independent
acceptance. The original 30 findings and then-next decision below are preserved
as the **historical architecture-pass record**, including its clean entry state.
They do not describe this later pass's already-dirty worktree.

Current exact next prompt:
**TIAF A7 — FORECASTING, EVALUATION & LEARNING ARCHITECTURE ACCEPTANCE**.

## Review scope and evidence

**2026-09-14 (Asia/Kolkata), documentation-only.** Entry worktree was clean.
HEAD and `tiaf-a6-baseline^{}` both resolve to
`6dc2ff304aae0e87540260b092919bb91e4d4189`; A5 tag resolves to
`167c51d40985e70e422df14af4a67531f8f66a65`. A6 is FROZEN; A7 architecture is
now DRAFT and runtime remains NOT_IMPLEMENTED. No training/live provider/model/
broker calls, changes to source/tests/packaging or Git publication in this pass.

The attached A7 brief supplied the requested architecture scope, not authority
to implement future example capabilities or mutate accepted baselines. Repository
code/contracts and current normative documents govern inherited meaning;
historical reviews retain their dated acceptance claims. This record documents
focused relevant-section inspection and source/test searches, not a claim to
have re-executed historical acceptance or exhaustively reviewed every source line.

## Source map

| Ref | Inspected source / relevant sections | Finding used |
|---|---|---|
| S01 | [README](../README.md), [MILESTONES](MILESTONES.md), [forward queue](IMPLEMENTATION_ROADMAP.md), [major roadmap](TRADINGINTELLIGENCE_ROADMAP.md), [engineering targets](TIAF_IMPLEMENTATION_TARGETS.md) | Current status/sequence and broad A7 charter; deterministic A6 precedes optional forecasting; A8/A9/A10 order preserved |
| S02 | [Architecture index](ARCHITECTURE.md), [thesis](TIAF_THESIS.md), [system boundary](TIAF_SYSTEM_ARCHITECTURE.md), [capability map](TIAF_CAPABILITY_MAP.md) | TI_CORE/consumer authority, nine-operation catalog; some lower narrative paragraphs still called implemented A6 future |
| S03 | [Ecosystem architecture](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md), [monitoring architecture](TIAF_MONITORING_ARCHITECTURE.md) | Scanner discovery, TI advice, TM operations and broker truth; monitoring is a separate unimplemented recurring runtime |
| S04 | [Source authority/provenance/contradiction](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md), especially forecast disagreement and revisions/time | Model confidence is not source authority; late acquisition cannot rewrite decision knowledge; forecasts remain distinct propositions |
| S05 | [A2.9 baseline](TIAF_A2_9_DETERMINISTIC_BASELINE.md), [A2.10 replay/evaluation](TIAF_A2_10_REPLAY_VALIDATION_EVALUATION.md) | Frozen component evidence/NO_TRADE; snapshot/run/outcome separation; observed excursions and captured replay, not arbitrary PIT or simulated execution |
| S06 | [A3 architecture](TIAF_A3_ARCHITECTURE.md), [A3.8 orchestration](TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md), [A3.9 product](TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md), [A3.10 hardening](TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md) | Forecast-consumer placeholder, calibrated evidence outside LLMs, individual opinions/gaps, replay modes and observational—not empirical-value—comparison |
| S07 | [A4 architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md), [A4 closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) | Arbitration ownership, no probability creation, separately governed forecast-enhanced candidate comparison |
| S08 | [A5 architecture](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md), [A5 closure](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md) | Current single-position advice without forecasts; future optional seam cannot mutate operational truth or become a scheduler |
| S09 | [A6 architecture](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md), [architecture acceptance](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md), [A6.4 hardening/freeze record](TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md) | Bounded deterministic long single-leg CE/PE, exact evidence/admission gates and lexicographic rank; no learned score/POP/utility; actual baseline tag verified independently |
| S10 | [R1](TIAF_PLUGGABILITY_R1_REQUIRED_SCOPE_EXPLICIT_ABSENCE.md), [R2](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA.md), [R3](TIAF_PLUGGABILITY_R3_COMPOSITION_ENVELOPE_PINNED_VERIFIER.md), [R4](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION.md), [R5](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md) | Required scope independent of bindings, descriptive discovery, exact pinning, optional imports, trusted COLD ownership; old catalog counts are historical |
| S11 | [Shell architecture](TIAF_TI_SHELL_ARCHITECTURE.md) | Closed grammar/caller-bound facade/rendering; no intelligence, trainer, registry backend or provider in Shell |
| S12 | [Deferral register](TIAF_DEFERRAL_REGISTER.md), all relevant rows and closure notes | Calendar/actions/PIT, outcome acquisition, optimization/options/ranking, scale, pricing, HOT and new peer publication remain separate obligations |
| S13 | [Forecasting/ensemble idea note](TBD_TI_FORECASTING_ENSEMBLE_LEARNING_ARCHITECTURE.md), [TBD index](README_TBD_DESIGN_NOTES.md) | Precise tasks, controls and governed learning retained; mandatory laboratory/ensemble hierarchy and broad initial task catalog not adopted |
| S14 | [Signal Qualification idea note](TBD_TI_SIGNAL_QUALIFICATION_FALSE_SIGNAL_SUPPRESSION_ARCHITECTURE.md), [Sector Rotation idea note](TBD_TI_SECTOR_ROTATION_INTELLIGENCE_ARCHITECTURE.md) | Separate future capabilities; no speculative A7.0/SR renumbering or circular current-run meta-labeling |
| C01 | [Agent contracts](../src/tiaf/agents/models.py), [forecast serialization tests](../tests/unit/agents/test_budget_forecast_serialization.py) | Existing `ForecastEvidence` checks calibration metadata but not empirical validity or exact path/endpoint semantics; synthetic six-month example is not trained performance |
| C02 | [Evaluation models](../src/tiaf/evaluation/models.py), [outcome calculations](../src/tiaf/evaluation/outcome.py), [metrics](../src/tiaf/evaluation/metrics.py), [outcome tests](../tests/unit/evaluation/test_outcome.py), [golden/store tests](../tests/unit/evaluation/test_regression_store_architecture.py) | `complete` is retained independently of observed excursion calculation; A7 needs separate label eligibility; NO_TRADE directional MFE/MAE stays absent |
| C03 | [A3 hardening evaluation](../src/tiaf/a3_hardening/evaluation.py), [cost/failure tests](../tests/unit/a3_hardening/test_cost_failure_evaluation.py) | Package replay/comparison/cost checks are not model calibration or predictive-value validation |
| C04 | [Facade catalog](../src/tiaf/facade/capabilities.py), [A6 regression boundaries](../tests/unit/a6/test_regression_boundaries.py), [A4 boundary tests](../tests/unit/a4/test_replay_failures_and_security.py), [A5 boundary tests](../tests/unit/a5/test_replay_and_boundaries.py) | Nine static operations; A6 source is `tiaf.trade_expression`, A5 is `tiaf.a5`; model/broker/forecast authority remains outside current policies |

Search terms included forecast, probability, calibration, expected return,
expected utility, learning, evaluation, backtest, walk-forward, leakage,
point-in-time, label, outcome, model, drift, promotion, benchmark,
counterfactual and rejected signal. Broad terms were narrowed to relevant
forecast/evaluation contracts and boundary tests, not treated as evidence that
every occurrence is an A7 implementation. No forecaster/trainer/registry
capability is in the current facade catalog.

## Reconciliation matrix

Classification records the finding **at entry**. Resolution is a proposal where
it adds A7 semantics; it does not retroactively accept a new architecture.

| ID | Classification | Sources / finding | Disposition in A7 draft | Owner / implementation impact |
|---|---|---|---|---|
| R01 | ALREADY_DECIDED | S01/S02: A7 is an optional overlay after frozen A6 | Preserve A2–A6 controls and fingerprints; A7 unavailable cannot disable the valid deterministic path | TI boundaries; unchanged |
| R02 | ALREADY_DECIDED | S04/S06: confidence/interpretation differs from calibrated forecast | No probabilities from LLM prose, source prestige or policy score | Forecast/evidence semantics |
| R03 | ALREADY_DECIDED | S05/C02: outcome separate from frozen decision | Append-only journal linked by identity; do not insert future path into input | Evaluation |
| R04 | ALREADY_DECIDED | S05/S06: captured replay is not arbitrary historical PIT | CAPTURED_AS_KNOWN initial eligibility; historical research labeled separately | Dataset owner; DEF-049 open |
| R05 | ALREADY_DECIDED | S07–S09: A4/A5/A6 own separate decisions | Forecast is future admitted input only; no v1 automatic influence | Consumer owners |
| R06 | ALREADY_DECIDED | S03: TM/broker and recurring Monitoring ownership | No capital, orders, position mutation, scheduler or autonomous retraining | A8/A10 external boundary |
| R07 | ALREADY_DECIDED | S10/S11: R1–R5 and Shell constraints | Scoped requiredness, COLD pins, SDK isolation, caller-bound Shell | Core/bootstrap/facade |
| R08 | NEEDS_RECONCILIATION | C01: broad Horizon and threshold “reaches” cannot name exact terminal event | Add proposed exact `ForecastEvidenceV2`; no automatic V1 conversion or old hash change | A7.1 then future consumer projection |
| R09 | NEEDS_RECONCILIATION | S13: rich distribution/ensemble hierarchy could become mandatory v1 | One binary endpoint target and logistic/sigmoid; hierarchy/distributions deferred | Architecture narrowing |
| R10 | NEEDS_RECONCILIATION | S01/S06: broad scorecards/cross-candidate/human comparison read as initial scope | Preserve long-term charter; v1 matched descriptive controls only; unsupported comparisons NOT_EVALUABLE | A7 evaluation; DEF-053 |
| R11 | NEEDS_RECONCILIATION | C02: partial-path excursions exist but supervised labels need completeness | Reuse factual records; add measure-specific eligibility, never change A2.10 calculation | A7 labeler |
| R12 | NEEDS_RECONCILIATION | S02/S03: current lower prose still calls A6 future | Update current navigation/ownership wording to frozen captured-read A6; retain dated acceptance narratives | Docs only |
| R13 | NEEDS_RECONCILIATION | S02: exploratory `forecast.return` might look like a reserved public ID | Prefer proposed `forecast.assess`; no alias/reservation/publication; catalog stays nine | A7.4 separately gated |
| R14 | NEEDS_RECONCILIATION | S08/S13: economic-utility objective could imply v1 numeric estimator | Keep objective; binary sign alone cannot estimate expected monetary utility or option POP | Explicit NOT_ESTIMABLE |
| R15 | NEW_A7_DECISION_REQUIRED | S01/S13: exact target/window not previously fixed | Strict next-session-close return > 0 for qualified NSE cash equity; flat is 0; supplied session schedule | A7.1 |
| R16 | NEW_A7_DECISION_REQUIRED | S05/S12: training eligibility not supplied by replay | Dated universe, first-capture/availability, source revisions, action exclusions and rights | A7.1 dataset gate |
| R17 | NEW_A7_DECISION_REQUIRED | S13: experimental separation unspecified | Chronological train/calibration/validation/test and forward shadow; dependency-interval purge/embargo | A7.1/2 |
| R18 | NEW_A7_DECISION_REQUIRED | S05: untraded/censored/ambiguous labels need distinct semantics | Independent selection/window/eligibility axes and immutable corrected labels | A7 journal |
| R19 | NEW_A7_DECISION_REQUIRED | S13: calibration/control implementation not chosen | Held-out sigmoid, base rate and logistic controls, reliability/proper scores/coverage | A7.2 |
| R20 | NEW_A7_DECISION_REQUIRED | S13: promotion/drift thresholds not validated | Preregister full numerical protocol in A7.1; no empirical gate passes with unknown parameters/evidence | Evaluation reviewer |
| R21 | NEW_A7_DECISION_REQUIRED | S10/S13: model lifecycle not delivered | Local immutable registry/events, explicit shadow/advisory approval, no decision-active v1 | A7.3 |
| R22 | NEW_A7_DECISION_REQUIRED | S06/S10: trained-model verification needs extra pins | Exact recorded replay separate from pinned inference and fit reproduction/tolerance reports | A7.3 |
| R23 | NEW_A7_DECISION_REQUIRED | S11/S13: user surface and cost not bounded | Minimal proposed assess/evaluate; registry inspection engineering; local finite budgets; thesis before acceptance | A7.4 / governance |
| R24 | EXPLICITLY_DEFERRED | S12: calendar, actions, historical qualification | Define input gates, not source procurement or arbitrary-history reconstruction | DEF-007/013/049 |
| R25 | EXPLICITLY_DEFERRED | S12: options probabilities/distributions/path risk | No direction-to-POP conversion; independent label/data/model acceptance required | DEF-040–044 |
| R26 | EXPLICITLY_DEFERRED | S12/S13: indicator optimization, ensembles, ranking | No A2 retuning, learned A4 weights, ensemble hierarchy or cross-candidate v1 | DEF-024/053; later A7 design |
| R27 | EXPLICITLY_DEFERRED | S12: scale, acquisition, LLM/pricing, HOT/public peers | No distributed store, scheduler, model Challenger, automatic egress or hot updates | DEF-050/051/052/055/057/058 |
| R28 | OUT_OF_SCOPE | S03/S14: Scanner, Sector Rotation, Signal Qualification runtime | Acyclic future seams only; no new milestone numbers | Separate capabilities / A9 |
| R29 | OUT_OF_SCOPE | S03/S11: TM, broker, remote Web/NLP, SigmaDSL | Preserve external authority; no services or execution; no current learning of operational policy | A8/A10 and separate products |
| R30 | OUT_OF_SCOPE | S01/S13: training/live validation/policy tuning during architecture | No trained model, promoted artifact, live calls or performance claim | This pass docs only |

Summary: **30 findings** — 7 ALREADY_DECIDED, 7 NEEDS_RECONCILIATION,
9 NEW_A7_DECISION_REQUIRED, 4 EXPLICITLY_DEFERRED, 3 OUT_OF_SCOPE. All are
dispositioned; empirical protocol values/source availability remain gated
choices, not hidden architecture acceptance or implementation claims.

## Forecasting idea-note disposition

The exploratory note remains historical/non-normative. Its body is not rewritten
to make proposed implementation appear delivered.

| Note sections | Disposition |
|---|---|
| 1–3 purpose, controls and concept separation | Retain principles; replace broad “laboratory plus production ensemble” with three bounded layers |
| 4–5 method configuration/model families | Retain exact identities and replaceability; use trusted COLD allowlists, not user checkbox authority or arbitrary plugins; conservative logistic first |
| 6–10 task taxonomy, horizons, attributes, batch and funnel ensemble | Choose one exact endpoint target; custom horizons, broad outputs, batch ranking and hierarchical ensembles deferred |
| 11–12 regime/cross-sectional designs | Retain PIT applicability and stratified evaluation; no regime engine or ranking implementation |
| 13–14 scorecards and controls | Retain, but distinguish proper probability metrics from ordinal policies and from causal/economic claims |
| 15–16 ensembles/distribution output | Deferred; a calibrated binary target is sufficient for v1; no mandatory hierarchical ensemble |
| 17–19 calibration/PIT/evaluation | Retain and make split, availability, label and calibration gates explicit |
| 20–22 feedback/promotion/retraining | Retain append-only learning; explicit shadow/advisory approval and COLD activation; no autonomous promotion |
| 23 RL | Remains deferred; not initial engine or TM policy optimizer |
| 24–25 headless output and cost/performance | Retain Core-owned objects and consumer visualization; closed local Shell first, finite local budgets and tiered complexity, no Web service |
| 26–28 milestone/questions/principle | A7 draft/roadmap now owns bounded answers; empirical choices and advanced families retain explicit gates |

## Deferral disposition and non-closure

No stable ID is removed, renumbered or marked implemented by architecture.
The existing register retains **DEF-001 through DEF-058**. A7 proposals are
near-term roadmap work, not duplicate new deferrals. The register's A7 note
records these carry-forwards:

- DEF-007/013/049: qualified supplied calendars/action coverage and captured
  datasets are prerequisites, not proof of solved historical-data infrastructure.
- DEF-024/044/053: broader optimization, expected-move/POP and cross-candidate
  ranking remain outside the selected v1; ownership/revisit retained.
- DEF-040–043 and DEF-014: historical option features/chain timing/term structure/
  surfaces not inferred from a one-session equity label.
- DEF-010/050/051: no recurring outcome acquisition, scheduler or distributed
  store; A7 defines outcome/drift semantics, A10 operationalizes later.
- DEF-052/055: classical local prediction is not production LLM reasoning;
  compute/resource usage does not fabricate monetary pricing.
- DEF-057/058: no HOT transition or new peer publication; A7.4 must resolve the
  specifically needed projection/admission without claiming universal closure.
- DEF-003/004/005/025/054/056: no remote service, TM/broker operation, SigmaDSL,
  rich Web/NLP or multi-leg A5 extension.

## Documentation changes and validation scope

New primary documents: [architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md),
[roadmap](TIAF_A7_DETAILED_ROADMAP.md), and this reconciliation record.
Current navigation/status is synchronized in README, MILESTONES,
IMPLEMENTATION_ROADMAP, TRADINGINTELLIGENCE_ROADMAP, TIAF_IMPLEMENTATION_TARGETS,
TIAF_CAPABILITY_MAP, TIAF_DEFERRAL_REGISTER, ARCHITECTURE, TIAF_SYSTEM_ARCHITECTURE,
TIAF_THESIS, TIAF_TRADING_ECOSYSTEM_ARCHITECTURE and README_TBD_DESIGN_NOTES.
A dated pointer in the forecasting TBD note directs readers to the new draft;
its historical body and earlier acceptance records remain unchanged.

Observed documentation validation:

| Check | Result |
|---|---|
| `git diff --check` | PASS; new Markdown files additionally checked against an empty file |
| Changed-document local Markdown links | PASS: 671 local targets, including 7 heading-anchor references; no missing target or anchor |
| Canonical deferral register | PASS: all 58 rows, IDs and statuses exactly equal to entry HEAD; only a disposition section added |
| Reconciliation matrix | PASS: 30 unique ordered findings; classification counts match the summary |
| Current status/navigation | PASS: 10 current status documents link the draft and retain A7 runtime NOT_IMPLEMENTED; no stale A7 ACTIVE / NEXT claim there |
| Scope | PASS: 16 Markdown files (13 updated, 3 new); no source, tests, scripts, configuration, dependency or binary artifact changes |
| Catalog/baseline | PASS: unchanged static nine-operation catalog; HEAD and A6 baseline tag unchanged |

The link/integrity checks used read-only local `python3` scripts; the bare
`python` executable is not on this shell's PATH. No full pytest/compile/lint/type
suite is needed for a docs-only design pass; none was run or claimed. No model
training, live validation, empirical metric or rendered-diagram test is claimed.

## Historical architecture-pass decision and remaining gates

**READY_FOR_A7_THESIS_OR_ACCEPTANCE.** Recommend the thesis first, not immediate
implementation. The draft resolves ownership/scope/compatibility conflicts;
it does not prove that a qualified dataset exists or that logistic forecasting
will outperform the control. Failure to establish those facts must yield
ineligible data or an unapproved model, not weaker standards.

Remaining bounded choices: actual data rights/availability and calendar/action
coverage; exact A2 feature schema; preregistered sample/calibration/improvement/
drift/shadow thresholds; pinned fit dependency and machine budgets; future
projection/publication versions. Their owners and blocking stages are in the
[roadmap](TIAF_A7_DETAILED_ROADMAP.md#unresolved-choices-and-gates).

**Historical architecture-pass next prompt title:**
**TIAF A7 — FORECASTING, EVALUATION & LEARNING THESIS CREATION**.

No implementation readiness, trained model, A7 consumer integration or Git
publication is asserted by this architecture decision.
