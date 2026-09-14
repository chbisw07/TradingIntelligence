# 1. A platform, not a winning model

Forecasting is a platform capability; forecasters are replaceable scientific instruments. This is the organizing proposition of the Forecasting Framework, or FF. TI should be able to learn that a model is unhelpful without learning that its whole architecture must be replaced. The contracts, independent outcomes, evaluation protocol and historical records should outlive any particular algorithm.

Imagine asking the same precise question of a base-rate control, logistic regression, a tree model and an advanced market-state model. Each instrument may use a different admitted information representation. None may choose a more convenient target after seeing reality. FF makes the question, the answer type, the comparison conditions and the authority boundary explicit. This is more demanding than putting a common method name around several libraries.

This handbook explains a **proposed platform**, not installed software. A6 is FROZEN at `tiaf-a6-baseline`. A7 acceptance remains PAUSED. FF architecture is DRAFT, FF runtime is NOT_IMPLEMENTED, and the existing A7 and FM/LFDE thesis editions remain intact. The [FF architecture](../../TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md) is normative for the proposed design; this book is a non-normative explanation. Its last chapter contains findings for review, not silently applied changes.

:::figure 01 FF inside TI: shared evidence, separate decisions
| Layer | Owns | FF relationship |
|---|---|---|
| A1 / Market Intelligence | Attributed, governed observations | Supplies admitted captures |
| A2 / A3 / A4 | Deterministic baseline, interpretation, challenge | Preserved evidence and dissent; not rewritten |
| A7 Forecasting / FF | Typed inference and complete node traces | Optional forecast records |
| A7 Evaluation / Learning | Common truth, scorecards / authorized candidate changes | Separate owners, not inference privileges |
| A5 / A6 | Position advice / supported expression analysis | Later consumer admission, no automatic overlay |
| TM / broker | Action, risk, capital / execution truth | No authority transferred to FF |
:::

All model outputs, symbols, cohorts, dates, intervals, timings, weights and approvals in the teaching examples are **illustrative and invented**. No model was trained or called to create them. Arithmetic can demonstrate how a score is calculated; it cannot demonstrate measured TI performance, calibration, alpha or implementation readiness.

Read the first thirteen chapters for the platform intuition, the middle chapters for scientific safeguards, and the worked cases for practical decisions. The intended experience is a system that can eventually be inspected and challenged at small scale before expensive research is added. Complexity is a candidate, not a commitment.

# 2. Why the framework exists

Without a platform boundary, a forecasting project often becomes the implementation of its first successful-looking model. Features, target definitions, prediction formats and evaluation notebooks become entangled. Replacing a tree model with a neural representation then changes not merely an instrument but the evidence contract and sometimes the meaning of success. A favorable chart can conceal a changed population, a later label revision or a different prediction window.

FF separates those decisions. An instrument says what it estimates under a pinned configuration. Evaluation says which observations and outcomes are comparable. Governance says what use, if any, the evidence permits. Consumers receive stable records rather than a model-specific object with an implied instruction to trade. A negative experiment becomes useful knowledge because the benchmark and records still work.

| Without stable seams | With the proposed FF boundary | What still needs proof |
|---|---|---|
| Each model prepares its own labels | Evaluation owns one target and journal | Source and session qualification |
| An ensemble hides weak members | Child and parent outputs remain visible | Incremental value on matched observations |
| New weights overwrite old settings | New artifact and COLD binding identity | Independent qualification and approval |
| A persuasive explanation implies confidence | Raw estimate, calibration and authority stay separate | Reliability in the admitted population |
| Research scripts become production dependencies | Optional adapters sit behind typed contracts | Dependency isolation and exact replay |

The payoff is not that every instrument becomes equally trustworthy. It is that differences become discussable in a common language. A slow, expensive instrument might improve a particular target but fail an operating cost limit. A simple instrument might remain preferable because an elaborate candidate has insufficient independent support. Both conclusions should be explainable without suppressing the losing arm.

FF is also not a framework-building excuse. The initial realization uses one target, common truth, a simple benchmark and one candidate. A typed singleton graph can establish mechanics first. No model zoo, plugin marketplace, microservice estate, new forecasting language or autonomous optimizer is needed. The framework earns its existence by preserving scientific meaning across a small number of changes, not by maximizing abstraction count.

# 3. Distinctions that prevent authority drift

Several words that sound similar answer different questions. A forecast estimates an event. A decision selects an action under authority and constraints. A benchmark supplies a reference comparison. A primary is the currently selected advisory root in an exact profile. Calibration concerns the relationship between probabilities and observed frequencies in a qualified population; it does not make a particular future event certain.

:::figure 02 The architecture's separation rules
| Distinction | Practical consequence |
|---|---|
| Framework ≠ forecaster; primitive ≠ composite | Replace the instrument without redefining the platform; identify aggregation explicitly |
| Forecast ≠ ground truth ≠ decision authority | A model cannot label its own success or authorize an order |
| Benchmark ≠ primary; primary ≠ best forever | Retain controls when a future primary changes |
| Shadow ≠ production; role ≠ lifecycle | Collect prospective evidence without influencing decisions |
| Calibration ≠ generation; evaluation ≠ training | Fit, apply and independently qualify under separate authority |
| Self-correction ≠ production mutation | A proposal changes no active binding |
| Voting ≠ probability ensemble; ranking ≠ voting | Discrete choice, probability combination and ordering have different types |
| kNN ≠ ensemble operator | Neighbor logic belongs inside a primitive artifact |
| FM/LFDE ≠ all forecasting; LLM confidence ≠ calibration | Advanced instruments have no privileged scientific status |
:::

Consider an illustrative KAYNES request. A future FF result could say that a qualified next-session endpoint estimate is 0.62. That does not say a CE is suitable, that an option has a 62% probability of profit, or that TM has capital and authority. A4's counter-thesis, A5's position advice and A6's `NO_OPTION_TRADE` remain independently meaningful. A forecast does not erase a veto or reinterpret insufficient evidence as a favorable score.

The same separation applies to failures. A failed optional LLM request is not a bearish observation. A successful forecast can be negative. A schema-valid number can be unqualified for advisory consumption. An approved model can be unavailable for a particular request. A runtime role can be disabled without retiring its artifact. Keeping these axes separate prevents a convenient status summary from changing the underlying record.

The [system architecture](../../TIAF_SYSTEM_ARCHITECTURE.md) and [source-authority design](../../TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md) remain superior constraints. A sophisticated forecaster is still a consumer of attributed evidence, not an issuer of market facts. The technical ability to produce a value never grants permission to use it for a different purpose.

# 4. Stable request and result contracts

The conceptual boundary is `ForecastRequest → Forecaster → ForecastResult`. These are proposed concepts, not a claim that new classes exist today. The request fixes the question and admissible context. The result fixes what was produced, what was absent and how the run can be understood later. Neither carries order-placement instructions, account permissions or execution fields.

:::flow 03 A complete question produces an attributable answer
Caller-bound admitted request: neutral subject + exact target/window + cutoff
↓ Captured evidence references + trusted profile + finite resource scope
FF admission: semantic compatibility, permissions, dependencies and validity
↓ Pinned primitive or typed composition; no request-time fitting
ForecastResult: typed output OR explicit absence + lineage + calibration state
↓ Complete node trace and immutable capture; later advisory exposure only if admitted
:::

A request identifies the neutral subject and venue, target ID/version, reference and terminal session window, as-of/cutoff, evidence fingerprints, permitted context, purpose, approved profile reference and request ID. It selects within caller scope. It cannot supply a model URL, dynamic import path, arbitrary query, training budget or privilege grant. Feature-family differences may be intentional experimental differences; they must not smuggle different target or cutoff meanings into the same comparison.

| Result field group | Meaning | What it must not imply |
|---|---|---|
| Target and horizon | Exact event, units and window | Generic DAY wording proves compatibility |
| Discriminated output | Binary probability, class, or separately admitted later kind | A score can be guessed to be a probability |
| Generation and absence | Generated, abstained, unsupported, unavailable or failed; reasons retained | Missing becomes zero or 0.50 |
| Calibration / uncertainty | Raw or qualified state, artifact and applicable population; limits | Persuasive prose certifies reliability |
| Identity / lineage | Request, observation, node, composition, evidence and replay pins | Symbol alone identifies a run |
| Validity / usage / authority | Issue and valid window; actual/unknown cost; advisory limits | A generated result is automatically consumable |

Semantic collections are frozen tuples accepting ordinary list/JSON input and emitting ordinary JSON arrays. Metadata remains extensible but cannot hide authority, target or calibration semantics. All instants are aware and normalize with `zoneinfo.ZoneInfo("Asia/Kolkata")`; naive values are rejected and JSON emits `+05:30`. A supplied date or session ID is not a fabricated instant. Package version `0.1.0`, existing contract schema `1.0` and future FF schema versions are separate concepts.

No output estimate accompanies an absence merely to make a table look complete. Conversely, an explicitly raw research probability can be stored even when it lacks calibrated advisory qualification. A validity window limits later use; it does not delete a historically correct capture. These distinctions belong in typed fields, not in a footnote users must remember.

# 5. Primitive instruments

Primitive means atomic at FF's composition boundary, not mathematically simple. A tree ensemble may contain hundreds of internal decisions. A neural network contains many transformations. FM/LFDE can contain a tensor, factor system, latent encoder and forecast head. Each still acts as one replaceable FF instrument if its boundary returns the agreed result type and exposes the required internal audit references.

:::figure 04 One boundary, different scientific instruments
| Primitive family | Internal scientific choice | Shared external obligations |
|---|---|---|
| HistoricalBaseRate / Persistence | Training-period event frequency / exact naive rule | Target, cutoff, artifact, output type and common evaluation |
| LogisticRegression | Regularized mapping from admitted features | Fit/scaler/calibration provenance and abstention |
| XGBoost or conventional ML | Qualified nonlinear model and finite search | Same outcomes and retained simple controls |
| kNN | Train-only scaling, distance, neighbors and label rule | No future neighbors or hidden population changes |
| NeuralNetwork | Learned representation and head | Bounded fit, independent validation, exact artifacts |
| LLM | Governed structured model response | Prompt/model lineage, raw probability warning, budget |
| FMLFDE | Explicit and latent market-state internals | Rich family trace plus the same FF contract |
:::

A HistoricalBaseRateForecaster might return a frequency learned from a pinned training population. It is not allowed to recompute that frequency using the test outcomes it is about to predict. Persistence is likewise a specified hypothesis, not a fallback phrase: persisting a discrete previous event and estimating a probability from persistence history are different outputs requiring different definitions.

Logistic regression is attractive as a starting instrument because its feature schema, coefficients, fitted transformations and limitations can be inspected without first explaining a large representation system. This is an engineering rationale, not a theorem that logistic regression is always best. XGBoost, kNN and neural models are candidates for different modeling assumptions. Their package availability does not establish qualified evidence or permission to run.

kNN's neighbor aggregation belongs inside its primitive model artifact. Changing its distance metric, scaling, reference population or neighbor count changes the instrument. It is not the FF operation that combines independent forecasters. Similarly, FM/LFDE's internal complexity does not give it a special consumer API. Pluggability preserves the outside contract while retaining, rather than concealing, meaningful internal lineage.

# 6. Composite instruments and recursion

A composite takes explicitly compatible child results and produces another ForecastResult. This allows a calibrated wrapper, mean, vote or later router to appear where a forecaster is expected. Recursive composition is useful because the platform does not need a separate public contract for every nesting depth. It is safe only when every edge has a declared meaning and the graph is finite.

:::figure 05 Recursion requires explicit types at every edge
| Branch | Transformation | Result admitted to parent |
|---|---|---|
| LLM raw probability | Qualified calibrator → declared class rule | Same-event discrete class or abstain |
| Logistic + conventional ML qualified probabilities | Probability mean → parent qualification → same class rule | Same-event discrete class or abstain |
| FM/LFDE qualified probability | Declared matching class rule | Same-event discrete class or abstain |
| Three class branches | Pinned electorate, quorum and tie policy | Voting class or abstention, not probability |
:::

`ENSEMBLE(XGBOOST)` is a valid conceptual singleton mean if its child satisfies admission. It returns the child's numeric value under that identity operation. It creates no diversification, independence or evidence gain. It still has a separate graph identity and must preserve any child qualification conditions; wrapping an unqualified model in a one-child ensemble cannot qualify it.

`ENSEMBLE(XGBOOST, KNN, NN)` expresses an intended combination, not a blanket admission decision. A mean over incompatible targets remains invalid. `VOTING(LLM, ENSEMBLE(LOGISTIC, ADABOOST), FMLFDE)` is convenient conceptual notation, but a probability mean cannot be fed directly into a class vote. The expanded diagram shows the conversions and qualifications that the shorthand omits. AdaBoost is an illustrative alternative, not a mandated model build.

| Composite | Main purpose | Additional learned dependency? |
|---|---|---|
| Mean / fixed weighted mean | Combine qualified same-event probabilities | None for fixed arithmetic; learned weights require a fit |
| Voting | Resolve compatible discrete outputs | Not necessarily; rules still need qualification |
| CalibratedForecaster | Apply a pinned transformation | Yes, unless a justified qualified identity is used |
| Stacking | Learn a meta-forecast from child predictions | Yes, with leakage-safe training predictions |
| RegimeRouter / future MoE | Select or mix experts using eligible context | Frozen rules or a separately qualified learned gate |

No new DSL is proposed. The notation is explanatory mathematics. Future implementation uses project-native typed configuration, with reviewed operator kinds and references. A string in Shell is not a graph parser, a model loader or an authority to experiment.

# 7. A typed, bounded forecasting DAG

A directed acyclic graph records which results depend on which others. Directed edges give data flow; acyclicity prevents a node from needing its own future output. Types make each edge checkable. Versioned node IDs, model artifacts, transformations, roots and policies make the graph inspectable and replayable. A tree is sufficient for some compositions, but a DAG can represent a shared child without pretending it was run twice.

:::figure 06 Shared-node DAG: two consumers, one captured result
| Node | Depends on | Output reference / execution |
|---|---|---|
| L | Captured request + logistic artifact | Probability; execute once |
| X | Same observation + tree artifact | Probability; execute once |
| C | L + qualified calibrator | Calibrated L result; execute once |
| E | C and qualified X result | Mean with its own qualification |
| V | Explicit class conversions of C and E | Discrete vote; disclose shared L ancestry |
| Run record | L, X, C, E, conversions and V | Every status, reason, pin and actual attempt |
:::

Stable topological traversal with a declared node-ID tie-break makes ordering reproducible; the first runtime can be serial. Node count, depth, fan-in, evidence bytes, output bytes and attempts are bounded before work begins. Reject cycles, self-reference, duplicate IDs, dangling edges and incompatible ports. A malformed graph is not repaired by silently choosing a simpler root.

Shared execution is not independent evidence. If L influences E and also influences V through C, the ancestry must remain visible. Repeating an equivalent child within one operator to multiply its influence is rejected; intentional weights belong in one explicit configuration. Equal numeric outputs alone do not prove two instruments identical. Conversely, renaming the same execution does not make it an independent voter.

:::chart 07 Shared-node work accounting — illustrative units, not benchmarks
cost.png
:::

The chart uses a separate two-root example, not the nested vote in Figure 06: P1 depends on C(L) and X; P2 depends on C(L). Its invented ledger assigns L two work units, X eight, shared calibration C one, and each parent one. Unique work is 13. Naively adding both inclusive parent totals yields 16 because L-plus-C is charged twice. Any actual retry adds its real work, even if its result failed. Wall time is separate; parallel elapsed time is not summed node latency. Unknown monetary cost stays UNKNOWN rather than zero.

Failure remains visible at the expected node. A missing required child makes its composite unavailable or abstained under the pinned policy; it does not silently shrink the denominator. Later routers record unselected children as NOT_SELECTED, not failed or imagined. New evaluation runs can collect missing expert outputs under separate authorization; recorded replay never calls them to complete a table.

# 8. Compatibility is more than syntax

Two results can both be decimals between zero and one and still be incomparable. One may estimate next-session close above reference, another a high-volatility regime, and a third a future option's profitability. FF therefore validates the graph at trusted COLD composition time and validates actual results again at run time. Static descriptors cannot promise that every future input is eligible.

