# TIAF_A2.10 — Replay, Validation, and Baseline Evaluation

## Status and purpose

**Status: COMPLETE / LIVE VALIDATED at tag `tiaf-a2.10`.**

A2.10 preserves the accepted A2.9 deterministic benchmark as an auditable
decision-time record. It persists normalized evidence, replays it without a
provider or network, compares policies over identical evidence, attaches later
factual price paths, calculates descriptive excursions, preserves original
batch ranks, and detects deterministic regressions.

A2.10 does not optimize policy 1.0, reconstruct arbitrary historical knowledge,
simulate execution, calculate P&L, or introduce Agents.

## Absolute three-object boundary

```text
EvidenceSnapshot at decision time
              |
              v
immutable BaselineRunRecord
              |
              v
later OutcomePath / BaselineOutcome
```

Outcome objects reference the frozen run and fingerprint. They are never fields
of `EvidenceSnapshot`, `DeterministicBaselineRequest`, or
`OpportunityAssessment`. Replay consumes only the snapshot and an exact policy.

## Evidence snapshot

`EvidenceSnapshot` contains the complete normalized
`DeterministicBaselineRequest`: primary feature bundle, optional indicators,
explicit-benchmark relative bundle, multi-timeframe context and bundle,
optional derivatives bundle, decision-time quality/freshness, timestamps,
source evidence IDs, horizon, style, and requested timeframe order. It also
retains normalized context references and explicit benchmark identity.

Full provider `AnalysisContext` bar histories are not duplicated because A2.9
does not consume them during synthesis. The actual derived evidence required by
every policy selector is embedded, so replay requires no provider ID lookup.
Snapshots prohibit obvious credential, token, authorization, client/account,
password, and secret-bearing keys recursively. Raw HTTP payloads are absent.

All contracts are frozen, collections use tuples, JSON emits ordinary arrays,
and every datetime uses canonical aware `Asia/Kolkata` representation.

## Semantic fingerprint and identity

The fingerprint is lowercase SHA-256 over UTF-8 canonical JSON using sorted
object keys and compact separators. The semantic payload contains:

- fingerprint-schema version;
- producer ID/version;
- policy ID/version;
- explicit benchmark identity;
- canonical normalized context references; and
- the complete decision request and embedded evidence.

`snapshot_created_at` and snapshot archive metadata are excluded because they
describe persistence rather than what was known at decision time. Evidence
`as_of`, source-observation times, bundle creation times, `requested_at`,
quality, freshness, warnings, and provenance remain fingerprinted. Snapshot ID
is UUIDv5 over the fingerprint. Deserialization recomputes and verifies both.

The only accepted A2.9 adjustments are reproducibility fixes: the
`evidence_freshness` source map is canonicalized by source, and assessment UUID
input uses sorted-key canonical request/policy JSON. Reordering semantically
unordered freshness entries or metadata keys can no longer change an assessment
ID. No evidence value, freshness value, or scoring semantic changed.

## Decision run record

`BaselineRunRecord` stores the assessment separately with its snapshot ID and
fingerprint, producer identity, policy, direction, class, opportunity and
component scores, quality, reasons, warnings, decision time, and optional
original ranking context. Its duplicated projection is validated against the
embedded immutable assessment. Later outcomes never update this object.

Producer version is the TIAF package version (`0.1.0` for this milestone), while
baseline policy version remains the separate `1.0` decision-policy identity.

`CapturedBaselineCase` is only a portable file envelope containing the separate
snapshot and run objects with link validation.

## Offline replay

`replay(ReplayRequest)` verifies snapshot integrity and exact policy ID,
version, and style, then gives the embedded decision request to
`BaselineEngine`. It imports no provider, resolver, HTTP client, broker,
execution layer, Agent, LLM, strategy selector, or wall clock. `replay_time`
describes the replay artifact and cannot affect decision-time freshness or the
assessment.

When an expected assessment is supplied, comparison is exact across the full
JSON model. Identical inputs reproduce the same assessment and assessment ID.
Failures report deterministic leaf paths with expected and actual JSON values.

## Policy comparison

`compare_policies` evaluates two explicitly supplied policies over the same
snapshot evidence. Only the request's policy-version selector is copied for the
hypothetical run; evidence remains byte-unchanged. Output retains both complete
assessments, direction/class/score changes, all 11 component deltas, and added
or removed reasons. An alternate test policy is not treated as superior or
registered as production policy.

## Subsequent outcome and excursion formulas

`OutcomeWindow`, ordered `OutcomeObservation` bars, and `OutcomePath` are
provider-neutral later facts. The window cannot start before `decision_at`.
`assessment_reference_price` is an explicit factual reference, never an
execution fill.

For reference price `R`, ending close `C`, maximum future high `H`, and minimum
future low `L`:

```text
ending_return_percent = 100 * (C/R - 1)
upside_excursion      = max(0, 100 * (H/R - 1))
downside_excursion    = min(0, 100 * (L/R - 1))
realized_range        = 100 * (H - L) / R

POSITIVE: MFE = upside_excursion;    MAE = downside_excursion
NEGATIVE: MFE = -downside_excursion; MAE = -upside_excursion
```

Thus MFE is non-negative and MAE non-positive. `NEUTRAL`, `CONFLICTED`, and
every `NO_TRADE` assessment retain raw ending/upside/downside/range facts but
have no directional MFE/MAE. There is no brokerage, position size, fill, P&L,
win rate, profit factor, Sharpe, or CAGR.

