"""R5 trusted selection, absence, immutability, isolation and replay regressions."""

import json
import socket
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from pathlib import Path
from threading import Event
from typing import Any

import pytest
from pydantic import ValidationError
from scripts._a3_8_fixtures import NOW, request

from tiaf.agents import AgentRegistry, SpecialistId
from tiaf.bootstrap import (
    ColdStartupConfig,
    ComponentSelection,
    StartupComposition,
    StartupError,
    StartupFailure,
    create_cold_runtime,
    registered_components,
    replay_startup_composition,
    resolve_startup_config,
)
from tiaf.cold_bindings import FrozenBindingsError
from tiaf.data.resolution import InstrumentQuery, InstrumentResolverRegistry
from tiaf.data.resolution.models import ResolutionResult
from tiaf.facade import capability_discovery_catalog
from tiaf.market_intelligence import MarketIntelligenceRegistry, MarketIntelligenceRouter
from tiaf.optional_adapters import OptionalAdapterError, OptionalAdapterFailure
from tiaf.shell import SessionDefaults, ShellBootstrapConfig, ShellDispatcher, ShellRuntime
from tiaf.shell.cli import main
from tiaf.workflows import (
    ControlledServices,
    OrchestrationCoordinator,
    capture_json,
    default_registry,
    replay_recorded,
    run_serial,
    verify_deterministic,
)

from .facade._support import AUTHORITY, PROFILE, config
from .shell._support import position_defaults
from .test_r4_optional_adapter_import_isolation import _isolated

YAHOO = "provider.market-intelligence.yahoo-mcp"


def engineering(*, required: bool = True, missing: str = "FAIL_STARTUP") -> dict[str, object]:
    return {
        "runtime_profile": "LOCAL_ENGINEERING",
        "selected_adapters": [{"component_id": YAHOO, "required": required, "on_missing": missing}],
    }


def unavailable(component_id: str) -> Any:
    raise OptionalAdapterError(
        failure=OptionalAdapterFailure.OPTIONAL_DEPENDENCY_MISSING,
        adapter_id=component_id,
        dependency="mcp",
    )


def test_defaults_and_explicit_override_have_one_deterministic_precedence() -> None:
    default = resolve_startup_config()
    overridden = resolve_startup_config({"selected_specialists": []})
    assert len(default.selected_specialists) == 9
    assert overridden.selected_specialists == ()
    assert overridden.selected_workflow == default.selected_workflow
    assert resolve_startup_config(overridden.model_dump(mode="json")) == overridden
    assert resolve_startup_config({}) == default


