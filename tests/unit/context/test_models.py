"""AnalysisContext contracts and requirement validation."""

from datetime import date, datetime

import pytest
from pydantic import TypeAdapter, ValidationError

from tiaf.context import (
    AnalysisContext,
    AnalysisContextRequirement,
    AnalysisPurpose,
    AnalysisSubject,
    EvidenceDescriptor,
    EvidenceRequirement,
    EvidenceStatus,
    HistoricalOptionRequirement,
)
from tiaf.contracts import DataQuality, FreshnessState, OptionType
from tiaf.data import ExpiryFlag, HistoricalOptionExpiryCode, RelativeStrike
from tiaf.data.runtime import FetchDisposition

from ._support import FRESH, NOW, make_builder, requirement, resolved


@pytest.mark.parametrize("purpose", list(AnalysisPurpose))
def test_analysis_purpose_serialization(purpose: AnalysisPurpose) -> None:
    adapter = TypeAdapter(AnalysisPurpose)
    assert adapter.dump_json(purpose).decode() == f'"{purpose.value}"'
    assert adapter.validate_json(adapter.dump_json(purpose)) is purpose


def test_requirement_accepts_coherent_history() -> None:
    context_requirement = requirement()
    assert context_requirement.history_interval == "1d"
    assert context_requirement.history_lookback_days == 90


@pytest.mark.parametrize(
    "changes",
    [
        {"history_interval": None},
        {"history_lookback_days": None},
        {"history_lookback_days": 0},
        {
            "include_history": False,
            "require_history": False,
            "history_interval": "1d",
            "history_lookback_days": 10,
        },
        {"include_derivatives": True, "option_expiry": None},
    ],
)
def test_requirement_rejects_incoherent_parameters(changes: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        requirement(**changes)


def test_required_evidence_is_automatically_included() -> None:
    value = AnalysisContextRequirement(
        purpose=AnalysisPurpose.RESEARCH,
        include_quote=False,
        include_history=False,
        require_history=False,
        require_derivatives=True,
        option_expiry=date(2026, 9, 29),
    )
    assert value.include_derivatives


def test_derivatives_expiry_is_rejected_when_not_requested() -> None:
    with pytest.raises(ValidationError, match="option_expiry requires"):
        AnalysisContextRequirement(
            purpose=AnalysisPurpose.RESEARCH,
            include_quote=False,
            require_quote=False,
            include_history=False,
            require_history=False,
            option_expiry=date(2026, 9, 29),
        )


def test_historical_options_require_exact_bounded_requests() -> None:
    request = HistoricalOptionRequirement(
        interval="15m",
        expiry_flag=ExpiryFlag.MONTH,
        expiry_code=HistoricalOptionExpiryCode.NEAR,
        relative_strike=RelativeStrike("ATM"),
        option_type=OptionType.CE,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 7),
    )
    value = requirement(
        include_historical_options=True,
        require_historical_options=True,
        historical_option_requests=[request],
        historical_options_freshness=FRESH,
    )
    assert value.historical_option_requests == (request,)


def test_historical_options_cannot_be_requested_without_specification() -> None:
    with pytest.raises(ValidationError, match="exact historical_option_requests"):
        requirement(include_historical_options=True)


def test_requirement_rejects_credentials_in_metadata() -> None:
    with pytest.raises(ValidationError, match="credentials"):
        requirement(metadata={"access-token": "secret"})
    with pytest.raises(ValidationError, match="credentials"):
        requirement(metadata={"nested": {"api_key": "secret"}})


def test_analysis_subject_is_immutable_and_normalizes_time() -> None:
    subject = AnalysisSubject(
        symbol="reliance",
        resolved_instrument=resolved(),
        requested_at=NOW.astimezone(datetime.now().astimezone().tzinfo),
    )
    assert subject.symbol == "RELIANCE"
    assert subject.requested_at.utcoffset() == NOW.utcoffset()
    with pytest.raises(ValidationError):
        subject.symbol = "OTHER"


def test_analysis_subject_rejects_symbol_mismatch_and_naive_time() -> None:
    with pytest.raises(ValidationError, match="must match"):
        AnalysisSubject(
            symbol="OTHER", resolved_instrument=resolved(), requested_at=NOW
        )
    with pytest.raises(ValidationError, match="timezone-aware"):
        AnalysisSubject(
            symbol="RELIANCE",
            resolved_instrument=resolved(),
            requested_at=datetime(2026, 9, 6),
        )


def test_failed_evidence_requires_safe_error_fields() -> None:
    with pytest.raises(ValidationError, match="requires error_type"):
        EvidenceDescriptor(
            evidence_name="quote",
            requested=True,
            required=True,
            requirement_role=EvidenceRequirement.REQUIRED,
            status=EvidenceStatus.FAILED,
        )


def test_not_requested_evidence_rejects_factual_provenance() -> None:
    with pytest.raises(ValidationError, match="cannot carry factual"):
        EvidenceDescriptor(
            evidence_name="option_chain",
            requested=False,
            required=False,
            requirement_role=EvidenceRequirement.NOT_REQUESTED,
            status=EvidenceStatus.NOT_REQUESTED,
            retrieval_freshness=FreshnessState.FRESH,
        )


def test_evidence_descriptor_preserves_provenance() -> None:
    descriptor = EvidenceDescriptor(
        evidence_name="quote",
        requested=True,
        required=True,
        requirement_role=EvidenceRequirement.REQUIRED,
        status=EvidenceStatus.AVAILABLE,
        retrieval_freshness=FreshnessState.FRESH,
        quality=DataQuality.GOOD,
        source_provider="TEST",
        source_observed_at=NOW,
        received_at=NOW,
        retrieval_age_seconds=2,
        observation_age_seconds=3,
        source_observation_semantics="quote_last_trade_time",
        fetch_disposition=FetchDisposition.PROVIDER,
    )
    assert descriptor.source_provider == "test"
    assert descriptor.retrieval_age_seconds == 2
    assert descriptor.observation_age_seconds == 3


def test_context_is_immutable_and_json_round_trips_with_array_collections() -> None:
    builder, *_ = make_builder()
    context = builder.build("RELIANCE", requirement(), context_id="ctx-fixed")
    dumped = context.model_dump(mode="json")
    assert isinstance(dumped["evidence"], list)
    assert isinstance(dumped["missing_required_evidence"], list)
    assert AnalysisContext.model_validate(dumped) == context
    with pytest.raises(ValidationError):
        context.complete = False


def test_context_contract_rejects_inconsistent_completeness() -> None:
    builder, *_ = make_builder()
    context = builder.build("RELIANCE", requirement())
    with pytest.raises(ValidationError, match="complete must agree"):
        AnalysisContext.model_validate(
            {
                **context.model_dump(),
                "complete": False,
                "missing_required_evidence": (),
            }
        )
