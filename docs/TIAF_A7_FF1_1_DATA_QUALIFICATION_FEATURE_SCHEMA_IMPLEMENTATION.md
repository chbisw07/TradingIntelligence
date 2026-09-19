# TIAF A7 / FF-1.1 — Data qualification and feature schema implementation

Date: **2026-09-19, Asia/Kolkata**. Decision: **FF1_1_ACCEPTED**.

**EMPIRICAL_FITTING_AUTHORIZED = NO.** Implementation acceptance and empirical
data/fitting authorization are separate gates. No real dataset, entitlement or
retained historical capture was inspected, acquired or certified in this pass.

## 1. Scope and preserved baselines

Entry HEAD: `8bd1a72` (completed FF-1 plan); entry worktree clean.
FF-0 remains frozen at `e5283c9eaa4294bd236186d663335efdf7dab236`,
`tiaf-a7-ff0-baseline`; A6 remains at
`6dc2ff304aae0e87540260b092919bb91e4d4189`, `tiaf-a6-baseline`.
No existing runtime module, dependency, public capability, FF-0 record, accepted
architecture or original FF-1 plan is changed. Package version remains `0.1.0`;
existing contract schema remains `1.0`. New, additive research envelopes use
schema `2.0`; the feature-policy version and target version remain `1.0`.

Implemented: supplied-data qualification, a five-feature A2 projector,
observation/exclusion accounting, deterministic identities, serialization,
bounded local JSON admission, and synthetic tests. Not implemented: scaler or
model fitting, trained artifacts, Logistic inference, splits/walk-forward,
paired metrics, calibration, ensembles, LLM/FM-LFDE, public forecasting or A8.
FF-1's learned forecasting runtime remains **NOT_IMPLEMENTED**.

The [accepted FF-1 plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md)
pins scientific policy. This narrower implementation brief deliberately does
not implement the plan's later split/paired-evaluation machinery.

## 2. Files and native patterns reused

| New file | Responsibility |
|---|---|
| [forecast_research_contracts.py](../src/tiaf/evaluation/forecast_research_contracts.py) | Source, rights, security, calendar, action, bar, maturation and qualification records |
| [forecast_qualification.py](../src/tiaf/evaluation/forecast_qualification.py) | Pure offline qualification and projection into native A2 context |
| [forecast_research_io.py](../src/tiaf/evaluation/forecast_research_io.py) | Explicit-path, explicit-dataset-ID bounded JSON reader |
| [research_contracts.py](../src/tiaf/forecasting/research_contracts.py) | Additive frozen research envelope, fixed schema, unscaled feature vector |
| [research_features.py](../src/tiaf/forecasting/research_features.py) | Five existing A2 calculators; no duplicate feature formulas |
| [_research_support.py](../tests/unit/forecasting/_research_support.py) | Authored 32-session dataset and negative-case construction |
| [test_research_qualification.py](../tests/unit/forecasting/test_research_qualification.py) | Qualification, formulas, clocks, accounting, seals and native truth seam |
| [test_research_isolation_edges.py](../tests/unit/forecasting/test_research_isolation_edges.py) | Dependency/I/O isolation, calendars, local-reader and policy edge cases |
| [Fixture guide](../tests/fixtures/forecasting/ff1_1/README.md) | Fixture meaning, reproduction and non-empirical limitations |

Native reuse: `InstrumentKey`, `ResolutionResult`/`ResolvedInstrument`, exact
decimal parsing, `EvidenceReference`, `SessionRecord`/`QualifiedSessionSchedule`,
`QualifiedCloseObservation`, `ForecastTargetSpec`/`ForecastWindow`, A2
`OHLCVBar`/`HistoricalSeries`/`AnalysisContext`, feature registry/results, FF
canonical JSON/SHA-256, and the existing safe internal JSON file reader.

Current status/navigation is synchronized in README, MILESTONES,
IMPLEMENTATION_ROADMAP, ARCHITECTURE index, TIAF_CAPABILITY_MAP,
TIAF_IMPLEMENTATION_TARGETS, and the A7/FF detailed roadmaps. Historical
planning/acceptance records retain their original then-next language.

## 3. Qualification pipeline and ownership

```text
Explicit local supplied dataset (no acquisition)
        |
        v
Evaluation: rights + source + security + calendar + action + bar/PIT gates
        |
        +--> blocked observation: retained slot, exact reasons, no values
        |
        v
21 qualified historical sessions, ending at reference close
        |
        v
Existing A2 engine -> five unscaled features -> Evaluation eligibility report
        |
        v
Canonical serialization + qualification/feature fingerprints
        |
        X  NO model/scaler fit, no forecast issuance, no order/execution
```

