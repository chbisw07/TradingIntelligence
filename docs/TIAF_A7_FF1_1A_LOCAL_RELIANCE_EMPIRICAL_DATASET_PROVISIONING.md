# TIAF A7 / FF-1.1A — Local RELIANCE empirical dataset provisioning

Inspection checkpoint: **2026-09-21T00:00:51+05:30**, Asia/Kolkata.

```text
HOLD_PROVISIONING
PROVISIONING_COMPLETE = NO
EMPIRICAL_FITTING_AUTHORIZED = NO
```

No empirical daily dataset was supplied or identified in the inspected repository.
The brief permits a fresh download only with explicit live-acquisition
authorization; no such authorization is present for this pass. No provider was
constructed or called, and credentials were not inspected. This is a local
provisioning preflight, not empirical qualification or a finding that Dhan is
unavailable.

## 1. Scope and preserved entry state

Entry HEAD: `2eb522c` (`feat(a7.ff1.1): implement data qualification and feature schema`).
The worktree already contained the accepted rights-policy revision and its
documentation/tests, plus the original qualification HOLD document/audit. All
those changes are preserved; this pass adds **only this document**.

Accepted subject/target: RELIANCE / NSE cash equity,
`equity.next_session_close.return_gt_zero@1.0`. Accepted feature schema:
`ff1.reliance.a2_daily_five/1.0`. No target, feature, COLD policy, runtime, public
capability, frozen A6 or accepted FF-0 semantics changed. No features, labels,
empirical qualification, model/scaler fitting, walk-forward forecasting or
paired metrics were run. No A8 work, commit, tag or push.

## 2. Local inventory and acquisition decision

Rechecked repository-local data/artifact filenames, including ignored `/data/`
and CSV/TSV, JSON/JSONL/NDJSON, Parquet/Arrow/Feather, XLSX/HDF/pickle and
compressed/archive candidates. Also searched names for RELIANCE, OHLCV,
calendar, holiday, corporate action and historical export. Excluded VCS,
environments, dependency/tool caches and unrelated home/download folders. No
additional dataset path or data-library root was supplied.

Findings:

- `data/instrument_master/dhan/api-scrip-master-detailed.csv` is an instrument
  master, **not** daily OHLCV. It cannot be substituted for the requested dataset.
- The RELIANCE files under `tests/fixtures/forecasting/ff0` are explicitly
  synthetic; their README also identifies their clocks as synthetic. An `actual`
  fixture name does not mean empirically captured data.
- Opportunity-intelligence compressed fixtures, golden manifests, acceptance
  corpora and handbook illustrative data are not an empirical daily-history
  export. No supplied corporate-action history or empirical calendar artifact
  was identified.

The existing provider method
[`DhanMarketDataProvider.get_historical`](../src/tiaf/data/providers/dhan/provider.py)
supports `1d` and routes to `/charts/historical` without a quote call. This is an
existing acquisition seam, **not a live availability check or authorization**.
The quote smoke script is not a history exporter, and the context smoke path
also requests quotes; neither was run or repurposed. No new acquisition client,
framework or script was created.

## 3. Dataset inspection result

Unknown values below are **not zero** and are not claims about an absent file.

| Requested field | Observed result |
|---|---|
| Source/provider | Unknown for daily dataset; Dhan master is separate identity evidence only |
| Acquisition method | None; no local export supplied and no live acquisition attempted |
| Acquisition timestamp | Not available; inspection time above is not acquisition time |
| Fresh versus historical capture | Unknown / not applicable without a dataset |
| Existing absolute/local dataset path | None identified |
| Dataset format / byte size | Unknown / unknown |
| Dataset SHA-256/content fingerprint | Not available |
| Columns / missing required columns | Not inspectable; no file |
| Row count / duplicate-row count | Unknown / unknown |
| First date / last date | Unknown / unknown |
| Apparent sort order | Unknown |
| Date/timezone representation | Unknown; future timestamps must be aware, canonical Asia/Kolkata |
| Embedded subject/exchange fields | Unknown; required scope is RELIANCE / NSE cash equity only |
| Desired coverage | Approximately Nov-2017 through Jan-2026; not claimed delivered |
| Normalization performed | None |
| Original / normalized fingerprints | Not applicable; no data read or transformed |
| Provisioning-manifest identity | NOT_CREATED — no dataset hash to reference |

No empty dataset or success-shaped manifest was created. Corporate-action/PIT
uncertainty may be packaged explicitly when a real file exists; it is not a
reason to invent a file or claim provisioning completion now.

## 4. Security, calendar, basis, PIT and rights evidence

### Security identity

The existing instrument master is 33,964,897 bytes, with SHA-256
`6e65523933d51e6aad54cb4b3cff4f27708fe0e4710a8c03f239da666f674fd2`.
Row 171597 records `NSE`, equity segment `E`, security ID `2885`,
`RELIANCE`, `EQUITY`, ISIN `INE002A01018`.
This is a current project-native mapping lead, not a dated historical-series
qualification. With no dataset, its rows cannot be checked against that mapping.
No BSE, derivative or similarly named issuer was substituted.

### Calendar reference

Reuse the existing
[`QualifiedSessionSchedule`](../src/tiaf/evaluation/forecast_contracts.py)
contract (`tiaf.ff.session-schedule`, existing schema `1.0`, venue `NSE`, segment
`NSE_EQUITY`, timezone `Asia/Kolkata`) through the research
[`SessionCalendarQualification`](../src/tiaf/evaluation/forecast_research_contracts.py)
wrapper. These contracts require explicit source/version/coverage references and
qualified sessions; they are not an authoritative historical calendar dataset.

