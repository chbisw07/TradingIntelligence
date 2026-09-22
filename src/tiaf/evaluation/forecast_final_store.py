"""Exclusive final execution and read-only captured-closure verification.

The fixed operator custody directory is a trusted local boundary, not a defense
against its owner deleting history. A consumed or interrupted attempt is terminal.
"""

import os
import time
from collections.abc import Callable
from datetime import datetime
from types import MappingProxyType
from typing import Literal, cast

from pydantic import Field

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation.forecast_final_custody import FinalAttempt, FinalProtocolStore
from tiaf.evaluation.forecast_final_outcomes import FinalOutcome, final_outcome
from tiaf.evaluation.forecast_final_protocol import FinalProtocol, final_decision
from tiaf.evaluation.forecast_final_scoring import (
    FinalDisposition,
    FinalEvaluation,
    FinalPair,
    FinalTable,
    pair_final,
    summarize_final,
    summary_evidence,
)
from tiaf.evaluation.forecast_retrospective_contracts import RetrospectiveDataset
from tiaf.forecasting.final_inputs import (
    FinalForecast,
    FinalInput,
    FinalSource,
    capture_source,
    final_inputs,
    infer_final,
)
from tiaf.forecasting.identity import ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.logistic_store import ResearchForecastStore
from tiaf.forecasting.research_contracts import AdjustedFF1FeatureSchema, AdjustedResearchProfile
from tiaf.learning.forecast_artifacts import (
    FifthFoldGrant,
    LogisticArtifact,
    ScalerArtifact,
    SealedResearch,
)
from tiaf.learning.forecast_fifth_preparation import FifthBaseRateState
from tiaf.learning.forecast_fifth_store import FifthHandoff
from tiaf.planner.models import Sha256


class FinalExecution(SealedResearch):
    protocol_fingerprint: Sha256
    authority_document_fingerprint: Sha256
    implementation_pins: tuple[tuple[str, Sha256], ...] = Field(min_length=1)
    created_at: ForecastDateTime
    actual_source: Literal["PINNED_LOCAL_FILE_ONLY"] = "PINNED_LOCAL_FILE_ONLY"
    model_fits: Literal[0] = 0
    scaler_fits: Literal[0] = 0
    network_calls: Literal[0] = 0
    broker_calls: Literal[0] = 0
    post_holdout_refit_allowed: Literal[False] = False


class FinalOpening(SealedResearch):
    protocol_fingerprint: Sha256
    execution_fingerprint: Sha256
    attempt_fingerprint: Sha256
    protected_population_fingerprint: Sha256
    consumed_at: ForecastDateTime
    one_shot_consumed: Literal[True] = True
    retry_allowed: Literal[False] = False


class FinalRowReferences(SealedResearch):
    request: Sha256
    logistic: Sha256
    baseline: Sha256
    truth: Sha256
    pair: Sha256 | None


class FinalShard(SealedResearch):
    rows: tuple[FinalRowReferences, ...] = Field(min_length=1, max_length=64)


class FinalLedger(SealedResearch):
    protocol: Sha256
    execution: Sha256
    opening: Sha256
    source: Sha256
    shards: tuple[Sha256, ...] = Field(min_length=1, max_length=64)
    table: Sha256
    evaluation: Sha256
    completed_at: ForecastDateTime
    state: Literal["COMPLETE"] = "COMPLETE"
    replay: Literal["MATCH"] = "MATCH"


class FinalFailure(SealedResearch):
    execution: Sha256
    occurred_at: ForecastDateTime
    stage: str
    exception_type: str
    state: Literal["CONSUMED_INVALID_NO_RETRY"] = "CONSUMED_INVALID_NO_RETRY"
    scientific_outcome: None = None


