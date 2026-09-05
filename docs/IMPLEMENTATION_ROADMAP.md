# Implementation Roadmap

TIAF evolves through small, gated increments. `TIAF_TGT0` establishes the
engineering baseline. `TIAF_A0` and `TIAF_A1` then define contracts and trusted
data before `TIAF_A2` supplies a deterministic reference implementation.

Interpretive capability arrives in `TIAF_A3`, followed by arbitration in
`TIAF_A4`. Position management and option expression are introduced separately
in `TIAF_A5` and `TIAF_A6`. Evaluation becomes a dedicated capability in
`TIAF_A7` before external integration with TradeMonitor (`TIAF_A8`) and scanners
(`TIAF_A9`). `TIAF_A10` completes production hardening.

## Acceptance philosophy

Every milestone should have explicit contracts, representative tests, and
observable acceptance criteria. Outputs must identify their timestamp,
provenance, horizon, and responsible component when those concepts become
applicable. A milestone is accepted for demonstrated behavior, not for the
presence of placeholders. External integrations must preserve the boundary
between pluggable intelligence and centralized authority.
