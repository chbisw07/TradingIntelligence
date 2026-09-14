# FM / LFDE — Detailed Research and Delivery Roadmap

**2026-09-15 (Asia/Kolkata): ADVANCED FMLFDEForecaster FAMILY / DRAFT / NOT_IMPLEMENTED.**
This is a gated research roadmap, not permission to start coding, acquire data,
train models, run providers or publish forecasts. FM is Forecasting Module;
LFDE is Latent Factor Discovery Engine. A6 stays frozen. The existing A7 design
is [ARCHITECTURE ACCEPTED](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md), its thesis
reconciled, implementation NOT_STARTED and runtime NOT_IMPLEMENTED. See the [integration record](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md).
The [FF platform roadmap](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) owns the
shared forecaster/benchmark/composition program. This nested roadmap retains
the ambitious advanced family's scientific gates; it is not the top-level
definition of forecasting and does not block a useful simpler FF miniature.

Authorities: [architecture](TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md),
[research reconciliation](TIAF_FM_LFDE_RESEARCH_RECONCILIATION.md),
[decision](TIAF_FM_LFDE_DECISION_RECORD.md),
[current forward queue](IMPLEMENTATION_ROADMAP.md).
FM-0–FM-6 are **local design-stage labels**, not accepted A7.x milestone numbers,
new facade operations, commitments to all seven implementations or new DEF IDs.

## 1. Before any implementation

```text
FM/LFDE architecture + advanced thesis — created; family now positioned in FF
  → FF platform architecture ACCEPTED; thesis RECONCILED
  → A7 FF integration RECONCILED
  → A7 ARCHITECTURE ACCEPTED
  → A7 IMPLEMENTATION SEQUENCING / FF-0 MINIATURE REALIZATION PLAN [NEXT]
  → separately authorized bounded scientific-control implementation
  → qualified data + preregistered experiment profile
  → candidate experiments, only as their gates are met
```

The [integrated A7 roadmap](TIAF_A7_DETAILED_ROADMAP.md) uses FF-0…FF-7 inside
A7, superseding the historical five-slice proposal. This nested family program
belongs to optional FF-5 after common FF-2 science/lifecycle; FF-3 is needed only
for ensemble use and FF-4 is never prerequisite. FM-0 reuses common infrastructure.
All scientific stages and gates below are unchanged; no automatic scope expansion.
A8/A9/A10 major ordering and TM/Scanner/Monitoring ownership remain unchanged.

### Common entry package for empirical work

| Prerequisite | Required evidence |
|---|---|
| Authorization | Named scope owner, exact allowed offline operations, finite trial/compute/storage/egress budget; no activation grant |
| Target | One explicit subject class, horizon/session schedule, endpoint/price basis, label version and abstention policy |
| Data | Rights/retention, qualified source availability and revision vintages, dated universe, action/calendar coverage; unknown historical fidelity labeled |
| Splits | Chronological fit/selection/calibration/test manifests, label maturity and overlap purge/embargo rules, final untouched test |
| Scientific profile | Primary/secondary metrics, usefulness and noninferiority margins, grouped interval method, support floors, missingness/population accounting and stop rules |
| Controls | Same target/population, base rate, simple explicit logistic model, deterministic A2/A4/A5/A6 records preserved |
| Reproducibility | Canonical captured inputs, environment/package and serializer pins, fit/seed/trial manifests, exact recorded replay and pinned-verifier policy |
| Cost | Resource ceilings chosen before fitting; actual local compute/latency/memory measurements; monetary unknowns explicit |

Unqualified data can support **synthetic contract testing** but not empirical
PIT or model-readiness claims. Deferred corporate-action/calendar/historical
coverage is not solved by importing an ML package.

## 2. Stage map

