# TIAF A6 — Trade Expression Intelligence Architecture Acceptance

## Decision

2026-09-13, Asia/Kolkata: **READY_TO_IMPLEMENT_A6_1**.

```text
A5 FROZEN
R1–R5 ACCEPTED / DONE
A6 ARCHITECTURE ACCEPTED
A6 THESIS ACCEPTED AS NON-NORMATIVE COMPANION
A6.1 ACTIVE / NEXT
A6 RUNTIME NOT_IMPLEMENTED
```

**A6 architecture accepted. A6 thesis accepted as non-normative companion.
A6.1 is the next implementation slice.** This accepts the bounded architecture,
not its implementation, live-data usefulness, economic calibration or eventual
freeze. Do not publish `expression.assess` until A6.3 acceptance.

This was an independent documentation/static review of the actual reconciled
architecture, roadmap, records and full thesis text. It did not implement A6,
alter frozen A5, begin A7, call a provider/model/broker, or commit/tag/push.
Entry HEAD was `928a12b`; existing uncommitted A6 documentation was preserved.
The open LibreOffice lock file is user-owned and untouched.

## Acceptance verdicts

| Area | Verdict | Acceptance basis |
| --- | --- | --- |
| User problem | ACCEPT | Given admitted thesis plus captured evidence, A6 identifies a supported advisory option expression or explicit absence. `THESIS != EXPRESSION != EXECUTION` has separate owners and records. |
| Bounded v1 | ACCEPT | Long buy-to-open single-leg CE/PE on captured eligible NSE equity/index contracts; deterministic gates, bounded ranking, explanation and replay. Multi-leg, selling/shorts, futures/cash optimization, margin/sizing/orders/routing, A7, NLP/Web and SigmaDSL runtime are outside v1. |
| Upstream gate | ACCEPT | Only intact COMPLETE A4 SUPPORTIVE with supported primary thesis and resolvable POSITIVE/NEGATIVE direction enters candidate evaluation. A2/A4 prohibition, A4 wait/conflict, abstention/insufficiency and direction conflicts have explicit precedence. No repair, upgrade, rerun or silent resolution. |
| Typed request | ACCEPT | Subject, consistent direction constraint, DAY/POSITIONAL plus explicit target/Horizon bounds, cutoff, admitted refs, universe capture and request restrictions are typed. COLD policy/profile is runtime-owned, not arbitrary caller thresholds. |
| Horizon/duration | ACCEPT | Exact positive elapsed duration and explicit target are canonical. Intraday, BTST and multi-week labels are normalized/refused above core. Sourced session facts are required for DAY; interpretation is replayed. |
| Timing source | ACCEPT WITH EXPLICIT LIMITATION | Observation/event time, acquisition/availability, derived freshness age, cutoff, expiry date, expiration instant, trading cutoff and timezone are distinct. Asia/Kolkata creates no authority. Date-only/acquisition-only input yields insufficient. No source/calendar/fallback is fabricated. |
| Freshness | ACCEPT | Requirement and fact meaning are architectural; exact maximum ages are versioned COLD policy data and replay pins. Stale/unknown cannot become current. |
| Expiry | ACCEPT | Membership and qualified expiration drive residual life/cushion. Date-only is inadequate. Weekly/monthly labels have no inferred preference. Expiration fit is not exit-tradability/liquidity; TM revalidates at action time. |
| Strike/moneyness | ACCEPT | Nearest listed strike, lower tie and actual neighbors are deterministic; CE/PE ITM1/OTM1 directions are explicit. Geometric ATM anchor is separate from intrinsic moneyness and delta. |
| Candidate universe | ACCEPT | One subject, normal one-to-three declared expiries, at most 512 listed strikes each and three selected neighbors per expiry (nine evaluations). Confirmed-empty and unavailable scopes differ. No generated strikes, implicit omissions or unbounded result dump. |
| Liquidity | ACCEPT | Qualified instrument/spot/quote identity and time, finite positive non-crossed bid/ask, known units/currency, positive top quantities, spread and coverage are mandatory. Missing is UNKNOWN; zero top depth fails. OI/volume zero is factual; OI/volume/LTP/full depth/qualified Greeks are optional. |
| Spread | ACCEPT | Versioned hard maximum is eligibility; versioned tier is lexicographic ranking. Retained draft profile: >500 bps rejects, ≤100 tier 0, >100–500 tier 1. Values are policy data, not universal schema truths or calibrated profitability claims. |
| Premium/volatility | ACCEPT | Optional per-unit cap is restriction, not affordability/sizing or cheapest-first rank. IV/Greeks preserve supplied semantics/absence. No fair value, POP, expected move, target probability, utility or synthesized Greeks. |
| Event risk | ACCEPT | Only admitted materiality/relevance/time is used. Known exact in-window material event yields WAIT; possibly intersecting unresolved evidence yields insufficient. Broad unknown coverage is disclosed unless event-clear requires qualified full-window coverage. Empty results do not prove absence. |
| Dispositions | ACCEPT | EXPRESSION_AVAILABLE, NO_OPTION_TRADE, WAIT_FOR_EXPRESSION, INSUFFICIENT_EVIDENCE and UNSUPPORTED have explicit conditions/precedence. Operational failures are separate. Upstream-prohibited NO_OPTION_TRADE records `selection_not_run`, never claims candidate evaluation. |
| TF-05/full coverage | ACCEPT | Early termination stays DEFERRED. A failed candidate gate does not excuse required evidence when omission could alter the global result. Stable order does not change semantics; only output-identical caching/shared arithmetic is optimization. |
| Ranking | ACCEPT | Eligible-only key is spread tier, requested moneyness rank, cushion excess, exact spread and neutral contract key. Canonical exact values and shuffled-order invariance are required. Hard gates precede preferences; no weighted score. |
| Alternatives | ACCEPT | Exactly one preferred for AVAILABLE and up to the next two eligible alternatives; all at-most-nine evaluations persist. Normative v1 schema bound, not a configurable chain dump. |
| User preferences | ACCEPT | Nonempty duplicate-free closed moneyness restriction/order and optional per-unit cap only. Cheapest/longest is rejected or clarified above core, never translated. Restrictions cannot weaken policy or evidence gates. |
| Explainability | ACCEPT | Structured gates carry evidence, values, threshold/policy refs and reason codes. Result records decisive rank difference, rejected/unknown/not-selected distinctions, absence reason, gaps and invalidations. Prose cannot invent another conclusion. |
| Replay/provenance | ACCEPT | Request, resolved horizon, cutoff, upstream refs, native/canonical evidence, timing meanings, universe/coverage, gates, ranks, every candidate state, reasons, pins, fingerprints and invalidations are captured. No current-market/current-policy fallback. |
| R1–R5 | ACCEPT | R1 scope/absence explicit; R2 discovery descriptive; R3 additive A6 pins; R4 isolates optional adapters; R5 one trusted COLD owner. No HOT request-time composition. |
| A5 | ACCEPT | EXPRESSION_REFRESH_REQUIRED is lineage/advice. A5 does not invoke/own A6; A6 does not own position truth. Refresh never closes, rolls, sizes or trades. Frozen A5 unchanged. |
| A7 | ACCEPT | Optional future evidence. Initial A6 has no learned rank, expected-return distribution or calibrated probability. Later overlays retain deterministic A6 as control. |
| Monitoring/scanner/future systems | ACCEPT | Scanner proposals are immutable provenance; Monitoring, Sector Rotation and Signal Qualification exchange separately versioned admitted state without cycles. A6 is not a scheduler/scanner/monitor/qualifier. |
| SigmaDSL | ACCEPT | Outside TI A6 v1; no parser/compiler/runtime or compatibility layer. Historical “A6 closure” text is not a current prerequisite. |
| TM/broker authority | ACCEPT | A6 emits no account, capital, quantity, permission, exposure, order type, routing or broker action. TM checks and creates ExecutionIntent; broker owns orders/fills. |
| Capability/Shell | ACCEPT | `expression.assess` matches `baseline.assess`/`position.assess`; proposed CAPTURED_READ, typed, deterministic, replayable, governed and REPL/one-shot-identical. Repository search confirms it is unpublished/unimplemented. No provider-direct Shell path. |
| Interaction | ACCEPT | Plain English, CLI, Web, Python/API and internal callers normalize to one typed request/capability. Confirmation is adapter policy for analytical intent, not NLP domain logic or execution consent. |
| Roadmap | ACCEPT | A6.1 establishes contracts/admission/policy and timing/absence proof before A6.2 evaluation/replay. A6.3 publishes facade/Shell only when callable. A6.4 hardens/freezes separately. Testable exits; no hidden live-provider success gate. |
| Deferrals | ACCEPT | DEF-006/007/014 preserve runtime/timing gaps and TF-05; DEF-025/SigmaDSL, DEF-039–046/A7 models, DEF-054 NLP/Web/reporting, DEF-010 monitoring and DEF-056 multi-leg remain open. No ID/status closure. |
| Documentation | ACCEPT | Current navigation/A6 sources distinguish accepted architecture/thesis from NOT_IMPLEMENTED runtime and unpublished capability. Historical checkpoints remain labeled. |

