"""Pure offline FF-1 qualification and A2 projection; no training or labeler."""

import math
from collections import defaultdict
from datetime import datetime, timedelta

from pydantic import TypeAdapter

from tiaf.context import AnalysisContext, AnalysisSubject, EvidenceDescriptor
from tiaf.context.enums import AnalysisPurpose, EvidenceRequirement, EvidenceStatus
from tiaf.context.requirements import AnalysisContextRequirement
from tiaf.contracts import DataQuality, FreshnessState
from tiaf.data.models import HistoricalSeries, OHLCVBar
from tiaf.evaluation.forecast_contracts import (
    EvidenceReference,
    ForecastWindow,
    QualifiedCloseObservation,
    QualifiedSessionSchedule,
    SessionRecord,
)
from tiaf.evaluation.forecast_research_contracts import (
    CorporateActionQualification,
    DailyBarInput,
    DailyBarQualification,
    EmpiricalDataset,
    EmpiricalDatasetQualification,
    ObservationEligibility,
    ReasonCount,
    qualification_verdicts,
)
from tiaf.evaluation.forecast_research_contracts import (
    QualificationReason as R,
)
from tiaf.evaluation.forecast_research_contracts import (
    QualificationState as Q,
)
from tiaf.forecasting.enums import DataBasis, QualificationStatus
from tiaf.forecasting.identity import ArtifactReference, ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.research_contracts import FeatureVector, FF1FeatureSchema
from tiaf.forecasting.research_features import derive_features


def _ordered(reasons: list[R] | tuple[R, ...]) -> tuple[R, ...]:
    return tuple(reason for reason in R if reason in reasons)


def _known(source: EvidenceReference | None, cutoff: datetime, basis: DataBasis) -> bool:
    return source is not None and source.data_basis is basis and source.admitted_at <= cutoff


def _rights_ok(dataset: EmpiricalDataset, at: datetime) -> bool:
    rights = dataset.rights
    return (
        all(
            state is Q.QUALIFIED
            for state in (
                rights.local_research,
                rights.model_training,
                rights.derived_feature_storage,
                rights.evaluation_artifact_retention,
                rights.replay_evidence_retention,
            )
        )
        and bool(rights.basis_refs)
        and rights.source_artifact == dataset.source.capture
        and rights.reference == dataset.source.rights_ref
        and rights.subject == dataset.target.subject
        and rights.coverage_start <= dataset.coverage_start
        and rights.coverage_end >= dataset.coverage_end
        and rights.assessed_at <= at
        and (rights.valid_until is None or at <= rights.valid_until)
    )


def _security_ok(dataset: EmpiricalDataset) -> bool:
    identity = dataset.security
    resolved = identity.resolution.resolved
    return (
        identity.state is Q.QUALIFIED
        and resolved is not None
        and not identity.resolution.ambiguous
        and not identity.resolution.not_found
        and resolved.instrument == dataset.target.subject
        and resolved.quality is DataQuality.GOOD
        and identity.resolution.query.symbol == dataset.target.subject.symbol
        and identity.resolution.source_provider == resolved.provider_name
        and identity.valid_from <= dataset.coverage_start
        and identity.valid_through >= dataset.coverage_end
        and identity.evidence is not None
    )


def _calendar(
    dataset: EmpiricalDataset,
) -> tuple[tuple[SessionRecord, ...], dict[str, QualifiedSessionSchedule], bool]:
    schedules = dataset.calendar.schedules
    sessions = tuple(s for schedule in schedules for s in schedule.sessions)
    owners = {s.session_id: schedule for schedule in schedules for s in schedule.sessions}
    valid = (
        dataset.calendar.state is Q.QUALIFIED
        and bool(dataset.calendar.authority_refs)
        and len(sessions) <= 8192
        and len(owners) == len(sessions)
        and len({s.opens_at.date() for s in sessions}) == len(sessions)
        and all(s.complete and s.qualification is QualificationStatus.QUALIFIED for s in schedules)
        and all(a.closes_at < b.opens_at for a, b in zip(sessions, sessions[1:]))
        and all(b.coverage_start <= a.coverage_end for a, b in zip(schedules, schedules[1:]))
        and schedules[0].coverage_start.date() <= dataset.coverage_start
        and schedules[-1].coverage_end.date() >= dataset.coverage_end
    )
    return sessions, owners, valid


