# TIAF Pluggability R3 — Composition Envelope / Pinned Verifier Acceptance

## Decision

**READY_TO_CLOSE_PLUGGABILITY_R3**

Independent bounded acceptance completed on 2026-09-13 (Asia/Kolkata). R3 is
correct, replay-safe, backward-compatible, and sufficiently bounded. No runtime
defect was found and no implementation change was required during this closure
pass. No live provider, model, broker, network, commit, tag, or push operation was
performed.

## Scope reviewed

The review inspected the immutable composition contracts, orchestration capture,
recorded replay, deterministic verifier, A3.10 verification projection, A3.9
handoff, facade/Shell catalog and authority boundaries, R1/R2 regressions, and
frozen A4/A5 source boundaries.

R3 preserves the intended separation:

```text
R2 descriptor       → what a capability is
R3 envelope         → what participated in this exact run
recorded replay     → reconstruct captured history without a registry
pinned verification → re-execute deterministic captured work with exact bindings
comparison          → create a new identity; never rewrite history
```

## Acceptance findings

### Envelope schema

`tiaf.workflows.composition-envelope` schema `1.0` is immutable, strict, and
deterministically fingerprinted. New materially composed A3.8 records use
`OrchestrationRunRecord` schema `1.1` and require exactly one aligned envelope.
Legacy schema `1.0` excludes the additive field from its original semantic
payload. Participant and scope collections are tuples and serialize as ordinary
JSON arrays.

The envelope records only run facts needed beyond R2: capability/version and
semantic role references, dependency identity, requiredness, invocation,
inputs, output identity, terminal participation state/reason, and usage
knowledge. It contains no callable, module path, credential, token, caller grant,
broker handle, or unrestricted authority.

### Scope and participation

Required and optional scopes are sorted, unique, disjoint, and together exactly
equal requested scope. Participants exactly cover that declared scope. The
builder projects from the final admitted Planner 1.1 plan and captured attempts,
not a later registry.

A missing required implementation remains `NOT_REGISTERED` and makes
`required_complete` false. Optional absence remains explicit but does not enter
required completeness. Later registry expansion cannot change the recorded scope
or introduce a new capability into deterministic verification.

The accepted status taxonomy is:

```text
SUCCEEDED
FAILED
ABSTAINED
SUPERSEDED
NOT_REGISTERED
UNAUTHORIZED
DEPENDENCY_UNAVAILABLE
SKIPPED_BY_POLICY
NOT_SELECTED
UNSUPPORTED
```

These are mutually exclusive run-participation states. They are not availability
summaries or market dispositions, and no failure/absence becomes positive or
negative evidence.

### Composition fingerprint

The composition fingerprint changes for participant-set, requiredness,
capability/interface version, policy/planner version, dependency identity,
material status, output identity, or lineage changes. It is stable under JSON
key/formatting order and volatile detailed usage measurements. Known/unknown/
not-applicable usage knowledge remains semantic, while elapsed/cost measurement
values remain auditable outside the composition-only identity.

The composition fingerprint remains distinct from specialist/domain semantic
fingerprints, the orchestration run fingerprint, and the exact capture checksum.
Optional parent/baseline references support a successor or enrichment identity
without rewriting the baseline.

### Pinned verification and replay

Recorded replay validates captured checksums, artifacts, references, and the
envelope without consulting any registry or executing work.

Deterministic verification resolves only capability specifications present in
the captured plan, constructs a reduced pinned registry, requires exact
specialist/interface versions and full dependency-declaration equality, and
re-executes deterministic specialists only over captured inputs. Extra
capabilities in a later resolver are ignored. No nearest-version or broad semver
fallback exists.

Missing/incompatible pinned implementations, changed dependency declarations,
policy mismatch, corruption, missing artifacts, output mismatch, or changed
deterministic output fail closed through typed `PinnedVerificationError` codes.
No automatic repair, scope weakening, optional enrichment, or live backfill is
performed.

Policy/composition comparison remains a distinct successor result with its own
identity and optional parent/baseline lineage. Original captures are immutable.

### Legacy, usage, and authority

Schema `1.0` records remain readable and replayable without modification. Their
deterministic verification retains the documented legacy compatible-registry
path. Schema `1.1` enforces the new envelope and exact pinned path.

Participant usage correctly distinguishes `KNOWN`, `UNKNOWN`, and
`NOT_APPLICABLE`. Captured deterministic zeroes remain zero; unresolved usage is
never fabricated as zero.

The existing engineering permission gate for `replay.verify` remains in force.
A3.10 projects typed failures as `PINNED_COMPOSITION:<code>` without leaking
details or granting invocation authority. The public/engineering facade catalog
remains exactly eight operations and no Shell command family was added.

### A3.9 and frozen domains

A3.9 accepts only orchestration schema `1.0` or `1.1` and retains all existing
subject, evidence, citation, projection, artifact, policy, and fingerprint
checks. It performs no silent recomputation and preserves required-absence
meaning inside the admitted A3.8 capture.

`src/tiaf/a4` and `src/tiaf/a5` have no differences from the frozen
`tiaf-a5-baseline` tag. A5 recommendation, posture, thesis, semantic/run
fingerprints, replay identity, capture checksum, and dependency surface are
unchanged. The R3 regression additionally proves identical A5 request, result,
run, and capture identities before and after an R3 orchestration run.

## Validation evidence

| Check | Result |
|---|---:|
| Dedicated R3 tests | 12 passed |
| Workflows | 62 passed |
| Facade | 71 passed |
| A4 | 37 passed |
| A5 | 52 passed |
| Full suite | 2,261 passed |
| R1 required-scope regression | 8 passed |
| R2 descriptor/catalog parity | 14 passed |
| Replay-isolation selection | 6 passed |
| `python -m compileall src scripts` | passed |
| `ruff check src tests scripts` | passed |
| `mypy src tests` | 533 source files; no issues |
| `python -m pip check` | no broken requirements |
| `git diff --check` | passed |
| Documentation links | 119 Markdown files; 944 links; zero missing |
| Deferral integrity | 58 stable IDs; all statuses parsed |
| Capability parity | 8 entries; exact deterministic order |
| Forbidden-import audit | 39 files; zero violations |
| Secret scan | zero credential-like assignments |
| Frozen A4/A5 parity | no source differences |

`pip check` emitted only the environment's non-writable pip-cache warning; the
dependency result was clean.

## Closure and remaining boundary

**R4_R5_UNTOUCHED**

R3 did not implement optional adapter import isolation, broad COLD configuration
ownership, HOT loading, Scanner/TM/monitoring runtime, Sector Rotation, Signal
Qualification, remote APIs, or A6. Same-process verifier implementations remain
trusted local code; R3 is not a sandbox. Legacy schema `1.0` cannot retrospectively
gain a complete R3 envelope and therefore retains its documented legacy
verification limitation.

Project status after this acceptance:

```text
A5 FROZEN
R1 ACCEPTED
R2 ACCEPTED
R3 ACCEPTED / DONE
R4 ACTIVE / NEXT
R5 PENDING BEFORE_A6
A6 NOT_IMPLEMENTED
```

Exact next prompt title:

**TIAF PLUGGABILITY — R4 OPTIONAL ADAPTER IMPORT ISOLATION**
