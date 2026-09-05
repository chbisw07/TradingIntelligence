# TradingIntelligence

TradingIntelligence is the repository for **TIAF — Trading Intelligence Agent
Fabric**, a planned reusable market-intelligence service. Its long-term role is
to turn scanner, watchlist, manual, and third-party inputs into structured,
attributable intelligence for consumers such as TradeMonitor.

## Current stage

The **TIAF_TGT0**, **TIAF_A0**, and **TIAF_A1.1** baselines are frozen, and
**TIAF_A1.2** and **TIAF_A1.3** are accepted/live-validated. Development is now
at **TIAF_A1.4**, which adds provider-neutral rolling historical/expired-option
data to the read-only DhanHQ v2 adapter.

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

See [the implementation roadmap](docs/IMPLEMENTATION_ROADMAP.md) for the
planned sequence.
