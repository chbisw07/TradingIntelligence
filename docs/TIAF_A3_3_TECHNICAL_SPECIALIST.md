# TIAF A3.3 Technical / Market-Structure Specialist

## Status

**TIAF_A3.2:** complete / accepted at `tiaf-a3.2`.

**TIAF_A3.3:** complete / accepted at `tiaf-a3.3`.

**Next:** TIAF_A3.4 — Fundamental Evidence and Company Quality Specialist,
implemented / pending acceptance.

Implementation began from commit
`42192121518c6fe34a3137e5cc6f2a415c119d1a`, exactly resolved by
`tiaf-a3.2`, with a clean worktree.

## Purpose and boundary

`TechnicalSpecialist` is the first concrete A3 specialist. It interprets
already-computed A2 facts; it does not calculate indicators, fetch evidence,
predict prices, select contracts, manage positions, arbitrate other
specialists, or issue trading actions. Its stable specialist identity is
`TECHNICAL`, implementation version is `1.0`, and its independently versioned
policy is `tiaf.technical-specialist` version `1.0`.

The authoritative path is deterministic and uses only
`READ_A2_EVIDENCE`. Its declared cost tier is `LOW`; it has no broker, Dhan,
HTTP, browser, filesystem, shell, model-SDK, order, position, or TradeMonitor
authority.

Policy 1.0 advertises `EQUITY` and `INDEX` instrument support. Futures and
options remain unsupported here because the current Agent request/evidence
identity does not bind an exact contract/expiry; this prevents accidental
substitution across expiries and does not change any A1/A2 derivative contract.

## Evidence seam

An A3.1 `AgentEvidenceReference` can now carry immutable scalar
`EvidenceFact` projections. A fact retains its canonical A2 feature/indicator
or baseline ID, exact scalar value, unit, parameters, output name, interval,
`as_of`, quality, freshness, and original source-evidence IDs. Lists are
accepted on validation, semantic collections become tuples, and JSON remains
ordinary arrays.

The projection helpers are deliberately mechanical:

- `feature_fact()` copies one usable scalar `FeatureResult`;
- `indicator_facts()` copies named scalar outputs from an `IndicatorResult`;
- `multi_timeframe_constituent_facts()` copies scalar facts from each retained
  independent A2.8 timeframe bundle so agreeing/disagreeing intervals remain
  visible; and
- `baseline_facts()` copies A2.9 direction, opportunity score, and candidate
  class from an `OpportunityAssessment`.

They neither invoke A2 calculators nor transform values. Vector and unusable
results cannot masquerade as scalar facts. A feature fact ID includes a stable
digest of its interval and parameters so distinct lookbacks remain distinct.

Core evidence requires at least two supplied trend observations plus supplied
structure evidence under a usable `TECHNICAL` reference. Indicators,
participation, volatility, MTF, relative context, and A2 baseline facts are
optional. Missing optional evidence yields typed `MissingEvidenceRequest`
entries and may produce a `PARTIAL` opinion; missing core evidence yields
`INSUFFICIENT_EVIDENCE` without substitution or fetching. Stale and degraded
states are retained and reduce confidence rather than being upgraded.

## Structured interpretation

The standard outer contract remains `AgentOpinionV2`. Its optional immutable
specialist-detail JSON uses schema `tiaf.technical-assessment/1.0` and
round-trips to a typed `TechnicalAssessment`. The detail records:

- trend, momentum, structure, breakout, participation, volatility, and MTF
  states;
- extension/chase state and remaining room;
- supplied-level invalidation concepts and within-domain contradictions;
- positive/negative supplied timeframes and evidence IDs by dimension;
- evidence coverage, internal agreement, confidence basis, reason codes;
- unmodified A2 direction, opportunity score, and candidate class.

Every emitted interpretive factual claim cites a supplied reference and exact
fact IDs. Claim quality and freshness equal the weakest cited reference.
Wick-only excursions are separate from confirmed close breaks. A high RSI is
positive momentum context, not an automatic bearish/reversal signal. No future
candle is used.

### Dimension semantics

- **Trend:** groups EMA distance, slope, signed efficiency, R-squared, and
  HH/HL/LH/LL structure. At least two observations are required; no single
  indicator creates a trend label.
- **Momentum:** groups RSI, MACD histogram, supplied short/medium returns, and
  move/ATR. Conflicting measurements remain visible; momentum opposing the
  trend becomes fading momentum.
