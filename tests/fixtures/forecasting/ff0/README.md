# FF-0 synthetic foundation and capture fixtures

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

No actual issuer/exchange evidence, fitted BaseRate or historical deployment is
claimed. The 0.6 output remains an authored contract example, not calculated
inference. FF-0.2 now tests persisted reconstruction and independently resolved
synthetic labels: reference 105, terminal 106/104/105 produces 1/0/0. Missing
terminal evidence has no label; revisions preserve the original bytes.
The complete 25-session/prior-label count witness, execution and full 28-case
CLI acceptance remain the later FF-0.3/0.4 steps.

Run the capture/truth/link tests with:

```bash
.venv/bin/pytest -q \
  tests/unit/forecasting/test_capture_store_replay.py \
  tests/unit/evaluation/test_forecast_truth.py \
  tests/unit/evaluation/test_forecast_linkage.py
```
