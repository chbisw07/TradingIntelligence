"""FLC-4 internal, descriptive model diagnostics over recorded artifacts.

Diagnostics explain recorded support or model mechanics. They do not evaluate,
fit, calibrate, rank, approve, promote, activate, fetch data or issue forecasts.
"""

import math
from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from tiaf.forecasting.forecaster_seams import ForecasterKey
from tiaf.forecasting.identity import (
    ArtifactReference,
    ForecastDateTime,
    LogicalId,
    semantic_fingerprint,
)
from tiaf.forecasting.support import BaseRateArtifact, HistoricalTransition
from tiaf.planner.models import Sha256

from .forecast_artifacts import (
    FEATURE_ORDER,
    FeatureOrder,
    Finite,
    Five,
    LogisticArtifact,
    Reconstruction,
    ScalerConfig,
    SealedResearch,
    reconstruct,
)
from .forecaster_custody import ForecasterStore
from .forecaster_training import ModelArtifactIdentity, reference
from .synthetic_trials import VERSION as SYNTHETIC_VERSION
from .synthetic_trials import SyntheticModel


class DiagnosticKind(StrEnum):
    BASE_RATE_SUPPORT = "BASE_RATE_SUPPORT"
    LOGISTIC_COEFFICIENTS = "LOGISTIC_COEFFICIENTS"
    LOGISTIC_LINEAR_CONTRIBUTIONS = "LOGISTIC_LINEAR_CONTRIBUTIONS"
    LOGISTIC_PREPROCESSOR = "LOGISTIC_PREPROCESSOR"


class DiagnosticStatus(StrEnum):
    GENERATED = "GENERATED"
    UNSUPPORTED = "UNSUPPORTED"
    UNAVAILABLE = "UNAVAILABLE"


_BASE_RATE_ID = "forecaster:historical-base-rate"
_LOGISTIC_ID = "forecaster:logistic-regression"
_SCHEMAS: Mapping[DiagnosticKind, tuple[str, str]] = MappingProxyType(
    {
        DiagnosticKind.BASE_RATE_SUPPORT: ("tiaf.flc4.baserate-support", "1.0"),
        DiagnosticKind.LOGISTIC_COEFFICIENTS: ("tiaf.flc4.logistic-coefficients", "1.0"),
        DiagnosticKind.LOGISTIC_LINEAR_CONTRIBUTIONS: (
            "tiaf.flc4.logistic-linear-contributions",
            "1.0",
        ),
        DiagnosticKind.LOGISTIC_PREPROCESSOR: ("tiaf.flc4.logistic-preprocessor", "1.0"),
    }
)
_LIMITATIONS: Mapping[DiagnosticKind, tuple[LogicalId, ...]] = MappingProxyType(
    {
        DiagnosticKind.BASE_RATE_SUPPORT: (
            "limitation:descriptive-pre-cutoff-support-only",
            "limitation:not-model-quality",
            "limitation:not-approval-evidence",
        ),
        DiagnosticKind.LOGISTIC_COEFFICIENTS: (
            "limitation:standardized-log-odds-association-not-causal",
            "limitation:correlated-features-complicate-interpretation",
            "limitation:not-feature-importance",
            "limitation:not-model-quality",
        ),
        DiagnosticKind.LOGISTIC_LINEAR_CONTRIBUTIONS: (
            "limitation:local-linear-decomposition-not-causal",
            "limitation:correlated-features-complicate-interpretation",
            "limitation:not-a-trading-reason",
            "limitation:not-model-quality",
        ),
        DiagnosticKind.LOGISTIC_PREPROCESSOR: (
            "limitation:training-transform-metadata-only",
            "limitation:not-data-quality-verdict",
            "limitation:not-model-quality",
        ),
    }
)


class DiagnosticFeatureInput(SealedResearch):
    """Outcome-free, already-recorded inference input; never a provider request."""

    input_id: LogicalId
    subject: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    feature_order: FeatureOrder = FEATURE_ORDER
    values: Five
    evidence_references: tuple[ArtifactReference, ...] = Field(min_length=1, max_length=16)
    evidence_scope: Literal["SYNTHETIC_REFERENCE", "RECORDED_INFERENCE_INPUT"]
    observed_at: ForecastDateTime
    outcome_fields_present: Literal[False] = False
    protected_evidence_used: Literal[False] = False
    consumed_holdout_reused: Literal[False] = False


