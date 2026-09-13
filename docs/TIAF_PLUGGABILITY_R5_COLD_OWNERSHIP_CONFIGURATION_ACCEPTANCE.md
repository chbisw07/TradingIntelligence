# TIAF Pluggability R5 — COLD Ownership / Configuration Acceptance

## Decision and boundary

Acceptance date: 2026-09-13 (Asia/Kolkata).

**Decision: `READY_TO_CLOSE_PLUGGABILITY_R5`.**

**HOT boundary: `HOT_NOT_IMPLEMENTED`.**

This independent review accepts the bounded
[R5 implementation](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md) on the
clean accepted R4 base `5fce47c`. It closes the cross-cutting R1–R5 pre-A6
pluggability hardening track. No runtime defect or semantic drift was found, so
the acceptance pass changes documentation/status only. It does not begin A6,
alter frozen A4/A5 policy, add a live provider/model/broker call, or introduce
HOT loading.

## Acceptance verdicts

| Concern | Verdict |
|---|---|
| Startup owner | PASS — `create_cold_runtime` is the single R5 bootstrap root and returns one `ColdRuntimeOwner`; consumers receive only caller-bound facade clients. Domain models, Shell requests and adapters cannot select or replace the composition. |
| Configuration sources | PASS — reviewed code defaults plus one explicit trusted `ColdStartupConfig`/mapping are the only sources. No environment, implicit file search, profile overlay, request override or module-local merge participates. |
| Precedence | PASS — defaults are overridden field-by-field by the one explicit object. Supplied selection arrays replace defaults completely, including an empty array; duplicates fail and canonical sorting removes irrelevant input order. |
| Freeze point | PASS — config/facade validation and selected allowlist resolution precede immutable composition sealing, binding snapshots and facade startup. No active runtime is returned on validation/import failure. |
| Selectable components | PASS — the code-owned allowlist contains exactly four optional adapter factories, nine implemented specialists and two workflows (serial or pinned LangGraph). A2/A4/A5 policy and future components are not selectable. |
| Configuration schema | PASS — `ColdStartupConfig` and nested contracts are frozen, strict about extra fields, explicitly schema-versioned `1.0`, tuple-backed and deterministically serializable. They contain IDs and versions, never module/class paths or secrets. |
| Validation | PASS — unknown/duplicate/wrong-category IDs, invalid profile/schema, incompatible version, unsupported combination, arbitrary module fields and secret-shaped fields fail before optional import or facade construction. Forged Pydantic copies are revalidated. |
| Required/optional behavior | PASS — required or `FAIL_STARTUP` missing selections fail closed with no owner. Only an optional selection explicitly using `RECORD_UNAVAILABLE` degrades; the absence is recorded and no substitute is selected. R1 required semantic scope does not shrink. |
| Error taxonomy | PASS — failures use narrow `StartupFailure` categories. Missing SDK, broken adapter export and unrelated internal import defects remain distinct; rejected values and secrets are absent from public error text. |
| Fingerprints | PASS — configuration identity covers canonical requested selection plus authority-policy identity; startup identity adds recorded import resolution. They are deterministic, order-stable and sensitive to semantic changes while excluding time, environment, artifacts, physical paths and secrets. |
| Secret handling | PASS — composition schemas admit no secret field; secret-bearing payloads are rejected. Credentials remain in existing adapter-specific trusted mechanisms and are neither serialized, replayed, inspected nor fingerprinted by R5. |
| R2 compatibility | PASS — the exact eight-operation descriptive catalog is unchanged. Discoverability neither selects a component nor proves readiness or grants invocation authority. |
| R3 compatibility | PASS — R5 startup selection remains separate from the unchanged per-run composition. Direct and R5-owned serial runs have the same run/composition fingerprints; recorded replay and pinned verification remain intact. |
| R4 compatibility | PASS — unselected SDKs are not imported. Selected missing dependencies are typed; optional degradation is explicit; installed adapter defects are not concealed. No eager global import was introduced. |
| Frozen A4/A5 | PASS — `src/tiaf/a4`, `src/tiaf/a5`, `tests/unit/a4` and `tests/unit/a5` have no difference from `tiaf-a5-baseline`. Configuration cannot replace their policies, and their regression/replay suites pass. |
| Shell / inspection | PASS — trusted Python may read/serialize `owner.composition`; the Shell has no enable, disable, reload, component setter or owner/registry/factory handle. Startup failures render through the existing safe error boundary. |
| Deployment | PASS — local trusted Python, same-process facade and filesystem/offline replay remain the deployment boundary. No config service, distributed registry, service mesh, remote API or plugin marketplace was added. |
| HOT behavior | PASS — supported registry/service consumers snapshot bindings, post-freeze mutation fails, active work blocks shutdown, and new work after shutdown fails. Changing composition requires a new owner. `HOT_NOT_IMPLEMENTED`. |

## Ownership and freeze proof

```text
reviewed code defaults
        +
one explicit trusted config
        ↓
central validation and allowlist checks
        ↓
resolve selected code-owned imports only
        ↓
seal StartupComposition + snapshot bindings
        ↓
start facade and return ColdRuntimeOwner
        ↓
caller-bound LocalFacadeClient (no mutation surface)
```

The owner is a frozen dataclass; its composition is a frozen Pydantic contract;
resolutions and selections are tuples; implementation bindings use a read-only
mapping; and the selected specialist registry is a frozen copy. Existing agent,
market-intelligence, resolver, feature, indicator and workflow-service seams pin
membership/references at their documented construction or first-use boundary.
The source builder may remain usable to construct a later runtime, but it cannot
mutate an already admitted consumer.

Python private-member access remains a trusted-code convention rather than a
hostile-code sandbox. That limitation is explicit and does not create a public
or Shell HOT API.

