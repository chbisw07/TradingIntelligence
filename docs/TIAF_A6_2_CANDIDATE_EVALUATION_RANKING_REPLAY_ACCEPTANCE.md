# TIAF A6.2 — Candidate Evaluation, Ranking & Replay Acceptance

## Decision and boundary

**READY_TO_CLOSE_A6_2** — independently accepted on 2026-09-13
(Asia/Kolkata).

- A6 architecture: **ACCEPTED**.
- A6.1 contracts/admission/policy: **ACCEPTED / DONE**.
- A6.2 candidate evaluation/ranking/replay: **ACCEPTED / DONE**.
- A6.3 facade and TI Shell exposure: **ACTIVE / NEXT**.
- A6.4: **NOT_IMPLEMENTED**.
- `expression.assess`: **NOT_PUBLISHED**; the public catalog remains exactly
  eight operations.
- A5 remains frozen at `tiaf-a5-baseline`; R1–R5 remain accepted/done.
- No live provider, model, broker, facade, Shell, Web, TM or A7 behavior was
  added or invoked by this acceptance.

The next prompt is exactly:
`TIAF A6.3 — FACADE & TI_SHELL EXPOSURE`.

## Independent semantic review

| Area | Verdict | Evidence / conclusion |
|---|---|---|
| Candidate universe | ACCEPT | Admitted BULLISH produces only long CE and BEARISH only long PE. Up to three captured expiries contribute actual listed ATM/ITM1/OTM1 contracts, bounded to nine evaluations. Missing neighbours are not synthesized and canonicalized chain/quote order fixes the universe. |
| Expiry | ACCEPT | Chain and quote expiration facts must agree exactly. Qualified expiration instants are required by the pinned policy; date-only evidence cannot pass. Residual life is exact expiration minus intended exit, with inclusive minimum and optional maximum owned by policy. Duplicate expiry dates and incoherent contract identities fail closed. |
| Strike geometry | ACCEPT | ATM is nearest listed strike with an exact midpoint tie resolved to the lower strike. ITM1/OTM1 are actual adjacent strikes with correct CE/PE orientation. Irregular grids work without interval or delta inference. |
| Candidate contract | ACCEPT | Frozen schema-1.0 candidate/evaluation contracts retain neutral contract identity, direction/LONG side, geometry, all gates, spread, eligibility, reason codes, rank facts, invalidations, evidence/policy references and semantic fingerprint. Event and global evidence conclusions remain assessment-level. No execution authority fields exist. |
| Gate semantics | ACCEPT | Every candidate records the complete canonical order: identity/membership, timing/freshness, horizon fit, quote geometry, top depth, spread and premium cap. All gates are evaluated; FAIL and UNKNOWN remain distinct. TF-05 early termination remains deferred and UNKNOWN anywhere prevents a final selection. |
| Liquidity | ACCEPT | Bid/ask and positive top quantities are required. Missing operands are UNKNOWN; known invalid/crossed geometry and zero depth are FAIL. Acquisition-only or stale timing cannot establish current suitability. Zero OI/volume remain factual zero and are not hard gates; LTP is not substituted. |
| Spread | ACCEPT | The A6.1 `Decimal` primitive supplies absolute spread, midpoint and bps. The 500-bps hard limit controls eligibility; the 100-bps inclusive tier boundary affects ranking only after eligibility. No display rounding, float score or fill-probability claim is used. |
| Premium cap | ACCEPT | The optional hard cap compares the captured ask in INR per unit. Equality passes, above fails and missing ask is UNKNOWN. No lot multiplication, account affordability, capital sizing or cheapest-first rule appears. |
| Events | ACCEPT | A qualified relevant material event in `(cutoff, target]` yields WAIT, including the target boundary and excluding cutoff. Qualified clear evidence may continue; unresolved relevant/material timing remains insufficient. Complete holding-window proof is required when event-clear is requested. No research or model call occurs. |
| Coverage / absence | ACCEPT | PRESENT, CONFIRMED_EMPTY, PARTIAL, UNAVAILABLE and UNKNOWN remain distinct. Only complete qualified CONFIRMED_EMPTY scope proves no listed expiry. Missing chain scope or any UNKNOWN required selected candidate fact cannot become NO_OPTION_TRADE. |
| Dispositions | ACCEPT | AVAILABLE requires a survivor and complete deterministic rank; NO_OPTION_TRADE requires complete bounded facts or a separately recorded upstream prohibition; WAIT is a known temporary blocker; INSUFFICIENT represents inadequate qualification/scope; UNSUPPORTED represents a well-formed request beyond v1. Operational failures remain typed exceptions. |
| Ranking | ACCEPT | Eligible candidates sort lexicographically by `(spread_tier, requested_moneyness_rank, expiry_cushion_excess_seconds, exact_spread_bps, canonical_contract_key)`. Smaller cushion excess is intentionally the earliest already-suitable expiry, consistent with the architecture's later tie-break and not nearest-expiry admission or longest-expiry optimization. Stable neutral keys close exact ties. No weighted score, expected return, probability, delta/IV or learned optimizer exists. |
| Preferences | ACCEPT | Only moneyness restriction/order, per-unit premium cap and event-clear are admitted. They narrow the pinned baseline and cannot override a hard gate. |
| Shortlist | ACCEPT | AVAILABLE has exactly one preferred candidate and at most two next-ranked eligible alternatives. All bounded candidate evaluations, including rejected and eligible-not-selected records, remain captured. |
| Assessment | ACCEPT | Frozen schema-1.0 assessment retains request/admission identities, disposition, shortlist, every evaluation, blockers/gaps, structured explanation, invalidations, request/A4/evidence/policy pins, composition references, zero usage and semantic fingerprint. It has no account, quantity, route, order type, execution consent or executable intent. |
| Explainability | ACCEPT | Stable disposition, gate, rejection and uncertainty codes answer why selected/rejected/waiting/insufficient/no-trade; rank differences record the first unequal dimension; evidence/policy references and invalidations state what facts support or can change the result. Canonical explanation is deterministic, not model-generated. |
| Replay | ACCEPT | Recorded candidate/evaluation/assessment identities are validated and the full result is recomputed from exact captured request, A4 result, evidence, policy, admission and composition references. Socket-denial coverage proves no wall clock, provider, network or current registry expansion is consulted. |
| Input-order invariance | ACCEPT | Contracts canonicalize chain and quote rows; reversed equivalent chain/row order produces identical evaluations, shortlist, assessment and semantic fingerprint. |

