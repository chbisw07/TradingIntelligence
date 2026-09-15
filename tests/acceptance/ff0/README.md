# FF-0 semantic acceptance corpus

This is an **executable test manifest**, not a persisted forecast/run corpus.
`corpus_manifest.csv` preserves all 28 IDs and names from the accepted FF-0 plan.
Each row names real pytest nodes. The driver runs their deduplicated union in
one offline subprocess, rejects errors/failures/skips, then checks every row
against executed JUnit results and against the plan's unchanged case names.

```bash
.venv/bin/pytest -q -s tests/acceptance/ff0
.venv/bin/pytest -q tests/unit/forecasting/test_engineering_cli.py -k golden
```

The first command reports 28 semantic assertions separately from the underlying
evidence-test count; overlapping tests are not extra independent cases. The
second runs four golden workflows: timely ACTUAL, later SIMULATED, insufficient
support, and re-sealed tamper detected by pinned verification. Golden result
fingerprints/capture IDs pin trusted test clocks and deterministic test IDs;
normal runs use current time/new IDs and need not equal those fixture hashes.
The tamper case changes only a temporary test corpus, never source fixtures.

`golden_results.json` records expected results, not runnable captures.
`_support.py` is test-only packet authoring. Production never imports it.
The serialized, registered inputs are in
[`tests/fixtures/forecasting/ff0`](../../fixtures/forecasting/ff0/README.md).
Packets pin the accepted serializer/build/dependency identity. Do not silently
regenerate them or change goldens to accommodate an incompatible environment.

The [operator guide](../../../docs/TIAF_A7_FF0_4_ENGINEERING_CLI_ACCEPTANCE_HARDENING_IMPLEMENTATION.md#3-operator-guide)
explains the explicit local config, input IDs, actual output corpus and command
exit meanings. The [acceptance record](../../../docs/TIAF_A7_FF0_ACCEPTANCE.md)
contains the final matrix and scope limitations. No live data, empirical
qualification, learned fit or public forecast capability is implied.
