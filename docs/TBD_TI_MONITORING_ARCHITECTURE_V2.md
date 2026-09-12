# Monitoring v2 — reconciliation record

## Post-R1 reconciliation disposition — 2026-09-12

The [TI Monitoring Architecture](TIAF_MONITORING_ARCHITECTURE.md) is now the
authoritative future design. This reconciliation prefix preserves the entire
original v2 note below unchanged as historical source material. PROMOTED refers
to architecture, not implemented runtime. All original sections are classified:

| Original section | Disposition | Reconciled meaning / authoritative section |
|---|---|---|
| 1 Thesis | PROMOTED | Governed subscriber-driven capability consumer (§1–2). |
| 2 Subscribers | PROMOTED | One conceptual contract for internal/external apps (§3). |
| 3 Watchlist ownership | PROMOTED | Option B selected over TI CRUD/hybrid core (§2). |
| 4 Optional watchlist | PROMOTED | Opaque namespaced refs; no mandatory group (§2–3). |
| 5 Object hierarchy | REVISED | MonitoringMandate is fundamental; mandatory subscription/item hierarchy REJECTED (§3). |
| 6 Identity/isolation | PROMOTED | Logical local scope, not a SaaS claim (§3). |
| 7 Multiple mandates | PROMOTED | Same instrument may have independent scope/profile/lifetime (§3). |
| 8 First-class horizon | REVISED | Canonical duration/basis or interval plus versioned app-label mapping; no guessed trading days (§4). |
| 9 Horizon vs cadence | PROMOTED | Independent dimensions (§4). |
| 10 Time dimensions | PROMOTED | Separate freshness, event termination and clock ownership too (§4). |
| 11 Termination | REVISED | Finite validity, cancel/run bounds and admitted events; no first-version lease (§4,7). |
| 12 One-shot/recurring | PROMOTED | No universal max_runs=1; reuse typed evaluation requests (§4). |
| 13 TM | PROMOTED | Subscriber with operational truth, not intelligence-owned execution (§2,5). |
| 14 Scanner/sector | PARTIALLY_PROMOTED | Scanner subscriber model approved; Sector Rotation implementation remains deferred (§6,13). |
| 15 UI | PROMOTED | Another governed subscriber; no new Shell/Web commands (§3). |
| 16 Evidence vs analysis | PROMOTED | Shared acquisition does not merge analyses (§9). |
| 17 Dedupe | PROMOTED | Entitlements, PIT, semantics, versions and freshness gate reuse (§9). |
| 18 Different conclusions | PROMOTED | Source comparability decides conflict; retain scoped disagreement (§9). |
| 19 Intelligence profiles | REVISED | Same pluggability model; availability intersection that erases required scope REJECTED (§6). |
| 20 Absence | PROMOTED | Preserve R1 stable obligations and explicit missing scope (§6–7). |
| 21 Capability invocation | PROMOTED | Current CAPTURED_READ is not live refresh; future acquisition requires admission (§6). |
| 22 Monitor compatibility | PARTIALLY_PROMOTED | Metadata contract direction accepted; R2 runtime flag/catalog not implemented (§6,12). |
| 23 Layers | PROMOTED | Consumer/runtime/capability responsibilities, no second Planner (§1,6). |
| 24 Optimization | PARTIALLY_PROMOTED | Bounded reuse promoted; incremental/adaptive mechanisms deferred (§9–12). |
| 25 Freshness | PROMOTED | Per-family/per-mandate semantics (§4,9). |
| 26 Profiles | PROMOTED | Trusted COLD versioned configuration (§6). |
| 27 Scheduled/event | PARTIALLY_PROMOTED | Periodic minimum; bounded event slice later (§8). |
| 28 Priority/budgets | PROMOTED | Ceilings, allocation lineage, no priority-granted authority (§11). |
| 29 Admission | REVISED | Atomic per-mandate acceptance; no initial batch partial-acceptance protocol (§7). |
| 30 Idempotency | PROMOTED | Subscriber/operation/key/digest; immutable amendments and idempotent cancel (§7). |
| 31 Lease | KEEP_TBD | No mandatory v1 lease; finite validity and explicit cancel selected (§7). |
| 32 Mutation/audit | PROMOTED | No retroactive rewrite or implicit external-list cascade (§2,7). |
| 33 Lineage | REVISED | No mandatory subscription ID; additive composition pins preserve child hashes (§3,10). |
| 34 Execution | PROMOTED | Intelligence cannot place orders or close positions (§2,5). |
| 35 Push/pull | PARTIALLY_PROMOTED | Transport separation approved; notification implementation deferred (§11–12). |
| 36 Persistence | PARTIALLY_PROMOTED | Single-writer durable protocol is a gate, not an existing filesystem guarantee (§10). |
| 37 Delivery guarantee | PROMOTED | At-least-once delivery/idempotent logical runs; exactly-once external effects REJECTED (§8). |
| 38 Missed runs | REVISED | Coalesce default, explicit skip; REPLAY_MISSED deferred (§8). |
| 39 A5 | REVISED | Normalize distinct runtime mandate with preserved source; no A5 rename (§5). |
| 40 Lifecycle | REVISED | Runtime state separate from purpose/A5 linkage and run health (§5). |
| 41 Pluggability | PROMOTED | Required/optional independent of COLD replacement; contracts STRUCTURAL (§12). |
| 42 R2–R5 | REVISED | Minimum prerequisites vs useful full remediation distinguished; no new A5 blocker (§12). |
| 43 Roadmap | REVISED | A8 TM/A9 intake/A10 operations; earlier minimal runtime needs a separate gate (§13). |
| 44 Diagram | REVISED | Remove mandatory subscription/watchlist/item hierarchy; retain admitted mandate/run/evidence boundaries (§2–3,10). |
| 45 Ownership | PROMOTED | Subscriber intent, TI governance/runtime, TM execution (§2). |
| 46 Questions | REVISED | Decisions resolved by §§2–13; detailed optional runtime mechanisms remain deferred. |
| 47 Non-goals | PROMOTED | No implementation or expansion into execution/UI/watchlist CRUD (§1). |
| 48 Promotion | REVISED | Reconciled architecture promoted; this source stays historical, not co-authoritative (§1,13). |
| 49 Final thesis | PROMOTED | Governed recurring/event-driven capability consumer (§1). |

