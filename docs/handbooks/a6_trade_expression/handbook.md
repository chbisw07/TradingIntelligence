# 1. What Trade Expression Intelligence Means

A market thesis is a statement about an underlying opportunity: the direction that may be supportable, the period over which the idea matters, and the evidence that could defeat it. An option expression is a particular instrument through which somebody might seek exposure to that idea. These are related questions, but answering the first does not answer the second. A bullish view does not identify an expiry, establish that a quoted premium is usable, or show that the surrounding contracts were compared fairly.

Consider the trader who says, “I am bullish on KAYNES for three weeks. What should I trade?” There are already several unresolved questions inside that sentence. Has TI actually admitted the thesis, or is bullishness only the caller's opinion? Does three weeks mean 21 calendar days or 15 trading sessions? Are there supported listed options whose life extends beyond that target? Do the quoted prices describe the market at the assessment cutoff? A6 exists to make those questions explicit before presenting an expression as suitable.

The proposed capability therefore asks a narrower, defensible question: within this declared set of captured contracts, which supported option passes the stated constraints and best matches the allowed preferences? It can prefer a contract without asserting that it is profitable, affordable for a particular account, or executable now. It can also conclude that there is no suitable expression, that a known condition calls for waiting, or that the evidence does not support a decision.

:::figure 01 A good thesis and a suitable expression are separate tests
| Underlying thesis | Expression evidence supports suitability | Expression fails or cannot be established |
| --- | --- | --- |
| Admitted and supportive | A6 may identify a preferred expression; TM still decides action. | Preserve the thesis but return no option trade, wait or insufficient evidence as appropriate. |
| Prohibited or not admitted | A good-looking quote cannot repair the thesis. No selection permission arises. | Neither a supportive thesis nor a suitable expression has been established. |
:::

## Why refusal is part of intelligence

An engine that always returns a contract hides the possibility that the available instruments do not represent the idea well. It may force a short-dated expiry onto a longer thesis, use an old last trade as though it were an executable quote, or call a low-priced option attractive without an appropriate comparison. Those shortcuts create apparent decisiveness by discarding the question being asked.

A6's alternative is not endless caution without a result. It is a bounded assessment with a specific conclusion and an explanation of the evidence needed to change that conclusion. “All captured eligible expiries end too soon” is actionable information about expression fit. “The quote's market time is unknown” is actionable information about data qualification. They are different answers and should lead to different next steps.

> WHY THIS EXISTS — A6 prevents an attractive underlying story from silently becoming a poorly supported instrument choice. It tests expression suitability; it does not certify future returns.

This handbook explains the proposed design, not an implemented trading service. All examples are synthetic teaching fixtures. Architecture sections 1–5 govern the meaning of suitability, admission and absence; Appendix A identifies the sources used throughout.

# 2. Where A6 Sits in the Trading Ecosystem

The ecosystem divides work by the truth each component can responsibly own. A scanner discovers something worth attention and may propose an expression of its own. TI develops evidence-linked intelligence. A4 challenges the underlying thesis. A6 evaluates an option expression only after admission. TradeMonitor, abbreviated TM, determines whether an action is operationally permitted. The broker supplies actual order, fill and position truth. A shared screen must not erase these distinctions.

:::flow 02 The owner chain, not a single trading decision
SCANNER / USER — Candidate revision and intent; a proposal is not TI validation.
↓ TI / A4 — Evidence-linked thesis challenge; preserve vetoes, conflict and uncertainty.
↓ A6 — Non-executable expression assessment, preferred candidate or explicit absence.
↓ TM — Account, permission, capital, risk, quantity and action-time checks.
↓ BROKER — Orders, fills and actual position facts; outcomes are not fabricated by TI.
:::

The word “preferred” belongs inside A6's comparison. It does not cross the TM boundary as “approved.” A contract that passed the analytical gates at 10:00 may be unavailable when TM checks it later. An account may already have correlated exposure or lack the necessary permission. A6 has neither the operational mandate nor the authoritative current state to resolve those questions.

| Object or decision | Owner | What must remain separate |
| --- | --- | --- |
| Source Candidate and optional proposed expression | Scanner or originating caller | TI does not edit the original proposal to make it agree with the assessment. |
| Baseline and specialist evidence | A2 / A3 | A6 does not recalculate or overwrite it. |
| Surviving thesis and residual conflict | A4 | A6 cannot turn NO_TRADE or AVOID into permission. |
| Candidate comparison and expression assessment | A6 | Analytical suitability is not an order or an account allocation. |
| Operational position, execution intent and final quantity | TM | A6 receives relevant references, not ownership of the position. |
| Order and fill facts | Broker | A planned or recommended transaction is not a fill. |

After execution, TM owns the operational position. A5 can evaluate a supplied position snapshot and current admitted thesis, producing advice rather than changing broker state. Future TI Monitoring may arrange separately admitted reassessments. These are not jobs started by A6, and an A6 result is not a standing authorization to keep buying the same contract.

In an ecosystem TI_REQUIRED route, TM requires acceptable TI analysis before approval under its policy. TI_OPTIONAL describes a separately authorized independent TM strategy path, visibly not TI-validated; it is not a way to reinterpret a TI veto as an outage. An unavailable capability and an unfavorable analytical opinion must remain distinguishable. Manual broker adoption and non-option workflows do not acquire an artificial A6 prerequisite.

This division also makes disagreements useful. The scanner's original view, A4's surviving thesis and A6's expression refusal can all coexist in the record. There is no need to overwrite history to produce a single attractive story. Sources: ecosystem ownership architecture; A4 and A5 architectures; A6 sections 1 and 8.

# 3. What A6 v1 Supports—and Why It Is Bounded

The proposed first version considers long single-leg calls and puts on captured, explicitly eligible NSE equity or index option contracts. A bullish admitted thesis maps to a CE expression and a bearish thesis to a PE expression. The familiar symbol names in this handbook are teaching labels, not evidence that those options are presently listed or permitted. Venue, underlying, contract identity, strike, side and expiry must come from qualified captured evidence.

| Proposed initial scope | Outside v1 or separately deferred |
| --- | --- |
| One subject, admitted direction and resolved holding target per assessment | Portfolio, cross-asset or account-wide optimization |
| Long single-leg CE / PE | Short options, covered/naked writing and multi-leg strategies |
| Listed ATM / ITM1 / OTM1 comparisons within declared expiries | Arbitrary strike searches, delta-target optimization or invented contracts |
| Deterministic suitability gates, ranking, explanation and replay | Learned utility, calibrated probability or automatic strategy synthesis |
| Advisory contract identity and evidence context | Quantity, capital allocation, order type, routing, stops/targets or broker action |

This is a scope decision rather than a claim that more sophisticated strategies lack value. A multi-leg expression adds relationships that single-contract screening cannot establish: leg compatibility, combined economics and the consequences of incomplete execution, among others. It deserves its own accepted contracts and evidence requirements. Calling two individually acceptable options a supported spread would bypass that design work.

Futures and cash instruments likewise have different expression semantics. They cannot simply be added as more rows in a CE/PE selector. A6's first baseline must establish whether its own bounded questions can be answered consistently, explained and replayed before the comparison becomes broader. Boundedness also makes absence meaningful: the output can say exactly which universe was assessed rather than implying that every possible strategy was searched.

Quantity is excluded for a different reason. It is not merely unfinished feature work; it belongs with TM's account, capital, risk and operational authority. A captured lot-size reference helps identify a contract convention. It is not a suggestion to trade one lot, and a per-unit premium cap does not establish total account affordability. No “recommended lots” column belongs in the canonical A6 result.

SigmaDSL is not part of TI A6 v1. Typed contracts and deterministic policies are sufficient for this bounded design; no parser, compiler or compatibility layer is required. A future programmable SigmaTrader-style product may share the principles of determinism and replay while remaining a separate product. This is not a hidden prerequisite for completing A6.

> CONSTRAINT — The design is specific about what it can compare. An unsupported instrument or strategy is not a negative market opinion, and it must not be silently translated into a supported substitute.

# 4. From Human Intent to One Typed Assessment

People express intent in shorthand. A reliable analytical boundary cannot operate on shorthand alone. “Bullish for three weeks” must become a specific subject, a direction constraint consistent with the admitted thesis, an explicit holding target and references to captured evidence. The distinction between intent and admission matters: the user may request a bullish assessment, but the request cannot create A4 SUPPORTIVE.

:::figure 03 Four interaction surfaces, one meaning
| Surface | Translation responsibility | Shared destination |
| --- | --- | --- |
| Future plain English | Resolve ambiguity and show the interpretation for confirmation. | Typed request + admitted evidence references |
| Structured Shell / REPL | Parse the same bounded command and preserve explicit fields. | Same governed facade |
| Future Web form | Validate fields and render the canonical result without changing it. | Same proposed expression.assess capability |
| Future Python / API caller | Supply typed intent and permitted logical artifacts. | Same admission, gates and ranking |
:::

A future language interface might show, “Interpret three weeks as 21 calendar days ending at this explicit Asia/Kolkata timestamp?” That is a proposed interaction, not an existing conversational feature. The architecture does not approve a universal trading-day calendar conversion. If the user means sessions rather than calendar days, the interface must not guess. The exact confirmation behavior is a thesis finding for reconciliation.

