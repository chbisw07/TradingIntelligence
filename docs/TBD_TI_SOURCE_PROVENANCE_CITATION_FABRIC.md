# TBD — TI Source, Provenance & Citation Fabric

**Consolidation disposition: SPLIT (2026-09-11).** The
[transition plan](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md) assigns Core
semantics to the now-implemented POST_A3_PRE_A4_FOUNDATION; DEF-054 minimal
captured-source rendering follows accepted foundation/facade/A4 with Shell v0.1,
while richer bibliography/Web remains later. Render from governed captures
without re-research; missing artifacts stay unavailable. Broad adapters and
original presentation ideas remain deferred.
The [A4 closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) changes DEF-054 to
`PLANNED` only for that minimal Shell renderer now that source and A4 lineage
exist. Rich reports, bibliography, Web UX and new acquisition remain deferred.

**Status:** Split after post-A3 pass 2: Core semantics promoted with revisions;
citation/report UX and adapter proposals remain deferred.
**Prefix meaning:** `TBD_` = intentionally unresolved / to be architected later  
**Current authority:** [Source semantic architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md)
for source/claim identity, scoped authority, comparability, independence,
confirmation, revisions and contradiction semantics.
**Remaining purpose:** Preserve later citation UX (DEF-054), source acquisition
and presentation ideas without treating them as implemented features.

The [pass-2 review](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md)
classifies all 28 sections. Only its explicitly revised Core principles are
promoted; this entire note is not an authoritative architecture. Examples below
are design hypotheses, not callable APIs, enabled sources or runtime contracts.

## 1. Why this exists

TradingIntelligence (TI) now has an increasingly rich Market Intelligence stack with multiple possible sources:

- structured providers / MCPs such as Tapetide and Yahoo
- authoritative sources such as NSE, BSE, SEBI, RBI and company Investor Relations
- future APIs / licensed feeds
- bounded website sources
- financial-media sources such as Economic Times, Moneycontrol, Business Standard, Reuters and similar outlets
- future OpenAI research/search capabilities
- future internal or local datasets

A later TI report should answer not only **what is the conclusion?** but also **what evidence supports it, where did that evidence come from, and which source was authoritative, secondary, corroborating, or conflicting?**

The intended spirit is similar to citation-rich research systems: a material conclusion should remain traceable to the evidence and source(s) that support it.

This document originally deferred that requirement until A3 closure. Source
semantics are now designed separately from the still-deferred report UX.

## 2. Hard invariant

> **Every material factual conclusion produced by TI should be traceable to one or more evidence records and source references.**

This traceability must remain provider-neutral, replayable where possible, auditable, point-in-time aware where applicable, compatible with multiple simultaneous sources, and independent of any one MCP, API, website or vendor.

Changing or adding a source must not require redesigning downstream specialist contracts or decision semantics.

## 3. Historical rationale — why full architecture was deferred until after A3

The following sequence describes the original note's context. A3 is now frozen;
the current sequence is in section 27.

A3.7–A3.10 still need to complete:

- A3.7 Derivatives / Opportunity-Risk Specialists
- A3.8 Planner + Specialist Orchestration
- A3.9 Structured Opportunity Intelligence MVP
- A3.10 Agent Replay / Baseline Comparison / Cost & Failure Hardening

These milestones may clarify final report/result shapes, how Opportunity Intelligence exposes reasons, what specialist outputs need source attribution, how synthesis outputs should cite supporting evidence, and what replay/audit contracts need to persist.

Correct sequence:

```text
NOW
  create this TBD note

A3.7
A3.8
A3.9
A3.10

A3 closure review
  - deferred-item burn-down
  - cumulative A1 + A2 + A3 alignment review
  - documentation reconciliation
  - regression/live acceptance/freeze

THEN
  reopen this TBD
  architecture pass
  implementation pass
```

## 4. Source categories to support

### 4.1 Authoritative / primary sources

Examples:

- NSE
- BSE
- SEBI
- RBI
- company Investor Relations / official company website
- official government ministry / regulator
- official credit-rating agency disclosure
- official IPO documents / prospectus / DRHP / RHP

Typical role: primary factual confirmation, original filings, regulatory facts, exact financial semantics, corporate actions, management changes, material company disclosures, macro/policy truth.

### 4.2 Structured Market Intelligence providers

Examples:

- Tapetide
- Yahoo MCP / yfinance-based providers
- future finance MCPs
- future licensed structured APIs

Typical role: efficient structured acquisition, fundamentals, ownership, forecasts, earnings/calendar, events/news, sector/index context, fallback/corroboration.

These are useful evidence providers but must not automatically be treated as universally authoritative.

### 4.3 Secondary financial-media sources

Examples:

- Economic Times
- Moneycontrol
- Business Standard
- CNBC-TV18
- Reuters
- Bloomberg
- other reputable financial media

Typical role: breaking news, management commentary, market interpretation, sector developments, interviews, broker/analyst views, international context, discovery of potentially material events.

These should normally remain secondary/contextual evidence when an authoritative primary source exists.

### 4.4 Lower-confidence sources

Examples:

- generic aggregators
- repost sites
- blogs
- forums
- social media

Potential role: discovery only, weak contextual evidence, possible research-gap triggers.

These should require stronger corroboration and must never silently receive authoritative status.

## 5. Configurable source registry

Source participation should be configuration-driven.

Conceptually:

```yaml
market_intelligence_sources:
  tapetide:
    enabled: true
    role: primary_structured
  yahoo:
    enabled: true
    role: secondary_fallback
  nse:
    enabled: true
    role: authoritative
  bse:
    enabled: true
    role: authoritative
  company_ir:
    enabled: true
    role: authoritative
  rbi:
    enabled: true
    role: authoritative_macro
  economic_times:
    enabled: true
    role: secondary_news
  moneycontrol:
    enabled: true
    role: secondary_news
```

Exact schema is deferred.

Potential future fields:

- enabled
- source ID
- source type
- authority class
- supported capabilities
- priority
- fallback role
- cost class
- rate limits
- freshness expectations
- official domains
- point-in-time limitations
- retention/replay behavior
- credential requirements
- legal/access constraints

## 6. Capability-based source selection

Source choice should be per capability, not merely global.

```yaml
READ_NEWS:
  sources: [tapetide, yahoo, moneycontrol, economic_times]

READ_REGULATION:
  sources: [rbi, sebi, nse, bse]

READ_FINANCIAL_RESULTS:
  sources: [tapetide, nse, bse, company_ir, yahoo]

READ_MACRO_CONTEXT:
  sources: [rbi, government, reuters]
```

Different sources have different roles by capability.

## 7. Multi-source acquisition and routing

The future system should not query every source every time.

Reuse the A3.6.1 philosophy:

> **Acquire -> normalize -> inspect -> selectively enrich -> update -> stop**

Possible patterns:

```text
Routine:
Tapetide -> sufficient -> stop

Corroboration:
Tapetide -> ambiguity/rate limit/gap -> Yahoo

Material event:
Tapetide/news discovery -> materiality detected -> NSE/BSE/company IR confirmation

Deep context:
structured providers + official source + financial media + future OpenAI research
-> normalized evidence -> synthesis
```

Orchestration belongs to TI, not to providers.

## 8. Source authority model

The former global source hierarchy is **rejected** for A4 evidential judgment.
Use claim/field/domain/subject/time-scoped authority with a captured basis and
limitations, as defined in the promoted semantic architecture. Company guidance
is evidence of what was announced, not proof of future realization; an exchange
link cannot validate a provider-defined valuation formula.

Current gateway route preference and coarse `SourceAuthority` summaries remain
accepted acquisition behavior. They are not a universal truth ordering, field
confirmation or independence proof. Preserve conflicting applicable sources.

## 9. Claim-to-source traceability

Material claims should carry explicit links to supporting evidence.

Conceptually:

```text
Claim
  claim_id
  statement
  evidence_refs[]
  source_refs[]
```

Source references may contain:

```text
source_id
source_name
source_type
authority_class
title
URL / document reference
published_at
event_time
acquired_at
provider/tool
document_id
content_fingerprint
```

The minimal semantic projection is now designed in the promoted architecture;
its bounded implementation remains a pre-A4 prerequisite. Original A3 claim and
evidence IDs must survive. User-facing citation contracts remain deferred.

## 10. Report-level citation behavior

The user-facing TI report should support source visibility similar in spirit to research citations.

Example:

```text
KAYNES has announced a material order win.[1]
The order is significant relative to the company's recent revenue base.[2]
Sector context remains supportive.[3]

Sources
[1] NSE filing — ...
[2] Company investor presentation — ...
[3] Tapetide sector data — ...
```

The exact rendering may later be CLI, Web UI or other clients.

## 11. Concise view vs expanded audit view

Normal concise view:

```text
Sources: NSE filing, Tapetide, Moneycontrol
```

Expanded audit view:

```text
[1] NSE filing
    authority: AUTHORITATIVE
    published: ...
    URL: ...
    evidence_id: ...

[2] Tapetide
    role: PRIMARY_STRUCTURED
    acquired: ...
    tool: get_financials

[3] Moneycontrol
    role: SECONDARY_MEDIA
    published: ...
    URL: ...
```

## 12. Citation selection / source compression

A conclusion may be supported by many records. The report should not dump all of them.

Potential preference:

```text
NSE filing -> primary citation
Tapetide -> supporting structured evidence
Moneycontrol -> contextual citation
```

Possible future selection criteria:

- authority
- directness
- recency
- relevance
- independence
- uniqueness
- contradiction state
- whether the source materially changed the conclusion

## 13. Event deduplication and source clustering

Repeated stories must not inflate confidence.

Example:

```text
Tapetide article
Yahoo article
Moneycontrol article
Economic Times article
NSE filing
```

may all refer to one underlying event.

Reuse existing `NormalizedEvent` source records and `EventCluster` identity.
Retain every observation; one underlying event does not mean five independent
bullish events, nor does cluster membership prove a common publication origin.
Source independence needs its own qualified lineage assessment.

## 14. Source conflicts

