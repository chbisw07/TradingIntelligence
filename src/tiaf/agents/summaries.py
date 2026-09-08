"""Small factual summaries of Agent records without recommendation logic."""

from pydantic import Field

from tiaf.contracts import ContractModel
from tiaf.contracts.common import NonEmptyStr, Symbol

from .budget import NonNegativeFiniteFloat
from .enums import AgentRunStatus, AgentStance, SpecialistId
from .models import AgentRunRecord


class AgentRunSummary(ContractModel):
    """Diagnostic projection of one immutable specialist run."""

    run_id: NonEmptyStr
    subject: Symbol
    specialist: SpecialistId
    status: AgentRunStatus
    stance: AgentStance | None = None
    evidence_fingerprint: NonEmptyStr
    deterministic_baseline_reference: NonEmptyStr
    cited_claim_count: int = Field(ge=0)
    missing_evidence_count: int = Field(ge=0)
    llm_calls: int = Field(ge=0)
    tool_calls: int = Field(ge=0)
    cost_units: NonNegativeFiniteFloat
    elapsed_seconds: NonNegativeFiniteFloat


def summarize_agent_run(record: AgentRunRecord) -> AgentRunSummary:
    """Return factual status/usage without inferring a market conclusion."""
    opinion = record.opinion
    return AgentRunSummary(
        run_id=record.request.run_id,
        subject=record.request.subject,
        specialist=record.specialist,
        status=record.status,
        stance=opinion.stance if opinion is not None else None,
        evidence_fingerprint=record.request.evidence_fingerprint,
        deterministic_baseline_reference=record.request.deterministic_baseline_reference,
        cited_claim_count=len(opinion.evidence_claims) if opinion is not None else 0,
        missing_evidence_count=len(opinion.missing_evidence) if opinion is not None else 0,
        llm_calls=record.usage.llm_calls,
        tool_calls=record.usage.tool_calls,
        cost_units=record.usage.cost_units,
        elapsed_seconds=record.usage.elapsed_seconds,
    )
