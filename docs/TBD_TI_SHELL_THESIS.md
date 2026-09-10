# TI_SHELL Thesis

## 1. Thesis

TI_SHELL should become one of TradingIntelligence's primary engineering and interactive tools.

Its role is analogous in spirit to Bash, Python's REPL, or `psql`:

> **TI_SHELL is a stateful interactive mediator between a human/operator and the curated capabilities published by TI_CORE.**

It should combine:

1. exact native commands for reproducibility;
2. natural-language Agent interaction for convenience and higher-level reasoning.

Both paths converge on the same typed TI capability surface.

---

## 2. What TI_SHELL owns

TI_SHELL owns:

- command parsing;
- REPL/session behavior;
- current working context;
- native command dispatch;
- NLP routing;
- Agent invocation;
- model/profile selection for engineering use;
- help and capability discovery;
- result rendering;
- history;
- trace/explain/replay tooling;
- developer diagnostics.

TI_SHELL does not own canonical market intelligence.

---

## 3. Core interaction model

```text
                         USER
                          │
                          ▼
                  ┌────────────────┐
                  │    TI_SHELL    │
                  │                │
                  │ Native parser  │
                  │ REPL/session   │
                  │ NLP mode       │
                  │ Agent gateway  │
                  │ Help/discovery │
                  │ Inspect/trace  │
                  │ Rendering      │
                  └───────┬────────┘
                          │
                  Typed TI operations
                          │
                ┌─────────▼─────────┐
                │ TI Capability API │
                └─────────┬─────────┘
                          │
                       TI_CORE
```

---

## 4. Native command mode

Native commands are direct, precise, deterministic entry points.

Examples:

```text
TI> technical KAYNES --tf 1d
TI> fundamental KAYNES
TI> news KAYNES --days 30
TI> derivatives KAYNES
TI> baseline KAYNES --horizon positional
TI> research KAYNES --depth deep
TI> orchestrate KAYNES --horizon 2w:6w
TI> opportunity KAYNES --horizon 2w:6w
TI> replay last
```

Native commands should not invoke an LLM merely to interpret their syntax.

---

## 5. NLP mode

```text
TI> set mode=nlp
TI[nlp]> Analyze KAYNES for a 2–6 week positional opportunity.
TI[nlp]> Why WAIT?
TI[nlp]> What is the biggest blocker?
TI[nlp]> What would need to change for OPPORTUNITY?
```

The Shell routes natural language to an Interaction Agent.

The Agent may use GPT-6 Astra, Claude, or another configured model, but it invokes only allowed typed TI capabilities.

---

## 6. Mixed mode

Recommended modes:

```text
command
nlp
mixed
```

In `mixed` mode:

- recognized native commands execute directly;
- other text is routed to the Agent.

This is likely the best developer experience.

---

## 7. Mode, profile, and model are separate

These concepts should never be conflated.

### Interaction mode

```text
mode = command | nlp | mixed
```

Controls how the user communicates.

### Intelligence profile

```text
profile = deterministic | balanced | deep
```

Controls how much intelligence/cost is authorized.

### Model policy

```text
model = default | gpt6-astra | claude-... | ...
```

Controls the reasoning engine used by an Agent.

Example:

```text
TI> set mode=mixed
TI> set profile=deep
TI> set model=gpt6-astra
```

---

## 8. Explicit Agent command

Even outside NLP mode:

```text
TI> ask "Why is KAYNES classified as WAIT?"
```

For controlled engineering experiments:

```text
TI> ask --model gpt6-astra         --profile deep         --query "Compare KAYNES and DIXON for positional trading."
```

Interactive NLP should not require `--query`.

---

## 9. Stateful context

The Shell should behave as a real REPL.

```text
TI> use KAYNES
Subject = KAYNES

TI> set style=positional
TI> set horizon=2w:6w

TI> opportunity
```

Possible session state:

- session ID;
- subject;
- instrument;
- objective;
- style;
- horizon;
- mode;
- intelligence profile;
- model policy;
- last run;
- last result;
- last capture.

`show context` should make all of this explicit.

Session context is not canonical market truth.

---

## 10. Suggested Shell controls

```text
help
capabilities
agents
use
set
show
history
replay
trace
explain
refresh
clear
exit
```

