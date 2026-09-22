# FF-1 — One-shot protected 2025 final-holdout evaluation

## Scope and authority

This is the additive execution of the
[accepted final protocol](TIAF_A7_FF1_FINAL_HOLDOUT_PROTOCOL_FREEZE_REVIEW_WITH_FIFTH_FOLD_HANDOFF.md),
not a new scientific design. The preceding
[fifth-fold preparation](TIAF_A7_FF1_PRE_HOLDOUT_FIFTH_FOLD_ARTIFACT_PREPARATION_AND_AUTHORITY_RECONCILIATION.md)
and [development evaluation](TIAF_A7_FF1_4_DEVELOPMENT_ONLY_PAIRED_BASERATE_VS_LOGISTIC_EVALUATION.md)
remain unchanged historical evidence.

Protocol: `2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814`.
The user authorized exactly one empirical execution. The frozen cutoff remains
2024-12-31 09:15 Asia/Kolkata, TRAIN 1690 (878 positive / 812 zero), references
2018-01-01 through 2024-12-27. The frozen BaseRate state is exactly 8/20 = 0.4,
last twenty scheduled transitions, unsmoothed, no invalid-transition backfill.
Neither scaler nor Logistic is fitted again.

## Execution and preservation boundary

1. Preflight verifies the exact protocol, 72 frozen source pins, dependency lock
   and installed versions, qualification bytes and structural membership,
   reviewed source files, original redacted context identity, and fifth-fold and
   development recorded closures. The unchanged reader redacts every 2025+
   numerical field. Opaque source-byte hashes are not an outcome opening.
2. A new execution identity pins the additive implementation and user authority
   document. The original protocol store consumes its deterministic, exclusive,
   fsynced claim. An opening record with actual Asia/Kolkata timestamp and
   protected-population identity is made durable before numeric source access.
3. Forecasting's final adapter reads only the union of required 21-session causal
   windows and target closes. The terminal 2026-01-01 row is **close-only**;
   unrelated future numerical fields are not converted or summarized. All
   causal inputs and both arms' forecasts are persisted before any Ground Truth
   projection. Both arms share each exact outcome-blind input identity.
4. Evaluation projects common revision-0 outcomes through the existing
   `research_direction` / `endpoint_direction` functions. It records endpoints,
   source identity, missing/precision/action facets, assumed label availability
   and one actual evaluation-as-known clock. The forecaster receives no labels.
5. Evaluation preserves every intended slot, joins only identity-matched evidence,
   and records row × arm × metric dispositions. Identity/clock/pin contradictions
   fail integrity; they are never silently excluded. The paired JSON table
   contains every probability, label, loss and lineage reference.
6. The complete captured closure is reconstructed before publishing its terminal
   `COMPLETE` ledger. Any consumed failure is terminal: no retry, no reset, no
   alternate seed or rescue fit. A report blob alone is not completion authority;
   the verified terminal ledger is required.

The original protected development and qualification contracts are not widened.
No public/runtime forecasting, recommendation, broker or execution semantics are
changed. The CLI blocks fitting-library/provider imports, socket operations,
subprocess execution and secret-file access; source files are read-only. Recorded
replay permits reads only from the final data corpus, not the original dataset,
qualification, development or fifth-fold data directories.

The local store uses exclusive content-addressed writes, canonical JSON,
fingerprints and immutable contracts. It is trusted operator custody, **not**
OS-level WORM storage or protection against an owner deleting/copying history.
Deleting the attempt/corpus to regain authority is forbidden.

## Frozen population, metrics and decision

The structural grid contains 249 references, 2025-01-01 through 2025-12-31,
including the terminal target 2026-01-01. A 2024 reference targeting 2025 is not
in the final grid. No imputation, backfill, target substitution or new exclusion.

Five A2 features retain their exact formulas and order: `ret_1`, `ret_5`,
`sma20_distance`, `realized_vol_20`, `relative_volume`. The adapter reuses the
accepted projector and its ±8 ULP perturbation checks. Missing bars, unsupported
action dependencies, unqualified volume, zero prior-volume denominator and
material feature drift retain the frozen absence semantics. Actual current
volume zero is not treated as missing. Equal normalized closes label zero;
non-equal near ties remain unavailable.

