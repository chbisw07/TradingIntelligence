# TIAF_A2.9 — Deterministic Market-State and Opportunity Baseline

## Status and purpose

**Status: IMPLEMENTED / LIVE VALIDATED; acceptance freeze pending.**

A2.9 is a transparent non-AI benchmark, not the final TradingIntelligence
recommendation engine. Future Agents must be evaluated against it rather than
replacing it. Given the same immutable evidence request and policy, it returns
the same assessment ID, scores, class, explanation codes, and ranking.

The baseline deliberately preserves opposing evidence, missing inputs,
`NO_TRADE`, and component provenance. Version 1.0 contains generic engineering
parameters; it was not fitted to RELIANCE, HDFCBANK, KAYNES, or any other live
example. A2.10/A7 evaluation may justify a new policy version, but must never
rewrite the meaning of version 1.0.

## Architecture and boundary

```text
A1 providers -> AnalysisContext
                   |
A2 feature/indicator engines -> immutable evidence bundles
                                   |
                                   v
                         tiaf.baseline (pure synthesis)
                                   |
                 assessment -> eligible-only stable ranking
```

`BaselineEngine` receives completed evidence and never imports a provider,
resolver, HTTP client, broker, Agent, LLM, LangGraph, strategy selector, or
TradeMonitor. The smoke script performs read-only acquisition outside the
engine. No current quote is inserted into completed-history calculations.

A2.9 may emit deterministic judgments because synthesis is its explicit role,
but does not emit order, option-contract, strike, strategy, target, stop, or
probability-of-profit instructions.

## Contracts and horizon

The immutable/versioned public contracts are `DeterministicBaselineRequest`,
`BaselinePolicy`, `EvidenceRule`, `EvidenceContribution`, `ScoreComponent`,
`MarketStateAssessment`, baseline `OpportunityAssessment`,
`OpportunityRankingItem`, and `OpportunityRanking`.

The request reuses A0 `TradeStyle` and `Horizon`. Both are mandatory:

- `TradeStyle.DAY` selects the intraday-oriented policy weights.
- `TradeStyle.POSITIONAL` selects the positional policy weights.
- `Horizon` retains the caller's exact label/bounds and is carried to results.

The request also retains primary and supporting timeframe order, primary
features, optional indicators, explicit-benchmark relative features, the A2.8
multi-timeframe context and aggregate features, optional derivatives facts,
explicit freshness per supplied evidence slot, requested time, and policy
version. It rejects cross-symbol, cross-context, timeframe-order, and missing
freshness mismatches. All timestamps retain the canonical aware
`Asia/Kolkata` policy and JSON emits `+05:30`.

## Policy version 1.0

All evidence selectors, exact parameters, transformations, scales, rule
weights, component weights, required components, quality factors, penalties,
direction thresholds, class thresholds, and output precision live in the
serializable frozen policy. There are separate DAY and POSITIONAL policy IDs;
both have version `1.0`.

Directional component weights are:

| Component | DAY | POSITIONAL |
|---|---:|---:|
| Directional structure | 0.17 | 0.20 |
| Trend quality | 0.18 | 0.24 |
| Momentum | 0.18 | 0.12 |
| Relative strength | 0.10 | 0.16 |
| Participation | 0.14 | 0.08 |
| Structural readiness | 0.10 | 0.07 |
| Multi-timeframe alignment | 0.13 | 0.13 |

Opportunity benefit weights are:

| Component | DAY | POSITIONAL |
|---|---:|---:|
| Directional structure | 0.10 | 0.12 |
| Trend quality | 0.12 | 0.16 |
| Momentum | 0.12 | 0.08 |
| Relative strength | 0.08 | 0.15 |
| Participation | 0.14 | 0.08 |
| Structural readiness | 0.16 | 0.10 |
| Volatility suitability | 0.11 | 0.10 |
| Remaining room | 0.09 | 0.13 |
| Multi-timeframe alignment | 0.06 | 0.06 |
| Optional derivatives context | 0.02 | 0.02 |

Each column sums to one. An unavailable optional component is excluded from
the applicable denominator; it is never inserted as zero. Required structure,
trend, or momentum evidence gates the candidate to `NO_TRADE` when missing.

## Transforms