Example:

```text
TI> help opportunity
TI> capabilities
TI> show config
TI> show context
```

---

## 11. Suggested capability commands

Initial families:

```text
evidence
technical
fundamental
news
relative
sector
macro
derivatives
baseline
research
orchestrate
opportunity
replay
```

Later:

```text
forecast
compare
position
expression
monitor
```

Names should mirror stable TI capabilities where practical.

---

## 12. Inspection commands

TI_SHELL should be a live engineering microscope.

```text
TI> show last
TI> show last --json
TI> show last --reasons
TI> show last --evidence
TI> show last --contradictions
TI> show last --audit
TI> show last --fingerprint
```

---

## 13. `explain`

Where Core output includes deterministic rule traces:

```text
TI> explain last
```

Example:

```text
State = WAIT

Matched:
- TIMING_RESTRICTION = TRUE
- QUALIFIED_SUPPORT = TRUE

Primary:
TIMING_RESTRICTION

Evidence:
- Technical extension = EXTENDED
- Remaining room = LIMITED
- Opportunity Risk = HIGH

A2 baseline:
NO_TRADE

Canonical classification used no LLM.
```

This should use structured Core trace data, not invent a new Shell-side rationale.

---

## 14. `trace`

```text
TI> trace last
```

Conceptually:

```text
request
  ↓
A2 evidence
  ↓
A3.8 orchestration
  ├─ Technical
  ├─ Fundamental
  ├─ News
  ├─ Relative
  ├─ Sector
  ├─ Derivatives
  └─ Quality/Risk
  ↓
A3.9 synthesis
  ↓
WAIT
```

Variants:

```text
TI> trace last --cost
TI> trace last --evidence
TI> trace last --timing
```

---

## 15. Follow-up questions

A major Shell benefit is context-aware follow-up.

```text
TI> opportunity KAYNES --horizon 2w:6w
State: WAIT

TI> why wait?
```

The Agent should first inspect the existing result.

It should not automatically rerun analysis.

```text
TI> what would need to change for OPPORTUNITY?
```

The Agent can inspect A3.9 predicates/rules.

```text
TI> has that changed since yesterday?
```

This requires new/temporal evidence and may justify another Core request.

The Agent must distinguish:

- answer from current captured context;
- new analysis required.

---

## 16. Refresh

Freshness should be explicit.

```text
TI> opportunity --refresh
TI> refresh news
TI> refresh market
```

Natural language:

```text
TI> Recheck this using current data.
```

No silent refresh should destroy reproducibility assumptions.

---

## 17. Dry-run

For expensive Agent requests:

```text
TI> ask --dry-run     "Analyze KAYNES deeply and compare it with DIXON."
```

The Shell/Agent should be able to expose:

- intended capabilities;
- reuse vs refresh;
- research depth;
- expected provider/model operations;
- budget implications.

This is especially useful for engineering and premium-cost control.

---

## 18. Show-plan

```text
TI> ask --show-plan     "Analyze KAYNES for a 2–6 week positional opportunity."
```

This should expose a concise operation plan, not hidden chain-of-thought.

Example:

```text
Plan:
1. Reuse latest eligible A2 baseline
2. Run opportunity orchestration
3. Assemble structured opportunity intelligence
4. Inspect timing/risk restrictions
5. Render response
```

---

## 19. Multi-symbol use

Native:

```text
TI> opportunity KAYNES DIXON RELIANCE --horizon 2w:6w
```

NLP:

```text
TI> Which of these has the cleanest setup?
```

The Shell must not invent ranking/comparison behavior before Core exposes it.

---

## 20. Capability discovery

```text
TI> capabilities
```

Possible groups:

```text
Evidence
Analysis
Research
Opportunity
Engineering
Forecasting
Position
Expression
Monitoring
```

This helps the Shell become self-discoverable.

---

## 21. Agent discovery

Developer/admin mode may support:

```text
TI> agents
```

showing available Agents/specialists and status without exposing private implementation unnecessarily.

---

## 22. Provenance of invocation

Every run should record origin:

```text
origin = SHELL_COMMAND
```

or:

```text
origin = SHELL_AGENT
agent = InteractionAgent
model_policy = GPT-6 Astra
```

This is crucial for audit and model evaluation.

