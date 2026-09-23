# A7 / FF-2.0 — Calibrated Logistic research protocol

Protocol identity: `ff2.calibrated_logistic.research/1.0`.
Defined 2026-09-23, Asia/Kolkata, against the verified FLC baseline below.
**CURRENT — PROTOCOL ONLY; HOLD_FF2_IMPLEMENTATION.**

This document fixes a bounded proposed scientific design, not an execution grant
or a runtime policy. Its exact document hash is recorded in the
[readiness record](TIAF_A7_FF2_0_BASELINE_DATA_RIGHTS_AND_READINESS.md).
Any substantive revision requires a new protocol version and review, never an
in-place change after inspecting new results. No executable protocol artifact,
calibrator, fitted parameters, new forecast, evaluation or activation is created
by this pass. “Protocol defined” is not “experiment authorized/frozen for opening.”

## 1. Verified starting point and immutable history

The entry tree was clean on `main`. Local HEAD, local `origin/main`, live remote
`refs/heads/main` and the peeled local/remote `tiaf-a7-flc-baseline` tag all resolve
to **`5f1e80c7e0614233b5670ca3acf9229edd0ea0db`**. The annotated tag object is
`08767b720c62410166717a6df0002a7e9e24e692`. Commit subject:
`TIAF A7: freeze Forecaster Lifecycle Completion baseline`. Ahead/behind: 0/0.
FF-0, FF-1 and FLC are COMPLETE / FROZEN. The
[FLC closure report](TIAF_A7_FLC_8_REFERENCE_IMPLEMENTATION_CLOSURE_AND_FLC_ACCEPTANCE.md#13-authorized-family-neutral-inference-reconciliation)
retains its historical review states; the verified Git freeze is subsequent.

```text
FF1_FINAL_CLOSURE_ACCEPTED
FF1_SCIENTIFICALLY_CLOSED_INCONCLUSIVE
FF1_SCIENTIFIC_OUTCOME = INSUFFICIENT_EVIDENCE
SCIENTIFIC_REASON = CONFIDENCE_NONDECISIVE
FF1_INFRASTRUCTURE_ACCEPTED = YES
BaseRate = BENCHMARK
Logistic = CHALLENGER / EXPERIMENTAL
LOGISTIC_PROMOTION_ELIGIBLE = NO
FF2_CALIBRATION_RESEARCH_ELIGIBLE = YES, NEW proposal only
FF1_2025_HOLDOUT = CONSUMED
FF1_FINAL_HOLDOUT_EXECUTIONS = 1
POST_HOLDOUT_REFIT_ALLOWED = NO
```

Historical FF-1 results, copied from accepted records, **not recomputed**:

| Paired N = 249 | BaseRate | Logistic | Logistic − BaseRate | 97.5% interval |
| --- | ---: | ---: | ---: | --- |
| Brier | 0.262811245 | 0.249963335 | -0.012847910 | [-0.028089925, 0.004386873] |
| Log loss | 0.719257487 | 0.693074294 | -0.026183193 | [-0.057021058, 0.008685324] |

Both intervals cross zero. Lower point losses are not a Logistic win. The
[readiness record](TIAF_A7_FF2_0_BASELINE_DATA_RIGHTS_AND_READINESS.md#frozen-preservation-checks)
records the four unchanged scientific fingerprints and 78 unchanged pins.
No FF-1 reopening, coefficient/scaler refit, new features, retuning, target change,
threshold optimization, calibration rescue or second final execution is allowed.

## 2. Exact question and estimand

For RELIANCE/NSE cash equity and the unchanged
`equity.next_session_close.return_gt_zero/1.0` target, does **one separately
identified sigmoid transform of one fixed Logistic artifact** improve proper
probability scores relative to its raw outputs and the unchanged BaseRate
benchmark, with acceptable calibration diagnostics on later observations?

Three questions must be reported separately:

| Question | Meaning | Permitted inference |
| --- | --- | --- |
| A. Calibration | Among predictions near P, is observed event frequency near P? | Compare with Ground Truth, not with BaseRate. Reliability diagnostics do not prove calibration everywhere. |
| B. Probabilistic quality | Are paired Brier/log-loss differences favorable with adequate uncertainty/support? | Primary scientific decision; better point scores alone are insufficient. |
| C. Discrimination | Do probabilities rank positive versus zero outcomes? | Secondary description; a monotone recalibration is not new ranking information. |

Proper scores assess probability quality, not calibration alone. The distinction
is motivated by [Gneiting and Raftery's scoring-rule paper](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf).
These are probability-research questions, not P&L, trading recommendation,
execution, causal effect or assurance of profitability. Results generalize only
to the named subject, target, data basis, periods and fixed artifacts.

## 3. Existing owners, real implementation limits

| Responsibility | Frozen implementation to reuse | FF-2 extension obligation, not delivered here |
| --- | --- | --- |
| Common inference and identity | [neutral contracts/runner](../src/tiaf/forecasting/inference_contracts.py), [legacy adapters](../src/tiaf/forecasting/forecaster_adapters.py) | Explicit adapter with exact request/descriptor/observation bindings; no family branch in common contracts. Native Logistic currently dispatches its four original development folds. |
| Logistic numeric reference | [artifact reconstruction](../src/tiaf/learning/forecast_artifacts.py), [native generation](../src/tiaf/forecasting/logistic_forecasts.py) | New versioned adapter applies the single pinned model to admitted later inputs; do not alter original year-to-model routing. |
| Training / model identity | [FLC-2 records](../src/tiaf/learning/forecaster_training.py), [service](../src/tiaf/learning/forecaster_reference.py), [authority](../src/tiaf/learning/forecaster_authority.py) | Existing executable service admits compiled synthetic recipes only. No empirical grant is inferred. Base-model fits remain zero; a calibrator fit needs a separate bounded Learning capability/grant. |
| Optimization | [FLC-3 orchestrator](../src/tiaf/learning/optimization.py) | Retain recorded objective/selection separation; do not run its synthetic C/intercept search for FF-2. There is no calibration grid. |
| Calibration | [FLC-5 identities](../src/tiaf/learning/calibration_contracts.py), [apply/replay](../src/tiaf/learning/calibration.py) | Fit is proposal-only; executable transform is an authored five-probability synthetic table. Learned Logistic fitting/application requires additive versioned codecs/adapters, not relaxing the old literals. |
| Calibrated output semantics | [native probability contract](../src/tiaf/forecasting/contracts.py), FLC-5 separate raw/calibrated fields | `BinaryProbabilityOutput.calibration` is literally RAW, including in the neutral result. Do not put q in that shape and mislabel it RAW. A separately versioned wrapper-result projection must preserve p, q and calibration provenance/qualification separately, leaving the frozen raw codec unchanged. |
| Model diagnostics | [FLC-4 owner](../src/tiaf/learning/forecaster_diagnostics.py) | Preserve descriptive coefficients/preprocessing and distinguish Evaluation's calibration diagnostics from a fitted candidate. |
| Independent Evaluation | [FLC-6 contracts](../src/tiaf/evaluation/forecast_normalization_contracts.py), [normalization](../src/tiaf/evaluation/forecast_normalization.py), [loss/block kernels](../src/tiaf/evaluation/forecast_comparison_metrics.py) | Executable profile is authored-synthetic-only, one/two participants. Add an explicit qualified FF-2 profile; never disguise empirical rows as synthetic or edit frozen FF-1 policy. |
| Ground Truth | [endpoint arithmetic / journal](../src/tiaf/evaluation/forecast_truth.py), [historical journal projection](../src/tiaf/evaluation/forecast_research_truth.py) | Reuse truth owner, strict comparator and revisions; add any new period/profile admission at the edge, not a second labeler. |
| Persistence / lifecycle | [custody](../src/tiaf/learning/forecaster_custody.py), [lifecycle](../src/tiaf/learning/forecaster_lifecycle.py) | Same ResearchForecastStore engine and immutable refs. Recorded review events are not an authenticated activation service. |
| Provenance / replay | [bounded DAG](../src/tiaf/forecasting/lifecycle_provenance.py), [replay owner](../src/tiaf/forecasting/lifecycle_replay.py) | Neutral recorded replay exists; arbitrary neutral numerical reconstruction is UNSUPPORTED. Supply a specific pinned verifier/captured closure for this adapter, never a dynamic loader. |

FLC establishes architecture readiness, not an already executable empirical
calibration workflow. Retain its optional-capability segregation, immutable
requests/results, tuple collections, versioned identity and fail-closed absence.
No second training service, registry, truth journal, metric engine, replay store
or approval authority. No production family is added.

## 4. New identity and fixed lineage

Proposed identifiers follow the existing `LogicalId` / `ForecasterKey` pattern;
they are reserved documentation names, **not registered implementations**:

| Object | Proposed identity / immutable dependency |
| --- | --- |
| Experiment | `experiment:ff2-reliance-sigmoid-001` |
| Candidate | `candidate:ff2-reliance-logistic-sigmoid-001` |
| Raw adapter | `forecaster:ff2-logistic-reference`, implementation `ff2.reference.1` |
| Source native forecaster | `forecaster:logistic-regression`, implementation `1.0`; historical lifecycle remains EXPERIMENTAL |
| Raw source artifact | FF-1 **2022 development-fold** model `7cbe4f2b14a72ae5e2af40c535710f1695687b81786f0c69efd271b50442a5d2` |
| Its scaler | `39e888ce1789405f4bdc9fa704e0f6ac43adfc5aaade55bc211d5c9f0986eb62` |
| Native parent training run | `f26605528584a68449396da9dea1a3e28d6e2295f355a7085887e5adedc94406` |
| Calibrator | `calibrator:ff2-logistic-sigmoid`, family `sigmoid-logit`, implementation/artifact adapter `ff2.sigmoid.1` |
| Calibrated root | `forecaster:ff2-calibrated-logistic`, implementation `ff2.calibrated.1`, CHALLENGER / EXPERIMENTAL |
| Composition | `composition:ff2-reliance-logistic-sigmoid-001`; immutable wrapper edge to the exact raw source and calibrator |

**Why that model, not the fifth fold?** It is the latest existing artifact that
leaves one full known year for calibration and two later full known years for
development validation without another base fit. Selection uses calendar
structure, not observed model scores. The fifth-fold model trained through 2024
would contaminate calibration on 2022–2024. Its consumed 2025 results are not an
admissible calibration set. No alternative model is tried if this choice fails.
The cost is a deliberately old fixed base; drift and limited relevance must be
reported, not repaired by an unannounced refit.

```text
Frozen native training run → exact 2022 model + scaler (read-only lineage)
                                      │
qualified features → FF-2 raw adapter → raw p and source capture ───────┐
                                      │                             │
known 2022 raw p + Ground Truth → Learning calibrator fit             │
                                      │                             │
                       separately sealed calibrator                 │
                                      │                             │
later raw p → pinned wrapper → calibrated q + distinct capture       │
                                      └──────────────┬──────────────┘
                                            independent Evaluation
                                      ← same-population BaseRate + truth
                                                     │
                                       custody / lineage / offline replay
                                                     │
                                           NO automatic activation
```

Store p and q separately. A wrapper result pins source forecast, model, scaler,
native training identity, calibration population, fit request/execution/result,
target/profile, experiment and composition. The raw adapter uses the existing
neutral runner. Calibrated output uses the additive wrapper-result codec within
the same Forecasting/Learning owners, not a disguised raw neutral result or a
new family-specific branch. Fitted/transformed does not mean scientifically
qualified: that distinction must survive Evaluation and replay. Calibration training is **not** a
rewrite of the base training record. Changes to any dependency create a new
candidate; no mutable `latest` alias. Package `0.1.0`, contract `1.0`, research
schema `2.0`, protocol version and adapter/model versions remain distinct.

## 5. Data availability, rights and exposure classification

The [complete inventory and permission matrix](TIAF_A7_FF2_0_BASELINE_DATA_RIGHTS_AND_READINESS.md#data-and-rights-inventory)
is part of this protocol's admission basis. It distinguishes physical custody,
scientific exposure, historical permission and proposed FF-2 purpose.

Current local source: 2,045 RELIANCE daily rows, 2017-11-01–2026-01-30,
acquired **2026-09-21T12:07:50.995917+05:30**; adjusted retrospective research,
not CAPTURED_AS_KNOWN. Rights remain **UNVERIFIED / WARN_ONLY /
ADMITTED_WITH_WARNING** under the historical FF-1 policy. No FF-2-specific
data-use/calibration-fit grant or qualified protected-final dataset was found.
The historical grant is not transferable merely because bytes are readable.
There is no claim of verified licensing or permission to redistribute data.

| Period | Scientific status / proposed role |
| --- | --- |
| 2017-11-01–2017-12-29, 42 rows | Known historical warm-up/support, not independent evaluation |
| 2018–2021 | TRAINING provenance of the selected fixed artifact; not new training permission |
| 2022, 248 scheduled source rows | DEVELOPMENT / proposed CALIBRATION, subject to exact qualification and new use authority |
| 2023, 246 rows | DEVELOPMENT / proposed candidate-selection validation block; 225 previously qualified feature/label pairs, not newly evaluated FF-2 results |
| 2024, 249 rows | DEVELOPMENT / proposed second forward validation block; 248 previous pairs, with the origin targeting 2025 excluded |
| 2025, 249 rows | CONSUMED FF-1 protected evidence; **excluded from every FF-2 fit, selection, validation, benchmark-support and final population** |
| 2026-01-01–2026-01-30, 20 rows | Existing later-vintage historical context, no protected designation; excluded from v1 for all numeric research roles |
| After 2026-01-30 in the inspected qualified source | UNAVAILABLE; no independent corpus or issuance history is asserted |
| Future after actual candidate/protocol freeze | Proposed PROTECTED_FINAL_EVALUATION accrual, currently UNAVAILABLE, no forecast/data acquisition authorized |
| FLC authored/synthetic data | ENGINEERING only; no empirical calibration or scientific acceptance evidence |

TUNING of coefficients, scaler, features, base hyperparameters, calibrator family,
bins or trading thresholds is **NONE / FORBIDDEN**. Calibration parameter
estimation on its named partition is the only proposed fit. Known data cannot
become unseen through new IDs, a re-download or a new output transformation.

## 6. Chronological design and clock safety

Choose **one fixed model → one calibration block → two forward development
blocks → prospective protected final accrual**. Random IID CV is forbidden.
No expanding/rolling base refits, nested hyperparameter search or pooling of
different base artifacts behind a single calibrator. This is simpler than nested
temporal model selection because there is one admitted method/configuration.
The temporal principle is that future observations cannot construct earlier
forecasts; see [Hyndman and Athanasopoulos](https://otexts.com/fpp3/tscv.html).

| Stage | Exact scope / ordering | Permitted use |
| --- | --- | --- |
| Base training, already complete | Native 2022 artifact: 2018-01-01–2021-12-29 train origins, 968 rows; cutoff/embargo 2021-12-31T09:15:00+05:30 | Read-only model/scaler/provenance; zero new coefficient/scaler fits |
| Calibration | Qualified 2022 origins with target and assumed label availability strictly before 2022-12-30T09:15:00+05:30 | Fit the one sigmoid once; exclude the whole 2022-12-30 embargo origin and any crossing/maturing dependency |
| Selection validation V1 | Qualified 2023 origins, retaining existing action exclusions, ending before any 2025 dependency | Evaluate frozen p/q/BaseRate; no calibration refit |
| Validation V2 | Qualified 2024 origins with reference **and target** before 2025-01-01 | Same frozen artifacts; V1 and V2 jointly drive a predeclared proceed/stop rule |
| Candidate freeze | After both known validation blocks and independent review | Freeze all artifacts, source permissions, target/basis, decisions, implementation/lock, protected schedule and accounting before prospective predictions |
| Final | First 500 scheduled eligible-subject origin slots strictly after that actual freeze; one whole origin-session embargo first | Accrue sealed contemporaneous inputs/predictions/outcomes; one final opening after all outcomes mature or time out |

V1/V2 are not independent final evidence: their source data were already
inspected during FF-1. Calling V2 “validation” does not hide that exposure.
Candidate selection is a deterministic **proceed or stop**, not a choice of
alternative methods or a choice of which validation year to report.

The exact calibration membership must be derived and sealed by Evaluation's
qualification owner **before fitting**. Source row counts are not fit counts:
purge/embargo reduce the 248 calibration candidates. No new membership/labels
were computed in this pass. Minimums in §8 must be met after all exclusions.

Important adapter constraint: previously saved 2023/2024 Logistic probabilities
used different year-specific models. **Do not reuse them as the FF-2 raw arm.**
Later authorized generation must use the selected 2022 model/scaler on already
qualified captured inputs for every FF-2 origin, with new request/output IDs.
No old forecast or year-dispatch function is overwritten.

Historical fit-knowledge cutoffs and model/calibrator evidence dependencies must
precede the simulated forecast cutoff. Actual computation, acquisition and fit
times remain their real later times; no backdated `issued_at`. Feature windows
may include prior past-only bars; labels crossing partition boundaries are
purged. Do not erase valid trailing-feature history merely to make rows disjoint.
The adjusted 2026 source vintage prevents a claim of genuine historical PIT
tradability even when split-time leakage guards pass.

For prospective evidence, freeze the same target, five-feature formulas/order,
provider-defined volume limitations and compatible adjusted price basis, but
capture each actual available vintage at issuance. Require common-basis qualified
truth endpoints, action/calendar evidence, source publication/acquisition/admission
clocks and historical preprocessing pins. Do not revise stored features after a
later provider adjustment. If this prospective basis cannot be qualified, remain
HOLD: do not switch silently to unadjusted/total-return labels or simulations.
All datetimes use aware `ZoneInfo("Asia/Kolkata")`, JSON `+05:30`; naive times reject.

## 7. One allowed calibrator; no method shopping

Admit only **two-parameter sigmoid-on-logit recalibration**:

```text
z = logit(clamp(p, 1e-15, 1 - 1e-15))
q = sigmoid(a + b*z)
```

This is a Platt-style logistic calibration, not a rerun of the base five-feature
Logistic estimator. A different map (for example sigmoid directly on p rather
than its logit) is not the same configuration. Preserve original p; clipping is
an explicit transform/metric policy, not overwriting evidence.

Predeclared fitting specification: unweighted binary log-loss on CALIBRATION
only, intercept included, no regularization, no class balancing, no data
augmentation; deterministic initial `(a,b)=(0,1)`, one optimizer configuration,
at most 1,000 iterations and gradient infinity norm ≤1e-8 for convergence.
The exact implementation/dependency lock and numerical verifier must be reviewed
and pinned in FF-2.1 before empirical access. Nonconvergence, separation,
nonfinite parameters or `b <= 0` rejects the fitted candidate; no rescue solver,
penalty, clipping grid, reversed ranking or second attempt. The candidate's
strictly increasing map preserves ranking apart from explicitly reported
floating-point saturation/clipping ties.

Sigmoid assumes a simple shape for the calibration distortion; it may underfit.
Isotonic is flexible but is excluded from v1 because the available single-year
calibration sample is small. The documentation's approximate 1,000-sample
caution is a heuristic, not a universal market-data threshold or a guarantee for
correlated observations. [Official calibration guidance](https://scikit-learn.org/stable/modules/calibration.html)
and [Niculescu-Mizil and Caruana](https://www.cs.cornell.edu/~alexn/papers/calibration.icml05.crc.rev3.pdf)
inform that deliberately narrow choice. No isotonic, beta, temperature, spline
or ensemble alternative is tried after seeing v1 results.

The above is a specification, **not implemented or fit here**. A diagnostics
regression used to estimate calibration slope/intercept is an Evaluation-only
summary, never an alternate calibrator or candidate parameter update.

## 8. Development selection and finite budget

Proposed v1 policy values below are generic engineering/scientific guardrails,
not thresholds optimized from FF-1 scores. Minimums are screening floors, not a
power calculation or proof of statistical independence. All must be ratified
with the protocol before a fit; after results, do not relax them.

1. CALIBRATION: at least 200 admitted pairs, at least 50 of each class, finite
   varying raw probabilities and complete provenance. Failure means
   INSUFFICIENT_EVIDENCE; do not borrow from V1/V2/2025.
2. V1 and V2: at least 150 common three-arm pairs, 30 of each class, 80% of the
   declared scheduled origins paired, and 20 complete nonoverlapping five-slot
   blocks per year. Retain masks for unavailable observations.
3. Primary selection objective: pooled mean Brier, uniformly weighted by unique
   common observations (not the unweighted average of annual scores).
   Proceed only if calibrated-minus-raw pooled Brier is **< -1e-6**, and its
   per-year difference is negative in both V1 and V2.
4. Relative to **each** raw and BaseRate comparator, neither year's Brier may
   worsen by >0.02 or log loss by >0.05; pooled log-loss worsening must be ≤0.01.
   These absolute loss-scale margins are not trading utility or profitability.
5. Apply §10's calibration guardrails on pooled validation. Publish both annual
   reports and uncertainty even when a gate fails. Development intervals are
   descriptive, not a protected-test acceptance claim.
6. Tie/no improvement (Brier difference ≥-1e-6) selects **no calibrated
   challenger**; keep the simpler untransformed reference for reporting and
   BaseRate as benchmark. Do not promote raw Logistic by this fallback.

One calibration fit, one configuration, one selection evaluation bundle, no
post-selection refit on calibration+validation. Proposed fit bound: 60 seconds,
512 MiB, one numeric thread, one durable attempt. At most 4,096 declared origins
per corpus and two pairwise comparisons on a common three-arm mask; keep existing
store/DAG bounds. Diagnostics do not consume a second candidate-fit slot but
must be individually bounded/pinned. No FLC-3 six-trial campaign is run.

Only training provenance, CALIBRATION and known V1/V2 may be inspected for this
selection. Forbidden: all 2025 numeric records, January 2026 numeric rows, future
protected forecasts/outcomes/score summaries, hidden alternate configurations,
period/feature/threshold/model shopping. Hash-only old-record verification is
not a numeric research use.

## 9. Comparison hierarchy and metrics

| Arm | Reporting role | Authority |
| --- | --- | --- |
| `forecaster:historical-base-rate` (primitive/policy 1.0; existing empirical binding 2.0) | BENCHMARK | Preserve each version's exact identity and unchanged formula/policy; no authority gained |
| Pinned FF-2 raw adapter / source Logistic artifact | REFERENCE LEARNED FORECAST (Evaluation SUBJECT) | Source stays CHALLENGER / EXPERIMENTAL, not promoted |
| New calibrated root | FF-2 CHALLENGER | Research only, never self-approved |

Retain the existing unsmoothed `k/n` BaseRate with exactly 20 last scheduled
transitions at a declared fit cutoff, minimum 20, no backfill/smoothing. Retain
annual development-block support cadence and original 2023/2024 support pins.
For the prospective final, pin one support artifact before the first origin and
keep it fixed for all 500 slots; never use current-target/final outcomes as new
benchmark support. The change of final period needs new, qualified pre-freeze
support evidence, not a new estimator. Invalid support means absence/HOLD, not
weakening the benchmark. [The existing empirical BaseRate adapter](../src/tiaf/forecasting/research_baserate.py)
also has FF-1-specific fold admission; extend the admitted FF-2 witness/period
profile separately, without relabeling empirical data as FF-0 synthetic support.
Its 2.0 research binding is distinct from the primitive 1.0 descriptor; do not
collapse these version identities in lineage. Pin any new FF-2 binding adapter
separately while retaining the source benchmark and policy identities.

FLC-6 allows two participants, not three-way ranking. Produce two independently
owned paired reports: **calibrated minus raw**, **calibrated minus BaseRate**.
Both use the **same intersection of three valid forecasts and one qualified
truth** on an identical declared population, with complete per-arm missingness
accounting. Keep each arm's broader marginal diagnostics separately; do not
present unlike denominators as paired improvements.

| Metric | Definition / role | Limitation |
| --- | --- | --- |
| Brier | Mean `(p-y)^2`; primary selection and final superiority endpoint | Probability quality combines calibration and resolution; not calibration alone |
| Log loss | Mean negative log probability of observed y; mandatory non-inferiority gate; existing epsilon 1e-15 only in scoring | Sensitive to confident errors; report clipping/endpoint counts |
| Reliability | Fixed ten bins `[0,.1), …, [.9,1]`, mean p, observed frequency, counts; bins <20 LOW_SUPPORT, empty bins null | Mandatory descriptive calibration evidence; no adaptive “nice-looking” bins |
| Calibration-in-the-large | Mean p − mean y, plus intercept-only logistic diagnostic with logit(p) as offset | Mean error can hide conditional miscalibration; intercept target zero |
| Calibration slope | Evaluation-only fit `logit P(y=1)=alpha+beta*logit(p)`; ideal beta 1 | Weak calibration diagnostic, not proof of a correct whole curve; non-estimable for constant/separated inputs |
| ECE | Sum over occupied fixed bins of `(n_bin/N)*abs(mean p − frequency)` | Descriptive, bin-dependent and noisy; include low-support contributions with warning, not silently drop them |
| MCE | Maximum occupied-bin absolute gap, with bin support shown | Very unstable on tiny bins; never sole rejection/promotion criterion |
| ROC-AUC | Rank discrimination, ties half credit | Not calibration; monotone transform should not create ranking gains |
| PR-AUC | Report specifically average precision (step-weighted precision over recall changes), not trapezoidal area | Prevalence-dependent; comparisons need the same labels/denominator |
| Discrimination slope | Mean p among y=1 minus mean p among y=0 | Probability spread, not the calibration slope; depends on prevalence/sample |

Brier/log-loss meanings follow [proper-score theory](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf).
Intercept/slope complement a curve but do not establish all forms of calibration;
see [Van Calster et al.](https://pmc.ncbi.nlm.nih.gov/articles/6912996/).
No clinical sample-size rule is imported as a financial guarantee. A constant
BaseRate may have valid scores but an unidentifiable diagnostic slope; report
NOT_ESTIMABLE, not zero or a forced candidate failure. No diagnostic is a forecast.

## 10. Final scientific criteria and outcome semantics

No qualified independent final evidence exists today. These rules are fixed
for a later **authorized**, prospective final, not applied to known history.

Final population: 500 scheduled origin slots after freeze/embargo; no extension
until significance. Require ≥400 common pairs, ≥80 of each class, ≥80% coverage,
and ≥40 complete nonoverlapping five-slot blocks. Each fixed chronological half
(slots 1–250 / 251–500) needs ≥150 pairs and ≥30 of each class. No class/period
balancing or removal based on whether a prediction was right.

Use the existing paired noncircular moving-block convention: length 5, 5,000
replicates, PCG64/seed 1729, linear quantiles .0125/.9875, same resampled indices
for losses and comparisons, original missing masks, no wrap or blocks spanning
the two halves. A zero-pair replicate yields NOT_ESTIMABLE, no redraw. Version
the FF-2 policy; do not alter the FF-1 kernel/policy or call its final runner.
The 97.5% two-sided intervals are conservative for the two predeclared Brier
comparisons; all gates below are conjunctive, not a menu of favorable tests.
Five-slot dependence is an assumption, not proof against longer dependence or
regime change. Invalid dependence assumptions require an independent validity
finding/new protocol before opening, not result-driven block-length searches.

**Scientific acceptance requires all of the following:**

- Valid authority, exact identities, chronology, support, complete custody and
  reproducible captured/pinned outputs; no protected selection exposure.
- Calibrated-minus-raw **and** calibrated-minus-BaseRate Brier interval upper
  bounds <0, with pooled mean improvements at least 0.001 against each. The
  0.001 minimum is a modest absolute-score practical floor, not a claim of power.
- Log-loss difference interval upper bounds ≤0.01 against **each** comparator.
  Log loss need not independently show superiority; this is non-inferiority.
- Each chronological half meets the development non-degradation limits 0.02
  Brier / 0.05 log loss against each comparator. No hiding a materially harmed half.
- Pooled calibrated `abs(mean q − mean y) ≤0.05`; ECE ≤0.08 and no more than
  0.02 worse than raw ECE. At least 80% of pairs occupy bins with ≥20 observations.
  Publish the entire reliability table and all diagnostics. These coarse
  guardrails do **not** establish universally correct conditional probabilities.
- No unexplained ranking change: ties/clipping and numeric tolerances must
  account for any difference. No new diagnostic fitting feeds back into q.

Improved proper scores plus acceptable diagnostics can qualify the candidate
without claiming that calibration superiority itself is statistically proven.
Report question A separately as DESCRIPTIVE_SUPPORT / MIXED / NOT_ESTIMABLE;
report B from paired evidence and C descriptively. ECE alone can never qualify.

| Outcome / finding | Meaning |
| --- | --- |
| INVALID_EXPERIMENT | Leakage, wrong identities/target, authority breach, tampered lineage, unauthorized retry or post-result adaptation; no scientific win/lose claim |
| INSUFFICIENT_EVIDENCE | Valid but unavailable/undersupported/non-estimable final evidence, or adequate evidence with nondecisive intervals; not rejection merely because improvement is unproven |
| REJECTED | Valid adequate evidence decisively rules out the required improvement (Brier interval lower bound ≥-0.001 against either comparator), demonstrates material log-loss degradation (lower bound >0.01), or fails predeclared stability/calibration quality gates |
| ACCEPTED | All scientific gates pass, independently reviewed within the stated research scope |
| PROMOTION_ELIGIBLE | A **separate review finding**, possible only after ACCEPTED plus prospective provenance/replay/health/scope qualification; not a replacement statistical classification or activation |

Precedence: INVALID first; inadequate support/estimability next; then all-pass
ACCEPTED; otherwise decisive rejection/gate failure; remaining uncertainty is
INSUFFICIENT_EVIDENCE. Preserve multiple reasons. Development failure closes or
holds this proposal without consuming a final slot. It does not reopen FF-1.
Actual approval, COLD binding, public exposure and A4/A5/A6 influence remain
forbidden here even if a future report says ACCEPTED or PROMOTION_ELIGIBLE.

## 11. Future final evidence and one-way governance

No calendar dates are invented for a future unacquired corpus. Before accrual,
an external authority must pin actual freeze time, the qualified exchange
schedule/start, first 500 origin slots, rights, outcome due-time policy and
custodian. Budget duration is count-based (~two trading years, illustrative,
not a promised completion date). No rolling significance checks or early success.

After the first whole-session embargo, emit all three research forecasts
before each target opens; retain raw inputs/vintages, all absence records and
immutable predictions. Source acquisition and independent Ground Truth maturation
are separate from final model evaluation. Protected predictions and outcomes go
to custody; selection operators receive only operational counts/errors, not
numeric probabilities, class summaries or scores. Hash-only integrity checks
are allowed. Market observations being public does not make them unavailable to
humans: any prohibited manual candidate-specific outcome/score inspection is a
recorded exposure breach, not something a directory name solves.

Truth deadline is target close + seven calendar days. At that fixed deadline,
resolve according to qualified journal evidence or mark unavailable; no fabricated
label or indefinite wait for convenient outcomes. Pin the selected journal revision
at final closure; later revisions append audit history, never overwrite the
scientific result. The exact schedule/endpoints/basis must be qualified before
accrual. No new data download or shadow run is authorized by this document.

Proposed ledger sequence:

```text
PROPOSED → RIGHTS/PROFILE_ADMITTED → DEVELOPMENT_COMPLETE
    → CANDIDATE_AND_PROTOCOL_FROZEN → ACCRUING_PROTECTED
    → SEALED_COMPLETE → EXECUTION_CLAIMED (irreversible)
    → CONSUMED + COMPLETE | CONSUMED + FAILED/INCOMPLETE
    → SCIENTIFIC_CLOSURE
```

Final evaluation maximum executions **1**. Consume a durable exact-request
claim before numeric outcome access; missing claim denies opening. A crash after
claim leaves consumed/incomplete, not permission to delete the claim, change the
directory or retry. Completed immutable evaluation may be displayed/recorded-
replayed without re-scoring or fitting. Numerical reruns that consume a new
execution are not implied by replay permission.

After any final exposure: no candidate/calibrator refit, threshold/metric/window
change, additional-method attempt or reclassification of final evidence as
unseen. A genuinely different later study needs new identity, authority and
independent evidence; past exposed evidence remains exposed. FF-1's ledger is
never part of this new state transition.

## 12. Required artifacts and exact lineage

Use additive sealed records/codecs over the existing custody owner; these are
required future artifacts, not claims that the FLC synthetic codecs admit them.

| Artifact | Required contents / owner |
| --- | --- |
| Protocol + evidence-use manifest | This design, exact parameters, source rights/exposure classifications, version and externally acknowledged authority; Learning/governance refs |
| Candidate / calibrator specification | Experiment/key/composition, native model/scaler/training pins, one method/configuration, scope; Learning |
| Qualified population + split membership | Scheduled IDs, disjoint purposes, dependency/purge/embargo, clocks, inclusion/absence, input/schema/profile/vintage hashes; existing qualification owner |
| Fit request → execution → result | Calibrator-only input and grant, one attempt, resources/lock/code, parameters, convergence/status; same Learning ownership/persistence pattern |
| Forecast captures | Immutable raw and calibrated output IDs, source input/observation/target/mode/composition; Forecasting |
| Development evidence / selection record | Two paired reports with shared denominator, per-year/pooled diagnostics, all failure reasons, recorded deterministic selection; Evaluation then Learning selection |
| Candidate / final freeze manifest | All source/model/calibrator/code/dependency/policy pins, prospective schedule, custodian, grants; external review |
| Final protocol / execution / evaluation / ledger | Four distinct semantic fingerprints, population and sampled-index seals, one-way consumption and immutable result; existing Evaluation/governance owners |
| Provenance / replay closure | Captured REQUIRED_BYTES versus IDENTITY_ONLY, typed dependency graph, recorded result and supported pinned numerical verification; existing FLC-7 owner |

Calibrator identity alone is not calibration-data custody or permission. Store
private data/artifacts locally under a new FF-2 research corpus, never the FF-1
artifact path. No secrets, licensed raw data or mutable model pickle in Git.
Canonical semantic fingerprints and file-byte hashes are both retained but are
not interchangeable; a fingerprint authenticates neither a person nor a grant.

## 13. Machine-checkable acceptance invariants for FF-2.1 onward

These are future tests/admission obligations, not assertions of code added today.

| ID | Required invariant / negative test |
| --- | --- |
| I01 | Four FF-1 fingerprints and all 78 pins match; FF-0 runtime and FLC baseline paths unchanged by this protocol pass |
| I02 | FF-1 2025 remains CONSUMED, executions=1, refit=false; wrong-year/cross-2025 sources reject before numeric decode |
| I03 | FF-2 experiment/candidate/protocol IDs differ from FF-1; historical grants never authorize FF-2 |
| I04 | Every FF-2 raw output uses the selected exact model/scaler; passing an original 2023/2024 model/output rejects |
| I05 | Raw capture bytes survive unchanged; calibrated output has a distinct ID, pins source p, calibrator and composition |
| I06 | Target, subject, five ordered features, price basis, source/vintage and realization mode match all participants/truth |
| I07 | Base training and calibrator-fitting dependency availability precedes simulated cutoffs; actual fit/computation/acquisition clocks are not backdated |
| I08 | No calibration label/target crosses fit cutoff; all fit IDs disjoint from validation/final IDs; final not selectable by purpose relabeling |
| I09 | One method/config/fit attempt; no implicit base fit, automatic CV cloning, hidden optimizer or post-selection refit |
| I10 | Same three-arm intersection and original scheduled masks feed both pairwise reports; unique observation IDs, missing ≠ zero |
| I11 | Exact BaseRate identity/policy retained; no optimized support window, smoothing or final-outcome updates |
| I12 | Fixed resource/sample/bin/interval/decision profiles, deterministic tie/stop behavior, no final count extension based on performance |
| I13 | Protocol/candidate freeze precedes first prospective forecast; irreversible final claim before numeric opening, max execution=1 even after failure |
| I14 | No post-result parameter/policy/candidate mutation; acceptance/selection fields cannot set approval/activation |
| I15 | Replay works without network, fit, current registry aliases or store writes; missing bytes UNAVAILABLE, absent numeric verifier UNSUPPORTED, broken lineage MISMATCH |
| I16 | Frozen aware contracts accept list/JSON reconstruction, emit arrays, reject mutation/naive clocks, normalize Asia/Kolkata |
| I17 | Synthetic FLC grants and authored-table codecs reject empirical FF-2 inputs unchanged; new admission/version required |
| I18 | Only the exact authorized external journal revisions supply labels; no calibrator/forecaster labeler or outcome-derived feature |
| I19 | q cannot serialize as native `BinaryProbabilityOutput(calibration=RAW)`; additive wrapper captures retain distinct p/q, component identity and unqualified-versus-qualified meaning; frozen raw JSON remains identical |

## 14. Finite delivery plan

Model recommendations below are task-specific engineering judgments. Retain the
requested **GPT-6 Astra**: Extra High (`xhigh`) for protocol/scientific decisions,
High for bounded implementation. Official documentation confirms those effort
options; it does not certify this experiment or guarantee account availability.
[OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-6-astra).

| Phase / recommended model | Purpose and deliverables | Tests and acceptance | Explicit non-goals |
| --- | --- | --- | --- |
| **FF-2.0 — GPT-6 Astra Extra High** | Protocol, inventory, permission/exposure matrix, source-seam gap map, finite plan and readiness decision | Clean/synchronized/tagged FLC preflight; hashes/pins; complete numerical policy and clear unresolved grants; links/scope | No fitting, implementation, execution or consumption. Current pass stops here. |
| **FF-2.1 — GPT-6 Astra High** | Additive calibration fit/apply and calibrated-output codecs, exact fixed-model adapter, empirical BaseRate/Evaluation profiles and pinned verifier over existing owners; retain synthetic restrictions | I01–I19 adversarial fixtures; wrong-model/cross-year/duplicate-attempt tests; toy numerical oracle, list/JSON round-trip, replay offline; focused/full tests, compileall, Ruff, mypy, diff check | No empirical run, base retraining, new family/registry/truth engine, production activation. Entry requires reviewed scope/authority resolution or explicit synthetic-only carve-out. |
| **FF-2.2 — GPT-6 Astra Extra High** | Exact known-development membership, one authorized calibrator fit, p/q/BaseRate captures, V1/V2 scores and deterministic selection record | Actual rights/profile/grant and frozen dependency pins; one attempt; no 2025 decode; common masks, all negative cases, reconstruction ≤1e-12, raw-byte preservation; no fit if entry fails | No final exposure, alternative method/model, refit after validation or “independent” claim for known years |
| **FF-2.3 — GPT-6 Astra Extra High** | Independent candidate/final-protocol freeze; qualified prospective accrual; one final evaluation after fixed maturity | Exact grants/schedule/basis, captured-as-known and timely issuance; sealed custody; freeze/one-shot fault injection tests; support/interval gates | No invented future corpus, early stopping, automatic collection authority, repeated holdout or candidate changes |
| **FF-2.4 — GPT-6 Astra Extra High** | Independent scientific closure, preservation check, immutable decision/limitations and optional promotion-eligibility recommendation | Read-only reconciliation of protocol/execution/evaluation/ledger, denominators, diagnostics, replay, uncertainty and all exposed trials | No result-driven rescue, approval by metrics or requirement that Logistic win |
| **FF-2.5 — GPT-6 Astra High** | Optional separately authorized prospective-health/shadow, approval/COLD selection and rollback integration only if scientific qualification holds | Explicit reviewer/activation authority, shadow/expiry/denial/revocation, wrong-binding and regression tests; separate public capability acceptance if requested | Not automatically scheduled; no HOT/autonomous promotion, trading or broker integration |

FF-2.3's final-accrual substeps are conditional milestones, not a pretense that a
two-year prospective sample can be completed in an implementation turn. FLC
already supplies lifecycle foundations; no competing full lifecycle project is
created. Existing conditional FF-3…FF-7 and A8 → A9 → A10 ordering are unchanged.

## 15. Risks, open gates and status

| Risk | Control / honest residual |
| --- | --- |
| Fit/validation leakage | Exact model chosen chronologically; fit-only labels, purged boundary, fixed dependencies; later-vintage historical adjustments still limit PIT claims |
| Method/period shopping | One sigmoid, one source model, one fit, two mandatory known validation years, no fallback candidate |
| Small sample / overfit | Two calibration parameters, minimum class support; isotonic excluded; dependent CIs; floors do not guarantee power |
| Stale model / temporal dependence | Fixed old model explicitly disclosed, per-period gates and prospective test; failure does not license retraining |
| FF-1 reopening / false independence | Four hashes/78 pins, read-only history, 2025 excluded, known years never protected; January 2026 not repurposed as a test |
| Rights/prospective basis | Old WARN_ONLY is not new permission; FF-2 use grant and prospective basis/calendar/accrual authority unresolved |
| Self-promotion / optimistic replay | Independent review; eligibility ≠ activation; exact captured bytes and explicit numerical verifier support |

The [readiness record](TIAF_A7_FF2_0_BASELINE_DATA_RIGHTS_AND_READINESS.md#readiness-decision)
owns the current blocking actions. Lack of a completed future final sample alone
does not prevent synthetic engineering. However, this pass does not infer a new
empirical admission policy or implementation authorization from FLC's synthetic
capabilities. A narrowly scoped synthetic-only FF-2.1 request can be authorized
separately without claiming that data rights or final evidence are resolved.

```text
FF2_PROTOCOL_DEFINED = YES
FF2_DATA_RIGHTS_RESOLVED = NO
FF1_PRESERVED = YES
FLC_PRESERVED = YES
FF0_PRESERVED = YES
READY_FOR_FF2_IMPLEMENTATION = NO
HOLD_FF2_IMPLEMENTATION
```

The hold is on unresolved FF-2 admission/authority and prospective qualification,
not a failed FLC freeze or a new FF-1 scientific finding. No implementation,
calibration fit, runtime promotion, final consumption, commit, tag or push occurs.