:::flow 08 The semantic admission gate
Same neutral subject, exact event, version, units and reference/terminal window?
↓ Compatible cutoff, availability, validity and admitted application population?
Correct output kind and explicit conversion where needed?
↓ Qualified child calibration and applicable support for a probability mean?
Every required branch, entitlement, integrity and budget condition satisfied?
↓ YES: execute pinned operator / NO: preserve typed rejection and reasons
:::

| Compatibility dimension | Valid illustrative pairing | Invalid pairing |
|---|---|---|
| Event and horizon | Same strict next-session endpoint event | Next-session direction with next-week volatility |
| Subject and basis | Same qualified cash equity and price basis | Underlying return with option contract return |
| Cutoff and window | Same admitted observation key and source session | Yesterday's valid forecast relabeled as today's |
| Output and conversion | Qualified probability to mean; class to vote | Raw score passed as probability; implicit threshold |
| Calibration scope | Exact admitted pipeline and population | Unqualified LLM percentage inside qualified mean |
| Population and inputs | Different admitted features, same comparison target | Different outcomes or later information in one arm |
| Requiredness | All required children produce usable results | Omit failed child and silently reweight survivors |

The invalid composition `VOTING(next-session-direction, next-week-volatility, regime-classifier)` has no coherent electorate. Its members answer different questions. More majority votes do not repair that error. Even two direction labels can differ: strict DOWN excludes unchanged prices, whereas NOT_ABOVE_REFERENCE includes them. Their dictionaries must not be silently conflated.

Different feature sets do not automatically invalidate a comparison. Comparing a price-only model against a price-plus-news model is a legitimate declared hypothesis when both respect the same cutoff, target and eligible population. Requiring identical evidence bytes would defeat that experiment. The common contract instead preserves the different information inputs and tests whether the added family earns incremental value under fair conditions.

Probability means initially require independently qualified, calibrated same-event children. A raw-score stacker would be a separately typed and trained meta-model, not a loophole. An outer calibrator cannot turn an invalid graph into a valid one. The consequence of admission failure is an attributable absence, not a convenient substitute estimate.

# 9. Voting, averaging, ranking and neighbors

Voting answers a discrete question: which class satisfies a declared decision rule across a fixed electorate? A probability mean answers a numeric question: what is the configured combination of qualified probabilities for one event? Ranking orders comparable candidates in a dated universe. kNN is an instrument that uses neighbors internally. These operations differ in both mathematics and authority.

:::figure 09 Four ideas that must not share an overloaded score
| Mechanism | Input → output | Example and limit |
|---|---|---|
| Voting | Common classes / abstain → class / abstain | Two ABOVE, one NOT_ABOVE; vote share is not event probability |
| Probability ensemble | Same-event qualified probabilities → mean candidate | Mean of 0.72, 0.70, 0.69 is about 0.7033; qualification remains |
| Ranking | Compatible scores + exact universe → order and ties | Candidate B before A is not a calibrated probability |
| kNN primitive | Eligible neighbors + fitted metric → declared prediction kind | Neighbor fraction is a raw estimate until evaluated |
:::

The numbers in Figure 09 are illustrative arithmetic. They do not establish calibration or independence. A weighted mean further requires frozen nonnegative weights summing to one. Learned weights need a leakage-safe fitting protocol. Negative weights or omission-driven renormalization are not quietly accepted as equivalent to the initial mean operator.

For voting, quorum uses the fixed declared electorate, not only whichever calls returned. A legitimate ABSTAIN differs from a failed required child. The simplest tie and insufficient-quorum policy abstains. Any supermajority threshold, conversion threshold or alternative tie rule is versioned and independently evaluated; this book invents no production default. For the first binary target, ABOVE_REFERENCE and NOT_ABOVE_REFERENCE are safer names than UP and DOWN because the latter pair can hide flat-return semantics.

Ranking has a different population boundary. It must pin candidate universe, timestamp, score orientation, comparability and ties. It does not override A3 opportunity ordering or A6 expression ranking. A forecast of the same binary event across equities could motivate a later ranking experiment, but comparable probabilities alone do not establish an investable ranking policy or authorize a scanner overlay.

Stacking is not simply a more fashionable mean. Its meta-model learns from child predictions produced without leaking each row's target into the child's fit. The eventual meta-model and any calibration then face independent testing. Each learned layer increases the number of dependencies and experiments that must be pinned, budgeted and justified.

# 10. Calibration: fit, apply, qualify

A probability of 0.70 is not validated by eloquent reasoning. Calibration asks whether forecasts near a probability level correspond to appropriate outcome frequencies in a defined population, with enough independent support and uncertainty reporting. It is a population-level property, not a promise that a particular event will occur, and it can deteriorate under changed conditions.

:::figure 10 Calibration placement changes the pipeline
| Pipeline | Transformation identity | Scientific obligation |
|---|---|---|
| CALIBRATE(A) | Primitive raw output → C_A | Fit on eligible held-out predictions; evaluate separately |
| MEAN(C_A(A), C_B(B)) | Qualified child transforms → mean | Children qualify; parent does not inherit certification |
| C_E(MEAN(A, B)) | Admitted child mean → outer transform | Mean children must already meet admission; outer fit is distinct |
| Nested calibrated composite | All child and parent stages retained | Leakage-safe stage inputs and transitive dependency pins |
:::

The mathematical placements are generally not equivalent. Averaging transformed values differs from transforming an average. An outer wrapper is not permission to combine unqualified raw scores through the probability-mean operator. The miniature follows the existing A7 proposal: regularized logistic output with a separately held-out sigmoid calibrator. An independently justified identity transform may be possible, but cannot conceal missing qualification.

:::chart 11 Reliability buckets — invented frequencies, no qualification claim
calibration.png
:::

The illustrative chart groups predictions near 0.30, 0.50 and 0.70. Invented observed frequencies of 0.20, 0.50 and 0.60 reveal overstatement in the outer buckets. A later transformed set near 0.20, 0.50 and 0.60 would visually align with those frequencies. This is a teaching construction, not a fitted calibrator or independent validation. Fitting and assessing on those same displayed outcomes would be invalid evidence of improvement.

Governed Learning owns authorized fitting. FF applies the exact admitted artifact. Independent Evaluation assesses reliability, proper loss, support and applicability. Training, selection, calibration and untouched final testing need chronological separation or an explicitly leakage-safe staged protocol. Replacing a child model can invalidate a parent's calibrator even when the graph shape is unchanged.

The base-rate control remains a useful raw probabilistic benchmark. Simplicity does not make it calibrated, and raw benchmark losses are not forbidden merely because its advisory qualification is absent. Store raw and transformed values, fit history, calibration population, method/version and limits. Never replace a recorded raw number with its later recalibrated counterpart.

# 11. Runtime roles describe the assignment

Roles answer how an instrument is used in a specific profile and observation scope. They do not name an algorithm's permanent rank. A logistic artifact can be PRIMARY in one profile and BENCHMARK in another. A promising model can be CHALLENGER while it is evaluated. A SHADOW run collects prospective, non-influencing results. DISABLED means not executed in that binding, not erased from history.

:::figure 12 Illustrative assignments, not actual model approvals
| Artifact | Role in this example | Consequence |
|---|---|---|
| BaseRate v1 | BENCHMARK | Fixed retained comparator |
| Calibrated Logistic v1 | PRIMARY, only after scoped approval | Selected eligible advisory root |
| XGBoost v2 | CHALLENGER | Paired evaluation, no silent replacement |
| LLM v1 | SHADOW | Observe without influencing the primary |
| FMLFDE v1 | SHADOW | Same truth and comparisons, richer internal trace |
| Old tree artifact | DISABLED | No attempt; historical results remain |
:::

There is at most one PRIMARY root per exact subject, target, horizon and profile. Research can have none. Multiple roots do not imply multiple simultaneous primary decisions. An auxiliary result remains identified by its role rather than being blended into an unlabeled final percentage. A changed benchmark suite must also receive a new pinned reference; otherwise the meaning of progress can move with the candidate.

Role assignment is contextual governance. A model is not entitled to become PRIMARY because it is implemented, installed, registered, enabled or individually accurate on a small sample. Those are distinct conditions. A disabled assignment can later be enabled only under the appropriate trusted selection and authority. It does not gain the right to run simply because its descriptor remains discoverable.

Shadow deserves particular care. Running at the same time as production is not the same as influencing it. Its captured output, failures and cost enter evaluation, but not a hidden selection policy that chooses whichever root looks better today. If shadow results affect current trading behavior, that is no longer a genuinely non-influencing shadow experiment and requires a different, explicitly admitted design.

# 12. Lifecycle describes evidence and permitted use

Lifecycle records the history of an artifact's qualification, suspension and retirement. It is not the same axis as the role of a particular run. The proposed FF vocabulary separates EXPERIMENTAL, VALIDATED, SHADOW, APPROVED, SUSPENDED and RETIRED. These concepts require later explicit mapping to the preserved A7 registry events; this thesis does not replace existing enum names or broaden old approval scopes.

:::flow 13 Lifecycle is a sequence of gates, not automatic progress
EXPERIMENTAL: bounded research artifact, no advisory qualification
↓ Independent validation of exact target, population, calibration and resource profile
VALIDATED → authorized SHADOW: prospective, non-influencing evidence
↓ Independent recommendation + explicit scope-limited owner approval
APPROVED: eligible for separately selected future COLD use, subject to health
↘ SUSPENDED or RETIRED: retained event history; no hidden resumption or deletion
:::

| Question | Role axis | Lifecycle axis |
|---|---|---|
| Why was this run made? | Benchmark, primary, challenger or shadow | Not answered by lifecycle alone |
| What evidence and approval exist? | Role grants no qualification | Experimental through approved history |
| Why did it not execute? | Disabled assignment may explain absence | Suspension may independently deny use |
| Can an approved artifact be shadowed? | Yes, for an explicitly scoped non-influencing assignment | Its approval history remains unchanged |
| Does SHADOW imply production? | No influence by role | No advisory permission by lifecycle |

Approval is limited by target, population, profile and health. It is not a permanent certificate of superiority and never a grant to trade. A suspended artifact can retain all of its old forecast records while new use is denied. Resumption requires the appropriate evidence and authorized future binding, not deleting the suspension event or rerunning history under a new model.

Rejection and hold are useful outcomes at every gate. A miniature can pass its engineering tests while no candidate qualifies empirically. The correct response is to preserve the benchmark, records and explicit absence of a qualified primary. Renaming a candidate APPROVED because the user interface needs a number would collapse engineering readiness, scientific evidence and operating authority into one misleading status.

# 13. The miniature is a complete scientific loop

The first useful FF should be small enough to inspect end to end. Its comparative realization has one exact target, one shared ground-truth journal, a base-rate benchmark, a logistic candidate, one independent evaluator, held-out calibration and immutable replay. There are normally two primitive instruments and at most one approved primary root. A one-node FF-0 fixture proves mechanics; it is not a complete comparative acceptance result.

:::figure 14 Miniature FF: parallel forecasts, later reality
| At decision time | At outcome time | At review time |
|---|---|---|
| Qualified PIT snapshot + exact target/window | Independent qualified terminal close | Ledger links original runs to exact outcome revision |
| BaseRate benchmark → captured raw p | Shared journal labels the event once | Paired proper losses, coverage and uncertainty |
| Logistic → pinned calibrator → captured p | Same label for both instruments | Calibration, stability, budget and shadow gates |
| No outcome is supplied to inference | No forecast may repair the label | Explicit approval or hold; future COLD choice only |
:::

The arrows are temporal dependencies, not a requirement to acquire future ground truth before forecasting. The target definition exists first; the realized outcome does not. An initial illustrative exercise can use tiny invented observations to test whether equal closes become label zero, missing closes remain absent, a failed run stays in coverage and old forecasts survive a label revision. Those mechanics are valuable without pretending that synthetic observations establish an actual trading-session dataset.

What can the user eventually “see, feel and twist”? Under a separately authorized experiment, inspect the same observation under two pinned artifacts; inspect a raw versus calibrated output; intentionally supply an incompatible window and see admission fail; replay with optional model dependencies unavailable; change a candidate configuration under a new identity and compare the resulting scorecards. These are bounded experiments, not ordinary request parameters that rewrite active models.

Why is it not a toy? The exact same target identity, output/absence contract, common truth, population accounting, lifecycle and replay apply to a future complex instrument. What is reduced is the number of families, features, roots and experiments, not the standard of evidence. A useful stopping point is a trustworthy benchmarked research system with no qualifying primary. The architecture remains useful even when the first candidate disappoints.

Later facade/Shell exposure needs its own acceptance and may follow FF-2 without waiting for ensembles, LLMs or latent research. No new command is delivered by this book. The [FF roadmap](../../TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) keeps these engineering, empirical, approval and publication gates separate.

# 14. Benchmarks that cannot move unnoticed

A benchmark is itself a Forecaster configuration, not merely a scalar copied from an old report. Its features, fit window, target, output semantics, calibration state and versions must be pinned. Evaluation's Benchmark Registry is a curated reference view over the shared artifact/lifecycle records. It is not a second model store, an approval authority or a runtime activation service.

:::figure 15 The benchmark ladder is a menu of justified controls
| Label | Instrument | Why retain it? |
|---|---|---|
| B0 | Historical base rate | Required miniature control; measures advantage over event frequency |
| B1 | Precisely defined persistence / naive rule | Optional simple temporal hypothesis |
| B2 | Regularized logistic regression | First candidate; later a transparent comparator |
| B3 | One conventional ML challenger | Tests added nonlinear capacity under a finite budget |
| B4 | kNN, optional | Tests a train-only local similarity hypothesis |
| B5 | Simple calibrated ensemble | Tests combination after useful compatible children exist |
| B6 | Explicit-factor K-only head | Required control for a claim that latent Z adds value |
:::

B0–B6 are not seven compulsory implementation stages. The miniature does not need B3–B6. K-only may reuse a logistic implementation with a distinct explicit-factor schema; different scientific arms do not require duplicate software or duplicate outcomes. What matters is whether the configuration tests the intended hypothesis and whether its observations are fairly matched.

Benchmark selection should precede final outcome inspection. Replacing an inconvenient benchmark after a challenger loses destroys the comparison's meaning. A newer benchmark suite can be introduced under a new reference and protocol, retaining the old one. The ledger must explain which controls were required, which were optional, which actually ran and why a comparison was excluded or not evaluable.

The deterministic A2 baseline stays visible but is not automatically one of these probability instruments. Its score, class and direction have their accepted semantics. Dividing an A2 score by a convenient constant does not turn it into a calibrated forecast. Any future transformation into an outcome predictor would be a new independently evaluated artifact, not a reinterpretation of A2's historical records.

# 15. Ground truth belongs outside the model

The first target remains the exact A7 event `equity.next_session_close.return_gt_zero / 1.0`: the probability that the qualified next trading session's close is strictly greater than the known reference close. The reference is the completed source-session close, not a hypothetical fill obtainable after it is known. The event measures price return, not total return, expected return size, drawdown, option PoP or realized monetary utility.

= y = 1 when terminal_close > reference_close; otherwise y = 0, only if both endpoints qualify.

:::flow 16 Illustrative clocks; supplied sessions, not a calendar assertion
S0 completed close → observation, publication and availability proof
↓ Decision cutoff 16:00 +05:30; issue 16:01 +05:30 in this invented example
Captured qualified schedule proves S1 is the next eligible session, with no intervening session
↓ S1 target window ends at its exact supplied completed close
Independent endpoint/action checks → label_available_at → append-only journal entry
↓ Later evaluation uses its own as-known time and exact revision, never earlier inference
:::

| Responsibility | Owner / admitted evidence | Consequence of a gap |
|---|---|---|
| Exact event and labeler | Independent Evaluation | No model-specific target repair |
| Session adjacency | Qualified versioned schedule and exceptions | No weekday arithmetic or substitute S2 |
| Reference and terminal closes | Accepted market-data authority, units, finite positive decimals | Missing/invalid is no eligible label |
| Corporate-action basis | Captured action policy and evidence | Unresolved basis is ineligible or ambiguous |
| Revision and availability | Source versions plus journal lineage | Later knowledge cannot enter earlier folds |

In an illustrative example, reference 100.00 and terminal 101.00 produce y=1; 100.00 and 100.00 produce y=0; an absent terminal price produces no label. Display rounding must not decide the strict comparison. Corporate-action adjustments must be qualified consistently, not inferred to rescue an apparently extreme return. A current quote cannot replace the specified completed close.

