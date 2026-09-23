# A7 / FLC-6 — Reusable independent Evaluation normalization

**FLC6_ACCEPTED**

Checkpoint: 2026-09-23, Asia/Kolkata. Final validation complete.
This is an additive, internal Evaluation profile. It does not reopen FF-0/FF-1,
run the 2025 holdout again, create new empirical evidence, or start FF-2.

## Scope, owner and reuse

FLC-6 stays inside the existing `tiaf.evaluation` owner. It adds immutable
normalization contracts and a bounded synthetic adapter alongside the accepted
Ground Truth, population-disposition, Brier/log-loss, moving-block and research
store implementations:

```text
explicit request, population, participant and external truth identities
                           │
          supplied forecast sets + supplied journal labels
                           ▼
        existing Evaluation loss + moving-block implementations
                           │
          normalized metrics / paired rows / coverage evidence
                           ▼
        existing content-addressed store + offline recomputation
                           │
       evidence only — decision and lifecycle remain external
```

There is no evaluator #2, benchmark registry #2, Ground Truth writer, labeler,
database or public capability. `forecast_normalization.py` is an adapter/profile
within Evaluation: it delegates binary losses and the non-circular moving-block
sampler to `forecast_comparison_metrics.py` and storage to the existing
`ResearchForecastStore`. It does not replace or modify development/final FF-1
evaluation code. Fixed-width ECE is the one new metric calculation required by
FLC-6; it is versioned as diagnostic-only and never participates in a decision.

## Immutable evaluation identity and request

`EvaluationIdentity` binds:

- evaluation ID/version and aware creation time;
- subject and explicit universe;
- exact target/event/horizon/cutoff/output/label semantics;
- realization mode;
- population and split identities;
- Ground Truth identity;
- metric-set, comparison and statistical-policy identities;
- evaluation policy reference.

`EvaluationRequest` embeds the complete identities plus ordered participants,
population, external Ground Truth authority, pairing rule, metric set, statistical
policy, evidence-use declaration and external decision-policy reference. All are
sealed and fingerprinted before any result exists. The validator requires every
participant to have the same target, population, realization mode and cutoff
semantics and requires every nested fingerprint to equal the request identity.
No mutable registry lookup, latest alias, ambient clock or runtime default enters
identity.

Request authority fields are schema-fixed false for training, optimizer selection,
calibration fit/application, diagnostics, approval, promotion and activation.
Extra fields are forbidden. A request is therefore evidence-production input,
not permission to train or change lifecycle state.

## Participant identity and roles

One `EvaluationParticipant` contract supports:

- primitive forecaster;
- artifact-backed forecaster;
- calibrated composition;
- future composite.

It uses a forecast/composition reference, optional neutral `ForecasterKey`, target,
population, mode, cutoff and probability semantics. No trainer job, scaler
implementation, optimizer trial order or diagnostic internals are required.
Participant form is identity metadata, not dispatch to a hidden family-specific
evaluator. At most two participants are admitted by this bounded profile; FLC-6
does not build an N-way leaderboard.

`BENCHMARK`, `CHALLENGER` and `SUBJECT` are report labels only. The metric and
pairing algorithms iterate the declared participant order and never branch on
role or hard-code BaseRate/Logistic mathematics.

## Population identity, pairing and absence

`EvaluationPopulation` makes the intended denominator first-class: population
ID/version, subject/universe, window, ordered observation IDs, eligibility and
exclusion policies, split, protection state, coverage policy and completeness.
Duplicate observations/universe members and invalid windows are rejected.
Changing membership creates a different population fingerprint; results cannot
silently narrow or broaden it.

`PairingIdentity` supports explicit `SINGLE_PARTICIPANT` and
`PAIRED_COMPARISON`. Paired comparison requires exactly two unique ordered
participants and exact observation-ID joining under an explicit retained-
denominator absence policy. The complete request validation also enforces the
same target, subject/population, mode, cutoff, Ground Truth, window/split, metric
set and statistical policy. Mismatched aggregates are never treated as paired
evidence. Single-participant evaluation produces no fake pair table or paired
statistics.

Every population observation has one explicit forecast row per participant and
one Ground Truth row. Missing/failed/unsupported forecasts and missing/ineligible/
ambiguous truth carry a reason and no numeric value. The original ordered grid is
retained for moving-block sampling. Only the exact eligible intersection is
scored; every other row remains `NOT_EVALUABLE` with all causes. No row silently
disappears.

