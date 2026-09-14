# Architecture

## Reading map and current status

Project control starts at the [README dashboard](../README.md) →
[milestone ledger](MILESTONES.md) → [roadmap](TRADINGINTELLIGENCE_ROADMAP.md).
The ledger owns historical/current acceptance and tag status; roadmaps own
intended order, not retrospective rewrites. From there read
[THESIS](TIAF_THESIS.md) → [SYSTEM](TIAF_SYSTEM_ARCHITECTURE.md) →
[PLUGGABILITY](TIAF_PLUGGABILITY_ARCHITECTURE.md) →
[MONITORING](TIAF_MONITORING_ARCHITECTURE.md) →
[ECOSYSTEM](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md) →
[A4](TIAF_A4_DETAILED_ROADMAP.md) / [A5](TIAF_A5_DETAILED_ROADMAP.md).
The README's documentation map defines the shared taxonomy: normative Markdown
architecture, implementation inventory (capability map), postponed work (deferral
register), non-authoritative TBD ideas, dated STUDY/ACCEPTANCE evidence and
non-normative DOCX/PDF companions. Accepted architecture is not runtime acceptance.

For the cross-system view, start with the
[Trading Ecosystem Architecture](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md):
scanners propose, TI advises, TI Monitoring reevaluates, TM authorizes and
coordinates, and brokers execute. It defines candidate/position/action ownership
and future Sheets/Cockpit boundaries without implementing integration. Bounded
captured-read A6 is now frozen; richer expression/forecast integration is future.

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
| What is A7's accepted architecture? | [FF-integrated architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md), [17-finding reconciliation](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md), [integrated stage crosswalk](TIAF_A7_DETAILED_ROADMAP.md); ARCHITECTURE ACCEPTED after the explicit FF integration and independent review. No runtime approval. |
| What is the stable forecasting platform? | [FF architecture ACCEPTED](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md), [bounded roadmap](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md), [decision and findings dispositions](TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md). Primitive/composite typed DAG, common truth, paired evaluation; miniature DEFINED, not implemented. |
| How do I learn the Forecasting Framework? | [Separate platform thesis PDF](TI_Forecasting_Framework_Thesis.pdf), [editable Word edition](TI_Forecasting_Framework_Thesis.docx), [creation/validation and 28 findings](TIAF_FORECASTING_FRAMEWORK_THESIS_RECORD.md). Non-normative; all 28 findings reconciled; FF architecture ACCEPTED; A7 integration RECONCILED; A7 architecture ACCEPTED; sequencing/planning NEXT. |
| Where does FM/LFDE fit? | [Advanced FMLFDEForecaster design](TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md), [research matrix](TIAF_FM_LFDE_RESEARCH_RECONCILIATION.md), [nested family roadmap](TIAF_FM_LFDE_DETAILED_ROADMAP.md). Internals retained; shared platform ownership is FF. |
| How do I understand FM/LFDE? | [Illustrated thesis PDF](TI_FM_LFDE_Market_State_Forecasting_Thesis.pdf), [editable DOCX](TI_FM_LFDE_Market_State_Forecasting_Thesis.docx), [creation record and current addendum](TIAF_FM_LFDE_THESIS_RECORD.md). Unchanged advanced-reference edition; separate FF thesis RECONCILED; FF architecture ACCEPTED; A7 integration RECONCILED; A7 architecture ACCEPTED; sequencing/planning NEXT. |
| How do I understand A7's forecasting, evaluation and learning concepts? | [Reference thesis PDF](TI_Forecasting_Evaluation_Learning_Thesis.pdf), [editable DOCX](TI_Forecasting_Evaluation_Learning_Thesis.docx), [creation record](TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md). Unchanged non-normative creation edition; thesis RECONCILED; A7 architecture ACCEPTED, implementation NOT_STARTED. |

A1–A5 are FROZEN; A5 is tagged at `tiaf-a5-baseline`. R1 is ACCEPTED / DONE.
R2 Discovery Metadata and R3 Composition/Pinned Verification are ACCEPTED / DONE.
R4 Optional Adapter Import Isolation is ACCEPTED / DONE;
[R5 COLD Ownership / Configuration](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md)
is [ACCEPTED / DONE](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION_ACCEPTANCE.md),
closing the R1–R5 pre-A6 track. Monitoring is authoritative
future architecture, not runtime. Sector Rotation, Signal Qualification, A7,
TM/scanner runtime integration and remote transport remain unimplemented.

