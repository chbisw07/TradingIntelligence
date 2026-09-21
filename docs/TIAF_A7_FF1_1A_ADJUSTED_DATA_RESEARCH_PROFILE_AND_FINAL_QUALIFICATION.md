# FF-1.1A — Adjusted-data research profile and final empirical qualification

## 1. Decision and scope

**FF1_1A_QUALIFICATION_COMPLETE**

```text
ADJUSTED_DATA_RESEARCH_PROFILE_ACCEPTED = YES
EMPIRICAL_FITTING_AUTHORIZED = YES
HOLDOUT_STATUS = SEALED
LEAKAGE_AUDIT = PASS
```

Assessed **2026-09-21T14:35:55.138317+05:30**. This is bounded data/feature/label/fold
qualification for the accepted FF-1 retrospective research experiment, not a
model fit, a claim of predictive value, operational replay eligibility, legal
rights approval or production authorization. A separate FF-1.2 implementation
request is next. No tuning was done against these counts or numeric summaries.

The previous [qualification HOLD](TIAF_A7_FF1_1A_EMPIRICAL_QUALIFICATION_RERUN.md)
and [evidence-resolution HOLD](TIAF_A7_FF1_1A_PIT_VINTAGE_DECIMAL_CALENDAR_CORPORATE_ACTION_RESOLUTION.md),
including their sealed JSON audits, are preserved byte-for-byte. They applied
the then-current stricter policy; this explicit correction does not rewrite
history. The original FF-0/captured-as-known path retains its stricter semantics.

## 2. Why the policy changed

Requiring an unadjusted series for every retrospective experiment conflated
two different jobs. Operational replay requires actual historical knowledge.
Retrospective numeric research can use a consistently adjusted later vintage,
provided it names that vintage and does not pretend to reconstruct historical
publication or decisions. Adjusted split/bonus continuity avoids artificial
return, moving-average and volatility discontinuities.

The accepted opt-in profile is `ff1.adjusted_retrospective/1.0`:

| Dimension | Pinned meaning |
|---|---|
| Research mode / vintage | SIMULATED_RESEARCH / FRESH_HISTORICAL_DOWNLOAD |
| Price basis | CORPORATE_ACTION_ADJUSTED, common to features and both target endpoints |
| Historical capture claim | NONE |
| Operational replay / production eligibility | NO / NO |
| Retrospective ML eligibility | YES, subject to the qualification gates |
| Availability | ASSUMED_CONSERVATIVE_POLICY, not measured publication |
| Precision | NORMALIZED_BINARY64_RESEARCH; no source-forensic claim |
| Volume | PROVIDER_DEFINED_COUNTS_WITH_WARNING |
| Rights | UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING |
| Configuration | Explicit immutable COLD bootstrap owner; not a universal default |

The unchanged target family is
`equity.next_session_close.return_gt_zero@1.0`.
Its direction is next completed session close versus reference close **under
the pinned adjusted series basis**, not a dividend-reinvested total return.
`FF1FeatureSchema` remains the old strict profile. The additive
`AdjustedFF1FeatureSchema` retains ID/version
`ff1.reliance.a2_daily_five/1.0` and the exact five A2 requests/formulas;
its separate profile changes its context fingerprint, not its feature formula
identity. Both schemas reject feature addition/removal.

```text
Pinned existing Dhan files + reviewed research evidence
          ↓ byte hashes / manifest seals / structural holdout redaction
Explicit COLD adjusted research profile → native Evaluation qualifier
          ↓                       ↓
same five A2 calculations     shared Ground Truth endpoint arithmetic
          └──────────┬────────────┘
        exact fold memberships / support checks
                     ↓
 private sealed qualification + safe checked-in count/seal summary
                     ↓
       separate FF-1.2 request (NOT executed here)
```

## 3. Dataset, integrity and provenance

Source: existing **TI-native Dhan daily historical** RELIANCE/NSE cash-equity
provisioning, provider security ID 2885. There were **zero new market-data API
calls** in this pass; public source-document research is not a data refetch.

