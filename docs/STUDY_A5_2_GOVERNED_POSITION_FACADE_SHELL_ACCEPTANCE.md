# Study: TIAF A5.2 Governed Position Facade and Shell Acceptance

## Decision

**READY_TO_ACCEPT_A5_2.** The governed local position capability and bounded
Shell exposure satisfy the accepted A5 authority, privacy, replay and
non-execution boundaries.

Date: 2026-09-12, Asia/Kolkata. Live calls: none required and none performed.

## Implemented acceptance surface

- Static `position.assess@1.0` public descriptor: `CAPTURED_READ`, deterministic,
  no model, known-zero cost, `ASSESS_POSITION` authority.
- Exact-checksum `A5_POSITION_REQUEST` artifact validation and position-specific
  read-time authority/entitlement enforcement.
- Direct A5.1 result and run-fingerprint parity for authorized calls.
- Identity, timestamp, freshness, linked-A4, policy, replay and semantic
  fingerprint preservation.
- A5 `A5_CAPTURE` support through generic `replay.recorded`; no duplicated replay
  engine or dedicated `position.replay` capability.
- Shared one-shot/REPL `position assess --snapshot QUALIFIED_ID` parser and
  dispatcher path.
- Allowlisted human/JSON, `explain last` and `trace last` projections.
- Isolated session convenience state; refresh is a new admitted artifact read.
- Explicit advisory monitoring and TradeMonitor/broker authority labels.
- Explicit A6 seam rendering with no replacement selection.

## Scenario evidence

The A5.2 tests cover:

1. descriptor identity/effect/replay/authority/cost metadata;
2. trusted Python client invocation parity with direct A5.1;
3. caller A denied caller B's restricted position;
4. artifact ID without the position entitlement denied;
5. capability permission and revocation denial;
6. fresh equity, future and single-leg option parity;
7. multi-leg preserved as `UNSUPPORTED_SHAPE` domain output;
8. stale snapshot preserved as successful `ABSTAIN` output;
9. corrupt checksum and tampered semantic artifact failure;
10. paths, traversal, URLs, extras and object injection rejected;
11. snapshot/A4/freshness/policy/run/replay fingerprints preserved;
12. generic A5 recorded replay performs zero external calls;
13. Shell position/facade/JSON parity;
14. real one-shot CLI bootstrap path through shared parser/dispatcher;
15. structured explain and redacted trace;
16. refresh reread with unchanged snapshot timestamp;
17. two Shell sessions share no position/last state;
18. `ABSTAIN` and `EXIT_RECOMMENDED` return process success;
19. permission denial returns nonzero and is not retained as `last`;
20. monitoring intent is displayed and not scheduled;
21. expression refresh names no replacement;
22. execution-like position verbs remain outside the grammar.

Existing A5.1 tests continue to cover closed/unknown state, invalid identity,
expiry, intraday windows, predecessor/successor lineage, contradictions,
reference levels, secret-shaped content, exact replay, deterministic verification
and policy comparison. Existing facade/Shell security tests cover lifecycle,
concurrency, baseline root/symlink safety, forbidden imports and safe errors.

## Quality-gate record

- `pytest -q tests/unit/a5`: **52 passed**.
- `pytest -q tests/unit/facade`: **57 passed**.
- `pytest -q tests/unit/shell`: **88 passed**.
- `pytest -q tests/unit/a4`: **37 passed**.
- `pytest -q tests/unit/source_semantics`: **27 passed**.
- `pytest -q tests/unit/opportunity_intelligence`: **65 passed**.
- `pytest -q tests/unit/a3_hardening`: **61 passed**.
- `pytest -q tests/unit/agents`: **270 passed**.
- `pytest -q tests/unit/workflows`: **42 passed**.
- `pytest -q`: **2,226 passed in 176.17 seconds**.
- Dedicated lifecycle/security/replay boundary selection: **39 passed**.
- `python -m compileall src scripts`: passed.
- `ruff check src tests scripts`: passed.
- `mypy src tests`: passed, 529 source files checked.
- `python -m pip check`: no broken requirements; the environment emitted only
  its non-writable pip-cache warning.
- Local Markdown link scan: 97 files checked, zero missing links.
- Secret scan: no credential value; matches were only parser rejection literals.
- Facade/Shell forbidden-import and A6/A7/remote-service scans: zero matches.
- Full tests include frozen A2/A3/A4 regression and A5 replay isolation checks.
- `git diff --check`: passed.

No live provider, broker, model or TradeMonitor operation is part of acceptance.

## Residual boundaries

The accepted slice evaluates only operator-installed captured request artifacts.
It deliberately has no live TM/broker adapter, durable artifact store, scheduler,
remote authentication/transport or multi-leg interpretation. These are visible
scope boundaries, not A5.2 correctness blockers.

Exact next prompt title:

**`TIAF_A5 — MAJOR MILESTONE CLOSURE REVIEW`**
