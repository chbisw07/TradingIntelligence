# TI System Architecture Thesis

## Executive thesis

TradingIntelligence (TI) should be organized around a stable architectural center:

> **TI_CORE is the intelligence kernel. TI exposes a curated, typed, versioned capability surface. TI_SHELL, TI_WEB, Agents, TradeMonitor, scanners, scripts, and external applications consume those capabilities without depending on Core internals.**

This does **not** move TI away from its original goal. It protects that goal as the system grows. The original objective remains to build a disciplined trading-intelligence system that can combine evidence, deterministic computation, specialist reasoning, later higher-intelligence reasoning, forecasting, risk controls, explainability, and eventually position/trade-expression intelligence.

The purpose of this architecture is not to add layers for their own sake. It is to prevent duplicated logic, conflicting paths, vendor lock-in, interface lock-in, and accidental coupling between user experience and intelligence policy.

---

## 1. Why this is not overengineering

TI already contains multiple independently valuable capabilities: evidence acquisition, deterministic features, baseline opportunity assessment, specialist intelligence, orchestration, deep research, provider routing, authoritative confirmation, structured opportunity synthesis, replay, and audit.

Future milestones add arbitration, position intelligence, option/future expression, forecasting, TradeMonitor integration, scanner integration, and product interfaces.

Without an explicit top-level architecture, the likely failure mode is gradual divergence:

- CLI calls one path.
- Web implements another.
- Agents acquire their own evidence.
- TradeMonitor calls internal modules directly.
- External scripts depend on unstable internals.

The proposed architecture prevents that while still allowing TI to remain a single repository and largely in-process for as long as that is practical.

> **Logical modularity does not require premature microservices.**

---

## 2. Top-level architecture

```text
                           TI ECOSYSTEM

                Humans / Developers / Operators
                            │
                            ▼
                    ┌───────────────┐
                    │   TI_SHELL    │
                    │ Native CLI    │
                    │ REPL/session  │
                    │ NLP / Agents  │
                    │ Help/inspect  │
                    │ Trace/replay  │
                    └───────┬───────┘
                            │

     ┌──────────────────────┼────────────────────────────┐
     │                      │                            │
   TI_WEB                TI Agents                   Scripts/Tools
     │                      │                            │
     │                GPT / Claude                       │
     │              or other models                      │
     │                                                   │
     ├──────────────────────┼────────────────────────────┤
     │                      │                            │
 TradeMonitor          Internal Apps               External Apps
 Scanners              / Services                  / Integrations
     │                      │                            │
     └──────────────────────┴────────────┬───────────────┘
                                         │
                           ╔═════════════▼═════════════╗
                           ║ TI PUBLIC CAPABILITY API ║
                           ║ Curated / Typed          ║
                           ║ Versioned / Governed     ║
                           ║ Stable / Auditable       ║
                           ╚═════════════╤═════════════╝
                                         │
                           ╔═════════════▼═════════════╗
                           ║        TI_CORE            ║
                           ║ Intelligence Kernel       ║
                           ║                           ║
                           ║ A1 Evidence               ║
                           ║ A2 Deterministic          ║
                           ║ A3 Intelligence           ║
                           ║ A4 Arbitration            ║
                           ║ A5 Position Intelligence ║
                           ║ A6 Trade Expression       ║
                           ║ A7 Forecast/Learning      ║
                           ╚═══════════════════════════╝
```

---

## 3. TI_CORE

TI_CORE owns canonical intelligence behavior.

It contains or coordinates:

- evidence contracts and semantic normalization;
- deterministic calculations;
- A2 baseline intelligence;
- A3 specialists and orchestration;
- structured opportunity intelligence;
- later arbitration/challenge;
- later forecasting;
- later position intelligence;
- later option/future expression;
- replay and semantic fingerprints;
- evidence lineage and provenance;
- canonical risk/authority rules that belong to TI;
- model-assisted reasoning only where explicitly authorized.

