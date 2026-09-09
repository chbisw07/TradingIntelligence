# TIAF_A3.6.1 Market Intelligence Provider Fabric and Deep Research Foundation

## Status and authority

**Status:** architecture defined / pending acceptance and implementation.
**Accepted base:** `tiaf-a3.6` at
`a7e00121b1662bc68dddf620330e7cd18d1dbd5f`.
**Milestone type:** architecture/design pass only.

This document is the authoritative implementation design for A3.6.1. The
forensic Tapetide study is retained separately in
[`STUDY_Tapetide_Forensic_Validation_Report_Phase1.md`](STUDY_Tapetide_Forensic_Validation_Report_Phase1.md).
`STUDY_` material is evidence informing the architecture, not an authoritative
domain contract. `TBD_` continues to mean an unresolved design note.

No production provider adapter, MCP invocation, deep-research workflow, model
call, trading action, or broker operation is implemented by this architecture
pass.

## Purpose and scope

A3.6.1 defines a provider-neutral market-intelligence acquisition fabric and
the structured foundation for selective deep company research. It assumes that
no provider covers the full evidence spectrum and makes provider composition,
substitution, provenance, ambiguity, cost, and failure explicit.

The fabric must support company identity, fundamentals, filings/events,
industry and dependency context, sector/market/macro context, and selected
historical-integrity evidence. It acquires and normalizes evidence for existing
specialists; it does not replace specialist interpretation or introduce a
single market-intelligence god-agent.

The governing flow is:

```text
authorized semantic evidence request
        -> capability-specific routing policy
        -> bounded provider adapter invocation
        -> provider-native observation preservation
        -> explicit canonical normalization
        -> coverage/conflict/gap inspection
        -> selective budgeted enrichment, if justified
        -> canonical evidence + sparse evidence-graph update
        -> structured context pack
        -> existing specialist or optional reasoning gateway
```

## Non-goals and authority boundaries

A3.6.1 does not implement A4 arbitration, A5 position actions, A6 option
expression, A7 calibrated forecasting/learning, A8 TradeMonitor integration,
A9 scanner ensembles, or production execution. It does not create a global
market-timing engine, portfolio allocator, recommendation engine, unrestricted
browser, generic MCP proxy, or raw-provider-data prompt.

Authority remains:

- scanners are sensors and candidate-discovery sources;
- TIAF produces intelligence and advice;
- specialists interpret supplied evidence;
- TradeMonitor owns governance, risk, lifecycle, and execution coordination;
- the broker is final truth for live broker state; and
- TIAF never places, modifies, or cancels broker orders.

Dhan remains the accepted live market/F&O source. A market-intelligence adapter
cannot silently replace Dhan for quotes, derivatives, chains, or broker truth.

## Provider-neutrality invariant

Changing, adding, disabling, or removing Tapetide, Yahoo, an MCP, a REST API,
an OpenAI research tool, a licensed feed, or a local point-in-time dataset must
require only adapter, normalization-map, routing-policy, and configuration
changes. It must not require changes to:

- TIAF canonical evidence contracts;
- specialist interfaces or interpretation policies;
- A2 deterministic calculations or scoring;
- downstream opinion, replay, or decision semantics; or
- TradeMonitor/broker authority boundaries.

MCP is transport, not a TIAF domain abstraction. Provider names, tool schemas,
SDK types, authentication, transport errors, and raw payloads stay in optional
adapter packages. Canonical packages and specialists must not import them.

Provider-substitution acceptance requires two distinct provider fixtures to
normalize into the same canonical contract type, after which the same
specialist runs unchanged. Exact numerical equality is required only when the
source observations are semantically equivalent; provider agreement must not
be manufactured by lossy mapping.

## Capability model: two levels, not duplicate authority enums

A3.2 `AgentCapability` remains the coarse security and authorization ceiling.
A3.6.1 introduces a finer `MarketIntelligenceCapability` vocabulary for
provider declarations and routing below an already-authorized gateway. Fine
capabilities do not grant authority. Each maps to one existing coarse
capability, and a gateway may request only fine capabilities within its coarse
authorization.

