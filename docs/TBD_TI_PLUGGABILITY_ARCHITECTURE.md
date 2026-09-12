# TBD — TI Pluggability Architecture

**Status:** PARTIALLY PROMOTED / retained exploratory history

**Authority:** Non-authoritative idea cache  
**Purpose:** Preserve the philosophy, terminology, architectural invariants and future work needed to make pluggability a first-order property of TradingIntelligence (TI).  
**Implementation status:** Not implemented by this document.

## Promotion disposition — 2026-09-12

The authoritative [TI Pluggability Architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md)
now governs this topic. The numbered sections below remain idea history, not
competing authority or current implementation claims.

| Disposition | Idea-cache sections | Resolution |
|---|---|---|
| PROMOTED | 1, 5–8, 10–18, 22, 28–32, 35 | First-order baseline invariant, governed dependencies/composition, separate Agent/model roles, failure/authority/cost boundaries and no generic plugin framework; refined by the authoritative document. |
| PROMOTED WITH REVISION | 2–4, 9, 21, 23–25, 27 | Nested HOT ⇒ COLD ⇒ STRUCTURAL; no STATIC enum; REQUIRED/OPTIONAL scoped presence plus independent traits; descriptor separated from scoped availability; immutable composition and distinct run fingerprints. |
| THOUGHT EXPERIMENT ONLY | 19–20 | Sector Rotation and Signal Qualification test future pluggability, not implemented or promoted capability designs. |
| PLANNED NEXT, NOT PERFORMED | 33, 36 | Dedicated A1–A5 compliance audit precedes conditional remediation and regression/composition/replay acceptance. Audit classifications are separate axes, not the original mixed enum. |
| REMAINS TBD | 26, 34, detailed 24–25 | Scientific metrics/calibration, concrete schemas/migration and audit-proven remediation; HOT runtime engineering requires a demonstrated need (DEF-057). |
| REVISED / REJECTED | 2–3, 9, 21, 30, 37 | No exception to HOT implying COLD; no overlapping lifecycle/role enums, mutable descriptor health, installed-equals-usable claim or automatic public export. Architecture promotion is not implementation/compliance acceptance. Remote transport stays separate. |

Governance policy never becomes consumer-modifiable through configuration.
Required safety dependencies are not optional; a failed capability has no market
stance. Historical replay never adopts later-installed contributors. These
resolved decisions supersede tentative wording below. No runtime framework,
compliance audit, A5 freeze or A6 work is delivered by this promotion.

## 1. Executive thesis

> **Pluggability should be a first-order architectural property of TI.**

TI should have a stable baseline that works on its own, while optional capabilities, intelligence contributors, Agents, providers, policies and adapters can be attached, configured, enabled, disabled, replaced or omitted without redesigning the baseline.

A capability may participate only when it is implemented, configured, enabled, authorized, data-ready, policy-compatible and healthy.

If it cannot safely participate, TI should continue honestly with the remaining valid baseline rather than fabricate substitute intelligence.

## 2. Three kinds of pluggability

### Structural pluggability
A component is structurally pluggable when it is replaceable, omittable or composable behind a stable contract, even if changing it requires code/configuration changes and restart.

### Cold pluggability
A component is cold-pluggable when its presence, implementation or enablement can be configured before TI starts.

### Hot pluggability
A component is hot-pluggable when it can be added, removed, enabled, disabled or replaced while TI is running without violating state, replay, authority or consistency guarantees.

Preferred hierarchy:

```text
HOT
  implies
COLD
  implies
STRUCTURAL
```

A capability declared HOT should normally also support equivalent startup configuration. Exceptions must be explicit.

## 3. Lifecycle and optionality are separate

Lifecycle mode:

```text
STATIC
COLD
HOT
```

Architectural role:

```text
REQUIRED
OPTIONAL
REPLACEABLE
COMPOSABLE
```

Example:

```text
A2 baseline
  lifecycle: STATIC
  role: REQUIRED

sector.rotation
  lifecycle: COLD initially
  role: OPTIONAL + COMPOSABLE

market-data provider
  lifecycle: COLD
  role: REPLACEABLE
```

## 4. Effective availability

Installed does not mean usable.

Possible dimensions:

```text
implemented
installed
configured
enabled
authorized
data-ready
policy-compatible
healthy
```

Possible effective states:

```text
AVAILABLE
DISABLED
NOT_INSTALLED
UNAUTHORIZED
INSUFFICIENT_DATA
UNSUPPORTED
DEGRADED
FAILED
```

Exact enum names remain TBD.

## 5. First-order invariants

