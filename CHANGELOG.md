# Changelog

All notable changes to this project will be documented here.

## Unreleased

- Added TIAF_A3.6 as three separate deterministic, cited Relative Strength,
  Sector / Rotation, and Macro Context specialists with independent identities,
  typed detail, policies, contradictions, missing-evidence behavior, A2
  comparison, and zero model usage.
- Added provider-neutral point-in-time sector/macro observations, explicit
  effective-time sector and subject-sensitivity mappings, bounded in-memory/test
  providers, controlled `READ_SECTOR_CONTEXT` / `READ_MACRO_CONTEXT` gateways,
  future-evidence exclusion, and sector/market source-snapshot reuse across
  symbols. Automatic mapping and licensed production context adapters remain
  deferred; no browsing, recommendation, forecast, trading, or execution was
  added.
- Added TIAF_A3.5 provider-neutral event/entity/source/structured-fact,
  point-in-time revision, contradiction, dedupe-cluster, and dataset contracts;
  deterministic classification/relevance/materiality helpers; stable JSON; and
  a bounded caller-supplied/test provider adapter.
- Added controlled `READ_NEWS` and filing-source-restricted `READ_FILINGS`
  gateway projections with cache-version identity, plus the deterministic cited
  News / Catalyst / Event Specialist and typed cluster assessment. Duplicate
  reports are one interpreted event, later corrections cannot leak backward,
  conflicting sources remain visible, and model usage is zero. No production
  scraper/feed, recommendation, forecast, or execution behavior was added.
- Added TIAF_A3.4 provider-neutral company identity, reporting-period,
  point-in-time fundamental fact/dataset, revision, source-quality, unit,
  currency, and deterministic derivation contracts.
- Added exact YoY/QoQ/CAGR/TTM/ratio preprocessing, explicit insufficient-window
  results, the bounded read-only `FundamentalProvider` adapter boundary,
  controlled `READ_FUNDAMENTALS` gateway projection/cache compatibility, and
  future-publication exclusion.
- Added the deterministic cited Fundamental / Company-Quality Specialist with
  dimensional growth, profitability, margin, capital-efficiency, balance-sheet,
  cash-flow, earnings-quality, valuation, stability, ownership-evidence,
  momentum and contradiction states; financial-sector abstention; and zero LLM
  usage. No production source scraper, forecast, target, recommendation, or
  execution behavior was added.
- Added the TIAF_A3.3 deterministic Technical / Market-Structure Specialist,
  immutable scalar A2 evidence-fact projections, typed technical assessment,
  dimension-grouped interpretation, explicit contradiction/invalidation,
  cited claims, A2 baseline comparison, and no-LLM registry/runtime path.
- Added versioned horizon-aware technical policy 1.0, 13 synthetic market-state
  cases, confidence/degradation/authority coverage, and a read-only live
  inspection CLI. Live representative attempts correctly stopped on expired
  Dhan credentials (`DH-901`) without inventing evidence.
- Added TIAF_A3.2 controlled evidence and optional reasoning gateways with
  deterministic registries, least-privilege capability authorization, a
  read-only frozen-A2 evidence adapter, freshness/version-aware result reuse,
  provider-neutral model-tier mappings, and explicit downgrade policy.
- Added pre/post tool/model/token/total-token/cost/time budget enforcement,
  schema-validated structured model output, sanitized failures, immutable audit
  records, future reasoning-cache identity, and a complete no-LLM path with
  zero provider calls or model usage. No live model adapter or specialist
  intelligence was added.
- Added the TIAF_A3.1 provider-neutral Agent foundation: stable specialist and
  controlled-capability identities, immutable requests/evidence/claims/
  confidence/opinion/run records, budget and usage enforcement, runtime-
  checkable specialist/reasoning protocols, an extensible registry, and a
  failure-isolating single-specialist runtime.
- Preserved the frozen A0 AgentOpinion schema 1.0 alongside an explicit A3
  AgentOpinion v2 compatibility boundary, added deterministic run-record JSON,
  a calibrated-forecast consumer seam, security/architecture coverage, and no
  provider, LLM, LangGraph, broker, option-expression, or position behavior.
