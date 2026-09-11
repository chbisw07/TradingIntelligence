# TBD - TI Forecasting / Ensemble / Calibration / Learning Architecture

**Consolidation disposition: REVISE_AND_KEEP_TBD (2026-09-11).**
The [transition plan](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md) retains A7
as the evaluation/forecast overlay after deterministic A6 candidates; its
admitted forecasts later enable enhanced A6 comparison. Architecture entry needs
PIT/outcome data rights, deterministic controls, target/horizon/calibration and
promotion/rollback criteria. Cross-candidate ranking belongs in evaluated A7
scope. Ensemble hierarchy, model selection and learning algorithms below remain
hypotheses, not mandatory complexity or implemented accuracy. Model prior
knowledge is not empirical forecast evidence.
The [A4 closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) confirms that A4
freezes without calibrated forecasting or a model Challenger. This note remains
an A7 input after deterministic A6 and does not block Shell or A5.

> **Status:** TBD / temporary exploratory design note  
> **Authority:** This document is **not yet part of the accepted TI architecture**. It captures an agreed design direction for later formal review.  
> **Promotion rule:** Before becoming authoritative, this note must be revisited at the relevant milestone, reconciled with the then-current repository architecture, tested against implementation realities, and either promoted, revised, split, or rejected.  
> **Repository placement:** Intended for `docs/` with the `TBD_` prefix so it is immediately recognizable as non-final.

---

## 1. Purpose

Capture the agreed future design direction for first-class forecasting in TradingIntelligence (TI).

Forecasting should eventually support questions such as:

- What is the likely price/return distribution of a stock by a target date?
- What is `P(return >= X)` over a requested horizon?
- Which stocks have the strongest probability of meeting a target return?
- Which candidates rank highest on risk-adjusted expected opportunity?
- For F&O, what is the probability of target-before-expiry / target-before-stop?
- What are expected MFE/MAE, time-to-target, realized-volatility, or other requested attributes?

The forecasting system must be judged against realized market outcomes.

---

## 2. Core Design Principle

> **TI should support multiple pluggable forecasting methods and ensembles. No model earns trust because it is mathematically sophisticated; it earns trust only through stable out-of-sample performance against reality.**

A simpler model that predicts actual outcomes better should outrank a more complex model.

Forecasting is therefore not one algorithm. It is a configurable forecasting laboratory plus a controlled production ensemble.

---

## 3. Separate Forecasting Concepts

Do not overload the word "forecast".

At minimum distinguish:

1. **Forecast Task** — what is being predicted.
2. **Forecast Method** — one concrete model family/implementation.
3. **Forecast Regime Model** — market-state detector/conditioner.
4. **Forecast Ensemble** — combination of methods.
5. **Forecast Meta-Ensemble** — combination of lower-level ensembles.
6. **Forecast Calibration** — whether predicted probabilities/distributions match observed frequencies.
7. **Forecast Scorecard** — empirical quality record.
8. **Forecast Policy** — which methods/ensembles are enabled for which task/horizon/instrument.
9. **Forecast Result** — structured output returned to TI consumers.
10. **Outcome Record** — what actually happened later.

These should eventually become typed domain concepts, not arbitrary metadata.

---

## 4. Configuration-Driven Method Registry

Forecasting methods should be registered/configured, not hard-coded.

A future UI may render enabled methods as checkboxes, but the TI core should consume configuration such as:

```yaml
forecasting:
  methods:
    arimax:
      enabled: true
    kalman:
      enabled: true
    garch:
      enabled: true
    hmm:
      enabled: true
    lightgbm:
      enabled: true
    xgboost:
      enabled: true
    catboost:
      enabled: true
    lstm:
      enabled: false
    transformer:
      enabled: false

  ensembles:
    statistical:
      enabled: true
    tabular_ml:
      enabled: true
    regime:
      enabled: true
    deep_temporal:
      enabled: false
    meta:
      enabled: true
```

The UI checkbox is presentation only. The domain uses semantic method/ensemble IDs.

---

## 5. Potential Model Families

Candidate methods may include:

- naive/random-walk controls
- historical mean/momentum baselines
- linear/logistic/regularized regression
- ARIMA/ARIMAX
- exponential/state-space/Kalman models
- GARCH-family volatility models
- HMM / Markov-switching regime models
- Random Forest
- XGBoost / LightGBM / CatBoost
- quantile regression
- survival/hazard models
- Bayesian models
- LSTM/GRU
- TCN
- N-BEATS/N-HiTS-style models
- TFT/Transformer-style models
- cross-sectional ranking models

No method is assumed to be superior before empirical validation.

---