Only Brier and natural log loss are primary. Log-loss clipping is metric-only
at epsilon 1e-15; raw forecast probabilities remain recorded unchanged.
Differences are always **Logistic minus BaseRate** (negative favors Logistic).

The unchanged moving-block numeric kernel receives the entire ordered final grid
and its missing mask: noncircular overlapping 5-session blocks, 5000 replicates,
fresh NumPy 2.3.3 `Generator(PCG64(1729))`, replicate-major sampling, concatenation
then truncation to the original grid length, and no zero-pair redraw. Both loss
differences use the same indices. Two-sided 97.5% percentile intervals use linear
quantiles .0125/.9875; nominal Bonferroni 95% familywise coverage is approximate.
The new result envelope says `FINAL_HOLDOUT`, not `DEVELOPMENT_ONLY`.

Let A mean integrity/replay/methodology/metrics/intervals valid, paired N ≥200,
each class ≥40, coverage ≥80%, and ≥20 complete nonoverlapping five-session
blocks anchored at the first intended slot (drop the short tail).

| Frozen partition | Outcome |
| --- | --- |
| Not A | INSUFFICIENT_EVIDENCE |
| A, Brier upper <0, log-loss upper ≤.01 | LOGISTIC_SUPPORTED |
| A, Brier lower ≥0 or log-loss lower >.01 | LOGISTIC_NOT_SUPPORTED |
| Otherwise | INSUFFICIENT_EVIDENCE |

No additional final .02/.05 point-estimate gate. Accuracy at .5 (ties positive),
confusion, mean probability, prevalence, fixed-.5 same-pairs diagnostic, fixed
ten-bin reliability (minimum bin support 20), disagreement and endpoint/clipping
counts are descriptive only and cannot override this decision.

## Reproducibility and commands

Private corpus: `data/ff1/final_holdout_20260922/`. Forecast/input/outcome/pair blobs
are individually sealed; shards contain at most 64 row-reference groups. The
table and final report bind ordered Ground Truth and paired-population identities.
All datetimes remain aware canonical Asia/Kolkata; actual capture/computation
clocks are distinct from the simulated reference-close +30/+35 minute clocks.

Safe commands, before opening:

```bash
.venv/bin/python scripts/evaluate_ff1_final_holdout.py
.venv/bin/python scripts/evaluate_ff1_final_holdout.py --help
.venv/bin/python scripts/evaluate_ff1_final_holdout.py --preflight
```

The authorized invocation is historical execution documentation, **not a retry
instruction** once the protected holdout has been consumed:

```bash
.venv/bin/python scripts/evaluate_ff1_final_holdout.py --execute \
  --approved-protocol 2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814
```

After completion, use `--verify-ledger <recorded-ledger-fingerprint>` only.
This reconstructs features, frozen-model probabilities, frozen BaseRate,
Evaluation-owned truth, pair losses, original mask, pooled metrics, bootstrap
intervals and exact classification from captured evidence. It performs no second
source opening, claim, fit, threshold selection or new experiment.

## Empirical execution record

**FF1_FINAL_HOLDOUT_ACCEPTED** — scientific outcome **INSUFFICIENT_EVIDENCE**,
reason `CONFIDENCE_NONDECISIVE`. Engineering acceptance is not evidence of
Logistic superiority and is not model promotion.

```text
PROTECTED_HOLDOUT_STATUS = CONSUMED
FINAL_HOLDOUT_EVIDENCE = COMPLETE
FINAL_HOLDOUT_EXECUTIONS_USED = 1
POST_HOLDOUT_REFIT_ALLOWED = NO
AUTOMATIC_PROMOTION = NO
```

| Recorded clock (canonical Asia/Kolkata) | Value |
| --- | --- |
| Execution identity created | 2026-09-22T10:49:21.973040+05:30 |
| Durable opening / consumed timestamp | 2026-09-22T10:49:22.158293+05:30 |
| Source capture | 2026-09-22T10:49:22.172946+05:30 |
| Final report created | 2026-09-22T10:49:39.073658+05:30 |
| Ledger assembly clock (`completed_at`; publication follows verification) | 2026-09-22T10:49:39.198922+05:30 |

