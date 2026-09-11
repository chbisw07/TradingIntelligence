# TIAF A4 Major Milestone Closure Review

## Status, scope, and decision

This review closes the implemented TIAF A4 major milestone on 2026-09-11
(Asia/Kolkata). It reviews the accepted A4.1 deterministic challenge/arbitration
runtime and the accepted A4.2 governed evidence-need/Planner bridge as one
coherent decision-intelligence layer.

Review entry was clean at A4.2 commit `ad3cc5a`; its accepted parent A4.1 commit
is `7b4bde9`. The closure changes documentation/governance only and leaves those
runtime commits unchanged.

The review finds A4 ready for a reviewed baseline commit and subsequent annotated
tag `tiaf-a4-baseline`. This pass does not create that commit or tag. Optional
model reasoning, TI_SHELL, A5-A7, remote services, durable operations, and broker
authority remain outside the delivered baseline.

**Closure decision:** `READY_TO_FREEZE_A4`.

## 1. North-star alignment and delivered scope

A4 is a disciplined L6 review layer over attributable A2/A3 intelligence. It:

- constructs one primary thesis and at most one evidence-supported counter-thesis;
- challenges evidence coverage, source basis, freshness, assumptions, thesis
  tension, risk, timing, and baseline divergence;
- arbitrates with explicit ordered rules rather than votes or confidence averages;
- preserves dissent, limitations, uncertainty, and invalidation conditions;
- emits provider-neutral material evidence needs where a declared question may
  be resolved;
- permits at most one governed A3.8 acquisition/enrichment round and one later
  successor review; and
- captures exact parent, policy, evidence, workflow, usage, failure, and replay
  lineage.

A4 does not select CE/PE, strike, expiry, quantity, target, stop, or entry; manage
positions; place orders; generate calibrated probabilities; own A7 evaluation;
or acquire broker authority. `SUPPORTIVE` is a survived underlying thesis, not a
buy or enter instruction. This preserves the user's economic interest through
risk control and honest uncertainty rather than attractive output tuning.

## 2. Integrated A4 flow and ownership

The implemented path is:

```text
A3.9 structured opportunity intelligence
  -> source-qualified A4SemanticInputProjection
  -> deterministic primary/counter thesis construction
  -> deterministic Challenger
  -> deterministic Arbitrator and A4 disposition
  -> optional material A4EvidenceNeed
  -> deterministic A4.2 admission
  -> narrow A4-to-A3.8 bridge
  -> existing Planner/workflow and controlled services
  -> explicit normalized evidence crosswalk
  -> later successor projection
  -> affected-finding lineage and complete successor arbitration
  -> successor A4 disposition or a conservative typed stop
```

`tiaf.a4` owns domain contracts and deterministic review. `tiaf.a4_enrichment`
is an application bridge. A3.8 remains the only Planner and workflow owner;
MI/data/confirmation gateways retain provider and source routing. A4 constructs
no provider/router/service handle and performs no A2/A3 calculation.

The bridge preserves subject, objective, horizon, parent run/projection, A2
assessment and fingerprint, A3 package and fingerprints, authority, remaining
budget, deadline, and evidence-need identity. The original parent artifacts are
frozen and a later acquisition cannot be backdated into them.

## 3. Disposition audit

| Disposition | Audited meaning and boundary |
| --- | --- |
| `NO_TRADE` | Applicable deterministic prohibition, including the original A2 hard gate. A4 cannot override it. |
| `AVOID` | Explicit risk veto or substantive invalidation. It is not a sell instruction. |
| `INSUFFICIENT_EVIDENCE` | A required evidence, authority, source, scope, or coverage basis is missing. |
| `ABSTAIN` | The declared review policy/process cannot complete a safe decision. It is distinct from missing market evidence. |
| `CONFLICTED` | Material supported opposition remains unresolved. Mere scope or semantic mismatch is insufficient. |
| `WAIT` | The thesis remains plausible but has a cited remediable timing or freshness condition. |
| `SUPPORTIVE` | The primary underlying thesis survives all applicable deterministic checks without a material blocker. It grants no action authority. |

