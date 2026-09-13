# TIAF A6.1 — Contracts, Admission & Policy Foundation

Status: **ACCEPTED / DONE** on 2026-09-13
(Asia/Kolkata). A6.2 is **ACTIVE / NEXT** and `expression.assess` is
**NOT_PUBLISHED**.

## Scope and authority

A6.1 answers one question only:

> Is this typed request and captured evidence admissible for later A6 evaluation
> under this exact versioned policy?

It does not choose, rank, recommend, size, route or execute an option. A4 still
owns thesis validity; A6 owns advisory expression suitability; TM owns account,
risk, capital, quantity and action-time validation; the broker owns orders, fills
and positions. No A6.1 contract contains account, capital, final quantity, order,
route, stop, target or consent fields.

The implementation is isolated in `src/tiaf/trade_expression/`:

| Module | Responsibility |
|---|---|
| `contracts.py` | Immutable schema-1.0 request, timing, identity, evidence, coverage, event, policy, spread and admission-result contracts; canonical serialization/fingerprints |
| `enums.py` | Closed direction, horizon, coverage, timing, event, spread, outcome and error vocabularies |
| `policy.py` | Pinned baseline policy, preference validation, listed-strike geometry and spread primitives |
| `admission.py` | Pure captured-input A4/request/evidence admission and deterministic replay verification |
| `errors.py` | Typed malformed-contract/configuration and replay-integrity errors |

There are no provider, model, optional-adapter, specialist, broker, facade or
Shell imports. Provider/model usage in `AdmissionResult` is constrained to zero.

## Request, direction and horizon

`TradeExpressionRequest` is frozen, forbids extra fields, and carries schema and
version, logical request/run identity, CAPTURED/REPLAY intent, provider-neutral
subject, objective, BULLISH/BEARISH direction, exact evaluation cutoff, A4 and
derivative-capture identities/fingerprints, exact policy/profile identity,
bounded preferences, authority and optional correlation/source lineage.

`ExpressionHorizon` is DAY or POSITIONAL and carries both a future target instant
and its exact elapsed duration in Decimal seconds. The request validates that the
two representations agree. Label-only terms such as “intraday”, “BTST” or “three
weeks” are invalid at this core boundary. DAY additionally requires a captured,
sourced session containing cutoff and target. POSITIONAL is bounded by the
policy's explicit 90 × 24-hour maximum.

All datetimes use the repository `TiafDateTime`: naive values are rejected and
aware values are normalized to `ZoneInfo("Asia/Kolkata")`. Normalization does not
turn an unqualified timestamp into an authoritative market timestamp.

## Timing and expiry qualification

`MarketTimingQualification` keeps `observed_at` separate from `acquired_at` and
states its freshness basis and qualification source. Acquisition-only evidence
has no authoritative observation time and cannot pass the strict freshness gate.
Observation cannot follow acquisition, and evidence unavailable at the explicit
evaluation cutoff is rejected.

`ExpirationTiming` keeps expiry date, qualified expiration instant, qualification
source and optional sourced trading cutoff distinct. DATE_ONLY and UNKNOWN cannot
carry an expiration instant. The code does not invent an exchange cutoff.

## Neutral option identity and evidence

`OptionContractIdentity` describes an NSE F&O CE/PE using provider-neutral
subject/class, strike and expiry, with optional captured native-instrument and lot
metadata plus provenance. Its stable identity fingerprint uses the neutral
contract geometry, not a provider alias. CE/PE, strike and expiry changes alter
identity; a provider-native identifier change does not.

`OptionQuoteEvidence` preserves bid, ask, top bid/ask quantities, INR price units,
quantity units, qualified timing, optional LTP/OI/volume, optional admitted IV
with explicit provider unit semantics/evidence, optional admitted Greeks and
provenance. Decimal values avoid binary-float ambiguity. Missing book
values remain `None`; factual zero OI and volume remain zero. Crossed books are
malformed. LTP never supplies a missing bid or ask and Greeks are never derived.

`ExpiryChainEvidence` and `DerivativesEvidenceCapture` are bounded to 512 quotes
per chain and three expiries per capture. They validate subject/expiry membership,
unique identities, counts and canonical order. This is captured evidence for
A6.2, not candidate selection.

## Coverage and event absence

`CoverageProof` uses exactly:

- PRESENT — qualified, complete, non-empty scope;
- CONFIRMED_EMPTY — qualified, complete, explicitly empty scope;
- PARTIAL — checked but incomplete scope;
- UNAVAILABLE — acquisition unavailable;
- UNKNOWN — qualification unknown.

An empty list with UNKNOWN or UNAVAILABLE coverage is not upgraded to
CONFIRMED_EMPTY. Complete states require a scope reference, expected/observed
counts, qualification source and evidence references.

`EventEvidenceWindow` separately represents a qualified known material blocker,
a qualified proof of no intersecting event, or unknown coverage. Scheduled event
time may correctly follow acquisition/publication time. A no-event conclusion
requires complete `CONFIRMED_EMPTY` coverage of the declared interval; missing
event evidence remains unknown. A known blocker is captured for the A6.2 event
gate and does not itself manufacture a recommendation or probability.