class DiagnosticRequest(SealedResearch):
    request_version: Literal["flc4.diagnostic-request.1"] = "flc4.diagnostic-request.1"
    diagnostic_request_id: LogicalId
    forecaster: ForecasterKey
    artifact_reference: ArtifactReference
    model_identity_reference: ArtifactReference | None = None
    kind: DiagnosticKind
    subject: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    input_reference: ArtifactReference | None = None
    evidence_references: tuple[ArtifactReference, ...] = Field(min_length=1, max_length=16)
    scope: Literal["INTERNAL_RESEARCH"] = "INTERNAL_RESEARCH"
    evidence_policy: Literal["ARTIFACT_ONLY_NO_OUTCOME_QUERY"] = "ARTIFACT_ONLY_NO_OUTCOME_QUERY"
    protected_outcomes_allowed: Literal[False] = False
    consumed_holdout_reuse: Literal[False] = False
    fitting_authorized: Literal[False] = False
    calibration_authorized: Literal[False] = False
    evaluation_authorized: Literal[False] = False
    approval_authorized: Literal[False] = False
    created_at: ForecastDateTime

    @model_validator(mode="after")
    def applicability(self) -> Self:
        base = self.kind is DiagnosticKind.BASE_RATE_SUPPORT
        if base != (self.forecaster.forecaster_id == _BASE_RATE_ID):
            raise ValueError("DIAGNOSTIC_FORECASTER_KIND_MISMATCH")
        if not base and self.forecaster.forecaster_id != _LOGISTIC_ID:
            raise ValueError("INCOMPATIBLE_DIAGNOSTIC_FORECASTER")
        contribution = self.kind is DiagnosticKind.LOGISTIC_LINEAR_CONTRIBUTIONS
        if contribution != (self.input_reference is not None):
            raise ValueError("DIAGNOSTIC_INPUT_APPLICABILITY_MISMATCH")
        if base != (self.model_identity_reference is None):
            raise ValueError("DIAGNOSTIC_MODEL_IDENTITY_APPLICABILITY_MISMATCH")
        if self.artifact_reference not in self.evidence_references:
            raise ValueError("DIAGNOSTIC_ARTIFACT_EVIDENCE_MISSING")
        return self


class BaseRateSourceRecord(SealedResearch):
    """Lossless read-only adapter snapshot; it does not replace the FF-0 artifact."""

    source_schema: Literal["tiaf.flc4.baserate-source-adapter/1.0"] = (
        "tiaf.flc4.baserate-source-adapter/1.0"
    )
    artifact: BaseRateArtifact


class BaseRateTransitionDiagnostic(SealedResearch):
    position: int = Field(ge=0, lt=20)
    reference_session_id: LogicalId
    terminal_session_id: LogicalId
    included: bool
    label: Literal[0, 1] | None
    label_available_at: ForecastDateTime | None
    label_source: ArtifactReference
    exclusion_reasons: tuple[LogicalId, ...]


class BaseRateSupportDiagnostic(SealedResearch):
    payload_schema_id: Literal["tiaf.flc4.baserate-support"] = "tiaf.flc4.baserate-support"
    payload_schema_version: Literal["1.0"] = "1.0"
    source_artifact: ArtifactReference
    fit_knowledge_cutoff: ForecastDateTime
    window_length: Literal[20] = 20
    selection: Literal["LAST_SCHEDULED_TRANSITIONS_AT_FIT_CUTOFF"]
    replacement: Literal["NO_BACKFILL"]
    estimate: Literal["UNSMOOTHED_K_OVER_N"]
    scheduled_transition_ids: tuple[tuple[LogicalId, LogicalId], ...] = Field(
        min_length=20, max_length=20
    )
    transitions: tuple[BaseRateTransitionDiagnostic, ...] = Field(min_length=20, max_length=20)
    eligible_count: int = Field(ge=0, le=20)
    positive_count: int = Field(ge=0, le=20)
    zero_count: int = Field(ge=0, le=20)
    unavailable_positions: tuple[int, ...]
    base_rate: Finite | None
    applicability: Literal["PRE_CUTOFF_SUPPORT_DESCRIPTION_ONLY"] = (
        "PRE_CUTOFF_SUPPORT_DESCRIPTION_ONLY"
    )

    @model_validator(mode="after")
    def counts(self) -> Self:
        included = tuple(item for item in self.transitions if item.included)
        if (
            tuple(item.position for item in self.transitions) != tuple(range(20))
            or self.scheduled_transition_ids
            != tuple(
                (item.reference_session_id, item.terminal_session_id) for item in self.transitions
            )
            or self.eligible_count != len(included)
            or self.positive_count != sum(item.label == 1 for item in included)
            or self.zero_count != sum(item.label == 0 for item in included)
            or self.unavailable_positions
            != tuple(item.position for item in self.transitions if not item.included)
            or self.base_rate
            != (None if self.eligible_count != 20 else self.positive_count / self.eligible_count)
        ):
            raise ValueError("BASERATE_DIAGNOSTIC_COUNT_MISMATCH")
        return self


