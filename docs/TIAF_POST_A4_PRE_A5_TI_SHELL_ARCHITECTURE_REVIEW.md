# POST_A4_PRE_A5 TI_SHELL Architecture Review

## Decision and scope

**Decision: `READY_TO_IMPLEMENT_TI_SHELL_V0_1`.**

The accepted A4 baseline (`tiaf-a4-baseline`, commit `494d968`) provides the
prerequisites for a small local engineering Shell: a caller-bound same-process
facade, seven explicitly described capabilities, logical artifact references,
safe errors, replay, immutable results and A4 provenance. The next implementation
may therefore build a command-first mediator. It may not add a capability,
publish A4.2 live enrichment, call private services, or infer authority from a
Shell mode.

This review approves architecture only. It adds no parser, REPL, command,
renderer, provider access, model access, service, persistence or A5 behavior.
The authoritative design is
[TIAF_TI_SHELL_ARCHITECTURE.md](TIAF_TI_SHELL_ARCHITECTURE.md).

## Repository evidence

The review used the accepted facade catalog and typed request/result contracts,
not prospective package APIs. The current catalog is:

| Capability | Interface | Effect | Replay | Model | Request -> result |
|---|---|---|---|---|---|
| `capabilities.list` | public | `PURE` | none | no | `CapabilityListRequest` -> `CapabilityListResult` |
| `baseline.assess` | public | `PURE` | deterministic | no | `BaselineAssessRequest` -> `BaselineAssessResult` |
| `opportunity.assemble` | public | `CAPTURED_READ` | deterministic | no | `OpportunityAssembleRequest` -> `OpportunityAssembleResult` |
| `a4_input.project` | public | `CAPTURED_READ` | deterministic | no | `A4InputProjectRequest` -> `A4InputProjectResult` |
| `a4.evaluate` | public | `CAPTURED_READ` | deterministic | no | `A4EvaluateRequest` -> `A4EvaluateResult` |
| `replay.recorded` | public | `CAPTURED_READ` | recorded | no | `RecordedReplayRequest` -> `RecordedReplayResult` |
| `replay.verify` | engineering | `CAPTURED_READ` | deterministic | no | `ReplayVerifyRequest` -> `ReplayVerifyResult` |

All currently published work is zero-model and has no `LIVE_READ` or `PERSIST`
effect. `opportunity.orchestrate`, A4.2 acquisition, direct specialist calls,
`trace.inspect`, A5-A7 operations and broker operations are not facade
capabilities. Python importability does not make them Shell commands.

The facade also establishes the controlling security facts:

- `LocalFacadeClient` is caller-bound and exposes only discovery/invocation;
- effective permission is recomputed from caller grant, operator policy,
  authority, entitlement, profile, interface and budget;
- captured inputs use authorized qualified logical references;
- requests cannot carry paths, URLs, credentials, policy objects or providers;
- safe `FacadeErrorRecord` values cross the boundary; and
- domain states such as `NO_TRADE`, `WAIT`, `ABSTAIN` and `CONFLICTED` are not
  process failures.

## Approved thesis

TI_SHELL v0.1 is a **local, command-first, stateful interaction adapter over a
caller-bound facade client**. It translates a closed command grammar into
existing typed facade requests, preserves exact typed results, and offers small,
allowlisted human/JSON projections. It owns interaction state and presentation;
it owns no intelligence, evidence, admission, orchestration, provider, model,
position, strategy, ranking or execution semantics.

This is useful now because the accepted facade is otherwise accessible only by
Python callers and milestone scripts. A reproducible command interface improves
manual acceptance and replay inspection before A5 without becoming an A5
dependency.

## Resolved architecture choices

