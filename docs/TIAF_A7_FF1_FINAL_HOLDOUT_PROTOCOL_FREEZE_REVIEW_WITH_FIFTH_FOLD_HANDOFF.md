# FF-1 — Final-holdout protocol freeze review with fifth-fold handoff

## Decision and scope

Review date: 2026-09-22, Asia/Kolkata. Entry tree clean at
`947f3fcd9aec8db00a64120b02a54f1251ffc372` (committed fifth-fold preparation).
This is a source/artifact-based independent verification of the earlier work,
not a claim of independent human peer review. All gates pass and the canonical
protocol is frozen. No protected evaluation is performed in this pass.

```text
FF1_READY_FOR_FINAL_HOLDOUT
FIFTH_FOLD_BLOCKER = RESOLVED
FINAL_HOLDOUT_EVALUATION_AUTHORIZED = YES
FINAL_DECISION_PROTOCOL_FROZEN = YES
PROTECTED_HOLDOUT_STATUS = SEALED
FINAL_HOLDOUT_EVIDENCE = NOT_RUN
POST_HOLDOUT_REFIT_ALLOWED = NO
```

Authorization applies only to the exact pinned one-shot protocol in the
separately requested execution pass. It does not trigger execution in this review.

The [prior independent review](TIAF_A7_FF1_INDEPENDENT_SCIENTIFIC_ACCEPTANCE_AND_FINAL_HOLDOUT_DECISION_DESIGN.md)
HOLDed solely because the planned fifth-fold model/scaler/BaseRate did not exist.
The [separate preparation](TIAF_A7_FF1_PRE_HOLDOUT_FIFTH_FOLD_ARTIFACT_PREPARATION_AND_AUTHORITY_RECONCILIATION.md)
supplied those artifacts under its one-fit authority. Both reports and all their
captured artifacts are preserved. No fitting is repeated here. Final readiness
does not change accepted FF-1.4's development-only INSUFFICIENT_EVIDENCE result.

## Independent handoff and development checks

The review reconstructs the fifth-fold closure, including TRAIN membership and
means/variances, exact coefficients/scales and the captured engineering probes,
using `verify_fifth`. It reconstructs the accepted DEVELOPMENT_ONLY Ledger using
`verify_evaluation`: common truth linkage, both arms, dispositions, losses,
bootstrap indices/intervals and the report seal. It does not reconstruct any
final-year probability or outcome.

Fifth cutoff is exactly **2024-12-31T09:15:00+05:30**. TRAIN has **1,690** rows,
878 positive / 812 zero, reference dates 2018-01-01 through 2024-12-27. Every
captured training target/availability is strictly pre-cutoff; the whole embargo
session is excluded. These are TRAIN counts, not protected class counts.
The fixed L2/C=1/lbfgs/tol=1e-8/max_iter=1000/intercept/no-class-weights model
converged in 11 iterations; no estimator is imported or fit in this review.
The original preparation source identity, plan bytes and lock must still match.

BaseRate is frozen at the **same cutoff**, last 20 scheduled transitions,
minimum support 20, unsmoothed **8/20 = 0.4**, without invalid-transition backfill.
No rolling update, prior-fold substitution or full-history average is permitted.
The pre-open preparation grant never authorizes post-open refitting.

Development evidence remains 969 exact pairs, all declared support/stability
gates passed, classification INSUFFICIENT_EVIDENCE because final evidence has
not run. Development gains do not prove operational/PIT validity, calibrated
probabilities, improvement over fixed .5, tradability or profitability. The prior
fixed-.5 diagnostic limitation is retained, not made into a new rejection gate.

## Frozen identities

