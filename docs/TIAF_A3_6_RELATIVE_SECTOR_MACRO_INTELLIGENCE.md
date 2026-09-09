# TIAF_A3.6 Relative / Sector / Macro Context Intelligence

## Status and boundary

**Status:** complete / accepted at `tiaf-a3.6`.

TIAF_A3.6 adds three independently registered specialists and does not create a
single market-context Agent:

- `RELATIVE_STRENGTH` (`tiaf.relative-specialist`, version `1.0`)
- `SECTOR` (`tiaf.sector-specialist`, version `1.0`)
- `MACRO` (`tiaf.macro-specialist`, version `1.0`)

Each produces a standard immutable `AgentOpinionV2` with typed detail, exact
evidence citations, A2 baseline comparison, an evidence fingerprint, and zero
model usage. The output says whether one context is supportive for the subject
and horizon. It is not a recommendation, prediction, allocation, option
expression, order, or position action. A3.7 remains the next milestone.

## Three-specialist separation

The Relative Specialist owns interpretation of already-computed comparative
facts. The Sector Specialist owns explicit classification, sector breadth,
participation, and multi-period rotation interpretation. The Macro Specialist
owns horizon-relevant market-risk, volatility, rates/yields, currency,
commodity, policy, growth, and geopolitical context. Their capabilities,
policies, detail schemas, reason codes, missing-evidence results, and run records
are separate, so any one can succeed, fail, or abstain independently.

Specialists receive an `AgentEvidencePack`; none calls a provider, network,
browser, shell, model SDK, broker, or another specialist.

## Relative evidence and the A2.8 boundary

A2.8 remains the sole owner of bar alignment and deterministic subject return,
benchmark return, return spread, return ratio, ATR-normalized excess move, and
consistency calculations. A3.6 copies usable scalar `FeatureResult` values with
`relative_feature_facts()` and attaches the caller-declared `BenchmarkReference`
with `relative_evidence_reference()`. The specialist does not access OHLCV bars
or recompute any formula.

An interpretable relative result requires one consistent explicit benchmark
symbol and role plus an already-computed A2.8 spread. Subject and benchmark
returns are optional audit detail: when present they are retained and cited, but
A3.6 does not reject the accepted A2.9 projection merely because it persists only
spread and consistency. Missing or conflicting benchmark identity yields
`INSUFFICIENT_EVIDENCE`, never an implicit NIFTY/sector/peer choice. Market,
sector, peer, and custom roles remain distinct.

Policy `1.0` groups performance into strongly/mildly outperforming, inline,
strongly/mildly underperforming, mixed, or insufficient states. Separate detail
retains consistency, cross-timeframe alignment/conflict, leadership, and
ATR-relative extremes. Strong outperformance plus a supplied extreme remains
supportive historical context but also exposes chase risk; it is not a future
return forecast.

Relative reason codes include `RELATIVE_OUTPERFORMANCE`,
`RELATIVE_UNDERPERFORMANCE`, `RELATIVE_LEADERSHIP`, `RELATIVE_LAG`,
`RELATIVE_MTF_ALIGNED`, `RELATIVE_MTF_CONFLICT`, `RELATIVE_EXTENDED`,
`BENCHMARK_MAPPING_MISSING`, and `BENCHMARK_MISMATCH` plus quality/freshness
codes.

## Sector identity and mapping policy

`SectorIdentity` stores sector/industry identity, benchmark symbol, mapping
source/version/quality, and an effective interval. The in-memory adapter accepts
only exact, caller/provider-supplied mappings and rejects simultaneous active
mappings. It never infers a sector from a symbol or company name.

Automatic benchmark and sector mapping remains `DEF-047`: no accepted
provider-neutral classification source is present. This milestone therefore
implements the safe explicit-mapping contract and controlled path, not a
heuristic mapper.

## Sector evidence, breadth, and rotation

Provider-neutral `ContextObservation` records may carry only supplied sector
facts such as absolute return/trend, sector-versus-market return, subject-versus-
sector spread, breadth, participation/concentration, volatility, and explicit
sector catalyst context. Every observation carries a source/version/reference,
observation time, availability time, quality, freshness, interval, and optional
horizon applicability.

