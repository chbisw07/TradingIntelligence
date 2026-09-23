# A7 / FLC-3 — Bounded development-only optimization

Checkpoint: 2026-09-23, Asia/Kolkata. **FLC3_ACCEPTED**. Implementation and
validation complete. Entry HEAD: `2873f83` (accepted FLC-2).

## Scope and resolved prerequisite

The initial FLC-3 review returned **HOLD_FLC3**: the existing FLC-2 executable
recipe and frozen FF-1 worker/artifact contracts could not express varied
configurations. No optimizer or fits were delivered by that earlier review.
Its diagnostic slice passed 22 tests, with 73 deselected; that was not acceptance.

The user subsequently explicitly authorized this narrow extension:

```text
FLC3_TRAINING_EXTENSION_AUTHORIZED = YES
extension_scope = SYNTHETIC_ONLY
training_service = EXISTING_FLC2_SERVICE
new_worker_version = REQUIRED
new_artifact_adapter_version = REQUIRED
FF1_FROZEN_FILES_MODIFIED = NO
FF1_ARTIFACTS_MODIFIED = NO
FLC2_EXISTING_BEHAVIOR_CHANGED = NO
EMPIRICAL_TUNING_AUTHORIZED = NO
CONSUMED_2025_REUSE = FORBIDDEN
PRODUCTION_TUNING_AUTHORIZED = NO
```

This resolves the prerequisite without a second training owner. Frozen Logistic
v1 is not a mutable trainer. The new worker version is `flc3.synthetic.1`, config
version `flc3.synthetic.config.1`, artifact-adapter version
`flc3.synthetic.artifact.1`. These artifacts are internal engineering candidates,
not registered/public forecast implementations or scientific qualification.

## Ownership and execution

```text
immutable OptimizationRequest + externally supplied exact grants
    │ finite grid; first ≤3 configurations; two ordered folds each
    ▼
Learning: TrialPlan → one attempt per TrainingIdentity
    ▼
FLC-2 execute_synthetic_once
    ├── existing fixed 600-row recipe / native v1 worker (UNCHANGED)
    └── explicit SyntheticSpec / versioned synthetic trial worker (NEW)
              │ TRAIN-only scaler + Logistic fit; never selection scoring
              ▼
existing TrainingExecution → TrainingResult → TrainingBundle
              │ same existing content-addressed research custody
              ▼
Evaluation-owned synthetic adapter → existing arm_metrics
              │ immutable development report; no fitting or selection
              ▼
Learning: mean of two recorded fold objectives → deterministic selection
              ▼
selected existing artifact identity; EXPERIMENTAL
approval absent / activation false / promotion false / no selection refit
```

The [FLC-2 service](../src/tiaf/learning/forecaster_reference.py) has one explicit
dispatch branch. Its original `synthetic_input` function and fixed execution
branch remain unchanged. The
[new service adapter](../src/tiaf/learning/forecaster_trial_service.py) consumes
the same external authority, attempt records and request/execution/result
contracts. The [worker](../src/tiaf/learning/synthetic_trial_worker.py) alone owns
the new sklearn invocation. The [optimizer](../src/tiaf/learning/optimization.py)
imports neither sklearn nor numpy and cannot supply its own fit callback.

One canonical forecaster registry remains unchanged. `OptimizationStore` only
adds codecs over `ForecasterStore` and the existing `ResearchForecastStore`; it
does not introduce another persistence engine, experiment tracker or lifecycle
authority. Evaluation delegates metrics to the existing
[independent Evaluation implementation](../src/tiaf/evaluation/forecast_comparison_metrics.py).
No duplicated Brier/log-loss/accuracy formulas or FF-1 scientific verdict logic.

## Contracts and deterministic plan

The [optimization contracts](../src/tiaf/learning/optimization_contracts.py) are
frozen, sealed, extra-field rejecting and content fingerprinted. Semantic
collections are tuples; JSON uses ordinary arrays and round-trips. Timestamps
reject naive datetimes and normalize to canonical `Asia/Kolkata` / `+05:30`.

