from pathlib import Path

from tiaf.facade import capability_catalog


def test_a6_3_catalog_contains_ninth_published_expression_capability() -> None:
    capabilities = tuple(item.capability_id for item in capability_catalog())
    assert len(capabilities) == 9
    assert "expression.assess" in capabilities


def test_trade_expression_boundary_has_no_provider_model_broker_or_specialist_imports() -> None:
    root = Path("src/tiaf/trade_expression")
    source = "\n".join(path.read_text() for path in root.glob("*.py"))
    forbidden = (
        "tiaf.providers",
        "tiaf.specialists",
        "dhanhq",
        "yahoo",
        "tapetide",
        "mcp",
        "openai",
        "broker",
    )
    assert not any(f"import {name}" in source or f"from {name}" in source for name in forbidden)


def test_a5_runtime_files_are_not_part_of_a6_namespace() -> None:
    assert not any(Path("src/tiaf/trade_expression").glob("*position*"))