## Historical v2 note (preserved verbatim)

# TBD — TI Monitoring / Subscriber-Driven Monitoring Architecture v2

**Status:** Deferred / exploratory design note  
**Authority:** Non-authoritative idea cache  
**Version:** v2  
**Purpose:** Preserve the post-A5/post-pluggability monitoring model centered on subscriber intent and monitoring mandates.  
**Implementation status:** Not implemented by this document.

## 1. Executive thesis

> **TI should not fundamentally own watchlists. TI should accept governed monitoring mandates from authorized subscriber applications.**

Watchlists are primarily subscriber-owned business groupings. The fundamental TI monitoring object should be a **MonitoringMandate**.

> **Monitoring Runtime is a governed recurring/event-driven consumer of TI capabilities on behalf of subscriber applications.**

TI owns admission, normalized mandates, scheduling, trigger handling, deduplication, shared evidence acquisition, freshness, budget enforcement, capability invocation, replay/audit, result lineage, and failure isolation.

Subscriber applications own business purpose, conceptual watchlists, selected instruments, horizon intent, requested intelligence profile, and lifetime/cancellation intent.

TradeMonitor remains operational position truth and action/execution authority.

---

## 2. Subscriber-driven model

Multiple internal or external apps may subscribe simultaneously:

```text
APP1
 ├─ WL11
 └─ WL12

APP2
 ├─ WL21
 ├─ WL22
 └─ WL23

TM
 └─ active-position monitoring

Scanner
 └─ temporary candidate monitoring

TI_WEB / TI_SHELL
 └─ user-created monitoring
```

Different apps may have very different purposes:
- intraday options;
- short/medium-term equity monitoring;
- long-term investing;
- active-position protection;
- scanner follow-up;
- future Sector Rotation or portfolio workflows.