| Request dimension | What the user means | What the boundary needs |
| --- | --- | --- |
| Subject | KAYNES | Neutral identity consistent with the upstream thesis and evidence |
| Direction | Bullish | A constraint matching the admitted positive thesis, not an override |
| Horizon | Three weeks | Explicit target, duration basis and compatible upstream bounds |
| Preference | Prefer ATM | A closed preference order among supported neighborhoods |
| Premium restriction | Do not exceed this per-unit amount | Explicit currency/amount; not an account allocation |
| Evidence | Use the supplied analysis | Authorized, integrity-checked logical artifacts and original cutoffs |

The future public operation resolves a logical request artifact, rather than accepting arbitrary files, provider objects or broker credentials. Authorization is checked independently of whether the artifact exists. A selected capability is not necessarily permitted for this caller, and a caller who knows an artifact identifier does not automatically gain access to it.

The policy is chosen by trusted startup composition. A user's permitted preferences can narrow the search or reorder supported moneyness choices, but cannot relax a freshness gate or admit an unsupported strike. This protects the meaning of comparisons between runs: a changed request creates a new record, while a changed engineering policy must have a distinct identity.

## Illustrative confirmation card—not a working command

> REQUEST PREVIEW — Subject KAYNES; bullish constraint; POSITIONAL; explicit exit target; ATM → ITM1 → OTM1 preference; admitted A4 and chain references required. “Confirm interpretation” would confirm intent only, never execution permission.

The same confirmation cannot be used to consent to a trade. It resolves what analysis was requested. Sources: A6 section 4 and section 9; Shell architecture and source-admission boundaries.

# 5. How A6 Builds the Candidate Set

A6 does not begin by searching for a persuasive option. It begins with an admitted thesis and a declared captured universe. The draft bounds that universe to one subject and at most three expiry chains, each with at most 512 listed strikes. It selects up to three nearby contracts per expiry, giving at most nine candidates. Inputs beyond the bounds are refused rather than silently truncated into a different comparison.

:::flow 04 The candidate-generation funnel
ADMISSION — Verified complete supportive A4 result; supported surviving primary thesis; consistent direction.
↓ DECLARED UNIVERSE — One subject; one to three captured expiries; scope and omissions visible.
↓ LISTED GEOMETRY — Nearest ATM plus one listed step ITM and OTM for CE or PE.
↓ REQUIRED EVIDENCE — Identity, timing, quotes, depth, horizon fit and requested restrictions.
↓ BOUNDED RESULT — At most nine evaluations; only fully eligible candidates may be ranked.
:::

The nearest listed strike is the ATM anchor. If two strikes are equally distant from the qualified underlying reference, the lower listed strike wins the tie. Neighboring means the actual next listed strike, not a hard-coded numerical interval. This matters for irregular spacing and incomplete captures: an absent row cannot automatically be treated as proof that the contract is unlisted.

For calls, the lower neighbor is ITM1 and the higher neighbor OTM1. For puts the direction reverses. These are the draft's geometric neighborhood labels. They do not carry an assumed delta, profit probability or ranking score. A later chapter examines why a geometric ATM label may itself deserve user-facing clarification when spot is between strikes.

The coverage manifest explains which expiries were considered and which were excluded from scope. Therefore, a preferred result means preferred within this declared comparison, not best among every exchange contract or strategy. Source omissions must remain visible even when the evaluated subset produces an available expression.

## Why complete coverage can be demanding

The draft requires complete hard-gate evidence for required selected slots before naming a preferred contract. If an expected rival has an unknown quote, it could have outranked the apparently valid candidate. The design withholds a preferred answer rather than pretending that the rival did not exist. Known-unlisted slots are different: attributable evidence of absence can support a recorded exclusion.

This is deliberately conservative. It can make the result unavailable even when the trader sees a convincing quote for one contract. Whether a candidate already decisively rejected on another gate still needs every other field is an unresolved precedence detail, recorded as THESIS_FINDING TF-05. The handbook does not introduce a partial-ranking exception. Sources: A6 sections 5 and 6.1.

# 6. Expiry Is a Horizon-Fit Problem

The holding target describes how long the idea needs an expression. The expiry tells us when a particular contract ends. Their relationship must be evaluated explicitly; they are not interchangeable labels. A highly liquid near-expiry contract cannot satisfy a thesis that requires the option to remain alive beyond that expiry.

The current draft requires residual life after the intended exit: at least 24 hours for DAY and 72 hours for POSITIONAL. These are provisional engineering cushions, not exchange requirements, calibrated safety margins or a computed theta forecast. DAY also requires an admitted session interval containing the assessment and intended exit. POSITIONAL is bounded to 90 calendar days in this proposed version.

:::figure 05 Horizon and expiry-fit ladder—illustrative, not live advice
| Captured timing relation | Visual position relative to target T | Draft POSITIONAL result |
| --- | --- | --- |
| Expiry before intended exit | Expiry → T | FAIL: instrument ends before the target. |
| Expiry 48 hours after exit | T → 48h → Expiry | FAIL: below the 72-hour cushion. |
| Expiry 96 hours after exit | T → 72h minimum → 24h excess → Expiry | PASS on timing; all other gates still apply. |
| Expiry date only | T → [unknown exact cutoff] | UNKNOWN: precise residual life not established. |
:::

Why might more time be useful? In general options education, time to expiration is one determinant of premium; the relationship between time erosion and directional sensitivity changes with time and moneyness. A longer-dated contract can provide a different time exposure, but “further” does not mean automatically better, cheaper or safe. See OIC's [Time Erosion vs. Delta Effect](https://www.optionseducation.org/optionsoverview/leaps-time-erosion-versus-delta-effect). A6's specific choice remains the captured-policy comparison, not a general rule imported from that educational discussion.

Weekly and monthly descriptions are optional admitted series metadata. They cannot be inferred from the weekday or a familiar symbol. The draft gives no ranking bonus to the word monthly; it compares actual timing fit and other gates. It also does not construct an expiry timestamp by adding an assumed close time to a date.

Suppose a user changes the same bullish idea from three weeks to four weeks. That is not a cosmetic filter change: the target and upstream horizon compatibility must be checked again. An expiry with four days of spare life in the first assessment may now end too early. If facts conclusively show that every declared expiry fails the target, the answer is NO_OPTION_TRADE, not a quietly shortened thesis.

> WHAT CAN GO WRONG — Calendar days, trading sessions, expiry date, expiration instant and freshness age describe different things. Convenient labels cannot substitute for the missing timing evidence.

The practical consequence is important: the current Dhan date-only/acquisition-only captures cannot alone satisfy the strict proposed timing gates. Chapter 8 explains that limitation without pretending that a new authoritative timing source already exists.

# 7. Strike, Moneyness and the Economics of the Same Thesis

Different strikes can provide different economic exposure to the same underlying view. In basic terminology, a call is in the money when spot exceeds strike; a put is in the money when spot is below strike. Premium contains intrinsic and time-value components. Those definitions help explain why a lower displayed premium is not a complete comparison of two expressions. See OIC's [Options Pricing](https://www.optionseducation.org/optionsoverview/options-pricing).

:::figure 06 Candidate cards around an exact ATM anchor—illustrative, not live advice
| Lower listed strike: 3,900 | Nearest listed strike: 4,000 | Higher listed strike: 4,100 |
| --- | --- | --- |
| Spot fixture: 4,000. For CE: ITM1. For PE: OTM1. | Spot fixture: 4,000. ATM for either side in this fixture. | Spot fixture: 4,000. For CE: OTM1. For PE: ITM1. |
| A neighborhood label, not a promised sensitivity or quantity. | A reference point, not an unconditional buy instruction. | A smaller premium, if observed, would not prove better value. |
:::

Delta describes local modeled sensitivity to a change in the underlying while other pricing inputs are held constant. It is not fixed, and the same strike label does not guarantee the same delta across expiries or conditions. Higher absolute sensitivity can matter to a trader, but it does not itself establish account affordability or a target-hit probability. OIC's [Options Delta](https://www.optionseducation.org/advancedconcepts/delta) explains the sensitivity concept; A6 v1 does not calculate delta or use delta bands to generate its candidate set.

That distinction prevents a common misunderstanding: “cheaper OTM” is not synonymous with “the same exposure for less money.” Nor can this handbook attach a win probability to the lower premium. The proposed baseline does not have the calibrated distribution needed for that statement. It screens the supported neighborhood using facts and constraints, then applies a declared ordering.

The default preference is ATM, then ITM1, then OTM1. However, a preference is reached only after hard gates, and spread tier is compared before moneyness rank. A fresh, eligible ITM1 candidate in a better spread tier can outrank ATM. Conversely, a user may reorder the permitted neighborhood preference, but cannot authorize an otherwise failing candidate merely by liking its strike.

## The cost question A6 can and cannot answer

A caller may supply an explicit per-unit premium cap. A6 compares the captured ask with that cap; it does not turn it into total capital at risk, choose a lot count or declare the trade affordable. A request to “prefer cheaper premium” is broader than the supported ordering: ask is not an independent ranking key in the draft. The language interface must not silently invent a cheapest-first policy. TF-08 records this interaction issue for reconciliation.

The opportunity cost of a narrow baseline is real. Some economically interesting candidates outside its neighborhood will not be explored. Its benefit is that the reader can inspect the entire bounded selection rule instead of relying on an unexplained optimizer. Sources: A6 sections 6.1, 6.4 and 7.

