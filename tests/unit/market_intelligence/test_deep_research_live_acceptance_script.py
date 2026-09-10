import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, cast

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts/deep_research_live_acceptance.py"
SPEC = spec_from_file_location("tiaf_deep_research_live_acceptance", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
live = cast(Any, module_from_spec(SPEC))
sys.modules[SPEC.name] = live
SPEC.loader.exec_module(live)


def test_deep_research_live_acceptance_requires_explicit_live_flag(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        live,
        "YahooMcpClient",
        lambda: (_ for _ in ()).throw(AssertionError("connector constructed")),
    )
    assert live.main([]) == 0
    assert "disabled" in capsys.readouterr().out


def test_live_matrix_is_bounded_and_covers_required_symbols() -> None:
    assert {item.symbol for item in live.SCENARIOS} == {
        "RELIANCE",
        "HDFCBANK",
        "KAYNES",
        "ATHERENERG",
    }
    maximum_acquisition_calls = sum(
        2 if capability.value == "READ_FINANCIALS" else 1
        for item in live.SCENARIOS
        for capability in item.capabilities
    )
    assert maximum_acquisition_calls + 1 <= 12


def test_live_script_uses_existing_adapters_and_has_no_mutation_operations() -> None:
    source = SCRIPT.read_text().casefold()
    assert "yahoomarketintelligenceprovider" in source
    assert "tapetidemarketintelligenceprovider" in source
    assert "authoritativeconfirmationgateway" in source
    assert all(token not in source for token in (".post(", ".put(", ".delete(", "place_order"))
