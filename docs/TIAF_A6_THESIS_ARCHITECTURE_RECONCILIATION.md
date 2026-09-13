# TIAF A6 — Thesis / Architecture Reconciliation

## Decision and scope

Successor decision: the
[independent architecture acceptance](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md)
records **READY_TO_IMPLEMENT_A6_1**. A6 architecture is accepted; the thesis is
accepted as non-normative companion; A6.1 is active/next; runtime remains
NOT_IMPLEMENTED. This record's READY_FOR decision below is the completed prior gate.

2026-09-13, Asia/Kolkata: **READY_FOR_A6_ARCHITECTURE_ACCEPTANCE**.

```text
A5 FROZEN
R1–R5 ACCEPTED / DONE
A6 ARCHITECTURE RECONCILED
A6 THESIS RECONCILED
A6 ACCEPTANCE NEXT
A6 RUNTIME NOT_IMPLEMENTED
```

This is the requested documentation-only reconciliation, not independent
acceptance, implementation readiness or policy calibration. Entry HEAD was
`928a12b`; prior architecture/thesis/navigation work was already uncommitted.
That work is preserved. The open Word lock file is user-owned and untouched.
No runtime, frozen A5, dependency, provider, Shell registry or A7 implementation
changes; no live provider/model/broker calls; no commit, tag or push.

## Actual sources and review method

Read the complete text extracted from the actual [DOCX thesis](TI_Trade_Expression_Intelligence_Thesis.docx),
including eight cases, FAQ and all findings, and inspected findings on PDF pages
28–30 of the [rendered edition](TI_Trade_Expression_Intelligence_Thesis.pdf).
Compared the underlying chapters, not only the creation-record summary, with:

- [A6 architecture](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md),
  especially §§4–7, 9–10 and 12–13.
- [A6 roadmap](TIAF_A6_DETAILED_ROADMAP.md),
  [original source reconciliation](TIAF_A6_RECONCILIATION_RECORD.md) and
  [thesis creation record](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_THESIS_RECORD.md).
- Current navigation and [deferral register](TIAF_DEFERRAL_REGISTER.md).
- Actual [derivative contracts](../src/tiaf/data/derivatives.py): expiry is a
  date, and empty `ExpiryListSnapshot.expiries` requires UNAVAILABLE quality.
- [Dhan derivative parser](../src/tiaf/data/providers/dhan/derivatives_parser.py):
  retrieval-time observations are explicitly labeled; receipt is not an
  authoritative market-event timestamp. No generalization to unrelated quote APIs.

The original source record inventories the supporting A4/A5, ecosystem,
pluggability, Shell, monitoring and provenance authority. Their boundaries are
preserved here; no claim that every historical document was reread in full.

The thesis is an unchanged dated design-review artifact. Its “reconciliation
next” wording and open questions describe its creation checkpoint, now answered
by this record and the revised normative Markdown. No actual authority or worked-
case inconsistency required changing the DOCX/PDF. They are not regenerated.

| Unchanged thesis artifact | SHA-256 |
| --- | --- |
| DOCX | `7685620e91b9b8cb2365a03d39b92e95690ebad66cf60673cee5c7e426a0b39a` |
| PDF | `048ee91fc62353c7b372ebf52fa9aeb133fef30d95cb280fca2e2fa08c63ed1b` |

## Fourteen-finding matrix

Page numbers refer to the unchanged 32-page PDF. Classification preserves the
thesis category; final decision is this reconciliation's disposition. `ARCH`
means the A6 architecture, `ROAD` the A6 roadmap, `DEF` the deferral register,
`RECORDS` both prior reconciliation/creation records. Every row is also recorded
here; navigation records the combined outcome rather than individual semantics.