The precedence order keeps A2 `NO_TRADE` first, then risk veto, required
evidence, incomplete review, material conflict, timing, surviving thesis, and no
supported thesis. No rule was found to manufacture `SUPPORTIVE`. The policy is
deliberately conservative around unknown authority and required evidence, but it
still permits a supported clean case and a later evidence-resolved successor.

## 4. Thesis, challenge, and arbitration audit

Exactly one primary thesis is built. A counter-thesis appears only for admitted
material opposition, explicit risk dominance, or an explicit timing alternative,
and the policy caps it at one. Fact premises resolve to admitted factual
assertions; hypotheses and unknown mappings cannot become facts. Dependency
cycles and unresolved claim/evidence/proposition references fail closed.

The eight challenge families are closed. Findings cite typed evidence, reason,
dispute, qualification, premise, and thesis references; free text alone cannot
be decisive. Findings are deterministically deduplicated by content identity and
stable ordering, not counted as votes. Arbitration uses neither source brands,
scalar trust, confidence averaging, argument count, nor model prestige.

Counter-theses, rejected/qualified issues, decisive conditions, dissent, and
residual uncertainty remain in immutable results. Challenger failure yields a
partial abstention; Arbitrator failure yields no valid result. No favorable
fallback is created by a failed review.

## 5. Source, provenance, authority, and contradiction

The pre-A4 foundation remains authoritative for source semantics:

- source, provider, upstream origin, document family/version, occurrence,
  assertion, and proposition identities remain distinct;
- authority is field-, subject-, basis-, and effective-time scoped, with
  `UNKNOWN` preserved;
- comparability is decided before factual value conflict;
- repeated/syndicated provider observations are not independent votes;
- independence is a qualified relationship with explicit root/derivation basis;
- `NOT_FOUND` is absence of confirmation, not factual falsehood;
- scope/semantic mismatch remains non-comparable or unresolved rather than being
  promoted automatically to factual conflict;
- revisions and dispute transitions are append-only and point-in-time aware;
- fact, inference, hypothesis, and forecast roles remain orthogonal to source
  authority; and
- no `SourceScore` or global provider prestige order exists.

A4.2 accepts only an explicit workflow-output-to-canonical-evidence crosswalk.
Every genuinely new semantic evidence ID must originate in a workflow-produced
inventory/artifact, then pass the existing normalization, authority,
comparability, dispute, independence, and PIT projection contracts.

## 6. Bounded open-world evidence review

`A4EvidenceNeed` expresses a semantic question, capability, claim/predicate/field
scope, materiality, evidence characteristics, authority/source-role scope,
budget/deadline, dedupe key, and parent/policy lineage. It contains no provider,
URL, endpoint, browser instruction, arbitrary tool, model instruction, broker,
order, or trade field.

Admission validates exact parent ownership and produces one of nine closed
outcomes: admitted, authority denied, budget denied, policy denied, duplicate,
unsupported capability, non-material, deadline exceeded, or already resolved.
Admission is permission logic rather than a market opinion.

The bridge supports the already accepted confirmation, company/fundamental,
event/news, sector/macro, derivatives, and no-model bounded-research paths. It
permits one round, one successor, one specialist attempt, and at most one provider
call. Equivalent, irrelevant, duplicate-wrapper, not-found, unavailable, or
unchanged ambiguous results stop as `NO_NEW_INFORMATION`; no recursive research
occurs.

Safe authority/confirmation/provenance/context evidence may create a later local
A4 successor. Price/market-state or specialist-input changes return
`UPSTREAM_REFRESH_REQUIRED`, leaving approved upstream composition to rebuild
lower layers. Finding lineage marks affected findings `RECOMPUTED`, semantically
unchanged findings `PRESERVED`, removed findings `RESOLVED`, and new findings
`NEW`; arbitration evaluates the complete successor set. The immutable parent
retains every prior finding and dissent.

This A4.2 path is replay/captured-fixture validated, not live-through-A4
validated. Existing underlying provider and authoritative-confirmation adapters
have separate bounded live evidence, but that does not convert A4.2's captured
acceptance into a live claim.

