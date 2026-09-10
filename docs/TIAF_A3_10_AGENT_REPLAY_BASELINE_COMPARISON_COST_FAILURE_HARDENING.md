# TIAF A3.10 — Agent Replay, Baseline Comparison, Cost & Failure Hardening

## Status and authority

Architecture approved at `tiaf-a3.10-arch`; implementation and offline acceptance
completed on 2026-09-10 over frozen `tiaf-a3.9`. A1, A2 and A3.1–A3.9 remain
immutable inputs, not redesign targets. This document is both the authoritative
design and implementation record for the final A3 sub-milestone before the
separate A3 major-closure review.

The implementation adds only replay/evaluation infrastructure under
`tiaf.a3_hardening`, deterministic synthetic fixtures, tests, and a bounded
offline helper. It adds no live call, provider, specialist, model, dependency,
or intelligence-policy change. It does not perform the A3 deferral burn-down,
closure, commit, tag, or push. Post-A3 system/Shell/source-fabric/monitoring/
forecasting documents remain deferred and were not reopened.

## 1. Purpose and ownership

A3.10 proves that accepted A3 intelligence is reproducible, comparable with the
frozen A2 benchmark, cost-accounted, failure-resilient and closure-ready. It
evaluates records; it does not produce new market intelligence.

A3.10 owns:

- self-contained capture manifests and integrity validation;
- recorded replay, bounded deterministic verification and explicit comparison replay;
- observational A2/A3 comparison without rewriting either side;
- original-run and replay-execution usage/cost views;
- normalized failure lineage and degradation summaries;
- deterministic fault injection and an append-only A3 acceptance corpus;
- evidence for the later A3 closure decision.

It does not retune A2, any specialist or A3.9; choose a winner; arbitrate;
produce BUY/SELL or position actions; select an option contract; estimate a win
probability; train weights; implement UI/Shell, TradeMonitor, scanner or broker
behavior; or claim predictive/profit superiority. A3.9 states remain unchanged.
A4 owns arbitration/recommendations, A5 positions, A6 expression, A7 outcomes,
forecasting and empirical value evaluation, A8 integration, A9 scanning and A10
production operations.

## 2. Existing seams and compatibility findings

| Existing seam | A3.10 use |
|---|---|
| A2.10 `EvidenceSnapshot`, `BaselineRunRecord`, `CapturedBaselineCase` | Reuse complete frozen A2 evidence/assessment when captured; do not alter its hash or append-only store. |
| `OrchestrationRunRecord` / A3.8 `capture_json` | Authoritative request, plans, registry snapshot, inventories, attempts, projections, artifacts, reservations, outcomes, usage, stops and semantic identity. |
| A3.8 `replay_recorded` | Recorded reconstruction with artifact validation and no execution. |
| A3.8 `verify_deterministic` | Current deterministic specialist/planner verification over captured inputs. Invoke only in explicitly selected deterministic-verification mode with provider/model paths disabled. |
| A3.9 `IntelligenceRunRecord` / capture | Immutable policy, predicates, all rule matches, structured result, imported A3.8 audit and A3.9 semantic identity. Its request already contains the exact A3.8 capture. |
| A3.9 `replay_intelligence` | Recorded A3.9 validation; it validates the embedded A3.8 capture but does not rerun specialists. |
| A3.9 `verify_intelligence` | Pure A3.9 assembly verification only. |
| `AgentUsage`, `Reservation`, MI `ProviderCallAudit` | Child truths for calls, tokens, configured cost units, elapsed time, attempts and held usage. They are not proof of known monetary cost. |

Do not modify accepted child fingerprint algorithms to make package comparison
convenient. A3.10 adds parent manifests and projections around existing records.

## 3. Complete replay package

### 3.1 Manifest plus content-addressed blobs

Use composition, not a nested god object. A package is an immutable manifest
whose typed references resolve to content-addressed canonical JSON blobs:

```text
corpus/
  blobs/sha256/<digest>.json
  packages/<package-id>/manifest.json
  evaluation_records.jsonl
  closure_records.jsonl
```

The implementation may offer a single-file portable envelope containing the
same manifest and blobs. Directory and envelope representations must validate
to the same package semantic fingerprint. Stores refuse replacement of an
existing digest or record ID; equal content is idempotent. No default corpus
may imply that the A3.9 synthetic fixture manifest is a live corpus.

### 3.2 Required content

`A3ReplayPackageManifest` schema `1.0` contains:

- `package_id`, subject, underlying instrument, horizon, as-of and purpose;
- `a2_capture`, `a38_capture` and `a39_capture` typed blob references;
- dependency/planner/registry/specialist/synthesis schema-policy-runtime versions;
- ordered A3.8 plan and admitted-evidence identities;
- active and superseded opinion IDs and specialist input/output fingerprints;
- MI, provider-attempt, confirmation, deep-research and graph artifact references;
- projection digests, reservations, outcomes, skips/abstentions/failures and stops;
- A2 evidence fingerprint/assessment ID and A3.8/A3.9 semantic fingerprints;
- exact checksums for each capture and for the whole package;
- capture completeness and replayability status;
- creation time as an operational, timezone-aware Asia/Kolkata timestamp.

`BlobReference` carries kind, schema ID/version, SHA-256, byte length and relative
content address. It carries no arbitrary external URL. The checksum is over the
exact stored bytes. The manifest semantic fingerprint is over canonical typed
identity/references and excludes only its self-hash and explicitly operational
package-write time. The complete package checksum covers canonical manifest plus
the ordered `(blob kind, digest, exact bytes)` sequence.

The A3.9 capture embeds the exact A3.8 capture; the package validator requires
that embedded bytes/checksum match the separately indexed A3.8 blob. The package
does not store a second divergent source of truth.

### 3.3 A2 capture modes

`A2CaptureDescriptor` has exactly two honest modes:

- `FULL_BASELINE_CASE`: a validated A2.10 `CapturedBaselineCase`, including the
  evidence snapshot and full assessment;
- `ORIGINAL_A38_PROJECTION`: the immutable original A2 evidence pack and A3.9
  `BaselineView`, including direction/class/score and eligibility only if captured.

Both preserve assessment ID and evidence fingerprint. The projection mode is
sufficient to replay accepted A3.8/A3.9 and compare captured fields, but it does
not pretend to reconstruct a full A2.10 evidence snapshot or missing eligibility.
Closure coverage reports the mode explicitly. A required corpus case that claims
full A2 deterministic verification must use `FULL_BASELINE_CASE`.

### 3.4 Completeness and integrity

`CaptureCompleteness` records required, present and missing artifact kinds and a
status of `COMPLETE`, `PARTIAL_RECORDED_ONLY` or `NON_REPLAYABLE`. Missing content
never triggers acquisition. Integrity errors include missing blobs, hash/checksum
mismatch, schema/policy mismatch, broken reference, identity/as-of mismatch,
future evidence, mutated A2 copies, incomplete model provenance or unsupported
nondeterministic verification. These are capture failures, not market gaps.

## 4. Replay taxonomy and APIs

### A. Recorded replay

`replay_a3_package(package)` validates every blob and cross-reference, calls only
the existing recorded A2/A3.8/A3.9 loaders, reconstructs accepted outcomes/state
transitions and returns equal semantic results. It executes no provider, model,
specialist, gateway, network or LangGraph checkpoint recovery.

### B. Deterministic verification replay

`verify_a3_package(package, verification_policy)` explicitly selects components:

- A2 only when a full captured A2 snapshot and identical policy are present;
- A3.8 planner and specialists only where the captured capability declares the
  accepted deterministic mode and all original inputs are present;
- projections from captured deterministic opinions;
- A3.9 pure assembly under the identical captured synthesis policy.

All external acquisition and model gateways are replaced by deny-by-default
guards. A verification plan labels every node `REEXECUTED_DETERMINISTIC`,
`RECORDED_ONLY`, `NOT_APPLICABLE` or `UNVERIFIABLE`. A future model-backed output
is `RECORDED_ONLY`; it is never silently re-inferred. Verification consumption
is new execution usage and is not added to historical usage.

### C. Comparison replay

`compare_a3_policy(package, candidate_versions)` intentionally runs a compatible
new pure policy/runtime over old captured evidence and emits a new
`A3PolicyComparisonRecord`. It retains old/new outputs, versions, differences and
separate fingerprint. It neither overwrites history nor reports exact replay.
Model-backed fresh reasoning requires a later explicitly authorized new run and
is outside offline comparison replay.

### D. Operational recovery

LangGraph checkpoint recovery, resuming external calls and production disaster
recovery are out of scope. They are not domain replay and cannot be reported as
A3.10 replay success.

Proposed public functions:

```text
capture_a3_package(a38_capture, a39_capture, optional_a2_capture) -> package
replay_a3_package(package) -> A3ReplayResult
verify_a3_package(package, verification_policy) -> A3VerificationResult
compare_a2_a3(package, comparison_policy) -> A2A3ComparisonRecord
compare_a3_policy(package, candidate_versions) -> A3PolicyComparisonRecord
summarize_a3_cost(package, replay_usage=None) -> A3CostSummary
summarize_a3_failures(package) -> A3FailureSummary
evaluate_a3_hardening(package) -> A3HardeningResult
```

No function accepts a provider/model/executor handle. Capture creation accepts
completed records, never instructions to fetch missing material.

## 5. Fingerprint hierarchy