| Fine market-intelligence capability | Existing A3.2 authority ceiling |
|---|---|
| `READ_COMPANY_PROFILE`, `READ_COMPANY_IDENTITY` | `READ_FUNDAMENTALS` |
| `READ_PEERS` | `READ_SECTOR_CONTEXT` |
| `READ_FINANCIALS`, `READ_FINANCIAL_RATIOS`, `READ_VALUATION_CONTEXT` | `READ_FUNDAMENTALS` |
| `READ_SHAREHOLDING`, `READ_PROMOTER_PLEDGE`, `READ_CREDIT_RATINGS` | `READ_FUNDAMENTALS` |
| `READ_ANALYST_FORECASTS` | `READ_FUNDAMENTALS` as provider evidence, never `READ_FORECAST` |
| `READ_FILINGS` | `READ_FILINGS` |
| `READ_NEWS` | `READ_NEWS` |
| `READ_CORPORATE_ACTIONS` | `READ_FILINGS` |
| `READ_EARNINGS_CALL_CONTEXT`, `READ_MANAGEMENT_EVIDENCE` | `READ_FILINGS` or `READ_NEWS`, selected explicitly by source class |
| `READ_INDUSTRY_CONTEXT`, `READ_COMPETITORS` | `READ_SECTOR_CONTEXT` |
| `READ_CUSTOMER_EXPOSURE`, `READ_SUPPLIER_EXPOSURE`, `READ_SUPPLY_CHAIN_EXPOSURE` | `REQUEST_ADDITIONAL_MARKET_EVIDENCE` |
| `READ_GEOGRAPHIC_EXPOSURE`, `READ_COMMODITY_EXPOSURE`, `READ_CURRENCY_EXPOSURE` | `REQUEST_ADDITIONAL_MARKET_EVIDENCE` |
| `READ_POLICY_REGULATION`, `READ_GOVERNANCE_RISK`, `READ_INTERNATIONAL_CONTEXT` | `REQUEST_ADDITIONAL_MARKET_EVIDENCE` |
| `READ_SECTOR_CONTEXT` | `READ_SECTOR_CONTEXT` |
| `READ_INDEX_CONTEXT`, `READ_MARKET_CONTEXT` | `READ_MACRO_CONTEXT` |
| `READ_INSTITUTIONAL_FLOW_CONTEXT`, `READ_MACRO_CONTEXT` | `READ_MACRO_CONTEXT` |
| `READ_IDENTIFIER_ASOF`, `READ_INDEX_MEMBERSHIP_ASOF` | `READ_SECTOR_CONTEXT` |
| `READ_POINT_IN_TIME_FINANCIALS` | `READ_FUNDAMENTALS` |

Provider analyst estimates are observations with explicit estimate semantics.
They are not empirically calibrated TIAF forecasts and cannot enter the A3.1
`ForecastEvidence` seam as `CALIBRATED`. A7 retains forecast production,
calibration, evaluation, promotion, and rollback.

An implementation may use a stable string-backed enum plus an explicit mapping
registry. It must not add every fine capability to `AgentCapability`, encode
capabilities as arbitrary queries, or allow metadata to widen authorization.

## Provider contract and registry

The implementation pass should add a provider-neutral
`MarketIntelligenceProvider` protocol with only stable operations such as:

- `identity()` returning provider and adapter identity/version;
- `manifest()` returning immutable capability declarations; and
- `fetch(request, context)` returning a typed provider observation batch or a
  typed failure.

The provider registry resolves adapter identity and capability declarations. It
does not expose transport objects, credentials, or a catch-all tool invocation.
Duplicate provider IDs or incompatible declaration versions fail registration.
Disabled optional adapters must not be imported during core package import.

Each `ProviderCapabilityDeclaration` should preserve:

- fine capability ID and `FULL`, `PARTIAL`, or `UNSUPPORTED` support;
- supported markets, exchanges, instruments, periods, and semantic filters;
- expected freshness and maximum historical coverage;
- point-in-time and revision limitations;
- rate-limit class, expected latency class, cacheability, and cost units;
- source-quality class and authority category;
- output nature: `PRIMARY_EVIDENCE`, `SECONDARY_STRUCTURED`,
  `INTERPRETED_AI`, or `PROVIDER_DERIVED`;
