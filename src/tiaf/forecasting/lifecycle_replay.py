"""FLC-7 integration codecs and bounded offline replay in the existing store.

No dynamic import, callbacks, registry, fitting, external acquisition or lifecycle
execution. Recorded verification checks content/lineage; reconstruction explicitly
delegates to the already accepted package implementations.
"""

from collections.abc import Iterator
from types import MappingProxyType
from typing import Literal, cast

from pydantic import BaseModel

from tiaf.evaluation.forecast_normalization import (
    NormalizedEvaluationStore,
    replay_normalized_evaluation,
)
from tiaf.evaluation.forecast_normalization_contracts import (
    EvaluationInput,
    GroundTruthSet,
    LegacyFF1EvaluationView,
    NormalizedEvaluationLedger,
    NormalizedEvaluationResult,
)
from tiaf.learning.calibration import CalibrationStore, replay_calibration
from tiaf.learning.calibration_contracts import CalibrationApplyResult
from tiaf.learning.forecast_artifacts import SealedResearch
from tiaf.learning.forecaster_custody import CustodyClass, restore_predictor, restore_training
from tiaf.learning.forecaster_diagnostics import (
    DiagnosticEnvelope,
    DiagnosticRequest,
    DiagnosticStore,
    replay_diagnostic,
)
from tiaf.learning.forecaster_lifecycle import ApprovalDecision
from tiaf.learning.forecaster_training import TrainingBundle, TrainingIdentity
from tiaf.learning.optimization import OptimizationStore, replay_optimization
from tiaf.learning.optimization_contracts import OptimizationClaim, OptimizationResult

from .contracts import BinaryProbabilityOutput
from .forecaster_adapters import resolve_inference_forecaster
from .forecaster_seams import ForecasterKey
from .identity import ArtifactReference, ForecastDateTime
from .lifecycle_provenance import (
    ArtifactPrediction,
    InferenceCapture,
    InferenceContext,
    LineageBranch,
    ProvenanceEdge,
    ProvenanceNode,
    ProvenanceRecord,
    Relation,
    ReplayRequest,
    ReplayResult,
    Stage,
    ref_key,
)

_NEW: dict[str, type[SealedResearch]] = {
    "provenance": ProvenanceRecord,
    "infercapture": InferenceCapture,
    "infercontext": InferenceContext,
    "predictionprobe": ArtifactPrediction,
    "replayrequest": ReplayRequest,
    "replayresult": ReplayResult,
    "externaltruth": GroundTruthSet,
}
LiteralStatus = Literal["MATCH", "MISMATCH", "UNAVAILABLE", "UNSUPPORTED"]
_CODECS: dict[str, type[SealedResearch]] = {
    **OptimizationStore.record_types,
    **DiagnosticStore.record_types,
    **CalibrationStore.record_types,
    **NormalizedEvaluationStore.record_types,
    **_NEW,
}
_KINDS = {model: kind for kind, model in _CODECS.items()}


def reference(value: SealedResearch) -> ArtifactReference:
    kind = _KINDS.get(type(value))
    if kind is None:
        raise ValueError("PROVENANCE_UNSUPPORTED_RECORD")
    prefix = "flc7" if kind in _NEW else "flc6" if kind.startswith("eval") else "flc"
    return ArtifactReference(
        artifact_id=f"{prefix}:{kind}",
        artifact_version=value.schema_version,
        fingerprint=cast(str, value.fingerprint),
    )


class LifecycleStore(
    CalibrationStore, DiagnosticStore, OptimizationStore, NormalizedEvaluationStore
):
    """Union of existing codecs, using exactly ResearchForecastStore get/put."""

    record_types = MappingProxyType(_CODECS)

    def resolve(self, ref: ArtifactReference) -> SealedResearch:
        ref = ArtifactReference.model_validate(ref.model_dump())
        prefix, _, kind = ref.artifact_id.partition(":")
        expected = "flc7" if kind in _NEW else "flc6" if kind.startswith("eval") else "flc"
        if prefix != expected or kind not in self.record_types:
            raise ValueError("UNKNOWN_LIFECYCLE_REFERENCE")
        value = self.get(kind, ref.fingerprint)
        if reference(value) != ref:
            raise ValueError("LIFECYCLE_REFERENCE_MISMATCH")
        return value


