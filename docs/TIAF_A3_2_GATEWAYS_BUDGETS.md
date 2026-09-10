# TIAF A3.2 Controlled Gateways and Budgets

## Status

**TIAF_A3.1:** complete / accepted at `tiaf-a3.1`

**TIAF_A3.2:** complete / accepted at `tiaf-a3.2`

**TIAF_A3.3:** complete / accepted at `tiaf-a3.3`

**Current:** TIAF_A3.4 — Fundamental Evidence and Company Quality Specialist,
implemented / pending acceptance

The implementation baseline is
`4b6cb8bacd6c6e7966fac2ce52ce6ab892ebc35c`. A3.2 adds infrastructure and
policy enforcement only. It does not implement specialist market judgment,
planning, arbitration, forecasting, option expression, position management, or
execution.

## Boundary

Future specialists receive evidence through `EvidenceGatewayRuntime` and may
request optional structured reasoning through `ReasoningGateway`. They do not
receive provider clients, credentials, arbitrary URLs, browser access, shell,
SQL, filesystem access, broker sessions, or order capabilities.

The gateway packages are provider and framework neutral:

```text
agents/gateways/
  contracts.py   immutable requests, results, and audit records
  protocols.py   EvidenceGateway protocol
  registry.py    evidence and reasoning-provider registries
  evidence.py    read-only A2 evidence gateway
  runtime.py     evidence authorization/cache/budget/timeout authority
  reasoning.py   optional structured-reasoning authority
  cache.py       evidence reuse and future reasoning-cache keys
  policy.py      capability ceilings, model mappings, and downgrade policy
  enums.py       statuses, tiers, capabilities, and decisions
  errors.py      typed boundary failures
```

Infrastructure status is never translated into a market stance. `TIMEOUT`,
`BUDGET_EXCEEDED`, `MODEL_DISABLED`, `UNAVAILABLE`, and invalid output remain
gateway outcomes; they are not `POSITIVE`, `NEGATIVE`, or `NEUTRAL` opinions.

## Evidence gateway and authorization

`EvidenceGateway` exposes only `identity()`, `capabilities()`,
`can_handle(request)`, and `fetch(request, context)`. The request names a
stable ID, exact `AgentCapability`, subject/instrument/horizon/purpose, evidence
family and requested attributes, decision/as-of boundary, required freshness,
optional bounded time range, A2 identity references, requesting specialist,
correlation ID, budget, and timeout. It deliberately has no URL, command,
header, SQL, generic query, or credential field.

Authorization is an intersection, not a prompt suggestion: the requested
capability must be present both in `request.allowed_capabilities` and the
global `EvidenceGatewayPolicy.enabled_capabilities`. No `ALL_ACCESS` or
wildcard capability exists. Denial occurs before registry lookup or gateway
invocation and is preserved as `UNAUTHORIZED_CAPABILITY` plus an audit record.
A prompt or metadata value cannot expand this authority.

`EvidenceGatewayRegistry` registers stable gateway IDs, rejects duplicates,
lists IDs/capabilities deterministically, and resolves implementations without
capability-specific runtime branches. If more than one gateway can handle a
capability, the caller must supply the gateway ID; ambiguity is never resolved
silently.

## A2 evidence gateway

`A2EvidenceGateway` is the first concrete gateway. It is initialized with
immutable `A2EvidenceEntry` objects containing an already-built
`AgentEvidencePack` and its externally owned validity boundary. It indexes the
pack by subject and evidence fingerprint and returns the exact pack object. It:

- preserves evidence, assessment, context, producer, checksum, timestamp,
  quality, freshness, and fingerprint identities;
- never recalculates an indicator, feature, score, or A2 fingerprint;
- never calls Dhan, another broker, HTTP, or a provider adapter;
- reports missing subject/fingerprint/family or assessment mismatches
  explicitly; and
- retains partial and stale states instead of upgrading them.

A gateway or reasoning failure cannot mutate the supplied A2 pack or promote a
different A2 result. A valid A2 baseline remains independently usable.

## Evidence cache and unchanged-evidence reuse

`InMemoryEvidenceGatewayCache` is an A3 tool-result cache, not a duplicate of
A1 transport caching. Its semantic key excludes request IDs, correlation IDs,
authorization bookkeeping, budgets, and metadata, while retaining subject,
capability, evidence family, attributes, horizon, as-of/time bounds, context,
freshness requirement, and requested evidence fingerprint.

Reuse is permitted only when the semantic key is unchanged, the returned
evidence fingerprint is therefore unchanged, the gateway identity/version is
compatible, the result was successful or partial, and `valid_until` has not
been reached. A hit returns the new request ID, records `HIT`, and consumes no
new tool call. Expired, stale, failed, deferred, or gateway-version-mismatched
entries are misses and are invalidated. A3.2 does not cache opinions.

