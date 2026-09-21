# TIAF A7 / FF-1.3 — Logistic walk-forward forecast generation

## Scope and acceptance

2026-09-21, Asia/Kolkata. **FF1_3_ACCEPTED**. Empirical generation, replay and
all regression gates are complete. No acceptance blockers remain.

```text
FF1_2_FINAL_STATUS = ACCEPTED
LOGISTIC_WALK_FORWARD_FORECASTS_COMPLETE = YES
PROTECTED_HOLDOUT_STATUS = SEALED
```

Entry HEAD `f84fe56` contained the committed FF-1.2 implementation and a clean tree.
The current request explicitly approves its dependency stack and authorizes four
pending empirical fits followed by Logistic-only development forecasts. It does
not authorize the protected fifth fold, BaseRate generation or paired evaluation.

Package version remains **0.1.0**. New research envelopes use **schema 2.0**;
forecaster/model version is **1.0**. These are separate concepts. FF-0 v1
synthetic-only contracts, rights, limits and behavior are unchanged.

## Accepted FF-1.2 handoff and exact pins

[FF-1.2](TIAF_A7_FF1_2_LOGISTIC_CANDIDATE_TRAINING_ARTIFACT_IMPLEMENTATION.md)
is now empirically complete: four serial fits, all converged, 11/9/11/10 optimizer
iterations, each canonical reconstruction maximum error 0.0 against tolerance
1e-12. No fits occur in the FF-1.3 generation or replay paths.

| Pin | SHA-256 / semantic fingerprint |
|---|---|
| Dependency lock | `54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86` |
| Qualification | `4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51` |
| Qualification bytes | `69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca` |
| Dataset bytes | `d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6` |
| Research profile | `1e616cc7a2f3654d856b916e790d054a6c1ff7f10efe2b316cf0a44835011c45` |
| Feature schema/profile | `76e63292685ee0b3b41f7ab033407e6bd014fc802d2092a2ed227888bdc71676` |
| Training run | `f26605528584a68449396da9dea1a3e28d6e2295f355a7085887e5adedc94406` |

| Fold | Model artifact | Scaler artifact |
|---|---|---|
| 2021 | `2f33466e4790693475c2f51c58e14c056a0ba5a67fae2f9c6d9b6ff15bc405d7` | `59b088f1a0b48b4c35c9fe780f30ae2b085fb2f28e2338dacc4b1ce636a60abf` |
| 2022 | `7cbe4f2b14a72ae5e2af40c535710f1695687b81786f0c69efd271b50442a5d2` | `39e888ce1789405f4bdc9fa704e0f6ac43adfc5aaade55bc211d5c9f0986eb62` |
| 2023 | `d5059d0474b438e5df4baf6d30030ceb10ad65ffe1fc078b055829407718a258` | `4e19aef805e3877599352daa8602c8b7ed5d9d48fd7586f65c2e29b7c3f88a1e` |
| 2024 | `2df0651702e6eaa9c9509e1e010efdc40e889fbdc8eb265bbfff7e256f78d153` | `495722019eb686dd720a4ffc1cc67a862afc7f3d87213e97ea5a606acda7421c` |

Generation checks the installed versions through package metadata without
importing the estimators: Python 3.12.3, scikit-learn 1.7.2, NumPy 2.3.3,
SciPy 1.16.2, joblib 1.5.2, threadpoolctl 3.6.0. Missing/mismatched versions or
lock bytes mean HOLD; no installation, upgrade or alternate solver fallback.
The parent training seal is pinned in the command; every separate model/scaler
file must equal its immutable nested training artifact before generation.

## Outcome-blind boundary and clocks

```text
Approved qualification byte pin
  -> syntax-only span scan (outcome values remain opaque)
  -> allow-listed features / clocks / exclusion metadata
  -> correct fixed fold model + train-only scaler
  -> SIMULATED request -> raw probability or explicit absence
  -> immutable capture -> sharded parent run
  -> offline recorded reconstruction + pinned numeric verification

Ground Truth -------------------- NOT AN INPUT TO THIS PATH
2025 origins -------------------- OUTSIDE GENERATION SCOPE
2024 origin targeting 2025 ------ PROTECTED, no feature decoding/inference
```

