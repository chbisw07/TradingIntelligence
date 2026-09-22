# A7 / FLC-2 — Training, model identity, persistence and lifecycle normalization

Implementation checkpoint: 2026-09-22, Asia/Kolkata. **FLC2_ACCEPTED.**
Internal additive Learning seams only; no public operation, empirical fit,
promotion executor, runtime selection, calibration or scientific re-evaluation.

Accepted entry: clean working tree at `3c1339f` (FLC-1). FF-0/FF-1 remain frozen.
FF-1 remains INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE, infrastructure accepted,
BaseRate BENCHMARK, Logistic CHALLENGER / EXPERIMENTAL, promotion eligibility NO.
Protected 2025 remains CONSUMED, one final execution used, no post-holdout refit.

## Inspected architecture and reuse

The [FLC completion plan](TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md),
[FLC-1 implementation](TIAF_A7_FLC_1_FORECASTER_CONTRACT_AND_LIFECYCLE_SEAM_NORMALIZATION.md),
[FF architecture §§9/22](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md), and
[A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md)
remain the design authorities. The native FF-1 training, fifth-fold preparation,
model/scaler/job schemas, stores, replay, dependency locks and FLC-1 lookup/adapters
were inspected before implementation.

Reusable: frozen contracts, aware canonical JSON/SHA-256, native sealed artifacts,
isolated bounded worker, pure reconstruction, content-addressed research store,
exact read-only implementation lookup. Logistic-specific: five ordered features,
fixed solver/configuration, native split/grant/qualification and research clocks.
FLC-1 training contracts deliberately remain proposal-only. They are not silently
widened into executable requests: actual Learning identities/results live here.

Native artifacts historically carry fixed role/lifecycle strings. They remain
unchanged. Lifecycle events now have a separate typed view rather than mutating
those artifacts or interpreting a successful fit as independent approval.

## Identity and ownership

```text
External owner: experiment + request-pinned synthetic training authority
                              │
Learning: TrainingIdentity → TrainingExecution → TrainingResult
               │                  │                   │
               └── native manifest/job refs ──────────┤
                                                     ▼
                                   ModelArtifactIdentity → PreprocessorIdentity
                                                     │
                                 existing research store + additive codecs
                                                     │
                           restored native artifact → pure numeric predictor
                                                     │
External reviewer: TransitionRequest → ApprovalDecision → retained event history
                                                     │
                                     ActivationState: NOT eligible / selected
```

Training creates an artifact. It does not create authority.

| Record | Identity and responsibility |
| --- | --- |
| `ExperimentIdentity` | Immutable experiment/candidate, exact forecaster/version and design reference |
| `TrainingIdentity` | Scientific request: experiment, family, subject, target/version, feature schema/version/hash, population/split, configuration, qualification, dataset/profile, dependency lock, implementation, native authority and creation clock; no mutable execution state |
| `TrainingExecution` | Separate request-linked, native-job-linked execution hash, start/end clocks, native status, observed library versions, resource policy and elapsed/CPU/RSS observations |
| `TrainingResult` | TRAINED / UNAVAILABLE / FAILED; exact request/execution references, optional model/preprocessor identities, diagnostics references and failure reason |
| `ModelArtifactIdentity` | Canonical native artifact hash/version, forecaster/family/version, request/execution, subject/target/features/configuration, optional preprocessor and original creation time |
| `PreprocessorIdentity` | Separate canonical scaler hash, implementation/configuration, request and training-population hash; parameters stay in native scaler, not generic forecaster identity |
| `ArtifactPersistence` | Logical custody declaration, never inferred availability or scientific/use approval |
| `LifecycleSubject` / history | Forecaster/artifact, role, initial evidence state and externally authored source events |
| `ApprovalDecision` | Exact transition/subject, authority/reviewer, evidence, scope, reason, decision clock and expiry |
| `ActivationState` | Separate eligibility/selection seam; both fixed false throughout FLC-2 |

Content-addressed references serve as request/execution/result IDs; there is no
mutable UUID alias or “latest” model. Their fingerprints are deliberately different.
The request includes declared creation time, while native FF-1 full/scientific
fingerprints retain their original distinctions and are never replaced by a wrapper
hash. Scientific target/schema IDs retain their native versioned spellings.

