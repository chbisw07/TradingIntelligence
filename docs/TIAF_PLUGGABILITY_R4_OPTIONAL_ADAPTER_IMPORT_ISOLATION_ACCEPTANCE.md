# TIAF Pluggability R4 — Optional Adapter Import Isolation Acceptance

## Decision and boundary

**READY_TO_CLOSE_PLUGGABILITY_R4**

Independent acceptance completed on 2026-09-13 (Asia/Kolkata). R4 is correct,
bounded, package-safe and backwards-compatible. This review made no live
provider, model, broker or network call and did not implement R5, A6, HOT
loading, startup composition ownership or configuration precedence.

```text
A5 FROZEN
R1 ACCEPTED
R2 ACCEPTED
R3 ACCEPTED
R4 ACCEPTED / DONE
R5 ACTIVE / NEXT
A6 NOT_IMPLEMENTED
```

## Independent findings

| Acceptance surface | Verdict | Evidence |
|---|---|---|
| Optional-adapter inventory | PASS | Required core, five `OPTIONAL_ISOLATED` integrations and not-applicable provider-neutral surfaces are explicitly classified. No in-scope `OPTIONAL_NOT_ISOLATED` boundary remains. |
| Core import isolation | PASS | With `httpx`, `mcp`, `dotenv`, `pydantic_settings`, `langgraph` and `langsmith` synthetically blocked, `tiaf`, baseline, facade, Shell, A4, A5, provider namespaces, serial workflows and replay imports succeed. Packages were not uninstalled. |
| Lazy implementation loading | PASS | Static metadata and public package imports do not import or instantiate transport implementations. Lazy public exports and `run_langgraph()` are the explicit implementation-use boundaries. |
| Failure taxonomy | PASS | Known missing roots become `OPTIONAL_DEPENDENCY_MISSING`; unknown IDs become `UNSUPPORTED_ADAPTER`; a missing export in an installed module becomes `OPTIONAL_ADAPTER_IMPORT_FAILED`. An unrelated internal `ModuleNotFoundError` escapes unchanged. |
| No silent fallback | PASS | Selecting unavailable Yahoo does not load Tapetide or select another provider. Existing explicit routing policy remains the only fallback owner. |
| Catalog behavior | PASS | Five deterministic adapter descriptors enumerate without probes/imports; failure does not mutate the catalog. The permission-filtered R2 facade catalog remains exactly eight operations and does not claim runtime readiness. |
| Replay and R3 | PASS | Recorded replay remains registry-, provider-, model-, optional-SDK- and network-independent. R3 composition identity, capture compatibility and pinned verification are unchanged. Historical captures were not rewritten. |
| A3 provider fabric | PASS | Specialists and domain contracts do not import provider SDKs. Concrete transport ownership, ticker mapping and normalization remain adapter-local; no-provider/no-model operation remains valid. |
| Workflow boundary | PASS | Serial orchestration and workflow-core imports work without LangGraph/LangSmith. Explicit LangGraph invocation loads the optional framework or fails locally and precisely. Domain semantics are unchanged. |
| Shell and facade | PASS | Help, `capabilities list`, `capabilities describe`, `baseline assess`, `position assess` and captured `replay recorded` work with every audited optional SDK blocked. Startup performs no provider/model/broker operation. |
| Packaging | PASS | `pydantic` is the sole mandatory application dependency. Named Dhan, HTTP, MCP, provider, orchestration and development extras match their adapters; the lock is synchronized. LangGraph transitives are recorded, with no direct LangChain dependency or import. |
| Security and side effects | PASS | Import/discovery reads no credentials, opens no network/session, constructs no adapter and mutates no authority. Error text exposes only stable adapter/dependency identifiers. Adapter presence grants no authority. |
| Frozen A4/A5 | PASS | `src/tiaf/a4` and `src/tiaf/a5` have no diff from `tiaf-a5-baseline`; A4/A5 tests, fingerprints and offline replay remain unchanged. No optional SDK dependency was added to either domain. |
| R1/R2/R3 compatibility | PASS | Required-scope/explicit-absence, discovery metadata/catalog parity, composition envelope and pinned verifier regressions all pass. |

## Import and failure mechanics accepted

The dependency-free `tiaf.optional_adapters` catalog describes these five
implementation surfaces without probing them:

| Adapter ID | Optional roots | Extra |
|---|---|---|
| `provider.market-data.dhan` | `httpx`, `pydantic-settings` | `data-provider-dhan` |
| `provider.market-intelligence.authoritative-http` | `httpx` | `market-intelligence-http` |
| `provider.market-intelligence.tapetide-mcp` | `mcp`, `python-dotenv` | `market-intelligence-mcp` |
| `provider.market-intelligence.yahoo-mcp` | `mcp` | `market-intelligence-mcp` |
| `workflow.langgraph` | `langgraph`, `langsmith` | `orchestration` |

Public provider export names remain compatible for installations containing the
relevant extras. Direct private implementation-module import is an explicit
low-level selection and is not a core-safe API. Static catalog presence is
metadata, not installation health, enablement, authority or runtime readiness.

## Validation

| Check | Result |
|---|---:|
| Dedicated R4 | 15 passed |
| Facade | 71 passed |
| Workflows | 62 passed |
| Agents | 270 passed |
| A3 hardening | 61 passed |
| A4 | 37 passed |
| A5 | 52 passed |
| R1 required-scope regression | 8 passed |
| R2 descriptor/catalog parity | 14 passed |
| R3 composition/replay | 12 passed |
| Selected replay/socket isolation | 6 passed |
| Full suite | 2,276 passed |
| `.venv/bin/python -m compileall src scripts` | passed |
| `.venv/bin/ruff check src tests scripts` | passed |
| `.venv/bin/mypy src tests` | 535 source files; no issues |
| `.venv/bin/python -m pip check` | no broken requirements |
| `.venv/bin/uv lock --check` | resolved 71 packages; synchronized |
| Documentation-link validation | 121 Markdown files; 960 local links; zero missing |
| Deferral integrity | passed; 58 sequential unique IDs and valid statuses |
| Forbidden-import audit | passed; zero violations |
| Changed-surface secret scan | passed; zero credential-like assignments |
| Frozen A4/A5 source parity | passed; no differences from `tiaf-a5-baseline` |
| `git diff --check` | passed |

## Residual risks and next boundary

- Installed adapter runtime health still depends on external service, transport
  and credential conditions and is intentionally not inferred from discovery.
- The static catalog is not a startup binding registry or availability probe.
- Private concrete-module imports remain the caller's explicit low-level choice.
- Trusted COLD selection ownership, enable/disable policy, configuration
  precedence, profiles and startup composition graph belong to R5.

**R5_UNTOUCHED**

Exact next prompt title:

**TIAF PLUGGABILITY — R5 COLD OWNERSHIP / CONFIGURATION**

No commit, tag or push was performed.
