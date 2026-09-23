# TradingIntelligence

TradingIntelligence implements **TIAF — Trading Intelligence Agent Fabric**:
reusable, evidence-linked market and position intelligence. Today it is a
governed local Python facade and command-first Shell, not a deployed trading
service or execution engine.

## North Star

Turn scanner, watchlist, manual and third-party inputs into explainable,
replayable decision support. Preserve deterministic baselines, uncertainty,
disagreement and `NO_TRADE`. Intelligence is pluggable; TradeMonitor retains
risk/capital/action authority and the broker retains execution truth.

## Current Project Status

**Current checkpoint — 2026-09-23 (Asia/Kolkata):** FF-0 COMPLETE / FROZEN at
`tiaf-a7-ff0-baseline`; FF-1 COMPLETE / FROZEN at `tiaf-a7-ff1-baseline`
(`21783ea31d4ce3b54fbcc6fcce6ef7e641bd5bec`). FF-1 scientific outcome remains
**INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE**; infrastructure accepted,
Logistic CHALLENGER / EXPERIMENTAL, promotion eligible NO; BaseRate BENCHMARK.
2025 is CONSUMED, executions used 1, post-holdout refit allowed NO.

**FLC — Forecaster Lifecycle Completion is CURRENT**: architecture/gap plan
complete; FLC-1 inference, FLC-2 training/custody/lifecycle, FLC-3 synthetic-only
optimization, FLC-4 model-specific diagnostics and FLC-5 synthetic calibration
composition readiness, FLC-6 reusable independent Evaluation and FLC-7
integration/provenance/replay hardening implemented.
Logistic is the sole learned reference;
no additional families or FF-0 behavior change. **FF-2 is intentionally
DEFERRED / NOT_STARTED until FLC closure**, then only a separately approved new
research proposal with new validation evidence. Eligibility is not a fit grant.
A7 overall remains IN_PROGRESS; no public forecasting capability or A4/A5/A6 influence.

