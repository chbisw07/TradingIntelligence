# 1. Why a Market-State Forecasting System?

Markets provide observations, not a ready-made description of their causes or future. A price series may rise while participation narrows, sector conditions deteriorate and an event changes the information available to participants. A useful forecasting system should be able to represent such tensions, attach uncertainty to its estimates and discover whether additional information improves predictions. It should also be able to conclude that a small direct model is sufficient. More elaborate internal structure is a hypothesis, not a requirement for intelligence.

The central proposition is that TI should construct a point-in-time representation of observable and latent market state, investigate its evolution, infer calibrated outcome distributions, measure each information source's incremental contribution and improve through governed correction. This handbook qualifies that proposition in two ways. First, the initial typed state is not automatically a probabilistic posterior; it may be a deterministic assembly carrying explicitly unestimated uncertainty. Second, a direct forecast head is a legitimate control and may outperform a separately modeled state-dynamics layer. The system must earn both probabilistic claims and architectural complexity.

:::flow 01 The proposed evidence-to-forecast chain and its control bypass
OBSERVE → Eligible, versioned information O at the decision cutoff
REPRESENT → Explicit K plus an optional pinned learned Z; preserve quality Q
ESTIMATE → Horizon-specific current state X, with stated uncertainty semantics
FORECAST → Direct head OR validated future-state dynamics followed by a head
EVALUATE → Later factual outcome, proper loss, coverage and retained controls
GOVERN → Candidate change → independent tests → shadow → explicit future approval
:::

FM means Forecasting Module. LFDE means Latent Factor Discovery Engine. Neither is implemented at this edition's checkpoint. A6 is frozen, A7 acceptance is paused, and the FM/LFDE architecture is a draft. The thesis is a non-normative companion; its findings do not silently amend that draft. Every symbol, model output, experimental metric, timing and approval in a worked teaching scenario is illustrative and invented. They are not live findings or policy defaults.

Deterministic A2/A4/A5/A6 remain visible controls, not inconvenient legacy stages to hide. TI offers intelligence; TradeMonitor owns authority, risk, capital and action coordination, while the broker supplies execution truth. A forecast cannot remove an A4 restriction, overturn an A6 absence or authorize an order. A system that respects those limits can produce a useful negative result: the richer representation did not help, so keep the simpler control.

# 2. Six Boundaries That Prevent Category Errors

An observation is a supplied claim about something measured or reported: a completed close, a volume field, a dated release. A state is an inference or constructed summary of eligible observations. A forecast is a distribution over a named later outcome. A decision incorporates authority, objectives and constraints that the distribution does not own. Collapsing these objects makes a system look decisive while making its explanations impossible to audit.

:::figure 02 Six distinctions and the mistake each prevents
| Distinction | Correct interpretation | Rejected shortcut |
|---|---|---|
| OBSERVATION ≠ STATE | A measured close can support a trend descriptor | Calling a latent regime an observed fact |
| STATE ≠ FORECAST | A bullish state can coexist with wide future uncertainty | Treating current trend as a calibrated success probability |
| FORECAST ≠ DECISION | Probability is evidence for an authorized consumer | Turning p = 0.70 into an order |
| LEARNING ≠ LIVE SELF-REWRITING | Offline candidates earn future approval | Replacing active weights after a miss |
| LATENT ≠ MAGIC | Coordinates are outputs of a versioned estimator | Naming z_3 as hidden institutional buying |
| COMPLEXITY ≠ INTELLIGENCE | More machinery must improve qualified evidence | Retaining a model because its diagram is impressive |
:::

Consider an illustrative bullish close-to-close descriptor. A short-horizon pullback model can still assign meaningful downside risk; an operational manager can still reject entry because capital is unavailable. None of these statements contradicts the others until target, horizon, information cutoff and decision authority are aligned. A2's score measures a deterministic policy's assessment. It is not a training label for truth and is not a probability waiting to be rescaled.

Learning introduces another distinction: parameters can be learned without granting the learner control over production. An authorized offline job may generate a candidate encoder or recalibrator. Evaluation can document whether it meets preregistered criteria. A reviewer can refuse promotion. The old record remains the old record at every step. The word self-correcting refers to this governed feedback process, not to an organism that rewrites its own rules.

These boundaries constrain language as well as code. Say “model-conditional regime estimate,” not “the market's hidden truth.” Say “illustrative improvement under an assumed protocol,” not “TI has alpha.” Say “proposed future capability,” not “the runtime does this.” Precise labels keep uncertainty and ownership available to both expert reviewers and ordinary users.

# 3. Mathematical Objects and Predictive Distributions

Let t be a decision cutoff instant. O_t is the information eligible under the pinned point-in-time and admission policy at that instant. A historical event is not eligible merely because it happened before t: its actual availability and accepted version matter. The notation O_≤t denotes the eligible history. K_t is a disclosed factor transform, Z_t a representation produced by a pinned encoder, and Q_t the quality/uncertainty/provenance envelope. Superscripts identifying schemas and artifacts are suppressed below only to keep the notation readable.

= K_t = g(O_≤t)                         Z_t = E_φ(M_t, N_t, G_t)

= X_t = F_ψ(K_t, Z_t, Q_t)

Y_(t+h) denotes a **random outcome**, not the distribution itself. Its forecast distribution is P_hat_t; Y*_(t+h) is the subsequently observed qualified realization. H identifies the exact horizon and B the price/label basis. This distinction matters: a binary random variable, a probability assigned to it and the later realized class are three different objects.

For a genuinely probabilistic state model, let q_η(x_t given O_≤t) describe current-state uncertainty and p_θ(x_f given x_t, O_≤t) describe future evolution, where x_f means x_(t+h). A head supplies p_β(y given x_t, x_f, H, B). Integrating over the unknown states yields a predictive distribution:

= P_raw(y given O_≤t, H, B) = ∫∫ p_β(y given x_t, x_f, H, B)
=                                      × p_θ(x_f given x_t, O_≤t) q_η(x_t given O_≤t) dx_f dx_t
= P_hat_t = Cal_κ(P_raw)                loss_t = L(P_hat_t, Y*_(t+h))

:::figure 03 Two valid routes; neither may condition on a known future state
| Route | Computation | Interpretation |
|---|---|---|
| Direct control | Eligible K or K+Z → head → calibration | No separate dynamics claim |
| State/dynamics candidate | Filtered current-state uncertainty → future-state distribution → integrate head → calibration | Additional model assumptions must earn their place |
| Forbidden route | Later realized state or label → today's features | Future leakage, not a better model |
:::

The equations assume the named distributions and conditional relationships are actually defined. They do not prove that X is Markov, sufficient or economically identifiable. A deterministic state can be treated mathematically as a point mass, but the report must not label unmodeled uncertainty as measured zero. A direct head P_raw(y given K_t, Z_t, H, B) is an acceptable simpler model. Separate marginal heads for direction and volatility do not automatically specify a coherent joint future path. These qualifications keep mathematical notation from implying guarantees the system has not earned.

# 4. Information Clocks and Point-in-Time Integrity

Point-in-time integrity asks a stricter question than “is this an old row?” It asks which version could legitimately have informed this particular decision. Each observation may have an event interval, publication time, source availability time, local acquisition time and admission time. Later revisions create new versions. A model has its own fit cutoff and artifact-availability history. Both data and learned transformations must satisfy the experiment's knowledge boundary.

:::figure 04 Illustrative cutoff audit: event time alone is insufficient
| Item | Clock evidence at cutoff 16:00 | Treatment |
|---|---|---|
| Completed local close | Observed, available and admitted before cutoff | Eligible if source/basis qualification passes |
| Earlier event reported at 16:05 | Event preceded cutoff; availability did not | Exclude from this decision |
| Overseas coming close | Same displayed date, but not yet observed locally | Exclude; an older available close may carry an age flag |
| Macro correction tomorrow | Older reference period, new later vintage | Separate later version, never overwrite |
| Encoder fitted on tomorrow's unlabeled rows | No outcome labels used, but future distribution observed | Ineligible historical encoder |
:::

All clock times in the example are illustrative; the table asserts no real exchange schedule. Application instants are timezone-aware and normalized with `zoneinfo.ZoneInfo("Asia/Kolkata")`. Other aware zones may be accepted and normalized; naive datetimes are rejected. JSON timestamps carry `+05:30`. Dates and session IDs are not converted into invented midnight instants. There is no naive `datetime.now()` or manual offset arithmetic.

Captured replay and retrospective historical research are related but not identical. Captured replay can prove what a particular recorded system consumed. A later-acquired historical dataset needs independently qualified historical availability, revisions and universe membership before it supports a strong as-known claim. Current adjusted prices, today's index constituents and an undated graph cannot automatically reconstruct yesterday's information set. If historical knowability is unknown, say so; a precise hash does not repair the missing provenance.

The fit boundary includes scalers, imputers, PCA, neural encoders, learned graph edges, probes and model selection. Self-supervision is still fitting. Training on unlabeled future test data exposes the future distribution and invalidates a strict prospective claim. Later labels also need maturity and qualification. Leakage is not a score penalty to subtract from a good result: it invalidates the comparison that produced the result.

# 5. Inside the Market Tensor

A Market Tensor is a typed arrangement of eligible measurements, not a picture of a candlestick chart. For one resolution, write M_t in R^(A×T×C): A indexes neutral assets or related market entities, T historical positions and C channels. The practical artifact also contains ordered manifests, masks, units, timestamps, transformation versions and evidence references. Without that surrounding contract, identical array dimensions can encode entirely different meanings.

:::figure 05 A small illustrative tensor slice and its three axes
| Asset axis A | Time slot τ1: return / volume | Time slot τ2: return / volume |
|---|---|---|
| Neutral equity ID A | 0.010 / 120 | 0.000 / 0 |
| Neutral equity ID B | −0.004 / MISSING | 0.006 / 95 |
| Benchmark ID | 0.002 / NOT_APPLICABLE | −0.001 / NOT_APPLICABLE |
:::

The cells show two channels at each time slot, not a two-dimensional image. Returns are dimensionless; volume units and applicability must be specified. The values are invented. A factual zero is retained, while missing volume and benchmark non-applicability remain different reasons. A real bundle never relies on the printed words in this table as numeric values: it stores typed masks/reasons alongside the numerical representation.

Asset IDs must not carry provider-local ticker suffixes into domain meaning. Channel order explicitly identifies feature owner, formula version, unit, source family and validity requirement. Asset order is a manifest, not an assertion that neighboring rows have spatial proximity. An encoder that applies image-style convolution across neighboring stock IDs would introduce an unjustified invariance. A new listing, delisting or changed membership must not silently slide the remaining columns into new identities.

Candidate channel families include OHLC transforms, returns, realized volatility, participation/liquidity, captured A2 features, breadth, relative/sector context, derivatives, available-vintage macro/global observations and admitted intelligence-derived summaries. The initial experiment uses a small qualified allowlist, not every row in that vocabulary. Raw text stays in a separate governed narrative branch.

Replay identity includes shape, axis order, dtype/precision, masks, data vintages, scaler, cutoff, admission policy, calendar and corporate-action basis. Semantic collections are immutable in future contracts; arrays can still serialize as ordinary JSON arrays. A content fingerprint protects identity, not truth. The schema must explain what the bytes mean before the model is allowed to learn from them.

# 6. Resolution, Normalization and Missingness

A useful logical design is a bundle of short-, medium- and long-resolution tensors. Their asset sets, lookbacks and channel families need not be identical. This is not a requirement to build every bundle initially. The first next-session experiment should choose the smallest qualified resolution set that addresses its hypothesis. A larger tensor increases storage, fit complexity, missingness and opportunities to mistake correlated inputs for independent evidence.

:::figure 06 Three masks answer three different questions
| Condition | Factual observation / structural padding / artificial mask | Learning treatment |
|---|---|---|
| Supplied zero return | Observed / no / no | Real zero enters eligible computation |
| Provider value missing | Missing / no / no | Missing reason; not a reconstruction target |
| Asset outside dated membership | Not an eligible cell / yes / no | Exclude structural padding |
| Observed training value deliberately hidden | Observed / no / yes | Reconstruct only if the chosen training objective selects it |
:::

The truth table explains concepts, not a finalized bit-level encoding. The final findings ask for precise mask interaction and empty-denominator behavior before implementation. In particular, artificial masking does not convert an unknown observation into ground truth. A batch with no valid reconstruction targets cannot contribute a fictitious zero loss. Missingness, non-applicability and an unavailable required branch must remain visible downstream.

Normalization is also a learned dependency. A per-channel mean and scale must come from eligible training data, or from a documented window-local transform using only that row's available past. Calibration/test rows do not refit the scaler. Prices, returns, volumes and categorical event IDs need different transformations. Whole-dataset clipping thresholds and imputation can leak just as readily as a neural encoder. A constant or sparse channel needs a declared treatment; division by a guessed scale is not a contract.

Multi-resolution joins respect actual availability and supplied calendars. A completed daily value cannot be attached to an earlier intraday cutoff merely because both have the same date. Current corporate-action-adjusted history may embed later knowledge; qualify the adjustment vintage or restrict/censor the affected window. Asynchronous overseas observations retain their age rather than being interpolated from an unavailable future close.

For storage intuition only, A×T×C counts cells; multiply by bytes per value and add masks/metadata to estimate tensor footprint. That is not the whole training-memory cost: optimizer state, activations and attention patterns matter. “Stack every feature” is poor design because it abandons hypothesis, units, coverage and resource ownership at precisely the point where they should become explicit.

# 7. Explicit Factors: The Disclosed Baseline

K_t = g(O_≤t) is explicit because g is specified. It need not be simple in every mathematical detail, but its inputs, formula, unit, time window, missingness rule and owner must be inspectable. A trend descriptor based on supplied moving-average distance has disclosed semantics. That does not make trend a causal explanation of tomorrow's price. Explicit means understandable construction, not infallible economic truth.

