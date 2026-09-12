"""Closed TI Shell command dispatcher over the caller-bound local facade."""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError

from tiaf.baseline import DeterministicBaselineRequest
from tiaf.context import AnalysisPurpose
from tiaf.contracts import Horizon
from tiaf.contracts.common import TIAF_TIMEZONE, TiafDateTime
from tiaf.facade import (
    A4EvaluateRequest,
    A4InputProjectRequest,
    BaselineAssessRequest,
    CapabilityDescriptor,
    CapabilityListRequest,
    CapabilityListResult,
    FacadeInvocationError,
    FacadeOperationRequest,
    FacadeStatus,
    InvocationBudget,
    InvocationScope,
    LocalFacadeClient,
    OpportunityAssembleRequest,
    PositionAssessRequest,
    RecordedReplayRequest,
    ReplayVerifyRequest,
)

from .commands import (
    CapabilitiesDescribeCommand,
    CapabilitiesListCommand,
    ClearContextCommand,
    ContextField,
    ExitCommand,
    ExplainLastCommand,
    HelpCommand,
    OperationCommand,
    OperationKind,
    ParsedCommand,
    RefreshLastCommand,
    SetCommand,
    ShellCommand,
    ShellOutputMode,
    ShowContextCommand,
    ShowLastCommand,
    TraceLastCommand,
    UnsetCommand,
    UseCommand,
)
from .errors import ShellErrorCode, shell_error
from .session import (
    InvocationPlan,
    ResolvedScope,
    SessionDefaults,
    ShellFacadeResult,
    ShellInvocationRecord,
    ShellSession,
    SuccessfulInvocation,
)

_DATETIME_ADAPTER = TypeAdapter(TiafDateTime)
_MAX_BASELINE_REQUEST_BYTES = 8 * 1024 * 1024

type ShellValue = (
    str | SessionDefaults | CapabilityDescriptor | SuccessfulInvocation | ShellFacadeResult
)


@dataclass(frozen=True, slots=True)
class DispatchOutcome:
    command: ShellCommand
    command_name: str
    value: ShellValue
    output_mode: ShellOutputMode
    facade_result: ShellFacadeResult | None = None
    invocation: SuccessfulInvocation | None = None
    should_exit: bool = False


HELP_TEXT = """TI Shell v0.1 (command mode)
help [TOPIC]
use SYMBOL
set FIELD VALUE | unset FIELD | clear context | show context
capabilities list | capabilities describe CAPABILITY_ID
baseline assess --request-file RELATIVE_JSON [scope options]
opportunity assemble --artifact-ref QUALIFIED_ID [scope options]
a4 project|evaluate --artifact-ref QUALIFIED_ID [scope options]
position assess --snapshot QUALIFIED_ID [scope options]
replay recorded|verify --artifact-ref QUALIFIED_ID [scope options]
show last [--json|--reasons|--gaps|--contradictions|--evidence]
explain last | trace last [--cost|--evidence|--timing] | refresh last
exit | quit
"""


def command_name(command: ShellCommand) -> str:
    if isinstance(command, HelpCommand):
        return "help"
    if isinstance(command, UseCommand):
        return "use"
    if isinstance(command, SetCommand):
        return "set"
    if isinstance(command, UnsetCommand):
        return "unset"
    if isinstance(command, ClearContextCommand):
        return "clear context"
    if isinstance(command, ShowContextCommand):
        return "show context"
    if isinstance(command, CapabilitiesListCommand):
        return "capabilities list"
    if isinstance(command, CapabilitiesDescribeCommand):
        return "capabilities describe"
    if isinstance(command, OperationCommand):
        return command.kind.value
    if isinstance(command, ShowLastCommand):
        return "show last"
    if isinstance(command, ExplainLastCommand):
        return "explain last"
    if isinstance(command, TraceLastCommand):
        return "trace last"
    if isinstance(command, RefreshLastCommand):
        return "refresh last"
    return "exit"


