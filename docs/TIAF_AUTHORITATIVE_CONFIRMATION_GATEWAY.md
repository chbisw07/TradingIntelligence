# TIAF Authoritative Confirmation Gateway

## Status and scope

**Status:** bounded implementation and live acceptance complete

**Placement:** bounded post-A3.6.1 follow-up before A3.7

**Purpose:** confirm materially important market-intelligence claims against
primary/original sources when available

This document defines the provider-neutral architecture for authoritative
confirmation from exchanges, regulators, company investor-relations sites, and
other official publishers. Initial implementation candidates are NSE, BSE, and
company IR sources. Their names and transports are adapter concerns, not domain
contracts.

The implementation adds immutable confirmation/document contracts, explicit
source/domain validation, deterministic materiality policy, configured
read-only NSE/BSE/company-IR adapters, bounded HTTP retrieval, content-addressed
cache, a plain-text/HTML parser boundary, conservative normalization, event and
evidence-graph integration, and exact offline replay. It adds no crawler,
browser automation, model call, specialist, recommendation, or trading behavior
and does not reopen A3.6.1 or begin A3.7.

The bounded live record is
[`STUDY_Authoritative_Confirmation_Gateway_Live_Acceptance.md`](STUDY_Authoritative_Confirmation_Gateway_Live_Acceptance.md).

## Architectural invariant

Authoritative confirmation remains behind the existing
`tiaf.market_intelligence` contracts and A3.2 authority/budget gateways.
Downstream contracts and specialists consume canonical evidence, normalized
events, evidence references, contradictions, and confirmation records. They do
not know which exchange, regulator, company site, transport, or parser supplied
the source.

No specialist or domain package may import or receive:

- exchange-specific clients, endpoints, cookies, or response schemas;
- browser automation or anti-bot handling;
- HTTP client implementations;
- provider-specific HTML/PDF parsers;
- credentials or login/session objects; or
- raw provider payloads.

Provider substitution must remain registry, adapter, normalizer, route-policy,
and configuration work. MCP is neither required nor assumed.

## Existing contracts reused

| Existing seam | Authoritative use |
|---|---|
| `AgentCapability` | Existing coarse authorization ceiling; primarily `READ_FILINGS` and, where explicitly justified, `READ_FUNDAMENTALS` |
| `MarketIntelligenceCapability` | Stable semantic request; no exchange-specific capability names |
| `MarketIntelligenceProvider` | Read-only adapter contract for source discovery/acquisition |
| `ProviderManifest` | Declares support, authority, output type, cost, freshness, PIT, and limitations |
| `SourceAuthority` | Qualitative trust class; no artificial numeric authority score |
| `CapabilityRoutePolicy` | Bounded source selection, call/cost/time ceilings, and authoritative provider set |
| `ProviderNativeObservation` | Preserves native fields, timestamps, source reference, checksum, and provider provenance |
| `NormalizationRecord` | Audits every accepted, provider-defined, or ambiguous mapping |
| `CanonicalEvidenceProjection` / `FundamentalFact` | Emits only facts with explicit compatible semantics |
| `NormalizedEvent` / `EventCluster` | Represents disclosures and clusters multiple reports of one real-world event |
| `ContradictionGroup` | Retains disagreements and may identify authority-based resolution without deleting inputs |
| `MarketIntelligenceRun` | Immutable serialization, fingerprinting, and offline replay |
| A3.2 budget/reasoning gateways | Enforces bounded acquisition and optional model use |

`RoutingMode.AUTHORITATIVE_CONFIRMATION` already expresses the route intent.
Implementation may need a materiality trigger and claim-confirmation contracts,
but must not create a second routing framework.

## Governing flow

```text
discovery evidence and material claim
        -> deterministic materiality/escalation policy
        -> authorized AUTHORITATIVE_CONFIRMATION route
        -> official-source registry and adapter selection
        -> bounded reference discovery
        -> source/domain validation
        -> document acquisition and content fingerprint
        -> deterministic parse/extract where possible
        -> native observation preservation
        -> conservative canonical normalization
        -> claim-confirmation record
        -> existing event cluster / contradiction journal / evidence graph
        -> immutable replay artifact
```

The authoritative gateway confirms evidence; it does not produce a trading
judgment or arbitrate specialist opinions.

## Routing roles

The existing modes retain distinct meanings:

- `PRIMARY_WITH_FALLBACK`: a structured source is attempted first. An official
  source may fulfill the semantic capability directly only after a configured
  typed fallback condition. A fallback result is labelled with its actual source.
