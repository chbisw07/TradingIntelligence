# Study — A3 Sub-Milestone Deferral Discovery Audit

## 1. Purpose and conclusion

**Audit date:** 2026-09-11, Asia/Kolkata  
**Conclusion:** `DEFERRAL_REGISTER_NEEDS_RECONCILIATION`

This documentation/governance audit asks whether accepted A3.1-A3.10 records
introduced concrete deferred capabilities that were never assigned stable
`DEF-*` IDs. It does not reopen accepted A3 semantics or implement any deferred
item. The required reconciliation has been applied narrowly: four new records
were added, two existing records were clarified, and historical A2 text was
explicitly labelled as a historical snapshot. No runtime file changed.

After that reconciliation, the A3 major closure decision remains valid. The
new records are later capabilities, not correctness prerequisites for the
accepted deterministic/no-LLM A3 boundary.

## 2. Documents reviewed

The audit reviewed all primary records named by the audit specification:

- A3.1-A3.7 milestone records and the A3.7 acceptance study;
- A3.6.1, A3.6.2 and Authoritative Confirmation records;
- A3.8-A3.10 designs/implementation records and acceptance studies;
- the A3 major closure review and complete deferral register; and
- supporting A3 architecture, detailed roadmap, capability map,
  implementation targets, canonical roadmap, README and CHANGELOG.

It also reviewed all current `TBD_TI_*` notes and their index to distinguish
architecture hypotheses from stable deferred capabilities.

## 3. Methodology

Each document was searched for explicit deferral language and then reviewed
semantically for bounded-only, unsupported, future, production, replay,
provider, model, persistence, scheduling, API, explanation and authority
constraints. Each distinct candidate was classified against the pre-audit
register as exactly one of `ALREADY_COVERED`, `PARTIALLY_COVERED`,
`NEW_DEFERRAL_CANDIDATE` or `NOT_A_DEFERRAL`.

The audit used a high bar for new records: the item had to be concrete,
material, intentionally deferred from accepted A3, and not safely preserved by
an existing record or an explicit future roadmap milestone. Repeated mentions
of the same capability across milestones were combined rather than counted as
separate candidates.

## 4. A3.1-A3.6 findings summary

Most early-A3 future language was planned sequencing or already governed:

- broad production fundamental/news/sector/macro acquisition maps to DEF-012;
- automatic benchmark/sector mapping maps to DEF-047;
- durable context caching maps to DEF-009;
- indicator/structure extensions map to their existing A2-era IDs; and
- forecasting/calibrated confidence remains explicitly owned by A7 rather than
  becoming an A3 deferral merely because consumer contracts exist.

One omission emerged across A3.1/A3.2 and later milestones. DEF-002 can remain
correctly IMPLEMENTED for the Agent/workflow layer, but it cannot also pretend
that a production model-backed reasoning adapter and operating policy were
delivered. That distinct capability is now DEF-052.

## 5. A3.7 findings

The richer derivative families are fully covered by DEF-039 through DEF-046.
The failed live Dhan acquisition does not create eight new records: primary
market-data fallback is DEF-008, the chain event-time limitation is DEF-014,
and historical/temporal/cross-expiry/model semantics retain their individual
existing IDs. CE/PE, strike, expiry, strategy and quantity selection remain
DEF-006.

Opportunity Quality/Risk did not introduce a separate position or forecast
deferral. A5/A6/A7 ownership is an intentional roadmap boundary, and A3.7's
typed states are not those later actions. No A3.7-specific new ID is needed.

## 6. A3.8 findings

Durable queue/restart/checkpoint recovery is covered by DEF-010 and distributed
storage/replay operation by DEF-050. Cross-run cache/single-flight and durable
graph state are DEF-009; provider health/telemetry is DEF-011; public
orchestration exposure is DEF-003; automatic mapping is DEF-047.