| Identity | Semantic content | Operational/exact content | Legitimate semantic change |
|---|---|---|---|
| A2 evidence fingerprint | Frozen normalized decision-time evidence and policy identity | Snapshot write time handled by accepted A2 rules | Evidence/value/time/quality/policy change |
| A2 assessment ID | Accepted A2 output identity | Original run record time separate | Assessment/policy/evidence change |
| Specialist input digest | Exact admitted pack under capability/policy | Invocation clock excluded by child rules | Admitted evidence/dependency/policy change |
| Specialist output fingerprint | Typed opinion/claims/citations/status/usage per accepted record | Service timing per accepted semantics | Opinion/status/citation/model/config change |
| Projection digest | Typed projected fields and source lineage | None beyond child definition | Field/value/source change |
| A3.8 semantic fingerprint | Request, plans, decisions, inputs, attempts, artifacts, result; accepted operational exclusions | Exact A3.8 capture checksum includes stored record | Plan/admission/deadline/evidence/outcome/policy change |
| A3.9 semantic fingerprint | Structured product, policy, predicates/rules and source semantic identity | Assembly time/elapsed and exact capture checksum separate | State/facet/reason/quality/source/policy change |
| A3.10 comparison fingerprint | Both immutable sides, axes, additions, taxonomy and comparison policy | Evaluation write time excluded | Either side/policy/mapping/result change |
| Package semantic fingerprint | Typed manifest identities and ordered blob digests | Write time excluded | Membership/schema/version/reference change |
| Complete package checksum | Canonical manifest and exact blob bytes | Includes exact serialization bytes | Any byte change |

Exact checksum equality is stricter than semantic equality. Operationally different
serial/LangGraph captures may have different exact checksums while accepted child
semantic fingerprints and A3.9/A3.10 results match. As-of, observed/available/fact
time, freshness, deadlines, admission order and meaning-bearing decision order are
semantic. Adapter name, transport latency and serialization formatting are not,
unless an accepted child algorithm already says otherwise.

## 6. A2/A3 comparison model

`A2A3ComparisonRecord` schema `1.0` is observational and contains:

- comparison/package identity, subject, horizon and as-of;
- an immutable `A2Side`: assessment ID/fingerprint, direction, class, score,
  captured eligibility/basis, reasons/warnings and content mode;
- an immutable `A3Side`: A3.9 fingerprint, state, price-direction and qualified
  bias, Quality, Risk, maturity, extension/room, completeness and contradictions;
- typed axis results, zero or more disagreement classes and information additions;
- A2-only cautions, A3-only additions, common evidence roots and coverage deltas;
- cited source/reason IDs and the explicit comparison policy ID/version;
- semantic fingerprint and operational comparison time.

Neither side is reduced to a common scalar. No “better”, “winner”, “upgrade”,
“alpha”, “confidence boost” or recommendation field exists.

### 6.1 Direction axis

Map only the same underlying/horizon price proposition:

| A2 | A3 price direction | Axis |
|---|---|---|
| POSITIVE / NEGATIVE | same sign | ALIGNED |
| POSITIVE / NEGATIVE | opposite sign | OPPOSED |
| POSITIVE / NEGATIVE | ABSTAIN / INSUFFICIENT_EVIDENCE | A3_INSUFFICIENT |
| NEUTRAL | POSITIVE / NEGATIVE | A3_DIRECTIONAL_A2_NEUTRAL |
| CONFLICTED | any directional result | A2_CONFLICTED |
| incomparable identity/horizon | any | NON_COMPARABLE |

Do not use contextual specialist stances as direction votes. A3 qualified MIXED
is reported separately from its Technical price-direction facet.

### 6.2 Class/state axis

`OpportunityAxis` preserves both enum values and emits a mapping category:

- `ALIGNED_OPPORTUNITY`: A2 TOP_MOVER/EARLY_OPPORTUNITY and A3 OPPORTUNITY;
- `ALIGNED_TIMING_CAUTION`: A2 MATURE_AVOID_CHASE and A3 WAIT;
- `BASELINE_NO_TRADE_WATCH`: A2 NO_TRADE and A3 WATCH;
- `BASELINE_NO_TRADE_PRESERVED`: A2 NO_TRADE and A3 NO_TRADE;
- `A3_RESTRICTION_ADDED`: A2 opportunity-like and A3 WAIT/AVOID/CONFLICTED;
- `A3_EVIDENCE_INSUFFICIENT`: any comparable A2 class and A3 insufficiency;
- `SEMANTIC_DIVERGENCE`: other comparable pair;
- `NON_COMPARABLE`: identity/horizon/content unavailable.

These names describe relationships, not correctness or permission. In particular,
A2 NO_TRADE/A3 WATCH remains `BASELINE_NO_TRADE_PRESERVED` as a disagreement
class plus `BASELINE_NO_TRADE_WATCH` on the axis; A2 eligibility is unchanged.

