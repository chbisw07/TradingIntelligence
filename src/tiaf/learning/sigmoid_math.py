"""Bounded numeric kernel. No data loading, fitting authority or candidate selection."""

import math

from pydantic import TypeAdapter

from .calibration_contracts import Probability
from .sigmoid_contracts import CalibrationSample, SigmoidParameters


def logit(p: float) -> float:
    p = TypeAdapter(Probability).validate_python(p)
    clipped = min(1 - 1e-15, max(1e-15, p))
    return math.log(clipped) - math.log1p(-clipped)


def sigmoid(z: float) -> float:
    if not math.isfinite(z):
        raise ValueError("NONFINITE_SIGMOID_SCORE")
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    exp = math.exp(z)
    return exp / (1 + exp)


def transform(parameters: SigmoidParameters, probability: float) -> float:
    parameters = SigmoidParameters.model_validate(parameters)
    return sigmoid(parameters.intercept + parameters.slope * logit(probability))


def _estimate(sample: CalibrationSample, *, offset_only: bool = False) -> tuple[float, float]:
    """Newton/Armijo v1: one solve, fixed start, 1000 steps, 32 backtracks/step.

    Used by the authorized Learning worker and Evaluation-only diagnostics.
    This kernel grants no permission and cannot persist/activate a fitted model.
    """
    sample = CalibrationSample.model_validate(sample)
    xs = tuple(logit(p) for p in sample.probabilities)
    ys = sample.labels
    if set(ys) != {0, 1}:
        raise ValueError("CALIBRATION_BOTH_CLASSES_REQUIRED")
    if not offset_only and max(xs) == min(xs):
        raise ValueError("CALIBRATION_NOT_ESTIMABLE")
    # Complete or quasi separation: no finite unpenalized two-parameter MLE.
    zero = tuple(x for x, y in zip(xs, ys, strict=True) if y == 0)
    one = tuple(x for x, y in zip(xs, ys, strict=True) if y == 1)
    if not offset_only and (max(zero) <= min(one) or max(one) <= min(zero)):
        raise ValueError("CALIBRATION_SEPARATION")
    a, b = 0.0, 1.0

    def loss(intercept: float, slope: float) -> float:
        zs = tuple(intercept + slope * x for x in xs)
        return sum(
            max(z, 0) - y * z + math.log1p(math.exp(-abs(z))) for z, y in zip(zs, ys, strict=True)
        ) / len(xs)

    for _ in range(1000):
        ps = tuple(sigmoid(a + b * x) for x in xs)
        ga = sum(p - y for p, y in zip(ps, ys, strict=True)) / len(xs)
        gb = (
            0.0
            if offset_only
            else sum((p - y) * x for p, y, x in zip(ps, ys, xs, strict=True)) / len(xs)
        )
        if max(abs(ga), abs(gb)) <= 1e-8:
            return a, b
        h00 = sum(p * (1 - p) for p in ps) / len(xs)
        h01 = sum(p * (1 - p) * x for p, x in zip(ps, xs, strict=True)) / len(xs)
        h11 = sum(p * (1 - p) * x * x for p, x in zip(ps, xs, strict=True)) / len(xs)
        determinant = h00 * h11 - h01 * h01
        if h00 <= 1e-15 or (not offset_only and determinant <= 1e-15):
            raise ValueError("CALIBRATION_SINGULAR_HESSIAN")
        da = ga / h00 if offset_only else (h11 * ga - h01 * gb) / determinant
        db = 0.0 if offset_only else (h00 * gb - h01 * ga) / determinant
        old = loss(a, b)
        for backtrack in range(32):
            step = 0.5**backtrack
            na, nb = a - step * da, b - step * db
            if loss(na, nb) <= old - 1e-4 * step * (ga * da + gb * db):
                a, b = na, nb
                break
        else:
            raise ValueError("CALIBRATION_LINE_SEARCH_FAILED")
    raise ValueError("CALIBRATION_NOT_CONVERGED")
