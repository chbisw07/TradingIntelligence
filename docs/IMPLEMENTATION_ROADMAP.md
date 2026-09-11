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
approved. A5.1 is the next bounded implementation: immutable additive contracts,
deterministic single-open-position advice, monitoring intent and captured replay.
It does not include live TM/broker integration, multi-leg interpretation,
scheduling, A6/A7 or Shell exposure.

## Acceptance philosophy

Every milestone should have explicit contracts, representative tests, and
observable acceptance criteria. Outputs must identify their timestamp,
provenance, horizon, and responsible component when those concepts become
applicable. A milestone is accepted for demonstrated behavior, not for the
presence of placeholders. External integrations must preserve the boundary
between pluggable intelligence and centralized authority.