class _ReplayStore(LifecycleStore):
    """Per-request accounting catches even failures swallowed by legacy adapters."""

    reads = 0
    unavailable = False
    invalid = False
    limit: int = 512

    def get(self, kind: str, fingerprint: str) -> SealedResearch:
        if self.reads >= self.limit:
            self.invalid = True
            raise ValueError("REPLAY_READ_LIMIT")
        self.reads += 1
        try:
            path = self._path(kind, fingerprint)
            if not path.exists():
                self.unavailable = True
                raise FileNotFoundError("REPLAY_REQUIRED_BYTES_UNAVAILABLE")
            return super().get(kind, fingerprint)
        except (PermissionError, FileNotFoundError):
            self.unavailable = True
            raise
        except (ValueError, OSError):
            self.invalid = True
            raise


def _children(value: object, depth: int = 0) -> Iterator[SealedResearch | ArtifactReference]:
    if depth > 32:
        raise ValueError("PROVENANCE_RECORD_DEPTH_LIMIT")
    if isinstance(value, ArtifactReference):
        yield value
    elif isinstance(value, SealedResearch) and type(value) in _KINDS:
        yield value
    elif isinstance(value, BaseModel):
        for name in type(value).model_fields:
            yield from _children(getattr(value, name), depth + 1)
    elif isinstance(value, tuple):
        for child in value:
            yield from _children(child, depth + 1)


def dependencies(value: SealedResearch) -> tuple[tuple[ArtifactReference, Relation], ...]:
    """Derive links from typed records, never trust caller-copied edge lists."""
    refs: set[ArtifactReference] = set()
    for name in type(value).model_fields:
        for child in _children(getattr(value, name)):
            refs.add(child if isinstance(child, ArtifactReference) else reference(child))
    refs.discard(reference(value))
    if isinstance(value, OptimizationResult):
        refs.add(
            reference(
                OptimizationClaim(
                    request_reference=value.request_reference, grant_reference=value.grant_reference
                )
            )
        )
    if isinstance(value, TrainingIdentity):
        for field in (
            "qualification_fingerprint",
            "dataset_fingerprint",
            "population_fingerprint",
            "feature_schema_fingerprint",
            "configuration_fingerprint",
            "dependency_lock_fingerprint",
            "implementation_fingerprint",
        ):
            refs.add(
                ArtifactReference(
                    artifact_id=f"training-pin:{field}",
                    artifact_version="1.0",
                    fingerprint=getattr(value, field),
                )
            )
    if isinstance(value, LegacyFF1EvaluationView):
        for field in (
            "protocol_fingerprint",
            "execution_fingerprint",
            "evaluation_fingerprint",
            "ledger_fingerprint",
            "paired_population_fingerprint",
            "ground_truth_fingerprint",
            "metric_policy_fingerprint",
        ):
            refs.add(
                ArtifactReference(
                    artifact_id=f"ff1-record:{field}",
                    artifact_version="1.0",
                    fingerprint=getattr(value, field),
                )
            )
    output = []
    for ref in refs:
        relation = Relation.USES
        if isinstance(value, TrainingIdentity) and ref == value.split_reference:
            relation = Relation.TRAINED_FROM
        elif isinstance(value, (InferenceCapture, ArtifactPrediction)):
            relation = Relation.DERIVED_FROM
        elif isinstance(value, DiagnosticEnvelope) and ref == value.artifact_reference:
            relation = Relation.DIAGNOSES
        elif isinstance(value, CalibrationApplyResult) and ref == value.request.source_reference:
            relation = Relation.CALIBRATED_FROM
        elif isinstance(value, EvaluationInput) and ref == reference(value.ground_truth):
            relation = Relation.EVALUATED_AGAINST
        elif isinstance(value, OptimizationResult) and ref in value.trial_references:
            relation = Relation.SELECTED_FROM
        elif isinstance(value, ApprovalDecision) and ref in value.evidence_references:
            relation = Relation.APPROVAL_REFERENCES
        output.append((ref, relation))
    return tuple(sorted(output, key=lambda pair: (ref_key(pair[0]), pair[1])))


def capture_record(store: LifecycleStore, value: SealedResearch) -> ArtifactReference:
    """Persist known embedded children first. No lookup/refetch of private sources."""
    value = type(value).model_validate(value.model_dump())
    pending = [value]
    ordered: dict[ArtifactReference, SealedResearch] = {}
    while pending:
        item = pending.pop()
        ref = reference(item)
        if ref in ordered:
            continue
        if len(ordered) >= 256:
            raise ValueError("PROVENANCE_NODE_LIMIT")
        ordered[ref] = item
        for name in type(item).model_fields:
            pending.extend(
                c for c in _children(getattr(item, name)) if isinstance(c, SealedResearch)
            )
    for item in reversed(tuple(ordered.values())):
        store.put(_KINDS[type(item)], item)
    return reference(value)


