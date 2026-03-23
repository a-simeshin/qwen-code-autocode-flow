"""Tests that permission_request.py uses Qwen tool names, not Claude tool names."""

import re
from pathlib import Path


def test_contains_qwen_tool_names(qwen_dir: Path):
    """permission_request.py must reference Qwen tool names.

    These are the Qwen-format tool names that should appear in the file
    as tool name checks or references (strings, dict keys, etc.).
    """
    content = (qwen_dir / "hooks" / "permission_request.py").read_text()
    # Tool names that must be present as active checks in permission_request.py
    # (read-only tools used in auto-allow patterns)
    qwen_read_tools = [
        "read_file",
        "run_shell_command",
        "glob",
        "grep_search",
    ]
    for tool in qwen_read_tools:
        assert tool in content, (
            f"Qwen tool name '{tool}' not found in permission_request.py"
        )

    # Additional Qwen tool names that should NOT be in Claude format
    # even if not all are referenced in this specific file.
    # Verify that any write/edit tool references use Qwen format.
    for claude_name, qwen_name in [
        ("Write", "write_file"),
        ("Edit", "edit"),
    ]:
        # If the file references these tools at all, it must use Qwen names
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            if re.search(rf'''(?<![a-zA-Z_])["']{claude_name}["'](?![a-zA-Z_])''', line):
                raise AssertionError(
                    f"Claude tool name '{claude_name}' found instead of "
                    f"'{qwen_name}' on line {i}: {line.strip()}"
                )


def test_no_claude_tool_names(qwen_dir: Path):
    """permission_request.py must not contain Claude tool names as tool checks.

    We look for standalone quoted tool name strings like "Read", "Write", "Bash"
    but exclude occurrences inside comments.
    """
    content = (qwen_dir / "hooks" / "permission_request.py").read_text()
    claude_tools = ["Read", "Write", "Bash"]
    for tool in claude_tools:
        # Match the tool name as a standalone quoted string (single or double quotes)
        # in non-comment lines
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue  # skip comment lines
            # Check for tool name as a standalone quoted string value
            # e.g. "Read", 'Read' -- used as a tool name reference
            if re.search(rf'''(?<![a-zA-Z_])["']{tool}["'](?![a-zA-Z_])''', line):
                raise AssertionError(
                    f"Claude tool name '{tool}' found as standalone string "
                    f"on line {i}: {line.strip()}"
                )
