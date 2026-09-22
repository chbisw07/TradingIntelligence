# FF-1 — Independent final scientific closure and baseline decision

## Decision and scope

**FF1_FINAL_CLOSURE_ACCEPTED**

Reviewed 2026-09-22, Asia/Kolkata, against clean entry HEAD
`12d62e0ea0214fe2131525431860911b951cba7b`. This is a scientific/governance
closure of the completed experiment, not another empirical evaluation. The
[accepted one-shot execution](TIAF_A7_FF1_ONE_SHOT_PROTECTED_2025_FINAL_HOLDOUT_EVALUATION.md)
and all earlier experiment records remain unchanged.

```text
FF1_SCIENTIFIC_OUTCOME = INSUFFICIENT_EVIDENCE
SCIENTIFIC_REASON = CONFIDENCE_NONDECISIVE
SCIENTIFIC_CLOSURE_STATE = FF1_SCIENTIFICALLY_CLOSED_INCONCLUSIVE
FF1_INFRASTRUCTURE_ACCEPTED = YES
BASERATE_ROLE = BENCHMARK
LOGISTIC_ROLE = CHALLENGER / EXPERIMENTAL
LOGISTIC_PROMOTION_ELIGIBLE = NO
FF2_CALIBRATION_RESEARCH_ELIGIBLE = YES
POST_HOLDOUT_REFIT_ALLOWED = NO
PROTECTED_HOLDOUT_STATUS = CONSUMED
FINAL_HOLDOUT_EVIDENCE = COMPLETE
FINAL_HOLDOUT_EXECUTIONS_USED = 1
AUTOMATIC_PROMOTION = NO
READY_TO_TAG_FF1 = YES
```

These are closure decisions, not new runtime enums, registry transitions, grants
or published capabilities. FF-2 eligibility means eligibility for a **new governed
research proposal**; its data, protocol, fit and prospective-use entry gates have
not been satisfied by this review. Tag readiness is for a research baseline,
subject to the separate final repository/freeze check, not a promotion baseline.
No integrity or scientific-protocol defect was found. Inconclusive evidence is
a legitimate final result, not an engineering blocker to closing this experiment.

## Review method and evidence boundary

The review independently inspected the recorded sequence, frozen source,
architecture, canonical captures and tests; it did not merely adopt the previous
acceptance label. Evidence sources are linked below. No new provider access,
empirical fit, forecast, Ground Truth calculation, loss computation, bootstrap,
alternative confidence level, subgroup or diagnostic was run.

In particular, this pass did **not** run the empirical `--execute`, `--preflight`
or `--verify-ledger` commands. The last command is read-only but numerically
reconstructs the experiment, including bootstrap; that exceeds this review's
explicit no-recomputation boundary. Recorded replay MATCH is checked as accepted
evidence, separately from the new integrity-only checks. Synthetic unit tests
exercise toy fits, forecasts and metrics in temporary stores; they do not touch
the empirical holdout or refit its artifacts.

The read-only integrity check used the existing `strict_json`, `canonical_json`
and `semantic_fingerprint` primitives, with ordinary dictionaries rather than
typed paired-record validators that would recalculate losses. It checked file
names, canonical bytes, declared seals, exact references and custody state.
Original qualification/OHLCV files were **byte-hashed only**, not numerically
decoded or requalified. No new scientific report was generated in the corpus.

## Complete sequence and ownership review