- upstream lineage ID when known, so correlated sources are not counted as
  independent confirmation;
- normalizer ID/version and native schema version; and
- explicit constraints or unavailable semantics.

An `UNSUPPORTED` declaration is useful audit truth; the router must never infer
support from provider presence or naming.

## Routing policy

Routing is per fine capability and policy/configuration version, never one
global `market_intelligence_provider`. A `CapabilityRoutePolicy` should name
eligible provider IDs, route mode, source-quality requirements, freshness and
PIT requirements, maximum calls/cost/latency, fallback conditions,
authoritative-confirmation triggers, and stop policy.

Supported modes are:

- `FIRST_SUCCESS`: call eligible providers sequentially until one result meets
  the declared sufficiency rule;
- `PRIMARY_WITH_FALLBACK`: use the configured primary, then a fallback only on
  typed absence, failure, staleness, or insufficient coverage;
- `MULTI_SOURCE`: intentionally acquire a bounded set of sources to improve
  coverage or expose disagreement;
- `AUTHORITATIVE_CONFIRMATION`: acquire an authority-class source only when a
  material ambiguity, conflict, or policy requirement justifies escalation.

Provider order is policy, not code branching. The router filters declarations
against the request before invocation and records every selection, skip,
fallback, and stop reason. `MULTI_SOURCE` does not imply unlimited parallel
fan-out. `AUTHORITATIVE_CONFIRMATION` does not delete lower-quality evidence.

Example policies may choose Tapetide as primary structured fundamentals and
escalate a material revenue/debt ambiguity to an authoritative filing. News may
use Tapetide plus a separately authorized research source before A3.5 clustering.
Customer or supply-chain context may use a research provider. Dhan routes remain
outside this fabric and pinned to accepted A1 market-data policy.

## Progressive evidence enrichment

The fabric implements:

```text
ACQUIRE -> NORMALIZE -> INSPECT -> ENRICH? -> UPDATE -> STOP
```

The caller supplies required, material, and optional evidence needs plus a hard
A3.2 budget. After each normalized batch, an `EvidenceCoverageAssessment`
records capability coverage, quality, freshness, PIT quality, semantic mapping
quality, contradictions, unresolved gaps, and source lineage. An immutable
`EnrichmentDecision` records `STOP_SUFFICIENT`, `STOP_BUDGET`,
`STOP_NO_ELIGIBLE_PROVIDER`, or `CONTINUE`, with the policy rule and expected
evidence value that justified it.

Enrichment continues only when all are true:

1. a required or policy-material gap/conflict remains;
2. an eligible provider declares relevant capability;
3. its output could improve the recorded sufficiency state;
4. authorization, timeout, call, latency, and cost budgets permit it; and
5. the route policy permits that escalation.

The controller stops when evidence is sufficient or the budget/eligible-source
set is exhausted. It never calls another provider merely because one exists.
Evidence sufficiency is deterministic/versioned policy, not an LLM's unbounded
choice.

A3.8 will later decide which specialists and research depth a candidate merits.
A3.6.1 only executes an already-authorized evidence request and performs
bounded provider-level enrichment. This preserves the Planner boundary.

## Provider-native preservation and canonical normalization

Normalization is two-stage. A typed `ProviderNativeObservation` first preserves
provider meaning without claiming a TIAF canonical metric. A versioned
`NormalizationRecord` then records whether and how it maps into an accepted
canonical evidence contract.

The native observation must retain, where applicable:

- provider, adapter, tool/endpoint, native record ID, and schema version;
- provider metric name, value, unit, period, and semantics;
- `REPORTED`, `PROVIDER_DERIVED`, or `TI_DERIVED` derivation class;
- publication time, `available_from`, availability basis, and acquisition time;
- revision identity and restatement/revision semantics;
- source URL or document reference and source-quality class;
- point-in-time quality and limitation; and
- payload checksum or immutable content reference, not an unbounded raw payload
  inside specialist contracts.

