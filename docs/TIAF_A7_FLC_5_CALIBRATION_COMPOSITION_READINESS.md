# A7 / FLC-5 — Calibration composition readiness

Checkpoint: 2026-09-23, Asia/Kolkata. **FLC5_ACCEPTED**.
This is an additive internal engineering capability, not empirical calibration.
**FF-2 has NOT started.** No calibrator is fitted and no frozen probability changes.

## Scope and reuse

The existing FLC-1 `CalibratableOutput` is the compatibility declaration:
`RAW_COMPATIBLE_NOT_QUALIFIED`, with fit/apply authorization both false. It means
only that the output shape can be consumed under a separately authorized
protocol. It does not mean calibrated, qualified, preferred or promoted.

FLC-5 keeps that seam unchanged. Its explicitly authorized application is
limited to an authored synthetic reference population. It does not widen the
forecaster descriptor, registry, public facade, shell, API or activation path.

```text
captured synthetic primitive output and original singleton composition
                │ raw probability retained unchanged
                ▼
     CALIBRATE(child) reference composition
       ├── immutable component + authored artifact
       ├── original primitive identity and graph
       ├── raw_probability
       └── calibrated_probability (synthetic transform only)
                │ separate, explicit future request
                ▼
      independent evaluation — NOT called here
                │ separate authority
                ▼
      approval / promotion / activation — NOT granted here
```

`CalibrationComposition` is the bounded `flc5.calibrate-singleton.1` profile of
the accepted FF composition architecture. It embeds the complete existing
`ForecastComposition`, reuses the existing typed `ForecastEdge`, and admits
exactly one wrapper node/root. The frozen singleton contract is not widened.
There is no second graph executor, DAG registry or composition discovery path.
Other composition shapes and actual Logistic application remain unsupported by
this engineering adapter rather than being implicitly admitted.

## Contracts, identity and observability

| Contract | Meaning and pinned content |
| --- | --- |
| `CalibrationTarget` | Target ID/version, positive event, horizon, cutoff policy and exact raw/transformed binary-probability semantics |
| `CalibrationComponent` | Immutable calibrator ID/version/family, source forecaster/model/preprocessor, target, mode, parameter fingerprint and aware creation time |
| `CalibrationEvidence` | Distinct source/new experiment, protocol, source forecast population, authored parameter population, qualification declaration and evidence policy |
| `CalibrationArtifactIdentity` | Component/evidence closure; authored synthetic origin; fit, promotion and advisory qualification all false |
| `CalibrationArtifact` | Separately versioned table codec, immutable knots, identity, availability and expiry |
| `CalibrationFitRequest` / `CalibrationFitResult` | Proposal only, `PROPOSED_NOT_AUTHORIZED` → `NOT_EXECUTED`; no artifact output or activation |
| `CalibrationSource` | Captured compatible output, whole original primitive composition, synthetic target, cutoff/computation clocks and source identity |
| `CalibrationApplyRequest` | Exact source/component/artifact/target/mode/policy references, aware request time and fixed synthetic/no-outcome scope |
| `CalibrationApplyResult` | Request/source, raw and optional transformed values, component composition, status/reason, artifact observation, exact lineage and fingerprint |

All inherit the existing immutable, sealed research contract. Semantic
collections are tuples, Python/JSON lists reconstruct cleanly, JSON emits
arrays, unknown fields and naive datetimes are rejected. Timestamps normalize
through the existing `ZoneInfo("Asia/Kolkata")` policy and emit `+05:30`.
No ambient `now()` participates in calculation or identity.

The artifact identity is the reusable lineage shape needed by a future fitted
calibrator, but this version only permits authored reference parameters. A
future fitted artifact requires a separately authorized adapter/protocol; it
cannot be represented as a successful fit in FLC-5.

Family identity is data, not a closed global family enumeration. The only
executable adapter is version `flc5.reference.1`, family
`calibrator:authored-monotonic-table`. Unknown implementations return
`UNSUPPORTED`; a future family needs its own typed payload/codec, not additional
optional fields or a fallback to the reference implementation.

Composition identity is `flc5-composition:<semantic fingerprint>` over the
primitive graph/identity, component, artifact, target, policy and profile/version.
Changing table parameters changes both component/artifact and composition
identity. The original forecaster identity and raw output remain unchanged.
Result validators reject altered lineage, unrelated compositions and
inconsistent artifact/status observations.

## Synthetic application, not a calibration experiment

The source contract admits only five index-pinned authored outputs:
`0.0, 0.2, 0.5, 0.8, 1.0`, the compiled synthetic forecaster/model references and
the synthetic one-step target. Symbol/provider/label/outcome fields are not
accepted. Merely labeling a market-data forecast "synthetic" does not admit it.
No RELIANCE/Dhan data or consumed 2025 record is loaded by this implementation.

The reference outputs and population/protocol pins are compiled engineering
declarations, not newly trained forecasts or externally qualified populations.
No actual primitive inference is claimed by these fixtures. Replay verifies the
persisted raw capture and transformation, not a new run of the primitive model.

