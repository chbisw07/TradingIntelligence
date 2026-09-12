# Study: A5.1 Deterministic Single-Position Baseline Acceptance

## Status

**Acceptance run: 2026-09-12 (Asia/Kolkata).** The implementation under test is
documented in
[TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md).

**Decision: `READY_TO_ACCEPT_A5_1`.**

No live broker, provider, model, TM, scheduler or remote-service call is required
or permitted. All cases are synthetic/captured and replayable.

## Acceptance coverage

The focused suite covers:

- fresh equity, future and single-option positions;
- strict signed quantity, instrument, expiry, subject and timestamp identity;
- stale, unknown, age-expired and future snapshots;
- missing A4 and unsupported multi-leg shape;
- all four postures and five thesis-health states reached by applicable inputs;
- milestone/protection, continuation/trailing, weakening, invalidation,
  conflict, adverse A4 and remaining-room policy;
- expired/near-expiry derivatives and supplied intraday exit windows;
- cited non-executable levels and expression-refresh-only A6 seam;
- active/inactive mandates, monitoring needs and successor mandate lineage;
- stable deterministic fingerprints and previous-result lineage;
- exact captured replay, deterministic verification and policy comparison;
- corrupt snapshot/run/A4/exact checksums;
- no provider/model/broker-SDK/A6/A7/remote imports;
- no credential, executable order, probability or mutation leakage;
- unchanged A4 bytes and deliberately absent facade/Shell capability.

## Representative semantic results

| Input | Posture/health | Recommendation |
|---|---|---|
| fresh supported equity | `CAPITAL_AT_RISK` / `INTACT` | `MAINTAIN` |
| cited structural milestone | `RISK_REDUCED` / `INTACT` | `PROTECT` |
| favorable continuation | `PROFIT_PROTECTION_ACTIVE` / `INTACT` | `TRAIL_PROTECTION` |
| thesis weakening | `CAPITAL_AT_RISK` / `WEAKENED` | `REDUCE_RISK` |
| cited A4 invalidation | `UNDETERMINED` / `INVALIDATED` | `EXIT_RECOMMENDED` |
| stale/unknown snapshot | `UNDETERMINED` / `UNDETERMINED` | `ABSTAIN` |
| missing A4 | `UNDETERMINED` / `UNDETERMINED` | `INSUFFICIENT_EVIDENCE` |
| multi-leg input | `UNDETERMINED` / `UNDETERMINED` | `UNSUPPORTED_SHAPE` failure |

## Boundary findings

- The broker/TM snapshot is never fetched or inferred.
- A4 semantic fingerprints and subject/lineage are verified; A4 bytes remain
  unchanged.
- Supplied structural levels are preserved with `executable=false`; none are
  created when absent.
- Inactive monitoring mandate does not alter an open position snapshot.
- Recorded replay and deterministic verification require no socket access.
- Policy comparison reuses the same captured input and creates a new record.
- A5 imports no provider adapter, transport, MCP, model SDK, A6 or A7 package.
- Usage and cost are known zero.

## Validation results

The completed gate results are:

- `pytest -q tests/unit/a5`: **52 passed**;
- `pytest -q tests/unit/a4`: **37 passed**;
- `pytest -q tests/unit/facade`: **42 passed**;
- `pytest -q tests/unit/shell`: **67 passed**;
- `pytest -q tests/unit/source_semantics`: **27 passed**;
- `pytest -q tests/unit/opportunity_intelligence`: **65 passed**;
- `pytest -q tests/unit/a3_hardening`: **61 passed**;
- `pytest -q tests/unit/agents`: **270 passed**;
- `pytest -q tests/unit/workflows`: **42 passed**;
- `pytest -q`: **2,190 passed**;
- `python -m compileall src scripts`: passed;
- `ruff check src tests scripts`: passed after one mechanical import-order fix;
- `mypy src tests`: passed across **527 source files**;
- `python -m pip check`: no broken requirements;
- documentation links, secret patterns, forbidden imports, replay isolation and
  `git diff --check`: passed.

No live call was made.

## Residual risks

- Freshness is explicit wall-clock policy only; exchange-calendar semantics
  remain DEF-007.
- Multi-leg combined-risk/hedge reasoning remains deferred.
- A5.1 trusts normalized cited signals and does not independently recalculate
  the underlying A2/A3 facts.
- Facade/Shell artifact admission and TM integration require separate acceptance.
- Monitoring due times are hints, not scheduler guarantees.

## Next prompt

**`TIAF_A5.2 — GOVERNED POSITION FACADE + BOUNDED SHELL EXPOSURE`**