| ID / title | Thesis section / page (finding page) | Architecture source | Classification | Impact if ignored | Recommended resolution | Final decision | Files updated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TF-01 Market-time feasibility | Ch8 pp10–11; Ch20 pp28–29 | §§4.1, 6.3, 10, 13 | CLARIFICATION_NEEDED | Receipt freshness could masquerade as market freshness. | Require field-qualified market time; expose current source gap and stage timing contracts before evaluation. | CLARIFICATION ADOPTED; strict time retained, weaker fallback not approved. | ARCH, ROAD, DEF, RECORDS |
| TF-02 Date-only expiry | Ch6 p8; Ch8 p11; Ch20 p29 | §§4.1, 6.2–6.3 | CLARIFICATION_NEEDED | Invented close time could falsely pass residual life. | Require sourced expiration; keep trading cutoff separate/contextual, never infer exit tradability. | CLARIFICATION ADOPTED; no calendar or new cutoff gate. | ARCH, ROAD, DEF, RECORDS |
| TF-03 Provisional limits | Ch6 p8; Ch8 pp10–11; Ch16 p19; Ch20 p29 | §§6, 6.2–6.3, 9 | CLARIFICATION_NEEDED | Illustrations could become unversioned or purportedly calibrated constants. | Separate invariant requirements from exact versioned policy values. | CLARIFICATION ADOPTED; all existing draft numbers unchanged for independent acceptance. | ARCH, ROAD, RECORDS |
| TF-04 Spread-tier discontinuity | Ch10 p13; Case6 p22; Ch20 p29 | §§6.3, 7, 12 | CLARIFICATION_NEEDED | Preferred contract could receive a fabricated liquidity explanation. | Confirm tier before preference and explain exact decisive key. | CLARIFICATION ADOPTED; no threshold or rank tuning. | ARCH, ROAD, RECORDS |
| TF-05 Unknown after decisive rejection | Ch5 p7; Ch12 pp14–15; Ch20 p29 | §§5, 6.1, 6.2, 10 | ARCHITECTURE_CHANGE_PROPOSED | Short-circuit could change coverage, disposition and replay. | Retain full-window scope; explicitly test failed gate plus another unknown. | DEFER; proposal not adopted. | ARCH, ROAD, DEF, RECORDS |
| TF-06 Duration-entry UX | Ch4 p6; Ch6 p8; Ch15 pp17–18; Ch20 p29 | §§4.1, 6.2, 9 | CLARIFICATION_NEEDED | 3w/BTST could silently change the target or upstream horizon. | Explicit target/style and exact elapsed duration; resolve labels above core. | CLARIFICATION ADOPTED; typed bounds/adapter confirmation separated. | ARCH, ROAD, RECORDS |
| TF-07 Preferred plus two alternatives | Ch10 p13; Ch20 p29 | §§4.3, 6, 7 | NO_CHANGE | UI limit could become unbounded canonical output or hide evaluated rivals. | Keep complete bounded evaluations and a schema-bounded top three. | NO_CHANGE; clarify normative v1 schema maximum. | ARCH, ROAD, RECORDS |
| TF-08 Cheaper-premium intent | Ch7 p9; Ch15 p18; Ch20 p29 | §§6.4, 7, 9 | CLARIFICATION_NEEDED | “Cheapest” could silently create a new policy or sizing claim. | Cap only; cheapest/longest ranking unsupported; no implicit OTM mapping. | CLARIFICATION ADOPTED; ranking extensions excluded. | ARCH, ROAD, RECORDS |
| TF-09 Plain-English confirmation | Ch4 p6; Ch15 p18; Ch20 pp29–30 | §§4.1, 9 | CLARIFICATION_NEEDED | NLP could become mandatory domain logic or imply trade consent. | Adapter resolves ambiguity and preserves typed intent; core validates only. | CLARIFICATION ADOPTED; NLP/Web delivery remains deferred. | ARCH, ROAD, DEF, RECORDS |
| TF-10 Event materiality/coverage | Ch9 p12; Ch12 pp14–15; Ch20 p30 | §§5, 6.4 | CLARIFICATION_NEEDED | Unknown event time could become a fabricated WAIT or all-clear. | Define scope/window/materiality source and uncertainty rules. | CLARIFICATION ADOPTED; possible intersecting material event unknown is insufficient. | ARCH, ROAD, RECORDS |
| TF-11 Empty fitting universe | Ch5 p7; Case3 p21; Ch20 p30 | §§4.1, 6.1–6.2 | CLARIFICATION_NEEDED | Empty-but-proven scope could be malformed, or missing data called no trade. | Add explicit confirmed-empty/unavailable wrapper variants; no A1 reinterpretation. | CLARIFICATION ADOPTED with additive representation detail; zero-chain proof path, not coverage short-circuit. | ARCH, ROAD, RECORDS |
| TF-12 Readable exact comparisons | Ch10–11 p13; Ch15 pp17–18; Ch20 p30 | §§7, 9–10, 12 | IMPLEMENTATION_DETAIL_ONLY | Rounded rendering could change tie-breaks or fingerprint identity. | Exact canonical computation, accessible separate display. | ASSIGNED TO A6.2/A6.3 acceptance tests; no runtime implementation here. | ARCH, ROAD, RECORDS |
| TF-13 Nearest-listed ATM terminology | Ch5 p7; Ch7 p9; Ch20 p30 | §§6.1, 7 | CLARIFICATION_NEEDED | Geometric anchor could be mistaken for zero intrinsic value or fixed delta. | Separate neighborhood labels from economic spot/strike comparison. | CLARIFICATION ADOPTED; lower tie and actual neighbors unchanged. | ARCH, ROAD, RECORDS |
| TF-14 Broader intelligence/interaction | Ch18 pp24–25; Ch19 pp26–28; Ch20 p30 | §§3, 8–9 | DEFER | Examples could import multi-leg, A7, NLP or recurring operations into v1. | Preserve separate future gates and acyclic consumers. | DEFER retained; SigmaDSL excluded, not a v1 prerequisite. | ARCH, ROAD, DEF, RECORDS |

