# TIAF_A1.2 Dhan Core Market-Data Adapter

## Scope and architecture

A1.2 is the first concrete implementation of the provider-neutral
`MarketDataProvider` contract. Dhan is the initial primary factual source for
quotes and OHLCV because its v2 data APIs support batched full quotes plus daily
and intraday history. “Primary” identifies the first adapter; it does not give
Dhan execution authority or leak Dhan payloads into downstream contracts.

```text
DhanMarketDataProvider
        |
        +-- DhanTransport protocol
        |       |
        |       +-- HttpxDhanTransport
        |
        +-- Dhan mapping and parsing functions
                |
                v
   QuoteSnapshot / HistoricalSeries
```

The adapter implements no orders, portfolios, positions, account mutation, or
other trading endpoints.

## Transport choice

A small direct `httpx` wrapper is used instead of the full `dhanhq` SDK. This
keeps trading-facing SDK features out of A1.2, limits the implementation to
documented read-only endpoints, and permits complete in-memory mocking through
an injected transport. HTTPX is constrained to `>=0.27,<1`.

The implemented endpoints are:

- `POST /v2/marketfeed/quote`
- `POST /v2/charts/historical`
- `POST /v2/charts/intraday`

The configured base URL already contains `/v2`, so internal transport paths are
`/marketfeed/quote`, `/charts/historical`, and `/charts/intraday`.

## Authentication and security

Set these environment variables without committing them:

```text
DHAN_CLIENT_ID=
DHAN_ACCESS_TOKEN=
```

`DhanConfig` stores the token as Pydantic `SecretStr`; configuration, transport,
and provider representations do not expose it. Errors contain only normalized
provider attribution and safe Dhan error code/message fields. Fixtures use fake
values only. Dhan documents manually generated access tokens as having a
24-hour validity; A1.2 does not generate, renew, or persist tokens.

## Security-ID boundary

Every provider request requires a positive numeric Dhan `securityId` in
`InstrumentKey.provider_instrument_id`. The A1.2 adapter itself does not guess
from a symbol. The current smoke utility now resolves and validates that
identity through the A1.5 instrument-master boundary before it invokes the
adapter; A1.2 still does not advertise `INSTRUMENT_MASTER`.

## Segment mappings

| TIAF segment | Dhan `exchangeSegment` |
|---|---|
| `NSE_EQUITY` | `NSE_EQ` |
| `NSE_FNO` | `NSE_FNO` |
| `NSE_INDEX` | `IDX_I` |
| `BSE_EQUITY` | `BSE_EQ` |
| `BSE_FNO` | `BSE_FNO` |
| `BSE_INDEX` | `IDX_I` |

Dhan uses the same `IDX_I` value for index requests, so the normalized TIAF
identity retains whether the requested index is NSE or BSE.

## Historical instrument mappings

| TIAF type | Dhan historical value |
|---|---|
| `EQUITY` | `EQUITY` |
| `INDEX` | `INDEX` |
| `FUTURE` | explicit `FUTIDX` or `FUTSTK` |
| `CALL_OPTION`, `PUT_OPTION` | explicit `OPTIDX` or `OPTSTK` |

The A1.1 identity cannot reliably distinguish index and stock derivatives. A1.2
therefore accepts an explicit security-ID-to-Dhan-type mapping for historical
requests and rejects ambiguity rather than inspecting symbol text.

## Quote normalization

Full quotes are grouped by Dhan segment and sent in chunks of at most 1,000
instruments. Output follows caller order even if response keys do not. A missing
segment or security ID raises `InstrumentNotFoundError`; a shorter tuple is never
returned silently.

The adapter maps LTP, OHLC, volume, OI, and positive best bid/ask levels into
`QuoteSnapshot`. Dhan OHLC `close` is treated as `previous_close` according to
the quote API's prior/market-close semantics. Empty depth does not fabricate a
price. Availability and quality reflect populated optional fields; freshness is
`UNKNOWN` because A1.2 defines no market TTL.

