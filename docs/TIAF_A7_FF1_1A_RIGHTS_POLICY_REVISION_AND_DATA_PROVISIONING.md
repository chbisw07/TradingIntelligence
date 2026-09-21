# TIAF A7 / FF-1.1A — Rights-policy revision and data provisioning

Review date: **2026-09-20, Asia/Kolkata**. Local inventory recheck:
`2026-09-20T22:34:46+05:30`. Scope: offline research qualification only.

```text
FF1_1A_RIGHTS_POLICY_REVISION_ACCEPTED
RIGHTS_POLICY_REVISION = COMPLETE
PROVISIONING = HOLD_NO_EMPIRICAL_DATASET
PROVISIONING_COMPLETE = NO
EMPIRICAL_FITTING_AUTHORIZED = NO
```

Policy implementation acceptance is separate from data/scientific acceptance.
No empirical qualification run, model/scaler fitting, walk-forward forecast,
provider call, download, broker call, calibration or publication occurred.

## 1. Entry state and historical audit

Entry HEAD: `2eb522c` (`feat(a7.ff1.1): implement data qualification and feature schema`).
The worktree already contained the previous HOLD document, its JSON audit and
one MILESTONES row. Those inputs belong to the preceding completed pass; they
are retained. A6 remains `6dc2ff304aae0e87540260b092919bb91e4d4189` /
`tiaf-a6-baseline`; FF-0 remains `e5283c9eaa4294bd236186d663335efdf7dab236` /
`tiaf-a7-ff0-baseline`. No commit/tag/push.

The [previous enforced HOLD](TIAF_A7_FF1_1A_EMPIRICAL_DATA_RIGHTS_QUALIFICATION_EXECUTION.md)
and [audit artifact](qualification_records/ff1_1a/qualification_attempt_4f6d2a998b241ca04e99757791545315482606381af170ff61d1c948c977b833.json)
are **byte-for-byte unchanged**. Their rights semantics were effectively ENFORCE;
their HOLD was correct. This is policy evolution, not a correction of history.

| Preserved object | SHA-256 |
|---|---|
| Original HOLD document bytes | `4b65f4c88665f1198535e837d70aa199443e08e4ebb337260ae499cce7839c79` |
| Original audit file bytes | `59be5223fc06dcdfb203f1e3a6ce0bfbd6d433804b31685ad9de2813cf54acee` |
| Original audit semantic seal, excluding its seal field | `4f6d2a998b241ca04e99757791545315482606381af170ff61d1c948c977b833` |

Original document pins in that audit refer to their then-current versions, not
the revised working copies. No old audit pin is rewritten. A regression test
checks both byte hashes and the original semantic seal.

## 2. Evidence, enforcement and admission are different

`RightsEvidenceStatus` describes supplied evidence: `VERIFIED_ALLOWED`,
`VERIFIED_DENIED`, `UNVERIFIED`, `AMBIGUOUS`. These are evaluated assertions, not
an authentication of an external license. Referenced basis is required for new
explicit VERIFIED assertions. Each of the five existing use-specific fields
can carry these statuses; its original value and evidence references are kept.

Legacy `QUALIFIED` assertions aggregate to VERIFIED_ALLOWED only with their
matching source/subject/pin, basis, coverage and valid assessment. `UNKNOWN`
maps to UNVERIFIED; `NOT_QUALIFIED` maps to AMBIGUOUS, **not an invented explicit
denial**. Missing basis is UNVERIFIED; expired/out-of-coverage/future-assessed
assertions are AMBIGUOUS. Any explicitly supplied denial takes precedence over
other states and is never erased by expiry, uncertainty or policy selection.

| Evidence | ENFORCE | WARN_ONLY (default) | DISABLED |
|---|---|---|---|
| VERIFIED_ALLOWED | ADMITTED | ADMITTED | NOT_ENFORCED |
| UNVERIFIED | HOLD | ADMITTED_WITH_WARNING | NOT_ENFORCED |
| AMBIGUOUS | HOLD | ADMITTED_WITH_WARNING | NOT_ENFORCED |
| VERIFIED_DENIED | HOLD | HOLD | HOLD |

