"""Immutable A6 request, evidence, admission, candidate, and assessment contracts."""

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Annotated, Literal, Self

from pydantic import (
    BeforeValidator,
    Field,
    StrictInt,
    ValidationError,
    field_validator,
    model_validator,
)

from tiaf.contracts import ContractModel, OptionType
from tiaf.contracts.common import NonEmptyStr, Symbol, TiafDateTime
from tiaf.planner.models import Sha256
from tiaf.source_semantics.contracts import QualifiedId

from .enums import (
    A6ErrorCode,
    AdmissionOutcome,
    CandidateEligibility,
    CandidateGateId,
    CoverageState,
    EvaluationIntent,
    EventEvidenceState,
    EventMateriality,
    EventRelevance,
    ExpirationQualification,
    ExpressionDirection,
    ExpressionDisposition,
    ExpressionHorizonClass,
    FreshnessBasis,
    GateStatus,
    MoneynessLabel,
    SpreadEligibility,
    SpreadQualityTier,
    SubjectClass,
    TimingQualification,
)
from .errors import A6ContractError


def _decimal(value: object) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean is not a decimal quantity")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid decimal quantity") from exc
    if not result.is_finite():
        raise ValueError("decimal quantity must be finite")
    return Decimal(0) if result == 0 else result.normalize()


FiniteDecimal = Annotated[Decimal, BeforeValidator(_decimal)]
NonNegativeDecimal = Annotated[Decimal, BeforeValidator(_decimal), Field(ge=Decimal(0))]
PositiveDecimal = Annotated[Decimal, BeforeValidator(_decimal), Field(gt=Decimal(0))]
NonNegativeStrictInt = Annotated[StrictInt, Field(ge=0)]
PositiveStrictInt = Annotated[StrictInt, Field(gt=0)]


def _canonical(value: object) -> object:
    if isinstance(value, ContractModel):
        value = value.model_dump(mode="python")
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, Decimal):
        return "0" if value == 0 else format(value.normalize(), "f")
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    return value


_FORBIDDEN_KEY_PARTS = (
    "access_token",
    "account_id",
    "api_key",
    "apikey",
    "authorization",
    "broker_account",
    "client_id",
    "credential",
    "password",
    "secret",
)
_FORBIDDEN_VALUE_MARKERS = (
    "access_token=",
    "api_key=",
    "authorization:",
    "client_secret=",
    "password=",
    "file://",
    ":/home/",
    ":/tmp/",
)


def _validate_portable(value: object) -> None:
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, ContractModel):
            pending.append(current.model_dump(mode="python"))
        elif isinstance(current, dict):
            for key, item in current.items():
                normalized_key = str(key).casefold().replace("-", "_")
                if any(part in normalized_key for part in _FORBIDDEN_KEY_PARTS):
                    raise ValueError(f"secret-bearing field is not portable: {key}")
                pending.append(item)
        elif isinstance(current, (tuple, list)):
            pending.extend(current)
        elif isinstance(current, str):
            normalized = current.casefold()
            if current.startswith(("/", "~/")) or any(
                marker in normalized for marker in _FORBIDDEN_VALUE_MARKERS
            ):
                raise ValueError("secret-shaped or local-path text is not portable")


def canonical_json(value: object) -> str:
    """Serialize semantic content without wall-clock or environment dependence."""
    _validate_portable(value)
    return json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"), allow_nan=False)


def semantic_fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _sorted_unique(values: tuple[str, ...], label: str) -> tuple[str, ...]:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")
    return tuple(sorted(values))


class ExpressionHorizon(ContractModel):
    schema_id: Literal["tiaf.a6.expression-horizon"] = "tiaf.a6.expression-horizon"
    schema_version: Literal["1.0"] = "1.0"
    horizon_class: ExpressionHorizonClass
    target_end_at: TiafDateTime
    exact_duration_seconds: PositiveDecimal

    def validate_against(self, cutoff: datetime) -> None:
        delta = self.target_end_at - cutoff
        actual = Decimal(delta.days * 86400 + delta.seconds) + (
            Decimal(delta.microseconds) / Decimal(1_000_000)
        )
        if actual != self.exact_duration_seconds:
            raise ValueError("horizon exact duration does not match cutoff and target")


class PolicySelection(ContractModel):
    schema_id: Literal["tiaf.a6.policy-selection"] = "tiaf.a6.policy-selection"
    schema_version: Literal["1.0"] = "1.0"
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    profile_id: QualifiedId
    policy_fingerprint: Sha256
    evaluator_id: QualifiedId
    evaluator_version: NonEmptyStr
    normalizer_id: QualifiedId
    normalizer_version: NonEmptyStr


class ExpressionPreferences(ContractModel):
    schema_id: Literal["tiaf.a6.expression-preferences"] = "tiaf.a6.expression-preferences"
    schema_version: Literal["1.0"] = "1.0"
    moneyness_order: tuple[MoneynessLabel, ...] = (
        MoneynessLabel.ATM,
        MoneynessLabel.ITM1,
        MoneynessLabel.OTM1,
    )
    premium_cap: PositiveDecimal | None = None
    premium_currency: Literal["INR"] | None = None
    require_event_clear: bool = False

    @model_validator(mode="after")
    def bounded(self) -> Self:
        if not self.moneyness_order or len(self.moneyness_order) > 3:
            raise ValueError("moneyness preference must contain one to three labels")
        if len(set(self.moneyness_order)) != len(self.moneyness_order):
            raise ValueError("moneyness preference labels must be unique")
        if (self.premium_cap is None) != (self.premium_currency is None):
            raise ValueError("premium cap and currency must be supplied together")
        return self