| Object | Explicit content |
| --- | --- |
| OptimizationRequest | Request ID/version, experiment ID, Logistic family and exact version, synthetic target/schema, search space, objective/population, budget, external authority, qualification/dataset/profile/code/dependency pins, aware creation clock and scope |
| SearchSpace / Domain | ≤3 uniquely named domains; each 1–8 finite typed categorical, integer, float or boolean values; no expressions/callbacks, duplicates or nonfinite numbers |
| Objective | Existing Brier/log-loss/accuracy metric ID; MINIMIZE or MAXIMIZE; exact development population; equal mean of two temporal fold values |
| TrialDefinition | Stable trial/candidate ID, index, parent request ref, assignment/fingerprint, versioned recipe/fold/config, unique FLC-2 TrainingIdentity |
| TrialRecord | Definition ref, status/reason, bundle/execution lineage, evaluation ref, model identity, objective and elapsed time |
| OptimizationResult | All ordered trial refs, eligible candidate scores, selected second-fold trial/model, declared selection rule, failures/budget/time, experimental/no-approval outcome |

Domains are generic data contracts; the authorized executable adapter accepts
only **C** (0.05–10.0) and **fit_intercept** (boolean). Solver, tolerance, seed,
iteration ceiling and scaler configuration are not optimization knobs. Unsupported
parameters, including calibration parameters, fail closed. Every declared grid
point is validated even when the trial cap excludes it from execution.

Plan order is Cartesian product in declared domain/value order, truncated to
the first `max_trials / 2` configurations, then folds 0 and 1. There is no random
sampling; seed 1729 is pinned for model fitting. The bounded grid has at most
512 points and execution at most six attempts. Assignment hashes identify
configurations; parent request/candidate/fold hashes identify trials. Child
experiment IDs bind the parent request and candidate: a changed request/config
cannot inherit an earlier exact training grant.

## Machine-enforced evidence boundary

The [synthetic recipe](../src/tiaf/learning/synthetic_trials.py) accepts **no data,
file, symbol, provider or market-date input**. It authors five features and binary
labels from a fixed integer-index formula. Indices are not market sessions.
RELIANCE/Dhan/2025 observations cannot enter this extension through its contracts.

| Fold | Train positions (inclusive) | Development positions (inclusive) |
| --- | --- | --- |
| 0 | 0–599 | 600–639 |
| 1 | 0–639 | 640–679 |

The second fold may train on the earlier fold's development positions, as an
explicit expanding temporal design; no fold trains on its own development rows.
The worker materializes training positions only. The scaler is fitted only on
those rows. Evaluation separately materializes its 40-row development population.
These are authored engineering sequences, not a market backtest or unseen test
cohort. Optimized development scores are not unbiased performance estimates.

Request/grant scope must be DEVELOPMENT_ONLY, protected/consumed access false,
experiment OPEN and holdout NONE. Dataset/qualification/profile/target/schema
must match compiled synthetic identities. Exact implementation and dependency
lock hashes are checked before launch and again inside the worker. External
per-trial grants bind request, experiment, input, qualification, custody root and
time window. The optimizer cannot mint them. Hashes do not authenticate a human:
the trusted caller remains responsible for genuine grant issuance and history.

Closed, protected, consumed or mismatched authorities are rejected before any
worker call. Renaming a grant cannot repeat an attempted training request.
Lifecycle/approval fields cannot override scope; unknown fields are rejected.
There is no empirical tuning or production tuning capability hidden behind a
synthetic label. FF-1 v1, its grants and its consumed 2025 evidence are untouched.

## Bounds, failures and candidate selection

| Bound | Enforced policy |
| --- | --- |
| Trial attempts | 2, 4 or 6 maximum; at most 3 configurations × 2 folds; no retries |
| Wall budget | Explicit ≤360 seconds; remaining budget checked before training/evaluation; no expired result selected |
| Worker wall/CPU | Parent kills/waits on timeout ≤60 seconds and remaining campaign budget; worker RLIMIT_CPU 60 seconds |
| Worker memory | RLIMIT_AS 512 MiB; core dumps disabled |
| Population/features | Compiled maximum 640 training observations, 40 evaluation observations per fold, exactly 5 features |
| Concurrency | One local worker; numeric thread pools restricted to one |
| Storage | Existing ≤1 MiB/record, ≤65,536 blobs, ≤2 GiB; canonical JSON, no pickle |

