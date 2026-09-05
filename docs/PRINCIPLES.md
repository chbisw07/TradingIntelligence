# Engineering Principles

- **Scanners are sensors.** They discover candidates; they do not provide
  final intelligence or execution authority.
- **Agents are interpreters.** Future agents may analyze ambiguous context,
  but they will not control a broker.
- **TradeMonitor is the governor.** Risk, authority, and execution decisions
  remain centralized there.
- **The broker is truth.** Broker state is authoritative for orders,
  executions, and positions.
- **Intelligence is pluggable; authority is centralized.** Intelligence
  providers may evolve independently without distributing control.
- **Compute deterministically where possible.** Use AI only where contextual
  judgment adds value, and make its outputs attributable and evaluable.
- **`NO TRADE` and `WAIT` are valid outcomes.** The system must not manufacture
  action when evidence is insufficient.
- **A watchlist alone will eventually be sufficient input.** Spreadsheet
  columns, indicators, and Greeks are optional enrichment rather than required
  coupling.
- **Position intelligence is forward-looking.** An adopted open position can
  be evaluated without reconstructing its original rationale.
- **Time horizon is first-class.** Analysis and evaluation must identify the
  horizon to which a conclusion applies.
