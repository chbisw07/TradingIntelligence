"""Black-box checks for the deterministic A3.7 user acceptance operation."""

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, cast

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts/a3_7_user_acceptance.py"
SPEC = spec_from_file_location("tiaf_a37_user_acceptance", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
acceptance = cast(Any, module_from_spec(SPEC))
sys.modules[SPEC.name] = acceptance
SPEC.loader.exec_module(acceptance)


def test_user_acceptance_runs_all_six_scenarios_without_external_access(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert acceptance.main() == 0
    output = capsys.readouterr().out

    assert "Scenarios passed: 6 / 6" in output
    assert "Forbidden structured fields/actions: NONE" in output
    assert "LLM calls/tokens/cost units: 0 / 0 / 0" in output
    assert "Exact offline record replay and fingerprint preservation: PASS" in output


def test_acceptance_profiles_cover_required_behavior_and_instruments() -> None:
    scenarios = acceptance.scenarios()

    assert tuple(item.code for item in scenarios) == ("A", "B", "C", "D", "E", "F")
    assert any(item.instrument_type.value == "INDEX" for item in scenarios)
    assert any(item.trade_style.value == "DAY" for item in scenarios)
    assert any(item.expect_missing for item in scenarios)
    assert any(item.expect_contradiction for item in scenarios)


def test_acceptance_script_uses_public_runtime_and_has_no_provider_or_action_path() -> None:
    source = SCRIPT.read_text()

    assert "AgentRuntime" in source and "AgentRegistry" in source
    assert "tiaf.data.providers" not in source
    assert "DhanMarketDataProvider" not in source
    assert "OptionExpression" not in source
    assert "PositionAction" not in source
    assert "ReasoningGateway" not in source
