# TIAF A6.3 — Facade & TI Shell Exposure Acceptance

## Decision and boundary

**READY_TO_CLOSE_A6_3** — independently accepted on 2026-09-14
(Asia/Kolkata).

- A6 architecture: **ACCEPTED**.
- A6.1 contracts/admission/policy: **ACCEPTED / DONE**.
- A6.2 candidate evaluation/ranking/replay: **ACCEPTED / DONE**.
- A6.3 facade and TI Shell exposure: **ACCEPTED / DONE**.
- A6.4 final hardening, acceptance corpus and freeze readiness: **ACTIVE / NEXT**.
- `expression.assess`: **PUBLISHED**; the public catalog contains exactly nine
  unique operations.
- A5 remains frozen at `tiaf-a5-baseline`; R1–R5 remain accepted/done.
- No live provider, model, broker, TM, Web/API, NLP or A7 behavior was added or
  invoked by this acceptance.

The next prompt is exactly:
`TIAF A6.4 — FINAL HARDENING, ACCEPTANCE CORPUS & FREEZE READINESS`.

## Independent acceptance review

| Area | Verdict | Evidence / conclusion |
|---|---|---|
| Capability publication | ACCEPT | `expression.assess` occurs once in the static catalog. The other eight descriptors are unchanged from the accepted A6.2 tree; no alias was added. |
| Discovery | ACCEPT | PUBLIC, CAPTURED_READ, deterministic, model-disabled, KNOWN_ZERO, DETERMINISTIC replay, STRUCTURAL, non-replaceable/non-composable, REQUIRES_RUNTIME_CHECK and MONITORING_FUTURE. Limitations explicitly say captured input, advisory only, no execution, no live freshness and no monitoring runtime. Discovery remains descriptive and non-authorizing. |
| Captured contract | ACCEPT | Frozen schema-1.0 `ExpressionAssessInput` contains the accepted A6 request, A4 result, evidence, policy, admission, optional recorded assessment and canonical composition references. It contains no provider/client/registry injection point. |
| Artifact admission | ACCEPT | Trusted startup validation checks schema, exact bytes checksum, secret absence and admission replay. A recorded result additionally undergoes exact A6 replay verification. Wrong-kind, mismatched, malformed and tampered artifacts fail closed. |
| Facade evaluation | ACCEPT | Invocation reads one authorized logical artifact, rechecks effective request authority and exact subject/objective/horizon/cutoff scope, then calls the accepted deterministic evaluator. It performs no provider fetch, chain lookup, timing inference, event synthesis or policy mutation. The returned assessment is exactly the canonical A6 result. |
| Authority | ACCEPT | Dedicated `ASSESS_EXPRESSION` authority is required. The result states `ADVISORY_ONLY_TM_RETAINS_ACTION_AUTHORITY`; no account, capital allocation, order quantity/type, submit/modify/cancel, `ExecutionIntent`, position mutation, provider or model handle is exposed. |
| Shell grammar | ACCEPT | `expression assess --input QUALIFIED_ID` uses the existing closed structured grammar and trusted logical-artifact convention. Paths, URLs, expansions, credential-like tokens, repeated options and execution-like verbs are rejected. No inline policy DSL or free-text interpreter exists. |
| REPL / one-shot | ACCEPT | Token and line entry share one parser, dispatcher, facade request and runtime handler. Equivalent invocations reproduce the same assessment semantic fingerprint. |
| Human rendering | ACCEPT | Compact output shows subject, disposition, direction, horizon, preferred listed contract, at most two alternatives, policy/version, reasons, blockers/gaps, rejected and uncertain candidates, invalidations, semantic fingerprint, integrity and advisory authority. It projects structured facts only. |
| JSON | ACCEPT | JSON returns the exact typed facade result and round-trips without losing candidate evaluations, explanation, evidence refs, policy/composition pins, fingerprints or zero-usage metadata. Human projection cannot modify it. |
| Explain / trace | ACCEPT | Existing `explain last` and `trace last` expose preferred/rejected/uncertain reasons, rank differences, candidate evidence, request/admission/A4/evidence/assessment fingerprints and input checksum without acquisition or model calls. |
| Replay | ACCEPT | Existing `replay recorded --artifact-ref QUALIFIED_ID` returns `A6_RECORDED` only when recorded material exists, recomputes the exact assessment and verifies its fingerprint. Input-only captures assess normally but are not mislabeled recorded replay. Socket-denial coverage proves network-free behavior. |
| Examples | ACCEPT | Synthetic trusted fixtures deterministically cover EXPRESSION_AVAILABLE, NO_OPTION_TRADE, WAIT_FOR_EXPRESSION and INSUFFICIENT_EVIDENCE. They are test evidence, not live recommendations. |
| Errors | ACCEPT | Syntax/unsafe-token errors remain Shell diagnostics; permission, absence, budget, replay-integrity and safe generic failures remain distinct facade statuses. Analytical no-trade/wait/insufficient outcomes remain result dispositions. Diagnostics disclose neither artifact paths nor secrets. |
| R2 | ACCEPT | The relevant catalog/discovery assertions move from eight to nine; historical milestone records retain their then-current eight-operation statements. Static discovery remains deterministic and import-safe. |
| R3 | ACCEPT | Canonical composition references survive the facade path. Artifact checksum, A6 request/admission/A4/evidence/assessment fingerprints and R3 composition identity remain distinct; recorded verification remains pinned and registry-independent. |
| R4 | ACCEPT | Isolated-process tests prove Shell help, capability listing/description and captured expression invocation with optional SDK roots unavailable and unloaded. No eager provider/model/orchestration SDK import was introduced. |
| R5 | ACCEPT | Trusted startup composition owns the artifact and bindings. Invocation cannot enable, disable or swap adapters, replace policy registries or introduce HOT behavior. |
| A5 | ACCEPT | The 52-test A5 suite passes. No source/test diff exists under `src/tiaf/a5` or `tests/unit/a5` against `tiaf-a5-baseline`; `position.assess` and A5 replay identities are unchanged. |
| A6.4 | ACCEPT | A6 is not frozen or tagged. Integrated hardening, the final acceptance corpus, cross-capability closure, residual rendering/replay UX review and baseline-tag readiness remain A6.4 work. |

