"""Preregistered development diagnostics; no forecast transformation or tuning."""

import math
import time
from typing import Annotated, Literal

from pydantic import Field

from tiaf.forecasting.research_contracts import ResearchContract
from tiaf.learning.forecast_artifacts import Finite, SealedResearch
from tiaf.planner.models import Sha256


class DevelopmentPolicy(SealedResearch):
    policy_id: Literal["ff1.development_only_paired/1.0"] = "ff1.development_only_paired/1.0"
    scope: Literal["DEVELOPMENT_ONLY"] = "DEVELOPMENT_ONLY"
    seed: Literal[1729] = 1729
    generator: Literal["numpy.Generator(PCG64)/2.3.3"] = "numpy.Generator(PCG64)/2.3.3"
    block_length: Literal[5] = 5
    replicates: Literal[5000] = 5000
    epsilon: Annotated[Finite, Field(ge=1e-15, le=1e-15)] = 1e-15
    interval_quantiles: tuple[Literal["0.0125"], Literal["0.9875"]] = ("0.0125", "0.9875")
    quantile_method: Literal["linear"] = "linear"
    threshold: Literal["p>=0.5; ties positive"] = "p>=0.5; ties positive"
    binning: Literal["10_FIXED_WIDTH; last bin closed; minimum 20"] = (
        "10_FIXED_WIDTH; last bin closed; minimum 20"
    )
    weighting: Literal["UNIFORM_UNIQUE_PAIRED_OBSERVATIONS"] = "UNIFORM_UNIQUE_PAIRED_OBSERVATIONS"
    ordering: Literal["FOLD_ASC; REFERENCE_SESSION_ASC; KEEP_MISSING_MASK"] = (
        "FOLD_ASC; REFERENCE_SESSION_ASC; KEEP_MISSING_MASK"
    )
    loss_difference: Literal["LOGISTIC_MINUS_BASERATE"] = "LOGISTIC_MINUS_BASERATE"
    bootstrap_draws: Literal["FRESH_SEED_PER_SUMMARY; FOLD_MAJOR; REPLICATE_MAJOR"] = (
        "FRESH_SEED_PER_SUMMARY; FOLD_MAJOR; REPLICATE_MAJOR"
    )
    minimum_fold_pairs: Literal[150] = 150
    minimum_class: Literal[30] = 30
    minimum_pooled_pairs: Literal[600] = 600
    minimum_coverage: Literal["0.8"] = "0.8"
    minimum_complete_blocks: Literal[20] = 20
    minimum_negative_brier_folds: Literal[3] = 3
    maximum_fold_brier_worsening: Literal["0.02"] = "0.02"
    maximum_fold_logloss_worsening: Literal["0.05"] = "0.05"
    bootstrap_timeout_seconds: Literal[120] = 120
    final_holdout_evidence: Literal["NOT_RUN"] = "NOT_RUN"
    support_permitted: Literal[False] = False


def losses(p: float, y: int) -> tuple[float, float]:
    if not math.isfinite(p) or not 0 <= p <= 1 or type(y) is not int or y not in (0, 1):
        raise ValueError("INVALID_PAIRED_METRIC_INPUT")
    q = min(1 - 1e-15, max(1e-15, p))
    return (p - y) ** 2, -math.log(q) if y else -math.log1p(-q)


class ReliabilityBin(ResearchContract):
    index: int
    count: int
    mean_probability: Finite | None
    observed_frequency: Finite | None
    support: Literal["LOW_SUPPORT", "DESCRIPTIVE_ONLY"]


class ArmMetrics(ResearchContract):
    brier: Finite
    log_loss: Finite
    accuracy: Finite
    mean_probability: Finite
    endpoint_count: int
    clipped_count: int
    confusion: tuple[int, int, int, int]  # TP, FP, TN, FN, fixed p>=.5
    reliability: tuple[ReliabilityBin, ...]


