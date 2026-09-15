# TIAF A7 — Implementation Sequencing and FF-0 Miniature Realization Plan

## 1. Decision, status and authority

**READY_FOR_FF0_IMPLEMENTATION** — planning readiness only.

Prepared **2026-09-15, Asia/Kolkata**. A7 and FF architecture remain ACCEPTED;
A7 / FF implementation is **NOT_STARTED**, runtime **NOT_IMPLEMENTED**. A6
remains FROZEN at `tiaf-a6-baseline`; A8 has not started. This document adds no
runtime, fixture, model, public capability or scientific qualification.

**READY_FOR_FF0_IMPLEMENTATION does not authorize implementation beyond FF-0.**
Coding requires a separate bounded request, following §18. An architecture
blocker discovered during implementation must be escalated, not silently fixed
by widening scope. Calibration/lifecycle completion remains at FF-2.

Repository entry was clean. HEAD already contains the architecture checkpoint:

```text
3aceb27c09c549036b1a179d07b37a4408618b39
docs(a7): accept FF-integrated forecasting evaluation and learning architecture

tiaf-a6-baseline^{}:
6dc2ff304aae0e87540260b092919bb91e4d4189
```

Source precedence: accepted [A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md)
and [FF architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md) govern meaning;
the [A7 roadmap](TIAF_A7_DETAILED_ROADMAP.md) and
[FF roadmap](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) govern stages;
[A7 acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) governs the architecture
decision. This plan chooses bounded implementation details within them. Below,
**A §n** and **F §n** refer to those architecture documents. The thesis editions
and historical reviews are retained, not rewritten as implementation evidence.

## 2. Exact FF-0 boundary and stage allocation

Choose one captured-input, local, inspectable **HistoricalBaseRateForecaster**
for one exact next-session equity event and one neutral symbol, RELIANCE.
FF-0 proves contracts, clock admission, a singleton typed composition, raw
generation, immutable capture, independent truth linkage and offline replay.
The shipped fixture profile is explicitly **synthetic engineering evidence**;
it does not establish empirical performance, calibration or live readiness.

| Capability | Delivery boundary |
|---|---|
| Target/schedule/price qualification, request/result/artifact/run contracts, two realization modes | FF-0 mandatory |
| Typed finite composition, one registered primitive and one BENCHMARK root; zero PRIMARY roots | FF-0 mandatory; no general DAG executor yet |
| Declarative pinned BaseRate count artifact, no request-time fit | FF-0 mandatory |
| Captured inputs, append-only forecast history and Outcome Journal, validated Evaluation Link and minimal joined Ledger snapshot | FF-0 mandatory |
| Recorded replay and exact pinned BaseRate verification, local engineering CLI | FF-0 mandatory |
| Population-disposition contract | FF-0 definition; actual population report emission in FF-1 |
| Qualified empirical datasets, count-artifact preparation, logistic training, chronological splits, paired comparisons and metrics | FF-1 deferred |
| Held-out sigmoid calibration, independent qualification/health, complete lifecycle/role history, reviewed prospective shadow and promotion gates | FF-2 deferred; complete miniature here |
| Public facade/Shell forecasting capability and consumer projection | Separately accepted publication checkpoint after FF-2; not required by FF-0 |
| Conventional challengers/ensembles, optional LLM, optional FM/LFDE | Optional FF-3/4/5 respectively |
| Expanded governed correction and advanced routing | Optional FF-6 / conditional FF-7 |

Non-goals: no training job, empirical fitting, statistical scorecard, optimization,
calibration, hidden feature calculation, live/provider/model call, market-calendar
engine, corporate-action adjustment, distributed persistence, scheduler, web
service, model download, arbitrary plugin loader, HOT replacement, A4/A5/A6
influence, A8 integration, broker/order access or trade-profit probability.
No scikit-learn, XGBoost, LLM or FM dependency enters FF-0.

FF-0 is a complete **mechanical path**, not the accepted scientifically qualified
calibrated miniature. A raw estimate remains `RAW`, `RESEARCH_ONLY`, uncertainty
`NOT_ESTIMATED`, and `NO_ACTION_AUTHORITY`. Twenty synthetic labels cannot prove
an empirical minimum sample size or justify production thresholds.

## 3. Repository inspection and reuse decisions

These are inspected existing paths, not assumed future APIs. Proposed files in
§14 do not yet exist. No runtime source is changed by this plan.

| Existing pattern | Finding and FF-0 decision |
|---|---|
| [Common contracts](../src/tiaf/contracts/common.py), [project configuration](../pyproject.toml) | Reuse frozen extra-forbidden Pydantic contracts, `TiafDateTime`, canonical `Symbol`; package 0.1.0 and A0 schema 1.0 stay unchanged; core depends on Pydantic, not ML |
| [Data models](../src/tiaf/data/models.py), [enums](../src/tiaf/data/enums.py) | Reuse `InstrumentKey`, `HistoricalSeries`, `OHLCVBar`; neutral `NSE_EQUITY` / `EQUITY`. Daily bars have floating prices and series observation time, not all exact-price/PIT/source-qualification proof |
| [AnalysisContext](../src/tiaf/context/models.py) | Its `history` and evidence descriptors can supply captured canonical history; context coherence is not historical source qualification |
| [Data coordinator](../src/tiaf/data/runtime/coordinator.py) | Existing acquisition/cache remains outside FF; FF never calls get-or-fetch or creates a parallel data subsystem |
| [A6 contracts](../src/tiaf/trade_expression/contracts.py) | `SessionWindow` proves a positive window and carries a qualification reference, not complete adjacent-session history. Do not alias it as the A7 schedule or modify frozen A6 |
| [Source contracts](../src/tiaf/source_semantics/contracts.py), [source replay](../src/tiaf/source_semantics/replay.py) | Preserve origin/provider/document-version/occurrence and publication/availability/acquisition distinctions; capture the small required qualified facts and referenced bytes, not a whole unrelated specialist projection |
| [A2 replay store](../src/tiaf/evaluation/store.py) | Existing JSON snapshots plus JSONL decision/outcome records are a good local pattern. Its keys and duplicate rules are A2-specific; add a narrow FF store, do not alter/subclass A2 persistence |
| [A2 serialization](../src/tiaf/evaluation/snapshot.py), [planner digests](../src/tiaf/planner/digests.py) | Domain-specific semantic projections remove selected metadata/timings. They are not a generic FF digest: FF must retain original realization clocks and usage |
| [Bootstrap contracts](../src/tiaf/bootstrap/contracts.py), [catalog](../src/tiaf/bootstrap/catalog.py), [runtime owner](../src/tiaf/bootstrap/runtime.py) | Reuse the trusted explicit COLD-config philosophy and code-owned IDs. Existing owner/profile supports accepted workloads, not FF. No new FF field is slipped into its frozen schema |
| [Facade artifacts](../src/tiaf/facade/artifacts.py), [capabilities](../src/tiaf/facade/capabilities.py), [Shell parser](../src/tiaf/shell/parser.py) | Existing artifact kinds and nine operations are bounded and caller-governed; the artifact store is not a durable FF corpus. Do not publish `forecast.assess` or broaden the parser in FF-0 |
| [Feature models](../src/tiaf/features/models.py), [returns](../src/tiaf/features/returns.py) | FF-1 can consume pinned A2 `FeatureResult` values, including `return.log`, without recalculating them inside a forecaster |
| [Evaluation tests](../tests/unit/evaluation/test_regression_store_architecture.py), [A6 acceptance corpus](../tests/acceptance/a6/test_a6_acceptance_corpus.py) | Follow unit/integration tests plus a checked-in named manifest and semantic goldens; do not repurpose the A2 golden manifest as a replay corpus |

No inspected artifact certifies a complete historical calendar, action-coverage
history and exact-price/PIT source chain for a real FF-0 cohort. That limits
empirical qualification, not synthetic mechanics. No new data source is procured
or certified here; DEF-007, DEF-013 and DEF-049 remain open.

## 4. First target, universe and session semantics

Target: `equity.next_session_close.return_gt_zero`, version `1.0`.
Its event is **P(S1 completed close > S0 known completed close)**, using positive,
finite, exact decimal **unadjusted** prices in the same declared unit and basis.
Equality is class 0; missing/invalid/ambiguous price is no label. Comparison uses
the prices, not a rounded displayed return. This is price direction, not total
return, a fill price, expected return magnitude, option POP or trade profit.

| Item | Exact miniature choice |
|---|---|
| Universe | Option A: one neutral `InstrumentKey(symbol=RELIANCE, exchange=NSE, segment=NSE_EQUITY, instrument_type=EQUITY)`; no provider ID or ticker suffix required |
| Alternatives rejected | An index (B) changes the accepted initial cash-equity domain; five–ten symbols (C) add coverage work without proving a new mechanism. No full F&O universe |
| Selection meaning | RELIANCE is a fixed engineering subject, not a claim about its current liquidity, suitability or future performance; no hindsight survivor-screening |
| Reference | S0's qualified completed close, observed and available by cutoff; never a quote's `previous_close`, current last price or guessed obtainable fill |
| Next session | Exact adjacent eligible S1 in a supplied versioned, complete schedule; coverage proves no intervening eligible session and subject eligibility |
| Window | S1 official open to S1 official completed close; `target_open_time` and `target_resolve_time` are scheduled instants, not the later arrival/recording of the close |
| Calendar | `QualifiedSessionSchedule` carries source authority, coverage, exceptions, publication/availability/acquisition/admission and revision chain; no weekday arithmetic/calendar engine |
| Equal close | Label 0, explicitly included |
| Missing outcome | PENDING before its pinned maturation deadline; CENSORED/INELIGIBLE after it, never zero |
| Corporate action | Known affected or unknown-coverage unadjusted S0→S1 window is ineligible. No adjustment engine; later discoveries append invalidation revisions |
| Revised target window | Do not move an old request to S2. A changed/cancelled captured window is censored; a new request independently qualifies the new schedule |
| Modes | ACTUAL requires genuine timely computation/issue; SIMULATED retains historical as-of and real later computation, never a historical `issued_at` (§9) |

