"""Offline adjusted FF-1 qualification. No capture backdating, model or fitting.

Evidence qualification flags are reviewed assertions from trusted bootstrap,
not authentication of a provider or automatic legal approval.
"""

import json
import math
from collections import Counter
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Literal

from pydantic import TypeAdapter

from tiaf.context import AnalysisContext, AnalysisSubject, EvidenceDescriptor
from tiaf.context.enums import AnalysisPurpose, EvidenceRequirement, EvidenceStatus
from tiaf.context.requirements import AnalysisContextRequirement
from tiaf.contracts import DataQuality, FreshnessState
from tiaf.data.models import HistoricalSeries, OHLCVBar
from tiaf.evaluation.forecast_research_contracts import (
    ResearchRightsConfig,
    RightsAdmissionResult,
    rights_admission,
)
from tiaf.evaluation.forecast_retrospective_contracts import (
    RetrospectiveDataset,
    RetrospectiveFold,
    RetrospectiveObservation,
    RetrospectiveQualification,
)
from tiaf.evaluation.forecast_truth import endpoint_direction
from tiaf.forecasting.identity import ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.research_contracts import (
    AdjustedFF1FeatureSchema,
    AdjustedResearchProfile,
    FeatureVector,
)
from tiaf.forecasting.research_features import derive_features

Session = tuple[date, datetime, datetime]


def research_direction(
    reference: float,
    terminal: float,
    *,
    reference_basis: str,
    terminal_basis: str,
    profile: AdjustedResearchProfile,
) -> Literal[0, 1]:
    """Qualify normalized endpoints then use the existing Ground Truth arithmetic.

    Equal *normalized* closes remain zero. Non-equal endpoints within the pinned
    two-endpoint perturbation envelope are unavailable, never rounded into ties.
    """
    if reference_basis != profile.price_series_basis or terminal_basis != reference_basis:
        raise ValueError("ENDPOINT_BASIS_MISMATCH")
    if not all(math.isfinite(p) and p > 0 for p in (reference, terminal)):
        raise ValueError("INVALID_DIRECTION_ENDPOINT")
    tolerance = profile.near_tie_ulps * (math.ulp(reference) + math.ulp(terminal))
    if reference != terminal and abs(terminal - reference) <= tolerance:
        raise ValueError("PRECISION_NEAR_TIE")
    return endpoint_direction(Decimal.from_float(reference), Decimal.from_float(terminal))


def _project(
    dataset: RetrospectiveDataset,
    bars: tuple[OHLCVBar, ...],
    schema: AdjustedFF1FeatureSchema,
    fingerprint: str,
    at: datetime,
) -> FeatureVector:
    reference = bars[-1].end_at
    cutoff = reference + timedelta(minutes=30)
    history = HistoricalSeries(
        instrument=dataset.resolved.instrument,
        interval="1d",
        bars=bars,
        source_provider=dataset.resolved.provider_name,
        observed_at=reference,
        freshness=FreshnessState.FRESH,
        quality=DataQuality.GOOD,
        metadata={
            "research_profile": schema.profile.fingerprint,
            "actual_acquisition_at": dataset.acquired_at.isoformat(),
        },
    )
    context = AnalysisContext(
        context_id="ff1-adjusted:" + fingerprint,
        subject=AnalysisSubject(
            symbol="RELIANCE",
            resolved_instrument=dataset.resolved,
            requested_at=cutoff,
            source_system="ff1-offline-adjusted-research",
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
                source_observed_at=reference,
                source_observation_semantics="ADJUSTED_RETROSPECTIVE_AVAILABILITY_ASSUMPTION",
            ),
        ),
        created_at=at,
        overall_quality=DataQuality.GOOD,
        overall_retrieval_freshness=FreshnessState.FRESH,
        complete=True,
    )
    return derive_features(
        context,
        reference_close_at=reference,
        information_cutoff=cutoff,
        input_fingerprint=fingerprint,
        schema=schema,
    )


