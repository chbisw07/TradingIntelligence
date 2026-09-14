# TIAF A7 — Forecasting, Evaluation & Learning Thesis Creation Record

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

## Subsequent reconciliation — current navigation

All [17 thesis findings are now reconciled](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md)
in the [proposed normative architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md).
Current status: **A7 ARCHITECTURE RECONCILED; THESIS RECONCILED;
ARCHITECTURE ACCEPTANCE NEXT; RUNTIME NOT_IMPLEMENTED**. A6 remains FROZEN.
TF-09's separate Evaluation-owned population report is adopted with constraints
by that subsequent pass, not by thesis creation. No actual factual inconsistency
requires changing the DOCX/PDF; they and their authoring assets remain byte-for-byte
the creation edition. Draft/then-next wording, source hashes, inventory and
validation counts below are historical creation evidence, not current acceptance.

Current exact next prompt:
**TIAF A7 — FORECASTING, EVALUATION & LEARNING ARCHITECTURE ACCEPTANCE**.

## Historical creation checkpoint

Date: **2026-09-14, Asia/Kolkata**. Documentation-only creation checkpoint.

Decision: **READY_FOR_A7_THESIS_ARCHITECTURE_RECONCILIATION**.
This is thesis readiness, **not** architecture acceptance, empirical model
approval, runtime implementation or authorization to begin A7.1.

## Deliverables and authority

- [Complete reference PDF](TI_Forecasting_Evaluation_Learning_Thesis.pdf)
- [Editable Word edition](TI_Forecasting_Evaluation_Learning_Thesis.docx)
- [Editable narrative source](handbooks/a7_forecasting/handbook.md)
- [Documentation-only DOCX builder](handbooks/a7_forecasting/build_handbook.py)
- [Synthetic chart source/data builder](handbooks/a7_forecasting/build_charts.py)
- [Document validator](handbooks/a7_forecasting/validate_handbook.py)
- [Rendered chapter page map](handbooks/a7_forecasting/page_map.json)
- [Calibration SVG](handbooks/a7_forecasting/assets/calibration.svg) /
  [PNG](handbooks/a7_forecasting/assets/calibration.png)
- [Precision/coverage SVG](handbooks/a7_forecasting/assets/coverage.svg) /
  [PNG](handbooks/a7_forecasting/assets/coverage.png)

The thesis is a non-normative conceptual reference. The primary A7 architecture
remains the controlling **draft**. Examples do not supply policy defaults,
training results, live market observations or a forecast guarantee. All model
names, symbol scenarios, cohorts, numerical observations and approvals are
invented teaching material. No models were trained or promoted.

The separate clocks and the strict next-session target are explained without
expanding them into option profit probability, target-hit probability, five-day
return, intraday direction or expected monetary return. A2/A4/A5/A6 controls and
TM/broker authority remain unchanged. The nine-operation catalog is unchanged.

## Edition inventory

| Item | Verified count / treatment |
|---|---|
| Rendered PDF pages | **39**, A4, tagged PDF 1.7; title, two contents pages, body and appendix |
| Chapters | **36**, plus **1 appendix**; all linked in the contents with rendered page numbers |
| Authoring-source words | **15,394**, whitespace-delimited, including Markdown/figure/table markup |
| Numbered figures | **25** |
| Editable Word tables | **30 total**: 23 numbered table/flow figures plus 7 other reference tables |
| Statistical charts | **2** embedded PNGs, each with editable SVG and explicit synthetic data in the builder |
| Worked scenarios | **10**, with context/target/window, model/version or absence, evidence, disposition and downstream consequence |
| FAQ answers | **29** |
| Thesis findings | **17**, classified below; none applied to architecture |

The diagrams are editable Word tables/flow boxes, not flattened screenshots of
text. The two plots have labeled axes and conspicuous illustrative-data notices.
SVG/data can be edited and regenerated; PNGs are the Word-compatible renditions.
Body type is 11 pt, table text 9.5 pt, with fixed-width grids and non-splitting
rows. Headers repeat on reference tables that continue onto another page.
Editing the DOCX in another application can change pagination; use the supplied
PDF as the reference edition and regenerate its contents if reflow changes.

## Sources and source preservation

Primary sources, read as the existing uncommitted architecture-pass snapshot:

| Source | SHA-256, unchanged from task entry |
|---|---|
| [A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md) | `a50328a65d37b8ce96baf53aadba4bb10a0882f7c8dfe30f5797965aa45828e0` |
| [A7 detailed roadmap](TIAF_A7_DETAILED_ROADMAP.md) | `061bbef29f90dc2fcd19a7285d678d0d630aba2ae445a51dc7a17573e3bb8655` |
| [A7 architecture-pass reconciliation](TIAF_A7_RECONCILIATION_RECORD.md) | `ff9cedf7705a4ef09cc1a6786a371aee4c7ef93f3210fdbb58ea9f016c8eac8a` |

Those three documents were **not edited** during thesis creation. Their
architecture-pass “thesis next” statements remain historical checkpoint text;
this record and current navigation advance that checkpoint to thesis CREATED.
Their 30 architecture-pass findings are distinct from this thesis's 17 findings.

Supporting repository sources:

| Source group | Sources and use |
|---|---|
| Deterministic controls and evaluation | [A2.9](TIAF_A2_9_DETERMINISTIC_BASELINE.md), [A2.10](TIAF_A2_10_REPLAY_VALIDATION_EVALUATION.md): scores are not probabilities; preserved runs and subsequent observations |
| Specialist/orchestration/replay | [A3 architecture](TIAF_A3_ARCHITECTURE.md), [A3.8](TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md), [A3.10](TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md): independent evidence, bounded orchestration, recorded replay and costs |
| Consumer ownership | [A4](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md), [A5](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md), [A6](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md), [A6.4 closure](TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md): preserved advice, admission, ranking and authority |
| Prior reference presentation | [A6 thesis record](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_THESIS_RECORD.md), [A6 editable handbook](handbooks/a6_trade_expression/handbook.md) and its local builder/validator: non-normative reference and OOXML rendering approach; none modified |
| Trust and operations | [Source/provenance](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md), [Monitoring](TIAF_MONITORING_ARCHITECTURE.md), [Pluggability](TIAF_PLUGGABILITY_ARCHITECTURE.md): PIT/source clocks, explicit absence, separate scheduler and COLD binding |
| Product boundary | [System](TIAF_SYSTEM_ARCHITECTURE.md), [Ecosystem](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md), [Capability Map](TIAF_CAPABILITY_MAP.md), [Deferral Register](TIAF_DEFERRAL_REGISTER.md), [TI Shell](TIAF_TI_SHELL_ARCHITECTURE.md): runtime versus future design; no new operations or execution |