Breadth remains `UNKNOWN` when no constituent-universe facts are supplied. The
baseline supports supplied positive/negative or above-MA fractions and an
explicit top-constituent concentration fraction; it does not manufacture
constituents, highs/lows, or breadth. Headline strength with weak breadth or
narrow participation becomes `CONCENTRATED_LEADERSHIP`, not broad strength.

Rotation requires at least two supplied periods. A one-day or single-period
return yields `INSUFFICIENT_EVIDENCE` for rotation. The deterministic states are
`ROTATING_IN`, `LEADING`, `IMPROVING`, `NEUTRAL`, `WEAKENING`, `LAGGING`,
`ROTATING_OUT`, `MIXED`, and `INSUFFICIENT_EVIDENCE`.

The assessment separately retains sector-versus-market, subject-versus-sector,
breadth, participation, concentration, and catalyst dimensions. Thus a leading
sector with a lagging subject and a weak sector with a resilient subject remain
explicit contradictions rather than one forced story.

Sector reason codes include `SECTOR_LEADING`, `SECTOR_IMPROVING`,
`SECTOR_ROTATING_IN`, `SECTOR_WEAKENING`, `SECTOR_LAGGING`,
`SECTOR_ROTATING_OUT`, breadth/concentration codes,
`SUBJECT_OUTPERFORMS_SECTOR`, `SUBJECT_LAGS_SECTOR`, event support/conflict, and
mapping/quality/freshness codes.

## Macro evidence architecture

The bounded macro vocabulary contains `MARKET_INDEX`, `VOLATILITY`,
`INTEREST_RATES`, `BOND_YIELDS`, `INFLATION`, `CURRENCY`, `COMMODITIES`,
`CENTRAL_BANK`, `FISCAL_POLICY`, `LIQUIDITY`, `ECONOMIC_GROWTH`,
`GEOPOLITICAL`, `GLOBAL_RISK`, and `OTHER`. A source need only implement families
it truly supplies.

`ContextObservation.kind` separates a discrete `EVENT` (for example, an
announced rate decision) from persistent `STATE` (for example, tightening).
Availability time, not hindsight, controls point-in-time inclusion. A future
release or announcement cannot enter an earlier snapshot.

There is no production macro feed in this repository. `MacroContextProvider`
and `InMemoryMacroContextProvider` establish provider-neutral/test and caller-
supplied boundaries. `MacroContextEvidenceGateway` is the only implemented
`READ_MACRO_CONTEXT` path. It accepts a market, decision time, horizon, requested
families, and freshness requirement—never a URL or arbitrary query. Live macro
validation is therefore not claimed.

## Macro regimes and explicit sensitivity

The Macro Specialist keeps market risk, volatility, rates/yields, currency, and
commodity context separate. Market-risk interpretation requires multiple
supplied dimensions; one index candle cannot create a regime. Volatility is not
recalculated from prices. Rate direction is not a policy-path forecast. Currency
direction is not automatically favorable or adverse.

`SubjectMacroSensitivity` explicitly maps a subject, macro family, and driver to
`BENEFITS_FROM_RISE`, `HARMED_BY_RISE`, `NEUTRAL`, `UNKNOWN`, or
`NOT_APPLICABLE`, with source/version/quality/effective dates. Commodity,
currency, or rate direction becomes company impact only through such a mapping.
Missing material mapping produces `MAPPING_REQUIRED` or partial/insufficient
evidence; broad risk context may remain interpretable with reduced confidence.

Macro reason codes include `RISK_ON_CONTEXT`, `RISK_OFF_CONTEXT`,
`MARKET_STRESS`, `VOLATILITY_ELEVATED`, `RATES_TIGHTENING`, `RATES_EASING`,
explicitly sensitivity-supported currency/commodity impact codes,
`MACRO_SENSITIVITY_UNKNOWN`, `MACRO_CONFLICT`, and quality/freshness/coverage
codes. A positive broad-risk dimension alongside an adverse mapped commodity
dimension remains `MIXED` with a contradiction.

