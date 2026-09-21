# TIAF A7 / FF-1.1A — Empirical qualification rerun

Assessment: **2026-09-21T12:24:29.146355+05:30**, Asia/Kolkata.

```text
HOLD_FF1_1A_QUALIFICATION
EMPIRICAL_FITTING_AUTHORIZED = NO
HOLDOUT_STATUS = SEALED
LEAKAGE_AUDIT = HOLD
```

The download succeeded and its integrity remains valid. The concrete dataset
does **not** yet satisfy scientific admission. Rights uncertainty is admitted
with warning; it is not the blocker. Historical knowledge/revision provenance,
source-decimal authority, a qualified historical NSE calendar, complete
corporate-action/price-basis evidence, and historical identity remain unresolved.

**Execution boundary:** this rerun executed the actual dataset's offline
integrity, numeric-bar, rights/configuration and current-resolver checks, followed
by scientific gate review. It did **not** invoke the full native
`ResearchQualificationRuntime.qualify` with empirical inputs: the mandatory
schedule/provenance envelope cannot be truthfully constructed from this package.
No fake sessions or historically captured decimals were supplied just to obtain
a runtime report. Features, labels and realized fold qualification stopped at
admission. Their unmeasured counts are **unknown, not zero**.

## 1. Scope, baseline and source review

HEAD remains `2eb522c1dc978c1f267d4ad6c9cf7d0b287ad9b8`.
A6 remains `tiaf-a6-baseline` at
`6dc2ff304aae0e87540260b092919bb91e4d4189`; FF-0 remains
`tiaf-a7-ff0-baseline` at `e5283c9eaa4294bd236186d663335efdf7dab236`.
Existing rights-policy edits and earlier HOLD/provisioning records are preserved.
This pass changes no runtime implementation, policy, dependency or capability.

Reviewed before the offline checks:

- [Accepted FF-1 plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md),
  especially §§3–5 and 9–10: empirical capture, five features, clocks and holdout.
- [FF-1.1 implementation](TIAF_A7_FF1_1_DATA_QUALIFICATION_FEATURE_SCHEMA_IMPLEMENTATION.md):
  supplied-input qualification, exact-decimal boundary and label-ready-only seam.
- [Rights-policy revision](TIAF_A7_FF1_1A_RIGHTS_POLICY_REVISION_AND_DATA_PROVISIONING.md):
  WARN_ONLY is not a vintage waiver or an empirical Outcome Journal extension.
- [TI-native provisioning record](TIAF_A7_FF1_1A_TI_NATIVE_RELIANCE_TEST_DATA_PROVISIONING.md),
  all four sidecars, the private CSV and cached master.
- [Source/provenance architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md):
  source versus provider, precision, revisions, knowledge and actual acquisition.
- Existing [qualifier](../src/tiaf/evaluation/forecast_qualification.py),
  [research contracts](../src/tiaf/evaluation/forecast_research_contracts.py),
  [schedule/truth contracts](../src/tiaf/evaluation/forecast_contracts.py),
  [Ground Truth](../src/tiaf/evaluation/forecast_truth.py),
  [feature schema](../src/tiaf/forecasting/research_contracts.py),
  [Dhan resolver/master](../src/tiaf/data/providers/dhan/instrument_master.py)
  and their existing qualification/isolation/calendar/action/security tests.

The local `data/` inventory contains only the provisioned package and current
instrument master. No historical schedule/exception, original-capture archive,
source-decimal companion or complete action-coverage artifact was found there.
No unrelated home-directory search, new Dhan call or master refresh was made.

## 2. Concrete dataset and integrity

Dataset:
`/home/cbiswas/Documents/Work/TradingIntelligence/data/ff1/reliance/reliance_daily_ohlcv.csv`