Input assertions are evaluated, **not authenticated by a hash**. A rights
record or source fingerprint does not prove a license, exchange authority or
historical capture existed. The caller must supply truthful, independently
reviewed records backed by retained artifacts. This pass provides neither a
legal-document verifier nor a provider-native capture authenticator.

## 4. Contracts and qualification gates

| Area | Enforced meaning |
|---|---|
| Rights | Five independent `QUALIFIED` / `NOT_QUALIFIED` / `UNKNOWN` states: local research, training, derived-feature storage, evaluation-artifact retention and replay-evidence retention. All must be qualified with nonempty basis references, matching source artifact, pinned rights hash, canonical subject, coverage and unexpired assessment. Provider name grants nothing. |
| Source | Provider/source/origin IDs, versioned acquisition artifact, declared IANA source timezone, data basis, actual bundle acquisition time, rights reference and provenance reference. Bars separately retain their original knowledge clocks. A bundle assembled today is not a historical original capture. |
| Security | Native unique resolution, exact RELIANCE/NSE/NSE_EQUITY/EQUITY target, matching provider security ID per row, GOOD mapping, dated coverage and cutoff-safe master evidence/observation clocks. Ambiguity, derivative series or silently merged identity blocks qualification. |
| Calendar | Native complete qualified NSE cash-equity schedules, source/authority/exception pins, unique ordered sessions, covered dates and contiguous schedule coverage. Every bar must map to its supplied session. Holidays and special weekend sessions follow supplied authoritative records; no weekday inference or live calendar call. |
| Corporate actions | Explicit complete scoped coverage and evidence: adjusted, unadjusted, or unknown. Qualified adjusted history is representable but not admissible for this plan's **unadjusted** target. Affected/unknown/overlapping/missing coverage excludes; no silent adjustment. Empty actions are not proof of no actions. |
| Maturation | Caller-supplied target session, due time, policy reference and historically known evidence. Deadline cannot precede target close. Missing input produces `MATURATION_UNQUALIFIED`; no invented maturity deadline or new label policy. |

Bounds: 8,192 supplied bars, 4,096 requested reference slots, 128 native schedule
segments of at most 64 sessions (8,192 total), and 8,192 action/maturation
records each. Native target/schedule invariants and aware-time rules also apply.

### Daily bars and absent/corrupt rows

Each row retains a logical row ID, session ID/date, canonical instrument,
provider security ID, exact source-decimal OHLC, integer volume, finality and
source evidence. Positive finite OHLC with `low <= open,close <= high` is
required; volume must be nonnegative and fit a signed 64-bit integer. A2 float
projection must remain finite and positive. No corrupt float-to-decimal repair.

Missing values, invalid envelopes, invalid session mappings, negative volume,
unfinalized bars and missing provenance remain reportable with row-level
reasons. Nonfinite scalars, floats in exact-price fields, bool-as-number,
fractional volume, impossible dates, naive clocks and malformed contracts fail
strict admission before producing a qualification report. This distinction is
intentional: structurally invalid input is not silently converted into data.

Chronological disorder blocks instead of being silently sorted. Identical
duplicates retain every row diagnostic but count the canonical session once,
as specified by the plan; differing values **or provenance** are conflicting
duplicates and exclude affected observations. Required missing sessions are
explicit; rolling windows never compress gaps or invent bars.

## 5. PIT clocks, observation identity and labels

For each requested reference session `t`:

- information cutoff = supplied scheduled close + 30 minutes;
- simulated as-of = cutoff + 5 minutes, strictly before next eligible open;
- computation/assessment time = explicit actual operation time, never backdated;
- every bar, master, calendar/exception, action and maturation dependency must
  be available/acquired/admitted by that cutoff under `CAPTURED_AS_KNOWN`;
- today-downloaded historical prices cannot acquire invented historical
  availability. Missing semantics or late revisions block the affected row.

All instants reject naive input, accept other zones and normalize using
`ZoneInfo("Asia/Kolkata")`; JSON emits `+05:30`. Source timezone remains explicit.
Date-only session/coverage fields serialize as ISO dates, including dates in
rejected nested instrument identities; FF-0 canonical hashing is unchanged.

The observation preserves target/subject/version, reference session, exact
reference/target window, cutoff/as-of, feature schema, raw input fingerprint,
eligibility and reasons. Its native `ff-observation:` ID is the **unchanged**
target/window/cutoff/as-of projection. A separate observation fingerprint adds
feature/eligibility identity; a stable slot ID keeps blocked requests visible
when a valid native window cannot yet be built. No invented valid observation
ID is assigned to such a slot.