The accepted qualification artifact includes truth, so generation **does not**
load it through the full qualification model or `json.loads` the whole document.
It hashes/scans source bytes for integrity and JSON boundaries, then decodes only
an explicit allow-list. Test label values, label-availability timestamps, audit
class summaries and fold outcome summaries are never decoded or used. The
synthetic sentinel test makes decoding them fail. Dates are checked before
feature decoding, including the final 2024 origin. Predetermined demerger and
holdout exclusion reasons are metadata, not observed outcome values.

Qualification remains the upstream admission authority; this is not a second
qualification or fresh A2 calculation. The raw CSV is not parsed. This boundary
requires the externally accepted qualification byte pin, not a self-asserted new
qualification fingerprint. Historical evidence is a fresh adjusted download,
**not CAPTURED_AS_KNOWN**. Rights remain UNVERIFIED / WARN_ONLY /
ADMITTED_WITH_WARNING. No production permission is created.

For each origin: reference close +30 minutes = information cutoff; cutoff
+5 minutes = simulation_as_of; simulation_as_of precedes target open. The fixed
model's fit cutoff precedes the forecast cutoff. `computed_at` is the real current
aware clock, not historical issuance. Result/request contracts have **no
`issued_at` field** and reject attempts to add it. All timestamps normalize to
`ZoneInfo("Asia/Kolkata")` and serialize with +05:30; naive clocks are rejected.

## Forecast meaning and lineage

Subject: `RELIANCE:NSE:NSE_EQUITY:EQUITY`. Target canonical ID:
`equity.next_session_close.return_gt_zero/1.0` (the brief's `@1.0` names the same
target/version). Probability means only
**P(next-session adjusted close > reference adjusted close)**.

Forecaster: `forecaster:logistic-regression`, version 1.0, EXPERIMENTAL
CHALLENGER. BaseRate remains BENCHMARK and is not changed. The five raw columns
remain `ret_1`, `ret_5`, `sma20_distance`, `realized_vol_20`, `relative_volume`,
schema `ff1.reliance.a2_daily_five/1.0`. Frozen training-fold means/scales feed
the frozen coefficients/intercept and overflow-safe sigmoid. No fitting,
imputation, feature selection, calibration, tuning or threshold-to-action step.

The additive v2 request retains native FeatureVector/FeatureResult evidence and
all input/profile/schema/model/scaler/training-run/qualification/dataset/lock
fingerprints, fold, session clocks and explicit singleton composition. Its
output reuses the existing BinaryProbabilityOutput: RAW, uncertainty not
estimated, validity UNKNOWN / RAW_RESEARCH_NOT_ADVISORY. Missing evidence never
becomes zero probability.

Scientific forecast ID hashes the semantic input values, schema, dataset/profile,
historical clocks, fixed model scientific identity, target and composition. It
excludes actual computation/capture clocks and clock-bearing full artifact hashes.
The separate full capture seal retains those audit identities. A new capture
clock does not create a different scientific forecast. Exact duplicate writes
are idempotent; conflicting captures for one scientific ID in a campaign are
rejected. Separate explicit rerun directories retain distinct audit captures;
they must never be double-weighted in future evaluation.

## Population accounting

Counts are disjoint except `eligible`, which equals `generated` in this completed
path. Protected exclusions are separate from ordinary exclusions. Reason counts
can overlap within one excluded row; they are not extra observations.

| Fold | Candidate | Eligible / generated | Unavailable | Excluded | Protected |
|---|---:|---:|---:|---:|---:|
| 2021 | 248 | 248 | 0 | 0 | 0 |
| 2022 | 248 | 248 | 0 | 0 | 0 |
| 2023 | 246 | 225 | 0 | 21 | 0 |
| 2024 | 249 | 248 | 0 | 0 | 1 |
| Total | 991 | 969 | 0 | 21 | 1 |

