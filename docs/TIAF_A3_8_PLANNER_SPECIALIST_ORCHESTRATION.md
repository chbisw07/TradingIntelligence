# TIAF A3.8 — Planner + Specialist Orchestration

## Status and authority

Architecture and implementation passes, 2026-09-10. **Implemented; pending user
acceptance/freeze.** The base remains `tiaf-a3.7` (`dbcad3b`); the architecture
pass started from a clean tree. No commit/tag/push was performed.
A1/A2 and A3.1–A3.7 remain accepted inputs, not redesign targets. A3.7's
deterministic user-level acceptance is complete; its documented unsuccessful
Dhan acquisition is not converted into a live-acceptance claim here.

This is the authoritative design and implementation record for A3.8 under the
[A3 architecture](TIAF_A3_ARCHITECTURE.md) and
[detailed roadmap](TIAF_A3_DETAILED_ROADMAP.md). All new names and policies
below describe the approved design; section 17 maps it to available APIs and
bounded implementation choices. The implementation adds runtime code and an
optional pinned framework dependency, not a new provider, specialist policy,
model call or live market request. See the
[user-level study](STUDY_A3_8_USER_LEVEL_ACCEPTANCE.md) for current gate results.

## 1. Ownership and scope

**The Planner owns workflow decisions, not investment decisions.** It chooses
specialists, evidence requirements, dependency order, parallel groups, reuse,
bounded enrichment, confirmation, selective reruns, and termination. It records
why each choice was made. Specialists retain their independent interpretation
policies; the Market Intelligence (MI) fabric retains source routing.

It cannot decide BUY/SELL, a specialist winner, Technical versus Fundamental
precedence, CE/PE, expiry/strike/quantity, stop-loss/target, HOLD/BOOK/EXIT/PROTECT,
calibrated probability, or final arbitration. A2 scores/classes/direction and
`NO_TRADE` remain unchanged, including when specialists disagree. Coverage,
materiality, cost, and workflow status are not investment scores.

A3.8 is bounded in-process orchestration for a caller-selected subject. It
does not add a scanner, universe scheduler, position lifecycle, option-expression
selector, new specialist/provider, model-backed planner, graph database, or
production distributed service. A3.9 owns the public underlying-intelligence
product; A4–A10 remain pending. TI Shell/natural-language outer architecture
and Source/Provenance/Citation report fabric remain post-A3 topics. Existing
evidence attribution and audit preservation are required, not a new report fabric.

## 2. Reuse of implemented seams

| Existing boundary | A3.8 use and limit |
|---|---|
| `tiaf.agents.AgentRequest`, `AgentEvidencePack`, `AgentOpinionV2`, `AgentRunRecord` | Reuse unchanged for each specialist invocation; preserve cited detail and baseline comparison. An `AgentRequest` names exactly one specialist, not an entire workflow. |
| `AgentRegistry`, `SpecialistCapability`, `AgentRuntime` | Resolve registered implementations and execute one bounded invocation. Capability declarations do not yet encode cross-specialist dependencies. Runtime neither plans nor recomputes evidence fingerprints. |
| A3.2 `EvidenceGatewayRuntime`, `EvidenceGatewayRequest`, `A2EvidenceGateway` | Authorized evidence reads, immutable A2 pack reuse, typed results, cache and audit seams. A2 acquisition/calculation stays upstream. |
| `AgentBudget`, `AgentUsage`, `ReasoningGateway`, `ModelTier` | Existing vendor-neutral resource vocabulary and optional reasoning authority. Add aggregate orchestration accounting around them, not a replacement budget system. |
| `MarketIntelligenceRequest`, `MarketIntelligenceRouter`, `CapabilityRoutePolicy` | Fine-capability acquisition, normalization, native lineage, typed failures, per-capability fallback/enrichment and coverage. Provider choice stays inside route policy. |
| `MarketIntelligenceResearchController` and research request/run models | Reuse for pre-budgeted multi-capability acquisition; currently synchronous and requires a run for every requested capability. It is not a partial-result parallel executor. |
| `DeepResearchIntegrationController`, `DeepResearchContextPack`, `DeepResearchResult` | Reuse normalized research assembly, quality/PIT envelopes, epistemic separation, confirmations, graph integration and replay. `assemble` can reuse acquired records without calling `execute` again. |
| `AuthoritativeEscalationPolicy`, `AuthoritativeConfirmationGateway` and request/result | Reuse materiality gate, explicit discovered claims, field-level reconciliation, official lineage and bounded route policy. No general web tool. |
| `SparseEvidenceGraph` | Reuse point-in-time neighborhoods and immutable snapshot updates; no graph traversal agent or new graph engine. |

Source anchors: `src/tiaf/agents/{models,evidence,runtime,budget}.py`,
`src/tiaf/agents/gateways/`, `src/tiaf/market_intelligence/{routing,models,deep_research,authoritative,authoritative_models,graph}.py`.
`src/tiaf/planner/` and `src/tiaf/workflows/` now implement these seams.
LangGraph is pinned in the optional `orchestration` dependency extra and isolated
to `workflows/langgraph_adapter.py`.

### Request composition, not a second specialist request

Use a small framework-neutral **orchestration envelope**,
`OrchestrationRequest`, to supply the missing workflow controls. Reuse existing
types and derive ordinary `AgentRequest`s only after selection. Do not clone
all AgentRequest fields into a parallel specialist schema, pass a dummy
specialist, or overload `metadata` with the entire plan.

`OpportunityRequest` is a universe/top-N consumer contract, and
`MarketIntelligenceResearchRequest` is acquisition-only. Neither should be
repurposed as a cross-specialist workflow request. Existing request IDs may be
linked in the envelope without importing A4/A5/A6 decision authority.