class FinalStore(ResearchForecastStore):
    record_types = MappingProxyType(
        {
            "protocol": FinalProtocol,
            "execution": FinalExecution,
            "opening": FinalOpening,
            "attempt": FinalAttempt,
            "model": LogisticArtifact,
            "scaler": ScalerArtifact,
            "baseline": FifthBaseRateState,
            "handoff": FifthHandoff,
            "source": FinalSource,
            "input": FinalInput,
            "forecast": FinalForecast,
            "outcome": FinalOutcome,
            "pair": FinalPair,
            "shard": FinalShard,
            "table": FinalTable,
            "evaluation": FinalEvaluation,
            "ledger": FinalLedger,
            "failure": FinalFailure,
        }
    )

    def sync(self) -> None:
        descriptor = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def validate_artifacts(
    protocol: FinalProtocol,
    model: LogisticArtifact,
    baseline: FifthBaseRateState,
    handoff: FifthHandoff,
    *,
    approved: str,
) -> None:
    """Hard pre-open identity gate, also repeated from captured closure during replay."""
    p = FinalProtocol.model_validate(protocol.model_dump())
    model = LogisticArtifact.model_validate(model.model_dump())
    baseline = FifthBaseRateState.model_validate(baseline.model_dump())
    handoff = FifthHandoff.model_validate(handoff.model_dump())
    g = model.manifest.grant
    if (
        p.fingerprint != approved
        or not p.authorized
        or model.fingerprint != p.model_fingerprint
        or model.reconstruction.scaler.fingerprint != p.scaler_fingerprint
        or baseline.fingerprint != p.baserate_state_fingerprint
        or handoff.fingerprint != p.fifth_handoff_fingerprint
        or model.manifest.observation_order_fingerprint != p.training_population_fingerprint
        or not isinstance(g, FifthFoldGrant)
        or g.fingerprint != p.authority_fingerprint
        or baseline.authority != g
        or baseline.cutoff != p.fifth_cutoff
        or model.manifest.fit_cutoff != p.fifth_cutoff
        or model.manifest.fold_id != 2025
        or baseline.output is None
        or baseline.output.probability != 0.4
        or len(baseline.support) != 20
        or sum(cast(int, r.label) for r in baseline.support) != 8
        or p.research_profile_fingerprint != AdjustedResearchProfile().fingerprint
        or p.feature_schema_fingerprint
        != AdjustedFF1FeatureSchema(profile=AdjustedResearchProfile()).fingerprint
        or any(
            getattr(g, k) != getattr(p, k)
            for k in (
                "qualification_fingerprint",
                "qualification_blob",
                "dataset_fingerprint",
                "research_profile_fingerprint",
                "feature_schema_fingerprint",
                "dependency_lock_fingerprint",
            )
        )
        or handoff.model_artifact_fingerprint != model.fingerprint
        or handoff.scaler_fingerprint != model.reconstruction.scaler.fingerprint
        or handoff.baserate_state_fingerprint != baseline.fingerprint
        or handoff.training_population_fingerprint != p.training_population_fingerprint
        or handoff.authority_fingerprint != p.authority_fingerprint
    ):
        raise ValueError("FINAL_FROZEN_IDENTITY_MISMATCH")


def make_report(
    protocol: FinalProtocol,
    execution: FinalExecution,
    opening: FinalOpening,
    source: FinalSource,
    rows: tuple[FinalRowReferences, ...],
    table: FinalTable,
    at: datetime,
) -> FinalEvaluation:
    summary = summarize_final(protocol, table.pairs, table.dispositions)
    return FinalEvaluation(
        protocol=protocol,
        execution_fingerprint=cast(str, execution.fingerprint),
        opening_fingerprint=cast(str, opening.fingerprint),
        holdout_consumed_at=opening.consumed_at,
        source_fingerprint=cast(str, source.fingerprint),
        ground_truth_fingerprint=semantic_fingerprint(tuple(r.truth for r in rows)),
        paired_population_fingerprint=table.population_fingerprint,
        forecast_population_fingerprint=semantic_fingerprint(
            tuple((r.logistic, r.baseline) for r in rows)
        ),
        summary=summary,
        decision=final_decision(summary_evidence(summary)),
        created_at=at,
    )


