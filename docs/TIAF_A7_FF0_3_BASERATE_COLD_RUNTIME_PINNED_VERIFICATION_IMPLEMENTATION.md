# TIAF A7 / FF-0.3 — BaseRate, COLD Runtime and Pinned Verification

## 1. Decision and checkpoint

**2026-09-15, Asia/Kolkata — FF0_3_ACCEPTED**, confined to the internal,
synthetic BaseRate runtime described here. A7 / FF is IMPLEMENTATION IN_PROGRESS;
FF-0 overall is **not** accepted. Public forecast capability is NOT_PUBLISHED.
FF-0.4 engineering CLI and acceptance hardening remains separately authorized work.
This is neither empirical model qualification nor evidence of historical deployment.

Entry was clean at `79c9726` (`feat(a7.ff0.2): implement forecast capture truth
and recorded replay`). A6 remains frozen at `tiaf-a6-baseline`, commit
`6dc2ff304aae0e87540260b092919bb91e4d4189`. No commit, tag or push in this pass.

Authority: [accepted FF-0 plan](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md)
§§6–18; [FF-0.1 foundation](TIAF_A7_FF0_1_CONTRACTS_TARGET_CLOCK_IMPLEMENTATION.md);
[FF-0.2 capture/truth/replay](TIAF_A7_FF0_2_CAPTURE_STORE_TRUTH_RECORDED_REPLAY_IMPLEMENTATION.md);
[A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md) and
[acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md);
[FF architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md),
[repeat acceptance](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE_REPEAT.md)
and [clock correction](TIAF_FORECASTING_FRAMEWORK_HISTORICAL_EVALUATION_CLOCK_SEMANTICS_CORRECTION.md).
Accepted architecture, original implementation records, plan, theses, deferral
rows, R1–R5 contracts and frozen A6 remain unchanged.

## 2. Runtime and ownership

```text
Trusted local startup                           Immutable FF COLD owner
  explicit config + pinned count witness ──────→ exact static registry lookup
  captured sources + build + corpus root         frozen BENCHMARK singleton
                                                           │
Validated request + captured input closure                  │
  └─ rights / identity / clocks / PIT qualification ─────────┤
                                                           ▼
                          AdmittedSupport: counts + eligible historical refs
                                                           │
                          HistoricalBaseRateForecaster: k/n or explicit absence
                                                           │
                          Runtime: fresh IDs, actual usage, completion / issue
                                                           │
                          FF-0.2 Forecast Capture Store ←───┘
                               │                     │
              recorded replay │                     │ exact pinned verification
              no invocation   ▼                     ▼ separate attempt/report
                      original capture         compare reconstructed payload

Independent target outcome → Evaluation Journal → exact link → immutable Ledger
                     No Outcome Journal query is available to the forecaster.
```

`Forecaster.descriptor()` exposes immutable metadata;
`Forecaster.forecast(request, admitted_support) -> GenerationPayload` is the
pure seam. `ForecastRuntimeOwner.run(request, snapshot, artifacts)` owns clocks,
`ForecastResult` construction and persistence and returns a `ForecastCapture`
containing that result. This makes the brief's conceptual result-returning
interface concrete without giving the scientific primitive clock/store authority.
It follows the accepted plan's ownership split; no public facade is added.

The brief's conceptual PRIMARY example is **not** an approval to publish a
PRIMARY: plan §§6/15/18 require exactly one BENCHMARK root, one primitive, zero
edges and zero PRIMARY roots. Existing `ForecastComposition` enforces that shape.
Composition identity is separate from forecaster identity and profile/config identity.

## 3. Exact changed-file inventory and reuse

