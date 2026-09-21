"""FF-1.1 qualification, exact A2 projection and no-leakage acceptance."""

import math
import statistics
from datetime import UTC, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_qualification import ResearchQualificationRuntime, qualify_dataset
from tiaf.evaluation.forecast_research_contracts import (
    EmpiricalDataset,
    EmpiricalDatasetQualification,
    ResearchRightsConfig,
    RightsEnforcementPolicy,
)
from tiaf.evaluation.forecast_research_contracts import (
    QualificationReason as R,
)
from tiaf.evaluation.forecast_research_io import load_research_dataset
from tiaf.forecasting.engineering import EngineeringAdmissionError
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint
from tiaf.forecasting.research_contracts import FF1FeatureSchema

from ._capture_support import outcome_packet, packet
from ._research_support import ASSESSMENT, dataset, payload, repin_rights


def report(
    data: dict[str, Any] | None = None,
    *,
    enforcement: RightsEnforcementPolicy = RightsEnforcementPolicy.WARN_ONLY,
) -> EmpiricalDatasetQualification:
    runtime = ResearchQualificationRuntime(
        ResearchRightsConfig(rights_enforcement_policy=enforcement)
    )
    return runtime.qualify(
        dataset() if data is None else EmpiricalDataset.model_validate(data), assessed_at=ASSESSMENT
    )


def test_clean_32_sessions_and_exact_lookback_boundary() -> None:
    result = report()
    assert result.verdicts == ("SYNTHETIC_ENGINEERING_ONLY",)
    assert (
        result.requested_observations,
        result.eligible_observations,
        result.excluded_observations,
    ) == (32, 11, 21)
    assert len(result.bars) == 32
    assert all(not b.reasons for b in result.bars)
    assert result.observations[19].reasons == (R.INSUFFICIENT_LOOKBACK,)
    assert result.observations[20].eligible
    assert result.observations[-1].reasons == (R.TARGET_UNAVAILABLE,)
    assert {c.reason: c.count for c in result.reason_counts} == {
        R.INSUFFICIENT_LOOKBACK: 20,
        R.TARGET_UNAVAILABLE: 1,
    }
    assert not result.empirical_fitting_authorized
    assert all(o.label is None for o in result.observations)


def test_all_five_exact_a2_formulas_and_order() -> None:
    observation = report().observations[20]
    features = observation.features
    assert features is not None
    close = list(range(100, 121))
    returns = [math.log(b) - math.log(a) for a, b in zip(close, close[1:])]
    expected = (
        math.log(120) - math.log(119),
        math.log(120) - math.log(115),
        100 * (120 - statistics.mean(close[-20:])) / statistics.mean(close[-20:]),
        statistics.stdev(returns) * math.sqrt(252) * 100,
        120 / statistics.mean(close[:-1]),
    )
    assert features.values == pytest.approx(expected, abs=1e-12)
    assert tuple(s.name for s in features.feature_schema.features) == (
        "ret_1",
        "ret_5",
        "sma20_distance",
        "realized_vol_20",
        "relative_volume",
    )
    assert observation.window is not None
    assert observation.window.reference.value == Decimal("120")
    assert observation.information_cutoff == observation.window.reference.observed_at + timedelta(
        minutes=30
    )
    assert observation.as_of == observation.information_cutoff + timedelta(minutes=5)
    assert observation.observation_id == "ff-observation:" + semantic_fingerprint(
        {
            "target": dataset().target,
            "window": observation.window,
            "information_cutoff": observation.information_cutoff,
            "as_of": observation.as_of,
        }
    )


@pytest.mark.parametrize(
    "field",
    [
        "local_research",
        "model_training",
        "derived_feature_storage",
        "evaluation_artifact_retention",
        "replay_evidence_retention",
    ],
)
@pytest.mark.parametrize("state", ["UNKNOWN", "NOT_QUALIFIED"])
def test_every_required_right_must_be_explicitly_qualified(field: str, state: str) -> None:
    data = payload()
    data["rights"][field] = state
    repin_rights(data)
    result = report(data, enforcement=RightsEnforcementPolicy.ENFORCE)
    assert "HOLD_DATA_RIGHTS" in result.verdicts
    assert result.eligible_observations == 0
    assert all(R.RIGHTS_UNQUALIFIED in o.reasons for o in result.observations)
    assert not result.empirical_fitting_authorized


