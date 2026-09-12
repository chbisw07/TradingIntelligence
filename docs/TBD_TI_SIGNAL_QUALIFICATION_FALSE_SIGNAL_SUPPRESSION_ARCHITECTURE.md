# TBD — TI Signal Qualification & False-Signal Suppression Architecture

**Status:** Deferred / exploratory architecture note  
**Authority:** Non-authoritative idea cache  
**Purpose:** Preserve the philosophy, probability objectives, architecture ideas, deterministic/ML/higher-intelligence methods and evaluation framework for using TI to suppress false TradingView/strategy signals.  
**Planned revisit:** After Sector Rotation deep work, unless roadmap review promotes it earlier.  
**Implementation status:** Not implemented by this document.

The [TI Pluggability Architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md) uses
`signal.qualify` only as a future conformance thought experiment. This note's
qualification design, thresholds, probability objectives and implementation
remain non-authoritative and unpromoted.

## 1. Executive thesis

Mechanical strategies such as SuperTrend, Momentum, EMA crossovers and breakouts inevitably produce false signals.

Parameter tuning can shift the error but cannot eliminate missing context.

> **Treat strategy signals as candidate events, not final trade decisions.**

TI should qualify candidates through progressively richer intelligence and act only on those that survive the required filters/challenges.

## 2. Target objective

Let:

```text
X = realized false-signal rate for accepted signals
τ = maximum acceptable false-signal rate
```

Desired empirical target:

\[
P(X \ge τ) < 10\%
\]

equivalently:

\[
P(X < τ) > 90\%
\]

This is a target, not a guarantee.

Also evaluate:

- precision;
- coverage/recall;
- expectancy;
- drawdown;
- profit factor;
- costs;
- calibration;
- tail loss.

## 3. Why standalone strategies fail

SuperTrend mainly sees:

```text
price + ATR
```

It does not inherently know:

- market regime;
- higher-timeframe alignment;
- sector leadership;
- relative strength;
- breadth;
- participation;
- extension;
- resistance room;
- event risk;
- IV/derivatives context.

Therefore parameter optimization cannot fully solve missing-context error.

## 4. Candidate-signal philosophy

```text
TradingView strategy
       ↓
CandidateSignal
       ↓
TI qualification
       ↓
ACCEPT / WAIT / REJECT / ABSTAIN
       ↓
only qualified signals proceed
```

Signal sources may include SuperTrend, Momentum, breakout, scanner or external alert systems.

## 5. Precision vs coverage

Higher precision usually means fewer accepted trades.

Example:

```text
100 raw signals
55 good
45 false
```

TI may accept:

```text
40
34 good
6 false
```

Precision improves, coverage falls.

For a user preferring fewer high-quality trades, this may be desirable.

## 6. Do not optimize win rate alone

Conceptual objective:

\[
EU = P(win) × AvgWin - P(loss) × AvgLoss - Costs - RiskPenalty
\]

A 92% win-rate system with rare catastrophic losses can be worse than a lower-win-rate system with strong payoff asymmetry.

## 7. Three-layer suppression architecture

### Layer 1 — deterministic filters

Potential:
- regime;
- trend strength;
- MTF alignment;
- momentum;
- RS;
- sector rotation;
- breadth;
- volume;
- extension;
- room;
- volatility;
- liquidity;
- event risk;
- derivatives context.

### Layer 2 — statistical / ML meta-label

Estimate:

\[
P(success | signal, context)
\]

### Layer 3 — A4 challenge

Ask:

- what could make this fail?
- is evidence stale?
- is sector leadership weakening?
- is event risk missing?
- is the model poorly calibrated in this regime?

## 8. Deterministic qualification example

```text
ST LONG
```

TI checks market regime, stock trend, HTF alignment, momentum, RS, sector tailwind, breadth, volume, room-to-resistance, extension, event risk and derivatives context.

Possible output:

```text
REJECT

sector decelerating
stock > 2.4 ATR extended
resistance only 0.6 ATR above
```

## 9. CandidateSignal contract

Future contract may preserve:

