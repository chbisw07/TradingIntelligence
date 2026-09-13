"""Optional pinned LangGraph infrastructure; no framework object crosses the API."""

from typing import TypedDict

from tiaf.agents import AgentRegistry
from tiaf.optional_adapters import load_optional_attribute
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
    end = load_optional_attribute(
        adapter_id="workflow.langgraph",
        module="langgraph.graph",
        attribute="END",
        dependency_imports=("langgraph", "langsmith"),
    )
    start = load_optional_attribute(
        adapter_id="workflow.langgraph",
        module="langgraph.graph",
        attribute="START",
        dependency_imports=("langgraph", "langsmith"),
    )
    state_graph = load_optional_attribute(
        adapter_id="workflow.langgraph",
        module="langgraph.graph",
        attribute="StateGraph",
        dependency_imports=("langgraph", "langsmith"),
    )
    tracing_context = load_optional_attribute(
        adapter_id="workflow.langgraph",
        module="langsmith.run_helpers",
        attribute="tracing_context",
        dependency_imports=("langgraph", "langsmith"),
    )
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

    builder = state_graph(_State)
    builder.add_node("initialize", initialize)
    builder.add_node("acquire", acquire)
    builder.add_node("run_waves", run_waves)
    builder.add_node("inspect", inspect)
    builder.add_node("finalize", finalize)
    builder.add_edge(start, "initialize")
    builder.add_edge("initialize", "acquire")
    builder.add_edge("acquire", "run_waves")
    builder.add_edge("run_waves", "inspect")
    builder.add_conditional_edges("inspect", lambda s: "acquire" if s.get("replan") else "finalize")
    builder.add_edge("finalize", end)
    # Even when a parent process has tracing credentials, this bounded path exports nothing.
    with tracing_context(enabled=False):
        output = builder.compile().invoke({}, config={"recursion_limit": 32, "callbacks": []})
    return OrchestrationRunRecord.model_validate_json(output["result_json"])