@pytest.mark.parametrize("fault", ["missing_basis", "expired", "scope", "pin", "capture"])
def test_rights_require_scoped_pinned_basis(fault: str) -> None:
    data = payload()
    if fault == "missing_basis":
        data["rights"]["basis_refs"] = []
    elif fault == "expired":
        data["rights"]["valid_until"] = "2022-01-01T00:00:00+05:30"
    elif fault == "scope":
        data["rights"]["coverage_start"] = "2021-02-01"
    elif fault == "capture":
        data["rights"]["source_artifact"]["fingerprint"] = "0" * 64
    if fault != "pin":
        repin_rights(data)
    else:
        data["source"]["rights_ref"]["fingerprint"] = "0" * 64
    assert "HOLD_DATA_RIGHTS" in report(data, enforcement=RightsEnforcementPolicy.ENFORCE).verdicts


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("high", "99", R.INVALID_BAR),
        ("low", "121", R.INVALID_BAR),
        ("close", "0", R.INVALID_BAR),
        ("open", None, R.INVALID_BAR),
        ("close", "1e-400", R.INVALID_BAR),
        ("close", "1e400", R.INVALID_BAR),
        ("final", False, R.INVALID_BAR),
        ("volume", -1, R.INVALID_VOLUME),
        ("volume", 2**63, R.INVALID_VOLUME),
        ("volume", None, R.MISSING_VOLUME),
        ("provider_security_id", "wrong", R.SECURITY_IDENTITY),
        ("session_date", "2021-01-31", R.INVALID_SESSION),
        ("session_id", "session:absent", R.INVALID_SESSION),
        ("provenance", None, R.PROVENANCE_UNQUALIFIED),
    ],
)
def test_bad_rows_are_retained_with_specific_reasons(field: str, value: object, reason: R) -> None:
    data = payload()
    data["rows"][20][field] = value
    result = report(data)
    assert len(result.bars) == 32 and len(result.observations) == 32
    assert reason in result.bars[20].reasons
    assert not result.observations[20].eligible
    assert (
        result.requested_observations == result.eligible_observations + result.excluded_observations
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("open", float("nan")),
        ("high", "Infinity"),
        ("low", "NaN"),
        ("close", 120.0),
        ("close", True),
        ("volume", 1.5),
        ("volume", True),
        ("session_date", "2021-02-30"),
    ],
)
def test_corrupt_scalars_reject_without_coercion(field: str, value: object) -> None:
    data = payload()
    data["rows"][20][field] = value
    with pytest.raises(ValidationError):
        EmpiricalDataset.model_validate(data)


def test_missing_bar_does_not_compress_the_session_window() -> None:
    data = payload()
    del data["rows"][19]
    result = report(data)
    assert R.MISSING_SESSION in result.observations[20].reasons
    assert result.observations[20].features is None
    assert len(result.bars) == 31 and len(result.observations) == 32


@pytest.mark.parametrize("conflicting", [False, True])
def test_duplicate_capture_weight_once_or_conflict_explicit(conflicting: bool) -> None:
    data = payload()
    duplicate = dict(data["rows"][20], row_id="bar:duplicate")
    if conflicting:
        duplicate["volume"] = 999
    data["rows"].insert(21, duplicate)
    result = report(data)
    assert len(result.bars) == 33 and len(result.observations) == 32
    if conflicting:
        assert R.CONFLICTING_DUPLICATE in result.observations[20].reasons
    else:
        assert result.bars[20].reasons == (R.DUPLICATE_SESSION,)
        assert result.eligible_observations == 11
        assert result.observations[20].features == report().observations[20].features


def test_out_of_order_rows_are_not_silently_sorted() -> None:
    data = payload()
    data["rows"][0], data["rows"][1] = data["rows"][1], data["rows"][0]
    assert R.NON_CHRONOLOGICAL in report(data).reasons


