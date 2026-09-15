"""Authored capture/terminal fixtures; no count calculation or empirical data."""

from decimal import Decimal
from typing import Any

from tiaf.data.models import OHLCVBar
from tiaf.evaluation.forecast_contracts import OutcomeJournalEntry, QualifiedCloseObservation
from tiaf.evaluation.forecast_truth import resolve_outcome
from tiaf.forecasting.capture import (
    CapturedArtifact,
    ForecastCapture,
    ForecastEvidenceSnapshot,
    capture_artifact,
    capture_roots,
    references,
)
from tiaf.forecasting.contracts import ForecastResult
from tiaf.forecasting.identity import ArtifactReference, CapturedBlobReference
from tiaf.forecasting.store import outcome_roots

from ._support import bar, instant, result, source


def subset(
    roots: tuple[ArtifactReference, ...], blobs: tuple[CapturedArtifact, ...]
) -> tuple[CapturedArtifact, ...]:
    mapping = {blob.reference: blob for blob in blobs}
    selected: dict[ArtifactReference, CapturedArtifact] = {}

    def visit(ref: ArtifactReference) -> None:
        if ref in selected:
            return
        item = mapping[ref]
        selected[ref] = item
        for child in item.dependencies:
            visit(child)

    for ref in roots:
        visit(ref)
    return tuple(sorted(selected.values(), key=lambda x: x.blob_reference.blob_hash))


def closure(blobs: tuple[CapturedArtifact, ...]) -> tuple[CapturedBlobReference, ...]:
    return tuple(sorted((blob.blob_reference for blob in blobs), key=lambda r: r.blob_hash))


def packet(
    *, simulated: bool = False, number: int = 1
) -> tuple[ForecastCapture, tuple[CapturedArtifact, ...]]:
    original = result(simulated=simulated)
    blobs: dict[str, CapturedArtifact] = {}
    for ref in references(original):
        source_payload: object = {
            "synthetic_contract_specimen": ref.artifact_id,
            "executable": False,
        }
        if ref.artifact_id == "fixture:bar":
            source_payload = bar()
        elif ref.artifact_id in ("fixture:calendar-v1", "fixture:schedule"):
            source_payload = {
                "synthetic_sessions": [
                    s.model_dump(mode="json") for s in original.request.window.schedule.sessions
                ]
            }
        elif ref.artifact_id == "fixture:close":
            source_payload = {"synthetic_completed_close": "105", "session": "session:s20"}
        elif ref.artifact_id == "fixture:action-coverage":
            source_payload = {"synthetic_action_coverage": "UNAFFECTED", "sessions": ["s20", "s21"]}
        blobs[ref.artifact_id] = capture_artifact(ref.artifact_id, source_payload)

    def replace_refs(value: Any) -> Any:
        if isinstance(value, dict):
            if {"artifact_id", "artifact_version", "fingerprint"} <= value.keys():
                return blobs[value["artifact_id"]].reference.model_dump(mode="json")
            return {key: replace_refs(item) for key, item in value.items()}
        if isinstance(value, list):
            return [replace_refs(item) for item in value]
        return value

    payload = replace_refs(original.model_dump(mode="json", exclude={"replay_fingerprint"}))
    mode = "simulated" if simulated else "actual"
    payload["run_id"], payload["result_id"] = (
        f"ff-run:{mode}-{number}",
        f"ff-result:{mode}-{number}",
    )
    specimen = ForecastResult.model_validate(payload)
    snapshot = ForecastEvidenceSnapshot(
        window=specimen.request.window, history=(bar(),), sources=specimen.request.evidence
    )
    evidence = capture_artifact(specimen.request.evidence_ref.artifact_id, snapshot)
    blobs[evidence.reference.artifact_id] = evidence
    payload["request"]["evidence_ref"] = evidence.reference.model_dump(mode="json")
    specimen = ForecastResult.model_validate(payload)
    build = capture_artifact("fixture:capture-build", {"build": "synthetic-ff0.2-v1"})
    versions = capture_artifact(
        "fixture:dependency-versions", {"serializer": "tiaf.ff.canonical-json/1.0"}
    )
    blobs[build.reference.artifact_id], blobs[versions.reference.artifact_id] = build, versions
    all_blobs = tuple(blobs.values())
    capture = ForecastCapture(
        result=specimen,
        snapshot=snapshot,
        build_ref=build.reference,
        dependency_versions_ref=versions.reference,
        closure=closure(all_blobs),
        recorded_at=instant(8) if simulated else instant(4, 16, 8),
    )
    selected = subset(capture_roots(capture), all_blobs)
    return capture, selected


