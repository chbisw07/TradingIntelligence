# TIAF_A3.6.2 Market Intelligence / Deep Research Integration

## Status and scope

**Status:** implementation, deterministic acceptance, and bounded live acceptance
complete.

**Acceptance decision:** `READY_TO_ACCEPT_A3_6_2`.

**Implementation base:** authoritative-confirmation gateway commit `46f2fcf`.

**Live acceptance:** 2026-09-10T12:55:55.444215+05:30.

A3.6.2 closes the integration seam between the accepted A3.6.1 provider fabric
and structured company research. It adds no provider, provider-specific domain
contract, model call, forecast probability, trade expression, broker action,
LangGraph workflow, or source/citation UI architecture.

## Implemented flow

```text
MarketIntelligenceResearchRequest
    -> capability route policy
    -> bounded primary/secondary acquisition
    -> native-preserving normalization
    -> coverage / ambiguity / contradiction inspection
    -> optional authoritative confirmation of an explicit material claim
    -> sparse evidence-backed graph update
    -> DeepResearchContextPack
    -> deterministic structured research components/profile
    -> semantic fingerprint
    -> JSON persistence and provider-free replay
```

`DeepResearchIntegrationController` reuses
`MarketIntelligenceResearchController`, `MarketIntelligenceRouter`, and
`AuthoritativeConfirmationGateway`. `AuthoritativeConfirmationTask` is only an
explicit work item for an already identified material claim; it is not a new
provider or authority mechanism. A confirmation claim must link to evidence in
the acquisition run.

The immutable `DeepResearchContextPack` contains normalized canonical facts,
bounded ambiguous projections, normalization records, quality/freshness/PIT
envelopes, normalized events, contradiction groups, authoritative results,
research gaps, sparse graph neighborhood, prior provider-neutral opinions,
objective/horizon/depth, and authority/budget constraints. It has no raw native
observation or provider transport field.

The immutable `DeepResearchResult` retains the complete acquisition run,
context, research components, company profile, sparse graph, confirmation
results, zero-LLM usage, and a validated semantic fingerprint. Reconstructing
it with `model_validate_json` invokes no connector or provider.

## Deterministic research policy

The baseline produces direct `FACT` assertions only from accepted canonical
evidence or normalized event IDs. It does not synthesize unsupported prose.
`INFERENCE` must cite direct evidence or a `FACT` assertion and include explicit
reasoning. `HYPOTHESIS` must cite evidence or a `FACT`/`INFERENCE`, state its
assumptions, and state invalidation conditions. A `FACT` cannot cite another
assertion, which prevents silent category promotion.

Requested families without safely normalized evidence produce explicit
`ResearchGap` entries and an insufficient component. Ambiguous and
provider-defined fields remain visible in the context but do not become facts.
Contradictory canonical values both survive, retain the router's unresolved
contradiction group, and produce separate `UNCERTAIN` graph edges when the
conflict concerns a supported graph relationship. Values are never averaged or
resolved by last write.

The sector-safety baseline detects an explicitly evidenced bank/financial
services classification and withholds industrial interpretations such as
EBITDA, capacity, inventory, or operating-leverage conclusions. The underlying
canonical observation remains in context for audit; the deterministic output
records a sector-safety gap instead of deleting evidence.

## Sparse Evidence Graph

Only allow-listed, evidence-backed relationships are projected automatically:

- `company.sector` -> `BELONGS_TO_SECTOR`;
- `company.industry` -> `BELONGS_TO_INDUSTRY`; and
- normalized direct events -> `HAS_CATALYST`.

Each edge retains the canonical/event evidence ID, provider, source reference,
availability/acquisition times, quality, derivation, validity, status, and a
materiality field. The baseline uses a documented neutral `0.5` materiality for
profile classification edges; an event with unknown source materiality remains
`0.0` and is not silently upgraded. Duplicate semantic edges are deduplicated.
Ambiguous customer/supplier strings do not create relationships.

## Progressive enrichment and failures

The existing route policy remains authoritative:

- sufficient primary evidence stops fan-out;
- configured `RATE_LIMITED`, unavailable, and coverage failures may fall back;
- multi-source mode retains each independent provider observation;
- both-provider failure returns no fabricated evidence and typed gaps;
- unsupported dependencies remain research gaps; and
- official-source absence remains `NOT_FOUND`, `UNAVAILABLE`, or another typed
  state, never a false confirmation.

Deterministic tests cover primary-only sufficiency, primary failure with
secondary fallback, both-provider failure, agreement dedupe, material
multi-source contradiction, unsupported/ambiguous dependency abstention,
authoritative-result linkage, HDFCBANK sector safety, ATHERENERG sparse history,
epistemic enforcement, context isolation, zero model usage, and exact replay.
The pre-existing Yahoo routing suite separately proves Tapetide
`RATE_LIMITED`/unavailable fallback through the real Yahoo adapter contract.

## Live acceptance

The explicit path is:

```bash
.venv/bin/python scripts/deep_research_live_acceptance.py --live
```

It requires explicit `--live`, uses only existing read-only adapters, accepts
the project virtual environment's `uvx`, and is capped at 12 provider calls.
The final run used exactly 12 calls across RELIANCE, HDFCBANK, KAYNES, and
ATHERENERG. Tapetide MCP reported version 1.0.0 and Yahoo Finance MCP reported
version 4.0.3.

All four cases returned honest `PARTIAL` research profiles because conservative
native ambiguity/gaps were retained. Each produced canonical evidence and two
evidence-backed profile graph edges. RELIANCE used Tapetide and Yahoo and made
one company-IR authoritative attempt. The configured annual-report index was
not available at that path and therefore returned `NOT_FOUND`; this is an
accepted typed result, not confirmation. Every complete result replayed exactly
after live acquisition with the same evidence, gaps, graph, confirmation state,
and semantic fingerprint. LLM calls, input tokens, and output tokens were zero.

The detailed run evidence is in
[`STUDY_A3_6_2_Deep_Research_Live_Acceptance.md`](STUDY_A3_6_2_Deep_Research_Live_Acceptance.md).

## Boundaries retained

- Provider and MCP imports remain in provider modules and explicit scripts.
- Specialists and domain contracts do not import Yahoo, Tapetide, NSE, BSE,
  company IR, MCP, or HTTP parser implementations.
- Provider-native evidence is retained in acquisition runs but excluded from
  synthesis context.
- No provider-specific ticker reaches the canonical subject.
- No model-generated statement becomes a fact.
- No probability, target, strike, expiry, option side, position action, or
  broker operation is produced.
- Durable graph storage, full citation/report UI, exhaustive dependency data,
  A3.7+, A4, and A7 remain deferred.
