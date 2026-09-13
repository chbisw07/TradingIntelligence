# TIAF Pluggability R2 — Discovery Metadata

## Decision and scope

Implementation date: 2026-09-13 (Asia/Kolkata).

**Decision: `READY_TO_ACCEPT_PLUGGABILITY_R2`.**

Closure update: the independent
[R2 acceptance](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA_ACCEPTANCE.md) returned
`READY_TO_CLOSE_PLUGGABILITY_R2`. R2 is now ACCEPTED / DONE; the implementation
decision and evidence below remain the implementation-pass record.

R2 adds explicit, typed, versioned and deterministic discovery metadata for the
eight existing facade operations. It changes neither operation identity nor
invocation semantics. A5 remains frozen at `tiaf-a5-baseline`.

This is declaration and permission-filtered discovery only. It adds no dynamic
loading, implementation binding, run composition envelope, pinned verifier,
optional-import refactor, startup composition framework, live read, provider,
model, broker, monitoring runtime or A6 behavior.

## Contract shape and compatibility

The frozen `CapabilityDescriptor` remains the legacy admission descriptor.
`CapabilityDiscoveryDescriptor` extends it only in the R2 discovery projection:

| Field | Meaning |
|---|---|
| `descriptor_schema_version` / `descriptor_id` | Version `1.0`; deterministic identity `descriptor:<capability-id>/<capability-version>`. |
| `semantic_role` | Meaning-based role, independent of package or milestone numbering. |
| `pluggability_level` | Highest demonstrated lifecycle level. Every current operation is STRUCTURAL; none claims COLD or HOT. |
| `replaceable` / `composable` | Separate traits; both are false for the current fixed facade operations. |
| `required_dependencies` / `optional_dependencies` | Sorted typed declarations. Current required items are input contracts, not run-time composition pins; optional sets are empty. |
| `required_authorities` / `required_entitlements` | Stable requirement categories, never grants or secrets. Invocation still intersects trusted caller/operator policy and artifact entitlement refs. |
| `registration_state` / `discovery_state` | Static catalog entries are REGISTERED; permission-filtered returned entries are DISCOVERABLE. |
| `readiness_state` | Always REQUIRES_RUNTIME_CHECK; registration/discovery is not request readiness. |
| `monitoring_compatibility` | Semantic suitability only, never proof of scheduler or fresh acquisition. |
| `limitations` | Stable explicit constraints such as captured-input-only, no-live-freshness and no-monitoring-runtime. |

`CapabilityListResult` advances additively from `1.0` to `1.1`, retaining the
unchanged `capabilities` tuple for legacy consumers and adding the exactly aligned
`discovery_metadata` tuple. The current reader accepts historical `1.0` results
without R2 metadata. It rejects partial, reordered or mismatched `1.1` metadata.
No historical capture is rewritten.

## Taxonomies

Semantic roles are: BASELINE, CAPABILITY_DISCOVERY, OPPORTUNITY_INTELLIGENCE,
CHALLENGE_ARBITRATION, POSITION_INTELLIGENCE, REPLAY and ENGINEERING.

Effects remain the accepted PURE or CAPTURED_READ values. No descriptor claims
LIVE_READ. The inherited legacy `availability=AVAILABLE` means only that the
static local binding participates in the existing admission catalog; it is not
a health/freshness/readiness statement. R2 separately reports
REQUIRES_RUNTIME_CHECK.

The discovery/readiness vocabulary can represent REGISTERED, DISCOVERABLE,
DISABLED, UNAUTHORIZED, DEPENDENCY_UNAVAILABLE, UNSUPPORTED and UNKNOWN without
fabricating a state. Current static metadata is REGISTERED; a returned,
permission-filtered item is DISCOVERABLE and still requires invocation checks.
Unauthorized inventory remains filtered rather than disclosed as a self-grant.

## Dependencies, authority and entitlement

Required dependencies name the already-consumed input contracts: deterministic
baseline request, A3 orchestration capture, source-semantic build/capture,
A5 position request, or trusted replay artifact. `capabilities.list` has no input
contract dependency. There are no current optional dependencies and no future
Sector Rotation, Signal Qualification or forecast dependencies.

Every discovery descriptor repeats exactly its existing facade authority scope.
Entitlement categories distinguish captured evidence, position data and
engineering access without exposing caller-specific refs. These declarations do
not mutate grants. Admission, revocation, profiles, authority refs, entitlement
refs, artifact checks and budgets remain independently enforced.

## Monitoring compatibility

- NOT_MONITORABLE: capability discovery and replay/verification operations.
- SEMANTICALLY_REPEATABLE: baseline, opportunity, source projection and A4
  evaluation can run again over separately admitted supplied/captured input.
- MONITORING_FUTURE: `position.assess` is semantically suitable for the accepted
  future monitoring design, while remaining CAPTURED_READ with no scheduler,
  live refresh, subscription, worker or delivery runtime.

This implements only the minimal descriptor seam identified by the
[Monitoring Architecture](TIAF_MONITORING_ARCHITECTURE.md).

## Catalog and Shell behavior

The catalog remains eight ID-sorted operations. `capabilities.list` returns
permission-filtered legacy descriptors plus aligned R2 metadata in deterministic
order. Static catalog possession and returned metadata grant nothing.

The Shell command family is unchanged. `capabilities list` remains concise;
`capabilities describe <id>` now renders the structured R2 descriptor including
role, effect, pluggability, dependency, readiness and monitoring metadata.
Engineering filtering remains enforced.

## Frozen A5 and later R boundaries

The frozen A5 fixture retains its exact run fingerprint, semantic fingerprint,
replay identity and capture checksum. R2 introduces no A5 dependency, policy,
recommendation, posture, thesis, protection, monitoring-intent or replay change.

- R3 still owns exact per-run composition envelopes and pinned verification.
- R4 still owns optional adapter import isolation.
- R5 still owns broader trusted COLD ownership/configuration.
- A6 remains not implemented.

## Acceptance

Focused and full regression verify deterministic identity/order, schema
round-trip and `1.0` reader compatibility, exact eight-operation coverage,
semantic roles/effects, STRUCTURAL-only claims, deterministic dependency sets,
non-granting authority metadata, denied invocation, conservative readiness,
honest monitoring semantics, Shell projection, documentation parity, forbidden
imports and frozen A5 identity.

No live broker/provider/model call is part of R2 acceptance.

Validation completed on 2026-09-13:

| Gate | Result |
|---|---|
| `pytest -q tests/unit/facade` | 68 passed |
| `pytest -q tests/unit/shell` | 89 passed |
| `pytest -q tests/unit/a5` | 52 passed |
| `pytest -q tests/unit/a4` | 37 passed |
| Full `pytest -q` | 2,246 passed |
| Compile / Ruff / mypy / pip check | PASS; mypy checked 531 files |
| Documentation links | PASS; 116 Markdown files and 921 repository-relative links |
| Deferral register | PASS; DEF-001 through DEF-058 remain complete and unique |
| Catalog parity | PASS; eight deterministic runtime/documentation entries |
| Import / secret boundary | PASS; zero forbidden imports or assigned credential literals |
| `git diff --check` | PASS |

The recommended short acceptance/closure was completed. R3 is now ACTIVE / NEXT,
but no R3 behavior is implemented by this record.

Exact next prompt title:

**`TIAF PLUGGABILITY — R3 COMPOSITION ENVELOPE / PINNED VERIFIER`**
