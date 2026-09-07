# TIAF_A2.7 — Derivatives / Option-Chain Features

## Status and role

**Status: COMPLETE / LIVE VALIDATED** at tag `tiaf-a2.7`.

TIAF_A2.7 converts the provider-neutral `OptionChainSnapshot` already embedded
in `AnalysisContext` into deterministic facts. Calculators perform no provider,
network, resolver, cache, broker, Agent, or recursive feature-engine calls.
The evidence path remains provider → A1 normalization → one explicit-expiry
context snapshot → A2.7.

## Snapshot and expiry semantics

Every result uses exactly `AnalysisContext.requirements.option_expiry` and
requires the embedded chain expiry to match. Expiries are never mixed. A past
expiry is malformed for this live-chain family and fails safely. The two expiry
features are:

- `derivatives.expiry_date`: the expiry as an ISO-8601 date string;
- `derivatives.days_to_expiry`: calendar days from the chain `observed_at`
  date to expiry. Zero DTE is valid.

The chain `observed_at` remains the feature `as_of`. Dhan currently supplies no
authoritative exchange event time for this response, so A1 records acquisition
time with `option_chain_acquisition_time_no_authoritative_market_timestamp`.
A2.7 preserves that statement and does not fabricate market time. All
datetimes remain aware and normalized to canonical `Asia/Kolkata`.

## Strike geometry and ATM

Calculations defensively sort positive finite numeric strikes ascending, reject
duplicates, and validate each supplied CE/PE side against its exact strike,
side, and expiry. CE and PE are keyed by strike; list adjacency is never a
pairing rule.

ATM is the listed strike minimizing `abs(strike - underlying_ltp)`. An exact
equal-distance tie chooses the lower strike. Geometry uses only the chain's own
`underlying_ltp`; quote LTP is not substituted. Spot must be positive for ATM
and spot-normalized measurements.

`derivatives.atm_distance_percent` is:

```text
(chain_underlying_ltp - atm_strike) / chain_underlying_ltp * 100
```

`derivatives.strike_count` reports the chain's unique listed-strike count.
Irregular spacing is safe because selection uses actual sorted list positions,
not fabricated strike increments.

## Exact ATM-centered windows

Every windowed request has an explicit nonnegative `strikes_each_side=N`.
The selected set is ATM plus exactly N lower and N higher listed strikes. A
full `2N+1` window is required. If either edge has fewer strikes, the feature
returns `INSUFFICIENT_DATA`; it does not silently shrink the window. Result
metadata reports N, requested and actual counts, and the selected bounds.
`N=0` is a valid single-ATM-strike window.

All CE and PE ratio operands use the same selected strike set. No outside tail
can leak into a calculation.

## Premium, IV, Greeks, and spreads

ATM CE/PE LTPs are provider-supplied facts. The combined ATM premium is CE LTP
plus PE LTP. Its spot percentage is that sum divided by the chain underlying
LTP and multiplied by 100. It is deliberately not modeled or named as an
expected move.

ATM CE and PE IV values are preserved exactly. Mean IV is `(CE IV + PE IV)/2`;
IV difference is `CE IV - PE IV`. A2.7 does not recompute IV.

ATM delta, gamma, theta, and vega are provider-supplied and are not recomputed.
All must be finite when used; delta additionally must be within `[-1, 1]`.
Delta-50 strike selection is deferred because it is optional to the core and
should be live-validated independently before expanding the inventory.

ATM bid/ask spread percentage is:

```text
(ask - bid) / ((bid + ask) / 2) * 100
```

It requires positive finite bid and ask and `ask >= bid`. Normalized zero
placeholders or absent sides remain missing; they never become a zero spread.

## OI and option-volume primitives

Within the exact selected window:

- CE/PE totals are direct sums of nonnegative integral provider values;
- OI put/call ratio is total PE OI divided by total CE OI;
- volume put/call ratio is total PE volume divided by total CE volume;
- maximum OI reports both value and strike for each side;
- tied maximum OI selects the strike closest to ATM, then the lower strike;
- top-1 concentration is maximum side OI divided by total side OI;
- OI-weighted strike is `sum(strike * OI) / sum(OI)`.

Zero CE denominators and zero-total concentration/weighted-strike calculations
are undefined and fail safely. Zero factual OI or volume values are otherwise
retained. The ratios and maximum-OI locations carry no directional,
support/resistance, or trade interpretation.

## Missingness, quality, and numerical safety

Each feature validates only the fields it requires. Missing spread fields do
not invalidate IV, Greeks, OI, or volume. Missing required sides/fields return
`INSUFFICIENT_DATA`; present but malformed identity, sign, type, NaN, infinity,
expiry, or denominator state returns `FAILED` with no value.

Evidence status and quality propagate from the option-chain descriptor. GOOD
can remain GOOD; PARTIAL or DEGRADED is never upgraded; failed or unrequested
evidence produces no fabricated result. Feature metadata contains expiry,
snapshot, underlying-price, and time provenance, but never raw provider
payloads.

Window IV means preserve each provider-supplied value and calculate a simple
arithmetic mean independently for CE and PE over the exact selected window.