| Envelope content | Representation and validation |
|---|---|
| Identity | Request/run/correlation IDs, optional parent request and replay-source run IDs. One canonical `Symbol` and existing `InstrumentType`; retain caller-supplied instrument/underlying references. |
| Objective and duration | `AnalysisPurpose`, task text, `TradeStyle`, `Horizon`. A positional example uses purpose `OPPORTUNITY`, style `POSITIONAL`, and structured duration; POSITIONAL is not an `AnalysisPurpose`. POSITION or OPTION_EXPRESSION labels do not authorize later-milestone actions. |
| Instrument/date context | Optional caller-selected expiry/date and explicit underlying/F&O-eligibility/mapping evidence references, including their effective dates. The planner never chooses a contract to fill a missing expiry. |
| Evidence inventory | References to available A2 contexts/packs, immutable deterministic assessment and fingerprint, normalized MI snapshots, prior specialist records, confirmations and graph snapshots. Resolve and validate referenced content before planning. |
| Depth and permissions | Existing `AnalysisMode` and `ResearchDepth`, explicit deep-research/authoritative-confirmation permission, allow-listed `AgentCapability` ceiling. Depth permits work; it never mandates expenditure or expands authority. |
| Limits and model policy | Aggregate `AgentBudget`, orchestration-only bounds below, no-LLM flag, allowed/max `ModelTier`. Deterministic-only policy cannot request a live model tier. |
| Time and replay | `as_of`, creation timestamp, optional deadline, and LIVE/CAPTURED/REPLAY execution intent. All use aware `TiafDateTime`; replay identity is separate from live-run identity. |

Use `ContractModel` validation, frozen fields, tuples for semantic collections,
ordinary list/JSON input and JSON-array output, and reconstruction tests.
Metadata remains simple, safe JSON-compatible extension data, not a mutable
policy channel. Copy/validate it at boundaries; semantic digests must detect
changes rather than relying on shallow `frozen=True` for deep immutability.
Canonical timestamps use `ZoneInfo("Asia/Kolkata")`, reject naive datetimes,
normalize other aware zones, and serialize with `+05:30`. No naive `now()` or
manual offset arithmetic. Package version `0.1.0`, base contract schema `1.0`,
existing `AgentOpinionV2` schema `2.0`, and planner/policy versions are distinct;
this design changes none of them.

## 3. Plan and record contracts

Planner contracts live in `tiaf.planner`, with no runtime-framework or
provider SDK types. They reference existing immutable evidence and Agent records.

- `AnalysisPlan`: plan ID/version/parent version, request digest, planner and
  policy version, registry/dependency-policy snapshot, selected and skipped
  specialists with reason codes, required/optional evidence predicates, DAG
  nodes/edges, stable parallel waves, acquisition/enrichment/confirmation nodes,
  depth, reservations, and stop bounds. Version 1 is never overwritten.
- `PlanDecision`: stable logical sequence, triggering evidence/claim/gap IDs,
  rule/version, action, reason, affected nodes, expected coverage contribution,
  prerequisite and budget disposition. Decisions include reuse and denial,
  not just successful actions.
- `OrchestrationRunRecord`: original request and all plan versions, input
  inventory snapshots/digests, decisions, per-node attempt/result/status,
  constituent gateway/MI/confirmation/Agent run references plus captured content,
  all original and superseding opinions, dependencies, reservations and actual
  usage, failures/gaps/conflicts, start/end times, and final stop reason.
- `OrchestrationResult`: stable active opinion set, explicit missing/partial/
  skipped/failed results, unchanged A2 reference, context/confirmation/research
  references and aggregate audit/run reference. It is not a merged stance.

Referenced records must be resolvable in the capture package; IDs pointing to a
live service alone are insufficient for replay. Validate unique IDs, acyclic
edges, dependency references, plan lineage, terminal-node coverage, reservation
ownership, and snapshot-to-opinion fingerprint links. Stable logical ordering
is separate from observed wall-clock completion order.

## 4. Capability and dependency model

Extend registry **composition**, not specialist policies: a versioned
`SpecialistDependencySpec` associates registered `SpecialistCapability` IDs
with fine evidence predicates, optional enrichment targets, upstream output
subscriptions, instrument applicability, and workflow-requiredness. The registry
remains the source of supported instruments, coarse authorities, cost tier and
no-LLM support. Validate that policy never grants more than the request and
implementation allow. Enum membership alone is not implementation: do not
schedule `CONTRARIAN_HYPOTHESIS` or `FORECAST_INTERPRETATION` placeholders.

All selected specialists require the preserved A2 assessment/reference and
identity-consistent pack. A2 is read through the accepted boundary, not rebuilt
by the Planner or specialists. Missing/invalid A2 identity is an explicit
prerequisite failure, not an invented neutral baseline.

| Implemented specialist | Current required `EvidenceType` | Useful optional evidence / controlled acquisition | Readiness and composition |
|---|---|---|---|
| Technical | TECHNICAL | A2 features, indicators, market/volatility, MTF and baseline through `READ_A2_EVIDENCE` | Independent after supplied A2 evidence is valid. Current implementation supports equity/index. |
| Fundamental | FUNDAMENTAL | Company profile, financials/ratios, valuation, ownership, filings through MI capabilities under authorized fundamental/filing reads | Equity/company only. Financial normalization and period/PIT checks precede interpretation; not dependent on News completing. |
| News/Event | NEWS | `READ_NEWS`, `READ_FILINGS`, earnings calendar/corporate actions and normalized event clusters | Equity/index. Can run alongside Fundamental once event evidence is ready. |
| Relative Strength | RELATIVE_STRENGTH | Existing A2.8 relative/MTF facts and explicitly supplied benchmark | Equity/index; independent of Sector output. No automatic benchmark inference. |
| Sector | SECTOR | Versioned subject-sector mapping and `READ_SECTOR_CONTEXT`/industry evidence | Equity/index; explicit mapping and usable sector facts are needed, not a guess based on company name. |
| Macro | MACRO | Market/index/macro context and explicit subject sensitivity mapping | Equity/index; conditional on supplied exposure/regime or requested research scope. Not run for every symbol by default. |
| Derivatives Context | DERIVATIVES | Supplied A2.7 chain, OI, IV, liquidity, expiry facts through authorized `READ_DERIVATIVES`/A2 reads | Verified F&O equity or explicit derivative/index context. No selection of option/expiry. |
| Opportunity Quality | TECHNICAL | A2.9 maturity/room and Technical, Relative, Sector, Fundamental, News, Macro, Derivatives outputs where selected; raw family evidence retained | Downstream of selected upstream attempts; evidence-family and output dependencies below. |
| Opportunity Risk | TECHNICAL | A2.9 plus extension/room, participation, volatility, event, context, fundamental, derivatives and liquidity evidence/output subsets | Downstream of applicable attempts; mandatory coverage attempt for an opportunity plan. No dependency on Quality's verdict. |

