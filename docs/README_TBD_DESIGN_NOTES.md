# TBD TI Design Notes — Revised Set

These documents are temporary design notes for the TradingIntelligence project.

They are intentionally prefixed with `TBD_` so they remain visibly non-authoritative until the relevant milestone revisits and promotes, revises, splits, or rejects them.

## Documents

1. `TBD_TI_MONITORING_ARCHITECTURE.md`
   - Semantic lifecycle states instead of color-named domain states
   - Instrument vs WatchMandate
   - Independent cadence/evidence clocks
   - Scheduled + event-driven monitoring
   - Incremental/delta-aware recalculation
   - Shared evidence and deduplication
   - Priority, adaptive cadence, budget-aware scheduling
   - TradeMonitor authority boundary

2. `TBD_TI_FORECASTING_ENSEMBLE_LEARNING_ARCHITECTURE.md`
   - Forecast task/method/regime/ensemble separation
   - Config-driven pluggable forecasting methods
   - Hierarchical/funnel ensembles
   - Reality-based scorecards and calibration
   - Champion/challenger lifecycle
   - Point-in-time validation discipline
   - Batch and cross-sectional forecasting
   - Headless structured output
   - Feedback learning with controlled promotion

3. `TBD_TI_CLI_WEB_UI_INTERACTION_ARCHITECTURE.md`
   - UFW/GUFW-inspired design
   - Semantic typed commands/requests
   - Exhaustive CLI, selective Web UI
   - No GUI parity rush
   - Equivalent CLI representation
   - Shared service/application layer
   - Async/long-running operation preparation
   - Common semantic error/version/auth models
   - Headless TI core and external visualization

## Authority

These notes do not override the accepted repository architecture, contracts, tests, milestone documents, or tagged baselines.

They should be re-opened at the relevant milestone and reconciled with the then-current implementation before becoming authoritative.
