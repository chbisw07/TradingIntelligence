# TBD - TI Monitoring / Watch-Mandate Architecture

**Consolidation disposition: REVISE_AND_KEEP_TBD (2026-09-11).**
The [transition plan](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md) assigns a
bounded mandate/lifecycle/evidence-family-clock/delta review before A5
implementation; on-demand A5 does not require a daemon. TI application
orchestration owns future monitoring semantics, never specialists or Shell.
A8 binds TM position identity/priority, A9 candidate intake, A10 durable due-work/
event scheduling and recovery. Calendar/outcome admission precedes unattended
timing claims. Adaptive cadence and original lifecycle names remain hypotheses;
source disputes do not implement price-event lifecycle. No monitoring is added.
The [A4 closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) preserves this timing:
revisit only the bounded position/mandate contract at A5 entry, after the
preferred Shell architecture slice; do not pull durable scheduling into Shell.

> **Status:** TBD / temporary exploratory design note  
> **Authority:** This document is **not yet part of the accepted TI architecture**. It captures an agreed design direction for later formal review.  
> **Promotion rule:** Before becoming authoritative, this note must be revisited at the relevant milestone, reconciled with the then-current repository architecture, tested against implementation realities, and either promoted, revised, split, or rejected.  
> **Repository placement:** Intended for `docs/` with the `TBD_` prefix so it is immediately recognizable as non-final.

---

## 1. Purpose

Capture the preferred design for how TradingIntelligence (TI) should manage watchlists, active monitoring, position-aware monitoring, cadence/heartbeat, evidence refresh, escalation, and runtime efficiency.

The core principle is:

> **Do not model a watchlist merely as a list of symbols with colors. Model it as a collection of independent monitoring mandates over shared instruments, where lifecycle, horizon, priority, cadence, triggers, evidence scope, analysis depth, specialist eligibility, and budget are separate dimensions.**

A color is only a UI presentation choice. It is not a domain state.

---

## 2. Semantic Lifecycle States

Internally, TI should use semantic lifecycle states, for example:

| Internal lifecycle state | Meaning | Suggested UI color |
|---|---|---|
| `PASSIVE` | Present for manual/user observation. TI performs little or no active analysis beyond shared maintenance. | BLUE |
| `ACTIVE_WATCH` | TI actively monitors this mandate according to its policy. | YELLOW |
| `ACTIVE_POSITION` | An actual position is being monitored with elevated priority and logging. | GREEN |
| `INACTIVE` | This mandate is terminated/suspended and receives no active monitoring. | BLACK |

Important rules:

- Colors belong to UI/configuration, not domain contracts.
- A future UI may change the colors without changing lifecycle semantics.
- Lifecycle remains separate from horizon, objective, priority, cadence, evidence policy, and analysis depth.
- `INACTIVE` terminates only the current mandate. The same instrument may later appear in a new mandate.
- Position truth remains external/authoritative in TradeMonitor/broker integration; `ACTIVE_POSITION` represents a monitoring mandate linked to that position.

A future configuration could map:

```yaml
lifecycle_colors:
  PASSIVE: blue
  ACTIVE_WATCH: yellow
  ACTIVE_POSITION: green
  INACTIVE: black
```

The mapping is presentation-only.

---

## 3. Instrument vs WatchMandate

One instrument may participate in multiple simultaneous monitoring purposes.

```text
Instrument:
    ATHERENERG

Mandate A:
    objective = long_term_growth
    horizon   = 1 year
    lifecycle = ACTIVE_WATCH

Mandate B:
    objective = positional_opportunity
    horizon   = 2 weeks
    lifecycle = PASSIVE

Position mandate:
    lifecycle = ACTIVE_POSITION
    position_ref = ...
```

These mandates share reusable evidence wherever freshness and semantics permit, while retaining independent objectives, cadences, budgets, and analysis policies.

---

## 4. Separate Orthogonal Dimensions

The monitoring model should not overload one state field.

