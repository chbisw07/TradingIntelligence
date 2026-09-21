# TIAF A7 / FF-1 — Logistic Benchmark and Paired Evaluation Plan

**2026-09-21 research-policy correction:** the
[adjusted-data profile and empirical qualification](TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md)
supersede the unadjusted-only, source-text-exact and captured-history requirements
below **only for this opt-in FF-1 retrospective research profile**. The fresh Dhan
adjusted vintage remains SIMULATED, with assumed close+30m/+5m clocks; actual
acquisition is preserved. Original operational CAPTURED_AS_KNOWN and FF-0 remain
unchanged. The target family, five A2 formulas/schema ID/version, fold boundaries,
support thresholds, no-tuning rule and sealed 2025 holdout are unchanged.
`EMPIRICAL_FITTING_AUTHORIZED = YES` for the pinned qualified dataset; no fitting
was performed. Next: **TIAF A7 / FF-1.2 — LOGISTIC CANDIDATE TRAINING ARTIFACT IMPLEMENTATION**.
The planning and earlier HOLD statements below retain their historical meaning.

Policy follow-up, 2026-09-20: §3.2 now records the approved FF-1.1A COLD rights
revision. Rights evidence remains distinct from policy admission; other
scientific choices are unchanged. Original planning status, validation counts
and then-next text below are historical. The current provisioning queue is in
the [revision record](TIAF_A7_FF1_1A_RIGHTS_POLICY_REVISION_AND_DATA_PROVISIONING.md).

## 1. Decision and authority

**READY_FOR_FF1_IMPLEMENTATION** — 2026-09-19 (Asia/Kolkata).
This is **planning readiness for separately requested FF-1.1 implementation**,
not empirical data qualification, fit authorization, scientific acceptance,
model approval, publication or deployment. FF-1 runtime is **NOT_IMPLEMENTED**.
Empirical fitting is **HOLD** until the explicit gates below pass. No learned
model, including a synthetic Logistic model, was fitted in this planning pass.
Drafting began on 2026-09-15; the resumed pass rechecked the unchanged HEAD,
baseline tags and documentation-only worktree on 2026-09-19.

Exact next prompt:
**TIAF A7 / FF-1.1 — DATA QUALIFICATION AND FEATURE SCHEMA IMPLEMENTATION**.

The question is deliberately small: does one fixed Logistic instrument improve
raw next-session cash-equity probabilities over the retained historical BaseRate
on the same qualified observations? Failure to improve is a valid result. It
does not invalidate FF, justify changing the target, or authorize tuning until
RELIANCE looks attractive. This is not a recommendation or trading policy.

### Checkpoint and governing references

| Item | Verified state / decision |
|---|---|
| Entry worktree | Clean |
| Entry HEAD and `tiaf-a7-ff0-baseline^{commit}` | Both `e5283c9eaa4294bd236186d663335efdf7dab236` |
| FF-0 | All four slices accepted; internal synthetic engineering miniature only |
| A6 tag | `tiaf-a6-baseline` remains `6dc2ff304aae0e87540260b092919bb91e4d4189` |
| Package / existing contract versions | Package `0.1.0`; existing FF-0 schema `1.0`; separate concepts, neither changed here |
| Git recommendation | FF-0 already committed and appropriately tagged; preserve both, do not recreate or move the tag |
| Planning commit | Recommend a separate documentation-only commit after review; none made here |

This plan instantiates the [A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md),
[FF architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md), their
[A7 acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) and
[FF repeat acceptance](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE_REPEAT.md),
and the [FF stage roadmap](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md).
The [FF-0 miniature plan](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md)
and [28-case acceptance](TIAF_A7_FF0_ACCEPTANCE.md) remain historical baselines.
FFT-15/16 and A7's pre-outcome protocol-review gates are instantiated here, not
declared empirically satisfied. No new deferral is needed.

## 2. Scope and subject decision

| Dimension | Frozen FF-1 study choice |
|---|---|
| Subject | **RELIANCE only**, qualified NSE cash equity; dated canonical security mapping, not a provider ticker |
| Target | Existing `equity.next_session_close.return_gt_zero/1.0` |
| Event | `1` iff the qualified next eligible session close is strictly greater than the qualified reference close; equality is `0` |
| Price / unit | Unadjusted authoritative close, positive source-decimal precision; price-return comparison, not total return or executable fill |
| Horizon | One next eligible qualified exchange session, not next weekday or next 24 hours |
| Models | B0 historical BaseRate and one B2 binary Logistic; no additional learned instrument |
| Study | Retrospective, chronological, **SIMULATED**, research-only, raw probabilities |
| Universe expansion | None; insufficient RELIANCE evidence does not trigger index, F&O, other-symbol or sector pooling |

Corporate-action-affected or unqualified reference/target pairs remain
NOT_EVALUABLE under the accepted target. Do not round closes into false ties,
substitute adjusted prices, infer missing closes, or relabel absent evidence as
negative. A later expanded subject study requires a new accepted protocol and
unseen evaluation population; this plan does not claim cross-symbol validity.

## 3. Empirical source, rights and qualification before fitting

### 3.1 Candidate acquisition plan — not a claim that data exists

Candidate source is **the existing Dhan daily historical adapter path** for
RELIANCE NSE cash OHLCV, with retained provider-native captures. FF-1 consumes
local immutable evidence admitted through existing provider-neutral capture
boundaries; it does not add a client, call Dhan from Learning/Evaluation, or
download a dataset in this pass. No automatic Yahoo/other-provider fallback.

Proposed source coverage: **2017-11-01 through 2026-01-31**, inclusive, covering
warm-up and terminal target sessions. Intended reference observations are
**2018-01-01 through 2025-12-31**; test reference years are 2021–2025. These are
scope limits, not assertions of provider retention or qualified coverage.
Qualified NSE-origin session schedules, corporate-action records and dated
security-master identity must accompany bars, with source/version/rights
references. Provider bars alone do not establish these authorities.

Use **CAPTURED_AS_KNOWN**: source availability, acquisition and original trusted
admission of every feature dependency must be no later than its historical
information cutoff. Present-day downloads of historical bars do **not** satisfy
this rule. Later feature computation is permitted only from demonstrably
cutoff-safe retained dependencies using the pinned transformation. Original
capture/admission evidence and today's import/computation timestamps are distinct;
no new import is backdated. The FF-0 synthetic later-acquisition simulation
profile is not an empirical-vintage waiver. If suitable archives do not exist,
stop empirical work; an alternative vintage policy needs separate architecture
acceptance or a separately planned prospective study.

Demand provider-native decimal lexical values or an independently qualified
source-decimal companion for target closes. A normalized floating-point bar
alone is not proof of authoritative decimal precision. Qualify OHLC ordering,
positive prices, nonnegative volume, timestamps, completed-bar status, duplicates,
corrections, missing sessions and symbol mapping. Volume zero is factual data;
zero denominator or missing volume is not a computable volume ratio.
Required rows contain open, high, low, close, volume and qualified session/time
identity. Require positive finite OHLC, `low <= min(open, close)`,
`high >= max(open, close)` and `low <= high`. Retain identical duplicate capture
references but weight each canonical observation once; conflicting duplicates
require a qualified revision choice, otherwise exclude them. Never average
conflicting closes. Sort admitted rows by qualified session order.