- Defined the provider-neutral TIAF_A3 Specialist Intelligence architecture
  and sequential A3.1–A3.10 implementation roadmap. The design preserves A2 as
  the visible deterministic benchmark, introduces controlled evidence and
  budget gateways, instrument-aware specialist planning, cited claims,
  separated confidence dimensions, replay/cost/failure records, and a future
  calibrated-forecast seam. That architecture pass implemented no runtime.
- Assigned fundamental and news/event evidence foundations to A3, refined A7
  to include forecasting/calibration without renumbering major milestones, and
  removed CE/PE from planned A3 output because A6 owns option expression.
- Closed the complete TIAF_A2 deterministic platform across A2.1-A2.10, added
  the major foundation baseline, acceptance report, A3 entry conditions, and
  the governed 51-record deferral burn-down. No scoring policy or runtime
  contract changed during closure.
- Added the provider-neutral A2.10 evaluation package with content-addressed
  normalized evidence snapshots, immutable decision records, exact offline
  replay, policy comparison, subsequent outcome paths, MFE/MAE, frozen-ranking
  statistics, append-only JSONL storage, and field-level regression checks.
- Added live capture plus provider-free replay/regression CLIs, synthetic golden
  coverage, secret-field scanning, canonical decision-time freshness order, and
  sorted-key assessment identity input. A2.9 policy weights, thresholds, and
  scoring semantics remain unchanged.
- Hardened A2.9 interpretability by publishing each component score's basis
  direction, separating score-relevant reasons from retained evidence facts,
  qualifying MTF labels with existing thresholds, and adding a complete
  deterministic policy inspector. Scoring weights and thresholds are unchanged.
- Added the separate provider-neutral TIAF_A2.9 deterministic-baseline package
  with immutable request, versioned policy, evidence-contribution, component,
  market-state, assessment, and ranking contracts.
- Added transparent horizon-aware direction, opportunity, remaining-room,
  extension/chase-risk, alignment/conflict, quality/freshness gating, four
  candidate classes, and eligible-only deterministic ranking. Policy 1.0 is a
  generic engineering benchmark and was not fitted to live examples.
- Added a read-only single/batch baseline smoke with explicit benchmark
  mappings, component/provenance output, stable JSON, all-`NO_TRADE` behavior,
  unit/architecture coverage, and the detailed A2.9 technical record.
- Added a stable-ID deferral register covering documented A0-A2.8 decisions,
  linked deferred capability-map entries, and established a deferral burn-down
  review at major milestone closures rather than after every sub-milestone.
- Added TIAF_A2.8 explicit MARKET/SECTOR/PEER/CUSTOM benchmark contracts and
  six deterministic cross-symbol relative-return, return-ratio, Wilder-ATR,
  and transition-consistency measurements.
- Added exact latest common bar-endpoint suffix alignment, weakest-history
  quality/provenance propagation, zero-denominator and malformed-history
  safeguards, and explicit missing-benchmark behavior.
- Added ordered first-class multi-timeframe contexts retaining independent
  A1 context and feature-bundle identity, plus ten factual count, return-sign,
  EMA-position, slope-sign, agreement, and disagreement measurements using
  valid-contributor denominators.
- Added dedicated read-only relative-strength and multi-timeframe smoke tools,
  regression/architecture coverage, and explicit automatic benchmark mapping,
  SuperTrend aggregation, resampling, scoring, and recommendation deferrals.
- Corrected a live-proven Dhan master normalization defect narrowly: the
  `0001-01-01` non-applicable expiry sentinel on cash/index rows no longer marks
  current index benchmarks inactive; derivative expiry semantics are unchanged.
- Added 39 TIAF_A2.7 provider-neutral, single-expiry option-chain features for
  expiry/ATM geometry, premiums, IV, provider Greeks, exact-window OI and
  option volume, put/call ratios, maximum OI, concentration, weighted strikes,
  and ATM bid/ask spreads.
- Added defensive strike normalization and identity checks, strict full-window
  semantics, independent missing-field handling, zero/NaN/infinity guards,
  inherited option-chain quality/acquisition-time provenance, a read-only
  `--derivatives` smoke pack, tests, and explicit model/strategy deferrals.