`NormalizationRecord` binds the native observation to an optional canonical
target, normalizer/version, mapping rationale, conversion/scale details, source
facts, and one of `EXACT`, `WELL_SUPPORTED`, `PROVIDER_DEFINED`, or `AMBIGUOUS`.
Only `EXACT` and policy-approved `WELL_SUPPORTED` mappings may emit a canonical
metric. `PROVIDER_DEFINED` and `AMBIGUOUS` observations remain visible for
audit, contradiction, and research-gap purposes but must not masquerade as a
canonical fact.

The fabric reuses existing canonical outputs:

- A3.4 `CompanyIdentity`, `FundamentalFact`, and `FundamentalDataset`;
- A3.5 `NormalizedEvent`, `EventCluster`, and event evidence references;
- A3.6 `SectorIdentity`, `SubjectMacroSensitivity`, and
  `ContextObservation`; and
- A3.1 `AgentEvidenceReference`, facts, citations, missing evidence, and
  fingerprints.

The implementation should use an additive provenance envelope or companion
normalization journal rather than replacing those accepted contracts. If a
later additive optional reference is necessary, it must preserve old JSON
validation and specialist behavior.

The forensic examples are mandatory mapping tests: Tapetide
`yearly_revenue` is not automatically `fundamental.revenue`; `Sales` is not
automatically revenue from operations; `Borrowings` is not automatically total
or gross debt; and provider free cash flow remains `PROVIDER_DERIVED` unless its
formula/source semantics are accepted.

## Contradiction preservation

Multi-provider ingestion is append/preserve, not last-write-wins. A
`ContradictionGroup` should identify the semantic subject, metric/relation,
period/as-of boundary, all observation and normalization IDs, differing values
or semantics, source-quality and lineage notes, materiality, resolution state,
and optional authoritative-escalation record.

Resolution states should distinguish `UNRESOLVED`, `QUALIFIED`, `SUPERSEDED`,
and `RESOLVED_BY_AUTHORITY`. A preferred source may drive a canonical current
projection only under explicit policy; conflicting observations remain in the
audit record and available to specialists. Two providers with shared upstream
lineage count as corroborating distribution, not independent confirmation.

This is evidence reconciliation. A4 still owns final opinion arbitration.

## Sparse evidence graph

The Evidence Graph is sparse, incremental, and materiality-driven research
memory. It is not a complete knowledge graph or a source of implicit truth.

Candidate nodes include company, security, sector, industry, index, competitor,
customer, supplier, end market, geography, commodity, currency, policy,
regulation, macro driver, catalyst, and risk. An `EvidenceGraphEdge` should
preserve:

- subject node, typed relation, and object node;
- materiality and evidence-quality/confidence basis;
- epistemic status: `CONFIRMED`, `REPORTED`, `INFERRED`, or `UNCERTAIN`;
- `valid_from`/`valid_to` where known;
- observation, acquisition, and last-verification times;
- evidence/normalization/source references and provider provenance;
- contradiction group/state where applicable; and
- edge/version identity and supersession history.

Unknown dates remain absent rather than invented. Graph updates are append-only
versions; replay selects only edges available at the requested decision time.
Edges do not silently become canonical company facts.

Research depth is demand-driven:

- `L0_IDENTITY`: entity and security identity;
- `L1_BASIC_CONTEXT`: sector, industry, broad peers, and current evidence;
- `L2_INVESTMENT_RESEARCH`: material business, competitive, customer,
  supplier, geography, policy, catalyst, and risk relationships;
- `L3_DEEP_POSITION_INTELLIGENCE`: targeted verification of material thesis and
  dependency edges for an explicitly authorized high-value case.

No company is required to have every node or relation.

## Fact, inference, and hypothesis separation

Every research assertion carries exactly one epistemic kind:

- `FACT`: directly supported by cited source evidence;
- `INFERENCE`: a reasoned interpretation linked to its supporting facts and
  reasoning policy/model identity; or
