# TIAF A7 — Integrated Forecasting / Evaluation / Learning Roadmap

The [FF-0.1 implementation record](TIAF_A7_FF0_1_CONTRACTS_TARGET_CLOCK_IMPLEMENTATION.md)
records **FF0_1_ACCEPTED**: immutable contracts, one synthetic RELIANCE target,
clock/knowledge validation and deterministic identity primitives. A7 / FF is
**IMPLEMENTATION IN_PROGRESS; FORECAST EXECUTION RUNTIME NOT_IMPLEMENTED**.
Only the first of the [four planned FF-0 steps](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md)
is complete. Next is separately authorized **FF-0.2 — Capture store, truth and
recorded replay**. FF-0 overall is not accepted; no model, public capability or
empirical qualification is delivered. Calibration remains at FF-2.

## Status and sequencing

**2026-09-15 (Asia/Kolkata): A7 ARCHITECTURE ACCEPTED;
A7 THESIS RECONCILED AS NEEDED; FF ARCHITECTURE ACCEPTED;
A7 / FF IMPLEMENTATION IN_PROGRESS (FF-0.1 ONLY); RUNTIME NOT_IMPLEMENTED.**

The [independent acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) approves the
architecture for sequencing. The separate FF-0.1 request implemented only the
foundation; FF-0.2 and later work still require their own bounded requests.

The [integration record](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md)
owns the old-to-new disposition. The [A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md)
owns umbrella science/governance; the
[accepted FF roadmap](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md)
owns FF stage entry/deliverables/tests/success/stop/next gates. These are
cooperating documents, not alternative implementation sequences.
The [milestone ledger](MILESTONES.md) owns actual acceptances/tags.

```text
A6 FROZEN at tiaf-a6-baseline; R1–R5 ACCEPTED / DONE
 → FF ARCHITECTURE ACCEPTED; FF THESIS RECONCILED
 → A7 FF INTEGRATION RECONCILED; A7 ARCHITECTURE ACCEPTED
 → FF-0 MINIATURE PLAN COMPLETE [planning only]
 → FF-0.1 CONTRACTS / TARGET / CLOCKS [ACCEPTED; FOUNDATION ONLY]
 → separately authorized FF-0.2 CAPTURE / TRUTH / RECORDED REPLAY [NEXT]
 → separately authorized bounded FF-0 → FF-1 → FF-2 [complete miniature]
      ├─ separate facade / Shell publication checkpoint, if authorized
      ├─ FF-3 optional multi-family / simple ensemble
      ├─ FF-4 optional LLM
      └─ FF-5 optional FM/LFDE, retaining internal FM/L gates
 → optional FF-6 governed correction expansion
 → conditional FF-7 advanced routing / stacking / MoE
 → closure of the explicitly accepted implemented scope
 → A8 → A9 → A10 [major order unchanged]
```

## One canonical stage model

**A7 is the umbrella containing FF-0…FF-7 unchanged.** Do not create a second
A7.0…A7.7 hierarchy or execute the old A7.1…A7.5 queue beside FF. Those old
numbers are historical proposal locators, not current delivery IDs. The
crosswalk below transfers their obligations without claiming any implementation.
FM-0…FM-6 / LFDE L0…L5 are nested family research gates at FF-5, not another
generic forecast/evaluation stack.

The first implementation request authorized FF-0.1 alone. FF-0/1 mechanics
and raw research can be useful before FF-2 completes calibration/lifecycle.
No requirement to finish every optional stage before bounded A7 closure.
Closure must explicitly identify implemented scope, empirical status and carried
conditional stages; this document does not freeze that scope or authorize A8.

The publication and closure checkpoints below are acceptance obligations, **not
new numbered stage hierarchies**. FF-2 may complete internal calibrated/shadow
science while the public surface remains unavailable. Publication can follow
FF-2 without FF-3/4/5/6/7. FF-4 is never required for numeric FF-5; FF-3 mechanics
are needed only when a selected family uses multi-family composition.
Basic approval, denial, replay and manual shadow are present by FF-2, not
postponed until FF-6.

## Historical five-slice crosswalk

