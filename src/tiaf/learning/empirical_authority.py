"""FF-2.3 denied authority and outcome-blind custody metadata review.

This is NOT an empirical qualifier, grant issuer, loader or training capability.
Metadata consistency is necessary, never sufficient: even a consistent proposal
is denied. Existing synthetic fit admission remains unchanged. A later grant and
artifact-derived admission edge require a separately reviewed version.
"""

from datetime import datetime
from typing import Annotated, Literal, NoReturn

from pydantic import Field, StrictInt

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import ArtifactReference, ForecastDateTime, LogicalId
from tiaf.learning.forecast_artifacts import SealedResearch
from tiaf.planner.models import Sha256


class EmpiricalSourcePins(SealedResearch):
    """Exact immutable source metadata, not an artifact deserializer."""

    forecaster_id: LogicalId
    implementation_version: str
    model: Sha256
    model_bytes: Sha256
    scaler: Sha256
    scaler_bytes: Sha256
    training_run: Sha256
    training_manifest: Sha256
    feature_schema: Sha256
    dataset_bytes: Sha256
    qualification: Sha256
    qualification_bytes: Sha256
    source_manifest: Sha256
    profile: Sha256
    target: str
    subject: str
    acquired_at: ForecastDateTime
    training_cutoff: ForecastDateTime


class EmpiricalAuthorityResolution(SealedResearch):
    """A sealed refusal record. A fingerprint cannot manufacture permission."""

    record_kind: Literal["AUTHORITY_RESOLUTION_NOT_EXECUTION_GRANT"] = (
        "AUTHORITY_RESOLUTION_NOT_EXECUTION_GRANT"
    )
    authority_id: Literal["authority:ff2-empirical-resolution-001"] = (
        "authority:ff2-empirical-resolution-001"
    )
    experiment_id: Literal["experiment:ff2-reliance-sigmoid-001"] = (
        "experiment:ff2-reliance-sigmoid-001"
    )
    entry_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    recorded_at: ForecastDateTime
    protocol_bytes: Sha256
    parent_authority: Sha256
    source: EmpiricalSourcePins
    determination: Literal["EMPIRICAL_AUTHORITY_UNVERIFIABLE"] = "EMPIRICAL_AUTHORITY_UNVERIFIABLE"
    calibration_2022: Literal["UNVERIFIABLE"] = "UNVERIFIABLE"
    validation_2023_2024: Literal["UNVERIFIABLE"] = "UNVERIFIABLE"
    historical_rights: Literal["UNVERIFIED_WARN_ONLY_FF1_ONLY"] = "UNVERIFIED_WARN_ONLY_FF1_ONLY"
    empirical_grant: None = None
    empirical_execution_allowed: Literal[False] = False
    prospective_collection_allowed: Literal[False] = False
    protected_evaluation_allowed: Literal[False] = False
    promotion_allowed: Literal[False] = False
    max_executions_now: Literal[0] = 0
    reasons: tuple[LogicalId, ...] = (
        "authority:ff2-use-admission-missing",
        "authority:ff2-exact-fit-grant-missing",
        "custody:ff2-qualified-membership-missing",
        "custody:empirical-adapter-and-verifier-not-admitted",
    )


class DevelopmentCustodyMetadata(SealedResearch):
    """Outcome-blind proposal: referenced raw p and external y are NEVER decoded.

    Producer assertions are not trusted proofs. This shape cannot be passed to a
    fit worker. Actual numeric custody/admission remains a future gated edge.
    """

    observation_id: LogicalId
    experiment_id: LogicalId
    subject: str
    target: str
    horizon: str
    purpose: Literal["CALIBRATION", "VALIDATION", "PROTECTED"]
    exposure: Literal["KNOWN_DEVELOPMENT", "CONSUMED", "PROSPECTIVE", "UNKNOWN"]
    source: EmpiricalSourcePins
    origin: ForecastDateTime
    information_cutoff: ForecastDateTime
    target_open: ForecastDateTime
    target_close: ForecastDateTime
    feature_available_as_of: ForecastDateTime
    feature_dependency_clocks: Annotated[
        tuple[ForecastDateTime, ...], Field(min_length=1, max_length=4096)
    ]
    support_dependency_clocks: Annotated[tuple[ForecastDateTime, ...], Field(max_length=4096)] = ()
    feature_capture: ArtifactReference
    raw_capture: ArtifactReference
    generated_at: ForecastDateTime
    persisted_at: ForecastDateTime
    generation_code: Sha256
    expected_generation_code: Sha256
    regenerated_capture: ArtifactReference | None = None
    journal_entry: ArtifactReference
    expected_journal_entry: ArtifactReference
    journal_revision: Annotated[StrictInt, Field(ge=1)]
    expected_journal_revision: Annotated[StrictInt, Field(ge=1)]
    truth_observation_id: LogicalId
    truth_subject: str
    truth_target: str
    truth_target_open: ForecastDateTime
    truth_target_close: ForecastDateTime
    truth_available_as_of: ForecastDateTime
    truth_recorded_at: ForecastDateTime
    assessed_at: ForecastDateTime
    qualification_status: Literal["PROPOSED", "REJECTED", "UNKNOWN"] = "PROPOSED"


class CustodyMetadataReview(SealedResearch):
    resolution: Sha256
    records: tuple[Sha256, ...]
    admitted: Literal[False] = False
    numeric_access_allowed: Literal[False] = False
    reasons: tuple[str, ...]