- `HYPOTHESIS`: a conditional forward-looking proposition with assumptions,
  disconfirming evidence, and research gaps.

An AI-generated statement is never promoted to `FACT` merely because it is
structured or repeated. An inference cannot overwrite its source facts. A
hypothesis cannot claim a calibrated probability unless it cites future A7
forecast evidence carrying accepted calibration metadata.

## Deep-research contracts and composition

Deep research is a composition of small immutable outputs, not one unrestricted
agent. The implementation pass should define provider-neutral records for:

- `CompanyResearchProfile` as an index of component records and evidence IDs;
- `BusinessModelAssessment`;
- `IndustryStructureAssessment`;
- `SupplyChainExposure` and `CustomerExposure`;
- `CompetitivePosition`;
- `ManagementEvidence`;
- `InternationalExposure` and `PolicyExposure`;
- `RiskRegister` and `CatalystRegister`;
- `ResearchHypothesis`;
- `ContradictingEvidence`; and
- `ResearchGap`.

Each component records subject/horizon, epistemic kind, claims and citations,
quality/freshness/PIT limitations, contradictions, missing evidence, producer
and policy/model version, evidence fingerprint, and timestamps. Collections
are immutable tuples and JSON arrays. All timestamps remain aware and normalize
to canonical `Asia/Kolkata`.

`CompanyResearchProfile` aggregates references and coverage; it does not copy
or flatten all provider payloads. Components may succeed, remain partial,
abstain, or report insufficient/missing evidence independently.

## Structured synthesis context and model boundary

The strongest configured model receives a bounded `ResearchSynthesisContext`,
not provider-native payload chaos. The context contains:

- normalized canonical facts and exact provenance;
- provider-defined/ambiguous observations explicitly labelled as such;
- contradiction groups and unresolved uncertainty;
- relevant sparse graph neighborhood at the requested depth/as-of;
- research gaps, risks, catalysts, and prior specialist opinions;
- unchanged A2 baseline/fingerprint; and
- authorization, budget, horizon, output schema, and authority constraints.

Optional synthesis goes only through the existing A3.2 `ReasoningGateway` and
model-tier mappings. It may emit cited inferences, conditional hypotheses,
causal candidates, contradiction explanations, or new `ResearchGap` requests.
It may not fetch evidence directly, call provider tools, fabricate facts, hide
conflict, invent calibrated probabilities, change A2, issue trade actions, or
override TradeMonitor authority.

No-LLM mode remains first-class. Structured acquisition, normalization,
coverage, contradiction detection, graph projection, and replay must work with
zero model calls.

## Cost and budget boundary

All evidence/model work remains under A3.2 authorization and `AgentBudget` call,
token, cost-unit, latency, and elapsed-time ceilings. Provider manifests expose
estimated cost/latency/rate classes; actual `AgentUsage` and audit records retain
observed calls and cost units. Secrets and vendor price tables stay outside
domain contracts.

The enrichment controller reserves budget before a call, accounts for actual
use afterward, and cannot exceed either request or global policy. Cache hits and
shared evidence reuse consume no provider call. Sufficient evidence must stop
fan-out. Budget exhaustion yields a typed partial/insufficient result with gaps;
it never becomes a market stance.

## Replay, audit, and provenance

A replayable market-intelligence run must retain:

- semantic request, capability, route-policy ID/version, and sufficiency policy;
- eligible/selected/skipped providers and reasons;
- provider/adapter/native-schema identities and declaration snapshots;
- native observation checksums/content references;
- normalization IDs/versions, mapping quality, canonical outputs, and failures;
- availability/publication/acquisition/revision/PIT semantics;
- contradiction groups and authoritative escalation;
- evidence-graph edge versions and selected as-of neighborhood;
- every enrichment decision and stop reason;
- evidence and context-pack fingerprints;
- specialist/reasoning inputs and outputs;
- model/prompt/config identity when used; and
- requested/actual tool, token, cost, latency, and failure usage.

Offline replay consumes persisted normalized/native references and decisions; it
does not silently contact a provider. A replay may either reproduce the
historical route decision or explicitly compare a newer normalizer/policy while
retaining both version identities.

