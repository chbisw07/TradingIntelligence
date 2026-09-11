# TIAF_A4.2 — Governed Evidence-Need / Planner Bridge

## Status and boundary

TIAF_A4.2 implements one bounded open-world enrichment cycle as an internal
application service. A4 emits a provider-neutral semantic question; deterministic
admission intersects it with operator grants; the existing A3.8 Planner/workflow
owns execution; a workflow-side projector supplies already-normalized source
semantics; and A4 may evaluate one later successor projection.

```text
A4RunRecord -> A4EvidenceNeed -> deterministic admission
            -> A4.2 bridge -> A3.8 OrchestrationRequest
            -> existing controlled services / MI / confirmation routing
            -> typed SuccessorEvidenceCapture
            -> later A4SemanticInputProjection -> successor A4RunRecord
```

The package is `tiaf.a4_enrichment`, not `tiaf.a4`. This placement keeps A4
domain contracts independent from Planner, workflow, providers and LangGraph.
It adds no model, general web-research tool, broker authority, trade expression,
position action, A5, A6 or A7 behavior.

## Final evidence-need contract

`A4EvidenceNeed` is now an immutable `OPEN` contract, not an execution
placeholder. It records:

- its ID and stable parent A4 run/projection identities and fingerprint;
- subject, objective, horizon and original evidence cutoff;
- semantic question and closed requested capability;
- optional claim, predicate and field scope;
- originating challenges/disputes, materiality and reason codes;
- the expected resolvable question and minimum PIT/authority/independence/source-
  role characteristics;
- required/partial policy, dedupe key, permitted authority refs, budget/deadline
  refs, policy/schema versions and creation time.

The six closed semantic capabilities are authoritative confirmation, company
fundamentals, event/news context, sector/macro context, derivatives context and
bounded no-model deep research. A need contains no provider preference, URL,
endpoint, browser/tool/model instruction, broker field or trade instruction.
Collections are tuples in Python and arrays in JSON. Timestamps remain aware,
normalize to `ZoneInfo("Asia/Kolkata")`, and serialize with `+05:30`.

`A4RunRecord.run_id` is deterministically known before findings are built from
the projection fingerprint and exact A4 policy. Evidence needs can therefore
cite their real parent without a result-fingerprint cycle. Run validation checks
that identity and every need relationship.

## Deterministic admission

`admit_evidence_need` first validates the complete parent A4 run and exact need
ownership. It then returns one typed outcome:

| Outcome | Meaning |
| --- | --- |
| `ADMITTED` | A material unresolved question fits all policy, authority, entitlement, profile, budget and time bounds. |
| `DENIED_AUTHORITY` | Permitted authority or minimum source-role scope is absent. |
| `DENIED_BUDGET` | Parent budget reference is denied or no bounded child allowance remains. |
| `DENIED_POLICY` | Entitlement/profile is absent or a decisive `NO_TRADE`/`AVOID` makes the request irrelevant. |
| `DUPLICATE` | The dedupe key was already processed. |
| `UNSUPPORTED_CAPABILITY` | The semantic capability is outside the versioned bridge policy. |
| `NOT_MATERIAL` | The owned need is optional/non-material. |
| `DEADLINE_EXCEEDED` | The granted deadline has passed. |
| `ALREADY_RESOLVED` | The need or all originating findings are already resolved. |

Admission is a permission decision, never a market opinion. The admitted budget
is the supplied *remaining* parent allowance; it is not reset. Unknown or held
leaf usage remains in the A3.8 record and is never silently refunded.

## Planner mapping and execution

The versioned bridge maps only semantic capabilities to existing coarse A3.8
capabilities and evidence types. It preserves need ID, parent correlation,
subject, purpose, horizon, frozen A2 identity/fingerprint, authority-derived
admission, remaining budget, deadline and later `as_of`. It forces `no_llm`,
model tier `NONE`, at most one enrichment/replan/attempt and at most one provider
call. The bridge never constructs a provider, router, connector or service
handle; trusted application composition supplies the existing `AgentRegistry`
and `ControlledServices`.