---

## 3. Watchlist ownership

Preferred principle:

> **Subscriber app owns the conceptual watchlist and its business meaning.**

TI may retain an admitted reference or normalized representation for runtime/replay, but should not become the semantic owner of every subscriber's watchlists.

Potential subscriber metadata:
- watchlist ID;
- display name;
- purpose;
- tags;
- opaque subscriber metadata.

---

## 4. Watchlist is optional

An app may request:

```text
monitor RELIANCE for the next hour
```

without maintaining any persistent watchlist.

Therefore:

> **Watchlist is optional grouping; MonitoringMandate is the fundamental monitoring semantic unit.**

This also fits TM positions, scanners, temporary campaigns, and ephemeral day-trading sets.

---

## 5. Candidate object hierarchy

```text
SubscriberApp
    ↓
MonitoringSubscription
    ↓
0..N Watchlists (optional)
    ↓
0..N WatchItems
    ↓
1..N MonitoringMandates
```

A mandate may also exist directly under a subscription without a watchlist.

A future review should decide whether `MonitoringSubscription` deserves its own first-class domain type or whether subscriber context on mandates is enough.

---

## 6. Subscriber identity and isolation

Potential lineage:

```text
subscriber_id
subscription_id
watchlist_id?   # optional
mandate_id
```

APP1 must not modify/cancel/read APP2 state unless explicitly authorized.

Logical subscriber isolation should work even in one local TI process; it does not imply SaaS/microservices.

---

## 7. WatchItem and multiple mandates

A watch item may identify the instrument:

```text
watchlist_id
instrument_ref
subscriber metadata
```

One item may create multiple mandates:

```text
WL11
 └─ KAYNES
      ├─ intraday mandate
      ├─ 2–6 week positional mandate
      └─ 3–6 month investment mandate
```

One mandate should generally have one principal semantic purpose.

---

## 8. Horizon is first-class

Subscriber labels such as `SHORT`, `MEDIUM`, `LONG`, `SWING` are not enough because different apps may define them differently.

TI should receive normalized semantics as well, for example:

```text
subscriber_label = "MEDIUM"
target_duration = 30 trading days
minimum_duration = 10 trading days
maximum_duration = 60 trading days
```

Exact contract TBD.

---

## 9. Horizon != cadence

Core invariant:

> **Analysis horizon and monitoring cadence are independent.**

Examples:

```text
horizon = 3 months
cadence = hourly
```

```text
horizon = 2 hours
cadence = every 5 minutes
```

---

## 10. Four time dimensions

Monitoring should separate:

1. **Analysis horizon** — what future/decision duration the intelligence concerns.
2. **Monitoring cadence** — how often TI reevaluates.
3. **Mandate lifetime** — how long the mandate remains active.
4. **Run/repetition limit** — maximum evaluations.

Do not collapse them into one `duration`.

---

## 11. Recurrence and termination

Possible future recurrence policy:

```text
max_runs
valid_from
valid_until
cadence
```

A mandate terminates on the earliest applicable condition:
- max runs reached;
- valid-until reached;
- subscriber cancellation;
- parent watchlist expiry;
- position close for position-bound monitoring;
- terminal trigger;
- lease expiry if leases are adopted.

---

## 12. One-shot evaluation vs recurring monitoring

A useful distinction may be:

```text
EvaluationRequest   # one shot
MonitoringMandate  # recurring and/or event-driven
```

This is cleaner than assuming `max_runs=1` is the global monitoring default.

A future API could conceptually expose:
- one-shot evaluation;
- recurring subscription.

Exact capability names remain TBD.

---

## 13. TradeMonitor as subscriber

Example:

```text
position opens
   ↓
TM creates position-linked MonitoringMandate
   ↓
TI invokes A5 as scheduled/event-driven
   ↓
A5 advice returned
   ↓
TM decides action
```

When the position closes, TM causes the mandate to end/deactivate.

Important:

> A position-linked mandate never makes TI the position-truth owner.

---

## 14. Scanner and Sector Rotation integration

