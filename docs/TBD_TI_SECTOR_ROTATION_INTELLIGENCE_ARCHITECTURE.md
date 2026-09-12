# TBD — TI Sector Rotation Intelligence Architecture

**Status:** Deferred / exploratory design note  
**Authority:** Non-authoritative idea cache  
**Purpose:** Preserve the full Sector Rotation Intelligence concept for later deep architecture, research, implementation and validation.  
**Promotion rule:** Before any part becomes authoritative, it must be revisited against the then-current TI architecture, implementation, data availability, cost constraints, replay/PIT requirements, A5/A6/A7/A9 ownership, and empirical evidence.  
**Implementation status:** Not implemented by this document.

---

# 1. Why this deserves its own workstream

Sector rotation is potentially one of the highest-value intelligence capabilities in TI.

The core investment thesis is:

> **Capital does not move uniformly across the market. Leadership often migrates between sectors, themes and industries. A stock supported by a strengthening sector tailwind may have better opportunity quality than an equally strong stock inside a deteriorating sector.**

The intended user workflow is:

```text
Detect emerging sector tailwind
        ↓
Identify strongest / best-positioned stocks inside that sector
        ↓
Validate stock-specific opportunity through TI
        ↓
Enter while sector rotation remains early/developing
        ↓
Hold while stock thesis + sector tailwind remain healthy
        ↓
Protect / reduce / exit when sector tailwind materially deteriorates
```

This is not a promise of profit.

Sector intelligence should improve contextual selection, timing and position management, while company-specific, market-wide and event risks remain capable of overriding the sector backdrop.

---

# 2. Fundamental distinction: sector strength != sector rotation opportunity

TI must distinguish at least two questions:

## Current strength
> Which sectors are strongest right now?

## Rotation opportunity
> Which sectors are becoming stronger, gaining breadth, accelerating and potentially moving into leadership?

Example:

```text
Sector A:
Current rank            #1
Absolute strength       VERY HIGH
Rotation state          MATURE / DECELERATING

Sector B:
Current rank            #4
Absolute strength       MODERATE
Rotation state          EMERGING / ACCELERATING
```

For a fresh positional investment, Sector B may be more attractive even though Sector A is currently stronger.

Therefore:

> **Absolute sector strength ≠ fresh rotation opportunity.**

---

# 3. Intended sector rotation lifecycle

A future canonical lifecycle may resemble:

```text
EMERGING
    ↓
ACCELERATING
    ↓
LEADING
    ↓
MATURE
    ↓
DECELERATING
    ↓
LOSING_LEADERSHIP
    ↓
LAGGING
```

Alternative states may include:

- RECOVERING
- REVERSING
- RANGE_BOUND
- CONFLICTED
- INSUFFICIENT_EVIDENCE

The exact state machine is TBD.

The architecture should avoid forcing every sector into a bullish/bearish binary classification.

---

# 4. Multi-horizon sector rotation

Rotation must be horizon-specific.

Possible horizons:

- very short term: 1–5 trading days;
- short term: 1–4 weeks;
- positional: 1–3 months;
- medium term: 3–6 months;
- long term: 6–18+ months.

A sector may simultaneously be:

```text
1 week       ACCELERATING
1 month      LEADING
3 months     MATURE
1 year       STRUCTURALLY STRONG
```

No single global sector state should erase horizon differences.

---

# 5. Universe hierarchy

Sector intelligence may operate over several hierarchical levels:

```text
Market
  ↓
Broad sectors
  ↓
Industries / sub-sectors
  ↓
Themes / factor baskets
  ↓
Stocks
```

Examples may include:

- Financials
  - Banks
  - NBFCs
  - Insurance
  - Capital markets

- Industrials
  - Capital goods
  - Defence
  - Railways
  - Power equipment

- Consumer
  - FMCG
  - Consumer discretionary
  - Auto
  - Retail

The exact taxonomy should be configuration-driven and historically versioned.

---

# 6. Sector membership must be point-in-time aware

A stock's sector/index membership may change.

A future implementation must preserve:

- canonical sector identity;
- industry identity;
- effective membership date;
- provider/source;
- historical membership;
- reclassification;
- index methodology where relevant.

Historical backtests must not use today's sector membership for past decision dates.

This requirement is critical for A7 evaluation.

---

# 7. Core evidence families

Sector Rotation Intelligence should combine several evidence families rather than relying on one indicator.

Potential families:

## 7.1 Relative price strength
- sector vs broad market;
- sector vs benchmark;
- sector vs peer sectors;
- stock vs sector;
- sector excess return over 1w / 1m / 3m / 6m;
- rolling relative-strength slope;
- relative-strength acceleration;
- breakout in relative-strength line.

## 7.2 Absolute momentum
- trend;
- moving-average structure;
- momentum;
- rate of change;
- ADX/trend strength;
- breakout state;
- distance from support/resistance;
- extension / overbought state.

## 7.3 Breadth
Potential measures:

- % constituents above EMA20 / EMA50 / EMA200;
- % constituents making 20D / 50D / 52W highs;
- advance/decline;
- median constituent return;
- participation ratio;
- breadth thrust;
- breadth acceleration;
- number of stocks with improving momentum;
- number of stocks outperforming sector benchmark;
- equal-weight vs cap-weight divergence.

A strong sector driven by two mega-cap stocks may be less healthy than broad participation suggests.

## 7.4 Leadership concentration
Measure whether performance is:

- broad;
- moderately concentrated;
- extremely concentrated.

Potential signals:

```text
sector index rising
but
median constituent weak
        ↓
fragile / narrow leadership
```

## 7.5 Volume / participation
- sector volume expansion;
- turnover;
- delivery participation where available;
- constituent volume breadth;
- breakout participation;
- liquidity changes.

## 7.6 Institutional / flow evidence
Potential future evidence:

- FII/DII sector allocation;
- mutual fund sector exposure;
- ETF/fund flows;
- block/bulk activity;
- futures positioning;
- institutional ownership change.

Availability and reliability must be validated before use.

## 7.7 Earnings / fundamental breadth
Possible signals:

- earnings growth breadth;
- revenue growth breadth;
- margin trend;
- earnings surprises;
- estimate upgrades/downgrades;
- order-book trends;
- capex cycle;
- balance-sheet improvement;
- credit conditions.

This should distinguish market-price rotation from fundamental-sector improvement.

## 7.8 Valuation context
Potential metrics:

- sector PE/PB relative to history;
- relative valuation vs market;
- dispersion;
- growth-adjusted valuation;
- valuation percentile.

