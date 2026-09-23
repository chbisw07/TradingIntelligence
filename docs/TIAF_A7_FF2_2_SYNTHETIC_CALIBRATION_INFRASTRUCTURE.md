# A7 / FF-2.2 — Synthetic calibration infrastructure

Date: 2026-09-23, Asia/Kolkata. **Implemented, synthetic engineering only.**
Empirical development, prospective collection, final protected evaluation,
promotion and activation remain unauthorized. This is not scientific evidence
that calibration improves Logistic.

## 1. Entry and scope

Entry `main` was clean. HEAD, local `origin/main` and read-only live remote main
all matched `e893c3ae426bea2f89ef7e158dccd79940186600`:
`TIAF A7: complete FF-2.1 data-use authority and prospective evidence governance`.
Local/remote `tiaf-a7-flc-baseline` remained annotated object
`08767b720c62410166717a6df0002a7e9e24e692`, peeled commit
`5f1e80c7e0614233b5670ca3acf9229edd0ea0db`.

The [FF-2.0 scientific protocol](TIAF_A7_FF2_0_CALIBRATED_LOGISTIC_RESEARCH_PROTOCOL.md),
[readiness history](TIAF_A7_FF2_0_BASELINE_DATA_RIGHTS_AND_READINESS.md),
[FF-2.1 governance](TIAF_A7_FF2_1_DATA_USE_AUTHORITY_AND_PROSPECTIVE_EVIDENCE_QUALIFICATION.md)
and [authority design artifact](qualification_records/ff2_1/data_use_authority.json)
are unchanged. The FF-2.1 empirical model/scaler/schema pins remain exact; this
task does **not** decode those artifacts for prediction or consume their market
inputs. The synthetic source below is explicitly a different authored model.

## 2. Inspected seams and bounded extensions

| Seam | Entry finding | This implementation |
| --- | --- | --- |
| Neutral inference / immutable RAW output | EXISTS | Unchanged; synthetic adapter uses `run_inference` |
| FLC-2 training identity, authority, execution and custody | EXISTS | Reused for a separate Learning **calibrator capability**, not a second Logistic trainer |
| FLC-5 calibration identity / edge / target | EXISTS; executable learned sigmoid MISSING | Reuses `CalibrationComponent`, `CalibrationTarget`, `ForecastEdge`; adds versioned fitted artifact |
| FLC-5 fit | Proposal-only, authored-table execution | Preserved exactly; no weakening of old literals |
| Calibrated common result | NEEDS_BOUNDED_EXTENSION; native probability is literally RAW | Additive `CalibratedCapture` wrapper; no q in a RAW probability codec |
| Content-addressed store / canonical seals | EXISTS | `SigmoidStore` adds codecs to `ForecasterStore`; same bounded I/O engine |
| Captured replay | PARTIAL | New wrapper closure verification; generic numerical reconstruction UNSUPPORTED |
| Independent Evaluation | EXISTS, one/two participants | Strict raw/calibrated projection plus existing normalized paired scorer; benchmark comparison uses same synthetic slots |
| Reliability / intercept / slope | NEEDS_BOUNDED_EXTENSION | Evaluation-owned fixed-bin and bounded diagnostic plumbing |

```text
External exact synthetic grant
  → existing TrainingIdentity + durable TrainingAttempt
  → compiled-only isolated sigmoid worker (no source-model fit)
  → SigmoidArtifact + TrainingExecution/Result/Bundle
                                      │
authored source → neutral inference → RAW capture
                                      │
                       versioned calibrated composition
                                      │
                       CalibratedCapture {p, q, lineage}
                          ├─ existing bounded store → recorded replay
                          └─ independent Evaluation ← external synthetic truth
                                      no activation
```

The common neutral runner, registries, native BaseRate/Logistic codecs, old FLC
codecs and FF-1 files have **no edits**. No new family dispatch was added to
common inference. The synthetic Logistic adapter is local to the explicit
engineering profile. `CalibratedCapture` binds a neutral source, not a union or
`if Logistic / elif FutureFamily` switch.

