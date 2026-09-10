# TIAF A3.9 — User-level acceptance

## Scope and status

Implementation/validation date: 2026-09-10, Asia/Kolkata. Base HEAD `75ad730`;
accepted A3.8 tag `tiaf-a3.8` resolves to `eb96879`. Prior architecture-pass
documentation changes were preserved. Implementation is complete, awaiting
user acceptance/freeze; no commit, tag or push was performed.

Authority: [approved A3.9 design](TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md).
A3.8 chooses work. A3.9 describes captured observations. A4 owns arbitration and
recommendations. No A2 or accepted specialist interpretation policy changed.
No external live call, new dependency, `.env` read/change or secret was needed.

## Public seam and work packages

Runtime package: `src/tiaf/service/opportunity_intelligence/`.

| Work package | Implementation |
|---|---|
| WP1 contracts/handoff | `contracts.py`, `handoff.py`: frozen `ContractModel` records, tuple collections accepting JSON/Python lists, schema 1.0, aware Asia/Kolkata timestamps, capture validation |
| WP2 contributions/lineage | `contributions.py`: active opinions, original reused packs, superseded audit, selected/skipped applicability, shared canonical roots |
| WP3 synthesis | `policy.py`: explicit v1 mappings, TRUE/FALSE/UNKNOWN, eight ordered rules, qualified bias without votes |
| WP4 conflicts/completeness | `assembly.py`, contribution profiles: typed contradiction classes, captured confirmation/research/graph outcomes, separate confidence |
| WP5 explanations | Cited typed reasons/templates, original reason codes, source locators and inert prerequisites |
| WP6 replay | `replay.py`: exact capture validation, recorded replay and deterministic assembly-only verification |
| WP7 application seam | `__init__.py`: public exports independent of any execution adapter |
| WP8 acceptance | `scripts/a3_9_user_acceptance.py`, loader and 18 persisted captures |
| WP9 hardening | `tests/unit/opportunity_intelligence/`: integrity, lineage, policy and execution/import boundaries; repository gates below |

Primary public types: `OpportunityIntelligenceRequest`, `OpportunitySynthesisPolicy`,
`StructuredOpportunityIntelligence`, `OpportunitySummary`, `SpecialistContribution`,
`BaselineView`, `Contradiction`, `CompletenessProfile`, `IntelligenceReason`,
`OrchestrationAuditLink`, `IntelligenceRunRecord` and `DeterministicComparison`.
Supporting facets, source locators, context, bias, lineage, prerequisite and trace
records are defined in `contracts.py`. No metadata action/winner escape hatch.

```python
from pathlib import Path
from tiaf.service.opportunity_intelligence import (
    request_from_capture, default_policy, assemble_opportunity_intelligence,
    capture_intelligence, replay_intelligence, verify_intelligence,
)

request = request_from_capture(
    Path("captured_a38.json").read_text(),
    request_id="inspection-001", policy=default_policy(),
)
run = assemble_opportunity_intelligence(request)
saved_json = capture_intelligence(run)
assert replay_intelligence(saved_json) == run
assert verify_intelligence(saved_json).exact_match
```

Only a captured A3.8 envelope is accepted. Subject, instrument, horizon, purpose,
style and as-of come from it, never side-channel replacements. Invalid checksums,
unsupported schemas/policies, mismatched identities, missing artifacts, altered
invocation/consumption digests, unresolved citations, inconsistent projections or
outcomes are integrity errors, not market-data insufficiency. Full source capture
is retained for exact audit; validation never calls A3.8 deterministic verification.

## State, bias and restrictions

Policy `a3.9-observation-v1`, version `1.0`, accepts its explicit supported snapshot;
editing mappings under the same version is rejected. No fitted weights/thresholds.
All predicates and all matching rules are retained; first TRUE rule wins:

| Order | Gate | Observation |
|---|---|---|
| 1 | A2/Technical/Quality/Risk core not usable | INSUFFICIENT_EVIDENCE |
| 2 | Unresolved comparable/material conflict | CONFLICTED |
| 3 | Captured CRITICAL Risk | AVOID |
| 4 | Timing/chase/event restriction or HIGH Risk | WAIT |
| 5 | A2 NO_TRADE | WATCH only with cited support, directional qualified bias and LOW/MODERATE Risk; otherwise NO_TRADE |
| 6 | Complete usable supported setup | OPPORTUNITY |
| 7 | Qualified support | WATCH |
| 8 | No supported setup | NO_TRADE |

