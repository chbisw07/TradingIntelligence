# TIAF_A1.5 — Instrument Resolver

## Status and boundary

TIAF_A1.5 is the provider-neutral identity-resolution layer between human
watchlist symbols and provider-specific market-data identifiers. It adds no
recommendation, ranking, Agent, LLM, order, account, or execution behavior.

Underlying selection and derivative-contract resolution remain separate:

1. a symbol such as `RELIANCE` resolves to an explicit cash/index underlying;
2. a derivative resolves only with its own identity fields, such as expiry,
   strike, and option side.

The resolver never chooses a nearest future or option strike. A deployment may
explicitly configure a primary cash exchange for otherwise underspecified
symbol-only underlying queries; this policy is visible and overridable.

## Provider-neutral contracts

- `InstrumentQuery` accepts a normalized symbol, exchange/segment/type filters,
  exact derivative identity, provider trading symbol, or provider instrument
  ID. At least one primary identifier is required.
- `ResolvedInstrument` retains the canonical `InstrumentKey`, provider name and
  ID, trading symbol, lot/tick details, source-record identity, observation
  time, quality, and safe metadata.
- `ResolutionResult` has exactly one valid state: unique, ambiguous, or not
  found. Matches are immutable tuples in Python and ordinary arrays in JSON.
- `InstrumentResolver` is synchronous and exposes `resolve`, `search`, and
  order-preserving `resolve_many` operations.
- `ResolutionPolicy` carries the configurable primary cash and F&O exchanges.

All timestamps are aware and normalize to the canonical TIAF timezone,
`Asia/Kolkata` (`+05:30` in JSON).

## Dhan instrument master

Dhan publishes credential-free compact and detailed CSV masters. A1.5 uses the
detailed file because resolution needs fields that the compact form does not
carry together: underlying security ID/symbol, expiry, strike, option type,
lot size, and tick size. Parsing uses CSV headers, not column positions, and
missing required headers produce `InstrumentMasterParseError`.

Default source:

```text
https://images.dhan.co/api-data/api-scrip-master-detailed.csv
```

Default local cache:

```text
${TIAF_DATA_DIR:-data}/instrument_master/dhan/api-scrip-master-detailed.csv
```

The file is downloaded only when absent or when refresh is explicitly
requested. Cache replacement is atomic. The public download uses no Dhan
credentials, and this narrow instrument-master cache is not a general market
data cache or scheduling policy.

Dhan rows map to existing provider-neutral segments and instrument types.
Unknown provider values map to `UNKNOWN`; the relevant raw classification
values remain in safe metadata rather than leaking complete CSV rows.

### Tradability and provider diagnostic rows

Live inspection of the detailed master found no active/status column, and
`BUY_SELL_INDICATOR=A` appears on both genuine and provider test derivatives.
The diagnostic cash underlyings are instead explicitly identified by Dhan ISIN
markers `DUMMYSAN001` through `DUMMYSAN022`. A1.5 preserves ISIN and buy/sell
status as safe metadata and excludes `DUMMYSAN` underlyings from the canonical
F&O universe. This is a narrow provider-identity rule, not a symbol substring
filter: a legitimate symbol containing `TEST` remains eligible when its ISIN
and derivative relationship are genuine.

Dhan documents the exchange-trading-symbol column as removed from the detailed
master. The parser accepts that column when present and otherwise uses the
detailed `SYMBOL_NAME` as the provider's exact symbol key. It does not join the
compact and detailed masters in A1.5; callers that need a distinct compact-only
`SEM_TRADING_SYMBOL` value should use an exact security ID until that enrichment
is deliberately added.

## Deterministic matching

Matching priority is:

1. exact Dhan security ID;
2. exact normalized provider trading symbol;
3. normalized canonical symbol plus every supplied filter.

Ordinary symbol/trading-symbol searches consider active rows. An exact provider
ID may retrieve an inactive row, which is marked inactive and degraded rather
than hidden.

Generic `search()` preserves every exact match and never applies deployment
preference. `resolve()` first honors explicit query exchange/segment, provider
ID, and trading symbol. For an otherwise symbol-only cash/index query spanning
exchanges, it may apply `ResolutionPolicy` only when exactly one candidate
exists in the configured primary exchange. That result uses
`POLICY_SELECTED`, and result metadata records `policy_applied`,
`preferred_exchange`, and the pre-policy candidate count. Multiple candidates
inside the preferred exchange remain ambiguous.