:::figure 07 Explicit-factor families and evidence ownership
| Family | Example eligible basis | Limit |
|---|---|---|
| Trend / momentum | Captured slopes, MA distances, RSI/MACD/returns | Do not rerun or retune frozen A2 |
| Breadth / sector tailwind | Dated constituent coverage and qualified relative evidence | No survivor-only historical universe |
| Volatility stress / risk context | Supplied realized measures and disclosed cross-market transforms | Not an expected move or universal regime truth |
| Derivatives pressure | Qualified OI, volume, IV, expiry/time basis | No invented intent or option POP |
| Narrative / macro | Attributed event summaries and available release vintages | Unknown sentiment and revisions remain explicit |
:::

Explicit factors remain valuable alongside deep learning because they anchor controls, expose data-quality failures and offer a low-capacity route to a forecast. They also let evaluation ask whether Z contributes information beyond what the disclosed factors already contain. A learned representation that merely repackages trend and sector exposure may be elegant compression without incremental predictive value. Conversely, an explicit factor can be redundant or unstable and should face its own ablation test.

A small fuzzy membership can express degree rather than a brittle binary label. For example, a versioned piecewise-linear curve could map a qualified volatility measure into a “stress membership” between zero and one. Such a number is a membership grade, not P(crash), predictive confidence or trust in the provider. The curve's thresholds are a declared experiment/policy choice, not values to optimize until a live symbol looks interesting. Raw-factor controls must remain available.

The design rejects an expanding expert-rule swamp: thousands of rules whose interactions cannot be independently tested or explained. It also rejects silent recalculation of A2 under new parameters. A proposed FM-owned factor can project existing captured facts; promoting a genuinely new factor into another layer requires separate versioned acceptance. No feature receives permanent protection simply because a human wrote its formula.

# 8. Latent Factors: Useful Compression, Not Hidden Truth

Z_t = E_φ(M_t, N_t, G_t) is a learned representation of an eligible input bundle. In the initial candidate, only the bounded numeric route and explicitly admitted context are relevant; narrative and graph encoders are later possibilities. A latent vector can compress correlated channels, represent nonlinear interactions or expose recurring structures that were not manually named. These are reasons to experiment, not guarantees that a useful hidden cause exists.

:::figure 08 Explicit and latent factors answer different questions
| Explicit K | Latent Z | Unified state X |
|---|---|---|
| Disclosed transform of known inputs | Coordinates learned under a pinned objective | Typed combination of eligible K/Z and quality |
| Human-readable formula semantics | Version-specific basis; meaning not automatic | Not a declaration of economic truth |
| Direct control and family ablation | Must prove incremental OOS contribution | Feeds a named forecast head or abstention |
:::

The word factor has several uses in finance and machine learning. A statistical latent coordinate, a priced economic risk factor and a deterministic technical feature are not synonyms. An autoencoder may devote capacity to a large source of variation with little relationship to the target. A representation can predict well while remaining economically opaque. Neither reconstruction quality nor a visually clean cluster certifies the coordinate as a causal driver.

Rotation illustrates the problem. If z is replaced by Rz for an orthogonal matrix R, its coordinate values change while pairwise distances can remain unchanged. A compatible downstream head may produce identical predictions after a corresponding transformation. Naming the first coordinate “momentum” would therefore be an unsupported attachment to an arbitrary basis. Changes across retraining can be more complicated than a rotation; dimensions and geometry may change too.

LFDE must report its encoder/basis identity, uncertainty method if any, input lineage, quality and validity. A deterministic encoder generally provides a vector, not a posterior distribution. If uncertainty is unestimated, say NOT_ESTIMATED. Seed dispersion is a useful diagnostic but not automatically a probability distribution over hidden economic truth. Later chapters distinguish representation stability, predictive contribution and optional economic interpretation because none implies the other two.

# 9. LFDE as a Governed Subsystem

LFDE has two different lifecycles. A separately authorized offline process learns an encoder artifact. A pinned inference component applies that artifact to a captured eligible input bundle. Training belongs to Governed Learning; inference belongs inside FM. Separating them prevents a forecast request from becoming an implicit retraining job and prevents a new candidate from replacing the active encoder midway through a run.

:::flow 09 LFDE responsibilities and acceptance boundary
QUALIFY INPUT → tensor schema, axis/mask identity, cutoff and admitted modalities
FIT OFFLINE, IF AUTHORIZED → objective, eligible windows, seed and bounded trial manifest
PIN ARTIFACT → family, dimension, weights checksum and latent-basis identity
ENCODE → captured input becomes an immutable latent snapshot
EVALUATE → contribution, uncertainty semantics, stability, redundancy and resources
RETAIN OR REJECT → a useful candidate still needs independent approval for future use
:::

A conceptual latent snapshot carries vector/subspace values, representation family, model/basis version, dimensions and precision. It links the tensor and any narrative/graph inputs; the exact scaler and preprocessing; training/selection cutoffs; source/data fingerprints; uncertainty type; coverage/OOD diagnostics; and issue/validity/scope. These are proposed design concepts, not newly exported classes in the present repository.

The consumer must reject an incompatible pairing of encoder and head. If a new encoder permutes coordinates, an old head cannot safely reuse them just because the length is unchanged. A missing required LFDE branch also cannot silently turn a K+Z model into a K-only model. A separately evaluated and COLD-bound K-only alternative can be selected under an explicit policy and recorded as a different composition. Otherwise absence or abstention is the honest output.

LFDE's responsibilities include rejecting its own representations. It supplies evidence for stability tests, grouped ablation and independent evaluation; it does not declare its own discoveries valuable. It does not fetch arbitrary data, invent uncertainty, assign economic names to coordinates or alter A2/A4/A5/A6. Optional ML libraries must remain behind provider-neutral ports. Recorded replay needs the captured snapshot/result and its decoding contract, not a functioning training stack or the latest model registry.

# 10. Classical Latent Controls

Classical controls ask whether the experiment needs nonlinear representation learning at all. With centered training observations arranged as a matrix D and d orthonormal loading directions W, PCA can be expressed as minimizing reconstruction error under WᵀW = I. It preserves a high-variance subspace, not necessarily a target-predictive one. Scaling changes the question, so channel units and fitted normalization are part of the control's identity.

= minimize_W ‖D − DWWᵀ‖²_F, subject to WᵀW = I

Probabilistic PCA specifies a latent Gaussian model rather than attaching a probability to ordinary PCA after the fact. In a simple form, v = Wz + μ + ε with z distributed N(0,I) and ε distributed N(0,σ²I). Posterior uncertainty is conditional on this model and its fitted parameters. It is not automatically calibrated uncertainty about tomorrow's binary outcome. The isotropic-noise assumption may be a poor approximation for mixed market channels.

:::figure 10 Classical models separate compression from evolution
| Control | Main question | Required caution |
|---|---|---|
| PCA | Can a small linear subspace replace a large channel set? | Variance explained is not forecast value |
| PPCA | Does an explicit linear probabilistic representation help? | Model covariance is not outcome calibration |
| Dynamic factor | Do shared factors and temporal evolution add value? | Fit/availability windows and loadings are pinned |
| Linear state-space | Can a simple transition/measurement model explain sequential observations? | Use filtering at cutoff, not future smoothing |
:::

A dynamic factor/state-space control can use z_(u+1) = Az_u + η_u and v_u = Cz_u + ε_u under explicit noise assumptions. Filtering estimates the current state from eligible history. Smoothing estimates an earlier state using later observations; it is useful for retrospective analysis but forbidden as a live-equivalent historical feature. A persistence or lagged linear prediction is another meaningful control before introducing complicated transition models.

The research lineage includes Stock–Watson factor forecasting, Tipping–Bishop PPCA and Kalman's filtering formulation; these establish relevant constructions, not TI-market superiority. Their assumptions and access limitations are cataloged in Chapter 34 and the research reconciliation. The roadmap requires PCA first and a selected probabilistic/dynamic control when its question is relevant, not an exhaustive classical-model tournament. Each control faces the same downstream target, population, calibration and resource accounting as a neural candidate.

# 11. One Masked Temporal Encoder

The initial nonlinear hypothesis is a small temporal patch Transformer with a masked-reconstruction objective. Historical numeric observations are grouped into temporal patches; selected observed values are hidden during training, and a decoder attempts reconstruction. The representation is then tested with a simple downstream forecast head. The encoder is not a chart-image classifier, and asset ordering does not become image geometry.

:::flow 11 Masked learning is an auxiliary task inside a chronological boundary
ELIGIBLE FIT WINDOW → qualified numeric channels and observation/padding masks
ARTIFICIAL MASK → hide selected observed training values only
ENCODER → temporal patch representation under a pinned architecture and seed
DECODER / LOSS → reconstruct hidden observed targets, not padding or unknowns
FREEZE ENCODER → fit and select the downstream head on eligible training history
CALIBRATE / TEST LATER → independent chronological data; evaluate K/Z/K+Z
:::

Let S be the set of deliberately hidden, genuinely observed training targets. A simple auxiliary loss is their mean squared reconstruction error, after a declared channel scaling. Its denominator is the number of valid selected targets, not all array cells. The exact objective may later differ, but its semantics must be pinned and independently reviewable.

= L_mask = (1 / number of valid targets in S) × Σ_(i in S) (m_i − m̂_i)²

If S is empty, the batch does not acquire a perfect loss of zero; its treatment needs an explicit training rule. Artificial masks and factual missingness cannot be conflated. Within a fully eligible historical window, bidirectional attention can use earlier and later positions **inside that window**. It may not read beyond the forecast row's cutoff. Pretraining on the final test period is future exposure even without labels.

Masked reconstruction can learn unhelpful variation. Consequently, low L_mask does not qualify an encoder. It must improve held-out forecast evidence beyond explicit/classical controls, with acceptable calibration, stability and cost. Ti-MAE and PatchTST motivate the proposed family; image MAE motivates a masking idea, not the use of screenshots. These are technique references, not adopted package defaults or reproduced TI results.

Mask ratio, patch length, latent dimension, channel transforms, regularization, seed list and trial cap are finite preregistered experiment choices. They are not user request parameters. The first experiment should answer one question well: does this bounded representation add useful information? Changing architecture repeatedly until a preferred live example looks attractive answers a different and scientifically weaker question.

# 12. Other Encoders and the Model-Zoo Trap

Many model families can consume sequential data. A plain autoencoder prioritizes reconstruction; a supervised autoencoder adds a target-related objective. Contrastive learning brings representations of selected views closer while separating other examples. Temporal CNNs use convolutional receptive fields. Transformers use learned attention, and selective state-space encoders use learned state updates that can offer different long-sequence resource profiles. None of these labels guarantees that its inductive assumptions fit this target or evidence population.

:::figure 12 Method choice is a gated hypothesis, not a shopping list
| Placement | Families | Admission question |
|---|---|---|
| Controls | Explicit logistic/base rate; PCA; selected PPCA/dynamic factor | What does the simple reproducible system already explain? |
| One initial nonlinear experiment | Small masked temporal patch encoder | Does Z improve matched OOS evidence? |
| Later alternatives | Plain/supervised AE, contrastive, TCN | What specific failure or resource hypothesis warrants another family? |
| Conditional later modalities | Narrative, graph, limited learned fusion | Does qualified information add stable value? |
| Deferred | Large Transformer, selective SSM, external pretrained checkpoints | Are benefits, provenance and compute justified? |
:::

Contrastive views require particular care. Cropping, time warping or sign reversal may preserve a generic signal-classification identity while changing the financial event being forecast. An augmentation must have an explicit justification for this experiment; there is no universal permission to transform price paths. Likewise, a Mamba-like selective neural SSM is not a Kalman filter with an automatically interpretable posterior covariance. Similar naming does not make uncertainty semantics interchangeable.

Multimodal design could eventually contain numerical, narrative, macro and derivatives encoders plus fusion. Initially, qualified macro/derivative summaries can remain explicit channels. Separate deep encoders must justify their additional parameters, data needs and missing-branch behavior. Graph embeddings similarly need dated edges before modeling sophistication becomes relevant.

External time-series and financial pretrained models are later comparators, not the definition of FM. Their exact checkpoint, training overlap, data/model rights, input semantics and compute requirements must be qualified. Unknown pretraining exposure undermines strong retrospective PIT claims. An independently authorized prospective comparison may be possible, but it cannot retroactively make historical benchmark contamination disappear. The best reason to choose a family is a falsifiable hypothesis and budget, not its prominence in current discussions.

# 13. Narrative and Market Intelligence

Prices do not contain a readable record of every available event, source disagreement or disclosure. A narrative representation can add a distinct information route, but it must not erase the provenance that makes the information admissible. Define N_t = E_news(Intelligence_≤t). Initially E_news is a bounded deterministic projection of admitted event summaries, not a new request to an LLM. Semantic embeddings are a later, separately governed possibility.

:::figure 13 Narrative joins numerical state without becoming raw tensor text
| Governed intelligence input | Separate N representation | Fusion boundary |
|---|---|---|
| Source IDs, event type, company/sector/global scope | Typed event/scope summaries | Keep original evidence references |
| Publication, availability, acquisition, cutoff | Age/validity and admitted version | No later article inserted into an old row |
| Supported direction/sentiment, uncertainty | Defined numeric/categorical meaning or UNKNOWN | Do not infer sentiment from a title alone |
| Novelty, dedup family, contradictory reports | Related-report structure and explicit conflict | Repeated reporting is not independent confirmation |
:::

Novelty is meaningful only relative to a specified eligible history and deduplication rule. Time decay is a modeling transform whose function and parameters must be versioned, not a statement that every event loses relevance at a universal rate. Source authority informs admission and qualification; it is not automatically a numerical probability weight. Conflicting admitted claims should survive as attributable alternatives, not disappear inside a mean sentiment score.

Later embeddings need text-access rights, retention policy, exact tokenizer/encoder/truncation versions and provenance from text to feature. They must also remain PIT-safe. An embedding made with a model trained on future evaluation information can compromise a historical claim even when the article itself predates the cutoff. An extraction model's uncertainty is different from uncertainty in the article's factual claim and from uncertainty in the forecast.

