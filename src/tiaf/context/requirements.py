"""Immutable, explicit requirements for AnalysisContext assembly."""

from datetime import date
from typing import Any, Self

from pydantic import Field, field_validator, model_validator

from tiaf.context.enums import AnalysisPurpose
from tiaf.contracts import ContractModel, Horizon, OptionType, TradeStyle
from tiaf.contracts.common import Metadata
from tiaf.data import ExpiryFlag, HistoricalOptionExpiryCode, RelativeStrike
from tiaf.data.models import NormalizedInterval
from tiaf.data.runtime import FreshnessRequirement

_SENSITIVE_METADATA_PARTS = (
    "access_token",
    "api_key",
    "apikey",
    "authorization",
    "client_id",
    "credential",
    "password",
    "secret",
)


def validate_safe_metadata(value: Metadata) -> Metadata:
    """Reject credential-shaped keys recursively from public context metadata."""
    pending: list[Any] = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                normalized = key.casefold().replace("-", "_")
                if any(part in normalized for part in _SENSITIVE_METADATA_PARTS):
                    raise ValueError(
                        f"credentials are not permitted in context metadata: {key}"
                    )
                pending.append(item)
        elif isinstance(current, list):
            pending.extend(current)
    return value


class HistoricalOptionRequirement(ContractModel):
    """One exact, bounded rolling historical-option factual request."""

    interval: NormalizedInterval
    expiry_flag: ExpiryFlag
    expiry_code: HistoricalOptionExpiryCode
    relative_strike: RelativeStrike
    option_type: OptionType
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.end_date <= self.start_date:
            raise ValueError("historical option end_date must be later than start_date")
        return self


class AnalysisContextRequirement(ContractModel):
    """Caller-owned description of which facts to request and require."""

    purpose: AnalysisPurpose
    trade_style: TradeStyle | None = None
    horizon: Horizon | None = None

    include_quote: bool = True
    include_history: bool = True
    include_derivatives: bool = False
    include_historical_options: bool = False

    require_quote: bool = True
    require_history: bool = True
    require_derivatives: bool = False
    require_historical_options: bool = False

    history_interval: str | None = None
    history_lookback_days: int | None = Field(default=None, gt=0)
    option_expiry: date | None = None
    historical_option_requests: tuple[HistoricalOptionRequirement, ...] = ()

    allow_partial: bool = True
    allow_stale_on_error: bool = False
    quote_freshness: FreshnessRequirement | None = None
    history_freshness: FreshnessRequirement | None = None
    derivatives_freshness: FreshnessRequirement | None = None
    historical_options_freshness: FreshnessRequirement | None = None
    metadata: Metadata = Field(default_factory=dict)

    @field_validator("metadata")
    @classmethod
    def reject_credentials(cls, value: Metadata) -> Metadata:
        return validate_safe_metadata(value)

    @model_validator(mode="before")
    @classmethod
    def required_evidence_is_included(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        normalized = dict(value)
        for name in ("quote", "history", "derivatives", "historical_options"):
            if normalized.get(f"require_{name}") is True:
                normalized[f"include_{name}"] = True
        return normalized

    @model_validator(mode="after")
    def validate_evidence_parameters(self) -> Self:
        if self.include_history:
            if self.history_interval is None or not self.history_interval.strip():
                raise ValueError("included history requires history_interval")
            if self.history_lookback_days is None:
                raise ValueError("included history requires history_lookback_days")
        elif self.history_interval is not None or self.history_lookback_days is not None:
            raise ValueError("history parameters require include_history=True")

        if self.include_derivatives and self.option_expiry is None:
            raise ValueError("included derivatives require an explicit option_expiry")
        if not self.include_derivatives and self.option_expiry is not None:
            raise ValueError("option_expiry requires include_derivatives=True")

        if self.include_historical_options and not self.historical_option_requests:
            raise ValueError(
                "included historical options require exact historical_option_requests"
            )
        if not self.include_historical_options and self.historical_option_requests:
            raise ValueError(
                "historical_option_requests require include_historical_options=True"
            )
        return self