## Component and failure audit

The selectable inventory is code-owned and finite:

- adapter factories: Dhan market data, authoritative HTTP, Tapetide MCP and
  Yahoo MCP;
- specialists: technical, fundamental, news/event, relative strength, sector,
  macro, derivatives context, opportunity quality and opportunity risk;
- workflows: serial `1.0` and LangGraph `1.2.11`.

Configuration never passes a module name to `import_module`; the only module and
attribute names are reviewed constants in the bootstrap catalog. `LOCAL_CAPTURED`
permits the serial/no-adapter captured profile. `LOCAL_ENGINEERING` permits
explicit optional factory and LangGraph selection but grants no live authority.

Failure behavior is:

| Condition | Result |
|---|---|
| Invalid schema/profile, arbitrary field | `CONFIG_SCHEMA_INVALID` |
| Unknown registered ID | `UNKNOWN_COMPONENT_ID` |
| Duplicate or conflicting declaration | `CONFIGURATION_CONFLICT` |
| Wrong profile/category/required workflow form | `UNSUPPORTED_COMPOSITION` (or earlier deterministic duplicate conflict) |
| Version mismatch | `INCOMPATIBLE_COMPONENT_VERSION` |
| Required or fail-startup dependency missing | `REQUIRED_COMPONENT_UNAVAILABLE` |
| Explicit optional recorded dependency absence | immutable `UNAVAILABLE` resolution; no fallback |
| Broken selected export | `COMPONENT_IMPORT_FAILED` |
| Unrelated internal `ModuleNotFoundError` | propagated as a programming defect |
| Secret-bearing configuration | `SECRET_CONFIGURATION_INVALID` |

## Identity and replay proof

`configuration_fingerprint` identifies the canonical requested config and the
non-secret facade authority policy. `startup_fingerprint` identifies that config
plus actual import-resolved/unavailable outcomes. Availability can therefore
change startup identity without rewriting requested configuration identity.
Neither identity is the R3 run-composition fingerprint, a domain semantic
fingerprint, a capture checksum or a whole-environment/SBOM hash.

`StartupComposition.model_dump_json()` round-trips through
`replay_startup_composition()` without optional imports, sockets, facade startup
or runtime construction. Fingerprint tampering and invalid recorded structure
fail validation. R3 recorded replay remains separately registry- and
provider-independent.

## Validation evidence

| Gate | Result |
|---|---:|
| Dedicated R5 | 44 passed |
| R1 required-scope regression | 8 passed |
| R2 descriptor/catalog parity | 14 passed |
| R3 composition/replay | 12 passed |
| R4 optional-import isolation | 15 passed |
| Combined R1–R5 selection | 93 passed in 72.73s |
| Facade | 71 passed |
| Shell | 89 passed |
| Workflows | 62 passed |
| Agents | 270 passed |
| A4 | 37 passed |
| A5 | 52 passed |
| Full suite | 2,320 passed in 708.14s |
| `python -m compileall src scripts` | passed |
| `ruff check src tests scripts` | passed |
| `mypy src tests` | 541 files; no issues |
| `python -m pip check` | no broken requirements |
| `uv lock --check` | 71 packages resolved; synchronized |
| Documentation links | 123 Markdown files; 984 local links; zero missing |
| Deferral integrity | 58 unique sequential IDs; valid status vocabulary |
| Forbidden imports | zero violations in audited core/agent/facade/Shell/A4/A5/baseline/contract surfaces |
| Secret scan | zero credential-like assignments in the R5 changed surface |
| Frozen A4/A5 parity | no relevant difference from `tiaf-a5-baseline` |
| `git diff --check` | passed |

No live provider, model or broker call was made. Validation uses the repository
`.venv/bin` tools. The full suite and static/documentation/security checks were
rerun after closure documentation synchronization.

## Closure status

```text
A5 FROZEN
R1 DONE
R2 DONE
R3 DONE
R4 DONE
R5 DONE
A6 ACTIVE / NEXT — NOT_IMPLEMENTED
```

The cross-cutting pre-A6 pluggability hardening track is complete.

## Residual risks

- R5 proves selected importability, not external credentials, entitlement,
  transport health or live-provider readiness.
- Startup metadata is not a signature and does not fingerprint the entire Python
  environment or external SDK dependency graph.
- Trusted Python can deliberately violate private-member conventions; TI is not
  an in-process hostile-code sandbox.
- Adapter-specific construction and live service composition remain explicit
  trusted engineering responsibilities outside this captured owner entry.
- HOT mutation, remote configuration/discovery, recurring monitoring and future
  peer publication remain separately deferred/gated.

No new deferral is needed and no existing deferral status changes.

## Files changed by acceptance

The acceptance pass adds this record and synchronizes current status/navigation
in `README.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`,
`docs/IMPLEMENTATION_ROADMAP.md`, `docs/MILESTONES.md`,
`docs/TIAF_CAPABILITY_MAP.md`, `docs/TIAF_DEFERRAL_REGISTER.md`,
`docs/TIAF_DEPLOYMENT_ARCHITECTURE.md`, `docs/TIAF_IMPLEMENTATION_TARGETS.md`,
`docs/TIAF_MONITORING_ARCHITECTURE.md`, `docs/TIAF_PLUGGABILITY_ARCHITECTURE.md`,
`docs/TIAF_THESIS.md`, `docs/TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md`, the R5
implementation record and `docs/TRADINGINTELLIGENCE_ROADMAP.md`. The implementation file inventory remains
in the R5 implementation record. No acceptance-driven runtime/test change was
required.

No commit, tag or push was performed.

## Exact next prompt title

```text
TIAF A6 — TRADE EXPRESSION INTELLIGENCE ARCHITECTURE PASS
```

A6 is not implemented by this acceptance pass.
