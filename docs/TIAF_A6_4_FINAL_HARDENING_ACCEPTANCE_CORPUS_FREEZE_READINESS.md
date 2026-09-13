# TIAF A6.4 — Final Hardening, Acceptance Corpus & Freeze Readiness

## Decision

**READY_TO_FREEZE_A6** — A6.4 completed on 2026-09-14
(Asia/Kolkata).

A6.1–A6.4 are accepted/done, `expression.assess` remains the ninth governed
captured-read capability, and A6 meets the documented baseline-freeze criteria.
This record recommends but does not create the `tiaf-a6-baseline` tag. A6 is
**READY_TO_FREEZE**, not yet frozen. A7 is next and was not started.

Recommended closure operations, only after explicit authorization:

```text
commit: feat(a6.4): harden and close trade expression intelligence
tag:    tiaf-a6-baseline
```

Next prompt:
`TIAF A6 — FINAL FREEZE / TAG CLOSURE`.

## Acceptance corpus

The machine-readable
[manifest](../tests/acceptance/a6/corpus_manifest.csv) contains exactly 93
contiguous case IDs with scenario, expected result, policy/profile, fixture or
logical artifact, test location and category. Its
[corpus guide](../tests/acceptance/a6/README.md) records category counts and
execution rules. No case is left as implicit coverage.

| Category | Cases |
|---|---:|
| Upstream admission | 8 |
| Timing/freshness | 9 |
| Coverage/absence | 6 |
| Candidate geometry | 9 |
| Liquidity/quote quality | 13 |
| Premium | 4 |
| Events | 6 |
| Ranking | 8 |
| Dispositions | 5 |
| Alternatives/evaluation retention | 4 |
| Replay/integrity | 8 |
| Public surface | 13 |
| **Total** | **93** |

Five semantic [public goldens](../tests/acceptance/a6/golden_public_results.json)
exercise EXPRESSION_AVAILABLE, NO_OPTION_TRADE, WAIT_FOR_EXPRESSION,
INSUFFICIENT_EVIDENCE and UNSUPPORTED through Shell → facade → admitted captured
artifact → A6 assessment. They assert shortlist, decisive rank dimensions,
candidate rejection reasons, blockers/gaps, invalidations, exact recorded
fingerprint equality, full JSON reconstruction, explain/trace lineage and
recorded replay without snapshotting irrelevant run IDs, elapsed time or human
formatting.

## Hardening findings and fixes

The corpus found one public-input defect: Shell's generic non-path token check
accepted `--input not-qualified`, despite promising a qualified logical artifact
ID. The artifact option now validates the existing `QualifiedId` contract before
facade invocation. Valid logical references and all facade/domain semantics are
unchanged.

The pass also closed bounded acceptance gaps without changing A6 policy:

- added the fifth public UNSUPPORTED capture and rendering/replay coverage;
- added disposition-specific deterministic operator wording so WAIT is clearly
  temporary, INSUFFICIENT is not a negative opinion, NO_OPTION_TRADE is
  conclusive for the captured scope and UNSUPPORTED is not a market view;
- isolated exact event cutoff/target/outside-window behavior, 501-bps spread,
  each zero-depth side, missing optional OI/volume, missing ITM/OTM neighbours,
  duplicate identity, survivor counts and the final two rank-key dimensions;
- persisted one exact capture and replayed the same bytes in subprocesses with
  three Python hash seeds, UTC process timezone and altered current-policy/
  registry-like environment values. Every replay returned its recorded semantic
  fingerprint. Rebuilding upstream synthetic fixtures may legitimately create a
  different capture identity; exact persisted replay does not.

No threshold, gate, rank order, admission rule, disposition meaning, domain
schema, fingerprint algorithm or A6.1–A6.3 authority was retuned.

## End-to-end and rendering verdict

```text
structured Shell command / REPL
        ↓
governed expression.assess facade admission
        ↓
trusted captured A6 envelope + verified A4 admission
        ↓
accepted deterministic evaluation/ranking
        ↓
TradeExpressionAssessment
        ↓
human / exact JSON / explain / trace / recorded replay
```

The public path is captured-input-only. AVAILABLE shows preferred and at most
two alternatives, decisive rank differences, policy, rationale and
invalidations. NO_OPTION_TRADE shows complete hard-gate rejection rather than
insufficiency. WAIT identifies a known temporary blocker. INSUFFICIENT names
missing qualification without expressing a negative view. UNSUPPORTED names the
v1 scope limit without implying market direction. Explain/trace preserve
candidate facts and captured composition pins. Every view repeats the advisory
authority boundary; canonical JSON is the exact frozen facade/A6 result and is
not derived from human rendering.