- `AUTHORITATIVE_CONFIRMATION`: discovery evidence and a material claim already
  exist. The gateway seeks primary evidence and emits an explicit confirmation
  outcome linked to the original claim.
- `MULTI_SOURCE`: structured and authoritative observations are both retained.
  Authority may resolve a factual conflict, but never erases the lower-quality
  observation or makes correlated copies independent votes.

Authoritative confirmation is not mandatory for every fact. Provider order,
eligible authorities, fallback statuses, maximum calls, cost, elapsed time, and
stop conditions remain versioned policy rather than code branches.

## Source-quality hierarchy

The existing qualitative `SourceAuthority` is sufficient. No numeric score is
introduced. Within a route, deterministic source preference is:

1. exchange/regulator filing or its verified official mirror —
   `AUTHORITATIVE`;
2. company investor-relations publication on a validated official domain —
   `AUTHORITATIVE` or `PRIMARY` according to document provenance;
3. official credit-rating agency or company-hosted rating disclosure —
   `PRIMARY`;
4. structured provider record carrying a verified original-source reference —
   normally `TRUSTED_SECONDARY`, with the linked original independently acquired
   before it is treated as authoritative;
5. secondary media/news — `TRUSTED_SECONDARY`; and
6. aggregator/repost — `AGGREGATOR`.

An implementation may add a provider-neutral `OfficialSourceKind` solely to
distinguish `EXCHANGE_OR_REGULATOR`, `COMPANY_IR`, and
`OFFICIAL_RATING_DISCLOSURE`. It must not duplicate the trust hierarchy or
contain names such as NSE/BSE. Source authenticity and source authority are
separate: a URL is not authoritative merely because an adapter expected it.

## Authoritative document evidence

Avoid ten nearly identical public model classes. Prefer one immutable
`AuthoritativeDocumentEvidence` envelope with a stable document-kind enum and
typed extracted facts. Add a specialized subtype only if it has distinct
validation semantics that cannot be expressed safely by the envelope.

The envelope should preserve:

- evidence/document ID and canonical company/instrument identity;
- `SourceAuthority` and provider-neutral official source kind;
- provider ID and provider-local exchange/source metadata;
- document kind and title;
- publication timestamp, exchange timestamp when supplied, effective/event
  date when distinct, acquisition timestamp, and point-in-time availability;
- canonical source URL/reference and filing/reference number when supplied;
- reporting period, quarter, FY, standalone/consolidated basis, audit status,
  units, and currency when applicable;
- raw-content SHA-256 and immutable content reference when bytes are retained;
- parser/extractor identity and version;
- parsed facts with page/section/table/record locators;
- revision/correction identity plus `supersedes`/`superseded_by` links when
  known; and
- complete provider and normalization provenance.

All timestamps remain timezone-aware and normalize through the canonical TIAF
`Asia/Kolkata` policy. Publication date alone must not be fabricated into an
exact publication time; its availability basis remains explicit.

The document-kind vocabulary must cover:

- filing document;
- corporate announcement;
- financial result;
- investor presentation;
- earnings-call document/transcript;
- annual report;
- corporate action;
- governance disclosure;
- regulatory disclosure;
- credit-rating disclosure; and
- IPO DRHP, RHP, or final prospectus.

Event-bearing documents also produce or enrich existing `NormalizedEvent`
records. Explicit scalar facts reuse `StructuredEventFact`,
`CanonicalEvidenceProjection`, or `FundamentalFact` according to meaning. The
document remains the traceable source; extracted facts never replace it.

## Claim-confirmation model

Implementation should add immutable, provider-neutral contracts with these
roles:

### `DiscoveredClaim`

- claim ID, canonical subject, claim/event type, asserted facts, and materiality;
- originating evidence IDs and event-cluster ID when applicable;
- claim publication/availability and creation timestamps; and
- explicit scope: fields to confirm, period/event date, and source limitations.

### `AuthoritativeConfirmationRequest`

- request ID, discovered claim ID, semantic capability, as-of time, and horizon;
- allowed coarse authorities and eligible official-source kinds;
- required fields and acceptable document kinds;
- escalation reasons and materiality class; and
- existing tool/cost/latency budget.

### `ClaimConfirmationRecord`

- confirmation ID and original claim/evidence IDs;
- authoritative document/evidence IDs;
- one status from `CONFIRMED`, `PARTIALLY_CONFIRMED`, `CONTRADICTED`,
  `NOT_FOUND`, `OUT_OF_COVERAGE`, `UNAVAILABLE`, or `AMBIGUOUS`;
