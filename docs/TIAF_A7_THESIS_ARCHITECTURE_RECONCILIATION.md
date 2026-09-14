# TIAF A7 — Thesis / Architecture Reconciliation

## Current navigation — A7 architecture accepted

**2026-09-15 (Asia/Kolkata): A6 FROZEN; FF ARCHITECTURE ACCEPTED;
A7 ARCHITECTURE ACCEPTED; A7 THESIS RECONCILED AS NEEDED;
A7 / FF IMPLEMENTATION NOT_STARTED; RUNTIME NOT_IMPLEMENTED.**

The [independent A7 acceptance](TIAF_A7_ARCHITECTURE_ACCEPTANCE.md) follows the
[FF integration reconciliation](TIAF_A7_FORECASTING_FRAMEWORK_INTEGRATION_RECONCILIATION.md).
The [A7 roadmap](TIAF_A7_DETAILED_ROADMAP.md) maps the old five-slice proposal
to FF-0…FF-7 within A7. FF owns forecasting contracts/runtime/composition;
Evaluation owns truth/qualification/linkage; Learning owns candidate artifacts
and lifecycle history. Independent approval and trusted COLD selection remain
separate. FM/LFDE remains an optional advanced Forecaster family.

Exact next prompt: **TIAF A7 — IMPLEMENTATION SEQUENCING AND FF-0 MINIATURE REALIZATION PLAN**.
Everything below is the preserved earlier record, including then-current status,
stage labels, findings and validation counts. Neither those historical labels
nor this navigation update authorize implementation, training, live work or A8.
No thesis DOCX/PDF, authoring assets or original finding disposition is rewritten.

## 1. Decision, authority and verified boundary

**READY_FOR_A7_ARCHITECTURE_ACCEPTANCE**

Review date: **2026-09-14, Asia/Kolkata**. This is a documentation-only
reconciliation, **not independent architecture acceptance, implementation
readiness, empirical model approval or authorization to train**.

| Item | Current status |
|---|---|
| A6 | FROZEN at `tiaf-a6-baseline` |
| A7 architecture | ARCHITECTURE RECONCILED; independent acceptance pending |
| A7 thesis | THESIS RECONCILED; unchanged non-normative creation edition |
| Next gate | ARCHITECTURE ACCEPTANCE NEXT |
| A7 runtime | NOT_IMPLEMENTED |
| A8–A10 | PLANNED; order and ownership unchanged |

HEAD and `tiaf-a6-baseline^{}` both resolve to
`6dc2ff304aae0e87540260b092919bb91e4d4189`. A5 remains at
`167c51d40985e70e422df14af4a67531f8f66a65`. Entry was **already dirty**:
13 tracked Markdown changes and 15 untracked A7 architecture/thesis files
from the preceding work, not unrelated runtime edits. Their entry hashes were
captured before editing. This pass preserves that work and changes only the
documentation listed in §8. Historical clean-entry statements in the earlier
architecture record describe that earlier pass, not this one.

The attached reconciliation brief defines this pass's scope. Embedded future
examples do not authorize runtime, model, data acquisition, broker, capability
publication or Git operations. Accepted repository ownership and frozen
contracts remain controlling. The [A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md)
now owns reconciled proposed semantics; this record owns the finding decisions.
The thesis remains explanatory, not a competing policy source.

## 2. Evidence inspected

This review inspected the actual DOCX chapter 36 finding text through its Word
XML and the PDF's rendered text/page locations, plus the substantive sections
behind the findings. It did **not** rely on the thesis creation summary alone.
Page numbers below are the PDF's one-based printed pages; chapter references
also identify the corresponding DOCX content. This pass does not claim a new
visual-layout review or re-execution of historical acceptance tests.

