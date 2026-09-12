# Architecture

## Reading map and current status

Read [THESIS](TIAF_THESIS.md) → [SYSTEM](TIAF_SYSTEM_ARCHITECTURE.md) →
[DEPLOYMENT](TIAF_DEPLOYMENT_ARCHITECTURE.md) →
[PLUGGABILITY](TIAF_PLUGGABILITY_ARCHITECTURE.md) →
[SOURCE SEMANTICS](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md) →
[A4](TIAF_A4_DETAILED_ROADMAP.md) → [A5](TIAF_A5_DETAILED_ROADMAP.md) →
[MONITORING](TIAF_MONITORING_ARCHITECTURE.md) →
[ROADMAP](IMPLEMENTATION_ROADMAP.md).

| Reader question | Authoritative navigation |
|---|---|
| What exists and what is next? | [Capability map](TIAF_CAPABILITY_MAP.md), [milestones](MILESTONES.md), [development roadmap](TRADINGINTELLIGENCE_ROADMAP.md), [targets](TIAF_IMPLEMENTATION_TARGETS.md). |
| What was accepted? | A4/A5 detailed roadmaps link each architecture, implementation, study and closure; historical counts are not current test runs. |
| What is unresolved? | [Deferral register](TIAF_DEFERRAL_REGISTER.md) and [TBD index](README_TBD_DESIGN_NOTES.md); idea notes are not runtime specifications. |
| How do consumers access TI? | [Local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md), [Shell](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md); no remote/live public operation. |
| What did this consolidation change? | [Post-R1 record](TIAF_POST_R1_DOCUMENTATION_CONSOLIDATION_AND_SYNCHRONIZATION.md). |

A1–A4 are frozen. A5.1/A5.2 and R1 are accepted; documentation is ready for the
final A5 freeze/tag-readiness check, but `tiaf-a5-baseline` does not yet exist.
R2–R5 are pending pre-A6 work, not A5 freeze blockers. Monitoring is authoritative
future architecture, not runtime. Sector Rotation, Signal Qualification, A6/A7,
TM/scanner runtime integration and remote transport remain unimplemented.

Markdown architecture is normative. The [Fabric thesis](TIAF_Trading_Intelligence_Agent_Fabric_Thesis.docx),
[Hierarchy thesis](TI_Intelligence_Hierarchy_Thesis.docx) and
[Monitoring thesis](TI_Monitoring_Architecture_Thesis.docx) are unchanged,
non-normative human-readable companions.

## Implementation-layer overview

The authoritative [TI Pluggability Architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md)
now governs cross-cutting composition and replay invariants. It is architecture
only; the separate A1–A5 audit and bounded R1 acceptance are complete. Their
findings do not imply that R2–R5 or all target composition guarantees exist.

The authoritative top-level boundary is now
[TIAF_SYSTEM_ARCHITECTURE.md](TIAF_SYSTEM_ARCHITECTURE.md): logical TI_CORE,
curated public/engineering/private interfaces and trusted in-process capability
admission. This document remains the accepted implementation-layer overview.
The [post-A3 pass-1 review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md)
adopts that architecture with revisions. The subsequent
[narrow local facade](TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md) implements its trusted
same-process admission/lifecycle slice. The additive
[A4.1 runtime](TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md) now exposes its
deterministic captured-read evaluation. The internal
[A4.2 application bridge](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md)
adds one governed A3.8 enrichment/successor cycle without expanding the facade;
it exposes no direct live/public command. No remote service exists.
The [A4 major closure review](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
audits both slices as one L6 layer, now frozen at `tiaf-a4-baseline` (`494d968`).
The [POST_A4_PRE_A5 Shell review](TIAF_POST_A4_PRE_A5_TI_SHELL_ARCHITECTURE_REVIEW.md)
approves the [command-first local Shell architecture](TIAF_TI_SHELL_ARCHITECTURE.md),
now delivered by the bounded
[v0.1 implementation](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md) over the existing
facade. The Shell adds no remote service. Model challenge and NLP remain
optional/deferred; this is not A4 runtime expansion.

The authoritative
[A5 Position Intelligence architecture](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md)
defines the implemented bounded position layer. It consumes an explicitly supplied
TM/broker position snapshot and immutable A4 result, separates operational state
from analytical posture/thesis health/recommendation, emits only non-executable
advice and monitoring intent, and preserves captured replay. Its
[review](TIAF_A5_ARCHITECTURE_REVIEW.md) approves A5.1 contracts plus a
deterministic single-position baseline, now implemented by
[A5.1](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md). The additive
[A5.2 publication slice](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md) exposes
this baseline through a position-scoped captured-read facade capability and
bounded Shell command. No scheduler, TM integration, multi-leg policy, broker
operation or remote service exists.

The authoritative [source-semantics companion](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md)
now defines field-scoped authority, proposition comparability, independence,
revisions and preserved contradictions for A4 admission. The
[pass-2 review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md)
proceeds to pass 3 A4 architecture; its projection is implemented by the
accepted pre-A4 foundation.

The approved [A4 challenge/arbitration architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md)
now defines two bounded roles, deterministic arbitration, optional selective
challenge, preserved dissent and explicit non-action dispositions. The
[pass-3 review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md)
led to the [deployment review](TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md).
The approved [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md) chooses
one trusted local Python application runtime, isolated invocations and a single
filesystem writer; existing adapter-local MCP subprocesses remain. Service,
worker and shared-storage deployment is conditional, not implemented.
The [completed consolidation](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md)
selected the offline POST_A3_PRE_A4_FOUNDATION, followed by a narrow local
facade/lifecycle and deterministic A4. Its bounded open-world amendment allows
model-prior hypotheses to motivate governed research, never canonical facts.
The source foundation and local facade are implemented and accepted. A4.1 now
implements deterministic challenge/arbitration, fingerprints and replay; A4.2
implements its bounded no-model evidence-acquisition/successor lane. Optional
model challenge remains future work. No unrelated
TBD is promoted.

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

A3.1-A3.10 and the separate
[A3 major closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md) are frozen
at `tiaf-a3-baseline` (`e690da2`). The review's earlier `READY_TO_FREEZE_A3`
decision remains a historical closure record.

## Long-term missions

### Opportunity Intelligence

Given a bounded universe plus a requested style and horizon, identify the
strongest forward underlying opportunities, preserve `WAIT`, `NO_TRADE`,
`ABSTAIN`, and insufficient-evidence outcomes, and estimate remaining
opportunity only when evidence supports it. A3 produces specialist underlying
intelligence; A6 separately owns `CE`/`PE` and option-expression selection.

### Position Intelligence

The accepted A5 architecture makes this an advisory successor to A4, not an
operational position store. Broker/TM snapshots remain authoritative; stale or
incoherent truth fails closed. A5 owns analytical posture, thesis health,
recommendation and typed refresh needs. TM owns operational lifecycle and action;
A6 owns executable expression. See the
[authoritative design](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md).

Evaluate existing or adopted positions prospectively. The trader's original
entry rationale is optional, but A5.1 requires a current accepted A4 thesis/result
rather than inventing one. Its bounded taxonomy and compatibility relationship
to frozen A0 actions are defined in the authoritative A5 design.

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
disagreement. Accepted A4 arbitrates them and A5 advises on supplied adopted
positions. Future A6 chooses option expression, A7 evaluates/calibrates as an
overlay, and A8 integrates with TM without transferring authority.