## 6. Forecast Task Taxonomy

Avoid a generic:

```text
predict(symbol)
```

Use explicit forecast tasks.

### Equity examples

- `DIRECTION_PROBABILITY`
- `RETURN_DISTRIBUTION`
- `PRICE_DISTRIBUTION`
- `RETURN_THRESHOLD_PROBABILITY`
- `DRAWDOWN_PROBABILITY`
- `VOLATILITY_FORECAST`
- `TARGET_EVENT_PROBABILITY`
- `CROSS_SECTIONAL_RANK`

### Futures/F&O examples

- `TARGET_BEFORE_EXPIRY`
- `TARGET_BEFORE_STOP`
- `MFE_FORECAST`
- `MAE_FORECAST`
- `TIME_TO_TARGET`
- `REALIZED_VOLATILITY_FORECAST`
- `IV_FORECAST` where justified
- `UNDERLYING_PATH_EVENT_PROBABILITY`

Different tasks may use different model families.

---

## 7. Horizon Semantics

Support both:

```text
duration = 6 months
```

and:

```text
target_date = 2027-03-31
```

For derivatives, expiry may be a natural forecast horizon.

Internally normalize horizon semantics into a canonical form.

Do not silently reinterpret a user-specified target date as a generic duration.

---

## 8. Requested Attributes

A ForecastRequest should explicitly state what outputs are needed.

Examples:

```text
price_distribution
return_distribution
P(return >= 25%)
P(return >= 50%)
P(return >= 100%)
```

or:

```text
P(target before expiry)
P(target before stop)
expected MFE
expected MAE
time_to_target_distribution
```

Do not compute every possible attribute for every request.

---

## 9. Single-Symbol and Batch Forecasting

The same architecture should support:

- one stock
- a user-selected group
- NIFTY 500
- up to ~1000 equities
- ~200 F&O underlyings

Batch forecasting should naturally support ranking.

Shared feature/evidence preparation should be reused across batch requests.

---

## 10. Hierarchical / Funnel Ensemble

Support multi-stage ensemble structures.

Example:

```text
m1 ─┐
m2 ─┼─> Statistical Ensemble M1
m3 ─┘

m4 ─┐
m5 ─┼─> Tabular ML Ensemble M2
m6 ─┘

m7 ─┐
m8 ─┼─> Deep Temporal Ensemble M3
m9 ─┘

M1 ─┐
M2 ─┼─> Meta Ensemble
M3 ─┘
```

This is preferable to one flat model pool when different method families solve different aspects of the problem.

---

## 11. Regime-Conditioned Forecasting

A regime model should generally be treated as context/gating evidence rather than automatically as the final price predictor.

Potential regimes:

- bull trend
- bear trend
- sideways
- low volatility
- high volatility
- stress
- recovery

A future mixture-of-experts design may use regime state to select/weight model families.

---

## 12. Cross-Sectional Ranking Is a Distinct Problem

For questions such as:

> "Give me the top 10 stocks for the next 6 months"

cross-sectional ranking may be more important than independent per-stock point prediction.

Potential training shape:

```text
stock × historical decision date
        ↓
technical + fundamental + valuation + sector + event + regime features
        ↓
future 1m / 3m / 6m / 12m outcome
        ↓
rank today's universe
```

A stock may have a high expected return but poor reliability/downside; ranking should consider risk-adjusted opportunity, not raw expected return alone.

---

## 13. Reality-Based Scorecards

Model ranking should be context-aware.

A future scorecard key may resemble:

```text
Model × ForecastTask × Horizon × InstrumentType × Sector/Regime
```

Potential metrics:

### Continuous forecasts

- MAE
- RMSE
- Median Absolute Error
- directional accuracy

### Ranking

- rank IC
- Spearman IC
- top-K realized return
- top-K downside
- future-winner hit rate

### Probability forecasts

- Brier score
- log loss
- calibration error
- reliability curves

### Distribution forecasts

- pinball loss
- CRPS
- interval coverage
- interval width vs coverage

### Economic usefulness

- target-hit accuracy
- target-before-stop accuracy
- MFE/MAE quality
- drawdown prediction
- risk-adjusted realized result
- opportunity-ranking quality

No single universal score should dominate every task.

---

## 14. Benchmarks / Controls

Maintain simple untouched controls such as:

- random walk
- historical mean
- simple momentum
- market/sector return
- A2 deterministic ranking

These are essential to answer:

> Is the forecasting machinery actually adding value?

---

## 15. Model Weighting

Weights should eventually reflect empirical evidence such as:

- long-term out-of-sample performance
- recent performance
- calibration
- horizon
- market regime
- sector/instrument type
- sample size
- stability

