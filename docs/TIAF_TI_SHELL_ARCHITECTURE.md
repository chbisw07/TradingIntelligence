# TIAF TI_SHELL Architecture

## Status, decision and compatibility

**Approved architecture for `POST_A4_PRE_A5 — TI_SHELL v0.1`, 2026-09-11
(Asia/Kolkata). Runtime status: implemented on 2026-09-12.** The decision record is the
[POST_A4_PRE_A5 review](TIAF_POST_A4_PRE_A5_TI_SHELL_ARCHITECTURE_REVIEW.md).
The implementation record is
[TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md).

The implementation target is a command-first local engineering interface over
the accepted `tiaf-a4-baseline` (`494d968`). It must not modify A0 contract
schema `1.0`, package version `0.1.0`, existing capability versions, canonical
results, fingerprints, policies or milestone semantics. Shell grammar version,
Shell output schema version, facade capability version, domain schema version
and package version are separate concepts.

## 1. Thesis and boundaries

TI_SHELL v0.1 is a small stateful interaction adapter:

```text
one-shot argv ─┐
               ├─> closed parser -> normalized ShellCommand -> dispatcher
REPL + shlex ──┘                                      |
                                                     v
                                   caller-bound LocalFacadeClient
                                                     |
                                      typed facade request/result
                                                     |
                           exact-result holder -> allowlisted renderer
```

The Shell owns command syntax, transient defaults, invocation correlation,
bounded last-result state and presentation. The facade continues to own
capability discovery, admission, authority/budget intersection, lifecycle,
logical artifacts, composition, safe errors and dispatch. TI_CORE continues to
own evidence and intelligence meaning.

The Shell is not:

- an intelligence, scoring, recommendation, ranking or position engine;
- another facade, service layer, workflow planner or dependency container;
- a provider/router/model/tool/broker client;
- a private package/object explorer;
- a Python evaluator, operating-system shell or script runner;
- an HTTP/Web server, database, queue, scheduler or durable job owner; or
- permission to expose A4.2 live enrichment, A5, A6, A7 or execution behavior.

No command may import or invoke a specialist, provider, gateway, Planner,
Arbitrator helper, artifact store or broker object. The only intelligence call
edge is the injected caller-bound `LocalFacadeClient`.

## 2. Deployment and startup composition

v0.1 runs in the same trusted Python application process as the accepted local
facade. It adds no transport. The primary Python composition seam accepts an
already constructed caller-bound client and a frozen Shell bootstrap config.
The console entry point may load an operator-owned local bootstrap document to
construct the existing `TrustedFacadeConfig`, start its owner and select exactly
one configured caller. This is process bootstrap, not a command field or an
authorization mechanism.

The bootstrap document may contain only:

- an accepted `TrustedFacadeConfig` with logical artifacts;
- the one configured `caller_id` to bind;
- an operator-rooted directory for pure baseline request documents;
- a bounded session-ledger limit, default 32 and maximum 64; and
- presentation defaults that grant no authority.

It contains no provider credentials, model keys, broker handles, dynamic import
paths, functions or plugin names. The console bootstrap path is never copied to
requests, results, history or trace. Anyone who can replace the operator config
already shares the trusted local process boundary; v0.1 does not claim to
sandbox hostile local Python users.

The owner is started once, the Shell obtains one caller-bound client, and
shutdown is coordinated once after the one-shot invocation or REPL exits. Shell
code never reaches back through the client to the owner.

## 3. Interaction mode, profile and model

v0.1 has one implicit interaction mode: `COMMAND`. It does not accept
`--mode nlp`, `--mode mixed`, an `ask` command, or unrecognized free text.

These concepts remain independent:

| Concept | Owner and v0.1 meaning |
|---|---|
| Interaction mode | Shell parser; fixed to `COMMAND`. |
| Analysis objective/horizon | Canonical request scope; explicit or session default and recorded. |
| Profile | Requested facade `profile_ref`; admission intersects it with caller/operator policy. It grants nothing. |
| Model policy | Trusted facade admission/result metadata; no Shell selector and all current capabilities are no-model. |
| Output view | Presentation only; cannot change the invoked request or result. |
| Engineering access | Facade descriptor/interface and grants; never a Shell mode or flag. |

