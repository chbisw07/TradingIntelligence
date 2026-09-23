# IFL pre-A8 foundation — producer, claim and service contracts

Implementation and validation record: 2026-09-24, Asia/Kolkata.
Authority: bounded pre-A8 foundation implementation request, not authority to
implement full IFL, start A8 integration, run empirical research or publish a
new facade capability. The [IFL architecture](TIAF_IFL_INTELLIGENCE_SERVICE_ARCHITECTURE.md)
remains authoritative and unchanged; no architectural contradiction was found.

## 1. Verified starting point

Before source edits, branch `main` and the working tree were clean. HEAD,
`origin/main` and the actual remote `refs/heads/main` matched:

`b67482d1a77812e2912eb4c584500e9d80a5d320`

Read-only remote verification used `git ls-remote` after sandbox DNS prevented
the initial check. Committed/pushed ancestry included initial IFL architecture
`24225e5`, active-primary reconciliation `a979b5b`, and README synchronization
`b67482d`. No commit, tag or push is part of this implementation pass.

## 2. Repository findings and reuse

The new namespace is `tiaf.service.intelligence`, alongside existing bounded
service facades, rather than inside a forecasting family or provider adapter.
The repository already provides the necessary immutable contracts, time codec,
identity primitives and deterministic JSON/fingerprinting conventions.

| Existing primitive | Reuse in this foundation |
|---|---|
| `ContractModel` / `ForecastContract` | Frozen contracts, explicit schema version, forbidden extra fields; the new base also revalidates instances |
| `LogicalId`, `ArtifactReference` | Logical IDs and typed artifact/policy/evidence references |
| `ForecastDateTime` | Reject naive datetimes; normalize to `ZoneInfo("Asia/Kolkata")`; JSON carries `+05:30` |
| `ForecasterKey`, `FamilyIdentifier` | Existing non-LLM model/version and family identity, not a competing model-ID system |
| `ReasoningModelIdentity` | Existing provider/model identity with optional provider-exposed model version |
| `ForecastRealizationMode` | Preserve actual issuance versus simulated historical clock meaning |
| `canonical_json`, `semantic_fingerprint` | Existing deterministic codec/hash; no new serializer framework |

Inspection included forecasting identity/inference contracts, agent and reasoning
gateway identity/errors, evaluation envelopes, local service contracts and test
organization. No FF/FLC or existing gateway adapter needed modification.

## 3. Identity and version boundaries

`ServiceIdentity` is a logical service ID plus service version. It has no host,
endpoint, transport or credential. `ProducerIdentity` binds the actual producer
type/ID, service, configuration version and capability declaration. Nine producer
kinds can be represented without forcing ML fields onto rules or other producers.
Optional model family, `ForecasterKey`, artifact and training references reuse the
existing identities. Capabilities declare bounded, unique supported claim kinds.

LLM producers use `ReasoningModelIdentity` plus mandatory prompt, tool-configuration
and orchestration versions. An unknown provider-exposed model version remains
absent, not invented. Tests use OpenAI-like, Anthropic-like, Google-like and
synthetic strings, with no SDK imports or provider calls.

`ActiveLLMConfiguration` contains a scope/configuration identity and exactly one
primary LLM producer. It is a configuration value, not a global active-model
registry, switching mechanism or admission grant. Direct deterministic outputs
need neither this configuration nor a synthesizer: `NO_LLM` remains valid.

Package version `0.1.0`, contract schema `1.0`, service version, model version,
configuration version, prompt version and orchestration version are distinct.
Request/response schema IDs and fingerprint profiles identify the new envelope;
existing persisted FF/FLC formats and identities are untouched.

## 4. Typed claims and resolution

| Kind | Bounded value semantics |
|---|---|
| BINARY | Exactly one probability or boolean assertion; raw/calibrated/not-applicable state and explicit calibrator reference where calibrated |
| NUMERIC | Finite numeric value and unit |
| CATEGORICAL | Value belongs to an explicitly supplied unique vocabulary |
| ORDINAL | Value belongs to an explicitly supplied unique ordered scale |
| RANKING | Exact ordered permutation of the declared unique universe |
| INTERVAL | Ordered finite bounds, unit and predictive coverage strictly between zero and one |
| EVENT_TIME | Aware point-time estimate, not a fabricated probability or survival distribution |

`EvaluableClaim` binds claim/request identities, actual producer, information
cutoff, as-of and creation clocks, realization mode, discriminated value and a
mandatory `ResolutionContract`. Kind must agree with both the resolution and
producer capability. Invalid pairings, non-finite values and malformed domains
are rejected. Explicit absolute maturity follows as-of; actual issuance must
precede that maturity, while simulated historical creation may occur later.

`ResolutionContract` carries typed target and resolver references, target
semantics, subject, reference timestamp/evidence, claim kind, resolution mode and
one explicit maturity variant:

- absolute timestamp;
- positive trading-session count with calendar reference;
- positive calendar duration in seconds;
- event identity/policy, optionally with an explicit deadline.

