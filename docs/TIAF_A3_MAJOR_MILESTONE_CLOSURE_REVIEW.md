# TIAF A3 Major Milestone Closure Review

## 1. Closure scope and decision

**Review date:** 2026-09-11, Asia/Kolkata  
**Accepted implementation head:** `68134f677e42e265cb23f0d18a0ba9f3228e2b0f`
(`tiaf-a3.10`)  
**Decision:** `READY_TO_FREEZE_A3`

This review covers frozen A1/A2 and all accepted A3 work through A3.10,
including Tapetide, Yahoo, authoritative confirmation and A3.6.2. It makes no
live call and implements no A4-A10, TI Shell, monitoring, forecasting or
source/citation-fabric capability. The changes made by the review are
documentation/governance corrections only.

The repository remains aligned with its north star. It builds evidence first,
keeps deterministic A2 visible beside richer A3 interpretation, treats
`WAIT`, `NO_TRADE`, `ABSTAIN`, `CONFLICTED` and
`INSUFFICIENT_EVIDENCE` as useful results, and grants no broker or execution
authority to TI. The objective remains risk-adjusted expected economic utility,
not raw profit or attractive-looking live examples.

## 2. Accepted milestone inventory

Every required A3 tag exists. No tag/code disagreement was found.

| Milestone / tag | Capability and implementation | Acceptance / live truth | Replay / model status | Principal limitation / open IDs |
|---|---|---|---|---|
| A3 architecture / `tiaf-a3-arch` | Specialist, gateway, Planner and ownership architecture | Accepted architecture | Not runtime; no model | Later runtime details are governed by milestone records |
| A3.1 / `tiaf-a3.1` | Immutable Agent/evidence/claim/budget/run contracts and single-specialist runtime | Accepted; `NOT_APPLICABLE` live | JSON reconstruction; no provider/model adapter | Full workflow arrived later in A3.8 |
| A3.2 / `tiaf-a3.2` | Controlled evidence/reasoning gateways, policy, cache, budgets and audits | Accepted; `NOT_APPLICABLE` live-provider claim | Deterministic fake-provider coverage; no-LLM mode; no live model | Model vendor remains replaceable/unbound |
| A3.3 / `tiaf-a3.3` | Technical/market-structure specialist over unchanged A2 facts | Accepted; one prior live A2 RELIANCE capture is `REPLAY_VALIDATED`; four-case fresh attempt stopped on expired Dhan credentials | Exact run reconstruction; zero model calls/tokens/cost | Scalar projection subset; no forecast; DEF-020/022/034/035/038 |
| A3.4 / `tiaf-a3.4` | PIT fundamental contracts, normalization, metrics, gateway and specialist | Accepted; `SYNTHETIC_ONLY` specialist validation | Deterministic reconstruction; zero model use | No broad licensed production feed; DEF-012/013 |
| A3.5 / `tiaf-a3.5` | PIT event/news facts, revision/dedupe, gateway and specialist | Accepted; `SYNTHETIC_ONLY` specialist validation | Deterministic reconstruction; zero model use | No broad licensed production feed; DEF-012 |
| A3.6 / `tiaf-a3.6` | Separate Relative, Sector and Macro specialists | Accepted; Relative is `BOUNDED_LIVE_VALIDATED`; Sector/Macro are `SYNTHETIC_ONLY` | Exact records; zero model use | Explicit mappings and provider-supplied context; DEF-012/047 |
| A3.6.1 / `tiaf-a3.6.1` | Provider-neutral MI routing, native/canonical evidence, conflicts, graph and research foundation | Accepted deterministic fabric. Exact-current Tapetide matrix is `LIVE_ATTEMPT_FAILED` on quota; Yahoo follow-up is `BOUNDED_LIVE_VALIDATED` | Provider-free replay; zero model use | Tapetide coverage/quota and broad production source governance; DEF-012 |
| Authoritative follow-up | Configured official-source acquisition and claim reconciliation | `BOUNDED_LIVE_VALIDATED`: 3 reads, 2 official artifacts, one typed not-found | Exact offline replay; zero model use | Not a crawler; no complete NSE/BSE/IR coverage; DEF-012/013 |
| A3.6.2 / `tiaf-a3.6.2` | Integrated multi-source research, confirmation, graph and quality/PIT context | Accepted; `BOUNDED_LIVE_VALIDATED`: 12 read-only calls across four symbols | Exact provider-free replay; zero model use | Conservative gaps and limited source coverage remain explicit |
| A3.7 / `tiaf-a3.7` | Separate Derivatives Context, Opportunity Quality and Opportunity Risk specialists | Accepted deterministic/user-level; Dhan chain attempt is `LIVE_ATTEMPT_FAILED` before evidence | 18/18 run reconstructions; zero model use | Rich derivative families and live acquisition remain unavailable; DEF-039-046 |
| A3.8 / `tiaf-a3.8` | Instrument-aware Planner, bounded waves, shared budgets/evidence, replans and framework adapter | Accepted/frozen; `SYNTHETIC_ONLY` public matrix | `REPLAY_VALIDATED`; serial/LangGraph semantic parity; zero model use | No durable queue/distributed operation; DEF-009/010/011 |
| A3.9 / `tiaf-a3.9` | Captured-input structured underlying opportunity intelligence | Accepted/frozen; `SYNTHETIC_ONLY` public matrix | Recorded plus pure assembly replay; zero new model use | No rank, arbitration, position action, expression or forecast |
| A3.10 architecture / `tiaf-a3.10-arch` | Capture/replay/comparison/cost/failure design | Accepted architecture | Not a separate runtime claim | No closure decision by design |
| A3.10 / `tiaf-a3.10` | Content-addressed A3 packages, replay, A2 comparison, cost/failure and closure-evidence seam | Accepted offline; `REPLAY_VALIDATED` | 14/14 public cases; provider/model-disabled replay | Local corpus, no arbitrary PIT history/scheduled outcomes; DEF-049-051 |

