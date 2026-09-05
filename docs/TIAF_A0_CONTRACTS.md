# TIAF_A0 Domain Contracts

## Purpose

TIAF_A0 defines the provider-neutral language exchanged by future data,
planning, interpretation, evaluation, and integration components. These models
validate and serialize information; they do not fetch data, form market views,
rank opportunities, manage risk, or execute orders.

The Python package version and contract schema version are separate concepts.
The package version is `0.1.0`; every A0 contract independently carries a
`schema_version` of `1.0`. Changing package code does not implicitly change the
wire schema, and evolving the wire schema does not prescribe a package version.

Contracts reject undeclared fields and are frozen against top-level attribute
reassignment. Identifiers are caller-supplied non-empty strings so tests,
replay, and integrations can use deterministic values.

Consumers must inspect `schema_version` and reject versions they do not support.
An incompatible field or meaning change requires a new major schema version;
an additive optional change requires a new minor schema version. Because strict
older readers reject unknown fields, producers and consumers must agree on a
minor version before exchanging an expanded payload.

## Public models

- `Horizon` describes a flexible duration or hard end time.
- `EvidenceItem` captures an attributable observation or interpretation input.
- `DataSnapshot` identifies snapshot metadata without embedding OHLC arrays.
- `OpportunityRequest` requests analysis of a normalized symbol universe.
- `PositionRequest` requests forward analysis of an existing position.
- `AgentOpinion` records a bounded specialist view.
- `AgentDecisionBundle` groups opinions, consensus, and disagreement without a
  broker action.
- `OpportunityAssessment` represents forward opportunity intelligence.
- `PositionAssessment` represents forward management intelligence for an open
  or adopted position.
- `OptionExpression` describes an option contract and observed attributes; it
  performs no selection or sizing.

## Enums

| Enum | Meanings |
|---|---|
| `TradeStyle` | `DAY`, `POSITIONAL` |
| `DirectionPolicy` | `CE`, `PE`, `BOTH` |
| `TradeDirection` | `BULLISH`, `BEARISH`, `NEUTRAL` |
| `OpportunityAction` | `ENTER`, `WAIT`, `NO_TRADE` |
| `PositionAction` | `HOLD`, `WATCH_CLOSELY`, `PROTECT`, `PARTIAL_BOOK`, `BOOK`, `EXIT` |
| `ActionStrength` | `MILD`, `MODERATE`, `STRONG`, `URGENT` |
| `FreshnessState` | `FRESH`, `AGING`, `STALE`, `UNKNOWN` |
| `EvidenceType` | market, technical, volume, relative-strength, sector, fundamental, news, macro, volatility, derivatives, risk, and other categories |
| `EvidenceSource` | user, Dhan, Zerodha, web, derived, third-party, and internal origins |
| `ConfidenceBand` | `VERY_LOW`, `LOW`, `MEDIUM`, `HIGH`, `VERY_HIGH` |
| `DataQuality` | `GOOD`, `PARTIAL`, `DEGRADED`, `UNAVAILABLE` |
| `OptionType` | `CE`, `PE` |

Enum values serialize as stable uppercase strings.

## Timestamp policy

All datetime fields require timezone-aware input. The canonical TIAF application
timezone is `Asia/Kolkata`, represented by `zoneinfo.ZoneInfo("Asia/Kolkata")`.
UTC and other aware zones are accepted and normalized to `Asia/Kolkata`; naive
datetimes are rejected. JSON output uses ISO-8601 timestamps with the `+05:30`
offset. Contracts do not invent the current time. Producers must explicitly
supply observation, request, production, creation, adoption, expiry-bound, and
validity timestamps where applicable. A `valid_until` value must be strictly
later than its corresponding `produced_at` or `created_at` value.

## Numeric conventions

- Confidence is a ratio in the closed range `0.0`–`1.0`.
- Fields named `*_score` use the closed range `0.0`–`100.0`.
- Fields named `*_pct` use percentage points: `4.5` means 4.5%, not `0.045`.
  They may be signed where gains and losses or directional moves are relevant.
- Prices are non-negative except that an option strike must be strictly
  positive. Quantity may be positive or negative but cannot be zero.

## Horizon semantics

`Horizon` is deliberately not a closed enum. It may use a human label, inclusive
day bounds, a hard end timestamp, or a useful combination. Day bounds cannot be
negative, and `max_days` cannot precede `min_days`. At least a label or one
structured bound must be present.

Examples include `Horizon(label="intraday")`,
`Horizon(label="2–5 days", min_days=2, max_days=5)`, and a `hard_end_at` value
for “hold until” semantics.

## Separation of responsibilities

An `OpportunityAssessment` concerns the underlying opportunity. An
`OptionExpression` describes a possible derivative expression separately. No
contract assumes that a valid underlying view implies a suitable option trade.

`PositionRequest` and `PositionAssessment` evaluate an existing position from
the request time forward. Original entry rationale is optional context and is
never required. The assessment expresses intelligence only; TradeMonitor
retains governance and execution authority, and the broker remains the source
of truth for live state.

## Request examples

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from tiaf.contracts import DirectionPolicy, Horizon, OpportunityRequest, TradeStyle

request = OpportunityRequest(
    request_id="opp-request-20260905-01",
    universe=[" reliance ", "TCS", "RELIANCE"],
    trade_style=TradeStyle.DAY,
    horizon=Horizon(label="intraday"),
    direction_policy=DirectionPolicy.BOTH,
    top_n=5,
    requested_at=datetime(
        2026, 9, 5, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata")
    ),
)

assert request.universe == ("RELIANCE", "TCS")
```

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from tiaf.contracts import Horizon, PositionRequest

request = PositionRequest(
    request_id="position-request-20260905-01",
    position_id="position-17",
    underlying="RELIANCE",
    instrument="RELIANCE26SEP3000CE",
    quantity=75,
    average_price=31.5,
    horizon=Horizon(label="through this week", max_days=5),
    requested_at=datetime(
        2026, 9, 5, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata")
    ),
)
```

Use `model_dump(mode="json")` or `model_dump_json()` for transport-safe output
and `model_validate()` or `model_validate_json()` for reconstruction. Metadata
is restricted to JSON-compatible values and must contain only non-secret
enrichment supplied by the producer.

Finalized semantic sequences—such as universes, provider lists, evidence IDs,
opinions, concerns, factors, changes, and reasons—are stored as tuples. Pydantic
continues to accept normal Python lists and JSON arrays for these fields, while
JSON serialization emits ordinary arrays. Metadata dictionaries deliberately
remain mutable and extensible in A0; deep collection immutability is not a goal.

## Explicit non-goals

TIAF_A0 includes no LangGraph or agent implementation, LLM call, broker or
market-data adapter, market fetch, ranking or prediction logic, option
selection, position sizing, persistence, API server, TradeMonitor integration,
order intent, or execution behavior.