- signal ID;
- strategy ID/version;
- parameters;
- symbol;
- timeframe;
- direction;
- signal time;
- bar identity;
- raw trigger;
- source fingerprint.

Signal is evidence, not authority.

## 10. Meta-labeling

Primary strategy:

```text
SuperTrend → LONG
```

Meta-model:

```text
TAKE / SKIP
```

Features may include ADX, RSI, MACD, ATR%, EMA distance, breakout state, room, volume, RS, sector rotation, regime, breadth, gap, IV, OI, extension, recent return and event context.

## 11. Why meta-labeling is attractive

It asks:

> Given the primary strategy already emitted a signal, should this signal be acted on?

This is narrower than predicting every market bar.

## 12. Strategy-specific vs general model

Possible:
- strategy-specific models;
- general signal-quality model;
- general model + strategy-specific calibration.

TBD.

## 13. Instrument/horizon specificity

Qualification should respect:
- equity;
- futures;
- options;
- intraday;
- positional;
- swing;
- long-term.

Same signal can be good for one horizon and poor for another.

## 14. Sector Rotation integration

Sector Rotation may become a powerful optional contributor.

Example:

```text
ST LONG
sector ACCELERATING
stock sector leader
breadth broadening
```

is different from:

```text
ST LONG
sector LOSING_LEADERSHIP
stock sector laggard
breadth deteriorating
```

Standalone ST treats them equally; TI should not.

## 15. Regime / MTF / extension filters

Potential deterministic suppressors:

- trend vs range regime;
- 5m/15m/1h/daily alignment;
- ATR extension;
- EMA distance;
- breakout age;
- room-to-resistance;
- gap size.

All must remain PIT-safe.

## 16. Breadth and participation

Breakouts supported by broad participation deserve different treatment from isolated movement.

Possible market/sector/constituent breadth and volume-participation inputs.

## 17. Event risk

Signals near earnings, policy events, filings, court/regulatory decisions or macro releases may need rejection, WAIT or higher threshold.

## 18. Derivatives context

For F&O:
- OI;
- basis;
- IV;
- skew;
- liquidity.

Context only; not infallible predictor.

## 19. A4 role

Even after ML ACCEPT, A4 can challenge:

- stale data;
- event risk;
- sector deterioration;
- regime mismatch;
- calibration weakness;
- contradictory evidence.

ML acceptance never forces a trade.

## 20. Abstention

Very high precision requires willingness to say:

```text
WAIT
NO_TRADE
ABSTAIN
```

Forced activity is incompatible with high-selectivity design.

## 21. Confidence-bound gating

Future decision may accept only when a calibrated lower confidence bound exceeds threshold.

Same point estimate with wide uncertainty may still yield WAIT.

Exact method TBD.

## 22. A7 calibration ownership

A7 should own:
- calibration;
- reliability curves;
- Brier score;
- log loss;
- champion/challenger;
- drift.

No "85% success" claim without calibration.

## 23. Sample size / dependence

A 90% observed win rate over 10 trades is weak evidence.

Signals are time-dependent and correlated by symbol/sector/regime.

Any statistical guarantee must account for sample size and dependence.

## 24. Coverage constraint

Avoid trivial solution:

```text
accept zero signals
→ zero false positives
```

Always report:
- accepted count;
- coverage;
- precision;
- expectancy.

## 25. Distribution shift

Monitor:
- calibration drift;
- feature drift;
- regime drift;
- strategy decay.

Historical precision may not persist.

## 26. Walk-forward / PIT validation

Use:
- train past;
- validate future;
- roll forward;
- no random temporal leakage.

Every feature must exist at signal time.

## 27. Label design

Possible:
- target-before-stop;
- horizon return;
- triple-barrier;
- utility label.

Label should match the trading objective.

## 28. MFE / MAE

Track maximum favorable/adverse excursion to distinguish harmless noise from severe false signals and support later stop/target research.

## 29. False-signal categories

Possible:

```text
WHIPSAW
BREAKOUT_FAILURE
REGIME_MISMATCH
SECTOR_MISMATCH
OVEREXTENDED
EVENT_SHOCK
LIQUIDITY_FAILURE
DERIVATIVES_CONFLICT
RANDOM_NOISE
UNKNOWN
```