Historical milestone studies retain the status of the run they describe. In
particular, the Tapetide `HOLD` is not rewritten as a successful exact-current
Tapetide matrix merely because the provider fabric was later tagged and Yahoo
and A3.6.2 passed their separate bounded live matrices.

## 3. Cumulative capability inventory

The accepted A1-A3 stack is coherent:

| Layer | Accepted ownership |
|---|---|
| A1 | Provider-neutral factual data, identity, normalization, runtime coordination and immutable `AnalysisContext` |
| A2 | Deterministic features, indicators, derivative facts, MTF/relative context, baseline scoring/ranking and captured replay/evaluation |
| A3 | Cited specialist interpretation, controlled evidence/model seams, MI acquisition/normalization, Planner orchestration, structured opportunity observation, cumulative replay/comparison/cost/failure evidence |
| A4 and later | Arbitration, positions, option/future expression, calibrated forecasting/learning, integrations and production operations; not implemented by this review |

The cumulative corpus covers positive, negative, mixed, `NO_TRADE`, `WAIT`,
`WATCH`, `AVOID`, `CONFLICTED`, `INSUFFICIENT_EVIDENCE`, provider failure,
fallback, stale/partial evidence, non-F&O, unknown applicability, budget denial,
tamper, policy mismatch, replay, known-zero model cost and unknown/unpriced
provider cost. Synthetic coverage is not described as live coverage.

## 4. A2/A3 relationship

The core invariant holds:

> A2 is deterministic benchmark truth; A3 is richer specialist interpretation
> and structured opportunity intelligence.

A3 keeps A2 assessment identity, direction, class, score and fingerprint. It
does not mutate or overwrite A2, recalculate A2 indicators/features, or turn
A2/A3 disagreement into a winner. A3.9 retains A2 `NO_TRADE` alongside states
such as `WATCH`; A3.10 classifies that relationship observationally. A3 is not
a second fitted baseline: its component claims, conflicts, missing evidence,
rule traces and confidence bases remain individually visible.

## 5. Provider, evidence and provenance status

Provider-native observations survive before canonical projection. Mapping
quality, provider/source identity, timestamps, evidence IDs and contradiction
groups remain explicit. Yahoo `.NS` suffixes remain adapter-local; canonical
subjects remain provider-neutral. Tapetide/Yahoo routing and fallback are
market-intelligence evidence routing, not a hidden replacement for Dhan's
quote/OHLCV/F&O data surface.