2023 reasons: 20 `FEATURE_ACTION_DEMERGER`, one `LABEL_UNSUPPORTED_ACTION`.
2024: one `TARGET_HOLDOUT_SEALED`, the 2024-12-31 origin targeting 2025.
No protected outcomes, class balance or protected forecast probabilities are
computed. All 2025 reference origins remain outside this run. No unknown counts
are silently substituted with zero; the source memberships are explicitly
enumerated and every in-scope origin gets a generated or absence capture.

## Persistence and replay

The additive research-v2 Capture Store profile uses content-addressed canonical
JSON and exclusive `xb` writes plus fsync, under the local Forecasting owner.
It does not widen synthetic-v1 custody rights or limits. A maximum of 64 capture
references per immutable shard, 1 MiB per record, 65,536 artifacts and 2 GiB per
campaign is enforced. Origins are capped at 4,096, one attempt each; inference
uses a cooperative one-second deadline and the campaign a 600-second bound.
No remote fetch, symlink or path escape, executable pickle, mutable current alias,
service, or new truth store. No cross-file transaction guarantee: partial writes
without a complete parent remain an incomplete campaign, not a usable report.

```text
data/ff1/logistic_forecasts_20260921/
  training-<training-run-fingerprint>.json
  model-<fingerprint>.json       # four
  scaler-<fingerprint>.json      # four
  capture-<fingerprint>.json     # generated AND explicit absence records
  shard-<fingerprint>.json       # <=64 ordered capture references each
  run-<fingerprint>.json         # parent, pins, populations, verification
```

The closed typed graph has no arbitrary reference edges: run → shards → captures
→ pinned training/model/scaler artifacts. Missing/tampered dependencies fail.
Recorded replay reconstructs captured contracts without source qualification,
CSV, Ground Truth, ML estimator imports or fitting. Pinned verification derives
probability from captured raw features and canonical model/scaler, comparing
with **absolute tolerance 1e-12**, then verifies parent lineage and population.
Pinned closure verification streams row-by-row through the immutable shards,
retaining only counters, scientific IDs and the four model artifacts, rather
than materializing the whole corpus. Result is MATCH/MISMATCH; originals are
never rewritten. Absence captures are
verified semantically, not numerically. Model artifacts retain their original
training summaries; no new test outcome summaries are read or produced.

## Commands and validation

Actual generation command:

```bash
.venv/bin/python scripts/generate_ff1_logistic_forecasts.py \
  --output data/ff1/logistic_forecasts_20260921
```

The fixed accepted paths can be relocated with `--qualification` and
`--training-run`, but their pins cannot be relaxed. Generation requires a new
Git-ignored directory under `data/ff1`. Replay uses `--corpus` and `--verify-run`
and does not require the optional ML packages. Exit 0 means completion/MATCH;
1 means HOLD/MISMATCH; 2 means invalid CLI arguments. No implicit default corpus.

Actual forecast run:
`4dc2adb6f2bb9977bf3a06c2c5903065223cfc6e2c6a58898c0cb65090197812`.
Persisted at
`data/ff1/logistic_forecasts_20260921/run-4dc2adb6f2bb9977bf3a06c2c5903065223cfc6e2c6a58898c0cb65090197812.json`.
All 991 result captures (969 numeric + 22 explicit exclusions/protection) replay
MATCH, **991 matches / 0 mismatches**, absolute tolerance **1e-12**. This includes
a second read-only replay after streamed verification hardening, with the same
original immutable run fingerprint. The initial generation/verification command
took **42.572 seconds**. Its probability minimum **0.3612836189804599** and maximum
**0.5627020269833228** are engineering range checks only, **not model quality**.

Exact offline verification command:

```bash
.venv/bin/python scripts/generate_ff1_logistic_forecasts.py \
  --corpus data/ff1/logistic_forecasts_20260921 \
  --verify-run 4dc2adb6f2bb9977bf3a06c2c5903065223cfc6e2c6a58898c0cb65090197812
```

