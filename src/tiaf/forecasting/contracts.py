"""FF-0.1 contract shapes and pure validation; no forecaster or runtime."""

from typing import Annotated, Any, Literal, Self

from pydantic import (
    Field,
    SerializerFunctionWrapHandler,
    StrictFloat,
    field_validator,
    model_serializer,
    model_validator,
)

from tiaf.evaluation.forecast_contracts import (
    EvidenceReference,
    ForecastTargetSpec,
    ForecastWindow,
)
from tiaf.planner.models import Sha256

from .enums import ForecastRealizationMode, ForecastReason, ForecastStatus, KnowledgeBasis
from .evidence import validate_knowledge, validate_required_evidence, window_evidence
from .execution import ForecastExecution
from .identity import ArtifactReference, ForecastContract, ForecastDateTime, LogicalId
from .identity import semantic_fingerprint as fingerprint


class ForecastRequest(ForecastContract):
    """Decision-time request; future production/issue clocks belong only to results."""

    schema_id: Literal["tiaf.ff.request"] = "tiaf.ff.request"
    request_id: LogicalId
    target: ForecastTargetSpec
    window: ForecastWindow
    realization_mode: ForecastRealizationMode
    information_cutoff: ForecastDateTime
    as_of: ForecastDateTime
    knowledge_basis: KnowledgeBasis
    evidence_ref: ArtifactReference
    evidence: tuple[EvidenceReference, ...]
    profile_ref: ArtifactReference
    configuration_ref: ArtifactReference
    simulation_profile_ref: ArtifactReference | None = None
    purpose: Literal["SYNTHETIC_ENGINEERING"] = "SYNTHETIC_ENGINEERING"
    data_basis: Literal["SYNTHETIC_FIXTURE"] = "SYNTHETIC_FIXTURE"

    @field_validator("evidence")
    @classmethod
    def canonical_reference_set(
        cls, values: tuple[EvidenceReference, ...]
    ) -> tuple[EvidenceReference, ...]:
        ids = [value.artifact.artifact_id for value in values]
        if len(ids) != len(set(ids)):
            raise ValueError("evidence reference identities must be unique")
        return tuple(sorted(values, key=lambda value: value.artifact.artifact_id))

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if self.target.subject != self.window.reference.subject:
            raise ValueError("target and reference subject must agree")
        if not self.window.reference.observed_at <= self.information_cutoff <= self.as_of:
            raise ValueError("reference close <= information cutoff <= as-of is required")
        if self.as_of >= self.window.target_open_time:
            raise ValueError("decision/as-of must be strictly before target open")
        simulated = self.realization_mode is ForecastRealizationMode.SIMULATED_ISSUANCE
        if simulated != (self.simulation_profile_ref is not None):
            raise ValueError("simulation profile is required only for SIMULATED_ISSUANCE")
        by_id: dict[str, EvidenceReference] = {}
        for source in self.all_evidence:
            key = source.artifact.artifact_id
            if key in by_id and by_id[key] != source:
                raise ValueError("conflicting versions of one evidence reference")
            by_id[key] = source
        validate_knowledge(
            self.all_evidence,
            self.information_cutoff,
            self.realization_mode,
            self.knowledge_basis,
        )
        return self

    @property
    def all_evidence(self) -> tuple[EvidenceReference, ...]:
        return (*window_evidence(self.window), *self.evidence)

    @property
    def simulation_as_of(self) -> ForecastDateTime | None:
        """Read-only semantic view, not a second editable/serialized clock."""
        return (
            self.as_of
            if self.realization_mode is ForecastRealizationMode.SIMULATED_ISSUANCE
            else None
        )

    @property
    def observation_id(self) -> str:
        """Common scientific observation excludes producer, request ID and mode."""
        return "ff-observation:" + fingerprint(
            {
                "target": self.target,
                "window": self.window,
                "information_cutoff": self.information_cutoff,
                "as_of": self.as_of,
            }
        )

    @property
    def semantic_fingerprint(self) -> str:
        return fingerprint(self)