All 14 accounted for: ten clarifications adopted, one proposed change deferred,
one no-change retained, one implementation detail assigned, one deferral retained.
No architecture relaxation or new ranking criterion is adopted. Clarifications
do add testable contract requirements (notably absence representation and event
uncertainty); they are not claimed to be already delivered runtime behavior.

## Timing, policy and liquidity resolutions

Strict qualified market observation remains required for quote/top-book/spot
age. Acquisition says when TI obtained the evidence; cutoff defines what was
knowable. Scheduled future events may be known by cutoff, but future quote
observations may not. An aware timestamp or timezone conversion creates neither
market-time authority nor a precise expiration instant. Derive only elapsed age,
residual life and cushion excess from qualified operands. Date-only expiry and
acquisition-only chain evidence remain inadequate; report insufficient, not WAIT.

Expiration is contract lifetime; last trading cutoff is a separate fact. The
retained gate measures expiration fit, **not guaranteed exit tradability**.
Supplied cutoff is attributable context, absence a disclosed limitation. This
review deliberately does not add a cutoff gate or infer exchange hours. TM owns
action-time checks; any later exit-tradability profile needs independent design.
Acceptance should scrutinize that bounded claim rather than read “suitable” as
an execution guarantee. A6.1 qualification contracts precede A6.2; actual live
source feasibility remains unproven. No acquisition-qualified fallback approved.

Freshness requirements are normative; concrete seconds/minutes are exact policy
data. Retain draft `deterministic-long-option/1.0-draft`: quote/spot maximum 60s,
DAY upstream 15m, POSITIONAL upstream 24h, 24/72h cushions, 90-day positional
bound. These predate the thesis and are unchanged engineering review values, not
calibrated economic advice or permanent schema constants. Exact pins/content
digest prevent replay from inheriting today's settings. Selection stays COLD.

Bid/ask, positive top quantities, qualified identity/time/units, expiration fit
and scoped coverage are required. A spread above 500 bps fails; eligible tiers
are ≤100 and >100–500 under the draft policy. Worse tier affects rank, not a
weighted gate offset. OI/volume zero is factual; absence remains optional context,
as do LTP, full depth and qualified IV/Greeks. They cannot replace bid/ask or top
quantities. A premium cap and complete event-clear coverage are request-dependent
requirements; no hidden OI/volume/profile thresholds are introduced.

## Duration, preferences and interaction

Typed DAY/POSITIONAL plus explicit `as_of`/`intended_exit_at` and compatible Horizon
bounds determine exact elapsed duration. Calendar days mean 24 hours in this
Asia/Kolkata baseline, not sessions. Labels are presentation. BTST/intraday/session
language must resolve via qualified timing or be declined above core. No silent
target shortening. Unsupported well-formed horizons remain UNSUPPORTED; internal
request contradictions and unknown schema fields are validation failures.

Closed nonempty duplicate-free ATM/ITM1/OTM1 restriction/order is allowed below
hard gates and spread tier. Cheapest-premium and longest-expiry ranking are not
v1 features. A per-unit cap is neither a cheaper-first rule nor quantity advice.
A different target creates a newly admitted request, not a preference loophole.
Policy thresholds/version come from the existing COLD owner, never user objects.

One preferred plus up to two alternatives is a v1 schema bound; populate the
next two when eligible and preserve every ≤9 evaluation. Display can collapse
rows, not change result meaning. Explain exact comparison and geometric ATM
versus economic moneyness; no inferred delta or synthetic strike spacing.

Plain English/Web/CLI/API are adapters above the same typed capability. Ambiguous
interpretation needs explicit resolution and retained original/normalized intent,
not an NLP dependency inside A6. Intent confirmation never grants trade consent.
The proposed name remains `expression.assess`: governed logical artifacts,
CAPTURED_READ, deterministic, replayable, one-shot/REPL parity, no direct provider
path or LIVE_READ claim. It is **not published** as a ninth operation here.

