# FF-1.1A — PIT/vintage, decimal, calendar and corporate-action evidence resolution

Review date: **2026-09-21, Asia/Kolkata**. Evidence checkpoint:
`2026-09-21T12:56:05.319635+05:30`. This is an evidence-resolution pass,
not an empirical qualification run, historical replay, or fitting authorization.

```text
HOLD_EVIDENCE_RESOLUTION
READY_FOR_EMPIRICAL_QUALIFICATION_RERUN = NO
EMPIRICAL_FITTING_AUTHORIZED = NO
HOLDOUT_STATUS = SEALED
```

## 1. Outcome and preserved baseline

The material new finding is **documented adjusted daily data**, not an absence of
corporate actions. Dhan says its daily historical API adjusts for bonuses and
splits. The accepted FF-1 target requires **unadjusted completed closes**. Therefore
the existing source must not be admitted as that target's price basis. This is a
provider-policy-based assessment, not a reconstruction or independent certification
of the original HTTP response. The source's full adjustment method remains
unqualified. [Dhan official support](https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/)

The blocker set is narrower in *what must be obtained*: a source-exact,
qualified **unadjusted** artifact is needed, not just another copy of the same
adjusted endpoint. The number of failed scientific gates has not fallen to zero.
Calendar and identity checkpoints improve evidence but do not establish complete
coverage. No statistical invariance or historical-PIT claim has been inferred.

Preserved inputs:

| Item | Pin / state |
| --- | --- |
| Repository HEAD | `2eb522c1dc978c1f267d4ad6c9cf7d0b287ad9b8` |
| Frozen A6 baseline | `6dc2ff304aae0e87540260b092919bb91e4d4189` |
| Accepted FF-0 baseline | `e5283c9eaa4294bd236186d663335efdf7dab236` |
| Previous qualification audit | `f30caf330ce5192a235d85d18629770d34b3b1547fac9f3dfdfdf5870210a2ed` |
| RELIANCE CSV SHA-256 | `d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6` |
| Source-manifest semantic fingerprint | `3d1a4e21b6f4d08cb94b29d0aac83ec368c3c79c40bc535f2a75da55fb452c09` |
| Actual acquisition completed | `2026-09-21T12:07:50.995917+05:30` |
| Dataset integrity | 2,045 supplied rows; prior numeric validation PASS; zero duplicates reconfirmed |
| Rights | `UNVERIFIED`, `WARN_ONLY`, `ADMITTED_WITH_WARNING`; not legal permission or training approval |

The existing CSV, all four companions, earlier HOLD audits, runtime and governing
architecture remain unchanged. In particular, the original source manifest still
says `UNKNOWN`: this new assessment is an additive record of later knowledge.
See the [previous qualification report](TIAF_A7_FF1_1A_EMPIRICAL_QUALIFICATION_RERUN.md).

## 2. Versioned resolution record and evidence retention

The [sanitized resolution audit](qualification_records/ff1_1a/evidence_resolution_20260921.json)
contains the source index, independently fingerprinted policy proposal,
partial calendar evidence and small dated identity record. It is **not** a native
`EmpiricalDataset`, a runnable corpus, a qualified schedule, or an admission token.

| Record | FF canonical semantic fingerprint |
| --- | --- |
| Resolution audit | `0e6d8036f8429238a97859c65772b706aac108c0b80f4e58c30517abe5c2d2b8` |
| Research-vintage proposal v1.0 | `25307e246e72626bd153e425f5aa2646155d627a406cb78eb8f47bfdc1b5a5ac` |
| Partial calendar evidence v1.0 | `95b115334a61b8e0cde4f79210fcaa6390b9ddd6e8c91caa9861a74876f5b2a0` |
| Identity checkpoints v1.0 | `dde938630170af24778b24b83cb6fee19166a0c2e4d3f967d2168515f3a0fe1a` |

Each seal hashes the object excluding its own fingerprint field, using existing
`tiaf.forecasting.identity.semantic_fingerprint`. The audit seal includes its
three nested seals. Changing a warning, eligibility rule, clock assumption or
source assessment changes the applicable fingerprint. A hash establishes
integrity, **not authenticity, completeness, entitlement or historical availability**.