## Replay and compatibility verdicts

| Boundary | Verdict |
|---|---|
| Replay | ACCEPT — exact recorded assessment and fingerprint; input-only capture is not called recorded replay; composition mismatch/tampering fail; socket denied; current wall clock/environment/hash seed cannot alter fixed captured semantics. |
| R1 | ACCEPT — required/optional scope and explicit absence remain distinct end-to-end. |
| R2 | ACCEPT — exactly nine unique deterministic descriptive descriptors; `expression.assess` remains CAPTURED_READ and not LIVE_READ. |
| R3 | ACCEPT — capture/composition/admission/assessment identities remain distinct; recorded replay remains registry-independent and pinned. |
| R4 | ACCEPT — optional provider/model/orchestration SDK absence does not break help, list, describe, expression assessment or replay. |
| R5 | ACCEPT — trusted startup composition remains immutable COLD ownership; no enable/disable, swap or HOT path exists. |
| A4 | ACCEPT — A4 veto/conflict/incompleteness stop A6; A6 verifies rather than repairs or recalculates upstream truth. No A4 semantics changed. |
| A5 | ACCEPT — no A5 source/test diff from `tiaf-a5-baseline`; `position.assess`, replay identity and advisory refresh semantics are unchanged. No auto-roll or A5→A6 orchestration exists. |
| A7 | ACCEPT — no probability, expected return/value, forecast, learned ranker, optimizer or model invocation drives A6 v1. |
| TM/broker | ACCEPT — no account, capital, margin, final quantity, order type/route, submit/modify/cancel, `ExecutionIntent` or position mutation. |
| Provider/live | ACCEPT — no Shell/facade provider call, enrichment or broker SDK dependency. Captured-only behavior is explicit. |
| NLP | ACCEPT — the grammar remains structured; no plain-English intent parser exists. |

`ADVISORY_ONLY_TM_RETAINS_ACTION_AUTHORITY`

`NLP_BOUNDARY_PRESERVED`

## Deferrals

No deferral was closed merely because A6 is ready to freeze. DEF-006 records
the delivered long single-leg captured baseline while retaining TF-05,
multi-leg, option-selling, futures/cross-asset and broader strategy work.
DEF-007/014 retain live session and authoritative market/expiration-time gaps;
DEF-004 retains TM integration; DEF-010 retains Monitoring Runtime; DEF-025
keeps SigmaDSL separate; DEF-044 retains A7 forecast/probability models;
DEF-054 retains NLP/Web/rich reports; and DEF-056 retains multi-leg A5 position
interpretation. HOT composition remains DEF-057.

## Validation evidence

All validation used synthetic or captured data and made no live provider, model,
TM or broker call.

| Gate | Result |
|---|---:|
| `pytest -q tests/unit/a6` | **114 passed** |
| `pytest -q tests/unit/facade` | **84 passed** |
| `pytest -q tests/unit/shell` | **106 passed** |
| `pytest -q tests/unit/a4` | **37 passed** |
| `pytest -q tests/unit/a5` | **52 passed** |
| R1–R5 focused regression | **93 passed** |
| `pytest -q tests/acceptance/a6` | **13 passed** |
| `pytest -q` | **2,477 passed** |
| `python -m compileall src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS — 563 source files |
| `python -m pip check` | PASS — no broken requirements |
| `uv lock --check` | PASS — 71 packages resolved |
| `git diff --check` | PASS |

Additional checks cover catalog parity, optional-import isolation, socket denial,
A5 tag parity, prohibited A7/TM/broker/provider/NLP edges, secret absence, local
documentation links, canonical deferral integrity and README A0–A10 visibility.
Package version `0.1.0`, contract/capability schema `1.0`, policy version
`1.0-draft`, Shell grammar `0.1` and Asia/Kolkata timestamp policy remain
separate and unchanged.

## Freeze criteria and residual risks

All 15 freeze criteria pass: accepted architecture/thesis and A6.1–A6.3;
completed A6.4 corpus; stable public capability; exact replay; preserved
authority/R1–R5/A4/A5; no in-scope defect; explicit deferrals; green full suite;
and reconciled status documentation.

Residual risks are intentionally outside the frozen v1 scope: live providers
may not supply qualified market/expiration timing; strict evidence rules may
therefore return INSUFFICIENT_EVIDENCE; engineering thresholds are not
profitability calibration; only advisory long single-leg CE/PE is supported;
and no TM, broker, live monitoring, NLP/Web or A7 forecasting integration exists.