def capture_provenance(
    store: LifecycleStore,
    *,
    provenance_id: str,
    root: ForecasterKey,
    branches: tuple[LineageBranch, ...],
    created_at: ForecastDateTime,
    consumed: bool = False,
) -> ProvenanceRecord:
    """Close over captured children; external identities are explicitly unarchived."""
    nodes: dict[ArtifactReference, ProvenanceNode] = {}
    edges: list[ProvenanceEdge] = []
    pending = [r for branch in branches for r in branch.references]
    while pending:
        ref = pending.pop()
        if ref in nodes:
            continue
        if len(nodes) >= 256:
            raise ValueError("PROVENANCE_NODE_LIMIT")
        prefix, _, kind = ref.artifact_id.partition(":")
        captured = prefix in {"flc", "flc6", "flc7"} and kind in _CODECS
        nodes[ref] = ProvenanceNode(
            reference=ref,
            custody=CustodyClass.LOCAL_RESEARCH_ARTIFACT
            if captured
            else CustodyClass.TRACKED_REPOSITORY_METADATA,
            closure="REQUIRED_BYTES" if captured else "IDENTITY_ONLY",
        )
        if captured:
            value = store.resolve(ref)
            if isinstance(value, (ProvenanceRecord, ReplayRequest, ReplayResult)):
                raise ValueError("NESTED_PROVENANCE_REPLAY_NOT_ALLOWED")
            for dep, relation in dependencies(value):
                edges.append(ProvenanceEdge(source=ref, target=dep, relation=relation))
                pending.append(dep)
    graph = ProvenanceRecord(
        provenance_id=provenance_id,
        root=root,
        branches=branches,
        nodes=tuple(nodes.values()),
        edges=tuple(edges),
        created_at=created_at,
        evidence_state="HISTORICAL_ACCEPTED_CONSUMED" if consumed else "SYNTHETIC_ENGINEERING",
    )
    _validate_graph(
        graph, {r: store.resolve(r) for r, n in nodes.items() if n.closure == "REQUIRED_BYTES"}
    )
    store.put("provenance", graph)
    return graph