- field-level confirmed facts and unresolved differences;
- source authority and confirmation timestamp;
- evidence quality/confidence basis and typed reason codes;
- route/audit references and policy version; and
- a semantic fingerprint suitable for offline reconstruction.

`NOT_FOUND` means the bounded, valid search completed without locating matching
authoritative evidence as of the request time. It does not mean the claim is
false. `UNAVAILABLE` means the source/document could not be accessed.
`CONTRADICTED` requires explicit authoritative evidence inconsistent with a
claim. `AMBIGUOUS` preserves incompatible semantics or uncertain document
identity. `OUT_OF_COVERAGE` means the configured official sources do not cover
the subject/capability.

Confirmation is field-level where necessary. A document may confirm the event
date but leave amount or customer identity unresolved, yielding
`PARTIALLY_CONFIRMED`. This is evidence reconciliation, not A4 arbitration.

## Materiality-driven escalation

A deterministic, versioned `AuthoritativeEscalationPolicy` should authorize a
confirmation route when at least one configured trigger applies:

- high-materiality catalyst or risk;
- active-position impact;
- material discrepancy between providers;
- conflict in a major financial metric;
- corporate action;
- regulatory, legal, or governance event;
- earnings/result publication;
- IPO subscription research;
- management change; or
- major order, capex, merger/acquisition, fund raising, promoter transaction,
  or credit-rating change.

The decision record preserves trigger IDs, materiality, expected evidence value,
budget impact, selected capability, and stop reason. Routine quotes, minor
headlines, and every ordinary metric do not trigger confirmation. The policy
reuses A3.6.1 progressive enrichment and A3.2 budgets; it does not create an
unbounded research loop.

## Gateway and adapter boundary

```text
AuthoritativeConfirmationGateway
    -> MarketIntelligenceRegistry / MarketIntelligenceRouter
        -> NSE official-source adapter
        -> BSE official-source adapter
        -> company-IR adapter
        -> future SEBI/regulator/licensed adapter
```

The gateway owns confirmation request validation, escalation-policy evaluation,
route execution, field reconciliation, and confirmation-record assembly. Each
adapter remains a read-only `MarketIntelligenceProvider` with an injected,
transport-specific client beneath the protocol. Adapters may use official
REST/JSON, direct document URLs, bounded HTML discovery, a controlled browser,
or a future licensed feed. None of those choices changes the gateway contract.

NSE/BSE identity mapping is explicit and effective-time aware. A company-IR
adapter starts from a known profile/filing URL when possible, validates the
official domain, performs bounded discovery only for the requested document,
and never crawls the whole site. Redirect chains and the final domain are
recorded and validated. Failure to establish official ownership yields
`AMBIGUOUS`, `NOT_FOUND`, or `UNAVAILABLE`; it never yields invented evidence.

## Document pipeline

```text
source reference
    -> validate scheme/domain/source ownership
    -> bounded fetch
    -> record retrieval metadata and timestamps
    -> hash exact bytes
    -> immutable content-addressed cache
    -> classify document/version
    -> deterministic parse/extract
    -> optional controlled OCR or model-assisted extraction
    -> preserve native observations
    -> conservative canonical normalization
    -> event/confirmation/journal integration
```

Raw content remains traceable when retention and source terms permit it. Where
content cannot be retained, preserve its source reference, retrieval metadata,
and provider-supplied fingerprint without pretending replay contains the bytes.
Parsing failure is a typed failure, never `fact=false`.

Extracted facts cite page, section, table, row, or provider record whenever
available. Parsers preserve labels, units, scale, currency, periods, statement
basis, and table structure. OCR is off by default and enabled only for a
specific unsupported text layer under explicit budget/policy. OCR/model output
is labelled extraction/inference and cannot upgrade source truth.

Corrections and revisions are appended and linked. They never overwrite the
prior document or make revised facts visible before their actual availability.

## Cache, deduplication, and replay

- Raw cache key: SHA-256 of exact document bytes.
- Retrieval record: requested URL, validated final URL/domain, acquisition time,
  response metadata, and content hash.
- Parsed cache key: content hash plus parser/extractor ID and version.
- Confirmation fingerprint: request, policy, document/evidence IDs, field-level
  outcomes, reason codes, and relevant run fingerprints.
- Revalidation policy: source/document-kind freshness plus explicit conditional
  retrieval metadata where supported.

