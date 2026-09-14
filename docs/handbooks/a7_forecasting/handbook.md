# 1. Why A7 Exists

TradingIntelligence already has a reasoned account of what it sees: factual data, deterministic features, specialist interpretations, challenged theses, position advice and bounded option-expression assessment. Those layers can explain why a candidate is attractive or unsuitable under a policy. They do not, merely by agreeing, establish how often an exactly defined future event will occur. A7 addresses that missing empirical question without discarding the earlier reasoning.

There are three different jobs. Forecasting estimates an event before it occurs. Evaluation compares a preserved estimate or decision with later qualified observations. Learning constructs and tests a candidate improvement for future use. Combining these into one opaque “AI engine” would make it difficult to distinguish a prediction from its later explanation, or an experiment from an approved deployment. Separation is therefore an audit mechanism, not just an organizational preference.

:::figure 01 Three questions, separate products and authorities
| FORECASTING | EVALUATION | LEARNING |
| What may happen? | How did the frozen estimate perform? | What improvement earns future use? |
| Before outcome: forecast or abstention | After observation: journal and scorecard | Offline: new artifact and review evidence |
| Cannot retrain itself | Cannot rewrite the original decision | Cannot approve its own deployment |
:::

Consider a repeated tendency to call certain setups “supportive.” That could be an understandable deterministic classification yet offer little additional predictive information over the market's historical positive-session rate. A7 should expose that possibility. Conversely, a model might add useful information but only in a qualified cohort. The appropriate conclusion is bounded applicability, not a universal badge of intelligence.

This book explains a proposal, not a running forecaster. A6 is frozen; A7 architecture remains a draft; no A7 model has been trained or validated for this thesis. Every numerical cohort and scenario is invented for teaching. The primary draft architecture, roadmap and reconciliation record listed in Appendix A remain the controlling sources. A thesis finding is an invitation to reconcile, never a silent amendment.

# 2. Deterministic vs Probabilistic Intelligence

Deterministic does not mean infallible, and probabilistic does not mean arbitrary. A deterministic policy returns the same result for the same qualified inputs and exact policy. Its thresholds may be engineering choices rather than empirically optimal ones. A fitted model can also perform deterministic inference when its coefficients, transforms and runtime are pinned. The difference is that its parameters were estimated from data and its output addresses uncertainty about a specified event.

The two forms of intelligence answer different questions. A6 may reject an option because the captured quote is stale. A high underlying-direction probability does not make that quote current. A4 may preserve NO_TRADE because the thesis fails a required gate. A7 does not acquire authority to remove that gate. Prediction and admissibility must not be collapsed into a single attractive number.

:::figure 02 Two views of the same captured evidence
| Visible deterministic control | Optional proposed A7 overlay |
| A2 facts, score, class and NO_TRADE | Exact event, horizon and probability or abstention |
| A3 evidence and disagreement; A4 arbitration | Model, calibration, dataset and applicability |
| A5 position advice; A6 eligible candidates/rank | Separate forecast record, no v1 reranking |
| Remains usable when its own requirements pass | Unavailability does not rewrite the control |
:::

Keeping the control makes improvement testable. If a new model changes both the candidate set and the evaluation population, apparent gains may be selection effects. If it erases rejected candidates, mistakes disappear from view. Preserve the original record, add a separate forecast, then compare on defined matched cohorts.

The proposed v1 is shadow/advisory only. “Advisory” does not mean a model-selected trade slips into the system through softer language. It means a separately identified estimate can be inspected without automatically changing frozen A4, A5 or A6 policy. Future integration needs its own versioned admission and consumer policy, with both views still visible.

# 3. What Is a Forecast?

A forecast is a statement made with an information boundary about an outcome that has not yet been observed. “Bullish, 70%” is incomplete: bullish over which interval, against which reference, on which asset and with what definition of success? A precise record must allow an independent evaluator to determine whether the event happened without interpreting the author's intention afterward.

The proposed A7 record names the neutral subject, target version, exact horizon, reference observation, feature snapshot, model and calibrator, issue time, validity and applicability. It also carries limitations and an explicit unavailable/abstention state. Evidence quality, uncertainty about model performance and the event probability are different dimensions. None should be compressed into a self-confidence score.

:::figure 03 Anatomy of a forecast record — proposed, not a current API
| Identity | Meaning | Audit link |
| Subject + target/version | Precisely defined future event | Qualified instrument and label specification |
| Reference + exact window | Starting comparison and observation endpoint | Price and supplied session artifact |
| Estimate or absence | Calibrated probability, or a reason no estimate is admitted | Model/calibrator and gate report |
| Cutoff + issue + validity | What was known, when issued, when usable | Captured features and composition |
:::

A forecast can be wrong without having been dishonestly constructed. A 70% estimate explicitly allows the other outcome. Conversely, a correct prediction made using future information is invalid evaluation evidence. Forecast quality cannot be inferred from one correct or incorrect case.

A7 does not manufacture a distribution when it has only a binary model. It does not infer a price target from a probability. The currently existing A3 forecast contract is a consumer placeholder, not an implemented predictor. The A7 draft proposes a separate precise evidence version; broad legacy records cannot be automatically converted when their event semantics are unknown.

# 4. Forecast Targets

The narrow initial target is **P(next-session close > known reference close)** for qualified NSE cash-equity context. Its label is one if the terminal close is strictly greater than the reference close and zero otherwise. Equal prices belong to zero. Missing terminal prices belong to neither class. Source prices and their basis must be retained precisely enough that rounding a displayed return cannot change the label.

Suppose, purely illustratively, the reference is 100.00. A qualified next-session close of 100.01 has label one; 100.00 or 99.99 has label zero. This says nothing about the route prices took, the size of a gain, an available entry price or trading expenses. The underlying could finish marginally higher after a severe intraday drawdown. An option could lose value even while its underlying finishes higher.

| Question | Answered by initial target? | Why |
| Next qualified session closes above the reference? | Yes, probabilistically | This is the declared endpoint event |
| An option earns a profit? | No | Requires premium, contract, path and cost semantics |
| A target is touched before a stop? | No | Requires ordered path events and fixed levels |
| Five-day return or intraday direction? | No | Different observation window and target |
| Expected monetary return? | No | Sign probability does not supply payoff magnitude or execution |

The restriction is intentional: one target makes the entire chain inspectable. However, simplicity is not evidence of usefulness. The thesis asks reconciliation to ensure user-facing language describes a short-horizon diagnostic, not a general positional recommendation. If the target cannot beat an appropriate control or prove applicability, the honest result is an unapproved model.

Future targets may predict returns, distributions, volatility or path events, but each requires new labels, data qualifications and empirical gates. A generic output field is not permission to support every economically interesting question.

# 5. Forecast Horizons

“Tomorrow” and “one day” are poor internal specifications. A holiday, suspension or exceptional session changes which observations exist. The architecture uses a supplied, qualified session schedule, with identifiers and exact instants. It does not infer a trading calendar from weekdays or a default close time.

:::figure 04 Reference, cutoff, issue, outcome and expiry of use
| Illustrative event | Clock / role | Meaning |
| S0 completed close | 15:30, source observation | Known reference, not a promised fill |
| Evidence cutoff | 16:00, decision information boundary | Eligible information must be available and captured |
| Forecast issued | 16:01, before supplied S1 open | Immutable prediction recorded before outcome |
| S1 open → S1 close | Exact supplied next session | Future observation period; no weekday guessing |
| Admission valid-until | Separately pinned boundary | May end before outcome time; not the target endpoint |
:::

These clock values are illustrative, not assertions of a particular exchange's schedule. Application instants remain timezone-aware and normalized with ZoneInfo("Asia/Kolkata"); JSON uses +05:30. A date label is not a substitute for an instant. Naive datetimes cannot establish this sequence.

The reference was known at issuance, but that does not mean a trader could enter at it. Any economic simulation needs an independently declared post-issue entry convention. Otherwise the test can accidentally award overnight gains that were already unavailable to the hypothetical trader.

The same care applies to downstream alignment. A next-session forecast beside a five-day positional thesis is a short-horizon annotation, not evidence about all five days. A6 expiry and A5 position horizon remain their own constraints. Unknown calendar changes or mismatched windows produce explicit incompatibility or censoring; they do not quietly extend the target until a convenient price appears.

# 6. Scores, Probabilities and Calibration

A score ranks or summarizes according to its construction. A probability makes a frequency claim about a defined event and cohort. Dividing an A2 score by 100 does not create a probability. Neither does averaging specialist confidence. The number must have an empirical interpretation supported by an appropriate evaluation design.

Our first illustrative cohort contains 1,000 invented forecasts all at 0.70, with 690 positive labels: observed frequency 0.69. The aggregate is reasonably close to the stated probability. It is a useful teaching example of calibration, not proof that a real system meets a statistical tolerance. A second invented cohort contains 1,000 forecasts at 0.90 with 620 positives: frequency 0.62. The model is conspicuously overconfident in that cohort.

:::chart 05 Illustrative reliability chart — invented cohorts, not measured performance
calibration.png
:::

Calibration is a relationship across comparable cases, not a verdict on an individual forecast. Cohort size, dependence, selection and uncertainty matter. One thousand correlated equities observed on very few sessions offer less independent evidence than the row count suggests. A model can look calibrated overall and fail in a required regime. Always ask which cases entered the bins and which were missing.

A monotone recalibration can preserve the ordering of candidates while changing the numeric probabilities substantially. This explains why ranking ability can look respectable even when probabilities are unsafe. It also explains why AUC alone cannot certify calibrated confidence.