## TF-05 early-termination decision: DEFER

The hoped-for benefit is reduced acquisition cost/latency for rejected candidates.
It is not measured here, and the evaluator itself never acquires evidence.
Changing capture requirements could benefit a future acquisition planner, but
the present rule requires all selected-window hard-gate evidence.

Counterexample: declared expiry A has a proved horizon failure and unknown quote;
expiry B has complete valid candidates. Current §5/§6.1 result is insufficient.
Discarding A's quote requirement permits B to become AVAILABLE. Therefore the
proposal is **not semantically equivalent** to the current baseline and cannot
be labeled an implementation optimization.

Retain complete requirements, stable gate reporting order, UNKNOWN dependencies
and all evaluable failures. Benefits do not yet outweigh changed coverage,
incomplete explanations, gate-order dependence, replay identity changes and
rejected-candidate comparability. Upstream veto/wait short-circuits remain
separate admitted disposition branches with explicit selection-not-run reasons.
Shared computations/caching are acceptable only if output and semantic identity
remain identical; do not omit facts or gate outcomes.

Revisit only under DEF-006's separately reviewed post-baseline policy work:
specify an exhaustive reference policy that agrees with the proposed short-
circuit semantics, deterministic gate order, explicit short-circuit reason and
untested/unknown representation, then prove complete semantic equivalence to
that versioned reference with adversarial replay tests. It must not retroactively
change the existing full-coverage baseline or its captures. No cost claim is
made from synthetic examples.

## Dispositions, empty scope and events

| Condition, subject to documented §5 precedence | Canonical outcome |
| --- | --- |
| Valid scope, complete required facts, no eligible candidates | NO_OPTION_TRADE; evaluated scope and failures explicit. |
| Intact upstream A2/A4 prohibition | NO_OPTION_TRADE; selection not run, never a claim of tested illiquidity. |
| Known upstream wait/conflict or admitted in-window material event | WAIT_FOR_EXPRESSION; original blocker retained, no automatic retry/guaranteed future viability. |
| Required data stale/missing/ambiguous; possibly intersecting admitted material event with unresolved time | INSUFFICIENT_EVIDENCE, not invented wait/all-clear. |
| Well-formed outside-v1 shape/horizon/instrument | UNSUPPORTED, not a market judgment or substituted expression. |
| All required coverage established and at least one survivor ranked | EXPRESSION_AVAILABLE; advisory shortlist only. |
| Integrity, authorization or malformed schema failure | Operational failure; no fabricated analytical disposition. |

TF-11 distinguishes a complete-empty **expiry list** proof (zero chains allowed
in an additive A6 variant) from an empty **fitting subset** after full evaluation
of a nonempty declared scope. Missing provider data is insufficient; A1 empty
UNAVAILABLE responses cannot establish positive absence. No horizon-prefilter
loophole is allowed to bypass TF-05. Ordinary scope declares one-to-three expiry
identities, max512 strikes each and max9 selected candidates. Proof coverage and
scope exclusions are explicit, never claims of searching the entire market.

Event materiality/relevance comes from admitted upstream source/rule evidence.
Event-clear proof must cover the subject, declared material categories and full
`(as_of, intended_exit_at]` interval. Known exact in-window events yield WAIT;
possibly intersecting uncertain material events yield insufficient. Generic
unknown broad coverage remains an optional disclosed gap unless event-clear is
requested. There is no invented sentiment, adjacency buffer or probability.

## Preserved boundaries and replay

A4 NO_TRADE/AVOID and A2 veto remain prohibitions. A6 neither invents nor repairs
thesis, recalculates A2/A3/A4/A5, nor treats conflict as bullishness. A5 refresh
is advisory successor lineage, never an auto-roll or runtime A5→A6 call. TM owns
account/risk/capital/sizing/action-time validation/execution intent. Broker owns
actual live order/fill truth. None of the eight cases contradicts these owners.

A7 target-hit probabilities, calibrated distributions, expected value and
forecast-derived optimal strikes remain future, separately accepted evidence;
retain the deterministic control. Monitoring, Sector Rotation and Signal
Qualification exchange immutable earlier/successor versions, not circular
runtime dependencies. SigmaDSL is outside TI A6 v1: no parser/compiler/runtime
or compatibility layer, no mandatory A6 integration. A future SigmaTrader product
is separate.

