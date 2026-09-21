"""Mock-only acceptance for the internal TI-native research exporter."""

import csv
import io
import json
import sys
from datetime import UTC, datetime
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, cast

import pytest

from tiaf.data import ProviderAuthError, ProviderBadResponseError
from tiaf.data.providers.dhan import DhanMarketDataProvider
from tiaf.data.resolution import ResolutionResult

from ._instrument_master_support import MASTER_CSV, resolver_at
from ._support import RecordingTransport, dhan_config

SCRIPT = Path(__file__).resolve().parents[5] / "scripts/provision_reliance_test_data.py"
SPEC = spec_from_file_location("research_provisioner", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
live = cast(Any, module_from_spec(SPEC))
sys.modules[SPEC.name] = live
SPEC.loader.exec_module(live)
NOW = datetime(2026, 9, 21, 1, tzinfo=live.TIAF_TIMEZONE)


def resolved(tmp_path: Path) -> ResolutionResult:
    # Demonstrates dynamic identity rather than a hard-coded production security ID.
    (tmp_path / "dhan.csv").write_bytes(MASTER_CSV.replace(b"2885", b"123456"))
    resolver, downloader = resolver_at(tmp_path, body=MASTER_CSV.replace(b"2885", b"123456"))
    result = cast(ResolutionResult, live.resolve_identity(resolver))
    assert downloader.calls == []
    assert result.resolved is not None and result.resolved.provider_instrument_id == "123456"
    return result


def response() -> dict[str, Any]:
    return {
        "timestamp": [
            int(datetime(2020, 1, day, 9, 15, tzinfo=live.TIAF_TIMEZONE).timestamp())
            for day in (3, 2)
        ],
        "open": [110, 100],
        "high": [113, 103],
        "low": [109, 99],
        "close": [112, 102],
        "volume": [0, 1234],
        "unused_provider_field": "fixture-sensitive-value-never-exported",
    }


def acquire(tmp_path: Path, data: dict[str, Any] | None = None) -> tuple[Any, RecordingTransport]:
    resolution = resolved(tmp_path)
    transport = RecordingTransport(lambda path, payload: response() if data is None else data)
    provider = DhanMarketDataProvider(dhan_config(), transport=transport, clock=lambda: NOW)
    result = live.provision(
        provider,
        resolution,
        root=tmp_path,
        master_sha256="a" * 64,
        resolved_at=NOW,
        clock=lambda: NOW,
    )
    return result, transport


def test_no_live_flag_performs_no_bootstrap_or_provider_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("unexpected bootstrap")

    monkeypatch.setattr(live, "Settings", fail)
    monkeypatch.setattr(live, "DhanMarketDataProvider", fail)
    assert live.main([]) == 0


def test_native_provider_export_and_only_one_historical_request(tmp_path: Path) -> None:
    manifest, transport = acquire(tmp_path)
    assert transport.calls == [
        (
            "/charts/historical",
            {
                "securityId": "123456",
                "exchangeSegment": "NSE_EQ",
                "instrument": "EQUITY",
                "oi": False,
                "fromDate": "2017-11-01",
                "toDate": "2026-02-01",
            },
        )
    ]
    output = tmp_path / "data/ff1/reliance"
    raw = (output / "reliance_daily_ohlcv.csv").read_bytes()
    rows = list(csv.DictReader(io.StringIO(raw.decode())))
    assert list(rows[0]) == list(live.HEADER)
    assert [r["date"] for r in rows] == ["2020-01-02", "2020-01-03"]
    assert rows[1]["volume"] == "0"
    assert len(list(output.iterdir())) == 5
    source = json.loads((output / "source_manifest.json").read_text())
    assert source["row_count"] == 2 and source["duplicate_sessions"] == 0
    assert source["rights_evidence_status"] == "UNVERIFIED"
    assert source["rights_enforcement_policy"] == "WARN_ONLY"
    assert source["rights_admission_result"] == "ADMITTED_WITH_WARNING"
    assert source["acquisition_kind"] == "FRESH_HISTORICAL_DOWNLOAD"
    assert source["acquired_at"] == NOW.isoformat()
    assert source["price_basis"] == source["historical_availability_semantics"] == "UNKNOWN"
    assert not manifest["empirical_fitting_authorized"]
    for file in output.iterdir():
        text = file.read_text()
        assert "test-token-value" not in text and "test-client-id" not in text
        assert "fixture-sensitive-value" not in text
        assert file.stat().st_mode & 0o777 == 0o600
    live.verify_package(output)
    assert len(transport.calls) == 1  # Offline verification adds no live request.


@pytest.mark.parametrize(
    "fault",
    [
        "duplicate",
        "invalid_ohlc",
        "negative_volume",
        "missing_volume",
        "missing_close",
        "nonfinite",
        "empty",
        "outside",
    ],
)
def test_invalid_transport_does_not_publish_final_csv(tmp_path: Path, fault: str) -> None:
    data = response()
    if fault == "duplicate":
        data["timestamp"][1] = data["timestamp"][0]
    elif fault == "invalid_ohlc":
        data["high"][0] = 1
    elif fault == "negative_volume":
        data["volume"][0] = -1
    elif fault == "missing_volume":
        data["volume"][0] = None
    elif fault == "missing_close":
        del data["close"]
    elif fault == "nonfinite":
        data["high"][0] = float("inf")
    elif fault == "outside":
        data["timestamp"][0] = int(NOW.timestamp())
    else:
        data = {key: [] for key in ("timestamp", "open", "high", "low", "close", "volume")}
    with pytest.raises((ProviderBadResponseError, live.ProvisioningError)):
        acquire(tmp_path, data)
    assert not (tmp_path / "data/ff1/reliance").exists()


@pytest.mark.parametrize("fault", ["bse", "future", "wrong_symbol", "id_mismatch", "ambiguous"])
def test_wrong_resolution_is_rejected_before_history(tmp_path: Path, fault: str) -> None:
    result = resolved(tmp_path)
    assert result.resolved is not None
    match = result.resolved
    instrument = match.instrument.model_dump(mode="json")
    if fault == "bse":
        instrument.update(exchange="BSE", segment="BSE_EQUITY")
    elif fault == "future":
        instrument.update(instrument_type="FUTURE", segment="NSE_FNO")
    elif fault == "wrong_symbol":
        instrument["symbol"] = "KAYNES"
    elif fault == "id_mismatch":
        instrument["provider_instrument_id"] = "other"
    changed = match.model_copy(update={"instrument": match.instrument.model_validate(instrument)})
    wrong = result.model_copy(
        update={"resolved": changed, "matches": (changed,), "ambiguous": fault == "ambiguous"}
    )
    transport = RecordingTransport(lambda path, payload: pytest.fail("unexpected history call"))
    provider = DhanMarketDataProvider(dhan_config(), transport=transport)
    with pytest.raises(live.ProvisioningError, match="RESOLUTION"):
        live.provision(provider, wrong, root=tmp_path, master_sha256="a" * 64, resolved_at=NOW)
    assert not transport.calls


def test_deterministic_chunk_merge_order_hash_and_utc_daily_date(tmp_path: Path) -> None:
    result = resolved(tmp_path)
    assert result.resolved is not None
    instrument = result.resolved.instrument
    transport = RecordingTransport(lambda path, payload: response())
    provider = DhanMarketDataProvider(dhan_config(), transport=transport)
    full = provider.get_historical(instrument, "1d", live.START, live.END)
    first = full.model_copy(update={"bars": full.bars[:1]})
    second = full.model_copy(update={"bars": full.bars[1:]})
    csv_text = live.canonical_csv((second, first), instrument)
    assert csv_text == live.canonical_csv((full,), instrument)
    assert live.exact_bytes_checksum(csv_text) == live.exact_bytes_checksum(
        live.canonical_csv((first, second), instrument)
    )
    utc = full.model_copy(
        update={
            "bars": tuple(
                b.model_copy(update={"start_at": b.start_at.astimezone(UTC)}) for b in full.bars
            )
        }
    )
    assert live.canonical_csv((utc,), instrument) == csv_text
    with pytest.raises(live.ProvisioningError, match="DUPLICATE"):
        live.canonical_csv((first, first), instrument)


@pytest.mark.parametrize("volume", [None, -1, True, 1.5, 2**63])
def test_invalid_normalized_volume_is_never_coerced(tmp_path: Path, volume: object) -> None:
    result = resolved(tmp_path)
    assert result.resolved is not None
    instrument = result.resolved.instrument
    provider = DhanMarketDataProvider(
        dhan_config(), transport=RecordingTransport(lambda p, b: response())
    )
    series = provider.get_historical(instrument, "1d", live.START, live.END)
    broken = series.model_copy(
        update={"bars": (series.bars[0].model_copy(update={"volume": volume}),)}
    )
    with pytest.raises(live.ProvisioningError, match="INVALID_VOLUME"):
        live.canonical_csv((broken,), instrument)


def test_stable_manifest_and_byte_fingerprints(tmp_path: Path) -> None:
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    # Master cache mtimes differ; inject the same resolution provenance for replay determinism.
    result = resolved(a)

    def run(root: Path) -> dict[str, Any]:
        provider = DhanMarketDataProvider(
            dhan_config(), transport=RecordingTransport(lambda p, b: response()), clock=lambda: NOW
        )
        return cast(
            dict[str, Any],
            live.provision(
                provider,
                result,
                root=root,
                master_sha256="a" * 64,
                resolved_at=NOW,
                clock=lambda: NOW,
            ),
        )

    assert run(a) == run(b)


def test_output_policy_symlink_existing_and_no_overwrite(tmp_path: Path) -> None:
    with pytest.raises(live.ProvisioningError, match="FIXED"):
        live.check_destination(tmp_path / "elsewhere", tmp_path)
    (tmp_path / "data").symlink_to(tmp_path / "escape")
    with pytest.raises(live.ProvisioningError, match="SYMLINK"):
        live.check_destination(tmp_path / "data/ff1/reliance", tmp_path)
    other = tmp_path / "other"
    target = other / "data/ff1/reliance"
    target.mkdir(parents=True)
    with pytest.raises(live.ProvisioningError, match="EXISTS"):
        live.check_destination(target, other)


def test_offline_tamper_detection_and_no_secret_keys(tmp_path: Path) -> None:
    acquire(tmp_path)
    root = tmp_path / "data/ff1/reliance"
    with pytest.raises(ValueError, match="secret-bearing"):
        live.seal({"access_token": "not-a-real-token"})
    with (root / "reliance_daily_ohlcv.csv").open("a") as file:
        file.write("tampered\n")
    with pytest.raises(live.ProvisioningError, match="CSV_FINGERPRINT"):
        live.verify_package(root)


def test_engineering_only_surface_no_trading_or_tm_import() -> None:
    source = SCRIPT.read_text()
    for prohibited in (".get_quote(", ".post(", "place_order", "modify_order", "TradeMonitor"):
        assert prohibited not in source
    assert "MarketDataProvider" in source
    assert "DhanInstrumentResolver" in source
    assert "canonical_json" in source and "semantic_fingerprint" in source
    from tiaf.facade import capability_catalog

    assert len(capability_catalog()) == 9


def test_provider_failure_is_one_attempt_no_output(tmp_path: Path) -> None:
    result = resolved(tmp_path)
    transport = RecordingTransport(lambda p, b: (_ for _ in ()).throw(ProviderAuthError("denied")))
    provider = DhanMarketDataProvider(dhan_config(), transport=transport)
    with pytest.raises(ProviderAuthError):
        live.provision(provider, result, root=tmp_path, master_sha256="a" * 64, resolved_at=NOW)
    assert len(transport.calls) == 1
    assert not (tmp_path / "data/ff1/reliance").exists()