def execute_final(
    custody: FinalProtocolStore,
    store: FinalStore,
    protocol: FinalProtocol,
    execution: FinalExecution,
    model: LogisticArtifact,
    baseline: FifthBaseRateState,
    handoff: FifthHandoff,
    context: RetrospectiveDataset,
    read_source: Callable[[], bytes],
    *,
    approved: str,
) -> str:
    """Exactly one durable claim. No recovery or retry after consume_once begins."""
    validate_artifacts(protocol, model, baseline, handoff, approved=approved)
    if (
        execution.protocol_fingerprint != protocol.fingerprint
        or store.count != 0
        or not store.writable
        or custody.protocol(approved) != protocol
        or tuple(custody.root.glob("attempt-*.json"))
    ):
        raise ValueError("FINAL_ALREADY_CONSUMED_OR_BAD_EXECUTION")
    started = time.monotonic()
    stage = "CLAIM"
    store.put("protocol", protocol)
    store.put("execution", execution)
    store.put("model", model)
    store.put("scaler", model.reconstruction.scaler)
    store.put("baseline", baseline)
    store.put("handoff", handoff)
    store.sync()
    try:
        claim = custody.consume_once(approved, approved_protocol=approved)
        store.put("attempt", claim)
        opening = FinalOpening(
            protocol_fingerprint=approved,
            execution_fingerprint=cast(str, execution.fingerprint),
            attempt_fingerprint=cast(str, claim.fingerprint),
            protected_population_fingerprint=cast(str, protocol.population.fingerprint),
            consumed_at=datetime.now(TIAF_TIMEZONE),
        )
        store.put("opening", opening)
        store.sync()  # actual opening time/identity durable before the source callback
        stage = "CAPTURE"
        source = capture_source(
            read_source(),
            protocol,
            claim,
            cast(str, execution.fingerprint),
            context,
            datetime.now(TIAF_TIMEZONE),
        )
        store.put("source", source)
        inputs = final_inputs(protocol, source)
        # Persist ALL outcome-blind forecasts before any Ground Truth projection.
        stage = "FORECAST"
        forecasts = []
        for request in inputs:
            store.put("input", request)
            arms = infer_final(request, context, model, baseline, datetime.now(TIAF_TIMEZONE))
            for arm in arms:
                store.put("forecast", arm)
            forecasts.append(arms)
            if time.monotonic() - started > protocol.policy.campaign_timeout_seconds:
                raise ValueError("FINAL_CAMPAIGN_TIMEOUT")
        store.sync()
        stage = "TRUTH_AND_PAIRS"
        refs, pairs, dispositions = [], [], []
        evaluated_at = datetime.now(TIAF_TIMEZONE)
        for request, (logistic, benchmark) in zip(inputs, forecasts, strict=True):
            truth = final_outcome(protocol, source, request, evaluated_at)
            truth_fp = store.put("outcome", truth)
            pair, disposition = pair_final(
                protocol, request, logistic, benchmark, truth, evaluated_at
            )
            pair_fp = None if pair is None else store.put("pair", pair)
            if pair is not None:
                pairs.append(pair)
            dispositions.append(disposition)
            refs.append(
                FinalRowReferences(
                    request=cast(str, request.fingerprint),
                    logistic=cast(str, logistic.fingerprint),
                    baseline=cast(str, benchmark.fingerprint),
                    truth=truth_fp,
                    pair=pair_fp,
                )
            )
        shards = tuple(
            store.put("shard", FinalShard(rows=tuple(refs[i : i + 64])))
            for i in range(0, len(refs), 64)
        )
        table = FinalTable(pairs=tuple(pairs), dispositions=tuple(dispositions))
        table_fp = store.put("table", table)
        stage = "SCORING"
        report = make_report(
            protocol, execution, opening, source, tuple(refs), table, datetime.now(TIAF_TIMEZONE)
        )
        report_fp = store.put("evaluation", report)
        ledger = FinalLedger(
            protocol=approved,
            execution=cast(str, execution.fingerprint),
            opening=cast(str, opening.fingerprint),
            source=cast(str, source.fingerprint),
            shards=shards,
            table=table_fp,
            evaluation=report_fp,
            completed_at=datetime.now(TIAF_TIMEZONE),
        )
        stage = "CAPTURED_CLOSURE_REPLAY"
        # COMPLETE is published only after full captured reconstruction succeeds.
        verify_closure(FinalStore(store.root), ledger)
        if time.monotonic() - started > protocol.policy.campaign_timeout_seconds:
            raise ValueError("FINAL_CAMPAIGN_TIMEOUT")
        result = store.put("ledger", ledger)
        store.sync()
        return result
    except BaseException as exc:
        # Never erase the claim, even if failure reporting itself cannot be written.
        store.put(
            "failure",
            FinalFailure(
                execution=cast(str, execution.fingerprint),
                occurred_at=datetime.now(TIAF_TIMEZONE),
                stage=stage,
                exception_type=type(exc).__name__,
            ),
        )
        store.sync()
        raise