| Validation | Measured result |
|---|---|
| Final FF-1.3 + FF-1.2 targeted | **99 passed in 258.49s**: 44 FF-1.3 + 55 FF-1.2 |
| Forecasting/evaluation + FF-0 acceptance | **818 passed in 360.70s**; includes FF-1.1/1.1A regressions and 28 FF-0 acceptance tests |
| Full repository | **3,295 passed in 660.01s** |
| Compile | `.venv/bin/python -m compileall -q src scripts` PASS |
| Ruff | `.venv/bin/ruff check src tests scripts` PASS |
| Mypy | `.venv/bin/mypy src tests` PASS, 629 source files |
| Dependency consistency | Exact approved hash/versions PASS; `pip check` PASS; `uv lock --check --offline` PASS (76 packages) |
| Documentation | 6 Markdown files, 278 local link targets, balanced fences PASS |
| CLI help | PASS; generation and read-only verification modes explicit |
| Source preservation | All six original provisioning/qualification SHA-256 values unchanged |
| Whitespace | `git diff --check` PASS |

The broader 818-test run began before the final streaming-verifier test was
added. The final 99-test run includes that test and the streamed implementation;
the passing full repository run also includes it. Early targeted runs passed 38 initial
and then 43 expanded tests. No empirical retry or fit retune was needed.
The optional `uv` executable was not on the shell PATH; the existing
`.venv/bin/uv` was used with a fresh writable `/tmp` cache after the default
read-only cache refused its temporary lock. This was an offline environment
adjustment, not installation, dependency resolution drift or a lock change.

Additional empirical isolation proof: in a fresh Python process, a meta-path
guard prohibited sklearn/NumPy/SciPy/joblib/threadpoolctl imports; socket creation
and original qualification/CSV/training-directory opens raised immediately.
The captured-corpus CLI replay still returned **991 MATCH / 0 MISMATCH** with
none of those optional packages imported. Generation's synthetic tests likewise
make fitting/network calls fail. Tests reject output outcome fields, protected
numeric inference, changed feature order, wrong fold model, probability tampering,
stale seals, missing closure, unsafe paths and conflicting scientific duplicates.
No application provider, broker or network operation was invoked in this pass.

The immutable parent was created **2026-09-21T21:02:51.214907+05:30**. The corpus
contains **1,017 files / 11,725,159 bytes**, including 16 immutable reference
shards. A6 and FF-0 tags remain unchanged at
`6dc2ff304aae0e87540260b092919bb91e4d4189` and
`e5283c9eaa4294bd236186d663335efdf7dab236` respectively.

File inventory: new `src/tiaf/forecasting/logistic_projection.py`,
`logistic_forecasts.py`, `logistic_store.py`,
`scripts/generate_ff1_logistic_forecasts.py`,
`tests/unit/forecasting/test_logistic_forecasts.py`, and this document. Updated
the FF-1.2 handoff record, `README.md`, `scripts/README.md`,
`docs/MILESTONES.md`, and `docs/IMPLEMENTATION_ROADMAP.md`. No existing runtime
source, tests, dependency locks, accepted plan or training implementation changed.

## Boundaries and next gate

No Brier, log loss, accuracy, calibration, reliability, paired losses, bootstrap,
model ranking, winner/loser verdict, trading threshold, recommendation or action.
No provider/broker/network/LLM calls, tokens or external cost. Local inference
does consume CPU; monetary cost is UNPRICED, not claimed zero. No A6, FF-0,
BaseRate, public facade/Shell or broader runtime changes. No holdout opening,
model promotion, ensemble, LLM/FM-LFDE or A8 implementation.

Only after FF-1.3 acceptance, the next separately authorized prompt is
**TIAF A7 / FF-1.4 — PAIRED BASERATE VS LOGISTIC EVALUATION**. Do not begin it here.
Recommended commit only after acceptance/review:
`feat(a7.ff1.3): generate logistic walk-forward forecasts`. No tag yet.
No commit/tag/push in this pass. Raw data, model artifacts and corpora remain
private, Git-ignored, and are not part of the proposed commit.