### 3.2 Rights gate

**2026-09-20 policy evolution:** the
[FF-1.1A rights-policy revision](TIAF_A7_FF1_1A_RIGHTS_POLICY_REVISION_AND_DATA_PROVISIONING.md)
separates evidence from local-research admission. The data-rights owner supplies
the actual known state for **each** of local research, model training,
derived-feature/model retention, retained source evidence for audit/replay, and
evaluation use. Record licensor, dataset/version,
account or entitlement reference without credentials, permitted users/machines,
retention/expiry and redistribution restrictions. Availability, a working API,
personal access, or public visibility is not a training/retention license.

The COLD default is **WARN_ONLY**: `UNVERIFIED` / `AMBIGUOUS` may proceed with an
explicit warning, never a claim of rights approval. `ENFORCE` blocks those states;
`DISABLED` records non-enforcement and keeps the evidence. Explicit
`VERIFIED_DENIED` blocks under **all three** policies: no override authority is
implemented. Evidence/source identity mismatches remain hard provenance failures.
The five legacy assertions remain readable; `NOT_QUALIFIED` means ambiguous, not
proof of explicit denial. The previous enforced HOLD is preserved as history.

Rights remain **UNVERIFIED** for the absent empirical dataset. Policy permission
to proceed is not legal permission, redistribution/publication authority, a
retention change or a learning grant. Revocation/retention handling is unchanged.
Pin the evidence reference/status, policy/configuration fingerprint, admission
result and qualification seal in later training-job and paired-evaluation
lineage. Do not select enforcement per request, from environment variables, or
to improve an outcome. A new trusted bootstrap is required to change policy.
All scientific/PIT gates remain mandatory; no synthetic label may disguise an
empirical dataset. No fitting is authorized in FF-1.1A.

### 3.3 Qualification checklist and current disposition

`CHECK` means inspection pending; `PASS` requires referenced evidence; `FAIL`
means a known violation; `BLOCKING` prevents the dependent job. Row-level
exclusions are counted even when dataset-level gates pass. Unknown scientific
evidence does not pass. Rights admission alone follows §3.2. For scientific
rows, absent/unverifiable evidence is blocking CHECK; evidence that
violates its pass condition is FAIL with the response in the last column.

| CHECK | PASS CONDITION (referenced evidence) | Current result / BLOCKING? | FAIL CONDITION / response |
|---|---|---|---|
| Accepted runtime / target | FF-0 tag, target and clock versions | PASS | Stop incompatible extension |
| Rights by permitted use | Evidence status plus pinned COLD policy admits research | UNVERIFIED / WARN_ONLY — warning, not rights approval | Explicit denial always HOLD; ENFORCE also holds unknown/ambiguous |
| Provider coverage and decimal authority | Immutable native captures and source specification | CHECK — BLOCKING | No guessed close/basis |
| Subject identity | Dated NSE cash mapping for RELIANCE throughout range | CHECK — BLOCKING | Exclude unresolved scope; no present-day membership inference |
| Calendar and completed sessions | Versioned qualified schedule, exceptions and terminal target session | CHECK — BLOCKING | No weekday-generated grid |
| Corporate actions | Qualified coverage of each input window and target pair | CHECK — BLOCKING | Affected/unknown windows NOT_EVALUABLE |
| OHLCV integrity | Duplicates, missing bars, source decimals, volume, revisions | CHECK — BLOCKING | Retain all diagnostics; exclude invalid rows |
| PIT / archive provenance | Original availability, acquisition, admission and revisions | CHECK — BLOCKING | No retrospectively invented access |
| Features / dependency closure | Five allowed A2 results, complete inputs, finite values | CHECK — BLOCKING | Feature absence, not imputation |
| Training truth | Label evidence available before each fit cutoff | CHECK — BLOCKING | Purge late/unresolved labels |
| Split / support | Realized split manifest, embargo, counts and class support | CHECK — BLOCKING | No fit on invalid/insufficient fold |
| Evaluation truth / pairing | Exact common label revision and mode; ledger references | CHECK — BLOCKING | No score on unqualified pairs |
| Protocol and job grant | Independent pre-outcome review, immutable plan hash, bounded grant | CHECK — BLOCKING | No learned fit or holdout access |
| Optional dependency / replay | Approved exact lock and supported serializer/verifier | CHECK — BLOCKING for training | Qualification and FF-0 remain usable |

Do not reduce coverage until these pass. A qualification report may be useful
while every empirical row is NOT_EVALUABLE. Empty reports must explain why.

## 4. Observation identity and clocks

One observation is the existing canonical target + exact qualified reference/
target `ForecastWindow` + `information_cutoff` + `as_of`, using the existing
`observation_id` projection. Do not replace it with a symbol/date string.
Mode and forecaster identity are separate comparison constraints, not changes
to the accepted observation hash. Both arms consume the **same** target/window
objects and source references; equivalent-looking windows with differing pins
are not casually joined.

For reference session `S_t`, set information cutoff to its **scheduled close
plus 30 minutes**, and simulated forecast as-of to cutoff **plus 5 minutes**.
Both must precede the next eligible session open; otherwise that planned row is
unavailable. These are observation-profile choices, not assumptions about fixed
exchange hours. All datetimes remain aware, reject naive input, normalize using
`ZoneInfo("Asia/Kolkata")`, and serialize with `+05:30`. Durations are not manual
timezone arithmetic. Session timestamps come from qualified schedules.

| Clock / identity | Rule |
|---|---|
| Feature knowledge | Every source dependency available/acquired/admitted by the row cutoff |
| Fit knowledge | Training features and truth evidence available by the fold fit cutoff; later corrected values cannot leak backward |
| Historical as-of | Simulated forecast eligibility time; must be before target open |
| Computation / artifact / journal time | Actual present-day operation time; never rewritten to historical as-of |
| Issuance | No actual issue for this retrospective campaign; `issued_at` absent |
| Evaluation as-known | Actual evaluation job timestamp, pinned before its label selection; original source knowledge cutoffs remain separately enforced |
| Label | Existing target/label version `1.0`, exact outcome key, selected append-only journal revision and source pins |

Training truth uses the latest qualified source revision actually known before
the historical fold fit cutoff; a later materialized label may derive from that
older retained revision but records its real materialization time. Test truth
uses the latest qualified revision known at the pinned evaluation as-known time.
Both arms use that exact same test revision. A later correction yields a new
comparison with new lineage, never mutates an old one. Do not pretend a journal
entry created today existed at a historical journal-read cutoff.