Let `clamp(x,a,b) = min(b,max(a,x))`. Each evidence rule declares one of these
bounded transforms:

```text
SIGNED_LINEAR(x, scale) = clamp(x / scale, -1, 1)
CENTERED_LINEAR(x,c,s)  = clamp((x - c) / s, -1, 1)
UNSIGNED_LINEAR(x,l,h)  = clamp((x - l) / (h - l), 0, 1)
LOWER_BETTER(x,l,h)     = 1 - UNSIGNED_LINEAR(x,l,h)
```

`TRIANGLE(x,l,t,h)` is zero at/outside `l,h`, one at target `t`, and linearly
interpolated on each side. It rewards a usable volatility band rather than
maximum volatility. DAY ATR-percent bounds are `0.2 / 1.4 / 4.0`; POSITIONAL
bounds are `0.5 / 2.5 / 7.0`.

Every transform and intermediate public score rejects NaN/infinity. Output is
clamped to 0..100 and rounded to six decimal places only at the public edge.

## Component inventory

1. **Directional structure** uses 20-transition HH, HL, LH, and LL fractions.
   Positive and negative sides have separate capacities, preventing a paired
   one-sided feature family from being artificially capped at 50.
2. **Trend quality** uses 20-bar signed efficiency, 20-bar OLS slope percent,
   and EMA(20)-EMA(50) spread. Optional RSI(14) direction and ADX(14) strength
   are low-weight supporting facts; neither is an oracle.
3. **Momentum** uses 5- and 20-bar returns. DAY scales are 3%/7%; POSITIONAL
   scales are 6%/15%.
4. **Relative strength** uses explicit 20-bar subject-minus-benchmark spread
   and outperformance consistency. Missing benchmark makes this component
   unavailable, not neutral.
5. **Participation** uses 20-transition signed volume balance plus factual
   relative volume. It makes no institutional or smart-money claim.
6. **Structural readiness** uses position versus a fixed 20-bar prior range,
   10/20 nested range compression, and positive-only close excursions beyond
   prior high/low.
7. **Volatility suitability** uses ATR percent and the horizon triangle above.
8. **Remaining room** uses 20-bar fixed-boundary distances in ATR units.
9. **Extension/chase risk** uses EMA(20) distance in ATR, absolute 20-bar
   movement, and latest range versus the prior 20-bar average.
10. **Multi-timeframe alignment** uses A2.8 valid-contributor positive/negative
    return fractions plus agreement/disagreement. Missing intervals remain
    excluded under A2.8 denominator semantics.
11. **Derivatives context** optionally uses ATM CE/PE bid-ask spread percentages
    as expression-feasibility facts only. PCR and maximum OI do not determine
    direction or support/resistance.

Correlated measurements are grouped before cross-component weighting. The
policy does not blindly add every available indicator or duplicate the same
20-bar return fact even though that fact transparently participates in both
movement and maturity.

## Direction and disagreement

For component `c`, rule signal `s_i`, rule weight `w_i`, and policy quality
factor `q_i`:

```text
P_c = 100 * sum(w_i*q_i*max(s_i, 0)) / positive-capable weight
N_c = 100 * sum(w_i*q_i*max(-s_i,0)) / negative-capable weight

P = sum(W_c*P_c) / sum(available W_c)
N = sum(W_c*N_c) / sum(available W_c)
margin = P - N
alignment = 100 * max(P,N) / (P+N), or 0 when P+N=0
```

Quality factors are GOOD `1.0`, PARTIAL `0.8`, DEGRADED `0.55`, and
UNAVAILABLE `0.0`. Positive and negative scores are never collapsed before
publication.

Version 1.0 direction rules are evaluated in this order:

- both scores at least 42 -> `CONFLICTED`;
- strongest score below 52 -> `NEUTRAL`;
- margin at least +8 -> `POSITIVE`;
- margin at most -8 -> `NEGATIVE`;
- otherwise -> `CONFLICTED`.

A component counts as conflicting when both component-side scores are at least
35. The count remains public even when the final direction is not conflicted.

The absolute evidence floor is intentionally independent of directional
margin. For example, positive `15.319647`, negative `43.604477`, and margin
`-28.284830` is `NEUTRAL`: conflict does not apply because both sides are not
at least 42, but the stronger side is still below 52. A wide margin between two
weak scores is not enough to declare a direction.