| Stage | Evidence and accepted boundary |
| --- | --- |
| [FF-1 plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md) | Fixed RELIANCE next-session binary target, five A2 features, one Logistic configuration, chronological development/final partitions, benchmark and independent Evaluation ownership. |
| [FF-1.1 qualification foundation](TIAF_A7_FF1_1_DATA_QUALIFICATION_FEATURE_SCHEMA_IMPLEMENTATION.md) | Qualification acceptance did not itself authorize empirical fitting. Frozen additive research envelopes preserve the older synthetic FF-0 contracts. |
| [FF-1.1A adjusted qualification](TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md) | Explicit adjusted retrospective profile resolved prior HOLDs without erasing them. Rights remain UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING; scientific qualification is not legal or operational approval. |
| [FF-1.2 training](TIAF_A7_FF1_2_LOGISTIC_CANDIDATE_TRAINING_ARTIFACT_IMPLEMENTATION.md) | Separately approved pinned dependency stack; four bounded, serial, converged development fits. Learning owns train-only scaler/model artifacts, not their scientific approval. |
| [FF-1.3 generation](TIAF_A7_FF1_3_LOGISTIC_WALK_FORWARD_FORECAST_GENERATION.md) | Fixed fold artifacts, outcome-blind projection, actual computation versus simulated historical clocks, 991 origins accounted for and 969 forecasts. Protected fields excluded before decoding. |
| [FF-1.4 development evaluation](TIAF_A7_FF1_4_DEVELOPMENT_ONLY_PAIRED_BASERATE_VS_LOGISTIC_EVALUATION.md) | Evaluation owns common truth, exact paired population, exclusions, proper losses and uncertainty. Development support/stability passed; final support remained forbidden before final evidence. |
| [Independent pre-final review](TIAF_A7_FF1_INDEPENDENT_SCIENTIFIC_ACCEPTANCE_AND_FINAL_HOLDOUT_DECISION_DESIGN.md) | Correctly HOLDed opening for the missing fifth-fold handoff. No placeholder artifact or retrospective permission was substituted. |
| [Fifth-fold preparation](TIAF_A7_FF1_PRE_HOLDOUT_FIFTH_FOLD_ARTIFACT_PREPARATION_AND_AUTHORITY_RECONCILIATION.md) | Separate narrow pre-open authority supplied the originally planned fifth fit and BaseRate freeze. One fit before opening is not permission for post-open refitting. |
| [Protocol freeze](TIAF_A7_FF1_FINAL_HOLDOUT_PROTOCOL_FREEZE_REVIEW_WITH_FIFTH_FOLD_HANDOFF.md) | Exact artifacts, population, source/code/dependency pins, support gates, bootstrap and support/rejection/inconclusive partition frozen before protected numeric access. |
| [One-shot final evaluation](TIAF_A7_FF1_ONE_SHOT_PROTECTED_2025_FINAL_HOLDOUT_EVALUATION.md) | Durable claim/opening before bounded source read; all forecasts captured before Evaluation-owned truth; verified COMPLETE ledger; one consumed execution, no retry. |
| This closure | Interpret the frozen evidence and retain lifecycle boundaries; no scientific rule, artifact or runtime change. |

### Target, features, training and baseline

The target remains `equity.next_session_close.return_gt_zero/1.0`: next-session
adjusted close strictly above reference adjusted close. Equal normalized closes
label zero; non-equal precision-ambiguous endpoints remain unavailable. This is
neither a return-size prediction nor a probability of profitable execution.
The ordered schema remains `ret_1`, `ret_5`, `sma20_distance`,
`realized_vol_20`, `relative_volume`, using the accepted A2 calculations.

Inspection of [training admission](../src/tiaf/learning/forecast_training.py),
[artifact contracts](../src/tiaf/learning/forecast_artifacts.py) and the
[isolated worker](../src/tiaf/learning/forecast_worker.py) confirms train-only
standardization and fitting. The worker sees admitted TRAIN rows, not later test
labels. StandardScaler uses mean/std and ddof=0; no imputation or feature selection.
Logistic remains L2, C=1, lbfgs, tol=1e-8, max_iter=1000, with intercept and no
class weights/warm start. Failed convergence does not authorize a rescue fit.

Development TRAIN sizes were 720 / 968 / 1,216 / 1,441. The fifth-fold cutoff is
`2024-12-31T09:15:00+05:30`, TRAIN 1,690 (878 positive / 812 zero), reference range
2018-01-01 through 2024-12-27. Target maturity and assumed label availability
must precede cutoff; 2024-12-30 and 2024-12-31 are boundary-purged, with the latter
also protected/embargoed and counted only once. The fifth fit completed before
opening; its stored model reports convergence in 11 iterations.

The [research BaseRate](../src/tiaf/forecasting/research_baserate.py) retains the
unsmoothed last-20-scheduled-transition rule, with no invalid-transition backfill.
Its final frozen support is 8/20, probability 0.4, not a benchmark recalibrated
to 2025 prevalence. The empirical research binding is version 2.0; FF-0's
synthetic version 1.0 remains unchanged. **0.4 is this fold's frozen artifact,
not a new global default or a replacement for FF-0 runtime computation.**

