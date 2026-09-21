"""Research Evaluation owner: immutable truth/link/Ledger/scorecard closure."""

import time
from types import MappingProxyType
from typing import Literal, cast

from pydantic import Field

from tiaf.evaluation.forecast_comparison import (
    DevelopmentEvaluation,
    PairedObservation,
    PopulationDisposition,
    decide,
    pair_observation,
    paired_identity,
    summarize,
)
from tiaf.evaluation.forecast_comparison_metrics import DevelopmentPolicy
from tiaf.evaluation.forecast_research_truth import ResearchOutcomeEntry, ResearchTruthJournal
from tiaf.forecasting.identity import ForecastDateTime
from tiaf.forecasting.logistic_store import ResearchForecastStore, recorded_replay, verify_run
from tiaf.forecasting.research_baserate import (
    ResearchBaseRateArtifact,
    ResearchBaseRateForecast,
    baseline_forecast,
    freeze_baseline,
)
from tiaf.learning.forecast_artifacts import SealedResearch
from tiaf.planner.models import Sha256


class TruthIndex(SealedResearch):
    qualification_blob: Sha256
    qualification_fingerprint: Sha256
    journal_fingerprint: Sha256
    entries: tuple[Sha256, ...] = Field(max_length=4096)
    baseline_support: tuple[tuple[int, tuple[str, ...]], ...]


class EvaluationManifest(SealedResearch):
    scope: Literal["DEVELOPMENT_ONLY"] = "DEVELOPMENT_ONLY"
    logistic_run: Sha256
    truth_index: Sha256
    baseline_artifacts: tuple[Sha256, ...] = Field(min_length=4, max_length=4)
    baseline_forecasts: tuple[Sha256, ...] = Field(max_length=4096)
    policy_fingerprint: Sha256
    protocol_document_sha256: Sha256
    clarification_document_sha256: Sha256
    implementation_sha256: Sha256
    evaluated_at: ForecastDateTime
    final_holdout_evidence: Literal["NOT_RUN"] = "NOT_RUN"


class EvaluationShard(SealedResearch):
    pairs: tuple[Sha256, ...] = Field(max_length=64)
    dispositions: tuple[PopulationDisposition, ...] = Field(min_length=1, max_length=64)


class EvaluationLedger(SealedResearch):
    manifest: Sha256
    shards: tuple[Sha256, ...] = Field(min_length=1, max_length=64)
    report: Sha256


class DevelopmentEvaluationStore(ResearchForecastStore):
    record_types = MappingProxyType(
        {
            **ResearchForecastStore.record_types,
            "truth": ResearchOutcomeEntry,
            "truthindex": TruthIndex,
            "baseline": ResearchBaseRateArtifact,
            "baselineforecast": ResearchBaseRateForecast,
            "policy": DevelopmentPolicy,
            "manifest": EvaluationManifest,
            "pair": PairedObservation,
            "evaluationshard": EvaluationShard,
            "evaluation": DevelopmentEvaluation,
            "ledger": EvaluationLedger,
        }
    )


def capture_logistic(
    source: ResearchForecastStore, target: DevelopmentEvaluationStore, run_fp: str
) -> None:
    if verify_run(source, run_fp).status != "MATCH":
        raise ValueError("FF1_3_REPLAY_REQUIRED")
    # Copy only the exact reachable immutable run closure, never unrelated files.
    parent, records, training = recorded_replay(source, run_fp)
    target.put("training", training)
    for job in training.jobs:
        assert job.artifact is not None
        target.put("model", job.artifact)
        target.put("scaler", job.artifact.reconstruction.scaler)
    for r in records:
        target.put("capture", r)
    for fp in parent.shards:
        target.put("shard", source.get("shard", fp))
    target.put("run", parent)


def write_truth(store: DevelopmentEvaluationStore, journal: ResearchTruthJournal) -> str:
    return store.put(
        "truthindex",
        TruthIndex(
            qualification_blob=journal.qualification_blob,
            qualification_fingerprint=journal.qualification_fingerprint,
            journal_fingerprint=cast(str, journal.fingerprint),
            entries=tuple(store.put("truth", e) for e in journal.entries),
            baseline_support=journal.baseline_support,
        ),
    )


def read_truth(store: DevelopmentEvaluationStore, fp: str) -> ResearchTruthJournal:
    index = cast(TruthIndex, store.get("truthindex", fp))
    return ResearchTruthJournal(
        qualification_blob=index.qualification_blob,
        qualification_fingerprint=index.qualification_fingerprint,
        entries=tuple(cast(ResearchOutcomeEntry, store.get("truth", e)) for e in index.entries),
        baseline_support=index.baseline_support,
        fingerprint=index.journal_fingerprint,
    )