In an illustrative event-heavy cohort, narrative features might improve calibrated forecasts while adding nothing on routine sessions. That suggests a testable scope hypothesis, not immediate dynamic gating. The cohort definition must be available at decision time and qualified independently. A classifier trained after inspecting losses cannot retrospectively declare all successful rows “event-heavy.” The richer narrative path earns admission through held-out group ablation, coverage accounting and costs. If it cannot do so, explicit event summaries or no narrative branch remain valid choices.

# 14. Graphs and Dated Interdependencies

A graph describes relations, not necessarily causes. Write G_t = (V_t, E_t^explicit, E_t^learned). Nodes can represent stocks, sectors, indices, commodities, FX and macro variables. Explicit edges come from qualified dated evidence or disclosed estimators; learned edges are separate fitted parameters. Both need cutoffs and version identities. A static relation database downloaded today is not automatically a historical graph.

:::figure 14 Illustrative typed graph; every edge needs its own clock
| From → relation → to | Edge type | Required identity / caution |
|---|---|---|
| Equity A → belongs to → Sector S | Explicit membership | Effective dates plus known/available vintage |
| Supplier B → supplies → Equity A | Evidence-derived relation | Attributed dated claim; uncertainty retained |
| Equity A ↔ rolling correlation ↔ Index I | Estimated association | Return basis, overlap/window and estimator |
| FX F → fitted lead/lag → Sector S | Learned association | Past-only fit, search budget; no causal label |
| Event E → concerns → Equity A | Narrative relation | Event scope, dedup family and publication/admission clocks |
:::

Common-factor exposure is another relation, but its meaning depends on the exact factor basis and estimator. A correlation edge fitted over the full test interval exposes future covariance. A lead/lag graph searched over many pairs creates multiple-testing risk even if the downstream neural head is small. A learned adjacency matrix is therefore a model artifact, not background factual truth. Missing edge evidence must not silently become a zero-strength economic relationship.

The initial FM/LFDE experiment has no graph. A later study should first ask whether simple explicit sector or benchmark context explains the apparent benefit. A GNN must then beat comparable non-graph and simpler-relation controls under dated membership, matched populations, perturbation tests and resource gates. If the only gain comes from current sector labels applied retrospectively, the result is invalid rather than encouraging.

Graphs can also duplicate information already encoded in K or Z. A “minus sector” ablation that leaves sector edges and sector-trained embeddings intact does not remove sector information. Decide whether the question concerns one branch or the full information family, then cut the appropriate routes and refit affected transforms. Graph visual appeal has no special scientific status. A diagram full of connections can be a valuable hypothesis map while remaining a poor forecasting model.

# 15. Multi-Horizon State and Honest Disagreement

The symbols X_t^short, X_t^medium and X_t^long identify horizon-oriented state representations. They are not automatic aliases for the existing DAY and POSITIONAL request horizons. Each target declares the resolutions it consumes, its prediction window, label basis, calibration population and validity. The number of short bars available should not decide how much authority short-term information receives in a longer-horizon estimate.

:::figure 15 Illustrative disagreement across resolutions is preserved
| Supplied state descriptor | Possible horizon role | Correct interpretation |
|---|---|---|
| 5-minute bearish pullback | Short-context branch for an independently qualified short target | Does not cancel a longer trend by vote |
| Daily bullish structure | Medium/session context | Not automatically P(next session up) |
| Monthly strongly bullish descriptor | Long context, if qualified | “Strong” is descriptor intensity, not calibrated probability |
| Missing short bars / fresh daily data | Different branch validity | Long state may remain valid under its own policy; no fabricated short state |
:::

The table describes invented observations and proposed later scope. It does not claim supported intraday or monthly FM runtime. A multi-week forecast cannot be dominated by five-minute observations merely because thousands of them overwhelm a few daily tokens. Separate projections, branch capacity limits and resolution ablations provide a way to test this concern. A monthly descriptor should not silently be used to answer tomorrow's exact endpoint question without a qualified head.

Conflicts are often informative. A bullish longer state plus a short pullback can describe timing risk rather than a logical contradiction. A report should preserve target and state resolution instead of summarizing the bundle as “two bullish votes versus one bearish vote.” Incompatible horizons cannot be averaged into a single probability. An authorized consumer may interpret the separate claims, but the forecasting module cannot invent a trading rule to resolve them.

Staleness is also horizon-specific. An old narrative event, a late macro release and an incomplete intraday panel age differently. Effective forecast validity remains constrained by the earliest relevant input, model, calibrator, health and target limit. A still-valid long state does not rescue an expired short head. The simplest initial next-session model can use one bounded session-resolution bundle while the architecture leaves later multiresolution questions explicitly open.

# 16. State Estimation and Fusion

State estimation turns eligible observations into a useful current representation. It does not forecast merely by giving that representation a financial name. The initial X is a deterministic typed assembly of K, an admitted pinned Z where applicable, and Q. This preserves transparency and lets evaluation distinguish the information routes. The function F is versioned; its output's meaning depends on the schemas and artifacts it combines.

:::figure 16 Three fusion choices, three different claims
| Fusion choice | What is produced | What must be tested |
|---|---|---|
| Deterministic typed assembly | K/Z values plus separate quality/uncertainty envelope | Units, compatibility, missing branches and downstream contribution |
| Learned projection / gate | A fitted mixture or lower-dimensional state | Nested fitting, ablation, stability and calibration effects |
| Probabilistic measurement/state model | A conditional state distribution under explicit assumptions | Noise/model adequacy, filtering and uncertainty evaluation |
:::

Q includes quality, freshness, provenance and uncertainty metadata. Not every Q field should become a predictive feature. Availability masks and ages might have legitimate predictive use under an explicit allowlist and ablation, but future label disposition, operator acceptance or later corrections would expose information unavailable at issue. Source authority is an admission property, not a free numerical predictor of price direction.

A probabilistic state estimator could infer q(x_t given O_≤t) from a measurement model and a prior. Its covariance then has a defined conditional interpretation. The deterministic assembly cannot claim that same covariance without modeling it. Conversely, a probabilistic formulation does not eliminate misspecification: a sharply concentrated posterior under the wrong noise model can be misleadingly certain. Fit uncertainty, measurement ambiguity and future process uncertainty are different layers.

Missing branches require explicit behavior. If the bound model requires Z, its disappearance changes the function being evaluated. Substituting zeros or quietly averaging the remaining branches can produce an unvalidated model. A separately accepted K-only composition is a legitimate fallback only when the policy selects and records it as that model. Otherwise abstain or report absence. Interpretation must follow the actual composition, not the fuller composition that was hoped for.

Finally, state sufficiency is a hypothesis. If eligible residual history materially improves a head after conditioning on X, the chosen representation may be incomplete for that target. The remedy may be a better explicit feature, a different representation, or simply a direct-history control—not necessarily a deeper fusion network.

# 17. State Dynamics and Regimes

State dynamics asks how an estimated present state might evolve. It is different from estimating the present and different again from assigning a probability to a later endpoint event. A model p(x_(t+h) given x_t, O_≤t) can add useful structure, but it also adds assumptions, parameters and failure modes. Its scientific comparator is the same state with a direct outcome head, not a deliberately weak or incompatible baseline.

:::figure 17 Current-state filtering, future evolution and forbidden smoothing
| Question | Eligible computation | Not equivalent to |
|---|---|---|
| What state now? | Filter using observations available by t | Retrospectively smoothed state using later data |
| What state later? | Transition distribution conditional on current eligible information | Actual realized future state |
| What outcome later? | Head integrated over uncertain future state | Regime label alone |
| Is dynamics useful? | Paired test against same-state direct head | Attractive regime segmentation |
:::

A small linear state-space model provides a control with explicit transition and measurement assumptions. Persistence and lagged linear models can be even simpler. A bounded HMM introduces a discrete state S_t, transition probabilities and state-conditioned observation distributions. Its filtered regime probability uses evidence up to cutoff. A smoothed probability uses later observations and cannot enter the historical live-equivalent feature row. HMM state numbers also need version-specific interpretation; state 1 in a new fit need not mean state 1 in the old fit.

A regime can shift while an outcome forecast remains well calibrated. Suppose an illustrative model changes its conditional state mixture from quieter to more volatile conditions, while a separately tested head correctly accounts for that mixture. A change in state frequency is then not sufficient evidence of forecast failure. Input-distribution drift, representation instability and outcome calibration must be measured separately. The opposite is also possible: stable regime frequencies with a deteriorating head.

Temporal neural networks, Transformers and selective SSMs are later dynamics alternatives. They do not bypass the filtered-information rule or acquire Bayesian uncertainty by using the word state. A transition model that fails to improve proper loss, robustness or useful uncertainty should be removed. The direct-head bypass is a permanent scientific alternative, not temporary scaffolding that must eventually disappear.

# 18. Forecast Heads and Calibration

A head needs an exact question. The initial proposal preserves A7's qualified next-session endpoint event: y = 1 when the next supplied eligible session's close is strictly greater than the known reference session's close; otherwise y = 0. Ties are zero. Missing or ambiguous endpoints are unlabeled, not zero. The reference close is already known at issue and is not a hypothetical entry fill available then. This is underlying price-return direction, not total return, expected cash P&L or option probability of profit.

:::figure 18 Forecast heads are separate scientific contracts
| Head | Target / evaluation | Independent gate |
|---|---|---|
| Initial binary direction | Strict next-session endpoint event; Brier and log loss | Qualified schedule/basis, logistic/base-rate controls, held-out sigmoid calibration |
| Later return distribution | Named simple/log return, horizon and basis; proper distribution scores | Labels, support and distribution calibration |
| Later realized volatility | Sampling/window/overnight/annualization specified | Qualified path coverage and volatility controls |
| Later drawdown / path risk | Ordered path and censoring convention | Joint dynamics/path truth; endpoint bars alone insufficient |
:::

Calibration relates assigned probabilities to outcome frequencies in a specified population. A binary forecast of 0.70 is not wrong simply because one outcome is zero. Nor do many correctly classified observations establish calibration. For an illustrative cohort with identical p = 0.70 and an observed positive fraction 0.60, the mean Brier score is 0.60×0.30² + 0.40×0.70² = 0.25. Assigning 0.60 to that same fictional cohort gives 0.24. These are arithmetic teaching examples, not fitted results or a justification to calibrate on the test cohort.

= Brier = mean[(p_i − y_i)²]
= LogLoss = −mean[y_i log(p_i) + (1 − y_i) log(1 − p_i)]

A separate held-out calibrator is fitted after the raw head is frozen; final evaluation remains later and untouched. A sigmoid map might transform a raw score s to 1/(1+exp(−(a s+b))), with a and b fitted only on the calibration population. Endpoint clipping for numerical log loss is a pinned metric convention, not a hidden change to emitted probabilities. Reliability bins, support, class balance, uncertainty and coverage must accompany aggregate loss.

Unqualified schedules, corporate actions, unsupported scope, stale inputs, unhealthy calibration or exhausted budgets require explicit absence/abstention—not a neutral-looking 0.5. Initial validity ends within the separately pinned target/model/input constraints. Additional heads cannot borrow the initial binary calibrator or imply joint future paths simply because they share an encoder.

# 19. Uncertainty Beyond One Confidence Number

A factor is more than its estimate. Represent it conceptually as (estimate, uncertainty kind/value, freshness, quality, provenance). This tuple prevents source ambiguity, statistical variability, staleness and model confidence from being collapsed into one attractive percentage. It also makes unestimated uncertainty explicit. A deterministic formula can be perfectly reproducible while its inputs remain ambiguous or its predictive usefulness unknown.

:::figure 19 Uncertainty meanings cannot be exchanged or multiplied casually
| Layer | Legitimate meaning | Misleading substitute |
|---|---|---|
| Explicit K | Measurement ambiguity or qualified estimator uncertainty | “Formula is deterministic, therefore confidence is 100%” |
| Latent Z | Conditional posterior if modeled; seed dispersion labeled diagnostic | Calling every embedding a probability distribution |
| Regime | Probability under named transition/emission assumptions | Universal market-state truth |
| Narrative | Source, extraction and embedding uncertainties separated | Source prestige multiplied into forecast certainty |
| Forecast | Distribution plus calibration/support for an exact event | Guarantee of profit or future reliability after any shift |
:::

The familiar distinction between variability inherent in outcomes and uncertainty in estimated parameters is helpful but not a complete accounting system. A deterministic neural encoder may estimate neither. An ensemble of random seeds measures behavior under that chosen fitting procedure, not every possible model uncertainty. A PPCA covariance is conditional on its distributional assumptions. A simulated path's sampling error is separate from the uncertainty and misspecification of the dynamics used to generate it.

Freshness is an age/validity property. Quality summarizes admission, coverage and related evidence conditions. Provenance identifies origins and versions. Multiplying a freshness ratio, source score and head confidence produces no justified probability unless a separately specified and tested statistical model establishes such a meaning. The default is to keep the fields separate and use admission rules to determine whether a forecast can be offered.

Uncertainty itself must be evaluated. A confidence interval that repeatedly fails its stated population coverage, or a model that is overconfident under a shift, has not solved uncertainty by reporting it. Calibration evidence is finite and population-dependent. Missing support can legitimately lead to NOT_ESTIMATED or abstention. The handbook's examples use invented numbers to make these distinctions concrete; they do not set production uncertainty thresholds.

# 20. Does LFDE Add Anything?

LFDE's critical test is incremental contribution, not reconstruction skill. Compare K only, Z only and K+Z for the same target, eligible subject/date population, input vintages, chronological evaluation and declared head/search budget. Classical Z and learned Z should be reported separately. K+Z may show that a learned representation adds information beyond explicit factors; Z alone helps distinguish replacement/compression from complementary value.

= Δ_Z = mean_paired[L(P_hat_K, Y*) − L(P_hat_K+Z, Y*)]

Positive Δ_Z means lower paired loss, not causal discovery. The comparison must include calibration, regime robustness, seed/retraining sensitivity, redundancy, latent dimension, missingness and compute. A favorable mean can coexist with unacceptable calibration or unstable required cohorts. The smallest useful improvement and noninferiority margins must be chosen before inspecting the final results. An inconclusive uncertainty interval is not evidence of success.