class TradeExpressionRequest(ContractModel):
    schema_id: Literal["tiaf.a6.trade-expression-request"] = "tiaf.a6.trade-expression-request"
    schema_version: Literal["1.0"] = "1.0"
    request_id: QualifiedId
    run_id: QualifiedId
    intent: EvaluationIntent = EvaluationIntent.CAPTURED
    subject: Symbol
    subject_class: SubjectClass
    objective: NonEmptyStr
    direction: ExpressionDirection
    horizon: ExpressionHorizon
    evaluation_cutoff: TiafDateTime
    a4_result_ref: QualifiedId
    a4_result_fingerprint: Sha256
    derivatives_capture_ref: QualifiedId
    derivatives_capture_fingerprint: Sha256
    policy: PolicySelection
    preferences: ExpressionPreferences = Field(default_factory=ExpressionPreferences)
    correlation_id: QualifiedId | None = None
    source_candidate_ref: QualifiedId | None = None
    authority_refs: tuple[QualifiedId, ...]

    @field_validator("authority_refs", mode="after")
    @classmethod
    def sorted_authorities(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("request requires an authority reference")
        return _sorted_unique(values, "request authority refs")

    @model_validator(mode="after")
    def exact_horizon(self) -> Self:
        self.horizon.validate_against(self.evaluation_cutoff)
        return self


class MarketTimingQualification(ContractModel):
    schema_id: Literal["tiaf.a6.market-timing"] = "tiaf.a6.market-timing"
    schema_version: Literal["1.0"] = "1.0"
    observed_at: TiafDateTime | None = None
    acquired_at: TiafDateTime
    qualification: TimingQualification
    freshness_basis: FreshnessBasis
    qualification_source_ref: QualifiedId | None = None

    @model_validator(mode="after")
    def timing_authority(self) -> Self:
        if self.observed_at is not None and self.acquired_at < self.observed_at:
            raise ValueError("acquisition cannot predate market observation")
        if self.qualification is TimingQualification.QUALIFIED:
            if self.observed_at is None:
                raise ValueError("qualified timing requires market observation time")
            if self.freshness_basis is not FreshnessBasis.MARKET_OBSERVATION_TIME:
                raise ValueError("qualified timing requires observation-time freshness")
            if self.qualification_source_ref is None:
                raise ValueError("qualified timing requires an authority reference")
        if self.freshness_basis is FreshnessBasis.ACQUISITION_TIME_ONLY:
            if self.observed_at is not None:
                raise ValueError("acquisition-only timing cannot claim observation time")
            if self.qualification is TimingQualification.QUALIFIED:
                raise ValueError("acquisition-only timing is not qualified")
        return self

    @property
    def authoritative_observed_at(self) -> datetime | None:
        if self.qualification is TimingQualification.QUALIFIED:
            return self.observed_at
        return None


class ExpirationTiming(ContractModel):
    schema_id: Literal["tiaf.a6.expiration-timing"] = "tiaf.a6.expiration-timing"
    schema_version: Literal["1.0"] = "1.0"
    expiry_date: date
    expiration_at: TiafDateTime | None = None
    qualification: ExpirationQualification
    qualification_source_ref: QualifiedId | None = None
    trading_cutoff_at: TiafDateTime | None = None
    trading_cutoff_source_ref: QualifiedId | None = None

    @model_validator(mode="after")
    def qualified_expiration(self) -> Self:
        if self.qualification is ExpirationQualification.QUALIFIED_INSTANT:
            if self.expiration_at is None or self.qualification_source_ref is None:
                raise ValueError("qualified expiry requires an instant and source")
            if self.expiration_at.date() != self.expiry_date:
                raise ValueError("qualified expiry instant must match expiry date")
        elif self.expiration_at is not None:
            raise ValueError("unqualified/date-only expiry cannot claim an instant")
        if (self.trading_cutoff_at is None) != (self.trading_cutoff_source_ref is None):
            raise ValueError("trading cutoff requires both instant and source")
        if (
            self.trading_cutoff_at is not None
            and self.expiration_at is not None
            and self.trading_cutoff_at > self.expiration_at
        ):
            raise ValueError("trading cutoff cannot follow expiration")
        return self

    @property
    def is_qualified(self) -> bool:
        return self.qualification is ExpirationQualification.QUALIFIED_INSTANT


class OptionContractIdentity(ContractModel):
    schema_id: Literal["tiaf.a6.option-contract-identity"] = "tiaf.a6.option-contract-identity"
    schema_version: Literal["1.0"] = "1.0"
    subject: Symbol
    subject_class: SubjectClass
    exchange: Literal["NSE"] = "NSE"
    segment: Literal["NSE_FNO"] = "NSE_FNO"
    option_type: OptionType
    strike: PositiveDecimal
    expiry_date: date
    expiration: ExpirationTiming
    native_instrument_ref: QualifiedId | None = None
    lot_size: PositiveStrictInt | None = None
    provenance_refs: tuple[QualifiedId, ...]

    @field_validator("provenance_refs", mode="after")
    @classmethod
    def sorted_provenance(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("option identity requires provenance")
        return _sorted_unique(values, "option provenance refs")

    @model_validator(mode="after")
    def expiry_matches(self) -> Self:
        if self.expiry_date != self.expiration.expiry_date:
            raise ValueError("contract and timing expiry dates differ")
        return self

    def identity_fingerprint(self) -> str:
        return semantic_fingerprint(
            {
                "subject": self.subject,
                "subject_class": self.subject_class,
                "exchange": self.exchange,
                "segment": self.segment,
                "option_type": self.option_type,
                "strike": self.strike,
                "expiry_date": self.expiry_date,
                "expiration_at": self.expiration.expiration_at,
            }
        )


class AdmittedGreeks(ContractModel):
    schema_id: Literal["tiaf.a6.admitted-greeks"] = "tiaf.a6.admitted-greeks"
    schema_version: Literal["1.0"] = "1.0"
    delta: FiniteDecimal | None = None
    gamma: FiniteDecimal | None = None
    theta: FiniteDecimal | None = None
    vega: FiniteDecimal | None = None
    unit_semantics: NonEmptyStr
    evidence_refs: tuple[QualifiedId, ...]

    @field_validator("evidence_refs", mode="after")
    @classmethod
    def sorted_evidence(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("admitted Greeks require evidence")
        return _sorted_unique(values, "Greek evidence refs")

    @model_validator(mode="after")
    def has_value(self) -> Self:
        if all(value is None for value in (self.delta, self.gamma, self.theta, self.vega)):
            raise ValueError("admitted Greeks require at least one supplied value")
        return self


class AdmittedImpliedVolatility(ContractModel):
    """Provider-supplied IV with explicit units and attributable evidence."""

    schema_id: Literal["tiaf.a6.admitted-implied-volatility"] = (
        "tiaf.a6.admitted-implied-volatility"
    )
    schema_version: Literal["1.0"] = "1.0"
    value: NonNegativeDecimal
    unit_semantics: NonEmptyStr
    evidence_refs: tuple[QualifiedId, ...]

    @field_validator("evidence_refs", mode="after")
    @classmethod
    def sorted_evidence(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("admitted implied volatility requires evidence")
        return _sorted_unique(values, "implied-volatility evidence refs")


class OptionQuoteEvidence(ContractModel):
    schema_id: Literal["tiaf.a6.option-quote-evidence"] = "tiaf.a6.option-quote-evidence"
    schema_version: Literal["1.0"] = "1.0"
    quote_id: QualifiedId
    contract: OptionContractIdentity
    bid: NonNegativeDecimal | None = None
    ask: NonNegativeDecimal | None = None
    top_bid_quantity: NonNegativeDecimal | None = None
    top_ask_quantity: NonNegativeDecimal | None = None
    price_currency: Literal["INR"] = "INR"
    quantity_unit: NonEmptyStr
    timing: MarketTimingQualification
    ltp: NonNegativeDecimal | None = None
    open_interest: NonNegativeStrictInt | None = None
    volume: NonNegativeStrictInt | None = None
    implied_volatility: AdmittedImpliedVolatility | None = None
    greeks: AdmittedGreeks | None = None
    provenance_refs: tuple[QualifiedId, ...]

    @field_validator("provenance_refs", mode="after")
    @classmethod
    def sorted_provenance(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("quote requires provenance")
        return _sorted_unique(values, "quote provenance refs")

    @model_validator(mode="after")
    def valid_book(self) -> Self:
        if self.bid is not None and self.ask is not None and self.ask < self.bid:
            raise ValueError("crossed quote is malformed")
        return self


class CoverageProof(ContractModel):
    schema_id: Literal["tiaf.a6.coverage-proof"] = "tiaf.a6.coverage-proof"
    schema_version: Literal["1.0"] = "1.0"
    state: CoverageState
    scope_ref: QualifiedId
    checked_at: TiafDateTime
    observed_item_count: NonNegativeStrictInt
    expected_item_count: NonNegativeStrictInt | None = None
    scope_complete: bool = False
    qualification_source_ref: QualifiedId | None = None
    evidence_refs: tuple[QualifiedId, ...] = ()

    @field_validator("evidence_refs", mode="after")
    @classmethod
    def sorted_evidence(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return _sorted_unique(values, "coverage evidence refs")

    @model_validator(mode="after")
    def truthful_coverage(self) -> Self:
        if self.expected_item_count is not None:
            if self.observed_item_count > self.expected_item_count:
                raise ValueError("observed coverage cannot exceed expected coverage")
            if self.scope_complete and self.observed_item_count != self.expected_item_count:
                raise ValueError("complete scope count must equal expected count")
        qualified = self.qualification_source_ref is not None and bool(self.evidence_refs)
        if self.state is CoverageState.PRESENT:
            if (
                self.observed_item_count == 0
                or not self.scope_complete
                or self.expected_item_count is None
                or not qualified
            ):
                raise ValueError("PRESENT requires complete observed scope and qualified proof")
        elif self.state is CoverageState.CONFIRMED_EMPTY:
            if (
                self.observed_item_count != 0
                or not self.scope_complete
                or self.expected_item_count is None
                or not qualified
            ):
                raise ValueError("CONFIRMED_EMPTY requires complete, qualified empty proof")
        elif self.state is CoverageState.PARTIAL:
            if self.scope_complete:
                raise ValueError("PARTIAL coverage cannot claim complete scope")
        elif self.scope_complete:
            raise ValueError("unknown/unavailable coverage cannot claim complete scope")
        return self


class ExpiryChainEvidence(ContractModel):
    schema_id: Literal["tiaf.a6.expiry-chain-evidence"] = "tiaf.a6.expiry-chain-evidence"
    schema_version: Literal["1.0"] = "1.0"
    chain_id: QualifiedId
    subject: Symbol
    subject_class: SubjectClass
    expiration: ExpirationTiming
    underlying_price: PositiveDecimal
    underlying_timing: MarketTimingQualification
    quotes: tuple[OptionQuoteEvidence, ...] = Field(max_length=512)
    coverage: CoverageProof
    provenance_refs: tuple[QualifiedId, ...]

    @field_validator("quotes", mode="after")
    @classmethod
    def canonical_quotes(
        cls, values: tuple[OptionQuoteEvidence, ...]
    ) -> tuple[OptionQuoteEvidence, ...]:
        ids = [item.quote_id for item in values]
        if len(ids) != len(set(ids)):
            raise ValueError("quote IDs must be unique within a chain")
        return tuple(
            sorted(
                values,
                key=lambda item: (
                    item.contract.strike,
                    item.contract.option_type.value,
                    item.quote_id,
                ),
            )
        )

    @field_validator("provenance_refs", mode="after")
    @classmethod
    def sorted_provenance(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("chain requires provenance")
        return _sorted_unique(values, "chain provenance refs")

    @model_validator(mode="after")
    def consistent_chain(self) -> Self:
        if self.coverage.observed_item_count != len(self.quotes):
            raise ValueError("coverage count must match captured quotes")
        if self.coverage.state is CoverageState.PRESENT and not self.quotes:
            raise ValueError("PRESENT chain coverage requires quotes")
        if self.coverage.state is CoverageState.CONFIRMED_EMPTY and self.quotes:
            raise ValueError("CONFIRMED_EMPTY chain cannot contain quotes")
        for quote in self.quotes:
            contract = quote.contract
            if (
                contract.subject != self.subject
                or contract.subject_class is not self.subject_class
                or contract.expiry_date != self.expiration.expiry_date
                or contract.expiration != self.expiration
            ):
                raise ValueError("quote contract does not belong to its chain")
        identities = [quote.contract.identity_fingerprint() for quote in self.quotes]
        if len(identities) != len(set(identities)):
            raise ValueError("option contract identities must be unique within a chain")
        return self


class DerivativesEvidenceCapture(ContractModel):
    schema_id: Literal["tiaf.a6.derivatives-evidence-capture"] = (
        "tiaf.a6.derivatives-evidence-capture"
    )
    schema_version: Literal["1.0"] = "1.0"
    capture_id: QualifiedId
    subject: Symbol
    subject_class: SubjectClass
    captured_as_of: TiafDateTime
    chains: tuple[ExpiryChainEvidence, ...] = Field(max_length=3)
    coverage: CoverageProof
    provenance_refs: tuple[QualifiedId, ...]

    @field_validator("chains", mode="after")
    @classmethod
    def canonical_chains(
        cls, values: tuple[ExpiryChainEvidence, ...]
    ) -> tuple[ExpiryChainEvidence, ...]:
        dates = [item.expiration.expiry_date for item in values]
        if len(dates) != len(set(dates)):
            raise ValueError("expiry dates must be unique within a capture")
        return tuple(sorted(values, key=lambda item: item.expiration.expiry_date))

    @field_validator("provenance_refs", mode="after")
    @classmethod
    def sorted_provenance(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("derivatives capture requires provenance")
        return _sorted_unique(values, "capture provenance refs")

    @model_validator(mode="after")
    def consistent_capture(self) -> Self:
        if self.coverage.observed_item_count != len(self.chains):
            raise ValueError("capture coverage count must match expiry chains")
        if self.coverage.state is CoverageState.PRESENT and not self.chains:
            raise ValueError("PRESENT capture requires at least one chain")
        if self.coverage.state is CoverageState.CONFIRMED_EMPTY and self.chains:
            raise ValueError("CONFIRMED_EMPTY capture cannot contain chains")
        if any(
            chain.subject != self.subject or chain.subject_class is not self.subject_class
            for chain in self.chains
        ):
            raise ValueError("chain subject does not match capture")
        return self

    def fingerprint(self) -> str:
        return semantic_fingerprint(self)


class UpstreamA4Evidence(ContractModel):
    schema_id: Literal["tiaf.a6.upstream-a4-evidence"] = "tiaf.a6.upstream-a4-evidence"
    schema_version: Literal["1.0"] = "1.0"
    a4_result_ref: QualifiedId
    a4_result_fingerprint: Sha256
    evidence_as_of: TiafDateTime
    acquired_at: TiafDateTime
    qualification_source_ref: QualifiedId

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.acquired_at < self.evidence_as_of:
            raise ValueError("A4 acquisition cannot predate evidence as-of")
        return self


class SessionWindow(ContractModel):
    schema_id: Literal["tiaf.a6.session-window"] = "tiaf.a6.session-window"
    schema_version: Literal["1.0"] = "1.0"
    opens_at: TiafDateTime
    closes_at: TiafDateTime
    qualification_source_ref: QualifiedId

    @model_validator(mode="after")
    def valid_window(self) -> Self:
        if self.closes_at <= self.opens_at:
            raise ValueError("session close must follow session open")
        return self


class AdmittedEvent(ContractModel):
    schema_id: Literal["tiaf.a6.admitted-event"] = "tiaf.a6.admitted-event"
    schema_version: Literal["1.0"] = "1.0"
    event_id: QualifiedId
    subject: Symbol
    event_at: TiafDateTime | None = None
    acquired_at: TiafDateTime
    timing_qualification: TimingQualification
    materiality: EventMateriality
    relevance: EventRelevance
    provenance_refs: tuple[QualifiedId, ...]

    @field_validator("provenance_refs", mode="after")
    @classmethod
    def sorted_provenance(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("event requires provenance")
        return _sorted_unique(values, "event provenance refs")

    @model_validator(mode="after")
    def timing(self) -> Self:
        if self.timing_qualification is TimingQualification.QUALIFIED:
            if self.event_at is None:
                raise ValueError("qualified event requires event time")
        return self


class EventEvidenceWindow(ContractModel):
    schema_id: Literal["tiaf.a6.event-evidence-window"] = "tiaf.a6.event-evidence-window"
    schema_version: Literal["1.0"] = "1.0"
    state: EventEvidenceState
    subject: Symbol
    window_start: TiafDateTime
    window_end: TiafDateTime
    coverage: CoverageProof
    events: tuple[AdmittedEvent, ...] = ()
    provenance_refs: tuple[QualifiedId, ...]

    @field_validator("events", mode="after")
    @classmethod
    def canonical_events(cls, values: tuple[AdmittedEvent, ...]) -> tuple[AdmittedEvent, ...]:
        ids = [item.event_id for item in values]
        if len(ids) != len(set(ids)):
            raise ValueError("event IDs must be unique")
        return tuple(sorted(values, key=lambda item: item.event_id))

    @field_validator("provenance_refs", mode="after")
    @classmethod
    def sorted_provenance(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("event window requires provenance")
        return _sorted_unique(values, "event-window provenance refs")

    @model_validator(mode="after")
    def event_semantics(self) -> Self:
        if self.window_end <= self.window_start:
            raise ValueError("event window end must follow start")
        if any(event.subject != self.subject for event in self.events):
            raise ValueError("event subject does not match window")
        if self.coverage.observed_item_count != len(self.events):
            raise ValueError("event coverage count must match events")
        blockers = [
            event
            for event in self.events
            if event.timing_qualification is TimingQualification.QUALIFIED
            and event.materiality is EventMateriality.MATERIAL
            and event.relevance is EventRelevance.RELEVANT
            and event.event_at is not None
            and self.window_start <= event.event_at <= self.window_end
        ]
        if self.state is EventEvidenceState.KNOWN_BLOCKER and not blockers:
            raise ValueError("known blocker requires a qualified intersecting event")
        if self.state is EventEvidenceState.QUALIFIED_NO_INTERSECTING_EVENT:
            if self.coverage.state is not CoverageState.CONFIRMED_EMPTY or self.events:
                raise ValueError("no-event proof requires confirmed-empty qualified coverage")
        if (
            self.state is EventEvidenceState.UNKNOWN
            and self.coverage.state is CoverageState.CONFIRMED_EMPTY
        ):
            raise ValueError("confirmed-empty qualified coverage cannot remain unknown")
        return self


class ExpressionEvidenceBundle(ContractModel):
    schema_id: Literal["tiaf.a6.expression-evidence-bundle"] = "tiaf.a6.expression-evidence-bundle"
    schema_version: Literal["1.0"] = "1.0"
    bundle_id: QualifiedId
    subject: Symbol
    subject_class: SubjectClass
    evaluation_cutoff: TiafDateTime
    upstream_a4: UpstreamA4Evidence
    derivatives: DerivativesEvidenceCapture
    session: SessionWindow | None = None
    event_evidence: EventEvidenceWindow | None = None
    provenance_refs: tuple[QualifiedId, ...]

    @field_validator("provenance_refs", mode="after")
    @classmethod
    def sorted_provenance(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("evidence bundle requires provenance")
        return _sorted_unique(values, "bundle provenance refs")

    @model_validator(mode="after")
    def consistent_bundle(self) -> Self:
        if (
            self.derivatives.subject != self.subject
            or self.derivatives.subject_class is not self.subject_class
        ):
            raise ValueError("derivatives evidence subject does not match bundle")
        if self.derivatives.captured_as_of > self.evaluation_cutoff:
            raise ValueError("derivatives capture cannot follow evaluation cutoff")
        if self.upstream_a4.evidence_as_of > self.evaluation_cutoff:
            raise ValueError("upstream evidence cannot follow evaluation cutoff")
        if self.upstream_a4.acquired_at > self.evaluation_cutoff:
            raise ValueError("upstream evidence was not acquired by evaluation cutoff")
        if self.event_evidence is not None and self.event_evidence.subject != self.subject:
            raise ValueError("event evidence subject does not match bundle")
        coverage_times = [
            self.derivatives.coverage.checked_at,
            *(chain.coverage.checked_at for chain in self.derivatives.chains),
        ]
        if self.event_evidence is not None:
            coverage_times.append(self.event_evidence.coverage.checked_at)
        if any(checked_at > self.evaluation_cutoff for checked_at in coverage_times):
            raise ValueError("coverage proof cannot postdate evaluation cutoff")
        market_acquisition_times = [
            *(chain.underlying_timing.acquired_at for chain in self.derivatives.chains),
            *(
                quote.timing.acquired_at
                for chain in self.derivatives.chains
                for quote in chain.quotes
            ),
        ]
        if self.event_evidence is not None:
            market_acquisition_times.extend(
                event.acquired_at for event in self.event_evidence.events
            )
        if any(acquired_at > self.evaluation_cutoff for acquired_at in market_acquisition_times):
            raise ValueError("evidence was not acquired by evaluation cutoff")
        return self

    def fingerprint(self) -> str:
        return semantic_fingerprint(self)


class HorizonAgeLimit(ContractModel):
    horizon_class: ExpressionHorizonClass
    max_age_seconds: PositiveStrictInt


class HorizonDurationLimit(ContractModel):
    horizon_class: ExpressionHorizonClass
    maximum_seconds: PositiveStrictInt | None = None


class ResidualLifeRule(ContractModel):
    horizon_class: ExpressionHorizonClass
    minimum_seconds: PositiveStrictInt
    maximum_seconds: PositiveStrictInt | None = None

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.maximum_seconds is not None and self.maximum_seconds < self.minimum_seconds:
            raise ValueError("maximum residual life cannot be below minimum")
        return self


class SpreadTierPolicy(ContractModel):
    tier: Literal[SpreadQualityTier.TIER_0, SpreadQualityTier.TIER_1]
    lower_bound_exclusive_bps: NonNegativeDecimal | None = None
    upper_bound_inclusive_bps: PositiveDecimal

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if (
            self.lower_bound_exclusive_bps is not None
            and self.lower_bound_exclusive_bps >= self.upper_bound_inclusive_bps
        ):
            raise ValueError("spread tier bounds are reversed")
        return self


class TradeExpressionPolicy(ContractModel):
    schema_id: Literal["tiaf.a6.trade-expression-policy"] = "tiaf.a6.trade-expression-policy"
    schema_version: Literal["1.0"] = "1.0"
    policy_id: QualifiedId
    policy_version: NonEmptyStr
    profile_id: QualifiedId
    evaluator_id: QualifiedId
    evaluator_version: NonEmptyStr
    normalizer_id: QualifiedId
    normalizer_version: NonEmptyStr
    supported_subject_classes: tuple[SubjectClass, ...]
    allowed_horizons: tuple[ExpressionHorizonClass, ...]
    max_candidate_expiries: Literal[3] = 3
    max_strikes_per_chain: Literal[512] = 512
    max_evaluated_candidates: Literal[9] = 9
    strike_neighborhood: tuple[MoneynessLabel, ...]
    quote_max_age_seconds: Literal[60] = 60
    spot_max_age_seconds: Literal[60] = 60
    upstream_age_limits: tuple[HorizonAgeLimit, ...]
    horizon_duration_limits: tuple[HorizonDurationLimit, ...]
    require_observation_time: Literal[True] = True
    require_qualified_expiration: Literal[True] = True
    hard_spread_limit_bps: PositiveDecimal
    spread_tiers: tuple[SpreadTierPolicy, ...]
    minimum_top_quantity_exclusive: NonNegativeDecimal
    residual_life_rules: tuple[ResidualLifeRule, ...]
    premium_cap_is_hard_gate: Literal[True] = True
    known_event_blocks: Literal[True] = True
    allowed_preferences: tuple[Literal["MONEYNESS_ORDER", "PREMIUM_CAP", "EVENT_CLEAR"], ...]
    max_alternatives: Literal[2] = 2
    require_qualified_coverage: Literal[True] = True
    max_provider_calls: Literal[0] = 0
    max_model_calls: Literal[0] = 0
    rule_order: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def complete_policy(self) -> Self:
        for values, label in (
            (self.supported_subject_classes, "supported subject classes"),
            (self.allowed_horizons, "allowed horizons"),
            (self.strike_neighborhood, "strike neighborhood"),
            (self.allowed_preferences, "allowed preferences"),
            (self.rule_order, "policy rules"),
        ):
            if not values or len(values) != len(set(values)):
                raise ValueError(f"{label} must be non-empty and unique")
        if {item.horizon_class for item in self.upstream_age_limits} != set(self.allowed_horizons):
            raise ValueError("upstream age limits must cover allowed horizons")
        if {item.horizon_class for item in self.residual_life_rules} != set(self.allowed_horizons):
            raise ValueError("residual-life rules must cover allowed horizons")
        if {item.horizon_class for item in self.horizon_duration_limits} != set(
            self.allowed_horizons
        ):
            raise ValueError("duration limits must cover allowed horizons")
        return self

    def fingerprint(self) -> str:
        return semantic_fingerprint(self)


class SpreadAssessment(ContractModel):
    schema_id: Literal["tiaf.a6.spread-assessment"] = "tiaf.a6.spread-assessment"
    schema_version: Literal["1.0"] = "1.0"
    quote_ref: QualifiedId
    absolute_spread: NonNegativeDecimal | None = None
    midpoint: PositiveDecimal | None = None
    relative_spread_bps: NonNegativeDecimal | None = None
    eligibility: SpreadEligibility
    quality_tier: SpreadQualityTier
    reason_code: NonEmptyStr


class TradeExpressionCandidate(ContractModel):
    schema_id: Literal["tiaf.a6.trade-expression-candidate"] = "tiaf.a6.trade-expression-candidate"
    schema_version: Literal["1.0"] = "1.0"
    candidate_id: QualifiedId
    contract: OptionContractIdentity
    direction: ExpressionDirection
    position_side: Literal["LONG"] = "LONG"
    moneyness: MoneynessLabel

    @model_validator(mode="after")
    def correct_side(self) -> Self:
        required = OptionType.CE if self.direction is ExpressionDirection.BULLISH else OptionType.PE
        if self.contract.option_type is not required:
            raise ValueError("candidate option side conflicts with admitted direction")
        return self


class CandidateGateAssessment(ContractModel):
    schema_id: Literal["tiaf.a6.candidate-gate-assessment"] = "tiaf.a6.candidate-gate-assessment"
    schema_version: Literal["1.0"] = "1.0"
    gate_id: CandidateGateId
    status: GateStatus
    reason_code: NonEmptyStr
    measured_value: FiniteDecimal | None = None
    measured_unit: NonEmptyStr | None = None
    threshold_value: FiniteDecimal | None = None
    threshold_unit: NonEmptyStr | None = None
    evidence_refs: tuple[QualifiedId, ...] = ()
    policy_ref: QualifiedId

    @field_validator("evidence_refs", mode="after")
    @classmethod
    def sorted_evidence(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return _sorted_unique(values, "candidate-gate evidence refs")

    @model_validator(mode="after")
    def complete_units(self) -> Self:
        if (self.measured_value is None) != (self.measured_unit is None):
            raise ValueError("measured value and unit must be supplied together")
        if (self.threshold_value is None) != (self.threshold_unit is None):
            raise ValueError("threshold value and unit must be supplied together")
        return self


class CandidateRankingFacts(ContractModel):
    schema_id: Literal["tiaf.a6.candidate-ranking-facts"] = "tiaf.a6.candidate-ranking-facts"
    schema_version: Literal["1.0"] = "1.0"
    spread_tier_rank: Literal[0, 1]
    requested_moneyness_rank: Annotated[StrictInt, Field(ge=0, le=2)]
    expiry_cushion_excess_seconds: NonNegativeDecimal
    exact_spread_bps: NonNegativeDecimal
    canonical_contract_key: tuple[NonEmptyStr, NonEmptyStr, NonEmptyStr, NonEmptyStr, NonEmptyStr]


class ExpressionCandidateEvaluation(ContractModel):
    schema_id: Literal["tiaf.a6.expression-candidate-evaluation"] = (
        "tiaf.a6.expression-candidate-evaluation"
    )
    schema_version: Literal["1.0"] = "1.0"
    evaluation_id: QualifiedId
    candidate: TradeExpressionCandidate
    quote_ref: QualifiedId
    evaluated_at: TiafDateTime
    gates: tuple[CandidateGateAssessment, ...]
    spread: SpreadAssessment
    eligibility: CandidateEligibility
    rejection_reason_codes: tuple[NonEmptyStr, ...] = ()
    uncertainty_reason_codes: tuple[NonEmptyStr, ...] = ()
    ranking_facts: CandidateRankingFacts | None = None
    invalidation_conditions: tuple[NonEmptyStr, ...]
    evidence_refs: tuple[QualifiedId, ...]
    policy_fingerprint: Sha256
    semantic_fingerprint: Sha256

    @field_validator("evidence_refs", "invalidation_conditions", mode="after")
    @classmethod
    def sorted_semantic_sets(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("candidate evaluation requires evidence and invalidations")
        return _sorted_unique(values, "candidate evaluation semantic values")

    @model_validator(mode="after")
    def coherent_evaluation(self) -> Self:
        expected_order = tuple(CandidateGateId)
        if tuple(item.gate_id for item in self.gates) != expected_order:
            raise ValueError("candidate gates must use the canonical complete order")
        has_unknown = any(item.status is GateStatus.UNKNOWN for item in self.gates)
        has_failure = any(item.status is GateStatus.FAIL for item in self.gates)
        if self.eligibility is CandidateEligibility.ELIGIBLE:
            if has_unknown or has_failure or self.ranking_facts is None:
                raise ValueError("eligible candidate requires all gates and ranking facts")
            if self.rejection_reason_codes or self.uncertainty_reason_codes:
                raise ValueError("eligible candidate cannot carry rejection or uncertainty")
        elif self.eligibility is CandidateEligibility.UNKNOWN:
            if (
                not has_unknown
                or not self.uncertainty_reason_codes
                or self.ranking_facts is not None
            ):
                raise ValueError("unknown candidate requires unknown gates and no rank")
        elif not has_failure or not self.rejection_reason_codes or self.ranking_facts is not None:
            raise ValueError("ineligible candidate requires a failed gate and no rank")
        return self


class RankDifference(ContractModel):
    schema_id: Literal["tiaf.a6.rank-difference"] = "tiaf.a6.rank-difference"
    schema_version: Literal["1.0"] = "1.0"
    preferred_candidate_ref: QualifiedId
    compared_candidate_ref: QualifiedId
    decisive_dimension: Literal[
        "SPREAD_TIER",
        "MONEYNESS_PREFERENCE",
        "EXPIRY_CUSHION_EXCESS",
        "EXACT_SPREAD_BPS",
        "CANONICAL_CONTRACT_KEY",
    ]
    preferred_value: NonEmptyStr
    compared_value: NonEmptyStr


class ExpressionExplanation(ContractModel):
    schema_id: Literal["tiaf.a6.expression-explanation"] = "tiaf.a6.expression-explanation"
    schema_version: Literal["1.0"] = "1.0"
    disposition_reason_codes: tuple[NonEmptyStr, ...]
    preferred_reason_codes: tuple[NonEmptyStr, ...] = ()
    rank_differences: tuple[RankDifference, ...] = ()

    @field_validator("disposition_reason_codes", mode="after")
    @classmethod
    def nonempty_reasons(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("assessment explanation requires a disposition reason")
        return values


class TradeExpressionAssessment(ContractModel):
    schema_id: Literal["tiaf.a6.trade-expression-assessment"] = (
        "tiaf.a6.trade-expression-assessment"
    )
    schema_version: Literal["1.0"] = "1.0"
    result_id: QualifiedId
    request_id: QualifiedId
    admission_result_id: QualifiedId
    subject: Symbol
    direction: ExpressionDirection | None = None
    horizon: ExpressionHorizon
    evaluation_cutoff: TiafDateTime
    disposition: ExpressionDisposition
    preferred_candidate_ref: QualifiedId | None = None
    alternative_candidate_refs: tuple[QualifiedId, ...] = ()
    candidate_evaluations: tuple[ExpressionCandidateEvaluation, ...] = Field(max_length=9)
    blockers: tuple[NonEmptyStr, ...] = ()
    gaps: tuple[NonEmptyStr, ...] = ()
    explanation: ExpressionExplanation
    invalidation_conditions: tuple[NonEmptyStr, ...]
    request_fingerprint: Sha256
    admission_fingerprint: Sha256
    a4_result_fingerprint: Sha256
    evidence_fingerprint: Sha256
    policy: PolicySelection
    composition_refs: tuple[QualifiedId, ...] = ()
    executable: Literal[False] = False
    provider_calls: Literal[0] = 0
    model_calls: Literal[0] = 0
    input_tokens: Literal[0] = 0
    output_tokens: Literal[0] = 0
    model_cost_units: Literal[0] = 0
    semantic_fingerprint: Sha256

    @field_validator("candidate_evaluations", mode="after")
    @classmethod
    def canonical_evaluations(
        cls, values: tuple[ExpressionCandidateEvaluation, ...]
    ) -> tuple[ExpressionCandidateEvaluation, ...]:
        ids = [item.candidate.candidate_id for item in values]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate evaluations must be unique")
        return tuple(sorted(values, key=lambda item: item.candidate.candidate_id))

    @field_validator(
        "blockers",
        "gaps",
        "invalidation_conditions",
        "composition_refs",
        mode="after",
    )
    @classmethod
    def canonical_sets(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return _sorted_unique(values, "assessment semantic values")

    @field_validator("alternative_candidate_refs", mode="after")
    @classmethod
    def bounded_alternatives(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if len(values) > 2 or len(values) != len(set(values)):
            raise ValueError("alternatives must be unique and bounded to two")
        return values

    @model_validator(mode="after")
    def coherent_selection(self) -> Self:
        by_id = {item.candidate.candidate_id: item for item in self.candidate_evaluations}
        eligible = [
            item
            for item in self.candidate_evaluations
            if item.eligibility is CandidateEligibility.ELIGIBLE
        ]
        if self.disposition is ExpressionDisposition.EXPRESSION_AVAILABLE:
            if self.preferred_candidate_ref is None or self.preferred_candidate_ref not in by_id:
                raise ValueError("available assessment requires a preferred candidate")
            selected = (self.preferred_candidate_ref, *self.alternative_candidate_refs)
            if len(selected) != len(set(selected)) or any(
                by_id[item].eligibility is not CandidateEligibility.ELIGIBLE for item in selected
            ):
                raise ValueError("shortlist must contain unique eligible candidates")
            if len(self.alternative_candidate_refs) != min(2, len(eligible) - 1):
                raise ValueError("available assessment must expose the bounded alternatives")
        elif self.preferred_candidate_ref is not None or self.alternative_candidate_refs:
            raise ValueError("non-available assessment cannot contain a shortlist")
        return self


class AdmissionResult(ContractModel):
    schema_id: Literal["tiaf.a6.admission-result"] = "tiaf.a6.admission-result"
    schema_version: Literal["1.0"] = "1.0"
    result_id: QualifiedId
    request_id: QualifiedId
    outcome: AdmissionOutcome
    resolved_direction: ExpressionDirection | None = None
    reason_codes: tuple[NonEmptyStr, ...]
    request_fingerprint: Sha256
    a4_result_fingerprint: Sha256
    evidence_fingerprint: Sha256
    policy_fingerprint: Sha256
    semantic_fingerprint: Sha256
    provider_calls: Literal[0] = 0
    model_calls: Literal[0] = 0
    input_tokens: Literal[0] = 0
    output_tokens: Literal[0] = 0
    model_cost_units: Literal[0] = 0

    @field_validator("reason_codes", mode="after")
    @classmethod
    def sorted_reasons(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("admission result requires a reason")
        return _sorted_unique(values, "admission reason codes")


def parse_trade_expression_request(value: object) -> TradeExpressionRequest:
    """Translate Pydantic detail into the stable malformed-request taxonomy."""
    try:
        return TradeExpressionRequest.model_validate(value)
    except ValidationError as exc:
        message = str(exc)
        code = (
            A6ErrorCode.UNSUPPORTED_PREFERENCE
            if "preferences" in message
            else A6ErrorCode.INVALID_HORIZON
            if "horizon" in message
            else A6ErrorCode.INVALID_REQUEST_SCHEMA
        )
        raise A6ContractError(code, "invalid A6 trade-expression request") from exc


def parse_option_quote_evidence(value: object) -> OptionQuoteEvidence:
    try:
        return OptionQuoteEvidence.model_validate(value)
    except ValidationError as exc:
        raise A6ContractError(A6ErrorCode.MALFORMED_QUOTE, "malformed A6 option quote") from exc


def parse_coverage_proof(value: object) -> CoverageProof:
    try:
        return CoverageProof.model_validate(value)
    except ValidationError as exc:
        raise A6ContractError(A6ErrorCode.INVALID_COVERAGE, "invalid A6 coverage proof") from exc


def parse_trade_expression_assessment(value: object) -> TradeExpressionAssessment:
    try:
        return TradeExpressionAssessment.model_validate(value)
    except ValidationError as exc:
        raise A6ContractError(
            A6ErrorCode.INVALID_ASSESSMENT,
            "invalid A6 trade-expression assessment",
        ) from exc