The table adds planning predicates; it does not change the current runtime's
required/optional type declarations. Quality/Risk support the existing broader
instrument set, as does Derivatives Context. An equity instrument type does
**not** prove F&O membership. Use point-in-time instrument-master/resolver or
caller-supplied attributable eligibility evidence; unknown membership is an
explicit unresolved applicability decision. Non-F&O equities skip Derivatives.
For future/option inputs, preserve the caller-selected contract and route only
supported underlying-context requests using explicit underlying identity.
Do not pass an option as an equity to bypass a capability check. For indices,
skip company-only Fundamental. Unsupported instrument/depth combinations are
reported rather than repaired by inventing a new specialist.

Distinguish three dependency meanings:

1. **Hard evidence requirement:** minimum type/semantic predicate to run safely.
   When missing, acquire if authorized or record blocked/insufficient; never
   provide placeholder facts that claim real coverage.
2. **Completion barrier:** wait for a selected upstream node to reach a terminal
   result, including failure/abstention. Quality/Risk need not wait forever for
   a successful opinion that cannot exist. Missing optional context degrades
   coverage rather than making the DAG unsatisfiable.
3. **Optional evidence/output subscription:** consume it when present; record
   its absence and invalidate only actual subscribers when it changes. A
   selected plan can make a normally optional family required for this objective
   without changing the specialist's global capability contract.

Quality and Risk can run in parallel after the relevant upstream barrier; there
is no Quality→Risk investment-ranking edge and no feedback cycle in one plan.
Their direct subscriptions are explicit: Quality uses relative alignment as
well as company/context evidence; Risk does not rerun for unrelated Relative
text it does not consume. New registered capabilities can declare new edges
later without modifying the generic executor.

### Provider-neutral acquisition mapping

The Planner asks for semantic capabilities, e.g. `READ_FINANCIALS`,
`READ_EARNINGS_CALENDAR`, `READ_NEWS`, or `READ_SECTOR_CONTEXT`, never
"ask Tapetide" or "ask Yahoo". The A3.2 capability ceiling and MI
`authorities_for` mapping both apply. An authorized composition adapter maps a
typed evidence need to the existing MI request/router or factual A1/A2 evidence
boundary. It does not import a transport into a specialist or relabel market
price/derivative reads as MI capabilities that do not exist.

Tapetide/Yahoo/NSE/BSE/company-IR identities remain visible in acquisition audit,
not planner branch conditions. Route policy chooses source priority/fallback.
Dhan remains behind the factual market-data boundary. A missing route is
unsupported evidence, not permission for arbitrary browsing or a new provider.

### Upstream opinion projection: the integration seam to implement

A3.7 reads supplied scalar families such as `technical.*`, `relative.*`,
`news_event.*`, and `derivatives_context.*`. Its acceptance fixtures supply
these projections; they are not a general automatic upstream-opinion adapter.
A3.8 must implement and test a mechanical, versioned projection outside the
specialists, rather than parse their prose or copy a whole opinion as a fact.

Use the public typed detail extractors and an allow-listed field-to-metric map.
A proposed `SpecialistOutputProjection` retains the source `AgentOpinionV2`,
detail schema/version, field locators, original raw citation IDs, input digest,
and epistemic classification. Derived scalar references use `EvidenceSource.DERIVED`,
the projection's producer/version, a distinct checksum/ID, and the existing
scalar FEATURE representation only as **a feature of a recorded interpretation**.
They never claim an A2 producer or masquerade as a raw market observation.
Mirror the validated origin/epistemic envelope in safe reference metadata where
needed for the existing pack interface; the typed projection remains the
authoritative lineage record, not arbitrary metadata supplied by a model.

For example, `technical.remaining_room` may quote the exact typed Technical
state and cite its opinion field and original distance evidence; the adapter
does not recalculate room or reinterpret synonyms to get a preferred result.
A factual statement about a supplied label is only "Technical reported X",
not independent proof that the market is X. Downstream market conclusions
remain INTERPRETIVE; preserve original FACT/INFERENCE/HYPOTHESIS boundaries.
Do not boost confidence by counting an opinion and its own raw facts as
independent evidence families. Never project absent/ABSTAIN/unknown values into
substantive positive/negative coverage.

Keep original raw references alongside projections, with distinct IDs;
validate every claim locator and evidence type. Unmapped or semantically
incompatible detail fields remain explicit projection gaps, not new enum
values or guessed market facts. Field compatibility and attribution are a
hard work-package acceptance gate, not permission to retune A3.7.

## 5. Deterministic DAG and bounded parallelism

The initial execution shape is:

```text
validate request / freeze inventory / read A2 / build plan
                           |
      deduplicated required acquisition -> normalize / publish snapshot
                           |
       ready independent specialists (bounded parallel waves)
                           |
      inspect gaps / conflicts / confirmation and research gates
                           |
       optional bounded enrichment -> new snapshot / plan version
                           |             |
                           |       affected upstream reruns only
                           v             v
             Quality and Risk (independent downstream nodes)
                           |
             assemble separate opinions / audit / finalize
```

If Quality/Risk themselves expose a recoverable material gap, use the same
bounded later-round replan path. Each plan version is a DAG; the overall
workflow is a finite sequence of DAG versions, not an unbounded graph cycle.

Sort ready nodes by policy phase, registry specialist/capability ID, then stable
node ID. Construct explicit waves before dispatch. Reserve budgets in that
order; run at most the configured concurrency cap. Fundamental and News, or
Relative and Sector, may overlap once their respective inputs are ready.
Shared sector/macro/company reads are single acquisition nodes. Cache identity
includes canonical subject, capability, requested fields/time window, as-of,
freshness, mapping/normalization and route versions, and authorization scope;
compatible supersets may be reused only after the same checks.

Deduplicate both completed reads and in-flight reads. A cache hit can still
incur a local gateway/tool operation under existing accounting, but must incur
zero new external provider calls. Do not grant each consumer a fresh fallback
allowance for one shared acquisition. Synchronize infrastructure caches or
serialize unsafe provider access; concurrency does not imply thread safety of
existing registries/routers/connectors.

Workers return immutable result envelopes; only the coordinator publishes state
at a deterministic wave barrier. Persist successes, failures and timeouts in
logical node order, while retaining actual start/end/arrival timestamps for
observability. Never let "first response wins" choose evidence or consume
unreserved budget. Serial and LangGraph execution must produce identical
semantic plans/results given identical admitted evidence and recorded outcomes;
wall-clock latency and live deadline outcomes are not promised identical.

## 6. Progressive acquisition, enrichment, and stop value

