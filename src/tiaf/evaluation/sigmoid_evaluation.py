"""Independent FF-2 synthetic calibration projection and descriptive diagnostics.

Learning never owns truth or comparison decisions. This bridge validates p/q
against captured lineage before handing off to the unchanged FLC-6 evaluator.
"""

from typing import Literal

from pydantic import Field

from tiaf.learning.forecast_artifacts import Finite, SealedResearch
from tiaf.learning.forecaster_training import reference
from tiaf.learning.sigmoid_contracts import CalibratedCapture, CalibrationSample
from tiaf.learning.sigmoid_math import _estimate

from .forecast_normalization import evaluate_normalized
from .forecast_normalization_contracts import (
    EvaluationInput,
    NormalizedEvaluationResult,
    Probability,
)


def evaluate_calibrated(
    supplied: EvaluationInput,
    captures: tuple[CalibratedCapture, ...],
) -> NormalizedEvaluationResult:
    """Two-arm raw/calibrated join; no empirical adapter or execution grant."""
    supplied = EvaluationInput.model_validate(supplied)
    captures = tuple(CalibratedCapture.model_validate(c) for c in captures)
    if not captures or len(captures) > 120:
        raise ValueError("CALIBRATED_EVALUATION_CAPTURE_BOUND")
    rows = {c.source.result.request.observation_id: c for c in captures}
    if len(rows) != len(captures) or set(rows) != set(supplied.request.population.observation_ids):
        raise ValueError("CALIBRATED_EVALUATION_POPULATION_MISMATCH")
    if len({c.candidate.fingerprint for c in captures}) != 1:
        raise ValueError("CALIBRATED_EVALUATION_MIXED_CANDIDATES")
    candidate = captures[0].candidate
    component = candidate.artifact.component
    participants = supplied.request.participants
    if len(participants) != 2 or tuple(p.form for p in participants) != (
        "ARTIFACT_BACKED_FORECASTER",
        "CALIBRATED_COMPOSITION",
    ):
        raise ValueError("CALIBRATED_EVALUATION_RAW_THEN_CALIBRATED_REQUIRED")
    for index, participant in enumerate(participants):
        expected_key = component.source_forecaster if index == 0 else candidate.key
        expected_ref = (
            candidate.source_composition if index == 0 else reference("sigmoidcandidate", candidate)
        )
        if (
            participant.forecaster != expected_key
            or participant.forecast_or_composition != expected_ref
            or participant.target.target_id != component.target.target_id
            or participant.target.target_version != component.target.target_version
            or participant.target.horizon != component.target.horizon
            or participant.target.event != component.target.positive_event
            or participant.target.cutoff_policy != component.target.cutoff_policy
            or participant.realization_mode != component.mode
            or participant.report_role != ("SUBJECT" if index == 0 else "CHALLENGER")
        ):
            raise ValueError("CALIBRATED_EVALUATION_IDENTITY_CONTRADICTION")
        for observation in supplied.forecast_sets[index].observations:
            capture = rows[observation.observation_id]
            probability = capture.raw_probability if index == 0 else capture.calibrated_probability
            forecast_ref = (
                reference("neutralinfercapture", capture.source)
                if index == 0
                else reference("sigmoidcapture", capture)
            )
            if (
                observation.probability != probability
                or observation.forecast_ref != forecast_ref
                or capture.created_at > supplied.captured_at
                or supplied.request.population.subject != capture.source.result.request.subject
            ):
                raise ValueError("CALIBRATED_EVALUATION_OUTPUT_CONTRADICTION")
    return evaluate_normalized(supplied.request, supplied)


class ReliabilityBin(SealedResearch):
    index: int = Field(ge=0, lt=10, strict=True)
    count: int = Field(ge=0, strict=True)
    mean_probability: Probability | None
    event_frequency: Probability | None
    support: Literal["EMPTY", "LOW_SUPPORT", "SUPPORTED"]


class CalibrationDiagnostics(SealedResearch):
    count: int = Field(ge=2, le=4096, strict=True)
    bins: tuple[ReliabilityBin, ...] = Field(min_length=10, max_length=10)
    mean_error: Finite
    ece: Probability
    mce: Probability
    offset_intercept: Finite | None
    slope_intercept: Finite | None
    slope: Finite | None
    offset_status: Literal["ESTIMATED", "NOT_ESTIMABLE"]
    slope_status: Literal["ESTIMATED", "NOT_ESTIMABLE"]
    interpretation: Literal["SYNTHETIC_DESCRIPTIVE_NOT_QUALIFICATION"] = (
        "SYNTHETIC_DESCRIPTIVE_NOT_QUALIFICATION"
    )
    feedback_to_calibrator: Literal[False] = False


def calibration_diagnostics(sample: CalibrationSample) -> CalibrationDiagnostics:
    """Evaluation-only, bounded diagnostic fits; never emit candidate parameters.

    Inputs are supplied probability/truth pairs, not observations labeled by a
    forecaster. This function is a pure numeric diagnostic, not fit admission.
    """
    sample = CalibrationSample.model_validate(sample)
    bins: list[ReliabilityBin] = []
    gaps: list[float] = []
    ece = 0.0
    for index in range(10):
        values = tuple(
            (p, y)
            for p, y in zip(sample.probabilities, sample.labels, strict=True)
            if min(9, int(p * 10)) == index
        )
        n = len(values)
        mean = sum(p for p, _ in values) / n if n else None
        frequency = sum(y for _, y in values) / n if n else None
        if mean is not None and frequency is not None:
            gap = abs(mean - frequency)
            gaps.append(gap)
            ece += n / len(sample.labels) * gap
        bins.append(
            ReliabilityBin(
                index=index,
                count=n,
                mean_probability=mean,
                event_frequency=frequency,
                support="EMPTY" if not n else "LOW_SUPPORT" if n < 20 else "SUPPORTED",
            )
        )
    try:
        offset, _ = _estimate(sample, offset_only=True)
    except ValueError:
        offset = None
    try:
        intercept, slope = _estimate(sample)
    except ValueError:
        intercept, slope = None, None
    return CalibrationDiagnostics(
        count=len(sample.labels),
        bins=tuple(bins),
        mean_error=sum(p - y for p, y in zip(sample.probabilities, sample.labels, strict=True))
        / len(sample.labels),
        ece=ece,
        mce=max(gaps),
        offset_intercept=offset,
        slope_intercept=intercept,
        slope=slope,
        offset_status="ESTIMATED" if offset is not None else "NOT_ESTIMABLE",
        slope_status="ESTIMATED" if slope is not None else "NOT_ESTIMABLE",
    )
