# TIAF A7 / FF-1.1A — Empirical data rights and qualification execution

## 1. Decision and stop boundary

**HOLD_FF1_1A_QUALIFICATION**

**EMPIRICAL_FITTING_AUTHORIZED = NO**

Recorded: **2026-09-19T23:23:01.962328+05:30**, Asia/Kolkata.

The attempt stopped at empirical-input preflight. No user-supplied empirical
dataset path or rights document was provided, and no RELIANCE daily-history
archive was identified in the inspected repository. This is not a failed
OHLCV-quality result, a zero-row dataset, a completed empirical qualification,
or evidence that no dataset exists elsewhere on the user's computer.

No live acquisition was authorized or attempted. No provider/broker calls,
Logistic/scaler fitting, empirical forecasts, paired metrics or candidate model
artifacts were produced. Existing FF-1.1 semantics remain unchanged.

Entry HEAD was clean at `2eb522c1dc978c1f267d4ad6c9cf7d0b287ad9b8`
(accepted FF-1.1). FF-0 remains at
`e5283c9eaa4294bd236186d663335efdf7dab236`; A6 remains at
`6dc2ff304aae0e87540260b092919bb91e4d4189`. Their baseline tags are unchanged.

## 2. Evidence inventory and source identity

Inspected tracked and ignored project artifact paths, including `data/`,
`examples/`, fixtures/corpora and documentation inventories. Excluded virtualenv,
VCS metadata, tool caches and secrets. No `.env` or credentials were opened.
No external data-library path was supplied; arbitrary home/Downloads contents
were not searched. Only the named task brief was read from Downloads.

| Observed item | Finding | Why it is not the requested dataset |
|---|---|---|
| `data/instrument_master/dhan/api-scrip-master-detailed.csv` | Existing ignored Dhan-format instrument master, 33,964,897 bytes | Security metadata, not daily OHLCV or historical capture lineage |
| [FF-1.1 fixture guide](../tests/fixtures/forecasting/ff1_1/README.md) | Authored 32-session programmatic fixture | Synthetic values/rights, not empirical support |
| [FF-0 fixtures](../tests/fixtures/forecasting/ff0/README.md) | Synthetic miniature captures | No empirical daily archive or rights proof |
| [A3.9 capture guide](../tests/fixtures/opportunity_intelligence/README.md) | Explicitly synthetic compressed captures | Not recovered live historical data |
| Prior live-study documents | Reports/code references | A smoke-test result is not a retained PIT-qualified daily archive |

The master has a matching row: NSE / E / EQUITY / EQ, symbol RELIANCE,
provider security ID `2885`, ISIN `INE002A01018`. This is an observed local
mapping, **not range-qualified historical identity**. Other RELIANCE-named
companies, venues and derivatives were not merged.

Master SHA-256:

`6e65523933d51e6aad54cb4b3cff4f27708fe0e4710a8c03f239da666f674fd2`

File modification time is not source publication, acquisition or trusted
historical admission proof. Dhan attribution comes from local path/format,
not independent authenticity verification.

Actual empirical provider, dataset ID, content/provenance fingerprint, coverage,
source timezone, frequency, adjustment basis and historical mapping are unknown.
Dhan is the plan's candidate source, not a dataset acquired in this attempt.

## 3. Rights gate

No official terms/license, subscription/entitlement contract or explicit scoped
user rights evidence was supplied for an identified dataset. No public-provider
terms/legal review was performed after the missing-input stop: no dataset or
entitlement was identified against which to establish scope. This is absence,
**not a determination that the provider denies these uses**.

| Required use | Evidence reference | State |
|---|---|---|
| Local research | None | UNKNOWN |
| Model training | None | UNKNOWN |
| Derived-feature storage | None | UNKNOWN |
| Retained evaluation evidence | None | UNKNOWN |
| Replay-evidence retention | None | UNKNOWN |

Result: **HOLD_DATA_RIGHTS**. Provider access, local possession, repository
source-code licensing and synthetic fixture grants do not establish dataset
permissions. Supply non-secret entitlement/document references, use/scope
and retention/expiry constraints; no API credentials are needed.

## 4. Blocking-gate matrix

All twelve gates block fitting. NOT_RUN/UNKNOWN is not PASS.