A valid Dhan `last_trade_time` from year 2000 onward becomes `observed_at`.
Missing, malformed, or sentinel-era values fall back to the actual injected
retrieval timestamp and record that choice in safe metadata. `received_at` is
captured after the response. Both normalize to `Asia/Kolkata`.

## Historical normalization

| TIAF interval | Dhan interval/endpoint |
|---|---|
| `1d` | daily `/charts/historical` |
| `1m` | `1` |
| `5m` | `5` |
| `15m` | `15` |
| `25m` | `25` |
| `60m`, `1h` | `60`, normalized as `1h` |

Provider parallel arrays are length-checked before indexing; no `zip()`
truncation occurs. Epochs are normalized to `Asia/Kolkata`, bars are sorted,
and duplicate starts are rejected by `HistoricalSeries`. OI is retained when
present and otherwise remains `None`.

Intraday boundaries use the returned candle start plus the requested minute
duration. Daily values use the provider epoch's India trading date with
calendar-midnight-to-calendar-midnight boundaries, avoiding fabricated market
session times. Dhan's daily `toDate` remains non-inclusive. Input ranges are not
silently altered. Intraday ranges above the documented 90-day request maximum
fail explicitly; automatic chunk/rate orchestration belongs to the Data Service.

## Error translation

| Failure | TIAF error |
|---|---|
| HTTP 401/403; Dhan auth/token codes | `ProviderAuthError` |
| HTTP 429; Dhan rate-limit codes | `ProviderRateLimitError` |
| HTTPX timeout | `ProviderTimeoutError` |
| HTTPX connection/request failure | `ProviderNetworkError` |
| Dhan invalid `securityId` code | `InstrumentNotFoundError` |
| Unsupported interval, segment, or unresolved derivative subtype | `UnsupportedCapabilityError` |
| Non-JSON, malformed, inconsistent, or invalid normalized response | `ProviderBadResponseError` |

No access token is included in exception detail or representation.

## Tests

Unit tests use injected recording transports and `httpx.MockTransport`; they
perform no network calls. Official response shapes are represented with small,
deterministic fixtures containing no credentials. Coverage includes mappings,
quote depth, OI, batching, chunking, missing instruments, every supported
interval, daily boundaries, array-length validation, sorting, duplicates,
timezone normalization, error translation, protocol conformance, secrecy, and
JSON round trips.

## Optional real read-only smoke test

After setting current credentials, resolve a symbol and request exactly one
quote:

```bash
python scripts/dhan_market_data_smoke.py \
  --symbol RELIANCE
```

The script calls only the full-quote data endpoint and prints normalized JSON.
It refuses to run without credentials and never prints them. It is not part of
pytest. `--security-id` remains available for diagnostics, but if both symbol
and ID are supplied they must resolve to the same master identity before any
provider request occurs.

### Live-validation identity correction

Earlier A1.2/A1.3/A1.4 smoke invocations paired the caller label `RELIANCE`
with security ID `1333`. Subsequent A1.5 master validation on 2026-09-06 showed
that current Dhan identities are `1333 = HDFCBANK` and `2885 = RELIANCE`. The
earlier transport and factual data-path validation remains valid for ID 1333,
but its displayed RELIANCE label was incorrect. Current smoke utilities resolve
symbols and refuse symbol/ID mismatches before provider transport.

## Capabilities, limitations, and next target

A1.2 advertises only `QUOTES` and `HISTORICAL_OHLCV`. It deliberately excludes
instrument-master search, rich partial batch results, retry/sleep policy,
streaming, full-depth preservation, option chain, Greeks, IV analytics, expired
options, caches, persistence, agents, ranking, trading decisions, TradeMonitor,
and Google Sheets.

The next target, **TIAF_A1.3**, extends Dhan derivatives data capability without
crossing into execution or trading logic.

Official references: [Dhan market quote](https://dhanhq.co/docs/v2/market-quote/),
[historical data](https://dhanhq.co/docs/v2/historical-data/),
[instrument list](https://dhanhq.co/docs/v2/instruments/), and
[authentication](https://dhanhq.co/docs/v2/authentication/).
