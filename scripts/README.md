# Scripts

`provision_reliance_test_data.py` is **INTERNAL / ENGINEERING_RESEARCH_SUPPORT_ONLY**.
It uses TI's existing local Dhan resolver and neutral historical-data provider
to provision one RELIANCE/NSE cash-equity daily dataset. It does not define
production ingestion, scheduling, storage, streaming, freshness or failover.
Without `--live` it exits safely without settings/provider construction or
external calls. With explicit authorization:

```bash
.venv/bin/python scripts/provision_reliance_test_data.py --live
```

The fixed request covers 2017-11-01 through 2026-01-31 (API end-exclusive
2026-02-01), with one historical request and no retries, quotes or master
refresh. Existing configuration and an unambiguous cached identity are required;
the security ID is resolved, not hard-coded. Output is restricted to the
Git-ignored `data/ff1/reliance/` directory; existing outputs/symlinks are refused.
Validation precedes CSV publication. Manifests retain fresh acquisition clocks,
hashes, UNKNOWN basis/PIT and the accepted WARN_ONLY rights policy. No features,
labels or fitting are performed. See the [implementation/live record](../docs/TIAF_A7_FF1_1A_TI_NATIVE_RELIANCE_TEST_DATA_PROVISIONING.md).
After the initial **DH-901 / ProviderAuthError**, a separately user-authorized
retry succeeded on **2026-09-21 at 12:07:50 Asia/Kolkata**: **2,045 rows**,
2017-11-01 through 2026-01-30, with offline CSV/manifest verification passing.
The five local artifacts now exist; rerunning will refuse to overwrite them.
Provisioning is not scientific qualification or fitting authorization. Next:
**TIAF A7 / FF-1.1A — EMPIRICAL QUALIFICATION RERUN**.

`dhan_option_chain_smoke.py` is an optional read-only A1.3 inspection utility.
Without `--expiry` it lists active expiries and stops; chain retrieval always
requires an explicit expiry. It uses Dhan credentials from the environment and
never prints them. Symbol-first identity resolution is supported; an optional
security ID must match the resolved underlying before provider access.

`dhan_expired_options_smoke.py` is the optional read-only A1.4 rolling-history
inspection utility. It requires an explicit underlying, option class, expiry
context, relative strike, interval, and half-open date range. The underlying ID
is resolved from its symbol or checked for exact consistency when supplied.

`dhan_instrument_resolver_smoke.py` is the credential-free A1.5 resolver
inspection utility. It supports explicit symbol/contract lookup and a
deterministic `--list-fno-underlyings` mode. Master refresh occurs only with
`--refresh`; it never fetches market data or performs trading operations.
Universe output defaults to the configured primary F&O exchange and 20 rows;
use `--exchange` to override scope and `--all-matches` for full diagnostics.

`dhan_market_data_smoke.py` likewise accepts symbol-first usage. Across all
three factual smoke utilities, a symbol/security-ID mismatch is a hard failure
before provider construction; ID-only output is derived from the master.

`data_runtime_smoke.py` is the read-only A1.6 quote path. It resolves RELIANCE
symbol-first by default, fetches through `DataFetchCoordinator`, then repeats
the request to show provider-versus-cache disposition, freshness, age, source,
and local runtime metrics. `--force-refresh` demonstrates an explicit second
gate decision and never sleeps to wait for eligibility. The demo measures cache
age from the quote's `received_at`; the nested quote still preserves Dhan's
actual `observed_at`/last-trade time, including outside market hours.

`analysis_context_smoke.py` is the read-only A1.7 context inspection path. It
combines symbol-first resolution, quote and explicit calendar-day history, and
optionally an explicit-expiry option chain through the A1.6 coordinator.
`--include-derivatives` makes that chain required; `--optional-derivatives`
requests it without making it required. Output shows Requested/Required/Status
and separates retrieval freshness/age from source observation time/age.
`--symbols RELIANCE,HDFCBANK,KAYNES` runs a sequential, order-preserving batch
with an explicit completed, partial, deferred, or error result per symbol.
Deferred rows show provider gate and retry-after details without claiming
factual unavailability or freshness. The utility never sleeps or retries
implicitly. There is no recommendation, scoring, or ranking. `--repeat`
demonstrates cache reuse.

