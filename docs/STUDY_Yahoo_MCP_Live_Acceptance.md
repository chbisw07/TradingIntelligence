# Yahoo MCP Live Acceptance

## Result

**Status:** `READY_TO_ACCEPT_YAHOO`  
**Latest corrected live run:** `2026-09-10T01:40:49.398929+05:30`  
**Command:** `python scripts/yahoo_live_acceptance.py --live`  
**Live Yahoo calls performed:** `10`

The mapping/status correction is implemented, deterministically verified, and
live-validated through the repository virtual environment's `uvx`. All ten
bounded calls were accepted, every replay and semantic-fingerprint check passed,
and no API key or token was required.

## Acceptance history

### Local preflight attempt — 2026-09-10T01:09:52+05:30

The initial local attempt stopped before transport because `uvx` was absent.
Live Yahoo calls: 0. No live evidence or replay artifact was produced.

### Live mapping diagnostic — timestamp not supplied

The subsequently reported bounded live run reached the real Yahoo MCP server
and observed FastMCP/Yahoo server version 4.0.3. Transport, connector lifecycle,
provider provenance, canonical-symbol isolation, serialization, fingerprints,
and offline replay worked. The run remained `HOLD` because TIAF parsed the
FastMCP structured `result` wrapper as the Yahoo payload itself:

- all four profile calls returned `SUCCESS`, but each retained one native
  wrapper observation and emitted no canonical evidence;
- RELIANCE and ATHERENERG financials were falsely `OUT_OF_COVERAGE`;
- RELIANCE news was falsely `OUT_OF_COVERAGE`;
- earnings dates were exercised through the semantically incorrect
  `READ_CORPORATE_ACTIONS` capability;
- recommendations remained valid `PARTIAL` empty evidence; and
- the deterministic Tapetide-rate-limit route selected Yahoo, but its company
  name projection was absent.

These were adapter/capability-mapping defects, not Yahoo transport failures.

### Corrected local retry — 2026-09-10T01:32:14+05:30

The adapter now decodes the string-valued FastMCP `result` envelope before
profile, financial, earnings, or news parsing. Valid empty collections/provider
empty messages become `PARTIAL` evidence rather than false coverage failures.
Profile name, sector, industry, description, and other explicitly safe mappings
can emit canonical evidence. Earnings now use additive
`READ_EARNINGS_CALENDAR` under the existing `READ_FILINGS` authority ceiling.

The real corrected rerun could not start because this environment still lacks
`uvx`. Live Yahoo calls: 0; all ten corrected-run calls were skipped.

### Corrected bounded live acceptance — 2026-09-10T01:40:49.398929+05:30

The project virtual environment supplied `uvx` and started Yahoo Finance MCP
Server 4.0.3. The script completed its exact ten-call ceiling. All four company
profiles, both financial statements, earnings calendar, and news returned
`SUCCESS`; empty analyst recommendations returned valid `PARTIAL` evidence.
The deterministic Tapetide `RATE_LIMITED` fixture permitted fallback, Yahoo was
selected, and canonical company-name evidence was returned.

All accepted results preserved Yahoo provenance and provider-neutral canonical
symbols. Serialization and reconstruction occurred after the live connector
closed, with exact evidence and semantic fingerprints for every call and the
fallback result.

## Bounded matrix

The script authorizes exactly ten Yahoo calls:

| Scope | Symbols | Calls |
|---|---|---:|
| Company profile | RELIANCE, HDFCBANK, KAYNES, ATHERENERG | 4 |
| Annual income financials | RELIANCE, ATHERENERG | 2 |
| Earnings dates/EPS history | RELIANCE | 1 |
| News | RELIANCE | 1 |
| Optional analyst recommendations | RELIANCE | 1 |
| Yahoo fallback after deterministic Tapetide rate limit | RELIANCE | 1 |

The fallback primary is explicitly an in-memory deterministic fixture. It does
not manufacture or claim a live Tapetide failure.

## Acceptance evidence

The runnable path uses the existing `YahooMcpClient`,
`YahooMarketIntelligenceProvider`, provider registry, provider-neutral router,
normalizer, and immutable `MarketIntelligenceRun` contracts. After the connector
closes, each serialized run is reconstructed offline and checked for exact run
fingerprint, canonical evidence, and semantic-fingerprint equality. It also
checks provider provenance, canonical symbol isolation, conservative financial
mapping, factual earnings, unsentimented news, valid empty recommendations, and
provider import isolation.

The injected script regression proves the complete bounded control flow and
exact ten-call ceiling without network access. Existing routing tests prove the
same `RATE_LIMITED -> Yahoo` policy path. The corrected real-MCP run confirms
those deterministic paths against the live server.

## Observations from the corrected live run

- Yahoo MCP server: Yahoo Finance MCP Server 4.0.3.
- Live calls: 10; 9 `SUCCESS`, 1 valid-empty `PARTIAL`, 0 failures/skips.
- Latency: 6.479 seconds total; 0.671 median; 0.232 minimum; 1.168 maximum.
- Profiles: canonical evidence emitted for RELIANCE, HDFCBANK, KAYNES, and
  ATHERENERG while Yahoo ticker suffixes remained adapter-local.
- Financials: both calls emitted canonical facts while 382 uncertain native
  facts remained protected by provider-defined/ambiguous semantics.
- Earnings: 12 factual events retained dates and supplied EPS fields without
  probability or forecast invention.
- News: 5 events retained provenance and timestamps without invented sentiment.
- Recommendations: empty provider result correctly remained `PARTIAL` and was
  not counted as failure.
- Replay: exact canonical evidence and semantic fingerprints for every result.
- Fallback: deterministic Tapetide `RATE_LIMITED` to live Yahoo passed.
- Secrets: none required, read, or printed.

## Deterministic validation

- `pytest -q tests/unit/market_intelligence`: 110 passed.
- `pytest -q`: 1,661 passed.
- The script-specific three-test selection proves safe no-live behavior,
  missing-`uvx` preflight, and the complete injected ten-call control flow.
- `python -m compileall src scripts`: passed.
- `ruff check src tests scripts`: passed.
- `mypy src tests`: passed for 386 source files.
- `git diff --check`: passed.

Final acceptance is `READY_TO_ACCEPT_YAHOO`.
