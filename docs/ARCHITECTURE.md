# Architecture

TIAF is intended to occupy an intelligence boundary between sources of market
candidates and the system that governs risk and execution:

```text
Scanners / Manual input / Third-party sources
                    |
                    v
       TradingIntelligence / TIAF
                    |
                    v
        structured intelligence
                    |
                    v
              TradeMonitor
                    |
                    v
                 Broker
```

TIAF will produce timestamped, attributable, and evaluable structured
intelligence. It will not own broker execution authority. TradeMonitor remains
the governor, while the broker remains the final truth for live state.

## Long-term missions

### Opportunity Intelligence

Given a bounded universe plus a requested style and horizon, identify the
strongest forward underlying opportunities, preserve `WAIT`, `NO_TRADE`,
`ABSTAIN`, and insufficient-evidence outcomes, and estimate remaining
opportunity only when evidence supports it. A3 produces specialist underlying
intelligence; A6 separately owns `CE`/`PE` and option-expression selection.

### Position Intelligence

Evaluate existing or adopted positions prospectively. The service should
eventually support conclusions such as `HOLD`, `WATCH_CLOSELY`, `PROTECT`,
`PARTIAL_BOOK`, `BOOK`, or `EXIT` without requiring the original trade thesis.

## Package boundaries

The namespaces reserve clear seams for contracts, data, planning, specialist
interpretation, arbitration, workflows, memory, evaluation, service delivery,
and observability. TIAF_A1 implements the factual data boundary through
immutable `AnalysisContext`. TIAF_A2 adds deterministic features, indicators,
explicit-benchmark and multi-timeframe evidence, a transparent baseline, and
provider-free replay/evaluation. The provider-neutral A3 architecture is now
defined in [`TIAF_A3_ARCHITECTURE.md`](TIAF_A3_ARCHITECTURE.md), with sequential
implementation gates in
[`TIAF_A3_DETAILED_ROADMAP.md`](TIAF_A3_DETAILED_ROADMAP.md). Planning and
interpretive namespaces contain the accepted A3.1 provider-neutral contracts,
registry, and exactly-one-specialist runtime foundation. A3.2 adds controlled
evidence and optional reasoning gateways, least-privilege capability policy,
model/tool budgets, freshness-aware evidence reuse, no-LLM mode, and audit
records. A3.3 adds the first deterministic Technical / Market-Structure
specialist over immutable scalar A2 fact projections, with typed detail, cited
claims, explicit contradiction, and zero model usage. A3.4 adds provider-neutral
point-in-time fundamental facts, deterministic period-safe preprocessing, a
controlled read gateway, and a cited no-LLM Fundamental / Company-Quality
specialist. A3.5 adds provider-neutral point-in-time event records, revision and
dedupe clusters, controlled news/filing reads, and a deterministic cited
News/Event specialist. The bounded A3.4/A3.5 adapters accept normalized
caller-owned/licensed data; no production scraper/feed, live model adapter,
multi-Agent orchestration, or execution behavior is implemented.
A3.6 adds separate Relative, Sector, and Macro specialists. Relative consumes
unchanged A2.8 facts; sector and macro use provider-neutral point-in-time
observations through controlled capability gateways. Sector and subject-macro
mappings are explicit/versioned, and reusable source snapshots are cached by
sector or market rather than fetched once per symbol. Production context feeds
and automatic mapping remain deferred; no arbitrary browsing was added.
A3.6.1 implements the provider-neutral acquisition layer without changing those specialists:
fine provider capabilities sit beneath A3.2 authorization, route policy is per
capability, native observations are retained before explicit normalization, and
gaps/conflicts trigger only budgeted progressive enrichment. It also defines a
sparse point-in-time Evidence Graph and structured deep-research context while
keeping provider/MCP code outside canonical packages. Detail is in
[`TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md`](TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md).
The bounded post-A3.6.1
[`Authoritative Confirmation Gateway`](TIAF_AUTHORITATIVE_CONFIRMATION_GATEWAY.md)
design reuses that fabric to confirm only material claims against exchange,
regulator, company-IR, or other official evidence. It preserves original
discovery evidence, field-level confirmation status, document/revision lineage,
event clustering, budgets, replay, and provider neutrality. No connector or
scraper was implemented by the architecture pass. The subsequent bounded
implementation supplies configured read-only source adapters, domain/redirect
validation, immutable document hashing/cache, deterministic parser boundaries,
claim reconciliation, and offline replay without adding a crawler.
A3.6.2 composes those accepted seams into one bounded company-research flow:
multi-capability acquisition, progressive enrichment, material-claim
confirmation, sparse evidence-backed graph updates, a normalized quality/PIT
context pack, deterministic FACT-only baseline components, explicit gaps and
contradictions, semantic fingerprinting, and provider-free replay. It adds no
new provider, model call, planner/LangGraph workflow, recommendation, or source
UI. Detail is in
[`TIAF_A3_6_2_MARKET_INTELLIGENCE_DEEP_RESEARCH_INTEGRATION.md`](TIAF_A3_6_2_MARKET_INTELLIGENCE_DEEP_RESEARCH_INTEGRATION.md).

## A3 architecture boundary

A3 Agents consume immutable A2 evidence through controlled, least-privilege
gateways; they do not recalculate A2 facts or receive arbitrary browser, shell,
database, broker, or execution access. An instrument-aware Planner selects
bounded specialists and reasoning depth under explicit token, tool, latency,
specialist, and cost budgets. A3 preserves individual cited opinions and
disagreement. A4 later arbitrates them, A5 manages adopted positions, A6 chooses
option expression, A7 evaluates and calibrates intelligence, and A8 integrates
with TradeMonitor without transferring authority.
