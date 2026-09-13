# TIAF Trading Ecosystem Architecture

## 1. Authority, scope and implementation truth

**Authoritative ecosystem design, 2026-09-12 (Asia/Kolkata).** This formalizes
the accepted clarification: **scanners propose, TI advises, TI Monitoring
reevaluates, TM authorizes and coordinates, and brokers execute.** A common
cockpit may present these responsibilities without merging authority.

This document is normative for future ecosystem integration, not evidence that
the interfaces, lifecycle enums or services below are implemented. Review entry
was clean at `4780eb5`, after documentation consolidation. A1–A4 are frozen;
A5.1/A5.2 and R1 are accepted; A5 freeze/tag-readiness remains a separate gate.
TM responsibilities here are integration requirements, not a certification of a
TM repository or broker implementation inspected in this pass.

**Post-tag update (2026-09-13, Asia/Kolkata):** A5 is now FROZEN at
`tiaf-a5-baseline`. R2, R3, R4 and R5 are ACCEPTED / DONE; the R-series is
closed before A6. This changes project status only, not the ecosystem design.

**A6 design follow-up (2026-09-13):** the
[reconciliation architecture draft](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md)
preserves this ownership model and proposes long single-leg CE/PE v1, with no
SigmaDSL dependency. Status is ARCHITECTURE ACCEPTED / THESIS ACCEPTED AS
NON-NORMATIVE COMPANION / A6.1–A6.2 ACCEPTED / DONE / A6.3 ACTIVE / NEXT /
A6.4 NOT_IMPLEMENTED; `expression.assess` is
NOT_PUBLISHED. The
[fourteen-finding reconciliation](TIAF_A6_THESIS_ARCHITECTURE_RECONCILIATION.md)
is complete, and the [independent acceptance](TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE_ACCEPTANCE.md)
records READY_TO_IMPLEMENT_A6_1. The subsequent
[A6.1 acceptance](TIAF_A6_1_CONTRACTS_ADMISSION_POLICY_FOUNDATION_ACCEPTANCE.md)
closes the foundation. These navigation updates change no ecosystem ownership
and publish no capability. The subsequent
[A6.2 acceptance](TIAF_A6_2_CANDIDATE_EVALUATION_RANKING_REPLAY_ACCEPTANCE.md)
closes the internal evaluator and makes A6.3 active/next without changing those
boundaries.

[System architecture](TIAF_SYSTEM_ARCHITECTURE.md) owns TI's curated boundary;
[source semantics](TIAF_SOURCE_AUTHORITY_PROVENANCE_CONTRADICTION_ARCHITECTURE.md)
owns factual admission; [monitoring](TIAF_MONITORING_ARCHITECTURE.md) and
[deployment](TIAF_DEPLOYMENT_ARCHITECTURE.md) retain their detailed gates.
[A4](TIAF_A4_DETAILED_ROADMAP.md) and [A5](TIAF_A5_DETAILED_ROADMAP.md) preserve
their accepted schemas, policies, fingerprints and captured replay. New design
roles below do not rename existing classes, publish a schema or increment package
version `0.1.0` / A0 schema version `1.0`.

Current public TI operations are local PURE/CAPTURED_READ capabilities. Repeating
a captured request does not acquire fresh live evidence. A4.2's internal bounded
acquisition is not a public pre-trade API. Scanner runtime, live TM integration,
Monitoring Runtime, A6, A7, Sector Rotation, Signal Qualification, remote APIs,
Sheets connectors and Web Cockpit remain unimplemented by this design. No broker
order operation may be introduced into TI.

## 2. Responsibilities, planes and clients

| Owner | Normative responsibility | Must not own |
|---|---|---|
| Scanner/source app | Universe/group selection, discovery rules, candidate proposals and discovery refresh. | Broker execution or TI endorsement by assertion. |
| TI intelligence | Admitted evidence, deterministic baseline, specialist interpretation, challenge/arbitration, position advice and future expression/forecast intelligence. | Account action authority or broker order commands. |
| TI Monitoring | Governed recurring/event-driven capability invocation, mandate admission, freshness, budgets, run lineage and failure isolation. | Operational position truth or execution. |
| TM | Risk/authority/capital/quantity policy, candidate intake, operational position lifecycle, adoption, broker reconciliation and execution coordination. | A second thesis/scoring engine or rewriting TI findings. |
| Broker | Authoritative acknowledgements, executions/fills and observed live order/position state. | TI analytical conclusions. |
| Interaction clients | Scoped requests and faithful projections, operator confirmation and navigation. | Hidden grants, canonical broker state or independent execution bypasses. |

Five logical planes are retained: discovery; intelligence; governance/execution;
intelligence orchestration/monitoring **inside TI**; and interaction. TM operational
monitoring belongs to governance/execution, not the TI orchestration plane.
Planes do not prescribe separate processes, microservices or one shared database.