The sole `--execute` invocation exited 0. Protected capture contains 269 causal
OHLCV bars (2024-12-03 through 2025-12-31) and only the 2026-01-01 terminal close:
270 rows total. No unrelated 2026 numerical fields were normalized. The final
corpus contains **1,261 blobs, 7,003,440 bytes**; largest blob **375,777 bytes**,
below the native 1 MiB record bound.

### Population and support

| Quantity | Recorded result | Frozen minimum |
| --- | ---: | ---: |
| Candidate protected origins | 249 | Fixed intended grid |
| Logistic available | 249 | — |
| BaseRate available | 249 | — |
| Ground Truth available | 249 | — |
| Paired eligible / evaluated | 249 / 249 | 200 |
| Positive / zero labels | 128 / 121 | 40 each |
| Coverage | 1.0 (100%) | 0.8 |
| Complete nonoverlapping 5-session blocks | 49 | 20 |
| Exclusions / exclusion facets | 0 / none | No new exclusions permitted |

Integrity, methodology, reconstruction, metrics, intervals and all support gates
passed. The result is uncertain because of interval evidence, **not** because
of missing observations, class insufficiency or a failed replay.

### Primary results

| Primary metric | BaseRate | Logistic | Logistic − BaseRate | Frozen 97.5% interval for difference |
| --- | ---: | ---: | ---: | --- |
| Brier | 0.26281124497991964 | 0.24996333507967594 | -0.012847909900243735 | [-0.028089924933311944, 0.004386873268651029] |
| Natural log loss | 0.7192574865685811 | 0.6930742937929326 | -0.026183192775648522 | [-0.05702105803609845, 0.008685324032304249] |

The recorded difference is the frozen mean of per-observation loss differences;
subtracting the two separately rounded displayed means can differ in the last
binary64 bit. No numerical policy was changed.

The original-grid paired moving-block calculation used block length **5**,
**5,000** replicates, seed **1729**, confidence **97.5%**, linear quantiles
.0125/.9875 and **zero** zero-pair replicates. Both metrics shared exactly the
same sampled indices. No alternate sample, seed, block length or interval was run.

Applying the frozen partition: A is true; Brier upper is positive, so the
strict Brier-superiority condition fails. Log-loss upper is below .01, but that
alone cannot establish support. Brier lower is negative and log-loss lower is
below .01, so neither decisive-rejection condition holds. Therefore
**INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE**. Lower point estimates do not
override the interval rule. No retuning or reinterpretation follows this result.

### Frozen descriptive diagnostics

| Diagnostic | BaseRate | Logistic | Fixed .5 diagnostic |
| --- | ---: | ---: | ---: |
| Accuracy at .5, ties positive | 0.4859437751004016 | 0.5180722891566265 | 0.5140562248995983 |
| Mean probability | 0.4 | 0.5192597531249322 | 0.5 |
| TP / FP / TN / FN | 0 / 0 / 121 / 128 | 128 / 120 / 1 / 0 | 128 / 121 / 0 / 0 |
| Endpoint / clipped counts | 0 / 0 | 0 / 0 | 0 / 0 |

Observed prevalence: **0.5140562248995983**. Reliability retains ten fixed-width
bins, final bin closed, minimum descriptive support 20. BaseRate's [0.4,0.5)
bin contains all 249 observations (mean .4, observed .5140562248995983).
Logistic's [0.5,0.6) bin contains 248 observations (mean .519357780147542,
observed .5161290322580645); its [0.4,0.5) bin contains one observation (mean
.49494905151770346, observed 0), explicitly **LOW_SUPPORT**. Empty bins are
retained with null estimates, not fabricated calibration evidence. No calibration
fit or probability adjustment was performed.

The arms lie on opposite sides of .5 for **248/249** observations. Mean absolute
probability difference is **0.1192597531249322**. The five frozen largest
disagreements (reference date, absolute probability difference) are:

| Reference | Difference |
| --- | ---: |
| 2025-05-12 | 0.1505421619445233 |
| 2025-04-28 | 0.14036606789158745 |
| 2025-04-11 | 0.1325246127562948 |
| 2025-05-23 | 0.1323761311295646 |
| 2025-05-15 | 0.13139712211265953 |

These are descriptive, not a new subpopulation, alternative decision rule or
selection of days for rescue analysis.

### Immutable identities and lineage

