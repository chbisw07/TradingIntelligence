# TIAF Pluggability R4 — Optional Adapter Import Isolation

## Status and decision boundary

**R4 ACCEPTED / DONE.** This bounded pre-A6 pass isolates
optional adapter imports and package dependencies. It does not select configured
implementations, create a plugin loader, add HOT loading, grant provider/model
authority, or start R5/A6.

The independent
[acceptance review](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION_ACCEPTANCE.md)
verified the implementation and returned `READY_TO_CLOSE_PLUGGABILITY_R4`.

```text
A5 FROZEN
R1 ACCEPTED
R2 ACCEPTED
R3 ACCEPTED
R4 ACCEPTED / DONE
R5 ACTIVE / NEXT
A6 NOT_IMPLEMENTED
```

No live provider, model, broker, network, commit, tag, or push operation is part
of this implementation.

## Audit inventory and classification

The audit searched all application imports and packaging declarations. The
classification is about third-party import/startup coupling, not capability
authority or runtime health.

| Surface | Before R4 | After R4 | Reason |
|---|---|---|---|
| Pydantic contracts, deterministic baseline, serial workflow, facade, Shell, replay and A5 | `REQUIRED_CORE` | `REQUIRED_CORE` | Baseline application semantics; Pydantic remains the sole mandatory package dependency. |
| Dhan market-data adapter (`httpx`, `pydantic-settings`) | `OPTIONAL_NOT_ISOLATED` | `OPTIONAL_ISOLATED` | Public `tiaf.data.providers` and Dhan package exports now resolve implementation modules only when the named export is selected. |
| Official-document HTTP transport (`httpx`) | `OPTIONAL_NOT_ISOLATED` | `OPTIONAL_ISOLATED` | Provider-neutral official-source contracts and normalizers load without the HTTP transport. |
| Tapetide MCP connector (`mcp`, `python-dotenv`) | `OPTIONAL_NOT_ISOLATED` | `OPTIONAL_ISOLATED` | Provider adapter/protocol remains importable; connector SDK and credential helpers load only on connector selection. |
| Yahoo MCP connector (`mcp`) | `OPTIONAL_NOT_ISOLATED` | `OPTIONAL_ISOLATED` | Provider adapter, symbol mapper and normalizer remain core-safe; MCP loads only on connector selection. |
| LangGraph workflow adapter (`langgraph`, `langsmith`) | `OPTIONAL_NOT_ISOLATED` at adapter-module import | `OPTIONAL_ISOLATED` | The adapter module itself is import-safe; framework symbols resolve only when `run_langgraph` is invoked. |
| Fixture providers, provider-neutral protocols/normalizers and deterministic reasoning gateways | `NOT_APPLICABLE` | `NOT_APPLICABLE` | They have no optional third-party implementation dependency. |
| External model SDK adapters | `NOT_APPLICABLE` | `NOT_APPLICABLE` | No production external model SDK adapter exists in repository scope. |

No `OPTIONAL_NOT_ISOLATED` application boundary remains in the audited source.
Direct imports of concrete implementation modules are considered explicit
low-level adapter selection; supported callers use the stable public package
exports.

## Import-isolation design

`tiaf.optional_adapters` is a dependency-free boundary containing:

- frozen static `OptionalAdapterDescriptor` metadata;
- a deterministic catalog that does not import or probe implementations;
- a narrow attribute loader used by lazy public package exports; and
- a compact typed failure taxonomy.

The Dhan and market-intelligence provider package `__init__` modules preserve
their existing `__all__` names and type-checking visibility. At runtime they
load transport-backed modules through module-level `__getattr__` only when an
export is requested, then cache the resolved object. Provider-neutral adapters,
contracts, fixture providers, normalizers and protocols continue to import
normally.

The LangGraph adapter follows the same rule inside `run_langgraph`. Importing
`tiaf.workflows`, importing the optional adapter module, running the serial
workflow, and recorded replay do not import LangGraph or LangSmith.

There is no import-time network connection, adapter construction, credential
read, provider registration, authority mutation, or runtime health claim.

## Missing-package and runtime failures

Supported public adapter selection translates only a known missing SDK import
into:

```text
OPTIONAL_DEPENDENCY_MISSING
  adapter_id=<selected adapter>
  dependency=<missing import root>
```

Unknown static adapter IDs use `UNSUPPORTED_ADAPTER`; a malformed installed
implementation export uses `OPTIONAL_ADAPTER_IMPORT_FAILED`. An unrelated
`ModuleNotFoundError` arising inside adapter code is deliberately not swallowed
or relabeled. Existing connector/provider runtime errors continue to distinguish
credentials, timeout, rate limit, schema drift and transport failures after an
adapter has loaded.

The error text contains only stable adapter/dependency identifiers. Missing
Yahoo never selects Tapetide, missing Dhan never selects another market-data
provider, and missing LangGraph never changes the requested workflow. Any
fallback remains the responsibility of an explicit existing routing policy.