DISABLED is deliberately conservative: it disables the uncertainty gate, not
explicit-denial protection. **No higher-authority override exists in this
workflow; none is introduced.** It emits `RIGHTS_ENFORCEMENT_DISABLED` even for
allowed evidence. WARN_ONLY emits `RIGHTS_NOT_APPROVED_RESEARCH_ONLY` for
uncertainty; ENFORCE emits `RIGHTS_EVIDENCE_NOT_VERIFIED_ALLOWED` when holding it.
Explicit denial emits `EXPLICIT_RIGHTS_DENIAL_NO_OVERRIDE` under every policy.

The report separately serializes `rights_evidence_status`,
`rights_enforcement_policy`, `rights_admission_result`, `rights_warnings`,
`rights_ref` and `rights_configuration_fingerprint`. A rights-level admission
does **not** imply that the dataset or scientific pipeline passes. Wrong rights
artifact, source or subject identity still yields `PROVENANCE_UNQUALIFIED` under
every policy; it cannot be treated as harmless uncertainty.

This policy does not grant legal permission, alter provider contracts or external
law, authorize redistribution/commercial publication, or change retention.
Unknown rights remain unknown. A learning grant is still separate.

## 3. COLD configuration and replay

Trusted bootstrap chooses one `ResearchRightsConfig`, then constructs a frozen
`ResearchQualificationRuntime`. It defensively revalidates/copies the config;
the owner and nested config reject attribute replacement. Its `qualify` method
has no policy argument. Reconfiguration requires a new owner, not a mid-run
mutation. Like R5, this is an API contract, not a hostile-Python sandbox.

```python
from tiaf.evaluation.forecast_qualification import ResearchQualificationRuntime
from tiaf.evaluation.forecast_research_contracts import (
    ResearchRightsConfig,
    RightsEnforcementPolicy,
)

# Trusted application startup, not supplied dataset/request content:
runtime = ResearchQualificationRuntime(
    ResearchRightsConfig(rights_enforcement_policy=RightsEnforcementPolicy.WARN_ONLY)
)
# supplied_dataset and aware_assessment_time come from the existing local flow.
# result = runtime.qualify(supplied_dataset, assessed_at=aware_assessment_time)
```

Omitting config selects WARN_ONLY. Existing `qualify_dataset(dataset,
assessed_at=...)` is a one-run trusted bootstrap using that same default.
There is no environment-variable override, implicit file lookup, new CLI flag,
Shell/facade capability or policy field in the dataset. This separate research
owner follows R5; it does not change R5's facade composition schema.

The config pins `FF1_RIGHTS_1.0` and its enforcement policy. Qualification policy
is explicitly revised from `FF1_1_QUALIFICATION_1.0` to
`FF1_1_QUALIFICATION_1.1`. The qualification seal covers policy, config hash,
rights evidence status/reference, admission, warnings and the existing full
report. Changing policy changes the qualification seal even if scientific
features are identical. Dataset and feature values are not retuned.

Canonical JSON plus `EmpiricalDatasetQualification.model_validate_json(...)`
round-trips current reports with identical seals, without providers or fitting.
Reconstruction rejects an inconsistent policy/admission/warnings/config hash,
even when the outer seal is omitted. This is integrity verification, not a
signature or re-authentication of source assertions. Old policy-1.0 reports are
not silently interpreted as policy-1.1; retain their original version/reader.
The prior generic preflight audit is not this typed report and is unchanged.

Future training-job qualification evidence and paired-evaluation lineage must
reference the **full qualification seal** and rights/configuration pins, not just
the dataset or feature hash. Those later jobs do not yet exist; no pretend
training integration is added. Research envelopes remain schema `2.0`; package
version `0.1.0`, A0/FF-0 schema `1.0`, target and feature formulas are unchanged.
All actual clocks remain aware and normalize to `ZoneInfo("Asia/Kolkata")`.

## 4. Local provisioning recheck

