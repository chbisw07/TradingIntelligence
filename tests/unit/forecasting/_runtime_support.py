"""Explicit synthetic counts/sources, no learned fit, provider or calendar inference."""

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data.models import OHLCVBar
from tiaf.evaluation.forecast_contracts import (
    EvidenceReference,
    ForecastTargetSpec,
    ForecastWindow,
    QualifiedCloseObservation,
    QualifiedSessionSchedule,
    SessionRecord,
)
from tiaf.forecasting.capture import CapturedArtifact, ForecastEvidenceSnapshot, capture_artifact
from tiaf.forecasting.contracts import (
    ForecastComposition,
    ForecastNode,
    ForecastRequest,
    ForecastRoot,
)
from tiaf.forecasting.enums import (
    DataBasis,
    ForecastRealizationMode,
    KnowledgeBasis,
    QualificationStatus,
)
from tiaf.forecasting.forecasters import implementation_artifacts
from tiaf.forecasting.runtime_contracts import ColdForecastConfig, SimulationProfile
from tiaf.forecasting.support import BaseRateArtifact, HistoricalTransition

from ._support import instant, subject


class FixedClock:
    def __init__(self, at: datetime, *, step: float = 0.01) -> None:
        self.at, self.step, self.tick = at, step, 0.0

    def now(self) -> datetime:
        return self.at

    def monotonic(self) -> float:
        self.tick += self.step
        return self.tick


@dataclass(frozen=True)
class RuntimeFixture:
    config: ColdForecastConfig
    artifact: BaseRateArtifact
    blobs: tuple[CapturedArtifact, ...]
    snapshot: ForecastEvidenceSnapshot
    request: ForecastRequest
    build: CapturedArtifact


