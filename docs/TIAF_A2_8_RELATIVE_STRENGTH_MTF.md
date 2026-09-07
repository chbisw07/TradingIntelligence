# TIAF_A2.8 — Relative Strength, Benchmark & Multi-Timeframe Context

## Status and role

**Status: IMPLEMENTED / LIVE VALIDATED; acceptance freeze and review pending.**

TIAF_A2.8 adds provider-neutral factual comparison structures above the
accepted A1 `AnalysisContext` and A2 `FeatureBundle` contracts. Calculators do
not resolve symbols, fetch Dhan, resample bars, rank instruments, select trades,
or call Agents. The two evidence paths are:

```text
provider -> normalized subject + benchmark AnalysisContext -> relative result
provider -> one AnalysisContext/FeatureBundle per interval -> MTF result
```

All timestamps remain aware and normalize through the canonical TIAF
`Asia/Kolkata` policy. JSON timestamps therefore carry `+05:30`.

## Explicit benchmark contracts

`BenchmarkRole` has exactly `MARKET`, `SECTOR`, `PEER`, and `CUSTOM`.
`BenchmarkReference` preserves the caller-supplied symbol, role, optional
exchange, and extensible metadata. `RelativeStrengthContext` retains separate
subject and benchmark `AnalysisContext` objects, one normalized interval,
creation time, and deterministic context identity.

The caller chooses the benchmark. Calculators contain no mappings such as
RELIANCE to NIFTY or HDFCBANK to BANKNIFTY. A benchmark reference must match
the normalized benchmark context symbol and, when supplied, exchange. Subject
and benchmark symbols must differ. Automatic market/sector classification is
deferred until TIAF has an accepted provider-neutral classification source.

## Cross-symbol alignment

Relative features use only the latest contiguous suffix for which every
subject bar has the exact same `(start_at, end_at)` as its benchmark bar.
Histories may contain different total bar counts, but comparison never searches
past an incompatible latest endpoint and never pairs bars by list position or
calendar date alone. Thus a subject Sep-05 bar is not compared with a benchmark
Sep-04 bar. Duplicate, out-of-order, non-finite, negative, or malformed OHLC
bars fail before arithmetic.

Every `bars=N` return uses the final `N+1` aligned bars:

```text
return_percent = (last_close / first_close - 1) * 100
```

The minimum is therefore `N+1` exact aligned bars and positive starting
closes. Result `as_of` is the shared final aligned bar end. Metadata records
both context IDs, both symbols, benchmark role/exchange, interval, both aligned
endpoints, and the alignment rule.

## Relative feature inventory and formulas

The six features remain separate from the ordinary single-context registry
because their source contract is `RelativeStrengthContext`:

- `relative.subject_return_percent[bars=N]`: aligned subject return percent.
- `relative.benchmark_return_percent[bars=N]`: aligned benchmark return percent.
- `relative.return_spread_percent[bars=N]`: subject return minus benchmark
  return, in percentage points.
- `relative.return_ratio[bars=N]`: subject return divided by benchmark return.
  An exactly zero benchmark return is undefined and returns `FAILED`; it is not
  replaced by zero or infinity.
- `relative.excess_move_atr[atr_period=A,bars=N]`: return spread in percentage
  points divided by the latest subject Wilder ATR expressed as a percentage of
  its aligned latest close. It requires both `N+1` aligned bars and at least
  `A+1` subject history bars. Zero ATR percent is undefined and fails safely.
- `relative.strength_consistency[bars=N]`: among the same N aligned adjacent
  transitions, the fraction for which the subject simple return is strictly
  greater than the benchmark simple return. Ties are factual non-wins; no
  future transition is used.

`relative.outperformance_percent` is intentionally omitted because, without a
different window or normalization, it would duplicate return spread exactly.
Suggested 1/5/20-bar windows are caller choices rather than hard-coded limits.

## Ordered multi-timeframe contracts

`TimeframeFeatureContext` preserves one normalized interval, source context ID,
feature-bundle ID, embedded immutable `FeatureBundle` when obtained, status,
quality, `as_of`, and warnings. Explicit feature request intervals in an
embedded bundle must match the wrapper interval.

`MultiTimeframeContext` preserves caller order exactly, requires normalized
interval uniqueness, records unavailable intervals explicitly, and checks
that every bundle belongs to the same subject. Its completeness and overall
quality are validated from its members rather than trusted as caller labels.
Each interval is provider-acquired independently; there is no accepted
resampling contract in A2.8.

## Multi-timeframe factual inventory

The ten MTF features are separate from the single-context registry:

- `mtf.requested_timeframe_count`
- `mtf.available_timeframe_count`
- `mtf.positive_return_fraction[bars=N]`
- `mtf.negative_return_fraction[bars=N]`
- `mtf.price_above_ema_fraction[period=P]`
- `mtf.price_below_ema_fraction[period=P]`
- `mtf.positive_slope_fraction[bars=N]`
- `mtf.negative_slope_fraction[bars=N]`
- `mtf.directional_agreement_fraction[bars=N]`
- `mtf.disagreement_fraction[bars=N]`

Return fractions consume an exact matching `return.percent[bars=N]` from each
bundle, EMA fractions consume
`trend.distance_from_ema_percent[period=P]`, and slope fractions consume
`trend.linear_slope[bars=N]`. Positive means greater than zero and negative
means less than zero; exact zero belongs to neither fraction.

Directional agreement maps each valid return to positive, negative, or flat,
then divides the largest sign-group count by valid contributor count.
Disagreement is exactly one minus that fraction. No bullish/bearish label is
created.

