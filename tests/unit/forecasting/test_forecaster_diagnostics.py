"""FLC-4 internal diagnostics over synthetic/recorded artifacts only."""

import ast
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.forecasting.forecaster_seams import ForecasterCapability, ForecasterFamily, ForecasterKey
from tiaf.forecasting.identity import ArtifactReference, canonical_json, semantic_fingerprint
from tiaf.learning.forecast_artifacts import (
    LibraryVersions,
    Reconstruction,
    ScalerArtifact,
    SealedResearch,
    reconstruct,
)
from tiaf.learning.forecaster_diagnostics import (
    BaseRateSupportDiagnostic,
    DiagnosticEnvelope,
    DiagnosticFeatureInput,
    DiagnosticKind,
    DiagnosticRequest,
    DiagnosticStatus,
    DiagnosticStore,
    LogisticCoefficientDiagnostic,
    LogisticContributionDiagnostic,
    LogisticPreprocessorDiagnostic,
    generate_diagnostic,
    limitations,
    payload_schema,
    replay_diagnostic,
)
from tiaf.learning.forecaster_training import ModelArtifactIdentity, reference
from tiaf.learning.synthetic_trials import (
    KEY as SYNTHETIC_KEY,
)
from tiaf.learning.synthetic_trials import (
    VERSION as SYNTHETIC_VERSION,
)
from tiaf.learning.synthetic_trials import (
    SyntheticConfig,
    SyntheticModel,
    SyntheticSpec,
)

from ._runtime_support import fixture

AT = datetime(2026, 9, 23, 9, 15, tzinfo=TIAF_TIMEZONE)


def pin(name: str) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=f"test:{name}", artifact_version="1.0", fingerprint=semantic_fingerprint(name)
    )


def changed[T: SealedResearch](value: T, **updates: Any) -> T:
    return type(value).model_validate({**value.model_dump(), **updates, "fingerprint": None})


def subject(artifact: Any) -> str:
    value = artifact.target.subject
    return f"{value.symbol}:{value.exchange}:{value.segment.value}:{value.instrument_type.value}"


def base_request(artifact: Any, **updates: Any) -> DiagnosticRequest:
    result = DiagnosticRequest(
        diagnostic_request_id=f"flc4:base-{artifact.artifact_id.rsplit(':', 1)[-1]}",
        forecaster=ForecasterKey(
            forecaster_id="forecaster:historical-base-rate", implementation_version="1.0"
        ),
        artifact_reference=artifact.reference,
        kind=DiagnosticKind.BASE_RATE_SUPPORT,
        subject=subject(artifact),
        target_id=f"{artifact.target.target_id}/{artifact.target.target_version}",
        evidence_references=(artifact.reference,),
        created_at=AT,
    )
    return changed(result, **updates) if updates else result


@pytest.fixture
def logistic_store(tmp_path: Path) -> tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel]:
    store = DiagnosticStore(tmp_path / "diagnostics", create=True)
    spec = SyntheticSpec(
        config=SyntheticConfig(C=1.0, fit_intercept=True),
        fold=0,
        created_at=AT,
        dependency_lock_fingerprint="a" * 64,
        implementation_fingerprint="b" * 64,
    )
    scaler = ScalerArtifact(
        n=600,
        means=(1.0, 2.0, 3.0, 4.0, 5.0),
        variances=(4.0, 9.0, 16.0, 25.0, 0.0),
        scales=(2.0, 3.0, 4.0, 5.0, 1.0),
        constant_columns=(4,),
        training_fingerprint=cast(str, spec.fingerprint),
    )
    artifact = SyntheticModel(
        spec=spec,
        request_reference=pin("synthetic-training-request"),
        reconstruction=Reconstruction(
            scaler=scaler,
            coefficients=(0.1, -0.2, 0.3, -0.4, 0.5),
            intercept=0.07,
        ),
        versions=LibraryVersions(python="3.12.3", numeric_backends=("SYNTHETIC_NO_FIT",)),
        n_iter=1,
        created_at=AT,
    )
    identity = ModelArtifactIdentity(
        artifact=reference("trialmodel", artifact),
        forecaster=SYNTHETIC_KEY,
        family=ForecasterFamily.LOGISTIC_REGRESSION,
        model_version=artifact.artifact_adapter_version,
        request_reference=pin("recorded-training-request"),
        execution_reference=pin("recorded-training-execution"),
        subject=artifact.spec.subject,
        target_id="synthetic:positive-label",
        feature_schema_id="synthetic:five-patterns-v1",
        configuration_fingerprint=cast(str, artifact.spec.config.fingerprint),
        created_at=artifact.created_at,
    )
    store.put("scaler", artifact.reconstruction.scaler)
    store.put("trialmodel", artifact)
    store.put("modelidentity", identity)
    return store, identity, artifact