ACTUAL remains supported by the accepted contracts and tested for compatibility,
but is not run by this campaign. Actual issuance requires real pre-open clocks.
Never pool ACTUAL and SIMULATED; deliberately mixed pairs fail compatibility.
Recorded replay only reads captured artifacts; pinned inference recomputes with
the captured model, not a new fit. Re-fitting is a separate authorized Learning
job, not replay, issuance or ordinary forecasting.

## 5. Exactly five features, supplied by A2

Feature schema ID: **`ff1.reliance.a2_daily_five/1.0`**. Fixed order below;
timeframe `1d`, latest input the completed reference session, no target-session
bar. All five use the existing A2 calculators and captured `FeatureResult`
contracts; FF-1 projects/validates these results, it does not reimplement A2.
Existing code: [returns](../src/tiaf/features/returns.py),
[trend](../src/tiaf/features/trend.py),
[volatility](../src/tiaf/features/volatility.py),
[volume](../src/tiaf/features/volume.py).

| Order / feature ID | Exact parameters | Native meaning / unit | Minimum input |
|---|---|---|---|
| 1 — `return.log` | `bars=1` | Natural log close difference / `log_ratio` | 2 closes |
| 2 — `return.log` | `bars=5` | Five-session natural log close difference / `log_ratio` | 6 closes |
| 3 — `trend.distance_from_sma_percent` | `period=20` | `100 * (close - SMA20) / SMA20` / percent | 20 closes, including reference |
| 4 — `volatility.realized` | `bars=20`, `annualization_factor=252` | Sample standard deviation of 20 log returns times sqrt(252), expressed in percent | 21 closes |
| 5 — `volume.relative` | `bars=20` | Reference volume divided by mean of the preceding 20 volumes, excluding reference / ratio | 21 volumes |

Supply one qualified **21-session** rolling input closure to the existing A2
feature path; do not compress missing bars into consecutive observations. Verify
calendar continuity and applicable action status over every dependency window.
252 is a declared normalization convention, not a statement that each year has
exactly 252 sessions. Preserve A2 feature versions, units, parameters, source
fingerprints, result status and actual computation time. Derived computation
today does not turn a late raw input into PIT-safe evidence.

These five cover short returns, a longer trend reference, variability and
participation with a small fixed schema. Correlation between features is expected
and documented; no independence or causal interpretation is claimed. This study
does not impose coefficient signs: returns and SMA distance can express
continuation or reversion; volatility and relative volume have no presumed
directional sign. Report the learned sign and scaled-unit association without
interpreting it as a guaranteed mechanism. The FF-0
plan's two-return Logistic preview was not a frozen learned schema; this pass
adds three existing generic A2 features to meet the bounded five-feature study,
before inspecting any empirical outcomes. No symbol-specific selection was run.

Excluded: RSI/MACD variants, indicator grids, discretionary trend labels, A2/A4
scores as probability surrogates, news, fundamentals, broker/order data,
derivatives/IV/Greeks, sector/index features, regime embeddings, LLM text,
future/revised data, PCA, interactions, feature selection and target leakage.

### Missing data and preprocessing

Require all five results `AVAILABLE`, fresh for their declared reference window,
with correct units and finite numeric values. PARTIAL, stale, missing, NaN,
infinity or mismatched dependency pins means feature-ineligible; preserve the
requested observation and reasons. No mean fill, zero fill, forward/back fill,
interpolation, dropping columns, or scaling on all dates. Legitimate zero
returns, zero variance and zero volume ratios remain numbers, not absence.