All new records reuse sealed research schema `2.0`, immutable models and tuple
collections accepting Python lists/JSON arrays. Serialization emits JSON arrays.
All clocks reject naive datetimes and normalize through
`ZoneInfo("Asia/Kolkata")` to ISO-8601 `+05:30`. Package `0.1.0`, existing contract
`1.0`, research schema `2.0`, native model artifact `1.0` and implementation version
are separate concepts. No dependency or package version changed.
FLC content references use the record's codec/schema version (`2.0` for these
research records); `ModelArtifactIdentity.model_version` separately preserves
the native model artifact version `1.0`. A new wrapper is not a new fitted model.

Execution libraries come from the native successful artifact. Missing/failed jobs
may have no observed versions; worker/process identity is explicitly `None` when
the existing job did not record one. It is not fabricated. Cost remains UNPRICED,
not an invented monetary zero. The native 60-second/512-MiB/one-thread worker and
single-attempt boundary remain in effect.

## Persistence, availability and registry

`ForecasterStore` is a codec profile of the existing `ResearchForecastStore`, like
the existing fifth-fold profile. It inherits the same `put/get`, canonical JSON,
safe paths, exclusive writes/fsync, 1-MiB record, 65,536-record and 2-GiB bounds.
No new database, I/O engine, experiment-tracking platform, pickle, mutable alias,
registry service or lifecycle writer is introduced.

`persist_training` validates native job/manifest lineage before writing children,
then publishes the bundle last. Identical writes are idempotent. Changed content
has a new hash; corrupted duplicates fail. Interrupted writes cannot publish a
complete bundle. `restore_training` checks the exact pinned parent, native job,
manifest, request/result/model/scaler closure and recomputed **metadata** view.
Missing/mismatched/unknown-version artifacts are explicit failures, not substitutions.
Canonical native model/scaler/job bytes are copied unchanged if custody is requested;
there is no migration or resealing of source records.

| Custody class | Intended material | What it does not prove |
| --- | --- | --- |
| TRACKED_REPOSITORY_METADATA | References, fingerprints, governance reports | A private model/data blob is installed |
| LOCAL_RESEARCH_ARTIFACT | Ignored local canonical models/scalers/results | Scientific approval or runtime registration |
| PRIVATE_LICENSED_DATA | Privately entitled evidence custody reference | Permission to disclose, fit, or reuse holdout |
| GENERATED_EPHEMERAL | Temporary synthetic engineering products | Durable retention or production suitability |

Locations are logical references, not exposed private paths. A declaration always
says NOT_CHECKED; `inspect_availability` separately reports PRESENT_VERIFIED or
UNAVAILABLE at a supplied time. Neither grants use. Read-only restoration does not
require sklearn/numpy/scipy/joblib/threadpoolctl, a provider, an evaluator or a refit.

| Question | Owner / answer |
| --- | --- |
| What exists, with which bytes/lineage? | Existing Learning custody and exact content references |
| Which implementation/version/capability is known? | Existing registry plus unchanged FLC-1 read-only adaptation view |
| What lifecycle decision was externally authorized? | Pinned review/event records; not the model or evaluator |
| What may run or influence outputs? | Separate future COLD admission/activation, NOT FLC-2 |

The store profile is not consulted by runtime startup and does not register any
forecaster. FLC-1 descriptors stay fixed: BaseRate BENCHMARK/UNSPECIFIED with no
training or learned artifact requirement; Logistic CHALLENGER/EXPERIMENTAL.

## Lifecycle, lossless source events and approval

The existing FLC-1 lifecycle enum is extended additively, without changing either
descriptor: EXPERIMENTAL → VALIDATED → SHADOW → APPROVED. SUSPENDED and RETIRED
are explicit. UNSPECIFIED remains the truthful legacy BaseRate state, not approval.
There is no “active” or “challenger” lifecycle state.

`LifecycleHistory` is a bounded, predecessor-linked, caller-pinned chain, not a
mutable current-state cache. Role stays on the immutable subject. Source event
IDs/names/schema, effective/recorded clocks, original evidence, scope/expiry,
authority/reviewer and old/proposed policy references are retained.

REGISTERED, TRAINED and CALIBRATION_FITTED observations remain EXPERIMENTAL.
EVALUATED observations preserve the current state. No observation invokes an
evaluator or calibration code. VALIDATED requires an external decision;
SHADOW_APPROVED and ADVISORY_APPROVED retain their original event names while
mapping to the distinct lifecycle states. DENIED/HELD/REJECTED preserve the
previous state and policy. Suspension history survives denied resumption.
Approved resumption cannot skip to a state not previously attained; retirement
is terminal. Unknown, expired, missing, mismatched or illegal transition data fail.

