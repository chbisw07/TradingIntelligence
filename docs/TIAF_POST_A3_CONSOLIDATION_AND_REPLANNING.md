# Post-A3 Consolidation and Replanning

**Subsequent status / historical scope:** the transition below completed through
source foundation, local facade and frozen A4. A5.1/A5.2 and R1 are now accepted.
This record's next-step instructions, counts and architecture-entry evidence
remain historical. The [post-R1 consolidation](TIAF_POST_R1_DOCUMENTATION_CONSOLIDATION_AND_SYNCHRONIZATION.md)
and [current roadmap](IMPLEMENTATION_ROADMAP.md) own today's documentation status
and final A5 freeze check; they do not alter this record's accepted principles.

## 1. Decision, authority and verified entry

**Decision: `READY_FOR_POST_A3_FOUNDATION_IMPLEMENTATION`.**
**Architecture baseline readiness: `READY_TO_TAG_POST_A3_ARCHITECTURE`.**

Authoritative transition decision record, **2026-09-11 (Asia/Kolkata)**.
Entry worktree was clean at `eabff0c` (`docs(architecture): establish A4 and
deployment architecture`). A1/A2 remain frozen; A3.1–A3.10 remain frozen at
`tiaf-a3-baseline`, `e690da2ce0a1dc0d3eb263c3b9e8e59ad52b6212`.
Readiness means the design can be checkpointed after review; no tag is created,
and an uncommitted worktree is not itself the eventual tag target.

This record owns the current transition sequence and bounded implementation
gates. [System architecture](TIAF_SYSTEM_ARCHITECTURE.md) owns the logical kernel
and capability boundary; [source architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md)
owns source/claim semantics; [A4 architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md)
owns challenge/arbitration; [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md)
owns hosting. Narrow amendments in this pass clarify their relationship, not
replace frozen runtime behavior. The roadmap owns major milestones, the register
owns stable deferrals, and this record resolves the transition timing.

The supplied brief defines this documentation/governance task. It is not evidence
that proposed contracts or consumers exist. No runtime/source/scripts/tests,
dependencies, providers, models, infrastructure or product plan are implemented.
No live call, credential read, commit, tag or push is performed.

## 2. Accepted architecture as one system

North star:

> TI should act as a disciplined decision-intelligence system working in the
> user's economic interest, combining deterministic evidence, specialist
> intelligence, higher-order reasoning, probabilistic forecasting and later
> feedback learning while preserving risk control, explainability, auditability,
> evidence provenance, reproducibility where possible, uncertainty, cost
> discipline and authority boundaries.

Maximize risk-adjusted expected economic utility, not raw profit at any cost.
This is an objective, not validated profitability. WAIT, NO_TRADE, AVOID,
CONFLICTED, ABSTAIN and INSUFFICIENT_EVIDENCE remain legitimate outcomes with
their layer-specific meanings, not one replacement enum.

| Accepted effort | Preserved decision | Consolidation finding |
|---|---|---|
| [Pass 1](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md) | Logical TI_CORE; curated typed/versioned public, engineering and private boundaries; trusted admission. | No `ti_core` relocation or import-based sandbox. Local facade timing now selected explicitly in §7. |
| [Pass 2](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md) | Field-scoped authority, proposition comparability, qualified independence, append-only disputes, frozen capture lineage. | Foundation is immediate implementation work, not citation UX or a source-brand score. Model priors can motivate inquiry, never fill factual gaps. |
| [Pass 3](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md) | Two roles: Challenger and deterministic Arbitrator; preserved dissent, bounded research, optional selective model. | Existing escalation is compatible with open-world reasoning; explicit prior/hypothesis/admission wording added without increasing limits. |
| [Deployment review](TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md) | Trusted local Python, isolated requests, single-writer filesystem replay; conditional services/workers. | No operational foundation blocks semantic work. Small local facade follows foundation; production remains gated. |

Current implementation seams were checked: [A3.8 request](../src/tiaf/planner/models.py)
requires no-LLM and rejects future evidence; [controlled services](../src/tiaf/workflows/services.py)
compose existing acquisition and process-local single-flight; [reasoning requests](../src/tiaf/agents/gateways/contracts.py)
still use SpecialistId; [A3.10 store](../src/tiaf/a3_hardening/store.py) is local
check/write/append, not transactional multi-writer durability.
[Arbitration](../src/tiaf/arbitration/__init__.py) is reserved;
[app context](../src/tiaf/app.py) is bootstrap metadata, not a facade.
Architecture support is not implementation, live coverage or production acceptance.

## 3. Bounded open-world reasoning amendment

