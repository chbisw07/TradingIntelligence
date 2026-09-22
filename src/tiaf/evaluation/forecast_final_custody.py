"""Outcome-blind freeze review and durable one-shot custody; no final scorer.

The fixed operator corpus is trusted local custody, not an adversarial security
boundary. Deleting/copying it to reset authority is forbidden. A failed consumed
attempt is terminal. This module never calls a protected-data reader.
"""

import json
import os
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Literal, cast

from tiaf.evaluation.forecast_comparison import DevelopmentEvaluation
from tiaf.evaluation.forecast_comparison_store import (
    DevelopmentEvaluationStore,
    EvaluationLedger,
    EvaluationManifest,
    verify_evaluation,
)
from tiaf.evaluation.forecast_final_protocol import FinalPopulation, FinalProtocol, FinalSlot
from tiaf.forecasting.identity import canonical_json
from tiaf.forecasting.logistic_forecasts import LogisticForecastRun
from tiaf.forecasting.logistic_projection import object_spans
from tiaf.forecasting.logistic_store import ResearchForecastStore
from tiaf.learning.forecast_artifacts import FifthFoldGrant, SealedResearch
from tiaf.learning.forecast_fifth_preparation import FifthBaseRateState, _objects
from tiaf.learning.forecast_fifth_store import FifthHandoff, FifthStore, verify_fifth
from tiaf.learning.forecast_jobs import TrainingRun
from tiaf.learning.forecast_training import read_bounded
from tiaf.planner.models import Sha256


def final_grid(path: Path, blob: str, qualification: str) -> FinalPopulation:
    """Decode exactly IDs/dates/context and nothing derived from protected values."""
    raw = read_bounded(path)
    if sha256(raw).hexdigest() != blob:
        raise ValueError("FINAL_GRID_BYTE_PIN")
    top = object_spans(raw.decode().strip())
    if json.loads(top["fingerprint"]) != qualification:
        raise ValueError("FINAL_GRID_QUALIFICATION_PIN")
    slots = []
    for fields in _objects(top["observations"]):
        ref = date.fromisoformat(json.loads(fields["reference_date"]))
        if ref.year == 2025:
            slots.append(
                FinalSlot.model_validate(
                    {
                        "observation_id": json.loads(fields["observation_id"]),
                        "reference_date": ref,
                        "target_date": json.loads(fields["target_date"]),
                    }
                )
            )
    folds = [f for f in _objects(top["folds"]) if json.loads(f["test_year"]) == 2025]
    if len(folds) != 1 or tuple(s.observation_id for s in slots) != tuple(
        json.loads(folds[0]["test_ids"])
    ):
        raise ValueError("FINAL_GRID_QUALIFIED_MEMBERSHIP")
    return FinalPopulation(
        qualification_blob=blob,
        qualification_fingerprint=qualification,
        context_fingerprint=json.loads(top["context_fingerprint"]),
        slots=tuple(slots),
    )


def review_handoffs(
    fifth: FifthStore,
    handoff_fp: str,
    development: DevelopmentEvaluationStore,
    ledger_fp: str,
    evaluation_fp: str,
) -> FifthHandoff:
    """Both captured closures only; never a qualification/raw-price outcome read."""
    if verify_fifth(fifth, handoff_fp) != "MATCH":
        raise ValueError("FINAL_FIFTH_REPLAY_FAILED")
    h = cast(FifthHandoff, fifth.get("handoff", handoff_fp))
    a = cast(FifthFoldGrant, fifth.get("authority", h.authority_fingerprint))
    b = cast(FifthBaseRateState, fifth.get("baseline", h.baserate_state_fingerprint))
    if (
        len(b.support) != 20
        or sum(cast(int, e.label) for e in b.support) != 8
        or b.output is None
        or b.output.probability != 0.4
    ):
        raise ValueError("FINAL_BASELINE_NOT_EIGHT_OF_TWENTY")
    if verify_evaluation(development, ledger_fp) != "MATCH":
        raise ValueError("FINAL_DEVELOPMENT_REPLAY_FAILED")
    ledger = cast(EvaluationLedger, development.get("ledger", ledger_fp))
    report = cast(DevelopmentEvaluation, development.get("evaluation", ledger.report))
    manifest = cast(EvaluationManifest, development.get("manifest", ledger.manifest))
    # Validate the run's unchanged lineage without reading original qualification.
    run = cast(LogisticForecastRun, development.get("run", manifest.logistic_run))
    grant = cast(TrainingRun, development.get("training", run.training_run_fingerprint)).grant
    if (
        ledger.report != evaluation_fp
        or report.decision.support_failures
        or report.decision.stability_failures
        or report.decision.classification != "INSUFFICIENT_EVIDENCE"
        or report.summaries[-1].n != 969
        or report.research_profile_fingerprint != h.research_profile_fingerprint
        or manifest.protocol_document_sha256 != a.protocol_fingerprint
        or any(
            getattr(grant, field) != getattr(a, field)
            for field in (
                "qualification_fingerprint",
                "dataset_fingerprint",
                "research_profile_fingerprint",
                "feature_schema_fingerprint",
                "dependency_lock_fingerprint",
            )
        )
    ):
        raise ValueError("FINAL_DEVELOPMENT_OR_LINEAGE_NOT_ACCEPTED")
    return h


