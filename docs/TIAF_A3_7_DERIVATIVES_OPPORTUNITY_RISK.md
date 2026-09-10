# TIAF A3.7 — Derivatives Context, Opportunity Quality, and Opportunity Risk

## Status

Implemented with deterministic and six-scenario user-level acceptance complete.
Bounded live acquisition was attempted on 2026-09-10, but Dhan returned
`request failed` before active-expiry evidence could be acquired. No live
interpretation is claimed.

## Boundary

A3.7 adds three independently selectable, provider-neutral specialists:

- `DERIVATIVES_CONTEXT` interprets already-computed A2.7 option-chain facts;
- `OPPORTUNITY_QUALITY` describes whether an A2 candidate is early, mature,
  clean, conflicted, extended, or short of remaining room;
- `OPPORTUNITY_RISK` exposes grouped pre-arbitration downside and invalidation
  risks.

All three return the existing `AgentOpinionV2`. Each embeds typed canonical JSON
detail, stable reason codes, evidence-family mappings, contradictions, baseline
agreement, the unchanged evidence fingerprint, and zero model/tool usage. They
have no provider client and do not recalculate A2 primitives.

A3.7 does not choose CE/PE, strike, expiry, strategy, or quantity; create a
target, stop, probability, or return forecast; manage a position; place an
order; or arbitrate a final recommendation. A5 retains position-management
ownership, A6 retains option-expression ownership, and A4 retains arbitration.

## Evidence consumed

The derivatives specialist recognizes the implemented A2.7 families:

- ATM and window IV;
- OI and option-volume put/call ratios;
- CE/PE OI concentration;
- CE/PE option volume;
- ATM CE/PE bid/ask spread percentage;
- explicit expiry and days to expiry;
- supplied A2.9 baseline direction.

It may cite additional `derivatives.*` facts, but does not silently create a
meaning for them. IV rank, IV percentile, cross-expiry term structure, skew
surface, max pain, OI-change regimes, gamma exposure, and probability/expected
move models are not implemented A2.7 facts. Their existing deferrals remain
unchanged. A supplied max-pain value is therefore retained as context and cannot
become a target or direction oracle.

Opportunity quality and risk consume supplied projections under the existing
baseline, technical, relative, sector, news/event, fundamental, macro,
derivatives-context, liquidity, and contradiction namespaces. Those projections
are evidence inputs; the specialists do not invoke or reconstruct the producer.

## Deterministic policy

The versioned policy uses generic engineering boundaries, not symbol-fitted
values. For current A2.7 IV units, values at or below 12 are compressed and
values at or above 30 are elevated. Put/call ratios below 0.8 or above 1.2 are
outside the balanced band. A top-strike OI fraction at or above 0.45 is
concentrated. ATM spread percentages at or below 3 are adequate and at or above
5 are weak. Expiry at one calendar day or less is imminent and at three days or
less is near.

These labels are context only:

- elevated IV is not bearish and compressed IV is not bullish;
- PCR is oriented only against an explicitly supplied baseline direction;
- PCR without direction is non-directional;
- OI concentration is crowding context, not support/resistance truth;
- high IV, CE IV, PE IV, and related fields form one confidence family rather
  than independent confidence votes;
- contradictory OI and volume PCR remain visible.

Opportunity quality maps the existing A2.9 candidate class and supplied
maturity/room/context projections into `STRONG`, `GOOD`, `MIXED`, `WEAK`, or
`INSUFFICIENT_EVIDENCE` detail. Mature/extended or limited-room evidence cannot
be upgraded merely by supportive context. `NO_TRADE` remains weak rather than
being optimized away.

Opportunity risk groups extension, remaining room, participation, volatility,
events, sector/macro context, fundamentals, derivatives crowding, liquidity,
and contradiction. It classifies the number of active independent families as
low, moderate, high, critical, or insufficient. It does not count correlated
raw facts separately. Fundamental fragility is material to short-term/medium
contexts but is not promoted to an active DAY-horizon risk by this initial
policy; event and expiry proximity remain visible for short horizons.

## Instrument and horizon handling

Capability declarations accept equity and index underlyings, futures, and call
or put option instrument contexts. The exact provider-neutral instrument type
is retained in specialist detail. Missing fields stay missing; stock and index
contexts are never assumed to have identical chain capabilities. Unrecognized
instrument types are rejected.

The detail records `DAY`, `SHORT_TERM`, or `MEDIUM` from the existing
`TradeStyle` and flexible `Horizon` contracts. No new public horizon contract or
symbol-specific threshold was introduced.

## Confidence, citations, and abstention

`AgentConfidence.policy_derived` combines pack coverage, weakest quality,
freshness, grouped-family completeness, and internal agreement. It is explicitly
not market-success probability. Adding correlated IV fields cannot increase it.

Every used scalar fact produces a factual claim with its exact evidence
citation. Each derived summary produces evidence-type-homogeneous interpretive
claims citing the facts on which it relies. Evidence IDs, provenance, quality,
freshness, and the original semantic fingerprint remain intact.

Too few core families produce `INSUFFICIENT_EVIDENCE` and a typed
`MissingEvidenceRequest`. A complete but stale derivatives pack produces
`ABSTAIN`; it is not converted to neutral or bullish context. Weak liquidity or
absent participation constrains a completed derivatives opinion to mixed.
Explicit unknown/unavailable state placeholders remain auditable but do not
count as substantive evidence-family coverage.

## Replay and no-LLM result

All specialists use `AgentUsage()` and have no reasoning/provider SDK imports.
The standard `AgentRuntime`, `agent_record_json`, and `load_agent_record_json`
round trip the complete request, evidence pack, opinion detail, citations,
fingerprint, and zero-usage record exactly without provider access.

## Acceptance scenarios

Deterministic coverage includes:

- supportive moderate-IV, supportive-OI, liquid context;
- elevated-IV/near-expiry context that remains non-bearish;
- conflicting OI/volume PCR and concentrated OI;
- mature, extended, limited-room quality;
- sparse and stale derivatives evidence;
- equity, index, futures, stock-option, and index-option-shaped identities;
- DAY versus medium-horizon fundamental-risk materiality;
- A2.9 agreement and disagreement;
- correlated-feature confidence protection;
- citation, no-LLM, ownership-boundary, and exact replay checks.

Focused command:

```bash
pytest -q tests/unit/agents/test_opportunity_specialists_a37.py
```

The six-scenario black-box record is
[`STUDY_A3_7_USER_LEVEL_ACCEPTANCE.md`](STUDY_A3_7_USER_LEVEL_ACCEPTANCE.md).

## Live attempt

The existing bounded read-only Dhan option-chain diagnostic was used for the
first suggested subject:

```bash
python scripts/dhan_option_chain_smoke.py --symbol RELIANCE
```

Instrument resolution succeeded for RELIANCE as NSE equity security ID 2885.
The expiry command then returned `Dhan API error: request failed`, including
when the resolved ID and segment were supplied explicitly, before active
expiries were available. The remaining symbols were not used to repeat the same
authenticated option-data failure. RELIANCE, HDFCBANK, KAYNES, and NIFTY
specialist outputs were therefore not manufactured, and no live chain
fingerprint/replay is claimed. The failure occurred at evidence acquisition;
the specialist itself made no provider, model, broker, or execution call.

## Handoff

A3.8 may select these specialists through the existing registry and runtime.
It must preserve their separate opinions and contradictions. It may not turn a
risk or quality label into an option contract, order, or final recommendation
without the later A4–A6 ownership layers.