```text
INTERACTION: Sheets / TI_SHELL / future cockpit / external apps
       | typed scoped requests                  | TM command requests
       v                                        v
DISCOVERY                                    GOVERNANCE / OPERATIONS
subscriber groups -> scanners -> Candidates -------> TM
                         |                          | authorized commands
                         | evaluation requests      v
                         v                        BROKERS
TI INTELLIGENCE                                 orders / fills / positions
 admission -> A2 -> A3 -> A3.9 -> A4                 | truth
                   A5 position advice               +----------> TM
                   A6 expression [future]            |
                   A7 overlay [future]              | position snapshot/intent
                         ^                          v
TI ORCHESTRATION / MONITORING [future recurring runtime]
subscriber intent -> admitted mandates -> bounded capability runs
                         |
                         +---- results/advice -> subscribers / TM

Cross-cutting: identity, evidence/provenance, authorization, configuration,
              pluggability, budgets, audit and captured replay.
```

TI may read authorized market data through factual adapters; that is distinct
from broker submit/modify/cancel. Shared evidence contracts do not imply shared
mutable analysis or unrestricted cross-account access.

Scanner apps and manual tools produce candidates. TM, scanners, TI_WEB,
TI_SHELL, external Python/portfolio apps and future sector workflows can consume
TI capabilities; authorized applications may also request monitoring. Sheets is
a transport/client for an identified application and acting principal, not a
trusted identity by itself. Internal TI-native apps obey the same admission rules.

## 3. Scanner model and normalized candidate contract

**Scanner = universe/watchlists + discovery logic + optional TI enrichment.**
Independent scanners remain valid without TI. The default advanced pattern is
cheap discovery followed by selective bounded TI evaluation; recurring evaluation
uses admitted TI mandates. A TI-native scanner is a consumer application, not
extra Core authority. TM consumes one candidate-source interface irrespective of
TradingView, Chartink, Python, manual or future ML origin.

All normalized candidate outputs are non-executable. The following field model is
the normative initial contract design; executable Python/JSON schema publication
is deferred to the candidate-source implementation gate. Fields must not be
inferred from labels or received credentials.

| Field / group | Required semantics |
|---|---|
| `schema_version` | Exact supported candidate schema version on future publication; unknown versions fail admission. |
| `candidate_id`, `revision`, `predecessor_ref` | Source-namespaced stable ID, positive integer revision; predecessor required after revision 1. |
| `source_id`, `scanner_id`, `originating_event_id` | Trusted source binding and stable producer event identity. Manual sources use an explicit manual-adapter/rule identity, not invented market evidence. |
| `correlation_id` | Cross-system trace context validated/mapped by the receiver; not authority or object identity. |
| `instrument` | Canonical provider-neutral instrument key with venue/type/expiry identity where applicable; ambiguous identity is quarantined, not guessed. |
| `purpose`, `horizon` | Explicit purpose and canonical duration/target interval with mapping version when an app label is supplied. Trading-session meanings require a calendar. |
| `group_ref` | Optional subscriber-namespaced watchlist/item reference and relevant membership revision; not a TI-owned watchlist or permission grant. |
| `signal_at`, `received_at`, `valid_until` | Signal time from source; receipt time assigned by receiving adapter; finite source/profile-derived expiry with derivation policy retained. |
| `strategy_id`, `strategy_version` | Exact discovery rule/config identity, including an explicit manual-entry rule when applicable. |
| `evidence_refs`, `provenance_refs` | Required collections, allowed empty only with explicit absence. Preserve source assertions and raw-content digest/ref subject to rights; they are not yet TI-admitted facts. |
| `direction` | Optional BULLISH/BEARISH/NEUTRAL analytical suggestion; absent means unspecified, not neutral. Original BUY/SELL labels remain source annotations, never orders. |
| `raw_score` | Optional finite value plus declared scale/unit/range, basis and direction-of-better where known; unknown semantics explicitly marked. Zero is valid. |
| `source_confidence` | Optional source-reported value with semantics/basis, or explicit UNKNOWN basis; never silently interpreted as calibrated probability. |
| `proposed_expression` | Optional nested non-executable source proposal; identity, shape, proposed side and supplied constraints/levels are attributable source content. Unsupported shapes remain proposals, not admissible trades. |

No raw score becomes probability by normalization; incompatible source scores are
not averaged or ranked as if comparable. Receipt/authentication proves origin,
not factual correctness. Canonical TI evidence requires separate source, rights,
normalization, authority and PIT admission. A proposed expression is neither TI
endorsement nor TM authorization.