| File(s) | Change |
|---|---|
| `src/tiaf/forecasting/forecasters.py` | Pure protocol, single built-in BaseRate, immutable descriptor/catalog/exact registry, code-owned policy and dependency declarations |
| `src/tiaf/forecasting/support.py` | Frozen twenty-transition count witness, exact-price/bar correspondence and bounded PIT admission |
| `src/tiaf/forecasting/clocks.py` | Trusted aware system clock and monotonic duration seam |
| `src/tiaf/forecasting/execution.py` | Lean immutable invocation usage, support summary, inference provenance and verification report contracts |
| `src/tiaf/forecasting/runtime_contracts.py` | Internal COLD config, simulation profile and exact binding contracts |
| `src/tiaf/forecasting/runtime.py` | Explicit startup, immutable owner, admission, one attempt, clock/status/usage construction and native capture persistence |
| `src/tiaf/forecasting/contracts.py` | Add optional recorded `inference` facts; preserve legacy result serialization and hashes; retain existing status and broker-field guards |
| `src/tiaf/forecasting/enums.py` | Add `HISTORY_SUPPORT_INSUFFICIENT` and `LOCAL_DEADLINE_EXCEEDED` reasons; no new generation status |
| `src/tiaf/forecasting/capture.py` | Pure selection of the exact transitive artifact closure from a supplied bounded shelf |
| `src/tiaf/forecasting/store.py` | Read-only `get_forecast_artifacts(run_id)` for the selected persisted capture closure |
| `src/tiaf/forecasting/replay.py` | Separate exact `verify_pinned`; existing `verify_replay` remains recorded-only |
| `tests/unit/forecasting/_runtime_support.py` | Authored synthetic support, captured sources, exact COLD fixtures and test clock |
| `tests/unit/forecasting/test_baserate_runtime.py` | Probability/support, leakage, metadata, startup, clocks, failures, observability and runtime tests |
| `tests/unit/forecasting/test_pinned_runtime_replay.py` | Capture/replay/verification distinction, mismatch/absence, independent truth linkage and fresh-process isolation |
| `tests/fixtures/forecasting/ff0/runtime_cases.json` | Exact 25-session synthetic profile, 21 decimal closes, authored count and fourteen scenario descriptions; test manifest, not corpus |
| `tests/fixtures/forecasting/ff0/README.md` | Distinguish unchanged contract/capture specimens from new executed runtime tests; commands |
| `README.md`, `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_ROADMAP.md`, `docs/MILESTONES.md`, `docs/TIAF_IMPLEMENTATION_TARGETS.md`, `docs/TIAF_CAPABILITY_MAP.md`, `docs/TIAF_A7_DETAILED_ROADMAP.md`, `docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md` | Current status/navigation only: FF-0.3 accepted, internal synthetic runtime implemented, FF-0.4 next |
| This implementation record | Scope, semantics, evidence, coverage, limitations and handoff |

Reuse: `ForecastContract`, native `InstrumentKey`/`OHLCVBar`, exact positive-price
companions, qualified schedules, knowledge/time validators, canonical JSON and
SHA-256 identity, typed singleton composition, FF-0.2 closure/rights/append-safe
store and Evaluation truth/link/Ledger APIs. Static resolver and frozen owner
follow R3/R5 patterns without changing those shared/public owners. No dependency,
dynamic loader, filesystem discovery or provider SDK is added.

## 4. BaseRate, fixed support and probability

The only target is RELIANCE NSE cash:
`equity.next_session_close.return_gt_zero@1.0`. Class 1 means exact completed
unadjusted terminal close is strictly greater than reference close; class 0
means less than or equal. Equality is not missingness.

| Policy | Implemented meaning |
|---|---|
| Window | Last twenty scheduled adjacent-session transitions ending at the artifact's pinned fit cutoff; not a rolling per-request fit |
| Witness | Complete ordered twenty-row window, qualified supplied calendar, endpoint/source/action references, prior-label availability/revision, inclusion/exclusion reasons and counts |
| Eligibility | Both endpoints qualified, final exact positive prices, subject-eligible supplied sessions, unaffected action coverage, label consistent with exact prices, all relevant availability no later than fit cutoff |
| Exclusions | Missing/invalid/unavailable/future-available labels are not counted; no backfill from earlier transitions |
| Minimum | All twenty transitions must be eligible; n=0, 1 or 19 returns UNAVAILABLE / HISTORY_SUPPORT_INSUFFICIENT without a probability |
| Exact minimum | n=20 generates raw k/n; baseline 12/20=0.6 |
| Boundary values | 0/20 serializes numeric 0.0; 20/20 serializes numeric 1.0; neither means scientific certainty |
| Estimate | No smoothing, prior, recency/regime weight, calibration or learned fit |