A4 is not permanently restricted to the first evidence bundle. A model/Agent
may identify a material information gap, formulate a research hypothesis and
request evidence through governed TI capabilities. **Model prior knowledge may
motivate inquiry; it is not canonical factual evidence.** A hypothesis that
introduces a new subject/event must remain explicitly unverified. It needs a
bounded semantic question and materiality link, not invented source/claim IDs.
An actual factual premise still needs resolvable admitted evidence and typed
value/scope validation. Unsupported conjecture alone cannot upgrade a disposition.

```text
admitted A2/A3 evidence -> higher-order challenge
  -> material hypothesis / typed evidence need
  -> trusted admission -> A3.8 / gateway / MI research capability
  -> attributable acquisition -> provenance / normalization / authority /
     entitlement / PIT admission -> successor A4 semantic projection
  -> selective re-challenge and deterministic re-arbitration
```

The future A4-to-Planner bridge translates semantic needs; no Agent acquires
directly, chooses arbitrary URLs/tools or changes grants. Unsupported/out-of-
coverage questions remain unmet; the architecture does not add a general browser
or new research provider. Source text is untrusted data, never instructions.
Default captured/no-LLM mode remains zero live calls and zero model calls.
Authorized enrichment remains at most one round/two projection cycles; optional
Challenger calls at most one per cycle/two total, zero Arbitrator model calls,
with finite shared tool/token/cost/deadline limits and no reset in child work.
Stop on denial, unavailable capability, no relevant new information, budget,
deadline or round limit. No recursive free-form research loop.

Reprojection of eligible captured data can keep its cutoff. Acquisition after
that cutoff requires a successor run/new as-of and explicit parent link; never
backdate it into the original capture. Upstream composition owns any needed
A1/A2 refresh; A4 cannot recalculate the benchmark. Recorded replay reconstructs
all captured cycles without live provider/model access. A policy change creates
a comparison, not a rewritten original. These are design amendments only.

## 4. Hierarchy and future expression comparison

| Level | Owner | Preserved boundary |
|---|---|---|
| L0 | Raw providers/sources | Native observations, not investment conclusions. |
| L1 | A1/MI normalized and admitted evidence | Canonical identity, provenance, uncertainty, time and entitlement. |
| L2 | Deterministic features/indicators | Compute once under explicit formula/version; higher layers consume facts. |
| L3 | A2 baseline | Immutable score/class/direction and component evidence; benchmark not retuned for examples. |
| L4 | A3 specialists | Independent attributed interpretations; confidence is not probability or a vote. |
| L5 | A3.9 opportunity intelligence | Structured single-underlying observation and preserved conflicts/gaps. |
| L6 | A4 | Challenge, counter-thesis, governed evidence needs and deterministic arbitration. |
| L7 | A5/A6 | Position advice and valid trade-expression candidates, not broker execution. |
| Overlay | A7 | Empirical forecast/outcome/evaluation evidence; no self-training on model prose as truth. |

Scanners are discovery/sensors. Agents are bounded actors, not synonymous with
LLMs. TM is operational governor/risk/lifecycle/execution coordinator; broker is
final live execution/state truth. The DOCX hierarchy was considered as explanatory
reference only; its shorthand "action" or non-action descriptions cannot override
these Markdown owners, A3.9 enums or the explicit A4 NO_TRADE gate.

Long-term dataflow is not a mandatory implementation-order dependency:
A4 surviving thesis + later admitted A7 forecast/risk evidence -> A6 valid
expression candidates -> separately versioned higher-order candidate comparison
-> A5 advice / TM governance -> broker truth. A6 constructs/validates candidate
contracts, expiry/strike/structure/payoff/liquidity constraints and candidate IDs.
Later reasoning may compare **those** candidates against the thesis and admitted
forecast assumptions; it cannot invent a candidate, recompute Greeks/payoffs,
choose an unlisted contract, manufacture probabilities or confer execution rights.
The comparison seam is a future A6/A7 design extension, **not initial A4 scope**.
It preserves all alternatives, source/candidate/forecast versions and non-action.

## 5. TBD dispositions and revisit ownership

TBDs are an **idea cache**: unfinished, non-authoritative thinking preserved so
useful ideas are not forgotten. One useful principle never promotes a whole note.

