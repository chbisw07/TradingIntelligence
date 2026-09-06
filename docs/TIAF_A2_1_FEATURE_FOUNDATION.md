# TIAF A2.1 Feature Contracts and Deterministic Engine Foundation

## 1. Purpose

TIAF_A2.1 establishes the provider-neutral contracts and pure calculation
boundary for deterministic features. It consumes one accepted A1
`AnalysisContext` and derives reproducible measurements without acquiring new
facts or interpreting them as trading advice.

A1 answers, "What do we factually know?" A2 answers, "What measurable
structure can be deterministically derived from those facts?" Interpretation,
recommendations, option selection, confidence judgments, Agents, and workflows
remain outside A2.1.

## 2. Public contracts

The immutable public contract inventory is:

- `FeatureDefinition`: stable identity, category, description, value type,
  unit, factual source needs, history minimums, supported intervals, and
  independent definition/parameter-schema versions;
- `FeatureRequest`: feature ID, canonical name-sorted scalar parameters,
  optional normalized interval, and required/optional role;
- `FeatureResult`: definition and request, status, typed value, unit, source
  context and symbol, evidence names and observation time, inherited quality,
  lookback actually used, warnings, and metadata;
- `FeatureBundle`: an ordered result tuple for one context with deterministic
  aggregate quality, completeness, missing required IDs, and warnings.

All contracts inherit the TIAF contract schema version `1.0`. Feature
definition versions are also currently `1.0`, but are independent of both the
contract schema and the Python package version `0.1.0`. Feature IDs never embed
a version.

Semantic collections are tuples in Python and serialize as ordinary JSON
arrays. Aware input timestamps from any zone normalize to the canonical TIAF
timezone, `Asia/Kolkata`; JSON timestamps therefore use the `+05:30` offset.
Naive datetimes are rejected. Metadata remains JSON-safe and rejects
credential-shaped keys.

## 3. Status and result semantics

Statuses have these precise meanings:

- `AVAILABLE`: the required factual evidence is usable and a value was
  calculated;
- `PARTIAL`: a value was calculated from explicitly partial, degraded, or
  stale-but-retained evidence;
- `INSUFFICIENT_DATA`: the source was requested but is missing/failed, or the
  exact requested lookback is unavailable;
- `NOT_APPLICABLE`: the source was not requested or the context timeframe is
  incompatible with the request;
- `FAILED`: calculation was unsafe or undefined, such as division by a zero
  base close, or an isolated calculator failure was captured by bundle
  computation.

Only `AVAILABLE` and `PARTIAL` carry values. Insufficient, inapplicable, and
failed results never fabricate zero or another substitute. A required request
is acceptable only when it is `AVAILABLE` or `PARTIAL`; an unacceptable
required result makes the bundle incomplete. An optional failure remains
visible but does not by itself make the bundle incomplete.

## 4. Registry and engine

`FeatureRegistry` is populated explicitly. It rejects duplicate feature IDs,
raises a typed error for unknown IDs, and returns an immutable feature-ID-sorted
definition snapshot. A2.1 does not discover or auto-import plugins.

`DeterministicFeatureEngine` accepts only a registry, an `AnalysisContext`, and
immutable requests. It validates context identity, refuses a context that
still contains deferred evidence, preserves request order, invokes each known
calculator independently, and validates calculator output identity. Unknown
feature IDs are request errors and stop construction before a partial bundle is
returned. Ordinary evidence insufficiency is a result status. Within
multi-feature computation, one typed calculator failure becomes a visible
`FAILED` result and does not suppress other results.

No calculator accesses a provider, resolver, cache, scheduler, network, clock,
broker, LLM, or Agent workflow. Result `as_of` is the corresponding A1 evidence
observation time when present, otherwise the context creation time. Bundle
creation time is the context creation time. When the caller does not supply a
bundle ID, the engine derives a stable UUID from the context ID and canonical
ordered requests; it does not read the wall clock.

## 5. Quality and provenance

Every built-in names the actual A1 evidence slot it consumed. Quote-derived
features retain `("quote",)` and history-derived features retain
`("history",)`, along with the source context ID, canonical symbol, source
observation timestamp, and exact evidence quality. A `PARTIAL` or `DEGRADED`
source can never become `GOOD` in a feature.

Bundle quality is deterministic:

- no usable result: `UNAVAILABLE`;
- a missing required feature or usable degraded evidence: `DEGRADED`;
- any remaining partial or unavailable optional result: `PARTIAL`;
- otherwise: `GOOD`.

This aggregation describes the bundle; it does not overwrite individual
source quality.

## 6. Initial built-in baseline

| Feature ID | Source | Exact value | Unit |
|---|---|---|---|
| `price.current` | quote | normalized quote LTP | `price` |
| `history.bar_count` | history | number of chronological bars | `bars` |
| `history.first_close` | history | earliest supplied close | `price` |
| `history.last_close` | history | latest supplied close | `price` |
| `return.absolute` | history | latest close minus close N intervals earlier | `price` |
| `return.percent` | history | percentage change from close N intervals earlier | `%` |
| `range.high_low_percent` | history | latest N-bar high/low range divided by latest close | `%` |

For `bars=N`, return features use `close[-1]` and `close[-1-N]` and require
exactly enough input to address both, meaning at least `N+1` bars:

```text
absolute_return = latest_close - base_close
return_percent = ((latest_close / base_close) - 1) * 100
```

`bars` therefore means intervals back, not the number of bars in a window. The
engine never silently shortens it. A zero base makes percentage return
`FAILED` because the result is undefined.

For range, `bars=N` means the latest N bars:

```text
range_percent = ((max(high) - min(low)) / latest_close) * 100
```

A zero latest close makes this calculation `FAILED`. This feature is a simple
range measurement and is not ATR.

## 7. Human inspection

The optional read-only proof path builds its factual substrate through A1 and
then invokes the A2.1 engine:

```bash
python scripts/feature_engine_smoke.py \
  --symbol RELIANCE \
  --history-interval 1d \
  --lookback-days 90
```

The default output includes current price, history count, 1/5/20-interval
percentage returns, and the latest 20-bar range, with status, value, unit,
quality, context ID, and evidence name. `--json` emits the contracts and
`--repeat` repeats A1 context construction to make cache reuse and deterministic
feature behavior inspectable. The script is read-only and emits no market
opinion or recommendation.

## 8. Non-goals and A2.2 handoff

A2.1 intentionally contains no RSI, MACD, ADX, SuperTrend, ATR, moving-average
library, scoring, ranking, direction labels, recommendation, contract choice,
execution, replay, or Agent/LLM workflow. It does not change any A1 contract.

A2.2 can extend this fixed boundary with rigorously defined price, return, and
volatility calculators. New features should retain exact window semantics,
explicit parameter schemas, source-quality inheritance, deterministic
timestamps, and ordinary insufficient-data results established here.
