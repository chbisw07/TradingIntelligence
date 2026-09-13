# TIAF A6.2 — Candidate Evaluation, Ranking & Replay

Status: **ACCEPTED / DONE** on 2026-09-13 (Asia/Kolkata), closed by the
[independent acceptance](TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY_ACCEPTANCE.md).
A6.1 is **ACCEPTED / DONE**; A6.3 is **ACTIVE / NEXT**; A6.4 is **NOT_IMPLEMENTED**;
`expression.assess` is **NOT_PUBLISHED**.

## Scope and authority

A6.2 is an internal, captured-input, deterministic advisory engine. It consumes
an exact A6.1 admission result, request, A4 result, evidence bundle and pinned
policy. It neither reacquires evidence nor reruns A2, A3, A4 or A5. It owns no
account, capital, sizing, order, route, execution, broker or monitoring action.

The implementation remains inside `tiaf.trade_expression`:

| Module | A6.2 responsibility |
|---|---|
| `contracts.py` | Immutable/versioned candidate, complete gate evaluation, rank facts, structured explanation and assessment contracts |
| `enums.py` | Closed disposition, candidate eligibility and gate vocabularies |
| `evaluation.py` | Pure candidate generation, gate evaluation, global disposition, lexicographic ranking, content addressing and offline replay |
| `admission.py` | Preserved A6.1 admission; known qualified event blockers retain precedence so A6.2 can emit WAIT without inspecting a stale candidate universe |
| `policy.py` | Reused exact A6.1 spread and listed-strike geometry primitives; no parallel thresholds |

## Candidate universe

The admitted direction fixes the only supported side:

```text
BULLISH → LONG CE
BEARISH → LONG PE
```

For each of at most three captured expiry chains, the evaluator uses the
qualified chain spot and actual listed contracts to create ATM, ITM1 and OTM1
on that side. The lower listed strike wins an exact ATM midpoint tie. ITM1/OTM1
use actual adjacent strikes with CE/PE orientation; a missing neighbor creates no
candidate. Request moneyness preferences may restrict/reorder this closed set.
At most nine candidates are evaluated and all evaluations remain in the result.

Candidate identity is content-addressed from provider-neutral contract identity,
direction, LONG side and geometry label. Provider-native instrument references
remain attributable evidence but do not determine candidate or ranking identity.

## Complete gate evaluation

Every generated candidate records the same complete ordered gate vector:

```text
IDENTITY_MEMBERSHIP
→ TIMING_FRESHNESS
→ HORIZON_FIT
→ QUOTE_GEOMETRY
→ TOP_DEPTH
→ SPREAD
→ PREMIUM_CAP
```

Each gate records PASS, FAIL or UNKNOWN, a stable reason, available exact
measurement/unit, threshold/unit, evidence references and policy reference.
FAIL and UNKNOWN remain distinct. All gates are recorded even when an earlier
gate fails; TF-05 early termination remains deferred.

- Expiry fit uses the qualified expiration instant minus the intended exit and
  the horizon-specific residual-life rule. Equality passes. It does not promise
  future liquidity or executable exit availability.
- Freshness uses qualified market observation time at the captured cutoff.
  Acquisition-only, future or stale observations cannot establish suitability.
- Bid/ask and top quantities are mandatory. Missing operands are UNKNOWN; known
  invalid geometry or zero depth is FAIL. LTP, OI and volume do not substitute.
- Spread reuses the Decimal midpoint/bps primitive and exact policy boundaries.
- A premium cap compares the captured ask in INR per unit. It is not total
  capital, affordability, cheapest-first ranking or an order price.

Candidate eligibility is ELIGIBLE only when every gate passes. Any UNKNOWN makes
the candidate UNKNOWN even if another gate already failed, preserving the full
required-window rule. Otherwise any FAIL makes it INELIGIBLE.

## Global dispositions and evidence precedence

`TradeExpressionAssessment` uses the canonical dispositions:

- `EXPRESSION_AVAILABLE` — complete required evidence and at least one eligible
  candidate;
