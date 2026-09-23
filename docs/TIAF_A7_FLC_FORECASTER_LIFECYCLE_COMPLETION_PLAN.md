# A7 — Forecaster Lifecycle Completion: gap baseline and bounded plan

**Subsequent implementation checkpoint:** [FLC-1 inference/identity seams and
validation](TIAF_A7_FLC_1_FORECASTER_CONTRACT_AND_LIFECYCLE_SEAM_NORMALIZATION.md)
are now implemented. [FLC-2 training/custody/lifecycle normalization](TIAF_A7_FLC_2_TRAINING_MODEL_IDENTITY_PERSISTENCE_AND_LIFECYCLE_NORMALIZATION.md)
is also implemented. [FLC-3 bounded synthetic-only optimization](TIAF_A7_FLC_3_BOUNDED_DEVELOPMENT_ONLY_OPTIMIZATION.md)
now extends that same training service with a separately versioned worker and
artifact adapter. [FLC-4 model-specific diagnostics](TIAF_A7_FLC_4_MODEL_SPECIFIC_DIAGNOSTICS_NORMALIZATION.md)
now adds common internal request/envelope semantics with typed BaseRate and
Logistic payloads, existing custody and offline replay.
[FLC-5 calibration composition readiness](TIAF_A7_FLC_5_CALIBRATION_COMPOSITION_READINESS.md)
adds separate raw/transformed outputs, a synthetic-only reference wrapper and
offline replay without fitting or lifecycle authority. FLC-6 reusable independent
evaluation normalization is next under separate authorization; FF-2 remains
deferred. The FLC-0 baseline, gap classifications and counts below are
retained as historical evidence, not current missing-feature claims.

## Decision, scope and evidence baseline

**FLC-0 DOCUMENTATION / GAP PLAN COMPLETE; GO for separately requested FLC-1.
FLC implementation NOT_STARTED. FF-2 intentionally DEFERRED / NOT_STARTED until
FLC closes and a new governed research proposal is accepted.**

Reviewed 2026-09-22 (Asia/Kolkata). Entry branch `main`, clean worktree, HEAD and
`tiaf-a7-ff1-baseline^{}` both `21783ea31d4ce3b54fbcc6fcce6ef7e641bd5bec`.
Local `origin/main` matches (0 ahead / 0 behind); no remote fetch/push in this pass.
FF-0 remains frozen at `tiaf-a7-ff0-baseline`. User reports FF-1 was pushed;
local refs substantiate the synchronized baseline, not a new remote query.