The serial coordinator is the reference runner. The optional LangGraph runner is
lazy-imported only in `a4_enrichment.bridge`; domain contracts, source semantics,
facade contracts and recorded replay do not import it. LangChain is not a
dependency.

## Evidence capture and successor semantics

Workflow output is not guessed into canonical facts. A
`SuccessorEvidenceCapture` must be produced at the normalization/application
boundary and include the workflow fingerprint, new/reused evidence IDs, explicit
workflow-to-semantic crosswalk, acquisition time, independence/relevance,
mapping/change class, affected challenges, resolved gaps, failures and exact
usage. Every new semantic evidence ID requires a captured workflow artifact or
evidence-reference crosswalk.

`NO_NEW_INFORMATION` covers equivalent wrappers, duplicate source facts,
unchanged unavailable/not-found results, unresolved ambiguity and evidence that
does not touch the challenged proposition. It creates no successor and preserves
the conservative parent disposition after the single round.

Safe context, source-authority, confirmation and factual-conflict changes can
form a successor only through the accepted `ProjectionBuildInput`,
`validate_successor`, and `build_projection` path. The successor must:

- use a later cutoff, link the exact parent projection and identify new evidence;
- retain the identical frozen A2/A3 parent package and artifact hashes;
- preserve old evidence, disputes, dissent and usage/cost knowledge supplied in
  the successor input;
- never backdate evidence or mutate the parent; and
- receive a new semantic fingerprint and A4 run identity.

Price/OHLCV or effective market-state changes, specialist-input invalidation,
and A2 eligibility/class/direction changes stop with
`UPSTREAM_REFRESH_REQUIRED`. A4.2 never recomputes or patches A2/A3.

The successor is deterministically evaluated under the same A4 policy.
`FindingLineage` marks affected findings `RECOMPUTED`, semantically unchanged
findings `PRESERVED`, removed findings `RESOLVED`, and newly introduced findings
`NEW`; arbitration considers the complete successor set. The parent result and
all prior dissent remain captured unchanged.

## Failure, accounting and replay

Admission denial performs zero acquisition. Workflow exceptions, timeout/budget
stops, malformed/crosswalk-invalid evidence, partial evidence, successor failure,
upstream-refresh requirement and re-evaluation failure remain typed conservative
stops. No failure can improve a disposition. The outcome records rounds/cycles,
provider calls, exact A3.8 usage, failures, original/final dispositions and its
content fingerprint. All bounds are hard `0..1`.

`A4EnrichmentCapture` stores the complete parent/need/admission/plan/workflow/
evidence/successor chain. Recorded replay only verifies and deserializes captured
contracts: zero provider, model and network calls. Deterministic verification
re-runs admission, bridge mapping, successor projection and A4 evaluation from
captured material. A policy comparison requires a changed policy identity and
creates a distinct admission/comparison fingerprint.

## Facade decision

A4.2 remains internal. A genuine execution may be `LIVE_READ`, while the current
public local facade intentionally accepts captured reads only and has no stable
live lifecycle/provider-policy surface. Publishing a magical one-call operation
would either leak trusted service handles or misstate effects. A later facade
milestone may expose an explicit admitted lifecycle after `LIVE_READ` authority,
configuration and storage semantics are separately accepted.

## Explicit non-goals and residual risk

No live provider call is required or performed for milestone acceptance. The
typed workflow-side source-semantic projector is intentionally explicit; adding
production mappings for further provider-native shapes remains ordinary MI/
source-foundation work, not an A4 inference shortcut. Selective re-evaluation is
recorded at finding semantic-lineage granularity while deterministic arbitration
is rebuilt over the whole successor set. Model-backed challenge, Shell/report
UX, distributed execution and durable multi-writer storage remain deferred.

Acceptance evidence is in
[the A4.2 acceptance study](STUDY_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE_ACCEPTANCE.md).