High momentum + extreme valuation may represent mature/crowded leadership rather than an emerging opportunity.

## 7.9 News / catalyst breadth
Possible sector catalysts:

- government policy;
- regulation;
- taxes/tariffs;
- commodity price shift;
- interest-rate move;
- subsidies;
- PLI schemes;
- defence/railway/capex spending;
- global supply-chain change;
- geopolitical change;
- industry capacity shortage;
- demand-cycle acceleration.

Repeated reports of one catalyst must remain one event root, not multiple independent bullish votes.

## 7.10 Macro sensitivity
Potential context:

- interest rates;
- inflation;
- liquidity;
- currency;
- oil/commodity prices;
- bond yields;
- credit growth;
- government capex;
- fiscal/monetary policy;
- global growth;
- China/US/global sector drivers.

Sector response to macro evidence should remain explicit, not hidden in one score.

## 7.11 Derivatives context
For F&O-heavy sectors:

- futures basis;
- open interest;
- roll behavior;
- option skew;
- implied volatility;
- put/call structure;
- sector/index derivative positioning;
- constituent derivatives breadth.

This is contextual evidence, not direct proof of future direction.

---

# 8. Sector rotation state should be multi-dimensional

Avoid one unexplained scalar score.

A future `SectorRotationIntelligence` result may contain dimensions such as:

```text
Sector                 Capital Goods
Rotation State         ACCELERATING
Relative Strength      STRONG
RS Acceleration        POSITIVE
Breadth                BROAD / IMPROVING
Momentum               STRONG
Participation          SUPPORTIVE
Fundamental Breadth    SUPPORTIVE
Macro Context          SUPPORTIVE
Catalyst Context       POSITIVE
Valuation              ELEVATED
Crowding / Extension   MODERATE
Persistence            DEVELOPING
Risk                    MODERATE
```

A concise score may later exist for ranking, but all major components must remain visible.

---

# 9. Rotation transitions matter more than static rank

TI should detect:

- improving rank;
- declining rank;
- acceleration;
- deceleration;
- leadership persistence;
- regime transition.

Useful questions:

```text
Is the sector strong?
Is it getting stronger?
Is breadth confirming?
Is the move broadening?
Is momentum accelerating?
Is it already mature?
Is leadership beginning to deteriorate?
```

This may be more valuable than today's absolute ranking.

---

# 10. Entry intelligence

For fresh investment selection, desirable states might include:

```text
Sector:
EMERGING / ACCELERATING
        +
Breadth:
IMPROVING
        +
Relative strength:
POSITIVE AND RISING
        +
Stock:
OUTPERFORMING SECTOR
        +
A2/A3/A4:
VALID STOCK-SPECIFIC OPPORTUNITY
```

A stock should not be selected solely because its sector is strong.

Stock-specific filters remain critical:

- company quality;
- technical structure;
- liquidity;
- valuation;
- event risk;
- individual relative strength;
- extension;
- A4 challenge/arbitration.

---

# 11. Stock selection inside leading sectors

The sector engine should later feed a stock-ranking layer.

Possible within-sector ranking dimensions:

- stock vs sector relative strength;
- stock absolute momentum;
- stock breadth contribution;
- earnings/fundamental quality;
- valuation;
- catalysts;
- liquidity;
- technical room;
- extension;
- derivatives support;
- A4 opportunity quality.

Potential flow:

```text
Top sectors
    ↓
Top industries
    ↓
Top stocks within each
    ↓
A2 deterministic filter
    ↓
A3 opportunity intelligence
    ↓
A4 arbitration
```

This connects Sector Rotation with DEF-053 cross-candidate ranking.

---

# 12. Holding-period intelligence

Once a stock is owned, TI should monitor both:

```text
Stock thesis health
        +
Sector tailwind health
```

Possible behavior:

### Strong stock + strong sector
Maintain / allow trend to develop.

### Strong stock + sector decelerating
Protect gains / watch closely.

### Stock weakening + sector strong
Company-specific weakness deserves attention.

### Stock strong + sector losing leadership
Potential late-cycle survivor; tighten monitoring.

### Stock weak + sector losing leadership
Strong candidate for reduction/exit recommendation.

Sector state should not automatically exit an otherwise healthy stock, but materially declining tailwind should affect A5.

---

# 13. Sector-tailwind deterioration model

A future exit/position-management policy should not use one arbitrary rank threshold.

Potential deterioration evidence:

- falling relative-strength slope;
- negative RS acceleration;
- breadth breakdown;
- fewer constituents above key averages;
- narrowing leadership;
- falling participation;
- deterioration in earnings revisions;
- negative macro sensitivity;
- catalyst exhaustion;
- valuation crowding;
- sector becoming underperformer;
- repeated lower highs in relative-strength line.

A future `SectorTailwindHealth` might classify:

- STRONG
- HEALTHY
- WEAKENING
- DETERIORATING
- BROKEN
- UNKNOWN

Exact semantics TBD.

---

# 14. Tailwind persistence

Persistence is crucial.

A one-day surge is not necessarily rotation.

Potential persistence logic:

- consecutive evaluation windows;
- breadth confirmation;
- RS trend durability;
- cross-timeframe alignment;
- event/catalyst duration;
- fundamental support;
- volatility-adjusted persistence.

A sector should not flip state too frequently because of noise.

Hysteresis/state-transition rules may be needed.

---

# 15. Early-warning signals

TI should look for emerging sector leadership before it becomes obvious.

Potential early indicators:

- RS inflection before absolute breakout;
- breadth improves before index breakout;
- bottom-up constituent accumulation;
- increasing number of sector stocks triggering setups;
- earnings-revision breadth improving;
- derivatives positioning improving;
- sector ETF/index volume expansion;
- macro variable turning favorable;
- sector leadership rank rising quickly.

This is potentially one of the highest-value parts of the project.

---

# 16. Crowding / late-stage detection

Strong sectors can become poor fresh entries.

Potential maturity/crowding evidence:

- extreme extension;
- very high breadth already;
- valuation extremes;
- parabolic price action;
- declining breadth despite index highs;
- leadership concentration;
- heavy consensus positioning;
- IV/call skew extremes;
- price momentum deceleration.

Possible states:

- EARLY
- DEVELOPING
- ESTABLISHED
- MATURE
- CROWDED
- EXHAUSTING

Exact model TBD.

---

# 17. Market-regime interaction

Sector behavior depends on broad market regime.

Possible market regimes:

- broad risk-on;
- broad risk-off;
- high-volatility;
- low-volatility;
- rate-sensitive;
- commodity inflation;
- liquidity expansion;
- liquidity contraction;
- recovery;
- recession/stress.

Sector rotation should be conditioned on regime but should not assume a single regime classifier is infallible.

Potential structure:

```text
Market Regime
     ↓
Sector Rotation Context
     ↓
Sector Leadership
```

---

# 18. Relative Rotation Graph / quadrant concepts

A future implementation may evaluate RRG-like concepts:

- leading;
- weakening;
- lagging;
- improving.

However:

- do not copy proprietary definitions blindly;
- exact formulas/licensing must be reviewed;
- TI can implement its own transparent relative-strength / momentum quadrant framework.

This may be useful for visual representation but should not become the entire rotation model.

---

# 19. Sector breadth hierarchy

Breadth may need several layers:

```text
Sector index
    ↓
Large-cap constituents
Mid-cap constituents
Small-cap constituents
Equal-weight basket
    ↓
Sub-industry breadth
```

A cap-weighted sector index may hide broad deterioration.

TI should preserve weighting methodology.

---

# 20. Sector-to-stock causality must remain cautious

Sector strength can help a stock but does not prove the stock will rise.

Potential causal relationships:

- demand expansion;
- policy tailwind;
- cost improvement;
- common macro driver;
- valuation re-rating;
- institutional reallocation.

But stock-specific factors can dominate.

Therefore TI should state:

> sector tailwind = contextual support, not guaranteed causal outcome.

---

# 21. Sector-relative stock classes

Possible future stock classification within a sector:

- LEADER
- EMERGING_LEADER
- PARTICIPANT
- LAGGARD
- COUNTER_SECTOR_OUTPERFORMER
- DETERIORATING
- UNKNOWN

Useful questions:

```text
Is the stock leading the sector?
Is it merely moving because the sector is strong?
Is it lagging despite sector strength?
Is it strong while sector is weak?
```

This distinction may improve stock selection substantially.

---

# 22. Sector-neutral vs sector-aware opportunity intelligence

A future A3/A4 opportunity result might compare:

```text
Stock-only thesis
vs
Sector-aware thesis
```

Example:

```text
Stock technical          SUPPORTIVE
Fundamental              SUPPORTIVE
Sector rotation          DETERIORATING

Final interpretation:
Opportunity still valid,
but lower quality / protect / WAIT for fresh entry.
```

A4 may challenge a stock thesis using sector deterioration evidence.

---

# 23. A5 Position Intelligence integration

Sector intelligence is highly relevant to A5.

A5 may consume:

- current sector state;
- sector tailwind health;
- change since entry;
- sector-relative stock strength;
- rotation deterioration;
- monitoring triggers.

Potential A5 impacts:

```text
Sector tailwind strong
    -> MAINTAIN

Sector weakening
    -> WATCH_CLOSELY / PROTECT

Sector deteriorating materially
    -> REDUCE_RISK

Sector broken + stock thesis weak
    -> EXIT_RECOMMENDED
```

These are conceptual examples only.

A5 remains position intelligence; Sector Rotation remains its own intelligence capability.

---

# 24. A6 Trade Expression integration

Sector intelligence may influence expression choice later.

Examples:

- strong persistent broad tailwind may support directional expression;
- mature/crowded sector may favor capped-risk expression;
- high IV sector conditions may affect option-expression economics.

A6 owns actual expression selection.

Sector Rotation should provide context, not construct trades directly.

---

# 25. A7 predictive sector rotation

A7 should later own calibrated prediction such as:

> Probability sector X outperforms NIFTY over 1 month / 3 months / 6 months.

Potential tasks:

- sector future-return forecast;
- sector excess-return forecast;
- probability of entering leadership;
- probability of maintaining leadership;
- probability of tailwind breakdown;
- expected rotation duration;
- cross-sectional sector ranking.

This requires empirical calibration and PIT historical data.

No such probability should be emitted by the deterministic rotation engine.

---

# 26. Predictive model families

Potential future A7 methods:

- momentum/RS statistical models;
- cross-sectional linear/logistic models;
- tree-based ML;
- gradient boosting;
- rank-learning;
- regime-conditioned models;
- temporal/deep models;
- Bayesian/state-space models;
- ensemble/meta-models.

Models should compete against simple controls.

---

# 27. Forecast evaluation

Potential metrics:

## Ranking
- Spearman rank IC;
- rank IC;
- top-K sector excess return;
- top-K downside;
- leadership hit rate.

## Classification
- Brier score;
- log loss;
- calibration;
- transition-state accuracy.

## Economic usefulness
- sector-tailwind entry effectiveness;
- duration captured;
- drawdown;
- sector-aware stock-selection uplift;
- exit-timing improvement.

No model should be accepted merely because it looks sophisticated.

---

# 28. Point-in-time research requirements

Backtesting rotation is highly vulnerable to leakage.

Need:

- historical sector memberships;
- historical constituent weights;
- point-in-time price/index data;
- PIT financial/estimate data;
- publication/availability timestamps;
- historical macro releases;
- revision-aware data;
- corporate actions.

Today's sector composition must never be applied blindly to the past.

---

# 29. Benchmark controls

Keep simple untouched baselines:

- sector 1m momentum;
- 3m momentum;
- equal-weight breadth;
- market-relative return;
- simple RRG-like quadrant;
- static top-sector ranking;
- random sector ranking.

Advanced methods must prove incremental value over these.

---

# 30. Rotation score vs explainability

A future ranking score may be useful operationally.

However:

> **The score should never replace the component evidence.**

A user should be able to ask:

```text
Why is Capital Goods ranked #1?
Why did Auto fall from #2 to #6?
Why does TI say Banking is improving?
```

TI should expose component changes.

---

# 31. Sector rotation confidence semantics

Do not confuse:

- evidence quality;
- rotation strength;
- persistence;
- predictive probability;
- confidence basis.

A deterministic sector state may be HIGH quality without implying an 80% chance of future outperformance.

Calibrated probability belongs to A7.

---

# 32. Refresh cadence

Potential cadence depends on evidence family:

### Fast
- prices;
- breadth;
- derivatives;
- market regime.

### Daily
- relative strength;
- leadership ranking;
- breadth state;
- participation.

### Event-driven
- policy;
- earnings;
- regulation;
- macro releases;
- major sector news.

### Slow
- valuation;
- fundamentals;
- ownership.

