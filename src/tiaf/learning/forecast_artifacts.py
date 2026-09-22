"""FF-1.2 data-only research artifacts and dependency-free reconstruction.

These additive research contracts do not widen the synthetic FF-0 identities.
Full capture fingerprints include audit clocks; scientific fingerprints do not.
"""

import math
from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import Field, StrictFloat, StrictInt, model_validator

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.identity import ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.research_contracts import ResearchContract, ResearchDate
from tiaf.planner.models import Sha256

Finite = Annotated[StrictFloat, Field(allow_inf_nan=False)]
Five = tuple[Finite, Finite, Finite, Finite, Finite]
FeatureOrder = tuple[
    Literal["ret_1"],
    Literal["ret_5"],
    Literal["sma20_distance"],
    Literal["realized_vol_20"],
    Literal["relative_volume"],
]
FEATURE_ORDER: FeatureOrder = (
    "ret_1",
    "ret_5",
    "sma20_distance",
    "realized_vol_20",
    "relative_volume",
)


class SealedResearch(ResearchContract):
    fingerprint: Sha256 | None = None

    @model_validator(mode="after")
    def seal(self) -> Self:
        expected = semantic_fingerprint(self.model_dump(exclude={"fingerprint"}))
        if self.fingerprint is not None and self.fingerprint != expected:
            raise ValueError("TRAINING_ARTIFACT_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", expected)
        return self


class LogisticConfig(SealedResearch):
    penalty: Literal["l2"] = "l2"
    C: Annotated[StrictFloat, Field(ge=1.0, le=1.0)] = 1.0
    solver: Literal["lbfgs"] = "lbfgs"
    tol: Annotated[StrictFloat, Field(ge=1e-8, le=1e-8)] = 1e-8
    max_iter: Literal[1000] = 1000
    fit_intercept: Literal[True] = True
    class_weight: None = None
    dual: Literal[False] = False
    warm_start: Literal[False] = False
    random_state: Literal[1729] = 1729
    n_jobs: Literal[1] = 1


class ScalerConfig(SealedResearch):
    implementation: Literal["StandardScaler"] = "StandardScaler"
    with_mean: Literal[True] = True
    with_std: Literal[True] = True
    ddof: Literal[0] = 0
    constant_policy: Literal["SKLEARN_1_7_2_SCALE_ONE"] = "SKLEARN_1_7_2_SCALE_ONE"
    imputation: Literal["NONE"] = "NONE"


class TrainingGrant(SealedResearch):
    """Explicit COLD job authority and dependency/provenance pins, never a forecast grant."""

    grant_id: str = Field(min_length=1, max_length=100)
    basis: Literal["QUALIFIED_ADJUSTED_RESEARCH", "SYNTHETIC_ENGINEERING"]
    qualification_fingerprint: Sha256
    dataset_fingerprint: Sha256
    research_profile_fingerprint: Sha256
    feature_schema_fingerprint: Sha256
    holdout_year: Literal[2025] = 2025
    allowed_folds: tuple[Literal[2021], Literal[2022], Literal[2023], Literal[2024]] = (
        2021,
        2022,
        2023,
        2024,
    )
    protocol_fingerprint: Sha256
    dependency_lock_fingerprint: Sha256
    code_fingerprint: Sha256
    issued_at: ForecastDateTime
    max_fits: Literal[4] = 4
    fit_timeout_seconds: Literal[60] = 60
    campaign_timeout_seconds: Literal[600] = 600
    worker_memory_mib: Literal[512] = 512
    numeric_threads: Literal[1] = 1
    max_attempts_per_fold: Literal[1] = 1


FIFTH_CUTOFF = datetime(2024, 12, 31, 9, 15, tzinfo=TIAF_TIMEZONE)