The reference artifact contains 2–16 monotonic piecewise-linear knots covering
the entire unit interval. Inputs and ordinates must be finite probabilities,
abscissae strictly increase, and the parameter fingerprint must match. Explicit
identity knots `[(0, 0), (1, 1)]` are supported. Missing calibration is never
silently converted into identity.

Illustrative engineering example, **not measured calibration performance**:

| Raw probability | Identity output | Reference knots `(0,0), (0.5,0.4), (1,1)` |
| --- | --- | --- |
| 0.0 | 0.0 | 0.0 |
| 0.2 | 0.2 | 0.16 |
| 0.5 | 0.5 | 0.4 |
| 0.8 | 0.8 | 0.76 |
| 1.0 | 1.0 | 1.0 |

Interpolation is deterministic Python floating-point arithmetic. Displayed
decimal values are rounded illustrations; canonical records retain the actual
floating values and offline replay recomputes them exactly in this runtime.
The field name `calibrated_probability` denotes the wrapper's transformed
output, **not evidence of calibration quality**. Every result fixes its
interpretation to `SYNTHETIC_TRANSFORM_NOT_CALIBRATION_QUALIFICATION`.

## Compatibility, clocks and failure semantics

Application requires exact source forecast reference/ID/forecaster/model;
target ID/version/event/horizon/cutoff policy; raw output semantics; realization
mode; component and artifact identity; and the compiled reference apply policy.
The synthetic primitive has no preprocessor: supplying one is incompatible.
This explicitly prevents accidentally applying a different Logistic scaler or
model, not an assertion that arbitrary Logistic models are supported.

The artifact must be available at the source information cutoff and not expired
there. Source computation cannot precede that cutoff; request creation cannot
precede computation. Later replay wall-clock time neither renews nor expires a
historically valid application.

| Condition | Result |
| --- | --- |
| Compatible reference and artifact | `GENERATED`, raw and transformed values plus composition |
| Unknown component implementation/family | `UNSUPPORTED`, no transformed output, artifact not checked |
| Absent/unreadable/invalid artifact closure | `UNAVAILABLE`, no identity substitution |
| Incompatible source/target/dependency/mode/policy or stale artifact | Explicit validation error; no successful application record |
| Invalid/nonfinite probability | Contract rejection |
| Arithmetic/application error | `FAILED`, raw retained, no transformed output |
| Broken replay lineage, missing child, tampering or changed transform | `MISMATCH` |

An unavailable observation records that the dependency could not be verified;
it does not assert that no file existed. A recorded absence replays as the same
observation even if an artifact is subsequently provisioned. This is not a
historical filesystem-availability proof. Successful replay resolves every
persisted child and recomputes the transform; a formerly failing transform that
now succeeds mismatches rather than silently upgrading the recorded result.

## Persistence, custody and offline replay

`CalibrationStore` only extends codecs on the existing `ForecasterStore` /
`ResearchForecastStore`. Existing content-addressed canonical serialization,
exclusive creation/no overwrite, bounds, read-only mode and custody metadata
remain the sole persistence engine. No calibration database or registry exists.

```text
result reference
  ├── request reference ── exact policy/component/artifact references
  ├── source reference ── original graph + raw compatible output
  ├── artifact reference
  │     └── identity ── component + evidence declaration
  └── composition reference ── original child + calibration edge/root
                │ resolve and validate all required children
                ▼
       recompute table(raw) → compare whole sealed result → MATCH / MISMATCH
```

Requests, sources, components, evidence, artifact identities/artifacts,
compositions and results are independently persisted. Fit proposals and
non-execution results use the same store without invoking any fit. Application
persists a result last; orphaned content-addressed children after a failed write
are not a successful application. Replay performs no write, fit, evaluation,
provider, broker or network operation, and does not invoke the apply service.
Custody metadata records possession, never approval or permission to use.

## Evidence and authority boundaries

The evidence contract permits only compiled authored-population/protocol/policy
references and requires distinct source/new experiment IDs. It forbids
consumed-2025 reuse, same-experiment rescue and closed/sealed holdout states.
Qualification is explicitly **not verified**. These guards are machine-enforced,
not inferred from a descriptive scope string. They do not create a future fit
grant: genuinely qualified evidence and a new authorized experiment remain
prerequisites for a later FF-2 implementation.

No calibrator fit routine exists. Apply cannot call fitting, self-evaluate,
read Ground Truth, produce a metric/verdict or imply empirical benefit.
Existing independent evaluation remains the owner of future comparisons.
Approval, promotion and activation fields are fixed false; lifecycle services
are not called. FLC-4 remains the diagnostics owner and can later inspect this
lineage through separately authorized integration; no diagnostics are duplicated
or automatically invoked. FLC-3 search/results are unchanged; no calibration
search or parameter optimization is added.

## Compatibility and frozen-baseline preservation