Single-context FAILED evidence prints its safe error type/detail, provider, and
operation. Quote output also exposes the safe Dhan REST fields needed to audit
previous-close normalization; it never prints credentials or authentication
headers.

`feature_engine_smoke.py` is the read-only A2 proof path. Its concise default
retains the A2.1 current-price, history-count, fixed-window return, and high/low
range output. `--extended` adds A2.2 price location, candle structure, Wilder
ATR, realized volatility, rolling extrema, path measures, and signed move/ATR.
Previous close and current-session OHLC come from normalized quote fields;
previous close alone has a visible session-aware daily-history fallback.
Daily extended output defaults realized-volatility annualization to 252;
intraday use must pass `--annualization-factor` explicitly. The feature layer
performs no provider access. Use `--json` for immutable contracts or `--repeat`
to inspect repeatability and A1 cache reuse.

`--trend` adds the A2.3 completed-history moving-average, regression,
directional-efficiency, close-persistence, adjacent high/low structure,
rolling-range position, and ATR-extension view. It can be used alone with the
concise baseline or combined with `--extended`. Its 10/20/50 smoke periods are
inspection defaults, not calculator restrictions, and it does not mix current
quote data into historical trend measurements.

`--volume` adds the A2.5 completed-history raw/relative volume, dispersion,
slope, persistence, close-transition participation, signed balance, and
price/range correlation measurements. It can be combined with `--extended`
and `--trend`; its 5/20-bar values are inspection defaults. Short history and
undefined denominator/variance cases stay explicit, and no quote is mixed into
the historical volume calculations.

`--levels` adds the A2.6 fixed prior-boundary, signed-distance, close/wick
excursion, prior-range geometry, compression, and latest-range comparison
measurements. Every prior window excludes the latest completed bar. The smoke
uses 20/50-bar level examples, ATR period 14, and 10/50 compression defaults;
these are inspection choices rather than calculator restrictions.

`indicator_engine_smoke.py` is the dedicated read-only A2.4 path. It requests
completed history only and runs the default SuperTrend, RSI, MACD, ADX/DI,
Bollinger, and Donchian pack. Use repeatable or comma-separated `--indicator`
selectors, `--all`, `--json`, or `--repeat`. It emits indicator measurements
and minimal deterministic state without strategy or recommendation semantics.

`relative_strength_smoke.py` is the dedicated A2.8 cross-symbol path. The
caller must supply `--benchmark` and may state its MARKET, SECTOR, PEER, or
CUSTOM role. Subject and benchmark histories are acquired independently
through A1, then aligned by an exact latest common `(start_at, end_at)` suffix.
Output exposes both identities, latest endpoints, window, status, quality,
`as_of`, and the six raw relative measurements. There is no automatic benchmark
mapping or judgment about whether the chosen comparison is appropriate.

`multi_timeframe_smoke.py` is the dedicated A2.8 ordered timeframe path. Each
requested interval receives its own provider history, `AnalysisContext`, and
`FeatureBundle`; no bars are resampled. It then reports requested/available
counts and raw return-sign, EMA-position, slope-sign, agreement, and
disagreement fractions. Missing constituent results are excluded from the
valid-contributor denominator and remain visible. Dhan's accepted intraday
single-request maximum is 90 days, so a larger common `--lookback-days` value
is visibly capped for intraday intervals while daily lookback remains unchanged.