UNKNOWN never satisfies a positive gate. Partial/aging evidence can remain a
usable quoted facet, but complete OPPORTUNITY requires required GOOD/FRESH coverage,
Quality GOOD/STRONG, LOW/MODERATE Risk and no unresolved qualifications/timing.
STRONG is Quality, not a new observation state. AVOID_CHASE is a WAIT reason.

Only Technical contributes to the price-structure directional facet. Other domain
stances remain context, not price votes. Material positional weak-company tension
can qualify the headline as MIXED without replacing Technical's direction. Expensive
valuation alone qualifies support, not CRITICAL risk. High material event plus high
execution risk restricts timing; a disputed event gate remains CONFLICTED. Optional
adverse evidence can restrict even when it is not needed in the coverage denominator.

Quality/Risk remain downstream summaries. A cited Quality supportive family can
represent existing underlying support, never another independent vote. Root-lineage
groups collapse repeated/shared canonical source IDs across projections and provider
wrappers; unresolved independence is explicitly UNKNOWN. No confidence average,
vote count, source-brand preference or hidden arbitration is computed.

Contradiction kinds remain distinct: BASELINE_DISAGREEMENT, SAME_PROPOSITION,
CROSS_DOMAIN_TENSION, SOURCE_DISCREPANCY and AUTHORITATIVE_FIELD. Known Technical
directional-dimension conflicts share a price axis; unclassified source tension has
UNKNOWN comparability/materiality, not fabricated certainty. Captured source-level
material unresolved conflicts restrict; field confirmations do not confirm a thesis.
NOT_FOUND is not falsehood. An active interpretation that did not consume a relevant
captured confirmation is marked unusable with a prerequisite, not rewritten/rerun.
Research/graph epistemic labels and ambiguous semantics remain visible and cannot
independently satisfy factual completeness.

## A2, confidence, evidence and replay

The original A2 capture bytes, assessment reference and fingerprint are retained.
The complete original direction/class/score pack projection is required, or an
explicit BASELINE_CONTENT_MISSING gap is emitted. Contradictory copies fail. If a
full typed A2 assessment was captured in original A2 pack metadata under
`baseline_assessment`, it is preserved with components/warnings and checked against
the projection. This is not a caller side channel. Missing full assessment content
is never recalculated. Eligibility is copied only when captured, otherwise
`NOT_CAPTURED`/null; it is not inferred. A2 NO_TRADE never becomes OPPORTUNITY.

Each original AgentConfidence/basis is retained separately from completeness sets
and the applicable required-coverage ratio. Verified non-F&O and index exclusions
do not add missing requirements; unknown F&O applicability stays unknown. Source
confidence is not a success probability. Gap prerequisites are inert.

Reasons quote typed field values, source opinion/run/schema/evidence/fact IDs,
categories and rule IDs. Source prose/metadata cannot select policy or state.
Facet citation sets conservatively retain the source opinion's supplied evidence;
they do not claim a newly inferred minimal per-field causal attribution. Original
typed detail remains available in the capture. Reasons sort by category, code and
stable ID; predicates/rules retain policy order. Confirmation/research citations
retain their artifact IDs and original epistemic status.

Exact capture checksum covers stored content. Semantic fingerprint includes product,
explicit policy, traces, original source semantic identity, quality, evidence times
and known consumption. It excludes only new assembly clocks/elapsed time and scoped
source transport/adapter timing already excluded by A3.8, not market as-of/freshness.
JSON key/formatting order and serial/LangGraph operational labels do not affect
meaning; ordered workflow decisions remain audit semantics, not freely sortable data.
Recorded replay validates the stored product; deterministic verification runs only
A3.9 assembly and compares fingerprints. Neither regenerates specialist opinions.

## Observed public acceptance cases

Command: `.venv/bin/python scripts/a3_9_user_acceptance.py`.
All cases are offline synthetic observations, not live company assessments.