:::chart 20 Illustrative K/Z/K+Z losses: usefulness is a paired question
incremental.png
:::

The plotted losses are invented summaries, not outputs from a trained model. They illustrate a possible complementary representation: K at 0.240, Z at 0.248, K+Z at 0.226. The arithmetic difference 0.014 alone does not establish acceptance. A real result also needs a qualified common cohort, session-aware uncertainty, adequate support, stable calibration and the preregistered resource and robustness gates. Other scenarios deliberately show no gain or a rejection.

Chronological fitting includes preprocessing, encoder training, graph construction, probes and selection. Calibration is separate and test data stay untouched. Correlated assets on one session do not supply independent temporal replications; confidence intervals must respect shared sessions and serial dependence. Label overlap requires an explicit purge/embargo strategy. Repeatedly inspecting the final holdout for model redesign spends that holdout.

Coverage is part of the result. A candidate cannot improve its score by silently dropping difficult rows. Report paired intersections and union exclusions with per-metric denominators, retaining failures and abstentions. Chapter 35 proposes a bounded comparison-manifest clarification/change for later review: persist the identity linking compared arms, protocol and eligible populations. That is a thesis finding, not an already adopted additional architecture contract.

# 21. Ablation That Actually Removes Information

Ablation asks what changes when a defined information family or model branch is removed. It is not just deleting one column from the final head. If sector information trained the numeric encoder, shaped graph edges and entered K, removing only K's sector field leaves several sector routes intact. The interpretation of the experiment depends on stating exactly which question is being asked.

:::figure 21 Leave-one-family-out must cut all relevant routes
| Arm | Routes removed for a total-family question | Required refit |
|---|---|---|
| Minus sector | K sector, sector inputs to Z, sector graph/context routes | Affected preprocessing/encoders/head/calibrator |
| Minus narrative | Summary and embedding routes, event-derived relations as declared | Affected transforms and downstream pipeline |
| Minus derivatives | Derivatives channels and dependent relations | Same chronological protocol |
| Minus latent temporal | Learned numeric Z branch | Remaining head/calibration |
| Minus graph / minus macro | All declared graph / macro routes respectively | No full-model fitted artifact carrying removed information |
:::

The full model contains only **currently admitted** groups, not all speculative future modalities. An unavailable graph is NOT_TESTED, not proven useless. A branch ablation can deliberately retain another route carrying similar information, but then the report must say it measures branch contribution rather than the family's total information. Interactions mean individual marginal gains cannot generally be added into a complete importance budget.

Retrained ablation refits every affected stage inside the same eligible fit windows with a bounded comparable trial budget. A frozen encoder trained with narrative inputs is not a valid “no narrative” representation merely because its final narrative vector is hidden. Inference-time occlusion instead studies robustness to removal at use time; it often creates an out-of-distribution input and is a different experiment. Both can be useful when labeled correctly.

Changing modalities may change which rows can be scored. Compare matched rows and show union coverage/reasons so apparent improvements do not come from selection. Report per-metric denominators: an abstained request may count toward coverage but supply no Brier value. Costs include acquisition/qualification burden, storage and fit/inference resources, not just parameter count. If a modality adds a tiny unstable gain at disproportionate cost, deferral is an honest outcome. The experiment should explain why the simpler system remains preferable rather than inventing a score that guarantees complexity wins.

# 22. Latent Stability, Alignment and Identifiability

Raw coordinates need not stay numerically equal across equivalent representations. A PCA sign flip or an orthogonal rotation can preserve important geometry while changing every coordinate name. For column vectors z′ = Rz with RᵀR = I, a linear head wᵀz is preserved by w′ = Rw. Reusing w unchanged generally is not safe. This is why encoder, latent basis and head must be bound together rather than matched only by vector length.

:::chart 22 Illustrative latent rotation preserves geometry, not coordinate names
rotation.png
:::

The four invented points are rotated together; pairwise distances are unchanged. The plot establishes only that arithmetic property. It does not demonstrate an economic factor, a stable learned model or predictive value. Real retraining can change geometry, rank and dimension, not just rotate a fixed representation. Coordinate-level drift and representation failure are therefore different hypotheses.

Orthogonal Procrustes alignment conceptually finds a rotation that best aligns two anchor representations: minimize ‖Z_A R − Z_B‖²_F subject to RᵀR = I, using an eligible training anchor set and a fixed row-vector convention. CCA compares correlated subspaces; principal angles and CKA provide other diagnostic views. Their invariances differ, and high dimensionality relative to sample size can make a similarity statistic misleading. No one metric is an automatic pass gate.

Use train-fitted alignment and held-out anchors. Compare seeds, successive fit windows, predefined regimes and cluster assignments after accounting for permissible relabeling. A linear or nonlinear probe that associates a representation with an explicit factor must itself be trained without the evaluation holdout. Probe accuracy is not a causal interpretation, and high subspace similarity does not prove the head forecasts well.

Historical snapshots retain their original basis and fingerprint. Alignment produces a separate diagnostic artifact; it must not rewrite old vectors to make a stability chart look smoother. An unstable candidate can be rejected even when one seed looks strong. Conversely, harmless rotation should not be mislabeled catastrophic economic drift. The scientific question is whether compatible representations and their predictions remain useful and robust under a predeclared diagnostic protocol.

# 23. From Latent Pattern to Explicit Factor

A stable latent association can motivate an economic hypothesis, but it does not arrive with a trustworthy name. The goal of optional promotion is to translate a reproducible pattern into a separately specified deterministic candidate factor, then test that factor independently. This may improve transparency, reduce compute or expose that the latent observation was merely redundant with an existing variable. Every outcome is useful if reported honestly.

:::flow 23 Optional latent-to-explicit promotion, with independent gates
STABLE PATTERN → survives eligible seeds/windows and predictive checks
PROBE / INTERPRET → document associations, uncertainty and alternative explanations
ECONOMIC HYPOTHESIS → say what mechanism might be relevant, without claiming causality
DETERMINISTIC CANDIDATE → exact formula, units, inputs, timing and missingness
INDEPENDENT PIT VALIDATION → new eligible data, controls, ablation and stability
EXPLICIT REVIEW → optional new K schema for future runs, or reject the hypothesis
:::

Suppose, purely illustratively, a stable subspace is associated with increasing participation during broad sector strength. Calling z_3 “institutional accumulation” would add an unsupported cause and tie meaning to an arbitrary axis. A safer hypothesis is a disclosed interaction between qualified participation and sector breadth. Define a formula, establish its available inputs, and compare it with the original K controls and K+Z candidate on independent evidence. The formula may fail or simply reproduce information already present.

Finding a hypothesis after looking at test outcomes means that test is no longer independent validation for the hypothesis. A new evaluation opportunity is necessary. Factor promotion also changes the feature schema, downstream model fit and possibly calibration; it cannot be slipped into the current composition as a harmless label. Approval is explicit, with old versions retained for replay.

An FM-owned new factor does not automatically become an A2 indicator or alter a frozen policy. Separate owner acceptance is required for changes outside FM. The optional loop therefore improves explainability only when its semantics and evidence survive scrutiny. Some useful representations may remain unnamed latent features. Others should be rejected. There is no requirement that every encoder coordinate eventually receive an economic story.

# 24. Governed Self-Correction and Diagnosis

Self-correction begins with an immutable forecast and a later qualified outcome, not with an instruction to make yesterday's answer look better. The outcome journal records what happened under the named label convention; evaluation examines proper loss, calibration, coverage and diagnostics. A correction proposal identifies a suspected weakness and a bounded test. Only a separately authorized offline job may generate new model artifacts. Training success is not activation authority.

:::flow 24 The correction loop has a permission boundary at every transition
FROZEN FORECAST → later qualified outcome / append-only revision if needed
EVALUATION → matched losses, calibration, coverage and uncertainty
DIAGNOSIS → suspected component, alternative explanations and support
PROPOSAL → bounded data / operations / resource grant required for candidate work
CANDIDATE → new fit / recalibrator / weights, never an edit to the old artifact
INDEPENDENT VALIDATION → untouched eligible evidence, then prospective shadow
EXPLICIT APPROVAL → new COLD binding for future runs; otherwise reject or hold
:::

“Forecast wrong” is not a sufficient diagnosis. An event assigned probability 0.70 can legitimately fail to occur. Repeated error can arise from poor calibration, an inadequate head, wrong dynamics, unstable latent features, explicit-factor errors, stale data, a provider/schema change, an unmodeled event, OOD scope or defective labels. Some causes cannot be distinguished with the available evidence. INCONCLUSIVE is preferable to an automatic causal story.

| Diagnosis family | Possible components | Evidence / corrective hypothesis |
|---|---|---|
| DATA_INTEGRITY | Missing/stale input, provider drift, label/data defect | Audit clocks, schema, versions and qualification first |
| STATE_REPRESENTATION | Explicit state, latent degradation, regime estimate | Factor/representation comparisons and support |
| DYNAMICS_OR_HEAD | Transition model or target head | Same-state direct-head comparison and residuals |
| CALIBRATION | Probability reliability deterioration | Mature held-out reliability/proper-score evidence |
| SCOPE_OR_EVENT | OOD population, unmodeled event | Applicability/event lineage; alternatives retained |
| INCONCLUSIVE | Insufficient or inseparable evidence | Hold the diagnosis; no invented cause |

These families are reporting categories, not a trained causal classifier. A report should name suspected components and supporting observations, distinguish evidence from hypotheses, and state uncertainty in the diagnosis. Recalibration cannot repair an ineligible data vintage or a mislabeled target. Retraining a larger encoder cannot cure a broker execution assumption that never belonged to FM in the first place.

:::figure 25 Fast, medium and slow describe change classes, not schedules
| Class | Candidate change | Unchanged governance |
|---|---|---|
| Fast | Calibration, uncertainty mapping, abstention thresholds | New version, validation/shadow and explicit COLD approval |
| Medium | Weights, regime routing, bounded ensemble composition | Compatibility and incremental-value tests, no HOT swap |
| Slow | Encoder/dimension/family or explicit-factor promotion | Full fit/data/basis/consumer review |
:::

Future authorized automation may detect drift, run bounded diagnostics, propose retraining and produce candidate models or promotion reports. It may not grant itself new data access, unlimited trials or production activation. An existing health policy can deny new inference immediately when its conditions are met; that is different from replacing weights. The conceptual speeds impose no hard calendar. A failed shadow candidate leaves the existing approved composition unchanged, or the system abstains under already accepted health rules. Historical records are untouched in either case.

# 25. Replay Without Rewriting Yesterday

Improvement should change future behavior, never historical recorded behavior. Replay therefore has three distinct meanings. Recorded replay decodes the captured result and verifies its integrity without running a model. Pinned recomputation applies the exact compatible implementation and artifacts to the captured inputs. Counterfactual reevaluation applies a different model as a new run explicitly linked to the original. Calling all three “replay” without qualification invites silent historical rewriting.

:::figure 26 Old and new model lineages never merge by overwrite
| Historical lineage | Separate future lineage | Invariant |
|---|---|---|
| Evidence E1 → tensor T1 → encoder Z1/basis B1 | New authorized fit → encoder Z2/basis B2 | Both identities retained |
| Fusion/dynamics/head/calibrator/policy pins → forecast F1 | Explicit approval → future COLD composition C2 | C2 does not replace F1's pins |
| Later outcome J1; revision J2 links to J1 | New evaluation can cite F1 and J2 | Original issued prediction remains F1 |
| Recorded replay returns F1 | Counterfactual run F2 has new identity | F2 is not what the old system said |
:::

The pin set includes FM and LFDE versions, weights and latent basis; tensor/channel/axis schemas; K transforms; narrative/graph versions; fusion, dynamics, head and calibrator; admission, health, target, label and resource policies; source/data/scaler/universe/calendar/action fingerprints; fit/split/seed/trial manifests; and numerical execution/serialization identity. A model file alone is not enough to explain a run.

Exact recorded replay must not need optional ML SDKs, live providers or the current model registry. A missing exact verifier yields explicit UNVERIFIABLE status for recomputation, not permission to substitute the latest compatible-looking model. Floating-point tolerance, if admitted for numerical verification, is predefined and reported. A tolerant recomputation result is not equality of captured serialized bytes or permission to change the old semantic fingerprint.

If future stochastic inference or Monte Carlo is admitted, persist sampled outputs and PRNG algorithm/seed/state as required for the chosen verifier. Sampling error, model uncertainty and environment nondeterminism remain separate. A new label correction can create a new evaluation version without changing the forecast that was originally issued. Similarly, a change in data-retention permission must be handled explicitly; unavailable archived inputs cannot be silently reacquired and represented as the original capture.

Replay is thus both a technical and scientific boundary. It lets a reviewer say exactly which information, versions, assumptions and authority were present then, even when a better model exists now. It does not prove that those assumptions were correct or that an uncaptured historical information set can be reconstructed exactly.

# 26. Monte Carlo, Ensembles and Mixture of Experts

Monte Carlo is a numerical integration/simulation technique, not an independent voter. Given a qualified joint process, it can approximate a path-dependent expectation by sampling paths and averaging a defined function of them. More samples reduce some sampling error under that process; they do not repair a misspecified process, missing dependence or unqualified input data. The future drawdown or barrier event must be defined before the simulation result has meaning.

= Estimated E[f(path)] = (1 / S) × Σ_(s=1…S) f(simulated_path_s)

The expression assumes a justified path distribution. Separately calibrated direction and volatility marginals do not specify one. Neither an endpoint probability nor an illustrative synthetic path supplies option POP, execution costs or barrier order. Monte Carlo stays deferred until dynamics and path evidence are scientifically qualified. Simulated observations must never be admitted as factual market evidence.