| Note | Disposition | Promoted / retained / revisit |
|---|---|---|
| [System thesis](TBD_TI_SYSTEM_ARCHITECTURE_THESIS.md) | SUPERSEDE | Authoritative system/deployment documents supersede it as specification; retain original rationale, no duplicate Core implementation. |
| [Shell](TBD_TI_SHELL_THESIS.md) | PROMOTE_SELECTED_PRINCIPLES | Mediator, isolated session and governed capabilities approved. Formal architecture after local facade acceptance, before A5 planning; bounded command-first v0.1 after deterministic A4 acceptance, preferably before A5 implementation. NLP/mixed modes conditional on model/interaction acceptance, not mandatory v0.1. |
| [CLI/Web](TBD_TI_CLI_WEB_UI_INTERACTION_ARCHITECTURE.md) | REVISE_AND_KEEP_TBD | Independent consumers and structured rendering retained. Formal local command subset at Shell architecture; Web/transport at actual consumer/A8 need. Exhaustive internal access and Shell-out-as-API not accepted. |
| [Monitoring](TBD_TI_MONITORING_ARCHITECTURE.md) | REVISE_AND_KEEP_TBD | Shared evidence and TM ownership retained. Before A5 implementation, review bounded mandate/lifecycle/delta semantics; A8 position binding, A9 candidate intake, A10 durable scheduling/recovery. No daemon required for on-demand A5. |
| [Forecasting](TBD_TI_FORECASTING_ENSEMBLE_LEARNING_ARCHITECTURE.md) | REVISE_AND_KEEP_TBD | A7 overlay/calibration/PIT/benchmarks/provenance retained. Revisit architecture at deterministic A6 candidate boundary (earlier contract review allowed); no ensemble hierarchy, model family or trained ranking approved by default. |
| [Source/citation](TBD_TI_SOURCE_PROVENANCE_CITATION_FABRIC.md) | SPLIT | Core semantics approved and assigned foundation; UX remains DEF-054. Minimal captured-source rendering at Shell v0.1, richer bibliography/Web UX later, no re-research. Broad adapters remain DEF-012. |
| [Deployment](TBD_TI_DEPLOYMENT_ARCHITECTURE.md) | SPLIT | Local target/gates promoted; speculative profiles/distributed stack remain TBD. Revisit local service for operational TM/multi-app need, production at A10 gates. |

The TBD index is the navigational summary, not an eighth proposed subsystem.
No entire Shell, monitoring, forecasting or Web product is promoted. Historical
four pass reviews remain unchanged; their next-step wording records the decision
at that time, not the current pending task.

## 6. Deferral reconciliation: all 55 stable records

Classifications below are **planning dispositions**, not new register status
enums. No record is implemented by this pass. Status totals remain 55:
43 DEFERRED, 3 PLANNED, 4 IMPLEMENTED, 3 REJECTED, 2 SUPERSEDED.
Every ID appears once below; ranges include each intervening ID.