| Gate | Evidence | Status | Blocking? | Reason |
|---|---|---|---|---|
| Rights | No scoped documents | HOLD_DATA_RIGHTS | Yes | Five permissions unknown |
| Source provenance | No empirical captures | HOLD_PIT_PROVENANCE | Yes | Dataset/origin/version and original capture lineage absent |
| Security identity | Local master row only | HOLD_SECURITY_IDENTITY | Yes | No historically dated coverage/mapping |
| Daily frequency | Master has no daily bars | NOT_EVALUATED | Yes | Missing empirical dataset |
| OHLCV quality | No daily rows | NOT_RUN | Yes | Cannot count valid/invalid/duplicate bars |
| Calendar | No qualified historical schedule/exceptions | HOLD_CALENDAR | Yes | No authoritative grid; no weekday substitute |
| Corporate actions | No basis/coverage records | HOLD_CORPORATE_ACTIONS | Yes | Action and price-basis handling unqualified |
| PIT availability | No original historical clocks | HOLD_PIT_PROVENANCE | Yes | Availability/acquisition/admission by cutoff unproved |
| Feature derivation | Schema exists; empirical inputs absent | NOT_RUN | Yes | No qualified 21-session window |
| Label construction | No qualified endpoints | NOT_RUN | Yes | No empirical labels; synthetic journal boundary preserved |
| Fold feasibility | No qualified rows/classes/grid | HOLD_FOLD_FEASIBILITY | Yes | Support/purge/embargo/BaseRate counts unknown |
| Leakage audit | No empirical dependency closure | NOT_RUN | Yes | No empirical leakage-freedom claim; no confirmed leakage finding |

### PIT and corporate-action policy remain unchanged

The [FF-1 plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md),
[A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md) and
[FF architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md) require
**CAPTURED_AS_KNOWN**: original availability, acquisition and trusted admission
must precede each historical cutoff. Cutoff remains scheduled reference close
+ 30 minutes; simulated as-of is cutoff + 5 minutes and before next eligible
open. Actual computation time remains separate.

A fresh download of old prices does **not** establish historical acquisition
or admission. Documented EOD timing or a conservative availability lag alone
cannot waive those clocks. If suitable archives do not exist, a different
historical-vintage policy or prospective study requires separate architecture
authorization, not a repair invented in this execution pass.

The target remains same-basis **unadjusted** close. Adjusted history may be
representable but is not admissible under this policy. Affected/unknown action
windows remain excluded. No silent adjustment or retroactive action knowledge.

### Label boundary identified during inspection

[FF-1.1](TIAF_A7_FF1_1_DATA_QUALIFICATION_FEATURE_SCHEMA_IMPLEMENTATION.md)
produces label-ready observations with `label=None`, not empirical journals.
The existing [Ground Truth resolver](../src/tiaf/evaluation/forecast_truth.py)
returns [OutcomeJournalEntry](../src/tiaf/evaluation/forecast_contracts.py),
whose v1 guard rejects empirical sources with `EMPIRICAL_OUTCOME_NOT_ENABLED`.

This is a preserved scope boundary, not a defect repaired here. Future empirical
label integration needs explicit authority consistent with the plan's additive
research-version boundary and must reuse the one truth definition. Real data
must never be relabeled SYNTHETIC_FIXTURE. No second comparator, new empirical
label contract or FF-1.2 implementation was added.

## 5. Population, features, labels and folds

**N/E = not evaluated; JSON null, not a measured zero.** No dataset means no
known requested-session denominator.

| Requested measure | Result |
|---|---|
| Actual coverage; raw/qualified/invalid daily rows | N/E |
| Invalid-row reasons; missing/duplicate sessions | N/E |
| Requested observations | N/E |
| Feature-eligible / label-eligible / paired-ready observations | N/E |
| Excluded observations and per-reason counts | N/E |
| Positive / zero / unavailable labels | N/E |
| Feature sanity statistics and nonfinite counts | N/E |
| Empirical feature-set fingerprint | None |
| Dataset content/provenance fingerprint | None |

Measured preflight activity: **0 empirical daily-history files found within
the repository, 0 empirical qualifier invocations, 0 empirical rows processed,
0 empirical feature/label calculations**. These are operation counts, not
population counts.

Feature schema remains **`ff1.reliance.a2_daily_five/1.0`**: ret_1, ret_5,
sma20_distance, realized_vol_20, relative_volume. No scaling or imputation.

| Annual test fold | Training/class support | Feature/label/paired-ready support | Purge/embargo/BaseRate counts | State |
|---|---|---|---|---|
| 2021 | N/E | N/E | N/E | NOT_EVALUATED |
| 2022 | N/E | N/E | N/E | NOT_EVALUATED |
| 2023 | N/E | N/E | N/E | NOT_EVALUATED |
| 2024 | N/E | N/E | N/E | NOT_EVALUATED |
| 2025 protected holdout | N/E | N/E | N/E | NOT_EVALUATED; unopened |