# 8. Liquidity, Freshness and Evidence Quality

A quoted contract is not a promise of execution. The bid and ask describe a displayed market at an observation time; size describes observed top-book presence. Spread is an important burden to notice, but does not determine a future fill price or guarantee that displayed depth will remain. OIC's [Understanding the Bid and Ask Prices for Options](https://www.optionseducation.org/news/understanding-the-bid-and-ask-prices-for-options) provides general educational context. Here, the normative question is whether the captured facts pass the A6 draft policy.

The draft requires finite positive bid and ask, ask not below bid, and positive captured bid and ask quantities. It measures relative spread in basis points using the midpoint. For a bid of 99.5 and ask of 100.5, the midpoint is 100 and the spread is 100 bps, or 1%. These are synthetic values. The hard maximum is 500 bps; the first ranking tier ends at 100 bps. Neither threshold establishes expected execution quality.

:::flow 07 Quote quality gate
IDENTITY — Does this observation belong to the exact declared contract and underlying?
↓ TIME — Is the market observation qualified and no older than 60 seconds at the cutoff?
↓ GEOMETRY — Are bid and ask positive, finite and non-crossed?
↓ DEPTH / SPREAD — Are both captured top quantities positive, and spread ≤ 500 bps?
↓ EVIDENCE STATE — PASS can proceed; FAIL is a known constraint failure; UNKNOWN cannot be filled with optimism.
:::

## The five timing concepts the screen must not blur

:::figure 08 Different clocks answer different questions—illustrative timing only
| Concept | Synthetic illustration | What it establishes |
| --- | --- | --- |
| Market event / observation time | Quote observed at 09:59:50 | When the represented market fact was observed, if the source qualifies it. |
| Acquisition time | TI receives it at 09:59:55 | When TI obtained the evidence, not necessarily when the market changed. |
| Assessment cutoff / quote age | As-of 10:00:00; qualified age 10 seconds | Which point-in-time question is answered and the age relative to that cutoff. |
| Expiry date | A calendar date on a chain | Which date is named; not the precise moment the option ends. |
| Expiration instant | A separately sourced aware timestamp | The exact point needed to compare residual life with the holding target. |
:::

If a provider delivers an old quote at 09:59:55 but does not supply a qualified observation time, “received five seconds ago” does not prove that the quote is five seconds old. In the current Dhan chain path, the architecture identifies acquisition-time semantics and date-only expiries. Renaming those fields cannot create the missing market time or expiration instant. Under the proposed strict policy, those captures alone lead to INSUFFICIENT_EVIDENCE, even when their prices look plausible.

This is a product limitation, not a solution hidden in the handbook. TF-01 and TF-02 require architecture reconciliation to address timing-source feasibility and exact expiry representation. No substitute source, assumed exchange close, calendar engine or weaker freshness profile has been implemented or approved here. All canonical application timestamps remain aware and normalize to Asia/Kolkata, but consistent timezone formatting does not fix uncertain time meaning.

## Known zero, missing and stale are different

| Captured fact | Interpretation in the draft |
| --- | --- |
| Volume 0 or OI 0 | Legitimate contextual observation, not missing merely because zero is falsy. |
| Top quantity 0 | Known absence of required positive top depth: FAIL. |
| Required top quantity absent | UNKNOWN, not proof of zero or adequate depth. |
| Valid-looking quote 180 seconds old | Stale for the 60-second gate: insufficient current evidence, not proof of present illiquidity. |
| Missing optional IV or Greeks | Visible contextual limitation, not by itself a hard failure. |

Volume and OI are informational in v1. They do not compensate for absent bid/ask evidence. A stale underlying reference can also invalidate strike geometry: a recent option quote alone does not make an old spot reference fresh. The user needs the original facts and their limitations, not a single green “data OK” badge.

# 9. Volatility, Premium and Event Context

