"""Evaluation-owned target, synthetic session/price and population contracts.

No label resolution, metrics, journal, calendar service or persistence lives here.
"""

from typing import Annotated, Literal, Self

from pydantic import (
    Field,
    StrictBool,
    StrictInt,
    field_serializer,
    field_validator,
    model_validator,
)

from tiaf.data.enums import InstrumentType, MarketSegment
from tiaf.data.models import InstrumentKey
from tiaf.forecasting.enums import (
    DataBasis,
    ForecastRealizationMode,
    ForecastReason,
    PopulationDisposition,
    QualificationStatus,
)
from tiaf.forecasting.identity import (
    ArtifactReference,
    ExactPositivePrice,
    ForecastContract,
    ForecastDateTime,
    LogicalId,
    decimal_text,
    semantic_fingerprint,
)


def _reliance(value: InstrumentKey) -> InstrumentKey:
    value = InstrumentKey.model_validate(value.model_dump(mode="python"))
    if (
        value.symbol != "RELIANCE"
        or value.exchange != "NSE"
        or value.segment is not MarketSegment.NSE_EQUITY
        or value.instrument_type is not InstrumentType.EQUITY
        or any(
            x is not None
            for x in (
                value.expiry,
                value.strike,
                value.option_type,
                value.trading_symbol,
                value.provider_instrument_id,
            )
        )
    ):
        raise ValueError("FF-0 supports only provider-neutral RELIANCE NSE cash equity")
    return value


class ForecastTargetSpec(ForecastContract):
    schema_id: Literal["tiaf.ff.target"] = "tiaf.ff.target"
    target_id: Literal["equity.next_session_close.return_gt_zero"] = (
        "equity.next_session_close.return_gt_zero"
    )
    target_version: Literal["1.0"] = "1.0"
    subject: InstrumentKey
    horizon: Literal["NEXT_TRADING_SESSION_CLOSE"] = "NEXT_TRADING_SESSION_CLOSE"
    event: Literal["TERMINAL_CLOSE_GT_REFERENCE_CLOSE"] = "TERMINAL_CLOSE_GT_REFERENCE_CLOSE"
    price_basis: Literal["UNADJUSTED_COMPLETED_CLOSE"] = "UNADJUSTED_COMPLETED_CLOSE"
    price_unit: Literal["INR"] = "INR"
    return_unit: Literal["DIMENSIONLESS_PRICE_RETURN"] = "DIMENSIONLESS_PRICE_RETURN"
    equal_close_policy: Literal["CLASS_ZERO"] = "CLASS_ZERO"
    missing_outcome_policy: Literal["PENDING_THEN_CENSORED_NO_LABEL"] = (
        "PENDING_THEN_CENSORED_NO_LABEL"
    )
    invalid_outcome_policy: Literal["INELIGIBLE_NO_LABEL"] = "INELIGIBLE_NO_LABEL"
    corporate_action_policy: Literal["EXCLUDE_AFFECTED_OR_UNKNOWN"] = "EXCLUDE_AFFECTED_OR_UNKNOWN"
    labeler_ref: ArtifactReference
    qualification_policy_ref: ArtifactReference

    _subject = field_validator("subject")(_reliance)


class EvidenceReference(ForecastContract):
    """Pinned neutral source/version reference; hashes do not prove authenticity."""

    artifact: ArtifactReference
    source_id: LogicalId
    origin_id: LogicalId
    document_version_id: LogicalId
    provider_adapter_id: LogicalId | None = None
    data_basis: DataBasis
    observed_at: ForecastDateTime | None = None
    published_at: ForecastDateTime | None = None
    available_at: ForecastDateTime
    acquired_at: ForecastDateTime
    admitted_at: ForecastDateTime

    @model_validator(mode="after")
    def knowledge_order(self) -> Self:
        if self.published_at is not None and self.published_at > self.available_at:
            raise ValueError("publication cannot follow availability")
        if not self.available_at <= self.acquired_at <= self.admitted_at:
            raise ValueError("availability/acquisition/admission order is invalid")
        if self.observed_at is not None and self.observed_at > self.available_at:
            raise ValueError("observed fact cannot become available before observation")
        return self


class SessionRecord(ForecastContract):
    session_id: LogicalId
    opens_at: ForecastDateTime
    closes_at: ForecastDateTime
    subject_eligible: StrictBool

    @model_validator(mode="after")
    def positive_window(self) -> Self:
        if self.opens_at >= self.closes_at:
            raise ValueError("session close must be after open")
        return self