Optional training dependencies remain outside base installation/runtime imports:
CPython 3.12.3, scikit-learn 1.7.2, NumPy 2.3.3, SciPy 1.16.2, joblib 1.5.2,
threadpoolctl 3.6.0. The platform-specific wheel lock is pinned, not a claim of
cross-platform bitwise fitting equivalence. Package version is 0.1.0, existing
contract schema 1.0, additive research schema 2.0, and candidate version 1.0;
these are distinct concepts.

## Final evidence: interpretation without recomputation

The following values are copied from the sealed final evaluation, not recalculated.
Differences are Logistic minus BaseRate; negative point differences favor Logistic.

| Primary metric | BaseRate | Logistic | Paired mean difference | Frozen 97.5% interval |
| --- | ---: | ---: | ---: | --- |
| Brier | 0.26281124497991964 | 0.24996333507967594 | -0.012847909900243735 | [-0.028089924933311944, 0.004386873268651029] |
| Natural log loss | 0.7192574865685811 | 0.6930742937929326 | -0.026183192775648522 | [-0.05702105803609845, 0.008685324032304249] |

The recorded population is 249 intended origins, 249 pairs, 128 positive /
121 zero, coverage 1.0, 49 complete five-session blocks and zero exclusions.
All fixed adequacy gates passed. Uncertainty is **not** a missing-data or
engineering-failure classification.

The frozen [decision implementation](../src/tiaf/evaluation/forecast_final_protocol.py)
requires, after adequacy, Brier upper <0 and log-loss upper <=0.01 for support.
The stored Brier upper is positive, so support fails. Decisive rejection requires
Brier lower >=0 or log-loss lower >0.01; neither holds. Both reported intervals
cross zero. Thus the recorded `INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE`
is the correct frozen partition, not a discretionary judgment about how close
the point estimates look. No extra final .02/.05 mean gate is introduced.

Superiority was not established; decisive rejection was not established.
This experiment is inconclusive. It is not proof Logistic is bad or better,
not “almost supported,” not “practically supported,” and not a failed experiment.

### Development versus final

The stored development report has 969 pairs across 2021–2024, 22 explicit
unpaired slots and no support/stability failures. Pooled recorded differences
were -0.020716138102064203 Brier and -0.04671946807533704 log loss; their recorded
97.5% intervals were [-0.03172577151413767, -0.010356651512753121] and
[-0.07029345626881534, -0.024448987068300437]. Three development folds had negative
mean Brier differences; 2022's worsening stayed within the fixed .02/.05 margins.

That development evidence justified proceeding to the protected test, **not**
declaring support. Final point differences have the same favorable direction
but wider uncertainty relative to their magnitude and no decisive final bounds.
There is no contradiction: development and final are different predeclared
populations with different decision roles. Their observations/intervals are not
pooled here, development significance cannot substitute for final confirmation,
and the historical development `NOT_RUN / SEALED` fields remain correct as-of
that report rather than current authority to reopen the holdout.

### Fixed-0.5 and other descriptive diagnostics

The already-recorded fixed-.5 diagnostic has Brier 0.25 and log loss
0.6931471805599453; Logistic has 0.24996333507967594 and 0.6930742937929326.
These are close descriptively. This does **not** establish equivalence, make
fixed-.5 a new primary comparator or prove incremental skill. No new difference,
interval, hypothesis test or diagnostic gate was calculated.

Recorded accuracy is 48.5944% BaseRate, 51.8072% Logistic, and 51.4056% fixed-.5.
Mean Logistic probability is 0.519259753 versus prevalence 0.514056225;
248 observations lie in [0.5,0.6), one lower-bin observation is LOW_SUPPORT.
The arms classify on opposite sides of .5 for 248/249 observations, with mean
absolute probability difference 0.119259753. A threshold-sensitive classification
contrast is not a large or qualified probabilistic advantage. Reliability bins
remain descriptive; none establishes calibration. These facts neither override
the primary rule nor motivate a new calibration fit in the same experiment.

## Custody, fingerprints and preservation

| Identity | Exact fingerprint |
| --- | --- |
| Frozen protocol | `2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814` |
| Execution | `2948bc46874f8196c535720bd4f7882f6293fc96077acb563e2e11409c3e4840` |
| Final evaluation | `8c0556e7b88284c170db57d745de7ece707d365ab52a585db5ebb0d3e81a7d0e` |
| COMPLETE ledger | `630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583` |
| Fifth-fold handoff | `c40148f60e985c83fe8bca027a3722583ed8c1999ecfc86e4959c4fe6166ce54` |
| Frozen model | `c287d9333fbf6067dd16fe5ab51bb1e6a7c6168df6289b9e73669aa2a15f6381` |
| Frozen scaler | `00e0ceaa160a7df2e518aafb4a8b1c2f86c55837eeeda94f131b002fae20afe8` |
| Frozen BaseRate | `6a89a25e67d1a2e6d538b3754e61f7da932f4c8b5b6b72fbb2346a7040bf7e8e` |