A future NLP or mixed adapter must produce the same normalized `ShellCommand`,
surface ambiguity instead of guessing, and operate with no more authority than
the bound caller. It requires a separate accepted Interaction-Agent contract,
model/privacy/budget policy and replay/evaluation design. The command dispatcher
does not depend on that future work.

## 4. Command grammar

Grammar version `0.1` is deliberately conventional:

```text
ti [BOOTSTRAP_OPTIONS] [--output human|json] COMMAND [SUBCOMMAND] [OPERAND] [OPTIONS]
```

`BOOTSTRAP_OPTIONS` is closed to `--config PATH` and `--version`. `--config`
identifies the operator-owned local bootstrap document described in §2; it is
required before entering the REPL or invoking a capability, and optional for
local help/version. It is not a facade request field and is never retained or
rendered. With a config and no command, `ti` enters the REPL; without a config or
command it prints safe usage and exits. There is no implicit current-directory
or home-directory config search.

Inside the REPL, omit `ti`. One-shot `argv` is passed directly to the shared
parser. REPL lines are tokenized once with POSIX `shlex.split` and passed to the
same parser and dispatcher. Strings are never joined and reparsed.

Rules:

- command/subcommand/option names are lowercase kebab-case and case-sensitive;
- enum values are accepted case-insensitively and normalized to their canonical
  contract value;
- canonical symbols are uppercase provider-neutral values such as `RELIANCE`;
  provider suffixes such as `.NS` are invalid at this layer;
- qualified IDs and logical artifact refs are opaque complete tokens;
- timestamps must be aware ISO-8601 values; canonical contracts normalize them
  to `Asia/Kolkata`; naive values fail before invocation;
- quoting/escaping follows the host shell for one-shot use and POSIX `shlex` in
  the REPL;
- repeated options, unknown options, extra operands and ambiguous abbreviations
  are errors; `allow_abbrev=False` is required;
- v0.1 has no command aliases except REPL `quit` as an exact synonym for `exit`;
  the standard `-h` is the only short option;
- no `--flag=true`, shell expansion, glob expansion, command substitution,
  environment interpolation or arbitrary pipeline is performed by the Shell;
- human output is UTF-8 plain text without ANSI color; JSON output is one UTF-8
  object on stdout; and
- ordinary diagnostics go to stderr so machine-readable stdout stays clean.

The parser is an explicit declarative catalog backed by standard-library
`argparse` with `exit_on_error=False`. A small custom adapter converts parser
errors to `ShellError`; parser actions do not call capabilities. No Click,
Typer, REPL framework or dynamic command discovery is needed.

## 5. Command taxonomy

The minimum coherent v0.1 surface is:

```text
help [TOPIC]
use SYMBOL
set FIELD VALUE
unset FIELD
show context
capabilities list
capabilities describe CAPABILITY_ID

baseline assess --request-file RELATIVE_JSON [SCOPE_ASSERTIONS]
opportunity assemble --artifact-ref QUALIFIED_ID [SCOPE_OPTIONS]
a4 project --artifact-ref QUALIFIED_ID [SCOPE_OPTIONS]
a4 evaluate --artifact-ref QUALIFIED_ID [SCOPE_OPTIONS]
replay recorded --artifact-ref QUALIFIED_ID [SCOPE_OPTIONS]
replay verify --artifact-ref QUALIFIED_ID [SCOPE_OPTIONS]

show last
explain last
trace last
refresh last
exit
quit
```

`FIELD` is closed to `subject`, `objective`, `horizon`, `as-of`, `profile-ref`,
`authority-ref`, `position-context-ref`, and `output`. `unset` restores the
operator/bootstrap default where one exists and otherwise removes the default.
`show context` displays requested defaults, never effective grants.

Common `SCOPE_OPTIONS` are `--subject`, `--objective`, `--horizon`, `--as-of`,
`--profile-ref`, `--authority-ref`, and optional `--position-context-ref`.
Command options override session defaults for that invocation only. Required
values missing from both places cause a validation error. The Shell creates new
request and correlation IDs; users cannot spoof run/admission/budget IDs.

For `baseline assess`, subject, horizon and `as_of` are derived from the
validated `DeterministicBaselineRequest`. Corresponding flags/defaults are only
assertions: a mismatch fails rather than rewriting the request. Objective must
be `OPPORTUNITY`. Profile and requested authority remain explicit facade scope.

