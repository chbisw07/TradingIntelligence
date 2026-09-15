"""FF-0.4 closed grammar, trusted file admission and full local command workflows."""

import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

from tiaf.forecasting import engineering
from tiaf.forecasting.clocks import SystemClock, read_clock
from tiaf.forecasting.engineering import main
from tiaf.forecasting.identity import canonical_json
from tiaf.forecasting.store import ForecastCorpusStore

from ._runtime_support import FixedClock
from ._support import instant
from .test_capture_store_replay import inventory

FIXTURES = Path(__file__).parents[2] / "fixtures/forecasting/ff0"


def local_config(tmp_path: Path) -> Path:
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    for source in FIXTURES.glob("reliance-s21-*.json"):
        (inputs / source.name).write_bytes(source.read_bytes())
    config = json.loads((FIXTURES / "local_config.json").read_text())
    config["corpus_root"] = str(tmp_path / "corpus")
    path = inputs / "config.json"
    path.write_text(json.dumps(config))
    return path


def invoke(
    capsys: pytest.CaptureFixture[str], config: Path, operation: str, *args: str
) -> tuple[dict[str, Any], int]:
    code = main([operation, "--config", str(config), *args])
    output = capsys.readouterr()
    assert not output.err
    payload = json.loads(output.out)
    assert payload["exit_code"] == code
    assert payload["schema_version"] == "1.0"
    assert payload["public_capability"] == "INTERNAL_ENGINEERING_CLI_ONLY"
    return payload, code


@pytest.mark.parametrize("args", [[], ["--help"], ["help"], ["run", "--help"]])
def test_help_never_reads_config_or_dispatches(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], args: list[str]
) -> None:
    def denied(*args: object, **kwargs: object) -> None:
        raise AssertionError("help attempted I/O")

    monkeypatch.setattr(engineering, "load_config", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    assert main(args) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["operation"] == "help" and "no live calls" in data["message"]


@pytest.mark.parametrize(
    "args",
    [
        ["run"],
        ["simulate"],
        ["train"],
        ["order"],
        ["delete"],
        ["forecast", "run"],
        ["run", "--mode", "ACTUAL_ISSUANCE"],
        ["run", "--now", "2026-02-04"],
        ["run", "--issued-at", "2026-02-04"],
        ["run", "--model", "evil.py"],
        ["run", "--input", "https://example.invalid/private"],
        ["run", "--input", "../private.json"],
        ["run", "--input", "os.system"],
        ["run", "--input", "ff:one", "--input", "ff:two"],
        ["run", "--input", "secret=private"],
        ["run", "--input", "$(private)"],
        ["run", "--config=private"],
        ["run", "--inp", "ff:one"],
    ],
)
def test_closed_grammar_redacts_invalid_authority_and_arguments(
    capsys: pytest.CaptureFixture[str], args: list[str]
) -> None:
    assert main(args) == 2
    output = capsys.readouterr()
    assert "private" not in output.out + output.err
    assert json.loads(output.out)["error_category"] == "COMMAND_CONFIG_ADMISSION"


@pytest.mark.parametrize(
    "variant,probability", [("actual", 0.6), ("simulated", 0.6), ("insufficient", None)]
)
def test_golden_command_pipeline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    variant: str,
    probability: float | None,
) -> None:
    from tiaf.forecasting import runtime

    clock = FixedClock(instant(4, 16, 6) if variant == "actual" else instant(9))
    monkeypatch.setattr(engineering, "SystemClock", lambda: clock)
    monkeypatch.setattr(runtime, "uuid4", lambda: UUID(int=1))
    monkeypatch.setattr(engineering, "uuid4", lambda: UUID(int=2))
    config = local_config(tmp_path)
    original_inputs = inventory(config.parent)
    generated, code = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-" + variant)
    assert code == 0
    result = generated["result"]
    assert result["probability"] == probability and result["support_count"] == (
        19 if probability is None else 20
    )
    assert result["status"] == ("UNAVAILABLE" if probability is None else "GENERATED")
    assert result["issued_at"] == (instant(4, 16, 6).isoformat() if variant == "actual" else None)
    assert result["computed_at"] == clock.at.isoformat()
    assert result["original_usage"]["local_cost"] == "UNPRICED"
    assert result["original_usage"]["attempts"] == 1
    for field in (
        "external_model_calls",
        "external_provider_calls",
        "input_model_tokens",
        "output_model_tokens",
        "external_model_cost",
    ):
        assert result["original_usage"][field] == 0
    # Fixed-ID/test-clock golden retains full scientific clocks and original usage.
    expected = json.loads(
        (Path(__file__).parents[2] / "acceptance/ff0/golden_results.json").read_text()
    )[variant]
    assert result["fingerprint"] == expected["result_fingerprint"]
    assert result["capture_id"] == expected["capture_id"]
    clock.at = instant(10)
    outcome, code = invoke(capsys, config, "outcome", "--input", "ff-outcome-input:reliance-s21-up")
    assert code == 0 and outcome["result"]["label"] == 1
    linked, code = invoke(
        capsys,
        config,
        "link",
        "--run",
        result["run_id"],
        "--outcome",
        outcome["result"]["outcome_id"],
    )
    assert code == 0
    assert linked["result"]["eligibility"] == (
        "NOT_EVALUABLE" if probability is None else "ENGINEERING_LINK_ELIGIBLE"
    )
    before = inventory(tmp_path / "corpus")
    for operation, suffix in (("inspect", ()), ("replay", ()), ("replay", ("--verify",))):
        viewed, code = invoke(capsys, config, operation, "--run", result["run_id"], *suffix)
        assert code == 0 and viewed["result"]["fingerprint"] == result["fingerprint"]
        assert viewed["result"]["computed_at"] == result["computed_at"]
        if suffix:
            assert viewed["result"]["verification"]["status"] == "VERIFIED"
            assert viewed["result"]["verification"]["usage"]["attempts"] == 1
        if operation == "inspect":
            assert len(viewed["result"]["links"]) == 1
    assert inventory(tmp_path / "corpus") == before
    assert inventory(config.parent) == original_inputs


