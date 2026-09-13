# A6 Acceptance Corpus

This directory is the bounded synthetic freeze-readiness corpus for TIAF A6.
It contains no live recommendation, provider credential, broker state or
production capture.

## Inventory

- `corpus_manifest.csv` maps all 93 required case IDs to an explicit scenario,
  expected result, policy/profile, fixture or logical artifact, test location
  and coverage category.
- `golden_public_results.json` records stable semantic expectations for all five
  canonical dispositions through the public `expression.assess` path. It avoids
  snapshots of run IDs, elapsed time and human formatting. Selected candidates,
  rank-difference dimensions, key candidate rejection reasons, gaps, blockers
  and invalidations remain explicit. A fingerprint is required to match the
  exact assessment embedded in the captured artifact.
- `test_a6_acceptance_corpus.py` validates manifest completeness and referenced
  tests, runs the five public goldens through Shell → facade → A6, round-trips
  JSON, checks explain/trace, replays every golden capture, rejects a composition
  mismatch and proves exact fixed-capture replay across hash-seed/environment
  changes.

## Categories

| Category | Cases |
|---|---:|
| Upstream admission | 8 |
| Timing/freshness | 9 |
| Coverage/absence | 6 |
| Candidate geometry | 9 |
| Liquidity/quote quality | 13 |
| Premium | 4 |
| Events | 6 |
| Ranking | 8 |
| Dispositions | 5 |
| Alternatives/evaluation retention | 4 |
| Replay/integrity | 8 |
| Public surface | 13 |
| **Total** | **93** |

The manifest references focused A6.1–A6.3 regression tests plus the A6.4 edge
hardening tests. Domain-level tests own contract and ranking primitives; cases
whose acceptance claim is specifically public-path behavior point to this
directory or to the governed facade/Shell tests.

## Run

```bash
pytest -q tests/acceptance/a6
```

All inputs are captured or programmatically synthetic. The corpus must open no
provider/model/broker connection, and recorded replay must not consult current
wall clock, environment-selected policy, expanded registry state or the network.
