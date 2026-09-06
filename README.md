# TradingIntelligence

TradingIntelligence is the repository for **TIAF — Trading Intelligence Agent
Fabric**, a planned reusable market-intelligence service. Its long-term role is
to turn scanner, watchlist, manual, and third-party inputs into structured,
attributable intelligence for consumers such as TradeMonitor.

## Current stage

The **TIAF_TGT0** and **TIAF_A0** baselines are frozen. **TIAF_A1.1** through
**TIAF_A1.7** form the complete, live-validated A1 Data Foundation at tag
`tiaf-a1.7`. The next target is **TIAF_A2**, which consumes factual
`AnalysisContext` values to build deterministic derived features.

It is **not** a trading system at this stage. It has no trading logic, agents,
workflows, scanners, broker execution/account integration, LLM calls, or
TradeMonitor integration. Nothing in this repository currently produces or
acts on market recommendations.

## Layout

- `src/tiaf/` — application package and future capability namespaces
- `tests/` — unit, integration, and replay test suites
- `docs/` — architecture, principles, thesis, and milestone plan
- `examples/` — future usage examples
- `scripts/` — future development and operational helpers

## Installation

Python 3.12 or newer is required. From a virtual environment:

```bash
python -m pip install -e '.[dev]'
```

For runtime dependencies only, use `python -m pip install -e .`.

The current India deployment defaults symbol-only cash resolution and F&O
universe generation to NSE. Override these non-secret settings when needed:

```bash
TIAF_PRIMARY_EXCHANGE=NSE
TIAF_PRIMARY_FNO_EXCHANGE=NSE
```

## Verification

```bash
python -m compileall src
pytest
ruff check src tests
mypy src tests
```

## Milestone philosophy

Capabilities are introduced only when their contracts, boundaries, and tests
are ready. Each milestone should produce a small, independently verifiable
increment. Deterministic computation stays deterministic; judgment-oriented AI
capabilities will be introduced deliberately and remain subordinate to the
centralized authority and risk controls of TradeMonitor.

See the [A1 foundation baseline](docs/TIAF_A1_FOUNDATION_BASELINE.md),
[A1 acceptance report](docs/TIAF_A1_ACCEPTANCE_REPORT.md), and
[implementation roadmap](docs/IMPLEMENTATION_ROADMAP.md).
