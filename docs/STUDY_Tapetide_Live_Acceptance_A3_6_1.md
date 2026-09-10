# Tapetide Live Acceptance — TIAF_A3.6.1

## Final status

**Decision:** `HOLD`

**Historical-status clarification (A3 closure):** this `HOLD` remains the
truthful result for the exact-current standalone Tapetide matrix. It does not
describe the later Yahoo fallback matrix or A3.6.2 integrated run, which passed
their own bounded live acceptance, and it does not undo the accepted
provider-neutral A3.6.1 contracts/runtime at tag `tiaf-a3.6.1`.
**Latest retry:** `2026-09-09T18:29:42+05:30`
**Implementation base:** `tiaf-a3.6.1-arch`
(`f3fc9369c181d35affbb9c824eb33e9af73d1284`)

The production read-only stdio connector works and an earlier 12-call batch
passed adapter-to-replay checks. A later per-event provenance correction was
validated for KAYNES, but the final exact-code matrix stopped before a raw
ATHERENERG financial response could be observed. A direct standalone probe
then showed that Tapetide can return a quota denial as ordinary text while MCP
reports `isError=false`. The daily quota was exhausted, so the ATHERENERG
diagnostic is inconclusive. No evidence was fabricated, and freeze readiness is
not claimed.

## Preserved first HOLD attempt

The first attempt at `2026-09-09T16:39:33+05:30`, retried at
`2026-09-09T17:16:41+05:30`, correctly returned `HOLD`: no callable
Tapetide transport or concrete client was then exposed. It made zero provider
calls and made no live semantic claim. The corrective prerequisite was the
concrete connector implemented by this retry.

## Connector and credential boundary

- Connector: `TapetideMcpClient`
- Python MCP SDK: `mcp>=1.30,<2`
- Transport: stdio via `npx -y tapetide-mcp`
- Observed server: `tapetide 1.0.0`
- Credential: `TAPETIDE_TOKEN` from the process or repository `.env`
- Optional settings: `TAPETIDE_DEBUG`, `TAPETIDE_MCP_URL`
- Lifecycle: one initialized session reused for the complete batch
- Child stderr: suppressed at the credential-safe connector boundary
- Model/LLM calls, tokens, and cost: zero

The connector allows only the nine adapter-supported read operations and fails
closed for everything else. No portfolio, watchlist, broker, order, or arbitrary
tool can cross this boundary. No credential value was printed, persisted, or
stored in a fixture.

## Calls and latency

The earlier complete post-financial-schema batch made exactly **12** provider
calls:

| Symbol | Capability | Native observations | Canonical projections | Result |
|---|---|---:|---:|---|
| RELIANCE | company profile | 137 | 0 | partial; 2 explicit null gaps |
| RELIANCE | profit/loss | 327 | 13 | success |
| RELIANCE | balance sheet | 258 | 0 | success |
| RELIANCE | cash flow | 162 | 0 | success |
| HDFCBANK | company profile | 140 | 0 | partial; 2 explicit null gaps |
| HDFCBANK | profit/loss | 327 | 13 | success |
| KAYNES | company profile | 140 | 0 | partial; 4 explicit null gaps |
| KAYNES | profit/loss | 227 | 9 | success |
| KAYNES | filings/events | 81 | 0 | partial; 2 explicit null gaps |
| ATHERENERG | company profile | 135 | 0 | partial; 4 explicit null gaps |
| ATHERENERG | profit/loss | 202 | 8 | success |
| RELIANCE | quarterly shareholding | 204 | 0 | partial; 1 explicit null gap |

That batch's provider latency was 0.661 seconds minimum, 0.806 seconds median,
1.492 seconds maximum, and 10.581 seconds total. The connector work also made
26 additional bounded diagnostic/retry calls: one profile shape probe, a first
12-call run that exposed the financial-schema defect, one field-path-only
financial probe, one KAYNES provenance check, seven successful exact-code
matrix calls followed by the failed ATHERENERG call, and three focused
ATHERENERG retries. Thus this corrective session made 38 live read calls in
total. All were allow-listed reads; the count exceeded the target because two
live schema defects required correction and the final provider failure was
retried to establish that it was repeatable.

## Exact-current acceptance blocker and classification correction

On the exact current adapter, the first seven matrix calls completed through
KAYNES financials and ATHERENERG profile. The ATHERENERG profit/loss diagnostic
did not yield a raw financial response before the daily quota was exhausted.
A direct standalone probe exposed the decisive transport/provider distinction:
MCP returned `isError=false`, while its plain text explicitly said the Tapetide
rate limit had been reached and the request was denied. It also supplied
retry-after seconds, an exact IST reset time, and the free-plan daily limit.

A3.6.1 now classifies explicit provider-level textual failures before creating
observations or invoking normalization. The observed denial maps to the
existing provider-neutral `RATE_LIMIT` failure and `RATE_LIMITED` result, is
retryable, preserves explicit retry/reset diagnostics, and permits fallback
only when the route policy allows it. Exact IST reset timestamps are represented
as timezone-aware canonical `Asia/Kolkata`; vague relative reset wording is not
inferred. Credential-shaped text is redacted.

