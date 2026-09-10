"""Black-box coordinator, adapter, budget and replay acceptance."""

from scripts._a3_8_fixtures import financial_services, request

from tiaf.workflows import capture_json, default_registry, run_serial, verify_deterministic
from tiaf.workflows.langgraph_adapter import run_langgraph


def test_serial_and_langgraph_rich_snapshot_parity() -> None:
    req = request()
    serial = run_serial(req, default_registry())
    parallel = run_langgraph(req, default_registry())
    assert serial.fingerprint == parallel.fingerprint
    assert serial.result.provider_calls == 0
    assert len(serial.attempts) == 8
    assert all(a.record is not None for a in serial.attempts)
    assert len(serial.result.opinions) >= 3
    assert serial.result.usage.llm_calls == 0
    assert verify_deterministic(capture_json(serial), default_registry()) == serial


def test_missing_financial_capability_acquired_once_and_replayed() -> None:
    req = request(financials=False)
    record = run_serial(req, default_registry(), financial_services(req))
    assert record.result.provider_calls == 1
    assert len(record.artifacts) == 1
    assert any(r.evidence_type.value == "FUNDAMENTAL" for r in record.inventories[-1].references)
    assert verify_deterministic(capture_json(record), default_registry()) == record


def test_rate_limit_uses_existing_provider_fabric() -> None:
    req = request(financials=False)
    record = run_serial(req, default_registry(), financial_services(req, fallback=True))
    assert record.result.provider_calls == 2
    assert "RATE_LIMITED" in record.artifacts[0].canonical_json
    assert "yahoo" in record.artifacts[0].canonical_json
