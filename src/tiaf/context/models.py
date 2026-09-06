"""Provider-neutral immutable AnalysisContext contracts."""

from datetime import date
from typing import Self

from pydantic import Field, field_validator, model_validator

from tiaf.context.enums import BatchItemStatus, EvidenceRequirement, EvidenceStatus
from tiaf.context.requirements import AnalysisContextRequirement, validate_safe_metadata
from tiaf.contracts import ContractModel, DataQuality, FreshnessState
from tiaf.contracts.common import Metadata, NonEmptyStr, Symbol, TiafDateTime
from tiaf.data import HistoricalOptionSeries, HistoricalSeries, OptionChainSnapshot, QuoteSnapshot
from tiaf.data.models import NormalizedProvider
from tiaf.data.resolution import ResolvedInstrument
from tiaf.data.runtime import CacheDisposition, FetchDisposition, ProviderGateState


class AnalysisSubject(ContractModel):
    """Canonical identity and request attribution for one context."""

    symbol: Symbol
    resolved_instrument: ResolvedInstrument
    requested_at: TiafDateTime
    source_system: NonEmptyStr | None = None
    correlation_id: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_symbol(self) -> Self:
        if self.symbol != self.resolved_instrument.instrument.symbol:
            raise ValueError("subject symbol must match the resolved instrument")
        return self


class EvidenceDescriptor(ContractModel):
    """Requirement role and dual retrieval/observation provenance for one slot."""

    evidence_name: NonEmptyStr
    requested: bool
    required: bool
    requirement_role: EvidenceRequirement
    status: EvidenceStatus
    retrieval_freshness: FreshnessState | None = None
    quality: DataQuality | None = None
    source_provider: NormalizedProvider | None = None
    source_observed_at: TiafDateTime | None = None
    received_at: TiafDateTime | None = None
    retrieval_age_seconds: float | None = Field(default=None, ge=0)
    observation_age_seconds: float | None = Field(default=None, ge=0)
    source_observation_semantics: NonEmptyStr | None = None
    cache_disposition: CacheDisposition | None = None
    fetch_disposition: FetchDisposition | None = None
    stale_fallback_used: bool = False
    deferred_reason: NonEmptyStr | None = None
    deferred_provider: NormalizedProvider | None = None
    deferred_operation: NonEmptyStr | None = None
    retry_after_seconds: float | None = Field(default=None, ge=0)
    gate_state: ProviderGateState | None = None
    error_type: NonEmptyStr | None = None
    error_detail: NonEmptyStr | None = None
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_status(self) -> Self:
        expected_role = (
            EvidenceRequirement.REQUIRED
            if self.required
            else (
                EvidenceRequirement.OPTIONAL_REQUESTED
                if self.requested
                else EvidenceRequirement.NOT_REQUESTED
            )
        )
        if self.requirement_role is not expected_role:
            raise ValueError("requirement_role must agree with requested and required")
        if self.required and not self.requested:
            raise ValueError("required evidence must also be requested")
        if self.status is EvidenceStatus.NOT_REQUESTED and self.requested:
            raise ValueError("requested evidence cannot have NOT_REQUESTED status")
        if self.status is not EvidenceStatus.NOT_REQUESTED and not self.requested:
            raise ValueError("unrequested evidence must have NOT_REQUESTED status")
        if self.status is EvidenceStatus.FAILED:
            if self.error_type is None or self.error_detail is None:
                raise ValueError("FAILED evidence requires error_type and error_detail")
        elif self.error_type is not None or self.error_detail is not None:
            raise ValueError("error fields are only valid for FAILED evidence")
        deferred_fields = (
            self.deferred_reason,
            self.deferred_provider,
            self.deferred_operation,
            self.gate_state,
        )
        factual_fields = (
            self.retrieval_freshness,
            self.quality,
            self.source_provider,
            self.source_observed_at,
            self.received_at,
            self.retrieval_age_seconds,
            self.observation_age_seconds,
            self.source_observation_semantics,
            self.cache_disposition,
            self.fetch_disposition,
        )
        if self.status is EvidenceStatus.DEFERRED:
            if any(value is None for value in deferred_fields):
                raise ValueError(
                    "DEFERRED evidence requires reason, provider, operation, and gate state"
                )
            if any(value is not None for value in factual_fields):
                raise ValueError("DEFERRED evidence cannot claim factual provenance")
        elif any(value is not None for value in (*deferred_fields, self.retry_after_seconds)):
            raise ValueError("deferred fields are only valid for DEFERRED evidence")
        if self.status is EvidenceStatus.NOT_REQUESTED:
            if any(value is not None for value in factual_fields):
                raise ValueError("NOT_REQUESTED evidence cannot carry factual provenance")
        return self