## Component score interpretation

`ScoreComponent.score` is not a signed direction. For directional-support
components it is the 0..100 opportunity-support magnitude for the published
`score_basis_direction`, which is the stronger overall market side. The
independent `positive_score` and `negative_score` preserve opposing evidence.
An exact side-score tie uses `POSITIVE` only as the deterministic score-basis
tie-break; it does not change the published `NEUTRAL`/`CONFLICTED` direction.
For pure suitability components the score is direction-independent and the
basis is absent; for extension it is an absolute penalty magnitude.

The human smoke output therefore prints score semantics, score-basis direction,
both directional side scores, score-relevant reasons, and all factual evidence
codes separately. This makes cases such as `MOMENTUM 75 / NEGATIVE` explicit.
It also explains a legitimate `RELATIVE_STRENGTH 0 / NEGATIVE` accompanied by
`RELATIVE_OUTPERFORMANCE`: the benchmark facts support the positive side, but
give zero support to the market's currently stronger negative side. The raw
outperformance fact remains retained; it does not automatically become an
opportunity benefit.

## Opportunity, room, and maturity

For the dominant side, a component score is the rule-weighted mean of
quality-adjusted directional support and suitability. Opposing fixed-side
rules do not dilute that side's denominator. A penalty-only component reports
the weighted absolute transformed magnitude.

```text
benefit = weighted mean of available component scores
opportunity = clamp(
    benefit
    - 25 * extension_score/100
    - 15 * (1 - alignment/100)
    - quality penalty
    - explicit freshness penalties,
    0, 100)
```

Quality penalties are 0/5/15/100 points for GOOD/PARTIAL/DEGRADED/UNAVAILABLE.
Each AGING supplied source deducts 4 points and each UNKNOWN source 8. Explicit
STALE primary evidence is a hard `NO_TRADE`; stale optional evidence is not
scored. No wall-clock lookup occurs in the baseline.

For positive direction, room is the latest-close distance below prior
resistance in ATR units, capped at three ATR. For negative direction it is the
distance above prior support, also capped at three ATR. Once beyond a boundary,
version 1.0 assigns zero post-boundary room credit; it never reports negative
room or invents a target.

Both `POSITIVE_ROOM_AVAILABLE` and `NEGATIVE_ROOM_AVAILABLE` may appear under
factual evidence because both boundary distances were observed. The separate
score-relevant reason contains only the room fact selected by
`score_basis_direction`. No factual distance is removed and no target is
inferred.

Maturity/chase risk is the extension component. It is distinct from momentum:
strong movement may qualify `TOP_MOVER`, while EMA/return/range extension can
lower opportunity score or produce `MATURE_AVOID_CHASE`.

Multi-timeframe factual codes report positive, negative, agreement, and
disagreement evidence without calling every non-zero value "aligned". The
component-level reason uses existing policy thresholds without changing its
numeric score: both component sides at least 35 is `MTF_CONFLICTED`; otherwise
a component score at least the policy alignment floor 52 is `MTF_ALIGNED`; a
lower available score is `MTF_MIXED`.

## Complete policy inspection

The deterministic inspector prints both component-weight sets, all 31 rules
grouped by component, exact selectors and parameters, transforms, sign
semantics, bounds/scales/caps, raw weights, and full-evidence GOOD-quality
effective maximum direction/benefit/penalty points:

```bash
python scripts/inspect_baseline_policy.py --horizon DAY
python scripts/inspect_baseline_policy.py --horizon POSITIONAL
```

It also prints every direction/classification threshold, penalty, and quality
factor. Effective maxima are explicitly a full-evidence reference; optional
component absence causes the documented denominator renormalization.

The correlated-family review found no accidental duplicate rule. The deliberate
overlaps are bounded and visible: 20-bar return supplies direction in momentum
and absolute realized movement in extension; EMA(20)/EMA(50) spread describes
trend ordering while close-to-EMA(20) ATR distance describes extension; HH/HL
transition persistence differs from current prior-range position/breakout; and
MTF return fractions describe cross-timeframe agreement rather than adding a
second primary return rule. Slope, efficiency, EMA spread, and optional RSI/ADX
are grouped inside one normalized trend component. These are engineering
assumptions to evaluate later, not claims of statistical independence.

