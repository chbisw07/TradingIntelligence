# Study — TI_SHELL v0.1 Acceptance

## Scope and method

This offline study validates the command-first local Shell implementation over
the accepted frozen-A4 facade. It uses synthetic/captured repository fixtures;
no live provider, network, model, tool or broker call is required or made.

Validation date: 2026-09-12 (Asia/Kolkata).

## Acceptance observations

- `tiaf.shell` provides one-shot and `TI> ` REPL entry modes over the same
  parser, dispatcher and renderer.
- All seven accepted facade capabilities remain the only executable
  intelligence/discovery operations.
- Capability descriptors are caller-filtered by the facade; an unavailable
  engineering descriptor cannot be recovered through `describe`.
- Baseline output has direct `BaselineEngine` parity and preserves `NO_TRADE`
  as a successful process outcome.
- Captured opportunity, A4 projection/evaluation, recorded replay and
  deterministic verification return the exact accepted facade result types.
- `show last` retains object identity; failures do not overwrite it; refresh
  creates new request/run IDs and a parent Shell invocation link.
- JSON includes a losslessly reconstructable canonical facade result. Human,
  reason, gap, contradiction and evidence views are allowlisted projections.
- A4 explanation contains existing thesis/finding/uncertainty/invalidation
  structures and adds no market reasoning.
- Trace is limited to safe lifecycle, logical evidence, policy, usage/cost and
  timing metadata.
- Recorded replay remains offline and is identity-distinct. Verification is
  denied cleanly without the engineering grant.
- Independent sessions do not share context. Defaults are request-local and do
  not grant authority.
- Aware timestamps normalize to Asia/Kolkata; naive/invalid timestamps fail.
- Absolute, traversal and symlink-escaping baseline paths fail before facade
  invocation.
- Provider suffixes/URLs, credential-looking input, shell controls, code
  evaluation/import, subprocess, broker/order and future A5-A7 commands are
  rejected.

## Validation results

The complete offline acceptance run passed:

| Gate | Exact result |
|---|---|
| `pytest -q tests/unit/shell` | 67 passed |
| `pytest -q tests/unit/facade` | 42 passed |
| `pytest -q tests/unit/a4` | 37 passed |
| `pytest -q tests/unit/source_semantics` | 27 passed |
| `pytest -q tests/unit/opportunity_intelligence` | 65 passed |
| `pytest -q tests/unit/a3_hardening` | 61 passed |
| `pytest -q tests/unit/agents` | 270 passed |
| `pytest -q tests/unit/workflows` | 42 passed |
| `pytest -q` | 2,138 passed in 206.17 seconds |
| `python -m compileall src scripts` | passed |
| `ruff check src tests scripts` | all checks passed |
| `mypy src tests` | no issues in 512 source files |
| `python -m pip check` | no broken requirements |
| `git diff --check` | passed |
| local Markdown link audit | 91 files checked; 0 missing local links |
| changed-surface secret scan | 0 credential/private-key/token-pattern matches |
| Shell forbidden-import/execution scan | 0 matches; AST boundary test passed |

`python -m tiaf.shell --help` and `--version` were exercised directly. The
console entry declaration `ti = "tiaf.shell.cli:main"` is covered by the Shell
suite. The already-created project venv predates this entry and does not contain
the Hatchling build backend, so an optional no-network editable-metadata refresh
could not create `.venv/bin/ti`; this is not required for module entry or normal
build-isolated installation and does not affect runtime acceptance.

No live, network, provider, model, tool or broker call occurred. Facade results
used by the accepted cases report zero model calls, zero tool calls and known
zero model usage/cost semantics where applicable.

## Residual limits

- The bootstrap is an operator-owned trusted local document, not a hostile-user
  sandbox or remote authentication boundary.
- Session and history state are intentionally process-local and non-durable.
- Baseline assessment is the sole bounded filesystem-input exception; captured
  operations require configured logical artifact references.
- Human formatting is deliberately compact. Rich citations, bibliography,
  hyperlinks and Web presentation remain under the uncompleted portion of
  DEF-054.
- The implementation exposes no A4.2 live-enrichment trigger and no A5-A7
  commands.

These limits are intentional boundaries, not acceptance blockers.

## Decision

`READY_TO_ACCEPT_TI_SHELL_V0_1`