def _action(
    dataset: EmpiricalDataset,
    session: SessionRecord,
    cutoff: datetime,
) -> tuple[CorporateActionQualification | None, tuple[R, ...]]:
    matches = tuple(
        a
        for a in dataset.actions
        if a.subject == dataset.target.subject
        and a.from_session <= session.opens_at.date() <= a.through_session
    )
    if len(matches) != 1:
        return None, (R.CORPORATE_ACTION_UNRESOLVED,)
    action = matches[0]
    reasons: list[R] = []
    if action.basis != "UNADJUSTED":
        reasons.append(R.PRICE_BASIS_UNSUPPORTED)
    if action.state is not Q.QUALIFIED or not action.complete or action.coverage == "UNKNOWN":
        reasons.append(R.CORPORATE_ACTION_UNRESOLVED)
    if action.coverage == "AFFECTED":
        reasons.append(R.CORPORATE_ACTION_AFFECTED)
    if not _known(action.evidence, cutoff, dataset.source.data_basis):
        reasons.append(R.PROVENANCE_UNQUALIFIED)
    return action, _ordered(reasons)


def _bar_reasons(
    dataset: EmpiricalDataset,
    row: DailyBarInput,
    session: SessionRecord | None,
) -> tuple[R, ...]:
    reasons: list[R] = []
    if session is None or row.session_date != session.opens_at.date():
        reasons.append(R.INVALID_SESSION)
    resolved = dataset.security.resolution.resolved
    if (
        row.instrument != dataset.target.subject
        or resolved is None
        or row.provider_security_id != resolved.provider_instrument_id
    ):
        reasons.append(R.SECURITY_IDENTITY)
    prices = (row.open, row.high, row.low, row.close)
    if not row.final or any(
        p is None or p <= 0 or not math.isfinite(float(p)) or float(p) <= 0 for p in prices
    ):
        reasons.append(R.INVALID_BAR)
    else:
        assert row.low is not None and row.high is not None
        assert row.open is not None and row.close is not None
        if not row.low <= min(row.open, row.close) <= max(row.open, row.close) <= row.high:
            reasons.append(R.INVALID_BAR)
    if row.volume is None:
        reasons.append(R.MISSING_VOLUME)
    elif row.volume < 0 or row.volume > 2**63 - 1:
        reasons.append(R.INVALID_VOLUME)
    source = row.provenance
    if (
        source is None
        or session is None
        or source.observed_at != session.closes_at
        or source.data_basis is not dataset.source.data_basis
        or source.source_id != dataset.source.source_id
        or source.origin_id != dataset.source.origin_id
    ):
        reasons.append(R.PROVENANCE_UNQUALIFIED)
    if not dataset.coverage_start <= row.session_date <= dataset.coverage_end:
        reasons.append(R.INVALID_SESSION)
    return _ordered(reasons)


def _window(
    dataset: EmpiricalDataset,
    reference: SessionRecord,
    target: SessionRecord,
    row: DailyBarInput,
    action: CorporateActionQualification,
    owners: dict[str, QualifiedSessionSchedule],
) -> ForecastWindow:
    first, second = owners[reference.session_id], owners[target.session_id]
    notices = first.exception_notice_refs
    if first != second:
        notices = (*notices, *second.exception_notice_refs, second.source)
    schedule = QualifiedSessionSchedule(
        calendar_ref=ArtifactReference(
            artifact_id="calendar:ff1-pair",
            artifact_version="1.0",
            fingerprint=semantic_fingerprint(
                (first.calendar_ref, second.calendar_ref, reference, target)
            ),
        ),
        coverage_start=reference.opens_at,
        coverage_end=target.closes_at,
        sessions=(reference, target),
        complete=True,
        qualification=QualificationStatus.QUALIFIED,
        qualification_policy_ref=first.qualification_policy_ref,
        source=first.source,
        exception_notice_refs=notices,
    )
    assert row.provenance is not None and action.evidence is not None and row.close is not None
    close = QualifiedCloseObservation(
        observation_id=row.row_id,
        subject=dataset.target.subject,
        session_id=reference.session_id,
        observed_at=reference.closes_at,
        value=row.close,
        source=row.provenance,
        bar_ref=row.provenance.artifact,
        qualification=QualificationStatus.QUALIFIED,
        final=True,
        precision="SOURCE_DECIMAL",
        action_coverage="UNAFFECTED",
        action_coverage_ref=action.evidence,
    )
    maturation = next(m for m in dataset.maturation if m.target_session_id == target.session_id)
    return ForecastWindow(
        schedule=schedule,
        reference=close,
        target_session_id=target.session_id,
        target_open_time=target.opens_at,
        target_resolve_time=target.closes_at,
        outcome_due_at=maturation.outcome_due_at,
        maturation_policy_ref=maturation.policy_ref,
    )