A supplied schedule must prove adjacency over a covered interval. Two dates alone do not prove that no eligible session occurred between them. A material later change to the captured target window can censor it; the original forecast is preserved rather than shifted to a favorable later session. Late qualification may support later evaluation, but cannot retroactively justify an earlier forecast's admission or training eligibility.

The [A7 target and schedule contract](../../TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md#3-selected-first-target-and-exact-horizon) owns these inherited semantics. Deferrals for qualified session/action/history evidence remain open. The thesis uses invented sessions to teach the contract, not to certify a current exchange calendar or historical data provider.

# 16. The ledger links prediction to reality

The Outcome Journal stores immutable outcome entries and revisions. The Forecast Ledger is an Evaluation-owned immutable joined projection of forecast captures, journal references and population-disposition reports. It is not a second writable journal. This distinction prevents a spreadsheet-like implementation from overwriting a past prediction when a later price correction arrives.

:::figure 17 A pending record stays pending in its original snapshot
| Artifact | Contains | Later change |
|---|---|---|
| Run R1 | Original request, child/root outputs, absence, pins and cost | Never edited to add a future outcome |
| Journal J1 | Window open; label pending | Retained after maturation |
| Ledger L1 | R1 joined to J1; no Brier yet | Remains a pending historical view |
| Journal J2 | Qualified outcome, predecessor J1, availability | Appended, not overwritten |
| Ledger L2 | R1 joined to J2 and new disposition report | New projection and fingerprint |
| Comparison M2 | Exact runs, L2/J2, population and metric policy | Old M1, if any, still resolves old pins |
:::

The ledger carries observation ID, all request IDs, neutral subject, as-of/cutoff, target/window, child and composite outputs, artifact/graph/calibration versions, role and lifecycle evidence, context definitions, outcome references and metric-specific eligibility. One row may be convenient for display, but the source relationships must remain resolvable. A single cell labeled “latest probability” cannot represent this history faithfully.

Observation identity is independent of forecaster identity. Exact duplicate requests may map to one supervised observation under a pinned deduplication rule, while all request costs and failures remain visible. Different feature families can form distinct experimental arms for that observation. Conflicting reference captures are not merged merely because their symbols match. Multiple stochastic model calls about the same session are not extra independent market outcomes.

Outcome facets remain separate: window open/closed/censored/unobservable; label eligible/pending/ineligible/ambiguous; operation proposed/rejected/not-taken/taken/unknown; and observability by endpoint, full path or execution. A factual underlying close can be observable even if no trade was taken. It does not create a hypothetical option fill or P&L. REVISED is a predecessor relationship, not another mutually exclusive label status.

This model is also practical for audits. “What did we know then?” resolves the old ledger and exact source revision. “What do we know now about that observation?” resolves a newer projection. Both questions are legitimate; silently answering the first with the second would introduce look-ahead and make six-month replay unreliable.

# 17. Paired comparison is an identified experiment

A score difference is meaningful only when the arms answer the same question on a well-defined population. Comparing a challenger on easy days against a benchmark on all days can manufacture apparent improvement. Comparing the same symbols but different cutoff information or label revisions is similarly misleading. The Evaluation-owned PairedComparisonManifest makes those conditions inspectable rather than implicit in a notebook.

:::figure 18 Comparison identity binds the experiment, not just its name
| Identity layer | Pinned content |
|---|---|
| Arms | Exact benchmark/challenger runs, model/graph/calibrator versions |
| Question | Target/version, horizon, reference/terminal window, venue and basis |
| Population | Intended set, common eligible intersection, union, observation/request mapping |
| Time and truth | Cutoff policy, exact label revisions, evaluation-as-known time |
| Scientific protocol | Realized splits, fit/calibration/test cutoffs, metrics, weights and uncertainty method |
| Resources and lineage | Preregistration, trials/budgets, actual usage, ledger/disposition fingerprints |
:::

An opaque `comparison_id` is useful for lookup but insufficient for scientific identity. A semantic fingerprint binds its content. A new comparison can be created after forecasts have matured; it references their immutable IDs. The original forecast does not need to predict its future comparison ID or be mutated to contain it. This separation is one of the most important consequences of treating evaluation as a distinct owner.

Suppose an illustrative intended set has ten observations, both arms produced usable probabilities for eight, and one additional outcome remains unqualified. Paired proper loss uses only the exact eligible intersection after those checks. The report still exposes all ten intended observations and each absence/exclusion reason. It does not advertise the eight successful calls as 100% coverage. No eligible pair means NOT_EVALUABLE, not zero loss or PASS.

For each observation, metric and arm, retain INCLUDED, EXCLUDED or NOT_EVALUABLE with reasons. Coverage and loss have different denominators. An abstention can be included in coverage accounting while not evaluable for Brier. The manifest pins both denominators, the label revision and the split membership, allowing another reviewer to reconstruct which rows contributed to a conclusion.

Different admitted features remain permissible. Equal information eligibility is not a demand for identical tensors or prompts. A paired study can ask whether Market Intelligence adds value while preserving common truth and cutoff constraints. It must record that experimental difference rather than disguise it as an implementation detail.

# 18. Metrics: honest answers to different questions

No single metric establishes forecast quality. Brier and log loss evaluate probabilities against binary outcomes; reliability examines probability-frequency behavior; coverage and abstention describe where a system speaks or remains silent. Classification metrics require an explicit threshold and class dictionary. Economic utility needs an additional investable target and execution assumptions not supplied by the initial endpoint event.

:::figure 19 Metric map with explicit denominators
| Question | Measure | Required context |
|---|---|---|
| How wrong were the probabilities? | Mean Brier; mean log loss | Eligible probabilities and common qualified labels |
| Did confidence match frequency? | Reliability/calibration report | Fixed bins or method, support, uncertainty, population |
| Where did the system speak? | Coverage; abstention and failure rates | Full intended population and generation states |
| Did a declared class rule work? | Accuracy, precision, recall | Fixed threshold/ties, class support; undefined denominators retained |
| Did a tradable policy create utility? | Later economic evaluation | Separately accepted target, entry/cost/path assumptions |
:::

= Brier(p, y) = (p − y)².
= LogLoss(p, y) = −y ln(p) − (1 − y) ln(1 − p).

For invented p=0.60 and y=1, Brier is 0.16 and natural-log loss is about 0.5108. For p=0.60 and y=0, Brier is 0.36 and log loss about 0.9163. A probability does not become false simply because one uncertain event fails; a repeated scoring protocol assesses the sequence. Logarithm base and handling of exact endpoints must be declared. A report-side numeric clipping convention must not rewrite the issued probability or hide an impossible-event mistake.

A more selective model can reduce loss on its surviving cases while becoming less useful overall. That is why coverage accompanies proper loss. Unsupported, unavailable and failed calls are distinguished from intentional abstention; none becomes a synthetic label zero. Precision is undefined when there are no predicted positives, and recall is undefined without actual positives. A tidy zero in those cells would imply information that is absent.

Profit is not a substitute for this scorecard. A profitable trade can occur after a poor forecast, and a good underlying forecast can accompany a losing option because of price, volatility, timing or execution effects. The first FF target deliberately does not model those components. Its scientific claim must stay smaller than the eventual business objective.

# 19. Tiny advantages may be noise

Statistical comparison uses paired losses because the same difficult observation affects both arms. Define challenger-minus-benchmark loss explicitly: negative favors the challenger. A mean difference without independent support, uncertainty and selection history is only a descriptive summary. It should not become a promotion certificate because the displayed decimal is smaller.

:::figure 20 Illustrative paired loss, with its sign made visible
| Observation | Benchmark Brier | Challenger Brier | Challenger minus benchmark |
|---|---|---|---|
| O1 | 0.2304 | 0.1600 | −0.0704 |
| O2 | 0.2704 | 0.1600 | −0.1104 |
| O3 | 0.2304 | 0.0900 | −0.1404 |
| O4 | 0.2704 | 0.2500 | −0.0204 |
| Mean over four invented rows | 0.2504 | 0.1650 | −0.0854; arithmetic only |
:::

These four rows are reused in the miniature worked case. Their favorable average is not independent empirical evidence and supports no inference about actual equities. A real protocol must declare the population, weights, minimum support, interval method and practical-usefulness criterion before inspecting final outcomes. This architecture deliberately invents no universal sample floor or confidence threshold.

Financial observations can be dependent across nearby sessions and across equities in the same session. A time-aware or session-block bootstrap may be suitable when its assumptions fit; resampling isolated rows as independent can understate uncertainty. Block construction, unequal-panel handling and any forecast-comparison test need a preregistered rationale. A small, changing or heavily overlapping sample may justify INCONCLUSIVE rather than a precise-looking interval.

Search also matters. Trying many models, prompts, feature schemas, seeds and calibrators and reporting only the best result makes the nominal comparison incomplete. Record the bounded trial ledger and how selection was performed. Validation-selected best is different from best-on-test. Preserve an untouched test stage and, when relevant, prospective non-influencing shadow evidence.

The FM family sometimes expresses latent gain with the opposite sign, `Delta_Z = loss(K) − loss(K+Z)`, where positive favors Z. Reports must label the convention; a sign mistake could reverse a recommendation. The arithmetic and protocol definitions here follow the [FF metrics specification](../../TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#13-metrics-paired-statistics-and-regimes), not a claim that any actual statistical test was performed in this documentation pass.

# 20. Global success can hide local weakness

A forecaster can improve a global loss while doing worse in a particular regime, sector or event context. That is not automatically contradictory: the global average weights the population actually evaluated. A strong majority cohort can dominate a weak minority cohort. The report must make that population and support visible so an operator does not mistake a global summary for universal suitability.

:::chart 21 Regime-specific loss — invented cohorts, not measured advantage
regime.png
:::

In the chart's invented panel, logistic Brier is 0.22 in a trend cohort and 0.24 in a range cohort; the tree challenger has 0.19 and 0.28 respectively. With 800 trend and 200 range observations, global losses are 0.224 and 0.208. The challenger wins globally while losing in the smaller range cohort. These arithmetic aggregates are not observed performance, confidence intervals or a routing policy.

Predefine regime assignments, their availability cutoffs and the intended slices. A regime label obtained from future-smoothed data cannot justify a decision-time router. Model-relative regimes must be labeled as such; they are not independent market truth. Horizon-specific results concern different target windows and should not be pooled as if they were interchangeable observations.

Subgroup support is often weaker than global support. Report class/session counts, coverage and uncertainty rather than selecting visually striking cells. An apparent local win can be noise, especially after examining many alternative sectors, date ranges or event definitions. The same multiplicity and holdout discipline applies to choosing regimes as to choosing models.

A future RegimeRouter might be justified by repeatedly supported conditional differences, but that is another candidate instrument. It must use eligible context, a frozen rule or fitted gate, explicit unknown-regime behavior and independently qualified calibration. “Use the model that would have won each day” is an oracle diagnostic, not a deployable policy. The simplest adequate response to this chart could be to hold the challenger or restrict a proposed future scope, not build a router.

# 21. Never lose the children

Composition must never destroy component observability. A final percentage is the last line of a calculation, not the whole record. To understand it later, the reviewer needs every child, operator, calibration and conversion result; missingness and reasons; weights; shared ancestry; and exact input and artifact identities. A composite that cannot expose those dependencies is scientifically and operationally opaque.

:::figure 22 What a nested vote must retain
| Stage | Record required | Why it matters |
|---|---|---|
| Primitive A | Raw output, qualified stage if any, absence and lineage | Its independent behavior remains evaluable |
| Primitives B and C | Separate outputs and common-event admission | A mean cannot hide a failed or weak child |
| Ensemble E(B,C) | Weight/operator pins and raw/qualified parent stages | Attribution and parent calibration |
| Primitive D | Same complete trace | No privileged unrecorded opinion |
| Explicit class conversions | Threshold, tie and class dictionary versions | Probability-to-vote meaning is inspectable |
| VOTE(A,E,D) | Fixed electorate, quorum, final class or abstention | Vote is not mislabeled probability |
:::

Introspection should show both the declared graph and the executed graph. A disabled root, a later router's unselected expert and an attempted failure have different meanings. The request can be scientifically incomplete even if a parent returned a number; admission should prevent required-scope shrinkage from being hidden by a successful status.

Attribution also includes resource usage. A shared node has one captured execution under exact input pins but may influence several parents. Its cost is charged once per actual execution, with retries preserved, and its influence is disclosed at every use. Cost deduplication is not vote independence. The architecture must be able to explain both without treating a graph as a simple list of unrelated models.

Node-level evaluation becomes possible because the original outputs survive. A reviewer can ask whether the parent improved on its children or whether calibration helped one branch but hurt another. For a router, predictions from unexecuted experts do not exist. A separately authorized comparison can capture them on matched inputs; recorded replay must never make new calls or fabricate values to improve the scorecard's completeness.

# 22. Does the ensemble earn its place?

A composite should be compared with its major components, a relevant simple control and a declared best-component comparator. “Best” must distinguish selection using eligible validation from an ex-post best-on-test oracle. The latter can be a useful labeled diagnostic but cannot prove that the best instrument could have been chosen before outcomes were known.

:::chart 23 Leave-one-out contribution — invented scorecard
contribution.png
:::

The invented scorecard has full ensemble E loss 0.200, E without A loss 0.210, E without kNN loss 0.190, and E without C loss 0.205. Define contribution of member j as `loss(E−j) − loss(E)`. kNN's contribution under this experiment is −0.010: removing it improves the declared variant. That observation motivates investigation, not immediate removal from the active graph.

An individually decent model can harm a composite. Its errors may duplicate other members, its confidence can be inappropriate for the ensemble population, or a weight/calibration interaction can outweigh standalone usefulness. Marginal contributions need not sum to total gain. They depend on the chosen removal variant and do not by themselves establish causal importance.

E−j is a new graph and experiment. The protocol must say whether surviving weights follow a preapproved normalization rule or are refitted, and whether downstream calibrators or routers are refitted. All fitting remains outside final evaluation. A required child failing live does not authorize the same removal operation: silent reweighting would execute an untested composition.

Compare coverage, uncertainty and resource use as well as proper loss. A favorable difference on a tiny matched subset can coexist with worse overall availability. A parent that fails to improve the validation-selected best child may be rejected while the children remain useful challengers. Rejecting a composite is not a failure of the framework; it is the framework preventing unnecessary complexity from becoming a hidden dependency.

# 23. Disagreement is information, not a vote of confidence

Two ensembles can have similar-looking averages while their members tell different stories. A summary alone hides whether the forecast is broadly shared or the result of canceling opposing estimates. FF therefore retains dispersion, member identities, abstention counts and ancestry. It does not turn agreement into a probability of correctness or automatically make disagreement a reason to suppress a result.

:::chart 24 Forecast disagreement — illustrative member probabilities
disagreement.png
:::

The first invented group, XGB 0.72, FMLFDE 0.70 and LLM 0.69, has mean about 0.7033 and range 0.03. The second, 0.71, 0.42 and 0.76, has mean 0.63 and range 0.34. The second group's lower FM estimate is not discarded to make the ensemble more attractive. The result exposes that difference alongside target, calibration scope and evidence limitations.

Range is only one possible descriptive statistic. If a future profile uses variance or another measure, it must pin the definition, included members, weights and missingness treatment. Three strongly agreeing branches that share one underlying model or source are not three independent confirmations. Likewise, a missing member cannot quietly narrow the displayed disagreement range.

What should TI do with high disagreement? Initially, report it without inventing an automatic threshold. A later separately validated policy may use disagreement as a feature or abstention condition, but that policy needs its own target, data, version and evaluation. Current A4 dissent, missing evidence and A6 restrictions continue to exist independently of FF dispersion.

The practical user question is not “Did all models agree?” but “Which instruments disagree, about which exact event, using which eligible information and with what calibration limits?” That question can lead to an evidence-quality investigation, a cohort-specific study or a candidate correction. It does not give the most confident model authority to decide which facts are true.

# 24. An LLM is an optional instrument

An LLMForecaster can consume captured deterministic TI state, governed Market Intelligence and admitted sector, macro or derivatives context to answer an exact target question. Its output must be structured: a supported forecast kind or abstention, uncertainty/conflict, evidence references and exact prompt/model lineage. It is a normal optional primitive, not a supervisor that can change the graph or give itself more tools.

:::flow 25 The LLM stays behind the existing governed boundary
Captured, admitted TI evidence + exact target/window + bounded prompt template
↓ Existing model/budget gateway: authority, attempts, tokens, cost and allowed effects
Optional LLMForecaster: structured output or explicit absence
↓ Schema and evidence-reference checks; raw probability remains raw
Separate eligible calibration and independent comparison against common truth
↓ Qualified result or hold; no privileged vote, PRIMARY role or trading permission
:::

Persuasive language is not calibrated probability. A model might explain an invented 0.80 estimate fluently while comparable outcomes occur only 0.60 of the time. Evaluation must measure the actual relationship, rather than awarding a reliability claim for a well-written rationale. A later calibrator may improve the relationship on independent data, but it does not cure unsupported evidence or historical information leakage.

Future use routes through the existing governed gateway. No model SDK or Yahoo/MCP import belongs in domain contracts, specialists or Shell. Prompts cannot authorize topology changes, new source acquisition, hidden retries or production replacement. Instructions embedded in supplied news or documents are untrusted evidence content, not operating instructions. Unsupported references and malformed probabilities produce explicit failures or absence, not repaired prose presented as an original model result.

Pin rendered prompt and response, evidence versions, model/deployment revision where observable, decoding configuration, gateway policy, attempts, tokens and actual or unknown cost. A mutable remote model can make exact recomputation unavailable even though recorded offline replay succeeds. Historical pretraining vintage, rights and overlap require qualification; a qualified prospective shadow study may be more honest when historical knowability cannot be established. This handbook runs no model and makes no provider-readiness claim.

# 25. FM/LFDE has a stable home

FM/LFDE remains the advanced market-state forecaster family, not the definition of all forecasting. FM means Forecasting Module; LFDE means Latent Factor Discovery Engine. FF lets the family pursue a rich research hypothesis while TI retains simpler instruments and common evaluation. If the latent program fails to add value, the platform and deterministic TI remain useful.

:::figure 26 Inside one FMLFDEForecaster node
| Internal layer | Meaning | Boundary preserved at FF |
|---|---|---|
| Market Tensor M | Governed numerical channels, time/asset axes and masks | No screenshot or unqualified future input |
| Explicit Factors K | Versioned deterministic factor formulas | Frozen A2 facts are consumed, not retuned |
| LFDE Z | Learned latent representation in an artifact-specific basis | Not an identified economic truth vector |
| Market State X with quality Q | Typed fusion of admitted components | Quality/uncertainty is not execution authority |
| Direct head / optional dynamics | Exact-target forecast; dynamics is conditional later work | No actual future state at inference |
| Calibration / uncertainty | Internal stages and admitted scope | Outer FF calibration remains separately pinned |
| Shared FF result and Evaluation | Full family trace plus common target/outcomes | No family-owned ground truth or approval service |
:::

Primitive at FF's boundary does not mean opaque internally. Preserve tensor schema, masks, scaler, explicit factors, encoder basis, fusion/head artifacts, internal calibration and K/Z/K+Z ablations. Required Z absence must not silently choose an untested K-only route. A separately qualified K-only binding can remain available as a distinct instrument, with its own identity and permitted use.

The minimal family experiment starts with qualified explicit inputs and classical controls before advanced encoders, graphs or learned multimodal fusion. A direct head is a valid control; a dynamics model is not compulsory. Latent coordinates can rotate without creating new economic meaning. Representation stability and incremental outcome performance are separate questions, each requiring appropriate evidence.

“Standalone FM/LFDE” means selected alone through FF contracts, replay and common evaluation. It does not bypass governance. The family can begin as CHALLENGER or SHADOW and later qualify for a specific primary, benchmark, ensemble or routed role. Each use has its own conditions. The preserved [family architecture](../../TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md), [roadmap](../../TIAF_FM_LFDE_DETAILED_ROADMAP.md) and [advanced thesis](../../TI_FM_LFDE_Market_State_Forecasting_Thesis.pdf) remain the place for its deeper mathematics and research gates; this platform book does not merge or replace them.

# 26. Evolution is conditional, not a shopping list

An attractive diagram can accidentally imply that every later box must be built. FF's evolution is instead a set of hypotheses. Add a family only to test a bounded question; retain it only when independently qualified evidence justifies its role and cost. Model variety without useful diversity increases failure modes and audit obligations without guaranteeing better forecasts.

:::figure 27 A possible evolution, with exits at every step
| Possible step | Evidence needed | If it fails |
|---|---|---|
| Calibrated Logistic + BaseRate | Complete miniature mechanics and empirical gates | Keep control/absence; no forced primary |
| One tree challenger | Paired gain over retained simple instruments | Retain as rejected/disabled research record |
| Simple Logistic–tree ensemble | Parent beats relevant components under qualification | Use simpler qualified root |
| Optional LLM or FM/LFDE | Independently useful contribution and acceptable cost | Numeric/simple platform remains intact |
| Learned weights / member revision | Leakage-safe fitting, calibration and shadow | Current healthy binding unchanged |
| Regime routing / later MoE | Stable conditional value and eligible context | Preserve qualified static alternatives |
:::

LLM and FM/LFDE are independent optional branches, not sequential prerequisites. A numeric latent experiment does not need a working LLM. A conventional ensemble can be studied before FM/LFDE exists. Conversely, a standalone FM/LFDE challenger can be compared with a retained benchmark without first deploying a multi-family ensemble, provided the shared infrastructure is qualified.

Each additional learned stage creates downstream dependencies. Refitting a child can require new ensemble weights, calibration qualification and replay pins. Adding a modality adds rights, availability, missingness and provenance obligations. A model that wins proper loss but exceeds resource constraints has not necessarily earned operational use. A weak new component is not rescued by lowering a threshold after seeing named-symbol examples.

The safest growth path is the one a reviewer can explain as a sequence of separately identified experiments. Historical failures and alternative trials remain part of the record. No implementation stage earns the right to bypass the next gate, and no milestone promises that deep learning, language models or latent factors will eventually become the primary instrument.

# 27. Governed self-correction

Self-correction means using observed outcomes and diagnostics to propose bounded changes, not allowing a live system to rewrite production because yesterday's forecast was wrong. A wrong individual outcome is expected under uncertainty. Even a sustained loss change needs diagnosis: it might reflect data revisions, selection, calibration drift, population change, missing scope or genuine model weakness.

:::flow 28 Improvement proposals stop at an authority boundary
Captured forecast → independent qualified reality → paired Evaluation
↓ Diagnosis: evidence quality, support, calibration, contribution, cost and alternatives
Correction proposal with lineage, hypothesis, finite grant and test plan
↓ Authorized candidate fit / calibrator / weights / new graph; current binding unchanged
Independent walk-forward + calibration + coverage/cost review → prospective SHADOW
↓ Promotion recommendation → explicit owner approval OR reject/hold
Future trusted COLD selection; previous forecasts and approvals remain immutable
:::

Proposals can request recalibration, retraining, member removal, weight changes, ensemble redesign, routing changes or challenger promotion. They do not themselves grant compute, source rights or activation permission. Governed Learning owns authorized candidate generation; independent Evaluation tests it; the appropriate owner makes an explicit scope-limited approval decision. Basic gates already belong in the miniature, not only in a later correction-planner stage.

Consider an illustrative negative kNN contribution. The proposal creates a new `MEAN(XGB, FMLFDE)` candidate, including its new weight and calibration dependencies. It does not remove kNN from the currently bound `MEAN(XGB, KNN, FMLFDE)` while a request is running. If the candidate gains in backtests but fails prospective shadow, it remains unpromoted. If data quality explains the original result, a model change may be the wrong correction entirely.

Drift-triggered denial under an existing pinned health policy is distinct from learning a new policy. A healthy previously approved binding may continue where allowed; otherwise the system abstains or denies new use. Rollback selects an earlier qualified binding for future runs, never edits old predictions. Monitoring and correction cadence remain separately governed operational concerns; a diagram is not a running scheduler.

# 28. Replay has three different promises

Recorded replay asks what the system captured. Pinned recomputation asks whether the exact admitted computation can be reproduced. Counterfactual evaluation asks what a different configuration would do. These are different operations with different dependencies and identities. Confusing them allows today's model to replace yesterday's answer while still claiming “replay passed.”

:::figure 29 Replay pinning and the point of divergence
| Mode | Uses | Honest outcome |
|---|---|---|
| Recorded replay | Immutable request, node/root captures, serializer and semantic fingerprints | Same captured evidence/results, without live calls or current registry |
| Pinned recomputation | Exact graph, artifacts, transforms, verifier, numeric/seed/runtime closure | Exact or declared-tolerance verification; missing closure is UNVERIFIABLE |
| Counterfactual experiment | New model/weights/calibration/graph under new authority and identity | New result beside original, never substituted into it |
| Evaluation replay | Exact ledger, journal revisions, population/split/metric protocol and comparison | Same paired scorecard under its own as-known pins |
:::

| Pin group | Why it is needed |
|---|---|
| Request, subject, target/window/reference | Reconstructs the exact question |
| Evidence, source basis and availability | Prevents latest-data substitution |
| Graph, child/operator/weight/router versions | Explains the exact computational composition |
| Calibration and fit/selection lineage | Preserves transformation and qualification meaning |
| Role, approval, profile and health/budget policy | Preserves permitted purpose and admission conditions |
| Node outputs, reasons and actual usage | Replays failures and costs, not only successes |
| Comparison and outcome revisions, when evaluating | Prevents latest-label or denominator drift |

An exact recorded replay should not import an optional model SDK, query Yahoo/MCP, call an LLM or look up the latest active model. It reads the captured record and checks integrity. Exact recomputation needs the transitive closure of selected dependencies, including an FM latent basis/head pairing or a rendered LLM prompt where relevant. A mutable remote service may prevent reproduction of a recorded response; that is UNVERIFIABLE, not permission to call a newer deployment.

A numeric-tolerance check is not identical to serialized equality or equal semantic fingerprints. The verifier must state which promise it tests. A new journal revision creates a new evaluation projection without mutating the old forecast. A later composition upgrade similarly creates future identities while the original root, children, calibration and authority remain explainable six months later.

# 29. Pluggability without runtime replacement

R1–R5 provide the design discipline, not an automatic FF implementation. STRUCTURAL means a stable substitution boundary; COLD adds trusted pre-start selection; HOT would require safe live transitions and stronger lifecycle guarantees. FF targets STRUCTURAL plus COLD behavior. It does not add HOT model replacement, dynamic plugin installation or user-controlled import paths.

:::figure 30 Optional family, required selected dependency
| Boundary | Requiredness in scope | Change mechanism |
|---|---|---|
| Primitive / Composite / CompositionEngine | Selected ancestors and execution engine required for a new run | Reviewed typed contracts + trusted COLD graph |
| Calibrator | Required when claiming calibrated output | Exact artifact; separate fitting grant |
| Evaluator / GroundTruthProvider | Required for qualified evaluation/labels, not future labels at inference | Pinned independent protocols and source policies |
| BenchmarkRegistry / OutcomeJournal | Required for benchmarked comparison / outcome history | Shared versioned references, not extra activation authority |
| CorrectionPlanner | Optional until an authorized correction workflow needs it | Bounded proposal policy, never self-approval |
| Recorded replay | Captured record and integrity closure | No optional inference adapter or current registry dependency |
:::

R1 means required absence stays explicit. An optional family can be absent without invalidating unrelated TI functions, but once selected as a required branch it cannot silently disappear. R2 discovery describes shape and dependencies, not calibration or permission. R3-inspired envelopes pin participants, absence and exact verifier identity without pretending existing A3-scoped schemas already serve FF.

R4 isolates optional ML/LLM/provider dependencies from Core contracts, deterministic paths and recorded replay. R5 provides the ownership principle for trusted startup selection; the existing R5 implementation is not claimed to support FF selectors today. Adding an artifact to a registry or running a shadow root does not mutate the active composition.

Availability, role and lifecycle remain independent. A registered instrument can be unauthorized, data-unready or unhealthy for the request. An approved but unavailable primary produces explicit absence under its policy, not an opportunistic switch to the most recent challenger. The existing nine-operation facade catalog is unchanged. Any later FF publication is a separately reviewed consumer boundary.

# 30. Which controls may be changed, and by whom?

Tunability is not a reason to expose every hyperparameter to every user. An architecture invariant is not an experiment knob. A trusted startup profile is not a request field. An experiment configuration is not a production binding. Separating these controls makes both reproducibility and authority easier to understand.

| Class | Example | Owner / user visibility | Fingerprinted? |
|---|---|---|---|
| Architecture invariant | Common truth, PIT, no execution or self-promotion | Explained, never request-overridable | Governing schema/policy version |
| COLD profile | Required roots, scope, limits and approved roles | Trusted owner; safe read-only projection | Yes |
| Composition config | Edges, operator, electorate, threshold and weight refs | Reviewed immutable configuration | Yes |
| Model artifact | Coefficients, scaler, neighbors, encoder, prompt, calibrator | Authorized artifact owner; not casual Shell edit | Yes, including dependencies |
| Experiment config | Splits, trials, seeds, cohorts, metrics and acceptance protocol | Research owner before final outcomes | Yes |
| Request parameter | Neutral subject, admitted target/window, cutoff and captured input refs | Caller-scoped selection | Yes |
| Correction candidate | New fit, members, weights or routing proposal | Reviewable proposal, no active authority | Yes, separately from old binding |

The user should be able to inspect which profile and model version produced a result, why a forecast was absent and which evidence contributed. That does not imply a command to type arbitrary ensemble expressions, choose a provider model URL or edit weights in the middle of a run. Safe observability and unrestricted mutability are not the same usability feature.

Experiment owners also need bounds. Model search, calibration method selection, subgroup definitions and practical-usefulness thresholds must be fixed or governed by a declared protocol before final outcomes are inspected. Repeatedly changing them until a named-symbol example looks attractive turns experimentation into hidden fitting. A future candidate can change them under a new identity and fresh qualification, without revising the old record.

The same principle applies to cost. Budget ceilings are authority and operating constraints; actual cost is a measurement; unknown cost is a limitation. A request cannot raise its own limit because a preferred instrument is expensive. A future approved profile can differ, but the old run must retain the boundary under which it was attempted.

# 31. A staged delivery path with stop conditions

The following local stage labels explain the [bounded FF roadmap](../../TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md). They are not accepted A7 milestone replacements or permission to begin implementation. Every stage has an entry condition, tangible artifacts, tests and a meaningful stop. The complete benchmarked miniature is FF-0 through FF-2; later sophistication is optional.

| Stage | What becomes inspectable or usable | What it does not establish |
|---|---|---|
| FF-0 | Singleton contracts, label mechanics and recorded replay | Comparative or empirical model value |
| FF-1 | BaseRate versus Logistic, ledger and paired scorecard | Qualified calibrated primary |
| FF-2 | Calibrated candidate, lifecycle/shadow and complete miniature | Automatic publication or trade authority |
| FF-3 | One added family and qualified simple composition | A requirement to keep an unhelpful ensemble |
| FF-4 | Optional structured LLM comparison instrument | Privileged confidence or prerequisite for FM |
| FF-5 | Optional advanced FM/LFDE family experiment | Proof that latent state adds value |
| FF-6 | Governed correction proposals and candidate workflows | Autonomous activation |
| FF-7 | Separately qualified routing/stacking/MoE where earned | HOT installation or hindsight selection |

:::flow 31 Stage dependencies, not a mandatory model ladder
Thesis reconciliation → explicit A7 integration review → independent architecture acceptance
↓ Separately authorized implementation: FF-0 → FF-1 → FF-2 miniature
From FF-2: optional FF-3 multi-family composition / FF-4 LLM / FF-5 FM-LFDE
↓ FF-4 is NOT prerequisite to FF-5; FF-3 is needed when composing multiple families
FF-6 expands governed correction; FF-7 needs qualified experts and composition mechanics
↓ Every branch may stop with simpler qualified controls and explicit absence preserved
:::

## FF-0 — Contracts, common truth and one instrument

**Purpose:** establish reproducible mechanics. **Entry:** reviewed architecture/integration and a bounded implementation request, not a training grant. **Deliverables:** frozen typed request/result/node/DAG/run contracts, exact target/schedule/label references, one BaseRate fixture artifact and captured/pinned replay boundaries. **Tests:** list/tuple/JSON, aware timezone, flat versus missing labels, invalid schedule/action basis, cycles, duplicate IDs, required absence and unavailable optional imports. **Success:** deterministic mechanics on a named synthetic corpus. **Stop/fallback:** reject malformed scope; unqualified real data supports no empirical claim. **Usable result:** a singleton scientific-control inspection path. **Next gate:** accepted mechanics, observation identity and a finite paired-study protocol.

## FF-1 — Benchmark references and paired evaluation

**Purpose:** make comparative claims reproducible. **Entry:** FF-0 plus qualified data and a fit/comparison grant, or a clearly SYNTHETIC_ONLY exercise. **Deliverables:** B0 and raw logistic candidate, Benchmark Registry view, ledger snapshots, comparison manifests and population reports. **Tests:** exact paired identity, duplicate requests, revision conflicts, common/union denominators, zero eligible pairs, undefined class metrics and unchanged old ledgers. **Success:** complete scorecards including negative/inconclusive outcomes. **Stop/fallback:** missing identity or support blocks the claim, not the control tool. **Usable result:** benchmarked research inspection, not calibrated primary publication. **Next gate:** independent calibration/test data and frozen qualification protocols.

## FF-2 — Calibration, lifecycle and complete miniature

**Purpose:** separate raw generation from qualified potential use. **Entry:** FF-1, held-out calibration data and explicit prospective shadow authority. **Deliverables:** calibrated logistic root, raw/B0 retention, role/lifecycle histories, shadow and independent promotion recommendation, recorded/recompute/counterfactual distinctions. **Tests:** wrong calibration pins, leakage, unsupported classes, suspension, denied primary, no HOT switch and replay after upgrade. **Success:** accepted mechanics plus honest empirical qualification; primary only if all gates pass. **Stop/fallback:** hold unsupported, miscalibrated, over-budget or failed-shadow candidates. **Usable result:** complete comparative miniature, possibly no approved primary. **Next gate:** justified extension or separately accepted A7.4 facade/Shell projection.

## FF-3 — One new family and simple composition

**Purpose:** test incremental nonlinear or combination value. **Entry:** FF-2 and a finite grant for one conventional ML challenger; compatible qualified members before averaging. **Deliverables:** auxiliary roots, deterministic shared-node execution, traces/cost, optional simple calibrated mean, operator rejection fixtures and component/leave-one-out reports. **Tests:** type/window/calibration mismatches, nested cycles, singleton means, duplicate influence, vote quorum, missing child, no renormalization and unique charging. **Success:** independently useful new family/composite within coverage and cost constraints. **Stop/fallback:** reject an unhelpful ensemble; retain simpler qualified instruments. **Usable result:** inspectable bounded multi-family experiments. **Next gate:** optional evidence-backed extensions, not mandatory completion of every benchmark rung.

## FF-4 — Optional governed LLM forecaster

**Purpose:** test structured narrative/context forecasting value. **Entry:** FF-2, qualified rights/vintage or prospective mode, gateway authority and finite token/attempt/cost limits. **Deliverables:** one optional adapter with prompt/response/version capture, absence, raw probability, separate calibration and common paired evaluation. **Tests:** malformed/injected output, invented references, unknown revision/cost, missing credentials, exhausted budget and replay without remote reproduction. **Success:** independently qualified contribution, not eloquence. **Stop/fallback:** leave unhelpful or unqualified LLM disabled/unapproved. **Usable result:** governed optional comparison instrument. **Next gate:** none compulsory; numeric FF and FM research do not depend on this branch.

## FF-5 — Advanced FMLFDEForecaster

**Purpose:** test learned market-state contribution against explicit/classical controls. **Entry:** FF-2, bounded family-research grant, qualified tensor/K inputs and K-only comparator; FF-3 only for ensemble use. **Deliverables:** retained FM-0–FM-6 and LFDE L0–L5 gates behind one neutral boundary, with masks, basis/head lineage and K/Z/K+Z reports. **Tests:** future leakage, empty masks, basis mismatch, anchors, ablations, uncertainty NOT_ESTIMATED and internal/outer calibration identity. **Success:** stable incremental proper-loss/calibration evidence within support and cost. **Stop/fallback:** keep explicit controls if Z, dynamics or added modalities fail. **Usable result:** qualified advanced challenger where earned. **Next gate:** each additional family hypothesis separately justified; no mandatory LLM or dynamics.

## FF-6 — Governed correction expansion

**Purpose:** make repeated diagnosis/proposal work bounded and auditable. **Entry:** trusted journal/comparison infrastructure and explicit job/resource authority; basic approval already exists in FF-2. **Deliverables:** proposals, authorized candidate changes, independent validation/shadow and future COLD approval records. **Tests:** no grant/no job, new identities, consumed trials, holdout contamination, backtest gain with shadow failure, rejection and historical replay. **Success:** supported improvements and documented rejections, without autonomous activation. **Stop/fallback:** hold inconclusive causes or failed candidates; retain healthy binding or deny under existing policy. **Usable result:** auditable change proposals and candidate workflows. **Next gate:** recurring supported conditional evidence before routing complexity.

## FF-7 — Routing, stacking and future mixture of experts

**Purpose:** test context-dependent combination beyond static controls. **Entry:** qualified experts, eligible regimes, sufficient held-out support, relevant FF-3 mechanics and bounded gate/meta-model budget. **Deliverables:** typed frozen router/stacker, leakage-safe fitting, combined qualification and selected/unselected traces. **Tests:** future-smoothed regimes, in-sample meta-fit, stale/unknown context, expert absence, support collapse, cycles and replay after upgrades. **Success:** robust incremental value over static/simple alternatives. **Stop/fallback:** reject unhelpful routing; no silent live topology repair. **Usable result:** a separately qualified context-sensitive instrument, not HOT installation. **Next gate:** further research or operating scope only by a new accepted proposal.

# 32. A7, consumers and deployment

FF belongs within A7 Forecasting. Independent Evaluation owns common ground truth, outcome history, paired comparisons and qualification. Governed Learning owns authorized fits, candidate artifacts and correction workflow. The user-facing “platform” spans cooperation among these owners; it must not turn them into one inference object with permission to train and approve itself.

:::figure 32 Future A7 ownership, with existing consumers preserved
| Owner | Future responsibility | Excluded responsibility |
|---|---|---|
| A7 Forecasting / FF | Admission, typed graph, primitive/composite inference and trace | Labels, request-time fit or self-promotion |
| A7 independent Evaluation | Ground truth, journal, ledger, paired metrics, calibration qualification, drift | Selecting a trade or editing past forecasts |
| A7 Governed Learning | Authorized training/calibration fits, candidates, correction and registry history | Granting its own access or automatic activation |
| Independent reviewer / startup owner | Scope-limited approval / future COLD selection | Rewriting historical records |
| Caller-bound facade / Shell | Later admitted projection / allowlisted rendering | Direct model SDK, arbitrary graph language or train command |
| TI Monitoring / A5 / TM | Future reevaluation / position advice / operational action | FF result bypasses none of these owners |
:::

The preserved A7 proposal still needs explicit integration review. Its A7.1 target/journal semantics remain; future FF graph and comparison contracts need mapping. A7.2 evaluation generalizes to named arms while preserving held-out calibration and population reports. A7.3 needs lossless role/lifecycle and replay closure mapping. A7.4 needs scoped facade exposure. A7.5 needs an acceptance corpus for the actual miniature. This book changes none of those normative files or public operations.

Deployment should begin with the existing [trusted local capability model](../../TIAF_DEPLOYMENT_ARCHITECTURE.md). Logical diagram boxes are not an instruction to deploy microservices. Optional heavy/model adapters may need isolation when justified, but the interface and captured result remain stable. Reuse evidence only under compatible input, rights and scope; separate analytical state and approvals even when the underlying capture is shared.

The [Monitoring architecture](../../TIAF_MONITORING_ARCHITECTURE.md) is still future runtime. Its admitted mandates would invoke capabilities as a governed consumer, not make forecasting or A5 into a scheduler. A5 advice cannot close a TM position; a forecast cannot make monitoring operational truth. The [Shell boundary](../../TIAF_TI_SHELL_ARCHITECTURE.md) remains presentation through a caller-bound facade. No public train, promote, configure-model or forecast command is created by an illustration.

# 33. Failure is part of the product

A reliable forecasting interface must be able to decline, fail or remain inconclusive without inventing an estimate. The framework preserves useful lower-layer TI behavior when optional forecasting is absent. It does not promise a forecast when required evidence, calibration or authority is missing. Those two statements are compatible: optional to TI does not mean optional inside a selected scientific claim.

:::figure 33 Failure and degradation matrix
| Condition | Required response | What remains valid |
|---|---|---|
| Unqualified schedule or endpoint basis | No real forecast/label qualification; reasons retained | Synthetic mechanics and captured absence inspection |
| Missing required child | Composite absent under pinned policy | Child records and unrelated roots; no untested reweighting |
| Optional family not selected | Explicit absence / not selected, not negative opinion | Required selected graph and deterministic TI |
| Raw or unsupported calibration | No calibrated advisory claim | Raw research output and eligible diagnostic losses |
| No eligible paired observations | NOT_EVALUABLE, denominators/reasons shown | Failed study as an auditable artifact |
| Model revision/verifier unavailable | Recorded replay may pass; recompute UNVERIFIABLE | Original capture, never current-model substitution |
| Shadow candidate fails | Hold/reject, no active replacement | Prior healthy approved binding or explicit denial |
| Resource limit reached | Stop under captured budget; retain attempts and unknowns | Complete failure/cost lineage |
:::

Bad source data is not cured by a better model. A forecast-target mismatch is not cured by averaging more children. A statistically inconclusive comparison is not cured by formatting the winning decimal in green. Each failure should identify which boundary failed and what evidence would be needed to make a new, independently admitted attempt.

Recovery also needs an identity. If a source publishes a corrected close, append a journal revision. If a required dependency becomes available, a new run can be admitted under its then-current authority and cutoff; it is not a repair of the old issued forecast. If a candidate is approved later, new COLD bindings affect future runs. Preserving these distinctions makes failure analysis possible without losing the original evidence of what happened.

The [deferral register](../../TIAF_DEFERRAL_REGISTER.md) remains unchanged. Qualified calendar/action/history inputs, durable scheduling/storage, production model readiness, HOT replacement and publication are not closed by this handbook. A6 stays frozen, A7 acceptance stays paused and no runtime/training/live call occurs in this pass. These are scope boundaries, not defects concealed behind a readiness label.

# 34. Fourteen worked scenarios

Every case below is **ILLUSTRATIVE / INVENTED / NOT MEASURED TI PERFORMANCE**. None represents a model fit, live call, qualified market dataset or actual approval. Unless stated otherwise, all arms use the exact first target: qualified NSE cash-equity next-session close strictly above its known reference, with common observation windows, cutoff policy and label revisions. Short vectors are teaching rows, not sufficient independent support for promotion. “Qualified” in a scenario is a hypothetical premise, never a claim about installed models.

| Case | Question demonstrated | Governance lesson |
|---|---|---|
| 1 | Does the miniature compare two instruments fairly? | Arithmetic success is not empirical approval |
| 2 | A tree challenger beats logistic | Keep the old primary pending independent gates |
| 3 | Global win, local regime loss | No post-hoc router or hidden scope change |
| 4 | A mean beats all children | Parent still needs its own qualification |
| 5 | A mean loses to the best child | Reject unjustified complexity |
| 6 | One-child ensemble | Identity is valid, not diversification |
| 7–8 | Persuasive LLM, then calibration | Separate explanation, fitting and reliability |
| 9–10 | FM wins / FM adds no value | Same evaluation, no architectural privilege |
| 11 | High disagreement | Preserve opposing estimates and authority |
| 12–13 | Negative kNN contribution, then proposal | Removal experiment is not live fallback |
| 14 | Replay after graph upgrade | Old result and outcome pins remain immutable |

## Case 1 — BaseRate and Logistic make the miniature tangible

**Configuration:** illustrative graph G1 has BaseRate B0 as BENCHMARK and raw Logistic L1 followed by qualified calibrator C1 as CHALLENGER. It has no approved primary. A separate fitting exercise would have produced each artifact; none is fitted on these four teaching rows. The intent is to inspect the same question through two instruments.

**Target/horizon:** the exact next-session endpoint target on four invented qualified session pairs for a neutral equity S. The reference closes are all 100; terminal closes are 101, 99, 102 and 100. Request identities differ by window, while observation identity is shared across the two arms.

**Component forecasts:** B0=[0.52, 0.52, 0.52, 0.52]. L1 raw=[0.65, 0.35, 0.75, 0.55]; C1(L1)=[0.60, 0.40, 0.70, 0.50]. The raw stage stays in the trace, even though the qualified root is the paired candidate.

**Ground truth:** y=[1,0,1,0]; the flat fourth close is zero, not missing. Both arms reference the same four journal entries and exact labeler version.

**Metric/result:** B0 mean Brier=0.2504; calibrated logistic=0.1650; paired difference=−0.0854. Both have four generated probabilities and four qualified labels in this miniature fixture. These counts show arithmetic completeness only.

**Interpretation:** the chain from request to capture to common truth to comparison is visible. It is now possible to inspect a calibration transform or inject an invalid window without changing the benchmark's meaning. Four constructed rows do not establish useful prediction.

**Governance outcome:** engineering illustration only; no primary approval. A real qualification would still need eligible fit/calibration/test data, independent support, uncertainty, resource reporting and prospective shadow. The fixture cannot close data-source or session-calendar deferrals.

## Case 2 — XGBoost beats Logistic without replacing it

**Configuration:** retain the hypothetically approved Logistic+C1 primary and BaseRate control. Add XGBoost X2 with its separately qualified calibration as CHALLENGER under a finite comparison grant. The current root selection is unchanged while the comparison runs.

**Target/horizon:** the same four invented qualified session-pair observations and exact event used in Case 1. No arm receives a later cutoff or a revised label unavailable to the other.

**Component forecasts:** Logistic=[0.60,0.40,0.70,0.50]; calibrated X2=[0.70,0.30,0.80,0.40]; retained BaseRate=[0.52,0.52,0.52,0.52]. X2's raw stage and transformation identity are assumed separately captured, not reconstructed from its calibrated root.

**Ground truth:** y=[1,0,1,0], from the same Evaluation-owned journal revisions. Neither model changes the target's flat-return convention to improve its score.

**Metric/result:** X2 mean Brier=0.095 versus Logistic 0.165; paired difference=−0.070. The sign favors X2 on these invented rows. It says nothing about uncertainty or real future performance.

**Interpretation:** a better score creates a candidate claim. It does not prove that X2 is best in every regime, that its costs are acceptable or that the calibration population supports the intended use. The old primary remains an important comparator even if a future upgrade is eventually approved.

**Governance outcome:** recommend further independent qualification, not automatic replacement. Only a separately adequate study and shadow record could support explicit approval and a future COLD binding. A completed challenger request never changes the active graph by itself.

## Case 3 — Global winner, range-regime loser

**Configuration:** compare qualified Logistic and tree challenger roots under one frozen protocol. The trend/range labels are assumed to be predefined and available at each decision cutoff. No future-smoothed regime state is admitted.

**Target/horizon:** the same next-session endpoint target on an invented panel with 800 trend and 200 range observations. Both arms use the same observations and labels; the counts are synthetic scorecard assumptions, not a historical universe claim.

**Component forecasts:** one illustrative trend row has Logistic 0.60 and tree 0.70; one range row has Logistic 0.45 and tree 0.70. These two rows are examples, not the data from which the panel averages below were calculated.

**Ground truth:** assume independently qualified binary labels for the whole panel; the example trend row is y=1 and range row y=0. Their role is to make the kind of local reversal concrete.

**Metric/result:** stipulated illustrative mean Brier values are Logistic 0.22/0.24 and tree 0.19/0.28 for trend/range. Weighted global values are 0.224 and 0.208. The tree's global advantage is −0.016; its range disadvantage is +0.040.

**Interpretation:** the majority cohort dominates the aggregate. The correct report shows global and conditional performance with support and uncertainty, not only the attractive global number. The small example rows do not validate those stipulated cohort summaries.

**Governance outcome:** hold the scope decision for review. A restricted future profile or router is a new hypothesis requiring independent data and qualification. Selecting the winner after observing each regime's final outcomes would be hindsight, not an operating rule.

## Case 4 — A simple ensemble beats both children

**Configuration:** two hypothetical independently qualified probability instruments A and B answer the same event. E is a fixed equal-weight mean whose root qualification is evaluated separately. No weight was selected from these displayed outcomes.

**Target/horizon:** four invented qualified next-session endpoint observations with shared reference/window and decision cutoff semantics.

**Component forecasts:** A=[0.90,0.70,0.80,0.40]; B=[0.60,0.20,0.50,0.10]; E=[0.75,0.45,0.65,0.25]. Every primitive and mean output is retained; the mean does not replace the child records.

**Ground truth:** y=[1,0,1,0]. Both members are wrong to different degrees on different rows. The event labels are not chosen by a vote of the models.

**Metric/result:** A mean Brier=0.175; B=0.115; E=0.1125. E beats both children on this constructed vector, but only slightly beats B. This example demonstrates the arithmetic possibility, not statistically significant diversification or calibration.

**Interpretation:** combining errors can help even without a learned meta-model. The gain over the best child is the relevant comparison, not merely a gain over a weaker control. Shared input or model ancestry would also need disclosure; a mean does not prove independent evidence.

**Governance outcome:** keep E as a candidate for independent parent calibration, coverage, cost and shadow evaluation. If the small apparent gain fails a preregistered usefulness or uncertainty criterion on real eligible observations, select the simpler qualified child. The framework supports both outcomes without retuning the displayed weights.

## Case 5 — The ensemble is worse than its best child

**Configuration:** candidate E is the fixed equal-weight mean of two qualified instruments. A was selected as the best component using eligible validation before the final comparison, not by choosing its test result afterward.

**Target/horizon:** four constructed qualified next-session endpoint observations, with identical labels, split and target version for all arms.

**Component forecasts:** A=[0.80,0.20,0.80,0.20]; B=[0.60,0.40,0.60,0.40]; E=[0.70,0.30,0.70,0.30]. Child scope and all required branches are complete.

**Ground truth:** y=[1,0,1,0], independently supplied in the illustrative journal. No candidate is excluded because it makes the ensemble look worse.

**Metric/result:** A Brier=0.040; B=0.160; E=0.090. E beats B but loses clearly to A. Comparing only E against B would create a misleading success story.

**Interpretation:** more instruments do not guarantee more useful information. This example does not establish that A will remain best forever; it simply shows that the proposed combination has not earned superiority over the declared comparator. An ex-post best-on-test oracle, if shown, must be labeled separately.

**Governance outcome:** reject E under this illustrative experiment's purpose of demonstrating incremental benefit over A. Retain A's existing healthy binding if applicable and preserve B/E as research records. Do not add weights after inspecting these outcomes and present the revised composition as the original successful experiment. A new weighted proposal would require its own fit/selection and untouched evaluation.

## Case 6 — A one-child ensemble is a real identity operation

**Configuration:** graph G6 declares E=ENSEMBLE(X2), a nonempty singleton mean. X2 is assumed to satisfy the exact calibrated-child admission scope. The wrapper is not used to disguise an unqualified raw estimate.

**Target/horizon:** one invented RELIANCE next-session endpoint request using neutral identity RELIANCE, not a provider ticker suffix, and a qualified captured schedule/window.

**Component forecasts:** X2=0.64; E=0.64. There is one executed primitive, one trivial mean operator and one ancestry chain. No duplicate model vote or fictional independent member is introduced.

**Ground truth:** illustrative reference 100 and terminal 101 give y=1 under the shared strict endpoint label. The reference is not a fill price available at issue.

**Metric/result:** X2 and E each have Brier 0.1296. Numeric identity is expected. Their graph fingerprints differ because the wrapper is declared, while the scientific event and observation remain the same.

**Interpretation:** singleton composition can simplify uniform configuration and test the composite interface. It does not improve accuracy, calibration or diversity. Evaluation must avoid counting its output as an independent market observation or charging the child twice merely because both references appear in the trace.

**Governance outcome:** accept the identity behavior as a hypothetical engineering case, with no new empirical qualification from wrapping. A future required child failure makes the singleton absent, not 0.50. If X2's qualification is absent, a one-child wrapper cannot supply it. The active profile remains whatever the trusted owner previously bound.

## Case 7 — A persuasive LLM is poorly calibrated

**Configuration:** optional LLM L7 runs in a non-influencing research role through the governed gateway. It produces fluent reasons and raw probability 0.80 for each of five constructed observations. A logistic comparator emits 0.60; no persuasive-language score is used as a vote weight.

**Target/horizon:** five invented observations of the same qualified next-session endpoint event. Rights, cutoff and model-vintage eligibility would still require independent proof in a real study.

**Component forecasts:** L7 raw=[0.80,0.80,0.80,0.80,0.80]; comparator=[0.60,0.60,0.60,0.60,0.60]. Evidence references and any conflicts remain attached to the LLM's output, regardless of rhetorical confidence.

**Ground truth:** y=[1,1,1,0,0], a synthetic 0.60 event frequency in this tiny group. The examples do not establish a population calibration estimate.

**Metric/result:** L7 mean Brier=0.280; comparator=0.240. Mean natural-log loss is approximately 0.7777 versus 0.6730. The group illustrates overstatement: 0.80 claims meet a constructed frequency of 0.60.

**Interpretation:** plausible reasons did not create a calibrated probability. Five rows cannot validate a calibrator, yet they can teach why structured output and convincing explanation are insufficient scientific evidence. No new sentiment or source fact is inferred from the wording.

**Governance outcome:** no qualified-primary or ensemble admission from this result. Preserve raw diagnostics and actual/unknown usage. A separate eligible calibration experiment may be proposed; it does not repair historical PIT gaps or authorize more model calls on its own.

## Case 8 — Calibration improves an LLM pipeline, conditionally

**Configuration:** candidate C8(L7) applies a separately fitted, pinned calibrator. For this example, assume its mapping of raw 0.80 to 0.60 was learned on earlier eligible calibration data, not on the five displayed evaluation labels. The unchanged LLM raw output remains in the trace.

**Target/horizon:** a new invented evaluation panel for the exact next-session event, with nonoverlapping fit/calibration/test membership and independent qualified outcomes as hypothetical premises.

**Component forecasts:** raw L7=[0.80,0.80,0.80,0.80,0.80]; C8(L7)=[0.60,0.60,0.60,0.60,0.60]. C8 is a distinct artifact and the pipeline has a new identity. This is not a retrofit of Case 7's captured forecasts.

**Ground truth:** constructed y=[1,1,1,0,0] on the new panel. Reusing the same illustrative pattern does not mean these are the fitting rows or independent real evidence.

**Metric/result:** mean Brier changes from 0.280 to 0.240; mean log loss from about 0.7777 to 0.6730. Predicted group frequency now matches the constructed 0.60 outcome frequency. No reliable population conclusion follows from the tiny example.

**Interpretation:** calibration can change the probability-frequency relationship without changing the prose or underlying model. Improvement may still be too small, poorly supported, unstable or expensive relative to simple controls. A new LLM deployment could invalidate C8's qualification.

**Governance outcome:** propose independent broader reliability/support and prospective shadow review. Do not mark an LLM calibrated merely because a wrapper exists. A qualifying future pipeline needs scoped approval and COLD selection; historical raw forecasts and failed calls remain unchanged.

## Case 9 — FM/LFDE wins in shadow

**Configuration:** retain a conventional ensemble E as hypothetical primary. Add FMLFDE F9 in SHADOW and a K-only explicit-state comparator, all using the same common evaluation. The FM family exposes its tensor/K/Z/head/calibration trace and does not replace the shared labeler.

**Target/horizon:** four invented qualified next-session endpoint observations. The direct family head is sufficient for this scenario; no dynamics model or LLM is assumed necessary.

**Component forecasts:** E=[0.70,0.30,0.70,0.30]; K-only=[0.75,0.25,0.75,0.25]; F9(K+Z)=[0.80,0.20,0.80,0.20]. These are stipulated qualified-root outputs, not trained latent results.

**Ground truth:** y=[1,0,1,0], common across all three arms and pinned to the same outcome revisions. Z does not have a directly observed economic-factor truth label in this example.

**Metric/result:** E Brier=0.090; K-only=0.0625; F9=0.040. Challenger-minus-E is −0.050; the family's opposite-sign latent gain is Delta_Z=0.0625−0.040=0.0225.

**Interpretation:** the arithmetic supports the possibility that an advanced family improves both a conventional comparator and its explicit-state control. It establishes neither representation identifiability nor real predictive value. Full-route ablation, stability, calibration, support and cost still matter.

**Governance outcome:** keep F9 non-influencing until independent qualification and explicit approval. A promising shadow result is not a deployment event. If eventual use is as an ensemble member or routed expert rather than standalone primary, the corresponding parent/gate requires its own admission and evaluation.

## Case 10 — FM/LFDE fails to add value

**Configuration:** the same common comparison structure is retained, but another bounded family candidate F10 is tested. Conventional E and K-only remain visible. The latent research hypothesis is allowed to fail without replacing the target or dropping the explicit comparator.

**Target/horizon:** the exact same invented next-session endpoint observations used for the arithmetic contrast; in a real study, final evaluation and trial reuse would be governed by a preregistered selection protocol.

**Component forecasts:** E=[0.70,0.30,0.70,0.30]; K-only=[0.75,0.25,0.75,0.25]; F10=[0.60,0.40,0.60,0.40]. All required family inputs are assumed present, so this is a performance example rather than an absence fallback.

**Ground truth:** y=[1,0,1,0], independently supplied and unchanged. The family does not relabel difficult observations as a new regime to improve its headline score.

**Metric/result:** F10 Brier=0.160, worse than E's 0.090 and K-only's 0.0625. Delta_Z is −0.0975. A separate representation plot could still look orderly, but it would not reverse these outcome losses.

**Interpretation:** the proposed latent route has not earned this role. The result says nothing about all possible FM/LFDE models, yet it is enough to reject an unsupported improvement claim for this candidate. Continued research needs a new bounded hypothesis, not an obligation to keep tuning until it wins.

**Governance outcome:** no promotion. Retain simple qualified forecasters, the family record and its failure diagnosis. TI remains useful without latent contribution. The platform succeeds by permitting that honest conclusion while preserving the advanced family's research design for separately justified work.

## Case 11 — High disagreement is shown to TI

**Configuration:** an illustrative KAYNES graph has qualified same-event XGB, FM/LFDE and LLM children with an equal-weight mean E. The configured graph is assumed admitted; disagreement does not authorize topology changes.

**Target/horizon:** qualified next-session cash-equity close above known reference. This is not the intraday CE profitability question that an A6/TM workflow would need to answer.

**Component forecasts:** XGB=0.71, FM/LFDE=0.42, LLM=0.76; E=0.63. Range=0.34. The FM output, its evidence and calibration limits remain visible even though it disagrees with the other two.

**Ground truth:** invented reference 100, terminal 99, so y=0. The fact that FM's lower estimate fares better on this row does not make it the best model or the source of truth.

**Metric/result:** E Brier=0.3969; child losses are 0.5041, 0.1764 and 0.5776. These single-row losses are diagnostics, not a selection protocol or an independent calibration study.

**Interpretation:** the headline mean should travel with its disagreement record, target and limitations. A user seeing only 0.63 might miss that one qualified instrument sees a different balance of evidence. The architecture specifies exposure, not a final dispersion-triggered abstention threshold.

**Governance outcome:** preserve E and all children under the existing policy. A4's dissent and A6's restrictions remain separate. No “two out of three” claim becomes order authority, and no model gets removed because this single realized event makes another look more accurate. Future disagreement policies need independent qualification.

## Case 12 — kNN has negative marginal contribution

**Configuration:** E=MEAN(XGB, kNN, FMLFDE) is compared with separately specified removal variants. The experimental protocol freezes the surviving-weight rule and eligible recalibration/refit behavior before final outcomes. These variants are new graphs, not simulations of a required live child failing.

**Target/horizon:** one common invented panel of qualified next-session binary observations with matched population, cutoff, label revision and split. The summary losses below are stipulated teaching values, not aggregates reconstructed from the one example row.

**Component forecasts:** one representative row has XGB=0.65, kNN=0.80, FMLFDE=0.55, giving E about 0.6667 and E−kNN=0.60 under fixed equal surviving weights. Individual kNN performance on the illustrative panel is stipulated to be respectable, mean Brier 0.205.

**Ground truth:** the representative row is y=0; the panel uses shared Evaluation-owned binary labels. No missingness or selection difference is hidden in the comparison.

**Metric/result:** stipulated mean losses are E=0.200, E−XGB=0.210, E−kNN=0.190, E−FM=0.205. kNN contribution is 0.190−0.200=−0.010; the other contribution differences are +0.010 and +0.005.

**Interpretation:** a decent standalone model can worsen a specific combination through correlated errors, confidence or weight interactions. The contribution numbers need not add to ensemble gain and are not causal factor importances. A real report still needs paired uncertainty, support and cost.

**Governance outcome:** open a diagnosis/proposal, not an active removal. Verify data/calibration explanations and whether the advantage survives independent testing before changing a future composition.

## Case 13 — Removing kNN becomes a proposal, not a mutation

**Configuration:** following Case 12, CorrectionPlanner proposes G_new=MEAN(XGB,FMLFDE). G_old still includes kNN. The proposal records the negative-contribution evidence, alternatives, candidate weights/calibrator dependencies, bounded work grant and acceptance protocol.

**Target/horizon:** the same target definition, but candidate validation and prospective shadow use their separately eligible windows. Reusing the diagnostic panel as final independent proof would be invalid.

**Component forecasts:** on an invented diagnostic row, old children 0.65/0.80/0.55 yield about 0.6667; proposed surviving children yield 0.60 before any separately specified parent transform. Both stage records are preserved under different graph IDs.

**Ground truth:** diagnostic y=0; later validation/shadow outcomes are independent journal references. They cannot be known when the original proposal is formed, and pending rows stay pending.

**Metric/result:** the diagnostic panel repeats E_old=0.200 versus E_new=0.190. Suppose a separate invented shadow summary then gives old=0.202 and candidate=0.209, a candidate disadvantage of +0.007. These are stipulated teaching summaries, not observed research results.

**Interpretation:** a promising removal hypothesis can fail prospective evaluation. It may have fitted noise, shifted population or changed calibration behavior. The proposal machinery is useful precisely because it does not require activation as its only successful output.

**Governance outcome:** hold or reject the candidate under the preregistered protocol; no future COLD replacement is approved. Keep the existing binding only while its own health/authority remains valid, otherwise deny new use. The planner cannot reinterpret its grant as permission to deploy after a disappointing shadow result.

## Case 14 — Replay survives a composition upgrade

**Configuration:** old run R14 captured G_old with XGB/kNN/FM, its weights, calibrator C_old, profile and all children. At a later date, an independently approved G_new without kNN is selected for future runs. This example assumes that separate approval occurred; the handbook performs none.

**Target/horizon:** the original request's exact KAYNES next-session window, reference, cutoff and target version remain pinned. New requests have their own observation identities; a newer model does not change R14's question.

**Component forecasts:** R14 retains [0.65,0.80,0.55] and mean 0.6667 (unrounded two-thirds for arithmetic). A separately authorized counterfactual using G_new on matched captured inputs might return 0.60, but that value is not written into R14.

**Ground truth:** original qualified J1 has y=0. A later source correction, if any, would append J2 and a new evaluation projection; it would not silently change a report pinned to J1. Here the replayed comparison deliberately retains J1.

**Metric/result:** original mean Brier on that row is 4/9, approximately 0.4444. A separate counterfactual 0.60 has loss 0.36 against J1. The old serialized result and semantic fingerprint remain unchanged; a changed graph/counterfactual receives a different identity. No literal cryptographic digest is invented as if generated by FF.

**Interpretation:** recorded replay answers what was captured, not which model is active today. It works without live model calls. If the exact historical verifier is unavailable, recomputation is UNVERIFIABLE while recorded replay can still pass integrity checks.

**Governance outcome:** preserve both histories and their authority. A later improvement is additive evidence, never a rewrite of earlier forecasts, child dissent, cost or evaluation results.

# 35. Forty practical questions

These answers describe the proposed FF design. They are not promises about current runtime capabilities, guaranteed model quality or investment outcomes. The same four questions recur: What exact event is estimated? Which information was eligible? How was it independently evaluated? Who, if anyone, is authorized to use the result?

## Q1. Why a framework instead of one best model?

Because model quality is conditional and can change, while the meaning of a target, outcome and historical record should not change unnoticed. A framework lets TI replace or reject an instrument without rebuilding unrelated intelligence or losing its controls. It does not guarantee a winner; it supplies the stable comparison, replay and governance conditions needed to find out whether a candidate deserves a role.

## Q2. Why start with Logistic Regression?

It makes a small feature schema, fitted coefficients, regularization and calibration easier to inspect than a large representation system. That reduces the number of moving parts while testing the complete scientific loop. It is an engineering baseline choice, not a claim of universal accuracy. If logistic fails independent qualification, the miniature retains its benchmark and truthful absence rather than granting it primary status by default.

## Q3. Why keep naive and base-rate benchmarks?

They reveal whether a complicated instrument adds anything beyond a simple, precisely defined hypothesis. A base-rate control must use a pinned eligible fit population, not the final test frequency. Persistence must specify its exact output meaning. Neither is automatically calibrated or approved, but both can be useful controls. Removing an inconvenient benchmark after observing losses would change the experiment instead of improving the candidate.

## Q4. Why might XGBoost beat deep learning?

As a modeling hypothesis, a tree method may fit a bounded structured-feature problem adequately with less representation complexity. Deep capacity can add fitting and stability burdens without adding relevant information. FF does not assume this outcome; it tests the exact qualified candidates on matched observations, including calibration, coverage and resource costs. Algorithm reputation is neither evidence of superiority nor a reason to skip a simple comparator.

## Q5. Why might FM/LFDE beat XGBoost?

The family hypothesis is that structured temporal representations and explicit-plus-latent state can retain useful information absent from a simpler feature map. That hypothesis must survive K-only, classical and conventional-model controls, ablation, PIT checks and independent evaluation. If it does, FF can host the resulting instrument without changing consumer contracts. A visually appealing latent space or rich mathematical architecture alone establishes no such advantage.

## Q6. Why might FM/LFDE fail?

Its latent representation might duplicate explicit factors, fit noise, drift across versions, use insufficiently qualified data or cost too much for a small benefit. A head or dynamics layer might add complexity without improving observable outcome loss. FF preserves those failure diagnoses rather than redefining success around a favorable representation plot. Further work needs a new bounded hypothesis; the architecture does not require endless tuning until the family wins.

## Q7. Can TI remain useful if FM/LFDE fails?

Yes. Deterministic A2 evidence, specialist interpretation, A4 challenge, A5 advice and A6 expression analysis retain their accepted meanings. FF itself can stop at a simple qualified miniature or a benchmarked research path with no primary. Optional advanced forecasting does not become a hidden prerequisite for existing safety and absence behavior. The ability to reject a non-contributing family is a strength of the platform boundary.

## Q8. Why can an LLM be a forecaster?

An admitted instrument can map governed context and an exact target into a structured estimate or abstention. An LLM is one possible implementation of that mapping. It must use the existing budget/model gateway, preserve prompt/model/evidence lineage and face the same independent outcomes and controls as numeric instruments. It gains no extra source authority, vote weight or activation rights because its output includes readable reasoning.

## Q9. Why is an LLM percentage not automatically calibrated?

Producing a number between zero and one establishes a format, not a probability-frequency relationship. Persuasive explanations can accompany systematic overstatement or context-dependent error. Independent evaluation must assess reliability in the intended population, and any calibration fit needs eligible separate data and its own artifact. Model or prompt changes can invalidate that qualification. A wrapper named calibrator is no more sufficient than a fluent rationale.

## Q10. What is a primitive forecaster?

It is one scientific instrument at FF's substitution boundary. Primitive does not mean one equation or simple internals. A tree model, language model or rich FM/LFDE pipeline can be primitive from the outer graph's perspective. Required internal trace and dependency lineage still survive. The classification tells the composition engine where substitution occurs; it does not give the instrument permission to become an opaque or unauditable black box.

## Q11. What is a composite forecaster?

It is a forecaster that consumes compatible child results through a declared operator and returns the same outer result contract. Examples include a probability mean, calibrated wrapper, discrete vote and later router or stacker. The graph must remain finite, typed and versioned. Parent qualification is separate from child qualification, and child outputs remain preserved. Nesting is not permission to combine mismatched events or hide a failed dependency.

## Q12. Why is ENSEMBLE(XGBOOST) valid?

A nonempty one-child mean can serve as an identity operation under the normal admission rules. It makes uniform composition handling possible without inventing multiple members. The numeric result equals the child; the graph still records the wrapper. It creates no diversification, independence or new calibration evidence. A raw or unqualified child cannot become qualified merely by being wrapped, and its absence cannot become a neutral probability.

## Q13. What separates voting from probability averaging?

Voting combines shared discrete classes under fixed electorate, quorum and tie rules. Probability averaging combines compatible qualified probabilities of one event. Thresholding probabilities into classes requires an explicit versioned conversion. A two-thirds vote fraction is not automatically a two-thirds event probability. Their evaluation differs as well: Brier applies to admitted probabilistic outputs, while a class rule needs classification metrics and explicit abstention/coverage accounting.

## Q14. Where does ranking fit?

Ranking is a separately admitted operation over comparable scores and an exact dated candidate universe, with orientation and tie semantics. It yields an order, not a calibrated probability or execution instruction. FF's first binary event does not automatically authorize cross-candidate scanner ranking, A3 opportunity reordering or A6 expression replacement. A future ranking study needs its own target, population, metric and consumer acceptance rather than borrowing probability-mean semantics.

## Q15. Where does kNN fit?

kNN is a primitive with an internal reference population, fitted scaler, distance definition, neighbor selection and prediction rule. Those choices belong to a pinned artifact and must exclude future information. Its internal neighbor aggregation is not the FF operator that combines multiple instruments. Adding kNN as an ensemble member therefore creates both a new primitive dependency and a contribution hypothesis to test against the other members and the full parent.

## Q16. What is stacking?

Stacking uses a trained meta-model over child predictions. Those training predictions must be generated without target leakage, commonly through a specified leakage-safe out-of-fold procedure. The meta-model, its selection and any calibration create additional artifacts and independent evaluation requirements. A stacker is not a mean with an impressive name, and a raw-score stacker needs a separately typed specification rather than bypassing the initial calibrated-probability admission rule.

## Q17. What is a regime router?

A router selects an already admitted expert or branch using eligible context and a frozen policy. It is not a mechanism for choosing, after outcomes, which model would have been right. Unselected experts have no produced output for that run and are recorded as NOT_SELECTED. Unknown/stale regimes, missing experts, conditional support and total cost need explicit policies. Evidence of stable conditional advantage must precede qualified routing use.

## Q18. What is a mixture of experts?

Conceptually it uses a context-dependent gate to combine or select specialized instruments. A learned gate introduces another trained component, leakage risk, calibration dependency and support requirement. FF reserves it for separately justified later work, not the miniature. The name does not grant live installation or self-modification: the admitted gate and experts remain pinned, and the full pipeline must beat appropriate static and simple controls under independent evaluation.

## Q19. Why forbid arbitrary compositions?

Syntactic nesting says nothing about shared target meaning, cutoff, units, calibration or missingness. Combining next-session direction, next-week volatility and a regime classifier in one vote creates no coherent event. Arbitrary executable configuration also broadens security and authority. Typed declarative graphs allow finite preflight checks, explicit conversions and replay. They preserve useful recursion while rejecting cycles, hidden loaders, unsupported operators and request-controlled searches.

## Q20. Why preserve child outputs?

Without them, an audit cannot explain whether a parent was useful, dominated by one child, affected by a failed branch or driven by opposing estimates. Child outputs enable component comparisons, leave-one-out hypotheses, calibration diagnostics and resource attribution. They also preserve raw versus transformed stages. A root result alone is insufficient even when its serialized fingerprint is intact: integrity of a summary is not completeness of its scientific explanation.

## Q21. How do we know an ensemble helps?

Compare the exact parent against each major component, an appropriate simple control and a best component selected using eligible validation. Use matched observations, independent calibration, coverage, uncertainty and cost. An ex-post best-on-test oracle must be labeled, not adopted as a selection policy. A tiny lower loss on surviving rows can be noise or selection bias. Engineering execution of an ensemble is not evidence that it earns operational use.

## Q22. What is leave-one-out contribution?

It compares the full ensemble E with a separately specified E-minus-member experiment. Under the stated sign convention, loss(E−j)−loss(E) is negative when removal improves the variant. Weights and downstream refits must be declared before evaluation. Contributions depend on interactions and need not sum to total gain. The result can motivate a future correction proposal; it does not authorize dropping a failed required member during a live request.

## Q23. Why compare the same observations?

Otherwise population difficulty can masquerade as model quality. A challenger evaluated only on easy available cases may look better than a benchmark evaluated everywhere. Shared observation keys, labels and cutoff semantics establish fair pairs, while intended/union populations preserve absence and coverage. Different admitted feature sets are allowed when they are the experimental question. Identical evidence bytes are not required, but comparable outcomes and information eligibility are essential.

## Q24. What does paired comparison add beyond two averages?

It evaluates loss differences on matched observations and pins the exact arms, truth revisions, split, metric policy, denominators and resource protocol. A PairedComparisonManifest makes the scientific claim reconstructible. It also preserves excluded and not-evaluable cases instead of silently dropping them. A negative mean challenger-minus-benchmark loss is only a summary; uncertainty, support and selection history still determine whether it is convincing evidence rather than noise.

## Q25. Why is ground truth outside the models?

Because a forecaster must not define or repair the outcomes used to judge itself. Evaluation owns the shared event definition and qualified labeler, using independently admitted source evidence. All arms face the same terminal/reference comparison, schedule and action basis. Model agreement is not a label, a recommendation is not reality, and a provider's revised data cannot silently replace earlier knowledge. This separation prevents self-confirming scientific claims.

## Q26. What if ground truth changes?

Append a new source/journal revision with predecessor, availability time and reasons. Create a new ledger/evaluation projection that explicitly selects that revision. The old forecast and old report remain pinned to their original records. Later evidence can disqualify future use or reveal an earlier mistake without rewriting what was captured. Replay must not simply select the latest label, and later corrections cannot enter earlier training folds.

## Q27. What is benchmark versus challenger?

The benchmark is the declared reference configuration for an exact study/profile. The challenger is a candidate compared against retained controls or the current primary. These are contextual roles, not permanent quality labels. A former challenger can later be approved and selected for future primary use while the old primary remains a benchmark. The Benchmark Registry pins references; it does not grant training authority or activate the challenger.

## Q28. What does shadow mode actually guarantee?

Its intended guarantee is prospective, non-influencing collection under explicit authority and bounds. Outputs, failures and costs are captured for evaluation without choosing current trading actions or replacing the primary. SHADOW role and SHADOW lifecycle are distinct concepts. If users or hidden logic select actions from shadow outputs, the non-influencing premise no longer holds. A real acceptance protocol must therefore define allowed exposure as well as model execution.

## Q29. What happens when forecasters disagree?

Their different estimates, ancestry, calibration scope and evidence limits stay visible. FF can report a pinned dispersion measure without declaring that consensus is correctness or disagreement is failure. No final automatic abstention threshold is invented here. A future policy may use disagreement only after independent qualification. Existing A4 dissent and A6 restrictions are preserved; the most confident instrument does not receive authority to erase competing evidence.

## Q30. Can FF self-learn?

It can support a governed learning process around shared outcomes: diagnosis, bounded proposals, authorized candidate training, independent validation, shadow and approval. That process is outside request-time inference. A proposal does not grant its own compute or source access, and a drift signal does not justify arbitrary retraining. The miniature already needs basic lifecycle and replay discipline; a later correction planner expands workflows without inventing autonomous authority.

## Q31. Can FF rewrite production automatically?

Not in the proposed initial design. Candidate generation, even if eventually automated within bounds, is separate from independent approval and trusted future COLD selection. Shadow execution does not mutate active roots. Existing health policies may deny new use of a degraded artifact, but that is not permission to train or install a replacement. Old forecasts, artifacts and approval events remain immutable through promotion, suspension and rollback.

## Q32. Why no forecasting DSL now?

Typed project-native configuration can express finite graphs, ports, artifacts and rules without another language, parser or executable surface. Conceptual expressions help readers but are not Shell commands. A DSL would add syntax, validation and security work before the miniature proves its science. Future configuration ergonomics can be revisited if concrete needs justify them, while preserving the same typed admission, authority and fingerprint semantics.

## Q33. How is replay guaranteed?

Only a precisely stated replay promise can be guaranteed by an implementation. Recorded replay verifies captured inputs/results and semantic integrity without live dependencies. Exact recomputation needs the historical artifact/verifier closure and a reproducible numeric execution; missing or mutable dependencies can make it UNVERIFIABLE. Counterfactual evaluation is a new run. The architecture requires these distinctions, but this thesis is not evidence that an FF runtime or verifier has been implemented.

## Q34. How does FF relate to A7?

FF is the proposed platform within A7 Forecasting, cooperating with independent Evaluation and Governed Learning. It reuses common ground truth, journal, registry and population concepts rather than duplicating them. The existing A7 documents remain a preserved checkpoint. Explicit integration must map contracts, role/lifecycle events, replay and later facade exposure before independent acceptance. A7 acceptance is still paused; this handbook does not rewrite its milestones or approve implementation.

## Q35. How does FF relate to FM/LFDE?

FF supplies shared contracts, composition and fair scientific infrastructure. FM/LFDE supplies an advanced instrument family's tensor, explicit/latent state and head internals. The family keeps its own rich trace and research gates while using common outcomes and evaluation. Other instruments need not build a Market Tensor or learn Z. The existing FM/LFDE thesis is preserved as the advanced-research companion, not merged into this platform handbook.

## Q36. Could transfer-learning models fit later?

Conceptually yes, as qualified primitives with explicit pretrained artifact and adaptation lineage. Pretraining on future or unqualified data is not exempt from PIT requirements merely because labels were absent. Rights, vintage, overlap, fit cutoffs, reproducibility and calibration still need review. A model family can be structurally representable while remaining scientifically unqualified. Registration is not proof of historical knowability, independent value or permitted production use.

## Q37. Can ensembles be nested?

Yes, within a finite typed DAG whose every edge satisfies admission. Nested probability means, calibrators, conversions and votes retain distinct output meanings and artifacts. Shared children execute once under identical pins, but shared ancestry is disclosed rather than counted as independent confirmation. Duplicate influence within one operator is rejected. The parent requires its own qualification, and any required child failure remains visible rather than silently changing the nested graph.

## Q38. Can one ensemble benchmark another?

Yes. Composites are Forecasters, so exact qualified compositions can form paired arms just like primitives. Compare matching targets, observations, cutoffs, label revisions and metric policies, with complete child traces and resource usage. Retain relevant simple and component controls so an elaborate-versus-elaborate comparison does not hide a better simple model. New weights, calibrators or topology create new identities rather than changing a benchmark in place.

## Q39. Can a forecaster abstain?

Yes, with an explicit status, reasons and lineage. Abstention differs from unsupported semantics, unavailable dependencies and operational failure. It produces no invented probability, including no “neutral” 0.50, and is not a negative market label. The evaluation population records its coverage contribution and metric-specific absence. A composite's handling of abstention must be pinned; a live missing required child cannot silently reduce its electorate or probability denominator.

## Q40. Who owns final trading action authority?

TM owns authority, account risk, capital, quantity and action decisions; the broker owns execution truth. A4 owns thesis challenge, A5 position advice and A6 expression suitability. FF contributes an optional, scoped forecast only through separately admitted consumers. A 0.70 underlying endpoint estimate cannot authorize a CE purchase or establish option PoP. Missing FF does not remove existing vetoes, NO_TRADE, insufficient evidence or NO_OPTION_TRADE behavior.

# 36. Glossary, sources and reading routes

This book is derived from repository architecture, not new market research or measured experiments. The source hierarchy matters: current FF design owns shared proposed semantics; system/source/pluggability constraints remain superior; FM/LFDE owns its advanced internal science; A7's preserved checkpoint requires later explicit integration. Historical status wording in an older artifact is not a new implementation approval.

| Term | Meaning in this handbook |
|---|---|
| FF / instrument | Stable Forecasting Framework / replaceable scientific forecaster |
| PIT / cutoff | Point-in-time eligibility / latest admitted decision information instant |
| Target / horizon | Exact event and units / exact reference and terminal window |
| DAG / node / root | Finite acyclic typed dependency graph / identified computation / assigned output |
| Calibration | Qualified probability-frequency relationship plus separately fitted transformation where used |
| Observation / request | Evaluation-owned market question identity / one admitted invocation identity |
| Journal / ledger | Append-only outcome truth references / immutable joined evaluation view |
| Benchmark / primary | Fixed comparator / selected scoped advisory root, not best forever |
| COLD / HOT | Trusted pre-start binding / stronger live replacement capability, not delivered here |
| Recorded / recomputed / counterfactual | Captured history / exact pinned verification / new alternative experiment |
| K / Z / X / Q | Explicit factors / learned representation / fused state / typed quality-uncertainty envelope |
| NOT_EVALUABLE / UNVERIFIABLE | Metric lacks eligible basis / exact recomputation cannot be established |

The primary platform sources are [FF architecture](../../TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md), [bounded detailed roadmap](../../TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) and [architecture decision/reconciliation record](../../TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md). They specify admission, DAG identity, role/lifecycle separation, common truth, comparison and staged gates. Numerical examples in this book teach those rules; they are not architecture policy defaults.

For the initial target, clocks, outcome facets and existing evaluation proposal, read [A7 architecture](../../TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md), [A7 roadmap](../../TIAF_A7_DETAILED_ROADMAP.md), [A7 thesis reconciliation](../../TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md) and the [A7 thesis record](../../TIAF_A7_FORECASTING_EVALUATION_LEARNING_THESIS_RECORD.md). The preserved [A7 illustrated PDF](../../TI_Forecasting_Evaluation_Learning_Thesis.pdf) provides the earlier end-to-end explanation. None is rewritten by this thesis.

For advanced state research, read [FM/LFDE architecture](../../TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md), [family roadmap](../../TIAF_FM_LFDE_DETAILED_ROADMAP.md), [family decision record](../../TIAF_FM_LFDE_DECISION_RECORD.md), [thesis record](../../TIAF_FM_LFDE_THESIS_RECORD.md) and the preserved [FM/LFDE PDF](../../TI_FM_LFDE_Market_State_Forecasting_Thesis.pdf) / [editable DOCX](../../TI_FM_LFDE_Market_State_Forecasting_Thesis.docx). The FF decision record dispositions the earlier family findings; this book's FFT identifiers are a new review list, not replacements for them.

Boundary references are the [A2 deterministic baseline](../../TIAF_A2_9_DETERMINISTIC_BASELINE.md), [A3 specialist architecture](../../TIAF_A3_ARCHITECTURE.md), [A4 challenge design](../../TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md), [A5 position design](../../TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md) and [frozen A6 expression design](../../TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md). They explain why a forecast cannot recalculate a baseline, erase dissent or authorize an order.

Cross-cutting sources are [source/provenance](../../TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md), [R1–R5 pluggability](../../TIAF_PLUGGABILITY_ARCHITECTURE.md), [Monitoring](../../TIAF_MONITORING_ARCHITECTURE.md), [deployment](../../TIAF_DEPLOYMENT_ARCHITECTURE.md), [TI Shell](../../TIAF_TI_SHELL_ARCHITECTURE.md), [capability map](../../TIAF_CAPABILITY_MAP.md) and [deferral register](../../TIAF_DEFERRAL_REGISTER.md). The [forward roadmap](../../IMPLEMENTATION_ROADMAP.md) owns current navigation.

No new paper search, provider query, model call or training run was required to produce this explanatory companion. Statistical methods are described as protocol choices requiring suitable assumptions, not newly validated research claims. The editable source, chart data/SVG and local artifact validators accompany the document so a future author can review both its calculations and its layout without touching TI runtime.

# 37. Thesis Findings for FF Architecture Reconciliation

The findings below are numbered **FFT-01–FFT-28** to distinguish them from FF-0–FF-7 implementation stages and the earlier FM thesis's FF-prefixed findings. Each states a classification, source seam and next action. None is silently applied to normative architecture. NO_CHANGE means the current proposed boundary is adequate; it does not mean implemented or accepted. Clarifications and details should be resolved during the next scoped reconciliation/acceptance, not through runtime improvisation.

| Class | Meaning in this review |
|---|---|
| NO_CHANGE | 15 findings: preserve the existing proposed architecture rule |
| CLARIFICATION_NEEDED | 9 findings: make an existing boundary more precise before implementation |
| ARCHITECTURE_CHANGE_PROPOSED | 0 findings: no necessary change to ownership or governing behavior identified |
| IMPLEMENTATION_DETAIL_ONLY | 2 findings: choose and test a bounded representation/profile without changing the principle |
| DEFER | 2 findings: keep conditional later scope outside the miniature |

## FFT-01. Request/result boundary — CLARIFICATION_NEEDED

FF architecture §3 adequately separates request, result, generation and qualification. The later schema review should make the minimum validity, uncertainty-kind and typed absence fields explicit, including whether each is required for a raw research result versus admitted advisory projection. **Next action:** create a field-level mapping with examples of unavailable, raw and qualified outputs. Do not encode missing scientific state inside metadata or migrate existing schemas merely because the conceptual names match.

## FFT-02. Primitive and composite abstraction — NO_CHANGE

FF §4 already supports one outer Forecaster boundary while preserving instrument internals. FM/LFDE can remain sophisticated without owning a second platform, and kNN remains a primitive. **Next action:** retain conformance examples for a simple primitive, an advanced primitive and a composite. Internal opacity must not be excused by the word primitive; transitive provenance and scientifically important traces still need resolvable references.

## FFT-03. Graph identity and equivalent nodes — CLARIFICATION_NEEDED

FF §5 defines bounded typed DAGs, stable traversal and duplicate influence rejection. Before schema freeze, specify how semantic execution identity treats aliases, commutative child order, shared input pins and an intentional new stochastic replicate. **Next action:** provide positive/negative identity fixtures. Equal numeric predictions are not proof of equivalence, renamed identical nodes are not independent voters, and random replicates must not inflate the market-observation count.

## FFT-04. Composition compatibility — NO_CHANGE

FF §6 makes exact target/window/basis/cutoff/type/calibration mandatory while allowing different admitted feature families. This supports fair scientific comparison without requiring identical evidence bytes. **Next action:** preserve the distinction in schema documentation and rejection fixtures. No outer calibrator, attractive average or common symbol should repair a target mismatch, missing required branch or information-eligibility violation.

## FFT-05. Singleton composites — NO_CHANGE

FF §5 permits a documented one-child probability identity operator without claiming diversification. Case 6 demonstrates why the graph identity can differ while the numeric result remains equal. **Next action:** test identity output, unique cost and inherited admission explicitly. A singleton should not become an independent ensemble observation, a calibration bypass or a fallback for a multi-child graph whose required members failed.

## FFT-06. Voting edge cases — CLARIFICATION_NEEDED

FF §7 establishes fixed electorate, explicit conversion, quorum and tie/abstention behavior. The bounded operator specification still needs a truth table distinguishing a legitimate child ABSTAIN, required execution failure, no votes, insufficient quorum and a class tie. **Next action:** pin those cases before implementing any vote. Keep ABOVE_REFERENCE versus NOT_ABOVE_REFERENCE semantics explicit so flat prices do not accidentally become strict downward events.

## FFT-07. Probability ensemble semantics — NO_CHANGE

FF §§6–8 require qualified same-event children and independent parent qualification. The worked cases show both a helping and a harmful mean without adjusting weights to make either attractive. **Next action:** retain complete child traces, finite nonnegative normalized weights and no silent missing-member renormalization. A future raw-score stacker is a different typed instrument, not an alternative interpretation of the initial mean operator.

## FFT-08. Ranking scope — DEFER

FF §7 keeps ranking separate from probability composition and from A3/A6 authority. The initial binary target does not define an investable cross-candidate policy. **Next action:** leave ranking as later scope requiring a dated universe, score orientation, tie rules, target/metric and consumer acceptance. Do not implement a forecast-to-scanner ordering shortcut as a usability feature of the miniature.

## FFT-09. Calibration placement — NO_CHANGE

FF §8 already separates fit, application and qualification and distinguishes child versus parent calibrators. Nested calibration cannot repair an incompatible graph. **Next action:** preserve raw/transformed stage records and explicit leakage-safe fit lineage. Any downstream wrapper must be reconsidered when a child artifact is refitted; the mere continued existence of a calibrator ID does not establish continued applicability.

## FFT-10. Roles and lifecycle mapping — CLARIFICATION_NEEDED

FF §9 deliberately refines the A7 proposal without editing its existing state names. The next integration review should provide a lossless mapping of old SHADOW_APPROVED/ADVISORY_APPROVED events to separate lifecycle history, role assignments and scoped approvals. **Next action:** include denied and suspended histories in mapping fixtures. No conversion may broaden authority or mistake a run's SHADOW purpose for production eligibility.

## FFT-11. Benchmark Registry ownership — NO_CHANGE

FF §10 makes the registry an Evaluation-owned curated reference view over shared artifact/lifecycle records. That avoids a second approval or activation system. **Next action:** retain benchmark-suite versioning and preregistered comparator requirements. Changing a control after inspecting a challenger result must create a new experiment identity, not replace an old reference to make progress appear larger.

## FFT-12. Ground-truth ownership — NO_CHANGE

The exact A7 event, qualified adjacency, positive finite same-basis decimal endpoints and append-only revisions are preserved by FF §10. A model never owns or repairs its label. **Next action:** retain explicit missing/invalid/flat/censored examples and source qualification gates. Synthetic session pairs can validate mechanics but cannot close calendar, action or historical-availability deferrals or justify a real forecast retroactively.

## FFT-13. Forecast Ledger — NO_CHANGE

FF §11 defines immutable joined projections rather than mutable probability/outcome cells. Case 14 shows why new truth and new models need new views, not overwritten records. **Next action:** maintain one observation identity with all request-level attempts/costs and exact predecessor links. Do not create a second source-of-truth journal or merge conflicting captures merely because they concern the same symbol.

## FFT-14. Paired-comparison identity — NO_CHANGE

The Evaluation-owned manifest in FF §12 already binds exact arms, populations, revisions, splits, metric and resource policies. It can be created later without adding future IDs to old forecasts. **Next action:** preserve comparison-level fingerprints and per-metric dispositions. The common intersection supports paired loss while full intended/union accounting supports honest coverage; an empty intersection must never yield PASS or zero loss.

## FFT-15. Numeric metric conventions — IMPLEMENTATION_DETAIL_ONLY

FF §13 identifies the right metric families but intentionally does not choose all numerical conventions. The implementation protocol must pin log base, exact-endpoint/clipping treatment, weights, reliability summaries and undefined denominator representation. **Next action:** add deterministic arithmetic fixtures and document which outputs are finite, infinite or not evaluable. Reporting conventions must not silently alter the issued probability or invent labels.

## FFT-16. Statistical protocol choices — IMPLEMENTATION_DETAIL_ONLY

FF §13 requires preregistered time-aware uncertainty and selection discipline without universal thresholds. Concrete data-dependent block design, support criteria, confidence reporting and practical-usefulness limits remain bounded study decisions. **Next action:** specify them before final outcome inspection and capture realized split membership and all trials. An inconclusive outcome remains legitimate; a small apparent gain is not a reason to choose a more favorable test afterward.

## FFT-17. Context slices and router evidence — CLARIFICATION_NEEDED

FF §13 requires cutoff-eligible, predefined regimes and separate horizon evaluation. Before empirical study, clarify how cohort-definition versions, UNKNOWN context, support and overlapping memberships enter population/metric reports. **Next action:** provide an example in which global improvement and local degradation coexist without hidden filtering. Later routing needs independent evidence and cannot use future-smoothed labels or a best-regime oracle as a production policy.

## FFT-18. Component observability — NO_CHANGE

FF §14 already requires every child, operator, conversion, calibration and root record, with reasons and ancestry. **Next action:** retain a nested composition example in which a shared child executes once but influences multiple ancestors. Recorded replay cannot invent outputs for a later router's unselected experts; any full-expert comparison needs separately authorized captured runs over the matched inputs.

## FFT-19. Leave-one-out variants — CLARIFICATION_NEEDED

FF §14 correctly treats removal as a new experiment, not live failure handling. The comparison manifest or referenced protocol should identify surviving-weight rules, downstream refits, calibration qualifications and actual resource changes for each E-minus-member arm. **Next action:** provide both fixed-rule and refitted variant examples with separate identities. Negative contribution is conditional evidence for a proposal, not a causal feature importance or automatic permission to remove the member.

## FFT-20. Disagreement exposure — NO_CHANGE

FF §14 exposes disagreement without inventing a final abstention rule. The two illustrative member groups show why a mean alone is insufficient and why consensus is not calibrated confidence. **Next action:** retain member identities, common-event admission, missingness and ancestry with any dispersion statistic. Any later disagreement-based policy must be independently trained/qualified and cannot overwrite A4 dissent or A6 restrictions.

## FFT-21. LLM qualification limits — CLARIFICATION_NEEDED

FF §16 places LLMs behind the governed gateway with raw-probability and historical-vintage warnings. The next acceptance profile should explicitly distinguish known model revision, historical training-vintage qualification, prospective-only evidence and exact-recompute availability. **Next action:** include UNKNOWN revision/cost and persuasive-but-miscalibrated cases. A stored response can support recorded replay without proving historical knowability or a reproducible remote model.

## FFT-22. FM/LFDE boundary — NO_CHANGE

FF §16 preserves the advanced family and its tensor/K/Z/state/head trace while moving common truth and comparison to shared owners. **Next action:** keep K-only controls, local family gates and internal-versus-outer calibration identity visible. A failed latent contribution should stop that candidate without removing deterministic TI or requiring all other forecasters to implement the family's internal representation.

## FFT-23. Correction authority — NO_CHANGE

FF §15 separates diagnostics, proposals, authorized candidate generation, independent evaluation, recommendation and explicit future COLD approval. Case 13 shows a candidate that improves retrospectively but fails shadow. **Next action:** preserve rejection, denial and rollback history. Neither recalibration nor member removal is a special fast path around approval, and a proposal's resource grant cannot be interpreted as deployment permission.

## FFT-24. Replay pins and promise levels — CLARIFICATION_NEEDED

FF §18 distinguishes recorded replay, pinned recomputation and counterfactual work. The verifier specification should enumerate the exact equality promise versus declared numeric tolerance, including mutable remote instruments and transitive calibration/basis dependencies. **Next action:** provide a captured-pass/recompute-unverifiable example and evaluation replay pinned to an older truth revision. A new comparison links an old forecast; it does not mutate it to add future identity.

## FFT-25. COLD composition — NO_CHANGE

FF §§17–18 apply R1–R5 without claiming existing R5 selectors already implement FF. **Next action:** preserve trusted startup ownership, requiredness by operation, optional adapter isolation and no HOT replacement. Registration and shadow execution must not change active roots. Descriptors remain discovery metadata, not evidence of calibration, readiness or authority for a specific request.

## FFT-26. Miniature scope — NO_CHANGE

FF §17 and FF-0–FF-2 define a comparative miniature with BaseRate and Logistic, one target/journal and at most one qualified primary. A singleton is a valid mechanics step but not a complete comparative success. **Next action:** keep engineering, empirical, approval and publication gates separate. The system must remain usable for benchmark inspection and explicit absence if logistic never qualifies; no ensemble or advanced family is mandatory.

## FFT-27. A7 and FF integration — CLARIFICATION_NEEDED

FF §20 supplies a precise future integration map while preserving current A7 files. The next review should resolve concrete schema/role-event mappings and the boundary between shared Evaluation services and FF inference before acceptance. **Next action:** make a section-by-section integration diff only when separately authorized. Avoid duplicate journals/registries, accidental A3-schema reuse or a new public train/promote/configuration surface under the name of FF usability.

## FFT-28. Advanced routing and MoE — DEFER

FF-7 remains conditional on useful qualified experts, eligible context, sufficient support and bounded fitting. The miniature does not need it. **Next action:** retain static/simple controls and explicit NOT_SELECTED records; a future gate needs its own calibration, missing-expert policy and counterfactual comparison plan. No automatic family tournament, best-on-test switching, HOT loading or unbounded search follows from describing recursive composition.

The review identifies no necessary new ownership mechanism or architecture change to make the handbook coherent. Its clarification/detail items should be dispositioned explicitly; its deferred items remain deferred. All 58 canonical deferral rows are preserved. No finding accepts FF or A7, approves a model, closes a data gate or authorizes runtime work.

**Next: TIAF FORECASTING FRAMEWORK — THESIS / ARCHITECTURE RECONCILIATION PASS.** A6 FROZEN; A7 ACCEPTANCE PAUSED; FF ARCHITECTURE DRAFT; FF THESIS CREATED; FM/LFDE preserved as an advanced family; FF RUNTIME NOT_IMPLEMENTED.