Observation identity binds target/version, neutral subject, S0/S1 IDs and pinned
schedule/window/reference basis. The source close is a known reference before
the future observation window, not an intraday path or execution entry.

## 5. Data qualification and input boundary

Use a captured `HistoricalSeries(interval="1d")`, directly or extracted from an
unchanged `AnalysisContext.history`. Add a **small qualification companion**, not
a second market-data client. Each qualified close carries session/subject, exact
decimal source price and unit/basis, canonical bar fingerprint, source/provider/
origin/document-version refs and captured bytes, observation/publication/
availability/acquisition/admission times, completeness/precision/authority
decisions, action-coverage and revision refs. A schedule has analogous source
coverage and completeness proof. Both policies are pinned, not free-text claims.

A1 floating close values alone do not establish exact source precision.
`Decimal(str(bar.close))` is not proof of an original decimal lexeme. A real
capture needs its exact source price or accepted exact-price companion plus a
validated correspondence to the canonical bar. Synthetic fixtures author exact
decimal strings and matching bars openly; they cannot masquerade as official
exchange captures. Do not retrofit A1/A2 contracts to add this qualification.

Use a typed data basis, `SYNTHETIC_FIXTURE` or `QUALIFIED_CAPTURE`, orthogonal to
the two realization modes. The shipped FF-0 profile enables only the synthetic
basis. An attempted empirical run is denied before execution with
`EMPIRICAL_PROFILE_NOT_ENABLED`; it is not silently relabeled synthetic.
Schema support for qualified captures is not approval of a dataset. Real
historical qualification/count preparation is an FF-1 entry gate.

Forecast input closure contains the reference close, schedule, source proofs,
prior-label/count artifact, permitted request and binding. **It excludes the
future target outcome.** Later outcome input is separate and Evaluation-owned.
Past labels supporting a count artifact must have been available by its fit
knowledge cutoff, itself no later than the request information cutoff. All
selection/universe/action knowledge is similarly bounded. Later acquisition
must remain later; it is never `CAPTURED_AS_KNOWN` by assertion.

Missing values are typed absences, not 0, null converted to a fact, imputation or
0.5 probability. Zero volume/OI, where supplied, remains valid factual data and
is not a BaseRate predictor. No A2 indicator or previous-close recalculation.

## 6. Exactly one forecaster and its artifact

Choose `HistoricalBaseRateForecaster`, registered ID
`forecaster:historical-base-rate`, implementation version `1.0`.

| Policy | FF-0 definition |
|---|---|
| Window | Last **20 scheduled adjacent-session transitions ending at the artifact's pinned fit cutoff**, not a per-request rolling refit |
| Support | Synthetic engineering profile requires all 20 eligible labels; no reaching farther back to replace excluded transitions. Fewer than 20 → UNAVAILABLE |
| Pool | One pooled cohort across the declared miniature universe, currently one subject; no subject-specific model map or adaptive weighting |
| Estimate | `p = positive_count / eligible_count`; deterministic rational calculation, bounded finite binary probability |
| Input validity | Counts strict integers (reject bool), `0 <= k <= n <= 20`; count witness must agree with included prior labels and exclusions |
| Zero/one | k=0,n=20 → raw 0; k=20,n=20 → raw 1. Valid boundary estimates, not statements of certainty |
| No history | No 0.5 fallback, smoothing, learned prior or default forecast; explicit required-support absence |
| Artifact | Immutable declarative counts plus complete ordered window, included/excluded row refs/reasons, target, source/label revisions, fit-knowledge cutoff, actual preparation completion, producer/code/config/rights and semantic digest |
| Leakage | Current target outcome cannot enter fit data; all label availability, preprocessing/selection and universe evidence meet fit cutoff; mode-specific existence constraints still apply |
| ACTUAL | Exact artifact and authorized synthetic-use binding actually exist before timely issue; historical unit-test clocks do not establish live deployment |
| SIMULATED | Artifact may be prepared later from eligible historical knowledge; retain actual preparation/computation time and simulation profile, not fake issuance |

FF-0 consumes an authored synthetic count artifact and independently checks its
count witness; it does **not** implement empirical training, a model-selection
loop or inference-time refitting. A different window/counts is a new artifact
and future COLD selection. Twenty is a small test-data boundary, **not** a
scientifically sufficient empirical training/calibration threshold. FF-1 must
preregister its empirical population/window/minimum support before outcome
inspection. PersistenceForecaster is not added as a second FF-0 instrument;
LogisticRegressionForecaster belongs to FF-1 (§19).

## 7. Minimal contract inventory

Names below are the selected proposed Python concepts. Nested value objects may
live together; the table is not a demand for one module/service per row. Semantic
fields cannot hide in metadata. Common policy: frozen, extra-forbidden models;
tuple collections accept Python/JSON lists and dump as arrays; naive times fail,
aware zones normalize via `ZoneInfo("Asia/Kolkata")` and JSON emits `+05:30`.
All IDs/versions are typed, nonempty and validated; digests use §12. Mutable
metadata remains extensible but outside authority and scientific requiredness.

| Contract / owner | Required fields and invariants | Persistence / why now |
|---|---|---|
| `ForecastTargetSpec` / Evaluation | ID/version, domain/venue, strict endpoint comparator, threshold 0, price basis/unit, horizon, labeler/action/qualification policy refs; one exact event | One object also serves GroundTruthDefinition; avoid duplicate definitions; pin in every run/outcome |
| `QualifiedSessionSchedule` with nested session records / Evaluation admission of evidence-owner facts | Calendar/venue/segment/timezone, complete ordered sessions, coverage, exceptions, subject eligibility, source knowledge/provenance, qualification decision and predecessor/revision; positive non-overlapping windows and proven adjacency | Full captured schedule, not only a lookup ID; FF-0 synthetic source explicitly identified |
| `QualifiedCloseObservation` / Evaluation admission of evidence-owner facts | Exact decimal price, unit/basis, subject/session, completed bar ref, event/knowledge times, origin/source/version/coverage/finality/precision/action decisions; positive finite price for eligible labels | Exact facts retained for replay/label revisions; unavailable facts have typed reasons |
| `ForecastWindow` / Evaluation | S0/S1, reference observation/ref, open/resolve, calendar version/hash, `outcome_due_at` and maturation-policy pin; source precedes next session, due >= resolve | No mutable next-session lookup during replay |
| `ForecastEvidenceSnapshot` / FF capture of qualified inputs | Target/window, canonical history and qualification companions, ordered evidence refs/hashes, cutoff, basis, universe/rights/source pins, explicit missingness | Complete bounded input closure; no terminal target observation |
| `ForecastRequest` / FF | ID, subject/domain, target/window refs, mode, as-of/cutoff, evidence fingerprint, purpose, permitted profile ref, simulation-profile ref when applicable; no path/model URL/weights/grant | Immutable requested scope; new execution does not overwrite prior request/run |
| `SimulationProfile` / Evaluation protocol, enforced by FF | ID/version, historical knowledge/fit policy, permitted purpose/basis, same-mode comparison policy, code/config digest; no ACTUAL-issuance grant | Required only for SIMULATED; prevents unqualified historical claims |
| `ForecasterDescriptor` / FF execution catalog | ID/version, primitive/composite family, supported target/input/output contracts, dependencies/requiredness and declared resource envelope | Metadata only, not qualification or approval |
| `ForecasterArtifact` with nested BaseRate parameters / Learning artifact custody, read-only in FF | Descriptor/code/config/target/fit/source/version/rights pins, counts/window witness, preparation clock, output kind and calibration dependencies | Declarative immutable model identity; no Learning service or fitted-model serializer in FF-0 |
| `ForecastComposition` with node/edge/root records / FF semantics, startup selection | Version/hash, finite typed node/port/edge/root tuples, IDs/dependencies, roles and policies; reject cycles, duplicates, dangling/type/mode-incompatible edges; FF-0 profile admits one primitive, zero edges, one BENCHMARK root | Same eventual primitive/composite seam; no empty opaque `dict` graph, no implicit PRIMARY |
| `ForecastResult` with binary-output/absence variants / FF | Request/observation/node/root/composition/artifact IDs, mode and applicable clocks, target/window, status, output OR reasons, uncertainty, calibration, validity, limitations/conflicts, provenance, usage, `RESEARCH_ONLY` and `NO_ACTION_AUTHORITY` | One common result envelope; generated raw does not imply admissible advice. Missing field != invented zero |
| `NodeRunRecord` and `ForecastRun` / FF | Expected/attempted nodes, routes, per-node result/absence, exact child/input refs, unique attempt usage, roots by role and aggregate failure/skip reasons | Full declared scope retained even on failure; singleton today, no best-child substitution tomorrow |
| `ForecastUsage` / FF runtime | Attempt ID, monotonic duration, call/token counters, known external cost, local-cost status/reason, resource-policy/version | Zero external/model usage is a fact; unknown local cost is not zero |
| `ForecastCapture` / FF | Schema, run/result/request, complete transitive evidence/artifact/graph/config/code closure, original clocks/usage, semantic and capture hashes, actual record time | Forecast-side write history, not the Evaluation Ledger |
| `OutcomeJournalEntry` / Evaluation | OutcomeKey, observation refs, target/window, exact facts, event/label availability/recording times, truth facets, provenance, revision/predecessor, reasons | Append-only shared truth; never patches a forecast or implies profit |
| `EvaluationLink` / Evaluation | Run/result and outcome revision IDs, exact join tuple, mode/basis/purpose/policy compatibility, eligibility/reasons, creation time/hash | Minimal linkage, not metrics or promotion |
| `ForecastLedgerSnapshot` / Evaluation | Immutable joined projection of captured runs, exact journal revisions and link decisions, snapshot time/policy/hash | Minimal native Ledger view now; full population/metrics in FF-1 |
| `EvaluationPopulationDispositionReport` / Evaluation | Preregistered population/protocol, request-to-observation map, per-arm/per-metric INCLUDED/EXCLUDED/NOT_EVALUABLE and reasons, pinned source revisions and denominator counts | Define invariant-bearing schema in FF-0 per A §9.1; emit actual reports in FF-1, not empty claims of evaluation |
| `ForecastColdConfig` / trusted engineering composition root | Allowed IDs/versions/modes/basis/subject/purpose, registered forecaster and graph/artifact refs, input/output allowlists, immutable bounds and access policy | Explicit local constructor input; not request-editable authority or a replacement R5 owner |

