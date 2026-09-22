"""Evaluation-owned final Outcome Journal; the forecaster never receives labels.

This is the authorized final-year adapter to the existing research Ground Truth
function, not a new label definition. Every entry retains the source endpoints,
unavailability facets, actual capture clock and simulated session clocks.
"""

from datetime import datetime, timedelta
from typing import Annotated, Literal, cast

from pydantic import Field, StrictInt

from tiaf.evaluation.forecast_final_protocol import FinalProtocol
from tiaf.evaluation.forecast_retrospective import research_direction
from tiaf.forecasting.final_inputs import FinalInput, FinalSource, FinalSourceRow
from tiaf.forecasting.identity import ForecastDateTime
from tiaf.forecasting.research_contracts import AdjustedResearchProfile
from tiaf.learning.forecast_artifacts import SealedResearch
from tiaf.planner.models import Sha256


class FinalOutcome(SealedResearch):
    common_request_fingerprint: Sha256
    protocol_fingerprint: Sha256
    execution_fingerprint: Sha256
    source_fingerprint: Sha256
    label_policy: Literal["QUALIFIED_ADJUSTED_ENDPOINT_DIRECTION"] = (
        "QUALIFIED_ADJUSTED_ENDPOINT_DIRECTION"
    )
    revision: Literal[0] = 0
    reference: FinalSourceRow | None
    terminal: FinalSourceRow | None
    label: Annotated[StrictInt, Field(ge=0, le=1)] | None
    assumed_label_available_at: ForecastDateTime | None
    reasons: tuple[str, ...]
    evaluation_as_known: ForecastDateTime


def final_outcome(
    protocol: FinalProtocol, source: FinalSource, request: FinalInput, at: datetime
) -> FinalOutcome:
    if (
        request.protocol_fingerprint != protocol.fingerprint
        or request.execution_fingerprint != source.execution_fingerprint
        or at < source.captured_at
        or (request.target_closes_at is not None and at < request.target_closes_at)
    ):
        raise ValueError("FINAL_TRUTH_IDENTITY_OR_CLOCK")
    rows = {r.session_date: r for r in source.rows}
    ref, target = request.slot.reference_date, request.slot.target_date
    first, last = rows.get(ref), None if target is None else rows.get(target)
    reasons = []
    label = None
    if any(
        not a.provider_adjustment_supported and ref < a.boundary <= target
        for a in source.context.actions
        if target is not None
    ):
        reasons.append("LABEL_UNSUPPORTED_ACTION")
    elif first is None or last is None:
        reasons.append("TARGET_UNAVAILABLE")
    else:
        try:
            label = research_direction(
                first.close,
                last.close,
                reference_basis=protocol.price_basis,
                terminal_basis=protocol.price_basis,
                profile=AdjustedResearchProfile(),
            )
        except ValueError as exc:
            reasons.append(str(exc))
    return FinalOutcome(
        common_request_fingerprint=cast(str, request.fingerprint),
        protocol_fingerprint=protocol.fingerprint,
        execution_fingerprint=source.execution_fingerprint,
        source_fingerprint=cast(str, source.fingerprint),
        reference=first,
        terminal=last,
        label=label,
        assumed_label_available_at=None
        if label is None or request.target_closes_at is None
        else request.target_closes_at + timedelta(minutes=30),
        reasons=tuple(reasons),
        evaluation_as_known=at,
    )