The inability to force-kill a synchronous worker is an operational subcase of
durable orchestration rather than a new domain capability. DEF-010 was clarified
to name checkpoint/resume and late-work/preemption policy. The deterministic
`ModelTier.NONE` boundary contributes to DEF-052; it does not justify a second
model record.

## 7. A3.9 findings

The in-process `tiaf.service.opportunity_intelligence` seam is not a complete
external capability facade; DEF-003 covers that future surface. Two separate
A3.9 omissions are material:

- one-underlying assembly intentionally excludes cross-candidate A3 comparison,
  batch/top-N behavior and ranking, now DEF-053; and
- internal cited reasons are not a user-facing bibliography, hyperlink,
  citation-compression or report projection, now DEF-054.

TI Shell and Web UI remain non-authoritative TBD designs, not additional DEF
records. A model-assisted assembler is part of the single production-model
governance problem in DEF-052. Monitoring/follow-up loops remain DEF-010/051.

## 8. A3.10 findings

The local corpus, distributed scale, scheduled outcomes and arbitrary
historical reconstruction are fully covered by DEF-050, DEF-051 and DEF-049.
Checkpoint/resume/recovery maps to DEF-010/050, and an external replay service
maps to DEF-003. Recorded-only future model output is a correctness invariant;
fresh nondeterministic comparison belongs with DEF-052/A7 evaluation, not a
promise of exact replay.

A3.10 did reveal one distinct dependency: it can represent provider/model money
as unknown or unpriced, but the repository has no versioned monetary pricing
catalog or billed-unit attribution policy. DEF-055 preserves that need without
weakening the rule that unknown is not zero. Closure automation is deliberately
human governance and is not a deferred product capability.

## 9. Candidate-to-existing-DEF mapping matrix

The matrix contains 44 distinct candidate items. Repeated wording across files
is combined into one row where the deferred meaning is the same.

