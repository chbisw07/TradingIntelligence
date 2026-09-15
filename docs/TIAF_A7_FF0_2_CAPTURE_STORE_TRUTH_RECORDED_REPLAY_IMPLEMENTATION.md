# TIAF A7 / FF-0.2 — Capture Store, Truth and Recorded Replay

## 1. Decision and checkpoint

**2026-09-15, Asia/Kolkata — FF0_2_ACCEPTED**, limited to the synthetic
capture/truth/recorded-replay slice described below. A7 / FF remains
IMPLEMENTATION IN_PROGRESS. Forecast execution runtime is NOT_IMPLEMENTED;
FF-0 overall is not accepted. No empirical or calibrated forecast is claimed.

Entry was clean at `7be1726` (`feat(a7.ff0.1): implement forecasting contracts
target and clock foundation`). A6 remains frozen at `tiaf-a6-baseline`, commit
`6dc2ff304aae0e87540260b092919bb91e4d4189`. This pass does not commit, tag or push.

Authority: [accepted FF-0 plan](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md)
§§10–12, 14–18; [FF-0.1 foundation](TIAF_A7_FF0_1_CONTRACTS_TARGET_CLOCK_IMPLEMENTATION.md);
[A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md)
and [acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md);
[FF architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md),
[repeat acceptance](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE_REPEAT.md)
and [clock correction](TIAF_FORECASTING_FRAMEWORK_HISTORICAL_EVALUATION_CLOCK_SEMANTICS_CORRECTION.md).
Accepted architecture, plan, theses and frozen A6 remain unchanged.

## 2. Delivered boundary and ownership

```text
Supplied immutable ForecastResult + captured evidence/artifacts
      │ Forecast owner: append_forecast (no model execution)
      ▼
Forecast Capture Store ─────────────┐
                                   │ exact capture + exact outcome revision
Independent terminal evidence      ▼
      │ Evaluation: resolve_outcome → EvaluationLink → immutable Ledger snapshot
      ▼                            ▲
Outcome Journal ───────────────────┘
      └─ correction → new entry + predecessor (old rows/views unchanged)

Recorded replay: store → verify closure/identity → original capture
                no model, labeler, new run, clock rewrite or write
```

Forecast writes cannot implicitly append an outcome; Evaluation can append
truth before any forecast exists. Link construction and Ledger materialization
are explicit Evaluation operations. A shared local corpus does not merge their
ownership. `StoreOwner` defaults to READ_ONLY; FORECAST and EVALUATION admit only
their respective writes. These are trusted local caller roles, not authenticated
service identities or replacements for R5 startup governance.

## 3. Exact changed-file inventory and reuse

| Files | Change |
|---|---|
| `src/tiaf/forecasting/identity.py` | Add `CapturedBlobReference`, separating semantic content pins from storage-envelope pins; existing FF-0.1 digest semantics unchanged |
| `src/tiaf/forecasting/errors.py` | Add safe store/integrity error classes |
| `src/tiaf/forecasting/capture.py` | New immutable artifact/rights/snapshot/capture models and pure transitive-closure checks |
| `src/tiaf/forecasting/store.py` | New bounded JSON/JSONL corpus with typed ownership, immutable records and explicit integrity errors |
| `src/tiaf/forecasting/replay.py` | New recorded-only `verify_replay` |
| `src/tiaf/evaluation/forecast_contracts.py` | Add Outcome Journal entry, scientific OutcomeKey, Evaluation Link and Ledger snapshot; existing foundation classes unchanged |
| `src/tiaf/evaluation/forecast_truth.py` | New pure exact-close resolver; independent of forecast inputs |
| `src/tiaf/evaluation/forecast_linkage.py` | New exact compatibility/eligibility linkage |
| `tests/unit/forecasting/_capture_support.py` | Authored artifact closure and outcome fixture builders |
| `tests/unit/forecasting/test_capture_store_replay.py` | Persistence, immutability, tamper, rights, write faults, replay, golden and lean-import tests |
| `tests/unit/evaluation/test_forecast_truth.py` | Exact labels, missingness, clocks, revisions, invalidations and source-bar correspondence tests |
| `tests/unit/evaluation/test_forecast_linkage.py` | Exact links, absent results, shared truth and historical Ledger tests |
| `tests/fixtures/forecasting/ff0/capture_cases.json` | Ten-scenario test manifest and two pinned capture fingerprints; not a runnable corpus |
| `tests/fixtures/forecasting/ff0/README.md` | Explain foundation versus capture fixtures and how to run tests |
| `README.md`, `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_ROADMAP.md`, `docs/MILESTONES.md`, `docs/TIAF_IMPLEMENTATION_TARGETS.md`, `docs/TIAF_CAPABILITY_MAP.md`, `docs/TIAF_A7_DETAILED_ROADMAP.md`, `docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md` | Current status/navigation only: FF-0.2 accepted; separately authorized FF-0.3 next |
| This implementation record | Scope, evidence, acceptance mapping, limitations and handoff |