:::flow 27 Ensemble admission comes before combination
INDEPENDENT MEMBERS → each passes its own target/data/calibration/value gates
COMPATIBILITY → same target, horizon, cutoff eligibility, subject and price/label basis
SIMPLE COMBINATION CONTROL → average before learned weights or routing
GOVERNED FIT → valid historical out-of-fold predictions; no final-test weight fitting
COMBINED EVALUATION / CALIBRATION → cover missing-member and shift behavior
EXPLICIT FUTURE APPROVAL → new composition; no automatic voting or renormalization
:::

A probability average can be a useful control when members estimate the same event. Averaging an A2 score, fuzzy stress membership and event probability has no such interpretation. Even compatible members can share data and errors, so three agreeing models are not three independent pieces of evidence. A weighted ensemble, stacking model or regime-aware mixture-of-experts introduces additional fitted parameters and calibration needs.

Weights and routing belong to governed artifacts. They are not user preferences to change on a forecast request. Stacking must use appropriate out-of-fold predictions inside eligible training history, not predictions fitted to the same labels used to choose weights. Missing members cannot silently trigger untested weight renormalization. A regime-aware expert gate also needs a valid cutoff, stability evidence and clear failure behavior.

The initial design does not require ensembles. If individual models have not demonstrated contribution, their combination can multiply search opportunities without adding evidence. A direct simple forecast, an explicit absence or a rejected ensemble are all scientifically legitimate endpoints.

# 27. Configuration, Pluggability and Compute Budgets

Not every adjustable number should be user-facing. Architecture invariants define what no request can override: PIT eligibility, immutable replay, no execution authority, no initial RL/chart-image path and no autonomous promotion. Trusted COLD profiles bind approved behavior at startup. Experiment configuration defines finite research choices, while model artifacts preserve the selected learned parameters. A request selects only among admitted subjects, targets, horizons and captured inputs.

| Class | Examples | Owner |
|---|---|---|
| Invariant | Replay/PIT/authority boundaries | Architecture acceptance |
| COLD profile | Universe, channels, lookbacks, required branches, freshness/budget limits | Trusted startup owner |
| Experiment config | Masking ratio, seed/dimension trials, regularization, splits, ablation groups | Preregistered research owner |
| Model artifact | Encoder/dimension/weights, regime count, scaler/fusion/head/calibrator | Governed Learning output |
| Request parameter | Supported subject/target/horizon/cutoff/input refs | Scoped consumer; no loader paths or weights |
| Future adaptation | Proposal to alter thresholds, routing or model | New version and explicit COLD approval |

:::chart 28 Illustrative complexity trade-off, not a benchmark or budget default
cost.png
:::

The chart uses invented dimensions, latencies and loss gains to teach diminishing returns; none is a measured TI result. A smaller model's lower latency is not universal, and vector size alone does not determine compute. Actual studies must measure training and inference wall time, CPU/GPU use, memory, artifact/tensor size, failures and usage frequency. Monetary estimates require a defensible rate/context; unknown cost is UNKNOWN, not zero. Zero external model calls do not imply free local computation.

All material tunables participate in identity. A selected mask ratio, scalar transform, latent dimension, calibrator or abstention threshold changes the experiment/model/policy version. Future adaptive changes remain candidates until independently accepted. Runtime requests must not supply arbitrary model URLs, module paths or permission grants. Optional ML/provider dependencies stay isolated behind neutral ports so deterministic specialists and recorded replay remain usable without them.

Cost gates should be set before comparing held-out outcomes. A finite trial budget limits not only spending but also opportunistic selection. Exceeding it creates an incomplete/failed study, not an excuse to silently reduce required evidence or swap the bound model. Pluggability is controlled replacement with explicit compatibility, not unlimited interchangeability.

# 28. Scientific Failure and the Right to Stop

The strongest protection against an unfocused research laboratory is a protocol that can reject its own sophistication. A stage is not successful because code runs, reconstruction loss declines or a latent-space picture looks organized. The claim concerns qualified out-of-sample contribution under support, calibration, stability and cost constraints. If those constraints are not preregistered, an experiment can explore but cannot declare acceptance by choosing convenient thresholds afterward.

:::flow 29 Scientific failure gates preserve the simpler valid system
PIT OR LABEL FAILURE? → invalidate the comparison; repair qualification first
NO ROBUST INCREMENTAL VALUE? → reject or hold LFDE; retain explicit/classical controls
WORSE CALIBRATION OR REQUIRED-REGIME STABILITY? → deny broad acceptance
DISPROPORTIONATE COST / MISSINGNESS? → drop or defer the weak modality/model
FAILED INDEPENDENT TEST OR SHADOW? → reject promotion; never rewrite the old result
TRIAL BUDGET EXHAUSTED? → stop; no search until a preferred story appears
:::

The paired improvement must satisfy the study's smallest-useful-value criterion, with appropriate uncertainty. A confidence interval that spans negligible or harmful values does not establish usefulness. Conversely, lack of support should be called inconclusive rather than proof that all latent methods are useless. Failure classifications should distinguish invalid evidence, non-contribution, instability, excessive cost and insufficient evidence.

Calibration can worsen even when threshold accuracy improves. A graph can add a tiny favorable average while failing under dated edge availability or costing far more to qualify. A correction candidate can improve a retrospective test and still fail prospective shadow. Each is a reason to preserve the control or abstain, not to retune the protocol around the example. Removing difficult rows or weak regimes after the fact is not robustness.

> Sophistication has no entitlement to survive.

This principle does not mean permanent hostility to deep learning. It means that claims must scale with evidence. The same standard applies to hand-written factors and classical models. A small direct model can be the best supported outcome; a well-documented null result can prevent expensive repetition. No metric is designed to produce a desired number of attractive opportunities, and no claim of alpha follows from a good proper score. Operational usefulness remains a separate later evaluation under its own authority and execution assumptions.

# 29. Staged FM and LFDE Roadmaps

FM-0 through FM-6 are local research-stage labels, not accepted new A7.x milestone numbers. They describe gates and alternatives, not a compulsory seven-stage release. The first implementation, if separately accepted and authorized later, should prove the scientific control chain before adding representations. A useful K-only model can remain without LFDE; a useful Z can remain without dynamics; a useful single head can remain without graphs or ensembles.

:::figure 30 Conditional stages; progression can stop at every row
| Stage | Scientific question | Exit or stop |
|---|---|---|
| FM-0 Control | Are target/PIT/labels/calibration/journal/replay trustworthy? | Mechanics plus honest empirical control scorecard |
| FM-1 Explicit state | Which disclosed factors add information? | Qualified K and group ablations |
| FM-2 LFDE v1 | Does one bounded representation add value? | K/Z/K+Z, stability and cost; rejection allowed |
| FM-3 Dynamics | Does evolution modeling beat the same-state direct head? | Retain dynamics only if justified |
| FM-4 Heads | Does another exact target earn qualification? | One head/label/calibrator at a time |
| FM-5 Modalities / graph | Does richer qualified information help? | Retrained ablation or defer |
| FM-6 Ensemble / correction | Does governed combination/adaptation add value? | Independent members, tests, shadow and explicit approval |
:::

LFDE has a nested sequence: L0 qualifies the tensor and masks; L1 establishes classical controls; L2 studies one small masked encoder; L3 assesses stability and incremental value. Optional L4 considers a justified alternative/modality and L5 a latent-to-explicit hypothesis. Alternatives require a new bounded hypothesis and budget, not automatic expansion after a disappointing result. Classical dynamic controls can be shared with FM-3 rather than implemented twice for naming symmetry.

Before any empirical work, qualify rights, actual availability, corporate actions, calendars, dated populations and label maturity. Select finite channels/resolutions, fit and untouched test windows, seed/trial/dimension budgets, support/uncertainty criteria and resource ceilings before looking at held-out performance. Synthetic contract tests can prove mechanics but not historical knowability or forecast skill.

The dedicated architecture and roadmap remain drafts at this checkpoint. This handbook creates teaching material and classified findings only. It does not authorize FM-0, close a canonical deferral, train an encoder or publish a capability. If a later integration review keeps the bounded original A7 v1 before advanced FM/LFDE experiments, this roadmap permits that outcome rather than forcing a wholesale rewrite.

# 30. Future A7 Integration and Authority

FM fits conceptually inside A7 Forecasting, while evaluation and governed learning retain separate responsibilities. LFDE inference can be part of FM; LFDE training belongs to Governed Learning. This is a proposed seam, not a fourth authority or an autonomous model service. A7 has not been rewritten around FM/LFDE. Its prior thesis reconciliation remains completed history, while independent acceptance is paused for the intervening FM/LFDE work.

:::figure 31 The proposed A7 seam preserves three owners
| A7 responsibility | FM/LFDE placement | Cannot do |
|---|---|---|
| Forecasting | PIT inputs, K, pinned LFDE inference, state/fusion, optional dynamics, heads/calibration | Train on a request or override operational authority |
| Independent Evaluation | Outcome journal, population report, proper scores, ablation, stability/drift | Rewrite the forecast or approve its own candidate |
| Governed Learning | Bounded fits, correction proposals, registry and promotion evidence | Self-activate a production replacement |
| Trusted approval / COLD binding | Exact future composition and allowed use | Change historical records |
:::

FM-0 should reuse the A7 scientific-control infrastructure once it is independently accepted and implemented. Creating competing outcome journals, target definitions or registries would obscure lineage and duplicate governance. The existing A7 proposal's strict next-session cash-equity target and separate sigmoid calibration remain unchanged by this thesis. Any later alteration requires explicit reconciliation and acceptance, not interpretation of an illustrative diagram as permission.

A4 owns challenge/arbitration, A5 position intelligence and A6 bounded trade-expression candidate evaluation/selection. Forecast evidence may inform separately admitted future consumer policies, but no automatic overlay exists here. A probability cannot lift a deterministic restriction, manufacture an option candidate, set quantity or change a position action. TM owns risk, capital and action coordination; the broker supplies actual execution truth. Scanner intake and durable monitoring remain their separately governed integration/runtime concerns.

The present catalog remains nine facade operations. No FM/LFDE operation, remote API, recurring job or live provider path is added. Optional ML dependencies must not leak into deterministic contracts or specialists. The thesis's next step is reconciliation against the draft—not implementation, A7 acceptance, A8 or a tag. This separation lets architectural ambition be discussed thoroughly without misrepresenting what the repository can currently do.

# 31. Research Lineage and Paper Readiness

The framework combines established ideas: factor compression, probabilistic/state-space estimation, temporal representation learning, multimodal and relational finance, proper scoring, calibration and governed model lifecycle. That combination can be valuable engineering without constituting a new learning algorithm. The research reconciliation contains a 31-row comparison with evidence strengths and access limitations. This handbook explains those decisions; it does not reproduce the papers' experiments or certify transfer to TI's target population.

:::flow 32 The paper path requires more than a finished handbook
ARCHITECTURE DRAFT + THIS THESIS → explain concepts, assumptions and open findings
RECONCILIATION + INDEPENDENT REVIEW → stabilize claims, scope and interfaces
ADDITIONAL NOVELTY AUDIT → compare closest factor/multimodal/governance prior art
PAPER 1 CANDIDATE → conceptual manuscript, with proposal claims only
QUALIFIED IMPLEMENTATION / DATA / PREREGISTERED EXPERIMENTS → independent results
PAPER 2 CANDIDATE → empirical study, including null results, costs and limitations
:::

Paper 1's working title is **FM-LFDE: A Multimodal Market-State Forecasting Framework with Latent Factor Discovery and Governed Self-Correction**. A potentially distinctive contribution could be the concrete TI combination of typed information lineage, explicit/latent evaluation, authority separation and immutable replay. That is a hypothesis about positioning, not an established novelty claim. The authors would need to compare closely related financial factor models, multimodal/graph forecasting and evaluation/governance systems before claiming originality.

Unsafe claims include “first latent market-state system,” “causal hidden factor discovery,” “new foundation model” or “proven alpha.” StockNet, HIST and financial autoencoder work already supply close related ideas; numeric financial sequence models such as Kronos further caution against claiming tensor inputs are new. General forecasting benchmark success does not establish financial calibration, and a developer announcement is not independent replication. Some source reviews were abstract-level; that limitation carries forward.

Paper 2 needs qualified permitted data, dated universes/vintages, exact labels, preregistered chronological splits and trial budgets, controls, K/Z/K+Z and modality ablations, stability/calibration/coverage/cost reporting, reproducible artifacts and prospective shadow evidence. Null and failed results must remain visible. If the final result favors the simple model, that is the result the paper should report. Neither paper is written now, and finishing the thesis does not establish submission readiness.

# 32. Ten Worked Scenarios

Every case below is **ILLUSTRATIVE: invented data, model names, results, timings, intervals and approvals**. No model was trained and no symbol was live-validated for this handbook. Reported intervals are assumed fictional evaluation summaries, not intervals computed from an undisclosed dataset. Numerical values are not TI defaults. All cases preserve the exact target, source clocks, named owners and frozen lower-layer controls; potential future approval is an imagined governance outcome, not an action performed here.

## Case 1 — K is sufficient; LFDE adds nothing

**State:** an illustrative RELIANCE snapshot has supportive medium-horizon structure and ordinary volatility. **Explicit factors:** K contains qualified trend, momentum and participation projections, with all required inputs available at cutoff. **Latent contribution:** encoder L1 produces a valid pinned Z, but probes indicate that much of its variation is already associated with K. **Forecast:** a fictional K-only head issues 0.66 for the strict next-session endpoint event; K+Z issues 0.67. The small difference in one row is not evidence of usefulness.

**Evaluation:** on the same invented eligible cohort, K has Brier 0.225 and K+Z 0.226, so Δ_Z = −0.001. Assume the preregistered uncertainty and calibration gates do not support incremental gain. **Diagnosis:** the candidate representation is non-contributing under this tested protocol; this does not prove all latent methods are useless or that the encoder discovered no structure. Reconstruction success is irrelevant to the acceptance failure.