| Old proposed slice | Responsibility retained | Canonical destination | Deliberate change |
|---|---|---|---|
| A7.1 | Target/schedule/tuple/time contracts, small A2 feature schema, PIT dataset/label/journal/population contracts, protocol preregistration | FF-0 foundation; FF-1 dataset/split realization and report emission | Use FF request/result/DAG contracts and both realization modes, not a singular A7 model envelope |
| A7.2 | BaseRate/logistic, chronological walk-forward, controls/proper metrics, calibration, all trials/costs and denominator accounting | FF-1 B0/B2 raw paired research; FF-2 separately held-out sigmoid/qualification | Do not require fitted calibration to prove FF-0/1 research mechanics |
| A7.3 | Local registry, approvals/drift, COLD selection, exact/tolerated replay and explanation | FF-0 capture/verifier and artifact-reference foundation; FF-1 evaluation replay; FF-2 lifecycle/calibration/full miniature | One typed registry, FF role/lifecycle separation and exact graph closure; no competing active-model owner |
| A7.4 | Caller-bound facade/Shell, discovery, engineering evaluation and manual prospective shadow | Internal authorized shadow at FF-2; separately accepted post-FF-2 publication checkpoint | Shadow is not dependent on a public facade; publication does not require ensembles/LLM/FM |
| A7.5 | Failure/leakage corpus, lean imports, lower-layer regression, empirical scorecard, deferral burn-down and freeze review | Incremental tests at each FF stage plus scoped major closure checkpoint | No single final phase postpones safety; optional family completion is not compulsory |

The earlier [30-finding record](TIAF_A7_RECONCILIATION_RECORD.md),
[17-finding record](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md) and unchanged
thesis remain historical evidence of the original plan. Their A7.x references
are resolved by this table; their scientific requirements are not deleted.

## Stage ownership and bounded deliverables

| Canonical stage | FF / Forecasting | Independent Evaluation | Governed Learning / external approval | Exit and failure boundary |
|---|---|---|---|---|
| FF-0 | Immutable request/result/descriptor/artifact/DAG/run, singleton B0 fixture, capture and pinned-verifier boundary; mode/clock and finite graph admission | One target/horizon/schedule/label specification, journal and population contracts, knowledge/rights qualification rules | Exact declarative artifact references and separate bounded job grants; no empirical fit implied | Synthetic contract/PIT/replay mechanics; unqualified data cannot yield empirical claims |
| FF-1 | B0 control and B2 logistic raw research instruments; named comparison arms | Benchmark view, Ledger snapshots, PairedComparisonManifest, proper metrics, dispositions, chronological walk-forward, context and uncertainty protocols | Authorized candidate fits/selection with all trials/usage; one typed artifact registry | Reproducible honest paired report; zero pairs or insufficient support is NOT_EVALUABLE/inconclusive |
| FF-2 | Pinned sigmoid wrapper, complete graph/artifact replay, scoped shadow and eligible advisory root enforcement | Independent calibration, controls, health/drift and matured ACTUAL shadow evidence | Lossless lifecycle/role events, explicit reviewer approvals and trusted COLD binding/rollback | Complete miniature; reject miscalibrated/unsupported/failed-shadow candidates, no public or decision influence inferred |
| FF-3 | Optional B3 single conventional challenger; B4 kNN only by hypothesis; B5 simple compatible calibrated ensemble, typed vote, shared-node execution | Component/parent/best-control and optional preregistered removal studies, disagreement and unique cost | New weights/member set as candidates, independent qualification before binding | Keep simpler useful root if complexity adds no supported value; no renormalization after required failure |
| FF-4 | Optional LLMForecaster via governed model gateway; exact captured prompt/response/observable revision | Common truth, proper losses/calibration, mode/vintage limits, failure-rate and latency/cost comparison | Prompt/model/calibration or inclusion/removal candidates under separate grants | No privileged vote/role; unknown history bars PIT claims, exact replay need not imply recomputation |
| FF-5 | Optional FMLFDEForecaster preserving tensor/K/Z/state/head/internal calibration | Shared truth and K/Z/K+Z, classical and other FF controls, ablations/stability | Nested FM/L candidates and basis/calibration manifests | Reject weak Z/dynamics/modalities within finite budget; family never owns generic truth or approval |
| FF-6 | Supply immutable observations; enforce existing binding | Independent diagnosis and evaluation of corrections | Expand CorrectionPlanner/train/recalibrate/shadow/promotion-evidence workflow | Proposals and metrics never auto-activate or widen target/authority |
| FF-7 | Conditional frozen router/stacking/MoE under typed DAG | PIT context support, paired comparison versus static/simple controls, full coverage | Leakage-safe gate/meta-fit/calibration, independent approval and COLD selection | Hindsight routing, weak experts or inadequate scope blocks; HOT remains deferred |