Reuse: native `ForecastContract`, `TiafDateTime`, `InstrumentKey`, `OHLCVBar`,
source references, FF-0.1 exact-price companions, knowledge checks and canonical
serializer; existing planner SHA-256 primitive and Evaluation secret-field check.
The inspectable local artifact/JSONL conventions in `evaluation/store.py` and
`a3_hardening/store.py` inform the store; neither existing store nor replay engine
is changed. No database abstraction, new dependency, optional SDK import or
public catalog entry is introduced. Tests reuse the unchanged FF-0.1 fixtures.

## 4. Persistence, schema and capture

Exactly the filesystem layout selected by plan §10:

```text
ff0_corpus/
  artifacts/<sha256>.json
  forecast_runs.jsonl
  outcome_records.jsonl
  evaluation_links.jsonl
  ledger_snapshots/<sha256>.json
  .writer.lock
```

No SQLite, persistent mutable index or authoritative `latest` pointer. Bounded
indexes are reconstructed and validated from disk on each operation. Known
schema IDs only, all at contract `schema_version: "1.0"`; the existing package
version remains `0.1.0`, a separate concept. Serializer profile remains
`tiaf.ff.canonical-json/1.0`.

New schema IDs: `tiaf.ff.captured-artifact`, `tiaf.ff.evidence-snapshot`,
`tiaf.ff.capture`, `tiaf.a7.outcome-journal-entry`,
`tiaf.a7.forecast-outcome-link`, `tiaf.a7.forecast-ledger-snapshot`.
Unknown versions/extra fields, duplicate JSON keys, nonfinite numbers and missing
recorded hashes reject. Reading a stripped hash does not silently generate one.

Capture nests the original result/request: request/run/result and observation
IDs, neutral subject, exact target/version, realization mode, cutoff/as-of,
computed/issued times, target window, binding/forecaster/artifact references,
status/absence, output and original result fingerprint. It adds captured canonical
evidence, explicit build/dependency-version references, recording time and its
own sealed identity. Model/code/profile references are data, never executable
imports selected from a request.

Every transitive reference resolves to captured canonical JSON content. The
native reference fingerprint pins that content; a second SHA-256 pins its
storage envelope, including rights and dependencies. Capture/outcome closures
pin both. Missing, duplicate, conflicting, cyclic or extra unreferenced closure
members reject. Snapshot bytes must match the request's evidence fingerprint;
ordered daily history cannot include the target outcome. Reference and qualified
terminal price companions must match their captured canonical bars. The existing
bar check proves numeric correspondence, not recovery of source decimal precision
from a float: the exact decimal companion remains separately required/preserved.

Synthetic-only rights policy `SYNTHETIC_FIXTURE_ONLY_V1` preserves retain/replay
permission and optional aware read expiry. Admission and selected-record access
enforce those rights; replay cannot refresh expiry or substitute current content.
Source identity hashes preserve provenance assertions, not issuer authenticity,
licensed rights or historically deployed operation.

