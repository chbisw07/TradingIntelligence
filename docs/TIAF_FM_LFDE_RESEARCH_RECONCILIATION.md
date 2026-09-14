# FM / LFDE — Research and Prior-Art Reconciliation

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

## 1. Conclusion and evidence standard

**ALIGNED_WITH_CONSTRAINTS.** Representation learning is a defensible experiment
inside TI's optional forecasting layer. It is not a reason to replace the
deterministic benchmark, bypass point-in-time (PIT) evidence admission, merge
prediction with trading authority, or establish an open-ended model laboratory.
The proposed smallest learning comparison is explicit factors, classical latent
controls and **one** masked temporal encoder, evaluated on one exact target.
This is an engineering recommendation inferred from the evidence below, not a
published result about TI.

Evidence strength is relative to the claim being made:

| Evidence label | What it supports | What it does not support |
|---|---|---|
| Foundational | A mathematical construction or result under stated assumptions | Those assumptions holding in TI markets |
| Peer-reviewed empirical | Results in the authors' specified tasks/data/protocol | Transfer to qualified Indian equities, calibration or business value |
| Preprint empirical | A testable method and author-reported experiments | Independent replication or accepted production suitability |
| Developer report | Current family capabilities described by its developers | Independent benchmark verification or superiority |
| Design inference | A proposed TI constraint derived from evidence and existing architecture | Measured incremental predictive value |

Primary papers, author manuscripts and official developer material support the
technical comparisons. There was no training, benchmark reproduction, model
download or dataset qualification. Abstract-only access is identified in the
source notes; numerical performance claims are deliberately not transferred into
TI acceptance thresholds. Unavailable full text is a limitation, not inferred
confirmation. “Adopt” below means adopt a **design principle/control obligation**,
not ship a model or dependency.

## 2. Prior-art decision matrix