At minimum keep these concepts separate:

1. **Lifecycle** — passive, active watch, active position, inactive.
2. **Horizon** — intraday, days, weeks, months, years, explicit date/expiry.
3. **Objective / trade type** — investment, positional opportunity, F&O opportunity, position supervision, research, etc.
4. **Priority** — low/normal/high/urgent or equivalent.
5. **Cadence policy** — when evidence becomes due.
6. **Evidence policy** — which evidence families matter for this mandate.
7. **Analysis policy** — which deterministic components/specialists may run and at what depth.
8. **Trigger policy** — what causes immediate reassessment.
9. **Budget policy** — provider/tool/model/cost/latency limits.
10. **Runtime state** — last/next execution and fingerprints.

This separation is critical for flexibility and performance.

---

## 5. WatchMandate Concept

A future typed model may conceptually contain:

```text
WatchMandate
├── mandate_id
├── instrument_ref
├── instrument_type
├── objective
├── trade_type
├── horizon
├── lifecycle
├── priority
│
├── cadence_policy
│   ├── profile_id
│   ├── next_due_at
│   ├── adaptive rules
│   └── calendar/session constraints
│
├── evidence_policy
│   ├── PRICE
│   ├── TECHNICAL
│   ├── MTF
│   ├── RELATIVE_STRENGTH
│   ├── DERIVATIVES
│   ├── FUNDAMENTALS
│   ├── NEWS
│   ├── SECTOR
│   ├── MACRO
│   └── FORECAST
│
├── analysis_policy
│   ├── deterministic components
│   ├── allowed specialists
│   ├── escalation conditions
│   └── maximum reasoning depth
│
├── trigger_policy
│   ├── price/level triggers
│   ├── structure triggers
│   ├── event/news triggers
│   ├── volatility triggers
│   ├── expiry/time triggers
│   └── user/manual triggers
│
├── budget_policy
│   ├── provider-call budget
│   ├── tool-call budget
│   ├── model-call budget
│   ├── token/cost budget
│   └── latency budget
│
└── runtime_state
    ├── last_checked_at
    ├── last_full_assessment_at
    ├── next_due_at
    ├── last_material_change_at
    ├── last_trigger
    ├── last_evidence_fingerprint
    └── last_assessment_id
```

Important runtime/scheduling fields should eventually become first-class typed fields rather than arbitrary metadata. Metadata remains useful for extensible extras.

---

## 6. Horizon / Objective Determines What Is Watched

TI must not evaluate every feature or evidence family on every heartbeat.

The combination of:

- horizon
- objective/trade type
- instrument type
- lifecycle
- priority

determines the evidence scope and cadence.

### Short positional F&O mandate

```text
price/structure      15m / 1h
momentum             15m / 1h
MTF                  1h
derivatives          active refresh
news                 event-driven
fundamentals         normally skipped
forecast             horizon/expiry appropriate
```

### 6–12 month equity mandate

```text
technicals           daily / periodic
relative strength    daily
fundamentals         on filing / periodic
valuation            daily/weekly
news/events          event-driven + periodic
sector               daily/weekly
forecast             slower cadence / material-change trigger
deep agents          only after meaningful evidence change
```

This selective-evidence policy is a major performance safeguard.

---

## 7. Independent Evidence Clocks

A mandate should not necessarily have one monolithic heartbeat.

Different evidence families may have independent clocks.

For example:

```text
Market technicals      every 1h
Relative strength      every 1h
News                    event-driven + periodic check
Fundamentals            daily / on filing
Valuation               daily
Forecast                weekly / material-event trigger
Deep Agent synthesis     only on meaningful evidence change
```

The scheduler should ultimately think in terms of:

```text
WatchMandate × EvidenceFamily × RequiredFreshness
```

rather than simply:

```text
Symbol
```

This is analogous to multiple timing domains in electronic circuitry.

---

## 8. Scheduled + Event-Driven Monitoring