`Y_t` remains the accepted next-session close-direction target, including exact
ties as class 0. FF-1.1 emits **label-ready windows only**: `label=None`,
`NOT_RESOLVED_FF1_1`. A missing future terminal price is not substituted into
features. Missing next-session schedule or maturation is explicit absence.
Synthetic up/down/tie checks invoke existing FF-0 Ground Truth through its
native fixture helper; there is no second target comparator or empirical
outcome journal implementation.

## 6. Exact feature schema and no leakage

ID/version: **`ff1.reliance.a2_daily_five/1.0`**; envelope schema `2.0`.
Derivation version: `A2_PROJECTOR_1.0`; policy:
`FF1_1_QUALIFICATION_1.0`. Fixed order:

| Name | Existing A2 request | Formula / unit | Required inputs |
|---|---|---|---|
| `ret_1` | `return.log`, bars=1 | `ln(C_t) - ln(C_(t-1))`; log ratio | 2 closes |
| `ret_5` | `return.log`, bars=5 | `ln(C_t) - ln(C_(t-5))`; log ratio | 6 closes |
| `sma20_distance` | `trend.distance_from_sma_percent`, period=20 | `100 × (C_t − mean(C_(t-19)..C_t)) / mean(C_(t-19)..C_t)`; percent | 20 closes |
| `realized_vol_20` | `volatility.realized`, bars=20, annualization_factor=252 | Sample standard deviation of 20 one-session log returns × `sqrt(252) × 100`; percent | 21 closes |
| `relative_volume` | `volume.relative`, bars=20 | `V_t / mean(V_(t-20)..V_(t-1))`; ratio, reference excluded from baseline | 21 volumes |

These are the accepted plan's formulas, not tuned implementation alternatives.
No additional features, global statistic, scaler or imputation. Zero returns,
zero variance and zero current volume remain valid factual numbers. An all-zero
volume denominator is explicitly ineligible.

The projector receives only the preceding 20 qualified sessions plus reference,
with no target price or future bar. It also checks the exact final bar time,
21-bar window and cutoff. Its `FRESH` context means qualified at the historical
reference, not a claim of present-day market freshness. The projector alone is
not a rights/source authorization API; callers use the Evaluation qualifier.

## 7. Accounting, verdicts and fingerprints

`requested_observations = eligible_observations + excluded_observations`.
Every request appears once. Reason counts count affected observations, not
duplicate capture rows; one observation can contribute to multiple reasons.
All raw supplied rows have separate diagnostics. No silently dropped denominator.

Non-blocking warm-up and missing terminal-next-session slots remain excluded
and counted. Other blocking gates yield one or more `HOLD_DATA_RIGHTS`,
`HOLD_DATA_QUALITY`, `HOLD_SECURITY_IDENTITY`, `HOLD_CALENDAR`,
`HOLD_CORPORATE_ACTIONS`, `HOLD_PIT_PROVENANCE`. An empty eligible population is
HOLD. Successful authored data is `SYNTHETIC_ENGINEERING_ONLY`; supplied
`QUALIFIED_CAPTURE` assertions can yield `QUALIFIED_FOR_FF1_RESEARCH`, never a
claim that this pass obtained such empirical data. Both retain
`empirical_fitting_authorized=False`, `NO_LEARNING_GRANT_FF1_1`.

| Identity | Material content |
|---|---|
| Dataset fingerprint | Entire normalized supplied envelope: source/capture, rights, mapping, calendar, action/maturation, coverage, row identities/content and requested population |
| Qualification seal | Dataset hash, explicit policy/version, source/rights/security/calendar/action pins, schema, all row/observation outcomes/counts and actual assessment time |
| Feature-schema fingerprint | Ordered five names, native requests/parameters, formulas/units/lookbacks, missing/action/knowledge policies and derivation version |
| Local feature input/vector | Exact local rows and sessions, local action and calendar/policy/notice pins, source/rights/security identity, schema and native A2 results |
| Observation / feature-set fingerprint | Native observation or blocked slot, raw input pin, schema, eligibility/reasons and feature values/results; excludes actual computation time |

Identical content reproduces hashes. Material source, rights, mapping, calendar,
action, data or schema changes cannot silently reuse identity. Changed future
target prices do not change an earlier observation/vector; they do change the
full dataset/report. A new actual assessment timestamp changes the report seal
but not identical feature content. Hashes are content identity, not signatures.

## 8. Local ingestion, serialization and isolation

`load_research_dataset(Path(...), dataset_id=...)` is an **internal Python seam**,
not a new CLI/public capability. It reuses FF-0's strict JSON/local reader:
explicit local file only, 1 MiB maximum, regular single-link file, symlink and
unsafe-path rejection, duplicate-key/nonfinite JSON rejection. No default
corpus, URL fetch, provider SDK, `.env` discovery or CSV/provenance guessing.
Canonical field names are required. Extra source-row columns are ignored;
unknown envelope fields reject. Original native source artifacts must remain
separately retained/pinned; ignored columns do not become features.

