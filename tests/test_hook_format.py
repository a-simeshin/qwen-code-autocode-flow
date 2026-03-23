"""Tests that each hook .py file compiles and handles empty stdin gracefully."""

import py_compile
import subprocess
import sys
from pathlib import Path

import pytest

EXPECTED_HOOKS = [
    "context_router.py",
    "notification.py",
    "permission_request.py",
    "post_tool_use_failure.py",
    "post_tool_use.py",
    "pre_compact.py",
    "pre_tool_use.py",
    "section_loader.py",
    "session_end.py",
    "session_start.py",
    "setup.py",
    "stop.py",
    "subagent_stop.py",
    "user_prompt_submit.py",
]


@pytest.mark.parametrize("hook_file", EXPECTED_HOOKS)
def test_hook_exists(qwen_dir: Path, hook_file: str):
    """Each expected hook file must exist in .qwen/hooks/."""
    hook_path = qwen_dir / "hooks" / hook_file
    assert hook_path.exists(), f"Hook file not found: {hook_path}"


@pytest.mark.parametrize("hook_file", EXPECTED_HOOKS)
def test_hook_compiles(qwen_dir: Path, hook_file: str):
    """Each hook .py file must compile without syntax errors."""
    hook_path = qwen_dir / "hooks" / hook_file
    if not hook_path.exists():
        pytest.skip(f"Hook file not found: {hook_path}")
    try:
        py_compile.compile(str(hook_path), doraise=True)
    except py_compile.PyCompileError as exc:
        pytest.fail(f"Hook {hook_file} has compilation error: {exc}")


@pytest.mark.parametrize("hook_file", EXPECTED_HOOKS)
def test_hook_handles_empty_stdin(qwen_dir: Path, hook_file: str):
    """Each hook must handle empty stdin gracefully (exit without traceback)."""
    hook_path = qwen_dir / "hooks" / hook_file
    if not hook_path.exists():
        pytest.skip(f"Hook file not found: {hook_path}")
    result = subprocess.run(
        [sys.executable, str(hook_path)],
        input="",
        capture_output=True,
        text=True,
        timeout=10,
    )
    # Hook should not crash with a traceback on empty input.
    # Exit code 0 or 1 are acceptable; what matters is no unhandled exception.
    assert "Traceback (most recent call last)" not in result.stderr, (
        f"Hook {hook_file} crashed on empty stdin:\n{result.stderr}"
    )