Recorded consumption is **2026-09-22T10:49:22.158293+05:30**. Protocol custody
contains exactly one protocol and one attempt, identical to their final-corpus
copies. The final corpus has one opening, one execution, one COMPLETE ledger
and no failure records. `executions_consumed=1`, no retry and no post-holdout
refit are sealed. Inspection of
[custody](../src/tiaf/evaluation/forecast_final_custody.py) and
[execution/publication ordering](../src/tiaf/evaluation/forecast_final_store.py)
confirms exclusive fsynced consumption before source decoding, and captured
numerical verification before COMPLETE ledger publication.

The new integrity-only audit completed at
**2026-09-22T11:22:42.520481+05:30**:

- All **5,282** canonical blobs matched their names, seals and canonical bytes:
  final corpus 1,261; canonical protocol custody 2; fifth-fold corpus 8;
  development evaluation corpus 4,011.
- **72** protocol source pins and **6** additive execution implementation/test
  pins matched current files. Model/scaler/BaseRate/handoff final copies matched
  the pre-open fifth-fold bytes. Development ledger/report identities matched.
- All **249** ordered row groups link their common input, two frozen-arm
  forecasts, pair and revision-0 truth. Ground Truth and forecast-population
  reference hashes match the final report; pair blobs match the captured table.
- The ledger still records `replay=MATCH`. This is the previously completed
  numerical reconstruction, corroborated by the accepted execution record, not
  a fresh numerical replay claimed by this review.
- All **4,026** prior fifth-fold/development/provisioning/qualification files
  match the previously recorded aggregate path-to-byte-hash identity
  `d1f77860abd2d2ed332224246338d99125367e6390b81d2138462793f3bfd6ac`.

Two precision limits matter. First, `completed_at` is ledger **assembly** time;
durable publication follows verification. It is not a separately measured
publication timestamp. Second, these are trusted local custody guarantees, not
OS-level WORM or evidence that an administrator could never have deleted or
copied a corpus. No such bypass is indicated by the reviewed record, and deleting
history to regain execution authority is forbidden. A consumed failure would
also remain consumed. Historical nested SEALED/NOT_RUN states are preserved
freeze/preparation metadata; the completed outer ledger/report owns current state.

## Findings and policy classifications

Each Action names either NO_CHANGE or a classified clarification below.
No HOLD findings, runtime fixes, new scientific gates or retroactive policy edits
are required. Severity describes the boundary if misused, not a defect found.