- **Structure/breakout:** interprets supplied prior-range position,
  compression/expansion, HH/HL/LH/LL fractions, and causal close/wick
  excursions. It never invents pivots.
- **Participation:** interprets supplied signed volume balance and relative
  volume as confirmation, contradiction, neutral, or unusual participation;
  it makes no accumulation/distribution or “smart money” claim.
- **Volatility:** describes low, normal, elevated, extreme, compressing,
  expanding, or mixed context. High volatility is not automatically bad.
- **MTF:** interprets supplied positive/negative/alignment/disagreement
  fractions without rebuilding histories or resampling bars.
- **Extension:** uses supplied move/ATR and EMA-distance/ATR, qualified by
  participation and room. `EXHAUSTION_RISK` is a risk state, not a reversal
  forecast.
- **Remaining room:** uses only the signed A2 distance to the relevant supplied
  prior boundary. It emits no target.
- **Invalidation:** may state that a completed close through an explicitly
  supplied prior support/resistance level invalidates the interpretation. This
  is not an order or stop-loss instruction.
- **Contradiction:** preserves positive and negative dimension groups and cites
  both sides instead of forcing a clean conclusion.

## Deterministic policy 1.0

The policy uses generic engineering values, not values fitted to RELIANCE,
HDFCBANK, KAYNES, or any desired stance:

| Area | Policy 1.0 |
|---|---|
| Trend direction/strength | slope threshold 0.05%; efficiency 0.30; R² 0.60; structure margin 0.10 |
| Momentum | RSI positive 55, negative 45; overbought/oversold is not reversed |
| Participation | signed balance 0.10; unusual relative volume high 1.50, low 0.60 |
| Volatility | ATR% low 1.0, elevated 3.0, extreme 5.0; compression 0.80; expansion 1.25 |
| MTF | alignment 0.67; conflict/disagreement 0.50 |
| Extension | mature 1.5 ATR, extended 2.5 ATR, exhaustion-risk context 3.0 ATR |
| Room | large 2.0 ATR, moderate 1.0 ATR, limited above 0.25 ATR, otherwise minimal |

DAY requests select supplied `15m`, then `1h`, then `1d` observations when a
metric exists more than once. POSITIONAL requests select `1d`, then `1h`, then
`15m`. These priorities are explicit policy fields. MTF aggregate facts are
interpreted directly. No missing timeframe is fetched or reconstructed.

Correlated measurements vote inside a dimension. Final stance counts dimension
directions, not every indicator, preventing EMA, slope, SuperTrend-like, and
structure observations from manufacturing independent confidence. Three or
more positive dimensions with no negative dimension yields `POSITIVE`; the
mirror rule yields `NEGATIVE`; opposing directional dimensions yield `MIXED`;
otherwise the result is `NEUTRAL`. Core insufficiency overrides synthesis.

The stable policy-1.0 reason-code catalog is:
`TREND_UP_ALIGNED`, `TREND_DOWN_ALIGNED`, `TREND_WEAK`,
`MOMENTUM_POSITIVE`, `MOMENTUM_FADING`, `MOMENTUM_NEGATIVE`,
`BREAKOUT_CONFIRMED_CLOSE`, `BREAKOUT_WICK_ONLY`,
`BREAKDOWN_CONFIRMED_CLOSE`, `BREAKDOWN_WICK_ONLY`, `VOLUME_CONFIRMS`,
`VOLUME_DIVERGES`, `MTF_ALIGNED`, `MTF_MIXED`,
`VOLATILITY_ELEVATED`, `RANGE_COMPRESSED`, `RANGE_EXPANDING`,
`EXTENDED_FROM_MEAN`, `EXHAUSTION_RISK`,
`LIMITED_ROOM_TO_RESISTANCE`, `LIMITED_ROOM_TO_SUPPORT`,
`TECHNICAL_CONFLICT`, `OPTIONAL_EVIDENCE_MISSING`,
`CORE_EVIDENCE_MISSING`, `EVIDENCE_PARTIAL`, and `EVIDENCE_STALE`.

## Confidence and A2 comparison

Policy-derived confidence is explicitly not a success or profit probability.
It is:

```text
evidence coverage × dimension agreement × quality factor × freshness factor
```

