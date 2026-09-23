# Forecasting Framework — Bounded Delivery Roadmap

**Current checkpoint — 2026-09-23 (Asia/Kolkata):** FF-0 COMPLETE / FROZEN at
`tiaf-a7-ff0-baseline`; FF-1 COMPLETE / FROZEN at `tiaf-a7-ff1-baseline`
(`21783ea31d4ce3b54fbcc6fcce6ef7e641bd5bec`). FF-1 scientific outcome remains
**INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE**; infrastructure accepted,
Logistic CHALLENGER / EXPERIMENTAL, promotion eligible NO; BaseRate BENCHMARK.
2025 is CONSUMED, executions used 1, post-holdout refit allowed NO.

**FLC — Forecaster Lifecycle Completion is CURRENT**: architecture/gap plan
complete; FLC-1 inference, FLC-2 training/custody/lifecycle and FLC-3 synthetic-only optimization implemented.
Logistic is the sole learned reference;
no additional families or FF-0 behavior change. **FF-2 is intentionally
DEFERRED / NOT_STARTED until FLC closure**, then only a separately approved new
research proposal with new validation evidence. Eligibility is not a fit grant.
A7 overall remains IN_PROGRESS; no public forecasting capability or A4/A5/A6 influence.

See [FF lifecycle architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#22-forecaster-lifecycle-completion-flc)
and [FLC gaps/packages](TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md).
See the [FLC-1 implementation and validation](TIAF_A7_FLC_1_FORECASTER_CONTRACT_AND_LIFECYCLE_SEAM_NORMALIZATION.md).
See the [FLC-2 implementation and validation](TIAF_A7_FLC_2_TRAINING_MODEL_IDENTITY_PERSISTENCE_AND_LIFECYCLE_NORMALIZATION.md).
See the [FLC-3 synthetic-only optimization and validation](TIAF_A7_FLC_3_BOUNDED_DEVELOPMENT_ONLY_OPTIMIZATION.md).
Exact next task: **TIAF A7 / FLC-4 — MODEL-SPECIFIC DIAGNOSTICS NORMALIZATION**, separately requested.


## 1. Sequence, dependencies and deliberate simplification

```text
A7: FF-0 COMPLETE / FROZEN
 → FF-1 COMPLETE / FROZEN — INSUFFICIENT_EVIDENCE
 → FLC CURRENT — FLC-1/2/3 implemented; FLC-4 next
     Logistic only learned reference; BaseRate BENCHMARK
 → FF-2 DEFERRED until FLC closes + separate new research/data/protocol approval
 → existing conditional FF-3…FF-7 and separate publication / scoped closure gates
 → A8 → A9 → A10 [major order unchanged]
```

FF-0–FF-7 remain the canonical delivery notation within the A7 umbrella;
FLC is an intervening completion track, not an additional model stage,
not an additional A7.x hierarchy or eight compulsory model deployments. FF-4 is **not** a prerequisite for FF-5; an LLM adds no
necessary capability for numeric latent research. FF-3 is required before using
a multi-family ensemble, not before evaluating a standalone advanced forecaster
against a retained benchmark. Basic versioning, denial, replay and explicit
approval are present from the miniature, not postponed until FF-6.

The architecture accommodates finite 1..N forecasters at every stage. FF-0 can
prove mechanics with a singleton. The comparative miniature has B0 base rate
plus a calibrated B2 logistic candidate; PRIMARY is assigned only after its
independent scope-limited approval. No ensemble, LLM, multi-child graph or latent encoder
is a prerequisite to useful simple forecasting. If the candidate never qualifies,
retain a truthful benchmark/evaluation tool and explicit absence; do not claim
a production primary merely because the mechanics pass.

The first bounded ACTUAL inference path does not require a successful historical
simulation or qualified backfill dataset: an already eligible artifact/binding,
contemporaneous captured evidence and timely issuance can satisfy its operation.
Both mode contracts and synthetic negative fixtures still belong in FF-0.
FF-1 can compare qualified ACTUAL pairs; when retrospective walk-forward or
counterfactual generation is performed, it must use SIMULATED semantics. This
does not waive the complete miniature's evaluation/calibration/shadow gates,
its promised simulation/replay mechanics, or later facade/publication acceptance.

There is no separate FF-owned source-truth store: journal, labels, population
dispositions, ledger and comparisons reuse A7-wide Evaluation concepts. Likewise
the Benchmark Registry is a curated reference view over the one artifact/lifecycle
registry, not a new activation service. The old A7.1–A7.5 proposal is superseded
by the [explicit A7 crosswalk](TIAF_A7_DETAILED_ROADMAP.md#historical-five-slice-crosswalk).
FF-0 and FF-1 are complete/frozen. FLC implementation is next under a separate
request; FF-2 is deferred until its closure and a newly approved research proposal.
A8/A9/A10 ordering is unchanged.

## 2. Common entry package and completion meanings

| Requirement | Gate before empirical work |
|---|---|
| Authority | Named owner, exact permitted offline/inference/shadow operations, finite compute/trial/storage/egress budgets; no automatic activation |
| Target / data | Exact initial cash-equity endpoint, qualified adjacent sessions and positive same-basis closes; rights, vintages, action coverage, availability and neutral identity |
| Partitions | Chronological fit/selection/calibration/test; label maturity, dependency purge/embargo, dated universe and untouched final holdout |
| Realization / clocks | ACTUAL or SIMULATED explicitly pinned; real computation versus actual issuance/historical as-of; strict pre-open decision boundary, all-dependency PIT and per-comparison mode policy; no backdating |
| Protocol | Preregister metric definitions, support/class/session floors, paired uncertainty method, usefulness/noninferiority criteria, coverage and cost ceilings before seeing held-out results |
| Reproduction | Input/graph/artifact closure, deterministic fixtures, numeric tolerance policy, exact recorded replay and unavailable-verifier behavior |
| Bound scope | One target, finite population, small evidence schema, finite roots/nodes and trial lists; no request-controlled searches |
| Lower-layer preservation | A2/A4/A5/A6 and nine-operation catalog unchanged; no consumer authority or live procurement inferred |

**Engineering acceptance** proves typed mechanics and behavior on a declared
corpus. **Empirical qualification** needs eligible real observations, independent
support and uncertainty/calibration/cost evidence. **Approval** is an explicit
scope-limited owner decision after that evidence; **publication** is a further
caller/facade/Shell acceptance. None implies profitability or permission to trade.
Synthetic fixtures cannot close historical-calendar/action/data deferrals.

## 3. FF-0 — Contracts, common truth and one forecaster

**Entry:** FF architecture and separately scoped A7 integration independently accepted, bounded implementation
request authorized, frozen baselines checked. No empirical training unless a
separate qualified data/fit grant exists.

**Deliverables:** project-native immutable request/result/descriptor/artifact,
typed DAG/node/edge/root and run-trace contracts; one target/horizon/schedule
definition; shared label/journal references with append-only revisions; singleton
BaseRateForecaster using a pinned declarative artifact and fixture values first.
Support finite node collections now, reject cycles/unknown implementations, and
record explicit status/absence. Add neutral capture/recorded replay and a pinned
verifier boundary without optional model SDK imports.

Add architecture §§3.2–3.3's mode/clock fields and guards now: ACTUAL actual
issuance versus SIMULATED historical as-of, real computation for both, target
window and simulation-profile identity; typed absence for inapplicable clocks.
Preserve all original clocks through capture/replay without model dependencies.

**Tests:** tuple/list/JSON round trips; aware Asia/Kolkata normalization/naive
rejection; exact up/down/flat versus missing/invalid labels; calendar adjacency,
corporate-action ambiguity, late/revised labels and no future leakage; singleton
graph, duplicate IDs, self-cycle and depth caps; incomplete required scope;
recorded replay with unavailable model/provider modules; unchanged A6 capture.
Include correction cases A–G plus exact-open rejection, late-but-honest ACTUAL
rejection and original-clock preservation under later verification. Unknown or
leaky evidence fails PIT qualification even when the numeric clock checks pass.

**Success:** reproducible scientific-control mechanics on the named synthetic
corpus; qualified versus synthetic evidence remains explicit. “One forecaster
runs” does not establish comparative model value.

**Stop/fallback:** unqualified schedule/data means no empirical label or forecast
claim; retain inspection of absence and synthetic mechanics. Malformed graph
fails before executing nodes; no repair by selecting a different instrument.

**Next-stage gate:** reviewed contracts/absence/PIT and replay evidence, stable
common observation identity, accepted finite protocol for comparison work.

## 4. FF-1 — Benchmark Registry, Forecast Ledger and paired evaluation

**Current status: COMPLETE / FROZEN at `tiaf-a7-ff1-baseline`.**
The [FF-1 plan](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md) and
[slice/closure evidence](TIAF_A7_FF1_INDEPENDENT_FINAL_SCIENTIFIC_CLOSURE_AND_BASELINE_DECISION.md)
record the actual qualification, fixed training, walk-forward, development,
fifth-fold, one-shot evaluation and final closure. Planned slice names are not
claims of separate tags. Final outcome is INSUFFICIENT_EVIDENCE; 2025 CONSUMED,
one execution, no refit. The stage obligations below are retained, not a new
instruction to run FF-1. Remaining reusable lifecycle gaps belong to FLC.

**Entry:** FF-0 mechanics accepted; qualified paired dataset or explicitly
SYNTHETIC_ONLY exercise; exact fit/comparison grant and frozen protocol.

**Deliverables:** B0 benchmark configuration and B2 logistic candidate over the
small allowed feature schema; raw output explicitly labeled until calibration.
Benchmark Registry as immutable curated references; common Forecast Ledger
snapshots; `PairedComparisonManifest`; A7 population dispositions and scorecard
emission even for partial/zero-evaluable attempts. Retain ground truth once per
observation, request-to-observation dedupe, exact outcome revisions and arm costs.
Report Brier/log loss, reliability, coverage/abstention, scoped secondary metrics
and preregistered paired uncertainty. Finite chronological fit/search ledger.
Walk-forward generation creates SIMULATED records with actual later fit/computation
and historical decision/fit cutoffs; all training/calibrator/selection knowledge
is cutoff-bounded. Ledger arms preserve mode and simulation profile, share target
truth without overwriting actual history, and pin comparison mode policy.

**Tests:** same rows/target/horizon/cutoff/basis/revision/split compatibility;
mixed-label-version rejection; duplicate requests without double outcome weight;
different feature families with the same admitted comparison key; conflicting
captures not merged; common-intersection versus union denominators; undefined
precision/zero-pair outcomes; no best-run or future-label cherry-picking;
append a revised ledger without mutating old records; shared ground truth across
all arms; statistical fixture arithmetic, not a claim of empirical superiority.
Test actual/actual and simulated/simulated pairs, denied implicit mixed pooling,
explicitly permitted matched mixed-mode research, future-fold leakage, delayed
outcome recording and multiple simulations without duplicate outcome weighting.

**Success:** independently reproducible paired reports with complete coverage and
negative/inconclusive results preserved. No production PRIMARY or calibrated
claim just because an uncalibrated candidate beats one fixture control.

**Stop/fallback:** missing population identity or qualification blocks the score;
insufficient independent support produces INCONCLUSIVE/NOT_EVALUABLE, not PASS.
Benchmark-only mechanics remain usable for engineering inspection.

**Next-stage gate:** trusted comparison infrastructure and sufficient separately
qualified calibration/test data; no additional ML families required.

## 4a. FLC — Forecaster Lifecycle Completion before FF-2

[FF §22](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#22-forecaster-lifecycle-completion-flc)
owns the additive architecture; [FLC-0…8](TIAF_A7_FLC_FORECASTER_LIFECYCLE_COMPLETION_PLAN.md)
owns the inspected gap matrix, package deliverables/tests/non-goals/models.
CURRENT: FLC-1/2/3 implemented; FLC-4 next. This brings forward
reusable inference/training/artifact/event/tuning/diagnostic and evaluation seams
using only Logistic and BaseRate. Calibration contracts/test doubles are in scope;
fitted calibration, real shadow/advisory approval and FF-2 science are not.

Exit: reviewed synthetic reference lifecycle, native restore and recorded/pinned
replay separation, old FF-0/1 preservation, independent common evaluation,
finite trials and explicit failure/absence. No empirical superiority required.
Failure of a mandatory seam blocks FLC closure, never licenses editing FF-1.

## 5. FF-2 — Calibration, lifecycle, shadow and complete miniature

**Status: DEFERRED / NOT_STARTED until FLC closure.**

**Entry:** accepted FLC reference closure and FF-1 comparison/ledger, a separately
approved new experiment/validation strategy (2025 is not unseen), qualified held-out calibration split,
frozen support/usefulness/shadow/health policies and explicit prospective grant.

**Calibration placement decision:** FF-0 defines typed calibration state/pins and
tests raw/absent qualification; FF-1 can score raw B0/B2 research probabilities;
FLC defines/tests reusable calibration and lifecycle seams without fitting;
FF-2 fits/applies/independently qualifies the held-out sigmoid wrapper and completes
the calibrated miniature. No fitted calibrator or advisory calibration claim is
required to prove FF-0 singleton mechanics. Fit grants/data gates still apply.

**Deliverables:** separately held-out sigmoid-calibrated logistic root, retaining
raw output and B0; calibrator wrapper identity, scope and independent reliability
evaluation. Split role assignments from lifecycle events with no widened approval.
Candidate validation and prospective non-influencing shadow records; independent
promotion recommendation and explicit future COLD selection. Exact recorded,
pinned recomputation and separately labeled historical counterfactual simulation.
Prospective shadow requires ACTUAL_ISSUANCE, not reconstructed simulations;
historical model/calibrator studies retain their SIMULATED provenance. A complete miniature is
one target/journal, benchmark/candidate, evaluator/calibrator and replay chain.

**Tests:** wrong calibrator/target/fit pins, insufficient classes, test-fit leakage,
refit invalidating downstream calibration, degraded primary, failed shadow,
denial/resumption, DISABLED versus RETIRED, SHADOW role versus lifecycle,
unapproved PRIMARY rejection, no HOT switch and old forecast/label replay after
new artifact approval. Missing exact verifier never runs the current model.
Verify no simulated-to-actual/shadow conversion; recorded/pinned operations retain
original computation/issue/as-of while verifier time/cost stay separate. Reject
a current/historical model whose learned dependencies violate the simulated cutoff.

**Success:** accepted mechanics plus an honest empirical scorecard. Only a candidate
meeting all gates can become the scoped advisory PRIMARY; otherwise retain the
qualified controls/absence. No promise that logistic will qualify.

**Stop/fallback:** hold or reject miscalibrated, unsupported, unstable, over-budget
or failed-shadow candidate. A previously approved healthy binding can continue;
otherwise abstain under pinned health policy. No result-driven threshold rescue.

**Next-stage gate:** stable miniature and an independently justified additional
family/composition hypothesis. A later separately accepted post-FF-2 facade/Shell
projection may expose captured graphs and comparison reports after FF-2, without
requiring FF-3 or adding public train/promote/config-edit operations.

## 6. FF-3 — Bounded multi-family execution and simple ensemble

**Entry:** FF-2 quality/governance infrastructure; qualified B0/B2 controls;
bounded grant for one conventional ML challenger (B3, XGBoost or one substitute).
An actual ensemble additionally requires independently qualified compatible members.

**Deliverables:** finite auxiliary roots; deterministic DAG traversal, shared-node
dedupe, node-level traces and unique work accounting; B3 first, B4 kNN only for a
separate hypothesis. Optional B5 simple probability mean and its own calibrated
root. Typed vote/conversion configuration and rejection fixtures; advanced voting
policies need separate validation, not a bare score-average implementation.
Composite versus components/validation-selected best/simple-control reports;
optional declared leave-one-out variants and disagreement diagnostics.

Follow architecture §§5.1/7.1/7.2 for semantic duplicate identities, operator-specific
ordering, legal singleton mean/vote and the fixed-electorate truth table. Follow
§14.1 for optional versus preregistered promotion-required removal/control studies;
do not interpret a failed required child as a removal experiment.

**Tests:** nested/cross-reference cycles, incompatible output/event/cutoff/basis,
raw versus calibrated states, singleton mean, duplicate voters, fixed electorate
quorum/ties/ABSTAIN versus failure, required missing child, no implicit probability
conversion or renormalization; B/C/ensemble/root results all retained; shared
node charged once, retries included and parent totals not double-counted;
leave-one-out refit/cost identity; best-on-test oracle labeled non-deployable.

**Success:** new family/composite earns incremental qualified value within cost
and coverage constraints. A valid multi-model execution without ensemble gain
is an engineering result only; keep the simpler root.

**Stop/fallback:** reject unjustified composition, keep members as optional
challengers or disabled records; no automatic allocation to whichever wins a
recent subgroup. Missing required children cause declared absence, not runtime
conversion into an untested singleton.

**Next-stage gate:** optional extension justified by evidence and budget. LLM and
FM/LFDE tracks can instead enter from FF-2 with the necessary common interfaces;
no requirement to complete every B0–B6 rung.

## 7. FF-4 — Optional LLM forecaster

**Entry:** FF-2 shared science/replay; specifically approved model-gateway use,
prompt/evidence scope, privacy/rights and total attempts/token/cost caps. Historic
training-vintage uncertainty bars historical PIT claims; qualified prospective
shadow is a distinct possible path, not an exemption from evidence admission.

**Deliverables:** one structured LLMForecaster adapter behind the governed
gateway, not specialist SDK imports. Captured prompt/response/model/decoding
lineage, abstention/conflicts/evidence refs, raw probability state and separate
eligible calibration. Compare against the same B0/B2 outcomes/observations with
actual latency/cost and failed-call coverage.

**Tests:** malformed outputs, nonfinite values, unsupported target, injected
instructions in supplied text, fabricated evidence refs, missing credentials,
budget exhaustion, retries, unknown model revision/cost, lack of calibration,
nonrepeatable remote result with successful offline recorded replay; no tools
or request instruction can mutate topology/weights/authority.

**Success:** only measured qualified incremental evidence warrants use; no
privileged vote or PRIMARY role due to being an LLM. Record negative results.

**Stop/fallback:** missing qualification, weak contribution, unreliable calibration
or excessive cost leaves LLM unapproved/disabled; numeric FF remains independent.

**Next-stage gate:** none mandatory. LLM is not an entry gate for FM/LFDE, A7
acceptance of the miniature or later numeric research.

## 8. FF-5 — Advanced FMLFDEForecaster

**Entry:** accepted FF-2 common evaluation/calibration/replay and independent
bounded family-research authorization; qualified tensor/K inputs and a B6 K-only
comparator. FF-3 is needed only for an ensemble use; FF-4 is not required.

**Deliverables:** neutral FMLFDEForecaster boundary over the retained
[FM-0–FM-6 and LFDE L0–L5 program](TIAF_FM_LFDE_DETAILED_ROADMAP.md).
Reuse FF scientific infrastructure for FM-0; do not duplicate journals, labels,
registries or primary selection. Add explicit K, classical controls and one
masked temporal encoder only as local gates pass. Preserve numeric tensors,
latent basis, state/fusion/head/internal calibration trace and optional later
dynamics, modalities and graph experiments. Register initially as CHALLENGER.

**Tests:** K/Z/K+Z paired identity, full-route/retrained ablation, masks versus
zero/padding/empty target batch, future SSL leakage, temporal/asset alignment,
PCA and relevant dynamic controls, basis/head compatibility, held-out stability
anchors, NOT_ESTIMATED uncertainty, outer/internal calibration identity and
optional branch absence. All standard FF contract/replay/authority tests apply.

**Success:** stable incremental proper-loss/calibration evidence over K and
relevant FF benchmarks, within support/coverage/cost limits. Standalone advisory,
ensemble or routed use each needs the appropriate qualification; none is granted
by implementation of the wrapper.

**Stop/fallback:** retain explicit/classical forecasters if Z fails. Drop weak
graphs/modalities, keep a direct head if dynamics adds nothing, stop within the
finite trial budget. No aesthetic latent plots or named-symbol tuning as success.

**Next-stage gate:** independent evidence for each local FM extension and later
FF composition/correction hypothesis; no obligation to complete every FM stage.

## 9. FF-6 — Governed self-correction expansion

**Entry:** stable shared Outcome Journal/paired diagnostics and lifecycle; explicit
job and resource authority. FF-2 already has manual gates; this stage expands
bounded proposal/candidate workflows, not initial activation powers.

**Deliverables:** CorrectionPlanner proposals for recalibration, fits, member
removal, weights, role changes or challenger promotion. Record suspected causes,
alternatives, expected test and input/graph lineage. Candidate generation under
grants, independent validation/shadow, recommendation and explicit COLD approval.
Example: remove negative-contribution kNN in a newly evaluated graph, not the
current active one. Reuse A7-wide training/registry rather than another loop.

**Tests:** diagnosis inconclusive, no grant/no job, proposal not permission,
new graph/weight/calibrator identities, backtest gain but shadow failure,
consumed trial budget, contamination from repeated holdout selection,
rejected/rolled-back candidate history and old forecast replay unchanged.

**Success:** independently supported future improvements and rejected poor
candidates are both useful outputs. No autonomous activation, even for “fast”
calibration. Concrete schedules remain separately governed operational policy.

**Stop/fallback:** insufficient cause/support or a failed candidate leads to
hold/rejection; continue old healthy binding or deny under existing policy.

**Next-stage gate:** only recurring supported regime-specific evidence and an
independent need can justify FF-7. FF-6 need not train or use every family.

## 10. FF-7 — Advanced routing / stacking / mixture of experts

**Entry:** independently useful compatible experts, stable scope/regime metadata,
sufficient held-out support, bounded router/meta-model budget and qualification
protocol. Depends on the relevant FF-3 composition mechanics and FF-2 governance,
not universal completion of LLM or FM research.

**Deliverables:** separately typed frozen routing/meta-model policy; train-only
or valid out-of-fold weight/gate fitting; context eligibility and missing-expert
rules; combined calibration, conditional support and full node trace. Report
selected/unselected experts and no invented outputs for unexecuted branches.

**Tests:** future-smoothed regimes, post-hoc cohort selection, invalid meta-fit
rows, stale routing context, missing expert/unknown regime, hidden component
failure, recursive cycles, support collapse, out-of-distribution gates, replay
after router/model updates and controlled cost versus static mean/simple primary.

**Success:** robust incremental value over static composition and simple controls,
not just an attractive best-regime chart. Scope remains exact and externally
approved; frozen routing is COLD configuration executing deterministically, not
HOT model installation.

**Stop/fallback:** reject unhelpful routing; preserve independently qualified
static/simple alternatives as separate bindings. No silent live topology rewrite.

**Next-stage gate:** separately proposed further research/operations only;
no new automatic-learning or trading permission follows from completing FF-7.

## 11. Deferrals, unresolved profile choices and next artifact

No canonical row in the [58-entry deferral register](TIAF_DEFERRAL_REGISTER.md)
is changed. DEF-007/013/049 still gate qualified session/action/history claims;
DEF-010/050/051 do not become schedulers/stores through a ledger diagram;
DEF-052/055 are not closed by describing an LLM; DEF-057/058 still constrain
HOT loading and publication. Option/path/PoP and cross-candidate ranking remain
separate targets and consumer acceptances, not consequences of binary forecasting.

Before authorizing the miniature, choose the exact limited evidence schema,
population, fit/calibration/test windows and source qualification; all numeric
support/uncertainty/usefulness/health/shadow/graph/resource limits; enum/event
mapping and verified artifact serialization; and concrete later facade scope.
These are bounded future acceptance/profile decisions, not defaults tuned to
RELIANCE/HDFCBANK/KAYNES or proof that empirical data is already available.

The previous architecture checkpoint requested a **separate FF platform thesis**,
preserving the FM/LFDE advanced handbook. That thesis
is now created and its 28 findings are reconciled; neither artifact edition is
regenerated by this pass. Current next prompt:
**TIAF A7 / FLC-4 — MODEL-SPECIFIC DIAGNOSTICS NORMALIZATION**.
The bounded FFA-B01 correction supplies mode/clock guards and FF-0–FF-2 fixture
obligations; the repeat review accepts the architecture, not their implementation.
All four non-blocking
FFA-C01–FFA-C04 follow-ups remain as recorded, without reopening operators or
adding retention, scheduling, process-isolation or pricing machinery.

### 11.1 Mandatory implementation-prompt carry-forward

Both implementation-detail findings retain **architecture impact = none**: the
existing obligation to version/preregister these policies already exists. No
new metric, significance hurdle or numerical default is adopted here.

| Finding / owner / stage | Later implementation prompt must explicitly request | Required fixture / stop condition |
|---|---|---|
| FFT-15; Evaluation; FF-1, reliability application FF-2 | Pin metric registry/version, log base, endpoint/clipping treatment, weights/denominators, bins/reliability summary and finite/infinite/undefined serialization; retain original issued p | Exact p=0/1 and labels 0/1; clipped versus unclipped reporting; empty and zero-weight populations; zero-denominator class metrics. JSON must not silently encode nonfinite loss as a finite score; use typed result state. Missing conventions block metric computation |
| FFT-16; Evaluation protocol owner + independent reviewer; before FF-1 holdout, repeat at later stages | Pin time/session-block scheme, panel clustering, support/classes, interval/confidence method, practical-usefulness/noninferiority gates, split membership, purge/embargo, trials/multiplicity and resource limits before protected outcomes | Correlated sessions, sparse class/cohort support, inconclusive paired interval, all trials retained; post-hoc method change creates new approved protocol and independent holdout, never rescues the old claim |

### 11.2 Deferred findings and admission triggers

These are retained local design deferrals, not new canonical DEF IDs. Existing
register links below are related constraints, not assertions that either finding
has an exact canonical equivalent. All 58 canonical rows/statuses stay unchanged.

| Finding / retained reason | Destination / owner | Admission trigger and evidence | Existing canonical relationship |
|---|---|---|---|
| FFT-08 Ranking: binary event does not define an investable cross-candidate order; miniature must not expose a scanner shortcut | Separately authorized post-FF-2 rank-target/operator design; only then a reviewed FF-3 extension and later relevant A7 consumer/A9 acceptance. Not implicitly included in FF-3 | Exact dated universe and PIT membership; what score ranks, direction/ties/units, rank-compatible target/metric and paired population; useful evidence and separate consumer policy. Until then no singleton ranking, A3/A6 rerank or scanner ordering | DEF-049 constrains historical universe/PIT claims; DEF-058 constrains new publication. Neither is closed or relabeled “ranking” |
| FFT-28 Advanced routing/MoE: useful experts and specialization evidence are not established; unnecessary to miniature | Conditional FF-7; Forecasting operator, Learning fit, Evaluation qualification, independent reviewer/startup binding | Accepted relevant FF-3 mechanics and FF-2 governance; useful compatible experts, cutoff-eligible cohorts/support, independent walk-forward against static/simple controls, leakage-safe gate fit/calibration, bounded cost, missing-expert/UNKNOWN rules and separately captured counterfactual plan | DEF-049 for historical PIT, DEF-057 continues HOT prohibition, DEF-058 for later consumer publication; DEF-052/055 only if optional LLM experts are selected |

Both require a fresh bounded request; documentation alone does not promote them.
The initial FF-3 mean/weight/vote rules do not authorize learned stacking,
adaptive or regime-specific weights, ranking, a model tournament or HOT selection.

### 11.3 Reconciled acceptance-fixture obligations by stage

| Stage | Additional precision from this reconciliation; existing six gate fields above remain |
|---|---|
| FF-0 | Raw/absent/qualified contract examples; clocks and authority; exact semantic/capture projection; no alias-based duplicate influence |
| FF-1 | FFT-15/16 pinned protocols; UNKNOWN/overlapping cohort memberships, global win/local loss and old-label comparison replay |
| FF-2 | Lossless A7 events including rejected/denied/suspended histories; qualified SHADOW fields; promotion decision distinct from binding; full replay promise modes |
| FF-3 | Operator-specific order, weight-pair permutation, explicit replication restrictions, singleton/failure/voting fixtures and fixed-rule versus refitted removal arms |
| FF-4 | Independent revision/vintage/prospective/recompute/cost axes; captured PASS with recompute UNVERIFIABLE; malformed/timeout and strict-price-cap denial |
| FF-5 | Family internals retained; transitive basis/head/internal-and-outer-calibrator closure; no duplicate Evaluation services |
| FF-6 | Exact proposal/grant/recommendation/reviewer-decision/binding chain; no auto-activation or rejected-history deletion |
| FF-7 | Deferred admission package above; matched captures for unselected-expert studies, no invented counterfactuals or hindsight routing |

This roadmap specifies what an independently accepted implementation request must
carry; it does not execute those fixtures or claim empirical qualification.
