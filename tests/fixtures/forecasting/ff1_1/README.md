# FF-1.1 authored qualification specimens

These cases are built programmatically by
[_research_support.py](../../../unit/forecasting/_research_support.py) and varied
by the [qualification tests](../../../unit/forecasting/test_research_qualification.py)
and [isolation/edge tests](../../../unit/forecasting/test_research_isolation_edges.py).
They are not an empirical dataset, source-rights certificate, real NSE session
calendar, runnable replay corpus, trained model or performance benchmark.

The clean authored sequence contains 32 sessions, exact decimal prices 100–131,
volumes 100–131 and explicit synthetic master/calendar/action/rights knowledge.
At reference index 20 the 21-input A2 feature window is complete. Expected
population: 32 requested, 11 eligible, 20 insufficient-lookback exclusions and
one terminal-next-session exclusion. Additional capture copies never add weight.

Coverage: missing/duplicate/conflicting sessions; invalid OHLC; finite scalar
admission; zero/missing/invalid volume; action uncertainty/adjusted basis;
wrong/ambiguous/derivative identity; stale knowledge and future-price leakage;
insufficient history; existing Ground Truth class 1, class 0 and exact ties;
calendar exceptions; fingerprints, serialization and isolation.

From the repository root:

```bash
.venv/bin/pytest -q tests/unit/forecasting/test_research_qualification.py \
  tests/unit/forecasting/test_research_isolation_edges.py
```

No downloads, live provider calls or model fitting. The test exercising the
`QUALIFIED_CAPTURE` vocabulary still uses authored values and is not a claim
of qualified empirical evidence. See the
[implementation record](../../../../docs/TIAF_A7_FF1_1_DATA_QUALIFICATION_FEATURE_SCHEMA_IMPLEMENTATION.md)
for the independent empirical gate.
