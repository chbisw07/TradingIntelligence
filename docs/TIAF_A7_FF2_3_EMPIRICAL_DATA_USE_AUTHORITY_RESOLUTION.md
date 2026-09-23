# A7 / FF-2.3 — Empirical data-use authority resolution

Reviewed 2026-09-23, Asia/Kolkata. **EMPIRICAL_AUTHORITY_UNVERIFIABLE.**
The authority-resolution pass is complete; empirical development is **not ready**.
There is no grant and no empirical fit, forecast generation, calibrated-output
inspection, scoring, protected opening, promotion or activation in this pass.

**HOLD_FF2_EMPIRICAL_DEVELOPMENT**

## 1. Baseline and scope

| Precondition | Verified observation |
| --- | --- |
| Branch / entry worktree | `main` / clean |
| HEAD, local `origin/main`, live remote `main` | `bd80dff52c61aad772e25e70d3d29fec5f4e0d0c` |
| Committed and pushed FF-2.2 | `TIAF A7: implement FF-2.2 synthetic calibration infrastructure` |
| FLC tag object, local and remote | `08767b720c62410166717a6df0002a7e9e24e692` |
| FLC tag peeled commit | `5f1e80c7e0614233b5670ca3acf9229edd0ea0db` |
| FF-1 preservation at entry | Four scientific fingerprints MATCH; 78/78 frozen pins MATCH |

The first remote query failed sandbox DNS; the approved read-only `git ls-remote`
retry verified the actual remote. No Git write was performed.