`exit` and `quit` are REPL controls. In one-shot use they terminate successfully
without invoking Core. `show last`, `explain last`, `trace last` and `refresh
last` require session state; a fresh one-shot process reports `NO_PRIOR_RESULT`.

There is no generic `invoke CAPABILITY`, dotted Python path, direct specialist
command, `research`, `orchestrate`, `rank`, `health`, `ask`, `model`, `provider`,
`broker`, `order`, `dry-run`, `show-plan`, pipe or batch command in v0.1.

## 6. Command-to-capability mapping

Every capability-backed adapter constructs exactly the named accepted request
and accepts exactly the named accepted result:

| Shell command | Facade operation | Interface/effect | Input rule | Result ownership |
|---|---|---|---|---|
| `capabilities list` | `LocalFacadeClient.list_capabilities(CapabilityListRequest)` / `capabilities.list` | public / `PURE` | profile and requested authority only | exact `CapabilityListResult` |
| `capabilities describe ID` | same filtered `capabilities.list`, then exact-ID selection | public / `PURE` | cannot consult static/private catalog directly | exact descriptor from the returned result |
| `baseline assess` | `invoke(BaselineAssessRequest)` / `baseline.assess` | public / `PURE` | bounded validated typed request document | exact `BaselineAssessResult` |
| `opportunity assemble` | `invoke(OpportunityAssembleRequest)` / `opportunity.assemble` | public / `CAPTURED_READ` | one admitted A3.8 capture logical ref | exact `OpportunityAssembleResult` |
| `a4 project` | `invoke(A4InputProjectRequest)` / `a4_input.project` | public / `CAPTURED_READ` | one admitted foundation build-input logical ref | exact `A4InputProjectResult` |
| `a4 evaluate` | `invoke(A4EvaluateRequest)` / `a4.evaluate` | public / `CAPTURED_READ` | one admitted foundation capture logical ref | exact `A4EvaluateResult` |
| `replay recorded` | `invoke(RecordedReplayRequest)` / `replay.recorded` | public / `CAPTURED_READ` | one admitted A3 package/foundation capture logical ref | exact `RecordedReplayResult` |
| `replay verify` | `invoke(ReplayVerifyRequest)` / `replay.verify` | engineering / `CAPTURED_READ` | one admitted A3 package logical ref and engineering grant | exact `ReplayVerifyResult` |

Local help/context/last-result commands invoke no capability. There is no direct
mapping to A4.2 because it is intentionally not in the facade catalog. A Shell
command adapter is added only after its facade descriptor, typed contracts,
effect, replay, admission and safe error behavior are accepted.

### Pure baseline request exception

`baseline.assess` is the only published operation whose accepted request embeds
a large caller-supplied typed evidence request rather than naming a trusted
artifact. The Shell therefore accepts `--request-file` only for this command:

1. the path must be relative to the frozen operator `baseline_request_root`;
2. resolved containment is checked after symlink resolution;
3. the target must be a regular file within a fixed byte limit;
4. one JSON object must validate as `DeterministicBaselineRequest`;
5. forbidden secret/path/URL values still fail facade safe-input validation;
6. the validated model, not the path or untyped mapping, is retained for
   explicit refresh; and
7. the Shell never writes, repairs or updates the document.

Absolute paths, `..`, URLs, stdin code, YAML, pickle and dynamic loaders are not
accepted. This narrow adapter does not become a second artifact repository.

## 7. Session contract and lifecycle

The session is application-owned, request-external and transient. Its conceptual
immutable snapshot contains:

```text
session_id
started_at
command_grammar_version = "0.1"
requested defaults:
  subject, objective, horizon, as_of,
  profile_ref, authority_ref, position_context_ref, output
last normalized facade-backed ShellCommand (optional)
last exact FacadeResult (optional)
last ShellInvocationRecord (optional)
bounded tuple[ShellInvocationSummary, ...]
```

An invocation record includes an optional `parent_shell_invocation_id`; explicit
refresh uses it to relate the new invocation without rewriting facade metadata.

The runtime may replace the session snapshot atomically after a command; public
contract collections are tuples. No mutable global current request exists.
Session state is never passed as authority. Each invocation materializes a fresh
typed facade request and the facade rechecks the current caller grant/operator
policy/artifact access.

