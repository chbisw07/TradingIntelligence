"""Synthetic-only FF-1.4 engineering: no empirical metrics or holdout decoding."""

import json
import math
import shutil
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from tiaf.evaluation.forecast_comparison import (
    DevelopmentDecision,
    DevelopmentEvaluation,
    decide,
    pair_observation,
)
from tiaf.evaluation.forecast_comparison_metrics import (
    DevelopmentPolicy,
    arm_metrics,
    bootstrap,
    losses,
)
from tiaf.evaluation.forecast_comparison_store import (
    DevelopmentEvaluationStore,
    EvaluationLedger,
    EvaluationManifest,
    capture_logistic,
    persist_evaluation,
    verify_evaluation,
    write_truth,
)
from tiaf.evaluation.forecast_research_truth import (
    ResearchTruthJournal,
    load_research_truth,
)
from tiaf.evaluation.forecast_retrospective_contracts import RetrospectiveQualification
from tiaf.forecasting.forecasters import HistoricalBaseRateForecaster
from tiaf.forecasting.logistic_forecasts import (
    ForecastShard,
    LogisticForecastRun,
    generate,
    population,
)
from tiaf.forecasting.logistic_projection import ForecastProjection
from tiaf.forecasting.logistic_store import ResearchForecastStore, capture_training
from tiaf.forecasting.research_baserate import (
    ResearchBaseRateArtifact,
    baseline_forecast,
    freeze_baseline,
)
from tiaf.forecasting.support import admit_support
from tiaf.learning.forecast_jobs import TrainingRun

from ..forecasting.test_adjusted_retrospective_research import AT
from ..forecasting.test_logistic_forecasts import handoff as handoff
from ..forecasting.test_logistic_forecasts import projection as projection
from ..forecasting.test_logistic_training_admission import qualification as qualification


@pytest.fixture(scope="module")
def journal(
    qualification: RetrospectiveQualification,
    handoff: TrainingRun,
    tmp_path_factory: pytest.TempPathFactory,
) -> ResearchTruthJournal:
    p = tmp_path_factory.mktemp("truth") / "q.json"
    raw = qualification.model_dump_json().encode()
    p.write_bytes(raw)
    return load_research_truth(p, sha256(raw).hexdigest(), handoff)


def update(model: Any, **fields: Any) -> Any:
    return type(model).model_validate({**model.model_dump(exclude={"fingerprint"}), **fields})


@pytest.mark.parametrize("p,y,brier", [(0.0, 0, 0.0), (1.0, 1, 0.0), (1.0, 0, 1.0), (0.5, 1, 0.25)])
def test_proper_loss_toys(p: float, y: int, brier: float) -> None:
    b, ll = losses(p, y)
    assert b == brier and math.isfinite(ll)
    if p == 0.5:
        assert ll == math.log(2)


@pytest.mark.parametrize("p,y", [(float("nan"), 0), (1.1, 0), (-0.1, 1), (0.5, True), (0.5, 2)])
def test_invalid_loss_inputs(p: float, y: int) -> None:
    with pytest.raises(ValueError):
        losses(p, y)


def test_logloss_same_clipping_accuracy_ties_and_bins() -> None:
    assert losses(0.0, 1)[1] == -math.log(1e-15)
    assert losses(1.0, 0)[1] == -math.log1p(-(1 - 1e-15))
    m = arm_metrics(((0.5, 1), (0.0, 0), (1.0, 0)))
    assert m is not None
    assert m.accuracy == 2 / 3 and m.endpoint_count == m.clipped_count == 2
    assert m.reliability[5].count == 1 and m.reliability[9].count == 1
    assert all(b.support == "LOW_SUPPORT" for b in m.reliability)
    assert arm_metrics(()) is None


def test_bootstrap_identical_repeatable_zero_and_masks() -> None:
    zero = bootstrap((((0.0, 0.0),) * 25,))
    assert zero.point == zero.bootstrap_mean == zero.brier_interval == (0.0, 0.0)
    assert zero.logloss_interval == (0.0, 0.0)
    grid = tuple(None if i in (4, 8, 9) else (float(i), float(i) * 2) for i in range(25))
    result = bootstrap((grid,))
    assert result == bootstrap((grid,)) and result.effective_n == 22
    compressed = bootstrap((tuple(r for r in grid if r is not None),))
    assert result.sampled_indices_fingerprint != compressed.sampled_indices_fingerprint
    assert result.replicates == 5000 and result.block_length == 5 and result.seed == 1729
    assert bootstrap(((None,) * 20,)).zero_pair_replicates == 5000