## Core inventory

The 39 registered features are:

```text
derivatives.expiry_date
derivatives.days_to_expiry
derivatives.strike_count
derivatives.atm_strike
derivatives.atm_distance_percent
derivatives.atm_ce_ltp
derivatives.atm_pe_ltp
derivatives.atm_straddle_premium
derivatives.atm_straddle_percent_of_spot
derivatives.atm_ce_iv
derivatives.atm_pe_iv
derivatives.atm_mean_iv
derivatives.atm_iv_difference
derivatives.ce_iv_mean[strikes_each_side=N]
derivatives.pe_iv_mean[strikes_each_side=N]
derivatives.ce_oi_total[strikes_each_side=N]
derivatives.pe_oi_total[strikes_each_side=N]
derivatives.oi_put_call_ratio[strikes_each_side=N]
derivatives.ce_volume_total[strikes_each_side=N]
derivatives.pe_volume_total[strikes_each_side=N]
derivatives.volume_put_call_ratio[strikes_each_side=N]
derivatives.ce_max_oi_strike[strikes_each_side=N]
derivatives.pe_max_oi_strike[strikes_each_side=N]
derivatives.ce_max_oi[strikes_each_side=N]
derivatives.pe_max_oi[strikes_each_side=N]
derivatives.ce_oi_top1_fraction[strikes_each_side=N]
derivatives.pe_oi_top1_fraction[strikes_each_side=N]
derivatives.ce_oi_weighted_strike[strikes_each_side=N]
derivatives.pe_oi_weighted_strike[strikes_each_side=N]
derivatives.atm_ce_delta
derivatives.atm_pe_delta
derivatives.atm_ce_gamma
derivatives.atm_pe_gamma
derivatives.atm_ce_theta
derivatives.atm_pe_theta
derivatives.atm_ce_vega
derivatives.atm_pe_vega
derivatives.atm_ce_bid_ask_spread_percent
derivatives.atm_pe_bid_ask_spread_percent
```

## Read-only smoke

First resolve an active expiry rather than retaining a dated example:

```bash
python scripts/dhan_option_chain_smoke.py --symbol RELIANCE
```

Then pass that exact date:

```bash
python scripts/feature_engine_smoke.py \
  --symbol RELIANCE \
  --purpose OPTION_EXPRESSION \
  --history-interval 1d \
  --lookback-days 90 \
  --include-derivatives \
  --expiry YYYY-MM-DD \
  --derivatives
```

The `--derivatives` pack requests all 39 features and uses N=5 for every
window. It is read-only and prints factual feature IDs, values, status,
quality, time, expiry, and source provenance.

## Live validation record

On 2026-09-07, Dhan reported active expiries `2026-09-29`, `2026-10-27`, and
`2026-11-23` for both RELIANCE and HDFCBANK. The complete 39-feature smoke used
the explicit `2026-09-29` expiry and succeeded for both:

- RELIANCE: chain LTP 1309.5, 101 strikes, ATM 1310, ATM CE/PE LTP
  23.85/20.7, combined premium 44.55, ATM mean IV 17.17135310550772,
  N=5 OI ratio 0.629195877245926, and volume ratio 0.6864702945581628.
- HDFCBANK: chain LTP 710.5, 64 strikes, ATM 710, ATM CE/PE LTP
  13.85/10.2, combined premium 24.049999999999997, ATM mean IV
  17.027878337903743, N=5 OI ratio 0.6111371422660087, and volume ratio
  0.6115859014713417.

Raw N=5 RELIANCE inspection confirmed CE maximum OI 7,697,000 at strike 1340
and PE maximum OI 5,423,000 at strike 1300. Ratio, concentration, and weighted
strike arithmetic matched their displayed operands and selected bounds; both
weighted strikes stayed inside the positive-OI window. ATM deltas had plausible
CE-positive/PE-negative signs and both spreads were nonnegative.

The same live RELIANCE chain contained 202 option-side records; 124 had bid and
ask normalized as missing while none lacked the four supplied Greeks. This
confirmed real missing-field evidence exists in chain tails and remains local:
the populated ATM measurements stayed available. An initial smoke run also
revealed and fixed missing derivatives-provider injection in the unified smoke
builder; reruns were complete.

## Explicit deferrals and non-goals

Historical option-bar features remain a later library over A1.4 rather than a
second subsystem inside this core. Multiple chains/cross-expiry term structure,
IV surface and wing-skew models, and OI-change temporal interpretation are
deferred until their evidence contracts are explicit. Max pain requires a
separate payoff/OI convention. Dealer GEX requires sign and positioning
assumptions not present in raw gamma/OI. Probability-of-profit and modeled
expected move are future models.

Option strategy templates, comparison/ranking, strike selection, trade
recommendations, risk targets, and execution belong to later strategy, Agent,
and TradeMonitor boundaries. A2.7 supplies only attributable factual inputs.

## Handoff to A2.8

A2.8 may combine immutable feature contexts across explicit timeframes. It must
retain this milestone's single-chain expiry, snapshot consistency, quality,
and acquisition-time provenance rather than re-fetching or reinterpreting the
derivatives evidence.