Replay records typed intent and exact horizon/cutoff, upstream refs, native and
canonical evidence, declared universe and proof/gaps, all gates/ranks, preferred/
alternatives/rejected/not-selected states, reasons, policy/profile/composition
pins, fingerprints and invalidations. Timing meanings/availability are semantic;
display rounding and latency are not. Exact-pin verification refuses missing
artifacts/versions, never fetches today's market or falls back to current policy.

## Roadmap and deferral reconciliation

| Slice, after architecture acceptance | Reconciled obligation |
| --- | --- |
| A6.1 Contracts, admission and policy | Typed timing/coverage prerequisites, strict absence proof, exact duration, frozen collections, exact policy identity and admission; no publication. |
| A6.2 Evaluation, ranking, explanation and replay | Full required coverage, exact boundaries and all fourteen finding regressions; synthetic captured reference first, no acquisition in selector. |
| A6.3 Facade and TI_SHELL | Existing COLD owner and governed artifact facade; typed REPL/one-shot parity, bounded rendering, exact replay; publish only when callable. |
| A6.4 Hardening, acceptance and freeze readiness | Full implementation gates, explicit live limitations, no authority drift; independent closure, never automatic tag. |

DEF-006 stays PLANNED: bounded A6 unimplemented, broader strategies and TF-05
future policy still open. DEF-014 stays DEFERRED with explicit A6 timing-source
revisit; DEF-007 stays DEFERRED with precise expiry/session qualification tracked
without claiming a calendar implementation. DEF-025 stays DEFERRED for separate
strategy/product review; historical A6-closure wording does not create a DSL gate.
DEF-039–046 models, DEF-044 A7 probabilities, DEF-054 rich reporting/NLP/Web,
DEF-010 monitoring/runtime and DEF-056 multi-leg A5 remain open. No IDs added,
deleted or renumbered, and no status closed. The register owns current wording;
dated historical closure tables remain intact.

## Files changed and validation

Created this reconciliation. Updated the A6 architecture, detailed roadmap,
original reconciliation record and thesis creation record; README, ARCHITECTURE,
MILESTONES, IMPLEMENTATION_ROADMAP, TRADINGINTELLIGENCE_ROADMAP,
TIAF_IMPLEMENTATION_TARGETS, TIAF_CAPABILITY_MAP, TIAF_SYSTEM_ARCHITECTURE,
TIAF_TRADING_ECOSYSTEM_ARCHITECTURE and TIAF_DEFERRAL_REGISTER. All are Markdown
documentation: one new file and fourteen updated files in this pass. Thesis
binaries and authoring source/tooling are untouched; ecosystem changes only
synchronize its current A6 navigation, preserving ownership semantics.

Final static validation using the repository virtual-environment Python:

- `git diff --check`: PASS.
- **564 local Markdown links/anchors across 16 changed/untracked Markdown
  documents**, plus balanced fences: PASS. Counts include preserved prior work.
- **58 unique sequential canonical deferral IDs**, identical IDs/statuses to
  HEAD, valid categories: PASS. Counts: 45 DEFERRED, 4 PLANNED, 4 IMPLEMENTED,
  3 REJECTED, 2 SUPERSEDED. No added/deleted/renumbered/closed record.
- **Nine current navigation documents** agree on architecture/thesis reconciled,
  acceptance next and runtime NOT_IMPLEMENTED; all link this record. Fourteen
  matrix IDs are unique/complete; architecture/roadmap/record next titles agree:
  PASS. Historical checkpoint sections are explicitly labeled as history.
- Both thesis artifact SHA-256 values unchanged: PASS. Documentation-only scope
  confirmed across 21 changed/untracked files including preserved prior work;
  the user-owned Word lock is excluded and untouched. No runtime file changed.

No dedicated repository documentation/deferral/status checker was found in
scripts/tests/configuration; these were explicit read-only standard-library
checks, not claims of runtime tests or rendered diagram validation. No full
runtime suite or DOCX/PDF regeneration was run for unchanged runtime/binaries.

## Residual questions for independent acceptance

These are explicit review choices/implementation prerequisites, not hidden
permission to improvise: approve or revise the retained draft policy numbers;
confirm strict timing with current live-data limitations; confirm expiration-fit
without a default last-trading-cutoff gate; validate the additive absence-proof
schema and event qualification path in A6.1. No production source feasibility,
economic calibration, NLP/Web runtime or acquisition-qualified profile is
claimed. Any rejected design choice returns to reconciliation before A6.1.

Historical next prompt at this checkpoint:
`TIAF A6 — TRADE EXPRESSION INTELLIGENCE ARCHITECTURE ACCEPTANCE`.
Current next prompt is recorded by the successor acceptance document.