## Reasoning gateway and no-LLM mode

The reasoning gateway uses the accepted A3.1 `ReasoningProvider` protocol. A
provider receives a gateway-assembled, SDK-neutral `ReasoningRequest`; callers
cannot call or select SDK objects through the contract. The A3.2 request binds
the specialist/task/subject/horizon, structured instructions, access-safe
evidence references and fingerprint, requested model tier, allowed model
capability, request budget, prompt/policy/specialist versions, output-schema
ID, bounded configuration, timeout, correlation ID, and canonical timestamp.

`ModelTier` is vendor neutral and ordered: `NONE`, `DETERMINISTIC`,
`LIGHTWEIGHT`, `STANDARD`, and `DEEP`. A `ModelTierMapping` in global policy
maps an enabled non-`NONE` tier to provider/model/version/configuration
identity. Changing that mapping requires no specialist-code change.

`NONE` and globally disabled reasoning are normal paths. They make no provider
call, consume zero model tokens/cost, and return `MODEL_DISABLED` with a full
audit record. Deterministic evidence workflows remain available. No real model
adapter or vendor SDK is included in A3.2: fake providers prove the protocol
and enforcement locally, while concrete adapters belong to a later explicitly
authorized milestone. This is planned sequencing, not a new deferral.

## Budgets and accounting

Global reasoning policy is the authority ceiling; a request budget may be
equal or smaller but cannot exceed it. `AgentBudget` covers model calls, tool
calls, input tokens, output tokens, optional total tokens, provider-neutral
`cost_units`, and elapsed seconds. Core code contains no vendor price table.

Before invocation the runtime checks capability, request-versus-global limits,
model tier/mapping/provider identity, remaining call count, estimated input
tokens, timeout, and registered output schema. Impossible work is rejected
without spending a call. After invocation it records reported token/cost use
and observed latency, then applies request and global caps. Provider overruns
become `BUDGET_EXCEEDED` or `TIMEOUT`, but true usage remains in both result and
audit even when output is rejected.

Evidence and reasoning calls run behind bounded synchronous timeouts. A timeout
is reported explicitly and cannot become an opinion. The in-process thread may
finish after a timeout, but its result is discarded and it has no authority
beyond the gateway/provider object supplied by the host.

## Structured output, downgrade, and replay identity

Every reasoning request names a registered output schema. The runtime invokes
its typed validator before accepting fields. Malformed, mismatched, or
schema-invalid output becomes `MODEL_OUTPUT_INVALID`; raw vendor response
objects are never exposed. Usage remains recorded.

Unavailable tier behavior is explicit policy:

- `FAIL` returns `UNAVAILABLE`;
- `DOWNGRADE` chooses the highest configured lower tier and records requested
  tier, actual tier, and reason; and
- `NO_LLM_FALLBACK` returns `MODEL_DISABLED` with the recorded reason.

Reasoning results and audits preserve provider/model/version/configuration,
requested and actual tier, evidence fingerprint, prompt/policy/specialist
versions, tokens, cost units, latency, finish/failure status, timestamps, and
correlation ID. `reasoning_cache_key()` prepares later opinion/result reuse
over semantic task, evidence fingerprint, model identity/version, prompt and
policy versions, specialist/schema identity, tier, and relevant configuration.
No reasoning-result reuse is performed in A3.2.

The later A3 sub-milestone deferral-discovery audit assigns DEF-052 to the
distinct production model-backed reasoning adapter/policy that remains after
the provider-neutral gateway contracts were accepted. This does not change the
historical A3.2 implementation boundary.

## Security and future gateways

Contract metadata and structured fields reject credential-shaped keys such as
`access_token`, `authorization`, `password`, `secret`, `api_key`,
`client_secret`, and broker-account identifiers. This is defense in depth; the
primary control is that contracts expose neither credentials nor generic
transport/tool authority. Architecture tests prohibit broker/provider HTTP
clients, OpenAI/Anthropic SDKs, LangGraph, subprocess, arbitrary file access,
and code execution in the gateway layer.

The existing capability vocabulary prepares later bounded gateways for
fundamentals, filings, news, sector, macro, derivatives, additional market
evidence, and forecasts. Future results can carry source/event/publication and
acquisition times, validity, quality, freshness, evidence identity,
provenance, and cache state. `READ_FORECAST` is only a future read capability:
forecast production and calibration remain A7, and an LLM cannot manufacture
calibrated probabilities.

## A3.3 handoff

A3.3 may implement the first Technical and Market Structure specialist using
only authorized `READ_A2_EVIDENCE` results and, optionally, this reasoning
gateway. It must not recompute A2 indicators/features, add browser or broker
access, perform final arbitration, or emit trading/option actions. No other
specialist is implemented by A3.2.
