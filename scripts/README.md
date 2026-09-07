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

Development and operational scripts will be added when a concrete milestone
requires them. The bootstrap baseline intentionally has no runtime scripts.