def reconstruct_inputs(
    store: DevelopmentEvaluationStore, manifest: EvaluationManifest
) -> tuple[
    tuple[PairedObservation, ...], tuple[PopulationDisposition, ...], ResearchTruthJournal, str
]:
    if verify_run(store, manifest.logistic_run).status != "MATCH":
        raise ValueError("LOGISTIC_PINNED_REPLAY_MISMATCH")
    parent, records, training = recorded_replay(store, manifest.logistic_run)
    journal = read_truth(store, manifest.truth_index)
    if (
        journal.qualification_blob != parent.qualification_blob
        or journal.qualification_fingerprint != parent.qualification_fingerprint
    ):
        raise ValueError("EVALUATION_QUALIFICATION_MISMATCH")
    truth = {e.observation_id: e for e in journal.entries}
    artifacts = tuple(
        cast(ResearchBaseRateArtifact, store.get("baseline", fp))
        for fp in manifest.baseline_artifacts
    )
    for job, artifact in zip(training.jobs, artifacts, strict=True):
        assert job.artifact is not None
        expected = freeze_baseline(journal, job.fold_id, job.artifact.manifest.fit_cutoff)
        if expected != artifact:
            raise ValueError("BASERATE_RECONSTRUCTION_MISMATCH")
    forecasts = tuple(
        cast(ResearchBaseRateForecast, store.get("baselineforecast", fp))
        for fp in manifest.baseline_forecasts
    )
    forecast_map = {f.observation_id: f for f in forecasts}
    expected_ids = {
        r.request.origin.observation_id for r in records if not r.request.origin.protected
    }
    if set(forecast_map) != expected_ids or len(forecast_map) != len(forecasts):
        raise ValueError("BASELINE_FORECAST_POPULATION_MISMATCH")
    artifact_map = {a.fold: a for a in artifacts}
    pairs, dispositions = [], []
    for r in records:
        o = r.request.origin
        b = forecast_map.get(o.observation_id)
        if b is not None and b != baseline_forecast(
            artifact_map[r.request.fold_id], r.request, b.computed_at
        ):
            raise ValueError("BASELINE_FORECAST_REPLAY_MISMATCH")
        p, d = pair_observation(r, b, truth.get(o.observation_id), manifest.evaluated_at)
        if p is not None:
            pairs.append(p)
        dispositions.append(d)
    return tuple(pairs), tuple(dispositions), journal, parent.research_profile_fingerprint


def evaluate_manifest(
    store: DevelopmentEvaluationStore, manifest: EvaluationManifest
) -> tuple[DevelopmentEvaluation, tuple[PairedObservation, ...], tuple[PopulationDisposition, ...]]:
    start = time.monotonic()
    policy = cast(DevelopmentPolicy, store.get("policy", manifest.policy_fingerprint))
    pairs, dispositions, journal, profile = reconstruct_inputs(store, manifest)
    summaries = tuple(
        summarize(
            str(f),
            tuple(p for p in pairs if p.fold == f),
            tuple(d for d in dispositions if d.fold == f),
        )
        for f in (2021, 2022, 2023, 2024)
    )
    pooled = summarize("POOLED", pairs, dispositions)
    if time.monotonic() - start > 120:
        raise ValueError("COMPARISON_EXECUTION_TIMEOUT")
    report = DevelopmentEvaluation(
        policy=policy,
        input_manifest_fingerprint=cast(str, manifest.fingerprint),
        paired_population_fingerprint=paired_identity(pairs),
        ground_truth_fingerprint=cast(str, journal.fingerprint),
        logistic_run_fingerprint=manifest.logistic_run,
        research_profile_fingerprint=profile,
        summaries=(*summaries, pooled),
        decision=decide(summaries, pooled),
        created_at=manifest.evaluated_at,
    )
    return report, pairs, dispositions


def persist_evaluation(store: DevelopmentEvaluationStore, manifest: EvaluationManifest) -> str:
    manifest_fp = store.put("manifest", manifest)
    report, pairs, dispositions = evaluate_manifest(store, manifest)
    pair_refs = {p.observation_id: store.put("pair", p) for p in pairs}
    shards = tuple(
        store.put(
            "evaluationshard",
            EvaluationShard(
                dispositions=dispositions[i : i + 64],
                pairs=tuple(
                    pair_refs[d.observation_id] for d in dispositions[i : i + 64] if d.paired
                ),
            ),
        )
        for i in range(0, len(dispositions), 64)
    )
    return store.put(
        "ledger",
        EvaluationLedger(
            manifest=manifest_fp,
            shards=shards,
            report=store.put("evaluation", report),
        ),
    )


def verify_evaluation(store: DevelopmentEvaluationStore, ledger_fp: str) -> str:
    try:
        ledger = cast(EvaluationLedger, store.get("ledger", ledger_fp))
        manifest = cast(EvaluationManifest, store.get("manifest", ledger.manifest))
        report, pairs, dispositions = evaluate_manifest(store, manifest)
        stored_pairs: list[PairedObservation] = []
        stored_dispositions: list[PopulationDisposition] = []
        for ref in ledger.shards:
            shard = cast(EvaluationShard, store.get("evaluationshard", ref))
            stored_dispositions.extend(shard.dispositions)
            stored_pairs.extend(
                cast(PairedObservation, store.get("pair", fp)) for fp in shard.pairs
            )
        if (
            tuple(stored_pairs) != pairs
            or tuple(stored_dispositions) != dispositions
            or store.get("evaluation", ledger.report) != report
        ):
            raise ValueError("EVALUATION_RECONSTRUCTION_MISMATCH")
        return "MATCH"
    except (ValueError, OSError, LookupError, AssertionError):
        return "MISMATCH"
