# Study — TIAF A3.10 User-Level Acceptance

## Scope and provenance

Run on 2026-09-10 in Asia/Kolkata against architecture baseline
`tiaf-a3.10-arch` and frozen runtime baseline `tiaf-a3.9`. This was a bounded,
offline acceptance. It made no live provider, broker, model, network, or
execution call and did not read `.env`. All public corpus cases are explicitly
`SYNTHETIC` with fixture builder `a3.10-public-fixtures/1.0`; accepted persisted
A3.8/A3.9 captures are reused where available.

## Command and result

```bash
.venv/bin/python scripts/a3_10_user_acceptance.py
```

Result: `PASS: 14 / FAIL: 0`.

| Case | Evidence exercised | Result |
|---|---|---|
| A | Clean aligned package | Recorded replay, aligned axes, leaf reconciliation passed |
| B | A2 `NO_TRADE`, A3 `WATCH` | Both values retained; permissive divergence is observational |
| C | Constructive A2, A3 `WAIT` | Timing restriction and reason lineage retained |
| D | Conflict capture plus neutral-axis probe | Conflict remains visible; neutral/MIXED is non-comparable, no winner |
| E | Sparse KAYNES fixture | `INSUFFICIENT_EVIDENCE`, gaps and prerequisites retained |
| F | Deterministic Tapetide rate-limit/Yahoo fallback fixture | Both provider attempts, failure lineage, fallback and leaf charging retained |
| G | Unknown-applicability partial capture plus optional-failure probe | Surviving evidence remains visible; no complete-state fabrication |
| H | Required downstream abstention | Required restriction produces insufficient evidence |
| I | Deterministic budget denial | `BUDGET_EXHAUSTED`, zero post-denial provider work, ledger retained |
| J | Byte-level tamper | Rejected before reconstruction |
| K | Unsupported policy version | Rejected as historical replay; explicit comparison API remains separate |
| L | Serial/LangGraph operational variants | Equal semantic package/comparison/cost/failure identities, unequal exact checksums |
| M | Provider attempts without monetary price source | `UNPRICED`, never numeric zero |
| N | No-LLM capture | Zero calls/tokens and `KNOWN_ZERO` model monetary cost |

Case D does not relabel the directional persisted conflict fixture as neutral;
the neutral mapping is an explicit typed axis probe. Case G does not relabel
unknown F&O applicability as a child exception; optional-failure losslessness is
proved by the deterministic failure fixture/unit boundary. These distinctions
avoid manufacturing provenance merely to make a scenario label look exact.

## Replay and integrity observations

- Manifest plus three content-addressed blobs round-trips through portable and
  directory forms with the same semantic identity.
- Exact bytes, byte lengths, blob paths, package checksum, child capture
  checksums/fingerprints, subject/horizon/as-of, A2 identity, and A3.8/A3.9 links
  validate before reconstruction.
- `FULL_BASELINE_CASE` re-executes accepted A2 deterministic policy when its
  identity matches; `ORIGINAL_A38_PROJECTION` honestly reports A2 verification
  as not applicable.
- Synthetic precomputed specialist output is recorded-only. A3.9 pure assembly
  is deterministically re-executed. Future model-backed output is recorded-only;
  invalid/incomplete model provenance is rejected by existing opinion contracts
  before package capture.
- Recorded replay and observational comparison pass with socket, provider
  router, specialist runtime, and coordinator entry points replaced by failure
  guards. No missing artifact falls through to acquisition.

## Cost and failure observations

A3.8 reservations are the debit leaves. Their captured actuals reconcile exactly
to original usage; MI provider-attempt detail is linked but excluded from the
original total to avoid double debit. Replay execution use is separate. Failed,
rate-limited, fallback, reused, and held semantics remain explicit. Configured
cost units are not treated as money. Provider/model money is `KNOWN_ZERO`,
`KNOWN_NONZERO`, `UNKNOWN`, `UNPRICED`, or `NOT_APPLICABLE`; absent pricing never
becomes zero.

The failure projection preserves normalized category/code plus original child
type/code/message digest, provider/specialist/node/attempt/artifact identifiers,
usage links, terminality, and affected capabilities. The checked-in fault matrix
contains 22 versioned synthetic cases and never manufactures a live outage.

## Claims and limitations

This acceptance proves deterministic replay/integrity, observational A2/A3
comparison, accounting/failure truth, offline isolation, and closure-evidence
composition. It does not prove live provider availability, predictive value,
profitability, model determinism, operational disaster recovery, or production
SLOs. It does not perform A3 major closure. Database/distributed corpus,
arbitrary historical reconstruction, scheduled outcome acquisition, A4
arbitration, A5 position actions, A6 expression, A7 forecasting/evaluation, A8
integration, A9 scanning, and A10 operations remain outside A3.10.

## Validation evidence

| Gate | Result |
|---|---|
| `.venv/bin/pytest -q tests/unit/agents tests/unit/market_intelligence tests/unit/planner tests/unit/workflows tests/unit/opportunity_intelligence` | 554 passed in 35.37s |
| `.venv/bin/pytest -q tests/unit/a3_hardening` | 61 passed in 70.36s |
| `.venv/bin/pytest -q` | 1,921 passed in 112.44s |
| `.venv/bin/python -m compileall -q src scripts` | Passed |
| `.venv/bin/ruff check src tests scripts` | All checks passed |
| `.venv/bin/mypy src tests` | No issues in 445 source files |
| `.venv/bin/python -m pip check` | No broken requirements; non-blocking pip-cache permission warning |
| `git diff --check` | Passed |
| Changed-document relative links | 107 checked; none missing |
| Scoped source/fixture secret scan | Passed |

The tested closure-readiness constructor returns `READY_FOR_CLOSURE_REVIEW`
only when every required evidence item is `PASS`; required `UNKNOWN` produces
`NOT_READY`. This is evidence for the later human closure decision, not closure
itself.