## 3. Mathematics, bounds and deterministic fixture

Exactly the FF-2.0 map:

```text
z = logit(clamp(p, 1e-15, 1 - 1e-15))
q = sigmoid(a + b*z)
```

Original p is immutable and unclipped in the capture. Clipping occurs only inside
the transform/log-loss policy. Parameters are finite, b must be strictly positive;
invalid probabilities, nonfinite values, booleans and numeric strings reject.
Parameter/adapter identity: `ff2.synthetic.sigmoid.1`; wrapper profile:
`ff2.synthetic.calibrated-wrapper.1`. These are not the reserved empirical FF-2
candidate or a mutable FF-1 Logistic artifact version.

The single compiled fit recipe has 60 authored pairs: ten copies each of
p = .10, .20, .40, .60, .80, .90, with positive counts 2, 3, 4, 6, 7, 8.
No data loader or caller-selected feature/price matrix exists. A supplied sample
must match the entire compiled recipe, not just a provenance flag or hash
provided by the caller. Relabeled arbitrary numeric arrays fail admission.

Solver `newton-armijo-32` v1 minimizes unweighted log loss, with intercept,
no regularization/balancing/augmentation, initial (0,1), maximum 1,000 iterations,
gradient infinity norm <=1e-8, and up to 32 deterministic Armijo backtracks per
iteration. Constant scores, missing classes, complete/quasi separation, singular
Hessian, nonconvergence, nonfinite parameters and nonpositive fitted slope fail;
there is no alternative solver or rescue attempt. Tests separately check scalar
proper-score oracles, identity-transform endpoints and deterministic fitted parameters.

The child process has 60-second wall/CPU bounds, 512 MiB address-space limit,
one numerical thread and one attempt. It can generate only the compiled recipe;
it accepts no path, observations or configuration arguments. Python/stdlib
dependency identity and the five new Learning source-file hashes are bound into
the training request. There is no additional ML dependency. This Linux worker
profile is not an empirical solver-lock approval or a cross-platform bitwise
reproducibility guarantee.

Observed synthetic parameters are approximately a = -1.61e-16,
b = 0.6365858283318643. These demonstrate finite fitting, not empirical value.
The source adapter is an **authored one-feature Logistic reference**, coefficient
1, intercept 0, input logit of the authored grid; it is never trained. Binary64
sigmoid/logit round-off is retained. It is not the five-feature FF-1 model.
Synthetic evaluation uses distinct observation IDs 60–119 and separately authored
external labels; reused toy grid shapes provide no claim of independent science.

## 4. Identity, authority, persistence and replay

The candidate content identity includes the source composition, fitted artifact,
source forecaster/model/training/schema references, calibrator version/parameters,
fit request, external grant, consumed attempt, population and timestamps. Changing
parameters changes the candidate key. `experiment:ff2-synthetic-engineering-001`
is distinct from the reserved real experiment. Full capture hashes include clocks;
numeric parameter identity is separate. Selection, approval and activation are
not consequences of successful fitting.

`fit_synthetic_once` revalidates the exact compiled request/sample, reuses
`TrainingAuthorization` / `admit_training`, and verifies request, experiment,
input, authority, qualification, custody root, OPEN/NONE state and grant expiry.
It writes an exclusive claim and fsyncs file/directory before launching the worker.
A timeout/crash leaves a consumed incomplete attempt; no retry or quiet deletion.
The existing store is single-writer; hashes are integrity, not signatures or
administrator-proof WORM. A caller cannot gain empirical access by forging a
synthetic grant because this worker has no empirical input route. Pure internal
math/diagnostic functions do not constitute an execution grant.

All records inherit existing frozen, sealed, timezone-aware research contracts.
Semantic collections are tuples; list/JSON input reconstructs and JSON emits
arrays. Naive datetimes reject; UTC input normalizes to Asia/Kolkata and JSON
emits `+05:30`. Existing package 0.1.0, core schema 1.0 and research schema 2.0
remain distinct and unchanged. No historical record migration occurs.

