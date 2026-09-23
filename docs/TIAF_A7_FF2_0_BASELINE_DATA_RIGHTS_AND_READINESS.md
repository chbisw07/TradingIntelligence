# FF-2.0 — Baseline, data rights and readiness record

Date: 2026-09-23, Asia/Kolkata. Scope: read-only repository/data metadata and
documentation for the [calibrated Logistic protocol](TIAF_A7_FF2_0_CALIBRATED_LOGISTIC_RESEARCH_PROTOCOL.md).
No experiment, model/calibrator fit, forecast generation, scoring, holdout opening,
market API, runtime modification, commit, tag or push.

## Git precondition

| Required check, before FF-2 work | Observed result |
| --- | --- |
| Branch / tree | `main`; `git status --short` empty |
| HEAD / local origin/main | Both `5f1e80c7e0614233b5670ca3acf9229edd0ea0db`; ahead/behind 0/0 |
| FLC closure commit | `TIAF A7: freeze Forecaster Lifecycle Completion baseline` |
| Local tag | `tiaf-a7-flc-baseline`, annotated object `08767b720c62410166717a6df0002a7e9e24e692`, peeled to HEAD |
| Actual origin main / tag | `git ls-remote` confirmed identical main, tag object and peeled commit |

The first remote check hit sandbox DNS restrictions. An approved read-only retry
succeeded; remote status is not inferred solely from the cached tracking branch.
This pass verifies the user's existing freeze; it does not perform another one.
The FLC report's earlier “not frozen” language remains truthful historical text.

## Data and rights inventory

Inspection scope: local `data/` inventory, existing acquisition/provisioning/
qualification summaries, historical implementation/closure reports, selected
training artifact metadata and frozen final metadata. The source CSV was
byte-hashed and its **date column** inventoried. No price/label-based metric,
new feature, membership qualification or calibration was computed. A date-only
inventory does not prove uninspected outcomes or grant any future use.

The available local data directories are `ff1` and `instrument_master`; the
master is instrument metadata, not a fresh forecast/outcome corpus. No FF-2
qualified corpus was present in that inventory. This is a bounded repository
finding, not a claim that no external data could ever be acquired.

| Evidence | Actual identity / limitation |
| --- | --- |
| Source file | `data/ff1/reliance/reliance_daily_ohlcv.csv`, 99,118 bytes, 2,045 rows, 2017-11-01–2026-01-30 |
| Source SHA-256 | `d91311cdae0ecec8b3f7c60522e805c6b495e02ea633fdcb63b65476ef0dd6f6` |
| Source manifest | `data/ff1/reliance/source_manifest.json`; semantic fingerprint `3d1a4e21b6f4d08cb94b29d0aac83ec368c3c79c40bc535f2a75da55fb452c09` |
| Acquisition | TI-native Dhan, fresh historical download at `2026-09-21T12:07:50.995917+05:30`; raw response not retained |
| Native qualification used by FF-1 training | Semantic fingerprint `4b021081c3f5ee1afa3ff389f754ce91920fa45a367d4c88064330a0d1999d51`; bytes `69333427ebb355672d67e19885ba83a659a0427c8760cce4eac717c49a87d4ca` |
| Research profile | `ff1.adjusted_retrospective/1.0`, fingerprint `1e616cc7a2f3654d856b916e790d054a6c1ff7f10efe2b316cf0a44835011c45` |
| Feature schema/profile | Five existing A2 features, fingerprint `76e63292685ee0b3b41f7ab033407e6bd014fc802d2092a2ed227888bdc71676` |
| Original rights policy | UNVERIFIED / WARN_ONLY / ADMITTED_WITH_WARNING; configuration `2ca6488c4b09e6437e246f91bfc227c6376c01849498d06df2fb038b5a64d981` |
| Source limitations | Later adjusted vintage, assumed historical availability, provider-defined volume, normalized binary64 not forensic source decimals, bounded action review |

The private directory named `adjusted_qualification_20260921_final` contains an
earlier qualification checkpoint. Its name alone is not authority to replace the
exact qualification pin used by accepted training. Follow artifact references,
not directory names. The
[accepted qualification report](TIAF_A7_FF1_1A_ADJUSTED_DATA_RESEARCH_PROFILE_AND_FINAL_QUALIFICATION.md)
and [training handoff](TIAF_A7_FF1_3_LOGISTIC_WALK_FORWARD_FORECAST_GENERATION.md)
explain the source and exact downstream pins. Their then-SEALED status must not
override the later consumed ledger.

### Period and use matrix

“Proposed” below is protocol purpose, not permission to execute. Calendar-year
source counts include rows that may be ineligible as forecast origins.

