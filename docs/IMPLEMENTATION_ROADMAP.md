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
not create `tiaf-a5-baseline`. The next bounded work is the A6 Option Expression
Intelligence architecture pass.

## Acceptance philosophy

Every milestone should have explicit contracts, representative tests, and
observable acceptance criteria. Outputs must identify their timestamp,
provenance, horizon, and responsible component when those concepts become
applicable. A milestone is accepted for demonstrated behavior, not for the
presence of placeholders. External integrations must preserve the boundary
between pluggable intelligence and centralized authority.
