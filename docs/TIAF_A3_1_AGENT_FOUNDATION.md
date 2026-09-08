# TIAF A3.1 Agent Contracts and Runtime Foundation

## Status

**IMPLEMENTED / PENDING ACCEPTANCE**

Starting baseline: `tiaf-a3-arch` at
`9e8c6ec09a7ec8929247a1deb37b546aceaae0a0`.

A3.1 establishes provider-neutral, framework-neutral contracts and a bounded
single-specialist runtime. It does not implement a real specialist, evidence
gateway, LLM call, Planner, LangGraph graph, fundamental/news acquisition,
forecast model, arbitration, position action, option expression, or execution.

## Package structure

The public package is `tiaf.agents`:

- `enums.py` — specialist, stance, capability, run, citation, calibration, and
  analysis-mode identities;
- `evidence.py` — references, citations, claims, missing-evidence requests, and
  immutable evidence packs;
- `budget.py` — vendor-neutral hard budgets and observed usage;
- `models.py` — request, confidence, specialist definition, AgentOpinion v2,
  run record, forecast seam, and reasoning contracts;
- `protocols.py` — runtime-checkable `SpecialistAgent` and
  `ReasoningProvider` protocols;
- `registry.py` — caller-populated, duplicate-safe specialist discovery;
- `runtime.py` — exactly-one-specialist invocation and failure isolation;
- `compatibility.py` — explicit A0 opinion compatibility boundary;
- `serialization.py` — deterministic run-record JSON and reconstruction;
- `summaries.py` — factual run/usage diagnostics only;
- `errors.py` — typed Agent, evidence, budget, timeout, output, registry, and
  future reasoning-provider failures.

No package module imports a live provider, broker, HTTP client, LLM SDK, or
LangGraph.

## Stable identities

`SpecialistId` contains:

- `TECHNICAL`
- `FUNDAMENTAL`
- `NEWS_EVENT`
- `RELATIVE_STRENGTH`
- `SECTOR`
- `MACRO`
- `DERIVATIVES_CONTEXT`
- `OPPORTUNITY_RISK`
- `CONTRARIAN_HYPOTHESIS`
- `FORECAST_INTERPRETATION`

Only identity and contracts exist. There is no built-in specialist
implementation in A3.1.

`AnalysisMode` distinguishes `DETERMINISTIC_ONLY`, `RULE_POLICY`,
`LIGHTWEIGHT_REASONING`, `FULL_SPECIALIST`, and `DEEP_ANALYSIS`. A mode names
permitted depth; it never causes an implicit LLM call.

## AgentRequest

`AgentRequest` binds one request/run to one subject, normalized instrument type,
accepted `TradeStyle` where applicable, accepted `Horizon`, purpose, analysis
mode, task, and one stable specialist identity. It requires:

- explicit A2 context and evidence IDs;
- the original deterministic A2 assessment reference;
- a SHA-256 evidence fingerprint;
- an immutable allow-list of controlled capabilities containing
  `READ_A2_EVIDENCE`;
- an immutable `AgentBudget`; and
- an aware timestamp normalized to `Asia/Kolkata`.

The request cannot silently change the A2 baseline or authorize capabilities
after creation.

## Evidence references and availability

`AgentEvidenceReference` reuses the accepted A1 `EvidenceStatus` vocabulary:
`AVAILABLE`, `PARTIAL`, `STALE`, `MISSING`, `FAILED`, `DEFERRED`, and
`NOT_REQUESTED`. It also preserves accepted `DataQuality` and `FreshnessState`.

Available/partial/stale evidence requires quality, freshness, and a checksum.
Stale availability requires stale freshness. Missing, failed, deferred, or
unrequested evidence cannot claim factual quality. Failed evidence requires a
typed failure code/detail. Acquisition cannot predate observation.

`AgentEvidencePack` contains references rather than fetching or recomputing
facts. It separately preserves AnalysisContext, feature, indicator, relative,
MTF, derivatives, deterministic-assessment, fingerprint, quality, freshness,
coverage, and missing-evidence identities. Aggregate quality/freshness must
equal the weakest factual reference; an empty/unavailable pack cannot be
silently upgraded.

## Claims and missing evidence

Every `EvidenceClaim` has a stable ID, kind, statement, evidence family,
as-of timestamp, provenance, quality, freshness, and at least one structured
`EvidenceCitation`. Each citation explicitly `SUPPORTS` or `CONTRADICTS` the
claim. The runtime verifies that cited IDs exist in the supplied pack, are
factually available, and match the claim's evidence family.

`MissingEvidenceRequest` expresses what the specialist lacks, why, importance,
freshness, optional bounded time range, and the controlled capability needed.
It has no method for fetching evidence. A future A3.2 gateway/Planner decides
whether the request is authorized and satisfied.

## AgentOpinion v2 and frozen A0 compatibility

The accepted A0 `tiaf.contracts.AgentOpinion` remains unchanged at schema
`1.0`. Its direction and mandatory scalar confidence cannot represent A3's
full semantics. A3.1 therefore exposes `tiaf.agents.AgentOpinionV2` at schema
`2.0` rather than mutating or shadowing A0.

AgentOpinion v2 preserves:

- request/run/specialist/subject/horizon/version identities;
- `POSITIVE`, `NEGATIVE`, `NEUTRAL`, `MIXED`,
  `INSUFFICIENT_EVIDENCE`, or `ABSTAIN` stance;
- explicit run status;
- reason codes, claims/citations, supporting and contradictory evidence;
- missing evidence, risks, and caveats;
- A2 assessment and agreement relationship;
- evidence fingerprint, quality, and freshness;
- optional model and prompt identity, required policy version, usage/cost, and
  validity timestamps; and