## 7. Planner, LangGraph, and facade boundaries

A4.2 translates one admitted semantic need into an ordinary bounded A3.8
`OrchestrationRequest`; it does not choose providers or duplicate planning.
Serial execution remains the semantic reference. LangGraph is an optional lazy
application adapter with parity tests; no LangGraph type appears in A4/source/
facade contracts, no LangChain dependency exists, and recorded replay needs
neither framework.

The stable same-process facade exposes `a4_input.project` and `a4.evaluate`
through typed logical artifact references and permission-filtered descriptors.
Callers cannot inject paths, URLs, registries, routers, provider handles,
policies, or authority grants. A4.2 stays internal because a public live
lifecycle, configuration, and storage surface has not been separately accepted.
Closure does not force a misleading one-call live operation.

## 8. Replay, integrity, cost, and degradation

A4.1 recorded replay verifies projection/run checksums, semantic fingerprints,
parent identities, and exact policy without live repair. Deterministic
verification reruns captured input and policy; policy comparison creates a new
run identity rather than masquerading as replay.

A4.2 capture seals the parent run, evidence need, admission, bridge plan, A3.8
workflow record, canonical evidence capture, successor projection/run, usage,
failures, and semantic fingerprint. Recorded chain replay has no registry,
service, provider, model, graph, or network input. Missing/corrupt captures fail
closed. Verification reconstructs admission, bridge mapping, projection, and
deterministic A4 from captured material only.

A4.1 records known-zero model/provider usage while preserving parent cost
knowledge. A4.2 carries the remaining parent budget instead of resetting it,
retains A3.8 leaf accounting, caps provider calls, distinguishes reuse/failure,
and performs no implicit retry/refund. Unknown or unpriced monetary usage remains
unknown/unpriced rather than zero. DEF-055 is therefore not a deterministic A4
freeze blocker; it remains necessary before claiming strict monetary enforcement
for an optional production model.

Denied admission performs no acquisition. Provider/workflow failure, timeout,
budget exhaustion, failed/malformed evidence capture, successor projection
failure, upstream-refresh requirement, and A4 re-evaluation failure all stop
conservatively. Projection failure and re-evaluation failure have distinct typed
terminal reasons. No failure path improves the parent disposition.

## 9. Frozen A2/A3 and intelligence hierarchy

The closure diff changes no A2 feature, scoring, class, direction, policy, or
fingerprint implementation and no A3 specialist, A3.8 workflow, A3.9 assembly,
or A3.10 capture implementation. A4 references their frozen identities and
creates new additive artifacts. It may downgrade an A3 `OPPORTUNITY`, qualify a
`WATCH` only when material blockers are absent, or preserve an A2 `NO_TRADE`; it
does not reinterpret old records.

The accepted hierarchy remains:

| Level | Owner |
| --- | --- |
| L0 | Raw sources/providers |
| L1 | Normalized evidence and source semantics |
| L2 | Deterministic features/indicators |
| L3 | A2 deterministic market/opportunity state |
| L4 | A3 specialist interpretations |
| L5 | A3.9 structured opportunity intelligence |
| L6 | A4 challenge, arbitration, and bounded evidence-needs |
| L7 | Future A5 position and A6 option-expression intelligence |
| Overlay | A7 empirical evaluation, forecast, and learning evidence |

A4 has no position action, option-selection, probability-generation, or broker
operation. TradeMonitor remains the future operational governor.

## 10. Optional model-backed Challenger

**Recommendation: `KEEP_DEFERRED`.**

Deterministic A4 is complete as an explainable no-LLM benchmark. A model may
later add useful alternative hypotheses or challenge coverage, but it is not
required to freeze A4 and cannot supply canonical facts from memory. A separate
optional A4 enhancement must first provide role-aware gateway composition,
approved adapter/configuration, privacy and egress policy, structured
ID/path/value rejection, bounded tools/context/output, prompt/model identity,
price and usage knowledge, failure semantics, recorded replay, no-LLM control,
and evaluation against the deterministic benchmark. DEF-052 and DEF-055 retain
that gate. This need not be moved wholesale into A7: A7 may provide evaluation
methods, while any Challenger runtime remains an explicit optional A4 lane.

