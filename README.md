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

Status checked **2026-09-14 (Asia/Kolkata)**. The
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
| A7 | ACTIVE / NEXT — NOT_IMPLEMENTED | Forecasting, evaluation and learning architecture is next; no runtime exists | Architecture pass |
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
`expression.assess` PUBLISHED; A7 ACTIVE / NEXT — NOT_IMPLEMENTED.** The bounded
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
  → A6 FROZEN (`tiaf-a6-baseline`) → A7 ACTIVE / NEXT → A8 → A9 → A10
```

Forward sequence: `A6.1 → A6.2 → A6.3 → A6.4 → A7 → A8 → A9 → A10`.

## NEXT STEPS

1. **TIAF A7 — FORECASTING, EVALUATION & LEARNING ARCHITECTURE PASS**.
2. Preserve the deterministic A6 baseline; A7 is not implemented yet.

## Parallel / Future Workstreams

Accepted design does **not** imply implemented runtime. These are not additional
A5 tag gates or an instruction to start parallel implementation.

| Workstream | Architecture accepted? | Implementation started? | Placement |
|---|---|---|---|
| TI Monitoring | Yes | Runtime: NOT_IMPLEMENTED; A5 intent exists | A8/A9 integration; A10 operations |
| Trading Ecosystem | Yes, responsibility model | Integration: NOT_IMPLEMENTED | A8/A9/A10 |
| Forecasting / evaluation | A7 roadmap; detailed design future | NOT_IMPLEMENTED | A7 after initial A6 |
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
