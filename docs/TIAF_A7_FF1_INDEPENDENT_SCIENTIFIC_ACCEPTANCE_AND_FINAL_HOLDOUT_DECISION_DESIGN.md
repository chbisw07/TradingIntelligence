# FF-1 — Independent scientific acceptance and final-holdout decision design

## Decision

Review began 2026-09-21 and concluded 2026-09-22, Asia/Kolkata. Entry tree clean at
`7702544827305fe0bed852be188975b9c774b3bf` (accepted FF-1.4).
This is a source/artifact-based review, not a fresh empirical experiment or an
independent human/statistical peer review. The development findings below were
checked against code and sealed records, not accepted solely from the prior report.

```text
HOLD_FF1_BEFORE_FINAL_HOLDOUT
FINAL_HOLDOUT_EVALUATION_AUTHORIZED = NO
PROTECTED_HOLDOUT_STATUS = SEALED
FINAL_HOLDOUT_EVIDENCE = NOT_RUN
FINAL_DECISION_PROTOCOL_FROZEN = NO
```

**Blocker B1: the plan's fifth-fold pre-holdout model/artifact handoff is missing.**
Development evidence passes its registered gates, but that does not create an
exact, admitted final model identity. No protected outcome violation was found
in the reviewed path. This readiness HOLD does **not** overturn FF1_4_ACCEPTED,
constitute a failed development scientific gate, or change its
INSUFFICIENT_EVIDENCE classification.

The request explicitly says to stop if authorization is NO. Consequently this
pass does not create a purported frozen final protocol with placeholder model
hashes, implement a final scorer, open labels, train a model, or add a holdout
execution mechanism. Final-protocol tests are not claimed as implemented.

## Exact blocking evidence

