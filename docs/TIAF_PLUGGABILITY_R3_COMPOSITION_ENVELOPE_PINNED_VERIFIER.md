# TIAF Pluggability R3 — Composition Envelope / Pinned Verifier

## Status and boundary

Implemented and subsequently **ACCEPTED / DONE** on 2026-09-13 (Asia/Kolkata).
The independent
[acceptance review](TIAF_PLUGGABILITY_R3_COMPOSITION_ENVELOPE_PINNED_VERIFIER_ACCEPTANCE.md)
returned `READY_TO_CLOSE_PLUGGABILITY_R3`.
R1 and R2 remain accepted; A5 remains frozen at `tiaf-a5-baseline`. R4 optional
adapter import isolation, R5 trusted COLD composition ownership, and A6 remain
unimplemented. This pass adds no provider, model, broker, plugin-loader, HOT
replacement, recurring-monitor, or remote-API behavior.

R3 addresses one precise distinction:

```text
R2 CapabilityDiscoveryDescriptor  → what a capability is
R3 CompositionEnvelope            → what happened in this exact run
```

The envelope is attached to new materially composed A3.8 orchestration records.
It does not alter A2 evidence, specialist opinions, A3.9 synthesis, A4 decisions,
or A5 position-domain results.

## Versioned immutable schema

`tiaf.workflows.composition-envelope` version `1.0` contains:

| Field | Meaning |
|---|---|
| `run_id` | Identity of the captured orchestration run |
| `policy_id`, `policy_version`, `planner_version` | Exact composition-governing policy and planner identity |
| `requested_scope` | Stable sorted union of required and optional capability IDs |
| `required_scope`, `optional_scope` | R1 policy-owned scopes, pinned independently of the resolver supplied later |
| `participants` | One immutable entry for every requested capability, including explicit non-participation |
| `parent_composition_fingerprint`, `baseline_composition_fingerprint` | Optional lineage for an intentional successor/comparison; absent for ordinary runs |
| `composition_fingerprint` | Deterministic identity of policy, scope, versions, and participation |

Each participant records only run facts needed beyond the R2 static descriptor:
capability ID, exact interface version when resolved, semantic role,
requiredness, dependency-specification fingerprint, invocation flag, sorted
input references, output reference and semantic fingerprint, status, explicit
failure/non-participation reason, and honest usage knowledge plus the existing
`AgentUsage` record where known. Contracts are frozen; tuples serialize as JSON
arrays.

Separate `absent`, `failed`, and `skipped` collections were deliberately not
added. Those facts are mutually and completely represented by the participant
status and reason without duplicating state.

## Participation taxonomy

The closed run-level taxonomy is:

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

These are execution/participation states, never market direction or evidence.
A failure or absence cannot become a bearish or bullish opinion. Successful and
abstaining executions require a captured output identity. Every other state
requires an explicit reason. A non-invoked participant cannot claim inputs,
outputs, or usage.

## Required and optional pinning

The envelope is projected from the admitted request and final Planner 1.1 plan,
not from a future registry query. Participants exactly cover the requested
scope. Required and optional scopes must be sorted, unique, disjoint, and their
union must equal requested scope.

`required_complete` counts only required participants and is true only when
each required participant succeeded or explicitly abstained. A missing required
implementation therefore remains visible and cannot improve completeness.
Optional absence is retained as a participant fact but never enters the required
denominator.

## Composition fingerprint

The composition fingerprint is separate from the domain semantic fingerprint,
orchestration run fingerprint, and capture checksum. It covers the envelope's
schema and governing policy identities, pinned scopes, participant set,
requiredness, exact capability/dependency versions, invocation/status/reason,
input/output identity, usage-knowledge state, and optional lineage.

It is calculated from canonical semantic JSON. Object-key/formatting order and
runtime usage measurements do not change composition identity. Known versus
unknown versus not-applicable usage does change the honesty claim; detailed
usage remains preserved in the run envelope but is excluded from this
composition-only fingerprint. Participant set, order-normalized identity,
requiredness, version, policy, output identity, or lineage changes create a new
fingerprint.