class AnalysisContext(ContractModel):
    """One coherent immutable substrate with required-only retrieval freshness."""

    context_id: NonEmptyStr
    subject: AnalysisSubject
    requirements: AnalysisContextRequirement
    quote: QuoteSnapshot | None = None
    history: HistoricalSeries | None = None
    option_chain: OptionChainSnapshot | None = None
    historical_options: tuple[HistoricalOptionSeries, ...] | None = None
    evidence: tuple[EvidenceDescriptor, ...]
    created_at: TiafDateTime
    overall_quality: DataQuality
    overall_retrieval_freshness: FreshnessState
    complete: bool
    missing_required_evidence: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    metadata: Metadata = Field(default_factory=dict)

    _safe_metadata = field_validator("metadata")(validate_safe_metadata)

    @model_validator(mode="after")
    def validate_coherence(self) -> Self:
        names = tuple(item.evidence_name for item in self.evidence)
        if len(names) != len(set(names)):
            raise ValueError("evidence names must be unique within a context")
        required_names = {item.evidence_name for item in self.evidence if item.required}
        if not set(self.missing_required_evidence) <= required_names:
            raise ValueError("missing_required_evidence must name required evidence slots")
        if self.complete != (not self.missing_required_evidence):
            raise ValueError("complete must agree with missing_required_evidence")
        if self.created_at < self.subject.requested_at:
            raise ValueError("created_at must not be earlier than requested_at")

        instrument = self.subject.resolved_instrument.instrument
        if self.quote is not None and self.quote.instrument != instrument:
            raise ValueError("quote must match the analysis subject instrument")
        if self.history is not None and self.history.instrument != instrument:
            raise ValueError("history must match the analysis subject instrument")
        if self.option_chain is not None and self.option_chain.underlying != instrument:
            raise ValueError("option chain must match the analysis subject instrument")
        if self.historical_options is not None:
            if any(series.underlying != instrument for series in self.historical_options):
                raise ValueError("historical options must match the analysis subject instrument")

        if not self.requirements.include_quote and self.quote is not None:
            raise ValueError("unrequested quote must not be embedded")
        if not self.requirements.include_history and self.history is not None:
            raise ValueError("unrequested history must not be embedded")
        if not self.requirements.include_derivatives and self.option_chain is not None:
            raise ValueError("unrequested option chain must not be embedded")
        if (
            not self.requirements.include_historical_options
            and self.historical_options is not None
        ):
            raise ValueError("unrequested historical options must not be embedded")
        return self


class AnalysisContextBatchItem(ContractModel):
    """Explicit completed, partial, deferred, or error batch outcome."""

    symbol: Symbol
    status: BatchItemStatus
    context: AnalysisContext | None = None
    error_type: NonEmptyStr | None = None
    error_detail: NonEmptyStr | None = None
    reason: NonEmptyStr | None = None
    provider: NormalizedProvider | None = None
    operation: NonEmptyStr | None = None
    retry_after_seconds: float | None = Field(default=None, ge=0)
    gate_state: ProviderGateState | None = None
    context_id: NonEmptyStr | None = None
    correlation_id: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        has_error = self.error_type is not None or self.error_detail is not None
        deferred_fields = (self.reason, self.provider, self.operation, self.gate_state)
        has_deferred = any(
            value is not None for value in (*deferred_fields, self.retry_after_seconds)
        )
        if self.status is BatchItemStatus.COMPLETE_CONTEXT:
            if self.context is None or not self.context.complete:
                raise ValueError("COMPLETE_CONTEXT requires a complete context")
            if has_error or has_deferred:
                raise ValueError("COMPLETE_CONTEXT cannot carry error or deferred fields")
        elif self.status is BatchItemStatus.PARTIAL_CONTEXT:
            if self.context is None or self.context.complete:
                raise ValueError("PARTIAL_CONTEXT requires an incomplete context")
            if has_error or has_deferred:
                raise ValueError("PARTIAL_CONTEXT cannot carry error or deferred fields")
        elif self.status is BatchItemStatus.DEFERRED:
            if self.error_type is None or self.error_detail is None:
                raise ValueError("DEFERRED requires typed error details")
            if any(value is None for value in deferred_fields):
                raise ValueError(
                    "DEFERRED requires reason, provider, operation, and gate state"
                )
        else:
            if self.context is not None:
                raise ValueError("ERROR cannot carry a context")
            if self.error_type is None or self.error_detail is None:
                raise ValueError("ERROR requires typed error details")
            if has_deferred:
                raise ValueError("ERROR cannot carry deferred fields")
        if self.context is not None:
            if self.context_id not in {None, self.context.context_id}:
                raise ValueError("context_id must match the batch context")
            if self.correlation_id not in {
                None,
                self.context.subject.correlation_id,
            }:
                raise ValueError("correlation_id must match the batch context")
        elif self.context_id is not None:
            raise ValueError("context_id requires a retained context")
        return self


class ContextSummary(ContractModel):
    """Deterministic diagnostics whose freshness describes retrieval only."""

    symbol: Symbol
    quote_ltp: float | None = None
    history_bar_count: int = Field(ge=0)
    option_chain_strike_count: int = Field(ge=0)
    option_expiry: date | None = None
    historical_option_series_count: int = Field(ge=0)
    overall_quality: DataQuality
    overall_retrieval_freshness: FreshnessState
    complete: bool
    missing_required_evidence: tuple[str, ...]
    warnings: tuple[str, ...]