Candidate semantic collections are immutable tuples with list/JSON-array input
and ordinary JSON-array output; metadata remains extensible under the existing
contract convention. All datetimes reject naive input, normalize through
`zoneinfo.ZoneInfo("Asia/Kolkata")`, and emit ISO-8601 `+05:30`. No guessed signal
time: missing time can remain a raw intake failure/draft, not an active normalized
candidate. `valid_until` must exceed `signal_at`; a late receipt is recorded as
expired rather than granted a fresh lifetime. Future-dated/incoherent signals are
quarantined for explicit clock-policy review, never silently backdated.

### Identity, revisions, deduplication and authentication

Only an authenticated source binding may publish in its namespace. A signed/
authenticated ingress or trusted local caller binding supplies source authority;
payload `scanner_id` alone cannot impersonate a source. Transport-specific auth
technology is DEFERRED_WITH_BOUNDARY: no external admission until credential
verification, replay resistance, revocation and payload bounds are accepted.

Canonical semantic digest covers source payload, scope, validity, rule identity
and nested expression, excluding receiver-assigned receipt/trace metadata.
Receipts retain their own immutable identity and captured checksum. Same source +
candidate ID + revision + digest is an idempotent duplicate; differing digest is
a conflict. A correction must create a successor revision with expected
predecessor. Event identity maps repeated deliveries to that same record; when
one source event emits multiple candidates, each has a stable distinct candidate
ID. Out-of-order predecessors cannot silently replace the current head.

Do not dedupe independent sources, horizons or subscriber purposes into one
candidate. Optional cluster links may describe related proposals without merging
identity, source independence or authority. Withdrawal/expiry is a retained
lifecycle event, not deletion. New versions invalidate cached approval linkage;
they do not silently cancel an already submitted broker order.

## 4. State dimensions and expression lifecycle

There is **no global candidate-to-fill enum**. The following are design state
roles; they do not extend accepted A4/A5 enums.

| Dimension | Owner | State/transition rule |
|---|---|---|
| Discovery | Source app | DISCOVERED -> ACTIVE when valid; EXPIRED at validity bound, RETRACTED by source, SUPERSEDED by accepted successor. Terminal records remain auditable. |
| Evaluation execution | TI | Pending/running and completed/partial/failed are run status; failure does not manufacture a disposition. |
| Intelligence disposition | TI domain | A4 SUPPORTIVE/WAIT/NO_TRADE/AVOID/CONFLICTED/ABSTAIN/INSUFFICIENT_EVIDENCE remains distinct from A2 class and A5 recommendation. |
| Operational proposal | TM | RECEIVED -> REVIEWING -> BLOCKED or APPROVED; SUBMITTING only after action-time checks. Approval expires/requires new review when bound inputs change. |
| Broker execution | Broker, reconciled by TM | Acknowledged/rejected/partial fill/fill/cancel/unknown outcomes recorded independently. Approval != submission != fill; cancellation does not undo fills. |

An active discovery can have TI WAIT and TM BLOCKED simultaneously. UI must show
all three, not replace them with QUALIFIED. Any qualification label names its
policy/version, scope and validity; it never asserts unconditional safety.

**Expression decision: one optional nested `proposed_expression` under Candidate;
no independently managed ProposedExpression aggregate and no mandatory TradeIntent.**
Editing the external expression increments the candidate revision. The proposal
is preserved byte-/semantically attributable alongside any A6 assessment.

A6's future TradeExpression is a separate immutable analytical result, with
source candidate revision, original proposal digest, evaluated alternatives,
rejected/unsupported reasons, policy, evidence/cutoff and fingerprint. It does
not mutate the proposal. Reassessment creates a new result/successor; changed
inputs expire its use for action, not erase history. TM selection and actual
order lifecycle remain distinct from analytical preference.

## 5. Object chain and normative ownership matrix

```text
Candidate [optional nested external expression]
 -> TI Opportunity / A4 thesis
 -> TradeExpression [A6 where supported]
 -> TM ExecutionIntent -> BrokerOrder -> Fill
 -> BrokerPosition -> TM OperationalPosition
 -> A5 advice -> monitoring results -> separately authorized TM review
```

The chain is not compulsory: no-trade candidates stop; manually created broker
positions enter through adoption; equity proposals need not pretend an
options-only A6 evaluated them. Position is exposure, not necessarily one order:
TM maps multiple fills/orders to broker-reconciled position identity explicitly.

