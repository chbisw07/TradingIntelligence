# TIAF A7 / FF-1.1A — TI-native RELIANCE empirical test-data provisioning

Date: **2026-09-21, Asia/Kolkata**. Implementation and mocked acceptance complete.
The initial live attempt failed authentication; after the user refreshed the
token and explicitly authorized a retry, one bounded retry **succeeded**.

```text
RELIANCE_TEST_DATA_PROVISIONED
EMPIRICAL_FITTING_AUTHORIZED = NO
```

## 1. Classification, authority and non-goals

```text
ENGINEERING_RESEARCH_SUPPORT_ONLY
NOT_PRODUCTION_RUNTIME
NOT_PUBLIC_CAPABILITY
NOT_FINAL_DATA_ARCHITECTURE
```

**This utility is an engineering/research provisioning aid for FF-1 qualification
and tests. It does not define TI's eventual production market-data ingestion,
scheduling, storage, streaming, freshness, failover, or provider architecture.
Those remain separately governed/TBD.**

TI and TradeMonitor are separate projects. Only TI infrastructure was used; no
TM dependency, script, configuration or export was used. The brief explicitly
authorized one bounded, read-only Dhan historical-data acquisition for
RELIANCE/NSE cash equity. That authority does not include quotes, orders, trading,
position mutation, background collection or scheduling. The original authority
was used once. The user's subsequent “i updated dhan access token. pls try again.”
authorized one additional bounded request. Each invocation made one request with
no automatic retries: **two live historical requests total, one in this retry**.

No features or labels were generated from empirical data. No empirical
qualification, Logistic/scaler fitting, walk-forward forecasts, paired metrics,
calibration, ensembles, LLM/FM-LFDE, public Shell/API capability or A8 was added.
No accepted A6/FF-0 semantics or rights architecture changed.

## 2. Entry state and files changed

Entry HEAD remains `2eb522c`. The existing dirty worktree contains the preceding
accepted rights-policy changes and historical HOLD records. Those files were
preserved. This pass creates/changes exactly:

| File | Change |
|---|---|
| [scripts/provision_reliance_test_data.py](../scripts/provision_reliance_test_data.py) | New fixed-scope internal engineering provisioner |
| [tests/unit/data/providers/dhan/test_reliance_provisioning_script.py](../tests/unit/data/providers/dhan/test_reliance_provisioning_script.py) | New mock-only acceptance tests |
| [scripts/README.md](../scripts/README.md) | Internal-use command, scope, output and latest provisioning status |
| This document | Implementation, live result, validation and next gate |

No source module, dependency, registry, public capability map or production
entry point was changed in this pass. Prior provisioning/HOLD audits remain
history rather than being rewritten as successful acquisitions.

The token-refresh retry changed **only this record and `scripts/README.md`**,
and generated the five ignored local artifacts listed below. Script, tests,
source, dependencies and public contracts were unchanged during the retry.

## 3. Repository inspection and reuse

| Existing TI component | Reuse / boundary |
|---|---|
| `DhanInstrumentMaster` / `DhanInstrumentResolver` | Load existing cache without refresh; require unique RELIANCE/NSE/EQUITY mapping. Cash lookup uses native `UNIQUE_NORMALIZED`, not derivative `EXACT` semantics |
| `InstrumentQuery`, `ResolutionResult`, `InstrumentKey` | Explicit scope, ambiguity/quality/identity checks; no hard-coded security ID, fuzzy resolver or second mapping |
| `MarketDataProvider.get_historical` | Provider-neutral request boundary consumed by the export helper |
| `DhanMarketDataProvider` / `HttpxDhanTransport` | Existing authentication, request construction, normalized history and typed errors; transport closed after use; no duplicate HTTP client |
| `Settings` / `DhanConfig` | Existing `.env`/environment bootstrap, without printing values. Live root accepts only the canonical Dhan API base URL |
| `HistoricalSeries`, `OHLCVBar`, Dhan historical parser | Existing A1 daily OHLCV normalization and calendar-day boundaries; script adds bounded transport checks, not scientific qualification |
| `normalize_datetime_to_ist` / `ZoneInfo("Asia/Kolkata")` | Aware acquisition clocks and ISO daily dates; no naive `now()` or manual offset arithmetic |
| `ResearchRightsConfig`, `rights_admission` | Frozen WARN_ONLY default; actual evidence remains UNVERIFIED, with warning |
| FF `canonical_json` / `semantic_fingerprint` | Existing deterministic manifest/normalized-series identities and offline verification |
| A3 `exact_bytes_checksum` | Existing exact UTF-8 SHA-256 utility for CSV and manifest bytes; not a new hashing scheme |
| `validate_no_secrets` | Reject sensitive manifest keys; provider/config objects and arbitrary provider extras are never serialized |
| Existing script/mocked-transport conventions | Explicit `--live`, safe default exit, importable helper, temporary fixture outputs and recording transport |
| `/data/` Git-ignore convention | Fixed local research output; no licensed/raw data in tracked source |