@pytest.mark.parametrize(
    ("payload", "failure"),
    [
        ({"schema_version": "999"}, StartupFailure.CONFIG_SCHEMA_INVALID),
        ({"runtime_profile": "unknown"}, StartupFailure.CONFIG_SCHEMA_INVALID),
        ({"selected_model_provider": "anything"}, StartupFailure.CONFIG_SCHEMA_INVALID),
        ({"feature_flags": {"a5_policy": "override"}}, StartupFailure.CONFIG_SCHEMA_INVALID),
        ({"module": "/tmp/unknown.py"}, StartupFailure.CONFIG_SCHEMA_INVALID),
        ({"selected_adapters": [{"component_id": "unknown"}]}, StartupFailure.UNKNOWN_COMPONENT_ID),
        (
            {"selected_specialists": [{"component_id": "specialist:forecast-interpretation"}]},
            StartupFailure.UNKNOWN_COMPONENT_ID,
        ),
        (
            {
                "selected_workflow": {
                    "component_id": "workflow.serial",
                    "implementation_version": "999",
                }
            },
            StartupFailure.INCOMPATIBLE_COMPONENT_VERSION,
        ),
        (
            {"selected_adapters": [{"component_id": "workflow.serial"}]},
            StartupFailure.CONFIGURATION_CONFLICT,
        ),
        (
            {"selected_specialists": [{"component_id": YAHOO}]},
            StartupFailure.UNSUPPORTED_COMPOSITION,
        ),
        ({"selected_adapters": [{"component_id": YAHOO}]}, StartupFailure.UNSUPPORTED_COMPOSITION),
        (
            {"selected_workflow": {"component_id": "workflow.serial", "required": False}},
            StartupFailure.UNSUPPORTED_COMPOSITION,
        ),
        (
            {"selected_adapters": [{"component_id": YAHOO, "on_missing": "RECORD_UNAVAILABLE"}]},
            StartupFailure.CONFIGURATION_CONFLICT,
        ),
        (
            {"selected_adapters": [{"component_id": YAHOO, "required": "false"}]},
            StartupFailure.CONFIG_SCHEMA_INVALID,
        ),
    ],
)
def test_invalid_selection_fails_before_import_or_facade_construction(
    payload: dict[str, object],
    failure: StartupFailure,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("invalid config reached construction/import")

    monkeypatch.setattr("tiaf.bootstrap.runtime.load_selected_adapter", forbidden)
    monkeypatch.setattr("tiaf.bootstrap.runtime.create_local_facade", forbidden)
    with pytest.raises(StartupError) as caught:
        create_cold_runtime(config(), explicit=payload)
    assert caught.value.failure is failure
    assert "/tmp/" not in str(caught.value)


def test_duplicate_selection_and_forged_model_fail_closed() -> None:
    duplicate = [ComponentSelection(component_id=YAHOO)] * 2
    forged = ColdStartupConfig().model_copy(update={"selected_adapters": tuple(duplicate)})
    with pytest.raises(StartupError) as caught:
        create_cold_runtime(config(), explicit=forged)
    assert caught.value.failure is StartupFailure.CONFIGURATION_CONFLICT


@pytest.mark.parametrize(("required", "policy"), [(True, "FAIL_STARTUP"), (False, "FAIL_STARTUP")])
def test_missing_selected_adapter_fails_closed_without_constructing_runtime(
    required: bool,
    policy: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("tiaf.bootstrap.runtime.load_selected_adapter", unavailable)
    with pytest.raises(StartupError) as caught:
        create_cold_runtime(config(), explicit=engineering(required=required, missing=policy))
    assert caught.value.failure is StartupFailure.REQUIRED_COMPONENT_UNAVAILABLE


def test_optional_missing_is_recorded_without_substitution_and_is_replayable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def missing(component_id: str) -> Any:
        calls.append(component_id)
        return unavailable(component_id)

    monkeypatch.setattr("tiaf.bootstrap.runtime.load_selected_adapter", missing)
    runtime = create_cold_runtime(
        config(), explicit=engineering(required=False, missing="RECORD_UNAVAILABLE")
    )
    assert calls == [YAHOO]
    assert runtime.composition.degraded
    assert len(runtime.composition.config.selected_adapters) == 1
    with pytest.raises(StartupError):
        runtime.implementation(YAHOO)
    saved = runtime.composition.model_dump_json()
    assert replay_startup_composition(saved) == runtime.composition
    assert calls == [YAHOO]


def test_selected_factory_is_bound_and_import_does_not_construct_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class NeverConstructed:
        def __init__(self) -> None:
            pytest.fail("startup must not read credentials or construct transports")

    monkeypatch.setattr("tiaf.bootstrap.runtime.load_selected_adapter", lambda _: NeverConstructed)
    runtime = create_cold_runtime(config(), explicit=engineering())
    assert runtime.implementation(YAHOO) is NeverConstructed
    assert not runtime.composition.degraded
    with pytest.raises(StartupError):
        runtime.implementation("provider.market-intelligence.tapetide-mcp")


def test_broken_internal_import_is_never_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(_: str) -> Any:
        raise ModuleNotFoundError("internal defect", name="internal_module")

    monkeypatch.setattr("tiaf.bootstrap.runtime.load_selected_adapter", broken)
    with pytest.raises(ModuleNotFoundError, match="internal defect"):
        create_cold_runtime(
            config(), explicit=engineering(required=False, missing="RECORD_UNAVAILABLE")
        )


def test_broken_export_is_typed_and_never_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(_: str) -> Any:
        raise OptionalAdapterError(
            failure=OptionalAdapterFailure.OPTIONAL_ADAPTER_IMPORT_FAILED, adapter_id=YAHOO
        )

    monkeypatch.setattr("tiaf.bootstrap.runtime.load_selected_adapter", broken)
    with pytest.raises(StartupError) as caught:
        create_cold_runtime(
            config(), explicit=engineering(required=False, missing="RECORD_UNAVAILABLE")
        )
    assert caught.value.failure is StartupFailure.COMPONENT_IMPORT_FAILED


def test_identity_is_order_independent_and_changes_with_selection_policy_and_authority() -> None:
    before = create_cold_runtime(config()).composition
    reordered = ColdStartupConfig().model_dump(mode="json")
    reordered["selected_specialists"].reverse()
    assert create_cold_runtime(config(), explicit=reordered).composition == before
    reduced = create_cold_runtime(config(), explicit={"selected_specialists": []}).composition
    assert reduced.configuration_fingerprint != before.configuration_fingerprint
    changed = config().model_copy(
        update={"operator": config().operator.model_copy(update={"policy_version": "2.0"})}
    )
    assert (
        create_cold_runtime(changed).composition.configuration_fingerprint
        != before.configuration_fingerprint
    )
    policy = ColdStartupConfig().model_dump(mode="json")
    policy["selected_specialists"][0]["required"] = False
    assert (
        create_cold_runtime(config(), explicit=policy).composition.configuration_fingerprint
        != before.configuration_fingerprint
    )


def test_availability_changes_startup_identity_without_changing_requested_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected = engineering(required=False, missing="RECORD_UNAVAILABLE")
    monkeypatch.setattr("tiaf.bootstrap.runtime.load_selected_adapter", unavailable)
    absent = create_cold_runtime(config(), explicit=selected).composition
    monkeypatch.setattr("tiaf.bootstrap.runtime.load_selected_adapter", lambda _: object)
    present = create_cold_runtime(config(), explicit=selected).composition
    assert present.configuration_fingerprint == absent.configuration_fingerprint
    assert present.startup_fingerprint != absent.startup_fingerprint


def test_secret_environment_never_enters_config_fingerprint_or_discovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = create_cold_runtime(config()).composition
    for value in ("test-credential-one", "test-credential-two"):
        monkeypatch.setenv("DHAN_ACCESS_TOKEN", value)
        monkeypatch.setenv("TIAF_SELECTED_WORKFLOW", "workflow.langgraph")
        current = create_cold_runtime(config()).composition
        assert current == original
        assert value not in current.model_dump_json()
        assert value not in repr(registered_components())
        with pytest.raises(StartupError) as caught:
            resolve_startup_config({"api_key": value})
        assert caught.value.failure is StartupFailure.SECRET_CONFIGURATION_INVALID
        assert value not in str(caught.value)


def test_snapshot_and_owner_are_immutable_and_client_has_no_mutation_surface() -> None:
    runtime = create_cold_runtime(config())
    with pytest.raises(FrozenInstanceError):
        setattr(runtime, "composition", runtime.composition)
    with pytest.raises(ValidationError, match="frozen"):
        setattr(runtime.composition.config, "selected_adapters", ())
    with pytest.raises(FrozenBindingsError):
        runtime._registry.register(default_registry().get(SpecialistId.TECHNICAL))
    assert not hasattr(runtime.client("caller:test"), "implementation")
    assert not hasattr(runtime.client("caller:test"), "composition")
    assert isinstance(runtime.composition.resolutions, tuple)
    payload = runtime.composition.model_dump(mode="json")
    assert isinstance(payload["resolutions"], list)
    assert StartupComposition.model_validate(payload) == runtime.composition
    payload["startup_fingerprint"] = "0" * 64
    with pytest.raises(StartupError):
        replay_startup_composition(json.dumps(payload))


def test_missing_unselected_sdks_do_not_break_startup_and_recorded_replay() -> None:
    # Synthetic trusted facade payload supplied via stdin; child imports no fixture/provider code.
    result = _isolated(
        """
from tiaf.facade import TrustedFacadeConfig
from tiaf.bootstrap import create_cold_runtime, replay_startup_composition
runtime = create_cold_runtime(TrustedFacadeConfig.model_validate_json(sys.stdin.read()))
assert replay_startup_composition(runtime.composition.model_dump_json()) == runtime.composition
assert not OPTIONAL_ROOTS.intersection(sys.modules)
runtime.shutdown()
""",
        stdin=config().model_dump_json(),
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "component",
    [
        "provider.market-data.dhan",
        YAHOO,
        "provider.market-intelligence.tapetide-mcp",
        "provider.market-intelligence.authoritative-http",
        "workflow.langgraph",
    ],
)
def test_actual_blocked_selected_sdk_fails_at_startup(component: str) -> None:
    selected: dict[str, object] = {"runtime_profile": "LOCAL_ENGINEERING"}
    if component == "workflow.langgraph":
        selected["selected_workflow"] = {
            "component_id": component,
            "implementation_version": "1.2.11",
        }
    else:
        selected["selected_adapters"] = [{"component_id": component}]
    result = _isolated(
        f"""
from tiaf.facade import TrustedFacadeConfig
from tiaf.bootstrap import create_cold_runtime, StartupError, StartupFailure
try:
    trusted = TrustedFacadeConfig.model_validate_json(sys.stdin.read())
    create_cold_runtime(trusted, explicit={selected!r})
except StartupError as exc:
    assert exc.failure is StartupFailure.REQUIRED_COMPONENT_UNAVAILABLE
else:
    raise AssertionError("startup unexpectedly succeeded")
""",
        stdin=config().model_dump_json(),
    )
    assert result.returncode == 0, result.stderr


def test_r2_and_r3_stay_unchanged_and_replay_opens_no_socket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = capability_discovery_catalog()
    runtime = create_cold_runtime(config())

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("offline operation opened a network socket")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    actual = runtime.run_workflow(request())
    direct = run_serial(request(), default_registry())
    assert actual.fingerprint == direct.fingerprint
    assert actual.composition is not None and direct.composition is not None
    assert actual.composition.composition_fingerprint == direct.composition.composition_fingerprint
    assert replay_recorded(capture_json(actual)) == actual
    assert verify_deterministic(capture_json(actual), default_registry()) == actual
    assert capability_discovery_catalog() == before
    assert len(before) == 9
    assert "startup_fingerprint" not in actual.model_dump(mode="json")


def test_required_scope_does_not_shrink_with_cold_binding_absence() -> None:
    selected = ColdStartupConfig().model_dump(mode="json")
    selected["selected_specialists"] = [
        item
        for item in selected["selected_specialists"]
        if item["component_id"] != "specialist:fundamental"
    ]
    runtime = create_cold_runtime(config(), explicit=selected)
    record = runtime.run_workflow(request())
    assert record.composition is not None
    fundamental = next(
        x for x in record.composition.participants if x.capability_id == "specialist:fundamental"
    )
    assert fundamental.requiredness.value == "REQUIRED"
    assert fundamental.status.value == "NOT_REGISTERED"
    assert not record.composition.required_complete


def test_langgraph_selected_workflow_preserves_serial_semantics() -> None:
    runtime = create_cold_runtime(
        config(),
        explicit={
            "runtime_profile": "LOCAL_ENGINEERING",
            "selected_workflow": {
                "component_id": "workflow.langgraph",
                "implementation_version": "1.2.11",
            },
        },
    )
    actual = runtime.run_workflow(request())
    assert actual.fingerprint == run_serial(request(), default_registry()).fingerprint
    assert runtime.composition.config.selected_workflow.component_id == "workflow.langgraph"


def test_in_flight_registry_and_services_are_stable_when_source_owner_changes() -> None:
    source = default_registry()
    reduced = AgentRegistry(
        tuple(
            source.get(c.specialist)
            for c in source.capabilities()
            if c.specialist is not SpecialistId.FUNDAMENTAL
        )
    )
    services = ControlledServices()
    coordinator = OrchestrationCoordinator(reduced, services)
    entered, proceed = Event(), Event()

    def execute() -> Any:
        coordinator.initialize(request())
        entered.set()
        assert proceed.wait(10)
        coordinator.acquire()
        coordinator.run_waves()
        coordinator.inspect()
        return coordinator.finalize("serial-1.0")

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(execute)
        assert entered.wait(10)
        try:
            reduced.register(source.get(SpecialistId.FUNDAMENTAL))
            services.prior_runs = ()
            with pytest.raises(FrozenBindingsError):
                coordinator.services.router = None
            with pytest.raises(FrozenBindingsError):
                coordinator.registry.register(source.get(SpecialistId.FUNDAMENTAL))
        finally:
            proceed.set()
        record = future.result(timeout=15)
    assert record.composition is not None
    assert (
        next(
            x
            for x in record.composition.participants
            if x.capability_id == "specialist:fundamental"
        ).status.value
        == "NOT_REGISTERED"
    )


def test_resolver_replacement_is_pre_start_only_and_frozen_copy_is_independent() -> None:
    class Resolver:
        def __init__(self, marker: str) -> None:
            self.marker = marker

        def resolve(self, query: InstrumentQuery) -> ResolutionResult:
            return ResolutionResult(
                query=query, not_found=True, observed_at=NOW, metadata={"marker": self.marker}
            )

        def search(self, query: Any) -> Any:
            return ()

        def resolve_many(self, queries: Any) -> Any:
            return ()

    registry = InstrumentResolverRegistry()
    registry.register("dhan", Resolver("first"))
    registry.register("dhan", Resolver("chosen"))
    pinned = registry.frozen_copy()
    registry.register("dhan", Resolver("later-owner"))
    query = InstrumentQuery(symbol="RELIANCE", provider="DHAN")
    assert pinned.resolve(query).metadata["marker"] == "chosen"
    assert registry.resolve(query).metadata["marker"] == "later-owner"
    with pytest.raises(FrozenBindingsError):
        registry.register("dhan", Resolver("too-late"))


def test_market_provider_snapshot_pins_pairs_and_cannot_add_after_router_start() -> None:
    from tiaf.market_intelligence import RuleBasedNormalizer
    from tiaf.market_intelligence.providers import FixtureMarketIntelligenceProvider

    registry = MarketIntelligenceRegistry()
    first = FixtureMarketIntelligenceProvider("first", (), {})
    registry.register(first, RuleBasedNormalizer("first", ()))
    router = MarketIntelligenceRouter(registry)
    second = FixtureMarketIntelligenceProvider("second", (), {})
    registry.register(second, RuleBasedNormalizer("second", ()))
    assert router._registry.provider("first") is first
    with pytest.raises(LookupError):
        router._registry.provider("second")
    with pytest.raises(FrozenBindingsError):
        router._registry.register(second, RuleBasedNormalizer("second", ()))


def test_shell_bootstrap_uses_cold_owner_and_a5_remains_captured_read(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bootstrap = ShellBootstrapConfig(
        facade=config(),
        caller_id="caller:test",
        baseline_request_root=str(tmp_path),
        defaults=position_defaults(),
    )
    path = tmp_path / "shell.json"
    path.write_text(bootstrap.model_dump_json(), encoding="utf-8")
    assert (
        main(
            [
                "--config",
                str(path),
                "--output",
                "json",
                "position",
                "assess",
                "--snapshot",
                "artifact:position-request",
            ]
        )
        == 0
    )
    output = json.loads(capsys.readouterr().out)
    assert output["capability_id"] == "position.assess"
    runtime = create_cold_runtime(config())
    shell = ShellRuntime(
        ShellDispatcher(
            runtime.client("caller:test"),
            baseline_request_root=tmp_path,
            defaults=SessionDefaults(profile_ref=PROFILE, authority_ref=AUTHORITY),
        )
    )
    before = runtime.composition
    for command in (
        ["config", "set", "selected_workflow", "workflow.langgraph"],
        ["enable", YAHOO],
        ["set", "selected_adapters", YAHOO],
    ):
        assert shell.execute_tokens(command).exit_code == 2
    assert runtime.composition == before


def test_unknown_facade_capability_is_rejected_without_authority_escalation() -> None:
    original = config()
    forged = original.model_copy(
        update={
            "operator": original.operator.model_copy(
                update={
                    "allowed_capabilities": (
                        *original.operator.allowed_capabilities,
                        "live.acquire",
                    )
                }
            )
        }
    )
    with pytest.raises(StartupError) as caught:
        create_cold_runtime(forged)
    assert caught.value.failure is StartupFailure.UNKNOWN_COMPONENT_ID


def test_workflow_shutdown_waits_for_active_call_and_rejects_new_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entered, proceed = Event(), Event()

    def bounded(*args: Any) -> Any:
        entered.set()
        assert proceed.wait(10)
        return run_serial(*args)

    monkeypatch.setattr("tiaf.bootstrap.runtime.run_serial", bounded)
    runtime = create_cold_runtime(config())
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(runtime.run_workflow, request())
        assert entered.wait(10)
        try:
            with pytest.raises(RuntimeError, match="workflows are active"):
                runtime.shutdown()
        finally:
            proceed.set()
        future.result(timeout=15)
    runtime.shutdown()
    with pytest.raises(RuntimeError, match="shut down"):
        runtime.run_workflow(request())


def test_owner_cannot_smuggle_live_services_into_captured_workflow() -> None:
    runtime = create_cold_runtime(config())
    services = ControlledServices(router=MarketIntelligenceRouter(MarketIntelligenceRegistry()))
    with pytest.raises(StartupError) as caught:
        runtime.run_workflow(request(), services)
    assert caught.value.failure is StartupFailure.UNSUPPORTED_COMPOSITION


def test_selected_langgraph_installed_version_must_match_pin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("tiaf.bootstrap.catalog.version", lambda _: "999.0")
    with pytest.raises(StartupError) as caught:
        create_cold_runtime(
            config(),
            explicit={
                "runtime_profile": "LOCAL_ENGINEERING",
                "selected_workflow": {
                    "component_id": "workflow.langgraph",
                    "implementation_version": "1.2.11",
                },
            },
        )
    assert caught.value.failure is StartupFailure.INCOMPATIBLE_COMPONENT_VERSION


def test_feature_indicator_engines_pin_registry_membership() -> None:
    from tiaf.features.engine import DeterministicFeatureEngine, builtin_feature_registry
    from tiaf.features.registry import FeatureRegistry
    from tiaf.indicators import IndicatorEngine, IndicatorRegistry, builtin_indicator_registry

    features = FeatureRegistry()
    feature_engine = DeterministicFeatureEngine(features)
    feature_builtins = builtin_feature_registry()
    calculator = feature_builtins.get_calculator(feature_builtins.definitions()[0].feature_id)
    features.register(calculator)
    assert feature_engine.definitions() == ()
    with pytest.raises(FrozenBindingsError):
        feature_engine._registry.register(calculator)
    indicators = IndicatorRegistry()
    indicator_engine = IndicatorEngine(indicators)
    indicator_builtins = builtin_indicator_registry()
    indicator = indicator_builtins.get_calculator(indicator_builtins.definitions()[0].indicator_id)
    indicators.register(indicator)
    assert indicator_engine.definitions() == ()
    with pytest.raises(FrozenBindingsError):
        indicator_engine._registry.register(indicator)