For serialization use `canonical_json(dataset_or_report)` and reconstruct with
the corresponding `model_validate_json`. Semantic collections are tuples;
JSON arrays and normal list inputs work. Frozen fields reject replacement;
native extensible metadata does not gain deep immutability. Report
reconstruction validates counts, policy/schema, observation clocks/identities
and seal. No automatic writes, overwrites, shared store or experiment tracker
is introduced; this slice takes the task's **serialization** option. Callers
remain responsible for permitted immutable retention of resulting bytes.

No dependencies were added. Fresh-process tests deny optional ML/provider SDK
imports, execute qualification and verify the unchanged nine-capability public
catalog. Additional tests prohibit file/network/process I/O during qualification.
No live provider/broker call, fitting method, model token, trained artifact or
external acquisition occurs.

## 9. Synthetic acceptance and validation

The authored 32-session case has **32 requested / 11 eligible / 21 excluded**:
20 warm-up slots plus one terminal slot without a next session. This is fixture
arithmetic, not empirical sample support or NSE calendar certification.

Tests cover all 14 requested fixture categories: clean sequence, exact lookback,
missing and duplicate sessions, invalid OHLC, zero/missing volume, unresolved
actions, wrong/ambiguous security, leakage attempts, insufficient history and
native class-1/class-0/exact-tie labels. Additional cases cover qualified adjusted
basis rejection, holidays/special sessions, revisions, rights scope/expiry,
strict admission, immutable round trips, fingerprints, blocked populations,
reader bounds and import/I/O isolation.

| Validation | Result |
|---|---|
| `.venv/bin/pytest -q tests/unit/forecasting/test_research_qualification.py tests/unit/forecasting/test_research_isolation_edges.py` | **102 passed** (14.91s); includes fresh-process import and no-I/O checks |
| `.venv/bin/pytest -q tests/unit/forecasting tests/unit/evaluation/test_forecast_truth.py tests/unit/evaluation/test_forecast_linkage.py --ignore=tests/unit/forecasting/test_research_qualification.py --ignore=tests/unit/forecasting/test_research_isolation_edges.py` | **416 passed** (44.25s), existing FF-0 regression tests |
| `.venv/bin/pytest -q tests/acceptance/ff0` | **28 passed** (31.04s), unchanged semantic acceptance corpus |
| `.venv/bin/pytest -q tests/unit/data tests/unit/context tests/unit/features tests/unit/source_semantics` | **1,056 passed** (14.12s) |
| `.venv/bin/pytest -q --tb=short` | **3,023 passed** (301.27s), no failures or skips |
| `.venv/bin/python -m compileall -q src scripts` | PASS |
| `.venv/bin/ruff check src tests scripts` | PASS |
| `.venv/bin/mypy src tests` | PASS, **608 source files** |
| Local documentation-target check | PASS: **10 Markdown files, 604 local file targets, zero missing** (file targets, not remote URLs or fragment anchors) |
| `git diff --check` | PASS; new-file whitespace separately checked |

These overlapping suites are not additive counts. No integration gate required
live provider calls. HEAD and baseline tags remain unchanged; no existing
`src/`, `tests/` or dependency file was modified (all implementation/tests are additive).

## 10. Empirical blockers, limitations and next gate

**EMPIRICAL_FITTING_AUTHORIZED = NO** because no real rights/retention evidence,
qualified RELIANCE captures, historical security/calendar/action provenance or
governed fitting grant has been supplied. Broad historical OHLC alone is not
enough: today-downloaded history fails the plan's original-knowledge clocks.
The plan's proposed Nov-2017–Jan-2026 coverage is not claimed to exist locally.

No architecture deviation. Minimal implementation choices are explicit supplied
maturation inputs, typed additive schema-2 envelopes, label-ready rather than
empirical-label construction, canonical serialization rather than a second
store, and an internal JSON reader rather than extending the frozen FF-0 CLI.
Unknown authority cannot be resolved by relabeling synthetic fixtures.

Next exact prompt title:

**TIAF A7 / FF-1.1A — EMPIRICAL DATA RIGHTS AND QUALIFICATION EXECUTION**

No direct advance to FF-1.2 while fitting remains unauthorized. A separate
future grant/review is required even if supplied data mechanically qualifies.

Recommended commit after acceptance (not executed):
`feat(a7.ff1.1): implement data qualification and feature schema`.
No tag. No commit/tag/push performed in this pass.