Artifact counts are strict integers, reject bool/float, satisfy `0 <= k <= n <= 20`
and must exactly agree with the complete witness. Repeated adjacent use of one
close must preserve the same qualified observation. Every qualified endpoint
is checked against its captured canonical bar, even when a bar reference is
reused. The separately captured exact decimal companion remains authoritative
for comparison; a float is not claimed to recover source precision.

The forecaster receives only `AdmittedSupport`: the request fingerprint, pinned
artifact, k/n and eligible historical-label references. It does not receive
excluded future rows, a journal object, unrestricted history, target outcome,
provider or store. Independently validating authored counts is not model fitting.
The payload remains `RAW`, uncertainty `NOT_ESTIMATED`, no interval or utility,
and no BUY/SELL/advisory conversion. The declared synthetic research purpose
does not promote a model or authorize a consumer.

## 5. PIT and clock semantics

Admission checks artifact fit cutoff <= request information cutoff, every
included fit/selection source available **strictly before** request cutoff,
and historical endpoints before the current target open. The accepted <= fit
cutoff rule and the brief's strict request-cutoff rule are both enforced.
Availability of selection/universe, calendar notices and action proof is part
of fit evidence; limiting only price timestamps would be insufficient.

`CAPTURED_AS_KNOWN` also requires actual acquisition/admission by the historical
cutoff. SIMULATED `QUALIFIED_HISTORICAL_AVAILABILITY` may retain later real
acquisition with qualified historical availability; it never rewrites that
acquisition as early. ACTUAL cannot select the historical-only basis.
An excluded late-available prior label may be retained in the captured audit
witness, but never reaches the primitive's admitted support. No current-target
future outcome is queried or included as support.

| Clock / operation | ACTUAL | SIMULATED |
|---|---|---|
| As-of | Supplied valid decision/as-of, not a completion override | Explicit historical `simulation_as_of` derived from request as-of |
| Runtime completion | Real trusted execution clock | Real later trusted execution clock, not historical as-of |
| Issue | Runtime-controlled internal handoff, strictly before target open | None; cannot claim actual historical issue |
| Artifact and binding | Genuinely prepared/bound before use/issue | Explicit prepared/bound times retained, possibly later than as-of |
| Late dispatch/completion/issue | UNAVAILABLE, no issue and no silent conversion to simulation | Historical as-of remains strictly pre-open; later computation is explicit |
| Repeat | Fresh run/result/attempt IDs | Fresh run/result/attempt IDs, same observation identity when scientific window is unchanged |

Production default is `SystemClock` using `datetime.now(TIAF_TIMEZONE)`;
`TIAF_TIMEZONE` is `ZoneInfo("Asia/Kolkata")`. Naive clocks reject and other aware
zones normalize; JSON emits `+05:30`. Monotonic time measures local inference.
The `_clock` and `_new_id` constructor seams are trusted Python test injection,
not caller request fields, environment selectors or public clock overrides.
Historical ACTUAL fixtures demonstrate invariants only. A real-clock run with
their now-past open is explicitly unavailable; a real-clock SIMULATED run really
computes now. No live issuance validation is claimed.

Issuance here is the private `_forecast` → `run` internal handoff before store
commit, not stdout, broker execution or a public publication event. Persistence
failure raises an error and does not claim capture success; it cannot retroactively
make a prior internal handoff or consumed local work disappear.

## 6. Metadata, registry, COLD configuration and identity

`forecaster:historical-base-rate@1.0` is the sole registered primitive. Its frozen
descriptor pins supported target/version, both modes, required PIT count evidence,
determinism, recorded/exact replay capability, no optional dependencies, one
attempt, one-second deadline, code and policy references. Lookup is deterministic
through an immutable `MappingProxyType`; unknown IDs/versions fail explicitly.
No registration API, import string, entry-point scan, fallback to latest or HOT
replacement exists. Descriptor discovery confers no operation authority.