class LogisticCoefficientDiagnostic(SealedResearch):
    payload_schema_id: Literal["tiaf.flc4.logistic-coefficients"] = (
        "tiaf.flc4.logistic-coefficients"
    )
    payload_schema_version: Literal["1.0"] = "1.0"
    model_artifact: ArtifactReference
    feature_order: FeatureOrder = FEATURE_ORDER
    coefficients: Five
    intercept: Finite
    coefficient_semantics: Literal["STANDARDIZED_FEATURE_LOG_ODDS_ASSOCIATION"] = (
        "STANDARDIZED_FEATURE_LOG_ODDS_ASSOCIATION"
    )
    applicability: Literal["RECORDED_STANDARDIZED_LINEAR_MODEL"] = (
        "RECORDED_STANDARDIZED_LINEAR_MODEL"
    )
    causal_claim: Literal[False] = False


class LogisticPreprocessorDiagnostic(SealedResearch):
    payload_schema_id: Literal["tiaf.flc4.logistic-preprocessor"] = (
        "tiaf.flc4.logistic-preprocessor"
    )
    payload_schema_version: Literal["1.0"] = "1.0"
    scaler_artifact: ArtifactReference
    feature_order: FeatureOrder = FEATURE_ORDER
    sample_count: int = Field(ge=1)
    means: Five
    variances: Five
    scales: Five
    constant_columns: tuple[int, ...]
    config: ScalerConfig
    applicability: Literal["RECORDED_TRAINING_TRANSFORM_METADATA"] = (
        "RECORDED_TRAINING_TRANSFORM_METADATA"
    )


class LogisticContributionDiagnostic(SealedResearch):
    payload_schema_id: Literal["tiaf.flc4.logistic-linear-contributions"] = (
        "tiaf.flc4.logistic-linear-contributions"
    )
    payload_schema_version: Literal["1.0"] = "1.0"
    model_artifact: ArtifactReference
    input_reference: ArtifactReference
    feature_order: FeatureOrder = FEATURE_ORDER
    raw_values: Five
    standardized_values: Five
    coefficients: Five
    contributions: Five
    intercept: Finite
    logit: Finite
    raw_uncalibrated_probability: Finite = Field(ge=0, le=1)
    contribution_semantics: Literal["STANDARDIZED_X_I_TIMES_COEFFICIENT_I"] = (
        "STANDARDIZED_X_I_TIMES_COEFFICIENT_I"
    )
    applicability: Literal["RECORDED_OUTCOME_FREE_INFERENCE_INPUT"] = (
        "RECORDED_OUTCOME_FREE_INFERENCE_INPUT"
    )
    calibration_applied: Literal[False] = False
    causal_claim: Literal[False] = False
    trading_reason_claim: Literal[False] = False

    @model_validator(mode="after")
    def arithmetic(self) -> Self:
        expected = tuple(
            x * b for x, b in zip(self.standardized_values, self.coefficients, strict=True)
        )
        if self.contributions != expected or self.logit != self.intercept + math.fsum(expected):
            raise ValueError("LOGISTIC_CONTRIBUTION_ARITHMETIC_MISMATCH")
        return self


DiagnosticPayload = (
    BaseRateSupportDiagnostic
    | LogisticCoefficientDiagnostic
    | LogisticContributionDiagnostic
    | LogisticPreprocessorDiagnostic
)


class _DiagnosticArtifactUnavailable(Exception):
    """Internal classification for a missing or unreadable recorded artifact."""