## 5. Truth, missingness, clocks and revisions

The resolver accepts only the native RELIANCE NSE cash target
`equity.next_session_close.return_gt_zero@1.0`. It takes target/window, qualified
terminal input, availability-check evidence, evaluation/recording clocks and
captured closure; **no probability, forecaster, run or realization-mode input**.

| Supplied independent evidence | Recorded result |
|---|---|
| Qualified exact reference 105, terminal 106 | class 1 |
| Qualified exact reference 105, terminal 104 | class 0 |
| Equal exact closes, including equivalent decimal spellings | class 0 |
| Missing terminal before pinned due time | no label; MISSING/PENDING; window OPEN or CLOSED according to supplied resolution time |
| Missing terminal at or after pinned due time | no label; MISSING, CENSORED/INELIGIBLE |
| Late qualified terminal after a previously censored entry | new eligible revision; old censored entry unchanged |
| Invalid/nonpositive/nonfinite/partial/stale endpoint or unqualified calendar | malformed prices reject, otherwise no label/INELIGIBLE; never synthetic zero |
| Explicit source/action/schedule contradiction or unknown action coverage | no label/AMBIGUOUS; explicit invalidation evidence retained |

Comparisons use exact positive decimals, not rounded returns or binary-float
equality. Deadline is the supplied S22 open for S21, not selected from eventual
arrival time; equality at the boundary is censored. An explicit typed MISSING
terminal and an absent terminal both follow this missingness policy. No weekday
calendar guessing, adjusted-price repair, source preference or retargeting to S2.

Window state, observation state and label eligibility are separate. Operation
is UNKNOWN with `OPERATION_NOT_OBSERVED_IN_FF0`: no execution feed is not evidence
of NOT_TAKEN. Path/execution measures are NOT_APPLICABLE; no fabricated MFE/MAE,
fills, realized P&L, probability or utility. This slice records the class and
price facts, not metrics or a trading outcome.

For an eligible label:
`outcome_event_time <= label_available_at <= evaluated_at <= recorded_at`.
Qualification availability is the latest admission time of all required supplied
evidence, including the independent terminal check. Missing labels have no
invented event/label-availability clock; scheduled resolve time stays known.
All timestamps remain aware and normalize through `ZoneInfo("Asia/Kolkata")`;
JSON emits `+05:30`. There is no naive `datetime.now()` or manual offset arithmetic.

`OutcomeKey` binds target/version, neutral subject, S0/S1 event/window and price
basis; it excludes producer, mode and source revision. An immutable journal entry
has its own ID/hash, revision number and exact predecessor/reason. Revisions
cannot fork, skip, duplicate an entry ID or move recording/qualification time
backward. Material source/action/schedule correction creates a new explicit
invalidation revision; it never overwrites an old label. A changed scientific
window is a different key, not a quiet rewrite of S1.

## 6. Exact linkage, eligibility and Ledger

`link_forecast_outcome` revalidates both contracts and requires exact target,
version, subject, horizon, scientific window and reference/source-basis
compatibility. It pins the capture identity, original run/result/observation
identity, mode, OutcomeKey, exact outcome revision and link policy. A link cannot
predate either record. A resealed forged eligibility, mode or reference cannot
bypass the store's relation checks.

GENERATED plus qualified outcome yields ENGINEERING_LINK_ELIGIBLE under
`SYNTHETIC_EXACT_LINK_V1`; other forecast statuses or unavailable labels retain
NOT_EVALUABLE with reasons. Incompatible identity rejects instead of linking a
different observation. Qualified synthetic linkage is not empirical eligibility,
calibration, prediction validity, promotion or consumer admission. Explicit
`NO_METRICS_NO_POOLING` preserves this boundary.

