# TIAF A5.2 Governed Position Facade and Bounded Shell

## Status

**Implemented; acceptance ready, 2026-09-12
(Asia/Kolkata).** This slice publishes the accepted
[A5.1 deterministic single-position baseline](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md)
through the existing local facade and command-first TI Shell. It does not change
A5.1 policy or position semantics.

## Capability contract

`position.assess` version `1.0` is a public, deterministic `CAPTURED_READ`
capability. It reports known-zero cost, supports deterministic replay, requires
the dedicated `ASSESS_POSITION` authority scope, and uses:

- request schema `schema:tiaf.facade.position-assess-request` version `1.0`;
- result schema `schema:tiaf.facade.position-assess-result` version `1.0`.

The descriptor is static metadata and contains no callable. Package version
`0.1.0`, capability version `1.0`, facade schema version `1.0`, and A5 policy
version `1.0` remain separate concepts.

The request contains one logical `position_request_ref`. The referenced trusted
artifact is a complete `PositionIntelligenceRequest`: immutable position
snapshot, linked A4 result, objective/horizon/as-of, policy identity, optional
predecessor and supplied signals. A single trusted artifact is used instead of
accepting caller-created broker state or separate independently mutable snapshot
and A4 inputs. The caller cannot supply an A5 policy object, filesystem path,
URL, account selector, provider/router/model/broker handle, credentials, or
execution instruction.

The effect is `CAPTURED_READ`, not `PURE`, because the facade resolves the
logical reference from its private trusted artifact owner after admission.

## Admission and artifact boundary

Every invocation intersects the caller grant and operator policy across:

- `position.assess` capability permission;
- `ASSESS_POSITION` scope;
- requested authority reference;
- position-specific entitlement;
- profile and zero-external-call budget; and
- facade lifecycle/revocation state.

The logical artifact is reread after admission. Read-time checks require its
authority and entitlement sets to be contained in the effective admission. The
embedded A5 request and position snapshot must also name the effective authority.
Possession of an artifact ID, a Shell default, or developer display access does
not grant position access. Revocation is rechecked before every read.

`A5_POSITION_REQUEST` startup artifacts must be exact-checksum JSON and validate
as a supported `PositionIntelligenceRequest` with intact A4 fingerprints and
accepted A5 policy. `A5_CAPTURE` artifacts receive the existing A5 capture,
snapshot, run and linked-A4 integrity checks. Missing, corrupt, tampered,
wrong-kind or unauthorized artifacts fail closed. Callers never receive the
artifact store, storage paths, raw artifact content or mutable storage objects;
there is therefore no caller path or symlink resolution surface in this
capability.

## Evaluation and result

After authorization, the facade checks outer subject, `POSITION` purpose,
horizon and `as_of` against the captured request without rewriting either. It
selects only the repository-supported policy by captured version and delegates
to `tiaf.a5.evaluate_position`, using the captured `as_of` as deterministic
evaluation time.

`PositionAssessResult` preserves the canonical A5 result, run fingerprint,
request checksum and ordinary facade metadata. The result includes position and
snapshot identity/time, effective freshness, linked A4 identity/fingerprint,
posture, thesis health, recommendation, protection intent, remaining-opportunity
state, monitoring needs/mandate, reasons, gaps, contradictions, invalidation
references, policy, replay identity and semantic fingerprint. It repeats the
canonical authority boundary:

```text
ADVISORY_ONLY_TRADEMONITOR_DECIDES_BROKER_EXECUTION
```

It also labels monitoring output:

```text
ADVISORY_MONITORING_INTENT_ONLY_NOT_SCHEDULED
```

`MAINTAIN`, `WATCH_CLOSELY`, `PROTECT`, `REDUCE_RISK`, `TRAIL_PROTECTION`,
`EXIT_RECOMMENDED`, `WAIT_FOR_CONFIRMATION`, `ABSTAIN` and
`INSUFFICIENT_EVIDENCE` are successful domain results. Stale snapshots remain
`ABSTAIN`; multi-leg remains the A5.1 `UNSUPPORTED_SHAPE` domain result. Neither
is flattened into an opaque facade failure.