## 30. Strategy families

Qualification may differ for:
- trend following;
- momentum;
- breakout;
- mean reversion;
- reversal;
- volatility expansion.

## 31. SuperTrend as first research candidate

Compare:

```text
Raw ST
vs ST + deterministic filters
vs ST + Sector Rotation
vs ST + ML meta-label
vs ST + A4 challenge
```

SuperTrend is attractive because its signal is simple and its whipsaw failure mode is familiar.

## 32. Momentum as second candidate

The user's Momentum strategy provides a useful second family to test generalization.

## 33. Multiple indicator agreement

Correlated indicators should not be treated as independent evidence merely because several are bullish.

ST, EMA cross and MACD all derive strongly from price.

No naive vote.

## 34. Signal lifecycle

Possible:

```text
DETECTED
QUALIFYING
ACCEPTED
WAIT
REJECTED
EXPIRED
SUPERSEDED
```

Exact state model TBD.

## 35. Signal expiration / requalification

Accepted signal may become stale before execution.

If evidence changes:

```text
ACCEPTED
→ requalify
→ WAIT / REJECT
```

Capture signal time, receipt time, evidence cutoff, qualification time and intended execution window.

## 36. SignalQualificationResult

Future result may include:

```text
signal_id
strategy
direction
horizon
decision
deterministic_findings
optional_sector_context
optional_ml_probability
calibration_basis
A4_findings
missing_capabilities
invalidation
fingerprint
```

Exact contract TBD.

## 37. Pluggability

Signal Qualification itself should be optional.

Possible:

```text
required:
  raw signal
  deterministic baseline

optional:
  sector.rotation
  derivatives
  forecast
  ML meta-label
  deep research
```

Absence of optional capabilities must be disclosed, not fatal where policy permits.

## 38. Threshold configuration

Possible knobs:
- maximum false-signal target;
- minimum precision;
- minimum expected utility;
- coverage floor;
- probability lower bound;
- regime-specific threshold.

All versioned and empirically justified.

## 39. A6 integration

Qualifier should not choose CE/PE/strike/expiry.

It should output a qualified decision/thesis context.

A6 constructs the trade expression later.

## 40. A5 integration

Once position exists, A5 may consume:
- signal invalidation;
- original qualification context;
- sector tailwind;
- position outcome.

## 41. A9 integration

TV/scanner signals may eventually flow through Signal Qualification before entering expensive TI stages.

Exact ordering needs architecture review.

## 42. Cost funnel

Preferred future pipeline:

```text
raw signals
  ↓
cheap deterministic rejection
  ↓
sector/regime filter
  ↓
deeper specialists
  ↓
ML
  ↓
A4 challenge
```

Only a fraction reaches expensive stages.

## 43. Outcome journal

Track:

- raw signal;
- accepted/rejected;
- features;
- capability composition;
- model/policy versions;
- eventual trade expression;
- outcome;
- MFE/MAE;
- costs.

This becomes the learning corpus.

## 44. Rejected-signal counterfactuals

Track what happened to rejected signals offline.

Otherwise TI cannot measure whether it is rejecting too many good trades.

## 45. Versioning

Capture:
- strategy version;
- parameters;
- timeframe;
- signal schema;
- qualification policy;
- feature version;
- sector capability version;
- ML model/calibration;
- A4 policy;
- expression version.

## 46. Explainability

User should be able to ask:

> Why was this ST LONG rejected?

and see structured reasons, not one opaque score.

## 47. Replay

Future replay should reconstruct:
- raw signal;
- evidence;
- capability composition;
- qualifier;
- policy/model;
- result.

No live fallback.

## 48. Cold-start behavior

Before ML exists:

```text
deterministic qualification only
```

As calibrated models mature, they become optional enrichers.

## 49. Fallback policies

Possible:

```text
STRICT
BASELINE
PARTIAL
```

Behavior when optional qualifier/enricher is unavailable must be explicit/versioned.

## 50. Sector Rotation first

User preference:

> Deep-dive Sector Rotation first, then Signal Qualification.

This is sensible because Sector Rotation becomes an important optional input.