class QualifiedSessionSchedule(ForecastContract):
    schema_id: Literal["tiaf.ff.session-schedule"] = "tiaf.ff.session-schedule"
    calendar_ref: ArtifactReference
    venue: Literal["NSE"] = "NSE"
    segment: Literal["NSE_EQUITY"] = "NSE_EQUITY"
    timezone: Literal["Asia/Kolkata"] = "Asia/Kolkata"
    coverage_start: ForecastDateTime
    coverage_end: ForecastDateTime
    sessions: tuple[SessionRecord, ...] = Field(min_length=2, max_length=64)
    complete: StrictBool
    qualification: QualificationStatus
    qualification_policy_ref: ArtifactReference
    source: EvidenceReference
    exception_notice_refs: tuple[EvidenceReference, ...] = ()
    revision: Annotated[StrictInt, Field(ge=0)] = 0
    predecessor: ArtifactReference | None = None

    @model_validator(mode="after")
    def validate_schedule(self) -> Self:
        ids = [item.session_id for item in self.sessions]
        if len(ids) != len(set(ids)):
            raise ValueError("session identities must be unique")
        if self.coverage_start > self.sessions[0].opens_at:
            raise ValueError("coverage omits the first session")
        if self.coverage_end < self.sessions[-1].closes_at:
            raise ValueError("coverage omits the last session")
        if any(a.closes_at >= b.opens_at for a, b in zip(self.sessions, self.sessions[1:])):
            raise ValueError("schedule must be strictly ordered and non-overlapping")
        if (self.revision > 0) != (self.predecessor is not None):
            raise ValueError("schedule revisions require an explicit predecessor")
        if self.predecessor is not None and self.predecessor == self.calendar_ref:
            raise ValueError("schedule cannot supersede itself")
        if self.qualification is QualificationStatus.QUALIFIED and not self.complete:
            raise ValueError("qualified schedule must assert complete coverage")
        return self


class QualifiedCloseObservation(ForecastContract):
    schema_id: Literal["tiaf.ff.close-observation"] = "tiaf.ff.close-observation"
    observation_id: LogicalId
    subject: InstrumentKey
    session_id: LogicalId
    observed_at: ForecastDateTime
    value: ExactPositivePrice | None
    price_unit: Literal["INR"] = "INR"
    price_basis: Literal["UNADJUSTED_COMPLETED_CLOSE"] = "UNADJUSTED_COMPLETED_CLOSE"
    source: EvidenceReference
    bar_ref: ArtifactReference
    qualification: QualificationStatus
    final: StrictBool
    precision: Literal["SOURCE_DECIMAL", "UNQUALIFIED"]
    action_coverage: Literal["UNAFFECTED", "AFFECTED", "UNKNOWN"]
    action_coverage_ref: EvidenceReference
    reasons: tuple[ForecastReason, ...] = ()

    _subject = field_validator("subject")(_reliance)

    @field_serializer("value")
    def serialize_price(self, value: ExactPositivePrice | None) -> str | None:
        return None if value is None else decimal_text(value)

    @model_validator(mode="after")
    def qualified_price(self) -> Self:
        if self.source.observed_at != self.observed_at:
            raise ValueError("close and source observation times must agree")
        if self.qualification is QualificationStatus.QUALIFIED:
            if self.value is None or not self.final or self.precision != "SOURCE_DECIMAL":
                raise ValueError("qualified close requires an exact final positive price")
        elif not self.reasons:
            raise ValueError("unqualified close requires reasons")
        return self


class ForecastWindow(ForecastContract):
    schema_id: Literal["tiaf.ff.window"] = "tiaf.ff.window"
    schedule: QualifiedSessionSchedule
    reference: QualifiedCloseObservation
    target_session_id: LogicalId
    target_open_time: ForecastDateTime
    target_resolve_time: ForecastDateTime
    outcome_due_at: ForecastDateTime
    maturation_policy_ref: ArtifactReference

    @model_validator(mode="after")
    def adjacent_session_identity(self) -> Self:
        ids = [session.session_id for session in self.schedule.sessions]
        if self.reference.session_id not in ids or self.target_session_id not in ids:
            raise ValueError("requested sessions must exist in supplied schedule")
        index = ids.index(self.reference.session_id)
        if index + 1 >= len(ids) or ids[index + 1] != self.target_session_id:
            raise ValueError("target must be the supplied adjacent next session")
        source, target = self.schedule.sessions[index : index + 2]
        if self.reference.observed_at != source.closes_at:
            raise ValueError("reference must be the source session completed close")
        if (self.target_open_time, self.target_resolve_time) != (target.opens_at, target.closes_at):
            raise ValueError("target window must match its pinned session")
        if self.outcome_due_at < self.target_resolve_time:
            raise ValueError("outcome deadline cannot precede scheduled resolution")
        return self

    @property
    def fingerprint(self) -> str:
        return semantic_fingerprint(self)


