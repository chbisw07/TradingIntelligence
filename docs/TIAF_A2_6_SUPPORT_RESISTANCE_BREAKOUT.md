# TIAF_A2.6 Support / Resistance / Breakout Structure

## Status and architectural role

**Status: CURRENT — implemented and live read-only validated; pending acceptance.**

TIAF_A2.6 adds deterministic, provider-neutral measurements of fixed prior
price boundaries and current completed-bar geometry. It remains inside the
accepted Feature subsystem and consumes only normalized `HISTORY` evidence
already present in `AnalysisContext`.

These primitives can support future scanners, replay, charts, rules, market
state, and reasoning. They do not decide whether an excursion is desirable,
reliable, or actionable. No feature emits a recommendation, score, target,
stop, strategy choice, or option direction.

## Information-time and anti-lookahead rule

For a request with `bars=N`, the latest completed bar is the observation being
measured. Every prior boundary is derived from exactly the N completed bars
immediately before it:

```text
prior bars = history[-N-1:-1]
current bar = history[-1]
```

The current bar can therefore cross a boundary but cannot change that
boundary. Older bars outside the exact prior window and unavailable future
bars cannot participate. No live quote is appended as a synthetic current
bar. All prior-boundary features require N+1 bars and never shorten a window.

The words support and resistance in IDs identify low/high boundary families;
they do not claim that a rolling extreme is a definitive market level.

## Feature inventory

Let `PH_N` and `PL_N` be maximum high and minimum low over the fixed prior N
bars. Let the current completed bar be `(H_t, L_t, C_t)`.

| Feature ID | Definition | Minimum input |
|---|---|---:|
| `resistance.prior_high[bars=N]` | `PH_N` | N+1 bars |
| `support.prior_low[bars=N]` | `PL_N` | N+1 bars |
| `resistance.distance_percent[bars=N]` | `(C_t-PH_N)/PH_N*100` | N+1 bars |
| `support.distance_percent[bars=N]` | `(C_t-PL_N)/PL_N*100` | N+1 bars |
| `resistance.distance_atr[bars=N,atr_period=A]` | `(C_t-PH_N)/ATR_A` | max(N+1, A+1) bars |
| `support.distance_atr[bars=N,atr_period=A]` | `(C_t-PL_N)/ATR_A` | max(N+1, A+1) bars |
| `breakout.above_prior_high_percent[bars=N]` | `max(0,(C_t-PH_N)/PH_N*100)` | N+1 bars |
| `breakdown.below_prior_low_percent[bars=N]` | `max(0,(PL_N-C_t)/PL_N*100)` | N+1 bars |
| `breakout.high_above_prior_high_percent[bars=N]` | `max(0,(H_t-PH_N)/PH_N*100)` | N+1 bars |
| `breakdown.low_below_prior_low_percent[bars=N]` | `max(0,(PL_N-L_t)/PL_N*100)` | N+1 bars |
| `structure.position_vs_prior_range[bars=N]` | `(C_t-PL_N)/(PH_N-PL_N)*100` | N+1 bars |
| `structure.prior_range_percent[bars=N]` | `(PH_N-PL_N)/((PH_N+PL_N)/2)*100` | N+1 bars |
| `structure.prior_range_atr[bars=N,atr_period=A]` | `(PH_N-PL_N)/ATR_A` | max(N+1, A+1) bars |
| `structure.range_compression_ratio[short_bars=S,long_bars=L]` | midpoint-normalized prior range S / prior range L | L+1 bars; 1<S<L |
| `structure.latest_bar_range_vs_average[bars=N]` | `(H_t-L_t)/mean(H-L over prior N bars)` | N+1 bars |

There are 15 canonical A2.6 IDs. The read-only smoke also requests 50-bar
examples for the two boundary-level IDs.

## Distance and excursion semantics

Distance features are signed. A close below a prior high has negative
resistance distance; a close above it has positive distance. A close above a
prior low has positive support distance; a close below it has negative
distance. No meaning is assigned to either sign.

Excursion features are positive-only magnitudes. No excursion and exact
boundary contact both return numeric zero. Close and wick measurements remain
separate: the latest high can exceed `PH_N` while the latest close remains
below it, and the latest low can fall below `PL_N` while the close remains
above it. The feature layer reports both facts without combining them.