Use the existing loop: **Acquire → normalize → inspect gaps/conflicts →
selectively enrich → update immutable context → stop**. First inspect valid
captured memory. A rich, fresh existing pack may require no provider calls.
One provider's sufficient canonical evidence is not a reason to call all others.
Provider-defined/ambiguous metrics remain noncanonical, and stale or PIT-limited
evidence does not become adequate because a second source repeated it.

The planner selects *which evidence need* warrants work. The MI router selects
*which permitted source* can satisfy it and owns source-level fallback. Their
nested budgets share one reservation; no duplicate nested retry/enrichment loops.
Use router-level calls for independently publishable capability nodes. Use the
existing research controller only when its complete request has been reserved.
Do not invent a successful full `MarketIntelligenceResearchRun` after its
controller stopped early: preserve completed capability records and workflow
gaps, and assemble research only from a valid explicitly scoped acquisition run.

Evaluate `MissingEvidenceRequest` and planned gaps with stable dispositions:

| Disposition | Meaning and action |
|---|---|
| RECOVERABLE | Authorized, supported, point-in-time usable capability with a specific missing field/family or conflict to address; reserve and schedule within bounds. |
| UNSUPPORTED | No accepted route/schema/instrument/date coverage; retain typed gap, do not retry or discover a new tool. |
| NOT_WORTH_COST | Optional/redundant, already satisfied, repeated unchanged result, immaterial, or no identifiable information contribution; stop this branch with reason. |
| BUDGET_BLOCKED | Potentially useful but call/token/cost/deadline/concurrency/round allocation cannot be safely reserved; keep gap and return partial where necessary. |
| PERMISSION_DENIED | Caller/policy disallows capability, confirmation, depth, or model tier; never silently expand authority. |

Information value is an understandable engineering rule, not an estimate of
profit or a calibrated probability. Prioritize required evidence, then material
gaps/conflicts with an available named field/document, then optional context.
Record the specific coverage predicate or ambiguity that could change, affected
consumer IDs, and bounded cost before approving acquisition. If no predicate
can improve, do not acquire. Repeated identical need/input/route-version keys
cannot consume another round without new eligible evidence or an explicitly
budgeted transient retry. Do not tune weights/thresholds to KAYNES or any live
example; reuse accepted materiality policies and version any engineering limits.

## 7. Confirmation, deep research, and graph memory

### Selective authoritative confirmation

After discovery, route material claims through the accepted
`AuthoritativeEscalationPolicy` and `AuthoritativeConfirmationGateway`, only
when permission, required authority, a configured route and budget exist.
Candidates include conflicting material numbers, ambiguous financial semantics,
results/order/regulatory events, and IPO/prospectus claims. A future caller's
active-position-impact flag may justify evidence verification only; it confers
no position-management authority and requires no A5 implementation here.

Use existing `DiscoveredClaim`/`AuthoritativeConfirmationRequest` fields and
explicit required fields/document kinds. Preserve secondary discovery evidence,
field-level confirmed/unresolved/discrepant status, content hashes, acquisition
and availability times, revisions and event clusters. An official document
does not automatically make every claim true or resolve an incomparable metric.
NOT_FOUND/unavailable remains honest missing confirmation. Do not confirm every
headline or replace the MI fabric with a blanket official-source fetch.

### Selective deep research

An explicit permission is always necessary. Within that ceiling, L2-style
company research is eligible for a caller-requested deep objective, longer
holding context with material company gaps, a material contradiction/event, or
a caller/A2-provided eligible-candidate stage needing more evidence. The latter
is a workflow input, not an A3.8 winner/ranking rule; a negative A2 result or
`NO_TRADE` never gets rewritten to unlock research. DAY plans normally use
available concise context unless an explicit material need warrants more.

Use existing `ResearchDepth` values. L3's name does not authorize position
actions; unsupported requested scope is explicit. Long horizon alone is not a
command to exhaust the research budget. Reuse `DeepResearchIntegrationController`
and its normalized `DeepResearchContextPack`/`DeepResearchResult`, not raw
provider responses or an unstructured LLM conversation. Assembly over existing
acquisition/confirmation records is preferred over a second `execute` call.
Depth controls bounded component/field scope; it does not create a model call.
No-LLM assembly remains fully functional. No new model provider is added in A3.8.

### Sparse Evidence Graph

Reuse caller-supplied/captured `SparseEvidenceGraph` snapshots for known company,
sector, customer/supplier, exposure and event relationships. Limit scope by
subject, permitted relation, as-of, node/edge count and depth; initial policy
uses one-hop neighborhoods only. Preserve provenance and FACT/INFERENCE/HYPOTHESIS,
availability and effective-time limitations. Missing edges are not proof of no
exposure. An inferred edge cannot supply canonical factual coverage.

The graph's existing `with_updates` is append-oriented and validates unique IDs.
Produce explicit new snapshot/revision identities rather than appending duplicate
IDs to overwrite relationships. A graph snapshot ID alone is not a versioned
content digest. No automatic classification, recursive discovery, persistent
graph engine, or arbitrary historical reconstruction is introduced.

## 8. Selective invalidation and bounded replanning

Record each node's actual input subset, semantic digest, normalization/mapping
versions, upstream output field digests, and policy version. A material change
means a change in a declared consumed value, availability/quality/freshness,
confirmation state, permission/budget outcome, or applicable policy—not simply
a new fetch timestamp. Preserve acquisition-time provenance separately.

New evidence is staged until the next wave barrier, must be authorized and
eligible at the original `as_of`, and receives an admission sequence/digest.
Do not mutate an in-flight pack. Evidence available only after `as_of` belongs
to a new request, not retrospective improvement of the current replay. Preserve
conservative/unknown PIT quality instead of claiming historical certainty.

Create a new plan version with parent ID, trigger, exact changed evidence,
invalidated nodes and reason. Preserve all previous plans/results. In-flight
old-version work finishes or times out against its pinned input; charge its
usage, mark superseded results, and exclude them from the active output set.
Do not restart it speculatively while holding an unaccounted old reservation.

| Change | Invalidation example |
|---|---|
| New material financial filing | Fundamental and News if they consume the changed facts/event; Risk directly and Quality where subscribed; Technical/Relative unchanged. |
| Sector mapping corrected | Sector, then Quality/Risk context consumers; Fundamental only if its own sector-dependent input changed. No company-wide restart. |
| Option-chain snapshot changed | Derivatives Context and affected Quality/Risk derivative families; no Fundamental/News rerun unless separate consumed evidence changed. |
| Authoritative confirmation/discrepancy | Only specialists consuming that claim/field/confirmation state and their downstream subscribers. |
| Identical values with changed consumed freshness | Rerun affected freshness/coverage consumers; do not mistake this for irrelevant transport latency. |