An ACTUAL capture and multiple SIMULATED captures may share one outcome without
becoming independent market observations. Each retains its own mode/run/capture
identity. Later source corrections cannot silently legitimize earlier PIT inputs.

`ForecastLedgerSnapshot` is an immutable Evaluation-owned joined view of exact
links, resolving to immutable forecast/outcome records. New views may name a
predecessor; earlier links/views continue to resolve their old outcome revision.
It is not a second forecast store or a mutable label column attached to forecasts.

## 7. Replay and narrow APIs

| API | Boundary |
|---|---|
| `capture_artifact` / `validate_capture` | Pure packaging and exact closure/rights validation; no data acquisition |
| `ForecastCorpusStore(root, as_of, owner=READ_ONLY)` | Explicit absolute root and aware trusted access clock; constructor performs no I/O |
| `append_forecast` / `get_forecast` | Exact run identity; identical retry returns false without changing bytes; conflicting run/result identity rejects |
| `resolve_outcome` | Pure independent endpoint label calculation, invoked explicitly by Evaluation only |
| `append_outcome` / `get_outcome` | Independent journal and exact revision retrieval |
| `link_forecast_outcome` / `append_link` / `get_link` | Pure compatibility decision followed by separate owned persistence |
| `append_ledger` / `get_ledger` | Immutable exact joined view |
| `verify_replay(store, run_id)` | Reconstruct/verify original capture; no computation, new run, simulation or mutation |

Reads verify the bounded corpus, record seals, transitive source/artifact closure,
schema, identity, relation invariants and selected-record rights. Ordinary
contract-integrity checks are not a new truth resolution or forecaster execution.
Replay preserves the original mode, clocks, result and fingerprints exactly;
it does not call `resolve_outcome`, runtime, registry, model, provider or broker.
Fresh-process tests block those imports and external-call paths. Missing/corrupt
closure is an error, not partial successful replay.

**Recorded replay is not pinned recomputation.** FF-0.3 supplies the exact
BaseRate verifier and missing-verifier disposition. New historical simulation
requires a new explicit SIMULATED execution/capture; FF-0.2 can persist distinct
caller-supplied run IDs but does not allocate or execute a new run. Native usage
stays `NOT_RECORDED_CONTRACT_ONLY`, not fabricated zero-duration/zero-priced
execution telemetry.

## 8. Append safety, failures and trust limits

Each writer exclusively creates its local lock. Immutable blobs and Ledger files
use exclusive creation; journals append canonical complete lines. Full validation,
duplicate/revision/ownership/rights checks and size preflight precede data writes.
Only the owning invocation removes its own lock; a pre-existing stale/replaced
lock fails closed. Reads do not create directories or repair data.

The final complete journal line is a logical record commit. There is **no
cross-file atomic transaction or general rollback**, exactly as plan §10 requires.
The requested rollback tests therefore prove no persisted bytes on preflight
denial, then inject failure before the commit line and during a partial line:

- Valid orphan blobs from an interrupted append are not completed forecasts.
  An explicit identical retry may reuse those blobs if no corrupt line exists.
- A partial/corrupt line blocks reads and appends; no skipping or truncation.
- A write/fsync failure reports no commit claim. If a complete line reached
  disk, callers must inspect/retry the exact identity, not assume rollback.
- No power-loss durability, concurrent-reader snapshot, distributed locking,
  automatic repair, cleanup service or malicious concurrent-writer protection
  is claimed. Local append-only semantics are not filesystem WORM protection.

Bounds: 1 MiB per artifact/record, 256 rows per journal, 32 MiB total corpus,
256 artifacts per closure, 64 history bars/supplied sessions. Paths must be
explicit absolute corpus roots, not `/` or traversal paths. Symlinks, hardlinked
or nonregular data files and unknown corpus entries reject. This is a trusted
single-operator local store; host OS access controls remain necessary. Its
`as_of` is a supplied actual access clock, not a historical analysis override:
future recorded/created times reject. Tests inject it; a trusted clock source
and execution-time allocation remain FF-0.3. Hashes cannot authenticate clocks.

