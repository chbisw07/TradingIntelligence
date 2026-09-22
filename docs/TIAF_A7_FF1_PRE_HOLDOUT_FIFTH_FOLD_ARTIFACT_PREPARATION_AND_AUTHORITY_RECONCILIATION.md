# FF-1 — Pre-holdout fifth-fold artifact preparation and authority reconciliation

## Status and scope

2026-09-22, Asia/Kolkata. The single empirical preparation completed at
**2026-09-22T00:35:32.278719+05:30**, before the interrupted session was resumed.
It was **not repeated** on resumption. All preparation and regression gates pass.

```text
FIFTH_FOLD_PREPARATION_COMPLETE
PRE_HOLDOUT_FIFTH_FOLD_FIT_AUTHORIZED = YES
POST_HOLDOUT_REFIT_ALLOWED = NO
PROTECTED_HOLDOUT_STATUS = SEALED
FIFTH_FOLD_HANDOFF_READY = YES
FINAL_HOLDOUT_EVALUATION_AUTHORIZED = NO
FINAL_DECISION_PROTOCOL_FROZEN = NO
```

The [prior independent review](TIAF_A7_FF1_INDEPENDENT_SCIENTIFIC_ACCEPTANCE_AND_FINAL_HOLDOUT_DECISION_DESIGN.md)
HOLDed because the accepted handoff contained only four development-fold fits.
That report is preserved **unchanged**. This pass supplies the missing original
fifth fold, not a different model or a response to protected performance.
Entry tree was clean at `2bad695` (`docs(a7.ff1): review final-holdout readiness
and identify fifth-fold blocker`). FF-1.4 and its development classification
remain accepted; no final scientific classification is produced here.