These are declarations for later independent Ground Truth, not a scheduler,
market-calendar implementation or executed resolver. References and fingerprints
express identity/integrity bindings, not proof of custody, truth or authorization.

## 5. Response, provenance and immutability

```text
IntelligenceRequest: logical service + expected producer + capability + clocks
                                 |
                       IntelligenceResponse
                       |-- actual producer / optional synthesizer
                       |-- exactly one primary claim if EVALUABLE
                       |-- zero or more secondary claims
                       |-- contributor identities + output refs + claim IDs
                       |-- evidence refs
                       |-- explanation
                       `-- advisory-only recommendations
```

Non-evaluable responses have no primary or secondary evaluable claims. A scalar
primary field prevents multiple primaries; claim IDs must be unique. Every claim
correlates to the response request and cannot be created after its response.
The actual producer owns the primary claim. Claims from other producers require
matching contributor identity and claim attribution; contributors require a
synthesizer. Direct outputs can omit both. Duplicate/conflicting contributor IDs
and double attribution are rejected, not silently deduplicated.

Fallback proof uses the actual fallback producer identity in a newly bound
request/response. It does not substitute fallback output under the old primary
identity. Prior serialized output continues replaying with its original identity.
No failover policy or live switch is implemented.

All semantic collections are bounded tuples, all foundation values are frozen,
and mutable identity dictionaries are absent. Ordinary Python lists and JSON
arrays are accepted and normalized; JSON serialization still emits arrays.
Boundary validators and fingerprint methods reconstruct values defensively,
including values originating from unchecked Pydantic copy/construct operations.

Claim IDs are explicit logical IDs, not hashes of presentation text. Claim
fingerprints cover admitted claim semantics. The response's scientific
`semantic_fingerprint()` deliberately excludes explanation and recommendations;
full serialization preserves them. This projection is **not** full-document
integrity: a future capture store must retain/hash the complete canonical response
as well when protecting presentation/advisory bytes. No capture store is added here.

## 6. Service and transport boundary

`IntelligenceService` is a protocol with `describe()`, `analyze(request)` and
`health()`. `ServiceDescriptor` declares service, capabilities and exact producer
bindings; `ServiceHealth` is timestamped readiness metadata.

`LocalAdapter` adds separate deployment metadata. `RemoteAdapter` additionally
declares request encoding and response decoding. Both consume the same semantic
request/response. Deployment ID, transport kind and latency live outside the
scientific envelope. There is no concrete network adapter or service registry.

Pure `validate_request` / `validate_response` helpers enforce descriptor,
capability, exact producer/version, request correlation, primary-resolution and
clock binding. They do not authenticate a caller or grant execution authority.
Future adapters must use these checks at their decoding/admission boundary.

Typed error categories are `UNAVAILABLE`, `TIMEOUT`, `INVALID_REQUEST`,
`INVALID_RESPONSE`, `VERSION_MISMATCH`, `PROVENANCE_MISMATCH` and
`UNSUPPORTED_CAPABILITY`. Serializable `ServiceFailure` and a code-only exception
provide bounded error semantics. Retry, failover, credentials and network errors
are not implemented; timeout/unavailable behavior is exercised with test doubles.

## 7. Compatibility evidence

- A central synthetic contract test combines categorical and binary contributing
  services under a synthetic LLM identity, preserves attribution and resolution,
  and verifies serialized reconstruction and scientific fingerprint equivalence.
  The LLM is identity-only: no model/network inference is called.
- In-memory local and remote-wire test doubles preserve identical canonical
  response semantics/fingerprints despite different deployment metadata.
- The existing family-neutral inference path runs with its existing test-only
  synthetic adapter; the wrapper preserves native capture identity and output.
  Its explicit event-maturity context does not invent a horizon absent upstream.
- A synthetic FF-0 BaseRate request through the existing inference seam maps the
  native target/window, labeler, subject/reference close, terminal maturity,
  probability and clocks without changing the native result. Target/window
  fingerprint references retain the existing scientific definition.
- Hypothetical FF-2 raw/calibrated claims retain distinct configuration and
  calibrator references. This is compatibility proof, not fitting or empirical
  FF-2 execution and not a grant to reuse consumed 2025 evidence.
- A fresh-process dependency guard proves the foundation imports without
  OpenAI/Anthropic/Google, network/MCP or sklearn dependencies. AST checks enforce
  the bounded source boundary.

No existing source/test file is modified. FF-0 behavior, FF-1 history, FLC, FF-2,
family-neutral inference, existing persisted formats, TM and Workflow App remain
unchanged. Frozen FF-1 custody was checked by hashes only, without recomputing
protected forecasts or scores: all **78 frozen pins** and all four persisted
protocol/execution/evaluation/ledger fingerprints matched.

## 8. Exact file inventory

New source:

- `src/tiaf/service/intelligence/__init__.py`
- `src/tiaf/service/intelligence/common.py`
- `src/tiaf/service/intelligence/identity.py`
- `src/tiaf/service/intelligence/claims.py`
- `src/tiaf/service/intelligence/envelopes.py`
- `src/tiaf/service/intelligence/protocols.py`

New tests:

- `tests/unit/intelligence/__init__.py`
- `tests/unit/intelligence/helpers.py`
- `tests/unit/intelligence/test_contracts.py`
- `tests/unit/intelligence/test_services.py`
- `tests/unit/intelligence/test_compatibility.py`

Documentation: this report (new), `README.md` and
`docs/IMPLEMENTATION_ROADMAP.md` (minimal current-status/navigation updates).
The authoritative architecture and all frozen scientific documents remain unchanged.

## 9. Validation

Commands use the repository `.venv` executables.

| Check | Result |
|---|---|
| `pytest -q tests/unit/intelligence --tb=short` | 145 passed |
| Focused existing inference/seam/lifecycle/authority compatibility tests below | 250 passed |
| `pytest -q --tb=short` | 4,127 passed in 1163.30s (19m 23s) |
| `python -m compileall -q src` | PASS |
| `ruff check src tests` | PASS |
| `mypy src tests` | PASS; 697 source files |
| `validate_links(True)` from the A7 handbook validator | PASS; 5 Markdown files, 241 local links |
| `git diff --check` plus new-file whitespace/fence check | PASS; 12 new files checked separately |
| FF-1 preservation hashes | 78/78 pins; 4/4 record fingerprints MATCH |

Focused compatibility command:

```bash
.venv/bin/pytest -q \
  tests/unit/forecasting/test_neutral_inference.py \
  tests/unit/forecasting/test_forecaster_seams.py \
  tests/unit/forecasting/test_forecaster_lifecycle.py \
  tests/unit/forecasting/test_lifecycle_integration.py \
  tests/unit/evaluation/test_ff2_empirical_authority.py --tb=short