Refer to FF's unchanged stage-specific failure/operator test obligations. Above
is the A7 ownership allocation, not a substitute set of mathematical defaults.

## Retained scientific and contract entry gates

Before **any empirical fit or protected-outcome inspection**, require:

- Exact `equity.next_session_close.return_gt_zero/1.0`, qualified NSE cash
  equity, positive finite same-basis unadjusted endpoints, strict comparator
  (flat = 0, absent/invalid = no label), supplied official-origin schedule
  coverage proving adjacency, exceptions/revisions and source/action rights.
- A small concrete ordered allowlist of existing A2 fields with units/lookbacks,
  projection/version/lineage and explicit missingness. No A2 recalculation,
  indicator optimization or provider-specific fields.
- Qualified dated universe, source availability/acquisition/admission/vintages,
  action exclusions, all learned/selected knowledge cutoffs and retention/
  training rights. A history download is not CAPTURED_AS_KNOWN.
- Chronological whole-origin-session train/calibration/validation/test blocks,
  dependency-aware purge and at least the retained target-session embargo,
  distinct split-plan and realized-membership fingerprints; locked holdout,
  no repeated test observations counted as new independent evidence.
- Reviewer-approved preregistered numerical support/class/session/cohort/bin,
  uncertainty, Brier-improvement/log-loss non-inferiority, calibration/stability,
  health/expiry, shadow duration/mature-label/coverage/interruption and budget
  profiles. Missing values block affected empirical work, not synthetic tests.
- FF FFT-15/16 metric and statistical convention pins: log/clipping/finite or
  undefined serialization, fixed ECE bins/weights/empty-bin rules, panel/time
  resampling, multiplicity and practical usefulness. No thesis example is a
  policy default and no tuning to RELIANCE/HDFCBANK/KAYNES/ATHERENERG.
- Bounded rows/features/folds/trials/fit iterations/time/memory/artifact size,
  seeds/runtime/dependency pins and all failed-attempt costs; optional isolated
  fitting adapters, declarative local inference artifacts, no arbitrary pickle.
- ACTUAL and SIMULATED contracts from FF-0. Strict pre-open ACTUAL issue follows
  real completion; historical simulation has later real completion, historical
  as-of and no issued_at. Both gate all fitting/selection knowledge. Current
  authority cannot be backdated by an old research cutoff.

FF-1 can compare qualified ACTUAL pairs without a successful historical
simulation dataset. Retrospective generation uses SIMULATED profiles/folds.
Both need qualified later labels for supervised metrics, not for generation.
Mixed-mode comparisons need explicit preregistered matched research policy;
composition edges cannot mix modes. SIMULATED reliability is not ACTUAL shadow.

## Publication checkpoint — separately authorized after FF-2

No capability is published by this roadmap. Current catalog remains **nine**.

Potential minimal future surface: `forecast.assess` as an advisory/public
candidate, `forecast.evaluate` as engineering-only bounded captured evaluation,
and additive supported artifact kinds for existing `replay.recorded` /
`replay.verify`. These names are not reserved/registered by this pass.
`forecast.compare` is not added just because paired comparison exists.
`model.list` / `model.describe` remain engineering views unless justified.

Before publication, separately accept exact versioned FF-to-consumer projection
(`ForecastEvidenceV2` name retained conceptually, not an alias), admission,
caller/entitlement/effect/budget/artifact scope and permission-filtered discovery.
Unknown mode/graph/calibration/provenance cannot be coerced into legacy A3.1
ForecastEvidence or hidden in metadata. Preserve A0 package/schema distinction.

Shell remains parser → typed command → caller-bound facade → allowlisted
renderer, with no model/trainer/registry-backend/provider imports, loader paths,
Python/DSL evaluation, public train/promote/config-edit or broker command.
Graph/node, comparison, population and raw-logit/calibration explanations must
be faithful to captured fields, not probability-point or causal attributions.

Acceptance requires domain/facade parity, human/JSON/explain/trace parity,
denied-scope and optional-dependency behavior, offline recorded replay and zero
unintended external effects. Valid A2/A4/A5/A6 results/fingerprints remain
identical with forecasting available, absent, failed or abstaining. Forecasting
absence cannot rescue an invalid deterministic baseline.