class ShellDispatcher:
    """Translate typed commands into exact facade requests; no private dispatch."""

    def __init__(
        self,
        client: LocalFacadeClient,
        *,
        baseline_request_root: Path,
        defaults: SessionDefaults | None = None,
        history_limit: int = 32,
    ) -> None:
        try:
            root = baseline_request_root.resolve(strict=True)
        except OSError as exc:
            raise ValueError("baseline request root is unavailable") from exc
        if not root.is_dir():
            raise ValueError("baseline request root must be a directory")
        self._client = client
        self._baseline_request_root = root
        self.session = ShellSession(defaults=defaults, history_limit=history_limit)

    def execute(self, parsed: ParsedCommand) -> DispatchOutcome:
        command = parsed.command
        output = parsed.output_override or self.session.defaults.output
        if isinstance(command, ShowLastCommand) and command.force_json:
            output = ShellOutputMode.JSON
        name = command_name(command)

        if isinstance(command, HelpCommand):
            value = HELP_TEXT if command.topic is None else self._help_topic(command.topic)
            return DispatchOutcome(command, name, value, output)
        if isinstance(command, UseCommand):
            self.session.use_subject(command.subject)
            return DispatchOutcome(command, name, self.session.defaults, output)
        if isinstance(command, SetCommand):
            self._set(command)
            return DispatchOutcome(command, name, self.session.defaults, output)
        if isinstance(command, UnsetCommand):
            self.session.unset_default(command.field.value.replace("-", "_"))
            return DispatchOutcome(command, name, self.session.defaults, output)
        if isinstance(command, ClearContextCommand):
            self.session.clear()
            return DispatchOutcome(command, name, self.session.defaults, output)
        if isinstance(command, ShowContextCommand):
            return DispatchOutcome(command, name, self.session.defaults, output)
        if isinstance(command, ExitCommand):
            return DispatchOutcome(command, name, "Shell session closed", output, should_exit=True)
        if isinstance(command, CapabilitiesListCommand):
            invocation = self._list_capabilities(command)
            return DispatchOutcome(
                command, name, invocation.result, output, invocation.result, invocation
            )
        if isinstance(command, CapabilitiesDescribeCommand):
            invocation = self._list_capabilities(command)
            assert isinstance(invocation.result, CapabilityListResult)
            descriptor = next(
                (
                    item
                    for item in invocation.result.capabilities
                    if item.capability_id == command.capability_id
                ),
                None,
            )
            if descriptor is None:
                raise shell_error(
                    ShellErrorCode.UNSUPPORTED,
                    "capability is unavailable to this caller",
                    command_name=name,
                )
            return DispatchOutcome(
                command, name, descriptor, output, invocation.result, invocation
            )
        if isinstance(command, OperationCommand):
            plan = self._plan(command)
            invocation = self._invoke_plan(command, plan)
            return DispatchOutcome(
                command, name, invocation.result, output, invocation.result, invocation
            )
        if isinstance(command, ShowLastCommand | ExplainLastCommand | TraceLastCommand):
            last = self._require_last(name)
            return DispatchOutcome(command, name, last, output, last.result, last)
        if isinstance(command, RefreshLastCommand):
            last = self._require_last(name)
            if last.plan is None:
                raise shell_error(
                    ShellErrorCode.UNSUPPORTED,
                    "the prior command is not refreshable",
                    command_name=name,
                )
            invocation = self._invoke_plan(
                command,
                last.plan,
                parent_shell_invocation_id=last.record.shell_invocation_id,
            )
            return DispatchOutcome(
                command, name, invocation.result, output, invocation.result, invocation
            )
        raise shell_error(ShellErrorCode.UNSUPPORTED, "command is not supported")

    @staticmethod
    def _help_topic(topic: str) -> str:
        normalized = topic.strip().casefold()
        lines = tuple(line for line in HELP_TEXT.splitlines() if normalized in line.casefold())
        if not lines:
            raise shell_error(ShellErrorCode.UNSUPPORTED, "help topic is unavailable")
        return "\n".join(lines)

    def _set(self, command: SetCommand) -> None:
        field = command.field
        value: object
        try:
            if field is ContextField.SUBJECT:
                value = self._safe_subject(command.value)
            elif field is ContextField.HORIZON:
                value = Horizon(label=command.value.strip().upper())
            elif field is ContextField.OBJECTIVE:
                value = AnalysisPurpose(command.value.strip().upper())
            elif field is ContextField.AS_OF:
                value = _DATETIME_ADAPTER.validate_python(command.value)
            elif field is ContextField.OUTPUT:
                value = ShellOutputMode(command.value.casefold())
            else:
                value = self._safe_ref(command.value)
        except (ValidationError, ValueError) as exc:
            raise shell_error(
                ShellErrorCode.CONTEXT_ERROR,
                f"invalid value for {field.value}",
                command_name="set",
            ) from exc
        self.session.replace_default(field.value.replace("-", "_"), value)

    @staticmethod
    def _safe_ref(value: str) -> str:
        result = value.strip()
        if (
            not result
            or "://" in result
            or "/" in result
            or "\\" in result
            or result.startswith(("~", ".."))
        ):
            raise ValueError("unsafe logical reference")
        return result

    @staticmethod
    def _safe_subject(value: str) -> str:
        result = value.strip().upper()
        if re.fullmatch(r"[A-Z0-9][A-Z0-9_&-]*", result) is None:
            raise ValueError("subject must be a provider-neutral symbol")
        return result

    def _scope_value(self, explicit: object | None, field: str) -> object | None:
        return explicit if explicit is not None else getattr(self.session.defaults, field)

    def _resolve_scope(self, command: OperationCommand) -> ResolvedScope:
        scope = command.scope
        values = {
            "subject": self._scope_value(scope.subject, "subject"),
            "objective": self._scope_value(scope.objective, "objective"),
            "horizon": self._scope_value(scope.horizon, "horizon"),
            "as_of": self._scope_value(scope.as_of, "as_of"),
            "profile_ref": self._scope_value(scope.profile_ref, "profile_ref"),
            "authority_ref": self._scope_value(scope.authority_ref, "authority_ref"),
            "position_context_ref": self._scope_value(
                scope.position_context_ref, "position_context_ref"
            ),
        }
        missing = tuple(
            name
            for name in ("subject", "objective", "horizon", "as_of", "profile_ref", "authority_ref")
            if values[name] is None
        )
        if missing:
            raise shell_error(
                ShellErrorCode.CONTEXT_ERROR,
                f"missing required context: {', '.join(missing)}",
                command_name=command.kind.value,
            )
        return ResolvedScope(
            subject=str(values["subject"]),
            objective=values["objective"],  # type: ignore[arg-type]
            horizon=values["horizon"],  # type: ignore[arg-type]
            as_of=values["as_of"],  # type: ignore[arg-type]
            profile_ref=str(values["profile_ref"]),
            authority_ref=str(values["authority_ref"]),
            position_context_ref=(
                str(values["position_context_ref"])
                if values["position_context_ref"] is not None
                else None
            ),
        )

    def _plan(self, command: OperationCommand) -> InvocationPlan:
        if command.kind is not OperationKind.BASELINE_ASSESS:
            if command.artifact_ref is None:
                raise shell_error(ShellErrorCode.CONTEXT_ERROR, "artifact reference is required")
            resolved = self._resolve_scope(command)
            if command.kind is OperationKind.POSITION_ASSESS:
                if (
                    resolved.position_context_ref is not None
                    and resolved.position_context_ref != command.artifact_ref
                ):
                    raise shell_error(
                        ShellErrorCode.CONTEXT_ERROR,
                        "position-context-ref must match the logical snapshot reference",
                    )
                resolved = ResolvedScope(
                    subject=resolved.subject,
                    objective=resolved.objective,
                    horizon=resolved.horizon,
                    as_of=resolved.as_of,
                    profile_ref=resolved.profile_ref,
                    authority_ref=resolved.authority_ref,
                    position_context_ref=command.artifact_ref,
                )
            return InvocationPlan(
                kind=command.kind,
                scope=resolved,
                artifact_ref=command.artifact_ref,
            )

        baseline = self._load_baseline(command.request_file)
        assertions = command.scope
        default = self.session.defaults
        asserted_subject = assertions.subject or default.subject
        asserted_horizon = assertions.horizon or default.horizon
        asserted_as_of = assertions.as_of or default.as_of
        asserted_objective = (
            assertions.objective or default.objective or AnalysisPurpose.OPPORTUNITY
        )
        if asserted_subject is not None and asserted_subject != baseline.subject:
            raise shell_error(ShellErrorCode.CONTEXT_ERROR, "baseline subject assertion mismatch")
        if asserted_horizon is not None and asserted_horizon != baseline.horizon:
            raise shell_error(ShellErrorCode.CONTEXT_ERROR, "baseline horizon assertion mismatch")
        if asserted_as_of is not None and asserted_as_of != baseline.requested_at:
            raise shell_error(ShellErrorCode.CONTEXT_ERROR, "baseline as-of assertion mismatch")
        if asserted_objective is not AnalysisPurpose.OPPORTUNITY:
            raise shell_error(
                ShellErrorCode.CONTEXT_ERROR,
                "baseline objective must be OPPORTUNITY",
            )
        profile_ref = assertions.profile_ref or default.profile_ref
        authority_ref = assertions.authority_ref or default.authority_ref
        if profile_ref is None or authority_ref is None:
            raise shell_error(
                ShellErrorCode.CONTEXT_ERROR,
                "baseline requires profile-ref and authority-ref",
            )
        return InvocationPlan(
            kind=command.kind,
            scope=ResolvedScope(
                subject=baseline.subject,
                objective=AnalysisPurpose.OPPORTUNITY,
                horizon=baseline.horizon,
                as_of=baseline.requested_at,
                profile_ref=profile_ref,
                authority_ref=authority_ref,
                position_context_ref=assertions.position_context_ref
                or default.position_context_ref,
            ),
            baseline_request=baseline,
        )

    def _load_baseline(self, request_file: Path | None) -> DeterministicBaselineRequest:
        if request_file is None or request_file.is_absolute() or ".." in request_file.parts:
            raise shell_error(
                ShellErrorCode.INPUT_SAFETY_ERROR,
                "baseline request must be a relative path below the configured root",
            )
        try:
            resolved = (self._baseline_request_root / request_file).resolve(strict=True)
            resolved.relative_to(self._baseline_request_root)
            if not resolved.is_file() or resolved.stat().st_size > _MAX_BASELINE_REQUEST_BYTES:
                raise OSError
            content = resolved.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError) as exc:
            raise shell_error(
                ShellErrorCode.INPUT_SAFETY_ERROR,
                "baseline request file failed bounded-root validation",
            ) from exc
        try:
            return DeterministicBaselineRequest.model_validate_json(content)
        except ValidationError as exc:
            raise shell_error(
                ShellErrorCode.SYNTAX_ERROR,
                "baseline request does not match DeterministicBaselineRequest",
            ) from exc

    def _list_capabilities(
        self,
        command: CapabilitiesListCommand | CapabilitiesDescribeCommand,
    ) -> SuccessfulInvocation:
        profile = self.session.defaults.profile_ref
        authority = self.session.defaults.authority_ref
        if profile is None or authority is None:
            raise shell_error(
                ShellErrorCode.CONTEXT_ERROR,
                "capability discovery requires profile-ref and authority-ref",
            )
        request_id, correlation_id = self._identities()
        started = datetime.now(TIAF_TIMEZONE)
        request = CapabilityListRequest(
            request_id=request_id,
            correlation_id=correlation_id,
            profile_ref=profile,
            requested_authority_ref=authority,
        )
        try:
            result = self._client.list_capabilities(request)
        except FacadeInvocationError as exc:
            raise self._from_facade(exc, command_name(command)) from exc
        return self._record(command, result, None, started)

    def _invoke_plan(
        self,
        command: ShellCommand,
        plan: InvocationPlan,
        *,
        parent_shell_invocation_id: str | None = None,
    ) -> SuccessfulInvocation:
        request_id, correlation_id = self._identities()
        facade_scope = self._facade_scope(plan.scope, request_id, correlation_id, plan.artifact_ref)
        if plan.kind is OperationKind.BASELINE_ASSESS:
            assert plan.baseline_request is not None
            request: FacadeOperationRequest = BaselineAssessRequest(
                scope=facade_scope,
                baseline_request=plan.baseline_request,
            )
        elif plan.kind is OperationKind.OPPORTUNITY_ASSEMBLE:
            assert plan.artifact_ref is not None
            request = OpportunityAssembleRequest(
                scope=facade_scope,
                orchestration_capture_ref=plan.artifact_ref,
            )
        elif plan.kind is OperationKind.A4_INPUT_PROJECT:
            assert plan.artifact_ref is not None
            request = A4InputProjectRequest(scope=facade_scope, build_input_ref=plan.artifact_ref)
        elif plan.kind is OperationKind.A4_EVALUATE:
            assert plan.artifact_ref is not None
            request = A4EvaluateRequest(
                scope=facade_scope,
                projection_capture_ref=plan.artifact_ref,
            )
        elif plan.kind is OperationKind.POSITION_ASSESS:
            assert plan.artifact_ref is not None
            request = PositionAssessRequest(
                scope=facade_scope,
                position_request_ref=plan.artifact_ref,
            )
        elif plan.kind is OperationKind.REPLAY_RECORDED:
            assert plan.artifact_ref is not None
            request = RecordedReplayRequest(scope=facade_scope, artifact_ref=plan.artifact_ref)
        else:
            assert plan.artifact_ref is not None
            request = ReplayVerifyRequest(scope=facade_scope, artifact_ref=plan.artifact_ref)
        started = datetime.now(TIAF_TIMEZONE)
        try:
            result = self._client.invoke(request)
        except FacadeInvocationError as exc:
            raise self._from_facade(exc, command_name(command)) from exc
        return self._record(
            command,
            result,
            plan,
            started,
            parent_shell_invocation_id=parent_shell_invocation_id,
        )

    @staticmethod
    def _identities() -> tuple[str, str]:
        suffix = uuid4().hex
        return f"shell-request:{suffix}", f"shell-correlation:{suffix}"

    @staticmethod
    def _facade_scope(
        scope: ResolvedScope,
        request_id: str,
        correlation_id: str,
        artifact_ref: str | None,
    ) -> InvocationScope:
        artifacts = (artifact_ref,) if artifact_ref is not None else ()
        return InvocationScope(
            request_id=request_id,
            correlation_id=correlation_id,
            subject=scope.subject,
            objective=scope.objective,
            horizon=scope.horizon,
            as_of=scope.as_of,
            profile_ref=scope.profile_ref,
            requested_authority_ref=scope.authority_ref,
            requested_budget=InvocationBudget(max_elapsed_seconds=30),
            position_context_ref=scope.position_context_ref,
            admitted_artifact_refs=artifacts,
        )

    def _record(
        self,
        command: ShellCommand,
        result: ShellFacadeResult,
        plan: InvocationPlan | None,
        started: datetime,
        *,
        parent_shell_invocation_id: str | None = None,
    ) -> SuccessfulInvocation:
        record = ShellInvocationRecord(
            shell_invocation_id=f"shell-invocation:{uuid4().hex}",
            command_name=command_name(command),
            capability_id=result.metadata.capability_id,
            request_id=result.metadata.request_id,
            correlation_id=result.metadata.correlation_id,
            facade_run_id=result.metadata.run_id,
            status=result.metadata.status.value,
            started_at=started,
            completed_at=datetime.now(TIAF_TIMEZONE),
            parent_shell_invocation_id=parent_shell_invocation_id,
        )
        invocation = SuccessfulInvocation(command=command, result=result, record=record, plan=plan)
        self.session.record_success(invocation)
        return invocation

    def _require_last(self, name: str) -> SuccessfulInvocation:
        if self.session.last is None:
            raise shell_error(
                ShellErrorCode.NO_PRIOR_RESULT,
                "no successful facade result exists in this session",
                command_name=name,
            )
        return self.session.last

    @staticmethod
    def _from_facade(exc: FacadeInvocationError, name: str) -> Exception:
        status = exc.record.status
        if status is FacadeStatus.PERMISSION_DENIED:
            code = ShellErrorCode.PERMISSION_DENIED
        elif status in {FacadeStatus.UNSUPPORTED, FacadeStatus.MODEL_DISABLED}:
            code = ShellErrorCode.UNSUPPORTED
        elif status is FacadeStatus.REPLAY_INTEGRITY_ERROR:
            code = ShellErrorCode.INTEGRITY_ERROR
        elif status is FacadeStatus.INVALID_REQUEST:
            code = ShellErrorCode.SYNTAX_ERROR
        else:
            code = ShellErrorCode.EXECUTION_FAILED
        return shell_error(
            code,
            exc.record.message,
            command_name=name,
            facade_error=exc.record,
        )