def _perturb(bars: tuple[OHLCVBar, ...], sign: int, ulps: int) -> tuple[OHLCVBar, ...]:
    result = []
    for index, bar in enumerate(bars):
        close = bar.close
        toward = math.inf if (index % 2 == 0) == (sign == 1) else -math.inf
        for _ in range(ulps):
            close = math.nextafter(close, toward)
        result.append(
            OHLCVBar.model_validate(
                {
                    **bar.model_dump(),
                    "close": close,
                    "high": max(bar.high, close),
                    "low": min(bar.low, close),
                }
            )
        )
    return tuple(result)


def _observations(
    dataset: RetrospectiveDataset,
    schema: AdjustedFF1FeatureSchema,
    sessions: tuple[Session, ...],
    at: datetime,
    context_fp: str,
    blocked: bool,
) -> tuple[RetrospectiveObservation, ...]:
    rows = {row.session_date: row for row in dataset.rows}
    result = []
    for index, (day, _, close) in enumerate(sessions):
        if not dataset.reference_start <= day <= dataset.reference_end:
            continue
        target = sessions[index + 1] if index + 1 < len(sessions) else None
        target_day = None if target is None else target[0]
        cutoff, as_of = close + timedelta(minutes=30), close + timedelta(minutes=35)
        selected = sessions[max(0, index - 20) : index + 1]
        window_dates = tuple(s[0] for s in selected)
        selected_rows = tuple(rows.get(d) for d in window_dates)
        # No target value participates in the feature closure/fingerprint.
        input_fp = semantic_fingerprint((context_fp, day.isoformat(), selected_rows))
        reasons: list[str] = []
        features, drift = None, None
        label: Literal[0, 1] | None = None
        state: Literal["ELIGIBLE", "UNAVAILABLE", "SEALED"] = "UNAVAILABLE"
        if day.year >= 2025:
            reasons.append("HOLDOUT_SEALED")
            state = "SEALED"
        elif blocked:
            reasons.append("GLOBAL_GATE_HOLD")
        else:
            if len(selected) != 21:
                reasons.append("INSUFFICIENT_LOOKBACK")
            if any(row is None or row.bar is None for row in selected_rows):
                reasons.append("MISSING_FEATURE_BAR")
            # A feature vector cannot straddle an unsupported adjustment boundary.
            for action in dataset.actions:
                if (
                    not action.provider_adjustment_supported
                    and window_dates[0] < action.boundary <= day
                ):
                    reasons.append("FEATURE_ACTION_" + action.kind)
            if not reasons:
                bars = tuple(row.bar for row in selected_rows if row is not None and row.bar)
                if any(bar.volume is None or bar.volume > 2**53 for bar in bars):
                    reasons.append("VOLUME_NUMERIC_UNQUALIFIED")
                elif sum(bar.volume or 0 for bar in bars[:-1]) == 0:
                    reasons.append("ZERO_VOLUME_BASELINE")
                else:
                    try:
                        features = _project(dataset, bars, schema, input_fp, at)
                        drift = max(
                            abs(a - b)
                            for sign in (-1, 1)
                            for a, b in zip(
                                features.values,
                                _project(
                                    dataset,
                                    _perturb(bars, sign, schema.profile.near_tie_ulps),
                                    schema,
                                    input_fp,
                                    at,
                                ).values,
                                strict=True,
                            )
                        )
                        if drift > schema.profile.feature_absolute_tolerance:
                            features = None
                            reasons.append("PRECISION_FEATURE_DRIFT")
                    except ValueError:
                        features = None
                        reasons.append("FEATURE_UNAVAILABLE")
            reference_row = rows.get(day)
            terminal_row = rows.get(target_day) if target_day is not None else None
            if target_day is not None and target_day.year >= 2025:
                state = "SEALED"
                reasons.append("TARGET_HOLDOUT_SEALED")
            elif any(
                not a.provider_adjustment_supported and day < a.boundary <= target_day
                for a in dataset.actions
                if target_day is not None
            ):
                reasons.append("LABEL_UNSUPPORTED_ACTION")
            elif (
                reference_row is None
                or reference_row.bar is None
                or terminal_row is None
                or terminal_row.bar is None
            ):
                reasons.append("TARGET_UNAVAILABLE")
            else:
                try:
                    label = research_direction(
                        reference_row.bar.close,
                        terminal_row.bar.close,
                        reference_basis=reference_row.price_series_basis,
                        terminal_basis=terminal_row.price_series_basis,
                        profile=schema.profile,
                    )
                    state = "ELIGIBLE"
                except ValueError as exc:
                    reasons.append(str(exc))
        result.append(
            RetrospectiveObservation(
                observation_id="ff1-adjusted:RELIANCE:" + day.isoformat(),
                reference_date=day,
                target_date=target_day,
                profile_fingerprint=schema.profile.fingerprint,
                input_fingerprint=input_fp,
                reference_closes_at=close,
                information_cutoff=cutoff,
                simulation_as_of=as_of,
                target_opens_at=None if target is None else target[1],
                target_closes_at=None if target is None else target[2],
                assumed_label_available_at=None
                if label is None or target is None
                else (target[2] + timedelta(minutes=30)),
                feature_window_dates=window_dates,
                features=features,
                label=label,
                label_state=state,
                reasons=tuple(reasons),
                precision_feature_drift=drift,
            )
        )
    return tuple(result)