A scanner may create a short-lived mandate for a candidate without polluting a permanent watchlist.

Future Sector Rotation may emit events that lead an authorized caller to create mandates.

Neither scanner nor Sector Rotation should own the monitoring runtime.

---

## 15. TI native UI is just another subscriber

If TI_WEB or TI_SHELL later supports watchlists, model it as a subscriber app rather than a special monitoring architecture.

This preserves one monitoring system.

---

## 16. Shared Evidence != Shared Analysis State

Fundamental principle:

> **Deduplicate compatible evidence acquisition/computation, not subscriber intent or analysis state.**

If three mandates monitor RELIANCE at different horizons, TI may share compatible:
- price retrieval;
- filings/news;
- sector evidence;
- deterministic calculations.

But it must preserve separate:
- mandate state;
- purpose;
- horizon;
- result;
- lifecycle;
- ownership.

---

## 17. Dedupe constraints

Evidence sharing is constrained by:
- source entitlement/licensing;
- authorization;
- PIT identity;
- freshness;
- semantic equality;
- policy compatibility.

No sharing merely because data looks similar.

---

## 18. Same symbol, different valid conclusions

Example:

```text
RELIANCE intraday → WAIT
RELIANCE 6-month → SUPPORTIVE
```

Not necessarily contradictory.

Horizon/purpose belongs in proposition/comparability semantics.

---

## 19. Intelligence profiles

A mandate may request:

```text
required:
  baseline.assess

optional:
  sector.rotation
  forecast.return
```

Effective execution remains:

```text
requested
∩ available
∩ authorized
∩ policy-compatible
∩ budget-allowed
```

This must reuse first-order pluggability rather than invent a parallel dependency model.

---

## 20. Required vs optional capability absence

If an optional capability is unavailable, baseline may continue with explicit limitation.

If a required capability is unavailable, return an explicit insufficient/degraded outcome according to policy.

Never silently pretend enrichment occurred.

---

## 21. Monitoring invokes capabilities; it does not duplicate intelligence

Monitoring Runtime should orchestrate existing capabilities:

```text
Monitoring Runtime
      ↓
curated capability fabric
      ↓
A2 / A3 / A4 / A5 / future Sector / Forecast / Signal
```

It should not reimplement technical analysis, sector analysis, position intelligence, or forecasting.

---

## 22. Monitor-compatible capabilities

Not every capability should automatically be schedulable.

Future discovery metadata may need to state whether a capability is:
- monitoring-compatible;
- recurrence-safe;
- replay-safe;
- event-safe.

This likely interacts with pluggability R2/R3 later.

---

## 23. Three-layer mental model

```text
SUBSCRIBER INTENT LAYER
Apps / optional watchlists / mandates
          ↓
MONITORING ORCHESTRATION LAYER
cadence / triggers / dedupe / admission / budget / scheduling
          ↓
INTELLIGENCE LAYER
A2 / A3 / A4 / A5 / future capabilities
```

Underneath:

```text
shared evidence fabric
```

---

## 24. Centralized optimization

Across all active `WLij` and direct mandates, TI can compile one active mandate set.

Example: RELIANCE appears in seven mandates.

Compatible work may be shared:
- 5m candles fetched once;
- fresh-enough news reused;
- identical deterministic feature computation reused;
- interpretation remains separate per mandate.

This is a major reason to centralize monitoring execution.

---

## 25. Freshness is mandate-dependent

Long-term monitoring may tolerate slower evidence; intraday monitoring may require minute-level freshness.

Independent evidence-family clocks remain useful.

Most apps should specify an intent/profile rather than every low-level clock.

---

## 26. Monitoring profiles

Possible versioned profile fields:

```text
horizon defaults
cadence/freshness bounds
required capabilities
optional capabilities
budget
priority
```

Profiles could become COLD-pluggable policies.

---

## 27. Scheduled + event-driven

A mandate may evaluate:
- every N minutes;
- on price trigger;
- on sector-state change;
- on important news;
- on other governed events.

Cadence and events can coexist.

---

## 28. Priority and budgets

Examples:

```text
active position risk → CRITICAL
long-term research watch → NORMAL
```

Priority never grants authority.

Budgets may exist at subscriber/subscription/mandate levels and should reuse existing budget-gateway concepts.

---

## 29. Admission

External callers must not be able to request unbounded work.

Admission should eventually consider:
- authority;
- universe;
- active-mandate limits;
- cadence bounds;
- cost budget;
- capability availability;
- system capacity.

Possible outcomes:
- ACCEPTED;
- PARTIALLY_ACCEPTED;
- REJECTED.

Exact v1 behavior TBD.

---

## 30. Idempotency and retries

External apps may retry after timeout.

A subscriber request/idempotency identity should prevent accidental duplicate mandates.

---

## 31. Lease semantics

For external subscribers, a lease may prevent abandoned forever-monitoring after app failure.

Possible:

```text
lease_until
```

with renewal.

A future review should decide whether `valid_until` alone is sufficient for v1.

---

## 32. Watchlist mutation and historical audit

Apps may add/remove instruments, change cadence/horizon, pause/resume, or expire lists.

Historical admitted mandates/results should remain auditable.

Do not silently rewrite historical monitoring intent.

---

## 33. Result lineage

Every monitoring result should preserve enough lineage to identify:

```text
subscriber
subscription
watchlist/group ref
mandate
run/evaluation ID
instrument
horizon
as_of
policy
capability composition
```

This is crucial for replay/debugging.

---

## 34. Monitoring results never imply execution

A result such as:

```text
position thesis weakened
```

does not mean a broker action occurred.

TM remains execution/action governor.

---

## 35. Push vs pull is transport

Subscribers may later consume results via:
- pull;
- callback;
- event/message;
- internal handoff.

Transport must not alter monitoring domain semantics.

---

## 36. Persistence and restart recovery

Durable mandates likely need persistence.

Initial implementation should follow deployment architecture:
- local;
- single writer;
- filesystem may be sufficient.

DB/queue/service only when demonstrated need appears.

---

## 37. At-least-once vs exactly-once

Do not promise exactly-once scheduling unnecessarily.

Likely future model:

```text
at-least-once scheduling
+ idempotent run identity
```

For example:

```text
mandate_id + scheduled_run_id
```

---

## 38. Missed runs

Potential future policies:
- SKIP_MISSED;
- COALESCE_TO_LATEST;
- REPLAY_MISSED.

For live markets, coalescing to current state may often be preferable.

No authoritative choice yet.

---

## 39. A5 reconciliation

A5 already promoted a minimal immutable `MonitoringNeed` / `WatchMandate` subset.

v2 should preserve:
- identity/lineage;
- advisory lifecycle/freshness/trigger intent.

A5 should emit monitoring intent, not own:
- scheduler;
- queue;
- retry;
- persistence;
- dispatch.

The future review must decide whether A5 `WatchMandate` is the same object as the broader runtime `MonitoringMandate`, a subtype, or an intent that gets normalized into one.

---

## 40. Lifecycle-state reconciliation

Earlier monitoring states included:

```text
PASSIVE
ACTIVE_WATCH
ACTIVE_POSITION
INACTIVE
```

These may be mixing:
- mandate lifecycle;
- subscriber purpose;
- TM position linkage.

Future architecture should separate these dimensions where appropriate.

---

## 41. Pluggability classification

Tentative:

```text
Monitoring contracts      STRUCTURAL
Scheduler                 COLD + REPLACEABLE
Event adapters            COLD + OPTIONAL
Persistence backend       COLD + REPLACEABLE
Notification adapters     COLD + OPTIONAL
Adaptive scheduler        OPTIONAL
Telemetry                 OPTIONAL
```

No HOT implementation replacement needed initially.

---

## 42. R2–R5 interaction

Future pluggability work likely affects monitoring:

- R2 discovery metadata → useful for monitor-compatible capability discovery;
- R3 composition envelope/pinned verifier → useful for exact run composition/replay;
- R4 optional adapter isolation → useful for optional providers/event adapters;
- R5 COLD ownership/configuration → useful for scheduler/persistence/profile selection.

