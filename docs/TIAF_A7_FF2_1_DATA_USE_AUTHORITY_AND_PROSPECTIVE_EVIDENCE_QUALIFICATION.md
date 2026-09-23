# A7 / FF-2.1 — Data-use authority and prospective evidence qualification

Date: 2026-09-23, Asia/Kolkata. **GOVERNANCE DESIGN COMPLETE; next boundary:
FF-2.2 CALIBRATION IMPLEMENTATION, SYNTHETIC ONLY.** No empirical execution grant,
calibrator, fitted candidate, prospective collection or final evaluation exists
as a result of this pass. The three readiness questions are deliberately separate.

This record supplements, and does not edit, the
[FF-2.0 protocol](TIAF_A7_FF2_0_CALIBRATED_LOGISTIC_RESEARCH_PROTOCOL.md) and
[then-current HOLD record](TIAF_A7_FF2_0_BASELINE_DATA_RIGHTS_AND_READINESS.md).
The scientific method, model choice, partitions and numerical rules remain v1.
The latest task inserts this governance stage before implementation: FF-2.0 §14's
old **FF-2.1 implementation** slot is now **FF-2.2**. Its later empirical/final
stages remain conditional work packages, not permissions or silently renumbered
historical deliverables. No need to wait for future data before writing safe
synthetic infrastructure.

## 1. Verified entry and preservation boundary

| Check | Actual observation |
| --- | --- |
| Branch / entry tree | `main`, clean |
| HEAD / local `origin/main` / live origin `main` | `1c451eb28bc0cfd5f8e8951260add24d718aee7b` |
| Commit | `TIAF A7: complete FF-2.0 calibration research protocol` |
| FLC tag / peeled commit, local and live remote | `tiaf-a7-flc-baseline` / `5f1e80c7e0614233b5670ca3acf9229edd0ea0db` |
| Annotated FLC tag object | `08767b720c62410166717a6df0002a7e9e24e692` |
| Four FF-1 scientific fingerprints | All match; exact values in the [authority record](qualification_records/ff2_1/data_use_authority.json) |
| Frozen FF-1 file pins | 72 source + 6 implementation = **78/78 MATCH** |

The first remote query failed sandbox DNS; the approved read-only `git ls-remote`
retry succeeded. No remote status is inferred from a cached ref alone. HEAD is
the subsequent FF-2.0 documentation commit, not a moved FLC tag.