This aligns naturally with the future monitoring architecture.

---

# 33. Monitoring integration

Sector rotation may emit monitoring needs:

- watch sector entering EMERGING;
- alert when ACCELERATING becomes LEADING;
- alert when breadth deterioration crosses threshold;
- alert when held-stock sector enters DECELERATING;
- alert when leadership breaks.

Durable scheduling remains monitoring/A8/A9/A10 territory.

---

# 34. A9 Scanner integration

Sector Rotation can become a powerful upstream scanner:

```text
Market universe
      ↓
Sector Rotation Engine
      ↓
Top emerging / accelerating sectors
      ↓
Best stocks inside each sector
      ↓
A2/A3/A4 opportunity pipeline
      ↓
candidate shortlist
```

This may materially reduce search-space and provider/LLM cost.

---

# 35. Cross-candidate ranking

Sector Rotation and DEF-053 should eventually cooperate.

Possible hierarchy:

```text
Rank sectors
    ↓
Rank stocks within sectors
    ↓
Compare candidates across sectors
```

Avoid one opaque universal score.

Rankings should preserve:

- sector state;
- stock-specific quality;
- maturity;
- downside;
- horizon;
- uncertainty.

---

# 36. Long vs short opportunity

Rotation architecture should support both:

- sectors gaining leadership;
- sectors losing leadership.

Potential short-side intelligence:

```text
sector losing leadership
+ weak breadth
+ stock sector-laggard
+ A4 negative thesis
```

This is useful for:

- short futures;
- PE expressions;
- avoidance;
- hedging.

No execution logic belongs here.

---

# 37. Defensive rotation

Sector rotation is not always risk-on.

Capital may rotate into:

- FMCG;
- Pharma;
- Utilities;
- high-quality financials;
- other defensive groups.

The engine should distinguish:

```text
positive absolute trend
vs
relative defensive leadership during market decline
```

This may change interpretation.

---

# 38. Commodity / rate / currency transmission

Some sectors are driven strongly by macro variables.

Examples:

- metals ↔ commodity prices;
- banks ↔ rates/liquidity/credit;
- IT ↔ USD/global tech spending;
- autos ↔ rates/consumer demand/commodities;
- oil & gas ↔ crude prices/policy;
- cement ↔ energy/infrastructure;
- power ↔ demand/capex/regulation.

A future sector model may define explicit macro sensitivity maps.

These should be versioned and empirically evaluated.

---

# 39. Global sector influences

Indian sectors may respond to global peers.

Potential evidence:

- US semiconductor index;
- global metals;
- global autos;
- crude;
- shipping;
- China demand;
- US rates;
- global technology cycle.

Cross-market evidence should remain source/PIT aware.

---

# 40. Sector event graph

A future evidence graph may connect:

```text
Policy event
   ↓
Sector
   ↓
Sub-industry
   ↓
Companies
```

Examples:

- tariff;
- subsidy;
- defence order budget;
- PLI scheme;
- commodity shock.

This may allow structured propagation of sector catalysts without treating all companies equally.

---

# 41. Theme vs sector

Market themes may cut across sectors.

Examples:

- defence;
- renewables;
- data centers;
- EV;
- railways;
- electronics manufacturing;
- AI infrastructure;
- capex;
- China+1.

Future architecture may need:

```text
Sector
Industry
Theme
Factor
```

as separate taxonomies.

A stock may belong to one sector and several themes.

Do not overload sector classification to represent themes.

---

# 42. Theme rotation extension

A future extension could reuse the same architecture for:

- sector rotation;
- industry rotation;
- theme rotation;
- factor rotation.

This argues for generic cross-sectional group-intelligence contracts rather than hard-coding only NSE sector indices.

But do not over-generalize before the sector use case is proven.

---

# 43. Risk controls

Sector intelligence should surface:

- overextension;
- concentration;
- valuation;
- event dependency;
- volatility;
- liquidity;
- macro sensitivity;
- crowding;
- correlation.

A strongly rotating sector may still be unsuitable for fresh entry.

---

# 44. Portfolio concentration

Later portfolio-aware reasoning may ask:

> Several top opportunities are from one sector. Should TI recommend all of them?

Sector intelligence can reveal hidden concentration.

This belongs to later portfolio/risk architecture, but the sector identities should be preserved now for future use.

---

# 45. Position sizing implications

Sector conviction might later influence risk allocation, but sector rotation should not directly determine quantity.

Sizing remains future risk/expression/TM responsibility.

No sector score -> quantity rule should be hard-coded here.

---

# 46. User-facing outputs

Possible concise output:

```text
Sector: CAPITAL GOODS
State: ACCELERATING
Strength Rank: 2 / 20
Rotation Rank: 1 / 20
Breadth: IMPROVING
RS: STRONG + RISING
Participation: BROAD
Fundamental Context: SUPPORTIVE
Macro Context: SUPPORTIVE
Maturity: DEVELOPING
Risk: MODERATE

Best current stocks:
1. ...
2. ...
3. ...
```

Expanded view:

- why state changed;
- breadth components;
- RS history;
- leaders/laggards;
- catalysts;
- risks;
- evidence provenance;
- transition history.

Exact UI remains future work.

---

# 47. Visualizations

Potential future visuals:

- relative rotation quadrant;
- sector rank heatmap;
- breadth heatmap;
- sector momentum matrix;
- rotation-state timeline;
- sector vs benchmark relative-strength chart;
- sector leaders/laggards;
- stock-within-sector scatter;
- sector lifecycle Sankey/transition map;
- sector-tailwind vs stock-return overlay.

TI_CORE should return structured data; Shell/Web/UI own visualization.

---

# 48. Sector rotation replay

Every rotation decision should be replayable.

Capture:

- universe;
- membership;
- weights;
- evidence cutoff;
- component metrics;
- sector states;
- rankings;
- policy versions;
- source refs;
- fingerprints.

Historical replay must not fetch current sector membership or current data.

---

# 49. Cost discipline

Sector rotation can be expensive if run naively across every stock.

Potential efficiency:

```text
market data first
    ↓
cheap deterministic sector ranking
    ↓
deep evidence only for top/emerging sectors
    ↓
deep stock intelligence only for shortlisted constituents
```

Progressive enrichment should reduce provider and model cost.

---

# 50. Deterministic vs higher-intelligence role

Deterministic engine should own:

- price/RS;
- breadth;
- ranking;
- state transitions;
- persistence;
- mathematical indicators.

Higher intelligence may add:

- policy interpretation;
- cross-sector causal reasoning;
- industry structure;
- supply-chain implications;
- narrative/catalyst synthesis;
- hidden dependencies;
- research gaps.

LLM-originated facts must still pass TI evidence admission.

---

# 51. Bounded open-world sector research

Higher intelligence may say:

> "Capital Goods is accelerating, but current evidence does not explain whether this is driven by government capex, private capex or a narrow electrical-equipment theme."

That can create a governed evidence need.

Research results must be:

- sourced;
- normalized;
- PIT-aware;
- authority checked;
- admitted.

This follows A4 bounded open-world principles.

---

# 52. Sector Rotation Agent architecture

This may eventually be its own multi-stage Agent system.

Possible logical roles:

- Sector State Specialist;
- Breadth Specialist;
- Relative Strength Specialist;
- Fundamental Sector Specialist;
- Macro Sensitivity Specialist;
- Catalyst Specialist;
- Rotation Synthesizer;
- Rotation Challenger.

But do not implement a large multi-Agent system without evidence it adds value.

A deterministic baseline should exist first.

---

# 53. Potential canonical contracts

Future architecture may define:

- `SectorIdentity`
- `SectorMembershipSnapshot`
- `SectorEvidenceSnapshot`
- `SectorStrengthAssessment`
- `SectorBreadthAssessment`
- `SectorRotationState`
- `SectorTailwindHealth`
- `SectorRotationIntelligence`
- `SectorRankingResult`
- `SectorStockRelativeAssessment`
- `SectorMonitoringNeed`

Exact contracts TBD.

---

# 54. Candidate deterministic rotation features

Possible initial v1:

- 5D / 20D / 60D sector return;
- excess return vs NIFTY;
- RS slope;
- RS acceleration;
- % above 20/50/200 DMA;
- median constituent return;
- % constituents outperforming sector;
- new-high participation;
- volume participation;
- equal-weight vs cap-weight divergence;
- sector volatility;
- drawdown;
- extension;
- leadership persistence.

These should be empirically tested before final selection.

---

# 55. Candidate state-machine design

Possible logic:

```text
EMERGING
  RS improving
  breadth improving
  absolute trend not yet fully mature

ACCELERATING
  RS positive + rising
  breadth broadening
  participation increasing

LEADING
  RS strong
  breadth strong
  absolute trend established

MATURE
  strong but acceleration flattening
  extension/crowding rising

DECELERATING
  RS slope weakening
  breadth deterioration
  participation slowing

LOSING_LEADERSHIP
  relative underperformance
  breadth breakdown
  leadership exits

LAGGING
  weak relative and absolute state
```

Exact thresholds must be data-driven/backtested, not chosen cosmetically.

---

# 56. State hysteresis

To reduce noise:

- require minimum persistence;
- different enter/exit thresholds;
- transition confirmation;
- avoid one-day oscillation.

Example:

```text
LEADING -> DECELERATING
may require
RS acceleration negative
AND
breadth deterioration
for N evaluation points
```

Thresholds TBD and must be empirically calibrated.

---

# 57. Sector-tailwind threshold for A5 exit/protection

The user's intended investment style:

```text
enter stock while sector tailwind developing
hold while tailwind healthy
protect / exit after material deterioration
```

A future A5 integration may use a policy like:

```text
Tailwind HEALTHY
    -> no sector-based intervention

Tailwind WEAKENING
    -> WATCH_CLOSELY

Tailwind DETERIORATING
    -> PROTECT / REDUCE_RISK

Tailwind BROKEN
    -> sector evidence supports EXIT_RECOMMENDED
       if stock thesis also weak / no offsetting evidence
```

This must remain evidence-driven and should not force exits based on sector state alone.

---

# 58. Evaluation of stock-selection uplift

One major empirical question:

> Does sector-aware stock selection outperform stock-only selection?

Future A7 experiment:

```text
Control:
A2/A3/A4 stock selection without sector rotation

Candidate:
same system + sector rotation filter/ranking
```

Compare:

- future return;
- drawdown;
- hit rate;
- holding period;
- target-before-stop;
- opportunity ranking;
- turnover;
- cost.

Sector Rotation should justify itself empirically.

---

# 59. Evaluation of exit uplift

Second major experiment:

> Does tailwind-aware exit/protection improve outcomes?

Compare:

```text
Stock-only exit
vs
Stock + sector-tailwind deterioration
```

Metrics:

- retained profit;
- avoided drawdown;
- premature exit frequency;
- re-entry quality;
- turnover/cost;
- MFE captured.

---

# 60. Re-entry logic

If a sector tailwind weakens and later resumes:

- prior stock position may be closed;
- a later fresh setup is a new trade;
- no revenge/recovery semantics.

This matches TI's general trade discipline.

---

# 61. Cross-sector diversification

Sector rankings can support portfolio diversification:

- avoid five positions from one sector;
- choose top stocks from several independent rotations;
- compare sector correlations.

Portfolio optimization is future work, but sector intelligence should preserve the necessary grouping/correlation evidence.

---

# 62. Sector correlation / hidden common factor

Two sectors may actually share one macro driver.

Examples:

- capital goods + power equipment;
- metals + mining;
- banks + NBFC;
- defence + electronics manufacturing.

Future architecture may cluster correlated sectors/factors to avoid false diversification.

---

# 63. Data-source strategy

Possible sources:

- NSE/BSE index/constituent data;
- Dhan/live market data;
- structured MI providers;
- company filings;
- macro/regulator data;
- future licensed PIT datasets;
- global indices/commodities;
- local historical research datasets.

Provider substitution must remain adapter/configuration work.

---

# 64. Missing sector indices

Some industries/themes may not have official indices.

Possible future approaches:

- synthetic equal-weight basket;
- float/cap-weight basket;
- factor-weighted basket;
- curated membership.

Synthetic indices must preserve:

- methodology;
- membership;
- weight;
- rebalance dates;
- PIT identity.

No hidden basket construction.

---

# 65. Corporate actions

Sector constituent price histories need:

- splits;
- bonuses;
- demergers;
- mergers;
- dividends where relevant;
- index rebalances.

Adjustment policy must be consistent with A1/A7 PIT rules.

---

# 66. Survivorship bias

Critical for historical testing.

Historical rotation models must include:

- delisted stocks;
- old index constituents;
- reclassified companies;
- membership changes.

No current-survivor-only backtest.

---

# 67. Look-ahead protection

No use of:

- future index composition;
- revised fundamentals unavailable then;
- later analyst estimates;
- event data published after decision time;
- future sector rankings.

Every feature must have an availability timestamp.

---

# 68. Rotation-policy versioning

Every deterministic state/ranking should preserve:

- feature version;
- state-machine policy;
- thresholds;
- universe;
- membership version;
- benchmark;
- horizon;
- as-of;
- semantic fingerprint.

Policy changes create comparison runs.

---

# 69. Replay / policy comparison

A historical sector decision should be reconstructible offline from captured data.

Policy comparison:

```text
Original policy
vs
new rotation policy
```

creates a new comparison record, not rewritten history.

---

# 70. Failure semantics

Potential failures:

- missing sector membership;
- stale index data;
- incomplete constituent data;
- benchmark unavailable;
- insufficient breadth coverage;
- conflicting taxonomy;
- missing corporate-action adjustment;
- PIT unavailable.

Valid outputs may include:

- INSUFFICIENT_EVIDENCE
- PARTIAL
- ABSTAIN
- UNKNOWN

No fabricated sector state.

---

# 71. Coverage threshold

Breadth metrics are unreliable if constituent coverage is too low.

A future policy must define:

- minimum constituent coverage;
- weight coverage;
- minimum liquidity;
- missing-data treatment.

Coverage must be reported.

---

# 72. Sector taxonomy governance

Need an authoritative, versioned taxonomy.

Potential hierarchy:

```text
market
sector
industry
sub-industry
theme
```

Mappings should be explicit and provider-neutral.

Conflicts should remain visible.

---

# 73. Indian-market specifics

Potential Indian-market considerations:

- NSE sectoral indices;
- BSE sectoral indices;
- F&O eligibility;
- PSU/private-sector distinctions;
- government policy sensitivity;
- commodity/import exposure;
- promoter/government ownership;
- monsoon/rural demand;
- RBI-rate sensitivity;
- capex cycles;
- index rebalances.

These need proper architecture later, not hard-coded assumptions now.

---

# 74. Sector Rotation and F&O

For option/futures candidates:

- sector state may improve directional prior/context;
- F&O liquidity remains stock-specific;
- IV can be elevated in hot sectors;
- expiry must align with expected rotation duration.

A6 owns actual derivative expression.

---

# 75. Sector Rotation and cash stocks

Sector intelligence is especially useful for:

- 2–6 week momentum;
- 1–3 month swing/positional;
- 3–12 month thematic investments.

Cash stocks without derivatives can still use the same sector intelligence.

---

# 76. Sector Rotation and long-term investing

Longer-horizon tailwinds may involve:

- multi-year capex;
- policy;
- demographic change;
- technological adoption;
- supply-chain shifts.

Short-term technical rotation and structural secular tailwind should remain separate dimensions.

---

# 77. Structural vs cyclical tailwind

Potential classification:

- STRUCTURAL
- CYCLICAL
- EVENT_DRIVEN
- POLICY_DRIVEN
- LIQUIDITY_DRIVEN
- DEFENSIVE
- UNKNOWN

A sector can have multiple drivers.

This may help estimate persistence later.

---

# 78. Driver decomposition

Future result may explain:

```text
Rotation driver:
40% conceptual contribution from earnings
30% macro
20% policy/catalyst
10% technical participation
```

But numeric causal attribution should not be invented without a defensible model.

Prefer qualitative driver evidence initially.

---

# 79. Causal reasoning

Higher intelligence may synthesize:

```text
RBI easing
    ↓
credit growth / funding costs
    ↓
bank/NBFC sector
```

or:

```text
government capex
    ↓
capital goods order books
    ↓
industrial suppliers
```

Causal chains should reference evidence and remain hypotheses unless empirically established.

---

# 80. Sector rotation and game-theoretic market behavior

Markets contain strategic behavior.

Possible concepts:

- crowded leadership;
- anticipation of policy;
- pre-positioning;
- sell-the-news;
- rotation from winners into laggards;
- institutional rebalancing;
- benchmark chasing.

LLM reasoning may help form hypotheses, but market-strategy claims require evidence.

---

# 81. Relative strength reference benchmark

Different sectors may be compared against:

- NIFTY 50;
- NIFTY 500;
- broad market;
- equal-weight market;
- relevant parent index;
- global peer.

Benchmark choice affects conclusions and must be explicit/versioned.

---

# 82. Multiple benchmark views

Potential output:

```text
Capital Goods vs NIFTY50       strong
Capital Goods vs NIFTY500      strong
Capital Goods vs Industrials   moderate
```

This can distinguish broad vs local leadership.

---

# 83. Sector-neutral alpha

A strong stock in a weak sector may represent true company-specific alpha.

TI should not automatically reject it.

Potential class:

`COUNTER_SECTOR_OUTPERFORMER`

Such stocks may deserve attention because their strength is idiosyncratic.

---

# 84. Sector-driven beta

Conversely:

```text
stock rising
sector rising strongly
stock underperforming sector
```

may indicate the stock is merely being carried by sector beta.

This can reduce stock-selection quality.

---

# 85. Rotation breadth at stock-selection time

Within top sector, prefer:

- leaders with healthy structure;
- not necessarily highest 5D return;
- avoid most extended names;
- identify laggards with genuine catch-up potential separately.

Do not confuse momentum with chasing.

---

# 86. Catch-up vs leader strategy

Two different opportunity families:

### Leader continuation
Strong stock in strong accelerating sector.

### Catch-up
High-quality laggard beginning to improve while sector remains strong.

These require different policies and should not be mixed in one ranking.

---

# 87. Mean-reversion sector strategy

Future research may examine:

- oversold sector recovery;
- laggard-to-improving rotation.

This is distinct from momentum rotation.

The architecture should permit multiple rotation strategies.

---

# 88. Multi-strategy rotation framework

Potential strategies:

- momentum leadership;
- emerging acceleration;
- recovery;
- defensive rotation;
- macro-driven;
- earnings-driven;
- valuation mean reversion.

One common evidence layer can support multiple policy profiles.

---

# 89. Sector policy profiles

Future configuration may specify:

```text
rotation_policy = emerging_growth
rotation_policy = persistent_leadership
rotation_policy = defensive
rotation_policy = contrarian_recovery
```

These should be explicit/versioned.

No hidden strategy switching.

---

# 90. Agent / deterministic cooperation

Possible future pattern:

```text
Deterministic sector engine
        ↓
Sector Specialist
        ↓
Catalyst/Macro Specialist
        ↓
Rotation Synthesizer
        ↓
A4 Challenger
```

