# TIAF A6.3 — Facade & TI Shell Exposure

## Status

Implemented on 2026-09-13 and independently
[accepted / done](TIAF_A6_3_FACADE_TI_SHELL_EXPOSURE_ACCEPTANCE.md) on
2026-09-14 (Asia/Kolkata). A6.1 and A6.2 remain accepted/done; A6.4 is active/
next. This slice publishes `expression.assess` but does not freeze A6, create a
tag, or begin A7.

## Delivered boundary

`expression.assess` is the ninth static local-facade capability. It is PUBLIC,
`CAPTURED_READ`, deterministic, model-disabled, known-zero-cost, structurally
pluggable and `REQUIRES_RUNTIME_CHECK`. Its semantic role is
`TRADE_EXPRESSION_INTELLIGENCE`; its dedicated authority scope is
`ASSESS_EXPRESSION`. Discovery metadata is descriptive and grants no authority.

The facade accepts one startup-validated logical artifact reference. The
artifact is a versioned `ExpressionAssessInput` containing the accepted A6
request, A4 result, evidence bundle, deterministic policy, admission result,
optional recorded assessment and composition references. Startup validates
checksum, schema, secret absence, admission replay, and—when a recorded result
is present—exact deterministic assessment replay. Invocation rechecks
caller/operator authority, entitlement, profile, budget, logical artifact kind,
request authority and captured scope before running the accepted evaluator.

```text
logical artifact reference
        ↓
facade admission + artifact authority
        ↓
captured A6 request / A4 / evidence / policy / admission
        ↓
exact A6.2 deterministic evaluation
        ↓
TradeExpressionAssessment + checksum + input-integrity proof
```

The result is advisory and carries
`ADVISORY_ONLY_TM_RETAINS_ACTION_AUTHORITY`. It contains no account, capital,
quantity, order, target, stop, provider, broker, TM, model or tool handle.
No live lookup or timing inference occurs.

## TI Shell

One-shot and REPL use the same closed parser and dispatcher:

```text
expression assess --input QUALIFIED_ID [scope options]
```

`--input` is a logical reference pre-admitted in trusted startup composition;
it is not a file path, URL, symbol lookup, or inline policy. Paths, URLs,
credential-looking values, repeated options and shell expansion are rejected.
The command returns compact human output or the exact full facade result with
`--output json`. `show last`, `explain last`, `trace last`, `refresh last`, and
the existing `replay recorded --artifact-ref QUALIFIED_ID` seam support the
same captured expression result. Refresh creates a new admitted facade run over
the unchanged capture; it does not fetch fresh data.

Example with an operator-provisioned synthetic artifact:

```bash
python -m tiaf.shell --config shell-bootstrap.json \
  expression assess --input artifact:a6-available
```

The human view exposes disposition, direction, horizon, preferred listed
contract when present, at most two alternatives, blockers, gaps, reason codes,
invalidations, semantic fingerprint, replay status and advisory authority. JSON
retains every candidate evaluation, gate, evidence reference, policy identity,
fingerprint and zero-usage field.

## Deterministic examples and replay

Focused fixtures prove `EXPRESSION_AVAILABLE`, `NO_OPTION_TRADE`,
`WAIT_FOR_EXPRESSION`, and `INSUFFICIENT_EVIDENCE`. They are synthetic and do
not tune policy. `WAIT_FOR_EXPRESSION` preserves upstream A4 conflict;
known-complete zero depth remains a factual hard rejection; missing bid/ask
remains insufficient rather than being relabeled illiquid.

The existing public recorded-replay capability accepts an A6 capture containing
the optional recorded assessment and returns `A6_RECORDED`; an input-only
envelope remains valid for `expression.assess` but is not mislabeled a recorded
run. Replay uses only the captured cutoff and pins, performs no
provider/model/broker call, and must reproduce the recorded assessment semantic
fingerprint exactly. A tampered recorded result is rejected during trusted
startup validation.

## Preserved boundaries

- A2 policy and benchmark outputs are unchanged.
- A4 results are supplied and verified; A6 does not bypass or recalculate A4.
- Frozen A5 contracts, policy, replay identity, facade behavior and monitoring
  authority remain unchanged.
- R2 discovery stays non-authorizing; R3 capture references remain immutable;
  R4 optional-adapter isolation remains intact; R5 owns COLD startup selection.
- No HOT mutation, NLP, remote transport, Web API, live provider acquisition,
  A7 forecast, recurring monitor, TM/broker integration or execution operation
  is introduced.
- Package version `0.1.0`, contract schema version `1.0`, capability version
  `1.0`, Shell grammar `0.1`, and discovery descriptor schema `1.0` remain
  separate concepts.

## A6.4 boundary

A6.4 still owns integrated hardening, the final acceptance corpus,
cross-capability closure, any deliberately deferred replay/rendering UX review,
and A6 freeze/tag readiness. No new deferral was introduced by A6.3.

## Implementation validation

The implementation pass completed these non-live checks:

| Check | Result |
|---|---|
| A6 unit suite | 99 passed |
| Facade unit suite | 82 passed |
| Shell unit suite | 104 passed |
| A4 regression | 37 passed |
| A5 regression | 52 passed |
| Combined R1–R5 regressions | 93 passed |
| Full repository suite | 2,445 passed |
| `python -m compileall src scripts` | passed |
| `ruff check src tests scripts` | passed |
| `mypy src tests` | passed, 561 source files |
| `python -m pip check` | passed; no broken requirements |
| `uv lock --check` | passed using repository `.venv/bin/uv` |
| `git diff --check` | passed |
| Local Markdown links | 131 files checked; zero missing |
| Canonical deferral table | 58 unique/classified rows; zero duplicates |
| A5 baseline/source parity | no A5 source or A5-test diff from `tiaf-a5-baseline` |

Focused tests include socket denial for A6 assessment/replay and optional-SDK
absence for Shell help, discovery and invocation. Source/import and request
surface checks found no provider, model, A7, TM or broker call edge. A secret
scan found only intentional credential-denylist strings, no secret value.

Next prompt:

`TIAF A6.4 — FINAL HARDENING, ACCEPTANCE CORPUS & FREEZE READINESS`
