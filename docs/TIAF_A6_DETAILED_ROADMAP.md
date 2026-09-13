# TIAF A6 — Detailed Roadmap

## Current gate

2026-09-13 (Asia/Kolkata): **A5 FROZEN; R1–R5 ACCEPTED / DONE;
A6 ARCHITECTURE ACCEPTED / THESIS ACCEPTED AS NON-NORMATIVE COMPANION;
A6.1 ACCEPTED / DONE; A6.2 ACTIVE / NEXT;
`expression.assess` NOT_PUBLISHED.**

The [architecture](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md) defines
the proposed policy and boundaries; the [reconciliation record](TIAF_A6_RECONCILIATION_RECORD.md)
records inherited decisions and conflicts. This roadmap does not authorize
implementation. Its first gate is:

```text
Architecture + thesis reconciliation + acceptance (complete)
  → A6.1 contracts / admission / policy foundation (accepted / done)
  → A6.2 evaluation / ranking / replay (active / next)
  → A6.3 facade / Shell → A6.4 hardening → A7 → A8 → A9 → A10
```

The [architecture acceptance](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md)
approves A6.1 as the next slice. Do not freeze architecture now or begin A7.
Numeric defaults remain
the unchanged versioned engineering baseline for independent review, not
calibrated trading policy. Full-window evidence coverage is retained; TF-05's
candidate short-circuit proposal is deferred.

## Four bounded implementation slices, after acceptance only

Four slices combine the proposed separate ranking/replay slice with evaluation.
This avoids an interim selector that cannot explain or replay its selection.
Contracts still get an independent gate, and facade publication still follows
a usable deterministic core. Acceptance is demonstrated behavior, not scaffolding.

### A6.1 — Contracts, admission and deterministic policy foundation

Deliver additive immutable request/intent, admitted-input capture, timing,
identity, evidence, coverage, event, spread-foundation and policy contracts.
Implement strict upstream admission,
closed A2-direction mapping, Horizon resolution validation, schema/units/time
rules, fixed engineering-policy identity and separate operational failures.
Define canonical identity/fingerprint projections without a self-hash cycle.
Preserve A0 `OptionExpression` and every existing A2/A3/A4/A5 contract.

**Prerequisite before A6.2:** specify and test additive provider-neutral time
qualification (market observation versus acquisition, expiration versus trading
cutoff, availability by cutoff, sourced DAY session) and normal/confirmed-empty/
unavailable coverage variants. A1 empty expiry lists cannot prove absence. Select
the exact reviewed policy/profile; numeric limits are not domain-schema constants.
Name the accepted capture qualification path and missing-data behavior. Synthetic
fixtures can validate the contract; a live-qualified source is not thereby proven.
If no source satisfies it, retain insufficient and record the live-use limitation;
do not insert an acquisition-only fallback. No source procurement is authorized.

Acceptance evidence:

- List/JSON-array input, tuple immutability and JSON-array output; aware
  Asia/Kolkata normalization and naive rejection.
- All A4 dispositions/statuses, A2 veto, subject/horizon/direction conflicts,
  supported-primary requirements and source-parent integrity tested.
- Policy preference cannot weaken gates; required evidence absence explicit.
- Date-only expiry and acquisition-only quote time cannot masquerade as precise
  timing facts; no provider access or fresh-data inference.
- Schema, capability, package, policy and composition versions remain distinct.
- No callable `expression.assess` descriptor or Shell command published yet.
- Exact duration/bound equality, session ambiguity, confirmed-empty proof versus
  unavailable/partial data, nonempty duplicate-free preferences, unsupported
  cheapest/longest ranking, and one-preferred/two-alternative schema limits.

Implemented by [TIAF A6.1](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION.md)
and closed by its [independent acceptance](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION_ACCEPTANCE.md).
Exit achieved: contracts and admission accepted; this is not a claim of complete selection.

### A6.2 — Bounded evaluation, ranking, explanations and replay

Deliver the one-to-three-expiry, at-most-nine-candidate evaluator with listed
ATM/ITM1/OTM1 geometry; exact expiry fit, liquidity/freshness, premium/event
constraints; optional qualified IV/Greek context; deterministic lexicographic
ranking and all five analytical dispositions. Retain rejected, excluded,
not-selected and unknown states distinctly. Implement captures, semantic replay
and exact-pin deterministic verification together with the selector.

Required suites follow architecture §12: boundary/equality cases, irregular
strikes, listed absence versus missing data, coverage, zero factual values,
ineligible near expiry, events, stale/unqualified time, no-trade preservation,
shuffled-order invariance, decimal normalization and attribution for every claim.
Include all eight worked scenarios as synthetic fixtures, with no tuning to
their symbols. Prove replay uses captured cutoff/policy, makes no external call
and refuses unavailable pins or missing/tampered artifacts. Keep parent A4/A5
and upstream composition identities unchanged.