def test_bootstrap_matches_independent_reference() -> None:
    import numpy as np

    grids = (
        tuple((float(i), -float(i)) for i in range(11)),
        tuple(None if i == 7 else (float(i * 2), float(i)) for i in range(13)),
    )
    rng = np.random.Generator(np.random.PCG64(1729))
    totals = [[0.0, 0.0, 0] for _ in range(5000)]
    for grid in grids:
        for rep in range(5000):
            starts = rng.integers(0, len(grid) - 4, size=math.ceil(len(grid) / 5))
            indices = [int(s) + j for s in starts for j in range(5)][: len(grid)]
            for i in indices:
                row = grid[i]
                if row is not None:
                    totals[rep][0] += row[0]
                    totals[rep][1] += row[1]
                    totals[rep][2] += 1
    samples = [r[0] / r[2] for r in totals]
    expected = np.quantile(samples, [0.0125, 0.9875], method="linear")
    result = bootstrap(grids)
    assert result.brier_interval == tuple(expected)
    assert result.bootstrap_mean is not None
    assert result.bootstrap_mean[0] == pytest.approx(math.fsum(samples) / 5000, abs=1e-12)


def test_truth_loader_never_decodes_protected_outcomes(
    qualification: RetrospectiveQualification,
    handoff: TrainingRun,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = qualification.model_dump(mode="json")
    for o in data["observations"]:
        if o["reference_date"] >= "2025" or (o["target_date"] or "") >= "2025":
            for key in ("label", "label_state", "assumed_label_available_at"):
                o[key] = "FORBIDDEN_PROTECTED_OUTCOME"
    for fold in data["folds"]:
        if fold["test_year"] == 2025:
            for key in tuple(fold):
                if key != "test_year":
                    fold[key] = "FORBIDDEN_PROTECTED_OUTCOME"
    raw = json.dumps(data).encode()
    p = tmp_path / "poison.json"
    p.write_bytes(raw)
    original = json.loads

    def guard(value: Any, *args: Any, **kwargs: Any) -> Any:
        assert "FORBIDDEN_PROTECTED_OUTCOME" not in value
        return original(value, *args, **kwargs)

    monkeypatch.setattr(json, "loads", guard)
    result = load_research_truth(p, sha256(raw).hexdigest(), handoff)
    assert all(e.reference_date.year < 2025 and e.target_date.year < 2025 for e in result.entries)
    assert not any(e.reference_date.isoformat() == "2024-12-31" for e in result.entries)


@pytest.mark.parametrize(
    "field,value",
    [("reference_date", "2025-01-01"), ("target_date", "2025-01-01"), ("label", True)],
)
def test_journal_hard_guard(journal: ResearchTruthJournal, field: str, value: Any) -> None:
    with pytest.raises(ValueError):
        update(journal.entries[0], **{field: value})


def test_last_twenty_no_backfill_or_current_target(
    journal: ResearchTruthJournal, handoff: TrainingRun
) -> None:
    model = handoff.jobs[0].artifact
    assert model is not None
    a = freeze_baseline(journal, 2021, model.manifest.fit_cutoff)
    assert a.output is not None and len(a.support) == 20
    assert a.output.probability == sum(cast(int, e.label) for e in a.support) / 20
    missing = update(
        a.support[-1], label=None, label_state="UNAVAILABLE", assumed_label_available_at=None
    )
    changed = update(
        journal,
        entries=tuple(
            missing if e.observation_id == missing.observation_id else e for e in journal.entries
        ),
    )
    unavailable = freeze_baseline(changed, 2021, model.manifest.fit_cutoff)
    assert unavailable.output is None and unavailable.scheduled_ids == a.scheduled_ids
    # Native truth requires target+30m; arbitrary late-clock mutation is invalid.
    with pytest.raises(ValueError):
        update(a.support[-1], assumed_label_available_at=a.fit_cutoff)


def test_baserate_v1_fixture_parity(journal: ResearchTruthJournal, handoff: TrainingRun) -> None:
    from ..forecasting._runtime_support import fixture

    model = handoff.jobs[0].artifact
    assert model is not None
    a = freeze_baseline(journal, 2021, model.manifest.fit_cutoff)
    for pattern in ("baseline", "zero", "one"):
        f = fixture(pattern=pattern)
        native = HistoricalBaseRateForecaster().forecast(
            f.request, admit_support(f.artifact, f.request)
        )
        labels = tuple(r.label for r in f.artifact.rows)
        support = tuple(update(e, label=y) for e, y in zip(a.support, labels, strict=True))
        output = native.output
        from tiaf.forecasting.contracts import BinaryProbabilityOutput

        assert isinstance(output, BinaryProbabilityOutput)
        research = ResearchBaseRateArtifact(
            fold=2021,
            fit_cutoff=a.fit_cutoff,
            scheduled_ids=a.scheduled_ids,
            support=support,
            output=output,
        )
        assert research.output == native.output


def test_pair_identity_and_absence(
    projection: ForecastProjection, handoff: TrainingRun, journal: ResearchTruthJournal
) -> None:
    o = projection.origins[0]
    r = generate(o, projection, handoff, AT + timedelta(seconds=1))
    model = handoff.jobs[0].artifact
    assert model is not None
    artifact = freeze_baseline(journal, 2021, model.manifest.fit_cutoff)
    b = baseline_forecast(artifact, r.request, AT + timedelta(seconds=2))
    truth = next(e for e in journal.entries if e.observation_id == o.observation_id)
    pair, d = pair_observation(r, b, truth, AT + timedelta(seconds=3))
    assert pair is not None and d.paired and pair.ground_truth_fingerprint == truth.fingerprint
    assert pair.brier_difference == pair.logistic_brier - pair.baseline_brier
    assert pair.logloss_difference == pair.logistic_logloss - pair.baseline_logloss
    assert len(d.decisions) == 4
    assert pair_observation(r, None, truth, AT + timedelta(seconds=3))[0] is None
    with pytest.raises(ValueError, match="IDENTITY"):
        pair_observation(
            r, update(b, common_request_fingerprint="0" * 64), truth, AT + timedelta(seconds=3)
        )
    with pytest.raises(ValueError, match="IDENTITY"):
        pair_observation(
            r, b, update(truth, dataset_fingerprint="0" * 64), AT + timedelta(seconds=3)
        )
    protected = generate(projection.origins[-1], projection, handoff, AT + timedelta(seconds=1))
    with pytest.raises(ValueError, match="PROTECTED"):
        pair_observation(protected, b, truth, AT + timedelta(seconds=3))


@pytest.fixture(scope="module")
def corpus(
    projection: ForecastProjection,
    handoff: TrainingRun,
    journal: ResearchTruthJournal,
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, str]:
    source = ResearchForecastStore(tmp_path_factory.mktemp("source") / "corpus", create=True)
    capture_training(source, handoff)
    records = tuple(
        generate(o, projection, handoff, AT + timedelta(seconds=1)) for o in projection.origins
    )
    refs = tuple(source.put("capture", r) for r in records)
    shards = tuple(
        source.put("shard", ForecastShard(captures=refs[i : i + 64]))
        for i in range(0, len(refs), 64)
    )
    q = records[0].request
    parent = LogisticForecastRun(
        **{
            k: getattr(q, k)
            for k in (
                "qualification_blob",
                "qualification_fingerprint",
                "dataset_fingerprint",
                "research_profile_fingerprint",
                "feature_schema_fingerprint",
                "training_run_fingerprint",
                "dependency_lock_fingerprint",
            )
        },
        shards=shards,
        populations=(
            population(2021, records),
            population(2022, records),
            population(2023, records),
            population(2024, records),
        ),
        verification_matches=len(records),
        created_at=AT + timedelta(seconds=2),
    )
    fp = source.put("run", parent)
    store = DevelopmentEvaluationStore(
        tmp_path_factory.mktemp("evaluation") / "corpus", create=True
    )
    policy = store.put("policy", DevelopmentPolicy())
    capture_logistic(source, store, fp)
    # Projection fixtures independently serialize the same source qualification.
    journal = update(
        journal,
        qualification_blob=q.qualification_blob,
        entries=tuple(update(e, qualification_blob=q.qualification_blob) for e in journal.entries),
    )
    ti = write_truth(store, journal)
    artifacts = {}
    for job in handoff.jobs:
        assert job.artifact is not None
        artifacts[job.fold_id] = freeze_baseline(
            journal, job.fold_id, job.artifact.manifest.fit_cutoff
        )
    forecasts = tuple(
        baseline_forecast(artifacts[r.request.fold_id], r.request, AT + timedelta(seconds=3))
        for r in records
        if not r.request.origin.protected
    )
    m = EvaluationManifest(
        logistic_run=fp,
        truth_index=ti,
        policy_fingerprint=policy,
        baseline_artifacts=tuple(store.put("baseline", a) for a in artifacts.values()),
        baseline_forecasts=tuple(store.put("baselineforecast", f) for f in forecasts),
        protocol_document_sha256="a" * 64,
        clarification_document_sha256="b" * 64,
        implementation_sha256="c" * 64,
        evaluated_at=AT + timedelta(seconds=4),
    )
    return store.root, persist_evaluation(store, m)


def report_from(corpus: tuple[Path, str]) -> DevelopmentEvaluation:
    store = DevelopmentEvaluationStore(corpus[0])
    ledger = cast(EvaluationLedger, store.get("ledger", corpus[1]))
    return cast(DevelopmentEvaluation, store.get("evaluation", ledger.report))


def test_complete_population_reconstructs(
    corpus: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    import socket

    import tiaf.learning.forecast_jobs as jobs

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("forbidden fitting/network access")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(jobs, "run_fit", forbidden)
    assert verify_evaluation(DevelopmentEvaluationStore(corpus[0]), corpus[1]) == "MATCH"
    report = report_from(corpus)
    assert report.summaries[-1].n == 969
    assert tuple(s.n for s in report.summaries[:4]) == (248, 248, 225, 248)
    assert report.summaries[-1].population.requested == 991
    assert report.summaries[-1].population.protected == 1
    assert report.decision.final_holdout_evidence == "NOT_RUN"
    assert DevelopmentEvaluation.model_validate_json(report.model_dump_json()) == report
    with pytest.raises(ValidationError):
        report.created_at = AT


def test_development_rule_no_invented_interval_rejection(corpus: tuple[Path, str]) -> None:
    report = report_from(corpus)
    good = tuple(
        update(s, brier_difference=-0.001, logloss_difference=0.001) for s in report.summaries[:4]
    )
    assert decide(good, report.summaries[-1]).classification == "INSUFFICIENT_EVIDENCE"
    bad = (update(good[0], brier_difference=0.021), *good[1:])
    assert decide(bad, report.summaries[-1]).classification == "LOGISTIC_NOT_SUPPORTED"
    not_three = tuple(update(s, brier_difference=0.001) for s in good)
    assert decide(not_three, report.summaries[-1]).classification == "LOGISTIC_NOT_SUPPORTED"
    low = (update(bad[0], n=20), *bad[1:])
    assert decide(low, report.summaries[-1]).classification == "INSUFFICIENT_EVIDENCE"


def test_supported_and_2025_summary_forbidden(corpus: tuple[Path, str]) -> None:
    with pytest.raises(ValidationError):
        DevelopmentDecision(
            classification="LOGISTIC_SUPPORTED",  # type: ignore[arg-type]
            support_failures=(),
            stability_failures=(),
        )
    with pytest.raises(ValidationError):
        update(report_from(corpus).summaries[0], name="2025")


@pytest.mark.parametrize("kind", ["pair", "truth", "baseline", "policy", "manifest"])
def test_tampered_closure_mismatch(corpus: tuple[Path, str], tmp_path: Path, kind: str) -> None:
    root = tmp_path / "corpus"
    shutil.copytree(corpus[0], root)
    p = next(root.glob(f"{kind}-*.json"))
    p.write_text("{}\n")
    assert verify_evaluation(DevelopmentEvaluationStore(root), corpus[1]) == "MISMATCH"


@pytest.mark.parametrize(
    "field,value",
    [
        ("seed", 123),
        ("block_length", 10),
        ("replicates", 1000),
        ("epsilon", 1e-10),
        ("support_permitted", True),
    ],
)
def test_fixed_preregistered_policy(field: str, value: Any) -> None:
    with pytest.raises(ValidationError):
        DevelopmentPolicy.model_validate({field: value})
