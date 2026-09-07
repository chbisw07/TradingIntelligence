# TIAF A2.3 Trend and Structure Features

## 1. Scope and boundary

TIAF_A2.3 extends the accepted A2.1 engine and A2.2 measurement library with
deterministic moving-average, close-path, and adjacent-bar structure features.
Every calculation consumes completed normalized history already present in one
immutable `AnalysisContext`.

These features measure price structure. They do not interpret a measurement as
a recommendation, signal, opportunity, confidence judgment, option choice,
target, stop, or execution action. No A2.3 calculator accesses a provider,
resolver, cache, network, clock, broker, LLM, Agent, or workflow. Current quote
data is deliberately excluded.

The built-in registry contains 53 definitions: 7 from A2.1, 23 from A2.2, and
23 from A2.3.

## 2. Moving averages

For period `P`, `trend.sma[period=P]` is the arithmetic mean of exactly the
latest P completed closes:

```text
SMA(P) = sum(latest P closes) / P
```

It requires P bars and reports P as its lookback.

`trend.ema[period=P]` uses the canonical multiplier:

```text
alpha = 2 / (P + 1)
```

It initializes from the arithmetic mean of the first P supplied chronological
closes, then incorporates every remaining supplied close in order:

```text
EMA_seed = mean(first P closes)
EMA_t = alpha * close_t + (1 - alpha) * EMA_(t-1)
```

EMA requires at least P bars. Unlike SMA's exact latest-P window, a warmed EMA
uses all supplied bars because its recursive state contains their history. A
period of one is valid and yields the latest close. It is never initialized
from the first close unless `P=1`.

## 3. Distance and spread

All references use completed historical closes:

```text
trend.distance_from_sma_percent[period=P]
    = ((latest_close / SMA(P)) - 1) * 100

trend.distance_from_ema_percent[period=P]
    = ((latest_close / EMA(P)) - 1) * 100

trend.sma_spread_percent[fast_period=F, slow_period=S]
    = ((SMA(F) / SMA(S)) - 1) * 100

trend.ema_spread_percent[fast_period=F, slow_period=S]
    = ((EMA(F) / EMA(S)) - 1) * 100
```

Spreads require `F < S` and at least S bars. A nonpositive denominator makes
the calculation `FAILED`; no zero or infinity is fabricated. These are signed
distances, not crossover events or classifications.

## 4. Linear regression

The following features use exactly the latest `B` closes with equally spaced
`x = 0 ... B-1` and ordinary least squares:

- `trend.linear_slope[bars=B]`: regression slope in price per bar;
- `trend.linear_slope_percent[bars=B]`: `slope / mean_close * 100`, in percent
  per bar;
- `trend.linear_r2[bars=B]`: coefficient of determination in `[0, 1]`.

Each requires `B >= 2` and at least B bars. A zero mean makes normalized slope
undefined and `FAILED`. A perfectly constant close series has slope `0` and
R-squared `1.0`: the fitted constant line explains the path exactly even though
there is no variation. Numerical round-off in R-squared is bounded to `[0, 1]`.

## 5. Directional efficiency

`bars=B` means B transitions and therefore requires B+1 closes:

```text
displacement = latest_close - close[-1-B]
path_length = sum(abs(close_t - close_(t-1))) over B transitions

trend.directional_efficiency = abs(displacement) / path_length
trend.signed_efficiency = displacement / path_length
```

The unsigned range is `[0, 1]`; the signed range is `[-1, 1]`. A constant path
has zero displacement and zero path length. Both features deterministically
return `0.0`, representing no directional movement. No interpretation is
attached to either sign or magnitude.

## 6. Close-transition persistence

The latest exact B transitions require B+1 closes:

```text
trend.up_close_fraction[bars=B]   = count(close_t > close_(t-1)) / B
trend.down_close_fraction[bars=B] = count(close_t < close_(t-1)) / B
trend.flat_close_fraction[bars=B] = count(close_t = close_(t-1)) / B
```

Every transition belongs to exactly one group, so the three results sum to
one, subject only to floating-point representation.

`trend.consecutive_up_closes` and `trend.consecutive_down_closes` count the
immediately trailing strict run. They require at least two closes. Equality or
movement in the other direction terminates the run and can produce zero. The
result is an integer number of transitions.

## 7. Adjacent high/low structure

The structure features use deterministic adjacent comparisons rather than
subjective swing-point detection. For B comparisons, each requires B+1 bars:

```text
structure.higher_high_fraction = count(high_t > high_(t-1)) / B
structure.lower_high_fraction  = count(high_t < high_(t-1)) / B
structure.higher_low_fraction  = count(low_t > low_(t-1)) / B
structure.lower_low_fraction   = count(low_t < low_(t-1)) / B
```