Facade process failures retain the established safe categories:
`INVALID_REQUEST`, `PERMISSION_DENIED`, `UNAVAILABLE`,
`REPLAY_INTEGRITY_ERROR`, `UNSUPPORTED` and `FAILED`. Safe child exception codes
may be preserved, but private payloads are not.

## Replay decision

No `position.replay` capability was added. The existing `replay.recorded`
capability is the canonical recorded-replay boundary and now recognizes
authorized `A5_CAPTURE` artifacts as `A5_RECORDED`. It delegates to the A5.1
replay engine and performs no provider, broker, model, TM or network call. A5
deterministic verification and policy comparison remain direct engineering
functions from A5.1; this slice does not duplicate them in the facade.

## Shell command and session

The minimum command is:

```text
position assess --snapshot QUALIFIED_ID [scope options]
```

`--snapshot` is a logical trusted A5 request-artifact reference, not a file path
and not a live broker lookup. The linked A4 result is already inside that
validated captured request, avoiding an untrusted cross-artifact join. A typical
one-shot call is:

```bash
ti --config shell-bootstrap.json --output json \
  position assess \
  --snapshot artifact:accepted-position-request \
  --subject RELIANCE \
  --objective position \
  --horizon positional \
  --as-of 2026-09-12T12:00:00+05:30 \
  --profile-ref profile:deterministic \
  --authority-ref authority:authorized-position-owner
```

The REPL and one-shot paths share the same parser, typed `OperationCommand`,
dispatcher and facade invocation. Human output allowlists position/snapshot
identity, freshness, posture, health, recommendation, protection, monitoring
intent, reasons/gaps, A4 linkage, fingerprints and authority statement. Stable
JSON contains the typed facade result and round-trips through
`PositionAssessResult`.

Existing `explain last` and `trace last` are reused; no separate facade
explanation capability is needed. Explain projects only structured A5 fields.
Trace exposes logical refs, A4/A5 lineage, fingerprints, timing and known-zero
usage, not prices, quantities, broker source payloads, credentials or private
objects. No hidden chain-of-thought is created.

Session `last` and the typed refresh plan are convenience pointers only.
`refresh last` creates a new facade invocation, rechecks admission, rereads the
artifact and preserves the captured snapshot timestamp. It does not claim a
fresh broker snapshot. Two Shell runtimes do not share session state.

Domain `EXIT_RECOMMENDED` and `ABSTAIN` exit with code `0`. Permission and process
failures remain nonzero. Commands such as `position exit`, `modify`, `stop`,
`trail`, `roll`, `hedge` and `squareoff` are outside the grammar.

## Python consumer

Trusted local programs use the existing facade client, not a second SDK:

```python
request = PositionAssessRequest(
    scope=authorized_scope,
    position_request_ref="artifact:accepted-position-request",
)
result = owner.client("caller:trusted-script").invoke(request)
```

The embedding application constructs `owner` and grants. Ordinary callers see
only a caller-bound `LocalFacadeClient`; the example does not authorize itself.
The request/result contracts contain serializable typed values and logical refs,
so a future transport can wrap them without changing A5 semantics. No HTTP,
gRPC, FastAPI, Flask, WebSocket or remote service is added here.

## Preserved boundaries

- No broker, provider, MCP, model or LLM call/import exists in the position path.
- No account-wide lookup, hidden snapshot repair or operational-state inference.
- No A2/A3/A4 recalculation or mutation; linked A4 is validated and preserved.
- No stop/order instruction; analytical levels remain `executable=false`.
- Monitoring needs are displayed but never scheduled or claimed active.
- `EXPRESSION_REFRESH_REQUIRED` renders as “expression refresh required; no
  replacement selected”; A6 is not called.
- No A7 forecast/probability and no invented target.
- TradeMonitor remains the action-time governor and broker-execution authority.
- Multi-leg interpretation, TM transport, durable monitoring, remote APIs and
  production storage remain separately gated.

Acceptance evidence is recorded in
[STUDY_A5_2_GOVERNED_POSITION_FACADE_SHELL_ACCEPTANCE.md](STUDY_A5_2_GOVERNED_POSITION_FACADE_SHELL_ACCEPTANCE.md).

The exact next prompt title is:

**`TIAF_A5 — MAJOR MILESTONE CLOSURE REVIEW`**