- Added 15 TIAF_A2.6 completed-history prior-boundary, signed-distance,
  close/wick excursion, prior-range geometry, compression, and latest-range
  comparison features with strict current-bar exclusion.
- Added shared anti-lookahead range helpers, ATR/range reuse, a `--levels`
  read-only smoke pack, numerical/provenance safeguards, regression tests, and
  detailed placement/deferral documentation.
- Added 17 TIAF_A2.5 completed-history raw, relative, dispersion, slope,
  persistence, close-transition participation, signed-balance, and transparent
  price/range correlation features.
- Added strict exact-window and destination-volume alignment semantics,
  zero-denominator/variance guards, inherited history quality and market-time
  provenance, a `--volume` read-only smoke pack, tests, and architecture docs.
- Added the first-class TIAF_A2.4 indicator contracts, explicit registry, and
  indicator-agnostic deterministic engine.
- Added completed-history SuperTrend, Wilder RSI, MACD, Wilder ADX/+DI/-DI,
  population Bollinger Bands, and Donchian Channel calculations with a
  dedicated read-only smoke CLI.
- Added indicator architecture documentation, extension guidance, revised A2
  numbering, and a platform capability-placement map; HalfTrend is explicitly
  deferred pending selection of a stable canonical variant.
- Added 23 TIAF_A2.3 completed-history moving-average, regression,
  directional-efficiency, persistence, adjacent-structure, rolling-range, and
  ATR-normalized extension measurements.
- Added strict A2.3 window/warm-up semantics, shared pure calculations,
  inherited history quality, latest-bar market timestamps, numerical guards,
  a `--trend` smoke view, and architecture documentation.
- Preserved safe provider/operation diagnostics for failed AnalysisContext
  evidence and exposed them in the read-only context smoke without leaking
  credentials or untyped exception details.
- Corrected Dhan REST quote `previous_close` normalization to derive it from
  `last_price - net_change`; raw OHLC close remains diagnostic metadata rather
  than being mislabeled as the prior-session close.
- Corrected A2.2 previous-close semantics after live validation: normalized
  quote `previous_close` is canonical, with a session-aware daily-history
  fallback shared by price change and move/ATR calculations.
- Clarified that `price.open`, `price.high`, `price.low`, and day-range position
  use current-session quote facts rather than latest historical-bar OHLC.
- Added 23 TIAF_A2.2 price-location, log-return, candle-range, Wilder ATR,
  realized-volatility, rolling-extrema, drawdown/run-up, and signed move/ATR
  measurements to the deterministic feature registry.
- Added strict exact-window and numerical-safety behavior, worst-source quality
  propagation, and explicit market-time versus acquisition-time provenance.
- Extended the read-only feature smoke with `--extended` and explicit intraday
  annualization, plus deterministic A2.2 tests and architecture documentation.
- Added the TIAF_A2.1 provider-neutral immutable feature contracts, explicit
  calculator registry, deterministic context-only engine, and factual bundle
  summary.
- Added seven small baseline price/history/return/range features with exact
  lookback, insufficient-data, source-quality, timestamp, and provenance
  semantics.
- Added a read-only A1-to-A2 feature smoke utility, focused test coverage, and
  the A2.1 architecture/handoff record.
- Added the canonical A1 architectural baseline and engineering acceptance
  report, and closed milestone/roadmap status for the A2 handoff.

## TIAF_A1.7 — Complete / Live Validated

- Added immutable, provider-neutral AnalysisContext requirements, subjects,
  evidence descriptors, aggregate context, ordered batch outcomes, and factual
  diagnostic summaries.
- Added a dependency-injected builder that resolves through A1.5 and routes
  quote, history, option-chain, and exact historical-option requests through
  the A1.6 coordinator.
- Added deterministic completeness, quality, retrieval freshness,
  partial/failure, and dual retrieval/source-observation provenance semantics.
- Hardened the read-only utility with explicit required-versus-optional
  derivatives and sequential, order-preserving batch inspection.
- Preserved A1.6 provider-scheduler blocks as typed A1.7 deferrals with gate
  provenance, partial-context retention, truthful `UNKNOWN` required freshness,
  and explicit completed/partial/deferred/error batch statuses.

