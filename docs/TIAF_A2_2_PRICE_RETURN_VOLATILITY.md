# TIAF A2.2 Price, Return, and Volatility Features

## 1. Purpose and boundary

TIAF_A2.2 extends the accepted A2.1 deterministic engine with transparent
price-location, return-path, candle-range, rolling-extrema, ATR, realized-
volatility, and normalized-movement measurements. Every calculator consumes
only one immutable A1 `AnalysisContext` and one canonical `FeatureRequest`.

These values describe observed measurements. They do not classify direction,
score an opportunity, choose an option, predict an outcome, or recommend an
action. No calculator accesses a provider, resolver, cache, network, clock,
broker, LLM, Agent, or workflow.

The A2.1 public contracts and seven original feature calculations are
unchanged. The built-in registry now contains 30 definitions: the seven A2.1
features plus 23 A2.2 features.

## 2. Price and location features

`price.previous_close` is the factual previous trading-session close relative
to the current quote. One shared resolver supplies it to every dependent
feature. A finite positive normalized `QuoteSnapshot.previous_close` is the
authoritative source. In that primary case the result uses only `("quote",)`,
inherits quote quality, and uses quote `observed_at`.

If that quote field is absent, zero, or invalid, a deterministic daily-history
fallback compares the latest daily bar's India trading date with the quote
observation date:

- if the dates match, history contains the quote session, so the preceding bar
  supplies previous close and at least two bars are required;
- if latest history is earlier than the quote date, history does not contain
  the current session, so its latest bar supplies previous close;
- history later than the quote observation is inconsistent and fails safely.

The fallback never blindly chooses either `history[-1]` or `history[-2]`.
Metadata records the selected source, bar times, acquisition time, whether the
quote session was present, and a visible fallback warning. Its provenance is
`("quote", "history")` because quote time anchors session selection.

`price.open`, `price.high`, and `price.low` mean current trading-session values
from normalized quote fields. They do not use historical-bar OHLC. Missing
quote fields produce `INSUFFICIENT_DATA` rather than silently substituting an
older session.

The mixed quote/history calculations are:

```text
price.change_absolute = quote_ltp - canonical_previous_close
price.change_percent = ((quote_ltp / canonical_previous_close) - 1) * 100
price.position_in_day_range =
    ((quote_ltp - quote_session_low) / (quote_session_high - quote_session_low)) * 100
```

These session features use interval `1d`. Previous close and change need no
history when quote previous-close data is valid; fallback history needs one or
two bars according to session inclusion. Position in day range is quote-only.
A flat range produces `INSUFFICIENT_DATA`. Values outside 0–100 are retained
rather than clamped and carry a warning. If neither quote nor fallback yields a
positive previous close, dependent calculations fail without a value.

## 3. Return and path features

`return.log[bars=N]` follows A2.1 intervals-back semantics:

```text
log_return = ln(latest_close) - ln(close[-1-N])
```

It requires `N+1` bars and positive endpoint closes. The log-difference form is
mathematically equivalent to `ln(latest/base)` while avoiding intermediate
ratio overflow. Parameterized `return.percent` remains canonical; no redundant
named aliases or cumulative-return duplicate was added.

`return.max_drawdown_percent[bars=N]` scans the latest N closes, tracks the
running peak, and returns the most negative later decline:

```text
min((close / running_peak) - 1) * 100
```

Its convention is negative-or-zero. A monotonically increasing or one-bar
window returns `0`.

`return.max_runup_percent[bars=N]` scans the same exact window, tracks the
running trough, and returns the greatest later rise:

```text
max((close / running_trough) - 1) * 100
```

Its convention is positive-or-zero. A monotonically decreasing or one-bar
window returns `0`. A rise from a zero trough is undefined and produces
`FAILED`, never infinity.

## 4. Candle and true-range features

The latest-bar features are:

```text
range.true_range = max(
    high - low,
    abs(high - previous_bar_close),
    abs(low - previous_bar_close),
)
range.bar_percent = (high - low) / close * 100
range.body_percent = abs(close - open) / close * 100
range.upper_wick_percent = (high - max(open, close)) / close * 100
range.lower_wick_percent = (min(open, close) - low) / close * 100
```

True range requires two bars. Each percentage requires one bar and fails safely
when its close is zero. These are unclassified candle-shape measurements.

## 5. Wilder ATR

`volatility.atr[period=P]` computes true ranges from every adjacent pair in the
available chronological history. It requires at least `P+1` bars. The first P
true ranges initialize ATR with their arithmetic mean. Every remaining true
range is incorporated in order using Wilder smoothing:

```text
ATR_t = ((ATR_previous * (P - 1)) + TR_t) / P
```

The latest result therefore uses all supplied history after its strict warm-up;
it never silently switches to a rolling arithmetic mean.

`volatility.atr_percent[period=P]` uses the same ATR and computes:

```text
ATR / latest_close * 100
```

