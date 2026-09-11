# Study — POST_A3_PRE_A4 Local Facade Acceptance

**Date:** 2026-09-11 (Asia/Kolkata)

**Scope:** same-process trusted configuration, discovery/admission, bounded
captured artifact use, deterministic invocation lifecycle and offline replay.
No live provider, network, model, broker, or execution call was authorized.

The implementation base was `05109d7`, the accepted pre-A4 semantic foundation
commit. All changes in this pass are additive facade/tests/documentation work;
the base A2/A3/foundation contracts were not edited.

## Implemented boundary

The additive `tiaf.facade` package exposes six explicitly cataloged operations:
`baseline.assess`, `opportunity.assemble`, `a4_input.project`,
`replay.recorded`, `capabilities.list`, and engineering-only `replay.verify`.
It does not expose `opportunity.orchestrate`, `trace.inspect`, arbitrary
specialists/providers/routers/registries, or implementation callables.

The trusted owner receives typed operator configuration and caller grants,
validates/install artifacts during startup, freezes composition before work,
admits each request using an intersection of caller/operator/capability/profile/
authority/entitlement/model/budget constraints, creates request-local run state,
and projects operation-specific results/errors. Consumers use logical artifact
references and a caller-bound client only.

## Mandatory scenario evidence

The focused facade suite maps the required scenarios as follows:

| # | Acceptance scenario | Evidence |
| ---: | --- | --- |
| 1 | Catalog contains only safe implemented capabilities | exact static catalog assertion |
| 2 | Discovery is grant filtered | caller capability/interface filtering test |
| 3 | Discovery does not grant invocation | catalog-possession denial test |
| 4 | Unsupported capability rejected | `UNSUPPORTED` projection test |
| 5 | No caller self-grant of admin/live/model | extra-field validation matrix |
| 6 | Developer label alone is insufficient | engineering visibility denial test |
| 7 | `baseline.assess` A2 parity | direct-engine equality and policy identity test |
| 8 | `opportunity.assemble` A3.9 parity | direct structured-intelligence/fingerprint equality |
| 9 | `a4_input.project` foundation parity | direct projection equality |
| 10 | Recorded replay parity and zero live calls | A3/foundation replay matrix and zero usage |
| 11 | Arbitrary path rejected | absolute/relative path validation matrix |
| 12 | Arbitrary URL rejected | URL validation matrix |
| 13 | Provider/router/registry injection rejected | forbidden extra object and input scan |
| 14 | No credentials in serialization | request/artifact secret rejection and safe result test |
| 15 | Request grants/budget do not bleed | sequential request isolation and budget identity tests |
| 16 | Subject/horizon/objective/`as_of` isolation | concurrent horizons plus captured-identity matrix |
| 17 | Missing/revoked permission blocks artifact read | entitlement and revocation tests |
| 18 | Integrity failure triggers no live repair | corrupt startup artifact and network-blocked replay |
| 19 | Domain `NO_TRADE` stays valid | explicit neutral A2 parity assertion |
| 20 | Optional evidence absence remains a gap | custom optional foundation-gap projection test |
| 21 | Engineering capability denied normally | direct `replay.verify` invocation denial |
| 22 | Capability/schema identities stable | version/schema descriptor assertions |
| 23 | Startup composition cannot mutate during active run | blocked active-call freeze/shutdown test |
| 24 | Single-writer rule enforced/documented | literal-true frozen config test |
| 25 | No A4 Challenger/Arbitrator behavior | projection/result and AST boundary assertions |
| 26 | No model/provider addition | imports/classes/usage boundary assertions |
| 27 | No remote service/HTTP imports | AST dependency boundary assertion |
| 28 | No broker authority | public/class boundary assertion |

Additional checks cover request-schema mismatch, shutdown admission, failure
isolation, artifact-kind restrictions, frozen/JSON-safe contracts, safe error
projection, explicit caller/operator/request budget intersection, no captured
payload in the A3.9 result, and direct replay verification parity.

## Semantic and security results

- A2 assessment, A3.9 assembly, pre-A4 projection, A3 replay and verification
  stay delegated to their accepted implementations; facade parity is exact at
  semantic outputs/fingerprints.
- `NO_TRADE` remains a successful domain result. Optional source detail remains
  a typed gap. No facade status upgrades either into a recommendation.
- A3.9 facade output deliberately omits the raw `capture_json`; it returns only
  the safe structured intelligence and content identities.
- Artifact payloads remain owner-private. Logical refs, type/checksum validation,
  admission membership, authority, entitlement, and revocation are checked.
- Recorded replay succeeds with socket connection blocked. No live repair,
  provider, model, token, cost, or broker operation occurs.
- All invocation timestamps remain aware and canonicalize to `Asia/Kolkata`.
- Concurrent pure requests keep separate run IDs, evidence profiles and horizons.
  Failure of one call cannot mutate a completed frozen result.
- Startup composition remains immutable while an invocation is active. This is
  same-process behavior only; multi-process safety is not claimed.

## Deferred candidates and residual boundaries

`opportunity.orchestrate` remains deferred because its honest effect includes
controlled live acquisition and privileged A3.8 composition. No live capability
was needed for this milestone, so the required live serialization, budget and
failure gates have not been accepted. `trace.inspect` remains deferred because
there is no single mature redacted trace projection suitable for publication.

The artifact store is intentionally local/in-memory behind the owner. Durable
filesystem loading, multiple roots/writers, remote consumers, transport auth,
process isolation, persistent revocation, and operational cleanup remain future
hosting work. This facade grants no Shell or execution authority and does not
close any model, citation-rendering, remote-service, or A4-runtime deferral.
Because it is a same-process Python boundary, it is not a hostile-code sandbox;
the embedding application must keep the trusted owner/configuration away from
untrusted code.

## Validation results

All required gates passed:

- facade suite: `40 passed`;
- source-semantics suite: `27 passed`;
- opportunity-intelligence suite: `65 passed`;
- A3-hardening suite: `61 passed`;
- agents suite: `270 passed`;
- workflows suite: `42 passed`;
- full suite: `1988 passed`;
- `python -m compileall src scripts`: pass;
- `ruff check src tests scripts`: pass;
- `mypy src tests`: success across 470 source files;
- `python -m pip check`: no broken requirements (pip cache ownership warning only);
- documentation links: 447 local Markdown targets checked, none missing;
- scoped facade/document secret-assignment scan: no match;
- restricted dependency/import/A4/broker AST boundary: pass;
- recorded replay with socket connection blocked: pass;
- dependency manifest and `.env` diffs: empty;
- `git diff --check`: pass.

No live external call is part of this acceptance.

**Decision:** `READY_TO_ACCEPT_POST_A3_PRE_A4_LOCAL_FACADE`.