| ID | Area | Evidence | Finding | Decision | Severity | Action |
| --- | --- | --- | --- | --- | --- | --- |
| F01 | Qualification | FF-1.1A seal and reviewed profile | Research admission complete; rights warning is not a license grant. | ACCEPT_WITH_CLARIFICATION | Medium | C01 |
| F02 | Research vintage | Adjusted profile; actual acquisition clock | Later adjusted research is not historical PIT/ACTUAL evidence. | ACCEPT_WITH_CLARIFICATION | Medium | C02 |
| F03 | Target/features | Fixed schema, A2 projector, artifact manifest | Same binary target and five ordered features; no retuning. | ACCEPT | Informational | NO_CHANGE |
| F04 | Training clocks | Admission source; fifth cutoff | Label maturity, purge/embargo and aware Asia/Kolkata clocks retained. | ACCEPT | Informational | NO_CHANGE |
| F05 | Dependency isolation | Optional extra, wheel lock, worker/tests | Pinned learned stack is optional; lean inference/replay do not fit. | ACCEPT | Informational | NO_CHANGE |
| F06 | Train-only scaling | Worker and manifest audit | Scaler and model see admitted TRAIN only; fixed config, no rescue. | ACCEPT | Informational | NO_CHANGE |
| F07 | Fold boundaries | Four training manifests; fifth handoff | Annual walk-forward and fifth cutoff remain frozen. | ACCEPT | Informational | NO_CHANGE |
| F08 | Pre-open protection | Redacting readers; synthetic sentinels | Protected origin/target guard precedes numerical decoding. | ACCEPT | Informational | NO_CHANGE |
| F09 | BaseRate | Research policy; frozen fifth artifact | Last 20 scheduled, unsmoothed 8/20, no backfill or protected updates. | ACCEPT | Informational | NO_CHANGE |
| F10 | Logistic artifacts | Canonical model/scaler and grants | Transparent coefficients/scales, exact lineage, RAW_UNCALIBRATED. | ACCEPT | Informational | NO_CHANGE |
| F11 | Walk-forward | FF-1.3 run and development captures | Fixed fold, common semantics, explicit absence; outcome-blind inference. | ACCEPT | Informational | NO_CHANGE |
| F12 | Development comparison | Sealed 969-pair report | Development gates passed; not a substitute for final confirmation. | ACCEPT_WITH_CLARIFICATION | Medium | C03 |
| F13 | Fifth-fold preparation | Separate grant/handoff; pre-open clock | Original fifth fit completed before opening; old four-fold grant not widened. | ACCEPT | Informational | NO_CHANGE |
| F14 | Frozen final protocol | Protocol, policy and 72 source pins | Exact method and exhaustive decision partition predate opening. | ACCEPT | Informational | NO_CHANGE |
| F15 | One-shot execution | Canonical attempt/opening/ledger; source order | One consumed execution, terminal on success/failure, no retry. | ACCEPT | Informational | NO_CHANGE |
| F16 | Pairing / truth | 249 reference groups, table and journal identities | Same input and revision-0 truth per pair; zero new exclusions. | ACCEPT | Informational | NO_CHANGE |
| F17 | Uncertainty method | Frozen paired five-session/5000/1729 policy | Exact accepted bootstrap preserved; approximate coverage is not guaranteed power. | ACCEPT_WITH_CLARIFICATION | Medium | C04 |
| F18 | Final decision | Stored bounds and decision source | Neither support nor rejection condition holds; nondecisive result correct. | ACCEPT | Informational | NO_CHANGE |
| F19 | Replay / immutability | COMPLETE/MATCH ledger and canonical checks | Prior numerical MATCH retained; current check is integrity-only. | ACCEPT_WITH_CLARIFICATION | Low | C05 |
| F20 | No post-hoc rescue | Immutable policy/grants; no-refit tests | No reopening, refit, alternate seed, exclusion or same-experiment calibration. | ACCEPT | Informational | NO_CHANGE |
| F21 | Lifecycle / promotion | FF plan §8; FF architecture §9; artifact literals | Research closure does not validate/promote Logistic or retire it automatically. | ACCEPT_WITH_CLARIFICATION | Medium | C06 |
| F22 | FF-0 interaction | Preserved FF-0 tag, BaseRate tests, no runtime diff | No synthetic baseline replacement or new public/production authority. | ACCEPT | Informational | NO_CHANGE |
| F23 | Infrastructure | Admission/artifacts/generation/evaluation/custody tests | Complete research chain works with an inconclusive outcome. | ACCEPT | Informational | NO_CHANGE |
| F24 | FF-2 eligibility | FF roadmap §5 and FF-1 seam | New research proposal eligible; actual entry/fit/prospective gates remain open. | ACCEPT_WITH_CLARIFICATION | Medium | C07 |
| F25 | Future validation | Consumed state and architecture separation | 2025 is development-known; new independent evidence is required. | ACCEPT_WITH_CLARIFICATION | Medium | C08 |
| F26 | Baseline tag | Existing tag convention; ignored private corpus | Freeze machinery/result/pins, not superiority; retain private evidence separately. | ACCEPT_WITH_CLARIFICATION | Medium | C09 |
| F27 | Custody limit | Exclusive writes and canonical store contract | Trusted local operator boundary, not adversarial tamper-proof storage. | ACCEPT_WITH_CLARIFICATION | Low | C10 |
| F28 | Ledger clock | Assembly then verify/publish source order | `completed_at` is assembly time, not measured durable publication. | ACCEPT_WITH_CLARIFICATION | Low | C11 |

