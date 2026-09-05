"""CLI regressions for the read-only expired-options smoke utility."""

import runpy
import sys
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tiaf.contracts import OptionType
from tiaf.data import ExpiryFlag, HistoricalOptionExpiryCode


def test_cli_near_expiry_code_reaches_provider_as_plain_integer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    namespace = runpy.run_path("scripts/dhan_expired_options_smoke.py")

    class FakeProvider:
        def get_historical_options(self, **kwargs: Any) -> SimpleNamespace:
            captured.update(kwargs)
            return SimpleNamespace(
                underlying=SimpleNamespace(symbol="RELIANCE"),
                option_type=OptionType.CE,
                expiry_flag=ExpiryFlag.MONTH,
                expiry_code=HistoricalOptionExpiryCode.NEAR,
                relative_strike="ATM",
                requested_from="2026-08-01",
                requested_to="2026-08-02",
                bars=(),
            )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "dhan_expired_options_smoke.py",
            "--segment",
            "NSE_FNO",
            "--security-id",
            "1333",
            "--symbol",
            "RELIANCE",
            "--instrument",
            "OPTSTK",
            "--expiry-flag",
            "MONTH",
            "--expiry-code",
            "1",
            "--strike",
            "ATM",
            "--option-type",
            "CE",
            "--interval",
            "15m",
            "--from-date",
            "2026-08-01",
            "--to-date",
            "2026-08-02",
            "--sample-size",
            "0",
        ],
    )

    main = cast(Callable[[], int], namespace["main"])
    main.__globals__["DhanMarketDataProvider"] = FakeProvider
    assert main() == 0
    assert captured["expiry_code"] == 1
    assert type(captured["expiry_code"]) is int


def test_cli_rejects_zero_expiry_code(monkeypatch: pytest.MonkeyPatch) -> None:
    namespace = runpy.run_path("scripts/dhan_expired_options_smoke.py")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "dhan_expired_options_smoke.py",
            "--segment",
            "NSE_FNO",
            "--security-id",
            "1333",
            "--symbol",
            "RELIANCE",
            "--instrument",
            "OPTSTK",
            "--expiry-flag",
            "MONTH",
            "--expiry-code",
            "0",
            "--strike",
            "ATM",
            "--option-type",
            "CE",
            "--interval",
            "15m",
            "--from-date",
            "2026-08-01",
            "--to-date",
            "2026-08-02",
        ],
    )
    main = cast(Callable[[], int], namespace["main"])
    with pytest.raises(SystemExit, match="2"):
        main()