Content-identical NSE, BSE, and company-hosted copies share one content node but
retain separate retrieval/provenance references. They do not count as three
independent confirmations. Different hashes are not assumed contradictory:
revision markers, publication times, and correction links are checked first.

Offline replay reconstructs the document metadata, parsed facts, event-cluster
links, and confirmation record without transport access. Persistent/distributed
cache operations remain governed by DEF-009; the first implementation may use a
bounded local deterministic store.

## Financial confirmation semantics

Official financial facts become canonical only when the document explicitly
supports the accounting meaning. Required context includes the native label,
period, reporting basis, units/scale, currency, audited/provisional status, and
source locator.

Mappings such as Revenue from Operations, Total Income, PAT, EBITDA, Gross Debt,
and Cash Flow from Operations require named, versioned rules per explicit source
label and statement context. Generic provider-defined `revenue`, `sales`,
`borrowings`, or similar labels are retained as native/ambiguous unless the
authoritative document resolves their meaning. Derived EBITDA or debt must not
be presented as reported unless the source reports that exact metric.

Authority resolves provenance quality, not semantic mismatch. A highly
authoritative but differently scoped metric does not silently replace a lower
authority metric with another definition.

## Event journal integration

One underlying event can have Tapetide, Yahoo, NSE, BSE, and company-IR records.
Existing `EventCluster` identity and revision rules remain authoritative. The
official filing enriches the cluster and source-quality evidence; it does not
increment economic-event count.

The journal retains every evidence reference, correlated-source lineage,
publication/availability time, field disagreement, and correction. A
confirmation record links to the cluster and original discovery evidence.
Contradictions remain visible even when authority resolves a field for a
specific as-of view.

## IPO support

The generic document envelope supports DRHP, RHP, and prospectus identity,
version, filing/reference number, source, hash, dates, and revision lineage.
Typed extracted facts can later represent issue structure, fresh issue versus
OFS, use of proceeds, promoter/shareholder details, financial statements, risk
factors, litigation, disclosed peer valuation, anchor-book references, and issue
dates with page/section citations.

This gateway only acquires, identifies, preserves, and normalizes source
evidence. IPO scoring, valuation judgment, subscription advice, allocation, and
forecast probability are explicit non-goals.

## Failure semantics

Provider acquisition continues to use `ProviderResultStatus` and
`ProviderFailure`. The implementation pass should add only genuinely missing,
provider-neutral failure kinds, likely:

- `DOCUMENT_UNAVAILABLE`;
- `ACCESS_DENIED` for policy-compliant anti-bot/access refusal;
- `UNSUPPORTED_DOCUMENT_TYPE`;
- `AMBIGUOUS_SOURCE_AUTHENTICITY`;
- `MISSING_CANONICAL_IDENTITY`;
- `PARSE_FAILURE`; and
- `SUPERSEDED_DOCUMENT` when a stale filing was specifically requested.

Existing `NETWORK`, `TIMEOUT`, `MALFORMED_PAYLOAD`, `PROVIDER_UNAVAILABLE`,
`OUT_OF_COVERAGE`, `UNAUTHORIZED`, and `BUDGET_EXCEEDED` remain reusable.
Confirmation status and provider-call status are separate. No secondary source
may be relabelled authoritative after an official-source failure.

## Security and compliance

- Read-only retrieval only; no submission, mutation, trading, or broker action.
- No login automation unless a later source contract explicitly authorizes it.
- No CAPTCHA circumvention, credential harvesting, anti-bot bypass, or rate-limit
  evasion.
- Exact adapter allowlists for hosts, operations, redirects, document size,
  MIME types, and call counts.
- HTTPS by default; official-domain registry and redirect validation before
  content is trusted.
- No arbitrary URL supplied directly by an Agent or model.
- Bounded document size, parser resources, archive depth, and content types.
- Credentials, cookies, raw headers, and sensitive diagnostics never enter
  evidence, logs, prompts, or replay artifacts.
- Source terms, robots/access limits, licensing, and retention restrictions are
  policy inputs, not bypass targets.

## Optional LLM extraction

Deterministic extraction is preferred. When it is insufficient, a model may
identify sections, extract candidate facts, summarize cited risks, or compare
versions only through the existing A3.2 reasoning/budget gateway.

Model output is labelled `INFERENCE` or versioned `EXTRACTION`; the original
document remains authoritative. Every extracted fact requires a document ID and
locator. Schema validation, token/tool/cost ceilings, no-LLM mode, and full audit
remain mandatory. No calibrated probability or forecast is produced here.