class DiagnosticEnvelope(SealedResearch):
    envelope_schema_id: Literal["tiaf.flc4.diagnostic-envelope"] = "tiaf.flc4.diagnostic-envelope"
    envelope_schema_version: Literal["1.0"] = "1.0"
    diagnostic_id: LogicalId
    request_reference: ArtifactReference
    forecaster: ForecasterKey
    artifact_reference: ArtifactReference
    model_identity_reference: ArtifactReference | None
    subject: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    kind: DiagnosticKind
    status: DiagnosticStatus
    payload_reference: ArtifactReference | None = None
    payload_schema_id: str | None = None
    payload_schema_version: str | None = None
    lineage_references: tuple[ArtifactReference, ...] = Field(min_length=2, max_length=8)
    limitations: tuple[LogicalId, ...] = Field(min_length=1)
    reason: LogicalId | None = None
    created_at: ForecastDateTime
    authority: Literal["DESCRIPTIVE_ONLY"] = "DESCRIPTIVE_ONLY"
    lifecycle_effect: Literal["NONE"] = "NONE"
    approval: Literal[False] = False
    promotion: Literal[False] = False
    activation: Literal[False] = False
    evaluation_performed: Literal[False] = False
    calibration_applied: Literal[False] = False
    optimization_effect: Literal["NONE"] = "NONE"

    @model_validator(mode="after")
    def outcome(self) -> Self:
        generated = self.status is DiagnosticStatus.GENERATED
        supplied = (
            self.payload_reference is not None,
            self.payload_schema_id is not None,
            self.payload_schema_version is not None,
        )
        if generated != all(supplied) or (not generated and any(supplied)):
            raise ValueError("DIAGNOSTIC_ENVELOPE_PAYLOAD_MISMATCH")
        if generated == (self.reason is not None):
            raise ValueError("DIAGNOSTIC_ENVELOPE_REASON_MISMATCH")
        if (
            generated
            and (self.payload_schema_id, self.payload_schema_version) != _SCHEMAS[self.kind]
        ):
            raise ValueError("DIAGNOSTIC_PAYLOAD_SCHEMA_MISMATCH")
        if self.limitations != _LIMITATIONS[self.kind]:
            raise ValueError("DIAGNOSTIC_LIMITATIONS_MISMATCH")
        if len(set(self.lineage_references)) != len(self.lineage_references):
            raise ValueError("DUPLICATE_DIAGNOSTIC_LINEAGE")
        return self


class DiagnosticStore(ForecasterStore):
    """Add codecs to the existing custody engine; this is not another database."""

    record_types = MappingProxyType(
        {
            **ForecasterStore.record_types,
            "diagrequest": DiagnosticRequest,
            "diaginput": DiagnosticFeatureInput,
            "diagbaseratesource": BaseRateSourceRecord,
            "diagbaserate": BaseRateSupportDiagnostic,
            "diagcoefficients": LogisticCoefficientDiagnostic,
            "diagcontributions": LogisticContributionDiagnostic,
            "diagpreprocessor": LogisticPreprocessorDiagnostic,
            "diagnostic": DiagnosticEnvelope,
        }
    )


def _transition(position: int, row: HistoricalTransition) -> BaseRateTransitionDiagnostic:
    return BaseRateTransitionDiagnostic(
        position=position,
        reference_session_id=row.reference_session_id,
        terminal_session_id=row.terminal_session_id,
        included=row.included,
        label=cast(Literal[0, 1] | None, row.label),
        label_available_at=row.label_available_at,
        label_source=row.label_source.artifact,
        exclusion_reasons=row.exclusion_reasons,
    )


def _base_subject(artifact: BaseRateArtifact) -> str:
    subject = artifact.target.subject
    return (
        f"{subject.symbol}:{subject.exchange}:"
        f"{subject.segment.value}:{subject.instrument_type.value}"
    )


def _base_payload(source: BaseRateSourceRecord) -> BaseRateSupportDiagnostic:
    artifact = source.artifact
    transitions = tuple(_transition(i, row) for i, row in enumerate(artifact.rows))
    return BaseRateSupportDiagnostic(
        source_artifact=artifact.reference,
        fit_knowledge_cutoff=artifact.fit_knowledge_cutoff,
        selection="LAST_SCHEDULED_TRANSITIONS_AT_FIT_CUTOFF",
        replacement="NO_BACKFILL",
        estimate="UNSMOOTHED_K_OVER_N",
        scheduled_transition_ids=tuple(
            (row.reference_session_id, row.terminal_session_id) for row in artifact.rows
        ),
        transitions=transitions,
        eligible_count=artifact.eligible_count,
        positive_count=artifact.positive_count,
        zero_count=artifact.eligible_count - artifact.positive_count,
        unavailable_positions=tuple(item.position for item in transitions if not item.included),
        base_rate=(
            None
            if artifact.eligible_count != 20
            else artifact.positive_count / artifact.eligible_count
        ),
    )


