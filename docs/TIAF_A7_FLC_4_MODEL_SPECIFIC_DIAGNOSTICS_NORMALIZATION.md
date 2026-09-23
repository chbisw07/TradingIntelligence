# A7 / FLC-4 — Model-specific diagnostics normalization

Checkpoint: 2026-09-23, Asia/Kolkata. **FLC4_ACCEPTED**. This is an additive,
internal research capability. It does not reopen FF-0/FF-1, evaluate a model,
fit or calibrate anything, or grant lifecycle authority.

## Scope and design

FLC-4 implements one common immutable diagnostic envelope and four separately
versioned, model-specific payloads:

```text
explicit DiagnosticRequest
        │ artifact-only; no outcome query or ambient clock
        ▼
DiagnosticEnvelope
        ├── BASE_RATE_SUPPORT
        │     └── BaseRateSupportDiagnostic
        ├── LOGISTIC_COEFFICIENTS
        │     └── LogisticCoefficientDiagnostic
        ├── LOGISTIC_LINEAR_CONTRIBUTIONS
        │     └── LogisticContributionDiagnostic
        └── LOGISTIC_PREPROCESSOR
              └── LogisticPreprocessorDiagnostic
```

The envelope normalizes identity, forecaster/artifact, subject/target, request,
status, schema, lineage, timestamp and limitations. It deliberately does not
flatten different forecasters into a giant optional-field object. The earlier
FLC-1 optional diagnostic seam remains the model-neutral interface declaration;
FLC-4 supplies the sealed, persisted research request/envelope and adapters.

The accepted forecaster descriptors remain byte-for-byte unchanged and therefore
do not advertise a new public/routable capability. The existing FLC-1 optional
diagnostic protocol remains the neutral seam; FLC-4 is its internal,
exact-artifact research implementation. No registry entry, mutable latest/active
alias, UI or monitoring endpoint was added.

## Request and authority boundary

`DiagnosticRequest` pins:

- request schema/identity and exact `ForecasterKey`;
- subject and target;
- source artifact and, for learned artifacts, model-identity reference;
- one typed diagnostic kind;
- optional recorded feature input for linear contributions;
- explicit evidence references and aware creation time.

Its fixed scope is `INTERNAL_RESEARCH`; its evidence policy is
`ARTIFACT_ONLY_NO_OUTCOME_QUERY`. Protected outcomes, consumed-holdout reuse,
fitting, calibration, evaluation and approval are all literal false. Extra
fields are rejected, including outcome, label and Ground Truth aliases. Naive
datetimes remain invalid and accepted datetimes serialize in the canonical
Asia/Kolkata timezone with `+05:30`.

Generated envelopes are fixed to `DESCRIPTIVE_ONLY`, lifecycle effect `NONE`,
optimization effect `NONE`, evaluation/calibration false, and approval,
promotion and activation false. Unsupported implementation versions and absent
artifacts return distinct sealed `UNSUPPORTED` or `UNAVAILABLE` envelopes.
Unknown kinds, incompatible forecasters, mismatched lineage and invalid inputs
fail explicitly rather than becoming a generic success or fabricated payload.

## BaseRate support diagnostic

The BaseRate adapter reads an immutable snapshot of the existing
`BaseRateArtifact`; it does not replace or rewrite that FF-0 artifact. It records:

- the exact 20 scheduled transition pairs and their positions;
- fit-knowledge cutoff and per-transition availability;
- included labels and original label-source references;
- excluded/unavailable positions and reasons;
- eligible, positive and zero counts;
- the unsmoothed `k / n` value only when all 20 positions are eligible;
- `LAST_SCHEDULED_TRANSITIONS_AT_FIT_CUTOFF` and `NO_BACKFILL` policy.

A missing or late label stays at its scheduled position. A later transition is
never substituted. Only data already present in the accepted pre-cutoff support
artifact is exposed; no post-outcome lookup occurs.

## Logistic diagnostics

Coefficient diagnostics preserve the exact feature order, standardized-space
coefficients and intercept in the recorded Logistic reconstruction. Their
declared meaning is `STANDARDIZED_FEATURE_LOG_ODDS_ASSOCIATION`. They contain no
importance/rank alias and no causal claim.

Preprocessor diagnostics preserve the exact scaler identity, feature order,
sample count, means, variances, scales, constant-column positions and scaler
configuration. This is recorded transformation metadata, not a data-quality or
model-quality verdict.

Contribution diagnostics require an explicit persisted, outcome-free feature
input. For each fixed-order feature they expose exactly:

```text
standardized_x_i = (raw_x_i - mean_i) / scale_i
contribution_i   = standardized_x_i * coefficient_i
logit            = intercept + sum(contribution_i)
raw_probability  = sigmoid(logit)
```

The probability is checked against the existing reconstruction function. It is
raw and uncalibrated; no probability changes occur. Contributions are local to
this linear model, depend on the recorded scaling, are not causal, can be hard
to interpret under correlated features, and are not trading reasons.

Both frozen FF-1 `LogisticArtifact` and the separately versioned FLC-3
`SyntheticModel` are read through their recorded `Reconstruction`; neither is
mutated. The test reference uses a hand-authored FLC-3-style synthetic artifact
and performs no fit.

## Diagnostics are not evaluation, lifecycle, calibration or optimization

| Concern | FLC-4 behavior |
| --- | --- |
| Evaluation | No Ground Truth read; no Brier, log-loss, accuracy, support/rejection or ranking |
| Lifecycle | No approval, promotion, activation or lifecycle transition |
| Calibration | Shows only recorded raw logit/probability; no fit, application or readiness verdict |
| Optimization | No trial objective, candidate selection or mutation of FLC-3 results |
| Trading | No target, probability forecast, confidence or trade-reason claim is invented |