def fixture(
    *,
    simulated: bool = True,
    included: int = 20,
    pattern: str = "baseline",
    late_label: bool = False,
    late_acquisition: bool = False,
) -> RuntimeFixture:
    manifest = json.loads(
        (Path(__file__).parents[2] / "fixtures/forecasting/ff0/runtime_cases.json").read_text()
    )
    dates = manifest["sessions"]
    prices = [Decimal(x) for x in manifest["close_strings"]]
    if pattern == "zero":
        prices = [Decimal(100)] * 21
    elif pattern == "one":
        prices = [Decimal(100 + i) for i in range(21)]
    blobs: list[CapturedArtifact] = []

    def add(name: str, payload: object) -> CapturedArtifact:
        blob = capture_artifact("fixture-runtime:" + name, payload)
        blobs.append(blob)
        return blob

    def when(index: int, hour: int, minute: int) -> datetime:
        return datetime.fromisoformat(dates[index]).replace(
            hour=hour, minute=minute, tzinfo=TIAF_TIMEZONE
        )

    known = datetime(2026, 1, 5, 16, tzinfo=TIAF_TIMEZONE)

    def source(
        blob: CapturedArtifact, available: datetime = known, observed: datetime | None = None
    ) -> EvidenceReference:
        return EvidenceReference(
            artifact=blob.reference,
            source_id="source:synthetic",
            origin_id="origin:synthetic",
            document_version_id="document:" + blob.reference.artifact_id,
            data_basis=DataBasis.SYNTHETIC_FIXTURE,
            observed_at=observed,
            published_at=available,
            available_at=available,
            acquired_at=instant(8) if late_acquisition else available,
            admitted_at=instant(8) if late_acquisition else available,
        )

    schedule_blob = add(
        "calendar",
        {
            "synthetic_dates": dates,
            "complete": True,
            "excluded_notice": "authored-not-exchange-certified",
        },
    )
    schedule_policy = add("calendar-policy", {"policy": "supplied-adjacent-complete-only"})
    schedule = QualifiedSessionSchedule(
        calendar_ref=schedule_blob.reference,
        coverage_start=when(0, 9, 15),
        coverage_end=when(24, 15, 30),
        sessions=tuple(
            SessionRecord(
                session_id=f"session:s{i:02d}",
                opens_at=when(i, 9, 15),
                closes_at=when(i, 15, 30),
                subject_eligible=True,
            )
            for i in range(25)
        ),
        complete=True,
        qualification=QualificationStatus.QUALIFIED,
        qualification_policy_ref=schedule_policy.reference,
        source=source(schedule_blob),
    )
    action_source = source(
        add("action-coverage", {"synthetic_coverage": "UNAFFECTED", "sessions": dates})
    )
    target = ForecastTargetSpec(
        subject=subject(),
        labeler_ref=add("labeler", {"rule": "terminal>reference"}).reference,
        qualification_policy_ref=add(
            "price-policy", {"rule": "positive-exact-unadjusted-final"}
        ).reference,
    )
    closes: list[QualifiedCloseObservation] = []
    bars: list[OHLCVBar] = []
    for i, price in enumerate(prices):
        bar = OHLCVBar(
            instrument=subject(),
            interval="1d",
            start_at=when(i, 9, 15),
            end_at=when(i, 15, 30),
            open=float(price),
            high=float(price) + 1,
            low=float(price) - 1,
            close=float(price),
            source_provider="synthetic",
            volume=0,
        )
        bars.append(bar)
        bar_blob = add(f"bar-s{i:02d}-{pattern}", bar)
        fact = add(f"close-s{i:02d}-{pattern}", {"synthetic_exact_close": str(price)})
        closes.append(
            QualifiedCloseObservation(
                observation_id=f"observation:close-s{i:02d}",
                subject=subject(),
                session_id=f"session:s{i:02d}",
                observed_at=when(i, 15, 30),
                value=price,
                source=source(fact, when(i, 15, 35), when(i, 15, 30)),
                bar_ref=bar_blob.reference,
                qualification=QualificationStatus.QUALIFIED,
                final=True,
                precision="SOURCE_DECIMAL",
                action_coverage="UNAFFECTED",
                action_coverage_ref=action_source,
            )
        )
    rows = []
    for i in range(20):
        present = i < included
        label = int(prices[i + 1] > prices[i]) if present else None
        available = instant(5) if late_label and i == 19 else when(i + 1, 15, 36)
        use = present and not (late_label and i == 19)
        label_blob = add(
            f"label-{i:02d}-{pattern}-{included}-{late_label}",
            {
                "label": label,
                "reference_session": f"session:s{i:02d}",
                "terminal_session": f"session:s{i + 1:02d}",
                "revision": 0,
            },
        )
        rows.append(
            HistoricalTransition(
                reference_session_id=f"session:s{i:02d}",
                terminal_session_id=f"session:s{i + 1:02d}",
                reference=closes[i] if present else None,
                terminal=closes[i + 1] if present else None,
                label=label,
                label_source=source(
                    label_blob, available, when(i + 1, 15, 30) if present else None
                ),
                label_available_at=available if present else None,
                included=use,
                exclusion_reasons=()
                if use
                else ("support:future-availability" if present else "support:missing-label",),
            )
        )
    code, policy, descriptor = implementation_artifacts()
    artifact = BaseRateArtifact(
        artifact_id=f"artifact:baserate-{pattern}-{included}-{late_label}-{simulated}",
        target=target,
        configuration_ref=policy.reference,
        code_ref=code.reference,
        schedule=schedule,
        selection_evidence=(
            source(
                add("universe", {"synthetic_subject": "RELIANCE", "selection": "fixed-engineering"})
            ),
        ),
        fit_knowledge_cutoff=instant(4, 15, 45),
        prepared_at=instant(8) if simulated else instant(4, 15, 50),
        rows=tuple(rows),
        positive_count=sum(r.label == 1 for r in rows if r.included),
        eligible_count=sum(r.included for r in rows),
    )
    mode = (
        ForecastRealizationMode.SIMULATED_ISSUANCE
        if simulated
        else ForecastRealizationMode.ACTUAL_ISSUANCE
    )
    graph = ForecastComposition(
        composition_id=f"composition:baserate-{pattern}-{included}-{late_label}-{simulated}",
        nodes=(
            ForecastNode(
                node_id="node:baserate", artifact_ref=artifact.reference, realization_mode=mode
            ),
        ),
        roots=(ForecastRoot(root_id="root:benchmark", node_id="node:baserate"),),
        policy_ref=add(
            "singleton-policy", {"nodes": 1, "edges": 0, "role": "BENCHMARK", "primary_roots": 0}
        ).reference,
    )
    sim = (
        add("simulation-profile", SimulationProfile(profile_id="simulation:synthetic"))
        if simulated
        else None
    )
    config = ColdForecastConfig(
        profile_id=f"profile:baserate-{pattern}-{included}-{late_label}-{simulated}",
        forecaster_id="forecaster:historical-base-rate",
        implementation_version="1.0",
        target=target,
        composition=graph,
        descriptor_ref=descriptor.reference,
        simulation_profile_ref=sim.reference if sim else None,
    )
    window = ForecastWindow(
        schedule=schedule,
        reference=closes[-1],
        target_session_id="session:s21",
        target_open_time=when(21, 9, 15),
        target_resolve_time=when(21, 15, 30),
        outcome_due_at=when(22, 9, 15),
        maturation_policy_ref=add("maturation", {"due": "S22-open"}).reference,
    )
    evidence = (source(add("input-qualification", {"basis": "synthetic-reference-window"})),)
    snapshot = ForecastEvidenceSnapshot(window=window, history=(bars[-1],), sources=evidence)
    request = ForecastRequest(
        request_id=f"ff-request:{pattern}-{included}-{late_label}-{simulated}",
        target=target,
        window=window,
        realization_mode=mode,
        information_cutoff=instant(4),
        as_of=instant(4, 16, 5),
        knowledge_basis=KnowledgeBasis.QUALIFIED_HISTORICAL_AVAILABILITY
        if late_acquisition
        else KnowledgeBasis.CAPTURED_AS_KNOWN,
        evidence_ref=capture_artifact(
            f"input:runtime-{pattern}-{included}-{late_label}", snapshot
        ).reference,
        evidence=evidence,
        profile_ref=capture_artifact(graph.composition_id, graph).reference,
        configuration_ref=capture_artifact(config.profile_id, config).reference,
        simulation_profile_ref=sim.reference if sim else None,
    )
    build = add("runtime-build", {"synthetic_build": "ff0.3-test", "executable": False})
    return RuntimeFixture(config, artifact, tuple(blobs), snapshot, request, build)
