# FM / LFDE — Architecture Decision and Reconciliation Record

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

The [bounded FF-0 implementation plan](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md) is complete
(**READY_FOR_FF0_IMPLEMENTATION**, planning only). It chooses synthetic captured-input
BaseRate mechanics, four FF-0 steps and a 28-case acceptance corpus. FF-0.1 is
next only under a separate implementation request; calibration stays at FF-2,
public capability publication stays separate, and runtime remains NOT_IMPLEMENTED.

Exact next prompt: **TIAF A7 / FF-0.1 — CONTRACTS, TARGET AND CLOCK FOUNDATION IMPLEMENTATION**.
Everything below is the preserved earlier record, including then-current status,
stage labels, findings and validation counts. Neither those historical labels
nor this navigation update authorize implementation, training, live work or A8.
No thesis DOCX/PDF, authoring assets or original finding disposition is rewritten.

## Current FF reconciliation addendum — 2026-09-14 (Asia/Kolkata)

FM/LFDE is **REPOSITIONED AS ADVANCED FORECASTER FAMILY** within the draft
[Forecasting Framework](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md), not abandoned
or reduced to a replacement for its internal factor/state research. The
[FF decision record](TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md) owns this
new decision and the 24 FM thesis finding dispositions. Shared ground truth,
paired comparison, composition and lifecycle belong to FF/A7-wide owners;
the revised family architecture and local roadmap retain scientific internals.

The FM/LFDE thesis is CREATED and unchanged. A **separate FF platform thesis**
is next: **TIAF FORECASTING FRAMEWORK — THESIS CREATION**. A6 remains FROZEN;
A7 ACCEPTANCE PAUSED; FF and FM/LFDE architecture DRAFT; RUNTIME NOT_IMPLEMENTED.
No independent architecture acceptance, runtime, training or paper readiness
is implied. **Sections 1–7 below preserve the earlier architecture-pass decision,
source audit and then-next wording as history, not the current work queue.**

## 1. Decision

**READY_FOR_FM_LFDE_THESIS**

Project alignment: **ALIGNED_WITH_CONSTRAINTS**.
Review date: **2026-09-14 (Asia/Kolkata)**.
This decision means readiness to create a dedicated explanatory thesis. It is
**not implementation readiness, independent architecture acceptance, model
approval, data qualification or evidence of predictive improvement**.

The research direction fits TI when it remains an optional, falsifiable
forecasting experiment under PIT, replay, uncertainty, cost and authority
constraints. It becomes scope drift if it turns into an unconstrained model
zoo, chart-image predictor, autonomous trader, continuous self-rewriter or a
replacement for deterministic A2/A4/A5/A6 controls.

## 2. Entry-state reconciliation and preserved authority

The initiating brief describes A7 thesis reconciliation as not yet run. The
actual workspace already contains the completed
[17-finding A7 thesis reconciliation](TIAF_A7_THESIS_ARCHITECTURE_RECONCILIATION.md).
The correct entry state is **A7 architecture RECONCILED; thesis RECONCILED;
independent acceptance pending; runtime NOT_IMPLEMENTED**. No completed work
was undone to match the older premise.

