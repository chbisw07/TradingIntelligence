"""FF-0's single local command adapter, not a published TI Shell capability.

Reuse the Shell argparse/argument-safety seam; never its public capability dispatcher.
Operation-specific runtime/labeler imports stay behind explicit verbs.
"""

import argparse
import os
import stat
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Self
from uuid import uuid4

from pydantic import Field, TypeAdapter, ValidationError, model_validator

from tiaf.planner.models import Sha256
from tiaf.shell.errors import ShellError
from tiaf.shell.parser import _Parser, _reject_unsafe_or_repeated_options

from .capture import MAX_RECORD_BYTES, ForecastCapture, strict_json
from .clocks import Clock, SystemClock, read_clock
from .contracts import BinaryProbabilityOutput, ForecastAbsence
from .enums import ForecastStatus
from .errors import ForecastAdmissionError, ForecastIntegrityError, ForecastStoreError
from .identity import ForecastContract, LogicalId, canonical_json, semantic_fingerprint
from .store import ForecastCorpusStore, StoreOwner

HELP = """FF-0 internal synthetic engineering commands (JSON output; no live calls):
  run     --config PATH --input LOGICAL_ID
  outcome --config PATH --input LOGICAL_ID
  link    --config PATH --run RUN_ID --outcome OUTCOME_ID
  inspect --config PATH --run RUN_ID
  replay  --config PATH --run RUN_ID [--verify]
run preserves the input's explicit ACTUAL/SIMULATED mode and cutoff/as-of.
No --mode, --now, production clock override, model path, training or broker operation.
replay is read-only; --verify adds one separately accounted pinned recomputation.
Exit 0: completed operation/domain absence; 2: command/config/admission error;
1: execution/storage/integrity or requested verification failure/unavailability.
--config is required: there is no default corpus, .env discovery or live fallback.
"""


class InputRegistration(ForecastContract):
    input_id: LogicalId
    kind: Literal["FORECAST", "OUTCOME"]
    filename: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,60}\.json$")
    fingerprint: Sha256


class EngineeringConfig(ForecastContract):
    schema_id: Literal["tiaf.ff.engineering-config"] = "tiaf.ff.engineering-config"
    input_root: str = Field(min_length=1, max_length=4096)
    corpus_root: str = Field(min_length=1, max_length=4096)
    inputs: tuple[InputRegistration, ...] = Field(max_length=64)

    @model_validator(mode="after")
    def unique_ids(self) -> Self:
        if len({i.input_id for i in self.inputs}) != len(self.inputs):
            raise ValueError("DUPLICATE_INPUT_REGISTRATION")
        return self


@dataclass(frozen=True)
class EngineeringCommand:
    operation: str
    config: Path
    input_id: str | None = None
    run_id: str | None = None
    outcome_id: str | None = None
    verify: bool = False


class EngineeringAdmissionError(ValueError):
    """Only safe code-owned messages are printed by the outer command adapter."""


def parse_command(tokens: Sequence[str]) -> EngineeringCommand | None:
    if len(tokens) > 16 or any(len(t) > 4096 for t in tokens):
        raise EngineeringAdmissionError("COMMAND_LIMIT")
    _reject_unsafe_or_repeated_options(tokens)
    if not tokens or list(tokens) == ["help"] or "--help" in tokens or "-h" in tokens:
        return None
    parser = _Parser(prog="forecast_miniature", add_help=False, allow_abbrev=False)
    verbs = parser.add_subparsers(dest="operation", required=True)
    for operation in ("run", "outcome", "link", "inspect", "replay"):
        command = verbs.add_parser(operation, add_help=False, allow_abbrev=False)
        command.add_argument("--config", type=Path, required=True)
        if operation in ("run", "outcome"):
            command.add_argument("--input", dest="input_id", required=True)
        else:
            command.add_argument("--run", dest="run_id", required=True)
        if operation == "link":
            command.add_argument("--outcome", dest="outcome_id", required=True)
        if operation == "replay":
            command.add_argument("--verify", action="store_true")
    values = vars(parser.parse_args(list(tokens)))
    for field in ("input_id", "run_id", "outcome_id"):
        if field in values:
            TypeAdapter(LogicalId).validate_python(values[field])
    return EngineeringCommand(**values)


def _safe_path(path: Path) -> Path:
    if ":" in str(path) or ".." in path.parts or str(path).startswith("~"):
        raise EngineeringAdmissionError("UNSAFE_LOCAL_PATH")
    absolute = path.absolute()
    if any(p.is_symlink() for p in (absolute, *absolute.parents)):
        raise EngineeringAdmissionError("SYMLINK_INPUT_DENIED")
    return absolute