Authority was checked against the unchanged [FF-2.0 protocol](TIAF_A7_FF2_0_CALIBRATED_LOGISTIC_RESEARCH_PROTOCOL.md),
[rights/readiness inventory](TIAF_A7_FF2_0_BASELINE_DATA_RIGHTS_AND_READINESS.md),
[FF-2.1 governance](TIAF_A7_FF2_1_DATA_USE_AUTHORITY_AND_PROSPECTIVE_EVIDENCE_QUALIFICATION.md),
[its sealed design](qualification_records/ff2_1/data_use_authority.json),
[FF-2.2 implementation](TIAF_A7_FF2_2_SYNTHETIC_CALIBRATION_INFRASTRUCTURE.md),
[FLC closure](TIAF_A7_FLC_8_REFERENCE_IMPLEMENTATION_CLOSURE_AND_FLC_ACCEPTANCE.md#13-authorized-family-neutral-inference-reconciliation),
[historical rights policy](TIAF_A7_FF1_1A_RIGHTS_POLICY_REVISION_AND_DATA_PROVISIONING.md),
[adjusted qualification](TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md),
and [FF-1 scientific closure](TIAF_A7_FF1_INDEPENDENT_FINAL_SCIENTIFIC_CLOSURE_AND_BASELINE_DECISION.md).
The local source, qualification, grant, model, scaler, training manifest/run and
their nested identities were inspected without invoking fitting or forecasting.

This is repository scientific-governance evidence, not external legal-rights
certification. An integrity seal authenticates neither the research owner nor a
provider license. No provider terms were newly researched, no credentials read,
and no provider/network operation occurred except the read-only Git check.

## 2. Actual source and historical exposure

One inspected qualified empirical source: `data/ff1/reliance/reliance_daily_ohlcv.csv`,
99,118 bytes, 2,045 daily rows, 2017-11-01 through 2026-01-30. TI-native Dhan
RELIANCE/NSE cash equity, security 2885, ISIN INE002A01018; acquired
`2026-09-21T12:07:50.995917+05:30`. Raw provider responses were not retained.
Fresh date-column inventory and byte hashes match FF-2.1. No new data acquisition.

The training-granted qualification is
`data/ff1/adjusted_qualification_20260921_clock_review/qualification.json`,
not the older `_final` checkpoint. It uses `ff1.adjusted_retrospective/1.0`:
later-vintage adjusted prices, provider-defined volume, binary64-normalized
values, bounded corporate-action/calendar review and assumed historical
availability. It is **not CAPTURED_AS_KNOWN** or forensic raw-decimal evidence.

| Source period / exact first–last date / rows | Recorded previous uses and exposure | Possible FF-2 scientific role, conditional on new authority |
| --- | --- | --- |
| 2017-11-01–2017-12-29 / 42 | Known warm-up/feature-support prices; not a standalone scored label population | Past-only support and lineage, not fit/final |
| 2018-01-01–2018-12-31 / 246; 2019-01-01–2019-12-31 / 245 | All 491 included in selected 2022 model training; labels were used | Read-only training lineage; no new base/scaler fit |
| 2020-01-01–2020-12-31 / 252 | 229 train rows in 2021 fold, 231 in selected 2022 fold; action exclusions/purge retained | Same lineage/past-only support |
| 2021-01-01–2021-12-31 / 248 | 246 selected-model training rows, 248 later-fold training rows; 248 FF-1 development pairs and diagnostics | Known training/validation history, not calibrator-fit rows |
| 2022-01-03–2022-12-30 / 248 | 248 FF-1 development pairs and diagnostics; 246 train rows in 2023 fold, 248 in 2024 fold; **zero in selected 2022 model training** | Conditional one-time CALIBRATION subset; not protected |
| 2023-01-02–2023-12-29 / 246 | 225 FF-1 qualified development pairs/diagnostics; 223 train rows in 2024 fold; eligible history also used by fifth fold | Conditional known V1 validation/diagnostics/proceed-stop |
| 2024-01-01–2024-12-31 / 249 | 248 FF-1 development pairs/diagnostics; eligible history used by fifth fold | Conditional known V2; exclude any target/dependency reaching 2025 |
| 2025-01-01–2025-12-31 / 249 | One consumed FF-1 final execution and published final diagnostics; outcomes exposed | **DENIED for all FF-2 numeric roles**, including benchmark/feature support; hashes/status only |
| 2026-01-01–2026-01-30 / 20 | Known acquired later history; endpoint context may support last FF-1 target; not all rows claimed scored | **DENIED for v1 numeric roles** and never newly protected |
| Later pre-freeze data | No qualified independent corpus/issuance history identified | No implicit acquisition/use permission; cannot backfill as prospective |
| Future post-freeze data | No actual candidate freeze, schedule, corpus or custodian | Prospective design only; no collection/final permission |
| FLC and FF-2.2 fixtures | FLC fixed 600-row and trial 680-row authored recipes, authored calibration tables; FF-2.2 compiled 60-pair fit sample | Synthetic engineering only, never empirical evidence |

Fresh metadata checks reproduced FF-1 training sizes 720 / 968 / 1,216 / 1,441
and the per-year selected-model counts above. Every admitted training ID's target
and assumed label clock precedes its fold cutoff. Training grant, qualification,
schema, nested model/scaler and manifest/run joins match. Existing qualification
metadata records FF-1 development potential 248 / 248 / 225 / 248; these are
**not new FF-2 membership or class-support counts**. Exact CAL/V1/V2 membership
has not been materialized here.

The recorded sequence is: acquisition/qualification and fixed feature development
→ four development fits → 991 forecast records (969 generated, 22 excluded)
→ 969 development pairs/diagnostics → separately authorized fifth fit (1,690
rows) → one protected final execution → independent closure. Grant/run/report
identities are retained in FF-2.1 §2 rather than inventing a new historical
experiment ID. The fifth-fold model is not the FF-2 source.

Known agent inspection includes those recorded engineering/scientific passes
and their reports; outputs were exposed in repository reports for user review.
Repository evidence cannot prove which reports the human actually read, nor
exclude private/unlogged exploration. Exposure is a lower bound, not an unseen
certificate. No empirical hyperparameter search or calibration-like fitted
transform is recorded in the accepted FF-1 runs. FLC optimization/calibration
and FF-2.2 fitting are synthetic only. FF-2.0/.1 inspected metadata and published
history; this pass adds provenance/authority review, not numeric research.

## 3. Authority determinations

| Question | Finding |
| --- | --- |
| 2022 calibration-use authority | **UNVERIFIABLE / NOT GRANTED** |
| 2023–2024 development-use authority | **UNVERIFIABLE / NOT GRANTED** |
| Partially granted empirical purposes | None |
| 2025 and January-2026 numeric use | Explicit protocol prohibition; not merely missing permission |
| Prospective-only route now | Not ready: no accepted candidate/freeze, source qualification, schedule or collection authority |

Custody exists; permission does not follow. The accepted rights audit is still
`UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING`, with warning
`RIGHTS_NOT_APPROVED_RESEARCH_ONLY`. The FF-1 grant
`ff1.2:four-development-artifacts` binds its own qualification and four fits.
The FLC and FF-2.2 grants are synthetic-only. FF-2.1 explicitly records a null
empirical grant. No later scoped FF-2 use admission or exact empirical fit grant
was found in the inspected repository governance/custody evidence.

This task authorizes checking permission, not issuing it. Therefore no synthetic
grant is widened and no default WARN_ONLY setting is treated as owner consent.
UNVERIFIABLE is used instead of DENIED for 2022/V1/V2: their scientific roles
are conditionally coherent, but permission is absent. There is no verified
provider denial asserted by this report either.

### 2022: out-of-training-sample is not historical PIT

The selected model uses 968 training origins, 2018-01-01–2021-12-29, with
cutoff/embargo `2021-12-31T09:15:00+05:30`. Its scaler has the same 968 rows.
Neither includes 2022. The fact that **other** frozen models used 2022 does not
create train overlap for this exact model. Prior known validation/diagnostic
use does not itself prohibit a transparently declared development calibration
set under FF-2.0; it does prohibit claiming unseen confirmation.

The original training admission excludes later origins before feature/label
access, enforces target/label maturity before fit, and passes only TRAIN rows
to StandardScaler and the worker. Existing source and metadata show no direct
2022 label-to-scaler/model-fitting path. Feature formulas use trailing facts.
That is split-time leakage control, **not proof of true historical PIT safety**:
the adjusted data vintage was acquired in 2026. No false actual historical
issuance or complete corporate-action/volume certainty is claimed.

No recorded previous 2022 calibration-like parameter tuning was found; absence
of a record cannot certify absence of undocumented exploration. A future owner
must acknowledge that exposure and the retrospective basis explicitly.

### 2023–2024: known development only

Conditional uses are calibration diagnostics, fixed-candidate validation,
prespecified annual/pooled stability, proper-score comparisons and deterministic
proceed/stop. They do not permit refitting, alternative methods, changing bins,
selecting favorable years or protected/final relabeling. They remain known even
after regeneration, new IDs or a new transform. Nothing runs under this report.

## 4. Exact Logistic identity and generation limits

The [sealed resolution](qualification_records/ff2_3/authority_resolution.json)
contains full semantic and byte pins. Fresh checks:

| Dependency | Verified identity |
| --- | --- |
| Native forecaster | `forecaster:logistic-regression`, implementation/artifact 1.0, 2022 fold, CHALLENGER / EXPERIMENTAL |
| Model semantic | `7cbe4f2b14a72ae5e2af40c535710f1695687b81786f0c69efd271b50442a5d2` |
| Model bytes | `6f5b4c8cfa794073500c680d322f7ee3501126f4751eac1d301a66ce9ec61d6a` |
| Scaler semantic | `39e888ce1789405f4bdc9fa704e0f6ac43adfc5aaade55bc211d5c9f0986eb62` |
| Scaler bytes | `ea956a9a6612bd8c14023fe67caf63f05e5bf17744415ed891694ad430d47245` |
| Training run / manifest | `f26605528584a68449396da9dea1a3e28d6e2295f355a7085887e5adedc94406` / `da5ecbd29a3577cc21baeba4786848de36dc533a25ca7135f2896b6ca0d429f9` |
| Feature schema | `ff1.reliance.a2_daily_five/1.0`, `76e63292685ee0b3b41f7ab033407e6bd014fc802d2092a2ed227888bdc71676` |
| Ordered features | `ret_1`, `ret_5`, `sma20_distance`, `realized_vol_20`, `relative_volume` |
| Reconstruction | `52837a1beb5d9bcab74666d13db5f33b64d30bf41e30d1e7917872fffcad8127` |
| Source dataset / qualification | Byte and semantic identities MATCH FF-2.1; exact values in resolution |

Model and scaler files are under `data/ff1/logistic_training_20260921`.
The model's embedded manifest equals the separate manifest; its reconstruction
scaler equals the separate scaler; the selected training job contains that same
artifact. Verification is hash/metadata-based, not a new prediction calculation.

The native [generator](../src/tiaf/forecasting/logistic_forecasts.py) chooses a
model by **origin year**. Saved 2023/2024 outputs therefore cannot be reused as
this fixed model's raw arm. The [reconstruction primitive](../src/tiaf/learning/forecast_artifacts.py)
retains dependency-free deterministic inference mechanics and historical
reconstruction evidence; no new empirical numerical reproducibility check was
run. A later separately admitted `ff2.reference.1` adapter must bind the exact
2022 model/scaler for all admitted origins and record new immutable capture IDs,
actual computation clocks, simulated cutoffs, byte closure and a pinned numeric
verifier (≤1e-12 per the protocol). It must compare regenerated outputs against
that same new identity, not against a different-year legacy artifact.
No silent refit, current alias, fallback model or change to native year routing.

## 5. Custody design and actual enforcement delivered

[empirical_authority.py](../src/tiaf/learning/empirical_authority.py) adds a small
Learning-owned refusal record and pure metadata review using the existing
`SealedResearch`, `ArtifactReference`, fingerprint and aware-clock conventions.
It adds no registry, trainer, truth labeler, loader, storage engine or grant issuer.

- `EmpiricalAuthorityResolution` permits only UNVERIFIABLE and null grant; all
  execution/collection/final/promotion flags are false, current execution limit 0.
- `require_empirical_development_authority` revalidates and always denies before
  numeric access. There is deliberately no success path in this version.
- `DevelopmentCustodyMetadata` references captured raw probability and external
  Ground Truth without containing or decoding p/q/y. At most 4,096 proposal rows.
- `review_development_metadata` returns a sealed **denied** review even when all
  structural joins pass. It checks supplied metadata, not independent evidence
  authenticity. It is not plugged into an empirical runner because none is
  admitted; the existing FF-2.2 fit edge still rejects empirical input unchanged.

These distinctions are intentional: a test-only consistent proposal is not an
accepted empirical record. Numeric custody qualification, journal extraction,
calendar/action checks and pinned numerical verification still require an
artifact-derived owner edge and new authorization; self-attested fields cannot
replace them. No actual empirical proposal population is created in this pass.

| Future admitted record must retain | Owner/check |
| --- | --- |
| Observation ID and economic key (experiment, subject, target, origin/target interval) | Qualification/custody; duplicates and renamed copies cannot increase N |
| Forecast capture with original finite raw p in [0,1], raw schema and byte hash | Existing Forecasting owner, exact source capture; separate q later, never overwrite p |
| Model/scaler/schema/training/config/adapter/code/lock pins | Learning/adapter; exact identities and bytes, no model or scaler fit |
| Source dataset/manifest/profile, feature capture and every dependency clock | Existing qualification owner; no future data or 2025/January-2026 support |
| Origin, simulated cutoff, target open/close, horizon | Existing target/calendar owner; next-session close, no inference from string year alone |
| Actual acquisition/generation/persistence versus assumed historical availability | Preserve 2026 clocks; do not backdate acquisition/issuance |
| External journal reference/revision, matching observation/subject/target, maturity and availability | Existing Ground Truth owner only; no calibrator labels or immature targets |
| Qualified membership/masks, use authority, exposure/custody state, byte closure, verifier result | Independent qualification/custody; absent or unverifiable proof denies |

Historical label revision policy: pin one externally qualified journal revision
and endpoint basis in the pre-fit population; retain amendments as append-only
audit. A revision is not a license to refit or rescore after exposure. A material
error yields INVALID/independent review and, if authorized, a new experiment;
never silently overwrite. Future prospective deadline policy remains FF-2.1's
latest-qualified-by-fixed-deadline rule, not this historical proposal policy.

Resolution fingerprint:
`15a8fb667ad5ec793c737de929cebea5de0c281687c83316fa1e5bfef4ceb8ec`.
It records the absence of authority; it is **not an empirical grant**. Repeated
serialization of the same contents yields the same seal. A different review
clock/content is a new record, not an in-place grant mutation.

## 6. Conditional execution accounting and numerical freedom

**Current authorized executions: zero.** The following preserves FF-2.0's future
budget and is not permission to use it. A later grant must bind canonical
experiment/custody root, exact request/input membership, rights admission and
code/dependency pins; same existing FLC request/execution/result/attempt owners.

| Operation | Conditional count and consequence |
| --- | --- |
| Metadata preflight fails before claim, no numeric exposure | May repair preflight; append failure record; no candidate fit consumed |
| Calibrator fit | One durable exclusive request/root claim, file + directory durability, **before worker/numeric opening**; one attempt, 60s/512 MiB/one thread |
| Technical failure after claim, including before useful output | CONSUMED_INCOMPLETE; no retry, new grant alias or relocated directory; independent incident review, not automatic resume |
| Scientific rerun after outputs/results | Forbidden within this experiment; new identity/authority required, old exposure retained; cannot rescue this candidate |
| Candidate/configuration mutation | Invalidates same-candidate claim; record INVALID and seek separate experiment/protocol review, not a second v1 trial |
| Development selection | One pinned bundle: both annual blocks and pooled diagnostics, two paired comparisons on the same three-arm mask; no selective reruns |
| Diagnostic rerun | Recorded immutable display/replay is equivalent and grants no fit. Numeric recomputation is a new execution record; no such extra execution is granted here. Pin intended diagnostics before the one bundle |
| Final protected opening | Separate authority, maximum one durable claim after cohort closure; zero authorized now; crash consumes, no rescoring retry |

Even deterministic numerical repetition is an execution, not recorded replay.
Correcting a bug is not permission to alter data, parameters, methods or exposure.
No experimental execution-claim file is created while authority is absent.

| Degree of freedom | Classification / fixed rule |
| --- | --- |
| Intercept a, slope b | The only scientifically estimated parameters; one unweighted binary-log-loss fit on admitted CAL only; b must be positive and finite |
| Transform, objective, method | Frozen sigmoid(a + b × logit(clamp(p))); no penalty, class weighting, augmentation or other calibrator |
| Clamp epsilon | Frozen protocol value 1e-15; never overwrite original p |
| Initialization / convergence / iteration limit | Frozen (0,1), gradient infinity norm ≤1e-8, 1,000 iterations |
| Solver | Implementation parameter already concretized by FF-2.2: Newton/Armijo, ≤32 backtracks, step 0.5^k, Armijo 1e-4, singularity threshold 1e-15; no result-driven solver swap |
| Execution implementation / dependency lock | Must be byte-pinned with an independently reviewed empirical adapter/verifier before access; synthetic implementation acceptance alone is not empirical admission |
| Failure | Nonfinite, nonpositive slope, separation, singularity, line-search failure or nonconvergence stops; no fallback regularization, reversal, clipping grid or rescue fit |

The synthetic kernel is byte-preserved. Numerical implementation identity must
be included in any later actual grant; this report does not fabricate hashes
for missing empirical components. Evaluation-only offset/intercept/slope
diagnostics never feed parameters back into the candidate. No FLC-3 search.

## 7. Conditional development flow and decisions

```text
Owner's scoped use admission + exact one-attempt grant + qualified membership
    → pinned 2022 model raw captures on admitted 2022 observations
    → one calibrator fit → freeze parameters/candidate/closure
    → known 2023 V1 + known 2024 V2 (raw / calibrated / BaseRate)
    → one independent Evaluation bundle → deterministic development decision
    → if DEVELOPMENT_ACCEPTED: independent prospective freeze review
    → only after separate authority: future accrual → one protected opening
```

No link in this sequence is executed here. BaseRate stays BENCHMARK; Logistic
stays CHALLENGER / EXPERIMENTAL. Preserve unsmoothed last-20-scheduled-transition
BaseRate, no support optimization/backfill; no forbidden-year support.

Retain FF-2.0 §§8–10 exactly: CAL ≥200 admitted pairs and ≥50 per class;
each V block ≥150 common pairs, ≥30 per class, ≥80% scheduled coverage and ≥20
complete five-slot blocks. Pooled calibrated-minus-raw Brier must be <−1e-6 and
negative in each year. Against each raw/BaseRate comparator, annual Brier/log-loss
worsening ≤0.02/0.05; pooled log-loss worsening ≤0.01. Use the fixed calibration
guardrails (absolute mean error ≤0.05, ECE ≤0.08 and ≤raw+0.02, ≥80% in bins with
≥20 support), all annual/pooled diagnostics and retained missingness. These are
predeclared floors, not a power guarantee; no recalculation or tuning here.

| Development status | Meaning; precedence |
| --- | --- |
| `FF2_DEVELOPMENT_INVALID` | First: authority, lineage, leakage, prohibited exposure, unauthorized retry or mutation breach; no scientific win/lose claim |
| `FF2_DEVELOPMENT_INSUFFICIENT` | Valid but insufficient membership/support/estimability; no borrowing from validation/final, no automatic extra data |
| `FF2_DEVELOPMENT_ACCEPTED` | All predeclared development gates pass; eligible for independent prospective-freeze review only |
| `FF2_DEVELOPMENT_REJECTED` | Valid adequate evidence fails proceed/stop, including tie/no improvement or fixed quality/stability gate failure; no alternative calibrator tried |

These are documented decision labels, not new runtime approval enums. No
development status is assigned to real data in this pass. Later
`FF2_FINAL_ACCEPTED / REJECTED / INSUFFICIENT` map to the unchanged protocol's
ACCEPTED / REJECTED / INSUFFICIENT_EVIDENCE; INVALID_EXPERIMENT remains separate.
Final acceptance is not promotion eligibility or activation. The future first
500 scheduled slots, whole-session embargo, maturity deadlines and one-shot
trigger remain unchanged; no known history can fill them.

## 8. Leakage guards, tests and limitations

[New tests](../tests/unit/evaluation/test_ff2_empirical_authority.py) exercise
authored metadata only. They check denial independently of optional consistency
findings: an internally consistent proposal remains unauthorized.

| Risk | Implemented metadata negative check / remaining artifact-level obligation |
| --- | --- |
| Wrong source model/scaler/schema/training | Exact source identity and byte-pin projection rejects substitutions; actual byte closure must later be derived by admitted owner |
| Target/temporal/scaler leakage | Target/subject/horizon joins, TRAIN cutoff before origin, trailing dependency clocks before cutoff, CAL target/label before embargo |
| Post-horizon contamination | Future feature/support dependencies and target clocks reject; actual next-session calendar/basis proof remains required |
| Duplicate observation | Reused ID, same economic origin even with renamed ID/purpose, or reused raw capture rejects within proposed population; no persistent empirical admission exists yet |
| Inspection contamination | Known-development only; consumed, prospective, unknown and protected relabeling reject; no proof about unlogged external reading is fabricated |
| Regeneration mismatch | Different code/capture references reject; actual numerical equivalence is not inferred from matching self-supplied hashes |
| Dataset mutation/tamper | Wrong source/qualification byte pins reject; model revalidation rejects stale seals, including model_copy bypass attempts |
| Truth leakage/revision | Observation/subject/target/interval/maturity/journal/revision joins reject; label extraction remains external Ground Truth owner |
| 2025 / January2026 / prospective use | Prohibited numeric dependency clocks and wrong periods/exposure reject before any numeric load |
| Unauthorized positive grant | Literal false/null/zero resolution fields reject grant injection; authority function has no success branch |

Also test deterministic sealed round-trip, frozen fields/tuple collections with
JSON arrays, UTC normalization to Asia/Kolkata, naive rejection, row bounds,
unknown numeric fields, and no file/network/subprocess side effects. There is
no positive grant fixture or positive empirical acceptance claim. Existing
FF-2.1 specification and FF-2.2 synthetic admission tests are rerun unchanged.

## 9. Validation

Fresh focused run: **628 passed in 272.23s (4m32s)**, no failures or skips.
Counts below are disjoint modules in that invocation, not extra test executions.

| Focused component | Passed |
| --- | ---: |
| New FF-2.3 authority/custody tests | 63 |
| Existing FF-2.1 governance | 37 |
| Existing FF-2.2 synthetic calibration | 52 |
| FLC seams / neutral inference / lifecycle / optimization | 27 / 51 / 55 / 60 |
| FLC diagnostics / calibration / Evaluation normalization / integration-replay | 31 / 58 / 49 / 54 |
| Capture/store/replay / pinned-runtime replay | 48 / 15 |
| FF-0 acceptance corpus | 28 |
| **Total** | **628** |

| Other gate | Result |
| --- | --- |
| Full repository pytest (required for new governance source) | **3,982 passed in 852.87s (14m12s)**; no failures or skips |
| Compileall `src scripts` | PASS |
| Ruff `src tests scripts` | PASS |
| mypy `src tests` | PASS, 686 source files |
| Documentation links/anchors | PASS, 987 local links across 14 Markdown files |
| Four FF-1 scientific fingerprints | 4/4 MATCH, canonical metadata hashing only |
| Frozen FF-1 files | 78/78 MATCH (72 source + 6 implementation pins) |
| Existing tracked `src`, scripts, dependency files | No diff against entry HEAD; only one additive source module |
| FF-0 native sources and checked-in acceptance artifacts | No diff against `tiaf-a7-ff0-baseline` |
| Historical FF-2.0/.1/.2 and FLC closure reports | No diff against entry HEAD |
| Markdown fences, new-file whitespace and `git diff --check` | PASS, including final documentation edits |

The four unchanged scientific identities are those in FF-2.1's `historical_ff1`
record: protocol `2664b2d4…`, execution `2948bc46…`, evaluation `8c0556e7…`,
ledger `630dd96c…`; full 64-character values were compared. Final FF-1 remains
INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE; 2025 CONSUMED; one execution,
no refit; BaseRate BENCHMARK and Logistic CHALLENGER / EXPERIMENTAL.

Commands used the existing `.venv`:

```bash
.venv/bin/pytest -q tests/unit/evaluation/test_ff2_empirical_authority.py tests/unit/evaluation/test_ff2_data_use_authority.py tests/unit/forecasting/test_sigmoid_calibration.py tests/unit/forecasting/test_forecaster_seams.py tests/unit/forecasting/test_neutral_inference.py tests/unit/forecasting/test_forecaster_lifecycle.py tests/unit/forecasting/test_optimization.py tests/unit/forecasting/test_forecaster_diagnostics.py tests/unit/forecasting/test_calibration.py tests/unit/forecasting/test_evaluation_normalization.py tests/unit/forecasting/test_lifecycle_integration.py tests/unit/forecasting/test_capture_store_replay.py tests/unit/forecasting/test_pinned_runtime_replay.py tests/acceptance/ff0 --tb=short
.venv/bin/pytest -q --tb=short
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
.venv/bin/python -c 'from docs.handbooks.a7_forecasting.validate_handbook import validate_links; print(validate_links(True))'
git diff --check
```

An initial new-test collection failed on an incorrectly named authored-fixture
argument (`version` instead of `artifact_version`); it was fixed before the
final focused/full runs. Formatting warnings were likewise fixed. The earlier
62-test preliminary run is superseded by the 63-case final module above. No
failed or preliminary run is counted as an additional passing gate. Tests may
execute accepted synthetic workers; no empirical experiment command was run.

## 10. Closure and required next authority

Delivered: this report, sealed refusal record, one bounded Learning metadata
review module and tests; current navigation updated without editing historical
FF-2.0/.1/.2 or frozen FLC/FF-1 records. No existing data/artifact, dependency or
scientific-policy change.

Created (four paths):

- `docs/TIAF_A7_FF2_3_EMPIRICAL_DATA_USE_AUTHORITY_RESOLUTION.md`
- `docs/qualification_records/ff2_3/authority_resolution.json`
- `src/tiaf/learning/empirical_authority.py`
- `tests/unit/evaluation/test_ff2_empirical_authority.py`

Updated navigation/status only (eleven paths): `README.md`,
`docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_ROADMAP.md`, `docs/MILESTONES.md`,
`docs/TIAF_A7_DETAILED_ROADMAP.md`,
`docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md`,
`docs/TIAF_CAPABILITY_MAP.md`, `docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md`,
`docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md`,
`docs/TIAF_IMPLEMENTATION_TARGETS.md`, `docs/TRADINGINTELLIGENCE_ROADMAP.md`.

Remaining blockers, in order:

1. Accountable research owner must explicitly adopt a scoped FF-2 WARN_ONLY
   research-use admission with uncertainty acknowledged **or** supply verified
   use evidence; explicit provider denial blocks either route. This is not a
   request to infer legal rights from repository accessibility.
2. Exact CAL/V1/V2 membership, retrospective limitations/exposure, journal/basis,
   source/feature bytes and leakage/custody checks must be independently qualified.
3. Separately reviewed/pinned fixed-source empirical adapter, calibrated wrapper,
   common-mask Evaluation profile and numerical verifier must exist; preserve
   synthetic contracts and native FF-1 routers.
4. A new exact one-attempt calibrator grant must bind those artifacts, experiment,
   request and canonical custody root. No implicit authority from this resolution.
5. Prospective collection/final permission requires a later accepted candidate,
   independent freeze and actual schedule/custodian/qualified source basis.

`FF2_EMPIRICAL_DATA_LINEAGE_RESOLVED = YES` means the recorded repository lineage
and its limitations have been reconstructed, **not** verified external rights,
complete knowledge of private inspection, true historical PIT, or execution
readiness. UNVERIFIABLE is an explicit completed authority-review finding.

```text
FF2_EMPIRICAL_DATA_LINEAGE_RESOLVED = YES
FF2_2022_CALIBRATION_AUTHORITY = UNVERIFIABLE
FF2_2023_2024_VALIDATION_AUTHORITY = UNVERIFIABLE
FF2_PINNED_LOGISTIC_IDENTITY_VERIFIED = YES
FF2_EMPIRICAL_CUSTODY_DEFINED = YES
FF2_EMPIRICAL_EXECUTION_POLICY_DEFINED = YES
FF2_EMPIRICAL_AUTHORITY_GRANTED = NO
FF2_EMPIRICAL_DEVELOPMENT_READINESS = NO
FF2_FINAL_PROTECTED_EVALUATION_READINESS = NO
FF1_PRESERVED = YES
FLC_PRESERVED = YES
FF0_PRESERVED = YES
```

No empirical fitting, forecasting, calibration diagnostics/scoring, protected
evaluation, refit, retune, A8/IFL, promotion or activation. No commit, tag or push.