Only the most recent exact result is retained. The bounded ledger records safe
command/capability/run/status/timing identities, not request JSON, evidence,
raw errors, paths, tokens or credentials. v0.1 exposes no general `history`
command; the ledger exists for lifecycle/audit testing and possible later safe
projection. Session end erases defaults, last result and ledger.

`refresh last` means **new invocation of the exact normalized prior command**:

- new request/correlation/facade run/Shell invocation identities;
- same typed baseline input snapshot or same logical artifact ref;
- same semantic scope including the original `as_of`;
- fresh facade discovery/admission and artifact access checks; and
- no provider/model/broker call and no claim that data became current.

Changed session defaults do not silently change refresh. A user must issue a new
operation command to use changed defaults. If the prior command was not
capability-backed, or the grant was revoked, refresh fails explicitly.

## 8. Result ownership and rendering

The exact facade result remains canonical. The Shell neither mutates it nor
creates a competing domain result/fingerprint. The last-result slot holds that
typed value. Renderers are pure functions selected by concrete accepted result
type; generic reflection, `repr`, arbitrary field paths and provider payload
dumping are forbidden.

### JSON

`--output json` emits a versioned `tiaf.shell.result-envelope` object containing:

- Shell schema version `1.0` and grammar version `0.1`;
- Shell invocation and command identity;
- capability ID/version and facade request/run/correlation identity;
- facade status/effect and timestamps;
- the exact `result.model_dump(mode="json")` under `result`; and
- no duplicated/recomputed intelligence fields.

Tests reconstruct the concrete facade result from `result` and require equality.
Shell envelope serialization is deterministic, but it is never used as a Core
semantic fingerprint. stdout contains only the JSON object; warnings and process
diagnostics use stderr.

### Human summary

The default renderer displays identity, status/effect, as-of, policy/profile,
usage and the smallest useful typed summary. It must preserve non-action,
partial, stale, insufficient-evidence and conflict states. Type-specific
allowlists include:

- baseline class/direction/scores, component explanation codes and warnings;
- opportunity state/bias/confidence basis, contributions, contradictions,
  completeness, reasons, prerequisites and lineage identifiers;
- source-semantic projection identity, gaps/disputes/confirmation and
  fingerprints;
- A4 execution/disposition, primary and counter thesis, surviving theses,
  challenge/arbitration findings, residual uncertainty, evidence needs,
  invalidation conditions, failures, usage and fingerprints; and
- replay kind/integrity/fingerprint and verification outcome.

The renderer does not calculate trading conclusions, collapse disagreement,
invent prose, repair gaps, fetch source details or create probabilities/targets.

## 9. Explain and trace

`show last` renders the same exact object already held in the session. It never
re-invokes a capability. Identity/equality tests must prove that claim.

`explain last` builds a versioned, deterministic presentation projection solely
from allowlisted fields of the held result. It can organize existing reasons,
gaps, warnings, contradictions, thesis/finding links, evidence/source IDs and
invalidation conditions. It cannot add a reason, summarize with a model,
re-score evidence, follow a URL or acquire evidence. Unsupported result types
return `EXPLANATION_UNAVAILABLE`, not reflective fallback output.

`trace last` is intentionally an **invocation summary**, not the deferred
`trace.inspect` capability. It renders allowlisted `InvocationMetadata`: IDs,
capability/version, status/effect, subject/objective/horizon/as-of, profile and
policy references, admitted logical artifact refs, warnings/gaps, timing and
usage/cost knowledge. It does not expose private objects, stack traces, config,
filesystem paths, raw artifact contents, provider requests/responses or secrets.

Rich numbered citations, hyperlinks, bibliography, document retrieval and Web
reports remain the deferred part of DEF-054. v0.1 may display already admitted
canonical evidence/source/claim identifiers and labels; it may not re-research
or imply that a locator was opened.

## 10. Discovery, engineering visibility and authority

`capabilities list` always calls the facade for the current profile/requested
authority and displays only the returned descriptors. `capabilities describe`
selects from that returned tuple. Shell help may describe local grammar, but its
“available capability commands” view is filtered from discovery and does not
read `capability_catalog()` directly.