def _folds(
    observations: tuple[RetrospectiveObservation, ...],
    sessions: tuple[Session, ...],
) -> tuple[RetrospectiveFold, ...]:
    result = []
    for year in range(2021, 2026):
        first = next((i for i, s in enumerate(sessions) if s[0].year == year), None)
        if first is None or first == 0:
            continue
        embargo, fit_cutoff, _ = sessions[first - 1]
        earlier = tuple(o for o in observations if o.reference_date.year < year)
        cutoff_safe = tuple(
            o
            for o in earlier
            if o.target_closes_at is not None
            and o.target_closes_at + timedelta(minutes=30) < fit_cutoff
        )
        train = tuple(o for o in cutoff_safe if o.features is not None and o.label is not None)
        safe_ids = {o.observation_id for o in cutoff_safe}
        purge = tuple(o for o in earlier if o.observation_id not in safe_ids)
        # Select last 20 *scheduled*, not last 20 valid/feature-complete transitions.
        baseline = cutoff_safe[-20:]
        support = sum(o.label is not None for o in baseline)
        test = tuple(o for o in observations if o.reference_date.year == year)
        paired = tuple(o for o in test if o.features is not None and o.label is not None)
        positive, zero = sum(o.label == 1 for o in train), sum(o.label == 0 for o in train)
        paired_ids = {o.observation_id for o in paired}
        blocks = sum(
            all(o.observation_id in paired_ids for o in test[i : i + 5])
            for i in range(0, len(test) - 4, 5)
        )
        problems = []
        if len(train) < 500 or min(positive, zero) < 100:
            problems.append("TRAIN_SUPPORT")
        if len(baseline) != 20 or support != 20:
            problems.append("BASERATE_SUPPORT")
        if year < 2025 and (
            len(paired) < 150
            or min(sum(o.label == 1 for o in paired), sum(o.label == 0 for o in paired)) < 30
            or len(paired) < 0.8 * len(test)
            or blocks < 20
        ):
            problems.append("DEVELOPMENT_TEST_SUPPORT")
        if year == 2025 and len(test) < 200:
            problems.append("HOLDOUT_STRUCTURAL_SUPPORT")
        result.append(
            RetrospectiveFold(
                test_year=year,
                fit_cutoff=fit_cutoff,
                embargo_date=embargo,
                train_ids=tuple(o.observation_id for o in train),
                purged_ids=tuple(o.observation_id for o in purge),
                test_ids=tuple(o.observation_id for o in test),
                paired_potential_ids=tuple(o.observation_id for o in paired),
                baseline_support_ids=tuple(o.observation_id for o in baseline),
                baseline_support_eligible=support,
                train_positive=positive,
                train_zero=zero,
                test_feature_complete=None
                if year == 2025
                else sum(o.features is not None for o in test),
                test_label_complete=None
                if year == 2025
                else sum(o.label is not None for o in test),
                test_positive=None if year == 2025 else sum(o.label == 1 for o in test),
                test_zero=None if year == 2025 else sum(o.label == 0 for o in test),
                complete_five_session_blocks=None if year == 2025 else blocks,
                structural_holdout_slots=len(test) if year == 2025 else None,
                test_outcomes_sealed=year == 2025,
                blocking_reasons=tuple(problems),
            )
        )
    return tuple(result)