An option is not a fixed multiple of its underlying. Its premium can change with time and implied volatility as well as the underlying price. Around events, those influences can work against the directional story; being right about direction does not by itself explain the option's outcome. This qualitative distinction is described in OIC's [Option Price Behavior](https://www.optionseducation.org/referencelibrary/faq/option-price-behavior). A6 does not turn that background into an unvalidated price forecast.

The draft deliberately separates hard eligibility, ranking and information. IV, delta, theta, skew, IV rank/percentile and historical ATR can be displayed only with their admitted meanings and provenance. Optional missing Greeks do not force a made-up value or an automatic failure. Ambiguous units remain PROVIDER_DEFINED or AMBIGUOUS. A raw percentage-like IV field cannot be normalized by guesswork, and a straddle premium is not an expected move.

| Layer of use | v1 treatment | What is not inferred |
| --- | --- | --- |
| Hard gate | Qualified quotes, spread/depth, timing, horizon, explicit cap and applicable events | No fair-value or calibrated economic-return threshold |
| Ranking | Declared spread tier, moneyness preference, residual-life excess and tie-breakers | No hidden IV, premium-cheapness or delta score |
| Information | Qualified IV/Greeks and other admitted context, with gaps visible | No synthesized Greek, target-hit probability or “underpriced” label |

This restraint matters when a trader asks whether premiums are distorted. The concern is economically legitimate, but v1 cannot certify richness or cheapness without a supported model and evidence. It can identify a violated premium cap, problematic spread or admitted blocking event. It must say when the broader valuation question remains unanswered. A nice-looking selection should not imply that every economic dimension has been optimized.

## What an event can change

The proposed rule uses admitted event facts, not live research inside A6. A known material event within the holding interval after the cutoff and up to the intended exit produces WAIT_FOR_EXPRESSION. This can include relevant company, policy, corporate-action or regulatory events if they are already admitted with appropriate scope and materiality. A6 does not classify news headlines with a hidden model or invent sentiment.

Unknown event coverage is not “no events.” By default it remains a disclosed limitation. If the caller requires event-clear screening, complete qualified coverage becomes a requirement, and unknown coverage yields insufficient evidence. Neither setting removes a known blocking event. TF-10 asks for clearer architecture treatment of event materiality, coverage intervals and uncertainty; this handbook does not resolve ambiguous event timing on its own.

> WHY NOT A PENALTY SCORE? — The current draft uses an explicit wait condition for known material events, not a small deduction that a favorable strike could outweigh. The record should make that choice visible.

# 10. Ranking: A Transparent Comparison, Not a Promise

Ranking answers a question only after eligibility. Comparing invalid candidates with valid ones in one weighted score would permit a sufficiently attractive preference to compensate for a hard failure. The draft avoids that trade-off: a stale quote, failed expiry fit or prohibited upstream thesis cannot be repaired by a better moneyness preference.

Among fully eligible candidates, the order is lexicographic. That means compare the first criterion; only if tied compare the next. There is no universal suitability score, average confidence or hidden set of weights. This makes the consequence of a policy choice inspectable even when somebody disagrees with it.

:::flow 09 Ranking ladder: first unequal key decides
PRECONDITION — All required gates and scoped coverage support ranking.
1 → SPREAD TIER — Tier 0 (≤ 100 bps) before tier 1 (> 100 to 500 bps).
2 → MONEYNESS PREFERENCE — Default ATM, ITM1, OTM1; permitted request order may differ.
3 → EXPIRY CUSHION EXCESS — Smaller excess first, among expiries already fitting the target.
4 → EXACT SPREAD — Lower unrounded spread if earlier keys tie.
5 → CANONICAL CONTRACT KEY — Stable neutral identity breaks the remaining tie.
:::

Take two eligible candidates in the same spread tier and expiry: ATM at 90 bps and ITM1 at 70 bps. Under the default preference, ATM wins. The correct explanation is not “ATM has better liquidity”; the tighter spread belongs to ITM1. ATM wins because preference is compared before exact spread within the same tier. A transparent engine must be willing to state such a trade-off rather than invent a flattering reason afterward.

Now put ATM just above the first tier boundary while ITM1 remains below it. ITM1 can win because tier comes first. This discontinuity is intentional in the draft ordering but has not been calibrated as economically optimal. TF-04 proposes explaining and reviewing it before acceptance, not moving the boundary to make a particular example look attractive.

Determinism does not prove prediction quality. It supplies a control: the same admitted facts, cutoff and policy can be replayed to explain the same result. Future A7-supported comparison may be evaluated against that control instead of deleting it. Differences can then be attributed to new evidence or policy, rather than a model's unrecorded change of preference.

One preferred candidate and up to two eligible alternatives are shown. Every bounded evaluation remains available for inspection, including eligible contracts outside the displayed top three. “Not selected” is not “rejected.” The display must not turn a compact shortlist into a false claim that every other candidate was invalid. Sources: A6 sections 6–7 and 10.

# 11. Reading “Why This Contract?”

A useful explanation should let the reader challenge the actual comparison. It should identify the admitted thesis, the declared universe, the facts and thresholds used by each gate, the decisive ranking difference, the relevant gaps and the conditions that invalidate the result. It should not be a fluent summary that loses the comparison's less convenient details.

:::figure 10 An explanation panel—illustrative, not live advice
| Preferred: synthetic KAYNES ATM CE | Alternatives and rejections |
| --- | --- |
| Upstream thesis: supportive bullish, intact captured reference. | ITM1 CE: eligible, tighter spread within the same tier, lower default moneyness preference. |
| Expiry: target + 96 hours; exceeds provisional 72-hour minimum. | OTM1 CE: eligible, but in spread tier 1 rather than tier 0. |
| Spread: 90 bps, tier 0; qualified quote age: 10 seconds. | Shorter expiry: rejected because it ends before the target, not because its price is unattractive. |
| Meaning: preferred within the declared scope, not permission to buy. | Missing optional Greeks remain disclosed; they were not calculated to justify selection. |
:::

An explanation becomes misleading if it says “stronger liquidity” merely because the preferred candidate won. Chapter 10's ATM candidate can beat a tighter-spread ITM1 because of preference ordering. The prose must faithfully describe that result. Similarly, a horizon-rejected expiry should not be described as illiquid unless independent admitted facts support that claim.

The underlying evidence needs a visible path back to its source. A display can show a short evidence label and offer a detailed view of observation identity, timing qualification, source/adapter lineage and the relevant policy threshold. Provider provenance must survive normalization, while the downstream subject stays provider-neutral. A provider's brand, symbol suffix or confidence statement is not a substitute for field-specific evidence authority.

## A result is a record, not a persuasion attempt

The compact view should show disposition and its main reason before listing a candidate. A result with no preferred expression must not keep an old preferred card visually active. A candidate table should distinguish PASS, FAIL and UNKNOWN, and show eligible-but-not-selected rows separately from rejected rows. Alternatives are alternatives under this policy, not individually authorized trades.

The detailed view also needs an invalidation panel: thesis change or veto, expiry of evidence freshness, new material event, changed instrument/universe facts, or a different intended exit. These are reasons for a newly admitted assessment. They are not promises of a background alert service, and a user must not assume that silence means continuing validity.

> EXPLANATION TEST — Can the reader identify the fact, the rule and the comparison that caused the result? If the answer is only “the score was higher,” the proposed v1 explanation has not done its job.

# 12. When No Expression Is the Correct Answer

NO_OPTION_TRADE is a successful analytical outcome when a decisive prohibition or complete scoped facts show no suitable expression. It is not a euphemism for a software failure. A6 should be able to say that an admitted thesis remains supportable while the captured instruments fail the expression requirements. That separation gives the user information instead of pressuring the system to return something tradable-looking.

Not every absence is NO_OPTION_TRADE. Stale data does not prove that the expression is bad. An unsupported horizon does not prove that no financial instrument could express it. A known blocking event may call for waiting rather than a permanent judgment. These distinctions are especially important when a screen reduces several pages of evidence to one status badge.

:::flow 11 Absence decision path: preserve the reason
OPERATIONAL VALIDATION FAILS? → Operational error, not a market disposition.
↓ A2 / A4 PROHIBITION? → NO_OPTION_TRADE; preserve NO_TRADE / AVOID.
↓ REQUEST OUTSIDE V1? → UNSUPPORTED; no substituted strategy or horizon.
↓ A4 WAIT / CONFLICTED? → WAIT_FOR_EXPRESSION; preserve the original state.
↓ UPSTREAM ADMISSION INSUFFICIENT? → INSUFFICIENT_EVIDENCE, before event screening.
↓ KNOWN ADMITTED MATERIAL EVENT IN WINDOW? → WAIT_FOR_EXPRESSION.
↓ REQUIRED DERIVATIVES / COVERAGE UNKNOWN OR STALE? → INSUFFICIENT_EVIDENCE.
↓ COMPLETE FACTS, NONE ELIGIBLE? → NO_OPTION_TRADE; otherwise rank eligible candidates.
:::

Figure 11 follows the primary ordering in architecture section 5. Upstream insufficiency includes abstention, incomplete analysis, stale admission and unresolved direction. An event-clear request also needs qualified coverage. The detailed reason record preserves all inspected conditions; the coverage/rejection corner case in TF-05 remains for reconciliation rather than being resolved by this figure.

| Situation | Correct kind of answer | What the answer does not say |
| --- | --- | --- |
| Good thesis + all expiries too short | NO_OPTION_TRADE | The underlying thesis has become bearish. |
| Good thesis + current spreads above the hard limit | NO_OPTION_TRADE | The option can never become suitable later. |
| Good thesis + quote market time missing | INSUFFICIENT_EVIDENCE | Current liquidity is demonstrably poor. |
| Admitted material event tomorrow in the holding window | WAIT_FOR_EXPRESSION | A scheduler will automatically retry or trade afterward. |
| Request for a futures expression or a 120-day positional target | UNSUPPORTED | Futures or long-horizon investing are inherently unsuitable. |
| Weak/prohibited thesis + attractive-looking quote | Upstream gate prevents selection | Low premium can rescue A4 NO_TRADE. |

Waiting also needs discipline. A WAIT result must identify the known condition and the need for separately admitted successor evidence. It should not create an implied countdown to guaranteed availability. A future run can still return no trade or insufficient evidence after the original event or constraint changes.

For the product owner, these outputs are not all failures to convert a user into a trade. They are evidence-quality and suitability outcomes worth measuring independently. A higher selection rate could simply mean that required evidence was ignored. No implementation should optimize that metric at the expense of transparent refusal.

# 13. A5 Expression Refresh: A New Question, Not an Automatic Roll

An existing position changes the context but not A6's authority. TM supplies operational position truth. A5 interprets that supplied snapshot with an admitted current thesis and can emit EXPRESSION_REFRESH_REQUIRED. That intent means the expression should be reassessed; it does not specify the replacement contract or authorize closing the old one.

:::flow 12 The advisory refresh seam
TM / BROKER — Current operational position and authoritative observed state.
↓ A5 — Position advice includes EXPRESSION_REFRESH_REQUIRED, with reasons and lineage.
↓ GOVERNED CALLER — Separately admits current A4 thesis and fresh qualified derivatives evidence.
↓ A6 — Evaluates a successor expression request; may still return no trade, wait or insufficient.
↓ TM — Independently decides any position action; no automatic close, roll or replacement.
:::

A trader may hear “refresh required” as “roll into the next expiry.” The latter is an operational multi-action interpretation that the current seam does not grant. The existing position may require separate risk treatment, the fresh thesis may no longer be supportive, or no replacement expression may pass. Even if A6 returns a candidate, TM must decide whether doing anything with that candidate fits its account, risk and current-position constraints.

The old assessment is not overwritten. A successor carries references to the earlier position/advice and analysis, allowing a reviewer to see why a refresh was requested and what facts changed. A6 does not reconstruct the original broker state, and A5's current advice does not retroactively change the user's original entry rationale.

Future TI Monitoring may respond to expiry approach, chain changes, event updates or thesis changes by requesting another evaluation. That recurring runtime remains separately governed. A6 itself evaluates one point-in-time request and stops. A holding horizon does not set a polling interval, and a refresh intent is not evidence that a background job exists.

# 14. Replay and “Why Did TI Say This Then?”

Suppose a contract is preferred today and looks obviously poor a month later. The relevant audit question is not whether today's evidence would have selected it. It is whether the original result followed the original admitted evidence and policy, with the limitations that were actually known then. Replacing missing history with present-market data would answer a different question and conceal the original decision boundary.

:::flow 13 Replay lineage: reconstruct the old question
CAPTURE — Intent, explicit target/cutoff, A4 and parent identities, declared chain universe and timing qualification.
↓ PIN — Policy/profile, evaluator and normalization versions; exact input integrity.
↓ RECORD — Every bounded candidate, gate, rank key, preferred/alternative/rejected state and explanation.
↓ OFFLINE REPLAY — Read captured artifacts; no current provider lookup, model call or fresh market time.
↓ VERIFY / COMPARE — Reproduce exact pinned semantics, or report mismatch / unavailable pin; new policy creates a successor.
:::

Two forms of integrity matter. Exact byte checksums detect changes to persisted artifacts. Semantic fingerprints identify the meaningful request, evidence and result under a defined canonical projection. Formatting or transport latency should not become a market fact; observation and acquisition times are meaningful and cannot be replaced by replay time. A fingerprint is an integrity aid, not evidence that the original market observation was correct or complete.

Recorded replay reconstructs the saved analysis without running today's selection. Deterministic verification evaluates the saved inputs using the exact recorded implementation and policy pins. If a required version or local artifact is unavailable, verification must refuse explicitly rather than quietly selecting a newer rule. A comparison with a changed policy is a separately identified successor, not a repair of the old record.

This is useful even before any learned model exists. A user can ask whether a wider spread, a different horizon or a preference change caused a different result. A product owner can distinguish stricter evidence coverage from a changed ranking rule. Future A7 work can retain the deterministic baseline and compare against it rather than rewriting what the baseline “would have meant.”

Provenance survives through native observation, connector/adapter normalization and canonical TI evidence. Sharing captured evidence across assessments does not merge their intent, admission or analysis state. Two users may legitimately request different horizons from the same evidence and obtain different results. Neither gets permission to read the other's private artifacts merely because the underlying subject is the same.

> REPLAY LIMIT — Exact reproducibility proves what was computed from the preserved inputs. It does not prove profitable outcomes, source truth, sufficient coverage or permission to trade.

# 15. Interaction Surfaces and the Trader's Workspace

The same assessment should mean the same thing whether a trader uses a command, a form or a future language interface. Otherwise each surface becomes its own undocumented policy. The proposed common boundary is expression.assess through the governed facade; the surface translates intent and renders the returned canonical result.

The current repository does not publish expression.assess or an A6 Shell command. The examples here are mock interactions only. Even the structured command needs a logical artifact containing admitted upstream analysis and evidence; it does not obtain fresh authority or a thesis by parsing a symbol.

:::figure 14 Interaction mockups—future design, not runnable today
| Surface | Example | Boundary |
| --- | --- | --- |
| Plain English | “Find a bullish KAYNES expression for three weeks.” | Resolve intent; show exact duration interpretation; obtain admitted references. |
| Structured Shell / REPL | expression assess --request artifact:admitted-kaynes-expression-request | Same parser/facade semantics in both modes; no direct provider calls. |
| Convenience syntax, future | expression assess KAYNES --direction bullish --horizon 3w | Not sufficient alone; must resolve to the same fully admitted request. |
| Web form | Subject, direction constraint, target, preferences, evidence reference; “Review assessment” | No quantity/order button masquerading as A6 analysis. |
| Python / future API | Typed intent plus permitted expression_request_ref | No private provider/router handles, raw paths or policy objects. |
:::

## A useful results workspace

The primary panel should start with disposition, cutoff and limitation. Below it, the preferred card exists only for EXPRESSION_AVAILABLE. A candidate comparison can then show eligibility, the first decisive ranking key, evidence references and rejected or unknown reasons. Explain, trace and replay should expose the same underlying record, not generate a second opinion while rendering.

| Candidate | Gate state | Rank meaning | User-visible next step |
| --- | --- | --- | --- |
| Synthetic ATM CE | PASS | Preferred under recorded policy | Inspect rationale; TM still decides action. |
| Synthetic ITM1 CE | PASS | Eligible alternative | Compare actual decisive ranking difference. |
| Synthetic near-expiry CE | FAIL | Rejected on horizon fit | Inspect target and sourced expiry timing. |
| Synthetic missing-quote slot | UNKNOWN | No supported ranking conclusion | Inspect evidence gap; do not hide the row. |

This table is a UI vocabulary illustration, not a single available-result fixture: under the draft's complete-window rule, a required UNKNOWN slot can withhold the preferred result. Keeping that distinction visible prevents the mockup from silently creating a partial-ranking feature.

TI's workspace contains evidence and analysis. TM's workspace contains operational permissions, positions, risk/capital and execution decisions. A future multi-console cockpit can link them with visible ownership labels, but a common screen does not grant a common authority. Selecting “inspect expression” should never be treated as selecting “place order.”

## Language confirmation needs its own design

Some ambiguity is harmless presentation; other ambiguity changes the analytical question. Calendar versus trading days, a premium cap versus cheapest-first ranking, and “refresh” versus “roll” belong to the second category. TF-06, TF-08 and TF-09 record the need for explicit interpretation and confirmation rules. These proposed safeguards do not claim that an NLP implementation exists or that confirmation is an execution approval.

# 16. What A6 Cannot Know or Decide

The proposed engine has a precise source of strength: its facts, constraints and ordering can be exposed. Its corresponding limitation is that it cannot infer facts outside its admitted evidence merely because the user needs a decision. A large chain does not establish complete event coverage. A provider's last acquisition time does not establish market recency. A declared symbol does not establish current contract eligibility. The correct response must preserve those boundaries.

| Constraint / failure mode | Honest consequence | Shortcut to avoid |
| --- | --- | --- |
| Date-only expiry or unqualified quote time | Required timing may be unknown; selection withheld. | Inventing an exchange close or relabeling receipt time. |
| Incomplete selected window | Cannot claim complete comparison under the draft. | Dropping an unavailable rival from the denominator. |
| Sparse stock-option quotes or ambiguous units | Show actual FAIL/UNKNOWN basis, not a universal liquidity score. | Treating OI or LTP as a replacement for current bid/ask evidence. |
| Missing Greeks or IV conventions | Context remains absent/ambiguous. | Deriving a plausible-looking number without an admitted model. |
| Material event uncertainty | Disclose scope and qualification; apply only supported rules. | Guessing event sentiment, importance or time. |
| Changed account/position state | TM checks current authority and risk. | A6 chooses quantity from a per-unit premium cap. |
| Corrupt artifact or denied access | Operational failure, not market advice. | Returning NO_OPTION_TRADE as a generic error message. |

The 60-second quote gate, 15-minute DAY and 24-hour POSITIONAL upstream-age limits, 24/72-hour expiry cushions, 90-day positional bound and spread tiers are provisional engineering values. They are neither backtested optimums nor provider promises. They make the draft inspectable, but they still need thesis/architecture reconciliation and acceptance. An illustrative example that passes them is not validation of their economic suitability.

Keeping A6 advisory is a structural safeguard, not merely a disclaimer at the bottom of an order screen. A6 does not decide account allocation, quantity, margin optimization, stops or targets, routing, order types, broker changes or current operational position truth. Nor does it run hidden live research or consume an unrecorded A7 forecast. Future functionality must pass its own source, contract, authority and evaluation gates.

The user should therefore read EXPRESSION_AVAILABLE as a supported analytical comparison with stated limits. It is not “all relevant risks were measured.” A6 can be confident about applying a deterministic rule to admitted inputs while remaining explicitly uncertain about missing market facts and future outcomes. That distinction is more informative than a single confidence percentage.

# 17. Eight Worked Scenarios and Controlled Variants

Every case below is an **illustrative example—not live advice**. Dates, prices, depth, eligibility, listing and timing qualifications are synthetic fixture assumptions, not observed Dhan or exchange facts. Numerical examples explain the proposed policy; they do not tune it. Unless explicitly changed, cases use complete required evidence, no A2 veto, admitted supportive A4 analysis and default ATM → ITM1 → OTM1 preference. Missing optional Greeks remain disclosed. The scope is the stated capture, never the whole market.

## Case 1 — Bullish KAYNES, three-week positional CE

The user asks for a bullish expression lasting three calendar weeks. The fixture supplies a complete supportive A4 result, a supported primary thesis and positive admitted direction. The as-of is 2026-09-14T10:00:00+05:30; the intended exit is 2026-10-05T10:00:00+05:30. Upstream evidence is five minutes old, qualified market quotes and spot are ten seconds old, and the synthetic underlying reference is 4,000.

Two declared expiries provide six candidate slots. E-S ends at 2026-10-04T10:00:00+05:30, before the target. E-L ends at 2026-10-09T10:00:00+05:30, 96 hours after it. These exact instants are supplied fictional timing facts, not inferred exchange schedules. E-S has complete otherwise-valid quotes, so its failure is known rather than an evidence gap. For E-L, both top quantities are positive in every row.

| E-L candidate | Bid / ask, synthetic INR per unit | Spread | Gate / rank result |
| --- | --- | --- | --- |
| 4,000 CE, ATM | 99.55 / 100.45 | 90 bps, tier 0 | Eligible, preference 0: preferred. |
| 3,900 CE, ITM1 | 199.30 / 200.70 | 70 bps, tier 0 | Eligible, preference 1: first alternative. |
| 4,100 CE, OTM1 | 49.55 / 50.45 | 180 bps, tier 1 | Eligible: second alternative. |

The surviving candidates are the three E-L calls. The expiry has 24 hours of cushion excess above the 72-hour minimum. ATM wins within tier 0 because its moneyness preference comes before exact spread. The output is EXPRESSION_AVAILABLE, not an instruction to buy. The three E-S calls are rejected for horizon mismatch, while the two lower-ranked E-L calls are eligible alternatives rather than failures.

Uncertainty remains: optional Greeks and complete event coverage are not asserted. The fixture has no known admitted blocking event and does not request event-clear screening, so that unknown coverage is a visible limitation rather than a made-up “no events” finding. Changed thesis, new material event, changed target or stale/widened quotes invalidate reliance on the old result. TM still checks account authority, current instrument availability, quotes, capital, risk, quantity and operational state.

> CASE 1 LESSON — A6 can prefer ATM even when ITM1 has a tighter spread. The declared ranking explains why; the result must not invent a liquidity advantage for ATM.

## Case 2 — Bearish index, DAY-horizon PE

The user requests a bearish intraday index expression. The synthetic subject label is NIFTY, with complete supportive A4 analysis and negative admitted direction. The target is 14:30 on the as-of day, from an assessment at 10:00. A separately supplied fictional session interval of 09:00–16:00 contains both instants; it is a test interval, not a claim about NSE hours. Expiration is exactly 48 hours after the target, meeting the draft's 24-hour DAY cushion.

The qualified spot is 24,000. The declared single expiry contains ATM PE at 24,000, ITM1 PE at 24,100 and OTM1 PE at 23,900. ATM quotes 99.60/100.40 (80 bps), ITM1 199.10/200.90 (90 bps), and OTM1 49.55/50.45 (180 bps). All required timing, identity and positive top-depth facts are supplied; quotes are ten seconds old and upstream evidence five minutes old. There is no known admitted blocking event.

All three puts survive. ATM and ITM1 share tier 0; ATM wins default preference. OTM1 is tier 1. The result is EXPRESSION_AVAILABLE with ATM preferred and the other two eligible alternatives. There are no hard-rejected candidates in this declared universe. The direction mapping selects puts without inventing an expected return or claiming that the option price must rise.

Optional Greeks and broad event coverage remain limitations. A new thesis, event, target or quote state requires a new record. TM still determines whether any position is permitted and how to act; the DAY label does not authorize zero-day expiry, immediate entry or a particular order type. This case illustrates an expiry extending beyond the DAY target, not a policy for holding until expiry.

## Case 3 — Strong thesis, no expiry that fits

Keep Case 1's user intent, supportive A4 thesis, three-week target, qualified spot, quotes and depth. Change only the declared capture: it now contains E-S and no E-L, with exclusions and complete scoped coverage recorded. The candidate universe is E-S ATM/ITM1/OTM1 calls. All three expire before the intended exit; there is no unknown timestamp or missing rival in this fixture.

The hard horizon gate fails for each candidate. None survives, so no ranking or preferred/alternative output is supported. The disposition is NO_OPTION_TRADE with horizon-mismatch reasons for all three. Their otherwise acceptable spreads do not compensate for an instrument that ends before the stated target. This is not a promise that no suitable option exists outside the declared scope.

The remaining uncertainty concerns future conditions and omitted scope, not the demonstrated timing failure. A new qualified expiry capture or a legitimately changed and re-admitted target could change the result; shortening the target solely to obtain a selection would ask a different question. TM receives no preferred contract from this assessment and must not translate the refusal into a near-expiry order.

## Case 4 — Strong thesis, demonstrably poor current liquidity

Keep Case 1's bullish thesis and three-week target, but declare only E-L. Required identities, timing, spot and top quantities are known. The three selected calls have synthetic quotes: ATM 96.5/103.5, ITM1 192/208, and OTM1 47.75/52.25. Their spreads are respectively 700, 800 and 900 bps; all observations are ten seconds old. No other blocking event or missing gate is introduced.

Each exceeds the 500-bps hard limit. None survives, ranking is not performed, and no preferred or alternative expression is returned. The result is NO_OPTION_TRADE with spread-too-wide reasons. In a separate controlled variant, a known zero top quantity can cause the depth gate to fail even if the spread narrows. A missing quantity would instead be unknown evidence, not a factual zero.

The decision is limited to the captured state and universe. It does not declare permanent illiquidity, a bearish underlying thesis or a forecast of actual slippage. A later qualified narrower-spread capture would require a new assessment. TM still owns any action; it must not infer that A6 has approved an aggressive order simply because the chart remains attractive.

## Case 5 — A fresh receipt carrying stale or unknown market facts

Keep Case 1's intent, admitted thesis, target and complete E-L geometry. Quotes now have qualified market observation times 180 seconds before as-of, despite being acquired five seconds before it. The selected universe is still the three E-L calls with otherwise acceptable numeric quotes. An alternate version removes market observation time entirely while retaining acquisition time.

In the first version, the required 60-second freshness gate cannot support current suitability. In the alternate version, quote age cannot be established. Both produce INSUFFICIENT_EVIDENCE with different reasons: stale qualified time versus unqualified market time. There is no preferred expression; apparently passing numerical rows are not promoted into a supported shortlist. A6 must not “refresh” them by substituting acquisition time.

The missing conclusion is whether those contracts are currently suitable—not whether they are permanently bad. Qualified successor facts may resolve the gap, but the evaluator itself performs no live fetch. New data, changed thesis or target creates a separately admitted run. TM receives no current expression recommendation and cannot treat yesterday's or an unqualified quote as authorized present execution evidence.

## Case 6 — Multiple valid contracts and a preference change

Use Case 1's E-L-only universe, same supportive bullish thesis, explicit three-week target and complete fresh evidence. The surviving set is ATM at 90 bps, ITM1 at 70 bps and OTM1 at 180 bps, all with valid horizon and depth. No candidate is hard-rejected. Default ranking is ATM first, ITM1 second and OTM1 third; EXPRESSION_AVAILABLE names ATM.

Now change only the permitted moneyness order to ITM1 → ATM → OTM1. Because ATM and ITM1 share tier 0 and expiry, ITM1 becomes preferred. This is a new request/result identity, not a correction to the earlier record. Both explanations should remain replayable, showing that preference—not a change in market facts—caused the change.

A separate tier variant changes only ATM's bid/ask to 99.495/100.505, or 101 bps at midpoint 100. It moves to tier 1, so ITM1's tier 0 wins even under default preference. This intentionally exposes the provisional tier boundary, without claiming that a small spread change produces a measured discontinuity in expected returns. TF-04 calls for reviewing this user-visible consequence.

Optional context remains uncertain as in Case 1; changed evidence, target or upstream state invalidates the old conclusion. Lower-ranked eligible contracts are alternatives, not failures. TM must independently assess any action; a preference reversal does not grant authority to replace an existing position or change its quantity.

## Case 7 — A4 NO_TRADE blocks an attractive-looking chain

The user still requests a bullish three-week KAYNES call comparison, and the fixture supplies Case 1's complete, fresh E-L universe. Change only the upstream result to A4 NO_TRADE, with its reasons and parent fingerprints intact. The request's desired direction cannot create a surviving supportive thesis.

The upstream prohibition short-circuits selection. There is no admitted eligible candidate set, no ranking and no preferred or alternative expression. The result is NO_OPTION_TRADE with the upstream-veto reason; it must not mislabel the three quotes as individually illiquid or horizon-incompatible. They were not the decisive basis for refusal.

The result preserves what is known: the current admitted TI path prohibits proceeding. A separately admitted successor A4 result might change that state, but A6 cannot rerun A4 to obtain it. Uncertainty about future evidence remains; a cheaper premium or better spread is not a remedy. TM must not relabel this opinion as a TI outage or silently invoke TI_OPTIONAL to bypass the prohibition.

## Case 8 — Existing position and advisory refresh

The user asks what to do after A5 emits EXPRESSION_REFRESH_REQUIRED for a supplied existing option position. TM owns that position snapshot and operational truth. The initial request references the old bullish three-week analysis and its old E-L chain, now outside freshness limits. A5's refresh intent provides lineage, not a new supportive thesis or fresh quote evidence.

The declared old ATM/ITM1/OTM1 universe cannot support a current selection. Required freshness/admission evidence is insufficient, so no candidates are promoted, no ranking runs and no preferred result is supplied. INSUFFICIENT_EVIDENCE does not mean “roll anyway”; no contract is asserted as a viable replacement.

For a second, separately admitted synthetic run, suppose the caller supplies current compatible A4 analysis, an explicit remaining target and a fully qualified chain with three eligible calls. If the gates and ranking match Case 1, that successor can prefer ATM. The old result and A5 refresh reason remain linked rather than overwritten. Missing optional context, new events, changed quotes and thesis invalidations are still explicit.

TM must now decide whether any operation is appropriate for the actual current position. Closing an old leg, opening a new one, choosing quantity and sequencing actions are not A6 outputs. A suitable successor expression can coexist with TM deciding to do nothing. A5 advice, A6 assessment and TM action remain separate records.

## Sensitivity matrix: one changed input, one explainable consequence

:::figure 15 Controlled variants of Case 1—illustrative, not live advice
| Change, with new admission where needed | Expected draft outcome | Why |
| --- | --- | --- |
| Target extends from 21 to 28 calendar days; original E-L retained | NO_OPTION_TRADE if all declared expiries now fail | Holding intent changed; original expiry is not silently extended. |
| Keep target; capture only the shorter E-S expiry | NO_OPTION_TRADE | Complete facts prove horizon mismatch. |
| ATM widens to 101 bps; ITM1 stays 70 bps | ITM1 preferred if all else passes | Spread tier outranks default moneyness preference. |
| Required market observations age to 180 seconds | INSUFFICIENT_EVIDENCE | Numeric attractiveness cannot cure stale facts. |
| Admitted material earnings event tomorrow, inside holding window | WAIT_FOR_EXPRESSION | Known event block; no forecast of event direction. |
| User says “cheapest,” without a supported preference/cap | No new ranking rule implied | Clarify intent; draft does not rank directly by premium. |
| User explicitly sets INR 60 per-unit cap | OTM1 can be the sole eligible candidate if every other gate passes | ATM and ITM1 asks exceed the cap; this is not account sizing. |
:::

The cap variant does not contradict the default preference: hard restrictions are applied before ranking. All expected slots still have complete evidence, and known cap failures are recorded. Under an event-clear request, a separate variant with unknown event coverage yields insufficient evidence rather than event-safe selection. Each variant preserves the original assessment; it does not mutate history until a desired contract wins.

# 18. Future Evolution Without Losing the Baseline

A6's first deterministic version is intended to be a control, not the final expression intelligence product. Better evidence, richer permitted strategies and calibrated future-outcome information may make later assessments more useful. They should improve the system through visible new capabilities and policy versions, not by quietly changing the meaning of an old result.

:::figure 16 Evolution map: separate gates, not automatic scope expansion
| Foundation under review | Separately accepted future improvement | Boundary that survives |
| --- | --- | --- |
| Deterministic long single-leg A6 | Admitted A7 forecast/evaluation overlay | Preserve baseline result; do not forecast an invalid candidate into eligibility. |
| Qualified captured evidence | Better timing, event and derivative coverage | Preserve source semantics and unknowns; no invented authority. |
| Narrow supported neighborhood | Multi-leg or broader instrument expression | New contracts and combined-risk/execution boundaries require review. |
| Local captured facade / Shell design | Plain English, Web, remote API or Cockpit | Same typed meaning and permission checks; no execution authority transfer. |
| Point-in-time evaluation | Future governed TI Monitoring | Each successor run independently admitted; A6 is not the scheduler. |
:::

A7 may later contribute calibrated outcome distributions or evaluation evidence. Those possibilities are not existing A6 inputs that the handbook can assume, and an option's premium or delta cannot be substituted for them. A later overlay should demonstrate what it adds compared with the deterministic control, retain uncertainty, and use separately accepted policy. Better-looking historical examples alone would not establish better future decisions.

Improved source coverage may matter before more sophisticated scoring. A source that can support meaningful market observation times and exact expiry timing addresses a requirement the current strict design cannot infer from existing Dhan fields. Better event qualification may reduce uncertainty about material events. Neither is declared implemented by listing it in a roadmap.

## Pluggability is a discipline the user can observe

:::figure 17 R1–R5 translated into user-visible promises
| Foundation | What the user should experience |
| --- | --- |
| R1: required scope | Missing evidence remains visible; requirements are not quietly removed. |
| R2: honest discovery | A listed future capability is not advertised as currently callable or authorized. |
| R3: exact pins | Old results retain the versions needed to explain or verify them. |
| R4: adapter isolation | Provider choice does not redefine the specialist/domain contract. |
| R5: trusted COLD ownership | Reviewed startup policy selection is separate from request preferences and permission. |
:::

Sector Rotation and Signal Qualification may supply earlier admitted context after their own acceptance, but should not create a cycle in which A6 calls a layer that calls A6 to justify the same result. Shared evidence can be reused while each request's intent, scope, policy and analysis state remain distinct. Future TM/scanner integration and operational monitoring keep their separately owned milestones.

Zero A6 model calls and cost are intended properties of the deterministic evaluator, not a claim that acquiring all upstream evidence is free. The record must preserve upstream usage rather than erase it. Nor is the existence of a policy descriptor proof that the capability is ready, permitted or executing. The user benefits when the system makes these limitations visible before, rather than after, an invocation.

# 19. Questions Traders and Product Owners Should Ask

## Why not simply buy ATM every time?

ATM is a geometric starting point and a default preference, not a substitute for admission, expiry fit or current evidence. An ATM contract can fail on spread, depth, freshness or horizon while another supported candidate passes. Even among eligible candidates, the spread tier is compared before moneyness preference. Buying ATM unconditionally would discard the expression question rather than answer it.

## Why not always buy the cheaper OTM option?

“Cheaper” needs a defined meaning: lower ask per unit is not proof of equal exposure, affordability or a higher-quality expression. The draft permits a per-unit cap but does not rank directly by premium or estimate a probability from it. A trader can inspect an OTM candidate's facts and restrictions without A6 inventing an economic-value score. Case 1 and its cap variant illustrate that distinction.

## Why not always choose the nearest expiry?

The nearest expiry may end before the user's target or fail the required residual-life cushion. Its liquidity does not change that timing fact. The draft considers smaller cushion excess only after hard gates and earlier ranking criteria. A near-expiry preference cannot rewrite the horizon or bypass the requirement for a sourced expiration instant.

## Why can a further expiry sometimes be better?

For this architecture, the clearest reason is structural fit: an expiry further away may be the first declared one that remains alive sufficiently beyond the intended exit. That does not make the furthest expiry universally preferable. Eligible candidates still follow the declared ranking, and no premium-value or forecast advantage is inferred simply from additional time. Chapter 6 distinguishes the design constraint from general options economics.

## Why does liquidity matter if I intend to hold?

An intended holding period does not supply execution evidence. The contract must first be accessed under current conditions, and the actual position may later need action for reasons the initial assessment cannot settle. A6's top-book/spread checks establish only bounded captured facts. They do not guarantee depth for TM's eventual quantity or a usable exit market throughout the holding period.

## Why does spread matter?

Spread distinguishes a displayed buying side from a displayed selling side, rather than pretending the last trade is the only relevant price. The draft uses a relative spread gate and tier so that the comparison is inspectable across premiums. The measure is still limited: passing it is not a fill guarantee, and a tier does not quantify expected slippage. The calculation and example are in Chapter 8.

## Why can TI refuse when the chart looks excellent?

The chart contributes to an underlying thesis; it does not supply qualified option quotes, suitable expiries or account permission. A4 may admit the thesis while A6 finds no supported expression. Alternatively, A4 itself may retain a prohibition or unresolved state despite one attractive chart feature. A6 must preserve that conclusion rather than choose a contract to make the output look more decisive.

## Why does A6 need fresh option-chain data?

The question is about a particular cutoff, not an old market remembered by the application. Qualified timing is necessary to judge whether the captured quote and underlying reference meet the proposed recency policy. Recent acquisition alone does not establish recent market observation. Without that distinction the engine could present an old spread and old strike geometry as a current comparison.

## Why does A6 not decide quantity?

Quantity requires account, capital, risk and current-position context owned by TM. The A6 request's premium cap is per unit; it is not permission to spend the corresponding amount multiplied by an inferred lot count. Keeping sizing out of the result also makes the same analytical evidence reusable without falsely treating two accounts as operationally identical.

## Why can A6 not directly place an order?

The preferred candidate is analytical advice at a recorded cutoff. Permissions, current quotes, live availability and operational position state must still be checked where action authority resides. TM creates its own execution intent if allowed; broker order/fill truth then establishes what happened. Adding an order call to the evaluator would collapse this ownership chain and make replay of analysis entangled with action.

## Why WAIT instead of NO_OPTION_TRADE?

WAIT describes a known constraint such as upstream waiting/conflict or an admitted material event, not an assurance that an expression will become available. NO_OPTION_TRADE describes a decisive prohibition or complete scoped facts showing none suitable. The distinction preserves the reason for absence. A future evaluation needs new admission in either case; WAIT does not create a retry job or an order scheduled for later.

## What does INSUFFICIENT_EVIDENCE mean?

It means a required conclusion cannot be supported from the supplied facts at the cutoff. That can reflect missing time qualification, stale quotes, incomplete selected slots or incomplete upstream admission. It does not establish that the underlying is bad or that every option is illiquid. The useful next question is which specific evidence is missing, not which optimistic number could replace it.

## What if two contracts look almost equally good?

“Almost” is a display impression; the recorded ranking uses exact defined comparisons. Spread tier, moneyness preference, cushion excess, exact spread and neutral contract identity settle the order. Rounded labels cannot silently determine a tie. The alternative remains visible, and the explanation should identify the first unequal key without claiming a large economic advantage that the policy never measured.

## What if conditions change after assessment?

The old result stays an accurate record of its old inputs, not an evergreen recommendation. Changed quotes, events, thesis, timing fit or target can require a successor assessment and action-time TM validation. A6 does not monitor silently in the background. If a later monitoring capability is adopted, its cadence, authority and budget must be explicit and separate from the analytical horizon.

## How does replay help with an old decision?

Replay lets the user inspect the original question, evidence, scope, policy and reasons without substituting today's market. Exact-pin verification can check whether the original computation is reproducible; missing artifacts or versions are explicit failures. It cannot prove that the original evidence was true or the result profitable. That limitation makes replay a disciplined audit tool rather than a retrospective justification machine.

## Will A7 change how A6 chooses contracts?

Possibly, through a separately accepted forecast-informed policy or comparison that records its evidence and keeps the deterministic control visible. A7 is not required by v1 and does not already supply probabilities here. Any later enhancement must preserve hard validity constraints, be evaluated appropriately and create a new identifiable result rather than rewrite the baseline's historical answer.

## Why are multi-leg strategies deferred?

The first baseline tests bounded single-contract suitability. Combining legs introduces relationships and operational implications that this contract does not model. A broader strategy engine needs its own accepted structure, evidence, risk assumptions and handoff semantics. Deferring it avoids claiming that a collection of acceptable legs automatically forms an acceptable combined expression or an executable plan.

## Why is SigmaDSL not used here?

The bounded A6 policy can be expressed with native typed contracts and deterministic rules. A parser/compiler/runtime and compatibility layer would be a separate commitment, not a requirement for explaining this selection. A future SigmaTrader-style programmable product may have different needs. Shared principles such as replay do not make that product a prerequisite for TI's initial A6 capability.

# 20. Thesis Findings for Architecture Reconciliation

The examples reveal design questions; they do not authorize solutions. The findings below are a review agenda against the current A6 architecture. NO_CHANGE retains a decision; CLARIFICATION_NEEDED asks for precise meaning; ARCHITECTURE_CHANGE_PROPOSED identifies a possible semantic revision requiring acceptance; IMPLEMENTATION_DETAIL_ONLY belongs to delivery; DEFER keeps separate future scope out of v1.

## Timing and feasibility

**THESIS_FINDING TF-01 — CLARIFICATION_NEEDED: market-time feasibility.** Strict qualified market time is required by the draft, while current Dhan chain evidence can be acquisition-only. Clarify the source/capture path that could satisfy the requirement and how the product presents inability to qualify it. The handbook keeps INSUFFICIENT_EVIDENCE as the result for that gap; it does not approve an acquisition-qualified replacement policy. Architecture sections 6.3 and 13 own the resolution.

**THESIS_FINDING TF-02 — CLARIFICATION_NEEDED: date-only expiry.** A date cannot prove the exact residual life in the worked timeline. Specify the provenance and representation of the required expiration instant and DAY session facts, including what happens when they are unavailable. No assumed exchange cutoff or calendar implementation is introduced here. This is distinct from merely converting a known instant to Asia/Kolkata.

**THESIS_FINDING TF-03 — CLARIFICATION_NEEDED: provisional age and life limits.** The 60-second quote gate, 15-minute/24-hour upstream-age limits, 24/72-hour cushions and 90-day positional bound are transparent but not calibrated safety guarantees. Reconciliation should explicitly accept or revise their engineering purpose and explain their operational consequences. The handbook proposes no symbol-specific values and does not make live pass rates an acceptance target.

## Ranking and coverage

**THESIS_FINDING TF-04 — CLARIFICATION_NEEDED: spread-tier discontinuity.** Moving from 100 to 101 bps can change the preferred candidate because tier precedes preference. Confirm that this user-visible ordering is intended and require the explanation to name the actual decisive key. Do not describe a small threshold crossing as a measured discontinuity in profitability. No changed tier value is proposed by the handbook.

**THESIS_FINDING TF-05 — ARCHITECTURE_CHANGE_PROPOSED: unknown fields after a decisive rejection.** The draft requires complete hard-gate evidence across selected slots. A contract already conclusively excluded by an immutable horizon failure might still have a missing quote, potentially withholding a valid different-expiry candidate. Consider permitting proved-ineligible candidates to stop further gate collection while preserving their rejection and the required coverage of possible survivors. This would relax the current completeness rule and requires explicit design, precedence and replay tests. No such exception is applied in the worked examples or adopted here.

**THESIS_FINDING TF-07 — NO_CHANGE: one preferred plus two alternatives.** The bound is understandable when all evaluations remain inspectable. Keep eligible-but-not-selected separate from rejected; do not expand the canonical output into an unbounded chain dump. A compact shortlist does not establish a globally optimal search.

## User intent and contextual evidence

**THESIS_FINDING TF-06 — CLARIFICATION_NEEDED: duration-entry UX.** Decide how calendar-day expansion is shown and confirmed, how session-based requests are refused or resolved, and how the interpretation is recorded. A language model or form must not silently shorten the target to an available expiry. The same compatible upstream horizon is required regardless of interface.

**THESIS_FINDING TF-08 — CLARIFICATION_NEEDED: cheaper-premium intent.** A cap is a supported hard restriction; cheapest-first ranking is not in the draft. Specify how interfaces explain or decline the latter request rather than translating it into OTM preference without confirmation. A future premium-ranking criterion would be a separate architecture/policy change, not a rendering choice.

**THESIS_FINDING TF-09 — CLARIFICATION_NEEDED: plain-English confirmation.** Confirm which ambiguous fields require explicit user resolution and preserve the interpreted request. Intent confirmation is not execution consent. Language interaction remains future scope; the shared typed capability should not depend on a conversational implementation.

**THESIS_FINDING TF-10 — CLARIFICATION_NEEDED: event materiality and coverage.** Clarify the admitted source of materiality, the interval over which event-clear coverage is claimed, and the treatment of uncertain event timing. A known material in-window event still yields WAIT; unknown coverage is not absence. A6 cannot invent classifications to fill these gaps.

## Representation and delivery

**THESIS_FINDING TF-11 — CLARIFICATION_NEEDED: empty fitting universe.** The draft refers both to one-to-three declared chains and to a complete empty horizon-fitting scope. Clarify how an empty-but-complete expiry result is represented without becoming a malformed request. An unavailable expiry list remains insufficient; a proved absence can support no trade. The examples avoid the unresolved empty-container case.

**THESIS_FINDING TF-12 — IMPLEMENTATION_DETAIL_ONLY: readable exact comparisons.** Render rounded spread values for convenience while retaining exact comparison values, clear thresholds and the decisive key in detailed explanation. Provide a reliable missing/unknown visual state and accessible table labels. Formatting must not alter fingerprints or policy decisions.

**THESIS_FINDING TF-13 — CLARIFICATION_NEEDED: nearest-listed ATM terminology.** When spot lies between listed strikes, the nearest strike may technically be in or out of the money while the draft calls it the ATM anchor. Explain the geometric neighborhood label separately from economic moneyness and do not infer an exact delta. No strike-selection change is made in this thesis.

**THESIS_FINDING TF-14 — DEFER: broader intelligence and interaction.** Multi-leg/short/futures optimization, A7 forecast overlays, rich NLP/Web/Cockpit and recurring monitoring remain separate accepted-delivery questions. None is silently added to v1 to make a worked scenario more convenient. SigmaDSL remains outside A6 rather than a deferred v1 prerequisite.

## Reconciliation decision boundary

There are fourteen findings: ten CLARIFICATION_NEEDED, one ARCHITECTURE_CHANGE_PROPOSED, one NO_CHANGE, one IMPLEMENTATION_DETAIL_ONLY and one DEFER. The proposed coverage relaxation is the only specific semantic change suggested here; it is not accepted. Timing-source feasibility remains a major implementation gate even though it does not prevent a faithful user-facing thesis from being completed.

The next step is **TIAF A6 — THESIS / ARCHITECTURE RECONCILIATION PASS**. A6 architecture remains draft; the thesis is created; runtime remains NOT_IMPLEMENTED. Only after reconciliation and explicit architecture acceptance may A6.1 begin. No part of this handbook freezes the provisional policy, changes A5, begins A7 or grants trading authority.

# Appendix A. Source Guide, Glossary and Reading Map

## Repository sources—the controlling design basis

The primary sources are `docs/TIAF_A6_TRADE_EXPRESSION_INTELLIGENCE_ARCHITECTURE.md`, `docs/TIAF_A6_DETAILED_ROADMAP.md` and `docs/TIAF_A6_RECONCILIATION_RECORD.md`. They define draft meaning, the future implementation gates and the historical reconciliation. The companion Markdown thesis record contains clickable repository links and identifies the source snapshot. This handbook paraphrases their user implications; it does not publish new runtime contracts.

Supporting architecture sources used are the A4 Challenge/Arbitration Architecture; A5 Position Intelligence Architecture; Trading Ecosystem Architecture; TI Shell Architecture; Monitoring Architecture; Deployment Architecture; TI Pluggability Architecture; Source Authority/Provenance/Contradiction Architecture; System Architecture; and the Capability Map and architecture navigation. These distinguish analytical meaning, source competence, invocation authority and operational ownership. The R1–R5 integration treatment follows the reconciled A6 obligations and accepted foundation, not a new plugin framework.

The source snapshot is the post-R5 A6 draft prepared on 2026-09-13. This edition intentionally does not update that architecture to settle the findings. It contains no live chain capture, credential, account detail, broker response, generated forecast or verified listing. Mock commands and UI cards are prospective design illustrations, not available product endpoints.

## Educational references—background, not NSE rules or A6 policy

The following Options Industry Council / OCC educational pages were consulted for basic option economics. They discuss their own market context; they are not authority for current NSE listing, expiry cutoffs, settlement, permissions or TIAF thresholds. No external passage supplies the draft's numeric engineering policy, and no live price was fetched. Their relevant discussion is cited next to the educational explanation in Chapters 6–9.

- [Options Pricing](https://www.optionseducation.org/optionsoverview/options-pricing): intrinsic/time value and basic moneyness.
- [Options Delta](https://www.optionseducation.org/advancedconcepts/delta): conditional local sensitivity, not an A6 probability.
- [Time Erosion vs. Delta Effect](https://www.optionseducation.org/optionsoverview/leaps-time-erosion-versus-delta-effect): qualitative time/sensitivity trade-off.
- [Understanding the Bid and Ask Prices for Options](https://www.optionseducation.org/news/understanding-the-bid-and-ask-prices-for-options): displayed market context.
- [Option Price Behavior](https://www.optionseducation.org/referencelibrary/faq/option-price-behavior): why underlying direction alone does not determine option-price behavior.

## Working glossary

| Term | Meaning in this handbook |
| --- | --- |
| Admitted thesis | Verified upstream analysis satisfying the required A4/parent boundaries; not a caller's desired direction. |
| Expression | Analytical contract choice for a thesis; non-executable and distinct from TM's execution intent. |
| CE / PE | Call / put side in the supported single-leg option vocabulary; not a quantity or order. |
| ATM / ITM1 / OTM1 | Draft nearest-listed anchor and one-step neighborhood labels, with side-specific direction. |
| Basis point (bps) | One hundredth of a percentage point; 100 bps is 1%. |
| Cutoff / as-of | The instant whose admitted information defines the question, not the later rendering time. |
| Expiry cushion | Required residual life after the intended exit; a policy constraint, not an economic forecast. |
| PASS / FAIL / UNKNOWN | Gate met, known gate failure, or evidence unable to establish the gate. |
| Scope / coverage | The declared universe and what is known or absent within it; not an assertion about all markets. |
| Lexicographic ranking | Ordered comparisons; the first unequal key determines the relative order. |
| Semantic fingerprint | Integrity identity for meaningful captured input/result under its defined projection. |
| COLD selection | Trusted pre-start composition choice, separate from request preference and permission. |
| Successor run | A newly admitted record linked to earlier analysis, not a rewrite of it. |

## Reader self-check

Before relying on an expression assessment, the reader should be able to identify the admitted thesis and horizon, the captured scope and cutoff, why the preferred candidate passed, why its alternatives lost, which facts remain uncertain, and who still owns the next decision. If any of those answers is hidden behind a green badge or a persuasive paragraph, request the evidence-linked explanation rather than assume that more intelligence has been established than the record supports.