The A1 cache/coordinator conventions were inspected. This one-shot fresh download
uses the existing provider directly; it does not install a new cache, claim an
old cache hit is a fresh acquisition, or create a scheduler. The instrument-master
cache's observation time is its file mtime and is explicitly **not** historical
capture proof.

## 4. Command, bounds and output contract

```bash
.venv/bin/python scripts/provision_reliance_test_data.py --live
```

Without `--live`, the command exits safely before settings, resolution or provider
construction. No configurable symbol, date range or output override is exposed:
only the reviewed RELIANCE request is available. A pre-existing output directory,
symlink, missing local master, absent credentials, noncanonical endpoint or
ambiguous/wrong-scope identity causes HOLD before the historical call.

One daily request uses `[2017-11-01, 2026-02-01)` in Asia/Kolkata, including the
requested January 31 date. Dhan documents `/charts/historical` for daily history
and a non-inclusive `toDate`; its 90-day limit is stated for intraday history,
not this daily request. No unsupported daily limit was invented and no automatic
chunk retry was added. [Dhan historical-data documentation](https://dhanhq.co/docs/v2/historical-data/).
The merge helper supports deterministic native chunks for tests, rejects all
duplicate daily dates and never fills gaps; live chunk count is fixed to one.

Local package (created by the successful separately authorized retry):

```text
/home/cbiswas/Documents/Work/TradingIntelligence/data/ff1/reliance/
  reliance_daily_ohlcv.csv
  source_manifest.json
  security_identity.json
  acquisition_request.json
  provisioning_manifest.json
```

CSV schema: `date,open,high,low,close,volume`; UTF-8, LF, ISO dates, ascending
daily order. No feature/label columns, imputation, adjusted prices, synthetic
rows or missing-session filling. OHLC uses the existing A1 float representation
without additional local rounding; volume is a nonnegative integer (zero is
retained). This does not certify original source-decimal precision for later FF
scientific qualification.

Before any final file is written: nonempty response, one identity/frequency,
authorized window, normalized daily boundaries, finite positive OHLC, valid
high/low envelope, nonmissing nonnegative bounded integer volume, duplicate dates
and stable order are checked. Invalid input yields HOLD, not a repaired series.
Final files are exclusively created with private permissions; existing data is
never overwritten. The provisioning manifest is written last as the success
marker. A filesystem failure may leave partial files, which must not be mistaken
for a completed package or silently replaced on a rerun.

Each companion JSON carries a semantic seal. The provisioning manifest pins
relative filenames, semantic fingerprints and byte SHA-256 values, plus the
CSV hash, rights/configuration identity and classification. Offline
`verify_package` checks these without another provider call. Raw HTTP responses
are not retained; normalized-series fingerprints are clearly distinguished
from raw response-byte fingerprints. No raw data is embedded in manifests.

## 5. Actual live attempts

### 5.1 Initial attempt — historical authentication HOLD

This subsection records the first attempt's state, before the successful retry.
The missing files and unavailable counts below describe that attempt only.

| Field | Observed result |
|---|---|
| Provider/source | TI-native Dhan, existing configured API |
| Canonical identity | RELIANCE / NSE / NSE_EQUITY / EQUITY |
| Provider security ID | **2885**, resolved dynamically at runtime |
| Resolver source | Existing local Dhan detailed instrument master; no refresh |
| Resolution timestamp | Completed before acquisition start; not separately persisted because no success package was created |
| Acquisition method | One existing `MarketDataProvider.get_historical` call via `DhanMarketDataProvider` |
| Endpoint | `POST /v2/charts/historical` |
| Interval | `1d` |
| Request window | 2017-11-01 inclusive; 2026-02-01 exclusive |
| Acquisition start | **2026-09-21T11:22:43.761556+05:30** |
| Failure observed / attempt stopped | **2026-09-21T11:22:43.944641+05:30**; not successful acquisition completion |
| Response status | **ProviderAuthError, DH-901** |
| Request attempts / retries | **1 / 0** |
| Chunks | One bounded planned request; no accepted chunk |
| Delivered coverage / first / last date | Not available |
| Row count / duplicate count / CSV size | Not available, **not zero** |
| Transport validation | No accepted OHLCV response to validate; authentication failed first |
| Dataset path | Expected path above; CSV does not exist |
| Source/security/acquisition/provisioning JSON | Not created |
| Dataset / manifest fingerprints | Not available; no fabricated success hashes |
| Raw HTTP response retention | Not retained |
| Price basis / corporate-action evidence | UNKNOWN |
| Historical availability / PIT | UNKNOWN; no per-bar availability inferred |
| Rights | UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING at research-policy level |
| Empirical-fitting authority | NO |

No arbitrary provider error body or credential value was printed. The script
reports a typed error plus the bounded `DH-901` code. This establishes rejection
at Dhan's authentication/authorization boundary; it does **not** distinguish an
expired token from an invalid client/token pairing. No credential was modified,
refreshed or borrowed from TM.

The local master byte SHA-256 remains
`6e65523933d51e6aad54cb4b3cff4f27708fe0e4710a8c03f239da666f674fd2`.
It supports current instrument resolution, not qualified historical identity.
The native NSE schedule/price-basis/PIT scientific gates are unchanged; none was
fabricated to compensate for the failed acquisition.

### 5.2 User-authorized retry — successful provisioning

The existing command was rerun once after the user's token update, without
reading/printing credentials or changing code. Destination absence and Git-ignore
were checked first. No existing dataset was overwritten.

| Field | Observed result |
|---|---|
| Credential / live status | Configured credentials accepted for this historical request |
| Identity / provider ID | RELIANCE / NSE / NSE_EQUITY / EQUITY; **2885**, dynamically resolved |
| Resolution timestamp | **2026-09-21T12:07:50.652429+05:30** |
| Resolver / master | Existing TI Dhan resolver and unchanged cached master; no refresh |
| Acquisition path | `MarketDataProvider.get_historical` → `DhanMarketDataProvider` → existing `HttpxDhanTransport`; `POST /v2/charts/historical` |
| Acquisition start | **2026-09-21T12:07:50.682638+05:30** |
| Acquisition end | **2026-09-21T12:07:50.995917+05:30** |
| Elapsed request / normalization | **0.313279 seconds**, recorded end minus start; not an isolated network-latency measurement |
| Requested window | Daily, 2017-11-01 through 2026-01-31 inclusive; API end 2026-02-01 exclusive |
| Delivered coverage | **2017-11-01 through 2026-01-30**; no completeness/calendar certification implied |
| Rows / duplicate dates | **2,045 / 0** |
| CSV size / schema | **99,118 bytes**; `date,open,high,low,close,volume` |
| Response / transport validation | `NORMALIZED_RESPONSE_ACCEPTED` / PASS |
| Chunks / automatic retries | **1 accepted chunk / 0**; one historical request in this invocation |
| Acquisition semantics | `FRESH_HISTORICAL_DOWNLOAD`; actual current acquisition clock, no fabricated old capture |
| Price basis / corporate-action evidence | UNKNOWN / UNKNOWN |
| PIT / historical availability | UNKNOWN; no per-bar operational availability inferred |
| Calendar / historical identity qualification | NOT_PERFORMED / NOT_PERFORMED |
| Rights | UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING; `RIGHTS_NOT_APPROVED_RESEARCH_ONLY` |
| Raw HTTP responses | Not retained; normalized-series fingerprint is not a raw-response byte hash |
| Output | All five files in `data/ff1/reliance/`; each Git-ignored, mode `0600`; directory mode `0700` |
| Offline verification | PASS; no additional provider call |
| Empirical-fitting authority | **NO** |

Content identities from the actual artifacts:

| Artifact / identity | Value |
|---|---|
| CSV byte SHA-256 | `d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6` |
| Source manifest semantic fingerprint | `3d1a4e21b6f4d08cb94b29d0aac83ec368c3c79c40bc535f2a75da55fb452c09` |
| Security identity semantic fingerprint | `8ba737a541bb8a12b94ea0f6664270731fd9450d4310b6ca17a3d5b077440579` |
| Acquisition request semantic fingerprint | `9561d3f62a8f9c5bfbfab7c5b8d029bf6ee2c873f16912f28e7a91539c2717d7` |
| Provisioning manifest semantic fingerprint | `c54cbf1c7ba1d11a8166aec3a9c10a72efbc95446cc5cc240692fd1b6410e272` |
| Native normalized-series fingerprint | `d9adeb6bfc0df589084fdd90eb9aba45485ceb92546ee90791106ad86b3c3582` |
| Rights configuration fingerprint | `2ca6488c4b09e6437e246f91bfc227c6376c01849498d06df2fb038b5a64d981` |

The offline package verifier checked CSV bytes, companion byte hashes and all
manifest semantic seals against the provisioning manifest. Independent read-only
CSV checks confirmed the six columns, UTF-8/LF, ascending unique ISO dates inside
the authorized window, finite positive OHLC with valid envelopes, and nonnegative
integer volume. Secret-key guards passed for all manifests. These are transport
and artifact-integrity checks, **not** an empirical scientific qualification.

## 6. Validation

The initial implementation gates below ran before this token-refresh retry;
mocked acceptance passed before the first live call. No test made a live
provider request.
Positive tests traverse the real TI resolver and provider/normalizer with mocked
master data and transport, using a different synthetic security ID to prove the
ID is not hard-coded. Negative tests cover wrong scope/identity, ambiguity,
duplicates, invalid OHLC/volume, empty/out-of-window data, unsafe output paths,
existing outputs, offline tampering and secret-key rejection. Other tests prove
stable chunk merge/order/fingerprints, IST date handling, zero factual volume,
fresh-acquisition metadata, safe no-live behavior and no public capability change.

| Gate | Result |
|---|---|
| New exporter tests alone | **26 passed**, 1.20s |
| New exporter plus existing historical-provider tests, pre-live | **43 passed**, 1.16s |
| Dhan provider regression, post-live | **211 passed**, 1.47s |
| Full repository `pytest -q` | **3,094 passed**, 341.92s; no failures or warnings |
| `ruff check src tests scripts` | PASS |
| `mypy src tests scripts/provision_reliance_test_data.py` | PASS; 611 files |
| `python -m compileall -q src scripts` | PASS |
| CLI without `--live`; `--help` | PASS; no acquisition |
| Output inventory | No `data/ff1/reliance/` directory or completed package created |
| Git-ignore | Planned CSV/source/provisioning paths match `/data/` rule |
| Historical HOLD/audit records | Preserved byte-for-byte |
| Documentation / whitespace / worktree preservation | PASS; seven local targets, balanced fences, explicit new-file whitespace checks, four historical byte hashes and preceding tracked diff unchanged |

All initial engineering gates passed, but did not override the first attempt's
live DH-901 HOLD. That acquisition blocker was resolved only by the subsequent
successful live request in §5.2. Test counts overlap and must not be added together.

Retry validation (no runtime code change):

| Gate | Result |
|---|---|
| `.venv/bin/pytest -q tests/unit/data/providers/dhan` | **211 passed**, 1.52s |
| Offline `verify_package` and independent CSV checks | PASS; 2,045 rows, no duplicate dates, five manifests/data artifacts verified |
| Git-ignore / private permissions | PASS for all five artifacts; no raw data staged/tracked |
| Provisioner source byte hash | Unchanged: `591a3cb2fb490c307f56fdc9c555945f217160e911e76ccbfb9517975172f50a` |
| Historical HOLD/audit documents and preceding tracked changes | Preserved; four historical byte hashes and pre-existing tracked diff unchanged |
| `git diff --check` / updated document links and fences | PASS |
| Full pytest / Ruff / mypy / compileall | Not rerun for this acquisition-only retry; previous passing results above retained, not claimed as new runs |

The mock recording transport observes only `/charts/historical`; no quote/order
method is called. The script contains no broker mutation path and imports no TM
code. Existing public capability count remains nine. Unit tests may exercise
synthetic formulas elsewhere in the repository; no real downloaded dataset was
used for features, labels or fitting.

## 7. Remaining gates and exact next step

**No provisioning blocker remains.** The authentication failure is retained as
history in §5.1; the authorized retry succeeded with actual persisted artifacts.
Do not rerun the live utility over this package: it deliberately refuses existing
destinations. No automatic repeated acquisition or scope expansion is authorized.

Exact next prompt title:

**TIAF A7 / FF-1.1A — EMPIRICAL QUALIFICATION RERUN**.
Provisioning does not authorize fitting or pass PIT, corporate-action, calendar,
feature/label or fold qualification automatically. These scientific gates remain
unperformed for this empirical dataset. `EMPIRICAL_FITTING_AUTHORIZED = NO`.

Recommended reusable-utility commit after review (not executed):
`testdata(a7.ff1): add bounded TI-native Dhan history provisioner`.
Never commit raw market data. No tag; no commit/tag/push performed.