| Case | Observed state |
|---|---|
| aligned | OPPORTUNITY |
| weak_company | CONFLICTED |
| valuation | WATCH |
| poor_timing | WAIT |
| extended | WAIT, AVOID_CHASE reason |
| critical | AVOID |
| event_risk | WAIT |
| disputed_event | CONFLICTED; timing rule also retained |
| conflict | CONFLICTED, qualified bias MIXED |
| baseline_watch | WATCH; original A2 NO_TRADE retained |
| baseline_no_trade | NO_TRADE |
| abstain | INSUFFICIENT_EVIDENCE |
| stale | INSUFFICIENT_EVIDENCE |
| non_fno | OPPORTUNITY; derivatives NOT_APPLICABLE |
| unknown_fno | WATCH; applicability remains UNKNOWN |
| index | OPPORTUNITY; company Fundamental not required |
| negative | OPPORTUNITY; negative price bias is not a short/SELL instruction |
| sparse_kaynes | INSUFFICIENT_EVIDENCE; original NO_TRADE and sparse gaps retained |

Seventeen hypothetical captures use explicit synthetic precomputed specialist
details through the accepted A3.8 fixture pipeline. They validate assembly, not
whether current raw market facts imply those details. `sparse_kaynes` captures the
existing accepted A3.8 sparse fixture using unchanged specialists. No historical
live A3.8 KAYNES capture was found locally; this is not claimed as recovered live
acceptance. No supportive architecture illustration was borrowed. Its insufficient
result is preserved rather than tuning policy to obtain WATCH.

All public cases require equal recorded replay and deterministic semantic hashes.
New A3.9 provider calls, specialist executions, model calls, input/output tokens
and model cost are zero. The script separately prints imported A3.8 usage. Context
unit tests also exercise nonzero imported fixture-provider usage while downstream
usage remains zero. No live external provider was called in this pass.

## Validation

All commands used the repository `.venv` (Python 3.12); no live access required.

| Gate | Final result |
|---|---|
| `python scripts/a3_9_user_acceptance.py` | PASS: 18 / FAIL: 0; recorded replay equality and deterministic fingerprint parity in every case |
| `pytest -q tests/unit/agents tests/unit/market_intelligence tests/unit/planner tests/unit/workflows` | 489 passed in 13.54s |
| `pytest -q tests/unit/opportunity_intelligence` | 65 passed |
| `pytest -q` | 1,860 passed in 30.35s |
| `python -m compileall src scripts` | Passed |
| `ruff check src tests scripts` | All checks passed |
| `mypy src tests` | No issues in 430 source files |
| `git diff --check` | Passed; also checked all 35 untracked files against `/dev/null`, no whitespace failures |
| `python -m pip check` | No broken requirements found; sandbox cache permission warning only |
| Changed-document relative file links | 102 checked, none missing |

Integrity hardening found and corrected malformed-checksum error wrapping,
projection/outcome identity checks, baseline-disagreement versus unknown source
conflict classification, and stale cited facts hidden behind fresh pack summaries.
These were implementation/test findings, not changes to accepted upstream policies.
Boundary tests demonstrate no provider/router/runtime/coordinator/socket call and
no model/transport/LangGraph imports while assembling and verifying captures.

Implementation recommendation: **READY_TO_ACCEPT_A3_9**. No remaining acceptance
blocker found within the captured-input MVP scope. User acceptance/freeze remains
separate; this pass does not claim live KAYNES validation or empirical profitability.
Suggested commit message (not committed):
`feat(a3.9): assemble replayable structured opportunity intelligence from A3.8 captures`.

## Files and boundaries

Added seven runtime modules (`__init__`, `contracts`, `handoff`, `contributions`,
`policy`, `assembly`, `replay`), two scripts, the fixture README and 18 compressed
captures, test package/authoring helper and three test modules. Updated this study,
A3.9 design, README, CHANGELOG, scripts README, architecture indexes, A3 detailed
roadmap, capability map and implementation targets. A1/A2/A3.1–A3.8 source,
dependency manifests/lockfiles, `.env` and the deferral register are unchanged.

Tests block provider/router/runtime/coordinator/network execution and framework,
model and transport imports during assembly/replay. AST and schema checks exclude
winner/arbitration, action, position, option-expression and forecast fields.
There is no A4/A5/A6/A7 authority, broker call, ranking, scanning, scheduler or UI.

Limitations: one captured underlying per request; explicit known v1 source schemas
and mappings only; no profitability/accuracy claim; unknown lineage independence
stays unknown; generic context restrictions are conservative, not an adjudication.
No new A3.10 corpus/cost harness or A4–A10 design is introduced. Future replay and
failure hardening belongs to A3.10. No TI Shell or provenance-fabric redesign.