### 6.3 Disagreement taxonomy

`DisagreementClass` is a tuple because facts may co-exist:

- `ALIGNED`, `A3_MORE_CONSERVATIVE`, `A3_MORE_PERMISSIVE`;
- `DIRECTION_CONFLICT`, `TIMING_CONFLICT`;
- `EVIDENCE_GAP_DIFFERENCE`, `RISK_CONTEXT_DIFFERENCE`;
- `BASELINE_NO_TRADE_PRESERVED`, `NON_COMPARABLE`;
- `INSUFFICIENT_EVIDENCE`.

Ordering is policy-defined and stable. “More conservative/permissive” describes
restriction relation only; it is not value judgment. Agreement is not correctness;
disagreement is not an error.

### 6.4 Additional intelligence

`InformationAddition` uses a closed category, typed source locators and
`PRESENT`, `ABSENT` or `UNKNOWN` status:

- company quality; event/catalyst context; sector/macro context;
- derivatives context; extension/timing restriction;
- evidence insufficiency; source contradiction/confirmation;
- explicit missing evidence; risk restriction; preserved specialist disagreement.

It states that A3 contains attributable context absent from the A2 projection.
It does not claim usefulness, causal value, predictive advantage or profit. A7
may later join immutable decision IDs to point-in-time outcomes and evaluate that.

## 7. Cost accounting design

### 7.1 Knowledge before arithmetic

Existing `AgentUsage.cost_units` is a nonnegative configured unit. `0.0` cannot
prove a provider's monetary price is known zero. Add a wrapper without changing
the child:

```text
CostKnowledge = KNOWN_ZERO | KNOWN_NONZERO | UNKNOWN | UNPRICED | NOT_APPLICABLE
CostMeasure = {knowledge, amount?, currency?, configured_units?, source_refs}
```

`amount` is permitted only for known states, is zero exactly for KNOWN_ZERO and
positive for KNOWN_NONZERO. `currency` is required for monetary amount. UNPRICED
means an attempt occurred but no price contract was supplied; UNKNOWN means the
record cannot establish whether/what cost occurred; NOT_APPLICABLE means no such
cost domain. Neither serializes as numeric zero.

### 7.2 Attribution and rollup

`UsageAttribution` identifies phase, capability, specialist, provider/model,
attempt/accounting/reservation IDs, parent accounting ID, disposition
`FRESH|FALLBACK|REUSED|REPLAY`, calls/tokens/configured units, service time,
monetary measure and `included_in_original_total`.

`A3CostSummary` separates:

- `original_captured_usage`: historical leaf-attributed consumption;
- `original_held_usage`: unsettled allowances, never actual spend;
- `replay_execution_usage`: current recorded/verification/comparison work;
- `provider_monetary_cost`, `model_monetary_cost`, `unknown_or_unpriced`;
- counts/provider mix, fallback attempts, reuse counts/eligible count and ratio;
- per-capability/specialist summaries and service-time samples.

Roll up from settled leaf reservations/provider-call audits exactly once. Parent
controller rollups are reconciliation checks, not additional debit rows. Every
child total must equal its accepted source record. Failed, rate-limited, malformed
and timed-out attempts retain any recorded usage. Fallback is a new attempt;
primary and fallback are each charged from their own audit. Reused evidence has
zero **new call count**, but its historical acquisition cost remains on its source
package and is not reassigned to the reuse event.

No-LLM means model calls/input tokens/output tokens/model monetary cost are
KNOWN_ZERO only when the captured model gateway/audits prove no model attempt.
It says nothing about provider monetary cost. Recorded replay has no historical
re-debit; its local execution time is reported separately. Mean/median latency is
reported only for homogeneous sample labels with count; no percentile from tiny
samples. Future deterministic/balanced/deep profile labels may group records but
do not implement product tiers.

## 8. Failure and degradation design

### 8.1 Preserve child truth

`A3FailureEvent` never replaces the original typed error. It contains normalized
category/code, phase, source artifact/attempt/node/provider/specialist IDs,
original type/code/sanitized message reference, retry/fallback relation, terminal
flag, captured usage reference and affected capabilities/predicates. Aggregation
is deterministic over source IDs; duplicate lineage is one event with multiple
observations, not erased detail.

Normalized codes:

- evidence/provider: `RATE_LIMITED`, `UNAVAILABLE`, `TIMEOUT`, `MALFORMED`,
  `AMBIGUOUS`, `OUT_OF_COVERAGE`, `PERMISSION_DENIED`, `BUDGET_BLOCKED`;
- specialist: `EXCEPTION`, `INVALID_OUTPUT`, `ABSTAIN`,
  `INSUFFICIENT_EVIDENCE`, `UNSUPPORTED`;