| Identity | SHA-256 semantic fingerprint unless explicitly bytes |
|---|---|
| Development evaluation | `5f6d4342c61017fecda2196715d707a356ff8728eb0ec1f6996c362723ba19e1` |
| Development Ledger | `62bc746d90386f3b718bf6fe106f4a80832bfa8206ea3605ec96bbb2e5817246` |
| Fifth-fold handoff | `c40148f60e985c83fe8bca027a3722583ed8c1999ecfc86e4959c4fe6166ce54` |
| Scaler | `00e0ceaa160a7df2e518aafb4a8b1c2f86c55837eeeda94f131b002fae20afe8` |
| Logistic model | `c287d9333fbf6067dd16fe5ab51bb1e6a7c6168df6289b9e73669aa2a15f6381` |
| Ordered TRAIN population | `7a448191a66a40d56dda54575c39ea9b586468b5ba17e0b65b948abb99203da0` |
| Fifth-fold fit authority | `31b54fdc10f6639c940e524f21ed10a343305c998b99d9f5815d710398c2c2ba` |
| BaseRate state | `6a89a25e67d1a2e6d538b3754e61f7da932f4c8b5b6b72fbb2346a7040bf7e8e` |
| Qualification | `4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51` |
| Qualification bytes | `69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca` |
| Dataset bytes | `d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6` |
| Research profile | `1e616cc7a2f3654d856b916e790d054a6c1ff7f10efe2b316cf0a44835011c45` |
| Five-feature schema | `76e63292685ee0b3b41f7ab033407e6bd014fc802d2092a2ed227888bdc71676` |
| Dependency-lock bytes | `54e8577800d2a9132df2c8d3721e0d880da9e706a58f6d8b9beba75338e0ac86` |
| Final population | `899d3852798f3ff92b6ddc2f1b1651504b4923a7ad440e702230fdb9f986adda` |
| Final decision policy | `1f3157945c25e643846812973d370621e2c81f04bec6f71533c5833f46a508e3` |
| Final protocol | **`2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814`** |

Experiment `ff1.reliance.daily_logistic_vs_b0/1.0`; protocol
`ff1.final_holdout.protocol/1.0`; schema remains additive research 2.0.
Package version remains 0.1.0. Protocol also pins the accepted plan, this review
request, original provisioning/calendar/action review and arithmetic source
files. No source file governing the frozen semantics may drift during execution.
The next pass may add an outcome adapter/runner without changing these pinned
files or policy. It must record its own implementation hash in the execution
manifest before consumption, pass synthetic conformance checks and use the
unchanged arithmetic. Protocol verification checks the named pinned files, not
a wildcard inventory that would incorrectly forbid the planned additive runner.

## Exact population and materialization boundary

Subject: RELIANCE/NSE cash equity. Target:
`equity.next_session_close.return_gt_zero/1.0`. Mode SIMULATED_RESEARCH, adjusted
price basis, same five-feature schema. Fresh 2026 data vintage and assumed
historical availability remain explicit; not ACTUAL or CAPTURED_AS_KNOWN.
Rights remain UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING for this existing
bounded research scope, not a new legal or production authorization.

Freeze the ordered IDs, reference dates and target dates from the byte-pinned
qualification. Check exact agreement with the pinned reviewed exchange calendar
and fifth-fold `test_ids`. **All qualified 2025 reference sessions** remain in
the intended grid, including unavailable rows. The target is the true next
qualified session, including a terminal 2026 session. Exclude 2024 references
even when they target 2025; never drop a 2025 reference because its target is in
2026. Missing targets remain explicit unavailable slots, not substitute dates.
The checked structural grid contains **249** reference sessions, 2025-01-01
through 2025-12-31, with terminal target 2026-01-01. No final paired N, class
balance or eligible-feature count is measured here.

The sealed qualification deliberately contains **no 2025 features or labels**.
Its HOLDOUT_SEALED placeholder is an access-control state, not permanent final
scientific ineligibility. The subsequent authorized one-shot pass must use an
additive protected adapter after consuming authority; it must not relax the old
development/qualification readers or relabel research as synthetic. It applies
the already pinned qualification/feature/Ground Truth arithmetic to the exact
original byte-pinned source. No new data download, qualification policy or
exclusion choice. Implementation and synthetic conformance checks precede the
single opening; discovering a policy gap requires a separate review, not an
on-the-fly decision while observing outcomes.

Rules carried forward unchanged:

- Feature input: the reference session and 20 preceding scheduled bars, no
  target/future bar; all five fixed A2 values AVAILABLE, finite, correct units
  and order, no imputation. Preserve missing-bar/lookback/action, volume numeric
  bounds/zero denominator and precision-drift exclusions in the pinned qualifier.