| Source | Inspection / conclusion used |
|---|---|
| [A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md), [five-slice roadmap](TIAF_A7_DETAILED_ROADMAP.md), [original reconciliation](TIAF_A7_RECONCILIATION_RECORD.md), [thesis record](TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md) | Read primary design and records; distinguish the original 30-source-finding audit from the 17 thesis findings reconciled here |
| [Actual thesis PDF](TI_Forecasting_Evaluation_Learning_Thesis.pdf), [DOCX](TI_Forecasting_Evaluation_Learning_Thesis.docx) | Chapter 36, pp. 36–38, all TF-01–TF-17; substantive target/PIT/split/journal/calibration/control/registry/promotion/drift/consumer/replay/attribution chapters and worked cases cited in §3 |
| [A2.9 baseline](TIAF_A2_9_DETERMINISTIC_BASELINE.md), [A2.10 replay/evaluation](TIAF_A2_10_REPLAY_VALIDATION_EVALUATION.md) | Deterministic score is not probability; immutable snapshot/run/outcome; partial observed movement is not automatically an eligible supervised label |
| [A3 architecture](TIAF_A3_ARCHITECTURE.md), forecast/confidence and governed-learning sections | Existing consumer seam does not supply a trained/calibrated forecasting implementation or justify invented probabilities |
| [A4 architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md), ownership and future-forecast sections | Arbitration and non-action gates remain A4-owned; future probability evidence needs separately compatible admission |
| [A5 architecture](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md), entry and future-context sections | Supplied position snapshot and A4 remain required; no operational truth, scheduler or new position/path model moves into A7 |
| [A6 architecture](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md), status/scope/A7 seam; [A6.4 freeze-readiness record](TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md) | Frozen deterministic long single-leg CE/PE selection; readiness record versus actual tag distinguished; no option POP or expected utility from endpoint direction |
| [Monitoring architecture](TIAF_MONITORING_ARCHITECTURE.md), ownership, evidence, persistence and cadence sections | A7 supplies pure outcome/drift needs, not recurring dispatch/acquisition; replay is not a fresh evaluation or prospective issuance |
| [Source/Provenance architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md), source authority, contradiction, clocks and revisions | Field-scoped qualification; event/publication/acquisition/admission distinctions; correction history and known future events do not become hindsight features |
| [Pluggability architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md), lifecycle, required scope, discovery and replay sections | Requiredness is per operation; HOT implies COLD implies STRUCTURAL; exact pinned replay and import isolation; no new HOT seam |
| [System](TIAF_SYSTEM_ARCHITECTURE.md), [Ecosystem](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md), [Shell](TIAF_TI_SHELL_ARCHITECTURE.md), [Capability map](TIAF_CAPABILITY_MAP.md) | Curated facade; caller-bound Shell; TI advice/TM authority/broker truth; current nine capabilities, no forecast publication |
| [Deferral register](TIAF_DEFERRAL_REGISTER.md), canonical rows and A7 disposition note | Calendar/actions/PIT, options/ranking, acquisition/monitoring, model operations and publication remain gated; 58 canonical records retained |
| [Actual A6 session contract](../src/tiaf/trade_expression/contracts.py), [admission](../src/tiaf/trade_expression/admission.py), [A2 previous-close calculation](../src/tiaf/features/_calculation.py) | `SessionWindow` provides opens/closes and qualification ref, not historical adjacent-session completeness; previous-close fallback cannot identify the next session |
| [Actual facade catalog](../src/tiaf/facade/capabilities.py) | Read-only source inspection; nine static operations, no A7 operation; no runtime import needed |

## 3. All 17 findings and dispositions

File abbreviations: **A** = [A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md);
**R** = [A7 detailed roadmap](TIAF_A7_DETAILED_ROADMAP.md);
**C** = this reconciliation record. Section references in the architecture-source
column identify the pre-existing subject and the reconciled subsection added
where needed. The two earlier records and navigation receive shared status
annotations (§8), not revised historical finding classifications.

