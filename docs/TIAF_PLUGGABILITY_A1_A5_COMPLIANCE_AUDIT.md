# TI Pluggability — A1–A5 Compliance Audit

## Decision, scope and evidence limits

Audit date: 2026-09-12 (Asia/Kolkata).

**Decision: READY_FOR_PLUGGABILITY_REMEDIATION**

**A5 freeze impact: A5_FREEZE_BLOCKED_PENDING_PLUGGABILITY_REMEDIATION**

Post-audit remediation addendum, 2026-09-12: the bounded
[R1 implementation](TIAF_PLUGGABILITY_R1_REQUIRED_SCOPE_EXPLICIT_ABSENCE.md)
corrects F1 with Planner schema/policy `1.1`, explicit required/optional absence,
stable A3.9 completeness, and a legacy `1.0` compatibility path. Its current
implementation decision was `READY_TO_ACCEPT_PLUGGABILITY_R1` and
`A5_FREEZE_BLOCKER_R1_RESOLVED`. The subsequent
[acceptance closure](TIAF_PLUGGABILITY_R1_ACCEPTANCE_AND_A5_FREEZE_READINESS.md)
returns `READY_TO_CLOSE_PLUGGABILITY_R1` and
`A5_READY_FOR_FINAL_DOCUMENTATION_AND_FREEZE`. The two lines above remain the
original audit verdict rather than a claim that the defect is still present.
A5 remains untagged pending consolidation and a final tag-readiness check.

One bounded pre-freeze issue is demonstrated: the A3 Planner derives required
participation from the installed registry. Removing a required specialist can
silently remove that requirement and its missingness from A3.9 completeness for
the same request. Fix the requirement/availability distinction, not A5 rules or
the deterministic A2 benchmark. Other metadata/composition improvements are
pre-A6 work; future Sector Rotation, forecasting and HOT are not A5 prerequisites.

