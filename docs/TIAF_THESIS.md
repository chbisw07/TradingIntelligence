# TIAF Architecture Thesis

## North star and authority

TradingIntelligence should act in the user's economic interest: **maximize
risk-adjusted expected economic utility, not raw profit at any cost**. This is
an engineering objective, not demonstrated profitability or a calibrated utility
model. Deterministic evidence, specialist intelligence and higher-order reasoning
should eventually combine with evaluated probabilistic forecasting and learning,
while preserving risk control, uncertainty, explainability, provenance, replay
and cost discipline.

This is the current philosophy after accepted A4, A5 and pluggability R1.
[System architecture](TIAF_SYSTEM_ARCHITECTURE.md) owns the capability boundary;
the [architecture index](ARCHITECTURE.md) links normative designs, implemented
slices and historical evidence. A1–A4 are frozen; A5.1/A5.2 are accepted and
documentationally ready for the final freeze check, but `tiaf-a5-baseline` is
not yet created. Future design is not an implemented product.

## Intelligence hierarchy

| Layer | Meaning | Current boundary |
|---|---|---|
| L0 | Raw sources | Provider-native observations and supplied operational snapshots; source labels alone are not authority. |
| L1 | Admitted evidence | Typed normalization, provenance, availability/PIT and field-scoped authority. |
| L2 | Derived features | Deterministic calculations over factual inputs, not model-generated prices or indicators. |
| L3 | A2 deterministic state | Visible replayable baseline/benchmark, including NO_TRADE. |
| L4 | A3 specialists | Bounded attributable interpretation, explicit gaps and disagreement; accepted path is deterministic/no-LLM. |
| L5 | A3.9 structured opportunity intelligence | One underlying product, not an unexplained rank or execution instruction. |
| L6 | A4 challenge/arbitration | Deterministic challenged theses, dissent, non-action dispositions and governed one-round evidence enrichment. |
| L7 | A5 position / A6 trade-expression intelligence | A5 single-position advice is accepted; A6 expression construction/selection remains future. |
| A7 overlay | Forecasting, evaluation and future learning | Future calibrated evidence and empirical controls across layers; not a forced extra rung or prerequisite to the initial deterministic A6 slice. |

The layers own different questions, not successively more authoritative opinions.
An interpreter cannot recalculate its evidence, an Arbitrator cannot invent a
contract, and a forecast cannot grant operational authority.

## Baseline before enrichment

A2 remains a deterministic control against which future Agents and policies are
evaluated, not a disposable precursor. Preserve component evidence, assumptions,
NO_TRADE, original direction/class/score and fingerprints alongside enrichment.
Do not optimize weights or thresholds to make selected live examples attractive.
The accepted A4.1 policy preserves A2 NO_TRADE as a hard gate.

Optional context may improve an answer but is not permission to fabricate missing
facts. A sparse watchlist plus horizon is a long-term input aspiration, not a
claim that all current capabilities accept it. Current operations retain their
typed evidence/artifact requirements. Removing optional enrichment preserves the
baseline; removing a required contributor preserves its unresolved obligation,
not a deceptively complete answer.

## Evidence before inference; bounded open-world reasoning

Distinguish FACT, INFERENCE, ASSUMPTION and HYPOTHESIS. Model prior knowledge may
motivate a hypothesis, identify missing information or request governed research;
it cannot become canonical evidence by being eloquent, familiar or repeated.
New research must pass sourcing, normalization, provenance, field-scoped
authority, entitlements and point-in-time admission. Different horizons or
accounting bases are not automatically contradictory propositions; copied sources
are not independent confirmations.

The accepted [A4.2 bridge](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md)
admits a material semantic need through existing Planner/gateway controls and
allows one bounded no-model enrichment/successor cycle. It is not a browser
agent, unbounded debate or public live capability. New admissible evidence gets
a later cutoff and successor identity; old evidence, dissent and results remain
unchanged. No new information preserves the conservative parent result. Changed
market-state inputs require upstream refresh, not an A4 patch to A2/A3.

Optional model-backed challenge still requires separate privacy/egress, adapter,
structured-output, budget/pricing, no-LLM-control and evaluation acceptance.
Deterministic and model-backed reasoning must never be conflated.

## Pluggability without hidden authority

The canonical guarantee hierarchy is **HOT ⇒ COLD ⇒ STRUCTURAL**. STRUCTURAL
is the base contract boundary; COLD adds governed replacement at startup/restart;
HOT is strongest and requires safe in-flight transition, state ownership and
rollback. Reverse implications are not assumed. No HOT runtime is accepted.

