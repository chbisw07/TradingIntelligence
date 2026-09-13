# TIAF A6 — Reconciliation Record

## Current successor review

The original architecture-pass evidence below is a historical snapshot. The
[independent acceptance](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md)
now records **READY_TO_IMPLEMENT_A6_1**: A6 architecture accepted, thesis accepted
as non-normative companion, A6.1 active/next, runtime NOT_IMPLEMENTED. The
[thesis/architecture reconciliation](TIAF_A6_THESIS_ARCHITECTURE_RECONCILIATION.md)
accounts for all fourteen findings. A5 remains FROZEN; R1–R5 ACCEPTED / DONE.
The intermediate READY_FOR_A6_ARCHITECTURE_ACCEPTANCE and earlier
READY_FOR_A6_THESIS decisions below are dated history. Current next:
**TIAF A6.1 — CONTRACTS, ADMISSION & POLICY FOUNDATION**.

## Review scope and baseline

Documentation-only review, 2026-09-13 (Asia/Kolkata). Entry working tree was
clean at `928a12b` (`feat(pluggability): implement and accept R5 cold composition`).
A5 remains frozen and R1–R5 accepted/done. No A6 runtime was found; existing
`OptionExpression` is a data-only legacy contract, not a selector. No provider,
model or broker calls were performed. No runtime policy was changed.