def outcome_packet(
    capture: ForecastCapture,
    forecast_blobs: tuple[CapturedArtifact, ...],
    *,
    price: Decimal | None = Decimal("106"),
    revision: int = 0,
    previous: OutcomeJournalEntry | None = None,
    day: int = 5,
    evaluated_hour: int = 16,
    invalidation: str = "NONE",
) -> tuple[OutcomeJournalEntry, tuple[CapturedArtifact, ...]]:
    blobs = list(forecast_blobs)
    terminal: QualifiedCloseObservation | None = None
    if price is not None:
        quote = float(price)
        candle = OHLCVBar.model_validate(
            {
                **bar().model_dump(mode="json"),
                "start_at": instant(5, 9, 15),
                "end_at": instant(5, 15, 30),
                "open": quote,
                "close": quote,
                "high": quote + 1,
                "low": max(0.01, quote - 1),
            }
        )
        candle_blob = capture_artifact(f"fixture:terminal-bar-r{revision}", candle)
        source_blob = capture_artifact(
            f"fixture:terminal-source-r{revision}",
            {"synthetic_close": str(price), "session": "session:s21"},
        )
        blobs.extend((candle_blob, source_blob))
        proof = source("terminal", day).model_dump(mode="json")
        proof["artifact"] = source_blob.reference.model_dump(mode="json")
        proof["observed_at"] = instant(5, 15, 30)
        terminal = QualifiedCloseObservation.model_validate(
            {
                **capture.snapshot.window.reference.model_dump(mode="json"),
                "observation_id": f"observation:terminal-r{revision}",
                "session_id": "session:s21",
                "observed_at": instant(5, 15, 30),
                "value": str(price),
                "source": proof,
                "bar_ref": candle_blob.reference,
            }
        )
    check_blob = capture_artifact(
        f"fixture:outcome-check-r{revision}-{day}-{evaluated_hour}",
        {
            "synthetic_check": "missing" if price is None else "present",
            "invalidation": invalidation,
        },
    )
    blobs.append(check_blob)
    check = source("check", day).model_dump(mode="json")
    check.update(
        {
            "artifact": check_blob.reference,
            "observed_at": None,
            "published_at": None,
            "available_at": instant(day, evaluated_hour),
            "acquired_at": instant(day, evaluated_hour),
            "admitted_at": instant(day, evaluated_hour),
        }
    )
    proof_check = type(source("check")).model_validate(check)
    entry = resolve_outcome(
        entry_id=f"outcome:synthetic-r{revision}",
        target=capture.result.request.target,
        window=capture.snapshot.window,
        terminal=terminal,
        check_evidence=(proof_check,),
        evaluated_at=instant(day, evaluated_hour),
        recorded_at=instant(day, evaluated_hour, 1),
        closure=closure(tuple(blobs)),
        revision=revision,
        predecessor=previous.reference if previous else None,
        revision_reason="revision:source-correction" if previous else None,
        invalidation=invalidation,
        invalidation_evidence=(proof_check,) if invalidation != "NONE" else (),
    )
    selected = subset(outcome_roots(entry), tuple(blobs))
    data = entry.model_dump(mode="json", exclude={"fingerprint"})
    data["closure"] = [item.model_dump(mode="json") for item in closure(selected)]
    return OutcomeJournalEntry.model_validate(data), selected