## Candidate classes and `NO_TRADE`

Hard missing required evidence, stale critical evidence, `NEUTRAL` or
`CONFLICTED` direction, alignment below 52, or score below the policy minimum
can produce `NO_TRADE`. After safety gates:

- extension at least 65, or remaining-room score at most 20, produces
  `MATURE_AVOID_CHASE`;
- momentum at least 70 and participation at least 52 produces `TOP_MOVER`;
- opportunity at least 50 produces `EARLY_OPPORTUNITY`;
- otherwise the result is `NO_TRADE`.

The minimum score floor is 35. Threshold comparisons are inclusive and tested.
`TOP_MOVER` is not a ranking override and is not synonymous with best
opportunity. A moderate, less-extended `EARLY_OPPORTUNITY` may have and rank by
a higher opportunity score.

## Ranking and reproducibility

Ranking requires unique subjects with the same policy ID/version, trade style,
and exact horizon. Inputs are canonicalized by symbol, then eligible (non-
`NO_TRADE`) assessments are sorted by:

1. opportunity score descending;
2. evidence quality (`GOOD`, `PARTIAL`, `DEGRADED`, `UNAVAILABLE`);
3. canonical symbol ascending.

Input order is never an undocumented tie-break. `top_n` truncates eligible
items only. If fewer qualify it returns fewer; if none qualify, `items` is an
empty tuple/JSON array. All assessments remain attached in canonical symbol
order for audit, including excluded `NO_TRADE` candidates. `input_universe`
separately retains the caller's original ordered universe without influencing
ties.

Assessment identity is UUIDv5 over canonical serialized request plus policy.
Ranking identity is UUIDv5 over canonical assessment IDs plus `top_n`.
`requested_at`, not current wall time, becomes result time. Contributions
retain rule, feature/indicator selector, raw value, normalized and weighted
signal, quality, freshness, context ID, underlying evidence IDs, and `as_of`.

## Read-only smoke

```bash
python scripts/baseline_opportunity_smoke.py \
  --symbol RELIANCE \
  --horizon POSITIONAL \
  --benchmark NIFTY \
  --timeframes 1d,1h,15m

python scripts/baseline_opportunity_smoke.py \
  --symbols RELIANCE,HDFCBANK,KAYNES \
  --horizon POSITIONAL \
  --benchmark NIFTY \
  --benchmark-map HDFCBANK=BANKNIFTY \
  --timeframes 1d,1h,15m \
  --rank
```

The caller owns every benchmark choice. A global explicit benchmark may be
combined with per-symbol overrides; the script never invents sector mappings.
Use `--json` for the complete immutable record.

## Live validation record

Read-only validation on 2026-09-07 succeeded for RELIANCE with independently
acquired 1d/1h/15m evidence and NIFTY as the explicit benchmark. The untouched
version 1.0 policy produced GOOD quality and safely returned `NO_TRADE`.

A five-symbol batch (RELIANCE, HDFCBANK, KAYNES, INFY, ICICIBANK) used NIFTY
except explicit BANKNIFTY overrides for HDFCBANK and ICICIBANK. All five safely
returned `NO_TRADE`; ranking with `top_n=5` returned zero items rather than
force-filling slots. HDFCBANK/ICICIBANK retained PARTIAL benchmark evidence,
and KAYNES retained an unavailable primary-history result. These outcomes were
recorded as validation, not used to alter weights or thresholds.

Synthetic acceptance fixtures cover short/missing/FAILED evidence, stale
critical freshness, optional absence, every direction and candidate class,
an all-`NO_TRADE` universe, deterministic ties, repeat identity, and an early
candidate outranking an already-moved candidate.

## Limitations and handoff

Version 1.0 parameters are explainable priors, not empirically calibrated
claims. There is no market-calendar-aware observation-recency policy
(DEF-007), automatic benchmark mapping (DEF-047), multi-timeframe indicator
context (DEF-048), live-forming-bar model (DEF-022), probabilistic model,
strategy choice, or execution. Optional derivatives assess spread feasibility
only; no historical/cross-expiry inference is made.

A2.10 must replay versioned requests without lookahead, measure stability and
outcomes, and compare future Agent behavior against this preserved benchmark.
Any later recalibration creates a new policy version and leaves `1.0`
reconstructable.