## 51. Research agenda

Future deep research should examine:
- financial meta-labeling;
- triple-barrier labeling;
- selective classification;
- conformal prediction;
- confidence intervals;
- calibration;
- precision-recall optimization;
- class imbalance;
- concept drift;
- cost-sensitive learning;
- regime-conditioned models.

## 52. Selective classification

Signal Qualification is naturally a selective-prediction problem:

```text
predict / act only when evidence is sufficient
otherwise abstain
```

This is central to high accepted-signal precision.

## 53. Experimental ladder

Suggested:

```text
E0 Raw strategy
E1 + deterministic filters
E2 + Sector Rotation
E3 + broader A3 context
E4 + A4 challenge
E5 + ML meta-label
E6 + calibrated uncertainty
E7 + expression-aware expected utility
```

Each stage should prove incremental value.

## 54. Success criteria

Future acceptance should require:
- precision improvement;
- expectancy improvement;
- controlled drawdown;
- adequate coverage;
- walk-forward stability;
- calibration;
- cost inclusion;
- no single-regime dependence.

No arbitrary 90% target if economic utility worsens.

## 55. User objective

The practical preference is:

> fewer, higher-quality trades are preferable to many low-confidence entries.

Therefore a precision-oriented, abstention-capable policy is appropriate.

## 56. Pluggability requirement

Signal Qualification should be:
- structurally pluggable;
- cold-pluggable at minimum;
- availability-aware;
- optional to baseline;
- dependency-explicit;
- failure-isolated;
- composition-recorded.

## 57. Future capability surface

Illustrative only:

```text
signal.qualify
signal.explain
signal.replay
signal.model_status
signal.outcomes
```

## 58. External API vision

Future TradingView/AlgoTest flow:

```text
TradingView alert
    ↓
TI API / signal.qualify
    ↓
qualified result
    ↓
execution system
```

Transport remains later.

## 59. Explicit non-goals now

Do NOT implement now:
- classifier;
- model training;
- sector integration;
- signal API;
- webhook;
- probability model;
- threshold optimization;
- execution;
- Pine changes.

This document is an idea cache.

## 60. Planned revisit

Preferred sequence:

```text
Sector Rotation deep research/architecture
        ↓
Sector Rotation deterministic baseline
        ↓
Signal Qualification deep research
        ↓
Signal Qualification architecture
        ↓
Deterministic qualifier
        ↓
ML meta-label / A7 integration
        ↓
A4 challenge
        ↓
A6 expression-aware decision
```

Exact order subject to roadmap review.

## 61. Promotion criteria

Before this TBD becomes authoritative, settle:
- CandidateSignal contract;
- outcome label;
- deterministic filters;
- sector/regime dependencies;
- ML task;
- calibration;
- uncertainty framework;
- coverage/precision trade-off;
- replay;
- outcome journal;
- drift;
- API;
- pluggability;
- empirical evidence.

## 62. North-star principles

1. Strategy signal is a candidate, not a decision.
2. Precision matters, but economic utility matters more.
3. Abstention is a feature.
4. High success claims require calibration and sample size.
5. No lookahead.
6. Sector/regime context should be optional but powerful.
7. A4 may challenge model acceptance.
8. Model confidence cannot bypass hard risk/authority rules.
9. Baseline must work without ML.
10. Every optional layer must prove incremental value.
11. Rejected signals should be evaluated counterfactually.
12. Prefer fewer high-quality trades over forced activity when policy prioritizes precision.

## 63. Final thesis

> **TI can potentially reduce the false-signal rate of mechanical strategies far beyond what parameter tuning alone can achieve by treating raw signals as candidate events and qualifying them through deterministic context, Sector Rotation, statistical meta-labeling, calibrated uncertainty and A4 challenge/arbitration.**

The desired end state is not "SuperTrend that never loses."

It is:

> **a disciplined selective-decision system that trades only when combined evidence, expected utility and uncertainty justify action, and is comfortable rejecting or abstaining from most raw signals when necessary.**

This remains a non-authoritative `TBD_` idea cache until a future deep research/architecture pass promotes or revises it.