## Horizon and instrument relevance

Observations can declare applicable horizon labels and providers filter them at
the decision time. DAY analysis emphasizes immediate index/volatility shocks
and known event evidence. POSITIONAL analysis can use near-term rates, currency,
commodity, and event risk. Future 3–6 and 6–12 month callers can request longer-
cycle growth, monetary, fiscal, inflation, and commodity evidence without
changing the contract.

For cash equities, explicit sector and sensitivity mappings determine whether
context is applicable. Stock derivatives may consume the same underlying
context later, while A3.7 owns derivative-specific risk. Index instruments can
use broad market/macro state directly. No A3.6 policy selects an instrument or
times the market.

## Controlled gateways and shared reuse

`SectorContextEvidenceGateway` owns only `READ_SECTOR_CONTEXT`;
`MacroContextEvidenceGateway` owns only `READ_MACRO_CONTEXT`. Both require the
existing A2 baseline reference and project immutable context observations into
an `AgentEvidencePack`.

The accepted A3.2 cache still keys complete semantic requests. In addition, the
context gateways cache normalized source snapshots by sector or market,
decision time, horizon, family set, freshness, and provider version. Subject-
specific packs and fingerprints are then projected from that shared snapshot.
Consequently the same sector/macro source fetch is reused across constituents
while citations, mapping, sensitivity, subject, and evidence fingerprint remain
correct. This avoids an N-stock-by-identical-context acquisition pattern. The
current cache is process-local; distributed persistence remains deferred.

## Confidence, no-LLM behavior, and audit

Confidence combines evidence coverage, quality, freshness, dimensional
agreement, mapping quality, and horizon relevance. It is explicitly not success
probability. Every specialist uses deterministic policy `1.0`; `AgentUsage`
reports zero LLM calls, input/output tokens, and model cost. Optional later model
reasoning may explain already-supplied interactions but may not fetch facts,
invent mappings/sensitivities, override missing evidence, or fabricate odds.

Standard `AgentRunRecord` retains specialist/version, policy version, A2
baseline/fingerprint, all evidence and mapping references, claims/citations,
stance, confidence basis, timestamps, and usage. Typed detail is stable canonical
JSON. A3.7 can later compare each contextual opinion with the unchanged A2
benchmark.

## Validation and live status

Synthetic coverage includes outperform/underperform/inline and MTF-relative
conflict; missing/mismatched benchmarks and relative extremes; all four strong/
weak sector/subject combinations; rotating-in/out and single-period exclusion;
narrow breadth, missing mapping, and sector-event conflict; risk-on/off/mixed,
volatility, rate, currency, commodity, sensitivity, and macro-conflict cases;
point-in-time future exclusion; claim/citation integrity; immutable JSON
round-trip; and sector/market source-cache sharing across symbols.

The read-only `scripts/inspect_relative_specialist.py` path supports existing
A2/Dhan live acquisition or a captured A2.10 input. Live sector and macro
validation is intentionally skipped until trustworthy bounded production
classification/context providers exist. Fixtures are never reported as live.

The 2026-09-09 representative live read covered RELIANCE/NIFTY,
HDFCBANK/BANKNIFTY, and KAYNES/NIFTY. Each retained its A2 `NO_TRADE` baseline,
used the exact supplied primary-timeframe spread, reported `SINGLE_TIMEFRAME`
because the accepted A2.9 request contains no cross-timeframe relative bundle,
and used zero model calls/tokens/cost. Direct A2.8 reconciliation confirmed each
spread against its component returns. No policy threshold was changed in
response to those outputs.

## Limitations and A3.7 handoff

- `DEF-047` still governs automatic benchmark/sector classification.
- `DEF-012` still governs licensed production sector, peer, and macro adapters.
- Breadth exists only when a trustworthy constituent universe supplies it.
- The process-local shared cache is not a distributed context store.
- Regime states are transparent engineering baselines, not fitted forecasts.

A3.7 may consume these independently cited contextual opinions alongside A2.7
derivative evidence. It must not turn them into option-contract selection,
position management, unsupported probabilities, or execution authority.