## Prior-range position and width

`structure.position_vs_prior_range` differs from A2.3
`structure.position_in_rolling_range`. A2.3 includes the latest bar in its
rolling range, while A2.6 compares the current close with a prior-only fixed
range. A2.6 position is deliberately not clamped: values below zero and above
100 are valid when the current close lies outside that prior range. A
zero-width prior range yields `INSUFFICIENT_DATA`.

Prior range percentage uses the prior range midpoint, not the latest close:

```text
midpoint = (PH_N + PL_N) / 2
width_percent = (PH_N - PL_N) / midpoint * 100
```

A nonpositive midpoint is invalid. ATR-normalized distances and width reuse the
accepted A2.2 Wilder ATR helper. Wilder ATR uses all supplied chronological
history after its strict `A+1` warm-up, matching accepted A2.2 semantics. Zero
ATR produces `FAILED` rather than infinity.

## Compression and latest-bar expansion

Compression compares two nested prior-only boundary ranges ending immediately
before the current bar. Both widths use their own midpoint normalization, with
`1 < short_bars < long_bars`. Because the short range is a subset of the long
range and normalized prices are nonnegative, its high/low span cannot exceed
the enclosing long range; the ratio is therefore naturally in `[0,1]`. A zero
long-window width has no defined divisor and yields `FAILED`.

Latest-bar range comparison is a different measurement. It divides the
current raw high-low range by the mean raw high-low range of the preceding N
bars. The current range is excluded from its baseline. It may be below, equal
to, or above one. A zero prior mean yields `FAILED`.

The raw range helper and percentage range helper are shared with A2.2; the
Feature engine is never invoked recursively.

## Quality, time, and numerical safety

Every A2.6 definition requires only history. Usable results preserve its
quality without upgrade: GOOD remains GOOD, while PARTIAL/DEGRADED evidence
produces `PARTIAL` with the original quality. Failed or unavailable history
does not fabricate a level.

`as_of` and `source_observed_at` are the latest completed historical bar's
market `end_at`. Acquisition time remains separate provenance metadata. All
timestamps retain canonical aware `Asia/Kolkata` normalization, and no
calculator reads the wall clock.

Shared preparation rejects malformed OHLC envelopes, negative or non-finite
prices, duplicate timestamps, and nonchronological history. Calculators guard
nonpositive percentage boundaries/midpoints, zero-width ranges, zero ATR, and
zero range baselines. No available or partial result can carry NaN or infinity.

## Deliberate deferrals

Touch counts are deferred. A leakage-free count needs a fixed boundary derived
before a distinct inspection region, which introduces another explicit window
and minimum-history contract. A2.6 does not adopt an ambiguous shortcut.

Breakout persistence and re-entry classification are also deferred. Correct
run semantics require discovery and freezing of an event-time boundary; simply
recomputing a rolling boundary for each historical bar would change the event
retrospectively. Later deterministic market-state/replay work can model this
information time explicitly.

Swing pivots and fractals are future work because right-side confirmation uses
later bars and needs an explicit availability timestamp. Classic floor pivot
points are deferred to a later level/Indicator library because session and
calendar semantics must be explicit. No hindsight pivot is registered.

A2.6 does not combine A2.5 volume measurements with excursions. Volume-based
breakout quality, support/resistance scoring, failed-break classification,
multi-timeframe levels, anchored VWAP, volume/market profile, and strategy
interpretation remain future capabilities.

## Read-only smoke and handoff

```bash
python scripts/feature_engine_smoke.py \
  --symbol RELIANCE \
  --history-interval 1d \
  --lookback-days 180 \
  --levels
```

`--levels` may be combined with `--extended`, `--trend`, and `--volume`. It
requests 20-bar core measurements, 20/50-bar prior boundaries, ATR period 14,
and short/long compression windows of 10/50. Short history remains visibly
`INSUFFICIENT_DATA`; it is never shortened.

The next milestone is A2.7 Derivatives / Option-Chain Features. It may consume
the same stable Feature contracts but must not redefine these prior-boundary
semantics.