Specialists and the A3.9 assembler contain no provider transport. MCP imports
are confined to provider connector modules; LangGraph imports are confined to
the workflow adapter. The authoritative gateway retains discovered claims,
official document identity/hash, parser limitations and field-level
confirmation without translating `NOT_FOUND` or `AMBIGUOUS` into falsehood.

Current internal lineage is sufficient to freeze A3: every material emitted
claim has evidence/citation references and replay identity. It is not yet the
future report-level Source/Provenance/Citation Fabric. Source licensing,
display/citation compression, durable graph storage, exact historical
availability and broad source governance remain post-A3 work.

## 6. Replay status

A3.10 composes, rather than erases, the useful replay levels:

- A2 snapshot/baseline replay remains the deterministic benchmark;
- Agent and MI records retain their local audit/reconstruction identities;
- A3.8 captures the bounded workflow and child results;
- A3.9 replays captured-input assembly without reacquisition or specialist run;
- A3.10 packages A2, A3.8 and A3.9 as integrity-checked content-addressed blobs.

Recorded replay is self-contained and fails on missing/tampered artifacts.
Deterministic verification re-executes only eligible deterministic components.
Future model-backed outputs are recorded-only, not silently re-inferred. Policy
comparison creates a new comparison record and is not called historical
replay. Provider/model/network/framework guards prove offline isolation.

## 7. Cost and failure status

A3.8 reservation settlements are accounting leaves. Nested provider-attempt
detail is linked but not debited twice. Historical/original usage, held usage
and replay execution usage are separate. Fallback, failure and reuse remain
visible. Configured cost units are not mislabeled as money; provider/model
monetary knowledge is one of `KNOWN_ZERO`, `KNOWN_NONZERO`, `UNKNOWN`,
`UNPRICED` or `NOT_APPLICABLE`. Missing pricing never becomes zero.

Failure projection retains the original child type/code/message digest and
provider, specialist, node, attempt, artifact and usage lineage. Provider,
specialist, orchestration and replay/capture failures remain distinct. Partial
survival cannot become fabricated completeness; integrity failures abort
replay rather than becoming market evidence.

## 8. Live-validation claims and non-claims

| Surface | Truthful status | Claim boundary |
|---|---|---|
| Dhan A1/A2 factual foundation | `LIVE_VALIDATED` | Accepted milestone studies; not rerun for this closure |
| A3.3 Technical | `REPLAY_VALIDATED` | Prior live RELIANCE A2 capture reconciled; fresh four-case attempt failed on expired credentials |
| A3.4 Fundamental specialist | `SYNTHETIC_ONLY` | No broad licensed production adapter claim |
| A3.5 News/Event specialist | `SYNTHETIC_ONLY` | No broad licensed production adapter claim |
| A3.6 Relative | `BOUNDED_LIVE_VALIDATED` | Three symbol/benchmark pairs; sector/macro remain synthetic |
| Tapetide exact-current A3.6.1 matrix | `LIVE_ATTEMPT_FAILED` | Quota stopped the exact matrix; historical partial successes remain evidence, not a pass |
| Yahoo MI provider | `BOUNDED_LIVE_VALIDATED` | 10 read-only calls, deterministic Tapetide-rate-limit fallback, exact replay |
| Authoritative confirmation | `BOUNDED_LIVE_VALIDATED` | Three configured reads; no complete-source/crawler claim |
| A3.6.2 integrated research | `BOUNDED_LIVE_VALIDATED` | 12 read-only calls, four subjects, provider-free replay |
| A3.7 derivatives specialists | `LIVE_ATTEMPT_FAILED` and `REPLAY_VALIDATED` | Dhan failed before active-expiry evidence; deterministic cases passed |
| A3.8-A3.10 | `SYNTHETIC_ONLY` and `REPLAY_VALIDATED` | No live/model/profitability claim |
| Forecasting/profitability | `NOT_APPLICABLE` | No calibrated forecast, realized-value or profitability claim exists in A3 |

No new live call was necessary or made during closure.

## 9. Deferral burn-down

The binding, row-by-row disposition is in the
[deferral register](TIAF_DEFERRAL_REGISTER.md). All 43 records active at review
entry were classified:

| Classification | Count | IDs |
|---|---:|---|
| `CLOSE_NOW` | 1 | DEF-002 |
| `KEEP_DEFERRED` | 27 | DEF-004, 006, 014-016, 020-021, 025-032, 034, 036, 038-046, 048 |
| `PROMOTE_TO_POST_A3_ARCH_REVIEW` | 13 | DEF-003, 007, 009-011, 013, 022, 024, 035, 047, 049-051 |
| `NEEDS_REWORDING` | 2 | DEF-008, DEF-012 |
| `MUST_FIX_BEFORE_A3_FREEZE` | 0 | None |
| Newly `OBSOLETE / SUPERSEDED` | 0 | None |

DEF-002 is implemented by A3.1-A3.10. DEF-008 now distinguishes unimplemented
primary quote/OHLCV/F&O fallback from implemented MI fallback. DEF-012 now
distinguishes implemented bounded sources from unresolved broad licensed
production acquisition. At the time of closure, status totals were 39
DEFERRED, 3 PLANNED, 4 IMPLEMENTED, 3 REJECTED and 2 SUPERSEDED.

The later
[A3 sub-milestone deferral-discovery audit](STUDY_A3_SUBMILESTONE_DEFERRAL_DISCOVERY_AUDIT.md)
found four A3-specific records that were absent from that entry inventory:
DEF-052 production model-backed reasoning, DEF-053 cross-candidate A3
opportunity analysis, DEF-054 user-facing explanation/citation rendering and
DEF-055 monetary pricing/cost attribution. All four remain deferred and none
is a freeze blocker. Corrected current totals are 55 records: 43 DEFERRED, 3
PLANNED, 4 IMPLEMENTED, 3 REJECTED and 2 SUPERSEDED. Nothing was dropped.

## 10. TBD architecture impact

| Non-authoritative note | Classification | A3 impact |
|---|---|---|
| TI System Architecture Thesis | `REQUIRES_POST_A3_ARCH_CONSOLIDATION` | Current typed packages and A3.9 service seam are compatible, but a curated public capability boundary is not yet formalized |
| TI Shell Thesis | `REQUIRES_POST_A3_ARCH_CONSOLIDATION` | A future Shell can call typed capabilities; it must not shell out to scripts or own intelligence |
| Source/Provenance/Citation Fabric | `REQUIRES_POST_A3_ARCH_CONSOLIDATION` | A3 supplies internal lineage; public/report citation and source governance remain to be designed |
| Monitoring Architecture | `REQUIRES_POST_A3_ARCH_CONSOLIDATION` | A3 fingerprints, budgets and selective invalidation are useful inputs; durable cadence/queue/health ownership remains unresolved |
| Forecasting/Ensemble/Learning Architecture | `REQUIRES_POST_A3_ARCH_CONSOLIDATION` | A3 preserves the forecast-consumer seam but produces no forecast/probability; A7 remains owner |
| CLI/Web Interaction Architecture | `REQUIRES_POST_A3_ARCH_CONSOLIDATION` | Existing scripts are diagnostics, not an API; future clients should converge on typed application operations |
| TBD notes index | `REQUIRES_POST_A3_ARCH_CONSOLIDATION` | It must index all current TBD notes and keep them explicitly non-authoritative |

The compatible working idea is that TI_CORE is the intelligence kernel and
typed/versioned capabilities are consumed by Shell, Web, Agents, TradeMonitor,
scanners and external applications without exposing Core internals. Current
packages do not prevent that design, but `tiaf.app` is still bootstrap-only and
scripts call lower-level seams directly. That is a future surface-governance
issue, not an A3 semantic or correctness defect.

**Post-A3 consolidation required, no A3 blocker.** None of the TBD notes is
promoted to authoritative architecture by this review.

## 11. Architecture alignment findings

### Ownership and authority

No accepted A3 API places/modifies/cancels an order; issues `BUY`/`SELL` or
position actions; selects CE/PE, strike, expiry, strategy or quantity; or emits
a calibrated probability. A3.9 states are observations, not A4
recommendations. TradeMonitor remains the future governor and execution
coordinator; the broker remains final execution truth.

### Layering versus duplication

The code has several evidence, assessment, routing and replay contracts, but no
harmful duplicate was found:

- A1 factual models, A3 evidence references, MI native/canonical records, A3.9
  source locators and A3.10 blob references represent different boundaries;