Use a structural `Forecaster` protocol shared by primitive/composite instruments:
accept typed request, admitted evidence and exact artifact; return the same
typed generation payload/absence used by `ForecastResult`. The runtime supplies
trusted clocks, run/node identity and usage in the common result envelope.
No provider, store, broker, mutable registry or clock authority is passed into
the instrument. No competing public `A7Forecast` envelope or automatic mapping
to frozen `agents.models.ForecastEvidence` is introduced.

## 8. Result, qualification and failure taxonomy

Keep F §3's five states: **GENERATED, ABSTAINED, UNSUPPORTED, UNAVAILABLE, FAILED**.
RAW/qualified, synthetic/empirical, actual/simulated, lifecycle, role and consumer
admissibility are separate axes. BaseRate adds no selective-abstention heuristic;
an ABSTAINED golden record exercises persistence/replay of the shared contract,
not a newly invented BaseRate trading rule.

| Condition | Boundary / result | Retry and visibility |
|---|---|---|
| Wrong schema, naive time, malformed ID/mode, impossible field combination | Pydantic validation / typed `ForecastAdmissionError` before execution; not a fabricated ForecastResult | No automatic retry; safe field/reason summary, never input dump |
| Valid request but unsupported target/domain/universe or unresolved unique S1 | UNSUPPORTED / `SCOPE_UNSUPPORTED` or `TARGET_SESSION_UNRESOLVED`; no estimate | New correctly scoped request only |
| Known S1 but absent/stale/ambiguous source, unknown action coverage, too few prior labels, missing request-specific artifact | UNAVAILABLE with `EVIDENCE_MISSING`, `EVIDENCE_STALE`, `CALENDAR_UNQUALIFIED`, `ACTION_COVERAGE_UNKNOWN`, `HISTORY_SUPPORT_INSUFFICIENT` or `ARTIFACT_UNAVAILABLE` | New evidence/request may help; no hidden fetch, imputation or retry |
| Cutoff leakage, actual completion/issue at or after target open | UNAVAILABLE / `KNOWLEDGE_CUTOFF_VIOLATION` or `TEMPORAL_INELIGIBLE`; preserve actual attempt clocks, no backdated issuance | No retry of the same historical ACTUAL window |
| Supported explicit selective denial from a future forecaster | ABSTAINED with pinned policy reason | No FF-0 selector implemented |
| Local execution exceeds budget or instrument raises | FAILED / `LOCAL_DEADLINE_EXCEEDED` or `INTERNAL_EXECUTION_FAILURE`, attempted usage retained | No automatic retry; sanitized failure, diagnostic correlation ID |
| Bad COLD binding, required startup artifact unavailable, unregistered implementation, empirical profile disabled | Typed startup/admission failure before dispatch | Operator correction and fresh construction, never fallback to latest/default |
| Corrupt capture, hash mismatch, missing reference, conflicting duplicate, partial JSONL line, writer lock, disk denial | `ForecastStoreError` / `ForecastIntegrityError`; no false saved-run or replay success | No automatic retry/repair/truncation; report exact safe class and affected ID |
| Pinned verifier absent/incompatible | Verification `UNVERIFIABLE`, recorded replay still allowed if closure is valid | No latest-code substitution or provider/model recovery |
| Programmer/invariant failure in pure functions | Tests expose exception; outer runtime converts only execution-boundary failure to FAILED | Do not catch validation/storage faults as successful domain absence |

Result-producing failures preserve all known requested scope and attempted
usage. Process death or a failed durable write cannot manufacture a completed
capture; logs may explain an incomplete attempt. The CLI maps valid domain
absences to an inspectable successful command, not to scientific success (§13).
If essential target/window identity cannot be constructed at all, the typed
admission error carries the UNSUPPORTED/UNAVAILABLE category and supplied refs;
do not fabricate a qualified window merely to instantiate a full result/run.
That is an admission denial (CLI exit 2), not a completed forecast capture.
Once identity is well-formed, failed qualification can retain the declared
window with explicit reasons without certifying it as qualified.

## 9. ACTUAL / SIMULATED clocks and validation ownership

Exactly two modes; no third historical/replay mode:

```text
ACTUAL_ISSUANCE
  source_close <= information_cutoff <= as_of
    <= computed_at <= issued_at < target_open_time < target_resolve_time

SIMULATED_ISSUANCE
  source_close <= information_cutoff <= simulation_as_of < target_open_time
  simulation_as_of <= computed_at
  issued_at = NOT_APPLICABLE
  computed_at may be later than target_resolve_time
```

`ForecastRequest.as_of` supplies simulation-as-of meaning in SIMULATED mode;
there are not two independently editable request clocks. Retain all nine
accepted meanings: observation event, information availability, information
cutoff, simulation-as-of, actual issue, actual computation completion, target
open, target resolve and outcome recording. Source publication/acquisition/
admission, fit knowledge/preparation completion and label availability are
additional facts, not aliases. Scheduled future opens/action effective dates
may be known at cutoff; realized future prices may not.

| Owner / stage | Check |
|---|---|
| Contract construction | Aware timestamps, field applicability, finite windows, cutoff/as-of ordering; no simulated `issued_at`, no caller-supplied completion/issue override |
| Evaluation qualification | Exact known source revisions, complete calendar coverage, prices/labels/action/universe knowledge, approved historical-availability policy |
| FF admission | Request/artifact/graph/mode/profile compatibility, every relevant fit/selection/evidence knowledge cutoff; genuinely existing admitted binding for ACTUAL |
| FF runtime | Actual completion time and final actual-issue guard, using aware current time; monotonic elapsed duration. Injectable test clock only through Python test construction |
| Evaluation truth/linkage | Outcome event/label availability/recording and revisions are independent of forecast-generation clocks; mode/basis/purpose compatibility is explicit |
| Replay | Preserve original mode/clocks without testing them against today's wall clock; verification adds separate current telemetry, not a replacement original issuance |

The FF-0 internal engineering API defines issuance as the trusted runtime's
handoff of the finalized result to its caller. Prepare its payload before the
final clock/target-open check and do not add asynchronous work between that
guard and handoff. This is **not** CLI stdout time, a database commit, facade
publication or a broker signal. The synchronous owner then saves the capture
with real `recorded_at`; storage failure does not backdate/retract a handoff or
claim a successful saved run. Crash-safe transactional publication is not
claimed by this local miniature.

Illegal ACTUAL timing yields a recorded unavailable attempt, with actual
completion but no invented issuance. A generated raw research result uses an
explicit UNKNOWN validity with `RAW_RESEARCH_NOT_ADVISORY`; that denies current
consumer admission. SIMULATED validity is historical/hypothetical, never a
current-use window. A CLI run of the old fixture is SIMULATED and records today's
real completion time. Only deterministic unit tests inject past ACTUAL clocks;
those prove inequalities, not historical deployment or prospective shadow.

## 10. One persistence path: local JSON artifacts plus JSONL journals

Choose a single filesystem corpus, following existing inspectable repository
patterns. No SQLite, database abstraction layer or distributed store is added.
Separate typed append methods preserve write ownership in the same directory.

```text
ff0_corpus/
  artifacts/<sha256>.json           # immutable input/artifact closure
  forecast_runs.jsonl              # FF-owned ForecastCapture records
  outcome_records.jsonl            # Evaluation-owned OutcomeJournalEntry records
  evaluation_links.jsonl           # Evaluation-owned link decisions
  ledger_snapshots/<sha256>.json    # Evaluation-owned immutable joined views
  .writer.lock                    # exclusive local single-writer guard
```

`ForecastCorpusStore` is narrow and FF-specific. A2 `ReplayCorpusStore` and its
duplicate semantics stay unchanged. Forecast history is not renamed the native
Ledger. Evaluation materializes that Ledger from exact forecasts and journal
revisions; no mutable label is attached to a forecast row.

| Logical record | Unique key / append rule |
|---|---|
| Input/model/config/graph artifact | Content hash; identical bytes are idempotent, same ID with different bytes is a conflict; verify hash before use |
| Forecast capture | Fresh run-instance ID plus content-addressed capture identity; repeated save of the identical capture is idempotent; changed payload under same ID fails |
| Journal row | Stable OutcomeKey plus revision number/entry ID; new revision explicitly names predecessor, reason and real recording time; no overwrite/fork/gap |
| Evaluation link | Content identity includes exact run/result, outcome revision and policy; a later revision creates a new link |
| Ledger snapshot | Hash of pinned joined content including link/record refs and snapshot identity; newer views do not mutate old views |