`create_forecast_runtime` requires an explicit validated config, artifact,
captured source shelf, trusted build and absolute corpus root. It resolves the
exact registered descriptor, validates target/artifact/config/code pins and
preparation time, captures the binding and validates complete retained closure
and source-bar correspondence before any inference or write. The owner is frozen
and its semantic collections are tuples. Operational lock/consumed-ID bookkeeping
does not expose mutable scientific configuration. A new profile requires a new
owner; requests cannot replace profile, graph, implementation or artifact.

| Category | Fields / owner |
|---|---|
| Architecture invariant | Target comparator, neutral subject scope, aware clocks, realization meanings, BENCHMARK-only singleton, no trading authority |
| Trusted COLD config | Exact profile ID/version, target, forecaster/version, graph/artifact/descriptor/simulation pins; minimum 20, attempt 1, deadline 1 second, synthetic engineering purpose |
| Artifact identity | Authored k/n/window/qualifications/exclusions, source and fit cutoff, actual preparation, code and BaseRate policy pins |
| Request | Request ID, exact permitted target/window, mode/as-of/cutoff/knowledge basis, captured evidence and permitted profile pins; no hyperparameters or clocks of production |
| Operational location | Explicit local corpus root; excluded from scientific profile/composition fingerprints so moving identical captured science is not a new model |
| Build/dependencies | Explicit trusted build, actual Python patch and Pydantic version and serializer/numeric profile, retained in the binding/capture |

The code reference is a reviewed versioned algorithm declaration, not executable
code or an automatically collected source/binary digest. Build identity is
explicit launcher-supplied provenance, not Git discovery or cryptographic proof
that a trusted local operator ran particular bytes. Fingerprints prove identity,
not authenticity, licensing or deployment history. R5's one-local-operator/OS
permissions trust boundary remains; no multitenant authentication claim.

## 7. Capture, recorded replay and exact pinned verification

Every run captures original request/evidence, graph, config, descriptor, artifact
and support, fit/source/preparation/binding clocks, build/dependencies, mode,
schema/version, output, IDs, actual invocation usage and result/capture fingerprints.
`select_artifacts` traverses only the supplied shelf; it never loads absent refs
from an arbitrary path or network. Missing/conflicting/cyclic closure fails.

`run` invokes FF-0.2 `append_forecast` exactly once and returns only after success.
The original identical-append retry is idempotent; same-ID/different-content
conflicts remain errors. Fresh runtime requests allocate new IDs, and reuse of
an injected consumed ID fails before a second dispatch. Forecast owns forecast
writes only; it cannot append outcomes or mutate Evaluation records.

`verify_replay(store, run_id)` still reconstructs the exact original capture
without registry, primitive, runtime, label resolution, network or mutation.
`get_forecast_artifacts` returns the selected read-validated captured closure,
not arbitrary future Outcome Journal rows.

`verify_pinned(store, run_id)` separately resolves the exact registered version
and captured descriptor/code/policy/config/composition/target/artifact/binding,
checks current dependency-profile availability, revalidates support and invokes
one pure recomputation. It substitutes the new generation payload and support
into the original semantic projection, retaining original IDs/clocks/usage,
and compares the resulting SHA-256. **No historical completion or issue is
re-executed/backdated.** Verification records its new ID, actual timing/usage
and VERIFIED/MISMATCH/UNVERIFIABLE report outside the original capture; it is a
returned typed report, not an append or replacement forecast.

| Condition | Verifier result |
|---|---|
| Exact sufficient-support generation or deterministic insufficient-support absence | VERIFIED if reconstructed semantic fingerprint is identical |
| Resealed changed probability, support or material binding/profile pin | MISMATCH; no corrected capture is written |
| Exact implementation/descriptor/dependency profile unavailable | UNVERIFIABLE; recorded replay still works if capture is intact |
| Legacy FF-0.1/0.2 contract specimen with no executed usage | UNVERIFIABLE, zero attempts; never relabeled as executed |
| Temporal admission absence, historical timeout/runtime failure | UNVERIFIABLE for recomputation; cannot honestly reproduce that original operating accident |
| Current verification call exception/deadline overrun | UNVERIFIABLE with its separate consumed attempt; no fallback/retry |
| Corrupt/missing closure or impossible verification clock | Explicit integrity error; not successful partial verification |