| IDs | Disposition | Current next owner / unresolved dependency |
|---|---|---|
| DEF-001, DEF-002, DEF-017, DEF-018 | ALREADY_SATISFIED | Accepted A1/A3/indicator capabilities, not production LLM or A4. |
| DEF-005, DEF-019, DEF-033 | REJECT | Preserve broker-execution exclusion and rejection of redundant aliases/flags. |
| DEF-023, DEF-037 | SUPERSEDE | Existing independent timeframe acquisition/A2 synthesis; distinct MTF indicators/event lifecycle still open. |
| DEF-003 | SPLIT_WITHIN_SAME_STABLE_ID | Activate local facade planning after foundation, before deterministic A4; A8 remote/service remains conditional. PLANNED, not closed. |
| DEF-004 | KEEP_DEFERRED | A8 integration needs TM contracts/freshness/authority; remains PLANNED. |
| DEF-006 | SPLIT_WITHIN_SAME_STABLE_ID | A6 deterministic admissible candidate version first; forecast-enhanced expression only after A7 evidence. Remains PLANNED, no new ID. |
| DEF-007 | KEEP_DEFERRED | Calendar/session recency review before scheduled monitoring; conservative captured-time handling suffices for foundation/A4. |
| DEF-008 | KEEP_DEFERRED | Primary quote/OHLCV/F&O second provider and mapping/operations; MI fallback does not close it. |
| DEF-009 | KEEP_DEFERRED | A10 or earlier demonstrated concurrency/storage need; local sparse graph/filesystem not a durable distributed cache. |
| DEF-010 | SPLIT_WITHIN_SAME_STABLE_ID | Bounded monitoring contracts at A5 review; durable jobs/retry/checkpoint/recovery before unattended operation, normally A10. No queue activation now. |
| DEF-011 | KEEP_DEFERRED | Incremental provider operations at actual exposed-host need/A10; typed failures are not health arbitration. |
| DEF-012 | KEEP_DEFERRED | Licensed production source coverage/operations; bounded open-world requests do not authorize new acquisition surfaces. |
| DEF-013 | KEEP_DEFERRED | A1/A2 adjusted-history extension before adjustment-dependent A7 evaluation; official documents alone do not define adjustments. |
| DEF-014 | KEEP_DEFERRED | Authoritative chain-event timestamp source absent; keep explicit acquisition basis. |
| DEF-015 | KEEP_DEFERRED | Leaf HTTP-call accounting before claiming strict wire-call caps; bounded A4 live bridge must enforce proven scope or decline route. |
| DEF-016 | KEEP_DEFERRED | Future identity work needs authoritative aliases and explicit preferences. |
| DEF-020, DEF-021 | KEEP_DEFERRED | Confirmed-pivot information time / named HalfTrend variant, future A2 library consumer need. |
| DEF-022 | KEEP_DEFERRED | Event/current-bar revision contract before forming-bar features; no live quote insertion into completed-bar A2. |
| DEF-024 | KEEP_DEFERRED | A7 empirical objectives, leakage controls and promotion; replay alone is insufficient. |
| DEF-025, DEF-026 | KEEP_DEFERRED | A6 strategy contracts / separately specified indicator variants; no incidental DSL/custom library expansion. |
| DEF-027, DEF-028, DEF-029, DEF-030, DEF-031, DEF-032 | KEEP_DEFERRED | Session/anchor/binning/variant/ranking-window/provider evidence respectively; future A2 extensions only for specified consumers. |
| DEF-034, DEF-035, DEF-036 | KEEP_DEFERRED | Fixed-window touch counts, frozen price-event lifecycle, prior-session pivots; monitoring/source dispute lifecycle does not supply these contracts. |
| DEF-038 | KEEP_DEFERRED | Future A2 first-class timeframe-specific level identity. |
| DEF-039, DEF-040, DEF-041, DEF-042, DEF-043 | KEEP_DEFERRED | A6 consumer review: delta selection, historical features, temporal OI, cross-expiry, surface contracts. No requirement to implement every family in initial A6. |
| DEF-044 | REWORD | A6/A7 seam: expected-move/POP needs named probabilistic assumptions and empirical calibration, not deterministic premium geometry. |
| DEF-045, DEF-046 | KEEP_DEFERRED | Named max-pain model / evidenced dealer positioning assumptions; A6 only if justified. |
| DEF-047 | KEEP_DEFERRED | A1 classification extension at benchmark/scanner demand; explicit versioned mappings do not implement an automatic mapper. |
| DEF-048 | KEEP_DEFERRED | Future explicit MTF IndicatorBundle context; not FeatureBundle duplication. |
| DEF-049 | KEEP_DEFERRED | A7 arbitrary-history claims need vintage/universe/corporate-action/PIT data; captured replay remains valid without solving all history. |
| DEF-050 | KEEP_DEFERRED | A10 or demonstrated replay-scale/concurrent-writer need, not foundation. |
| DEF-051 | SPLIT_WITHIN_SAME_STABLE_ID | A7 defines admissible outcome acquisition/calendar policy; runtime scheduling/durable attempts before unattended use at A10 or a separately gated earlier slice. |
| DEF-052 | REWORD | Optional A4 model lane may be reviewed before A7 after §9 gates; broader specialist/model integration remains deferred. No production model exists. |
| DEF-053 | KEEP_DEFERRED | Cross-candidate A3/A4 comparison and ranking inside A7 evaluation design after stable per-candidate products; do not invent a pre-A7 leaderboard. |
| DEF-054 | SPLIT_WITHIN_SAME_STABLE_ID | Captured-source explanation rendering with Shell v0.1; richer reports/Web later. Foundation does not close UX. |
| DEF-055 | REWORD | Bounded auditable price knowledge before optional billable models/strict monetary caps; production catalog/attribution at A10. UNKNOWN is not zero or a numeric nonzero estimate. |

No `ACTIVATE_NEXT` record is needed for source foundation: it is already the
immediate prerequisite package, not deferred A3 scope. Local DEF-003 is the next
separate track after it. Current revisit hints are updated where A3 closure is
past; historical closure tables/counts are preserved, not reinterpreted.

## 7. Exact next implementation: POST_A3_PRE_A4_FOUNDATION

Entry: this architecture consolidation reviewed/checkpointed, frozen A3 parent
contracts available, clean or explicitly scoped worktree, no provider/model
credentials needed. Implement **internally, in-process, deterministic and offline**.
No public facade dependency, no service or source discovery task.

| Work package | Contracts/design roles and work | Dependency / exit evidence |
|---|---|---|
| F1 Identity, authority and policy bindings | Separate source/provider/publisher/origin/document-version and assertion occurrence; field/subject/basis/effective-time authority applicability with explicit UNKNOWN; typed scoped policy IDs/versions/digests, never SourceScore. | Frozen native/canonical capture adapters; known/unknown identity and scoped authority fixtures; no invented lineage. |
| F2 Proposition, comparisons and relations | Proposition keys and typed assertion bindings; EXACT/COMPARABLE_WITH_TRANSFORM/NOT_COMPARABLE/UNDETERMINED; explicit transformations; qualified pair/root independence; eight dispute kinds and append-only lifecycle/revision relations. | F1; mismatched scope/unit/period and dependent echoes cannot resolve by vote/brand; cycles/invalid transitions rejected. |
| F3 Confirmation and semantic projection | ConfirmationProjection preserves recorded status separately from field admission; examine all documents/conflicts, no last-write-wins. A4SemanticInputProjection references original A3.10/A3.8/A3.9/A2, indexed claims/qualifications/coverage/exclusions, active/superseded opinions and unchanged A2 relationship. | F1/F2; typed locator/value/scope validation, partial versus mandatory-integrity failure, projection-only A2 limitations. |
| F4 Capture, verification and fixtures | Additive foundation projection envelope referencing unchanged A3 artifacts; deterministic serialization/hashes; recorded replay, pinned-policy verification and explicit new-policy comparison. | F1–F3; all corpus cases, zero acquisition/model execution, original child bytes/hashes preserved. |