**Correction:** no automatic larger encoder or new masking search is launched. The evaluation report preserves the failed candidate and its cost; a future experiment needs a distinct hypothesis and bounded authorization. **Governance result:** reject this LFDE candidate, retain the separately qualified K-only model if its own gates passed, and keep A2/A4/A5/A6 outputs untouched. There is no obligation to retain Z merely because a subsystem was designed to produce it.

## Case 2 — Stable incremental evidence earns retention

**State:** an illustrative HDFCBANK panel shows mixed explicit momentum with varying participation/sector interaction. **Explicit factors:** K is a disclosed, qualified baseline. **Latent contribution:** L2 adds an interaction representation that remains useful after controlling for K and after seed/window checks. **Forecast:** on one invented row the K-only head gives 0.58 and K+Z gives 0.63 for exactly the same next-session event, cutoff and basis. Neither number authorizes action.

**Evaluation:** the invented comparison matches Figure 20: K Brier 0.240, Z alone 0.248 and K+Z 0.226. Assume an independently reported paired improvement interval of [0.006, 0.022], adequate preregistered session support, improved reliability and acceptable resource/required-regime limits. These are explicit scenario assumptions, not a statistical calculation from this book. Z alone performing worse illustrates complementarity rather than a reason to discard K.

**Diagnosis:** evidence supports retaining the combined representation within the tested scope, without assigning an economic cause to its coordinates. **Correction:** no correction is required merely because the representation is complex; register a promotion candidate with the complete comparison and fit lineage. **Governance result:** after a separately assumed successful shadow and explicit reviewer approval, a new COLD binding may admit future advisory runs. Historical forecasts and the K-only control remain available. A retained encoder is not proof of alpha or permission to expand to untested horizons.

## Case 3 — One good seed cannot rescue instability

**State:** an illustrative KAYNES sample has qualified but sparse changing participation conditions. **Explicit factors:** the same K definition and eligible population are used across trials. **Latent contribution:** L3 has an attractive result in one seed, but other preregistered seeds yield different subspaces and inconsistent downstream behavior. **Forecast:** one fitted candidate issues 0.74 on a row where another issues 0.51 under the same inputs; this spread is a fitting diagnostic, not calibrated posterior uncertainty.

**Evaluation:** invented paired improvements range from −0.006 to +0.015, and the assumed preregistered stability criterion fails. Train-fitted alignment removes harmless rotations, but the substantive predictive disagreement remains. **Diagnosis:** representation/retraining instability is supported; naming a coordinate “event sensitivity” would not explain or repair it. The cause might involve sample support, objective mismatch or capacity, so alternatives remain hypotheses.

**Correction:** record the failure. A bounded lower-dimensional or classical-control experiment could be proposed with independent evaluation, but no trial is run automatically and the favorable seed is not selected after inspecting the final test. **Governance result:** reject L3 for promotion or hold pending an independently justified study. Keep the existing qualified composition or abstain if none is admitted. Historical seed-specific artifacts are retained, not overwritten by the best-looking fit.

## Case 4 — Narrative helps only in a qualified event cohort

**State:** a fictional RELIANCE event snapshot combines ordinary numeric state with an admitted company disclosure. **Explicit factors:** K includes available technical/context measures; source authority, publication and acquisition clocks remain separate. **Latent contribution:** a later hypothetical narrative branch adds information during an event-heavy cohort defined before outcomes and available at decision time. **Forecast:** the event-conditioned K+Z+N head differs from K+Z for the same endpoint event; no sentiment is inferred from an unsupported headline.

**Evaluation:** assume retrained narrative ablation shows useful calibration/loss improvement in that preregistered event cohort, but no stable improvement on routine sessions. Union coverage reveals more missingness when narrative is required. **Diagnosis:** scope-conditional contribution is plausible; universal narrative superiority is not established. Repeated publishers sharing one source are not counted as independent confirming events.

**Correction:** propose a separately scoped policy/model or a simple explicit event-summary control for further validation. Do not invent a new live gate after inspecting errors, and do not silently activate dynamic routing. **Governance result:** broad promotion is declined; any event-scoped candidate needs its own independent tests, shadow and COLD approval. Missing narrative yields explicit absence or an independently bound simpler composition, never fabricated neutral sentiment. The evidence remains attributable even if a future semantic embedding is used.

## Case 5 — Graph complexity fails the cost-adjusted question

**State:** an illustrative qualified equity/sector panel already has broad relative context. **Explicit factors:** K includes dated sector membership and benchmark-relative facts. **Latent contribution:** a hypothetical graph G5 adds rolling relations, all fitted before cutoff and with explicit vintage provenance. **Forecast:** its probabilities closely resemble those of the non-graph K+Z model. The graph is rich visually, but visual density is not a predictive measure.

**Evaluation:** assume a correctly retrained minus-graph arm finds no robust useful loss or calibration gain. In this separate fictional study, inference latency rises from 8 ms to 25 ms and relation qualification adds storage/coverage burden. These numbers are invented and unrelated to any measured runtime. **Diagnosis:** the graph is non-contributing at its cost for the tested scope, not universally invalid as a research idea.

**Correction:** retain the simpler dated sector/context inputs and defer graph expansion. The team records whether other routes already explained the association; it does not preserve the GNN by redefining a smaller favorable population after the result. **Governance result:** no graph-model promotion. A future graph experiment requires a new information hypothesis and budget. If the graph had used undated modern relations historically, the disposition would instead be invalid evidence, a stronger failure than poor cost-adjusted gain.

## Case 6 — Short pullback and long strength coexist

**State:** an invented KAYNES bundle contains a 5-minute bearish pullback, daily bullish structure and a monthly strongly bullish descriptor. **Explicit factors:** each descriptor cites its own observation resolution and validity. **Latent contribution:** medium-state Z summarizes qualified session history; it is not allowed to average all three descriptors into a vote. **Forecast:** only the separately qualified next-session head emits a fictional probability, 0.57. The short and monthly descriptors do not become unsupported additional forecast probabilities.

**Evaluation:** compare the medium-head event with its later qualified label and evaluate repeated eligible cases under that head's calibration/population rules. A single down outcome does not prove the long descriptor false. **Diagnosis:** the apparent disagreement is primarily a horizon/state distinction; no model defect is established from the labels alone. If short inputs dominate a long-horizon candidate by token count, that is a separate resolution-ablation hypothesis.

**Correction:** preserve the distinct claims and their clocks; no consensus forcing or live weight change. **Governance result:** report the supported medium estimate and explicit unsupported/absent head scope elsewhere. A4/A5/A6 and TM retain their own responsibilities. Even a future long-horizon forecast would need its own target and calibrator before comparison. The purpose of multi-horizon architecture is truthful coexistence, not a stronger-looking composite direction.

## Case 7 — Regime shifts without calibration failure

**State:** an illustrative HMM's filtered probability of its internally named quiet state falls from 0.80 to 0.30 across eligible observations. **Explicit factors:** supplied volatility and participation changes support investigating a different state mixture. **Latent contribution:** the pinned representation remains compatible and stable on held-out anchors. **Forecast:** the same qualified head accounts for its model-conditional mixture and issues an invented next-session probability of 0.56; no smoothed future state was used.

**Evaluation:** assume the preregistered later evaluation window has adequate support and its reliability/proper scores remain within the approved bounds. **Diagnosis:** state-distribution change is detected, but outcome calibration failure is not established. A state label shift alone is not grounds to retune, and a stable calibration result does not prove the HMM states are true economic regimes.

**Correction:** continue bounded diagnostics and retain the existing binding under the assumed health policy. No new regime count or expert-routing model is activated. **Governance result:** no correction candidate is required by this evidence alone; retain the explanatory record and control comparison. If subsequent qualified outcomes demonstrate deterioration, a new proposal can be raised. The example separates input/state drift, representation stability and forecast reliability so one signal cannot masquerade as all three.

## Case 8 — Overconfidence produces a recalibration candidate

**State:** a fictional forecast service has accumulated matured qualified outcomes across its admitted population. **Explicit factors:** K's data-quality audit passes. **Latent contribution:** the encoder remains basis-compatible and its stability diagnostics do not show the same deterioration. **Forecast:** a predeclared probability cohort centered on 0.80 has an invented observed frequency near 0.60 over adequately supported evaluation data. The concern is repeated reliability, not a single missed prediction.

**Evaluation:** assume Brier/log-loss and reliability evidence meet the pinned diagnostic threshold for calibration deterioration. **Diagnosis:** CALIBRATION is supported as a candidate explanation, with label drift and scope changes still audited as alternatives. A recalibrator is not assumed to fix every cause simply because the probabilities look overconfident.

**Correction:** propose a new separately fitted calibrator using an eligible calibration window, then independent later validation and prospective shadow. No final-test outcomes are reused as the fitting set and then reported as independent success. **Governance result:** an existing approved health policy may suspend new qualified-probability admission, while deterministic controls remain available. The candidate recalibrator receives no automatic activation privilege because it is a “fast” change. Explicit review and a new COLD binding are necessary; old probabilities stay exactly as issued.

## Case 9 — Better backtest, failed shadow

**State:** a hypothetical candidate L9 is proposed after a diagnosed weakness. **Explicit factors:** the candidate preserves the qualified K definition and declared data scope. **Latent contribution:** a new encoder/head combination reports retrospective improvement on an independently defined test. **Forecast:** it begins an authorized prospective shadow, producing records without influencing A4/A5/A6 or TM actions. The accepted old composition remains separate.

**Evaluation:** assume the new candidate fails preregistered shadow calibration or coverage limits despite the earlier backtest gain. Its labels are admitted only after maturity; exclusions and failures are retained. **Diagnosis:** the discrepancy may reflect distribution change, selection risk or incomplete applicability. The record does not invent a causal explanation, and retrospective success cannot override the prospective failure.

**Correction:** reject the promotion proposal. A follow-up diagnosis can suggest a bounded future test, but changing thresholds to rescue this shadow would require a new protocol and independent evidence. **Governance result:** no new active binding; the old approved model continues only if its own health rules permit it, otherwise abstention. The rejected candidate, its forecast records and shadow scorecard remain immutable. The system has improved its knowledge by refusing an unsupported change, even though no new production model emerges.

## Case 10 — A better future model leaves history unchanged

**State:** an invented historical snapshot E10 was assessed under composition C1. **Explicit factors:** qualified K is pinned with encoder L1/basis B1, head H1 and calibrator CAl1. **Latent contribution:** the old vector and its uncertainty/quality fields are captured exactly. **Forecast:** record F10 contains the originally issued probability 0.62 for its precise target. Later qualified training produces L2/B2 and an explicitly approved future composition C2.

**Evaluation:** assume C2 improves future qualified evidence under its own protocol. A retrospective counterfactual application to E10 would issue 0.68, but it receives a new run identity and is labeled counterfactual. **Diagnosis:** there is no defect in F10 merely because a later model disagrees. Recorded replay must still return 0.62 and the original semantic fingerprint; a missing exact C1 verifier is UNVERIFIABLE for recomputation, not a reason to call C2.

**Correction:** none is applied to the historical forecast. Later label revisions append new outcome/evaluation versions without altering F10. **Governance result:** future requests may use C2 under its COLD approval; old requests remain explainable under C1. No provider call, model execution or current registry lookup is required for recorded replay. This is the central temporal promise: learning can improve tomorrow without falsifying what the system knew and said yesterday.

# 33. Frequently Asked Questions

These answers describe the proposed architecture, not implemented capability. Examples and model choices remain bounded by the draft and the final reconciliation findings. An answer that mentions future training, admission or promotion grants no permission to perform it.

## Q1. Why not put XGBoost or a neural network directly on OHLC?

That is a legitimate control, not a straw man. A direct model can win if the additional state decomposition contributes no useful information. FM/LFDE proposes explicit lineage, interpretable controls and a way to test representations and dynamics separately; it does not prove that a multi-stage neural architecture is superior. Any direct model still needs PIT data, exact targets, fit/calibration separation, coverage, costs and replay. Model simplicity does not exempt evidence qualification, while an elaborate state model does not deserve a weaker comparator.

## Q2. Why keep explicit factors when deep learning exists?

Disclosed factors provide a reproducible reference, help expose input-quality problems and make some model behavior easier to inspect. They also establish what a learned representation must add beyond known features. A deep encoder may simply reproduce trend, sector or volatility information already present in K. That can be useful compression without incremental forecast value. Explicit factors themselves are not sacred: redundant or unstable ones should face ablation and independent evaluation. The design preserves transparency without claiming that manual formulas contain all useful structure.

## Q3. What exactly is a latent factor?

Here it is a coordinate or subspace produced by a particular fitted representation model from an eligible input bundle. Its meaning depends on the encoder, training objective, data/scaler and basis version. It can capture shared variation or nonlinear interactions without having a human-assigned name. The word factor does not automatically mean a priced economic risk factor or a causal mechanism. A useful latent representation is one that passes independent predictive/calibration/stability/resource tests, not one that merely has a plausible interpretation after inspection.

## Q4. Is latent state the market's hidden economic truth?

No. Multiple latent representations can explain similar observations or produce similar forecasts. Coordinates can rotate or permute; model assumptions and training data influence the result. A sharply estimated latent state may still be misspecified. The system should describe model-conditional representations, not discovered omniscient truth. Economic interpretation requires separate probes, hypotheses and independent validation, and even a successful predictive probe does not establish causality. Some representations can remain useful without semantic names; others should be rejected despite a compelling story.

## Q5. Why are chart-image inputs excluded?

The selected architecture uses structured eligible observations with explicit units, ordering, masks and timestamps. A rendered screenshot adds choices about scaling, plotting style, resolution and annotations while making exact underlying values and missingness harder to audit. Excluding screenshots is a project boundary, not a claim that all visual finance research is invalid. The system can still use diagrams to teach its design and numeric plots to inspect results. Those teaching visuals are outputs for humans, never model inputs masquerading as canonical evidence.

## Q6. Why borrow CV-inspired methods for tensors?

