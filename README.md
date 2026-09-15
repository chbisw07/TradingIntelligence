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

Status checked **2026-09-15 (Asia/Kolkata)**. The
[milestone ledger](docs/MILESTONES.md) owns history, tags and closure evidence.

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
| A7 | ARCHITECTURE ACCEPTED / THESIS RECONCILED / IMPLEMENTATION NOT_STARTED / RUNTIME NOT_IMPLEMENTED | Integrated around accepted FF; no runtime authorization | a separately authorized FF-0.1 contracts / target / clock foundation request |
| Forecasting Framework (FF) | ARCHITECTURE ACCEPTED / THESIS RECONCILED / IMPLEMENTATION NOT_STARTED / MINIATURE REALIZATION DEFINED / RUNTIME NOT_IMPLEMENTED | Stable primitive/composite forecaster platform; common ground truth and paired evaluation | All 28 findings reconciled; FF architecture ACCEPTED; A7 integration RECONCILED; A7 architecture ACCEPTED; FF-0 plan COMPLETE; separately authorized FF-0.1 NEXT; no implementation approval |
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
`expression.assess` PUBLISHED; A7 ARCHITECTURE ACCEPTED / THESIS RECONCILED / IMPLEMENTATION NOT_STARTED / RUNTIME NOT_IMPLEMENTED.**
The non-normative A7 reference is available as [PDF](docs/TI_Forecasting_Evaluation_Learning_Thesis.pdf)
and [editable DOCX](docs/TI_Forecasting_Evaluation_Learning_Thesis.docx), with a
[creation record](docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md).
All [17 thesis findings are reconciled](docs/TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md).
Independent [A7 architecture acceptance](docs/TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) is complete; implementation is not started.
The reconciled [Forecasting Framework architecture](docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md),
[bounded FF roadmap](docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) and
[decision/reconciliation](docs/TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md)
define the stable platform: **forecasting is a platform capability; forecasters
are replaceable scientific instruments**. Its miniature is defined, not implemented.
[FM/LFDE](docs/TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md) remains an
advanced family inside FF; its scientific internals are retained.
The existing FM/LFDE thesis is unchanged: [PDF](docs/TI_FM_LFDE_Market_State_Forecasting_Thesis.pdf),
[editable DOCX](docs/TI_FM_LFDE_Market_State_Forecasting_Thesis.docx) and
[creation/findings record](docs/TIAF_FM_LFDE_THESIS_RECORD.md).
**FF ARCHITECTURE ACCEPTED; FFA-B01 CLOSED; FF THESIS RECONCILED.**
Next: FF-0.1 contracts / target / clock foundation, only after a separate implementation request.
A6 remains FROZEN and A7 ARCHITECTURE ACCEPTED; IMPLEMENTATION NOT_STARTED. No runtime, training,
model approval or new consumer authority is implied.
The [A7 architecture](docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md),
[detailed roadmap](docs/TIAF_A7_DETAILED_ROADMAP.md) and
[reconciliation record](docs/TIAF_A7_RECONCILIATION_RECORD.md) propose one exact
next-session equity-return target, chronological calibration/evaluation and
explicit model approval. No trained model, new capability or automatic A4/A5/A6
influence exists; the catalog remains nine. The bounded
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
  → A6 FROZEN (`tiaf-a6-baseline`) → A7 ARCHITECTURE ACCEPTED / IMPLEMENTATION NOT_STARTED → A8 → A9 → A10
```

Forward sequence: `A6.1 → A6.2 → A6.3 → A6.4 → A7 → A8 → A9 → A10`.

## NEXT STEPS

1. **TIAF A7 / FF-0.1 — CONTRACTS, TARGET AND CLOCK FOUNDATION IMPLEMENTATION**.
   Review the [FF-integrated A7 architecture and ownership crosswalk](docs/TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md).
   FF and A7 architectures are independently accepted; implementation is NOT_STARTED.
2. Review the [completed FF-0 plan](docs/TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md).
   After separately authorized FF-0.1, proceed through accepted FF-0.2–FF-0.4
   gates. FF-1/2 and optional families need their own requests; plan readiness
   grants no authority beyond FF-0.
3. Preserve frozen A5/A6 and the unchanged A8/A9/A10 major order. All forecasting
   runtime remains NOT_IMPLEMENTED; no model or data approval is implied.

## Parallel / Future Workstreams

Accepted design does **not** imply implemented runtime. These are not additional
A5 tag gates or an instruction to start parallel implementation.

| Workstream | Architecture accepted? | Implementation started? | Placement |
|---|---|---|---|
| TI Monitoring | Yes | Runtime: NOT_IMPLEMENTED; A5 intent exists | A8/A9 integration; A10 operations |
| Trading Ecosystem | Yes, responsibility model | Integration: NOT_IMPLEMENTED | A8/A9/A10 |
| Forecasting / evaluation | [FF platform ACCEPTED](docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md); A7 architecture ACCEPTED, thesis reconciled | NOT_IMPLEMENTED | completed FF-0 plan → separately authorized FF-0.1 |
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

## Forecasting Framework and A7 — architecture accepted; FF-0 plan complete

The [bounded FF-0 implementation plan](docs/TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md) is complete
(**READY_FOR_FF0_IMPLEMENTATION**, planning only). It chooses synthetic captured-input
BaseRate mechanics, four FF-0 steps and a 28-case acceptance corpus. FF-0.1 is
next only under a separate implementation request; calibration stays at FF-2,
public capability publication stays separate, and runtime remains NOT_IMPLEMENTED.

The [A7 acceptance](docs/TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) records
**A7_ARCHITECTURE_ACCEPTED** on **2026-09-15 (Asia/Kolkata)**:
A6 FROZEN; FF ARCHITECTURE ACCEPTED; A7 ARCHITECTURE ACCEPTED;
A7 THESIS RECONCILED AS NEEDED; A7 / FF IMPLEMENTATION NOT_STARTED;
RUNTIME NOT_IMPLEMENTED. FM/LFDE remains an optional advanced Forecaster family.

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

Exact next prompt: **TIAF A7 / FF-0.1 — CONTRACTS, TARGET AND CLOCK FOUNDATION IMPLEMENTATION**.
This is planning readiness only. FF-0.1 still needs separate authorization;
this pass does not authorize training, model approval, publication, frozen-A6
changes or A8.