Names are design roles; reuse compatible contracts and existing capture/graph
ports before adding small typed records. Do not duplicate the entire evidence
graph/store or place all fields in an untyped metadata bag. Match pass-2 semantics
exactly; uncertain/missing source scope stays unknown. Policy bindings are
resolved by trusted composition, not caller self-grants. Foundation validates
the supplied authorized scope; a public authentication system is not its task.

Migration rules: leave frozen A3 schemas/enums/hashes intact. A new versioned
foundation envelope is **not an A4 result/run that never occurred**. Retain
original capture refs and distinguish full A2 from original projection-only
mode. Resolve required references inside the supplied artifact scope; corruption,
wrong subject/digest or mandatory absence fails closed. Optional missing content
produces named gaps. New policy/revision yields a new projection/comparison;
never modify old decisions or fabricate backfilled availability.

Contracts remain frozen, tuple semantic collections accept lists and emit JSON
arrays; defensive serialization/revalidation handles legacy mutable metadata.
Use aware `ZoneInfo("Asia/Kolkata")`, reject naive values, normalize other zones,
emit `+05:30`. Package `0.1.0`, A0 schema `1.0` and new projection/policy versions
are separate. Do not increment package/schema merely to describe a milestone.

### Foundation acceptance corpus (designed here, not executed foundation tests)

| Case | Required result |
|---|---|
| F01 source/provider/issuer distinction | Preserve source identity and original occurrence, canonical symbol neutral. |
| F02 unknown origin / authenticity | Unknown is explicit, neither shared root nor authoritative fact assumed. |
| F03 scoped authority | Applicability changes by field/time/basis, not provider brand. |
| F04 comparable opposing values | Genuine conflict preserved, zero factual values retained. |
| F05 unit/period/consolidation mismatch | NOT_COMPARABLE/UNDETERMINED; explicit supported transform only. |
| F06 duplicate echoes / partial independence | SAME_ROOT/derived claims not votes; unknown independent status stays unknown. |
| F07 dispute lifecycle | Append-only valid transitions; no disappearance of unresolved disagreement. |
| F08 correction/revision | Correct field scope and availability; original historical capture remains unchanged. |
| F09 conflicting confirming documents | All field assertions retained; no dictionary-order winner. |
| F10 partial/NOT_FOUND/ambiguous confirmation | Recorded status separate from A4 admissibility; NOT_FOUND is not false. |
| F11 full versus projection-only A2 | No invented missing facts or recalculation; original fingerprints unchanged. |
| F12 tampered/missing/wrong-subject references | Mandatory integrity failure versus attributed optional gap. |
| F13 fact/inference/hypothesis/forecast | Model-prior hypothesis/source instructions cannot become canonical facts or permissions. |
| F14 PIT successor boundary | Later acquisition excluded from old cutoff; separately supplied successor with parent link can admit it. No acquisition performed by foundation. |
| F15 policy/version and relation integrity | Missing policy, cycles and fabricated ID/value/path rejected; policy change creates comparison. |
| F16 serialization/offline replay | Lists/tuples/JSON, aware time, defensive metadata, stable semantic fingerprint; no gateway/provider/model call and no mutation of parent artifacts. |

All 16 must be implemented as deterministic tests, with parameterized variants
where useful; this is a case inventory, not a promised pytest count. Add a bounded
offline inspection/capture path only if needed for user-level acceptance; no
new public service or elaborate CLI framework. Live validation is **not required**:
this package projects supplied evidence. Existing authorized captures may be
used offline; their live provenance does not make synthetic variants live tests.

Quality gates for the implementation pass:

```bash
python -m compileall src scripts
pytest -q tests/unit/market_intelligence tests/unit/workflows tests/unit/a3_hardening
pytest -q
ruff check src tests scripts
mypy src tests
git diff --check
```

Also run the new foundation tests explicitly, architecture import/no-call tests,
all F01–F16 and parent-byte/fingerprint preservation checks. Report exact counts
and paths. Use the project venv where needed. Exit decision:
`READY_TO_ACCEPT_POST_A3_PRE_A4_FOUNDATION` only with all gates and zero live/model
calls; otherwise `FIX_REQUIRED`. Acceptance permits a subsequent task, not an
automatic commit/tag or start of A4.

Non-goals: Challenger/Arbitrator runtime; public facade, Shell/Web; new providers,
media/research adapters; model adapter/prompt execution; A5/A6/A7; deployment;
citation UI; SourceScore; broad calendar/adjusted-history/current-bar redesign.

