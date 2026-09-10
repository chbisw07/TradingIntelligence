# TIAF A3.8 — Deterministic User-Level Acceptance

## Status and scope

Implementation-pass acceptance, 2026-09-10 (Asia/Kolkata); representative capture
inspection at `2026-09-10T19:30:23.404521+05:30`. Decision:
**READY_TO_ACCEPT_A3_8**. User acceptance/freeze is separate; the base remains
`tiaf-a3.7` (`dbcad3b`). No commit, tag or push was performed.

This is **offline synthetic/captured acceptance**, not live market validation.
Fixtures use fixed `2026-09-10T12:00:00+05:30` evidence and attributed synthetic
instrument mappings. They do not assert current KAYNES F&O membership, prices,
financial results, corporate events or sector mapping. No credentials or `.env`
content were read or changed for acceptance.

The implementation is the bounded A3.8 workflow layer, not the A3.9 public
intelligence product, a recommendation/arbitration engine, scanner, option
selector, position manager or broker executor. The accepted A2 baseline and all
existing specialist interpretation policies are unchanged.

## Reproduction

```bash
python -m pip install -e '.[dev,orchestration]'
python scripts/a3_8_user_acceptance.py
# Framework-free alternative:
python scripts/a3_8_user_acceptance.py --adapter serial
```

The installed optional adapter is pinned to `langgraph==1.2.11`. The script uses
public `run_serial`, `run_langgraph`, `capture_json` and `verify_deterministic`
APIs. Both adapters use one coordinator/policy; there is no separate serial
policy engine. Framework state stays local to the adapter, with tracing disabled.

## Observed public matrix

All **14 cases passed**. Every case was executed with both adapters; its captured
record was checked offline and serial/LangGraph semantic fingerprints matched.
Counts below are **per adapter**, not sums of replay verification invocations.

| Case | Result | Specialist attempts | Fixture provider calls | Plan versions | Proof |
|---|---|---:|---:|---:|---|
| A. Attributed non-F&O equity | PARTIAL | 7 | 0 | 1 | Derivatives skipped; Risk still attempted. |
| B. Existing evidence | PARTIAL | 8 | 0 | 1 | Captured families reused; no acquisition. |
| C. Missing financial family | PARTIAL | 8 | 1 | 1 | Existing MI router/normalizer acquires once before specialist execution. |
| D. Material discovered claim | PARTIAL | 12 | 1 | 2 | Existing authoritative gateway; only News, Sector, Quality and Risk rerun. |
| E. Rate-limited source | PARTIAL | 8 | 2 | 1 | Fixture Tapetide RATE_LIMITED → policy-authorized Yahoo fallback; typed failure retained. |
| F. Unsupported financial need | PARTIAL | 8 | 0 | 1 | Missing evidence remains explicit; no manufactured financial facts. |
| G. Changed derivatives chain | PARTIAL | 11 | 0 | 2 | Only Derivatives, Quality and Risk rerun; original outputs superseded. |
| H. Zero acquisition budget | PARTIAL | 8 | 0 | 1 | BUDGET_EXHAUSTED; available deterministic Risk interpretation survives. |
| I. Explicit index context | PARTIAL | 7 | 0 | 1 | Company Fundamental specialist skipped. |
| J. Unknown F&O eligibility | PARTIAL | 7 | 0 | 1 | Derivatives not guessed; unresolved eligibility recorded. |
| K. Missing mappings | PARTIAL | 8 | 0 | 1 | Missing benchmark/sector mapping retained. |
| L. Unsupported instrument | INSUFFICIENT_EVIDENCE | 0 | 0 | 1 | No invented applicable specialist or neutral verdict. |
| M. DAY/shallow profile | PARTIAL | 7 | 0 | 1 | Fundamental skipped by the bounded DAY policy; no automatic deep research. |
| N. KAYNES, 14–42 days | PARTIAL | 8 | 0 | 1 | Independent opinions, unchanged A2, gaps and disagreement preserved. |