- orchestration: `INVALID_REQUEST`, `UNSAFE_DAG`, `DEADLINE_EXCEEDED`,
  `BUDGET_EXHAUSTED`, `TERMINAL_FAILURE`, `PARTIAL_COMPLETION`;
- replay/capture: `MISSING_ARTIFACT`, `CHECKSUM_MISMATCH`, `SCHEMA_MISMATCH`,
  `POLICY_VERSION_MISMATCH`, `CORRUPT_REFERENCE`,
  `NON_REPLAYABLE_MODEL_OUTPUT`.

Unknown child codes map to `UNCLASSIFIED` while retaining the original; they do
not become UNAVAILABLE. Capture-integrity failures abort package replay and are
reported separately from market/specialist degradation.

### 8.2 Degradation projection

`A3FailureSummary` groups events without severity arithmetic. `DegradationSummary`
contains surviving/failed/skipped capabilities, required/optional impact, captured
A3.8 status/stops, unchanged A3.9 state/completeness/prerequisites and a status:
`NONE`, `DEGRADED_COMPLETE`, `PARTIAL`, `INSUFFICIENT_EVIDENCE` or
`NON_REPLAYABLE`.

A3.10 does not decide the A3.9 state. It verifies accepted behavior:

- unavailable Fundamental leaves other outputs but may reduce/qualify coverage;
- rate-limited primary plus fallback preserves both attempts and lineage;
- unavailable F&O derivatives restricts captured Risk/Quality as A3.8/A3.9 did;
- optional Macro failure need not block required coverage;
- missing/failed Risk cannot look like unrestricted complete OPPORTUNITY;
- core unusable remains A3.9 INSUFFICIENT_EVIDENCE;
- timeouts/budget denials prevent post-denial work and preserve partial results;
- confirmation NOT_FOUND is not falsehood; unresolved contradiction stays visible.

Any fixture that produces a different state exposes a defect in an accepted
boundary and requires a narrow correction process; A3.10 must not introduce a
shadow synthesis rule.

## 9. Deterministic fault-injection matrix

| Case | Injection | Required evidence |
|---|---|---|
| Primary throttled/fallback succeeds | RATE_LIMITED primary, deterministic secondary success | Both attempts/failure and one accepted evidence lineage; each usage once |
| All providers unavailable | Typed unavailable results | No fabricated facts; gaps/partial state |
| Malformed payload | Schema-invalid native fixture | MALFORMED retained; no partial invented normalization |
| Ambiguous financial semantics | PROVIDER_DEFINED/AMBIGUOUS canonical mapping | Unknown semantic restriction remains visible |
| Confirmation NOT_FOUND | Deterministic official-source response | NOT_FOUND preserved, never converted to false |
| Confirmation contradiction | Conflicting field fixture | Both evidence values and unresolved field lineage |
| Specialist exception/invalid output | Runtime double | Failure isolated; original error and usage retained |
| ABSTAIN/insufficient | Valid typed opinion states | Not converted to NEUTRAL/support |
| Missing required Risk | Denied/failed Risk node | Complete unrestricted opportunity cannot be reported |
| Timeout/late completion | Controlled elapsed clock/barrier | Deadline status, no late admission, usage truth |
| Budget exhaustion | Reservation denial | No post-denial call, partial outputs and held/settled ledger reconcile |
| Unknown provider cost | Attempt with no price source | UNPRICED/UNKNOWN, never numeric zero |
| Missing artifact/tamper | Remove blob/change byte/reference | Typed capture failure before replay |
| Schema/policy mismatch | Unsupported version | Explicit mismatch; comparison mode only for compatible new policy |
| Completion-order variation | Controlled serial/parallel schedules | Equal semantics for equivalent admissions |
| Duplicate provider lineage | Two wrappers over one root | One canonical lineage, independence UNKNOWN |
| Stale evidence | Fact/reference freshness fixture | No fresh completeness via pack-summary masking |
| Unknown F&O | Unresolved applicability | UNKNOWN denominator/state restriction retained |
| Verified non-F&O | Explicit eligibility false | Derivatives NOT_APPLICABLE, no false missing requirement |

No test manufactures a live outage. Faults are injected before capture or by
validated test doubles, then replayed offline.

## 10. Provider/model-disabled and framework-independent replay

Tests install guards that fail on network/socket, provider connector, evidence
gateway, reasoning/model gateway, `AgentRuntime.run`, specialist `.analyze`, A3.8
coordinator invocation and LangGraph/LangSmith/MCP/OpenAI transport import during
recorded replay/comparison. The package contains no secret and replay never reads
`.env`. Missing required artifacts fail with typed capture error; no fallback to
live access exists. Recorded replay has no LangGraph checkpoint dependency.

Deterministic A3.8 verification may import its accepted runtime deliberately, but
its verification policy still denies external acquisition/model calls and uses
only complete captured invocation packs. This mode is tested separately from the
stricter recorded-replay process.