Inspected repository-local data/artifact candidates, including ignored data,
CSV/TSV, JSON/JSONL/NDJSON, Parquet/Arrow/Feather, XLSX/HDF/pickle and compressed
fixture/archive names. Excluded VCS, environment, node/dependency and tool caches.
Did not read secrets or search unrelated home/download folders. No additional
dataset path, data-library root or acquisition grant was supplied in this brief.

**No usable empirical RELIANCE daily OHLCV dataset was identified. Dataset path:
none.** Preferred Nov-2017–Jan-2026 coverage remains a requirement, not a claim.
Candidate inventory consists of synthetic fixtures, handbook illustrative data,
manifests, the previous audit, and the existing instrument master.

The only local market-data CSV is
`data/instrument_master/dhan/api-scrip-master-detailed.csv` (ignored; not changed).
Its SHA-256 remains
`6e65523933d51e6aad54cb4b3cff4f27708fe0e4710a8c03f239da666f674fd2`.
Line 171597 maps `RELIANCE`, `NSE`, cash `EQUITY`, security ID `2885`,
ISIN `INE002A01018`. This supports a current identity lead, **not** historical
dataset identity or daily OHLCV. No BSE, derivative or similarly named series is
substituted. Synthetic FF-0/FF-1 and A3 fixtures do not satisfy empirical gates.

Source/provider acquisition context, dataset content fingerprint, capture
vintage, historical mapping, approved NSE session calendar, adjustment policy,
corporate-action coverage and PIT availability therefore remain unqualified.
No bars, calendar sessions, features, labels, folds or counts are invented.
Empirical qualification invocations: **0**; empirical row/observation counts are
**unknown, not zero**. Policy tests use explicitly authored synthetic inputs.

### Fresh-download boundary

A future fresh download may support historical **SIMULATED** research only with
honest acquisition time and an explicitly approved conservative availability
policy, qualified source corrections/revisions, corporate actions and price
basis. It cannot be backdated or described as historically captured.

No such source-specific policy or dataset was supplied here. The implemented
`CAPTURED_AS_KNOWN` feature/PIT checks are **unchanged**; a fresh download does not
automatically pass them. Adopting another availability profile requires explicit
versioned scientific review, not a rights-policy toggle. The existing empirical
Outcome Journal/label integration boundary also remains: FF-0's synthetic-only
outcome contract is not widened and no second label comparator is introduced.

## 5. Current gate matrix

| Gate | Evidence state | Enforcement policy if applicable | Status | Blocking? | Reason |
|---|---|---|---|---|---|
| Rights evidence / enforcement | UNVERIFIED; no real entitlement supplied | WARN_ONLY | ADMITTED_WITH_WARNING at rights-policy level | No, for uncertainty alone | Not rights approval; explicit denial would still hold |
| Empirical dataset | Missing | — | HOLD | Yes | No RELIANCE daily source file supplied/found |
| Source/provenance | Unknown | — | HOLD | Yes | No acquisition context, artifact hash or vintage for daily bars |
| Security identity | Current master lead only | — | HOLD | Yes | NSE equity 2885 requires historical mapping to selected series |
| Frequency / OHLCV | Unknown | — | HOLD | Yes | Cannot verify completed daily bars, price/volume or duplicates |
| Session calendar | Unqualified | — | HOLD | Yes | No dataset-scoped authoritative native NSE schedule supplied |
| Corporate actions / basis | Unknown | — | HOLD | Yes | No adjustment policy or unaffected/affected coverage evidence |
| PIT availability | Unknown | — | HOLD | Yes | No qualified capture vintage or adopted source-specific alternative |
| Features | Not evaluated empirically | — | HOLD | Yes | Five-feature projector exists; empirical inputs absent |
| Labels | Not constructed | — | HOLD | Yes | No empirical truth/maturation evidence; versioned integration still needed |
| Fold feasibility | Not evaluated | — | HOLD | Yes | No admitted population/classes or realized split counts |
| Leakage | Not audited empirically | — | HOLD | Yes | No realized dataset/population; synthetic boundary tests are not proof |