Totals: **28 workflow executions**, 107 specialist attempts per adapter before
verification reexecution, **8 fixture provider attempts across both adapters**,
and **zero live provider calls**. The four fixture calls per adapter are C:1,
D:1 and E:2. No live failure was manufactured. Offline replay makes no further
provider call. All cases report **zero LLM calls, input/output tokens and cost
units**. Sparse evidence is intentionally not upgraded to a COMPLETE result.

## KAYNES illustrative evidence reconciliation

Inputs: canonical KAYNES, OPPORTUNITY purpose, POSITIONAL style, 14–42 day horizon,
supplied synthetic NIFTY/sector/F&O references, fixed aware as-of. Macro is not
requested. Stable waves are:

1. Derivatives Context, Fundamental, News/Event.
2. Relative Strength, Sector, Technical.
3. Opportunity Quality and Opportunity Risk, independent after upstream barriers.

The supplied A2 judgment stays **NEGATIVE / NO_TRADE / score 30**. No A2 calculation
or policy modification occurs. Observed independent opinions:

| Specialist | Stance / run status | Comparison to A2 |
|---|---|---|
| Technical | POSITIVE / PARTIAL | DISAGREES |
| Fundamental | INSUFFICIENT_EVIDENCE | NOT_COMPARABLE |
| News/Event | INSUFFICIENT_EVIDENCE | NOT_COMPARABLE |
| Relative Strength | INSUFFICIENT_EVIDENCE | NOT_COMPARABLE |
| Sector | INSUFFICIENT_EVIDENCE | NOT_COMPARABLE |
| Derivatives Context | NEUTRAL / SUCCESS | PARTIALLY_AGREES |
| Opportunity Quality | NEGATIVE / SUCCESS | AGREES |
| Opportunity Risk | NEUTRAL / SUCCESS | DISAGREES |

The missing company dimensions, complete clustered-event schema, relative/sector
core evidence and Technical MTF coverage are retained. Stop:
`UNSUPPORTED_REMAINING`. Confidence and typed specialist details remain in each
original opinion; the Planner neither averages them nor chooses a winner.
The directional differences above are fixture observations, not market advice.

## Work-package and boundary proof

- **WP1–3:** immutable contracts, canonical aware Asia/Kolkata timestamps,
  capability-driven selection, required/optional evidence, versioned DAG and
  deterministic missing-evidence/depth/stop policy. Package `0.1.0`, base schema
  `1.0` and existing opinion schema `2.0` remain distinct and unchanged.
- **WP2 projection seam:** typed field extractors, explicit derived/inference
  labeling, source opinion/schema/input identity and citations; no summary/prose
  parsing or duplicate A2 fact creation. UNKNOWN/ABSTAIN is not projected as a
  substantive fact. Conservative citation unions are disclosed in the design.
- **WP4–5:** LangGraph isolation, serial parity and completion barriers;
  shuffled delays demonstrate simultaneous work greater than one and at most
  three. Atomic competing reservation tests admit only budget-covered work.
  Concurrent duplicate acquisition joins the same future and one provider call.
- **WP6:** progressive missing-family acquisition, material official confirmation,
  permission/depth-gated deep research from existing normalized runs, bounded
  one-hop as-of/allowed-relation graph reuse and preserved original snapshots.
  Missing deep-research prerequisites remain gaps, not raw-data fabrication.
- **WP6–7:** changed chain reruns only its declared consumers; unrelated or
  acquisition-time-only revisions do not reinterpret unchanged inputs. Prior
  matching runs are captured/reused without restamping. Replan limits supersede
  direct and transitive stale opinions. Quality/freshness revisions invalidate
  subscribers, while unchanged projected output permits projection-only
  downstream reuse. Budgets/permissions never reset.
- **WP7:** partial/insufficient/ABSTAIN, returned runtime failures, exceptions,
  deadline/budget denials and terminal failures preserve distinct outcomes.
  Known consumption is separated from held unknown allowances; failed/timeout
  work is not falsely refunded or double counted. Root wall time is not a sum of
  concurrent child elapsed times.
- **WP8:** exact capture checksum, separate semantic fingerprints, resolved child
  artifact references, active/superseded audit and original A2 preservation.
  Tampered or missing captures and changed registries fail verification.