---

## 23. Do not shell out internally

The architecture should not be:

```text
Agent -> generate command string -> subprocess -> parse stdout
```

Instead:

```text
Agent/Shell -> typed capability -> structured result
```

Existing scripts continue to serve smoke tests, CI, diagnostics, and reproducibility.

---

## 24. Typed composition

Do not initially implement Unix text pipes as the canonical composition mechanism.

Prefer typed capability composition.

A future DSL may look like:

```text
TI> universe fno
    |> screen momentum
    |> top 20
    |> opportunity --horizon 2w:6w
```

but each step must exchange typed objects rather than parsed display text.

This should be deferred until needed.

---

## 25. Public vs developer Shell

TI_SHELL may have modes such as:

```text
user
developer
admin
```

Developer commands might expose:

- planner trace;
- evidence graph;
- projection details;
- budget ledger;
- fingerprint verification.

These need not become public APIs.

---

## 26. Error semantics

Prefer typed errors:

```text
UNKNOWN_COMMAND
INVALID_ARGUMENT
CAPABILITY_NOT_AVAILABLE
INSUFFICIENT_EVIDENCE
PERMISSION_DENIED
BUDGET_EXCEEDED
MODEL_NOT_ALLOWED
STALE_CONTEXT
CAPTURE_INTEGRITY_ERROR
```

NLP should never disguise a real system error as plausible prose.

---

## 27. Authority

Natural language is never an execution authority bypass.

```text
User
  ↓
Shell / Agent
  ↓
typed capability request
  ↓
authorization / entitlement / policy
  ↓
TI capability
```

Broker execution remains under TradeMonitor/broker-authorized flows.

---

## 28. Testing role

TI_SHELL should become a principal manual acceptance/debugging tool.

For example:

```text
TI> opportunity KAYNES --profile deterministic
TI> explain last
TI> replay last
TI> show last --json
```

It complements automated tests; it does not replace them.

---

## 29. Model-evaluation role

TI_SHELL can become a model laboratory:

```text
TI> ask --model gpt6-astra --same-context "Assess KAYNES."
TI> ask --model claude-opus --same-context "Assess KAYNES."
TI> compare-responses last-2
```

Future evaluation can measure:

- unsupported claims;
- agreement;
- usefulness;
- latency;
- cost;
- consistency.

This will help choose models for product tiers.

---

## 30. Recommended v0.1

After A3 closure, a useful first implementation can remain deliberately small.

Commands:

```text
help
exit
set
show
use
capabilities
evidence
baseline
technical
research
orchestrate
opportunity
replay
ask
explain
trace
```

Settings:

```text
mode = command | nlp | mixed
profile = deterministic | balanced | deep
model = default | configured model
```

This alone would substantially improve A4–A7 engineering productivity.

---

## 31. What TI_SHELL must never become

It must not become:

- a second intelligence engine;
- a home for technical-analysis rules;
- a hidden ranking engine;
- a Web-specific backend;
- a broker shortcut;
- an LLM prompt collection that bypasses Core;
- a monolith containing every service.

It is an interaction, mediation, inspection, composition, and Agent-access layer.

---

## 32. TI_SHELL invariants

1. Native commands call typed TI capabilities.
2. NLP input is interpreted by Agents.
3. Models are replaceable.
4. Mode and intelligence profile are separate.
5. Session context is not market truth.
6. Shell does not own canonical intelligence policy.
7. Shell cannot bypass authorization.
8. Existing structured results should be reused before rerunning work.
9. Refresh is explicit.
10. Developer diagnostics may exceed public API surface.
11. All Shell actions are auditable.
12. Canonical outputs remain machine-readable.
13. Agent explanations do not become hidden canonical truth.
14. Existing scripts/tests remain valid without TI_SHELL.
15. TI_SHELL is a primary engineering tool, not the only interface to TI.

---

## 33. Final thesis

> **TI_SHELL should be the stateful interactive interpreter for TradingIntelligence: precise native commands when the user knows what to invoke, Agent/NLP interaction when the user expresses a goal, and engineering inspection/replay facilities for understanding exactly what TI did.**

It should make TI easier to build, test, explore, compare, debug, and eventually use—without moving any canonical intelligence policy out of TI_CORE.