`KnownCount` distinguishes `KNOWN(value)` from `UNKNOWN(None)`: unknown is never
encoded as zero. `CoverageAccounting` reports requested observations, each
participant's availability, Ground Truth availability, paired eligibility,
evaluated rows, protected exclusions, consumed exclusions, reasons and coverage.
It recomputes these counts from dispositions and rejects a resealed mismatch.
The executable synthetic profile reports protected/consumed exclusions as known
zero because such evidence is rejected at request admission; the historical
legacy view reports consumed state separately.

## Ground Truth ownership

`GroundTruthIdentity` pins the external Outcome Journal, target/label version and
resolution policy. `GroundTruthSet` contains externally supplied immutable journal
entry references and labels. It has no endpoint price fields and the evaluator
imports no labeler. Available labels require a journal entry reference; absent
truth cannot carry a numeric label. FLC-6 does not compare prices, refresh a label
vintage, query a provider or reconstruct target truth.

This preserves the existing one-owner rule: Outcome Journal authority supplies
truth, while Evaluation joins and measures it. Forecast/composition identity and
Ground Truth identity remain separate until the evaluation request links them.

## Metric-set and statistical identities

The synthetic `MetricSetIdentity` demonstrates four independently typed metrics:

| Metric | Tier | Direction / meaning |
| --- | --- | --- |
| Brier | `PRIMARY` | Lower is better; exact existing squared-probability loss |
| Natural log loss | `SECONDARY_DESCRIPTIVE` | Lower is better; existing `1e-15` metric-only clipping |
| Threshold accuracy | `SECONDARY_DESCRIPTIVE` | Higher is better; `p >= 0.5`, ties positive |
| Fixed-width ECE | `DIAGNOSTIC_ONLY` | Descriptive reliability; 10 bins, final bin closed, empty bins contribute nothing |

Each definition pins its version, tier, denominator, direction and numeric-policy
reference. Result rows copy the declared tier. No diagnostic can silently become
a support criterion, and the evaluator emits no scientific classification at all.
Metric-set contracts are not hard-coded to FF-1 participant identities.

`StatisticalPolicy` fingerprints the paired non-circular moving-block method,
block length 5, 5,000 replicates, seed 1729, 97.5% two-sided percentile interval,
quantiles, minimum support, population order, terminal-block handling and
zero-pair behavior. These match the accepted FF-1 sampling kernel. FLC-6 calls
that existing kernel over the retained ordered grid and shared paired mask; it
does not choose a method after seeing results. Short grids and non-estimable
samples remain explicit absence, not zero-width confidence or PASS.

Paired differences use the accepted sign convention:

```text
d_i = loss(second participant, y_i) - loss(first participant, y_i)
```

The summary is `EVIDENCE_ONLY_NO_DECISION`. A lower interval or apparent
improvement grants no support, promotion or activation.

## Result, coverage and authority boundaries

`NormalizedEvaluationResult` preserves exact request/input references,
population and Ground Truth fingerprints, coverage/dispositions, metric bundle,
optional pair table, statistical summary, limitations and aware creation time.
Its internal validators require the complete participant-by-metric grid, ordered
participant availability, exact population dispositions and exact paired identity.

Statuses are:

| Condition | Representation |
| --- | --- |
| Valid request with declared minimum support | `GENERATED` evidence |
| Valid request below minimum support | `INSUFFICIENT_SUPPORT`; metrics may be descriptive but no sufficiency claim |
| Missing forecast or Ground Truth | Explicit `NOT_EVALUABLE` disposition and reason |
| Unsupported metric | Explicit exception; no fabricated metric |
| Invalid target/population/mode/pairing | Request rejection |
| Short/non-estimable paired grid | `NOT_ESTIMABLE`, absent intervals |
| Replay/tamper mismatch | `MISMATCH` |
| Consumed-evidence execution/reclassification | Admission rejection |

The result fixes scientific decision ownership to `NOT_OWNED_BY_EVALUATOR` and
optimizer selection, approval, promotion and activation to false. It has no
lifecycle transition method. `decision_policy_ref` merely identifies an external
policy; FLC-6 does not execute it.

Training provides immutable forecast artifacts and is never invoked. FLC-3 may
consume evaluation evidence but search order, objective selection and optimizer
state are absent here. FLC-5 may supply a calibrated-composition participant, but
Evaluation neither fits nor applies a calibrator and never overwrites a raw
probability. FLC-4 diagnostics remain separate; no diagnostic input or verdict
can alter pairing or metrics. Static tests reject imports/calls across these
boundaries.