| Research area | Representative method | Purpose | Evidence strength | FM/LFDE role | Principal risk | Disposition |
|---|---|---|---|---|---|---|
| Large-panel / dynamic factors | Stock–Watson principal-component forecasts [^1] | Compress correlated predictors before forecasting | Foundational plus macro empirical | PCA and dynamic-factor control family | Large variance need not be predictive; macro results do not establish daily equity value | Adopt controls |
| Probabilistic latent factors | Tipping–Bishop PPCA [^2] | Linear latent-variable likelihood | Foundational | Optional uncertainty-aware linear control | Conditional Gaussian covariance mistaken for calibrated outcome uncertainty | Experiment |
| State-space estimation | Kalman filtering [^3] | Sequential state estimate and error covariance | Foundational under model assumptions | Small linear filtering/dynamics control | Incorrect dynamics; retrospective smoothing leaking future evidence | Adopt control boundary |
| HMM / regime switching | Hamilton [^4] | Unobserved discrete state transitions | Foundational plus macro empirical; access limited | Optional FM-3 regime control | Overfit state count; arbitrary labels; current regime mistaken for future return | Experiment later |
| Financial latent factors | Gu–Kelly–Xiu autoencoder asset pricing [^5] | Nonlinear conditional factor structure | Peer-reviewed financial empirical; limited full-text access | Evidence that finance already has nonlinear factor models | Asset-pricing objective/population differs from TI endpoint probability | Experiment later |
| CV-inspired masking | He et al. MAE [^6] | Learn representations from masked input reconstruction | Peer-reviewed vision empirical | Transfer the masking idea only | Importing chart images or spatial assumptions into numeric assets | Adopt technique boundary; reject images |
| Masked time-series encoding | Ti-MAE [^7] | Reconstruct masked time-series values | Preprint empirical | One candidate pretraining objective | Reconstructing nuisance variation; training outside eligible dates | Experiment |
| Temporal self-supervision | TS2Vec [^8] | Learn timestamp/context representations | Peer-reviewed general time-series empirical | Contrastive alternative if the initial hypothesis fails for a stated reason | Augmentations remove market meaning; extra search opportunities | Defer initial implementation |
| Temporal CNN | Bai–Kolter–Koltun TCN [^9] | Sequence modeling with temporal convolutions | General sequence preprint empirical | Lower-complexity replacement candidate | Receptive-field assumptions; unsupported cross-asset locality | Experiment later, not a second initial arm |
| Temporal patch Transformer | PatchTST [^10] | Patch-based history representation and forecasting | Peer-reviewed general time-series empirical | Small numeric masked encoder template | More parameters/tokens than evidence; normalization/padding leakage | Experiment, one bounded family |
| Simple temporal controls | DLinear [^11] | Test whether a complex forecaster beats a simple model | Peer-reviewed benchmark challenge | Linear/lagged controls remain mandatory | Treating one benchmark result as a universal rejection of Transformers | Adopt comparison discipline |
| Selective neural SSM | Mamba [^12] | Efficient learned sequence processing | Sequence-model preprint empirical | Alternative if sequence cost is a demonstrated bottleneck | Efficiency mistaken for market skill or Bayesian filtering | Defer |
| Multi-horizon forecasting | Temporal Fusion Transformer [^13] | Mix static, past and genuinely known-future covariates | Peer-reviewed forecasting empirical | Later horizon-aware design reference | Realized future covariates disguised as known-future inputs | Experiment later |
| Multimodal finance | StockNet [^14] | Combine text and prices in a predictive latent model | Peer-reviewed financial empirical | Separate narrative channel, later fusion | Training-only posterior or future labels leaking into inference | Experiment later |
| Explicit market relations | Temporal Relational Ranking / RSR [^15] | Use inter-stock relations for ranking | Peer-reviewed financial empirical | Graph extension reference | Undated relation snapshots; ranking is not calibrated probability | Experiment later |
| Explicit plus learned relations | HIST [^16] | Use predefined and hidden concepts | Preprint financial empirical | Close prior art for known/latent fusion | Hidden concept renamed as an economic cause | Experiment later |
| Unified market-state representation | Factor/state-space/StockNet/HIST combination | Separate measured state, learned state and prediction | Design inference from established families | Typed K/Z/Q envelope before optional learned fusion | No single observable “true market state”; identifiability | Adopt separation; test usefulness |
| Probability calibration | Guo et al. [^17] | Correct predictive probability reliability | Peer-reviewed classification empirical | Separate held-out calibration and reliability evaluation | Post-hoc calibration treated as a guarantee under drift | Adopt principle, retain A7 sigmoid first |
| Probabilistic scoring | Gneiting–Raftery [^18] | Evaluate distributions with proper scoring rules | Foundational | Brier/log loss; later CRPS/quantile scores | Optimizing accuracy alone or equating score with P&L | Adopt |
| Uncertainty under shift | Ovadia et al. [^19] | Examine predictive uncertainty on shifted data | Peer-reviewed empirical | Calibration/shift stress tests and abstention | A single uncertainty scalar obscures failure types | Adopt tests |
| Adaptive coverage | Gibbs–Candès adaptive conformal inference [^20] | Adapt interval coverage under shift | Theoretical and empirical under specified guarantees | Possible later interval wrapper | Long-run coverage confused with per-case probability; automatic updates violate COLD scope | Defer |
| Latent identifiability | Locatello et al. [^21] | Examine unsupervised disentanglement assumptions | Theoretical and empirical | No unqualified coordinate semantics | Reading economic causes into arbitrary latent axes | Adopt caution |
| Representation stability | Kornblith et al. CKA [^22] | Compare learned representations | Peer-reviewed empirical/methodological | Subspace, anchor and probe diagnostics | Similarity mistaken for value; high-dimensional CCA artifacts | Adopt diagnostics, not proof of skill |
| Uncertainty-aware embeddings | PPCA / probabilistic StockNet [^2][^14] | Represent uncertainty conditional on an encoder/model | Foundational and task-specific empirical | Typed posterior uncertainty if actually modeled | Seed dispersion called posterior probability; inference uses training-only information | Experiment, semantics mandatory |
| Time-series foundation models | Chronos; original TimesFM [^23][^24] | Pretrained general forecasting | Preprint / peer-reviewed general empirical | Later external-model control, not an initial dependency | Pretraining overlap, model/data rights, uncontrolled revisions | Defer |
| Recent multivariate pretrained models | Chronos-2; TimesFM-3 [^25][^27] | Multivariate/covariate-informed zero-shot forecasts | Preprint / developer report | Revisit exact pinned versions later | Assuming all family versions have the same capabilities or audited PIT history | Defer |
| Financial pretrained models | Kronos [^26] | Model numeric OHLCV-like sequences | Financial preprint empirical | Important close prior art; optional later external comparator | Pretraining vintage/contamination; synthetic series confused with factual evidence | Defer |
| Gradational explicit concepts | Zadeh fuzzy membership [^29] | Represent degree of membership | Foundational; abstract access | Small optional versioned factor transform | Membership interpreted as event probability; expert-rule explosion | Experiment narrowly; reject rule swamp |
| Factor/modality ablation | Factor controls and model-specific ablations [^1][^10][^16] | Test incremental information | Design inference informed by empirical methods | First-class matched, retrained group ablation | Leakage, interaction effects or changed populations masquerade as contribution | Adopt protocol |
| Drift and governed retraining | Shift evidence plus ML-system debt [^19][^30] | Diagnose changed input/model behavior | Empirical and engineering evidence | Independent diagnostics and reviewed replacement | Feedback loops and silent configuration/model changes | Adopt governance; defer unattended activation |
| Multiple testing / selection | Bailey et al. backtest overfitting [^28] | Expose selection risk across many trials | Methodological/empirical | Trial ledger and untouched chronological tests | Repeatedly tuning to the same holdout | Adopt discipline; not a substitute for PIT splits |