| Object | Owner | Producer -> consumer | Executable / authority | Persistence, revision and replay |
|---|---|---|---|---|
| Watchlist | Subscriber app | User/app -> scanner/TI client | No; grouping only. | Version membership; retain admitted group context, not a live lookup on replay. |
| Candidate | Source app | Authenticated scanner/manual adapter -> TI/TM | No; proposal only. | Immutable revisions + receipt/discovery events; reconstruct without rescanning. |
| Nested proposed expression | Source app, within Candidate | Source -> A6/TM | No; source assertion only. | Version with Candidate; no independent lifecycle or mutable shared reference. |
| Opportunity/Thesis | TI | A2/A3/A3.9/A4 -> apps/A6/TM/A5 | No; advisory. | Preserve respective schemas/captures/policies; successors never rewrite parents. |
| TradeExpression | TI/A6 | Accepted future A6 evaluator -> TM | No; suitable representation is not permission. | Capture evaluated alternatives/inputs; new identity on changed evaluation. |
| ExecutionIntent | TM | Authorized TM workflow -> TM broker adapter | Conditionally actionable only through current TM gates. | Durable idempotent action identity, pinned approval and attempts; amendments reauthorized; replay never dispatches. |
| BrokerOrder | Broker; TM retains reconciled view | Broker -> TM/client projections | Actual broker order state; no UI-authored truth. | Preserve broker IDs, acknowledgements, updates and unknown states; replay events, never resubmit. |
| Fill | Broker | Broker -> TM reconciliation | Executed fact, not reusable command authority. | Immutable observed fill ID/account/quantity/price/time; corrections append with provenance. |
| BrokerPosition | Broker | Broker snapshots/events -> TM | Exposure truth, not command. | Version observations and acquisition times; retain uncertainty and corrections. |
| OperationalPosition | TM | Reconciliation/adoption -> risk/operations/TI | Managed lifecycle under TM grants, not a thesis. | Stable account/position identity, origin/adoption, revisions and broker refs; replay no broker access. |
| A5Advice | TI | A5 -> TM/subscriber | Non-executable advice. | Existing A5 capture/replay and policy version; no schema rename implied by this role name. |
| MonitoringMandate | TI after admission | Subscriber intent -> TI runtime | Bounded intelligence work only. | Immutable admitted revisions plus lifecycle log; preserve source A5 intent if supplied. |
| MonitoringResult | TI | Governed capability run -> subscriber/TM | Advisory run output, never action permission. | Mandate/run/attempt/input/policy/usage links; captured replay never reacquires evidence. |

Retention follows rights and recorded policy. Active commands, unknown outcomes,
unresolved costs and their idempotency records must not disappear before safe
reconciliation. Exact durations, storage engine and cross-system export protocol
are DEFERRED_WITH_BOUNDARY, required before claiming durable integration.
No shared database is mandated; each owner persists its own records and links.

## 6. A6 and future intelligence boundaries

Initial A6 scope is **deterministic selection/assessment of supported single-leg
CE/PE option expressions** over an admitted underlying thesis. It may compare
expiry/strike/moneyness, supplied liquidity/IV/Greeks and explicit policy/risk
constraints, retaining alternatives or NO_OPTION_TRADE. It remains future work.
No universal cash/future/options/spread optimizer, hedge/roll engine, multi-leg
policy, calibrated expected move or probability-of-profit is approved here.

Exact eligible instruments, long/short exposure permissions, orderability rules
and numeric thresholds require A6 architecture/acceptance; unapproved cases are
unsupported, not inferred permission for short options. Cash/future proposals can
have their own approved TM/TI validation path, not a false A6 endorsement.

External proposals undergo exact instrument/expiry/strike/side/shape validation,
thesis consistency, factual freshness and accepted liquidity/risk constraints.
Unsupported shape or incomplete required evidence cannot become a preferred
expression. A6 stores the original candidate reference plus evaluated alternatives
separately; TM owns account eligibility, capital allocation, actual quantity,
order parameters and action-time checks. A6 supplies analytical constraints, not
broker credentials or submission methods.

Sector Rotation is future TI context: it can prioritize a scanner's universe and
separately inform opportunity/qualification. It is not the scanner or existing
A3.6 sector-context specialist. Stock-specific contrary evidence survives.

Signal Qualification is a future acyclic consumer:
candidate -> cheap eligibility -> admitted A2/A3/A4 -> optional approved
sector/forecast/meta-label evidence -> qualification -> expression consideration.
Its dependency graph cannot call itself through a scanner, specialist or Planner.
Later evidence creates bounded successor evaluation, not repeated searching for
a favorable answer. Source BUY is not a qualification result.

A7 owns future forecasting, calibration, evaluation and controlled learning/
champion-challenger promotion. It is an overlay, grants no execution authority,
and is not required for initial deterministic A6. Forecast-enhanced comparison
requires admitted calibrated A7 evidence. Sector Rotation's exact placement
relative to A7/A8 remains DEFERRED_WITH_BOUNDARY; Signal Qualification follows
its review unless explicitly reordered. No speculative A7.0/SR milestone is added.

## 7. TM operations and pre-execution validation

TM owns broker connectivity/adapters and submit/modify/cancel; order/fill/position
reconciliation; external-position adoption; risk/authority modes; capital/quantity
limits; candidate intake; required TI checks; action-time revalidation; monitoring
requests; and operational responses to advice. **TM enforces intelligence
requirements; it does not become a second thesis engine.** TI may not place,
modify or cancel broker orders, including through a Sheet/UI escape hatch.

