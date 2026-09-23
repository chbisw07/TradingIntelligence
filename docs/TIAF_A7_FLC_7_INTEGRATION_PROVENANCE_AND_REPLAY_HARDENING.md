# A7 / FLC-7 — Integration, provenance and replay hardening

**FLC7_ACCEPTED**

Checkpoint: 2026-09-23, Asia/Kolkata. Acceptance validation complete.
Entry tree clean at `26a7053` (accepted FLC-6). Scope is additive internal
integration of FLC-1 through FLC-6. No public capability is added.

## Inspected gaps and integration decision

The [FLC completion plan](TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md),
FLC-1…6 implementation reports, native inference/adapters, training identity and
custody, optimization, diagnostics, calibration, normalized Evaluation, native
FF-0/FF-1 replay, lifecycle/approval contracts, capability map and active roadmap
checkpoints were inspected. Existing package stores are codec profiles of one
`ResearchForecastStore`; existing replay routines already own reconstruction.

The gaps addressed here are cross-package references, a bounded provenance
closure, consistent missing-bytes status, and checks on copied fields across
seams. Existing package hashes and numerical implementations are retained.

Two constraints from that inspection shape the reference lifecycle:

- FLC-2's restored numeric predictor is a pure probe, not an issued forecast.
  `ArtifactPrediction` captures its exact bundle/model/scaler/features/output
  without widening the FLC-1 Logistic issuance contract.
- FLC-5 accepts five authored reference probabilities. Its calibration branch
  remains explicit and separate from the learned probe; it does not pretend to
  calibrate that Logistic model. Actual Logistic calibration is still deferred.

## Unified lineage and provenance identity

[Contracts](../src/tiaf/forecasting/lifecycle_provenance.py) provide
`ProvenanceRecord`, `ProvenanceNode`, `ProvenanceEdge`, `LineageBranch`,
`InferenceCapture`, `InferenceContext`, `ArtifactPrediction`, `ReplayRequest`
and `ReplayResult`.

`ProvenanceRecord` pins a logical record ID, root `ForecasterKey`, exact policy
version, ten explicit branches, nodes, typed edges, evidence state, aware capture
time and content fingerprint. The graph carries references, not whole artifacts.
Native payloads stay in their original records/codecs. The FLC-1 capture wrapper
preserves its whole native envelope, with context stored separately.

Every branch is present exactly once: qualification, training, model,
preprocessor, inference, optimization, diagnostics, calibration, evaluation and
lifecycle. It contains references or explicit `NOT_APPLICABLE` / `NOT_REQUESTED`
absence. BaseRate needs neither a training branch nor learned artifacts.

```text
external qualification/data/configuration pins
                 ↑ TRAINED_FROM / USES
training request ← execution ← result/bundle
                 ↖ model identity → model / scaler / preprocessor
                                      ↑ DERIVED_FROM
                           captured numeric probe
                                      ↑ forecast reference + exact value
external Outcome Journal ← Evaluation input → request/population/policies
                                      ↑
                              Evaluation result/ledger
                                      ↑ APPROVAL_REFERENCES
                           external HELD review record

optional diagnostic branch → exact model / request / payload
optional calibration branch → authored source / component / artifact / result
optional optimization branch → plan / trials / training / evaluations / selection
```

Arrows in the persisted DAG run from dependent to prerequisite. Edge relations
are `DERIVED_FROM`, `TRAINED_FROM`, `USES`, `CALIBRATED_FROM`,
`EVALUATED_AGAINST`, `DIAGNOSES`, `SELECTED_FROM`, and `APPROVAL_REFERENCES`.
They are descriptive data, never instructions or callbacks. Nodes, edges and
branches are canonically sorted; branch reference order is retained as declared
semantic order. Duplicate nodes/edges, unknown endpoints, self-links, cycles,
unreachable nodes, missing stages and excessive depth are rejected.

The [integration adapter](../src/tiaf/forecasting/lifecycle_replay.py) derives
dependency edges from typed records and requires exact equality with the graph.
A caller cannot omit an edge, change its relation or downgrade a captured
dependency to an identity-only declaration. Training roots, inference contexts,
prediction model/scaler/bundle identities, diagnostic copied fields, evaluation
forecast values/participant identities and ledger children receive additional
cross-record checks.

## Fingerprints and time