Monitoring should combine scheduled cadence with event-driven triggers.

Potential triggers:

- price/level reached or broken
- support/resistance state change
- volatility spike
- new filing/earnings result
- material news/catalyst
- sector or market event
- position/P&L milestone
- expiry proximity
- user/manual request

A long-horizon mandate may run slowly under normal conditions but escalate immediately on material change.

---

## 9. Refresh Is Not Full Reanalysis

Preferred flow:

```text
heartbeat / event
      ↓
refresh only due evidence
      ↓
delta/fingerprint comparison
      ↓
material change?
  ├── NO  → record and stop
  └── YES
        ↓
recompute only affected deterministic dimensions
        ↓
meaningful intelligence change?
  ├── NO  → stop
  └── YES → invoke only relevant specialist(s)
```

A heartbeat must not imply:

- fetch everything
- calculate every feature
- run every indicator
- invoke every specialist
- call an LLM

---

## 10. Dependency-Aware Incremental Recalculation

A later optimization should track which derived features depend on which evidence.

Example:

```text
new price bar
    ↓
price/return/technical/MTF affected

new quarterly filing
    ↓
fundamentals/valuation affected

new option-chain snapshot
    ↓
derivatives affected
```

Only impacted deterministic features and specialist interpretations should be invalidated/recomputed.

This can prevent large amounts of unnecessary work.

---

## 11. Shared Evidence Across Mandates

The same instrument may appear in several watchlists/mandates.

TI should avoid duplicate acquisition and computation.

```text
                 RELIANCE
                    │
              shared evidence
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    1-month       6-month      position
    mandate       mandate      mandate
```

Different mandates interpret shared facts according to their own objective/horizon, while acquisition is reused where semantics permit.

This should build on A1/A3 caching, single-flight, evidence fingerprints, and gateway infrastructure.

---

## 12. Scheduler Model

Prefer `next_due_at` / due-work scheduling rather than scanning every symbol continuously.

Conceptually:

```text
09:30  SBIN ACTIVE_POSITION
09:35  KAYNES ACTIVE_WATCH
09:45  MCX ACTIVE_POSITION
10:00  RELIANCE ACTIVE_WATCH
```

More precisely, schedule due work units:

```text
WatchMandate
× EvidenceFamily
× RequiredFreshness
```

This scales better than global polling.

---

## 13. Priority Model

Priority is separate from lifecycle.

Illustrative queue priority:

```text
P0  urgent active-position trigger
P1  normal ACTIVE_POSITION monitoring
P2  ACTIVE_WATCH event-triggered reassessment
P3  ACTIVE_WATCH scheduled monitoring
P4  PASSIVE batch/shared maintenance
```

A mandate may be temporarily escalated without changing its lifecycle.

---

## 14. Adaptive Cadence

A future optimization may change cadence dynamically.

Example:

```text
ACTIVE_WATCH positional
normal             = 1h
approaching breakout = 15m
condition clears     = 1h
```

Example:

```text
ACTIVE_POSITION option
25 days to expiry = 30m
2 days to expiry  = 5m
```

Adaptive cadence should come only after a simpler scheduler is proven stable.

---

## 15. Configuration-Driven Profiles

Defaults should be configuration-driven, not hard-coded.

```yaml
monitoring_profiles:
  positional_candidate:
    technical_refresh: 1h
    mtf_refresh: 1h
    news_refresh: event_or_1h
    fundamental_refresh: 1d
    priority: normal

  long_term_candidate:
    technical_refresh: 1d
    news_refresh: event_or_1d
    fundamental_refresh: filing_or_1w
    forecast_refresh: 1w
    priority: normal

  active_position:
    normal_interval: 15m
    event_driven: true
    priority: high
```

Individual mandates may override profile defaults within policy limits.

---

## 16. Budget-Aware Scheduling

Monitoring should be aware of:

- provider rate limits
- gateway/tool limits
- model/LLM budgets
- latency budgets
- queue pressure