## 11. Deferral burn-down

No new stable deferral ID is needed. Status vocabulary remains the register's
six accepted values; planning classifications below refine scope without
inventing statuses.

| ID | Closure classification | Result after A4 |
| --- | --- | --- |
| DEF-003 | `SPLIT_WITHIN_STABLE_ID` | Same-process facade is implemented; remote service/API remains `PLANNED` for justified A8/A10 need. |
| DEF-007 | `KEEP_DEFERRED` | Exchange-calendar/session recency is still required before unattended scheduling. |
| DEF-009 | `KEEP_DEFERRED` | No distributed cache/store/telemetry need was demonstrated by local A4. |
| DEF-010 | `REWORD` | One-round A4 is not a durable queue; review bounded lifecycle contracts before A5 and runtime scheduling at A10. |
| DEF-011 | `KEEP_DEFERRED` | Existing typed failures/fallback are not an operational provider-health model. |
| DEF-022 | `KEEP_DEFERRED` | A4 consumes completed evidence and does not define forming-bar revision semantics. |
| DEF-024 | `KEEP_DEFERRED` | Optimization still needs A7 objectives and leakage controls. |
| DEF-035 | `KEEP_DEFERRED` | A4 successor lineage is not a price-event persistence/re-entry lifecycle. |
| DEF-047 | `KEEP_DEFERRED` | Benchmark/sector identities remain explicit; no neutral automatic classifier exists. |
| DEF-049 | `KEEP_DEFERRED` | Captured replay still cannot recreate an uncaptured historical information set. |
| DEF-050 | `KEEP_DEFERRED` | Filesystem replay remains sufficient; no distributed replay farm is justified. |
| DEF-051 | `KEEP_DEFERRED` | Outcome acquisition still needs calendars, retention, and durable scheduling. |
| DEF-052 | `KEEP_DEFERRED` | Optional model Challenger lacks the accepted privacy/adapter/evaluation gates. |
| DEF-053 | `KEEP_DEFERRED` | Cross-candidate ranking remains an A7 evaluated capability; A2 is the benchmark. |
| DEF-054 | `PLANNED_NEXT` / `SPLIT_WITHIN_STABLE_ID` | Plan minimal captured-source rendering with command-first Shell; retain rich report/Web bibliography later. |
| DEF-055 | `KEEP_DEFERRED` | Unknown-safe accounting suffices for no-model A4; monetary catalog remains an optional-model/A10 dependency. |

The register changes DEF-054 from `DEFERRED` to the supported `PLANNED` status.
All other stable statuses remain unchanged; delivered/remaining scope is clarified
without duplicate IDs.
The resulting current register contains 42 `DEFERRED`, 4 `PLANNED`, 4
`IMPLEMENTED`, 3 `REJECTED`, and 2 `SUPERSEDED` records across all 55 stable IDs.

## 12. TBD implications and next boundary

| TBD area | A4 closure implication |
| --- | --- |
| TI_SHELL | Selected next architecture slice: command-first local mediator over the seven accepted facade capabilities; NLP remains separate. |
| Monitoring | Review bounded position/WatchMandate lifecycle, evidence clocks, and delta semantics at A5 entry; no daemon is required for on-demand A5. |
| Forecasting | Keep for A7 after deterministic A6 candidates and admitted PIT/outcome definitions. A4 does not generate probabilities. |
| CLI/Web | Promote only the local command subset with Shell; Web/remote transport waits for a real consumer/A8 need. |
| Citation UX | Plan minimal rendering from captured A4/source lineage with Shell; do not re-research or hide contradiction. Rich reports remain deferred. |
| Deployment | Keep local Python, request isolation, and filesystem replay. Service/worker/database/queue/cloud deployment remains conditional. |