def _validate_graph(
    graph: ProvenanceRecord, records: dict[ArtifactReference, SealedResearch]
) -> None:
    expected = {
        ProvenanceEdge(source=ref, target=dep, relation=relation)
        for ref, value in records.items()
        for dep, relation in dependencies(value)
    }
    if expected != set(graph.edges):
        raise ValueError("PROVENANCE_NATIVE_EDGE_MISMATCH")
    for node in graph.nodes:
        if (
            node.reference.artifact_id.partition(":")[0] in {"flc", "flc6", "flc7"}
            and node.reference.artifact_id.partition(":")[2] in _CODECS
            and node.closure != "REQUIRED_BYTES"
        ):
            raise ValueError("CAPTURED_ARTIFACT_CANNOT_BECOME_IDENTITY_ONLY")
    for branch in graph.branches:
        if branch.stage == Stage.TRAINING:
            for ref in branch.references:
                record = records.get(ref)
                if (
                    not isinstance(record, TrainingBundle)
                    or record.request.experiment.forecaster != graph.root
                ):
                    raise ValueError("PROVENANCE_TRAINING_ROOT_MISMATCH")
        if branch.stage == Stage.INFERENCE:
            for ref in branch.references:
                record = records.get(ref)
                key = (
                    record.result.request.key
                    if isinstance(record, InferenceCapture)
                    else record.forecaster
                    if isinstance(record, ArtifactPrediction)
                    else None
                )
                if key != graph.root:
                    raise ValueError("PROVENANCE_INFERENCE_ROOT_MISMATCH")
        if branch.stage == Stage.OPTIMIZATION:
            for ref in branch.references:
                record = records.get(ref)
                if not isinstance(record, OptimizationResult) or (
                    record.selected_model_identity is not None
                    and record.selected_model_identity.forecaster != graph.root
                ):
                    raise ValueError("PROVENANCE_OPTIMIZATION_ROOT_MISMATCH")
    for value in records.values():
        if isinstance(value, InferenceCapture):
            context = records.get(value.context)
            if (
                not isinstance(context, InferenceContext)
                or context.native.reference != value.result.request.context_ref
                or value.result.request.computed_at > graph.created_at
            ):
                raise ValueError("PROVENANCE_INFERENCE_CONTEXT_MISMATCH")
        elif isinstance(value, ArtifactPrediction):
            bundle = records.get(value.bundle)
            if (
                not isinstance(bundle, TrainingBundle)
                or bundle.result.model_identity is None
                or bundle.result.preprocessor_identity is None
            ):
                raise ValueError("PROVENANCE_PREDICTION_TRAINING_MISSING")
            if (
                value.forecaster != bundle.request.experiment.forecaster
                or bundle.request.purpose != "SYNTHETIC_ENGINEERING"
                or value.model != bundle.result.model_identity.artifact
                or value.scaler != bundle.result.preprocessor_identity.artifact
                or value.computed_at < bundle.execution.completed_at
            ):
                raise ValueError("PROVENANCE_PREDICTION_LINEAGE_MISMATCH")
        elif isinstance(value, EvaluationInput):
            for forecast_set in value.forecast_sets:
                for row in forecast_set.observations:
                    source = records.get(row.forecast_ref) if row.forecast_ref else None
                    probability = None
                    if isinstance(source, ArtifactPrediction):
                        probability = source.output.probability
                    elif isinstance(source, InferenceCapture) and isinstance(
                        source.result.output, BinaryProbabilityOutput
                    ):
                        probability = source.result.output.probability
                    elif isinstance(source, CalibrationApplyResult):
                        probability = source.calibrated_probability
                    if source is not None and (
                        probability is None or probability != row.probability
                    ):
                        raise ValueError("PROVENANCE_EVALUATION_FORECAST_MISMATCH")
                    if isinstance(source, ArtifactPrediction):
                        participant = forecast_set.participant
                        if (
                            participant.forecaster != source.forecaster
                            or participant.forecast_or_composition != source.model
                        ):
                            raise ValueError("PROVENANCE_EVALUATION_PARTICIPANT_MISMATCH")
                    source_at = getattr(source, "computed_at", None)
                    if source_at is not None and source_at > value.captured_at:
                        raise ValueError("PROVENANCE_EVALUATION_BEFORE_FORECAST")
        elif isinstance(value, DiagnosticEnvelope):
            diagnostic_request = records.get(value.request_reference)
            if not isinstance(diagnostic_request, DiagnosticRequest):
                raise ValueError("PROVENANCE_DIAGNOSTIC_REQUEST_MISSING")
            for field in (
                "forecaster",
                "artifact_reference",
                "model_identity_reference",
                "subject",
                "target_id",
                "kind",
                "created_at",
            ):
                if getattr(value, field) != getattr(diagnostic_request, field):
                    raise ValueError("PROVENANCE_DIAGNOSTIC_LINEAGE_MISMATCH")
        elif isinstance(value, NormalizedEvaluationLedger):
            result = records.get(value.result)
            supplied = records.get(value.evaluation_input)
            if not isinstance(result, NormalizedEvaluationResult) or not isinstance(
                supplied, EvaluationInput
            ):
                raise ValueError("PROVENANCE_EVALUATION_CLOSURE_MISSING")
            if (
                result.request != supplied.request
                or result.input_reference != value.evaluation_input
                or reference(supplied.request) != value.request
                or reference(supplied.request.population) != value.population
                or reference(result.metrics) != value.metrics
                or reference(result.statistics) != value.statistics
                or (reference(result.paired_table) if result.paired_table else None)
                != value.paired_table
                or value.completed_at != result.created_at
            ):
                raise ValueError("PROVENANCE_EVALUATION_LEDGER_MISMATCH")
        if (
            isinstance(value, LegacyFF1EvaluationView)
            and graph.evidence_state != "HISTORICAL_ACCEPTED_CONSUMED"
        ):
            raise ValueError("CONSUMED_EVIDENCE_CANNOT_BE_RELABELLED")
        for field in ("created_at", "computed_at", "completed_at", "recorded_at"):
            at = getattr(value, field, None)
            if at is not None and at > graph.created_at:
                raise ValueError("PROVENANCE_BACKDATED_BEFORE_COMPONENT")


_TARGETS: dict[str, tuple[type[SealedResearch], ...]] = {
    "INFERENCE": (InferenceCapture, ArtifactPrediction),
    "TRAINING_ARTIFACTS": (TrainingBundle,),
    "DIAGNOSTICS": (DiagnosticEnvelope,),
    "CALIBRATION": (CalibrationApplyResult,),
    "EVALUATION": (NormalizedEvaluationLedger, LegacyFF1EvaluationView),
    "OPTIMIZATION": (OptimizationResult,),
    "PROVENANCE": (ProvenanceRecord,),
}