After an upstream rerun, compare subscribed output digests: if unchanged, reuse
its downstream output unless a downstream raw-evidence/quality dependency also
changed. Bind reused outputs to their original input/run; never restamp an old
opinion with a new fingerprint. Quality/Risk that have not yet run simply use
the latest admitted version at their barrier, avoiding a needless early pass.

Bound replan count, enrichment rounds, per-node attempts, total invocations and
deadline. A replan cannot reset budgets, widen permissions, or erase original
decisions. If a useful rerun cannot fit, retain previous opinions as explicitly
superseded/outdated, expose missing current coverage, and return partial.

## 9. Budgets, cost and time

Reuse `AgentBudget` for tool/model calls, input/output/total tokens, cost units
and elapsed limits; roll up `AgentUsage`. Add only orchestration-specific
limits: specialist count, invocation count, concurrency, provider attempts,
enrichment rounds, replans, per-node attempts and bounded graph scope.

Initial proposed engineering profile: at most nine distinct implemented
specialists, concurrency three, two enrichment rounds, two replans, two attempts
per specialist and eighteen specialist invocations total. These are safety caps,
not performance/accuracy claims; caller and deployment policy can tighten them.
No automatic retry is the default. At most one transient retry may be explicitly
enabled within the same attempt/call/deadline envelope. Existing zero-call
`AgentBudget` defaults remain zero: live acquisition requires an explicit finite
allowance, not a hidden positive default. Existing elapsed limits remain in
force; the effective limit is the tightest applicable caller/policy/node limit.

Before dispatch, atomically reserve the worst-case allowed calls/tokens and
known cost for a node, including its internal fallback, confirmation and research
work. Ensure `spent + outstanding reservations + proposed <= ceiling` in each
additive dimension. Each underlying operation has one accounting ID; MI audits
and parent usage are linked, not double-debited. Distinguish local tool reads,
external provider attempts and model attempts in the rollup. Reconcile actual
usage on completion, release unused reservation, charge failed attempts, and
stop admitting work if a provider reports more than reserved. Unreported usage
remains unknown/held, never falsely refunded to zero.

Cost units are not silently rupees/dollars. Use configured, versioned known
units or a conservative authorized bound; if a hard cost ceiling cannot be
guaranteed for an unpriced operation, block it. Report unknown provider monetary
cost separately. No-LLM means zero model calls, input/output tokens and model
cost, not necessarily zero provider/tool cost. Existing deterministic specialists
receive zero model allocation; no hidden reasoning call is allowed in the Planner.

Aggregate elapsed time is wall-clock duration, **not the sum of concurrent node
durations**. Track both node service time and critical-path/run duration. Use a
monotonic clock for deadlines and aware wall time for audit. The current
single-specialist runtime measures synchronous elapsed usage after `analyze`;
it does not preempt arbitrary synchronous work. The adapter must bound provider
transport timeouts and admission, isolate uncooperative work, and record a
timeout/late completion honestly. Cancelling a future is not proof an external
call stopped: keep its reservation until reconciled, prevent follow-on work,
and never claim a strict process-kill SLA from LangGraph alone.

## 10. Failures and stopping

Proposed orchestration node states distinguish pending/ready/running/reused,
completed/partial, blocked/skipped, failed/timed-out and superseded. Map existing
typed result enums into these states without overwriting the original result.
Every selected node ends with a result or a reason it did not run.

| Condition | Workflow response |
|---|---|
| Provider unavailable/rate-limited/timeout | Let the existing route policy choose a permitted fallback within the reserved budget; otherwise keep the typed evidence gap. No synthetic live failure or planner vendor switch. |
| Malformed/ambiguous payload | Retain normalization failure/ambiguity; reject invalid canonical facts; optional route fallback does not erase the original failure. |
| Unsupported capability/date/instrument | Terminal gap for that need; no repeated retry or tool discovery. |
| Specialist exception/invalid output | Record `AgentFailure`/failed attempt, isolate the node and allow independent work. Never synthesize a positive opinion. |
| Specialist ABSTAIN or insufficient evidence | Valid substantive outcome; preserve reasons and inspect only recoverable material gaps. Do not retry merely to change stance. |
| Confirmation unavailable/NOT_FOUND | Preserve unconfirmed claim/discrepancy and context; partial if required, otherwise qualified optional absence. |
| Budget/deadline exhausted | Stop admission, settle/capture outstanding outcomes and return valid partial records. |
| Optional specialist failure | Keep other results; explicitly report unavailable optional coverage. |
| Invalid request, authorization escape, corrupt snapshot or unsafe DAG | Reject/quarantine before further work; terminal workflow failure, not apparent partial success based on unsafe evidence. |

Stable terminal reasons cover EVIDENCE_SUFFICIENT, REQUIRED_WORK_COMPLETE,
NO_USEFUL_NEW_EVIDENCE, BUDGET_EXHAUSTED, DEADLINE_EXCEEDED, DEPTH_LIMIT,
UNSUPPORTED_REMAINING, TERMINAL_FAILURE and ABSTENTION_ACCEPTED. Persist all
applicable reasons and choose the primary by a versioned order: integrity/
authorization failure, deadline/budget, required insufficiency/abstention,
depth/unsupported/no-progress, then successful completion/sufficiency.

Sufficiency means required predicates and required attempts are fulfilled or
have a truthful terminal disposition; it does not mean all opinions agree.
Distinguish **workflow completion** from **evidence completeness**: a completed
workflow can return PARTIAL/INSUFFICIENT/ABSTAIN. A missing required Risk attempt
cannot look like a fully covered opportunity, and all-abstain is a useful
result. Stop when required work is complete and no justified optional need
remains; never continue until a desired market stance appears.

## 11. State and LangGraph isolation

Select LangGraph as the execution adapter, not a contract language. Proposed
placement is `tiaf.planner` for contracts/pure policy/dependency logic and
`tiaf.workflows` for the application coordinator, reference runner and a thin
`langgraph_adapter` infrastructure module. Framework dependencies are imported
only there (and at explicit composition roots), never by `tiaf.contracts`,
`tiaf.agents`/specialists, canonical evidence, or deterministic calculators.