All new records reuse `SealedResearch`, `semantic_fingerprint` and the existing
canonical JSON/SHA-256 primitive. No alternative hash implementation or registry
exists. Existing `flc:` and `flc6:` references keep their exact identities;
`flc7:` names only new codec records. Unsupported ID/version pairs fail closed.
Legacy full-envelope versus sealed-body hashing conventions remain explicit
behind their native adapters rather than being silently equated.

The full provenance fingerprint includes ID and capture time.
`structure_fingerprint` omits only this new envelope's ID and capture clock. It
still includes exact child capture fingerprints; it is **not** a promise that
different training executions have identical scientific identities. Existing
model scientific fingerprints and recorded execution timings remain untouched.

New clocks use the existing `ForecastDateTime` → `ZoneInfo("Asia/Kolkata")`
policy: naive times rejected, other aware zones normalized, JSON `+05:30`.
Inference retains ACTUAL versus SIMULATED mode, historical `as_of`, information
cutoff and original computation time. Replay separately records the caller's
aware `checked_at`. Graph capture cannot predate component creation/computation;
prediction cannot predate training completion; evaluation cannot precede its
captured probe; replay cannot predate the graph. No ambient clock enters replay.

The FLC clock audit found aware `datetime.now(TIAF_TIMEZONE)` only in existing
training/optimization execution observation code. FLC-7 changes no frozen
timestamp and introduces no naive `datetime.now()` or offset arithmetic.

## Replay seam and package closure

`replay_lifecycle` accepts a pinned provenance reference, exact target and target
kind, explicit mode, bounded read budget and checked-at time. It opens a fresh
read-only view of the same store. No write, subprocess, provider, broker, fit,
calibration fit, lifecycle execution or network operation occurs.

| Target | Required captured closure | RECORDED_VERIFY | RECONSTRUCT_FROM_ARTIFACTS |
| --- | --- | --- | --- |
| FLC-1 inference | Native result and exact context | Validate envelopes/context links | Existing inference adapter, compare exact result |
| FLC-2 numeric probe | Bundle, model, scaler, features and captured output | Check identity and clock links | Existing restored predictor, compare output |
| Training artifacts | Request, execution, result, native job/manifest and model/scaler identities | Validate canonical records and links | Existing metadata normalization/restore; never fit |
| Optimization | Request, plan, external grants, campaign claim, trial records and training/evaluation children | Verify recorded closure | Existing deterministic selection using recorded objectives; no new Evaluation |
| Diagnostics | Request, exact model/source, payload and envelope | Check recorded content and copied identities | Existing diagnostic replay |
| Calibration | Authored source, component, evidence, artifact, request, composition and result | Check captured content and lineage | Existing synthetic table application replay; no fit |
| Evaluation | Population, request, participants, external truth, input, metrics, statistics, pair table when applicable, result and ledger | Verify recorded closure without scoring | Existing FLC-6 synthetic-only evaluation replay |
| Provenance | Exact typed closure and edges | Validate canonical DAG and native links | Rebuild/check the graph from recorded dependencies; does not implicitly reconstruct every numerical child |
| Consumed FF-1 view | Existing read-only normalized final view and exact source identity pins | Historical recorded verification | UNSUPPORTED; no final scoring or second execution |

The reference test explicitly invokes each numerical package target; a graph
`MATCH` alone does not claim numerical reconstruction of all children.
`RECORDED_VERIFY` never calls `_reconstruct` or Evaluation scoring. It verifies
the pinned captured evidence rather than promising to recover missing source data.
Changing replay mode changes the request fingerprint.

## Custody, availability, authority and immutable storage

```text
identity exists  ── does not imply ── bytes available
bytes available ── does not imply ── use authorized
verified lineage ─ does not imply ── approval / promotion / activation
```

Each node declares custody and either `REQUIRED_BYTES` or `IDENTITY_ONLY`.
External qualification/data/policy pins can be identity-only: their inclusion
does not claim a licensed corpus is archived or mounted. Replay returns these
unresolved identities explicitly. Selecting an identity-only node as an executable
target yields `UNAVAILABLE`. A graph-only recorded `MATCH` preserves that
limitation in `identity_only` and grants no reuse.

All required nodes in the envelope are checked, even for a narrower replay
target. Thus losing a declared calibration artifact makes that envelope's
closure `UNAVAILABLE`; an optional branch omitted at capture has no such
dependency. Missing/unmounted bytes return `UNAVAILABLE`; corrupt bytes,
unsupported record versions, inconsistent links and read-budget exhaustion
return `MISMATCH`. No invalid child is silently repaired or substituted.