| Question | Resolution |
|---|---|
| Interaction style | Native commands only in v0.1. NLP and mixed modes wait. |
| Process | Same trusted Python process as the facade/Core composition owner. |
| Parser | Standard-library `argparse` over an explicit command catalog; `shlex.split` only for REPL text. |
| REPL | A small loop is sufficient; no REPL framework. |
| One-shot parity | One-shot `argv` and REPL tokens enter the same parser and dispatcher. |
| Session | Transient, process-local defaults plus one exact last result and a bounded redacted invocation ledger. |
| Invocation | Always a fresh typed request through `LocalFacadeClient`; no private import/registry dispatch. |
| Artifact inputs | Existing facade logical refs. No caller filesystem paths for captured operations. |
| Baseline input | Bounded JSON below a trusted startup request root, because the facade's pure baseline request embeds typed evidence rather than an artifact ref. |
| Rendering | Typed allowlists; exact canonical result nested in a versioned JSON envelope. Never `repr`, reflection or raw provider payloads. |
| Explain | Deterministic projection from the exact last structured result. No new reasoning. |
| Trace | Facade invocation metadata only. It is not a new `trace.inspect` capability. |
| Engineering | Visibility and invocation follow filtered facade discovery/admission. A flag or prompt cannot grant it. |
| Refresh | Explicitly reruns the immutable prior command with new request/run identity; it never implies live acquisition. |
| Persistence | None for Shell state/history in v0.1. Existing facade/corpus ownership is unchanged. |
| Future milestones | A5/A6/A7 command nouns remain reserved and unavailable until typed facade capabilities are accepted. |

## Complexity audit

1. **Is Shell needed now?** Yes, narrowly. It provides one repeatable human and
   scripting adapter over the already accepted facade and improves pre-A5
   engineering inspection. It is not needed to make A5 correct.
2. **Smallest useful command set?** Help/context, permitted-capability discovery,
   adapters for the six invocable facade operations, exact last-result viewing,
   explain, trace, explicit refresh and REPL exit. Removing any family would
   leave either no governed execution or no useful interactive mediation.
3. **Should NLP wait?** Yes. No Interaction Agent contract, intent grammar,
   ambiguity protocol or production model admission has been accepted.
4. **Parser choice?** `argparse` plus an explicit registry. Click/Typer would add
   dependency and annotation-driven magic without solving a present need.
5. **REPL framework?** No. The v0.1 loop needs prompt/read/tokenize/dispatch/exit,
   not completion, terminal control or asynchronous jobs.
6. **Shared dispatcher?** Yes. This prevents semantic drift between one-shot and
   interactive use.
7. **What stays out?** NLP, models, live acquisition, refresh-to-current,
   specialist/private operations, arbitrary Python/shell execution, Web/HTTP,
   jobs, durable history, multi-symbol ranking, A5-A7, broker operations and rich
   citation/bibliography work.
8. **Could it become a second service layer?** Yes, if it owns admission,
   composition, artifact loading, retries or business policy. The approved
   dependency rule and closed adapters forbid those moves.
9. **Does it improve engineering before A5?** Yes: capability discovery,
   repeatable captured invocation, exact JSON, replay verification and bounded
   explanation become available through one coherent interface.

## Shell thesis section dispositions

The classifications below apply to the numbered sections of
[`TBD_TI_SHELL_THESIS.md`](TBD_TI_SHELL_THESIS.md). “Promote” means the revised
principle is incorporated into the authoritative architecture, not that runtime
code exists.

