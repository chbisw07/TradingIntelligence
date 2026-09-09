# Tapetide Forensic Validation Report — Phase 1

**Status:** Completed forensic review of the 16-call Phase-1 quality test  
**Purpose:** Decide whether Tapetide is suitable as a serious external evidence provider for TradingIntelligence (TI).  
**Conclusion:** **Conditionally approved for A3-era current evidence**, behind TI-owned normalization/gateway contracts. **Not yet approved as an unqualified historical point-in-time truth source for A7.**

---

## 1. Executive Decision

Tapetide is good enough to move from **candidate** to **recommended integration target for controlled TI evidence acquisition**, subject to field-level normalization rules.

Recommended role:

```text
Dhan
    -> primary live market / F&O / option-chain / Greeks

Tapetide
    -> fundamentals / filings / events / ownership / ratings /
       analyst forecasts / sector-index context / selected historical context

OpenAI models
    -> reasoning / synthesis / deep research / contradiction analysis
```

Do **not** map Tapetide payloads directly into TI domain fields without a normalization layer.

---

## 2. Phase-1 Operational Result

The Phase-1 harness executed 16/16 calls successfully.

Observed latency was roughly 1.9–2.4 seconds per call, suitable for TI's planned funnel because most non-price evidence can be cached/shared.

No write/portfolio/watchlist tools were called.

---

## 3. Strong Findings

### 3.1 Financial statement depth

Tapetide exposes:

- profit & loss
- balance sheet
- cash flow
- ratios
- quarterly/annual history
- availability metadata

This is sufficient to feed much of A3.4 after normalization.

### 3.2 Point-in-time availability metadata

Financial statement sections expose `availability` records containing:

- `period`
- `available_from`
- `basis = reported | estimated`

This is valuable for no-lookahead filtering.

However, the dates should be treated as **conservative availability metadata**, not assumed to be exact exchange-event timestamps.

Example observed:

- RELIANCE FY26 Tapetide `available_from`: 2026-04-27
- official RIL result release: 2026-04-24

The Tapetide date is later, which is conservative and avoids lookahead, but is not exact enough for event-day reconstruction.

### 3.3 Explicit restatement caveat

Tapetide explicitly states that financial values may reflect later restatements even when `available_from` reflects original availability timing.

Therefore:

- acceptable for many current/A3 uses,
- useful but imperfect for A7 point-in-time training,
- historical model training should retain a `revision_semantics` limitation.

### 3.4 Filings/events provenance

RELIANCE filing responses include:

- event/document IDs
- BSE source
- document type
- title
- date
- source URL
- category

This maps well to A3.5 and the proposed Market Intelligence Journal.

### 3.5 New-listing sparse-history behavior

ATHERENERG resolves correctly with listing date and current fundamentals.

Sparse/negative-history conditions are visible rather than replaced by fabricated long histories.

### 3.6 Bank-sector safety

HDFCBANK's detailed ratio section is sparse and largely ROE-oriented instead of forcing generic industrial debt/EBITDA ratios.

This supports TI's decision to keep sector-specific interpretation logic.

### 3.7 Historical-universe semantics

`get_index_membership_asof` correctly returned `out_of_coverage` for RELIANCE / Nifty 500 on 2024-03-31 instead of guessing.

The semantics are excellent, but the current observed membership coverage begins only in 2026, so Tapetide does not yet solve long-history NIFTY-500 survivorship reconstruction.

---

## 4. Forensic Numeric Reconciliation — RELIANCE FY26

### 4.1 PAT / earnings

Tapetide `get_financials`:

- Net Profit FY26: ₹95,754 Cr

Official RIL FY26 reporting:

- Profit after tax before associate/JV adjustment: ₹95,610 Cr
- share of associate/JV profit: ₹144 Cr
- combined: ₹95,754 Cr

**Verdict:** Tapetide's `Net Profit` is internally meaningful, but TI should normalize the exact semantic definition rather than assume it equals profit attributable to owners.

