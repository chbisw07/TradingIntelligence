"""Cold imports, local-only admission and adversarial supplied-data boundaries."""

import builtins
import json
import socket
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_qualification import qualify_dataset
from tiaf.evaluation.forecast_research_contracts import EmpiricalDataset
from tiaf.evaluation.forecast_research_io import load_research_dataset
from tiaf.forecasting.engineering import EngineeringAdmissionError
from tiaf.forecasting.identity import canonical_json
from tiaf.forecasting.research_contracts import FF1FeatureSchema
from tiaf.forecasting.research_features import derive_features

from ._research_support import ASSESSMENT, dataset, payload, repin_rights
from .test_research_qualification import report


def test_fresh_process_no_optional_providers_ml_or_public_capability() -> None:
    code = """
import sys
blocked = {"httpx", "mcp", "dotenv", "numpy", "pandas", "sklearn", "torch",
           "tensorflow", "yfinance", "dhanhq"}
class Guard:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition(".")[0] in blocked:
            raise ModuleNotFoundError("blocked optional", name=fullname)
sys.meta_path.insert(0, Guard())
from tiaf.evaluation.forecast_qualification import qualify_dataset
from tiaf.evaluation.forecast_research_io import load_research_dataset
from tests.unit.forecasting._research_support import dataset, ASSESSMENT
from tiaf.facade import capability_catalog
assert qualify_dataset(dataset(), assessed_at=ASSESSMENT).eligible_observations == 11
assert len(capability_catalog()) == 9
assert not blocked.intersection(sys.modules)
assert not any(n.startswith(("tiaf.data.providers.dhan.client",
    "tiaf.market_intelligence.providers.yahoo_mcp",
    "tiaf.market_intelligence.providers.tapetide_mcp")) for n in sys.modules)
print("FF1_1_IMPORT_ISOLATION_PASS")
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", code], capture_output=True, text=True, timeout=30, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "FF1_1_IMPORT_ISOLATION_PASS" in result.stdout


def test_qualification_does_not_open_files_call_network_or_spawn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    supplied = dataset()

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("qualification attempted I/O")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    assert qualify_dataset(supplied, assessed_at=ASSESSMENT).eligible_observations == 11


def test_no_reference_or_future_feature_window_bypass(monkeypatch: pytest.MonkeyPatch) -> None:
    from tiaf.evaluation import forecast_qualification

    seen: list[int] = []

    def check_context(context, **kwargs):  # type: ignore[no-untyped-def]
        assert len(context.history.bars) == 21
        seen.append(len(context.history.bars))
        # A caller cannot pass target history under the earlier reference clock.
        with pytest.raises(ValueError, match="WINDOW_OR_CUTOFF"):
            derive_features(
                context,
                **{
                    **kwargs,
                    "reference_close_at": kwargs["reference_close_at"] - timedelta(days=1),
                },
            )
        return derive_features(context, **kwargs)

    monkeypatch.setattr(forecast_qualification, "derive_features", check_context)
    assert report().eligible_observations == 11
    assert len(seen) == 11


@pytest.mark.parametrize("variant", ["holiday", "special_saturday"])
def test_schedule_controls_weekends_and_holidays_not_weekday_heuristics(variant: str) -> None:
    data = payload()
    schedule = data["calendar"]["schedules"][0]
    if variant == "holiday":
        # Authored closure: deleting a schedule session and its bar is not a missing bar.
        removed = schedule["sessions"].pop(10)["session_id"]
        data["rows"].pop(10)
        data["reference_session_ids"].remove(removed)
        data["maturation"] = [m for m in data["maturation"] if m["target_session_id"] != removed]
    else:
        # Explicit authored special session replaces Friday with Saturday.
        schedule["sessions"][24]["opens_at"] = "2021-02-06T09:15:00+05:30"
        schedule["sessions"][24]["closes_at"] = "2021-02-06T15:30:00+05:30"
        data["rows"][24]["session_date"] = "2021-02-06"
        for key, minute in (
            ("observed_at", 30),
            ("available_at", 35),
            ("acquired_at", 36),
            ("admitted_at", 37),
        ):
            data["rows"][24]["provenance"][key] = f"2021-02-06T15:{minute}:00+05:30"
    schedule["exception_notice_refs"] = [schedule["source"]]
    result = report(data)
    assert result.verdicts == ("SYNTHETIC_ENGINEERING_ONLY",)
    assert result.eligible_observations == (10 if variant == "holiday" else 11)


def test_wrong_derivative_identity_remains_hashable_and_explicitly_blocked() -> None:
    data = payload()
    for instrument in (
        data["security"]["resolution"]["resolved"]["instrument"],
        data["security"]["resolution"]["matches"][0]["instrument"],
    ):
        instrument.update(instrument_type="FUTURE", expiry="2021-02-25", segment="NSE_FNO")
    assert "HOLD_SECURITY_IDENTITY" in report(data).verdicts


@pytest.mark.parametrize("facet", ["source", "rights", "security", "calendar", "actions"])
def test_material_qualification_pins_change_report(facet: str) -> None:
    data = payload()
    if facet == "source":
        data["source"]["capture"]["fingerprint"] = "f" * 64
    elif facet == "rights":
        data["rights"]["basis_refs"][0]["fingerprint"] = "f" * 64
        repin_rights(data)
    elif facet == "security":
        data["security"]["evidence"]["artifact"]["fingerprint"] = "f" * 64
    elif facet == "calendar":
        data["calendar"]["schedules"][0]["qualification_policy_ref"]["fingerprint"] = "f" * 64
    else:
        data["actions"][0]["evidence"]["artifact"]["fingerprint"] = "f" * 64
    first, other = report(), report(data)
    assert first.fingerprint != other.fingerprint
    assert first.feature_set_fingerprint != other.feature_set_fingerprint


def test_empirical_contract_branch_is_not_an_actual_data_qualification_claim() -> None:
    # Exercise contract vocabulary with authored values, never call this real empirical evidence.
    data = json.loads(canonical_json(dataset()).replace("SYNTHETIC_FIXTURE", "QUALIFIED_CAPTURE"))
    result = report(data)
    assert result.verdicts == ("QUALIFIED_FOR_FF1_RESEARCH",)
    assert not result.empirical_fitting_authorized


def test_empty_population_has_explicit_hold() -> None:
    data = payload()
    data["rows"] = []
    result = report(data)
    assert result.eligible_observations == 0 and result.excluded_observations == 32
    assert "HOLD_DATA_QUALITY" in result.verdicts


@pytest.mark.parametrize("fault", ["formula", "lookback", "order", "version", "imputation"])
def test_schema_cannot_silently_change(fault: str) -> None:
    schema = FF1FeatureSchema().model_dump(mode="json")
    if fault == "formula":
        schema["features"][0]["formula"] = "future_close"
    elif fault == "lookback":
        schema["features"][0]["input_bars"] = 1
    elif fault == "order":
        schema["features"].reverse()
    elif fault == "version":
        schema["feature_schema_version"] = "2.0"
    else:
        schema["missing_policy"] = "FILL_ZERO"
    with pytest.raises(ValidationError):
        FF1FeatureSchema.model_validate(schema)


def test_local_input_ignores_extra_source_columns_not_unknown_envelope_fields(
    tmp_path: Path,
) -> None:
    data = payload()
    data["rows"][0]["provider_unused_column"] = 99
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert load_research_dataset(path, dataset_id=dataset().dataset_id) == dataset()
    data["extra_envelope"] = "not-allowed"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_research_dataset(path, dataset_id=dataset().dataset_id)


@pytest.mark.parametrize("content", ['{"a":1,"a":2}', "NaN", "{}" * 600000])
def test_local_input_duplicate_keys_nonfinite_or_oversize_rejected(
    tmp_path: Path,
    content: str,
) -> None:
    path = tmp_path / "input.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(EngineeringAdmissionError):
        load_research_dataset(path, dataset_id="dataset:ff1-synthetic")


def test_unknown_timezone_and_duplicate_reference_ids_rejected() -> None:
    data = payload()
    data["source"]["source_timezone"] = "Not/A_Zone"
    with pytest.raises(ValidationError):
        EmpiricalDataset.model_validate(data)
    data = payload()
    data["reference_session_ids"].append(data["reference_session_ids"][0])
    with pytest.raises(ValidationError):
        EmpiricalDataset.model_validate(data)
