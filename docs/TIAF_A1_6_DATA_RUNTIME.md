# TIAF_A1.6 — Cache, Freshness & Provider Scheduling

## Purpose

A1.6 is the synchronous, in-process factual data runtime between consumers and
provider adapters. It decides whether a cached fact meets the caller's freshness
requirement and whether a new provider request may run now. It adds no trading
judgment, background service, distributed state, or persistence.

> A1.6 decides: **Should/factually may I fetch this data now?**
>
> A future Intelligence OS decides: **What should TIAF analyze next?**

Those are different architectural layers.

## Cache architecture

`CacheBackend` is provider-neutral. `InMemoryCacheBackend` is a thread-safe
implementation with optional bounded LRU eviction. Cache entries are immutable
containers; the cache does not mutate their factual values. Overwriting a key
increments its generation. Explicit invalidation is available by key,
namespace, or instrument identity.

The A1.5 Dhan instrument-master file cache remains separate. It is long-lived
provider reference data with download and atomic-file semantics. The A1.6 cache
is an in-memory request-result cache. A future persistent cache may unify some
mechanics, but A1.6 does not force the master CSV into memory-only storage.

## CacheKey semantics

`CacheKey` describes what factual data is cached:

- normalized namespace and operation;
- optional normalized provider;
- optional stable instrument identity;
- sorted string parameter pairs;
- contract schema version `1.0`.

It is immutable, hashable, deterministic in JSON and log strings, and rejects
common credential-bearing parameter names. Callers must use factual identifiers,
not Python object identity. Secrets never belong in cache keys.

## Caller-relative freshness

`FreshnessRequirement` supplies fresh, aging, and maximum-stale age boundaries.
`classify_entry_freshness` returns the existing `FRESH`, `AGING`, `STALE`, or
`UNKNOWN` state. Provider `observed_at` is preferred. `stored_at` is used only
when a caller explicitly enables `use_stored_at_if_observed_missing`; otherwise
a missing observation time remains `UNKNOWN`.

The generic `FreshnessPolicyRegistry` deliberately starts empty. Operations
such as `quote`, `historical`, `option_expiries`, `option_chain`,
`historical_options`, and `instrument_master` can receive explicit defaults,
while each consumer may override them. No universal TTL or horizon-to-seconds
rule is encoded. All wall-clock timestamps are aware and normalized to the
canonical TIAF timezone, `Asia/Kolkata`.

## Provider policies and gate

`RatePolicy` can express minimum spacing, a rolling request window, or both,
scoped by provider, operation, or request key. `ProviderScheduler` atomically
checks and reserves capacity with monotonic time. It returns a
`ProviderGateDecision`; a blocked coordinator call raises
`ProviderScheduleBlockedError` with state, reason, and retry timing. The gate
never calls `sleep`.

Providers can also be manually disabled and re-enabled. Acceptable cached facts
remain usable while a provider is disabled. A recorded provider rate-limit can
establish an explicit monotonic cooldown for future calls.

### Dhan policies

Dhan rules live in `tiaf.data.providers.dhan.rate_policies`, outside the generic
runtime:

- `quote`: minimum one-second spacing per quote operation, based on Dhan's
  [Market Quote documentation](https://dhanhq.co/docs/v2/market-quote/);
- `option_chain`: minimum three-second spacing per unique request key, based on
  Dhan's [Option Chain documentation](https://dhanhq.co/docs/v2/option-chain/).

No historical-data restriction is registered in A1.6. Dhan publishes broader
category/day limits, but A1.6 does not invent an endpoint rule or pretend that a
category limit is an exact historical-operation policy.

## Fetch coordination and single flight

`DataFetchCoordinator.get_or_fetch` performs this synchronous sequence:

1. inspect and classify a cached entry;
2. return it only if the caller accepts its state;
3. join an identical in-flight `CacheKey`, if present;
4. atomically reserve provider capacity;
5. execute the provider callback once and store its result;
6. return an immutable `FetchResult` with disposition, age, timestamps, source,
   freshness, and fallback/coalescing flags.

Key-scoped events coalesce simultaneous identical calls. Provider work occurs
outside cache and flight-map locks, so unrelated keys can progress concurrently.
The same provider exception is exposed to joined callers, and flight state is
cleaned after both success and failure.

`force_refresh=True` bypasses an otherwise acceptable cache entry but still
passes through the provider gate.

## Stale-on-error

Stale fallback is never implicit. It requires `allow_stale_on_error=True`, a
finite caller-provided `max_stale_seconds`, an actually `STALE` cached entry,
and an age within that bound. The result visibly reports `STALE` and
`stale_fallback_used=True`. Otherwise the provider or scheduling failure is
raised. General `allow_stale=True` remains a separate decision to accept a
bounded stale cache hit without attempting a provider call.

## Metrics

An immutable runtime snapshot reports cache entries, hits, misses, fresh/aging/
stale hits, puts, evictions, provider fetches, coalesced requests, provider
blocks, and stale fallbacks. These are local process counters; A1.6 adds no
Prometheus or distributed telemetry dependency.

## Future relationships

A future `AnalysisContext` can carry `FetchResult` attribution so consumers see
where facts came from and how old they are. A future provider-health layer can
drive the existing enable/disable and cooldown boundary. A future Intelligence
OS can decide work order above this runtime without putting candidate queues,
Agents, LLM orchestration, ranking, or trading semantics into factual caching.

## Non-goals and limitations

- no background loop, queue, async runtime, Redis, database, or distributed lock;
- no fallback-provider arbitration or full health/degradation model;
- no Agent, LLM, LangGraph, scoring, recommendation, account, order, or execution code;
- no automatic provider waits;
- no automatic inference of provider observation time for values that do not
  expose it;
- one coordinator callback represents one rate-counted provider request;
  adapter methods that internally create multiple HTTP chunks should be
  decomposed into request-sized coordinated work when strict per-call gating is
  required;
- no deep immutability of arbitrary cached values or metadata;
- process-local cache, scheduler history, metrics, and single-flight state only.

The read-only quote demo explicitly uses the normalized quote `received_at` to
measure the age of the retrieved API snapshot. The nested `QuoteSnapshot`
continues to preserve Dhan's distinct last-trade `observed_at`, so a closed
market does not make a just-retrieved response look like an old cache entry.