class FifthFoldGrant(SealedResearch):
    """Separate pre-open authority. Never widens the four-development-fold grant."""

    grant_id: Literal["ff1.pre_holdout.fifth_fold/1.0"] = "ff1.pre_holdout.fifth_fold/1.0"
    basis: Literal["QUALIFIED_ADJUSTED_RESEARCH", "SYNTHETIC_ENGINEERING"]
    qualification_fingerprint: Sha256
    qualification_blob: Sha256
    dataset_fingerprint: Sha256
    research_profile_fingerprint: Sha256
    feature_schema_fingerprint: Sha256
    protocol_fingerprint: Sha256
    authority_document_fingerprint: Sha256
    dependency_lock_fingerprint: Sha256
    code_fingerprint: Sha256
    issued_at: ForecastDateTime
    cutoff: ForecastDateTime = FIFTH_CUTOFF
    allowed_folds: tuple[Literal[2025]] = (2025,)
    pre_holdout_fifth_fold_fit: Literal["AUTHORIZED"] = "AUTHORIZED"
    post_holdout_refit: Literal["FORBIDDEN"] = "FORBIDDEN"
    holdout_status: Literal["SEALED"] = "SEALED"
    protected_outcome_access: Literal["NONE"] = "NONE"
    final_evaluation_authorized: Literal[False] = False
    forecast_generation: Literal["DEFERRED_TO_ONE_SHOT_EVALUATION"] = (
        "DEFERRED_TO_ONE_SHOT_EVALUATION"
    )
    max_fits: Literal[1] = 1
    max_scaler_fits: Literal[1] = 1
    max_attempts_per_fold: Literal[1] = 1
    fit_timeout_seconds: Literal[60] = 60
    campaign_timeout_seconds: Literal[600] = 600
    worker_memory_mib: Literal[512] = 512
    numeric_threads: Literal[1] = 1

    @model_validator(mode="after")
    def fixed_cutoff(self) -> Self:
        if self.cutoff != FIFTH_CUTOFF or self.issued_at <= self.cutoff:
            raise ValueError("FIFTH_FOLD_CUTOFF_OR_AUTHORITY_CLOCK")
        return self


class PopulationAudit(ResearchContract):
    """Disjoint whole-population buckets; purge total includes the embargo subset."""

    requested: Annotated[StrictInt, Field(ge=1, le=4096)]
    train: Annotated[StrictInt, Field(ge=0)]
    positive: Annotated[StrictInt, Field(ge=0)]
    zero: Annotated[StrictInt, Field(ge=0)]
    ineligible: Annotated[StrictInt, Field(ge=0)]
    purge_only: Annotated[StrictInt, Field(ge=0)]
    embargo: Annotated[StrictInt, Field(ge=0)]
    sealed: Annotated[StrictInt, Field(ge=0)]
    later_unsealed: Annotated[StrictInt, Field(ge=0)]

    @model_validator(mode="after")
    def counts(self) -> Self:
        if self.positive + self.zero != self.train or self.requested != (
            self.train
            + self.ineligible
            + self.purge_only
            + self.embargo
            + self.sealed
            + self.later_unsealed
        ):
            raise ValueError("TRAINING_DENOMINATOR_MISMATCH")
        return self