Safeguards should prevent overreacting to tiny samples.

Potential techniques:

- shrinkage toward equal weights
- minimum sample requirements
- exponentially weighted performance
- Bayesian model averaging
- stability penalties
- champion/challenger promotion

---

## 16. Forecast Output Should Be Distributional

Prefer structured probability/distribution output over false precision.

Illustrative result:

```text
reference_price
forecast_horizon
forecast_date
expected_return
median_price
q10/q25/q50/q75/q90
P(return >= 25%)
P(return >= 50%)
P(drawdown <= -20%)
model/ensemble identity
calibration status
valid_until
```

An LLM must never invent calibrated probability values.

---

## 17. Calibration Is Separate From Confidence

Do not confuse:

- model self-confidence
- evidence quality
- ensemble agreement
- empirically calibrated probability

Only the last can support statements such as:

```text
P(return >= 50%) = 0.63
```

Calibration must be measured against realized frequencies.

---

## 18. Point-in-Time Data Discipline

Forecasting must use only evidence available at forecast time.

Critical safeguards:

- point-in-time fundamentals
- point-in-time universe membership
- no future filings
- no revised future corporate values
- no future news
- no lookahead through survivorship
- no post-event labels leaking into features

This requirement is stronger than model sophistication.

---

## 19. Validation Discipline

Require future support for:

- walk-forward validation
- time-series cross-validation
- purging/embargo where relevant
- untouched out-of-sample periods
- regime testing
- champion/challenger comparison
- rollback

A backtest that leaks future information is invalid regardless of headline accuracy.

---

## 20. Feedback / Learning Loop

```text
evidence at T
    ↓
forecast
    ↓
immutable forecast record
    ↓
future market outcome
    ↓
evaluation
    ↓
scorecards/calibration
    ↓
candidate model improvement
    ↓
out-of-sample validation
    ↓
controlled promotion
```

The system learns from realized outcomes, not from previous TI output treated as ground truth.

---

## 21. Champion / Challenger and Promotion

Production models should eventually follow controlled promotion.

Possible states:

```text
CANDIDATE
CHALLENGER
CHAMPION
RETIRED
```

Promotion requires empirical superiority and minimum evidence.

Rollback must remain possible.

These should be semantic model-lifecycle states, not UI labels.

---

## 22. Retraining Is Not Automatic Trust

A model may retrain automatically later, but retraining does not imply production promotion.

Separate:

```text
retrain
evaluate
approve/promote
deploy
```

This prevents self-reinforcing degradation.

---

## 23. RL Boundary

Reinforcement learning should not be the first forecasting engine.

It may later be investigated for sequential decisions such as:

- hold
- reduce
- add
- protect
- exit
- re-enter

Even there, overfitting and simulation mismatch require strict controls.

---

## 24. Forecasting Is Headless

TI owns structured objects such as:

- `ForecastRequest`
- `ForecastResult`
- `HistoricalForecastRecord`
- `OutcomeRecord`
- `ModelScorecard`

External applications own:

- actual-vs-predicted plots
- forecast cones
- calibration charts
- model comparison dashboards
- visualization

TI should not grow charting complexity merely because visual consumers exist.

---

## 25. Cost / Performance Principles

1. Do not run every model for every request.
2. Use task/horizon/instrument policies to select model families.
3. Reuse prepared features/evidence.
4. Batch where appropriate.
5. Prefer cheaper models when performance is equivalent.
6. Escalate to expensive models only when justified.
7. Track model compute/cost as part of evaluation.
8. Do not reward complexity for its own sake.

---

## 26. Likely Roadmap Placement

Current agreed direction:

- A3 defines/consumes forecast evidence but does not fabricate it.
- A7 is expected to become the formal **Evaluation, Forecasting and Learning** milestone.
- Exact A7 decomposition remains TBD.

---

## 27. Open Questions

- final ForecastRequest/Result contracts
- model registry interface
- model-family plugin contract
- exact scorecard aggregation
- meta-ensemble algorithm
- regime-gating design
- forecast store
- dataset construction pipeline
- training infrastructure
- retraining cadence
- promotion thresholds
- sample-size requirements
- calibration monitoring
- historical point-in-time data availability
- compute/storage strategy
- model lifecycle governance

---

## 28. Working Design Principle

> **Forecasting in TI should be multi-model, pluggable, configuration-driven, task-specific, horizon-aware, regime-aware, empirically scored against realized outcomes, and calibrated. Hierarchical ensembles are preferred where useful. Complexity earns no privilege. TI returns structured forecast data; external applications visualize it.**