Add reconciliation regressions: failed horizon plus missing quote still withholds
selection; full gate/reason output is order invariant; 100 versus 101 bps changes
tier before preference without retuning; missing trading cutoff stays a disclosed
context limitation, not invented expiration authority; known in-window event
versus possibly intersecting uncertain event gives WAIT versus insufficient;
event-clear proof spans the entire holding window. Confirmed-empty proof may
produce no trade without chains; ordinary failed-expiry scope cannot discard
required slots. Optional zero OI/volume never becomes absence or a hidden gate.

Exit: standalone captured deterministic evaluation is reviewable and replayable;
no public live-acquisition, forecast, broker or Shell authority introduced.

### A6.3 — Governed facade, COLD composition and bounded TI Shell

Publish `expression.assess` only once callable, with a dedicated authority scope,
logical request artifact, versioned descriptor/schemas, CAPTURED_READ effect,
zero-external-call cost and explicit boundedness/replay metadata. Reuse existing
facade admission, artifact entitlement/revocation, profile/budget and error
boundaries. Add A6-specific run pins following R3; do not force A6 into A3.8's
specialist envelope or invent another composition owner.

Extend R5's explicit trusted configuration additively/versionedly only as needed
to select reviewed expression policies. Retain reading and documented behavior
of existing config 1.0 and legacy captures. Selection remains COLD, frozen and
separate from invocation authorization. No caller policy objects, arbitrary
plugins, new optional imports in core, environment overrides or HOT selection.

Publish the shared one-shot/REPL typed command and compact canonical rendering,
explain/trace/replay. Plain English, Web and remote APIs remain future adapters
to the same typed facade, not independent implementations. Test malformed,
unauthorized, revoked, wrong-kind and tampered artifacts; valid no-trade output;
descriptor/readiness honesty; core-only import isolation; unchanged existing
capabilities and immutable source/TM handoff metadata.

Exit: bounded local captured-input capability and Shell path accepted. This
contributes to TI_SHELL v1.0; it does not claim full conversational/Web delivery.

### A6.4 — Integrated hardening, acceptance and freeze readiness

Audit core + facade + Shell as one path. Reconcile docs and every deferral. Prove
zero A6 model calls/input-output tokens/model cost, provider calls and broker
operations; unchanged A2 benchmark/A4/A5 outputs; full exact replay and explicit
absence semantics. Test runtime-selected-but-unauthorized cases and exact pinned
verification under unavailable implementations.

A separately authorized bounded live-read exercise may capture real chain and
timing evidence outside the evaluator. It must report available/unknown timing
basis honestly; INSUFFICIENT_EVIDENCE is valid under the strict draft policy.
Do not fabricate an expiration instant or tune policy to force live selection.
If live usefulness requires a new data source or weaker freshness policy, stop
and seek that separate design/admission decision. No provider success can
substitute for synthetic replay/boundary tests.

Run the repository-required runtime quality gates for implementation slices:
compileall, focused/full pytest, Ruff, mypy and diff checks; record exact counts
and scope at that time. Finish with a closure/freeze-readiness review, not an
automatic tag, commit or push. Those operations require explicit authorization.

## Dependencies and non-dependencies

| Need | Position |
| --- | --- |
| Frozen A4/A5 and accepted R1–R5 | Existing inputs/boundaries to preserve, not new work. |
| Exact expiry/session and qualified quote timing | Required captured facts for the strict proposed policy; current A1 alone may be insufficient. Honest absence remains supported. |
| A1 capture extension | Additive provider-neutral qualification wrapper only as separately implemented; do not recalculate A2.7 or relabel acquisition time. |
| A7 | Not required. Later admitted forecast overlay is a separately versioned follow-up. |
| SigmaDSL / SigmaTrader | No A6 prerequisite; separate future programmable strategy product. |
| Multi-leg / short / portfolio optimization | Outside v1; no partial strategy engine. |
| A5 refresh / TI Monitoring | Metadata/successor-request seam only; no roll, scheduler or daemon. |
| Sector Rotation / Signal Qualification | Optional earlier captured inputs after their own acceptance; no circular runtime dependency. |
| TM / broker / scanner integrations | Ownership metadata only; A8/A9/A10 retain implementation ownership. |
| Full NLP / Web / Cockpit | Separate interaction delivery; shared typed facade architecture preserved. |

## Independent architecture acceptance checklist

The completed thesis teaches, visually, the owner chain, gate precedence, strike ladder,
expiry cushion, distinct observation/acquisition/cutoff and expiry timing, explicit
absence, immutable source versus TI analysis, A5 refresh, R1–R5 and replay.
It includes the eight concrete non-live scenarios and candidate table/CLI
mockups, without implying that commands already run.

Independently review the reconciled strict timing/source limitation, conservative
full-window coverage, provisional 24/72-hour cushions, 90-day bound, spread
tiers, event-coverage distinction and duration-entry UX before A6.1. Review the
fourteen decisions, deferred TF-05 optimization, empty-scope proof and context-only
trading-cutoff treatment. A handbook example is not policy authority. Acquisition-
qualified policies remain unapproved. Do not hide these choices in implementation.

**Next prompt:** `TIAF A6.1 — CONTRACTS, ADMISSION & POLICY FOUNDATION`.