No row demonstrates incremental TI forecasting value. References to experiments
are permissions to formulate future hypotheses, not present implementation scope.

## 3. Reconciled design choices

### 3.1 Controls before representations

Low-dimensional statistical factors already provide a principled alternative to
large feature stacks. The recommendation is a regularized explicit-feature
forecast, a PCA representation and, only where useful, a probabilistic/dynamic
linear variant. It is unnecessary to run every classical variant before asking
whether a nonlinear encoder adds anything. [^1][^2]

DLinear and PatchTST provide a useful methodological contrast: complexity can
lose to a simple baseline, and a revised architecture can improve on earlier
complex designs. Neither finding identifies the winner for TI. The experimental
unit must be the complete pinned pipeline, not an architecture label. [^10][^11]

### 3.2 One masked numeric encoder, not chart vision

The first nonlinear candidate is a **small temporal patch Transformer with a
masked-reconstruction objective**. This is a proposed TI experiment inspired by
time-series work, not a reproduction of an image MAE. Temporal patches operate
inside eligible historical windows; asset adjacency has no image-like spatial
meaning. Masks, observed-only losses, sample boundaries and training vintages
belong to the experiment contract. Reconstruction is an auxiliary training
objective; only held-out downstream comparisons can establish usefulness. [^6][^7][^10]

TS2Vec-style contrastive learning is a separate later alternative. Changing a
price path by time warping or sign inversion is not automatically a
label-preserving augmentation. A TCN can be a bounded replacement candidate;
Mamba-like selective SSMs are deferred until long-sequence resource pressure
justifies a new family. None becomes mandatory because it appears in a paper. [^8][^9][^12]

### 3.3 Multimodal and graph results are close prior art, not a novelty licence

Combining finance text with numerical prices, predefined with hidden concepts,
and stock relations with temporal representations all have direct prior art.
TI's proposed separation of explicit and latent state cannot honestly be called
the first such combination. [^5][^14][^15][^16]

An important implementation warning comes from StockNet's distinction between
a training inference network and its test-time generative path: a training
posterior may condition on the observed label, but that information cannot
become a live latent feature. Likewise, a relation listed in a modern knowledge
graph is not evidence it was available historically. These are TI admission
requirements, not allegations that those papers violated their own protocols. [^14][^15]

### 3.4 Calibration, uncertainty and interpretation remain separate

Proper scores, explicit calibration and tests under dataset shift have different
roles. Calibration fitted on one population is not a standing guarantee on
another. Adaptive interval coverage is also not interchangeable with calibrated
binary-event probability, and an adaptive update would still be a material
versioned change in TI. [^17][^18][^19][^20]

Unsupervised latent coordinates do not acquire economic names merely because
they look disentangled. Representation similarity can help diagnose retraining
stability but is not evidence of predictive gain or causality. Semantic probes
must themselves be fitted without the final test data and reported with their
limitations. [^21][^22]