Successful transition demonstrations are restricted to explicitly synthetic
history, starting EXPERIMENTAL. Read-only legacy history cannot execute successful
promotion. A transition record, even when externally APPROVED, has runtime effect
NONE; activation eligibility/selection are fixed false. There is no transition,
approval or activation method on any trainer, result, forecaster or evaluator.

FLC-2 validates declared authority/reference/scope integrity; it does **not** claim
cryptographic reviewer authentication or implement an enterprise authorization
service. Trusted callers own authority issuance, experiment/candidate uniqueness,
custody and choosing an authoritative predecessor. A forged authority document or
an old history prefix must never be treated as current runtime authorization.
Actual admission, registry concurrency, revocation/latest-state resolution and
promotion execution remain deferred, with no public route bypassing that boundary.

## Consumed-holdout guard and bounded synthetic reference

`TrainingAuthorization` is independent of lifecycle approval and pins one exact
experiment/candidate/version, request, qualification, input and custody-root hash.
Evidence policy must be SYNTHETIC_TRAIN_ONLY; the experiment must be OPEN and have
no protected/consumed holdout. CLOSED, PROTECTED and CONSUMED are rejected before
worker launch. READ_ONLY_LEGACY requests cannot execute. Changed candidate,
version, experiment, qualification, input or location invalidates the existing
authority. External ownership must issue a genuinely new experiment and grant for
new scientific work; renaming/resealing metadata cannot renew FF-1 authority.

The only executable adapter is `execute_synthetic_once`. It has **no observation
input parameter**: it reconstructs a fixed 600-row integer-pattern recipe and
requires the request to match it exactly. Native RELIANCE/schema/date spellings
are codec compatibility only, not empirical data or real trading sessions.
Dataset/qualification/profile pins describe authored engineering data. Caller
supplies creation, implementation and dependency-lock pins explicitly. A grant
cannot relabel an arbitrary empirical population into this recipe.

An exclusive durable attempt claim precedes worker launch, following the existing
fifth-fold custody pattern. Failure/crash/persistence error consumes the attempt;
no retry orchestration exists. Reopened stores are read-only; a different root
does not match the original grant. As with the existing store, this is bounded
single-writer local custody, not distributed locking or a cross-file transaction.

Reference proof in [the FLC-2 tests](../tests/unit/forecasting/test_forecaster_lifecycle.py):
new synthetic request/grant → existing isolated native Logistic worker → normalized
execution/result → canonical model/scaler persistence → exact restore → pure
`RestoredLogisticPredictor.predict` → raw probability → externally HELD lifecycle
record linked to that same model identity → activation remains false.

The restored predictor is the **numeric leaf**, not an alternative forecast issuer.
It returns the existing RAW/UNKNOWN `BinaryProbabilityOutput`; it does not invent
issuance clocks, qualify inputs or bypass FLC-1 admission. A one-fit synthetic job
must not be disguised as the qualified four-fold FF-1 research handoff required by
the FLC-1 Logistic envelope. Existing FLC-1 tests separately prove complete native
forecast/inference-envelope preservation on the synthetic FF-1 compatibility corpus.
BaseRate continues directly through its unchanged inference/replay path, with no
training request, model, scaler or fake training success.

## Compatibility and failures

| Legacy path | Normalized view | Migration | Frozen byte change | Semantic/replay impact |
| --- | --- | --- | --- | --- |
| FF-0 BaseRate registry, requests/results, capture | Unchanged FLC-1 BaseRate adapter; optional artifact-free lifecycle metadata | None | NO | NO; learned training bypassed |
| FF-1 `TrainingJob` / fifth-fold job / native manifest | `TrainingIdentity` + `TrainingExecution` + `TrainingResult` read-only view | None | NO | NO; historical native grant never renewed |
| FF-1 `LogisticArtifact` | `ModelArtifactIdentity` plus exact native content reference | None | NO | NO; native coefficients and reconstruction retained |
| FF-1 `ScalerArtifact` | Separate `PreprocessorIdentity` and original scaler | None | NO | NO; same order/means/scales/class convention |
| FF-1 forecasts / `TrainingRun` | Existing native envelope and FLC-1 adapter | None | NO | NO; no forecast regeneration required |
| FF-1 evaluation/protocol/execution/ledger | Existing canonical records, hash-only preservation audit | None | NO | NO; consumed evidence not re-evaluated |
| FLC-1 inference/proposal/calibration-compatible seams | Inference/proposals unchanged; additive lifecycle enum and separate Learning contracts | None | NO for captured evidence | NO; compatibility never grants calibration fitting |