## 8. Facade timing and deterministic A4 sequence

Choose **A: foundation -> narrow local facade/lifecycle -> deterministic A4**
as the planned delivery order. Factual dependency does not force facade before
internal projection/A4 unit work; this ordering stabilizes the trusted caller,
policy and lifecycle seam before live evidence-need integration and avoids
repeating assembly in every consumer. It is a small non-major engineering
foundation, not all of DEF-003 or a network service. Option B postpones useful
admission discipline; C risks coupling semantic foundation to runtime resources.
Minimal internal fixture composition is permitted in foundation, but is not
advertised as delivery of the facade.

Facade entry: accepted foundation plus existing A3 typed seams. Initial published
subset: captured opportunity assembly, foundation projection/inspection and
recorded replay with caller-filtered static descriptors. Trusted bindings hide
registries, policies, filesystem paths and services; no arbitrary reflection/RPC.
Where existing bounded A3.8 acquisition is exposed, explicit authority, entitlement,
budget/effect/deadline and lifecycle tests are mandatory first. No new provider.
Single-writer local persistence and request-local mutable state; no remote auth
stack. Exit: typed list/JSON roundtrips, unauthorized/unsupported denial before
effects, revoked cached/artifact access, isolated requests, exact replay, shutdown
and unknown-usage behavior verified. Do not build exhaustive consumers/catalog.
The facade is mandatory before Shell/public consumer use regardless of sequencing.

After foundation/facade acceptance, separately authorize these A4 work packages
(planning labels, not new tags or already implemented numbered milestones):

1. **A4-D1 contracts and policies:** thesis/premise/challenge/result/uncertainty/
   need records, strict ID/path/value validation, explicit limits and dispositions.
2. **A4-D2 deterministic benchmark:** Challenger and Arbitrator using captured
   projection, hard constraints/argument defeat, dissent and non-action. No LLM,
   source voting, A2 retuning or closed-world claim of complete knowledge.
3. **A4-D3 governed research bridge:** typed needs -> existing Planner/gateways ->
   admitted successor -> selective re-challenge. Deterministic fixtures prove
   denial, no-information, cutoff, leaf budgets, bounded loops and failures.
   Any live acceptance is a separately bounded test of existing routes only.
4. **A4-D4 replay/cost/failure acceptance:** parent capture across cycles, held
   unknown usage, no double debit, offline verification and the pass-3 18-case
   corpus plus explicit model-prior-to-unmet/admitted-need variants.

Each step preserves original A2/A3 captures and must pass its focused/full quality
gates before acceptance. A4-D2 can be evaluated before live bridge availability;
full bounded-open-world runtime acceptance requires D3/D4. Optional model lane
is separate, never a hidden requirement for the deterministic benchmark.

## 9. Optional model lane: DEF-052 and DEF-055

Architecture support exists; production integration does not. Review optional
model-backed Challenger after deterministic A4 and bridge/replay acceptance,
without waiting for all A7 or blocking A5. Do not reuse SpecialistId as an A4
role or relax frozen A3.8 no-LLM validation. Prerequisites:

- additive role-aware gateway using existing permission/reservation/accounting;
- separately approved replaceable model/provider adapter, capability scope and
  prompt/config/schema versions, bounded context and output size;
- privacy/data-egress/retention and entitlement review; source text untrusted;
- structured claim/ID/path/value validation, material hypothesis distinct from
  cited fact, no arbitrary tools or invented source locators;
- finite call/token/deadline and monetary limits with auditable price/currency/
  effective-time assumptions where monetary enforcement is claimed; unknown
  pricing remains unknown and cannot satisfy a strict monetary cap;
- governed research scope and existing successor/no-info/round limits, no model
  permission escalation or recursive research;
- NO_LLM deterministic parity/control, recorded outputs and provider-free replay,
  failure/timeout/required-stage semantics and held uncertain usage;
- versioned evaluation corpus for unsupported assumptions, hallucinated IDs and
  mismatched real values, injection attempts, disagreement, budget stops and
  usefulness against the deterministic A4 benchmark, not attractive live tuning.

The minimal pricing slice supports the specific authorized provider/model, not
the complete A10 billing catalog. DEF-052/055 remain DEFERRED until separately
implemented/accepted; one Challenger adapter cannot close all specialist/model
integration or enterprise pricing/attribution. Broader evaluation/calibration is
A7, production model/price operations A10. Model confidence is never probability.

## 10. Re-evaluated A5–A10 and adjacent tracks

Keep major numbering/order; split dependencies inside later milestones instead
of forcing A7 ahead of all A6. Safety and replay gates accompany every increment,
not just A10.