- **WP9–10:** public matrix, full regression and import/AST/security checks.
  A subprocess blocks LangGraph, LangSmith, HTTPX and MCP imports while performing
  recorded replay and deterministic verification. Existing specialist/provider/
  model/execution boundary tests pass. Planner policy has no vendor branches or
  BUY/SELL, winner, quantity, strike, target, stop-loss or probability fields.

No accepted specialist, A2 calculator/scoring policy, provider adapter, execution
module, model gateway or deferred post-A3 architecture was modified. `.env` and
the deferral register are unchanged.

## Replay modes and limits

`replay_recorded` validates and reconstructs the portable captured record without
external execution. `verify_deterministic` additionally rebuilds plans, validates
reservations, reruns the deterministic specialists against the captured packs and
rebuilds projections. Both retain the original A2 reference/fingerprint.

Provider outcomes and timeout/evidence-admission outcomes are captured inputs;
verification does not simulate original wall-clock races or rerun the complete
external acquisition/confirmation state machine. No exact fresh-model replay or
arbitrary historical source-availability claim is made. Version changes require
explicit comparison, not silent migration.

## Quality gates

Run in the repository virtual environment after implementation hardening:

| Command | Observed result |
|---|---|
| `.venv/bin/python scripts/a3_8_user_acceptance.py` | PASS: 14 / FAIL: 0; both adapters and offline verification. |
| `.venv/bin/pytest -q tests/unit/agents tests/unit/market_intelligence tests/unit/planner tests/unit/workflows` | **489 passed** in 13.55s. |
| `.venv/bin/pytest -q` | **1,795 passed** in 16.80s. |
| `.venv/bin/python -m compileall src scripts` | Passed. |
| `.venv/bin/ruff check src tests scripts` | All checks passed. |
| `.venv/bin/mypy src tests` | Success; no issues in **418 source files**. |
| `.venv/bin/python -m pip check` | No broken requirements found. |
| `git diff --check` | Passed; untracked new files checked separately. |

There are **70 new planner/workflow test cases** over the 1,725-test accepted
base. Full/focused runs include the public matrix subprocess. All-ABSTAIN and
terminal-failure tests use explicit deterministic test stubs; they do not retune
production specialists to produce those outcomes.

## Remaining limits and decision

No acceptance blocker was observed. This is bounded in-process execution, not a
durable/distributed scheduler. A timed-out synchronous worker may finish later;
admission stops, its unknown allowance remains held, and late output is not
published into the completed record. Parallel source acquisition is not claimed:
controlled acquisitions are serial at barriers, with a thread-safe single-flight
seam. The policy supports deterministic `ModelTier.NONE` only. Sparse fixtures
prove honest degradation, not complete market coverage or predictive accuracy.

Existing historical-reconstruction, automatic mapping, unavailable derivatives,
distributed-operation and later-product deferrals remain unchanged. Suggested
commit message, for the user to apply after acceptance:

`feat(orchestration): implement bounded A3.8 planner and replayable specialist workflows`

## Files changed

- `src/tiaf/planner/`: `__init__.py`, `digests.py`, `models.py`, `policy.py`,
  `projection.py`.
- `src/tiaf/workflows/`: `__init__.py`, `coordinator.py`, `langgraph_adapter.py`,
  `ledger.py`, `records.py`, `registry.py`, `replay.py`, `services.py`.
- `scripts/`: `_a3_8_fixtures.py`, `a3_8_user_acceptance.py`, `README.md`.
- `tests/unit/planner/`: `__init__.py`, `test_contracts_policy.py`;
  `tests/unit/workflows/`: `__init__.py`, `test_hardening.py`, `test_orchestration.py`.
- `pyproject.toml`, `README.md`, `CHANGELOG.md`.
- `docs/`: `ARCHITECTURE.md`, `TIAF_A3_ARCHITECTURE.md`,
  `TIAF_A3_DETAILED_ROADMAP.md`, `TIAF_CAPABILITY_MAP.md`,
  `TIAF_IMPLEMENTATION_TARGETS.md`, `TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md`,
  and this study. Index changes include the preceding architecture pass.