```

The 145 new cases include all seven kinds, identity/version rejection,
primary/secondary attribution, clocks/timezone, immutable/list/JSON round trips,
fingerprint behavior, local/remote parity, all error categories, provider-neutral
LLM identity, fallback replay, NO_LLM and existing-FF compatibility. The focused
250 cases are a subset of the full suite, not additional unique repository tests.

## 10. Intentional deferrals and readiness boundary

No Claim Ledger/persistence service, outcome scheduling, Ground Truth runtime,
Performance Memory, drift detection, improvement proposals, retraining thresholds,
network transport, authentication, discovery, retries, live failover, real LLM
calls, provider SDKs, production ML model, calibration fit, TM or Workflow App was
added. Existing repository regression tests may exercise their existing synthetic
workers; this foundation introduces no new training or empirical execution.

This bounded vocabulary does not yet support ranking ties/partial rankings,
confidence intervals with estimator-specific meaning, event-time survival or
censoring distributions, natural-language claim extraction, or cross-version
contributors sharing one producer ID inside one response. Those require explicit
future contract decisions, not opaque extensions. No generic resolver is claimed.

Full IFL runtime remains **NOT_IMPLEMENTED**. Contract readiness permits future
separately authorized consumption, not approval, promotion, activation or an A8
start. Remaining ledger/integration work is separate; durable recurring operations
remain A10 absent explicit earlier operational authority. FF-2 empirical HOLD and
the consumed-2025/no-refit boundaries remain unchanged.

## 11. Final status and recommendation

All required gates pass. No existing subsystem needed invasive changes, and no
acceptance blocker remains for this bounded contract surface.

```text
IFL_PRODUCER_IDENTITY_IMPLEMENTED = YES
IFL_SERVICE_IDENTITY_IMPLEMENTED = YES
IFL_MODEL_VERSION_INTEGRATION_ACCEPTED = YES
IFL_ACTIVE_LLM_CONFIGURATION_IMPLEMENTED = YES
IFL_CLAIM_TYPES_IMPLEMENTED = YES
IFL_PRIMARY_SECONDARY_CLAIM_MODEL_IMPLEMENTED = YES
IFL_RESOLUTION_CONTRACT_IMPLEMENTED = YES
IFL_SYNTHESIZER_CONTRIBUTOR_PROVENANCE_IMPLEMENTED = YES
IFL_INTELLIGENCE_RESPONSE_IMPLEMENTED = YES
IFL_INTELLIGENCE_SERVICE_CONTRACT_IMPLEMENTED = YES
IFL_LOCAL_ADAPTER_CONTRACT_IMPLEMENTED = YES
IFL_REMOTE_ADAPTER_CONTRACT_IMPLEMENTED = YES
IFL_NO_LLM_PATH_ACCEPTED = YES
IFL_PROVIDER_NEUTRAL_LLM_IDENTITY_ACCEPTED = YES
IFL_LOCAL_REMOTE_SEMANTIC_EQUIVALENCE_ACCEPTED = YES
CURRENT_FF_PRESERVED = YES
CURRENT_FLC_PRESERVED = YES
CURRENT_FF2_PRESERVED = YES
READY_FOR_A8_IFL_FOUNDATION_CONSUMPTION = YES
```

Recommendation: **GO_A8_INTEGRATION_FOUNDATION**.
Consume this surface only in a separately authorized bounded integration step;
do not infer authorization to implement the deferred runtime phases.