def logistic_request(
    identity: ModelArtifactIdentity,
    kind: DiagnosticKind,
    *,
    input_reference: ArtifactReference | None = None,
    version: str = SYNTHETIC_VERSION,
) -> DiagnosticRequest:
    evidence = (identity.artifact, input_reference) if input_reference else (identity.artifact,)
    return DiagnosticRequest(
        diagnostic_request_id=f"flc4:{kind.value.lower().replace('_', '-')}",
        forecaster=ForecasterKey(
            forecaster_id="forecaster:logistic-regression", implementation_version=version
        ),
        artifact_reference=identity.artifact,
        model_identity_reference=reference("modelidentity", identity),
        kind=kind,
        subject=identity.subject,
        target_id=identity.target_id,
        input_reference=input_reference,
        evidence_references=cast(tuple[ArtifactReference, ...], evidence),
        created_at=AT,
    )


def feature(identity: ModelArtifactIdentity) -> DiagnosticFeatureInput:
    return DiagnosticFeatureInput(
        input_id="flc4:synthetic-feature-vector",
        subject=identity.subject,
        target_id=identity.target_id,
        values=(1.5, 1.0, 6.0, 0.0, 9.0),
        evidence_references=(pin("authored-feature-vector"),),
        evidence_scope="SYNTHETIC_REFERENCE",
        observed_at=AT,
    )


def resolve_payload(store: DiagnosticStore, result: DiagnosticEnvelope) -> SealedResearch:
    assert result.payload_reference is not None
    return store.resolve(result.payload_reference)


def test_request_envelope_roundtrip_timezone_and_capability(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
) -> None:
    _, identity, _ = logistic_store
    request = logistic_request(identity, DiagnosticKind.LOGISTIC_COEFFICIENTS)
    assert DiagnosticRequest.model_validate_json(request.model_dump_json()) == request
    assert request.model_dump(mode="json")["evidence_references"] == [
        identity.artifact.model_dump(mode="json")
    ]
    rebuilt = DiagnosticRequest.model_validate(
        {**request.model_dump(), "created_at": request.created_at.astimezone(UTC)}
    )
    assert rebuilt == request and rebuilt.model_dump(mode="json")["created_at"].endswith("+05:30")
    assert ForecasterCapability.DIAGNOSTICS.value == "DIAGNOSTICS"
    with pytest.raises(ValidationError):
        request.kind = DiagnosticKind.LOGISTIC_PREPROCESSOR


def test_baserate_exact_support_no_backfill_and_replay(tmp_path: Path) -> None:
    runtime = fixture(pattern="baseline")
    store = DiagnosticStore(tmp_path / "base", create=True)
    original = canonical_json(runtime.artifact)
    result = generate_diagnostic(
        store, base_request(runtime.artifact), baserate_artifact=runtime.artifact
    )
    payload = resolve_payload(store, result)
    assert isinstance(payload, BaseRateSupportDiagnostic)
    assert payload.window_length == len(payload.transitions) == 20
    assert payload.eligible_count == runtime.artifact.eligible_count == 20
    assert payload.positive_count == runtime.artifact.positive_count
    assert payload.zero_count == 20 - runtime.artifact.positive_count
    assert payload.base_rate == runtime.artifact.positive_count / 20
    assert payload.replacement == "NO_BACKFILL"
    assert payload.scheduled_transition_ids == tuple(
        (row.reference_session_id, row.terminal_session_id) for row in runtime.artifact.rows
    )
    assert all(
        row.label_available_at is None
        or row.label_available_at <= runtime.artifact.fit_knowledge_cutoff
        for row in payload.transitions
        if row.included
    )
    assert canonical_json(runtime.artifact) == original
    assert replay_diagnostic(store, reference("diagnostic", result)) == "MATCH"
    assert not result.approval and not result.promotion and not result.activation