At bounded startup/read, build in-memory indexes by artifact hash, run ID,
OutcomeKey/revision and link ID. No persistent mutable index or unversioned
`latest` pointer is authoritative. Validate references and revision chains.
Repeated SIMULATED generation always has a new run ID even with the same
probability; idempotent persistence retry of one capture is a different action.

One local writer acquires an exclusive-create lock for a command. Immutable
files use exclusive creation and journals append complete canonical JSON lines.
A stale lock blocks writes until separately authorized inspection; never
silently remove it. A partial/corrupt line blocks reads/appends rather than being
skipped/truncated. Valid orphan artifact files from an interrupted command are
not completed runs. No cross-file transaction, power-loss durability, automatic
repair, concurrent reader/writer snapshot or distributed-lock claim is made.
These are explicit bounded limitations, not reasons to invent a database now.

## 11. Ground Truth, Outcome Journal and Evaluation Link

Evaluation alone resolves labels, triggered by an explicit later local command;
there is no background watcher. It loads the captured target/schedule/reference
and separately supplied completed terminal close and source qualifications.
The labeler never asks the forecaster which outcome is desirable.

```text
Captured S0/reference + exact S1 schedule
                  + later qualified S1 close
                              |
                  Evaluation labeler / policy
                  /                       \
      ELIGIBLE y = 0 or 1        PENDING / CENSORED / INELIGIBLE
                  \                       /
                append OutcomeJournalEntry revision
                              |
       exact ForecastCapture + EvaluationLink policy
                              |
               immutable ForecastLedgerSnapshot
```

The **OutcomeKey** binds neutral subject, target ID/version, S0/S1 window and
reference/terminal basis. It excludes forecaster and realization mode: those do
not create different market facts. A forecast's **observation ID** additionally
binds its cutoff/as-of and qualified source/window versions. Linkage retains
both identities rather than treating every request/simulation as an independent
outcome. Source corrections revise the same outcome when its scientific window
is unchanged; a different scientific window has a different key.

Valid `terminal > reference` gives y=1; equal/down gives y=0. Unavailable,
nonpositive, nonfinite, partial, contradictory or unqualified endpoints are
not labels. Preserve accepted orthogonal truth facets: window maturity,
observation completeness, label eligibility and reasons. The pinned
`outcome_due_at` is supplied by Evaluation's maturation policy and cannot be
chosen from eventual arrival time. For fixtures it is S22's supplied open for
an S21 target (§17); this is an illustrative grace boundary, not a production
SLA. Before due, missing data is PENDING; after due it is CENSORED/INELIGIBLE.
Late valid proof may append a new revision, never retroactively change a prior
report or legitimize an earlier forecast's missing PIT proof.

Keep A §7's axes explicit: window OPEN/CLOSED/CENSORED/UNOBSERVABLE and label
ELIGIBLE/PENDING/INELIGIBLE/AMBIGUOUS are separate. Selection/operation is UNKNOWN
with `OPERATION_NOT_OBSERVED_IN_FF0`; absence of an execution feed is not evidence
that a trade was NOT_TAKEN. Endpoint return can be recorded from qualified
prices; path extrema, MFE/MAE, fills and realized P&L are NOT_APPLICABLE/absent
for this endpoint-only input, never zero-valued substitutes.

Require `outcome_event_time <= label_available_at <= recorded_at` for an eligible
terminal label. Missing terminal facts have no fabricated event timestamp;
scheduled target-resolve remains separately known. Recording/revision time is
actual, monotonically ordered along the predecessor chain. Known action or
schedule corrections append explicit invalidation; no adjusted-price repair,
silent source preference or shift to S2.

The minimal `EvaluationLink` validates exact target/version, subject, window,
reference/source-basis compatibility, pinned journal revision, purpose, data
basis and realization-mode policy. Generated raw forecasts can link to truth
for inspection; absent forecasts/outcomes retain NOT_EVALUABLE/reasons. A
synthetic eligible label is only **engineering-link eligible**, not empirical
evidence. No synthetic/real pooling or mixed-mode comparison is implicit.
FF-0 stops at linkage and its immutable joined view: no metric, benchmark win,
calibration, trading utility or promotion claim. FF-1 adds full populations,
paired comparison and metric-specific dispositions.

## 12. Identity, recorded replay and pinned verification

Use a dedicated serializer profile `tiaf.ff.canonical-json/1.0`: sorted object
keys, compact separators, UTF-8, `ensure_ascii=True`, `allow_nan=False`, canonical
aware ISO timestamps, enum values, ordered semantic arrays and normalized exact
decimal strings (no exponent/trailing fractional zeros; zero as `"0"`). These
settings are frozen and tested. SHA-256 hashes this canonical representation;
self-identifying digest fields are excluded only from their own hash input.
No global removal of clocks, cost, absent fields or lineage. Do not reuse a
legacy semantic helper that intentionally removes timings for another domain.
Exact price facts use the decimal-string convention. Binary probability remains
a finite JSON number: BaseRate computes `k / n` from strict integers once, while
the count witness preserves the exact rational basis. Probability zero is not
omitted; round-trip/verifier comparisons use the pinned representation.

Minimum transitive pins:

- Request/observation/run/node/root identity; exact subject, target/version,
  window/reference, mode, cutoff/as-of, simulation profile where applicable.
- Full captured canonical evidence, qualification decisions and source bytes;
  schedule/action/universe/label revisions and rights policy, not URLs alone.
- Descriptor/implementation/build identity, declarative model contents and fit
  lineage; graph, COLD binding, config, output semantics and dependency versions.
- Original result, status/absence, calibration/uncertainty/validity, original
  computation/issuance/recording facts and unique usage; serializer/schema IDs.

The trusted launcher supplies an explicit build identity; the forecaster does
not invoke Git. Hostnames, filesystem paths and transient process IDs are not
scientific identity. Artifact locations may change without changing content.
Every new execution allocates a run-instance ID even if an injected test clock
and payload match another run. Metadata must not carry unpinned semantics.

| Operation | FF-0 behavior |
|---|---|
| Recorded replay | Validate versions, references and hashes; reconstruct the exact captured contracts/result. No registry, forecaster invocation, provider, model, fitting or re-labeling |
| Pinned deterministic verification | Resolve only the exact compatible registered BaseRate implementation, recompute its generation payload from captured inputs, reconstruct original semantic envelope with original clocks/usage and compare; record new verification timing/cost separately |
| Missing verifier | `UNVERIFIABLE`; never use current/latest implementation or substitute a forecast. Valid recorded replay remains available |
| Corrupt/missing closure | Fail integrity explicitly, not partial replay success |
| New historical simulation | Execute a new SIMULATED run, with actual current computation and a new ID/capture; not replay even if p is equal |

BaseRate verification is exact; no tolerated floating replay is needed. Later
numerical-tolerance profiles must be separately versioned and accepted; they
cannot weaken old exact records. Storage retries cannot refresh validity or
rewrite realization mode. Original capture bytes remain unchanged after replay.

## 13. Local workflows and command boundary

One **future engineering script**, `scripts/forecast_miniature.py`, not a public
TI Shell operation. It follows explicit command/artifact conventions, with no
NLP routing, hidden acquisition or arbitrary import/model path. `--help` and
missing-verb invocation perform no writes/external calls. `--config` is an
explicit trusted local configuration path; scientific input/run/outcome options
are logical registered IDs resolved only within its bounded allowlists.

```text
Trusted config + captured forecast inputs
  -> bounded parse / source & clock admission
  -> exact registered singleton composition
  -> raw BaseRate result OR explicit absence
  -> FF capture / actual record timestamp
  -> later Evaluation truth command + separate terminal evidence
  -> journal revision -> link -> derived Ledger snapshot
  -> offline recorded replay / optional exact pinned verification
```

Historical simulation uses a historical cutoff and simulation profile over the
same PIT-qualified inputs, but current real computation time and no issue time.
There is no historical fit loop or hindsight outcome in the inference closure.
An ACTUAL request to an already-open target fails timely admission; no `--now`
or automatic conversion to SIMULATED can disguise it.

**Planned commands, available only after FF-0.4 implementation:**

```bash
python scripts/forecast_miniature.py run \
  --config tests/fixtures/forecasting/ff0/local_config.json \
  --input ff-request:reliance-s21-simulated
python scripts/forecast_miniature.py outcome \
  --config tests/fixtures/forecasting/ff0/local_config.json \
  --input ff-outcome-input:reliance-s21-up
python scripts/forecast_miniature.py link \
  --config tests/fixtures/forecasting/ff0/local_config.json \
  --run ff-run:REPLACE_WITH_EMITTED_ID \
  --outcome ff-outcome:REPLACE_WITH_EMITTED_ID
python scripts/forecast_miniature.py replay \
  --config tests/fixtures/forecasting/ff0/local_config.json \
  --run ff-run:REPLACE_WITH_EMITTED_ID --verify
```

The checked-in example config will declare captured fixture inputs and one
explicit output directory `/tmp/tiaf-ff0-miniature`; it is not a default when
config is absent. The operator reviews/owns that directory, with no symlink
traversal or cleanup. Tests substitute `tmp_path` through trusted construction.
No command writes into checked-in fixture directories. Use emitted IDs in the
last two commands; the placeholders are not pre-existing runs. Each result
prints mode, basis, target/window, raw probability or absence/reasons, IDs,
qualification limits and replay/link status. JSON output is versioned.

