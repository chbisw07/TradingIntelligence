# TIAF_A2.5 Volume / Participation Features

## Status and scope

TIAF_A2.5 adds provider-neutral, deterministic measurements of participation
from completed historical OHLCV bars. It extends the accepted A2 feature
registry and engine; it does not introduce another framework. Every definition
requires only `HISTORY` evidence, and no calculator acquires data.

Participation primitives are deliberately distinct from traditional technical
indicators. These features expose reusable factual statistics about reported
volume and its alignment with completed-bar price movement. Stateful or
convention-heavy studies remain in the Indicator subsystem introduced by A2.4.

## Feature inventory and formulas

Here, `V_t` is destination/latest bar volume, `C_t` is close, `H_t` is high,
and `L_t` is low. `N` always denotes an exact requested window; windows are
never shortened.

| Feature ID | Formula / meaning | Minimum input |
|---|---|---|
| `volume.current` | latest completed-bar `V_t` | 1 bar |
| `volume.average[bars=N]` | arithmetic mean of latest N volumes | N bars |
| `volume.median[bars=N]` | deterministic median of latest N volumes | N bars |
| `volume.relative[bars=N]` | `V_t / mean(V_(t-N)..V_(t-1))`; latest is excluded from baseline | N+1 bars |
| `volume.change_percent` | `(V_t / V_(t-1) - 1) * 100` | 2 bars |
| `volume.position_in_range[bars=N]` | `(V_t - min(V)) / (max(V) - min(V)) * 100` | N bars |
| `volume.coefficient_of_variation_percent[bars=N]` | population standard deviation / mean * 100 | N bars |
| `volume.linear_slope[bars=N]` | equally spaced OLS slope | N bars, N >= 2 |
| `volume.linear_slope_percent[bars=N]` | OLS slope / mean volume * 100 | N bars, N >= 2 |
| `volume.consecutive_increases` | latest strict adjacent-volume increase run | 1 or more bars |
| `volume.consecutive_decreases` | latest strict adjacent-volume decrease run | 1 or more bars |
| `participation.up_volume_fraction[bars=N]` | volume on rising close transitions / all transition volume | N+1 bars |
| `participation.down_volume_fraction[bars=N]` | volume on falling close transitions / all transition volume | N+1 bars |
| `participation.flat_volume_fraction[bars=N]` | volume on equal close transitions / all transition volume | N+1 bars |
| `participation.signed_volume_balance[bars=N]` | `(up volume - down volume) / all transition volume` | N+1 bars |
| `participation.return_volume_alignment[bars=N]` | Pearson correlation of absolute simple return and destination volume | N+1 bars, N >= 2 |
| `participation.range_volume_alignment[bars=N]` | Pearson correlation of `(H_t-L_t)/C_t*100` and same-bar volume | N bars, N >= 2 |

All fraction and correlation outputs are ratios. Signed balance and
correlations are bounded to `[-1, 1]`; range position is bounded to `[0, 100]`.
Slope is `volume/bar`, normalized slope is `%/bar`, and change/dispersion are
percentages.

## Transition and alignment semantics

Participation direction is close-to-close, matching the A2.3 transition
convention:

- up when `C_t > C_(t-1)`;
- down when `C_t < C_(t-1)`;
- flat when the closes are equal.

The volume assigned to each transition is the destination bar's `V_t`. Thus N
transitions need N+1 bars. The first bar supplies only the base close; its
volume is not included. Up, down, and flat fractions sum to one when total
destination volume is nonzero. Signed balance assigns `+V_t`, `-V_t`, or zero
to up, down, or flat transitions respectively, then divides by all destination
volume.

Return/volume alignment pairs each absolute simple close return
`abs(C_t/C_(t-1)-1)` with that same destination bar's volume. Range/volume
alignment pairs each A2.2 high-low range percentage with its own bar volume.
Both use ordinary Pearson correlation. If either input series has zero
variance, the result is deterministically `NOT_APPLICABLE`; no numeric value is
invented.

## Data, quality, and time semantics

Only completed historical bars participate. A live quote is never appended as
a synthetic final bar, and option-chain or historical-option OI is not used.
Underlying history quality is preserved: partial or degraded evidence cannot
be upgraded by calculation, and unavailable/failed evidence yields an explicit
non-available result.

For every usable history-derived result:

- `as_of` and `source_observed_at` equal the latest completed bar's market
  `end_at`;
- history acquisition time remains visible as provenance metadata;
- all timestamps retain the canonical TIAF `Asia/Kolkata` timezone policy.

## Numerical safety

Missing required volume produces `INSUFFICIENT_DATA`. Negative, non-integer,
NaN, or infinite volume introduced through malformed evidence produces
`FAILED`. Zero volume remains a valid fact, but a zero divisor is explicit:
relative-volume baseline, prior volume, mean volume, total transition volume,
and flat volume range cannot leak NaN or infinity. Malformed OHLC envelopes,
non-finite prices, and duplicate or out-of-order timestamps follow the shared
feature-foundation failure behavior.

The implementation reuses A2.3's pure equally spaced OLS helper and A2.2's
pure bar-range-percentage helper. It does not invoke the Feature engine
recursively and does not duplicate those formulas.

## Read-only smoke

The user-facing feature smoke accepts an independent A2.5 pack:

```bash
python scripts/feature_engine_smoke.py \
  --symbol RELIANCE \
  --history-interval 1d \
  --lookback-days 180 \
  --volume
```

`--volume` may be combined with `--extended` and `--trend`. It requests all 17
A2.5 feature IDs, with both 5/20-bar average examples and 20-bar defaults for
other parameterized measurements. A short history remains visible as explicit
insufficient data rather than silently using fewer bars. Output is factual and
does not assign market meaning or recommend action.

## Placement decisions and non-goals

Session VWAP is deferred because it needs explicit intraday session boundaries.
Anchored VWAP and volume profile likewise require additional anchoring/binning
contracts. OBV, MFI, Chaikin, and the Accumulation/Distribution Line are
traditional indicators and belong in a later Indicator-library extension,
where their canonical variants and warm-up semantics can be named explicitly.

A2.5 does not implement percentile rank because empirical tie conventions need
a separate explicit choice; range position supplies an unambiguous primitive.
It also excludes redundant above-average flags, delivery/participant statistics
without provider evidence, recommendation language, breakout confirmation,
option-chain analysis, Agents, brokers, accounts, and execution.

The next deterministic feature milestone is A2.6 Support / Resistance /
Breakout Structure. Later interpretation may consume these A2.5 measurements,
but it must not be folded back into the primitive calculators.