class FoldManifest(SealedResearch):
    subject: Literal["RELIANCE:NSE:NSE_EQUITY:EQUITY"] = "RELIANCE:NSE:NSE_EQUITY:EQUITY"
    target_id: Literal["equity.next_session_close.return_gt_zero/1.0"] = (
        "equity.next_session_close.return_gt_zero/1.0"
    )
    feature_schema_id: Literal["ff1.reliance.a2_daily_five/1.0"] = "ff1.reliance.a2_daily_five/1.0"
    feature_order: FeatureOrder = FEATURE_ORDER
    grant: TrainingGrant | FifthFoldGrant
    fold_id: Literal[2021, 2022, 2023, 2024, 2025]
    fit_cutoff: ForecastDateTime
    embargo_date: ResearchDate
    train_start: ResearchDate
    train_end: ResearchDate
    observation_ids: tuple[str, ...] = Field(min_length=1, max_length=4096)
    observation_order_fingerprint: Sha256
    training_values_fingerprint: Sha256
    label_identity: Literal["FF1_1A_QUALIFIED_ADJUSTED_ENDPOINT_DIRECTION"] = (
        "FF1_1A_QUALIFIED_ADJUSTED_ENDPOINT_DIRECTION"
    )
    price_series_basis: Literal["CORPORATE_ACTION_ADJUSTED"] = "CORPORATE_ACTION_ADJUSTED"
    purge_policy: Literal["TARGET_AND_AVAILABILITY_STRICTLY_BEFORE_EMBARGO_OPEN"] = (
        "TARGET_AND_AVAILABILITY_STRICTLY_BEFORE_EMBARGO_OPEN"
    )
    audit: PopulationAudit
    model_config_value: LogisticConfig = Field(default_factory=LogisticConfig)
    scaler_config: ScalerConfig = Field(default_factory=ScalerConfig)

    @model_validator(mode="after")
    def membership(self) -> Self:
        ids = self.observation_ids
        if (
            self.fold_id not in self.grant.allowed_folds
            or (isinstance(self.grant, FifthFoldGrant) and self.fit_cutoff != FIFTH_CUTOFF)
            or len(ids) != self.audit.train
            or len(ids) != len(set(ids))
            or self.observation_order_fingerprint != semantic_fingerprint(ids)
            or self.train_start > self.train_end
            or self.train_end >= self.embargo_date
            or self.embargo_date != self.fit_cutoff.date()
            or self.fit_cutoff.year != self.fold_id - 1
        ):
            raise ValueError("TRAINING_MEMBERSHIP_MISMATCH")
        return self

    @property
    def scientific_fingerprint(self) -> str:
        # The training-values hash excludes acquisition/qualification/job clocks.
        return semantic_fingerprint(
            {
                "dataset": self.grant.dataset_fingerprint,
                "profile": self.grant.research_profile_fingerprint,
                "schema": self.grant.feature_schema_fingerprint,
                "values": self.training_values_fingerprint,
                "order": self.observation_order_fingerprint,
                "fold": self.fold_id,
                "cutoff": self.fit_cutoff,
                "model": self.model_config_value,
                "scaler": self.scaler_config,
                "code": self.grant.code_fingerprint,
                "lock": self.grant.dependency_lock_fingerprint,
            }
        )


class TrainingRow(ResearchContract):
    observation_id: str
    reference_date: ResearchDate
    target_date: ResearchDate
    label_available_at: ForecastDateTime
    values: Five
    label: Annotated[StrictInt, Field(ge=0, le=1)]

    @model_validator(mode="after")
    def protected(self) -> Self:
        if not 2018 <= self.reference_date.year < 2025 or not (
            self.reference_date < self.target_date and self.target_date.year < 2025
        ):
            raise ValueError("HOLDOUT_NOT_AUTHORIZED")
        if self.observation_id != f"ff1-adjusted:RELIANCE:{self.reference_date.isoformat()}":
            raise ValueError("OBSERVATION_ID_MISMATCH")
        return self


class TrainingInput(ResearchContract):
    manifest: FoldManifest
    rows: tuple[TrainingRow, ...] = Field(min_length=1, max_length=4096)

    @model_validator(mode="after")
    def exact_input(self) -> Self:
        m = self.manifest
        dates = tuple(r.reference_date for r in self.rows)
        if (
            tuple(r.observation_id for r in self.rows) != m.observation_ids
            or dates != tuple(sorted(set(dates)))
            or dates[0] != m.train_start
            or dates[-1] != m.train_end
            or semantic_fingerprint(self.rows) != m.training_values_fingerprint
            or sum(r.label for r in self.rows) != m.audit.positive
            or any(r.label_available_at >= m.fit_cutoff for r in self.rows)
        ):
            raise ValueError("TRAINING_INPUT_MISMATCH")
        return self


class ScalerArtifact(SealedResearch):
    config: ScalerConfig = Field(default_factory=ScalerConfig)
    feature_order: FeatureOrder = FEATURE_ORDER
    n: Annotated[StrictInt, Field(ge=500, le=4096)]
    means: Five
    variances: Five
    scales: Five
    constant_columns: tuple[Annotated[StrictInt, Field(ge=0, le=4)], ...]
    training_fingerprint: Sha256

    @model_validator(mode="after")
    def valid_scale(self) -> Self:
        if len(set(self.constant_columns)) != len(self.constant_columns):
            raise ValueError("DUPLICATE_CONSTANT_COLUMN")
        for i, (variance, scale) in enumerate(zip(self.variances, self.scales, strict=True)):
            if (
                variance < 0
                or scale <= 0
                or (i in self.constant_columns and scale != 1.0)
                or (
                    i not in self.constant_columns
                    and (variance == 0 or scale != math.sqrt(variance))
                )
            ):
                raise ValueError("INVALID_SCALER_PARAMETERS")
        return self