| ID / exact thesis finding title | Thesis chapter / page; finding page | Current architecture source | Original classification | Impact if ignored | Recommended resolution | Final decision | Files updated |
|---|---|---|---|---|---|---|---|
| TF-01 — Binary target usefulness | Ch. 4, 26, pp. 6, 22–23; finding p. 36 | A §3, consumer alignment | CLARIFICATION_NEEDED | Endpoint diagnostic could be sold as demonstrated A6 improvement | Keep target; require separate qualified consumer comparison before stronger usefulness claims | CLARIFICATION_ADOPTED; no scope expansion | A, C |
| TF-02 — Next-session calendar dependency | Ch. 5, pp. 6–7; finding p. 36 | A §3 → §3.1; §7 | CLARIFICATION_NEEDED | Weekday guesses, stale schedules or silent S2 shifts alter the event | Require qualified adjacent-session artifact, official-origin coverage, revision/admission/label rules; existing A6 window is insufficient | CLARIFICATION_ADOPTED; both forecast and label qualification required | A, R, C |
| TF-03 — Calibration sample adequacy | Ch. 6, 16, 20, pp. 7–8, 15–16, 18–19; finding p. 36 | A §8 → §8.1; §12 gate contract | CLARIFICATION_NEEDED | Correlated rows or empty classes masquerade as adequate information | Pin rows, distinct sessions, classes, required cohorts, bin support and clustered precision; reviewer-approved numerical profile in A7.1 | CLARIFICATION_ADOPTED; no illustrative count becomes default | A, R, C |
| TF-04 — ECE binning and uncertainty | Ch. 6–7, 16, pp. 7–9, 15–16; finding p. 36 | A §8 → §8.1; §9 | CLARIFICATION_NEEDED | Post-test bins/weights hide calibration weakness | Predeclare fixed edges, closure rules, weights, empty/sparse-bin treatment and uncertainty; show reliability beside Brier/log-loss/ECE | CLARIFICATION_ADOPTED; exact values are policy, not thesis defaults | A, R, C |
| TF-05 — Promotion thresholds and review independence | Ch. 20, pp. 18–19; finding p. 36 | A §12 → §12.1 | CLARIFICATION_NEEDED | Metrics self-authorize or holdout reuse becomes invisible | Evaluation owner proposes; authorized reviewer approves; changed result-informed protocol needs new version and untouched later test | CLARIFICATION_ADOPTED; automatic producers cannot approve | A, R, C |
| TF-06 — Regime-stability definition | Ch. 20 and case 6, pp. 18–19, 29; finding p. 36 | A §12 → §12.1; §13 | CLARIFICATION_NEEDED | Post-hoc scope narrowing hides a required-cohort failure | Separate preregistered applicability from exploratory groups; narrowed claim needs new scope/protocol, independent test and shadow; unknown regime cannot pass | CLARIFICATION_ADOPTED; no regime engine | A, R, C |
| TF-07 — Shadow duration and information content | Ch. 21, p. 19; finding pp. 36–37 | A §12 → §12.1 | CLARIFICATION_NEEDED | Calendar duration or replay volume substitutes for prospective support | Joint time/session/mature-label/cohort/coverage gates; retained interruptions; explicit exact-artifact exit approval | CLARIFICATION_ADOPTED; duration remains pinned policy | A, R, C |
| TF-08 — Drift thresholds and delayed labels | Ch. 22, pp. 19–20; finding p. 37 | A §13 → §13.1 | CLARIFICATION_NEEDED | Missing labels imply health or stale artifacts continue silently | Define denial precedence; UNKNOWN performance is not healthy; bounded pending-label grace cannot extend expired evidence; suspend or propose retraining without replacing bindings | CLARIFICATION_ADOPTED; pure evaluator, no scheduler | A, R, C |
| TF-09 — Outcome-availability report as a first-class artifact | Ch. 12, 17, pp. 12–13, 16–17; finding p. 37 | A §4, §7, §9 → §9.1 | ARCHITECTURE_CHANGE_PROPOSED | Denominators become hard to audit; overlapping statuses can double count or erase missing cases | Separate immutable Evaluation-owned derived artifact; three per-metric buckets plus orthogonal source facets; exact manifests/revisions and scorecard link | ADOPT_WITH_CONSTRAINTS | A, R, C |
| TF-10 — Corporate-action exclusions and selection | Ch. 8, 13 and case 10, pp. 9–10, 13, 30–31; finding p. 37 | A §5 → §5.1; §7.1; §9.1 | CLARIFICATION_NEEDED | Informative censoring disappears or hindsight adjustment contaminates features | Preserve effective and known-at clocks, conditional coverage and later revision; ambiguous labels ineligible; no hindsight action adjustment | CLARIFICATION_ADOPTED; unadjusted same-basis v1 retained | A, R, C |
| TF-11 — Reproducibility tolerance | Ch. 29, pp. 24–25; finding p. 37 | A §14 | CLARIFICATION_NEEDED | Numerically close refits acquire old identity or admission flips pass tolerance | Exact recorded replay; declared-environment inference; separate numeric/refit comparisons, transformed coefficient basis and exact status boundaries | CLARIFICATION_ADOPTED; no universal bitwise refit promise | A, R, C |
| TF-12 — Model-registry scope | Ch. 19, pp. 17–18; finding p. 37 | A §12, §16 | NO_CHANGE | Registry membership might be confused with approval/publication | Retain local immutable manifests and append-only lifecycle, exact pins and COLD activation | NO_CHANGE; existing scope sufficient | C |
| TF-13 — Feature-attribution presentation | Ch. 30, p. 25; finding p. 37 | A §14 | IMPLEMENTATION_DETAIL_ONLY | Logit contributions become probability points or causal claims | Later allowlisted renderer reconciles intercept plus transformed contributions to captured raw logit, then separately displays calibration | IMPLEMENTATION_DETAIL_ONLY; assigned to A7.3, not implemented | A, R, C |
| TF-14 — A4/A5/A6 admission | Ch. 24–26, pp. 21–23; finding p. 38 | A §11 | NO_CHANGE | Forecast availability bypasses parent ownership or missing prerequisites | Retain no automatic v1 influence; restate future target/model/calibration/PIT/replay/freshness/consumer-policy admission intersection | NO_CHANGE to consumer semantics; boundary made explicit | A, C |
| TF-15 — Forecast staleness | Ch. 5, 22, pp. 6–7, 19–20; finding p. 38 | A §3, §13 → §13.2 | CLARIFICATION_NEEDED | Tomorrow's horizon implies indefinite freshness; delayed issue resets ages | Half-open finite validity ending at earliest forecast/input/approval/calibration/health/target bound; trusted consume time and revocation checks | CLARIFICATION_ADOPTED; no backdating or refreshed age from replay | A, R, C |
| TF-16 — Advanced models and broader targets | Ch. 35, p. 35; finding p. 38 | A §3 later families; §18; deferral note | DEFER | Illustrated broad ideas silently become required v1 or disappear from roadmap | Retain broad targets/families/operations as explicitly gated carry-forwards, without duplicate deferral IDs | DEFER_RETAINED | C; scoped deferral-register note |
| TF-17 — Independence of the deterministic path | Ch. 2, 17 and case 8, pp. 4–5, 16–17, 30; finding p. 38 | A §2, §11, §17 | NO_CHANGE | A7 failure mutates valid baselines, or fallback rescues invalid ones | Preserve original A2/A4/A5/A6 values/fingerprints and their own required evidence; test both directions | NO_CHANGE; regression obligation retained | C |