`LifecycleStore` unions existing codec profiles over the **same**
`ResearchForecastStore.get/put`. This adds no persistence engine, mutable active
alias, model registry, evaluator or graph database. Identical duplicate writes
are idempotent; changed content gets a new identity; conflicting/corrupt duplicate
bytes are rejected and left unchanged. Previous versions remain present.

## Package lineage, component observability and authority

Training request/execution/result, model/scaler, raw probe/native forecast,
diagnostic payload, calibration component/raw/transformed result, evaluation
participant/population/truth/metric/statistical policies are separately visible.
Nested native payloads never erase component identity.

Optimization keeps request → plan → trial → training/evaluation → deterministic
selection, including its durable campaign claim. Failed/unattempted trial states
remain native; replay does not retry them or create replacement evidence.
Diagnostics retain request/source/payload. Calibration preserves both raw and
transformed values with its distinct authored source. Evaluation links forecast
references and exact probabilities to captured inputs while truth stays external.
An externally supplied `ApprovalDecision` may reference Evaluation without
changing its fingerprint. The integrated reference uses `HELD`, not activation.

All provenance authority fields are literal false: training, calibration fitting,
approval, promotion, activation, unseen status and holdout execution. Replay also
fixes reuse false and lifecycle effect NONE. Hash integrity is not reviewer
authentication; external governance still owns authorizations and their history.

The consumed FF-1 view forces `HISTORICAL_ACCEPTED_CONSUMED`. Relabeling it as
synthetic fails cross-record validation. All reconstruction under consumed
provenance is rejected as `UNSUPPORTED`; recorded inspection remains possible.
No API for same-experiment refit, calibration rescue, renewed holdout access or
second one-shot execution is introduced.

## Synthetic reference and adversarial evidence

The integration fixture uses FLC-2's existing externally authorized, fixed
synthetic recipe once, then persists/restores the resulting artifacts. Five
numeric probes feed a single-participant independent Evaluation with externally
authored synthetic labels. A coefficient diagnostic and external HELD review
reference the same model/evidence. FLC-5's optional authored calibration branch
is separately captured and replayed. Another bounded fixture captures FLC-3's
six synthetic trials and verifies recorded selection. Separate BaseRate cases
cover ACTUAL and SIMULATED native inference without training requirements.

These are engineering fixtures, not empirical model performance or calibrated
Logistic evidence. Existing native RELIANCE/date spellings in the fixed FLC-2
recipe are codec compatibility, not acquired market data. No Dhan/provider/broker
or network call, empirical refit, or consumed holdout scoring is performed.

| Tamper target | Expected result |
| --- | --- |
| Training request/result, model/scaler | MISMATCH; original corpus unchanged |
| Forecast/probe, diagnostic, calibration artifact/result | MISMATCH |
| Evaluation request/result, provenance bytes | MISMATCH |
| Resealed wrong edge, identity-only downgrade, copied diagnostic subject | MISMATCH / admission rejection |
| Resealed Evaluation probability inconsistent with referenced probe | Admission rejection |
| Cycle, self-link, unknown relation, bounds violation, naive timestamp | Contract rejection |
| Consumed evidence relabeled as synthetic; authority flags | Rejection; no execution |

| Missing-artifact case | Result |
| --- | --- |
| Model or scaler | UNAVAILABLE |
| Calibration artifact | UNAVAILABLE |
| External Ground Truth capture | UNAVAILABLE |
| Evaluation input or native inference context | UNAVAILABLE |
| Private corpus represented by fingerprint only | Explicit identity-only; target UNAVAILABLE |
| Corpus unmounted after opening | UNAVAILABLE, zero artifact reads |
| Optional diagnostic not requested | Explicit branch absence, no fabricated failure |

Offline tests block training-library imports, subprocess, socket and store writes.
All recorded-mode tests also block reconstruction and scoring. The corpus bytes
are compared before/after replay. Duplicate/conflict, stale versions, aware-clock
equivalence, ordinary JSON arrays, immutable collections, depth and read-budget
checks are included.

## Bounds and backward compatibility

Maximum 256 provenance nodes, 1,024 edges, ten branches with at most 64 references
each, graph and typed-record depth 32, and at most 512 record reads per replay.
Traversal is iterative; no nested provenance/replay dispatch is allowed during
capture. Existing store limits remain 1 MiB/record, 65,536 records and 2 GiB/corpus.
No unlimited recursive graph walk, arbitrary script edge or plugin dispatch.