def _read_json(path: Path) -> object:
    path = _safe_path(path)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise EngineeringAdmissionError("REGULAR_SINGLE_LINK_INPUT_REQUIRED")
            if info.st_size > MAX_RECORD_BYTES:
                raise EngineeringAdmissionError("INPUT_BYTE_LIMIT")
            content = handle.read(MAX_RECORD_BYTES + 1)
        if len(content) > MAX_RECORD_BYTES:
            raise EngineeringAdmissionError("INPUT_BYTE_LIMIT")
        return strict_json(content.decode("utf-8"))
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise EngineeringAdmissionError("LOCAL_INPUT_INVALID") from exc


def load_config(path: Path) -> tuple[EngineeringConfig, Path, Path]:
    path = _safe_path(path)
    config = EngineeringConfig.model_validate(_read_json(path))
    roots = []
    for value in (config.input_root, config.corpus_root):
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = path.parent / candidate
        roots.append(_safe_path(candidate))
    inputs, corpus = roots
    if inputs.is_relative_to(corpus) or corpus.is_relative_to(inputs):
        raise EngineeringAdmissionError("INPUT_OUTPUT_ROOTS_MUST_BE_DISJOINT")
    return config, inputs, corpus


def _input(config: EngineeringConfig, root: Path, identifier: str, kind: str) -> object:
    registered = next((i for i in config.inputs if i.input_id == identifier), None)
    if registered is None or registered.kind != kind:
        raise EngineeringAdmissionError("INPUT_NOT_REGISTERED_FOR_OPERATION")
    content = _read_json(root / registered.filename)
    if semantic_fingerprint(content) != registered.fingerprint:
        raise ForecastIntegrityError("REGISTERED_INPUT_FINGERPRINT_MISMATCH")
    if not isinstance(content, dict) or content.get("input_id") != identifier:
        raise EngineeringAdmissionError("REGISTERED_INPUT_ID_MISMATCH")
    return content


def _summary(capture: ForecastCapture) -> dict[str, Any]:
    result, request = capture.result, capture.result.request
    inference = result.inference
    return {
        "request_id": request.request_id,
        "run_id": result.run_id,
        "result_id": result.result_id,
        "capture_id": capture.capture_id,
        "status": result.status.value,
        "target": request.target.target_id,
        "target_version": request.target.target_version,
        "subject": request.target.subject.symbol,
        "realization_mode": request.realization_mode.value,
        "data_basis": request.data_basis,
        "information_cutoff": request.information_cutoff,
        "as_of": request.as_of,
        "simulation_as_of": request.simulation_as_of,
        "computed_at": result.computed_at,
        "issued_at": result.issued_at,
        "recorded_at": capture.recorded_at,
        "target_open_time": request.window.target_open_time,
        "target_resolve_time": request.window.target_resolve_time,
        "probability": result.output.probability
        if isinstance(result.output, BinaryProbabilityOutput)
        else None,
        "reasons": result.output.reasons if isinstance(result.output, ForecastAbsence) else (),
        "calibration": result.output.calibration,
        "uncertainty": result.output.uncertainty,
        "validity": result.output.validity,
        "support_count": inference.support.qualified_count
        if inference is not None and inference.support is not None
        else None,
        "forecaster_id": result.artifact_identity.forecaster_id
        if result.artifact_identity
        else None,
        "implementation_version": result.artifact_identity.implementation_version
        if result.artifact_identity
        else None,
        "artifact_ref": result.artifact_identity.artifact if result.artifact_identity else None,
        "configuration_ref": request.configuration_ref,
        "composition_ref": request.profile_ref,
        "evidence_ref": request.evidence_ref,
        "request_fingerprint": request.semantic_fingerprint,
        "fingerprint": result.replay_fingerprint,
        "original_usage": inference.usage if inference is not None else None,
        "source_refs": tuple(s.artifact for s in request.all_evidence),
        "admission": result.admission,
        "authority": result.authority,
        "limitations": result.limitations,
    }