**Actual calendar ID/version/source/coverage: UNKNOWN; empirical artifact
reference: MISSING.** No synthetic schedule is promoted to authority. No weekday
heuristic, invented holiday, fabricated session or filled bar is introduced.

### Corporate actions and price basis

`price_basis = UNKNOWN`. No dataset-specific provider adjustment declaration or
corporate-action file/source was supplied or identified. No adjustments were
applied. This explicit unknown can be recorded in a future provisioning package;
its scientific materiality belongs to the later qualification pass.

### PIT availability

`pit_availability_status = UNKNOWN`; dataset-specific provider documentation or
approved policy reference is missing. The existing feature-schema
`CAPTURED_AS_KNOWN` requirement is unchanged. No historical acquisition or
availability timestamps were inferred from prices, file modification times or
the instrument master.

If later authorized, a fresh download must record its true acquisition time,
remain marked fresh, and support only SIMULATED historical research. A
conservative source-specific availability policy candidate can be packaged for
review; it is not adopted or used to bypass PIT checks in this pass.

### Rights policy

The [accepted rights-policy revision](TIAF_A7_FF1_1A_RIGHTS_POLICY_REVISION_AND_DATA_PROVISIONING.md)
remains unchanged:

```text
rights_evidence_status = UNVERIFIED
rights_enforcement_policy = WARN_ONLY
rights_admission_result = ADMITTED_WITH_WARNING
```

This states the applicable **rights-level preflight disposition**, not an actual
dataset qualification result or rights approval. There is no supplied rights
record for an empirical daily dataset. Explicit VERIFIED_DENIED would remain
HOLD under every supported policy; no override exists. No legal permission,
redistribution/publication authority or retention change is inferred.

## 5. Required input and proposed local package

The repository already ignores `/data/`; use that area rather than adding an
unignored `local_data/` root. Expected location, **not created**:

```text
/home/cbiswas/Documents/Work/TradingIntelligence/data/ff1/reliance/
  reliance_daily_ohlcv.csv
  source_manifest.json
  security_identity.json
  calendar_reference.json
  corporate_action_basis.json
  pit_availability.json
  provisioning_manifest.json
```

Primary next user action: **provide an existing RELIANCE / NSE cash-equity daily
OHLCV export**, either at the CSV path above or by supplying its actual absolute
path. Required information is date/session identity, open, high, low, close and
volume; preserve the original column names and bytes for inspection. Include
source/provider, acquisition/export time if known, capture-vintage description,
symbol/exchange/security mapping and any available adjustment/calendar/PIT
references. Unknown evidence must be declared unknown, not guessed. A shorter
history can be provisioned; fold sufficiency is assessed later.

If no export exists, the alternative user action is to **explicitly authorize a
bounded, read-only Dhan historical-OHLCV acquisition** for RELIANCE / NSE cash
equity / security ID 2885, daily interval, requested coverage
2017-11-01 through 2026-01-31. That grant must not include quote, order or trade
operations. Credential/endpoint availability and safe existing-utility reuse
would then be checked without exposing secrets; they are not validated here.
If no suitable acquisition utility can be reused, supply a local export instead.

Once a real file is available, retain its original hash, inspect shape/security,
perform only documented transport/schema normalization if necessary, and package
true acquisition context, actual or missing calendar reference, UNKNOWN basis/PIT
where appropriate, and unchanged rights policy. A content-addressable
provisioning manifest must pin the dataset and companion evidence hashes without
embedding raw market data. No provisional hash is fabricated in this HOLD.

## 6. Validation and Git disposition

| Check | Result |
|---|---|
| Dataset exists / required OHLCV fields | BLOCKED — no dataset to inspect |
| Dataset hash, source manifest and content-addressed provisioning manifest | NOT_CREATED |
| Dataset-scoped security/calendar/action/PIT evidence package | NOT_CREATED; current mapping lead and native contract references documented above |
| Rights policy/evidence/admission | Recorded as unverified / WARN_ONLY / warning, not approval |
| Raw data outside Git | No raw data added; `git check-ignore -v` confirms planned CSV/source/provisioning paths match `.gitignore` `/data/` |
| Features/labels, qualification, fits, walk-forward and paired metrics | None performed |
| Provider/quote/broker calls and public capability changes | None |
| Previous HOLD/audit and rights-policy record | Byte hashes unchanged |
| Pre-existing tracked working diff | Unchanged; only this untracked document added |
| `git diff --check` and new-document whitespace/link/fence checks | PASS |

No runtime source/test/dependency changes; no test suite or empirical qualifier
was run in this documentation-only preflight. The preceding pass's test counts
are not represented as new validation.

Original HOLD document byte hash:
`4b65f4c88665f1198535e837d70aa199443e08e4ebb337260ae499cce7839c79`.
Original audit byte hash:
`59be5223fc06dcdfb203f1e3a6ce0bfbd6d433804b31685ad9de2813cf54acee`.
Accepted rights-policy record entry byte hash:
`d26b42265df6d670b8ef7a0593466cdec611fc7de4da7582f3144da36873b348`.

Git recommendation: retain this small HOLD record for review with the existing
uncommitted work. Do not commit raw data or claim a completed provisioning
manifest. No tag; no commit/tag/push performed.

Exact next prompt title:

**TIAF A7 / FF-1.1A — SUPPLY LOCAL RELIANCE DAILY OHLCV EXPORT FOR PROVISIONING**

Only after provisioning completes should the next pass be titled
**TIAF A7 / FF-1.1A — EMPIRICAL QUALIFICATION RERUN**.
Empirical fitting remains unauthorized in either provisioning outcome.