Minimal serializable domain state: request/plan version references; admitted
inventory and digests; node status/attempts; pending gap and contradiction IDs;
confirmation/research state; budget ledger; ordered events; independent opinion
references; and stop/degradation reasons. Graph/framework state, reducers,
checkpoint handles, tasks/futures and connector objects remain adapter-local.
Raw LLM message history is neither workflow state nor an audit source of truth.

Conceptual nodes are initialize, assess inventory, construct plan, acquire,
normalize/publish, run ready specialists, inspect gaps/conflicts, decide bounded
enrichment, confirm, assemble research, replan/rerun affected nodes, assemble
results and finalize. Typed policy decisions determine edges; no prompt decides
which tool runs next. One reducer/coordinator owns budget and evidence admission.
The thin in-process serial runner is a portability/test oracle, not a second
production policy engine. Both adapters call the same pure decision functions
and `AgentRuntime`/controlled services.

Introduce/pin and verify the actual LangGraph API during implementation, not
in this architecture pass. Domain replay must not require LangGraph checkpoints
or an installed framework. Checkpoint serialization is optional infrastructure
recovery; arbitrary crash/restart guarantees, distributed queues and production
checkpoint operations remain deferred. No live model endpoint is needed to
prove the framework adapter works.

## 12. Replay and A2 preservation

Capture normalized evidence, native/normalization references where already
recorded, original A2 assessment/pack, graph snapshots, all consumed upstream
projections/opinions, policy/registry snapshots, reservations/usage, branch and
stop decisions, admitted evidence sequence, plan versions and runtime version.
Capture specialist/prompt/model configuration versions when applicable; no
secrets or executable instructions. Preserve original evidence hashes and
existing MI/research fingerprint algorithms.

Use separate identities:

- **A2 fingerprint:** copied unchanged alongside its immutable assessment;
  enrichment never writes a new hash onto the old A2 evidence.
- **Invocation input digest:** hashes the exact authorized pack plus consumed
  upstream/MI projection content and policy versions. Populate the existing
  request/pack/opinion fingerprint consistently for that invocation, while
  preserving the distinct original A2 fingerprint in the orchestration record.
- **Orchestration semantic fingerprint:** versioned canonical JSON of effective
  request, policy/dependency versions, admitted content, logical plan/decision
  sequence, semantic outputs, failure/stop outcomes and active/superseded links.
  Transport latency and fresh replay wall timestamps are excluded, not evidence
  availability/quality or deadline outcomes. Store exact record checksum and
  observed timing/usage separately. Do not modify child fingerprint algorithms
  just to make hashes compare equal.

Two explicit offline modes avoid misleading "exact replay" claims:

1. **Recorded-run replay:** validate all digests/contracts, reconstruct recorded
   state transitions and output from captured outcomes/decisions, and reproduce
   the original audit record without any gateway/provider/model execution.
2. **Deterministic policy/execution verification:** rerun pure planner policy and
   deterministic specialists using captured packs, versions and injected recorded
   clock/budget/deadline outcomes; compare plans, claims, detail, gaps and semantic
   fingerprints. Any future nondeterministic model step uses its captured output,
   explicitly marked not re-inferred. A version mismatch fails verification or
   is an explicit comparison run, not an undocumented migration.

Replay must work with live connectors and model access disabled and must fail
clearly on missing captured content. Shuffled worker completion alone cannot
change canonical ordering/results; materially different live deadline/evidence
admission outcomes legitimately define a different run. Captured replay does
not assert exact arbitrary historical data availability (DEF-049).

### A3.9 handoff

Return independent `AgentOpinionV2` records in stable specialist order, with
active/superseded versions, original A2 assessment/reference, quality/freshness,
confidence bases, missing evidence, conflicts, normalized research components,
authoritative confirmations and orchestration metadata. Preserve disagreement
with A2 and between specialists; never average confidence or select a winner.
A3.9 may assemble its structured underlying-intelligence output from this
bundle. A3.8 does not implement that public product, ranking, recommendation,
position action, option expression or calibrated forecasting.

## 13. Representative plans and acceptance scenarios

### KAYNES positional plan (illustrative, not a live claim)

Subject `KAYNES`, purpose `AnalysisPurpose.OPPORTUNITY`,
`TradeStyle.POSITIONAL`, `Horizon(min_days=14, max_days=42)` (2–6 weeks),
explicit supplied benchmark/sector/F&O context, fixed aware as-of, no LLM.

1. Require the unchanged A2 baseline and inventory its technical/relative/MTF
   facts. Reuse adequate normalized company/event/sector evidence first.
2. Select Technical, Fundamental, News, Relative, Sector, Opportunity Quality
   and Opportunity Risk as required coverage attempts for this profile.
   Select Derivatives Context as required if F&O eligibility is verified; skip
   if verified non-F&O, or report unknown applicability. Macro is conditional
   on supplied exposure/regime or explicitly requested context.
3. Deduplicate and reserve missing eligible capability reads. Publish normalized
   evidence; run ready Technical/Fundamental/News/Relative/Sector/conditional
   Macro/Derivatives in bounded independent waves, not all-at-once by fiat.
4. Inspect explicit gaps/conflicts. Confirm a material discovered claim only if
   permitted and supported. Deep research is conditional, not automatic for
   KAYNES. Preserve unsupported financial semantics and missing mapping gaps.
5. Rerun only affected upstream consumers after admitted enrichment; execute
   Quality/Risk against the final ready context, in parallel where independent.
6. Return all opinions, including negative/mixed/insufficient/ABSTAIN, A2
   disagreement and `NO_TRADE`, with zero model calls/tokens/model cost. Report
   coverage gaps and the stop reason without tuning any interpretation rule.

| Scenario | Required implementation acceptance proof |
|---|---|
| A. Ordinary non-F&O equity | Derivatives skipped with eligibility evidence; other applicable specialists and mandatory Risk attempted; no synthetic chain or option selection. |
| B. Rich existing evidence | All needed fresh/PIT-eligible inputs reused, zero external provider calls; no duplicate fetch just because multiple consumers need a profile. |
| C. Missing financial evidence | Authorized MI capability acquired once, normalized and supplied to Fundamental; bounded partial result if unsupported/inadequate. |
| D. Material news requiring confirmation | Discovery preserved; existing official confirmation gate invoked only after a linked material claim, with field-level result and no blanket verification. |
| E. Provider rate limit | Offline injected primary RATE_LIMITED followed by policy-permitted secondary selection inside the fabric; bounded audits/usage, same neutral contract. Do not manufacture a live failure. |
| F. Unsupported evidence | Stable unsupported disposition, no repeated retry, explicit missing/partial coverage and finite stop. |
| G. Changed material evidence | Replan retains original graph/output; only subscribed nodes and affected downstream Risk rerun; unchanged Technical/Relative records reused. |
| H. Budget exhaustion | Reservations prevent oversubscription, independent completed opinions survive, required coverage remains partial, no model/provider call after denial. |