The wall budget stops admitting numerical work and excludes over-budget output;
bounded metadata persistence/final failure accounting may finish after that
deadline. It is not a promise to terminate Python/filesystem finalization at an
exact instant. Memory limits apply to the isolated fit process, not the host test
runner. Resource cost remains explicitly UNPRICED, not falsely reported as zero;
unobserved CPU/RSS values stay absent in the existing execution contract.

The dedicated store is single-writer, as before. A durable exclusive campaign
claim precedes the first trial, and an attempt claim precedes each subprocess.
Every planned trial gets a recorded outcome: EVALUATED, TRAINING_FAILED,
EVALUATION_FAILED or BUDGET_EXCEEDED. Failure reason/time/available lineage remain
visible. Interrupted or failed persistence cannot publish a complete result;
there is no resume/retry of consumed attempts. Admission/custody faults raise
explicitly rather than manufacturing a successful campaign.

Only configurations with **both folds evaluated** are eligible. Their primary
score is the equal mean of the two recorded objectives. Sort by the declared
direction, then lexical stable candidate ID on an exact tie. Select the winning
configuration's **existing second-fold artifact**. No hidden seventh fit,
complexity heuristic, manual override, promotion or activation. If no complete
configuration survives, return NO_VALID_TRIAL with no selected artifact.

## Persistence and recorded-only replay

```text
caller-pinned result fingerprint
  ├─ request → search/objective/budget/pins
  ├─ plan → ordered definitions → assignment/spec/training request
  ├─ external grant + durable campaign claim
  ├─ trial records
  │    ├─ authority/attempt → TrainingBundle → job/model/scaler identities
  │    └─ development Evaluation report → recorded objective
  └─ deterministic aggregation/tie rule → selected artifact identity
```

`replay_optimization(OptimizationStore(root), result_reference)` is read-only.
It resolves exact canonical records, reconstructs the deterministic plan, checks
training and evaluation lineage, and reselects using **recorded objectives**.
It does not refit, predict, recompute metrics, contact providers, read market data
or re-open protected evidence. It returns MATCH or MISMATCH. Changed bytes,
missing records and a resealed wrong selected artifact fail verification.
Replay is not a new scientific evaluation or independent fit reproduction.

Creation clocks and measured timings make full artifact fingerprints specific to
an execution; deterministic planning/selection does not promise identical wall
times or job fingerprints across new executions. The same captured record has
the same fingerprint and replay result. Historical grants are checked as recorded
lineage, not renewed by replay or invalidated by today's wall clock.

## Concrete synthetic reference

The reference is [test_optimization.py](../tests/unit/forecasting/test_optimization.py).
It preregisters `C=[0.05, 1.0]`, `fit_intercept=[true, false]`, six attempts,
Brier MINIMIZE, the fixed temporal folds and stable-ID tie rule **before fits**.
The fourth grid configuration is not executed because of the declared cap.

Observed engineering run (not empirical financial evidence):

| Executed configuration | Fold-mean Brier | Result |
| --- | ---: | --- |
| C=0.05, intercept=true | 0.09884391026455586 | Eligible |
| C=0.05, intercept=false | 0.11148047929768748 | Eligible |
| C=1.0, intercept=true | 0.09373466559257404 | Selected second-fold artifact |

Six unique training requests/artifacts, three distinct configurations and
distinct learned coefficient vectors were verified. No extra selection fit.
Observed combined-test campaign: 11.18 seconds, six evaluated, zero failed.
Request fingerprint `c74e2959162f84f16f74c55e409eef6bfe20549add634efc04e8ad6471c073c8`;
result fingerprint `676019d27454294cbf87e370e0cdfee6cbd61c34ae85fcc03fc47b436fd845d5`.
The test custody directory is ephemeral, not a production model store. Every
test invocation creates new authorized synthetic engineering attempts; the
six-attempt cap is per campaign, not across separate test-suite invocations.

The selected identity remains Logistic CHALLENGER / EXPERIMENTAL, approval
absent, activation false, promotion false. Numerical values above demonstrate
plumbing, not superiority, calibration, profitability or readiness for use.