Recorded replay checks the exact captured wrapper and separately persisted
candidate, raw source, input, authored model, fit request/execution/result/model
identity/bundle, synthetic sample, external grant and consumed claim. Static
schema/training/composition policy references are identity-only declarations,
not assertions that an external blob or empirical qualification was archived.
Missing required bytes => UNAVAILABLE; malformed/tampered/contradictory closure
=> MISMATCH; intact closure => MATCH. Replay does not fit, apply the sigmoid,
call inference, evaluate outcomes, access network or write files. Numerical
reconstruction remains **UNSUPPORTED**; MATCH is captured integrity, not a new
numeric verification or scientific qualification. Reopening the same custody
root is read-only; moving it does not silently transfer root-bound fit authority.

## 5. Evaluation and diagnostics

The strict raw/calibrated bridge checks exact candidate/source/target/schema
lineage, participant roles, probability/capture references and observation joins
before using the unchanged FLC-6 evaluator. It rejects raw/q swaps and conflicting
identities. Ground Truth is externally supplied under its own journal identity;
neither source adapter nor calibrator manufactures outcome labels.

Tests score raw, calibrated and the **existing native BaseRate** output from its
authored twenty-transition fixture. The fixed benchmark is explicitly projected
onto the toy evaluation slots for the second paired comparison; this is not
empirical per-slot issuance. Both reports use the same 60-slot truth population:
calibrated-minus-raw and calibrated-minus-BaseRate. They verify Brier and natural
log loss against independent scalar calculations, and preserve Evaluation's
no-scientific-decision/no-promotion fields. No superiority claim is made.

Reliability plumbing uses ten fixed bins, last bin inclusive of 1, null values
for empty bins and LOW_SUPPORT below 20. ECE includes low-support bins; MCE and
mean-p-minus-mean-y are descriptive. Offset-only intercept and two-parameter
diagnostic intercept/slope use bounded Evaluation-only regressions; constant or
separated inputs report NOT_ESTIMABLE, never a fabricated zero. They cannot
update candidate parameters. This pass does not deliver the entire future
empirical FF-2 diagnostics/selection/final-criteria service: discrimination
summaries, three-arm missingness admission, qualified empirical adapters,
source grants, exact native numerical verifier and prospective custody remain
later separately authorized work. Existing FLC-6 absence accounting is unchanged.

## 6. Validation and preservation

| Fresh check | Result |
| --- | --- |
| New FF-2.2 synthetic/negative/end-to-end tests | **52 passed in 6.47s** |
| Focused FF-2/FLC/inference/custody/replay/Evaluation/FF-0 slice | **442 passed in 292.31s**; includes the 52 above, not an additional independent count |
| Full repository suite | **3,919 passed in 1,187.68s (19:47)**; no failures or skips |
| Compileall `src scripts` | PASS |
| Ruff `src tests scripts` | PASS |
| mypy `src tests` | PASS, 684 source files |
| Documentation links/anchors | PASS, 962 local links in 14 Markdown files |
| Four FF-1 scientific fingerprints | 4/4 MATCH |
| Frozen FF-1 source/implementation pins | 78/78 MATCH |
| Existing tracked source/tests/scripts edits | None; all runtime additions use new files |
| Historical FF-2.0/2.1 reports and authority artifact | Byte-preserved |
| `git diff --check`, including separate checks of new files | PASS |

