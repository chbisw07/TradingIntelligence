# TI Intelligence Feedback & Learning and Intelligence Service Architecture

**Architecture defined — 2026-09-23, Asia/Kolkata. Implementation NOT_STARTED.**
This is the design and impact-analysis record for heterogeneous intelligence
services and Intelligence Feedback & Learning (IFL). It is not runtime acceptance,
an empirical-use grant, a model-promotion decision, or permission to start A8.
The proposed foundation still needs a separately authorized, bounded contract
implementation and acceptance pass. Conceptual names below are not published APIs.

Inspection baseline: `396228f9c70016e09be8ffaffbfd57e0c7bc77d0` (clean working
tree before this documentation pass). Existing behavior and historical scientific
records are not changed. Normative ownership remains with the
[system architecture](TIAF_SYSTEM_ARCHITECTURE.md),
[Forecasting Framework](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md),
[deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md),
[monitoring architecture](TIAF_MONITORING_ARCHITECTURE.md), and
[trading ecosystem](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md).
This document adds the higher-level service/claim/feedback design, not a second
implementation of their responsibilities.

Reading routes:

- [Repository findings](#2-repository-findings-and-reusable-boundaries) →
  [ownership diagram](#3-complete-logical-architecture-and-ownership) →
  [claims](#5-typed-claims-and-interpretation).
- [IFL and truth](#7-ifl-components-capture-and-durable-state) →
  [measurement](#8-independent-evaluation-and-performance-memory) →
  [governed improvement](#9-learning-coordinator-and-governed-improvement).
- [Deployment](#12-local-remote-and-deployment-architecture) →
  [failure handling](#13-failure-degradation-and-replay) →
  [impact matrix](#14-impact-and-compatibility-assessment).
- [Phased plan](#15-phased-work-plan-and-implementation-timing) →
  [invariants](#16-architectural-invariants) →
  [TBDs/risks](#17-open-decisions-and-risks) →
  [readiness decision](#18-closure-readiness-and-next-bounded-decision).

## 1. Decision, problem and scope

TI will consume **logical Intelligence Services** that expose stable, typed
contracts. A service can wrap an existing forecaster, specialist, rule engine,
LLM, ensemble or future model. A service boundary does not require a process
boundary. Use local adapters first; introduce remote adapters only for justified
isolation, ownership, dependency or deployment needs.

IFL will retain claims and measure their observed effectiveness independently of
the producers. It will connect existing capture, Ground Truth, Evaluation,
provenance and Learning owners through additive contracts. It is not a universal
trainer, a second Ground Truth authority, an autonomous optimization loop, or a
conversation-memory feature.

The present gap is not another Logistic implementation. It is a common way to
identify heterogeneous producers, distinguish evaluable claims from explanation,
preserve their resolution rules and measure them over time. Without that layer,
a compelling synthesis, a calibrated probability, an agent's policy confidence
and a profitable trade could incorrectly be treated as the same kind of evidence.

**Design philosophy:** use LLMs for ambiguity, interpretation, synthesis and
diagnosis; use deterministic TI infrastructure for identity, clocks, history,
truth, measurement, provenance and authority. Astra can contribute intelligence;
it cannot become the historical record or approve its own effectiveness.

Goals are heterogeneous outputs, independent measurement, attributable synthesis,
offline recorded replay, service-specific evolution and topology-independent
meaning. Non-goals are runtime implementation, endpoints, public forecast
exposure, new production models, empirical fitting, automatic retraining,
TM changes, Workflow App implementation, infrastructure procurement and changes
to frozen scientific behavior.

### 1.1 Preserved scientific and authority state

[FF-2.3](TIAF_A7_FF2_3_EMPIRICAL_DATA_USE_AUTHORITY_RESOLUTION.md) remains the
authority resolution record. Its JSON record and fingerprint are not rewritten.

| Work | Preserved state |
|---|---|
| FF-0 | COMPLETE / FROZEN; accepted bounded foundation remains valid. |
| FF-1 | COMPLETE / FROZEN; INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE. BaseRate BENCHMARK; Logistic CHALLENGER / EXPERIMENTAL. |
| FF-1 protected 2025 evidence | CONSUMED, one execution used; no reuse as unseen evidence, no post-holdout refit. |
| FLC | COMPLETE / FROZEN; Logistic reference and family-neutral binary inference retained. |
| FF-2.0 / FF-2.1 / FF-2.2 | Protocol, governance and synthetic-only calibration infrastructure retained. Synthetic engineering success is not empirical permission. |
| FF-2.3 | Authority review complete; 2022 calibration use and 2023–2024 validation use UNVERIFIABLE / NOT GRANTED. |
| FF-2 empirical development / final protected evaluation | HOLD; readiness NO; neither fitting nor protected evaluation starts here. |

IFL access, discovery metadata, a successful service call, performance history
or a Learning proposal cannot override these restrictions. No prospective
protected evidence is collected or examined for this design.

## 2. Repository findings and reusable boundaries

The following are implemented seams, not evidence that the proposed IFL exists.

| Inspected source / architecture | Finding and consequence |
|---|---|
| [Inference contracts](../src/tiaf/forecasting/inference_contracts.py) | `ForecasterKey`, open `FamilyIdentifier`, descriptor, request, provenance and validating `run_inference` exist. `NeutralInferenceResult` remains **binary probability or absence**. Family-neutral does not mean output-kind-neutral. |
| [FLC training identities](../src/tiaf/learning/forecaster_training.py), [trial service](../src/tiaf/learning/forecaster_trial_service.py) | Request/execution/result/artifact lineage belongs to Learning. Existing fixed/trial synthetic authority must not be broadened by wrapping it as a service. |
| [Lifecycle records](../src/tiaf/learning/forecaster_lifecycle.py) | Lifecycle/approval/activation concepts exist; an identity or historical record is not authenticated operational permission. |
| [Ground Truth](../src/tiaf/evaluation/forecast_truth.py) | Pure supplied-evidence endpoint-direction resolution exists, separate from forecasting. It is not a generic arbitrary-claim resolver or a live maturity scheduler. |
| [Normalized Evaluation](../src/tiaf/evaluation/forecast_normalization.py) and [contracts](../src/tiaf/evaluation/forecast_normalization_contracts.py) | Common identities, populations, pairings, metrics and coverage exist. The executable normalized profile is synthetic; legacy FF-1 is a read-only recorded projection, not authorization for new empirical evaluation. |
| [Provenance](../src/tiaf/forecasting/lifecycle_provenance.py), [replay](../src/tiaf/forecasting/lifecycle_replay.py) | Bounded typed lineage, custody distinctions and offline `MATCH` / `MISMATCH` / `UNAVAILABLE` / `UNSUPPORTED` exist. Reuse the ownership and patterns; do not widen frozen graph shapes in place. |
| [Research store](../src/tiaf/forecasting/logistic_store.py) | Content-addressed persisted records underpin existing codec extensions. This is not a transactional multi-writer Claim Ledger or durable job queue. |
| [Agent protocols](../src/tiaf/agents/protocols.py), [models](../src/tiaf/agents/models.py) | `SpecialistAgent` interprets supplied evidence; `ReasoningProvider` and `ReasoningModelIdentity` are SDK-neutral. Confidence dimensions are already separate. Agent opinions are not automatically testable forecasts. |
| [Reasoning gateway](../src/tiaf/agents/gateways/reasoning.py) | Model policy, capability, budget, validation and usage admission have an existing owner. No new direct Astra client belongs in a specialist or domain contract. |
| [Coordinator](../src/tiaf/workflows/coordinator.py), [captured assembly](../src/tiaf/service/opportunity_intelligence/assembly.py) | Planner/workflows own request coordination; assembly preserves contributions/conflicts from captured inputs. `service` currently means a logical module, not a hosted TI HTTP service. |
| [Facade catalog](../src/tiaf/facade/capabilities.py), [COLD owner](../src/tiaf/bootstrap/runtime.py) | Nine local PURE/CAPTURED_READ operations, trusted startup bindings and caller-bound admission exist. No public generic intelligence-service or forecast operation is introduced here. |
| [Memory namespace](../src/tiaf/memory/__init__.py) | Reserved namespace, not an implemented longitudinal Performance Memory. A package name is not a capability. |
| [Deployment](TIAF_DEPLOYMENT_ARCHITECTURE.md) / [monitoring §13](TIAF_MONITORING_ARCHITECTURE.md#13-roadmap-disposition-and-next-action) | Logical boxes may share a runtime. A8 owns TM integration, A9 scanners, A10 durable recurring operations; earlier durable scheduling needs a separate bounded authorization. Existing provider MCP subprocesses are not TI network services. |

No current work is invalidated. The missing generic claim/service layer needs
additive adapters and new, bounded contracts; it does not justify rewriting
FF/FLC, replacing the Planner, or changing the nine-operation catalog now.

## 3. Complete logical architecture and ownership

All boxes marked future below describe roles, not new executables.

```text
Workflow App / Shell / future TM and scanner consumers
                    |
                    v
     TI governed facade / admission / request ownership
                    |
         existing Planner + workflows
           |         |          |                 (future adapters)
           v         v          v
       FF service  Specialist  Other Intelligence Services
       adapter     adapters   Regime / Volatility / Ranking / LLM ...
           \         |          /
            individual immutable outputs + dissent + provenance
                              |
                   validated TI result / claim capture
                      |                         |
                 consumer view             IFL Claim Ledger
                                                |
                      maturity eligibility / bounded resolution work
                                                |
             independent Ground Truth + qualified outcome evidence
                                                |
                          independent Evaluation
                                                |
                          Performance Memory
                                                |
                Learning Coordinator + optional LLM diagnosis
                                                |
                         improvement PROPOSAL
                                                |
                  separate authority / service-owned lifecycle
                                                |
               candidate vNext -> independent validation -> governance
                                      (no automatic activation)
```

| Object or decision | Accountable owner | Must not own |
|---|---|---|
| Capability contract and permitted output kind | TI contract/governance owner with service implementer | Broker authority or scientific success by declaration |
| Model internals, features, training/tuning and artifacts | Owning Intelligence Service; FF learned services delegate to existing Learning/FLC owners | Common external outcome labels or unilateral production acceptance |
| Invocation, selection, budgets and contributor plan | TI admission + existing Planner/workflow owner | Secret model substitution or training through inference |
| Original output and evaluable claim capture | Producer emits; TI validates and persists admitted result | Reinterpretation after outcomes |
| Market outcome / label | Independent Ground Truth owner, pinned resolver and qualified source | Producer self-scoring or LLM judgment replacing facts |
| Metrics, eligible cohort and scientific conclusion | Independent Evaluation owner and approved protocol | Promotion or broker execution |
| Durable performance projections | IFL Performance Memory, derived from immutable Evaluation records | New labels, hidden cohort filtering or raw conversational recollection |
| Diagnosis / improvement proposal | Learning Coordinator; optional versioned LLM advisor | Training code, authority grants, activation |
| Fit / promotion / activation authority | Separately governed authority owners and service lifecycle gates | Implicit grants from selection, metadata or good metrics |
| Orders, fills, live position lifecycle, capital and operational risk | TM; broker is execution-state truth | TI redefining broker truth |
| Views and user interactions | Workflow App / Shell | Canonical claim history or duplicated intelligence logic |

## 4. Producers, services and contracts

### 4.1 Producer is not synonymous with probabilistic forecaster

A **producer** is the attributable origin of an output under a particular
implementation/model/configuration. A **service** is the stable capability and
contract boundary through which one or more producers are invoked. A model is
an implementation artifact, not the service address. These are separate identities.

| Producer kind | Example output | Boundary |
|---|---|---|
| FORECASTER | Binary event probability or future distribution | Existing FF remains the specialized probabilistic/event subsystem. |
| CLASSIFIER | Independently defined regime category | Hard labels need not supply probabilities. |
| REGRESSOR | Future realized volatility estimate | Units, target measurement and maturity must be explicit. |
| RANKER | Ordered candidate set | Freeze universe, ties, target utility and evaluation window. |
| LLM | Structured claim or evidence-linked interpretation | Ambiguous prose is not an evaluable claim by default. |
| AGENT | Specialist stance plus factual support | An opinion/confidence is not silently mapped to event probability. |
| RULE_ENGINE | Deterministic threshold/event claim | Preserve rule and input versions. |
| ENSEMBLE | Composed claim | Preserve members, combination policy and synthesizer identity. |
| HUMAN_ASSISTED | Reviewed structured claim | Preserve human/advisor roles and attestation; do not invent model artifacts. |

No common `predict_proba()` or common training method is required. A service
declares inference/output capabilities separately from optional training,
diagnostics or calibration capabilities. Read-only inference cannot trigger those
administrative capabilities.

Illustrative future services (not registrations): `DirectionalForecastService`
wraps FF; `RegimeDetectionService` classifies regimes; `VolatilityForecastService`
emits numeric/interval claims; `SectorRotationService` emits comparative context;
`CandidateRankingService` ranks a fixed universe; `OptionsIntelligenceService`
separates underlying claims from expression advice; `MacroIntelligenceService`
provides contextual claims; `LLMReasoningService` provides structured reasoning.
One service may compose multiple producers; one producer may serve several
capabilities. Neither multiplicity implies multiple hosts.

### 4.2 Logical request/result boundary

Proposed minimum logical envelope, to be frozen in Phase II:

| Part | Required meaning |
|---|---|
| Service descriptor | Service ID, contract/capability versions, producer kinds, supported claim/target schemas, replay class and explicit limitations. |
| Admitted request | Request/correlation identity, caller scope, capability, subject or frozen universe, question/target, horizon, information cutoff, as-of, realization mode, evidence references, producer/version binding, budgets and deadline. |
| Result | Exact request binding, actual service/producer identity, status, primary claim when evaluable, optional secondary claims, evidence, explanation, separate advice, lineage, clocks and usage. |
| Absence/error | Typed unsupported, unavailable, timeout, rejected, ambiguous or insufficient-evidence state; never a fabricated zero, probability or neutral success. |
| Operational metadata | Health, endpoint/deployment revision, latency, retries and cost; separated from scientific meaning and authority. |

Inputs/outputs use existing frozen contract conventions: timezone-aware clocks
normalized with `ZoneInfo("Asia/Kolkata")`, ISO-8601 `+05:30` JSON, reject naive
datetimes, immutable semantic collections represented as tuples and JSON arrays.
Metadata can stay extensible but cannot conceal identity, claims, grants or
unvalidated executable instructions. All external values are validated at admission
and again at the capture boundary; caller-supplied identity is not attestation.

Preserve historical clock semantics: `information_cutoff <= as_of <= computed_at`
for the existing FF path, plus acquired/available/persisted/outcome clocks where
relevant. SIMULATED historical inference must not masquerade as ACTUAL issuance
before an outcome. Clocks are evidence, not retroactive availability rights.

### 4.3 Identity and versioning

| Identity | Carries | Change rule |
|---|---|---|
| ServiceIdentity | Logical service ID + semantic contract/capability versions | Stable across host moves; incompatible contract requires explicit new version. |
| ProducerIdentity | Producer ID/kind + implementation version + owner | Change when meaning/implementation changes; not merely a DNS change. |
| ModelIdentity | Family/model ID, model version, artifact digest where obtainable, configuration, feature/preprocessor references | No mutable `latest` binding in a historical claim. |
| TrainingIdentity | Existing candidate/experiment/request/execution/artifact lineage and rights scope | Refer to FLC records for FF; do not recreate them with a new namespace-only identity. |
| LLMIdentity | Provider, requested model, observed model/revision or explicit UNKNOWN, prompt/template, tools, orchestration and decoding configuration | Prompt/tool/policy changes affecting interpretation create new bindings; aliases are not proof of immutable weights. |
| InvocationIdentity | Request, semantic input digest, selected generation, captured response and attempt lineage | Retries are attempts of a bound request, not new independent scientific observations. |
| DeploymentIdentity | Endpoint, process/container/build revision, authentication principal and health | Operational identity retained separately; cannot override model/producer identity. |
| ClaimIdentity | Producer output + exact target/value/horizon/resolution policy + provenance references | Append-only; a revision gets a new identity and explicit supersedes link. |

Use existing artifact-reference and semantic-fingerprint patterns. Freeze the
new canonicalization domain in Phase II rather than changing a legacy digest.
Package release version, contract schema version, producer/model version and
deployment generation remain separate concepts; one cannot stand in for another.
Model/provider secrets never enter identity documents. A digest proves content
consistency, not authenticity, data rights, calibration, approval or availability.
Opaque external models declare the limit: retain requested/observed identity and
captured bytes, but do not claim weight custody or reproducible regeneration.

## 5. Typed claims and interpretation

### 5.1 Bounded ontology

The proposed initial ontology has seven kinds. Final schemas, score profiles and
supported subsets are Phase II decisions; unsupported kinds fail explicitly.

| Kind | Illustrative claim | Frozen resolution semantics and measurement boundary |
|---|---|---|
| BINARY | `P(high reaches reference * 1.05 within 15 sessions) = 0.68` | Event definition, probability vs hard assertion, reference basis, inclusive window, price field and complete observation policy. Binary probability loss only for declared probabilities. |
| NUMERIC | Predicted end-window return `0.03` | Units/fraction convention, reference and terminal prices, adjustment basis, horizon. Numeric error, not hit-probability scoring. |
| CATEGORICAL | Regime `RANGE` | Closed label vocabulary, independent label policy, time window; optional probability vector is a separately validated representation. |
| ORDINAL | Relative strength `HIGH` on an ordered scale | Ordered vocabulary and independently defined realization/rubric. Do not equate an arbitrary category distance with financial utility. |
| RANKING | `[candidate-A, candidate-C, candidate-B]` | Immutable universe, eligibility, ties, ranking objective and outcome window. No evaluation on only survivors. |
| INTERVAL | Return in `[0.01, 0.05]` at declared coverage | Ordered finite bounds, units, coverage level and predictive-vs-parameter interval meaning. Coverage and width belong to a pinned interval profile. |
| EVENT_TIME | First target touch time within a window | Event definition, time origin/resolution, observation and censoring rules. No hit is censored/defined absence, not an invented timestamp. |

These values are **illustrative engineering examples**, not live forecasts,
empirical results, parameter choices or recommendations. A contemporaneous regime
description also needs an independent reference labeling policy if evaluated;
future maturity is not forced onto a claim whose target is present state.

A claim binds: claim/producer IDs, subject/universe, value kind/representation,
units, target ID/version, reference evidence, horizon/calendar/maturity rule where
applicable, resolver ID/version, information and publication clocks, realization
mode, evidence-use scope, lineage and expected evaluation profile. Missing
resolution semantics means NON_EVALUABLE or rejection, never an implicit default.
Finite-value, range, category, interval, duplicate and schema checks are mandatory.

### 5.2 Primary, secondary and non-claim content

For an **evaluable forecast response**, exactly one designated primary claim is
required. Secondary claims are optional and separately identified. Multi-target
requests can return a bounded collection of such response units; a versioned
aggregate specifies which scientific question is primary before outcomes.

An explanatory-only response, abstention or service failure need not manufacture
a primary claim; it is explicitly non-evaluable and still recorded for coverage.
The request/protocol fixes primary-target selection, not an evaluator choosing
the best-looking claim later. Secondary scores remain separately labeled;
multiplicity and comparison rules must be specified before scientific conclusions.

```text
TI response
  primary claim       -> one defined scientific question -> its resolver/score
  secondary claims    -> separately identified questions -> separate scores
  evidence            -> immutable supporting/contradicting facts + references
  explanation         -> attributable interpretation, not automatic truth target
  recommendation      -> separate proposed action; TM retains authority
```

`BUY`, `SELL`, `HOLD`, `ENTRY`, `STOP`, `TARGET`, `MAINTAIN`, `PROTECT` and
`EXIT_RECOMMENDED` are not themselves probabilities or market outcomes.
A target level used in advice becomes an evaluable event only through an
explicit, prospectively frozen event claim. Preserve `WAIT`, `NO_TRADE`, dissent
and insufficient evidence rather than coercing every response into a trade.

### 5.3 LLM-assisted classification and direct LLM claims

Use deterministic templates for known structured requests. Astra may assist in
classifying an ambiguous query, extracting candidate targets/horizons, explaining
evidence or proposing a schema mapping. The validated request/claim must exist
before any applicable outcome is visible to that production flow. Material
ambiguity requires clarification or explicit non-evaluable status; the LLM cannot
silently choose “touched intraday” when the user meant “closed above at horizon.”

Direct Astra claims need the same identity, time, target, horizon, resolver,
evidence and immutable capture as model claims. An LLM's stated confidence is
not empirical calibration and an agent's policy confidence is not event
probability. Store the original response plus the normalization policy/result;
do not repair historical claims by rerunning a newer prompt.

## 6. Astra roles and deterministic boundaries

| Astra / LLM may assist | Deterministic or separately governed owner remains |
|---|---|
| Query interpretation and typed-claim extraction | Request validation, permitted ontology, clarification and capture |
| Evidence-linked thesis and multi-producer synthesis | Contributor lineage, conflict preservation, schema and budget admission |
| Human-readable explanation | Persisted claims/facts, not private reasoning as an audit dependency |
| Performance decomposition and drift hypotheses | Qualified cohorts, independently computed metrics and actual drift tests |
| Diagnostic reasoning and improvement proposals | Learning proposal records, data-use checks, authorized training and independent acceptance |
| Direct structured prediction | Immutable producer identity, truth resolution and objective Evaluation |

Producer role and diagnostic-reasoner role have separate IDs/role labels and
permissions. A diagnostic prompt consumes an authorized, frozen report; it may
not browse protected outcomes, change the population or promote its own producer.
Evidence/tool text is untrusted data, not authority-bearing instructions. Use
existing reasoning/evidence gateways, bounded tool scopes and usage accounting.
Do not embed OpenAI/Yahoo/MCP SDK types in specialists or domain contracts.

Persist prompts/templates, visible structured outputs, relevant supplied tool
results and version/configuration references subject to retention/data rights.
Do not require private chain-of-thought. Objective score reproduction uses the
captured claim, qualified truth and pinned deterministic Evaluation implementation
and must not call the original LLM. Repeating stochastic inference is a different
operation and is not promised to be byte-identical.

For implementation planning, Astra High and Extra High are the recommendations
in §15, not runtime model requirements. Official OpenAI documentation lists
`high` and `xhigh` reasoning settings and describes model snapshot pinning.
This design still requires actual observable provider identity; it does not
invent a dated snapshot or assume a model alias is immutable.
[OpenAI GPT-6 Astra model documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
(checked 2026-09-23). Effort recommendations are engineering judgment, not a
measured accuracy/cost comparison or a claim about this account's availability.

## 7. IFL components, capture and durable state

IFL is a cross-producer feedback layer assembled around existing responsibility
owners. The following are future responsibilities, not six new microservices.

| Component | Responsibility | Reuse / limit |
|---|---|---|
| Claim Capture | Validate exact request/result/identity/claim bindings; record issuance, abstention, rejection and failures; retain evidence and contributor references | Extend existing capture conventions; never rewrite native FF or agent records. |
| Claim Ledger | Append immutable claim and response records, deduplicate requests, track supersession and resolution/evaluation links | Additive store codec/boundary; durable transaction design required before operational guarantees. |
| Outcome Scheduler | Identify claims eligible for resolution, submit bounded work, record attempts, recover overdue work | Reuse eventual monitoring/job substrate; it does not own truth or force one-future-timestamp semantics. |
| Ground Truth Resolver | Resolve typed targets using qualified observable evidence and pinned independent rules | Existing Evaluation/Ground Truth owner; new resolver profiles only as separately accepted. |
| Evaluation + Performance Memory | Independently score aligned claims/truth, preserve coverage, maintain longitudinal versioned projections | Evaluation owns metrics; Memory indexes its immutable results, not a rival evaluator. |
| Learning Coordinator | Inspect qualified history, commission bounded diagnosis, issue improvement/retraining proposals | Existing Learning/lifecycle owners perform authorized work; coordinator contains no training algorithm. |

### 7.1 Claim Ledger and capture commitment

Capture native result bytes/reference, normalized claims and adapter version,
request/selection/budget bindings, contributors, provenance and capture receipt.
Claim records are immutable; resolution, evaluation and correction records append
links rather than editing the original. Persisted native evidence and its wrapper
have distinct identities, with a verified mapping between them.

For future durable service operation, do not report a claim as “recorded” until
the capture commitment succeeds. If the response arrived but persistence failed,
return an explicit unrecorded/failed-capture outcome and retain the recoverable
attempt under an approved policy. Exactly-once network execution is not assumed;
one committed scientific observation is enforced by ledger identity/idempotency.
Atomic commit, crash recovery and concurrent-writer tests are prerequisites to
that promise, not properties inferred from today's filesystem store.

Future state projection (events remain append-only):

```text
received -> validated -> recorded -> pending maturity -> resolving -> resolved
    |           |                            |              |
 rejected   non-evaluable                 overdue       pending / censored /
 / failed   / abstained                                 ambiguous / ineligible
                                                               |
                                  eligible resolved truth -> evaluated
                                                               |
                                                   performance projection

truth correction -> new linked truth revision -> new evaluation/projection version
claim correction -> new claim + supersedes link; original remains queryable
```

Statuses distinguish missing, pending, censored, invalidated and ineligible
outcomes; none is silently a false binary label. Scheduler attempt status and
claim scientific state are separate. Retired producers' pending claims still
mature and their history remains attributable under retention policy.

### 7.2 Clocks, scheduling and Ground Truth

A resolution contract pins target semantics, eligible outcome sources, observation
basis, event/window boundaries, calendar/version, earliest observability,
finalization delay/deadline, censoring and revision policy. Acquired-at and
available-at are not interchangeable. Persist outcome event/observation time,
source availability, acquisition, resolution and recording clocks.

| Target | Resolution approach | Failure or ambiguity |
|---|---|---|
| Target reached within a horizon | Observe the whole admitted window or a validated first-hit event. A positive hit may be known early under policy; a negative requires complete eligible coverage through the end. | Missing bars cannot establish no-hit. Intrabar order, high-vs-close, adjustments and exchange sessions must be explicit. |
| End-horizon direction | Compare qualified terminal and reference closes using the exact target rule | No substitution of a convenient nearby timestamp or a wick touch. Preserve existing FF equality/endpoint semantics. |
| Numeric horizon return | Compute pinned return definition from qualified reference/terminal values | Units, corporate actions and missing terminal evidence remain explicit; no default zero return. |
| Regime category | Apply an independently versioned labeling policy to its declared measurement window | Not agreement with the producer's own label. Proxy/rubric truth is labeled as such, with uncertainty; unresolved ambiguity remains unresolved. |
| Ranking / interval / event time | Use the corresponding frozen universe, target or censoring contract | Require separately accepted resolver/metric profiles; not implemented by this design. |

The scheduler schedules **eligibility to try**, not guaranteed truth. Delayed
sources yield pending/overdue states; late resolutions preserve actual clocks.
Revision policy prevents silent replacement of already-scored truth. PIT-safe
source semantics, corporate-action basis and evidence-use qualification remain
mandatory. Historical backfills never acquire prospective status merely because
they were just captured locally.

Resolver independence means common target rules and qualified source selection
outside the producer. It need not mean a different process. A resolver may later
be a logical/network service, but its authority, version and raw evidence must
remain inspectable; an LLM deciding whether its own narrative was right is not
an objective resolver.

## 8. Independent Evaluation and Performance Memory

Service-local evaluation answers “does this artifact behave as intended?” using
training/validation diagnostics, solver health, feature checks, calibration
diagnostics and family-specific tests. It is necessary but not sufficient.
Common Evaluation answers “how did these issued claims perform against the
declared real-world target on an eligible population?” independently of internals.
A service cannot be the sole judge of its production performance.

Reuse FLC Evaluation identity/pairing/coverage and immutable metric references.
Add heterogeneous metric profiles only when their claim and truth contracts are
accepted. Do not force ranks into binary labels or score an ordinal output as a
probability. Do not compare different horizons, target definitions, price bases,
realization modes or evidence populations as a paired benchmark.

Performance Memory is a durable, rebuildable projection over immutable records:

```text
claim + truth revision + evaluation protocol + population/membership
                    -> Evaluation result reference
                    -> versioned Performance Memory projection
                    -> authorized dashboard / diagnosis / proposal inputs
```

Index by service, producer, model/version, claim/target, horizon, instrument,
sector, regime, evaluation period and evidence-use class. Sector/regime slices
must declare whether membership was known at issuance or is an ex-post diagnostic;
future knowledge cannot enter historical selection features. Preserve retired
versions, replacements and synthetic/empirical distinctions, not one rolling
“current model accuracy” number.

Every aggregate exposes membership/protocol/projection versions; eligible,
issued, abstained, failed, unresolved, matured and scored counts; exclusions and
reasons; sample/time coverage; uncertainty where the accepted method supports it;
and metrics only for compatible targets. Small or selection-biased samples do
not become promotion evidence. Do not invent universal minimum samples or drift
thresholds; freeze them per approved protocol before adaptive use. Show missing
and unpriced usage explicitly rather than reporting zero cost.

Selection policies can change the observed population. Log eligible alternatives
and selection reasons where authorized, report availability/selection bias, and
distinguish descriptive history from independently qualified comparative evidence.
Protected evaluation partitions are not a training or diagnostic prompt pool.
Corrections generate new projections without destroying the prior report.

## 9. Learning Coordinator and governed improvement

The coordinator emits attributable proposals, not parameter mutations.

```text
qualified evidence minimum met
      AND (age condition OR drift OR degradation OR governed manual trigger)
                            |
                   versioned proposal + evidence
                            |
              authority / rights / budgets / partition admission
                            |
              owning service lifecycle -> candidate vNext
                            |
               independent validation + baseline comparison
                            |
             governance: reject / defer / approve separate activation
```

Sample adequacy and conditions are policy inputs TBD per use case, not arbitrary
numbers added here. Time alone does not justify a fit with insufficient data.
A manual trigger does not bypass evidence or rights gates. An emergency safety
action such as suspending a producer follows separate operational governance,
not an exception that permits under-qualified retraining.

Proposals pin the diagnosed version, target/population, supporting Evaluation
references, trigger policy, requested change, permitted evidence scope, cost
envelope and expected validation/rollback criteria. LLM hypotheses remain
hypotheses. Authorized service-specific work owns features, solver, tuning,
artifacts, diagnostics and candidate identity. FF services continue through the
same FLC request/execution/result/persistence owners, not “trainer number two.”

Every accepted fit/change creates a new version; the deployed artifact is never
mutated in place. Selection is not approval; approval is not activation; a
successful synthetic test is not empirical validation. Independent comparison,
rights review and deployment acceptance precede activation. The coordinator
cannot grant FF-2 use authority, reopen consumed 2025 or treat a previous grant
as permission for another experiment.

## 10. Multi-producer orchestration, agents and synthesis

Extend the existing Planner/workflow boundary after authorization; do not add a
parallel generic dispatcher. Capability/target compatibility, allowed evidence,
deadline/cost, lifecycle admissibility and explicit absence determine the plan.
Producer selection and fallback policy are versioned and captured before outcomes.

Illustrative response lineage (no current registrations implied):

```text
Regime producer/version    -> categorical claim + evidence ----\
Sector producer/version    -> ranking/context + evidence ------+-> TI synthesis
FF producer/model/version  -> binary claim + evidence --------/        |
                                                                      v
LLM/synthesizer identity + prompt + combination policy -> explanation and/or
                                                       NEW synthesized claim
                                                                      |
                               TI result retains ALL contributor claims,
                               dissent, absences and synthesis derivation edges
```

If synthesis only explains existing claims, it does not own a new scientific
target. If it emits a new evaluable claim, that claim has its own producer and
resolution contract plus derivation edges to contributors; evaluate it separately.
Do not assign the synthesizer's success/failure to every input producer or count
copied/reused claims as independent samples. Independence assumptions between
producers require evidence; shared sources/models can create correlated errors.

Existing `AgentOpinionV2` stances, confidence basis, baseline agreement,
contradictions and evidence remain intact. Adapter projections are lossless and
refer back to the original. A3 evidence interpretation, A4 arbitration, A5
position advice and A6 expression evaluation keep their present boundaries.
IFL feedback does not automatically retune A2 or alter A4/A5/A6 policy. A2 remains
the replayable benchmark, not an output to optimize for attractive examples.

## 11. TM and Workflow App boundaries

```text
TI claim -> TI/A6 advice -> TM authority/risk/capital decision -> broker execution
    |                            |                                  |
    v                            \-------- trade/order/fill IDs <---/
market outcome -> claim Evaluation             |
    |                                TM position/P&L lifecycle
    \--------- explicit lineage links ---------/
              NOT a shared scoring target
```

A directional claim can be correct while a call option loses because of time
decay, volatility change, spread or execution timing. Claim accuracy, expression
quality and realized trade P&L are distinct measurements. Future trade-action
evaluation must specify costs, sizing, execution assumptions, counterfactual
limits and TM-authoritative outcome links; it cannot be smuggled into the
forecast loss function. No current TM adapter or broker operation is added.

A future unified **Workflow App** consumes stable TI results and separately
authorized TM operational views. It can show claim/value kind, target/horizon,
producer/model/prompt identity, evidence, dissent, resolution status, qualified
performance, cost/freshness and advice-versus-authority. It must not depend on
Logistic/NN internals, prompt source code or deployment topology to interpret a
claim, and never receives broker/provider credentials from TI.

Illustrative view, not an implemented UI:

| Item | TI intelligence view | TM operational view |
|---|---|---|
| Candidate | Primary claim, secondary context, expiry, evidence, unresolved conflicts | Intake/eligibility and whether any action is authorized |
| Position | Captured assessment/advice, as-of and limitations | Authoritative quantity, orders/fills, risk/capital and reconciled state |
| Performance | Versioned claim/truth metrics and sample qualification | Execution and position outcomes, not relabeled forecast accuracy |
| Failure | Unavailable/stale/not-evaluable with reason | Own safe operation and reconciliation; no inferred approval |

Workflow App is a presentation/integration consumer, not the IFL ledger. Shell,
web and later consoles should use the same admission/result boundary, not each
reimplement service selection or scoring.

## 12. Local, remote and deployment architecture

```text
                    SAME logical Intelligence Service contract
                                     |
                     +---------------+---------------+
                     |                               |
               LocalAdapter                    RemoteAdapter (future)
                     |                               |
              existing TI owner             authenticated transport binding
              or local component                  HTTP / gRPC TBD
                                                     |
                                    local process / container / remote host /
                                      cloud / external provider boundary

Both -> canonical validated result + actual identity + capture + typed absence
```

Near term: service-oriented logical architecture in mixed in-process/local
deployment. A separate process is justified by isolation, independent releases,
credentials, incompatible dependencies or measured resource requirements—not the
number of boxes. Future deployments may mix direct calls, local hosts, containers,
separate machines, cloud services and third-party APIs. Kubernetes, service mesh,
distributed cache and model-registry products are not prerequisites.

### 12.1 Semantic invariant and transport controls

With the same admitted semantic request and pinned producer/artifacts/policies,
moving location must preserve the meaning of identity, claim, truth and Evaluation.
Endpoint and latency are operational facts, not a new scientific target. Transport
can affect availability, deadlines, freshness and cost; expose those differences.
Do not promise bitwise repeatability for stochastic or opaque inference.

| Concern | Future design requirement |
|---|---|
| Discovery | Start with explicit COLD allowlisted bindings. Descriptor states capabilities/versions; discovery grants neither execution nor evidence use. |
| Endpoint identity | Bind authenticated service principal and deployment generation separately from producer/model identity. Do not trust a URL or claimed model name alone. |
| Version negotiation | Require compatible contract/capability and target schema before dispatch; pin actual producer generation for the full request. Unknown fields cannot change meaning silently. |
| Authentication / authorization | Scoped principals, transport protection, per-call capability/evidence/tenant checks and revocation policy; credentials stay out of records. Local linking is trusted code, not a security sandbox. |
| Deadline / cancellation | Bound connect/read/total time and request budgets. Cancellation may not stop remote compute; record unknown completion and usage instead of assuming zero cost. |
| Retry / idempotency | One logical request key bound to payload digest, principal scope and producer generation; bounded attempts. Changed payload under same key is a conflict. Provider without idempotency cannot be promised exactly-once inference. |
| Circuit / fallback | Bounded circuit policy, explicit failures and permitted fallback only. Another model is a new attempt/producer binding, not equivalent output hidden under the original identity. |
| Health / staleness | Distinguish reachability, readiness, version compatibility, lifecycle admissibility and data freshness; healthy endpoint does not imply usable evidence. |
| Observability | Correlation/parent-child IDs, attempts, model/tool usage, latency, result/capture status and safe errors. No keys, private data dumps or fabricated cost zeros. |
| Resource/privacy limits | Bound request/response sizes, concurrency, calls/tokens/cost, data export rights and retention. Reserve budgets across attempts; deny unauthorized evidence egress. |
| Replay | Local archived records/codecs only; replay never calls a remote service to fill a missing artifact. |

Moving a binding is a governed composition/deployment change. COLD remains the
default; an endpoint changing model mid-request is a mismatch, not HOT support.
Remote administrative training/promotion APIs are out of this initial contract.

### 12.2 Registry recommendation

Use a small, versioned **metadata view** over existing capability descriptors,
COLD composition and FLC model/candidate/training identities. Add service and
endpoint bindings only where absent. Do not create a second authoritative model
registry or dynamic plugin loader. Distinguish descriptive “known,” bound,
available, validated, approved, active and retired states.

The view may join descriptor, owner, contract, producer/model versions, optional
artifact custody, permitted capabilities, lifecycle-record references, endpoint
generation, replay class and retention constraints. Activation still requires
the separately trusted authority path; a metadata edit cannot activate a model.
No MLflow/Kubeflow or comparable product is selected without concrete operational
needs. Multiple service-local stores are possible, but TI must retain sufficient
authorized capture/lineage for independent evaluation and offline recorded replay.

## 13. Failure, degradation and replay

| Failure | Required behavior | Acceptance probe before that capability ships |
|---|---|---|
| Remote unavailable | Explicit unavailable; no fabricated neutral answer; optional admitted fallback retains new identity | Unreachable endpoint yields typed absence with bounded attempts. |
| Timeout / unknown remote completion | Record deadline and ambiguous completion/cost; reconcile by request identity if supported | Late response cannot become an unnoticed second claim. |
| Retry duplicates | Deduplicate committed scientific result; preserve attempts | Identical key/payload cannot add independent samples; conflicting payload rejects. |
| Stale model/version | Reject incompatible binding; otherwise label permitted staleness explicitly | Old descriptor cannot satisfy newly pinned request. |
| Producer switches mid-request | Reject identity/provenance mismatch; require separately admitted new request/attempt | Descriptor/result generation mismatch fails closed. |
| Malformed result / invalid value | Reject invalid schema, nonfinite values, probability ranges or interval ordering | Zero remains factual zero; null is not silently substituted. |
| Ambiguous LLM claim | Clarify or record non-evaluable; retain original prose and normalization reason | Missing target/horizon cannot be retrospectively inferred from outcomes. |
| Missing / delayed truth | Pending/overdue/censored according to policy; coverage retained | No truth is not a negative label; late evidence has its real clock. |
| Duplicate source claim in synthesis | One original identity plus derivation links; no double-counted independent observations | Two aliases of same capture do not increase effective sample count. |
| Producer retired | Keep records, outstanding resolution and version-specific history | Archived claim remains readable without current registration. |
| Artifact missing | Recorded replay can display complete captures; reconstruction reports UNAVAILABLE where bytes are required | Identity-only reference cannot masquerade as artifact custody. |
| Provenance/result mismatch | Quarantine/reject; no ledger acceptance or silent remapping | Tampered producer/input/target binding fails validation. |
| Schema mismatch | Explicit UNSUPPORTED/incompatible; no lossy coercion | Old reader never treats new claim kind as binary. |
| Offline replay | Verify stored bytes/lineage without network; report mode-specific limits | Provider/model/network stubs fail if invoked. |
| Tampered ledger/evidence | Integrity failure and preserved incident; do not regenerate replacement content to hide mismatch | Byte/fingerprint mismatch surfaces even when JSON is parseable. |
| Prompt/version interpretation drift | New producer/config binding; preserve old capture and resolver | New prompt cannot rewrite old target or improve historical scores. |
| Capture persistence fails | No false “durably recorded” receipt; explicit failed/unrecorded result | Crash between response and commit cannot create a success-only ghost record. |
| Truth correction / split source authority | Append revision with source evidence and reason; version affected evaluations | Original evaluation and corrected projection both remain inspectable. |
| Permission revoked / evidence egress denied | Fail closed; retain only legally permitted audit metadata | Retries/fallback cannot evade use/tenant scope. |
| Performance cohort too small / biased | Descriptive or insufficient-evidence result, no silent selection/promotion | Dashboard displays coverage and qualification, not an unqualified leaderboard. |

Replay has separate promises: **recorded reconstruction** restores validated
captures; **deterministic verification** reproduces supported computations from
required pinned bytes; **stochastic inference re-execution** is not a replay
substitute. Objective Evaluation replay does not require original model weights
or LLM access once claim/truth/metric inputs are present. Missing Evaluation code
or truth bytes still yields explicit UNAVAILABLE/UNSUPPORTED, never a fabricated
MATCH. Preserve native FF/FLC replay statuses and add outer records rather than
retroactively changing old schemas or fingerprints.

## 14. Impact and compatibility assessment

Categories describe **future integration work**, not edits authorized now.
`NO_CHANGE` preserves frozen behavior; `COMPATIBLE_AS_IS` means ownership fits;
`MINOR_ADAPTER_NEEDED` means additive lossless projection; `FUTURE_EXTENSION_NEEDED`
means new bounded capability. `ARCHITECTURAL_CHANGE_REQUIRED` is reserved for a
demonstrated conflict; no inspected subsystem requires that classification.

| Area | Classification | Required future action / preserved guarantee |
|---|---|---|
| FF-0 | NO_CHANGE | Preserve target/clock/BaseRate/capture semantics; wrap existing records. |
| FF-1 | NO_CHANGE | Preserve all frozen files, artifacts, scientific conclusion and consumed-holdout restrictions; no new evaluation or training. |
| FLC | COMPATIBLE_AS_IS | Specialized FF lifecycle remains valid; governance and worker scopes unchanged. |
| Family-neutral inference | MINOR_ADAPTER_NEEDED | Map existing binary output/absence to typed claim envelope; no widening/reinterpretation of frozen output union. Other output kinds use separate accepted contracts. |
| FF-2 | NO_CHANGE | Future source only; raw/calibrated distinction and all authority HOLDs remain. |
| Ground Truth | FUTURE_EXTENSION_NEEDED | Reuse independent owner; add claim-kind resolver contracts/profiles, observability and revisions without replacing endpoint resolver. |
| Evaluation | FUTURE_EXTENSION_NEEDED | Reuse metrics/pairing/coverage owner; accept new target-aligned profiles and longitudinal projections separately. Existing normalized executable authority stays synthetic. |
| Replay | MINOR_ADAPTER_NEEDED | Add service/claim capture and wrapper verification using existing patterns; remote/stochastic regeneration is not required for recorded replay. |
| Provenance | MINOR_ADAPTER_NEEDED | Add service, contributor and synthesizer links in new versioned envelopes; keep FLC bounded DAG and native records intact. |
| Persistence | FUTURE_EXTENSION_NEEDED | Add Claim Ledger and Performance Memory codecs/boundaries; prove atomicity/recovery before multi-writer/durable scheduling claims. |
| Candidate/model identity | MINOR_ADAPTER_NEEDED | Reference FLC identities; add heterogeneous/opaque identity envelope with explicit missing custody. |
| Training identity | COMPATIBLE_AS_IS | Service ownership delegates FF work to existing request/execution/result lineage; non-FF training later needs its own accepted adapter, not a universal trainer. |
| Calibration | COMPATIBLE_AS_IS | Preserve RAW probability and calibrated wrapper/identity; IFL must not label self-confidence as calibrated. No new fits or empirical grants. |
| Current agent foundations | MINOR_ADAPTER_NEEDED | Preserve opinion/evidence/confidence/run records; project only explicitly evaluable claims. Reuse reasoning gateway. |
| Planner / orchestration | MINOR_ADAPTER_NEEDED | Extend existing capability planning and captured contributors; no parallel dispatcher or hidden policy tuning. |
| Facade / COLD composition | FUTURE_EXTENSION_NEEDED | Separately admit new service capabilities after foundation tests; current catalog remains nine. Optional remote transport needs security acceptance. |
| Future A8 TI/TM integration | FUTURE_EXTENSION_NEEDED | Add claim/result links and separate trade-outcome joins; preserve TM authority and broker truth. |
| Future Workflow App | FUTURE_EXTENSION_NEEDED | Consume stable result/status/performance projections; no implementation or delivery promise here. |
| Monitoring/runtime | FUTURE_EXTENSION_NEEDED | Reuse operational ownership for maturity attempts; durable recurrence remains A10 unless separately authorized earlier. |

**Compatibility decision:** current FF, FLC and FF-2 are compatible. No existing
work is invalidated. Required changes are additive heterogeneous envelopes,
adapter mappings and later ledger/resolver/evaluation/operational capabilities.
No frozen producer must adopt the complete ontology to remain useful.

## 15. Phased work plan and implementation timing

Major order remains A7 → A8 → A9 → A10. IFL is cross-cutting, not a replacement
FF stage or an automatic renumbering of milestones. FF-2's empirical HOLD is a
parallel authority condition, not permission to train through IFL. Recommended
Codex models below are planning guidance, not runtime dependencies or approvals.

### Phase I — Now: architecture and impact analysis only

- Purpose: establish the boundaries in this document.
- Dependencies: inspected frozen FF/FLC, FF-2.3, system/deployment/monitoring plans.
- Deliverables: this design, impact matrix, invariants, risks/TBDs and navigation.
- Tests/gates: source traceability, link checks, documentation diff/scope review;
  no claim that documentation proves runtime behavior.
- Non-goals: all fitting, services, runtime, scheduler and empirical-use changes.
- Recommended model: GPT-6 Astra **Extra High**, for cross-owner reconciliation.

### Phase II — Late A7 / A7-to-A8 boundary: minimum foundation

- Purpose: make generic intelligence capture possible without replacing FF.
- Dependencies: separate scope approval; review/freeze the initial contract
  subset, identity/canonicalization and exact reuse of store/owner seams.
- Deliverables: versioned ProducerIdentity/ServiceIdentity, typed response/claim
  and resolution references, service descriptor/request/result, LocalAdapter
  and transport-neutral RemoteAdapter interface only, minimal Claim Ledger
  boundary; one synthetic existing-FF binary mapping end to end.
- Tests/gates: immutable/list/JSON and Asia/Kolkata round trips; exact native FF
  preservation; claim/request/version mismatch rejection; zero live/network/model
  calls in replay; duplicate semantics; non-evaluable/absence handling; scoped
  authority denial. A test double may prove local/remote contract parity without
  a real endpoint. Unsupported claim kinds must reject, not coerce.
- Non-goals: all seven resolver implementations, empirical fitting, actual remote
  hosting, generic model registry, autonomous learning or public live exposure.
- Recommended model: GPT-6 Astra **High**; Extra High for independent acceptance
  if unresolved identity/clock or ownership conflicts remain.

Exit: a separately accepted bounded foundation, not “IFL fully implemented.”
Complete this before A8 promises generic claims. Unrelated existing captured-read
TI/TM design exploration need not wait for every future IFL capability.

### Phase III — A8 integration, with explicit A10 operational gate

- Purpose: integrate admitted claim capture, outcome links and useful visibility.
- Dependencies: Phase II, separately admitted A8 TM boundary, evidence-use and
  privacy scopes, accepted resolver/metric subset and capture durability profile.
- Deliverables at A8: bounded/event-driven or explicitly invoked capture and
  maturity-resolution work; independent Ground Truth integration, initial
  Performance Memory projections, existing-orchestrator adapters and stable UI
  view contracts. Workflow App implementation requires its own scope acceptance.
- Durable recurring scheduler/delivery/recovery remains A10 under the monitoring
  roadmap. If A8 needs it, approve a minimum local slice with admission, durable
  attempts, idempotency, budgets, recovery and calendar gates first; do not claim
  operational completeness from a timer or an in-memory queue.
- Tests/gates: delayed/missing/revised truth, complete-window negative resolution,
  PIT clocks, paired population/coverage, permission boundaries, broker-vs-market
  outcomes, unavailable TI behavior and offline projection reproduction.
  Any early durable slice also needs restart/concurrency/duplicate tests.
- Non-goals: auto-training, automatic producer selection by performance, broker
  execution, full UI build or mandatory network/cloud migration.
- Recommended model: GPT-6 Astra **High** for bounded adapters; **Extra High**
  for authority, scheduler and independent outcome acceptance review.

### Phase IV — Qualified diagnosis and proposal generation

- Purpose: use history to explain failures and propose governed improvements.
- Dependencies: enough qualified independent evidence under accepted protocols;
  scoped diagnostic access, predeclared thresholds and protected-partition barriers.
- Deliverables: performance decomposition, accepted drift signals, optional
  LLM-assisted diagnoses, versioned retraining/improvement proposal records and
  evidence-threshold policy; service lifecycle handoff, not embedded fitting.
- Tests/gates: insufficient samples, unauthorized/consumed partitions, diagnostic
  prompt drift, reproducible numeric reports, proposal deduplication and proof
  that proposals cannot activate, approve or mutate a producer.
- Non-goals: arbitrary thresholds, FF-2 rights bypass, autonomous promotion.
- Recommended model: GPT-6 Astra **Extra High** for scientific/authority design,
  **High** for implementation of already accepted bounded contracts.

### Phase V — Conditional mature multi-service operations

- Purpose: operate multiple independently versioned services and governed
  retraining where measured needs justify it.
- Dependencies: accepted A10 operational substrate, rights/security/retention
  review, service SLO evidence and explicit candidate/activation governance.
- Deliverables: necessary remote adapters/hosts, cross-service budget/health
  control, governed lifecycle automation and possibly evaluated ensembles or
  producer-selection policies. Use service-local implementations, common external
  evaluation and immutable candidate lineage.
- Tests/gates: version-switch, malicious/malformed remote response, timeout/unknown
  completion, duplicate delivery, retirement/rollback, recovery/load, multi-tenant
  isolation, cost accounting and local/remote semantic conformance.
- Non-goals: compulsory distribution, service mesh, self-approved deployment,
  replacing benchmark history or unrestricted online learning.
- Recommended model: GPT-6 Astra **High** for scoped transport work; **Extra High**
  for deployment threat-model and scientific/governance acceptance.

## 16. Architectural invariants

1. Every evaluable claim has an immutable, attributable producer/version identity.
2. Every evaluable claim has a typed target and resolution contract.
3. Every applicable claim pins its horizon, calendar and maturity/observability rule.
4. Historical claims are append-only; corrections never overwrite prior meaning.
5. Ground Truth is attached only when observable under the declared evidence policy.
6. LLM reasoning cannot rewrite historical claims, outcomes, cohorts or metrics.
7. Services/models can evolve independently behind versioned contracts.
8. Retraining and material configuration changes create new candidate/model versions.
9. Production artifacts and their identity bindings are never silently mutated.
10. Approval, promotion and activation remain separate governed decisions.
11. Common outcome measurement is independent of producer internals.
12. Local/remote movement preserves scientific meaning and explicit absence semantics.
13. Network transport cannot silently change claim/target/evaluation semantics.
14. Performance history survives producer replacement and retirement under retention policy.
15. Existing FF scientific history, fingerprints and consumed-holdout status remain immutable.
16. Synthesized results preserve all contributing identities, outputs, dissent and derivation.
17. A service is not the sole judge of its own production effectiveness.
18. IFL proposes adaptation; it does not silently change producers or execute training.
19. Objective Evaluation is reproducible without invoking the original LLM.
20. Deployment topology is orthogonal to scientific identity; operational provenance is retained.
21. Primary claims and comparison rules are designated before outcomes; secondary claims cannot be cherry-picked into success.
22. Probability, confidence, explanation and trade advice are not interchangeable.
23. Missing/ambiguous/censored/invalid evidence never becomes a fabricated zero or negative label.
24. Captured output replay and numerical regeneration are distinct guarantees.
25. Descriptor, fingerprint, lifecycle label and good performance do not grant data-use or execution authority.
26. Synthetic, historical-consumed and prospectively qualified evidence remain distinct through every projection.
27. Replay never acquires evidence, calls a producer, refits or silently loads a substitute implementation.
28. Semantic collections are immutable and clocks remain aware/canonical Asia/Kolkata.
29. Planner, Ground Truth, Evaluation, Learning and TM retain their respective ownership; no parallel engines are introduced by naming IFL.
30. No UI/session/conversation is the authoritative ledger or a source of operational grants.

## 17. Open decisions and risks

These are explicit design gates, not silently chosen defaults. The identifiers
below are local to this architecture and do not claim existing DEF register IDs.

| TBD | Decision still needed | Owner / earliest gate |
|---|---|---|
| IFL-T01 | Final ontology schema and first supported subset | Contract owner, Phase II |
| IFL-T02 | Deterministic classification vs LLM assistance and clarification policy | TI admission/agents, Phase II |
| IFL-T03 | Ground Truth rules/sources/revisions per claim kind | Ground Truth owner, II/III |
| IFL-T04 | Primary/secondary scoring and multiplicity semantics | Independent Evaluation, II/III |
| IFL-T05 | Fuzzy/ordinal reference rubrics and metrics | Independent Evaluation, before those kinds ship |
| IFL-T06 | Ranking utility, ties, universe and missing-member evaluation | Independent Evaluation, before ranking acceptance |
| IFL-T07 | Minimum qualified sample requirements | Research governance, IV |
| IFL-T08 | Time/sample/condition retraining policy | Learning + governance, IV |
| IFL-T09 | Drift/degradation thresholds and false-alarm treatment | Evaluation + governance, IV |
| IFL-T10 | Producer selection, fallback and ensemble policy | Planner/governance, II/III then V |
| IFL-T11 | LLM prompt/tool/version provenance granularity and retention | Reasoning gateway + custody, II |
| IFL-T12 | HTTP vs gRPC vs local IPC for justified deployment | Deployment owner, before remote implementation |
| IFL-T13 | Service discovery mechanism beyond COLD allowlist | Deployment/composition, V if required |
| IFL-T14 | Authentication, authorization, tenancy and revocation design | Security/authority owner, before remote access |
| IFL-T15 | Metadata registry projection/store implementation | Existing composition/FLC owners, II |
| IFL-T16 | Trade-recommendation evaluation distinct from forecasts | TI/TM + Evaluation, A8 or later |
| IFL-T17 | TM outcome links, corrections and access rights | A8 integration owners |
| IFL-T18 | Whether independent resolvers need service deployment | Ground Truth/deployment, III/V |
| IFL-T19 | Remote retirement, artifact retention and replay availability | Custody/deployment, before remote acceptance |
| IFL-T20 | Opaque external model pinning and unverifiable-version policy | Gateway/governance, II then remote acceptance |
| IFL-T21 | Ledger atomicity, crash recovery, retention and multi-writer profile | Persistence/operations, before durability promises |
| IFL-T22 | Missingness/selection-bias and adaptive-cohort reporting | Independent Evaluation, III/IV |
| IFL-T23 | Exact placement/acceptance of an early A8 scheduler slice, if needed | Monitoring/roadmap owner; otherwise A10 |

| Risk | Architectural control / residual limitation |
|---|---|
| Ontology becomes an unbounded universal framework | Small versioned subset first; unknown kinds explicit; no frozen-union rewrite. |
| Attractive explanations conceal weak science | Typed primary target, independent resolver, sample/coverage disclosure and abstention. |
| Learned feedback leaks protected evidence | Evidence-use scopes enforced at every owner; protected reports are not diagnostic/training input by default. |
| Selection creates a misleading winner | Freeze eligible populations/policies, retain failed/absent results and evaluate adaptivity separately. |
| Registry/IFL duplicates existing owners | Metadata projections and adapters; matrix in §14 makes ownership explicit. |
| Remote retries/capture races corrupt history | Idempotency plus atomic commitment and attempt lineage; no exactly-once network assumption. |
| External model or data disappears | Honest custody/replay modes and authorized retention; hashes alone cannot restore missing bytes. |
| Excessive infrastructure delays useful foundations | In-process first; distribution conditional on demonstrated needs. |
| Rights/privacy retention conflicts with immutable history | Authorized retention and metadata tombstone/redaction policy must be accepted; record loss of reproducibility rather than fabricate preservation. |
| Feedback interpreted as execution authority | Separate proposal/validation/approval/activation and TM boundaries throughout. |

## 18. Closure, readiness and next bounded decision

The complete architecture, compatibility assessment and phased plan are defined.
IFL is **NOT_IMPLEMENTED**. Current FF/FLC/FF-2 remain compatible; empirical FF-2
HOLD is unchanged. No runtime, HTTP/gRPC service, broker action, model fit,
protected evaluation, promotion, commit, tag or push is part of this pass.

`READY_FOR_FUTURE_IFL_IMPLEMENTATION = NO` means the broad runtime is not ready
to start under a frozen implementation contract or granted execution scope.
The design is ready for review and a separately authorized **Phase II minimum
foundation** specification. That narrower next step is not blocked on completing
every future TBD or resolving FF-2 empirical authority, because it can be strictly
synthetic and additive. It does not grant readiness for empirical use or A8.

```text
IFL_ARCHITECTURE_DEFINED = YES
INTELLIGENCE_SERVICE_ARCHITECTURE_DEFINED = YES
LOGICAL_SERVICE_MODEL_DEFINED = YES
NETWORK_SERVICE_MODEL_DEFINED = YES
LOCAL_REMOTE_ADAPTER_MODEL_DEFINED = YES
LLM_ROLE_DEFINED = YES
CLAIM_MODEL_DEFINED = YES
GROUND_TRUTH_MODEL_DEFINED = YES
PERFORMANCE_MEMORY_MODEL_DEFINED = YES
RETRAINING_PHILOSOPHY_DEFINED = YES
MULTI_PRODUCER_ORCHESTRATION_DEFINED = YES
CURRENT_FF_COMPATIBLE = YES
CURRENT_FLC_COMPATIBLE = YES
CURRENT_FF2_COMPATIBLE = YES
A8_INTEGRATION_DIRECTION_DEFINED = YES
WORKFLOW_APP_DIRECTION_DEFINED = YES
READY_FOR_FUTURE_IFL_IMPLEMENTATION = NO
```

**Recommendation: REQUIRES_PRE_A8_FOUNDATION_WORK.** This recommends the bounded
Phase II contracts/adapters/capture foundation before generic A8 service promises,
not architectural rework or permission to begin implementation now.

### Documentation validation for this pass

- Existing `docs.handbooks.a7_forecasting.validate_handbook.validate_links(True)`:
  PASS, 703 local links across eight Markdown files (the six changed/new files
  plus the validator's two fixed handbook/reference inputs). External URLs are
  not covered by this local-link check; the cited OpenAI page was checked separately.
- Markdown scope, final newline, trailing whitespace and balanced fenced blocks:
  PASS for all six changed/new files. All 17 final flags, 30 invariants and 23
  locally numbered TBDs are present. Plain-text diagrams require no Mermaid renderer.
- `git diff --check`: PASS. The untracked new document was also checked explicitly
  for whitespace; Git's ordinary diff does not include untracked content.
- `git diff --exit-code HEAD -- src scripts tests data docs/qualification_records`:
  PASS, unchanged. Working-tree inventory contains only this document and five
  Markdown navigation updates. HEAD remains the inspection baseline above.
- Runtime tests were not rerun: this is architecture/documentation-only work,
  not a new FF/FLC runtime acceptance or protected scientific evaluation.
