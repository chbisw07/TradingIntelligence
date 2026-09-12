# TIAF A5 Position Intelligence Architecture

## Status

**Authoritative architecture; implemented and ready for A5 baseline freeze,
2026-09-12 (Asia/Kolkata).** The evidence and complexity review are recorded in
[the A5 architecture review](TIAF_A5_ARCHITECTURE_REVIEW.md).
The bounded contract/deterministic/replay slice is now implemented by
[TIAF A5.1](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md); later seams and
operational exclusions in this document remain authoritative.
The combined [A5 closure review](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md)
accepts A5.1 plus A5.2 and recommends, but does not create,
`tiaf-a5-baseline`.

This document defines contracts and ownership. It does not implement A5,
TradeMonitor integration, monitoring workers, scheduling, broker access, A6,
A7, a remote service or durable storage. Accepted A0-A4 contracts and captures
remain unchanged. A5 contracts are additive and versioned independently.

## 1. Responsibility and authority

A5 turns an explicitly supplied current position snapshot, an accepted A4
result and admitted evidence into explainable position-management advice. The
accepted A4 result may be a current thesis created after position adoption; A5
does not require or reconstruct the trader's original entry rationale.
It answers whether the current thesis remains usable, how the position's
analytical risk posture has changed, what non-executable response is warranted,
and what evidence should be refreshed next.

The authority chain is fixed:

```text
TradeMonitor / broker snapshot (operational truth)
                    |
                    v
        A5 Position Intelligence (advice)
                    |
                    v
        TradeMonitor policy and governance
                    |
                    v
       execution decision, if independently allowed
                    |
                    v
                  broker
```

- A4 owns the surviving thesis, challenges, disposition and residual
  uncertainty at its evidence cutoff.
- A5 owns position-aware interpretation and advisory monitoring needs.
- TradeMonitor (TM) owns operational position lifecycle, risk authority and the
  decision whether and how to act.
- The broker is final truth for live position and execution state.
- A6 owns construction and validation of trade expressions.
- A7 may later own calibrated forecasts and evaluation evidence.

A5 never places, modifies or cancels an order; selects a strike, expiry or
strategy; closes a position; reconstructs broker state; rewrites an A4 record;
or manufactures probabilities. Its objective is risk-adjusted expected utility,
subject to preserved uncertainty and fail-closed authority—not attractive advice.

## 2. Position input boundary

### 2.1 `PositionContext`

The future `PositionContext` is a frozen, immutable, versioned value object. Its
minimum semantic groups are:

- identity: `position_ref`, `snapshot_ref`, optional `tm_position_ref`, canonical
  underlying and exact instrument identity;
- exposure: side, positive quantity magnitude, product/instrument kind, entry
  price and aware entry time when supplied;
- current state: observed price, supplied realized/unrealized P&L, operational
  state and supplied protective-order references;
- derivative facts when applicable: contract identity, option/future attributes
  and aware expiry; absent facts stay absent;
- authority: source/broker identity, snapshot sequence or version, aware
  `observed_at`, aware `acquired_at`, explicit freshness status and reason;
- intelligence lineage: exact A4 run/result/thesis reference and fingerprint,
  plus an optional later A6 expression-origin reference;
- scope/policy/schema identifiers and limited extensible metadata.

Collections representing meaning use tuples. Timestamps are timezone-aware and
normalize to the canonical `Asia/Kolkata` application timezone. JSON continues
to use ordinary arrays and ISO-8601 timestamps with `+05:30`. Metadata remains a
plain extensible dictionary under the established A0 rule.

`PositionContext` is not an account query and is not a broker object. It contains
only the caller-authorized position snapshot needed for one assessment. Provider
SDK objects, sessions, credentials and executable handles are forbidden.
The original entry rationale is optional, but A5.1 still requires a current
accepted A4 result so it does not invent an implicit thesis.

### 2.2 Operational state is supplied, not owned

An operational-state field may carry a small external snapshot vocabulary such
as `OPEN`, `CLOSING`, `CLOSED` or `UNKNOWN`. It reports TM/broker truth at the
snapshot time; it is not an A5 lifecycle machine. A5.1 assesses only a coherent
open single position. Closed, unknown or contradictory state produces an
explicit non-success outcome, never an inferred open position.