The verifier does not independently authenticate original clocks or billed
resources. Its exact dependency profile is deliberately conservative; another
Python/Pydantic version can remain recorded-replay capable while exact pinned
verification is unavailable. No latest-version substitution.

## 8. Compatibility, truth and failure semantics

Package version is **0.1.0**; contract/schema version is **1.0**. They are separate.
New leaf schemas are `tiaf.ff.baserate-policy`, `tiaf.ff.baserate-artifact`,
`tiaf.ff.forecaster-descriptor`, `tiaf.ff.cold-config`, `tiaf.ff.simulation-profile`,
`tiaf.ff.cold-binding`, `tiaf.ff.invocation-usage`, `tiaf.ff.execution` and
`tiaf.ff.pinned-verification`, all explicit 1.0. Serializer remains
`tiaf.ff.canonical-json/1.0` and the dependency floor is unchanged.

`ForecastResult.inference` is an optional additive extension. When absent, its
serializer omits the key entirely and retains `NOT_RECORDED_CONTRACT_ONLY`; old
1.0 semantic and capture goldens therefore remain byte/identity compatible.
New runtime results explicitly use `RECORDED` and typed inference facts. Current
code reads both projections; pre-FF-0.3 code is not promised to understand the
new additive field. No silent migration or fabricated legacy telemetry occurs.
The name `execution` remains forbidden at the result-field boundary because
existing contracts reserve broker semantics; the new field is `inference`.

Evaluation's pure truth resolver and journal/link/Ledger code is unchanged.
Integration generates one ACTUAL and two fresh SIMULATED runs, appends independent
truth, and links all three to one OutcomeKey/observation without manufacturing
three independent market outcomes. Synthetic eligibility remains
`ENGINEERING_LINK_ELIGIBLE`, never empirical qualification or pooling authority.

| Failure / absence | Disposition |
|---|---|
| Insufficient historical support | UNAVAILABLE / HISTORY_SUPPORT_INSUFFICIENT; one consumed primitive attempt, no probability |
| Missing/stale/partial/ambiguous current proof, unknown/affected action | UNAVAILABLE with existing reason, no primitive attempt |
| Temporal/fit knowledge violation | Admission error before eligible construction or UNAVAILABLE at runtime; never a backdated issue |
| Unsupported scope/target | Contract rejection or UNSUPPORTED / existing reason; no estimate |
| Missing registered version, bad config/descriptor/artifact/profile pin | Typed validation/integrity startup/admission failure, before dispatch |
| Corrupted support/count/bar/closure | Validation/integrity error; no repair, fallback or fabricated result |
| Actual pure-call exception | FAILED / INTERNAL_EXECUTION_FAILURE, safe reason, retained single attempt |
| Local inference > 1 second | FAILED / LOCAL_DEADLINE_EXCEEDED after return; no retry |
| Persistence/rights/lock/size failure | Existing typed store/integrity error; no returned capture success |
| Duplicate consumed execution ID | Integrity error before redispatch; original store idempotence/conflict policy retained |

ABSTAINED remains an accepted contract state but no new BaseRate abstention policy
is invented. FAILED is not trading non-action. GENERATED/RAW is not calibration,
support qualification, consumer admission or permission to trade.

## 9. Bounds, cost, observability and exclusions

One node/root, zero edges, twenty transitions, 64 session/close records per input,
1 MiB per artifact/record, 256 closure items/journal records and 32 MiB corpus
retain native bounded checks. Store limits apply at storage; they are not a
transactional reservation of future disk space before inference. A saturated or
failed store can reject persistence after local work has occurred.
Inference timing brackets the one pure call; the one-second budget is validated
before dispatch and checked after return. This is cooperative detection, not hard
cancellation. File I/O is outside model duration and separately size-bounded.