## Incremental hardening and bounded closure

Keep architecture §17's full corpus obligations, including:

- tuple/list/JSON/fingerprint round trips, naive-time rejection and aware
  Asia/Kolkata normalization; source/target clock edges, real completion versus
  start, exact-open rejection, no backdating or SIMULATED-to-ACTUAL relabeling;
- missing/revised/censored endpoints, calendar correction without S2 retargeting,
  corporate-action unknowns and selection bias, delayed labels/recording;
- future feature/fit/calibration/selection/SSL leakage, survivor bias, train-only
  transforms, same-session split contamination and exhausted holdout;
- sparse classes/bins/regimes, bad calibration despite AUC, worse control,
  pooled win/required-cohort loss, honest inconclusive/negative results;
- population partitions/count integrity, original requests versus unique
  observations, rejected/untraded/abstained/failed and revised-label cases;
- every approval/expiry/health gate, bounded pending-label grace, earliest
  use-by, denied resumption, interrupted shadow and fake authority;
- graph cycle/incompatibility/duplicate influence/shared cost, failed required
  child versus legitimate abstention, no survivor renormalization;
- exact recorded versus pinned/tolerated/refit checks; tamper/missing pin, absent
  verifier, newer model installed, original clocks unchanged, tolerance never
  permits a class/admission boundary flip;
- fake fills/P&L/option POP or path ordering, no automatic A4/A5/A6 influence,
  security/lean-import/cost/failure and unchanged R1–R5/frozen baselines.

At scoped closure, report engineering acceptance independently of empirical
qualification and model approval. A correct implementation may reject every
candidate. Carry all unimplemented conditional stages/deferrals honestly; no
requirement to finish FM research or deploy an LLM to freeze a bounded miniature.
No automatic tag operation follows.

Future implementation gates, **not run by this documentation pass**:

```bash
python -m compileall src scripts
pytest -q
ruff check src tests scripts
mypy src tests
git diff --check
```

## Unresolved choices and gates

| Remaining choice / evidence | Owner / blocking gate |
|---|---|
| Eligible source/schedule/action/PIT dataset | Evidence qualification + Evaluation; blocks empirical use, DEF-007/013/049 remain open |
| Exact feature IDs, FF schemas/native artifact/serializer and fit dependency | FF + Evaluation/Learning engineering; FF-0/1 before fitting |
| Numerical metrics/support/uncertainty/shadow/health/budget profile | Evaluation proposes; independent reviewer approves before protected outcomes |
| Calibration and lossless lifecycle/event/role mapping | Learning artifacts, Evaluation qualification, FF enforcement; FF-2 before scoped use |
| Capture closure, current rights, retention and exact verifier availability | FF/Evaluation/replay owner; FFA-C03 retained, strong durability separately gated |
| Timeouts, held unknown usage, unique attempts and process limits | Runtime/gateway owner; FFA-C04 retained, import isolation is not hard cancellation |
| Final namespaced failure taxonomy and child-failure fixtures | FF-0 and FF-3; FFA-C01 retained without operator changes |
| First ACTUAL operation versus complete miniature | FF-0/1/2 staged as above; FFA-C02 sequencing clarified, empirical evidence still required |
| Consumer projection/discovery/Shell versions | Separate post-FF-2 publication acceptance; DEF-058 not globally closed |
| Recurring acquisition/Monitoring, scale, HOT and pricing | DEF-010/050/051/055/057; not silently implemented by a ledger or registry |

Advanced routing/MoE is FF-7 conditional; transfer-learning, multimodal/graph,
Monte Carlo, distributions/options/ranking and operational automation retain
their existing FF/FM/DEF gates. No new canonical deferral is required.
Sector Rotation/Signal Qualification placement remains separately unresolved;
A8 TM, A9 Scanner and A10 operations keep their major order.

## Decision and exact next prompt

**A7_ARCHITECTURE_ACCEPTED; FF0_1_ACCEPTED (foundation only)**

**TIAF A7 / FF-0.2 — CAPTURE STORE, TRUTH AND RECORDED REPLAY**

Independent architecture acceptance is complete; FF-0 planning is complete; FF-0.1 is accepted; separately authorized FF-0.2 is next.
Only a later separately
authorized bounded request may implement FF-0.2 or subsequent steps. No training, live calls, A8 work,
frozen-A6 change, new public capability, commit, tag or push.