No last-known snapshot is silently treated as current. Position identity,
instrument, side, quantity, expiry and linked-thesis conflicts fail before a
directional recommendation. A missing factual value stays unknown.

## 3. Freshness and truth

Freshness is a versioned policy evaluation over supplied timestamps and source
status. A5 may classify the snapshot `CURRENT`, `STALE`, `UNKNOWN` or `INVALID`
and must retain the reason and evaluated-at time. It must not claim
exchange-session awareness until an accepted calendar contract resolves
DEF-007.

- `CURRENT` permits assessment if the remaining evidence is sufficient.
- `STALE` or `UNKNOWN` produces `ABSTAIN` for position action, with refresh needs.
- `INVALID` or identity conflict is a typed failure.
- TM remains free to impose a stricter action-time freshness policy.
- A5 results always cite snapshot identity, observation/acquisition time,
  freshness status, policy version and evidence cutoff.

Advice does not remain current merely because its content-addressed record is
valid. Any position mutation or newer authoritative snapshot requires a
successor assessment. The old result remains historical and immutable.

## 4. Separate state dimensions

Operational position state, analytical risk posture, thesis health,
recommendation and monitoring lifecycle are independent. They must never be
collapsed into one color or status.

### 4.1 Analytical risk posture

The labels `RISK`, `PROTECTED`, `FREE`, and `TRAIL` are not adopted as one
canonical lifecycle:

- `RISK` is renamed because all investments retain some risk.
- `FREE` is rejected as an accounting/legal assertion unless authoritative
  realized-cost and residual-exposure facts plus a separate policy prove a
  precisely named condition.
- `TRAIL` describes a protection recommendation/mode, not lifecycle state.

The bounded posture taxonomy is:

| Posture | Meaning |
|---|---|
| `CAPITAL_AT_RISK` | No cited structural protection milestone materially reduces the original open-position exposure. |
| `RISK_REDUCED` | Supplied position facts and cited structural evidence show material risk reduction, without claiming loss is impossible. |
| `PROFIT_PROTECTION_ACTIVE` | A favorable structural milestone and supplied protection facts support preserving accrued gain. This is not proof of a broker order. |
| `UNDETERMINED` | Evidence cannot safely establish one of the above. |

Postures are non-monotonic. A successor may move from protection back to
`CAPITAL_AT_RISK` if position or market facts change. Every transition cites the
old record, new snapshot/evidence and policy rule. P&L thresholds may corroborate
a transition but cannot replace structural/thesis evidence.

### 4.2 Thesis health

| Health | Rule |
|---|---|
| `INTACT` | Current admitted evidence does not satisfy an A4 invalidation and remains consistent with the surviving thesis. |
| `STRENGTHENED` | A comparable successor A4 result adds cited support without erasing contrary evidence. |
| `WEAKENED` | Comparable successor evidence materially reduces support or raises admitted risk without satisfying invalidation. |
| `INVALIDATED` | A cited A4 invalidation condition is satisfied by admissible current evidence. |
| `UNDETERMINED` | Lineage, comparability or evidence is insufficient. |

A5 does not edit an original thesis. Strengthening or weakening requires a
comparable successor and explicit lineage; elapsed time or price movement alone
does not rewrite historical meaning.

### 4.3 Recommendation

The initial bounded taxonomy is:

| Recommendation | Advisory meaning |
|---|---|
| `MAINTAIN` | Current exposure remains consistent with an intact supported thesis. |
| `WATCH_CLOSELY` | Continue observation under elevated refresh needs; this is not an order. |
| `PROTECT` | Seek stronger downside protection under TM/A6 policy. |
| `REDUCE_RISK` | Reduce exposure semantically; no units, order or contract are selected. |
| `TRAIL_PROTECTION` | Maintain a dynamic profit-protection intent; not an executable trailing order. |
| `EXIT_RECOMMENDED` | A5 advises full exit consideration; TM retains decision and execution authority. |
| `WAIT_FOR_CONFIRMATION` | Evidence conflict is material and an identified refresh can resolve it. |
| `ABSTAIN` | A valid action recommendation is unsafe because current position truth or authority is inadequate. |
| `INSUFFICIENT_EVIDENCE` | Position truth may be current, but required thesis/market evidence is missing. |