Three public documents were retained separately in Git-ignored
`data/ff1/evidence_resolution_20260921/`, outside the original dataset package:

| Local file | Bytes | Raw SHA-256 |
| --- | ---: | --- |
| `dhan_basis.html` | 496,236 | `65d4dbf30bd77a9f3595440a6755542b3305b65d2d8235fe229ae7c6ce9fa6e4` |
| `ril_identity_2018.pdf` | 343,114 | `b4989f943e98722f56cc5eb5312c5fbb9fc825221ee9cf18c924016d8e66405c` |
| `ril_rights_2020.pdf` | 9,210,659 | `28f2020c48f4dc1ea66b2e0811d49b8382a5b90e6ed20a105b75571fdaae41e6` |

The checkpoint above is when retention/hashes were verified, **not** a provider
publication time. No credentials, request headers, secrets or raw OHLCV are in
the checked-in audit. CI tests use only sanitized records, not these local blobs.

Raw NSE archive downloads failed with HTTP/2 errors and one bounded HTTP/1.1
retry per URL timed out. The source index labels browser-extracted documents and
search-only excerpts explicitly, with `null` raw hashes. No successful archival
capture is claimed for them. Public-document research is distinct from a market-data
API call; **zero new Dhan history requests** were made.

## 3. Vintage and PIT availability: separate proposal, no waiver

The [FF-1 plan §2](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md) and
[FF architecture §10.1](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md) require
`CAPTURED_AS_KNOWN`: availability, first acquisition and original trusted admission
must all satisfy the historical cutoff. The native `FF1FeatureSchema` still fixes
that literal. Fresh acquisition cannot be substituted without a separately
accepted, explicitly bound profile/schema.

Decision: fresh history can describe a **revised-history research simulation**,
but is **not sufficient to admit this dataset to the accepted FF-1 historical
benchmark**. A hypothetical EOD arrival rule does not remove revisions or later
corporate-action adjustments embedded in a 2026 download. No bound on their
influence on the approved features has been established. Calling it SIMULATED
does not demonstrate leak-free, historically available dependencies.

The independently pinned proposal is therefore `NOT_ADOPTED_FOR_CURRENT_FF1`:

| Meaning | CAPTURED_AS_KNOWN | Proposed fresh-history research class |
| --- | --- | --- |
| Source | Demonstrably cutoff-safe retained dependencies | `FRESH_HISTORICAL_DOWNLOAD` |
| Historical capture claim | Requires supporting clocks/artifacts | `NONE` |
| Realization | Determined by the accepted protocol; replay does not change original mode | `SIMULATED` only |
| Historical-PIT / operational replay | Only when the original protocol's gates pass | Ineligible |
| Revised-history exploration | Not an automatic waiver | Conditional on a separate accepted profile |
| Current FF-1 training/evaluation admission | All current gates required | Ineligible; not runtime-enabled |
| Fitting grant from this pass | None | None |

This is a **research-policy proposal**, not a silent architecture amendment or new
runtime enum. No active admission, exclusion or identity-continuity policy changed.
The explicit proposal avoids a large taxonomy and provides a stable artifact for
the required separate review. Selecting an alternative later must retain warnings,
prevent pooling with captured-as-known results, and bind the profile throughout
qualification/replay; changing a document alone is not implementation.

The proposed `CONSERVATIVE_EOD_SIMULATION` timing is:

```text
qualified session close t
  +30 minutes = hypothetical information cutoff
   +5 minutes = simulated forecast as-of
               must be strictly before the next qualified target-session open

actual 2026 acquisition/admission and computation clocks remain actual
```

`availability_evidence = ASSUMED_CONSERVATIVE_POLICY`. No verified Dhan publication
SLA was found in the reviewed sources. These offsets are research assumptions, not
a measured upper bound on publication delay or a guarantee against revision bias.
Use actual qualified special-session closes, not a universal 15:30 close. No
`EvidenceReference.available_at`, `acquired_at` or `admitted_at` was fabricated or
backdated. Asia/Kolkata remains canonical; all recorded instants are aware.

## 4. Source decimals: not recovered, no tolerance waiver

Inspection confirmed this path:

```text
Dhan JSON -> response.json() -> normalized floating OHLCV -> csv.writer
             original numeric lexemes not retained
```