### Policy modes

| Mode | New-entry rule |
|---|---|
| TI_REQUIRED | Required TI validation must be present, fresh, complete for declared required scope and acceptable under the exact TM policy before approval; otherwise block. |
| TI_OPTIONAL | Only an independently approved, versioned TM strategy policy may permit entry without validated TI support. Record NOT_TI_VALIDATED and the policy basis; never claim TI approval. |

Optional missing enrichment does not invalidate an otherwise complete declared
required scope. Required absence stays in completeness under R1. The mode is
chosen by trusted policy before the request; deadline/outage cannot downgrade
TI_REQUIRED. An unfavorable result is not an outage: preserve it and apply the
policy's declared blocking dispositions. A TI_OPTIONAL missing-data path must
not bypass an applicable recorded veto by relabeling it unavailable. A4's
accepted A2 NO_TRADE gate remains unchanged.

TI's SUPPORTIVE never authorizes entry by itself. For TI_REQUIRED, approval pins
at minimum:

- Source namespace, candidate ID/revision and semantic digest; subject/purpose/
  horizon and optional group scope.
- Opportunity/result and A4 thesis/run IDs/fingerprints when required by profile;
  absent optional artifacts explicitly marked, not fabricated.
- Exact selected expression identity/revision/fingerprint, or original nested
  proposal digest and declared supported non-A6 validation path.
- Decision `as_of`, source/evidence availability and freshness cutoffs, validation
  expiry and input snapshot refs; acquisition time is not market-event time.
- TM strategy/mode/risk/authority policy versions and TI profile/domain/capability
  versions, declared required scope, actual gaps and disposition.
- Captured composition/binding identity where available. If missing, record
  COMPOSITION_UNAVAILABLE and retain available capability/policy/child hashes;
  no synthetic manifest or claim of full composition verification. A policy
  requiring exact composition must block until that facility exists.
- Scoped actor, account/environment, grant/approval refs, capital/quantity bounds,
  approved action parameters, decision validity and parent correlation.

Immediately before dispatch, TM rechecks current grants, broker exposure/open
orders, risk/capital, candidate/validation validity and exact selected parameters.
Changed proposal/expression requires revalidation against the new revision;
changed quantity/price within a previously approved envelope still needs TM's
current gate, and changes outside it require a new decision. Persist the approved
action identity/reservation before submission. Revocation or changed risk state
cannot be ignored because a UI button was previously enabled.

### Idempotent operational actions

Commands bind principal/application, account/environment, operation, idempotency
key and canonical body digest. Same key/body returns its recorded outcome;
different body conflicts. Broker client-order IDs are linked, not assumed to
guarantee exactly-once execution. Ambiguous timeout is OUTCOME_UNKNOWN: reconcile
broker acknowledgements/fills before retry, never blindly resubmit. Replace/cancel
is separately authorized against current order revision; partial fills survive.
No distributed atomic TI-approval/broker-fill transaction is claimed.

## 8. Positions, adoption and three kinds of monitoring

```text
Broker confirms exposure -> TM reconciles OperationalPosition
 -> TM requests position-linked intelligence monitoring
 -> TI admits normalized MonitoringMandate
 -> governed fresh input -> A5 -> advisory result
 -> TM revalidates broker truth/risk/authority -> possible separate action
```

Broker truth supersedes cached assumptions, but delayed/inconsistent responses
remain uncertain rather than guessed current. TM tracks opening/partial/closing/
closed operational state; A5 posture, thesis health and recommendation stay
orthogonal. A5's current supported baseline is one open single-leg position;
unsupported multi-leg shapes are not flattened, and absent A4 support stays
INSUFFICIENT_EVIDENCE. No fabricated entry thesis is required to preserve origin.

Detection leaves external exposure **BROKER_EXTERNAL / UNMANAGED**. Only an
explicit authorized adoption command establishes TM management scope. It pins
current broker account/position/snapshot, expected revision, acting principal,
management policy/limits and audit confirmation; external origin remains forever
visible. Adoption does not authorize every action or automatically create an
intelligence subscription. Account-wide exposure checks may observe unmanaged
positions; discretionary management requires adoption or a separately explicit
account-level authority, not implicit permission from detection.

After adoption TM may request monitoring. TI owns the admitted mandate, retaining
A5 WatchMandate/MonitoringNeed IDs/hashes as source advice. Those A5 values do not
schedule or auto-renew work. Verified position closure may terminate a linked
mandate under its admitted rule; stale/unknown position state is not closure.

| Monitoring concern | Owner | Question |
|---|---|---|
| Discovery refresh | Scanner | Which candidates satisfy discovery rules now? |
| Intelligence reevaluation | TI Monitoring | Has admitted evidence changed the assessment? |
| Operational monitoring | TM | What orders/exposure exist and what action is authorized? |