| Stage | Scope | Gate to enter | Exit evidence / stop alternative |
|---|---|---|---|
| FM-0 Scientific Control | Exact target, PIT features, logistic/base-rate controls, held-out calibration, journal, walk-forward, replay | Later accepted integration plan + common entry package | Reproducible end-to-end control, population accounting and honest scorecard; no lift required merely to prove mechanics |
| FM-1 Explicit Market State | Typed K factors, quality/uncertainty, deterministic fusion, limited qualified context | FM-0 controls trustworthy | Factor-family attribution and paired ablation; reject unnecessary new factors |
| FM-2 LFDE v1 | Tensor/masks, PCA and selected dynamic/probabilistic control, one masked temporal encoder | Qualified tensor, finite representation budget, stable K comparator | K/Z/K+Z out-of-sample, stability, calibration, cost and replay report; LFDE may be rejected |
| FM-3 State Dynamics | Persistence/linear state-space control; optional bounded regime model | Stable state contract and enough independent temporal support; not necessarily learned-Z success | Dynamics versus same-state direct-head gain; otherwise keep direct head |
| FM-4 Multi-head Forecasting | One additional target at a time: volatility or endpoint return distribution | Independently qualified new labels/data/calibration | Per-head proper-score/support/abstention evidence; no inferred joint paths |
| FM-5 Multimodal / Graph Extensions | Narrative embeddings or dated graph relations, then limited learned fusion if earned | Numeric controls stable, sources/edges PIT-qualified, one modality hypothesis | Retrained group/route ablation, missing-modality robustness, resource and lineage proof; drop weak modality |
| FM-6 Governed Ensemble / Correction Expansion | Static combination before learned routing; bounded candidate generation and promotion reports | Independently qualified members, compatible targets, mature outcome/evaluation/shadow process | Incremental ensemble/correction value and unchanged historical replay; explicit COLD approval only |

Later stages are **conditional options**. A usable K-only forecaster can survive
without LFDE, a learned representation without a dynamics layer, and a single
head without graphs, ensembles or path simulation. Failure at a stage does not
justify relaxing its metrics or hiding the control.

## 3. FM-0 — Scientific control, not a duplicate A7 pipeline

**Deliverables:** reuse the accepted FF miniature and shared A7 target/qualified schedule, captured
A2 feature snapshot, outcome journal, population report, chronological split,
logistic model, training-window base rate, separate sigmoid calibration,
registry/replay and promotion seams. The completed integration maps this reuse
to FF-0–FF-2 within A7, not the superseded five-slice queue. FM-0 is a reuse gate,
not a duplicate implementation. FF-5 can host local FM experiments once shared
FF-2 controls/governance are qualified; neither an LLM nor an ensemble is required.

**Tests:** naive timestamp rejection/Asia-Kolkata normalization; strict `>` tie
semantics; missing endpoint not false; cutoffs and label maturity; calendar
adjacency/revisions; unknown corporate actions; chronological leakage;
abstention/population denominators; JSON/fingerprint round trips; recorded replay
without model dependencies; missing pinned verifier; lower-layer preservation.

**Acceptance distinction:** synthetic tests can accept mechanics only. Real
forecast readiness requires qualified evidence, support, empirical gates and
explicit approval. A control can fail predictive usefulness while still proving
the evaluation machinery; publish that negative result rather than a forecast
service. No forced live call is part of this research pass.

## 4. FM-1 — Explicit market state

Begin with the existing qualified technical/market context allowlist, not all
factor families at once. Give each K member a formula owner/version, unit,
evidence paths, freshness, missingness and uncertainty kind. Sector/breadth,
derivatives, narrative and macro are separate optional admission groups.

Use deterministic typed fusion and small simple heads. Compare full K with
retrained group ablations on matched rows and report union coverage. Optional
fuzzy memberships require a separate bounded hypothesis and raw-factor control;
no large expert-rule inference engine. Reject changes that merely reproduce
A2 scores, add unqualified facts or make explanations less attributable.

Acceptance must show no A2 reparameterization/recalculation by the new consumer,
no probability invented from a score, and explicit state quality when a group
is absent. “Known factor” means a disclosed formula, not causal certainty.

## 5. FM-2 — LFDE v1 and subroadmap

### LFDE-specific gates