def _model(
    store: DiagnosticStore, request: DiagnosticRequest
) -> tuple[ModelArtifactIdentity, Reconstruction]:
    if request.model_identity_reference is None:
        raise ValueError("DIAGNOSTIC_MODEL_IDENTITY_REQUIRED")
    try:
        identity = store.resolve(request.model_identity_reference)
    except (OSError, ValueError) as error:
        raise _DiagnosticArtifactUnavailable from error
    if not isinstance(identity, ModelArtifactIdentity):
        raise ValueError("DIAGNOSTIC_MODEL_IDENTITY_REQUIRED")
    try:
        artifact = store.resolve(identity.artifact)
    except (OSError, ValueError) as error:
        raise _DiagnosticArtifactUnavailable from error
    if isinstance(artifact, (LogisticArtifact, SyntheticModel)):
        reconstruction = artifact.reconstruction
    else:
        raise ValueError("DIAGNOSTIC_MODEL_CODEC_UNSUPPORTED")
    if (
        request.artifact_reference != identity.artifact
        or request.forecaster != identity.forecaster
        or request.subject != identity.subject
        or request.target_id != identity.target_id
    ):
        raise ValueError("DIAGNOSTIC_MODEL_LINEAGE_MISMATCH")
    return identity, reconstruction


def _coefficient_payload(
    artifact_ref: ArtifactReference, reconstruction: Reconstruction
) -> LogisticCoefficientDiagnostic:
    return LogisticCoefficientDiagnostic(
        model_artifact=artifact_ref,
        feature_order=reconstruction.scaler.feature_order,
        coefficients=reconstruction.coefficients,
        intercept=reconstruction.intercept,
    )


def _preprocessor_payload(reconstruction: Reconstruction) -> LogisticPreprocessorDiagnostic:
    scaler = reconstruction.scaler
    return LogisticPreprocessorDiagnostic(
        scaler_artifact=reference("scaler", scaler),
        feature_order=scaler.feature_order,
        sample_count=scaler.n,
        means=scaler.means,
        variances=scaler.variances,
        scales=scaler.scales,
        constant_columns=scaler.constant_columns,
        config=scaler.config,
    )


def _sigmoid(logit: float) -> float:
    if logit >= 0:
        return 1.0 / (1.0 + math.exp(-logit))
    value = math.exp(logit)
    return value / (1.0 + value)


def _contribution_payload(
    artifact_ref: ArtifactReference,
    reconstruction: Reconstruction,
    input_ref: ArtifactReference,
    value: DiagnosticFeatureInput,
) -> LogisticContributionDiagnostic:
    scaler = reconstruction.scaler
    standardized = cast(
        Five,
        tuple(
            (x - mean) / scale
            for x, mean, scale in zip(value.values, scaler.means, scaler.scales, strict=True)
        ),
    )
    contributions = cast(
        Five,
        tuple(
            x * coefficient
            for x, coefficient in zip(standardized, reconstruction.coefficients, strict=True)
        ),
    )
    logit = reconstruction.intercept + math.fsum(contributions)
    probability = _sigmoid(logit)
    if abs(probability - reconstruct(reconstruction, value.values)) > 1e-15:
        raise ValueError("DIAGNOSTIC_RECONSTRUCTION_MISMATCH")
    return LogisticContributionDiagnostic(
        model_artifact=artifact_ref,
        input_reference=input_ref,
        feature_order=value.feature_order,
        raw_values=value.values,
        standardized_values=standardized,
        coefficients=reconstruction.coefficients,
        contributions=contributions,
        intercept=reconstruction.intercept,
        logit=logit,
        raw_uncalibrated_probability=probability,
    )


def _payload_kind(payload: DiagnosticPayload) -> str:
    return {
        BaseRateSupportDiagnostic: "diagbaserate",
        LogisticCoefficientDiagnostic: "diagcoefficients",
        LogisticContributionDiagnostic: "diagcontributions",
        LogisticPreprocessorDiagnostic: "diagpreprocessor",
    }[type(payload)]