| Error family | Examples / effect |
|---|---|
| Native validation / `ValueError` | Invalid schema, naive clocks, unsupported target, malformed exact price, inconsistent facets; reject invalid construction |
| `ForecastIntegrityError` | Missing/tampered closure, conflict/fork/gap, source-bar mismatch, future recording or incompatible link; no success/repair |
| `ForecastStoreError` | Owner/rights/path/lock denial, bounds, read/write failure; stable safe reason message |

Errors expose reason codes rather than captured payloads or secrets; the store
does not log payloads, discover credentials or inspect `.env`. These local
exceptions are not a new public facade error taxonomy. No model/provider call,
model token or model charge is produced by this slice; no empirical price or
blanket machine-cost estimate is invented.

## 9. Fixtures and 28-case coverage

All prices, calendars and clock histories are openly synthetic. The ten scenarios
in [capture fixture notes](../tests/fixtures/forecasting/ff0/README.md) are authored
programmatically and written to temporary corpora by tests. `capture_cases.json`
is a manifest, **not** input for a replay CLI; no FF CLI exists yet. The original
`foundation_cases.json` is unchanged. Exact stored capture golden fingerprints:

| Specimen | Capture-envelope SHA-256 |
|---|---|
| ACTUAL | `3b8e7b1547028192a18c36c4eb789868cb58057f2285efc2a0e36f5213049462` |
| SIMULATED | `519c4bd7fb7b3f59d524a60af67d6e73b94bb24e508cdc60326a3d055d551c01` |

The original FF-0.1 result goldens remain unchanged and pass regression. These
new capture IDs intentionally also include captured source bytes/rights/build
and dependency references. They are not interchangeable with result hashes.

The captured forecaster/code/model payloads are explicitly non-executable
**contract specimens**, not a fitted or recomputable model. The 0.6 result remains
authored. The full 25-session input and twenty-transition BaseRate witness from
plan §17 belong to FF-0.3; current fixtures use S20–S22 and a reference bar plus
separate terminal evidence. Capturing opaque specimen content proves retention
and integrity, not scientific verification of a working forecaster.

| Plan cases | Current evidence and remaining obligation |
|---|---|
| FF0-01–03 | Satisfied: existing strict contracts/target/mode scope; new capture/truth/link/Ledger frozen tuple and JSON reconstruction checks |
| FF0-04–07 | Partial: supplied ACTUAL/SIMULATED clocks, leakage checks and retained closure pass; runtime completion/issuance, full witness and trusted execution provenance remain 0.3 |
| FF0-08–10 | Satisfied: strict open boundary, timezone/distinct clocks, supplied qualified schedule/exact-price guards; no empirical certification claim |
| FF0-11 | Pending: calculated deterministic BaseRate/witness in 0.3 |
| FF0-12 | Partial: finite/zero/one/count shapes; calculation/support behavior remains 0.3 |
| FF0-13–14 | Partial: qualification, all status and stored absence/link checks; runtime emission remains 0.3 |
| FF0-15 | Satisfied: existing finite singleton graph contracts |
| FF0-16 | Pending: exact static registry/COLD startup/absence in 0.3 |
| FF0-17 | Newly satisfied: immutable append/retrieve, identical retry, ID conflict, exact refs |
| FF0-18 | Partial: persisted ACTUAL plus two SIMULATED captures share one observation/outcome; fresh execution/run allocation remains 0.3 |
| FF0-19 | Newly satisfied: independent exact up/down/tie, decimal precision and separate truth clocks |
| FF0-20 | Newly satisfied: absent/typed-missing, exact deadline, censoring, invalidation and no invented label |
| FF0-21 | Newly satisfied: original plus correction, late proof, source/action/schedule invalidation, predecessor/time/fork/gap guards |
| FF0-22 | Newly satisfied: exact subject/target/session/version/basis/mode linkage, absent eligibility, immutable old/new Ledger |
| FF0-23 | Newly satisfied: stored reconstruction, canonical equality, no calls/relabel/new simulation/byte mutation |
| FF0-24 | Pending: pinned recomputation and missing-verifier behavior in 0.3 |
| FF0-25 | Newly satisfied: tamper, missing closure, partial line, stale lock, disk fault, rights and path denial |
| FF0-26 | Partial across stages: current lean-import/no-call/catalog/A6/R5 regressions pass; recheck later runtime/CLI integration |
| FF0-27 | Partial: store resource bounds and safe failure messages pass; deadline/attempt cost/accounting remain 0.3–0.4 |
| FF0-28 | Pending: local CLI engineering end-to-end acceptance in 0.4 |