| Identity | SHA-256 / semantic fingerprint |
| --- | --- |
| Frozen protocol | `2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814` |
| Frozen final policy | `1f3157945c25e643846812973d370621e2c81f04bec6f71533c5833f46a508e3` |
| Execution ID | `2948bc46874f8196c535720bd4f7882f6293fc96077acb563e2e11409c3e4840` |
| Durable attempt | `1578a48d3eae7c0c47ac72297845fe3f6b43a2c9b3bb8b20c3a60d63f0307815` |
| Opening record | `9fdfb4b0109e30c5d4f7f0ca7cb73379b4068541401bd91f8227cd1c2a8b7e2d` |
| Fifth-fold handoff | `c40148f60e985c83fe8bca027a3722583ed8c1999ecfc86e4959c4fe6166ce54` |
| Fifth-fold Logistic model | `c287d9333fbf6067dd16fe5ab51bb1e6a7c6168df6289b9e73669aa2a15f6381` |
| Fifth-fold scaler | `00e0ceaa160a7df2e518aafb4a8b1c2f86c55837eeeda94f131b002fae20afe8` |
| TRAIN ordered population | `7a448191a66a40d56dda54575c39ea9b586468b5ba17e0b65b948abb99203da0` |
| Fifth-fold authority | `31b54fdc10f6639c940e524f21ed10a343305c998b99d9f5815d710398c2c2ba` |
| Frozen BaseRate 8/20 state | `6a89a25e67d1a2e6d538b3754e61f7da932f4c8b5b6b72fbb2346a7040bf7e8e` |
| Qualification | `4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51` |
| Qualification bytes | `69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca` |
| Original dataset bytes | `d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6` |
| Adjusted research profile | `1e616cc7a2f3654d856b916e790d054a6c1ff7f10efe2b316cf0a44835011c45` |
| Feature schema | `76e63292685ee0b3b41f7ab033407e6bd014fc802d2092a2ed227888bdc71676` |
| Dependency lock | `54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86` |
| Protected intended population | `899d3852798f3ff92b6ddc2f1b1651504b4923a7ad440e702230fdb9f986adda` |
| Captured bounded source | `e980493a39a28bb28e6a8449476c7397e26dbe1749be734fbe8a8126006a9ddb` |
| Ordered Ground Truth journal | `277f6734b535c8f75e1aa8aa26d53080c510992caf7c95cf104b01c08dffc339` |
| Paired population | `318063789f31dbaf779513679aaa36d3acc44ab88744e4c04697bdd8dc8d3444` |
| Forecast population (both arms) | `000fed6c8736f748f28e3f66aeb16ca349b47d29f69861603fd2eff9252007ac` |
| Paired table / dispositions | `174bbc8e8fa5524af9e673df4cddc43adeb3c156ffb263ec37f5cf471630c3dc` |
| Bootstrap sampled indices | `ff27bcde090b415343aca2f4f0a2944278ce06a815d777c609750e2f9e4b2ab9` |
| Final evaluation | `8c0556e7b88284c170db57d745de7ece707d365ab52a585db5ebb0d3e81a7d0e` |
| Complete ledger | `630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583` |

The transparent per-observation JSON table is
`data/ff1/final_holdout_20260922/table-174bbc8e8fa5524af9e673df4cddc43adeb3c156ffb263ec37f5cf471630c3dc.json`.
Each pair links its common causal input, both forecast identities and exactly
one revision-0 Ground Truth identity. The journal identity hashes the ordered
outcome references carried in the captured shards; it is not a recomputed
classification detached from source evidence.

### Captured replay and preservation proof

The execution's internal full-closure verification passed before COMPLETE
publication. A separate **read-only** CLI verification then also returned MATCH:

```bash
.venv/bin/python scripts/evaluate_ff1_final_holdout.py \
  --verify-ledger 630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583
```

It reconstructed all features/probabilities/truth links/losses/metrics, the fixed
bootstrap and scientific classification/fingerprint without another source read
or execution claim. Only one attempt exists in canonical protocol custody.
The 72 original source pins and six additive implementation/test pins matched
after execution and during CLI verification. No code, feature/exclusion rule,
artifact, metric, seed, threshold or model/scaler/BaseRate was changed after
opening; subsequent edits only record results and update documentation navigation.