def _reconstruct(store: LifecycleStore, value: SealedResearch, target: ArtifactReference) -> str:
    if isinstance(value, TrainingBundle):
        return "MATCH" if restore_training(store, target) == value else "MISMATCH"
    if isinstance(value, ArtifactPrediction):
        output = restore_predictor(store, value.bundle).predict(value.features)
        return "MATCH" if output == value.output else "MISMATCH"
    if isinstance(value, InferenceCapture):
        context = store.resolve(value.context)
        assert isinstance(context, InferenceContext)
        actual = resolve_inference_forecaster(value.result.request.key, context.native).forecast(
            value.result.request
        )
        return "MATCH" if actual == value.result else "MISMATCH"
    if isinstance(value, DiagnosticEnvelope):
        return replay_diagnostic(store, target)
    if isinstance(value, CalibrationApplyResult):
        return replay_calibration(store, target)
    if isinstance(value, NormalizedEvaluationLedger):
        return replay_normalized_evaluation(store, target)
    if isinstance(value, OptimizationResult):
        return replay_optimization(store, target)
    return "MATCH" if isinstance(value, ProvenanceRecord) else "UNSUPPORTED"


def replay_lifecycle(store: LifecycleStore, request: ReplayRequest) -> ReplayResult:
    """One read-only seam; missing bytes never become an integrity success."""
    request = ReplayRequest.model_validate(request.model_dump())
    try:
        reader = _ReplayStore(store.root)
    except (OSError, ValueError):
        missing = not store.root.exists()
        return ReplayResult(
            request=request,
            status="UNAVAILABLE" if missing else "MISMATCH",
            reason="replay:corpus-unavailable" if missing else "replay:unsafe-corpus",
            artifact_reads=0,
            checked_at=request.checked_at,
        )
    reader.limit = request.max_artifact_reads
    identity_only: tuple[ArtifactReference, ...] = ()
    historical_as_of = None
    mode = None
    status = "MISMATCH"
    reason = "replay:integrity-or-lineage-mismatch"
    try:
        graph = reader.resolve(request.provenance)
        if not isinstance(graph, ProvenanceRecord) or request.checked_at < graph.created_at:
            raise ValueError("INVALID_PROVENANCE_OR_REPLAY_CLOCK")
        identity_only = tuple(n.reference for n in graph.nodes if n.closure == "IDENTITY_ONLY")
        records = {
            n.reference: reader.resolve(n.reference)
            for n in graph.nodes
            if n.closure == "REQUIRED_BYTES"
        }
        _validate_graph(graph, records)
        target = graph if request.target == request.provenance else records.get(request.target)
        if target is None:
            if request.target in identity_only:
                reader.unavailable = True
                raise FileNotFoundError("REFERENCE_ONLY_TARGET_UNAVAILABLE")
            raise ValueError("REPLAY_TARGET_OUTSIDE_GRAPH")
        if type(target) not in _TARGETS[request.target_kind]:
            raise ValueError("REPLAY_TARGET_KIND_MISMATCH")
        if isinstance(target, InferenceCapture):
            historical_as_of, mode = target.result.request.as_of, target.result.request.mode
        if request.mode == "RECORDED_VERIFY":
            status = "MATCH"
        elif graph.evidence_state == "HISTORICAL_ACCEPTED_CONSUMED":
            status = "UNSUPPORTED"
            reason = "replay:consumed-evidence-recorded-verification-only"
        else:
            status = _reconstruct(reader, target, request.target)
        if status == "MATCH":
            reason = (
                "replay:recorded-closure-verified"
                if request.mode == "RECORDED_VERIFY"
                else "replay:artifact-reconstruction-verified"
            )
    except (OSError, ValueError, LookupError, AssertionError):
        status = "MISMATCH"
    if reader.invalid:
        status, reason = "MISMATCH", "replay:invalid-record-or-read-limit"
    elif reader.unavailable:
        status, reason = "UNAVAILABLE", "replay:required-bytes-unavailable"
    return ReplayResult(
        request=request,
        status=cast("LiteralStatus", status),
        reason=reason,
        artifact_reads=reader.reads,
        identity_only=identity_only,
        checked_at=request.checked_at,
        historical_as_of=historical_as_of,
        realization_mode=mode,
    )