| Milestone/track | Entry and chosen work | Exit / boundary |
|---|---|---|
| Shell architecture / v0.1 | Architecture after facade acceptance, before A5 planning; command-first same-process v0.1 after deterministic A4, preferably before A5 implementation. | Curated invocation/replay/explain/trace only; no credentials, hidden research or privileged NLP. Engineering convenience, not a hard A5 dependency. NLP/mixed require independent model/interaction gates. |
| A5 position intelligence | Accepted A4 outputs and versioned caller/TM position snapshots; first review bounded mandate/lifecycle, evidence-family clock and delta contracts. | On-demand replayable advice/reassessment with position identity/freshness and original thesis. No scheduler required, no execution authority. A5 precedes A6 because adopted positions already exist. |
| A6 deterministic first | A4 thesis, appropriate A5 risk context where applicable, explicit option/market evidence and candidate constraints. | Valid candidate IDs/contracts, factual geometry/liquidity/payoff assumptions, alternatives and NO_OPTION_TRADE. No expected-move/POP/utility claim without A7 evidence. Not every deferred derivative model required. |
| A7 evaluation/forecasting | Stable A2/A4 controls, A5/A6 records, outcome definitions and permitted PIT dataset; deterministic A6 candidate seam reviewed. | Forecast target/horizon/as-of/model/calibration provenance, leakage-safe walk-forward/out-of-sample evaluation, benchmarks, uncertainty, promotion/rollback. Ensembles/learning/ranking must earn complexity. |
| A6 forecast-enhanced follow-up | Admitted A7 forecast evidence/calibration with compatible A6 candidates. | Versioned higher-order candidate comparison under explicit risk/utility assumptions; no A4 contract creation or TM bypass. May decline due to forecast uncertainty. |
| A8 TM integration | Governed facade, position/advice compatibility/freshness, idempotency/security and operational failure isolation. | TM retains authority and broker credentials/truth; local host preferred when operational, remote only if justified. |
| A9 scanner integration | Stable capability inputs; mapping/mandate interfaces if used. | Independent discovery sensors feed candidates; no scanner-owned duplicate intelligence or unreviewed automatic mapping. |
| A10 production | Real operating demand and retained semantic/audit contracts. | Recovery, quota/health/SLOs, durable jobs/store, retention/privacy, load/fault acceptance. No automatic distributed stack. |

Cross-candidate comparison/ranking (DEF-053) belongs in A7 evaluation architecture,
not an unevaluated A3 leaderboard before A7. Plain per-symbol batching is not
ranking; preserve A2 benchmark and input/product identities. Define universe/PIT,
horizon/objective compatibility, absent/failed candidate handling, ties and
selection bias before ranking. No parameter fitting to named live examples.

Monitoring: TI application orchestration owns future WatchMandate identity,
lifecycle, evidence-family clocks, semantic triggers and delta recomputation
policy. A5 reviews/contracts an on-demand slice before position-linked state;
A8 binds authoritative position references/priority inputs, A9 admits scanner
mandates, A10 schedules durable due work/events. Specialists own none of the
heartbeats/queues. Calendar recency (DEF-007) and outcome scheduling (DEF-051)
must precede claims of correct unattended timing. Price-event lifecycle
(DEF-035) is separate from source-dispute or mandate lifecycle. Do not make a
daemon mandatory for initial on-demand A5, or claim continuous monitoring early.

A7 architecture entry must specify outcome availability, retained data/license
scope, corporate-action and universe assumptions, benchmark/null models, sample
and calibration criteria, regime/horizon stratification and candidate promotion/
rollback. Captured prospective datasets can support bounded evaluation without
solving arbitrary historical PIT reconstruction; do not claim wider coverage.
Ensemble/regime weighting, optimization and feedback learning are hypotheses
until out-of-sample evidence justifies them. Later forecasts enter A4/A6 through
ordinary admitted evidence; they are not model-memory probabilities.

DEF-054: implement a minimal deterministic captured-source renderer with Shell
v0.1 after source foundation/facade. Preserve gaps, conflicts, source qualifiers,
exact locators and access controls; missing artifacts render as unavailable.
No re-research to render a citation. Rich bibliography/compression/Web layout
follow consumer needs; UI prose is never new canonical evidence. No change to
rendering's DEFERRED status merely from this plan.

## 11. Deployment, risks and baseline readiness

Remain trusted local Python, same-process Core/facade and single-writer
filesystem replay. Preserve adapter-local MCP subprocesses. No database, queue,
service, Docker, Kubernetes or cloud dependency now. Add operational admission,
secret/lifecycle/storage protections with each actual consumer; do not wait for
A10 to protect an exposed interface, or bring all A10 infrastructure forward.

Residual risks and explicit containment:

- Source scope/availability/independence can remain unknown: foundation must
  refuse unjustified comparison, not fill gaps from models or source prestige.
- Legacy confirmation/candidate grouping is narrower than general A4 admission:
  inspect all captured fields/contexts in the projection, preserve old status.