## Synthetic reference evaluation

The executable example is entirely authored engineering data: five ordered
observations, two supplied forecast sets and one supplied external synthetic
journal. It performs no primitive inference and claims no empirical performance.

```text
labels       = [0,   1,   0,   1,   0]
benchmark p  = [0.5, 0.5, 0.5, 0.5, 0.5]
challenger p = [0.1, 0.9, 0.2, 0.8, 0.3]
```

Hand-checkable outputs:

| Result | Benchmark | Challenger |
| --- | ---: | ---: |
| Brier | 0.250 | 0.038 |
| Accuracy (`p >= 0.5`) | 0.4 | 1.0 |
| Fixed-10-bin ECE | 0.1 | 0.18 |

The log loss is also checked against direct `-log(p_y)` arithmetic in tests.
These values are illustrative and deliberately are not acceptance thresholds,
scientific support, calibration qualification or evidence that one production
forecaster is better.

## Persistence and offline replay

`NormalizedEvaluationStore` is only a codec profile on the existing bounded,
content-addressed `ResearchForecastStore`. Population, request, captured input,
pair table, metric bundle, statistical summary, result and ledger are separately
sealed and persisted. Existing canonical JSON, record-size/corpus bounds,
exclusive creation, no-overwrite and read-only behavior remain authoritative.

```text
normalized ledger
  ├── exact population and request
  ├── exact supplied forecast/truth input
  ├── paired table (paired mode only)
  ├── metric bundle
  ├── statistical summary
  └── result
          │ resolve all children under recorded policies
          ▼
     reconstruct join, losses, coverage and moving-block evidence
          ▼
                    MATCH / MISMATCH
```

Replay is read-only and recomputes only from captured synthetic rows and policies.
It performs no model inference, training, optimization, calibration, diagnostics,
provider, broker or network operation and makes no write. Changed metrics,
lineage, missing children or corrupt canonical records return `MISMATCH`.

## FF-1 read-only adaptation and consumed-evidence guard

`adapt_legacy_ff1_final` accepts the exact typed protocol, execution, evaluation
and ledger records and projects only their recorded identities and conclusion.
It does **not** read raw outcome data, reconstruct pairs, rerun scoring, invoke the
final verifier, or generate a normalized result that would pretend the old
population was newly evaluated.

The view preserves:

- original protocol/execution/evaluation/ledger fingerprints;
- paired-population, Ground Truth and metric-policy fingerprints;
- `INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE`;
- BaseRate `BENCHMARK` and Logistic `CHALLENGER / EXPERIMENTAL`;
- holdout `HISTORICAL_ACCEPTED_CONSUMED`, execution count 1;
- post-holdout refit false, automatic promotion false;
- no reclassification as unseen and no evaluation re-execution.

`EvidenceUseDeclaration` machine-enforces evidence state. Consumed FF-1 evidence
in the original experiment is `HISTORICAL_REPLAY_ONLY`; in a different/new
experiment it is `DEVELOPMENT_KNOWN`. Both forbid evaluation execution and cannot
claim unseen/protected status. Only the compiled authored synthetic reference is
executable in FLC-6. Renaming an evidence or experiment ID does not renew it.

This allows historical accepted evidence to remain inspectable/replayable while
preventing another one-shot path or a recycled pristine holdout.

## Compatibility and preservation

| Layer | FLC-6 treatment |
| --- | --- |
| FF-0 BaseRate | Existing target/truth/contracts, evaluation acceptance and pinned replay unchanged |
| FF-1 development/final | Existing evaluator, metric formulas, sampler, decisions, stores and artifacts unchanged |
| FLC-1 inference | Forecast identity/output consumed; predictor never asked to fit or fetch |
| FLC-2 training/custody/lifecycle | Immutable artifacts/custody remain inputs; no training or transition |
| FLC-3 optimization | May consume evidence later; evaluator does not select or mutate trials |
| FLC-4 diagnostics | Separate descriptive owner; no metric/pairing influence |
| FLC-5 calibration | Composition may be a participant; no calibration execution or raw overwrite |
| FLC-6 | Additive contracts, synthetic adapter, existing-store codecs, replay and read-only legacy view |

Frozen FF-1 remains `INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE`; BaseRate
is BENCHMARK, Logistic CHALLENGER / EXPERIMENTAL, promotion eligibility NO, 2025
CONSUMED, execution count 1 and post-holdout refit forbidden.

