# TradingIntelligence

TradingIntelligence is the repository for **TIAF — Trading Intelligence Agent
Fabric**, a planned reusable market-intelligence service. Its long-term role is
to turn scanner, watchlist, manual, and third-party inputs into structured,
attributable intelligence for consumers such as TradeMonitor.

## Current stage

### Past — accepted foundations

A0/TGT0, A1 and A2 are frozen. A3.1-A3.10 are accepted through
`tiaf-a3.10`; A3.8 bounded orchestration is frozen at `tiaf-a3.8` and A3.9
structured opportunity intelligence at `tiaf-a3.9`. See the
[detailed roadmap](docs/TIAF_A3_DETAILED_ROADMAP.md).

### Present — frozen A4 and implemented pre-A5 TI Shell v0.1

[A3.10](docs/TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md)
is accepted with content-addressed cumulative A3 capture, offline replay,
observational A2/A3 comparison, unknown-safe cost accounting, failure
degradation and a 14-case synthetic acceptance corpus. The separate
[A3 major closure review](docs/TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
classifies every active deferral, reconciles live/non-live claims and concludes
`READY_TO_FREEZE_A3` without changing runtime semantics. The major tag
`tiaf-a3-baseline` now exists at `e690da2`. A subsequent
[A3 sub-milestone deferral audit](docs/STUDY_A3_SUBMILESTONE_DEFERRAL_DISCOVERY_AUDIT.md)
reconciles four omitted A3-specific governance records without changing that
freeze decision.

### Pre-A4 source-semantic foundation

The [post-A3 pass-1 review](docs/TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md)
adopts the revised [TI_CORE/capability architecture](docs/TIAF_SYSTEM_ARCHITECTURE.md).
[Pass 2](docs/TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md)
now approves the [source-semantics foundation](docs/TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md).
[Pass 3](docs/TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md)
approves the [A4 challenge/arbitration architecture](docs/TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md):
two bounded roles, deterministic arbitration and optional selective challenge.
The [deployment review](docs/TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md)
now approves the [bounded hosting architecture](docs/TIAF_DEPLOYMENT_ARCHITECTURE.md):
local Python first, isolated request state and filesystem replay; service,
worker and database adoption require concrete operational triggers.
The [completed consolidation](docs/TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md)
selected POST_A3_PRE_A4_FOUNDATION, then a narrow local facade/lifecycle and
deterministic A4. Bounded open-world reasoning permits governed research needs,
not model memory promoted to evidence. A5–A10 retain their major order; A6 gets
deterministic candidates first and forecast-enhanced comparison after A7.
The architecture checkpoint precedes this implementation; no new tag is created
by the foundation work.
The separate [POST_A3_PRE_A4_FOUNDATION](docs/TIAF_POST_A3_PRE_A4_FOUNDATION.md)
now implements the bounded source/proposition/authority/dispute contracts,
deterministic A4 input projection and provider-free replay required before A4.
The subsequent [narrow local facade](docs/TIAF_POST_A3_PRE_A4_LOCAL_FACADE.md)
provides trusted same-process admission/lifecycle and logical-ref captured
replay. [A4.1 deterministic challenge/arbitration](docs/TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md)
now adds immutable thesis/finding/result contracts, eight evidence-linked
challenge families, explicit non-voting arbitration, known-zero model usage and
offline replay/verification. Its additive `a4.evaluate` operation makes seven
static facade capabilities. The internal
[A4.2 governed evidence bridge](docs/TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md)
now admits material semantic needs, delegates one bounded round to A3.8, captures
normalized successor evidence, applies upstream-refresh/no-information stops and
replays the complete chain offline. Its `LIVE_READ` lifecycle is intentionally
not published through the facade. Neither slice adds a remote API, Shell, model,
position, option-expression, forecast or broker authority.
A4.1 and A4.2 are reviewed together in the
[A4 major milestone closure](docs/TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md),
which accepted the deterministic, bounded and replayable A4 layer now frozen at
`tiaf-a4-baseline` (`494d968`).
The optional model-backed Challenger remains deferred. The preferred next slice
is now approved by the
[POST_A4_PRE_A5 Shell review](docs/TIAF_POST_A4_PRE_A5_TI_SHELL_ARCHITECTURE_REVIEW.md),
[authoritative architecture](docs/TIAF_TI_SHELL_ARCHITECTURE.md) and
[implementation record](docs/TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md): the
command-first, same-process mediator now exposes only the seven governed facade
capabilities through `python -m tiaf.shell` and `ti`. NLP, models, live
acquisition, remote transport and intelligence policy remain outside v0.1.
A4 retains arbitration/recommendations; position,
option-expression, forecast and execution authority remain outside A3. TI is
an intelligence and decision-support system, not an execution system.

## Layout

- `src/tiaf/` — application package and future capability namespaces
- `tests/` — unit, integration, and replay test suites
- `docs/` — architecture, principles, thesis, and milestone plan
- `examples/` — future usage examples
- `scripts/` — future development and operational helpers

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
The [A3.7 specialist record](docs/TIAF_A3_7_DERIVATIVES_OPPORTUNITY_RISK.md)
documents the three independent deterministic specialists, implemented A2.7
evidence surface, non-oracle IV/PCR/OI rules, grouped confidence, instrument and
horizon handling, abstention, A2 comparison, ownership exclusions, exact
replay, and truthful live-acquisition status.
Its [user-level acceptance study](docs/STUDY_A3_7_USER_LEVEL_ACCEPTANCE.md)
records six deterministic black-box scenarios through the public runtime,
including conflict, avoid-chase, event-risk, insufficient-evidence, and
cash-only behavior.
The [A4.1 implementation record](docs/TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md)
documents the deterministic no-LLM challenge/arbitration benchmark, and its
[acceptance study](docs/STUDY_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION_ACCEPTANCE.md)
maps the required replay, failure, authority and non-action scenarios.
The [A4.2 implementation record](docs/TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md)
and [acceptance study](docs/STUDY_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE_ACCEPTANCE.md)
cover governed admission, the existing A3.8 workflow bridge, one later
source-semantic successor, selective finding lineage and zero-live replay.
The [A4 major closure review](docs/TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
audits both slices, records the live-validation truth table and deferral
burn-down, and defines the scope of the recommended A4 baseline tag.
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