A zero latest close makes ATR percentage `FAILED`. Constant-price history can
legitimately produce ATR `0`.

## 6. Realized volatility

`volatility.realized[bars=N, annualization_factor=A]` requires `N+1` positive
closes and at least two log returns. It uses only the latest exact window:

```text
r_t = ln(close_t) - ln(close_(t-1))
realized_volatility = sample_stdev(r_1 ... r_N) * sqrt(A) * 100
```

The annualization factor is always explicit in the feature request. `252` is
the smoke CLI's default only for normalized daily (`1d`) history. Intraday
extended smoke use requires `--annualization-factor`; the engine never invents
one. Constant-price returns produce factual zero volatility.

No redundant unannualized feature was added.

## 7. Rolling extrema

For `bars=N`, the four features use only the latest N bars:

```text
price.rolling_high = max(high)
price.rolling_low = min(low)
price.distance_from_rolling_high_percent =
    ((latest_close / rolling_high) - 1) * 100
price.distance_from_rolling_low_percent =
    ((latest_close / rolling_low) - 1) * 100
```

All require the exact N-bar window. Zero extrema make the corresponding
distance undefined and `FAILED`. These extrema are not interpreted as support,
resistance, or a breakout state.

## 8. Signed move over ATR

`range.move_over_atr[atr_period=P]` uses the same canonical previous close as
the price-change features and combines it with historical ATR:

```text
(quote_ltp - canonical_previous_close) / latest_wilder_atr(P)
```

It requires usable quote evidence and at least `P+1` history bars. Quote
previous close remains authoritative even when the ATR history contains the
quote's current session. Positive and negative values preserve the measured
direction of the price difference. A zero ATR produces `FAILED`; no redundant
absolute variant was added.

## 9. Quality and source-time semantics

History-only results inherit history quality. Mixed results use the
deterministic worst of quote and history quality in this order:

```text
GOOD < PARTIAL < DEGRADED < UNAVAILABLE
```

An `AVAILABLE` status never implies `GOOD`; usable partial/degraded/stale input
produces `PARTIAL` status with the unchanged worst source quality.

A2.2 distinguishes acquisition time from market time:

- new history features use the latest bar `end_at` as `as_of` and
  `source_observed_at`;
- quote-sourced session features use quote `observed_at`;
- history-fallback previous close uses the selected previous-session bar end;
- mixed quote/history features use the oldest factual market observation they
  actually consume, including a fallback previous-close bar when applicable;
- metadata retains `history_acquired_at`, latest bar start/end, quote
  observation time where applicable, and an explicit source-time semantic.

A2.1 history feature timestamps remain unchanged for compatibility: their
`as_of` continues to use the A1 history evidence acquisition/observation time.
This difference is explicit and tested rather than silently rewriting accepted
A2.1 results.

## 10. Insufficiency and numerical safety

No calculator shortens a requested window. Missing or failed source evidence
and insufficient exact history produce value-less `INSUFFICIENT_DATA` or
`NOT_APPLICABLE` according to A2.1 conventions. An interval mismatch is
`NOT_APPLICABLE`.

Calculators explicitly guard zero denominators, nonpositive log inputs,
non-finite or negative OHLC values, malformed high/low envelopes,
nonchronological or duplicate timestamps, and non-finite computed results.
Unsafe calculations produce a value-less `FAILED` result with a factual
warning. NaN and infinity cannot enter a usable `FeatureResult`.

The fallback's trading-session alignment uses canonical Asia/Kolkata calendar
dates already carried by quote and daily-bar timestamps. It does not invent a
market calendar. This is deterministic for the normalized A1 daily-bar and
quote semantics, including closed-market quotes whose observation remains on
the last trading session. Dhan normally provides that market observation as
`last_trade_time`. If A1 must instead mark a quote with retrieval-time
observation metadata, a non-trading-day acquisition can be session-ambiguous;
the fallback does not guess around that missing market fact.

## 11. Smoke inspection

The accepted concise A2.1 output remains the default:

```bash
python scripts/feature_engine_smoke.py --symbol RELIANCE
```

The extended daily measurement set is:

```bash
python scripts/feature_engine_smoke.py \
  --symbol RELIANCE \
  --history-interval 1d \
  --lookback-days 90 \
  --extended
```

An intraday caller must provide its chosen annualization factor:

```bash
python scripts/feature_engine_smoke.py \
  --symbol RELIANCE \
  --history-interval 1h \
  --lookback-days 30 \
  --extended \
  --annualization-factor 1638
```

`--json` and `--repeat` retain their A2.1 behavior. The script is read-only and
prints measurements, status, quality, parameters, context identity, and
provenance without analytical opinion.

## 12. Non-goals and A2.3 handoff

A2.2 adds no moving averages, momentum indicators, trend classification,
support/resistance model, breakout interpretation, participation analysis,
derivatives analysis, score, ranking, recommendation, Agent, or execution
behavior. A2.3 can build deterministic trend and structure features on this
same stable registry/engine boundary.
