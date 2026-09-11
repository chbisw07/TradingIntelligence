# TBD TI Design Notes — Revised Set

These documents are an **idea cache**: unfinished, non-authoritative thinking
preserved so useful ideas are not forgotten. Selected principles can be promoted
without approving an entire note or implementing its proposed product.

Post-A3 pass 1 has now promoted the revised kernel/capability-boundary decisions
into [TIAF_SYSTEM_ARCHITECTURE.md](TIAF_SYSTEM_ARCHITECTURE.md). The
[pass-1 decision record](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_1_CORE_CAPABILITY_BOUNDARY.md)
owns the hypothesis-by-hypothesis disposition. The original TBD files remain
historical proposals, not parallel authoritative specifications.

Pass 2 has separately promoted the revised Core principles from the source note
into [source authority/provenance/contradiction architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md).
Its [section dispositions and prerequisites](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_2_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION.md)
keep citation UX under DEF-054 and do not implement A4 or new source adapters.

Pass 3 approves the [A4 challenge/arbitration architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md).
Its [decision record](TIAF_POST_A3_DEEP_ARCHITECTURE_PASS_3_A4_CHALLENGE_ARBITRATION_AGENTS.md)
selected the now-completed [deployment review](TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md).
The authoritative [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md)
promotes a revised local target and conditional adoption gates, not speculative
Level 3 infrastructure. The [completed consolidation](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md)
now sets foundation -> narrow local facade/lifecycle -> deterministic A4.
Shell/other TBD products and deployment runtime remain unimplemented.
The [A4 major closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) now selects a
small command-first local Shell architecture pass before A5. This plans only
governed facade commands plus minimal captured-source/A4 rendering under
DEF-054; it does not promote NLP, Web, monitoring, forecasting, or deployment
proposals.

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

7. `TBD_TI_DEPLOYMENT_ARCHITECTURE.md`
   - logical boundaries versus hosting/process topology
   - shared evidence, isolated request state, authority and replay
   - revised local target and adoption gates promoted; no deployment implementation
   - all 16 original sections classified in the deployment review; production details remain conditional

## Authority

These notes do not override the accepted repository architecture, contracts, tests, milestone documents, or tagged baselines.

They should be re-opened at the relevant milestone and reconciled with the then-current implementation before becoming authoritative.

## Current post-A3 dispositions

| Note | Current disposition |
|---|---|
| System architecture thesis | SUPERSEDE: system/deployment architecture now governs; preserve rationale, no package relocation. |
| Shell thesis | PLANNED_NEXT: retain mediator and governed boundary. Formalize a command-first local interface over accepted facade capabilities before A5; NLP/mixed remains separately gated. |
| CLI/Web interaction | REVISE_AND_KEEP_TBD: promote only the local command subset with Shell; Web/transport waits for an actual consumer/A8 need, with no exhaustive internals. |
| Source/provenance/citation | SPLIT: Core semantics are implemented; DEF-054 now plans minimal captured-source/A4 rendering with Shell, while rich report/Web UX and adapters remain deferred. |
| Monitoring | REVISE_AND_KEEP_TBD: review bounded mandate/lifecycle/clocks/delta at A5 entry; A8 position binding, A9 intake and A10 durable scheduling remain later. Initial on-demand A5 needs no daemon. |
| Forecasting/ensemble/learning | REVISE_AND_KEEP_TBD: A7 architecture after deterministic A6 seam, with PIT/outcome/benchmark/calibration prerequisites. Algorithms/ensembles/learning remain hypotheses; A7 then informs enhanced A6. |
| Deployment | SPLIT: local Python/state/security/replay design promoted; service/production options conditional at A8/A10 or demonstrated operational need. No runtime rollout. |

The [A3 major closure review](TIAF_A3_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
previously classified all six notes as `REQUIRES_POST_A3_ARCH_CONSOLIDATION`
and found no A3 blocker. The table above records the subsequent bounded
consolidation; it does not retroactively change that closure review.