class PopulationObservation(ForecastContract):
    """Immutable mapping contract only; FF-1 owns constructing evaluation reports."""

    observation_id: LogicalId
    request_ids: tuple[LogicalId, ...] = Field(min_length=1)
    source_run_refs: tuple[ArtifactReference, ...]
    journal_revision_refs: tuple[ArtifactReference, ...]
    realization_mode: ForecastRealizationMode

    @model_validator(mode="after")
    def unique_request_mapping(self) -> Self:
        if len(set(self.request_ids)) != len(self.request_ids):
            raise ValueError("duplicate request mapping")
        return self


class MetricDisposition(ForecastContract):
    observation_id: LogicalId
    metric_id: LogicalId
    arm_id: LogicalId
    disposition: PopulationDisposition
    primary_reason: LogicalId
    contributing_reasons: tuple[LogicalId, ...]
    source_facet_refs: tuple[ArtifactReference, ...]
    unevaluated_checks: tuple[LogicalId, ...] = ()

    @model_validator(mode="after")
    def reason_is_retained(self) -> Self:
        if self.primary_reason not in self.contributing_reasons:
            raise ValueError("primary reason must remain among contributing reasons")
        return self


class MetricDispositionCounts(ForecastContract):
    metric_id: LogicalId
    arm_id: LogicalId
    included: Annotated[StrictInt, Field(ge=0)]
    excluded: Annotated[StrictInt, Field(ge=0)]
    not_evaluable: Annotated[StrictInt, Field(ge=0)]


class EvaluationPopulationDispositionReport(ForecastContract):
    """Validate population partitions, without computing metrics or emitting a report."""

    schema_id: Literal["tiaf.a7.population-disposition"] = "tiaf.a7.population-disposition"
    report_id: LogicalId
    manifest_ref: ArtifactReference
    split_ref: ArtifactReference
    target: ForecastTargetSpec
    label_policy_ref: ArtifactReference
    metric_policy_ref: ArtifactReference
    mode_policy_ref: ArtifactReference
    weighting_policy_ref: ArtifactReference
    evaluation_as_of: ForecastDateTime
    observations: tuple[PopulationObservation, ...]
    metric_ids: tuple[LogicalId, ...] = Field(min_length=1)
    arm_ids: tuple[LogicalId, ...] = Field(min_length=1)
    dispositions: tuple[MetricDisposition, ...]
    counts: tuple[MetricDispositionCounts, ...]
    requested_count: Annotated[StrictInt, Field(ge=0)]
    unique_observation_count: Annotated[StrictInt, Field(ge=0)]
    unmapped_request_ids: tuple[LogicalId, ...] = ()
    forecast_available_observation_ids: tuple[LogicalId, ...] = ()
    label_mature_observation_ids: tuple[LogicalId, ...] = ()
    unresolved_refs: tuple[LogicalId, ...] = ()
    population_complete: StrictBool

    @model_validator(mode="after")
    def exact_partition(self) -> Self:
        ids = [o.observation_id for o in self.observations]
        request_keys = [r for o in self.observations for r in o.request_ids]
        request_keys.extend(self.unmapped_request_ids)
        for values in (ids, request_keys, list(self.metric_ids), list(self.arm_ids)):
            if len(values) != len(set(values)):
                raise ValueError("population identities must not duplicate")
        if self.unique_observation_count != len(ids) or self.requested_count != len(request_keys):
            raise ValueError("population counting units disagree with captured mapping")
        expected = {(o, m, a) for o in ids for m in self.metric_ids for a in self.arm_ids}
        actual = [(d.observation_id, d.metric_id, d.arm_id) for d in self.dispositions]
        if len(actual) != len(set(actual)) or set(actual) != expected:
            raise ValueError("exactly one disposition is required per observation/metric/arm")
        count_keys = [(count.metric_id, count.arm_id) for count in self.counts]
        if len(count_keys) != len(set(count_keys)) or set(count_keys) != {
            (metric, arm) for metric in self.metric_ids for arm in self.arm_ids
        }:
            raise ValueError("counts must cover exactly the declared metric/arm pairs")
        for count in self.counts:
            rows = [
                d
                for d in self.dispositions
                if (d.metric_id, d.arm_id)
                == (
                    count.metric_id,
                    count.arm_id,
                )
            ]
            expected_counts = tuple(
                sum(d.disposition is status for d in rows)
                for status in (
                    PopulationDisposition.INCLUDED,
                    PopulationDisposition.EXCLUDED,
                    PopulationDisposition.NOT_EVALUABLE,
                )
            )
            if (count.included, count.excluded, count.not_evaluable) != expected_counts:
                raise ValueError("metric counts disagree with disposition counting units")
        for facets in (
            self.forecast_available_observation_ids,
            self.label_mature_observation_ids,
        ):
            if len(facets) != len(set(facets)) or not set(facets) <= set(ids):
                raise ValueError("facet counts must reference unique population observations")
        if self.population_complete and (self.unresolved_refs or self.unmapped_request_ids):
            raise ValueError("unresolved population cannot claim completeness")
        return self