- A2 candidate class, specialist stance/detail, A3.7 quality/risk and A3.9
  observation state retain distinct meanings;
- data-runtime coordination, A3.2 authorization and A3.6.1 provider routing
  enforce different scopes;
- layered replay retains local identities while A3.10 composes them.

This layering is complex, but each layer protects a material invariant:
provider neutrality, least privilege, immutable evidence, deterministic
benchmark preservation, captured orchestration or package integrity. The safe
simplification is future facade/capability consolidation, not merging accepted
domain contracts.

### Replaceability

Providers remain registry/adapter-bound. MCP/Yahoo/Tapetide code does not leak
into specialists or canonical domain contracts. LangGraph remains adapter-local
and serial/LangGraph semantics match. Model vendors are behind the A3.2
protocol and no live vendor is required. A3.9 neither reacquires evidence nor
recomputes A3.8; replay requires no live service.

## 12. Residual risks

These are accepted limitations, not freeze blockers:

1. Live derivative acquisition failed in the A3.7 acceptance attempt; richer
   derivative families remain DEF-039-046.
2. Tapetide's exact-current standalone matrix retained `HOLD` due quota, while
   Yahoo and integrated A3.6.2 separately passed bounded live validation.
3. Fundamental/news/sector/macro production coverage and licensing are not
   comprehensive; missing and ambiguous evidence must remain visible.
4. No exact arbitrary historical reconstruction, scheduled outcome acquisition
   or persistent/distributed replay/graph infrastructure exists.
5. No production health/SLO/circuit-breaker/retry-queue architecture exists.
6. No empirical profitability, forecast calibration or live model intelligence
   has been established.
7. The public capability/API boundary is incomplete; direct diagnostic scripts
   should not become permanent consumer contracts.

## 13. Corrective actions

No runtime or architecture correction is required before freeze. Closure makes
only these small documentation/governance corrections:

- reconcile A3.7-A3.10 and major-stage status across indexes;
- close DEF-002 and clarify DEF-008/DEF-012;
- preserve historical live `HOLD`/failed-attempt records while pointing to
  later, separate accepted evidence;
- index and classify all current TBD notes; and
- establish this report as the A3 major closure evidence.

## 14. Regression and quality-gate evidence

The closure reran the 14-case A3.10 offline public matrix and focused
architecture/security/replay tests before the final repository-wide gates.

| Gate | Closure result |
|---|---|
| `.venv/bin/python scripts/a3_10_user_acceptance.py` | PASS: 14 / FAIL: 0; offline, no provider/model calls |
| Focused architecture/security/replay selection | 72 passed in 60.42s |
| `.venv/bin/pytest -q` | 1,921 passed in 98.51s |
| `.venv/bin/python -m compileall src scripts` | Passed |
| `.venv/bin/ruff check src tests scripts` | All checks passed |
| `.venv/bin/mypy src tests` | No issues in 445 source files |
| `.venv/bin/python -m pip check` | No broken requirements; non-blocking pip-cache permission warning |
| `git diff --check` | Passed |
| Documentation relative-link check | 154 repository-relative Markdown links checked; none missing |
| Scoped secret scan | 317 source/script/fixture text files checked; no credential-shaped literals |

## 15. Final closure decision

`READY_TO_FREEZE_A3`

There is no correctness blocker, ownership leak, A2 mutation, replay/cost/
failure inconsistency, unclassified active deferral or TBD-disclosed A3 blocker.
The subsequent sub-milestone discovery audit reconciled four omitted governance
records without identifying a runtime or pre-freeze blocker.
The exact recommended major baseline tag is **`tiaf-a3-baseline`**, after user
review and a separate authorized commit of the closure documentation. This
review does not create that commit or tag.

## 16. Exact next step

Do not start A4 automatically. After the A3 closure documentation is reviewed,
committed and tagged `tiaf-a3-baseline`, run a dedicated **post-A3 architecture
consolidation**. Reopen the TI System Architecture, TI_CORE/public capability
boundary, TI Shell, Source/Provenance/Citation Fabric, monitoring, forecasting
and roadmap-alignment notes; derive concrete architecture work items; decide
whether a small realignment belongs before A4; only then authorize A4.
