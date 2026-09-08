# TIAF_A3.4 Fundamental / Company-Quality Intelligence

## Status and boundary

**Status:** complete / accepted at `tiaf-a3.4`.
**Accepted base:** `tiaf-a3.3`.  
**Contract, gateway, specialist, policy, and formula version:** `1.0`.

A3.4 adds point-in-time, provider-neutral company evidence and a deterministic,
cited Fundamental Specialist for listed equities. It does not add news, live web
browsing, model forecasts, target prices, recommendations, order authority, or
multi-Agent arbitration. A3.5 owns News / Filing / Catalyst / Event
intelligence.

## Architecture

```text
licensed/authorized source or caller-owned data
        -> FundamentalProvider
        -> normalized FundamentalDataset
        -> controlled READ_FUNDAMENTALS gateway
        -> AgentEvidencePack
        -> FundamentalSpecialist
        -> AgentOpinionV2 + FundamentalAssessment
```

The specialist receives only validated evidence. It cannot call a provider,
HTTP client, browser, broker, shell, A2 calculator, or model SDK. Provider
selection, transport, licensing, secrets, retries, and caching remain outside
specialist reasoning. `AgentRuntime` and the gateway runtime retain their generic
registry dispatch; neither contains a Fundamental-specific branch.

## Source decision

Primary company or exchange filings are the preferred provenance class. NSE and
BSE expose filing/results surfaces with publication and revision information,
and NSE also describes paid corporate-data products. Those official surfaces
are interactive/download or licensed products; A3.4 does not assume that they
are a stable, freely automatable API and does not scrape them.

The implemented source boundary is therefore the `FundamentalProvider` protocol
plus `InMemoryFundamentalProvider`, a bounded read-only adapter for deterministic
fixtures and normalized data supplied by a licensed caller. It performs exact
symbol resolution, point-in-time filtering, explicit revision resolution,
family/history selection, and dataset fingerprinting. No provider-specific
model leaks into public contracts. A production licensed NSE/BSE or other
provider adapter and corresponding live reconciliation remain within the
existing `DEF-012` acquisition scope.

## Company and fact contracts

`CompanyIdentity` contains the canonical symbol, existing `InstrumentKey`
listing identity, optional legal name, sector/industry, and source entity ID.
It accepts equities only and requires the symbol to match the listing exactly;
there is no fuzzy entity matching.

`FundamentalFact` preserves:

- fact, company, metric, and family identity;
- finite numeric value, semantic unit, explicit scale, and currency where
  monetary;
- exact reporting period;
- `REPORTED` versus `DERIVED` basis;
- source-quality class, provider, and source reference;
- publication and acquisition timestamps;
- revision number/ID and replaced fact where available;
- data quality, freshness, and safe metadata;
- formula version, requested window, and source fact IDs for derived values.

All contract timestamps are aware and normalized to the canonical TIAF
`Asia/Kolkata` timezone. JSON emits `+05:30`. Naive datetimes are rejected.
Semantic collections are tuples in Python and ordinary arrays in JSON.

Units distinguish currency, percent points, ratios, per-share values, and
counts. Scale distinguishes ones, thousands, millions, billions, lakhs, and
crores. Currency facts require a three-letter currency code. Metric-specific
unit validation prevents percent/currency/ratio conflation. Scale conversion is
explicit deterministic multiplication; currency conversion is rejected unless
an explicit FX source is added in a later milestone.

## Reporting periods and point-in-time rules

`ReportingPeriod` supports `FISCAL_QUARTER`, `FISCAL_YEAR`, `TTM`, and `INSTANT`.
Fiscal quarters retain fiscal-year and quarter identity. A TTM period must list
exactly four constituent quarters. Instant facts use the same start/end date.
Period kind is part of arithmetic compatibility and is never inferred from a
calendar year.

`PeriodRequirement` states an exact kind and history count. Underfilled annual
or quarterly history is preserved in `FundamentalDataset.missing_periods`, the
dataset fingerprint, gateway warnings, coverage, and structured missing-evidence
requests. A request for five years never silently becomes a three-year result.

For decision time `T`, a fact is usable only when both `published_at <= T` and
`acquired_at <= T`. Period end alone never makes a result available. Future
publications and facts not yet acquired are excluded. Same-source revisions are
selected only by explicit revision number among facts visible at `T`; ambiguous
duplicates fail. Equally preferred cross-source disagreements remain separate
facts and become visible specialist contradictions.

## Fact families and deterministic metrics

The request vocabulary covers income, margins, capital efficiency, cash flow,
balance sheet, working capital, valuation, ownership, and stability. Canonical
metrics include revenue/profit/EPS, margins, ROE/ROCE/ROA, operating/free cash
flow, capex, cash/debt/equity/assets/liabilities, working-capital facts,
valuation, ownership/pledge/dilution, and deterministic trend/consistency facts.

Versioned deterministic helpers implement:

- exact annual or same-quarter-prior-year growth;
- adjacent-quarter growth, including fiscal-year boundaries;
- exact N-year CAGR from N+1 consecutive fiscal years;
- TTM sums from exactly four contiguous fiscal quarters;
- same-company, same-period, same-currency ratios;
- conversion of available results to `DERIVED` facts with formula/source IDs.

Insufficient history, a missing quarter, mixed period kinds, zero denominator,
currency mismatch, non-meaningful CAGR endpoints, and unsupported windows
produce explicit unavailable/not-meaningful results rather than shortened or
invented metrics. Reported facts never claim derivation metadata; derived facts
must provide it.

## Controlled gateway and caching

