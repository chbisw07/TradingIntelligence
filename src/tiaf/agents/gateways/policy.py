"""Provider-neutral A3.2 authorization, model mapping, and budget policy."""

from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from tiaf.agents._validation import require_unique, validate_safe_metadata
from tiaf.agents.budget import AgentBudget
from tiaf.agents.enums import AgentCapability
from tiaf.agents.models import ReasoningField
from tiaf.contracts import ContractModel
from tiaf.contracts.common import Metadata, NonEmptyStr

from .enums import DowngradePolicy, ModelCapability, ModelTier, model_tier_rank


class EvidenceGatewayPolicy(ContractModel):
    """Global ceiling for capabilities the evidence runtime may authorize."""

    schema_version: Literal["1.0"] = "1.0"
    enabled_capabilities: tuple[AgentCapability, ...]
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_capabilities(self) -> Self:
        if not self.enabled_capabilities:
            raise ValueError("evidence policy requires enabled capabilities")
        require_unique(self.enabled_capabilities, "enabled evidence capabilities")
        return self


class ModelTierMapping(ContractModel):
    """Configuration-driven mapping from a generic tier to one provider model."""

    tier: ModelTier
    provider_id: NonEmptyStr
    model_id: NonEmptyStr
    model_version: NonEmptyStr | None = None
    configuration_id: NonEmptyStr
    configuration: tuple[ReasoningField, ...] = ()

    @model_validator(mode="after")
    def validate_tier(self) -> Self:
        if self.tier is ModelTier.NONE:
            raise ValueError("NONE tier cannot map to a provider")
        require_unique(tuple(item.name for item in self.configuration), "model configuration")
        return self


class ReasoningGatewayPolicy(ContractModel):
    """Global authority ceiling for optional model reasoning."""

    schema_version: Literal["1.0"] = "1.0"
    enabled: bool = False
    default_model_tier: ModelTier = ModelTier.NONE
    max_model_tier: ModelTier = ModelTier.NONE
    allowed_model_tiers: tuple[ModelTier, ...] = (ModelTier.NONE,)
    allowed_model_capabilities: tuple[ModelCapability, ...] = (
        ModelCapability.STRUCTURED_REASONING,
    )
    model_mappings: tuple[ModelTierMapping, ...] = ()
    budget: AgentBudget = Field(default_factory=AgentBudget)
    downgrade_policy: DowngradePolicy = DowngradePolicy.FAIL
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_policy(self) -> Self:
        if not self.allowed_model_tiers:
            raise ValueError("reasoning policy requires allowed tiers")
        require_unique(self.allowed_model_tiers, "allowed model tiers")
        require_unique(self.allowed_model_capabilities, "allowed model capabilities")
        mapping_tiers = tuple(item.tier for item in self.model_mappings)
        require_unique(mapping_tiers, "model tier mappings")
        if ModelTier.NONE not in self.allowed_model_tiers:
            raise ValueError("reasoning policy must preserve NONE/no-LLM tier")
        if self.default_model_tier not in self.allowed_model_tiers:
            raise ValueError("default model tier must be allowed")
        if any(
            model_tier_rank(item) > model_tier_rank(self.max_model_tier)
            for item in self.allowed_model_tiers
        ):
            raise ValueError("allowed model tier exceeds global maximum")
        if not self.enabled:
            if self.default_model_tier is not ModelTier.NONE:
                raise ValueError("disabled reasoning must default to NONE")
        else:
            mapped = set(mapping_tiers)
            required = {item for item in self.allowed_model_tiers if item is not ModelTier.NONE}
            if not required <= mapped:
                raise ValueError("every enabled non-NONE tier requires a model mapping")
        return self

    def mapping(self, tier: ModelTier) -> ModelTierMapping | None:
        """Return the configured mapping for a tier without vendor branching."""
        return next((item for item in self.model_mappings if item.tier is tier), None)


def budget_within(requested: AgentBudget, ceiling: AgentBudget) -> bool:
    """Return whether every request limit is bounded by global policy."""
    total_within = (
        ceiling.max_total_tokens is None
        or (
            requested.max_total_tokens is not None
            and requested.max_total_tokens <= ceiling.max_total_tokens
        )
    )
    return (
        requested.max_llm_calls <= ceiling.max_llm_calls
        and requested.max_tool_calls <= ceiling.max_tool_calls
        and requested.max_input_tokens <= ceiling.max_input_tokens
        and requested.max_output_tokens <= ceiling.max_output_tokens
        and total_within
        and requested.max_cost_units <= ceiling.max_cost_units
        and requested.max_elapsed_seconds <= ceiling.max_elapsed_seconds
    )