The exact next milestone is a small architecture pass before A5:
**POST_A4_PRE_A5 — TI_SHELL Command-First Local Engineering Interface Architecture**.
It should define commands, session state, safe rendering, capability admission,
and replay/explanation projection over the existing facade without adding NLP,
live A4 enrichment, remote transport, or intelligence policy. This reduces A5
integration and acceptance friction without becoming an A5 dependency.

## 13. Live-validation truth table

| Surface | Status | Truthful scope |
| --- | --- | --- |
| A4.1 deterministic logic | `REPLAY_VALIDATED` | Synthetic/captured projection cases, exact deterministic rerun, facade parity, and offline replay. No live data is required by the evaluator. |
| A4.2 Planner bridge | `REPLAY_VALIDATED` | Real A3.8 serial/optional-LangGraph execution with captured services, successor construction, and offline chain replay. |
| Source-semantic foundation | `REPLAY_VALIDATED` | Deterministic source/authority/comparison/dispute/confirmation projections and captured replay. |
| Existing authoritative-confirmation integration | `BOUNDED_LIVE_VALIDATED` | Separately accepted NSE/BSE/company-IR gateway evidence; not a live A4.2 run. |
| Existing MI/provider acquisition substrates | `BOUNDED_LIVE_VALIDATED` | Provider-specific bounded studies exist; coverage is not universal and does not certify A4.2 live routing. |
| Provider acquisition through A4.2 | `SYNTHETIC_ONLY` | Captured fixture provider and offline confirmation adapter exercise the bridge; no external live call was made. |
| Model-backed Challenger | `NOT_APPLICABLE` | Not implemented or invoked. |
| Profitability/calibrated forecasting | `NOT_APPLICABLE` | A4 acceptance does not measure returns or generate calibrated forecasts. |

No synthetic/captured-fixture path is reported as live validation.

## 14. Validation and freeze readiness

The closure gate includes the A4.1/A4.2 suites, facade, source semantics, A3.8
workflows, MI, opportunity intelligence, A3 hardening, Agents, and the entire
repository. It also checks compilation, lint, typing, package dependencies,
documentation links, credential-shaped assignments, forbidden imports, replay
isolation, frozen A2/A3 code paths, future-layer leakage, and whitespace.

The final executed counts are recorded after the closure run:

| Gate | Result |
| --- | --- |
| A4.1 `tests/unit/a4` | 37 passed |
| A4.2 `tests/unit/a4_enrichment` | 44 passed |
| Facade | 42 passed |
| Source semantics | 27 passed |
| Workflows | 42 passed |
| Market intelligence | 149 passed |
| Opportunity intelligence | 65 passed |
| A3 hardening | 61 passed |
| Agents | 270 passed |
| Required closure suites including A4.1 | 693 passed |
| Combined closure-focused set including A4.2 | 737 passed |
| Full repository | 2,071 passed |
| `python -m compileall src scripts` | Passed |
| `ruff check src tests scripts` | Passed |
| `mypy src tests` | Passed — 497 source files |
| `python -m pip check` | Passed — no broken requirements |
| `git diff --check` | Passed |
| Changed-document links | 255 checked across 21 documents; none missing |
| Scoped secret scan | 21 changed text files; no credential-shaped assignments |
| A4/source/facade import boundaries | 32 files; no violations; LangChain absent |

Residual risks are bounded and disclosed: A4.2's production workflow-to-source
projectors remain trusted gateway/application work; live A4.2 routing is not
validated; literal incremental per-rule execution is not an optimization target,
although semantic affected/preserved lineage is explicit; source scope and
independence may remain unknown; model usefulness and investment profitability
are unproven; and local storage/facade are not multi-process services. None
invalidates the deterministic, bounded, replayable A4 contract.

After review of the final implementation commit, create the annotated tag
`tiaf-a4-baseline`. The tag must mean deterministic challenge/arbitration,
governed one-round evidence enrichment, conservative successor/replay/failure
semantics, and no required model. It must not imply live A4 acquisition,
profitability, position/option intelligence, remote production readiness, or
broker authority.

No commit, tag, or push is performed by this review.