FF-1 remains **INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE**, infrastructure
accepted, 2025 CONSUMED, executions used 1, post-holdout refit false. BaseRate is
BENCHMARK; Logistic CHALLENGER / EXPERIMENTAL, promotion eligible NO.
The [independent scientific closure](TIAF_A7_FF1_INDEPENDENT_FINAL_SCIENTIFIC_CLOSURE_AND_BASELINE_DECISION.md)
and [FLC closure §13](TIAF_A7_FLC_8_REFERENCE_IMPLEMENTATION_CLOSURE_AND_FLC_ACCEPTANCE.md#13-authorized-family-neutral-inference-reconciliation)
remain historical, byte-preserved records. No FF-1 scoring or numerical final
replay was invoked. This pass reads provenance, dates/counts and existing artifacts;
it performs no new feature/label projection, fit, forecast or scientific metric.

## 2. Provenance traced, not inferred from filenames

The local source is TI-native Dhan RELIANCE/NSE cash equity, security ID 2885,
economic series ISIN INE002A01018. Its CSV has **2,045 rows**, 99,118 bytes,
2017-11-01–2026-01-30, acquired **2026-09-21T12:07:50.995917+05:30**.
The file's date column was inventoried; source bytes were hashed. Acquisition is
a fresh later-vintage download, not contemporaneous historical capture. Raw
provider response was not retained. No new provider call was made.

| Trace object | Exact reference / finding |
| --- | --- |
| Dataset SHA-256 | `d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6` |
| Original source manifest | `data/ff1/reliance/source_manifest.json`, seal `3d1a4e21b6f4d08cb94b29d0aac83ec368c3c79c40bc535f2a75da55fb452c09`; original UNKNOWN basis retained |
| Accepted later qualification | `data/ff1/adjusted_qualification_20260921_clock_review/qualification.json`, seal `4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51`; byte hash in authority artifact |
| Actual training grant | `ff1.2:four-development-artifacts`, seal `b80c3561e5dbaab11bcaa95ceb9bf7e1301d6f3cfdc7a679ef48134d306829ad`; binds that qualification, schema, source and four folds |
| Training run | `data/ff1/logistic_training_20260921/run-f26605528584a68449396da9dea1a3e28d6e2295f355a7085887e5adedc94406.json` |
| Development forecast run | `4dc2adb6f2bb9977bf3a06c2c5903065223cfc6e2c6a58898c0cb65090197812`, under `data/ff1/logistic_forecasts_20260921` |
| Paired development ledger | `62bc746d90386f3b718bf6fe106f4a80832bfa8206ea3605ec96bbb2e5817246`, report `5f6d4342c61017fecda2196715d707a356ff8728eb0ec1f6996c362723ba19e1`, under `data/ff1/development_evaluation_20260921` |
| Fifth-fold handoff | `c40148f60e985c83fe8bca027a3722583ed8c1999ecfc86e4959c4fe6166ce54`, separate authority `31b54fdc10f6639c940e524f21ed10a343305c998b99d9f5815d710398c2c2ba`; original fifth fit, not post-holdout refit |
| Final custody | `data/ff1/final_protocol_20260922` and `data/ff1/final_holdout_20260922`; outer consumed ledger, not nested historic SEALED strings, owns final status |

The directory ending `_final` has qualification seal `182c75…`, an earlier
checkpoint. It is **not** the training grant's `4b0210…` input. The artifact and
grant trace, not the directory name, determines the accepted source. Private raw
data remain local/ignored; this report and its JSON contain metadata, not a data
redistribution or model-parameter dump.

The accepted profile is `ff1.adjusted_retrospective/1.0`, with the same five A2
features, corporate-action-adjusted price basis, provider-defined volume,
binary64-normalized prices and assumed historical availability. See the
[qualification report](TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md)
and [rights-policy record](TIAF_A7_FF1_1A_RIGHTS_POLICY_REVISION_AND_DATA_PROVISIONING.md).
The clock-review qualification pin governs the actual training; report creation
dates and earlier HOLD/SEALED states are not rewritten.

## 3. Authoritative historical evidence-use ledger

Counts below are source rows unless explicitly called pairs/train rows. Periods
are actual first/last source dates. Inspection means recorded acquisition,
qualification, training or evaluation exposure, not a claim to know every manual
read on the user's computer. No audit can prove undocumented private exploration
did not occur; known exposure is a lower bound, never proof of independence.

| Segment / rows | Prior use and label availability | Exposure / scientific status | FF-2 role now |
| --- | --- | --- | --- |
| 2017-11-01–12-29 / 42 | Warm-up/features for FF-1; source prices known, not assigned standalone forecast labels in this study | Inspected support; DEVELOPMENT_KNOWN, PROHIBITED_AS_PROTECTED | Read-only lineage; past-only feature support under a future grant |
| 2018-01-01–12-31 / 246; 2019-01-01–12-31 / 245 | All 491 used in selected 2022 model training and other historical folds | TRAINING_USED; input/label exposure certain | Read-only source-model lineage; no base/scaler fit |
| 2020-01-01–12-31 / 252 | 229 train rows in 2021 fold, 231 in selected 2022 fold; rights-action and boundary exclusions retained | TRAINING_USED; known source/qualified labels | Same; not calibration/protected rows |
| 2021-01-01–12-31 / 248 | 248 FF-1 development pairs; 246 selected-model train rows, 248 in later folds | TRAINING_USED + VALIDATION_USED, diagnostic score/reliability exposure | Lineage/past-only feature history, not new calibrator fit |
| 2022-01-03–12-30 / 248 | 248 FF-1 development pairs; 246 training rows in 2023 fold, 248 in 2024 fold | TRAINING_USED by other models + VALIDATION_USED + development diagnostics; not training of selected 2022 model | Conditional CALIBRATION subset; exact FF-2 eligible N **not yet materialized** |
| 2023-01-02–12-29 / 246 | 225 previous qualified pairs; 223 training rows in 2024 fold; later fifth-fold prefix also uses eligible history | TRAINING_USED + VALIDATION_USED + diagnostics | Conditional V1, all 246 scheduled origins retain masks; no cal refit |
| 2024-01-01–12-31 / 249 | 248 previous development pairs; eligible history in original fifth-fold training | TRAINING_USED + VALIDATION_USED + diagnostics | Conditional V2; last origin targeting 2025 excluded; no cal refit |
| 2025-01-01–12-31 / 249 | One protected FF-1 execution, 249 pairs and recorded final diagnostics; labels exposed | CONSUMED_PROTECTED; permanently PROHIBITED_AS_PROTECTED | All FF-2 numeric research roles forbidden, including support; hash/status checks only |
| 2026-01-01–01-30 / 20 | Known acquisition context; next-session endpoint context may support last FF-1 2025 target; not a new independent partition | PROHIBITED_AS_PROTECTED; no claim all rows had scored labels | All numeric v1 research roles excluded; no Jan-2026 holdout |
| Later history after 2026-01-30, before actual FF-2 freeze / none in this qualified source | No qualified issuance corpus identified; no acquisition now | UNAVAILABLE, not automatically unobserved because absent locally | Cannot backfill and call prospective; pre-freeze benchmark support needs separate qualification |
| Future after actual freeze + embargo / none yet | Outcomes not yet available at freeze/issuance; capture first, truth later | FUTURE_UNOBSERVED → PROSPECTIVE_CANDIDATE → qualified only under §6 | No collection/execution authority today |
| FLC authored fixtures / 600 fixed-recipe or 680 trial-recipe rows; five authored calibration probabilities | FLC engineering fits/optimization/diagnostics/evaluation and authored-table exploration only | SYNTHETIC_ENGINEERING; no acquired RELIANCE/Dhan/2025 evidence despite native compatibility spellings | Synthetic implementation/test support, never empirical acceptance |

Experiment-use trace: FF-1.2's four-fold grant produced training sizes
720/968/1,216/1,441. FF-1.3 generated 991 development records, 969 numerical
forecasts and 22 exclusions. FF-1.4 evaluated 969 pairs. The separate fifth-fold
preparation trained 1,690 rows through its pre-2025 cutoff; the final protocol's
one consumed execution is the exact FF-1 final experiment identity in §1/JSON.
Legacy artifacts have grant/run/protocol identities rather than one invented
modern `experiment_id`; those exact identities above are the experiment trace.

No empirical hyperparameter optimization or learned calibration fit appears in
these accepted runs. Prior diagnostics include training artifact reconstruction
and development/final scores/reliability, not just coefficient inspection.
No empirical calibration-related trial is recorded; this is **not proof of no
unlogged human exploration**. FLC's optimization/calibration exploration is
synthetic only. FF-2.0/2.1 have inspected metadata and previously published
results, and have not performed empirical calibration exploration. None of the
existing history may be advertised as untouched final evidence.

## 4. What historical development use is and is not authorized

Three distinct decisions must not be collapsed:

1. Custody exists and is hash-checkable.
2. Provider-use evidence is **UNVERIFIED**, historically admitted WARN_ONLY with
   `RIGHTS_NOT_APPROVED_RESEARCH_ONLY`. That is not verified licensing or legal
   advice. This task neither researches current provider terms nor certifies them.
3. **No FF-2-specific empirical data-use/fit grant is present.** FF-1 grants and
   FLC synthetic grants do not transfer. Defining this record does not sign a grant.

Consequently, current authorization is metadata/integrity review and synthetic
engineering only. The following is a precise **scientific allocation conditional
on a new FF-2 grant**, not permission to execute it now:

| Purpose | Exact allowed data if separately granted | Ordering / exclusions / meaning |
| --- | --- | --- |
| A. Calibrator parameter fit | Raw p from the pinned 2022 model/scaler on qualified 2022 features, plus external Ground Truth y | Target endpoint and assumed label availability strictly before 2022-12-30 09:15 IST; full embargo origin excluded. One fit, no V1/V2/2025 labels |
| B. Bounded configuration selection | One already specified sigmoid-logit configuration; V1 + V2 evaluate deterministic proceed/stop only | No configuration grid, method shopping or second fit. Numerical solver/lock frozen before fitting; convergence failure stops |
| C. Development diagnostics | CAL descriptive fit diagnostics; V1/V2 raw/q/BaseRate diagnostics, exact source model/scaler artifact metadata | Keep denominators/roles separate; diagnostic slope regression cannot overwrite calibrator parameters |
| D. Chronological validation | Qualified 2023 V1 and 2024 V2, same three-arm intersection and supplied labels | Preserve action exclusions; reference and target before 2025; both blocks known development, not final |
| E. Robustness/stability | Prespecified per-year and pooled V1/V2 reports under FF-2.0 | No after-results subperiods, bin changes, bootstrap searches, threshold retuning or selecting only a favorable year |

Past-only trailing features may cross the CAL/V1/V2 origin partition boundary;
that does not authorize fitting on validation labels. FF-2 historical admission
must check **every dependency**, not merely an origin-year flag, before numeric
decoding. No 2025 or January-2026 values may enter features, truth, calibration,
selection, benchmark support or final scoring. Old 2023/2024 Logistic forecasts
used different models and cannot serve as FF-2's raw arm. They are provenance,
not interchangeable predictions. The 248/225/248 prior counts are not newly
qualified FF-2 counts or class-support claims.

Historical computation/acquisition clocks remain real 2026 times. Simulated
availability/reference cutoffs follow the explicitly assumed retrospective
profile, not fabricated actual issuance. Actual future capture must instead
prove available-as-known inputs, publication/acquisition/admission, source basis,
actions and session calendar. A later adjusted download never supplies that proof.

To admit an empirical run later, the accountable research owner must explicitly
bind this experiment, source hashes, allowed purposes, qualified membership,
custody and fit request; adopt a scoped WARN_ONLY research policy with its
uncertainty acknowledged **or** supply verified use evidence; and obtain a
separate exact one-attempt calibrator execution grant. Explicit provider denial
blocks either route. No redistribution/production rights are inferred. The new
grant must not widen this scientific allocation. **Historical scientific roles
are defined; historical execution authority and data rights remain unresolved.**

## 5. Exact fixed Logistic identity and enforcement obligations

The complete machine-readable pins are in the [authority artifact](qualification_records/ff2_1/data_use_authority.json).
The source candidate is native `forecaster:logistic-regression`, implementation
and model artifact **1.0**, FF-1 **2022 development fold**, CHALLENGER /
EXPERIMENTAL—not the 2025 fifth-fold candidate. Its exact native identity is
model + manifest + run, not a mutable candidate alias.

| Dependency | Verified immutable identity |
| --- | --- |
| Model semantic hash | `7cbe4f2b14a72ae5e2af40c535710f1695687b81786f0c69efd271b50442a5d2` |
| Model file SHA-256 | `6f5b4c8cfa794073500c680d322f7ee3501126f4751eac1d301a66ce9ec61d6a` |
| Scaler semantic hash | `39e888ce1789405f4bdc9fa704e0f6ac43adfc5aaade55bc211d5c9f0986eb62` |
| Scaler file SHA-256 | `ea956a9a6612bd8c14023fe67caf63f05e5bf17744415ed891694ad430d47245` |
| Ordered feature schema | `ff1.reliance.a2_daily_five/1.0`, hash `76e63292685ee0b3b41f7ab033407e6bd014fc802d2092a2ed227888bdc71676` |
| Reconstruction object | `52837a1beb5d9bcab74666d13db5f33b64d30bf41e30d1e7917872fffcad8127`; contains coefficients, intercept, classes and exact scaler |
| Training | 968 rows, 2018-01-01–2021-12-29 origins; fit cutoff/embargo 2021-12-31 09:15 IST; run/manifest pins in §2/JSON |

Files are `model-<model hash>.json` and `scaler-<scaler hash>.json` under
`data/ff1/logistic_training_20260921`. Byte and semantic hashes are distinct.
Exact coefficients/scales were checked in those existing artifacts, not refit.
The model-config seal pins original L2/C=1/lbfgs recipe; schema pins feature
order `ret_1, ret_5, sma20_distance, realized_vol_20, relative_volume`.

Before an empirical adapter may run, machine admission must verify both byte
hashes, canonical seals, nested scaler/manifest/run/schema/config and training
lineage equality. It must reject alternate-year models, reordered/changed
features, modified coefficients/scales, fallback models and stale mutable
aliases. Base/scaler fit budgets are **zero**. Calibrator accepts only the exact
raw-capture stream; no feature-matrix estimator fit or old year-routing reuse.
Raw p remains immutable and q has a separate output/capture/composition.
This document defines these future edge checks; the current tests are a bounded
executable metadata specification, **not an implemented empirical adapter**.

## 6. Prospective evidence and observation qualification

```text
External empirical permission → development fit/selection (later, not now)
    → independent candidate + protocol + source/capture/final-policy freeze
    → one whole predeclared origin-session embargo
    → first 500 scheduled origin slots; no outcome-selected replacement
        → Forecasting persists input vintage + raw p + q + fixed BaseRate
        → target opens → target closes → Ground Truth journal evidence arrives
        → independent Evaluation qualifies at each fixed truth deadline
    → all slots terminal → one durable final claim → one protected evaluation
```

“Prospective” is relative to an **actual** freeze and issuance, not a filename,
download date, new experiment label or simulated forecast timestamp. Target
outcomes must not be known to this experiment at freeze or issuance. Require
actual `freeze < embargo completion < origin close < generation <= durable
capture < target open <= target close <= truth available`. If truth is available
at target close, equality is allowed; it is still strictly after capture. Inputs
must have been published/acquired/admitted no later than generation and must
include no post-reference information. Do not confuse record assembly with
durable publication time. All clocks are aware Asia/Kolkata, UTC/other zones
normalize, naive times reject, JSON `+05:30`.

The existing [neutral capture](../src/tiaf/forecasting/lifecycle_provenance.py),
[custody](../src/tiaf/learning/forecaster_custody.py),
[replay](../src/tiaf/forecasting/lifecycle_replay.py) and
[truth journal](../src/tiaf/evaluation/forecast_truth.py) provide identity/storage
building blocks. They do **not** by themselves demonstrate a live prospective
FF-2 calibrated issuer, sealed-role access, a durable receipt timestamp, an
authorized empirical profile or generic numerical reconstruction. Those gaps
must be closed/tested before accrual. Recorded MATCH alone is insufficient when
the native numerical verifier is UNSUPPORTED or required bytes are absent.

| Rule | Required independent evidence / deterministic result |
| --- | --- |
| UNIQUE_SLOT | Exact frozen schedule membership and economic key: experiment, subject, target, origin, target open/close. Changing an observation ID cannot create another slot |
| NOT_HISTORICAL | Actual contemporaneous source vintage, not the existing 2017–Jan-2026 source or a re-download of its old dates. Renaming source/purpose cannot erase origin/capture history |
| EXACT_FREEZE | Experiment/candidate/calibrator parameters/composition/target and implementation closure exactly match the independently frozen record |
| SOURCE_PINS | Exact base model/scaler/feature schema and provenance from §5, unchanged raw-capture bytes |
| AFTER_FREEZE_EMBARGO | Origin/generation strictly after the real freeze and whole-session embargo; target unknown at freeze |
| TIMELY_CAPTURE | All three forecasts and source inputs durably captured before target open, not merely before delayed label ingestion |
| PAST_ONLY_FEATURES | All feature dependencies available by generation, with immutable actual vintage and qualified cutoff/basis |
| UNKNOWN_TRUTH | Earliest objective truth availability and exposure record strictly after generation/capture. Delaying ingestion or editing a label clock cannot make known truth unknown |
| MATURED | Normal qualified next-session endpoint reached; adjudication at the fixed deadline, not at a favorable partial horizon |
| TRUTH_DEADLINE | Qualified journal truth actually available by target close + 7 calendar days; use the pinned revision rule below |
| INTEGRITY_REPLAY | Required capture bytes/seals/joins verified; recorded replay and the exact admitted numeric verifier pass without fitting/network; absent proof fails closed |
| COMMON_BASIS | Source rights, identity, calendar, action coverage and compatible price basis qualified across inputs/endpoints/all arms |
| NO_EARLY_EXPOSURE | No candidate-specific protected scores/probabilities/class aggregates shown to selection operators; breaches recorded, never ignored |

The actual qualifier must derive these facts from independent custody and pinned
bytes; producer-supplied `passed=true` is not proof. Fingerprints are integrity,
not authentication or administrator-proof WORM. Unknown truth access/provenance
is not positively qualified. Public prices can be known outside the system;
candidate-specific manual protected evaluation also violates the exposure gate.

### Qualification artifact and revision state

The JSON's `qualification_record_design` specifies the future fields and states;
it intentionally contains **no real QUALIFIED_PROTECTED observation**. It reuses
`ArtifactReference` / `CapturedBlobReference`, sealed research envelopes,
`ForecastDateTime`, external Outcome Journal revisions and the same research
store, with a later additive codec, not a new persistence system.

Each record pins experiment/authority/freeze/schedule, slot and observation,
subject/target, publication/acquisition/admission/generation/durable capture and
maturity/deadline clocks, feature/model/scaler/calibrator/composition, distinct
raw/q/benchmark capture references, journal revision, assessment, reason tuple,
replay/evidence-closure references, predecessor and semantic fingerprint. No
public audit contains numeric protected p/q/y. Codecs must preserve tuple/list
JSON round-trip and immutable fields.

| Situation | Required handling; slot remains in the denominator |
| --- | --- |
| Captured before maturity | CAPTURED_PENDING_TRUTH; never a zero/negative label |
| Timely truth received | ELIGIBLE_PROVISIONAL; no scientific aggregation yet. At deadline, seal QUALIFIED_PROTECTED if every rule passes |
| Forecast missing, malformed or late | UNAVAILABLE/REJECTED with reason; never backfill a prediction or replace the scheduled slot |
| Missing truth / partial horizon | Pending until the fixed deadline, then UNAVAILABLE; no indefinite waiting or fabricated endpoint |
| Delayed truth | Accept only qualified evidence available by deadline; after deadline audit-only, no new pair or rescoring |
| Identical delivery retry | Return the existing capture/qualification; count exactly once, not a second observation |
| Duplicate with changed observation ID | Same economic slot rejects duplicate qualification; never increase N |
| Conflicting duplicate / corruption / tamper | Quarantine; INVALID_EXPERIMENT review, not drop the inconvenient row and continue |
| Amended source/input | Original forecast-time features/p/q immutable. No retroactive provider adjustment may overwrite them |
| Amended truth | Append journal history. Select the latest qualified revision objectively available **by that slot's deadline**, using unchanged truth-owner ordering; unresolved conflicting revisions are unavailable. Pin it at deadline; later amendments audit-only |
| Basis/action/calendar cannot be reconciled | Explicit unavailable reason; systemic provenance/authority failure invalidates the experiment, not a convenient exclusion |

The deadline revision rule concretizes FF-2.0's “resolve at fixed deadline and
pin selected revision at closure”; closure retains each already fixed slot
revision. No best-result revision selection. Sparse/failed samples remain sparse.

## 7. Fixed accrual and exact final trigger

Keep FF-2.0 unchanged: **first 500 scheduled origin slots** strictly after freeze
and one whole origin-session embargo, not 500 successful forecasts, 500 positive
labels or “enough significance.” Schedule/order/closures/action handling and
deadline calculation must be externally qualified and pinned before accrual.
No actual start date/calendar/rights/custodian has been supplied, so those JSON
fields remain null and accrual is NOT_STARTED. A test fixture's 2027 dates are
authored examples, not a promise of collection or an exchange calendar.

No replacement slots or extension after missing data. About two trading years
is illustrative duration only. Minima are the existing protocol's screening
floors, not a power guarantee; serial dependence and regime shift may still make
the result inconclusive. No retrospective power estimate/result-based N revision
is performed. An independently justified change before accrual would require a
new protocol review/version; after exposure it must fork with fresh evidence.

**Administrative permission to open** requires ALL:

1. Exact independent freeze and current scoped external rights/collection/final
   grant; immutable candidate and evaluator closures available.
2. The pinned 500-slot schedule is complete: every slot has reached its fixed
   deadline and a sealed terminal qualification or explicit absence, with no
   known unresolved integrity/exposure/authority breach.
3. Independent Evaluation/custodian signs an outcome-blind population/lineage
   attestation. Reviewers may see operational errors/counts, not class balance,
   probabilities, losses, reliability or candidate-specific outcome summaries.
4. Final execution count is zero in the canonical experiment custody, and an
   exact-request durable exclusive claim can be recorded before numeric opening.

**Statistical adequacy is checked inside that single consumed evaluation**, not
used to repeatedly peek or prolong collection: ≥400 common three-arm pairs,
≥80 of each class, ≥80% scheduled-slot coverage, ≥40 complete five-slot blocks;
slots 1–250 and 251–500 each ≥150 pairs and ≥30 of each class. Both comparisons
use that identical intersection/missingness mask. An inadequate completed cohort
yields INSUFFICIENT_EVIDENCE; it does not extend the schedule. The protocol's
primary Brier, log-loss, reliability, stability and uncertainty gates remain
unchanged. Qualification alone is not scientific acceptance.

Maximum final executions **1**. Reuse the existing Evaluation custody pattern:
canonical experiment root/request, exclusive claim + file/directory durability
verification before numeric access. Do not run FF-1's fixed final runner for
FF-2. A crash after claim, even before useful results, is CONSUMED_INCOMPLETE;
no retries, deleted claim, new directory or renamed grant. A demonstrable failure
before any durable claim and with no exposure permits repairing preflight only.
Completed immutable results may be displayed/recorded-replayed; no rescoring,
new bootstrap or “replay” fit. Recovery design/fault tests belong to later
implementation; no final permission service is delivered here.

## 8. Freeze boundary, forks and invalidation

Freeze comes **after** the single authorized development fit/proceed decision
and independent review, **before** any prospective issuance. It must seal the
protocol bytes and authority, external grants, source/model/scaler/native
lineage, exact feature formulas/order/basis, target/horizon, calibrator family,
configuration/parameters, preprocessing, clipping/transformation, raw and wrapper
adapters, candidate/composition, dependency lock/code, selection report and
membership, evaluator/metric/bootstrap policy and verifier, fixed BaseRate
support, calendar/action/clock/revision policy, 500-slot schedule and owners.
The JSON enumerates these pins. Placeholder identities are **not** a freeze.

Source candidate/experiment names remain those in FF-2.0; the actual parameter
and implementation fingerprints are unknown, not fabricated. BaseRate remains
the unsmoothed 20-scheduled-transition benchmark, primitive policy 1.0 / existing
empirical binding 2.0 distinct; final support must be qualified and frozen before
accrual, with no 2025/January-2026 or protected outcomes as support. An additive
FF-2 binding may be needed; do not alter the estimator or legacy fold router.

Any change to parameters, source candidate, features/target, probability map,
solver/selection, comparison masks, metric/bin/interval policy, schedule/accrual,
truth timing/basis or benchmark support invalidates “same frozen candidate.”
Early protected result inspection, dropping unfavorable qualified observations,
retrospective additions, outcome-driven exclusions or undisclosed trials are
exposure breaches. Stop, preserve history, record INVALID_EXPERIMENT when
appropriate, and use a **new experiment/candidate/protocol and fresh evidence**
for scientific changes. Never resurrect FF-1 or consumed FF-2 as untouched.

Post-freeze documentation/UI/logging fixes outside the pinned execution closure
may be reviewed with proof that bytes, timing, eligibility and visibility are
unaffected; append an administrative record. Changes inside the scientific,
capture, clock, qualification, custody or evaluator closure are **not** waived as
“bug fixes.” Before any protected issuance, close/refreeze with new identities
and start boundary; after accrual, stop/fork and do not transfer accumulated
observations as untouched evidence for the changed candidate. Even a numerically
equivalent dependency upgrade needs that review; no vague “same model” exception.

## 9. Machine-readable authority and bounded validation design

Authoritative design artifact:
[data_use_authority.json](qualification_records/ff2_1/data_use_authority.json).
Its semantic seal is SHA-256 of the existing FF canonical JSON projection
excluding `fingerprint`; its `record_kind` is explicitly
GOVERNANCE_DESIGN_NOT_EXECUTION_GRANT. It pins the untouched FF-2.0 document
bytes, source/native identities, historical purpose map/prohibitions, actual
missing grants/freeze/schedule, qualification design, fixed accrual and one-shot
policy. It does not authenticate the author or grant empirical rights.

Authority semantic fingerprint:
`723350f586781ae47497683c57be98472dd359d1d692d41ecd985f886c31f981`.

[Governance tests](../tests/unit/evaluation/test_ff2_data_use_authority.py)
provide an executable **test-only metadata specification** of the thirteen
qualification predicates. The accepted witness is an authored hypothetical
schedule/capture, not real evidence or a production qualifier. The tests verify
the actual authority artifact's seal, refusal flags, source/protocol pins,
historical exclusions and sample/deadline policies, then exercise wrong models,
candidate/schema/target/component substitution, consumed-year relabeling,
pre-freeze issuance, known truth, late/missing capture, immature/delayed truth,
duplicates and missing integrity/calendar/basis/exposure proofs. Round-trip seals,
immutable tuples, arrays and aware timezone normalization reuse existing types.

This intentionally changes **no `src/` runtime file**. Test predicates neither
read private market rows nor supply empirical authority. FF-2.2 must implement
real artifact-derived edge enforcement and port these cases; tests here do not
pretend that sealed boolean attestations certify their own truth. A broad new
registry, persistence engine, rights service or alternative truth labeler would
be outside this task.

## 10. Readiness and FF-2.2 handoff

| Readiness | Result | Boundary / missing prerequisites |
| --- | --- | --- |
| Implementation | **YES — SYNTHETIC ONLY** | Can code immutable sigmoid-candidate/fit/apply interfaces, separate p/q, custody/provenance, pinned replay, Evaluation compatibility and synthetic unit/integration tests without future data |
| Empirical development | **NO** | No FF-2-specific rights admission/fit grant, exact qualified CAL/V1/V2 manifest, admitted empirical adapter/evaluator/verifier or frozen implementation/lock; no actual calibrator parameters |
| Prospective collection | **NO** | Needs empirical selection and independent candidate freeze, actual rights/source vintage/capture qualification, fixed benchmark support, schedule and custodian |
| Final protected evaluation | **NO** | No frozen candidate, qualified cohort, completion attestation or one-shot grant; definition of rules does not supply observations |

FF-2.2 is **CALIBRATION IMPLEMENTATION**, not empirical execution. Add/version the
calibrator and calibrated wrapper through the existing Learning/Forecasting/
Evaluation/custody owners. Keep original RAW codecs and FLC synthetic grants
unchanged; no second trainer or production family. Use authored engineering
inputs only, prove no arbitrary empirical loader path, raw p retention, exact
pins, bounded fit attempts, independent metrics and offline replay. Do not refit
the Logistic source or run native empirical adapters on real rows as “tests.”

FF-2.0 §7 requested implementation pins before empirical access; that obligation
is now FF-2.2's output plus later independent review. It cannot be completed by
inventing hashes for unimplemented code in this governance pass. There is no
permission here to fit/select the actual candidate, collect live data, inspect
protected results, activate models or publish a forecast capability. The next
implementation request can safely proceed under the synthetic boundary without
waiting months for final evidence; empirical execution remains a separate gate.

Remaining scientific limitations: old fixed base artifact, one symbol, small
single-year calibration block, known reused validation years, later adjusted
historical vintage/non-PIT limitations, volume/action uncertainty, unverified
external rights, dependent samples and no guaranteed power. No claim calibration
will improve Logistic; an insufficient result is acceptable. FF-0 behavior and
FF-1/FLC science stay frozen.

```text
FF2_PROTOCOL_DEFINED = YES
FF2_DATA_USE_AUTHORITY_DEFINED = YES
FF2_HISTORICAL_DEVELOPMENT_USE_RESOLVED = NO
FF2_PROSPECTIVE_EVIDENCE_DEFINED = YES
FF2_PROSPECTIVE_QUALIFICATION_RULES_DEFINED = YES
FF2_CANDIDATE_FREEZE_BOUNDARY_DEFINED = YES
FF2_FINAL_EVALUATION_TRIGGER_DEFINED = YES
FF2_IMPLEMENTATION_READINESS = YES
FF2_EMPIRICAL_DEVELOPMENT_READINESS = NO
FF2_FINAL_PROTECTED_EVALUATION_READINESS = NO
FF1_PRESERVED = YES
FLC_PRESERVED = YES
FF0_PRESERVED = YES
```

`FF2_DATA_RIGHTS_RESOLVED = NO`. The historical-use NO denotes missing empirical
authority, not ambiguity in scientific partitions. Source permission cannot be
manufactured from this task's authorization to design governance.

**GO_FF2_SYNTHETIC_IMPLEMENTATION_ONLY**

## 11. Validation and changed files

| Fresh validation | Result |
| --- | --- |
| Governance + existing rights + Evaluation normalization + FF-0 acceptance | **159 passed in 39.72s**, no warnings/failures/skips: 37 new governance, 45 rights, 49 normalization, 28 FF-0 |
| Compileall `src scripts` | PASS |
| Ruff `src tests scripts` | PASS |
| mypy `src tests` | PASS, 677 source files |
| Existing documentation links/anchors | PASS, 957 local links across 14 Markdown files (12 changed/new plus two fixed handbook inputs) |
| Authority seal, native model/scaler semantic and byte pins, source/qualification byte pins, protocol hash | MATCH |
| Four FF-1 fingerprints / frozen pins / terminal status | MATCH / 78 of 78 MATCH / CONSUMED, one execution, no refit, inconclusive |
| FLC tagged `src scripts pyproject.toml uv.lock requirements` | No diff |
| FF-0 tagged native source and acceptance corpus | No diff |
| Historical FF-1/FLC and FF-2.0 reports | No diff against entry HEAD |
| New Markdown fences/whitespace and `git diff --check` | PASS |

Commands used the existing virtual environment:

```bash
.venv/bin/pytest -q tests/unit/evaluation/test_ff2_data_use_authority.py tests/unit/forecasting/test_research_rights_policy.py tests/unit/forecasting/test_evaluation_normalization.py tests/acceptance/ff0 --tb=short
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
.venv/bin/python -c 'from docs.handbooks.a7_forecasting.validate_handbook import validate_links; print(validate_links(True))'
git diff --check
```

The initial 36-test pass exposed a Pydantic field-shadowing warning in the new
test-only witness. Renaming `schema` to `feature_schema` removed it; the final
37-case specification above includes the added fixed-source/protocol check.
A preliminary 130-test slice is superseded by the final 159, not additive.
An isolated-file mypy invocation lacked the source roots; the final repository
command `mypy src tests` passes. No whole-repository pytest run is claimed:
this pass changes only documentation, one metadata artifact and its test-only
specification. The selected slice exercises affected governance contracts and
frozen compatibility; prior FLC full-suite results remain historical.

Created (three paths):

- `docs/TIAF_A7_FF2_1_DATA_USE_AUTHORITY_AND_PROSPECTIVE_EVIDENCE_QUALIFICATION.md`
- `docs/qualification_records/ff2_1/data_use_authority.json`
- `tests/unit/evaluation/test_ff2_data_use_authority.py`

Updated current navigation/status only (eleven paths):

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/IMPLEMENTATION_ROADMAP.md`
- `docs/MILESTONES.md`
- `docs/TIAF_A7_DETAILED_ROADMAP.md`
- `docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md`
- `docs/TIAF_CAPABILITY_MAP.md`
- `docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md`
- `docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md`
- `docs/TIAF_IMPLEMENTATION_TARGETS.md`
- `docs/TRADINGINTELLIGENCE_ROADMAP.md`

No source change, empirical execution, FF-1 rescore, calibration fit, market-data
call, commit, tag or push. The only network request was read-only Git verification.