Additional instrument tests cover explicit index context with company Fundamental
skipped, explicit caller-selected derivative underlying, unknown F&O membership,
missing benchmark/sector mapping, unsupported instrument, DAY shallow scope,
and no authority escalation from a purpose/depth label.

## 14. Internal A3.8 implementation work packages

These are internal packages, not new milestones or deferral detours. Build
ledger/admission interfaces in WP1–4 before allowing WP5 concurrency; WP7
completes failure/timeout hardening rather than first introducing budgets.

| Package | Deliverable and exit gate |
|---|---|
| WP1 — Contracts | Minimal orchestration envelope, immutable plan/decisions/run/result and ledger interfaces; reuse existing Agent/evidence types. Tuple/list/JSON roundtrip, identity, PIT and timezone tests. |
| WP2 — Dependency registry | Validate implemented capability inventory, applicability, hard/optional/barrier edges and acyclicity. Versioned typed-detail projections with field/epistemic/citation tests; no prose parsing or fake A2 facts. |
| WP3 — Deterministic policy | Initial plan, stable order, missing-evidence dispositions, materiality/depth/stop rules and baseline-preserving pure reducers. Same inputs/policy yield same decisions. |
| WP4 — LangGraph adapter | Thin infrastructure-only execution graph plus shared-policy serial reference runner; injected controlled services, bounded admission and no-LLM parity. |
| WP5 — Parallel execution | Deterministic waves, atomic reservations, single-flight evidence reuse, immutable input pinning, thread-safety and shuffled-completion tests. |
| WP6 — Enrichment/replanning | Existing MI/confirmation/deep-research composition, bounded graph reuse, new plan versions and selective invalidation, including in-flight/late evidence. |
| WP7 — Budgets/failure/stops | Complete rollups, nested-call accounting, transient failure/fallback bounds, nonpreemptible-work behavior, all-abstain and honest partial termination. |
| WP8 — Run record/replay | Content-addressed capture, semantic versus exact-record checks, policy replay and provider/model-disabled replay; A2 assessment/fingerprint preservation. |
| WP9 — User acceptance | KAYNES-style plan plus scenarios A–H through public orchestration seams; report selected/skipped/reused/rerun nodes, gaps, stop, cost and replay. Any live read acceptance is separately opt-in, bounded, and not needed for this architecture pass. |
| WP10 — Hardening | Full regression, security/architecture boundaries, concurrency/failure fuzz cases, documentation/help consistency and acceptance evidence. No tuning to attractive output. |

### Required test matrix (implemented coverage: section 17 and study)

Test capability-driven/provider-independent selection and no unregistered enum
execution; non-F&O/index/unknown applicability; hard versus optional readiness;
parallel budget races and deterministic ordering; completed/in-flight reuse and
no duplicate provider fetch; progressive sufficiency and unsupported/denied gaps;
typed output-projection attribution and no double-counting; selective rerun,
unchanged-output reuse and bounded replans; authoritative materiality/PIT/NOT_FOUND;
deep-research permission/depth/context gates; rate-limit fallback and nested
retry limits; specialist exception/ABSTAIN/insufficient and optional failure;
partial/deadline/budget stops and uncooperative work; zero-LLM calls/tokens/cost;
capture tampering/missing records/version mismatch; serial/LangGraph replay
parity; and unchanged A2 evidence/class/score/fingerprint.

Add AST/import and behavior checks for LangGraph isolation, no vendor names in
planner policy branches, no provider/model/execution access from specialists,
and no A4/A5/A6/A7 authority fields or hidden tool execution. Keep existing
architecture/security tests and the full repository suite as regression gates.

## 15. Risks and unchanged deferrals

The implementation risks are the upstream projection seam, nested-controller
all-or-nothing behavior, parallel reservation/thread safety, nonpreemptible sync
work, selective invalidation with quality/PIT changes, and replay-versus-latency
identity. They are explicit WP2/WP4–8 acceptance gates, not reasons to redesign
accepted specialists. Unknown provider cost and unsupported acquisition remain
honest gaps; no new live-access claim is made.

At A3.8 acceptance, existing deferrals included DEF-002 through A3 closure,
DEF-006 option expression,
DEF-009/010 persistent/distributed operation, DEF-040–046 unavailable derivatives
families, DEF-047 automatic benchmark/sector mapping and DEF-049 arbitrary
historical reconstruction. Existing bounded provider fallback is reused, not a
claim that every broader provider-health/operations deferral is closed. No
deferral-register status change was justified by bounded in-process
orchestration alone. The later A3 closure marks DEF-002 implemented by the
complete A3.1-A3.10 layer; all other IDs named here remain governed by the
closure disposition.

TI Shell and the post-A3 Source/Provenance/Citation report fabric stay out of
scope. No A3.9 or A4–A10 implementation is authorized by this document.

## 16. Historical architecture-pass validation

Validation performed on 2026-09-10 with the repository virtual environment:

| Command | Result |
|---|---|
| `.venv/bin/pytest -q tests/unit/agents tests/unit/market_intelligence` | **419 passed**; includes architecture/security, provider/model/execution isolation, gateway/no-LLM, specialist, MI, confirmation and deep-research tests. |
| `.venv/bin/pytest -q` | **1,725 passed**. |
| `.venv/bin/python -m compileall src scripts` | Passed. |
| `.venv/bin/ruff check src tests scripts` | All checks passed. |
| `.venv/bin/mypy src tests` | Success; no issues in **402 source files**. |
| `git diff --check` | Passed; new design file also checked separately against `/dev/null`. |

These historical checks covered the documentation-only architecture pass, not
the subsequent runtime. The implementation-pass gates are in the linked study.

## 17. Implemented APIs, execution and acceptance