| Source milestone | Candidate item | Evidence/reference | Classification | Existing DEF | Action | Rationale |
|---|---|---|---|---|---|---|
| A3.1/A3.2/A3.6.2/A3.8/A3.10 | Production model-backed reasoning adapter, operating policy and provenance | `ReasoningProvider` is a seam; accepted Planner/research/replay is no-LLM or recorded-only | NEW_DEFERRAL_CANDIDATE | DEF-002 covers the delivered Agent/workflow layer, not the remaining adapter | ADD_NEW_DEF | Concrete optional capability with privacy, budget, evaluation and replay dependencies; added as DEF-052 |
| A3.1 | Empirically calibrated confidence | Confidence contract permits it but A3 emits none | NOT_A_DEFERRAL | — | NONE | A7 explicitly owns calibration/evaluation; this is planned layer ownership |
| A3.1 | Full Agent replay | Early record called it future | NOT_A_DEFERRAL | — | NONE | Implemented by later A3.8-A3.10; no active deferral remains |
| A3.2 | Durable/cross-run reasoning-result reuse | A3.2 has only cache keys and no reasoning-result reuse | ALREADY_COVERED | DEF-009 | NONE | Persistent/distributed cache semantics cover the durable form |
| A3.3 | Exact futures/options Technical identity support | Technical v1 supports equity/index only | NOT_A_DEFERRAL | — | NONE | A3.7 later supplies derivative-context interpretation; expanding Technical is not a concrete accepted need |
| A3.3 | Additional indicator, event-state and MTF-level interpretation | Scalar projection subset and completed-bar limits | ALREADY_COVERED | DEF-020/022/034/035/038/048 | NONE | Existing feature/indicator records preserve each concrete missing semantic |
| A3.4 | Broad production fundamental provider | No production feed/live reconciliation in A3.4 | ALREADY_COVERED | DEF-012 | NONE | Broad licensed external acquisition is explicit |
| A3.5 | Broad production news/filing provider | Caller/test adapter only | ALREADY_COVERED | DEF-012 | NONE | Same production acquisition/governance need |
| A3.6 | Production sector/macro/peer evidence | Caller/test providers only | ALREADY_COVERED | DEF-012 | NONE | Existing record includes sector, macro and peer acquisition |
| A3.6 | Automatic benchmark/sector classification | Explicit caller/versioned mapping required | ALREADY_COVERED | DEF-047 | NONE | Exact mapping capability is already named |
| A3.6 | Distributed sector/macro context cache | Current cache is process-local | ALREADY_COVERED | DEF-009 | NONE | Persistent/distributed cache is explicit |
| A3.6.1 | Durable Sparse Evidence Graph/research memory | Sparse graph is in-memory/local | ALREADY_COVERED | DEF-009 | NONE | Resolution note already includes durable sparse Evidence Graph storage |
| A3.6.1 | Provider health, circuit breaking and operations | Bounded failure/fallback policy is not operational health | ALREADY_COVERED | DEF-011 | NONE | Health signals, thresholds and circuit-breaking are explicit |
| A3.6.1 | Broad provider/source coverage and licensing | Bounded Tapetide/Yahoo sources only | ALREADY_COVERED | DEF-012 | NONE | A3 closure already clarified bounded versus broad production coverage |
| A3.6.1 | Arbitrary exact historical PIT evidence | Limited/revision-sensitive source history | ALREADY_COVERED | DEF-049 | NONE | Existing record names universes, revisions and availability vintages |
| Authoritative gateway | Crawler/general official-source coverage and adjustment semantics | Configured URLs and bounded parsers only | ALREADY_COVERED | DEF-012/013 | NONE | Broad source acquisition and corporate-action adjustment remain separate existing records |
| A3.7 | IV rank/skew/surface, temporal OI, cross-expiry, expected move, max pain and dealer positioning | Explicit unavailable-family list | ALREADY_COVERED | DEF-039-046 | ADD_CROSS_REFERENCE | Every concrete derivative family retains its stable existing ID |
| A3.7 | Live derivative acquisition fallback beyond Dhan | Dhan attempt failed before active-expiry evidence | ALREADY_COVERED | DEF-008/014 | ADD_CROSS_REFERENCE | Primary market-data fallback and timestamp limits cover acquisition; failure alone is not a new capability |
| A3.7 | CE/PE, strike, expiry, strategy and quantity selection | Explicitly prohibited output | ALREADY_COVERED | DEF-006 | NONE | Option-expression selection is already planned for A6 |
| A3.7 | Position HOLD/BOOK/EXIT/PROTECT | Explicitly prohibited output | NOT_A_DEFERRAL | — | NONE | A5 owns position intelligence; this is an authority boundary, not unfinished A3.7 |
| A3.7 | Calibrated success probability/forecast | Explicitly prohibited output | NOT_A_DEFERRAL | — | NONE | A7 owns forecasting/calibration and A3.7 must not fabricate it |
| A3.8 | Durable queue, restart and LangGraph checkpoint recovery | Bounded in-process workflow; no checkpointer | ALREADY_COVERED | DEF-010/050 | ADD_CROSS_REFERENCE | Retry/restart and distributed operational scale already cover it |
| A3.8 | Cross-run/session single-flight and cache reuse | Reuse is process/request-local | ALREADY_COVERED | DEF-009 | NONE | Durable/distributed cache semantics are explicit |
| A3.8 | Production provider observability/circuit breaking | Typed failures and fallback, no health service | ALREADY_COVERED | DEF-011 | NONE | Existing provider-health record is sufficient |
| A3.8 | Hard cancellation/preemption of synchronous work | Timed-out worker may finish; late result is rejected | PARTIALLY_COVERED | DEF-010 | REWORD_EXISTING_DEF | Operationally part of durable work/restart semantics; DEF-010 now explicitly names late-work/preemption policy |
| A3.8 | Public orchestration API/facade | Public Python workflow seam, no external API | ALREADY_COVERED | DEF-003 | NONE | Governed service/capability surface is the existing future item |
| A3.8 | Automatic mapping/applicability | Caller supplies canonical identities/mappings | ALREADY_COVERED | DEF-047 | NONE | Existing mapping deferral is exact |
| A3.8/A3.10 | Versioned provider/model monetary pricing and billed attribution | Unknown provider cost remains held/UNPRICED | NEW_DEFERRAL_CANDIDATE | — | ADD_NEW_DEF | Cost discipline needs a separate effective-time pricing source; added as DEF-055 |
| A3.9 | Governed public Opportunity Intelligence facade | In-process service modules; no server/external contract | ALREADY_COVERED | DEF-003 | ADD_CROSS_REFERENCE | Facade consolidation, versioning and external exposure belong to the public-surface record |
| A3.9 | Batch/cross-candidate opportunity comparison and ranking | One captured underlying; no top-N, batch scheduler or A3 rank | NEW_DEFERRAL_CANDIDATE | — | ADD_NEW_DEF | Semantically distinct from A2 ranking and operational scheduling; added as DEF-053 |
| A3.9 | User-facing explanation/source-citation report rendering | Internal reason/citation IDs only; no bibliography/hyperlink resolver/report fabric | NEW_DEFERRAL_CANDIDATE | — | ADD_NEW_DEF | Material explainability capability distinct from acquisition and transport; added as DEF-054 |
| A3.9 | TI Shell/Web UI | Explicitly absent from the application seam | NOT_A_DEFERRAL | — | KEEP_AS_TBD | Interaction architecture remains exploratory and does not define accepted A3 work |
| A3.9 | External follow-up loop and opportunity-state monitoring | Assembly never reacquires/reruns; one captured state | ALREADY_COVERED | DEF-010/051 | NONE | Runtime queues/monitoring triggers and scheduled later evidence/outcomes cover it |
| A3.10 | Persistent/distributed replay corpus | Filesystem append-only corpus only | ALREADY_COVERED | DEF-050/009 | NONE | Distributed replay farm and persistent storage are explicit |
| A3.10 | Scheduled subsequent-outcome acquisition | No wait/schedule/backfill | ALREADY_COVERED | DEF-051 | NONE | Exact capability already exists |
| A3.10 | Arbitrary historical reconstruction | Captured replay only | ALREADY_COVERED | DEF-049 | NONE | Exact PIT limitation already exists |
| A3.10 | Operational recovery/checkpoint resume | Domain replay is not disaster recovery | ALREADY_COVERED | DEF-010/050 | ADD_CROSS_REFERENCE | Long-running restart and distributed operational recovery cover it together |
| A3.10 | External replay service/API | Local package/store APIs only | ALREADY_COVERED | DEF-003 | NONE | Public service surface is the correct owner |
| A3.10 | Exact fresh replay of nondeterministic model output | Future model output is deliberately recorded-only | NOT_A_DEFERRAL | — | NONE | Exact fresh inference is not reproducible; later A7 may compare a new run under DEF-052 provenance |
| A3.10 | Automatic closure/freeze decision | Closure-readiness is evidence, human decides | NOT_A_DEFERRAL | — | NONE | Human governance is an intentional control, not a missing runtime capability |
| Monitoring TBD | Durable cadence, triggers, health, queues and telemetry | Non-authoritative monitoring thesis | ALREADY_COVERED | DEF-009/010/011/051 | KEEP_AS_TBD | Concrete operational pieces have IDs; the combined architecture remains TBD |
| Forecasting TBD | Forecast/ensemble/learning implementation | Non-authoritative forecasting thesis and A7 roadmap | NOT_A_DEFERRAL | — | KEEP_AS_TBD | Explicit A7 planned work should not be duplicated as an A3 deferral |
| TI Shell TBD | Stateful human/engineering mediator | Non-authoritative Shell thesis | NOT_A_DEFERRAL | — | KEEP_AS_TBD | Concrete implementation has not been accepted or deferred from A3 |
| System/CLI-Web TBD | External authentication, authorization, entitlement and capability discovery | Future public consumers must not access Core internals | PARTIALLY_COVERED | DEF-003 | REWORD_EXISTING_DEF | Material operational scope of the public surface; DEF-003 now states it explicitly |