## TIAF_A1.6 — Complete / Live Validated

- Added a provider-neutral in-process factual cache with deterministic keys,
  optional LRU capacity, explicit invalidation, generation tracking, and local
  metrics.
- Added caller-relative freshness requirements and an explicit operation policy
  registry without universal TTL assumptions.
- Added a monotonic, non-sleeping provider scheduler with explicit rate blocks,
  cooldowns, provider disable/enable controls, and documented Dhan quote and
  option-chain policies.
- Added synchronous fetch coordination, key-scoped single flight, explicit
  bounded stale-on-error behavior, immutable acquisition results, tests, and a
  read-only Dhan quote demo.

## TIAF_A1.5 — Complete / Live Validated

- Added frozen provider-neutral instrument query, resolved identity, and
  explicit unique/ambiguous/not-found result contracts behind a synchronous
  resolver protocol and provider registry.
- Added header-driven Dhan detailed instrument-master ingestion with a narrow
  local file cache, absent/explicit-refresh downloads, atomic replacement,
  typed schema failures, and indexed exact lookup.
- Added exact provider-ID/trading-symbol lookup, filtered equity/index/future/
  option resolution, inactive-record visibility, order-preserving batches, a
  deterministic eligible F&O-underlying universe, tests, and read-only smoke.
- Added configurable primary cash/F&O exchange policy after live validation
  exposed legitimate NSE/BSE symbol duplication. Policy-selected results are
  explicit, query scope always overrides policy, and F&O universes are unique
  within their configured exchange scope.
- Hardened all Dhan factual smoke utilities with symbol-first master resolution
  and mandatory symbol/security-ID consistency before provider transport.
- Excluded Dhan `DUMMYSAN` diagnostic underlyings from canonical F&O universes
  using provider identity metadata rather than broad symbol substring matching.

## TIAF_A1.4 — Accepted / Live Validated

- Added frozen provider-neutral rolling historical-option bars, series,
  expiry context, and ATM-relative strike types behind a segregated protocol.
- Added Dhan expired-options requests with complete factual arrays, half-open
  30-day chunking, deterministic merging, and typed malformed-data handling.
- Corrected the rolling expired-options endpoint to its live-validated dedicated
  expiry-code mapping: `1` near, `2` next, and `3` far; `0` is rejected.
- Added mocked tests, a read-only smoke utility, and the detailed evolving TIAF
  implementation-target map.

## TIAF_A1.3 — Accepted / Live Validated

- Added provider-neutral immutable expiry, option-chain, strike, contract, and
  Greeks snapshots behind a segregated derivatives provider protocol.
- Extended the Dhan adapter with active-expiry discovery and complete live
  option-chain normalization, including contract IDs, spot, prices, depth, OI,
  volume, IV, Greeks, provenance, and typed failures.
- Added deterministic mocked coverage and an explicit-expiry read-only smoke
  utility.

## TIAF_A1.2 — Accepted / Live Validated

- Added a secret-safe, read-only DhanHQ v2 adapter using an injectable HTTPX
  transport.
- Added normalized full quotes, ordered 1,000-instrument batch chunking, daily
  and supported intraday OHLCV, explicit mappings, and typed error translation.
- Added mocked transport/provider tests and an optional one-quote smoke script.

## TIAF_A1.1 — Complete / Frozen

- Added provider-neutral market-data enums, normalized models, provider
  protocol, typed failures, and deterministic normalization/freshness helpers.
- Added A1.1 model, serialization, protocol, validation, and public-export tests.

## TIAF_A0 — Complete / Frozen

- Added immutable, versioned Pydantic domain contracts for requests, evidence,
  opinions, assessments, horizons, snapshots, and option expressions.
- Added contract validation, serialization, and public-export tests.
- Established `Asia/Kolkata` as the canonical timezone for contract timestamps.
- Made finalized semantic contract collections immutable tuples while retaining
  JSON-array and Python-list input compatibility.

## 0.1.0 - 2026-09-05

- Established the initial `TIAF_TGT0` repository baseline.
- Added packaging, configuration, documentation, namespace scaffolding, and
  smoke tests.