This is an **intervening FM/LFDE research-design pass before A7 acceptance**.
The current queue advances to the FM-LFDE thesis and then a later explicit
design/A7 integration review. The existing A7 architecture, roadmap, records,
DOCX/PDF and handbook sources remain unchanged. Their earlier “acceptance next”
wording is retained as a dated checkpoint; the
[forward queue](IMPLEMENTATION_ROADMAP.md#current-forward-sequence) owns the
current intervening work. A7 is not rewritten around FM/LFDE now.

HEAD and `tiaf-a6-baseline^{}` at entry both resolve to
`6dc2ff304aae0e87540260b092919bb91e4d4189`.
A5 remains `tiaf-a5-baseline` at
`167c51d40985e70e422df14af4a67531f8f66a65`.
The entry tree already had A7 documentation/thesis work; it was **not clean**.
Entry hashes were recorded before edits to distinguish this pass from that
pre-existing work. No runtime file, schema version, package version, capability
catalog, policy, model artifact or tag is changed. The current facade remains
nine operations; FM/LFDE introduces none.

Applicable inherited boundaries include the
[system architecture](TIAF_SYSTEM_ARCHITECTURE.md),
[source/provenance/contradiction architecture](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md),
[pluggability architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md),
[ecosystem architecture](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md),
[A7 reconciled proposal](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md)
and [deferral register](TIAF_DEFERRAL_REGISTER.md).

## 3. Deliverables and exact change scope

### Four new documents

| File | Purpose |
|---|---|
| [TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md](TIAF_FM_LFDE_MARKET_STATE_FORECASTING_ARCHITECTURE.md) | Proposed mathematics, tensor/contracts, state/heads, uncertainty, evaluation, correction, replay and ownership |
| [TIAF_FM_LFDE_DETAILED_ROADMAP.md](TIAF_FM_LFDE_DETAILED_ROADMAP.md) | Conditional FM-0–FM-6 and LFDE gates, failure corpus, existing deferrals and thesis handoff |
| [TIAF_FM_LFDE_RESEARCH_RECONCILIATION.md](TIAF_FM_LFDE_RESEARCH_RECONCILIATION.md) | Primary-source prior-art matrix, evidence strength/access limitations, design inferences and paper readiness |
| [TIAF_FM_LFDE_DECISION_RECORD.md](TIAF_FM_LFDE_DECISION_RECORD.md) | This status/source reconciliation, decisions, scope, validation and final report |

### Twelve navigation/status updates

- [README.md](../README.md)
- [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)
- [docs/MILESTONES.md](MILESTONES.md)
- [docs/README_TBD_DESIGN_NOTES.md](README_TBD_DESIGN_NOTES.md)
- [docs/TIAF_CAPABILITY_MAP.md](TIAF_CAPABILITY_MAP.md)
- [docs/TIAF_DEFERRAL_REGISTER.md](TIAF_DEFERRAL_REGISTER.md)
- [docs/TIAF_IMPLEMENTATION_TARGETS.md](TIAF_IMPLEMENTATION_TARGETS.md)
- [docs/TIAF_SYSTEM_ARCHITECTURE.md](TIAF_SYSTEM_ARCHITECTURE.md)
- [docs/TIAF_THESIS.md](TIAF_THESIS.md)
- [docs/TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md)
- [docs/TRADINGINTELLIGENCE_ROADMAP.md](TRADINGINTELLIGENCE_ROADMAP.md)

These updates correct active/next status and add navigation; they do not change
accepted layer responsibilities or the existing A7 target/slice design.
The already-dirty forecasting TBD idea note is **not edited by this pass**.
No generated thesis, chart asset, runtime, test, script, dependency or secret
file is changed. No full runtime suite is claimed from documentation checks.

## 4. Complete architecture report

The following is the 38-item report for this pass. “Proposed” applies throughout;
references to controls and experiments do not imply they have been implemented.

| Item | Decision / result | Detail |
|---|---|---|
| 1. Exact decision | READY_FOR_FM_LFDE_THESIS; not implementation readiness | §1 above |
| 2. Alignment | ALIGNED_WITH_CONSTRAINTS: bounded optional forecasting; controls/PIT/cost/authority preserved | Architecture §1 |
| 3. Files | Four new documents and twelve navigation/status updates; pre-existing A7 work preserved | §3 above |
| 4. Literature areas | Factors/state-space/HMM; SSL/masked/contrastive; CNN/Transformer/SSM; multimodal/graph finance; explicit+latent state; calibration/uncertainty/drift; ablation/stability; multi-horizon and pretrained time-series/financial models | Research §2 and sources |
| 5. Prior-art matrix | Adopt control/evaluation principles, experiment with one numeric masked encoder; later modalities/dynamics/ensembles; defer pretrained/large families; reject images and initial RL/self-activation | Research §2–3; no novelty claim |
| 6. Mathematics | Eligible O; explicit K; learned Z; typed X/Q; optional filtered-state/dynamics integration into a target head; observed Y* and proper loss; paired Delta_Z | Architecture §3; no realized future state at inference |
| 7. Market Tensor | Bounded multi-resolution A×T×C bundle; neutral ordered axes, three masks, actual-availability joins, train-only transforms, calendar/action/vintage fingerprints | Architecture §4 |
| 8. Explicit factors | Versioned trend, momentum, breadth, sector, volatility, risk context, derivatives, narrative and macro vocabulary; small qualified initial allowlist; optional bounded membership transforms | Architecture §5; no A2 recalc/retuning |
| 9. LFDE purpose / contract | Test useful unnamed representations; snapshot pins encoder/basis/vector, uncertainty kind, quality, fit/PIT/tensor lineage and validity | Architecture §6 |
| 10. LFDE families | PCA plus selected PPCA/dynamic control; one small masked temporal patch Transformer initially; other objectives/families alternatives, not a required model zoo | Architecture §6 family table |
| 11. Market Intelligence | Separate N branch: attributed event summaries first, governed embeddings later; timestamps, novelty/dedup, uncertainty and contradictions preserved | Architecture §7 |
| 12. Graph | Typed dated explicit edges separate from learned edges; no graph initially; full graph value must beat context controls in ablation | Architecture §8 |
| 13. Multi-horizon | Separate short/medium/long resolution/state/head/calibration/TTL; bounded cross-resolution context; disagreements retained | Architecture §9 |
| 14. State estimation | Deterministic typed K/Z/Q fusion first; later learned/Bayesian fusion only with stated assumptions and tests | Architecture §10 |
| 15. Dynamics | Optional persistence/linear state-space controls; bounded HMM later; compare with same-state direct head, never use future-smoothed state | Architecture §3/10 |
| 16. Heads | Initial A7 strict next-session endpoint price-return probability; later qualified volatility/return distributions one at a time; path targets deferred | Architecture §11 |
| 17. Monte Carlo | Deferred; samples validated joint dynamics later; not a voter, observed fact, POP generator or substitute for calibration | Architecture §12 |
| 18. Latent evaluation | Paired K/Z/K+Z OOS loss, calibration, stability, redundancy, dimensions, seeds and costs; no visual/reconstruction-only acceptance | Architecture §13 |
| 19. Ablation | Retrained full/minus-sector/narrative/derivatives/latent-temporal/graph/macro for admitted groups; all-route versus branch removal explicit; matched and union populations | Architecture §13 |
| 20. Identifiability | No economic meaning bound to z_3; rank/seed/retraining/subspace and train-fitted probe/CCA/CKA checks; no old-vector rotation | Architecture §14 |
| 21. Latent-to-explicit | Probe → economic hypothesis → deterministic candidate formula → independent PIT validation → optional reviewed new K schema | Architecture §14 |
| 22. Uncertainty-aware factors | Estimate, typed uncertainty, freshness, quality, provenance; posterior/seed diagnostic/regime/extraction meanings separated | Architecture §15 |
| 23. Self-correction | Journal → diagnostics → proposal → authorized candidate job → independent validation → shadow → explicit approval → future COLD binding | Architecture §16 |
| 24. Diagnosis | Six reason families with specific suspected-component codes; data, representation, dynamics/head, calibration, scope/event, inconclusive; hypotheses not causal verdicts | Architecture §16 |
| 25. Timescales | Fast calibration/thresholds, medium weights/routing, slow encoder/factor changes; all versioned/reviewed, no hard schedule or HOT exception | Architecture §16 |
| 26. Replay | Exact recorded replay without ML runtime; pinned recomputation separate; all model/data/transform/policy/composition identities retained; no current-model substitution | Architecture §17 |
| 27. Ensembles | Deferred initial scope; independent compatible members, simple average before weighted/stacked/MoE variants; weights/routing/calibration are governed artifacts | Architecture §12 |
| 28. Configuration | Invariants vs COLD profile vs artifact vs experiment vs request vs future proposal; every material value fingerprinted; requests cannot change loaders/weights | Architecture §18 |
| 29. Scientific failure | Reject complexity without robust incremental/calibration/stability/resource value; leakage invalidates results; failed shadow denies promotion; trial budget is finite | Architecture §19 |
| 30. FM roadmap | FM-0 control → FM-1 explicit → FM-2 latent → conditional FM-3 dynamics / FM-4 heads / FM-5 modalities / FM-6 ensemble/correction | Roadmap §2; not a mandatory seven-stage release |
| 31. LFDE roadmap | L0 tensor → L1 classical → L2 one SSL → L3 stability/value → optional L4 extension / L5 factor hypothesis | Roadmap §5 |
| 32. A7 seam | FM inference inside Forecasting; Evaluation owns outcomes/scorecards; Governed Learning owns fits/correction/registry/approval; no competing journal or A7 rewrite | Architecture §20 |
| 33. Paper 1 | Candidate conceptual manuscript only after dedicated thesis/design review and additional novelty audit; no novel algorithm/first-system/superiority claim | Research §5 |
| 34. Paper 2 | Qualified rights/PIT data, preregistered trial/split/metric protocol, controls/ablations/stability/costs, reproducible results and prospective shadow evidence | Research §5 |
| 35. Thesis | Dedicated illustrated FM-LFDE handbook recommended; explain unknowns, failures, ownership and future-versus-implemented status | Roadmap §11 |
| 36. Validation | Documentation/link/deferral/status and entry-preservation checks; no runtime tests/training/live validation | §5 below |
| 37. Residual risks | Data vintages, sample support, nonstationarity, latent utility/identity, missing modalities, resource cost, external checkpoint exposure/rights and unsettled empirical thresholds | §6 below |
| 38. Next prompt | TIAF FM-LFDE — MARKET-STATE FORECASTING THESIS CREATION | §7 below |

## 5. Validation record

| Check | Actual result |
|---|---|
| `git diff --check` | PASS; no whitespace errors |
| New-file whitespace checks | PASS for all four new Markdown files using `git diff --no-index --check /dev/null <file>`; not omitted merely because untracked |
| Existing local-link validator | PASS: **868 local links across 23 Markdown files**, including the pre-existing dirty A7 documentation/handbook |
| New-document structure | PASS: four documents checked for balanced fences, table widths, explicit NOT_IMPLEMENTED status and absence of internal search citation markers |
| Footnote references | PASS: all references resolve to unique definitions; 31 source entries in research and two methodological notes in architecture |
| Report/matrix completeness | PASS: 38 report items; 31 prior-art matrix rows; five Mermaid architecture diagrams (source/fences checked, not renderer-validated) |
| Deferral integrity | PASS: all **58 canonical register rows byte-for-byte unchanged** against entry snapshot; no ID/status reclassification or duplicate |
| Existing-file preservation | PASS: of 160 entry-hashed documentation files, only the twelve listed navigation/status files changed; **148 unchanged** |
| A7 preservation | PASS: all **16** A7 architecture/roadmap/records, DOCX/PDF, handbook/build/validation sources and chart assets match entry SHA-256 hashes |
| Runtime / tags | PASS: no `src`, `tests`, `scripts` or dependency changes; HEAD and A6 baseline hash unchanged; A5 tag still resolves to the recorded hash |
| Status consistency | PASS: active navigation says FM/LFDE thesis next, A7 reconciled/acceptance pending, both runtimes NOT_IMPLEMENTED; unchanged A7 documents retain their explicitly acknowledged earlier checkpoint |

The existing link check was invoked with the local virtual environment:

```bash
.venv/bin/python -B - <<'PY'
import importlib.util
spec = importlib.util.spec_from_file_location(
    "handbook_validation", "docs/handbooks/a7_forecasting/validate_handbook.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print(module.validate_links(True))
PY
git diff --check
```

Read-only Python checks compared entry/final SHA-256 maps and canonical DEF
rows, counted report/matrix entries, and checked new-document structure and
footnote references. The link validator checks local targets/anchors, **not
external URL availability**. Literature retrieval limitations are disclosed in
the research source notes. Mermaid rendering was not run; no new tool was
installed for this documentation pass.

No training, live provider/model/broker call, runtime suite, compile, lint or
type-check was run for this documentation-only scope. These are documentation
checks, not a runtime test count or scientific validation. External literature
browsing is research, not a live financial-provider or model inference call.

## 6. Residual risks and open decisions

| Risk / decision | Consequence / owner |
|---|---|
| No qualified empirical corpus established | Data owner must qualify rights, vintages, historical membership, corporate actions and schedules before any strong PIT/model claim |
| Low effective sample support / nonstationarity | Evaluation must preregister session-aware intervals, support/coverage and stability limits; no favorable-result tuning |
| Latent utility/identifiability unproven | LFDE can be rejected; keep simple controls. Probes and attractive plots do not identify causes |
| Richer modality/graph missingness and source uncertainty | Stage one qualified group at a time; preserve contradictions; NOT_TESTED distinct from failed value |
| Exact initial population / channels / lookbacks / latent dimension / trial budget undecided | Resolve in an explicitly authorized scientific profile before fitting; no silent defaults or request-level overrides |
| Cost and hardware not measured | Set finite budgets before work; report local resource measurements and monetary unknowns truthfully |
| Pretrained-model vintage/overlap/rights unknown | Deferred external checkpoints cannot establish historical PIT performance without qualification; prospective separately labeled studies may be considered |
| Source access / review depth limits | Some classical/financial sources were abstract-level or unavailable in full text; research notes disclose this. Further novelty review is required before a paper claim |
| Future A7 integration placement unresolved | Dedicated thesis/review precedes explicit integration reconciliation and independent acceptance; existing A7 v1 is not expanded now |

None prevents creating an explanatory thesis that states these limitations.
They **do** prevent claims of implementation/model/publication readiness.
No current empirical performance or timing/cost gain is reported.

## 7. Exact next step and preserved prohibitions

**TIAF FM-LFDE — MARKET-STATE FORECASTING THESIS CREATION**

Do not start implementation or either research paper from this decision.
No commit, tag or push is performed. No A6 semantic change, A7 rewrite, A8 work,
live provider/model/broker call, model training, image-input path or RL path is
introduced. The architecture is ready to explain and scrutinize, not ready to
claim superiority.