## Frozen-ranking evaluation and aggregates

`RankingEvaluation` associates one outcome with every originally retained
assessment. It preserves original rank, class, and eligibility and never
re-sorts by hindsight. It reports descriptive averages for original top-1,
top-N, all eligible candidates, and the separate `NO_TRADE` population.
Corpus-level `EvaluationMetrics` counts directions, classes, quality, replay
passes/failures, and observed return/MFE/MAE averages. These are observations,
not causal alpha claims.

## Corpus and regression harness

`ReplayCorpusStore` provides content-addressed snapshot JSON plus append-only
`decision_records.jsonl` and `outcome_records.jsonl`. Existing decision or
outcome IDs cannot be overwritten. The regression harness loads captured cases,
resolves exact policy versions, replays in stable run-ID order, and emits
`PASS` or `FAIL`. Failures include snapshot/run ID, policy ID/version,
fingerprint, and leaf-level differences.

Synthetic golden coverage under `tests/fixtures/evaluation/` freezes all four
directions, all four classes, partial, missing optional and stale evidence,
ranking, and all-`NO_TRADE` behavior. The checked-in
`golden_manifest.json` is a **golden test manifest**, not a runnable replay
corpus: pytest reads the profiles and constructs stable synthetic cases
programmatically. Live transient provider data is not a golden fixture.

A runnable replay corpus is instead a directory with persisted records in this
conceptual layout:

```text
corpus/
  snapshots/
    <snapshot-id>.json
  decision_records.jsonl
  outcome_records.jsonl   # optional
```

`--corpus` searches `decision_records.jsonl` for persisted decision/run records
and resolves their content-addressed evidence from `snapshots/`. It does not
consume the synthetic golden manifest directly.

## User workflows

Capture once with provider access:

```bash
python scripts/capture_baseline_snapshot.py \
  --symbol RELIANCE \
  --horizon POSITIONAL \
  --benchmark NIFTY \
  --timeframes 1d,1h,15m \
  --output /tmp/reliance_a210.json
```

Then disable provider/network access and replay the portable capture:

```bash
python scripts/replay_baseline_snapshot.py \
  --input /tmp/reliance_a210.json
```

Run one or more captures as a regression corpus:

```bash
python scripts/run_baseline_regression.py \
  --input /tmp/reliance_a210.json
```

The validation workflows deliberately remain distinct:

1. **Synthetic golden tests** use pytest and stable, programmatically
   constructed fixtures. They validate deterministic behavior:

   ```bash
   .venv/bin/pytest -q \
     tests/unit/evaluation/test_regression_store_architecture.py \
     -k golden
   ```

2. **Captured snapshot regression** uses `--input` with a portable persisted
   snapshot/run file. It validates real persisted replay of one capture (or
   several files when `--input` is repeated).

3. **Replay corpus regression** uses `--corpus` with a directory containing
   persisted snapshots and decision/run records. It validates a collection of
   persisted runs.

Passing `tests/fixtures/evaluation/golden_manifest.json` to `--corpus` is
therefore invalid: the path is a test manifest file, not a persisted corpus
directory.

Replay and regression scripts contain no provider/resolver imports. Capture is
the only live script and remains read-only.

## Live validation record

On 2026-09-07, the capture CLI acquired normalized RELIANCE evidence with an
explicit NIFTY benchmark and ordered `1d,1h,15m` timeframes. Policy
`tiaf-a2.9-positional` version `1.0` produced `NEUTRAL`, opportunity
`24.509451`, and `NO_TRADE`. The snapshot fingerprint was
`b82a78d7530b5369f71bf764d8a9648f5df5e4650afc13182a7257f78824d763`.

With Dhan credential environment variables removed, offline replay reproduced
assessment ID `2fc0342a-5908-546a-98ae-768e7619a759` and the complete assessment
exactly. The standalone regression CLI reported `PASS 1 / FAIL 0` over the same
portable capture.

The first live replay had reproduced scores/class/direction but exposed a
different assessment UUID after sorted-key file serialization. Root cause was
A2.9 UUID input using insertion-ordered JSON metadata. Assessment identity now
uses canonical sorted-key JSON, with a regression protecting this exact
serialization round trip. No policy or assessment arithmetic changed.

## Historical reconstruction boundary and security

Replaying captured knowledge is not the same as reconstructing what would have
been available on an arbitrary historical date. The latter requires
point-in-time instrument universes, corporate actions, data-vintage semantics,
and availability timestamps. A2.10 does not fabricate that fidelity.

Snapshots must be treated as immutable audit artifacts. Although they contain
no configured credentials, market-data licensing and retention obligations are
deployment concerns.

## Deferrals and limitations

- DEF-049: exact arbitrary historical point-in-time reconstruction.
- DEF-050: persistent database and distributed/large-scale replay farm.
- DEF-051: scheduled provider-backed subsequent-outcome acquisition.

Statistical policy optimization remains DEF-024. Agent/human comparison awaits
their producer implementations and existing later-layer boundaries. A2.10 only
executes `DETERMINISTIC_BASELINE`, though producer identity contracts reserve
future stable enum values.

A2.10 is the final accepted A2 sub-milestone. The separate A2 major closure and
deferral burn-down are recorded in `TIAF_A2_FOUNDATION_BASELINE.md`,
`TIAF_A2_ACCEPTANCE_REPORT.md`, and `TIAF_DEFERRAL_REGISTER.md`.