Provider/model calls, input/output model tokens and external model cost are
strict zero-valued facts. Local CPU/storage is **UNPRICED**, not falsely free;
duration and one attempt are retained once. A requested strict total-currency cap
is denied at startup because local resources are unpriced. No model/provider
budget service or inferred external bill is added.

Structured success logs expose run/request/result/capture identity, neutral
subject, target/version, mode/basis, status/reasons, profile/composition,
forecaster/artifact, support count, duration and replay fingerprint. They do not
dump prices, source bodies, arbitrary metadata, sensitive root paths or exception
payloads. Call-boundary exceptions become safe reason codes. No telemetry service.

Not implemented: FF-0.4 CLI/full acceptance driver; FF-1 Logistic Regression,
learned training, empirical sampling/splits, metrics/calibration; ensembles,
shadow/challenger lifecycle, dynamic discovery/HOT replacement, LLM/FM/LFDE,
public Shell/facade, A8, live acquisition or broker/order/execution operations.
No public capability was added; the catalog remains nine. No production service
level, historical deployment, calibrated forecast or new authority is claimed.

## 10. Tests and planned acceptance-case mapping

`runtime_cases.json` describes fourteen synthetic profiles, not fourteen runnable
corpus records. Builders consume the exact plan's 25 supplied dates and decimal
closes; baseline twenty transitions contain twelve up, seven down and one tie.
Tests add explicit boundary/negative variants. They write temporary corpora only;
original foundation/capture fixtures and their four golden fingerprints are unchanged.

| Planned cases | This pass / cumulative status and evidence |
|---|---|
| 01, 02, 03 | Retained satisfied: immutable contracts, exact target/scope and malformed-field/mode admission; FF-0.1 regressions |
| 04, 05, 06 | Newly satisfied: trusted timely ACTUAL, late dispatch/completion/issue absence, real-clock SIMULATED later computation; runtime clock/failure tests |
| 07 | Newly satisfied: fit/label cutoff, future exclusion, historical-basis late-acquisition checks plus retained feature/selection/action leakage regressions |
| 08, 09, 10 | Retained satisfied: strict open, timezone/distinct clocks, exact supplied calendar/price; FF-0.1 regressions |
| 11, 12 | Newly satisfied: exact 0.6/0/1, equal close, deterministic output, complete witness, strict counts, n=0/1/19/20 absence/boundary tests |
| 13, 14 | Newly satisfied: current stale/partial/ambiguous/action absence without dispatch; RAW generated vs absent/failed states; unchanged ABSTAINED contract |
| 15 | Retained satisfied: typed finite BENCHMARK singleton; old graph negatives plus new frozen startup |
| 16 | Newly satisfied: exact immutable registry, startup pins, artifact absence, unknown versions, no request mutation/import paths |
| 17 | Retained satisfied: append idempotence/conflicts; runtime adds fresh IDs and consumed-ID redispatch denial |
| 18 | Newly satisfied: new ACTUAL/two simulations coexist and share independent truth, preserving separate run identities |
| 19, 20, 21, 22, 23 | Retained satisfied: independent exact truth/missingness/revisions/link/Ledger/recorded replay; new generated-run integration and execution-blocked replay added |
| 24 | Newly satisfied: exact separate verification, original fingerprints/clocks retained, resealed mismatch and unavailable implementation, no mutation |
| 25 | Retained satisfied: corrupt/partial/locked store denial; runtime persistence failure regression added |
| 26 | PARTIAL through FF-0.4: new fresh-process recorded replay blocks inference/ML/provider/MCP imports and network; unchanged nine-capability catalog and A6 regressions pass; CLI boundary recheck still pending |
| 27 | PARTIAL through FF-0.4: strict usage/budget, one attempt, deadline, safe structured logs and existing store bounds exercised; final CLI-level bounds/cost/failure acceptance still pending |
| 28 | PENDING: separately authorized FF-0.4 engineering CLI/end-to-end acceptance |

