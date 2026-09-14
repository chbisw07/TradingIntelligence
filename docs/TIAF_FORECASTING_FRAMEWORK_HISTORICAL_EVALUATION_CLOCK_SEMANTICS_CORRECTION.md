# Forecasting Framework — Historical Evaluation Clock Semantics Correction

## Current status — architecture accepted after repeat review

**FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTED** — 2026-09-14 (Asia/Kolkata).
The [independent repeat acceptance](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE_REPEAT.md)
closes FFA-B01: the five prior HOLD dimensions now have four ACCEPT and one
ACCEPT_WITH_CLARIFICATION verdicts. Current FF ARCHITECTURE ACCEPTED;
FF THESIS RECONCILED; FF IMPLEMENTATION NOT_STARTED / RUNTIME NOT_IMPLEMENTED;
A6 FROZEN; A7 ACCEPTANCE PAUSED; FM/LFDE preserved as an advanced forecaster family.
All four prior non-blocking follow-ups remain; no runtime or model is approved.

Exact next prompt: **TIAF A7 — FORECASTING FRAMEWORK INTEGRATION RECONCILIATION**.
Everything below retains its original review/correction/reconciliation checkpoint,
including old HOLD, correction-readiness, then-next wording, findings and validation
counts. This addendum does not rewrite the original verdicts, the 28 thesis
dispositions or any thesis artifact. No A7 rewrite, training, live call, commit,
tag or push is performed.

## 1. Decision and bounded scope

**READY_TO_REPEAT_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE**

2026-09-14 (Asia/Kolkata). The normative correction addresses FFA-B01; it does
**not** independently accept FF or claim implementation readiness. The original
acceptance's 26 ACCEPT, five ACCEPT_WITH_CLARIFICATION and five HOLD verdicts
remain an immutable historical review, with a current-status addendum. Repeat
acceptance must verify the correction and reassess the affected dimensions.

```text
A6 FROZEN at tiaf-a6-baseline
A7 ACCEPTANCE PAUSED
FF ARCHITECTURE CORRECTED AFTER HOLD
FF THESIS RECONCILED
FF ARCHITECTURE ACCEPTANCE MUST BE REPEATED
FF IMPLEMENTATION NOT_STARTED / RUNTIME NOT_IMPLEMENTED
FM/LFDE PRESERVED AS ADVANCED FORECASTER FAMILY
```

Only mode/clock, identity, eligibility, ledger/comparison, historical evaluation
and replay wording is corrected. No composition/operator redesign, new model
family, temporal service, runtime, training, live/model/provider/broker calls,
A7 rewrite, A8 work, frozen-A6 change, commit, tag or push.

## 2. Evidence and root cause

Source brief: supplied
`Codex_TIAF_Forecasting_Framework_Historical_Evaluation_Clock_Semantics_Correction.md`.

| Source | Why used |
|---|---|
| [Original acceptance](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE.md) §§3–5/7 | FFA-B01, five affected dimensions, counterexample and four non-blocking follow-ups |
| [FF architecture](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md) §§3/10–12/16/18/20 | Contract, initial-target, truth, comparison, optional LLM and replay seams corrected here |
| [FF roadmap](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) §§2–5/11 | Finite FF-0–FF-2 mechanics and explicit future tests; no new stage |
| [FF decision](TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md), [28-finding reconciliation](TIAF_FORECASTING_FRAMEWORK_THESIS_ARCHITECTURE_RECONCILIATION.md), [thesis record](TIAF_FORECASTING_FRAMEWORK_THESIS_RECORD.md) | Preserve original findings/artifacts and distinguish correction from repeat acceptance |
| [A7 architecture](TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md) §§5–7 | Existing actual-versus-simulated cutoffs, all-dependency PIT, walk-forward and outcome facets; unchanged |
| [Source/Provenance](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md) §§9/14 | Event versus knowledge/acquisition time; later projections are not original history; capture/verifier limits |
| [A2.10 replay](TIAF_A2_10_REPLAY_VALIDATION_EVALUATION.md) “Offline replay” | New replay processing time cannot alter original decision-time meaning |