Accounting: **17/17**; **11 CLARIFICATION_NEEDED**, **1 ARCHITECTURE_CHANGE_PROPOSED**,
**1 IMPLEMENTATION_DETAIL_ONLY**, **3 NO_CHANGE**, **1 DEFER**. All eleven
clarifications are adopted in proposed normative Markdown. The sole finding
classified ARCHITECTURE_CHANGE_PROPOSED is adopted with constraints. The named
calendar input contract resolves an already-required qualification dependency
under TF-02; it adds no calendar service or new target. No finding is dropped.
No whole finding is rejected; unsafe interpretations and scope expansions are
explicitly disallowed below. The historical thesis proposal was not adopted
during creation; its adoption occurs in this separate record.

## 4. TF-09 design decision and denominator proof

**ADOPT_WITH_CONSTRAINTS.** The benefit is an independently fingerprinted,
testable account of what the scorecard measured. The report is derived from
immutable source records; it neither owns new outcome truth nor approves models.

| Benefit / risk | Resolution |
|---|---|
| Denominator transparency and precision/coverage | Preregister expected population, metric arms, dedupe/weighting; retain unsuccessful requests and gaps |
| Audit/replay and revised outcomes | Exact journal/forecast revisions, as-known cutoff and population-report fingerprint; no latest-record lookup |
| Dataset versus model quality | Disclose qualification, availability, label maturity and model participation separately |
| Taxonomy complexity / duplicate statuses | Exactly INCLUDED, EXCLUDED, NOT_EVALUABLE **per observation × metric arm**; other meanings are source facets |
| Unclear ownership / lifecycle duplication | Evaluation alone emits immutable projection; no new service, mutable row lifecycle, registry or public operation |
| Extra artifact / hash-cycle burden | Scorecard references report fingerprint; report references only inputs/policies, not scorecard fingerprint |

```text
Preregistered population + request aliases + metric/comparison policy
                          ↓
Pinned forecast participation + operation facts + exact journal revisions
                          ↓
EvaluationPopulationDispositionReport [Evaluation owns; immutable]
  per observation × requested metric arm:
       INCLUDED | EXCLUDED | NOT_EVALUABLE
  independent facets: abstained, rejected, ineligible, missing, revised ...
                          ↓ fingerprint checked by
EvaluationReport [metrics + uncertainty + control comparisons]
                          ↓ evidence only
Separate authorized review [never approval by the report itself]
```

Illustrative disposition examples—not observed market results:

| Source situation | Request coverage | Brier metric | What must remain visible |
|---|---|---|---|
| Model abstains, qualified endpoint exists | INCLUDED as a requested case; forecast unavailable | NOT_EVALUABLE: no admitted probability | Abstention and factual label are independent |
| TM rejects an operation, admitted forecast and label exist | INCLUDED | INCLUDED | Rejection is not a bad forecast, fill or loss |
| Outcome still pending after issue | INCLUDED | NOT_EVALUABLE: qualified label missing | Maturity/deadline, not synthetic class zero |
| Later eligible correction J2 replaces J1 for a new report | INCLUDED | INCLUDED using exactly J2 | J1 remains replayable in old reports; REVISED is a relationship |
| Predeclared out-of-scope observation | Remains in total request accounting | EXCLUDED under the pinned metric-scope rule | No retrospective denominator shrink |

These examples apply only where the relevant coverage metric's own prerequisites
are satisfied. Request counts and deduped observation counts are separate;
facet counts can overlap and are not added as a partition. A missing source
must be accounted against its expected ID. Unprovable population mapping fails
report integrity; it cannot support a complete-denominator or approval claim.
Conflicting captures are not merged by symbol or best prediction. All request
usage/failures remain visible even when exact duplicates count once statistically.

The detailed contract, reason precedence and zero/partial/failed-report behavior
are in architecture §9.1. Contract in A7.1 → emission A7.2 → replay A7.3 →
display A7.4 fits the existing sequence; it is not an extra milestone.

## 5. Normative boundary verdicts

The references in this section are to the reconciled [architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md),
not new runtime claims.

