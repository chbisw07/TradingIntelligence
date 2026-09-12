# TIAF TI_SHELL v0.1 Implementation

## Status and scope

`POST_A4_PRE_A5 TI_SHELL v0.1` implements the approved command-first local
engineering interface over the frozen A4 facade. It is an unnumbered application
adapter, not an A4 capability expansion and not an A5 prerequisite.

The implementation preserves four separate version concepts:

- package version: `0.1.0`;
- Shell grammar version: `0.1`;
- Shell result/context/error schema version: `1.0`; and
- existing facade/domain capability and contract versions, unchanged.

There is no NLP, Interaction Agent, LLM, live acquisition, provider client,
remote service, durable session, live position lookup, option selection,
forecasting or broker operation in this slice.

## Placement and call boundary

The package is `tiaf.shell`, with both entry points sharing one parser,
dispatcher and renderer:

```text
argv -------------------> parse_tokens --┐
                                         ├-> ShellDispatcher
REPL line -> shlex.split -> parse_tokens -┘         |
                                                    v
                                      caller-bound LocalFacadeClient
                                                    |
                                                    v
                                       exact typed facade result
                                                    |
                                                    v
                                         allowlisted renderer
```

The package entry points are:

```bash
python -m tiaf.shell ...
ti ...
```

The Shell imports the facade and canonical request contracts needed to build
exact requests. It does not import specialists, providers, MCP/HTTP clients,
models, broker code or A5-A7 packages. Command handlers have one intelligence
call edge: the injected, caller-bound `LocalFacadeClient`.

## Startup and trusted bootstrap

Capability execution needs an explicit operator-owned JSON bootstrap file. No
default path is searched. The frozen `ShellBootstrapConfig` contains exactly:

- the existing `TrustedFacadeConfig`;
- one configured `caller_id`;
- a baseline-request root;
- non-authorizing session defaults; and
- a bounded history limit from 1 to 64, default 32.

The config schema rejects extra fields and carries no provider/model/broker
credentials or dynamic import hooks. A relative baseline root is resolved from
the bootstrap document's directory. Help and version do not require a config.

Typical invocations are:

```bash
python -m tiaf.shell --help
python -m tiaf.shell --version
python -m tiaf.shell --config shell-bootstrap.json capabilities list
python -m tiaf.shell --config shell-bootstrap.json --output json \
  a4 evaluate --artifact-ref artifact:accepted-a4-input
python -m tiaf.shell --config shell-bootstrap.json
```

The last form enters the local `TI> ` REPL. Bootstrap documents are deployment
inputs assembled from the accepted facade configuration; the repository does
not ship a permissive or misleading default.

## Canonical command surface

The executable grammar follows the authoritative architecture exactly. The
short illustrative forms in the implementation brief are not aliases.

```text
help [TOPIC]
use SYMBOL
set FIELD VALUE
unset FIELD
clear context
show context

capabilities list
capabilities describe CAPABILITY_ID

baseline assess --request-file RELATIVE_JSON [SCOPE_ASSERTIONS]
opportunity assemble --artifact-ref QUALIFIED_ID [SCOPE_OPTIONS]
a4 project --artifact-ref QUALIFIED_ID [SCOPE_OPTIONS]
a4 evaluate --artifact-ref QUALIFIED_ID [SCOPE_OPTIONS]
position assess --snapshot QUALIFIED_ID [SCOPE_OPTIONS]
replay recorded --artifact-ref QUALIFIED_ID [SCOPE_OPTIONS]
replay verify --artifact-ref QUALIFIED_ID [SCOPE_OPTIONS]

show last [--json|--reasons|--gaps|--contradictions|--evidence]
explain last
trace last [--cost|--evidence|--timing]
refresh last
exit
quit
```

`FIELD` is closed to `subject`, `objective`, `horizon`, `as-of`, `profile-ref`,
`authority-ref`, `position-context-ref` and `output`. Common scope options are
typed and explicit. Command names and options are case-sensitive; enum values
are case-insensitive and normalize to canonical contract values. Subjects are
uppercase provider-neutral symbols. Aware timestamps from any zone are accepted
and canonicalized by the existing `Asia/Kolkata` contract; naive timestamps are
rejected.

The parser uses standard-library `argparse` with abbreviation disabled and
POSIX `shlex` only for REPL tokenization. It rejects unknown commands/options,
extra operands, repeated options, equals-style options, malformed quoting,
shell expansion/control syntax, provider URLs/suffixes and credential-looking
command arguments. It has no evaluation, import, subprocess or shell escape.

## Capability mapping and request construction