def _features(
    dataset: EmpiricalDataset,
    rows: tuple[DailyBarInput, ...],
    sessions: tuple[SessionRecord, ...],
    cutoff: datetime,
    computed_at: datetime,
    fingerprint: str,
) -> FeatureVector:
    resolved = dataset.security.resolution.resolved
    assert resolved is not None
    bars = tuple(
        OHLCVBar.model_validate(
            {
                "instrument": row.instrument,
                "interval": "1d",
                "start_at": session.opens_at,
                "end_at": session.closes_at,
                "open": row.open,
                "high": row.high,
                "low": row.low,
                "close": row.close,
                "volume": row.volume,
                "source_provider": resolved.provider_name,
            }
        )
        for row, session in zip(rows, sessions, strict=True)
    )
    reference_at = sessions[-1].closes_at
    history = HistoricalSeries(
        instrument=dataset.target.subject,
        interval="1d",
        bars=bars,
        source_provider=resolved.provider_name,
        observed_at=reference_at,
        freshness=FreshnessState.FRESH,
        quality=DataQuality.GOOD,
    )
    context = AnalysisContext(
        context_id="ff1-features:" + fingerprint,
        subject=AnalysisSubject(
            symbol="RELIANCE",
            resolved_instrument=resolved,
            requested_at=cutoff,
            source_system="ff1-offline",
        ),
        requirements=AnalysisContextRequirement(
            purpose=AnalysisPurpose.RESEARCH,
            include_quote=False,
            require_quote=False,
            history_interval="1d",
            history_lookback_days=60,
        ),
        history=history,
        evidence=(
            EvidenceDescriptor(
                evidence_name="history",
                requested=True,
                required=True,
                requirement_role=EvidenceRequirement.REQUIRED,
                status=EvidenceStatus.AVAILABLE,
                quality=DataQuality.GOOD,
                source_observed_at=reference_at,
                source_observation_semantics="QUALIFIED_COMPLETED_SESSION_CAPTURE",
            ),
        ),
        created_at=computed_at,
        overall_quality=DataQuality.GOOD,
        overall_retrieval_freshness=FreshnessState.FRESH,
        complete=True,
    )
    return derive_features(
        context,
        reference_close_at=reference_at,
        information_cutoff=cutoff,
        input_fingerprint=fingerprint,
    )


