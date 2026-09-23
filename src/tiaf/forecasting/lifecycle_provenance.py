"""FLC-7 bounded, authority-neutral lineage contracts; no graph executor."""

from enum import StrEnum
from typing import Literal, Self

from pydantic import Field, model_validator

from tiaf.learning.forecast_artifacts import Five, SealedResearch
from tiaf.learning.forecaster_custody import CustodyClass
from tiaf.planner.models import Sha256

from .contracts import BinaryProbabilityOutput
from .enums import ForecastRealizationMode
from .forecaster_adapters import BaseRateContext, LogisticContext
from .forecaster_seams import ForecasterKey, InferenceResult
from .identity import ArtifactReference, ForecastDateTime, LogicalId, semantic_fingerprint
from .inference_contracts import NeutralInferenceResult


class Relation(StrEnum):
    DERIVED_FROM = "DERIVED_FROM"
    TRAINED_FROM = "TRAINED_FROM"
    USES = "USES"
    CALIBRATED_FROM = "CALIBRATED_FROM"
    EVALUATED_AGAINST = "EVALUATED_AGAINST"
    DIAGNOSES = "DIAGNOSES"
    SELECTED_FROM = "SELECTED_FROM"
    APPROVAL_REFERENCES = "APPROVAL_REFERENCES"


class Stage(StrEnum):
    QUALIFICATION = "QUALIFICATION"
    TRAINING = "TRAINING"
    MODEL = "MODEL"
    PREPROCESSOR = "PREPROCESSOR"
    INFERENCE = "INFERENCE"
    OPTIMIZATION = "OPTIMIZATION"
    DIAGNOSTICS = "DIAGNOSTICS"
    CALIBRATION = "CALIBRATION"
    EVALUATION = "EVALUATION"
    LIFECYCLE = "LIFECYCLE"


class LineageBranch(SealedResearch):
    stage: Stage
    references: tuple[ArtifactReference, ...] = Field(default=(), max_length=64)
    absence: Literal["NOT_APPLICABLE", "NOT_REQUESTED"] | None = None

    @model_validator(mode="after")
    def presence(self) -> Self:
        if bool(self.references) == (self.absence is not None):
            raise ValueError("LINEAGE_EXPLICIT_BRANCH_PRESENCE_REQUIRED")
        if len(set(self.references)) != len(self.references):
            raise ValueError("LINEAGE_DUPLICATE_BRANCH_REFERENCE")
        return self


class ProvenanceNode(SealedResearch):
    reference: ArtifactReference
    custody: CustodyClass
    closure: Literal["REQUIRED_BYTES", "IDENTITY_ONLY"]
    # Identity-only nodes expressly make no storage/archive/availability claim.
    use_authorized: Literal[False] = False


class ProvenanceEdge(SealedResearch):
    # Dependent -> prerequisite; never an executable instruction.
    source: ArtifactReference
    target: ArtifactReference
    relation: Relation


def ref_key(ref: ArtifactReference) -> tuple[str, str, str]:
    return ref.artifact_id, ref.artifact_version, ref.fingerprint