| Clarification | Classification | Required interpretation / disposition |
| --- | --- | --- |
| C01 | RESEARCH_POLICY_CLARIFICATION | Retain UNVERIFIED/WARN_ONLY warning. No legal rights certification or new entitlement. |
| C02 | RESEARCH_POLICY_CLARIFICATION | Retain later-vintage, provider-defined volume, binary64, bounded calendar/action and non-PIT limitations. |
| C03 | NO_CHANGE | Existing development and final rules have different jobs. Do not pool, rescore or override them. |
| C04 | NO_CHANGE | Five-session dependence approximation and nominal multiplicity coverage remain disclosed, not post-hoc vetoes. |
| C05 | IMPLEMENTATION_DETAIL | State what was checked now versus the numerical replay already recorded; no new replay/evaluation mode. |
| C06 | ARCHITECTURE_CLARIFICATION | Role, lifecycle, scientific outcome, fit authority, approval and COLD binding remain separate. |
| C07 | RESEARCH_POLICY_CLARIFICATION | YES to considering a new governed FF-2 stage, not approval to start fits or activate calibration. |
| C08 | RESEARCH_POLICY_CLARIFICATION | New candidate/version/protocol and independent evidence; consumed 2025 cannot become unseen again. |
| C09 | ARCHITECTURE_CLARIFICATION | Tag code/docs and their evidence identities; private-corpus retention is separately necessary for replay. |
| C10 | IMPLEMENTATION_DETAIL | Preserve canonical custody; do not claim WORM, duplicate-corpus detection or administrative reset prevention. |
| C11 | IMPLEMENTATION_DETAIL | Keep the historical assembly clock unchanged and accurately named. |

Actual FF-2 fitting, calibration qualification, shadow and deployment are **DEFER**
to separately authorized work. No **BLOCKER** classification remains for this
closure; missing future data/grants block that future execution, not this review.

## Lifecycle, infrastructure and future research decision

