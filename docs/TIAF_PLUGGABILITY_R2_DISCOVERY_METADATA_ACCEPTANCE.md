# TIAF Pluggability R2 — Discovery Metadata Acceptance

## Decision and reviewed boundary

Acceptance date: 2026-09-13 (Asia/Kolkata).

**Decision: `READY_TO_CLOSE_PLUGGABILITY_R2`.**

**Boundary verdict: `R3_R4_R5_UNTOUCHED`.**

This independent closure review accepts the bounded
[R2 implementation](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA.md) as the capability-
discovery baseline. It reviewed the uncommitted R2 implementation and tests; it
made no runtime semantic change. The only additional implementation-pass artifact
is stronger acceptance coverage for immutability and `1.1` fail-closed behavior.

R2 adds declarations and permission-filtered projections only. It does not add
live acquisition, monitoring runtime, dynamic loading, implementation bindings,
run-composition pinning, optional-import isolation, COLD ownership, A6, or
execution behavior.

## Contract and catalog verdict

`CapabilityDiscoveryDescriptor` is an immutable `ContractModel` with explicit
descriptor schema version `1.0`. Its identity is deterministically constrained to
`descriptor:<capability-id>/<capability-version>`. Required and optional
dependencies, authority categories, entitlement categories and limitations are
tuple-backed, sorted where order is semantic, and reject contradictory metadata.

The descriptor contains no callable, implementation binding, secret, token, or
caller-specific grant. Its inherited capability fields must match the unchanged
legacy `CapabilityDescriptor` exactly.

The exact ID-sorted catalog remains:

1. `a4.evaluate`
2. `a4_input.project`
3. `baseline.assess`
4. `capabilities.list`
5. `opportunity.assemble`
6. `position.assess`
7. `replay.recorded`
8. `replay.verify`

Runtime metadata and [the capability map](TIAF_CAPABILITY_MAP.md) match exactly.

## Semantic metadata verdicts

| Concern | Acceptance verdict |
|---|---|
| Roles | PASS — BASELINE, CAPABILITY_DISCOVERY, OPPORTUNITY_INTELLIGENCE, CHALLENGE_ARBITRATION, POSITION_INTELLIGENCE, REPLAY and ENGINEERING describe semantics rather than package paths or milestone names. |
| Effects | PASS — existing PURE/CAPTURED_READ behavior is preserved; no LIVE_READ is declared or implied. |
| Pluggability | PASS — all eight operations are STRUCTURAL; replaceable/composable are separately false; no COLD or HOT claim steals later scope. |
| Dependencies | PASS — required input contracts are explicit and deterministic; optional sets are explicit and empty; no future capability is introduced. These declarations are not an R3 run envelope. |
| Authority | PASS — each descriptor repeats its existing facade authority scope and grants nothing. Permission filtering, operator policy and invocation admission remain independent. |
| Entitlements | PASS — only stable CAPTURED_EVIDENCE, POSITION_DATA and ENGINEERING categories appear; no entitlement reference or secret is disclosed. |
| Readiness | PASS — catalog entries are REGISTERED, permission-filtered returned entries are DISCOVERABLE, and every entry remains REQUIRES_RUNTIME_CHECK. No health, authorization or freshness is invented. |
| Monitoring | PASS — NOT_MONITORABLE, SEMANTICALLY_REPEATABLE and MONITORING_FUTURE describe semantic suitability only. No scheduler, refresh or live-monitoring runtime is claimed. |

The legacy inherited `availability=AVAILABLE` remains the already-accepted static
binding/admission vocabulary. The R2 readiness field explicitly prevents it from
being interpreted as proven live usability.

## Discovery and Shell verdict

`CapabilityListResult` version `1.1` retains the legacy `capabilities` tuple and
adds a permission-filtered, exactly aligned `discovery_metadata` tuple. Ordering
is deterministic. Missing metadata, reordering, changed legacy fields, or partial
coverage fail closed. Historical explicit `1.0` payloads still validate with an
empty discovery projection; no capture is rewritten.

`capabilities list` remains concise in the human Shell view. The existing
`capabilities describe <id>` path renders the structured descriptor. It creates
no command family, authority, readiness upgrade, live call, provider/model/broker
call, or private-binding exposure. Engineering-only discovery remains filtered.

## Frozen A5 and later boundaries

The A5 source tree has no difference from tag `tiaf-a5-baseline` at commit
`167c51d40985e70e422df14af4a67531f8f66a65`. Direct-before/after R2 regression
preserves the position result, recommendation/posture/thesis semantics, run
fingerprint, semantic fingerprint, replay identity and capture checksum. The A5
suite and facade parity tests pass. No A5 dependency or execution behavior was
added.

R2 did not implement:

- R3 per-run composition envelopes, pinned verification or participation hashes;
- R4 optional-adapter import isolation;
- R5 broad trusted COLD composition/configuration ownership.

## Validation evidence

| Gate | Result |
|---|---|
| Dedicated R2 acceptance tests | 14 passed |
| `pytest -q tests/unit/facade` | 71 passed |
| `pytest -q tests/unit/shell` | 89 passed |
| `pytest -q tests/unit/a5` | 52 passed |
| `pytest -q tests/unit/a4` | 37 passed |
| Facade/A5 parity selection | 43 passed |
| Full `pytest -q` | 2,249 passed in 195.85 seconds |
| Compile / Ruff / mypy / pip check | PASS; mypy checked 531 files; no broken requirements |
| Documentation links | PASS; 117 Markdown files and 928 repository-relative links |
| Deferral register | PASS; DEF-001 through DEF-058 remain complete and unique |
| Catalog parity | PASS; eight runtime/documentation entries in exact order |
| Import boundary | PASS; 28 A5/facade/Shell files checked, zero forbidden imports |
| Secret scan | PASS; zero assigned credential-like literals |
| `git diff --check` | PASS after acceptance status synchronization |

No live broker, provider or model call was made.

## Closure and next work

R2 is accepted. Project navigation advances to:

```text
A5 FROZEN
R1 ACCEPTED
R2 ACCEPTED
R3 ACTIVE / NEXT
R4–R5 PENDING BEFORE_A6
A6 NOT_IMPLEMENTED
```

Exact next prompt title:

**`TIAF PLUGGABILITY — R3 COMPOSITION ENVELOPE / PINNED VERIFIER`**

This record does not authorize or begin R3.