This matrix is a provisioning preflight, not a fabricated typed qualification
report. Rights policy changes exactly the rights admission row. Scientific
requirements and future protocol/job approval remain independent.

## 6. Files and validation

Runtime changes are restricted to
[`forecast_research_contracts.py`](../src/tiaf/evaluation/forecast_research_contracts.py)
and [`forecast_qualification.py`](../src/tiaf/evaluation/forecast_qualification.py).
Tests update [`test_research_qualification.py`](../tests/unit/forecasting/test_research_qualification.py)
to select ENFORCE explicitly for its original strict-rights regressions and add
[`test_research_rights_policy.py`](../tests/unit/forecasting/test_research_rights_policy.py).
The new 45 cases cover all policy/status combinations, unknown evidence
preservation, legacy assertions, explicit basis requirements, scientific and
identity hard gates, immutable COLD config/no env or request override, config
fingerprints, offline reconstruction and original HOLD byte/seal preservation.

Documentation changed (eight files): this record;
[`TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md`](TIAF_A7_FF1_LOGISTIC_BENCHMARK_PAIRED_EVALUATION_PLAN.md);
[`TIAF_A7_FF1_1_DATA_QUALIFICATION_FEATURE_SCHEMA_IMPLEMENTATION.md`](TIAF_A7_FF1_1_DATA_QUALIFICATION_FEATURE_SCHEMA_IMPLEMENTATION.md);
[`TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md`](TIAF_FORECASTING_FRAMEWORK_DECISION_RECORD.md);
[`TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md`](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md);
[`README.md`](../README.md); [`MILESTONES.md`](MILESTONES.md); and
[`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md).
The prior HOLD document/audit remain existing untracked inputs from the preceding
pass, not rewritten products of this revision. Twelve files changed in this pass
(two source modules, two test modules, eight documents).

Commands use the repository `.venv/bin` executables. Counts below overlap; they
are not additive.

| Validation | Result |
|---|---|
| `pytest -q tests/unit/forecasting/test_research_rights_policy.py` | **45 passed**, 9.63s; no warnings in final run |
| Three research test modules: qualification, isolation edges, rights policy | **147 passed**, 25.21s; initial expected forged-config serializer warning subsequently captured by its test |
| `pytest -q tests/unit/forecasting tests/acceptance/ff0 tests/unit/features tests/unit/source_semantics` | **1,136 passed**, 116.94s; includes all 28 FF-0 acceptance cases |
| `pytest -q` | **3,068 passed**, 327.90s; no failures or warnings |
| `python -m compileall -q src scripts` | PASS |
| `ruff check src tests scripts` | PASS |
| `mypy src tests` | PASS; 609 source files |
| Changed/new Markdown file targets and code fences | PASS; eight documents, no missing local file targets, balanced fences |
| `git diff --check` plus explicit new-file whitespace checks | PASS |
| Prior HOLD bytes and semantic seal | PASS; original hashes above |
| Frozen A6/FF-0 tag identity and source scope | PASS; only the two research Evaluation modules changed in `src` |

No optional provider/ML dependency was added. Existing isolation tests also
verify qualification performs no file/network/process I/O and adds no public
capability. Rights relaxation does not alter the five A2 formulas, future-price
leakage tests, calendar/action checks, aware-time behavior or original FF-0
recorded/pinned replay.

## 7. Decision, blockers and next work

No architecture deviation beyond the explicitly approved local-research rights
policy evolution. No dependency, target, A2 feature formula, A6/FF-0 semantics,
provider, public capability or execution authority changes. WARN_ONLY is chosen
instead of DISABLED to make uncertainty visible. Explicit denial remains a
conservative HOLD because no override authority exists.

The code revision can close while provisioning remains blocked on an actual
dataset and its scientific evidence. No scaler/model fitting, future stage or
retention permission is inferred from implementation acceptance.

Recommended commit after review (not executed):
`feat(a7.ff1.1a): make rights qualification policy-configurable`.
No tag. No commit, tag or push was performed.

Exact next prompt title:

**TIAF A7 / FF-1.1A — LOCAL RELIANCE EMPIRICAL DATASET PROVISIONING**
