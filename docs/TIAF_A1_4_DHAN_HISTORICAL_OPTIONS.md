# TIAF_A1.4 Dhan Historical / Expired Options Data

## Purpose and boundary

A1.4 adds factual rolling historical-option evidence through DhanHQ v2
`POST /charts/rollingoption`. It supports research without expired option
contract security IDs: callers provide only the underlying identity and a
validated relative strike. The implementation contains no contract-selection
intelligence, recommendation, strategy, look-ahead feature, pricing model,
replay engine, or execution behavior.

The direct A1.2 `httpx` transport remains the only HTTP boundary. Raw Dhan
parallel arrays stop in the Dhan parser and never enter provider-neutral model
metadata.

## Provider-neutral contracts

- `ExpiryFlag`: `WEEK` or `MONTH`.
- `HistoricalOptionExpiryCode`: endpoint-specific `NEAR=1`, `NEXT=2`, or
  `FAR=3`.
- `RelativeStrike`: immutable normalized `ATM`, `ATM+N`, or `ATM-N` value.
- `HistoricalOptionBar`: one timestamp with optional OHLC, IV, volume, OI,
  actual strike, and underlying spot.
- `HistoricalOptionSeries`: an immutable chronological tuple of bars plus the
  complete request context and half-open date range.
- `HistoricalOptionsDataProvider`: a segregated provider protocol, leaving the
  original quote/OHLCV and live-derivatives protocols unchanged.

All contracts are frozen. Python lists and JSON arrays are accepted for `bars`,
while JSON serialization emits arrays and reconstructs cleanly. Package version
`0.1.0` remains separate from contract schema version `1.0`.

## Request mapping

| TIAF value | Dhan value |
|---|---|
| `1m`, `5m`, `15m`, `25m`, `1h` | `1`, `5`, `15`, `25`, `60` |
| `OptionType.CE` | `CALL` |
| `OptionType.PE` | `PUT` |
| equity underlying | `OPTSTK` |
| index underlying | `OPTIDX` |
| NSE underlying | `NSE_FNO` |
| BSE underlying | `BSE_FNO` |

`securityId` is always the underlying Dhan security ID. No expired contract ID
is requested or inferred. Every request asks for `open`, `high`, `low`, `close`,
`iv`, `volume`, `strike`, `oi`, and `spot`.

Dhan's older/general annexure may describe expiry codes as `0/1/2`. Live Dhan
support and endpoint validation confirm that `/charts/rollingoption` instead
uses `1` for near, `2` for next, and `3` for far expiry. A1.4 captures this
inconsistency explicitly with the dedicated `HistoricalOptionExpiryCode`; it
does not alter expiry-code behavior for any unrelated API. The weekly/monthly
cadence remains a separate field.

`expiryCode` is assigned unconditionally in every rolling-option request as the
exact integer `1`, `2`, or `3`. Zero and `None` are rejected before transport.

`RelativeStrike` accepts arbitrary positive integer offsets as a provider-neutral
value type. At the Dhan boundary, index requests are limited to ATM ±10 and
stock requests to ATM ±3, matching the endpoint documentation. The adapter
does not determine which strike is desirable.

## Half-open chunking and merge behavior

Caller ranges are explicit dates `[requested_from, requested_to)`. Datetimes are
rejected at this date-only endpoint boundary rather than silently truncated.
The deterministic planner creates adjacent chunks of no more than 30 calendar
days:

```text
[start, start+30) [start+30, start+60) ... [last, end)
```

Exactly 30 days produces one request; 31 days produces a 30-day request and a
one-day request. Boundaries are shared as date markers, not overlapping date
ranges, so no day is omitted. The adapter performs sequential factual calls
without sleeping or enforcing a hidden rate schedule.

Returned bars are merged by aware timestamp and sorted. An identical duplicate
timestamp is retained once and counted in safe metadata; a conflicting
duplicate raises `ProviderBadResponseError`. Bars outside the caller's overall
half-open range are rejected. No local five-year cutoff is imposed—older-data
rejections remain truthful provider errors. A range beginning today or later is
rejected as future-only.

## Parsing, units, quality, and time

The parser reads only the requested `data.ce` or `data.pe`. A null requested
side becomes an empty `UNAVAILABLE` series. All ten arrays—timestamp plus the
nine requested facts—must exist and have equal length. Indexing occurs only
after validation; no `zip()` truncation is used.

OHLC values are non-negative and their available envelope must be consistent.
IV is preserved exactly in Dhan's returned units; there is no division by 100.
Volume and OI are non-negative integers, actual strike is positive, and spot is
non-negative. Missing entries remain `None`.

Bar quality is deterministic:

- `GOOD`: every requested factual value is present.
- `PARTIAL`: complete OHLC remains, but another requested value is absent.
- `DEGRADED`: incomplete OHLC but at least one useful fact remains.
- `UNAVAILABLE`: no requested factual value is usable.

Series quality reflects its chunks and bars. Empty results are `UNAVAILABLE`;
an unavailable chunk alongside useful chunks is `PARTIAL`.

Dhan timestamps are epochs and are converted through UTC to
`ZoneInfo("Asia/Kolkata")`. `observed_at` is the actual post-response acquisition
time of the last chunk. All model timestamps reject naive datetimes and JSON
emits the `+05:30` offset.

## Errors, security, and smoke test

The established transport translates authentication, rate-limit, timeout,
network, invalid-security-ID, and malformed-response failures into typed TIAF
errors. Unsupported intervals, segments, identities, and Dhan-relative strike
limits raise `UnsupportedCapabilityError`. Credentials remain environment-only
and absent from models, reprs, errors, fixtures, and documentation examples.

Optional read-only inspection:

```bash
python scripts/dhan_expired_options_smoke.py \
  --segment NSE_FNO \
  --symbol RELIANCE \
  --instrument OPTSTK \
  --expiry-flag MONTH \
  --expiry-code 1 \
  --strike ATM \
  --option-type CE \
  --interval 15m \
  --from-date 2026-08-01 \
  --to-date 2026-08-15
```

The utility prints normalized factual bars only. It imports no trading/order
API and emits no directional analysis. It resolves the underlying security ID
from the symbol. If `--security-id` is also supplied, it must match the resolved
underlying—not a child option contract—before the historical request is made.

Earlier validation paired the label `RELIANCE` with security ID `1333`.
Subsequent A1.5 live master validation on 2026-09-06 established the current
mapping as `2885 = RELIANCE` and `1333 = HDFCBANK`. The rolling-options endpoint,
payload, expiry-code, parsing, and chunking validation remains valid for the
underlying ID that was requested, but the earlier displayed RELIANCE identity
was incorrect. The hardened smoke path now refuses this mismatch.

Official references: [Dhan expired options data](https://dhanhq.co/docs/v2/expired-options-data/),
[Dhan annexure](https://dhanhq.co/docs/v2/annexure/), and
[Dhan releases](https://dhanhq.co/docs/v2/releases/).