Exit 0 means the requested operation completed, including a valid domain
UNAVAILABLE/UNSUPPORTED result; it does not mean forecast/evaluation success.
Exit 2 means command/config/admission error. Exit 1 means execution, persistence,
integrity or requested verification failure/unverifiability. No live default,
implicit model fetch, `--mode` override of persisted inputs or secret loading.

**Public Shell/facade and capability map:** FF-0 publishes no `forecast.assess`,
new `ArtifactKind`, R2 descriptor, R5 catalog field or automatic consumer mapper.
The nine-operation catalog remains unchanged. A separately reviewed caller-bound
projection/publication can follow FF-2 without optional FF-3+; deferring that
surface avoids pretending the engineering script grants consumer authority.

## 14. Concrete proposed modules and dependency direction

```text
src/tiaf/forecasting/                    # new, lean FF package
  __init__.py                           # docstring only; explicit module imports
  enums.py                              # leaf mode/status/output enums
  contracts.py                          # FF contracts, COLD config, graph/pins
  evidence.py                           # pure capture/qualification checks
  forecasters.py                        # one protocol, BaseRate, static registry
  runtime.py                            # COLD construction, dispatch, clocks, usage
  store.py                              # narrow JSON/JSONL corpus and canonical hash
  replay.py                             # recorded replay and exact pinned verifier
  errors.py                             # bounded admission/store/integrity errors
src/tiaf/evaluation/                     # extend existing package, no A2 redesign
  forecast_contracts.py                 # target/schedule/close/window/truth/link/ledger
  forecast_truth.py                     # independent deterministic labeler
  forecast_linkage.py                   # linkage and joined snapshot
scripts/forecast_miniature.py            # engineering run/outcome/link/replay
tests/unit/forecasting/
tests/unit/evaluation/test_forecast_truth.py
tests/unit/evaluation/test_forecast_linkage.py
tests/fixtures/forecasting/ff0/
tests/acceptance/ff0/
  corpus_manifest.csv
  golden_results.json
  test_ff0_acceptance_corpus.py
  README.md
```

Shared mode/status enums are leaf-only. Evaluation contracts may reference the
mode enum and neutral data/common types but not FF runtime/contracts; linkage
implementation may consume FF captures. FF contracts reference Evaluation's
target/window specifications. A docstring-only FF `__init__` avoids import
cycles and optional SDK activation. No `learning` service package, abstract
repository framework, metrics/config/logging package or generic plugin loader
is needed now. Target/clock validators live next to their owning contracts and
runtime checks, not in a second calendar or forecasting framework.

Future facade publication may extend existing bootstrap/facade/Shell seams
through a new versioned additive contract after review. This tree is an internal
constructor, not a second permanent application-wide startup owner.

## 15. Static registry, COLD configuration and trust

The execution registry is a code-owned immutable typed mapping of one exact
registered descriptor/version to the BaseRate implementation. Use a read-only
mapping view after construction; no request registration, dotted import path,
entry-point scan, mutable global registry or fallback to latest. It is a resolver
view, not a second artifact/lifecycle registry. Learning retains future artifact
custody; fixture artifacts are explicit declarative specimens, not approved
trained-model registry entries.

| Setting | Classification / ownership |
|---|---|
| Two modes, target comparator/basis, tuple/time/clock/authority semantics | Architecture invariant; not configurable |
| Allowed IDs/versions/subject/modes/basis/purpose, exact graph/artifact and input/output roots, limits/access policy | Trusted COLD config; explicit file or object only, no `.env` discovery; frozen startup fingerprint |
| Subject within allowed scope, target/window, as-of/cutoff/mode, evidence and permitted simulation-profile IDs | Request-level; cannot widen COLD authority or change model |
| Counts/window/support, fit knowledge/source/config/code/rights | Pinned model artifact; no request hyperparameters |
| Empirical sampling, splits, logistic penalties, calibration/support thresholds | Future preregistered experiment protocol, not FF-0 switches |

Fixed **engineering** bounds for the shipped profile: one node, one root, zero
edges, depth one, one execution attempt, twenty transitions, at most 64 supplied
session/close records per input, 1 MiB per artifact/JSONL record, 256 records per
journal and 32 MiB total corpus. Local inference deadline is one second, checked
before/after the pure call; file I/O is separately bounded by size, not hidden
inside model duration. Bounds are checked before allocation/dispatch where
possible; exceedance fails, never silently truncates. Altering bounds requires
a new trusted profile identity. These are resource limits for fixtures, not
estimated production service levels.

Trust boundary: one local operator and OS file permissions; no multi-tenant
authentication claim. Only allowlisted artifact IDs under canonical configured
roots; reject traversal, escapes, symlink substitution, unknown schema and
unauthorized writes. A digest proves byte identity, not source authority.
No untrusted pickle, executable model, credentials, free-form loader path or
metadata-driven authority. Read rights/retention restrictions remain captured
and enforced; possession of a file does not create a data-use license.

Retention: keep captures, inputs, journal revisions, links and snapshots
append-only; no automatic TTL cleanup/compaction/deletion. Read access never
mutates. Rights expiry may deny a new use without falsifying old records; any
legally required deletion/repair needs separate authorization and must expose
resulting replay unavailability, not promise eternal retention. FF cannot write
truth, and Evaluation cannot overwrite forecasts. No R1–R5 accepted semantics
or current startup contracts are changed.

## 16. Timeout, cost and observability

Record structured run/request/result IDs, target/version, subject, mode, basis,
forecaster/artifact/composition, status/reasons, duration and capture/link/replay
fingerprints. Log no evidence bodies, prices-by-default, arbitrary metadata,
credentials, local sensitive paths or exception payloads. Safe error classes
and correlation IDs are enough for bounded diagnostics. A metrics/telemetry
service and provider-billing integration are deferred.

FF-0 has zero external provider/model calls, zero input/output model tokens and
zero external model cost. Local CPU/storage cost is `UNKNOWN` / unpriced,
not falsely zero; measured duration is retained. Count one attempt once even
when referenced by root and run summaries. Verification records its own usage
separately from the original generation. A local overrun produces FAILED after
return; this is cooperative deadline detection, **not** process isolation or
hard preemption. Hard cancellation, external retries/reservations and provider
cost settlement remain gated future work. No automatic retry is enabled now.
The profile does not offer a strict currency cap over unpriced local resources;
a request requiring such a guarantee is denied before dispatch, not declared
within budget because external model cost is zero.

## 17. Deterministic fixtures, test matrix and 28-case corpus

Create fixtures only during implementation under
`tests/fixtures/forecasting/ff0/`. They are openly synthetic, not claims about
actual RELIANCE prices, exchange holidays or source availability. The supplied
calendar covers these 25 ordered fixture sessions S00…S24:

```text
2026-01-06  2026-01-07  2026-01-08  2026-01-09  2026-01-12
2026-01-13  2026-01-14  2026-01-15  2026-01-16  2026-01-19
2026-01-20  2026-01-21  2026-01-22  2026-01-23  2026-01-27
2026-01-28  2026-01-29  2026-01-30  2026-02-02  2026-02-03
2026-02-04  2026-02-05  2026-02-06  2026-02-09  2026-02-10
```

Each has supplied 09:15 open and 15:30 close, Asia/Kolkata, with explicit
synthetic complete coverage and excluded-date notices; do not infer them from
weekdays. S00…S20 exact decimal close strings:

```text
100, 101, 102, 101, 102, 103, 102, 103, 104, 103, 104,
105, 104, 105, 106, 105, 106, 107, 106, 105, 105
```

These produce twenty transitions: twelve up, seven down, one equal; the
authored count artifact returns **12/20 = 0.6**, an illustrative raw estimate.
S20 reference is 105; separate S21 outcome inputs give 106 (up), 104 (down),
105 (equal), missing, conflicting-source and action-affected variants. S21 due
time is S22's supplied open. Missing/invalid session variants remove completeness
or qualify a material revision; the labeler must not guess a replacement day.

Each prior close becomes available at its session's supplied 15:35 and admitted
at 15:36 in synthetic history. The artifact fit-knowledge cutoff is S20 15:45;
forecast cutoff 16:00, as-of 16:05. The ACTUAL unit fixture injects completion
16:06 and issue 16:07 and a genuinely prior fixture preparation/binding time.
The separate SIMULATED specimen has historical as-of but later actual artifact
preparation/computation. Actual CLI execution never uses injected past clocks.
Every origin/source/rights/qualification is labeled fixture-only; a fictional
official-looking provider name is not source proof.

Fixture files: target spec, schedule, canonical daily history, exact-price/
qualification companions, count artifact with prior-label witness, singleton
graph, forecast request/simulation profile, separate outcome inputs and trusted
local config. Golden recorded captures use fixed IDs and test clocks; timing
assertions in live CLI tests are structural/range-based, not achieved by deleting
timestamps from semantic hashes. All writes go to `tmp_path` in tests. No test
downloads data, trains a model or calls providers.

**U** = unit; **I** = local integration; **G** = semantic golden. The manifest
contains exactly 28 named semantic cases; parameterized pytest item counts may
be higher and must be reported from actual runs, not inferred as “28 tests.”
Clause references retain the accepted architecture as the test oracle.