An idea such as masking and reconstructing parts of an input can be useful beyond images. In FM/LFDE, it is applied to typed historical numerical patches rather than screenshots. Transfer the technique, not every image assumption: neighboring asset IDs are not neighboring pixels, and price-path transformations may change financial meaning. The proposed encoder must respect factual masks, cutoff boundaries and channel units. Reconstruction is only an auxiliary objective; downstream OOS contribution determines whether the representation deserves retention.

## Q7. What makes a Market Tensor different from a dataframe?

The distinction is contractual rather than mystical. A dataframe can hold much of the underlying information, but the tensor bundle explicitly pins model-facing asset, time and channel axes, transformations, masks, units and provenance. Two arrays of the same shape can mean different things if channel order or price basis changes. The bundle records those semantics so training and replay consume the same object. It need not flatten all sources into one giant array; separate resolutions and narrative/graph branches preserve meaningful differences.

## Q8. Why have multiple horizons?

Short pullbacks, session-scale trend and longer context can coexist. Their labels, applicable features, uncertainty and freshness differ. Separate state/head/calibration contracts prevent a monthly descriptor from becoming a next-session probability by assertion. Multi-horizon architecture is not majority voting and does not require all horizons initially. The first model can remain a single qualified next-session head. More resolutions are justified only when their scoped contribution is tested, and five-minute token abundance must not silently dominate a multi-week forecast.

## Q9. Why consider an HMM?

An HMM offers a bounded way to test whether discrete latent states and transitions help describe sequential behavior. It can be a useful dynamics control when there is a specific regime hypothesis. Its state probabilities are conditional on the fitted model, not verified economic regimes. Historical forecasting uses filtering, not smoothing with later evidence. State count, fit windows and compatibility must be pinned. If a direct head on the same state performs as well with fewer assumptions, the HMM has not earned inclusion.

## Q10. Why is RL excluded initially?

The immediate question is supervised/probabilistic forecasting from qualified evidence, not choosing actions in a reward environment. RL would introduce reward design, action permissions, execution assumptions, exploration and policy-change risks that are outside the accepted initial scope. A better forecast does not confer operational authority. Excluding RL keeps the experiment falsifiable under observable labels and proper scores while TM retains decisions. It does not settle whether a separately governed future project could study RL; this roadmap does not authorize that project.

## Q11. Why not vote across algorithms?

Algorithms can estimate different events, use different cutoffs and produce incompatible score meanings. Their outputs are not comparable ballots. Even calibrated probabilities for the same event may share errors because the models share inputs and training history. A later ensemble needs independently qualified compatible members, an explicit combination rule, valid fitting/calibration and contribution tests. Simple averaging is a control, not guaranteed improvement. A2 scores, fuzzy memberships and probabilities cannot be mixed into a vote and presented as a calibrated likelihood.

## Q12. Why is Monte Carlo not a voter?

Monte Carlo approximates a quantity under the process from which it samples. It contributes numerical integration, not independent evidence about whether that process is correct. More simulated paths can reduce sampling error while leaving model bias unchanged. Path-dependent claims also need qualified joint dynamics and path labels; separate direction and volatility marginals are insufficient. The design therefore defers Monte Carlo. Simulations, if later admitted, need pinned assumptions, PRNG/sample identity and clear separation between synthetic paths, factual observations and model uncertainty.

## Q13. How do we know LFDE helps?

Compare K, Z and K+Z on matched eligible rows under a preregistered chronological protocol. Evaluate paired proper loss, calibration, coverage, required regimes, seeds/retraining, latent stability, redundancy and resources. The improvement must satisfy a chosen usefulness criterion with suitable uncertainty and support; the criterion cannot be chosen after seeing the result. Reconstruction accuracy and clustering plots are insufficient. Union coverage must show rows excluded by a modality or failed fit. A candidate that improves averages by discarding hard cases has not demonstrated the intended contribution.

## Q14. What if latent space changes after retraining?

Some changes are harmless basis transformations; others reflect substantial representational instability. Compare subspaces and eligible anchors using declared diagnostics, with alignment fitted only on appropriate training anchors. Test the compatible encoder/head pair rather than raw coordinate names alone. A new basis requires a new identity and compatible downstream artifacts. Historical vectors are not rotated in place to match the new model. Diagnostic alignment is separate from recorded replay, and similarity never substitutes for held-out predictive/calibration evidence.

## Q15. Can a latent pattern become an explicit factor?

Yes, as an optional governed hypothesis process. A stable pattern can motivate a probe, an economic interpretation and a disclosed deterministic candidate formula. That formula then needs independent PIT validation, controls, ablation and explicit versioned approval. If it was invented after inspecting a test, that same test cannot provide independent confirmation. Promotion into FM's K schema does not authorize changing frozen A2. Some patterns remain unnamed; some hypotheses fail. Neither failure nor continuing opacity justifies fabricating an economic name.

## Q16. What does self-correcting mean here?

It means an auditable cycle from frozen forecasts and later qualified outcomes to diagnostics, correction proposals, authorized candidate work, independent evaluation, shadow and explicit future approval. Detection and candidate generation can eventually be automated within a bounded grant, but they do not authorize themselves. The system can reject a proposed correction. Old outputs, artifacts and policies remain available for replay. This kind of correction improves future behavior while preserving what was actually known and issued, rather than rewriting past errors away.

## Q17. Can FM rewrite itself live?

Not under this design. Request-time fitting, HOT weight replacement and autonomous production activation are excluded. A future authorized job may produce a new candidate artifact, but an explicit approval and new COLD binding are required for use. Fast recalibration is still a material change, not a loophole. An already accepted health policy may deny inference when its conditions are met; that is a governed admission response, not self-rewriting. No such model runtime or automation is implemented by this thesis.

## Q18. What if the correction is worse?

Independent validation or shadow should reject it, retaining the current qualified binding or abstaining under existing health policy. The rejection becomes useful evidence, with the candidate, protocol and failures preserved. An improved retrospective metric cannot override a failed prospective gate. Changing thresholds to rescue the candidate spends the independence of that evaluation and requires a new protocol/evidence opportunity. The learner does not get production control simply because it proposes an improvement; eligibility reporting and activation authority remain distinct.

## Q19. Why retain deterministic controls permanently?

They provide a replayable benchmark that makes incremental claims meaningful and supports valid behavior when forecasting is absent. Removing the control after a model appears promising makes later regressions harder to detect and encourages explanations based on the model's own changing outputs. A2/A4/A5/A6 are not probability estimators to be rescaled; their original semantics and fingerprints remain intact. A future forecast overlay needs separate consumer acceptance. Preserving controls does not claim they are optimal; it keeps comparisons and authority transparent.

## Q20. What if FM/LFDE never beats simple controls?

Then the research should report that result and stop unjustified complexity. It may still have produced useful data qualification, replay, evaluation and diagnostic infrastructure. A strong control or a well-supported decision to abstain is preferable to a complex unproven model. An inconclusive low-support study should not be generalized into a universal impossibility claim, but neither should it be called success. New experiments need a distinct hypothesis, independent evidence and a budget—not an entitlement to keep searching until a favorable example appears.

## Q21. How does replay work after model upgrades?

Recorded replay returns the captured historical output and verifies its identity without executing a model or consulting the latest registry. Pinned recomputation, if requested and supported, uses exactly compatible old inputs/artifacts under a declared numerical policy. A new model's assessment of old inputs is a separately identified counterfactual run. These operations must not be conflated. Missing old computation dependencies yield explicit unverifiability, not substitution. Later label revisions append new evaluation versions while the originally issued forecast remains unchanged.

## Q22. What differs from ordinary stock prediction?

The proposed emphasis is on typed information/state/forecast separation, explicit and latent contribution tests, distinct governance owners and immutable lineage across model changes. These are engineering and scientific commitments, not proof of a novel algorithm. Many existing systems and papers already address subsets or related combinations. A direct stock predictor can satisfy rigorous governance, and a market-state framework can fail it. The differentiator must eventually be demonstrated in reproducible interfaces and evidence, not inferred from the FM/LFDE name or an elaborate diagram.

## Q23. Is alpha guaranteed?

No. This thesis reports no trained-model performance or live market result. Proper-loss improvement concerns an exact predictive target; profitability additionally depends on entry, costs, execution, payoff, risk and authority conventions that may be outside that target. The initial endpoint probability is not option POP or expected monetary utility. Even a qualified forecast can lose relevance under shift. Scenarios are explicitly invented to teach acceptance and rejection. Any future empirical or investment-value claim needs independent evidence appropriate to that claim.

## Q24. How do news and Market Intelligence fit?

They enter a separate governed N representation, initially as attributed event summaries. Relevant attributes may include type, scope, supported direction/sentiment, novelty, age and uncertainty, each with source/version/cutoff lineage. Missing sentiment remains unknown; repeated reporting does not create independent confirmation. Later embeddings need rights, exact encoder/tokenizer identity and PIT qualification. Richer text features earn inclusion through retrained ablation and coverage/cost tests. Source authority affects admission, not an automatic multiplier that makes a forecast more certain.

## Q25. Why consider graphs at all?

Some relationships are easier to represent explicitly as dated connections: sector membership, supply chains, common exposure or event scope. A graph may help test how such context contributes beyond per-asset histories. That possibility does not establish that a GNN is needed or that learned edges are causal. Start with simple qualified sector/context controls; then test graph contribution under dated edges and full-route ablation. Undated modern relations cannot support strong historical PIT claims, and a visually rich graph can still be scientifically unhelpful.

## Q26. Why not use Transformers everywhere?

Attention provides a flexible sequence-modeling mechanism, but flexibility consumes sample support, compute and selection budget. Different tasks may be handled adequately by explicit transforms, linear factors or simple heads. A larger Transformer does not solve source ambiguity, missing calendars or calibration by itself. The initial neural experiment is deliberately one small masked temporal encoder. A new family or larger capacity needs a specific hypothesis, qualified data, fair controls and resource evidence. Efficiency or prominence in a benchmark is not market-specific predictive proof.

## Q27. What is the simplest useful implementation?

After separate acceptance and authorization, begin with the scientific-control chain: one exact target, qualified PIT features, simple logistic/base-rate models, held-out calibration, chronological evaluation, an immutable outcome/population record and replay. This corresponds conceptually to FM-0 reusing A7 infrastructure once delivered. No encoder, graph or dynamics layer is necessary to prove that chain. Empirical readiness still requires data/support gates; synthetic contract tests alone do not qualify forecasts. The simplest useful research outcome may be a trustworthy negative scorecard rather than a published model.

## Q28. How do we decide complexity is worth it?

Preregister the smallest useful improvement, calibration/robustness limits, support/uncertainty method and resource ceilings. Compare candidates on matched and union populations, retain failed trials, and measure fit/inference and evidence-qualification burden. A gain that vanishes across seeds, required regimes or correct PIT treatment is not worth accepting. Nor is a tiny uncertain gain automatically worth a large operational burden. There is no universal cost-adjusted scalar supplied here. The future scientific profile must make the trade-off explicit before held-out results tempt a convenient decision.

## Q29. How does this fit A7 now?

It does not rewrite A7 now. FM is a proposed inference subsystem within future Forecasting; Evaluation retains outcomes, calibration/ablation/stability diagnostics; Governed Learning owns candidate fits and promotion evidence, with explicit trusted approval. The existing A7 architecture/thesis reconciliation is preserved and acceptance is paused. This handbook's next step is FM/LFDE thesis/architecture reconciliation, followed by the separately governed integration/acceptance decisions. It adds no capability, model fit, A8 work or consumer authority. The distinction between conceptual placement and implemented behavior is deliberate.

# 34. Glossary, Reading Guide and Source Register

Read Chapters 1–6 for information and tensor semantics, 7–14 for representations and modalities, 15–23 for state/outcome/evaluation distinctions, and 24–31 for governance, replay and delivery. The worked cases and FAQ can be read independently, but their numerical examples should always be interpreted with the illustrative-data notice. Chapter 35 is the reconciliation handoff: classifications and proposals there have not been applied to architecture.

| Term | Meaning in this handbook |
|---|---|
| PIT / cutoff | Information eligible at the exact decision instant under a pinned policy |
| K / Z / X | Disclosed factors / learned representation / typed inferred state |
| Q / N / G | Quality-uncertainty-provenance envelope / narrative representation / dated relations |
| P_hat / Y / Y* | Forecast distribution / random target outcome / later qualified realization |
| Calibration | Probability reliability for a named population, assessed with finite evidence |
| OOS / shadow | Held-out evaluation / prospective non-influencing candidate records |
| COLD binding | Trusted explicit selection for future runs; no mid-run model replacement |
| Δ_Z | Paired loss reduction of K+Z relative to K, not causal attribution |
| Recorded replay | Read historical captured output without model/provider execution |

The four controlling repository sources are the [FM/LFDE architecture](../../TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md), [detailed roadmap](../../TIAF_FM_LFDE_DETAILED_ROADMAP.md), [research reconciliation](../../TIAF_FM_LFDE_RESEARCH_RECONCILIATION.md) and [decision record](../../TIAF_FM_LFDE_DECISION_RECORD.md). The thesis preserves their creation snapshot; the accompanying thesis record contains exact source hashes. The [A7 architecture](../../TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md), [source/provenance architecture](../../TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md), [pluggability architecture](../../TIAF_PLUGGABILITY_ARCHITECTURE.md) and [ecosystem architecture](../../TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md) provide inherited ownership context. Proposed design is not runtime acceptance.

## Primary research lineage

The following references identify established ideas behind the research comparison, not implemented dependencies or replicated TI experiments. Dates refer to the cited paper/version. The architecture research checkpoint was 2026-09-14. Its detailed access notes remain authoritative: Hamilton, financial-autoencoder and fuzzy-set coverage was limited to bibliographic/abstract or indexed primary excerpts where full text was unavailable; PPCA PDF extraction was degraded. No paper is represented as fully reviewed merely because its URL appears here.