Required/optional scope is independent of replacement lifecycle, installation,
registration, authorization and successful execution. Capability presence never
grants authority. R1 pins declared required scope independently of registry
membership, keeps required absence in completeness, and makes optional absence
visible. Failure is not a negative market opinion, and absence is not evidence
that a company or thesis is bad. The [pluggability design](TIAF_PLUGGABILITY_ARCHITECTURE.md)
governs future changes; R1 acceptance does not certify all R2–R5 mechanisms.

## Position intelligence and valid non-action

Opportunity intelligence asks what merits further consideration; position
intelligence asks what current admitted evidence means for an existing exposure.
The original entry rationale is optional, but actionable A5 assessment requires
a current accepted A4 thesis/result. Missing A4 yields insufficient evidence;
stale/unknown operational truth cannot silently become MAINTAIN.

[A5](TIAF_A5_DETAILED_ROADMAP.md) separates operational state, analytical risk
posture, thesis health and recommendation. Protection/trailing is advisory, not
an order or broker lifecycle. Multi-leg interpretation is explicitly unsupported.
A6 will separately choose valid trade expressions; A7 may later inform enhanced
comparison with calibrated evidence, never fabricated target-hit probabilities.

WAIT, NO_TRADE, AVOID, ABSTAIN, CONFLICTED and INSUFFICIENT_EVIDENCE are legitimate
outcomes, not errors to tune away. Their exact vocabularies remain owned by each
versioned domain contract; this philosophy does not add enum values to A5.

## Monitoring philosophy

[Monitoring is subscriber-driven, mandate-centric and capability-oriented](TIAF_MONITORING_ARCHITECTURE.md).
A watchlist is organization; a mandate is semantics. Subscriber applications own
business purpose, selected instruments, horizon intent and optional groupings.
TI owns governed admission and, in a future runtime, recurring execution,
freshness, budgets, failure isolation and replay. TM retains position truth and
action authority.

Shared evidence does not imply shared analysis state. Deduplicate compatible
evidence acquisition, not subscriber intent; each mandate retains its scope,
rights, cutoff, lifecycle and result lineage. A5's implemented WatchMandate is
advisory source intent, not a running subscription. Runtime admission, scheduling,
durability and event handling remain unimplemented. Repeating a captured-read
facade call does not create fresh live evidence.

## Replay, cost and learning discipline

Recorded replay reconstructs captured meaning without live repair or acquisition
of later capabilities. Deterministic verification uses captured inputs/policy
and compatible bindings; missing historical bindings must be explicit. Policy
comparison is a new labeled evaluation, never a rewritten historical result.
Preserve immutable child hashes, lineage and declared scope. Contract timestamps
remain aware, normalize via `ZoneInfo("Asia/Kolkata")`, and emit `+05:30` JSON;
naive datetimes are rejected.

Research depth is bounded by evidence needs, authority, latency and budgets.
Unknown monetary cost is not zero; attempt/reservation lineage survives failures
and replay does not double-bill captured work. Future learning requires observed
outcomes, PIT/leakage controls, null/baseline comparisons and controlled policy
promotion—not retrospective selection of persuasive explanations.

## TI, TM and broker boundaries; future work

Scanners are discovery/sensors. TI is intelligence/advice. TM is governor of
risk, authority, operational lifecycle and execution coordination. The broker
is final live-state/execution truth. **TI never places, modifies or cancels
broker orders.** Typed capabilities and internal/external consumers obey the
same authority boundary; neither UI nor model output bypasses admission.

Sector Rotation, Signal Qualification, calibrated Forecasting/A7, Trade
Expression/A6, monitoring runtime, TM/scanner runtime integration and remote
transport remain future work. Existing A3.6 sector-context interpretation is not
a Sector Rotation engine. Future Signal Qualification is intended after Sector
Rotation review; their exact placement relative to A7/A8 remains explicitly TBD,
not a new milestone sequence inferred from an idea note.

See the [current roadmap](IMPLEMENTATION_ROADMAP.md) and
[deferral register](TIAF_DEFERRAL_REGISTER.md). Human-readable companions are
[Fabric thesis](TIAF_Trading_Intelligence_Agent_Fabric_Thesis.docx),
[Intelligence hierarchy thesis](TI_Intelligence_Hierarchy_Thesis.docx) and
[Monitoring thesis](TI_Monitoring_Architecture_Thesis.docx). These DOCX files are
non-normative companions; accepted Markdown architecture/contracts govern.