The focused slice comprises `test_sigmoid_calibration.py`, `test_calibration.py`,
`test_neutral_inference.py`, `test_forecaster_seams.py`,
`test_lifecycle_integration.py`, `test_evaluation_normalization.py`,
`test_forecaster_lifecycle.py`, `test_forecaster_diagnostics.py` under
`tests/unit/forecasting/`, plus
`tests/unit/evaluation/test_ff2_data_use_authority.py` and `tests/acceptance/ff0`.
Preliminary test runs caught new-code identifier spelling, a reserved capture
field name and missing-file status handling; these were fixed without modifying
the existing codecs. The passing runs above supersede those development failures.

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_sigmoid_calibration.py --tb=short
.venv/bin/pytest -q --tb=short
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
.venv/bin/python -c 'from docs.handbooks.a7_forecasting.validate_handbook import validate_links; print(validate_links(True))'
git diff --check
```

Read-only `_legacy_records()` verification produced the unchanged fingerprints:

| Record | Fingerprint |
| --- | --- |
| FF-1 protocol | `2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814` |
| FF-1 execution | `2948bc46874f8196c535720bd4f7882f6293fc96077acb563e2e11409c3e4840` |
| FF-1 final evaluation | `8c0556e7b88284c170db57d745de7ece707d365ab52a585db5ebb0d3e81a7d0e` |
| FF-1 complete ledger | `630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583` |

FF-2.0 protocol byte SHA-256 remains
`33d334c3ab3aad21d739924898e6f2838545df47cf07cb0179d5d850ddaac271`.
FF-1 remains CONSUMED, one execution, no post-holdout refit,
INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE. FLC's fixed synthetic recipe,
authored-table calibration, native adapters, neutral runner and Evaluation
contracts/scoring are unchanged. Existing BaseRate remains BENCHMARK and
Logistic CHALLENGER / EXPERIMENTAL.

No historical market outcomes, real 2022 fit, 2023–2024 FF-2 selection, 2025 or
January-2026 numeric evidence, live/provider calls, base/scaler refits, prospective
collection, protected opening, promotion, activation, commit, tag or push.

## 7. Handoff boundary

The next task is **empirical authority resolution**, not empirical execution.
Historical roles are defined but their grants remain unresolved. Any later
empirical capability must bind the exact untouched FF-2.1 source pins, qualified
partitions and separately reviewed solver/implementation/permission closure;
it must not widen this synthetic recipe or disguise real values as engineering
fixtures. Final protected evidence/readiness remains absent.

```text
FF2_SIGMOID_CALIBRATOR_IMPLEMENTED = YES
FF2_CALIBRATED_CANDIDATE_CONTRACT_IMPLEMENTED = YES
FF2_RAW_PROBABILITY_PRESERVED = YES
FF2_SYNTHETIC_FIT_ACCEPTED = YES
FF2_PERSISTENCE_ACCEPTED = YES
FF2_REPLAY_ACCEPTED = YES
FF2_EVALUATION_COMPATIBILITY_ACCEPTED = YES
FF2_EMPIRICAL_AUTHORITY_GUARD_ACCEPTED = YES
FF2_SYNTHETIC_E2E_ACCEPTED = YES
FF2_EMPIRICAL_DEVELOPMENT_READINESS = NO
FF2_FINAL_PROTECTED_EVALUATION_READINESS = NO
FF1_PRESERVED = YES
FLC_PRESERVED = YES
FF0_PRESERVED = YES
```

**GO_FF2_EMPIRICAL_AUTHORITY_RESOLUTION**

This recommendation accepts synthetic infrastructure and its engineering tests,
not scientific superiority, verified external rights, permission for empirical
fitting, protected-evidence access, candidate promotion or runtime activation.

## 8. Exact change inventory

Added:

- `src/tiaf/learning/sigmoid_contracts.py`
- `src/tiaf/learning/sigmoid_math.py`
- `src/tiaf/learning/sigmoid_worker.py`
- `src/tiaf/learning/sigmoid_synthetic.py`
- `src/tiaf/learning/sigmoid_calibration.py`
- `src/tiaf/evaluation/sigmoid_evaluation.py`
- `tests/unit/forecasting/test_sigmoid_calibration.py`
- `docs/TIAF_A7_FF2_2_SYNTHETIC_CALIBRATION_INFRASTRUCTURE.md`

Current navigation/status updated, without rewriting historical reports:

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