| ID / case | Kind | Required assertion | Clause / first step |
|---|---|---|---|
| FF0-01 immutable-contract-roundtrip | U/G | Tuple/list/JSON round-trip, frozen replacement/append rejection, strict schema/finite decimals | A §4; F §3 / 0.1 |
| FF0-02 target-and-subject-scope | U/G | Exact target succeeds; unknown target/version, index and outside-universe subject do not produce estimates | A §3; F §3 / 0.1 |
| FF0-03 malformed-mode-and-fields | U | Unknown mode, contradictory mode-specific fields and missing required refs reject before dispatch | A §5.2; F §3.2 / 0.1 |
| FF0-04 timely-actual | U/G | Valid ACTUAL inequalities, artifact existence and true completion/issue preserved; synthetic basis explicit | A §5.2 / 0.1 then 0.3 |
| FF0-05 late-actual-no-backdating | U/G | Completion or issue after open → unavailable attempt; no fake issued_at or conversion to simulation | A §5.2 / 0.3 |
| FF0-06 later-computed-simulation | U/G | Historical as-of, real later compute/fit completion, no actual issue, profile pinned | A §5.2; F §3.3 / 0.1 then 0.3 |
| FF0-07 cutoff-and-fit-leakage | U/G | Future feature, prior-label availability, selection/universe/action knowledge or fabricated earlier acquisition denied | A §5; F §13 / 0.1 then 0.3 |
| FF0-08 target-open-strict-boundary | U | Equality at open fails ACTUAL issue and SIMULATED as-of; no one-microsecond adjustment | A §§3/5.2 / 0.1 |
| FF0-09 timezone-and-distinct-clocks | U | Naive rejects; UTC/other aware normalize to +05:30; cutoff != as-of permitted; no duplicate editable simulation clock | A §§3/5.2 / 0.1 |
| FF0-10 qualified-calendar-and-price | U/G | Adjacency/coverage/finality/positive exact price required; float rendering alone insufficient; no weekday/quote substitution | A §3.1 / 0.1 |
| FF0-11 deterministic-baserate | U/G | 12/20=0.6, stable payload/hash, prior witness matches counts, no request-time fitting | A §8; F §17 / 0.3 |
| FF0-12 support-and-zero-boundaries | U/G | n<20 unavailable; no history no 0.5; k=0 and k=20 serialize 0 and 1; bool/invalid counts reject | A §§8/10; F §3 / 0.3 |
| FF0-13 missing-stale-action-evidence | U/G | Missing/stale proof and unknown/affected action window produce explicit absence, no source fallback or adjustment | A §§3.1/5.1/13 / 0.1 then 0.3 |
| FF0-14 status-not-qualification | U/G | All five status contracts; RAW generated is not calibrated/advisory; ABSTAINED recorded fixture has no invented BaseRate rule | A §10; F §3 / 0.1–0.3 |
| FF0-15 finite-singleton-composition | U | One typed primitive/root accepted; duplicate/dangling/cyclic/type-incompatible graphs reject; unsupported non-singleton config never dispatches | F §§4–6; A §2.2 / 0.1 |
| FF0-16 cold-binding-and-absence | U/I | Registered exact version only; immutable mapping; request cannot choose imports/artifact replacement; missing required binding fails startup | A §16; F §15 / 0.3 |
| FF0-17 append-idempotence-conflict | U/I/G | Append then identical retry idempotent; same ID/different bytes rejects; no overwrite; exact references | A §14; F §18 / 0.2 |
| FF0-18 mode-coexistence-new-run | I/G | ACTUAL/SIMULATED distinct captures coexist; repeated simulation creates fresh run; no extra independent outcome | A §5.2; F §12 / 0.2–0.3 |
| FF0-19 independent-up-down-tie-truth | U/G | Exact completed close gives 1/0/0 without forecaster call; window/event/availability/recording distinct | A §§3/7 / 0.2 |
| FF0-20 pending-missing-and-censored | U/G | Missing before deadline pending; after deadline censored/ineligible; bad source/nonpositive/action conflict not zero | A §§3.1/7 / 0.2 |
| FF0-21 journal-revision-and-time | U/I/G | Revised close/source/action/schedule appends predecessor; recording can't precede availability; no fork/rewrite or S2 shift | A §§3.1/7/14 / 0.2 |
| FF0-22 exact-link-and-ledger | U/I/G | Target/subject/window/version/mode/basis mismatch denied; exact journal revision joined; absent labels NOT_EVALUABLE | A §§7.2/9.1; F §§11–12 / 0.2 |
| FF0-23 recorded-replay-no-calls | I/G | Full reconstructed semantics/fingerprints equal; forecaster/registry/provider sentinels remain unused; original bytes unchanged | A §14; F §18 / 0.2 |
| FF0-24 pinned-verify-not-simulate | I/G | Exact recomputation, separate verifier usage; missing verifier UNVERIFIABLE; new simulation is not replay | A §14; F §18 / 0.3 |
| FF0-25 corrupted-partial-locked-store | U/I | Altered hash/missing closure/partial JSONL/writer lock/disk failure deny success; no auto repair or truncated reads | A §§14–15; F §18 / 0.2 |
| FF0-26 lean-import-and-authority | U/I | No optional ML/provider/MCP import, network/model/broker call, old A2/A6 mutation or new published capability | A §§11/16; F §16 / 0.1–0.4 |
| FF0-27 bounds-cost-and-private-logs | U/I | Size/count/deadline fails closed; zero model/provider calls/tokens, unpriced local cost, no sensitive logs, no double-counting | A §15; F §18 / 0.3–0.4 |
| FF0-28 local-engineering-end-to-end | I/G | CLI help safe, explicit config/IDs, simulated run→separate truth→link→replay; exit codes and unavailable paths; source fixtures untouched | A §§14/16–17; F §17 / 0.4 |

Extra assertions attach to these named cases rather than inflating a compliance
number. Tests must cover malformed target vs valid-but-unsupported target,
invalid source vs absent source, logical generation vs storage success, and
unpriced cost vs zero external cost. No green test count is an empirical claim.

## 18. Four bounded FF-0 implementation sub-milestones

These are substeps **inside FF-0**, not a parallel A7.x hierarchy. Each needs a
separate implementation/acceptance request; checkpoints below are recommended
future commits only. No tag or runtime work is authorized by this plan.

| Step | Scope and files | Tests / exit criteria | Dependency / checkpoint |
|---|---|---|---|
| **FF-0.1 — Contracts, target and clock foundation** | New FF `__init__`, enums, contracts, errors and pure evidence validators; Evaluation `forecast_contracts`; deterministic target/schedule/price/request specimens. Define population-report invariants, not metric emission | FF0-01–04/06–10/13–15/26 relevant contract cases; list→tuple→JSON, strict target/schedule/PIT, both modes, graph shape and no optional imports. No runtime/store/CLI/train path | Accepted plan and explicit request. Suggested `feat(ff0): add target contracts and clock admission foundation` |
| **FF-0.2 — Capture store, truth and recorded replay** | `store`, recorded part of `replay`, `forecast_truth`, `forecast_linkage`; constructed immutable run specimens; journal/link/ledger fixtures | FF0-17–23/25 plus scope/version/rights failures; full captured closure, append/revision/locking integrity, independent exact truth, recorded replay with all execution sentinels forbidden | 0.1 accepted. Suggested `feat(ff0): persist captures and link immutable outcome truth` |
| **FF-0.3 — BaseRate, COLD runtime and pinned verification** | `forecasters`, `runtime`, exact verifier extension in `replay`; synthetic count artifact/witness and immutable binding | FF0-04–07/11–16/18/24/26–27; timely ACTUAL tests, real-clock SIMULATED, exact 0.6/0/1, unavailable support, one-attempt accounting and missing-verifier denial. No empirical profile/fit | 0.2 accepted. Suggested `feat(ff0): run pinned baserate miniature with honest realization clocks` |
| **FF-0.4 — Engineering CLI and acceptance hardening** | `scripts/forecast_miniature.py`, named 28-case manifest/goldens/driver/README, relevant script documentation; no public parser/catalog change | All 28 semantic cases mapped to runnable tests, full existing quality gates, local end-to-end/absence/failed-store/replay demonstrations, zero external calls and no frozen semantics changes | 0.3 accepted. Suggested `test(ff0): harden captured miniature workflow and acceptance corpus` |

At each step run relevant tests and repository static gates in proportion to
scope; FF-0.4 runs the full suite. Future complete-miniature commands (not run
by this planning pass, and only once these paths exist):

```bash
python -m compileall src scripts
pytest -q tests/unit/forecasting tests/unit/evaluation
pytest -q tests/acceptance/ff0
pytest -q
ruff check src tests scripts
mypy src tests
git diff --check
```

FF-0 acceptance must report actual test counts, deterministic example result,
failure/absence examples, preservation of frozen A1–A6, no capability addition,
recorded/pinned replay and all carried empirical/calibration/publication limits.
It does not freeze the A7 major milestone or authorize FF-1 automatically.

## 19. FF-1 / FF-2 preview and growth without a second framework

**FF-1:** add one regularized LogisticRegressionForecaster as B2 beside pinned
B0, a small explicit feature schema and persisted model artifact. Initial
feature proposal is A2 `return.log` for 1 and 5 completed daily bars, both
`AVAILABLE`, finite, same context/cutoff, unit `log_ratio`, with source lineage;
the forecaster consumes, not recalculates them. Exact empirical dataset/split,
solver/dependency/seed/penalty/scaling/support protocol and all trials must be
pinned and approved before fitting/outcome inspection. No large feature system
or tuning to RELIANCE examples. A2 feature presence alone does not prove PIT.

Evaluation realizes the Benchmark Registry view, population-disposition report,
chronological walk-forward with purge/embargo as required, paired common-outcome
comparisons, proper metrics and uncertainty/denominator accounting. Zero pairs
or inadequate support remains NOT_EVALUABLE/inconclusive. Candidate preparation
and count/model fitting require separate bounded Learning grants. No calibration
is silently folded into B2 or a count artifact.