## Failure semantics

The fabric must distinguish at least:

- unauthorized capability or invalid semantic request;
- provider/capability unsupported or provider disabled;
- unavailable/not found/out of historical coverage;
- partial/underfilled evidence;
- stale evidence;
- provider rate limit, timeout, network, or malformed output;
- semantic mapping `PROVIDER_DEFINED` or `AMBIGUOUS`;
- multi-source conflict or shared-lineage non-independence;
- point-in-time/revision limitation;
- budget exhausted; and
- no eligible enrichment source.

Failures are sanitized before crossing adapter boundaries. Partial evidence,
ambiguity, and contradiction remain evidence state and research gaps. None may
be translated into `POSITIVE`, `NEGATIVE`, or `NEUTRAL` infrastructure output,
and no unavailable field may be fabricated.

## Tapetide role

Tapetide is the first recommended production-candidate adapter, not the
architecture. Conditional candidate capabilities include company/profile,
financial statements and ratios, valuation, shareholding/pledge, credit
ratings, provider analyst estimates, filings/events, earnings-call context,
sector/index context, institutional flows, and selected historical identity or
membership.

The adapter must be read-only and tool-allowlisted, with a separate normalizer
per semantic tool family. Portfolio/watchlist mutation and any future write or
trading tools are prohibited. Tapetide native IDs and provenance are retained.

The Phase-1 study requires explicit limitations:

- similar field names differ across tools and accounting bases;
- `available_from` can be conservative rather than exact event time;
- later restatements may affect historical values;
- index-membership coverage observed in Phase 1 is too shallow for long
  survivorship-free backtests;
- banking evidence remains sector-specific and incomplete under generic ratios;
- customer/supplier/supply-chain/policy/international coverage is not assumed;
  and
- Tapetide does not replace Dhan.

## Yahoo and other secondary providers

Yahoo or another provider may be configured for a selected capability as a
fallback, supplementary observation source, or cross-check. It is not
authoritative merely because it agrees with Tapetide. The manifest must state
source quality, native semantics, coverage, PIT limitations, and known upstream
lineage. Shared lineage prevents double-counting as independent confirmation.

No secondary provider is a mandatory core dependency. Disabling every optional
provider must leave TIAF domain imports and deterministic tests operational.

## Future A7 and A9 compatibility

A7 may later consume historical canonical/native observations only with their
availability, revision, lineage, mapping, and PIT-quality records. Provider
analyst estimates remain a distinct evidence cohort. A7-calibrated forecasts
remain separately versioned and must never be backfilled from an A3.6.1
hypothesis.

A9 scanners may register as candidate sensors or evidence providers behind
future explicit policies. Scanner agreement is not a decision, and scanner
outputs do not bypass normalization, provenance, deduplication, A2 comparison,
specialist interpretation, A4 arbitration, or TradeMonitor authority.

## Implementation work packages

A3.6.1 remains one governed milestone with internal work packages:

1. **WP1 — Capability and provider contracts:** fine capability taxonomy,
   authority mapping, declarations, provider protocol, registry, typed failures,
   and optional-adapter import isolation.
2. **WP2 — Routing and progressive enrichment:** versioned per-capability route
   policies, four routing modes, coverage/sufficiency assessment, enrichment
   decisions, budget and audit integration.
3. **WP3 — Canonical normalization and contradictions:** native observation,
   normalization journal, explicit semantic maps, derivation/PIT semantics,
   contradiction groups, and existing-contract projections.
4. **WP4 — Tapetide adapter:** read-only tool allowlist, capability manifest,
   tool-family normalizers, sanitized failures, fixture tests, and bounded live
   acceptance.
5. **WP5 — Secondary provider fixture/adapter:** a non-Tapetide fixture first,
   followed by a real secondary adapter only when justified; provider
   substitution and lineage tests.
6. **WP6 — Sparse Evidence Graph:** versioned nodes/edges, PIT neighborhood,
   materiality-driven depth, contradiction links, storage boundary, and replay.