def arm_metrics(values: tuple[tuple[float, int], ...]) -> ArmMetrics | None:
    if not values:
        return None
    n = len(values)
    loss = tuple(losses(p, y) for p, y in values)
    bins = []
    for index in range(10):
        rows = tuple((p, y) for p, y in values if min(9, int(p * 10)) == index)
        bins.append(
            ReliabilityBin(
                index=index,
                count=len(rows),
                mean_probability=None if not rows else math.fsum(p for p, _ in rows) / len(rows),
                observed_frequency=None if not rows else sum(y for _, y in rows) / len(rows),
                support="LOW_SUPPORT" if len(rows) < 20 else "DESCRIPTIVE_ONLY",
            )
        )
    return ArmMetrics(
        brier=math.fsum(b for b, _ in loss) / n,
        log_loss=math.fsum(ll for _, ll in loss) / n,
        accuracy=sum(int(p >= 0.5) == y for p, y in values) / n,
        mean_probability=math.fsum(p for p, _ in values) / n,
        endpoint_count=sum(p in (0, 1) for p, _ in values),
        clipped_count=sum(p < 1e-15 or p > 1 - 1e-15 for p, _ in values),
        confusion=(
            sum(p >= 0.5 and y == 1 for p, y in values),
            sum(p >= 0.5 and y == 0 for p, y in values),
            sum(p < 0.5 and y == 0 for p, y in values),
            sum(p < 0.5 and y == 1 for p, y in values),
        ),
        reliability=tuple(bins),
    )


class BootstrapResult(ResearchContract):
    scope: Literal["DEVELOPMENT_ONLY"] = "DEVELOPMENT_ONLY"
    status: Literal["ESTIMATED", "NOT_ESTIMABLE"]
    effective_n: int
    point: tuple[Finite, Finite] | None  # Brier, log loss
    bootstrap_mean: tuple[Finite, Finite] | None
    brier_interval: tuple[Finite, Finite] | None
    logloss_interval: tuple[Finite, Finite] | None
    zero_pair_replicates: int
    seed: Literal[1729] = 1729
    block_length: Literal[5] = 5
    replicates: Literal[5000] = 5000
    sampled_indices_fingerprint: Sha256


def bootstrap(grids: tuple[tuple[tuple[float, float] | None, ...], ...]) -> BootstrapResult:
    """Masked original grids; no blocks across folds or circular boundary wrap.

    One deterministic stream per summary, folds in ascending order. Both losses use
    the same sampled indices. Batch size bounded by 5000 x <=4096 indices.
    """
    from hashlib import sha256

    import numpy as np

    if not grids or sum(map(len, grids)) > 4096:
        raise ValueError("BOOTSTRAP_GRID_LIMIT")
    started = time.monotonic()
    rng = np.random.Generator(np.random.PCG64(1729))
    totals = np.zeros((5000, 2), dtype=np.float64)
    counts = np.zeros(5000, dtype=np.int64)
    digest = sha256()
    observed = tuple(row for grid in grids for row in grid if row is not None)
    for grid in grids:
        length = len(grid)
        if length < 5:
            raise ValueError("BOOTSTRAP_GRID_SHORTER_THAN_BLOCK")
        starts = rng.integers(0, length - 4, size=(5000, math.ceil(length / 5)))
        indices = (starts[:, :, None] + np.arange(5)).reshape(5000, -1)[:, :length]
        digest.update(indices.astype("<i8").tobytes())
        mask = np.array([row is not None for row in grid], dtype=np.bool_)
        values = np.array(
            [row if row is not None else (0.0, 0.0) for row in grid], dtype=np.float64
        )
        if not np.isfinite(values).all():
            raise ValueError("NONFINITE_BOOTSTRAP_INPUT")
        totals += values[indices].sum(axis=1, dtype=np.float64)
        counts += mask[indices].sum(axis=1, dtype=np.int64)
        if time.monotonic() - started > 120:
            raise ValueError("BOOTSTRAP_TIMEOUT")
    empty = int((counts == 0).sum())
    point = (
        None
        if not observed
        else (
            math.fsum(r[0] for r in observed) / len(observed),
            math.fsum(r[1] for r in observed) / len(observed),
        )
    )
    if empty:
        return BootstrapResult(
            status="NOT_ESTIMABLE",
            effective_n=len(observed),
            point=point,
            bootstrap_mean=None,
            brier_interval=None,
            logloss_interval=None,
            zero_pair_replicates=empty,
            sampled_indices_fingerprint=digest.hexdigest(),
        )
    samples = totals / counts[:, None]
    intervals = np.quantile(samples, [0.0125, 0.9875], axis=0, method="linear")
    return BootstrapResult(
        status="ESTIMATED",
        effective_n=len(observed),
        point=point,
        bootstrap_mean=(float(samples[:, 0].mean()), float(samples[:, 1].mean())),
        brier_interval=(float(intervals[0, 0]), float(intervals[1, 0])),
        logloss_interval=(float(intervals[0, 1]), float(intervals[1, 1])),
        zero_pair_replicates=0,
        sampled_indices_fingerprint=digest.hexdigest(),
    )
