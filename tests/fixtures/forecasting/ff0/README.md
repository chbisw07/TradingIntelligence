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
their golden fingerprints are unchanged. The complete 28-case CLI acceptance
remains FF-0.4, not delivered here.

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