## 10. New DEF records

Four records were justified and added without renumbering existing entries:

| ID | Title | Deferred from | Category | Priority / revisit |
|---|---|---|---|---|
| DEF-052 | Production model-backed specialist/reasoning integration | A3.2; reaffirmed A3.8-A3.10 | CAPABILITY_DEFERRAL | MEDIUM / A7 CLOSURE |
| DEF-053 | Cross-candidate A3 opportunity analysis and ranking | A3.9 | CAPABILITY_DEFERRAL | MEDIUM / FUTURE |
| DEF-054 | User-facing explanation, source-citation and report rendering fabric | A3.9; reaffirmed A3 closure | CAPABILITY_DEFERRAL | HIGH / POST-A3 ARCH |
| DEF-055 | Provider/model monetary pricing catalog and cost attribution | A3.10 | DEPENDENCY_DEFERRAL | MEDIUM / A10 CLOSURE |

All are `DEFERRED`. None authorizes implementation or changes current A3
behavior.

## 11. Existing DEF rewording

- DEF-003 now says governed public capability/service/API surface and explicitly
  includes facade versioning, discovery, authentication/authorization and
  entitlement. This avoids treating diagnostic scripts as an API.
- DEF-010 now explicitly includes durable checkpoint/resume and late-work/
  preemption policy for the bounded A3.8 worker limitation.