Hash-only preservation audit, without final evaluation execution:

| Canonical record | Fingerprint — expected MATCH |
| --- | --- |
| Protocol | `2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814` |
| Execution | `2948bc46874f8196c535720bd4f7882f6293fc96077acb563e2e11409c3e4840` |
| Evaluation | `8c0556e7b88284c170db57d745de7ece707d365ab52a585db5ebb0d3e81a7d0e` |
| Ledger | `630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583` |

All **72 source + 6 implementation pins = 78/78 MATCH** in a hash-only audit;
no evaluation was executed by that audit.
No existing runtime Python source, FF-0/FF-1 artifact, outcome data or frozen
policy is edited by FLC-6.

## Validation

Commands:

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_evaluation_normalization.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_evaluation_normalization.py tests/unit/forecasting/test_calibration.py tests/unit/forecasting/test_forecaster_diagnostics.py tests/unit/forecasting/test_optimization.py tests/unit/forecasting/test_forecaster_lifecycle.py tests/unit/forecasting/test_forecaster_seams.py --tb=short
.venv/bin/pytest -q tests/unit/evaluation --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_seams.py tests/acceptance/ff0 tests/unit/forecasting/test_contracts.py tests/unit/forecasting/test_pinned_runtime_replay.py tests/unit/forecasting/test_identity_isolation.py tests/unit/forecasting/test_logistic_training.py tests/unit/forecasting/test_logistic_forecasts.py --tb=short
.venv/bin/pytest -q --tb=short
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
.venv/bin/python -c 'from docs.handbooks.a7_forecasting.validate_handbook import validate_links; print(validate_links(True))'
git diff --check
```

Current results:

- FLC-6 targeted: **49 passed**; prior FLC-1…5: **231 passed**;
  combined FLC regression: **280 passed in 194.33s**.
- Existing Evaluation regression: **218 passed in 293.96s**.
- FLC-1 / FF-0 / FF-1 compatibility: **251 passed in 257.90s**.
- Full repository suite: **3,725 passed in 1,114.73s (0:18:34)**.
- Compileall (`src scripts`), Ruff (`src tests scripts`) and mypy (`src tests`;
  **670 source files**): PASS.
- Documentation: **807 local links across 13 Markdown files**: PASS.
- Four canonical FF-1 fingerprints and **78/78 frozen pins**: MATCH.
- `git diff --check`, Markdown fence balance and new-file whitespace checks:
  PASS.

Targeted coverage includes identities/fingerprints, participant forms, exact
population/pairing, external truth, toy metrics/ECE, metric tiers, deterministic
moving-block policy, missingness and unknown counts, single participant, target/
population/mode rejection, authority separation, consumed evidence, persistence,
replay/tamper, read-only legacy mapping, timezone/JSON and cross-owner import/call
guards. No empirical evaluation was run.

## Files, deferrals and handoff

Created:

- `src/tiaf/evaluation/forecast_normalization_contracts.py`
- `src/tiaf/evaluation/forecast_normalization.py`
- `tests/unit/forecasting/test_evaluation_normalization.py`
- this report.

Modified only active navigation: `README.md`, `docs/ARCHITECTURE.md`,
`docs/IMPLEMENTATION_ROADMAP.md`, `docs/MILESTONES.md`,
`docs/TIAF_IMPLEMENTATION_TARGETS.md`, `docs/TRADINGINTELLIGENCE_ROADMAP.md`,
`docs/TIAF_A7_DETAILED_ROADMAP.md`,
`docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md`,
`docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md` and
`docs/TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md`.

Deferred: arbitrary metric plugins, N-way leaderboard/ranking, empirical
calibration evaluation, new uncertainty methods/thresholds, new outcome sources,
general family/composite execution, lifecycle decisions, public runtime exposure
and FF-2. FLC-7 still owns cross-seam integration, provenance and adversarial
replay hardening. FLC-8 owns final closure/acceptance.

Acceptance blockers: **none**.

Next only after acceptance and a separate request:
**TIAF A7 / FLC-7 — INTEGRATION, PROVENANCE AND REPLAY HARDENING**.
Requested handoff model: **GPT-6 Astra — High**.
Suggested commit after acceptance:
`feat(a7.flc6): normalize reusable independent evaluation`.
No commit, tag or push is performed by this task. No tag is proposed.