TI candidate mandates can exist without TM. Independent subscriber/horizon/purpose
mandates for one symbol must not merge. Share evidence only with compatible
rights, semantics, PIT, freshness and versions; never share mutable analysis or
authority. A TI outage does not revoke TM's independently authorized operations.

Fresh-input preparation must be accepted through capability/admission boundaries
before claiming live monitoring: no private provider/Planner bypass through
today's captured-read facade. For runtime delivery, retain the monitoring design's
finite validity/cancel model, no initial subscription aggregate/mandatory lease,
local single-writer periodic minimum, coalesce-to-latest missed runs, at-least-once
delivery/idempotent run identity and unknown-attempt reconciliation. Durable
publication/restart and shared-live quota/entitlement gates precede operational
claims. Event ingress and process/service separation need separately accepted
interfaces; no mandatory queue, database or microservice is prescribed.

## 9. Interaction, Sheets, workspaces and projections

Sheets is a replaceable client. It may edit subscriber-owned watchlists, candidate
drafts and allowed preferences, and submit adoption/approval/cancel requests.
Broker orders/positions, TI results, risk/authority, authoritative times and audit
are read-only projections. No credentials, canonical broker state or risk engine
belongs in Sheets. Proposed tabs are Dashboard, Watchlists, Candidates,
Opportunities, Active Positions, TI Advice, Orders, Trade Log, Alerts and scoped
Config; tab existence grants no operation.

An edit/button is a request. The authenticated application and human/service
principal are both identified; neither a Sheet row nor hidden cell grants rights.
Sensitive commands present exact account/environment, object revision, proposed
action and expiry for confirmation. Confirmation binds that digest and remains
subject to TM's live gate/idempotency. Stale edits are rejected; disconnected
clients must not auto-replay expired approvals on reconnect. External clients need
accepted authentication, revocation, session and anti-forgery/replay controls;
identity-provider/transport selection is DEFERRED_WITH_BOUNDARY, not bypassable.

Console means commands, event streams, controls, logs and trace inspection. UI
means dashboards, tables, charts, forms, alerts and drill-down. Both consume the
same governed interfaces; no Shell-outs to private engines or direct Sheet broker
calls. TI_SHELL's accepted surface remains unchanged, with no monitoring commands.

An optional unified daily-use Cockpit can host Scanner, Intelligence, Operations,
Monitoring, Position and Audit panels. Independent clients remain supported.
TI workspace asks **why does TI believe this?** and shows evidence, A2/A3/A4,
thesis, sector/forecast context when actually available, uncertainty and runs.
TM workspace asks **what exists and what may I do?** and shows orders, positions,
adoption, P&L, risk, authority and execution/monitoring health. A broker panel
projects reconciled truth; it is not another command authority.

Shared instrument selection is permitted; shared account authority is not.
Every request binds actor, application, account/environment and permitted scope.
Cross-account navigation cannot silently retain an approval or credential.
Client-visible permitted actions are advisory affordances: the server rechecks
on command, records denial and shows a reason, not just a disabled green/red icon.

### Candidate table projection

Mandatory visible information: source/scanner, instrument, horizon, discovery
state, TI evaluation status/disposition/freshness, selected/proposed expression
state, TM review/risk/authority, execution status, signal age/expiry and permitted
actions. Candidate ID/revision/correlation are stable row metadata and accessible
in drill-down. Group and source direction show explicit absent values when
unsupplied. In a scanner-only view TM fields say NOT_SUBMITTED/NOT_APPLICABLE,
not APPROVED; unevaluated TI is NOT_EVALUATED, not SUPPORTIVE.

Expandable fields: raw score/scale, source confidence/basis, provenance, detailed
sector/signal/forecast context, A6 alternatives, required gaps, policy versions,
usage and trace. Never merge discovery, TI disposition, TM approval and broker
fill into one traffic light. Layout may collapse columns but not hide these
distinctions or relabel optional absence as adverse evidence.

### Position table projection

| Field group | Authority / display requirement |
|---|---|
| Broker/account, position identity, origin/adoption | Broker identity mapped by TM; TM owns adoption/management state. |
| Instrument/expression, quantity, entry, mark, P&L/time | Broker-supplied truth with source/as-of; any TM-derived P&L/mark is explicitly labeled with calculation basis, not misrepresented as broker data. |
| A5 posture, thesis health, recommendation, protection | TI-owned immutable result and evaluation cutoff; supplied levels remain non-executable. |
| TM risk/authority and actions | TM-owned current policy/grants; enabled UI never substitutes for action-time checks. |
| TI Monitoring health, last evaluation, next due | TI runtime-owned only when it exists and is admitted; A5 hint separately labeled, never a scheduled guarantee. |