@pytest.mark.parametrize(
    "fault",
    [
        "missing",
        "profile",
        "schema",
        "fingerprint",
        "symlink",
        "hardlink",
        "oversize",
        "overlap",
        "duplicate_ids",
        "remote_root",
        "secret",
        "fifo",
        "mode",
        "backdate",
        "leakage",
        "profile_mutation",
    ],
)
def test_trusted_input_failures_precede_any_inference_or_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], fault: str
) -> None:
    from tiaf.forecasting.forecasters import HistoricalBaseRateForecaster

    config = local_config(tmp_path)
    packet = config.parent / "reliance-s21-simulated.json"
    cfg = json.loads(config.read_text())
    if fault == "missing":
        packet.unlink()
    elif fault == "symlink":
        packet.rename(config.parent / "original.json")
        packet.symlink_to(config.parent / "original.json")
    elif fault == "hardlink":
        os.link(packet, config.parent / "other.json")
    elif fault == "oversize":
        packet.write_text(" " * 1_048_577)
    elif fault == "fifo":
        packet.unlink()
        os.mkfifo(packet)
    elif fault in (
        "profile",
        "schema",
        "secret",
        "mode",
        "backdate",
        "leakage",
        "profile_mutation",
    ):
        data = json.loads(packet.read_text())
        if fault == "profile":
            data["configuration"]["forecaster_id"] = "forecaster:unknown"
        elif fault == "schema":
            data["schema_version"] = "2.0"
        elif fault == "mode":
            data["request"]["realization_mode"] = "PRIVATE_LIVE"
        elif fault == "backdate":
            data["request"]["issued_at"] = instant(4).isoformat()
        elif fault == "leakage":
            data["request"]["information_cutoff"] = instant(10).isoformat()
        elif fault == "profile_mutation":
            data["configuration"]["minimum_support"] = 1
        else:
            data["api_key"] = "private-sentinel"
        packet.write_text(canonical_json(data))
        from tiaf.forecasting.identity import semantic_fingerprint

        for item in cfg["inputs"]:
            if item["filename"] == packet.name:
                item["fingerprint"] = semantic_fingerprint(data)
    elif fault == "fingerprint":
        packet.write_text(packet.read_text().replace('"eligible_count":20', '"eligible_count":19'))
    elif fault == "overlap":
        cfg["corpus_root"] = str(config.parent)
    elif fault == "duplicate_ids":
        cfg["inputs"].append(cfg["inputs"][0])
    else:
        cfg["input_root"] = "https://example.invalid/private"
    config.write_text(json.dumps(cfg))

    calls = 0

    def denied(*args: object, **kwargs: object) -> None:
        nonlocal calls
        calls += 1
        raise AssertionError("invalid input dispatched")

    monkeypatch.setattr(HistoricalBaseRateForecaster, "forecast", denied)
    output, code = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-simulated")
    assert code in (1, 2) and "private-sentinel" not in json.dumps(output)
    assert calls == 0
    assert not (tmp_path / "corpus").exists()