7. **WP7 — Deep-research contracts and synthesis context:** small component
   outputs, epistemic separation, gap requests, structured context pack, and
   optional reasoning-gateway integration.
8. **WP8 — Acceptance, replay, and failure hardening:** full fixtures, live
   read-only reconciliation, budgets, no-fan-out, security, import isolation,
   replay, scale, and failure injection.

WP1–WP3 must precede production adapters. WP6 and WP7 may build on their stable
identities. WP8 gates milestone acceptance. Work packages are not permanent
roadmap sub-milestones unless governance later requires that change.

## Implementation acceptance-test design

The implementation pass must include:

1. **Provider substitution:** two provider fixtures normalize semantically
   equivalent data to the same canonical type; the same specialist is unchanged.
2. **Provider absence:** disabling/uninstalling Tapetide leaves core imports and
   deterministic tests healthy.
3. **MCP independence:** canonical domain and specialist packages have no MCP
   imports.
4. **Tapetide isolation:** no A3 specialist imports the Tapetide adapter.
5. **Semantic ambiguity:** `yearly_revenue`, `Sales`, `Borrowings`, and
   provider-derived FCF cannot be silently mapped to unsafe canonical metrics.
6. **Multi-source conflict:** all observations and a contradiction group survive;
   no last-write-wins behavior.
7. **Missing capability:** unsupported/disabled providers return typed
   unavailable or insufficient evidence.
8. **Partial evidence:** downstream interpretation may abstain or request named
   missing evidence.
9. **Cost control:** sufficient evidence causes zero enrichment fan-out; call and
   cost budgets stop further providers.
10. **Point in time:** evidence is excluded before `available_from`; revisions
    and limitations survive replay.
11. **Replay:** native references, normalization, routes, conflicts, graph
    neighborhood, context packs, and outputs round-trip deterministically.
12. **Lineage:** correlated secondary sources do not count as independent
    confirmation.
13. **Security:** arbitrary tool names, URLs, queries, credentials, writes,
    broker methods, and provider calls from specialists are rejected.
14. **Epistemic separation:** model/provider hypotheses cannot validate as facts
    or calibrated forecasts.
15. **Backward compatibility:** accepted A2 and A3.1–A3.6 suites and serialized
    fixtures remain unchanged.

Live acceptance, when the implementation reaches WP8, must compare normalized
Tapetide outputs with source documents for a bounded representative set and
report semantic mismatches. It must not tune domain meaning to attractive live
results.

## Risks and deferred items

No new permanent `DEF-*` ID is required by this design pass:

- `DEF-012` already covers production fundamentals, filings, sector, macro, and
  peer acquisition; A3.6.1 designs its provider fabric and selects Tapetide only
  as a conditional first candidate.
- `DEF-008` continues to cover market-data fallback; market-intelligence routing
  must not be mistaken for Dhan/Zerodha quote fallback.
- `DEF-009` covers durable/distributed evidence-graph and cache persistence.
- `DEF-013` still governs corporate-action normalization and adjusted history.
- `DEF-049` still prevents claims of exact arbitrary historical reconstruction.

Open implementation questions that require evidence rather than architectural
guessing are: Tapetide production access/licensing and rate limits; exact tool
schema/version stability; storage/retention rights for native payload references;
authoritative source adapter availability; Yahoo or other provider selection;
upstream-lineage discoverability; and the operational graph store. These remain
explicit work-package inputs, not reasons to weaken provider neutrality.

## Architecture acceptance gate

Accept this design only if implementation can demonstrate that:

- providers can be substituted without changing canonical contracts or
  specialists;
- every provider/tool remains isolated behind a declared adapter/normalizer;
- ambiguity and conflict remain visible;
- no optional provider is required to import or test TIAF core;
- progressive enrichment performs no unjustified fan-out;
- all facts, inferences, and hypotheses remain distinct and cited;
- all acquisition/model use remains authorized, budgeted, and replayable;
- A2 and A3.1–A3.6 behavior remains unchanged; and
- A4–A9 and TradeMonitor authority boundaries remain intact.
