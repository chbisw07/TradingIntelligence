# Study — A3.7 User-Level Acceptance

## Result

Deterministic black-box acceptance passed on 2026-09-10 in the canonical
Asia/Kolkata application timezone. Six scenarios were run through the public
`AgentRegistry` and `AgentRuntime`, using all three A3.7 specialists. This is
the highest existing application-level composition before A3.8 introduces
planner-owned orchestration.

The acceptance operation is:

```bash
python scripts/a3_7_user_acceptance.py
```

It is local, read-only, deterministic, and makes no provider, model, broker, or
execution call.

## Scenario results

| Case | Subject | Instrument / horizon | Derivatives | Quality | Risk | A2 agreement: derivatives / quality / risk |
|---|---|---|---|---|---|---|
| A — supportive positional | RELIANCE | EQUITY / POSITIONAL | POSITIVE | STRONG | LOW | AGREES / AGREES / AGREES |
| B — overextended avoid-chase | HDFCBANK | EQUITY / POSITIONAL | POSITIVE | MIXED | HIGH | AGREES / PARTIALLY_AGREES / AGREES |
| C — high-IV event risk | KAYNES | EQUITY / DAY | MIXED | WEAK | CRITICAL | AGREES / AGREES / AGREES |
| D — bullish underlying, derivatives conflict | NIFTY | INDEX / POSITIONAL | MIXED | WEAK | HIGH | PARTIALLY_AGREES / DISAGREES / DISAGREES |
| E — insufficient derivatives evidence | RELIANCE | EQUITY / POSITIONAL | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | NOT_COMPARABLE / NOT_COMPARABLE / NOT_COMPARABLE |
| F — plain equity, no chain | ATHERENERG | EQUITY / POSITIONAL | INSUFFICIENT_EVIDENCE | GOOD | LOW | NOT_COMPARABLE / AGREES / AGREES |

These are interpretation states, not recommendations. In particular:

- Scenario A retained sufficient room, moderate IV, liquid/supportive OI
  context, broad support, no contradiction, and grouped evidence confidence.
- Scenario B retained the positive underlying context while independently
  surfacing `OPPORTUNITY_MATURE`, `OPPORTUNITY_EXTENDED`, limited room, and high
  risk consistent with A2.9 `MATURE_AVOID_CHASE`.
- Scenario C surfaced elevated IV, imminent earnings/event and expiry risk, and
  conflicting PCR as critical risk while keeping derivatives direction MIXED;
  elevated IV did not become an automatic bearish claim.
- Scenario D retained the bullish baseline/relative evidence and the opposing
  concentrated/conflicting derivatives context. Three contradiction records
  remained visible, and no forced positive conclusion was emitted.
- Scenario E produced zero-confidence insufficient opinions with eight visible
  missing-evidence entries across the three bounded runs.
- Scenario F produced no derivatives opinion because the runtime correctly
  gated the absent required evidence type. Quality and risk continued using
  available cash evidence without inventing an option chain.

## User-level fields

Each successful scenario report contains symbol, instrument, horizon,
derivatives stance, opportunity quality, opportunity risk, top reason codes,
contradiction and missing-evidence counts, policy-derived grouped confidence,
and A2 agreement for each specialist. Underlying requests, evidence packs,
claims, citations, run records, and semantic fingerprints remain available in
the replayable contracts behind the concise report.

## Defects found and corrected

The black-box pass found two narrow A3.7 semantic defects:

1. An implicit `MIXED` or `CONFLICTED` fact activated risk contradiction but
   contradiction detail looked only for explicit `contradiction.*` evidence.
   The resulting empty citation set failed contract validation. It now cites
   the actual baseline/context family records that exposed the conflict.
2. Explicit `UNKNOWN`, `UNAVAILABLE`, `MISSING`, and
   `INSUFFICIENT_EVIDENCE` state placeholders counted toward family coverage.
   They remain auditable evidence but no longer count as substantive quality or
   risk coverage, preventing unknown evidence from looking low risk.

Focused regression tests cover both cases. No threshold, A2.9 policy, provider,
recommendation, or trading behavior was added.

## Forbidden-output checks

Every serialized run was recursively inspected for prohibited structured keys
or position-action values. The check found none of:

- option type or CE/PE selection;
- strike or expiry selection;
- lot size or quantity;
- target, stop, or stop-loss;
- `HOLD`, `BOOK`, `EXIT`, `PROTECT`, or `PARTIAL_BOOK`;
- calibrated success probability.

Context fields such as `expiry_proximity` remain factual risk interpretation;
they do not identify an expiry contract.

## Confidence and no-LLM result

All opinions identify grouped evidence-family coverage, quality, freshness,
agreement, and contradiction burden as their confidence basis. Confidence is
not described as success probability.

Across 18 bounded specialist runs:

- model/LLM calls: 0;
- input tokens: 0;
- output tokens: 0;
- model cost units: 0;
- model identity: absent.

## Replay and fingerprint result

Each `AgentRunRecord` was serialized with `agent_record_json`, reconstructed
with `load_agent_record_json`, and compared exactly. All 18 records matched.
Each request, evidence pack, and emitted opinion retained the same scenario
semantic fingerprint. Replay made no provider call.

## Optional live status

Live Dhan data is not an acceptance dependency. The immediately preceding
bounded A3.7 attempt successfully resolved RELIANCE to NSE security ID 2885,
then the active-expiry endpoint returned `Dhan API error: request failed`, even
with the explicit resolved ID and segment. This pass did not repeat or fan out
that known provider failure. No live chain, specialist result, or live replay
is claimed.

## Security and secrets

The acceptance fixtures contain only synthetic facts and canonical public
symbols. No API key, token, credential, header, provider payload, or secret is
stored or printed. The script imports no provider adapter.
