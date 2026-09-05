"""Resolution behavior over representative Dhan master records."""

from datetime import date
from pathlib import Path

import pytest

from tiaf.contracts import DataQuality, OptionType
from tiaf.data import InstrumentType, MarketSegment
from tiaf.data.resolution import (
    InstrumentQuery,
    ResolutionKind,
    ResolutionPolicy,
    ResolutionResult,
)

from ._instrument_master_support import MASTER_HEADER, MASTER_ROWS, resolver_at


def test_unique_nse_equity_resolves_to_fixture_security_id(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(
        InstrumentQuery(
            symbol="reliance",
            exchange="nse",
            instrument_type=InstrumentType.EQUITY,
        )
    )
    assert result.resolved is not None
    assert result.resolved.provider_instrument_id == "2885"
    assert result.resolved.instrument.segment is MarketSegment.NSE_EQUITY


def test_symbol_only_cross_exchange_listings_use_default_nse_policy(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(InstrumentQuery(symbol="RELIANCE"))
    assert result.resolved is not None
    assert result.resolved.provider_instrument_id == "2885"
    assert result.resolved.resolution_kind is ResolutionKind.POLICY_SELECTED
    assert result.metadata == {
        "policy_applied": True,
        "preferred_exchange": "NSE",
        "candidate_count_before_policy": 2,
    }


@pytest.mark.parametrize(
    "exchange,expected",
    [("NSE", "2885"), ("BSE", "500325")],
)
def test_exchange_and_equity_type_disambiguate_cash_listing(
    tmp_path: Path, exchange: str, expected: str
) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(
        InstrumentQuery(
            symbol="RELIANCE",
            exchange=exchange,
            instrument_type=InstrumentType.EQUITY,
        )
    )
    assert result.resolved is not None
    assert result.resolved.provider_instrument_id == expected
    assert result.metadata["policy_applied"] is False


def test_exact_index_lookup_uses_master_identity(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(
        InstrumentQuery(symbol="nifty", segment=MarketSegment.NSE_INDEX)
    )
    assert result.resolved is not None
    assert result.resolved.provider_instrument_id == "13"
    assert result.resolved.instrument.instrument_type is InstrumentType.INDEX


def test_futures_without_expiry_are_ambiguous(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(
        InstrumentQuery(symbol="RELIANCE", instrument_type=InstrumentType.FUTURE)
    )
    assert result.ambiguous
    assert {item.instrument.expiry for item in result.matches} == {
        date(2026, 9, 24),
        date(2026, 10, 29),
    }


@pytest.mark.parametrize(
    "expiry,expected",
    [(date(2026, 9, 24), "7001"), (date(2026, 10, 29), "7002")],
)
def test_future_expiry_resolves_exact_contract(
    tmp_path: Path, expiry: date, expected: str
) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(
        InstrumentQuery(
            symbol="RELIANCE",
            segment=MarketSegment.NSE_FNO,
            instrument_type=InstrumentType.FUTURE,
            expiry=expiry,
        )
    )
    assert result.resolved is not None
    assert result.resolved.provider_instrument_id == expected


@pytest.mark.parametrize(
    "instrument_type,strike,option_type,expected",
    [
        (InstrumentType.CALL_OPTION, 3000, OptionType.CE, "8001"),
        (InstrumentType.PUT_OPTION, 3000, OptionType.PE, "8002"),
        (InstrumentType.CALL_OPTION, 3100, OptionType.CE, "8003"),
    ],
)
def test_full_option_identity_resolves_exact_contract(
    tmp_path: Path,
    instrument_type: InstrumentType,
    strike: float,
    option_type: OptionType,
    expected: str,
) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(
        InstrumentQuery(
            symbol="RELIANCE",
            segment=MarketSegment.NSE_FNO,
            instrument_type=instrument_type,
            expiry=date(2026, 9, 24),
            strike=strike,
            option_type=option_type,
        )
    )
    assert result.resolved is not None
    assert result.resolved.provider_instrument_id == expected
    assert result.resolved.resolution_kind is ResolutionKind.EXACT


@pytest.mark.parametrize(
    "trading_symbol,expected",
    [
        ("reliance", "2885"),
        ("RELIANCE 24 SEP 3000 CE", "8001"),
        ("NIFTY 50", "13"),
    ],
)
def test_exact_trading_symbol_lookup(
    tmp_path: Path, trading_symbol: str, expected: str
) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(InstrumentQuery(trading_symbol=trading_symbol))
    assert result.resolved is not None
    assert result.resolved.provider_instrument_id == expected
    assert result.resolved.resolution_kind is ResolutionKind.TRADING_SYMBOL
    assert result.metadata["policy_applied"] is False


@pytest.mark.parametrize("security_id", ["2885", "1333", "8001", "999"])
def test_exact_provider_id_lookup_includes_inactive_record(
    tmp_path: Path, security_id: str
) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(InstrumentQuery(provider_instrument_id=security_id))
    assert result.resolved is not None
    assert result.resolved.provider_instrument_id == security_id
    assert result.resolved.resolution_kind is ResolutionKind.PROVIDER_ID
    assert result.metadata["policy_applied"] is False
    if security_id == "999":
        assert result.resolved.quality is DataQuality.DEGRADED
        assert result.resolved.metadata["active"] is False


def test_normal_lookup_excludes_inactive_record(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(InstrumentQuery(symbol="OLDCO"))
    assert result.not_found
    assert result.matches == ()


@pytest.mark.parametrize(
    "query",
    [
        InstrumentQuery(symbol="ABSENT"),
        InstrumentQuery(provider_instrument_id="404"),
        InstrumentQuery(symbol="RELIANCE", provider="ZERODHA"),
        InstrumentQuery(
            symbol="RELIANCE", exchange="MCX", instrument_type=InstrumentType.FUTURE
        ),
    ],
)
def test_not_found_is_an_ordinary_result(tmp_path: Path, query: InstrumentQuery) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(query)
    assert result.not_found is True
    assert result.ambiguous is False
    assert result.resolved is None


def test_conflicting_provider_id_and_symbol_returns_not_found(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(
        InstrumentQuery(symbol="NIFTY", provider_instrument_id="2885")
    )
    assert result.not_found


def test_resolve_many_preserves_order_and_independent_results(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    results = resolver.resolve_many(
        (
            InstrumentQuery(provider_instrument_id="13"),
            InstrumentQuery(symbol="ABSENT"),
            InstrumentQuery(symbol="RELIANCE"),
        )
    )
    assert results[0].resolved is not None
    assert results[0].resolved.provider_instrument_id == "13"
    assert results[1].not_found
    assert results[2].resolved is not None
    assert results[2].resolved.resolution_kind is ResolutionKind.POLICY_SELECTED


def test_repeated_queries_reuse_one_download_and_parse(tmp_path: Path) -> None:
    resolver, downloader = resolver_at(tmp_path)
    resolver.resolve(InstrumentQuery(provider_instrument_id="13"))
    resolver.resolve(InstrumentQuery(provider_instrument_id="2885"))
    assert len(downloader.calls) == 1


def test_explicit_refresh_rebuilds_master(tmp_path: Path) -> None:
    resolver, downloader = resolver_at(tmp_path)
    resolver.resolve(InstrumentQuery(provider_instrument_id="13"))
    resolver.refresh()
    assert len(downloader.calls) == 2


def test_fno_underlying_list_is_unique_current_and_deterministic(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    underlyings = resolver.get_fno_underlyings()
    assert [(item.instrument.symbol, item.provider_instrument_id) for item in underlyings] == [
        ("HDFCBANK", "1333"),
        ("NIFTY", "13"),
        ("RELIANCE", "2885"),
    ]
    assert all(item.instrument.exchange == "NSE" for item in underlyings)
    assert all(item.metadata["fno_exchange"] == "NSE" for item in underlyings)


def test_explicit_bse_fno_scope_returns_only_bse_backed_underlyings(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    underlyings = resolver.get_fno_underlyings(exchange="BSE")
    assert [(item.instrument.symbol, item.provider_instrument_id) for item in underlyings] == [
        ("RELIANCE", "500325")
    ]


def test_configured_primary_fno_exchange_controls_default_scope(tmp_path: Path) -> None:
    resolver, _ = resolver_at(
        tmp_path,
        policy=ResolutionPolicy(primary_exchange="NSE", primary_fno_exchange="BSE"),
    )
    underlyings = resolver.get_fno_underlyings()
    assert [item.provider_instrument_id for item in underlyings] == ["500325"]


def test_fno_universe_excludes_cash_symbol_without_derivative_relationship(
    tmp_path: Path,
) -> None:
    resolver, _ = resolver_at(tmp_path)
    assert "KAYNES" not in {
        item.instrument.symbol for item in resolver.get_fno_underlyings()
    }


def test_two_candidates_inside_preferred_exchange_remain_ambiguous(tmp_path: Path) -> None:
    duplicate = (
        "NSE,E,1334,EQUITY,,,RELIANCE,RELIANCE-N2,Reliance Duplicate,EQ,1,,,,0.05,Y"
    )
    body = (MASTER_HEADER + "\n" + "\n".join((*MASTER_ROWS, duplicate)) + "\n").encode()
    resolver, _ = resolver_at(tmp_path, body=body)
    result = resolver.resolve(InstrumentQuery(symbol="RELIANCE"))
    assert result.ambiguous
    assert len(result.matches) == 3
    assert result.metadata["policy_applied"] is False


def test_no_preferred_exchange_candidate_preserves_ordinary_ambiguity(tmp_path: Path) -> None:
    resolver, _ = resolver_at(
        tmp_path,
        policy=ResolutionPolicy(primary_exchange="MCX", primary_fno_exchange="NSE"),
    )
    result = resolver.resolve(InstrumentQuery(symbol="RELIANCE"))
    assert result.ambiguous
    assert {item.instrument.exchange for item in result.matches} == {"NSE", "BSE"}
    assert result.metadata["preferred_exchange"] == "MCX"


def test_policy_can_be_disabled_without_changing_generic_matches(tmp_path: Path) -> None:
    resolver, _ = resolver_at(
        tmp_path,
        policy=ResolutionPolicy(prefer_primary_cash_listing=False),
    )
    result = resolver.resolve(InstrumentQuery(symbol="RELIANCE"))
    assert result.ambiguous
    assert len(result.matches) == 2


def test_unique_symbol_does_not_claim_policy_selection(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(InstrumentQuery(symbol="KAYNES"))
    assert result.resolved is not None
    assert result.resolved.resolution_kind is ResolutionKind.UNIQUE_NORMALIZED
    assert result.metadata["policy_applied"] is False


def test_policy_selected_result_has_clean_json_round_trip(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(InstrumentQuery(symbol="RELIANCE"))
    dumped = result.model_dump(mode="json")
    assert dumped["resolved"]["resolution_kind"] == "POLICY_SELECTED"
    assert dumped["metadata"]["policy_applied"] is True
    assert isinstance(dumped["matches"], list)
    assert ResolutionResult.model_validate(dumped) == result


def test_source_attribution_and_canonical_identity_are_preserved(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(InstrumentQuery(provider_instrument_id="8001"))
    assert result.source_provider == "dhan"
    assert result.resolved is not None
    assert result.resolved.source_record_id == "dhan:NSE_FNO:8001"
    assert result.resolved.underlying_symbol == "RELIANCE"
    assert result.resolved.lot_size == 250
    assert result.resolved.tick_size == 0.05


def test_search_returns_deterministically_sorted_immutable_matches(tmp_path: Path) -> None:
    resolver, _ = resolver_at(tmp_path)
    matches = resolver.search(InstrumentQuery(symbol="RELIANCE"))
    assert isinstance(matches, tuple)
    assert [item.provider_instrument_id for item in matches] == [
        "500325",
        "2885",
    ]


@pytest.mark.parametrize(
    "symbol,expected",
    [("RELIANCE", "2885"), ("HDFCBANK", "1333")],
)
def test_live_corrected_fixture_symbols_resolve_under_default_policy(
    tmp_path: Path,
    symbol: str,
    expected: str,
) -> None:
    resolver, _ = resolver_at(tmp_path)
    result = resolver.resolve(InstrumentQuery(symbol=symbol))
    assert result.resolved is not None
    assert result.resolved.provider_instrument_id == expected
    assert result.resolved.resolution_kind is ResolutionKind.POLICY_SELECTED


def test_fno_universe_excludes_dummy_inactive_and_non_tradable_rows_without_substring_rule(
    tmp_path: Path,
) -> None:
    header = (
        "EXCH_ID,SEGMENT,SECURITY_ID,ISIN,INSTRUMENT,UNDERLYING_SECURITY_ID,"
        "UNDERLYING_SYMBOL,SYMBOL_NAME,SM_EXPIRY_DATE,OPTION_TYPE,ACTIVE,"
        "BUY_SELL_INDICATOR"
    )
    rows = (
        "NSE,E,2000,INE000000001,EQUITY,,,CONTEST,,,Y,A",
        "NSE,D,3000,NA,FUTSTK,2000,CONTEST,CONTEST-Dec2026-FUT,2026-12-31,XX,Y,A",
        "NSE,E,2100,DUMMYSAN001,EQUITY,,,011NSETEST,,,Y,A",
        "NSE,D,3100,NA,FUTSTK,2100,011NSETEST,011NSETEST-Dec2036-FUT,"
        "2036-12-31,XX,Y,A",
        "NSE,E,2200,INE000000002,EQUITY,,,INACTIVE,,,N,A",
        "NSE,D,3200,NA,FUTSTK,2200,INACTIVE,INACTIVE-Dec2026-FUT,2026-12-31,XX,Y,A",
        "NSE,E,2300,INE000000003,EQUITY,,,HALTED,,,Y,A",
        "NSE,D,3300,NA,FUTSTK,2300,HALTED,HALTED-Dec2026-FUT,2026-12-31,XX,Y,N",
    )
    body = (header + "\n" + "\n".join(rows) + "\n").encode()
    resolver, _ = resolver_at(tmp_path, body=body)
    underlyings = resolver.get_fno_underlyings()
    assert [(item.instrument.symbol, item.provider_instrument_id) for item in underlyings] == [
        ("CONTEST", "2000")
    ]


def test_dummy_isin_marker_is_preserved_as_safe_provider_metadata(tmp_path: Path) -> None:
    header = (
        "EXCH_ID,SEGMENT,SECURITY_ID,ISIN,INSTRUMENT,UNDERLYING_SECURITY_ID,"
        "UNDERLYING_SYMBOL,SYMBOL_NAME,ACTIVE,BUY_SELL_INDICATOR"
    )
    body = (
        header
        + "\nNSE,E,2100,DUMMYSAN001,EQUITY,,,011NSETEST,Y,A\n"
    ).encode()
    resolver, _ = resolver_at(tmp_path, body=body)
    result = resolver.resolve(InstrumentQuery(provider_instrument_id="2100"))
    assert result.resolved is not None
    assert result.resolved.metadata["isin"] == "DUMMYSAN001"
    assert result.resolved.metadata["provider_test_instrument"] is True