### 4.2 Revenue / sales inconsistency across Tapetide surfaces

Tapetide returns multiple top-line values:

- `get_financials` Sales FY26: ₹1,055,780 Cr
- profile/forecast annual revenue: ₹1,086,181 Cr

Official RIL consolidated FY26:

- Value of Sales & Services / Gross Revenue: ₹1,175,919 Cr
- Revenue from Operations net of GST: ₹1,075,675 Cr
- Other Income: ₹28,962 Cr
- Total Income: ₹1,104,637 Cr

**Verdict:** Different Tapetide tools use different provider/accounting definitions of "sales/revenue".

This is the most important forensic finding.

TI must not merge these fields under one generic `revenue` contract.

Recommended TI normalization:

```text
provider_metric_name
provider_tool
accounting_basis
consolidation_basis
gross_or_net_tax_basis
reported_period
```

Only after an explicit mapping should a provider field become canonical `revenue_from_operations`, `gross_revenue`, `total_income`, etc.

### 4.3 Borrowings / debt

Tapetide balance sheet:

- Borrowings FY26: ₹402,962 Cr

Official RIL consolidated gross debt:

- ₹374,421 Cr

**Verdict:** Tapetide's generic `Borrowings` is not safely interchangeable with RIL's official `Gross Debt`.

Treat this field as `provider_defined_borrowings` until the underlying formula/source is reconciled.

Do not use it directly for:
- net debt,
- leverage,
- debt/equity,
- debt trend
without normalization.

### 4.4 Cash flow

Tapetide FY26:

- CFO: ₹192,113 Cr
- investing CF: -₹101,089 Cr
- financing CF: -₹51,549 Cr
- net cash flow: ₹39,475 Cr

These align with published financial-statement values.

**Verdict:** Strong.

### 4.5 Free cash flow

Tapetide:

- FCF: ₹70,023 Cr

A simple official-statement calculation using CFO minus capex can produce a somewhat different value depending on which capex line is used.

**Verdict:** Treat FCF as a **derived provider metric**, not an official reported fact.

TI should preserve derivation metadata before using it in forecasting or fundamental scoring.

### 4.6 Shareholding

Tapetide:
- promoter Jun-2026: 50.48%
- FII: ~17.20%
- DII: ~21.19%

Official/exchange data confirms promoter holding of 50.48%.

Small category differences for institutional buckets may arise from classification methodology.

**Verdict:** Good for monitoring trends, but preserve provider classification semantics for FII/DII categories.

---

## 5. Forensic Numeric Reconciliation — ATHERENERG FY26

Tapetide profile:
- yearly revenue: ~₹3,823.1 Cr
- EBITDA: -₹257 Cr
- net income/loss: ~-₹517.2 Cr

Official Ather FY26 reporting:
- Revenue from operations: ₹3,671.76 Cr
- Other income: ₹151.32 Cr
- Total income: ₹3,823.08 Cr
- EBITDA loss: ₹257 Cr
- loss for the year: ₹517.17 Cr

**Verdict:** Tapetide's `yearly_revenue` in the profile corresponds much more closely to **Total Income**, not `Revenue from Operations`.

This confirms the RELIANCE finding: generic profile fields may carry provider-specific accounting semantics.

TI must normalize them explicitly.

---

## 6. HDFCBANK Sector-Specific Check

Tapetide profile exposes generic profile fields including ROE/ROCE/PE/book-value.

The detailed `ratios` financial section contains mainly `ROE %`.

Official HDFC Bank FY26 reporting uses bank-specific KPIs such as:

- ROE
- ROA
- NIM
- GNPA / NNPA
- capital adequacy
- cost-to-income
- provision coverage

**Verdict:** Do not treat Tapetide's generic company profile as sufficient bank fundamental evidence.

A3.4's `SECTOR_POLICY_REQUIRED` behavior remains correct.

