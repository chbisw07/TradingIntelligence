# TIAF A5.1 Deterministic Single-Position Baseline

## Status

**Implemented; acceptance-ready, 2026-09-12 (Asia/Kolkata).** This is the first
bounded runtime slice under the accepted
[A5 architecture](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md). The validation
record is [STUDY_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE_ACCEPTANCE.md](STUDY_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE_ACCEPTANCE.md).

A5.1 is a local, deterministic, captured-input advisory capability. It adds no
facade descriptor, Shell command, provider/model/broker call, TM transport,
scheduler, A6/A7 logic, remote service, or durable database.

The later additive
[A5.2 publication slice](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md) exposes
this unchanged baseline through the governed facade and bounded Shell; that
publication is not retroactively part of A5.1.

## 1. Package

The provider- and broker-neutral implementation is under `src/tiaf/a5/`:

| Module | Responsibility |
|---|---|
| `enums.py` | Closed posture, health, recommendation, monitoring, failure, shape and replay vocabularies. |
| `contracts.py` | Frozen input, result, policy, mandate, capture and replay contracts. |
| `freshness.py` | Explicit wall-clock snapshot freshness without exchange-calendar claims. |
| `policy.py` | Versioned generic deterministic policy and exact rule order. |
| `monitoring.py` | Pure monitoring-need and immutable mandate construction; no dispatch. |
| `evaluation.py` | Identity validation, conservative rule evaluation, fingerprints and run validation. |
| `replay.py` | Content-addressed capture, recorded replay, verification and policy comparison. |
| `errors.py` | Typed input, output, policy and replay integrity errors. |

## 2. Input contracts

`PositionSnapshot` carries one authorized operational snapshot: stable position,
snapshot and optional TM references; exact provider-neutral `InstrumentKey`;
underlying; signed quantity plus side; entry/current values; supplied P&L;
product; expiry; supplied reference levels; operational source/state; snapshot
version/time; declared freshness/basis; optional intraday exit time; and scoped
authority references.

Validation requires:

- aware timestamps normalized to `Asia/Kolkata`;
- `LONG` with positive quantity and `SHORT` with negative quantity;
- exact instrument-type and expiry agreement;
- expiry for futures/options and no expiry for equity;
- snapshot at or after entry;
- at least two leg references for declared multi-leg shape;
- no future snapshot relative to request `as_of`;
- explicit source, version, freshness basis and authority.

`PositionIntelligenceRequest` embeds the snapshot and optional A4 result so all
deterministic inputs can be captured. A missing A4 result remains representable
and yields `INSUFFICIENT_EVIDENCE`; it is never reconstructed. Optional successor
A4 and previous A5 results require consistent subject/position/lineage.

`PositionSignal` is an already-normalized, cited supplied observation. It does
not ask A5 to calculate indicators. Thesis invalidation must reference an actual
condition in the linked A4 lineage. Any exact `ReferenceLevel` is explicitly
`executable=false` and must cite supplied evidence.

## 3. Supported shape and authority

A5.1 evaluates one open single-leg equity, future, call, or put position. A
declared multi-leg shape returns `UNSUPPORTED_SHAPE`; legs are neither flattened
nor partially evaluated. Closed, closing, or unknown operational position state
returns `ABSTAIN` and never becomes an inferred open position.

TM/broker state remains caller-supplied operational truth. A5 receives no SDK
object, credential, session, order API or portfolio query. The result carries:

```text
ADVISORY_ONLY_TRADEMONITOR_DECIDES_BROKER_EXECUTION
```

## 4. Deterministic policy

The baseline policy ID is `a5-policy:deterministic-single-position`, version
`1.0`. The rule precedence is explicit:

1. unsupported shape;
2. supplied operational position state;
3. effective snapshot freshness;
4. missing A4 result;
5. expired contract or reached intraday exit window;
6. cited thesis invalidation;
7. material conflict;
8. thesis weakening or supplied position risk;
9. favorable continuation;
10. cited structural/protection milestone;
11. linked A4 disposition;
12. supported maintain.

This precedence ensures missing/stale truth cannot become `MAINTAIN`. It contains
no tuned security-specific thresholds. Version `1.1-comparison` exists only to
exercise explicit policy comparison with a different near-expiry/heartbeat
configuration.

### Result dimensions

- Posture: `CAPITAL_AT_RISK`, `RISK_REDUCED`,
  `PROFIT_PROTECTION_ACTIVE`, or `UNDETERMINED`.
- Thesis health: `INTACT`, `STRENGTHENED`, `WEAKENED`, `INVALIDATED`, or
  `UNDETERMINED`.
- Recommendation: `MAINTAIN`, `WATCH_CLOSELY`, `PROTECT`, `REDUCE_RISK`,
  `TRAIL_PROTECTION`, `EXIT_RECOMMENDED`, `WAIT_FOR_CONFIRMATION`, `ABSTAIN`, or
  `INSUFFICIENT_EVIDENCE`.