## Replay, pinned verification, and comparison

These paths remain deliberately separate:

```text
recorded replay
  captured JSON + checksum → validated historical record
  registry-free; no execution

deterministic verification
  validated historical record + compatible local resolver
  → resolve only captured capability IDs
  → require exact recorded versions/dependency declarations
  → re-execute deterministic specialists over captured evidence

policy/composition comparison
  original immutable record + intentionally different policy/composition
  → new result and new lineage/composition identity
```

A later-expanded resolver is reduced to the exact capability specifications
captured in the historical first plan. Later capabilities and enrichers cannot
enter replay or verification. R3 uses exact specialist/interface version and
full dependency-declaration equality; it implements no broad semantic-version
substitution. Missing or incompatible required bindings fail closed.

Recorded replay never calls a registry, provider, model, broker, or network.
Deterministic verification resolves local implementations only and reuses the
existing zero-live-call specialist path. It does not repair captures or execute
side effects.

## Fail-closed verification

`PinnedVerificationError` exposes one of these stable failure codes:

```text
CORRUPTED_ENVELOPE
MISSING_PINNED_CAPABILITY
INCOMPATIBLE_CAPABILITY_VERSION
PINNED_DEPENDENCY_MISMATCH
POLICY_MISMATCH
REQUIRED_PARTICIPANT_UNRESOLVED
MISSING_ARTIFACT
OUTPUT_FINGERPRINT_MISMATCH
UNAUTHORIZED
DETERMINISTIC_OUTPUT_MISMATCH
```

No code auto-repairs, silently substitutes, weakens requiredness, or relabels a
failure as market evidence. The existing engineering-only `replay.verify`
authority remains unchanged. Capability/envelope presence grants no invoke
permission and the envelope contains no credentials, caller grants, provider
tokens, broker handles, module paths, or callables.

## Usage and cost

R3 reuses `AgentUsage`; it introduces no billing layer. A captured specialist
record yields `KNOWN` usage, including legitimate deterministic zeroes. An
invoked operation without a settled record is `UNKNOWN`, not fabricated zero.
Non-invocation is `NOT_APPLICABLE`. Detailed usage remains auditable even though
volatile measurements are not part of composition identity.

## Integration and exposure

- New A3.8 `OrchestrationRunRecord` captures use schema `1.1` and require one
  validated envelope.
- A3.9 handoff accepts orchestration schemas `1.0` and `1.1`; all existing
  identity, evidence, citation, and projection checks remain enforced.
- Opportunity assembly consequently retains the envelope in its admitted A3.8
  capture without duplicating it into the A3.9 domain result.
- A3.10 package replay stays registry-free. Deterministic package verification
  uses the pinned verifier and reports `PINNED_COMPOSITION:<failure-code>` when
  unavailable.
- Existing facade/Shell `replay.verify` therefore exposes governed verification
  disposition and reason through its structured result. No new Shell command or
  default output noise was added.
- A4 and A5 remain consumers of already governed upstream identities. They were
  inspected but receive no new domain fields or policy changes.

This is sufficient for future Scanner/TM/monitoring consumers to pin the
captured orchestration basis while leaving those consumers unimplemented.

## Legacy compatibility

Existing orchestration schema `1.0` records carry no composition envelope and
retain their original semantic fingerprint. They remain readable and recorded-
replayable without rewriting. Their deterministic verification follows the
documented legacy path: dependency resolution uses the explicitly supplied
compatible registry under the captured policy, preserving pre-R3 behavior.
New Planner 1.1 captures use schema `1.1`; legacy Planner 1.0 test captures stay
schema `1.0`.

## Acceptance boundary

R3 is accepted after a short closure pass confirmed schema examples, legacy
replay, typed failure projection, frozen-domain parity, and full regression
without redesigning R3.

```text
A5 FROZEN
R1 ACCEPTED
R2 ACCEPTED
R3 ACCEPTED / DONE
R4 ACTIVE / NEXT
R5 PENDING BEFORE_A6
A6 NOT_IMPLEMENTED
```