Do not pull those implementations into this TBD.

---

## 43. Roadmap ownership questions

Likely mapping to revisit:
- A8: TM integration / active-position linkage;
- A9: scanner/candidate intake;
- A10: durable scheduler, dispatch, retries, persistence, telemetry.

The review may revise this mapping.

---

## 44. Conceptual model

```text
                 SUBSCRIBER APPLICATIONS
       ┌────────────┬────────────┬────────────┐
       │            │            │            │
     APP1          APP2          TM         Scanner
       │            │            │            │
   WL11/WL12    WL21/WL22/...   positions   candidates
       │            │            │            │
       └────────────┴────────────┴────────────┘
                         │
                         ▼
               MONITORING SUBSCRIPTIONS
                         │
                         ▼
                  MONITORING MANDATES
                         │
             ┌───────────┼────────────┐
             │           │            │
          cadence      triggers     lifetime
          horizon      priority     max-runs
             │           │            │
             └───────────┼────────────┘
                         ▼
               MONITORING ORCHESTRATOR
                         │
          ┌──────────────┼───────────────┐
          │              │               │
     shared evidence   dedupe          budgets
          │              │               │
          └──────────────┼───────────────┘
                         ▼
                  TI CAPABILITY FABRIC
          ┌──────────────┼───────────────┐
          │              │               │
         A2             A3/A4            A5
                                      future:
                           Sector / Forecast / Signal
                         │
                         ▼
                 MONITORING RESULT
                         │
                         ▼
                  owning subscriber
```

---

## 45. Ownership summary

### Subscriber app owns
- business purpose;
- conceptual watchlists/grouping;
- instruments;
- labels/tags;
- horizon intent;
- requested intelligence profile;
- cancellation/lifetime intent.

### TI owns
- admission;
- normalized mandate;
- scheduling;
- trigger handling;
- dedupe;
- evidence freshness;
- shared acquisition;
- budget enforcement;
- capability invocation;
- replay/audit;
- result lineage;
- failure isolation.

### TM owns
- position truth;
- action governance;
- execution authority.

---

## 46. Central architecture questions for authoritative review

1. Should watchlists remain subscriber-owned opaque groupings?
2. Should `MonitoringMandate` be the fundamental monitoring object?
3. Is a distinct `MonitoringSubscription` type worth keeping?
4. Should one-shot evaluation and recurring monitoring be separate?
5. How should A5 `WatchMandate` map to general monitoring?
6. Which lifecycle states belong to mandate vs purpose vs TM linkage?
7. How should horizon/cadence/freshness/lifetime/repetition be represented?
8. What minimum state must be persisted for restart/replay?
9. Which capabilities are monitor-compatible?
10. Which R2–R5 items are prerequisites?
11. Should internal and external subscribers share one conceptual contract?
12. What is the smallest viable runtime without premature scheduler/platform complexity?

---

## 47. Explicit non-goals

Do NOT implement from this note:
- scheduler;
- queue;
- DB;
- remote API;
- notification transport;
- watchlist CRUD;
- lease engine;
- adaptive cadence;
- event bus;
- SaaS infrastructure;
- Sector Rotation;
- Signal Qualification;
- R2–R5 remediation.

---

## 48. Promotion rule

Before promotion:
- reconcile with A5;
- reconcile with pluggability;
- reconcile with deployment;
- reconcile with facade/capability fabric;
- reconcile with TM;
- settle ownership/lifecycle/persistence/admission;
- map work to later milestones.

---

## 49. Final thesis

> **TI Monitoring should be subscriber-driven, mandate-centric and capability-oriented.**

Subscriber apps own business intent and optional watchlist groupings.

TI owns governed execution of admitted monitoring mandates over shared evidence and pluggable intelligence capabilities.

TM remains position truth and action authority.

The central conceptual shift is:

> **Watchlist is optional grouping; MonitoringMandate is the fundamental monitoring semantic unit.**

And the key runtime principle is:

> **Deduplicate evidence acquisition, not subscriber intent.**