| Topic | Reconciled verdict / normative location |
|---|---|
| Three layers | Forecasting estimates; Evaluation measures; Learning proposes new artifacts. Evaluation cannot authorize promotion; Forecasting cannot train itself; explicit reviewer/operator approval and new COLD binding govern later use (§2, §12). |
| Initial target | Keep only `equity.next_session_close.return_gt_zero/1.0`: qualified NSE cash-equity S1 close strictly above known completed S0 close. Exact same-basis finite positive source prices; equality or decline = 0; absence/invalid price is not zero. No total return, executable entry, option POP, magnitude, path or utility claim (§3). |
| Calendar/session | Require `QualifiedSessionSchedule`: official-origin venue/segment schedule and exceptions, ordered completeness proving adjacency, qualification/revision/clock/fingerprint lineage. No current feed is certified. A6 `SessionWindow` and previous-close support do not suffice. Missing proof blocks both forecast and supervised-label admission. Unresolvable S1 is unsupported; known S1 lacking proof abstains. Post-issue material change retains run and appends window CENSORED / label INELIGIBLE; never retarget S2 (§3.1). |
| PIT/leakage | Distinct event, publication/feature availability, acquisition/admission, cutoff/issue, fit cutoff/completion, outcome/label availability, action effective time and dated universe membership. Realized post-cutoff facts, future-survivor knowledge and hindsight adjustments forbidden. Known future announcements retain announcement/effective distinction, not a new v1 feature. Later-acquired history is research-only unless separately PIT-qualified; incomplete lineage fails closed (§5.1). |
| Dataset splits | Chronological TRAIN/CALIBRATION/VALIDATION/TEST, walk-forward and prospective SHADOW; row/session separation within each fold, boundary purging for overlapping/unmatured dependencies, mandatory full-target-session embargo for v1. Fingerprint split definition and realized membership; cross-fold reuse only forward with true availability. Final test stays untouched; random shuffle is not default (§6.1). |
| Calibration | Frozen estimator plus separate held-out sigmoid calibration, then independent validation/test. Raw logit/score, even logistic output, is not admitted calibrated evidence merely because it lies in [0,1]. Model/calibrator/transform/data/split/policy pins, support, approval, current health, validity and replay are required. Reliability/Brier/log-loss/ECE each visible; stale/drifted calibration cannot silently continue (§8.1, §13). |
| Sample size/ECE | Gate obligations are architecture; actual rows/sessions/classes/cohorts, clustered uncertainty, numerical edges/weights/support and bounds are reviewer-approved policy frozen in A7.1; plotting is implementation. Fixed finite edges cover [0,1], left-closed/right-open except final endpoint; empty bins have zero ECE weight and UNKNOWN reliability, sparse required support fails. No thesis example becomes default (§8.1, §12). |
| Outcome journal | Separate forecast generation, downstream operation, window state, label eligibility and per-measure observability. Ignored is NOT_TAKEN, unknown is not TAKEN; rejected/untraded does not equal failed forecast. Immutable predecessor-linked corrections and as-known exact revision references; no old feature/run/report mutation (§7.1). |
| Label governance | Strict above = 1, equal/below = 0 only when qualified. Missing = PENDING until pinned deadline, then censored/unobservable with no number. Invalid = INELIGIBLE; unresolved action/session = AMBIGUOUS and barred from supervised metrics. Revision is a link, not a new binary class; later availability cannot enter earlier folds (§7). |
| Benchmarks | Training-only historical prior mandatory, fixed 0.5 diagnostic mandatory; persistence contextual with predeclared mapping. Logistic is initial candidate/reference, not its own hurdle; later complex families must also beat it. Paired held-out Brier improvement needs preregistered uncertainty evidence and log-loss non-inferiority, calibration/coverage/cohort gates. A2/A4, A5/A6 and human comparisons are contextual only where estimands/methods match; no ordinal-score-to-probability conversion (§9, §12). |
| Promotion | No leakage, adequate independent support, calibrated OOS/control improvement, stability, reproducibility, rights/budgets, shadow and explicit approval. Authorized reviewer, not automatic evaluator, approves protocol and artifact. Result-driven changes require new versions and untouched later evidence; no arbitrary numerical threshold chosen here (§12.1). |
| Shadow | Prospective requests/inputs/controls/forecasts and failures, mature label revisions, usage, drift, coverage and matched metrics; exact model/calibrator lineage. Duration plus distinct sessions/classes/cohorts/maturity/interruptions are policy. Replayed histories do not count. Separate approved exit; neither shadow nor advisory v1 authorizes A4/A5/A6 or TM (§12.1). |
| Drift | Separate feature, calibration, performance, regime and coverage drift. Pure pinned evaluator may warn, deny scope, suspend admission or recommend retraining. Security/integrity failures retain outer causes; unavailable/expired approval or health is UNAVAILABLE; unsupported target is UNSUPPORTED; request evidence/regime gaps can ABSTAIN. Pending labels mean UNKNOWN performance, not health; grace is bounded by valid predeclared policy and existing approval/health support. No scheduler, auto-refit or silent continuation (§13.1). |
| Forecast staleness | Nonempty half-open `[issued_at, valid_until)`, ending no later than earliest forecast TTL, input freshness, model approval, calibration review, health expiry and target close. Initial issue must precede S1 open with original cutoff. Trusted later consume time checks current authority/revocation/health and original use-by; delay/replay/renewal cannot reset input ages or extend old evidence. Expired forecasts remain historical only (§13.2). |
| Registry | No change: local immutable manifests plus append-only lifecycle. Model ID/version, target/horizon/cohort, feature schema, data/split fingerprints, calibrator, metrics/control refs, code/dependencies, seeds, approval scope/state/events, validity and checksum. Checksum is not approval/authenticity; no mutable latest model, service or public promotion (§12). |
| Reproducibility | Exact recorded replay without inference; exact canonical inference on declared supported environment. Cross-environment numeric comparison and refit are separately reported, with changed checksums retained. Proposed `1e-10` probability / `1e-8` metric bounds still need A7.1 fixture qualification; transformed-coefficient absolute/relative/near-zero rules must be pinned. Any class/admission/abstention flip fails regardless of small difference. All seeds, order, libraries, hardware and threading recorded; no universal bitwise refit guarantee (§14). |
| Attribution | Intercept + coefficient × actual train-transformed feature explains raw logit; calibration is separate. Sufficient for initial trace, not additive probability points or causality. Later A7.3 renderer fixtures check captured fields; no invented missing-feature contribution or new explanation model. SHAP/heavy explainers deferred (§14). |
| A4 seam | No automatic v1 influence. Future exact subject/target/horizon/applicability, approved model/calibrator, calibration, PIT/provenance, replay, current health/freshness and separately accepted consumer-policy gates all intersect. A4 arbitration/non-action survives without A7; no rescoring or authority transfer (§11). |
| A5 seam | Same future evidence gates; supplied position truth and A4 remain required. A5 owns position advice, TM operations; v1 endpoint estimate does not imply target/stop/path/deterioration models or a monitoring daemon (§11). |
| A6 seam | Deterministic candidate validity and ranking remain untouched and independent. Only a later accepted overlay may compare A6-produced valid IDs. Direction probability is never option POP, expected option return or sizing/operational permission (§3, §11). |
| Rejected/counterfactual | Qualified future underlying endpoint may be observable without a trade. Hypothetical option fill/P&L is separately NOT_OBSERVABLE/UNKNOWN unless its own method/evidence is accepted; v1 implements no execution counterfactual. Population report retains these distinct gaps (§7.1, §9.1). |
| Corporate actions | Effective and knowledge/availability clocks stay separate. Same-basis unadjusted v1 excludes ambiguous/action-affected coverage explicitly; later discovery can revise eligibility, never original features. PIT-safe adjustment needs a separately accepted vintage/formula policy and is not adopted now. Conditional population and informative censoring prevent broad representativeness claims (§5.1, §7.1, §9.1). |
| Learning lifecycle | Snapshot → features/labels/splits → train → calibrate → validate/test/benchmark → explicit shadow approval → prospective shadow → explicit advisory approval/new COLD binding → assess drift/validity → suspend/retire or propose new training version. No online self-modification (§12). |
| Capability surface | Future `forecast.assess` public candidate; `forecast.evaluate` engineering; `model.list`/`model.describe` engineering inspection only. Additive replay kinds require acceptance. No publication, promotion command or population-report operation now; existing nine IDs unchanged (§16). |