@pytest.mark.parametrize("included,late", [(19, False), (20, True)])
def test_baserate_missing_or_late_position_is_not_backfilled(
    tmp_path: Path, included: int, late: bool
) -> None:
    runtime = fixture(included=included, late_label=late)
    store = DiagnosticStore(tmp_path / f"base-{included}-{late}", create=True)
    result = generate_diagnostic(
        store, base_request(runtime.artifact), baserate_artifact=runtime.artifact
    )
    payload = cast(BaseRateSupportDiagnostic, resolve_payload(store, result))
    assert payload.eligible_count == 19 and payload.base_rate is None
    assert payload.unavailable_positions == (19,)
    assert payload.transitions[19].exclusion_reasons
    assert len(payload.scheduled_transition_ids) == 20


def test_logistic_coefficients_are_exact_and_descriptive(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
) -> None:
    store, identity, artifact = logistic_store
    result = generate_diagnostic(
        store, logistic_request(identity, DiagnosticKind.LOGISTIC_COEFFICIENTS)
    )
    payload = resolve_payload(store, result)
    assert isinstance(payload, LogisticCoefficientDiagnostic)
    assert payload.coefficients == artifact.reconstruction.coefficients
    assert payload.intercept == artifact.reconstruction.intercept
    assert payload.feature_order == artifact.reconstruction.scaler.feature_order
    assert payload.coefficient_semantics == "STANDARDIZED_FEATURE_LOG_ODDS_ASSOCIATION"
    assert payload.applicability == "RECORDED_STANDARDIZED_LINEAR_MODEL"
    assert not payload.causal_claim
    assert "limitation:not-feature-importance" in result.limitations
    assert not any(
        "importance" in name or "rank" in name
        for name in LogisticCoefficientDiagnostic.model_fields
    )


def test_logistic_preprocessor_is_exact(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
) -> None:
    store, identity, artifact = logistic_store
    result = generate_diagnostic(
        store, logistic_request(identity, DiagnosticKind.LOGISTIC_PREPROCESSOR)
    )
    payload = resolve_payload(store, result)
    scaler = artifact.reconstruction.scaler
    assert isinstance(payload, LogisticPreprocessorDiagnostic)
    assert payload.sample_count == scaler.n
    assert payload.means == scaler.means and payload.variances == scaler.variances
    assert payload.scales == scaler.scales and payload.constant_columns == scaler.constant_columns
    assert payload.config == scaler.config


def test_logistic_contribution_reconstructs_logit_probability_and_replay(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
) -> None:
    store, identity, artifact = logistic_store
    value = feature(identity)
    input_ref = reference("diaginput", value)
    result = generate_diagnostic(
        store,
        logistic_request(
            identity,
            DiagnosticKind.LOGISTIC_LINEAR_CONTRIBUTIONS,
            input_reference=input_ref,
        ),
        feature_input=value,
    )
    payload = resolve_payload(store, result)
    assert isinstance(payload, LogisticContributionDiagnostic)
    expected_standardized = tuple(
        (x - mean) / scale
        for x, mean, scale in zip(
            value.values,
            artifact.reconstruction.scaler.means,
            artifact.reconstruction.scaler.scales,
            strict=True,
        )
    )
    assert payload.standardized_values == expected_standardized
    assert payload.contributions == tuple(
        x * coefficient
        for x, coefficient in zip(
            expected_standardized, artifact.reconstruction.coefficients, strict=True
        )
    )
    assert payload.logit == payload.intercept + math.fsum(payload.contributions)
    assert payload.raw_uncalibrated_probability == reconstruct(
        artifact.reconstruction, value.values
    )
    assert not payload.calibration_applied and not payload.causal_claim
    assert not payload.trading_reason_claim
    assert payload.applicability == "RECORDED_OUTCOME_FREE_INFERENCE_INPUT"
    assert replay_diagnostic(store, reference("diagnostic", result)) == "MATCH"