If many items become due simultaneously, the scheduler should prioritize high-value work and safely defer lower-priority work rather than overload TI.

This should integrate with existing A1.6 and A3.2 budget/gateway concepts.

---

## 17. Session / Calendar Awareness

Cadence should eventually respect:

- market open/closed state
- exchange sessions
- holidays
- instrument-specific trading sessions
- corporate-event timing
- expiry calendars

A 15-minute cadence should not blindly behave the same way outside trading hours.

Exact calendar semantics remain TBD.

---

## 18. ACTIVE_POSITION / TradeMonitor Boundary

`ACTIVE_POSITION` may correspond to an actual position.

Authority remains:

```text
TI = intelligence
TradeMonitor = risk / authority / lifecycle / execution
Broker = final truth
```

The monitoring mandate should reference the authoritative position identity; it should not create a second position truth.

---

## 19. Agent Boundary

The monitoring/scheduling subsystem decides **when** an Agent should run.

Agents remain:

```text
task + evidence → opinion
```

Do not embed:

- heartbeat logic
- persistent scheduler state
- provider polling
- watchlist lifecycle

inside specialist Agents.

---

## 20. Audit / Logging

For active mandates, TI should eventually retain enough structured runtime history to answer:

- why did this mandate run?
- was it scheduled or triggered?
- which evidence changed?
- which work was skipped?
- which specialists ran?
- what was the previous fingerprint/state?
- what changed in the resulting assessment?
- what was the cost?

This should support later replay/evaluation without turning monitoring logs into market truth.

---

## 21. Failure / Degradation

A monitoring cycle may encounter:

- provider unavailable
- stale evidence
- budget exhausted
- gateway timeout
- model disabled
- specialist failure

The mandate must remain valid.

Failure should update monitoring/runtime status, not silently become a bullish/bearish opinion.

Lower-priority work may be deferred safely.

---

## 22. Performance Principles

1. Do not evaluate every feature on every heartbeat.
2. Do not refetch unchanged evidence.
3. Do not recompute unaffected features.
4. Do not invoke every specialist for every mandate.
5. Do not invoke LLMs merely because time elapsed.
6. Reuse evidence across mandates.
7. Use evidence-family-specific clocks.
8. Use delta/fingerprint checks before escalation.
9. Prefer deterministic refresh before non-deterministic reasoning.
10. Prioritize active positions/material events.
11. Let horizon/objective/instrument type determine analysis depth.
12. Make scheduling and budgets explicit.

---

## 23. Likely Roadmap Placement

Current view:

- **A3:** specialists remain bounded/stateless; do not interrupt specialist implementation.
- **A5:** formally revisit WatchMandate / position-monitor architecture.
- **A8:** operationalize active-position / TradeMonitor linkage.
- **A9:** scanners may create/populate monitoring mandates.
- **A10:** production scheduler, persistence, queues, adaptive cadence, retries, recovery, load management and observability.

---

## 24. Open Questions

- final lifecycle names/transitions
- whether `SUSPENDED` should differ from `INACTIVE`
- BLUE/PASSIVE maintenance semantics
- exact cadence profiles
- evidence-family dependency graph
- adaptive cadence rules
- event-source architecture
- scheduler persistence
- queue/preemption behavior
- scanner-created vs user-created mandates
- user overrides
- cross-watchlist dedupe
- historical monitoring audit/replay
- forecast refresh policy
- market-calendar/session contracts
- budget-pressure degradation
- active-position binding semantics
- mandate expiry/auto-close rules

---

## 25. Working Design Principle

> **A watchlist is not a list of symbols with colored states. It is a collection of typed monitoring mandates over shared instruments. Semantic lifecycle, horizon, objective, priority, cadence, evidence scope, triggers, analysis depth, specialist eligibility, and budget are independent dimensions. Colors are merely a presentation mapping. Monitoring should be scheduled + event-driven, incremental, shared, delta-aware, and selectively escalated.**