def dispatch(
    command: EngineeringCommand, *, _clock: Clock | None = None
) -> tuple[dict[str, Any], int]:
    """One-shot only; trusted Python clock injection is never exposed as a CLI argument."""
    config, input_root, corpus = load_config(command.config)
    clock = _clock if _clock is not None else SystemClock()
    now = read_clock(clock)
    store = ForecastCorpusStore(corpus, as_of=now)
    if command.operation == "run":
        from .engineering_inputs import ForecastInput
        from .runtime import create_forecast_runtime

        assert command.input_id is not None
        packet = ForecastInput.model_validate(
            _input(config, input_root, command.input_id, "FORECAST")
        )
        runtime = create_forecast_runtime(
            packet.configuration,
            packet.artifact,
            packet.artifacts,
            root=corpus,
            build=packet.build,
            _clock=clock,
        )
        capture = runtime.run(packet.request, packet.snapshot, packet.artifacts)
        return _summary(capture), 1 if capture.result.status is ForecastStatus.FAILED else 0
    if command.operation == "outcome":
        from tiaf.evaluation.forecast_truth import resolve_outcome

        from .capture import references, select_artifacts
        from .engineering_inputs import OutcomeInput

        assert command.input_id is not None
        packet_out = OutcomeInput.model_validate(
            _input(config, input_root, command.input_id, "OUTCOME")
        )
        selected = select_artifacts(
            references(packet_out.model_dump(mode="json", exclude={"artifacts"})),
            packet_out.artifacts,
        )
        entry = resolve_outcome(
            entry_id="ff-outcome:" + uuid4().hex,
            target=packet_out.target,
            window=packet_out.window,
            terminal=packet_out.terminal,
            check_evidence=packet_out.check_evidence,
            evaluated_at=now,
            recorded_at=read_clock(clock),
            closure=tuple(a.blob_reference for a in selected),
        )
        writer = ForecastCorpusStore(corpus, as_of=read_clock(clock), owner=StoreOwner.EVALUATION)
        writer.append_outcome(entry, selected)
        return {
            "outcome_id": entry.entry_id,
            "outcome_key": entry.key,
            "label": entry.label,
            "eligibility": entry.label_eligibility,
            "recorded_at": entry.recorded_at,
            "fingerprint": entry.fingerprint,
        }, 0
    assert command.run_id is not None
    capture = store.get_forecast(command.run_id)
    summary = _summary(capture)
    if command.operation == "link":
        from tiaf.evaluation.forecast_contracts import ForecastLedgerSnapshot
        from tiaf.evaluation.forecast_linkage import link_forecast_outcome

        assert command.outcome_id is not None
        outcome = store.get_outcome(command.outcome_id)
        link = link_forecast_outcome(capture, outcome, created_at=now)
        writer = ForecastCorpusStore(corpus, as_of=now, owner=StoreOwner.EVALUATION)
        writer.append_link(link)
        ledger = ForecastLedgerSnapshot(links=(link,), created_at=now)
        writer.append_ledger(ledger)
        return {
            "run_id": command.run_id,
            "outcome_id": command.outcome_id,
            "link_id": link.link_id,
            "eligibility": link.eligibility,
            "ledger_id": ledger.snapshot_id,
        }, 0
    if command.operation == "inspect":
        summary["links"] = tuple(
            {
                "link_id": link.link_id,
                "outcome_id": link.outcome_ref.artifact_id,
                "eligibility": link.eligibility,
            }
            for link in store.get_forecast_links(command.run_id)
        )
        return summary, 0
    if command.operation != "replay":
        raise EngineeringAdmissionError("UNKNOWN_OPERATION")
    summary["replay"] = "EXACT_RECORDED_MATCH"
    if command.verify:
        from .replay import verify_pinned

        report = verify_pinned(store, command.run_id, _clock=clock)
        summary["verification"] = report
        return summary, 0 if report.status == "VERIFIED" else 1
    return summary, 0


def main(argv: list[str] | None = None) -> int:
    payload: dict[str, Any]
    try:
        command = parse_command(sys.argv[1:] if argv is None else argv)
        if command is None:
            payload, code = {"operation": "help", "message": HELP}, 0
        else:
            result, code = dispatch(command)
            payload = {"operation": command.operation, "result": result}
    except (
        ShellError,
        argparse.ArgumentError,
        EngineeringAdmissionError,
        ForecastAdmissionError,
        ValidationError,
    ):
        payload, code = (
            {
                "error_category": "COMMAND_CONFIG_ADMISSION",
                "message": "Command or trusted local input rejected; see engineering guidance.",
            },
            2,
        )
    except ForecastIntegrityError:
        payload, code = (
            {
                "error_category": "INTEGRITY",
                "message": "Captured identity or history failed validation; no repair performed.",
            },
            1,
        )
    except ForecastStoreError:
        payload, code = (
            {
                "error_category": "PERSISTENCE_ACCESS",
                "message": "Local persistence/access failed; no success or repair claimed.",
            },
            1,
        )
    except Exception:
        payload, code = (
            {
                "error_category": "EXECUTION",
                "message": "Engineering operation failed safely; inspect retained records.",
            },
            1,
        )
    print(
        canonical_json(
            {
                "schema_id": "tiaf.ff.engineering-result",
                "schema_version": "1.0",
                "public_capability": "INTERNAL_ENGINEERING_CLI_ONLY",
                "exit_code": code,
                **payload,
            }
        )
    )
    return code