- Uncaptured history/calendar/adjustments/live coverage remain incomplete:
  bound dataset/claim scope; no broad live certification from fixture success.
- A3.8 is not a generic A4 role executor; bridge and model request changes must
  be additive and separately tested, with no specialist-ID impersonation.
- Opaque acquisition may hide multiple HTTP calls; strict caps need verified
  leaf accounting or refusal. Timeouts do not prove work stopped/refund cost.
- Filesystem store/caches are not multi-user/durable coordination. Maintain
  ownership restrictions until operations are tested, not simply documented.
- Expression utility and forecast accuracy remain empirical unknowns. Initial
  A6 cannot claim optimized expected utility or profitable recommendations.

None blocks the bounded offline foundation implementation. Architecture/tag
readiness does not assert these risks are solved. A proposed
`tiaf-post-a3-architecture` tag must describe **design consolidation only**, not
foundation/A4 runtime, live coverage or production readiness.

Recommended Git checkpoints (for later explicit authorization, not executed):

1. Review this documentation-only diff and validation; ensure no unrelated files.
2. Commit the consolidated architecture/docs as one reviewed checkpoint.
3. Inspect that exact commit and, if accepted, annotate
   `tiaf-post-a3-architecture` with architecture-only scope. Do not tag the older
   entry HEAD or imply the uncommitted documents are included.
4. Begin a separately authorized foundation implementation from that checkpoint;
   commit/accept it independently with its exact tests before the facade/A4 track.
5. Push only on separate user authorization. No commit/tag/push occurs here.

## 12. Validation and exact next task

Executed focused current-behavior regression:

```bash
.venv/bin/pytest -q \
  tests/unit/workflows \
  tests/unit/a3_hardening \
  tests/unit/agents/test_gateway_architecture_security.py \
  tests/unit/agents/test_reasoning_gateway.py \
  tests/unit/opportunity_intelligence/test_integrity_boundaries.py
```

**156 passed in 79.42s.** Covers existing bounded orchestration, replay/integrity,
no-provider/model execution in recorded paths, reasoning-gateway and authority
boundaries. No live provider/model call was made. Proposed F01–F16 and future
A4/model/service gates are not executed tests. Full compile/pytest/ruff/mypy are
implementation gates in §7, not rerun or claimed for this documentation-only pass.

- `git diff --check`: PASS.
- 202 local Markdown link targets across 19 changed Markdown files: all resolve;
  final newlines, paired code fences and new-document whitespace: PASS.
- All 55 register IDs/statuses preserved; exactly one consolidation disposition
  per ID; 43 DEFERRED, 3 PLANNED, 4 IMPLEMENTED, 3 REJECTED, 2 SUPERSEDED.
- F01–F16 design inventory complete; not a foundation runtime acceptance claim.
- All four historical architecture reviews byte-identical to entry HEAD;
  historical closure tables preserved (only current-disposition navigation
  clarified). No open register row still directs work to the past A3 closure.
- Current README/index/targets/roadmap next-step checks: no pending-consolidation
  claim. Historical/TBD proposal text is explicitly marked as such.
- Only Markdown changed; frozen source/scripts/tests/config/dependencies and
  DOCX reference unchanged. No commit/tag/push; design-only tag readiness is
  conditional on the later reviewed commit containing these changes.

Exact files changed: this new transition record plus these 18 existing files:

```text
README.md
docs/ARCHITECTURE.md
docs/TIAF_SYSTEM_ARCHITECTURE.md
docs/TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md
docs/TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md
docs/TIAF_DEPLOYMENT_ARCHITECTURE.md
docs/TIAF_CAPABILITY_MAP.md
docs/TIAF_IMPLEMENTATION_TARGETS.md
docs/TRADINGINTELLIGENCE_ROADMAP.md
docs/TIAF_DEFERRAL_REGISTER.md
docs/README_TBD_DESIGN_NOTES.md
docs/TBD_TI_SYSTEM_ARCHITECTURE_THESIS.md
docs/TBD_TI_SHELL_THESIS.md
docs/TBD_TI_CLI_WEB_UI_INTERACTION_ARCHITECTURE.md
docs/TBD_TI_MONITORING_ARCHITECTURE.md
docs/TBD_TI_FORECASTING_ENSEMBLE_LEARNING_ARCHITECTURE.md
docs/TBD_TI_SOURCE_PROVENANCE_CITATION_FABRIC.md
docs/TBD_TI_DEPLOYMENT_ARCHITECTURE.md
```

Exact next Codex prompt title:

**POST_A3_PRE_A4_FOUNDATION — Source Semantics, A4 Input Projection and Replay Integrity**

Implement only §7, using the authoritative source/A4 boundaries and unchanged
A3 artifacts. Stop at its acceptance report; do not begin the facade, A4 runtime,
new acquisition, model integration or Shell in that task.