**FLC**, rather than the suggested FFA, avoids collision with existing FFA-B01
and FFA-C01–C04 architecture findings. It is one bounded intervening A7 completion
track using Logistic as the only learned reference, not FF-1 reopening or FF-stage
renumbering. Normative architecture lives in [FF §22](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#22-forecaster-lifecycle-completion-flc);
this document owns repository gaps/packages, not a competing architecture.
[A7](TIAF_A7_DETAILED_ROADMAP.md) owns the umbrella crosswalk and the
[FF roadmap](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) owns delivery gates.

The [independent FF-1 closure](TIAF_A7_FF1_INDEPENDENT_FINAL_SCIENTIFIC_CLOSURE_AND_BASELINE_DECISION.md)
and [final evaluation](TIAF_A7_FF1_ONE_SHOT_PROTECTED_2025_FINAL_HOLDOUT_EVALUATION.md)
are unchanged. Final N=249; Logistic-minus-BaseRate Brier difference
-0.012847910, frozen 97.5% CI [-0.028089925, 0.004386873]; log-loss difference
-0.026183193, CI [-0.057021058, 0.008685324]. These are rounded recorded values,
not recomputed metrics. Both intervals cross zero. The reference implementation
role is an engineering choice, not empirical superiority.

```text
FF1_FINAL_CLOSURE_ACCEPTED
FF1_SCIENTIFICALLY_CLOSED_INCONCLUSIVE
FF1_SCIENTIFIC_OUTCOME = INSUFFICIENT_EVIDENCE
SCIENTIFIC_REASON = CONFIDENCE_NONDECISIVE
FF1_INFRASTRUCTURE_ACCEPTED = YES
BASERATE_ROLE = BENCHMARK
LOGISTIC_ROLE = CHALLENGER / EXPERIMENTAL
LOGISTIC_PROMOTION_ELIGIBLE = NO
FF2_CALIBRATION_RESEARCH_ELIGIBLE = YES (new governed proposal only)
PROTECTED_HOLDOUT_STATUS = CONSUMED
FINAL_HOLDOUT_EXECUTIONS_USED = 1
POST_HOLDOUT_REFIT_ALLOWED = NO
```

| Preserved canonical identity | Fingerprint |
| --- | --- |
| Protocol | `2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814` |
| Execution | `2948bc46874f8196c535720bd4f7882f6293fc96077acb563e2e11409c3e4840` |
| Final evaluation | `8c0556e7b88284c170db57d745de7ece707d365ab52a585db5ebb0d3e81a7d0e` |
| COMPLETE ledger | `630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583` |

## Repository findings and assessment

The platform is not missing its entire lifecycle. FF-0 has a pure BaseRate
protocol/registry, admitted support, COLD runtime, capture, independent truth and
recorded versus pinned replay. FF-1 has separately versioned research inputs,
fixed optional isolated training, declarative scaler/coefficients, native numeric
reconstruction, walk-forward captures, paired evaluation and final custody.
The missing piece is reusable family-neutral lifecycle integration, not a new
scientific engine or a rewrite of these accepted implementations.

Evidence locators below are relative to the repository. The named symbols and
tests distinguish implemented bounded behavior from broader architecture intent.

| Ref | Inspected implementation / evidence |
| --- | --- |
| S1 | [forecasters.py](../src/tiaf/forecasting/forecasters.py): `Forecaster`, `ForecasterDescriptor`, `HistoricalBaseRateForecaster`, exact static registry. Descriptor literals and `AdmittedSupport` are BaseRate-specific. |
| S2 | [contracts.py](../src/tiaf/forecasting/contracts.py), [runtime_contracts.py](../src/tiaf/forecasting/runtime_contracts.py), [runtime.py](../src/tiaf/forecasting/runtime.py): immutable FF envelopes and synthetic-only COLD profiles. |
| S3 | [forecast_artifacts.py](../src/tiaf/learning/forecast_artifacts.py): fixed `LogisticConfig`, `TrainingGrant` / `FifthFoldGrant`, `FoldManifest`, `LogisticArtifact`, `Reconstruction`, `reconstruct`. |
| S4 | [forecast_training.py](../src/tiaf/learning/forecast_training.py), [forecast_jobs.py](../src/tiaf/learning/forecast_jobs.py), [forecast_worker.py](../src/tiaf/learning/forecast_worker.py): approved-input checks, isolated bounded optional sklearn fit, train-only scaling, native output. |
| S5 | [logistic_projection.py](../src/tiaf/forecasting/logistic_projection.py), [logistic_forecasts.py](../src/tiaf/forecasting/logistic_forecasts.py), [logistic_store.py](../src/tiaf/forecasting/logistic_store.py): outcome-blind projection, fixed research-v2 singleton, captured requests/results and bounded content-addressed store. |
| S6 | [forecast_truth.py](../src/tiaf/evaluation/forecast_truth.py), [forecast_linkage.py](../src/tiaf/evaluation/forecast_linkage.py), [forecast_retrospective.py](../src/tiaf/evaluation/forecast_retrospective.py), [research_baserate.py](../src/tiaf/forecasting/research_baserate.py): shared endpoint semantics, qualified research truth and retained control. |
| S7 | [forecast_comparison.py](../src/tiaf/evaluation/forecast_comparison.py), [forecast_comparison_metrics.py](../src/tiaf/evaluation/forecast_comparison_metrics.py), [forecast_final_scoring.py](../src/tiaf/evaluation/forecast_final_scoring.py): common losses, fixed reliability bins, paired masks/denominators and dependent-block uncertainty. |
| S8 | [forecast_final_protocol.py](../src/tiaf/evaluation/forecast_final_protocol.py), [forecast_final_custody.py](../src/tiaf/evaluation/forecast_final_custody.py), [forecast_final_store.py](../src/tiaf/evaluation/forecast_final_store.py): fixed final protocol, one-shot custody and sealed ledger. |
| S9 | [identity.py](../src/tiaf/forecasting/identity.py), [capture.py](../src/tiaf/forecasting/capture.py), [replay.py](../src/tiaf/forecasting/replay.py), [execution.py](../src/tiaf/forecasting/execution.py): canonical hashes, capture closure, recorded versus exact pinned operations. |
| T1 | [training tests](../tests/unit/forecasting/test_logistic_training.py), [admission tests](../tests/unit/forecasting/test_logistic_training_admission.py): fixed/no-tuning config, constants, reconstruction, timeout, optional imports, storage and grants. |
| T2 | [forecast tests](../tests/unit/forecasting/test_logistic_forecasts.py), [runtime/replay tests](../tests/unit/forecasting/test_pinned_runtime_replay.py): outcome-blind generation, no fit/network, tamper, fixed schema and offline replay. |
| T3 | [final tests](../tests/unit/evaluation/test_final_holdout.py), [protocol tests](../tests/unit/evaluation/test_final_protocol.py): synthetic one-shot, evidence preservation and scientific decision fixtures. |

In particular, Logistic has no implementation of S1's generic-looking protocol;
it uses `ResearchForecastRequest/Result` and `reconstruct`. Do not describe it as
already a registered FF-0 primitive. Persistence already works without sklearn
or pickle; a common codec/binding adapter is the gap, not another database.
Current model role/lifecycle are fixed CHALLENGER/EXPERIMENTAL literals, not an
implemented general approval/event service. Existing scientific fingerprints are
not a fully reusable experiment registry. Calibration is designed in FF §8/A7 §8,
but no fitted reusable calibrator is implemented. Reliability bins already exist;
a reusable calibrated-pipeline qualification report and ECE contract do not.

## Gap matrix

EXISTS means bounded behavior at the inspected baseline, not universal readiness.
EXISTS_BUT_NEEDS_REFACTOR means additive normalization/adaptation for future work,
never changing a sealed FF-1 configuration. PARTIAL means some mechanics exist
but the reusable contract/test closure does not. MISSING is absent implementation;
NOT_NEEDED_NOW is deliberately excluded, not a hidden acceptance requirement.

| Capability | Classification | Evidence / bounded gap | Package |
| --- | --- | --- | --- |
| Generic forecaster contract | EXISTS_BUT_NEEDS_REFACTOR | S1 protocol is BaseRate-specific; add neutral sibling seam, retain v1 | FLC-1 |
| Logistic forecaster compliance | PARTIAL | S3/S5 pure numeric predictor exists, not S1-compatible | FLC-1/2 |
| Model identity | EXISTS | S3 exact artifact and scientific hashes, family/version | Preserve; FLC-2 adapter |
| Model versioning | PARTIAL | S3 fixed version; new-version dispatch/lineage not reusable | FLC-1/2 |
| Feature schema identity | EXISTS | S3/S5 ordered five fields, schema/profile/value pins | Preserve; FLC-1 tests |
| Training lifecycle | EXISTS_BUT_NEEDS_REFACTOR | S4 bounded jobs, but FF-1-specific grants/populations | FLC-2 |
| Model freeze | EXISTS | S3/S8 immutable seals, protocol and custody | Preserve; FLC-2/7 |
| Save/load/persistence | EXISTS_BUT_NEEDS_REFACTOR | S4/S5 bounded declarative records; add family codec dispatch, no new store | FLC-2 |
| Prediction contract | PARTIAL | S2/S5 share binary semantics but different purpose-specific envelopes | FLC-1 |
| Optimizer abstraction | MISSING | No finite generic trial/selection envelope | FLC-3 |
| Logistic hyperparameter search | MISSING | S3/T1 deliberately prohibit tuning; separate new synthetic recipe only | FLC-3 |
| Temporal tuning rules | PARTIAL | S4 train/fold cutoffs exist; search/selection chronology not implemented | FLC-3 |
| Calibrator abstraction | PARTIAL | FF §8 design and state/pins, no reusable executable interface | FLC-5 contracts only |
| Logistic calibration compatibility | PARTIAL | Raw numeric reconstruction exists; wrapper dependency checks absent | FLC-5 |
| Logistic diagnostics | PARTIAL | S3 coefficients/scaler/convergence captured, no common report | FLC-4 |
| Logistic statistical studies | MISSING | No bounded study manifests; independent loss CIs are not coefficient studies | FLC-4 scaffolding |
| Common framework metrics | EXISTS_BUT_NEEDS_REFACTOR | S7 losses exist; extract/adapt new neutral view without changing frozen formulas | FLC-6 |
| Calibration metrics | PARTIAL | S7 reliability bins exist; reusable ECE/qualification/support contract missing | FLC-6; empirical FF-2 |
| Benchmark comparison | EXISTS | S6/S7 matched BaseRate arm; retained first-class comparator | FLC-6 compatibility |
| Paired statistical comparison | EXISTS | S7/S8 development and final paired masks/protocols | FLC-6 compatibility |
| Uncertainty/confidence intervals | EXISTS | Fixed dependent-block methods in S7/S8, not universal IID CI service | Preserve; FLC-6 |
| Ground Truth compatibility | EXISTS | S6 shared strict endpoint direction, missing is not negative | Preserve; FLC-7 |
| PIT safety | EXISTS | S2/S4/S5/S6 cutoff, purge/embargo, explicit retrospective mode | New seams must retain; FLC-7 |
| Replay compatibility | PARTIAL | S5/S9 versioned replay works; new neutral artifact closure unproved | FLC-7 |
| Provenance | EXISTS | S3–S9 data/code/dependency/clock/report chains | Preserve; FLC-7 |
| Fingerprints | EXISTS | S3/S9 separate scientific/capture seals | Preserve; FLC-7 |
| Immutable experiment identity | PARTIAL | S3/S8 fixed grants/protocol/custody; reusable identity/trial lineage missing | FLC-2/3 |
| Lifecycle events versus roles / approval | PARTIAL | Fixed roles plus architecture mapping, no general lossless event implementation | FLC-2/7; actual use FF-2+ |
| Tests | PARTIAL | T1–T3 strong fixed-path corpus; family-neutral seam tests missing | Every package |
| Documentation | PARTIAL | Accepted FF/A7 ownership; FLC gap/target added here, implementation evidence pending | FLC-0/8 |
| Rich empirical ablation/sensitivity/odds-ratio inference studies | NOT_NEEDED_NOW | New data/grants/identities needed; not required to prove interfaces | Later separate study |
| Additional families, routing engine, online learning | NOT_NEEDED_NOW | Existing FF-3…7 gates, no present Logistic-driven need | Deferred |
| MLflow/service, universal serialization, distributed tuning | NOT_NEEDED_NOW | Local native artifacts and bounded jobs suffice | Deferred |

## Bounded implementation packages

Order: **FLC-0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8**. No work below has been
implemented by this pass. FLC uses newly identified synthetic fixtures by default;
any later empirical fit/study requires separate data, protocol and job approval.
No new performance target or Logistic superiority is an exit criterion.

Existing modules below identify integration seams, not permission to rewrite
pinned code. Prefer additive sibling modules (suggested names only) and exact
version adapters. Do not modify FF-0 defaults, FF-1 literal configs/grants,
scientific protocol, captures or historical interpretation. If preserving the
old pinned verifier requires retaining its source implementation, retain it.

| Package / purpose | Concrete deliverables and likely files | Tests and acceptance | Non-goals | Recommended model |
| --- | --- | --- | --- | --- |
| FLC-0 — architecture/gap baseline (this pass) | FF §22, this evidence matrix and synchronized roadmaps | Source-linked gaps, explicit ownership and FF-1 preservation; docs links/diff | No runtime implementation | GPT-6 Astra Extra High |
| FLC-1 — neutral inference seam | Add internal descriptor/input/predictor/absence contracts adjacent to `forecasters.py` / `contracts.py`; BaseRate and Logistic reference adapters, not legacy registry replacement | Same target/output semantics, explicit required inputs, tuple/JSON/time tests, unknown version/target rejection, predictor cannot fit/fetch; unchanged old registry/imports | No training API on predictor; no arbitrary loaders/new family | GPT-6 Astra High |
| FLC-2 — training, identity and artifact lifecycle | Add Learning lifecycle/experiment manifests and bounded trainer/codec adapters around S3/S4/S5; immutable new candidate refs and append-only event view in the existing storage ownership | Synthetic train→freeze→restore→predict, new content gives new identity, role not approval, denied/suspended history preserved; native restore without sklearn; old FF-1 blobs untouched | No legacy refit, pickle, separate registry or actual activation | GPT-5.6 Sol Extra High |
| FLC-3 — bounded Logistic optimization lifecycle | Add Learning trial/selection manifest plus Logistic-only config validator/tuner; common objective/report reference, finite development-only synthetic recipe | Maximum 3 declared configs × 2 temporal inner folds = 6 attempts, no automatic retry; predeclared order/seed/tie rule; TRAIN-only scaler, no holdout access; all failures/time/cost captured; no supported candidate yields absence | No empirical search, FF-1 retuning, Bayesian/distributed search or generic Logistic knobs | GPT-6 Astra High |
| FLC-4 — model diagnostics and studies | Add model-neutral diagnostic report envelope and Logistic diagnostics adapter referencing frozen scaler/model and declared synthetic cohort; descriptive coefficients, scale-aware odds ratios, probability distribution and fold stability; optional-study manifest | Units/feature order, constant/correlated columns, exponent overflow as unavailable not infinity, absent support, deterministic report fingerprint; never returns superiority/approval | No FF-1 new analysis, causal/p-value claims or mandatory empirical ablation/bootstrap fits | GPT-5.6 Sol High |
| FLC-5 — calibration composition readiness | Add internal calibrator descriptor/artifact-reference/compatibility seam next to FF contracts; raw-versus-transformed trace and qualification-required absence; test doubles only | Wrong model/scaler/target, logit-vs-probability mismatch, stale calibration refs, no grant/no apply; missing calibration never silently becomes identity; raw record preserved | No Platt/isotonic/temperature implementation, calibration fit or FF-2 experiment | GPT-6 Astra High |
| FLC-6 — reusable common Evaluation | Add neutral adapters around S6/S7, common metric/report protocol and benchmark-role checks; bounded synthetic ECE/support summary with pinned bin/undefined conventions | Hand-computed Brier/log-loss/ECE, endpoints/empty bins, missingness/paired denominators, dependent-CI references; frozen FF-1 policies unchanged; same rows for both arms, forecaster cannot set verdict | No re-score of FF-1, new CI/tuning thresholds, promotion or profitability claims | GPT-5.6 Sol Extra High |
| FLC-7 — integration, capture and adversarial replay | Add focused `tests/unit/forecasting` / `tests/unit/evaluation` lifecycle corpus; new capture/version dispatch only where required | Full synthetic pipeline, recorded replay with ML/trainer/network blocked, exact pinned verification distinct, unknown pins fail closed, no leakage, no activation, all failed attempts retained; FF-0/FF-1 preservation | No live acquisition, consumed-holdout replay/recompute, real grant or public Shell operation | GPT-6 Astra High |
| FLC-8 — reference closure and gate review | Update this matrix with actual evidence, FF/A7 status and explicit carry-forwards; independent acceptance checklist | All completion criteria below evidenced, actual test counts, no unresolved mandatory seam blocker; decide readiness for FF-2 proposal, not fit authorization | No implicit tag, new learned family or empirical model approval | GPT-6 Astra Extra High |

The FLC-3 count is a bounded **engineering fixture ceiling**, not FF-1 or future
empirical tuning policy. The implementation request must pin its exact synthetic
config list, objective, tie rule and worker timeout/memory/trial-byte caps before
running it; absence blocks execution, not contract work. A separately allowed
selection refit must have its own budget/identity; the six-attempt fixture has no
hidden seventh fit. Every learned transform and selection dependency participates
in cutoff checks. Optional studies cannot turn this into an unbounded tournament.

Model assignments are engineering judgment: Astra for cross-owner governance and
independent closure; Sol for bounded artifact/report implementation. The
[official Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol) references were
checked on 2026-09-22; Extra High denotes `xhigh`. These are planning recommendations,
not account availability, cost estimates or a claim that a model was switched.

## Completion criteria and risks

FLC is complete only when all nine checks have evidence:

1. BaseRate and the Logistic reference satisfy the same narrow inference seam
   without pretending they have the same preprocessing or training requirements.
2. New candidate, experiment, feature, implementation and artifact identities are
   separate; old FF-0/FF-1 deserialization, role and fingerprints are preserved.
3. A finite new synthetic training/tuning path demonstrates immutable freeze and
   native restore, complete attempt accounting and strict development-only access.
4. Diagnostics are attributable, scale-aware and descriptive; independent
   Evaluation alone performs common comparisons and reports insufficient evidence.
5. Reusable calibration composition validates transitive identity and absence
   without implementing/fitting a calibrator or asserting calibrated qualification.
6. Shared truth, paired denominators, metric conventions and uncertainty references
   are reused; no duplicated benchmark/evaluator or second registry.
7. Recorded replay requires no fit/inference/live call; exact pinned verification
   is separately invoked and refuses missing versions. Fit reproduction is not replay.
8. Synthetic role/lifecycle denial tests prove no approval by model name, report,
   grant or COLD selection alone; nine public operations and lower layers unchanged.
9. Reviewed tests/docs and explicit scope closure permit only the next FF-2 proposal.
   FF-1 stays inconclusive/consumed/no-refit; FLC is not a calibrated-model milestone.

Risks: a universal estimator API would force benchmark training and collapse
authority; generalizing fixed literal contracts would invalidate old semantics;
a second registry or evaluator would split custody; trial proliferation would
consume evidence as a tuning target; replay that re-fits or loads latest would
erase reproducibility; calibration scaffolding could be misread as qualified
probabilities. Mitigations are the narrow split interfaces, additive versioning,
single owners, finite grants, explicit replay modes and negative fixtures above.

Do not implement additional families, ensembles, regime/sector production models,
autonomous retraining, online learning, remote services, HOT binding, A8 or forecast
publication. Future model-specific studies must not revisit FF-1's consumed holdout
to rescue the result. Any Logistic revision needs a new model/candidate, experiment
and validation strategy; no exception follows from a new name or calibration layer.

## Validation and next request

This pass is documentation-only. Validate links/heading references, scope and
`git diff --check`; historical empirical commands and full training suites are
not needed to establish documentation changes. Later implementation packages run
their focused tests plus compileall, pytest, Ruff, mypy and diff checks as required
by the existing A7 quality gates; report actual rather than inherited counts.

Executed validation for this documentation pass:

- **206 passed in 27.69s**: `test_contracts.py`, `test_identity_isolation.py`,
  `test_population_contract.py` under `tests/unit/forecasting`, and
  `test_final_holdout.py`, `test_final_protocol.py` under `tests/unit/evaluation`.
  These use synthetic fixtures, not an empirical FF-1 rerun.
- **695 local links and 28 heading/anchor references** across the 11 changed
  Markdown files passed; incoming references from README and top-level docs to
  changed documents have no broken anchors.
- Canonical-byte/hash-only checks matched all four recorded FF-1 identities,
  all 72 protocol source pins and 6 execution pins; ledger remains COMPLETE/MATCH.
  No empirical inference, loss recomputation, bootstrap or numerical replay was performed.
- Changed-lines whitespace and new-plan whitespace checks passed; scope is
  Markdown only. Existing Markdown hard-break spaces outside changed lines are
  preserved. Full pytest, compileall, Ruff and mypy were not rerun: no source,
  tests, dependencies or runtime configuration changed.
- No private data or .env is tracked/staged; no empirical corpus or dated FF-1
  report was edited. No commit, tag or push was performed.

**GO — sufficiently defined to begin FLC-1 under a separate implementation
request. NO-GO for FF-2 execution or any empirical fit in this pass.** No missing
scientific dataset blocks the first contract-only package. Exact internal names
can be finalized in FLC-1 without changing the ownership/admission obligations.

Exact next task: **TIAF A7 / FLC-1 — FORECASTER CONTRACT AND LIFECYCLE SEAM NORMALIZATION**.
