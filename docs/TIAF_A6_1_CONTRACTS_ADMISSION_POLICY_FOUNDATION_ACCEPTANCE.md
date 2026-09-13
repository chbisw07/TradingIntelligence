# TIAF A6.1 — Contracts, Admission & Policy Foundation Acceptance

## Decision and boundary

**READY_TO_CLOSE_A6_1** — independently accepted on 2026-09-13
(Asia/Kolkata).

- A6 architecture: **ACCEPTED**.
- A6.1 contracts/admission/policy foundation: **ACCEPTED / DONE**.
- A6.2 candidate evaluation/ranking/replay: **ACTIVE / NEXT**, not implemented
  by this pass.
- `expression.assess`: **NOT_PUBLISHED**; the public catalog remains exactly
  eight operations.
- A5 remains frozen at `tiaf-a5-baseline`; R1–R5 remain separate accepted/done
  cross-cutting workstreams.
- No provider, model, broker, facade publication, Shell command, commit, tag or
  push was introduced by this acceptance.

Version identities remain separate: the Python package is `0.1.0`, A6.1
contract schemas are `1.0`, the baseline policy is `1.0-draft`, and evaluator,
normalizer, capability and composition identities retain their own namespaces.

The next prompt is exactly:
`TIAF A6.2 — CANDIDATE EVALUATION, RANKING & REPLAY`.

## Independent acceptance findings

| Area | Verdict | Evidence / conclusion |
|---|---|---|
| Request contract | ACCEPT | Frozen schema-1.0 `TradeExpressionRequest` forbids extras and contains no account, capital, final quantity, order type, route, executable stop/target, execution consent or broker authority. |
| Direction | ACCEPT | Closed `BULLISH`/`BEARISH`; A4 `POSITIVE`/`NEGATIVE` maps deterministically. No CE/PE recommendation is produced. |
| Horizon | ACCEPT | DAY/POSITIONAL only, with aware exact target and matching Decimal elapsed seconds. Ambiguous labels are invalid below the adapter boundary. |
| Timing | ACCEPT | Market observation, acquisition, evaluation cutoff, freshness basis, expiry date, qualified expiration instant and optional sourced trading cutoff remain separate. Asia/Kolkata normalization grants no source authority. |
| Option identity | ACCEPT | Subject, class, exchange/segment, CE/PE, strike, expiry date and qualified instant define semantic identity. Provider-native references remain evidence metadata and do not define the identity fingerprint. |
| Quote/chain evidence | ACCEPT | Missing book fields stay missing; LTP cannot fill bid/ask; zero OI, volume and depth remain factual zero; crossed quotes fail. Provider IV now has an explicit immutable value/unit/evidence wrapper. Greeks require supplied values, unit semantics and evidence and are never synthesized. |
| Coverage / absence | ACCEPT | PRESENT, CONFIRMED_EMPTY, PARTIAL, UNAVAILABLE and UNKNOWN are distinct. CONFIRMED_EMPTY requires complete qualified proof; an empty response alone proves nothing. |
| Expiry qualification | ACCEPT | Date-only/unknown expiry cannot claim an instant or satisfy strict admission. No NSE cutoff is invented; trading cutoff is separate sourced context. |
| Policy | ACCEPT | Immutable `deterministic-long-option/1.0-draft` policy pins evaluator/normalizer identity, candidate/chain bounds, horizon and age limits, observation authority, expiration qualification, spread tiers/hard limit, depth, residual life, premium/event behavior, permitted preferences, alternatives and coverage requirements. No hidden admission constant was found. |
| Preferences | ACCEPT | Only bounded moneyness order, INR premium cap and event-clear requirement are accepted. Preferences narrow/reorder policy and cannot weaken hard gates; no callbacks, DSL, cheapest-first or longest-expiry rule exists. |
| Moneyness | ACCEPT | ATM uses nearest listed strike with lower-strike ties; ITM1/OTM1 use actual adjacent listed strikes with correct CE/PE orientation. No spacing or delta is fabricated. |
| A4 admission | ACCEPT | Integrity and lineage are checked; only COMPLETE/SUPPORTIVE with a supported surviving primary thesis and resolved matching direction proceeds. A4 admission now executes before horizon/evidence policy gates, matching declared policy precedence. |
| Admission taxonomy | ACCEPT | Normal results are typed ADMITTED, REJECTED_UPSTREAM, INSUFFICIENT_EVIDENCE, UNSUPPORTED or INVALID_REQUEST outcomes; malformed/unsupported policy and replay-integrity failures use typed exceptions. |
| Event evidence | ACCEPT | Known blocker, qualified no-intersecting-event proof and unknown remain distinct. Confirmed-empty qualified coverage cannot be mislabeled UNKNOWN. Event evidence creates no probability or recommendation. |
| Freshness | ACCEPT | Admission uses captured cutoff and authoritative observation times only. Acquisition-only evidence cannot pass observation freshness; no wall clock, provider or network is consulted. |
| Spread | ACCEPT | Decimal absolute spread, midpoint and bps preserve exact boundaries, missingness, crossed/invalid quote, zero depth, hard-limit and tier outcomes. The primitive does not rank/select. |
| Precision / fingerprints | ACCEPT | Decimal canonicalization, stable semantic-set ordering, ISO aware timestamps and content-addressed results are deterministic. Semantic changes alter fingerprints; irrelevant reference ordering does not. Credential-shaped fields/text and local paths are rejected. |
| Replay | ACCEPT | Admission replay verifies captured request/A4/evidence/policy identities and exact semantic result. Socket-denial coverage proves no current network/provider state is used. |