- the separated confidence contract.

Infrastructure `FAILED`, `TIMEOUT`, and `BUDGET_EXCEEDED` states cannot be
encoded as market opinions. `BUY`, `SELL`, `CE`, `PE`, `HOLD`, and `EXIT` are
not Agent stances.

The explicit compatibility adapter wraps a v1 opinion only when subject and
evidence references are consistent. The exact original v1 contract is embedded
for lossless reconstruction. Native v2 opinions cannot be down-converted
because that would discard A3 semantics.

## Confidence semantics

`AgentConfidence` separates:

- evidence coverage;
- evidence quality;
- optional self-reported confidence plus its explicit basis;
- optional policy-derived confidence plus policy identity/version; and
- optional empirically calibrated confidence plus method, cohort, sample size,
  calibration identity, and evaluation time.

Missing values remain `None`. Self-reported confidence is not probability of
financial success. A3.1 implements no confidence algorithm.

## Specialist and reasoning protocols

`SpecialistAgent` is runtime-checkable and requires only:

```text
capability() -> SpecialistCapability
analyze(AgentRequest, AgentEvidencePack) -> AgentOpinionV2
```

`SpecialistCapability` declares identity/version, supported instrument types,
required/optional evidence types, allowed capability contracts, no-LLM support,
relative cost tier, and explicit prohibitions.

`ReasoningProvider` is an unused future seam:

```text
identity() -> ReasoningModelIdentity
reason(ReasoningRequest) -> ReasoningResponse
```

It preserves provider/model/config identity, structured fields, exact usage,
timeout/failure state, and timestamps without importing a vendor SDK. A3.1
provides no implementation and makes no model call.

## Registry and single-specialist runtime

`AgentRegistry` registers protocol-conforming specialists, rejects duplicate
stable IDs, performs typed lookup, and lists capabilities deterministically by
ID. Adding a dummy specialist requires no runtime modification.

`AgentRuntime.run()`:

1. resolves exactly one requested specialist;
2. validates specialist identity, supported instrument, capability allow-list,
   evidence-pack/request linkage, evidence fingerprint, and A2 assessment ID;
3. returns `INSUFFICIENT_EVIDENCE` without invocation when required evidence is
   absent;
4. invokes the specialist once with no provider/tool side effects;
5. reconstructs and validates AgentOpinion v2;
6. verifies claims and missing-evidence capability requests against the pack;
7. records observed elapsed time and validates all budget dimensions; and
8. emits an immutable `AgentRunRecord` with an opinion or a sanitized typed
   failure—never both for infrastructure failure.

The runtime contains no specialist-specific branches, multi-Agent plan,
arbitration, graph, model selection, evidence acquisition, or retry loop.

## Budget and usage

`AgentBudget` provides hard maximums for LLM calls, tool calls, input/output
tokens, abstract cost units, and elapsed seconds. Defaults permit zero model
and tool calls. `AgentUsage` preserves actual counts/cost/elapsed time.

Every exceeded non-time limit becomes `BUDGET_EXCEEDED`; elapsed-limit breach
becomes `TIMEOUT`. The invalid opinion is discarded, but observed usage and the
typed failure remain in the run record.

## Run record, serialization, and future replay

`AgentRunRecord` embeds the complete immutable request and evidence pack, the
specialist/version, opinion or typed failure, status, exact usage, and aware
start/completion times. Cross-field validation preserves request, subject,
fingerprint, and A2 baseline identity.

`agent_record_json()` uses stable key ordering and ordinary JSON arrays;
`load_agent_record_json()` performs full reconstruction and validation. This is
not full Agent replay. It supplies the future A3.10/A7 identity seam for
specialist/horizon/regime comparison, A2 disagreement value, coverage effects,
cost per useful assessment, and later confidence calibration.

## Forecast, fundamental, and news boundaries

`ForecastEvidence` is a consumer-only contract for external, versioned numeric
distributions and probabilities. A calibrated label requires method, sample
size, calibration ID, and held-out validation metrics. Quantiles must be unique
and ordered. A3.1 generates no forecast or probability.

Fundamental and news/event concepts exist only as specialist/evidence/capability
identities. No provider, browser, HTTP client, filing fetch, news fetch, or
fundamental calculation is present.

## Security and authority

Architecture tests inspect imports and public enums to prohibit provider,
broker, HTTP/network, shell/subprocess, LLM SDK, LangGraph, option-expression,
position-action, and execution leakage. Public Agent metadata recursively
rejects credential-shaped keys. Unexpected specialist exceptions are sanitized
and isolated without producing a market stance.

TradeMonitor remains the future governor and the broker remains outside TIAF's
authority.

## Validation record

The A3.1 implementation passed:

- `.venv/bin/python -m compileall src`;
- `.venv/bin/pytest` — **1,302 passed in 4.06s**;
- `.venv/bin/ruff check src tests`;
- `.venv/bin/mypy src tests` — no issues in 257 source files; and
- `git diff --check`.

Of the 1,302 tests, 73 directly exercise the A3.1 package. No live validation
is applicable because A3.1 has no provider, network, model, or broker adapter.
No new deferral was discovered; A3.2–A3.10 remain planned milestones rather
than deferrals.

## A3.2 handoff

A3.2 may implement controlled evidence/reasoning/budget gateways against these
contracts. It must preserve the existing allow-list, budget, failure,
fingerprint, claim, no-LLM, A2-baseline, and zero-authority semantics. It must
not bypass `MissingEvidenceRequest` by giving specialists direct provider or
network access.