def _envelope(
    request: DiagnosticRequest,
    status: DiagnosticStatus,
    lineage: tuple[ArtifactReference, ...],
    payload: DiagnosticPayload | None = None,
    reason: LogicalId | None = None,
) -> DiagnosticEnvelope:
    schema = _SCHEMAS[request.kind]
    return DiagnosticEnvelope(
        diagnostic_id=f"flc4:diagnostic-{request.fingerprint}",
        request_reference=reference("diagrequest", request),
        forecaster=request.forecaster,
        artifact_reference=request.artifact_reference,
        model_identity_reference=request.model_identity_reference,
        subject=request.subject,
        target_id=request.target_id,
        kind=request.kind,
        status=status,
        payload_reference=(reference(_payload_kind(payload), payload) if payload else None),
        payload_schema_id=schema[0] if payload else None,
        payload_schema_version=schema[1] if payload else None,
        lineage_references=lineage,
        limitations=_LIMITATIONS[request.kind],
        reason=reason,
        created_at=request.created_at,
    )


def generate_diagnostic(
    store: DiagnosticStore,
    request: DiagnosticRequest,
    *,
    baserate_artifact: BaseRateArtifact | None = None,
    feature_input: DiagnosticFeatureInput | None = None,
) -> DiagnosticEnvelope:
    """Generate from explicit recorded inputs; no loaders, clock or outcome query."""
    if not store.writable:
        raise ValueError("DIAGNOSTIC_STORE_READ_ONLY")
    request = DiagnosticRequest.model_validate(request.model_dump())
    store.put("diagrequest", request)
    request_ref = reference("diagrequest", request)
    lineage: tuple[ArtifactReference, ...] = (request_ref, request.artifact_reference)
    payload: DiagnosticPayload | None = None
    if request.kind is DiagnosticKind.BASE_RATE_SUPPORT:
        if request.forecaster.implementation_version != "1.0":
            result = _envelope(
                request,
                DiagnosticStatus.UNSUPPORTED,
                lineage,
                reason="diagnostic:unsupported-baserate-version",
            )
            store.put("diagnostic", result)
            return result
        if baserate_artifact is None:
            result = _envelope(
                request,
                DiagnosticStatus.UNAVAILABLE,
                lineage,
                reason="diagnostic:baserate-artifact-not-supplied",
            )
            store.put("diagnostic", result)
            return result
        artifact = BaseRateArtifact.model_validate(baserate_artifact.model_dump())
        if (
            artifact.reference != request.artifact_reference
            or request.subject != _base_subject(artifact)
            or request.target_id != f"{artifact.target.target_id}/{artifact.target.target_version}"
        ):
            raise ValueError("BASERATE_DIAGNOSTIC_LINEAGE_MISMATCH")
        source = BaseRateSourceRecord(artifact=artifact)
        store.put("diagbaseratesource", source)
        source_ref = reference("diagbaseratesource", source)
        lineage = (*lineage, source_ref)
        payload = _base_payload(source)
    else:
        if request.forecaster.implementation_version not in ("1.0", SYNTHETIC_VERSION):
            result = _envelope(
                request,
                DiagnosticStatus.UNSUPPORTED,
                lineage,
                reason="diagnostic:unsupported-logistic-version",
            )
            store.put("diagnostic", result)
            return result
        try:
            _, reconstruction = _model(store, request)
        except _DiagnosticArtifactUnavailable:
            result = _envelope(
                request,
                DiagnosticStatus.UNAVAILABLE,
                lineage,
                reason="diagnostic:model-artifact-unavailable-or-incompatible",
            )
            store.put("diagnostic", result)
            return result
        assert request.model_identity_reference is not None
        lineage = (*lineage, request.model_identity_reference)
        if request.kind is DiagnosticKind.LOGISTIC_COEFFICIENTS:
            payload = _coefficient_payload(request.artifact_reference, reconstruction)
        elif request.kind is DiagnosticKind.LOGISTIC_PREPROCESSOR:
            payload = _preprocessor_payload(reconstruction)
        else:
            if feature_input is None or request.input_reference is None:
                raise ValueError("DIAGNOSTIC_FEATURE_INPUT_REQUIRED")
            feature_input = DiagnosticFeatureInput.model_validate(feature_input.model_dump())
            input_ref = reference("diaginput", feature_input)
            if (
                request.input_reference != input_ref
                or feature_input.subject != request.subject
                or feature_input.target_id != request.target_id
                or feature_input.feature_order != reconstruction.scaler.feature_order
            ):
                raise ValueError("DIAGNOSTIC_FEATURE_INPUT_MISMATCH")
            store.put("diaginput", feature_input)
            lineage = (*lineage, input_ref)
            payload = _contribution_payload(
                request.artifact_reference, reconstruction, input_ref, feature_input
            )
    store.put(_payload_kind(payload), payload)
    result = _envelope(request, DiagnosticStatus.GENERATED, lineage, payload=payload)
    store.put("diagnostic", result)
    return result