`baseline_opportunity_smoke.py` is the read-only A2.9 synthesis path. It
acquires each timeframe through accepted A1/A2 boundaries, then passes only
immutable evidence to the provider-neutral `BaselineEngine`. `--horizon` is
mandatory. `--benchmark` is an explicit common choice and repeatable
`--benchmark-map SYMBOL=BENCHMARK` entries provide explicit per-symbol
overrides; no sector mapping is invented. `--rank` and `--top-n` return only
eligible candidates, while all assessments—including `NO_TRADE`—remain in the
JSON audit record. It emits no option contract, strategy, order, target, or
stop instruction.

`inspect_baseline_policy.py --horizon DAY|POSITIONAL` requires no provider
access and deterministically prints every A2.9 component weight, evidence rule,
selector, transform, scale/cap, sign semantic, effective maximum contribution,
classification threshold, quality factor, and penalty.

`capture_baseline_snapshot.py` is the only live A2.10 utility. It acquires
normalized evidence once, writes a portable `EvidenceSnapshot` plus separate
immutable `BaselineRunRecord`, and refuses replacement unless `--overwrite` is
explicit. `replay_baseline_snapshot.py` loads that file with no provider or
resolver import and reports exact original-versus-replay equality.
`run_baseline_regression.py` accepts repeatable `--input` captured snapshot/run
files or a persisted `--corpus` directory and reports stable field-level replay
failures.

`inspect_technical_specialist.py` is the read-only A3.3 vertical smoke path. It
acquires accepted A2 evidence with an explicit symbol, horizon, benchmark, and
timeframe list; freezes the A2 fingerprint and baseline; mechanically projects
only usable scalar facts; then invokes the registered deterministic Technical
Specialist. Output includes structured dimensions, reasons, contradiction,
missing evidence, baseline agreement, fingerprint, and zero model usage. It
does not recalculate A2 facts, place trades, or call a model. Example:

```bash
python scripts/inspect_technical_specialist.py \
  --symbol RELIANCE \
  --horizon POSITIONAL \
  --benchmark NIFTY \
  --timeframes 1d,1h,15m \
  --mode deterministic
```

An existing A2.10 captured snapshot/run can be inspected entirely offline with
`python scripts/inspect_technical_specialist.py --input /path/to/capture.json`.
`--input` is mutually exclusive with `--symbol`; it performs no Dhan/provider
access and preserves the capture's A2 assessment and evidence fingerprint.

`a3_7_user_acceptance.py` is the deterministic black-box acceptance path for
the A3.7 Derivatives Context, Opportunity Quality, and Opportunity Risk
specialists. It runs six immutable profiles through the public specialist
registry/runtime composition, asserts expected interpretation families,
citations, contradictions, missing evidence, grouped confidence, A2 agreement,
zero model usage, forbidden-output absence, and exact offline record replay.
It makes no external call and requires no credentials:

```bash
python scripts/a3_7_user_acceptance.py
```

A3.8, not this script, owns general multi-specialist planning and
orchestration.

### A3.8 deterministic orchestration acceptance

`a3_8_user_acceptance.py` exercises the public planner/workflow APIs using bounded
synthetic/captured fixtures from `_a3_8_fixtures.py`. It needs no credentials and
makes **zero live provider/model calls**. Fixture transport calls are labelled as
such; partial/insufficient specialist evidence is an expected visible result.

```bash
python -m pip install -e '.[dev,orchestration]'
python scripts/a3_8_user_acceptance.py
python scripts/a3_8_user_acceptance.py --adapter serial
```

The default compares serial and pinned LangGraph execution for 14 cases, checks
offline replay, selective reruns, conditional confirmation, synthetic rate-limit
fallback, budget stops and unchanged A2 fingerprints. The serial option does not
import LangGraph. This is neither live acceptance nor a recommendation/scanner
CLI. See [the study](../docs/STUDY_A3_8_USER_LEVEL_ACCEPTANCE.md) for exact scope,
counts and limitations.

`inspect_relative_specialist.py` is the read-only A3.6 Relative Strength
Specialist path. It acquires or loads the accepted A2 request/baseline, copies
the already-computed A2.8 subject return, benchmark return, spread, ratio,
consistency, and ATR-relative excess facts, and preserves the explicit
benchmark identity. It does not recalculate those values. Example:

```bash
python scripts/inspect_relative_specialist.py \
  --symbol RELIANCE \
  --horizon POSITIONAL \
  --benchmark NIFTY \
  --benchmark-role MARKET \
  --timeframes 1d,1h,15m
```

`--input /path/to/capture.json` runs the same specialist provider-free when the
captured A2.10 request contains relative evidence. There are intentionally no
live sector/macro scripts: this repository has controlled contracts and
caller-supplied/test adapters, not trustworthy production sector/macro feeds.

`tapetide_live_acceptance.py` is the explicit A3.6.1 read-only live path. It
requires `TAPETIDE_TOKEN` in the process environment or repository `.env` and
will not run without `--live`. It launches `npx -y tapetide-mcp`, uses one
reusable MCP session for exactly 12 bounded calls, prints only sanitized
counts/statuses/fingerprints, and verifies persisted offline reconstruction
after the connector closes:

```bash
python scripts/tapetide_live_acceptance.py --live
```

Normal unit tests inject a fake connector worker and never require Tapetide,
credentials, `npx`, or network access.

`yahoo_live_acceptance.py` is the explicit read-only Yahoo secondary-provider
acceptance path. It requires `--live`, preflights `uvx`, and makes exactly nine
scheduled Yahoo calls plus one Yahoo call after a deterministic (not live)
Tapetide `RATE_LIMITED` fixture. It uses the existing connector, provider,
registry, router, normalizer, and replay contracts:

```bash
python scripts/yahoo_live_acceptance.py --live
```

Its connector launch is fixed to
`uvx --from git+https://github.com/mobatmedia/yfinance-mcp yfinance-mcp`. No
Yahoo API credential is required. The allowlist excludes options, price
history, multiple quotes, and search. Without `uvx`, the script exits before
constructing the connector and does not claim live acceptance.

`authoritative_live_acceptance.py` is the explicit bounded read-only official
source path:

```bash
python scripts/authoritative_live_acceptance.py
python scripts/authoritative_live_acceptance.py --live
```

Without `--live`, it exits without external calls. With `--live`, it performs
at most three configured HTTPS reads covering Reliance IR, NSE KAYNES
announcements, and BSE RELIANCE corporate actions. Initial and final domains are
validated before authority classification; acquired content is hashed,
normalized through the provider-neutral router, and replayed offline. The
script never crawls, submits forms, logs in, bypasses access controls, or invokes
a broker.

`deep_research_live_acceptance.py` is the explicit A3.6.2 integration path:

```bash
.venv/bin/python scripts/deep_research_live_acceptance.py
.venv/bin/python scripts/deep_research_live_acceptance.py --live
```

Without `--live`, it makes no external call. The live mode preflights `npx` and
`uvx` (including the repository virtual environment sibling executable), uses
the existing Tapetide/Yahoo adapters and authoritative gateway, and permits at
most 12 read-only calls across RELIANCE, HDFCBANK, KAYNES, and ATHERENERG. It
prints provider-neutral research counts/statuses, serializes complete
`DeepResearchResult` records, closes the live connectors, and reconstructs the
same evidence, gaps, graph, confirmation states, and semantic fingerprints
offline. It performs no model or broker call.

These are three distinct validation paths:

1. **Synthetic golden tests.**
   `tests/fixtures/evaluation/golden_manifest.json` is a golden test manifest,
   not a runnable replay corpus. The test suite reads its profiles and constructs
   stable synthetic cases programmatically. Run them with:

   ```bash
   .venv/bin/pytest -q \
     tests/unit/evaluation/test_regression_store_architecture.py \
     -k golden
   ```

2. **Captured snapshot regression.** Use `--input` for one portable captured
   snapshot/run file (and repeat the option for more files):

   ```bash
   python scripts/run_baseline_regression.py \
     --input /tmp/reliance_a210.json
   ```

