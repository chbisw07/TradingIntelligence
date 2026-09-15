# TIAF A7 / FF-0.4 — Engineering CLI and Acceptance Hardening

## 1. Scope and checkpoint

2026-09-15, Asia/Kolkata. This implements the final bounded FF-0 step; the
[final acceptance record](TIAF_A7_FF0_ACCEPTANCE.md) owns the verdict and quality
results. Entry was clean at `1a61cb7` (`feat(a7.ff0.3): implement baserate cold
runtime and pinned verification`). A6 remains frozen at `tiaf-a6-baseline`,
commit `6dc2ff304aae0e87540260b092919bb91e4d4189`. No commit/tag/push was performed.

Authority is the [accepted miniature plan](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md)
§§13–18 and the FF-0.4 request. Reviewed prerequisites include the
[FF-0.1](TIAF_A7_FF0_1_CONTRACTS_TARGET_CLOCK_IMPLEMENTATION.md),
[FF-0.2](TIAF_A7_FF0_2_CAPTURE_STORE_TRUTH_RECORDED_REPLAY_IMPLEMENTATION.md),
[FF-0.3](TIAF_A7_FF0_3_BASERATE_COLD_RUNTIME_PINNED_VERIFICATION_IMPLEMENTATION.md)
implementation records, accepted A7/FF architecture and acceptance, TI Shell,
capability governance and R1–R5. Historical records/architectures/theses and the
deferral register are unchanged. No FF-1, training, calibration, model approval,
live calls, advanced families or A8 is implemented.

Public-capability decision: **INTERNAL_ENGINEERING_CLI_ONLY**. The nine-operation
catalog, public parser/dispatcher, R5 bootstrap and existing consumers do not
change. Accepted architecture schedules public projection separately after FF-2.

## 2. Small command adapter, existing owners

```text
scripts/forecast_miniature.py
  → existing Shell _Parser + argument-safety utilities
  → typed EngineeringCommand + strict trusted config/registered packet
      run        → existing FF-0.3 COLD owner → result/capture → FF-0.2 store
      outcome    → existing independent Evaluation labeler → Outcome Journal
      link       → exact Evaluation link + one-link Ledger snapshot
      inspect    → existing stored capture + exact persisted links
      replay     → validate/read stored capture only
        --verify → existing pinned verifier → separate usage/report, no append
```

Plan §16 chooses one internal script with `run/outcome/link/replay --verify`.
`inspect` is justified by the request's immutable metadata/linkage inspection.
No separate simulate/verify verb or second interactive CLI is needed. There is
no REPL, so one-shot/REPL dispatcher parity is not applicable. Reusing the public
capability dispatcher would publish an unauthorized capability; the adapter
reuses the existing Shell parsing/safety seam without altering its grammar.

New `engineering_inputs.py` defines frozen, extra-forbidden, versioned packet
contracts: ForecastInput contains the explicit COLD config, count artifact,
request, snapshot, build and source shelf; OutcomeInput contains only independent
target/window/terminal/check evidence and its source shelf. Public request
semantics remain unchanged. Input registration IDs are distinct from the
embedded forecast request IDs, both retained without rewriting scientific identity.

New `engineering.py` admits packets and projects allowlisted JSON summaries;
it contains no forecasting algorithm. Store's only addition is read-only
`get_forecast_links(run_id)`, which checks current access/retention rights before
returning exact persisted links. There is no latest-truth join or implicit re-label.

## 3. Operator guide

Use the repository's installed editable package/virtual environment. Everything
below is **synthetic engineering**, not current market data or financial advice.

### Explicit local configuration

Review `tests/fixtures/forecasting/ff0/local_config.json` before using it. Its
`input_root` is relative to that config's parent; it registers four filenames,
logical IDs, kinds and semantic fingerprints. Its explicit `corpus_root` is
`/tmp/tiaf-ff0-miniature`. There is **no CLI default corpus**. If that directory
already contains data, preserve it; use a separately reviewed config with an
unused, disjoint output directory for a fresh exercise. When relocating config,
set `input_root` to the absolute fixture directory or a correctly relative root.
No `.env`, credentials or API access is required or read.

```bash
.venv/bin/python scripts/forecast_miniature.py --help
.venv/bin/python scripts/forecast_miniature.py run \
  --config tests/fixtures/forecasting/ff0/local_config.json \
  --input ff-request:reliance-s21-simulated
```

Expected: `GENERATED`, support 20, probability 0.6, calibration RAW, validity
UNKNOWN, synthetic basis, SIMULATED_ISSUANCE, historical as-of/cutoff and real
current `computed_at`, no `issued_at`. Copy the returned `run_id` exactly.
Do not substitute the input or request ID for a run ID. Repeated `run` performs
another bounded attempt and creates a **new** capture, even with identical inputs.