- Corporate actions: supported split/bonus adjustment only under existing
  evidence; unsupported action crossing a feature dependency or label interval
  retains its established exclusion. No new event-dependent rule after opening.
- Truth: Evaluation owns the common journal. Apply existing `research_direction`
  and `endpoint_direction`: same adjusted positive finite endpoints, exactly
  equal normalized closes map to zero; non-equal values within the fixed eight-
  ULP perturbation envelope are unavailable, not rounded to zero. Missing targets
  and incompatible basis remain unavailable/failure under the same rules.
- Preserve simulated information cutoff = reference close +30 minutes and
  simulation-as-of = cutoff +5 minutes, strictly before target open. Assumed
  label availability = target close +30 minutes. Actual acquisition, computation
  and evaluation-as-known clocks remain separate and aware Asia/Kolkata.
- Qualified original context/structural IDs stay pinned. When protected features
  are materialized, hash **actual causal bars**, not the qualification's redacted
  placeholder rows. Both arms share that exact feature-input/request identity;
  no target value enters it. Truth revision 0 refers to this same fixed source
  and profile; a later correction is a new identity/experiment, not a rerun.
- Logistic uses only the fifth-fold model/scaler. BaseRate is 0.4 with its exact
  support identity. Both must be AVAILABLE and finite in [0,1]. No missing arm
  replaced by .5, zero or an earlier model. Ground Truth must be evaluable and
  identically linked to both forecasts at the fixed execution-as-known clock.

Exact pair key is captured in `FinalPopulation.pair_key`: experiment/fold,
observation, subject/target version, reference/target/session window, basis/unit,
information cutoff/simulation clock/mode, common causal input fingerprint,
qualification/dataset/profile, label policy, truth revision, evaluation-as-known
and uniform weighting. Arm model IDs differ intentionally. Identity, duplicate,
source-pin or clock contradictions fail integrity; never silently exclude a
mismatched row to improve coverage. Known policy absences retain primary reason,
all facets and unevaluated checks for each requested row × metric × arm.
Disposition order: scope → identity/PIT/basis/session/actions → forecast absence
→ truth absence → metric applicability → included. No compressed-grid bootstrap
or silent inner join.

## Metrics, uncertainty and exact decision partition

Primary metrics are Brier `(p-y)^2` and natural-log loss. Metric-only clipping
uses epsilon 1e-15; raw probabilities are retained. Uniform unique paired rows.
Difference is **Logistic loss minus BaseRate loss**: negative favors Logistic.
Secondary only: fixed `p>=.5` accuracy (ties positive), confusion, mean p,
coverage, ten fixed-width reliability bins (last closed; <20 LOW_SUPPORT),
probability disagreement, endpoint/clipping counts and fixed-.5 same-pair
diagnostic. No threshold optimization, learned calibrator or subgroup search.

Bootstrap is the accepted paired non-circular moving-block method:

| Setting | Frozen value |
|---|---|
| Grid/order | Full intended final-year grid, reference-session ascending, preserve missing mask |
| Blocks | 5 scheduled sessions; starts uniformly in `0..T-5`; no wrapping |
| Replicates | 5,000; same sampled indices for both primary losses |
| Generator | NumPy 2.3.3 `Generator(PCG64(1729))`; fresh final-summary seed |
| Terminal handling | Concatenate blocks, truncate to T slots, then apply mask |
| Interval | 97.5% two-sided percentile, linear quantiles .0125/.9875 |
| Multiplicity | Nominal Bonferroni 95% familywise, conditional on dependence approximation |
| Empty replicate | NOT_ESTIMABLE, no redraw, seed retry or shorter block |
| Support | ≥200 pairs; ≥40 per class; ≥80% original-grid coverage; ≥20 complete nonoverlapping five-session paired blocks starting at first grid slot (short tail ignored) |

