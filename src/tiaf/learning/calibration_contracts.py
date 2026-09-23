"""FLC-5 internal calibration identities and a bounded FF wrapper profile.

Fit contracts are proposals only. Executable examples admit the authored
synthetic population, never market observations or consumed outcome evidence.
"""

from typing import Annotated, Final, Literal, Self

from pydantic import Field, StrictInt, model_validator

from tiaf.forecasting.contracts import ForecastComposition, ForecastEdge
from tiaf.forecasting.enums import ForecastRealizationMode, ForecastStatus
from tiaf.forecasting.forecaster_seams import CalibratableOutput, ForecasterKey
from tiaf.forecasting.identity import (
    ArtifactReference,
    ForecastDateTime,
    LogicalId,
    semantic_fingerprint,
)
from tiaf.planner.models import Sha256

from .forecast_artifacts import Finite, SealedResearch
from .forecaster_training import reference

Probability = Annotated[Finite, Field(ge=0, le=1)]
VERSION: Final = "flc5.reference.1"
SOURCE_KEY = ForecasterKey(
    forecaster_id="forecaster:flc5-synthetic-reference", implementation_version=VERSION
)
PROBABILITIES = (0.0, 0.2, 0.5, 0.8, 1.0)


def synthetic_pin(name: str) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=f"flc5:{name}",
        artifact_version=VERSION,
        fingerprint=semantic_fingerprint((VERSION, name)),
    )


class CalibrationTarget(SealedResearch):
    target_id: LogicalId
    target_version: str = Field(min_length=1, max_length=40)
    positive_event: LogicalId
    horizon: LogicalId
    cutoff_policy: ArtifactReference
    input_semantics: Literal["RAW_BINARY_PROBABILITY"] = "RAW_BINARY_PROBABILITY"
    output_semantics: Literal["TRANSFORMED_BINARY_PROBABILITY"] = "TRANSFORMED_BINARY_PROBABILITY"


def synthetic_target() -> CalibrationTarget:
    return CalibrationTarget(
        target_id="synthetic:next-step",
        target_version="1.0",
        positive_event="synthetic:positive",
        horizon="synthetic:one-step",
        cutoff_policy=synthetic_pin("cutoff-policy"),
    )


class CalibrationComponent(SealedResearch):
    calibrator_id: LogicalId
    implementation_version: str = Field(min_length=1, max_length=40)
    family: LogicalId
    target: CalibrationTarget
    source_forecaster: ForecasterKey
    source_model: ArtifactReference
    source_preprocessor: ArtifactReference | None = None
    mode: ForecastRealizationMode
    configuration_fingerprint: Sha256
    created_at: ForecastDateTime


class CalibrationEvidence(SealedResearch):
    """Proposal lineage, not verified qualification or a fit grant."""

    experiment_id: LogicalId
    source_experiment_id: LogicalId
    protocol: ArtifactReference
    source_forecast_population: ArtifactReference
    training_population: ArtifactReference
    qualification: ArtifactReference
    evidence_policy: ArtifactReference
    experiment_state: Literal["OPEN"] = "OPEN"
    holdout_state: Literal["NONE"] = "NONE"
    consumed_2025_reuse: Literal[False] = False
    same_experiment_rescue: Literal[False] = False
    qualification_verified: Literal[False] = False
    scope: Literal["SYNTHETIC_REFERENCE_ONLY"] = "SYNTHETIC_REFERENCE_ONLY"

    @model_validator(mode="after")
    def new_design(self) -> Self:
        if self.experiment_id == self.source_experiment_id:
            raise ValueError("SAME_EXPERIMENT_CALIBRATION_RESCUE_FORBIDDEN")
        expected = {
            "protocol": "reference-protocol",
            "source_forecast_population": "source-population",
            "training_population": "authored-parameter-population",
            "qualification": "synthetic-engineering-declaration",
            "evidence_policy": "synthetic-only",
        }
        if any(getattr(self, key) != synthetic_pin(name) for key, name in expected.items()):
            raise ValueError("ONLY_AUTHORED_SYNTHETIC_EVIDENCE_ADMITTED")
        return self


class CalibrationFitRequest(SealedResearch):
    request_id: LogicalId
    component: CalibrationComponent
    evidence: CalibrationEvidence
    created_at: ForecastDateTime
    status: Literal["PROPOSED_NOT_AUTHORIZED"] = "PROPOSED_NOT_AUTHORIZED"
    fit_authorized: Literal[False] = False