**FF-2:** separately held-out sigmoid fitting by Learning, independent calibration
and health/context qualification by Evaluation, exact wrapper application by FF,
lossless lifecycle/role/approval history, scoped manual prospective ACTUAL shadow,
and explicit reviewer approval followed by COLD binding. Offline success does
not authorize shadow or advisory use; matured ACTUAL shadow is not replaced by
SIMULATED reliability. This completes the accepted calibrated miniature. The
basic review/denial/rollback workflow is not deferred until FF-6.

```text
FF-0 BaseRate mechanical path
   -> FF-1 Logistic + B0 paired raw research
   -> FF-2 independent calibration / lifecycle / reviewed shadow
        + separately authorized public projection, if wanted
        + optional FF-3 conventional challenger / simple ensemble
        + optional FF-4 LLM
        + optional FF-5 FM/LFDE
        -> optional FF-6 governed correction expansion
        -> conditional FF-7 advanced routing
```

Stable meanings carried through growth: request/target/window/mode, evidence
and fit knowledge, common output/absence envelope, typed graph/node/root IDs,
full lineage, unique usage, truth identity, revision linkage and replay pins.
An ensemble adds graph members, not its own truth; an LLM adds a governed adapter,
not privileged authority; FM/LFDE adds family-specific artifact internals, not
a second Forecast Ledger or evaluator. Governed correction proposes new
artifacts and evidence, never auto-activates them. Later schemas may need explicit
new versions; “growth seam” does not mean an unversioned promise that no field
will ever be added. Do not implement these optional families now.

## 20. Versioning and compatibility

Give each new request/result/capture/journal/link/ledger/config schema an explicit
domain ID and version `1.0`; target version, forecaster implementation version,
artifact content ID and serializer profile are separate pins. Existing package
`0.1.0`, A0 schema `1.0`, A2 replay and R3/A6 fingerprints do not change.

Unknown/newer schema versions are explicitly unsupported, never parsed as the
nearest/latest version. Recorded replay uses exact captured schema semantics;
pinned recomputation also needs compatible recorded implementation identity.
A future converter creates a new artifact with old→new lineage and a reviewed
mapping; original bytes remain. No migration engine, silent in-place rewrite,
automatic V1↔V2 forecast mapping or metadata compatibility escape hatch.

## 21. Implementation prerequisites and carried constraints

| Prerequisite | Status | Resolution / gate |
|---|---|---|
| Accepted architecture and checkpoint | RESOLVED | A7 acceptance complete; HEAD already contains `3aceb27` architecture commit |
| Exact FF-0 scope, target, universe and BaseRate policy | RESOLVED | §§2/4/6: singleton synthetic mechanics; no empirical threshold claim |
| Market-data artifact and package/type conventions | RESOLVED | Inspected `HistoricalSeries`, `InstrumentKey`, common time/frozen models; companion qualification is explicit |
| Qualified session/price fixture source | RESOLVED | Authored synthetic schedule/decimal/source records in §17, never real source certification |
| Empirical calendar/price/action/PIT coverage and source/fit rights | DEFERRED | Blocks affected empirical work, not synthetic FF-0; FF-1 must acquire/qualify before fitting; no registry deferral closed |
| Persistence and failure/retention policy | RESOLVED | Bounded single-writer JSON/JSONL, revision/index rules and explicit crash/recovery limits |
| Provenance/fingerprint/replay API | RESOLVED | Reuse neutral source facts; dedicated FF canonical serializer; full closure and exact BaseRate verifier |
| Config/bootstrap/registry | RESOLVED | Trusted local constructor, immutable registered IDs; no change to existing R5 owner or catalog |
| Fixture/test locations, resource limits and engineering commands | RESOLVED | §§13–18 concrete paths, limits, 28 semantic cases, four steps |
| Empirical support/splits/metric thresholds/dependencies and fit grants | DEFERRED | FF-1 preregistration/review before protected outcomes, not guessed here |
| Calibration/lifecycle and operational shadow proof | DEFERRED | FF-2 independent qualification and approvals, not implied by RAW generation |
| Public facade/Shell and downstream use | DEFERRED | Separate post-FF-2 publication/consumer authorization |
| Explicit request to implement FF-0.1 | BLOCKER to executing code now, not to plan readiness | This is a planning-only request; next prompt must authorize the bounded implementation |

No prerequisite remains `NEEDS_REPO_INSPECTION` for this synthetic scope. There
is no new architecture blocker. A7 acceptance clarifications A7A-C01/C02 remain
resolved; C03 failure mapping, C04 local cost/deadline and C05 replay/retention
now have bounded implementation choices. C06 empirical protocols remain gated,
not guessed or waived. C07 navigation is synchronized. The FF acceptance
follow-ups FFA-C01/C03/C04 are planned, not declared implemented; FFA-C02's
FF-0→FF-1→FF-2 separation is unchanged. All 17 A7 findings, 28 FF findings and
58 canonical deferral rows remain intact; this pass closes no runtime deferral.

## 22. Git checkpoint and authorization recommendation

The architecture documentation checkpoint **must precede runtime implementation**
and already does: inspected HEAD is `3aceb27c09c549036b1a179d07b37a4408618b39`,
with the requested `docs(a7): accept FF-integrated forecasting evaluation and learning architecture`
message. Do not repeat that commit, amend it or move `tiaf-a6-baseline`.

Choose a **subsequent planning commit** for this plan and navigation updates.
It separates an already accepted architecture baseline from concrete FF-0
implementation choices. The precise optional future staging/checkpoint sequence
is in §23; it is advice, not executed by this pass. No tag is expected now.
After a reviewed planning checkpoint, separately request FF-0.1. Discovery of a
true architecture incompatibility during coding stops the affected step for
review; it does not authorize a broader A7 redesign.

## 23. Changed files, validation and optional future checkpoint

**26 documentation files: one new plan and 25 navigation/preamble updates.**
The entry snapshot contained 207 README/docs files: 25 updated, 182 unchanged,
none removed; this plan makes 208. Navigation is repeated in existing canonical
dashboards/current-status sections, so those pointers are synchronized rather
than leaving incompatible “next” queues. No old acceptance finding is rewritten.
The FF decision/review/thesis-record set is unchanged; the current plan is reached
through the FF roadmap and current A7 decision/acceptance navigation instead.

| # | Exact changed file | Change |
|---|---|---|
| 1 | [README.md](../README.md) | Current status/next-step navigation only; accepted scope unchanged |
| 2 | [docs/ARCHITECTURE.md](ARCHITECTURE.md) | Current status/next-step navigation only; accepted scope unchanged |
| 3 | [docs/IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) | Current status/next-step navigation only; accepted scope unchanged |
| 4 | [docs/MILESTONES.md](MILESTONES.md) | Current status/next-step navigation only; accepted scope unchanged |
| 5 | [docs/README_TBD_DESIGN_NOTES.md](README_TBD_DESIGN_NOTES.md) | Current status/next-step navigation only; accepted scope unchanged |
| 6 | [docs/TIAF_CAPABILITY_MAP.md](TIAF_CAPABILITY_MAP.md) | Current status/next-step navigation only; accepted scope unchanged |
| 7 | [docs/TIAF_IMPLEMENTATION_TARGETS.md](TIAF_IMPLEMENTATION_TARGETS.md) | Current status/next-step navigation only; accepted scope unchanged |
| 8 | [docs/TIAF_SYSTEM_ARCHITECTURE.md](TIAF_SYSTEM_ARCHITECTURE.md) | Current status/next-step navigation only; accepted scope unchanged |
| 9 | [docs/TIAF_THESIS.md](TIAF_THESIS.md) | Current status/next-step navigation only; accepted scope unchanged |
| 10 | [docs/TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md) | Current status/next-step navigation only; accepted scope unchanged |
| 11 | [docs/TRADINGINTELLIGENCE_ROADMAP.md](TRADINGINTELLIGENCE_ROADMAP.md) | Current status/next-step navigation only; accepted scope unchanged |
| 12 | [docs/TIAF_A7_RECONCILIATION_RECORD.md](TIAF_A7_RECONCILIATION_RECORD.md) | Existing current-navigation preamble only; original body preserved |
| 13 | [docs/TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md) | Existing current-navigation preamble only; original body preserved |
| 14 | [docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md](TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md) | Existing current-navigation preamble only; original body preserved |
| 15 | [docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md) | Current status/next-step navigation only; accepted scope unchanged |
| 16 | [docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) | Current status/next-step navigation only; accepted scope unchanged |
| 17 | [docs/TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md](TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md) | Current status/next-step navigation only; accepted scope unchanged |
| 18 | [docs/TIAF_FM_LFDE_DETAILED_ROADMAP.md](TIAF_FM_LFDE_DETAILED_ROADMAP.md) | Current status/next-step navigation only; accepted scope unchanged |
| 19 | [docs/TIAF_FM_LFDE_THESIS_RECORD.md](TIAF_FM_LFDE_THESIS_RECORD.md) | Existing current-navigation preamble only; original body preserved |
| 20 | [docs/TIAF_FM_LFDE_DECISION_RECORD.md](TIAF_FM_LFDE_DECISION_RECORD.md) | Existing current-navigation preamble only; original body preserved |
| 21 | [docs/TIAF_FM_LFDE_RESEARCH_RECONCILIATION.md](TIAF_FM_LFDE_RESEARCH_RECONCILIATION.md) | Existing current-navigation preamble only; original body preserved |
| 22 | [docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md) | Current status/next-step navigation only; accepted scope unchanged |
| 23 | [docs/TIAF_A7_DETAILED_ROADMAP.md](TIAF_A7_DETAILED_ROADMAP.md) | Current status/next-step navigation only; accepted scope unchanged |
| 24 | [docs/TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md) | Existing current-navigation preamble only; original body preserved |
| 25 | [docs/TIAF_A7_ARCHITECTURE_ACCEPTANCE.md](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) | New current-navigation preamble; original acceptance body preserved |
| 26 | [docs/TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md) | New plan, implementation choices, corpus, gates and complete report |