## Compatibility and validation

| Surface | Change | Evidence |
| --- | --- | --- |
| FLC-1 inference / registry | None | Existing seam regression |
| FLC-2 fixed synthetic recipe | None | Recipe and fixed execution branch AST-identical to accepted HEAD; 55 existing tests |
| FLC-2 execution/custody | Additive exact-version branch/codecs | Same request/execution/result/persistence owner |
| FLC-3 | New internal synthetic orchestration | 60 targeted tests; six real fits per reference campaign |
| FF-0 BaseRate | No byte/semantic change; still non-trainable | Existing acceptance/regression |
| FF-1 frozen Logistic | No source/artifact/config change | Four canonical records and all 78 source pins MATCH |

FF-1 remains INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE; BaseRate BENCHMARK;
Logistic CHALLENGER / EXPERIMENTAL; promotion NO; 2025 CONSUMED; execution count 1;
post-holdout refit forbidden. The preservation audit uses plain JSON canonical
hashes and file SHA-256 only, never scientific-evaluation validators.

Validation checkpoint:

Reproducible commands (no live providers or empirical fitting):

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_optimization.py tests/unit/forecasting/test_forecaster_lifecycle.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_seams.py tests/acceptance/ff0 tests/unit/forecasting/test_contracts.py tests/unit/forecasting/test_pinned_runtime_replay.py tests/unit/forecasting/test_identity_isolation.py tests/unit/forecasting/test_logistic_training.py tests/unit/forecasting/test_logistic_forecasts.py --tb=short
.venv/bin/pytest -q --tb=short
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
git diff --check
```

- FLC-3 + existing FLC-2: **115 passed in 63.64s** (60 + 55).
- FLC-1 / FF-0 / FF-1 compatibility: **251 passed in 190.20s**.
- Full repository suite: **3,587 passed in 948.74s (15:48)**.
- Compileall (`src scripts`), Ruff (`src tests scripts`), mypy
  (`src tests`; 662 source files) and `git diff --check`: PASS.
- Documentation: **717 local links / 26 anchors across 11 files**, fences: PASS.
- Four FF-1 protocol/execution/evaluation/ledger fingerprints: MATCH.
- All 78 frozen source/implementation pins: MATCH.

## Files, deferrals and handoff

Python paths in this paragraph are relative to `src/tiaf/`.
Created: `learning/optimization.py`, `learning/optimization_contracts.py`,
`learning/synthetic_trials.py`, `learning/synthetic_trial_worker.py`,
`learning/forecaster_trial_service.py`, `evaluation/optimization_evaluation.py`,
the targeted test module and this report. Modified existing FLC-2
`forecaster_reference.py` and `forecaster_custody.py` only for additive dispatch
and codecs. Active navigation/status pages and the FLC plan checkpoint are
synchronized; historical FLC-0 gap classifications and accepted reports remain.

The new test is `tests/unit/forecasting/test_optimization.py`. Modified navigation
files are `README.md`, `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_ROADMAP.md`,
`docs/MILESTONES.md`, `docs/TIAF_IMPLEMENTATION_TARGETS.md`,
`docs/TRADINGINTELLIGENCE_ROADMAP.md`, `docs/TIAF_A7_DETAILED_ROADMAP.md`,
`docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md`,
`docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md` and
`docs/TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md`.
Total: 20 changed/added files (8 source, 1 test, 11 documentation).

Not implemented: model-specific diagnostics/studies (FLC-4), calibration
readiness/application (FLC-5/FF-2), general empirical tuning, distributed AutoML,
new families, public forecasting, promotion, activation, A6 influence or A8.
No provider/network/broker calls; no empirical fitting; no commit/tag/push.

No outstanding acceptance blockers. Suggested commit:
`feat(a7.flc3): add bounded development-only optimization`. **No tag yet.**

Exact next task: **TIAF A7 / FLC-4 — MODEL-SPECIFIC DIAGNOSTICS NORMALIZATION**.
The task brief recommends **GPT-5.6 Sol — High** for that separate bounded
diagnostics/interpretability pass; this is a handoff preference, not an assertion
of model availability or a model switch.
