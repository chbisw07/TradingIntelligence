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

A3.1-A3.10 are accepted through `tiaf-a3.10`. The separate
[A3 major closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md) concludes
`READY_TO_FREEZE_A3`; `tiaf-a3-baseline` is the recommended major tag after
the documentation-only closure changes are reviewed and committed.

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

A3.7 completes the initial nine-specialist inventory with separate Derivatives
Context, Opportunity Quality and Opportunity Risk specialists, accepted at
`tiaf-a3.7`. The
[`A3.8 Planner + Specialist Orchestration design`](TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md)
now implements the bounded workflow boundary: capability/dependency-driven
selection, deterministic bounded parallel waves, shared evidence and budget
reservations, selective MI enrichment/confirmation/deep research, affected-node
reruns, partial stops and captured replay. Framework-neutral planner contracts
and policy sit above a replaceable LangGraph infrastructure adapter. The Planner
owns workflow decisions, not investment decisions; opinions and A2 disagreement
remain separate for A3.9. A3.8 has serial/LangGraph deterministic acceptance;
see the [offline acceptance study](STUDY_A3_8_USER_LEVEL_ACCEPTANCE.md).

A3.8 is now frozen at `tiaf-a3.8`. The
[A3.9 Structured Opportunity Intelligence MVP design](TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md)
defines the implemented application boundary: a single-underlying immutable product
assembled from captured A3.8 results, with typed contribution/bias semantics,
explicit observation-state rules, retained A2/conflicts/gaps, separate confidence,
cited reasons and offline assembly replay. Runtime lives in
`tiaf.service.opportunity_intelligence`; see the
[acceptance study](STUDY_A3_9_USER_LEVEL_ACCEPTANCE.md). It neither reruns specialists nor acquires providers,
votes among opinions, ranks candidates or assumes A4–A10 authority.

A3.9 is frozen at `tiaf-a3.9`. The
[A3.10 hardening implementation](TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md)
implements the final A3 sub-milestone: content-addressed complete replay packages,
recorded/deterministic/comparison replay, observational A2/A3 comparison,
unknown-safe cost accounting, lossless failure/degradation summaries and a
closure-readiness evidence seam and a 14-case offline acceptance corpus. See the
[acceptance study](STUDY_A3_10_USER_LEVEL_ACCEPTANCE.md). It changes no
intelligence state or authority. The later, separate
[A3 closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md) found no A3
blocker and did not change A3.10 runtime semantics.

## A3 architecture boundary

A3 Agents consume immutable A2 evidence through controlled, least-privilege
gateways; they do not recalculate A2 facts or receive arbitrary browser, shell,
database, broker, or execution access. An instrument-aware Planner selects
bounded specialists and reasoning depth under explicit token, tool, latency,
specialist, and cost budgets. A3 preserves individual cited opinions and
disagreement. A4 later arbitrates them, A5 manages adopted positions, A6 chooses
option expression, A7 evaluates and calibrates intelligence, and A8 integrates
with TradeMonitor without transferring authority.
