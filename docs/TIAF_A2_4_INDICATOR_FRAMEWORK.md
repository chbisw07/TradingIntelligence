# TIAF A2.4 Indicator Framework and Initial Library

## 1. Purpose and architectural boundary

TIAF_A2.4 introduces indicators as a first-class, provider-neutral subsystem.
An indicator is versioned, discoverable deterministic evidence calculated from
an existing immutable `AnalysisContext`. It is not merely another primitive
feature and it is not strategy logic.

A2.3 primitives and A2.4 indicators are complementary evidence layers. A
primitive exposes a small reusable measurement such as SMA, EMA, ATR, slope,
or range position. An indicator applies a named, versioned multi-step algorithm
and may expose several related values and a minimal factual state.

The strict layering is:

```text
indicator calculation -> deterministic indicator state -> future strategy -> future Agent
```

A2.4 implements only calculation and limited factual state. It does not emit
orders, recommendations, entry/exit conditions, rankings, confidence, option
selection, optimization, replay, LLM, Agent, LangGraph, or broker behavior.

## 2. Framework architecture

The public package is `tiaf.indicators`:

- `IndicatorDefinition` describes stable ID, independent definition and
  parameter-schema versions, typed parameters/defaults, required evidence,
  interval constraints, named outputs, allowed states, and default warm-up;
- `IndicatorRequest` carries a canonical ID, name-sorted parameters, one
  normalized interval, and required/optional role;
- `IndicatorResult` carries canonical resolved parameters, version, interval,
  typed named values/states, status, quality, market time, source identity,
  exact lookback, warnings, and safe metadata;
- `IndicatorBundle` preserves ordered results, the registry version,
  deterministic identity, aggregate quality, completeness, missing
  requirements, and warnings;
- `IndicatorRegistry` explicitly maps definitions to calculators, rejects
  duplicate IDs, and returns ID-sorted immutable discovery snapshots;
- `IndicatorEngine` performs indicator-agnostic orchestration. It contains no
  branch for RSI, MACD, or another concrete indicator.

The built-in registry is explicit. There is no filesystem discovery, dynamic
user-code import, `eval`, or plugin magic. A future proprietary calculator can
implement the same protocol and be registered without changing the engine.
The initial registry version is explicitly `1.0` and participates in bundle
identity.

## 3. Parameters and serialization

Definitions declare integer or floating parameters, defaults, descriptions,
and exclusive lower bounds. Requests accept ordinary mappings, Python/JSON
lists of pairs, or tuples; they store parameters as immutable name-sorted
tuples. Unknown parameters, missing parameters without defaults, wrong scalar
types, non-finite numbers, and invalid cross-parameter relationships are
rejected rather than ignored.

All contracts are frozen, reject unknown model fields, and inherit contract
schema version `1.0`. Indicator definition version and parameter-schema version
are independently `1.0`. Semantic collections are tuples in Python and JSON
arrays on the wire. Round-trip reconstruction preserves values, versions,
parameter order, and Asia/Kolkata timestamps. Named `IndicatorValue` and
`IndicatorState` tuples avoid arbitrary result dictionaries while retaining
multi-output extensibility.

Defaults are resolved into each result. Therefore an omitted default and the
same explicitly supplied value have the same semantic result identity.

## 4. Status, quality, provenance, and time

Indicators reuse the accepted feature statuses: `AVAILABLE`, `PARTIAL`,
`INSUFFICIENT_DATA`, `NOT_APPLICABLE`, and `FAILED`. Only available or partial
results carry values/state. An indicator failure is isolated inside a batch;
unknown indicator IDs remain typed request errors because no definition exists
from which a truthful result could be built.

All initial indicators consume only `("history",)`. They inherit history
quality without upgrade. Usable partial, stale, or degraded evidence yields a
`PARTIAL` result carrying the original quality. Future mixed-source indicators
must use deterministic worst-source quality.

Calculations use completed normalized history only. A live quote is never
inserted as a synthetic forming bar. `IndicatorRequest.interval` must match the
context history interval; the engine never fetches or resamples another
timeframe. Every usable result has `as_of` and `source_observed_at` equal to the
latest history bar's market `end_at`. Acquisition time remains separate
metadata. No calculator reads the wall clock.

## 5. SuperTrend 1.0

Parameters: `period=10`, `multiplier=3.0`. Minimum: `period+1` bars.

For each bar having a Wilder ATR value:

```text
hl2 = (high + low) / 2
basic_upper = hl2 + multiplier * Wilder_ATR(period)
basic_lower = hl2 - multiplier * Wilder_ATR(period)

final_upper_t = basic_upper_t
    if basic_upper_t < final_upper_(t-1)
       or close_(t-1) > final_upper_(t-1)
    else final_upper_(t-1)

final_lower_t = basic_lower_t
    if basic_lower_t > final_lower_(t-1)
       or close_(t-1) < final_lower_(t-1)
    else final_lower_(t-1)
```

The first warmed bar initializes both final bands from its basic bands and the
upper band as the initial line. While the upper band is active it remains
active when `close <= final_upper`; otherwise the lower band activates. While
the lower band is active it remains active when `close >= final_lower`;
otherwise the upper band activates.

Outputs are `basic_upper_band`, `basic_lower_band`, `final_upper_band`,
`final_lower_band`, and `line`. Minimal states are `relation`—`ABOVE_LINE`,
`BELOW_LINE`, or `ON_LINE`—and `active_band`—`UPPER_BAND_ACTIVE` or
`LOWER_BAND_ACTIVE`. These states are facts, not trade directions. Constant
positive history with zero ATR is valid and can produce `ON_LINE`.

## 6. RSI 1.0

Parameter: `period=14`. Minimum: `period+1` closes.

The first period close changes initialize average gain and average loss with
arithmetic means. Every later change uses Wilder smoothing:

```text
average_t = (average_(t-1) * (period - 1) + current_value) / period
RS = average_gain / average_loss
RSI = 100 - 100 / (1 + RS)
```

Zero average loss with positive gain returns 100; zero gain with positive loss
returns 0; a completely flat path with both zero returns 50. Output `rsi` is
bounded to 0–100 and carries no threshold classification.

## 7. MACD 1.0

Parameters: `fast_period=12`, `slow_period=26`, `signal_period=9`, with
`fast_period < slow_period`. Minimum:
`slow_period + signal_period - 1` closes.

Fast and slow series use A2.3's canonical EMA: each is seeded by the SMA of its
first period closes and recursively incorporates subsequent closes. Aligned
MACD values begin when the slow EMA first exists:

```text
macd_t = EMA_fast_t - EMA_slow_t
signal_t = EMA(macd_series, signal_period)
histogram_t = macd_t - signal_t
```

The signal EMA uses the same SMA-seeded convention. Outputs are `macd`,
`signal`, and `histogram`; no zero-cross or crossover state is interpreted.

## 8. ADX / +DI / -DI 1.0

Parameter: `period=14`. Minimum: `2 * period` bars.

For every transition:

```text
up_move = high_t - high_(t-1)
down_move = low_(t-1) - low_t

+DM = up_move   if up_move > down_move and up_move > 0 else 0
-DM = down_move if down_move > up_move and down_move > 0 else 0
```

Ties contribute zero to both. True range is A2.2's accepted canonical helper.
The first period TR, +DM, and -DM values are summed. Later totals use Wilder
smoothing:

```text
smoothed_t = smoothed_(t-1) - smoothed_(t-1)/period + raw_t
+DI = 100 * smoothed_+DM / smoothed_TR
-DI = 100 * smoothed_-DM / smoothed_TR
DX = 100 * abs(+DI - -DI) / (+DI + -DI)
```

The first ADX is the arithmetic mean of the first period DX values; later ADX
uses Wilder averaging. This yields the explicit `2 * period` bar warm-up.
Zero smoothed TR or zero combined DI deterministically produces zero DI/DX;
a constant market therefore returns zero for `adx`, `plus_di`, and `minus_di`.
No strength label is assigned.

## 9. Bollinger Bands 1.0

Parameters: `period=20`, `stddev_multiplier=2.0`; period must exceed one.
Minimum: exactly `period` bars. Only the latest exact close window is used.

```text
middle = SMA(period)
deviation = population_standard_deviation(latest period closes)
upper = middle + stddev_multiplier * deviation
lower = middle - stddev_multiplier * deviation
bandwidth_percent = (upper - lower) / middle * 100
percent_b = (latest_close - lower) / (upper - lower)
```

Population, not sample, deviation is deliberate. A flat positive series has
zero bandwidth and deterministic centered `percent_b=0.5`. A zero middle is
undefined and fails without values. No compression or breakout label exists.

## 10. Donchian Channel 1.0

Parameter: `period=20`. Minimum: exactly `period` bars.

```text
upper = max(high over latest period bars)
lower = min(low over latest period bars)
middle = (upper + lower) / 2
position_percent = (latest_close - lower) / (upper - lower) * 100
```

A flat channel has no defined position and yields value-less
`INSUFFICIENT_DATA`. The indicator emits no breakout condition.

## 11. Numerical safety

Shared preparation rejects unavailable evidence, insufficient strict warm-up,
interval mismatch, non-finite or nonpositive OHLC, malformed high/low
envelopes, duplicate timestamps, and nonchronological bars. Calculators handle
zero ATR, zero volatility, zero directional denominators, flat bands/channels,
and every indicator-specific denominator explicitly. No available or partial
result can contain NaN or infinity.

## 12. HalfTrend deferral

`halftrend` is deliberately not registered. Public implementations commonly
associated with the HalfTrend name differ in amplitude interpretation, channel
deviation, ATR use, state initialization, and reversal timing. No single
published, authoritative, version-stable algorithm specification was found in
the accepted repository baseline, and A2.4 does not canonize one by guesswork.

A later scoped milestone may select a named/referenceable variant, document
its provenance and formulas, assign an independent definition version, and add
known-fixture transition tests. Until then, registry discovery truthfully
reports only the six implemented indicators.

## 13. How to Add a New Indicator

1. Implement a pure calculator satisfying `IndicatorCalculator` (the shared
   history base is optional).
2. Create a versioned `IndicatorDefinition` with typed parameters, defaults,
   evidence, outputs, states, and warm-up metadata.
3. Register the calculator explicitly in an `IndicatorRegistry`.
4. Add independent known fixtures, boundary tests, and formula-reuse checks.
5. Expose it through the built-in registry only when it is accepted.
6. Do not modify `IndicatorEngine`; it has no indicator-specific branches.

This boundary supports future scanners, dashboards, replay, parameter
comparison, custom indicators, strategy engines, Agents, and SigmaDSL
references without implementing or coupling any of those systems now.

## 14. Read-only smoke inspection

The default completed-history pack is:

```bash
python scripts/indicator_engine_smoke.py \
  --symbol RELIANCE \
  --history-interval 1d \
  --lookback-days 180
```

Use `--indicator rsi`, repeated selectors, or comma-separated selectors to
narrow the pack. `--all`, `--json`, and `--repeat` are also supported. The
script requests history only and never performs an account or trading action.

## 15. Future boundary

The registry metadata is intentionally suitable for future UI discovery,
same-request multi-symbol scanners, parameter comparison, replay/optimization,
Agent evidence consumption, strategy transitions, and canonical SigmaDSL IDs.
Those capabilities remain outside A2.4. A2.5 resumes the revised deterministic
roadmap with volume and participation features.