A6 is **FROZEN at `tiaf-a6-baseline`; A6.1–A6.4 ACCEPTED / DONE;
`expression.assess` PUBLISHED. A7 is ARCHITECTURE ACCEPTED / IMPLEMENTATION NOT_STARTED / RUNTIME NOT_IMPLEMENTED**:
[Trade Expression Intelligence architecture](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md),
[reconciliation record](TIAF_A6_RECONCILIATION_RECORD.md), and
[detailed roadmap](TIAF_A6_DETAILED_ROADMAP.md). The bounded A6.1
contracts/admission/policy slice is [accepted](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION_ACCEPTANCE.md);
the [A6.2 evaluator](TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY.md) is
[accepted](TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY_ACCEPTANCE.md), and
[A6.3](TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE.md) publishes it through governed
captured-read facade/Shell paths without changing ecosystem authority and is
[independently accepted](TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE_ACCEPTANCE.md).
The [A6.4 closure](TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md)
records the 93-case acceptance corpus and freeze-readiness decision without
creating a commit or baseline tag.

The non-normative [A6 user-reference thesis](TI_Trade_Expression_Intelligence_Thesis.docx),
[PDF preview](TI_Trade_Expression_Intelligence_Thesis.pdf) and
[findings/validation record](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_THESIS_RECORD.md)
are created. The [thesis/architecture reconciliation](TIAF_A6_THESIS_ARCHITECTURE_RECONCILIATION.md)
resolves all fourteen findings and updates the normative Markdown. The
[independent architecture acceptance](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md)
records READY_TO_IMPLEMENT_A6_1. The
unchanged thesis retains its dated source snapshot and then-next wording.
The [reconciled A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md) proposes
one exact equity-return target, chronological calibrated evaluation and explicit
shadow/advisory approval; it does not change frozen A4/A5/A6 or the nine-operation
catalog. Thesis RECONCILED; A7 architecture ACCEPTED, implementation NOT_STARTED. The intervening
[FF platform design](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md) is ACCEPTED and
FM/LFDE is its advanced family. A7 ARCHITECTURE is ACCEPTED; sequencing/planning is NEXT;
**TIAF A7 — IMPLEMENTATION SEQUENCING AND FF-0 MINIATURE REALIZATION PLAN** is next.
FF repeat acceptance closes FFA-B01. The completed
[A7 integration reconciliation](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md)
and [independent acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) precede the
next sequencing plan; implementation remains separately authorized.
Historical records remain preserved; the current A7 architecture and roadmap are integrated.
The [original source audit](TIAF_A7_RECONCILIATION_RECORD.md)
remains a historical architecture-pass record.

Markdown architecture is normative. The [Fabric thesis](TIAF_Trading_Intelligence_Agent_Fabric_Thesis.docx),
[Hierarchy thesis](TI_Intelligence_Hierarchy_Thesis.docx) and
[Monitoring thesis](TI_Monitoring_Architecture_Thesis.docx) are unchanged,
non-normative human-readable companions.

## Implementation-layer overview

The authoritative [TI Pluggability Architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md)
now governs cross-cutting composition and replay invariants. The architecture
itself remains a design record; the separate A1–A5 audit and bounded R1–R5
implementation/acceptance passes establish the delivered guarantees they tested.

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
A6 owns non-executable analytical expression suitability; TM alone owns
ExecutionIntent and action authority. See the
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
positions. Frozen A6 chooses bounded option expressions; future A7 evaluates/calibrates as an
overlay, and A8 integrates with TM without transferring authority.

<a id="forecasting-framework--a7-integrated-architecture-acceptance-next"></a>

## Forecasting Framework and A7 — architecture accepted; sequencing next

The [A7 acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) records
**A7_ARCHITECTURE_ACCEPTED** on **2026-09-15 (Asia/Kolkata)**:
A6 FROZEN; FF ARCHITECTURE ACCEPTED; A7 ARCHITECTURE ACCEPTED;
A7 THESIS RECONCILED AS NEEDED; A7 / FF IMPLEMENTATION NOT_STARTED;
RUNTIME NOT_IMPLEMENTED. FM/LFDE remains an optional advanced Forecaster family.

A7 is the lifecycle umbrella. FF owns forecasting contracts, typed DAG and
bounded runtime; Evaluation owns Ground Truth, Outcome Journal, joined Forecast
Ledger, benchmarks/metrics/calibration qualification/drift; Learning owns
candidate fits and the single artifact/lifecycle registry. Independent reviewer
approval and trusted COLD selection stay separate. The
[A7 roadmap](TIAF_A7_DETAILED_ROADMAP.md) contains FF-0…FF-7 unchanged,
with the old A7.1…A7.5 crosswalk. FF-0/1 raw research precedes FF-2's calibrated
miniature; publication is separately accepted, advanced families optional.

The [FF repeat review](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE_REPEAT.md)
closed FFA-B01; the [A7 integration](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md)
then reconciled all 17 A7 findings. Original HOLD, correction, repeat acceptance,
integration and all 28 FF findings remain historical evidence. Their then-next
language and the Deferral Register's dated A7.x notes are not the current queue.
All 58 canonical deferral rows and six thesis DOCX/PDF artifacts are unchanged.

Exact next prompt: **TIAF A7 — IMPLEMENTATION SEQUENCING AND FF-0 MINIATURE REALIZATION PLAN**.
This is a planning gate, not implementation readiness or authorization to train,
approve models, publish capabilities, change frozen A6 or begin A8.
