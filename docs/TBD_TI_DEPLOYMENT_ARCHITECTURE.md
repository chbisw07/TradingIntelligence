# TBD — TI Deployment Architecture

**Status:** Reviewed; bounded architecture promoted with revisions, 2026-09-11 (Asia/Kolkata)

**Authority:** Historical hypothesis, not a parallel specification

**Purpose:** Preserve the original deployment proposals and their explicit disposition.

**Do not treat this document as an implementation directive.**

The authoritative [deployment architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md)
now selects a trusted local Python runtime, isolated invocation state and
filesystem replay, with explicit gates for later services/workers/storage.
The [deployment review](TIAF_POST_A3_DEPLOYMENT_ARCHITECTURE_REVIEW.md) classifies
every original section in §4 and concludes `READY_FOR_POST_A3_CONSOLIDATION`.
Level 3's infrastructure menu and illustrative profile names remain conditional
TBDs; no service, queue, database, container or cloud runtime is implemented.

Numbered sections below retain the original proposal for traceability. Their
"future review"/"current decision" wording is historical, superseded by the
review where indicated. The [completed consolidation](TIAF_POST_A3_CONSOLIDATION_AND_REPLANNING.md)
retains disposition SPLIT and selects POST_A3_PRE_A4_FOUNDATION next, then narrow
local facade/lifecycle and deterministic A4. No unrelated TBD
or infrastructure rollout is authorized by this promotion.

## 1. Why this document exists

TradingIntelligence now has an emerging logical architecture:

- `TI_CORE` as the intelligence kernel;
- a curated, typed, governed capability boundary;
- `TI_SHELL`, `TI_WEB`, Agents, TradeMonitor, scanners, scripts and future external applications as consumers of those capabilities.

The logical architecture intentionally does **not** prescribe process boundaries, network protocols, microservices or deployment topology.

Deployment architecture is therefore a separate concern:

> **Logical architecture defines what owns what. Deployment architecture defines where those responsibilities run, how they communicate, what state they share, and how they are isolated operationally.**

This TBD preserves the deployment questions without forcing answers prematurely.

## 2. Hard invariant

> **Deployment must preserve the accepted logical TI architecture rather than redefine it.**

Changing deployment topology must not create alternative intelligence semantics.

- moving a capability from an in-process call to a local service must not change its meaning;
- Web must not gain a separate intelligence implementation;
- Shell must not become the intelligence engine;
- TradeMonitor authority must not move into TI merely because it becomes a remote consumer;
- provider adapters must remain replaceable;
- model providers must remain replaceable;
- replay semantics must remain valid regardless of deployment topology.

## 3. Deployment should evolve in stages

### Level 0 — Development / current repository model

```text
single machine
single repository
in-process Python
local scripts / acceptance tools
filesystem replay/corpus
provider adapters
```

### Level 1 — Local engineering TI

```text
TI_SHELL
   |
local curated capability facade
   |
TI_CORE
   |
provider/model/storage adapters
```

Characteristics:
- one machine;
- primarily in-process;
- Shell becomes a primary engineering interface;
- stable public/engineering capability subset;
- local replay/audit;
- no requirement for remote service deployment.

### Level 2 — Multi-application local/service deployment

```text
TI_SHELL
TI_WEB
TradeMonitor
Scanners
External local tools
      |
      v
local TI service / capability boundary
      |
    TI_CORE
```

Questions:
- in-process vs IPC vs local HTTP/gRPC;
- shared evidence/cache;
- concurrency;
- credentials;
- authorization;
- long-running work;
- process restart;
- persistent state.

### Level 3 — Production / distributed deployment

```text
remote clients
     |
TI service/API
     |
runtime/workers
     |
TI_CORE capabilities
     |
providers / storage / model adapters
```

Potential concerns:
- multi-user authentication/authorization;
- service discovery;
- durable queue;
- distributed cache;
- persistent Evidence Graph;
- scheduler;
- observability;
- retries/circuit breakers;
- secrets management;
- scaling;
- retention;
- disaster recovery;
- SLOs.

This level is **not authorized merely by this document**.

## 4. Questions to answer during future review

### Process topology
- Which components should initially run in one process?
- Should TI_SHELL share a process with TI_CORE?
- When should TI_WEB become a separate process?
- Should TradeMonitor call TI in-process, locally, or remotely?
- When is a worker process justified?

### Capability exposure
- Which capabilities are in-process only?
- Which are safe for remote exposure?
- Which engineering capabilities must remain local/admin-only?
- Which operations require explicit live-data effects?

### State ownership
- What remains request-local?
- What state is reusable across consumers?
- Where do caches live?
- Where does replay/corpus storage live?
- Where does Evidence Graph state live?
- What survives restart?

### Security and authority
- Where are provider credentials stored?
- Where are model credentials stored?
- How is caller identity established?
- How is entitlement enforced?
- How is developer/admin access separated?
- How does TradeMonitor authority remain external?