## Catalog, R2 and R3 compatibility

`optional_adapter_catalog()` enumerates five implementation dependency surfaces
without importing any of them. It is static metadata, not an executable plugin
registry, selection policy, availability probe, facade capability, or authority
grant. Trusted startup selection/configuration remains R5.

R2 facade discovery remains exactly eight operations in its deterministic order.
No new `LIVE_READ`, readiness, registration, entitlement, or authority claim is
made. The optional-adapter catalog does not change R2 descriptor schemas.

R3 composition contracts, fingerprints, captures and pinned verification are
unchanged. Recorded replay remains registry-, provider-, network-, and optional-
SDK-independent. Optional package installation after capture cannot alter the
meaning of recorded participation.

## Provider fabric, workflow and Shell results

- A3 specialists/domain contracts import no Dhan, Yahoo, Tapetide, MCP or HTTP
  transport implementation.
- Provider-specific symbol/normalization/provenance semantics remain in their
  existing adapters; no provider was redesigned.
- Serial orchestration and replay work with LangGraph/LangSmith blocked.
- Shell help, `capabilities list`, `baseline assess`, and `position assess` work
  with all audited optional packages blocked.
- Selecting an absent optional adapter fails locally and explicitly; unrelated
  capability execution continues.
- A5 source and deterministic semantic/replay behavior are unchanged from
  `tiaf-a5-baseline`.

## Packaging

The base dependency set is now only `pydantic`. Integration packages are grouped
under explicit extras:

| Extra | Provides |
|---|---|
| `data-provider-dhan` | Dhan HTTP transport and settings support |
| `market-intelligence-http` | Official-document HTTP transport |
| `market-intelligence-mcp` | Yahoo/Tapetide MCP connectors and Tapetide dotenv support |
| `orchestration` | Pinned LangGraph plus its directly imported LangSmith dependency |
| `providers` | All current Dhan/HTTP/MCP provider dependencies |
| `dev` | Quality tools plus all provider dependencies used by the full test suite |

Examples:

```bash
python -m pip install -e .
python -m pip install -e '.[data-provider-dhan]'
python -m pip install -e '.[market-intelligence-mcp]'
python -m pip install -e '.[providers,orchestration]'
python -m pip install -e '.[dev,orchestration]'
```

This preserves source-level public adapter import names for installations that
include the corresponding extra. It intentionally stops forcing all live
integration SDKs into a baseline installation. `uv.lock` records every extra.

## Security and frozen-baseline protection

Import/discovery paths load no `.env`, credentials or network transports.
Connector-specific credential handling is reached only after explicit connector
selection. Errors contain no configuration values. Capability metadata grants
no permission, and this pass adds no broker/model operation.

`src/tiaf/a4` and `src/tiaf/a5` are untouched. Existing R1 required-scope, R2
descriptor/catalog and R3 composition/replay contracts remain compatible. The
public/engineering facade catalog remains exactly eight operations.

## Validation and residual boundary

The dedicated R4 suite contains 15 tests covering core imports, Shell help and
governed commands, baseline/position/replay continuity, static enumeration, typed
selection failures, unsupported IDs, no silent fallback, recorded replay,
LangGraph isolation, coding-defect visibility, broken-export classification,
extras and public-export compatibility.

| Check | Result |
|---|---:|
| Dedicated R4 tests | 15 passed |
| Facade | 71 passed |
| Workflows | 62 passed |
| Agents | 270 passed |
| A3 hardening | 61 passed |
| A4 | 37 passed |
| A5 | 52 passed |
| Full suite | 2,276 passed |
| R1 regression | 8 passed |
| R2 descriptor/catalog parity | 14 passed |
| R3 composition/replay | 12 passed |
| Selected replay/socket isolation | 6 passed |
| `.venv/bin/python -m compileall src scripts` | passed |
| `ruff check src tests scripts` | passed |
| `mypy src tests` | 535 source files; no issues |
| `.venv/bin/python -m pip check` | no broken requirements |
| `uv lock --check` | resolved 71 packages; synchronized |
| Documentation links | 121 Markdown files; 960 local links; zero missing |
| Deferral integrity | 58 sequential unique IDs; all statuses valid |
| Forbidden-import audit | 102 core/agent/facade/Shell/A4/A5 files; zero violations |
| Changed-surface secret scan | zero credential-like assignments |
| Frozen A4/A5 source parity | no differences from `tiaf-a5-baseline` |
| `git diff --check` | passed |

Residual risks are intentionally bounded:

- actual installed adapter runtime health still depends on its external service,
  credentials and transport environment;
- direct imports of private implementation modules are not a core-safe API;
- static metadata does not prove installation/readiness; and
- trusted COLD selection, enablement, precedence and composition ownership remain
  R5, not R4.

**R5_UNTOUCHED**

Exact next implementation:

**TIAF PLUGGABILITY — R5 COLD OWNERSHIP / CONFIGURATION**