Policy 1.0 factors are GOOD 1.0, PARTIAL 0.8, DEGRADED 0.6,
UNAVAILABLE 0.0 and FRESH 1.0, AGING 0.8, STALE 0.5, UNKNOWN 0.6.
Insufficient core evidence has value 0. Self-reported and empirically calibrated
confidence remain absent.

A2 baseline identity and fingerprint are copied unchanged. Direction mapping is
explicit: A2 POSITIVE/NEGATIVE/NEUTRAL corresponds to the same technical
stance, and A2 CONFLICTED corresponds to technical MIXED. Exact matches are
`AGREES`; a conflicted/mixed mismatch is `PARTIALLY_AGREES`; other comparable
mismatches are `DISAGREES`; missing baseline/core comparability is
`NOT_COMPARABLE`. The A2 assessment is never modified.

## No-LLM, replay, and audit behavior

No optional reasoning enrichment is implemented in A3.3. The useful baseline
path makes zero model calls, uses zero model tokens and cost units, and requires
no reasoning provider. `AgentRunRecord` retains specialist/policy versions,
evidence fingerprint, A2 assessment ID, typed opinion/detail, reason codes,
claims/citations, confidence basis, usage, and Asia/Kolkata timestamps for
future A3.10/A7 evaluation.

## Validation

Synthetic tests cover the 13 required conditions: clean bullish, clean bearish,
sideways, bullish with fading momentum, close-confirmed breakout with volume,
wick-only breakout, close-confirmed breakdown, MTF conflict, extended/chase
risk, early positive, mixed evidence, insufficient core evidence, and
stale/partial optional evidence. Separate tests cover all four A2 agreement
relations, confidence degradation, immutable projections, exact citations,
supplied invalidation levels, horizon priority, registry/runtime integration,
and forbidden imports.

The read-only `scripts/inspect_technical_specialist.py` path was attempted for:

- RELIANCE / POSITIONAL / NIFTY / `1d,1h,15m`;
- HDFCBANK / POSITIONAL / BANKNIFTY / `1d,1h,15m`;
- KAYNES / POSITIONAL / NIFTY / `1d,1h,15m`; and
- RELIANCE / DAY / NIFTY / `15m,1h,1d`.

On 2026-09-08 all four correctly stopped at insufficient core evidence. The
existing context diagnostic identified the external cause as Dhan `DH-901`:
the configured client ID or user-generated access token was invalid or expired.
No live technical state or evidence-vs-claim arithmetic was fabricated.
Synthetic arithmetic checks confirmed trend signs, close-versus-wick geometry,
MTF conflict, extension thresholds, and baseline agreement. Repeat the live
checks after refreshing credentials; do not tune policy based on their output.
The same inspection CLI also accepts `--input` for provider-free A2.10 captured
snapshot/run inspection, preserving the capture's assessment and fingerprint.

An existing RELIANCE live capture from 2026-09-07 replayed successfully through
that path. A2 remained `NEUTRAL`, score `24.509451`, class `NO_TRADE`; A3.3
reported `NEGATIVE`, `MODERATE_DOWNTREND`, negative momentum, compression,
no break, aligned-negative MTF, early extension, large downside room, and
`DISAGREES`, with confidence `0.6` and zero model usage. Manual fact checks:

- slope `-0.1015438%`, EMA spread `-0.2354942%`, signed efficiency
  `-0.0665973`, and HH/HL `0.4/0.4` versus LH/LL `0.6/0.6` support the
  moderate downtrend label;
- close breakout and breakdown excursions were both `0.0`, supporting
  `NO_BREAK`;
- compression ratio `0.7757033` is below policy `0.80`;
- MTF negative-return fraction `1.0`, positive fraction `0.0`, and disagreement
  `0.0` support `ALIGNED_NEGATIVE`;
- EMA distance `0.7411761 ATR` supports `EARLY`, while supplied support room
  `2.3634974 ATR` supports `LARGE`; and
- A2 `NEUTRAL` versus technical `NEGATIVE` correctly maps to `DISAGREES`.

## Limitations and A3.4 boundary

A3.3 accepts scalar A2 projections; it does not interpret every currently
available indicator output or relative-strength field, generate probabilistic
forecasts, or enrich narrative with a model. These are honest limitations, not
permission to recalculate or invent facts. No new deferral is introduced.

A3.4 may follow the same immutable fact, cited claim, versioned specialist,
least-privilege registry/runtime, and zero-LLM-capable pattern for fundamentals.
A3.3 adds no fundamental acquisition or company-quality judgment.
