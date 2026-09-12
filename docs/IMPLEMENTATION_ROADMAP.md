# Implementation Roadmap

TIAF evolves through small, gated increments. `TIAF_TGT0` establishes the
engineering baseline. `TIAF_A0` and `TIAF_A1` then define contracts and trusted
data before `TIAF_A2` supplies a deterministic reference implementation.

Interpretive capability arrives in `TIAF_A3`, followed by arbitration in
`TIAF_A4`. Position management and option expression are introduced separately
in `TIAF_A5` and `TIAF_A6`. Evaluation becomes a dedicated capability in
`TIAF_A7` before external integration with TradeMonitor (`TIAF_A8`) and scanners
(`TIAF_A9`). `TIAF_A10` completes production hardening.

After the frozen A4 baseline, the approved
[command-first TI_SHELL architecture](TIAF_TI_SHELL_ARCHITECTURE.md) is now
delivered by a
[small unnumbered local engineering interface](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md)
before A5. It is useful but not an A5 prerequisite and adds no NLP, Web, model,
live-acquisition or broker authority.

The [A5 architecture](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md) is now
implemented by the bounded
[A5.1 baseline](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md): immutable
additive contracts, deterministic single-open-position advice, monitoring intent
and captured replay. The additive
[A5.2 publication slice](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md) exposes it
through position-scoped logical-artifact admission and the bounded Shell. It
still does not include live TM/broker integration, multi-leg interpretation,
scheduling, A6/A7 or remote transport.
The [A5 major closure review](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md) reviews
both slices together and concludes `READY_TO_FREEZE_A5`; it recommends but does
not create `tiaf-a5-baseline`. The subsequent
[TI Pluggability Architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md) is complete
as architecture only. The [completed compliance audit](TIAF_PLUGGABILITY_A1_A5_COMPLIANCE_AUDIT.md)
found one pre-freeze issue: registry absence silently shrank required specialist
coverage. The bounded [R1 remediation](TIAF_PLUGGABILITY_R1_REQUIRED_SCOPE_EXPLICIT_ABSENCE.md)
now preserves stable declared scope, explicit absence, and old/new capture
compatibility. The subsequent
[acceptance closure](TIAF_PLUGGABILITY_R1_ACCEPTANCE_AND_A5_FREEZE_READINESS.md)
closes R1 and finds A5 ready for final documentation and freeze. The
[post-R1 consolidation](TIAF_POST_R1_DOCUMENTATION_CONSOLIDATION_AND_SYNCHRONIZATION.md)
now completes documentation synchronization. A5 remains untagged pending the
final freeze/tag-readiness check. No
A5 policy changed. R2–R5 remain separately bounded pre-A6 work and are not A5
freeze requirements. A6 has not begun; this workstream does not renumber
milestones or implement a plugin framework.

The post-R1 [Monitoring Architecture](TIAF_MONITORING_ARCHITECTURE.md) reconciles
future subscriber-driven mandates without changing accepted A5 intent or
implementing a runtime. A8 retains TM integration, A9 scanner/candidate intake,
and A10 durable monitoring operationalization. A separately approved minimum
runtime slice may accompany earlier integration only with its admission/replay/
budget/recovery gates; it is not automatically next. Detailed milestone coverage
is now available for [A4](TIAF_A4_DETAILED_ROADMAP.md) and
[A5](TIAF_A5_DETAILED_ROADMAP.md). No runtime or R2–R5 work is added.

## Current forward sequence

1. `TIAF_A5 — FINAL FREEZE / TAG READINESS CHECK`; then A5 freeze/tag only under
   separate explicit authorization against the reviewed candidate tree.
2. Bounded R2–R5 pluggability hardening before A6: descriptors/dependencies,
   additive composition/pinned verification, optional import isolation and trusted
   COLD ownership. These remain SHOULD_FIX_BEFORE_A6, not A5 freeze requirements.
3. A6 architecture/implementation: deterministic valid expressions first.
4. A7 forecasting/evaluation overlay; calibrated inputs may then support a
   separately versioned forecast-enhanced A6 follow-up.
5. A8 TM integration, A9 scanner/candidate intake, A10 monitoring operationalization
   and production hardening; preserve admission, authority and delivery gates.

**Adjacent workstream ordering remains explicit TBD:** Sector Rotation needs its
own architecture/acceptance after the relevant deterministic/PIT/evaluation seams;
Signal Qualification is intended after Sector Rotation review unless explicitly
reordered. Placement relative to A7/A8 is not yet authoritative. Do not promote
the exploratory A7.0/A7.x/SR labels or silently insert an implementation into the
numbered sequence. Neither workstream is an A5 freeze blocker or callable now.

## Acceptance philosophy

Every milestone should have explicit contracts, representative tests, and
observable acceptance criteria. Outputs must identify their timestamp,
provenance, horizon, and responsible component when those concepts become
applicable. A milestone is accepted for demonstrated behavior, not for the
presence of placeholders. External integrations must preserve the boundary
between pluggable intelligence and centralized authority.
