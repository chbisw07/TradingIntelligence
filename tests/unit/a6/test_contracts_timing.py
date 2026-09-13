from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from tiaf.trade_expression import (
    ExpirationQualification,
    ExpirationTiming,
    ExpressionDirection,
    ExpressionHorizon,
    ExpressionHorizonClass,
    FreshnessBasis,
    MarketTimingQualification,
    TimingQualification,
    TradeExpressionRequest,
    parse_trade_expression_request,
)
from tiaf.trade_expression.enums import A6ErrorCode
from tiaf.trade_expression.errors import A6ContractError

from ._support import IST, NOW, request


def test_request_is_immutable_versioned_and_json_round_trips() -> None:
    value = request()
    assert value.schema_version == "1.0"
    assert value.direction is ExpressionDirection.BULLISH
    with pytest.raises(ValidationError):
        value.subject = "OTHER"
    payload = value.model_dump(mode="json")
    assert isinstance(payload["authority_refs"], list)
    assert payload["evaluation_cutoff"].endswith("+05:30")
    assert TradeExpressionRequest.model_validate(payload) == value


def test_request_rejects_extra_and_ambiguous_horizon_input() -> None:
    payload = request().model_dump(mode="json")
    payload["unexpected"] = True
    with pytest.raises(ValidationError):
        TradeExpressionRequest.model_validate(payload)
    payload = request().model_dump(mode="json")
    payload["horizon"] = {"label": "3 weeks"}
    with pytest.raises(A6ContractError) as exc:
        parse_trade_expression_request(payload)
    assert exc.value.code is A6ErrorCode.INVALID_HORIZON


@pytest.mark.parametrize(
    "horizon_class",
    [ExpressionHorizonClass.DAY, ExpressionHorizonClass.POSITIONAL],
)
def test_horizon_preserves_exact_elapsed_time_and_normalizes_timezone(
    horizon_class: ExpressionHorizonClass,
) -> None:
    utc_cutoff = NOW.astimezone(UTC)
    horizon = ExpressionHorizon(
        horizon_class=horizon_class,
        target_end_at=utc_cutoff + timedelta(seconds=90, microseconds=500_000),
        exact_duration_seconds=Decimal("90.5"),
    )
    assert horizon.target_end_at.tzinfo == IST
    horizon.validate_against(NOW)


def test_horizon_rejects_naive_nonpositive_and_inexact_values() -> None:
    with pytest.raises(ValidationError):
        ExpressionHorizon(
            horizon_class=ExpressionHorizonClass.DAY,
            target_end_at=datetime(2026, 9, 10, 13),
            exact_duration_seconds=Decimal("3600"),
        )
    with pytest.raises(ValidationError):
        ExpressionHorizon(
            horizon_class=ExpressionHorizonClass.DAY,
            target_end_at=NOW,
            exact_duration_seconds=Decimal("0"),
        )
    horizon = ExpressionHorizon(
        horizon_class=ExpressionHorizonClass.DAY,
        target_end_at=NOW + timedelta(hours=1),
        exact_duration_seconds=Decimal("3599"),
    )
    with pytest.raises(ValueError, match="exact duration"):
        horizon.validate_against(NOW)


def test_observation_and_acquisition_are_distinct_authorities() -> None:
    observed = NOW - timedelta(seconds=5)
    timing = MarketTimingQualification(
        observed_at=observed.astimezone(UTC),
        acquired_at=NOW,
        qualification=TimingQualification.QUALIFIED,
        freshness_basis=FreshnessBasis.MARKET_OBSERVATION_TIME,
        qualification_source_ref="source:exchange-clock",
    )
    assert timing.observed_at == observed
    assert timing.acquired_at == NOW
    assert timing.authoritative_observed_at == observed


def test_acquisition_only_is_not_qualified_and_invalid_order_rejected() -> None:
    timing = MarketTimingQualification(
        acquired_at=NOW,
        qualification=TimingQualification.UNQUALIFIED,
        freshness_basis=FreshnessBasis.ACQUISITION_TIME_ONLY,
    )
    assert timing.authoritative_observed_at is None
    with pytest.raises(ValidationError):
        MarketTimingQualification(
            observed_at=NOW,
            acquired_at=NOW - timedelta(seconds=1),
            qualification=TimingQualification.QUALIFIED,
            freshness_basis=FreshnessBasis.MARKET_OBSERVATION_TIME,
            qualification_source_ref="source:clock",
        )


def test_date_only_expiry_is_not_a_qualified_instant() -> None:
    value = ExpirationTiming(
        expiry_date=date(2026, 9, 24),
        qualification=ExpirationQualification.DATE_ONLY,
    )
    assert value.expiration_at is None
    assert not value.is_qualified
    with pytest.raises(ValidationError):
        ExpirationTiming(
            expiry_date=date(2026, 9, 24),
            expiration_at=NOW,
            qualification=ExpirationQualification.DATE_ONLY,
        )