Fit `StandardScaler(with_mean=True, with_std=True)` **only on each fold's admitted
training rows**, population variance (`ddof=0`); retain its means/scales and exact
training membership. A constant column has scale 1, stays in the schema and is
reported; no automatic feature replacement. Validation/test transforms use only
that frozen scaler. No clipping, winsorization or other learned transform.
The selected semantics match the [versioned StandardScaler documentation](https://scikit-learn.org/1.7/modules/generated/sklearn.preprocessing.StandardScaler.html);
the stricter finite/missing-value rejection is this study's admission rule.

## 6. Logistic instrument and optional dependency

Select **scikit-learn 1.7.2**, as a fixed reviewed candidate release, not a claim
that it is the latest. One optional future training extra; no dependency added
or installed here. Before training, resolve and independently approve an exact
hash-pinned compatible lock for Python, NumPy, SciPy and the trainer's transitive
dependencies. Unresolved packaging blocks fitting, not FF-1.1 qualification.
No alternate trainer, automatic upgrade or fallback model if unavailable.
The optional Evaluation block sampler uses NumPy from this same approved lock;
its absence is explicit dependency-unavailable, not a different resampling
algorithm. Qualification, basic recorded reads and pinned JSON inference do
not require the training/sampling dependency stack.

The entire model configuration is one immutable protocol value:

```text
LogisticRegression(
    penalty="l2", C=1.0, solver="lbfgs", tol=1e-8, max_iter=1000,
    fit_intercept=True, class_weight=None, dual=False,
    warm_start=False, random_state=1729, n_jobs=1
)
X: ordered five-column float64; y: binary [0, 1]; positive event class: 1
```

This is a binary L2-regularized model with an intercept, equal observation
weights, no resampling or class balancing. `C=1` is a generic fixed engineering
baseline, not optimized. The selected solver supports this penalty; its
`random_state` is not a source of randomness for `lbfgs`. Keep the seed in the
protocol and use it for the separately specified bootstrap, without pretending
it guarantees identical floating-point optimization everywhere. See the
[versioned LogisticRegression API](https://scikit-learn.org/1.7/modules/generated/sklearn.linear_model.LogisticRegression.html).

Exactly **one configuration**, five predetermined fold fits; no grids, random
search, adaptive C, threshold search, warm starts, ensemble, calibration fit,
FM/LFDE, trees/boosting, deep learning or feature revision after evaluation.
Nonconvergence/`ConvergenceWarning` is a failed fit, not a usable result or an
invitation to increase iterations. Coefficients explain an association in scaled
input space, not a causal effect or a trade instruction.

Use one isolated optional Learning worker, numeric threads fixed to one before
imports. Missing package or incompatible version is typed
`ML_DEPENDENCY_UNAVAILABLE`; never install on a forecast/replay path. Existing
FF-0 imports, CLI and all replay of recorded results remain usable without ML.

## 7. Artifact identity and reproducibility

Learning emits a data-only, validated, finite-number JSON Logistic artifact:
forecaster ID **`forecaster:logistic-regression`**, instrument version **`1.0`**,
ordered feature schema/version, training mean/scale, coefficient vector,
intercept, `classes=[0,1]`, positive-event mapping, trainer configuration/version,
fold/split and exact training membership, rights/data qualification references,
source/label revisions, training cutoff, protocol and job-grant references.
Include target/version, preprocessing/inference/serializer versions and code
identities. Scientific identity excludes hostnames, temporary paths and unrelated
environment variables; provenance retains actual job timestamps separately.
Numeric values, relevant algorithm/dependency changes and training membership
must change the scientific artifact fingerprint.
Use declared semantic projections of dependencies for scientific identity;
do not indirectly pull real-time job/capture timestamps into it through audit
reference hashes. Full audit references belong in the separate capture closure.

Retain exact Python/numeric-library versions, BLAS backend/thread settings and
approved lock digest in a reproducibility profile. Distinguish the model's
content fingerprint, scientific configuration fingerprint and capture/audit hash;
do not hash the whole workstation environment or confuse a new capture time
with a new scientific model.

No pickle/joblib/cloudpickle or arbitrary Python import embedded in a model.
These object-loading formats have execution/environment risks documented in
[scikit-learn's persistence guidance](https://scikit-learn.org/1.7/model_persistence.html).
Use the existing canonical JSON/fingerprint boundary and explicit artifact
schema validation, never dynamic code deserialization.

Pinned Logistic inference uses a registered, pure numeric five-input dot product
plus overflow-safe sigmoid over the captured scaler/coefficients. This is an
artifact evaluator, not a second fitter. During later implementation, require
parity to the chosen trainer's `predict_proba` within **absolute 1e-12**, including
extreme finite inputs; nonfinite transformed values/logits fail explicitly.
Original probabilities are retained without rounding or metric clipping.

Recorded replay must be exact without sklearn, fitting, network or provider
access. Pinned Logistic inference uses an explicit versioned **absolute 1e-12**
numeric comparison profile with exact identity/status/lineage matching; FF-0's
existing exact verifier is unchanged. Same locked-environment repeat fits must
reproduce the artifact; cross-platform re-fitting may produce a new artifact
even when probabilities are numerically close. Never promise platform-universal
bitwise training equality or replace old coefficients during replay.

## 8. Ownership, roles and the synthetic-contract boundary

```text
Qualified captures + rights + pinned protocol
           |                         |
           v                         v
Evaluation: truth, splits       Governed Learning: bounded fit
           |                         |
           |                   candidate JSON artifact
           |                         |
           |                   one registry, EXPERIMENTAL
           |                         |
           +--> trusted COLD research binding --> FF inference
                                                   |
                                                   v
                        captured B0 / B2 runs + common truth
                                                   |
                                                   v
                      Evaluation: paired report + dispositions
                                                   |
                                                   v
                         independent reviewer; NO auto-promotion
```

| Object / decision | Owner / limitation |
|---|---|
| Native acquisition and canonical features | Existing provider/capture and A2 boundaries; no model-owned acquisition |
| Rights qualification | Authorized rights owner; referenced by data admission |
| Truth, splits, population, Ledger, metrics, comparisons | Evaluation; neither forecaster labels itself |
| Fits, preprocessing, candidate artifacts, all trial/usage records | Governed Learning under an explicit bounded job grant |
| Artifact registry and lifecycle records | Architecture-assigned Learning custody, implemented as one bounded registry extension; no second active-model database |
| Inference | FF, over immutable supplied evidence and pinned artifacts; never fits |
| Scientific review / PromotionDecision | Independently authorized reviewer, not the trainer's score function |
| Research composition selection | Trusted COLD startup within the research grant; no HOT replacement |
| Public publication, A4/A5/A6 use or trading authority | Not granted by FF-1 |

BaseRate remains **BENCHMARK**. Logistic is **CHALLENGER** with lifecycle
**EXPERIMENTAL** even after a favorable FF-1 result. A report may support a later
validation proposal; it cannot assign PRIMARY, approve a model, activate SHADOW
operation or bypass independent approval. Role, lifecycle, calibration and
scientific-support status are separate fields. Probabilities remain RAW;
calibration absent, uncertainty qualification not estimated, validity unknown
until a separately scoped authority establishes otherwise.

### Explicit additive research versions — do not relabel FF-0 data

Inspection found deliberate FF-0 restrictions: `ForecastRequest` and capture/
runtime profiles permit synthetic engineering only; artifact/composition types
name the singleton historical BaseRate; Outcome Journal/link types are synthetic,
and links assert `NO_METRICS_NO_POOLING`. Passing real rows through these by
metadata, casts or fake `SYNTHETIC_FIXTURE` values is prohibited.

Plan **additive research schema 2.0** in the existing forecasting/Evaluation
owners for request/result identity, model/composition binding, capture/rights,
outcome/link/Ledger and COLD profiles where those narrow literals require it.
Register explicit version dispatch and v2 replay handlers; retain original v1
classes, defaults, profiles, IDs and golden artifacts unchanged. Reuse the
unchanged target `1.0`, aware clock rules, observation identity projection,
raw binary output semantics and canonical serialization. Do not bump unrelated
contracts or silently make v1 more permissive.

The research BaseRate adapter needs its own declared adapter/artifact identity
(`historical-base-rate/2.0` research binding), while preserving
**BaseRatePolicy/1.0 arithmetic and its last-20 support rule**. Its version change
denotes admissible research inputs/lineage, not a new statistical estimator.
Require fixture parity to accepted v1 on identical synthetic transitions.
Do not claim the synthetic-only v1 forecaster already accepts empirical data.
Logistic uses its own first instrument version under the research envelope.

Research outcome links carry only qualified **research-metric** eligibility;
they do not promote old synthetic links to empirical authority. Synthetic v2
fixtures remain explicitly synthetic and cannot produce empirical acceptance.
This is an extension of one FF, one truth owner and one registry, not a parallel
A7 framework. Version/absence/import-isolation tests are mandatory before fit.

## 9. Chronological protocol and protected holdout

Protocol ID: **`ff1.reliance.daily_logistic_vs_b0/1.0`**. Independent review pins
its document hash and resolved data/split/configuration hashes **before** any
protected labels, metrics or model-selection feedback are exposed. Known market
history is not magically blinded: record any prior inspection of this exact
holdout; if contaminated, no confirmatory claim and a new future holdout requires
a new accepted protocol. No post-result editing of this one.

| Fold | Expanding training reference-date lower bound | Test reference dates | Role |
|---|---|---|---|
| 1 | 2018-01-01 | Qualified sessions in 2021 | Development walk-forward |
| 2 | 2018-01-01 | Qualified sessions in 2022 | Development walk-forward |
| 3 | 2018-01-01 | Qualified sessions in 2023 | Development walk-forward |
| 4 | 2018-01-01 | Qualified sessions in 2024 | Development walk-forward |
| 5 | 2018-01-01 | Qualified sessions in 2025 | Locked final holdout |

There is **no tuning-validation split and no calibration split** in this fixed
configuration: both are explicitly NOT_APPLICABLE, not missing unspecified
windows. Development folds diagnose stability but cannot choose parameters.
Final holdout is opened once, by a separate evaluation grant, only after the
earlier engineering/qualification checks pass; a failed earlier scientific gate
stops rather than consuming the holdout for curiosity.

### Exact fit boundary, purge and embargo

Let `S_b` be the first scheduled reference session in the fold's test year and
`S_g` its immediately preceding eligible scheduled session. Reserve **all of
S_g as embargo**; set the historical fit knowledge cutoff `F_j = S_g.open`.
Only training observations with reference date at/after 2018-01-01, target
resolution strictly before `F_j`, and all feature/truth availability by `F_j`
are eligible. Exclude any training dependency/label interval reaching the gap
or test boundary and any late-available revision. Persist exact boundaries and
excluded memberships; a numeric row count is not a split definition.

```text
eligible historical training       embargo       annual test references
... reference -> target resolved | full S_g | S_b ................ S_end
                                 ^ F_j=open
                                 both models frozen here (simulated cutoff)
```

In the ordinary consecutive-session case, the latest possible training origin
is two sessions before `S_g`, targeting the session immediately before `S_g`.
Do not use the embargo session's close to fit. Feature lookbacks for a test row
may include earlier historical prices (including the embargo session once
available); this is causal context, not training-label leakage. There is no
requirement to erase legitimate known history from test inputs.

No shuffle, random split, temporal backfill or adjacent target-overlap leak.
Earlier test rows may enter **later** folds' training only after their labels
are actually cutoff-safe; each observation is scored once as out-of-sample.
The last reference of a year can target the next year's first session: retain
that real window and purge it from any earlier-cutoff training fold. Fit each
model once per fold and freeze it for that test year; no within-year updates.

Minimum Logistic training support per fold: **500 eligible rows and 100 in each
class**. Feature-ineligible rows cannot train Logistic. Test support gates are
separate (§12). Failure does not shorten training, expand symbols, move dates,
relax rights, substitute class weights or combine nonadjacent missing windows.
Retain fold-level unavailable/failed runs and full requested denominators.

## 10. BaseRate and exact paired population

For each fold, BaseRate uses its accepted **last 20 scheduled transitions**
resolved and known before `F_j`, unsmoothed `k/n`, minimum support **20**, no
backfill past an invalid transition. It is frozen for the year just like
Logistic. The prior v1 policy is not changed to a full-training-window mean,
Laplace estimator or rolling test-year updater. This intentionally compares
a short historical-frequency reference with an expanding-training Logistic;
record the different training memberships and do not call them identical fits.
Both use the same admissible knowledge cutoff and identical test observations.

A missing BaseRate forecast is not zero, neutral 0.5, or permission to compare
Logistic against a different reference. Its rows remain in requested/union and
per-arm reports but cannot enter paired loss. Evaluation additionally reports
the architecture-required **fixed 0.5 diagnostic on exactly the paired rows**;
this is not a substitute BaseRate, new learned model or promotion candidate.
Any supplied A2/A4 deterministic controls retain their original non-probability
meaning; absent controls and A5/A6 applicability are explicit NOT_EVALUABLE,
not fabricated probabilities or dependencies of this cash-equity study.

An included pair requires the same observation ID, target/version, subject,
schedule/window, reference/basis/unit, information cutoff/as-of, realization
mode, label policy and exact outcome revision, evaluation-as-known, study/fold,
data qualification, and weighting policy. Both probabilities must be AVAILABLE,
finite and in [0,1]. Wrong modes, mismatched truth or incompatible semantics
are rejected rather than coerced. Arm model IDs intentionally differ.

### PairedComparisonManifest contents

Pin baseline/challenger instrument, artifact, scaler and composition identities;
target/label/subject/window/basis/unit; data/rights/feature schemas and exact
capture references; dates and ordered requested observations; planned/realized
split and fit-cutoff IDs; SIMULATED profile; common outcome revision references;
immutable Ledger snapshot; evaluation-as-known; metric registry/conventions;
uniform weights; support, uncertainty, multiplicity and resource policies;
all attempts/trials/selection reasons and usage references.

A later outcome correction, data revision, feature/scaler change or policy change
creates a different comparison identity. The immutable manifest and input
Ledger are hashed first; derived population/scorecard artifacts refer to them;
a final report index references all outputs. Avoid circular manifest/report
hash references. A filesystem name or current registry alias is not a pin.

## 11. Metrics, numerical conventions and population accounting

Primary proper losses, with equal weight for each included unique pair:

```text
Brier(p, y) = (p - y)^2
LogLoss(p, y) = -[y ln(q) + (1-y) ln(1-q)]
q = min(1 - 1e-15, max(1e-15, p))  # metric computation only
d_i = Loss(Logistic_i, y_i) - Loss(BaseRate_i, y_i)
negative mean(d) favors Logistic
```

Retain the original raw `p`, count endpoint/clipped inputs and pin natural-log
units. Clipping never changes the stored forecast. Empty populations, zero
denominators and nonfinite arithmetic emit typed NOT_EVALUABLE/FAILED results,
never zero loss. Accuracy at fixed `p >= 0.5` (ties positive), confusion counts,
per-arm availability/absence and paired coverage are secondary diagnostics;
accuracy does not override proper-loss gates. No threshold sweep or ROC-based
model selection.

Report reliability **diagnostics** for each arm using ten fixed width bins:
`[0,.1), ... [.9,1]`; bin count, mean p and observed positive frequency; bins
with fewer than 20 pairs marked LOW_SUPPORT. Weighted absolute bin gap (ECE)
may be shown descriptively. No fitted calibrator, qualified calibration claim,
confidence conversion or validity promotion; calibrated-qualified coverage is
zero. Binning is not learned from holdout outcomes.

Report each development fold, the pooled development pairs, and final holdout
separately. No pooled development+holdout headline. Regime/context without
qualified PIT annotations is UNKNOWN, not reconstructed by a new regime model.
Supplied overlapping contexts remain memberships, not extra observations;
global success cannot hide a reported local loss. No post-hoc subgroup search.

### EvaluationPopulationDispositionReport

Use the existing Evaluation-owned concept, extending version only where required
by research authority. Emit even on zero pairs, failed folds and partial runs.
For every requested observation × metric × arm, exactly one INCLUDED, EXCLUDED
or NOT_EVALUABLE disposition with primary reason, all contributing facets and
unevaluated checks. Precedence: scope → identity/PIT/basis/session/actions →
forecast absence/failure → truth absence → metric applicability → included.

Retain requested-row count separately from unique observation count; immutable
session grid, data/feature eligible population, attempted/successful forecasts,
benchmark/challenger intersection and union, truth-linked counts, late/unknown
data, each exclusion reason, per-fold/class support and exact weights. A failed
calendar qualification can enumerate intended date slots as unresolved scope,
but cannot claim valid observation IDs or a complete realized denominator.
No silent inner join or discarding failures to improve coverage.

## 12. Paired statistical comparison and scientific decision

This is a **predeclared engineering research protocol**, not a power calculation,
trading utility threshold or guarantee of model validity. Independent review
must accept its assumptions before protected outcomes; insufficient evidence is
an expected legitimate outcome.

### Dependent-session uncertainty protocol

Use a **moving-block bootstrap**, fixed block length **5 scheduled reference
sessions**, **5,000** replicates, `Generator(PCG64(1729))`, no adaptive block
selection. Resample the full chronological session grid **with its missing-pair
mask**, not compressed consecutive valid rows. Uniformly draw overlapping block
starts `0..T-5`, concatenate blocks until T slots, then truncate. No circular
end-to-start blocks or blocks crossing fold boundaries. Apply the sampled mask
before averaging paired losses; use the same sampled indices for both losses.

For pooled development diagnostics, resample each fold independently to its own
grid length in fixed fold order, then pool retained paired losses. Final
holdout uses a fresh generator with the same declared seed, independently of
development execution. Persist sampler/version, row grid/mask, seed, actual
replicate count and all settings. A zero-pair replicate is NOT_ESTIMABLE for the
interval; no favorable redraw or seed retry.

For each primary loss report the observed paired mean difference and a **97.5%
two-sided percentile interval**, quantiles `0.0125, 0.9875`, linear interpolation.
Two such intervals give a nominal Bonferroni 95% familywise policy for the two
primary comparisons; it is conditional on this time-dependence approximation,
not exact finite-sample coverage. No IID standard errors, row shuffle or claim
that bootstrap replicates are independent empirical observations. No refitting
inside the bootstrap; uncertainty is conditional on the specified fold fits.

Minimum support: each development fold **150 pairs, at least 30 per class**;
pooled development **600 pairs**; final holdout **200 pairs, at least 40 per
class**. Paired coverage must be **at least 80% of the intended qualified
session grid in every fold**. Also require **20 complete nonoverlapping
five-session paired blocks** in each fold, measured by partitioning the original
grid from its first slot; incomplete/masked blocks do not count. This is a
support guard, not proof of 20 independent observations. Report these counts.
Unqualified grid/labels or untenable dependence/stationarity assumptions yield
INSUFFICIENT_EVIDENCE, not a narrower interval. Do not tune block size to repair
the conclusion.

### Three scientific outcomes, separate from job failure

| Decision | Exact condition / consequence |
|---|---|
| `LOGISTIC_SUPPORTED` | All rights/data/software/support/coverage/uncertainty gates pass; development mean Brier difference is negative in at least 3/4 folds, no development fold worsens Brier by more than 0.02 or log loss by more than 0.05 nats; final Brier upper interval bound is strictly below 0; final log-loss upper bound is at most +0.01 nats. Supports a scoped research proposal only |
| `LOGISTIC_NOT_SUPPORTED` | Adequately qualified evaluable evidence fails a predeclared scientific gate; record the particular loss, instability or noninferiority failure. If development fails its stability gate, stop before opening the holdout and label final evidence NOT_RUN |
| `INSUFFICIENT_EVIDENCE` | Rights/PIT/support/coverage/paired population/interval assumptions or holdout integrity are not adequate; describe the blocked claim, not a loss of zero |

A software error gives a typed FAILED job and no scientific support verdict for
that failed computation; a report may still state which empirical claim remains
insufficient. Never call an exception `LOGISTIC_NOT_SUPPORTED`. One-sided
superiority/noninferiority decisions use the declared upper bounds, not whichever
tail looks good. Margins 0.02/0.05/0.01 are transparent fixed baseline policy
values, not estimated commercial benefit or fitted to named examples. A small
point-estimate win with an interval crossing the gate is not support.

No additional models/configurations are tested in this campaign. Any later
proposal retains all prior trials, requires new pre-registration and an independent
holdout, and cannot reuse inspected 2025 outcomes as a new confirmation sample.

## 13. Lineage, persistence and bounded resources

```text
rights + source captures + qualified calendar/actions/security mapping
       -> canonical observations + A2 feature snapshots + independent truth
       -> dataset / feature / planned-and-realized split manifests
       -> Learning job + scaler + Logistic artifact (all attempts retained)
       -> pinned B0 and Logistic compositions + COLD research binding
       -> SIMULATED requests / node results / run captures
       -> Evaluation links + immutable Ledger + paired manifest
       -> population dispositions + metrics / intervals + scientific report
       -> recorded replay or pinned inference verification (never implicit fit)
```

Reuse content-addressed local JSON blobs and append-only journals under the
existing storage owner. Add explicit research-profile indexes for datasets,
splits, jobs, artifacts and comparison bundles; no MLflow, database service,
distributed scheduler or second mutable source of truth. Preserve native source
references, original prices, qualifiers, failure/absence and exact label
revisions through the entire closure. A model hash without its admitted
training-data/transform references is not reproducible lineage.

FF-0 has a static execution resolver and declarative artifact custody, not an
implemented learned-model lifecycle service. FF-1 realizes the architecture's
Learning ownership with narrow artifact/job records; it must not repurpose the
agent/provider registries or describe a new training service as already present.

FF-0 limits (including 256-entry closures/journals and 32 MiB corpus) remain
unchanged. FF-1 requires a separately admitted research store profile with
streamed, bounded closure verification; cannot merely feed larger corpora to
v1 and ignore rejection. Pin immutable shards of at most **64 row records**,
each row no more than **1 MiB**, at most **65,536 referenced artifacts** and
**2 GiB total admitted retained bytes** per campaign. Verify each reachable
reference, enforce aggregate limits and reject missing/cyclic closure; no opaque
unverified shard loophole. Large provider payloads must be refused or separately
qualified upstream, not silently truncated. No reference-path escape or remote
fetch on replay.

Preserve the accepted limitation that forecast-link and Ledger appends are not
one atomic cross-file transaction. Research indexes use explicit complete/
partial state and idempotent references: a crash between appends produces an
incomplete bundle, not a score or an invented transaction guarantee. Resume
only by validating existing immutable entries and adding missing references;
do not double-weight rows or silently repair a previously published report.

| Resource | Hard campaign bound / behavior |
|---|---|
| Requested reference observations | 4,096, one subject; warm-up/target dependencies also count toward storage limits |
| Features | Exactly 5 float64 columns, fixed ordering |
| Configurations / fits | 1 configuration; 5 Logistic fits maximum, serial; five frozen BaseRate artifacts |
| Training | One isolated worker, one numeric thread; 1,000 optimizer iterations; 60 seconds per fit; 512 MiB worker memory |
| Forecast attempts | One attempt per arm/observation; maximum 8,192; no automatic retries |
| Numeric inference | Existing one-second bounded deadline principle, explicit research profile; no change to FF-0 cooperative deadline semantics |
| Evaluation bootstrap | 5,000 replicates per declared summary; 120 seconds total evaluation budget; no bootstrap refits |
| Campaign | 600 seconds total local execution budget, excluding human review and evidence provisioning; timeout retains partial report |
| External use | Zero LLM/API tokens, zero provider/live calls in the offline campaign; no broker operation |

Isolated training enforces wall-time/memory termination rather than pretending
a cooperative Python timer can interrupt a native optimizer. Retain attempted,
completed, failed, timed-out and partial usage; no invented completion costs.
Local ML fit/inference counts are **not zero** when later run: distinguish them
from zero external LLM calls. CPU cost is measured usage with monetary cost
UNPRICED unless an explicit local rate is supplied; strict monetary budgets must
not treat unknown cost as free. Resource rejection needs a new reviewed grant,
not an automatic increase. These bounds are policy, not observed benchmarks.

## 14. Fixture and acceptance strategy

No Logistic fitting occurs in this planning pass. Later separately authorized
implementation may use tiny synthetic mechanics fixtures and fixed handcrafted
coefficients; all are marked SYNTHETIC and cannot establish empirical value.
Later empirical acceptance requires the rights/PIT/protocol gates independently.

| Fixture group | Required assertions |
|---|---|
| Qualification | Rights unknown/expired/disallowed; today-downloaded history; revised/late data; decimal ties; unknown calendar/action; duplicate and unresolved subject |
| Features | All five exact A2 values/units/order/dependencies; warm-up; no target bar; zero data preserved; missing/PARTIAL/stale/nonfinite rejected; no imputation |
| Scaling | Train-only statistics; constant column; changing a test value cannot change scaler or fit; held-out extrema do not leak |
| Splits | Annual boundaries, full gap, actual availability purge, cross-year target, earlier test entering only later training; every test ID scored once; locked holdout |
| Training / artifacts | Single config; binary class support; convergence failure; bounded worker; safe JSON; field tampering; coefficient/scaler/source changes alter identity |
| Roles / v1 preservation | BENCHMARK vs EXPERIMENTAL CHALLENGER; no PRIMARY; research input rejected by v1; research BaseRate parity; all 28 FF-0 cases |
| Pairing | Same observations/truth; missing BaseRate; one-arm failure; ACTUAL/SIMULATED mismatch; label revision mismatch; no neutral imputation; union/intersection retained |
| Metrics | Hand-computed Brier/log loss including 0/1 clipping; sign convention; threshold tie; reliability edges; empty/undefined results; complete dispositions |
| Uncertainty / decisions | Deterministic block indices/masks, no cross-fold blocks; sparse classes; inconclusive interval; supported/not-supported/insufficient and FAILED kept separate |
| Context / comparison replay | UNKNOWN and overlapping contexts, global win/local loss, old-label replay, version and metric-policy incompatibility |
| Replay / isolation | Exact recorded replay without ML/network; bounded pinned JSON inference; independent refit grant; no current alias substitution; absent optional ML does not break FF-0 |
| Operator / failure | Safe read-only commands, explicit local roots/grants, budget failures, partial reports, all unsuccessful attempts retained |

Synthetic checks establish arithmetic, lineage, leakage controls and failure
semantics, not model skill, calibration, empirical support or data rights.

## 15. Five separately authorized implementation slices

| Slice | Deliverables / tests | Exit gate and stop boundary |
|---|---|---|
| **FF-1.1 — Data qualification and feature schema** | Typed qualification/rights and additive research contract design; five-feature schema/projector over A2; observation/feature/availability checks; planned/realized split validator; negative and absence fixtures | Reviewed schema, qualified-or-explicitly-blocked report, immutable v1 behavior. **No learned fit**, no acquisition. Unknown data may remain HOLD while qualification machinery passes |
| **FF-1.2 — Governed Logistic artifact training** | Optional sklearn worker/lock, grants and bounds, train-only scaler, one config, finite JSON artifacts/registry candidates, dependency isolation and synthetic fit/parity tests | Artifact/reproducibility/security tests pass. Empirical fit only if every admission gate and separate job grant pass; no score-driven tuning |
| **FF-1.3 — Pinned research runtime and walk-forward** | Additive COLD/descriptor/capture/store profiles; BaseRate v2 input-binding parity; fixed Logistic inference; five-fold runner, immutable simulated clocks and holdout admission | Both arms capture/replay, v1 remains exact, no actual backdating or automatic selection. Stop missing baseline/support or incompatible research profile |
| **FF-1.4 — Paired Evaluation and comparison** | Independent research truth links/Ledger, manifest, disposition emitter, proper losses, block intervals and three scientific outcomes | Exact same-pair reports including zero/failed cases; FFT-15/16 and mode/context fixtures pass; no role/lifecycle promotion |
| **FF-1.5 — Engineering CLI and acceptance hardening** | Internal commands below; synthetic end-to-end corpus; separately gated empirical report if qualified; documentation and full repository quality gates | Honest scoped acceptance, retained failures, no public forecast endpoint. Synthetic-only completion explicitly leaves empirical validation HOLD |

Concrete proposed module placement and handoff (names are planned, not files
created in this pass):

| Slice | Files/modules | Explicit inputs → persisted outputs | Git checkpoint recommendation |
|---|---|---|---|
| FF-1.1 | `evaluation/forecast_research_contracts.py`, `evaluation/forecast_qualification.py`, `evaluation/forecast_splits.py`, `forecasting/research_contracts.py`, `forecasting/research_features.py`; matching unit fixtures | Captures/rights/protocol + A2 results → qualification, feature-schema and realized-split manifests, including blocked reports | Separate qualification/schema implementation commit after its acceptance; no automatic tag |
| FF-1.2 | New lean `learning/forecast_training.py`, `learning/forecast_artifacts.py`, `learning/forecast_jobs.py`; optional dependency declaration only when authorized; training tests | Qualified training split + exact lock/config/grant → job/usage record, scaler and candidate artifact or typed failure | Separate training/artifact commit; never commit restricted data/model evidence without rights; no automatic tag |
| FF-1.3 | `forecasting/research_runtime.py`, `forecasting/logistic.py`, explicit research handlers in store/replay/forecasters; walk-forward tests | Pinned artifacts + research COLD config + split/grant → immutable two-arm simulated runs and replay proofs | Separate runtime/walk-forward commit after v1 parity and import isolation; no automatic tag |
| FF-1.4 | `evaluation/forecast_comparison.py`, `evaluation/forecast_metrics.py`, research handlers in truth/linkage; population/statistical tests | Captured runs + exact truth + paired manifest/grant → Ledger, dispositions, metric/interval results and scientific report | Separate Evaluation commit; retain all failures and trials, no automatic tag |
| FF-1.5 | Existing `forecasting/engineering.py` / `scripts/forecast_miniature.py`, `tests/acceptance/ff1`, synthetic fixtures and operator/acceptance docs | Accepted preceding slices + bounded corpus → CLI acceptance and explicit empirical-qualified or synthetic-only status | Separate hardening/acceptance commit if requested; recommend baseline tag only after independent scoped acceptance and explicit authorization |

All paths above are under `src/tiaf/` unless prefixed with `scripts/` or
`tests/`. These are future checkpoint recommendations, not Git actions now.
The qualification contract definitions needed by later slices belong in FF-1.1;
later slices implement their behavior, not introduce unreviewed semantic drift.
Suggested additions stay within `src/tiaf/forecasting`,
`src/tiaf/evaluation` and a small new `src/tiaf/learning` package for the
architecture-assigned Learning owner (no resident service). Use explicit
research-version modules and the one artifact registry/store. No specialist,
domain trading contract or provider package imports sklearn. Test files belong
with existing forecasting/Evaluation unit and acceptance suites.

Implementation entry requires a separately requested slice, reviewed plan,
preserved FF-0 baseline and agreed research-version boundaries. **Empirical
training additionally requires** qualified captures/rights, realized split and
class support, approved exact dependency lock, reviewer-pinned protocol and
bounded job grant. These are enforced inputs, not developer discretion.

## 16. Internal CLI / operator plan — not commands implemented now

Extend the existing **`scripts/forecast_miniature.py`** engineering entrypoint;
retain all existing FF-0 verbs and defaults unchanged. Planned research verbs:

| Planned verb | Inputs / authority / output |
|---|---|
| `research-qualify` | Explicit local dataset + rights + protocol references; no network or fit; qualification, feature and realized split manifests |
| `research-train` | Qualified manifest + fold + exact config + Learning grant; creates one EXPERIMENTAL candidate; never automatically evaluates/promotes |
| `research-walk-forward` | Pinned two-arm artifacts/bindings + split + research grant; bounded simulated inference; no hidden fitting or refits |
| `research-compare` | Captured runs/common truth + paired manifest + Evaluation grant; protected holdout requires its explicit one-time authorization; reports/dispositions |
| `research-inspect` | Local dataset/model/job/comparison IDs; read-only status, pins, support, failures, usage and scientific result |
| Existing replay / verify, explicit research version | Recorded output read or pinned numeric inference; no trainer/provider use; unsupported version explicit |

Operator sequence is qualify → separately grant/train predetermined folds →
infer frozen arms → compare development → separately open final holdout if
eligible → inspect/replay. IDs resolve only within trusted local captured roots;
do not load arbitrary executable model paths, URLs or dynamic classes. There
is no `--live`, auto-install, default empirical corpus, optimizer loop, generic
job launcher, scheduler or public `ti`/facade/Shell forecast capability.
Qualification, inspection and recorded replay must work without sklearn.
The capability catalog remains unchanged; **INTERNAL_ENGINEERING_CLI_ONLY**.

## 17. Failure taxonomy, stop rules and FF-2 seam

Names below are planned namespaced research outcomes, not existing exceptions
claimed to be implemented. Absence and scientific non-support are not crashes.

| Typed reason | Layer / required response |
|---|---|
| `DATA_RIGHTS_UNKNOWN` / `DATA_RIGHTS_DENIED` | Admission BLOCKED; no empirical fit/use |
| `DATA_QUALIFICATION_FAILED` | Qualification report with all failed/unknown facets |
| `INSUFFICIENT_TRAINING_DATA` | Fold UNAVAILABLE; no fallback fitting or moved dates |
| `FEATURE_LEAKAGE_VIOLATION` | Reject artifact/job; preserve the offending dependency references |
| `SPLIT_INVALID` | No fit/evaluation; report interval and availability violation |
| `ML_DEPENDENCY_UNAVAILABLE` | Training unavailable; lean FF-0/replay remain operational |
| `MODEL_FIT_FAILED` | FAILED job, convergence/numeric diagnostics, no usable artifact |
| `ARTIFACT_SERIALIZATION_FAILED` | Reject artifact, never fall back to pickle or unpinned memory object |
| `INSUFFICIENT_PAIRED_POPULATION` | NOT_EVALUABLE / INSUFFICIENT_EVIDENCE with complete denominators |
| `METRIC_CALCULATION_FAILED` / `INTERVAL_NOT_ESTIMABLE` | Typed failed/not-estimable metric, never fabricated finite result |
| `COMPARISON_INCOMPATIBLE` | Refuse mode/target/label/version/weight mismatch; no coercion |
| `RESOURCE_LIMIT_EXCEEDED` / `HOLDOUT_NOT_AUTHORIZED` | Preserve partial/denied attempt; no auto-retry or increased grant |

Stop if rights admission returns HOLD or PIT cannot be qualified, support is too small, feature schema
is unreliable, leakage is found, resource/dependency burden exceeds the grant,
or the fixed Logistic study is scientifically unsupported/unstable. There is
one campaign here, not repeated trials until success. A repair to a genuine
software defect requires narrow review; if it can use inspected holdout feedback,
retire the confirmatory claim and obtain a new independently approved holdout.
Do not keep retuning a losing Logistic against BaseRate. The accepted FF-0
engineering baseline remains valid regardless of this research outcome.

FF-2 can consume the frozen feature/preprocessing/model identities, raw
probabilities, split membership, exact labels, lineage, evaluation qualification
and role/lifecycle metadata. It needs a **new separately qualified held-out
calibration partition**, independent evaluation, manual approval, COLD selection
and shadow/advisory gates. Inspected FF-1 test outcomes cannot silently become
both its fitted calibration data and independent test. No calibrator artifact,
calibrated p, PRIMARY role or A4/A5/A6 overlay is created now.
Advanced families, public capability and A8 remain later work.

## 18. Planning validation and remaining blockers

The remaining scientific blockers are empirical admission facts, not unspecified
model choices: archive/PIT provenance, price/calendar/action qualification,
realized counts/classes, exact training lock and independent protocol/job
approvals. Rights evidence is separately recorded and admitted or held under
§3.2's pinned policy; unknown rights alone need not block WARN_ONLY research.
No qualified historical dataset was inspected, so none is claimed
to pass. These do not block implementing FF-1.1's qualification and refusal path.
No training grant is inferred from this plan's READY verdict.

Validation performed for this documentation pass:

- FF-0 acceptance preservation: `.venv/bin/pytest -q -s tests/acceptance/ff0`
  — **28 passed**; underlying evidence batch **229 passed** (nested evidence,
  not 257 distinct top-level tests).
- Local documentation links: **684 local targets/anchors across 12 Markdown
  files passed** (10 changed/new files plus the validator's two fixed references).
- Status/navigation and document structure: PASS; all ten changed files point
  to FF-1.1, retain empirical fitting HOLD and FF-1 runtime NOT_IMPLEMENTED;
  18 numbered plan sections, balanced code fences and table columns.
- Whitespace: `git diff --check` and explicit untracked-plan check passed.
- Changes restricted to Markdown planning/navigation/decision documentation;
  no `src`, `tests`, `scripts`, dependency, capability or runtime file changes.
- Existing FF-0 records and 28-case corpus unchanged; A6 frozen tag unchanged;
  no A8 edits. Existing baseline tag preserved.
- No Logistic/model fitting, data acquisition or live/provider/broker calls.
  Only public software documentation was consulted for dependency semantics;
  no secrets read or recorded. No commit, tag or push.

No full runtime suite is rerun for this planning-only change. Future code slices
must run their targeted tests and the repository quality gates required by their
acceptance scope; documentation readiness is not implementation acceptance.
