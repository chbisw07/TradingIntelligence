# POST_A3_PRE_A4_FOUNDATION

**Implemented deterministic foundation, schema `1.0`, 2026-09-11
(Asia/Kolkata).** This milestone implements source semantics and an A4 input
projection. It does not implement an A4 Challenger, Arbitrator, disposition,
model lane, provider, broker operation, public API or user interface.

## Boundary and placement

The additive `tiaf.source_semantics` package is the provider-neutral boundary
between frozen A2/A3 captures and future A4 reasoning. Existing A3 contracts
remain unchanged. The package depends on A3.10 validation/replay and A3.9
recorded reconstruction, but neither imports provider clients nor invokes a
specialist, model, broker or network service.

The package contains:

- `enums.py`: closed authority, epistemic, comparison, dispute, independence
  and admission vocabularies;
- `contracts.py`: frozen schema-`1.0` semantic and capture records;
- `comparison.py`: deterministic comparability, value-conflict and dispute
  lifecycle functions;
- `confirmation.py`: a field-scoped view over an unchanged authoritative
  confirmation result;
- `projection.py`: integrity validation and deterministic A4 input projection;
- `replay.py`: exact capture, offline reconstruction, policy comparison and
  successor validation.

## Identity model

The canonical model keeps these identities separate:

| Identity | Meaning |
| --- | --- |
| `SourceEntityIdentity` | Publisher, issuer, speaker, distributor or explicit unknown source. |
| `ProviderAdapterIdentity` | Transport/provider and adapter implementation identity. |
| `UpstreamOriginIdentity` | Known or unknown origin from which an occurrence derives. |
| `DocumentFamilyIdentity` | Stable publication/document family. |
| `DocumentVersionIdentity` | Content-addressed version with explicit revision relation. |
| `EvidenceOccurrenceIdentity` | One acquired observation, its evidence ID, origin, source and optional provider/document. |

IDs are namespace-qualified. Arbitrary URLs are rejected as canonical IDs;
locators remain qualified references. Provider is not source, adapter is not
publisher, and equal bytes do not prove independent origin. Original A3 IDs may
be retained as references. All times use aware `TiafDateTime` and serialize in
the canonical `Asia/Kolkata` timezone.

A changed document hash creates another version but does not itself mean a
correction. Supersession requires an explicit correction/restatement/
clarification, positive revision number, and scoped corrected predicates and
periods where known.

## Scoped authority

`AuthorityAssessment` records a source and optional document version against a
specific authority domain, subject, jurisdiction, predicate, period/effective
interval and statement basis. It retains source role, authenticity basis,
limitations, policy ID/version and assessment time. Its result is exactly
`APPLICABLE`, `NOT_APPLICABLE` or `UNKNOWN`; there is no universal trust score.

## Proposition, assertion and admission

`PropositionKey` describes the question before comparing values: subject,
predicate and version, qualifiers/negation, unit/currency, reporting/effective
period, consolidation, segment, accounting and statement basis, adjustment,
measure type/role, and optional horizon/target interval.

`AssertionIdentity` binds a typed scalar, interval, direction or explicit
missing value to that proposition, evidence occurrence IDs, epistemic role,
derivation role and retained original claim IDs. `AdmissionIdentity` records
which assertion entered which run/capture under which as-of, projection policy,
comparison policy and source mapping. Zero remains a value; it is never treated
as missing.

The projection also retains `FACT`, `INFERENCE`, `HYPOTHESIS` separately from
`REPORTED`, `PROVIDER_DERIVED`, `TI_DERIVED`. A provider-derived value cannot be
relabelled as an observed reported fact without an explicit mapping rule.

## Comparability and disputes

`compare_assertions` produces one of:

- `EXACT`;
- `COMPARABLE_WITH_TRANSFORM`, only through an explicit versioned unit rule and
  tolerance;
- `NOT_COMPARABLE` for known semantic/scope mismatch;
- `UNDETERMINED` when required meaning is unknown.

Unknown is not a wildcard. Same label or same numeric value is not enough.
Revenue from operations does not collapse into total income; standalone does
not collapse into consolidated. Conflict is evaluated only after comparability.