The correct current conclusion is: **The 2026-09-09 ATHERENERG diagnostic was
inconclusive because the daily Tapetide quota was exhausted before the raw
financial response could be observed.** This evidence does not establish that
ATHERENERG `profit_loss` is broken. After the daily reset, first rerun only the
standalone `get_financials(symbol="ATHERENERG", section="profit_loss")` probe;
if it succeeds, rerun the bounded 12-call acceptance script. No TIAF mapping or
policy was tuned around the quota response.

No raw live payload is checked in.

## Live schema corrections

The first batch exposed a genuine adapter-boundary defect: Tapetide financial
values are shaped as metric -> period -> value, while the generic scalar walker
treated the terminal period as the metric. That produced no canonical
projection. The narrow correction:

- preserves the metric key as `native_field`;
- preserves each statement period instead of applying the first period globally;
- matches each period to its own `available_from`;
- distinguishes provider-derived percentage-change series;
- uses the provider record ID as a provider-scoped source reference when no URL
  is supplied;
- preserves null fields as explicit unavailable gaps rather than zero or
  fabricated observations; and
- uses the live-advertised `date` argument for
  `get_index_membership_asof`.

These changes remain inside the connector/adapter boundary.

## Semantic reconciliation

### RELIANCE

- Profile identity matched `RELIANCE`.
- Profile `yearly_revenue` remained ambiguous and emitted no canonical
  revenue.
- All 13 profit/loss `Sales` periods remained `PROVIDER_DEFINED` and emitted
  no `fundamental.revenue`.
- Balance-sheet `Borrowings` remained ambiguous and emitted no
  `GROSS_DEBT`.
- All 12 cash-flow `Free Cash Flow` periods remained
  `PROVIDER_DERIVED` and non-canonical.
- `Net Profit` emitted 13 `WELL_SUPPORTED` canonical projections with period,
  provider record reference, and conservative availability.
- Financial `available_from` dates were retained as date-only conservative
  Asia/Kolkata end-of-day boundaries. Revision/restatement limitations remain
  declared by the provider manifest; no exact restatement claim was invented.

### HDFCBANK

- Profile identity matched `HDFCBANK`.
- The profit/loss history produced only well-supported Net Profit projections.
- No EBITDA, generic debt, industrial leverage, or fabricated bank-specific
  metric was promoted. Unsupported bank-quality dimensions remain absent.

### ATHERENERG

- Profile identity matched `ATHERENERG`.
- Financial history remained shorter: eight periods, from March 2020 through
  TTM, versus RELIANCE's thirteen.
- Four profile nulls became explicit unavailable gaps. No null became zero, and
  no older history was synthesized.

### KAYNES

- Profile identity matched `KAYNES`.
- Nine profit/loss periods were preserved with provider provenance and
  conservative availability.
- Profile, financial, and filings batches all serialized and replayed exactly.

### Filings/events

The exact-current targeted KAYNES filings check preserved 10 distinct provider
record IDs and 10 distinct references across 81 native observations. All 81
observations preserved date-only publication evidence as conservative
`ESTIMATED_DATE` Asia/Kolkata boundaries. No primary or canonical event fact
was fabricated.

### Ownership

The RELIANCE shareholding call preserved 204 native observations and periods
from March 2021 through June 2026, plus older/provider-specific periods. One
null became an explicit unavailable gap. No missing ownership category became
zero and no ambiguous ownership label was promoted.

## Replay and provider neutrality

In the earlier complete batch, each normalized batch was written to a temporary
JSONL file. The MCP connector was then closed, every batch was reconstructed with
`NormalizedEvidenceBatch.model_validate_json`, and normalized JSON plus the
SHA-256 semantic fingerprint matched exactly for all 12 records. Replay made no
provider call. The later exact-current run did not reach full-batch replay
because the quota-exhausted ATHERENERG diagnostic stopped the bounded batch.

MCP imports remain confined to
`tiaf.market_intelligence.providers.tapetide_mcp`. Canonical/domain packages
and A3 specialists import neither MCP nor Tapetide modules. Fixture checks for
provider unavailability, unsupported capability, contradiction preservation,
secondary fallback, substitution, and Tapetide-disabled core behavior pass.

## Validation

- Connector/adapter/architecture focused tests: covered by the focused suite.
- Focused A3.6.1 suite: **70 passed**.
- Bounded live acceptance: **HOLD; exact-current run stopped at call 8**.
- Complete repository suite: **1,621 passed**.
- `python -m compileall src`: passed.
- `ruff check src tests`: passed.
- `mypy src tests`: passed for 379 source files.
- `git diff --check`: passed.
- Architecture/security checks: passed.

A3.6.1 is not ready to freeze until the exact current 12-call matrix and its
post-close replay complete. No specialist, scoring, recommendation, trading, or
broker behavior changed.
