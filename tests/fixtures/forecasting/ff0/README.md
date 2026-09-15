# FF-0 synthetic foundation, capture and runtime fixtures

`foundation_cases.json` is a test-case manifest, not a persisted forecast corpus.
`tests/unit/forecasting/_support.py` constructs the corresponding target, three
supplied sessions S20–S22, exact reference price, provenance references and
request/result specimens. All facts and clock histories are synthetic.

The original foundation cases remain unchanged. `capture_cases.json` adds the
ten FF-0.2 acceptance scenarios and pins two capture-envelope fingerprints;
it too is a **test manifest, not a runnable replay corpus**. The helper
`tests/unit/forecasting/_capture_support.py` constructs complete captured
synthetic artifact closures and independent terminal observations in memory.
Store tests write only to `tmp_path`, never these checked-in files.

No actual issuer/exchange evidence, learned fit or historical deployment is
claimed. In the original foundation/capture specimens, 0.6 is an authored
contract example, not calculated inference. FF-0.2 tests persisted reconstruction and independently resolved
synthetic labels: reference 105, terminal 106/104/105 produces 1/0/0. Missing
terminal evidence has no label; revisions preserve the original bytes.
FF-0.3 adds `runtime_cases.json`: the exact 25-session/prior-label witness from
the accepted plan, twenty transitions and fourteen scenario descriptions.
It is also a **test manifest, not a runnable corpus**. `_runtime_support.py`
constructs the pinned counts/witness, explicit COLD config, input closure and
trusted test clocks. The runtime consumes those counts and really computes
12/20 = 0.6 (also 0/20 and 20/20), without fitting or acquiring data. Later
target truth stays a separate Evaluation operation. Original manifests and
their golden fingerprints are unchanged. FF-0.4 now completes the
[28-case CLI acceptance](../../../acceptance/ff0/README.md).

Run FF-0.3 BaseRate/runtime/pinned-verification tests with:

```bash
.venv/bin/pytest -q \
  tests/unit/forecasting/test_baserate_runtime.py \
  tests/unit/forecasting/test_pinned_runtime_replay.py
```

Run the capture/truth/link tests with:

```bash
.venv/bin/pytest -q \
  tests/unit/forecasting/test_capture_store_replay.py \
  tests/unit/evaluation/test_forecast_truth.py \
  tests/unit/evaluation/test_forecast_linkage.py
```

## FF-0.4 serialized engineering inputs

`local_config.json` explicitly registers four pinned JSON packets:

| Logical input ID | Packet | Meaning |
|---|---|---|
| `ff-request:reliance-s21-actual` | `reliance-s21-actual.json` | Synthetic ACTUAL, now-past target open; real-clock invocation must be UNAVAILABLE |
| `ff-request:reliance-s21-simulated` | `reliance-s21-simulated.json` | Historical SIMULATED request, raw 12/20 probability, computation now |
| `ff-request:reliance-s21-insufficient` | `reliance-s21-insufficient.json` | SIMULATED support n=19, explicit UNAVAILABLE without estimate |
| `ff-outcome-input:reliance-s21-up` | `reliance-s21-up.json` | Independent synthetic terminal evidence, label 1; no generation inputs |

These are data, not executable Python selectors. The configured input root is
this directory; the explicitly selected output root is `/tmp/tiaf-ff0-miniature`.
No CLI default selects that root. If it already contains a corpus, preserve it
and use a reviewed config with a separate output directory for a fresh exercise.
Do not run this config against important/shared data. No command deletes or repairs.

Follow the [operator guide](../../../../docs/TIAF_A7_FF0_4_ENGINEERING_CLI_ACCEPTANCE_HARDENING_IMPLEMENTATION.md#3-operator-guide).
The test manifests here and `tests/acceptance/ff0/corpus_manifest.csv` are **not**
`forecast_runs.jsonl` or replay inputs. The CLI accepts only registered input IDs
and exact persisted run/outcome IDs under the selected trusted config.
