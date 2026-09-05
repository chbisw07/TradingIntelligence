# TIAF_A1.3 Dhan Derivatives Data

## Purpose and boundary

A1.3 adds factual, read-only active-expiry discovery and complete live option
chains. It extends the direct `httpx` Dhan adapter and returns frozen,
provider-neutral contracts. It contains no recommendation, option selection,
pricing model, signal, order, position sizing, agent, or execution behavior.

The configured `/v2` base URL is used with:

- `POST /optionchain/expirylist`
- `POST /optionchain`

The Dhan adapter now advertises `QUOTES`, `HISTORICAL_OHLCV`,
`DERIVATIVES_METADATA`, and `OPTION_CHAIN`. A separate runtime-checkable
`DerivativesDataProvider` protocol keeps derivatives operations out of the
original core market-data interface.

## Normalized model inventory

- `OptionGreeks`: optional provider-reported delta, gamma, theta, and vega.
- `OptionMarketSnapshot`: one CE or PE contract with identity, prices,
  top-of-book, quantities, volume, OI, IV, Greeks, quality, and provenance.
- `OptionStrikeSnapshot`: at least one correctly keyed CE/PE side at one strike.
- `OptionChainSnapshot`: one underlying/expiry, spot LTP, and ascending unique
  immutable strikes.
- `ExpiryListSnapshot`: ascending unique immutable active dates.

`strikes` and `expiries` are tuples in Python. Normal list/JSON-array input is
accepted, JSON serialization emits arrays, and model reconstruction round-trips.
An empty chain or expiry list is representable only with explicit `UNAVAILABLE`
quality; a Dhan response claiming success with an empty result is rejected as a
bad response rather than silently converted.

## Identity and endpoint requests

The caller supplies the underlying Dhan security ID in
`underlying.provider_instrument_id`. Expiry discovery sends that value as
`UnderlyingScrip`, together with `UnderlyingSeg`. A chain request adds the
explicit ISO expiry date. No nearest expiry is silently selected.

Each returned CE/PE `security_id` is the option contract's ID and is also stored
in that option's `InstrumentKey.provider_instrument_id`. It is never confused
with the underlying ID. The normalized contract uses the underlying symbol and
exchange, the corresponding `NSE_FNO` or `BSE_FNO` segment, CE/PE type, expiry,
and strike. `trading_symbol` stays `None`; no exchange symbol is invented.

NSE and BSE index identities remain distinct in TIAF even though Dhan uses
`IDX_I` for each supported index request. Only consistent equity/equity-segment
and index/index-segment underlyings are accepted.

## Chain value semantics

Dhan's `data.last_price` becomes `underlying_ltp`, never an option premium. For
each available side, A1.3 maps LTP, previous close, average price, volume,
previous volume, OI, previous OI, best bid/ask and quantities, IV, and the four
Greeks. A CE-only or PE-only strike is valid; an entry with neither is invalid.

Greeks are transported exactly as returned. They are not recomputed or
"corrected." Missing values remain `None`, including an individually missing
Greek.

Dhan presents IV as a percentage-like number (for example `18.5`) but does not
give A1.3 a ratio contract. `implied_volatility` therefore preserves the
provider's numeric value exactly: there is no division by 100 or other unit
mutation. OI/volume current and previous values are stored independently; no
change or percentage features are calculated.

Positive bid and ask values must form a valid spread. Missing values remain
`None`. Dhan response fixtures use zero top price for no executable quote;
A1.3 normalizes that zero price and its paired quantity to `None`, preventing a
zero placeholder from being presented as market depth. Genuine positive prices
and zero or positive quantities are retained.

## Quality, freshness, and time

Quality is deterministic per option side:

- `GOOD`: LTP, volume, OI, IV, and all four Greeks are present.
- `PARTIAL`: LTP is present but one or more primary derivative values are absent.
- `DEGRADED`: LTP is absent but another usable market value is present.
- `UNAVAILABLE`: identification exists but no usable market value is present.

The chain reports the most severe usable child condition; it is `UNAVAILABLE`
only when no chain is usable. Missing one bid, ask, or Greek never makes the
whole chain unavailable.

Dhan's documented chain response has no per-chain market timestamp. A1.3 sets
both `observed_at` and `received_at` to the injected post-response acquisition
time and records `observed_at_source=retrieval_time`. Freshness is `UNKNOWN`
because this layer has no caller TTL. All timestamps are aware and normalized
with `ZoneInfo("Asia/Kolkata")`; JSON emits `+05:30`.

## Rate policy and errors

Dhan documents a special option-chain policy based on one unique request per
three seconds. The adapter does not sleep, serialize callers, retry, or cache.
The later shared Data Service can cache by `(underlying, expiry)` and schedule
calls with full workload context. HTTP/provider failures continue to translate
to typed authentication, rate-limit, timeout, network, not-found, unsupported,
or bad-response errors. Tokens are never included in model metadata, reprs, or
test fixtures.

## Optional real smoke test

After setting `DHAN_CLIENT_ID` and `DHAN_ACCESS_TOKEN`, list active expiries:

```bash
python scripts/dhan_option_chain_smoke.py \
  --symbol RELIANCE
```

The script stops after listing dates unless the user explicitly adds, for
example, `--expiry 2026-09-24`. It then displays only a compact normalized
near-spot sample for inspection. It has no trading import or order operation and
does not print credentials. The A1.5 resolver supplies the current underlying
ID; an optional caller-supplied ID must agree before any expiry or chain request.

Earlier validation paired `RELIANCE` with security ID `1333`. A1.5 live master
validation on 2026-09-06 corrected the current mapping to `2885 = RELIANCE` and
`1333 = HDFCBANK`. The option-expiry/chain transport validation for ID 1333 was
still factual, but the displayed underlying label was wrong. Symbol-first and
symbol-plus-ID smoke paths now prevent that integrity failure.

## Security, non-goals, and next target

Unit tests use only injected transports and deterministic fake payloads. Raw
Dhan response dictionaries stop at the parser boundary and are not copied into
metadata. There is no SDK dependency, WebSocket depth, cache, hidden sleep,
expired-chain history, analytics, Black-Scholes code, or Google Sheet coupling.

The next target is **TIAF_A1.4 — expired options history**.

Official references: [Dhan option chain](https://dhanhq.co/docs/v2/option-chain/),
[Dhan annexure](https://dhanhq.co/docs/v2/annexure/), and
[Dhan releases](https://dhanhq.co/docs/v2/releases/).