| § | Topic | Disposition | Reason |
|---:|---|---|---|
| 1 | Thesis | REVISE | Promote the mediator thesis, limited to command-first local v0.1. |
| 2 | Ownership | SPLIT | Promote command/session/render ownership; keep NLP/Agent/model ownership TBD. |
| 3 | Interaction model | REVISE | Approve only command -> typed facade -> result -> renderer. |
| 4 | Native command mode | REVISE | Replace private/example operations with the closed facade-backed taxonomy. |
| 5 | NLP mode | KEEP_TBD | Needs a separate Interaction-Agent/ambiguity/model architecture. |
| 6 | Mixed mode | KEEP_TBD | Depends on the NLP decision. |
| 7 | Mode/profile/model separation | PROMOTE | Separation is binding; v0.1 implements command mode only. |
| 8 | Explicit Agent command | KEEP_TBD | No accepted Interaction Agent exists. |
| 9 | Stateful context | REVISE | Promote only transient typed defaults, last result and bounded redacted ledger. |
| 10 | Suggested controls | REVISE | Promote context/help/output controls; reject model/provider/unsafe controls. |
| 11 | Capability commands | REVISE | Only descriptors in the caller-visible facade catalog may be adapted. |
| 12 | Inspection commands | REVISE | Promote typed `show last`, `explain last`, and metadata-only `trace last`. |
| 13 | Explain | PROMOTE | It must render structured reasons/gaps/dissent without new analysis. |
| 14 | Trace | REVISE | Limit v0.1 to safe facade metadata; unified Core trace remains unimplemented. |
| 15 | Follow-up questions | KEEP_TBD | Natural-language follow-up needs an Interaction Agent. |
| 16 | Refresh | REVISE | Promote explicit captured rerun, not live freshness or hidden reuse. |
| 17 | Dry-run | KEEP_TBD | No accepted facade admission-preview capability exists. |
| 18 | Show-plan | KEEP_TBD | Planner internals are private and no public plan capability exists. |
| 19 | Multi-symbol use | REJECT | v0.1 is single-invocation; A3 ranking is DEF-053 and A7-owned. |
| 20 | Capability discovery | PROMOTE | Use permission-filtered `capabilities.list`, never reflection. |
| 21 | Agent discovery | KEEP_TBD | Agent registries are not public facade catalogs. |
| 22 | Invocation provenance | PROMOTE | Record Shell invocation identity separately from canonical evidence provenance. |
| 23 | No internal shell-out | PROMOTE | Direct typed Python invocation is mandatory. |
| 24 | Typed composition | KEEP_TBD | Pipes/composition need compatibility, authority and failure semantics. |
| 25 | Public/developer Shell | REVISE | Promote filtered visibility; reject a developer-mode authority shortcut. |
| 26 | Errors | PROMOTE | Preserve facade/domain distinctions and define stable process exits. |
| 27 | Authority | PROMOTE | The facade remains the authority/admission owner. |
| 28 | Testing role | PROMOTE | Shell becomes an adapter acceptance surface, never the only test route. |
| 29 | Model-evaluation role | KEEP_TBD | Production model integration remains DEF-052/DEF-055. |
| 30 | Recommended v0.1 | SUPERSEDE | The old broad list is replaced by the bounded command set in the architecture. |
| 31 | Never becomes | PROMOTE | Its prohibitions remain binding and gain explicit provider/broker boundaries. |
| 32 | Invariants | REVISE | Preserve them with command-only, logical-ref and exact-result rules. |
| 33 | Final thesis | REVISE | Command-first now; Agent/NLP remains an optional later adapter. |

The thesis therefore remains a historical idea record with
`PARTIALLY_SUPERSEDED_BY_AUTHORITATIVE_ARCHITECTURE` status. Its unpromoted NLP,
model, composition and product ideas remain visibly TBD.

## CLI/Web overlap disposition

The local CLI half of
[`TBD_TI_CLI_WEB_UI_INTERACTION_ARCHITECTURE.md`](TBD_TI_CLI_WEB_UI_INTERACTION_ARCHITECTURE.md)
is split from Web/product speculation:

- **PROMOTE:** headless Core, semantic typed operations, direct shared facade,
  structured human/JSON output, common domain/error meaning, independent
  consumers, authorization and “Web must not run Shell”.
- **REVISE:** “CLI is exhaustive” means broadest *permitted curated facade*
  coverage, never private internals. Exact syntax is now governed by the Shell
  architecture. Equivalent-CLI display is future presentation, not execution.
- **KEEP_TBD:** Web workflows/stack, browser security, remote transport,
  visualization, async jobs, streaming, multi-user sessions and preference
  persistence.
- **REJECT for v0.1:** GUI parity, Web -> subprocess -> stdout parsing, a Shell
  HTTP layer, and placeholder commands for unavailable roadmap capabilities.

The CLI/Web note remains non-authoritative for Web and remote-product design.
This review does not implement or schedule Web before a concrete consumer/A8
need.

## Deferral reconciliation

No new deferral ID is needed and no register status changes.

- DEF-003 remains `PLANNED` for remote service/API and A8 consumer delivery; a
  local Shell does not close it.
- DEF-052 and DEF-055 remain deferred; command mode has no model path.
- DEF-053 remains deferred; the Shell does not rank A3 candidates.
- DEF-054 remains `PLANNED`, split within the stable ID. The v0.1 renderer is
  the bounded implementation candidate. Rich bibliography, hyperlink, report
  and Web presentation remains deferred. Architecture alone does not mark any
  part implemented.

## Implementation gate

The implementation may begin only as the separately reviewed prompt:

**`POST_A4_PRE_A5 — TI_SHELL v0.1 Command-First Local Engineering Interface Implementation`**

It must preserve the accepted facade/domain contracts and pass the 24-scenario
acceptance matrix in the authoritative architecture. This review does not
authorize commit, tag or push.