`REDUCE_RISK` is intentionally non-quantitative. A later result may carry a
semantic `PARTIAL` scope, while `EXIT_RECOMMENDED` is the full-exit advice. Exact
quantity remains TM-owned. A5.1 should omit the optional scope until a policy and
consumer need prove it necessary.

Each recommendation includes reason codes, cited evidence, affected risk,
thesis health, confidence basis (not probability), uncertainty/gaps, triggering
or invalidation conditions and an authority disclaimer. `ABSTAIN` and
`INSUFFICIENT_EVIDENCE` are first-class outcomes; failure never defaults to
`MAINTAIN`.

## 5. Protection, stops and targets

A5 owns analytical intent, not executable price construction. It may emit a
`ProtectionIntent` such as preserve current thesis room, protect at a cited
structural invalidation, reduce risk after a milestone, or refresh expression.
When evidence already supplies an exact structural level, A5 may repeat it as a
non-executable `ReferenceLevel` containing value, level kind, evidence ID,
observation time and derivation status.

A5 must not:

- invent an uncited stop/target or optimize one;
- round to tick size, choose order type, add slippage or produce broker payloads;
- translate an underlying level into an option-premium order;
- convert combined-premium semantics to leg orders;
- claim that “breakeven” or a percentage protection eliminates all risk.

A6 may later construct a valid expression; TM decides allowed quantity, order
type, exact executable levels and action. A5 can only emit
`EXPRESSION_REFRESH_REQUIRED` with cited reasons, never select the replacement.

## 6. Horizon, expiry and position shape

Horizon is an explicit input and policy dimension. Intraday, BTST/STBT,
positional, swing and long-term cases do not share implicit deadlines. A5 may
surface a supplied mandatory exit window, time-to-expiry pressure, theta/IV
risk, liquidity limitations, or authoritative assignment/exercise facts. It
must not infer these facts or construct a roll.

A5 architecture admits future `PositionShape` and immutable `LegSnapshot`
contracts so aggregate and leg evidence can remain distinct. A hedge
relationship is used only when explicitly supplied. Missing Greeks, chain data,
leg state or aggregate risk is a gap.

The A5.1 implementation boundary is one coherent single-leg equity, future or
option position. Multi-leg input must produce an explicit `UNSUPPORTED_SHAPE`
failure/insufficient outcome. It must not flatten legs or pretend aggregate
risk. Later multi-leg policy must define combined-premium versus leg-level
invalidation and hedge semantics without moving structure construction from A6.

## 7. Bounded monitoring contract

The later [TI Monitoring Architecture](TIAF_MONITORING_ARCHITECTURE.md) is
authoritative for future subscriber-driven runtime admission. It preserves this
A5 contract and normalizes its source advice into a distinct MonitoringMandate,
retaining immutable source identity/hash and requiring explicit subscriber,
lifetime and policy admission. A5 ACTIVE_POSITION/INACTIVE remains advisory;
runtime lifecycle is separate. No scheduler, automatic registration/renewal or
live TM binding is added to A5 by architectural promotion.

Monitoring in A5 means immutable intent, not continuous execution. A
`WatchMandate` is a versioned advisory contract with only:

- mandate ID, revision and predecessor reference;
- canonical instrument and required `position_ref` for A5;
- objective, horizon, `ACTIVE_POSITION`/`INACTIVE` lifecycle and priority intent;
- requested evidence families and per-family freshness intent;
- typed refresh triggers and analysis-depth/profile references;
- optional aware `next_due_at` hint;
- budget/policy/schema references, creation/as-of times and authority scope.

It contains no mutable job state, worker lease, retry counter, broker handle,
provider credential, queue priority guarantee or claim that work will occur.
`next_due_at` is a hint for a future admitted scheduler, not a scheduled job or
service-level promise.

### 7.1 Lifecycle

For A5, only `ACTIVE_POSITION` and `INACTIVE` are promoted. Activation requires
an authoritative open-position reference. Deactivation stops this mandate's
future eligibility; it does not close the broker position or invalidate other
mandates over the instrument. A successor revision records every transition.

The exploratory `PASSIVE` and `ACTIVE_WATCH` names remain TBD for A9 candidate
monitoring. UI colors are presentation-only and absent from domain contracts.

### 7.2 Refresh triggers

A5 may request, but does not execute, refresh for:

- cited price/structure thresholds;
- an A4 thesis invalidation predicate;
- corporate/news/fundamental events;
- volatility or derivatives evidence changes;
- expiry/time thresholds;
- authoritative broker/TM position changes;
- a periodic heartbeat hint or manual request.

Each trigger is typed and carries a predicate/reference, required evidence
family, reason and authority. It is not an arbitrary callback or executable
expression. A future scheduler must re-check mandate and position authority at
dispatch time.

### 7.3 Shared evidence and recomputation

Shared evidence is not shared analysis state. Evidence may be reused only when
identity, authority, cutoff, freshness and policy permit it. New evidence after
the cutoff creates a successor record; it never mutates an old result.

Fingerprints should expose component dependencies and deltas for future
selective recomputation. A5.1 deliberately recomputes the whole small
deterministic assessment from captured inputs. Component-level reuse is deferred
until dependency correctness is proven; it is not an optimization claim.

## 8. `PositionIntelligenceResult`

The immutable result contract contains:

- result/run identity, predecessor identity and aware timestamps;
- position/snapshot/TM references, snapshot time and freshness evaluation;
- exact A4 result/thesis/run references, fingerprints and evidence cutoff;
- supplied operational state plus analytical posture and transition;
- thesis health and bounded recommendation;
- protection intent and cited non-executable reference levels;
- structural milestones, remaining-opportunity state, invalidation/refresh
  triggers and monitoring needs;
- evidence IDs, reason codes, contradictions, gaps and residual uncertainty;
- confidence basis without calibrated probability;
- schema/policy/configuration versions and semantic/run fingerprints;
- leaf-exact model usage/cost state and authority statement.

Known deterministic A5.1 execution records zero calls/tokens/cost. Unknown cost
must remain unknown in any future model-enabled path. No order action, broker
payload, executable quantity, order type, strike or replacement strategy is
allowed in the result.

Result construction validates that cited evidence belongs to the supplied
cutoff/capture and that the A4 fingerprint is unchanged. It preserves A4
conflict, counter-thesis and residual uncertainty rather than projecting only
the chosen disposition.

## 9. Replay and audit

An A5 capture contains exact bytes or content-addressed artifacts for:

- the authorized position snapshot;
- the complete linked A4 capture/result and admitted evidence;
- position/freshness/policy/configuration versions and evidence cutoff;
- the result, predecessor/transition and emitted mandate/refresh needs;
- artifact, semantic and run fingerprints plus usage/cost records.

Recorded replay returns the captured result without broker, provider, model or
TM calls. Deterministic verification rebuilds from captured inputs under the
captured policy. Policy comparison creates a new comparison record and never
rewrites the original. A current snapshot change creates a successor result.
Corrupt/missing artifacts, fingerprint disagreement or policy ambiguity fail
closed.

## 10. Facade, Shell and integration seams

The architecture pass itself added no capability. The separately accepted
[A5.2 slice](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md) now publishes
`position.assess` with the proposed `CAPTURED_READ` effect and dedicated
position authority. Generic `replay.recorded` handles authorized A5 captures;
no redundant `position.replay` was needed. A separate `position.explain`
capability remains unnecessary because the Shell projects the bounded structured
result already returned to the same caller.

The Shell now activates only:

```text
position assess
explain last
trace last
```

Shell does not discover broker state, schedule monitoring or call private A5
objects. Execution-like position verbs remain unavailable.

The future TM handoff is versioned and idempotent by advice identity. TM supplies
or authorizes the snapshot, checks action-time freshness, and may reject, adapt
or ignore advice under its own policy without changing the immutable A5 record.
A5 receives no broker credential or execution handle.

A6 integration is limited to a typed future expression-origin reference and
`EXPRESSION_REFRESH_REQUIRED`; A5 never constructs the replacement. A7 is an
optional admitted evidence family with forecast identity, calibration/version
and cutoff. A5 works without A7 and never fills missing forecasts with invented
probabilities.

## 11. Failure semantics

