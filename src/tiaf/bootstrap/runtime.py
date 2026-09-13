"""Trusted startup owner above existing facade and engineering composition roots."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from threading import RLock
from types import MappingProxyType
from typing import Any

from pydantic import ValidationError

from tiaf.agents import AgentRegistry
from tiaf.agents._validation import validate_no_secrets
from tiaf.facade import (
    LocalFacadeClient,
    LocalFacadeOwner,
    TrustedFacadeConfig,
    create_local_facade,
)
from tiaf.facade.capabilities import capability_discovery_catalog
from tiaf.facade.contracts import CallerGrant, OperatorPolicy
from tiaf.facade.enums import LifecycleState
from tiaf.optional_adapters import OptionalAdapterError, OptionalAdapterFailure
from tiaf.planner.digests import digest
from tiaf.planner.models import OrchestrationRequest
from tiaf.workflows import (
    ControlledServices,
    OrchestrationRunRecord,
    default_registry,
    run_serial,
    specialist_capability_id,
)

from .catalog import check_langgraph_imports, load_selected_adapter, registered_component
from .contracts import (
    ColdStartupConfig,
    ComponentResolution,
    MissingSelectionPolicy,
    RuntimeProfile,
    StartupComposition,
    StartupError,
    StartupFailure,
    resolve_startup_config,
)

WorkflowRunner = Callable[
    [OrchestrationRequest, AgentRegistry, ControlledServices | None], OrchestrationRunRecord
]


@dataclass(frozen=True, slots=True)
class ColdRuntimeOwner:
    """Trusted handle. Only caller-bound facade clients go to Shell/consumers.

    Python private-member access is not a security sandbox. Implementations remain
    trusted code; neither factories nor service/registry objects reach facade clients.
    """

    composition: StartupComposition
    _facade: LocalFacadeOwner = field(repr=False)
    _implementations: Mapping[str, Any] = field(repr=False)
    _registry: AgentRegistry = field(repr=False)
    _runner: WorkflowRunner = field(repr=False)
    _lock: RLock = field(default_factory=RLock, repr=False, compare=False)
    _active: set[object] = field(default_factory=set, repr=False, compare=False)

    def client(self, caller_id: str) -> LocalFacadeClient:
        return self._facade.client(caller_id)

    def implementation(self, component_id: str) -> Any:
        """Trusted factory lookup only. No acquisition, credentials or construction."""
        self._require_started()
        if component_id not in self._implementations:
            raise StartupError(StartupFailure.REQUIRED_COMPONENT_UNAVAILABLE)
        return self._implementations[component_id]

    def run_workflow(
        self, request: OrchestrationRequest, services: ControlledServices | None = None
    ) -> OrchestrationRunRecord:
        """Trusted engineering entry; existing request/services admission still applies.

        The returned R3 record is unchanged. Persist composition separately and link
        its startup_fingerprint in the owning application's audit record when needed.
        """
        # Captured/prior evidence is invocation input. Live service composition needs
        # its existing trusted engineering root; this owner publishes no live operation.
        services = services.frozen_copy() if services is not None else None
        if services is not None and (
            services.router is not None
            or services.acquisitions
            or services.confirmation_gateway is not None
            or services.confirmation_tasks
            or services.research_controller is not None
        ):
            raise StartupError(StartupFailure.UNSUPPORTED_COMPOSITION)
        token = object()
        with self._lock:
            self._require_started()
            self._active.add(token)
        try:
            return self._runner(request, self._registry, services)
        finally:
            with self._lock:
                self._active.remove(token)

    def _require_started(self) -> None:
        if self._facade.state is not LifecycleState.STARTED:
            raise RuntimeError("COLD runtime is shut down")

    def shutdown(self) -> None:
        with self._lock:
            if self._active:
                raise RuntimeError("cannot shut down while workflows are active")
            self._facade.shutdown()


def _validated_facade(config: TrustedFacadeConfig) -> TrustedFacadeConfig:
    # Existing artifacts are separately checked by the facade. Do not hash/dump them.
    try:
        facade = TrustedFacadeConfig.model_validate_json(config.model_dump_json())
    except ValidationError:
        raise StartupError(StartupFailure.CONFIG_SCHEMA_INVALID) from None
    declarations = {c.capability_id for c in capability_discovery_catalog()}
    grants: tuple[OperatorPolicy | CallerGrant, ...] = (facade.operator, *facade.caller_grants)
    if any(set(item.allowed_capabilities) - declarations for item in grants):
        raise StartupError(StartupFailure.UNKNOWN_COMPONENT_ID)
    try:
        validate_no_secrets([item.model_dump(mode="json") for item in grants])
    except ValueError:
        raise StartupError(StartupFailure.SECRET_CONFIGURATION_INVALID) from None
    return facade


def _authority_fingerprint(config: TrustedFacadeConfig) -> str:
    # Collections in authority policy are sets; physical storage locations are excluded.
    def canonical(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: canonical(item) for key, item in value.items()}
        if isinstance(value, list):
            return sorted((canonical(item) for item in value), key=digest)
        return value

    return digest(
        {
            "schema": "tiaf.cold-authority/1.0",
            "operator": canonical(config.operator.model_dump(mode="json")),
            "callers": canonical([g.model_dump(mode="json") for g in config.caller_grants]),
        }
    )


def create_cold_runtime(
    facade_config: TrustedFacadeConfig,
    *,
    explicit: ColdStartupConfig | dict[str, object] | None = None,
) -> ColdRuntimeOwner:
    """Defaults < explicit trusted config; validate everything before any SDK import.

    Freeze chosen bindings/metadata before starting the existing local facade.
    Optional imports prove importability only, never credential/service readiness.
    """
    config = resolve_startup_config(explicit)
    facade = _validated_facade(facade_config)
    for category, selections in (
        ("adapter", config.selected_adapters),
        ("specialist", config.selected_specialists),
        ("workflow", (config.selected_workflow,)),
    ):
        for selection in selections:
            descriptor = registered_component(selection.component_id)
            if descriptor.category != category:
                raise StartupError(StartupFailure.UNSUPPORTED_COMPOSITION)
            if descriptor.implementation_version != selection.implementation_version:
                raise StartupError(StartupFailure.INCOMPATIBLE_COMPONENT_VERSION)
    if config.runtime_profile is RuntimeProfile.LOCAL_CAPTURED and (
        config.selected_adapters or config.selected_workflow.component_id != "workflow.serial"
    ):
        raise StartupError(StartupFailure.UNSUPPORTED_COMPOSITION)

    available = default_registry()
    specialists = {
        specialist_capability_id(c.specialist): available.get(c.specialist)
        for c in available.capabilities()
    }
    registry = AgentRegistry()
    implementations: dict[str, Any] = {}
    resolutions: list[ComponentResolution] = []
    runner: WorkflowRunner = run_serial
    selections = (*config.selected_adapters, *config.selected_specialists, config.selected_workflow)
    for selection in sorted(selections, key=lambda x: x.component_id):
        descriptor = registered_component(selection.component_id)
        try:
            if descriptor.category == "adapter":
                implementations[selection.component_id] = load_selected_adapter(
                    selection.component_id
                )
                if not callable(implementations[selection.component_id]):
                    raise StartupError(StartupFailure.COMPONENT_IMPORT_FAILED)
            elif descriptor.category == "specialist":
                agent = specialists[selection.component_id]
                if agent.capability().specialist_version != selection.implementation_version:
                    raise StartupError(StartupFailure.INCOMPATIBLE_COMPONENT_VERSION)
                registry.register(agent)
            elif selection.component_id == "workflow.langgraph":
                check_langgraph_imports()
                from tiaf.workflows.langgraph_adapter import run_langgraph

                runner = run_langgraph
        except OptionalAdapterError as exc:
            if exc.failure is not OptionalAdapterFailure.OPTIONAL_DEPENDENCY_MISSING:
                raise StartupError(StartupFailure.COMPONENT_IMPORT_FAILED) from None
            if selection.required or selection.on_missing is MissingSelectionPolicy.FAIL_STARTUP:
                raise StartupError(StartupFailure.REQUIRED_COMPONENT_UNAVAILABLE) from None
            resolutions.append(
                ComponentResolution(
                    selection=selection, status="UNAVAILABLE", failure="OPTIONAL_DEPENDENCY_MISSING"
                )
            )
            continue
        resolutions.append(ComponentResolution(selection=selection, status="IMPORT_RESOLVED"))

    snapshot = registry.frozen_copy()
    composition = StartupComposition.seal(
        config, _authority_fingerprint(facade), tuple(resolutions)
    )
    owner = create_local_facade(facade)
    return ColdRuntimeOwner(composition, owner, MappingProxyType(implementations), snapshot, runner)