3. **Replay corpus regression.** Use `--corpus` for a directory containing
   persisted snapshot and decision/run records:

   ```text
   corpus/
     snapshots/
       <snapshot-id>.json
     decision_records.jsonl
     outcome_records.jsonl   # optional
   ```

   `--corpus` loads `decision_records.jsonl` and resolves each run's snapshot
   from `snapshots/`. It does not consume `golden_manifest.json` directly.
   Golden fixtures validate deterministic behavior, captured files validate
   real persisted replay, and corpus regression validates a persisted collection
   of runs.

## A3.9 captured-input opportunity acceptance

```bash
python scripts/a3_9_user_acceptance.py
```

Runs exactly 18 persisted, offline scenarios using the public
`tiaf.service.opportunity_intelligence` API. It loads captured A3.8 records;
it does not acquire providers, run specialists, call models or start LangGraph.
Outputs are diagnostic observation states, not trade recommendations. There is
no live flag. Imported source usage and new assembly usage remain separate.
The [acceptance study](../docs/STUDY_A3_9_USER_LEVEL_ACCEPTANCE.md) records the
expected states, fixture limitations, replay checks and quality gates.

Inputs are gzip/base64-wrapped JSON captures in
`tests/fixtures/opportunity_intelligence/`, decoded by `_a3_9_cases.py` with the
standard library. This storage wrapper is only for checked-in test inputs;
public capture/replay uses ordinary JSON. Fixture authoring is test-only and
is never imported by the acceptance script.

## FF-0 internal forecasting miniature

