from pathlib import Path

from tiaf.market_intelligence import MarketIntelligenceCapability

ROOT = Path(__file__).resolve().parents[3]


def test_core_package_import_does_not_eagerly_import_provider_adapters() -> None:
    init_source = (ROOT / "src/tiaf/market_intelligence/__init__.py").read_text()
    assert "providers.tapetide" not in init_source
    assert "providers.yahoo" not in init_source
    assert MarketIntelligenceCapability.READ_FINANCIALS.value == "READ_FINANCIALS"


def test_specialists_do_not_import_provider_adapters_or_mcp() -> None:
    specialists = ROOT / "src/tiaf/agents/specialists"
    source = "\n".join(path.read_text() for path in specialists.rglob("*.py"))
    assert "tapetide" not in source.casefold()
    assert "yahoo" not in source.casefold()
    assert "market_intelligence.providers" not in source
    assert "mcp" not in source.casefold()


def test_domain_contracts_have_no_transport_dependency() -> None:
    for relative in (
        "src/tiaf/market_intelligence/models.py",
        "src/tiaf/market_intelligence/graph.py",
        "src/tiaf/market_intelligence/research.py",
    ):
        source = (ROOT / relative).read_text().casefold()
        assert "import httpx" not in source
        assert "import mcp" not in source
        assert "tapetide" not in source
        assert "yahoo" not in source


def test_mcp_sdk_import_is_confined_to_connector_module() -> None:
    package = ROOT / "src/tiaf/market_intelligence"
    importers = {
        path.relative_to(ROOT).as_posix()
        for path in package.rglob("*.py")
        if "from mcp import" in path.read_text() or "from mcp." in path.read_text()
    }
    assert importers == {
        "src/tiaf/market_intelligence/providers/tapetide_mcp.py",
        "src/tiaf/market_intelligence/providers/yahoo_mcp.py",
    }