The [authoritative pluggability architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md)
governs this review. The earlier [A5 closure](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
remains a historical READY_TO_FREEZE_A5 finding within its original scope.
This audit adds a cross-cutting condition; it does not identify an A5 evaluator
defect or invalidate existing recorded captures.

Entry HEAD remains `5d31a9d`. The preceding architecture pass was already
uncommitted: 13 modified Markdown files and one new architecture document.
Those changes are preserved. No A5 tag exists at audit entry. This pass changes
only documentation; no runtime/test/configuration refactoring, installation,
live request, model call, commit, tag, push or A6 work is performed.

Method: targeted source inspection of typed interfaces, composition roots,
selection/failure/admission and replay paths; inspection of relevant existing
test assertions; three bounded read-only Python diagnostic invocations using
existing synthetic fixtures and no external services. This is not a full security
audit, renewed live acceptance or proof of every behavior of every module.
Existing tests cited below were inspected, not rerun; no pytest pass count is
claimed. Required documentation checks are recorded at the end.

## 1. Classification and level interpretation

Canonical guarantees remain **HOT ⇒ COLD ⇒ STRUCTURAL**. STRUCTURAL is a stable
typed replacement/composition boundary; COLD additionally permits trusted
pre-start selection. HOT requires safe live composition transitions, not merely
a mutable dictionary or an enable flag. No audited component demonstrates or
needs the complete HOT guarantee.

In the matrix, `COLD (local)` means existing trusted Python construction/config
can select bindings before use; it does not claim a universal deployment config,
frozen registry, optional package extra or hot lifecycle. Missing safeguards are
reported separately. `FIXED` is a scoped semantic disposition, not a fourth
pluggability level; fixed implementations can expose structural contracts.

Role: REQUIRED is operation/profile-specific; OPTIONAL is independently
omissible only under a valid reduced contract. REPLACEABLE and COMPOSABLE are
traits, not alternatives to requiredness. `INTENTIONALLY_FIXED` is the primary
audit status requested by this audit brief, not a new runtime enum. It is not a
failure to comply. Recommendations and compliance status are separate axes.

## 2. Audit matrix

43 components across eight areas: A1, A2, A3, A4, A5, facade/catalog, Shell and
cross-layer replay. Each row has one primary status and primary recommendation.
R-numbers refer to the bounded plan in §13; additional observations are not
counted as additional components. Source links identify the inspected boundary;
the detailed findings below name the relevant functions and tests.

| ID | Area / component | Current role | Current pluggability | Target pluggability | Compliance | Freeze blocker? | Remediation | Evidence |
|---|---|---|---|---|---|---|---|---|
| 01 | A1: canonical identity/time | REQUIRED | FIXED contracts | Preserve fixed semantics | INTENTIONALLY_FIXED | No | PRESERVE_REQUIRED | [common.py](../src/tiaf/contracts/common.py), [normalization.py](../src/tiaf/data/normalization.py) |
| 02 | A1: quote/history/derivative provider ports | REQUIRED per live request; REPLACEABLE provider | STRUCTURAL / COLD (local injection) | COLD | COMPLIANT | No | NO_CHANGE | [provider.py](../src/tiaf/data/provider.py), [builder.py](../src/tiaf/context/builder.py) |
| 03 | A1: resolver registry / provider composition roots | REPLACEABLE resolver; explicit provider selection | STRUCTURAL / COLD (local); mutable registry | COLD, pinned bindings | PARTIALLY_COMPLIANT | No | MAKE_COLD (R5) | [registry.py](../src/tiaf/data/resolution/registry.py), [inspection script](../scripts/inspect_technical_specialist.py) |
| 04 | A1: context evidence requirements/admission | REQUIRED integrity; OPTIONAL requested evidence slots | STRUCTURAL with supplied requirement policy | STRUCTURAL | COMPLIANT | No | PRESERVE_REQUIRED | [builder.py](../src/tiaf/context/builder.py), [requirements.py](../src/tiaf/context/requirements.py) |
| 05 | A1: cache/coordinator/provider scheduling | REPLACEABLE cache; REQUIRED factual freshness | STRUCTURAL / COLD (local) | COLD within trusted scope | PARTIALLY_COMPLIANT | No | DEFER (R7) | [cache.py](../src/tiaf/data/runtime/cache.py), [models.py](../src/tiaf/data/runtime/models.py) |
| 06 | A2: feature engine/registry | COMPOSABLE calculators; request-required features | COLD (local) | COLD | COMPLIANT | No | NO_CHANGE | [registry.py](../src/tiaf/features/registry.py), [engine.py](../src/tiaf/features/engine.py) |
| 07 | A2: indicator engine/registry | COMPOSABLE calculators | COLD (local) | COLD | COMPLIANT | No | NO_CHANGE | [registry.py](../src/tiaf/indicators/registry.py), [engine.py](../src/tiaf/indicators/engine.py) |
| 08 | A2: relative strength / MTF | OPTIONAL context where supported; explicit benchmark inputs | STRUCTURAL pure modules | STRUCTURAL | COMPLIANT | No | NO_CHANGE | [relative.py](../src/tiaf/features/relative.py), [multi_timeframe.py](../src/tiaf/features/multi_timeframe.py) |
| 09 | A2: S/R and breakout geometry | Versioned benchmark facts | STRUCTURAL; formulas FIXED | Preserve fixed formulas | INTENTIONALLY_FIXED | No | PRESERVE_REQUIRED | [support_resistance.py](../src/tiaf/features/support_resistance.py), [breakout.py](../src/tiaf/features/breakout.py) |
| 10 | A2: derivative feature meaning | Versioned factual definitions; conditional applicability | STRUCTURAL; formulas FIXED | Preserve fixed formulas | INTENTIONALLY_FIXED | No | PRESERVE_REQUIRED | [derivatives.py](../src/tiaf/features/derivatives.py) |
| 11 | A2: market state/opportunity scoring/ranking | REQUIRED deterministic control | STRUCTURAL policy input; benchmark FIXED | Preserve control identity | INTENTIONALLY_FIXED | No | PRESERVE_REQUIRED | [engine.py](../src/tiaf/baseline/engine.py), [scoring.py](../src/tiaf/baseline/scoring.py), [ranking.py](../src/tiaf/baseline/ranking.py) |
| 12 | A2: snapshots/corpus/replay | REQUIRED integrity; REPLACEABLE storage boundary | STRUCTURAL, filesystem store | STRUCTURAL | COMPLIANT | No | PRESERVE_REQUIRED | [replay.py](../src/tiaf/evaluation/replay.py), [store.py](../src/tiaf/evaluation/store.py) |
| 13 | A3: Agent registry and identity extension | REPLACEABLE implementations; bounded role IDs | COLD (local), closed IDs, mutable registration | COLD with explicit snapshot ownership | PARTIALLY_COMPLIANT | No | MAKE_COLD (R5) | [registry.py](../src/tiaf/agents/registry.py), [enums.py](../src/tiaf/agents/enums.py) |
| 14 | A3: Technical | Independent peer; technical evidence required for its invocation | STRUCTURAL / COLD (local) | COLD | COMPLIANT | No | NO_CHANGE | [specialist.py](../src/tiaf/agents/specialists/technical/specialist.py) |
| 15 | A3: Fundamental | Independent peer; financial evidence required for its invocation | STRUCTURAL / COLD (local) | COLD | COMPLIANT | No | NO_CHANGE | [specialist.py](../src/tiaf/agents/specialists/fundamental/specialist.py) |
| 16 | A3: News/Event | Independent peer; event evidence required | STRUCTURAL / COLD (local) | COLD | COMPLIANT | No | NO_CHANGE | [specialist.py](../src/tiaf/agents/specialists/news_event/specialist.py) |
| 17 | A3: Relative Strength | Independent peer; benchmark-relative evidence required | STRUCTURAL / COLD (local) | COLD | COMPLIANT | No | NO_CHANGE | [specialist.py](../src/tiaf/agents/specialists/relative/specialist.py) |
| 18 | A3: Sector | Independent peer; attributed sector context required | STRUCTURAL / COLD (local) | COLD | COMPLIANT | No | NO_CHANGE | [specialist.py](../src/tiaf/agents/specialists/sector/specialist.py) |
| 19 | A3: Macro | OPTIONAL workflow peer; macro evidence required if invoked | STRUCTURAL / COLD (local) | COLD | COMPLIANT | No | NO_CHANGE | [specialist.py](../src/tiaf/agents/specialists/macro/specialist.py) |
| 20 | A3: Derivatives Context / Opportunity Quality / Risk | Context peer plus downstream summaries | STRUCTURAL / COLD (local) | COLD | COMPLIANT | No | NO_CHANGE | [specialists.py](../src/tiaf/agents/specialists/opportunity/specialists.py) |
| 21 | A3: MI registry/routing/normalization | REPLACEABLE, COMPOSABLE provider/normalizer pairs | COLD (local route policy) | COLD | COMPLIANT | No | NO_CHANGE | [registry.py](../src/tiaf/market_intelligence/registry.py), [routing.py](../src/tiaf/market_intelligence/routing.py) |
| 22 | A3: concrete adapter import aggregation | OPTIONAL routes, but aggregate import dependency | STRUCTURAL transports; eager package exports | COLD with import isolation | PARTIALLY_COMPLIANT | No | REMOVE_HARD_DEPENDENCY (R4) | [providers/__init__.py](../src/tiaf/market_intelligence/providers/__init__.py) |
| 23 | A3: evidence/model gateways | REQUIRED authority/budget gates; OPTIONAL model engine | STRUCTURAL / COLD policy and provider mapping | COLD | COMPLIANT | No | PRESERVE_REQUIRED | [policy.py](../src/tiaf/agents/gateways/policy.py), [reasoning.py](../src/tiaf/agents/gateways/reasoning.py) |
| 24 | A3: Planner requirement/inventory resolution | Required coverage derived from registrations | STRUCTURAL, registry-driven policy | COLD with independent required/optional scope | NON_COMPLIANT | Yes: F1 | ADD_DEPENDENCY_DESCRIPTOR (R1) | [policy.py](../src/tiaf/planner/policy.py), [coordinator.py](../src/tiaf/workflows/coordinator.py) |
| 25 | A3: serial/LangGraph workflows and budgets | REPLACEABLE runner; bounded common coordinator | STRUCTURAL / COLD caller choice | COLD | COMPLIANT | No | NO_CHANGE | [coordinator.py](../src/tiaf/workflows/coordinator.py), [langgraph_adapter.py](../src/tiaf/workflows/langgraph_adapter.py) |
| 26 | A3.9: structured synthesis / peer completeness | Typed composition, fixed interpreted fields | STRUCTURAL; closed contributor projections | STRUCTURAL; versioned peer extensions | PARTIALLY_COMPLIANT | Yes: F1 propagation | OTHER (R1, then R6) | [contributions.py](../src/tiaf/service/opportunity_intelligence/contributions.py), [policy.py](../src/tiaf/service/opportunity_intelligence/policy.py) |
| 27 | A3.10: verification and comparison | REQUIRED replay integrity | STRUCTURAL, current default registry verifier | STRUCTURAL with exact binding resolution | PARTIALLY_COMPLIANT | No | ADD_REPLAY_PINNING (R3) | [replay.py](../src/tiaf/a3_hardening/replay.py) |
| 28 | A4: deterministic Challenger | REQUIRED bounded review role | STRUCTURAL functions; implementation FIXED | STRUCTURAL; no HOT | INTENTIONALLY_FIXED | No | PRESERVE_REQUIRED | [challenges.py](../src/tiaf/a4/challenges.py), [evaluation.py](../src/tiaf/a4/evaluation.py) |
| 29 | A4: Arbitrator / policy | REQUIRED resolution/safety role | STRUCTURAL; approved policies FIXED | STRUCTURAL; approved COLD variants later | INTENTIONALLY_FIXED | No | PRESERVE_REQUIRED | [arbitration.py](../src/tiaf/a4/arbitration.py), [policy.py](../src/tiaf/a4/policy.py) |
| 30 | A4: evidence bridge/enrichment/successor | OPTIONAL bounded enrichment; REQUIRED grants/admission | STRUCTURAL / COLD injected services/runner | COLD | COMPLIANT | No | NO_CHANGE | [bridge.py](../src/tiaf/a4_enrichment/bridge.py), [admission.py](../src/tiaf/a4_enrichment/admission.py) |
| 31 | A4: source/PIT/authority projection | REQUIRED evidence integrity | STRUCTURAL; admission semantics FIXED | Preserve required boundary | INTENTIONALLY_FIXED | No | PRESERVE_REQUIRED | [projection.py](../src/tiaf/source_semantics/projection.py), [contracts.py](../src/tiaf/source_semantics/contracts.py) |
| 32 | A4: recorded/verification/chain replay | REQUIRED integrity and original lineage | STRUCTURAL captured inputs | STRUCTURAL | COMPLIANT | No | PRESERVE_REQUIRED | [replay.py](../src/tiaf/a4/replay.py), [chain replay](../src/tiaf/a4_enrichment/replay.py) |
| 33 | A5: position context/identity/freshness | REQUIRED supplied truth; A4 needed for substantive advice | STRUCTURAL; safety FIXED | Preserve required boundary | INTENTIONALLY_FIXED | No | PRESERVE_REQUIRED | [contracts.py](../src/tiaf/a5/contracts.py), [freshness.py](../src/tiaf/a5/freshness.py) |
| 34 | A5: posture/thesis/advice/protection/expiry | REQUIRED deterministic position baseline | STRUCTURAL; evaluator FIXED | Preserve accepted semantics | INTENTIONALLY_FIXED | No | PRESERVE_REQUIRED | [evaluation.py](../src/tiaf/a5/evaluation.py) |
| 35 | A5: MonitoringNeed / WatchMandate | Advisory intent; scheduler absent | STRUCTURAL typed output | STRUCTURAL | COMPLIANT | No | NO_CHANGE | [monitoring.py](../src/tiaf/a5/monitoring.py), [contracts.py](../src/tiaf/a5/contracts.py) |
| 36 | A5: policy selection | REQUIRED approved baseline; comparison-only variant | STRUCTURAL; executable versions restricted | STRUCTURAL, approved COLD later | INTENTIONALLY_FIXED | No | PRESERVE_REQUIRED | [policy.py](../src/tiaf/a5/policy.py) |
| 37 | A5: capture/replay/verification | REQUIRED exact snapshot/A4/policy lineage | STRUCTURAL offline replay | STRUCTURAL | COMPLIANT | No | PRESERVE_REQUIRED | [replay.py](../src/tiaf/a5/replay.py) |
| 38 | Facade: descriptor/catalog/discovery | Curated consumer capabilities | STRUCTURAL static catalog | STRUCTURAL descriptors + scoped readiness | PARTIALLY_COMPLIANT | No | ADD_DISCOVERY_METADATA (R2) | [contracts.py](../src/tiaf/facade/contracts.py), [capabilities.py](../src/tiaf/facade/capabilities.py) |
| 39 | Facade: admission/artifacts/position.assess | REQUIRED trusted authority; typed captured dispatch | STRUCTURAL | STRUCTURAL | COMPLIANT | No | PRESERVE_REQUIRED | [admission.py](../src/tiaf/facade/admission.py), [runtime.py](../src/tiaf/facade/runtime.py), [artifacts.py](../src/tiaf/facade/artifacts.py) |
| 40 | Facade: startup lifecycle/dispatch ownership | Fixed reviewed operations; configurable grants/artifacts | COLD config/artifacts; operation bindings FIXED | Retain static bindings until justified | INTENTIONALLY_FIXED | No | NO_CHANGE | [runtime.py](../src/tiaf/facade/runtime.py) |
| 41 | Shell: commands/discovery/one-shot/REPL | OPTIONAL consumer; closed grammar | STRUCTURAL, trusted client injection | STRUCTURAL; no loader | COMPLIANT | No | NO_CHANGE | [dispatcher.py](../src/tiaf/shell/dispatcher.py), [runtime.py](../src/tiaf/shell/runtime.py) |
| 42 | Shell: session/explain/trace/refresh | OPTIONAL presentation; no authority ownership | STRUCTURAL session-local state | STRUCTURAL | COMPLIANT | No | NO_CHANGE | [session.py](../src/tiaf/shell/session.py), [renderers.py](../src/tiaf/shell/renderers.py) |
| 43 | Cross-layer replay: composition manifest | REQUIRED attribution, fragmented current records | STRUCTURAL child captures; no unified composition descriptor | STRUCTURAL additive parent manifest | PARTIALLY_COMPLIANT | No | ADD_COMPOSITION_MANIFEST (R3) | [records.py](../src/tiaf/workflows/records.py), [contracts.py](../src/tiaf/a3_hardening/contracts.py) |

## 3. A1 and A2 findings

Matrix totals: **23 COMPLIANT, 8 PARTIALLY_COMPLIANT, 1 NON_COMPLIANT,
11 INTENTIONALLY_FIXED, 0 NOT_APPLICABLE** = 43. Two affected matrix rows
share the single F1 pre-freeze issue; there is one required remediation, R1.

A1 provider ports accept canonical typed identity/quotes/history and separate
derivative/historical-option protocols. `AnalysisContextBuilder.__init__` accepts
provider/resolver/coordinator objects; derivative providers can be absent. The
resolver registry routes explicit provider identity or the uniquely registered
resolver, not a guessed vendor. It permits replacement by dictionary assignment,
so it is not evidence of a frozen or HOT composition lifecycle (R5).

Provider choice is concretely pinned in live composition roots, for example
`scripts/inspect_technical_specialist.py` constructs Dhan resolver/provider/rate
policy objects around lines 308–311. Settings expose Dhan configuration; there
is no general A1 provider factory/configuration catalog. This is adapter/wiring
work behind an existing structural boundary, not Dhan semantics in A2 scoring.
A3's Tapetide/Yahoo route helper names provider IDs in explicit configuration;
its fallback does not implement secondary A1 quote/OHLCV/F&O routing (DEF-008).

`DataFetchCoordinator.get_or_fetch` preserves typed scheduling blocks, cache
freshness and explicitly enabled stale-on-error behavior; context requirements
decide required versus optional evidence and expose missing/failed descriptors.
A1 readiness is factual/scheduling readiness, not entitlement. `CacheKey` has
provider, instrument, operation and parameters but no first-class caller/
entitlement partition; the coordinator is a trusted local primitive, not a
multi-tenant authorization gateway. Do not share it across security scopes on
the strength of this audit (R7, deferred until a governed live/shared host).

Evidence source/provider identity, aware timestamps and PIT/quality boundaries
must stay required. Factual cache freshness does not prove historical availability;
A2 snapshots and later source/MI captures own their respective replay/PIT
guarantees. No evidence integrity primitive should become an optional plugin.

A2 already has explicit FeatureCalculator/IndicatorCalculator protocols,
duplicate-safe caller-populated registries and pure engines. Additional
independently requested calculators can be selected before use. A registry
lookup failure for an explicitly requested calculator is a request error, not
an optional peer failure to conceal. Relative/MTF input identity and S/R,
breakout and derivative definitions remain versioned factual semantics.

The distinction is **calculator extensibility versus benchmark identity**.
BaselineEngine accepts named policies but its market-state/component scoring,
classification, missingness and ranking remain the deterministic control. Adding
an unconsumed feature need not change that control; using it, changing weights,
or changing required feature treatment requires a separate policy/comparison.
Do not renormalize weights to hide omitted evidence. `evaluation.replay` checks
snapshot fingerprint and policy ID/version/style before scoring captured input;
the filesystem corpus has no provider fallback. No A2 remediation is prescribed.

Relevant existing evidence includes feature/indicator registry tests, A2.6/A2.7/
A2.8 architecture tests and
[snapshot replay tests](../tests/unit/evaluation/test_snapshot_replay.py).
These are existing coverage, not fresh gate results.

## 4. A3 findings and the freeze blocker

### F1 — Required scope disappears with registry membership

Source chain:

1. `planner/policy.py:66`, `dependencies`, iterates only registered capabilities
   in the closed IMPLEMENTED set. At line 85 all except Macro are marked required.
2. `build_plan` iterates those specs. It records inapplicable, permission-denied,
   no-LLM and bounded-cap skips for registered entries, but cannot record an
   entirely unregistered known requirement. Upstream edges are also restricted
   to registered/selected identities.
3. `workflows/coordinator.py`, `finalize`, adds incomplete-required gaps only for
   existing plan nodes; only a completely empty plan gets the generic no-agent gap.
4. A3.9 `project_contributions` processes plan nodes and recorded skips.
   `completeness` computes its required denominator from these contributions;
   synthesis `policy.evaluate` uses that set in `coverage_ok`.

Bounded synthetic probe, same `scripts._a3_8_fixtures.request()` and evidence:

| Observation | Default registry | Registry without Fundamental |
|---|---|---|
| Declared registry entries | 9 | 8 |
| Required coverage denominator in A3.9 projection | 8 | 7 |
| Fundamental in required set | Yes | No |
| Fundamental in missing set | Yes | No |
| Fundamental-specific orchestration gap | Yes | No |
| A2 pack preserved | Yes | Yes |
| Provider calls | 0 | 0 |
| Recorded replay fingerprint matches | Yes | Yes |

This does not prove an attractive final trade recommendation or changed A5
advice; the fixture's A2 NO_TRADE remains intact. It proves that installation
state can redefine reported required coverage without a request/profile scope
change. Raw registry membership is captured, but it cannot explain whether the
missing role was deliberately optional, disabled, unavailable or accidentally
omitted. That materially violates the new requirement-versus-usability invariant.

R1 is the only MUST_FIX_BEFORE_A5_FREEZE item. Define a bounded trusted required/
optional scope independently of actual bindings for the existing specialists,
retain absent/disabled outcomes and propagate them into A3.9 completeness.
Do not make all specialists universally mandatory; DAY Fundamental, optional
Macro and instrument-conditional derivatives must retain explicit applicability.
A legitimate reduced profile must be declared/pinned, not inferred from imports.
Preserve captured legacy interpretation under its old policy/version.

### Independent peers and actual downstream consumers

The first-order technical, fundamental, news, relative, sector, macro and
derivative modules expose SpecialistCapability/analyze contracts with required
and optional evidence, supported instrument types and no-LLM declarations.
They consume supplied facts, not provider clients. Missing required families
lead AgentRuntime to INSUFFICIENT_EVIDENCE; failed lookups/analysis produce
failure records, not fabricated stances. The defect is Planner omission before
that runtime, not those individual specialist contracts.

The probe found empty upstream dependency tuples for every selected first-order
peer. There is no arbitrary technical → fundamental → news → macro semantic
chain. Quality/Risk are genuine downstream summaries over supplied projections;
their edges are not evidence that execution order alone encodes investment
priority. Existing serial/concurrent parity tests cover shuffled completion and
selective reruns. The closed IMPLEMENTED, DOWNSTREAM, FIELDS and detail-schema
mappings are intentional current scope, but adding a new kind of peer will need
a versioned projection/descriptor extension (R6), not just register(new_object).

### Providers, gateways and workflow ownership

MI providers/normalizers register as matching explicit identities; route policy
selects per capability, preserves failures and source ambiguity, and bounds
fallback/enrichment. Registration is not permission. The controlled gateway/
request and caller composition own authorization. Model role and provider are
separate: reasoning policy defaults to disabled/NONE, explicitly controls tiers,
capabilities and budgets, and can return a no-LLM result before calling anything.
The accepted specialists and orchestration remain no-LLM.

F2 (R4): `market_intelligence/providers/__init__.py` eagerly imports official
HTTP, Tapetide MCP and Yahoo MCP implementations even when importing the fixture
provider submodule. An import-blocker probe successfully imported contracts,
baseline, workflows, A4, A5, facade and Shell with httpx/mcp/LangGraph/LangSmith
blocked, but importing `providers.fixture` failed on httpx from package init.
Thus Core remains transport-independent; concrete provider packaging is not
fully omission-independent. httpx/mcp are currently required package dependencies,
so this is not a demonstrated failure in a supported installed baseline. Separate
lazy/explicit adapter exports before promising optional installation. It is not
an A5 freeze blocker and does not authorize changing dependency extras now.

Agent/MI registries and ControlledServices are mutable trusted construction
objects; OrchestrationCoordinator retains references while capturing declarations.
They lack a unified “freeze on start” ownership rule (R5). No actual concurrent
registry-mutation failure was demonstrated. This is not HOT support, nor an
invitation for consumers to mutate registries. The facade does not expose them.

The serial/reference runner and optional LangGraph adapter share one coordinator.
`workflows.__init__` does not import the framework adapter. LangGraph selects
parallel execution and disables external tracing; framework objects do not enter
domain contracts. Preserve parity for the same selected set; budget/deadline
differences can legitimately alter participation and are recorded.

## 5. A4 and A5 findings

A4 Challenger and Arbitrator are required bounded roles in `a4.evaluate`.
Separate typed functions/contracts provide structural seams, while evaluation
directly binds the accepted implementations. `require_supported_policy` accepts
only the exact approved baseline/comparison variants. This is intentional
semantic fixation, not a requirement for a general challenger registry now.

A4 consumes a validated A4SemanticInputProjection with sources, assertions,
qualifications, disputes, admitted references and original A2/A3 lineage. It is
typed semantic composition, not arbitrary open-ended peer registration. New
challenge output/schema mappings require explicit versioning. An optional future
model Challenger remains DEF-052; it cannot replace required arbitration or
turn model memory into evidence.

A4.2 admits needs against grants, entitlements, source roles, budgets, depth and
deadline, maps bounded capabilities to Planner requests and reuses the controlled
services. A successor records new admitted evidence and preserves its parent;
recorded/verification chain replay does not execute acquisition. This is an
existing progressive-enrichment seam, not an unbounded research loop or public
LIVE_READ facade operation.

A5 requires validated supplied position identity/time/authority, a supported
single-position shape and current snapshot truth. The A4 field may be None in
the contract to represent INSUFFICIENT_EVIDENCE, not to permit unsupported
MAINTAIN advice. Freshness is explicit wall-clock policy, not a market calendar.
Current A4/successor identity checks and invalidation references preserve lineage.
Posture, thesis health, recommendation, protection and expiry/time-risk rules
remain deterministic and no-provider/no-model. MonitoringNeed/WatchMandate emit
intent only; no scheduler is implied.

A5 policy is a typed input with exact supported-version validation; the public
facade selects approved behavior, not consumer policy injection. Policy comparison
creates a separate record. PositionSignal and successor A4 results are existing
bounded future-context seams, not permission to squeeze sector or forecast
semantics into unrelated enum values or metadata. A sector/forecast observation
may later be mapped only if its accepted meaning and attribution genuinely fit;
otherwise a separately versioned adapter/contract/policy is needed. No A5 redesign
or dependency on these future contributors is required for the accepted baseline.

`position.assess` reads an authorized logical artifact, checks position/scope/
entitlement, delegates to A5, and returns canonical result/fingerprint. Shell
only builds that typed request. No provider or broker implementation handle
leaks through the public API. A5 rows have no local freeze blocker; F1 is an
upstream cross-cutting completeness issue, not a new A5 implementation mandate.

## 6. Facade and Shell findings

F3 (R2): CapabilityDescriptor has ID/version, input/output schemas, effect,
determinism/model, replay, authority, cost and deprecation fields, but no
pluggability level, scoped role/traits or dependency declarations. Availability
defaults to AVAILABLE in the static catalog. `can_discover` combines that field
with caller/operator grants and omits undiscoverable entries; it does not return
separate installed/configured/disabled/data/dependency/health dimensions.
Consequently discovery cannot explain the future architecture's full state model.

This does not bypass authorization or guarantee a usable artifact: admission
and artifact reads still enforce scope. Record the gap as PARTIALLY_COMPLIANT,
not a claim that every visible operation succeeds or that a privilege leak was
found. Future metadata/readiness projection must be additive/versioned because
current strict request/result contracts and clients are not universal readers.

The catalog and request dispatch are deliberately authored for eight operations.
LocalFacadeOwner deep-validates config, freezes artifacts on start, rejects
post-start additions and rechecks revocation. Configurable grants/artifacts
do not make every operation replaceable at runtime. Static dispatch is appropriate;
no generic function/module loader is recommended.

Shell commands are statically known while permissions/artifacts may be absent.
`capabilities describe` returns a safe unavailable error when no permitted
descriptor exists. Invocations use the facade, so session defaults do not grant
authority. One-shot/REPL share parser/dispatcher/renderer, sessions are local,
explain/trace project structured records and refresh re-admits a new invocation.
Missing descriptors do not need dynamic command unloading. Shell is compliant
with its current consumer role; richer availability wording follows R2 without
a plugin loader or new commands for unpublished capabilities.

## 7. Replay and composition findings

**Installing Sector Rotation next year cannot make recorded replay of a 2026
capture invoke it.** Recorded paths reconstruct validated bytes/typed artifacts;
they do not consult live providers or dispatch newly registered contributors.

The relevant pinning is distributed rather than absent:

| Layer | Captured/validated today | Limitation |
|---|---|---|
| A2 | Evidence snapshot, producer/policy identity, fingerprint and expected assessment | No arbitrary historical reconstruction from uncaptured live data. |
| A3.8 | Request, registry/dependency specs, plan versions, nodes, skips, attempts, opinions, failures, reservations and child artifacts | Missing unregistered expectations are not captured (F1); not the full new composition manifest. |
| A3.9/A3.10 | Captured orchestration, typed contributions, baseline side, policies, package/child digests and comparisons | Closed projections; current-default verifier binding limits compatibility. |
| A4/A4.2 | Exact semantic projection, policy, findings, admission/need/bridge/successor chain and captured child execution | Does not invent an open peer descriptor universe. |
| A5 | Exact snapshot, linked current A4, full request/signals, policy, run/result fingerprints and checksums | Future context needs an accepted typed mapping/version, not automatic rediscovery. |

F4 (R3): `a3_hardening.replay.verify_a3_package` obtains `default_registry()`.
`workflows.replay.verify_deterministic` compares rebuilt plans to captured plans
before specialist calls. A changed/additional registry therefore rejects mismatch
rather than silently enriching history. The offline probe verified that the
reduced capture replays exactly and verification with the full registry raises
“planner/dependency version or deterministic plan mismatch.” The A3.10 wrapper
maps such ValueError to UNVERIFIABLE. This is safe refusal, not full support for
verifying every historical/custom composition.

F5 (also R3): no shared parent descriptor/composition fingerprint spans facade,
availability, required/optional scope and all child histories. Existing plan/run/
package hashes are meaningful but must not be relabeled the new architecture's
complete manifest. Add a bounded parent envelope that references existing hashes
and records unavailable/disabled/used states without rewriting child captures.
Legacy records retain recorded replay and explicit limits; unavailable old code
means verification unavailable, not replacement with today's installed code.

Semantic verification only re-executes supported pinned deterministic behavior;
recorded model output never requires a model call. Policy/capability comparison
must create new records with unchanged control and disclosed evidence changes.
Neither exact arbitrary PIT reconstruction (DEF-049) nor distributed replay
(DEF-050) is necessary to resolve this audit.

## 8. Failure isolation, authority and cost verdicts

| Case | Observed boundary / result | Verdict |
|---|---|---|
| Provider unavailable/rate-limited | A1 typed gate/context missingness; MI configured fallback and retained failure records | Isolated within accepted policies; no market opinion invented. |
| Registered specialist fails | AgentRuntime failure record; coordinator captures failed/timed-out attempt and continues other admitted nodes | Compliant for attempted nodes; F1 covers pre-dispatch omission. |
| Planner refuses work | Explicit permission, no-LLM, unsupported, cap, missing-disposition and stop reasons | Honest for inventoried entries; absence inventory needs R1. |
| Model disabled | Reasoning policy NONE/disabled path and orchestration no-LLM constraints | No implicit model entitlement or execution. |
| Stale data | Quality/freshness propagated; A5 stale/unknown position yields ABSTAIN | Not a fabricated bearish or bullish factual view. |
| Unsupported input | Typed unsupported/error; A5 multi-leg shape preserved and rejected | Required semantics not silently weakened. |
| Replay corruption | Checksums/fingerprints/cross-reference validation fail closed | No live repair or favorable fallback. |
| Optional future contributor fails | Existing per-agent isolation is reusable; generic absent-peer inventory is incomplete | R1/R6 must preserve gaps rather than synthesize a stance. |

Existing test assertions inspected include specialist exception isolation,
timeout/unknown reservation retention, changed-registry rejection, offline imports,
A5 replay corruption, permission-only discovery, revocation/entitlement denial,
and Shell refresh identity. These do not prove hostile-code/process-crash
isolation; synchronous cancellation and durable accounting remain limited.

Authority verdict: required trusted boundaries are preserved. Facade discovery
or descriptor possession does not grant invocation; caller/operator/profile/
effect/budget intersection governs admission and artifact access rechecks rights.
Trusted operator config is the legitimate grant source; “configuration grants
nothing” means enabling/registering an implementation cannot self-authorize an
ordinary caller. Lower-level provider/Agent registries and A1 cache are trusted
internal APIs, not independent multi-tenant authorization services. No new
consumer-accessible privilege escalation was found in inspected paths.

Cost/composition verdict: progressive enrichment already exists. Planner chooses
applicable specialists, material gaps and bounded evidence tasks; MI stops on
sufficiency/budget/unsupported routes; A4.2 adds one admitted evidence round.
ControlledServices semantic acquisition keys and futures support shared reads,
and ReservationLedger reserves/settles nested work and retains unknown usage.
Available capability does not automatically justify acquisition. Selection is
generic engineering policy, not calibrated expected value or investment alpha.

The remaining limitations are already bounded: top-level opaque callbacks do
not prove exact leaf HTTP-call caps (DEF-015); unknown prices are not known-zero
currency cost (DEF-055); shared provider-account budgets and durable recovery
need later hosting work. No duplicate ledger, mandatory model or economic
threshold retuning is recommended.

## 9. Mandatory/fixed core and level recommendations

Preserve REQUIRED canonical identity, aware Asia/Kolkata/PIT semantics, evidence
admission/quality/source authority, caller authorization, replay integrity,
fingerprint/audit meaning and the A2 deterministic benchmark. A4 arbitration
and A5 snapshot/freshness/safety semantics are required for their operations.
No missing model/sector/forecast implementation may weaken those requirements.

Use STRUCTURAL for stable domain calculations, integrity and typed A4/A5 policy
boundaries. Use COLD for reviewed provider/normalizer bindings, independently
supported specialist sets, optional calculators/models and workflow adapters.
Preserve fixed semantic policy identities where comparison must be explicit.
No actual HOT need was demonstrated. Registry register/replace methods and A1
schedule enable/disable are not safe hot installation/unloading. DEF-057 remains
deferred; no service mesh, queue or universal DI framework follows.

## 10. Sector Rotation conformance forecast

- Registration: a new intelligence contributor needs a reviewed ID/typed output/
  dependency descriptor in the trusted composition. It is not automatically
  today's A3.6 SECTOR specialist or a market-data provider entry. R6 addresses
  the closed mappings before publication.
- Discovery: add an intentional versioned facade operation only if a consumer
  needs it; R2 supplies scoped availability. It is not in today's catalog.
- Enable/disable: operator-approved COLD composition with explicit scope under
  R1/R5; installation alone cannot create availability or authority.
- Consumers: typed upstream context can inform later synthesis/A4; A5 may consume
  an admitted A4 successor or genuinely compatible PositionSignal. New semantics
  require a versioned mapping/policy, not metadata injection or a direct A5 call.
- Absence: baseline operates without an opinion from this optional contributor;
  an explicitly sector-required request cannot silently claim complete coverage.
- Replay: capture its inputs, declaration/version, actual participation and
  output/child fingerprints through R3. Older captures stay unchanged/offline.

Therefore architecture placement is clear, but current runtime cannot promise
“register tomorrow and every consumer understands it.” That is a concrete
extension gap, not a reason to implement Sector Rotation now.

## 11. Signal Qualification conformance forecast

`signal.qualify` can be OPTIONAL and peer-composable. A real optional dependency
on Sector Rotation is recorded only if its policy consumes it; derivatives,
forecast or ML inputs may be optional under a valid reduced contract. Required
request predicates still block. Baseline works without qualification and no
absence is interpreted as a false-signal prediction or approval.

A later curated facade operation is possible after typed candidate/input/output,
dependency and policy contracts are accepted. Contributor lineage must preserve
which enrichers participated (R1/R3/R6). It must not recursively require its
own downstream A4 result while A4 simultaneously requires qualification:
choose an upstream contribution or explicit bounded successor stage. No circular
ownership is accepted. Probability objectives, thresholds and ML implementation
remain in the non-authoritative idea cache; no signal capability is promoted.

## 12. Findings inventory

| Finding | Concrete gap | Matrix rows | Priority |
|---|---|---|---|
| F1 | Registration changes required coverage without explicit profile/scope; omission lacks status | 24, 26 | MUST_FIX_BEFORE_A5_FREEZE |
| F2 | Provider package eager imports couple fixture/optional adapters to transports | 22 | SHOULD_FIX_BEFORE_A6 |
| F3 | Static facade descriptors lack lifecycle/role/dependencies and scoped readiness | 38 | SHOULD_FIX_BEFORE_A6 |
| F4 | A3.10 verification uses current default registry; safe mismatch rather than exact old binding resolution | 27 | SHOULD_FIX_BEFORE_A6 |
| F5 | Cross-layer composition identity/availability is not a complete additive manifest | 43 | SHOULD_FIX_BEFORE_A6 |
| F6 | Trusted registry/service mutation has no common frozen composition ownership | 03, 13 | SHOULD_FIX_BEFORE_A6 |
| F7 | New peer IDs/details require closed Planner/A3.9 mapping extensions | 26 | DEFER_TO_LATER, before first new peer |
| F8 | A1 cache is not a first-class entitlement-partitioned shared host | 05 | DEFER_TO_LATER, before shared/live host |

Rows 24 and 26 expose the same blocker, not two distinct mandatory remediations.
No additional runtime failure is inferred merely from missing generic metadata.

## 13. Bounded remediation plan and subsequent R1 disposition

### MUST_FIX_BEFORE_A5_FREEZE

**R1 — Stable required/optional scope and explicit absence (F1).**

Implemented by the bounded [R1 remediation](TIAF_PLUGGABILITY_R1_REQUIRED_SCOPE_EXPLICIT_ABSENCE.md).
The audit plan below is retained as the historical requirement; R2–R5 remain
unimplemented.

- Problem/files: `planner/models.py`, `planner/policy.py`,
  `workflows/coordinator.py`, `workflows/records.py`, A3.9
  `contributions.py`/`policy.py`, and affected handoff/capture validators.
- Semantic change: resolve a small trusted, versioned requirement profile for
  existing specialist IDs independently of actual registry membership. Preserve
  legitimate request-specific optionality/applicability. Missing required binding
  remains blocked/incomplete; missing optional binding is disclosed without a
  fabricated opinion. Record the expected set and absence reasons in a bounded
  plan/result extension; no general-purpose manifest is a prerequisite.
- Compatibility: changed plans/coverage are new semantics and need an explicit
  supported planner/capture/policy version path. Preserve old captured bytes,
  hashes and recorded reconstruction; never retrofit required peers into old
  records or demand a new profile field from legacy readers. R1 must include
  the minimal replay/handoff compatibility needed by its own new fields.
- Required tests: same declared request/profile with full/reduced/empty registry;
  required missing vs optional missing vs disabled vs denied; DAY company scope,
  Macro opt-out, equity/F&O applicability; unchanged A2; no invented opinion;
  denominator cannot shrink due solely to absence; A3.9 propagation; old/new
  capture round trips; recorded offline replay and changed-scope comparison;
  run existing upstream/facade/A4/A5 regression gates after implementation.
- Blast radius: **MEDIUM**, localized A3 planning/completeness/capture semantics
  with downstream regression verification. No A5 policy/rule change.

### SHOULD_FIX_BEFORE_A6

**R2 — Versioned descriptor and scoped discovery metadata (F3).**

- Files: facade `contracts.py`, `enums.py`, `capabilities.py`, `admission.py`,
  `runtime.py`; Shell rendering only as needed for the accepted discovery result.
- Change: scoped role/traits/lifecycle/dependency declaration plus separate
  readiness result; visibility distinct from eligibility and unknown data checks.
  Keep operation dispatch static, deny authority escalation, add no live probe.
- Compatibility: additive/versioned discovery contract or explicit supported
  projection; current strict 1.0 callers remain supported. Do not change existing
  child domain dispositions or equate missing readiness with bearishness.
- Tests: permission-filtered inventory, disabled/unregistered/unknown-data and
  dependency states, available-but-denied invocation, no effects from discovery,
  old descriptor readers and Shell safe rendering. **LOW–MEDIUM** blast radius.

**R3 — Composition envelope and pinned verification resolution (F4/F5).**

- Files: workflow records/replay, A3.10 contracts/package/replay and approved
  facade capture metadata. Reference existing A2/A4/A5 child records unchanged.
- Change: bounded parent manifest for expected/resolved/used/absent contributors,
  policies/dependencies/availability and composition identity; resolve exact
  compatible verification bindings instead of assuming today's default registry.
- Compatibility: new parent schema; legacy manifest completeness explicitly
  unknown, old recorded readers retained, no in-place migration of children.
  Unsupported old implementation remains UNVERIFIABLE, never live repaired.
- Tests: legacy captures, additional/removed installed contributor, missing
  pinned version, failure-vs-success identity, tampering, no-network replay,
  policy/capability comparisons, original-vs-replay usage. **MEDIUM** blast radius.

**R4 — Optional adapter import isolation (F2).**

- Files: `market_intelligence/providers/__init__.py`, explicit adapter imports
  and their smoke/test composition roots only.
- Change: prevent importing an unrelated adapter/fixture from eagerly requiring
  every HTTP/MCP connector. Do not create another client or change normalization.
- Compatibility: preserve documented exports via a reviewed lazy mechanism or
  explicit migration; dependency-extra packaging changes need separate approval.
- Tests: blocked/missing unrelated SDK, fixture-only import, individual Yahoo/
  Tapetide/official imports, Core import, no subprocess/network on import and
  adapter regressions. **LOW** blast radius.

**R5 — Trusted COLD composition ownership (F6).**

- Files: Agent/MI/resolver registries, workflow coordinator/services and explicit
  startup composition roots. Audit feature/indicator construction under the same
  owner rule before introducing shared use; no formula change.
- Change: bounded immutable binding snapshot/freeze at owner start or invocation
  admission; predictable duplicate/replacement rules before that boundary, no
  mid-run binding changes. Do not retrofit HOT or make the facade expose registries.
- Compatibility: construction APIs remain usable before freeze; reject unsupported
  later mutation explicitly. Preserve declared versions and existing capture hashes
  except separately versioned new identity fields where necessary.
- Tests: pre-start selection, duplicate binding, post-start mutation denial,
  in-flight stability, caller isolation and replay compatibility. **MEDIUM** radius.

### DEFER_TO_LATER

**R6 — New peer publication/projection (F7).** Before the first new contributor,
extend trusted IDs/descriptors, Planner dependencies, typed A3.9/source/A4 mapping
and optional facade publication. No Sector Rotation or Signal Qualification
implementation here. New schemas/policies and migration retain old inputs and
hashes. Tests must cover peer absence/order/conflict/non-comparability, required
scope and no circular qualifier/A4 dependency. **MEDIUM** radius; any design
requiring broad A1–A5 refactoring or a HIGH-radius semantic change must return for
architecture review instead of expanding this plan.

**R7 — Shared live/cache governance (F8).** Before multi-caller live hosting,
review A1 cache keys, coordinator ownership and authorized gateway/facade lookup
for entitlement/PIT partitioning and revocation. Existing local behavior stays
unchanged; new isolation keys may invalidate caches but must not rewrite evidence.
Tests: cross-grant denial, no future-as-of leakage, shared account quota and
unknown cost. **MEDIUM** radius; track within DEF-009/011 and relevant hosting
work, not an A5 requirement.

Also keep HOT generation/rollback engineering deferred (DEF-057), production
models (DEF-052), pricing (DEF-055), remote APIs (DEF-003), monitoring runtime
(DEF-010), arbitrary historical PIT (DEF-049), and distributed replay (DEF-050).
Their existing triggers/tests remain binding. No new HIGH-radius implementation
is recommended. No A5 freeze condition depends on sector/forecast/ML delivery.

## 14. Governance, validation and next step

The immediate remediation work is not a newly deferred capability. R1–R5 are
tracked in implementation targets; F7/new peer readiness is retained as DEF-058
until a separately approved contributor needs it. Existing DEF IDs are preserved;
no unrelated capability is declared implemented by this audit.

Next prompt title:

**TI PLUGGABILITY — BOUNDED REMEDIATION: REQUIRED SCOPE AND EXPLICIT ABSENCE**

That implementation should address R1 and its necessary compatibility tests
only. R2–R5 are separately bounded pre-A6 slices, not prerequisites for fixing
F1. After R1 acceptance, re-evaluate the A5 freeze condition without automatically
starting A6 or creating a tag. No unresolved architecture contradiction requires
another design pass; the requirement-versus-registration distinction is settled.

Validation completed:

- `git diff --check`: PASS.
- README/docs relative file-link check: 102 Markdown files, 705 targets,
  zero missing files (file existence, not a remote URL availability check).
- Matrix: 43 unique row IDs; primary compliance counts reconcile to 43.
- Deferral register: 58 unique IDs; 45 DEFERRED, 4 PLANNED, 4 IMPLEMENTED,
  3 REJECTED, 2 SUPERSEDED. DEF-058 is the sole new deferral in this audit.
- Current README/roadmap/targets/milestones/map/register all point to this audit
  and distinguish immediate R1 from pre-A6 and later work. Historical architecture
  and closure decisions remain historical, not competing current next steps.
- New-document whitespace checks: PASS. Source/tests/scripts/configuration
  remain unchanged; accumulated worktree is 13 modified and two new Markdown
  files, including the preserved preceding architecture pass.
- Three bounded diagnostic invocations completed: guarded imports, plan
  membership comparison, and captured workflow/completeness/replay comparison.
  No live/provider/model access or runtime file edit. Existing runtime tests were
  inspected, not rerun; **0 pytest tests executed in this audit**.

Files created/updated by this audit (eight): this new document; `README.md`;
`docs/IMPLEMENTATION_ROADMAP.md`; `docs/TRADINGINTELLIGENCE_ROADMAP.md`;
`docs/TIAF_IMPLEMENTATION_TARGETS.md`; `docs/MILESTONES.md`;
`docs/TIAF_CAPABILITY_MAP.md`; `docs/TIAF_DEFERRAL_REGISTER.md`.
Other pre-existing architecture-pass modifications are preserved, not attributed
to this audit. No commit, tag or push; A5 remains untagged.