- `NO_OPTION_TRADE` — complete scope proves no supported contract or candidate
  passes, or the admitted upstream prohibition maps here;
- `WAIT_FOR_EXPRESSION` — known temporary A4 WAIT/CONFLICTED or a qualified
  material relevant event inside `(cutoff, intended_exit]`;
- `INSUFFICIENT_EVIDENCE` — admission, scope, timing, event or any required
  candidate fact remains unknown;
- `UNSUPPORTED` — a well-formed admitted classification lies outside v1.

Upstream NO_TRADE/AVOID cannot be rescued by attractive option evidence.
Upstream WAIT/CONFLICTED and known event blockers produce no fabricated candidate
evaluations. CONFIRMED_EMPTY qualified derivative scope proves
`NO_LISTED_EXPIRIES_IN_SCOPE`; PARTIAL, UNAVAILABLE and UNKNOWN cannot. General
unknown event coverage is an explicit optional gap in default mode, while an
ambiguous relevant/material event is insufficient. An event-clear preference
requires qualified coverage of the full holding interval.

## Ranking and shortlist

Hard gates precede ranking. Eligible candidates sort ascending by the exact
architecture-defined tuple:

```text
(
  spread_tier,
  requested_moneyness_rank,
  expiry_cushion_excess_seconds,
  exact_spread_bps,
  canonical_contract_key,
)
```

The canonical key is exchange, provider-neutral subject, expiry date, normalized
strike and option side. The result exposes exactly one preferred candidate and
the next at most two eligible alternatives, but retains all candidate
evaluations. Structured `RankDifference` records the first decisive dimension
against every lower-ranked eligible candidate. There is no weighted score,
cheapest-first, longest-expiry-first, expected return, probability, delta/IV
optimization or learned policy.

## Explanation, invalidation and replay

Canonical explanation is structured reason-code data: disposition reasons,
preferred-selection reasons, every candidate gate/rejection/uncertainty and
decisive rank differences. The assessment also records blockers, evidence gaps,
input/policy fingerprints, optional supplied composition references and these
point-in-time invalidations:

- upstream thesis or holding target changes;
- quote/underlying freshness expiry;
- derivative coverage or contract availability changes;
- residual-life threshold crossing;
- spread-policy breach;
- event evidence changes;
- policy/profile changes.

Assessment, candidate and evaluation identities are content-addressed without a
self-hash cycle. `verify_trade_expression_replay` validates all recorded
identities and recomputes the assessment from the exact captured artifacts and
composition references. It reads no wall clock, network, provider, model,
broker, environment or current registry. Canonicalized chain/quote ordering
produces the same universe, shortlist and fingerprint.

## Preserved boundaries

- A5 runtime, `position.assess`, A5 replay and fingerprints are unchanged.
- R1 required scope, R2 eight-operation catalog, R3 capture/pins, R4 optional
  imports and R5 COLD ownership remain unchanged.
- `expression.assess`, its facade authority/handler and Shell command remain A6.3.
- No live source, acquisition-qualified fallback, A7 forecast, model call,
  multi-leg/short option, A5→A6 orchestration, TM handoff or broker operation was
  added.
- TF-05, live authoritative quote time/calendar/expiration feasibility and the
  existing wider strategy/integration work remain deferred under existing IDs;
  A6.2 introduced no new deferral.

## Validation

The focused A6 suite contains **99 passing tests** covering candidate bounds and
sides, expiry equality/failure, listed geometry, coverage states, quote/depth/
spread/premium/event gates, all dispositions, ranking precedence, preference
restriction, shortlist bounds, explanations, semantic fingerprints, input-order
invariance and socket-denied replay. Focused compatibility results are A4 37,
A5 52, facade 71, Shell 89 and R1–R5 93. The full suite passes **2,419 tests**.
Compileall, Ruff, mypy over 559 source files, pip dependency integrity, the
71-package lock check, diff whitespace, catalog/A5 parity, forbidden imports,
secret patterns and 129 Markdown local-link checks all pass.

Next prompt:
`TIAF A6.3 — FACADE & TI_SHELL EXPOSURE`.
