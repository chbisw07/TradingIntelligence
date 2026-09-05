# Architecture

TIAF is intended to occupy an intelligence boundary between sources of market
candidates and the system that governs risk and execution:

```text
Scanners / Manual input / Third-party sources
                    |
                    v
       TradingIntelligence / TIAF
                    |
                    v
        structured intelligence
                    |
                    v
              TradeMonitor
                    |
                    v
                 Broker
```

TIAF will produce timestamped, attributable, and evaluable structured
intelligence. It will not own broker execution authority. TradeMonitor remains
the governor, while the broker remains the final truth for live state.

## Long-term missions

### Opportunity Intelligence

Given an F&O universe plus a requested style and horizon, identify the strongest
forward opportunities, allow `CE`, `PE`, `WAIT`, or `NO TRADE` conclusions, and
estimate remaining opportunity. Underlying selection and option-expression
selection remain separate stages.

### Position Intelligence

Evaluate existing or adopted positions prospectively. The service should
eventually support conclusions such as `HOLD`, `WATCH_CLOSELY`, `PROTECT`,
`PARTIAL_BOOK`, `BOOK`, or `EXIT` without requiring the original trade thesis.

## Package boundaries

The current namespaces reserve clear seams for contracts, data, planning,
specialist interpretation, arbitration, workflows, memory, evaluation, service
delivery, and observability. At `TIAF_TGT0` these are boundaries only; no agent,
market, or execution behavior is implemented.
