# TBD TI Design Notes — Revised Set

These documents are temporary design notes for the TradingIntelligence project.

Post-A3 pass 1 has now promoted the revised kernel/capability-boundary decisions
into [TIAF_SYSTEM_ARCHITECTURE.md](TIAF_SYSTEM_ARCHITECTURE.md). The
[pass-1 decision record](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md)
owns the hypothesis-by-hypothesis disposition. The original TBD files remain
historical proposals, not parallel authoritative specifications.

Pass 2 has separately promoted the revised Core principles from the source note
into [source authority/provenance/contradiction architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md).
Its [section dispositions and prerequisites](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md)
keep citation UX under DEF-054 and do not implement A4 or new source adapters.

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

## Current post-A3 dispositions

| Note | Current disposition |
|---|---|
| System architecture thesis | Kernel and curated boundary promoted **with revisions** in the authoritative system document; no package relocation or implementation claim. |
| Shell thesis | Mediator placement and boundary-before-v0.1 prerequisite adopted; command list, NLP/model modes and implementation timing remain hypotheses. |
| CLI/Web interaction | Shared semantic boundary and independent consumers adopted; “exhaustive CLI” does not permit exhaustive internal access. UX/transport details remain deferred. |
| Source/provenance/citation | Pass 2 promotes revised Core semantics and rejects a global source hierarchy. All 28 sections are classified in its review; citation UX remains DEF-054. Next is pass 3 A4 architecture, with bounded semantic-projection implementation required before A4 runtime. |
| Monitoring | Shared-evidence/state-isolation and TM authority preserved; mandate/scheduler implementation remains deferred. |
| Forecasting/ensemble/learning | A7 placement and confidence/calibration distinction preserved; algorithms, model registry and learning implementation remain hypotheses. |

The [A3 major closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
previously classified all six notes as `REQUIRES_POST_A3_ARCH_CONSOLIDATION`
and found no A3 blocker. The table above records the subsequent bounded
consolidation; it does not retroactively change that closure review.
