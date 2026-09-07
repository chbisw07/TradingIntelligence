# TIAF A2 Deterministic Foundation Baseline

## 1. Purpose and status

TIAF_A2 establishes the transparent non-AI market-intelligence benchmark that
future Agents must be measured against rather than replace. A2 converts
provider-neutral factual context into deterministic features, indicators,
relative and multi-timeframe evidence, explainable market-state assessments,
stable candidate rankings, and replayable evaluation records.

**Status: COMPLETE / LIVE VALIDATED.** A2.1 through A2.10 are accepted. The
final accepted sub-milestone tag is `tiaf-a2.10` at commit
`3d878f583d93f6708ce23ea19a6f2feae57c3cd2`. This closure prepares, but does
not create, the separate major baseline tag `tiaf-a2-baseline`.

Package version `0.1.0`, contract schema version `1.0`, and A2.9 policy version
`1.0` are separate identities.

## 2. Architectural purpose and path

The complete deterministic path is:

```text
provider / resolver / process-local runtime
                    |
                    v
            immutable AnalysisContext
                    |
          +---------+---------+
          |                   |
          v                   v
 deterministic FeatureEngine  IndicatorEngine
          |                   |
          +---------+---------+
                    |
          explicit benchmark + ordered MTF evidence
                    |
                    v
          deterministic BaselineEngine
                    |
                    v
        frozen snapshot / run / ranking records
                    |
                    v
          provider-free replay / evaluation
```

Responsibilities remain deliberately separated:

- providers and the resolver acquire and normalize facts; they do not analyze
  or recommend;
- `AnalysisContextBuilder` coordinates factual requirements and preserves
  missing, partial, deferred, quality, freshness, and provenance states;
- feature and indicator engines consume contexts and never fetch;
- relative and MTF engines consume explicit contexts/bundles and never invent
  benchmark identity or resample bars;
- `BaselineEngine` consumes immutable evidence and a versioned policy; it has
  no provider, broker, Agent, strategy, or wall-clock dependency;
- evaluation consumes frozen evidence; replay never fetches, and later outcome
  facts cannot mutate or enter the original decision.

No layering violation was found at closure. The `agents`, `planner`,
`arbitration`, `workflows`, `memory`, `service`, and `observability` packages
remain reserved namespaces only.

## 3. Accepted A2 milestones

| Milestone | Accepted deterministic capability | Tag |
|---|---|---|
| A2.1 | Provider-neutral feature contracts, registry, engine, status/quality/provenance, and initial factual features | `tiaf-a2.1` |
| A2.2 | Price, return, range, Wilder ATR, realized volatility, rolling extrema, drawdown/run-up, and move/ATR | `tiaf-a2.2` |
| A2.3 | Moving averages, slopes, fit, efficiency, persistence, adjacent structure, rolling position, and ATR extension | `tiaf-a2.3` |
| A2.4 | Extensible indicator framework plus SuperTrend, RSI, MACD, ADX/DI, Bollinger, and Donchian | `tiaf-a2.4` |
| A2.5 | Completed-history volume, relative volume, dispersion, slope, runs, participation, and alignment | `tiaf-a2.5` |
| A2.6 | Fixed prior support/resistance, distance/excursion, range geometry, compression, and expansion | `tiaf-a2.6` |
| A2.7 | Single-expiry option-chain geometry, premium, IV, Greeks, OI, volume, concentration, and spread facts | `tiaf-a2.7` |
| A2.8 | Explicit-benchmark relative strength and ordered independently acquired multi-timeframe evidence | `tiaf-a2.8` |
| A2.9 | Versioned DAY/POSITIONAL market-state, opportunity, maturity/room, candidate class, and stable ranking benchmark | `tiaf-a2.9` |
| A2.10 | Content-addressed evidence capture, exact offline replay, policy comparison, outcomes, ranking metrics, and regression corpus | `tiaf-a2.10` |

The milestone-specific technical notes remain authoritative for exact formulas,
warm-up windows, parameters, and live observations.

## 4. Accepted public contracts

The A2 baseline accepts the public A1 `AnalysisContext` and normalized market
models without changing their provider-neutral meaning. Its principal public
contracts are:

- features: `FeatureDefinition`, `FeatureRequest`, `FeatureResult`,
  `FeatureBundle`, `FeatureCalculator`, `FeatureRegistry`,
  `RelativeStrengthContext`, `BenchmarkReference`, `TimeframeFeatureContext`,
  and `MultiTimeframeContext`;
- indicators: `IndicatorDefinition`, `IndicatorRequest`, `IndicatorResult`,
  `IndicatorBundle`, `IndicatorCalculator`, and `IndicatorRegistry`;
- baseline: `DeterministicBaselineRequest`, `BaselinePolicy`,
  `EvidenceRule`, `EvidenceContribution`, `ScoreComponent`,
  `MarketStateAssessment`, `OpportunityAssessment`, `OpportunityRanking`, and
  `OpportunityRankingItem`;
- evaluation: `EvidenceSnapshot`, `BaselineRunRecord`, `ReplayRequest`,
  `ReplayResult`, `BaselineComparison`, `OutcomePath`, `BaselineOutcome`,
  `RankingEvaluation`, `RegressionReport`, and `ReplayCorpusStore`.

Models are frozen. Finalized semantic collections are tuples while JSON emits
ordinary arrays. Metadata dictionaries remain intentionally extensible under
the accepted A0 shallow-immutability boundary.

## 5. Deterministic evidence inventory

The built-in feature foundation covers current/previous price facts, exact
fixed-window returns, OHLC range and candle structure, ATR/ATR%, realized
volatility, extrema, drawdown/run-up, moving averages, trend slopes and fit,
directional efficiency, close and high/low transition structure, volume and
participation, fixed-prior support/resistance and breakout geometry,
compression/expansion, and one-expiry option-chain structure.

The first-class indicator registry contains versioned SuperTrend, Wilder RSI,
MACD, Wilder ADX/+DI/-DI, population Bollinger Bands, and Donchian Channel.
The engine is indicator-agnostic and extensible; additional formulas require
named semantics and fixtures rather than changes to the engine abstraction.

A2.8 adds six exact-alignment relative measurements against a caller-supplied
MARKET, SECTOR, PEER, or CUSTOM benchmark and ten ordered MTF factual
measurements. Each timeframe is acquired independently through A1; A2 neither
resamples nor fabricates bars. Benchmark provenance is explicit and no mapping
is inferred.

A2.7 consumes exactly one explicit option-chain expiry. It retains listed
strike identity, chain spot, provider IV/Greeks, and exact ATM-centered window
provenance. It does not mix expiries or infer dealer positioning, probability,
expected move, strategy, or contract choice.

## 6. Baseline policy and `NO_TRADE`

A2.9 policy 1.0 is a generic engineering benchmark, not a fitted prediction
model. DAY and POSITIONAL policies expose every evidence selector, transform,
scale/cap, component weight, direction margin, quality gate, penalty, and class
threshold.

Component-level evidence, directional disagreement, missingness, quality, and
freshness remain visible. `NO_TRADE` is a first-class valid result when evidence
is unavailable, conflicted, neutral, below threshold, or too mature. Ranking
retains all assessments for audit but returns only eligible candidates; it does
not fill a requested top-N with `NO_TRADE` rows. Closure did not tune any
weight or threshold against live examples.

## 7. Quality, freshness, provenance, and time

All contract datetimes are aware and normalize to canonical
`Asia/Kolkata`; JSON timestamps carry `+05:30`. Acquisition time, source market
observation, decision time, replay time, and later outcome time remain distinct.

Quality has the shared ordered vocabulary `GOOD`, `PARTIAL`, `DEGRADED`, and
`UNAVAILABLE`. Freshness has `FRESH`, `AGING`, `STALE`, and `UNKNOWN`.
Calculators do not upgrade source quality or substitute retrieval time for
market observation. Missing optional evidence stays visible; missing required
evidence gates the baseline rather than receiving a hidden favorable default.

Canonical symbols, provider instrument IDs, context IDs, bundle/result IDs,
assessment/ranking/run IDs, snapshot IDs, and SHA-256 fingerprints retain their
separate identity roles. Semantically unordered metadata and freshness maps are
canonicalized where they participate in deterministic identity.

