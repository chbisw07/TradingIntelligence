# Implementation Roadmap

This is the **near-term forward queue**, subordinate to the intended major order
in the [development roadmap](TRADINGINTELLIGENCE_ROADMAP.md). The
[milestone ledger](MILESTONES.md) owns actual status/tags and the
[README](../README.md) is the executive dashboard. Status: 2026-09-13
(Asia/Kolkata); historical reviews retain their original then-next decisions.

```text
A5: FROZEN (`tiaf-a5-baseline`)
  → R2 (ACCEPTED / DONE)
  → R3 (ACCEPTED / DONE) → R4 (ACCEPTED / DONE)
  → R5 (ACCEPTED / DONE — BEFORE_A6)
  → A6 (ARCHITECTURE ACCEPTED / THESIS ACCEPTED)
  → A6.1 CONTRACTS / ADMISSION / POLICY ACCEPTED / DONE
  → A6.2 EVALUATION / RANKING / REPLAY ACCEPTED / DONE
  → A6.3 FACADE / SHELL ACTIVE / NEXT → A6.4 NOT_IMPLEMENTED → A7 → A8 → A9 → A10
```

R1 is ACCEPTED. [R2 Discovery Metadata](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA.md)
is [accepted](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA_ACCEPTANCE.md). R1–R5 form the
**cross-cutting pluggability remediation / hardening track**, not A5.x. R2–R5
do not block A5 freeze. See the
[R-series ledger](MILESTONES.md#cross-cutting-pluggability-remediation-track-r1r5)
for scope and evidence. This queue is intended execution order, not a claim of
new technical dependencies between all R items.

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
now completes documentation synchronization. The subsequent
[final readiness check](TIAF_A5_FINAL_FREEZE_TAG_READINESS_CHECK.md) returned
`READY_TO_TAG_A5`; documentation commit `167c51d` and annotated tag
`tiaf-a5-baseline` were then pushed. A5 is FROZEN. No
A5 policy changed. R2–R5 are separately bounded pre-A6 work and are not A5
freeze requirements. A6.2 is internal only; this workstream does not renumber
milestones or implement a plugin framework. R4 is now
[implemented](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION.md) and
[accepted](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION_ACCEPTANCE.md);
R5 is [implemented](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md) and
[accepted](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION_ACCEPTANCE.md).
The R1–R5 hardening track is closed. The
[A6 architecture](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md)
and [reconciliation record](TIAF_A6_RECONCILIATION_RECORD.md) are independently
[accepted](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md);
A6.1 is [accepted and done](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION_ACCEPTANCE.md).
A6.2 is [accepted and done](TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY_ACCEPTANCE.md),
A6.3 is ACTIVE / NEXT, A6.4 is NOT_IMPLEMENTED and `expression.assess` remains
NOT_PUBLISHED.
The [thesis creation record](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_THESIS_RECORD.md)
preserves history; the [fourteen-finding reconciliation](TIAF_A6_THESIS_ARCHITECTURE_RECONCILIATION.md)
now updates the normative draft. Thesis artifacts remain unchanged.

The post-R1 [Monitoring Architecture](TIAF_MONITORING_ARCHITECTURE.md) reconciles
future subscriber-driven mandates without changing accepted A5 intent or
implementing a runtime. A8 retains TM integration, A9 scanner/candidate intake,
and A10 durable monitoring operationalization. A separately approved minimum
runtime slice may accompany earlier integration only with its admission/replay/
budget/recovery gates; it is not automatically next. Detailed milestone coverage
is now available for [A4](TIAF_A4_DETAILED_ROADMAP.md) and
[A5](TIAF_A5_DETAILED_ROADMAP.md). No runtime or R2–R5 work is added.

## Current forward sequence

1. **TIAF A6.3 — FACADE & TI_SHELL EXPOSURE**.
2. Then A6.4 hardening/acceptance; A7; A8; A9; A10,
   as proposed in the [A6 roadmap](TIAF_A6_DETAILED_ROADMAP.md).

Initial A6 is long single-leg CE/PE only, non-executable, with explicit absence.
SigmaDSL is not an A6 dependency. The current gate is
A6.2 acceptance covers only the internal deterministic evaluator; A6.3 must
separately govern publication and does not freeze A6 as a whole.

R2–R5 are bounded pluggability hardening before A6: descriptors/dependencies,
additive composition/pinned verification, optional import isolation and trusted
COLD ownership. These remain SHOULD_FIX_BEFORE_A6, not A5 freeze requirements.
After initial A6, A7 forecasting/evaluation may supply calibrated inputs for a
separately versioned forecast-enhanced A6 follow-up.
A8 TM integration, A9 scanner/candidate intake, A10 monitoring operationalization
and production hardening retain their admission, authority and delivery gates.

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
