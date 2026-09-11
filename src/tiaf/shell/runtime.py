"""Shared one-shot and REPL execution runtime for TI Shell commands."""

from dataclasses import dataclass
from typing import TextIO

from .commands import ParsedCommand, ShellOutputMode
from .dispatcher import DispatchOutcome, ShellDispatcher
from .errors import ShellError, ShellErrorCode, shell_error
from .parser import parse_line, parse_tokens
from .renderers import render, render_error


@dataclass(frozen=True, slots=True)
class ShellRunResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    should_exit: bool = False
    outcome: DispatchOutcome | None = None
    error: ShellError | None = None


class ShellRuntime:
    """Execute both argv tokens and REPL text through one dispatcher."""

    def __init__(self, dispatcher: ShellDispatcher) -> None:
        self.dispatcher = dispatcher

    def execute_tokens(self, tokens: list[str] | tuple[str, ...]) -> ShellRunResult:
        parsed = None
        try:
            parsed = parse_tokens(tokens)
            outcome = self.dispatcher.execute(parsed)
            output = render(outcome)
            return ShellRunResult(
                exit_code=0,
                stdout=output,
                should_exit=outcome.should_exit,
                outcome=outcome,
            )
        except ShellError as exc:
            json_mode = (
                parsed is not None and parsed.output_override is ShellOutputMode.JSON
            ) or self.dispatcher.session.defaults.output is ShellOutputMode.JSON
            if "--json" in tokens:
                json_mode = True
            rendered = render_error(exc, json_mode=json_mode)
            return ShellRunResult(
                exit_code=exc.exit_code,
                stdout=rendered if json_mode else "",
                stderr="" if json_mode else rendered,
                error=exc,
            )
        except KeyboardInterrupt:
            interrupted = shell_error(ShellErrorCode.INTERRUPTED, "command interrupted")
            return ShellRunResult(
                exit_code=130,
                stderr=render_error(interrupted, json_mode=False),
                error=interrupted,
            )

    def execute_line(self, line: str) -> ShellRunResult:
        try:
            parsed = parse_line(line)
            return self.execute_tokens_from_parsed(parsed)
        except ShellError as exc:
            json_mode = self.dispatcher.session.defaults.output is ShellOutputMode.JSON
            rendered = render_error(exc, json_mode=json_mode)
            return ShellRunResult(
                exit_code=exc.exit_code,
                stdout=rendered if json_mode else "",
                stderr="" if json_mode else rendered,
                error=exc,
            )

    def execute_tokens_from_parsed(self, parsed: ParsedCommand) -> ShellRunResult:
        """Internal parity seam: a parsed REPL command enters normal execution once."""
        try:
            outcome = self.dispatcher.execute(parsed)
            return ShellRunResult(
                exit_code=0,
                stdout=render(outcome),
                should_exit=outcome.should_exit,
                outcome=outcome,
            )
        except ShellError as exc:
            json_mode = (
                parsed.output_override is ShellOutputMode.JSON
                or self.dispatcher.session.defaults.output is ShellOutputMode.JSON
            )
            rendered = render_error(exc, json_mode=json_mode)
            return ShellRunResult(
                exit_code=exc.exit_code,
                stdout=rendered if json_mode else "",
                stderr="" if json_mode else rendered,
                error=exc,
            )
        except KeyboardInterrupt:
            interrupted = shell_error(ShellErrorCode.INTERRUPTED, "command interrupted")
            return ShellRunResult(
                exit_code=130,
                stderr=render_error(interrupted, json_mode=False),
                error=interrupted,
            )


def run_repl(
    runtime: ShellRuntime,
    *,
    input_stream: TextIO,
    output_stream: TextIO,
    error_stream: TextIO,
) -> int:
    """Run the bounded local REPL without line-editing or arbitrary code hooks."""
    while True:
        output_stream.write("TI> ")
        output_stream.flush()
        try:
            line = input_stream.readline()
        except KeyboardInterrupt:
            error_stream.write("INTERRUPTED: input cancelled\n")
            continue
        if line == "":
            output_stream.write("\n")
            return 0
        if not line.strip():
            continue
        result = runtime.execute_line(line)
        if result.stdout:
            output_stream.write(f"{result.stdout}\n")
        if result.stderr:
            error_stream.write(f"{result.stderr}\n")
        if result.should_exit:
            return 0