These are engineering support guards, not a power calculation or proof of
independence/stationarity. Accepted dependence/vintage limitations are retained;
no discretionary new diagnostic veto or repaired block size after opening.
Source/identity drift, violated clocks, unauthorized refit/exclusion, leakage,
pre-open contamination, arithmetic/replay failure or violated declared bounds
invalidates the corresponding integrity/methodology gate. These are objective
checks, not a license to choose whether an unattractive outcome is valid.

Let `A` mean all fixed support, integrity, replay, methodology, primary-metric and
interval-estimability gates pass. Let `B_L,B_U` and `L_L,L_U` be the declared
Brier and log-loss difference interval endpoints. Development gates must already
pass before the opening grant; they are not reselected or pooled with final data.

| Priority | Exact condition | Classification |
|---|---|---|
| 1 | `not A` | INSUFFICIENT_EVIDENCE |
| 2 | `A and B_U < 0 and L_U <= .01` | LOGISTIC_SUPPORTED |
| 3 | `A and (B_L >= 0 or L_L > .01)` | LOGISTIC_NOT_SUPPORTED |
| 4 | `A` and neither bound condition above | INSUFFICIENT_EVIDENCE |

This partition is exhaustive and mutually exclusive for valid ordered finite
intervals. Brier upper bound **equal to zero** is not support; lower bound equal
to zero is decisive absence of the required strict benefit. Log-loss upper
bound **equal to .01** passes noninferiority; lower equal to .01 alone is not
decisive rejection. Crossing a gate, even with an unfavorable point estimate,
is inconclusive unless the other metric decisively rejects. An upper confidence
bound crossing .01 is not by itself rejection. No additional final .02/.05
point-estimate gate: those margins belong to development stability. Final
unacceptable degradation is controlled by the registered .01-nat bound.

The explicit lower-bound rejection/inconclusive split is a pre-open
RESEARCH_POLICY_CLARIFICATION of the original broad “scientific gate failure”
wording, required by this review request. Support thresholds, minimum N,
margins and uncertainty method do not change. It prevents treating ordinary
inconclusiveness as rejection; neither endpoint is chosen after seeing outcomes.
Invalid summaries raise a typed failure rather than being counted as evidence.
A crashed/failed job has **no scientific verdict**; its blocked claim remains
insufficient, never a fabricated zero loss or LOGISTIC_NOT_SUPPORTED.

## One-shot custody, no-refit and promotion

`FINAL_HOLDOUT_EXECUTIONS_ALLOWED = 1`; `POST_HOLDOUT_REFIT_ALLOWED = NO`.
The new Evaluation-owned store extends the existing canonical research store;
it admits one protocol per fixed operator corpus, not a mutable alias. Semantic
collections are tuples, JSON arrays round-trip, seals are checked on read, and
the protocol cannot be replaced through the supported API.

Future execution must preflight exact protocol/source/dependency/authority pins
and use `consume_once(protocol_fp, approved_protocol=protocol_fp)` **before any
protected numeric decoding**. It creates an exclusive deterministic attempt
record and fsyncs both the file and parent directory. Only one concurrent caller
can succeed. Any partial/failed write or later failure consumes the attempt;
reopening the process or store does not restore authority. There is no retry,
reset, force, alternate-output or holdout-opening option in the freeze CLI.
This pass writes **no attempt record** and does not invoke consumption on the
empirical corpus; one-shot tests use temporary synthetic stores only.

No post-open refit of either model or scaler; no changed features, target,
BaseRate, exclusions, threshold, bootstrap seed/block/confidence or metric.
A future read-only verification of the captured completed closure may reproduce
the exact published result without new source reads, alternative choices or a
fresh inference campaign. It is not a second scientific execution. An incomplete
attempt cannot be rescued by a second opening. A revised candidate needs a new
experiment/version and independent confirmation sample.

Custody is **trusted local single-experiment control**, not protection against
an administrator copying/deleting files or bypassing Python APIs. The fixed
private directory and external protocol pin must be retained; a copied empty
directory is not new authority. No distributed locking, broker integration or
public forecasting runtime is introduced. A final scorer is intentionally not
implemented in this review; its later adapter must obey these pins and the
tested consumption seam before obtaining outcome access.

