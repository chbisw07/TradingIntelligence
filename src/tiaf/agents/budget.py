"""Immutable budget and usage contracts for bounded specialist execution."""

from typing import Annotated

from pydantic import Field, field_validator

from tiaf.contracts import ContractModel
from tiaf.contracts.common import Metadata

from ._validation import validate_safe_metadata
from .errors import AgentBudgetExceededError

NonNegativeFiniteFloat = Annotated[float, Field(ge=0, allow_inf_nan=False)]
PositiveFiniteFloat = Annotated[float, Field(gt=0, allow_inf_nan=False)]


class AgentUsage(ContractModel):
    """Observed vendor-neutral resource consumption for one specialist run."""

    llm_calls: int = Field(default=0, ge=0)
    tool_calls: int = Field(default=0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cost_units: NonNegativeFiniteFloat = 0.0
    elapsed_seconds: NonNegativeFiniteFloat = 0.0
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)


class AgentBudget(ContractModel):
    """Hard request limits with no vendor-pricing assumptions."""

    max_llm_calls: int = Field(default=0, ge=0)
    max_tool_calls: int = Field(default=0, ge=0)
    max_input_tokens: int = Field(default=0, ge=0)
    max_output_tokens: int = Field(default=0, ge=0)
    max_cost_units: NonNegativeFiniteFloat = 0.0
    max_elapsed_seconds: PositiveFiniteFloat = 30.0
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    def violations(self, usage: AgentUsage) -> tuple[str, ...]:
        """Return every exceeded limit without changing either contract."""
        checks = (
            (usage.llm_calls, self.max_llm_calls, "llm_calls"),
            (usage.tool_calls, self.max_tool_calls, "tool_calls"),
            (usage.input_tokens, self.max_input_tokens, "input_tokens"),
            (usage.output_tokens, self.max_output_tokens, "output_tokens"),
            (usage.cost_units, self.max_cost_units, "cost_units"),
            (usage.elapsed_seconds, self.max_elapsed_seconds, "elapsed_seconds"),
        )
        return tuple(name for actual, maximum, name in checks if actual > maximum)

    def ensure_within(self, usage: AgentUsage) -> None:
        """Raise a typed error when any reported/observed usage exceeds limits."""
        violations = self.violations(usage)
        if violations:
            raise AgentBudgetExceededError(
                f"Agent usage exceeded budget limits: {', '.join(violations)}"
            )