| Period | Rows | Exposure / existing role | Proposed FF-2 use | Permission now |
| --- | ---: | --- | --- | --- |
| Nov–Dec 2017 | 42 | Known historical warm-up | Provenance/context only | Inspect metadata; no fit |
| 2018 | 246 | Known TRAINING / DEVELOPMENT | Selected native model training lineage | Read-only identity, not refit |
| 2019 | 245 | Known TRAINING / DEVELOPMENT | Same | Read-only identity, not refit |
| 2020 | 252 | Known TRAINING / DEVELOPMENT; action exclusions retained | Same | Read-only identity, not refit |
| 2021 | 248 | FF-1 inspected development; selected 2022 model uses qualified training prefix | Same; no new tuning | Read-only identity, not refit |
| 2022 | 248 | FF-1 inspected development | CALIBRATION subset after purge/embargo; not protected | New FF-2 grant/qualification required |
| 2023 | 246 | FF-1 inspected development, 225 original pairs | V1 DEVELOPMENT / selection validation | New FF-2 grant required; raw outputs must use the selected fixed model |
| 2024 | 249 | FF-1 inspected development, 248 original pairs | V2 DEVELOPMENT / validation; no target in 2025 | Same; never renamed independent final |
| 2025 | 249 | CONSUMED FF-1 protected final, one execution | EXCLUDED from all FF-2 numeric research roles | Metadata/hash preservation only |
| Jan 2026 | 20 | Later-vintage file context, not a registered protected partition; may include FF-1 endpoint context | EXCLUDED from v1 calibration/validation/final/support | No scientific reuse inferred |
| Later history / future issuance | Not present | UNAVAILABLE as qualified FF-2 evidence | Future protected accrual only after actual freeze, rights and capture gates | Not authorized or acquired |

TUNING: no period assigned; forbidden. PROTECTED_FINAL_EVALUATION: **zero
qualified FF-2 observations presently identified**. This is not a numeric sample
count from a newly opened protected corpus. The 969 known FF-1 development pairs
and 249 consumed final pairs do not become 1,218 new independent observations.
Synthetic FLC fixtures are engineering support only.

### Three different rights questions

1. **Technical custody:** the local bytes and hashes exist. This enables integrity
   inspection, not inference of lawful use or scientific independence.
2. **Source/data-use permission:** historical research admission knowingly used
   UNVERIFIED rights under WARN_ONLY. That is not verified provider licensing,
   legal advice, production permission or redistribution permission. This pass
   does not upgrade or newly interpret external contractual rights.
3. **Experiment/evidence-use authority:** FF-1 grants were bound to FF-1 and are
   consumed/closed. FLC executable grants are synthetic-only. Neither admits an
   empirical FF-2 calibration fit or protected evaluation. FF-2 must bind its own
   approved evidence-use declaration, inputs, purpose, grant and custody root.

The new grant must explicitly either accept a bounded WARN_ONLY **research-only**
policy with its uncertainty disclosed, or supply verified rights under a stricter
policy. Explicit provider denial always blocks. No default adoption of the old
warning policy and no production use under inferred permission. This is an
unresolved authority decision; it cannot be manufactured by writing this report.

## Frozen preservation checks

| Record | Expected / observed semantic fingerprint |
| --- | --- |
| FF-1 protocol | `2664b2d4963626e99a246eb30eb58dab2c8531038b59ef5a6cf679464cbaa814` — MATCH |
| FF-1 execution | `2948bc46874f8196c535720bd4f7882f6293fc96077acb563e2e11409c3e4840` — MATCH |
| FF-1 final evaluation | `8c0556e7b88284c170db57d745de7ece707d365ab52a585db5ebb0d3e81a7d0e` — MATCH |
| FF-1 complete ledger | `630dd96c0bcd65cb84139dfb20c7488d3e9385e16db18fbaacf60176c99fc583` — MATCH |

Read-only parsing of existing final contracts and hashing of their pinned files:
**72 source + 6 implementation = 78/78 MATCH**. Metadata remains CONSUMED,
executions 1, post-holdout refit false, automatic promotion false,
INSUFFICIENT_EVIDENCE / CONFIDENCE_NONDECISIVE. No final scoring/verifier command
or empirical training runner was invoked.

FF-0 native `forecasters`, `runtime`, `replay`, `support`, `contracts`, `identity`,
`capture` and the FF-0 acceptance/fixture directories have no diff against
`tiaf-a7-ff0-baseline`. FF-1/FLC reports and implementation are preserved; only
current navigation and new FF-2 documents change in this pass.

## Readiness decision