For the separate FF-1 adjusted retrospective qualifier, see
[the bounded offline command](#ff-11a-adjusted-retrospective-qualification) below.

`forecast_miniature.py` is an engineering-only one-shot adapter using the existing
Shell parser/safety utilities. It does not add a public Shell command/capability,
REPL, provider/LLM read or broker authority. All output is versioned JSON.

```bash
.venv/bin/python scripts/forecast_miniature.py --help
.venv/bin/python scripts/forecast_miniature.py run \
  --config tests/fixtures/forecasting/ff0/local_config.json \
  --input ff-request:reliance-s21-simulated
```

The config is required; there is no default corpus or environment discovery.
This checked-in synthetic config explicitly writes `/tmp/tiaf-ff0-miniature`.
Preserve an existing corpus; use a separate config/output root for a fresh
exercise. Mode, historical as-of, cutoff and pinned profile come from the
registered packet, not a `--mode`, `--now`, model path or remote URL.

Supported verbs: `run`, independent `outcome`, exact `link`, read-only `inspect`,
and read-only `replay [--verify]`. Recorded replay never invokes a forecaster;
`--verify` explicitly adds one separately accounted pinned recomputation.
Repeated `run` creates a new run, not a replay. Historical ACTUAL inputs invoked
today remain UNAVAILABLE, with no fake issue timestamp. `GENERATED` is raw
synthetic research, not calibrated or advisory.

Exit 0 means completed operation (including domain UNAVAILABLE); 2 means invalid
command/config/admission; 1 means execution/persistence/integrity failure or
requested verification MISMATCH/UNVERIFIABLE. Inspect JSON status, not only exit 0.

See the [complete operator guide](../docs/TIAF_A7_FF0_4_ENGINEERING_CLI_ACCEPTANCE_HARDENING_IMPLEMENTATION.md#3-operator-guide)
for all commands, linkage, corpus layout, failures and observability. Test manifests
and goldens are **not** persisted replay corpora:

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_engineering_cli.py -k golden
.venv/bin/pytest -q -s tests/acceptance/ff0
```

## FF-1.1A adjusted retrospective qualification

```bash
.venv/bin/python scripts/qualify_reliance_adjusted_research.py \
  --input data/ff1/reliance \
  --output data/ff1/adjusted_qualification_review_run
```

Internal/offline only: no provider access, fitting, probabilities or public Shell
capability. Requires the existing pinned Dhan provisioning files and checked-in
reviewed calendar/identity/action evidence. It explicitly installs the adjusted
SIMULATED research profile in the COLD qualification owner; it does not change
the default captured-as-known path. 2025+ numeric values are not parsed.

Use a **new** output directory under Git-ignored `data/ff1`; existing directories
are rejected, never overwritten. `qualification.json` contains private unsealed
features/labels and exact fold memberships; keep it out of Git. `summary.json`
contains safe counts, policy/context seals and no raw market-data rows. Persisted
JSON reconstruction must match before success. Exit 0 means all qualification
gates pass, 1 means HOLD/error; invalid CLI/output scope exits 2. Qualification
does not run FF-1.2, open the holdout, approve a model or grant production rights.

The [qualification record](../docs/TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md)
documents the dataset pin, assumptions, population, fold feasibility and remaining
research limitations. The old FF-0 CLI and replay corpus format are unchanged.

## FF-1.2 Logistic candidate training (internal)

`train_ff1_logistic_candidate.py --help` documents a bounded offline Learning path.
The [FF-1.2 implementation record](../docs/TIAF_A7_FF1_2_LOGISTIC_CANDIDATE_TRAINING_ARTIFACT_IMPLEMENTATION.md)
contains the exact command, input seals, population audit and current acceptance
gate. An independent reviewer must approve the
[fixed dependency lock](../requirements/ff1-training-linux-py312.lock) before
passing its SHA-256 to `--approve-dependency-lock`. No implicit approval or install.

Four artifacts entering 2021–2024 only; 2025 and the 2024→2025 target stay sealed.
New output directory under Git-ignored `data/ff1` only, no overwrite or retries.
Train-only StandardScaler and fixed Logistic emit transparent JSON, not executable
pickles. Exit 0: complete artifacts; 1: HOLD/partial/failure; 2: invalid CLI/grant.
No forecast records, empirical quality metrics, provider calls or public `ti`
capability. Installing optional ML never becomes a replay dependency.

## FF-1.3 Logistic walk-forward generation (internal)

The exact FF-1.2 dependency stack was explicitly approved and all four empirical
fits completed. This command consumes those pinned artifacts, never fits again:

```bash
.venv/bin/python scripts/generate_ff1_logistic_forecasts.py \
  --output data/ff1/logistic_forecasts_20260921
```

That actual acceptance directory now exists; choose a new Git-ignored `data/ff1`
directory for a separately authorized rerun. Existing outputs are never overwritten.
Generation verifies exact dependency versions and lock bytes, the accepted parent
training seal, every model/scaler, and the approved qualification byte digest.
Only feature/clock/exclusion fields are decoded; test outcomes and fold outcome
summaries are not inputs. 2021–2024 only; the 2024→2025 origin is explicitly
protected and all 2025 reference origins stay outside scope. No provider/network
calls, evaluation metrics, calibration, promotion, public Shell or trading action.

Replay the actual acceptance corpus without source qualification, CSV, Ground
Truth or optional ML packages:

```bash
.venv/bin/python scripts/generate_ff1_logistic_forecasts.py \
  --corpus data/ff1/logistic_forecasts_20260921 \
  --verify-run 4dc2adb6f2bb9977bf3a06c2c5903065223cfc6e2c6a58898c0cb65090197812
```

Exit 0 means complete/MATCH, 1 means HOLD/MISMATCH, 2 means invalid CLI.
An interrupted campaign has immutable partial blobs but no complete parent;
it is not an accepted corpus. No automatic retry, resume or latest-alias selection.
Scientific IDs deduplicate origins across audit captures; do not double-weight
separately captured reruns in future evaluation. See the
[FF-1.3 record](../docs/TIAF_A7_FF1_3_LOGISTIC_WALK_FORWARD_FORECAST_GENERATION.md)
for exact lineage, counts, immutable v2 corpus layout and no-evaluation boundaries.