class ForecastArtifactIdentity(ForecastContract):
    """Pinned forecaster/fit lineage only; no model bytes, counts or executable loader."""

    schema_id: Literal["tiaf.ff.artifact-identity"] = "tiaf.ff.artifact-identity"
    artifact: ArtifactReference
    forecaster_id: Literal["forecaster:historical-base-rate"] = "forecaster:historical-base-rate"
    implementation_version: Literal["1.0"] = "1.0"
    configuration_ref: ArtifactReference
    code_ref: ArtifactReference
    fit_knowledge_cutoff: ForecastDateTime
    prepared_at: ForecastDateTime
    fit_evidence: tuple[EvidenceReference, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def fit_clocks(self) -> Self:
        if self.fit_knowledge_cutoff > self.prepared_at:
            raise ValueError("artifact preparation cannot predate fit knowledge cutoff")
        if any(item.available_at > self.fit_knowledge_cutoff for item in self.fit_evidence):
            raise ValueError("artifact fit evidence violates its knowledge cutoff")
        if any(item.admitted_at > self.prepared_at for item in self.fit_evidence):
            raise ValueError("artifact preparation cannot predate admitted inputs")
        return self


class ForecastNode(ForecastContract):
    node_id: LogicalId
    artifact_ref: ArtifactReference
    realization_mode: ForecastRealizationMode
    input_kind: Literal["CAPTURED_EVIDENCE"] = "CAPTURED_EVIDENCE"
    output_kind: Literal["BINARY_PROBABILITY"] = "BINARY_PROBABILITY"
    family: Literal["PRIMITIVE"] = "PRIMITIVE"


class ForecastEdge(ForecastContract):
    """Typed declaration only; no edges are admitted by the singleton FF-0 profile."""

    source_node_id: LogicalId
    target_node_id: LogicalId
    output_kind: Literal["BINARY_PROBABILITY"] = "BINARY_PROBABILITY"


class ForecastRoot(ForecastContract):
    root_id: LogicalId
    node_id: LogicalId
    role: Literal["BENCHMARK"] = "BENCHMARK"


class ForecastComposition(ForecastContract):
    """Smallest finite typed graph; not a registry or general DAG executor."""

    schema_id: Literal["tiaf.ff.composition"] = "tiaf.ff.composition"
    composition_id: LogicalId
    nodes: tuple[ForecastNode, ...] = Field(min_length=1, max_length=1)
    edges: tuple[ForecastEdge, ...] = Field(default=(), max_length=0)
    roots: tuple[ForecastRoot, ...] = Field(min_length=1, max_length=1)
    policy_ref: ArtifactReference

    @model_validator(mode="after")
    def singleton(self) -> Self:
        if self.roots[0].node_id != self.nodes[0].node_id:
            raise ValueError("root must reference the declared node")
        return self


class BinaryProbabilityOutput(ForecastContract):
    kind: Literal["BINARY_PROBABILITY"] = "BINARY_PROBABILITY"
    probability: Annotated[StrictFloat, Field(ge=0, le=1, allow_inf_nan=False)]
    calibration: Literal["RAW"] = "RAW"
    uncertainty: Literal["NOT_ESTIMATED"] = "NOT_ESTIMATED"
    uncertainty_reason: Literal["NO_QUALIFIED_UNCERTAINTY_METHOD"] = (
        "NO_QUALIFIED_UNCERTAINTY_METHOD"
    )
    validity: Literal["UNKNOWN"] = "UNKNOWN"
    validity_reason: Literal["RAW_RESEARCH_NOT_ADVISORY"] = "RAW_RESEARCH_NOT_ADVISORY"


class ForecastAbsence(ForecastContract):
    kind: Literal["ABSENCE"] = "ABSENCE"
    expected_kind: Literal["BINARY_PROBABILITY"] = "BINARY_PROBABILITY"
    reasons: tuple[ForecastReason, ...] = Field(min_length=1)
    calibration: Literal["NOT_APPLICABLE"] = "NOT_APPLICABLE"
    uncertainty: Literal["NOT_APPLICABLE"] = "NOT_APPLICABLE"
    validity: Literal["NOT_APPLICABLE"] = "NOT_APPLICABLE"


class ForecastResult(ForecastContract):
    """Reconstructable result shape; clocks are supplied, never read or repaired here."""

    schema_id: Literal["tiaf.ff.result"] = "tiaf.ff.result"
    result_id: LogicalId
    run_id: LogicalId
    request: ForecastRequest
    composition: ForecastComposition
    artifact_identity: ForecastArtifactIdentity | None
    binding_ref: ArtifactReference | None
    binding_available_at: ForecastDateTime | None
    status: ForecastStatus
    output: Annotated[BinaryProbabilityOutput | ForecastAbsence, Field(discriminator="kind")]
    computed_at: ForecastDateTime | None
    issued_at: ForecastDateTime | None = None
    limitations: tuple[LogicalId, ...] = ()
    contradictions: tuple[ArtifactReference, ...] = ()
    authority: Literal["NO_ACTION_AUTHORITY"] = "NO_ACTION_AUTHORITY"
    admission: Literal["RESEARCH_ONLY"] = "RESEARCH_ONLY"
    usage_state: Literal["NOT_RECORDED_CONTRACT_ONLY", "RECORDED"] = "NOT_RECORDED_CONTRACT_ONLY"
    inference: ForecastExecution | None = None
    replay_fingerprint: Sha256 | None = None

    @model_serializer(mode="wrap")
    def preserve_legacy_projection(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        data: dict[str, Any] = handler(self)
        if self.inference is None:
            data.pop("inference", None)
        return data

    @model_validator(mode="after")
    def result_invariants(self) -> Self:
        if (self.usage_state == "RECORDED") != (self.inference is not None):
            raise ValueError("EXECUTION_USAGE_STATE_MISMATCH")
        if self.inference is not None:
            if self.inference.configuration_ref != self.request.configuration_ref:
                raise ValueError("EXECUTION_CONFIGURATION_MISMATCH")
            if self.inference.composition_ref != self.request.profile_ref:
                raise ValueError("EXECUTION_COMPOSITION_MISMATCH")
            if self.inference.usage.completed_at != self.computed_at:
                raise ValueError("EXECUTION_COMPLETION_MISMATCH")
            if self.status is ForecastStatus.GENERATED and (
                self.inference.usage.attempts != 1 or self.inference.support is None
            ):
                raise ValueError("GENERATED_REQUIRES_INVOKED_SUPPORT")
        request = self.request
        generated = self.status is ForecastStatus.GENERATED
        if generated != isinstance(self.output, BinaryProbabilityOutput):
            raise ValueError("GENERATED requires probability; every other status requires absence")
        if isinstance(self.output, ForecastAbsence):
            allowed = {
                ForecastStatus.UNSUPPORTED: {
                    ForecastReason.SCOPE_UNSUPPORTED,
                    ForecastReason.TARGET_SESSION_UNRESOLVED,
                },
                ForecastStatus.ABSTAINED: {ForecastReason.POLICY_ABSTENTION},
                ForecastStatus.FAILED: {
                    ForecastReason.INTERNAL_EXECUTION_FAILURE,
                    ForecastReason.LOCAL_DEADLINE_EXCEEDED,
                },
                ForecastStatus.UNAVAILABLE: set(ForecastReason)
                - {
                    ForecastReason.SCOPE_UNSUPPORTED,
                    ForecastReason.TARGET_SESSION_UNRESOLVED,
                    ForecastReason.POLICY_ABSTENTION,
                    ForecastReason.INTERNAL_EXECUTION_FAILURE,
                    ForecastReason.LOCAL_DEADLINE_EXCEEDED,
                },
            }
            if not set(self.output.reasons) <= allowed[self.status]:
                raise ValueError("absence reason does not match generation status")
        node = self.composition.nodes[0]
        if node.realization_mode is not request.realization_mode:
            raise ValueError("composition and result must preserve request mode")
        if (
            self.artifact_identity is not None
            and node.artifact_ref != self.artifact_identity.artifact
        ):
            raise ValueError("result artifact must match the pinned node artifact")
        if (self.binding_ref is None) != (self.binding_available_at is None):
            raise ValueError("binding identity and availability are required together")
        if self.computed_at is not None and self.computed_at < request.as_of:
            raise ValueError("completion cannot predate decision/as-of")
        if request.realization_mode is ForecastRealizationMode.SIMULATED_ISSUANCE:
            if self.issued_at is not None:
                raise ValueError("SIMULATED_ISSUANCE must not claim issued_at")
        elif generated:
            if self.computed_at is None or self.issued_at is None:
                raise ValueError("generated ACTUAL requires completion and issuance")
            if not self.computed_at <= self.issued_at < request.window.target_open_time:
                raise ValueError("ACTUAL requires completion <= issue < target open; no backdating")
        if not generated and self.issued_at is not None:
            raise ValueError("an absent forecast has no actual issuance")
        if generated:
            self._validate_generated()
        expected = fingerprint(self.model_dump(mode="python", exclude={"replay_fingerprint"}))
        if self.replay_fingerprint is not None and self.replay_fingerprint != expected:
            raise ValueError("result replay fingerprint does not match its semantic content")
        object.__setattr__(self, "replay_fingerprint", expected)
        return self

    def _validate_generated(self) -> None:
        request, artifact = self.request, self.artifact_identity
        if self.computed_at is None or artifact is None or self.binding_ref is None:
            raise ValueError("generated result requires completion, exact artifact and binding")
        validate_required_evidence(request.window)
        if not artifact.fit_knowledge_cutoff <= request.information_cutoff:
            raise ValueError("artifact fit knowledge exceeds forecast cutoff")
        if artifact.prepared_at > self.computed_at:
            raise ValueError("producing artifact cannot be prepared after computation")
        validate_knowledge(
            artifact.fit_evidence,
            artifact.fit_knowledge_cutoff,
            request.realization_mode,
            request.knowledge_basis,
        )
        if any(item.admitted_at > self.computed_at for item in request.all_evidence):
            raise ValueError("computation cannot predate acquisition/admission of its inputs")
        bound = self.issued_at if self.issued_at is not None else self.computed_at
        if self.binding_available_at is None or self.binding_available_at > bound:
            raise ValueError("binding cannot become available after its recorded use")

    @property
    def observation_id(self) -> str:
        return self.request.observation_id
