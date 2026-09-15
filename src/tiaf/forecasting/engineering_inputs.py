"""Declarative engineering input packets; never imported by recorded replay/help."""

from typing import Literal

from pydantic import Field

from tiaf.evaluation.forecast_contracts import (
    EvidenceReference,
    ForecastTargetSpec,
    ForecastWindow,
    QualifiedCloseObservation,
)

from .capture import MAX_ARTIFACTS, CapturedArtifact, ForecastEvidenceSnapshot
from .contracts import ForecastRequest
from .identity import ForecastContract, LogicalId
from .runtime_contracts import ColdForecastConfig
from .support import BaseRateArtifact


class ForecastInput(ForecastContract):
    schema_id: Literal["tiaf.ff.engineering-forecast-input"] = "tiaf.ff.engineering-forecast-input"
    input_id: LogicalId
    configuration: ColdForecastConfig
    artifact: BaseRateArtifact
    request: ForecastRequest
    snapshot: ForecastEvidenceSnapshot
    artifacts: tuple[CapturedArtifact, ...] = Field(max_length=MAX_ARTIFACTS)
    build: CapturedArtifact


class OutcomeInput(ForecastContract):
    schema_id: Literal["tiaf.ff.engineering-outcome-input"] = "tiaf.ff.engineering-outcome-input"
    input_id: LogicalId
    target: ForecastTargetSpec
    window: ForecastWindow
    terminal: QualifiedCloseObservation | None
    check_evidence: tuple[EvidenceReference, ...] = Field(min_length=1, max_length=64)
    artifacts: tuple[CapturedArtifact, ...] = Field(max_length=MAX_ARTIFACTS)