| Future scientific result | Next state |
|---|---|
| LOGISTIC_SUPPORTED | Close scoped experiment supported; independent closure/baseline review; Logistic remains CHALLENGER/EXPERIMENTAL pending separate promotion |
| LOGISTIC_NOT_SUPPORTED | Retain BaseRate BENCHMARK; close Logistic v1 unsupported; no tuning against this holdout; revision requires new experiment |
| INSUFFICIENT_EVIDENCE | Preserve uncertainty; no reopen/recycle of 2025; future ACTUAL evidence or a new experiment requires separate authority |

None activates PRIMARY, public/live forecasting, calibration, trading actions,
broker operations or A8. Scientific support is not promotion.

## Independent findings and policy classification

| ID | Area | Evidence | Finding | Decision | Severity | Action |
|---|---|---|---|---|---|---|
| F01 | Prior blocker | Fifth handoff and `verify_fifth` | Dedicated final artifacts replace missing identities, not the 2024 model | ACCEPT | Informational | Pin handoff |
| F02 | Training | Preparation TRAIN rows and manifest | All targets/availability pre-cutoff; no 2025 fitting label | ACCEPT | Informational | No more fitting |
| F03 | Scaler | Independent means/variance reconstruction | TRAIN-only, same five-feature order | ACCEPT | Informational | Keep exact scaler |
| F04 | Model | Frozen config, coefficients, 11 iterations, probe reconstruction | No hyperparameter/solver change | ACCEPT | Informational | Keep exact model |
| F05 | Dependencies | Lock/source hashes and installed versions | Same approved arithmetic/dependencies | ACCEPT | Informational | Refuse drift |
| F06 | BaseRate | Last-20 support membership and sum | 8/20, same cutoff, no backfill | ACCEPT | Informational | No rolling updates |
| F07 | Authority | Separate FifthFoldGrant | Pre-open original fit is not post-open refitting | ACCEPT | Informational | Post-open refit forbidden |
| F08 | Holdout integrity | Guarded safe-closure access and metadata allow-list/sentinels | No protected prices/labels/features/metrics decoded here | ACCEPT | Limitation | SEALED; cannot prove absence of external human familiarity |
| F09 | Development | Independent recorded Ledger replay | 969 pairs; fixed support/stability gates pass; final evidence absent | ACCEPT | Limitation | Preserve development INSUFFICIENT_EVIDENCE |
| F10 | Population | Pinned IDs/dates versus reviewed calendar | Preserve terminal 2026 target; absent protected features need later governed materialization | ACCEPT_WITH_CLARIFICATION | Engineering boundary | Additive opener only after durable claim |
| F11 | Bootstrap | Accepted plan §12 and DevelopmentPolicy | Same mask, five-session blocks, seed, quantiles; approximate coverage | ACCEPT | Limitation | No tuning or redraw |
| F12 | Decision partition | FinalPolicy and exhaustive synthetic boundary tests | Separate decisive rejection from ordinary uncertainty | ACCEPT_WITH_CLARIFICATION | Research policy | Freeze before opening |
| F13 | One-shot | Exclusive/fsynced claim and concurrent/failure tests | Restart/mutation cannot reset supported local workflow | ACCEPT_WITH_CLARIFICATION | Local-custody limitation | Preserve fixed store; no bypass/reset |
| F14 | Promotion | Decision contract and next-state policy | Supported is not PRIMARY/live/trading authority | ACCEPT | Informational | Independent closure/promotion |

| Item | Classification | Meaning |
|---|---|---|
| Target, five features, training, BaseRate, metrics, uncertainty, final support floors/bounds | NO_CHANGE | Existing accepted values preserved |
| Decisive lower-bound rejection versus interval overlap | RESEARCH_POLICY_CLARIFICATION | Explicit pre-open partition; no automatic rejection of uncertainty |
| Materialize sealed source into additive final research contracts | ARCHITECTURE_CLARIFICATION | Forecasting owns causal inputs/inference, Evaluation owns common Ground Truth; old guards stay intact |
| Exclusive attempt custody, hash pins and metadata projection | IMPLEMENTATION_DETAIL | Bounded local enforcement of one-shot/freeze rules |
| Protected scoring, final scientific classification and promotion | DEFER | Separate next pass; promotion remains separately governed |