The requested brief was the user's local
`Codex_TIAF_A6_Trade_Expression_Intelligence_Reconciliation_Architecture_Pass.md`.
This record distinguishes its new A6 design request from already accepted
repository decisions. The [architecture matrix](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md#2-reconciliation-matrix)
is the topic-by-topic resolution, and the [roadmap](TIAF_A6_DETAILED_ROADMAP.md)
is gated behind thesis reconciliation and architecture acceptance.

## Inspected-source inventory

Inspection used targeted relevant sections and repository-wide searches, not a
claim that every historical document was reread cover to cover. Source groups
below are the matrix's reference IDs. Current status/navigation overrides older
“next” statements, but historical closure evidence is not rewritten.

| ID | Inspected documents / code | Relevant authority or finding |
| --- | --- | --- |
| S01 | [README](../README.md), [architecture index](ARCHITECTURE.md), [milestones](MILESTONES.md), [implementation queue](IMPLEMENTATION_ROADMAP.md), [targets](TIAF_IMPLEMENTATION_TARGETS.md), [capability map](TIAF_CAPABILITY_MAP.md), [deferrals](TIAF_DEFERRAL_REGISTER.md) | Current state/forward navigation; overly broad option strategy library; DEF-025 A6-closure wording; distinguish canonical deferral rows from historical audits. |
| S02 | [Trading Ecosystem Architecture](TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md), especially object lifecycle, A6 and TM policy sections; [TIAF Thesis](TIAF_THESIS.md) | Source proposal separate from TI analytical expression; no mandatory TradeIntent; TI_REQUIRED/TI_OPTIONAL; TM and broker ownership; initial single-leg boundary. |
| S03 | [Development roadmap](TRADINGINTELLIGENCE_ROADMAP.md), A6/A7 sections; [System Architecture](TIAF_SYSTEM_ARCHITECTURE.md), higher-order comparison | Deterministic admissible candidates first; optional later forecast-enhanced comparison cannot invent candidates or cross TM authority. |
| S04 | [A1.3 derivatives](TIAF_A1_3_DHAN_DERIVATIVES.md), [A1.5 resolver](TIAF_A1_5_INSTRUMENT_RESOLVER.md), [A2.7 features](TIAF_A2_7_DERIVATIVES_OPTION_CHAIN_FEATURES.md) | Listed strike geometry; single-expiry A2 evidence; raw IV semantics; date-only expiry; quote absence versus zero factual OI/volume; acquisition-time limitations. |
| S05 | [A3.7](TIAF_A3_7_DERIVATIVES_OPPORTUNITY_RISK.md), [A3.8](TIAF_A3_8_PLANNER_SPECIALIST_ORCHESTRATION.md), [A3.9](TIAF_A3_9_STRUCTURED_OPPORTUNITY_INTELLIGENCE_MVP.md) | Specialist derivatives/risk/opportunity context and bounded orchestration; no CE/PE selection; preserved A2 benchmark and structured dissent. |
| S06 | [A4 architecture](TIAF_A4_CHALLENGE_ARBITRATION_HIGHER_INTELLIGENCE_ARCHITECTURE.md), [A4.1](TIAF_A4_1_DETERMINISTIC_CHALLENGE_ARBITRATION.md), [A4.2](TIAF_A4_2_GOVERNED_EVIDENCE_NEED_PLANNER_BRIDGE.md), [A4 closure](TIAF_A4_MAJOR_MILESTONE_CLOSURE_REVIEW.md) | SUPPORTIVE is not trade permission; separate disposition/execution status; enrichment does not select expressions. |
| S07 | [A5 architecture](TIAF_A5_POSITION_INTELLIGENCE_ARCHITECTURE.md), [A5.1](TIAF_A5_1_DETERMINISTIC_SINGLE_POSITION_BASELINE.md), [A5.2](TIAF_A5_2_GOVERNED_POSITION_FACADE_SHELL.md), [A5 closure](TIAF_A5_MAJOR_MILESTONE_CLOSURE_REVIEW.md) | Single-position advice, strict captured admission and refresh intent only; no A6 invocation, roll or execution authority. |
| S08 | [Monitoring Architecture](TIAF_MONITORING_ARCHITECTURE.md), [Deployment Architecture](TIAF_DEPLOYMENT_ARCHITECTURE.md) | Horizon differs from cadence; future monitoring and shared evidence ownership; local captured facade does not imply live runtime or execution. |
| S09 | [Pluggability Architecture](TIAF_PLUGGABILITY_ARCHITECTURE.md), [A1–A5 audit](TIAF_PLUGGABILITY_A1_A5_COMPLIANCE_AUDIT.md), R1–R5 records below | Required scope, honest metadata, exact pins, import isolation and one COLD owner apply to A6 without a new framework. |
| S10 | [Shell architecture](TIAF_TI_SHELL_ARCHITECTURE.md), [v0.1 implementation](TIAF_TI_SHELL_V0_1_IMPLEMENTATION.md), [interaction architecture note](TBD_TI_CLI_WEB_UI_INTERACTION_ARCHITECTURE.md), [Shell thesis note](TBD_TI_SHELL_THESIS.md) | Shared typed facade/REPL/one-shot; logical artifacts; future NLP/Web above contracts; eight actual operations, not a current expression command. |
| S11 | [A2.10 replay](TIAF_A2_10_REPLAY_VALIDATION_EVALUATION.md), [A3.10 hardening](TIAF_A3_10_AGENT_REPLAY_BASELINE_COMPARISON_COST_FAILURE_HARDENING.md), R3 records | Synthetic golden versus captured replay distinction; integrity, exact fingerprints, offline verification and explicit unavailable versions. |
| S12 | [A0 option contract](../src/tiaf/contracts/options.py), [common/Horizon](../src/tiaf/contracts/common.py), [derivative contracts](../src/tiaf/data/derivatives.py), [A4 enums](../src/tiaf/a4/enums.py), [A4 thesis construction](../src/tiaf/a4/thesis.py), [source semantics](../src/tiaf/source_semantics/contracts.py), relevant source/test searches | Actual fields and direction mapping, source timing limitations, frozen tuple conventions, existing no-expression boundaries. |

R-series documents inspected for S09 (implementation and acceptance are distinct):

| Slice | Implementation / accepted evidence | A6 reconciliation |
| --- | --- | --- |
| R1 | [Required Scope / Explicit Absence](TIAF_PLUGGABILITY_R1_REQUIRED_SCOPE_EXPLICIT_ABSENCE.md); [acceptance](TIAF_PLUGGABILITY_R1_ACCEPTANCE_AND_A5_FREEZE_READINESS.md) | Never reduce required gates to match available inputs. |
| R2 | [Discovery Metadata](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA.md); [acceptance](TIAF_PLUGGABILITY_R2_DISCOVERY_METADATA_ACCEPTANCE.md) | Planned capability cannot claim implementation/readiness/authority. |
| R3 | [Composition / Pinned Verifier](TIAF_PLUGGABILITY_R3_COMPOSITION_ENVELOPE_PINNED_VERIFIER.md); [acceptance](TIAF_PLUGGABILITY_R3_COMPOSITION_ENVELOPE_PINNED_VERIFIER_ACCEPTANCE.md) | Preserve A3.8-shaped envelope and exact pins; new A6 run schema is additive. |
| R4 | [Import Isolation](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION.md); [acceptance](TIAF_PLUGGABILITY_R4_OPTIONAL_ADAPTER_IMPORT_ISOLATION_ACCEPTANCE.md) | No provider/MCP/model SDK import in A6 domain. |
| R5 | [COLD Ownership](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION.md); [acceptance](TIAF_PLUGGABILITY_R5_COLD_OWNERSHIP_CONFIGURATION_ACCEPTANCE.md) | Existing owner, versioned future config extension, frozen policy selection distinct from authority. |

Search families included A6/trade expression/TradeExpression/option expression,
strike/expiry/moneyness/CE/PE/single-leg, EXPRESSION_REFRESH_REQUIRED,
SigmaDSL/TradeIntent/ExecutionIntent/TI_REQUIRED/TI_OPTIONAL, position.assess,
capabilities.list, Shell/plain English/NLP/CLI/interaction. Code was used to
check document assumptions, not changed to match the proposed architecture.

## Material resolutions

1. **Scope:** the ecosystem already bounded initial A6 to single-leg CE/PE;
   the broad capability-map strategy library did not mean every strategy must
   ship in v1. Long-only and initial NSE equity/index coverage are newly proposed
   narrow choices. The remaining library is future, separately accepted scope.
2. **SigmaDSL:** DEF-025's historical “A6 closure” revisit label could imply a
   prerequisite. The canonical row now explicitly excludes SigmaDSL from A6 v1
   and assigns any programmable product review separately. Historical A2/A3
   audit rows remain dated evidence, with a current clarification. No deferral
   is spuriously marked implemented or deleted.
3. **Meaning of executable:** “A6 owns executable expression” in the architecture
   index was misleading relative to the later ecosystem authority model. A6
   owns analytical suitability only; TM alone creates execution intent. “Option
   expression” and “Trade Expression Intelligence” describe the same bounded
   milestone, not permission for universal trade synthesis.
4. **Actual inputs:** flexible Horizon, A4 string direction, date-only expiry,
   acquisition-only chain time and optional legacy option scores are not hidden
   ready-made A6 contracts. The draft specifies exact admission mapping and
   additive evidence qualification, and exposes missing facts rather than
   silently deriving them.
5. **Pluggability:** R3's current specialist envelope and R5's current config do
   not already support A6 evaluator selection. A6-specific run pins and a later
   versioned config extension are required within existing ownership. There is
   no new A3 specialist, composition root, generic plugin framework or HOT scope.
6. **Sequence:** old “architecture then implementation” shortcuts now lead through
   a visual thesis, thesis/architecture reconciliation and acceptance before
   A6.1. Historical R5 acceptance's then-next recommendation is not rewritten.

## Deferrals and non-closure

DEF-006 stays PLANNED: deterministic initial A6 is not implemented by this pass.
Broader templates and later forecast-enhanced comparison remain separate. DEF-025
stays DEFERRED, with the SigmaDSL dependency removed. No canonical IDs/statuses
are added, deleted or renumbered.

DEF-007 (calendar-aware recency), DEF-014 (provider event-time gap), DEF-039
(richer/delta strike selection), DEF-040–DEF-046 (historical/temporal derivatives,
term structure, surfaces, probabilities/expected move and positioning models)
are not closed by reading multiple captured chains. DEF-054 rich interaction,
DEF-057 HOT swapping and DEF-058 peer publication remain outside this draft's
bounded implementation proposal. A7, multi-leg/short-option optimization,
monitoring runtime, TM/broker integration and full NLP/Web remain future scope.

## Review outcome and validation record

**READY_FOR_A6_THESIS**, not implementation readiness. The strict timing-source
feasibility and conservative provisional policy/coverage choices are surfaced
for thesis review rather than disguised as existing live capability. The
architecture's Thesis Readiness section and roadmap list the required visuals,
examples, questions and four gated future implementation slices.

This pass changes documentation only: three new A6 documents plus ten existing
status, scope and navigation documents. Exact files:

- Created: `docs/TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md`,
  `docs/TIAF_A6_DETAILED_ROADMAP.md`, `docs/TIAF_A6_RECONCILIATION_RECORD.md`.
- Updated: `README.md`, `docs/ARCHITECTURE.md`,
  `docs/IMPLEMENTATION_ROADMAP.md`, `docs/MILESTONES.md`,
  `docs/TRADINGINTELLIGENCE_ROADMAP.md`, `docs/TIAF_IMPLEMENTATION_TARGETS.md`,
  `docs/TIAF_CAPABILITY_MAP.md`, `docs/TIAF_DEFERRAL_REGISTER.md`,
  `docs/TIAF_SYSTEM_ARCHITECTURE.md`,
  `docs/TIAF_TRADING_ECOSYSTEM_ARCHITECTURE.md`.

Validation on this documentation change set:

- `git diff --check`: PASS.
- No dedicated documentation-link or deferral-integrity checker was found in
  the existing scripts/tests or project configuration. A read-only standard-
  library check using `.venv/bin/python` validated all **510 local Markdown
  links/anchors across the 13 changed/new documents**, balanced fenced blocks,
  and documentation-only change scope: PASS. This is a static link/fence check,
  not a rendered Mermaid visual acceptance test.
- Canonical deferrals: **58 unique sequential IDs**, identical IDs and statuses
  to HEAD. Counts remain 45 DEFERRED, 4 PLANNED, 4 IMPLEMENTED, 3 REJECTED and
  2 SUPERSEDED. Categories valid; no ID added/deleted/renumbered: PASS.
- Runtime tests intentionally not rerun for documentation-only changes. No
  runtime, contract, scoring, provider, replay implementation or dependency
  manifest changed. No live provider/model/broker call, commit, tag or push.

The shell's unqualified `python` command was unavailable; the repository virtual
environment interpreter ran the static checks successfully. This is not a
runtime acceptance blocker or a claim of newly executed runtime quality gates.
