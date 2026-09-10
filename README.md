# TradingIntelligence

TradingIntelligence is the repository for **TIAF — Trading Intelligence Agent
Fabric**, a planned reusable market-intelligence service. Its long-term role is
to turn scanner, watchlist, manual, and third-party inputs into structured,
attributable intelligence for consumers such as TradeMonitor.

## Current stage

The **TIAF_TGT0** and **TIAF_A0** baselines are frozen. **TIAF_A1.1** through
**TIAF_A1.7** form the complete, live-validated A1 Data Foundation at tag
`tiaf-a1.7`. **TIAF_A2.1** through **TIAF_A2.10** form the complete,
live-validated deterministic A2 platform, frozen at `tiaf-a2-baseline`.
**TIAF_A3 Specialist Intelligence architecture is accepted at `tiaf-a3-arch`.
A3.1 contracts and the bounded single-specialist runtime are accepted at
`tiaf-a3.1`. A3.2 controlled evidence/reasoning/budget gateways are accepted at
`tiaf-a3.2`. A3.3 Technical / Market-Structure Specialist is complete and
accepted at `tiaf-a3.3`. A3.4 Fundamental / Company-Quality Intelligence is
accepted at `tiaf-a3.4`. A3.5 News / Catalyst / Event Intelligence is accepted
at `tiaf-a3.5`. A3.6 Relative / Sector / Macro Context Intelligence is accepted
at `tiaf-a3.6`. The A3.6.1 Market Intelligence Provider Fabric and Deep Research
Foundation is frozen at `tiaf-a3.6.1`. Its post-freeze Yahoo/yfinance MCP
follow-up adds a bounded secondary/fallback provider for profile, financial,
earnings, and news evidence without changing specialist or canonical contracts.
The corrected Yahoo ten-call live-acceptance matrix and exact offline replay
passed on 2026-09-10. A bounded authoritative-confirmation gateway for NSE,
BSE, and company IR primary sources is implemented and bounded-live-validated
as a post-A3.6.1 follow-up. A3.6.2 now integrates these sources into bounded,
graph-aware deterministic company research with explicit gaps, epistemic
separation, zero-LLM operation, and exact offline replay. Its four-symbol,
12-call live matrix passed on 2026-09-10. A3.7 remains next.**

It is **not** a trading system. A2.9 emits replayable benchmark judgments and
may validly return `NO_TRADE`, but it has no final recommendation Agent,
strategy selection, broker execution/account integration, LLM calls, or
TradeMonitor integration and cannot act on its output.

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