If sources disagree:

```text
Tapetide says X
Yahoo says Y
Moneycontrol says Z
Official filing says W
```

TI must preserve each observation and provenance, create contradiction/conflict links, allow authoritative confirmation where applicable, and expose unresolved conflict downstream.

A materially important unresolved contradiction should remain visible or trigger enrichment/escalation.

## 15. Website sources

The future fabric should allow bounded website adapters for RBI, SEBI, NSE, BSE, company IR, Economic Times, Moneycontrol, Business Standard, Reuters, and other reputable sources.

Constraints:

- configuration-driven
- read-only
- bounded fetch/discovery
- domain validation
- no anti-bot bypass
- no CAPTCHA circumvention
- no general web crawler
- no uncontrolled site-wide scraping
- preserve source URL/acquisition time
- respect access constraints

## 16. Financial-media role

Economic Times, Moneycontrol and similar sites can be valuable for:

- breaking news
- interviews
- management comments
- broker/analyst views
- market sentiment
- sector trends
- policy interpretation
- event discovery

But they should generally not replace NSE/BSE filings, company IR, RBI/SEBI/government sources when those authoritative sources exist.

## 17. OpenAI research role

A future OpenAI research/search adapter may help with:

- missing context
- customer/supplier relationships
- policy/regulatory context
- international developments
- competitive changes
- causal investigation
- finding sources not covered by structured providers
- cross-domain synthesis

It must still feed normalized evidence into TI and must not become an untraceable shortcut around evidence contracts.

## 18. Provider-neutrality invariant

The future source/citation fabric must not depend on Tapetide-, Yahoo-, MCP-, NSE/BSE-, or website-specific raw response types.

Canonical claim/evidence/source references must remain stable if providers change.

## 19. Point-in-time and replay

Where timing matters, preserve:

- publication time
- event time
- acquisition time
- availability time
- revision/correction timing
- content fingerprint
- source version where possible

A replayed conclusion should reconstruct which evidence was available without live re-fetching when evidence was already persisted.

## 20. Cost / latency / source-use policy

Multi-source capability remains cost-aware.

Potential routing factors:

- economic materiality
- source cost
- provider quota
- expected information gain
- latency
- freshness
- current evidence coverage
- contradiction severity
- active-position impact

Do not fan out merely because sources exist.

## 21. Relationship to Evidence Graph

The citation fabric should reference the existing sparse Evidence Graph, not create a second graph system.

Evidence Graph = material relationships/research memory.  
Citation Fabric = maps claims/conclusions to relevant evidence/source refs for audit/reporting.

## 22. Relationship to Market Intelligence Journal

The Market Intelligence Journal should remain the chronological append-only record of meaningful events/evidence.

The citation layer may project journal/evidence records into human-readable report sources.

XLSX or other exports remain projections, not authoritative storage.

## 23. Relationship to A4 / A7

A4 may use source quality, contradictions and confirmation state during challenge/arbitration.

A7 may later evaluate provider/source reliability and predictive usefulness.

Source identity/provenance should remain historically available for both.

## 24. Future acceptance principle

> **Every material factual conclusion in a user-facing TI report can be traced to at least one evidence/source reference, unless the conclusion is explicitly an inference or hypothesis.**

For inference/hypothesis, supporting factual evidence must remain traceable and epistemic category explicit.

## 25. Deferred design questions

Revisit after A3 completion:

- exact `SourceRef` contract
- exact `ClaimCitation` contract
- citation numbering/rendering
- CLI rendering
- Web UI rendering
- expanded audit view
- source-selection algorithm
- website adapter framework
- media-source allowlist/config
- OpenAI research adapter
- source independence/lineage scoring
- persistence strategy
- report source compression
- citation handling for multi-document deep research
- citation handling for forecast outputs
- historical provider reliability evaluation

## 26. Explicit non-goals now

Do NOT implement now:

- website adapters
- Economic Times/Moneycontrol integration
- OpenAI research adapter
- report citation rendering
- citation ranking
- source scoring
- full source registry redesign
- A4/A7 integration

This note preserves remaining UX/adapter hypotheses. The promoted semantic design
is authoritative for future A4 admission, but no runtime was implemented by it.

## 27. Planned revisit sequence

1. A3 is frozen and pass 1 has settled the TI_CORE/capability boundary.
2. Pass 2 has approved source authority/provenance/contradiction semantics.
3. Next: **Post-A3 Deep Architecture Pass 3 — A4 Challenge / Arbitration /
   Higher-Intelligence Agent Architecture**.
4. Implement and accept the bounded source-comparability/input-projection
   foundation before A4 runtime work; it is not a prerequisite for pass 3 design.
5. Citation numbering, compression, hyperlinks, bibliography and CLI/Web report
   presentation remain DEF-054. New website/media/model adapters require their
   own scope/access/retention/budget decisions and are not authorized here.

## 28. Success criterion

The future system should make TI reports both easy to read and deeply auditable.

The user should be able to ask:

> **“Why did TI say this?”**

and TI should answer with the relevant evidence and source chain without exposing unnecessary internal complexity.