### ACTUAL and insufficient support

```bash
.venv/bin/python scripts/forecast_miniature.py run \
  --config tests/fixtures/forecasting/ff0/local_config.json \
  --input ff-request:reliance-s21-actual
.venv/bin/python scripts/forecast_miniature.py run \
  --config tests/fixtures/forecasting/ff0/local_config.json \
  --input ff-request:reliance-s21-insufficient
```

The checked-in ACTUAL target opens **2026-02-05T09:15:00+05:30**. Invoked today,
it must persist UNAVAILABLE / TEMPORAL_INELIGIBLE, no estimate, no fake issue,
zero inference attempts. Timely ACTUAL golden tests use a trusted test clock at
2026-02-04T16:06:00+05:30. They prove mechanics, not a historical deployment.
There is no production `--now`, `--issued-at` or clock override. A genuinely
timely ACTUAL exercise requires separately prepared/admitted evidence and
configuration, not editing dates to make this example attractive.

The insufficient SIMULATED packet has 19 qualified transitions: UNAVAILABLE /
HISTORY_SUPPORT_INSUFFICIENT, no probability and one attempted BaseRate call.
Do not replace absence with 0, 0.5, NO_TRADE or a successful forecast.

### Independent truth and linkage

```bash
.venv/bin/python scripts/forecast_miniature.py outcome \
  --config tests/fixtures/forecasting/ff0/local_config.json \
  --input ff-outcome-input:reliance-s21-up
```

Expected independent synthetic label 1. Copy the returned `outcome_id`. Replace
`RUN_ID` and `OUTCOME_ID` below with returned IDs; these words are placeholders.

```bash
.venv/bin/python scripts/forecast_miniature.py link \
  --config tests/fixtures/forecasting/ff0/local_config.json \
  --run RUN_ID --outcome OUTCOME_ID
.venv/bin/python scripts/forecast_miniature.py inspect \
  --config tests/fixtures/forecasting/ff0/local_config.json --run RUN_ID
.venv/bin/python scripts/forecast_miniature.py replay \
  --config tests/fixtures/forecasting/ff0/local_config.json --run RUN_ID
.venv/bin/python scripts/forecast_miniature.py replay \
  --config tests/fixtures/forecasting/ff0/local_config.json --run RUN_ID --verify
```

Link persists the **exact** outcome revision and a one-link immutable Ledger
snapshot. A generated synthetic case is ENGINEERING_LINK_ELIGIBLE, not an
empirically approved observation; absent forecasts link as NOT_EVALUABLE.
Labeling is independent of inference. No current-target truth becomes support.
Inspection lists persisted links, not a guessed latest outcome or metric.

Do not blindly retry `outcome` or `link`: these are append operations, not reads.
The CLI labels a first revision only; a duplicate first revision conflicts rather
than silently overwriting or automatically revising truth. Existing typed
Evaluation revision APIs remain available to separately governed callers. Link
and Ledger appends are individually safe but **not a multi-record transaction**;
if the second append fails, a valid first link can remain. Inspect retained
history and resolve through a reviewed procedure, never automatic repair/delete.

### Test manifests versus persisted corpus

```text
tests/fixtures/forecasting/ff0/
  local_config.json                 explicit config, not a run
  reliance-s21-*.json                registered input packets
  *_cases.json                      historical test manifests
tests/acceptance/ff0/
  corpus_manifest.csv               28 test requirements → pytest nodes
  golden_results.json               expected test-clock results

<explicit output corpus>/
  artifacts/<content-hash>.json      captured dependency closure
  forecast_runs.jsonl                immutable captured runs
  outcome_records.jsonl              independent truth revisions, when appended
  evaluation_links.jsonl             exact links, when appended
  ledger_snapshots/<hash>.json        immutable snapshots, when appended
```