FFA-B01 arose because FF §§3.1/10 required actual issue before target open
without a realization-mode distinction, while FF-1/FF-2 promised later historical
evaluation and new counterfactual requests. A7 already separated simulated
knowledge cutoffs from actual later computation. Applying FF's unscoped rule to
a new retrospective artifact either rejected legitimate research or encouraged
false backdating. Recorded reconstruction and pinned verification did not have
that same gap; their verification-time separation is retained and clarified.

## 3. Normative resolution and clock model

The single normative nine-clock table and mode inequalities are in
[FF §3.2](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#32-realization-modes-and-canonical-clocks-ffa-b01-correction).
It distinguishes observed events, exact-version availability, information cutoff,
simulated as-of, actual issuance, real computation, target open/resolution and
later outcome recording. Source acquisition/admission, model fit completion and
label availability remain in their existing owning records, never discarded.

- **ACTUAL_ISSUANCE:** genuine production and publication; real `computed_at`
  precedes or equals real `issued_at`, which must precede target open. Input and
  learned/selection knowledge are cutoff-bounded. Only this mode can provide
  genuine operational/prospective issuance history, subject to all other gates.
- **SIMULATED_ISSUANCE:** historical decision/cutoff precede target open;
  `computed_at` is the real later computation, even after resolution. `issued_at`
  is absent/NOT_APPLICABLE, never copied from historical `simulation_as_of`.
  The request's existing `as_of` carries simulation-as-of meaning, avoiding two
  competing as-of fields. Pin the simulation profile/version and experiment.

The anti-backdating invariant is normative in §3.2: a forecast cannot claim
issuance before actual production. Historical simulation is visibly later
computation, not evidence that the model was deployed or issued that forecast then.
`computed_at` means production/completion, not the earlier start of a long job.

**Boundary choice:** preserve strict `< target_open_time` for the initial target,
including rejection at exact equality. This satisfies the brief's `<=` necessary
bound without weakening its preferred “precedes” rule or the existing target.
Source close must be completed/available at cutoff; coarse/unknown timestamps
cannot manufacture proof of strict ordering. All instants remain aware and
normalized with `zoneinfo.ZoneInfo("Asia/Kolkata")`; JSON retains `+05:30`.

## 4. Identity, eligibility and common evaluation

[FF §3.3](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#33-result-identity-admission-and-evaluation-eligibility)
binds declared mode/context to the request and actual completion/issuance facts
to the result. Result fingerprints preserve mode, applicable clocks, target
boundaries, schedule, evidence/data, producing graph/artifacts and simulation
profile lineage. Requests cannot fabricate future processing timestamps. A
non-executed node has no invented completion, and a failed attempt is not issuance.

Forecast generation needs qualified target, PIT evidence/dependencies, clocks
and scoped authority. Supervised evaluation **additionally** needs a valid
qualified outcome, exact label revision and admitted comparison protocol. This
two-stage distinction prevents the future target outcome becoming a forecast-time
requirement. Missing/censored outcomes mean no eligible supervised score, not a
fabricated negative label or deletion of the forecast.

[FF §11](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#11-forecast-ledger-without-mutable-historical-cells)
preserves one actual and many simulated artifacts against one shared market
observation/outcome. Mode and run identity distinguish forecasts; they do not
create independent copies of market truth. Later journal revisions append; new
ledger snapshots never overwrite original forecasts. SHADOW role on a simulated
row does not establish prospective shadow issuance.

[FF §12](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#12-paired-comparison-engine-and-identity)
requires a fingerprinted realization-mode policy and per-arm modes/profile refs:
actual/actual and simulated/simulated require the ordinary exact scientific
compatibility checks; actual/simulated is default-excluded from pooling and needs
an explicit preregistered mixed-mode research policy with matched observations,
target/horizon, cutoff policy, population, labels/splits and metrics. Retain
per-mode counts, failures/exclusions and simulation limitations. It never becomes
prospective operational evidence by pooling or a change of display label.

## 5. Walk-forward, LLM/provider and Ground Truth implications

[FF §10.1](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#101-historical-simulation-and-walk-forward-eligibility)
inherits A7's historical eligibility without rewriting it. Fold manifests pin
fit/calibration/selection/forecast knowledge boundaries, population and data
vintages; labels used in learning must have matured by the permitted historical
boundary. Actual fitting today can realize that qualified retrospective protocol,
but future-trained weights, later folds, post-cutoff revisions, survivors or
test-selected transforms cannot enter an earlier simulated forecast. Preserve
real fit completion and simulated fit cutoffs separately. Repairs create new
experiment lineage rather than silently deleting contaminated cases.

CAPTURED_AS_KNOWN still requires availability, first capture and TI admission by
cutoff. Downloading an old bar today does not establish earlier eligibility.
The mode flag does not close DEF-049 or independently qualify any real dataset.

[FF §16](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#16-fmlfde-and-llm-forecaster-placement)
retains the optional governed LLM boundary. A permitted current LLM/provider
query simulating history is SIMULATED, with the current observable version,
rendered input/response, real computation and simulation profile. It is not
historical provider issuance; even historical version existence needs an original
capture to prove an actual old response. Training-vintage/overlap/rights still
need independent qualification. Unknown or contaminated history stays excluded
from PIT-qualified evaluation; only explicitly granted unqualified diagnostic
capture may remain, otherwise reject. No query is performed by this pass.

Ground Truth remains Evaluation-owned: target resolution is the qualified event
boundary; outcome recording is later journal processing. Delayed ingestion does
not move resolution or make the outcome knowable before its recorded availability.
Each revision preserves event/availability/recording facets and existing censoring.

## 6. Replay is not simulation

The normative rule in
[FF §18.1](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md#181-verification-promises-and-immutable-pins-fft-24)
is: **Replay verifies or reconstructs a historical artifact; simulation creates
a new explicitly simulated artifact.**

```text
original ACTUAL or SIMULATED capture
    ├─ recorded replay → original canonical mode/clocks/fingerprint
    └─ pinned verifier → original semantic comparison + separate verification time/cost

historical PIT capture + new research run/profile/model
    └─ historical simulation → new SIMULATED result, actual later computed_at
                               optional link to old control, never overwrite
```

Replay is not a third realization mode. Verifier processing time never becomes
new historical issuance or replaces the original `computed_at`. Missing old
verifier/artifacts cannot trigger current-model fallback. Changed model/profile
over a historical cutoff is a new simulation, not original replay. An intact
recorded simulated artifact itself also replays with its original SIMULATED mode.
Existing canonical-equality versus tolerated-verification and access/retention
limits remain; no old fingerprint algorithm/schema is changed in runtime.

## 7. Required semantic cases and additional boundary checks

All times below are **illustrative, aware Asia/Kolkata instants**, not asserted
NSE session times or a qualified real dataset. Historical date H = 2026-08-04;
synthetic target open H 09:30, resolution H 16:00; qualified reference close is
the prior source session. “Today” = 2026-09-14 12:00+05:30. Time-only values in
the table abbreviate H instants. Assume all non-clock gates pass unless stated.
These are architectural fixtures/hand checks, not an executed FF implementation.

| Case | Supplied facts | Required result |
|---|---|---|
| A — Actual valid | Cutoff/as-of 09:20; computed 09:20; issued 09:21; opens 09:30 | Valid ACTUAL clocks; genuine production and other admission gates still required; supervised scoring waits for eligible outcome |
| B — Actual backdated | Computed 18:00; claims issued 09:20 | Reject; issued before actual production, also no timely actual forecast |
| C — Simulated valid | Computed today; historical simulation-as-of/cutoff H 09:20; target H 09:30 | Valid SIMULATED clocks; no issued_at; eligible research/evaluation only with full PIT/profile/outcome gates |
| D — Simulated leakage | Historical cutoff 09:35; target opened 09:30 | Reject, even if computation is honestly recorded today |
| E — Same target, different artifacts | Actual A1 plus simulations S1/S2 from different model/composition/profile versions; shared O1/J1 | Preserve all three IDs/modes/clocks and one outcome; neither overwrite A1 nor triple independent sample weight |
| F — Replay versus simulation | Read/verify A1 using pinned original closure; separately compute S3 over its historical cutoff | Replay retains A1 issue/compute; new verification has separate processing/cost; S3 is a new SIMULATED result, not an updated A1 |
| G — Current LLM history query | Separately granted hypothetical query today over H cutoff, current provider/model revision | SIMULATED; no historical issuance claim; unknown vintage/overlap cannot pass PIT qualification even with captured response |
| H — Exact-open equality | ACTUAL issued 09:30, or SIMULATED as-of/cutoff 09:30 | Reject both under retained strict pre-open rule |
| I — Honest but late actual | Computed 09:31; issued 09:32; declared ACTUAL | Reject prospective admission, retain diagnostic; do not silently relabel as simulation to rescue the run |
| J — Learned leakage | Features by 09:20, but weights/calibrator/selection used outcome knowledge from a later fold | Reject PIT qualification; historical feature cutoff alone is insufficient |
| K — Late historical acquisition | Old event 09:00, first captured/admitted after H cutoff | Reject CAPTURED_AS_KNOWN eligibility; simulation flag grants no historical-vintage exception |
| L — Outcome arrives later | Actual A1 timely; target resolves H 16:00; outcome recorded next day | A1 can exist before outcome; score only after qualification at admitted evaluation cutoff; never move target to ingestion time |
| M — Replay simulated capture | Replay S1 months later without its optional SDK | Original SIMULATED mode/computation/as-of/fingerprint remains, subject to intact authorized capture; not an actual record |
| N — Mixed comparison | A1 and S1 share exact O1/outcome but no mixed-mode policy | Do not pool. A new explicit preregistered compatible mixed policy may admit research comparison, never relabel it prospective |

## 8. Five HOLD dimensions — correction coverage matrix

“Corrected” means the source gap is addressed and ready for independent repeat
review, **not** that this correction pass changes the original verdict to ACCEPT.

| Original HOLD dimension | Root cause | Correction | Architecture section | Status after correction |
|---|---|---|---|---|
| 3 — Forecast contracts | Unconditional actual issuance guard could not represent later historical computation | Two modes, nine-clock table, anti-backdating, request/result identity and staged eligibility | §§3.1–3.3 | CORRECTED; repeat acceptance required |
| 26 — Replay | New historical counterfactual request could be confused with pinned verification/old issuance | Replay over either original mode; new historical generation is SIMULATED with separate real computation/profile | §18/§18.1 | CORRECTED; recorded/pinned guarantees retained; repeat required |
| 29 — Miniature FF scope | FF-1 B0/B2 historical evaluation lacked valid new-run time semantics | Explicit fold-safe simulation, mode-preserving ledger/evaluation; FF-0–FF-2 guard/fixture obligations | §§3.2/10.1/11–12; roadmap §§3–5 | CORRECTED without expanding miniature; repeat required |
| 30 — FF-0…FF-7 roadmap | Historical comparison/counterfactual deliverables inherited ambiguous clocks | Foundation mode contracts, FF-1 historical research and mode policy, FF-2 actual shadow versus simulation; unchanged later stage order | §§10.1/18.1; roadmap §§2–5/11 | CORRECTED; no new stage or implementation authorization; repeat required |
| 31 — A7 ownership seam | A7's separate simulated/actual fit/forecast clocks were absent from FF admission | Carry A7 §§5–6 into FF; future projection preserves mode/clocks; no new truth owner or A7 edits | §§3.2–3.3/10–12/20.1 | CORRECTED at FF boundary; full A7 integration still separately pending |

## 9. Non-blocking follow-ups and residual choices

| Original clarification | Handling in this narrow pass |
|---|---|
| FFA-C01 — Failure mapping | PRESERVED follow-up: detailed required-child operator table governs; final namespaced mapping/fixtures remain implementation work; no voting rule changed |
| FFA-C02 — Staged implementation scope | PRESERVED: singleton foundation, separate B0/B2 comparisons and FF-2 calibrator before optional FF-3 machinery; add only clock/mode obligations, no graph-executor expansion |
| FFA-C03 — Retention/access | PRESERVED: exact capture closure and current rights needed; concrete retention/serializer policy later; no new store or retention service |
| FFA-C04 — Timeout/cost | PRESERVED: import isolation is not process containment; unknown held work and late publication/usage limits remain; no new cancellation/pricing machinery |

Remaining implementation choices are concrete additive schema/profile names,
canonical serializer/verifier field mapping, trusted clock provenance and precision
validation, finite study/fit/calibration/mixed-comparison profiles, data qualification
and consumer exposure. Unknown evidence/clock qualification fails closed; these
choices cannot relax the new mode or anti-backdating invariants. No metric weights,
model thresholds, source qualification or research performance is established.
Repeat FF acceptance and separately scoped A7 integration/implementation sequencing
remain prerequisites; A7 itself and all 28 original finding dispositions are intact.

## 10. Files changed and validation

One new correction record (this file). Existing edits: architecture and roadmap
semantics, four FF record/status addenda, and twelve navigation/status documents.
Compared with the entry snapshot: **18 existing files changed, one new file,
185 existing files unchanged, zero removed** (203 → 204 README/docs files,
excluding office locks and bytecode). The worktree already contained uncommitted
A7/FM/FF documentation; a diff against HEAD includes earlier work, not just this
pass. No earlier change is claimed as ours or implicitly authorized for staging.

| Existing files changed in this pass |
|---|
| [README.md](../README.md) |
| [docs/ARCHITECTURE.md](ARCHITECTURE.md) |
| [docs/IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) |
| [docs/MILESTONES.md](MILESTONES.md) |
| [docs/README_TBD_DESIGN_NOTES.md](README_TBD_DESIGN_NOTES.md) |
| [docs/TIAF_CAPABILITY_MAP.md](TIAF_CAPABILITY_MAP.md) |
| [docs/TIAF_DEFERRAL_REGISTER.md](TIAF_DEFERRAL_REGISTER.md) |
| [docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md) |
| [docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE.md](TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE.md) |
| [docs/TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md](TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md) |
| [docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md](TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md) |
| [docs/TIAF_FORECASTING_FRAMEWORK_THESIS_ARCHITECTURE_RECONCILIATION.md](TIAF_FORECASTING_FRAMEWORK_THESIS_ARCHITECTURE_RECONCILIATION.md) |
| [docs/TIAF_FORECASTING_FRAMEWORK_THESIS_RECORD.md](TIAF_FORECASTING_FRAMEWORK_THESIS_RECORD.md) |
| [docs/TIAF_IMPLEMENTATION_TARGETS.md](TIAF_IMPLEMENTATION_TARGETS.md) |
| [docs/TIAF_SYSTEM_ARCHITECTURE.md](TIAF_SYSTEM_ARCHITECTURE.md) |
| [docs/TIAF_THESIS.md](TIAF_THESIS.md) |
| [docs/TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md) |
| [docs/TRADINGINTELLIGENCE_ROADMAP.md](TRADINGINTELLIGENCE_ROADMAP.md) |

| Validation performed | Result |
|---|---|
| `git diff --check` | PASS |
| Untracked-document whitespace | PASS; all seven FF Markdown files checked with `git diff --no-index --check` against `/dev/null`; fences and heading separation also checked |
| Documentation links/anchors | PASS; existing handbook validator `validate_links(True)`; final count recorded below; no external URLs fetched |
| Semantic fixture completeness | PASS; nine canonical clock rows, cases A–N (14), all five original HOLD dimensions and complete 21-item report |
| Clock arithmetic | PASS; seven standalone aware-datetime assertions for A/B/C/D/H/I, including both equality rejections. This is document logic, not FF runtime testing |
| 28 thesis findings | PASS; exact FFT-01–FFT-28 and eleven-column rows; 15 NO_CHANGE, nine CLARIFICATION_ADOPTED, two IMPLEMENTATION_DETAIL, two DEFER |
| Four historical records | PASS; removing only the new addendum and restoring the status heading in memory reproduces each entry body exactly; original acceptance/reconciliation verdicts and tables preserved |
| Settled architecture | PASS; §§4–9 and §§13–15 remain byte-for-byte unchanged: no primitive/composite/operator/calibration/lifecycle/statistical/self-correction redesign |
| 58 canonical deferrals | PASS; full canonical rows byte-for-byte equal to the entry capture, no ID/status or unrelated narrative changes |
| Protected sources/artifacts | PASS; SHA-256 unchanged for six A7/FM/FF DOCX/PDF artifacts, ten A7/FM source records and 37 handbook source/build/chart/page-map files |
| Current status/navigation | PASS; architecture CORRECTED AFTER HOLD, thesis RECONCILED, acceptance MUST BE REPEATED, A7 PAUSED and runtime NOT_IMPLEMENTED; old HOLD/then-next text is historical |
| Runtime / A7 implementation | PASS preservation; all dirty paths remain README/docs; `git status --short -- src tests scripts pyproject.toml uv.lock` is empty |
| Frozen baseline / Git | PASS; HEAD and resolved `tiaf-a6-baseline` remain `6dc2ff304aae0e87540260b092919bb91e4d4189`; no commit/tag/push or staging |

Final local-link count: **1,210 local links across 33 Markdown files — PASS**.
No runtime tests, training, live/provider/model/broker calls or model evaluation
were performed. Documentation checks do not establish empirical qualification,
dataset readiness, or independent architecture acceptance.

## 11. Complete requested final report

| # | Item | Result |
|---|---|---|
| 1 | Exact decision | READY_TO_REPEAT_FORECASTING_FRAMEWORK_ARCHITECTURE_ACCEPTANCE |
| 2 | Files changed | §10; one new record and eighteen existing documentation files |
| 3 | Blocker | §2; unconditional actual-before-open clock conflicted with later historical research |
| 4 | Actual semantics | §3; genuine compute then issuance, strictly before target open |
| 5 | Simulated semantics | §3; historical as-of/cutoff, real later computation, no issued_at |
| 6 | Canonical clocks | Architecture §3.2; nine meanings, no competing as-of fields; owning-record provenance retained |
| 7 | Anti-backdating | Normative; historical context never becomes false actual issuance |
| 8 | Result / ledger identity | §4; mode, applicable clocks/profile, graph/evidence pins and distinct run IDs; one common outcome |
| 9 | Target-open rules | ACTUAL issued_at strictly before open; SIMULATED cutoff/as-of strictly before open, actual computation may follow |
| 10 | Actual evaluation | Genuine admitted forecast plus qualified later target/outcome/label and comparison; future truth not required at issue |
| 11 | Simulated evaluation | PIT-safe data and all learned/selection dependencies, replayable profile, qualified target/outcome; research only |
| 12 | Paired policy | §4; matching actual/actual or simulated/simulated, explicit preregistered mixed-mode research only, no silent pooling |
| 13 | Replay versus simulation | §6; reconstruct/verify original versus create new SIMULATED, no clock substitution |
| 14 | Walk-forward | §5; historical cutoffs/folds, actual later fit/computation, no future-fold contamination |
| 15 | LLM/provider simulation | §5; current-model SIMULATED, original historical issuance needs original capture; vintage/overlap qualification not waived |
| 16 | Ground Truth | §5; target event resolution distinct from label availability and journal recording |
| 17 | Five HOLD dimensions | §8; 3/26/29/30/31 corrected for repeat review, no automatic ACCEPT |
| 18 | Four clarifications | §9; all preserved as bounded follow-ups, no operator or operational redesign |
| 19 | Validation | §10; documentation/preservation checks only, no runtime test suite |
| 20 | Residual questions | §9; concrete schema/clock assurance/profile/data/retention choices under fixed invariants and later authorization |
| 21 | Exact next prompt | TIAF FORECASTING FRAMEWORK — ARCHITECTURE ACCEPTANCE (REPEAT) |

No commit, tag, push, runtime implementation, training or live call is performed.