Diagnostic limitations are schema-fixed namespaced codes, not optional prose.
The contracts reject attempts to reseal an envelope with authority or metric
fields. FLC-3 trial diagnostics remain owned by optimization; FLC-4 only explains
recorded model/support structure.

## Persistence, custody and replay

`DiagnosticStore` adds codecs to the existing `ForecasterStore`, which itself
uses the accepted content-addressed `ResearchForecastStore`. There is no second
database or registry. Requests, outcome-free inputs, source snapshots, typed
payloads and envelopes use canonical immutable JSON, content fingerprints,
exclusive creation and existing size/count/custody bounds.

```text
envelope reference
  ├── exact request
  ├── exact source/model artifact and learned model identity
  ├── BaseRate source snapshot OR recorded Logistic reconstruction
  ├── exact recorded input when contributions are requested
  └── exact typed payload
          ↓
offline regeneration → equality check → MATCH / MISMATCH
```

Replay is read-only. It requires no network, provider, broker, fitting,
prediction service, Ground Truth, Evaluation or current clock. Missing, corrupt
or tampered records return `MISMATCH`. A persisted unsupported/unavailable result
also replays exactly without fabricating a payload.

## Holdout and interpretation guards

The request and feature-input schemas make protected evidence, consumed-holdout
reuse and outcome-bearing inputs unrepresentable as true. Logistic diagnostics
operate on frozen model/scaler artifacts or an explicit recorded inference
vector only. BaseRate diagnostics operate on the already admitted support
artifact. Consequently FLC-4 cannot relabel consumed 2025 evidence as unseen,
query hidden labels or generate a same-experiment improvement signal.

The code imports no Evaluation, optimization, provider, broker, sklearn or
explainer library and contains no fit path. Coefficient magnitude is not named
importance; raw probability is not named confidence; diagnostic health is not
named model quality.

## Compatibility matrix

| Surface | Result |
| --- | --- |
| FF-0 BaseRate | Existing artifact/runtime unchanged; additive read-only support adapter |
| FF-1 Logistic | Frozen model/scaler/forecast/evaluation records unchanged; reconstruction read only |
| FLC-1 | Existing inference/identity/optional-diagnostic seams and descriptors unchanged |
| FLC-2 | Existing store/custody/lifecycle behavior unchanged; additive codec profile only |
| FLC-3 | Optimization/evaluation/selection unchanged; synthetic model can be diagnosed read only |
| FLC-4 | New internal request, envelope, four typed payloads, persistence and replay |

FF-1 remains `INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE`; BaseRate remains
BENCHMARK; Logistic remains CHALLENGER / EXPERIMENTAL and promotion-ineligible;
2025 remains CONSUMED; final-holdout executions remain one; post-holdout refit
remains forbidden.

## Tests and validation

Targeted tests cover request/envelope sealing and timezone normalization; exact
BaseRate counts/no-backfill/cutoff semantics; exact Logistic coefficients,
scaler and contribution arithmetic; schema separation; explicit statuses;
invalid kind/forecaster/input/lineage; holdout side channels; absence of metric,
calibration, optimization and lifecycle authority; canonical persistence;
offline replay and tamper mismatch; stable fingerprints and JSON arrays.

Validation commands:

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_diagnostics.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_optimization.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_lifecycle.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_seams.py --tb=short
.venv/bin/pytest -q tests/unit/forecasting/test_forecaster_seams.py tests/acceptance/ff0 tests/unit/forecasting/test_contracts.py tests/unit/forecasting/test_pinned_runtime_replay.py tests/unit/forecasting/test_identity_isolation.py tests/unit/forecasting/test_logistic_training.py tests/unit/forecasting/test_logistic_forecasts.py --tb=short
.venv/bin/pytest -q --tb=short
.venv/bin/python -m compileall -q src scripts
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src tests
git diff --check
```

Acceptance checkpoint:

- FLC-4 targeted: **31 passed**.
- FLC-3 regression: **60 passed**.
- FLC-2 regression: **55 passed**.
- FLC-1 seam regression: **27 passed**.
- FLC-1 / FF-0 / FF-1 compatibility: **251 passed in 234.36s**.
- Full repository suite: **3,618 passed in 1,072.29s (17:52)**.
- Compileall (`src scripts`), Ruff (`src tests scripts`), mypy (`src tests`;
  664 source files) and `git diff --check`: PASS.
- Documentation: **781 local links across 13 Markdown files**; all 11
  changed/new Markdown files have balanced fences.
- Protocol and captured final-ledger verification: MATCH; no holdout execution.
- Four canonical FF-1 protocol/execution/evaluation/ledger fingerprints: MATCH.
- All **72 source + 6 implementation pins = 78 frozen pins**: MATCH, zero
  mismatches.

## Files and deferrals

Created implementation: `src/tiaf/learning/forecaster_diagnostics.py`.
Created targeted tests: `tests/unit/forecasting/test_forecaster_diagnostics.py`.
No existing runtime Python source is modified. This report and active navigation
are updated; historical acceptance reports are unchanged.

Deferred beyond FLC-4: calibration composition/readiness, calibration fitting or
application, future model-family diagnostics, SHAP/permutation/counterfactual
explainers, statistical coefficient studies, public APIs/UI and production
monitoring.

Exact next task: **TIAF A7 / FLC-5 — CALIBRATION COMPOSITION READINESS**.
Recommended model: **GPT-6 Astra — High**.