The explicit authority is one fifth-fold scaler fit, one Logistic fit and one
BaseRate state freeze at **2024-12-31T09:15:00+05:30**. The entire preceding
scheduled session is embargoed, and both target resolution and assumed label
availability must be strictly before that cutoff. This is the original
[five-fold plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md#9-chronological-protocol-and-protected-holdout),
not post-holdout refitting. The historical cutoff and actual 2026 fitting clock
are separate; no backdated operational claim is made.

## Authority and implementation boundary

`FifthFoldGrant` is separate from the unchanged four-fold `TrainingGrant`.
It allows only `(2025,)`, one attempt, one model/scaler fit, SEALED holdout,
no protected outcome access, no final evaluation and no post-open refit.
The shared manifest can now represent fold 2025 **only with that separate
grant and exact cutoff**. Existing four-fold `TrainingRun`, development jobs,
public forecast scope and FF-0 semantics remain unchanged.

The existing isolated training worker, configuration and numerical reconstruction
are reused. No alternative estimator/client, solver retry, new feature, new
qualification policy, imputer, calibrator, threshold search or promotion path.
The old `run_fit` explicitly rejects the fifth-fold grant; the separately
admitted path records an attempt before invoking the shared worker.

The CLI uses one fixed private corpus location. Exclusive directory creation
prevents a second campaign; an exclusive, fsynced attempt record consumes the
attempt **before** worker invocation. Failure leaves a consumed attempt, never
an automatic retry. Relocated corpora are replay-only. This is a bounded trusted
local custody mechanism, not protection against an administrator deleting files
or invoking private Python internals. Such bypass would require new authority;
it is not a supported workflow. The future holdout-opening control is not
implemented or authorized by this preparation grant.

## Input and membership audit

Subject `RELIANCE:NSE:NSE_EQUITY:EQUITY`; target
`equity.next_session_close.return_gt_zero/1.0`; CORPORATE_ACTION_ADJUSTED;
SIMULATED_RESEARCH. The original fresh-download research profile and
UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING rights status remain unchanged.
This is not ACTUAL or CAPTURED_AS_KNOWN evidence, production permission or a new
source-rights determination.

| Population item | Count / range |
|---|---|
| Whole qualified reference inventory | 1,983 |
| Pre-2025 reference candidates, before protection/purge/eligibility | 1,734 |
| Candidates after protected-origin/target guard | 1,733 |
| Scheduled transitions strictly before fit cutoff | 1,732 |
| Admitted TRAIN | **1,690** |
| Training positive / zero | **878 / 812** |
| Ineligible pre-cutoff rows | 42 |
| Disjoint non-protected purge-only bucket | 1 |
| Disjoint embargo bucket | 0; embargo origin is in the sealed bucket |
| Disjoint sealed/protected bucket | 250 = 249 protected-year references + one prior-year protected target |
| Later unsealed bucket | 0 |
| Final training reference range | **2018-01-01 through 2024-12-27** |

The disjoint reconciliation is `1690 + 42 + 1 + 250 = 1983`.
There are **two boundary-purged origins**, 2024-12-30 and 2024-12-31. The latter
is the whole-session embargo origin **and** targets 2025. It is counted once in
the sealed bucket while both roles are retained through `purged_ids` and
`protected_purge_ids`. Zero in the disjoint embargo bucket does not mean the
embargo was removed. No row or exclusion policy was changed to adjust counts.
Exact admitted IDs and positive/zero TRAIN counts match the accepted fifth-fold
qualification. These counts are **not 2025 evaluation class counts**.

The reader first verifies the entire qualification byte pin, then parses
structural JSON spans. Reference/target dates guard protected rows **before**
decoding labels, label state, availability or features. Only TRAIN fold metadata
and cutoff-safe records are decoded; protected test summaries stay opaque.
No raw price CSV is parsed, no feature is recalculated and no label is rederived.
The captured preparation contains admitted training rows and baseline support,
not protected feature or outcome rows.

## Scaler and model

Feature schema: `ff1.reliance.a2_daily_five/1.0`, exact order below. Scaler is
train-only StandardScaler, mean/std enabled, population variance `ddof=0`,
1,690 rows and no constant columns. Values shown below retain enough precision
for inspection; canonical artifacts are authoritative.

| Feature | Mean | Scale (standard deviation) |
|---|---:|---:|
| ret_1 | .0006411636852931555 | .0181301061001096 |
| ret_5 | .003004301047120278 | .040266299124749105 |
| sma20_distance | .6140093577728013 | 4.512104256785325 |
| realized_vol_20 | 25.605757195785618 | 12.73355553864465 |
| relative_volume | 1.0320214929067588 | .5413742877990029 |

Exactly one empirical Logistic fit: L2, C=1, lbfgs, tol=1e-8, max_iter=1000,
intercept enabled, no class weights, dual=False, warm_start=False, random_state
1729, n_jobs=1. **Converged, n_iter=11**. Standardized-feature coefficients:

```text
(0.03130655827036798, -0.02448138507824083, 0.029090095538386835,
 0.006161188402226738, -0.011702388854382205)
intercept = 0.07817261404850911
```

Worker started 2026-09-22T00:35:30.377393+05:30; completed
2026-09-22T00:35:32.196118+05:30. Fit-job elapsed 1.818724 seconds; CPU .636744
seconds; peak lifetime RSS 172,576 KiB; enforced address space 536,870,912 bytes,
CPU 60 seconds, wall timeout 60 seconds. Whole preparation/replay command elapsed
8.198884 seconds. One numeric thread; monetary cost UNPRICED, not asserted free.
Python 3.12.3, sklearn 1.7.2, NumPy 2.3.3, SciPy 1.16.2, joblib 1.5.2,
threadpoolctl 3.6.0. No dependency installation or upgrade.

## BaseRate and reconstruction

BaseRate retains unchanged BaseRatePolicy/1.0: **last 20 scheduled transitions**,
minimum 20 eligible labels, unsmoothed `k/n`, **no invalid-transition backfill**.
All support targets and assumed availability precede the same frozen cutoff.
Support reference range **2024-11-29 through 2024-12-27**; `k=8`, `n=20`,
state probability **0.4**. This is pre-cutoff state, not a scored 2025 forecast.
No rolling test-year update or smoothed/full-window substitute.

The worker checked five algebraic vectors based only on the TRAIN scaler
(mean, ±1 scale, ±1,000,000 scales). Frozen standardization/logit/sigmoid matched
sklearn at the existing absolute 1e-12 policy; maximum error **0.0**. Captured
engineering probabilities replay exactly. They are not market forecasts.

Offline verification validates every canonical seal and authority/manifest/job
link, reconstructs TRAIN means/variances without fitting (scale-aware 1e-12
engineering tolerance), rechecks persisted scales under the original scaler
policy, reproduces the five probe probabilities, and rechecks BaseRate support,
last-20 membership, arithmetic and cutoff. It reads only eight captured blobs.
A separate guarded process blocked NumPy/sklearn/SciPy/joblib/threadpoolctl,
worker invocation, network sockets and every other `data/ff1` source path:
**MATCH**, zero attempted source reads, all eight byte hashes unchanged.

## Immutable handoff and pins

Private, Git-ignored corpus: `data/ff1/preholdout_fifth_fold_20260922/`.
Eight canonical JSON blobs, **827,981 bytes** total: authority, preparation,
baseline, attempt, job, model, scaler, handoff. Per-record 1 MiB bounds are
unchanged. The handoff is written last; a partial corpus is not completion.

| Identity | Fingerprint |
|---|---|
| Qualification semantic | `4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51` |
| Qualification bytes | `69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca` |
| Dataset bytes | `d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6` |
| Research profile | `1e616cc7a2f3654d856b916e790d054a6c1ff7f10efe2b316cf0a44835011c45` |
| Feature schema | `76e63292685ee0b3b41f7ab033407e6bd014fc802d2092a2ed227888bdc71676` |
| Training population / ordered IDs | `7a448191a66a40d56dda54575c39ea9b586468b5ba17e0b65b948abb99203da0` |
| Training values | `291d587488c46f066805851db9259281e030b7549e4ed63a0a641cd840748fd1` |
| Scaler | `00e0ceaa160a7df2e518aafb4a8b1c2f86c55837eeeda94f131b002fae20afe8` |
| Model | `c287d9333fbf6067dd16fe5ab51bb1e6a7c6168df6289b9e73669aa2a15f6381` |
| BaseRate state | `6a89a25e67d1a2e6d538b3754e61f7da932f4c8b5b6b72fbb2346a7040bf7e8e` |
| Dependency lock | `54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86` |
| Authority | `31b54fdc10f6639c940e524f21ed10a343305c998b99d9f5815d710398c2c2ba` |
| Preparation | `c63a572f1d8b522f7f19758183a77920ed713e2d31240640d5eaeea13c190006` |
| Consumed attempt | `f1d46e38530d4e3f14137a90c5e89080c4d04b618e22d55687b731597aa5c0d7` |
| Fit job | `9b2e7803ed0e0fabfbd7ab41bb2843b6f10ceee302eb6bef706111c233c47956` |
| Handoff | **`c40148f60e985c83fe8bca027a3722583ed8c1999ecfc86e4959c4fe6166ce54`** |

The authority additionally pins accepted plan bytes
`e5d09db101c1c6b7c3754ccda1a5bc2b9dd0f84f3219da2f8297bd88192c8c66`,
this request's authority-document bytes
`d8acaf8d9f1d7715c2521e4539cf7cf47119df6c5c257b6d0b88b6de9bc2491a`,
and preparation implementation identity
`434cd6747439c63cc513bae34b622a540c8c73b8a57df2a5c169e9719e400cc3`.
Issued at 2026-09-22T00:35:24.369795+05:30. These are preparation authority and
handoff hashes, **not** a frozen final decision protocol or opening grant.

## Commands and stop boundary

Command actually run once; **do not rerun preparation**:

```bash
.venv/bin/python scripts/prepare_ff1_fifth_fold_artifacts.py --prepare \
  --approve-dependency-lock 54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86
```

Safe default performs no operation. `--preflight` admits TRAIN only, without
fitting or writing. Replays are read-only and require neither optional ML
libraries nor original source files:

```bash
.venv/bin/python scripts/prepare_ff1_fifth_fold_artifacts.py \
  --verify-handoff c40148f60e985c83fe8bca027a3722583ed8c1999ecfc86e4959c4fe6166ce54
```

Optional `--corpus` relocates captured replay only; it cannot redirect a fit.
Exit 0 means safe/preflight success, preparation completion or replay MATCH as
appropriate; 1 means HOLD/MISMATCH; 2 invalid CLI. No auto-install/retry.

`forecast_generation = DEFERRED_TO_ONE_SHOT_EVALUATION`;
`forecast_records = 0`; `evaluation_metrics = 0`;
`protected_outcome_access = NONE`; `holdout_status = SEALED`;
`final_protocol_frozen = false`. No 2025 outcome/class balance, empirical quality
metric, confidence interval, calibration, provider/LLM/broker call or trade.
Regression tests retain their synthetic metrics/fits; those are not additional
empirical candidate fits or protected evaluation. No scientific outcome is
issued from this artifact-preparation pass.

## Tests, checks and files

Added 24 synthetic tests: narrow authority/cutoff/config refusal, old-grant
isolation, exact memberships, protected sentinels, late labels, no-backfill
BaseRate, consumed failed attempts, immutable/sealed handoff, replay without
ML/network, safe CLI default and preflight serialization. Pre-fit engineering
checks caught and fixed metadata fingerprint access, the protected/embargo
overlap accounting, CLI date serialization, and a provenance field name rejected
by secret hygiene. These were fixed **before the single empirical fit**; secret
filtering was not relaxed. No empirical retry or protected access resulted.

| Gate | Result |
|---|---|
| New targeted tests | 24 passed in 37.76s |
| Forecasting/evaluation + FF-0 acceptance | 875 passed in 587.63s |
| Full repository suite | 3,351 passed in 825.86s |
| Compileall `src scripts` | PASS |
| Ruff `src tests scripts` | PASS |
| mypy `src tests` | PASS, 638 source files |
| `pip check` | PASS; harmless read-only cache warning |
| `uv lock --check --offline` | PASS, 76 packages; temporary writable cache, no installs |
| Guarded handoff replay | MATCH; eight files unchanged |
| CLI help / captured code, plan, qualification and lock pins | PASS; prior scientific review byte-for-byte unchanged |
| Documentation links | PASS, 280 local link targets in the five changed documents |
| `git diff --check` / new-file whitespace | PASS |

Exact test commands (using the existing repository environment):

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_fifth_fold_preparation.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting tests/unit/evaluation tests/acceptance/ff0
.venv/bin/pytest -q
```

The focused suite includes FF-1.4, FF-1.3, FF-1.2, FF-1.1/1.1A and FF-0
regressions. No preparation blocker remains; final-holdout opening still requires
the separate protocol review and explicit authority.

New files: `src/tiaf/learning/forecast_fifth_preparation.py`,
`src/tiaf/learning/forecast_fifth_store.py`,
`scripts/prepare_ff1_fifth_fold_artifacts.py`,
`tests/unit/forecasting/test_fifth_fold_preparation.py`, this report.
Modified runtime files: `src/tiaf/learning/forecast_artifacts.py` (separate grant,
guarded manifest support), `src/tiaf/learning/forecast_jobs.py` (shared worker
invocation, distinct job types), `src/tiaf/forecasting/logistic_forecasts.py`
(type-only development-fold cast after existing handoff validation).
Navigation updates: README, scripts README, milestone ledger and implementation
roadmap. The original worker, model/scaler configuration, dependency locks,
accepted plan and prior scientific review remain unchanged.

## Next review

The missing-artifact blocker is addressed by this verified handoff and passing
regressions. It does **not** authorize final evaluation, promotion, PRIMARY,
public capability, A8, calibration or a change to any development result.

Exact next prompt:
**TIAF A7 / FF-1 — FINAL-HOLDOUT PROTOCOL FREEZE REVIEW (WITH FIFTH-FOLD HANDOFF)**.
Recommended model for that separately requested review: GPT-6 Astra, Extra High.
The reviewer must pin these identities and the one-shot decision protocol
before any protected outcomes are accessed.

Recommended commit only:
`feat(a7.ff1): prepare pre-holdout fifth-fold artifacts`.
No tag yet. No commit/tag/push was performed.