def test_zero_current_volume_is_factual_zero_but_zero_baseline_excludes() -> None:
    data = payload()
    data["rows"][20]["volume"] = 0
    features = report(data).observations[20].features
    assert features is not None and features.values[-1] == 0
    for row in data["rows"][:20]:
        row["volume"] = 0
    assert R.ZERO_VOLUME_BASELINE in report(data).observations[20].reasons


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("state", "UNKNOWN", R.CORPORATE_ACTION_UNRESOLVED),
        ("complete", False, R.CORPORATE_ACTION_UNRESOLVED),
        ("coverage", "UNKNOWN", R.CORPORATE_ACTION_UNRESOLVED),
        ("coverage", "AFFECTED", R.CORPORATE_ACTION_AFFECTED),
        ("basis", "ADJUSTED", R.PRICE_BASIS_UNSUPPORTED),
    ],
)
def test_action_uncertainty_and_qualified_adjusted_basis_never_silently_adjust(
    field: str,
    value: object,
    reason: R,
) -> None:
    data = payload()
    data["actions"][0][field] = value
    result = report(data)
    assert reason in result.reasons
    assert result.eligible_observations == 0
    assert "HOLD_CORPORATE_ACTIONS" in result.verdicts


@pytest.mark.parametrize("actions", [[], "overlap"])
def test_no_actions_list_is_not_proof_of_unaffected(actions: object) -> None:
    data = payload()
    data["actions"] = [] if actions == [] else data["actions"] * 2
    assert R.CORPORATE_ACTION_UNRESOLVED in report(data).reasons


@pytest.mark.parametrize(
    "fault", ["wrong_symbol", "exchange", "ambiguous", "unknown", "late_master"]
)
def test_identity_is_not_guessed_or_retroactively_known(fault: str) -> None:
    data = payload()
    resolution = data["security"]["resolution"]
    if fault in ("wrong_symbol", "exchange"):
        field, value = ("symbol", "HDFCBANK") if fault == "wrong_symbol" else ("exchange", "BSE")
        resolution["resolved"]["instrument"][field] = value
        resolution["matches"][0]["instrument"][field] = value
    elif fault == "ambiguous":
        resolution.update(resolved=None, ambiguous=True)
        resolution["matches"].append(dict(resolution["matches"][0], provider_instrument_id="other"))
    elif fault == "unknown":
        data["security"]["state"] = "UNKNOWN"
    else:
        resolution["observed_at"] = ASSESSMENT.isoformat()
    result = report(data)
    assert result.eligible_observations == 0
    assert (
        R.KNOWLEDGE_CUTOFF_VIOLATION if fault == "late_master" else R.SECURITY_IDENTITY
    ) in result.reasons


@pytest.mark.parametrize("fault", ["unknown", "no_authority", "ineligible", "late_notice"])
def test_calendar_requires_complete_known_authority(fault: str) -> None:
    data = payload()
    if fault == "unknown":
        data["calendar"]["state"] = "UNKNOWN"
    elif fault == "no_authority":
        data["calendar"]["authority_refs"] = []
    elif fault == "ineligible":
        data["calendar"]["schedules"][0]["sessions"][20]["subject_eligible"] = False
    else:
        notice = dict(data["calendar"]["schedules"][0]["source"])
        for key in ("available_at", "acquired_at", "admitted_at"):
            notice[key] = ASSESSMENT.isoformat()
        data["calendar"]["schedules"][0]["exception_notice_refs"] = [notice]
    assert report(data).eligible_observations == 0


@pytest.mark.parametrize("source_path", ["bar", "action", "calendar", "master"])
def test_today_downloaded_or_late_revised_evidence_does_not_pass_historical_cutoff(
    source_path: str,
) -> None:
    data = payload()
    source = {
        "bar": data["rows"][20]["provenance"],
        "action": data["actions"][0]["evidence"],
        "calendar": data["calendar"]["schedules"][0]["source"],
        "master": data["security"]["evidence"],
    }[source_path]
    for key in ("available_at", "acquired_at", "admitted_at"):
        source[key] = ASSESSMENT.isoformat()
    result = report(data)
    assert not result.observations[20].eligible
    assert "HOLD_PIT_PROVENANCE" in result.verdicts