## Critical timing feasibility judgment

Strict policy needs **qualified captured timing evidence**, but the evaluator does
not depend on Dhan or another live provider. This distinction permits acceptance.
Current Dhan option-chain acquisition timestamps and date-only expiries cannot
produce qualified AVAILABLE by themselves; the architecture deterministically
returns INSUFFICIENT_EVIDENCE. It never relabels receipt time, invents market time
or expiration, or weakens the gate. A6.1 can implement/test provider-neutral
qualification with synthetic captured evidence without claiming a live source.
A real source/admitted derivation remains a separately evidenced data-layer
prerequisite for live qualified selection, not a hidden A6.1 dependency.

Acceptance is invalidated if implementation makes timing optional, maps current
Dhan timestamps silently, or claims live usefulness without an accepted source.
An acquisition-qualified profile, calendar/session source or trading-cutoff gate
requires separate acceptance. Expiration fit does not guarantee tradability or
liquidity at intended exit.

## Disposition and coverage judgment

NO_OPTION_TRADE has distinguishable reasons: intact upstream prohibition means
selection not run; complete candidate evidence can prove none qualifies. This
preserves A4 without falsely reporting chain evaluation. WAIT is known temporary
blocking evidence; unknown time/coverage is insufficient. UNSUPPORTED is well-
formed outside-v1 intent. Operational failures never become market dispositions.