Validation is documentation/source inspection only, **not** a new runtime or
empirical acceptance. Historical test totals in preserved documents are not
rerun results.

| Check | Result |
|---|---|
| `git diff --check` | PASS |
| New-plan whitespace | PASS; `git diff --no-index --check /dev/null docs/TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md`; exit 1 with no diagnostics means ordinary file difference |
| Local docs links | PASS: 1,217 local links across 28 Markdown files using the existing handbook link validator with worktree checking enabled |
| Status/navigation | PASS: 17 current documents plus eight historical preambles point to FF-0.1, READY_FOR_FF0_IMPLEMENTATION (planning only) and NOT_IMPLEMENTED |
| Accepted normative bodies | PASS: A7 science and stage/crosswalk/gate body, FF architecture §§2–18 and roadmap §§2–10, FM architecture §§2–19 and roadmap §§2–10 byte-identical |
| Historical bodies | PASS: seven existing preamble-only records and the original A7 acceptance body unchanged |
| A7 / FF findings | PASS: all 17 A7 thesis/integration rows and all 28 FF rows/dispositions unchanged; six FF history/decision/reconciliation/creation files byte-identical |
| Deferrals | PASS: all 58 canonical rows and entire register unchanged |
| Thesis preservation | PASS: six DOCX/PDF SHA-256 digests and 37 authoring/assets file digests unchanged; no regeneration/layout claim |
| Frozen A6 / later scope | PASS: 15 A6 reference/artifact digests and all A8/A9/A10 sections in both major roadmap and milestone ledger unchanged |
| Runtime / catalog | PASS: no src/tests/scripts/package/lock edits; static catalog still has exactly nine operations, no forecast operation |
| Plan completeness | PASS: 28 consecutive semantic case IDs and 45 final-report rows; fixture arithmetic 12 up / 7 down / 1 equal = 0.6 |
| Documented clocks | PASS: 16 standalone aware-time assertions of documented inequalities; not tests of implemented FF code |
| Git baseline | PASS: HEAD still `3aceb27c09c549036b1a179d07b37a4408618b39`; A6 tag still resolves to `6dc2ff304aae0e87540260b092919bb91e4d4189`; no commit/tag/push |
| Runtime test suite | NOT RUN / not required for this planning-only pass |

**Optional future Git sequence, only after user review/authorization.**
First confirm the architecture commit above is present and inspect the index.
Stop if it contains unrelated staged work; do not unstage or overwrite it.
Then review/stage only the exact planning file set below. These commands were
**not executed** by this pass.

```bash
git status --short
git log -1 --format='%H%n%s'
git rev-parse 'tiaf-a6-baseline^{}'
git diff --cached --name-only
git diff --check
git add -- \
  README.md \
  docs/ARCHITECTURE.md \
  docs/IMPLEMENTATION_ROADMAP.md \
  docs/MILESTONES.md \
  docs/README_TBD_DESIGN_NOTES.md \
  docs/TIAF_CAPABILITY_MAP.md \
  docs/TIAF_IMPLEMENTATION_TARGETS.md \
  docs/TIAF_SYSTEM_ARCHITECTURE.md \
  docs/TIAF_THESIS.md \
  docs/TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md \
  docs/TRADINGINTELLIGENCE_ROADMAP.md \
  docs/TIAF_A7_RECONCILIATION_RECORD.md \
  docs/TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md \
  docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md \
  docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md \
  docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md \
  docs/TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md \
  docs/TIAF_FM_LFDE_DETAILED_ROADMAP.md \
  docs/TIAF_FM_LFDE_THESIS_RECORD.md \
  docs/TIAF_FM_LFDE_DECISION_RECORD.md \
  docs/TIAF_FM_LFDE_RESEARCH_RECONCILIATION.md \
  docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md \
  docs/TIAF_A7_DETAILED_ROADMAP.md \
  docs/TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md \
  docs/TIAF_A7_ARCHITECTURE_ACCEPTANCE.md \
  docs/TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md
git diff --cached --check
git diff --cached --stat
git diff --cached
# Only after reviewing that the staged set is exactly this planning checkpoint:
git commit -m "docs(a7): plan bounded FF-0 miniature implementation"
git status --short
```

Do not create a duplicate architecture commit, amend accepted history, tag this
planning pass or push. Runtime implementation remains a separate request.

## 24. Final report index and exact next prompt

| # | Requested report item | Answer / detailed location |
|---|---|---|
| 1 | Decision | READY_FOR_FF0_IMPLEMENTATION; planning only (§1) |
| 2 | Planning document | This document |
| 3 | Files changed | Exact inventory in §23 |
| 4 | Repository patterns inspected | Actual source/test paths and reuse decisions (§3) |
| 5 | Exact scope | One target/subject, raw BaseRate, capture/truth/link/replay, synthetic engineering CLI (§2) |
| 6 | Non-goals | No empirical fit, calibration, live/model/trade/public capability or A8 work (§2) |
| 7 | Target | `equity.next_session_close.return_gt_zero/1.0`; strict exact-price comparator (§4) |
| 8 | Universe | One neutral RELIANCE NSE cash-equity fixture; not a current-liquidity claim (§4) |
| 9 | Forecaster | HistoricalBaseRateForecaster; pinned twenty-transition synthetic count witness (§6) |
| 10 | FF-1 forecaster | Regularized logistic, small pinned A2 vector, no calibration yet (§19) |
| 11 | Evidence | Existing canonical daily history plus explicit qualified price/schedule/PIT companions (§5) |
| 12 | Contracts | Owner/requiredness/invariant/persistence inventory, nested rather than service explosion (§7) |
| 13 | Result states | GENERATED / ABSTAINED / UNSUPPORTED / UNAVAILABLE / FAILED (§8) |
| 14 | Realization modes | Both accepted modes, true clocks, anti-backdating and separate replay telemetry (§9) |
| 15 | Ledger | Evaluation-owned immutable joined view; FF capture is write-side history (§10–11) |
| 16 | Outcome Journal | Separate typed append-only JSONL in the same local corpus (§10–11) |
| 17 | Evaluation Link | Exact target/window/subject/revision/mode/basis/purpose validation; no metrics (§11) |
| 18 | Replay | Full transitive identity; recorded reconstruction vs exact pinned recomputation (§12) |
| 19 | Layout | New lean `forecasting`, three additive Evaluation modules, engineering script/tests (§14) |
| 20 | Registry | Static immutable execution resolver, one registered primitive; no lifecycle owner duplication (§15) |
| 21 | COLD config | Explicit trusted profile, bounded IDs/resources/roots; not caller authority (§15) |
| 22 | Shell/facade | Engineering script now planned; public projection deferred after FF-2 (§13) |
| 23 | Capability map | No new operation; current nine stay unchanged (§13) |
| 24 | Execution | Admit→generate/absence→capture→later truth→link→replay (§13) |
| 25 | Historical workflow | Early SIMULATED support with historical cutoff and real later computation (§9/13) |
| 26 | Ground Truth | Independent labeler, exact up/down/tie, maturity/censoring/revision (§11) |
| 27 | Tests | Unit/integration/golden matrix and future quality gates (§17–18) |
| 28 | Corpus | 28 named semantic cases, actual pytest count reported only when implemented (§17) |
| 29 | Fixtures | 25 supplied synthetic sessions, 12/20 raw base rate, separate target outcomes (§17) |
| 30 | Failures | Domain absence vs qualification/startup/store/integrity/programmer errors; no hidden retry (§8) |
| 31 | Retention/access | Local owner/allowlists, append-only, no automatic deletion/repair (§10/15) |
| 32 | Timeout/cost | One-second cooperative inference bound, zero external calls/tokens, unpriced local cost (§15–16) |
| 33 | Observability | Safe structured IDs/status/reasons/duration, no sensitive payload logs (§16) |
| 34 | Security | Trusted registered code/artifacts and bounded roots; no loader/import/network authority (§15) |
| 35 | Versioning | Independent explicit schemas/target/code/serializer pins; no silent migrations (§20) |
| 36 | Sub-milestones | Four FF-0 steps, exact dependencies/paths/tests/exits/checkpoints (§18) |
| 37 | FF-1 preview | Logistic+B0, qualified datasets, paired metrics/population, bounded Learning (§19) |
| 38 | FF-2 preview | Sigmoid, independent qualification, lifecycle and reviewed ACTUAL shadow (§19) |
| 39 | Growth | Same FF seam and truth through optional challengers/ensemble/LLM/FM/correction (§19) |
| 40 | Prerequisites | Inspected foundation resolved; empirical/public/lifecycle gates explicitly deferred (§21) |
| 41 | Blockers | No planning blocker; separate code authorization required; empirical data not qualified (§21) |
| 42 | Architecture checkpoint | Already committed as `3aceb27`; no duplicate/amend/tag (§22) |
| 43 | Planning commit | Subsequent documentation commit recommended, not executed (§22–23) |
| 44 | Validation | Measured checks and preserved scope in §23; runtime tests not required |
| 45 | Next prompt | Exact title below |

**TIAF A7 / FF-0.1 — CONTRACTS, TARGET AND CLOCK FOUNDATION IMPLEMENTATION**

**READY_FOR_FF0_IMPLEMENTATION does not authorize implementation beyond FF-0.**
No commit, tag or push was performed. No runtime implementation was started.
