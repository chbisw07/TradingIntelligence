"""FF0-04–10/13: supplied clocks, PIT and typed absence; no trusted runtime yet."""

from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_contracts import ForecastWindow, QualifiedCloseObservation
from tiaf.forecasting.contracts import ForecastRequest, ForecastResult
from tiaf.forecasting.enums import ForecastReason, KnowledgeBasis
from tiaf.forecasting.errors import ForecastAdmissionError
from tiaf.forecasting.evidence import validate_reference_bar, validate_required_evidence

from ._support import bar, instant, request, result, window
from .test_contracts import changed


@pytest.mark.parametrize("simulated", [False, True])
@pytest.mark.parametrize(
    "field,value",
    [
        ("information_cutoff", "2026-02-04T15:29:00+05:30"),
        ("information_cutoff", "2026-02-04T16:06:00+05:30"),
        ("as_of", "2026-02-05T09:15:00+05:30"),
        ("as_of", "2026-02-05T10:00:00+05:30"),
        ("evidence.0.available_at", "2026-02-05T10:00:00+05:30"),
        ("evidence.0.admitted_at", "2026-02-04T16:01:00+05:30"),
    ],
)
def test_cutoff_and_target_open_guards(simulated: bool, field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        ForecastRequest.model_validate(changed(request(simulated=simulated), {field: value}))


@pytest.mark.parametrize(
    "changes",
    [
        {"issued_at": "2026-02-04T16:05:00+05:30"},
        {"issued_at": "2026-02-05T09:15:00+05:30"},
        {"issued_at": "2026-02-05T10:00:00+05:30"},
        {"computed_at": "2026-02-04T16:04:00+05:30"},
        {"computed_at": None},
        {"issued_at": None},
        {"artifact_identity.fit_knowledge_cutoff": "2026-02-04T16:01:00+05:30"},
        {"artifact_identity.prepared_at": "2026-02-05T10:00:00+05:30"},
        {"binding_available_at": "2026-02-05T10:00:00+05:30"},
    ],
)
def test_actual_backdating_and_artifact_boundaries(changes: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ForecastResult.model_validate(changed(result(), changes))


def test_completion_equal_issue_is_valid_before_open() -> None:
    payload = changed(result(), {"issued_at": instant(4, 16, 6)})
    out = ForecastResult.model_validate(payload)
    assert out.computed_at == out.issued_at
    assert out.request.information_cutoff < out.request.as_of


def test_late_actual_attempt_can_be_absent_without_claiming_issue() -> None:
    payload = changed(
        result(),
        {
            "status": "UNAVAILABLE",
            "computed_at": instant(5, 10),
            "issued_at": None,
            "output": {"kind": "ABSENCE", "reasons": ["TEMPORAL_INELIGIBLE"]},
        },
    )
    out = ForecastResult.model_validate(payload)
    assert out.computed_at == instant(5, 10) and out.issued_at is None


def test_simulation_late_fit_and_acquisition_are_explicit_not_backdated() -> None:
    payload = changed(
        result(simulated=True),
        {
            "request.knowledge_basis": KnowledgeBasis.QUALIFIED_HISTORICAL_AVAILABILITY,
            "request.evidence.0.acquired_at": instant(7, 10),
            "request.evidence.0.admitted_at": instant(7, 10),
            "artifact_identity.prepared_at": instant(7, 11),
            "artifact_identity.fit_evidence.0.acquired_at": instant(7, 10),
            "artifact_identity.fit_evidence.0.admitted_at": instant(7, 10),
        },
    )
    out = ForecastResult.model_validate(payload)
    assert out.computed_at is not None and out.computed_at > out.request.window.target_resolve_time
    assert out.request.simulation_as_of == instant(4, 16, 5)
    assert "simulation_as_of" not in out.request.model_dump(mode="json")
    assert out.issued_at is None
    payload["request"]["knowledge_basis"] = "CAPTURED_AS_KNOWN"
    with pytest.raises(ValidationError):
        ForecastResult.model_validate(payload)


@pytest.mark.parametrize(
    "changes",
    [
        {"issued_at": "2026-02-04T16:07:00+05:30"},
        {"computed_at": "2026-02-04T16:04:00+05:30"},
        {"request.simulation_profile_ref": None},
        {"artifact_identity.fit_evidence.0.available_at": "2026-02-06T12:00:00+05:30"},
        {"request.evidence.0.data_basis": "QUALIFIED_CAPTURE"},
    ],
)
def test_simulation_rejects_fake_issue_missing_profile_and_leakage(
    changes: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        ForecastResult.model_validate(changed(result(simulated=True), changes))


@pytest.mark.parametrize("value", ["2026-02-04T16:00:00", datetime(2026, 2, 4, 16), 0, True])
@pytest.mark.parametrize("field", ["information_cutoff", "as_of", "window.target_open_time"])
def test_naive_and_non_iso_clock_inputs_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        ForecastRequest.model_validate(changed(request(), {field: value}))


@pytest.mark.parametrize("zone", ["UTC", "America/New_York", "Europe/London"])
def test_aware_zones_normalize_without_changing_identity(zone: str) -> None:
    req = request()
    other = ForecastRequest.model_validate(
        changed(
            req,
            {
                "information_cutoff": req.information_cutoff.astimezone(ZoneInfo(zone)),
                "as_of": req.as_of.astimezone(ZoneInfo(zone)),
            },
        )
    )
    assert other == req and other.semantic_fingerprint == req.semantic_fingerprint
    assert other.model_dump(mode="json")["as_of"].endswith("+05:30")
    assert isinstance(other.as_of.tzinfo, ZoneInfo)


@pytest.mark.parametrize("value", [True, 105.0, "NaN", "Infinity", "0", "-1"])
def test_source_price_is_positive_exact_and_not_a_float_conversion(value: object) -> None:
    with pytest.raises(ValidationError):
        QualifiedCloseObservation.model_validate(changed(window().reference, {"value": value}))


def test_exact_price_format_and_bar_correspondence_preserve_zero_volume() -> None:
    close = window().reference
    assert close.model_dump(mode="json")["value"] == "105"
    assert close.value == Decimal("105")
    validate_reference_bar(close, bar())
    assert bar().volume == 0
    with pytest.raises(ForecastAdmissionError):
        validate_reference_bar(close, bar().model_copy(update={"close": 105.5}))


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"schedule.complete": False, "schedule.qualification": "PARTIAL"}, "CALENDAR_UNQUALIFIED"),
        (
            {"reference.qualification": "STALE", "reference.reasons": ["EVIDENCE_STALE"]},
            "EVIDENCE_STALE",
        ),
        (
            {
                "reference.value": None,
                "reference.qualification": "MISSING",
                "reference.reasons": ["EVIDENCE_MISSING"],
            },
            "EVIDENCE_MISSING",
        ),
        ({"reference.action_coverage": "UNKNOWN"}, "ACTION_COVERAGE_UNKNOWN"),
        ({"reference.action_coverage": "AFFECTED"}, "ACTION_AFFECTED"),
        ({"schedule.sessions.1.subject_eligible": False}, "SCOPE_UNSUPPORTED"),
    ],
)
def test_missingness_qualifies_separately_and_generated_result_cannot_hide_it(
    changes: dict[str, object],
    reason: str,
) -> None:
    candidate = ForecastWindow.model_validate(changed(window(), changes))
    with pytest.raises(ForecastAdmissionError) as exc:
        validate_required_evidence(candidate)
    assert exc.value.reason == ForecastReason(reason)
    with pytest.raises(ValidationError):
        ForecastResult.model_validate(
            changed(result(), {"request.window": candidate.model_dump(mode="json")})
        )


def test_defensive_reconstruction_rejects_forged_pydantic_copies() -> None:
    forged = request().model_copy(update={"as_of": instant(5, 10)})
    with pytest.raises(ValidationError):
        ForecastRequest.model_validate(forged)
    forged_subject = request().target.subject.model_copy(update={"symbol": "KAYNES"})
    with pytest.raises(ValidationError):
        type(request().target)(
            subject=forged_subject,
            labeler_ref=request().target.labeler_ref,
            qualification_policy_ref=request().target.qualification_policy_ref,
        )
