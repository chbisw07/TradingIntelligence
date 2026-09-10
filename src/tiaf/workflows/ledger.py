"""Atomic pre-dispatch reservations shared by all nested controlled operations."""

from threading import RLock

from tiaf.agents import AgentBudget, AgentUsage
from tiaf.planner.models import Reservation


def reserved_usage(budget: AgentBudget) -> AgentUsage:
    return AgentUsage(
        tool_calls=budget.max_tool_calls,
        llm_calls=budget.max_llm_calls,
        input_tokens=budget.max_input_tokens,
        output_tokens=budget.max_output_tokens,
        cost_units=budget.max_cost_units,
    )


def add_usage(values: tuple[AgentUsage, ...], *, elapsed: float = 0) -> AgentUsage:
    return AgentUsage(
        tool_calls=sum(v.tool_calls for v in values),
        llm_calls=sum(v.llm_calls for v in values),
        input_tokens=sum(v.input_tokens for v in values),
        output_tokens=sum(v.output_tokens for v in values),
        cost_units=sum(v.cost_units for v in values),
        elapsed_seconds=elapsed,
    )


class ReservationLedger:
    def __init__(self, ceiling: AgentBudget, provider_limit: int) -> None:
        self.ceiling = ceiling
        self.provider_limit = provider_limit
        self._entries: dict[str, Reservation] = {}
        self._lock = RLock()
        self.exceeded = False

    def entries(self) -> tuple[Reservation, ...]:
        with self._lock:
            return tuple(self._entries.values())

    def committed_usage(self) -> AgentUsage:
        with self._lock:
            return add_usage(
                tuple(
                    r.actual
                    if r.state == "SETTLED" and r.actual is not None
                    else reserved_usage(r.budget)
                    for r in self._entries.values()
                )
            )

    def provider_calls(self) -> int:
        with self._lock:
            return sum(
                r.actual_provider_calls if r.actual_provider_calls is not None else r.provider_calls
                for r in self._entries.values()
            )

    def reserve(self, accounting_id: str, budget: AgentBudget, provider_calls: int = 0) -> bool:
        with self._lock:
            if accounting_id in self._entries:
                raise ValueError("duplicate accounting ID")
            proposed = add_usage((self.committed_usage(), reserved_usage(budget)))
            if self.exceeded or self.ceiling.violations(proposed):
                return False
            if self.provider_calls() + provider_calls > self.provider_limit:
                return False
            self._entries[accounting_id] = Reservation(
                accounting_id=accounting_id,
                budget=budget,
                provider_calls=provider_calls,
            )
            return True

    def settle(
        self, accounting_id: str, usage: AgentUsage | None, provider_calls: int | None = None
    ) -> None:
        with self._lock:
            original = self._entries[accounting_id]
            if original.state != "OUTSTANDING":
                raise ValueError("operation already settled")
            unknown = usage is None or (original.provider_calls > 0 and provider_calls is None)
            self._entries[accounting_id] = Reservation(
                accounting_id=accounting_id,
                budget=original.budget,
                provider_calls=original.provider_calls,
                actual=usage,
                actual_provider_calls=provider_calls,
                state="UNKNOWN" if unknown else "SETTLED",
            )
            if usage is not None and original.budget.violations(usage):
                self.exceeded = True
            if provider_calls is not None and provider_calls > original.provider_calls:
                self.exceeded = True
            if self.ceiling.violations(self.committed_usage()):
                self.exceeded = True
