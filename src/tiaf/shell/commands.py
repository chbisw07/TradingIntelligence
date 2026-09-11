"""Closed typed command vocabulary shared by one-shot and REPL execution."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from tiaf.context import AnalysisPurpose
from tiaf.contracts import Horizon
from tiaf.contracts.common import TiafDateTime


class ShellOutputMode(StrEnum):
    HUMAN = "human"
    JSON = "json"


class LastView(StrEnum):
    SUMMARY = "summary"
    REASONS = "reasons"
    GAPS = "gaps"
    CONTRADICTIONS = "contradictions"
    EVIDENCE = "evidence"


class TraceView(StrEnum):
    ALL = "all"
    COST = "cost"
    EVIDENCE = "evidence"
    TIMING = "timing"


class OperationKind(StrEnum):
    BASELINE_ASSESS = "baseline.assess"
    OPPORTUNITY_ASSEMBLE = "opportunity.assemble"
    A4_INPUT_PROJECT = "a4_input.project"
    A4_EVALUATE = "a4.evaluate"
    REPLAY_RECORDED = "replay.recorded"
    REPLAY_VERIFY = "replay.verify"


class ContextField(StrEnum):
    SUBJECT = "subject"
    HORIZON = "horizon"
    OBJECTIVE = "objective"
    AS_OF = "as-of"
    PROFILE_REF = "profile-ref"
    AUTHORITY_REF = "authority-ref"
    POSITION_CONTEXT_REF = "position-context-ref"
    OUTPUT = "output"


@dataclass(frozen=True, slots=True)
class ScopeOptions:
    subject: str | None = None
    objective: AnalysisPurpose | None = None
    horizon: Horizon | None = None
    as_of: TiafDateTime | None = None
    profile_ref: str | None = None
    authority_ref: str | None = None
    position_context_ref: str | None = None


@dataclass(frozen=True, slots=True)
class HelpCommand:
    topic: str | None = None


@dataclass(frozen=True, slots=True)
class UseCommand:
    subject: str


@dataclass(frozen=True, slots=True)
class SetCommand:
    field: ContextField
    value: str


@dataclass(frozen=True, slots=True)
class UnsetCommand:
    field: ContextField


@dataclass(frozen=True, slots=True)
class ClearContextCommand:
    pass


@dataclass(frozen=True, slots=True)
class ShowContextCommand:
    pass


@dataclass(frozen=True, slots=True)
class CapabilitiesListCommand:
    pass


@dataclass(frozen=True, slots=True)
class CapabilitiesDescribeCommand:
    capability_id: str


@dataclass(frozen=True, slots=True)
class OperationCommand:
    kind: OperationKind
    scope: ScopeOptions
    artifact_ref: str | None = None
    request_file: Path | None = None


@dataclass(frozen=True, slots=True)
class ShowLastCommand:
    view: LastView = LastView.SUMMARY
    force_json: bool = False


@dataclass(frozen=True, slots=True)
class ExplainLastCommand:
    pass


@dataclass(frozen=True, slots=True)
class TraceLastCommand:
    view: TraceView = TraceView.ALL


@dataclass(frozen=True, slots=True)
class RefreshLastCommand:
    pass


@dataclass(frozen=True, slots=True)
class ExitCommand:
    pass


type ShellCommand = (
    HelpCommand
    | UseCommand
    | SetCommand
    | UnsetCommand
    | ClearContextCommand
    | ShowContextCommand
    | CapabilitiesListCommand
    | CapabilitiesDescribeCommand
    | OperationCommand
    | ShowLastCommand
    | ExplainLastCommand
    | TraceLastCommand
    | RefreshLastCommand
    | ExitCommand
)


@dataclass(frozen=True, slots=True)
class ParsedCommand:
    command: ShellCommand
    output_override: ShellOutputMode | None = None