All **4,026** existing fifth-fold/development/provisioning/qualification files
were byte-identical before and after execution. Aggregate path-to-byte-hash
identity: `d1f77860abd2d2ed332224246338d99125367e6390b81d2138462793f3bfd6ac`.
This includes 4,019 prior fifth-fold/development blobs. No provider, broker,
network, external model call or empirical fit occurred in this pass.

## Validation and files

All substantive implementation tests ran before empirical consumption. Synthetic
fixtures are programmatically constructed and never read private holdout values.
Existing regression suites may perform their established synthetic toy fits;
they do not refit the empirical fifth-fold artifacts.

| Check | Result |
| --- | --- |
| New final-holdout tests | 31 passed (part of the combined run below) |
| New final-holdout + existing frozen-protocol tests | 94 passed in 23.92s; earlier combined run 26.40s also passed |
| Forecasting/evaluation regressions, including FF-0 and FF-1.1 through FF-1.4/fifth-fold | 941 passed in 606.93s |
| Full repository suite | 3,445 passed in 928.14s |
| Additional evaluation architecture tests | 7 passed in 1.15s |
| Existing engineering CLI regressions after documentation updates | 58 passed in 21.29s |
| Full-year synthetic closure / store-size proof | 261 origins, 1,322 blobs, largest 393,778 bytes, MATCH |
| `python -m compileall src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS, 646 source files |
| Offline `uv lock --check` | PASS, 76 packages resolved |
| Offline installed-environment `uv pip check` | PASS, 75 compatible packages |
| Safe default / CLI help / bad protocol | PASS; no opening |
| Frozen protocol / preflight | MATCH before opening |
| Captured final replay | MATCH, no second execution |
| Local documentation links / `git diff --check` | PASS; 289 links across five changed documents; new-file whitespace checked separately |

Principal commands used (with `.venv/bin/` executables):

```bash
pytest -q tests/unit/evaluation/test_final_holdout.py tests/unit/evaluation/test_final_protocol.py --tb=short
pytest -q tests/unit/forecasting tests/unit/evaluation
pytest -q
python -m compileall src scripts
ruff check src tests scripts
mypy src tests
uv lock --check --offline
uv pip check --python .venv/bin/python
git diff --check
```

New files: `scripts/evaluate_ff1_final_holdout.py`,
`src/tiaf/forecasting/final_inputs.py`,
`src/tiaf/evaluation/forecast_final_outcomes.py`,
`src/tiaf/evaluation/forecast_final_scoring.py`,
`src/tiaf/evaluation/forecast_final_store.py`,
`tests/unit/evaluation/test_final_holdout.py`, and this report.
Navigation updates: `README.md`, `scripts/README.md`, `docs/MILESTONES.md`,
`docs/IMPLEMENTATION_ROADMAP.md`. No pre-existing runtime source, dependency file,
prior scientific report, commit or tag was changed. Private final evidence and
the single canonical consumed claim are persisted in the existing ignored data
area, not added to Git.

Acceptance blockers: **none**. No empirical execution defect was found. The
scientific limitation is the frozen nondecisive confidence interval, which is
preserved rather than repaired or reinterpreted.

## Limitations and promotion boundary

This remains single-symbol adjusted **SIMULATED_RESEARCH**, from a fresh 2026
historical vintage, not point-in-time evidence or an ACTUAL operational forecast.
Rights remain UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING, not legal approval.
Provider-defined volume adjustment is uncertain; normalized binary64 values are
not source-forensic prices. The reviewed calendar/action scope is bounded, not a
full operational calendar or corporate-action platform. Block-bootstrap
stationarity/dependence and multiplicity coverage are approximations, not
guarantees of future performance. There is no trading/P&L claim.

Logistic remains CHALLENGER / EXPERIMENTAL regardless of this outcome. BaseRate
remains BENCHMARK. No automatic promotion, public/live activation, calibration,
trading action or post-holdout refit. The consumed 2025 holdout is never reusable
for this experiment. Future revisions require a new experiment and independent
evidence; insufficient evidence is not permission to reopen this holdout.

If accepted, the exact next task is **TIAF A7 / FF-1 — INDEPENDENT FINAL SCIENTIFIC
CLOSURE AND BASELINE DECISION**. Suggested commit (not performed here):
`feat(a7.ff1): execute one-shot 2025 final-holdout evaluation`. No tag yet.
