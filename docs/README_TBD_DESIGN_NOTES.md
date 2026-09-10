# TBD TI Design Notes — Revised Set

These documents are temporary design notes for the TradingIntelligence project.

They are intentionally prefixed with `TBD_` so they remain visibly non-authoritative until the relevant milestone revisits and promotes, revises, splits, or rejects them.

## Documents

1. `TBD_TI_SYSTEM_ARCHITECTURE_THESIS.md`
   - TI_CORE as an intelligence kernel
   - curated, typed, versioned public capability boundary
   - replaceable application, model, provider, and integration adapters
   - logical modularity without premature microservices

2. `TBD_TI_SHELL_THESIS.md`
   - stateful engineering mediator over typed TI capabilities
   - native deterministic commands plus explicitly gated NLP
   - no shell-out-as-domain-API and no intelligence ownership

3. `TBD_TI_SOURCE_PROVENANCE_CITATION_FABRIC.md`
   - material claim-to-evidence/source traceability
   - source authority, contradiction and citation presentation
   - point-in-time replay and provider-neutral source governance

4. `TBD_TI_MONITORING_ARCHITECTURE.md`
   - Semantic lifecycle states instead of color-named domain states
   - Instrument vs WatchMandate
   - Independent cadence/evidence clocks
   - Scheduled + event-driven monitoring
   - Incremental/delta-aware recalculation
   - Shared evidence and deduplication
   - Priority, adaptive cadence, budget-aware scheduling
   - TradeMonitor authority boundary

5. `TBD_TI_FORECASTING_ENSEMBLE_LEARNING_ARCHITECTURE.md`
   - Forecast task/method/regime/ensemble separation
   - Config-driven pluggable forecasting methods
   - Hierarchical/funnel ensembles
   - Reality-based scorecards and calibration
   - Champion/challenger lifecycle
   - Point-in-time validation discipline
   - Batch and cross-sectional forecasting
   - Headless structured output
   - Feedback learning with controlled promotion

6. `TBD_TI_CLI_WEB_UI_INTERACTION_ARCHITECTURE.md`
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

The [A3 major closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
classifies all six notes as `REQUIRES_POST_A3_ARCH_CONSOLIDATION` and finds no
A3 blocker. That classification is a review disposition, not promotion of any
note to authoritative architecture.
