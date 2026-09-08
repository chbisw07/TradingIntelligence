# Scripts

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

Development and operational scripts will be added when a concrete milestone
requires them. The bootstrap baseline intentionally has no runtime scripts.