- Stock and Watson (2002), [Forecasting Using Principal Components From a Large Number of Predictors](https://www.princeton.edu/~mwatson/papers/Stock_Watson_JASA_2002.pdf): classical factor-forecast control lineage.
- Tipping and Bishop (1999), [Probabilistic Principal Component Analysis](https://www.microsoft.com/en-us/research/publication/probabilistic-principal-component-analysis/): explicit probabilistic latent construction, not outcome calibration.
- Kalman (1960), [A New Approach to Linear Filtering and Prediction Problems](https://www.cs.cmu.edu/~./motionplanning/papers/sbp_papers/k/Kalman1960.pdf), and Hamilton (1989), [regime-switching article](https://www.jstor.org/stable/1912559): state/filter/regime lineage under assumptions.
- Gu, Kelly and Xiu (2021), [Autoencoder Asset Pricing Models](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3335536): nonlinear financial factor prior art; target transfer unproven.
- He et al. (2022), [Masked Autoencoders](https://openaccess.thecvf.com/content/CVPR2022/html/He_Masked_Autoencoders_Are_Scalable_Vision_Learners_CVPR_2022_paper.html); Li et al. (2023), [Ti-MAE](https://arxiv.org/html/2301.08871v1); Nie et al. (2023), [PatchTST](https://arxiv.org/html/2211.14730v2): masking and temporal-patch inspiration, not chart-image input.
- Yue et al. (2022), [TS2Vec](https://ojs.aaai.org/index.php/AAAI/article/view/20881); Bai, Kolter and Koltun (2018), [TCN comparison](https://arxiv.org/abs/1803.01271v2); Gu and Dao (2023, revised 2024), [Mamba](https://arxiv.org/abs/2312.00752v2): later alternative sequence/representation families.
- Zeng et al. (2023), [Are Transformers Effective for Time Series Forecasting?](https://arxiv.org/abs/2205.13504v3), and Lim et al. (2021), [Temporal Fusion Transformers](https://arxiv.org/abs/1912.09363v3): simple-control and multi-horizon comparison context.
- Xu and Cohen (2018), [StockNet](https://aclanthology.org/P18-1183/); Feng et al. (2019), [Temporal Relational Ranking](https://arxiv.org/pdf/1809.09441); Xu et al. (2021, revised 2022), [HIST](https://arxiv.org/abs/2110.13716): close multimodal/relational/hidden-concept financial prior art.
- Guo et al. (2017), [On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html); Gneiting and Raftery (2007), [Strictly Proper Scoring Rules](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf); Ovadia et al. (2019), [Uncertainty Under Dataset Shift](https://papers.neurips.cc/paper_files/paper/2019/hash/8558cb408c1d76621371888657d2eb1d-Abstract.html): scoring/calibration/shift distinctions.
- Gibbs and Candès (2021), [Adaptive Conformal Inference](https://arxiv.org/abs/2106.00170v3): later coverage-method reference, not initial automatic adaptation.
- Locatello et al. (2019), [Unsupervised Disentanglement Assumptions](https://proceedings.mlr.press/v97/locatello19a.html); Kornblith et al. (2019), [Representation Similarity](https://proceedings.mlr.press/v97/kornblith19a.html): identifiability and diagnostic cautions.
- Ansari et al. (2024), [Chronos](https://arxiv.org/abs/2403.07815v3); Das et al. (2024), [TimesFM](https://proceedings.mlr.press/v235/das24c.html); Ansari et al. (2025), [Chronos-2](https://arxiv.org/abs/2510.15821): pretrained time-series comparators, deferred pending exact checkpoint/data qualification.
- Shi et al. (2025), [Kronos](https://arxiv.org/html/2508.02739v1); Jain and Sen (2026-08-31), [TimesFM-3 developer announcement](https://www.research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/): numeric financial and newer multivariate prior art; preprint/developer reports are not independent TI validation.
- Bailey et al. (author version 2015), [Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf); Sculley et al. (2015), [Hidden Technical Debt](https://papers.neurips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html); Zadeh (1965), [Fuzzy Sets](https://doi.org/10.1016/S0019-9958%2865%2990241-X): selection/governance and membership context, not new TI policies.

These references support the conceptual lineage and the caution against premature novelty. They establish neither guaranteed financial skill nor acceptance of a particular library or architecture. Paper 1 needs a further focused novelty audit; Paper 2 needs independently reproducible empirical evidence. A reader should be able to separate every sourced construction, proposed engineering choice and invented numerical example.

# 35. Thesis Findings for FM/LFDE Architecture Reconciliation

The following **24 findings are a non-normative review handoff**, not accepted architecture amendments. Classifications are NO_CHANGE, CLARIFICATION_NEEDED, ARCHITECTURE_CHANGE_PROPOSED, IMPLEMENTATION_DETAIL_ONLY and DEFER. The four FM/LFDE primary sources remain unchanged. A6 remains frozen, A7 acceptance paused and FM/LFDE runtime NOT_IMPLEMENTED. The next pass must disposition each finding explicitly rather than treat this handbook as implementation authority.

## FF-01. Tensor dimensionality — CLARIFICATION_NEEDED

Clarify whether the first admissible tensor schema permits one target asset plus separate context or a bounded multi-asset panel, and how its axis manifest states that choice. The draft supports bounded representations but leaves concrete scope to the scientific profile. Reconciliation should distinguish this profile choice from a universally required A×T×C footprint; no all-market tensor is proposed.

## FF-02. Multi-resolution strategy — NO_CHANGE

Retain separate conceptual short/medium/long bundles and one minimal qualified initial resolution set. Longer-horizon contribution cannot be determined by short-token abundance. Exact lookbacks remain future profile choices, not thesis defaults. No need to require all resolutions or rename existing DAY/POSITIONAL semantics merely to match the conceptual state notation.

## FF-03. Missing-mask semantics — CLARIFICATION_NEEDED

Before implementation, specify the logical interaction of factual observation, structural padding/nonmembership and artificial training masks, including non-applicability and batches with no valid reconstruction targets. The truth table in Chapter 6 is explanatory, not a finalized encoding. Require an explicit empty-denominator treatment rather than letting a zero loss masquerade as successful learning.

## FF-04. Market Intelligence representation — NO_CHANGE

Keep separate N with deterministic admitted summaries first and governed embeddings later. Preserve unsupported sentiment as unknown, source-related duplication, contradictions and all availability/identity clocks. No raw-text dumping, new LLM acquisition or conversion of source authority into forecast certainty is justified by the thesis. Richer representations continue to require their own ablation and rights gates.

## FF-05. Latent dimension — IMPLEMENTATION_DETAIL_ONLY

Dimension values, finite candidate sets and selected architecture sizes belong in the future preregistered experiment/artifact profile, with compatible basis/head pins and compute ceilings. This handbook deliberately supplies no production values. A concrete engineering experiment can propose them later without converting the dimension into a public request parameter or changing the invariant architecture.

## FF-06. Initial encoder choice — NO_CHANGE

Retain one small masked temporal patch Transformer as the proposed first nonlinear experiment after classical controls. TCN/contrastive and other objectives remain separately justified alternatives. No evidence in this thesis warrants a larger family search, graph-first model, chart-image path or dependency purchase. Rejection of the initial candidate is a valid gate result.

## FF-07. PCA and dynamic-factor controls — CLARIFICATION_NEEDED

Clarify the minimal control obligations at each stage: PCA at LFDE entry, a selected probabilistic/dynamic control when that specific question is tested, and persistence/direct-head controls for dynamics. Avoid interpreting the family list as a requirement to run every classical variant. FM-2 and FM-3 should share qualified control implementations where appropriate rather than duplicate them.

## FF-08. Stability metric and anchors — CLARIFICATION_NEEDED

Require a declared diagnostic protocol identifying representation convention, rank/sample constraints, anchor membership/availability, alignment-fit partition and held-out evaluation anchors. CCA/CKA/principal angles and Procrustes have different invariances; the thesis does not choose a universal scalar threshold. Reconciliation should ensure harmless basis changes and substantive predictive instability are reported separately.

## FF-09. Uncertainty semantics — CLARIFICATION_NEEDED

Make machine-readable uncertainty kind and NOT_ESTIMATED behavior explicit in the eventual snapshot contract. Distinguish conditional posterior, estimator/sampling uncertainty, seed diagnostic, extraction ambiguity and forecast calibration. A deterministic X is not automatically probabilistic state. Clarify which Q-derived fields may be admitted as predictors and which are admission/reporting metadata only.

## FF-10. Graph scope — DEFER

Retain graphs beyond the initial numeric experiment. Dated node/edge identity, explicit versus learned relations, source qualification, simple sector controls, full-route ablation and resource limits are prerequisites. This handbook supplies no evidence that graph complexity is useful or that a modern relation snapshot is historically admissible. The attractive relational diagram is a hypothesis map, not acceptance evidence.

## FF-11. Multimodal learned fusion — DEFER

Retain deterministic summaries and typed assembly initially. Separate narrative/macro/derivative encoders and learned gating need independent modality value, missing-branch behavior, fit provenance and costs. The thesis does not justify stacking all modalities or assuming independence among repeated sources. Scope-conditional gains should motivate a new governed test, not immediate live routing.

## FF-12. State-fusion baseline — NO_CHANGE

Keep deterministic typed K/Z/Q fusion first and a separately qualified K-only control. Learned/Bayesian fusion is conditional later scope. A missing Z cannot silently mutate a K+Z model into K-only. Explicit selection of a separately evaluated composition, or absence, preserves both the model's meaning and its replay identity.

## FF-13. State-dynamics model — NO_CHANGE

Keep dynamics optional and compare it against the same-state direct head. Persistence/linear state-space precede a separately justified bounded regime or neural model. Filtering and future smoothing remain distinct, and actual future state never becomes an inference input. No Markov sufficiency, regime truth or mandatory HMM is established by the formal notation.

## FF-14. Calibration placement — NO_CHANGE

Retain separate held-out calibration after the raw head and before final independent evaluation. Initial binary target/sigmoid semantics remain unchanged. Different heads, horizons and future ensemble compositions need compatible calibration evidence; latent or state uncertainty does not substitute for it. The thesis's arithmetic examples do not authorize fitting on test outcomes.

## FF-15. Self-correction autonomy — NO_CHANGE

Retain bounded authorized diagnostics/candidate generation and explicit independent approval before any new COLD binding. Proposals grant no compute, data access or production activation. Health-policy denial is not model replacement. No runtime or scheduled learning is implemented, and the word fast introduces no HOT exception or permission to rewrite old artifacts.

## FF-16. Correction cadence — CLARIFICATION_NEEDED

Clarify that fast/medium/slow classify change depth and review burden, not elapsed-time commitments. Recalibration may be operationally small yet scientifically unsafe without support; encoder retraining may remain unnecessary despite a long interval. Exact schedules, if ever needed, belong to a separately governed runtime/job policy and must not be inferred from these conceptual categories.

## FF-17. Factor-promotion criteria — CLARIFICATION_NEEDED

Require the promotion report to preserve the probe-training boundary, economic hypothesis and alternatives, deterministic formula/input clocks, and independent validation opportunity after discovery. A test that inspired the factor is not independent evidence for it. Promotion affects a new FM K schema only unless another owner separately accepts a change; no frozen A2 edit follows automatically.

## FF-18. Replay pin set — CLARIFICATION_NEEDED

Clarify basis/head compatibility and diagnostic-alignment identity within the existing comprehensive pin requirement. Keep exact recorded replay, numerical pinned recomputation and counterfactual reevaluation visibly separate. Missing old implementations must never resolve through current-model substitution. A future tolerance or stochastic verifier policy needs its own explicit identity and cannot rewrite captured bytes.

## FF-19. Ensemble admission — DEFER

Retain independently qualified compatible members before any combination, static average before learned weights/routing, and explicit combined calibration/missing-member tests. Dynamic ensembles and MoE are not initial scope. The thesis supplies no empirical contribution evidence and no rationale for combining incompatible scores, memberships and probabilities as votes.

## FF-20. Tunability boundaries — NO_CHANGE

Keep architecture invariants, trusted COLD profiles, experiment configurations, model artifacts, scoped requests and future correction proposals distinct. Every material setting participates in identity. Consumer requests select supported behavior; they do not supply loader paths, authority, masking ratios or model weights. The narrative adds explanation, not a new configuration surface.

## FF-21. Compute and scientific gates — CLARIFICATION_NEEDED

Before empirical acceptance, require a finite resource/trial profile and a preregistered usefulness/noninferiority/support protocol, including which cost dimensions are actually measured. Monetary unknowns remain unknown. The illustrative latency chart is not a default. Clarify invalid versus inconclusive versus non-contributing results so budget exhaustion or sparse evidence cannot be reported as model success.

## FF-22. Paper 1 novelty readiness — DEFER

Retain conceptual manuscript readiness as a future review question. The potentially distinctive TI combination needs a focused closest-prior-art audit and stable reconciled architecture before an originality claim. No new learning algorithm, first-system claim or demonstrated superiority is established here. The thesis shares the working title but is not Paper 1.

## FF-23. Paper 2 prerequisites — NO_CHANGE

Retain qualified permitted PIT data, preregistered targets/splits/trials, reproducible controls and ablations, stability/calibration/coverage/cost reporting, untouched tests and prospective shadow. Failed and null results remain publishable evidence, not excluded inconveniences. No runtime, dataset qualification, experiment or paper is produced by the thesis, and none of those gates is closed.

## FF-24. Persisted paired-comparison identity — ARCHITECTURE_CHANGE_PROPOSED

Consider a small Evaluation-owned comparison-manifest concept linking the preregistered protocol, eligible common/union populations, K/Z/K+Z and ablation arm run IDs, per-arm fit budgets and metric denominators. The draft already requires most constituent evidence; the proposal is to make their comparison identity explicit and immutable. It must reuse existing journal/population-report seams, add no public API or scheduler, and be independently dispositioned rather than assumed adopted.

The findings total **9 NO_CHANGE, 9 CLARIFICATION_NEEDED, 1 ARCHITECTURE_CHANGE_PROPOSED, 1 IMPLEMENTATION_DETAIL_ONLY and 4 DEFER**. No finding is applied here. Exact next prompt: **TIAF FM-LFDE — THESIS / ARCHITECTURE RECONCILIATION PASS**.