No admitted mandate means NOT_ACTIVE. An absent/unreachable runtime means
UNAVAILABLE/UNKNOWN; retain last-known status/time instead of claiming stopped
or healthy without evidence. Missed evaluation is OVERDUE/DEGRADED as observable.
Unmanaged origin never silently displays management/monitoring active. Last
broker update, last TI evaluation and next-due hint/runtime value are distinct.

UX delivery is staged: existing local Shell and separately established operations
tools first; accepted Sheets connector only when justified; then local TI/TM Web
workspace after API/session gates; then multi-panel Cockpit after recovery,
isolation/load and operational acceptance. UI demand cannot bypass backend gates.

## 10. Audit, replay, identity and access

One global correlation context links source event -> candidate revision -> TI
evidence/results/A4 -> expression -> TM policy/approval -> ExecutionIntent ->
broker ack/fill -> OperationalPosition -> mandate -> A5 run -> subsequent action.
Each keeps immutable local IDs, parent refs, revision, scope and checksums. Batch,
fan-out and shared evidence use multiple parent/beneficiary links; they are not
forced into one giant transaction ID. A manual adoption may start its own trace
with explicit unavailable prehistory, not a fabricated scanner lineage.

Correlation IDs grant no access. Authorization applies before trace/artifact
lookup and return, including cross-account/client boundaries. Redacted views do
not change canonical fingerprints; absence of access is not absence of evidence.
No secrets in candidate refs, traces, logs, Sheets or captures.

Replay answers why the decision was made then using decision-time records,
policy, authority decision refs and original uncertainty. Recorded replay does
not consult today's registry, retrieve later evidence or resubmit broker orders.
Verification requires exact compatible captured inputs/bindings; unavailable
bindings are unverifiable, not silently substituted. Policy comparison is a
separate run. R3 future parent composition must preserve existing child hashes.
Command-outcome reconstruction never grants current permission to act again.

## 11. Failures and versioned latency/cost profiles

| Failure | Required behavior |
|---|---|
| Scanner unavailable | No fabricated candidates; existing candidates age/expire; other sources and operational positions remain independent. |
| TI unavailable | TI_REQUIRED entries block. Only preapproved TI_OPTIONAL strategies may continue with NOT_TI_VALIDATED; existing TM operations remain bounded by their own current authority. |
| Broker unavailable | Block new exposure where truth/execution cannot be established; outstanding attempts may be unknown. Reconcile before retry, retain reservations and uncertainty; no blind replay. |
| Sheet/Web unavailable | Backend continues only within existing admitted bounds; no fabricated confirmations, replayed stale approvals or need for UI uptime to preserve safety controls. |
| TI Monitoring unavailable | Show overdue/degraded/unknown intelligence as observable; TM operational controls continue independently. Last advice is not refreshed by display. |

No failed provider, capability or UI becomes positive or negative market evidence.
Timeout does not establish zero usage or release unknown operational exposure.
No exactly-once broker effect or uninterrupted local protection is promised by
this architecture; outages can limit what TM can actually observe or perform.

Profiles are trusted versioned policy, not fixed SLAs or user-granted authority:

| Profile | Intended trade-off, subject to explicit accepted scope |
|---|---|
| FAST_INTRADAY | Prepared compatible evidence, bounded deterministic eligibility/thesis checks; no opportunistic deep-research dependency on the critical path. |
| NORMAL_INTRADAY | Selective additional context where its freshness and deadline fit. |
| POSITIONAL | Broader company/event/sector context and longer analytical horizon, without assuming slower data is fresh enough. |
| DEEP_RESEARCH | Explicit larger bounded evidence/research scope; not a fast execution SLA. |

Every profile declares exact required/optional layers/evidence, allowed versions,
freshness, deadline, calls/tokens/time/known-money budgets, retry/stop and outage
behavior. FAST is not permission to omit a required A4 or risk gate. Optional
enrichment may fail visibly while a valid baseline survives; required absence
never shrinks with registry availability. Known-zero and unknown monetary usage
remain distinct; shared attempts keep exact usage/allocation lineage.

## 12. Pluggability classification

**HOT ⇒ COLD ⇒ STRUCTURAL**; reverse implications are not assumed. Requiredness
is separate from installation, authorization, runtime success and replaceability.
Targets below are architecture guarantees to prove, not compliance certification.

| Component | Target / replacement boundary |
|---|---|
| Scanner source adapters | STRUCTURAL normalized candidate contract; COLD source bindings and authentication configuration. |
| TI capabilities | Versioned STRUCTURAL meaning; approved COLD composition preserving R1 scope and old replay. |
| Broker adapters | TM-owned STRUCTURAL command/truth contract; COLD selection only with open-order/position reconciliation and recovery proof. |
| Monitoring scheduler/persistence | COLD replacement preserving admitted mandates, run identity, reservations and restart semantics. |
| Sheet connector | Optional STRUCTURAL client, trusted COLD deployment/configuration; no cell-defined credentials/grants. |
| UI clients/panels | Replaceable presentation over STRUCTURAL governed interfaces; trusted composition/config, no new domain authority. |
| Model providers | Optional governed COLD adapters; required only inside an explicitly admitted model-dependent lane. |