| Item | Observed result |
|---|---|
| Provider / path | Dhan via existing TI `MarketDataProvider.get_historical` → `DhanMarketDataProvider` → `HttpxDhanTransport` |
| Endpoint / frequency | `/v2/charts/historical` / `1d` |
| Identity | RELIANCE / NSE / NSE_EQUITY / EQUITY; dynamically resolved provider ID `2885` |
| Acquisition kind | `FRESH_HISTORICAL_DOWNLOAD` |
| Acquisition start | `2026-09-21T12:07:50.682638+05:30` |
| Acquisition end | `2026-09-21T12:07:50.995917+05:30` |
| Requested coverage | 2017-11-01 through 2026-01-31; API end 2026-02-01 exclusive |
| Delivered coverage | **2017-11-01 through 2026-01-30** |
| Raw rows / CSV bytes | **2,045 / 99,118** |
| Columns | Exactly `date,open,high,low,close,volume` |
| Encoding / ordering | UTF-8, LF, ascending ISO dates, no duplicates |
| Manifest integrity | All four semantic seals; companion byte hashes; CSV hash PASS |
| Git / retention | Five local files remain Git-ignored/untracked, mode `0600`; no data staged |
| Secret fields | Existing `validate_no_secrets` passed for all sidecars |
| New market-provider requests in this pass | **0** |

CSV byte SHA-256:
`d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6`

Provisioning semantic fingerprint:
`c54cbf1c7ba1d11a8166aec3a9c10a72efbc95446cc5cc240692fd1b6410e272`

The new audit pins the individual CSV/sidecar byte hashes, semantic manifest
identities, governing documents and source-code versions. It does not modify
the original package. There is no retained raw HTTP response; the normalized
series fingerprint is not an original response-byte digest.

## 3. Rights and security identity

| Rights dimension | Result |
|---|---|
| Actual evidence | `UNVERIFIED` |
| COLD enforcement | `WARN_ONLY` |
| Admission | `ADMITTED_WITH_WARNING` |
| Warning | `RIGHTS_NOT_APPROVED_RESEARCH_ONLY` |
| Configuration fingerprint | `2ca6488c4b09e6437e246f91bfc227c6376c01849498d06df2fb038b5a64d981` |
| Recomputed admission/config versus both manifests | PASS |

No VERIFIED_ALLOWED assertion or new entitlement evidence was created. Unknown
rights are not a hard blocker under the accepted default. Explicit denial would
still HOLD. Policy admission is neither a legal determination nor a fit grant.

The native resolver was rerun **offline** over the unchanged local master with
download and socket access denied. It returned one `UNIQUE_NORMALIZED`, GOOD
RELIANCE/NSE cash-equity match, ID **2885**, ISIN **INE002A01018**, matching the
source/security/request manifests. No futures, options, BSE or mixed identity
was substituted. This confirms the **current mapping**, not historical validity.

Master SHA-256:
`6e65523933d51e6aad54cb4b3cff4f27708fe0e4710a8c03f239da666f674fd2`.
Its native observation clock is `2026-09-05T23:50:59.627632+05:30` (local cache
mtime); the rerun check occurred at the assessment time above. Neither is proof
of a master known in 2018–2025. The accepted qualifier also requires dated
coverage and cutoff-safe mapping evidence. Therefore current identity PASS
coexists with **HOLD_SECURITY_IDENTITY** for historical qualification. This is
an evidence gap, not evidence that the resolved instrument is wrong.

## 4. Bar quality and calendar

| Bar check across the delivered file | Count / result |
|---|---|
| Raw rows | **2,045** |
| Valid lexical/numeric rows | **2,045** |
| Invalid lexical/numeric rows | **0**; reason counts `{}` |
| Nonfinite or nonpositive OHLC | **0** |
| Invalid OHLC envelope | **0** |
| Missing fields / invalid volume | **0 / 0** |
| Duplicate dates | **0** |
| Nonchronological or out-of-window rows | **0** |
| Scientifically qualified rows | **Unknown / not established** |

CSV lexical prices were parsed using TI's `exact_decimal` for finite/positive
and envelope checks; volume was explicitly checked as a nonnegative integer
within the native bound. There was no repair, rounding or row coercion. This
verifies the numbers **as exported**, not their original source precision.
The file was produced from existing A1 floats; converting its strings to Decimal
does not restore discarded source lexical evidence. The plan's source-decimal
close requirement is still **HOLD_SOURCE_DECIMAL_AUTHORITY**. Completed-bar
finality/revision authority is also not certified merely by old dates.

