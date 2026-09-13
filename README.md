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

Status checked **2026-09-13 (Asia/Kolkata)**. The
[milestone ledger](docs/MILESTONES.md) owns history, tags and closure evidence.

| Workstream | State | Meaning | Next step |
|---|---|---|---|
| TGT0 / A0 | FROZEN | Repository and contract foundations | Preserve |
| A1 / A2 / A3 / A4 | FROZEN | Data, deterministic benchmark, specialists, arbitration | Preserve baselines |
| TI_SHELL v0.1 | FROZEN | Governed local command client | Preserve boundary |
| A5 | ACCEPTED / FREEZE_READY | Single-position advice; final check: `READY_TO_TAG_A5`; tag absent | Save reviewed docs and separately authorize tag |
| R1 | ACCEPTED | Required scope and explicit absence fixed | Preserve old/new replay |
| R2 / R3 / R4 / R5 | PENDING — BEFORE_A6 | Cross-cutting pluggability remediation / hardening track; not A5.x | After A5 tag; does not block it |
| A6 | NOT_IMPLEMENTED | Deterministic option expression; not started | After R2–R5 acceptance |

FROZEN means an existing accepted tag; ACCEPTED means reviewed bounded scope;
FREEZE_READY is not a tag. ACTIVE names the current task, PENDING the gated
queue, DEFERRED registered postponed work, FUTURE later work, TBD unresolved
placement/design, and NOT_IMPLEMENTED absence of runtime.

## CURRENT ACTIVE WORKSTREAM

**ACTIVE: A5 documentation/navigation closeout and tag handoff.** The
[final readiness review](docs/TIAF_A5_FINAL_FREEZE_TAG_READINESS_CHECK.md)
already returned `READY_TO_TAG_A5` at `fe8c528`; that check is not pending.
The remaining action is to review/save the final readiness and navigation docs,
then separately authorize commit/push and creation/push of the proposed
`tiaf-a5-baseline` tag against the reviewed tree. No such action is performed
by this documentation pass.

### Current Active Path

```text
Final A5 readiness: READY_TO_TAG_A5 (done)
  → save/review documentation → authorized commit/push + A5 tag
  → R2 → R3 → R4 → R5 (bounded pre-A6 hardening queue)
  → A6 architecture / deterministic expression
```

## NEXT STEPS

1. Review the final documentation-only diff and save the readiness record.
2. Separately authorize documentation commit/push and `tiaf-a5-baseline` tag.
3. Execute and accept bounded R2–R5 hardening; preserve A1–A5 semantics.
4. Begin A6 architecture, then deterministic supported single-leg CE/PE expression.

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

For runtime dependencies only, use `python -m pip install -e .`.
The optional `orchestration` extra pins LangGraph for the A3.8 adapter; serial
execution and offline captures do not require it. Run the offline public matrix
with `python scripts/a3_8_user_acceptance.py` (or `--adapter serial`).

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
