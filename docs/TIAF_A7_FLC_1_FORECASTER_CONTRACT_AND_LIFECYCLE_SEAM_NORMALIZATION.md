# A7 / FLC-1 — Forecaster contracts and lifecycle seams

**FLC1_ACCEPTED.** Implementation checkpoint: 2026-09-22, Asia/Kolkata.
Internal additive seams; validation results below. No public operation, startup binding or scientific
approval is added. FF-0/FF-1 remain frozen; FF-2 remains deferred.

## Scope and inspected gap

The [FLC-0 gap baseline](TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md)
and [FF §22](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#22-forecaster-lifecycle-completion-flc)
own the architecture. This checkpoint implements only its first contract package.
FLC-0's 33-row inventory and historical validation counts are not rewritten.

`Forecaster`, `ForecasterDescriptor`, `ForecastArtifactIdentity` and the FF-0
`ForecastRequest/Result` composition are deliberately BaseRate-specific, with a
synthetic-engineering purpose. FF-1 separately owns `ResearchForecastRequest/Result`,
adjusted-research provenance, fixed four-fold artifacts, and native reconstruction.
Changing those literals would invalidate accepted version and source pins.

## Shared inference boundary

```text
Caller supplies native request + immutable, already qualified context
                      │
          InferenceRequest (same type for both)
                      │
   exact read-only resolve_inference_forecaster(key, context)
                ┌─────┴──────┐
         BaseRate adapter    Logistic adapter
         admit_support       existing generate / reconstruct
         existing k/n        immutable supplied model/scaler
                └─────┬──────┘
          InferenceResult (same type for both)
            native payload + descriptor + artifact references
                      │
        canonical serialization / trusted expected fingerprint
                      │
           recorded replay (decode, no numeric execution)
```

Source: [forecaster_seams.py](../src/tiaf/forecasting/forecaster_seams.py) and
[forecaster_adapters.py](../src/tiaf/forecasting/forecaster_adapters.py).
The narrow protocol is `forecast(InferenceRequest) -> InferenceResult`, plus a
typed descriptor. The immutable adapter is explicitly bound to a `BaseRateContext`
or `LogisticContext`. There is no clock read, I/O, fit, optimizer, provider or
label access in either adapter. A caller provides computation time explicitly.

The common request retains its original typed native envelope, not an untyped
dictionary. Target, subject, mode, information cutoff and as-of accessors are
projections of those authoritative fields. Native target definitions, evidence,
feature schema, price basis and purpose are never replaced by those display views.
The finite native union is version dispatch for the two accepted paths, not a
universal input schema or an assertion that composites are already executable.
Future compositions require additive types/admission, not widening frozen types.

The common **inference result** is additive: it is not the FF-0 capture/runtime
`ForecastResult`. BaseRate retains its exact `GenerationPayload`; Logistic retains
its complete sealed `ResearchForecastResult`. Both reuse `BinaryProbabilityOutput`
and `ForecastAbsence`. No research-v2 request is relabeled synthetic FF-0, and no
FF-0 runtime binding/issuance guarantee is implied by a primitive inference call.

All new models are frozen, extra-forbid and defensively revalidated; semantic
collections are tuples accepting list/JSON input and serializing to arrays.
Canonical aware `ZoneInfo("Asia/Kolkata")` timestamps remain `+05:30`, with naive
datetimes rejected. ACTUAL/SIMULATED support is retained for BaseRate; Logistic
remains SIMULATED only, with its strictly later real computation clock.
Package `0.1.0`, existing contract `1.0`, research schema `2.0`, model artifact
`1.0`, and the new `tiaf.flc.*` schema identities are separate version concepts.

## Identity, capability and authority

`ForecasterKey` holds exact logical ID/version, not a path, module or alias.
`LifecycleIdentity` separates algorithm family, role and lifecycle. BaseRate is
BENCHMARK with lifecycle UNSPECIFIED: FF-0 did not supply a generic scientific
lifecycle state. Logistic remains CHALLENGER / EXPERIMENTAL. UNSPECIFIED is not
approval or a replacement for historical frozen status.

| Capability at this normalized seam | BaseRate | Logistic |
| --- | --- | --- |
| INFERENCE | Yes | Yes, supplied development artifact only |
| TRAINING | No | No; existing native trainer is not adapted until FLC-2 |
| DIAGNOSTICS | No | No; typed seam only |
| CALIBRATION_COMPATIBLE | Raw binary output shape | Raw binary output shape |
| ARTIFACT_BACKED (learned model) | No | Yes |
| REPLAYABLE | Recorded envelope | Recorded envelope |

`supports(capability)` returns explicit false for unsupported optional behavior.
Duplicate capability declarations fail. Declarations are not grants. Descriptor
metadata on results must match the exact read-only identity view; a result cannot
claim a different role/capability set. `activation_eligible` is always false and
approval is always NOT_GRANTED_BY_INFERENCE. No promotion/activation operation
exists. Independent Evaluation and reviewer/Learning ownership stay unchanged.

### Optional seams, not implementations

- `TrainableForecaster`, `TrainingRequest/Result`: proposal references for inputs,
  configuration and external qualification; TRAIN partition only; status
  PROPOSED_NOT_AUTHORIZED / NOT_EXECUTED. Neither adapter implements it. No success
  artifact can be minted here. A caller-supplied qualification reference is not
  verified authority; FLC-2 must resolve evidence custody and grants before any
  execution. Relabeling a protected reference TRAIN grants nothing.
- `DiagnosableForecaster`, `DiagnosticRequest`, generic `DiagnosticReport[T]`:
  model-specific, typed payloads and logical diagnostic kinds, DESCRIPTIVE_ONLY.
  No coefficient analysis, study runner or diagnostic registration service.
- `CalibratableOutput`: raw binary output and input-forecast reference;
  RAW_COMPATIBLE_NOT_QUALIFIED; fit/apply authorization always false. No calibrator,
  changed probability, qualified calibration claim or FF-2 implementation.

## Adapter, lookup and artifact details

BaseRate delegates to the existing registry's exact resolver and pure forecaster,
with the existing admitted-support validator. Unsmoothing, minimum support,
zero/one endpoints and absence behavior are unchanged. The context pins its
original support artifact and singleton composition; it does not invent a fitted
model/scaler/training identity.

Logistic delegates to `generate` using a supplied outcome-blind projection and
native `TrainingRun`; all existing handoff, feature, dependency, fit-cutoff and
origin-membership checks remain. Its returned native request must match the
requested pins exactly. Only declarative native reconstruction runs, not sklearn.
The accepted four development folds remain the only supported native route;
fifth-fold/final evaluation types are not admitted by this adapter.

`describe_forecaster`, `inference_descriptors` and `resolve_inference_forecaster`
form one read-only **adaptation view**. There is no stored second registry,
registration API, artifact catalog or lifecycle database. BaseRate still uses
the sole frozen registry; Logistic has one exact compiled route to its existing
research implementation. Unknown IDs/versions fail with the existing integrity
exception; duplicate ID/version entries in the combined view fail closed. No
arbitrary modules, latest-version fallback, plugin imports or public registration.
The old registry contents and APIs are unchanged, not silently extended.

`ForecasterArtifacts` references the canonical context and composition and, for
Logistic, model/scaler/training hashes together. Those references identify existing
native hashes; they do not reseal native objects or create new stored copies.
The `flc-*` logical reference namespace distinguishes additive wrapper references
from native store keys. FLC-2 owns codec/custody integration; these references do
not install another store or pretend the new envelope is a legacy capture blob.

## Replay, absence and compatibility

`recorded_inference_replay` requires canonical JSON and a separately trusted
expected fingerprint, checks the decoded envelope and returns its captured
facts. It cannot verify a forged result against an equally forged expected hash;
trusted hash custody remains the caller's responsibility. It performs no model
inference, fitting, network or storage lookup. It is **not** exact pinned numeric
verification or fit reproduction. Original FF-0/FF-1 replay/verifier paths remain
available and unchanged. New end-to-end store/version routing belongs to FLC-7.

| Native result | Shared availability view | Preserved detail |
| --- | --- | --- |
| BaseRate any status | Same existing ForecastStatus | Exact GenerationPayload |
| Logistic GENERATED | GENERATED | Exact raw probability and full sealed native result |
| Logistic UNAVAILABLE | UNAVAILABLE / EVIDENCE_MISSING | Native status and reasons retained |
| Logistic EXCLUDED | UNAVAILABLE / EVIDENCE_UNQUALIFIED | EXCLUDED is not erased or counted as an evaluated row |
| Logistic PROTECTED | UNAVAILABLE / POLICY_ABSTENTION | PROTECTED and TARGET_HOLDOUT_SEALED retained; no numeric output |

These are inference-availability accessors, **not** a new Evaluation disposition
mapping. Evaluators must retain native dispositions; missing is never negative.
Invalid identity, target, context, clock or pins fail closed with existing
validation/integrity errors. Optional capability absence alone is not a failure.

| Legacy contract/path | Normalized path | Compatibility / migration | Behavioral change? |
| --- | --- | --- | --- |
| FF-0 Forecaster / GenerationPayload | BaseRateInferenceAdapter / InferenceResult | Additive wrapper; old callers and registry unchanged | NO |
| FF-0 ForecastRequest / ForecastResult / Capture | Native request retained; primitive result wrapped | Runtime/capture ownership stays legacy; no conversion of FF-0 result bytes | NO |
| FF-1 ResearchForecastRequest/Result | LogisticInferenceAdapter / InferenceResult | Exact native research envelope and probability retained | NO |
| Logistic model/scaler/TrainingRun | ForecasterArtifacts refs / LogisticContext | Immutable supplied native objects; no refit or persistence migration | NO |
| FF-0 and FF-1 recorded/pinned replay | Additive wrapper decode alongside legacy replay | No replacement of old stores, verifiers or pins | NO |

## Synthetic proof and validation

[test_forecaster_seams.py](../tests/unit/forecasting/test_forecaster_seams.py)
demonstrates both adapters through the same request/result and exact lookup,
BaseRate endpoints/absence and ACTUAL/SIMULATED, four Logistic development-fold
reference outputs and available absence categories, tuple/JSON/time rules,
unknown versions/targets, duplicates, invalid copies/context, authority denial,
and offline replay with numeric execution blocked. Logistic fixtures use
hand-authored coefficients/scalers, never an empirical fit. They test interfaces,
not financial merit. A separate external qualification boundary remains necessary.

Validation commands:

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_seams.py tests/unit/forecasting/test_logistic_forecasts.py
.venv/bin/pytest -q tests/acceptance/ff0 tests/unit/forecasting/test_contracts.py tests/unit/forecasting/test_pinned_runtime_replay.py tests/unit/forecasting/test_identity_isolation.py tests/unit/forecasting/test_forecaster_seams.py
.venv/bin/pytest -q
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
git diff --check
```

Completed focused checks:

- FLC-1 + FF-1 native forecast/replay slice: **71 passed in 128.37s**,
  comprising **27 FLC-1 tests** and **44 FF-1 tests**.
- FF-0 acceptance, native contracts, pinned runtime replay, identity isolation
  and the initial 23-case FLC-1 slice: **163 passed in 114.52s**. Four additional
  FLC-1 target/context/absence cases are included in the later 71-test run above.
- Compileall (`src scripts`), Ruff (`src tests scripts`), mypy (`src tests`,
  **649 source files**) and `git diff --check` pass.
- Changed-document validation: **716 local links and 29 anchors across 12
  Markdown files** pass.
- Initial full suite: **3,471 passed, 1 failed in 814.42s**. The failure was
  `tests/unit/workflows/test_hardening.py::test_timeout_is_partial_and_keeps_unreported_reservation`,
  an existing real-time 20 ms deadline test. Its UNKNOWN-reservation assertion
  assumes dispatch occurs before the deadline; the coordinator may legitimately
  exhaust that budget before dispatch. The workflow module rerun passed
  **39 tests in 11.29s**. Workflow source/tests are unchanged; no timeout semantics
  were adjusted. The fresh full run without concurrent test jobs passed:
  **3,472 passed in 787.29s (13m07s)**. There is no remaining FLC-1 acceptance
  blocker. The existing wall-clock-sensitive test is a recorded non-blocking
  regression risk, not silently fixed or omitted. No empirical commands or
  final-holdout entry points form part of these checks.

### File scope

Created by FLC-1: the two source modules linked above, `test_forecaster_seams.py`,
and this implementation record. Navigation updates extend the already-dirty
FLC-0 documentation in `README.md`, `docs/ARCHITECTURE.md`,
`docs/IMPLEMENTATION_ROADMAP.md`, `docs/MILESTONES.md`,
`docs/TIAF_IMPLEMENTATION_TARGETS.md`, `docs/TRADINGINTELLIGENCE_ROADMAP.md`,
`docs/TIAF_A7_DETAILED_ROADMAP.md`,
`docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md`,
`docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md`,
`docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md`, and the existing untracked
`docs/TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md`. The latter receives
only a subsequent-checkpoint note; its dated gap baseline and counts stay intact.
Those pre-existing changes are preserved, not attributed wholly to FLC-1.

Preservation check: all four canonical FF-1 protocol/execution/evaluation/ledger
fingerprints match the [FLC-0 recorded identities](TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md).
All 72 protocol source pins and 6 execution implementation pins match. The
ledger remains COMPLETE. Checks parsed only immutable metadata and hashed bytes;
no empirical numerical replay, loss recomputation, bootstrap or new forecast.
No existing runtime source file, private corpus, dependency lock, FF-0/FF-1
artifact or consumed-holdout ledger is modified by FLC-1.

## Next boundary

FF-1 remains INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE; BaseRate BENCHMARK;
Logistic CHALLENGER / EXPERIMENTAL with no promotion; 2025 CONSUMED, one execution,
no post-holdout refit. FF-2 is deferred until FLC closes and a new governed proposal.

Deferred: executable neutral training, codecs/custody and lifecycle events
(FLC-2), tuning (FLC-3), diagnostics (FLC-4), full calibration composition
readiness (FLC-5), neutral Evaluation (FLC-6), end-to-end store/replay integration
(FLC-7), and closure (FLC-8). No new model family, public forecasting operation,
A6 behavior, A8 work, broker action, commit, tag or push.

Exact next task: **TIAF A7 / FLC-2 — TRAINING, MODEL IDENTITY,
PERSISTENCE AND LIFECYCLE NORMALIZATION**. Requested recommendation:
GPT-5.6 Sol — Extra High, for cross-owner artifact custody and lifecycle governance.
Suggested later commit: `feat(a7.flc1): normalize forecaster contracts and lifecycle seams`.