For banks/NBFCs, TI should request or derive a dedicated banking evidence set before deep interpretation.

---

## 7. News / Filing / Market Intelligence Suitability

Tapetide is well suited to the proposed Market Intelligence Journal because stock-event evidence can carry:

- stock/entity
- event/document ID
- event type
- source
- date
- URL
- title
- category

Recommended TI flow:

```text
Tapetide source record
    ↓
normalize
    ↓
dedupe / cluster
    ↓
MarketIntelligenceEvent
    ↓
append canonical journal
    ↓
A3.5 interpretation
    ↓
decision linkage
    ↓
optional XLSX projection
```

Tapetide source IDs should be retained to prevent duplicates.

---

## 8. A7 / Historical ML Suitability

### Useful today

- financial period history
- `available_from`
- reported vs estimated basis
- historical prices
- some corporate-action semantics
- historical identifier tools
- explicit uncertainty states

### Not sufficient alone yet

- current index-membership history is too shallow for long backtests
- restated values can overwrite originally-known values
- `available_from` may be conservative rather than exact event timestamp
- provider-field semantics may differ across endpoints

**Verdict:** Tapetide can be an A7 input source, but not the sole historical truth source without additional controls.

---

## 9. TI Integration Rules

If Tapetide is integrated later, enforce these rules.

### Rule 1 — Read-only allowlist

Allow only approved evidence tools.

Do not expose:
- portfolio mutations
- watchlist mutations
- any future trading/write operations

### Rule 2 — Tool-specific normalizers

Do not create one giant generic Tapetide mapper.

Use separate normalizers for:

- company profile
- financial statements
- shareholding
- forecasts
- filings/events
- ratings/pledge
- sector/index context
- historical identity/membership

### Rule 3 — Preserve provider-native metric identity

Before canonical mapping, preserve:

```text
provider = TAPETIDE
tool
provider_metric_name
provider_value
provider_unit
provider_period
provider_semantics
```

### Rule 4 — Canonical mapping must be explicit

Examples:

```text
Tapetide profile yearly_revenue
    != automatically TI revenue_from_operations

Tapetide financials Sales
    != automatically official Revenue from Operations

Tapetide Borrowings
    != automatically official Gross Debt
```

### Rule 5 — Reported vs derived

Preserve:

```text
REPORTED
PROVIDER_DERIVED
TI_DERIVED
```

### Rule 6 — Point-in-time flags

Every historical fundamental observation should carry:

```text
available_from
availability_basis
revision_semantics
point_in_time_quality
```

### Rule 7 — Source quality

Primary filings remain preferable for critical facts when available.

Tapetide should be a highly useful evidence provider, not unquestioned authority.

---

## 10. Recommended Provider Status

### For A3.4 Fundamentals
**APPROVE CONDITIONALLY**

Good enough to build a bounded `READ_FUNDAMENTALS` adapter after explicit field mapping.

### For A3.5 News / Events / Filings
**APPROVE**

Very natural fit, subject to deduplication and source preservation.

### For A3.6 Sector / Market Context
**APPROVE CONDITIONALLY**

Promising index/sector/FPI/market tools; evaluate the specific subset needed.

### For A7 Historical Forecasting
**DO NOT APPROVE AS SOLE SOURCE**

Use selectively with point-in-time quality flags and supplementary historical sources.

### For Dhan replacement
**NO**

Keep Dhan as primary live market/F&O provider.

---

## 11. Final Recommendation

Tapetide has passed the forensic Phase-1 review sufficiently well to become:

> **TI's preferred candidate for external Indian-market company/market-intelligence evidence, behind TI-owned provider-neutral gateways and strict normalization.**

It should not be allowed to define TI semantics.

The integration philosophy should be:

```text
Tapetide supplies evidence.
TI defines meaning.
OpenAI models reason over normalized evidence.
TradeMonitor retains authority.
```

This keeps TI provider-neutral while avoiding the need to build a separate massive market-intelligence acquisition project.