Current India deployment defaults are configurable, non-secret settings:

```text
TIAF_PRIMARY_EXCHANGE=NSE
TIAF_PRIMARY_FNO_EXCHANGE=NSE
```

This is explicit deployment policy, not fuzzy matching and not an unconditional
first-NSE-row rule. Zero matches return `not_found`; unresolved multiple matches
return `ambiguous`; only one selected match populates `resolved`.

Consequences:

- `RELIANCE` across NSE and BSE resolves to NSE under the default policy and is
  labeled `POLICY_SELECTED`;
- `RELIANCE` with `exchange="BSE"` resolves BSE and does not apply policy;
- two valid NSE candidates remain ambiguous even when NSE is preferred;
- futures without expiry remain ambiguous when multiple contracts exist;
- options require instrument type, expiry, positive strike, and matching
  `CE`/`PE` side;
- no fuzzy matching or silent first-row selection exists.

The examples below use fixture IDs only; they are not production constants:

```python
from datetime import date

from tiaf.contracts import OptionType
from tiaf.data import InstrumentType, MarketSegment
from tiaf.data.providers.dhan import DhanInstrumentResolver
from tiaf.data.resolution import InstrumentQuery

resolver = DhanInstrumentResolver()

equity = resolver.resolve(
    InstrumentQuery(
        symbol="RELIANCE",
        exchange="NSE",
        segment=MarketSegment.NSE_EQUITY,
        instrument_type=InstrumentType.EQUITY,
        provider="DHAN",
    )
)

call = resolver.resolve(
    InstrumentQuery(
        symbol="RELIANCE",
        segment=MarketSegment.NSE_FNO,
        instrument_type=InstrumentType.CALL_OPTION,
        expiry=date(2026, 9, 24),
        strike=3000,
        option_type=OptionType.CE,
        provider="DHAN",
    )
)
```

## F&O-underlying universe

`DhanInstrumentResolver.get_fno_underlyings()` derives unique, currently
eligible underlying symbols from active derivative relationships inside one F&O
exchange scope. Its default scope is `TIAF_PRIMARY_FNO_EXCHANGE`; callers may
pass `exchange="BSE"` explicitly. Cash rows from another exchange cannot create
duplicate identities, and cash symbols without an eligible derivative
relationship are excluded. The result preserves canonical provider identity in
deterministic order and performs no ranking.

This is the foundation for a future F&O-stock watchlist workflow: callers may
obtain the current eligible universe from Dhan instead of requiring every stock
to be manually maintained in a spreadsheet. Existing spreadsheet watchlists
remain valid inputs; A1.5 does not integrate with or modify Google Sheets.

## Diagnostic identity integrity

The quote, option-chain, and expired-options smoke utilities are symbol-first.
They resolve the provider identity before constructing a market-data provider.
When both symbol and security ID are present, disagreement raises
`DhanIdentityMismatchError` and no provider request is made. ID-only diagnostic
mode resolves its displayed symbol from the master rather than reusing a
caller-supplied label.

This closes an earlier live-validation presentation error: smoke calls used
security ID 1333 with the label RELIANCE, while the current master establishes
`1333 = HDFCBANK` and `2885 = RELIANCE`. The earlier transport responses were
valid for ID 1333; only the displayed identity was wrong.

## Read-only smoke

Examples:

```bash
python scripts/dhan_instrument_resolver_smoke.py \
  --symbol RELIANCE --exchange NSE --instrument-type EQUITY

python scripts/dhan_instrument_resolver_smoke.py \
  --symbol RELIANCE --segment NSE_FNO --instrument-type CALL_OPTION \
  --expiry 2026-09-24 --strike 3000 --option-type CE

python scripts/dhan_instrument_resolver_smoke.py --list-fno-underlyings

python scripts/dhan_instrument_resolver_smoke.py \
  --list-fno-underlyings --exchange BSE --all-matches
```

Add `--refresh` only when a new master download is intended. The smoke needs no
market-data or trading credential and performs no market/trading operation.
Symbol resolution prints when policy was applied. Universe mode prints its F&O
exchange and total unique count, but only the first 20 rows unless
`--all-matches` is supplied.

## Deferred work

A1.5 intentionally does not define broad cache TTLs, endpoint scheduling,
provider fallback, Zerodha resolution, fuzzy aliases, liquidity preferences,
option selection, or recommendation semantics. Those remain later milestones.