@pytest.mark.parametrize(
    "fault", ["capture", "outcome", "missing_blob", "partial", "lock", "schema"]
)
def test_corrupt_persisted_history_never_repairs_or_claims_replay(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fault: str
) -> None:
    config = local_config(tmp_path)
    run, _ = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-simulated")
    corpus = tmp_path / "corpus"
    path = corpus / "forecast_runs.jsonl"
    if fault == "missing_blob":
        next((corpus / "artifacts").glob("*.json")).unlink()
    elif fault == "partial":
        path.write_bytes(path.read_bytes() + b'{"partial":')
    elif fault == "lock":
        (corpus / ".writer.lock").write_text("retained")
    elif fault == "outcome":
        (corpus / "outcome_records.jsonl").write_text('{"invalid":true}\n')
    else:
        original = path.read_text()
        path.write_text(
            original.replace('"probability":0.6', '"probability":0.7')
            if fault == "capture"
            else original.replace('"schema_version":"1.0"', '"schema_version":"9.0"', 1)
        )
    before = inventory(corpus)
    data, code = invoke(capsys, config, "replay", "--run", run["result"]["run_id"], "--verify")
    assert code == 1 and "error_category" in data
    assert inventory(corpus) == before


def test_real_cli_simulates_but_cannot_backdate_and_repeated_run_is_new(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = local_config(tmp_path)
    first, code = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-simulated")
    second, _ = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-simulated")
    assert code == 0 and first["result"]["run_id"] != second["result"]["run_id"]
    assert first["result"]["issued_at"] is None
    actual, code = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-actual")
    assert code == 0 and actual["result"]["status"] == "UNAVAILABLE"
    assert actual["result"]["issued_at"] is None
    assert actual["result"]["original_usage"]["attempts"] == 0


def test_fresh_process_cli_runs_without_optional_dependencies_or_live_calls(tmp_path: Path) -> None:
    config = local_config(tmp_path)
    code = r"""
import importlib.abc, socket, sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        banned=('numpy','sklearn','xgboost','torch','tensorflow','mcp','httpx','requests',
                'openai','langgraph','langsmith','dotenv','dhanhq','yfinance')
        if fullname.split('.')[0] in banned: raise AssertionError('optional import: '+fullname)
sys.meta_path.insert(0,Block())
def denied(*args,**kwargs): raise AssertionError('network')
socket.create_connection=denied
socket.socket.connect=denied
from tiaf.forecasting.engineering import main
assert main(['run','--config',sys.argv[1],'--input','ff-request:reliance-s21-simulated'])==0
from tiaf.facade.capabilities import capability_discovery_catalog
assert len(capability_discovery_catalog())==9
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", code, str(config)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["result"]["probability"] == 0.6


def test_persistence_failure_and_deadline_have_failure_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tiaf.forecasting.errors import ForecastStoreError

    config = local_config(tmp_path)
    monkeypatch.setattr(engineering, "SystemClock", lambda: FixedClock(instant(9), step=1.1))
    result, code = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-simulated")
    assert code == 1 and result["result"]["status"] == "FAILED"
    assert result["result"]["original_usage"]["attempts"] == 1

    def failed(*args: object, **kwargs: object) -> None:
        raise ForecastStoreError("private disk path")

    monkeypatch.setattr(ForecastCorpusStore, "append_forecast", failed)
    result, code = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-simulated")
    assert code == 1 and result["error_category"] == "PERSISTENCE_ACCESS"
    assert "private disk" not in json.dumps(result)


def test_golden_resealed_tamper_is_not_a_successful_verification(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from tiaf.forecasting.capture import ForecastCapture
    from tiaf.forecasting.contracts import ForecastResult
    from tiaf.forecasting.store import StoreOwner

    config = local_config(tmp_path)
    run, _ = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-simulated")
    original_store = ForecastCorpusStore(
        tmp_path / "corpus", as_of=read_clock(SystemClock())
    )
    original = original_store.get_forecast(run["result"]["run_id"])
    original_bytes = inventory(original_store.root)
    data = original.result.model_dump(mode="json", exclude={"replay_fingerprint"})
    data["output"]["probability"] = 0.7
    altered = ForecastResult.model_validate(data)
    capture_data = original.model_dump(mode="json", exclude={"capture_id"})
    capture_data["result"] = altered.model_dump(mode="json")
    resealed = ForecastCapture.model_validate(capture_data)
    target = ForecastCorpusStore(
        tmp_path / "resealed",
        as_of=read_clock(SystemClock()),
        owner=StoreOwner.FORECAST,
    )
    target.append_forecast(resealed, original_store.get_forecast_artifacts(original.result.run_id))
    cfg = json.loads(config.read_text())
    cfg["corpus_root"] = str(target.root)
    config.write_text(json.dumps(cfg))
    before = inventory(target.root)
    replay, code = invoke(capsys, config, "replay", "--run", original.result.run_id)
    assert code == 0 and replay["result"]["probability"] == 0.7
    verified, code = invoke(capsys, config, "replay", "--run", original.result.run_id, "--verify")
    expected = json.loads(
        (Path(__file__).parents[2] / "acceptance/ff0/golden_results.json").read_text()
    )["tampered"]
    assert code == expected["exit_code"]
    assert verified["result"]["verification"]["status"] == expected["verification"]
    assert inventory(target.root) == before
    assert inventory(original_store.root) == original_bytes
    assert expected["original_record_mutated"] is False


def test_missing_pinned_verifier_has_failure_exit_without_changing_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tiaf.forecasting import forecasters
    from tiaf.forecasting.errors import ForecastIntegrityError

    config = local_config(tmp_path)
    run, _ = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-simulated")
    before = inventory(tmp_path / "corpus")

    def denied(*args: object, **kwargs: object) -> None:
        raise ForecastIntegrityError("private missing implementation")

    monkeypatch.setattr(forecasters, "resolve_forecaster", denied)
    checked, code = invoke(capsys, config, "replay", "--run", run["result"]["run_id"], "--verify")
    assert code == 1 and checked["result"]["verification"]["status"] == "UNVERIFIABLE"
    assert "private" not in json.dumps(checked)
    replay, code = invoke(capsys, config, "replay", "--run", run["result"]["run_id"])
    assert code == 0 and replay["result"]["fingerprint"] == run["result"]["fingerprint"]
    assert inventory(tmp_path / "corpus") == before


@pytest.mark.parametrize(
    "identifier", ["../private", "os.system", "https://example.invalid", "ff:unknown"]
)
def test_bad_logical_input_with_otherwise_complete_command(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], identifier: str
) -> None:
    config = local_config(tmp_path)
    result, code = invoke(capsys, config, "run", "--input", identifier)
    assert code == 2 and result["error_category"] == "COMMAND_CONFIG_ADMISSION"
    assert not (tmp_path / "corpus").exists()


def test_fresh_process_cli_replay_blocks_runtime_and_keeps_public_grammar_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = local_config(tmp_path)
    run, _ = invoke(capsys, config, "run", "--input", "ff-request:reliance-s21-simulated")
    before = inventory(tmp_path / "corpus")
    code = r"""
import importlib.abc, socket, sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        banned=('tiaf.forecasting.runtime','tiaf.forecasting.forecasters',
                'tiaf.forecasting.support','tiaf.forecasting.engineering_inputs',
                'tiaf.evaluation.forecast_truth','numpy','sklearn','xgboost',
                'torch','tensorflow','mcp','httpx','requests','openai','dhanhq','yfinance')
        if any(fullname==p or fullname.startswith(p+'.') for p in banned):
            raise AssertionError('forbidden import: '+fullname)
sys.meta_path.insert(0,Block())
def denied(*args,**kwargs): raise AssertionError('network')
socket.create_connection=denied
socket.socket.connect=denied
from tiaf.forecasting.engineering import main
assert main(['replay','--config',sys.argv[1],'--run',sys.argv[2]])==0
from tiaf.facade.capabilities import capability_discovery_catalog
assert len(capability_discovery_catalog())==9
from tiaf.shell.parser import parse_tokens
from tiaf.shell.errors import ShellError
try: parse_tokens(['forecast','run'])
except ShellError: pass
else: raise AssertionError('public grammar expanded')
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", code, str(config), run["result"]["run_id"]],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["result"]["fingerprint"] == run["result"]["fingerprint"]
    assert inventory(tmp_path / "corpus") == before


def test_registered_packets_match_reviewed_synthetic_authoring(tmp_path: Path) -> None:
    from importlib import import_module

    from tiaf.forecasting.identity import semantic_fingerprint

    support = import_module("tests.acceptance.ff0._support")
    packets = support.authored_inputs(tmp_path / "authoring")
    config = support.config_for(packets, Path("/tmp/tiaf-ff0-miniature"))
    checked = engineering.EngineeringConfig.model_validate_json(
        (FIXTURES / "local_config.json").read_text()
    )
    assert config == checked
    for packet in packets:
        row = next(i for i in checked.inputs if i.input_id == packet.input_id)
        saved = json.loads((FIXTURES / row.filename).read_text())
        assert semantic_fingerprint(saved) == row.fingerprint == semantic_fingerprint(packet)