## Acceptance scenarios

1. **Order win:** discovery claim links to an official filing; amount, customer
   where disclosed, and effective date are field-level confirmed; one event
   cluster is enriched.
2. **Financial result:** disagreeing provider observations remain; an official
   result resolves only explicitly compatible metric semantics and periods.
3. **Corporate action:** exchange evidence confirms or contradicts the claimed
   split, bonus, or dividend terms without adjusting price history in this layer.
4. **Management change:** an official filing confirms role and effective date;
   an undated secondary headline cannot supply either.
5. **IPO:** DRHP/RHP/prospectus identity, hash, provenance, dates, and revisions
   survive normalization and offline replay.
6. **Not found:** bounded official discovery completes without a matching filing;
   status is `NOT_FOUND`, never false or contradicted.

## Required implementation tests

- Provider substitution leaves confirmation/domain contracts unchanged.
- Source authority and official-source-kind classification are deterministic.
- Host, redirect, and official-domain validation reject lookalike domains.
- Claim, source evidence, document, event cluster, and confirmation links round-trip.
- `NOT_FOUND`, `UNAVAILABLE`, `OUT_OF_COVERAGE`, `AMBIGUOUS`, and
  `CONTRADICTED` remain distinct.
- Lower-quality conflicting evidence remains after authoritative resolution.
- Document byte hash, parsed-output key, confirmation fingerprint, and offline
  replay are exact.
- Content-identical exchange/company copies deduplicate content but preserve
  each provenance path.
- Corrections supersede rather than overwrite and obey point-in-time visibility.
- Low-materiality evidence does not invoke an authoritative adapter.
- Budgets stop calls/downloads/parsing deterministically.
- No provider/browser/HTTP/parser import appears in specialists or canonical
  domain packages.
- Provider-defined financial labels cannot emit fabricated canonical metrics.
- IPO documents preserve type/version/reference/hash and required provenance.
- Malformed, oversized, unsupported, denied, and parse-failing documents produce
  typed failures.
- Cache reuse performs no transport call and retains original acquisition truth.
- Full repository regression, compile, lint, typing, diff, and architecture
  security checks pass.

## Internal implementation work packages

1. Authoritative document, discovered-claim, confirmation-status, request, and
   confirmation-record contracts.
2. Official-source registry, qualitative authority classification,
   official-domain policy, and deterministic materiality escalation.
3. Read-only NSE and BSE adapters behind existing provider/normalizer protocols.
4. Bounded company-IR reference discovery, domain validation, and retrieval.
5. Content fingerprint, immutable local cache, parser/extractor boundary, and
   replay records.
6. Conservative fact normalization plus event-cluster, contradiction-journal,
   and evidence-graph integration.
7. Bounded representative live acceptance with sanitized evidence and no
   mutation/login/bypass behavior.
8. Failure, security, deduplication, revision, replay, and full-regression
   hardening.

These are internal packages within one bounded post-A3.6.1 follow-up. They do
not create another permanent major milestone or renumber A3.7.

## Risks and deferred decisions

- NSE/BSE access mechanisms, terms, rate limits, anti-bot behavior, schemas, and
  document retention permissions require live/legal validation before adapter
  selection.
- Company official-domain ownership and heterogeneous IR publication patterns
  require conservative registry/discovery policy; a universal crawler is rejected.
- PDF tables, scanned documents, mixed scripts, and malformed source files may
  need format-specific deterministic parsers or bounded OCR.
- Filing mirrors and cross-posted documents may share or diverge in content;
  identity and revision cannot rely on URL/title alone.
- Exact historical availability may be absent and remains limited by DEF-049.
- Distributed/durable cache, queues, retries, and operational telemetry remain
  under DEF-009/DEF-010 rather than entering the first implementation.
- Corporate-action acquisition can progress under DEF-013, but adjusted-price
  history policy remains a separate design and is not solved by confirmation.
- Source licensing, compliance review, production monitoring, and provider
  health remain prerequisites for operational deployment.

## Non-goals

No full exchange market-data replacement, generic crawler/search engine, broad
news aggregation, recommendation/scoring engine, A4 arbitration, A5 position
management, A6 option expression, A7 forecasting, A8 integration, A9 scanning,
A10 scheduling, broker action, or production login automation belongs here.

## Next implementation prompt

`TIAF_A3.6.1 FOLLOW-UP — AUTHORITATIVE CONFIRMATION CONTRACTS, SOURCE REGISTRY, AND MATERIALITY POLICY`
