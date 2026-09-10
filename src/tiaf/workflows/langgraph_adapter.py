"""Optional pinned LangGraph infrastructure; no framework object crosses the API."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langsmith.run_helpers import tracing_context

from tiaf.agents import AgentRegistry
from tiaf.planner.models import OrchestrationRequest

from .coordinator import OrchestrationCoordinator
from .records import OrchestrationRunRecord
from .services import ControlledServices


class _State(TypedDict, total=False):
    replan: bool
    result_json: str


def run_langgraph(
    request: OrchestrationRequest,
    registry: AgentRegistry,
    services: ControlledServices | None = None,
) -> OrchestrationRunRecord:
    coordinator = OrchestrationCoordinator(registry, services, parallel=True)

    def initialize(state: _State) -> _State:
        coordinator.initialize(request)
        return {"replan": False}

    def acquire(state: _State) -> _State:
        coordinator.acquire()
        return {}

    def run_waves(state: _State) -> _State:
        coordinator.run_waves()
        return {}

    def inspect(state: _State) -> _State:
        return {"replan": coordinator.inspect()}

    def finalize(state: _State) -> _State:
        return {"result_json": coordinator.finalize("langgraph-1.2.11").model_dump_json()}

    builder = StateGraph(_State)
    builder.add_node("initialize", initialize)
    builder.add_node("acquire", acquire)
    builder.add_node("run_waves", run_waves)
    builder.add_node("inspect", inspect)
    builder.add_node("finalize", finalize)
    builder.add_edge(START, "initialize")
    builder.add_edge("initialize", "acquire")
    builder.add_edge("acquire", "run_waves")
    builder.add_edge("run_waves", "inspect")
    builder.add_conditional_edges("inspect", lambda s: "acquire" if s.get("replan") else "finalize")
    builder.add_edge("finalize", END)
    # Even when a parent process has tracing credentials, this bounded path exports nothing.
    with tracing_context(enabled=False):
        output = builder.compile().invoke({}, config={"recursion_limit": 32, "callbacks": []})
    return OrchestrationRunRecord.model_validate_json(output["result_json"])