Equality is neither higher nor lower, but remains in the fixed denominator.
The four fractions derive from one shared comparison-count calculation.
Separate public count features were intentionally omitted because they add no
information beyond `fraction * B` and could drift from the fraction semantics.

## 8. Position in rolling range

`structure.position_in_rolling_range[bars=B]` uses exactly the latest B
completed bars:

```text
rolling_high = max(high over B bars)
rolling_low = min(low over B bars)
position = ((latest_close - rolling_low) / (rolling_high - rolling_low)) * 100
```

It requires B bars. The normal range is 0–100 because the latest close belongs
to the measured bars. A zero rolling range produces value-less
`INSUFFICIENT_DATA`. This feature is distinct from A2.2's quote-sourced current
session `price.position_in_day_range`.

## 9. ATR-normalized moving-average extension

The completed-history features are:

```text
trend.distance_from_sma_atr[ma_period=M, atr_period=A]
    = (latest_close - SMA(M)) / Wilder_ATR(A)

trend.distance_from_ema_atr[ma_period=M, atr_period=A]
    = (latest_close - EMA(M)) / Wilder_ATR(A)
```

They reuse A2.2's exact Wilder ATR helper and require at least
`max(M, A+1)` bars. Wilder ATR and EMA incorporate all supplied history after
their strict initialization; the result records that full supplied lookback.
A zero ATR produces `FAILED`. Both ingredients use the same history evidence,
so there is no artificial second source or quality upgrade.

## 10. Minimum bars and exact windows

| Family | Parameter meaning | Minimum observations |
|---|---|---:|
| SMA / SMA distance | latest P bars | P |
| EMA / EMA distance | P-bar warm-up, then all supplied bars | P |
| MA spread | slow-period warm-up | slow period |
| slope / normalized slope / R-squared | latest B closes | B, with B >= 2 |
| efficiency | latest B transitions | B+1 |
| up/down/flat fraction | latest B transitions | B+1 |
| consecutive run | trailing transition run | 2 |
| high/low structure fraction | latest B comparisons | B+1 |
| rolling-range position | latest B bars | B |
| MA distance in ATR | MA and Wilder ATR warm-up | max(M, A+1) |

Positive integer parameters are mandatory. No calculator shortens a requested
window or substitutes a smaller warm-up.

## 11. Quality, provenance, and time

Every A2.3 result consumes only `("history",)` and inherits the history
evidence quality unchanged. Usable partial, degraded, or stale history yields
`PARTIAL` with the original lower quality; it never becomes `GOOD`.

`as_of` and `source_observed_at` use the latest historical bar's market
`end_at`, not acquisition time. Metadata separately retains the history
acquisition timestamp and latest bar boundaries. No calculation reads the wall
clock. Accepted A2.1 acquisition-time behavior remains unchanged.

## 12. Dhan daily timestamp convention

Dhan documents historical timestamps as epoch values but does not document
them as prior-session end boundaries. The accepted A1 adapter converts the
provider epoch to Asia/Kolkata, treats that India calendar date as the daily
bar start, and constructs a half-open midnight-to-midnight bar ending one day
later.

Consequently, a completed Sep-4 bar has normalized `start_at` Sep-4 00:00 and
`end_at` Sep-5 00:00; A2.3 reports the latter as its market `as_of`. This is a
TIAF normalized bar-boundary convention, not evidence that Dhan assigns the bar
to Sep-5. Ordered calculations depend only on validated chronological bars, so
no A1 timestamp change is required.

## 13. Numerical safety

Shared preparation rejects malformed high/low envelopes, negative or
non-finite prices, duplicate timestamps, and nonchronological bars even if an
invalid model was constructed without validation. Calculators explicitly
handle insufficient warm-up, zero averages, zero mean close, zero path length,
zero rolling range, and zero ATR. No usable result can contain NaN or infinity.

## 14. Smoke inspection

The concise A2.1 view remains the default. A2.3 completed-history measurements
can be added independently:

```bash
python scripts/feature_engine_smoke.py \
  --symbol RELIANCE \
  --history-interval 1d \
  --lookback-days 90 \
  --trend
```

Use `--extended --trend` to combine the A2.2 and A2.3 views. Default trend
periods are 10, 20, and 50 for human inspection only; calculator parameters
accept any positive period satisfying the available history.

## 15. Deferred work and A2.4 handoff

ADX, plus/minus directional indicators, subjective swing points, categorical
trend labels, and public structure-count duplicates are intentionally deferred.
ADX would materially enlarge the Wilder directional-movement surface and
deserves its own rigorously scoped follow-up if required.

A2.4 may add deterministic volume and participation measurements without
changing these completed-price semantics. Interpretation remains outside A2.