No implementation defect was found and no runtime code was changed by this
acceptance pass.

## Boundary and compatibility verdicts

| Gate | Verdict |
|---|---|
| A4 | INTACT — A6.2 first verifies exact A6.1 admission replay. Rejected, unresolved or conflicting upstream states cannot be rescued by option evidence. |
| A5 | INTACT — no A5 source/test diff exists against `tiaf-a5-baseline`; no auto-roll, mutation or expression refresh orchestration was added. |
| A7 | INTACT — no forecast, probability, expected return, learned ranking or model usage exists. |
| R1 | INTACT — required/optional scope and explicit-absence regression passes. |
| R2 | INTACT — catalog is exactly eight operations and contains no `expression.assess`. |
| R3 | INTACT — existing composition and pinned verifier behavior is unchanged; A6 accepts optional captured composition references without registry lookup. |
| R4 | INTACT — no optional provider/model integration import enters trade-expression core. The only cross-package imports are stable internal contracts/A4/hash types. |
| R5 | INTACT — no startup selector, ownership mutation or HOT behavior was added. |
| A6.3 | **A6_3_BOUNDARY_PRESERVED** — no descriptor registration, facade handler, Shell command, Web/API endpoint, provider integration or TM integration exists. |

## Deferral and navigation review

No deferred item was silently closed or removed. TF-05 remains deferred with
the full-window evidence rule intact. Live authoritative quote/expiration/session
availability, richer strategies, A7-informed ranking, TM/broker integration and
publication remain under their existing future owners. A6.2 introduced no new
unresolved issue requiring a deferral ID.

README and roadmap navigation retain separate R1–R5 rows and visible A7–A10
milestones. Closure advances only A6.2 to accepted/done and A6.3 to active/next;
A6.4 remains not implemented and publication remains absent.

## Validation evidence

All commands used captured/synthetic repository evidence and made no live calls.

| Gate | Result |
|---|---:|
| `pytest -q tests/unit/a6` | **99 passed** |
| `pytest -q tests/unit/a4` | **37 passed** |
| `pytest -q tests/unit/a5` | **52 passed** |
| `pytest -q tests/unit/facade` | **71 passed** |
| `pytest -q tests/unit/shell` | **89 passed** |
| R1–R5 focused regression | **93 passed** |
| `pytest -q` | **2,419 passed in 232.22s** |
| `python -m compileall src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS — 559 source files |
| `python -m pip check` | PASS — no broken requirements |
| `uv lock --check` | PASS — 71 packages resolved |
| `git diff --check` | PASS |

Additional verification confirms exact eight-operation catalog parity, A5 tag
parity, socket-denied replay, absence of facade/Shell publication, no forbidden
optional runtime imports, no recorded secrets, valid documentation links,
sequential deferral identities and README A0–A10 visibility.

## Residual risks

A6.2 evaluates only captured, qualified inputs. Live sources may still lack the
authoritative observation, session or expiration facts required by its strict
policy; the correct result then remains insufficient evidence. The baseline
thresholds are transparent engineering policy, not profitability calibration.
A6.3 must separately govern publication, authority, logical-artifact admission,
COLD composition and Shell rendering without weakening this internal result.
