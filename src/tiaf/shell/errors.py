"""Safe error vocabulary for the local TI Shell adapter."""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

from tiaf.contracts.common import TIAF_TIMEZONE, TiafDateTime
from tiaf.facade import FacadeErrorRecord


class ShellErrorCode(StrEnum):
    SYNTAX_ERROR = "SYNTAX_ERROR"
    CONTEXT_ERROR = "CONTEXT_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    UNSUPPORTED = "UNSUPPORTED"
    NO_PRIOR_RESULT = "NO_PRIOR_RESULT"
    EXPLANATION_UNAVAILABLE = "EXPLANATION_UNAVAILABLE"
    INPUT_SAFETY_ERROR = "INPUT_SAFETY_ERROR"
    INTEGRITY_ERROR = "INTEGRITY_ERROR"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    INTERRUPTED = "INTERRUPTED"


class ShellErrorRecord(BaseModel):
    """Serializable Shell error which never contains private exception state."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_id: Literal["tiaf.shell.error"] = "tiaf.shell.error"
    schema_version: Literal["1.0"] = "1.0"
    code: ShellErrorCode
    message: str
    command_name: str | None = None
    facade_error: FacadeErrorRecord | None = None
    occurred_at: TiafDateTime


_EXIT_BY_CODE = {
    ShellErrorCode.SYNTAX_ERROR: 2,
    ShellErrorCode.CONTEXT_ERROR: 2,
    ShellErrorCode.PERMISSION_DENIED: 3,
    ShellErrorCode.UNSUPPORTED: 4,
    ShellErrorCode.NO_PRIOR_RESULT: 4,
    ShellErrorCode.EXPLANATION_UNAVAILABLE: 4,
    ShellErrorCode.INPUT_SAFETY_ERROR: 5,
    ShellErrorCode.INTEGRITY_ERROR: 5,
    ShellErrorCode.EXECUTION_FAILED: 6,
    ShellErrorCode.INTERRUPTED: 130,
}


class ShellError(ValueError):
    """Expected, redacted command failure with a stable process exit category."""

    def __init__(self, record: ShellErrorRecord) -> None:
        super().__init__(record.message)
        self.record = record

    @property
    def exit_code(self) -> int:
        return _EXIT_BY_CODE[self.record.code]


def shell_error(
    code: ShellErrorCode,
    message: str,
    *,
    command_name: str | None = None,
    facade_error: FacadeErrorRecord | None = None,
) -> ShellError:
    return ShellError(
        ShellErrorRecord(
            code=code,
            message=message,
            command_name=command_name,
            facade_error=facade_error,
            occurred_at=datetime.now(TIAF_TIMEZONE),
        )
    )