## 8. Anti-lookahead and determinism guarantees

- indicators and completed-history features never append a live quote as a
  synthetic current bar;
- A2.6 prior boundaries use exactly N bars before the latest completed bar, so
  N+1 observations are required and the measured bar cannot move its boundary;
- N-bar measurements and N-transition measurements enforce their documented
  minimums without silent shortening;
- relative histories use an exact latest common `(start_at, end_at)` suffix;
- MTF contexts preserve requested order and per-timeframe identities;
- option features never substitute or mix expiries;
- future pivot/event semantics remain deferred rather than using hindsight;
- `OutcomePath` begins after the frozen decision and is stored outside decision
  evidence;
- replay time cannot recalculate decision-time freshness or change assessment;
- same normalized request plus same exact policy produces the same full
  assessment and assessment ID, including after JSON and subprocess replay;
- ranking tie-breaking is score, quality, then symbol, independent of input
  order for semantic rank results.

The closure audit found no anti-lookahead or determinism gap requiring code or
contract changes.

## 9. Replay and evaluation boundary

An `EvidenceSnapshot` freezes the complete normalized evidence consumed at
decision time and is content-addressed by canonical semantic JSON. A separate
immutable `BaselineRunRecord` freezes the assessment. Later `OutcomePath` and
`BaselineOutcome` objects reference that run and fingerprint without modifying
it.

Offline replay supports exact field-level comparison without providers,
resolvers, credentials, network, or wall clock. A2.10 calculates factual return,
MFE, MAE, and range observations and preserves original ranking membership. It
does not model fills, position size, brokerage, P&L, alpha, win rate, strategy
execution, or causal performance.

The checked-in `golden_manifest.json` is a test manifest whose synthetic cases
are constructed by pytest; it is not a persisted replay corpus. A runnable
corpus is a directory containing `snapshots/<snapshot-id>.json` and
`decision_records.jsonl`, with optional `outcome_records.jsonl`.

## 10. User-visible capability

Given explicit symbols/watchlists and required benchmark/expiry choices, A2 can
resolve instruments; retrieve quote, OHLCV, live option-chain, and A1 historical
option facts; build factual contexts; derive the accepted feature/indicator,
relative, MTF, and derivative evidence; produce an explainable deterministic
market state and candidate class; return `NO_TRADE`; rank eligible candidates;
capture decision evidence; replay it offline; attach later factual outcomes;
and regression-test frozen decisions.

A2 cannot choose a benchmark or sector automatically, ingest news/fundamentals,
reason as an Agent, select CE/PE or an option strategy, manage a position,
reconstruct arbitrary uncaptured historical knowledge, schedule future outcome
collection, simulate execution/P&L, operate a distributed replay farm, expose a
production service, integrate TradeMonitor, or place/modify/cancel broker orders.

## 11. Deferral closure and known limitations

The mandatory 51-record burn-down is authoritative in
`TIAF_DEFERRAL_REGISTER.md`: 3 were implemented already, 3 rejected, 2
superseded, 43 carried to A3 or later, and none implemented during closure.
Open work remains gated by calendar/event-time contracts, external evidence,
corporate actions/data vintage, historical/multi-expiry derivatives, strategy
semantics, Agent consumers, integration, or production operations.

The process-local scheduler can truthfully defer later members of a live batch;
it does not sleep or retry. Dhan is the only live provider. Option-chain event
time remains acquisition time where no provider event timestamp exists. These
limitations are explicit evidence states, not silent behavior.

## 12. A3 boundary

A3 may introduce Planner and specialist reasoning only after the major A2
baseline is frozen. Agents must consume shared A2 evidence and contracts rather
than fetch independently or duplicate deterministic calculations. They must
preserve `NO_TRADE`, disagreement, quality, freshness, provenance, immutable
decision records, and zero broker authority. Every Agent result must be
measurable against the frozen A2.9/A2.10 benchmark. Binding conditions are in
`TIAF_A3_ENTRY_CONDITIONS.md`.

