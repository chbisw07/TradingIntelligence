# TIAF A5 Architecture Review

## Decision

**READY_TO_IMPLEMENT_A5_1**

The accepted design is
[TIAF A5 Position Intelligence Architecture](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md).
This is a documentation/design decision only. No A5 runtime, facade descriptor,
Shell command, provider/model/broker call, scheduler, TM integration, A6/A7
behavior, service or storage infrastructure was added.

## 1. Review basis

The review reconciled the system and deployment architectures, A4 architecture
and closure, Shell architecture/implementation, capability map, implementation
targets, roadmaps, deferral register, frozen A0 position contracts, A4 result and
capture contracts, facade lifecycle/catalog, A3.8 planner seams, and the
non-authoritative monitoring idea cache.

The repo contains no implemented TM integration or current-position service.
The A0 position models are generic frozen `1.0` contracts and cannot carry the
new truth, lineage, posture, monitoring and replay semantics without an unsafe
reinterpretation. A5 therefore needs additive contracts.

## 2. Key decisions

| Question | Decision |
|---|---|
| What does A5 own? | Position-aware, evidence-linked advice and monitoring intent. |
| What is position truth? | The explicitly supplied, versioned TM/broker snapshot. |
| Does A5 own lifecycle? | No operational lifecycle; it owns analytical posture only. |
| Are `RISK/PROTECTED/FREE/TRAIL` canonical? | No. Replace with `CAPITAL_AT_RISK`, `RISK_REDUCED`, `PROFIT_PROTECTION_ACTIVE`, `UNDETERMINED`; keep trailing as advice. Reject “free.” |
| Does A5 alter A4? | No. It cites an immutable A4 result or comparable successor. |
| Does A5 set executable stops/targets? | No. It may cite non-executable supplied structural levels. A6/TM own expression/translation. |
| Does A5.1 support multi-leg policy? | No. Preserve shape and fail explicitly; never flatten. |
| Is A7 required? | No. Forecast evidence is optional and absent by default. |
| Is monitoring implemented? | No. Only immutable mandate/refresh-need contracts are designed. |
| Is Shell part of A5.1? | No. Capability-first exposure follows accepted runtime. |

## 3. Complexity audit

1. **Is A5 scope too broad?** It would be if it included acquisition,
   scheduling, multi-leg expression, broker actions or TM governance. Those are
   excluded. A5.1 is one deterministic single-position assessment plus replay.
2. **Should lifecycle and recommendation be separate?** Yes. Operational state,
   analytical posture, thesis health, recommendation and mandate lifecycle are
   orthogonal.
3. **Are the proposed short state names safe?** `FREE` is not; `TRAIL` is an
   action/mode; `RISK` is too absolute; `PROTECTED` overstates certainty. The
   revised posture names state exactly what evidence supports.
4. **Who owns exact stop prices?** A5 may cite a supplied structural reference,
   but A6/TM own executable translation, order parameters and quantity.
5. **How much monitoring is needed now?** Immutable mandate identity,
   position linkage, objective/horizon, lifecycle, evidence/freshness intent,
   typed triggers, next-due hint and policy/budget refs. Nothing operational.
6. **Does this duplicate TM?** No. A5 consumes TM truth and emits immutable
   advice. TM can reject/adapt/ignore it and remains lifecycle/risk governor.
7. **Does this duplicate A4?** No. A5 consumes and preserves A4 thesis,
   invalidations, conflict and lineage; it does not re-arbitrate.
8. **What remains TBD?** Candidate-watch lifecycle, cadence calculation,
   calendars, scheduler/queue/retry/recovery, adaptive budgeting, dependency-
   correct incremental execution, multi-leg policy and operational integration.
9. **What is the minimum implementable slice?** The six-part A5.1 scope in the
   authoritative architecture, with no live dependency.

## 4. Monitoring idea-cache dispositions

The disposition applies section by section to
[`TBD_TI_MONITORING_ARCHITECTURE.md`](TBD_TI_MONITORING_ARCHITECTURE.md).
`PROMOTE` below means only the revised subset stated, not verbatim adoption.