Relevant code is [Dhan transport](../src/tiaf/data/providers/dhan/transport.py),
[native provisioner](../scripts/provision_reliance_test_data.py) and
[existing exact-decimal identity utility](../src/tiaf/forecasting/identity.py).
The manifest explicitly records `raw_response_retained = false`.

| Route | Result |
| --- | --- |
| A: recover original bytes | No original response/decimal companion in the provisioned package |
| B: one decimal-preserving re-fetch | Not executed; it would still return documented adjusted data, not fix the target mismatch |
| C: prove float normalization invariant | Not established; no authoritative exact comparator or documented rounding bound |

The [official endpoint schema](https://dhanhq.co/docs/v2/historical-data/) does not
establish a source-decimal scale or an unadjusted selector in the reviewed
interface. Current instrument tick size is not proof of historical adjusted-bar
decimal precision. Source precision remains UNKNOWN; normalized precision is
Python-float CSV text. No new rounding rule, precision-restoration artifact,
empirical invariance test or decimal fingerprint is claimed.

The added **synthetic** test illustrates why float equality is not general proof:
exact values `100.0000000000000001` and `100.0000000000000002` can collapse to the
same float. It does not assert that these occur in RELIANCE. A future exact-source
capture should retain raw response bytes and parse numbers without an intermediate
float, then retain canonical decimal strings plus separate raw/semantic hashes.
Lexical precision and semantic value are separate: trailing-zero-only differences
can change a raw hash while native canonical Decimal hashing preserves equal value.

## 5. NSE calendar: scoped checks, not a manufactured schedule

No complete project-native historical calendar artifact was located. New primary
references establish only partial facts:

| Source | What it establishes | What it does not establish |
| --- | --- | --- |
| [NSE/CMTR/36475, 2017-12-12](https://nsearchives.nseindia.com/content/circulars/CMTR36475.pdf) | Initial 2018 CM holidays and November 7 Muhurat date | Later amendments, special-session clocks, full 2017–2026 scope |
| [NSE/CMTR/59722, 2023-12-12](https://nsearchives.nseindia.com/content/circulars/CMTR59722.pdf) | Initial 2024 CM holidays and November 1 Muhurat date | Later closures/session changes; Muhurat timings deferred |
| [NCL/CMPT/60343, 2024-01-19](https://nsearchives.nseindia.com/content/circulars/CMPT60343.pdf) | Settlement schedule corroborates January 20 trades and January 22 holiday; names two trading circulars | A replacement for trading-clock authority or full-range completeness |

The indexed calendar artifact is versioned **PARTIAL_NOT_A_QUALIFIED_SCHEDULE**.
It excludes the two stated Muhurat dates from the full-day-closure subset. It does
not build sessions from weekdays or interpolate unknown open/close times.

Date-only checks against the pinned CSV:

| Measure | Result |
| --- | --- |
| Required coverage | 2017-11-01 through 2026-01-30 |
| Complete qualified coverage | Not established |
| Supplied date rows / duplicates | 2,045 / 0 |
| Explicit full-day holidays checked | 28, across the two initial lists |
| Supplied rows on those 28 dates | 0 |
| Explicit Muhurat dates checked / missing | 2 / 0 |
| January 20 / January 22, 2024 | Present / absent, consistent with corroborating notice |
| Full-range expected / missing / extra sessions | **UNKNOWN / UNKNOWN / UNKNOWN** (`null`, not zero) |

Eight supplied weekend dates need qualified exception clocks:
`2019-10-27`, `2020-02-01`, `2020-11-14`, `2023-11-12`, `2024-01-20`,
`2024-03-02`, `2024-05-18`, `2025-02-01`. They are **not classified as invalid**
merely for being weekends. This is not an exhaustive exceptional-date list:
weekday closures, missing special dates, special closes and security-specific
suspensions remain to be checked. Successful subset checks cannot authorize
native qualification. No complete schedule, missing-session imputation or zero-gap
claim was produced.

## 6. Corporate actions and exactly one strategy

The following are authoritative **checkpoints, not a complete event ledger**:

| Event | Recorded fact | Remaining qualification |
| --- | --- | --- |
| 2020 rights issue | 1 for 15; record date 2020-05-14; partly-paid rights and entitlement have distinct ISINs | Ex-date/series effects, subsequent call mechanics and provider handling |
| 2023 financial-services demerger | Special pre-open/market boundary on 2023-07-20 | Full series adjustment/provenance and affected-window qualification |
| 2024 bonus | 1:1; record date 2024-10-28 | Independently pinned ex-date and source adjustment factors |

Sources: [issuer letter of offer, 2020-05-15, cover and p62](https://www.sebi.gov.in/sebi_data/attachdocs/may-2020/1589793193201.pdf),
[NSE Indices release, 2023-07-17](https://nsearchives.nseindia.com/web/sites/default/files/2023-07/ind_prs17072023.pdf),
[issuer bonus filing, 2024-10-16](https://nsearchives.nseindia.com/corporate/RELIANCE_16102024200409_SE_16102024.pdf).
The demerger release was available as an indexed primary-source excerpt; its raw
PDF was not successfully retained. Record date is not silently substituted for
ex-date. No statement that splits, dividends or other events are absent is made.

**Chosen strategy: C — HOLD.** The current provider-documented basis is ADJUSTED;
the accepted target is `UNADJUSTED_COMPLETED_CLOSE`. Strategy A cannot operate on
an unqualified/adjusted source. Strategy B would need a coherent separately
accepted target and full methodology, neither supplied here. The support FAQ is
not a versioned factor ledger or a guarantee about dividends, demergers, volume
adjustments or revisions. Do not infer those from chart appearance.

No active exclusion policy was introduced and no observations were excluded or
constructed. For a future qualified *unadjusted* source, the existing dependency
rule remains: complete unaffected action evidence must cover the **21-session
input closure** (20 returns/preceding volumes require 21 bars), the reference close
and next-session target transition. A material boundary contaminating any
dependency or unknown action coverage blocks that observation. This is not an
arbitrary ±20 calendar-day window, nor permission to infer unaffected intervals
from this short event list. Removing a few dates cannot undo retrospective
adjustments applied throughout an earlier series.

## 7. Historical identity: corroborated checkpoints, interval still HOLD

The small identity record in the audit contains RELIANCE, NSE, fully-paid cash
equity, ISIN `INE002A01018`, current Dhan ID `2885`, evidence references, and
**null historical effective dates** where not established.

The [2017–18 issuer governance report, printed p215](https://www.ril.com/ar2017-18/pdf/CorporateGovernanceReport.pdf)
identifies NSE RELIANCE and the same ISIN. The 2020 offer document, printed p62,
corroborates it while distinguishing partly-paid rights `IN9002A01024` and rights
entitlement `INE002A20018`. The previously pinned current resolver agrees in 2026.
These dated/report-period checkpoints support legal-instrument identity; they do
not prove every intervening provider row, a historically unchanged numeric ID,
absence of suspensions/series changes, or unchanged economic exposure through the
demerger. No invented provider effective date or interval interpolation is used.

Verdict: **CORROBORATED checkpoints; HOLD_FULL_INTERVAL_AND_PROVIDER_SERIES_UNQUALIFIED**.
The series must exclude partly-paid shares, rights entitlements and the spun-off
security unless separately modeled. This pass adds no general master-data service
or new identity-admission policy.

## 8. Scientific gate matrix and next work

| Gate | Previous | Evidence/policy added | Current | Blocking? |
| --- | --- | --- | --- | --- |
| Vintage/provenance | Fresh history fails cutoff | Pinned distinct revised-history proposal, no historical claim | HOLD; current FF-1 profile unchanged | Yes |
| PIT availability | No historical timing evidence | +30m/+5m explicitly an unadopted simulation assumption | HOLD; no fabricated publication/acquisition | Yes |
| Source decimals | Float-normalized only | Transport/exporter inspection; no comparator/invariance proof | HOLD; compatible source-exact capture required | Yes |
| Calendar | No qualified schedule | 28 holiday checks, two special dates, exception ledger | HOLD; complete clocks/coverage absent | Yes |
| Actions / basis | UNKNOWN | Documented adjusted Dhan daily policy and three action checkpoints | HOLD; adjusted-source/unadjusted-target mismatch plus incomplete actions/method | Yes |
| Historical identity | Current mapping only | 2017–18 and 2020 symbol/ISIN checkpoints | HOLD; full interval/provider series not qualified | Yes |
| Rights admission | WARN_ONLY | Existing policy preserved | ADMITTED_WITH_WARNING | No |
| Dataset integrity | PASS | CSV byte seal and date count rechecked | PASS; numeric PASS inherited unchanged | No |

2025 remains **SEALED**. Only date presence/counting and byte integrity were used;
no price summaries, returns, empirical features, labels, label balance, model
outputs, paired metrics or performance were inspected. Full-range session and
fold sufficiency remain uncomputed. Native empirical qualifier calls: **0**.
Logistic/scaler fits, learned forecasts and broker operations: **0**.

Required next inputs, in order:

1. Establish a source that can provide **unadjusted, exact-decimal closes/OHLCV**
   with compatible source provenance; do not silently switch providers, reverse
   adjustments or change target semantics. A new acquisition needs explicit scope.
2. Retain authoritative full-range NSE session calendars, revisions and special
   clocks; reconcile missing/extra dates and security eligibility.
3. Obtain complete applicable corporate-action and dated provider/security
   continuity evidence. Preserve uncertainty rather than infer unaffected coverage.
4. Independently accept/bind a revised-history research profile with explicit
   limits, or supply cutoff-safe historical captures / separately plan a prospective
   study. The proposed timing assumption alone cannot clear vintage leakage.
5. Only after those gates pass, rerun qualification prerequisites. Fitting remains
   separately unauthorized even if that later rerun succeeds.

Exact next prompt title:

**TIAF A7 / FF-1.1A — UNADJUSTED SOURCE-EXACT DATA, NSE SESSION/ACTION AND DATED IDENTITY EVIDENCE, WITH VINTAGE PROFILE ACCEPTANCE**

## 9. Changes, tests and Git scope

New tracked-scope candidates only:

- This report.
- [Sanitized versioned audit](qualification_records/ff1_1a/evidence_resolution_20260921.json).
- [32 audit guardrail tests](../tests/unit/forecasting/test_empirical_evidence_resolution_audit.py).

The tests cover nested seals, proposed versus current policy, no backdating,
synthetic exact-decimal preservation/float counterexample, scoped holiday/Muhurat
facts, unknown calendar totals, adjusted-source rejection semantics in the audit,
identity limitations, sealed holdout, no fitting and preservation of the prior
qualification seal. They do not pretend to validate unavailable empirical facts.
Existing native qualification tests additionally exercise missing/extra sessions,
affected/unknown actions, adjusted-basis rejection, late evidence and ambiguous
identity; those runtime algorithms were not changed.

Validation results follow. No runtime implementation,
FF-0, frozen A6, features, target, architecture acceptance or rights policy changed.
Recommend a **scoped review and later commit of only these three files**; exclude
the local retained source blobs and all unrelated pre-existing work. No commit,
tag or push was performed.

| Validation | Result |
| --- | --- |
| New audit tests | **32 passed**, final standalone run 0.91s |
| Focused FF-1 research/rights/isolation and both audit modules | **194 passed**, final run 24.03s |
| Full `.venv/bin/pytest -q` | **3,141 passed** in 341.70s; no failures/skips/warnings reported |
| `.venv/bin/python -m compileall -q src scripts` | PASS |
| `.venv/bin/ruff check src tests scripts` | PASS |
| `.venv/bin/mypy src tests` | PASS, 612 source files |
| `git diff --check` | PASS |
| Three new files' whitespace / final newlines | PASS (checked separately because untracked files are not in `git diff`) |
| Nine local documentation links / code fences / displayed seals | PASS |
| All five original dataset file hashes | PASS, unchanged |
| Three retained public-source byte hashes and inspected claim text | PASS; each file remains Git-ignored |
| All 909 pre-existing repository files | Byte-for-byte unchanged by this pass |

The original tracked diff SHA-256 remains
`358e8234f07c532af111fe9e194a4a9f184b803ab2382b9f807819801873438d`.
The final 32/194-test checks include the final sealed audit; full-suite synthetic
engineering tests are not empirical holdout opening, empirical qualification,
or learned fitting.
