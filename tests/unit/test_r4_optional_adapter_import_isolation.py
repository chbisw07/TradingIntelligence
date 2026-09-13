"""R4 optional adapter import-isolation and packaging regressions."""

import subprocess
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest

from tiaf.optional_adapters import (
    OptionalAdapterClassification,
    OptionalAdapterError,
    OptionalAdapterFailure,
    load_optional_attribute,
    optional_adapter_catalog,
    optional_adapter_descriptor,
)

ROOT = Path(__file__).resolve().parents[2]

_BLOCK_OPTIONALS = """
import sys
OPTIONAL_ROOTS = {"httpx", "mcp", "dotenv", "pydantic_settings", "langgraph", "langsmith"}
class OptionalImportBlocker:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition(".")[0] in OPTIONAL_ROOTS:
            raise ModuleNotFoundError(
                f"blocked optional dependency: {fullname}",
                name=fullname,
            )
sys.meta_path.insert(0, OptionalImportBlocker())
"""


def _isolated(code: str, *, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", _BLOCK_OPTIONALS + code],
        cwd=ROOT,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_core_facade_shell_and_provider_namespaces_import_without_optional_sdks() -> None:
    result = _isolated(
        """
import tiaf
import tiaf.a4
import tiaf.a5
import tiaf.baseline
import tiaf.data
import tiaf.data.providers
import tiaf.data.providers.dhan
import tiaf.facade
import tiaf.market_intelligence
import tiaf.market_intelligence.providers
import tiaf.shell
import tiaf.workflows
import tiaf.workflows.langgraph_adapter
from tiaf.data.providers import DhanInstrumentType
from tiaf.facade import capability_catalog
from tiaf.market_intelligence.providers import FixtureMarketIntelligenceProvider
from tiaf.optional_adapters import optional_adapter_catalog
assert DhanInstrumentType.EQUITY.value == "EQUITY"
assert FixtureMarketIntelligenceProvider.__name__ == "FixtureMarketIntelligenceProvider"
assert len(capability_catalog()) == 8
assert len(optional_adapter_catalog()) == 5
assert callable(tiaf.workflows.run_serial)
assert not OPTIONAL_ROOTS.intersection(sys.modules)
"""
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_shell_help_is_safe_without_optional_sdks() -> None:
    result = _isolated(
        """
from tiaf.shell.cli import main
assert main(["help"]) == 0
assert not OPTIONAL_ROOTS.intersection(sys.modules)
"""
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "TI Shell v0.1" in result.stdout


def test_shell_discovery_baseline_and_position_continue_without_optional_sdks(
    tmp_path: Path,
) -> None:
    from tiaf.shell import SessionDefaults, ShellBootstrapConfig

    from .facade._support import AUTHORITY, PROFILE, config
    from .shell._support import position_defaults, write_baseline

    write_baseline(tmp_path)
    baseline_bootstrap = ShellBootstrapConfig(
        facade=config(),
        caller_id="caller:test",
        baseline_request_root=str(tmp_path),
        defaults=SessionDefaults(profile_ref=PROFILE, authority_ref=AUTHORITY),
    )
    position_bootstrap = ShellBootstrapConfig(
        facade=config(),
        caller_id="caller:test",
        baseline_request_root=str(tmp_path),
        defaults=position_defaults().model_copy(
            update={"profile_ref": PROFILE, "authority_ref": AUTHORITY}
        ),
    )
    baseline_path = tmp_path / "baseline-shell.json"
    position_path = tmp_path / "position-shell.json"
    baseline_path.write_text(baseline_bootstrap.model_dump_json(), encoding="utf-8")
    position_path.write_text(position_bootstrap.model_dump_json(), encoding="utf-8")
    result = _isolated(
        f"""
from tiaf.shell.cli import main
baseline = ["--config", {str(baseline_path)!r}, "--output", "json"]
position = ["--config", {str(position_path)!r}, "--output", "json"]
assert main([*baseline, "capabilities", "list"]) == 0
assert main([*baseline, "capabilities", "describe", "baseline.assess"]) == 0
assert main([*baseline, "baseline", "assess", "--request-file", "baseline.json"]) == 0
assert main([*position, "position", "assess", "--snapshot", "artifact:position-request"]) == 0
assert main([*position, "replay", "recorded", "--artifact-ref", "artifact:a5-capture"]) == 0
assert not OPTIONAL_ROOTS.intersection(sys.modules)
"""
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"capability_id":"capabilities.list"' in result.stdout
    assert '"command_name":"capabilities describe"' in result.stdout
    assert '"capability_id":"baseline.assess"' in result.stdout
    assert '"capability_id":"position.assess"' in result.stdout
    assert '"capability_id":"replay.recorded"' in result.stdout


def test_static_catalog_enumeration_does_not_import_implementations() -> None:
    descriptors = optional_adapter_catalog()
    assert tuple(item.adapter_id for item in descriptors) == tuple(
        sorted(item.adapter_id for item in descriptors)
    )
    assert all(
        item.classification is OptionalAdapterClassification.OPTIONAL_ISOLATED
        for item in descriptors
    )
    assert all(item.dependencies and item.install_extra for item in descriptors)


def test_unknown_adapter_selection_is_explicit_and_scoped() -> None:
    with pytest.raises(OptionalAdapterError) as caught:
        optional_adapter_descriptor("provider.unknown")
    assert caught.value.failure is OptionalAdapterFailure.UNSUPPORTED_ADAPTER
    assert caught.value.adapter_id == "provider.unknown"


@pytest.mark.parametrize(
    ("statement", "adapter_id", "dependency"),
    (
        (
            "from tiaf.market_intelligence.providers import YahooMcpClient",
            "provider.market-intelligence.yahoo-mcp",
            "mcp",
        ),
        (
            "from tiaf.market_intelligence.providers import HttpxOfficialDocumentTransport",
            "provider.market-intelligence.authoritative-http",
            "httpx",
        ),
        (
            "from tiaf.data.providers import DhanMarketDataProvider",
            "provider.market-data.dhan",
            "pydantic_settings",
        ),
    ),
)
def test_selected_missing_adapter_fails_typed_at_its_boundary(
    statement: str,
    adapter_id: str,
    dependency: str,
) -> None:
    result = _isolated(
        f"""
from tiaf.optional_adapters import OptionalAdapterError, OptionalAdapterFailure
try:
    {statement}
except OptionalAdapterError as exc:
    assert exc.failure is OptionalAdapterFailure.OPTIONAL_DEPENDENCY_MISSING
    assert exc.adapter_id == {adapter_id!r}
    assert exc.dependency == {dependency!r}
else:
    raise AssertionError("selected adapter unexpectedly loaded")
"""
    )
    assert result.returncode == 0, result.stderr


def test_missing_yahoo_sdk_does_not_silently_select_tapetide() -> None:
    result = _isolated(
        """
from tiaf.optional_adapters import OptionalAdapterError, optional_adapter_catalog
before = optional_adapter_catalog()
try:
    from tiaf.market_intelligence.providers import YahooMcpClient
except OptionalAdapterError as exc:
    assert exc.adapter_id == "provider.market-intelligence.yahoo-mcp"
else:
    raise AssertionError("selected adapter unexpectedly loaded")
assert "tiaf.market_intelligence.providers.tapetide_mcp" not in sys.modules
assert optional_adapter_catalog() == before
"""
    )
    assert result.returncode == 0, result.stderr


def test_serial_workflow_and_recorded_replay_remain_framework_free() -> None:
    from scripts._a3_8_fixtures import request

    from tiaf.workflows import capture_json, default_registry, run_serial

    capture = capture_json(run_serial(request(), default_registry()))
    result = _isolated(
        """
from tiaf.workflows import replay_recorded
record = replay_recorded(sys.stdin.read())
assert record.result is not None
assert "langgraph" not in sys.modules
assert "langsmith" not in sys.modules
""",
        stdin=capture,
    )
    assert result.returncode == 0, result.stderr


def test_explicit_langgraph_selection_fails_typed_when_framework_is_missing() -> None:
    result = _isolated(
        """
from tiaf.optional_adapters import OptionalAdapterError, OptionalAdapterFailure
from tiaf.workflows.langgraph_adapter import run_langgraph
try:
    run_langgraph(None, None)
except OptionalAdapterError as exc:
    assert exc.failure is OptionalAdapterFailure.OPTIONAL_DEPENDENCY_MISSING
    assert exc.adapter_id == "workflow.langgraph"
    assert exc.dependency == "langgraph"
else:
    raise AssertionError("optional workflow unexpectedly loaded")
"""
    )
    assert result.returncode == 0, result.stderr


def test_unrelated_import_defect_is_not_hidden_as_missing_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken_import(module: str) -> None:
        del module
        raise ModuleNotFoundError("internal defect", name="unexpected_internal_module")

    monkeypatch.setattr("tiaf.optional_adapters.import_module", broken_import)
    with pytest.raises(ModuleNotFoundError, match="internal defect"):
        load_optional_attribute(
            adapter_id="provider.market-intelligence.yahoo-mcp",
            module="unused",
            attribute="unused",
            dependency_imports=("mcp",),
        )


def test_missing_adapter_export_is_typed_as_import_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "tiaf.optional_adapters.import_module",
        lambda module: SimpleNamespace(__name__=module),
    )
    with pytest.raises(OptionalAdapterError) as caught:
        load_optional_attribute(
            adapter_id="provider.market-intelligence.yahoo-mcp",
            module="installed_but_broken",
            attribute="MissingExport",
            dependency_imports=("mcp",),
        )
    assert caught.value.failure is OptionalAdapterFailure.OPTIONAL_ADAPTER_IMPORT_FAILED
    assert caught.value.adapter_id == "provider.market-intelligence.yahoo-mcp"


def test_optional_integrations_are_declared_as_extras_not_core_dependencies() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["dependencies"] == ["pydantic>=2.7,<3"]
    extras = project["optional-dependencies"]
    assert set(extras) >= {
        "data-provider-dhan",
        "market-intelligence-http",
        "market-intelligence-mcp",
        "orchestration",
        "providers",
    }
    assert "httpx>=0.27,<1" in extras["data-provider-dhan"]
    assert "mcp>=1.30,<2" in extras["market-intelligence-mcp"]
    assert "langgraph==1.2.11" in extras["orchestration"]


def test_existing_public_optional_exports_still_resolve_when_installed() -> None:
    import tiaf.data.providers as data_providers
    import tiaf.data.providers.dhan as dhan
    import tiaf.market_intelligence.providers as intelligence_providers

    assert data_providers.DhanMarketDataProvider is dhan.DhanMarketDataProvider
    assert intelligence_providers.YahooMcpClient.__name__ == "YahooMcpClient"
    assert (
        intelligence_providers.HttpxOfficialDocumentTransport.__name__
        == "HttpxOfficialDocumentTransport"
    )