| TBD section | Disposition | A5 disposition |
|---|---|---|
| 1. Purpose | `PROMOTE_TO_A5_ARCHITECTURE` | Preserve typed mandates over shared instruments; scope A5 to positions. |
| 2. Semantic Lifecycle States | `SPLIT` | Promote `ACTIVE_POSITION`/`INACTIVE`; keep candidate `PASSIVE`/`ACTIVE_WATCH` TBD; reject colors as domain state. |
| 3. Instrument vs WatchMandate | `PROMOTE_TO_A5_ARCHITECTURE` | One instrument may have multiple immutable mandates; A5 mandate requires a position reference. |
| 4. Separate Orthogonal Dimensions | `PROMOTE_TO_A5_ARCHITECTURE` | Keep lifecycle, horizon, objective, priority, freshness and depth separate. |
| 5. WatchMandate | `SPLIT` | Promote minimal immutable intent; mutable runtime/cadence state stays TBD. |
| 6. Selective Evidence Plans | `PROMOTE_TO_A5_ARCHITECTURE` | Promote typed evidence-family needs; exact acquisition profiles remain later policy. |
| 7. Independent Evidence Clocks | `REVISE_AND_KEEP_TBD` | A5 records per-family freshness intent; scheduler clock calculation and calendar semantics remain TBD. |
| 8. Scheduled + Event-Driven Monitoring | `SPLIT` | Promote typed trigger/next-due intent; scheduling and dispatch stay TBD. |
| 9. Refresh Does Not Mean Full Reanalysis | `SPLIT` | Promote successor/delta principle; A5.1 safely recomputes its small whole assessment. |
| 10. Dependency-Aware Incremental Recompute | `REVISE_AND_KEEP_TBD` | Fingerprint dependencies first; runtime incremental execution awaits correctness proof. |
| 11. Shared Evidence, Separate Analysis State | `PROMOTE_TO_A5_ARCHITECTURE` | Adopt as a hard boundary. |
| 12. Scheduler Architecture | `KEEP_TBD` | No scheduler, queue or worker in A5. |
| 13. Priority Model | `SPLIT` | Promote priority intent only; no queue/preemption guarantee. |
| 14. Adaptive Cadence | `KEEP_TBD` | Requires accepted calendars, outcomes and operations evidence. |
| 15. Configuration Profiles | `REVISE_AND_KEEP_TBD` | Permit versioned policy/profile refs; do not freeze YAML or named production profiles. |
| 16. Budget-Aware Scheduling | `SPLIT` | Carry budget/policy refs; allocation, degradation and dispatch remain runtime work. |
| 17. Market-Calendar Awareness | `KEEP_TBD` | DEF-007 remains unresolved; no session-aware claim. |
| 18. Active Position / TM Integration | `SPLIT` | Promote authority/link contract; operational integration remains DEF-004/A8. |
| 19. Agent/Analysis Boundary | `PROMOTE_TO_A5_ARCHITECTURE` | A5/specialists do not schedule or acquire implicitly. |
| 20. Auditability | `SPLIT` | Promote semantic capture/fingerprints/replay; operational attempt logs/metrics stay TBD. |
| 21. Failure Semantics | `PROMOTE_TO_A5_ARCHITECTURE` | Adopt explicit stale/partial/error outcomes, revised for advice versus dispatch. |
| 22. Performance Principles | `SPLIT` | Preserve bounded/delta principles; do not claim batching, caching or incremental runtime. |
| 23. Roadmap Placement | `SUPERSEDE` | A5 contracts monitoring intent; A8 integrates TM; A9 candidate intake; A10 durable operations. |
| 24. Open Questions | `SPLIT` | Position mandate minimum is resolved here; scheduler/cadence/calendar/candidate questions remain TBD. |
| 25. Working Principle | `SPLIT` | Promote typed independent semantics; keep operational claims and adaptive cadence TBD. |

Nothing is rejected wholesale. The only rejected semantics are color-as-domain
state, a mutable mandate as scheduler state, and any implication that a hint is
a guaranteed job.

## 5. Deferral reconciliation

No deferral is closed and no new ID is created.

| ID | Clarification after A5 architecture | Revisit |
|---|---|---|
| DEF-004 | A5 defines the advice/snapshot seam only; real TM integration remains absent. | A8 |
| DEF-005 | A5 reinforces the permanent no-broker-execution boundary. | Rejected/non-goal |
| DEF-007 | A5 can evaluate explicit age policy only; market-calendar freshness remains absent. | Before scheduled monitoring |
| DEF-009 | A5 capture remains local/filesystem-oriented; no durable/distributed state. | A10/operational need |
| DEF-010 | Mandate and trigger intent are architected; queue, dispatch, retry and recovery remain deferred. | A10 or separately gated operations |
| DEF-011 | Provider health remains outside position advice. | A10/hosting need |
| DEF-014 | Acquisition-time-only option-chain evidence remains labeled; A5 cannot repair event time. | Provider contract review |
| DEF-022/035 | Forming-bar and persistent price-event lifecycles remain absent; A5 cites only accepted supplied facts. | Event/data review |
| DEF-041/042/046 | Temporal OI, cross-expiry and dealer-positioning semantics remain absent; A5 never infers them. | A6 closure |
| DEF-049 | A5 offers captured replay, not arbitrary historical reconstruction. | A7/A10 review |
| DEF-050 | Local content-addressed capture is sufficient for A5.1. | A10/scale trigger |
| DEF-051 | A5 may emit outcome/refresh intent, not schedule acquisition. | A7 policy/A10 runtime |
| DEF-054 | Existing bounded Shell explanation remains sufficient; A5 adds no presentation runtime. | Later report/Web |

## 6. Acceptance and implementation gate

The 26-case minimum corpus in the architecture covers posture, thesis,
recommendation, failure, successor, replay, monitoring intent, TM non-authority,
unsupported multi-leg behavior, timestamps and known-zero model usage.

A5.1 is ready because each output has one owner, each factual conclusion has a
captured input, missing truth fails closed, replay needs no external call, and
the implementation can be completed without TM, A6, A7 or a scheduler.

Exact A5.1 scope:

- immutable additive input/result/mandate/capture contracts;
- deterministic single-open-position policy and assessment;
- identity/freshness/A4-lineage/citation checks;
- posture, thesis health, recommendation and refresh-need output;
- content-addressed capture, offline replay, verification and policy comparison;
- deterministic corpus, including unsupported multi-leg and authority tests.

Exact next prompt title:

**`TIAF_A5.1 — POSITION INTELLIGENCE CONTRACTS + DETERMINISTIC SINGLE-POSITION BASELINE IMPLEMENTATION`**