### Concurrency
- How do multiple consumers share evidence safely?
- How is single-flight acquisition coordinated?
- How are budgets/reservations enforced across processes?
- How are stale or late results prevented from contaminating active requests?

### Long-running work
- When are queues required?
- Who owns retry/backoff?
- How is checkpoint/resume handled?
- How are scheduled monitoring and outcome acquisition implemented?
- How is cancellation/preemption represented honestly?

### Observability
- What should be logged?
- What metrics are needed?
- What is semantic audit vs operational telemetry?
- How are provider/model costs observed?
- What information must never leak into logs?

## 5. TI_SHELL deployment questions

TI_SHELL is expected to be a primary engineering interface, but its physical placement is not yet decided.

Possible initial model:

```text
TI_SHELL and TI_CORE
same machine
same Python environment
direct typed capability invocation
```

Future alternative:

```text
TI_SHELL
   |
local/remote capability transport
   |
TI service / TI_CORE
```

The Shell must not depend on process location.

Its commands and Agent/NLP behavior should target semantic capabilities, not internal module paths or subprocess output.

## 6. TI_WEB deployment questions

TI_WEB should remain a separate consumer of TI capabilities.

Questions:
- local embedded Web app vs separate service;
- session state ownership;
- streaming progress;
- async job handling;
- browser authentication;
- multi-user isolation;
- result caching;
- visualization storage.

Web must never become a second intelligence implementation.

## 7. TradeMonitor relationship

TradeMonitor remains operational governor and execution coordinator.

```text
TradeMonitor -> TI intelligence capability
TI -> structured intelligence
TradeMonitor -> policy/lifecycle/execution decision
Broker -> final execution truth
```

A network boundary must not imply authority transfer.

## 8. Shared evidence vs shared mutable state

Preserve:

> **Shared Evidence != Shared Analysis State**

Deployment may enable shared evidence/cache, but each request must retain independent:
- objective;
- horizon;
- `as_of`;
- authority;
- budget;
- profile;
- position context;
- run identity;
- specialist/orchestration state.

No symbol-only global mutable analysis state.

## 9. Provider/model adapter deployment

Provider and model adapters may eventually run:
- in-process;
- as isolated local workers;
- as remote services.

Their location must not leak into TI domain contracts.

Transport/adapters remain infrastructure.

## 10. Persistence strategy

Do not assume every state requires a database.

```text
filesystem
    ->
embedded/local DB
    ->
shared DB/cache
    ->
distributed storage
```

Potential persisted domains:
- evidence;
- replay packages;
- Evidence Graph;
- monitoring mandates;
- forecast outcomes;
- audit;
- usage/cost;
- jobs.

Each requires its own retention and consistency semantics.

## 11. Microservices non-goal

> **A logical component is not automatically a process.**

Avoid premature:
- microservices;
- event buses;
- service mesh;
- distributed locks;
- remote registries;
- container orchestration.

Introduce them only when scale, isolation, reliability or organizational boundaries justify them.

## 12. Deployment profiles may eventually exist

Illustrative future profiles:

```text
DEV_LOCAL
ENGINEERING_LOCAL
SINGLE_USER_SERVICE
MULTI_APP_LOCAL
PRODUCTION_MULTI_USER
```

A deployment profile must not alter canonical intelligence semantics.

## 13. Relationship to existing deferrals

Reconcile later with:
- DEF-003 — public capability/service/API surface;
- DEF-009 — persistent/distributed cache and telemetry;
- DEF-010 — durable queues/retry/checkpoint/resume;
- DEF-011 — provider health/degradation;
- DEF-049 — historical PIT reconstruction;
- DEF-050 — persistent/distributed replay;
- DEF-051 — scheduled outcome acquisition;
- DEF-055 — monetary pricing/cost attribution.

Do not create duplicate DEF records solely from this document.

## 14. Planned revisit

```text
Post-A3 Deep Architecture Pass 1
    TI_CORE + capability boundary
        DONE

Post-A3 Deep Architecture Pass 2
    Source Authority / Provenance / Contradiction semantics

Post-A3 Deep Architecture Pass 3
    A4 Challenge / Arbitration / Higher-Intelligence Agents

Deployment Architecture Review
    revisit this TBD deeply

Full post-A3 consolidation
    reconcile roadmap / TBDs / deferrals / fresh work plan

Then authorize bounded pre-A4 foundation / A4
```

## 15. Success criterion for future promotion

Before promotion, define:
- supported deployment levels;
- process boundaries;
- state ownership;
- persistence boundaries;
- capability transport;
- security/credential model;
- concurrency model;
- long-running work model;
- observability;
- recovery;
- upgrade/version compatibility;
- local-development topology;
- future production topology;
- explicit non-goals.

The promoted design should preserve logical TI semantics independent of topology.

## 16. Current decision

> **Capture deployment concerns, do not implement them.**

The immediate project focus remains the next post-A3 deep architecture pass.