class FinalAttempt(SealedResearch):
    """Deterministic durable claim, consumed before any protected source decoding."""

    experiment_id: Literal["ff1.reliance.daily_logistic_vs_b0/1.0"] = (
        "ff1.reliance.daily_logistic_vs_b0/1.0"
    )
    protocol_fingerprint: Sha256
    executions_consumed: Literal[1] = 1
    consumed_before_outcome_access: Literal[True] = True
    retry_allowed: Literal[False] = False
    post_holdout_refit_allowed: Literal[False] = False


class FinalProtocolStore(ResearchForecastStore):
    record_types = MappingProxyType({"protocol": FinalProtocol, "attempt": FinalAttempt})

    def put(self, kind: str, value: SealedResearch) -> str:
        if kind != "protocol":
            raise ValueError("FINAL_ATTEMPT_REQUIRES_EXCLUSIVE_CONSUMPTION")
        existing = tuple(self.root.glob("protocol-*.json"))
        if existing or tuple(self.root.glob("attempt-*.json")):
            raise ValueError("FINAL_PROTOCOL_ALREADY_FROZEN")
        return super().put(kind, value)

    def protocol(self, fingerprint: str) -> FinalProtocol:
        paths = tuple(self.root.glob("protocol-*.json"))
        if paths != (self._path("protocol", fingerprint),):
            raise ValueError("FINAL_EXACT_FROZEN_PROTOCOL_REQUIRED")
        return cast(FinalProtocol, self.get("protocol", fingerprint))

    def consume_once(self, fingerprint: str, *, approved_protocol: str) -> FinalAttempt:
        """Future execution seam; deliberately not exposed by the freeze-review CLI.

        Caller must complete preflight and explicitly supply the approved pin.
        No outcome reader is invoked here. Once returned (or a write fails), no
        retry is permitted; a future runner must capture its failure/completion.
        """
        p = self.protocol(fingerprint)
        if not p.authorized or approved_protocol != fingerprint:
            raise ValueError("FINAL_EXECUTION_NOT_AUTHORIZED")
        if tuple(self.root.glob("attempt-*.json")):
            raise ValueError("FINAL_EXECUTION_ALREADY_CONSUMED")
        claim = FinalAttempt(protocol_fingerprint=fingerprint)
        path = self._path("attempt", cast(str, claim.fingerprint))
        with path.open("xb") as handle:
            handle.write((canonical_json(claim) + "\n").encode())
            handle.flush()
            os.fsync(handle.fileno())
        # Persist directory entry before handing control to any future reader.
        descriptor = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        if self.get("attempt", cast(str, claim.fingerprint)) != claim:
            raise ValueError("FINAL_ATTEMPT_PERSISTENCE_FAILED_NO_RETRY")
        return claim


def assemble_protocol(
    h: FifthHandoff,
    a: FifthFoldGrant,
    population: FinalPopulation,
    *,
    ledger_fp: str,
    evaluation_fp: str,
    review_document_fp: str,
    provisioning_review_fp: str,
    source_pins: tuple[tuple[str, str], ...],
    created_at: datetime,
) -> FinalProtocol:
    """Data-only assembly after review_handoffs. No source acquisition or fitting."""
    if (
        h.authority_fingerprint != a.fingerprint
        or h.qualification_fingerprint != population.qualification_fingerprint
        or a.qualification_blob != population.qualification_blob
        or created_at < h.created_at
    ):
        raise ValueError("FINAL_FREEZE_LINEAGE")
    return FinalProtocol(
        development_evaluation_fingerprint=evaluation_fp,
        development_ledger_fingerprint=ledger_fp,
        fifth_handoff_fingerprint=cast(str, h.fingerprint),
        scaler_fingerprint=h.scaler_fingerprint,
        model_fingerprint=h.model_artifact_fingerprint,
        training_population_fingerprint=h.training_population_fingerprint,
        authority_fingerprint=h.authority_fingerprint,
        baserate_state_fingerprint=h.baserate_state_fingerprint,
        qualification_fingerprint=h.qualification_fingerprint,
        qualification_blob=a.qualification_blob,
        dataset_fingerprint=h.dataset_fingerprint,
        research_profile_fingerprint=h.research_profile_fingerprint,
        feature_schema_fingerprint=a.feature_schema_fingerprint,
        dependency_lock_fingerprint=h.dependency_lock_fingerprint,
        plan_document_fingerprint=a.protocol_fingerprint,
        review_document_fingerprint=review_document_fp,
        provisioning_review_fingerprint=provisioning_review_fp,
        source_pins=source_pins,
        population=population,
        authorized=True,
        created_at=created_at,
    )
