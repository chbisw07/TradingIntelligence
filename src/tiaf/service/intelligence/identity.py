"""Provider-neutral service identity, with references to existing model identities."""

from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator

from tiaf.agents.models import ReasoningModelIdentity
from tiaf.forecasting.identity import ArtifactReference, LogicalId
from tiaf.forecasting.inference_contracts import FamilyIdentifier, ForecasterKey

from .common import ClaimKind, IntelligenceContract, Version, unique


class ProducerType(StrEnum):
    FORECASTER = "FORECASTER"
    CLASSIFIER = "CLASSIFIER"
    REGRESSOR = "REGRESSOR"
    RANKER = "RANKER"
    LLM = "LLM"
    AGENT = "AGENT"
    RULE_ENGINE = "RULE_ENGINE"
    ENSEMBLE = "ENSEMBLE"
    HUMAN_ASSISTED = "HUMAN_ASSISTED"


class CapabilityKind(StrEnum):
    FORECAST = "FORECAST"
    CLASSIFICATION = "CLASSIFICATION"
    REGRESSION = "REGRESSION"
    RANKING = "RANKING"
    ANALYSIS = "ANALYSIS"
    SYNTHESIS = "SYNTHESIS"


class ServiceIdentity(IntelligenceContract):
    service_id: LogicalId
    service_version: Version


class CapabilityDeclaration(IntelligenceContract):
    capability_id: LogicalId
    capability_version: Version
    kind: CapabilityKind
    claim_kinds: tuple[ClaimKind, ...] = Field(default=(), max_length=7)

    @model_validator(mode="after")
    def validate_kinds(self) -> Self:
        unique(self.claim_kinds, "CLAIM_KIND")
        return self


class ProducerIdentity(IntelligenceContract):
    producer_id: LogicalId
    producer_type: ProducerType
    service: ServiceIdentity
    configuration_version: Version
    capability: CapabilityDeclaration
    # Existing key is reused for model-backed non-LLM implementations; no new model ID type.
    model: ForecasterKey | None = None
    model_family: FamilyIdentifier | None = None
    artifact_identity: ArtifactReference | None = None
    training_identity: ArtifactReference | None = None
    llm: ReasoningModelIdentity | None = None
    prompt_version: Version | None = None
    tool_config_version: Version | None = None
    orchestration_version: Version | None = None

    @model_validator(mode="after")
    def identity_closure(self) -> Self:
        llm_fields = (
            self.llm,
            self.prompt_version,
            self.tool_config_version,
            self.orchestration_version,
        )
        if self.producer_type is ProducerType.LLM:
            if any(item is None for item in llm_fields) or self.model is not None:
                raise ValueError("LLM_IDENTITY_INCOMPLETE_OR_CONFLICTING")
            assert self.llm is not None
            ReasoningModelIdentity.model_validate(self.llm.model_dump())
        elif any(item is not None for item in llm_fields):
            raise ValueError("LLM_FIELDS_REQUIRE_LLM_PRODUCER")
        if (
            self.model is None
            and self.llm is None
            and any(
                value is not None
                for value in (self.model_family, self.artifact_identity, self.training_identity)
            )
        ):
            raise ValueError("MODEL_METADATA_REQUIRES_MODEL_IDENTITY")
        return self


class ActiveLLMConfiguration(IntelligenceContract):
    """One primary binding per scope; not selection, activation or failover logic."""

    scope_id: LogicalId
    configuration_id: LogicalId
    primary: ProducerIdentity

    @model_validator(mode="after")
    def llm_only(self) -> Self:
        if self.primary.producer_type is not ProducerType.LLM:
            raise ValueError("PRIMARY_MUST_BE_LLM")
        return self