Constituent minimum bars retain the accepted feature rules: return needs
`N+1`, EMA distance needs `P`, and linear slope needs `N`. Calendar lookback is
never treated as a guaranteed bar count.

## Denominator, quality, and provenance

Only one usable, parameter-exact constituent result per timeframe contributes
to a fraction. An unavailable timeframe, missing feature, mismatched parameter,
non-usable status, duplicate match, or non-finite value is listed in
`excluded_intervals`. It is not treated as a neutral zero. With contributors,
the fraction denominator is their count; excluded evidence makes status
`PARTIAL`. With no contributors, status is `INSUFFICIENT_DATA` and value is
absent.

Relative result quality is the weakest required subject/benchmark history
quality. MTF result quality is the weakest actual contributing feature quality,
while the enclosing multi-timeframe context records the weakest requested
timeframe quality. Quality is never promoted. MTF `as_of` is the oldest
contributing timeframe-context time, a conservative boundary that avoids
upgrading completed-history evidence to a later retrieval time. Metadata exposes requested,
contributing, and excluded intervals plus source bundle IDs.

## Read-only inspection

Explicit benchmark example:

```bash
python scripts/relative_strength_smoke.py \
  --symbol RELIANCE \
  --benchmark NIFTY \
  --benchmark-type INDEX \
  --benchmark-role MARKET \
  --history-interval 1d \
  --lookback-days 180 \
  --bars 20
```

Ordered timeframe example:

```bash
python scripts/multi_timeframe_smoke.py \
  --symbol RELIANCE \
  --timeframes 1d,1h,15m \
  --lookback-days 180 \
  --bars 20 \
  --ema-period 20
```

The accepted Dhan A1 adapter permits 1d and 1m/5m/15m/25m/1h history. Its
intraday endpoint has a 90-day maximum per request. The MTF smoke visibly caps
only intraday effective lookback to 90 days; it leaves daily history at the
requested duration and does not introduce hidden chunking. Use `--json` to
inspect complete immutable contracts and `+05:30` timestamp serialization.

## Deferrals and handoff

SuperTrend aggregation (DEF-048) is deferred because accepted A2.4 results live in a
separate `IndicatorBundle`; silently copying or merging them into a
`FeatureBundle` would weaken that boundary. It can be added through an explicit
multi-timeframe indicator context later. Multi-timeframe support/resistance
levels (DEF-038) likewise need an explicit context rather than premature
collapse. Alternate-timeframe resampling remains DEF-023; A2.8 uses independent
provider histories.

Automatic benchmark and sector mapping is DEF-047. Recommendation-bearing
Agents/LLMs are tracked by DEF-002, rule/strategy transitions by DEF-025,
option-expression selection by DEF-006, and the permanent execution-authority
boundary by DEF-005. Categorical strength
judgments, leadership/maturity labels, scoring, rankings, and candidate classes
are not A2.8 capabilities, but are not deferrals: A2.9 is their already-planned
deterministic baseline destination. A2.9 may consume the factual A2.1-A2.8
substrate without changing these source facts.

The complete cross-milestone rationale and revisit policy lives in the
[TIAF deferral register](TIAF_DEFERRAL_REGISTER.md).

## Live validation record

Read-only Dhan validation completed on 2026-09-07 with explicit caller-selected
benchmarks. RELIANCE versus NIFTY (MARKET) returned 121 GOOD daily bars on each
side. Both latest endpoints were exactly `2026-09-05T00:00:00+05:30`; all six
20-bar relative features were AVAILABLE. Subject/benchmark returns were
-0.9589451603236432% and -2.7388367829096927%; spread was
1.7798916225860495 percentage points, ratio 0.35012862625018365, excess move
1.090460555507326 subject ATR, and consistency 0.5.

HDFCBANK versus explicitly supplied BANKNIFTY (SECTOR) also returned 121 GOOD
daily bars per side with that same exact latest endpoint. Its 20-bar returns
were -2.5854993160054685% and -0.6525076433269827%; spread was
-1.9329916726784857 percentage points, ratio 3.9624046437565337, excess move
-1.1188766208802972 subject ATR, and consistency 0.5. These are raw arithmetic
facts; the positive ratio of two negative returns is not a strength label.

RELIANCE multi-timeframe acquisition succeeded independently for ordered 1d,
1h, and 15m contexts. All bundles were GOOD/AVAILABLE. Daily `as_of` was
`2026-09-05T00:00:00+05:30`; 1h and 15m were
`2026-09-07T15:15:00+05:30`. The aggregate conservatively used the oldest
contributor time. Dhan's 180-day daily request was preserved while both
intraday requests visibly used the accepted 90-day maximum. For the 20-bar
pack, return-sign agreement was 1.0 (all three negative), positive slope share
was 1/3, and price-above-EMA share was 1/3.

A ten-calendar-day request produced six aligned daily bars, so every 20-bar
relative request returned `INSUFFICIENT_DATA` with no value. A deliberately
invalid benchmark stopped at explicit instrument resolution. An ordered
`1d,2h,15m` request preserved the unsupported 2h bundle as
INSUFFICIENT_DATA/UNAVAILABLE; the 1d and 15m contributors remained usable,
dependent fractions were PARTIAL with denominator two, and no missing value
became neutral zero. Live JSON output preserved arrays and emitted aware
`+05:30` timestamps.

The first resolver attempt exposed one narrow A1.5 normalization defect in the
current Dhan detailed master: index rows carry `0001-01-01` as a non-applicable
expiry sentinel, which had made current indices look inactive. A2.8 normalizes
expiry to absent for all non-derivative identities; future/options retain their
existing expiry behavior. A regression protects this live-proven correction.