## Compatibility verdicts

| Gate | Verdict |
|---|---|
| R1 required/optional scope | INTACT — stable required scope and explicit absence regressions pass. |
| R2 discovery/catalog | INTACT — exactly eight capability IDs; no A6 descriptor. |
| R3 composition/verifier | INTACT — captured composition and pinned verification regressions pass. |
| R4 optional imports | INTACT — A6 imports no optional provider/model implementation and isolation regressions pass. |
| R5 COLD ownership | INTACT — trusted startup/configuration ownership regressions pass; A6 adds no startup selector. |
| A5 freeze | INTACT — no diff from `tiaf-a5-baseline` under `src/tiaf/a5` or `tests/unit/a5`; 52 focused A5 tests pass. |
| A6.2 boundary | **A6_2_BOUNDARY_PRESERVED** — no full candidate evaluation, preferred selection, lexicographic/alternative ranking, final evaluated-candidate disposition, facade publication or Shell command exists. Geometry and spread functions are explicitly foundation primitives. |

## Deferral-governance audit

No deferred item was silently removed or closed.

- DEF-006 remains PLANNED for the rest of bounded A6 and later strategy/A7
  work; TF-05 early termination remains deferred with full-window evidence
  requirements retained.
- DEF-007 remains DEFERRED: A6.1 supplies the session/expiry qualification
  contracts, not a calendar engine or live qualified source.
- DEF-014 remains DEFERRED: acquisition time is not promoted to an authoritative
  option-chain market-event timestamp.
- DEF-025/SigmaDSL, DEF-039–046 model/forecast work, DEF-044/A7,
  DEF-054/rich NLP/Web reporting, DEF-010/Monitoring Runtime and DEF-056/multi-leg
  position interpretation remain open or outside A6.1 with their existing owners.
- Multi-leg/short-option strategies, live acquisition, TM/broker integration and
  production operationalization remain outside this slice.

The acceptance audit found and fixed three in-scope semantic issues rather than
deferring them: explicit IV units/evidence, declared A4-first admission
precedence, and the confirmed-empty-versus-unknown event contradiction. No new
deferral ID was required.

## Validation evidence

All commands used the repository virtual environment and made no live calls.

| Gate | Result |
|---|---:|
| `pytest -q tests/unit/a6` | **56 passed** |
| `pytest -q tests/unit/a4` | **37 passed** |
| `pytest -q tests/unit/a5` | **52 passed** |
| `pytest -q tests/unit/facade` | **71 passed** |
| `pytest -q tests/unit/shell` | **89 passed** |
| R1–R5 focused regression | **93 passed** |
| `pytest -q` | **2,376 passed** |
| `python -m compileall src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS — 554 source files |
| `python -m pip check` | PASS — no broken requirements |
| `uv lock --check` | PASS — 71 packages resolved |
| `git diff --check` | PASS |

Additional audit results:

- capability catalog: exactly
  `a4.evaluate`, `a4_input.project`, `baseline.assess`, `capabilities.list`,
  `opportunity.assemble`, `position.assess`, `replay.recorded`, `replay.verify`;
- A6 provider/model/broker/specialist forbidden-import scan: PASS;
- A6 credential/local-path fingerprint rejection and repository secret scan:
  PASS; no secret material recorded;
- Markdown local-link validation: PASS;
- A5 tag parity: PASS;
- README contains separate R1, R2, R3, R4 and R5 rows, explicit A7–A10 rows,
  and the forward path `A6.1 → A6.2 → A6.3 → A6.4 → A7 → A8 → A9 → A10`.

## Residual risks

A6.1 is a captured-input deterministic foundation, not live source readiness or
a complete expression engine. A qualified live option observation timestamp,
session/calendar source and precise expiration authority may remain unavailable;
the system must continue to return insufficient evidence. Policy values are an
engineering baseline, not calibrated profitability claims. Candidate evaluation,
selection, alternative ranking and complete A6 run replay belong to A6.2;
publication belongs to A6.3 and final hardening to A6.4.