Requirements, not measured support: expanding training from 2018, 21 input
sessions for 20 returns, at least 500 training rows and 100 per class, full
predecessor-session embargo, cutoff-safe purge, and last-20 scheduled-transition
BaseRate support without invalid-row backfill. Proposed Nov-2017–Jan-2026
coverage is not claimed to be present.

Empirical target-row, post-cutoff, preprocessing, action-vintage, fold/label and
file-order leakage checks are NOT_RUN. Synthetic tests prove mechanics only.

## 6. Content-addressed stopped-at-preflight artifact

Artifact ID: `qualification-attempt:ff1-1a-20260919-232301`.

[Qualification attempt JSON](qualification_records/ff1_1a/qualification_attempt_4f6d2a998b241ca04e99757791545315482606381af170ff61d1c948c977b833.json)

Qualification-attempt fingerprint:

`4f6d2a998b241ca04e99757791545315482606381af170ff61d1c948c977b833`

The record contains evidence inventory/governing-document hashes, null dataset
identities/counts, rights states, all gates, fold requirements, stop reason,
no-fitting counters and validation results. It is an **audit artifact**, not a
fabricated EmpiricalDatasetQualification, rights certificate, dataset/feature
fingerprint or fitting grant.

Fingerprint = existing FF canonical SHA-256 of the JSON object excluding
`qualification_fingerprint`; the filename includes that hash. Preserve this
content-addressed attempt and create a new file/reference for a new attempt.
Hash verification detects edits; OS-enforced write protection and authenticated
source rights are not claimed. No new runtime contract or store was introduced.

## 7. Validation and no-fitting verification

| Check in this pass | Result |
|---|---|
| FF-1.1 qualification/schema/isolation tests | **102 passed**, 17.59s |
| FF-0 unit regressions, excluding FF-1.1 tests | **416 passed**, 45.27s |
| Feature and source/provenance tests | **610 passed**, 13.54s |
| FF-0 acceptance corpus | **28 passed**, 31.60s |
| `.venv/bin/python -m compileall -q src scripts` | PASS |
| `.venv/bin/ruff check src tests scripts` | PASS |
| `.venv/bin/mypy src tests` | PASS, 608 files |
| No-ML-import and no-I/O isolation | PASS, included in targeted tests |
| Audit-artifact integrity and governing/input hashes | PASS; all 12 gates block; empirical counts remain null |
| Documentation links | PASS: 2 Markdown files, 120 local file targets, zero missing (no remote URL or anchor claims) |
| `git diff --check` and new-file whitespace checks | PASS |
| Empirical qualification/feature/label/fold tests | NOT_RUN: dataset/rights/provenance absent |
| Full repository suite | NOT_RERUN: preflight stop and documentation/audit-only changes; runtime/tests unchanged |

Previous FF-1.1 **3,023 passed** is historical evidence, not a new full-suite
result. Test groups overlap and are not additive. No new tests were added to
pretend empirical execution occurred. Existing fixtures retain synthetic basis.

No sklearn/scaler fit, empirical candidate artifact, model walk-forward, paired
forecast metric or live acquisition occurred. Training libraries are blocked
in the fresh-process isolation test. Synthetic BaseRate test artifacts are not
empirical Logistic candidates. The audit JSON is a documentation record, not
runtime market data; it contains no prices, credentials or entitlement secrets.

## 8. Missing inputs and exact next step

Supply explicit local paths/artifact IDs for:

1. RELIANCE NSE cash daily OHLCV: exact source-decimal prices, actual coverage,
   native captures and price-basis declaration.
2. Scoped rights for research, training, derived-feature storage, evaluation
   retention and replay retention; non-secret documents/entitlement references.
3. Historical security mapping, qualified calendars/exceptions and complete
   corporate-action coverage.
4. Original availability, acquisition, trusted admission and revision evidence
   satisfying CAPTURED_AS_KNOWN; no invented historical timestamps.
5. Supplied maturation policy/evidence and independent protocol/holdout/job
   admissions before their dependent operations.

Exact next prompt title:

**TIAF A7 / FF-1.1A — LOCAL RELIANCE DATASET AND RIGHTS/PIT EVIDENCE PROVISIONING**

Do not advance to FF-1.2. This is an unresolved-input gate, not authorization
to download data or implement more runtime. Git recommendation: no completed
qualification checkpoint or tag; retain the HOLD evidence for review.
No commit/tag/push.

Files created: this record and its JSON audit artifact. The milestone ledger
gains a HOLD link. Prior acceptance records, architecture, source code, tests,
dependencies and dataset files remain unchanged.
