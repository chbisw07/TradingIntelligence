# TIAF A7 / FF-1.4 — Development-only paired BaseRate vs Logistic evaluation

## Authority and scope

2026-09-21, Asia/Kolkata. **FF1_4_ACCEPTED**: execution, reconstruction and final
regression gates passed. Scientific classification: **INSUFFICIENT_EVIDENCE**.
Entry tree was clean at `bd0d3c8` (`feat(a7.ff1.3): generate logistic walk-forward
forecasts`). A6 and FF-0 baselines remain frozen. No commit, tag or push is
authorized. Package version remains 0.1.0; additive research envelopes remain
schema 2.0, distinct from unchanged public/FF-0 schema 1.0.

The preceding FF-1.4 attempt stopped before implementation or empirical outcomes:
the [accepted plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md#12-paired-statistical-comparison-and-scientific-decision)
requires final-holdout evidence for final support, while that request prohibited
opening it. The revised development-only request explicitly resolves that gap:

| Condition | Classification |
|---|---|
| Adequately supported development evidence fails a preregistered stability criterion | `LOGISTIC_NOT_SUPPORTED` |
| Development gates pass but final holdout remains unexamined | `INSUFFICIENT_EVIDENCE` |
| Support/coverage/interval evidence is inadequate | `INSUFFICIENT_EVIDENCE` |
| Merely inconclusive development interval, without a rejection criterion | Never sufficient by itself for rejection |
| Final support | Not permitted in this pass |

The output type cannot represent `LOGISTIC_SUPPORTED`. Always retain
`FINAL_HOLDOUT_EVIDENCE = NOT_RUN` and `PROTECTED_HOLDOUT_STATUS = SEALED`.
Development intervals never substitute for final-holdout intervals. This is
research evidence generation, not promotion or a trading decision.

## Fixed inputs and policy

Subject: `RELIANCE:NSE:NSE_EQUITY:EQUITY`; target
`equity.next_session_close.return_gt_zero/1.0` (the prompt's `@1.0` notation
denotes the same target/version). Price basis CORPORATE_ACTION_ADJUSTED, mode
SIMULATED_RESEARCH; fresh historical download, not CAPTURED_AS_KNOWN.
Rights remain UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING under the accepted
research qualification. No new rights or production authorization.

The immutable Logistic [FF-1.3 corpus](TIAF_A7_FF1_3_LOGISTIC_WALK_FORWARD_FORECAST_GENERATION.md)
is consumed unchanged:

| Input | Fingerprint |
|---|---|
| Logistic run | `4dc2adb6f2bb9977bf3a06c2c5903065223cfc6e2c6a58898c0cb65090197812` |
| Qualification bytes | `69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca` |
| Qualification semantic identity | `4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51` |
| Approved dependency lock | `54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86` |
| Development evaluation policy | `1b725727e3400feb0f79cfc80b6239e62939b0f73f8ec53a6e1ac5fa4d7eb11e` |

The policy artifact is persisted and its fingerprint printed **before** loading
development outcomes. The input manifest pins the original plan document, the
revised clarification document, implementation source hashes, policy, exact
truth index and both forecast arms. No scientific setting is selected from the
results. Exact versions remain Python 3.12.3, sklearn 1.7.2, NumPy 2.3.3,
SciPy 1.16.2, joblib 1.5.2, threadpoolctl 3.6.0; no dependency changes/installations.

## Truth, BaseRate and exact pairing

```text
Pinned qualified external labels (Evaluation-owned)
  -> hard date guard BEFORE decoding label/state/availability
  -> immutable research Outcome Journal revisions
       |                                  |
       v                                  v
last 20 scheduled transitions       common per-origin truth
before each fold fit cutoff                |
  -> frozen BaseRate ----------------------+---- paired Evaluation
immutable FF-1.3 Logistic -> replay MATCH --+

2025 origins and 2024->2025 target: NO label decoding; NO pair; NO score
```

The accepted qualification already contains independently resolved labels. The
v2 journal **copies** those exact qualified labels, clocks, input/profile/source
fingerprints and exclusion reasons. It does not compare prices, rederive a
label, fetch a provider or route empirical data through synthetic-only FF-0
Journal types. Journal fingerprints are independent of forecast/model identities.
Only required pre-development BaseRate support and non-protected 2021–2024 truth
are decoded. Raw CSV prices, protected labels and fold class summaries are not
loaded. Source bytes are hashed/scanned opaquely before field-level decoding.
Synthetic sentinel tests fail if protected label/state/availability fields or
protected fold summaries are decoded.

BaseRate research binding is `forecaster:historical-base-rate/2.0`, BENCHMARK.
It reuses unchanged BaseRatePolicy/1.0: **last 20 scheduled transitions**, no
backfill, minimum 20 eligible, unsmoothed `k/n`. Qualified scheduled support IDs
are checked against the last cutoff-safe journal transitions. A bad/missing
label in that window causes unavailability, not selection of an older valid row.
One artifact per fold is frozen at the same historical fit cutoff as Logistic;
there is no test-year rolling update. Fixtures prove arithmetic parity to v1,
including zero and one probabilities. The 2.0 identity denotes research input
and lineage support, not a different estimator.

Logistic remains `forecaster:logistic-regression/1.0`, EXPERIMENTAL CHALLENGER.
No refit, scaler update, recalibration or parameter change. Its original run,
models, scalers, requests and captures are verified and copied byte-canonically
into the evaluation closure; the original corpus is never modified.

Pairing checks subject, target/version, reference/target sessions, cutoff/as-of,
price basis, input/profile/dataset/qualification identity and exact truth revision.
Both forecast probabilities must be present. Identity mismatches fail; ordinary
component absences produce explicit exclusions. There is one common truth per
pair, not arm-specific labels. Population identity excludes audit clocks and
model losses; comparison/report identity separately retains all audit lineage.

Every requested origin has four arm×metric dispositions. Precedence is scope,
identity/action, forecast absence, truth absence, then inclusion. All facets
are retained; primary reasons are disjoint. Protected slots remain in the
intended grid with an unpaired mask and unevaluated truth/metric checks. They
are **not** rows in the paired observation table and are not missing/zero labels.

## Numerical and statistical conventions

No rounding before computation; raw probabilities and per-observation values
remain binary64 canonical JSON. Aggregates use `math.fsum`; bootstrap arrays,
sums and quantiles use the approved NumPy float64 implementation.

```text
Brier(p,y) = (p-y)^2
q = min(1-1e-15, max(1e-15,p))                 # metric-only clipping
LogLoss(p,y) = -ln(q) if y=1 else -ln(1-q)     # natural-log nats
d = Logistic loss - BaseRate loss
```

Raw forecasts are not clipped or overwritten. Endpoint/clipped counts are
reported. Negative differences mean lower Logistic loss, not trading utility or
an automatic winner. Accuracy uses fixed `p >= 0.5`, ties positive; confusion
counts and mean probability are descriptive. Fixed-0.5 losses are a diagnostic
on the exact same pairs, not a replacement benchmark/new trained candidate.

Reliability uses ten fixed equal-width bins `[0,.1), ... [.9,1]`, with count,
mean probability and observed frequency. Bins below 20 observations are
LOW_SUPPORT. No calibrator is fitted; no calibrated-qualified coverage or
validity is claimed. Regime controls and A2/A4/A5/A6 non-probability comparisons
are NOT_EVALUABLE here, not invented probabilities.

Bootstrap: moving blocks of **five scheduled reference sessions**, **5,000
replicates**, `Generator(PCG64(1729))`. Full chronological grids retain missing
pair slots; blocks are overlapping/non-circular and never cross fold boundaries.
Uniform starts are `0..T-5`; concatenate then truncate to T slots, apply the
paired mask, average remaining losses. Both losses use the same indices.
Each summary starts a fresh seeded generator; pooled development processes
folds independently in fixed ascending order, then pools retained losses.
The sampler version, ordering, mask through dispositions, index digest and
all settings are persisted. Zero-pair replicates make intervals NOT_ESTIMABLE;
there is no redraw or seed retry.

Intervals are **97.5% two-sided percentile**, quantiles **0.0125 / 0.9875**,
linear interpolation. The two primary intervals implement the nominal Bonferroni
95% familywise policy, conditional on the dependence approximation. No IID
standard errors or assertion that replicates are independent observations.

Support gates: each fold ≥150 pairs, ≥30 per class, ≥80% intended-grid coverage
and ≥20 complete nonoverlapping five-session paired blocks counted from the
original first grid slot; pooled ≥600 pairs. These are support guards, not a
power calculation or proof of independence.

Exactly three preregistered development stability requirements:

1. Negative mean Brier difference in at least three of four folds.
2. No fold's mean Brier worsening greater than 0.02.
3. No fold's mean log-loss worsening greater than 0.05 nats.

An interval crossing zero is **not** an additional rejection criterion. With
adequate support, any of the three failures gives LOGISTIC_NOT_SUPPORTED.
Otherwise final evidence remains NOT_RUN and classification is
INSUFFICIENT_EVIDENCE. Inadequate support also gives INSUFFICIENT_EVIDENCE, never
a favorable fabricated zero or a scientific rejection caused by an exception.

## Storage, engineering command and reconstruction

```bash
.venv/bin/python scripts/evaluate_ff1_baserate_vs_logistic.py \
  --output data/ff1/development_evaluation_20260921
```

An explicitly registered Evaluation-owned extension reuses the research Capture
Store's canonical JSON, type validation, semantic seals, exclusive writes,
read-only reopening, 1 MiB record, 65,536 artifact and 2 GiB corpus bounds. The
FF-1.3 default record types and FF-0 v1 behavior remain unchanged. Paired rows and
dispositions use immutable ≤64-row shards. The manifest precedes derived scores;
the final Ledger references both and avoids circular hashes. No mutable alias,
database, second Ground Truth resolver or cross-file transaction promise. A
partial directory without a verified Ledger is not acceptance.

The private corpus includes original Logistic closure, independent truth rows
and index, four BaseRate support artifacts, per-origin BaseRate forecasts,
preregistered policy, comparison input manifest, paired row records, population
disposition shards, evaluation report and final Ledger. No protected outcome row.
There are 4,011 JSON artifacts: 1,010 truth rows, 991 Logistic captures,
990 BaseRate forecasts, 969 pairs, 16 evaluation shards, 16 Logistic shards,
four each of baseline/model/scaler artifacts, and seven singleton records
(policy, truth index, manifest, ledger, run, evaluation, training).

Offline reconstruction verifies Logistic at its accepted 1e-12 tolerance,
reconstructs BaseRate from captured scheduled support, relinks exact common
truth, rebuilds pair losses, populations, all summaries, sampler index digests,
bootstrap means/intervals and the complete report fingerprint. No source CSV,
original qualification or provider is needed. Full bootstrap recomputation
requires the pinned NumPy implementation, not sklearn fitting. Recorded numeric
values are never rounded or silently repaired. CLI exit 0 is completed/MATCH,
1 HOLD/MISMATCH, 2 invalid command. No automatic rerun or retry.

## Measured results and validation

Evaluation captured at **2026-09-21T22:25:13.307573+05:30**; command exited 0
after 115.37 seconds including full reconstruction. Scientific classification:
**INSUFFICIENT_EVIDENCE**. All development gates passed; final evidence is
**NOT_RUN**, protected holdout **SEALED**. This is not final support or promotion.
No empirical result was inspected while setting metrics, bootstrap, thresholds,
folds or exclusions. No runtime code changed after inspecting these results.

| Artifact | Semantic fingerprint |
|---|---|
| Paired population | `f8ac38d7afdffab2b3be21a467dfa913df77b02adbdaa4f04eb1c5d89b847830` |
| Ground Truth Journal | `5784f7b82cae781339a7b9d3afe689f905a6af318ff50baa095f1017653a89e1` |
| Evaluation | `5f6d4342c61017fecda2196715d707a356ff8728eb0ec1f6996c362723ba19e1` |
| Final Ledger | `62bc746d90386f3b718bf6fe106f4a80832bfa8206ea3605ec96bbb2e5817246` |

### Population and coverage

| Fold | Intended | Logistic | BaseRate | Valid truth | Paired N | Positive / zero | Prevalence | Paired coverage | Complete blocks |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 2021 | 248 | 248 | 248 | 248 | 248 | 137 / 111 | .55241935 | 1.00000000 | 49 |
| 2022 | 248 | 248 | 248 | 248 | 248 | 127 / 121 | .51209677 | 1.00000000 | 49 |
| 2023 | 246 | 225 | 246 | 245 | 225 | 115 / 110 | .51111111 | .91463415 | 44 |
| 2024 | 249 | 248 | 248 | 248 | 248 | 125 / 123 | .50403226 | .99598394 | 49 |
| Pooled | 991 | 969 | 990 | 989 | 969 | 504 / 465 | .52012384 | .97780020 | 191 |

Forecast union: 990; intersection: 969. Exactly **22 unpaired slots**:
20 FEATURE_ACTION_DEMERGER, one LABEL_UNSUPPORTED_ACTION and one
TARGET_HOLDOUT_SEALED. Overlapping facets retain 21 LOGISTIC_ABSENT and one
GROUND_TRUTH_UNAVAILABLE; BaseRate insufficient-support count is zero.
The protected slot's truth is **not checked**: scope exclusion is not a missing
label claim. No protected row appears in the paired table.

### Point estimates (display rounded; artifacts retain full precision)

| Fold | BaseRate Brier | Logistic Brier | Difference | BaseRate log loss | Logistic log loss | Difference |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | .2495161290 | .2479573818 | -.0015587473 | .6923039584 | .6890502526 | -.0032537058 |
| 2022 | .2500000000 | .2529200387 | +.0029200387 | .6931471806 | .6990428854 | +.0058957049 |
| 2023 | .2758333333 | .2491409486 | -.0266923847 | .7471807337 | .6914245854 | -.0557561484 |
| 2024 | .3104838710 | .2523961632 | -.0580877078 | .8325583285 | .6979565263 | -.1346018022 |
| Pooled | .2713544892 | .2506383511 | -.0207161381 | .7411579082 | .6944384401 | -.0467194681 |

| Fold | Frozen BaseRate k/n = p | Mean Logistic p | BaseRate accuracy | Logistic accuracy | Opposite sides of .5 | Mean absolute p gap |
|---|---|---:|---:|---:|---:|---:|
| 2021 | 12/20 = .60 | .52243066 | .55241935 | .54838710 | 25 | .07756934 |
| 2022 | 10/20 = .50 | .52874235 | .51209677 | .48790323 | 12 | .03149815 |
| 2023 | 7/20 = .35 | .52670583 | .48888889 | .51111111 | 225 | .17670583 |
| 2024 | 15/20 = .75 | .52194935 | .50403226 | .51209677 | 18 | .22805065 |
| Pooled | mean .55474716 | .52491554 | .51496388 | .51496388 | 280 | .12731074 |

Pooled confusion counts (TP, FP, TN, FN): BaseRate (389,355,110,115),
Logistic (474,440,25,30). Every endpoint/clipped count is zero.
Fixed-.5 descriptive diagnostic on these same 969 pairs: Brier .25,
log loss .6931471806, accuracy .52012384. **Logistic's pooled losses are
slightly worse than that fixed-.5 diagnostic**, despite being lower than the
accepted frozen BaseRate benchmark. This is a limitation, not a newly introduced
decision rule, benchmark replacement or invitation to tune.

### Development-only intervals

Every row uses the effective N above, five-session blocks, 5,000 replicates,
PCG64 seed 1729 and the fixed 97.5% two-sided percentile interval. All intervals
are ESTIMATED; zero-pair replicate counts are zero.

| Fold | Brier bootstrap mean | Brier difference interval | Log-loss bootstrap mean | Log-loss difference interval |
|---|---:|---|---:|---|
| 2021 | -.0015920033 | [-.0128476527, .0091879571] | -.0033218706 | [-.0262343532, .0185847147] |
| 2022 | .0032514061 | [-.0022143363, .0087479202] | .0065598974 | [-.0044309947, .0176244905] |
| 2023 | -.0274674952 | [-.0553358971, .0014977870] | -.0573484807 | [-.1145985688, .0021733320] |
| 2024 | -.0592630673 | [-.0879554826, -.0309912850] | -.1372106394 | [-.2006561051, -.0748603845] |
| Pooled | -.0211143932 | [-.0317257715, -.0103566515] | -.0476036445 | [-.0702934563, -.0244489871] |

These are not final-holdout intervals. Negative pooled development intervals
do not authorize support. Individual intervals crossing zero do not trigger
an unregistered rejection rule.

### Reliability and disagreement diagnostics

Nonempty pooled bins (all other bins are empty/LOW_SUPPORT):

| Arm | Bin | Count | Mean probability | Observed frequency | Support |
|---|---|---:|---:|---:|---|
| BaseRate | [.3,.4) | 225 | .35000000 | .51111111 | adequate |
| BaseRate | [.5,.6) | 248 | .50000000 | .51209677 | adequate |
| BaseRate | [.6,.7) | 248 | .60000000 | .55241935 | adequate |
| BaseRate | [.7,.8) | 248 | .75000000 | .50403226 | adequate |
| Logistic | [.3,.4) | 1 | .36128362 | 1.00000000 | LOW_SUPPORT |
| Logistic | [.4,.5) | 54 | .48370382 | .53703704 | adequate |
| Logistic | [.5,.6) | 914 | .52752939 | .51859956 | adequate |

The one-observation bin supports no calibration conclusion. Per-fold reports
also retain low-support bins (2022 counts 1 and 11; 2024 count 18). No calibrator,
calibrated-qualified claim or ECE estimate was introduced.
Largest five pooled probability gaps (reference session, absolute difference):
2024-06-04 .32008558; 2024-10-03 .27892545; 2024-08-30 .26799954;
2024-11-04 .26793380; 2024-08-05 .26610011. Full row lineage remains in the report.

### Applied gates and reconstructability

All support/coverage/complete-block/interval gates pass. Three folds have
negative mean Brier difference (2021, 2023, 2024), satisfying the required three.
Maximum positive fold worsening is .00292004 Brier (<.02) and .00589570 nats
log loss (<.05), both in 2022. Support failures: none; stability failures: none.
Therefore development-pass + unexamined final holdout gives
**INSUFFICIENT_EVIDENCE**, not rejection and not final support.

```bash
.venv/bin/python scripts/evaluate_ff1_baserate_vs_logistic.py \
  --corpus data/ff1/development_evaluation_20260921 \
  --verify-ledger 62bc746d90386f3b718bf6fe106f4a80832bfa8206ea3605ec96bbb2e5817246
```

The generation command's full reconstruction returned **MATCH**. A separate
fresh-process guarded replay also returned **MATCH** with socket creation,
sklearn/SciPy/joblib imports and original qualification/CSV/Logistic corpus reads
blocked. It used only the captured closure and required numerical implementation;
all **4,011 artifact byte hashes were unchanged** before versus after replay.
Initial targeted synthetic suite: **32 passed in 187.46s**. Final source
additionally hardens identity/capture-clock checks; full and focused suites run
against that source. Sentinel tests guard protected labels, clocks and class
summaries; classification's Literal type excludes final support. No fitting,
provider, broker or network acquisition exists in the evaluation command.

### Files and validation record

New implementation: `forecast_research_truth.py`, `forecast_comparison.py`,
`forecast_comparison_metrics.py`, `forecast_comparison_store.py` under
`src/tiaf/evaluation/`; `src/tiaf/forecasting/research_baserate.py`;
`scripts/evaluate_ff1_baserate_vs_logistic.py`;
`tests/unit/evaluation/test_development_comparison.py`; this report.
Existing `src/tiaf/forecasting/logistic_store.py` changes only record-type dispatch
to an immutable explicit class mapping, allowing the Evaluation-owned extension
without changing default FF-1.3 schemas or arithmetic. Navigation updates:
`README.md`, `scripts/README.md`, `docs/MILESTONES.md`,
`docs/IMPLEMENTATION_ROADMAP.md`. Private corpus is Git-ignored.

| Validation | Result |
|---|---|
| Initial FF-1.4 targeted tests | 32 passed in 187.46s |
| Final-source forecasting/evaluation + FF-0 acceptance regressions | 851 passed in 575.05s; includes all 32 FF-1.4 tests, FF-1.1/1.1A, FF-1.2, FF-1.3 and FF-0 |
| Full repository suite | 3,327 passed in 809.23s |
| Existing script-documentation/smoke checks after navigation edits | 10 passed in 0.28s |
| `python -m compileall -q src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS, 635 source files |
| `pip check` | PASS, no broken requirements; harmless read-only cache warning |
| `uv lock --check --offline` | PASS, 76 packages; temporary writable cache, no install/network |
| CLI `--help` | PASS |
| Local Markdown links / balanced code fences | PASS, 275 local targets in five changed documents |
| New-file whitespace / final newline; `git diff --check` | PASS |
| Captured implementation/protocol hashes versus final source | MATCH; no post-result runtime edits |

Commands used `.venv/bin/` executables. Final-source focused command:
`pytest -q tests/unit/forecasting tests/unit/evaluation tests/acceptance/ff0`;
full command: `pytest -q`. No skipped empirical holdout was presented as a test
pass. No provider/broker/network operation or optional ML fit was used.
Qualification byte hash and training lock hash still match the input table;
raw CSV byte hash remains
`d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6`.
Source hash verification treats protected source bytes opaquely; no protected
labels or class summaries are decoded. Source and dependency files are unchanged
in Git. HEAD remains `bd0d3c80021b233cb2692bc014626b2a143a1cd8`;
A6 peeled baseline `6dc2ff304aae0e87540260b092919bb91e4d4189` and FF-0
`e5283c9eaa4294bd236186d663335efdf7dab236` are unchanged.

## Limitations and next gate

One equity, one retrospective adjusted-data vintage, four development folds;
not a production/PIT study and not a test of tradable net returns. Rights remain
unverified but admitted with warning for this bounded research profile. BaseRate
uses a short frozen window while Logistic uses expanding history. Dependence and
stationarity approximations limit interval interpretation; no new regime model
or subgroup search is introduced. All intervals are development evidence only.

No protected outcome access, calibration, tuning, threshold optimization,
promotion, PRIMARY assignment, benchmark removal, public forecast activation,
provider/broker/network call, execution or A8 work. No commit/tag/push.
Engineering acceptance blockers: **none**. The deliberately unexamined final
holdout is a limitation on scientific support, not a failed implementation gate.

If accepted, recommended commit only:
`feat(a7.ff1.4): add development-only paired BaseRate vs Logistic evaluation`.
No tag yet. Exact next prompt given this measured classification:
**TIAF A7 / FF-1 — INDEPENDENT SCIENTIFIC ACCEPTANCE AND FINAL-HOLDOUT DECISION DESIGN**.
Recommended model for that separately requested review: GPT-6 Astra, Extra High.
That next pass is not authorized here, and its title does not authorize opening
the holdout.