def require_empirical_development_authority(
    supplied: EmpiricalAuthorityResolution,
) -> NoReturn:
    """Deny before ANY numeric load. There is intentionally no success branch."""
    EmpiricalAuthorityResolution.model_validate(supplied)
    raise ValueError("FF2_EMPIRICAL_AUTHORITY_NOT_GRANTED")


def review_development_metadata(
    supplied: EmpiricalAuthorityResolution,
    records: tuple[DevelopmentCustodyMetadata, ...],
) -> CustodyMetadataReview:
    """Bounded pure review, not persistent admission or positive qualification.

    Checks are against supplied metadata only. No boolean 'verified' flag can
    open empirical execution; even perfect joins retain the missing-grant denial.
    """
    resolution = EmpiricalAuthorityResolution.model_validate(supplied)
    if not 1 <= len(records) <= 4096:
        raise ValueError("FF2_CUSTODY_RECORD_BOUND")
    rows = tuple(DevelopmentCustodyMetadata.model_validate(row) for row in records)
    reasons = ["FF2_EMPIRICAL_AUTHORITY_NOT_GRANTED", "ARTIFACT_DERIVED_QUALIFICATION_REQUIRED"]
    seen_ids: set[str] = set()
    seen_slots: set[tuple[str, str, str, datetime]] = set()
    seen_captures: set[ArtifactReference] = set()
    for row in rows:
        reasons.extend(_metadata_reasons(resolution, row))
        # Do not let a changed ID, purpose or target-clock assertion duplicate an origin.
        slot = (row.experiment_id, row.subject, row.target, row.origin)
        if row.observation_id in seen_ids or slot in seen_slots or row.raw_capture in seen_captures:
            reasons.append("DUPLICATE_OBSERVATION_OR_CAPTURE")
        seen_ids.add(row.observation_id)
        seen_slots.add(slot)
        seen_captures.add(row.raw_capture)
    assert resolution.fingerprint is not None
    return CustodyMetadataReview(
        resolution=resolution.fingerprint,
        records=tuple(str(row.fingerprint) for row in rows),
        reasons=tuple(dict.fromkeys(reasons)),
    )


def _metadata_reasons(
    resolution: EmpiricalAuthorityResolution, row: DevelopmentCustodyMetadata
) -> tuple[str, ...]:
    source = resolution.source
    cutoff = datetime(2022, 12, 30, 9, 15, tzinfo=TIAF_TIMEZONE)
    history_end = datetime(2025, 1, 1, tzinfo=TIAF_TIMEZONE)
    dependencies = (
        row.origin,
        row.target_open,
        row.target_close,
        row.truth_available_as_of,
        *row.feature_dependency_clocks,
        *row.support_dependency_clocks,
    )
    checks = {
        "EXPERIMENT_MISMATCH": row.experiment_id == resolution.experiment_id,
        "SUBJECT_TARGET_HORIZON_MISMATCH": (row.subject, row.target, row.horizon)
        == (source.subject, source.target, "NEXT_SESSION_CLOSE"),
        "SOURCE_IDENTITY_OR_BYTES_MISMATCH": row.source == source,
        "WRONG_PERIOD_OR_PURPOSE": (row.purpose == "CALIBRATION" and row.origin.year == 2022)
        or (row.purpose == "VALIDATION" and row.origin.year in (2023, 2024)),
        "PROTECTED_OR_UNKNOWN_EXPOSURE": row.exposure == "KNOWN_DEVELOPMENT",
        "PROHIBITED_HISTORICAL_DEPENDENCY": all(d < history_end for d in dependencies),
        "TRAINING_OR_SCALER_OVERLAP": source.training_cutoff < row.origin,
        "FEATURE_OR_TEMPORAL_LEAKAGE": row.origin
        <= row.feature_available_as_of
        <= row.information_cutoff
        < row.target_open
        < row.target_close
        and all(d <= row.origin for d in row.feature_dependency_clocks)
        and all(d <= row.information_cutoff for d in row.support_dependency_clocks),
        "CALIBRATION_EMBARGO_OR_LABEL_LEAKAGE": row.purpose != "CALIBRATION"
        or max(row.origin, row.target_close, row.truth_available_as_of) < cutoff,
        "BACKDATED_ACTUAL_CLOCK": source.acquired_at
        <= row.generated_at
        <= row.persisted_at
        <= row.assessed_at
        and source.acquired_at <= row.truth_recorded_at <= row.assessed_at,
        "GROUND_TRUTH_JOIN_MISMATCH": (
            row.observation_id,
            row.subject,
            row.target,
            row.target_open,
            row.target_close,
        )
        == (
            row.truth_observation_id,
            row.truth_subject,
            row.truth_target,
            row.truth_target_open,
            row.truth_target_close,
        ),
        "IMMATURE_TRUTH": row.target_close <= row.truth_available_as_of <= row.assessed_at,
        "JOURNAL_REVISION_MISMATCH": row.journal_entry == row.expected_journal_entry
        and row.journal_revision == row.expected_journal_revision,
        "REGENERATION_IDENTITY_MISMATCH": row.generation_code == row.expected_generation_code
        and (row.regenerated_capture is None or row.raw_capture == row.regenerated_capture),
        "CUSTODY_STATUS_REJECTED": row.qualification_status == "PROPOSED",
    }
    return tuple(reason for reason, passed in checks.items() if not passed)