### 3.5 “Foundation model” is not the meaning of FM

The original Chronos and TimesFM papers establish relevant pretrained
time-series prior art. Chronos-2 and the **2026-08-31 developer announcement** of
TimesFM-3 describe newer multivariate capabilities; it would be stale to label
both entire families as univariate-only. This does not certify their training
corpora, TI target semantics or live suitability. [^23][^24][^25][^27]

Kronos is especially relevant because it models numeric financial K-line
sequences. Numeric market tensors and financial pretraining therefore are not
novel in themselves. Before any external checkpoint is compared historically,
TI must qualify its training cutoff, possible evaluation overlap, licence,
artifact identity and input/output semantics. Unknown pretraining exposure
precludes a strong historical PIT claim; a separately labeled prospective
comparison may still be proposed. [^26]

## 4. Research limitations and unresolved tests

Evidence is strongest for established statistical constructions and the need
for honest evaluation; it is weaker for transporting benchmark gains into this
specific market, horizon and data environment. No accepted PIT training corpus,
sample-size analysis, hardware-cost measurement or empirical superiority is
established here. Financial studies use different objectives, universes and
measurement conventions; a stock ranking is not a next-session probability.

Remaining research before a publication novelty claim should include a deeper
comparison with financial representation/factor discovery, weak-signal and
nonlinear-factor identification work, dynamic probabilistic state models,
multimodal/relational finance, temporal leakage and evaluation-governance
systems. The author's current financial-methods bibliography itself lists
later nonlinear-factor and weak-factor work that warrants a targeted follow-up;
this pass does not claim to settle that literature. [^31]

## 5. Paper readiness and thesis handoff

**Paper 1:** the working title *FM-LFDE: A Multimodal Market-State Forecasting
Framework with Latent Factor Discovery and Governed Self-Correction* describes
a conceptual proposal. Architecture plus a dedicated thesis could support a
manuscript outline **after independent review and an additional novelty audit**.
Safe claims concern the proposed TI decomposition, explicit governance and
testable design requirements. Claims of a new learning algorithm, first
multimodal latent system, causal factor discovery or forecasting superiority
are unsupported. No paper is written or submission readiness certified here.

**Paper 2:** requires permitted qualified data; preregistered targets/splits and
minimum evidence; transparent trial budgets; frozen controls; reproducible
training/artifact manifests; K/Z/K+Z and modality ablations; uncertainty and
cost reporting; untouched tests and prospective shadow evidence. Null findings,
missingness, failed runs and discarded candidates must be reported. Backtest
selection risk is a reason for this discipline, not grounds to adopt another
search-heavy validation scheme in place of chronological evaluation. [^28]

The next artifact is a dedicated **FM-LFDE Market-State Forecasting Thesis**,
not an implementation or either paper. It should visually teach information
clocks, known versus learned factors, the tensor/masks, state versus dynamics,
uncertainty, ablation, identifiability, governed correction and immutable replay.
Use symbolic or explicitly illustrative examples, never fabricated measured
performance. The [roadmap](TIAF_FM_LFDE_DETAILED_ROADMAP.md) defines its gate.

## 6. Sources and access notes

Sources were checked on 2026-09-14. Dates below refer to the paper/version, not
search-engine crawl dates. Primary abstracts support only high-level comparisons;
no inaccessible article is represented as fully reviewed. Links identify the
original source or an author/institutional copy, not a search-results page.