## Artifacts, commands and validation

Private protocol corpus: `data/ff1/final_protocol_20260922/`. Store preserves
the existing 1 MiB per-record, 65,536-record, 2 GiB limits. Protocol embeds the
non-outcome population and policy; no protected rows or probabilities. Created
at **2026-09-22T09:14:35.762573+05:30**, never backdated to the historical fit
cutoff. One canonical protocol blob, **47,370 bytes**, with **72** named source
file pins; **zero empirical attempt records**. Independent readback and the
operator `--verify-protocol` both return MATCH.
Do not remove this custody record or rerun freeze as a new experiment.

```bash
# Safe default: no work. There is no --execute or --open option.
.venv/bin/python scripts/freeze_ff1_final_protocol.py
.venv/bin/python scripts/freeze_ff1_final_protocol.py --help
# Freeze once, only after all review gates pass; no outcome access:
.venv/bin/python scripts/freeze_ff1_final_protocol.py --freeze
# Read-only replay; does not consume the execution slot:
.venv/bin/python scripts/freeze_ff1_final_protocol.py \
  --verify-protocol 2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814
```

The review process blocks sockets/subprocesses/fitting imports, all non-selected
`data/ff1` reads and writes to input corpora. The sole qualification read uses
byte verification then a strict ID/date/context allow-list, never whole-object
decoding, features, label state, availability or test-class summaries. Raw CSV
and protected numeric source files are blocked. The metadata calendar/action
review is local, with no live lookup. Prior captured inputs are byte-hashed
before/after review. This is access-path evidence, not a guarantee about previous
external human knowledge or unobserved processes.

| Gate | Result |
|---|---|
| New final-protocol tests | 63 passed in 3.91s (final source; initial 4.22s run also passed) |
| Forecasting/evaluation + FF-0 | 938 passed in 703.57s |
| Full repository suite | 3,414 passed in 937.97s |
| Compileall `src scripts` | PASS |
| Ruff `src tests scripts` | PASS |
| mypy `src tests` | PASS, 641 source files |
| Dependency lock / `pip check` | PASS; 76 packages resolved offline, no install; no broken requirements |
| Guarded development/fifth reconstruction | Both MATCH; all 4,019 safe input blobs unchanged |
| Existing script documentation/smoke tests | 10 passed in 0.32s after final navigation updates |
| Protocol canonical readback / CLI replay | MATCH; all handoff pins match; no empirical attempt record |
| Documentation links and `git diff --check` | PASS, 284 local targets; new-file whitespace and fences also checked |

Exact test commands:

```bash
.venv/bin/pytest -q tests/unit/evaluation/test_final_protocol.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting tests/unit/evaluation tests/acceptance/ff0
.venv/bin/pytest -q
```

Focused coverage includes fifth-fold, FF-1.4, FF-1.3, FF-1.2, FF-1.1/1.1A,
forecasting/evaluation regressions and FF-0 acceptance. Synthetic computations
in tests are not protected empirical scoring or new empirical fitting.

Files created: `src/tiaf/evaluation/forecast_final_protocol.py`,
`src/tiaf/evaluation/forecast_final_custody.py`,
`scripts/freeze_ff1_final_protocol.py`,
`tests/unit/evaluation/test_final_protocol.py`, this report. Navigation updates
affect README, scripts README, milestone ledger and implementation roadmap.
Existing runtime source, dependency files and prior scientific reports are
unchanged. No provider, broker or external model call, no fit, no final-year
forecast, no protected metric, no final scientific outcome.

## Next step and Git

Readiness blockers: **none**. No final-holdout evidence has been produced.
Exact next prompt:
**TIAF A7 / FF-1 — ONE-SHOT PROTECTED 2025 FINAL-HOLDOUT EVALUATION**.
That future pass is deterministic execution of this protocol, not fresh policy
design. It requires the separate explicit operator request; this review does
not itself open or score protected data.

Recommended commit:
`docs(a7.ff1): freeze one-shot final-holdout protocol`.
No tag yet. No commit/tag/push in this pass.