| Layer | Preservation / addition |
| --- | --- |
| FF-0 BaseRate | Existing inference, singleton composition, target, pinned replay and artifacts unchanged |
| FF-1 Logistic | No frozen source/artifact/probability changes, refit, rerun or new analysis |
| FLC-1 inference | Existing raw-compatible declaration reused; no descriptor/capability changes |
| FLC-2 training/custody/lifecycle | Existing store/custody reused; no training or lifecycle behavior changed |
| FLC-3 optimization | No search/evaluation/selection mutation or calibration objective |
| FLC-4 diagnostics | No diagnostic implementation or verdict changes |
| FLC-5 | Additive contracts, bounded synthetic wrapper/application, existing-store codecs and offline verification |

FF-1 remains `INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE`; BaseRate is
BENCHMARK, Logistic is CHALLENGER / EXPERIMENTAL, promotion eligibility NO,
2025 holdout CONSUMED, execution count 1, post-holdout refit forbidden.

Hash-only audit, without running the final evaluation:

| Canonical record | Fingerprint — MATCH |
| --- | --- |
| Protocol | `2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814` |
| Execution | `2948bc46874f8196c535720bd4f7882f6293fc96077acb563e2e11409c3e4840` |
| Evaluation | `8c0556e7b88284c170db57d745de7ece707d365ab52a585db5ebb0d3e81a7d0e` |
| Ledger | `630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583` |

All **72 source + 6 implementation pins = 78/78 MATCH**. No existing runtime
Python source, FF-0/FF-1 artifact or dataset is edited. FF-2 is deferred:
there is no empirical calibration, calibrator fitting, new holdout execution,
public capability, A6 modification or A8 work.

## Validation

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_calibration.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_diagnostics.py tests/unit/forecasting/test_optimization.py tests/unit/forecasting/test_forecaster_lifecycle.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_seams.py tests/acceptance/ff0 tests/unit/forecasting/test_contracts.py tests/unit/forecasting/test_pinned_runtime_replay.py tests/unit/forecasting/test_identity_isolation.py tests/unit/forecasting/test_logistic_training.py tests/unit/forecasting/test_logistic_forecasts.py --tb=short
.venv/bin/pytest -q --tb=short
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
.venv/bin/python -c 'from docs.handbooks.a7_forecasting.validate_handbook import validate_links; print(validate_links(True))'
git diff --check
```

- FLC-5 targeted: **58 passed**; compatibility, composition, parameter identity,
  no-authority/no-fit guards, stale clocks, invalid probabilities, explicit
  absence/unsupported/failure, custody, offline replay and tamper checks.
- FLC-4/3/2 combined: **146 passed** (31 + 60 + 55).
- FLC-1 seam tests separately: **27 passed**.
- FLC-1 / FF-0 / FF-1 compatibility: **251 passed in 229.74s**.
- Full repository suite: **3,676 passed in 1,057.18s (17:37)**.
- Compileall and Ruff: PASS; mypy: PASS, **667 source files**.
- Documentation: **794 local links across 13 Markdown files** passed;
  **11 changed/new Markdown files** have balanced fences.
- `git diff --check` and trailing-whitespace checks on all four new files: PASS.
- Additional invalid-table probes: **7/7 rejected** (bounds, coverage,
  duplicate/reversed abscissae and decreasing ordinates).
- Four canonical FF-1 fingerprints and 78 frozen pins: MATCH.

The regression suites exercise existing authorized synthetic training tests;
FLC-5 itself does not fit any model or calibrator and does not access empirical
outcomes. Synthetic transformations provide engineering replay proof only.

## Files, deferrals and handoff

Acceptance blockers: **none**. Entry worktree was clean at `01dd9cd` (accepted
FLC-4 implementation); all existing runtime files remain unchanged.

Created:

- `src/tiaf/learning/calibration_contracts.py`
- `src/tiaf/learning/calibration.py`
- `tests/unit/forecasting/test_calibration.py`
- this report.

Modified active navigation only: `README.md`, `docs/ARCHITECTURE.md`,
`docs/IMPLEMENTATION_ROADMAP.md`, `docs/MILESTONES.md`,
`docs/TIAF_IMPLEMENTATION_TARGETS.md`, `docs/TRADINGINTELLIGENCE_ROADMAP.md`,
`docs/TIAF_A7_DETAILED_ROADMAP.md`,
`docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md`,
`docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md` and
`docs/TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md`.
Historical acceptance reports and the FLC-0 gap baseline remain historical.

Deferred: actual fit authorization/implementation, empirical qualification,
arbitrary forecaster/calibrator families, Logistic application, future diagnostic
integration, independent calibration evaluation and production use. None is
silently enabled by persistence or a successful synthetic transform.

Next, only after acceptance and a separate request:
**TIAF A7 / FLC-6 — REUSABLE INDEPENDENT EVALUATION NORMALIZATION**.
Requested handoff model: **GPT-5.6 Sol — Extra High**.
Suggested commit after acceptance: `feat(a7.flc5): add calibration composition readiness`.
No commit, tag or push is performed by this task. No tag is proposed.