class CalibrationFitResult(SealedResearch):
    request: ArtifactReference
    status: Literal["NOT_EXECUTED"] = "NOT_EXECUTED"
    artifact: None = None
    activation: Literal[False] = False


class CalibrationArtifactIdentity(SealedResearch):
    """Reusable fitted-artifact identity shape; FLC-5 authors reference parameters only."""

    component: CalibrationComponent
    evidence: CalibrationEvidence
    origin: Literal["AUTHORED_SYNTHETIC_REFERENCE"] = "AUTHORED_SYNTHETIC_REFERENCE"
    fit_performed: Literal[False] = False
    promotion: Literal[False] = False
    qualified_for_advisory_use: Literal[False] = False


class CalibrationArtifact(SealedResearch):
    artifact_adapter_version: Literal["flc5.reference.1"] = VERSION
    identity: CalibrationArtifactIdentity
    # A future family gets its own payload codec; no giant optional-field model.
    knots: tuple[tuple[Probability, Probability], ...] = Field(min_length=2, max_length=16)
    available_at: ForecastDateTime
    valid_until: ForecastDateTime

    @model_validator(mode="after")
    def table(self) -> Self:
        xs = tuple(x for x, _ in self.knots)
        ys = tuple(y for _, y in self.knots)
        if xs[0] != 0.0 or xs[-1] != 1.0 or xs != tuple(sorted(set(xs))):
            raise ValueError("CALIBRATION_TABLE_MUST_COVER_UNIT_INTERVAL")
        if ys != tuple(sorted(ys)):
            raise ValueError("CALIBRATION_TABLE_MUST_BE_MONOTONIC")
        component = self.identity.component
        if component.configuration_fingerprint != semantic_fingerprint(self.knots):
            raise ValueError("CALIBRATION_CONFIGURATION_MISMATCH")
        if not component.created_at <= self.available_at < self.valid_until:
            raise ValueError("CALIBRATION_ARTIFACT_CLOCK_MISMATCH")
        return self


class CalibrationSource(SealedResearch):
    """Captured engineering output, structurally limited to five authored values."""

    index: Annotated[StrictInt, Field(ge=0, le=4)]
    forecast_id: LogicalId
    compatible: CalibratableOutput
    primitive_composition: ForecastComposition
    target: CalibrationTarget
    information_cutoff: ForecastDateTime
    computed_at: ForecastDateTime
    scope: Literal["SYNTHETIC_REFERENCE_ONLY"] = "SYNTHETIC_REFERENCE_ONLY"

    @model_validator(mode="after")
    def authored(self) -> Self:
        node = self.primitive_composition.nodes[0]
        if (
            self.forecast_id != f"flc5:authored-{self.index}"
            or self.compatible.forecaster.key != SOURCE_KEY
            or self.compatible.input_forecast != synthetic_pin(f"authored-{self.index}")
            or self.compatible.output.probability != PROBABILITIES[self.index]
            or self.target != synthetic_target()
            or node.artifact_ref != synthetic_pin("source-model")
            or node.realization_mode is not ForecastRealizationMode.SIMULATED_ISSUANCE
        ):
            raise ValueError("CALIBRATION_SOURCE_NOT_AUTHORED_SYNTHETIC_REFERENCE")
        if self.computed_at < self.information_cutoff:
            raise ValueError("CALIBRATION_SOURCE_CLOCK_MISMATCH")
        return self


class CalibrationApplyRequest(SealedResearch):
    request_id: LogicalId
    source_reference: ArtifactReference
    source_forecast_id: LogicalId
    source_forecaster: ForecasterKey
    component: CalibrationComponent
    artifact_reference: ArtifactReference
    target: CalibrationTarget
    mode: ForecastRealizationMode
    policy: ArtifactReference
    created_at: ForecastDateTime
    scope: Literal["SYNTHETIC_REFERENCE_ONLY"] = "SYNTHETIC_REFERENCE_ONLY"
    evidence_policy: Literal["NO_OUTCOME_QUERY"] = "NO_OUTCOME_QUERY"
    fit_authorized: Literal[False] = False
    production_apply_authorized: Literal[False] = False
    consumed_holdout_reuse: Literal[False] = False