1. Baseline must survive optional-feature absence.
2. Optional intelligence must be explicit, never hidden.
3. Pluggability must preserve replay and provenance.
4. Capability presence never grants authority.
5. Unavailable is different from negative.
6. HOT should imply COLD; COLD should imply structural.
7. Configuration never fakes readiness.
8. Plugin failure degrades honestly.
9. Composition must be inspectable.
10. Every optional capability should eventually prove incremental value.
11. No arbitrary code loading.
12. Do not overengineer HOT lifecycle where COLD is sufficient.

## 6. Presence / enablement / failure independence

If Sector Rotation is not installed:

```text
sector.rotation = NOT_INSTALLED
```

TI continues without it.

If installed but disabled:

```text
sector.rotation = DISABLED
```

TI continues without it.

If it fails:

```text
sector.rotation = FAILED
```

TI may continue with a partial/qualified result unless the request explicitly requires that capability.

## 7. Baseline preservation

Optional intelligence should enrich or challenge a baseline rather than erase it.

```text
Run A: baseline
Run B: baseline + sector.rotation
Run C: baseline + sector.rotation + forecast
```

This enables scientific comparison of whether a capability added economic value.

## 8. Composition manifest

Every enriched result should preserve a composition record such as:

```text
requested_capabilities
used_capabilities
disabled_capabilities
unavailable_capabilities
failed_capabilities
versions
policy
dependency graph
```

Example:

```text
used:
  technical@2.1
  fundamental@1.4
  sector.rotation@1.0

unavailable:
  signal.qualify
  forecast.return
```

## 9. Capability descriptor

A future descriptor may include:

```text
capability_id
semantic_version
interface_level
role
lifecycle_mode
optionality
required_dependencies
optional_dependencies
input_contract
output_contract
authority_requirements
data_requirements
effect_class
deterministic/model-backed
replay_support
cost_class
health
availability
deprecation/replacement
```

Implementation bindings remain private.

## 10. Required vs optional dependencies

Required dependency missing:

```text
capability unusable
```

Optional dependency missing:

```text
capability valid but degraded
```

Example:

```text
sector.rotation
required:
  sector.membership
  market.price

optional:
  institutional.flows
  analyst.revisions
```

## 11. Request-specific requirements

A capability can be optional globally yet mandatory for a request.

Cash-equity analysis can proceed without derivatives.

An option-spread request cannot proceed if derivatives intelligence is unavailable.

Dependencies therefore belong partly to request/policy semantics.

## 12. Same-level intelligence composition

Peer intelligence modules should not be hard-wired into arbitrary linear chains.

Possible peers:

```text
Opportunity Intelligence
Sector Rotation
Signal Qualification
Market Regime
Relative Leadership
Forecast Evidence
```

Preferred:

```text
peer contributors
      ↓
typed composition
      ↓
higher-order reasoning / A4
```

unless a genuine dependency exists.

## 13. Pluggable component families

Pluggability should apply, where appropriate, to:

- evidence providers;
- intelligence capabilities;
- specialist Agents;
- higher-reasoning Agents;
- model providers;
- policies;
- workflow adapters;
- consumers;
- feature families.

## 14. Providers

Provider substitution should remain adapter/configuration work.

No specialist should depend on provider transport.

## 15. Agents

Agents should declare:

- purpose;
- allowed capabilities;
- required evidence;
- authority;
- budget;
- model policy;
- version.

Optional Agent absence must be handled explicitly.

## 16. Models

Models are replaceable reasoning engines:

```text
NO_MODEL
GPT
Claude
local model
future provider
```

No-LLM mode remains valid.

## 17. Policies

Policies may also be pluggable:

- A4 arbitration policy;
- A5 position policy;
- sector-rotation policy;
- signal-qualification policy;
- ranking policy;
- monitoring policy.

Policy identity/version must be captured for replay.

## 18. Workflow adapters

Example:

```text
serial reference runner
LangGraph adapter
```

Domain semantics must remain independent of workflow implementation.

## 19. Sector Rotation as a key test

Desired future flow:

```text
sector.rotation not installed
        ↓
TI works without it

configure/install sector.rotation
        ↓
restart TI (cold plug)
        ↓
capability AVAILABLE
        ↓
A3/A4/A5 may consume it
```

No A4/A5 redesign.

## 20. Signal Qualification as a second test

Without it:

```text
candidate signal → existing TI path
```

With it:

```text
candidate signal → signal.qualify → ACCEPT / WAIT / REJECT
```

No redesign of the rest of TI.

## 21. Capability discovery

Future Shell/API should expose capability state:

```text
baseline.assess        AVAILABLE
a4.evaluate            AVAILABLE
position.assess        AVAILABLE
sector.rotation        NOT_INSTALLED
signal.qualify         DISABLED
forecast.return        UNAVAILABLE
```

## 22. Health vs permission