The Core should not care whether the caller is CLI, Web, Agent, scanner, TradeMonitor, or a third-party application.

---

## 4. TI Public Capability API

TI should **not expose everything** inside TI_CORE.

It should expose a deliberate set of useful, stable capabilities, analogous in spirit to a broker exposing meaningful APIs rather than its internal implementation.

Possible future capability families:

```text
get_market_evidence(...)
get_company_research(...)
get_technical_intelligence(...)
get_baseline_opportunity(...)
orchestrate_opportunity(...)
get_opportunity_intelligence(...)
compare_opportunities(...)
get_forecast(...)
get_position_intelligence(...)
get_trade_expression(...)
replay_analysis(...)
```

Requirements:

- typed;
- provider-neutral;
- framework-neutral;
- versioned;
- governed;
- documented;
- auditable;
- stable enough for external consumers.

Internal modules such as LangGraph nodes, reducer helpers, provider normalizers, cache internals, projection helpers, and policy utilities remain private.

---

## 5. Three interface levels

### Public capabilities
For Shell, Web, TradeMonitor, scanners, scripts, approved Agents, and external applications.

### Engineering capabilities
For inspection, diagnostics, testing, replay, trace, evidence-graph inspection, budget-ledger inspection, provider-normalization debugging, etc.

### Private Core internals
Implementation details free to evolve.

This protects API stability without limiting engineering visibility.

---

## 6. TI_SHELL

TI_SHELL is the stateful interactive interpreter and mediator for humans and engineering work.

It owns interaction concerns:

- command parsing;
- REPL/session context;
- natural-language routing;
- Agent invocation;
- help/discovery;
- rendering;
- trace/replay inspection;
- developer diagnostics.

It does **not** own technical analysis rules, fundamental policy, opportunity synthesis rules, forecasting logic, or trading policy.

A dedicated TI_SHELL thesis defines this in detail.

---

## 7. TI_WEB

TI_WEB is a separate application over the same public capability API.

It must not contain a private intelligence implementation.

A Web action such as “Analyze KAYNES” should invoke the same semantic capability used by TI_SHELL or an external program.

---

## 8. Agents and models

Agents are architectural components. Models are replaceable reasoning engines.

Examples:

- Interaction Agent;
- Research Agent;
- Comparison Agent;
- Forecast Interpretation Agent;
- Position Intelligence Agent.

An Agent owns:

- purpose;
- allowed capabilities;
- context;
- authority;
- budget;
- model policy.

The model may be GPT-6 Astra, Claude, another model, or no model.

TI_CORE must not depend on one LLM vendor.

---

## 9. Intelligence profiles

The architecture should support future product tiers without creating separate TI implementations.

Conceptually:

- DETERMINISTIC
- BALANCED
- DEEP

DETERMINISTIC emphasizes reproducibility and low cost.

BALANCED adds selective reasoning and enrichment.

DEEP may authorize broader evidence, stronger model reasoning, deeper research, later A4 challenge, and later A7 forecast intelligence.

The deterministic baseline remains visible in all profiles.

---

## 10. Shared evidence, isolated request state

Multiple applications may reuse immutable evidence, but their intent must remain isolated.

Example:

```text
User A: KAYNES positional, 2–6 weeks
User B: KAYNES intraday
TradeMonitor: active KAYNES option position
```

They may share company/news/market evidence but must not share:

- request intent;
- horizon;
- authority;
- budget;
- position context;
- intelligence profile.

> **Shared Evidence ≠ Shared Analysis State**

---

## 11. Concurrency and cooperation

The architecture should permit multiple consumers without unnecessary duplicate acquisition.

```text
App A ─┐
App B ─┼──> one eligible immutable acquisition
App C ─┘
```

Reuse is allowed only when identity, freshness, point-in-time semantics, authorization, and policy permit it.