The [FF architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#9-roles-and-lifecycle-are-independent),
[A7 ownership acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) and
[FF-1 plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md)
agree: artifact custody and evaluation results do not create a PromotionDecision.
An independently approved lifecycle transition and separately authorized COLD
binding would be needed for wider use. No such transition is made here.

HistoricalBaseRateForecaster remains BENCHMARK; LogisticRegression remains
CHALLENGER / EXPERIMENTAL, neither promoted nor automatically retired for lack
of superiority. `LOGISTIC_PROMOTION_ELIGIBLE = NO` for these artifacts/evidence.
FF-0's accepted internal synthetic BaseRate behavior, public capability inventory,
A2 deterministic scores, A4/A5/A6 decisions and all TM/broker authority are unchanged.
No research probability is promoted to a forecast-backed trade recommendation.

Infrastructure acceptance is **YES** independently of the model result: optional
dependency isolation, qualified supplied data, fixed features, train-only
preprocessing, transparent artifacts, walk-forward generation, exact paired
comparison, fixed bootstrap, protected one-shot governance, recorded reconstruction,
immutable lineage and honest inconclusive-result handling have been demonstrated.
This is a bounded single-symbol research chain, not a claim that a general
production registry, calibrator, data-rights service or operational FF is complete.

The [FF-2 roadmap](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md#5-ff-2--calibration-lifecycle-shadow-and-complete-miniature)
requires accepted comparison infrastructure **and** separately qualified
calibration/test data, frozen support/usefulness/shadow/health policies and
explicit prospective authority. The first is now available; the rest are not
granted here. Hence `FF2_CALIBRATION_RESEARCH_ELIGIBLE = YES` means a new governed
stage/version can be proposed, not that all FF-2 entry conditions have passed.
There is no promise calibration will qualify Logistic or rescue this result.

| Future direction | Required evidence/authority; no automatic activation |
| --- | --- |
| New Logistic version or other forecaster | New hypothesis, identity, fixed finite trial budget and preregistered validation; no relabeling of FF-1 v1. |
| FF-2 calibration research | Separately identified calibration-fit partition and independent test; raw and calibrated artifacts retained, no using the same inspected labels for both fit and independent test. |
| Future ACTUAL forecasts / rolling shadow | Separately qualified inputs and prospective grant; immutable forecasts captured before outcomes, no relabeling historical SIMULATED records as ACTUAL. |
| New future protected holdout | Freeze model/selection/calibration/metric/split policies before opening; consumed 2025 is ineligible as unseen final evidence. |
| Nested or rolling validation | New preregistered experiment with cutoff-safe fitting/selection/calibration, label maturity and purge/embargo; evaluated windows cannot feed their own fitted decisions. |
| FM/LFDE or later families | Separate scoped forecaster-family research within FF, appropriate baselines and independent qualification; not preauthorized by FF-1 closure. |

**2025 is now development-known evidence forever for this experiment.** A new
experiment may explicitly disclose previously inspected history as development
material, subject to rights and data/fit authority, but may not call it an unseen
holdout or quietly fold it into the original candidate. Chronological windows
already inspected are not made protected again by a renamed split or new seed.

Forbidden for FF-1: tuning Logistic against 2025; retraining Logistic v1 with
2025; changing the target/features/BaseRate, bootstrap/confidence, seed or
exclusions based on the result; selecting another 2025 slice; adding calibration
and calling it the same experiment; deleting custody to reopen; pooling final
and development evidence to rescue support. All scientific revisions require a
new candidate/version/experiment, disclosed prior access and a new validation
strategy. No production activation is preauthorized.

## Baseline meaning and next gate

**READY_TO_TAG_FF1 = YES**, for the following meaning only:

> FF-1 fixed Logistic challenger, BaseRate benchmark, adjusted retrospective
> research profile, walk-forward generation, paired evaluation, one-shot
> final-holdout protocol, consumed 2025 final evidence, and final
> INSUFFICIENT_EVIDENCE result are frozen and replayable. Logistic remains
> non-promoted; post-holdout refit is forbidden for this experiment.

Recommended name: `tiaf-a7-ff1-baseline`, consistent with the existing
`tiaf-a7-ff0-baseline` and `tiaf-a6-baseline`. Neither existing tag moved. The new
tag does not exist at review time. A Git tag freezes tracked code/documentation
and the recorded evidence pins; it does **not** package ignored private data.
Retain the private final/protocol/fifth-fold/development corpora, qualification,
authorized source artifacts and dependency lock under appropriate access/retention
controls. Do not publish market data merely to make a Git tag self-contained.

Suggested commit, not performed:
`docs(a7.ff1): close FF-1 with inconclusive final evidence`.
After the separate final freeze/readiness check and explicit Git authorization,
the recommended tag commands are:

```bash
git tag -a tiaf-a7-ff1-baseline -m "A7 FF-1 baseline: fixed Logistic challenger, one-shot final holdout consumed, final outcome INSUFFICIENT_EVIDENCE"
git push origin tiaf-a7-ff1-baseline
```

No commit, tag or push is performed in this pass. Exact next task:
**TIAF A7 / FF-1 — FINAL FREEZE / TAG READINESS CHECK**.

## Validation and changed files

No runtime/test/policy/dependency changes were necessary. Existing final tests
already cover consumed-attempt reuse denial, immutable/tampered closure,
inconclusive non-promotion and forbidden refit. No new closure tests were added.

| Check in this review | Result |
| --- | --- |
| Final-holdout/protocol synthetic tests | 94 passed in 21.70s |
| FF-1 regression slice plus FF-0 BaseRate preservation | 332 passed in 461.03s |
| Integrity-only canonical/reference/source-pin audit | PASS, counts above; no empirical recomputation |
| `python -m compileall -q src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS, 646 source files |
| Local documentation links | PASS, 298 local links across four changed documents, including three Markdown heading references |
| `git diff --check` and new-file whitespace check | PASS (new untracked closure file checked separately with `git diff --no-index --check`) |
| Full repository suite | Not rerun: documentation-only review. Prior accepted execution recorded 3,445 passed; not a new count from this pass. |

Commands use the existing `.venv/bin/` executables:

```bash
pytest -q tests/unit/evaluation/test_final_holdout.py tests/unit/evaluation/test_final_protocol.py --tb=short
pytest -q tests/unit/forecasting/test_research_qualification.py tests/unit/forecasting/test_adjusted_retrospective_research.py tests/unit/forecasting/test_logistic_training.py tests/unit/forecasting/test_logistic_training_admission.py tests/unit/forecasting/test_logistic_forecasts.py tests/unit/forecasting/test_fifth_fold_preparation.py tests/unit/forecasting/test_baserate_runtime.py tests/unit/evaluation/test_development_comparison.py --tb=short
python -m compileall -q src scripts
ruff check src tests scripts
mypy src tests
git diff --check
```

Files changed: this new closure record, `README.md`, `docs/MILESTONES.md`, and
`docs/IMPLEMENTATION_ROADMAP.md` (current status/navigation only). Previous
experiment reports, runtime, artifacts and scientific policies are unchanged.
Acceptance blockers: **none**.