`replay verify` is the only current engineering operation. The Shell may parse
the command for every user, but it must not claim availability before filtered
discovery and must invoke it only through the facade. The facade remains the
final decision and must reject missing engineering scope even if Shell state is
stale. There is no `--developer`, role switch, hidden environment bypass or
prompt phrase that grants access.

Public `trace last` displays only data already present in that caller's returned
safe result. Future deeper trace, graph, normalization or ledger operations need
separate engineering facade descriptors and redacted typed results.

## 11. A4 and future milestone seams

`a4 project` and `a4 evaluate` remain distinct because projection and arbitration
are distinct accepted capabilities. The Shell does not combine them, call the
internal A4.2 bridge, replace a captured projection, or turn an evidence need
into live acquisition. A4 input/result/fingerprints must be byte/semantic-equal
to direct facade invocation. Explain must retain counter-theses, challenges,
conflict, residual uncertainty and non-action dispositions.

Future commands are added capability-first:

| Reserved family | Earliest owner | v0.1 behavior |
|---|---|---|
| `position assess` | [A5.2 governed publication](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md) | authorized captured-read command; no broker lookup/execution |
| other `position ...` | A5/TM/A6 as applicable | unknown/unavailable command |
| `option ...` | A6 expression/selection | unknown/unavailable command |
| `evaluate ...`, `rank ...` | A7 evaluation/forecasting and DEF-053 resolution | unknown/unavailable command |
| `ask ...` | separately accepted Interaction Agent | unknown/unavailable command |

Reserved words confer no contract promise. When a future descriptor is accepted,
its Shell adapter must declare request construction, effect, replay, rendering,
errors and acceptance tests. A5 is not blocked by Shell implementation.

## 12. Scriptability and versioning

One-shot use is non-interactive: no prompt, confirmation or terminal-dependent
layout. Stable script inputs use long options and stable JSON output. Human
output is explicitly not a parsing contract. Commands do not read stdin except
the terminal line reader in REPL; baseline data uses the bounded request file.

Compatibility rules:

- additive optional JSON envelope fields may be backward-compatible;
- removing/renaming commands, changing option meaning or changing exit meaning
  requires a new Shell grammar version;
- a capability schema/version mismatch fails before rendering;
- Shell adapters bind an explicit supported capability/schema version and never
  silently coerce another version; and
- deprecation follows facade descriptor metadata before a Shell command is
  removed.

## 13. Error model and process exits

Shell parse/state/bootstrap errors use a closed, serializable `ShellError` with
code, safe message, command identity where available and timestamp. Facade
errors retain their original safe record nested by value; private exceptions and
tracebacks are never emitted in ordinary output.

| Exit | Meaning |
|---:|---|
| 0 | Successful Shell/facade operation, including valid `NO_TRADE`, `WAIT`, `ABSTAIN`, `CONFLICTED`, partial/stale/insufficient-evidence domain outcomes. |
| 2 | Command syntax, option, enum, timestamp or typed request validation error. |
| 3 | Facade `PERMISSION_DENIED` or engineering operation denied. |
| 4 | Unknown/unsupported/unavailable capability, no prior result, unsupported explain view or capability/schema incompatibility. |
| 5 | Baseline request-file safety failure or replay/capture integrity failure. |
| 6 | Budget exceeded, facade/artifact unavailable or sanitized unexpected invocation failure. |
| 130 | User interrupt. No completion is claimed. |

JSON failures use a versioned `tiaf.shell.error` object on stdout only when JSON
was successfully selected; incidental bootstrap failures go to stderr. Exit
codes classify the process outcome, not market advice. `PARTIAL`, `STALE` and
`INSUFFICIENT_EVIDENCE` facade results that are valid returned results exit 0;
the same labels inside a thrown safe error follow their error classification.

## 14. Security and effect controls

- The Shell accepts no secrets, access tokens, API keys, broker credentials,
  provider selection, URLs or arbitrary artifact paths as commands.
- Captured operations accept only qualified logical refs and retain facade
  entitlement/authority/checksum checks.
- The baseline request root is read-only, operator-set, containment checked and
  size bounded.
- No `eval`, `exec`, `subprocess`, shell expansion, dynamic import, reflection,
  arbitrary attribute access or plugin loading exists in the command path.