def qualify_dataset(
    dataset: EmpiricalDataset, *, assessed_at: datetime
) -> EmpiricalDatasetQualification:
    """Qualify supplied assertions, not authenticate them or authorize fitting."""
    dataset = EmpiricalDataset.model_validate(dataset.model_dump(mode="python"))
    assessed_at = TypeAdapter(ForecastDateTime).validate_python(assessed_at)
    schema = FF1FeatureSchema()
    sessions, owners, calendar_ok = _calendar(dataset)
    by_session = {s.session_id: s for s in sessions}
    positions = {s.session_id: i for i, s in enumerate(sessions)}
    rows: dict[str, list[DailyBarInput]] = defaultdict(list)
    bar_results: list[DailyBarQualification] = []
    global_reasons: list[R] = []
    if not _rights_ok(dataset, assessed_at):
        global_reasons.append(R.RIGHTS_UNQUALIFIED)
    if not _security_ok(dataset):
        global_reasons.append(R.SECURITY_IDENTITY)
    if not calendar_ok:
        global_reasons.append(R.CALENDAR_UNQUALIFIED)
    if (
        dataset.source.provenance_ref is None
        or dataset.source.acquisition_at is None
        or dataset.source.acquisition_at > assessed_at
    ):
        global_reasons.append(R.PROVENANCE_UNQUALIFIED)
    row_dates = tuple(row.session_date for row in dataset.rows)
    if row_dates != tuple(sorted(row_dates)):
        global_reasons.append(R.NON_CHRONOLOGICAL)
    for row in dataset.rows:
        rows[row.session_id].append(row)
    row_issues: dict[str, tuple[R, ...]] = {}
    for row in dataset.rows:
        reasons = list(_bar_reasons(dataset, row, by_session.get(row.session_id)))
        if row.provenance is not None and row.provenance.admitted_at > assessed_at:
            reasons.append(R.KNOWLEDGE_CUTOFF_VIOLATION)
        duplicates = rows[row.session_id]
        if len(duplicates) > 1:
            # Identical values are deduplicated for features; preserve every row record.
            bodies = {semantic_fingerprint(r.model_dump(exclude={"row_id"})) for r in duplicates}
            reasons.append(R.DUPLICATE_SESSION if len(bodies) == 1 else R.CONFLICTING_DUPLICATE)
        row_issues[row.row_id] = _ordered(reasons)
        bar_results.append(
            DailyBarQualification(
                row_id=row.row_id, session_id=row.session_id, reasons=_ordered(reasons)
            )
        )

    observations: list[ObservationEligibility] = []
    all_reasons = list(global_reasons)
    all_reasons.extend(
        r for bar in bar_results for r in bar.reasons if r is not R.DUPLICATE_SESSION
    )
    for session_id in dataset.reference_session_ids:
        reasons = list(global_reasons)
        index = positions.get(session_id)
        reference = by_session.get(session_id)
        cutoff = None if reference is None else reference.closes_at + timedelta(minutes=30)
        as_of = None if cutoff is None else cutoff + timedelta(minutes=5)
        window = None
        feature_vector = None
        target = None if index is None or index + 1 == len(sessions) else sessions[index + 1]
        if reference is None:
            reasons.append(R.INVALID_SESSION)
        elif not dataset.coverage_start <= reference.opens_at.date() <= dataset.coverage_end:
            reasons.append(R.INVALID_SESSION)
        if target is None:
            reasons.append(R.TARGET_UNAVAILABLE)
        if index is not None and index < 20:
            reasons.append(R.INSUFFICIENT_LOOKBACK)
        if as_of is not None and (as_of > assessed_at or (target and as_of >= target.opens_at)):
            reasons.append(R.KNOWLEDGE_CUTOFF_VIOLATION)
        selected = () if index is None else sessions[max(0, index - 20) : index + 1]
        inputs: list[DailyBarInput] = []
        actions: list[CorporateActionQualification] = []
        if cutoff is not None:
            if not _known(dataset.security.evidence, cutoff, dataset.source.data_basis):
                reasons.append(R.PROVENANCE_UNQUALIFIED)
            resolution = dataset.security.resolution
            if resolution.observed_at > cutoff or (
                resolution.resolved is not None and resolution.resolved.source_observed_at > cutoff
            ):
                reasons.append(R.KNOWLEDGE_CUTOFF_VIOLATION)
            maturation = next(
                (
                    m
                    for m in dataset.maturation
                    if target and m.target_session_id == target.session_id
                ),
                None,
            )
            if target and (
                maturation is None
                or maturation.outcome_due_at < target.closes_at
                or not _known(maturation.evidence, cutoff, dataset.source.data_basis)
            ):
                reasons.append(R.MATURATION_UNQUALIFIED)
            for session in (*selected, *((target,) if target else ())):
                owner = owners[session.session_id]
                if not session.subject_eligible:
                    reasons.append(R.SECURITY_IDENTITY)
                if not all(
                    _known(e, cutoff, dataset.source.data_basis)
                    for e in (owner.source, *owner.exception_notice_refs)
                ):
                    reasons.append(R.PROVENANCE_UNQUALIFIED)
                action, issues = _action(dataset, session, cutoff)
                # Target action coverage is a qualification fact, not target market data.
                reasons.extend(issues)
                if session is target:
                    continue
                if action is not None:
                    actions.append(action)
                matches = rows.get(session.session_id, [])
                if not matches:
                    reasons.append(R.MISSING_SESSION)
                    continue
                row = matches[0]
                inputs.append(row)
                reasons.extend(r for r in row_issues[row.row_id] if r is not R.DUPLICATE_SESSION)
                if not _known(row.provenance, cutoff, dataset.source.data_basis):
                    reasons.append(R.KNOWLEDGE_CUTOFF_VIOLATION)
            if inputs and len(inputs) == 21 and all(r.volume == 0 for r in inputs[:-1]):
                reasons.append(R.ZERO_VOLUME_BASELINE)
        input_rows = tuple(inputs)
        input_fingerprint = semantic_fingerprint(
            {
                "rows": input_rows,
                "sessions": selected,
                "actions": tuple(actions),
                "calendar_qualification": tuple(
                    {
                        "calendar_ref": owners[s.session_id].calendar_ref,
                        "policy_ref": owners[s.session_id].qualification_policy_ref,
                        "source": owners[s.session_id].source,
                        "notices": owners[s.session_id].exception_notice_refs,
                    }
                    for s in selected
                ),
                "security": dataset.security,
                "schema": schema,
                "source": dataset.source,
                "rights": dataset.rights.reference,
            }
        )
        if not reasons:
            assert reference is not None and target is not None and cutoff is not None
            action, _ = _action(dataset, reference, cutoff)
            assert action is not None
            window = _window(dataset, reference, target, input_rows[-1], action, owners)
            try:
                feature_vector = _features(
                    dataset, input_rows, selected, cutoff, assessed_at, input_fingerprint
                )
            except (ValueError, ArithmeticError):
                reasons.append(R.FEATURE_UNAVAILABLE)
        # Same accepted FF observation projection, without a synthetic ForecastRequest.
        observation_id = (
            None
            if window is None
            else "ff-observation:"
            + semantic_fingerprint(
                {
                    "target": dataset.target,
                    "window": window,
                    "information_cutoff": cutoff,
                    "as_of": as_of,
                }
            )
        )
        observations.append(
            ObservationEligibility(
                target=dataset.target,
                slot_id="ff1-slot:" + semantic_fingerprint((dataset.target, session_id)),
                reference_session_id=session_id,
                window=window,
                observation_id=observation_id,
                information_cutoff=cutoff,
                as_of=as_of,
                computed_at=assessed_at,
                feature_schema=schema,
                raw_data_fingerprint=input_fingerprint,
                input_row_ids=tuple(row.row_id for row in input_rows),
                eligible=not reasons,
                reasons=_ordered(reasons),
                features=feature_vector,
            )
        )
        all_reasons.extend(
            r for r in reasons if r not in (R.INSUFFICIENT_LOOKBACK, R.TARGET_UNAVAILABLE)
        )
    if not any(o.eligible for o in observations):
        all_reasons.append(R.NO_ELIGIBLE_OBSERVATIONS)
    reasons_tuple = _ordered(all_reasons)
    counts = tuple(
        ReasonCount(reason=r, count=n)
        for r in R
        if (n := sum(r in o.reasons for o in observations))
    )
    return EmpiricalDatasetQualification(
        dataset_id=dataset.dataset_id,
        dataset_fingerprint=dataset.fingerprint,
        data_basis=dataset.source.data_basis,
        assessed_at=assessed_at,
        feature_schema=schema,
        rights_ref=dataset.rights.reference,
        source_fingerprint=semantic_fingerprint(dataset.source),
        security_fingerprint=semantic_fingerprint(dataset.security),
        calendar_fingerprint=semantic_fingerprint(dataset.calendar),
        actions_fingerprint=semantic_fingerprint(dataset.actions),
        bars=tuple(bar_results),
        observations=tuple(observations),
        reasons=reasons_tuple,
        verdicts=qualification_verdicts(reasons_tuple, dataset.source.data_basis),
        requested_observations=len(observations),
        eligible_observations=sum(o.eligible for o in observations),
        excluded_observations=sum(not o.eligible for o in observations),
        reason_counts=counts,
    )