A3.8's single-flight, reservation, immutable publication, and selective invalidation ideas provide a useful foundation.

---

## 12. Event-driven future

Later TI may publish events such as:

- material filing admitted;
- market snapshot changed;
- earnings result arrived;
- forecast updated;
- position context changed.

Events should trigger only affected capabilities/subscribers, not full-system recomputation.

---

## 13. TradeMonitor relationship

TradeMonitor remains distinct.

TI provides intelligence.

TradeMonitor owns:

- position lifecycle;
- execution governance;
- broker-state reconciliation;
- broker interaction;
- final execution authority.

A future flow:

```text
TradeMonitor
    ↓
get_position_intelligence(...)
    ↓
TI
    ↓
structured intelligence
    ↓
TradeMonitor policy/action
```

---

## 14. Scanner relationship

Scanners are sensors/discovery systems.

They find candidates. TI evaluates them.

```text
Scanner → candidate set → TI capability → intelligence → consumer
```

Scanner logic must not redefine canonical TI intelligence semantics.

---

## 15. Provider independence

Tapetide, Yahoo, Dhan, NSE/BSE, company IR, and future providers are acquisition mechanisms.

Public capabilities request semantic evidence or intelligence, not provider-specific transport behavior.

Provider identity remains visible in provenance/audit, not in consumer-facing business logic.

---

## 16. Stability objective

The architecture succeeds if we can later:

- replace LangGraph;
- change model vendor;
- add/remove providers;
- refactor specialists;
- replace Web technology;
- change caching;
- upgrade forecasting;

without forcing every consumer to change.

That is the principal long-term value of the capability boundary.

---

## 17. Complexity guardrails

To avoid unnecessary complexity:

- keep one repository while useful;
- prefer in-process APIs initially;
- avoid distributed queues/services until justified;
- do not publish every internal method;
- do not add an abstraction unless it protects a real boundary;
- do not allow Shell/Web/Agent-specific intelligence logic.

The architecture is intended to **reduce future complexity**, not increase current operational complexity.

---

## 18. Architectural laws

1. TI_CORE owns intelligence.
2. Public consumers use curated typed capabilities.
3. TI_SHELL owns interaction, not market logic.
4. TI_WEB owns UX, not market logic.
5. Agents use permitted capabilities.
6. Models are replaceable.
7. Natural language is not an authority channel.
8. Shared evidence does not imply shared analysis state.
9. Public capabilities are stable; internals may evolve.
10. No consumer gets an undocumented privileged intelligence path.
11. Deterministic evidence remains foundational in higher-intelligence modes.
12. TradeMonitor retains execution/governance authority.
13. Provider identity is provenance, not business logic.
14. Logical boundaries do not imply microservices.
15. Every future milestone should identify:
   - what belongs in Core;
   - what capability is published;
   - whether Shell exposes it;
   - whether Web exposes it;
   - whether Agents can invoke it;
   - what external consumers may depend on.

---

## 19. Roadmap alignment

A3.9: structured opportunity intelligence inside Core.

A3.10: replay/baseline/cost/failure hardening.

Post-A3 consolidation: formalize this architecture, capability catalog, TI_SHELL, citation/provenance presentation, and roadmap alignment.

A4: challenge/arbitration capability.

A5: position-intelligence capability.

A6: option/future expression capability.

A7: forecast/learning capability.

A8: TradeMonitor integration through published capabilities.

A9: scanner integration through candidate/opportunity capabilities.

A10: operational hardening/deployment/observability.

---

## 20. Final thesis

This architecture does not deviate from TI's purpose. It gives the existing work a stable system shape.

> **TI_CORE is the intelligence kernel. TI publishes only intentional, governed capabilities. TI_SHELL is the principal interactive human/engineering interface. TI_WEB, Agents, TradeMonitor, scanners, scripts, and external applications consume the same stable capability surface. Models and providers remain replaceable.**

This should become the organizing architecture for remaining TI work.