Native FF-1 calendar logic consumes `QualifiedSessionSchedule` records with
authority, exception and historical knowledge references; it does not generate
an authoritative NSE calendar from weekdays. The supplied package has none.
An empty calendar is not a valid `EmpiricalDataset` input. The date-only CSV
cannot establish scheduled opens/closes or special-session eligibility.

| Calendar measure | Result |
|---|---|
| Supplied distinct date rows | **2,045** |
| Expected qualified sessions | **Unknown** |
| Missing sessions | **Unknown**, not zero |
| Extra/non-session rows | **Unknown**, not zero |
| Duplicate date rows | **0** |
| Unresolved anomaly count | **Unknown** |
| Verdict | **HOLD_CALENDAR** |

No guessed weekday grid, gap filling, weekend exclusion or silently compressed
rolling window was used. Missing-session materiality cannot be decided without
the expected schedule. Once qualified, affected 21-session windows must remain
explicitly ineligible; a missing target must never become a negative label.

## 5. Corporate actions and price basis

**HOLD_CORPORATE_ACTIONS.** Source/provisioning metadata explicitly says UNKNOWN
for price basis and corporate-action evidence. The reviewed
[Dhan daily-history specification](https://dhanhq.co/docs/v2/historical-data/)
describes OHLC/volume/timestamp fields but does not supply the adjustment,
revision or source-precision certification needed to resolve these gates.
No price-pattern inference was performed.

There are material actions inside coverage. RIL's Board report records the
financial-services demerger with record date **2023-07-20**.
[RIL 2023–24 annual report](https://www.ril.com/sites/default/files/2024-08/RIL_ANNUALREPORT_2023-24.pdf).
The indexed primary-source excerpt was reviewed; the full PDF could not be
opened by the web reader because of its size. RIL's allotment notice confirms
a **1:1 bonus**, record date **2024-10-28**.
[RIL bonus allotment notice, 2024-10-30](https://www.ril.com/sites/default/files/2025-03/Letter_to_shareholders.pdf).

These are **non-exhaustive, contemporary review findings**, not a complete
action calendar, exchange ex-date schedule or PIT-admitted historical evidence.
No source PDF is archived in the qualification package. No claim that these
are the only actions, or that all other dates are unaffected, is justified.

Engineering implication: an unqualified action/basis change can contaminate
cross-boundary one/five-session returns, the 20-session SMA distance, 20-return
volatility and reference/target close comparisons. Volume adjustment conventions
also matter to relative volume. That identifies possible dependencies, not a
measured effect on this series. No return or holdout outcome was calculated.

Deleting just the two named dates would not establish safe input windows or
target pairs. A valid exclusion policy needs complete action coverage, qualified
effective-session mapping and historically eligible evidence over all relevant
dependencies. None is available here. Excluding all unknown windows would leave
no qualified empirical population; it would not produce a successful
QUALIFIED_WITH_EXCLUSIONS verdict. No local price adjustment was made.

## 6. PIT policy and observation clocks

The accepted policy remains **CAPTURED_AS_KNOWN**. For a qualified reference
session, native code uses:

```text
information_cutoff = scheduled reference close + 30 minutes
simulation_as_of   = information_cutoff + 5 minutes
feature dependency available/acquired/admitted <= information_cutoff
information_cutoff <= simulation_as_of < target session open
actual assessment/computation/acquisition clocks remain separate
```

Do not replace scheduled closes with the provider's daily midnight boundary or
invent fixed hours for historical/special sessions. All timestamps remain aware,
normalized with `ZoneInfo("Asia/Kolkata")`, and serialize with `+05:30`.

Actual acquisition in September 2026 is later than every 2018–2025 observation
cutoff. Source availability/revision and original admission evidence are not
present. Today-downloaded historical values therefore cannot satisfy the current
policy. The actual acquisition remains unchanged and is never backdated.

The brief permits considering an explicit conservative SIMULATED policy. A
close-plus-30-minute assumption alone would not establish which revisions or
adjustments existed then, and does not satisfy the accepted acquisition/admission
checks. No defensible source-specific alternative was established from the
provided metadata or reviewed specification. FF-1 plan §3.1 and rights revision
§4 require separate versioned scientific review of a different vintage profile.
This pass did not add a new profile, relax the feature schema's literal policy,
or claim `SIMULATED_ONLY` itself grants a historical-vintage waiver.

Verdict: **HOLD_PIT_PROVENANCE**. No empirical feature-clock inequalities are
reported as passed without real qualified session/evidence inputs.

## 7. Population, features, labels and protected holdout

| Accounting measure | Result |
|---|---|
| Raw / numerically valid / numerically invalid rows | **2,045 / 2,045 / 0** |
| Warm-up-range supplied rows, 2017 | **42** (date presence, not certified sessions) |
| Supplied reference-date slots, 2018–2025 | **1,983** |
| Terminal-coverage supplied rows, January 2026 | **20** |
| Qualified rows / complete requested observation grid | **Unknown / unknown** |
| Feature-eligible / label-eligible / paired-ready observations | **Unknown / unknown / unknown** |
| Excluded qualified observations | **Unknown**; no valid observation IDs/grid constructed |
| Supplied date slots blocked at admission | **1,983**, each NOT_EVALUABLE |
| Positive / zero / unavailable labels | **Unknown / unknown / unknown** |
| Feature nonfinite count / min/max/sanity summaries | **Not computed** |
| Feature-set fingerprint | **None**, no feature vectors constructed |
| Qualified observations admitted / vectors built / labels built this attempt | **0 / 0 / 0** (execution counts, not unknown scientific populations) |

Date-slot accounting is exhaustive for **supplied CSV dates**, not an authoritative
exchange denominator. For each date in inclusive 2018-01-01..2025-12-31, the
deterministic audit disposition is NOT_EVALUABLE, primary reason HOLD_CALENDAR;
contributing reasons are PIT provenance, corporate actions, historical security
identity and source-decimal authority. Each reason affects all **1,983** supplied
slots at this gate; reason counts overlap and must not be added. The canonical
hash of the sorted date-only slot list is
`2c67a73a8e52ecc58a2442641d543253adde4fdf7483e405b509d10cb7ab3766`.
Dates absent from the CSV remain unknowable missing slots until the calendar is supplied.

Accepted feature schema **`ff1.reliance.a2_daily_five/1.0`** remains exactly
`ret_1`, `ret_5`, `sma20_distance`, `realized_vol_20`, `relative_volume`.
Schema fingerprint:
`521337f10dd977b523ad6a2bd073ba9f11351f8948c87beff6ec710b4e4b217a`.
This is a schema hash, **not** an empirical feature-set hash. The existing A2
projector was not invoked with empirical inputs because prerequisite gates fail.

No empirical labels were constructed. Native FF-1.1 outputs label-ready windows
only (`label=None`, `NOT_RESOLVED_FF1_1`); native FF-0 Outcome Journal rejects
empirical sources. These implemented boundaries were not widened, and no second
greater-than comparator or SYNTHETIC relabeling was introduced. The accepted
target's up/down/tie behavior continues to be covered by existing synthetic
Ground Truth regressions, not falsely claimed as empirical label counts.

**HOLDOUT_STATUS = SEALED.** The 2025 reference range contains **249 supplied
date rows**. Only date existence/counts and automated whole-file hash/schema/
boolean numeric-integrity checks were used. No 2025-specific prices, returns,
feature values, target directions, label balance, losses or outcome summaries
were exposed, and terminal January 2026 values were not used to label it.
This is outcome-access protection, not filesystem encryption. Prior independent
inspection outside this recorded workflow is not certified; later protocol
review must still establish holdout integrity. No evaluation-opening grant was used.

## 8. Fold feasibility without fitting

Protocol: **`ff1.reliance.daily_logistic_vs_b0/1.0`**.
Expanding training begins 2018-01-01. The full eligible session before each first
annual test reference is embargoed; fit cutoff is that session's open. Training
target resolution must be strictly earlier and feature/truth knowledge cutoff-safe.
Logistic requires 500 eligible training observations and 100 in each class;
BaseRate requires the last 20 eligible scheduled transitions without backfill.

| Test year | Role | Supplied earlier training-date slots, before purge | Supplied test-date slots | Qualified train/test; purge/embargo; feature/label/paired support |
|---|---|---:|---:|---|
| 2021 | Development | 743 | 248 | Unknown — NOT_EVALUABLE |
| 2022 | Development | 991 | 248 | Unknown — NOT_EVALUABLE |
| 2023 | Development | 1,239 | 246 | Unknown — NOT_EVALUABLE |
| 2024 | Development | 1,485 | 249 | Unknown — NOT_EVALUABLE |
| 2025 | Sealed holdout | 1,734 | 249 | Unknown — NOT_EVALUABLE |

These are date-only inventory counts, **not realized fold membership or support**.
Actual embargo sessions, purge counts, fit clocks, per-class counts, feature/
label-complete counts, paired-ready counts and BaseRate support all remain null.
Having more than 500 raw dates does not prove the minimum qualified support.
FF-1.1 did not implement the later walk-forward/split runtime; no new split
engine, scaler, BaseRate forecast or Logistic fit was created for this report.

## 9. Leakage audit and hard gates

**LEAKAGE_AUDIT = HOLD**, not a clean-population PASS and not an allegation of
observed fitted-model leakage. There is no admitted empirical feature/label/fold
closure over which the full scientific audit could run. Original revision and
action knowledge remain unresolved. An assumption that today's download was
historically captured would violate the accepted policy; that bypass was refused.

No target/future data entered features because no features were computed. No
global scaler/imputer, label-derived feature, fit, cross-fold join, file-order
selection or outcome-driven tuning ran. The source file remained sorted and
unchanged. Existing synthetic anti-leakage tests verify code mechanics only;
their PASS does not resolve empirical vintage uncertainty.

| Gate | Evidence | Status | Blocking? | Reason |
|---|---|---|---|---|
| Dataset integrity | CSV and all sidecar hashes/counts/schema | PASS | No | Provisioned content unchanged |
| Rights admission | Accepted config and both manifest assertions | ADMITTED_WITH_WARNING | No | UNVERIFIED under WARN_ONLY, not approval |
| Source provenance | Fresh acquisition recorded; native decimals/revisions absent | HOLD | Yes | No authoritative source-decimal or historical vintage closure |
| Security identity | Matching current native resolver/master | Current PASS; historical HOLD | Yes | No dated historical mapping/cutoff-safe master |
| Daily frequency/OHLCV quality | 2,045 rows checked | Numeric PASS | No for numeric check | Session/finality/precision remain separately blocked |
| Calendar | No qualified supplied NSE schedule/exceptions | HOLD | Yes | Expected, missing and extra sessions unknown |
| Corporate actions / price basis | UNKNOWN basis; partial action findings | HOLD | Yes | No qualified unaffected windows or safe exclusions |
| PIT availability | September 2026 fresh acquisition | HOLD | Yes | CAPTURED_AS_KNOWN not satisfied |
| Feature derivation | No admitted 21-session windows | NOT_RUN_BLOCKED | Yes | Upstream gates prevent projection |
| Label construction | No qualified endpoints/maturation; native boundary retained | NOT_RUN_BLOCKED | Yes | No invented truth or empirical journal widening |
| Fold feasibility | Date-presence inventory only | NOT_EVALUABLE | Yes | Support/classes/purge/embargo unknown |
| Holdout protection | Outcome access not performed | SEALED | No | No holdout-derived feedback |
| Leakage audit | No qualified empirical dependency closure | HOLD | Yes | Vintage/actions/fold safety not established |

## 10. Immutable audit and files created

Qualification-attempt fingerprint:
**`f30caf330ce5192a235d85d18629770d34b3b1547fac9f3dfdfdf5870210a2ed`**.

The [content-addressed audit](qualification_records/ff1_1a/qualification_attempt_f30caf330ce5192a235d85d18629770d34b3b1547fac9f3dfdfdf5870210a2ed.json)
records source/dataset pins, rights/configuration, current resolution,
calendar/action/PIT policy and missing evidence, schema, population, planned
fold protocol, holdout, leakage, explicit non-execution and fitting denial.
It follows the existing generic `QUALIFICATION_PREFLIGHT_AUDIT` convention;
it is **not** falsely labeled `EmpiricalDatasetQualification` or a fit grant.
Its seal uses existing `semantic_fingerprint` excluding the seal field itself.
The filename pins that seal; future attempts must be new files, never overwrites.
Hashing provides integrity, not authentication or OS-enforced immutability.

Files created in this pass only:

1. This document.
2. The content-addressed audit linked above (no raw OHLCV or outcome values).
3. [Audit regression tests](../tests/unit/forecasting/test_empirical_qualification_rerun_audit.py).

No existing file, provider, qualifier, feature formula, contract or frozen
baseline is modified. Previous HOLD and provisioning records retain their bytes.
The CSV and four original sidecars are unchanged and remain ignored.

## 11. Validation

Commands use repository `.venv/bin` executables. Counts overlap and are not additive.

| Check | Result |
|---|---|
| Actual private CSV/manifest preflight | PASS; all 2,045 lexical/numeric rows; offline fingerprints, rights/configuration and current identity verified |
| Three FF-1 qualification/isolation/rights test modules | **147 passed**, 22.73s |
| `tests/unit/forecasting/test_empirical_qualification_rerun_audit.py` | **15 passed**, 0.75s; sanitized audit/policy tests, not empirical feature/label acceptance |
| FF-0 acceptance plus data/context/features/source semantics/Ground Truth/linkage regressions | **1,175 passed**, 45.55s; includes the 28 FF-0 acceptance cases |
| Full repository `.venv/bin/pytest -q` | **3,109 passed**, 340.07s; no failures, skips or warnings |
| `python -m compileall -q src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS; **611 source files** |
| No-ML/provider import isolation and no-I/O qualification checks | PASS in the 147-test targeted group |
| Documentation links/fences, audit seal and `git diff --check` | PASS; 13 local links, three new-file whitespace checks, all 14 dataset/governing pins and previous HOLD bytes preserved |

Exact grouped regression command:

```bash
.venv/bin/pytest -q tests/acceptance/ff0 tests/unit/data tests/unit/context \
  tests/unit/features tests/unit/source_semantics \
  tests/unit/evaluation/test_forecast_truth.py \
  tests/unit/evaluation/test_forecast_linkage.py
```

No training dependency was installed or required. Calendar/security/action
mechanics are covered by existing supplied-input tests; those fixtures are not
certified empirical calendars or corporate-action evidence. Current empirical
scientific qualification tests cannot run beyond admission for the reasons
recorded above. Actual no-fitting counts are zero for Logistic/scaler fits,
model artifacts, learned forecasts, paired Brier/log-loss, calibration and all
provider/broker operations. Public-source browsing was limited to documentation
and action evidence review; it was not a market-provider acquisition or PIT capture.
Static inspection also found no `LogisticRegression`, `StandardScaler` or `.fit(`
in `src` or `scripts`; the accepted clock/knowledge literals and empirical
Outcome Journal rejection remain unchanged. Existing tracked changes have the
same whole-diff byte fingerprint as at entry; this pass only adds its three files.

## 12. Blockers and exact next step

The data no longer needs a credential retry. Do not repeat the historical fetch
to try to resolve scientific gates; identical fresh acquisition cannot supply
historical vintage evidence. Needed before another scientific attempt:

- Historical availability/revision evidence compatible with CAPTURED_AS_KNOWN,
  or a separately reviewed versioned SIMULATED vintage policy supported by
  actual source revision semantics; never fabricated original capture clocks.
- Source-decimal, unadjusted-close authority and complete scoped corporate-action
  coverage (including effective sessions and historical eligibility), sufficient
  to identify safe windows or explicit exclusions.
- Qualified historical NSE cash schedule/exceptions and dated security mapping.
- Thereafter admitted windows/maturation and the appropriate reviewed empirical
  truth/split integration, without changing FF-0 or duplicating its label logic.

Exact next prompt title:

**TIAF A7 / FF-1.1A — PIT/VINTAGE, SOURCE-DECIMAL, CALENDAR AND CORPORATE-ACTION EVIDENCE RESOLUTION**

Do not advance to FF-1.2 while these gates remain HOLD. No empirical fitting
authorization is implied by passing software tests. No source-policy relaxation
or approved protocol/learning grant is manufactured by this report.

Git recommendation after review: a documentation/audit-only checkpoint retaining
the HOLD, not a “dataset qualified” checkpoint. Do not include raw market data.
No commit, tag or push was performed. No A6/FF-0 change, public capability,
calibration/ensemble/LLM/FM-LFDE work or A8 work occurred.
