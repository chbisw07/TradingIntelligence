"""CLI bootstrap, REPL lifecycle, history and dependency-boundary tests."""

import ast
import json
from io import StringIO
from pathlib import Path

import pytest

from tiaf.shell import SessionDefaults, ShellBootstrapConfig
from tiaf.shell.cli import main
from tiaf.shell.runtime import run_repl

from ..facade._support import AUTHORITY, PROFILE, config
from ._support import runtime, write_baseline


def test_cli_help_and_version_need_no_config(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--help"]) == 0
    help_output = capsys.readouterr()
    assert "TI Shell v0.1" in help_output.out
    assert help_output.err == ""

    assert main(["--version"]) == 0
    version_output = capsys.readouterr()
    assert "package 0.1.0" in version_output.out
    assert "output schema 1.0" in version_output.out


def test_capability_command_without_config_fails_safely(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["capabilities", "list"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--config is required" in captured.err
    assert "/home/" not in captured.err


def test_one_shot_cli_loads_trusted_config_and_returns_exact_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write_baseline(tmp_path)
    bootstrap = ShellBootstrapConfig(
        facade=config(),
        caller_id="caller:test",
        baseline_request_root=str(tmp_path),
        defaults=SessionDefaults(profile_ref=PROFILE, authority_ref=AUTHORITY),
    )
    path = tmp_path / "shell.json"
    path.write_text(bootstrap.model_dump_json(), encoding="utf-8")
    exit_code = main(
        [
            "--config",
            str(path),
            "--output",
            "json",
            "baseline",
            "assess",
            "--request-file",
            "baseline.json",
        ]
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["capability_id"] == "baseline.assess"
    assert payload["result"]["assessment"]["candidate_class"] == "NO_TRADE"
    assert captured.err == ""


def test_repl_has_prompt_shared_parser_context_and_clean_exit(tmp_path: Path) -> None:
    shell = runtime(tmp_path, full_context=False)
    output = StringIO()
    errors = StringIO()
    exit_code = run_repl(
        shell,
        input_stream=StringIO('use "KAYNES"\nshow context\nexit\n'),
        output_stream=output,
        error_stream=errors,
    )
    assert exit_code == 0
    assert output.getvalue().count("TI> ") == 3
    assert "KAYNES" in output.getvalue()
    assert errors.getvalue() == ""
    assert shell.dispatcher.session.defaults.subject == "KAYNES"


def test_repl_eof_exits_cleanly(tmp_path: Path) -> None:
    shell = runtime(tmp_path)
    output = StringIO()
    assert (
        run_repl(
            shell,
            input_stream=StringIO(""),
            output_stream=output,
            error_stream=StringIO(),
        )
        == 0
    )
    assert output.getvalue() == "TI> \n"


def test_one_shot_and_repl_share_parser_dispatcher_renderer(tmp_path: Path) -> None:
    tokens_runtime = runtime(tmp_path, full_context=False)
    line_runtime = runtime(tmp_path, full_context=False)
    from_tokens = tokens_runtime.execute_tokens(["use", "KAYNES"])
    from_line = line_runtime.execute_line("use KAYNES")
    assert from_tokens.exit_code == from_line.exit_code == 0
    assert from_tokens.stdout == from_line.stdout


def test_history_is_bounded_redacted_and_not_a_public_command(tmp_path: Path) -> None:
    shell = runtime(tmp_path, history_limit=2)
    for _ in range(3):
        assert shell.execute_tokens(["capabilities", "list"]).exit_code == 0
    history = shell.dispatcher.session.history
    assert len(history) == 2
    serialized = repr(history).casefold()
    assert "access_token" not in serialized
    assert "api_key" not in serialized
    assert "artifact content" not in serialized
    assert shell.execute_tokens(["history"]).exit_code == 2


def test_shell_package_has_no_forbidden_runtime_imports_or_execution_calls() -> None:
    root = Path("src/tiaf/shell")
    forbidden_import_roots = {
        "subprocess",
        "httpx",
        "mcp",
        "requests",
        "tiaf.providers",
        "tiaf.broker",
        "tiaf.models",
        "tiaf.a5",
        "tiaf.a6",
        "tiaf.a7",
    }
    forbidden_calls = {"eval", "exec", "compile", "__import__"}
    discovered_imports: set[str] = set()
    discovered_calls: set[str] = set()
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                discovered_imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                discovered_imports.add(node.module)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                discovered_calls.add(node.func.id)
    assert not {
        name
        for name in discovered_imports
        if any(
            name == root_name or name.startswith(f"{root_name}.")
            for root_name in forbidden_import_roots
        )
    }
    assert not forbidden_calls & discovered_calls


def test_console_entry_point_is_declared_without_new_dependency() -> None:
    project = Path("pyproject.toml").read_text(encoding="utf-8")
    assert 'ti = "tiaf.shell.cli:main"' in project
    assert "click" not in project.casefold()
    assert "typer" not in project.casefold()
