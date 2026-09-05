# TIAF Architecture Thesis

Market discovery, interpretation, governance, and execution are different
responsibilities and should remain separate. Scanners discover; TIAF interprets;
TradeMonitor governs; the broker records authoritative live state.

TIAF should accept sparse inputs—eventually only a watchlist plus a horizon—and
improve when optional context is available without depending on a particular
spreadsheet or scanner schema. Its outputs should be structured, timestamped,
attributable, and suitable for later evaluation.

Deterministic computation is the reference layer. AI belongs only in bounded
tasks where context and judgment matter, and it must be reviewable rather than
authoritative. The system must be comfortable returning `WAIT` or `NO TRADE`.

Opportunity intelligence and position intelligence share infrastructure but
answer different questions. Position evaluation is prospective and does not
require the original entry rationale. Option expression follows, rather than
being entangled with, selection of the underlying opportunity.

This thesis implies contract-first milestones, strict integration boundaries,
and evaluation before operational authority is ever considered.
