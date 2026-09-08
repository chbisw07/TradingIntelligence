# TIAF A3 Entry Conditions

## Purpose

This handoff binds the future Planner and specialist Agent layer to the accepted
TIAF_A2 deterministic foundation. The design is now authoritative in
[`TIAF_A3_ARCHITECTURE.md`](TIAF_A3_ARCHITECTURE.md), and the sequential freeze
plan is in [`TIAF_A3_DETAILED_ROADMAP.md`](TIAF_A3_DETAILED_ROADMAP.md). No A3
runtime is implemented.

## Required inherited substrate

A3 inherits and must reuse:

- immutable provider-neutral A1 `AnalysisContext` and normalized factual data;
- A2 feature, indicator, explicit-benchmark, and ordered MTF contracts;
- A2.9 policy 1.0 assessments, component evidence, candidate classes, ranking,
  and valid `NO_TRADE` behavior;
- A2.10 content-addressed evidence snapshots, immutable run records, exact
  replay, policy comparison, regression, and later factual outcome separation;
- canonical aware `Asia/Kolkata` timestamps and explicit acquisition,
  observation, decision, replay, and outcome time roles;
- `GOOD`, `PARTIAL`, `DEGRADED`, `UNAVAILABLE` quality and
  `FRESH`, `AGING`, `STALE`, `UNKNOWN` freshness semantics;
- symbol/provider/context/bundle/assessment/snapshot/fingerprint provenance;
- zero broker authority and the external TradeMonitor governance boundary.

## Agent obligations

1. Agents consume shared A2 evidence; they do not independently call broker or
   market-data APIs or recreate factual calculations with drifting semantics.
2. Agent output remains a separate attributable interpretation. It cannot
   mutate A2 evidence, baseline assessments, replay records, or later outcomes.
3. Every factual claim identifies supporting evidence and retains quality,
   freshness, source, observation time, and missingness.
4. Disagreement and conflict remain visible. Arbitration may not erase dissent
   merely to produce a fluent conclusion.
5. `WAIT`, insufficient evidence, and `NO_TRADE` remain valid. A3 must not force
   CE/PE or directional conclusions.
6. Agent performance is evaluated against the frozen deterministic baseline on
   the same evidence. A3 does not overwrite or silently tune A2.9 policy 1.0.
7. Replayable Agent decisions must be captured before outcomes. Later outcome
   facts never enter decision-time evidence.
8. Agents have no authority to place, modify, or cancel broker orders.
   TradeMonitor remains the future governor for risk, lifecycle, and execution.

## Entry checks

Before A3 implementation begins:

- start from a clean worktree whose HEAD resolves to the accepted
  `tiaf-a2-baseline` tag;
- identify which high-priority A3-closure deferrals are required by the first
  concrete Agent consumer rather than implementing all of them speculatively;
- define stable Agent input/output, attribution, prompt/model identity, failure,
  cost/latency, and replay contracts without changing accepted A2 semantics;
- retain architecture tests that prevent provider, broker, and execution
  leakage into Agent reasoning.

## Explicit non-entry work

A3 entry does not authorize option strategy selection (A6), position
intelligence (A5), TradeMonitor integration (A8), production schedulers (A10),
statistical policy optimization (future evaluation), or broker execution
(rejected from TIAF scope).

## Entry decision

The architecture entry gate is satisfied at
`e27674070537a7d81e6e117283913d7da2785d1c` (`tiaf-a2-baseline`). A3 is
**architecture defined / ready for implementation**, and **A3.1 is next**.
A3.1 is limited to immutable provider-neutral contracts, enums, failures,
consumer-facing forecast evidence, and `SpecialistAgent`/`ReasoningProvider`
protocols with local fakes and contract tests. It does not authorize evidence
gateways, external model calls, specialist reasoning, or orchestration.