Invalid requests, missing qualification, mismatched native lineage, unauthorized
training, unavailable artifacts/replay closure, and illegal/missing approvals use
existing validation/ValueError failures. Native missing dependencies retain
UNAVAILABLE; worker failure retains FAILED, reason and execution linkage, without
inventing a model/scaler. Persistence faults remain explicit exceptions with a
consumed attempt and no complete parent; incomplete artifacts are not reported as
success. Activation true is invalid. No oversized failure taxonomy is added.

## Validation and frozen evidence

Completed checks:

- FLC-2 final targeted module: **55 passed in 43.73s**. One new deterministic
  synthetic worker fit per invocation; tests do not fit empirical models.
- FLC-1, FF-0 acceptance/contracts/pinned replay/identity isolation, FF-1 native
  training artifacts and forecast replay: **251 passed in 180.39s**.
- Compileall (`src scripts`), Ruff (`src tests scripts`), mypy (`src tests`,
  **655 source files**) and `git diff --check`: PASS.
- Documentation: **705 local links and 26 anchors across 11 Markdown files**
  PASS; Markdown fences balanced.
- Full suite: **3,527 passed in 950.04s (15m50s)**, one full run, no failures or
  skips. No concurrent test jobs. The earlier FLC-1 wall-clock-sensitive workflow
  failure did not recur; its source and tests remain untouched.
- No remaining FLC-2 acceptance blocker. This is engineering/lifecycle-seam
  acceptance, not scientific approval or permission to fit empirical models.

Commands (offline engineering tests):

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_lifecycle.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_seams.py tests/acceptance/ff0 tests/unit/forecasting/test_contracts.py tests/unit/forecasting/test_pinned_runtime_replay.py tests/unit/forecasting/test_identity_isolation.py tests/unit/forecasting/test_logistic_training.py tests/unit/forecasting/test_logistic_forecasts.py --tb=short
.venv/bin/pytest -q --tb=short
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
git diff --check
```

Hash-only audit (plain JSON/canonical bytes, **no final-evaluation validators**):

| Canonical record | Preserved fingerprint |
| --- | --- |
| Protocol | `2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814` |
| Execution | `2948bc46874f8196c535720bd4f7882f6293fc96077acb563e2e11409c3e4840` |
| Evaluation | `8c0556e7b88284c170db57d745de7ece707d365ab52a585db5ebb0d3e81a7d0e` |
| Ledger | `630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583` |

All four MATCH; 72 protocol source pins plus 6 execution pins MATCH. Native FF-0
and FF-1 source files/locks are not edited. The only existing Python source edit
is the additive FLC-1 lifecycle enum. No empirical final-holdout numerical replay, loss
recomputation, empirical fit, bootstrap, provider, broker or network calls occur.

## File scope and next boundary

Created: [training identities](../src/tiaf/learning/forecaster_training.py),
[external training authority](../src/tiaf/learning/forecaster_authority.py),
[custody profile/restore](../src/tiaf/learning/forecaster_custody.py),
[lifecycle records](../src/tiaf/learning/forecaster_lifecycle.py),
[bounded synthetic adapter](../src/tiaf/learning/forecaster_reference.py),
the FLC-2 test module linked above and this report.
Modified source: [shared lifecycle enum](../src/tiaf/forecasting/forecaster_seams.py).
Navigation: README, ARCHITECTURE, IMPLEMENTATION_ROADMAP, MILESTONES,
TIAF_IMPLEMENTATION_TARGETS, TRADINGINTELLIGENCE_ROADMAP, A7 detailed roadmap,
FF detailed roadmap, A7 architecture and the FLC plan's subsequent-checkpoint note.
FLC-1's accepted implementation/validation history is unchanged.

Deferred: optimizer/trial selection (FLC-3), diagnostics/calibration/evaluation
completion (remaining FLC), empirical training, authenticated approval services,
actual promotion/activation and public runtime exposure. FF-2 is not started;
it requires FLC closure and a separately approved new research/data/protocol
proposal. No A6/A8 changes. No commit, tag or push.

Suggested later commit, only after user review:
`feat(a7.flc2): normalize training identity persistence and lifecycle`.
No tag yet.

Exact next task: **TIAF A7 / FLC-3 — BOUNDED DEVELOPMENT-ONLY OPTIMIZATION**.
Recommended model: **GPT-6 Astra — High**; bounded implementation work under
explicit development-only controls, not authority for new empirical fitting.
