# A3.6.2 Deep Research Live Acceptance Study

## Result

**Decision:** `READY_TO_ACCEPT_A3_6_2`

**Final run:** 2026-09-10T12:55:55.444215+05:30

**Command:** `.venv/bin/python scripts/deep_research_live_acceptance.py --live`

**Live calls:** 12, read-only

**Model usage:** 0 calls, 0 input tokens, 0 output tokens

The final bounded run reached Tapetide MCP 1.0.0, Yahoo Finance MCP 4.0.3,
and the configured Reliance company-IR route. No secret was printed or written.

## Scenario results

| Symbol | Capabilities | Providers | Calls | Canonical facts | Gaps | Graph edges | Confirmation | Replay |
|---|---|---|---:|---:|---:|---:|---|---|
| RELIANCE | profile, financials | Yahoo, Tapetide, company IR | 4 | 29 | 124 | 2 | `NOT_FOUND` | exact |
| HDFCBANK | profile, financials | Yahoo, Tapetide | 3 | 29 | 116 | 2 | not requested | exact |
| KAYNES | profile, filings | Yahoo, Tapetide | 2 | 8 | 49 | 2 | not requested | exact |
| ATHERENERG | profile, financials | Yahoo, Tapetide | 3 | 23 | 123 | 2 | not requested | exact |

The large gap counts are intentional and mostly reflect conservative
per-field `AMBIGUOUS`/`PROVIDER_DEFINED` normalization records. They are not
collapsed into facts or hidden to make the profiles appear more complete.

## Observations

- Canonical subjects remained `RELIANCE`, `HDFCBANK`, `KAYNES`, and
  `ATHERENERG`; Yahoo `.NS` tickers stayed adapter-local.
- RELIANCE financial acquisition executed the configured multi-source path.
  Both providers survived in the acquisition snapshot. No live canonical
  contradiction happened in this sample; deterministic tests cover differing
  canonical values and preserve both plus an unresolved contradiction group.
- HDFCBANK produced no industrial interpretation. Sector-specific safety is
  enforced separately from evidence retention.
- KAYNES produced company-sector and company-industry relationships from
  canonical profile evidence. Tapetide filing fields remained ambiguous rather
  than becoming invented dependency/event facts.
- ATHERENERG returned a sparse, partial profile. Missing evidence and limited
  history remained explicit.
- RELIANCE authoritative confirmation was justified by an explicit material
  financial-source claim linked to acquired evidence. The configured company-IR
  annual-report index returned `NOT_FOUND`; the result and discovery lineage
  were retained exactly.
- Each graph contained two evidence-backed classification edges. No ambiguous
  supplier/customer relationship became an edge.
- All four serialized `DeepResearchResult` records reconstructed offline with
  identical canonical facts, contradictions, research gaps, graph, confirmation
  state, and semantic fingerprint. Replay made no provider call.

## Acceptance history

An initial sandboxed attempt made no calls because `uvx` was not visible on the
shell path. The script was corrected to recognize the accepted virtual
environment sibling executable without implementing another Yahoo client.

The first network-enabled run reached both MCP servers but constructed its
as-of envelope before process initialization. Yahoo acquisition-time evidence
therefore arrived after the as-of timestamp and was correctly excluded. This
was a live-script PIT-envelope defect, not a provider mapping defect. The final
script establishes a small bounded envelope per scenario after both sessions
initialize. It does not weaken timestamp filtering or alter provider semantics.

Three additional Yahoo profile diagnostics were read-only and printed only
status, field names, or response-envelope key/type shapes; no values or secrets
were retained. These diagnostics identified the timestamp cause before the
final bounded acceptance rerun.

## Latency

- minimum scenario total: 1.616775 seconds;
- median scenario total: 2.042990 seconds;
- maximum scenario total: 3.084447 seconds; and
- total reported provider elapsed time: 8.787203 seconds.

## Security and scope

The live script uses the accepted provider registry, router, Tapetide adapter,
Yahoo adapter, authoritative gateway, and integration assembler. It contains no
mutation operation, arbitrary MCP proxy, broker action, anti-bot bypass, model
call, probability generation, or trade expression. The study records no secret.