## 11. Serial/LangGraph parity and determinism boundaries

Pair fixtures with equal A3.8 semantic fingerprints but different adapter,
completion timing/order and exact capture checksums. Require equal A3.9 output,
A2/A3 comparison, cost semantics (excluding timing summaries) and A3.10 semantic
fingerprints. A real difference in evidence, availability/freshness, admission,
deadline, decision/plan semantics, failure, usage, schema or policy must change
the relevant identity. Shuffling JSON object keys does not; shuffling a
meaning-bearing ordered decision sequence does.

Deterministic today: A2 baseline, current accepted no-LLM specialists, A3.8 plan
policy, projections, A3.9 synthesis, record validators and A3.10 pure projections.
Potentially nondeterministic later: model-backed reasoning, generative synthesis
and stochastic forecasting. Such output must capture model/config/prompt/tool
identity, structured output and usage, replay recorded-only, and be explicitly
marked non-reexecutable unless a versioned deterministic verifier exists.

## 12. A3 cumulative corpus

`A3CorpusManifest` version `1.0` is an append-only list of package references and
case labels. Labels are descriptive test strata, never tuning targets:

- Technical; Fundamental; News/Event; Relative/Sector/Macro;
- MI/fallback/confirmation/deep research/graph;
- Derivatives, Quality/Risk, orchestration and A3.9 synthesis;
- positive/negative/mixed, NO_TRADE, conflict, insufficiency;
- failure/degradation, reuse, cost knowledge and replay/parity.

The minimum implementation corpus includes the 14 public cases below and reuses
accepted A3.8/A3.9/A2.10 captures where provenance permits. Synthetic cases carry
`SYNTHETIC` origin and fixture-builder version; live captures carry acquisition
study/reference and exact claims. Never relabel synthetic data as live. Symbols
provide diversity, not policy branches, and no rule is tuned to a symbol.

The corpus is intentionally local/filesystem-scale, following A2.10 conventions.
Database/distributed farm, arbitrary historical reconstruction and scheduled
outcomes remain DEF-050/049/051. Future A4/A7 may consume immutable package and
comparison IDs without modifying them.

## 13. Public acceptance matrix

| ID | Scenario | Expected proof |
|---|---|---|
| A | Clean aligned | Full package/replay, aligned comparison, exact cost reconciliation |
| B | A2 NO_TRADE / A3 WATCH | Both values/eligibility basis retained; observational divergence |
| C | Constructive A2 / A3 WAIT | Timing/risk addition cited, no A2 rewrite |
| D | Neutral A2 / A3 CONFLICTED | Conflict/reasons visible, no winner |
| E | Sparse evidence | INSUFFICIENT_EVIDENCE, no fabricated support |
| F | Primary rate-limit/fallback | Failure + fallback + lineage, leaf usage once |
| G | Optional specialist failure | Surviving results and explicit degradation |
| H | Required Risk failure | Completeness restriction; no unrestricted OPPORTUNITY |
| I | Budget exhaustion | No post-denial work; settled/held accounting exact |
| J | Replay tamper | Exact checksum/reference failure before reconstruction |
| K | Policy mismatch | Recorded replay rejected; compatible comparison makes new record |
| L | Serial/LangGraph equivalents | Equal semantic outputs, possibly unequal exact checksums |
| M | Unknown provider cost | UNKNOWN/UNPRICED, not zero |
| N | No-LLM | Exactly zero model calls/tokens and proven monetary knowledge state |

The helper prints package/case IDs, replay mode/status, A2/A3 axes, disagreement
classes, additions, failure/degradation summaries, original/replay usage, cost
knowledge, semantic/exact identities and gaps. It is diagnostic, local and
offline—not UI, ranking, live acquisition or a profitability report.

## 14. Minimal public contracts

Implement as small immutable `ContractModel` compositions, with semantic
collections as tuples and Asia/Kolkata-aware timestamps:

- capture: `BlobReference`, `A2CaptureDescriptor`, `CaptureCompleteness`,
  `A3ReplayPackageManifest`, optional `PortableA3ReplayPackage`;
- replay: `ReplayMode`, `VerificationDisposition`, `A3ReplayRequest`,
  `A3ReplayResult`, `A3VerificationResult`, `A3PolicyComparisonRecord`;
- comparison: `A2Side`, `A3Side`, `DirectionAxis`, `OpportunityAxis`,
  `DisagreementClass`, `InformationAddition`, `A2A3ComparisonRecord`;
- cost: `CostKnowledge`, `CostMeasure`, `UsageAttribution`, `A3CostSummary`;
- failure: `A3FailureEvent`, `A3FailureSummary`, `DegradationSummary`;
- evaluation: `A3HardeningResult`, `A3CorpusManifest`;
- closure seam: `MilestoneEvidence`, `A3ClosureReadinessRecord`.

