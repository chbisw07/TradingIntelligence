# TIAF_A3.5 News / Catalyst / Event Intelligence

## Status and boundary

**Status:** complete / accepted at `tiaf-a3.5`.
**Accepted base:** `tiaf-a3.4` at
`e0fdd056a4c056bd505d9f6b96620f4760de2981`.
**Contract, gateway, normalization, dedupe, policy, and specialist version:**
`1.0`.

A3.5 adds provider-neutral, point-in-time event evidence and a deterministic,
cited `NEWS_EVENT` specialist. It does not add unrestricted browsing, social or
rumor sentiment, forecasts, recommendations, position management, option
selection, broker authority, or A3.6 relative/sector/macro specialists.

## Architecture

```text
authorized filing/news source or normalized caller-owned data
        -> EventProvider
        -> PIT NormalizedEvent records
        -> conservative revision + event clustering
        -> controlled READ_NEWS / READ_FILINGS gateway
        -> AgentEvidencePack (one reference per source record)
        -> NewsEventSpecialist (one interpretation per cluster)
        -> AgentOpinionV2 + NewsEventAssessment
```

Acquisition and interpretation are separate. The specialist has no provider,
browser, arbitrary URL, HTTP, shell, broker, model SDK, or execution interface.
The generic gateway and Agent registries dispatch both components; there is no
event-specific runtime branch.

## Source/provider decision

Official exchange and regulator disclosures remain the preferred production
path. NSE exposes an official corporate-announcements surface with company,
subject, attachment, and broadcast timing, and says the displayed information
is company-uploaded and disseminated by the exchange. SEBI Regulation 30
materials establish the listed-entity material-event disclosure obligation.
BSE likewise publishes corporate filing surfaces and requires machine-readable
announcement documents. These are credible source surfaces, but this repository
has no accepted licensed API agreement, stable provider contract, credentials,
retention rights, or operational adapter for them.

A3.5 therefore does not scrape those sites or label an interactive web read as
a production feed. It implements `EventProvider` plus
`InMemoryEventProvider`, a deterministic read-only adapter for fixtures and
normalized records supplied by an authorized/licensed caller. A production
licensed exchange/news adapter and live reconciliation remain in existing
`DEF-012`; no duplicate deferral was created.

Reference surfaces evaluated on 2026-09-09:

- [NSE corporate filings announcements](https://www.nseindia.com/companies-listing/corporate-filings-announcements)
- [SEBI Regulation 30 material-event circular](https://www.sebi.gov.in/legal/circulars/jul-2023/disclosure-of-material-events-information-by-listed-entities-under-regulations-30-and-30a-of-securities-and-exchange-board-of-india-listing-obligations-and-disclosure-requirements-regulations-201-_73910.html)

## Event identity and structured facts

`NormalizedEvent` is one immutable source record. It preserves:

- stable event ID, broad family, and direction-neutral event type;
- exact primary entity and explicit related entities;
- source ID/class/publisher/provider/reference/document/revision marker;
- publication, event (when known), and acquisition timestamps;
- normalized bounded title, optional bounded excerpt, and content reference;
- typed scalar structured facts with unit/currency/locator/extraction version;
- independent relevance, materiality, novelty, status, quality, and freshness;
- optional underlying-event key, revision number, and superseded record ID.

Public contracts do not contain raw provider blobs or unbounded documents.
Collections are immutable tuples in Python and serialize as JSON arrays.
Contract timestamps reject naive values, accept aware values from any zone,
normalize to canonical `Asia/Kolkata`, and emit ISO-8601 `+05:30` JSON.

`StructuredEventFact` supports text, integer, finite number, boolean, and ISO
date values. Facts are source-supplied; no headline parser invents order value,
customer, earnings surprise, guidance, or completion status. An earnings
`BEAT`/`MISS` interpretation requires an explicit `earnings_context` fact that
already has a benchmark source upstream.

## Taxonomy: what happened, not what it means

The broad `EventFamily` taxonomy covers results, guidance, dividends,
buybacks, split/bonus, capital raise, M&A, orders, capex, management, promoter
ownership/pledge, regulatory, litigation, rating, product/expansion/customer,
supply-chain, sector/policy/macro/geopolitical, exchange filing, and `OTHER`.

`EventType` states the observed action, such as `ORDER_AWARDED`,
`GUIDANCE_CUT`, `REGULATORY_ACTION`, or `RESULTS_REPORTED`. It does not contain
`BULLISH` or `BEARISH`. `classify_explicit_action()` maps only declared source
action codes. Unrecognized or absent codes stay `OTHER`/`UNKNOWN`; attractive
headline tone is never a classification signal.

## Entity mapping and relevance

Entity links carry kind, canonical symbol when known, relation, and one of
`EXACT`, `EXPLICIT_RELATED`, or `UNRESOLVED`. The in-memory adapter builds an
exact per-symbol index from those links. It performs no fuzzy company-name
matching. A direct exact primary mapping is `DIRECT`; an explicitly related
symbol can be `HIGH`; unresolved identity remains `UNKNOWN`.

Relevance (`DIRECT` through `INCIDENTAL`/`UNKNOWN`) is separate from event
direction and materiality. A gateway request can impose a minimum relevance;
a large but incidental event does not pass merely because its magnitude is
large.

## Materiality, novelty, and source quality

Materiality is independently typed as `CRITICAL`, `HIGH`, `MODERATE`, `LOW`,
`IMMATERIAL`, or `UNKNOWN`. The optional generic size helper uses an explicitly
supplied company-relative percentage. It never labels a raw rupee amount
material without company scale and keeps missing scale `UNKNOWN`. The
specialist only forms a directional stance from moderate-or-stronger,
moderate-or-better relevant clusters; otherwise it can abstain.

Novelty is `NEW`, `UPDATE`, `REPEAT`, `DUPLICATE`, `CORRECTION`, or `UNKNOWN`.
Source classes are exchange/regulatory filing, company release, earnings
transcript, official government, trusted news, licensed aggregator, other, or
unknown. A category maps to a semantic primary/official/trusted-secondary
quality state for policy ordering, not a numerical truth probability.

## Deduplication, contradictions, and revisions

Clustering first uses an explicit underlying-event key. Without one, it uses a
conservative exact identity made from entity, family/type, event day, and
normalized title; a source document ID is used only within its source identity.
Similar wording alone does not merge unrelated events.

Each cluster retains every source record. The gateway emits one evidence
reference per record with cluster ID and active/superseded markers. The
specialist interprets the cluster once, so ten copies are not ten votes. It
still cites all active records and emits `NEWS_DUPLICATE` when multiple source
records are present.

Conflicting active structured facts remain in the cluster as named
`contradiction_fields`; equally active positive and negative event states also
remain mixed. Primary sources are preferred in quality assessment but do not
silently erase a conflicting report. `SOURCE_CONFLICT` and `CATALYST_MIXED`
make that uncertainty visible.

A correction must identify the exact prior event, preserve source/entity
identity, and increase revision number. The prior record remains serialized but
is marked superseded; only the visible current record drives the current
cluster direction. Ambiguous same-source revisions fail validation.

## Information-time semantics

`event_time`, `publication_time`, `acquisition_time`, and `decision_time`
(`EventRequest.as_of`) are distinct. At decision time `T`, a record is usable
only if both publication and acquisition occurred by `T`. The requested window
also ends no later than `T`.

Consequently, a later article cannot influence an earlier run, and a correction
visible tomorrow cannot rewrite yesterday's cluster. Replaying yesterday
selects the then-active record; replaying tomorrow retains both versions and
selects the correction. This is deterministic and covered directly by tests.

## Controlled gateways and cache/reuse

`EventEvidenceGateway` implements only `READ_NEWS` and `READ_FILINGS` with the
broad shared `EvidenceType.NEWS`. Source class preserves whether a record is a
filing. `READ_FILINGS` is restricted to exchange/regulatory filing classes;
`READ_NEWS` remains a bounded event read over caller-authorized normalized
sources. Requests contain subject, as-of/window, horizon, event families,
freshness, source classes, maximum clusters, relevance threshold, and explicit
normalization/dedupe versions. They contain no URL, headers, query language,
SQL, or credentials.

The accepted generic cache key includes subject, window/as-of, capability,
filters, source constraints, horizon, freshness, and normalization/dedupe
versions; gateway identity adds provider/version. Results expire after the
adapter validity interval. The in-memory adapter indexes by entity, clusters
before applying the maximum cluster count, and retains all records of every
selected cluster. A capped result records the total matching cluster count,
returns `PARTIAL`, and lowers coverage instead of appearing complete. This
supports bounded incremental NIFTY-500/~1000-equity use without repeated model
work. Persistent/distributed ingestion remains DEF-009.

## Specialist interpretation

`NewsEventSpecialist` has identity `NEWS_EVENT`, version `1.0`, and deterministic
low-cost operation. The A3.1 framework requires every specialist request to
retain `READ_A2_EVIDENCE` identity; beyond that inherited read-only requirement,
this specialist is authorized only for `READ_NEWS` and `READ_FILINGS`. It does
not inspect fundamental, technical, derivative, sector, macro, or forecast
facts and does not recompute A2/A3.3/A3.4.

`NewsEventAssessment` preserves per-cluster and aggregate:

- dominant family, direction, strength, and catalyst horizon;
- materiality, novelty, source quality, contradiction, and execution risk;
- all event IDs, active event IDs, and contradiction fields;
- evidence coverage, confidence basis, reason codes, and policy/version.

Direction comes from explicit event type/status and structured context, never
title wording. Results without explicit benchmark context remain neutral.
Announced capex/order/expansion can expose execution risk; delayed, cancelled,
or disputed status raises it. Long-lived capex/strategic events and immediate
regulatory/results events retain distinct catalyst horizons. Mixed material
clusters remain `MIXED` rather than being netted away. Requested horizon gates
directional synthesis: immediate/short/multi-horizon clusters inform DAY or
positional requests, while medium/long/multi-horizon clusters inform longer
requests. All clusters remain visible even when horizon-mismatched.

Allowed stances are `POSITIVE`, `NEGATIVE`, `NEUTRAL`, `MIXED`,
`INSUFFICIENT_EVIDENCE`, and `ABSTAIN`. None is a trade action. Low relevance,
immaterial evidence, or unknown scale can yield abstention. Missing usable
event evidence yields insufficient evidence.

Stable reason codes include primary filing, material positive/negative event,
order win/loss, earnings benchmark context, guidance change, capex/risk,
regulatory direction, rating change, duplicate, correction, source conflict,
stale/partial/immaterial/low-relevance evidence, and mixed catalyst state. A
code is emitted only when the corresponding structured evidence exists.

## Confidence, claims, and no-LLM operation

Policy confidence combines evidence coverage, source quality, explicit entity
relevance, freshness, cross-source consistency, and whether materiality has
support. It is evidence confidence—not the probability that price rises.
Self-reported and empirically calibrated confidence remain absent.

Every factual and interpretive claim cites active event evidence and its source
reference. The opinion contains no full document or title narrative. Prompt-like
text in a source title/excerpt is treated as inert evidence data and is never
copied into instructions or executed.

The complete A3.5 baseline uses zero LLM/model calls, zero input/output tokens,
zero model cost, and no model identity or prompt version. A future optional LLM
may summarize or extract difficult prose only after a controlled gateway has
retrieved explicit evidence, with structured-output validation and citations.
It may not browse freely or invent missing facts.

## Validation, limitations, and A3.6 boundary

Synthetic tests cover official positive/negative filings, duplicate articles,
primary plus secondary records, conflicting values, correction/update,
staleness, low relevance, material/immaterial orders, results/guidance context,
regulatory risk, mixed sets, insufficient evidence, future publication,
cross-source clustering, JSON/PIT/citation/security/runtime behavior, and a
1,000-record bounded input.

No production adapter was bound, so RELIANCE/HDFCBANK/KAYNES live reads and
manual live reconciliation were not performed. That is an explicit source and
licensing limitation, not synthetic live validation. The implemented fixture/
caller-data path is fully executable offline.

A3.6 may consume explicit event evidence for separately authorized relative,
sector, and macro context, but it must not move those interpretations into this
specialist or treat a company event as a sector/macro fact without explicit
entity mapping.