The complete deterministic platform and closure evidence are recorded in the
[A2 foundation baseline](docs/TIAF_A2_FOUNDATION_BASELINE.md) and
[A2 acceptance report](docs/TIAF_A2_ACCEPTANCE_REPORT.md). The
[A3 entry conditions](docs/TIAF_A3_ENTRY_CONDITIONS.md) bind future Agents to
the frozen A2 evidence and replay benchmark. The authoritative
[A3 architecture](docs/TIAF_A3_ARCHITECTURE.md) and
[detailed A3 roadmap](docs/TIAF_A3_DETAILED_ROADMAP.md) define the specialist,
evidence, budget, failure, and milestone boundaries. The
[A3.1 technical record](docs/TIAF_A3_1_AGENT_FOUNDATION.md) documents the
accepted provider-neutral contract and runtime foundation. The
[A3.2 gateway and budget record](docs/TIAF_A3_2_GATEWAYS_BUDGETS.md) documents
least-privilege evidence access, A2 reuse, optional model tiers, no-LLM mode,
budget enforcement, structured-output validation, and audit records.
The [A3.3 technical specialist record](docs/TIAF_A3_3_TECHNICAL_SPECIALIST.md)
documents its immutable A2 fact projections, deterministic interpretation
policy, cited claims, zero-LLM behavior, and live-validation status. The
[A3.4 fundamental intelligence record](docs/TIAF_A3_4_FUNDAMENTAL_INTELLIGENCE.md)
documents point-in-time company facts, period-safe metrics, the controlled
fundamental gateway, cited company-quality interpretation, and source limits.
The [A3.5 news/event intelligence record](docs/TIAF_A3_5_NEWS_EVENT_INTELLIGENCE.md)
documents event identity and information time, revisions, conservative
clustering, controlled news/filing reads, cited catalyst interpretation,
zero-LLM behavior, and production-source limits.
The [A3.6 contextual intelligence record](docs/TIAF_A3_6_RELATIVE_SECTOR_MACRO_INTELLIGENCE.md)
documents the three-specialist separation, explicit benchmark/sector/sensitivity
mappings, controlled sector/macro reads, shared context reuse, deterministic
cited interpretation, point-in-time rules, and production-source limits.
The [A3.6.1 provider-fabric record](docs/TIAF_A3_6_1_MARKET_INTELLIGENCE_PROVIDER_FABRIC.md)
documents the implemented per-capability provider declarations/routing,
progressive evidence enrichment, native-semantic normalization, contradiction
preservation, sparse research memory, and structured deep-research boundaries.
The [authoritative-confirmation gateway architecture](docs/TIAF_AUTHORITATIVE_CONFIRMATION_GATEWAY.md)
defines selective material-claim confirmation, official-source document and
revision evidence, conservative extraction, and claim-to-confirmation lineage
without exposing exchange transports to specialists. Its
[bounded live acceptance](docs/STUDY_Authoritative_Confirmation_Gateway_Live_Acceptance.md)
acquired and replayed official NSE/BSE evidence while preserving a typed
not-found company-IR result.
The [A3.6.2 integration record](docs/TIAF_A3_6_2_MARKET_INTELLIGENCE_DEEP_RESEARCH_INTEGRATION.md)
documents multi-capability planning, progressive enrichment, authoritative
linkage, sparse evidence-graph updates, deterministic research outputs,
epistemic enforcement, and provider-free replay. Its
[bounded live study](docs/STUDY_A3_6_2_Deep_Research_Live_Acceptance.md) covers
RELIANCE, HDFCBANK, KAYNES, and ATHERENERG without adding a provider or model
call.
The associated
[Tapetide forensic study](docs/STUDY_Tapetide_Forensic_Validation_Report_Phase1.md)
is non-authoritative evidence informing that design.

Intentional future work and architectural non-goals are tracked under stable
IDs in the [deferral register](docs/TIAF_DEFERRAL_REGISTER.md). Deferrals are
reviewed collectively at major milestone closures rather than interrupting
each sub-milestone.

The A2.8 formulas, alignment rules, denominator semantics, live
observations, and explicit deferrals are recorded in the
[A2.8 technical note](docs/TIAF_A2_8_RELATIVE_STRENGTH_MTF.md).

The A2.9 policies, exact transforms, quality gates, candidate classes, ranking
tie rules, live record, and non-AI benchmark role are documented in the
[A2.9 technical note](docs/TIAF_A2_9_DETERMINISTIC_BASELINE.md).

The snapshot fingerprint, offline replay, outcome separation, MFE/MAE,
append-only corpus, regression, and anti-lookahead rules are documented in the
[A2.10 technical note](docs/TIAF_A2_10_REPLAY_VALIDATION_EVALUATION.md).

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

For the separate read-only A2.9 synthesis smoke:

```bash
python scripts/baseline_opportunity_smoke.py \
  --symbols RELIANCE,HDFCBANK,KAYNES \
  --horizon POSITIONAL \
  --benchmark NIFTY \
  --benchmark-map HDFCBANK=BANKNIFTY \
  --timeframes 1d,1h,15m \
  --rank
```

The benchmark and any override mapping are explicit caller inputs. Ranking
never fills requested slots with `NO_TRADE` candidates.

Capture normalized evidence once, then replay it without network access:

```bash
python scripts/capture_baseline_snapshot.py \
  --symbol RELIANCE --horizon POSITIONAL --benchmark NIFTY \
  --timeframes 1d,1h,15m --output /tmp/reliance_snapshot.json
python scripts/replay_baseline_snapshot.py \
  --input /tmp/reliance_snapshot.json
```