- CSV: `data/ff1/reliance/reliance_daily_ohlcv.csv`, **99,118 bytes**.
- SHA-256: `d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6`.
- **2,045 rows**, 2017-11-01 through 2026-01-30; **0 duplicate dates**.
- Source-manifest semantic seal:
  `3d1a4e21b6f4d08cb94b29d0aac83ec368c3c79c40bc535f2a75da55fb452c09`.
- Actual acquisition: **2026-09-21T12:07:50.995917+05:30** (preserved).
- Provisioning-manifest seal:
  `c54cbf1c7ba1d11a8166aec3a9c10a72efbc95446cc5cc240692fd1b6410e272`.

All five source files are byte-pinned in the
[review record](qualification_records/ff1_1a/adjusted_research_review_20260921.json).
The reader checks manifest self-seals and cross-references, CSV size/hash,
row count, identity, chronology and coverage. The original source manifest's
UNKNOWN basis is not edited; the later reviewed adjustment evidence is an
explicit additional context. Integrity hashing covers the original file bytes;
it does not inspect protected price outcomes.

Canonical RELIANCE/NSE equity plus ISIN **INE002A01018** is qualified for this
economic-series research scope using historical issuer checkpoints and current
provisioning identity. It does **not** assert historical continuity of Dhan's
numeric security ID. The 2018 issuer governance report and 2020 rights document
corroborate the identity; the partly-paid/rights-entitlement ISINs are not silently
substituted for the fully-paid series.
[Issuer 2018 governance report](https://www.ril.com/ar2017-18/pdf/CorporateGovernanceReport.pdf);
[2020 SEBI-hosted issuer rights document](https://www.sebi.gov.in/sebi_data/attachdocs/may-2020/1589793193201.pdf).

Rights have not been upgraded. The unchanged COLD rights policy admits
uncertainty with warnings; explicit denial still blocks. This is research
admission, not a statement that licensing terms have been verified.

## 4. Price basis, actions and relative volume

Dhan documents its daily historical series as adjusted for bonuses and splits.
That supports the adjusted research basis; it does not establish a complete
rights/demerger/volume adjustment methodology.
[Dhan's adjustment statement](https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/).

| Known material boundary | Treatment | Evidence |
|---|---|---|
| 2020-05-13 rights ex-date | Unsupported adjustment class; exclude crossing dependencies | [NSE FAOP44356](https://nsearchives.nseindia.com/content/circulars/FAOP44356.pdf) |
| 2023-07-20 financial-services demerger | Unsupported adjustment class; exclude crossing dependencies | [NSE Indices notice](https://nsearchives.nseindia.com/web/sites/default/files/2023-07/ind_prs17072023.pdf) |
| 2024-10-28 1:1 bonus record boundary | Retain adjusted continuity; no exclusion merely for a bonus | [Issuer notice](https://nsearchives.nseindia.com/corporate/RELIANCE_16102024200409_SE_16102024.pdf) |

No reverse adjustment, estimated adjustment factor or provider-price repair is
performed. A 21-bar feature dependency is excluded exactly when its first date
is before an unsupported boundary and its reference date is on/after it.
A label is unavailable when its reference is before that boundary and its next
session endpoint is on/after it. When the first feature bar is already on the
post-action side, the window is eligible again. Consequently there are **20
feature exclusions and one crossing-label exclusion per unsupported action**.
These decisions are date-based, not chosen from favorable realized returns.

This is a bounded review of material capital-structure actions, not a complete
corporate-action platform. No total-return, distribution-reinvestment, or
rights-adjustment formula is claimed. Routine dividends are part of the
provider's published price series, not locally corrected. Extraordinary
distributions/spin-offs would require the same explicit unsupported-boundary
treatment if new evidence identifies them.

`relative_volume` remains the fifth feature. It is a dimensionless ratio of
provider-delivered counts to their preceding 20-session mean, not a claim of
corporate-action-neutral economic turnover. The counts are finite nonnegative
integers within exact binary64 integer range; zero current volume is valid,
zero denominator is unavailable. Unknown volume adjustment is retained as an
explicit provider-defined warning, including near the retained bonus boundary.
This is acceptable as a documented provider-series covariate, not evidence of
fully normalized volume or a basis for silently dropping/changing the feature.
Daily bars also include short Muhurat/DR sessions; volume is not normalized by
session duration. The retained A2 volatility annualization is the existing 252
factor, not a newly inferred calendar length. These baseline conventions remain
visible limitations rather than reasons to change the five-feature schema.

## 5. Research clock and numeric qualification

Every session uses an aware Asia/Kolkata clock:

```text
qualified normal-market close
  → +30 minutes: assumed information cutoff
  → +5 minutes: simulated forecast as-of
  → strictly before next scheduled normal-market open
```

Special-session clocks override regular 09:15–15:30. Bar clocks are research
session alignment, not recovered provider publication timestamps. Truth has a
separately named **assumed** target-close+30m availability; actual acquisition
remains in 2026. Future adjustments/revisions in that vintage are an explicit
retrospective limitation. Thus the leakage PASS below is conditional on this
accepted research basis, **not** proof of historical point-in-time tradability.

**SOURCE_DECIMAL_FIDELITY = QUALIFIED_FOR_FF1_NUMERIC_RESEARCH**.
CSV-normalized binary64 values are the pinned numeric benchmark. No raw JSON
lexical fidelity or provider rounding SLA is invented. Non-equal endpoint gaps
must exceed an envelope of eight ULPs per endpoint; ambiguous near-ties are
unavailable, not forced negative. Equal normalized closes retain the original
Ground Truth rule (zero); there is **one** such admitted equality.

| Numeric check, unsealed eligible observations only | Result |
|---|---|
| Smallest nonzero close difference | 0.01999999999998181 |
| Minimum nonzero gap / two-endpoint perturbation envelope | 5497558138.875 |
| Feature sensitivity protocol | Two opposite alternating ±8-ULP close perturbations through the same A2 engine |
| Maximum observed absolute feature drift | 3.367972567502875e-12 |
| Pinned absolute feature tolerance | 1e-8 |
| Nonfinite feature values | 0 |

These perturbations quantify normalization sensitivity, not a formal bound
against arbitrary provider revisions or lost original text. The large observed
nonzero label margin and tiny measured feature drift support numeric research;
they do not make this artifact suitable for source-forensic replay.

## 6. Practical calendar qualification

**CALENDAR = QUALIFIED_FOR_RETROSPECTIVE_DAILY_RESEARCH**.
All 2,045 supplied dates match the independently reviewed weekday/holiday/
special-session schedule: **0 missing scheduled bars, 0 unexplained dates**.
The bounded schedule is checked in with annual NSE notice references,
election/holiday amendments, clock overrides and access limitations. It is not
a production historical exchange-calendar service.

| Previously anomalous weekend | Explanation | Normal-market open → close, IST |
|---|---|---|
| 2019-10-27 | Muhurat; NSE annual notice establishes date | 18:15 → 19:15 |
| 2020-02-01 | Union Budget, CMTR43290 | 09:15 → 15:30 |
| 2020-11-14 | Muhurat, CMTR46230 | 18:15 → 19:15 |
| 2023-11-12 | Muhurat, CMTR59124 | 18:15 → 19:15 |
| 2024-01-20 | Regular Saturday, **MSD60340**; earlier DR plan withdrawn | 09:15 → 15:30 |
| 2024-03-02 | DR special session, MSD60677 | 09:15 → 12:30 aggregate |
| 2024-05-18 | DR special session, MSD61893 | 09:15 → 12:30 aggregate |
| 2025-02-01 | Union Budget, CMTR65729; structural only | 09:15 → 15:30 |

The DR days contain two normal trading intervals (09:15–10:00 and
11:30–12:30), represented here by one daily bar, not an invented continuous
intraday path. Post-close sessions do not replace the normal-market close.
[NSE March DR notice](https://nsearchives.nseindia.com/content/circulars/MSD60677.pdf),
[NSE May DR notice](https://nsearchives.nseindia.com/content/circulars/MSD61893.pdf),
[NSE January regular-session notice](https://nsearchives.nseindia.com/content/circulars/MSD60340.pdf).

The 2019 Muhurat date is established by NSE CMTR39612. Its revised clock is
corroborated by the broker's contemporaneous operational notice; the linked
CMTR42403 PDF was unreadable, so it is **not** claimed as a successfully inspected
clock source. This source-tier limitation is acceptable for the practical daily
research calendar, not a claim of complete exchange-archive reconstruction.
[NSE 2019 schedule](https://archives.nseindia.com/content/circulars/CMTR39612.pdf),
[Zerodha's 2019 session notice](https://zerodha.com/marketintel/bulletin/234057/muhurat-trading-session-on-account-of-diwali-3).

Weekday Muhurat clocks are also included (2018, 2021, 2022, 2024 and 2025).
The **2021-02-24 outage extension** is explicitly included: final normal-market
close 17:00, research cutoff 17:30, simulated as-of 17:35 IST. Final review caught
and corrected an initial regular-close assumption before the authoritative
qualification seal was issued. No prices, features/formulas, population counts
or policy thresholds were tuned. SEBI confirms the extension to 17:00.
[SEBI's outage clarification](https://www.sebi.gov.in/sebi_data/attachdocs/feb-2021/1614256948318.pdf).
The separate 2019-10-25 Dhanteras extension applied only to Gold ETFs/sovereign
gold bonds, not RELIANCE, so it does not change the cash-equity close used here.
[NSE-authored CMTR42455 notice](https://www.steelcitynettrade.com/Circulars/Extended%20LIVE%20TRADING%20session%20on%20Friday%2C%20October%2025%2C%202019.pdf).

Amendments include 2019 election closures, the June 2023 holiday shift, January
22 / May 20 / November 20 in 2024, and January 15 in 2026. Settlement-only
holidays were not treated as trading holidays without trading evidence.
[June 2023 NSE confirmation](https://niftyindices.com/Press_Release/ind_prs27062023.pdf),
[November 2024 election notice](https://nsearchives.nseindia.com/content/circulars/CMTR64960.pdf),
[January 2026 trading notice](https://nsearchives.nseindia.com/content/circulars/CMTR72260.pdf).
All per-year source IDs and special-date links are in the reviewed JSON.

## 7. Actual population and five-feature sanity

Requested reference period: **2018-01-01 through 2025-12-31**. The 42 rows from
2017 supply warm-up history. The 20 rows from January 2026 supply dates only;
like the 249 holdout rows, their numeric values are redacted before parsing.

| Population | Count / scope |
|---|---|
| Requested reference observations | 1,983 |
| Unsealed 2018–2024 requested | 1,734 |
| 2025 structural reference slots | 249; no empirical feature/label eligibility asserted |
| Feature-eligible, unsealed | 1,694 |
| Label-eligible, unsealed | 1,731 = 900 positive + 831 zero |
| Paired-ready potential, unsealed | 1,691; no forecasts or actual scored pairs |
| Label unavailable from unsupported boundary | 2 |
| Label sealed | 250 = 249 holdout origins + 2024-12-31 targeting 2025 |
| Feature exclusions | 20 rights + 20 demerger |
| Feature numerical failures / imputation | 0 / none |

Label eligibility is independent of feature completeness: an endpoint direction
can be known even when its feature lookback crosses an excluded action.
The complete label denominator reconciles as **1,731 + 2 + 250 = 1,983**.
Sealed labels are not counted as failures, zeros or missing-price imputations.

A2 values below are **observed qualification summaries**, not forecasts or
illustrative trading performance. No threshold was tuned to these ranges.

| Feature | Minimum | Maximum |
|---|---|---|
| `realized_vol_20` | 9.589227742062745 | 122.87519391562141 |
| `relative_volume` | 0.03767511902296471 | 5.128071382962299 |
| `ret_1` | -0.1410309343855385 | 0.13729299028143238 |
| `ret_5` | -0.2313441439743107 | 0.17050264049081143 |
| `sma20_distance` | -26.244004622037608 | 20.91101799359132 |

No scaler, imputer, alternate feature formula or learned transformation was used.
The feature vector/results and input closure are sealed in the private artifact.

## 8. Fold feasibility — no fitting

All five expanding training folds start in 2018. The immediately preceding
scheduled session is a whole-session embargo; fit cutoff is that session's
open. Both target resolution and assumed truth availability must be strictly
before it. Exact train/test/purge/BaseRate membership IDs are persisted, not
reconstructed from counts alone.

| Test year | Train (positive/zero) | Test slots | Test feature-complete | Test label-complete | Paired-ready potential | Purged boundary origins | BaseRate support | Complete 5-slot blocks |
|---|---|---|---|---|---|---|---|---|
| 2021 | 720 (374/346) | 248 | 248 | 248 | 248 | 2 | 20/20 | 49 |
| 2022 | 968 (510/458) | 248 | 248 | 248 | 248 | 2 | 20/20 | 49 |
| 2023 | 1216 (637/579) | 246 | 226 | 245 | 225 | 2 | 20/20 | 44 |
| 2024 | 1441 (753/688) | 249 | 249 | 248 | 248 | 2 | 20/20 | 49 |
| 2025 | 1690 (878/812) | 249 | SEALED | SEALED | SEALED | 2 | 20/20 | SEALED |

Fit cutoffs: 2020-12-31, 2021-12-31, 2022-12-30, 2023-12-29,
2024-12-31, all **09:15 +05:30**. Two prior-year reference origins per fold
are purged (one targets the embargo, the embargo origin targets the test).
Action and other eligibility exclusions are separate from that boundary purge.

Training passes 500 rows / 100 per class. Development tests pass 150 potential
pairs / 30 per paired class, 80% coverage and 20 complete five-session blocks.
Pooled development has **969 potential pairs**, exceeding 600. Development paired
populations have class counts (positive/zero) of **137/111, 127/121, 115/110, 125/123**
across 2021–2024 respectively. BaseRate's own eligibility check
uses the last **20 scheduled transitions** eligible by the same cutoff, never
20 selected valid replacements and never a full-window estimator. This checks
support only: no BaseRate probability/artifact is created.

**2025 is structural-only**: 249 scheduled slots clear the structural 200-slot
feasibility guard. Its feature/label/class/paired-block requirements remain
unmeasured and must pass at separately authorized holdout evaluation. Training
data through 2024 can be qualified without opening 2025. No statistical
performance acceptance is implied by this fold-feasibility PASS.

## 9. Leakage, replay and no-fitting verification

| Check | Result and boundary |
|---|---|
| Target values in features | None; projector receives exactly 21 bars ending at reference close |
| Future rolling rows | None; target date absent from feature window; future-price mutation test preserves earlier values |
| Post-cutoff information | No later session values under assumed research clocks; later-vintage adjustment/revision limitation explicitly retained |
| Label-derived features | None; A2 projection and independent endpoint truth remain separate |
| Global scaler/imputer | None |
| Fold leakage | Exact cutoff-safe memberships, whole-session embargo and no-backfill BaseRate support |
| Holdout outcomes | Not parsed; 2025 features/labels/class counts/relationships/performance remain absent |
| Historical capture claim | NONE; actual 2026 acquisition retained |
| Persistence | Native qualification JSON reconstructs exactly with the same semantic fingerprint |

Whole-file/context hashes intentionally bind the supplied vintage, including
structural knowledge of the complete source artifact. Hashing future bytes is
not using future prices as model inputs; the projector receives no such values.
The independent tests include deliberately nonnumeric protected cells, proving
that the reader does not normalize their numeric contents.

No LogisticRegression `.fit()`, scaler fit, model artifact, learned forecast,
Brier/log-loss or challenger-vs-BaseRate comparison exists in this pass.
The new qualification modules have no provider, broker or training imports;
tests enforce the boundary. There was no broker operation or A8 work.

## 10. Scientific gate reconciliation

| Gate | Prior status | Correction/evidence | Current status | Blocking? |
|---|---|---|---|---|
| Dataset integrity | PASS | Rechecked original bytes/manifests/2,045 rows | PASS | No |
| Rights admission | WARN_ONLY admitted | Same UNVERIFIED evidence and COLD policy | ADMITTED_WITH_WARNING | No |
| Source vintage | Wrong for captured-history path | Explicit fresh SIMULATED profile | QUALIFIED for research | No |
| Adjusted-price basis | Unadjusted-only HOLD | Documented split/bonus adjusted basis, explicit context | QUALIFIED for research | No |
| Decimal fidelity | Source text not retained | Pinned normalized series + quantified sensitivity | QUALIFIED_FOR_FF1_NUMERIC_RESEARCH | No |
| Security identity | Historic numeric ID proof absent | Canonical cash-equity/ISIN checkpoints + action treatment | QUALIFIED_FOR_RETROSPECTIVE_RESEARCH | No |
| Calendar | Incomplete prior exception review | All dates reconciled; eight weekend clocks resolved with stated source limitation | QUALIFIED_FOR_RETROSPECTIVE_DAILY_RESEARCH | No |
| Corporate actions | Unadjusted continuity unresolved | Supported bonus retained; unsupported rights/demerger dependencies excluded | QUALIFIED with exclusions | No |
| PIT availability | No historic publication capture | Explicit conservative research assumption; actual acquisition retained | QUALIFIED for SIMULATED only | No |
| Feature derivation | Not executed | Same five native A2 calculations, no imputation | PASS, 1,694 | No |
| Label construction | Not executed | Shared Ground Truth arithmetic, same adjusted basis | PASS, 1,731 | No |
| Fold feasibility | Not executed | Five train/support checks; development population; holdout structural only | PASS for next implementation step | No |
| Holdout protection | SEALED | Date-only inspection; numeric redaction | SEALED | No |
| Leakage audit | Previously not executable | Causal windows, pinned clocks/vintage, exact purges, no fitting | PASS under declared research assumptions | No |

Remaining **acceptance blockers: none** for this bounded qualification. Remaining
limitations are rights uncertainty, provider volume/methodology opacity,
retrospective vintage/revisions, bounded action/calendar evidence and untested
2025 empirical support—not hidden claims of full operational fidelity.

## 11. Seals, artifacts and reproducibility

| Artifact | Semantic fingerprint |
|---|---|
| Research profile | `1e616cc7a2f3654d856b916e790d054a6c1ff7f10efe2b316cf0a44835011c45` |
| Five-feature schema plus research profile | `76e63292685ee0b3b41f7ab033407e6bd014fc802d2092a2ed227888bdc71676` |
| Reviewed evidence | `3da26b18d674639ce9da6e49518d350d8640ac5e51341b07ca017b0a368a7e83` |
| Calendar | `e695b2c865703607489f8801e48277850bcaa48323f2fa9e53eb03c97e260c68` |
| Full dataset/research context | `b1c1d329990c25ff4de76f6c289a4b47eaa2c5d77d5b4dbf7dbef93c2f26f85b` |
| Feature vectors/results | `81c3cbb6269acf1bb559dff5fb454ff5102d35ed7be9bdb1fa75df8fb94df8d0` |
| Full qualification | `4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51` |
| Sanitized summary | `2432d79c8892c8942f0f35dfd13dee8a461cefd1622dc16d53d91908339ece72` |

The full qualification seal covers the CSV fingerprint, profile, rights policy,
reviewed basis/identity/calendar/actions via the context seal, features,
observations, population accounting, fold protocol/memberships, protected
holdout state and actual assessment clock.

- Private full artifact:
  `data/ff1/adjusted_qualification_20260921_clock_review/qualification.json`.
- Safe [checked-in summary](qualification_records/ff1_1a/adjusted_qualification_20260921.json).
- Safe [reviewed input evidence](qualification_records/ff1_1a/adjusted_research_review_20260921.json).
- Original HOLD qualification:
  `f30caf330ce5192a235d85d18629770d34b3b1547fac9f3dfdfdf5870210a2ed`.
- Original evidence-resolution HOLD:
  `0e6d8036f8429238a97859c65772b706aac108c0b80f4e58c30517abe5c2d2b8`.

Re-run offline with a fresh Git-ignored output directory:

```bash
.venv/bin/python scripts/qualify_reliance_adjusted_research.py \
  --input data/ff1/reliance \
  --output data/ff1/adjusted_qualification_new_run
```

A new assessment has a new assessment clock/qualification seal. Recorded
reconstruction preserves the original clock and exact seal; it is not a new
qualification. The final calendar correction changes context/feature provenance
fingerprints while leaving numeric feature values and population counts unchanged.
Earlier local trial outputs are not the authoritative result linked above.
The CLI never overwrites an earlier output directory.

## 12. Files and validation

New runtime/CLI files:

- `src/tiaf/evaluation/forecast_retrospective_contracts.py`
- `src/tiaf/evaluation/forecast_retrospective.py`
- `src/tiaf/evaluation/forecast_retrospective_io.py`
- `scripts/qualify_reliance_adjusted_research.py`

Modified runtime files:

- `src/tiaf/forecasting/research_contracts.py` — additive explicit profile/schema.
- `src/tiaf/forecasting/research_features.py` — same A2 projection with explicit schema.
- `src/tiaf/evaluation/forecast_qualification.py` — optional COLD profile/new method.
- `src/tiaf/evaluation/forecast_truth.py` — shared direction arithmetic; old FF-0 semantics unchanged.

New tests:

- `tests/unit/forecasting/test_adjusted_retrospective_research.py`
- `tests/unit/forecasting/test_adjusted_retrospective_io.py`
- `tests/unit/forecasting/test_adjusted_qualification_audit.py`

Documentation/record files (three created, five updated):

- `docs/TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md` — created.
- `docs/qualification_records/ff1_1a/adjusted_research_review_20260921.json` — created.
- `docs/qualification_records/ff1_1a/adjusted_qualification_20260921.json` — created.
- `README.md` — updated.
- `docs/MILESTONES.md` — updated.
- `docs/IMPLEMENTATION_ROADMAP.md` — updated.
- `docs/TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md` — updated.
- `scripts/README.md` — updated.

This pass creates **10** repository files and modifies **9** existing files.
Comparison with the entry hashes of 912 existing files confirms the other
**903** are unchanged, including prior HOLD/evidence-resolution records and
pre-existing uncommitted work outside these scoped edits. Original source
CSV/manifests match their provisioning hashes. They and private feature/label
artifacts remain Git-ignored; no raw market data was added to tracked files.
Final validation (2026-09-21, after the extended-session clock correction):

| Check | Exact result |
|---|---|
| New policy/IO/empirical audit coverage | 55 new tests included in the focused and full runs |
| FF-1 qualification/rights/isolation/prior audits plus new tests | **249 passed in 51.08s** |
| FF-0 semantic acceptance corpus, `pytest -q tests/acceptance/ff0` | **28 passed in 39.88s**; also included in the final full suite |
| Full `pytest -q` | **3,196 passed in 334.62s** |
| `python -m compileall -q src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS, **618 source files** |
| Markdown checks | PASS, **6 files / 283 local links**, balanced fenced blocks |
| `git diff --check` | PASS |
| CLI `--help` | PASS; explicit offline input and new private output directory |
| Persisted native reconstruction | Exact model equality and unchanged qualification fingerprint |
| Clock-only correction comparison | All numeric feature vectors, labels and eligibility counts identical |
| Dataset/prior-record preservation | Original five-file pins pass; prior HOLD records unchanged |

All Python commands used the repository `.venv/bin` tools. The focused command was:

```bash
.venv/bin/pytest -q \
  tests/unit/forecasting/test_adjusted_retrospective_research.py \
  tests/unit/forecasting/test_adjusted_retrospective_io.py \
  tests/unit/forecasting/test_adjusted_qualification_audit.py \
  tests/unit/forecasting/test_research_qualification.py \
  tests/unit/forecasting/test_research_rights_policy.py \
  tests/unit/forecasting/test_research_isolation_edges.py \
  tests/unit/forecasting/test_empirical_qualification_rerun_audit.py \
  tests/unit/forecasting/test_empirical_evidence_resolution_audit.py
```

## 13. Next step and Git

Exact next prompt:
**TIAF A7 / FF-1.2 — LOGISTIC CANDIDATE TRAINING ARTIFACT IMPLEMENTATION**.

Recommend one scoped checkpoint after review, excluding raw market data:

```text
feat(a7.ff1.1a): qualify adjusted RELIANCE retrospective research profile
```

No commit, tag or push was performed. A6 remains
`6dc2ff304aae0e87540260b092919bb91e4d4189` and FF-0 remains
`e5283c9eaa4294bd236186d663335efdf7dab236`. This pass stops before FF-1.2,
model/scaler fitting, learned forecasts or paired evaluation.
