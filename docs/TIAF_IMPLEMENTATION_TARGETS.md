# TIAF Detailed Implementation Targets

This document is the detailed, evolving engineering continuation map beneath
the stable project roadmap. Status must describe repository reality.

- `MILESTONES.md` is the concise status view.
- `TRADINGINTELLIGENCE_ROADMAP.md` is the canonical major roadmap.
- `TIAF_IMPLEMENTATION_TARGETS.md` is the detailed evolving engineering
  continuation map.

## Accepted foundation

### TIAF_TGT0 — Complete / Frozen

- Purpose: establish the Python repository, package layout, configuration,
  documentation, and quality tooling.
- Acceptance: importable baseline with passing compile, test, lint, type, and
  diff checks.
- Tag: `tiaf-tgt0`.

### TIAF_A0 — Complete / Frozen

- Purpose: establish immutable versioned domain contracts, shared enums,
  identifiers, evidence and assessment language, and Asia/Kolkata time policy.
- Acceptance: strict validated contracts with JSON round trips and immutable
  semantic collections.
- Tag: `tiaf-a0`.

### TIAF_A1.1 — Complete / Frozen

- Purpose: provider-neutral instrument, quote, OHLCV, historical-series,
  capability, normalization, and typed-error contracts.
- Acceptance: adapters can satisfy stable factual interfaces without leaking
  provider payloads.
- Tag: `tiaf-a1.1`.

### TIAF_A1.2 — Complete / Live Validated

- Purpose: direct read-only Dhan transport, full quotes, and daily/intraday
  historical OHLCV.
- Acceptance: deterministic mocked coverage plus successful live data
  validation with safe credentials.
- Tag: `tiaf-a1.2`.

### TIAF_A1.3 — Complete / Live Validated

- Purpose: Dhan active-expiry discovery and normalized complete live option
  chains with prices, depth, OI, volume, IV, and provider Greeks.
- Acceptance: provider-neutral immutable chains pass mocked validation and the
  read-only adapter is live-validated.
- Tag: `tiaf-a1.3`.

### TIAF_A1.4 — Current

- Purpose: provider-neutral rolling historical/expired-option data without
  expired contract IDs.
- Scope: Dhan rolling expiry and ATM-relative requests, complete factual arrays,
  endpoint-specific live-validated expiry codes (`1/2/3`), 30-day chunking,
  safe merging, typed failures, tests, and read-only smoke.
- Non-goals: replay engines, option choice, strategies, Agents, and execution.
- Dependency: accepted A1.1 contracts and A1.2 transport/mappings.
- Acceptance concept: long half-open date ranges become validated chronological
  historical-option series with no boundary gaps or silent array truncation.
- Live semantics note: older/general Dhan annexure values may show `0/1/2`, but
  the rolling expired-options endpoint is live-validated as `1/2/3`; A1.4 uses
  a dedicated type and does not change other expiry-code consumers.

## Planned near-term A1 decomposition

### TIAF_A1.5 — Zerodha secondary/fallback provider

- Purpose: introduce a second factual market-data source.
- Likely scope: adapter-specific authentication, supported quote/history
  capabilities, normalized mapping, and typed provider failures.
- Non-goals: automatic provider arbitration, cache policy, or trading APIs.
- Dependency: A1.1 provider contracts and established adapter boundaries.
- Acceptance concept: supported Zerodha facts normalize to the same public
  models under deterministic mocked tests and a safe validation path.

### TIAF_A1.6 — Instrument resolver

- Purpose: resolve provider-neutral identities to explicit provider IDs and
  derivative classifications.
- Likely scope: instrument-master ingestion, normalized lookup, ambiguity
  handling, and provider-ID attribution.
- Non-goals: ranking securities, choosing options, or fuzzy silent matches.
- Dependency: provider instrument sources and A1 identity contracts.
- Acceptance concept: representative equity, index, future, and option inputs
  resolve deterministically or return an explicit typed failure.

### TIAF_A1.7 — Cache, freshness, and provider scheduling

- Purpose: centralize reusable data acquisition and rate-aware coordination.
- Likely scope: keyed caches, caller-visible age/TTL, request coalescing, and
  endpoint-aware scheduling policies.
- Non-goals: Agent judgment, recommendation caching, or hidden adapter sleeps.
- Dependency: stable provider operations and normalized snapshot identities.
- Acceptance concept: repeated workloads reuse factual results while freshness,
  expiry, and provider rate constraints stay visible and deterministic.

### TIAF_A1.8 — AnalysisContext builder

- Purpose: assemble a timestamp-consistent provider-neutral factual context for
  downstream deterministic and Agent consumers.
- Likely scope: requested instruments, quotes, histories, derivatives evidence,
  provenance, quality, freshness, and missing-data visibility.
- Non-goals: scoring, recommendations, prompts, or execution authority.
- Dependency: resolution, caching, scheduling, and existing A1 models.
- Acceptance concept: a watchlist request yields one coherent immutable context
  or explicit missing/stale evidence.

### TIAF_A1.9 — Fallback and partial-data semantics

- Purpose: define deterministic behavior when providers fail or return
  incomplete facts.
- Likely scope: capability-aware fallback, provenance retention, conflict
  visibility, and stable partial/unavailable outcomes.
- Non-goals: blending facts by opaque judgment or concealing stale data.
- Dependency: at least two providers and shared Data Service context.
- Acceptance concept: simulated provider failures produce predictable fallback
  or explicit degradation without losing attribution.

### TIAF_A1.10 — News, filings, and external-evidence foundation

- Purpose: add normalized attributed event/text evidence for later analysis.
- Likely scope: source identity, publication/retrieval time, symbol association,
  deduplication, and freshness/quality metadata.
- Non-goals: sentiment recommendation, LLM conclusions, or automated actions.
- Dependency: common evidence contracts and shared acquisition boundaries.
- Acceptance concept: deterministic fixtures normalize and deduplicate evidence
  while preserving source, time, and missing-content status.

### TIAF_A1.11 — Fundamentals and macro evidence foundation

- Purpose: add structured attributed company and macroeconomic facts.
- Likely scope: provider-neutral observations, reporting periods, units,
  revisions, provenance, and freshness.
- Non-goals: valuation recommendations, forecasts, or portfolio construction.
- Dependency: evidence normalization conventions and provider integrations.
- Acceptance concept: representative observations round-trip with explicit
  period, unit, source, and revision semantics.

Major phases A2 through A10 remain defined only by the canonical
`TRADINGINTELLIGENCE_ROADMAP.md`; this continuation map does not replace or
invent detail for them.