`A3HardeningResult` composes references to replay, verification, comparison,
cost and failure records plus pass/fail/unknown checks. It does not embed all
children. `A3ClosureReadinessRecord` aggregates evidence status, not market
opinions or an automatic freeze decision.

All contracts reject unknown fields except explicitly bounded descriptive labels.
No general metadata policy escape. JSON arrays round-trip to tuples. Naive
datetimes fail; other aware zones normalize to Asia/Kolkata and serialize `+05:30`.

## 15. Closure-readiness seam

The later major closure consumes, but is not performed by, A3.10. A versioned
`A3ClosureReadinessRecord` references:

- capability and accepted tag/commit inventory;
- focused/full test and boundary-gate results;
- live-validation claims and explicit non-claims per capability/provider;
- deterministic/no-LLM and future nondeterministic boundaries;
- corpus manifest, replay coverage and parity evidence;
- A2 preservation/comparison examples;
- cost knowledge/ledger reconciliation and failure-matrix coverage;
- unresolved deferral IDs and known architectural risks;
- regression baseline and artifact fingerprints.

Each item is `PASS`, `FAIL`, `UNKNOWN` or `NOT_APPLICABLE`, with evidence refs and
timestamp. UNKNOWN cannot pass a required closure gate. The record says
`READY_FOR_CLOSURE_REVIEW` only when all required evidence is PASS; a human/user
still accepts/finalizes closure. It cannot assert profitability or live coverage
beyond linked studies.

## 16. Implementation work packages

1. **WP1 — Capture contracts/store:** manifest, blob references, portable envelope,
   A2 capture modes, append-only local corpus and secret scan.
2. **WP2 — Integrity/fingerprints:** complete checksum hierarchy, cross-record
   identity/as-of/schema/policy/reference validation and typed capture failures.
3. **WP3 — Replay:** recorded replay, component verification plan/dispositions,
   deterministic verifier and explicit comparison replay.
4. **WP4 — A2/A3 comparison:** closed axes/taxonomy/additions, no scalar/winner,
   reason/evidence lineage and immutable comparison fingerprint.
5. **WP5 — Cost accounting:** leaf attribution, reconciliation, reuse/fallback,
   unknown/unpriced monetary semantics and original/replay separation.
6. **WP6 — Failure/degradation:** lossless child mapping, lineage, impact and
   captured-state verification without new A3.9 rules.
7. **WP7 — Fault-injection corpus:** deterministic matrix, append-only fixtures,
   provenance/origin labels and no live outage fabrication.
8. **WP8 — Parity/isolation:** provider/model/framework-disabled replay,
   serial/LangGraph equivalence and semantic-versus-exact tests.
9. **WP9 — Public acceptance/closure seam:** 14-case helper, hardening result,
   closure-readiness record and reports.
10. **WP10 — Full hardening/regression:** cumulative A1–A3 tests, security,
    dependency, link, documentation and boundary checks.

WP order is deliberate: comparison/cost/failure projections consume a validated
package; public acceptance consumes all prior records. No work package can alter
accepted intelligence policy to satisfy a gate.

## 17. Test plan

Required tests cover:

- ContractModel immutability/list-to-tuple/JSON round-trip/timezone behavior;
- complete/full and projection-only A2 package modes;
- exact checksum, semantic hash, missing/tampered/reordered references;
- schema/policy/runtime mismatch and future/non-replayable model behavior;
- recorded replay with provider/model/network/framework imports blocked;
- deterministic component dispositions and no external fallback;
- every direction/opportunity axis and disagreement class;
- A2 NO_TRADE/class/direction/score/eligibility-basis byte preservation;
- risk/timing/context/gap additions without “better” claims;
- original versus replay consumption and cost-knowledge invariants;
- leaf rollup, nested-controller no-double-debit, failure/fallback charging,
  reuse semantics, held reservations and no-LLM/provider-cost separation;
- complete normalized failure matrix while retaining child codes/messages;
- optional failure survival, required Risk restriction, deadlines and budgets;
- ABSTAIN/insufficient, unknown F&O, non-F&O skip and stale evidence;
- serial/LangGraph parity, operational permutation and semantic mutation;
- append-only/idempotent corpus and secret scanning;
- no A4/A5/A6/A7 fields, calls or imports, and no authority-bearing
  recommendation or profitability claims;
- all 14 black-box scenarios, closure record truth and full regression.

## 18. Risks and controls

