"""Characterization tests for the tool-output parsers in ``scan_codebase.py``.

These pin the behavior of ``run_vulture``, ``run_ruff``, ``run_docsig`` and
``run_docvet`` before the shared run-and-parse shape is extracted, so the
refactor can be proven behavior-preserving.
"""

import subprocess
from collections.abc import Callable

import pytest
import scan_codebase  # local module: conftest.py puts scripts/ on sys.path

VULTURE_OUTPUT = """\
src/demo.py:12: unused function 'dead_helper' (90% confidence)
src/demo.py:20: unused variable 'tmp' (80% confidence)
WARNING: vulture skipped a file
"""

RUFF_OUTPUT = """\
src/demo.py:3:1: F401 `os` imported but unused
src/demo.py:10:5: F841 local variable `tmp` is assigned to but never used
"""

DOCSIG_OUTPUT = """\
src/utils.py:14:in function parse_timestamp: Extra parameter(s) in docstring: ts
"""

DOCVET_OUTPUT = """\
src/demo.py:7: DOC001 WARNING Stale docstring
"""


@pytest.fixture
def stub_tool(monkeypatch: pytest.MonkeyPatch) -> Callable[..., list[list[str]]]:
    """Install a fake tool: controllable ``which``, ``subprocess.run`` and argv capture."""

    def install(
        stdout: str = "",
        stderr: str = "",
        installed: bool = True,
        exc: Exception | None = None,
    ) -> list[list[str]]:
        calls: list[list[str]] = []
        monkeypatch.setattr(
            scan_codebase.shutil, "which", lambda _name: "/usr/bin/tool" if installed else None
        )

        def fake_run(cmd: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append(cmd)
            if exc is not None:
                raise exc
            return subprocess.CompletedProcess(cmd, 0, stdout, stderr)

        monkeypatch.setattr(scan_codebase.subprocess, "run", fake_run)
        return calls

    return install


def test_vulture_returns_structured_findings(stub_tool: Callable[..., list[list[str]]]) -> None:
    # Arrange
    stub_tool(stdout=VULTURE_OUTPUT)

    # Act
    findings = scan_codebase.run_vulture("/src")

    # Assert
    assert findings == [
        {
            "file": "src/demo.py",
            "line": 12,
            "type": "dead_code",
            "name": "'dead_helper'",
            "confidence": 90,
            "message": "unused function 'dead_helper'",
        },
        {
            "file": "src/demo.py",
            "line": 20,
            "type": "dead_code",
            "name": "'tmp'",
            "confidence": 80,
            "message": "unused variable 'tmp'",
        },
    ]


def test_vulture_single_word_message_becomes_its_own_name(
    stub_tool: Callable[..., list[list[str]]],
) -> None:
    # Arrange
    stub_tool(stdout="src/a.py:1: deadcode (100% confidence)\n")

    # Act
    findings = scan_codebase.run_vulture("/src")

    # Assert
    assert findings[0]["name"] == "deadcode"


def test_vulture_accepts_bare_percentage_form(
    stub_tool: Callable[..., list[list[str]]],
) -> None:
    # Arrange - ``(90%)`` without the word ``confidence``
    stub_tool(stdout="src/a.py:2: unused import (90%)\n")

    # Act
    findings = scan_codebase.run_vulture("/src")

    # Assert
    assert findings[0]["confidence"] == 90


def test_vulture_forwards_confidence_floor(stub_tool: Callable[..., list[list[str]]]) -> None:
    # Arrange
    calls = stub_tool(stdout="")

    # Act
    scan_codebase.run_vulture("/src", min_confidence=95)

    # Assert
    assert calls == [["vulture", "/src", "--min-confidence=95"]]


def test_ruff_returns_concise_findings(stub_tool: Callable[..., list[list[str]]]) -> None:
    # Arrange
    stub_tool(stdout=RUFF_OUTPUT)

    # Act
    findings = scan_codebase.run_ruff("/src", "F401,F841")

    # Assert
    assert findings == [
        {
            "file": "src/demo.py",
            "line": 3,
            "code": "F401",
            "message": "`os` imported but unused",
        },
        {
            "file": "src/demo.py",
            "line": 10,
            "code": "F841",
            "message": "local variable `tmp` is assigned to but never used",
        },
    ]


def test_ruff_forwards_select_and_output_format(
    stub_tool: Callable[..., list[list[str]]],
) -> None:
    # Arrange
    calls = stub_tool(stdout="")

    # Act
    scan_codebase.run_ruff("/src", "ERA")

    # Assert
    assert calls == [["ruff", "check", "--select=ERA", "--output-format=concise", "/src"]]


def test_docsig_tags_signature_mismatch(stub_tool: Callable[..., list[list[str]]]) -> None:
    # Arrange
    stub_tool(stdout=DOCSIG_OUTPUT)

    # Act
    findings = scan_codebase.run_docsig("/src")

    # Assert
    assert findings == [
        {
            "file": "src/utils.py",
            "line": 14,
            "type": "docstring_signature_mismatch",
            "message": "in function parse_timestamp: Extra parameter(s) in docstring: ts",
        }
    ]


def test_docvet_splits_rule_and_severity(stub_tool: Callable[..., list[list[str]]]) -> None:
    # Arrange
    stub_tool(stdout=DOCVET_OUTPUT)

    # Act
    findings = scan_codebase.run_docvet("/src")

    # Assert
    assert findings == [
        {
            "file": "src/demo.py",
            "line": 7,
            "rule": "DOC001",
            "severity": "WARNING",
            "message": "Stale docstring",
        }
    ]


def test_unparseable_output_yields_no_findings(
    stub_tool: Callable[..., list[list[str]]],
) -> None:
    # Arrange
    stub_tool(stdout="not a finding\n\n")

    # Act
    findings = scan_codebase.run_ruff("/src", "F401")

    # Assert
    assert findings == []


@pytest.mark.parametrize(
    ("runner", "tool"),
    [
        (lambda: scan_codebase.run_vulture("/src"), "vulture"),
        (lambda: scan_codebase.run_ruff("/src", "F401"), "ruff"),
        (lambda: scan_codebase.run_docsig("/src"), "docsig"),
        (lambda: scan_codebase.run_docvet("/src"), "docvet"),
    ],
)
def test_missing_tool_reports_not_installed(
    stub_tool: Callable[..., list[list[str]]], runner: Callable[[], list[dict]], tool: str
) -> None:
    # Arrange
    stub_tool(installed=False)

    # Act
    findings = runner()

    # Assert
    assert findings == [{"error": True, "tool": tool, "detail": f"{tool} not installed"}]


@pytest.mark.parametrize(
    "runner",
    [
        lambda: scan_codebase.run_vulture("/src"),
        lambda: scan_codebase.run_ruff("/src", "F401"),
        lambda: scan_codebase.run_docsig("/src"),
        lambda: scan_codebase.run_docvet("/src"),
    ],
)
def test_stderr_only_is_reported_as_not_installed(
    stub_tool: Callable[..., list[list[str]]], runner: Callable[[], list[dict]]
) -> None:
    # Arrange
    stub_tool(stderr="config error")

    # Act
    findings = runner()

    # Assert
    assert findings[0]["error"] is True


def test_stderr_with_stdout_still_parses(stub_tool: Callable[..., list[list[str]]]) -> None:
    # Arrange
    stub_tool(stdout=RUFF_OUTPUT, stderr="warning: deprecated flag")

    # Act
    findings = scan_codebase.run_ruff("/src", "F401")

    # Assert
    assert len(findings) == 2


def test_missing_binary_is_reported_as_not_installed(
    stub_tool: Callable[..., list[list[str]]],
) -> None:
    # Arrange
    stub_tool(exc=FileNotFoundError("ruff"))

    # Act
    findings = scan_codebase.run_ruff("/src", "F401")

    # Assert
    assert findings == [{"error": True, "tool": "ruff", "detail": "ruff not installed"}]