But the deterministic rotation baseline must remain visible.

---

# 91. Sector Rotation capability surface

Possible future curated capabilities:

- `sector.state`
- `sector.rank`
- `sector.rotation`
- `sector.leaders`
- `sector.stock_rank`
- `sector.explain`
- `sector.replay`

These are illustrative only.

They should eventually be available to:

- Shell;
- scripts;
- scanners;
- A5;
- A9;
- future remote API.

---

# 92. TI_SHELL future commands

Potential:

```text
sector rank --horizon 1m
sector show CAPITAL_GOODS
sector explain CAPITAL_GOODS
sector leaders CAPITAL_GOODS
sector rotation --emerging
sector trace CAPITAL_GOODS
```

Do not implement from this TBD.

---

# 93. API / external consumer relevance

Sector Rotation should follow the same capability-first strategy as the rest of TI.

Future programmers should be able to consume typed outputs without importing internal calculators.

Remote HTTP/gRPC remains a transport concern later.

---

# 94. Batch performance

Sector analysis naturally requires batch computation.

Need efficient:

- shared benchmark data;
- shared constituent data;
- vectorized features;
- shared evidence;
- cached deterministic calculations;
- selective enrichment.

Avoid per-stock repeated provider calls.

---

# 95. Incremental update

Future engine should avoid full recomputation when only a subset changed.

Possible:

```text
new market bar
    ↓
update sector price/breadth features
    ↓
re-evaluate affected states
```

Event:

```text
new RBI decision
    ↓
refresh affected sector macro context only
```

This aligns with monitoring/delta architecture.

---

# 96. Data quality / confidence basis

Every sector result should expose:

- constituent coverage;
- stale inputs;
- missing weights;
- membership confidence;
- source quality;
- evidence freshness;
- unsupported dimensions.

A strong score with poor data must remain qualified.

---

# 97. Sector-transition event records

A transition may be an event:

```text
AUTO:
LEADING -> DECELERATING
at T
policy vX
evidence refs [...]
```

This can drive monitoring/A5.

Transition history should be replayable.

---

# 98. Notification / alert use cases

Future alerts:

- sector entered EMERGING;
- sector entered ACCELERATING;
- held-stock sector entered DECELERATING;
- breadth broke;
- stock lost sector leadership;
- sector recovered.

Automation implementation belongs later.

---

# 99. Research notebook / experimentation

Before production implementation, the project should support research experiments:

- compare feature sets;
- test thresholds;
- transition stability;
- horizon performance;
- turnover;
- costs.

Exploratory research must remain separate from production policy.

---

# 100. Champion / challenger rotation policies

Later A7 may maintain:

- production rotation policy;
- challenger policies;
- walk-forward evaluation;
- promotion criteria.

No live tuning without controlled promotion.

---

# 101. Learning from outcomes

Track:

- sector state at entry;
- sector state at exit;
- state transitions during holding;
- stock outcome;
- sector outcome;
- whether sector deterioration preceded stock decline;
- false exit warnings;
- missed emerging rotations.

This creates the empirical basis for improving the system.

---

# 102. User feedback

User may mark:

- sector tailwind analysis useful/not useful;
- missed catalyst;
- exit too early;
- sector signal too slow.

Feedback is useful but should not directly retune production policy without evaluation.

---

# 103. Explainability requirement

User should eventually be able to ask:

> Why did TI say Capital Goods is accelerating?

and receive:

- RS trend;
- breadth;
- participation;
- fundamental context;
- macro/catalyst context;
- risks;
- transition history;
- evidence refs.

No black-box label-only output.

---

# 104. Historical inspection

Future Shell should support:

```text
sector replay CAPITAL_GOODS --as-of <date>
```

if historical evidence is retained.

This is important for debugging and trust.

---

# 105. Rotation-vs-stock attribution

When a stock profits/losses, TI may later decompose:

- market effect;
- sector effect;
- stock-specific effect.

This may help evaluate whether stock selection actually adds value beyond sector beta.

Requires careful statistical design.

---

# 106. Portfolio performance attribution

Later:

```text
Portfolio return
    =
Market
+ Sector allocation
+ Stock selection
+ Timing
+ Expression
```

This is future analytics, but sector identity should be retained now.

---

# 107. Rotation strategy economic objective

Do not maximize raw sector return.

Potential objective:

> maximize risk-adjusted expected economic utility of sector-aware candidate selection and holding decisions.

Include:

- drawdown;
- turnover;
- transaction costs;
- capacity;
- liquidity;
- concentration;
- false transitions.

---

# 108. India-specific sector backtest benchmarks

Possible benchmark universes:

- NSE sector indices;
- broad NSE sectors built from PIT members;
- NIFTY 500 sector groupings;
- F&O-only sector baskets.

Exact universes TBD.

---

# 109. Cash + F&O dual use

Same sector engine should support:

- long-term cash investing;
- positional cash;
- stock options;
- stock futures.

Expression varies later; sector evidence is shared.

---

# 110. Sector Rotation and top-down / bottom-up agreement

Powerful setup:

```text
Top-down:
sector improving

Bottom-up:
increasing count of strong stock setups
```

Agreement may strengthen confidence basis.

Disagreement may be informative:

```text
sector index strong
but
bottom-up stock breadth weak
```

possibly narrow/crowded leadership.

---

# 111. Cross-sectional anomaly research

Potential future features:

- momentum;
- quality;
- low-vol;
- value;
- earnings revisions;
- size.

Sector effects may interact with factor regimes.

This may eventually extend toward factor rotation.

---

# 112. Sector-tailwind half-life

A future empirical metric:

> How long does a detected tailwind usually persist for this sector/state/horizon?

This can support holding-horizon intelligence.

A7 owns calibrated prediction.

---

# 113. Transition hazard

Future predictive question:

> Probability sector exits LEADING in next N days/weeks.

Useful for A5 protection.

Again A7.

---

# 114. False-break rotation control

Need to detect temporary sector spikes caused by:

- one stock;
- one event;
- expiry;
- low liquidity;
- rebalancing.

Breadth/persistence/participation can help.

---

# 115. Structural break detection

Long-term sector relationships may change.

Examples:

- policy regime shift;
- technological disruption;
- index methodology change;
- new industry composition.

Policies/models should detect when old calibration is no longer reliable.

---

# 116. Source provenance

Every non-price material claim should trace to evidence/source refs.

Sector rotation must use the accepted Source Authority / Provenance / Contradiction architecture.