def qualify_retrospective(
    dataset: RetrospectiveDataset,
    *,
    assessed_at: datetime,
    profile: AdjustedResearchProfile,
    config: ResearchRightsConfig,
) -> RetrospectiveQualification:
    """Explicit offline scientific admission, not a learning grant or model fit."""
    dataset = RetrospectiveDataset.model_validate(dataset.model_dump())
    profile = AdjustedResearchProfile.model_validate(profile.model_dump())
    config = ResearchRightsConfig.model_validate(config.model_dump())
    assessed_at = TypeAdapter(ForecastDateTime).validate_python(assessed_at)
    schema = AdjustedFF1FeatureSchema(profile=profile)
    admission, warnings = rights_admission(dataset.rights_status, config.rights_enforcement_policy)
    sessions = dataset.calendar.sessions()
    dates = tuple(row.session_date for row in dataset.rows)
    expected = tuple(s[0] for s in sessions)
    problems = []
    if dates != tuple(sorted(set(dates))):
        problems.append("DATASET_CHRONOLOGY_OR_DUPLICATES")
    if set(dates) - set(expected):
        problems.append("UNEXPLAINED_NON_SESSION_ROW")
    if set(expected) - set(dates):
        problems.append("MISSING_SCHEDULED_BAR")
    if admission is RightsAdmissionResult.HOLD:
        problems.append("RIGHTS_HOLD")
    if not dataset.identity_qualified or dataset.resolved.quality is not DataQuality.GOOD:
        problems.append("IDENTITY_UNQUALIFIED")
    if not dataset.adjustment_qualified:
        problems.append("ADJUSTMENT_UNQUALIFIED")
    if not dataset.action_review_qualified:
        problems.append("ACTION_REVIEW_UNQUALIFIED")
    if not dataset.calendar.qualified or dataset.calendar.reviewed_at > assessed_at:
        problems.append("CALENDAR_UNQUALIFIED")
    if dataset.acquired_at > assessed_at:
        problems.append("ACQUISITION_AFTER_EVALUATION")
    for row in dataset.rows:
        if row.bar is not None and (
            row.bar.instrument != dataset.resolved.instrument
            or row.bar.source_provider != dataset.resolved.provider_name
            or row.bar.interval != "1d"
            or min(row.bar.open, row.bar.high, row.bar.low, row.bar.close) <= 0
            or (row.bar.start_at, row.bar.end_at)
            != next(((s[1], s[2]) for s in sessions if s[0] == row.session_date), (None, None))
        ):
            problems.append("BAR_IDENTITY_OR_CLOCK_OR_PRICE")
            break
    # The context seal binds the complete artifact but never puts future *values*
    # into a feature projector. 2025+ rows are structurally redacted by contract.
    context_fp = semantic_fingerprint((dataset, profile, config, schema))
    observations = _observations(dataset, schema, sessions, assessed_at, context_fp, bool(problems))
    folds = _folds(observations, sessions)
    if len(folds) != 5:
        problems.append("FOLD_COVERAGE")
    problems.extend(f"FOLD_{f.test_year}_{r}" for f in folds for r in f.blocking_reasons)
    if sum(len(f.paired_potential_ids) for f in folds if f.test_year < 2025) < 600:
        problems.append("POOLED_DEVELOPMENT_SUPPORT")
    if any(r.startswith("PRECISION_") for o in observations for r in o.reasons):
        problems.append("NUMERIC_PRECISION_MATERIAL")
    if any("FEATURE_UNAVAILABLE" in o.reasons for o in observations):
        problems.append("FEATURE_DERIVATION_FAILED")
    unsealed = tuple(o for o in observations if o.reference_date.year < 2025)
    feature_rows = tuple(o for o in unsealed if o.features is not None)
    value_rows = tuple(o.features.values for o in feature_rows if o.features is not None)
    bars_by_date = {r.session_date: r.bar for r in dataset.rows if r.bar is not None}
    endpoint_gaps = []
    equal_closes = 0
    for observation in unsealed:
        # Only already eligible, unsealed labels; never look at a protected price.
        if observation.label is None or observation.target_date is None:
            continue
        first_bar = bars_by_date[observation.reference_date]
        second_bar = bars_by_date[observation.target_date]
        gap = abs(second_bar.close - first_bar.close)
        if gap == 0:
            equal_closes += 1
        else:
            envelope = profile.near_tie_ulps * (
                math.ulp(first_bar.close) + math.ulp(second_bar.close)
            )
            endpoint_gaps.append((gap, gap / envelope))
    audit: dict[str, Any] = {
        "requested": len(observations),
        "unsealed_requested": len(unsealed),
        "holdout_structural": len(observations) - len(unsealed),
        "feature_eligible": len(feature_rows),
        "label_eligible": sum(o.label is not None for o in unsealed),
        "positive": sum(o.label == 1 for o in unsealed),
        "zero": sum(o.label == 0 for o in unsealed),
        "label_unavailable": sum(o.label_state == "UNAVAILABLE" for o in unsealed),
        "label_sealed": sum(o.label_state == "SEALED" for o in observations),
        "paired_ready_potential": sum(o.label is not None for o in feature_rows),
        "exclusion_reasons": dict(
            sorted(Counter(r for o in observations for r in o.reasons).items())
        ),
        "feature_nonfinite": sum(not math.isfinite(v) for row in value_rows for v in row),
        "feature_sanity": {
            spec.name: {
                "minimum": min(v[i] for v in value_rows),
                "maximum": max(v[i] for v in value_rows),
            }
            for i, spec in enumerate(schema.features)
        }
        if value_rows
        else {},
        "feature_fingerprint": semantic_fingerprint(
            tuple((o.observation_id, o.features) for o in feature_rows)
        ),
        "maximum_feature_perturbation": max(
            (o.precision_feature_drift or 0 for o in unsealed), default=0
        ),
        "rights_status": dataset.rights_status.value,
        "rights_policy": config.rights_enforcement_policy.value,
        "rights_admission": admission.value,
        "rights_config_fingerprint": config.fingerprint,
        "warnings": (*warnings, *dataset.warnings),
        "calendar_fingerprint": semantic_fingerprint(dataset.calendar),
        "calendar_missing_dates": tuple(d.isoformat() for d in sorted(set(expected) - set(dates))),
        "calendar_unexplained_dates": tuple(
            d.isoformat() for d in sorted(set(dates) - set(expected))
        ),
        "weekend_dates": tuple(d.isoformat() for d in dates if d.weekday() >= 5),
        "dataset_rows": len(dates),
        "source_manifest_fingerprint": dataset.source_manifest_fingerprint,
        "acquired_at": dataset.acquired_at.isoformat(),
        "holdout_status": "SEALED",
        "holdout_empirical_test_support": "DEFERRED_UNTIL_SEPARATE_HOLDOUT_GRANT",
        "leakage_audit": "PASS" if not problems else "HOLD",
        "fits": 0,
        "scaler_fits": 0,
        "forecasts": 0,
        "paired_metrics": 0,
        "equal_normalized_close_labels": equal_closes,
        "minimum_nonzero_endpoint_gap": min((x[0] for x in endpoint_gaps), default=None),
        "minimum_gap_over_perturbation_envelope": min((x[1] for x in endpoint_gaps), default=None),
    }
    # Metadata dictionaries are JSON-shaped so model reconstruction is exact.
    # Semantic collections/memberships remain tuples in the typed contracts.
    audit = json.loads(json.dumps(audit))
    return RetrospectiveQualification(
        profile=profile,
        assessed_at=assessed_at,
        dataset_fingerprint=dataset.dataset_sha256,
        context_fingerprint=context_fp,
        feature_schema=schema,
        observations=observations,
        folds=folds,
        audit=audit,
        blocking_reasons=tuple(dict.fromkeys(problems)),
        empirical_fitting_authorized=not problems,
    )