The dispute taxonomy is `FACTUAL_CONFLICT`, `SEMANTIC_MISMATCH`,
`TEMPORAL_DIFFERENCE`, `SCOPE_MISMATCH`, `INTERPRETIVE_DISAGREEMENT`,
`CROSS_DOMAIN_TENSION`, `FORECAST_DISAGREEMENT` and
`CONFIRMATION_DISCREPANCY`. A dispute begins at `DETECTED`, may enter
`UNDER_REVIEW`, and ends only in a typed terminal state with cited evidence.
History is tuple-backed and append-only; terminal events cannot be extended.

## Independence

Independence is pair- and dimension-scoped across publication lineage,
measurement origin and analytical derivation. Relations are `SAME_ROOT`,
`DERIVED_FROM`, `LIKELY_DEPENDENT`, `INDEPENDENT` or `UNKNOWN`.

An independent relation requires two explicit non-provider basis identities and
positive basis. Different provider names alone are insufficient. Two analyses
may be analytically independent while retaining the same measurement root.
Independence is not inferred transitively, and cyclic derivation is rejected.

## Field-level confirmation projection

`ConfirmationProjection` preserves the original confirmation ID, recorded
status and semantic fingerprint. Each requested field gets its own discovered
and authoritative assertions, comparisons, scoped authority assessments,
candidate document versions, admissibility and unresolved gaps.

All requested fields and all candidate documents that supplied a field must be
represented. Predicate and authority scope cannot leak across fields. Document
order never selects a winner. Equal-ranked conflicts remain conflicts;
`NOT_FOUND` remains an absence state and never becomes `FALSE`.

## A4 semantic input projection

`A4SemanticInputProjection` is a deterministic, immutable input product. It
contains:

- schema/policy/run/as-of/correlation/authority/profile/budget/model controls;
- exact frozen A3.10, A3.8, A3.9 and A2 parent references;
- unchanged A3.9 state, reasons, gaps, opinions and A2 baseline view;
- typed source, provider, origin, document, occurrence, assertion and admission
  indexes;
- authority, comparison, dispute, independence, epistemic and confirmation
  views;
- quality/freshness/directness/completeness, required/optional gaps and excluded
  evidence;
- referenced artifact digests and explicit usage/cost knowledge;
- a deterministic semantic fingerprint.

The build validates the complete A3.10 package and recorded A3.8/A3.9 children.
Its mandatory `a3-package`, `a2-capture`, `a38-capture` and `a39-capture`
digests must exactly match the frozen parent. Projection-only A2 captures cannot
support claims that require full A2 assertion evidence. Optional absence is a
typed gap. No A2 feature or A3 opinion is recalculated.

There is deliberately no A4 finding, thesis, vote, score, disposition or
recommendation in this schema.

## Capture, replay and policy comparison

`FoundationCapture` stores canonical build-input and projection JSON, byte
checksums, projection semantic fingerprint, capture identity and exact capture
checksum. Recorded replay validates all checksums and parent captures, rebuilds
from captured bytes, and requires exact model equality. It has no live fallback.

Changing projection policy creates a new projection and an explicit
`ProjectionPolicyComparison`; it is not called exact replay. Existing A3.10
schemas, serialized fixtures, fingerprints and child hashes are not upgraded or
rewritten.

## Successor semantics

Later governed evidence creates a successor input with a later `evidence_as_of`,
the exact parent projection and parent cutoff, and explicit new evidence IDs.
Each new ID must resolve to a captured occurrence available by the new cutoff.
The original projection remains immutable and its evidence is never backdated.
The foundation does not implement an A4 research request or live-planner bridge.

## Security and authority

Canonical contracts contain no credentials, raw provider payload or arbitrary
URL identity. Captured source text is data, never instructions. Replay has no
provider/model/network path and grants no new application, broker or execution
authority. The package remains at project version `0.1.0`; this new projection
and capture family has its separate contract schema version `1.0`.

## Next boundary

This milestone satisfies the semantic projection prerequisite for future A4.
The selected sequence still places the separately governed narrow local
facade/lifecycle before deterministic A4 runtime. A4 implementation requires a
new authorization and must consume this validated projection rather than mutate
frozen A2/A3 records.
