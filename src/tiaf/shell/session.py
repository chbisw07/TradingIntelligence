"""Isolated process-local TI Shell session state."""

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict

from tiaf.baseline import DeterministicBaselineRequest
from tiaf.context import AnalysisPurpose
from tiaf.contracts import Horizon
from tiaf.contracts.common import TIAF_TIMEZONE, TiafDateTime
from tiaf.facade import (
    A4EvaluateResult,
    A4InputProjectResult,
    BaselineAssessResult,
    CapabilityListResult,
    OpportunityAssembleResult,
    PositionAssessResult,
    RecordedReplayResult,
    ReplayVerifyResult,
)

from .commands import OperationKind, ShellCommand, ShellOutputMode

# Keep the accepted result set explicit so the Shell cannot retain private values.
type ShellFacadeResult = (
    CapabilityListResult
    | BaselineAssessResult
    | OpportunityAssembleResult
    | PositionAssessResult
    | A4InputProjectResult
    | A4EvaluateResult
    | RecordedReplayResult
    | ReplayVerifyResult
)


class SessionDefaults(BaseModel):
    """Requested interaction defaults; none of these values grants authority."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    subject: str | None = None
    objective: AnalysisPurpose | None = None
    horizon: Horizon | None = None
    as_of: TiafDateTime | None = None
    profile_ref: str | None = None
    authority_ref: str | None = None
    position_context_ref: str | None = None
    output: ShellOutputMode = ShellOutputMode.HUMAN


@dataclass(frozen=True, slots=True)
class ResolvedScope:
    subject: str
    objective: AnalysisPurpose
    horizon: Horizon
    as_of: datetime
    profile_ref: str
    authority_ref: str
    position_context_ref: str | None


@dataclass(frozen=True, slots=True)
class InvocationPlan:
    kind: OperationKind
    scope: ResolvedScope
    artifact_ref: str | None = None
    baseline_request: DeterministicBaselineRequest | None = None


@dataclass(frozen=True, slots=True)
class ShellInvocationRecord:
    shell_invocation_id: str
    command_name: str
    capability_id: str
    request_id: str
    correlation_id: str
    facade_run_id: str
    status: str
    started_at: datetime
    completed_at: datetime
    parent_shell_invocation_id: str | None = None


@dataclass(frozen=True, slots=True)
class SuccessfulInvocation:
    command: ShellCommand
    result: ShellFacadeResult
    record: ShellInvocationRecord
    plan: InvocationPlan | None = None


@dataclass(frozen=True, slots=True)
class ShellInvocationSummary:
    shell_invocation_id: str
    command_name: str
    capability_id: str
    facade_run_id: str
    status: str


class ShellSession:
    """Mutable owner of one isolated transient session; values stored are immutable."""

    def __init__(
        self,
        *,
        defaults: SessionDefaults | None = None,
        history_limit: int = 32,
    ) -> None:
        if not 1 <= history_limit <= 64:
            raise ValueError("history_limit must be between 1 and 64")
        self.session_id = f"shell-session:{uuid4().hex}"
        self.started_at = datetime.now(TIAF_TIMEZONE)
        self._bootstrap_defaults = defaults or SessionDefaults()
        self.defaults = self._bootstrap_defaults
        self.last: SuccessfulInvocation | None = None
        self._history: tuple[ShellInvocationSummary, ...] = ()
        self._history_limit = history_limit

    @property
    def history(self) -> tuple[ShellInvocationSummary, ...]:
        return self._history

    @property
    def last_result_reference(self) -> str | None:
        return self.last.record.facade_run_id if self.last is not None else None

    @property
    def last_invocation_id(self) -> str | None:
        return self.last.record.shell_invocation_id if self.last is not None else None

    @property
    def last_a4_result_reference(self) -> str | None:
        if self.last is not None and isinstance(self.last.result, A4EvaluateResult):
            return self.last.result.evaluation.result_id
        return None

    @property
    def last_replay_capture_reference(self) -> str | None:
        if self.last is None or self.last.plan is None:
            return None
        return self.last.plan.artifact_ref

    def use_subject(self, subject: str) -> None:
        self.defaults = self.defaults.model_copy(update={"subject": subject})

    def replace_default(self, field: str, value: object) -> None:
        self.defaults = self.defaults.model_copy(update={field: value})

    def unset_default(self, field: str) -> None:
        replacement = getattr(self._bootstrap_defaults, field)
        self.defaults = self.defaults.model_copy(update={field: replacement})

    def clear(self) -> None:
        self.defaults = self._bootstrap_defaults

    def record_success(self, invocation: SuccessfulInvocation) -> None:
        self.last = invocation
        item = ShellInvocationSummary(
            shell_invocation_id=invocation.record.shell_invocation_id,
            command_name=invocation.record.command_name,
            capability_id=invocation.record.capability_id,
            facade_run_id=invocation.record.facade_run_id,
            status=invocation.record.status,
        )
        self._history = (*self._history, item)[-self._history_limit :]
