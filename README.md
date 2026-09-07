# TradingIntelligence

TradingIntelligence is the repository for **TIAF — Trading Intelligence Agent
Fabric**, a planned reusable market-intelligence service. Its long-term role is
to turn scanner, watchlist, manual, and third-party inputs into structured,
attributable intelligence for consumers such as TradeMonitor.

## Current stage

The **TIAF_TGT0** and **TIAF_A0** baselines are frozen. **TIAF_A1.1** through
**TIAF_A1.7** form the complete, live-validated A1 Data Foundation at tag
`tiaf-a1.7`. A2.1 through A2.7 are complete and live-validated. The current
**TIAF_A2.8** target adds deterministic explicit-benchmark relative strength
and first-class multi-timeframe factual context.

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
[implementation roadmap](docs/TRADINGINTELLIGENCE_ROADMAP.md). The
[capability map](docs/TIAF_CAPABILITY_MAP.md) shows where implemented and future
platform capabilities belong.

Intentional future work and architectural non-goals are tracked under stable
IDs in the [deferral register](docs/TIAF_DEFERRAL_REGISTER.md). Deferrals are
reviewed collectively at major milestone closures rather than interrupting
each sub-milestone.

The current A2.8 formulas, alignment rules, denominator semantics, live
observations, and explicit deferrals are recorded in the
[A2.8 technical note](docs/TIAF_A2_8_RELATIVE_STRENGTH_MTF.md).

For a read-only A2.7 option-chain feature smoke, first obtain an active expiry
with `scripts/dhan_option_chain_smoke.py`, then run:

```bash
python scripts/feature_engine_smoke.py \
  --symbol RELIANCE \
  --purpose OPTION_EXPRESSION \
  --include-derivatives \
  --expiry YYYY-MM-DD \
  --derivatives
```

The expiry is explicit, the feature calculations use the chain snapshot's own
underlying LTP, and the command never places trades.

For an explicit-benchmark A2.8 comparison, pass both identities and the
caller-declared benchmark role:

```bash
python scripts/relative_strength_smoke.py \
  --symbol RELIANCE \
  --benchmark NIFTY \
  --benchmark-type INDEX \
  --benchmark-role MARKET \
  --history-interval 1d \
  --lookback-days 180
```

For ordered multi-timeframe evidence from separate provider histories:

```bash
python scripts/multi_timeframe_smoke.py \
  --symbol RELIANCE \
  --timeframes 1d,1h,15m \
  --lookback-days 180
```

Dhan intraday retrieval has an accepted 90-day single-request limit. The
multi-timeframe smoke reports its effective per-interval lookbacks and does not
resample or fabricate bars. Both commands are read-only factual diagnostics;
they do not select benchmarks, score candidates, or make recommendations.