- DEF-002 now cross-references DEF-052 so its valid IMPLEMENTED status cannot be
  misread as a claim that production model reasoning exists.

DEF-008 and DEF-012 retain the scope clarification already made by the A3
closure review; this audit found no further split necessary.

## 12. TBD versus DEF decisions

The System Architecture, TI Shell, Monitoring, Forecasting/Learning, CLI/Web and
Source/Provenance/Citation documents remain `TBD_*` and non-authoritative. The
audit extracted only concrete deferred capabilities already anchored in A3:
DEF-052 model integration and DEF-054 report/citation projection. It did not
convert the Shell, Web UI, product profiles, forecasting architecture or full
monitoring thesis into DEF records.

## 13. Count reconciliation

| Measure | Count |
|---|---:|
| Candidate items inspected | 44 |
| `ALREADY_COVERED` | 28 |
| `PARTIALLY_COVERED` | 2 |
| `NEW_DEFERRAL_CANDIDATE` | 4 |
| `NOT_A_DEFERRAL` | 10 |

The register previously contained 51 records. Adding four produces 55 total:
43 DEFERRED, 3 PLANNED, 4 IMPLEMENTED, 3 REJECTED and 2 SUPERSEDED. The A3
closure's original 43-active-record entry snapshot remains historical truth;
the closure report now records this post-closure reconciliation separately.

## 14. Quality checks

| Check | Result |
|---|---|
| Register ID/status/count consistency | 55 unique sequential IDs; status totals reconcile |
| Candidate-matrix consistency | 44 rows; 28/2/4/10 classification totals reconcile |
| Repository-relative Markdown links | 159 checked; none missing |
| `git diff --check` | Passed |
| Runtime/schema regression | Not rerun: this audit changes Markdown governance only; the immediately preceding A3 closure suite remains 1,921 passed |
| Live/provider/model activity | None |

## 15. Final conclusion

`DEFERRAL_REGISTER_NEEDS_RECONCILIATION`

The concern was valid: four material A3-specific deferrals were missing and two
older records needed A3-era scope clarification. The reconciliation is now
complete in documentation. It reveals no accepted-A3 correctness defect and no
reason to withdraw `READY_TO_FREEZE_A3`.

The next action is review of this governance-only diff. If accepted, include it
with the existing closure documentation before creating the recommended
`tiaf-a3-baseline` tag. Then perform the already-required post-A3 architecture
consolidation; do not start A4 automatically.