- Remaining opportunity: a direct projection from an explicit cited signal,
  otherwise `UNKNOWN`; never a probability.

`FREE` is absent. `TRAIL_PROTECTION` remains advice, not broker state.

### Protection and expression seam

`ProtectionIntent` carries a semantic action and supplied non-executable levels.
A5 invents no stop, target, tick rounding, order type, or quantity. A supplied
`EXPRESSION_UNSUITABLE` signal may produce `EXPRESSION_REFRESH_REQUIRED`; no
strike, expiry, hedge, roll, or replacement is selected.

### Expiry and intraday time risk

For a supplied derivative expiry, A5 calculates calendar days from aware
`as_of`. An expired contract produces a conservative non-maintain result; a
near-expiry contract produces heightened review and a time-risk monitoring need.
A supplied intraday mandatory-exit time similarly produces `WATCH_CLOSELY` before
the window and `EXIT_RECOMMENDED` after it, subject to current snapshot truth.
TM still decides whether and how to act.

## 5. Monitoring intent

Every active assessment emits a bounded position-snapshot heartbeat need plus
material thesis/time/evidence needs when applicable. `MonitoringNeed` carries
evidence family, typed trigger, reference, priority, freshness/cadence hints,
optional next-due hint, reason, materiality and policy/budget references.

`WatchMandate` implements only `ACTIVE_POSITION` and `INACTIVE`, with immutable
revision/predecessor lineage. Inactivation emits no needs and does not alter the
supplied operational position state. No job, worker, lease, queue, retry,
calendar, dispatch or service-level promise exists.

## 6. Successors and A4 preservation

A4 result fingerprints and IDs are verified before evaluation. Subject and
original A2/A3 lineage must remain comparable. A successor A4 result can
strengthen, weaken or conflict with the current thesis, but neither A4 object is
modified or recomputed.

A previous A5 result establishes predecessor result/mandate linkage and explicit
changed-input references. A5.1 recomputes the entire small deterministic result;
it makes no selective-execution claim.

## 7. Replay and fingerprints

An `A5Capture` stores canonical snapshot bytes, current A4-result bytes when
present, and the complete run bytes with exact SHA-256 checksums and semantic
links. The run embeds request, policy, result, predecessor and all monitoring
intent, so original and successor A4 inputs remain available.

- Recorded replay returns the exact captured run with zero live calls.
- Deterministic verification rebuilds from the captured request/policy and
  compares run plus result fingerprints.
- Policy comparison evaluates the same captured request under a supported
  candidate policy and creates a separate comparison record.
- Corruption, policy mismatch and unsupported versions fail closed; there is no
  live repair fallback.

Usage is leaf-exact known zero: zero provider calls, model calls, input/output
tokens and model-cost units.

## 8. Facade, Shell, TM, A6 and A7 decisions

`position.assess` remains unregistered. The existing facade has no A5 authority
scope or artifact lifecycle yet, so publishing it in this foundational slice
would broaden the accepted interface prematurely. Consequently the reserved
Shell `position ...` family remains unavailable.

The immutable A5 result is the future TM advisory handoff shape: advice/result
ID, position/snapshot identity and freshness, recommendation, policy/schema,
fingerprints and authority statement. TM integration/transport remains A8.

A6 receives only a future expression-refresh need. A7 forecast references are
not present in A5.1; no probability, expected return, target-hit chance or
distribution is emitted.

## 9. Failure behavior

Intrinsic contract incoherence and forged A4/replay fingerprints raise typed
integrity errors. Valid but non-actionable inputs produce explicit domain
results:

| Condition | Result |
|---|---|
| stale/unknown snapshot | `ABSTAIN` |
| missing A4 | `INSUFFICIENT_EVIDENCE` |
| unsupported multi-leg | `UNSUPPORTED_SHAPE` + insufficient result |
| closed/unknown operational state | `ABSTAIN` |
| expired derivative | conservative `EXIT_RECOMMENDED` |
| A4 insufficient/abstain | `INSUFFICIENT_EVIDENCE` |
| material conflict | `WAIT_FOR_CONFIRMATION`/heightened review |

Failure never silently becomes hold, maintain, protect, or execution.

## 10. Deliberate exclusions

No facade/Shell exposure, live position acquisition, broker/TM integration,
multi-leg interpretation, scheduler, queue, model, provider, A6 selection, A7
forecast, remote service, database, portfolio scan or execution behavior is
implemented.

## 11. Next bounded slice

After A5.1 acceptance, the exact proposed next prompt title is:

**`TIAF_A5.2 — GOVERNED POSITION FACADE + BOUNDED SHELL EXPOSURE`**

That slice should expose captured assessment/replay through accepted capability
admission and only then activate bounded `position` Shell projections. It must
not add broker synchronization, TM action, live acquisition, monitoring runtime,
multi-leg policy, A6 or A7.
