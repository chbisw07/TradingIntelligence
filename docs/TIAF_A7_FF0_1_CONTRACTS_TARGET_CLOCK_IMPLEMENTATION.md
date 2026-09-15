# TIAF A7 / FF-0.1 — Contracts, Target and Clock Foundation

## 1. Decision and scope

**2026-09-15, Asia/Kolkata — FF0_1_ACCEPTED.** The bounded foundation passes
the targeted, full-suite, static, import-isolation and documentation checks in
§10. There is no residual blocker to this step; FF-0 overall is not accepted.

This implements only step 1 of the
[accepted four-step FF-0 plan](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md#18-four-bounded-ff-0-implementation-sub-milestones).
It does not accept FF-0 overall, run a forecaster or qualify any empirical result.
Entry worktree was clean at `fbd6725d905a01615ff100525f3d99e08584879d`
(`docs(a7): define FF-0 miniature implementation plan`). Frozen A6 remains
`tiaf-a6-baseline` → `6dc2ff304aae0e87540260b092919bb91e4d4189`.

The authorized implementation consists of immutable contracts, a single target,
synthetic session/price specimens, clock and supplied-evidence checks, and
deterministic serialization/identity. Forecast **execution** remains
NOT_IMPLEMENTED; A7 / FF foundation implementation has started.

## 2. Architecture clauses and repository reuse

Source review covered the accepted plan, A7 and FF architectures, A7 acceptance,
FF roadmap/decision/clock correction/repeat acceptance, Source/Provenance,
R1–R5, common/data contracts, baseline/capture digests and package/test conventions.
Neither architecture nor any thesis or original acceptance record is rewritten.

| Governing source | Implemented foundation |
|---|---|
| Plan §§4–5; A7 §§3/3.1/5.1 | One exact target, captured schedule adjacency, exact-price companion, explicit missing/partial/stale/action qualification |
| Plan §§7–9; A7 §§4/5.2; FF §§3–3.3 | Frozen schemas, both native modes, supplied-clock ordering, five result states, raw/research-only output |
| Plan §7/18; FF §§4–6 | Typed singleton composition with one primitive, zero edges and one BENCHMARK root; no executor |
| Plan §12; A7 §14; FF §18 | Lossless canonical projection, material identity and defensive reconstruction; not persisted replay |
| Plan §7/18; A7 §9.1 | Evaluation-owned population disposition/count invariants; no metric/report emission |
| Plan §§14–16; R1–R5 | Lean imports, explicit absence, no request-selected loader or public capability |

Reused patterns:

- [Common contracts](../src/tiaf/contracts/common.py): frozen/extra-forbidden
  Pydantic models and `TiafDateTime`/`TIAF_TIMEZONE`, which uses
  `zoneinfo.ZoneInfo("Asia/Kolkata")`.
- [Data models](../src/tiaf/data/models.py): provider-neutral `InstrumentKey`
  and canonical `OHLCVBar`; no second symbol or candle implementation.
- [Source semantics](../src/tiaf/source_semantics/contracts.py): validated
  `QualifiedId` syntax. Logical artifact references add path/URL rejection.
- [Planner digests](../src/tiaf/planner/digests.py): the existing canonical-JSON
  SHA-256 primitive; [planner types](../src/tiaf/planner/models.py) supply `Sha256`.
  The timing-stripping `semantic` helper is deliberately not used: FF clocks
  are material scientific identity.

No existing calendar utility certified this target's ordered, complete,
versioned schedule coverage. The small synthetic `SessionRecord`/schedule
companion is the plan's explicit solution, not a new calendar service. Likewise
an existing float OHLCV close alone cannot establish exact source-decimal precision.

## 3. Exact files and contract inventory

Seven new runtime-package files; **no pre-existing runtime file modified**:

| File | Contents / ownership |
|---|---|
| [forecasting/__init__.py](../src/tiaf/forecasting/__init__.py) | Lean package marker, no eager integrations |
| [forecasting/enums.py](../src/tiaf/forecasting/enums.py) | Realization, status, reason, data/knowledge basis, qualification and population enums |
| [forecasting/identity.py](../src/tiaf/forecasting/identity.py) | `ForecastContract`, `ArtifactReference`, logical ID/time/exact-decimal validation and canonical digest projection |
| [forecasting/errors.py](../src/tiaf/forecasting/errors.py) | `ForecastAdmissionError` carrying a sanitized typed reason; no premature store errors |
| [forecasting/contracts.py](../src/tiaf/forecasting/contracts.py) | `ForecastRequest`, `ForecastArtifactIdentity`, `ForecastComposition` plus node/edge/root, `ForecastResult`, `BinaryProbabilityOutput`, `ForecastAbsence` |
| [forecasting/evidence.py](../src/tiaf/forecasting/evidence.py) | Pure knowledge/required-evidence/companion-bar validation; no acquisition |
| [evaluation/forecast_contracts.py](../src/tiaf/evaluation/forecast_contracts.py) | Evaluation-owned `ForecastTargetSpec`, `EvidenceReference`, `SessionRecord`, `QualifiedSessionSchedule`, `QualifiedCloseObservation`, `ForecastWindow`, `EvaluationPopulationDispositionReport` and its observation/disposition/count records |

One small new package (`forecasting`), one additive Evaluation module. There is
no competing public A7 forecast envelope, target-definition duplicate, registry,
calendar package or service. `ForecastWindow` and the derived observation ID
carry target-observation identity without another redundant wrapper class.

New test/fixture files:

- [tests/unit/forecasting/__init__.py](../tests/unit/forecasting/__init__.py)
- [tests/unit/forecasting/_support.py](../tests/unit/forecasting/_support.py)
- [test_contracts.py](../tests/unit/forecasting/test_contracts.py)
- [test_clocks_evidence.py](../tests/unit/forecasting/test_clocks_evidence.py)
- [test_identity_isolation.py](../tests/unit/forecasting/test_identity_isolation.py)
- [test_population_contract.py](../tests/unit/forecasting/test_population_contract.py)
- [foundation_cases.json](../tests/fixtures/forecasting/ff0/foundation_cases.json)
- [fixture README](../tests/fixtures/forecasting/ff0/README.md)

Documentation: this new record, and status/next-step updates only in
[README](../README.md), [Milestones](MILESTONES.md),
[forward roadmap](IMPLEMENTATION_ROADMAP.md),
[engineering targets](TIAF_IMPLEMENTATION_TARGETS.md),
[architecture navigation](ARCHITECTURE.md),
[capability map](TIAF_CAPABILITY_MAP.md),
[A7 detailed roadmap](TIAF_A7_DETAILED_ROADMAP.md) and
[FF detailed roadmap](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md).
The original planning/acceptance documents retain their historical then-next
instructions; these current navigation documents and this record supersede them.

## 4. Target, price and session identity

| Dimension | Sole supported v1 meaning |
|---|---|
| Target ID/version | `equity.next_session_close.return_gt_zero` / `1.0` |
| Subject | `RELIANCE`, `NSE`, `NSE_EQUITY`, `EQUITY`; no provider ticker/ID, derivative fields, index or other subject |
| Event | `P(S1 completed close > S0 known completed close)`; strict endpoint comparator, not path/fill/total-return profit |
| Basis / unit | Positive finite exact source-decimal unadjusted closes, INR; dimensionless price return |
| Tie | `CLASS_ZERO`; equal is non-up, never dropped or labeled missing |
| Missing outcome | `PENDING_THEN_CENSORED_NO_LABEL` under a pinned maturation policy |
| Invalid outcome | `INELIGIBLE_NO_LABEL`; no invented zero price or label |
| Corporate action | `EXCLUDE_AFFECTED_OR_UNKNOWN`; no hidden adjustment |
| Reference session | S0's completed close at its declared close time, observed/available by cutoff |
| Target session | The immediately following supplied session S1; exact open/close match the window |
| Calendar | Version/hash, coverage, complete ordered sessions, source/exception references, eligibility, qualification and revision/predecessor |
| Outcome deadline | Explicit aware `outcome_due_at >= target_resolve_time`, with maturation-policy identity |

Missing facts can be represented with qualification/reasons, but do not qualify
a GENERATED estimate. Partial or stale calendar, missing/stale/ambiguous close,
unknown/affected action coverage and ineligible subject fail pure qualification.
Impossible session identities fail construction: unknown S1, S2 substitution,
duplicate/overlapping sessions, mismatched close/window or invalid revisions.

The pure companion-bar check verifies neutral subject, daily interval, end time,
numeric correspondence and the supplied bar fingerprint. It does **not** infer
source precision from a float, authenticate a provider or prove action coverage.
No actual endpoint label or BaseRate probability is calculated in this step.

Schema version `1.0`, target version `1.0`, artifact version and canonical
serializer profile `tiaf.ff.canonical-json/1.0` are separate pins. Existing
package version **`0.1.0`** and A0 contract schema version **`1.0`** are unchanged.
Unknown target/schema versions reject; a different version is a material
fingerprint change, not automatic compatibility or migration.

## 5. Requests, results and clocks

`ForecastRequest` carries its ID, complete target/window identity, mode,
information cutoff, as-of, evidence refs/knowledge basis, profile/config refs and
SIMULATED-only simulation-profile ref. Subject/horizon are nested, not separately
editable duplicates. Requests cannot supply future completion/issuance metadata.
`simulation_as_of` is a read-only semantic view of `as_of`, not a second JSON field.

`ForecastResult` carries caller-supplied result/run IDs, the immutable request,
singleton graph, artifact/binding identity, status, probability **or** absence,
production/issuance clocks, limitations, contradictions and sealed fingerprint.
Its nested artifact identity is declarative: exact version/code/config refs,
fit-knowledge cutoff, actual preparation time and supplied fit-evidence refs.
It contains no model bytes, fitted parameters, counts, loaders or authority grant.

```text
Generated ACTUAL_ISSUANCE
S0 close <= information_cutoff <= as_of <= computed_at <= issued_at
                                                        < S1 open < S1 close

Generated SIMULATED_ISSUANCE
S0 close <= information_cutoff <= as_of (= simulation_as_of) < S1 open < S1 close
                                └─ <= computed_at (may be much later)
issued_at = None; simulation profile required
```

The accepted strict **before-open** boundary is retained; equality is not
repaired by shifting a timestamp. Completion equal to actual issuance is valid.
ACTUAL issuance before completion, completion before as-of, artifact preparation
after computation, binding availability after use and future fit knowledge fail.
SIMULATED forbids issuance even when computed much later. Fit knowledge must
remain `<= fit_knowledge_cutoff <= information_cutoff` in both modes.

All datetimes stay timezone-aware. UTC/other aware zones normalize to canonical
Asia/Kolkata and serialize with `+05:30`; naive and numeric epoch inputs reject.
Validation never reads `datetime.now()`, sleeps, normalizes a bad ordering,
backdates a timestamp or changes a realization mode.

**Trust limit:** contracts can reject inconsistent supplied clocks; they cannot
prove that an author supplied a real wall-clock time or genuinely deployed a
binding. These synthetic artifacts do not prove historical ACTUAL deployment.
The accepted plan assigns trusted clock capture and existence/admission checks
to the FF-0.3 runtime. Requests deliberately have no issuance override seam.

An honest late attempt can be represented as UNAVAILABLE/TEMPORAL_INELIGIBLE,
with its actual completion and no issuance. A never-executed absence may carry
`computed_at=None`; this is not a generated forecast or a fabricated execution.
Producing these attempt results automatically belongs to the future runtime.

| Generation state | Contract meaning |
|---|---|
| GENERATED | Finite binary probability in [0,1], RAW, uncertainty NOT_ESTIMATED with reason, validity UNKNOWN with reason |
| ABSTAINED | Explicit policy absence, not a newly implemented BaseRate abstention heuristic |
| UNSUPPORTED | Scope or unresolved-session absence |
| UNAVAILABLE | Typed evidence/qualification/temporal/artifact absence |
| FAILED | Execution-failure envelope seam, not an implementation that catches programmer defects |

Status/reason/output mismatches reject. All result shapes assert RESEARCH_ONLY
and NO_ACTION_AUTHORITY. Usage is explicitly NOT_RECORDED_CONTRACT_ONLY, not
made-up zero-duration/cost/token accounting. Pydantic structural errors and pure
`ForecastAdmissionError` remain distinct from future runtime FAILED results.

## 6. Provenance, knowledge and trust boundary

`EvidenceReference` preserves artifact/version/hash, origin, source, document
version, optional neutral adapter ID and observed/publication/availability/
acquisition/admission clocks. These are references to captured provenance,
not an alternative source authority or an authenticated capture store.

ACTUAL admits only CAPTURED_AS_KNOWN: acquisition/admission are not later than
cutoff. SIMULATED may explicitly use QUALIFIED_HISTORICAL_AVAILABILITY, retaining
later real acquisition/preparation/computation while availability stays inside
historical cutoffs. It cannot relabel that history as captured-as-known. Future
effective schedule dates known beforehand are allowed; future observed prices
are not made known by an early acquisition assertion. Conflicting same-ID
evidence versions reject.

FF-0.1 requests enable only SYNTHETIC_ENGINEERING/SYNTHETIC_FIXTURE. A source
reference can represent a QUALIFIED_CAPTURE identity, but the current request
qualifier rejects empirical use as EMPIRICAL_PROFILE_NOT_ENABLED. References
are not proof of complete input closure, source authenticity, rights or approval;
FF-0.2 captures the closure and later qualified-data protocols establish those
claims. No fixture download or real market/session certification is claimed.

Paths, URLs, arbitrary import/model fields, unknown target/subject, empirical
profile and extra broker/execution fields fail closed. Contract validation
performs no filesystem, network, provider, broker or subprocess I/O. Frozen
semantic collections are tuples, accept normal Python/JSON lists and dump to
JSON arrays. Reconstruction revalidates nested contracts, including instances
forged with the explicitly unsafe Pydantic `model_copy(update=...)` bypass.

## 7. Fingerprint and replay foundation

The existing SHA-256 digest receives a lossless FF canonical projection:
sorted string-key JSON objects, compact separators, escaped non-ASCII, arrays,
canonical aware IST timestamps and exact normalized decimal **strings**.
NaN/infinity/non-string keys reject; decimal formatting does not depend on
ambient Decimal precision. Ordering of mappings and unordered request evidence
does not affect identity. Ordered schedules/graph declarations retain order.

Request/result IDs, target/version/subject, mode, evidence/profiles, fit/code/
artifact/binding identity and original scientific clocks are material. Process
environment, current clock, duration samples and filesystem paths are not read.
The result hash excludes only its own fingerprint field; a supplied mismatched
hash rejects. Common observation identity binds target/window/cutoff/as-of but
excludes producer, request/run ID and mode: repeated runs are not extra truth.

| Authored synthetic specimen | Pinned result semantic fingerprint |
|---|---|
| ACTUAL | `0130acc66a1defbaa16fd20afda61fde6666dccc7d52ce0a2f1df918a2a52dfc` |
| SIMULATED | `a595b8eb9adab3b1620a5ffbe8be34c31c677d24f7916cd5498ee052f9878eb4` |

JSON serialization/reconstruction preserves exact canonical semantics and
fingerprints without external calls. This is **not** the FF-0.2 persisted
recorded-replay engine, FF-0.3 pinned verification, or a new simulation run.

The population-report contract separately verifies request-versus-observation
counting, explicit unmapped requests, unique observations, one disposition per
observation/metric/arm, matching denominator partitions, source facets and honest
incompleteness. Its fixtures test shape only: no Brier/paired metric or report
generation, Ledger or journal is implemented.

## 8. Synthetic fixtures and tests

All values and clocks are authored deterministic specimens, not imported market
history. S20/S21/S22 use explicit February 2026 windows; no claim that these are
qualified NSE calendar records. The test probability 0.6 is authored, not a
computed 12/20 BaseRate. Boundary probabilities 0 and 1 are valid factual output
shapes; no history is converted to 0.5.

The seven-case fixture manifest covers valid ACTUAL, backdated ACTUAL,
exact-open rejection, later-computed SIMULATED, fake simulated issue, simulated
cutoff leakage and equal-close policy. It is **not a runnable capture corpus**.
The four test modules add parametrized scope, reconstruction, evidence, precision,
fingerprint, no-I/O, import isolation and population-partition checks.

## 9. Mapping to the 28 planned semantic cases

PASS below is limited to implemented contract/pure-validation assertions.
It never closes an entire later runtime/store acceptance case prematurely.

| Planned cases | FF-0.1 evidence / remaining obligation |
|---|---|
| FF0-01–03 | PASS: frozen/tuple/JSON/finite/version, target/subject and mode/field scope |
| FF0-04 | PASS supplied ACTUAL clock/artifact identity; trusted production/existence proof remains FF-0.3 |
| FF0-05 | Added foundation regression: backdated GENERATED rejects, honest late absent shape allowed; producing that result remains FF-0.3 |
| FF0-06–07 | PASS supplied SIMULATED/fit/knowledge checks; complete captured inputs and runtime provenance remain FF-0.2/0.3 |
| FF0-08–10 | PASS strict-open, timezone, distinct clocks, supplied adjacency/qualified exact-price guards; empirical source certification remains unavailable |
| FF0-11–12 | BaseRate/count witness/support calculation pending FF-0.3; only finite output 0/1 shapes tested now |
| FF0-13–15 | PASS pure qualification/absence/five-state/singleton graph contracts; runtime emission/dispatch remains FF-0.3 |
| FF0-16 | COLD registry, permitted profile resolution and exact startup binding pending FF-0.3; no path/import selection accepted now |
| FF0-17 | Append/idempotence/conflict persistence pending FF-0.2 |
| FF0-18 | Mode-sensitive result hashes and common observation identity tested; fresh run allocation and persisted coexistence pending FF-0.2/0.3 |
| FF0-19–21 | Target tie/missing/deadline/revision shapes tested; actual truth resolution, maturation and journal revisions pending FF-0.2 |
| FF0-22 | Population partition schema tested; exact Evaluation Link/Ledger pending FF-0.2, real population report emission FF-1 |
| FF0-23 | Canonical reconstruction/no-I/O tested; full persisted recorded replay pending FF-0.2 |
| FF0-24–25 | Pinned verifier pending FF-0.3; corrupted/partial/locked store checks FF-0.2 |
| FF0-26 | PASS foundation optional-import/no-I/O/authority and unchanged nine-operation catalog checks; later integration rechecked through FF-0.4 |
| FF0-27 | No validation I/O and no secret/config discovery; actual runtime bounds/usage accounting/private logs pending FF-0.3/0.4 |
| FF0-28 | Engineering CLI/end-to-end acceptance pending FF-0.4 |

## 10. Validation and acceptance

Commands use the existing `.venv/bin` environment; no packages downloaded.

| Gate | Result |
|---|---|
| `.venv/bin/pytest -q tests/unit/forecasting` | 170 passed |
| `.venv/bin/pytest -q tests/unit/forecasting tests/unit/contracts tests/unit/source_semantics tests/unit/a6 tests/unit/test_r5_cold_startup.py` | 395 passed |
| `.venv/bin/pytest -q tests/unit/forecasting tests/unit/evaluation tests/unit/contracts tests/unit/source_semantics tests/unit/a6 tests/unit/test_r5_cold_startup.py` | Final expanded regression: 422 passed |
| `.venv/bin/pytest -q` | Final run: **2,647 passed in 292.01 seconds** |
| `.venv/bin/python -m compileall -q src scripts` | PASS |
| `.venv/bin/ruff check src tests scripts` | PASS |
| `.venv/bin/mypy src tests` | PASS: 576 source files |
| Fresh-process optional SDK/provider isolation | PASS within targeted tests; nine existing capabilities unchanged |
| Explicit golden/no-validation-I/O/fresh-import rerun | 3 passed, 26 deselected; already included in the 170 tests, not additional coverage counts |
| JSON-schema generation | PASS: all 21 new contract classes |
| Existing handbook `validate_links(True)` on changed Markdown | PASS: 12 Markdown files / 624 local links |
| Current navigation/status and protected-scope check | PASS: eight current navigation documents point to FF-0.2; no pre-existing code, accepted architecture/thesis/A6/deferral/plan changes |
| `git diff --check` | PASS; untracked new files also checked with `git diff --no-index --check` |

The first full run was **2,646 passed / 1 failed**. The pre-existing Evaluation
guard scans source text for `requests` and matched a new local identifier, not
an HTTP import. Renaming it to `request_keys` (and its mapping-validator name)
resolved that compatibility issue without weakening the guard or changing
contract fields, fingerprints or semantics. The final expanded 422-test run
includes that exact guard. Two initial test-only typing/lint issues were also
corrected before these final checks.

**Acceptance: FF0_1_ACCEPTED.** No in-scope test failure or implementation
blocker remains. Historical-source certification, trusted execution clocks,
complete input closure and persisted replay are explicitly pending at their
planned stages; a green synthetic foundation does not establish those claims.

No live provider/market/broker call, model fit, model/LLM inference, terminal
outcome inspection or `.env` discovery was performed for FF-0.1. Existing test
suites use their test fixtures/mocks; no live-acceptance script was invoked.

## 11. Limitations, deviations and explicit exclusions

No architecture-semantic deviation. Native enum names ACTUAL_ISSUANCE /
SIMULATED_ISSUANCE and the accepted five states override illustrative names in
the brief. The strict pre-open rule is the accepted rule, not a new tightening.
The small `identity.py` addition isolates the existing digest projection needed
now without introducing a premature persistence module. Full capture/run/usage,
simulation-policy resolution, descriptor/registry and executable-artifact shapes
are deliberately left to their planned consumers in FF-0.2/0.3.

No persistence, Forecast Ledger/Outcome Journal, Ground Truth resolver, BaseRate
calculation, fit, metric emission, paired evaluation, calibration, lifecycle,
registry, runtime clock source, bound executor, verifier, engineering CLI, public
Shell/facade operation, Logistic/XGBoost/LLM/FM-LFDE, A6 overlay or A8 is added.
No source/authenticity/rights claim follows merely from a hash or test count.

The next step must not mistake synthetic ACTUAL-shaped objects for historical
deployment, a logical binding reference for approval, a reconstructable result
for a durable capture, or constant output examples for a forecaster. The fixture
manifest will not be silently repurposed as the completed 28-case corpus.

## 12. Next authorized checkpoint and report index

After bounded acceptance, a reviewed sub-milestone commit is appropriate:

`feat(a7.ff0.1): implement forecasting contracts target and clock foundation`

No commit, tag or push is performed in this pass. No A7/FF tag is recommended
for this partial foundation. A separate request is required for the next step:

**TIAF A7 / FF-0.2 — CAPTURE STORE, TRUTH AND RECORDED REPLAY**

This is exactly the plan's next sub-milestone, not BaseRate/runtime execution.

| Requested final-report items | Location |
|---|---|
| 1 decision; 28 deviations; 29 blockers | §§1/10/11 |
| 2 files; 3 reuse; 4 inventory; 19 layout | §§2–3 |
| 5 target; 6 version; 7 tie; 8 sessions | §4 |
| 9 request; 10 result; 11 statuses; 12 ACTUAL; 13 SIMULATED; 14 backdating; 15 ordering | §5 |
| 16 fingerprint/replay; 17 provenance; 18 trust | §§6–7 |
| 20 fixtures; 21 tests; 22 satisfied / 23 pending cases | §§8–9 |
| 24 excluded scope | §11 |
| 25 targeted; 26 full suite; 27 validations | §10 |
| 30 next sub-milestone; 31 Git recommendation; 32 exact next title | §12 |