def test_future_target_price_never_changes_earlier_features_or_observation() -> None:
    original = report()
    data = payload()
    data["rows"][21].update(open="200", high="201", low="199", close="200", volume=20000)
    changed = report(data)
    assert original.observations[20] == changed.observations[20]
    assert original.observations[21].features != changed.observations[21].features
    assert original.fingerprint != changed.fingerprint


def test_missing_maturation_does_not_invent_a_deadline() -> None:
    data = payload()
    data["maturation"] = []
    result = report(data)
    assert R.MATURATION_UNQUALIFIED in result.observations[20].reasons
    assert result.observations[20].window is None


def test_deterministic_fingerprints_roundtrip_and_real_computation_clock() -> None:
    first, second = report(), report()
    assert first.fingerprint == second.fingerprint
    assert first.feature_set_fingerprint == second.feature_set_fingerprint
    assert EmpiricalDatasetQualification.model_validate_json(canonical_json(first)) == first
    assert EmpiricalDataset.model_validate_json(canonical_json(dataset())) == dataset()
    later = qualify_dataset(dataset(), assessed_at=ASSESSMENT + timedelta(hours=1))
    assert first.fingerprint != later.fingerprint
    assert first.feature_set_fingerprint == later.feature_set_fingerprint
    assert first.observations[20].fingerprint == later.observations[20].fingerprint
    changed = payload()
    changed["rows"][20]["volume"] = 999
    assert report(changed).feature_set_fingerprint != first.feature_set_fingerprint
    assert "2026-09-19T12:00:00+05:30" in canonical_json(first)


@pytest.mark.parametrize(
    "fault", ["counts", "seal", "verdict", "rights", "policy", "schema", "slot"]
)
def test_sealed_report_and_fixed_policy_cannot_be_forged(fault: str) -> None:
    data = report().model_dump(mode="json")
    if fault == "counts":
        data["eligible_observations"] += 1
    elif fault == "seal":
        data["fingerprint"] = "0" * 64
    elif fault == "verdict":
        data["verdicts"] = ["QUALIFIED_FOR_FF1_RESEARCH"]
        data.pop("fingerprint")
    elif fault == "rights":
        data["empirical_fitting_authorized"] = True
    elif fault == "policy":
        data["policy"] = "other"
    elif fault == "schema":
        data["feature_schema"]["features"].reverse()
    else:
        data["observations"][20]["slot_id"] = "ff1-slot:wrong"
    with pytest.raises(ValidationError):
        EmpiricalDatasetQualification.model_validate(data)


def test_frozen_semantic_collections_and_naive_clock_rejection() -> None:
    schema = FF1FeatureSchema()
    assert isinstance(schema.features, tuple)
    assert isinstance(schema.model_dump(mode="json")["features"], list)
    with pytest.raises(ValidationError):
        schema.feature_schema_version = "2.0"  # type: ignore[assignment]
    with pytest.raises(ValidationError):
        qualify_dataset(dataset(), assessed_at=ASSESSMENT.replace(tzinfo=None))
    converted = qualify_dataset(dataset(), assessed_at=ASSESSMENT.astimezone(UTC))
    assert converted == report()


def test_bounded_local_json_reader_and_no_automatic_output(tmp_path: Path) -> None:
    path = tmp_path / "supplied.json"
    path.write_text(canonical_json(dataset()), encoding="utf-8")
    assert load_research_dataset(path, dataset_id=dataset().dataset_id) == dataset()
    with pytest.raises(ValueError, match="ID_MISMATCH"):
        load_research_dataset(path, dataset_id="dataset:wrong")
    link = tmp_path / "link.json"
    link.symlink_to(path)
    with pytest.raises(EngineeringAdmissionError):
        load_research_dataset(link, dataset_id=dataset().dataset_id)
    with pytest.raises(EngineeringAdmissionError):
        load_research_dataset(Path("https://example.com/file"), dataset_id=dataset().dataset_id)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["link.json", "supplied.json"]


@pytest.mark.parametrize("price,label", [("106", 1), ("104", 0), ("105", 0)])
def test_label_seam_uses_existing_ground_truth_not_second_comparator(
    price: str, label: int
) -> None:
    capture, artifacts = packet()
    outcome, _ = outcome_packet(capture, artifacts, price=Decimal(price))
    assert outcome.label == label
    assert all(o.label is None for o in report().observations)