Three primary educational references were consulted on 2026-09-14:
[scikit-learn calibration](https://scikit-learn.org/stable/modules/calibration.html),
[Brier score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html),
and [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html).
They support metric/split explanations in Chapters 6, 7 and 10, not TI policy,
exchange rules, selected library versions or evidence of model success. No live
provider, model or broker calls were made. Educational web reads are not live
market validation.

## Chapter structure and coverage

| Chapter | Starts on page | Main teaching purpose |
|---|---:|---|
| 1. Why A7 Exists | 4 | Forecasting/evaluation/learning are three distinct jobs |
| 2. Deterministic vs Probabilistic Intelligence | 4 | Overlay and retained controls, not replacement |
| 3. What Is a Forecast? | 5 | Named event, applicability and evidence lineage |
| 4. Forecast Targets | 6 | Exact strict endpoint comparator; missing is not zero |
| 5. Forecast Horizons | 6 | Supplied session/calendar, reference and validity clocks |
| 6. Scores, Probabilities and Calibration | 7 | 0.70/0.69 versus 0.90/0.62; ranking is not calibration |
| 7. Why Accuracy Is Not Enough | 8 | Brier, log loss, AUC, reliability, coverage and utility |
| 8. Point-in-Time Data | 9 | Captured-as-known evidence and eligibility |
| 9. Leakage | 10 | Future high, survivor universe and future adjustment knowledge |
| 10. Dataset Splits | 10 | Distinct fit/calibration/selection/test rights |
| 11. Walk-Forward Evaluation | 11 | Expanding/rolling folds and purge/embargo |
| 12. Outcome Journal | 12 | Taken, rejected, unavailable and corrected outcomes |
| 13. Label Governance | 13 | Same-basis qualification and immutable revisions |
| 14. Baselines and Controls | 14 | Matched cohorts; no probability invented from A2 scores |
| 15. Initial Model Families | 14 | Small logistic/prior foundation; advanced families deferred |
| 16. Calibration Methods | 15 | Held-out sigmoid; fitting is not successful validation |
| 17. Abstention and Precision/Coverage | 16 | Explicit missing support and honest denominators |
| 18. Economic Objective / Expected Utility | 17 | Payoff/risk consequences differ from win rate |
| 19. Model Registry | 17 | Local immutable manifests, not an automatic approval service |
| 20. Promotion Lifecycle | 18 | Eligibility, review and explicit approval are distinct |
| 21. Shadow Mode | 19 | Prospective non-influencing records and failure coverage |
| 22. Drift and Degradation | 19 | Feature/performance/coverage drift and suspension |
| 23. Retraining Governance | 20 | Complete lifecycle and four clocks; no silent updates |
| 24. How A7 Helps A4 | 21 | Optional future evidence, no automatic arbitration override |
| 25. How A7 Helps A5 | 22 | Position advice owner retained; initial target is not path risk |
| 26. How A7 Helps A6 | 22 | Frozen candidates/rank; underlying direction is not option POP |
| 27. Scanner / Signal Qualification Seam | 23 | Acyclic future meta-label seam, not a new scanner |
| 28. Sector Rotation / Monitoring Seam | 23 | Separate context/analysis/operations ownership |
| 29. Replay and Reproducibility | 24 | Recorded replay versus pinned verification versus retraining |
| 30. Explainability and Non-Causality | 25 | Actual numerical attribution, not causal claims |
| 31. Cost, Privacy and Security | 25 | Local compute is not free; rights, pinning and safe loading |
| 32. Failure Modes | 26 | Absence/error matrix, not favorable defaults |
| 33. Worked Examples | 27 | Ten full decision stories |
| 34. Frequently Asked Questions | 31 | All 29 required questions answered |
| 35. Future Evolution | 35 | Proposed A7.1–A7.5 and preserved A8–A10 boundaries |
| 36. Thesis Findings for Architecture Reconciliation | 35 | Seventeen separately classified questions/dispositions |
| Appendix A. Sources, Glossary and Reading Guide | 38 | Source authority and practical interpretation checklist |

## Figures and substantive treatment

Figures 01–04 cover the three layers, deterministic/probabilistic views, forecast
identity and exact clocks. Figure 05 is the synthetic calibration plot; 06–08
cover metrics, PIT and the three leakage traps. Figures 09–14 cover chronological
partitions, forward folds, outcome journal, labels, controls and calibration.
Figure 15 plots invented precision versus coverage. Figures 16–21 cover registry,
promotion, shadow, drift, governed learning and the end-to-end lifecycle. Figures
22–25 show A4/A5/A6 ownership, acyclic future context/operations, replay lineage
and proposed evolution. The prose explains the assumptions and limits around
each diagram; the plots do not replace statistical qualification.

Calibration uses two invented 1,000-row cohorts: 0.70 with 690 positives and 0.90
with 620 positives. The book explains dependence, sparse bins, regime failures,
ECE sensitivity and why ranking can remain decent while probabilities are
unsafe. It selects no numerical calibration, promotion or drift policy.

Leakage examples include a 10:00 prediction using the 11:00 high, a historical
universe built from later survivors, and adjustments using future corporate-action
knowledge. The first is explicitly an out-of-v1 intraday teaching example. Not
every adjusted historical value is inherently leakage; available vintages and
transformation dependencies matter. Leaked evaluation is invalid, not a modest
score penalty.

Walk-forward separates training, held-out calibration, validation and test,
groups shared sessions, respects label maturity and explicitly purges/embargoes
overlap. The final holdout is not recycled as repeated independent evidence.
Outcome journals retain taken/rejected/unavailable/corrected states without
inventing counterfactual fills, labeling missing data zero or overwriting history.

Learning produces a new pinned artifact through offline fit/calibrate/evaluate,
review, prospective shadow and explicit promotion. Registration is not approval;
successful training cannot authorize itself. Drift can suspend new admission
while valid deterministic TI continues. A weakly supported 0.52 is not preferable
to a precise abstention. Coverage denominators include failures and exclusions.

A4/A5/A6 future seams preserve owners, target/horizon compatibility, original
outputs and fingerprints. No automatic v1 influence, option-POP conversion,
quantity selection or broker action is introduced. Recorded replay does not run
a model; pinned verification reruns an exact supported artifact; retraining is a
different experiment. Proposed numerical verifier tolerances are not calibration
tolerances or permission to substitute a newer artifact.

## Worked scenarios

All are synthetic; no named symbol represents a live recommendation or finding.

| Case | Context | Disposition and lesson |
|---|---|---|
| 1 | KAYNES, Model A/1.0, 0.70 next-session forecast | Reasonably calibrated cohort and assumed preregistered gates/shadow pass → eligible for explicit advisory approval, not automatic activation |
| 2 | RELIANCE, Model B/1.0, 0.90 versus 0.62 | Poor calibration/unstable regimes reject promotion despite attractive ranking |
| 3 | Model C/1.0, 10:00 row with 11:00 high | Leakage and unsupported intraday target invalidate the experiment |
| 4 | Model D/1.0 versus training-fitted 0.60 prior | Matched Brier 0.25 versus 0.24: no established improvement |
| 5 | HDFCBANK, Model E/1.0, many rows/two sessions | Insufficient independent temporal/cohort support blocks empirical approval |
| 6 | Model F/1.0, ordinary versus stressed cohorts | Weak required regime blocks broad promotion; no post-hoc cohort deletion |
| 7 | Model A/1.0 drifts from 0.70/0.69 to 0.70/0.50 | Assumed pinned suspension gate met; new admission suspended, baseline continues |
| 8 | KAYNES, configured Model A/1.0 pin missing | No forecast or invented 0.50; valid A4/A6 and recorded historical replay remain independent |
| 9 | RELIANCE rejected by TM, terminal observation revised | Append J2 linked to J1; preserve forecast and old dataset; no fabricated trade P&L |
| 10 | ATHERENERG, uncertain corporate-action qualification | No admitted probability/label; exclusions and selection bias remain visible |

The FAQ answers all 29 requested questions: probability meaning/guarantees,
accuracy/calibration/Brier, history/splits/walk-forward/leakage/overfitting,
baseline, automatic learning/disablement/drift/unavailability, quantity/execution/
strikes/A6, abstention, deep models/disagreement/ensembles/deferral, shadow,
replay/retraining, comparison with deterministic TI and expected utility.

## Findings for the next reconciliation pass

| ID | Topic | Classification |
|---|---|---|
| TF-01 | Narrow binary target's evidence-of-usefulness claim | CLARIFICATION_NEEDED |
| TF-02 | Exceptional supplied calendar revisions | CLARIFICATION_NEEDED |
| TF-03 | Calibration support and independent sessions | CLARIFICATION_NEEDED |
| TF-04 | ECE bins, sparse support and uncertainty | CLARIFICATION_NEEDED |
| TF-05 | Preregistered promotion thresholds and review | CLARIFICATION_NEEDED |
| TF-06 | Regime stability and narrowed applicability | CLARIFICATION_NEEDED |
| TF-07 | Shadow duration, mature labels and coverage | CLARIFICATION_NEEDED |
| TF-08 | Drift, expiry and delayed-label precedence | CLARIFICATION_NEEDED |
| TF-09 | Independently identifiable population-disposition report | ARCHITECTURE_CHANGE_PROPOSED |
| TF-10 | Corporate-action censoring/selection bias | CLARIFICATION_NEEDED |
| TF-11 | Exact replay versus numerical verification tolerances | CLARIFICATION_NEEDED |
| TF-12 | Local registry scope | NO_CHANGE |
| TF-13 | Raw-logit contributions and separate calibration display | IMPLEMENTATION_DETAIL_ONLY |
| TF-14 | No automatic A4/A5/A6 influence | NO_CHANGE |
| TF-15 | Forecast staleness versus target endpoint | CLARIFICATION_NEEDED |
| TF-16 | Advanced models, targets and automation | DEFER |
| TF-17 | Deterministic independence and own prerequisites | NO_CHANGE |

Totals: **11 CLARIFICATION_NEEDED, 1 ARCHITECTURE_CHANGE_PROPOSED,
1 IMPLEMENTATION_DETAIL_ONLY, 3 NO_CHANGE, 1 DEFER**.

The only proposed architecture change is TF-09: consider a separately identifiable,
immutable evaluation-population disposition report alongside empirical scorecards.
The draft already requires coverage/exclusion counts; the proposal concerns
artifact identity and reviewability, **not relaxed data eligibility**. Reconciliation
may reject a separate artifact if the existing EvaluationReport suffices. This
proposal is not implemented, adopted or assumed as a gate in the examples.

## Validation and rebuild

Validated locally with Python 3.12, stdlib OOXML tooling, ImageMagick, Poppler
and LibreOffice 24.2. No project dependencies were added. LibreOffice needed
approved access outside the filesystem sandbox for its local configuration;
rendering used isolated temporary profiles and no provider/model credentials.

Document checks pass for ZIP/OOXML integrity, package relationships, 37 contents
bookmarks and exact rendered page mapping, sequential figure IDs, all scenarios/
FAQ/findings, two embedded charts, 30 table grids and non-splitting rows. PDF word
bounds are within the page safety region; no replacement glyphs were found.
All 39 pages were visually reviewed as contact sheets, with larger checks of
the two charts and lifecycle diagram. The initial overlapping coverage labels
were corrected before the final edition. No blank or one-paragraph body pages.

Illustrative arithmetic checks pass for Brier 0.35, overconfident-cohort Brier
0.314, prior-control Brier 0.24, and precision 55%/70%/80% versus requested-population
coverage 80%/40%/15%. The PDF clearly labels all synthetic observations. Manual
semantic review preserves the strict target, no guarantee, no inferred POP/price
target, no automatic promotion and no authority drift.

Rebuild from the repository root:

```bash
python3 docs/handbooks/a7_forecasting/build_charts.py
.venv/bin/python docs/handbooks/a7_forecasting/build_handbook.py
render_dir=$(mktemp -d /tmp/tiaf-a7-render-XXXXXX)
libreoffice -env:UserInstallation=file://"$render_dir/profile" --headless \
  --convert-to pdf --outdir docs docs/TI_Forecasting_Evaluation_Learning_Thesis.docx
.venv/bin/python docs/handbooks/a7_forecasting/validate_handbook.py \
  --pdf docs/TI_Forecasting_Evaluation_Learning_Thesis.pdf --verify-toc \
  --check-worktree-links
```

If narrative/layout changes, first validate with `--page-map-out
docs/handbooks/a7_forecasting/page_map.json` instead of `--verify-toc`, then rebuild
and render again before verifying contents. Builder/validator/chart files are
documentation tooling only, with no TI/domain imports or model evaluation.
They need not be in the runtime test/type-check scope.

Final documentation gates:

| Gate | Result |
|---|---|
| Document validator with `--verify-toc --check-worktree-links` | PASS; **18 Markdown files, 740 local links**, including referenced heading anchors; external links not fetched by the validator |
| Word external relationships to local documents | PASS; all local targets exist and resolve from the delivered DOCX location |
| `git diff --check` | PASS |
| `git diff --no-index --check /dev/null <new-text-file>` | PASS for all **11** untracked text files, including the three preserved architecture files |
| `.venv/bin/python -m compileall docs/handbooks/a7_forecasting` | PASS |
| `.venv/bin/ruff check docs/handbooks/a7_forecasting` | PASS |
| `.venv/bin/ruff format --check docs/handbooks/a7_forecasting` | PASS |
| Three primary A7 entry hashes; HEAD/A5/A6 tag targets | Unchanged |
| Runtime/test/packaging and prior A6 handbook diff | No changes |

No full runtime suite or live acceptance is claimed or needed for this
documentation-only task. The generated edition checksums are:

| Artifact | SHA-256 |
|---|---|
| DOCX | `c3b955c2f1abb2d99bb651a8b7d585062d3a5b0e0cc25b1a543fdfc46cd771f2` |
| PDF | `3ea52729952d190501da5e810455cf134618c48219918c9910cfd89b02075721` |

Rebuilding can change package/PDF metadata and therefore these file checksums;
they identify this rendered edition, not a guarantee of byte-identical rebuilds.

## Historical creation scope, status and next prompt

Task entry was already dirty: 13 tracked documentation edits and the three new
A7 architecture documents. Those changes were preserved. This pass adds the
thesis, creation record and authoring assets/tooling; it updates current
navigation/status in README, architecture index, implementation roadmap,
milestones, major roadmap, targets, capability map, deferral navigation, system,
ecosystem and project thesis. It does not edit runtime, tests, packaging, frozen
A6 artifacts, model coefficients, policies or the three primary A7 documents.

| Status dimension | After this pass |
|---|---|
| A6 | **FROZEN** at `tiaf-a6-baseline` |
| A7 architecture | **DRAFT** |
| A7 thesis | **CREATED**, non-normative |
| A7 thesis / architecture reconciliation | **NEXT** |
| A7 runtime | **NOT_IMPLEMENTED** |
| A8–A10 | Planned, unchanged |
| Model training / live provider/model/broker calls | **None** |
| Commit / tag / push | **None performed** |

The baseline HEAD/tag remains `6dc2ff304aae0e87540260b092919bb91e4d4189`.
The existing `tiaf-a5-baseline` is also unchanged. No architectural finding is
silently accepted and no runtime work is authorized by thesis readiness.

Historical creation-pass next prompt: **TIAF A7 — THESIS / ARCHITECTURE RECONCILIATION PASS**.