class LibraryVersions(ResearchContract):
    python: str = Field(min_length=1)
    sklearn: Literal["1.7.2"] = "1.7.2"
    numpy: Literal["2.3.3"] = "2.3.3"
    scipy: Literal["1.16.2"] = "1.16.2"
    joblib: Literal["1.5.2"] = "1.5.2"
    threadpoolctl: Literal["3.6.0"] = "3.6.0"
    numeric_backends: tuple[str, ...] = Field(min_length=1)


class Reconstruction(SealedResearch):
    evaluator: Literal["ff1.standardized_logit_sigmoid/1.0"] = "ff1.standardized_logit_sigmoid/1.0"
    scaler: ScalerArtifact
    coefficients: Five
    intercept: Finite
    classes: tuple[Literal[0], Literal[1]] = (0, 1)
    positive_event: Literal[1] = 1


class LogisticArtifact(SealedResearch):
    artifact_version: Literal["1.0"] = "1.0"
    forecaster_id: Literal["forecaster:logistic-regression"] = "forecaster:logistic-regression"
    model_family: Literal["LogisticRegression"] = "LogisticRegression"
    implementation_version: Literal["1.0"] = "1.0"
    role: Literal["CHALLENGER"] = "CHALLENGER"
    lifecycle: Literal["EXPERIMENTAL"] = "EXPERIMENTAL"
    probability_basis: Literal["RAW_UNCALIBRATED"] = "RAW_UNCALIBRATED"
    manifest: FoldManifest
    reconstruction: Reconstruction
    versions: LibraryVersions
    converged: Literal[True] = True
    n_iter: Annotated[StrictInt, Field(ge=1, lt=1000)]
    created_at: ForecastDateTime
    reconstruction_tolerance: Annotated[StrictFloat, Field(ge=1e-12, le=1e-12)] = 1e-12
    reconstruction_max_error: Annotated[Finite, Field(ge=0, le=1e-12)]
    reconstruction_checks: Literal[5] = 5

    @model_validator(mode="after")
    def linked(self) -> Self:
        s, m = self.reconstruction.scaler, self.manifest
        if (
            s.n != m.audit.train
            or s.config != m.scaler_config
            or s.training_fingerprint != m.scientific_fingerprint
            or self.created_at < m.grant.issued_at
        ):
            raise ValueError("MODEL_SCALER_LINEAGE_MISMATCH")
        return self

    @property
    def scientific_fingerprint(self) -> str:
        return semantic_fingerprint(
            {
                "training": self.manifest.scientific_fingerprint,
                "reconstruction": self.reconstruction,
                "versions": self.versions,
                "n_iter": self.n_iter,
                "identity": self.forecaster_id,
                "version": self.implementation_version,
            }
        )


def reconstruct(model: Reconstruction, values: Five) -> float:
    """Minimal numeric seam, not a forecast issuer or a training/evaluation path."""
    if len(values) != 5 or any(not math.isfinite(x) for x in values):
        raise ValueError("INVALID_RECONSTRUCTION_INPUT")
    s = model.scaler
    transformed = tuple(
        (x - m) / scale for x, m, scale in zip(values, s.means, s.scales, strict=True)
    )
    if any(not math.isfinite(x) for x in transformed):
        raise ValueError("NONFINITE_TRANSFORM")
    logit = sum(x * b for x, b in zip(transformed, model.coefficients, strict=True))
    logit += model.intercept
    if not math.isfinite(logit):
        raise ValueError("NONFINITE_LOGIT")
    if logit >= 0:
        return 1.0 / (1.0 + math.exp(-logit))
    exp = math.exp(logit)
    return exp / (1.0 + exp)