## Pinned baseline policy

`deterministic-long-option` version `1.0-draft`, profile `baseline`, records all
reviewed engineering values as immutable policy data. It also pins the
`admission-foundation/1.0` evaluator and `canonical-contracts/1.0` normalizer;
these identities remain separate from the policy content fingerprint:

| Policy item | Baseline |
|---|---:|
| Subject/horizon scope | NSE equity/index; DAY/POSITIONAL |
| Expiry/chain/evaluation bounds | 3 expiries; 512 strikes each; 9 later candidates |
| Strike neighborhood | ATM, ITM1, OTM1 |
| Quote and spot maximum age | 60 seconds each, qualified observation time |
| Upstream maximum age | DAY 15 minutes; POSITIONAL 24 hours |
| Target-to-expiry cushion | DAY 24 hours; POSITIONAL 72 hours |
| POSITIONAL target maximum | 90 × 24 hours |
| Book | finite `ask >= bid > 0`; positive captured top quantities |
| Hard relative spread | 500 bps |
| Spread tiers | tier 0 `<= 100`; tier 1 `> 100 and <= 500` bps |
| Future output bound | one preferred plus at most two alternatives |
| Own provider/model calls | 0 / 0 |

These are transparent generic engineering defaults, not calibrated trading
truths. The only caller preferences are a closed non-empty ATM/ITM1/OTM1
restriction/order, an explicit per-unit INR premium cap and an event-clear
requirement. They can only narrow policy and never bypass hard gates. Cheapest,
longest-expiry, weighted rules, callbacks and DSL expressions are rejected.

## Geometry and spread foundations

`resolve_moneyness_geometry` validates strictly increasing unique listed strikes,
chooses the nearest ATM strike with the lower strike on an exact tie, then uses
actual adjacent strikes. CE uses lower/higher neighbors for ITM1/OTM1; PE reverses
them. It invents no spacing and makes no delta claim.

`assess_spread` distinguishes missing inputs, non-positive bid, invalid/crossed
ask, missing or zero top depth, spread above the hard limit, and the two eligible
tiers. It computes exact Decimal absolute spread, midpoint and
`10000 × spread / midpoint` bps. It does not rank or select candidates.

## A4 admission and outcomes

Admission validates policy, capture, subject/objective/cutoff and fingerprint
relationships before using the existing A4 contracts. Only an A4 result with:

- `A4ExecutionStatus.COMPLETE`;
- `A4Disposition.SUPPORTIVE`;
- a surviving primary thesis;
- `ThesisSupport.SUPPORTED`; and
- directional interpretation `POSITIVE` or `NEGATIVE`, agreeing with the request

can proceed. POSITIVE resolves to BULLISH and NEGATIVE to BEARISH. NO_TRADE,
AVOID, WAIT and CONFLICTED are rejected upstream. ABSTAIN, INSUFFICIENT_EVIDENCE
and incomplete execution remain insufficient. Conditional/refuted/undetermined,
non-surviving or directionless primaries do not proceed.

Normal results use `ADMITTED`, `REJECTED_UPSTREAM`, `INSUFFICIENT_EVIDENCE`,
`UNSUPPORTED` or `INVALID_REQUEST`; normal domain states are never exceptions.
Malformed requests, horizons, preferences, policies, quotes, timing, coverage or
replay integrity use typed A6 error codes/exceptions.

## Determinism and replay

Collections representing semantic sets are normalized to duplicate-free stable
order. Decimal, enum, date and Asia/Kolkata datetime content has canonical JSON.
Semantic fingerprints reject credential-shaped keys/text and local filesystem
paths rather than persisting them. Result IDs are content-addressed without a
self-hash cycle.

`verify_admission_replay` validates the recorded result, reruns admission over the
same captured request, A4 result, evidence and policy, and requires an exact
semantic fingerprint match. It reads no wall clock, environment, network,
provider registry or fallback path.

## Compatibility and deferred work

- R1–R5 composition/discovery/import/configuration behavior is unchanged.
- The public facade catalog remains eight operations.
- `expression.assess` is not registered and no Shell command exists.
- A5 runtime, `position.assess`, A5 replay and A5 fingerprints are unchanged.
- No source limitation is hidden: acquisition-only quote time, date-only expiry,
  incomplete coverage and unknown event coverage remain insufficient/unqualified;
  confirmed-empty qualified event coverage cannot be mislabeled unknown.
- Candidate construction, gate evaluation, deterministic ranking, preferred and
  alternative selection, complete A6 assessment/run records and A6.2 replay are
  **NOT_IMPLEMENTED** and remain the A6.2 scope.
- Live acquisition, A6.3 facade/Shell publication, TM handoff, broker authority,
  A7 forecasts and multi-leg/short-option strategies remain outside A6.1.

Accepted by
[TIAF A6.1 acceptance](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION_ACCEPTANCE.md).
Next prompt: `TIAF A6.2 — CANDIDATE EVALUATION, RANKING & REPLAY`.