| Gate | Status / exact next action |
| --- | --- |
| FLC Git freeze | PASS, independently checked against live origin |
| Existing owner/seam fit | PASS at design level; learned calibration application and empirical admission explicitly not yet implemented |
| Scientific protocol | DEFINED v1, bounded and reviewable; document-byte checkpoint, not execution authority |
| Historical data classification | COMPLETE; known development, consumed 2025 and unavailable final distinguished |
| FF-2 data-use/evidence grant | **OPEN / BLOCKING**: external authority must approve exact historical purposes and WARN_ONLY research admission or verified rights |
| Prospective qualification/accrual | **OPEN**: source retention/use, compatible contemporaneous price basis, action/calendar coverage, actual freeze/start schedule and protected custodian must be supplied before accrual |
| Empirical implementation entry | HOLD for unqualified broad FF-2 entry; separate synthetic-only FF-2.1 carve-out remains possible |
| Independent final scientific acceptance | NOT_AVAILABLE; future accrual required, not replacement of 2025 |

No lack of future sample is claimed to prevent writing synthetic tests. The
conservative overall HOLD prevents a downstream “GO” from being interpreted as
empirical permission. Resolve FF-2-specific admission and implementation scope
first; do not infer them from the user's authorization for this documentation pass.

```text
FF2_PROTOCOL_DEFINED = YES
FF2_DATA_RIGHTS_RESOLVED = NO
FF1_PRESERVED = YES
FLC_PRESERVED = YES
FF0_PRESERVED = YES
READY_FOR_FF2_IMPLEMENTATION = NO
HOLD_FF2_IMPLEMENTATION
```

## Validation and change scope

Protocol document-byte checkpoint (SHA-256, not an executable scientific artifact
seal or an approval signature):

`33d334c3ab3aad21d739924898e6f2838545df47cf07cb0179d5d850ddaac271`

| Fresh validation | Result |
| --- | --- |
| Existing documentation link/anchor validator | PASS: 958 local links in 15 Markdown files (13 changed/new plus two fixed handbook inputs) |
| Changed/new Markdown fence and scope checks | PASS: 13 Markdown files only |
| Existing FF-1 read-only normalization tests | **2 passed, 47 deselected in 1.04s**; no re-scoring or fitting |
| Four FF-1 scientific fingerprints | 4/4 MATCH |
| Frozen FF-1 file pins | 78/78 MATCH |
| Selected native model/scaler availability | Both exact identities present in the existing local training corpus |
| FF-0 tagged native source/acceptance/fixture comparison | No diff |
| FLC tagged source/tests/scripts/package configuration | No diff |
| Historical FF-1/FLC reports and plan | Byte-identical to entry HEAD |
| `git diff --check` | PASS |

Commands:

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_evaluation_normalization.py -k 'legacy_ff1' --tb=short
.venv/bin/python -c 'from docs.handbooks.a7_forecasting.validate_handbook import validate_links; print(validate_links(True))'
sha256sum docs/TIAF_A7_FF2_0_CALIBRATED_LOGISTIC_RESEARCH_PROTOCOL.md
git diff --exit-code tiaf-a7-flc-baseline -- src tests scripts pyproject.toml
git diff --check
```

The two selected tests are
`test_legacy_ff1_readonly_view_preserves_recorded_semantics` and
`test_legacy_ff1_adapter_rejects_changed_identity_or_conclusion`.
No full runtime suite, compileall, Ruff or mypy rerun is claimed or needed for
this documentation-only change. FLC's historical 3,830 passing tests remain
historical, not a fresh result. No empirical fit/evaluation runner was invoked.

Created:

- `docs/TIAF_A7_FF2_0_CALIBRATED_LOGISTIC_RESEARCH_PROTOCOL.md`
- `docs/TIAF_A7_FF2_0_BASELINE_DATA_RIGHTS_AND_READINESS.md`

Updated current navigation/status only:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/IMPLEMENTATION_ROADMAP.md`
- `docs/MILESTONES.md`
- `docs/TIAF_A7_DETAILED_ROADMAP.md`
- `docs/TIAF_A7_FORECASTING_EVALUATION_LEARNING_ARCHITECTURE.md`
- `docs/TIAF_CAPABILITY_MAP.md`
- `docs/TIAF_FORECASTING_FRAMEWORK_ARCHITECTURE.md`
- `docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md`
- `docs/TIAF_IMPLEMENTATION_TARGETS.md`
- `docs/TRADINGINTELLIGENCE_ROADMAP.md`

README and roadmaps now say FF-0/FF-1/FLC COMPLETE / FROZEN and FF-2 CURRENT at
protocol stage only, with implementation on HOLD. Existing historical review
checkpoints retain their then-current decisions; architecture ownership and
later conditional work are not rewritten as delivered capabilities.

The OpenAI Docs skill was used only to ground phase model/effort recommendations
in the requested GPT-6 Astra identity; it did not change scientific policy or
introduce a model call in the forecasting application.