### Pluggability verdict

Requiredness is per operation, not global installation. **All eight components
are STRUCTURAL; allowed selections are COLD; none is HOT** (architecture §16).

| Component | Required scope / absence behavior |
|---|---|
| Feature snapshotter/projector | Required for chosen forecast schema; optional to deterministic TI; no fabricated feature on absence |
| Labeler | Required for supervised training/evaluation; not for inference or recorded replay |
| Dataset splitter | Required when constructing supervised partitions; pinned algorithm/policy; absent definition blocks qualification, no shuffle fallback |
| Trainer | Only explicit training jobs; optional fit dependency cannot leak into Core/specialists/Shell/replay |
| Calibrator | Fit adapter for calibration work and exact declarative mapping for admitted probability; absent required mapping cannot be omitted |
| Evaluator | Required for scorecards/gate evidence, never empowered to approve its own result |
| Model runtime | Required for new inference/pinned verification; not needed to reconstruct recorded results |
| Registry | Required exact artifact/approval resolution for new admission; replay embeds its required historical records |

R1 required scope, R2 descriptive discovery, R3 exact composition/pinning,
R4 optional imports and R5 sealed trusted ownership stay intact. Current R5
selectors do not already implement A7. No HOT swap, universal loader, SDK
dependency, service or publication is added in this pass.

