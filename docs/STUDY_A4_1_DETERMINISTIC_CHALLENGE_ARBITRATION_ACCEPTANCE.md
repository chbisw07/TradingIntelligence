# Study — TIAF_A4.1 Deterministic Challenge and Arbitration Acceptance

**Date:** 2026-09-11 (Asia/Kolkata)

**Base:** `4556c3c`, accepted `POST_A3_PRE_A4_LOCAL_FACADE` implementation.

**Scope:** immutable A4 contracts, deterministic thesis/Challenger/Arbitrator,
policy, disposition/failure semantics, capture/replay/verification/comparison,
and a stable same-process `a4.evaluate` facade capability. No live, provider,
model, evidence-acquisition, broker, A5, A6 or A7 call was authorized.

## Acceptance scenario evidence

| # | Required scenario | Observed acceptance |
| ---: | --- | --- |
| 1 | Clean `OPPORTUNITY` | `SUPPORTIVE`, `COMPLETE`, surviving primary thesis |
| 2 | Critical source weakness | `SOURCE_BASIS` challenge and `INSUFFICIENT_EVIDENCE` |
| 3 | Copied-source dependence | dependence remains a cited material challenge |
| 4 | Stale catalyst | `FRESHNESS` challenge and `WAIT`, not factual conflict |
| 5 | Positive context plus poor timing | timing counter-thesis and `WAIT`, not factual conflict |
| 6 | Authoritative comparable conflict | two supported theses retained as `CONFLICTED` |
| 7 | A2 `NO_TRADE` plus A3 support | `NO_TRADE`; A3 support premise remains visible |
| 8 | Missing required evidence | `INSUFFICIENT_EVIDENCE` plus placeholder need |
| 9 | Unsupported assumption | `ASSUMPTION_SUPPORT` challenge and `ABSTAIN` |
| 10 | Supported counter-thesis | explicit counter retained and `CONFLICTED` |
| 11 | No supported thesis / unresolved required rule | `PARTIAL`/`ABSTAIN` with typed `UNRESOLVED_REQUIRED_RULE` failure |
| 12 | Deterministic risk veto | `AVOID`, with no sell instruction |
| 13 | Resolved scope mismatch | resolved non-material findings; not `CONFLICTED` |
| 14 | Projection-only A2 | uncaptured factual premise rejected |
| 15 | Unchanged deterministic rerun | identical result and run fingerprints |
| 16 | Policy-version change | explicit non-replay comparison and new run identity |
| 17 | Recorded replay | exact reconstruction and verification with socket blocked |
| 18 | Corrupt parent/capture | checksum/fingerprint integrity failure, no repair |
| 19 | Challenger failure | `PARTIAL`/`ABSTAIN`; no favorable fallback |
| 20 | Arbitrator failure | exception and no valid disposition/result |
| 21 | `SUPPORTIVE` action boundary | no buy/sell/action/execution approval |
| 22 | No expression fields | no CE/PE/strike/expiry/quantity/stop/target contract fields |
| 23 | No probability | no probability or universal confidence field |
| 24 | Import boundary | no provider/model/broker/remote/future-layer import |
| 25 | Facade parity | `a4.evaluate` equals direct evaluation/fingerprint with zero external usage |

Additional coverage proves frozen tuple-backed/JSON-array contracts, clean model
reconstruction, aware Asia/Kolkata timestamps, hypothesis-to-fact rejection,
premise dependency-cycle rejection, unchanged serialized input, optional-gap
preservation, output-fingerprint rejection, unsupported-policy rejection,
thesis-construction failure, secret-free captures, facade admission binding and
the absence of caller-injected policy.

## Policy and semantic observations

- The eight challenge families are closed and separately typed from severity,
  materiality and challenge status.
- Arbitration is an ordered rule system with one finding per issue. No vote,
  confidence average, scalar trust or source-brand winner exists.
- Exactly one primary thesis and no more than one evidence-backed counter-thesis
  are constructed. No counter is manufactured for a clean case.
- `NO_TRADE`, `AVOID`, `INSUFFICIENT_EVIDENCE`, `ABSTAIN`, `CONFLICTED`, `WAIT`
  and `SUPPORTIVE` remain distinct from `COMPLETE`, `PARTIAL` and `FAILED`.
- Original A2/A3 references and fingerprints remain unchanged and visible.
- Evidence needs are typed `PLACEHOLDER_ONLY`; there is no acquisition bridge.
- Model/provider calls, input/output tokens and model cost are exactly zero.
  Inherited parent cost knowledge remains attributable rather than relabeled.

## Replay and security observations

Captured replay validates exact projection/run checksums, semantic fingerprints,
input equality, policy support and content-derived identities. Recorded replay
does not rerun policy. Deterministic verification reruns only the captured
provider-free projection and policy. Policy comparison creates a successor run
and never masquerades as exact replay. Tests block socket connection to prove
there is no network repair path.

The `tiaf.a4` AST has no provider/model/broker/HTTP/gRPC/database imports or
future-layer classes. Captures contain no credentials or execution authority.
The facade accepts logical authorized artifacts only and exposes no policy,
filesystem path, URL, provider, router or registry field.

## Validation results

The final gate results are recorded after execution:

- A4 suite: `37 passed`;
- facade suite: `42 passed`;
- source-semantics suite: `27 passed`;
- opportunity-intelligence suite: `65 passed`;
- A3-hardening suite: `61 passed`;
- agents suite: `270 passed`;
- workflows suite: `42 passed`;
- full suite: `2027 passed`;
- `python -m compileall src scripts`: pass;
- `ruff check src tests scripts`: pass;
- `mypy src tests`: success across 484 source files;
- `python -m pip check`: no broken requirements (pip cache ownership warning only);
- documentation links: 462 local Markdown targets checked, none missing;
- scoped secret-assignment scan: no match;
- provider/model/broker/remote/future-layer import and expression-field scans:
  pass;
- A2/A3/source/foundation frozen-path diff: empty;
- replay isolation with socket connection blocked: pass;
- `git diff --check`: pass.

No live or model call is part of this acceptance.

## Residual risks and next boundary

The policy is intentionally a generic deterministic benchmark. It only
arbitrates reason forms represented in the captured projection; novel questions
abstain rather than being inferred from prose. Source qualification materiality
is conservative, and the comparison-only policy version changes identity rather
than claiming improved investment quality. This slice is not evidence that the
policy is profitable or calibrated.

The next bounded implementation candidate is the governed bridge from typed A4
evidence needs to already accepted Planner/gateway admission and a successor
projection. It requires a separate authorization and must preserve offline
replay, cutoff semantics, budgets and provider-neutral routing.

**Decision:** `READY_TO_ACCEPT_A4_1`.