class ProvenanceRecord(SealedResearch):
    provenance_id: LogicalId
    policy: Literal["tiaf.flc7.lineage.1"] = "tiaf.flc7.lineage.1"
    root: ForecasterKey
    branches: tuple[LineageBranch, ...] = Field(min_length=10, max_length=10)
    nodes: tuple[ProvenanceNode, ...] = Field(min_length=1, max_length=256)
    edges: tuple[ProvenanceEdge, ...] = Field(default=(), max_length=1024)
    evidence_state: Literal["SYNTHETIC_ENGINEERING", "HISTORICAL_ACCEPTED_CONSUMED"]
    created_at: ForecastDateTime
    grants_training: Literal[False] = False
    grants_calibration_fit: Literal[False] = False
    grants_approval: Literal[False] = False
    grants_promotion: Literal[False] = False
    grants_activation: Literal[False] = False
    grants_unseen_status: Literal[False] = False
    grants_holdout_execution: Literal[False] = False

    @model_validator(mode="before")
    @classmethod
    def canonical_order(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        value = dict(value)
        for name, limit in (("nodes", 256), ("edges", 1024), ("branches", 10)):
            if name in value and len(value[name]) > limit:
                raise ValueError("PROVENANCE_COLLECTION_LIMIT")
        for name, model, key in (
            ("nodes", ProvenanceNode, lambda n: ref_key(n.reference)),
            ("edges", ProvenanceEdge, lambda e: (ref_key(e.source), ref_key(e.target), e.relation)),
            ("branches", LineageBranch, lambda b: b.stage),
        ):
            if name in value:
                value[name] = tuple(sorted((model.model_validate(v) for v in value[name]), key=key))
        return value

    @model_validator(mode="after")
    def dag(self) -> Self:
        refs = {node.reference for node in self.nodes}
        if len(refs) != len(self.nodes) or len(set(self.edges)) != len(self.edges):
            raise ValueError("PROVENANCE_DUPLICATE_NODE_OR_EDGE")
        if {b.stage for b in self.branches} != set(Stage):
            raise ValueError("PROVENANCE_EXPLICIT_STAGES_REQUIRED")
        branch_refs = {r for b in self.branches for r in b.references}
        if not branch_refs or not branch_refs <= refs:
            raise ValueError("PROVENANCE_BRANCH_NODE_MISSING")
        adjacency: dict[ArtifactReference, set[ArtifactReference]] = {r: set() for r in refs}
        for edge in self.edges:
            if edge.source not in refs or edge.target not in refs or edge.source == edge.target:
                raise ValueError("PROVENANCE_EDGE_ENDPOINT_INVALID")
            adjacency[edge.source].add(edge.target)
        # Iterative bounded topological removal, depth <=32. No recursive traversal.
        remaining = dict(adjacency)
        depth: dict[ArtifactReference, int] = {}
        while remaining:
            leaves = tuple(r for r, deps in remaining.items() if deps <= depth.keys())
            if not leaves:
                raise ValueError("PROVENANCE_CYCLE")
            for ref in leaves:
                depth[ref] = 1 + max((depth[d] for d in remaining.pop(ref)), default=0)
                if depth[ref] > 32:
                    raise ValueError("PROVENANCE_DEPTH_LIMIT")
        reachable = set(branch_refs)
        for _ in range(32):
            reachable |= {d for r in tuple(reachable) for d in adjacency[r]}
        if reachable != refs:
            raise ValueError("PROVENANCE_UNLINKED_NODE")
        return self

    @property
    def structure_fingerprint(self) -> Sha256:
        """Omit only this envelope's capture clock/id; child capture hashes remain exact."""
        return semantic_fingerprint(
            self.model_dump(exclude={"fingerprint", "created_at", "provenance_id"})
        )


class NeutralInferenceCapture(SealedResearch):
    """Additive family-neutral codec. Native bytes remain adapter-owned references.

    Recorded replay validates this envelope and declared custody, not unavailable
    native bytes or numeric reconstruction. No code is loaded from references.
    """

    result: NeutralInferenceResult

    @property
    def computed_at(self) -> ForecastDateTime:
        return self.result.request.computed_at


class InferenceCapture(SealedResearch):
    """Lossless FLC-1 envelope plus separately addressable, exact native context."""

    result: InferenceResult
    context: ArtifactReference


class InferenceContext(SealedResearch):
    """Legacy native capture codec only; new families use NeutralInferenceCapture."""

    native: BaseRateContext | LogisticContext


class ArtifactPrediction(SealedResearch):
    """Recorded FLC-2 numeric probe; no issued forecast or new predictor family."""

    bundle: ArtifactReference
    forecaster: ForecasterKey
    model: ArtifactReference
    scaler: ArtifactReference
    features: Five
    output: BinaryProbabilityOutput
    computed_at: ForecastDateTime
    scope: Literal["SYNTHETIC_ENGINEERING_NUMERIC_PROBE"] = "SYNTHETIC_ENGINEERING_NUMERIC_PROBE"


class ReplayRequest(SealedResearch):
    request_id: LogicalId
    provenance: ArtifactReference
    target: ArtifactReference
    target_kind: Literal[
        "INFERENCE",
        "TRAINING_ARTIFACTS",
        "DIAGNOSTICS",
        "CALIBRATION",
        "EVALUATION",
        "OPTIMIZATION",
        "PROVENANCE",
    ]
    mode: Literal["RECORDED_VERIFY", "RECONSTRUCT_FROM_ARTIFACTS"]
    checked_at: ForecastDateTime
    max_artifact_reads: int = Field(default=512, ge=1, le=512, strict=True)
    retraining_authorized: Literal[False] = False
    empirical_rerun_authorized: Literal[False] = False


class ReplayResult(SealedResearch):
    request: ReplayRequest
    status: Literal["MATCH", "MISMATCH", "UNAVAILABLE", "UNSUPPORTED"]
    reason: LogicalId
    artifact_reads: int = Field(ge=0, le=512)
    identity_only: tuple[ArtifactReference, ...] = ()
    checked_at: ForecastDateTime
    historical_as_of: ForecastDateTime | None = None
    realization_mode: ForecastRealizationMode | None = None
    grants_reuse: Literal[False] = False
    lifecycle_effect: Literal["NONE"] = "NONE"

    @model_validator(mode="after")
    def clocks(self) -> Self:
        if self.checked_at != self.request.checked_at:
            raise ValueError("REPLAY_CLOCK_MISMATCH")
        if self.historical_as_of is not None and self.checked_at < self.historical_as_of:
            raise ValueError("REPLAY_BEFORE_HISTORICAL_AS_OF")
        return self