| Work package | Available implementation |
|---|---|
| WP1 | `planner/models.py`: frozen request/instrument/inventory, dependency, DAG/node, evidence-task candidate, decision, reservation and result models; aware Asia/Kolkata timestamps and JSON-array tuples. |
| WP2 | `planner/policy.py` and `projection.py`: nine implemented capability IDs, hard/optional families, News semantic predicates, instrument/permission checks, completion barriers and allowlisted typed-detail projections. |
| WP3 | Pure `build_plan`, input/consumed digests, missing-evidence dispositions, depth gating and ordered stops; no provider-specific selection or investment score. |
| WP4 | `workflows/langgraph_adapter.py`: local StateGraph around the shared coordinator; `run_serial` is the framework-free reference runner. |
| WP5 | Max-three deterministic waves, atomic `ReservationLedger`, immutable invocation packs and `ControlledServices` single-flight request futures. |
| WP6 | Existing MI routing/normalization, authoritative gateway and captured deep-research assembly; bounded scoped graphs, versioned replans and consumed-input invalidation. |
| WP7 | Actual/held usage, nested provider ceilings, root elapsed/deadline admission, isolated failed/partial/ABSTAIN runs, explicit superseded outcomes and surviving Risk attempt. |
| WP8 | `OrchestrationRunRecord`, `capture_json`, `replay_recorded`, `verify_deterministic`; exact checksums separate from semantic identity and preserved A2 fingerprint. |
| WP9 | `scripts/a3_8_user_acceptance.py`: 14 public black-box cases, including illustrative KAYNES, both adapters, replay and zero live/model calls. |
| WP10 | `tests/unit/planner/`, `tests/unit/workflows/`, full existing regression, import/AST isolation, shuffled completion, budget races and documentation. |

### Public use and dependency isolation

Install `.[dev,orchestration]` for the whole acceptance suite. The optional extra
pins `langgraph==1.2.11`; serial execution and recorded replay need only ordinary
TIAF runtime dependencies. `tiaf.workflows` does not import the adapter eagerly.
The adapter follows the documented
[StateGraph API](https://docs.langchain.com/oss/python/langgraph/use-graph-api).
Tracing is explicitly disabled and no checkpointer/network exporter is attached.

```python
from tiaf.workflows import (
    ControlledServices, capture_json, default_registry, replay_recorded,
    run_serial, verify_deterministic,
)
from tiaf.workflows.langgraph_adapter import run_langgraph

# request is a validated tiaf.planner.OrchestrationRequest containing an A2 pack.
# Inject existing MI/gateway services only for explicitly authorized acquisition.
record = run_serial(request, default_registry(), ControlledServices())
capture = capture_json(record)
assert replay_recorded(capture) == record
assert verify_deterministic(capture, default_registry()) == record
parallel = run_langgraph(request, default_registry(), ControlledServices())
assert parallel.fingerprint == record.fingerprint
```

Callers supply canonical identities and persisted evidence; there is no automatic
symbol mapping, live credential discovery or hidden acquisition. `LIVE` intent
does not itself authorize a call. Supplied A2 is required and never recalculated.
The default registry composes the existing nine specialists unchanged.

### Bounded engineering choices

- The implemented policy is **deterministic/no-LLM only**: requests reject model
  tiers other than `NONE` or `no_llm=False`; specialists receive zero tool/model
  allocations. No future nondeterministic model execution is implied.
- Plans carry separate conditional evidence-task candidates and specialist DAG
  waves. Actual controlled acquisition/confirmation/research is recorded in
  decisions, artifacts and reservations, not represented as a new provider graph.
  MI route policies retain source selection and fallback authority.
- Independent specialist work is parallel; acquisition is conservatively serial
  at publication barriers, with thread-safe single-flight for duplicate requests.
  Logical request IDs alone do not create duplicate provider reads.
- All selected required specialists get an attempt or explicit blocked outcome.
  Optional evidence absence is not a completion barrier. Sparse hard evidence
  is delivered with honest coverage so existing specialists can report
  insufficient/ABSTAIN; a type label alone is not a News event schema.
- Upstream projections quote allowlisted typed assessment fields, preserve the
  source opinion/schema/input digest/citations and label them `INFERENCE` from a
  derived producer. They do not parse prose or rewrite A2 observations. Citation
  sets are conservative (the source opinion's cited evidence union), not claims
  of per-field minimal attribution. Missing/UNKNOWN states are gaps, not facts.
- Exact invocation hashes retain provenance. Consumed-input hashes additionally
  disregard transport-only acquisition time/checksum changes while retaining
  values, observation/PIT times, identity, quality, freshness and semantics.
  Reused output is never restamped. Changed raw content reruns subscribers;
  unchanged quoted upstream output need not rerun downstream-only consumers.
- At a replan limit, stale direct and transitive opinions are superseded rather
  than advertised against new inputs. Original records/projections stay in audit.
- Root elapsed time is measured, not summed across concurrent work. Every child
  reserves its full allowance before dispatch; actual usage is counted once.
  Unknown usage stays held separately from known consumption. A synchronous
  uncooperative call cannot be force-killed: admission stops and its reservation
  remains held; the worker may finish later without publishing into the result.
- Deep research uses the accepted controller's `assemble` on captured MI runs,
  not a second fetch. Permission/depth/materiality gate it. Graph reuse is a
  bounded, as-of-filtered, relation-allowlisted one-hop snapshot; original capture
  is retained separately if scoping changes its content.

### Replay guarantee and limits

Recorded replay validates/reconstructs typed captured artifacts and their exact
checksum, plan sequence, active outcomes, A2 preservation and usage rollups,
without calling providers, models or LangGraph. Deterministic verification also
rebuilds every plan from the recorded request/current registry, reconciles ledger
entries, reruns deterministic specialists on their captured invocation packs and
rebuilds typed projections. Version/input/output mismatch fails verification.

Provider results, external evidence admission and deadline/timeout outcomes are
**recorded inputs**, not live operations repeated by verification. Verification
does not simulate the original wall-clock scheduling race or re-execute the full
acquisition/confirmation state machine. It proves policy/constituent output
consistency for the recorded inputs, not historical source availability.
Operational timings and runtime-adapter identity are excluded only from the
semantic fingerprint; exact capture retains them. Evidence availability and
meaningful stop/deadline differences remain semantic.

See [STUDY_A3_8_USER_LEVEL_ACCEPTANCE.md](STUDY_A3_8_USER_LEVEL_ACCEPTANCE.md)
for observed scenario results, exact tests, quality gates and remaining limits.
