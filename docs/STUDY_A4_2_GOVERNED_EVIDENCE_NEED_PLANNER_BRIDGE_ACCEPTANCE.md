# Study — TIAF_A4.2 Governed Evidence-Need / Planner Bridge Acceptance

## Scope and result

This study records offline acceptance of the one-round `tiaf.a4_enrichment`
application bridge. Inputs are synthetic, captured and attributable; they are
not policy calibration or live-market evidence. The tests execute a captured
fixture provider and an offline authoritative-confirmation adapter through the
real A3.8 route; no live/external provider, model, network, broker, order or
trade operation was performed.

The tests execute the real A3.8 serial coordinator and, when the pinned optional
dependency is installed, its LangGraph adapter. They use captured services only.
The final quality-gate counts below are updated from the acceptance run.

## Scenario matrix

| # | Scenario | Accepted evidence |
| ---: | --- | --- |
| 1 | Missing confirmation/material gap admitted and resolved | Later normalized evidence removes the required gap and changes `INSUFFICIENT_EVIDENCE` to `SUPPORTIVE`. |
| 2 | Confirmation/not-found equivalent | `NO_NEW_INFORMATION`; unresolved parent disposition retained. |
| 3 | Duplicate need | `DUPLICATE`, zero acquisition. |
| 4 | Unsupported capability | `UNSUPPORTED_CAPABILITY`. |
| 5 | Budget exhausted | `DENIED_BUDGET`, zero acquisition. |
| 6 | Authority denied | `DENIED_AUTHORITY`, zero acquisition. |
| 7 | Deadline exceeded | `DEADLINE_EXCEEDED`, zero acquisition. |
| 8 | Live acquisition successor time | Successor cutoff equals later acquisition time. |
| 9 | No backdating | Equal/earlier execution and malformed successor inputs fail closed. |
| 10 | Duplicate wrapper | Equivalent capture creates no successor. |
| 11 | Scope/gap resolution | Resolved gap disappears only in later successor. |
| 12 | New factual conflict | Explicit `FACTUAL_CONFLICT` is retained; no favorable assumption. |
| 13 | Partial confirmation | `PARTIAL` capture remains visible and cycle stays bounded. |
| 14 | Lower-layer refresh | Price/market-state and specialist-input classes return `UPSTREAM_REFRESH_REQUIRED`. |
| 15 | Safe context | Local successor A4 evaluation is allowed. |
| 16 | Affected finding | Originating required-gap finding is `RECOMPUTED`. |
| 17 | Unaffected finding | Unchanged exclusion finding is `PRESERVED` with parent/successor refs. |
| 18 | No information | Conservative parent disposition remains unchanged. |
| 19 | Resolving evidence | Supported fixture demonstrates a deterministic disposition change. |
| 20 | Hard `NO_TRADE` | A2 hard-gate finding remains visible; irrelevant acquisition is denied. |
| 21 | Acquisition failure | Typed failure retains original disposition and creates no successor. |
| 22 | One-round cap | Policy/contracts enforce one enrichment and one successor cycle. |
| 23 | Parent budget | Exact remaining grant budget is carried; it is not reset. |
| 24 | Serial/LangGraph parity | Semantic workflow payload, accounting and stop behavior agree. |
| 25 | Recorded replay | Exact chain replay reports zero provider/model calls. |
| 26 | Missing/corrupt replay | Checksum/contract validation fails closed. |
| 27 | Policy change | New policy identity creates distinct admission/comparison identity. |
| 28 | No LangChain | Dependency/import scan passes. |
| 29 | Domain LangGraph boundary | A4/source/facade contracts contain no LangGraph import. |
| 30 | No model | A4.2 contracts reject nonzero model calls/tokens. |
| 31 | No A5/A6/A7 | Application source has no later-phase runtime dependency. |
| 32 | No broker authority | Need/application contracts expose no broker/order/trade authority. |

Additional coverage verifies frozen/list-to-tuple/JSON-array contracts,
Asia/Kolkata timestamps, parent ownership, entitlement/profile denial, A2
fingerprint preservation, workflow crosswalk integrity, parent immutability,
chain tamper detection and deterministic verification.

## Acceptance observations

- The source-semantic successor reuses the exact frozen A2/A3 package identities.
- The original projection/result JSON is byte-for-byte unchanged after successor
  construction.
- The real A3.8 coordinator records zero model calls/tokens and no hidden retry.
- Serial and LangGraph records differ only in operational adapter/runtime data;
  their semantic payloads agree.
- Recorded replay has no registry, service, router, provider, model or network
  argument and cannot initiate live fallback.
- A4.2 is deliberately not exposed through the captured-read-only facade.

## Validation result

Acceptance was run on 2026-09-11 (Asia/Kolkata):

| Gate | Result |
| --- | --- |
| Dedicated `tests/unit/a4_enrichment` | 44 passed |
| Combined A4.1/A4.2 | 81 passed |
| Required cross-package focused set | 737 passed |
| Full repository `pytest -q` | 2,071 passed |
| `python -m compileall -q src scripts` | Passed |
| `ruff check src tests scripts` | Passed |
| `mypy src tests` | Passed — 497 source files |
| `python -m pip check` | Passed — no broken requirements |
| `git diff --check` | Passed |
| Documentation-link, secret-pattern and import-boundary checks | Passed |

No live/external provider or model calls were made. The optional installed
LangGraph adapter was exercised only with captured services; recorded replay
used no service, provider, model or graph adapter.

## Decision boundary

Acceptance requires every focused/full test and compile, lint, type, package,
documentation-link, secret, dependency/import and diff check to pass. Any
remaining correctness, authority, replay, accounting or boundary failure changes
the milestone decision to `HOLD_A4_2`.
