# TIAF_A1.7 — AnalysisContext Builder

## Purpose

`tiaf.context` is the first coherent factual analysis substrate. It combines
canonical identity, selected normalized market facts, retrieval freshness, quality,
availability, and A1.6 runtime provenance into one immutable
`AnalysisContext`.

AnalysisContext answers:

> What factual information do we currently know about this subject for this
> requested analysis?

It never answers what to trade.

## Architecture

`AnalysisContextBuilder` receives its resolver, market-data provider,
derivatives provider, historical-options provider, `DataFetchCoordinator`,
clock, freshness registry, and context-ID factory through dependency injection.
It imports or constructs no Dhan client. Resolution uses the A1.5 provider-
neutral interface; every factual provider operation goes through the A1.6
coordinator for cache, freshness, scheduling, coalescing, and stale-fallback
behavior.

The builder is synchronous and in-process. `build_many` is deliberately
sequential and returns one explicit completed-context, partial-context,
deferred, or error item for every input in the original order.

The layer boundaries are intentionally narrow:

- A1.6 answers: "May this provider request execute now?"
- A1.7 answers: "Can I build a truthful factual context now?"
- a future runtime/orchestrator will answer: "When should deferred analytical
  work be retried?"

`build_many` is not that future continuous-work scheduler and never sleeps or
retries implicitly.

## Requirements

`AnalysisContextRequirement` separates whether each evidence type is included
from whether it is required. Required evidence is automatically included.
This permits, for example, an optional requested option chain whose failure is
visible without making an otherwise complete context incomplete.

Every evidence descriptor makes that role explicit as `NOT_REQUESTED`,
`OPTIONAL_REQUESTED`, or `REQUIRED`, and also exposes the corresponding
`requested` and `required` booleans. `complete=True` means every `REQUIRED`
slot satisfied its policy; it does not mean all requested optional evidence
succeeded.

The caller supplies:

- factual purpose and optional trade-style/horizon labels;
- quote/history/derivatives/historical-options inclusion and requirement flags;
- explicit calendar-day history interval and lookback;
- explicit option-chain expiry;
- exact bounded rolling historical-option request specifications;
- explicit or centrally registered freshness requirements;
- partial and stale-on-error policy.

The generic builder has no default TTL, horizon conversion, trading-session
calendar, nearest-expiry selection, or automatic historical-option expansion.

## Evidence slots and provenance

Every standard slot is represented by an `EvidenceDescriptor`, including
`NOT_REQUESTED` slots. Status values are `AVAILABLE`, `PARTIAL`, `STALE`,
`MISSING`, `FAILED`, `DEFERRED`, and `NOT_REQUESTED`. Descriptors retain:

- explicit request role plus requested/required flags;
- normalized quality and retrieval freshness;
- source provider, source-observation time, and reception time;
- separate retrieval age and source-observation age;
- provider/cache/coalesced fetch disposition and cache-hit classification;
- explicit stale-fallback use;
- provider, operation, scheduler gate state, reason, and retry-after duration
  for a deferred acquisition;
- safe error type/detail.

Unknown exceptions receive a generic error detail so arbitrary exception text
cannot leak credentials. Common credential-like context metadata keys are
rejected. No raw Dhan payload is embedded.

`DEFERRED` means A1.6 rejected execution before a provider attempt. It carries
no factual quality or retrieval-freshness claim and is never rewritten as
`FAILED`, `MISSING`, or `UNAVAILABLE`. `FAILED` remains reserved for a real
provider/build attempt that failed. Instrument resolution errors remain typed
errors rather than either condition.

`retrieval_freshness` and `retrieval_age_seconds` describe acquisition/cache
recency. They are calculated from the coordinator timestamp, which uses the
normalized snapshot `received_at` for quote and option-chain retrievals. They
must not be interpreted as market recency.

`source_observed_at` and `observation_age_seconds` preserve the factual
object's observation timestamp where available. For a quote this can be an
older last-trade time even when an API response was fetched just now; the
builder never rewrites that old observation as current. No
`observation_freshness` classification is invented in A1.7 because deciding
whether the latest closed-market observation is acceptable requires a future
market-calendar-aware policy.

Dhan option-chain data provides no authoritative market-event timestamp in
this integration. Its normalized `observed_at` is therefore acquisition time,
and the descriptor declares
`option_chain_acquisition_time_no_authoritative_market_timestamp`. Historical
series keep their existing series retrieval timestamp and bar interval
semantics; A1.7 does not reinterpret them as quote-style last-trade times.

## Completeness and partial behavior

`complete=True` means every required included evidence slot is present and
acceptable under its explicit freshness and partial-data policy. It does not
mean every possible market fact was requested.

- optional missing or failed evidence never changes completeness;
- required `PARTIAL` evidence is acceptable only with `allow_partial=True`;
- explicitly bounded/allowed stale evidence can be complete but degraded;
- required missing/failed/unacceptable evidence makes a partial context
  incomplete when `allow_partial=True`;
