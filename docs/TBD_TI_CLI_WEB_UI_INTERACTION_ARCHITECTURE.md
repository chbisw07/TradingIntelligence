# TBD - TI CLI / Web UI / Application Interaction Architecture

> **Status:** TBD / temporary exploratory design note  
> **Authority:** This document is **not yet part of the accepted TI architecture**. It captures an agreed design direction for later formal review.  
> **Promotion rule:** Before becoming authoritative, this note must be revisited at the relevant milestone, reconciled with the then-current repository architecture, tested against implementation realities, and either promoted, revised, split, or rejected.  
> **Repository placement:** Intended for `docs/` with the `TBD_` prefix so it is immediately recognizable as non-final.

---

## 1. Purpose

Capture the agreed user-interaction architecture inspired by the Linux UFW/GUFW pattern.

The core principle is:

> **CLI is the exhaustive/power-user surface. Web UI is a curated human-friendly surface. Both map to the same typed TI command/request/service layer.**

Neither CLI nor Web UI owns intelligence logic.

---

## 2. UFW / GUFW Analogy

Desired user experience:

- CLI offers complete, scriptable control.
- Web UI offers selected workflows that are easier or more useful visually.
- Both invoke the same semantic operation.

The UI is not a second implementation of TI.

---

## 3. Semantic Operations, Not UI Actions

Domain/application concepts should be semantic operations such as:

- `AssessOpportunity`
- `RankCandidates`
- `Forecast`
- `AssessPosition`
- `InspectEvidence`
- `ReplayAssessment`
- `HealthCheck`

A button color, menu item, CLI flag, or URL route is only a presentation/adapter detail.

The domain should never contain concepts such as:

```text
CLICK_ASSESS_BUTTON
```

---

## 4. Preferred Internal Architecture

Do not implement:

```text
Web UI -> run shell command -> parse stdout
```

Preferred:

```text
CLI parser ─────┐
                ├──> typed command/request ───> TI application/service ───> TI core
Web UI ─────────┤
TradeMonitor ───┤
Scanner ────────┤
Automation ─────┘
```

All consumers should converge on the same typed application/service layer.

---

## 5. Headless TI Core

TI core should produce structured intelligence.

It should not know whether the caller was:

- CLI
- browser
- scanner
- TradeMonitor
- another API client

Presentation belongs to adapters/applications.

---

## 6. CLI Philosophy

CLI should remain the broadest and deepest interaction surface.

Potential CLI capabilities:

- full option set
- expert/research flags
- batch operations
- machine-readable JSON
- automation/scripting
- diagnostics
- replay
- evidence inspection
- model/gateway inspection
- health/status
- developer/operator functions

Illustrative future commands:

```bash
ti assess RELIANCE --horizon positional --benchmark NIFTY
ti rank --universe nifty500 --horizon 6m --top 10
ti forecast ATHERENERG --until 2027-03-31 --json
ti replay <assessment-id>
ti inspect-evidence <id>
ti health
```

Exact syntax remains TBD.

---

## 7. Web UI Philosophy

Web UI is likely indispensable for normal human use, but should grow slowly and intentionally.

Likely high-value GUI workflows:

- ranked candidate lists
- single-company intelligence dossier
- evidence drill-down
- specialist opinions
- fundamental/news/forecast summaries
- position intelligence
- option-expression views
- history/comparison
- common configuration
- cost/health/latency views

Do not auto-generate a GUI screen for every CLI switch.

---

## 8. Exhaustive CLI, Selective GUI

Formal working rule:

> **CLI is exhaustive; GUI is selective.**

A capability should move into GUI only when it provides clear value, for example:

- frequently used
- error-prone in CLI
- visually meaningful
- important recurring workflow
- useful for non-technical users
- benefits from comparison/filtering/drill-down/history

Rare, experimental, or diagnostic commands may remain CLI-only indefinitely.

---

## 9. No GUI-Parity Rush

Do not attempt feature parity merely for completeness.

A clean GUI with the right workflows is better than a cluttered GUI exposing every advanced parameter.

The GUI should be driven by user workflows, not by the existence of CLI commands.

---

## 10. Equivalent CLI Representation

Where practical, a GUI workflow may show an equivalent CLI invocation.

Example:

```text
Symbol: RELIANCE
Horizon: POSITIONAL
Benchmark: NIFTY
Timeframes: 1d,1h,15m

Equivalent CLI:
ti assess RELIANCE --horizon positional --benchmark NIFTY --timeframes 1d,1h,15m
```

Benefits:

- reproducibility
- transparency
- debugging
- scripting
- learning
- automation

The displayed CLI is a representation of the typed request, not the internal execution mechanism.

---

## 11. CLI Syntax Is Not the Domain Contract

Typed request/command models should be more stable than CLI syntax.

CLI flags may evolve without forcing changes to Web UI or TI core.

For example:

```text
CLI flags
    ↓
AssessOpportunityRequest
```

The request contract is authoritative; CLI syntax is an adapter.

---

## 12. GUI Workflows May Compose Multiple Operations

Not every GUI screen must map to one CLI command.

A screen may combine:

- load candidate list
- fetch latest assessment
- inspect evidence
- expand specialist opinions
- request deeper analysis

The rule is shared typed service operations, not artificial 1-button=1-command purity.

---

## 13. Structured CLI Output

CLI should support:

- human-readable output
- machine-readable output

Example:

```bash
ti assess RELIANCE
ti assess RELIANCE --json
```

Machine-readable output helps scripts/tests, but Web UI should normally call the service layer directly instead of parsing CLI output.

---

## 14. Long-Running / Asynchronous Operations

Some TI operations may become long-running:

- large-universe ranking
- deep research
- forecast batch
- replay/evaluation
- multi-specialist analysis

Future application/service contracts may need:

- job IDs
- progress/status
- cancellation
- streaming/partial updates
- result retrieval

The GUI should not require the core to become synchronous.

Exact job architecture remains TBD.

---

## 15. Security / Authorization

Once operations are exposed beyond local CLI, authorization becomes first-class.

Future application/service layers may need:

- read-only scope
- research scope
- operator/admin scope
- diagnostic scope

A Web UI must not gain access to every local CLI diagnostic command.

Prompt/user input cannot elevate capabilities.

---

## 16. Web UI Must Not Duplicate Intelligence

Never calculate intelligence in browser code such as:

- RSI
- opportunity score
- HOLD/EXIT
- forecast probability

Instead:

```text
Web UI
    ↓ request
TI service/core
    ↓ structured result
Web UI renders it
```

This preserves one authoritative implementation.

---

## 17. Visualization Boundary

TI returns structured data.

External applications own:

- price/forecast charts
- actual-vs-predicted plots
- dashboards
- timelines
- heatmaps
- tables
- comparative visuals

This keeps TI simpler and reusable.

---

## 18. Error Semantics

All clients should receive the same semantic failure/status model.

For example:

```text
INSUFFICIENT_EVIDENCE
STALE
UNAVAILABLE
BUDGET_EXCEEDED
MODEL_DISABLED
FAILED
```

CLI may print these as text; Web UI may render banners/badges; domain meaning remains identical.

---

## 19. Versioning / Compatibility

Future application commands/API contracts should be versionable.

Clients should not depend on unstable internal implementation details.

Potential concerns:

- request schema version
- result schema version
- CLI backward compatibility
- API compatibility
- deprecated fields
- capability discovery

Exact policy remains TBD.

---

## 20. Configuration Philosophy

Common user-facing settings may appear in Web UI.

Advanced/rare configuration may remain:

- config files
- CLI
- operator/admin tools

Do not force every configuration field into GUI.

---

## 21. Likely Roadmap Placement

Current view:

- preserve this design principle now
- avoid major GUI work during A3/A4
- stabilize intelligence contracts first
- formalize typed application/service boundary around A8
- grow GUI gradually after stable operations exist
- keep CLI evolving as an engineering/operator surface where useful

---

## 22. Open Questions

- exact command taxonomy
- typed application-command layer
- service/API protocol
- authentication/authorization
- Web UI stack
- async job model
- streaming updates
- equivalent-CLI generation
- API/CLI versioning
- multi-user support
- session management
- persistence of user preferences
- browser security model
- local vs remote deployment
- operator-only commands

---

## 23. Working Design Principle

> **Every important GUI capability should correspond to a stable semantic TI command/service operation, but not every CLI command needs a GUI. CLI remains exhaustive and scriptable; Web UI is deliberate and curated. Both are adapters over the same headless TI application/service layer.**