| Shell command | Accepted facade capability | Request source |
|---|---|---|
| `capabilities list` / `describe` | `capabilities.list` | caller profile and requested authority |
| `baseline assess` | `baseline.assess` | validated `DeterministicBaselineRequest` below bounded root |
| `opportunity assemble` | `opportunity.assemble` | authorized logical A3.8 capture ref |
| `a4 project` | `a4_input.project` | authorized logical foundation-input ref |
| `a4 evaluate` | `a4.evaluate` | authorized logical projection-capture ref |
| `position assess` | `position.assess` | authorized logical complete A5 position-request ref |
| `replay recorded` | `replay.recorded` | authorized logical captured-artifact ref |
| `replay verify` | `replay.verify` | authorized engineering logical-artifact ref |

Explicit scope values override session defaults for that request only. Missing
required context fails without guessing. Baseline subject, horizon and `as_of`
come from the validated request document; matching Shell values are assertions,
not rewrites. The baseline path must be relative, remain beneath the configured
root after symlink resolution, be a regular UTF-8 file no larger than 8 MiB and
validate as `DeterministicBaselineRequest`.

The Shell creates request/correlation IDs. Caller identity, grants, artifact
authorization, budget intersection, engineering eligibility and lifecycle
remain owned by trusted facade composition. No flag or session value grants
authority.

## Session, last result and refresh

Each `ShellRuntime` owns one isolated process-local `ShellSession`. Defaults are
frozen snapshots, history is a bounded tuple of allowlisted invocation IDs and
status, and two Shell instances share no mutable context. Session state is not
canonical evidence or audit state and is lost safely at process exit.

The session retains exactly one `SuccessfulInvocation` as `last`. It contains
the exact facade result object, its safe Shell correlation record and, when
refreshable, the typed invocation plan. Inspection never replaces or copies
that result. Failed commands preserve the previous successful value.

`refresh last` is an explicit new invocation. It reuses the already typed plan,
creates new request/run identities, records the prior Shell invocation as its
parent, and re-enters normal facade admission. It does not bypass the facade,
repair captures, or trigger A4.2 private enrichment.

## Rendering, explanation and trace

Human output is a concise allowlisted projection and never hides valid
non-action states. JSON capability output is a stable Shell envelope containing
the complete canonical facade result under `result`; reconstructing the typed
facade result from that value is lossless. `show last --json` therefore exposes
the exact stored result without an arbitrary object representation.

The reason, gap, contradiction and evidence views read only known structured
fields for the accepted result types. `explain last` assembles existing
structured facts; for A4 it preserves primary/counter theses, challenge and
arbitration findings, disposition, residual uncertainties, evidence needs,
invalidation conditions and evidence references. For A5 it preserves posture,
thesis health, recommendation, protection and monitoring intent, gaps,
contradictions, A4 linkage and invalidation refs. It performs no new reasoning.

`trace last` exposes only allowlisted Shell/facade identities, status/effect,
usage/cost knowledge, admitted logical refs, policy refs and timestamps. Its
flags narrow that projection. It never exposes config paths, credentials,
provider payloads, private instances, tracebacks or hidden reasoning.

## Errors, replay and lifecycle

Stable exit categories are:

- `0`: successful Shell/facade execution, including non-action domain states;
- `2`: syntax or missing/invalid context;
- `3`: permission denial;
- `4`: unsupported capability, no prior result or unavailable explanation;
- `5`: input-safety or replay-integrity failure;
- `6`: execution failure; and
- `130`: interrupted command.

Recorded replay and deterministic verification use only the accepted facade
capabilities and logical artifacts. Verification stays engineering-only and is
denied by facade policy when the bound caller lacks the grant. Original and
replay identities remain distinct. Current accepted capability usage reports
zero model and tool calls; the implementation adds no live call path.

Both entry modes coordinate one facade-owner startup/shutdown. The REPL handles
EOF and `exit`/`quit` cleanly; Ctrl-C cancels input or returns a safe interrupted
command result without corrupting the session.

## Deferred seams

Future NLP/mixed interaction may translate into the same closed `ShellCommand`
union and dispatcher only after a separately accepted Interaction-Agent,
privacy, model-budget and evaluation design. Rich citation numbering,
bibliographies, hyperlinks, Web UI, remote APIs, multi-user persistence,
batching, plugins and A6-A7 operations remain deferred. A Web consumer must call
the governed facade directly; it must not run the Shell or parse its output.

Acceptance evidence is recorded in
[STUDY_TI_SHELL_V0_1_ACCEPTANCE.md](STUDY_TI_SHELL_V0_1_ACCEPTANCE.md).