**Newly satisfied: 11** (04, 05, 06, 07, 11, 12, 13, 14, 16, 18, 24).
**Cumulative: 25 satisfied, 2 partial, 1 pending**, versus 14/10/4 at FF-0.2.
These are semantic case dispositions, not pytest item counts. They do not claim
the final 28-case CLI corpus or overall FF-0 acceptance.

## 11. Validation

| Check | Result |
|---|---|
| FF-0.3 targeted: `test_baserate_runtime.py`, `test_pinned_runtime_replay.py` | PASS: 75 tests |
| FF-0.1: `test_contracts.py`, `test_clocks_evidence.py`, `test_identity_isolation.py`, `test_population_contract.py` | PASS: 170 tests |
| FF-0.2: `test_capture_store_replay.py`, `test_forecast_truth.py`, `test_forecast_linkage.py` | PASS: 113 tests; original goldens unchanged |
| Related R3/R5/provenance/Evaluation/A6 set | PASS: 289 tests; overlapping regression groups are not added together |
| Full `.venv/bin/pytest -q` | PASS: 2,835 tests in 275.84 seconds |
| `.venv/bin/python -m compileall src scripts` | PASS |
| `.venv/bin/ruff check src tests scripts` | PASS |
| `.venv/bin/mypy src tests` | PASS: 594 source files |
| Fresh-process import/authority isolation | PASS in targeted and retained suites; no new public capability |
| Local documentation links/status consistency | PASS: 12 Markdown files, 621 local links; eight current-navigation docs point to FF-0.4, historical records retain their original status |
| `git diff --check`, scoped-file/protected-baseline inspection | PASS: only the 25 files in §3; no A6, public facade/catalog, original foundation/capture manifest, architecture/plan/thesis or dependency changes |
| Live provider/model/broker calls | 0; no network acquisition or credentials read |

Related command:

```bash
.venv/bin/pytest -q \
  tests/unit/workflows/test_r3_composition.py \
  tests/unit/test_r5_cold_startup.py \
  tests/unit/source_semantics tests/unit/evaluation tests/unit/a6
```

No architecture deviation: BENCHMARK rather than conceptual PRIMARY and
primitive payload/runtime-owned result are explicit applications of the accepted
plan. Narrow boundary fixes found during development were covered by regressions:
legacy field-name compatibility, repeated-bar-reference validation and strict
verification report/payload validation. No policy was tuned to market examples.

## 12. Handoff and requested report index

| Requested report items | Recorded evidence |
|---|---|
| 1 decision; 2 files; 3 reused patterns | §§1–3 |
| 4 BaseRate; 5 support window; 6 minimum; 7 PIT; 8 probability | §§4–5 |
| 9 interface; 10 metadata; 11 registry; 12 COLD owner; 13 composition; 14 fingerprints | §§2, 6 |
| 15 pinned verification; 16 ACTUAL; 17 SIMULATED; 18 runtime flow | §§2, 5, 7 |
| 19 persistence; 20 replay; 21 truth linkage; 22 statuses; 23 failures | §§7–8 |
| 24 config classification; 25 trust; 26 observability | §§6, 9 |
| 27 fixtures; 28 tests; 29 new cases; 30 cumulative; 31 excluded scope | §§9–10 |
| 32 targeted; 33 FF-0.1; 34 FF-0.2; 35 full; 36 validation | §11 |
| 37 deviations; 38 blockers | No architecture deviation; no FF-0.3 acceptance blocker. FF-0.4 and empirical/public gates remain explicitly pending |
| 39 next sub-milestone; 40 Git; 41 exact next prompt | Below |

Next, only after a separate request:
**TIAF A7 / FF-0.4 — ENGINEERING CLI AND ACCEPTANCE HARDENING**.
This is the plan's **FF-0.4 — Engineering CLI and acceptance hardening**, not
FF-1, public publication or overall A7 closure.

Suggested future commit:
`feat(a7.ff0.3): implement baserate cold runtime and pinned verification`.
No tag recommended. No commit, tag or push performed.