The manifests are run via pytest, **not** passed as runtime inputs or a replay
corpus. `replay --run` reads persisted runs under the selected config root.
Temporary demo corpora are retained for inspection; `/tmp` is not durable storage.

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_engineering_cli.py -k golden
.venv/bin/pytest -q -s tests/acceptance/ff0
```

## 4. Failure mapping and admission

| Exit | Meaning | Examples |
|---|---|---|
| 0 | Operation completed; inspect domain status | GENERATED, UNAVAILABLE, inspect, recorded replay, VERIFIED |
| 2 | COMMAND_CONFIG_ADMISSION | Bad grammar/IDs, unregistered/wrong-kind packet, malformed config/schema/mode, unsafe path, leakage/backdating, input size denial |
| 1 | INTEGRITY | Registered fingerprint mismatch, corrupt/re-sealed incompatible history, unknown exact implementation binding |
| 1 | PERSISTENCE_ACCESS | Existing store's access/rights/bounds failure, lock/residue, storage failure |
| 1 | EXECUTION or typed FAILED result | Unexpected local execution failure, cooperative deadline exceeded |
| 1 | Typed verification report | MISMATCH or UNVERIFIABLE; recorded replay may still succeed independently |

Messages are code-owned, generic and stable: no exception text, source bodies,
secrets, user argument echoes or physical path dumps. Verification failures keep
the native exact reason/fingerprints; do not collapse them into domain absence.
Parser limits 16 tokens / 4096 characters per token; only explicit local config
paths and registered logical IDs are accepted. URLs, traversal, import/model
paths as IDs, credentials, arbitrary fields, abbreviations, duplicate/unsafe
options and executable configuration are rejected.

Config/input reads require regular single-link files, reject symlinks, FIFOs,
duplicate JSON keys/nonfinite data/secret fields and enforce 1 MiB per file.
At most 64 registrations, 256 artifact shelf entries; roots must be disjoint.
Existing corpus limits remain 256 records per journal/closure and 32 MiB total,
64 supplied schedule/history bounds, no truncation, repair or implicit fallback.
This is a trusted local single-writer operator seam, **not a security sandbox
against a hostile concurrent filesystem owner** or a deployment service.

## 5. Clocks, identity, observability and resource accounting

All timestamps remain aware, normalized with `ZoneInfo("Asia/Kolkata")`, serialized
with `+05:30`; naive times reject. Native runtime owns computation/issue; SIMULATED
keeps explicit historical as-of and cutoff, later real computation and no issue.
All old source/result/fingerprint contracts remain unchanged. Package `0.1.0`,
contract schema `1.0`, target/forecaster versions and content identities are
separate concepts. The new engineering envelopes each declare schema ID / `1.0`.

Each result projects operation, request/run/result/capture IDs, subject/target,
mode/basis, all relevant clocks, support/estimate/absence, raw calibration/validity,
source refs, artifact/config/composition pins and fingerprints, limitations and
NO_ACTION_AUTHORITY. It does not dump raw provider/source payloads.

`original_usage` is historical inference usage, **not another replay charge**.
Recorded replay/inspect do no inference; pinned verification reports its one
separate attempt under `verification.usage`, never edits original usage or emits
a new forecast. Native monotonic `duration_seconds` measures inference/verifier
work, not end-to-end CLI startup/disk latency. Local cost stays UNPRICED; external
provider/model calls, model input/output tokens and model cost stay zero.
The one-second deadline is cooperative detection, not hard process interruption;
no hard-timeout infrastructure or invented currency price is added.

## 6. Acceptance evidence and limitations

See the [final 28-case matrix and gate results](TIAF_A7_FF0_ACCEPTANCE.md).
Before this pass FF0-26 import/authority and FF0-27 resource/log handling were
partial; FF0-28 operator workflow was pending. New CLI tests complete these
through real command dispatch, temporary corpora, blocked imports/network and
sentinel private errors. Other 25 cases are rerun, not redefined.

Four goldens cover timely ACTUAL, later SIMULATED, n=19 absence and tamper.
The fourth constructs a tampered **temporary** record with a recomputed envelope
hash: recorded replay can faithfully read those bytes, but the pinned primitive
reconstructs 0.6 versus the altered 0.7 and reports MISMATCH, exit 1. Missing
exact verifier gives UNVERIFIABLE, not fallback. Both leave original records
unchanged. Simple broken hashes, missing closure, corrupt outcome/run journals,
partial JSONL, locks, I/O failure, malformed profiles/modes, future cutoff and
duplicate executions also fail without repair or silent success.

No optional ML/LLM/FM/provider/broker SDK is needed. Fresh-process tests block
imports and sockets; recorded-replay tests additionally block runtime, support,
forecasters, input packet loading and labeler imports. Public discovery remains
nine; the public Shell rejects `forecast run`. Frozen A2/A6 source is untouched.

Still absent: empirical dataset/PIT qualification, learning grants, model fit,
paired metrics/calibration, uncertainty estimates, lifecycle/approval/shadow,
advanced families, public publication and consumer/execution integration. FF-0
is an engineering benchmark, not a proven predictor. FF-1 needs a **planning**
request and reviewed protocol/rights/data/split/dependency gates before fitting.