TF-05 is correctly deferred. Horizon FAIL plus quote UNKNOWN in one declared
expiry cannot be discarded because another expiry survives: that can change
INSUFFICIENT_EVIDENCE to AVAILABLE. Full required selected-window evidence stays
normative. Confirmed zero-expiry absence is separate positive scope proof; an
empty unavailable response cannot prove it. Gate order is deterministic for
reporting, not permission to stop collection. Future optimization must prove
semantic equivalence under a separately versioned reference policy.

## A6.1 entry contract

A6.1 may implement only contracts, admission and policy foundation. It must:

1. Add frozen, strict, timezone-aware typed contracts without changing A0/A5.
2. Normalize aware instants to Asia/Kolkata and reject naive datetimes.
3. Represent normal, confirmed-empty and unavailable/partial scope distinctly.
4. Model observation/acquisition/cutoff/expiration/trading-cutoff meanings and
   provenance without provider dependency or inferred authority.
5. Implement A2/A4 admission and direction/horizon consistency, not selection.
6. Pin policy/profile/evaluator/normalizer identities without self-hash cycles.
7. Preserve tuple/list/JSON-array round-trip and immutable semantic collections.
8. Publish no capability/Shell operation and make no provider/model/broker call.

Candidate evaluation/rank/replay execution remains A6.2. Facade/Shell remains
A6.3. Integrated closure/freeze remains A6.4. Acceptance is not a waiver to
combine slices or tune the baseline against live examples.

## Validation record

- `git diff --check`: PASS.
- Documentation link/anchor check: **574 local links/anchors across all 16
  changed/untracked Markdown files**, with balanced fenced blocks: PASS.
- Deferral integrity: **58 unique sequential IDs**, valid categories and exactly
  unchanged statuses versus HEAD: 45 DEFERRED, 4 PLANNED, 4 IMPLEMENTED,
  3 REJECTED, 2 SUPERSEDED: PASS.
- Architecture/status consistency: **10 current status/navigation documents**
  contain ARCHITECTURE ACCEPTED, A6.1, runtime NOT_IMPLEMENTED and a link to this
  acceptance; prior-gate records remain explicitly historical: PASS.
- Finding/record consistency: fourteen unique TF-01–TF-14 rows; exact acceptance
  statement and next prompt present: PASS.
- Repository search over `src`, `tests`, `scripts` and `pyproject.toml` finds no
  runtime `expression.assess`, `TradeExpressionRequest`, `ExpressionRunRecord`
  or deterministic A6 policy implementation: PASS (absence expected).
- DOCX/PDF SHA-256 values match the pre-acceptance artifacts: PASS. They were not
  regenerated or revalidated because neither binary nor its authoring source
  changed in this pass.
- Change scope: **16 documentation-only changed/untracked Markdown files**,
  including preserved earlier A6 work; no runtime/dependency file: PASS.

No dedicated repository documentation/deferral/status checker exists, so the
link, status, finding, deferral and hash checks used explicit read-only standard-
library validation. Runtime tests were not rerun because runtime did not change.

## Residual non-blocking risks

- No current live provider proves every strict timing fact. Live qualified
  selection remains unvalidated and may legitimately be unavailable.
- Policy numbers are engineering baselines, not calibrated safety/profitability
  thresholds. A6.1 pins them exactly; acceptance is not economic validation.
- Expiration-fit is narrower than exit tradability. Trading cutoff/future
  liquidity remain contextual or action-time concerns unless separately accepted.
- Confirmed-empty scope needs positive absence evidence not supplied by current
  A1 empty-UNAVAILABLE semantics.
- Event materiality, timing and full coverage require qualified upstream evidence.
- TF-05, multi-leg, A7, rich interaction and monitoring runtime remain deferred.

None blocks the conservative A6.1 foundation because absence has explicit
semantics and no live-success claim is made. Any implementation hiding these
limits falls outside this acceptance.

**Exact next prompt:** `TIAF A6.1 — CONTRACTS, ADMISSION & POLICY FOUNDATION`.