| Gate | Work / artifact | Required result |
|---|---|---|
| L0 Tensor qualification | One bounded resolution bundle, neutral ordered assets/channels, masks, availability/adjustment/scaler pins | Rebuild/fingerprint equality; missing vs zero/padding/artificial mask distinguished; no future fit data |
| L1 Classical controls | PCA first; PPCA or dynamic-factor variant only for a declared uncertainty/temporal question | K, Z-classical, K+Z-classical comparisons, finite dimension/search budget and declared uncertainty semantics |
| L2 One SSL encoder | Small temporal patch Transformer + masked reconstruction; train entirely inside eligible fit windows | Compatible latent snapshot/fit manifest, reproducible downstream comparison; reconstruction alone insufficient |
| L3 Stability and incremental value | Seeds/retraining, rank/dimension/anchor/probe tests, K redundancy, group ablations, cost | Paired proper-loss usefulness and calibration/stability limits met; otherwise reject/hold |
| L4 Optional extension | One alternative objective/family or narrative/graph experiment after review | New hypothesis, fresh eligible evaluation and budget; no automatic model-zoo expansion |
| L5 Optional latent-to-explicit proposal | Stable probe → economic hypothesis → independent deterministic factor formula | New untouched-data validation and explicit schema promotion; no automatic naming or A2 edit |

The first nonlinear encoder is **one** family. Plain/supervised autoencoders,
contrastive objectives and TCNs are later alternatives, not parallel mandatory
arms. Larger Transformers, selective SSMs and separate macro/derivative encoders
are deferred. The selected classical dynamic comparison can be shared with
FM-3; avoid duplicate implementations merely to fill the roadmap.

Important tests include asset-order perturbation, per-channel units and
train-only normalization, forbidden future SSL windows, training-only
label-conditioned latent paths, incompatible basis/head rejection, fixed-anchor
diagnostics, unavailable modality behavior and old snapshot replay after a new
encoder. Do not require raw coordinates from different fits to be equal.

## 6. FM-3 and FM-4 — Dynamics and additional targets

FM-3 distinguishes state estimation from state evolution. Start with persistence
or a small linear state-space model; a bounded HMM needs a regime hypothesis and
train-selected state count. Compare the complete dynamics-integrated head with
the same state/direct head. Test filtered versus forbidden future-smoothed
inputs and conditional-state uncertainty. No precondition that a deep Z must
survive: explicit/classical state can be sufficient.

FM-4 adds **one** new target after its own data/label contract review. Volatility
requires exact sampling and variance/volatility units; endpoint returns require
simple/log/adjusted basis and distribution/bucket definition. Calibration and
support are per horizon and head. Evaluation cannot infer return magnitude or
probability of profit from the original binary direction target.

Monte Carlo remains **DEFERRED**, outside the minimum FM-4 exit. It requires
validated joint state/return/volatility dynamics, dependence/discretization
assumptions and path truth. Sampling independent marginals does not earn path
risk or option-expression forecasts.

## 7. FM-5 — Modalities and graph complexity must earn admission

Add at most one group per approved experiment: governed narrative embedding,
dated graph relation, or another qualified context family. Begin with a simple
explicit context summary against the richer model; then evaluate learned fusion
only if its inputs add information independently. No raw text concatenation
into M; no chart screenshots; no current graph substituted historically.

Run retrained full/minus-sector/minus-narrative/minus-derivatives/minus-latent-
temporal/minus-graph/minus-macro arms for admitted groups. Define whether each
removal cuts all information routes or a single branch. Fit separate removed-
group preprocessing/encoders/calibrators; label inference-time occlusion as a
different test. Preserve contradictory sources and provider-neutral identity.

An unqualified group is NOT_TESTED. A failed group can be dropped without
disqualifying simpler accepted models. Source rights, archival vintages,
uncertain semantics and missingness may block a group indefinitely.

## 8. FM-6 — Ensembles and governed self-correction

Use FF's typed composition/calibration machinery and A7-wide Evaluation/Learning
workflow; do not implement a competing family-owned engine, registry or journal.
This local stage qualifies advanced-family use, not all conventional FF ensembles.

Require independent useful members before combination. Same target, horizon,
cutoff, subject, price/label basis and probability semantics are prerequisites.
Compare static average first; later weights/stacking/routing have their own
fit/calibration/compatibility artifacts. Dynamic ensembles are not initial scope.

Correction progression is diagnostics → proposal → authorized bounded candidate
job → independent evaluation → shadow → explicit approval → new COLD binding.
No automatic activation even for “fast” recalibration. Preserve rejection,
failure, abstention and rollback/denial records. A rollback changes a future
binding, not a past decision. Drift may deny new inference under existing policy;
it does not grant permission to train, acquire data or self-replace.

No hard fast/medium/slow schedule is prescribed. Later runtime scheduling remains
an independently authorized operational concern, not an FM research feature.

## 9. Stage-wide failure corpus