## 6. Roadmap, deferrals and rejected interpretations

Retain **A7.1 → A7.2 → A7.3 → A7.4 → A7.5**. The
[updated roadmap](TIAF_A7_DETAILED_ROADMAP.md) places the new population contract
and clarified proof/policy requirements within those five slices, adds the
corresponding hardening cases and preserves separate engineering versus
empirical model readiness. No sequencing defect requires a new slice.

| Carry-forward | Existing ownership / unchanged revisit gate |
|---|---|
| Qualified calendar, corporate actions and historical PIT | DEF-007/013/049; bounded input contracts do not close source/service or adjusted-history work |
| Ensembles, heavy/deep/RL families and optimization | A7 broader charter; DEF-024 optimization obligations retained; separately demonstrated incremental value, cost and qualification; not mandatory v1 |
| Broad distributions, option/path probabilities and expected utility | DEF-044 with historical derivative dependencies DEF-014/040–043; separate labels/data/models/consumer acceptance |
| Cross-sectional/cross-candidate ranking | DEF-053, separate evaluated objective/cohort/tie policy; endpoint forecast is not a ranking engine |
| Signal Qualification / Sector Rotation integration | Existing separate TBD workstreams; own architecture/PIT/evaluation/publication gates (including DEF-058 where applicable); no speculative A7.x renumbering |
| Autonomous learning / production model operations | No v1 autonomous updates; manual governed lifecycle only. Durable operations, activation and resource/pricing obligations remain separate (DEF-010/050/051/055/057); none is globally closed |
| Monitoring Runtime and scheduled outcome acquisition | DEF-010/051, with scale under DEF-050; A10 or separately authorized operational slice, not a pure A7 evaluator |
| HOT replacement / new peer or facade exposure | DEF-057/058; no replacement/publication merely from metadata or local registration |

The deferral register receives only an A7 scoped disposition note. **No new,
closed, renumbered or reclassified canonical entry**; all 58 canonical row texts
remain unchanged. Broad research examples remain visible rather than silently
removed from the major milestone charter.

Disallowed interpretations: expand v1 to make A6 look useful; treat weekday or
two-date input as calendar proof; calibrate from training/test leakage; lift
thesis sample counts into production; shrink scope after poor outcomes without
fresh independent evidence; merge journal statuses into metric buckets; pretend
replay is shadow; tolerate boundary-flipping verification; infer causal/option
profit from direction; install a scheduler, model service or HOT replacement.
No complete thesis finding is rejected; TF-16 is explicitly deferred and TF-13
remains later implementation detail.

## 7. Residual decisions and independent acceptance focus

| Remaining choice / evidence | Owner and blocking gate |
|---|---|
| Is an eligible PIT dataset and official-origin calendar/action supply actually available? | Evidence owner must demonstrate rights, source completeness, vintages and dated universe. NOT_ESTABLISHED; blocks affected empirical admission, not this documentation verdict |
| Exact small feature IDs, native artifact schema and optional fitting library/version | A7.1/2 engineering review; fix before fitting, without A2 recalculation or tuning |
| Actual sample/uncertainty/ECE/cohort/improvement/drift/shadow parameters | Evaluation owner proposes; authorized reviewer approves process at architecture acceptance and concrete profile in A7.1 before real experiments/protected results |
| Qualified environment, coefficient tolerance and bounded machine budgets | Engineering/operator profile and synthetic numerical fixtures; unknown/unsupported reproduction remains explicit |
| Future A7 evidence/consumer projection and publication versions | A7.3/4 and separate consumer-policy acceptance; no implicit conversion to legacy forecast placeholder, no automatic A4/A5/A6 use |

These are explicitly owned implementation/empirical gates, not missing choices
about this pass's architecture boundary. Independent acceptance should challenge
calendar/revision and health precedence, per-metric population counts, holdout
independence, finite validity, exact-versus-numerical replay and consumer
non-interference. Rejection of every real candidate remains a valid engineering
result; no qualified real model, improved accuracy or trading value is claimed.

## 8. Files changed and artifact preservation

Changes **relative to this pass's entry**, not all prior A7 work:

| Files | Change |
|---|---|
| `docs/TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md` | New complete 17-finding decisions, source/page evidence, boundary verdicts and validation record |
| `docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md` | Qualified calendar/PIT/split/journal/calibration/protocol/shadow/drift/staleness/reproduction clarifications; constrained population report; explicit splitter and consumer boundaries |
| `docs/TIAF_A7_DETAILED_ROADMAP.md` | Requirements assigned to unchanged five slices; architecture acceptance next |
| `docs/TIAF_A7_RECONCILIATION_RECORD.md`, `docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md` | Current follow-up annotation; original evidence, decisions, findings and creation hashes remain historical |
| `README.md`, `docs/MILESTONES.md`, `docs/IMPLEMENTATION_ROADMAP.md`, `docs/TRADINGINTELLIGENCE_ROADMAP.md`, `docs/TIAF_IMPLEMENTATION_TARGETS.md` | Current status and exact next gate synchronized; no major renumbering or runtime claim |
| `docs/ARCHITECTURE.md`, `docs/TIAF_CAPABILITY_MAP.md`, `docs/TIAF_SYSTEM_ARCHITECTURE.md`, `docs/TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md`, `docs/TIAF_THESIS.md` | Reconciled design navigation, proposed-only surface and unchanged owner boundaries |
| `docs/TIAF_DEFERRAL_REGISTER.md` | Scoped A7 disposition note only; canonical records unchanged |
| `docs/README_TBD_DESIGN_NOTES.md`, `docs/TBD_TI_FORECASTING_ENSEMBLE_LEARNING_ARCHITECTURE.md` | Idea-cache header/index points to reconciled design, not an accepted implementation |

Total: **18 Markdown files**, including this new record. No runtime source,
tests, scripts, dependencies, frozen A6 documents, model artifact or thesis
authoring/build/chart asset is changed by this pass.

The DOCX/PDF remain the **39-page creation edition** (36 chapters + appendix,
25 figures, 30 editable tables, 10 cases, 29 FAQ answers, 17 findings). Their
statement that TF-09 was not adopted *during creation* is historically accurate.
The record annotations distinguish the later decision; no factual inconsistency
requires rerendering. Creation counts are not newly run visual acceptance.

| Unchanged artifact | SHA-256 |
|---|---|
| `docs/TI_Forecasting_Evaluation_Learning_Thesis.docx` | `c3b955c2f1abb2d99bb651a8b7d585062d3a5b0e0cc25b1a543fdfc46cd771f2` |
| `docs/TI_Forecasting_Evaluation_Learning_Thesis.pdf` | `3ea52729952d190501da5e810455cf134618c48219918c9910cfd89b02075721` |

## 9. Validation and next gate

| Check | Result |
|---|---|
| `git diff --check` | PASS; no whitespace errors |
| Untracked Markdown whitespace | PASS; all 6 untracked Markdown files additionally checked using `git diff --no-index --check /dev/null <file>` |
| Existing local-link validator, worktree mode | PASS: **791 local links across 19 Markdown files**, including heading anchors; no network requests |
| Finding matrix | PASS: **17 ordered unique IDs**, 8 required columns each; exact titles and original classifications matched against actual DOCX paragraphs; 11/1/1/3/1 classification totals preserved |
| Canonical deferral integrity | PASS: **58/58** canonical rows byte-for-byte equal to task entry, including IDs and statuses; no additions, closures or duplicates |
| Current status/navigation | PASS: **16** current documents carry reconciled/unimplemented status with no obsolete A7 next-gate wording; exact next title in **9** current queue/design documents; **2** historical records have explicit current preambles |
| Roadmap | PASS: exactly A7.1–A7.5 in unchanged order; A8–A10 remain future |
| File-scope/hash audit | PASS: **18 Markdown files changed** relative to entry (17 updated + 1 new); all **11** prior thesis binary/source/build/chart/page-map files unchanged; no removed entry file |
| Thesis artifacts | Entry SHA-256 values above unchanged; no rebuild, rerender or new visual acceptance required or claimed |
| Runtime/catalog/baselines | Source/tests/scripts/dependencies and frozen A6 files unchanged; static catalog remains **9**; HEAD/A6/A5 tag targets unchanged |

The existing link check was invoked without its full document-render validation:

```bash
.venv/bin/python -B - <<'PY'
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "a7_docs_validation", Path("docs/handbooks/a7_forecasting/validate_handbook.py")
)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print(module.validate_links(True))
PY
git diff --check
```

The first attempt using bare `python` could not start because that executable
is absent from PATH; the repository `.venv/bin/python` succeeded. The first link
check found one incorrect A4 document target in this new record; it was corrected
and the complete check then passed. An initial broad status assertion also led
to making `RUNTIME NOT_IMPLEMENTED` explicit in the TBD navigation row. These
were documentation/check-environment issues, not runtime defects or blockers.

Additional read-only assertions checked the finding table against DOCX XML,
canonical register rows against entry, status/next-gate strings, five roadmap
headings, the nine static catalog declarations by AST, and file hashes/Git scope.
No full pytest/compile/lint/type suite was needed or run for this documentation-only
pass; historical test counts are not presented as current results.
**Zero model training and zero live provider/model/broker calls.** No commit,
tag or push; no new runtime, qualified dataset or empirical result.

**Exact next prompt title:**
**TIAF A7 — FORECASTING, EVALUATION & LEARNING ARCHITECTURE ACCEPTANCE**.

This is readiness for **independent review**, not permission to implement A7.1.