The [accepted plan, §9](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md#9-chronological-protocol-and-protected-holdout)
specifies **five annual expanding-training folds**, one model frozen for each
test year. Both arms use `F_j = preceding embargo session's open`. The final
2025 fold therefore needs the accepted **2024-12-31T09:15:00+05:30** cutoff,
not the development 2024 model's 2023 cutoff. The
[qualification, §8](TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md#8-fold-feasibility--no-fitting)
qualified training-only feasibility for this fifth fold without opening 2025;
that is not a completed fit or a captured model.

Directly validated accepted training run
`f26605528584a68449396da9dea1a3e28d6e2295f355a7085887e5adedc94406`:

| Test year | Captured model fingerprint | Fit cutoff (+05:30) | Last training reference |
|---|---|---|---|
| 2021 | `2f33466e4790693475c2f51c58e14c056a0ba5a67fae2f9c6d9b6ff15bc405d7` | 2020-12-31 09:15 | 2020-12-29 |
| 2022 | `7cbe4f2b14a72ae5e2af40c535710f1695687b81786f0c69efd271b50442a5d2` | 2021-12-31 09:15 | 2021-12-29 |
| 2023 | `d5059d0474b438e5df4baf6d30030ceb10ad65ffe1fc078b055829407718a258` | 2022-12-30 09:15 | 2022-12-28 |
| 2024 | `2df0651702e6eaa9c9509e1e010efdc40e889fbdc8eb265bbfff7e256f78d153` | 2023-12-29 09:15 | 2023-12-27 |
| 2025 | **No model in the accepted handoff** | Required: 2024-12-31 09:15 | Must be pinned in separate pre-open preparation |

Additional checks:

- [TrainingGrant](../src/tiaf/learning/forecast_artifacts.py) explicitly admits
  only `(2021, 2022, 2023, 2024)` and `max_fits = 4`.
- [TrainingJob/TrainingRun](../src/tiaf/learning/forecast_jobs.py) enforce those
  four fold identities; the persisted run contains exactly those four models.
- [Research forecast Fold](../src/tiaf/forecasting/logistic_forecasts.py) is
  `Literal[2021, 2022, 2023, 2024]`. Read-only validation probes reject 2025 and
  a five-fold extension of the existing grant.
- The accepted evaluation manifest references four BaseRate artifacts, also
  2021–2024 only. The last uses 2023-12-29, not the final fold's cutoff.
- [FF-1.2's handoff](TIAF_A7_FF1_2_LOGISTIC_CANDIDATE_TRAINING_ARTIFACT_IMPLEMENTATION.md)
  explicitly says four fits and no holdout fit. FF-1.3 is a development forecast
  run, not a final-model grant or an inventory of final forecasts.

Reusing the 2024 model/scaler or BaseRate for 2025 would silently change the
annual expanding-training/fold-cutoff semantics. Fitting the missing model in
this **design-only** pass would exceed its authority. Opening first and fitting
later would violate the requested no-refit/one-shot boundary. A rule saying
“insert a model hash later” is not the requested exact frozen artifact identity.

The missing step is **pre-open preparation of the already specified fifth fit**,
not hyperparameter selection or a new candidate design. A separate explicit
grant must reconcile this with the no-refit instruction: at most the originally
planned fifth fit, using only pre-cutoff unprotected training data; no training
after opening. The current four-fold grant must not be silently broadened.

## Independent findings

Evidence references below concern development-only artifacts or reviewed code.
No raw empirical CSV or original qualification file was opened in this pass.

| ID | Area | Finding | Evidence | Severity | Decision | Action |
|---|---|---|---|---|---|---|
| F01 | Target / basis | Both arms retain next-session positive close return on the same adjusted cash-equity basis | `pair_observation` compares target, subject, basis, dates and input identity | Informational | ACCEPT | Preserve target and basis |
| F02 | Qualification | Accepted adjusted research qualification remains the shared pinned authority | Manifest/run/journal qualification and dataset seals checked on reconstruction | Informational | ACCEPT | No requalification or new source substitution |
| F03 | Research profile | Actual 2026 fresh-download vintage and assumed historical clocks are explicit; no PIT/captured-as-known claim | Research profile and qualification §5; mode fields in both arms | Limitation | ACCEPT_WITH_CLARIFICATION | Interpret only as retrospective adjusted-series research |
| F04 | Training | Four development fits use frozen train-only scalers and annual purged/embargoed memberships; fifth artifact missing | Validated training run, grant limits and exact cutoffs above | Blocking for opening | HOLD | B1: separately prepare/pin final-fold artifacts before freeze |
| F05 | Forecast generation | 969 generated probabilities across 991 accounted development slots; immutable lineage | FF-1.3 run and pinned reconstruction through FF-1.4 | Informational | ACCEPT | Do not reinterpret this run as a 2025 model/forecast grant |
| F06 | BaseRate | Last 20 scheduled transitions, unsmoothed k/n, no backfill, same fold cutoff; not full-window or rolling | `freeze_baseline`, independent reconstruction, four artifact identities | Informational | ACCEPT | Preserve arithmetic; separately capture final-fold support/artifact |
| F07 | Paired population | One common truth and exact origin/request identity; no differing-population comparison | `pair_observation`, truth seals, 969 paired records and disposition shards | Informational | ACCEPT | Preserve row-level exclusions and masks |
| F08 | Development metrics | Correct loss signs, metric-only clipping, raw probabilities retained | `losses`, per-pair loss revalidation and full report reconstruction | Informational | ACCEPT | No new metric or threshold |
| F09 | Bootstrap | Full scheduled grids with missing masks; fixed non-circular five-session blocks; fold-separated pooling; shared indices for losses | `bootstrap`, preregistered policy and existing independent-reference test | Limitation | ACCEPT_WITH_CLARIFICATION | Conditional dependence approximation, not guaranteed finite-sample coverage |
| F10 | Fold stability | Three negative Brier folds; 2022 worsening below both fixed margins; all support gates pass | Recomputed `decide` through recorded evaluation | Informational | ACCEPT | Do not change rules after seeing results |
| F11 | Diagnostics | Pooled advantage over short frozen BaseRate does not establish improvement over fixed .5 | Pooled frozen losses and fixed-.5 same-population diagnostic | Material interpretive limitation | ACCEPT_WITH_CLARIFICATION | Retain the negative diagnostic; not a new rejection rule |
| F12 | Leakage | Explicit time/fold guards, no target features or full-dataset scaler in reviewed generation; later-vintage revisions remain a limitation | Projection/training/pairing code and accepted research basis | Limitation | ACCEPT_WITH_CLARIFICATION | No operational/PIT validity claim |
| F13 | Replay / integrity | Development closure reconstructs MATCH under blocked network, fitting imports and non-development-source reads | Fresh guarded replay; all 4,011 byte hashes unchanged | Informational | ACCEPT | Preserve exact source corpus and pins |
| F14 | Holdout protection | No protected label/feature inspection in this pass; guard still excludes 2024→2025; no 2025 result | Reads restricted to sealed development closure; structural metadata only from prior docs | Informational | ACCEPT | Keep SEALED; prior external human familiarity cannot be disproved by repository checks |
| F15 | Final decision | Exact final model identity cannot yet be pinned; no final execution protocol is frozen | B1; four-fold grant/artifact inventory | Blocking | HOLD | Resolve handoff, then complete support/rejection/inconclusive partition before opening |
| F16 | Promotion | Scientific comparison gives no PRIMARY/public/trading authority | BENCHMARK vs CHALLENGER/EXPERIMENTAL identities; no activation edits | Informational | ACCEPT | Separate promotion/calibration gates remain |

## Development scientific interpretation

| Fold | Paired N | Logistic − BaseRate Brier | Logistic − BaseRate log loss |
|---|---:|---:|---:|
| 2021 | 248 | −.0015587473 | −.0032537058 |
| 2022 | 248 | +.0029200387 | +.0058957049 |
| 2023 | 225 | −.0266923847 | −.0557561484 |
| 2024 | 248 | −.0580877078 | −.1346018022 |
| Pooled development | 969 | −.0207161381 | −.0467194681 |

2021 gives a small point-estimate advantage to Logistic; 2022 a small advantage
to BaseRate. Their development intervals both cross zero. The larger 2023/2024
differences dominate the pooled result; 2023 intervals still cross zero, while
2024 intervals do not. This is not uniform evidence of better forecasts in every
year and is not proof of an enduring regime effect.

The frozen BaseRate probabilities are .60, .50, .35 and .75, while Logistic's
annual mean probabilities stay near .52–.53. Thus the large later differences
are consistent with a less extreme challenger versus a short-window benchmark
that was mismatched to that year's observed prevalence. This explains the
comparison without asserting that the five learned covariates add useful skill.
No new empirical subgroup, threshold or model comparison was run in this review.

Pooled BaseRate/Logistic Brier: .2713544892 / .2506383511; log loss:
.7411579082 / .6944384401. Fixed .5 on the same pairs is .25 Brier and
.6931471806 log loss. Logistic is slightly worse on both fixed-.5 diagnostic
losses. Equal pooled accuracy (.51496388 for both learned/frozen arms), narrow
Logistic probability concentration and sparse reliability tail bins caution
against claims of calibration or incremental prediction skill. This is an
honest limitation, **not an added failure criterion**.

The pooled 97.5% development intervals are Brier
[-.0317257715, -.0103566515] and log loss [-.0702934563, -.0244489871].
They remain **DEVELOPMENT_ONLY**. Bootstrap uses 5 sessions, 5,000 replicates,
PCG64 seed 1729, original masks and fixed linear quantiles .0125/.9875.
Neither these intervals nor the 191 complete development blocks substitute for
final holdout evidence.

Support is adequate under the registered guards: each fold at least 150 pairs,
30 per class, 80% grid coverage and 20 complete blocks; pooled at least 600.
All three stability requirements pass: negative mean Brier in three folds,
no Brier worsening >.02, no log-loss worsening >.05. Exclusions stay exactly
20 demerger-feature, one unsupported-action label, one protected-target slot.
No fold, threshold, seed, feature, exclusion or dependency drift was found.

**Answer to the scientific-evidence question:** development results are clean
enough under the accepted bounded retrospective research assumptions to merit
continued pre-holdout preparation, but do not themselves show final support.
**Answer to the opening question:** NO at this checkpoint because the exact
planned final artifacts and their admission are missing. This is not a
post-hoc statistical veto based on the fixed-.5 diagnostic.

## Final protocol status — not frozen, no execution authority

The following are inherited constraints, not a newly executable grant:

- Subject `RELIANCE:NSE:NSE_EQUITY:EQUITY`; target
  `equity.next_session_close.return_gt_zero/1.0`; CORPORATE_ACTION_ADJUSTED;
  SIMULATED_RESEARCH; existing five-feature schema and research profile.
- Structural holdout: qualified **2025 reference sessions** and their true next
  scheduled target sessions, including a terminal 2026 target if needed. Never
  include the 2024 reference targeting 2025. Do not drop the last valid 2025
  reference merely because its target crosses the year boundary.
- Existing qualification documents 249 structural 2025 slots. That exceeds
  the 200-slot feasibility floor but does **not** establish final paired N,
  class support, valid labels, feature coverage or complete paired blocks.
  Those were not measured here. No protected class counts are reported.
- Pair only available forecasts against identical qualified outcome revisions,
  with fixed scope/action/feature/label rules. The final-fold BaseRate must use
  the last 20 scheduled cutoff-safe transitions; no backfill or smoothing.
- Primary metrics remain Brier and natural-log loss with metric-only epsilon
  1e-15; difference remains Logistic minus BaseRate. Accuracy at .5, fixed bins,
  fixed-.5 and disagreement are descriptive, never optimized.
- Five-session non-circular moving blocks remain a defensible registered
  short-dependence approximation; a roughly one-year grid is not structurally
  too short for the declared method. This is not proof that dependence ends
  after five sessions. No outcome-based block-length selection is permitted.
- Retain 5,000 replicates, fresh PCG64 seed 1729, fixed original-grid mask,
  concatenate/truncate to T slots, 97.5% two-sided percentile intervals with
  linear .0125/.9875 quantiles; no zero-pair redraw.
- The accepted final support requirements include at least 200 pairs, 40 in
  each class, 80% intended-grid coverage, 20 complete five-session blocks and
  adequate integrity/interval conditions. The accepted final support bounds
  are Brier upper bound strictly <0 and log-loss upper bound ≤+.01 nats,
  together with the passed development gates.

An exact mutually exclusive final support/rejection/inconclusive rule is **not
issued or fingerprinted in this stopped pass**. Failure to demonstrate support
must not automatically become rejection. The resumed freeze must settle that
partition, insufficient-support precedence, boundary equalities and failure
handling before any protected labels. There is **no final protocol fingerprint**;
hashes below identify prior evidence, not authorization to open the holdout.

No one-shot execution state machine or persistent consumed-grant record was
created. Future accepted design must consume authority before outcome access,
reject a second execution and post-open mutation, distinguish read-only replay
from a new scientific attempt, and prevent recovery from quietly becoming a
second attempt. Those guarantees cannot be claimed from a prose promise alone.

Promotion boundaries are unchanged for any future outcome:

| Possible future result | Subsequent state, not authorized action here |
|---|---|
| LOGISTIC_SUPPORTED | Scoped scientific success and independent closure; retain CHALLENGER until separately governed promotion; no automatic PRIMARY, public runtime, calibration or trading authority |
| LOGISTIC_NOT_SUPPORTED | Retain BaseRate; close Logistic v1 unsupported; a revised candidate needs a new version/experiment, never tune against the opened holdout |
| INSUFFICIENT_EVIDENCE | Preserve uncertainty and evidence; do not recycle/reopen the holdout; future ACTUAL evidence or a new experiment needs separate approval |

## Policy classification and exact next step

| Item | Classification | Consequence |
|---|---|---|
| Target, basis, features, folds, BaseRate arithmetic, metrics, bootstrap, margins | NO_CHANGE | Preserve preregistered research policy |
| Interpretation of pooled gains and fixed-.5 diagnostic | RESEARCH_POLICY_CLARIFICATION | Scoped evidence, not feature skill or a new rejection rule |
| Missing fifth-fold model/scaler/BaseRate artifact and grant | BLOCKER | Deny opening; no placeholder protocol identity |
| Distinguish the original fifth pre-open fit from forbidden post-open refitting | ARCHITECTURE_CLARIFICATION | Requires a separately requested Learning handoff, not Evaluation fitting |
| Final classification partition and one-shot control tests | DEFER | Resume only after B1 is resolved; no premature frozen-protocol claim |

Exact next prompt title:
**TIAF A7 / FF-1 — PRE-HOLDOUT FIFTH-FOLD ARTIFACT PREPARATION AND NO-REFIT AUTHORITY RECONCILIATION**.

That next request should explicitly authorize only the original fifth-fold
preparation: exact unprotected cutoff-safe memberships, unchanged model/scaler
configuration and approved dependencies, one bounded fit, canonical model/scaler
and BaseRate artifacts with replay, and continued 2025 label protection. It must
not authorize scoring or opening the holdout. Then repeat this independent
review to pin the final protocol and its authorization/one-shot tests. Reusing
the 2024 model instead would be a research-protocol amendment requiring explicit
review; it is not an implementation shortcut.

The requested accepted-state commit recommendation is **not applicable** because
no final protocol was frozen. No tag recommendation; FF-1 baseline waits for
separately authorized final evaluation and independent closure. No commit/tag/push.

## Evidence pins and validation

| Evidence | Fingerprint |
|---|---|
| Development evaluation | `5f6d4342c61017fecda2196715d707a356ff8728eb0ec1f6996c362723ba19e1` |
| Development Ledger | `62bc746d90386f3b718bf6fe106f4a80832bfa8206ea3605ec96bbb2e5817246` |
| Logistic development forecast run | `4dc2adb6f2bb9977bf3a06c2c5903065223cfc6e2c6a58898c0cb65090197812` |
| Development policy | `1b725727e3400feb0f79cfc80b6239e62939b0f73f8ec53a6e1ac5fa4d7eb11e` |
| Ground Truth Journal | `5784f7b82cae781339a7b9d3afe689f905a6af318ff50baa095f1017653a89e1` |
| Paired population | `f8ac38d7afdffab2b3be21a467dfa913df77b02adbdaa4f04eb1c5d89b847830` |
| Approved dependency lock | `54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86` |
| Research profile | `1e616cc7a2f3654d856b916e790d054a6c1ff7f10efe2b316cf0a44835011c45` |

Protected data safeguards for this review: no raw source/qualification was
opened; development corpus only. Guarded replay blocks **all** other
`data/ff1` reads, socket creation and sklearn/SciPy/joblib imports. It returned
MATCH, zero blocked-source attempts, and all 4,011 artifact byte hashes identical.
No empirical training, final inference, labels, class balances, protected metrics,
calibration, provider/broker/network operation or file containing secrets.
This verifies this review's access boundary, not omniscient absence of earlier
human knowledge of historical market events.

| Validation in this review | Result |
|---|---|
| Guarded development replay and artifact byte preservation | MATCH |
| Existing grant and forecast types reject final fold | Two read-only validation probes PASS |
| FF-1.4 / FF-1.3 / training-admission targeted regressions | 91 passed in 388.58s |
| Compileall `src scripts` | PASS |
| Ruff `src tests scripts` | PASS |
| mypy `src tests` | PASS, 635 source files |
| Dependency checks | `pip check` PASS; `uv lock --check --offline` PASS, 76 packages; no install/network |
| Documentation links and `git diff --check` | PASS, 273 local link targets in four changed documents; balanced fences and final newlines |
| New final-protocol/one-shot tests | Not added: authorization NO; no final protocol or runtime was implemented |
| Full suite / other broad regressions | Not rerun after the required blocker stop; prior FF-1.4 result was 3,327 full / 851 focused passes, not claimed as new executions |

Exact targeted command:

```bash
.venv/bin/pytest -q \
  tests/unit/evaluation/test_development_comparison.py \
  tests/unit/forecasting/test_logistic_forecasts.py \
  tests/unit/forecasting/test_logistic_training_admission.py
```

The captured development implementation and preregistered plan hashes were also
compared to the evaluation manifest and remain identical. There is no diff in
`src`, `scripts`, `tests`, dependency files or locks.

Changes in this review are documentation only: this report and current-status
pointers in `README.md`, `docs/MILESTONES.md`, `docs/IMPLEMENTATION_ROADMAP.md`.
Runtime, tests, dependencies, research records and protected source data unchanged.
A6 baseline remains `6dc2ff304aae0e87540260b092919bb91e4d4189`; FF-0 remains
`e5283c9eaa4294bd236186d663335efdf7dab236`. No commit/tag/push.
