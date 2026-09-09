# Yahoo MCP Secondary Provider Evaluation

## Status

**Recommendation:** `KEEP_AS_SECONDARY_PROVIDER`  
**Implementation base:** `tiaf-a3.6.1` (`b4c030e`)  
**Deterministic integration:** complete  
**Bounded live acceptance:** `READY_TO_ACCEPT_YAHOO`; corrected ten-call live
matrix and exact offline replay passed on 2026-09-10

Yahoo Finance via the standalone yfinance MCP is integrated behind the frozen
A3.6.1 provider-neutral contracts. It is a low-cost secondary/fallback and
corroboration source, not an authoritative source of Indian company truth.
Tapetide remains the preferred structured India-specific source.

## Implemented scope

The connector launches the previously evaluated read-only server with:

```text
uvx --from git+https://github.com/mobatmedia/yfinance-mcp yfinance-mcp
```

Only these tools cross the allowlist:

- `yfinance_get_stock_info` for company identity/profile and valuation context;
- `yfinance_get_stock_financials` for income, balance-sheet, and cash-flow
  statements over quarterly or annual periods;
- `yfinance_get_earnings_dates` for event dates, EPS estimates, reported EPS,
  and explicit surprise percentages;
- `yfinance_get_stock_news` for secondary news discovery; and
- `yfinance_get_stock_recommendations` as a deliberately non-blocking optional
  source. An empty recommendation history is valid empty evidence.

Yahoo options, historical OHLCV, multiple quotes, and ticker search are omitted.
They are redundant with current TIAF responsibilities or would broaden this
follow-up beyond its evidence-fallback purpose.

## Identity and provider boundary

Symbol translation is explicit and local to the adapter:

| Canonical TIAF symbol | Yahoo ticker |
|---|---|
| `RELIANCE` | `RELIANCE.NS` |
| `HDFCBANK` | `HDFCBANK.NS` |
| `KAYNES` | `KAYNES.NS` |
| `ATHERENERG` | `ATHERENERG.NS` |

No suffix is guessed. An unregistered canonical symbol returns a typed
`UNKNOWN_SYMBOL`/`OUT_OF_COVERAGE` result before transport. Yahoo tickers remain
provider metadata; canonical subjects retain their TIAF identity.

MCP SDK types, `uvx`, session/process management, tool names, and native response
shapes are confined to the Yahoo provider package. Specialists and canonical
contracts import none of them. Child stderr is suppressed so banners and logs
cannot become provider evidence.

## Normalization and provenance

All usable scalar values first become `ProviderNativeObservation` records with
the Yahoo ticker, provider tool, native field/path, acquisition time, provider
source reference, payload checksum, and conservative point-in-time limitation.

The small accepted mapping set includes company name, description, currency,
current price, market capitalization, trailing PE, sector, industry,
`Total Revenue`, and `Net Income`. `forward_pe` and every unknown financial label remain
provider-defined or ambiguous and cannot emit canonical evidence. Financial
publication times are not supplied by the MCP, so statements are available only
from acquisition time and are not represented as historical point-in-time
truth.

Yahoo earnings use the additive provider-neutral `READ_EARNINGS_CALENDAR`
capability and existing `NormalizedEvent`. This avoids misclassifying an
earnings-date calendar as a corporate action or earnings-call summary while
retaining the existing `READ_FILINGS` authority ceiling. Event date, EPS
estimate, reported EPS, and explicitly supplied surprise percentage remain
facts. A separately returned `next_earnings_date` still produces an upcoming
event when history is empty. No price, success, or target probability is
inferred.

FastMCP 4.0.3 exposes these string-returning tools through a structured
`result` wrapper whose value is the JSON document. The adapter unwraps and
decodes that transport envelope before capability-specific parsing. Valid empty
financial, news, earnings-calendar, and recommendation results remain `PARTIAL`
empty evidence; they are not classified as `OUT_OF_COVERAGE`. That status is
reserved for explicit coverage/symbol signals.

Yahoo news becomes provider-neutral event evidence with headline, publisher,
URL, publication time when timezone-aware, canonical subject, and Yahoo
provenance. Missing sentiment remains missing. A provider-independent underlying
event key is retained for later A3.5 clustering; agreement is not automatically
treated as independent confirmation.

## Routing and failure behavior

`yahoo_secondary_route_policy` configures Tapetide then Yahoo for profile,
financials, valuation, news, and optional analyst evidence. The existing route
policy remains authoritative: rate-limited or unavailable Tapetide results can
fall back to Yahoo, while a policy excluding that failure status stops without a
Yahoo call. Earnings use Yahoo as the single primary because Tapetide declares
the equivalent capability unsupported.

Multi-source mode preserves both providers' observations. Differences create
the existing unresolved contradiction group; values are neither overwritten nor
averaged. If both sources fail, the run contains typed failures and no evidence.

## Limitations

- Yahoo/yfinance uses unofficial endpoints whose coverage, latency, schema, and
  rate-limit behavior may change.
- India-specific financial semantics may differ from official exchange/company
  filings and from Tapetide labels.
- Historical statement publication time and revision lineage are not supplied.
- News is a secondary discovery channel, not authoritative relevance or
  sentiment evidence.
- Yahoo/yfinance live behavior remains externally mutable and should continue to
  be guarded by the bounded acceptance and conservative mapping tests.

The bounded acceptance entry point is:

```bash
python scripts/yahoo_live_acceptance.py --live
```

It performs the nine-call profile/financial/earnings/news/recommendation matrix,
then one Yahoo fallback call after a deterministic Tapetide rate-limit fixture.
Without `--live` it performs no external work; without `uvx` it stops at
preflight. Detailed run status is recorded in
[`STUDY_Yahoo_MCP_Live_Acceptance.md`](STUDY_Yahoo_MCP_Live_Acceptance.md).

The deterministic adapter, routing, contradiction, event, security, and offline
replay tests establish architectural fitness. The complete market-intelligence
selection passed 110 tests, and the complete repository passed 1,661 tests. The
compile, Ruff, mypy (386 source files), provider-isolation, and diff-whitespace
checks also passed. The corrected bounded live run made ten calls: nine returned
`SUCCESS`, empty analyst recommendations returned valid `PARTIAL`, the
deterministic rate-limit fallback selected Yahoo, and all offline replay and
semantic-fingerprint checks passed.