## Acceptance cleanup

The review found no domain, ranking, replay or authority defect. It made two
bounded clarity corrections:

1. renamed two legacy A6 test functions whose bodies had correctly changed to
   the nine-capability state but whose names still described the old unpublished
   eight-capability boundary; and
2. made the compact expression rendering explicitly display its policy/version
   references and cap the displayed alternatives at two, as required. The full
   canonical JSON and A6 assessment are unchanged.

`NLP_BOUNDARY_PRESERVED`

`A6_4_BOUNDARY_PRESERVED`

## Validation evidence

All checks used captured/synthetic repository evidence. No live call occurred.

| Gate | Result |
|---|---:|
| `pytest -q tests/unit/a6` | **99 passed** |
| `pytest -q tests/unit/facade` | **82 passed** |
| `pytest -q tests/unit/shell` | **104 passed** |
| `pytest -q tests/unit/a4` | **37 passed** |
| `pytest -q tests/unit/a5` | **52 passed** |
| R1–R5 focused regression | **93 passed** |
| A6.3-specific facade/Shell tests | **26 passed** |
| `pytest -q` | **2,445 passed** |
| `python -m compileall src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS — 561 source files |
| `python -m pip check` | PASS — no broken requirements |
| `uv lock --check` | PASS — 71 packages resolved |
| `git diff --check` | PASS |

Additional checks confirmed nine unique descriptors; unchanged legacy eight
descriptors; socket-denied replay; frozen A5 parity; no provider/model/A7/TM/
broker call edge; optional-import isolation; no recorded secret; valid local
documentation links; canonical deferral integrity; and README A0–A10 visibility.

## Deferrals and residual risks

No deferral was removed or closed. DEF-006 now records the completed bounded
A6.3 publication while retaining broader strategy, TF-05 and A7 follow-up work.
Strict source-time, session/calendar, authoritative option-event timestamp,
multi-leg/short-strategy, live acquisition, TM integration, monitoring runtime
and remote-service boundaries remain under their existing owners.

The public capability is intentionally captured-input-only. A caller must supply
a trusted, admitted bundle; live source availability may still yield
insufficient evidence. A6.3 acceptance does not establish profitability,
execution permission, live readiness, final corpus coverage or A6 freeze.