def replay_diagnostic(
    store: DiagnosticStore, envelope_reference: ArtifactReference
) -> Literal["MATCH", "MISMATCH"]:
    """Exact offline diagnostic replay; no fitting, Evaluation or external calls."""
    try:
        result = store.resolve(envelope_reference)
        if not isinstance(result, DiagnosticEnvelope):
            raise ValueError("DIAGNOSTIC_ENVELOPE_REQUIRED")
        request = store.resolve(result.request_reference)
        if not isinstance(request, DiagnosticRequest):
            raise ValueError("DIAGNOSTIC_REQUEST_REQUIRED")
        if (
            result.diagnostic_id != f"flc4:diagnostic-{request.fingerprint}"
            or result.forecaster != request.forecaster
            or result.artifact_reference != request.artifact_reference
            or result.model_identity_reference != request.model_identity_reference
            or result.subject != request.subject
            or result.target_id != request.target_id
            or result.kind != request.kind
            or result.created_at != request.created_at
        ):
            raise ValueError("DIAGNOSTIC_ENVELOPE_LINEAGE_MISMATCH")
        if result.status is not DiagnosticStatus.GENERATED:
            expected_result = _envelope(
                request, result.status, result.lineage_references, reason=result.reason
            )
            return "MATCH" if result == expected_result else "MISMATCH"
        assert result.payload_reference is not None
        recorded = store.resolve(result.payload_reference)
        expected_payload: DiagnosticPayload
        if request.kind is DiagnosticKind.BASE_RATE_SUPPORT:
            source_ref = next(
                ref
                for ref in result.lineage_references
                if ref.artifact_id == "flc:diagbaseratesource"
            )
            source = store.resolve(source_ref)
            if not isinstance(source, BaseRateSourceRecord):
                raise ValueError("BASERATE_DIAGNOSTIC_SOURCE_REQUIRED")
            expected_payload = _base_payload(source)
        else:
            _, reconstruction = _model(store, request)
            if request.kind is DiagnosticKind.LOGISTIC_COEFFICIENTS:
                expected_payload = _coefficient_payload(request.artifact_reference, reconstruction)
            elif request.kind is DiagnosticKind.LOGISTIC_PREPROCESSOR:
                expected_payload = _preprocessor_payload(reconstruction)
            else:
                assert request.input_reference is not None
                value = store.resolve(request.input_reference)
                if not isinstance(value, DiagnosticFeatureInput):
                    raise ValueError("DIAGNOSTIC_FEATURE_INPUT_REQUIRED")
                expected_payload = _contribution_payload(
                    request.artifact_reference, reconstruction, request.input_reference, value
                )
        expected_result = _envelope(
            request,
            DiagnosticStatus.GENERATED,
            result.lineage_references,
            payload=expected_payload,
        )
        if recorded != expected_payload or result != expected_result:
            raise ValueError("DIAGNOSTIC_REPLAY_MISMATCH")
        return "MATCH"
    except (OSError, StopIteration, ValueError):
        return "MISMATCH"


def payload_schema(kind: DiagnosticKind) -> tuple[str, str]:
    """Read-only schema discovery; not a mutable diagnostics registry."""
    return _SCHEMAS[kind]


def limitations(kind: DiagnosticKind) -> tuple[LogicalId, ...]:
    return _LIMITATIONS[kind]


def diagnostic_semantic_fingerprint(value: DiagnosticEnvelope) -> Sha256:
    """Stable helper for lineage displays, never a quality score."""
    return semantic_fingerprint(value)
