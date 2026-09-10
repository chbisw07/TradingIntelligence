import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, cast

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts/authoritative_live_acceptance.py"
SPEC = spec_from_file_location("tiaf_authoritative_live_acceptance", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
live = cast(Any, module_from_spec(SPEC))
sys.modules[SPEC.name] = live
SPEC.loader.exec_module(live)


def test_authoritative_live_acceptance_requires_explicit_live_flag(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert live.main([]) == 0
    assert "disabled" in capsys.readouterr().out


def test_authoritative_live_acceptance_is_bounded_to_three_https_reads() -> None:
    assert len(live.CASES) == 3
    assert all(item.source_url.startswith("https://") for item in live.CASES)
    assert {item.source_id for item in live.CASES} == {
        "nse_official",
        "bse_official",
        "reliance_ir",
    }


def test_authoritative_live_script_contains_no_mutation_or_broker_operation() -> None:
    source = (
        Path(__file__).resolve().parents[3] / "scripts/authoritative_live_acceptance.py"
    ).read_text().casefold()
    assert "broker" not in source
    assert all(token not in source for token in (".post(", ".put(", ".delete(", "captcha"))