The draft requires separate held-out calibration and later validation. A calibration identifier records lineage; it does not prove the fit worked. Official scikit-learn calibration documentation describes reliability diagrams as comparing grouped mean predictions with observed positive frequency and cautions that lower Brier loss alone does not establish better calibration. [Calibration reference](https://scikit-learn.org/stable/modules/calibration.html).

# 7. Why Accuracy Is Not Enough

Imagine an invented population with 80 positive labels out of 100. Always predicting the positive class achieves 80% accuracy while learning nothing about which individual cases are more likely. A model that reports extreme confidence may look attractive on hard-label accuracy and still penalize users badly when it is confidently wrong. Classification threshold, class balance and the cost of errors change the meaning of accuracy.

For this book's binary convention, the **Brier score** is the average of (p − y)². Smaller is better on the same eligible population. Four invented forecasts, 0.70, 0.70, 0.90 and 0.90, paired with labels 1, 0, 1 and 0, contribute 0.09, 0.49, 0.01 and 0.81. Their mean is 0.35. The last confident mistake contributes much more than the first correct prediction. This is an arithmetic illustration, not a model trial. [Brier reference](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html).

:::figure 06 A small metric dashboard beats a single success number
| Measure | Useful question | Cannot establish alone |
| Brier / log loss | Are numeric forecasts good on matched labels? | Calibration in every subgroup or economic value |
| Reliability / ECE | Do stated frequencies match observed frequencies? | Useful separation of cases or future stability |
| AUC | Does ordering discriminate the classes? | Safe probability values or profitable decisions |
| Precision / coverage | How selective is the accepted operating point? | Quality of excluded/unobserved cases |
| Utility / downside | What consequences follow under stated assumptions? | Actual fills or causal benefit without evidence |
:::

Log loss also evaluates probabilities and strongly penalizes confident mistakes. Numerical clipping at zero/one must be a pinned metric convention, not an unreported modification of captured forecasts. ECE summarizes bin discrepancies but depends on binning. Neither is a magic certificate.

The model must face a base-rate control, matched rows and uncertainty estimates. Show prevalence and coverage first. A model that scores only easy cases cannot compare its headline metric with a baseline scored on everyone and call the difference improvement.

# 8. Point-in-Time Data

Point-in-time discipline asks what the system could legitimately use at the decision cutoff, not merely what a historical database contains now. Event time, publication time, availability, acquisition and admission answer different questions. A filing may concern an earlier quarter yet be published later. An old publication downloaded today was not necessarily in TI's captured knowledge then.

:::figure 07 The knowledge boundary is not just an event timestamp
| Clock | Question | Eligibility implication |
| Event/effective time | When did the described thing occur or apply? | Historical subject does not prove historical knowledge |
| Publication/availability | When could this version be accessed? | Later disclosure cannot inform an earlier cutoff |
| Acquisition/admission | When did TI capture and admit it? | CAPTURED_AS_KNOWN requires the captured version by cutoff |
| Projection computation | When was the derived snapshot assembled? | Later research must identify itself, not masquerade as an issued forecast |
:::

The initial policy is deliberately conservative. It uses eligible captured evidence and records limitations. It does not declare arbitrary historical downloads backtest-ready. New calculations over a valid old immutable capture may be retrospective research, provided every dependency was eligible and transform selection belongs to training. They are not forecasts actually issued on that historical date.

This can mean a dataset is unusable for a desired experiment even though it contains years of prices. That is a finding about evidence, not a software inconvenience to hide. Dataset rights must also cover training and retention; access to a quote does not automatically grant every later use.

PIT discipline includes the historical universe and revisions. Preserve securities that disappeared, historical membership, action coverage and missing labels. The checksums of captured files prove integrity, not source accuracy, licensing, authentic availability or absence of selection bias. The prototype can be mechanically correct and still lack a qualified empirical corpus.

# 9. Leakage

Leakage allows the answer, or information unavailable at the supposed decision, to enter the prediction process. It invalidates the experiment's claim to simulate prediction before outcome. It can arise in raw data, features, universe selection, preprocessing, hyperparameter search or repeated use of a supposedly untouched test set.

:::figure 08 Three impressive backtests that answer the wrong question
| Leak | What went wrong | Required response |
| 10:00 prediction uses 11:00 high | Future market information entered the feature | Reject row/experiment; rebuild from eligible inputs |
| Historical universe contains later survivors only | Future survival chose the population | Reconstruct dated universe or qualify the claim as invalid |
| Latest adjusted history uses future action knowledge | Later revision/basis enters an earlier feature | Require captured vintage; do not infer earlier knowledge |
:::

The first example is obvious once clocks are visible. A “day high” field may look harmless in a dataframe, but at 10:00 it cannot contain an 11:00 high. A clean timestamp on the row does not make every joined field time-correct.

The second is subtler. Selecting only companies still listed today deletes some difficult historical outcomes and makes the strategy look more robust. Even perfectly timestamped prices for the survivors cannot repair the missing population. Unavailable delisting outcomes must remain visible rather than turn into excluded losses or presumed flat returns.

The third does not imply every adjusted series always changes every feature. A uniform rescaling may leave some ratios unchanged. The violation occurs when later adjustment knowledge changes the earlier feature, reference or eligibility without a qualified vintage. A7 must prove the actual field transformation, not assume that a familiar “adjusted” label is PIT-safe.

Less visible leaks include scaling across all dates, tuning to final-test results and using an A7-influenced A4 output to train the same forecast. Detecting leakage does not justify a small penalty to the performance report: affected evidence is invalid. Repair creates a new dataset and experiment, with the failure retained in lineage.

# 10. Dataset Splits

Each partition has a different right to influence the system. Training fits transforms and estimator parameters. Calibration fits the probability mapping on frozen estimator scores. Validation selects among predeclared candidates and operating points. Test evaluates the locked choice. Shadow observes a prospectively issued artifact in later conditions. Reusing these names for overlapping rows defeats their purpose.

:::figure 09 Rights of the chronological partitions
| Earlier → later | What may be fitted or chosen? | What stays frozen? |
| TRAIN | Estimator and preprocessing | Target, eligibility and split protocol |
| CALIBRATION | Calibrator only | Estimator and train-fit transforms |
| VALIDATION | Bounded candidate / abstention selection | Test outcomes remain unseen |
| TEST | Nothing | Artifact, calibrator, thresholds and reporting policy |
| SHADOW | Nothing automatically | Issued predictions and approval scope |
:::

Market observations are not interchangeable independent rows. Adjacent labels overlap; multiple equities share sessions and shocks. A random split can put tomorrow's conditions into training while yesterday's prediction sits in test. Even when no single feature is forward-looking, the experiment can claim a forecasting situation it never actually respected.

The A7 draft groups by origin session and uses label dependency intervals and availability. Preprocessing must also respect the partition: missing-value statistics, scaling and category vocabularies are not fitted on the test population. Required missing features cannot be imputed merely to make an otherwise inadmissible request pass.

Temporal splitting is necessary but not sufficient. The source vintage, corporate actions, universe and fitting clocks still matter. The scikit-learn TimeSeriesSplit reference is a useful illustration of chronological splits and an explicit gap, not an implementation of TI's complete PIT or label-interval policy. [Temporal split reference](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html).

No real numerical split sizes or quality hurdles are selected here. The architecture requires a preregistered profile before model selection sees holdout outcomes. A beautiful test result cannot retroactively determine what “enough data” means.

# 11. Walk-Forward Evaluation

Walk-forward evaluation repeats the prediction exercise as time advances. At each simulated fitting cutoff, only information and mature labels available then may be used. An expanding window retains eligible older training observations; a rolling window drops observations outside its fixed-length historical span. Neither automatically solves regime change: the choice encodes a hypothesis about how past data remains useful.

:::figure 10 Illustrative forward folds — logical blocks, not real date ranges
| Fold | Training | Gap / calibration / gap / validation / gap | Test |
| 1 expanding | Earlier block A | Later development block B | C |
| 2 expanding | A + eligible matured B/C | Later development block D | E |
| 3 rolling | Only the allowed recent historical span | New development block F | G |
:::

The table compresses time for teaching. Every component of a development block is chronologically disjoint. A later fold may use an earlier fold's test outcomes only once those outcomes were actually available; it must not count them again as newly independent test evidence. Keep a final untouched holdout beyond the selection process and record every trial.

Purging removes earlier examples whose label-information interval overlaps a later partition or was not mature at fit time. Embargo leaves an explicit interval between blocks. A7's draft uses at least a full target-session span for v1, with exact removal driven by dependencies and supplied sessions. A longer future target requires a correspondingly justified policy, not a fixed row count copied from a tutorial.

Suppose a training row starts before validation but its label depends on validation-session close. It is not safe merely because its start date is earlier. The split must inspect when its answer became known. Separately, feature lookback can reference older eligible data without granting permission to fit transforms on future rows.

Report fold-level performance, coverage and worst-cohort weaknesses, not just the best fold. Selecting the best of many experiments is itself learning; the selection history must be visible. Walk-forward is a rehearsal of chronological evidence use, not permission to repeatedly peek at the final examination.

# 12. Outcome Journal

The forecast is a promise to be evaluated later, not a mutable note to improve after seeing the result. The outcome journal appends qualified observations beside the original forecast and decision. It links identities and fingerprints without inserting later facts into the original feature snapshot. That separation makes it possible to ask both what TI believed and what was subsequently observed.

:::figure 11 Four journal stories must remain distinguishable
| Story | Preserved operation state | Evaluation consequence |
| Forecast; trade taken | TAKEN with supplied execution reference | Market label and actual execution evaluation remain separate |
| Forecast; trade rejected | REJECTED with owner and reason | Can study factual market label; no invented fill or trade loss |
| Forecast; outcome absent | UNKNOWN / pending or censored observation | Missing label is not class zero |
| Later market-data correction | New journal/label revision points to predecessor | Old dataset and replay retain the old pinned revision |
:::

An underlying price outcome may be observable for a rejected candidate. That can reveal whether the forecast discriminated events beyond the ultimately traded subset. It does not establish what would have happened if the rejected option had been filled. Counterfactual execution needs assumptions and evidence that the market label alone cannot provide.

Journal completeness is measure-specific. A qualified terminal close may support the binary endpoint label even if an intraday path is incomplete. The same evidence cannot establish full-window maximum favorable or adverse excursion. Partial observed extrema must be described as partial, not silently promoted to complete risk statistics.

Corrections append rather than erase. If a vendor later revises the terminal price, a new journal entry records the new fact, source availability, labeler version and relationship to the earlier entry. A dataset built before that revision cannot silently use the corrected answer at an earlier fitting cutoff.

The journal is not a scheduler. A7 defines outcome needs and admission rules; a future operational runtime can arrange acquisition under separate authority. “Outcome due” does not mean an observation exists, and no absent observation is filled with a synthetic favorable result.

# 13. Label Governance

A label turns evidence into a specific supervised-learning answer. It is not the future truth in general. The v1 label asks whether one precisely defined terminal close exceeded a known reference. Different labels can reasonably answer different questions about the same path, but their versions and meanings cannot be interchanged during evaluation.

:::figure 12 From observations to a governed label
| Gate | Accepted route | Otherwise |
| Correct subject / window / price basis | Compare qualified endpoints | Ineligible or pending |
| Required action and source coverage | Apply pinned label specification | Unknown coverage remains explicit |
| Strict comparison | Above → 1; equal/below → 0 | Missing is not 0 |
| Correction received later | Append revised label with known-at time | Do not mutate the old dataset |
:::

Corporate actions expose the importance of basis. The draft uses unadjusted price endpoints and excludes affected windows under sourced action coverage. It does not infer adjustments from a price jump. Unknown coverage prevents supervised eligibility. This is a restricted population, not a solved adjusted-history infrastructure. Exclusions can be informative: if difficult event periods disappear, apparent performance may not generalize. Report that limitation explicitly.

Future target-before-stop labels need ordering, not just extrema. When both levels are touched within a bar whose internal order is unknown, the answer is ambiguous. Selecting the favorable ordering would manufacture success. Future levels must also have been fixed at decision time, rather than chosen after observing the path.

Learning from labels requires mature information. The target session ending is not necessarily the label-availability instant: ingestion, correction and coverage checks may happen later. The labeler's version, timing and provenance are therefore training inputs in the governance sense, though future label values never become forecast features. Tests must cover ties, missing data, action changes and revisions before statistical performance is considered.

# 14. Baselines and Controls

The first question for a new model is not whether its output looks sophisticated, but whether it adds information beyond a plausible simpler alternative. The historical positive-label base rate is a natural probability control for the initial target, fitted only from eligible earlier training rows. A fixed 0.5 predictor is a diagnostic, not necessarily the strongest meaningful control. Persistence supplies another declared heuristic; hard-label persistence cannot acquire probability semantics without its own qualified mapping.

:::figure 13 Benchmark hierarchy — compare like questions on like rows
| Control level | What is preserved? | What comparison means |
| Prior / base rate | Earlier eligible frequency | Does the model add information? |
| Persistence / simple logistic | Pinned simple prediction policy | Does complexity earn its cost? |
| A2 / A4 | Original score, class, thesis and non-action | Matched coverage and conditional outcomes, not Brier on an ordinal score |
| A5 / A6 | Original advice and valid-candidate rank | Outcome analysis only under compatible path/economic assumptions |
:::

A7 must not divide an A2 score by 100 and calculate a misleading Brier comparison. A2 and A4 do not promise the same probability event. Their comparison needs a predeclared decision mapping, matched population and an appropriate descriptive or economic objective. A6's contract rank is also not a next-session direction forecast. Similar-looking columns are not interchangeable estimands.

Retain cases where controls abstain, reject or lack evidence. Compare metrics on a disclosed matched subset while showing the full population and exclusions. If a model needs richer evidence, report the extra cost and the population shift. A3.10 demonstrates attributable added context and accounting; that alone does not prove incremental predictive value.

A future human comparison requires a genuine timestamped decision or forecast, not an invented expert consensus. Observational outcome differences do not prove that following one adviser caused better returns. The control hierarchy is intended to prevent easy victories against a straw-man baseline and to make a legitimate “no improvement established” result possible.

# 15. Initial Model Families

The initial recommendation is regularized logistic regression on a small, pinned A2 feature schema. It offers an understandable mapping from input features to a raw logit, can be exported as declarative coefficients, and keeps experimentation manageable. These are engineering advantages, not a guarantee that market behavior is linear or that the model will outperform its prior.

The estimator, preprocessing and feature order are all part of the artifact. A coefficient cannot be interpreted independently of the scaling applied to its feature. A changed window, unit or missing-value convention changes the model's input meaning even if the column name stays the same. The concrete fields must be frozen before fitting; A7 does not quietly recalculate A2 or optimize its parameters.

| Family | Proposed disposition | What would justify more complexity? |
| Historical base rate | Required control | Remains visible even when a model is admitted |
| Regularized logistic | Initial reference estimator | Qualified data, reproducibility and held-out evidence |
| Trees / random forests / boosted models | Later bounded experiments | Incremental OOS value over the pinned simple model |
| Ensembles / deep or sequence models | Deferred | Added evidence, cost budget, explainability and governance |

A model library is an optional implementation adapter, not a new owner of TI semantics. Model training may use a pinned dependency later, while recorded replay must still read captured results without importing it. No production fit library is installed or selected by this thesis.

Starting small also limits the number of opportunities to fool ourselves. A huge search can produce an impressive winner through repeated selection even when no candidate generalizes. All tried configurations, failures and budgets must remain visible. A model that fails its gates is not repaired by introducing an unbounded search for a more flattering answer.

# 16. Calibration Methods

The estimator and calibrator have different jobs. The estimator learns a relationship between features and the target. The calibrator maps its frozen score into a probability scale using separate held-out evidence. If both are fitted to the same optimistic training predictions, the mapping can inherit overconfidence. A second fit step is not independent validation merely because it has a different function name.

:::flow 14 Calibration is fitted separately and still has to be evaluated
TRAIN → fit transforms and estimator; freeze them
CALIBRATION → score with the frozen estimator; fit sigmoid mapping
VALIDATION → compare predeclared candidates and operating points
TEST → measure locked estimator + calibrator; do not retune
SHADOW → later prospective evidence under explicit approval
:::

The draft chooses sigmoid calibration initially. Its limited flexibility is a conservative starting point, not an empirical claim of superiority. Isotonic calibration can represent more flexible monotone mappings but needs adequate support; sparse calibration data can give a deceptive sense of precision. Neither method is a substitute for PIT qualification, class support or appropriate chronological splits.

Reliability diagrams should carry counts and uncertainty, including empty bins. ECE averages discrepancies across bins; changing edges after looking at the report can hide weaknesses. A small ECE in a pooled sample can coexist with serious regime-specific errors. A7 therefore needs both proper-score comparison and direct calibration evidence, not one interchangeable “confidence metric.”

No numerical binning policy, minimum sample or admissible error is silently established by this book. Those belong to the preregistered protocol before holdout inspection. Findings TF-03 and TF-04 ask reconciliation to make sample adequacy and bin governance intelligible to users. A calibration-fitted artifact may still fail validation; it must not be displayed as an admitted calibrated forecast merely because the fit completed.

# 17. Abstention and Precision/Coverage

An estimate of 0.52 can be technically representable yet unhelpful for a particular use, especially when applicability or calibration support is weak. The alternative is not necessarily 0.48 or a bearish opinion. ABSTAIN says that the admitted system cannot justify a useful forecast under the declared conditions. Hard missing-evidence gates and soft selectivity thresholds have different causes and must remain distinguishable.

:::chart 15 Illustrative precision/coverage trade-off — invented validation sets
coverage.png
:::

In the invented chart, 100 requested cases include 20 hard exclusions. Thresholds of 0.50, 0.65 and 0.80 accept 80, 40 and 15 cases, with 44, 28 and 12 positives. Precision rises from 55% to 70% to 80%, while coverage over all requests falls from 80% to 40% to 15%. This illustrates a possible trade-off, not a rule that higher thresholds always improve precision. Small selective cohorts can become unstable.

The total-request denominator is essential. A pipeline cannot claim better coverage by omitting missing bindings, failed requests or censored outcomes. Label maturity should be reported separately from forecast availability. A model that abstains often may be appropriately cautious, but its narrow coverage must not be marketed as broad predictive reliability.

Thresholds are chosen under a preregistered validation protocol and locked before test. The number 0.52 is not a universal abstention threshold, and 0.80 is not an A7 policy default. If required calibration, feature or model status is missing, a high score cannot override the hard gate.

Abstention preserves the control path: A4 and A6 can still operate when their own inputs pass, without treating A7's silence as agreement. Conversely, if A4 itself lacks required evidence, losing the model does not authorize a fallback that magically makes A4 complete.

# 18. Economic Objective / Expected Utility

The project's economic objective is risk-adjusted expected utility, not raw profit or maximum win rate. Utility expresses how outcomes are valued under stated preferences and constraints. A distribution with rare severe losses may be unacceptable even when it wins frequently. The target, exposure, entry/exit convention and costs must all be explicit before an economic comparison means anything.

Consider two invented payoff sets of 100 hypothetical unit trades, ignoring costs only for arithmetic. Strategy W wins 90 times at +1 and loses ten times at −15: total −60. Strategy U wins 60 times at +2 and loses 40 times at −1: total +80. W has the higher win rate and the worse total. Neither example establishes a tradable strategy; neither shows the path ordering needed to measure drawdown.

| Illustrative payoff set | Wins / losses | Mean payoff per hypothetical trade | What is still absent? |
| W | 90 × +1; 10 × −15 | −0.60 | Costs, ordering, execution and risk preference |
| U | 60 × +2; 40 × −1 | +0.80 | Same missing economic/operational assumptions |

For a later distributional forecast, a declared utility function might allow E[u(R_net)]. The initial binary endpoint model supplies neither R_net's magnitude distribution nor an available fill. Multiplying its probability by a guessed profit is not expected utility. v1 must say NOT_ESTIMABLE when the target cannot answer the question.

Evaluation may later use a separately accepted unit-exposure convention with complete qualified data. Such hypothetical utility remains separate from actual account P&L. TM owns capital allocation, live risk limits, quantity, operational position truth and execution coordination. A user's risk preferences can select an approved evaluation profile; they cannot rewrite forecast facts or create a grant to trade.

# 19. Model Registry

A model registry is an evidence ledger for artifacts and their approved use, not a popularity list. “Use the latest model” is insufficient for replay: latest can change. A forecast must identify the exact estimator, calibrator, transforms, target, feature schema and policy that produced it, along with their approval and applicability at admission.

:::figure 16 Registry card — proposed structure, not a live model inventory
| Identity and artifact | Evidence lineage | Governance |
| Model ID/version and checksum | Train/calibration/test manifests | Owner and approval event |
| Target/horizon/feature schema | Label, transform and fold versions | Shadow/advisory scope and validity |
| Runtime/environment and calibrator | Metrics, controls and failed trials | Drift policy, suspension and retirement |
:::

The initial architecture needs no distributed registry service. Content-addressed local manifests and append-only lifecycle events are sufficient to describe the proposed boundary. A searchable index can be rebuilt; it is not the authority that decides a model is safe. Registration, successful training and approved deployment are different states.

The artifact format matters. Loading arbitrary executable objects can cross a security boundary. A7 proposes allowlisted declarative coefficients and transforms with validation, size limits and trusted origin checks. A checksum detects changed bytes; it does not prove a trustworthy publisher or sufficient permissions.

Model inspection remains engineering-oriented initially. A user should be able to understand a result's identity and limitations without receiving file paths, secrets or mutation handles. R5's current startup configuration has no A7 selector; the draft proposes a later versioned extension, not a configuration feature that already exists. Findings must not turn an illustrative registry card into a new current API.

# 20. Promotion Lifecycle

Promotion is an explicit permission to use a particular artifact for a particular bounded purpose. It is not a reward for winning a leaderboard. A candidate must survive data qualification, sample adequacy, OOS controls, calibration, regime stability, reproducibility, privacy, budgets and the required shadow evidence. Failure in a necessary gate cannot be averaged away by another strong metric.

:::figure 17 Three illustrative promotion candidates
| Candidate | Evidence story | Disposition |
| Model A | Calibrated, beats control, enough effective sample, stable, shadow passed | Eligible for explicit advisory approval, not automatically promoted |
| Model B | Higher AUC, poor calibration and unstable required regimes | Rejected for proposed use |
| Model C | Attractive historical metrics; leakage discovered | Experiment invalid; no promotion |
:::

All three stories are hypothetical. No real A7 candidate has passed these gates. Model A still needs a reviewer/operator event that pins the artifact, report, policy, cohort and expiry. Eligibility and approval must remain distinct so that a fit routine cannot accidentally grant itself production status.

The draft's lifecycle separates SHADOW_APPROVED from ADVISORY_APPROVED and contains no v1 decision-active state. A model cannot jump from training to influencing A4/A5/A6. A promotion also does not rewrite old forecasts or alter an in-flight request's binding. A new COLD composition pins a future selection; historical runs keep their original identity.

Thresholds require prior governance. There is no universal acceptable AUC or “500 rows is always enough” rule in this thesis. The protocol must state minimum distinct sessions, class/cohort support, uncertainty bounds and required improvement before the results are inspected. An absent threshold is not an invitation to choose a convenient one after seeing the data.

# 21. Shadow Mode

Shadow mode records what an approved experimental artifact would say without allowing it to alter operational decisions. The key word is prospective: its issue record must exist before the outcome. Running a model today over historical captures can be valid research under its stated conditions, but it is not evidence that the model survived the live sequence at that earlier time.

:::figure 18 Shadow means a parallel record, not a hidden decision path
| Existing path | Shadow path | Later comparison |
| Qualified evidence → A4/A5/A6 | Same scoped evidence → approved shadow forecast | Link both preserved records to mature outcomes |
| Original advice and rank retained | Probability or explicit absence | Compare coverage, calibration and controls |
| TM authority unchanged | No effect on capital, orders or frozen policy | Review before any advisory approval |
:::

Shadow testing reveals failures a clean offline cohort may conceal: delayed inputs, missing required features, unsupported regimes, expired health evidence and budget exhaustion. These requests belong in the denominator. A report built only from successfully scored and conveniently matured outcomes is incomplete.

Duration alone is not enough. Thirty days with very few eligible labels, or many highly correlated same-session observations, may not meet the approved protocol. The architecture requires prospective duration and sample/coverage conditions to be specified together. This book invents neither an operational schedule nor a mandatory shadow period.

A7 v1 does not create the recurring runtime that would collect everything automatically. Bounded manual shadow capture and later admitted outcomes can establish the conceptual path under separate implementation authority. Monitoring operationalization remains a later workstream. “Shadow approved” is not permission for unbounded provider calls, a hidden retry loop or a broker order.

# 22. Drift and Degradation

A model's past calibration belongs to a cohort and period; it is not a permanent property. Feature distributions, class prevalence, missingness, data conventions or market conditions can change. A good historical report cannot justify silently keeping an artifact active beyond its approved validity or outside its documented applicability.

:::flow 19 Drift response — illustrative, governed, not an implemented daemon
Initially qualified calibration and explicit advisory approval
↓ New conditions and mature labeled evidence show degradation
↓ Pinned drift policy evaluates scope, sample support and thresholds
↓ Admission suspended where required; gaps remain explicit
↓ Deterministic TI continues if its own requirements pass
↓ Review or retraining proposal; no automatic replacement
:::

Feature drift is not identical to calibration drift. A changed input distribution can be detected before enough labels mature to measure forecasting performance. Calibration drift concerns the relationship between predictions and outcomes. Coverage drift concerns who is no longer being scored or labeled. Each needs its own reference population and evidence; a single green health badge can hide these distinctions.

In an invented example, a once-reasonable 0.70 band later observes positives near 0.50. That raises a calibration concern, but the disposition still depends on mature samples and the predeclared policy. It is not valid to lower every probability by 0.20 and call that recalibration. Suspension is an admission decision; a repaired model must go through a new governed experiment.

If labels are pending, performance is UNKNOWN—not healthy by default and not automatically a loss. The proposal also requires expiry and current-health checks. Their interaction with no scheduler and delayed evidence needs clarification in reconciliation. The user should see whether a forecast is missing because of drift, staleness, insufficient support or an infrastructure failure.

# 23. Retraining Governance

**What “Learning” Does NOT Mean:** a live model sees today's trade, silently rewrites itself and causes tomorrow's trades to change. That story confuses observed outcomes, a training job, artifact approval, deployment and operational authority. It also makes old decisions hard to explain because the object called “the model” no longer has stable meaning.

:::figure 20 Learning is a governed successor, not self-modification
| NOT the design | Proposed governed route |
| Today's trade → silent update → different authority tomorrow | Outcomes → eligible immutable dataset → offline train/calibrate/evaluate |
| Current artifact overwritten | New model/version/checksum; previous artifact retained |
| Fit success implies live use | Review → shadow → explicit approval → new COLD binding |
| Better story replaces old decision | Old forecast, evidence and outcome lineage remain unchanged |
:::

Retraining can be motivated by drift, additional eligible data, a corrected label policy or a predeclared research proposal. The trigger does not establish that the candidate will be better. A failed retraining run should leave an explicit failure and the existing approved or suspended state intact, not deploy a half-written artifact.

:::flow 21 The whole lifecycle — four clocks, no automatic activation
FORECAST TIME: qualified PIT capture → pinned features → admitted model → pinned calibrator
↓ Immutable forecast evidence or explicit abstention; record before the outcome
↓ Separately governed future A4/A5/A6 consumption; no automatic initial-v1 influence
OUTCOME TIME: later qualified observation → immutable outcome journal → matched evaluation
TRAINING TIME: eligible journal/data → offline fit → held-out calibration → validation/test
↓ New version + complete report → review → approved prospective shadow → evaluation
PROMOTION TIME: explicit authorized approval → future COLD binding; old records unchanged
:::

Inference uses an already fitted, admitted calibrator; it does not fit that calibrator using the forecast's future answer. The four clock labels describe different events, often far apart. Promotion authorizes a particular future use of an artifact; it neither backdates a forecast nor retrospectively changes what a prior reviewer could know. This loop proposes future capability, not a running training or monitoring process.

The new run must pin data, feature and label versions, folds, seeds, dependencies, solver settings and every trial. Reusing a final holdout for many generations turns it into development evidence; a new later holdout is required for a fresh claim. Even operationally automated training in a future system would not imply automated promotion.

Policy learning is an even wider change than refitting the initial model. Changing A2 thresholds, A4 weights or A6 ranking semantics needs separate acceptance and a retained deterministic control. Personal trade outcomes also require governance before entering training. A user's filled trades are a selected population, not a complete market dataset, and private portfolio context must not flow into shared models by default.

# 24. How A7 Helps A4

A4 owns challenge and arbitration over a qualified underlying thesis. A future forecast can supply another precisely defined piece of evidence: perhaps short-horizon direction supports a timing argument, or a compatible path-risk estimate challenges it. The forecast does not gain authority merely because it is numeric. A4 must understand target, horizon, applicability, uncertainty and lineage before interpreting it.

The initial v1 does not automatically feed or modify A4. Its next-session target is particularly easy to overread beside a broader positional thesis. A favorable short-horizon probability cannot resolve a contradictory fundamental claim, supply a missing source or lift an A2 NO_TRADE gate. Nor does a less favorable probability automatically refute a longer thesis. Incomparable questions are not necessarily disagreements.

A later admission record should identify the forecast's model/calibrator, exact event/window, source feature snapshot, validity, evaluation support and comparison policy. A4 retains its original result as the control, and any separately accepted successor policy creates a new record. R3-style pinning makes it possible to explain which forecast was actually consumed.

There is a recursion risk. If an A7-enriched A4 conclusion becomes an input to the same A7 forecast, the pipeline can recycle its own opinion as evidence. The initial allowlist avoids that path. Future experiments must make upstream versions and causal ordering explicit. A7 helps by adding a testable proposition, not by creating an unquestionable statistical vote in a specialist majority.

# 25. How A7 Helps A5

A5 asks what current admitted evidence means for an existing position. Its ownership includes advisory posture and protection/reassessment reasoning, not broker state mutation. Future calibrated path or deterioration forecasts could become useful context, but those are not the initial binary endpoint target. A one-session positive close probability cannot establish whether the position's thesis survives, its stop is reached or holding dominates exiting.

An owned option further illustrates the difference. Even when the underlying closes above a reference, premium behavior depends on the specific contract and other conditions. It would be wrong to convert the initial probability into “70% chance you should hold this option.” A5 still requires its current qualified position snapshot and accepted A4 support; missing operational truth cannot be repaired by a forecaster.

The future seam links an optional compatible forecast to the current assessment cutoff and position context. It preserves the original A5 record and forecast absence separately. A model's failure is not MAINTAIN, and a model's positive estimate is not an order to retain exposure.

Monitoring may later arrange refreshed inputs and invoke A5, but neither a forecast nor A5's monitoring intent starts a running subscription today. TM decides whether and how to act under its authority, risk and capital constraints. A7 outcome evaluation can later study advice under explicit assumptions; without counterfactual execution evidence it cannot claim that an unchosen exit would certainly have improved P&L.

# 26. How A7 Helps A6

A6's frozen baseline evaluates supported long single-leg CE/PE expressions under strict captured evidence and admission rules. Its deterministic ordering is visible and replayable. A7 might eventually contribute an expression-compatible distribution or target/path probability, but that future comparison has to preserve the valid candidate set and cannot rescue an already rejected contract.

:::figure 22 Future consumer seams preserve three owners
| A4 arbitration | A5 position intelligence | A6 expression |
| May interpret admitted compatible forecast | May use qualified position/path context | May compare valid expressions under a new policy |
| Owns thesis disposition | Owns position advice | Owns candidate validation and selection |
| No automatic v1 influence | No position mutation or model-driven order | No v1 learned rerank or direction-to-POP conversion |
:::

Suppose KAYNES appears supportive upstream and the initial A7 estimate is 0.70 for its next-session close. That is not a 70% probability that a selected CE earns money. It neither identifies a strike nor says whether the premium is attractive. A6's quote freshness, horizon, coverage, liquidity and upstream-thesis gates retain their meaning. If they fail, a favorable probability cannot make the evidence adequate.

A future overlay would need forecast targets relevant to the expressions being compared, compatible horizons, qualified historical option data, calibration and an explicit economic comparison policy. It must retain original ranks, alternatives, rejected reasons and fingerprint lineage. Selection under a new policy must not overwrite the frozen baseline result.

The initial model is therefore a diagnostic foundation for later work, not a delivered probability-adjusted option selector. Keeping that modest promise is more useful than claiming immediate expression improvement that the target cannot substantiate.

# 27. Scanner / Signal Qualification Seam

Scanners discover or propose candidates. Signal Qualification is a distinct future capability that can assess whether a source signal merits further action or analysis under a declared policy. A7 can eventually supply a precisely defined meta-label probability to that qualifier. It does not become the scanner or take over its source identity and discovery state.

The permitted direction is scanner signal → deterministic qualification features → exact A7 meta-label evidence → qualification decision. Current-run qualification cannot feed itself back into the same forecast. Nor can the qualifier reinterpret a source score as a calibrated model output. Every object retains its source, version, cutoff and role.

The initial target is not automatically that meta-label. “The next close is above the reference” differs from “this signal's hypothetical trade meets a declared utility or stop/target rule.” A future meta-label needs its own action convention, path coverage, target and calibration. Using the same numeric output for both would create a hidden target mismatch.

Rejected and ignored signals should remain in the evaluation population where their outcomes can be observed. Otherwise a qualifier can appear excellent simply because only selected trades are ever studied. Missing outcomes and selection policies must accompany its scorecard. This thesis adds no Scanner integration, qualification capability, execution entitlement or new milestone number; their implementation placement remains separately governed.

# 28. Sector Rotation / Monitoring Seam

Sector Rotation could later supply PIT context or become the subject of a separately defined relative-performance target. It remains a distinct analytical capability, not a side effect of training A7. Existing sector-context interpretation should not be renamed a rotation engine merely because it is available. Historical mappings and regime labels must themselves respect the decision cutoff.

:::figure 23 Acyclic context and operational boundaries
| Input or consumer | Direction | Ownership retained |
| Future Sector Rotation context | Qualified snapshot → A7 feature admission | Sector engine owns context; A7 owns prediction |
| Future scanner signal | Deterministic features → A7 → qualification | Scanner and qualifier retain separate decisions |
| Future Monitoring Runtime | Bounded refresh/evaluation invocation → A7 | Runtime owns scheduling, budgets and dispatch |
| Retraining proposal | Drift/outcome report → engineering review | A7 does not self-schedule or self-promote |
:::

Monitoring can later schedule forecast refresh, outcome acquisition or drift evaluation. A7 should expose semantic needs and bounded operations, not embed a daemon in its estimator. A captured-read replay does not become fresh evidence merely by being invoked repeatedly. A missing outcome may need acquisition, but no automatic provider backfill is authorized by this architecture or thesis.

Shared market evidence can be reused without merging analysis state. Two subscribers may share a price snapshot while retaining different purposes, horizons, entitlements and result lineage. Repeated requests for the same subject/target/cutoff should not overweight training data, yet their original request references must remain available for audit.

A8 retains TM integration, A9 Scanner integration and A10 operational hardening. Sector Rotation and Signal Qualification have separate unresolved placement. The diagrams establish direction and ownership, not a mandatory deployment topology or permission to build future runtime during thesis creation.

# 29. Replay and Reproducibility

“Reproduce the result” can mean four different operations. Recorded replay reconstructs a stored forecast without executing a model. Pinned inference verification reruns the exact captured feature/model/calibrator/policy combination. Comparative evaluation creates a new report over identified records. Training reproduction refits an artifact under the original data, seed, dependencies and procedure. Calling all four replay obscures both cost and trust.

:::figure 24 Lineage survives a newer model and a corrected outcome
| Decision-time chain | Later append-only chain | What must not substitute |
| Features → target/window → model/calibrator → forecast fingerprint | Outcome revision → dataset → evaluation report | Today's data for captured features |
| Exact capture stores probability, gaps and controls | New training artifact → explicit approval | Latest model for the original model |
| Recorded replay reads the capture only | New COLD binding affects future runs | New label or policy inside an old capture |
:::

Exact recorded replay should work even after the original fit library is uninstalled, provided the retained capture and rights are sufficient. Missing model artifacts may prevent inference verification while recorded replay still succeeds. The report must distinguish these outcomes rather than contact a service to “repair” history.

Floating-point and environment differences complicate recomputation. The draft proposes separate tolerance reporting across environments, including 1e-10 probability and 1e-8 scalar-metric absolute tolerances, to be frozen in fixtures. These are engineering verification tolerances, not statistical calibration tolerances. A changed numeric result cannot retain an identical semantic fingerprint by assertion, and changed classification/abstention at a boundary always fails verification.

Training needs still more pins: row and feature order, every seed, RNG method, solver/convergence settings, threads, data revisions and dependency/environment identity. A numerically close refit with a different checksum is a different artifact. No retraining operation can change the meaning of an old forecast or the label revision used by an old dataset.

# 30. Explainability and Non-Causality

A useful explanation names exactly what is predicted, for which horizon and reference, by which artifact, with what historical calibration and which missingness or applicability limits. It should say what comparison established incremental value—or clearly state that no such value has been established. Merely attaching a model name and a confident adjective does not answer those questions.

For the proposed logistic reference, feature-wise standardized coefficient contributions can describe the raw logit. Calibration is a separate transform, so a contribution to the logit is not a directly additive number of probability points. Correlated features can complicate interpretation. A positive coefficient does not establish that changing the real-world feature would cause the predicted outcome.

An illustrative explanation might read: “This shadow artifact estimates the specified next-session endpoint event. Its admitted feature snapshot includes the pinned return and volatility fields. The displayed contributions describe the fitted computation, not causal drivers. The forecast does not measure option profit, and required regime support is limited.” That is more informative than a generated market narrative which invents motives for price movement.

User-facing explanation should retain uncertainty, contradictions and baseline disagreement. A short view can summarize, but an audit view must resolve the actual input/model/calibration and policy references. The Shell owns rendering, not evidence creation. Rich natural-language interaction remains later work; the thesis itself does not implement it.

The strongest explanation is often a precise reason for absence. “Unqualified terminal session schedule” or “calibration review expired” tells a user what is missing without implying that a smaller numeric score would have fixed the problem.

# 31. Cost, Privacy and Security

Local prediction is not free computation merely because it uses no external LLM tokens. Training, inference, evaluation, storage and data rights have different costs. The draft starts with a small CPU model and finite limits on rows, features, folds, trials, iterations, elapsed time, memory and artifact size. An exhausted budget yields a typed incomplete or stopped operation, not a half-trained model labeled complete.

| Principle | Practical consequence |
| Local default / no implicit egress | No training data upload, external telemetry or model download by default |
| Separate training rights | Data access alone does not establish permission for retention or shared training |
| Optional dependencies | Core, A5/A6, Shell help and recorded replay do not need training SDKs |
| Trusted artifact format | Validate declarative formats, size, origin and checksum; no arbitrary executable model path |
| Explicit cost knowledge | Zero external billing can coexist with unpriced local resources |

Personal portfolios and trade histories are not default shared-training material. Their selection bias and sensitive context require explicit scope, consent, tenant isolation and retention rules. Evidence text and artifacts remain untrusted inputs, not tool instructions. No model manifest grants filesystem access, execution authority or a new provider entitlement.

R1–R5 continue to apply: required scope does not shrink with availability; discovery is not readiness; replay pins exact versions; integrations remain isolated; startup composition is trusted and COLD. HOT replacement is deferred. Consumer requests cannot switch the registry's owner configuration mid-run.

Immutability does not override retention or deletion obligations. If an artifact must be removed under applicable governance, record the loss and resulting replay limitation rather than promising impossible permanent reproduction. This is a system-design boundary, not a legal determination about any particular dataset.

# 32. Failure Modes

Failures must remain facts about the pipeline, not fabricated market conclusions. An unavailable model is not a 50% forecast; a missing feature is not zero; a rejected trade is not a negative label. Clear failure types let users see which layer failed and whether the deterministic path still has enough evidence to operate.

| Failure | Forecast/evaluation response | Lower-layer consequence |
| Required feature or PIT proof missing | Abstain; preserve required denominator | No model agreement inferred |
| Calibration or approval absent/expired | Unavailable; no numeric substitute | A4/A5/A6 retain their own gates |
| Leaked dataset | Invalid experiment; rebuild with new lineage | No apparent accuracy enters admission |
| Outcome missing or ambiguous | Pending/censored/ineligible for that label | No fabricated loss, gain or fill |
| Model checksum / verifier missing | Integrity failure or verification unavailable | Recorded replay only if its own capture is valid |
| Budget exceeded | Typed stop; no partial artifact promotion | No expensive automatic fallback |
| Drift / unsupported regime | Restrict or suspend under pinned policy | Valid deterministic path remains visible |

There are two dangerous shortcuts. One hides failure to make the product feel smooth: filling an absent forecast with a neutral probability. The other treats any uncertainty as a universal failure of TI: disabling a valid deterministic assessment simply because an optional model is unavailable. Both collapse independent semantics.

Security and operational failures must preserve original causes and safe identifiers without leaking credentials or private paths. A failed replay must not fetch today's data. A source correction must not quietly replace an old prediction. A model that scores fewer cases must not obtain a deceptively better scorecard by losing difficult cases from its denominator.

The intended acceptance corpus therefore includes failures deliberately. A system that faithfully rejects an overfit or leaked candidate can be correct engineering even when it has no admissible real model. That distinction prevents an acceptance process from rewarding attractive performance claims over honest evidence.

# 33. Worked Examples

All ten cases below are **illustrative synthetic teaching scenarios**. They assert no live prices, calendars, model results, qualified datasets or actual approvals. Unless a case says otherwise, the target is next-session close strictly above the known reference close, with supplied sessions S0/S1, an S0-after-close cutoff and issuance before S1 opens. Model identifiers are invented, and probabilities describe hypothetical artifacts. Decisions refer to forecast admission or engineering review—not broker actions.

## Case 1 — Well-calibrated positive next-session forecast

**Context and scope.** A hypothetical KAYNES cash-equity request has qualified captured A2 features and a supplied next-session schedule. Its reference close is 100.00 in illustrative units. Target `equity.next_session_close.return_gt_zero/1.0` ends at the supplied S1 close; it is not the horizon of a proposed option contract.

**Model and forecast.** Invented Model A/1.0 with Cal-A/1.0 produces 0.70 and records its issue before the outcome. In the invented held-out cohort, 690 of 1,000 predictions in this exact-probability group were positive. Assume, solely for the scenario, that required broader controls, uncertainty, sample and shadow gates have separately passed a preregistered policy.

**Evaluation and decision.** This makes the candidate eligible for an explicit advisory approval, not automatically approved. A qualified S1 close of 101.00 later gives this one case label one. Its Brier contribution is (0.70 − 1)² = 0.09. One correct case does not validate calibration; the cohort evidence and all other gates remain necessary.

**Downstream effect.** A4 and A6 retain their frozen results. A reader may see the estimate as a labeled short-horizon diagnostic. It does not select a CE, imply 70% option-profit probability or authorize capital. If TM rejects an otherwise proposed trade, that operational decision remains independent of the positive label.

## Case 2 — Overconfident model rejected

**Context and scope.** A hypothetical qualified RELIANCE request uses the same exact endpoint target and next-session horizon. There are no known input gaps in this invented case; the problem is model quality, not missing evidence.

**Model and forecast.** Model B/1.0 with Cal-B/1.0 proposes 0.90. The invented test group contains 1,000 such predictions but only 620 positive outcomes. Its group Brier score is 0.62 × 0.01 + 0.38 × 0.81 = 0.314. A plausible ranking statistic elsewhere cannot repair this badly overstated numeric confidence.

**Evaluation and decision.** Assume the predeclared calibration gate rejects that discrepancy. The model is rejected for admitted probability use. The failure is not fixed by displaying 0.62 for the current request after inspecting the test; that would be a new calibration/selection step requiring proper separation and later evaluation.

**Why and downstream effect.** The estimate's frequency meaning is unsupported. The forecast can remain a recorded engineering diagnostic, but the user-facing admission is unavailable rather than “very bullish.” A4/A5/A6 do not inherit a bearish conclusion from the failed model; they keep their own evidence, disposition and requirements. No probability is altered in an old capture.

## Case 3 — Leaked feature invalidates a backtest

**Context and scope.** Model C/1.0 advertises excellent results from a supposed 10:00 prediction that includes an 11:00 high. This intraday story is deliberately **outside v1's supported horizon** and demonstrates leakage, not an approved new target. The same error would occur in v1 if a future S1 high entered the S0-after-close feature snapshot.

**Model and forecast.** The invented artifact records a candidate score of 0.95 and impressive retrospective metrics. Its calibrator identity is Cal-C/1.0, but a named calibrator cannot make unavailable information legitimate.

**Evaluation and decision.** The feature's event/availability time is after the stated cutoff. The experiment is invalid before any calibration or promotion claim is considered. Unsupported horizon and leaked information are separately recorded; neither is a small quality warning to average against a strong metric.

**Why and downstream effect.** The model answered a question with information from its answer period. Repair requires a new eligible dataset and experiment, retaining the failed lineage. No A4/A6 policy changes, no live test is manufactured, and the old apparently successful backtest cannot remain in an approved scorecard as if it had merely been recalibrated.

## Case 4 — Model worse than the base-rate control

**Context and scope.** An invented matched test cohort for the initial next-session target has 600 positive and 400 zero labels. The prior control's probability, fitted earlier on training data, was fixed at 0.60. It was not estimated from this test set, although the test frequency happens to match it in the illustration.

**Model and forecast.** Model D/1.0 plus Cal-D/1.0 outputs 0.50 for every test case. Its Brier score is 0.25. The prior control's score is 0.60 × 0.16 + 0.40 × 0.36 = 0.24. The candidate therefore performs worse on the same target and rows. No row or symbol can be removed after seeing this result.

**Evaluation and decision.** The OOS improvement gate fails; the model is not promoted. This arithmetic demonstration does not by itself assess confidence intervals or stability—those would be additional requirements, not ways to ignore the failed point comparison.

**Downstream effect.** The prior remains visible as the control; it is not automatically granted trading authority either. A2/A4/A6 keep their original outputs. A correct evaluation system should be willing to conclude that the candidate adds no established value, even when producing the candidate required substantial effort.

## Case 5 — Strong-looking metrics, insufficient sample

**Context and scope.** Model E/1.0 and Cal-E/1.0 target the same next-session endpoint across an invented multi-equity dataset. The report shows 2,000 rows, but these originate from just two shared sessions. Headlines emphasize agreement with outcomes and apparent calibration near the 0.70 band.

**Forecast and evidence.** A current hypothetical HDFCBANK request would receive 0.70. The reviewer sees that many observations share market conditions and the claimed deployment regimes have almost no independent temporal support. A large row count has not created a large number of independent market episodes.

**Evaluation and decision.** Under the scenario's preregistered distinct-session and cohort gates, sample adequacy fails. The disposition is insufficient empirical support, not a passing model with a cosmetic low-confidence footnote. No universal required count is being specified by this example.

**Why and downstream effect.** The artifact may remain useful for mechanical tests, but its probability is not admitted for the unsupported use. More qualified prospective or chronological data is needed; repeating the same rows does not help. Frozen deterministic TI continues where valid. Neither a confidence interval computed under false independence nor a per-symbol recalibrator can manufacture the missing temporal evidence.

## Case 6 — Regime instability blocks promotion

**Context and scope.** Model F/1.0 with Cal-F/1.0 predicts the initial endpoint target across two predeclared PIT regime cohorts. Most examples come from ordinary conditions; a required stressed-condition cohort is smaller but still large enough to reveal a material weakness under the illustrative protocol.

**Forecast and evidence.** In the ordinary invented cohort, forecasts around 0.70 observe positives near 0.69. In the stressed cohort, predictions around 0.80 observe positives near 0.40. The pooled average can obscure this difference because ordinary cases dominate.

**Evaluation and decision.** Broad proposed applicability is rejected. A restricted model might be considered only through an explicit scope/approval decision with validated regime identification and its own evidence. The reviewer cannot retroactively redefine the regime after finding poor performance or silently omit it from the claimed domain.

**Why and downstream effect.** An aggregate metric does not certify every required use. At a current request with unknown regime classification, the model must not assume ordinary conditions. A4/A5/A6 remain unchanged. The case illustrates why regime-stability criteria and PIT cohort definitions must be fixed before holdout inspection; it does not implement a new Sector Rotation or regime engine.

## Case 7 — Drift suspends forecast admission

**Context and scope.** Invented Model A/1.0 previously passed the required review and shadow process for advisory use of the same endpoint target. Its original calibration evidence remains valid as a historical record; it is not rewritten when conditions change.

**Forecast and evidence.** Later mature observations in the scenario show a 0.70 band occurring near 0.50, alongside increased feature missingness. The pinned drift policy distinguishes calibration deterioration from coverage drift. Assume it has enough qualifying evidence and its suspension criterion is met; the numeric discrepancy is not a universal production threshold.

**Evaluation and decision.** New forecast admission is suspended in the affected scope. Pending outcomes remain pending. The system does not subtract 0.20 from forecasts or switch to the newest model. A review or retraining proposal may follow, but activation requires its own approval and COLD composition.

**Downstream effect.** A valid deterministic A4/A6 result continues, visibly without an admitted A7 overlay. Old forecasts still replay with their original 0.70 values and model identity. Suspension changes eligibility for new use, not the meaning of past records or TM's authority. No recurring monitor is run by this thesis.

## Case 8 — A7 unavailable, deterministic TI continues

**Context and scope.** A hypothetical captured KAYNES request has sufficient qualified evidence for its existing A4 and A6 paths. The desired A7 request would use the initial next-session target and supplied S1 window.

**Model and forecast.** The configured exact Model A/1.0 pin is unavailable; therefore there is no executed forecast and no probability value. Its hypothetical prior evaluation is irrelevant to the inability to resolve the required current artifact. The result must not default to 0.50, borrow a model version or omit the required participant.

**Evaluation and decision.** Admission returns unavailable with a missing-pin reason. Recorded replay of a separately valid historical capture may still succeed, because it does not execute that model. Inference verification remains unavailable until the exact supported artifact is present.

**Why and downstream effect.** A7 is optional to the frozen controls. A4's disposition and A6's eligible candidate/rank remain exactly as their qualified inputs and policies determine. If those controls had their own missing requirements, they would still fail appropriately; the fallback promise is not a bypass. TM decides any operation independently. No provider fetch, training job or order is launched to conceal the missing overlay.

## Case 9 — Rejected candidate and a later label correction

**Context and scope.** An invented RELIANCE forecast uses reference 100.00 and the supplied next-session endpoint. Model A/1.0 with Cal-A/1.0 records 0.70. TM rejects a proposed operation for its own capital reason; the forecast itself remains an analytical record.

**Observed outcome.** A first qualified terminal observation is 100.01, so journal revision J1 labels the event one. No fill or realized trade P&L exists. A later sourced correction reports 99.99; journal revision J2 links to J1 and changes the label to zero under the same strict comparator, with its later availability recorded.

**Evaluation and decision.** A new report can use J2 when eligible. A dataset pinned to J1, especially one created before J2 was available, keeps that version. The forecast stays 0.70 in both histories; its apparent outcome changes because the observation changed, not because the model updated itself.

**Downstream effect.** The rejected operation does not become a failed trade or an implicit short. Studying the market label can improve understanding of rejected-candidate coverage, but it cannot establish that executing the rejected operation would have earned a particular amount. The full correction chain remains replayable within retention and rights.

## Case 10 — Corporate-action coverage prevents a label

**Context and scope.** A hypothetical ATHERENERG request concerns the initial endpoint target, not an actual forecast for that company. Model G/1.0 and Cal-G/1.0 are illustrative candidates, but the supplied evidence cannot establish the required action coverage and same-basis reference/terminal comparison for the target window.

**Forecast and evidence.** A candidate engineering score of 0.75 is not admitted as forecast evidence. Unknown action coverage is a required-evidence problem; the existence of a number does not satisfy it. If a price-basis-changing event is discovered only after an already issued forecast in another case, the architecture permits label censoring with explicit provenance rather than retroactive forecast repair.

**Evaluation and decision.** The current request abstains under the missing qualification. An unavailable terminal label remains ineligible or pending as appropriate, never class zero. A corrected/adjusted historical series downloaded later cannot silently fill the missing PIT proof.

**Why and downstream effect.** Restricted datasets may omit important event periods. The report must show those exclusions and the resulting limits on generalization. Frozen A4/A5/A6 follow their own requirements; none receives an invented favorable probability. The case motivates a reconciliation question about outcome-availability reporting, not an approved relaxation of the draft's action policy.

# 34. Frequently Asked Questions

## Q01. What does a 70% forecast mean?

It estimates the probability of one precisely named event within a defined eligible cohort and information boundary. Here that is the next qualified session closing above a known reference. If probabilities are well calibrated, comparable cases near 70% should have event frequencies near that level over appropriate samples. It does not say that this particular price move is assured or large.

## Q02. Is it a guarantee?

No. The complement remains possible, and the model can also be miscalibrated or outside its valid domain. A legitimate single failure is compatible with a useful probability model. The relevant questions are calibration, comparative quality, applicability and uncertainty across qualified observations—not whether every prediction succeeds.

## Q03. Why not use the highest accuracy?

Accuracy depends on prevalence and a decision threshold. A constant positive classifier can look excellent in an overwhelmingly positive cohort without separating useful cases. It also ignores the degree of overconfidence and economic consequences. Use matched proper scores, reliability, coverage, stability and explicitly supported utility alongside descriptive hard-label metrics.

## Q04. What is calibration?

It is agreement between stated probabilities and observed event frequencies over comparable groups. A fitted recalibration step is an attempt to improve that relationship, not proof of success. A7 asks for separate held-out fitting and later evaluation, with counts, cohort definitions and uncertainty kept visible.

## Q05. What is Brier score?

In this binary convention it averages the squared difference between probability p and label y. A 0.90 prediction followed by zero contributes 0.81; followed by one, 0.01. Compare it on the same eligible rows and target. A lower value is useful, but it is not by itself a complete calibration or profitability certificate.

## Q06. Why not train on all historical data?

Some history lacks qualified availability, universe or action vintages. Some must remain unseen to evaluate model selection honestly. If all outcomes influence fitting, the final score describes familiarity with those outcomes, not a clean future-prediction test. Later generations can use newly mature data under a new frozen chronological plan and holdout.

## Q07. Why are random splits dangerous?

Adjacent examples can overlap in outcome time, and different symbols share sessions. Random row assignment can place later information in training and related earlier cases in test. The proposed protocol instead respects chronological partitions, session groups and label-information intervals. Time ordering still needs additional PIT and preprocessing checks.

## Q08. What is walk-forward validation?

It repeats a simulated train/calibrate/select/test process as time advances, with only then-available information at each fitting cutoff. Expanding windows retain earlier eligible history; rolling windows use a bounded recent span. All folds and gaps remain visible, and previously scored rows are not repeatedly advertised as new independent evidence.

## Q09. What is leakage?

Leakage is use of unavailable information or outcome-dependent choices in a supposedly earlier prediction. Examples include an 11:00 high in a 10:00 row, today's survivors defining yesterday's universe, or later revisions entering earlier features. A leaked result is invalid evidence of predictive ability, even when its metrics look excellent.

## Q10. What is overfitting?

It is adaptation to peculiarities of the development evidence that does not generalize adequately. The process can overfit through model complexity, repeated trials, subgroup selection or holdout peeking. Simpler models help limit some risks but do not eliminate them. Independent chronological evaluation, trial records and later shadow evidence remain necessary.

## Q11. Why keep the deterministic baseline?

It is an explainable control and a valid independent path when its own requirements are satisfied. Without it, improvement claims lack a stable reference and model outages can remove all intelligence. Preserving it also exposes disagreement and prevents a new score from silently erasing NO_TRADE, source gaps or hard candidate gates.

## Q12. Can the model learn from my trades automatically?

Not under proposed v1. Private trading records require explicit data governance and can be a selected, biased sample. Outcomes may motivate a later authorized offline experiment; fitting, review, shadow, promotion and COLD activation remain separate. A trade outcome cannot directly rewrite an active model or alter execution authority.

## Q13. Can a model be disabled?

Yes, the proposed lifecycle includes suspension and retirement. Approval is scoped and time-bounded, not permanent because an artifact exists. Denying new admission does not change old recorded forecasts. Rolling back to another artifact requires explicit approved selection rather than an unrecorded hot swap.

## Q14. What happens on drift?

The pinned policy evaluates feature, calibration, performance, regime and coverage evidence separately. It may warn, restrict or suspend admission and produce a review/retraining proposal. Pending outcomes stay UNKNOWN. There is no automatic probability correction or self-promotion, and deterministic TI retains its own result and gates.

## Q15. What happens if A7 is unavailable?

The system reports an explicit unavailable overlay; it does not insert a neutral probability. A4/A5/A6 continue only if their own inputs and authority are valid. Their original results remain unchanged. A missing model does not justify live repair during replay, and a valid baseline does not require a forecast to exist.

## Q16. Does A7 decide quantity?

No. It may eventually support analysis under a separately approved utility profile, but that does not establish account capital, margin, live limits or executable size. TM retains operational risk, quantity and capital decisions. A probability or per-unit hypothetical outcome is not an allocation instruction.

## Q17. Does A7 execute trades?

No. TI is intelligence and advice, TM governs operational action and broker coordination, and the broker supplies execution truth. Neither a high probability nor a model promotion event grants order authority. No provider/model/broker operation was performed to build this thesis's teaching cases.

## Q18. Will A7 choose option strikes?

Not in the initial proposal. A6 owns supported expression candidates and their selection policy. The binary cash-equity endpoint forecast cannot determine which strike or expiry has suitable economics. Any forecast-enhanced comparison requires compatible expression data and targets plus separately accepted consumer policy.

## Q19. How does A7 help A6?

Initially it establishes an auditable forecasting/evaluation foundation. Later qualified path or expression forecasts may inform comparison of already valid A6 candidates, while retaining deterministic ranks and rejected reasons. That future possibility is not an implemented reranker, and a bullish probability is not option POP.

## Q20. Why abstain?

Because the admitted evidence or applicable model may not justify a useful estimate. Missing calibration, unsupported scope and stale approvals are not repaired by a numeric guess. Softer selectivity may also be appropriate under a validated threshold. The reason and resulting coverage must remain visible rather than hidden behind confidence language.

## Q21. Why not deep learning first?

The initial challenge is trustworthy data, targets, calibration and evaluation, not merely model capacity. More complexity introduces compute, reproducibility and selection burdens before benefit is established. A small logistic reference and meaningful controls provide a benchmark that later complexity must beat under the same qualified protocol.

## Q22. Can models disagree?

Yes. Compare exact targets, horizons, information cutoffs and cohorts before calling outputs contradictory. Two probabilities for different events may both be reasonable. If comparable models disagree, preserve their individual artifacts and evaluation limits. An average does not automatically resolve disagreement or become calibrated.

## Q23. What is an ensemble?

It combines multiple model outputs under a defined rule. The rule, component versions and weights are part of the artifact. Its combined score still needs appropriate calibration and validation. A larger collection of opinions is not inherently more accurate, independent or trustworthy than a simpler model.

## Q24. Why are ensembles deferred?

The first version needs to establish the complete single-target evidence chain. Ensembles add fitting, dependency, calibration and governance complexity, including the risk of training weights on the wrong partition. They can be reconsidered when incremental OOS benefit and a bounded cost/replay policy justify them, not because a diagram can accommodate them.

## Q25. What is shadow mode?

It prospectively records predictions and failures while the existing decision path remains unchanged. Later outcomes are joined for evaluation. It is not a synonym for a historical backtest or quiet operational influence. Required duration, distinct sessions and mature-label coverage must be fixed by policy before a model can claim shadow success.

## Q26. How is replay possible with ML?

Recorded replay reconstructs captured probabilities, reasons and fingerprints without invoking a model. Pinned verification separately reruns the exact retained artifact and input under a supported environment. Training reproduction is a third, explicitly costly engineering task. Separating them makes historical explanation possible even when a newer model exists.

## Q27. Can retraining change old replay?

No. A new model has a new artifact identity and affects only separately admitted future runs. Old forecasts retain their exact model/calibrator and evidence references. A later label correction also gets a new revision; it cannot overwrite the dataset version used by an earlier report.

## Q28. How do we prove a model is better than A2/A4/A6?

First match the question, population and outcome. Probability metrics compare compatible forecasts and calibrated controls; ordinal A2/A4 states and A6 ranks need separately defined observational or economic comparisons. Keep selection, coverage, cost and uncertainty visible. Some comparisons are NOT_EVALUABLE; better scores do not alone prove causal trading benefit.

## Q29. Why expected utility over win rate?

Frequent small gains can be overwhelmed by rare large losses, and users differ in their tolerance for downside and holding constraints. Utility makes those preferences explicit under defined outcomes and costs. The initial binary forecast lacks payoff magnitude, so it cannot provide monetary expected utility or take over TM's operational risk decisions.

# 35. Future Evolution

The future is a sequence of evidence gates, not a promise that the most elaborate model will eventually win. The proposed v1 establishes one target, captured features, labels, chronological evaluation, calibration, a local registry and governed shadow/advisory evidence. It is acceptable for this pipeline to reject every real candidate model while passing its engineering tests. Empirical model readiness is a separate conclusion.

:::figure 25 Proposed evolution — no runtime delivered by this thesis
| Stage | Bounded question | Gate before widening |
| A7.1 | Are targets, features, labels and PIT datasets well defined? | Contracts, chronology and preregistered numerical protocol |
| A7.2 / A7.3 | Does a simple candidate earn trust and preserve replay? | Controls, calibration, registry and explicit approval |
| A7.4 / A7.5 | Can bounded users inspect shadow/advisory evidence safely? | Facade/Shell parity, corpus, failures and closure |
| Later independent scope | Distributions, options, ranking, ensembles or operational learning? | New targets/data/consumer policies; no implicit promotion |
:::

Longer horizons and other asset classes need different observation and calibration support. Path forecasts need qualified paths, not merely endpoint bars. Options require historical contract availability, units, liquidity and timing. Cross-candidate ranking needs a comparable universe and tie/selection policy. None is supplied by adding another output column to the first binary model.

The broader roadmap preserves A8 TM integration, A9 Scanner integration and A10 operational hardening. Sector Rotation, Signal Qualification, HOT composition, Web/NLP and large-scale infrastructure remain separately gated. Proposed forecast/model capability names are not callable today: the public/engineering catalog still contains nine existing operations.

This thesis comes before architecture reconciliation and independent acceptance. It should help the user recognize unsupported claims, not persuade them that implementation must begin immediately. The next chapter records questions uncovered by teaching the design. They are not changes to the architecture, and the three primary A7 source drafts remain unchanged during creation.

# 36. Thesis Findings for Architecture Reconciliation

These findings classify issues for the next pass. NO_CHANGE preserves a decision; CLARIFICATION_NEEDED asks for sharper normative meaning; ARCHITECTURE_CHANGE_PROPOSED requests an explicit design decision; IMPLEMENTATION_DETAIL_ONLY belongs to a later bounded implementation; DEFER preserves future scope. No finding is applied to the current architecture or treated as an accepted rule in the worked cases.

## TF-01 — Binary target usefulness

**THESIS_FINDING TF-01 — CLARIFICATION_NEEDED:** The target is intentionally narrow, yet readers may expect immediate A6 value from the major-milestone name. Clarify the initial evidence-of-usefulness claim as an underlying diagnostic and empirical foundation, not delivered expression improvement. Require a separately defined consumer comparison before making stronger claims; do not expand the target merely to make the story attractive.

## TF-02 — Next-session calendar dependency

**THESIS_FINDING TF-02 — CLARIFICATION_NEEDED:** Specify how the qualified source-session/next-session artifact is versioned when an exceptional schedule changes after issuance. The draft already forbids weekday guesses and silent horizon shifts. Reconciliation should resolve which label becomes censored versus which new request is unsupported, and how old captures preserve the original schedule without claiming a calendar engine exists.

## TF-03 — Calibration sample adequacy

**THESIS_FINDING TF-03 — CLARIFICATION_NEEDED:** The numerical profile must distinguish row count, distinct origin sessions, class support and effective cohort information. Specify who approves the statistical precision criterion and how sparse bins or correlated panel rows affect admission. Do not adopt an arbitrary sample threshold from the illustrative 1,000-case chart; no such empirical threshold is chosen here.

## TF-04 — ECE binning and uncertainty

**THESIS_FINDING TF-04 — CLARIFICATION_NEEDED:** Freeze bin edges or the edge-learning rule, empty-bin handling, weighting, uncertainty presentation and minimum support before test. Clarify that ECE and Brier alone cannot certify calibration. Keep the planned reliability evidence directly visible rather than compressing it into a single user confidence field. This is policy specification, not a new calibrator recommendation.

## TF-05 — Promotion thresholds and review independence

**THESIS_FINDING TF-05 — CLARIFICATION_NEEDED:** The draft requires preregistration but leaves concrete parameters to A7.1. Clarify the approval owner, evidence needed to justify bounds and the consequences of repeated holdout inspection. State how a changed protocol obtains a new version and untouched evidence. Missing values must block real empirical work, not become negotiable after a model looks promising.

## TF-06 — Regime-stability definition

**THESIS_FINDING TF-06 — CLARIFICATION_NEEDED:** Distinguish a required applicability cohort from an exploratory diagnostic subgroup. Specify whether narrowing approval after seeing a weak regime requires a new independent test, and how unknown PIT regime identity behaves. Preserve poor-cohort results in the report rather than allowing data-dependent regime naming to hide failure. No regime engine is added by this finding.

## TF-07 — Shadow duration and information content

**THESIS_FINDING TF-07 — CLARIFICATION_NEEDED:** Define shadow acceptance jointly by prospective time, distinct sessions, matured labels and coverage/failure accounting. Clarify how interrupted collection or delayed outcomes affect completion. Calendar duration alone should not imply adequate evidence, and repeated captured replay should never satisfy prospective issuance. Exact values remain a preregistered protocol decision rather than thesis policy.

## TF-08 — Drift thresholds and delayed labels

**THESIS_FINDING TF-08 — CLARIFICATION_NEEDED:** Specify precedence between artifact expiry, health-evidence expiry, missing mature labels, feature drift and measured calibration drift. The draft already forbids stale silent use and automatic recalibration. Explain which situations require abstention before enough outcomes exist for a performance judgment, without accidentally inventing a Monitoring Runtime in the pure evaluator.

## TF-09 — Outcome-availability report as a first-class artifact

**THESIS_FINDING TF-09 — ARCHITECTURE_CHANGE_PROPOSED:** Consider making an immutable evaluation-population disposition report mandatory beside each empirical scorecard. Pin expected rows, matured labels, rejected/untraded cases, censoring, missing actions and revisions so reviewers can inspect selection before metrics. The draft already requires these counts; the proposed change is their independently identifiable report/acceptance contract, not relaxed eligibility. Reconciliation may decide the existing EvaluationReport is sufficient and reject the extra artifact.

## TF-10 — Corporate-action exclusions and selection

**THESIS_FINDING TF-10 — CLARIFICATION_NEEDED:** Explain the conditional population implied by excluding action-affected/unknown-coverage windows, especially when the reason becomes known only after issuance. Clarify reporting and uncertainty around informative censoring without labeling excluded rows as losses or retroactively changing features. Retain unadjusted same-basis v1 and leave adjusted-history policy deferred.

## TF-11 — Reproducibility tolerance

**THESIS_FINDING TF-11 — CLARIFICATION_NEEDED:** Keep exact recorded replay, same-environment inference verification and cross-environment tolerance reports distinct. Specify tolerance handling at classification/abstention boundaries, coefficient scaling and environment support. The draft's 1e-10/1e-8 values are proposed engineering tolerances, not statistical quality bounds; a new checksum must never be reported as an identical artifact merely because predictions are close.

## TF-12 — Model-registry scope

**THESIS_FINDING TF-12 — NO_CHANGE:** Retain local immutable manifests and append-only lifecycle events with engineering inspection. Registration is neither approval nor a public capability. No service, universal plugin loader, public promotion command or current-model substitution is needed for v1. Any A7 startup selectors or publication require their own versioned R5/facade acceptance.

## TF-13 — Feature-attribution presentation

**THESIS_FINDING TF-13 — IMPLEMENTATION_DETAIL_ONLY:** Render logistic contributions in their actual raw-logit basis, retain transform identity and show calibration separately. Label uncertainty and missing features; do not display logit contributions as additive probability points or causal effects. Allowlisted explanation/trace rendering should be tested against the exact captured numerical fields in the later implementation.

## TF-14 — A4/A5/A6 admission

**THESIS_FINDING TF-14 — NO_CHANGE:** Preserve no automatic v1 influence and separate owner policies. Exact subject/target/horizon/applicability must precede future interpretation. A4's non-action gates, A5's position/A4 requirements and A6's qualified candidate set remain intact. A favorable probability cannot rescue missing evidence or confer TM/broker authority.

## TF-15 — Forecast staleness

**THESIS_FINDING TF-15 — CLARIFICATION_NEEDED:** Separate model approval validity, calibration-review validity, input freshness, forecast use-by and target endpoint in public explanations and admission precedence. A prediction about tomorrow is not necessarily usable until tomorrow. Clarify how a delayed issue before next-session open differs from a later attempt to reuse the same forecast and how trusted admission time prevents backdating.

## TF-16 — Advanced models and broader targets

**THESIS_FINDING TF-16 — DEFER:** Preserve distributions, target-before-stop, option POP, position deterioration, ranking, ensembles, deep/RL models and automated operations as separately gated work. The educational need for these concepts does not make them mandatory initial implementation. Keep current deferral ownership and prohibit direction-to-utility shortcuts.

## TF-17 — Independence of the deterministic path

**THESIS_FINDING TF-17 — NO_CHANGE:** A7 failure or removal must not mutate otherwise valid A2/A4/A5/A6 results or fingerprints. Conversely, deterministic fallback cannot erase those layers' own missing prerequisites. Test both directions explicitly: valid baseline survives model failure; invalid baseline does not become valid merely because the model is absent.

Findings total: **17 — 11 CLARIFICATION_NEEDED, 1 ARCHITECTURE_CHANGE_PROPOSED, 1 IMPLEMENTATION_DETAIL_ONLY, 3 NO_CHANGE and 1 DEFER.** The proposed additional population-disposition artifact is not adopted, built or assumed in the scenarios. The architecture remains a draft awaiting reconciliation and independent acceptance.

# Appendix A. Sources, Glossary and Reading Guide

This companion is grounded in the repository snapshots recorded in the separate creation record. Markdown architecture governs semantics; historical studies describe their bounded evidence; DOCX/PDF theses are explanatory and non-normative. A7 runtime is NOT_IMPLEMENTED, no model is trained, and all numerical charts/cases in this book are synthetic teaching examples.

| Source group | Repository source | Contribution to this book |
| A7 primary | [Architecture](../../TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md); [roadmap](../../TIAF_A7_DETAILED_ROADMAP.md); [reconciliation](../../TIAF_A7_RECONCILIATION_RECORD.md) | Target, eligibility, three layers, lifecycle, v1 and future gates |
| Deterministic/evaluation | [A2.9](../../TIAF_A2_9_DETERMINISTIC_BASELINE.md); [A2.10](../../TIAF_A2_10_REPLAY_VALIDATION_EVALUATION.md) | Visible control and snapshot/run/outcome separation |
| Specialists | [A3 architecture](../../TIAF_A3_ARCHITECTURE.md); [A3.8](../../TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md); [A3.10](../../TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md) | Independent evidence, orchestration, cost and replay limits |
| Consumer owners | [A4](../../TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md); [A5](../../TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md); [A6](../../TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md); [A6 freeze scope](../../TIAF_A6_4_FINAL_HARDENING_ACCEPTANCE_CORPUS_FREEZE_READINESS.md) | Arbitration, position and expression boundaries; frozen baseline |
| Trust and operations | [Source/provenance](../../TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md); [Monitoring](../../TIAF_MONITORING_ARCHITECTURE.md); [Pluggability](../../TIAF_PLUGGABILITY_ARCHITECTURE.md) | Availability, distinct clocks, authority and pinned composition |
| Product boundary | [System](../../TIAF_SYSTEM_ARCHITECTURE.md); [Ecosystem](../../TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md); [capabilities](../../TIAF_CAPABILITY_MAP.md); [deferrals](../../TIAF_DEFERRAL_REGISTER.md); [Shell](../../TIAF_TI_SHELL_ARCHITECTURE.md) | Current nine-operation catalog, future scope and caller-bound UI |

The earlier A6 user-reference thesis and its documentation-only OOXML/LibreOffice workflow informed presentation. The new book does not modify that thesis or its builder. External calibration, Brier and temporal-split references linked in Chapters 6, 7 and 10 were consulted as primary educational documentation, not authority for TI policy thresholds, a chosen software dependency version or NSE calendar rules. No source offers proof that this proposed model will succeed in markets.

| Term | Meaning in this book |
| Target / label | Precisely predicted event / deterministic answer derived from qualified later observations |
| Cutoff / issue / outcome / promotion | Information boundary / prediction publication / observed event / approved future artifact use |
| Calibration / discrimination | Probability-frequency agreement / ability to order different outcome classes |
| Censoring / abstention | Incomplete outcome eligibility / refusal to issue an admitted estimate |
| Control / shadow | Preserved comparator / prospective non-influencing model record |
| COLD / replay | Trusted startup binding / reconstruction of captured meaning without current substitution |
| PIT / provenance | Qualified knowledge at the relevant time / attributable source and transformation lineage |
| Utility / authority | Declared valuation of consequences / permission owned outside the forecast |

To review a result, ask: What event? Which exact session and reference? What was available? Which model and calibrator? Which controls and cohort? What is missing? Is it valid for this request now? What remains the responsibility of A4, A5, A6 and TM? If the report cannot answer, a precise abstention is better than an unexplained confident number.

**Current checkpoint:** A6 FROZEN; A7 ARCHITECTURE DRAFT; A7 THESIS CREATED; A7 THESIS / ARCHITECTURE RECONCILIATION NEXT; A7 RUNTIME NOT_IMPLEMENTED. The exact next prompt is **TIAF A7 — THESIS / ARCHITECTURE RECONCILIATION PASS**. No implementation, architecture amendment, commit, tag or push is authorized by this book.