`FundamentalEvidenceGateway` handles only `READ_FUNDAMENTALS` plus
`EvidenceType.FUNDAMENTAL`. Its bounded attributes encode only requested families
and period counts; requests have no URL, headers, SQL, arbitrary query, or
credential field. It resolves exact company identity, asks the registered
provider for a typed request, projects every fact and reporting/provenance field
into an `AgentEvidencePack`, and records missing families or history.

The accepted generic gateway cache key already includes company, capability,
evidence type, family/period attributes, horizon, decision time, freshness,
context, and fingerprint. Cached results also require the same gateway
identity/version and an unexpired validity interval. This supports economical
quarterly/annual reuse at NIFTY-500 scale without hiding source changes.

## Deterministic specialist policy

`FundamentalSpecialist` has identity `FUNDAMENTAL`, version `1.0`, equity-only
scope, `LOW` deterministic cost, and only `READ_A2_EVIDENCE` plus
`READ_FUNDAMENTALS` authority. It performs no financial recalculation: it
interprets supplied normalized raw/derived facts.

The typed assessment keeps separate states for:

- growth;
- profitability;
- margins;
- capital efficiency;
- balance-sheet strength;
- cash-flow quality;
- earnings quality;
- valuation;
- stability;
- ownership/governance evidence availability and disclosed risks;
- fundamental momentum;
- deterministic company quality;
- contradictions.

Policy `tiaf.fundamental-specialist/1.0` uses transparent generic engineering
thresholds. It was not fitted to RELIANCE, HDFCBANK, KAYNES, or any live example.
Synthesis is hierarchical: evidence sufficiency and sector applicability first,
then the distinct operating dimensions, valuation, contradictions, horizon
relevance, and finally stance. There is no opaque composite quality score.

Valuation uses a supplied own-history percentile when available; an isolated
high/low P/E is not an oracle. Valuation becomes `NOT_MEANINGFUL` for supplied
non-positive earnings and `UNKNOWN` without contextual history. Peer valuation
is not inferred without peer evidence.

Fundamental momentum is separate from quality level. A high-return business can
still be deteriorating. Profit growth with weak cash conversion, growth with
contracting margins, high returns with high leverage, source disagreement, and
quality/growth with extreme valuation remain explicit contradictions.

Ownership ratios support only narrow evidence statements such as an elevated
reported pledge or dilution. They do not establish management quality,
trustworthiness, governance culture, competitive advantage, or a moat.

## Sector and horizon caution

Conventional industrial leverage, EBITDA, and valuation rules are unsafe for
banks/NBFCs/insurers. When such a company is detected, affected dimensions and
company quality become `SECTOR_POLICY_REQUIRED`, applicability is reduced, and
the specialist abstains. Banking-specific metrics are not fabricated.
Sector-specific policies for financials, cyclicals, utilities, capital-intensive
industrials, technology, and loss-making growth companies remain extension
points rather than dozens of premature rules.

Fundamental relevance is low for `DAY`, background-level for positional weeks,
and rises for three-to-six and six-to-twelve-month horizons. A DAY request
abstains; it does not turn slow-moving financial evidence into an intraday
signal.

## Confidence, claims, and output

The output is `AgentOpinionV2` with typed `FundamentalAssessment` detail.
Allowed stances remain `POSITIVE`, `NEGATIVE`, `NEUTRAL`, `MIXED`,
`INSUFFICIENT_EVIDENCE`, and `ABSTAIN`; none means BUY/SELL/HOLD/EXIT.
Baseline agreement is `NOT_COMPARABLE` because the A2 market-state baseline and
company-quality view answer different questions, while the exact A2 assessment
reference and evidence fingerprint remain unchanged.

Policy-derived confidence is the product of evidence coverage, weakest quality,
weakest freshness, internal dimensional agreement, sector applicability, and
horizon relevance. It is not a probability that price rises. Self-reported and
empirically calibrated confidence remain absent.

Every emitted dimensional claim cites supplied `EvidenceFact` IDs through exact
gateway evidence references. The assessment records evidence IDs by dimension,
and each contradiction records both evidence and fact IDs. Missing/partial/stale
evidence is not upgraded. Stable reason codes explain evidence, conflicts,
valuation, leverage, cash flow, sector gating, and degradation.

## No-LLM, replay, and future use

The accepted A3.4 path makes zero LLM calls, consumes zero model tokens, incurs
zero model cost, and has no model identity or prompt. A future optional model may
summarize explicitly supplied annual reports, transcripts, notes, or management
commentary only through the controlled reasoning gateway. It is not required by
A3.4 and may not browse freely.

Fundamental datasets and Agent run records serialize deterministically with
provider/formula/policy versions, periods, publication/acquisition times,
fingerprints, citations, confidence basis, stance, and usage. These point-in-time
facts can later become A7 forecasting features without look-ahead leakage, but
A3.4 creates no forecast, return probability, or price target.

## Validation and limitations

Synthetic coverage includes profitable growth, growth/extreme valuation, low
growth/cheap valuation, leveraged improvement, margin deterioration,
profit/cash divergence, leverage-driven returns, loss-making growth,
insufficient and stale evidence, source conflicts, missing history,
financial-sector gating, and future-publication exclusion. Period tests cover
annual, YoY quarter, QoQ, fiscal boundaries, TTM, CAGR, missing quarters, and
insufficient history. Architecture tests enforce no provider/broker/HTTP/browser/
shell/model authority in the specialist and no recommendation fabrication.

No production fundamental provider was bound, so live company cases and manual
live filing reconciliation were not performed. This is an explicit source/
licensing limitation, not synthetic live validation. The deterministic adapter,
contracts, gateway, and specialist are runnable and testable without network
access. A3.5 may consume filing/event evidence, but must not move news semantics
or uncontrolled web access into A3.4.