See [FF lifecycle architecture](docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#22-forecaster-lifecycle-completion-flc)
and [FLC gaps/packages](docs/TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md).
See the [FLC-1 implementation and validation](docs/TIAF_A7_FLC_1_FORECASTER_CONTRACT_AND_LIFECYCLE_SEAM_NORMALIZATION.md).
See the [FLC-2 implementation and validation](docs/TIAF_A7_FLC_2_TRAINING_MODEL_IDENTITY_PERSISTENCE_AND_LIFECYCLE_NORMALIZATION.md).
See the [FLC-3 synthetic-only optimization and validation](docs/TIAF_A7_FLC_3_BOUNDED_DEVELOPMENT_ONLY_OPTIMIZATION.md).
See the [FLC-4 model-specific diagnostics and validation](docs/TIAF_A7_FLC_4_MODEL_SPECIFIC_DIAGNOSTICS_NORMALIZATION.md).
See the [FLC-5 calibration composition and validation](docs/TIAF_A7_FLC_5_CALIBRATION_COMPOSITION_READINESS.md).
See the [FLC-6 reusable independent Evaluation and validation](docs/TIAF_A7_FLC_6_REUSABLE_INDEPENDENT_EVALUATION_NORMALIZATION.md).
See the [FLC-7 integration, provenance and replay hardening](docs/TIAF_A7_FLC_7_INTEGRATION_PROVENANCE_AND_REPLAY_HARDENING.md).
Exact next task: **TIAF A7 / FLC-8 — REFERENCE IMPLEMENTATION CLOSURE AND FLC ACCEPTANCE**, separately requested.

### Historical execution and preparation checkpoints

Execution checkpoint: [one-shot protected 2025 final-holdout evaluation](docs/TIAF_A7_FF1_ONE_SHOT_PROTECTED_2025_FINAL_HOLDOUT_EVALUATION.md)
returns **FF1_FINAL_HOLDOUT_ACCEPTED**, scientific outcome **INSUFFICIENT_EVIDENCE**
(`CONFIDENCE_NONDECISIVE`). All 249 origins paired; 128 positive / 121 zero,
100% coverage, 49 complete blocks, no exclusions. Captured replay **MATCH**;
**3,445** full-suite tests passed at execution (not rerun for documentation closure).
2025 is permanently **CONSUMED**, evidence
**COMPLETE**, execution count **1**. No post-holdout refit, retry or automatic
promotion; Logistic remains CHALLENGER / EXPERIMENTAL and BaseRate BENCHMARK.

The following checkpoints retain their as-of-review states; their SEALED/NOT_RUN
statements are historical, superseded by the completed execution above.

Development checkpoint: [FF-1.4 development-only paired evaluation](docs/TIAF_A7_FF1_4_DEVELOPMENT_ONLY_PAIRED_BASERATE_VS_LOGISTIC_EVALUATION.md)
has evaluated **969 paired 2021–2024 observations**, with offline reconstruction
MATCH. Development support/stability gates pass; scientific classification is
**INSUFFICIENT_EVIDENCE**, not final support. 2025 remains **SEALED** and final
holdout evidence **NOT_RUN**. **FF1_4_ACCEPTED**; its full-suite checkpoint was
**3,327 passed** (not a new full run in the subsequent documentation review).
No tuning, promotion or public forecast activation. Earlier FF-1.2 queue
statements below describe the historical FF-1.1A checkpoint, not the current queue.

Preparation checkpoint: [pre-holdout fifth-fold preparation](docs/TIAF_A7_FF1_PRE_HOLDOUT_FIFTH_FOLD_ARTIFACT_PREPARATION_AND_AUTHORITY_RECONCILIATION.md)
has produced the missing model/scaler and BaseRate handoff: 1,690 TRAIN rows,
one empirical fit, 11 iterations, reconstruction MATCH.
**FIFTH_FOLD_PREPARATION_COMPLETE**; **3,351** repository tests pass.
The prior independent review is preserved unchanged. That preparation did not
authorize final opening or freeze the decision protocol. 2025 remains **SEALED**
and final evidence **NOT_RUN**. No post-holdout refit is allowed.

Freeze checkpoint: [final-holdout freeze review](docs/TIAF_A7_FF1_FINAL_HOLDOUT_PROTOCOL_FREEZE_REVIEW_WITH_FIFTH_FOLD_HANDOFF.md)
returns **FF1_READY_FOR_FINAL_HOLDOUT**: fifth-fold blocker resolved, exact one-shot
protocol frozen, final evaluation authorized for the separately requested next
pass. **3,414** tests pass; both captured closures replay MATCH. 2025 remains
**SEALED**, final evidence **NOT_RUN**, empirical execution slot unconsumed.

Current queue resumes below; prior freeze/readiness checkpoints are complete.

### Current workstream inventory

| Workstream | State | Meaning | Next step |
|---|---|---|---|
| TGT0 / A0 | FROZEN | Repository and contract foundations | Preserve |
| A1 / A2 / A3 / A4 | FROZEN | Data, deterministic benchmark, specialists, arbitration | Preserve baselines |
| TI_SHELL v0.1 | FROZEN | Governed local command client | Preserve boundary |
| A5 | FROZEN | Single-position Position Intelligence frozen at `tiaf-a5-baseline` | Preserve baseline |
| R1 | ACCEPTED / DONE | Required scope and explicit absence fixed | Preserve old/new replay |
| R2 | ACCEPTED / DONE | Typed discovery metadata; cross-cutting hardening, not A5.x | Preserve discovery baseline |
| R3 | ACCEPTED / DONE | Immutable per-run composition envelope and exact pinned verifier | Preserve capture/verifier baseline |
| R4 | ACCEPTED / DONE | Optional adapter imports and package dependencies isolated | Preserve isolation baseline |
| R5 | ACCEPTED / DONE — BEFORE_A6 | Trusted startup selection, identity and binding freeze | Preserve COLD boundary |
| A6 | FROZEN | Deterministic captured-read Trade Expression Intelligence at `tiaf-a6-baseline`; `expression.assess` PUBLISHED | Preserve baseline |
| A7 | ARCHITECTURE ACCEPTED / IMPLEMENTATION IN_PROGRESS | FF-0 accepted; FF-1 scientific closure accepted, inconclusive; no public forecast capability | FLC-8 closure before FF-2 |
| Forecasting Framework (FF) | ARCHITECTURE ACCEPTED / FF-0 FROZEN / FF-1 FROZEN / FLC CURRENT / FF-2 DEFERRED | Final INSUFFICIENT_EVIDENCE; 2025 CONSUMED / evidence COMPLETE; no promotion | FLC CURRENT; FF-2 intentionally deferred; no refit or recycled holdout |
| FM / LFDE design track | ADVANCED FORECASTER FAMILY IN FF / THESIS RETAINED / RUNTIME NOT_IMPLEMENTED | Market-state/latent-factor research remains intact; not the platform definition | Conditional family research, not a prerequisite to a useful simple FF |
| A8 | PLANNED / NOT_IMPLEMENTED | TradeMonitor integration | After A7 |
| A9 | PLANNED / NOT_IMPLEMENTED | Scanner integration | After A8 |
| A10 | PLANNED / NOT_IMPLEMENTED | Production hardening + Monitoring Runtime operationalization | After A9 |

FROZEN means an existing accepted tag; ACCEPTED means reviewed bounded scope;
DONE means its bounded remediation is closed. READY_FOR_ACCEPTANCE means the
implementation and regression are complete but the closure remains separate.
PENDING is the gated queue, DEFERRED registered postponed work, FUTURE later
work, TBD unresolved placement/design, and NOT_IMPLEMENTED absence of runtime.

## CURRENT ACTIVE WORKSTREAM

**R1–R5 ACCEPTED / DONE; A6 FROZEN at `tiaf-a6-baseline`;
`expression.assess` PUBLISHED; A7 ARCHITECTURE ACCEPTED / THESIS RECONCILED / IMPLEMENTATION IN_PROGRESS (FF-0 ACCEPTED; FF-1 SCIENTIFICALLY CLOSED INCONCLUSIVE) / INTERNAL SYNTHETIC RUNTIME IMPLEMENTED.**
The non-normative A7 reference is available as [PDF](docs/TI_Forecasting_Evaluation_Learning_Thesis.pdf)
and [editable DOCX](docs/TI_Forecasting_Evaluation_Learning_Thesis.docx), with a
[creation record](docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md).
All [17 thesis findings are reconciled](docs/TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md).
Independent [A7 architecture acceptance](docs/TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) is complete; FF-0.1–0.4 add foundation, capture/truth/replay and internal synthetic BaseRate execution, not public forecast exposure.
The reconciled [Forecasting Framework architecture](docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md),
[bounded FF roadmap](docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) and
[decision/reconciliation](docs/TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md)
define the stable platform: **forecasting is a platform capability; forecasters
are replaceable scientific instruments**. Its FF-0 engineering miniature is accepted; FF-1.1A adjusted research data qualification is complete; FF-1 training/evaluation is complete and scientifically closed inconclusive; FF-2 remains future.
[FM/LFDE](docs/TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md) remains an
advanced family inside FF; its scientific internals are retained.
The existing FM/LFDE thesis is unchanged: [PDF](docs/TI_FM_LFDE_Market_State_Forecasting_Thesis.pdf),
[editable DOCX](docs/TI_FM_LFDE_Market_State_Forecasting_Thesis.docx) and
[creation/findings record](docs/TIAF_FM_LFDE_THESIS_RECORD.md).
**FF ARCHITECTURE ACCEPTED; FFA-B01 CLOSED; FF THESIS RECONCILED.**
FF-0 is accepted, including the engineering CLI and all 28 semantic cases.
FF-1 is **FF1_FINAL_CLOSURE_ACCEPTED / FF1_SCIENTIFICALLY_CLOSED_INCONCLUSIVE**.
The outcome remains **INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE**;
infrastructure is accepted. BaseRate remains BENCHMARK and Logistic remains
CHALLENGER / EXPERIMENTAL, promotion eligible NO. 2025 is CONSUMED, executions
used 1, post-holdout refit allowed NO. FF-1 is frozen at `tiaf-a7-ff1-baseline`; FLC is CURRENT.
FF-2 is intentionally DEFERRED / NOT_STARTED until FLC closure; later research
eligibility permits only a new governed proposal, not a fit or activation. A7 remains
IN_PROGRESS; no public forecasting capability or automatic A4/A5/A6 influence.
See the [FLC lifecycle gap/work plan](docs/TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md).
The [A7 architecture](docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md),
[detailed roadmap](docs/TIAF_A7_DETAILED_ROADMAP.md) and
[reconciliation record](docs/TIAF_A7_RECONCILIATION_RECORD.md) propose one exact
next-session equity-return target, chronological calibration/evaluation and
explicit model approval. A fixed Logistic challenger exists without promotion;
no new capability or automatic A4/A5/A6 influence exists; the catalog remains nine. The bounded
[R2 implementation](docs/TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA.md) and
[acceptance](docs/TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA_ACCEPTANCE.md) are
complete. R2 adds typed, permission-filtered declarations without granting
authority or claiming live readiness. The
[R3 implementation](docs/TIAF_PLUGGABILITY_R3_COMPOSITION_ENVELOPE_PINNED_VERIFIER.md)
and [acceptance](docs/TIAF_PLUGGABILITY_R3_COMPOSITION_ENVELOPE_PINNED_VERIFIER_ACCEPTANCE.md)
are complete. R3 records exact run participation and makes deterministic
verification resolve only pinned compatible implementations. Recorded replay
remains registry-free. The
[R4 implementation](docs/TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION.md)
and [acceptance](docs/TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION_ACCEPTANCE.md)
place optional provider/workflow imports behind explicit selection and move
integration SDKs into named extras. The
[R5 implementation](docs/TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md)
adds one trusted startup owner, explicit configuration precedence, secret-free
startup identity and frozen binding snapshots. The independent
[R5 acceptance](docs/TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION_ACCEPTANCE.md)
closes the cross-cutting pre-A6 hardening track without adding HOT behavior.

The [A6 architecture draft](docs/TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md),
[reconciliation record](docs/TIAF_A6_RECONCILIATION_RECORD.md) and
[detailed roadmap](docs/TIAF_A6_DETAILED_ROADMAP.md) now define the proposed
long single-leg CE/PE boundary. A6 is advisory and needs no SigmaDSL or A7. The
accepted versioned policy defaults bound A6.1 and the A6.2 evaluator; the
[A6.3 implementation](docs/TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE.md) now publishes
its captured-read facade/Shell path without live or execution authority; its
[independent acceptance](docs/TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE_ACCEPTANCE.md)
closes the publication slice without freezing A6.
The [A6.4 final hardening and acceptance record](docs/TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md)
adds the explicit 93-case corpus, closes the bounded implementation, and finds
A6 ready to freeze. The final closure freezes that accepted A6.1–A6.4 state at
`tiaf-a6-baseline` without changing its semantics.

The [complete user-reference thesis](docs/TI_Trade_Expression_Intelligence_Thesis.docx)
and [PDF preview](docs/TI_Trade_Expression_Intelligence_Thesis.pdf) are now created.
The [thesis record](docs/TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_THESIS_RECORD.md)
preserves the creation checkpoint. The [fourteen-finding reconciliation](docs/TIAF_A6_THESIS_ARCHITECTURE_RECONCILIATION.md)
adopts clarifications, defers the coverage relaxation and retains the versioned
numeric defaults. The [independent acceptance](docs/TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md)
records READY_TO_IMPLEMENT_A6_1. The subsequent
[A6.1 foundation](docs/TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION.md)
implements only immutable contracts, captured-evidence qualification, pinned
policy, deterministic A4 admission and replay-safe fingerprints. It publishes no
capability and performs no candidate selection. Its
[independent acceptance](docs/TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION_ACCEPTANCE.md)
closes A6.1 without expanding the eight-operation catalog.
The [A6.2 implementation](docs/TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY.md)
adds the internal bounded candidate evaluator, exact lexicographic selection,
structured explanations and captured replay. It still publishes no facade or
Shell capability. Its
[independent acceptance](docs/TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY_ACCEPTANCE.md)
closes A6.2 without expanding the catalog.

### Current Active Path

```text
A5 ── FROZEN (`tiaf-a5-baseline`)
  ↓
R2 ── ACCEPTED / DONE
  ↓
R3 ── ACCEPTED / DONE → R4 ── ACCEPTED / DONE → R5 ── ACCEPTED / DONE
  ↓
A6 ── ARCHITECTURE ACCEPTED / THESIS ACCEPTED
  ↓
A6.1 CONTRACTS / ADMISSION / POLICY — ACCEPTED / DONE
  ↓
A6.2 EVALUATION / RANKING / REPLAY — ACCEPTED / DONE
  ↓
A6.3 FACADE / SHELL — ACCEPTED / DONE → A6.4 ACCEPTED / DONE
  → A6 FROZEN (`tiaf-a6-baseline`) → A7 ARCHITECTURE ACCEPTED / IMPLEMENTATION IN_PROGRESS (FF-0 ACCEPTED; FF-1 SCIENTIFICALLY CLOSED INCONCLUSIVE) → A8 → A9 → A10
```

Forward sequence: `A6.1 → A6.2 → A6.3 → A6.4 → A7 → A8 → A9 → A10`.

## NEXT STEPS

1. **TIAF A7 / FLC-8 — REFERENCE IMPLEMENTATION CLOSURE AND FLC ACCEPTANCE**, separately requested; complete FLC-8 closure.
2. Preserve frozen FF-0/FF-1, consumed 2025 evidence and the no-refit restriction.
3. Defer FF-2 until FLC closes, then consider only a separately approved new governed research proposal
   with new qualified validation evidence; eligibility is not authorization.
4. Continue remaining A7 stages under the accepted FF-0…FF-7 sequence and ownership.
5. Keep A8 deferred under remaining A7; preserve the A8 → A9 → A10 major order.

## Parallel / Future Workstreams

Accepted design does **not** imply implemented runtime. These are not additional
A5 tag gates or an instruction to start parallel implementation.

| Workstream | Architecture accepted? | Implementation started? | Placement |
|---|---|---|---|
| TI Monitoring | Yes | Runtime: NOT_IMPLEMENTED; A5 intent exists | A8/A9 integration; A10 operations |
| Trading Ecosystem | Yes, responsibility model | Integration: NOT_IMPLEMENTED | A8/A9/A10 |
| Forecasting / evaluation | [FF platform ACCEPTED](docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md); A7 architecture ACCEPTED, thesis reconciled | Internal BaseRate and fixed Logistic training/evaluation implemented; FF-1 closed inconclusive; no public forecast capability | FF-0/FF-1 frozen → FLC CURRENT → FF-2 deferred until FLC closure and new governed proposal |
| Sector Rotation | No; TBD idea note | NOT_IMPLEMENTED | FUTURE; relative to A7/A8 TBD |
| Signal Qualification | No; TBD idea note | NOT_IMPLEMENTED | FUTURE; intended after Sector Rotation review, A7/A8 placement TBD |
| TM / Scanner integration | Ecosystem boundaries accepted | NOT_IMPLEMENTED | A8 / A9 respectively |
| Web / multi-console Cockpit | Ownership model accepted; UI design TBD | NOT_IMPLEMENTED | FUTURE; delivery placement TBD |
| Runtime / production hardening | Monitoring/deployment boundaries accepted | Full operational runtime NOT_IMPLEMENTED | A10 |

The [forward roadmap](docs/IMPLEMENTATION_ROADMAP.md) owns the intended queue
and explicitly unresolved ordering; A7 is not required for initial A6.

## Architecture at a Glance

```text
Scanner: discover/propose → TI: assess/advise → TM: authorize/coordinate → Broker: execute
                                ↑                    │                       │
                     TI Monitoring: reevaluate ← supplied position truth ←──┘
Clients (Shell / future Sheets, Web, Cockpit): project results and scoped requests
```

The loop is accepted **future integration design**, not a running monitor.
Current facade access is PURE/CAPTURED_READ only: no public LIVE_READ, broker
operation or recurring scheduler. See the
[ecosystem ownership model](docs/TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md).

## Documentation Map

| Document family | Authority / purpose |
|---|---|
| This README | Executive dashboard: now, next and navigation |
| [MILESTONES](docs/MILESTONES.md) | Canonical historical/current ledger and actual tags |
| [Major roadmap](docs/TRADINGINTELLIGENCE_ROADMAP.md), [forward queue](docs/IMPLEMENTATION_ROADMAP.md), [targets](docs/TIAF_IMPLEMENTATION_TARGETS.md) | Intended order, gates and engineering scope |
| [Thesis](docs/TIAF_THESIS.md), [architecture index](docs/ARCHITECTURE.md) | Conceptual introduction and normative Markdown design map |
| [System](docs/TIAF_SYSTEM_ARCHITECTURE.md), [pluggability](docs/TIAF_PLUGGABILITY_ARCHITECTURE.md), [monitoring](docs/TIAF_MONITORING_ARCHITECTURE.md), [ecosystem](docs/TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md) | Normative boundaries; implementation status remains separate |
| [Deferral register](docs/TIAF_DEFERRAL_REGISTER.md) | Explicit postponed work under stable IDs |
| [Capability map](docs/TIAF_CAPABILITY_MAP.md) | Implemented/exposed versus planned; not an executable registry |
| [TBD index](docs/README_TBD_DESIGN_NOTES.md) | Non-authoritative ideas and future design notes |
| [A4](docs/TIAF_A4_DETAILED_ROADMAP.md) / [A5](docs/TIAF_A5_DETAILED_ROADMAP.md) detailed maps | Implementation, dated STUDY/ACCEPTANCE evidence and historical closures |
| Thesis DOCX/PDF companions | Human-readable teaching material, not normative design or acceptance |

Suggested route: README → [MILESTONES](docs/MILESTONES.md) →
[ROADMAP](docs/TRADINGINTELLIGENCE_ROADMAP.md) →
[THESIS](docs/TIAF_THESIS.md) → [SYSTEM](docs/TIAF_SYSTEM_ARCHITECTURE.md) →
[PLUGGABILITY](docs/TIAF_PLUGGABILITY_ARCHITECTURE.md) →
[MONITORING](docs/TIAF_MONITORING_ARCHITECTURE.md) →
[ECOSYSTEM](docs/TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md) →
[A4](docs/TIAF_A4_DETAILED_ROADMAP.md) / [A5](docs/TIAF_A5_DETAILED_ROADMAP.md).
After each acceptance/tag, update the dashboard, ledger and forward queue
together; preserve earlier studies as dated evidence.

## Repository Layout

- `src/tiaf/` — implemented capability packages and governed local interfaces
- `tests/` — unit, integration and replay suites
- `docs/` — design, ledger, roadmap, deferrals and acceptance evidence
- `examples/` — usage examples
- `scripts/` — bounded diagnostics and helpers; see [script usage](scripts/README.md)

## Installation

Python 3.12 or newer is required. From a virtual environment:

```bash
python -m pip install -e '.[dev,orchestration]'
```

For the provider-free core runtime, use `python -m pip install -e .`. Named R4
extras are `data-provider-dhan`, `market-intelligence-http`,
`market-intelligence-mcp`, `providers`, and `orchestration`; see the
[R4 implementation record](docs/TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION.md).
The `orchestration` extra pins LangGraph for the A3.8 adapter; serial execution
and offline captures do not require it. Run the offline public matrix with
`python scripts/a3_8_user_acceptance.py` (or `--adapter serial`).

The current India deployment defaults symbol-only cash resolution and F&O
universe generation to NSE. Override these non-secret settings when needed:

```bash
TIAF_PRIMARY_EXCHANGE=NSE
TIAF_PRIMARY_FNO_EXCHANGE=NSE
```

## Local TI Shell

The bounded command-first engineering Shell runs in the same process as the
trusted facade. Capability calls require an explicit operator-owned bootstrap;
there is no implicit config discovery.

```bash
python -m tiaf.shell --help
python -m tiaf.shell --config shell-bootstrap.json capabilities list
python -m tiaf.shell --config shell-bootstrap.json
```

The final command enters the `TI> ` REPL. See the
[Shell implementation record](docs/TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md) for
the exact grammar, bootstrap contract and security boundary.

## Verification

```bash
python -m compileall src
pytest
ruff check src tests
mypy src tests
```

### Read-only diagnostics and replay

See [scripts/README.md](scripts/README.md) for option-chain, feature, relative-strength,
MTF and baseline smoke commands, prerequisites and bounded live-call behavior.

Capture normalized evidence once, then replay it without network access:

```bash
python scripts/capture_baseline_snapshot.py \
  --symbol RELIANCE --horizon POSITIONAL --benchmark NIFTY \
  --timeframes 1d,1h,15m --output /tmp/reliance_snapshot.json
python scripts/replay_baseline_snapshot.py \
  --input /tmp/reliance_snapshot.json
```

<a id="forecasting-framework--a7-integrated-architecture-acceptance-next"></a>

## Forecasting Framework and A7 — architecture accepted; FF-0 miniature accepted; engineering-only CLI

The [FF-0.1 foundation](docs/TIAF_A7_FF0_1_CONTRACTS_TARGET_CLOCK_IMPLEMENTATION.md)
and [FF-0.2 capture/truth/replay](docs/TIAF_A7_FF0_2_CAPTURE_STORE_TRUTH_RECORDED_REPLAY_IMPLEMENTATION.md)
remain accepted. The [FF-0.3 implementation record](docs/TIAF_A7_FF0_3_BASERATE_COLD_RUNTIME_PINNED_VERIFICATION_IMPLEMENTATION.md)
records **FF0_3_ACCEPTED**: deterministic synthetic BaseRate, an immutable internal
COLD owner, honest ACTUAL/SIMULATED execution, capture and separate exact pinned
verification. A7 / FF is **IMPLEMENTATION IN_PROGRESS; INTERNAL SYNTHETIC RUNTIME
IMPLEMENTED; PUBLIC FORECAST CAPABILITY NOT_PUBLISHED**.
All four [planned FF-0 steps](docs/TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md)
are complete. The [FF-0.4 engineering CLI](docs/TIAF_A7_FF0_4_ENGINEERING_CLI_ACCEPTANCE_HARDENING_IMPLEMENTATION.md)
and [final FF-0 acceptance](docs/TIAF_A7_FF0_ACCEPTANCE.md) record **FF0_ACCEPTED**:
28/28 semantic cases; **INTERNAL_ENGINEERING_CLI_ONLY**; frozen at `e5283c9`
(`tiaf-a7-ff0-baseline`). The [FF-1 plan](docs/TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md)
is complete. [FF-1.1 qualification/schema tooling](docs/TIAF_A7_FF1_1_DATA_QUALIFICATION_FEATURE_SCHEMA_IMPLEMENTATION.md)
is **FF1_1_ACCEPTED**. Subsequent training and paired evaluation are complete.
Rights remain UNVERIFIED/WARN_ONLY, not legally approved; the adjusted vintage
remains retrospective SIMULATED research, not CAPTURED_AS_KNOWN.
FF-1 is **FF1_FINAL_CLOSURE_ACCEPTED / FF1_SCIENTIFICALLY_CLOSED_INCONCLUSIVE**.
The outcome remains **INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE**;
infrastructure is accepted. BaseRate remains BENCHMARK and Logistic remains
CHALLENGER / EXPERIMENTAL, promotion eligible NO. 2025 is CONSUMED, executions
used 1, post-holdout refit allowed NO. FF-1 is frozen at `tiaf-a7-ff1-baseline`; FLC is CURRENT.
FF-2 is intentionally DEFERRED / NOT_STARTED until FLC closure; later research
eligibility permits only a new governed proposal, not a fit or activation. A7 remains
IN_PROGRESS; no public forecasting capability or automatic A4/A5/A6 influence.
See the [FLC lifecycle gap/work plan](docs/TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md).

The [A7 acceptance](docs/TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) records
**A7_ARCHITECTURE_ACCEPTED** on **2026-09-15 (Asia/Kolkata)**:
A6 FROZEN; FF ARCHITECTURE ACCEPTED; A7 ARCHITECTURE ACCEPTED;
A7 THESIS RECONCILED AS NEEDED; then A7 / FF IMPLEMENTATION NOT_STARTED;
RUNTIME NOT_IMPLEMENTED. The bounded implementation update above supersedes that status.
FM/LFDE remains an optional advanced Forecaster family.

A7 is the lifecycle umbrella. FF owns forecasting contracts, typed DAG and
bounded runtime; Evaluation owns Ground Truth, Outcome Journal, joined Forecast
Ledger, benchmarks/metrics/calibration qualification/drift; Learning owns
candidate fits and the single artifact/lifecycle registry. Independent reviewer
approval and trusted COLD selection stay separate. The
[A7 roadmap](docs/TIAF_A7_DETAILED_ROADMAP.md) contains FF-0…FF-7 unchanged,
with the old A7.1…A7.5 crosswalk. FF-0/1 raw research precedes FF-2's calibrated
miniature; publication is separately accepted, advanced families optional.

The [FF repeat review](docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE_REPEAT.md)
closed FFA-B01; the [A7 integration](docs/TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md)
then reconciled all 17 A7 findings. Original HOLD, correction, repeat acceptance,
integration and all 28 FF findings remain historical evidence. Their then-next
language and the Deferral Register's dated A7.x notes are not the current queue.
All 58 canonical deferral rows and six thesis DOCX/PDF artifacts are unchanged.

Exact next prompt: **TIAF A7 / FLC-8 — REFERENCE IMPLEMENTATION CLOSURE AND FLC ACCEPTANCE**.
No commit, tag or push is performed by this documentation pass. Historical
planning/acceptance records retain their then-current status.