class CalibrationComposition(SealedResearch):
    """Fixed CALIBRATE(child) profile in the FF architecture, no graph executor.

    The unchanged singleton child remains complete. ForecastEdge retains the
    accepted typed edge; this profile admits exactly one calibration wrapper.
    """

    profile: Literal["flc5.calibrate-singleton.1"] = "flc5.calibrate-singleton.1"
    primitive: ForecastComposition
    primitive_identity: ForecasterKey
    component: CalibrationComponent
    calibration_artifact: ArtifactReference
    target: CalibrationTarget
    policy: ArtifactReference
    edge: ForecastEdge
    root_node_id: LogicalId

    @model_validator(mode="after")
    def closure(self) -> Self:
        child = self.primitive.nodes[0]
        if (
            self.edge.source_node_id != child.node_id
            or self.edge.target_node_id != self.component.calibrator_id
            or self.root_node_id != self.component.calibrator_id
            or self.root_node_id == child.node_id
            or self.primitive_identity != self.component.source_forecaster
            or child.artifact_ref != self.component.source_model
            or child.realization_mode != self.component.mode
            or self.target != self.component.target
        ):
            raise ValueError("CALIBRATION_COMPOSITION_LINEAGE_MISMATCH")
        return self

    @property
    def composition_id(self) -> str:
        return f"flc5-composition:{self.fingerprint}"


class CalibrationApplyResult(SealedResearch):
    request: CalibrationApplyRequest
    source: CalibrationSource
    status: ForecastStatus
    raw_probability: Probability
    calibrated_probability: Probability | None = None
    composition: CalibrationComposition | None = None
    reason: LogicalId | None = None
    artifact_checked: Literal["PRESENT_VERIFIED", "UNAVAILABLE", "NOT_CHECKED"]
    lineage: tuple[ArtifactReference, ...] = Field(min_length=3, max_length=8)
    interpretation: Literal["SYNTHETIC_TRANSFORM_NOT_CALIBRATION_QUALIFICATION"] = (
        "SYNTHETIC_TRANSFORM_NOT_CALIBRATION_QUALIFICATION"
    )
    evaluation_performed: Literal[False] = False
    approval: Literal[False] = False
    promotion: Literal[False] = False
    activation: Literal[False] = False

    @model_validator(mode="after")
    def observation(self) -> Self:
        generated = self.status is ForecastStatus.GENERATED
        if self.status is ForecastStatus.ABSTAINED:
            raise ValueError("CALIBRATION_ABSTENTION_NOT_SUPPORTED")
        if generated != (self.calibrated_probability is not None and self.composition is not None):
            raise ValueError("CALIBRATION_RESULT_STATUS_MISMATCH")
        if not generated and (
            self.calibrated_probability is not None or self.composition is not None
        ):
            raise ValueError("CALIBRATION_ABSENCE_CANNOT_CONTAIN_OUTPUT")
        if generated == (self.reason is not None):
            raise ValueError("CALIBRATION_REASON_MISMATCH")
        if self.raw_probability != self.source.compatible.output.probability:
            raise ValueError("CALIBRATION_RAW_OUTPUT_CHANGED")
        if self.request.source_reference != reference("calsource", self.source):
            raise ValueError("CALIBRATION_SOURCE_REFERENCE_MISMATCH")
        expected_check = {
            ForecastStatus.GENERATED: "PRESENT_VERIFIED",
            ForecastStatus.FAILED: "PRESENT_VERIFIED",
            ForecastStatus.UNAVAILABLE: "UNAVAILABLE",
            ForecastStatus.UNSUPPORTED: "NOT_CHECKED",
        }
        if self.artifact_checked != expected_check.get(self.status):
            raise ValueError("CALIBRATION_ARTIFACT_OBSERVATION_MISMATCH")
        expected_lineage: tuple[ArtifactReference, ...] = (
            reference("calrequest", self.request),
            self.request.source_reference,
            self.request.artifact_reference,
        )
        if self.composition is not None:
            composition = self.composition
            if (
                composition.primitive != self.source.primitive_composition
                or composition.primitive_identity != self.request.source_forecaster
                or composition.component != self.request.component
                or composition.calibration_artifact != self.request.artifact_reference
                or composition.target != self.request.target
                or composition.policy != self.request.policy
            ):
                raise ValueError("CALIBRATION_RESULT_COMPOSITION_MISMATCH")
            expected_lineage = (*expected_lineage, reference("calcomposition", composition))
        if self.lineage != expected_lineage:
            raise ValueError("CALIBRATION_RESULT_LINEAGE_MISMATCH")
        return self