[^1]: James H. Stock and Mark W. Watson (2002), *Forecasting Using Principal Components From a Large Number of Predictors*, JASA 97(460), 1167–1179. [Author PDF](https://www.princeton.edu/~mwatson/papers/Stock_Watson_JASA_2002.pdf). Full text accessible; introduction and factor-forecast construction inspected.
[^2]: Michael E. Tipping and Christopher M. Bishop (1999), *Probabilistic Principal Component Analysis*. [Author publication and abstract](https://www.microsoft.com/en-us/research/publication/probabilistic-principal-component-analysis/), [author PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/bishop-ppca-jrss.pdf). Abstract inspected; PDF text extraction is degraded. No numerical experiment transferred.
[^3]: Rudolf E. Kalman (1960), *A New Approach to Linear Filtering and Prediction Problems*. [Primary article, institutional copy](https://www.cs.cmu.edu/~./motionplanning/papers/sbp_papers/k/Kalman1960.pdf). Full text accessible; formulation/introduction inspected.
[^4]: James D. Hamilton (1989), *A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle*, Econometrica 57(2), 357–384. [Original article](https://www.jstor.org/stable/1912559). Bibliographic/abstract-level review; full-text retrieval was unsuccessful. Detailed reproduction and parameter choices are not assessed here.
[^5]: Shihao Gu, Bryan Kelly and Dacheng Xiu (2021), *Autoencoder Asset Pricing Models*, Journal of Econometrics 222, 429–450; earlier author manuscript dated 2019. [Author manuscript](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3335536), [publisher](https://www.sciencedirect.com/science/article/pii/S0304407620301998). Indexed primary abstract/excerpts and author publication metadata inspected; full-text retrieval unsuccessful.
[^6]: Kaiming He et al. (2022), *Masked Autoencoders Are Scalable Vision Learners*, CVPR. [Primary proceedings](https://openaccess.thecvf.com/content/CVPR2022/html/He_Masked_Autoencoders_Are_Scalable_Vision_Learners_CVPR_2022_paper.html). Abstract/method overview; vision evidence only.
[^7]: Zhe Li et al. (2023), *Ti-MAE: Self-Supervised Masked Time Series Autoencoders*, arXiv 2301.08871v1. [Primary manuscript](https://arxiv.org/html/2301.08871v1). Introduction and encoder/decoder method sections inspected; preprint.
[^8]: Zhihan Yue et al. (2022), *TS2Vec: Towards Universal Representation of Time Series*, AAAI. [Primary proceedings](https://ojs.aaai.org/index.php/AAAI/article/view/20881), [author manuscript](https://arxiv.org/pdf/2106.10466). Abstract/context and representation construction inspected.
[^9]: Shaojie Bai, J. Zico Kolter and Vladlen Koltun (2018), *An Empirical Evaluation of Generic Convolutional and Recurrent Networks for Sequence Modeling*, arXiv 1803.01271v2. [Primary manuscript](https://arxiv.org/abs/1803.01271v2). Abstract-level comparison; preprint.
[^10]: Yuqi Nie et al. (2023), *A Time Series is Worth 64 Words: Long-term Forecasting with Transformers*, ICLR; arXiv 2211.14730v2. [Primary manuscript](https://arxiv.org/html/2211.14730v2). Patching/channel construction, self-supervised transfer and ablation sections inspected.
[^11]: Ailing Zeng et al. (2023), *Are Transformers Effective for Time Series Forecasting?*, AAAI; arXiv 2205.13504v3. [Primary manuscript](https://arxiv.org/abs/2205.13504v3). Abstract-level benchmark comparison.
[^12]: Albert Gu and Tri Dao (2023, revised 2024), *Mamba: Linear-Time Sequence Modeling with Selective State Spaces*, arXiv 2312.00752v2. [Primary manuscript](https://arxiv.org/abs/2312.00752v2). Abstract-level architecture/task comparison.
[^13]: Bryan Lim et al. (2021 journal publication; preprint version 2020), *Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting*. [Primary manuscript, arXiv 1912.09363v3](https://arxiv.org/abs/1912.09363v3). Abstract and covariate-role overview.
[^14]: Yumo Xu and Shay B. Cohen (2018), *Stock Movement Prediction from Tweets and Historical Prices*, ACL. [Proceedings](https://aclanthology.org/P18-1183/), [paper](https://aclanthology.org/P18-1183.pdf). Introduction and training/inference sections inspected, including label-conditioned training versus inference prior.
[^15]: Fuli Feng et al. (2019), *Temporal Relational Ranking for Stock Prediction*, ACM TOIS. [Author manuscript, arXiv 1809.09441](https://arxiv.org/pdf/1809.09441), [author repository/publication metadata](https://github.com/fulifeng/Temporal_Relational_Stock_Ranking). Temporal relation model and relation-data appendix inspected.
[^16]: Wentao Xu et al. (2021, revised 2022), *HIST: A Graph-based Framework for Stock Trend Forecasting via Mining Concept-Oriented Shared Information*, arXiv 2110.13716. [Primary manuscript](https://arxiv.org/abs/2110.13716). Abstract-level comparison; preprint.
[^17]: Chuan Guo et al. (2017), *On Calibration of Modern Neural Networks*, ICML. [Primary proceedings](https://proceedings.mlr.press/v70/guo17a.html). Abstract/calibration method overview.
[^18]: Tilmann Gneiting and Adrian E. Raftery (2007), *Strictly Proper Scoring Rules, Prediction, and Estimation*, JASA. [Author PDF](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf). Primary introduction/scoring-rule scope inspected.
[^19]: Yaniv Ovadia et al. (2019), *Can You Trust Your Model's Uncertainty? Evaluating Predictive Uncertainty Under Dataset Shift*, NeurIPS. [Primary proceedings](https://papers.neurips.cc/paper_files/paper/2019/hash/8558cb408c1d76621371888657d2eb1d-Abstract.html). Abstract/shift-evaluation scope inspected.
[^20]: Isaac Gibbs and Emmanuel Candès (2021), *Adaptive Conformal Inference Under Distribution Shift*, arXiv 2106.00170v3. [Primary manuscript](https://arxiv.org/abs/2106.00170v3). Abstract/guarantee scope inspected; not a per-instance conditional calibration guarantee.
[^21]: Francesco Locatello et al. (2019), *Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations*, ICML. [Primary proceedings](https://proceedings.mlr.press/v97/locatello19a.html). Abstract, identifiability claim and experimental scope inspected.
[^22]: Simon Kornblith et al. (2019), *Similarity of Neural Network Representations Revisited*, ICML. [Primary proceedings](https://proceedings.mlr.press/v97/kornblith19a.html). CKA/CCA motivation and abstract-level diagnostic limitations.
[^23]: Abdul Fatir Ansari et al. (2024), *Chronos: Learning the Language of Time Series*, arXiv 2403.07815v3. [Primary manuscript](https://arxiv.org/abs/2403.07815v3). Abstract-level probabilistic pretraining comparison.
[^24]: Abhimanyu Das, Weihao Kong, Rajat Sen and Yichen Zhou (2024), *A Decoder-only Foundation Model for Time-series Forecasting*, ICML. [Primary proceedings](https://proceedings.mlr.press/v235/das24c.html). Original TimesFM abstract/method scope; not a specification of every later version.
[^25]: Abdul Fatir Ansari et al. (2025), *Chronos-2: From Univariate to Universal Forecasting*, arXiv 2510.15821. [Primary manuscript](https://arxiv.org/abs/2510.15821). Abstract-level multivariate/covariate capability comparison; preprint.
[^26]: Yu Shi et al. (2025), *Kronos: A Foundation Model for the Language of Financial Markets*, arXiv 2508.02739v1. [Primary manuscript](https://arxiv.org/html/2508.02739v1). Abstract, numeric K-line formulation and tokenizer/pretraining architecture inspected; author-reported performance not independently reproduced.
[^27]: Ayush Jain and Rajat Sen (2026-08-31), *TimesFM-3: A zero-shot foundation model for multivariate forecasting*. [Official Google Research announcement](https://www.research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/). Developer architecture/capability report, not independent replication; accessed 2026-09-14.
[^28]: David H. Bailey et al. (author version February 2015), *The Probability of Backtest Overfitting*. [Author PDF](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf). Introduction and selection-risk framing inspected; no adoption of its cross-validation scheme implied.
[^29]: Lotfi A. Zadeh (1965), *Fuzzy Sets*, Information and Control 8(3), 338–353. [Original publisher abstract](https://doi.org/10.1016/S0019-9958%2865%2990241-X). Indexed primary abstract inspected; full-text retrieval unsuccessful.
[^30]: D. Sculley et al. (2015), *Hidden Technical Debt in Machine Learning Systems*, NeurIPS. [Primary proceedings](https://papers.neurips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html). Abstract/system-risk framing inspected.
[^31]: Dacheng Xiu, [author research/publication index](https://dachxiu.chicagobooth.edu/), accessed 2026-09-14. Used for publication metadata and follow-up leads only, not as empirical evidence for unreviewed papers.