| Failure / ambiguity | Required outcome |
|---|---|
| Historical universe or data vintage unknown | Do not claim historical PIT validity; qualify/restrict scope or label research-only |
| Input zero versus missing/padding | Preserve factual zero; missingness reason remains separate |
| Same-date global close or revised macro value unavailable at cutoff | Exclude; no calendar-date join leakage |
| SSL/scaler/graph fitted on future evaluation dates | Invalidate run; no “unlabeled data” exemption |
| Incompatible latent basis or missing pinned implementation | Explicit rejection / UNVERIFIABLE; no current-model substitute |
| Graph/sector information survives a supposedly complete ablation via another branch | Fail ablation protocol and rerun under an independently valid test plan |
| Uncertainty field unsupported | NOT_ESTIMATED; no fabricated confidence |
| Missed event / calibration decline with too few observations | INCONCLUSIVE diagnosis; no causal claim or automatic retuning |
| No robust Delta_Z or worse calibration/resource profile | Reject/hold complexity; preserve controls and negative results |
| New model fails shadow | Reject promotion; existing approved binding unchanged or health-policy abstention |
| Replayed output differs from captured record | Preserve original; report verifier discrepancy with exact pins |
| Resource budget exhausted | Explicit incomplete/failed run; no silent substitution or indefinite trial search |

## 10. Existing deferrals and residual decisions

No canonical deferral row is closed, renumbered or duplicated by architecture.
The [58-entry register](TIAF_DEFERRAL_REGISTER.md) remains authoritative.

| Existing boundary | Consequence for this roadmap |
|---|---|
| DEF-007 / DEF-013 / DEF-049 | Qualified calendar/action/history vintages gate empirical claims; captured replay alone is insufficient |
| DEF-024 | A research experiment does not authorize indicator tuning or frozen-policy optimization |
| DEF-014 / DEF-040–044 | Derivative surfaces/paths/expected move/POP remain separately gated; endpoint direction does not close them |
| DEF-010 / DEF-050 / DEF-051 | No scheduler, distributed store or automatic outcome acquisition is created |
| DEF-052 / DEF-055 | Local statistical inference is not production LLM reasoning; resources and monetary costs need their own evidence |
| DEF-053 | Forecast research adds no cross-candidate A3 ranking/public leaderboard |
| DEF-057 / DEF-058 | No HOT loader, consumer-discovery publication or authority expansion; optional dependencies remain isolated |

Before implementation, choose the concrete qualified population, exact channel
allowlist/resolutions and footprint budget, fit/test history, latent dimensions,
seed/trial caps, minimum support, usefulness/robustness thresholds and machine
resource limits. Choose these through engineering/scientific review **before
looking at held-out model performance**. No symbol-specific thresholds or
illusory universal defaults are embedded here.

## 11. Thesis and paper gates

The illustrated [FM-LFDE thesis is CREATED](TIAF_FM_LFDE_THESIS_RECORD.md) and is
retained as the advanced-forecaster reference. Its coverage includes:

- ownership and evidence → K/Z → state → forecast diagrams;
- multi-resolution tensor/mask and actual-availability timelines;
- direct-head versus state-dynamics paths and horizon disagreements;
- paired K/Z/K+Z and retrained ablation designs with denominator examples;
- latent rotation/probe limitations and optional factor-promotion flow;
- uncertainty meanings, correction denial/promotion and replay lineage;
- staged alternatives, null-result examples and explicit scientific stop rules.

Its numerical examples are **illustrative**, not measured TI performance.
The [FF decision record](TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md) dispositions
its 24 findings; source DOCX/PDF/build assets remain unchanged. The separate FF
platform thesis is now created/reconciled and FF architecture accepted. A7
integration is reconciled and architecture accepted; sequencing/planning is next.

Paper 1 becomes a candidate conceptual manuscript only after thesis/design
review and further novelty reconciliation. Paper 2 needs qualified data,
preregistration, reproducible empirical results, controls/ablations/costs and
shadow evidence. Neither is authored now. See
[research readiness](TIAF_FM_LFDE_RESEARCH_RECONCILIATION.md#5-paper-readiness-and-thesis-handoff).

Exact next prompt:
**TIAF A7 — IMPLEMENTATION SEQUENCING AND FF-0 MINIATURE REALIZATION PLAN**.