def test_common_envelope_different_payload_schemas(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
    tmp_path: Path,
) -> None:
    store, identity, _ = logistic_store
    base = fixture().artifact
    base_store = DiagnosticStore(tmp_path / "base-envelope", create=True)
    envelopes = (
        generate_diagnostic(base_store, base_request(base), baserate_artifact=base),
        generate_diagnostic(
            store, logistic_request(identity, DiagnosticKind.LOGISTIC_COEFFICIENTS)
        ),
        generate_diagnostic(
            store, logistic_request(identity, DiagnosticKind.LOGISTIC_PREPROCESSOR)
        ),
    )
    assert all(isinstance(item, DiagnosticEnvelope) for item in envelopes)
    assert len({item.payload_schema_id for item in envelopes}) == 3
    assert {
        type(resolve_payload(base_store if i == 0 else store, item))
        for i, item in enumerate(envelopes)
    } == {
        BaseRateSupportDiagnostic,
        LogisticCoefficientDiagnostic,
        LogisticPreprocessorDiagnostic,
    }


def test_unsupported_and_unavailable_are_explicit_and_replayable(tmp_path: Path) -> None:
    store = DiagnosticStore(tmp_path / "status", create=True)
    missing_identity = ModelArtifactIdentity(
        artifact=pin("missing-model"),
        forecaster=ForecasterKey(
            forecaster_id="forecaster:logistic-regression", implementation_version="1.0"
        ),
        family=ForecasterFamily.LOGISTIC_REGRESSION,
        model_version="1.0",
        request_reference=pin("request"),
        execution_reference=pin("job"),
        subject="SYNTHETIC:STATUS",
        target_id="synthetic:status",
        feature_schema_id="five",
        configuration_fingerprint=semantic_fingerprint("config"),
        created_at=AT,
    )
    unavailable = generate_diagnostic(
        store, logistic_request(missing_identity, DiagnosticKind.LOGISTIC_COEFFICIENTS)
    )
    unsupported = generate_diagnostic(
        store,
        logistic_request(missing_identity, DiagnosticKind.LOGISTIC_PREPROCESSOR, version="9.0"),
    )
    assert unavailable.status is DiagnosticStatus.UNAVAILABLE
    assert unsupported.status is DiagnosticStatus.UNSUPPORTED
    for item in (unavailable, unsupported):
        assert item.payload_reference is None and item.reason
        assert replay_diagnostic(store, reference("diagnostic", item)) == "MATCH"


@pytest.mark.parametrize(
    "updates",
    [
        {"kind": "UNKNOWN"},
        {"scope": "PUBLIC"},
        {"evidence_policy": "OUTCOMES"},
        {"protected_outcomes_allowed": True},
        {"consumed_holdout_reuse": True},
        {"fitting_authorized": True},
        {"calibration_authorized": True},
        {"evaluation_authorized": True},
        {"approval_authorized": True},
        {"outcome": 1},
        {"ground_truth": "2025"},
    ],
)
def test_unknown_kind_authority_and_holdout_side_channels_rejected(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
    updates: dict[str, Any],
) -> None:
    _, identity, _ = logistic_store
    request = logistic_request(identity, DiagnosticKind.LOGISTIC_COEFFICIENTS)
    with pytest.raises(ValueError):
        DiagnosticRequest.model_validate({**request.model_dump(), **updates, "fingerprint": None})


@pytest.mark.parametrize("kind", list(DiagnosticKind))
def test_explicit_payload_schema_and_limitations(kind: DiagnosticKind) -> None:
    schema, version = payload_schema(kind)
    assert schema.startswith("tiaf.flc4.") and version == "1.0"
    assert limitations(kind) and "limitation:not-model-quality" in limitations(kind)


def test_incompatible_forecaster_kind_and_input_rejected(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
) -> None:
    _, identity, _ = logistic_store
    value = logistic_request(identity, DiagnosticKind.LOGISTIC_COEFFICIENTS)
    with pytest.raises(ValidationError, match="FORECASTER_KIND"):
        changed(
            value,
            forecaster=ForecasterKey(
                forecaster_id="forecaster:historical-base-rate", implementation_version="1.0"
            ),
        )
    with pytest.raises(ValidationError, match="INPUT_APPLICABILITY"):
        changed(value, input_reference=pin("unexpected-input"))