Counted at the implemented synthetic assertion level: **7 newly satisfied,
14 cumulatively satisfied, 10 partial, 4 pending** out of 28. This is not “28
tests passed,” not empirical acceptance, and not the completed FF-0.4 corpus.

## 10. Validation and result

Commands use the existing `.venv`; no installation or download was needed.

| Validation | Result |
|---|---|
| `pytest -q tests/unit/forecasting/test_capture_store_replay.py tests/unit/evaluation/test_forecast_truth.py tests/unit/evaluation/test_forecast_linkage.py` | 113 passed |
| `pytest -q tests/unit/forecasting --ignore=tests/unit/forecasting/test_capture_store_replay.py` | 170 passed, unchanged FF-0.1 regressions |
| `pytest -q tests/unit/evaluation tests/unit/source_semantics tests/unit/contracts tests/unit/a6 tests/unit/test_r5_cold_startup.py` | 317 passed |
| `pytest -q` | **2,760 passed in 297.97s (4:57)** |
| `python -m compileall -q src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS, 585 source files |
| Fresh-process lean import / blocked live/model/labeler paths | PASS in targeted/full tests; original nine-operation catalog retained |
| Existing `validate_handbook.validate_links(True)` local Markdown validator | PASS: 12 Markdown files, 612 local links; no network |
| Current-status/protected-scope check | PASS: only the listed FF-0.2 code/tests/fixture and current documentation changed; accepted architecture, plan, historical records, theses, A6 and existing R1–R5 implementations unchanged |
| `git diff --check` | PASS |

Initial development failures were test-helper typing/placement and edge-case
checks fixed within the new slice. No accepted policy or lower-layer runtime
change was needed. Final test counts above are distinct invocations, not additive
unique totals; related suites intentionally overlap. All validation gates are
complete; the full suite adds 113 tests to the accepted 2,647-test FF-0.1 baseline.

## 11. Limitations, exclusions and next handoff

No architecture deviation: plan-selected JSON/JSONL is retained. In particular,
the brief's rollback wording is constrained by the accepted explicit no-cross-file-
transaction boundary, with failure behavior tested and disclosed in §8.
Remaining limitations are accepted scope, not a claim of production-grade storage,
authentic historical availability or empirical qualification.

Not implemented: BaseRate/count witness calculation, runtime dispatch/clock source,
run allocation, pinned recomputation, learned model/training, Logistic,
walk-forward metrics/Brier/log-loss, calibration, ensembles, LLM, FM/LFDE,
lifecycle registry, real source qualification, public facade/Shell, live provider,
broker, execution, A8 or frozen A6 changes. No remaining in-scope acceptance
blocker was found.

Exact next accepted-plan step: **FF-0.3 — BaseRate, COLD runtime and pinned
verification**. Exact next prompt title:

**TIAF A7 / FF-0.3 — BASERATE, COLD RUNTIME AND PINNED VERIFICATION**

It requires a separate bounded request; it has not begun. Suggested future commit,
only if separately authorized:
`feat(a7.ff0.2): implement forecast capture truth and recorded replay`.
No tag recommended. No commit, tag or push performed.
