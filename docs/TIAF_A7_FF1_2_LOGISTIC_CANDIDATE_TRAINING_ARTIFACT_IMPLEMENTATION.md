# TIAF A7 / FF-1.2 — Logistic candidate training artifacts

## Status and authority

2026-09-21, Asia/Kolkata. **HOLD_FF1_2** pending the accepted plan's independent
review of the exact dependency lock before empirical fitting.

```text
LOGISTIC_CANDIDATE_TRAINING_COMPLETE = NO
PROTECTED_HOLDOUT_STATUS = SEALED
```

Implementation and synthetic engineering checks are separate from empirical
completion. The user authorized the four development-fold training artifacts;
the [plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md#6-logistic-instrument-and-optional-dependency)
also requires independent approval of the exact transitive dependency lock.
That approval has been requested, not inferred. No empirical worker was started.
Do not proceed to FF-1.3 on this HOLD record.

Entry tree was clean at `2649cc6` (`feat(a7.ff1.1a): qualify RELIANCE empirical
research dataset`). A6 remains `6dc2ff304aae0e87540260b092919bb91e4d4189`;
FF-0 remains `e5283c9eaa4294bd236186d663335efdf7dab236`. Package version remains
`0.1.0`; these additive research envelopes use schema `2.0`, model artifact and
instrument version `1.0`. Existing FF-0 contracts/defaults are unchanged.

## Qualified input and explicit gates

The existing [FF-1.1A qualification](TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md)
remains authoritative. Its original private artifact and source CSV are not
rewritten or requalified. Preflight verified approved qualification bytes before
decoding, native reconstruction and the dataset byte hash before constructing
the exact four training inputs. No prices are parsed from the CSV by Learning.

| Pin | Exact value |
|---|---|
| Qualification | `4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51` |
| Qualification file SHA-256 | `69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca` |
| Dataset CSV | `d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6` |
| Research profile | `1e616cc7a2f3654d856b916e790d054a6c1ff7f10efe2b316cf0a44835011c45` |
| Feature schema/profile | `76e63292685ee0b3b41f7ab033407e6bd014fc802d2092a2ed227888bdc71676` |
| Candidate dependency lock | `54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86` |

Subject: RELIANCE / NSE cash equity. Target:
`equity.next_session_close.return_gt_zero/1.0`. Feature schema:
`ff1.reliance.a2_daily_five/1.0`, in this exact order:
`ret_1`, `ret_5`, `sma20_distance`, `realized_vol_20`, `relative_volume`.

Qualification, dataset, profile and schema seals must match the explicit COLD
grant. Missing/changed qualification is refused; no age-based magic refresh,
current-alias substitution, unqualified fallback, re-derived A2 feature or new
Ground Truth construction. Assessment cannot postdate the grant. The research
profile is adjusted fresh-download SIMULATED research, **not CAPTURED_AS_KNOWN**;
rights remain UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING. No rights or
production approval is created by training.

## Four admitted folds — preflight, not empirical fit results

All training starts at 2018-01-01. Cutoffs below are **09:15 +05:30**, the whole
embargo session's open. Targets and assumed label availability must be strictly
before the cutoff. Membership and chronological ordering are compared to the
qualification, not guessed from year ranges or row counts.

| Artifact entering | Last train origin | Cutoff / embargo date | Train | Positive / zero | Ineligible | Purge-only | Embargo | Sealed | Later unsealed |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 2020-12-29 | 2020-12-31 | 720 | 374 / 346 | 21 | 1 | 1 | 250 | 990 |
| 2022 | 2021-12-29 | 2021-12-31 | 968 | 510 / 458 | 21 | 1 | 1 | 250 | 742 |
| 2023 | 2022-12-28 | 2022-12-30 | 1216 | 637 / 579 | 21 | 1 | 1 | 250 | 494 |
| 2024 | 2023-12-27 | 2023-12-29 | 1441 | 753 / 688 | 42 | 1 | 1 | 250 | 248 |

Each row reconciles to 1,983 requested observations across the disjoint buckets.
Positive + zero equals train. Total purge is **purge-only + embargo = 2**, not
an extra count on top of those columns. Total excluded is requested minus train.
Total exclusions are **1,263 / 1,015 / 767 / 542** respectively for 2021–2024;
their disjoint reasons are retained above and in each typed fold audit.
Sealed means structural exclusion, not a missing label, zero or failed model.

The protected 2025 fold cannot be selected. All 249 protected origins and the
2024-12-31 origin targeting 2025 are excluded before reading their features or
labels for training. The accepted qualification contains null protected labels,
not secretly decoded values. TrainingRow independently rejects reference or
target dates in 2025+. No protected probability, class balance or outcome is
computed, sent to the worker or serialized into model artifacts.

## Fixed model, scaler and dependency boundary

```text
LogisticRegression(
    penalty="l2", C=1.0, solver="lbfgs", tol=1e-8, max_iter=1000,
    fit_intercept=True, class_weight=None, dual=False,
    warm_start=False, random_state=1729, n_jobs=1
)
StandardScaler(with_mean=True, with_std=True), population variance ddof=0
```

There is one configuration, no tuning or fallback solver, no imputation, clipping,
selection, calibration or automatic iteration increase. The scaler sees only the
fold's TRAIN rows. It persists five means, variances, positive scales, feature
order, count and constant-column indices. Constant/numerically indistinguishable
columns retain their position with scale one under the pinned sklearn rule.
See the versioned [StandardScaler](https://scikit-learn.org/1.7/modules/generated/sklearn.preprocessing.StandardScaler.html)
and [LogisticRegression](https://scikit-learn.org/1.7/modules/generated/sklearn.linear_model.LogisticRegression.html)
APIs. ConvergenceWarning or exhaustion of 1,000 iterations fails the fit; no model
is accepted from it.

Optional extra: `forecast-training`. Candidate reviewed environment: CPython
**3.12.3**, sklearn **1.7.2**, NumPy **2.3.3**, SciPy **1.16.2**, joblib **1.5.2**,
threadpoolctl **3.6.0**. [Platform wheel lock](../requirements/ff1-training-linux-py312.lock)
contains exact hashes for Linux x86_64 / CPython 3.12. `uv.lock` also includes the
optional extra; no pre-existing dependency version was upgraded. Only the new
ML packages were installed in the project environment; the lockfile tool used
for maintenance was installed in `/tmp`, not as a runtime dependency.

The parent launches a serial subprocess per fold with a credential-free,
single-thread numeric environment. Before ML imports the child applies hard
512 MiB address-space and 60-second CPU limits; the parent enforces 60-second
wall timeout and kills/reaps the child on timeout. Four fits maximum, one attempt
per fold, 600-second campaign deadline. No automatic resource increase. Usage
records actual elapsed/CPU time and peak RSS where available; monetary cost is
UNPRICED, never silently zero. Missing/incompatible dependencies yield UNAVAILABLE;
convergence, integrity and resource failures yield FAILED with no usable model.
Linux lifetime `ru_maxrss` can include the launcher's fork/exec high-water before
the worker installs its limits; it is retained as observed, not falsely called a
post-limit worker-only peak. Job records separately verify the actual kernel
address-space limit (536,870,912 bytes) and CPU limit (60 seconds). A bounded
64 MiB parent/child diagnostic reproduced the inherited high-water behavior.

## Artifacts, reconstruction and Learning ownership

```text
Evaluation's pinned qualification + explicit Learning grant
    -> exact train-only input + sealed fold manifest
    -> isolated optional scaler/Logistic worker
    -> transparent scaler/model JSON + job usage/failure
    -> immutable parent training-run record
    -> pure numeric reconstruction (no sklearn, no fit, no provider)
```

New lean `tiaf.learning` modules implement the architecture's Learning owner,
not a second forecasting framework. The native logical identity is
`forecaster:logistic-regression`, instrument `1.0`, **CHALLENGER / EXPERIMENTAL**,
RAW_UNCALIBRATED. There is no PRIMARY registration, active alias, public capability,
COLD inference binding, promotion service or BaseRate change. FF-1.3 will own
separately admitted runtime/capture integration.

Model JSON nests the immutable manifest/grant, exact train IDs and order/value
hashes, subject/target/schema, cutoff/range/count/classes, scaler, coefficients,
intercept, convergence/n_iter, actual library/backend versions and aware creation
clock. No raw prices, full feature/label rows, secrets, pickle/joblib loader or
arbitrary imports are embedded in the artifact. The qualified private input
remains the external reconstructable source lineage.

Scaler, configuration, manifest, reconstruction, model, job and parent run have
separate canonical SHA-256 fingerprints. Full audit seals retain real job clocks;
scientific model identity excludes actual capture/qualification/job timestamps,
using dataset/profile/schema and chronological numeric training values instead.
Scientific identity still pins code, dependency lock and fit cutoff. Repeat
synthetic fits in this locked environment reproduce scientific identity; full
audit hashes correctly differ. No cross-platform/BLAS bitwise promise is made.

Reconstruction performs frozen standardization, five-term dot product plus
intercept and overflow-safe sigmoid. It rejects nonfinite inputs/transforms/logits.
Five TRAIN-scaler-derived algebraic probes (mean, ±1 scale, ±1,000,000 scales)
must match sklearn predict_proba within absolute **1e-12**. They are engineering
probes, not market forecasts or model-quality evaluation; no probe probabilities
or outcome comparisons are retained. Coefficients/intercept are present in tested
synthetic JSON artifacts; empirical coefficients/convergence remain **NOT_RUN**.

Storage is a new private attempt directory with exclusive-create, fsynced,
content-addressed files: `grant-<hash>.json`, `manifest-<hash>.json`,
`scaler-<hash>.json`, `model-<hash>.json`, `job-<hash>.json`, `run-<hash>.json`, and
a sanitized `summary.json`. Each output record is at most 1 MiB and the store
at most 32 MiB, below campaign limits. No row shards are emitted. Existing FF-0
record limits and serializers are unchanged. The pre-existing native FF-1.1A
qualification is separately bounded to 32 MiB and checked against its approved
byte hash, not misrepresented as a v1 FF-0 record.

Each write is read back through the native model and compared exactly. A crash
leaves an incomplete attempt (grant/jobs, no COMPLETE run); there is no atomic
multi-file-transaction claim or implicit retry/overwrite. Parent references point
to jobs/models, while models point to the grant: no cyclic fingerprint dependency.
Empirical artifact paths/fingerprints and parent run are **not yet available**.

## Operator command and stop boundary

After independent approval of the exact lock, invoke once with a new directory:

```bash
.venv/bin/python scripts/train_ff1_logistic_candidate.py \
  --output data/ff1/logistic_training_20260921 \
  --approve-dependency-lock 54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86
```

Do not copy the approval flag as a substitute for actual review. The CLI checks
the lock and approved CPython version; no auto-install or network call occurs.
`--qualification` and `--dataset` may relocate identical pinned files, not select
another population. Output must be new and Git-ignored under `data/ff1`. Exit 0
means four complete artifacts, 1 means HOLD/partial/failure, 2 means invalid CLI
or approval/output boundary. Keep raw data and local model artifacts out of Git.

No empirical fit has run in this pass pending approval. Local synthetic fit calls
in engineering tests are real and not misreported as zero compute. No Brier,
log loss, accuracy, calibration, reliability, bootstrap or paired evaluation
was computed by this implementation. Regression tests elsewhere exercise their
existing synthetic evaluation behavior; that is not a new FF-1 empirical study.
No provider, market-data, LLM or broker call was made. Public package downloads
for environment preparation were the only external access besides software docs.

## Validation and next step

| Check | Result |
|---|---|
| FF-1.2 targeted modules | 55 passed in 132.64s; after RSS-accounting correction, worker/artifact module 40 passed in 15.65s |
| Forecasting + Evaluation unit suites (includes FF-1.1/1.1A regressions) | 747 passed in 260.07s |
| FF-0 acceptance | 28 passed in 38.06s |
| Full repository suite, final corrected state | **3,251 passed in 533.87s** |
| Compileall `src scripts` | PASS |
| Ruff `src tests scripts` | PASS |
| mypy `src tests` | PASS, 625 source files |
| Docs | 5 Markdown files, 272 local link targets and balanced fences PASS |
| CLI help | PASS, explicit dependency-lock approval and new output directory |
| Dependency consistency | `pip check` PASS; `uv lock --check --offline` PASS; all prior locked versions preserved |
| Source preservation | All six original provisioning/qualification byte hashes unchanged |
| Whitespace | `git diff --check` PASS |

The first full run had 3,250 passes and one failure in the new test's assumption
that process-lifetime RSS high-water must be below a subsequently installed
address-space cap. The measured 575,760 KiB included launch high-water; the
bounded diagnostic above reproduced that inheritance. This was an engineering
accounting correction, not a failed fit, relaxed resource policy or model retune.
The corrected tests verify the kernel-reported caps and retain raw RSS honestly.
The subsequent full run passes all 3,251 tests; code/test/dependency hashes were
unchanged during that final run. Tracked and newly created files also pass
whitespace checks. This closes the engineering failure, not the independent
lock-review/empirical-fit gate.

The complete regression commands use `.venv/bin`:

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_logistic_training.py \
  tests/unit/forecasting/test_logistic_training_admission.py
.venv/bin/pytest -q tests/unit/forecasting tests/unit/evaluation
.venv/bin/pytest -q tests/acceptance/ff0
.venv/bin/pytest -q
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
git diff --check
```

Changed code: new `learning/__init__.py`, `forecast_artifacts.py`,
`forecast_training.py`, `forecast_worker.py`, `forecast_jobs.py`; internal script;
two targeted test modules; optional extra and lockfiles. Documentation changes:
this record, scripts guide and current-status pointers. No scoring, A2 feature,
FF-0, provider, specialist, facade, Shell, A4/A5/A6 or A8 behavior changed.

Exact file inventory: **10 created, 6 modified**.

Created:

- `src/tiaf/learning/__init__.py`
- `src/tiaf/learning/forecast_artifacts.py`
- `src/tiaf/learning/forecast_training.py`
- `src/tiaf/learning/forecast_worker.py`
- `src/tiaf/learning/forecast_jobs.py`
- `scripts/train_ff1_logistic_candidate.py`
- `requirements/ff1-training-linux-py312.lock`
- `tests/unit/forecasting/test_logistic_training.py`
- `tests/unit/forecasting/test_logistic_training_admission.py`
- `docs/TIAF_A7_FF1_2_LOGISTIC_CANDIDATE_TRAINING_ARTIFACT_IMPLEMENTATION.md`

Modified:

- `pyproject.toml`
- `uv.lock`
- `README.md`
- `scripts/README.md`
- `docs/IMPLEMENTATION_ROADMAP.md`
- `docs/MILESTONES.md`

Blocker: exact dependency-lock approval before the four empirical fits. After
approval, run the bounded command, record each empirical scaler/model/run seal,
convergence and reconstruction evidence, then reassess FF-1.2 acceptance.
Only **if accepted**, next prompt:
**TIAF A7 / FF-1.3 — LOGISTIC WALK-FORWARD FORECAST GENERATION**.

After acceptance/review, recommended checkpoint:
`feat(a7.ff1.2): implement logistic candidate training artifacts`.
No commit, tag or push was performed. No tag is recommended yet.