def test_recorded_model_lineage_mismatch_is_invalid_not_unavailable(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
) -> None:
    store, identity, _ = logistic_store
    request = logistic_request(identity, DiagnosticKind.LOGISTIC_COEFFICIENTS)
    with pytest.raises(ValueError, match="MODEL_LINEAGE_MISMATCH"):
        generate_diagnostic(store, changed(request, subject="SYNTHETIC:WRONG"))


def test_feature_input_cannot_contain_outcome_or_protected_data(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
) -> None:
    _, identity, _ = logistic_store
    value = feature(identity)
    for updates in (
        {"outcome_fields_present": True},
        {"protected_evidence_used": True},
        {"consumed_holdout_reused": True},
        {"label": 1},
        {"outcome": "positive"},
    ):
        with pytest.raises(ValueError):
            DiagnosticFeatureInput.model_validate(
                {**value.model_dump(), **updates, "fingerprint": None}
            )


def test_diagnostics_have_no_evaluation_lifecycle_calibration_or_optimization_authority(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
) -> None:
    store, identity, _ = logistic_store
    result = generate_diagnostic(
        store, logistic_request(identity, DiagnosticKind.LOGISTIC_COEFFICIENTS)
    )
    assert not result.evaluation_performed and not result.calibration_applied
    assert result.lifecycle_effect == result.optimization_effect == "NONE"
    assert not result.approval and not result.promotion and not result.activation
    for field, value in (
        ("evaluation_performed", True),
        ("calibration_applied", True),
        ("approval", True),
        ("promotion", True),
        ("activation", True),
        ("lifecycle_effect", "PROMOTE"),
        ("optimization_effect", "SELECT"),
        ("brier", 0.1),
        ("log_loss", 0.2),
    ):
        with pytest.raises(ValueError):
            DiagnosticEnvelope.model_validate(
                {**result.model_dump(), field: value, "fingerprint": None}
            )
    for method in ("fit", "evaluate", "calibrate", "approve", "promote", "activate", "select"):
        assert not hasattr(result, method)


def test_replay_tamper_is_mismatch(tmp_path: Path) -> None:
    runtime = fixture()
    store = DiagnosticStore(tmp_path / "tamper", create=True)
    result = generate_diagnostic(
        store, base_request(runtime.artifact), baserate_artifact=runtime.artifact
    )
    assert result.fingerprint
    path = store.root / f"diagnostic-{result.fingerprint}.json"
    path.write_text(path.read_text().replace('"activation":false', '"activation":true'))
    assert replay_diagnostic(store, reference("diagnostic", result)) == "MISMATCH"


def test_recorded_replay_module_has_no_fit_evaluation_calibration_or_provider_imports() -> None:
    from tiaf.learning import forecaster_diagnostics as module

    tree = ast.parse(Path(module.__file__).read_text())
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)] + [
        name.name for node in ast.walk(tree) if isinstance(node, ast.Import) for name in node.names
    ]
    assert not any(
        token in name
        for name in imports
        for token in ("sklearn", "evaluation", "optimization", "provider", "socket", "requests")
    )
    source = Path(module.__file__).read_text()
    assert ".fit(" not in source and "arm_metrics" not in source


def test_json_collections_and_stable_fingerprint(
    logistic_store: tuple[DiagnosticStore, ModelArtifactIdentity, SyntheticModel],
) -> None:
    store, identity, _ = logistic_store
    result = generate_diagnostic(
        store, logistic_request(identity, DiagnosticKind.LOGISTIC_COEFFICIENTS)
    )
    assert DiagnosticEnvelope.model_validate_json(result.model_dump_json()) == result
    assert isinstance(result.lineage_references, tuple)
    assert isinstance(result.model_dump(mode="json")["lineage_references"], list)
    assert semantic_fingerprint(result) == semantic_fingerprint(
        DiagnosticEnvelope.model_validate(result.model_dump())
    )
    with pytest.raises(ValidationError):
        result.limitations = ()