No HOT replacement is required. Current route fallback across pinned adapters is
not HOT registry mutation. R2–R5 remain pre-A6 hardening, not retroactive A5 freeze
blockers. New peer publication, HOT, remote operations and runtime monitoring
retain existing deferral governance; no generic registry or duplicate dependency
model is introduced.

## 13. Nine pre-thesis decisions and bounded open choices

| # | Decision | Disposition / remaining boundary |
|---|---|---|
| 1 | Candidate fields, source namespace, immutable revisions, event mapping and digest-based idempotency are defined in §3. | RESOLVED contract semantics; DEFERRED_WITH_BOUNDARY for executable schema publication and transport auth implementation. No external intake before auth acceptance. |
| 2 | External expression is nested under Candidate revision, not an independent aggregate; no mandatory TradeIntent. | RESOLVED. A6 evaluated alternatives remain separate analytical results. |
| 3 | Initial A6 is deterministic supported single-leg CE/PE option expression, not universal allocation/spread optimization. | RESOLVED boundary; DEFERRED_WITH_BOUNDARY for eligibility, side permissions and numeric policy at A6 acceptance. Unsupported until approved. |
| 4 | TI_REQUIRED and independently approved TI_OPTIONAL semantics, veto/outage distinction and pinned action linkage are defined in §7. | RESOLVED governance; DEFERRED_WITH_BOUNDARY for concrete TM strategy policy values requiring TM-side acceptance, no live claim. |
| 5 | Global correlation plus local IDs/parents, scoped access and command idempotency; no order replay. | RESOLVED semantics; DEFERRED_WITH_BOUNDARY for rights-compliant retention periods and durable cross-system export/store protocol. |
| 6 | Fresh-input admission must precede live validation; TI owns Monitoring Runtime with local single-writer recovery gates. | RESOLVED ownership; DEFERRED_WITH_BOUNDARY for live facade/input binding, event ingress and concrete host/store delivery. Captured reads are not a substitute. |
| 7 | External origin remains UNMANAGED until explicit scoped adoption; no fabricated thesis or automatic monitoring. | RESOLVED semantics; DEFERRED_WITH_BOUNDARY for concrete TM authority modes/account-level emergency limits, which must be approved before such operations. |
| 8 | Actor/application/account-scoped sessions, confirmed digest-bound Sheet commands and server-side revalidation. | RESOLVED boundary; DEFERRED_WITH_BOUNDARY for identity provider, transport/session protocol and UI implementation. No authentication inferred from display access. |
| 9 | Sector context can feed scanner and qualification; qualification acyclic; A7 overlay and initial A6 independence. | RESOLVED dependency direction; exact Sector Rotation/Signal Qualification milestone placement remains DEFERRED_WITH_BOUNDARY, without changing A8/A9/A10. |

These are bounded implementation/operational choices, not unresolved ownership
contradictions. The thesis may describe this normative model if it labels future
delivery and deferred choices honestly. It must not invent dates, calibrated
accuracy, SLAs, broker execution guarantees or accepted A6/runtime behavior.

## 14. Derived documents, acceptance gates and next step

Do not create additional architecture documents immediately: this document
contains the initial candidate, integration and interaction contract boundaries.
Before implementation, separate TIAF_SCANNER_ARCHITECTURE.md for concrete source/
wire schema and auth mappings; TIAF_TM_TI_INTEGRATION_ARCHITECTURE.md for TM-owned
action/adoption/live-validation acceptance; and
TIAF_INTERACTION_WORKSPACE_ARCHITECTURE.md for actual transport/session/UX delivery
when those workstreams are authorized. Those names are recommendations, not
existing artifacts or permission to implement them.

Future acceptance must demonstrate duplicate/conflicting delivery handling,
revision invalidation, wrong-account/revoked authority denial, no required-scope
shrink, stale/unfavorable validation blocks, supported/unsupported expression
separation, partial-fill/unknown submission recovery, explicit adoption,
monitoring-vs-operational isolation, offline replay without effects and preserved
child hashes. Read-only projections must not manufacture current truth or grants.

Architecture decision: **READY_TO_ACCEPT_TRADING_ECOSYSTEM_ARCHITECTURE**.
Thesis readiness: **ECOSYSTEM_READY_FOR_THESIS**.

Historical next architecture prompt: **`TIAF — TRADING ECOSYSTEM THESIS CREATION`**.
At this design's review, the operational roadmap's A5 final freeze/tag-readiness
gate remained separate;
this design does not begin A6, R2–R5, integration or runtime delivery. No commit,
tag or push is performed by this architecture pass.