FF-0/FF-1 native sources and records stay byte- and semantically unchanged;
FLC-1…6 behavior and identities remain untouched. The FF-1 view is adapted by
the existing FLC-6 read-only mapper. No in-place migration or re-fingerprinting.

Hash-only preservation checks assert these original fingerprints:

| Record | Fingerprint |
| --- | --- |
| Protocol | `2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814` |
| Execution | `2948bc46874f8196c535720bd4f7882f6293fc96077acb563e2e11409c3e4840` |
| Evaluation | `8c0556e7b88284c170db57d745de7ece707d365ab52a585db5ebb0d3e81a7d0e` |
| Ledger | `630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583` |

All 72 protocol source pins + six execution implementation pins match (78/78).
FF-1 remains INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE, BaseRate BENCHMARK,
Logistic CHALLENGER / EXPERIMENTAL, promotion NO, 2025 CONSUMED, execution count
one, post-holdout refit forbidden.

## Validation, files and handoff

Validation commands (all pytest fixtures are synthetic; legacy checks read metadata):

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_lifecycle_integration.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_lifecycle_integration.py tests/unit/forecasting/test_evaluation_normalization.py tests/unit/forecasting/test_calibration.py tests/unit/forecasting/test_forecaster_diagnostics.py tests/unit/forecasting/test_optimization.py tests/unit/forecasting/test_forecaster_lifecycle.py tests/unit/forecasting/test_forecaster_seams.py --tb=short
.venv/bin/pytest -q tests/acceptance/ff0 tests/unit/forecasting/test_contracts.py tests/unit/forecasting/test_pinned_runtime_replay.py tests/unit/forecasting/test_identity_isolation.py tests/unit/forecasting/test_logistic_training.py tests/unit/forecasting/test_logistic_forecasts.py tests/unit/forecasting/test_capture_store_replay.py tests/unit/evaluation --tb=short
.venv/bin/pytest -q --tb=short
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
.venv/bin/python -c 'from docs.handbooks.a7_forecasting.validate_handbook import validate_links; print(validate_links(True))'
git diff --check
```

- Final targeted run: **54 passed in 23.77s**.
- FLC-1…7 combined regression: **334 passed in 162.36s**. This ran before the
  last root/native-clock checks; final targeted and full-suite runs include them.
- FF-0 acceptance / FF-1 compatibility / replay-store / Evaluation:
  **490 passed in 332.83s**.
- Full repository suite on final source: **3,779 passed in 909.42s (0:15:09)**.
- Compileall and Ruff PASS; mypy PASS over **673 source files**.
- Documentation: **898 local links across 14 Markdown files** PASS.
- Balanced fences in **12 changed/new Markdown files**, whitespace in all
  **four new files**, and `git diff --check`: PASS.

Created:

- `src/tiaf/forecasting/lifecycle_provenance.py`
- `src/tiaf/forecasting/lifecycle_replay.py`
- `tests/unit/forecasting/test_lifecycle_integration.py`
- this report.

Modified active navigation: `README.md`, `docs/ARCHITECTURE.md`,
`docs/IMPLEMENTATION_ROADMAP.md`, `docs/MILESTONES.md`,
`docs/TIAF_IMPLEMENTATION_TARGETS.md`, `docs/TRADINGINTELLIGENCE_ROADMAP.md`,
`docs/TIAF_A7_DETAILED_ROADMAP.md`,
`docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md`,
`docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md`,
`docs/TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md` and
`docs/TIAF_CAPABILITY_MAP.md`. The capability inventory links the internal
implementation without adding a public operation.
Historical FLC acceptance reports and frozen baseline documents remain unchanged.

Deferred: general Logistic/calibrator composition execution, broader evaluation
populations, public runtime exposure, empirical research, provider acquisition,
production monitoring, distributed custody and FF-2. FLC-8 owns independent
review of the full reference lifecycle and the final FLC freeze decision.

Acceptance blockers: **none**. All existing runtime source files and frozen
FF-0/FF-1 artifacts remain unchanged. Four canonical fingerprints and all
78 frozen pins match; no empirical numerical rerun occurred.

Suggested commit after acceptance:
`feat(a7.flc7): harden integration provenance and replay`.
No commit, tag or push is performed; no tag proposed.

Exact next task, after acceptance and a separate request:
**TIAF A7 / FLC-8 — REFERENCE IMPLEMENTATION CLOSURE AND FLC ACCEPTANCE**.
Requested model: **GPT-6 Astra — Extra High** for independent closure across
architecture, lineage, compatibility, authority and readiness for future FF-2.