| Condition | Required behavior |
|---|---|
| Stale/unknown position snapshot | `ABSTAIN`; emit authoritative-position refresh need. |
| Missing/unusable A4 result | `INSUFFICIENT_EVIDENCE`; do not reconstruct A4. |
| Position/A4/instrument identity conflict | Typed invalid-input failure; no recommendation. |
| Unknown/closed position state | Not applicable or typed failure; never assume open. |
| Partial leg data or multi-leg in A5.1 | `UNSUPPORTED_SHAPE`/insufficient outcome. |
| Missing current market evidence | `INSUFFICIENT_EVIDENCE` or `WAIT_FOR_CONFIRMATION` only when a resolvable conflict exists. |
| Authoritatively expired open derivative | Surface time-risk and normally `EXIT_RECOMMENDED` only under explicit policy; otherwise abstain. |
| Replay corruption/fingerprint mismatch | Integrity failure; no live fallback. |
| Policy/version mismatch | Fail closed or explicit comparison mode; never silent coercion. |

Provider/model failures remain typed evidence gaps. They cannot be transformed
into `MAINTAIN`. No result may fabricate a target, probability, broker state or
execution claim to fill a failure.

## 12. Security and privacy

Position data is sensitive. Admission is object-scoped to authorized position,
snapshot and evidence references. Captures minimize account data, use logical
references, follow existing redaction/retention boundaries, and never contain
credentials, raw broker sessions or arbitrary portfolio access. Public results
are allowlisted projections. Logs must not expose account identifiers beyond
the caller-authorized stable reference.

## 13. Acceptance corpus

The implementation corpus must include at least:

1. new position -> `CAPITAL_AT_RISK`;
2. intact thesis plus cited advance -> `RISK_REDUCED`;
3. favorable milestone -> `PROFIT_PROTECTION_ACTIVE`, without “free” claim;
4. strong continuation -> `TRAIL_PROTECTION`;
5. weakened thesis -> `REDUCE_RISK` or `PROTECT` by policy;
6. cited invalidation -> `EXIT_RECOMMENDED`;
7. stale snapshot -> `ABSTAIN`;
8. missing A4 -> `INSUFFICIENT_EVIDENCE`;
9. successor A4 strengthens thesis;
10. successor A4 creates preserved conflict;
11. multi-leg input is explicitly unsupported in A5.1;
12. partial leg data does not become aggregate truth;
13. near-expiry time risk;
14. intraday supplied mandatory-exit window;
15. no new information -> stable semantic result;
16. policy-version comparison creates a separate record;
17. exact recorded offline replay with zero live calls;
18. monitoring need/mandate emission;
19. mandate deactivated while position remains open;
20. TM rejection/ignore leaves the A5 record unchanged;
21. quantity/sign/instrument identity mismatch fails closed;
22. closed/unknown operational state is not assessed as open;
23. snapshot successor creates a new result and preserves the old one;
24. A4 conflicts/counter-thesis survive projection;
25. all timestamps are aware and normalize to Asia/Kolkata;
26. no broker/provider/model call and known-zero model usage in deterministic replay.

Fixtures are synthetic or captured and deterministic. Live profitability is not
an acceptance criterion.

## 14. Bounded implementation sequence

### A5.1 — contracts and deterministic single-position baseline

Implement only:

1. additive immutable versioned input/result/mandate/capture contracts;
2. strict identity, freshness, A4-lineage and citation validation;
3. a transparent deterministic no-model policy for one open single-leg position;
4. thesis-health, risk-posture, bounded recommendation and monitoring-need output;
5. content-addressed capture, recorded replay, deterministic verification and
   policy comparison;
6. the acceptance corpus above, including explicit unsupported multi-leg cases.

Keep it captured-input/local and provider-, broker-, TM-, scheduler- and
facade-independent. Do not add Shell commands in A5.1. Avoid trading thresholds
not already supplied by versioned policy/evidence. Preserve `ABSTAIN`, conflict
and insufficient evidence.

The separately accepted A5.2 slice adds governed facade/Shell exposure. Later
slices may add richer position shapes/protection, TM integration, or runtime monitoring. Durable queues,
calendar-aware dispatch, adaptive cadence, retry/recovery, remote service and
distributed persistence remain A10/explicit operational work.

## 15. Compatibility decision

The frozen A0 `PositionRequest`, `PositionAssessment` and `PositionAction` are
not silently redefined. A5 uses new versioned contracts. Any consumer projection
back to A0 requires an explicit, tested mapping and cannot erase A5 uncertainty
or authority semantics.

The closure review has completed the former next prompt. The exact next prompt
title after the A5 baseline freeze is:

**`TIAF_A6 — OPTION EXPRESSION INTELLIGENCE ARCHITECTURE PASS`**