- The explicit command catalog declares its facade capability and expected
  versions; no callable comes from discovery data.
- All current commands are `PURE` or `CAPTURED_READ`; help/output must show the
  effect. A future `LIVE_READ`/`PERSIST` command requires a separate acceptance
  pass and cannot arrive by generic dispatch.
- Interrupt/disconnect does not assert that already-running work was cancelled.
  Only a returned result is stored as completed.
- Core/facade results and A2/A3/A4 fingerprints remain unchanged.
- There is no broker/order command or imported broker SDK.

## 15. Acceptance design

Implementation acceptance must use direct-facade calls as the parity oracle and
cover at least these deterministic scenarios:

1. one-shot help exits without a facade/provider/model call;
2. `use RELIANCE` records a provider-neutral subject;
3. provider-suffixed `RELIANCE.NS` is rejected;
4. `set as-of` accepts aware UTC/other-zone input and canonicalizes to Kolkata;
5. a naive timestamp is rejected before facade invocation;
6. set/unset/show context is isolated between Shell sessions;
7. capability listing equals the facade's permission-filtered result;
8. describe cannot reveal a descriptor absent from filtered discovery;
9. a denied capability remains denied despite session/profile/output changes;
10. baseline Shell result equals direct-facade result for the same typed request;
11. baseline absolute/traversal/symlink-escape/oversize inputs are rejected;
12. opportunity assembly has exact request/result/fingerprint parity;
13. A4 input projection has exact request/result parity;
14. A4 evaluation has exact request/result/fingerprint parity;
15. `show last` uses the identical held result and causes no invocation;
16. `refresh last` creates new request/run identity, rechecks admission and
    preserves input/as-of without provider/model access;
17. explain uses structured fields only and preserves gaps/contradictions;
18. unsupported explain returns an explicit safe error, not reflection;
19. trace shows facade metadata and hides secrets, paths, object reprs and stacks;
20. recorded replay completes with network/providers/models unavailable;
21. replay verification is denied without an engineering grant;
22. replay verification works through the facade with the exact engineering grant;
23. JSON envelope reconstructs the exact concrete facade result;
24. JSON stdout is stable and uncontaminated by human diagnostics;
25. REPL and one-shot tokens produce equal normalized commands and requests;
26. malformed/unknown/abbreviated commands fail cleanly with exit 2;
27. a valid `NO_TRADE`, `WAIT`, `ABSTAIN` or `CONFLICTED` result exits 0;
28. session defaults and bootstrap presentation settings grant no authority;
29. every current capability invocation reports zero model calls/tokens/cost;
30. no provider, broker, Web, MCP or model package is imported by `tiaf.shell`;
31. no command can execute Python, a process, a URL, a glob or a shell pipeline;
32. A4 primary/counter thesis, dissent, evidence needs and invalidation survive
    human and JSON rendering;
33. direct-facade A2/A3/A4 results and semantic fingerprints remain unchanged;
34. `position`, `option`, A3 `rank`, `ask` and private specialist commands remain
    unavailable;
35. revoked admission between original invocation and refresh fails safely; and
36. Ctrl-C returns 130 without recording an in-flight operation as completed.

Tests must also include package-boundary import checks, command-catalog parity
against the accepted facade descriptors, golden human projections, JSON schema
round-trips, concurrent session isolation and property/fuzz cases for parser
tokens and path containment. Existing facade/domain tests remain authoritative;
Shell tests supplement rather than replace them.

## 16. Explicit implementation package

The implementation may add only an adapter-focused package such as:

```text
src/tiaf/shell/
  contracts.py       # Shell-only command/session/envelope/error contracts
  catalog.py         # explicit command specs and capability bindings
  parsing.py         # argparse/shlex normalization
  session.py         # transient isolated state
  dispatch.py        # typed request construction -> LocalFacadeClient only
  render.py          # allowlisted human/JSON/explain/trace projections
  runtime.py         # shared one-shot/REPL loop and lifecycle
  cli.py             # console/bootstrap adapter
  __main__.py
```

Names may be refined during implementation, but boundaries may not. No new
third-party dependency or runtime service is justified. The exact next work
prompt is:

**`POST_A4_PRE_A5 — TI_SHELL v0.1 Command-First Local Engineering Interface Implementation`**