| Risk | Architectural control |
|---|---|
| “Exact replay” used for unequal modes | Closed replay mode and result type; exact checksum and semantic comparison separate |
| Comparison becomes arbitration | Preserve both sides; no scalar/winner/recommendation field; closed observational mappings |
| Nested cost double debit | Leaf accounting IDs plus parent reconciliation and `included_in_original_total` |
| Unknown cost becomes zero | `CostKnowledge`; amount prohibited for UNKNOWN/UNPRICED |
| Aggregation erases child error | Required original code/artifact/attempt references and lossless event lineage |
| Replay contacts live service | No handles, import/socket guards, missing artifact fails |
| Future model output is re-inferred | RECORDED_ONLY disposition; model/config/prompt provenance requirement |
| Version drift is silent | Exact schema/policy/runtime support matrix; new comparison record |
| Timing pollutes semantics | Accepted child exclusions plus explicit package semantic/exact rules |
| Hardening retunes A3.9 | Read/verify only; expected states come from frozen `tiaf-a3.9` |
| Closure overstates evidence | Typed PASS/FAIL/UNKNOWN/N/A with linked live claims/non-claims |

Residual limitations are intentional: local-scale corpus only; no arbitrary
historical availability reconstruction; no scheduled outcome acquisition; no
production SLO/recovery; no monetary price inference where source pricing is
absent; no empirical value/profit evaluation; no fresh model replay. These map to
existing deferrals, so this architecture pass adds no new deferral record.

## 19. Architecture acceptance criteria

Ready for implementation only if the implementation follows this design and can
prove all of the following without changing accepted A3 semantics:

- self-contained, integrity-checked recorded replay with zero external access;
- explicit deterministic/comparison modes and future model recorded-only behavior;
- independently preserved A2/A3 sides and closed observational taxonomy;
- exact leaf cost reconciliation with unknown distinct from zero;
- lossless failure lineage and captured degradation truth;
- semantic/exact identity hierarchy and serial/LangGraph parity;
- append-only cumulative corpus and 14 public scenarios;
- closure-readiness evidence without performing closure;
- no A4–A10 authority leakage and full regression.

## 20. Implementation result

The ten work packages are implemented as follows:

- `contracts.py`, `package.py`, and `store.py` implement immutable manifests,
  portable envelopes, exact/content-addressed blobs, two honest A2 modes, and
  append-only local records;
- `replay.py` separates recorded replay, deterministic verification, and policy
  comparison; it never labels comparison as historical replay;
- `comparison.py` preserves A2 and A3 independently with closed axes,
  coexisting disagreement labels, and attributable information additions;
- `cost.py` reconciles A3.8 reservation leaves once, exposes nested provider
  attempts without debiting them again, separates replay use, and preserves
  `UNKNOWN`/`UNPRICED` monetary states;
- `failures.py` retains original child type/code/message digest and identifiers,
  and projects accepted A3.8/A3.9 degradation without a new synthesis rule;
- `evaluation.py` composes immutable hardening results, corpus manifests, and
  the later closure-readiness seam;
- the 22-case deterministic fault manifest and 14-case public corpus are
  explicitly `SYNTHETIC`, versioned, and offline.

`scripts/a3_10_user_acceptance.py` reports package/replay identities, both
comparison sides, axes, additions, failures/degradation, original versus replay
usage, cost knowledge, fingerprints/checksums, and gaps. Package-backed cases
are distinguished from two explicit closed-function probes: case D supplements
the persisted conflict capture with a neutral-direction axis probe; case G uses
captured partial applicability plus the separately tested synthetic optional-
failure normalizer. Neither is represented as live market evidence.

After A3.10 acceptance, perform a separate **TIAF_A3 Major Milestone Closure +
Deferral Burn-down**. Do not merge that review into A3.10.

## 21. Architecture-pass baseline

| Gate | Result |
|---|---|
| `.venv/bin/pytest -q tests/unit/agents tests/unit/market_intelligence tests/unit/planner tests/unit/workflows tests/unit/opportunity_intelligence` | 554 passed in 31.76s |
| `.venv/bin/pytest -q` | 1,860 passed in 35.48s |
| `.venv/bin/python -m compileall src scripts` | Passed |
| `.venv/bin/ruff check src tests scripts` | All checks passed |
| `.venv/bin/mypy src tests` | No issues in 430 source files |
| `.venv/bin/python -m pip check` | No broken requirements; non-blocking sandbox pip-cache warning |
| `git diff --check` | Passed |
| Changed-document relative links | 105 checked; none missing |
| Runtime/dependency/deferral diff | None |

Architecture/security isolation is unchanged because this pass changes only
documentation. Existing focused tests cover provider/model/execution isolation;
the implementation plan adds explicit replay import/socket guards. No live call
was required or made. No `.env` content was read or changed.

The architecture decision was `READY_FOR_A3_10_IMPLEMENTATION`. Implementation
acceptance results are recorded in
[`STUDY_A3_10_USER_LEVEL_ACCEPTANCE.md`](STUDY_A3_10_USER_LEVEL_ACCEPTANCE.md).