def verify_closure(store: FinalStore, ledger: FinalLedger) -> None:
    """Only captured blobs; no custody claim, raw source, fit or source reselection."""
    started = time.monotonic()
    protocol = cast(FinalProtocol, store.get("protocol", ledger.protocol))
    execution = cast(FinalExecution, store.get("execution", ledger.execution))
    opening = cast(FinalOpening, store.get("opening", ledger.opening))
    attempt = cast(FinalAttempt, store.get("attempt", opening.attempt_fingerprint))
    source = cast(FinalSource, store.get("source", ledger.source))
    model = cast(LogisticArtifact, store.get("model", protocol.model_fingerprint))
    baseline = cast(FifthBaseRateState, store.get("baseline", protocol.baserate_state_fingerprint))
    handoff = cast(FifthHandoff, store.get("handoff", protocol.fifth_handoff_fingerprint))
    report = cast(FinalEvaluation, store.get("evaluation", ledger.evaluation))
    table = cast(FinalTable, store.get("table", ledger.table))
    validate_artifacts(protocol, model, baseline, handoff, approved=ledger.protocol)
    if (
        store.get("scaler", protocol.scaler_fingerprint) != model.reconstruction.scaler
        or execution.protocol_fingerprint != protocol.fingerprint
        or opening.protocol_fingerprint != protocol.fingerprint
        or attempt.protocol_fingerprint != protocol.fingerprint
        or opening.execution_fingerprint != execution.fingerprint
        or source.execution_fingerprint != execution.fingerprint
        or source.attempt_fingerprint != attempt.fingerprint
        or opening.protected_population_fingerprint != protocol.population.fingerprint
        or not protocol.created_at
        <= execution.created_at
        <= opening.consumed_at
        <= source.captured_at
        <= report.created_at
        <= ledger.completed_at
        or tuple(store.root.glob("failure-*.json"))
    ):
        raise ValueError("FINAL_CLOSURE_IDENTITY_OR_CLOCK")
    refs = tuple(r for fp in ledger.shards for r in cast(FinalShard, store.get("shard", fp)).rows)
    inputs = final_inputs(protocol, source)
    if len(refs) != len(inputs):
        raise ValueError("FINAL_CLOSURE_GRID_MISMATCH")
    pairs: list[FinalPair] = []
    dispositions: list[FinalDisposition] = []
    forecast_clocks: list[datetime] = []
    truth_clocks: list[datetime] = []
    for ref, expected_request in zip(refs, inputs, strict=True):
        q = cast(FinalInput, store.get("input", ref.request))
        lf = cast(FinalForecast, store.get("forecast", ref.logistic))
        bf = cast(FinalForecast, store.get("forecast", ref.baseline))
        truth = cast(FinalOutcome, store.get("outcome", ref.truth))
        if (
            q != expected_request
            or (lf, bf) != infer_final(q, source.context, model, baseline, lf.computed_at)
            or truth != final_outcome(protocol, source, q, truth.evaluation_as_known)
        ):
            raise ValueError("FINAL_PINNED_RECONSTRUCTION_MISMATCH")
        forecast_clocks.extend((lf.computed_at, bf.computed_at))
        truth_clocks.append(truth.evaluation_as_known)
        pair, disposition = pair_final(protocol, q, lf, bf, truth, report.created_at)
        if (pair is None) != (ref.pair is None) or (
            pair is not None and store.get("pair", cast(str, ref.pair)) != pair
        ):
            raise ValueError("FINAL_PAIRED_CAPTURE_MISMATCH")
        if pair is not None:
            pairs.append(pair)
        dispositions.append(disposition)
        if time.monotonic() - started > protocol.policy.campaign_timeout_seconds:
            raise ValueError("FINAL_REPLAY_TIMEOUT")
    expected_table = FinalTable(pairs=tuple(pairs), dispositions=tuple(dispositions))
    if (
        max(forecast_clocks) > min(truth_clocks)
        or table != expected_table
        or report
        != make_report(
            protocol, execution, opening, source, refs, expected_table, report.created_at
        )
    ):
        raise ValueError("FINAL_REPORT_OR_FORECAST_BEFORE_TRUTH_MISMATCH")


def verify_final(store: FinalStore, fingerprint: str) -> str:
    try:
        ledger = cast(FinalLedger, store.get("ledger", fingerprint))
        verify_closure(store, ledger)
        return "MATCH"
    except (ValueError, OSError, LookupError, AssertionError, RuntimeError):
        return "MISMATCH"
