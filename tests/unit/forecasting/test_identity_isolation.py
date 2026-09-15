"""FF0-01/18/23/26 foundation: identity is not a replay engine or issuance proof."""

import builtins
import hashlib
import json
import socket
import subprocess
import sys
from decimal import Decimal, localcontext
from pathlib import Path

import pytest
from pydantic import ValidationError

from tiaf.forecasting.contracts import ForecastRequest, ForecastResult
from tiaf.forecasting.identity import ArtifactReference, canonical_json, semantic_fingerprint
from tiaf.planner.digests import digest

from ._support import instant, ref, request, result, source
from .test_contracts import changed


def test_golden_contract_fingerprints_are_explicit_synthetic_specimens() -> None:
    assert (
        result().replay_fingerprint
        == "0130acc66a1defbaa16fd20afda61fde6666dccc7d52ce0a2f1df918a2a52dfc"
    )
    assert (
        result(simulated=True).replay_fingerprint
        == "a595b8eb9adab3b1620a5ffbe8be34c31c677d24f7916cd5498ee052f9878eb4"
    )


def test_canonical_profile_reuses_existing_digest_and_preserves_precision() -> None:
    payload = {"z": [1, 0, None], "text": "₹", "price": Decimal("105.000")}
    encoded = canonical_json(payload)
    assert encoded == '{"price":"105","text":"\\u20b9","z":[1,0,null]}'
    assert semantic_fingerprint(payload) == hashlib.sha256(encoded.encode()).hexdigest()
    assert semantic_fingerprint(payload) == digest(json.loads(encoded))
    exact = Decimal("123456789012345678901234567890.0012300")
    with localcontext() as context:
        context.prec = 3
        assert canonical_json(exact) == '"123456789012345678901234567890.00123"'
    assert canonical_json(Decimal("-0.000")) == '"0"'


@pytest.mark.parametrize("value", [float("nan"), float("inf"), Decimal("NaN"), {1: "x"}])
def test_canonical_profile_rejects_nonfinite_and_ambiguous_keys(value: object) -> None:
    with pytest.raises(ValueError):
        canonical_json(value)


def test_mapping_construction_and_unordered_reference_order_do_not_change_identity() -> None:
    req = ForecastRequest.model_validate(
        changed(
            request(),
            {
                "evidence": [
                    source("b").model_dump(mode="json"),
                    source("a").model_dump(mode="json"),
                ],
            },
        )
    )
    data = req.model_dump(mode="json")
    reordered = dict(reversed(tuple(data.items())))
    reordered["evidence"] = list(reversed(data["evidence"]))
    rebuilt = ForecastRequest.model_validate(reordered)
    assert rebuilt == req and rebuilt.semantic_fingerprint == req.semantic_fingerprint


@pytest.mark.parametrize(
    "changes",
    [
        {"request_id": "ff-request:another"},
        {"information_cutoff": "2026-02-04T16:01:00+05:30"},
        {"as_of": "2026-02-04T16:04:00+05:30"},
        {"evidence_ref": ref("different-input-capture").model_dump(mode="json")},
        {"profile_ref": ref("different-profile").model_dump(mode="json")},
    ],
)
def test_material_request_change_changes_identity(changes: dict[str, object]) -> None:
    req = request()
    revised = ForecastRequest.model_validate(changed(req, changes))
    assert req.semantic_fingerprint != revised.semantic_fingerprint


def test_target_version_is_hashed_even_though_unaccepted_version_is_not_admitted() -> None:
    target = request().target.model_dump(mode="json")
    revised = {**target, "target_version": "2.0"}
    assert semantic_fingerprint(target) != semantic_fingerprint(revised)
    with pytest.raises(ValidationError):
        type(request().target).model_validate(revised)


@pytest.mark.parametrize(
    "changes",
    [
        {"result_id": "ff-result:another"},
        {"run_id": "ff-run:another"},
        {"computed_at": "2026-02-04T16:05:30+05:30"},
        {"issued_at": "2026-02-04T16:08:00+05:30"},
        {"output.probability": 0.4},
        {"artifact_identity.code_ref": ref("other-build").model_dump(mode="json")},
    ],
)
def test_material_result_and_original_clocks_change_fingerprint(changes: dict[str, object]) -> None:
    original = result()
    other = ForecastResult.model_validate(changed(original, changes))
    assert other.replay_fingerprint != original.replay_fingerprint


def test_mode_changes_capture_not_common_observation_and_no_generated_run_id() -> None:
    actual, simulated = request(), request(simulated=True)
    assert actual.semantic_fingerprint != simulated.semantic_fingerprint
    assert actual.observation_id == simulated.observation_id
    another = ForecastRequest.model_validate(
        changed(actual, {"request_id": "ff-request:duplicate"})
    )
    assert another.observation_id == actual.observation_id
    # Contracts never allocate a new runtime identity or sample the clock.
    out = result()
    assert ForecastResult.model_validate_json(out.model_dump_json()) == out


def test_supplied_fingerprint_tampering_is_rejected() -> None:
    payload = result().model_dump(mode="json")
    payload["output"]["probability"] = 0.4
    with pytest.raises(ValidationError, match="fingerprint"):
        ForecastResult.model_validate(payload)


@pytest.mark.parametrize(
    "identity",
    [
        "/tmp/model",
        "file:///tmp/model",
        "https://example.com",
        "x:../m",
        "x:folder/m",
        "x:folder\\m",
    ],
)
def test_artifact_references_cannot_be_paths_or_urls(identity: str) -> None:
    with pytest.raises(ValidationError):
        ArtifactReference.model_validate({**ref("safe").model_dump(), "artifact_id": identity})


def test_no_contract_validation_io_or_broker_authority(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = result().model_dump(mode="json")

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("contract attempted external or filesystem I/O")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    restored = ForecastResult.model_validate(payload)
    assert restored.issued_at == instant(4, 16, 7)
    assert restored.authority == "NO_ACTION_AUTHORITY"
    forbidden_fields = {
        "order",
        "order_id",
        "execution",
        "broker_account",
        "model_path",
        "python_import",
    }
    assert not forbidden_fields.intersection(ForecastResult.model_fields)
    assert not forbidden_fields.intersection(ForecastRequest.model_fields)


def test_fresh_imports_do_not_require_optional_sdks_or_concrete_providers() -> None:
    code = """
import sys
blocked = {"httpx", "mcp", "dotenv", "pydantic_settings", "langgraph", "langsmith",
           "numpy", "pandas", "sklearn", "xgboost", "torch", "tensorflow", "yfinance"}
class Guard:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition(".")[0] in blocked:
            raise ModuleNotFoundError("blocked optional", name=fullname)
sys.meta_path.insert(0, Guard())
from tiaf.forecasting.contracts import ForecastRequest, ForecastResult
from tiaf.evaluation.forecast_contracts import ForecastTargetSpec
from tests.unit.forecasting._support import result
from tiaf.facade import capability_catalog
assert result().replay_fingerprint
assert len(capability_catalog()) == 9
assert not blocked.intersection(sys.modules)
assert not any(name.startswith(("tiaf.data.providers.dhan.client",
    "tiaf.market_intelligence.providers.yahoo_mcp",
    "tiaf.market_intelligence.providers.tapetide_mcp"))
    for name in sys.modules)
print("FF0_IMPORT_ISOLATION_PASS")
"""
    process = subprocess.run(
        [sys.executable, "-B", "-c", code],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parents[3],
        timeout=30,
        check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    assert "FF0_IMPORT_ISOLATION_PASS" in process.stdout
