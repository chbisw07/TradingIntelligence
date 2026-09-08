"""A3.4 identity, time, provenance, immutability, and normalization contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from tiaf.contracts import DataQuality, FreshnessState
from tiaf.fundamentals import (
    FactBasis,
    FundamentalDataset,
    FundamentalMetric,
    FundamentalNormalizationError,
    FundamentalSourceQuality,
    FundamentalUnit,
    ValueScale,
    fundamental_dataset_json,
    fundamental_fingerprint,
    load_fundamental_dataset_json,
    normalize_percent,
    normalize_scale,
    point_in_time_facts,
    preferred_fact,
    resolve_revisions,
)

from ._support import ACQUIRED, NOW, PUBLISHED, company, derived_fact, fact


def test_contracts_are_frozen_tuple_backed_json_round_trippable_and_ist() -> None:
    item = derived_fact(FundamentalMetric.REVENUE_GROWTH_YOY, 12.5)
    dumped = item.model_dump(mode="json")

    with pytest.raises(ValidationError):
        item.value = 99.0
    with pytest.raises(AttributeError):
        item.derivation.source_fact_ids.append("other")  # type: ignore[union-attr]

    assert isinstance(dumped["derivation"]["source_fact_ids"], list)
    assert dumped["published_at"].endswith("+05:30")
    assert type(item).model_validate(dumped) == item


def test_naive_time_and_wrong_company_or_metric_unit_are_rejected() -> None:
    base = fact(FundamentalMetric.REVENUE_GROWTH_YOY, 12.0).model_dump(mode="python")
    with pytest.raises(ValidationError, match="timezone-aware"):
        type(fact(FundamentalMetric.REVENUE_GROWTH_YOY, 12.0)).model_validate(
            {**base, "published_at": datetime(2026, 5, 15, 12, 0)}
        )
    with pytest.raises(ValidationError, match="requires PERCENT unit"):
        type(fact(FundamentalMetric.REVENUE_GROWTH_YOY, 12.0)).model_validate(
            {**base, "unit": FundamentalUnit.RATIO}
        )

    wrong = company().model_copy(update={"symbol": "TCS"})
    with pytest.raises(ValidationError, match="symbol must match"):
        type(company()).model_validate(wrong.model_dump(mode="python"))


def test_utc_inputs_normalize_to_canonical_application_timezone() -> None:
    item = fact(
        FundamentalMetric.ROE,
        18.0,
        published_at=datetime(2026, 5, 15, 12, 30, tzinfo=UTC),
        acquired_at=datetime(2026, 5, 15, 13, 30, tzinfo=UTC),
    )
    offset = item.published_at.utcoffset()
    assert offset is not None
    assert offset.total_seconds() == 19_800
    assert item.published_at.hour == 18


def test_point_in_time_excludes_future_publication_and_future_acquisition() -> None:
    visible = fact(FundamentalMetric.ROE, 15.0)
    future_publication = fact(
        FundamentalMetric.ROCE,
        18.0,
        suffix="future-publication",
        published_at=NOW.replace(day=9),
        acquired_at=NOW.replace(day=9, hour=13),
    )
    future_acquisition = fact(
        FundamentalMetric.NET_MARGIN,
        12.0,
        suffix="future-acquisition",
        published_at=PUBLISHED,
        acquired_at=NOW.replace(day=9),
    )

    selected = point_in_time_facts(
        (visible, future_publication, future_acquisition), as_of=NOW
    )
    assert selected == (visible,)


def test_explicit_restatement_selects_latest_visible_revision() -> None:
    original = fact(FundamentalMetric.ROE, 15.0, suffix="original")
    revision = fact(
        FundamentalMetric.ROE,
        16.0,
        suffix="revision",
        revision=1,
        revision_id="revision-1",
        replaces_fact_id=original.fact_id,
    )
    assert resolve_revisions((revision, original)) == (revision,)


def test_future_restatement_does_not_replace_value_at_earlier_decision_time() -> None:
    original = fact(FundamentalMetric.ROE, 15.0, suffix="original")
    future_revision = fact(
        FundamentalMetric.ROE,
        16.0,
        suffix="future-revision",
        published_at=NOW.replace(day=9),
        acquired_at=NOW.replace(day=10),
        revision=1,
        revision_id="revision-1",
        replaces_fact_id=original.fact_id,
    )

    assert point_in_time_facts((original, future_revision), as_of=NOW) == (original,)


def test_duplicate_same_revision_is_rejected_and_cross_source_conflict_is_visible() -> None:
    first = fact(FundamentalMetric.ROE, 15.0, suffix="first")
    duplicate = fact(FundamentalMetric.ROE, 16.0, suffix="duplicate")
    with pytest.raises(FundamentalNormalizationError, match="ambiguous"):
        resolve_revisions((first, duplicate))

    alternate = fact(
        FundamentalMetric.ROE,
        16.0,
        suffix="alternate",
        source_provider="fixture.exchange.alternate",
    )
    with pytest.raises(FundamentalNormalizationError, match="conflict"):
        preferred_fact((first, alternate))


def test_explicit_scale_percent_and_currency_normalization() -> None:
    crores = fact(FundamentalMetric.NET_INCOME, 12.5)
    normalized = normalize_scale(crores)

    assert crores.scale is ValueScale.CRORES
    assert normalized.scale is ValueScale.ONES
    assert normalized.value == 125_000_000.0
    assert normalized.currency == "INR"
    assert normalize_percent(0.185, source_is_fraction=True) == 18.5
    assert normalize_percent(18.5, source_is_fraction=False) == 18.5


def test_dataset_fingerprint_and_json_round_trip_preserve_provider_and_periods() -> None:
    items = (
        fact(FundamentalMetric.ROE, 18.0),
        fact(FundamentalMetric.DEBT_EQUITY, 0.4),
    )
    fingerprint = fundamental_fingerprint(
        company(), "fixture.exchange", "1.0", NOW, items, ()
    )
    dataset = FundamentalDataset(
        dataset_id="dataset-1",
        company=company(),
        provider_id="fixture.exchange",
        provider_version="1.0",
        requested_as_of=NOW,
        acquired_at=ACQUIRED,
        valid_until=NOW.replace(year=2027),
        facts=items,
        quality=DataQuality.GOOD,
        freshness=FreshnessState.FRESH,
        fingerprint=fingerprint,
    )

    payload = fundamental_dataset_json(dataset)
    reconstructed = load_fundamental_dataset_json(payload)
    assert reconstructed == dataset
    assert reconstructed.facts[0].period == items[0].period
    assert reconstructed.provider_id == "fixture.exchange"


def test_reported_and_derived_provenance_cannot_be_conflated() -> None:
    derived = derived_fact(FundamentalMetric.PROFIT_GROWTH_YOY, 14.0)
    base = derived.model_dump(mode="python")
    with pytest.raises(ValidationError, match="derived fact requires"):
        type(derived).model_validate({**base, "derivation": None})
    with pytest.raises(ValidationError, match="reported fact cannot"):
        type(derived).model_validate({**base, "basis": FactBasis.REPORTED})

    assert derived.source_quality is FundamentalSourceQuality.DERIVED_FROM_PRIMARY