No separate provenance system.

---

# 117. Conflicting sector evidence

Example:

```text
Price/RS          strong
Breadth           weakening
Earnings          improving
Macro             adverse
```

Output should be:

- CONFLICTED / qualified;
- not forced into one bullish score.

A4 may later arbitrate.

---

# 118. Sector-level A4 challenge

A future A4 sector challenge may ask:

- Is leadership broad or narrow?
- Is the move already priced?
- Is sector strength just one mega-cap?
- Is macro tailwind durable?
- Are earnings revisions confirming?
- Is the catalyst already mature?
- Is there counter-evidence from global peers?

This can improve rotation quality.

---

# 119. Sector-specific policies

Different sectors may require different metrics.

Banks:
- credit growth;
- NIM;
- asset quality;
- liquidity/rates.

Metals:
- commodity prices;
- China/global demand;
- capacity.

IT:
- USD;
- global tech spending;
- deal pipeline.

Therefore common framework + sector-specific feature policies may be needed.

Avoid forcing identical fundamentals across sectors.

---

# 120. Sector data normalization

Provider labels/taxonomies may disagree.

TI should preserve:

- provider-native sector;
- canonical sector mapping;
- mapping quality;
- effective period.

Ambiguous classification remains explicit.

---

# 121. Sector Rotation major roadmap placement

Provisional recommendation for future review:

```text
A5
Position Intelligence
    ↓
A6
Trade Expression
    ↓
A7.0
Sector Rotation Foundation / cross-sectional infrastructure
    ↓
A7.x
Predictive sector rotation + ranking/evaluation
    ↓
A9
Scanner/universe integration
```

Alternative placement may be warranted after A5/A6 review.

Do not treat this sequence as authoritative yet.

---

# 122. Possible dedicated major workstream

Given its breadth, Sector Rotation may deserve its own dedicated milestone/workstream rather than being hidden inside A7.

Future consolidation should consider whether to introduce an explicit major milestone such as:

```text
SR1 — Deterministic Sector Rotation
SR2 — Sector-to-Stock Ranking
SR3 — Predictive Rotation
SR4 — Monitoring / Scanner Integration
```

or map them into A7/A9.

The numbering decision is intentionally deferred.

---

# 123. Research-before-architecture requirement

Before promotion, perform a deep study of:

- academic sector rotation literature;
- industry practices;
- relative-strength frameworks;
- breadth methods;
- RRG-like techniques;
- institutional flows;
- factor/sector interaction;
- Indian market data availability;
- empirical evidence.

Do not finalize architecture from intuition alone.

---

# 124. Candidate research questions

1. Does sector momentum persist in India?
2. Which horizon is most useful?
3. Does breadth lead sector index returns?
4. Does RS acceleration outperform simple RS?
5. Can emerging sectors be detected before breakouts?
6. How long do sector tailwinds persist?
7. Does sector-aware stock selection improve A2/A3/A4 outcomes?
8. Does tailwind deterioration improve exits?
9. Which macro variables add real predictive value?
10. Is sector ranking stable enough for production?
11. How much turnover/cost does rotation cause?
12. Do F&O sectors behave differently?
13. How much sector alpha is actually factor beta?
14. Does equal-weight breadth outperform cap-weight breadth as an early signal?
15. Does valuation improve timing or mostly reduce late entries?

---

# 125. Acceptance philosophy

Future deterministic Sector Rotation should not be accepted merely because examples look good.

Acceptance should require:

- no lookahead;
- PIT membership;
- stable contracts;
- replay;
- simple benchmark comparison;
- cross-period tests;
- regime tests;
- cost sensitivity;
- transparent states;
- user-level scenarios;
- full regression.

Predictive versions additionally require:
- walk-forward evaluation;
- calibration;
- champion/challenger;
- out-of-sample evidence.

---

# 126. Example end-state user workflow

```text
TI> sector rotation --horizon 1m

1. CAPITAL_GOODS     ACCELERATING
2. POWER             EMERGING
3. AUTO              LEADING
4. PHARMA            IMPROVING
...

TI> sector leaders CAPITAL_GOODS

1. STOCK_A
2. STOCK_B
3. STOCK_C

TI> opportunity STOCK_A
TI> a4 evaluate
...
```

After entry:

```text
TI> position assess
Sector tailwind: HEALTHY
Position: MAINTAIN
```

Later:

```text
Sector tailwind:
HEALTHY -> WEAKENING -> DETERIORATING

A5:
PROTECT / REDUCE_RISK
```

This is illustrative only.

---

# 127. Explicit non-goals now

Do NOT implement now:

- sector engine;
- state thresholds;
- sector scores;
- RRG;
- scanner;
- alerts;
- sector APIs;
- ML models;
- forecast probabilities;
- synthetic sector baskets;
- A5 sector exit rules;
- Web/Shell commands;
- remote API;
- monitoring daemon.

This document is an idea cache.

---

# 128. Planned revisit

Revisit after the current A5 work reaches its natural checkpoint and before/within the future cross-sectional/forecasting/scanner milestones.

At revisit:

1. deep research;
2. data-availability study;
3. architecture pass;
4. deterministic baseline implementation;
5. empirical acceptance;
6. predictive extension;
7. A5 integration;
8. A9 scanner integration.

Exact order remains TBD.

---

# 129. Promotion criteria

Before becoming authoritative, the design should settle:

- canonical taxonomy;
- PIT membership;
- deterministic features;
- state machine;
- persistence/hysteresis;
- ranking;
- breadth;
- maturity/crowding;
- macro/fundamental/catalyst integration;
- A4 challenge;
- A5 consumption;
- A7 prediction;
- A9 scanning;
- replay;
- monitoring;
- APIs;
- cost;
- empirical evidence.

---

# 130. Final thesis

> **Sector Rotation Intelligence should become a first-class TI capability that identifies where market leadership is emerging, measures the health and persistence of sector tailwinds, ranks stocks inside those tailwinds, and supplies sector-aware evidence to opportunity selection and position management.**

Its strongest potential economic use is not simply finding today's strongest sector.

It is:

> **entering high-quality stocks while sector tailwinds are emerging or accelerating, holding while those tailwinds remain healthy, and protecting/reducing/exiting when the tailwind materially deteriorates — while preserving stock-specific intelligence, uncertainty, provenance and disciplined risk control.**

This idea is important enough to merit a dedicated future project/workstream.

Until a full architecture/research pass promotes it, this document remains a non-authoritative `TBD_` idea cache.