A capability may be enabled but degraded.

Health does not grant permission.

Example:

```text
sector.rotation
installed      yes
enabled        yes
health         degraded
reason         incomplete breadth coverage
effective      DEGRADED
```

## 23. Configuration

Cold pluggability should be configuration-driven:

```yaml
capabilities:
  sector_rotation:
    enabled: true

  signal_qualification:
    enabled: false
```

Configuration cannot override authorization, data readiness, compatibility or health.

## 24. Hot lifecycle safety

If HOT is ever supported, define:

- activation;
- quiescence;
- in-flight request ownership;
- unload safety;
- state/cache disposal;
- replay identity;
- rollback;
- version compatibility.

HOT should not be built merely because it sounds flexible.

## 25. Replay

Historical replay must record exact composition:

- capabilities present;
- capabilities used;
- versions;
- policies;
- failures;
- availability assumptions.

Historical replay must not automatically use capabilities installed later.

## 26. Scientific evaluation

A7 should be able to compare:

```text
baseline
vs
baseline + sector.rotation
vs
baseline + signal.qualify
```

Metrics may include precision, expectancy, drawdown, ranking quality, calibration, coverage and cost.

Optional capabilities should earn their complexity.

## 27. Capability contribution attribution

Future results should explain when an optional capability changed the result.

Example:

```text
Baseline A4: SUPPORTIVE
With Sector Rotation: WAIT
Reason: sector tailwind deteriorating
```

## 28. Failure semantics

Capability failure is not a market opinion.

```text
sector.rotation FAILED
```

does not mean sector bearish.

Downstream must separate capability failure from negative intelligence.

## 29. Authority and security

Installing/enabling a capability never grants:

- data access;
- model access;
- engineering privilege;
- broker authority.

Reject arbitrary plugin loading, `eval`, `exec` or random Python module discovery.

Trusted implementations should be registered through controlled configuration.

## 30. External APIs

Pluggability should make external APIs capability-aware.

Clients should be able to discover what a TI deployment supports and adapt gracefully.

Transport remains separate from semantics.

## 31. Cost-aware composition

Optional capability execution should consider:

- materiality;
- expected information gain;
- cost;
- latency;
- evidence coverage.

Do not run every plugin merely because it exists.

## 32. Progressive enrichment

Preferred:

```text
baseline
  ↓
inspect gaps/materiality
  ↓
select useful optional capabilities
  ↓
enrich
  ↓
stop when sufficient
```

## 33. A1–A5 compliance audit

Before proceeding far into A6/A7, perform a dedicated audit.

Classify each current component:

```text
COMPLIANT
PARTIALLY_COMPLIANT
HARD_DEPENDENCY
SHOULD_BECOME_OPTIONAL
MUST_REMAIN_REQUIRED
NOT_APPLICABLE
```

Audit:

- A1 evidence/data foundation;
- A2 features/baseline;
- A3 specialists/providers/planner;
- A4 Challenger/Arbitrator;
- A5 position intelligence;
- facade;
- Shell;
- replay;
- policies.

## 34. Likely implementation work after audit

Potential remediation may include:

- richer capability descriptor;
- dependency descriptors;
- availability/health model;
- optional contributor registry;
- composition manifest;
- baseline/enriched lineage;
- policy-driven contributor selection;
- discovery enhancements;
- replay composition pinning;
- failure-isolation rules.

Implement only what the audit proves necessary.

## 35. No generic plugin framework

Do NOT build:

- arbitrary runtime plugin loader;
- plugin marketplace;
- dynamic package installer;
- generic event bus;
- service mesh;
- universal DI container.

Pluggability protects TI architecture; it should not become a framework project.

## 36. Planned work sequence

Recommended:

```text
P0 — Pluggability Architecture
P1 — A1–A5 Compliance Audit
P2 — Bounded remediation/refactoring
P3 — Regression / composition / replay acceptance
```

This should be treated as a cross-cutting workstream, not A5.x.

## 37. Promotion criteria

Before this TBD becomes authoritative, settle:

- taxonomy;
- lifecycle modes;
- descriptor contracts;
- availability;
- dependencies;
- composition;
- replay;
- security;
- compliance;
- migration/backward compatibility;
- acceptance tests.

## 38. Final thesis

> **TI should behave as a stable baseline intelligence kernel surrounded by governed, typed, configurable intelligence capabilities whose participation is explicit, replayable and optional where appropriate.**

If a capability exists and is usable, it can contribute. If it does not exist or cannot safely participate, TI continues honestly without pretending that intelligence was available.

This remains a non-authoritative `TBD_` idea cache. The promotion disposition
above identifies the ideas now governed by the authoritative architecture and
the implementation, audit and capability designs still deferred.
