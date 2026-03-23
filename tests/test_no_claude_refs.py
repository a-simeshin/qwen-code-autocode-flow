"""Tests that .qwen/ files contain no leftover Claude-specific references."""

import re
from pathlib import Path

import pytest

# Patterns that must NOT appear in .qwen/ files
FORBIDDEN_PATTERNS = [
    (r"\.claude/", "Reference to .claude/ directory"),
    (r"CLAUDE_PROJECT_DIR", "Reference to CLAUDE_PROJECT_DIR variable"),
    (r"CLAUDE_ENV_FILE", "Reference to CLAUDE_ENV_FILE variable"),
]

# Lines containing these words are excluded (credit/attribution/documentation lines)
EXCLUSION_WORDS = ["credit", "source", "ported from", "based on", "original", "upstream"]

# Files where CLAUDE_PROJECT_DIR is legitimate (Qwen Code inline expansion compatibility)
CLAUDE_PROJECT_DIR_ALLOWED_FILES = {"settings.json", "paths.py"}


def _collect_qwen_files(qwen_dir: Path) -> list[Path]:
    """Collect all .py, .md, and .json files under .qwen/."""
    extensions = {".py", ".md", ".json"}
    files = []
    for ext in extensions:
        files.extend(qwen_dir.rglob(f"*{ext}"))
    return sorted(files)


def _is_exclusion_line(line: str) -> bool:
    """Check if a line is an attribution/credit line that should be excluded."""
    lower = line.lower()
    return any(word in lower for word in EXCLUSION_WORDS)


@pytest.mark.parametrize(
    "pattern,description",
    FORBIDDEN_PATTERNS,
    ids=[p[1] for p in FORBIDDEN_PATTERNS],
)
def test_no_forbidden_pattern(qwen_dir: Path, pattern: str, description: str):
    """No .qwen/ file should contain Claude-specific references."""
    violations = []
    for filepath in _collect_qwen_files(qwen_dir):
        try:
            content = filepath.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(content.splitlines(), 1):
            if _is_exclusion_line(line):
                continue
            if re.search(pattern, line):
                rel = filepath.relative_to(qwen_dir)
                # Allow CLAUDE_PROJECT_DIR in specific files (Qwen inline expansion)
                if (
                    "CLAUDE_PROJECT_DIR" in pattern
                    and filepath.name in CLAUDE_PROJECT_DIR_ALLOWED_FILES
                ):
                    continue
                violations.append(f"  {rel}:{i}: {line.strip()}")

    assert not violations, (
        f"{description} found in .qwen/ files:\n" + "\n".join(violations)
    )