- required failure or unacceptable result raises
  `RequiredEvidenceUnavailableError` when `allow_partial=False`;
- any scheduler deferral makes `build()` raise
  `AnalysisContextDeferredError`, retaining the partial context and exact gate
  details for the caller;
- resolution failure and missing freshness configuration are build errors.

## Deterministic quality aggregation

- `UNAVAILABLE`: required core quote or history is unacceptable/missing;
- `DEGRADED`: non-core required evidence is missing, or required evidence is
  stale/degraded;
- `PARTIAL`: required partial evidence was explicitly accepted, or requested
  optional evidence is partial, stale, missing, failed, or deferred; a retained
  partial context whose only missing required evidence is deferred is also
  `PARTIAL`, never `UNAVAILABLE`;
- `GOOD`: all required evidence is good/acceptable and requested optional
  evidence introduces no degradation.

Optional `NOT_REQUESTED` evidence has no quality effect.

## Deterministic retrieval-freshness aggregation

`AnalysisContext.overall_retrieval_freshness` aggregates only acquisition/cache
freshness for required evidence. It is not a claim that the underlying market
was recently observed. Only required evidence contributes:

- any required `STALE` evidence gives `STALE`;
- any required `DEFERRED` evidence gives `UNKNOWN`;
- otherwise any insufficient timestamp gives `UNKNOWN`;
- otherwise any required `AGING` evidence gives `AGING`;
- otherwise all observed required evidence gives `FRESH`;
- no timestamped required evidence gives `UNKNOWN`.

Missing and failed evidence remains explicit through status and completeness;
optional stale evidence never makes overall required retrieval freshness stale.

## Batch and scheduling semantics

`AnalysisContextBatchItem.status` is one of `COMPLETE_CONTEXT`,
`PARTIAL_CONTEXT`, `DEFERRED`, or `ERROR`. Provider scheduling blocks become
`DEFERRED` and preserve symbol, typed error, scheduler reason, provider,
operation, retry-after duration, gate state, and available correlation/context
identity. Any evidence acquired before the block remains in the retained
partial context. A required deferred slot makes that context incomplete and
its overall retrieval freshness `UNKNOWN`.

An actual provider failure can produce a `PARTIAL_CONTEXT` with a `FAILED`
evidence descriptor under partial mode. Instrument not-found or ambiguous
resolution produces `ERROR`. Neither is relabeled as `DEFERRED`. One item never
suppresses later symbols and input order is preserved.

## History and derivatives

Regular history uses aware `requested_at` as the end and subtracts the explicit
lookback as calendar days. No trading-session inference is performed.

Option-chain retrieval requires an explicit expiry. Historical-options
retrieval requires one or more exact interval, expiry flag/code, relative
strike, option type, and half-open date ranges. Each requested historical-
option series receives its own provenance descriptor.

## Summary and smoke utility

`summarize_context` returns only deterministic diagnostics: symbol, LTP, bar/
strike/series counts, expiry, aggregate quality/retrieval freshness, completeness,
missing evidence, and warnings. It has no direction, recommendation, or score.

Read-only examples:

```bash
python scripts/analysis_context_smoke.py \
  --symbol RELIANCE \
  --purpose RESEARCH \
  --history-interval 1d \
  --lookback-days 90

python scripts/analysis_context_smoke.py \
  --symbol RELIANCE \
  --purpose RESEARCH \
  --history-interval 1d \
  --lookback-days 90 \
  --include-derivatives \
  --expiry 2026-09-29 \
  --repeat

python scripts/analysis_context_smoke.py \
  --symbol RELIANCE \
  --optional-derivatives \
  --expiry 2026-09-29

python scripts/analysis_context_smoke.py \
  --symbols RELIANCE,HDFCBANK,KAYNES
```

On this acceptance surface, `--include-derivatives` means the option chain is
required. Use `--optional-derivatives` to request it without affecting
completeness if it fails. The output always prints Requested, Required, and
Status separately. Batch mode is sequential, retains input order, and prints
one explicit status for every supplied symbol. Deferred output prints the
scheduler reason, provider, operation, gate state, and retry duration; it does
not print `UNAVAILABLE` quality or `FRESH` retrieval freshness. The smoke CLI
does not sleep or retry deferred work and performs no ranking or scoring.

`--repeat` holds the explicit requested timestamp/range constant so the second
identical build demonstrates A1.6 cache provenance without changing the
factual request key.

## Future relationships and non-goals

A2 may compute deterministic features from this context. A3 Planners and
specialist Agents may consume it without independently calling factual
providers. A1.7 itself contains no indicators, scoring, ranking, direction,
option selection, recommendation, news, fundamentals, queue, background loop,
LLM/LangGraph, TradeMonitor, broker, account, order, or execution behavior.
