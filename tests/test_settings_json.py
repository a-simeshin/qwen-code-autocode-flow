"""Tests for .qwen/settings.json validity and correctness."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def settings(qwen_dir: Path) -> dict:
    """Load and return the parsed settings.json."""
    settings_path = qwen_dir / "settings.json"
    assert settings_path.exists(), "settings.json not found in .qwen/"
    content = settings_path.read_text(encoding="utf-8")
    try:
        data: dict = json.loads(content)
    except json.JSONDecodeError as exc:
        pytest.fail(f"settings.json is not valid JSON: {exc}")
    return data


def test_settings_is_valid_json(qwen_dir: Path):
    """settings.json must be valid JSON."""
    settings_path = qwen_dir / "settings.json"
    content = settings_path.read_text(encoding="utf-8")
    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        pytest.fail(f"settings.json is not valid JSON: {exc}")


def test_settings_has_hooks_key(settings: dict):
    """settings.json must have a 'hooks' key."""
    assert "hooks" in settings, "settings.json missing 'hooks' key"


def test_hook_scripts_exist(qwen_dir: Path, settings: dict):
    """Each hook command must reference a script file that exists."""
    hooks = settings.get("hooks", {})
    missing = []
    for event_name, hook_list in hooks.items():
        for hook_entry in hook_list:
            for hook in hook_entry.get("hooks", []):
                command = hook.get("command", "")
                # Extract the script path from the command
                # Commands look like: uv run --no-project $CLAUDE_PROJECT_DIR/.qwen/hooks/script.py
                # Qwen Code uses $CLAUDE_PROJECT_DIR for inline expansion in command strings
                parts = command.split()
                for part in parts:
                    if part.endswith(".py"):
                        # Resolve $CLAUDE_PROJECT_DIR to the project root
                        script_rel = part.replace(
                            "$CLAUDE_PROJECT_DIR/", ""
                        )
                        script_path = qwen_dir.parent / script_rel
                        if not script_path.exists():
                            missing.append(
                                f"{event_name}: {script_rel} (from: {command})"
                            )
    assert not missing, (
        "Hook commands reference missing script files:\n"
        + "\n".join(f"  - {m}" for m in missing)
    )


def test_uses_claude_project_dir_for_inline_expansion(settings: dict):
    """Hook commands must use $CLAUDE_PROJECT_DIR (Qwen Code inline expansion).

    Qwen Code only expands $CLAUDE_PROJECT_DIR and $GEMINI_PROJECT_DIR in command strings.
    $QWEN_PROJECT_DIR is available as env var but NOT expanded inline.
    """
    hooks = settings.get("hooks", {})
    violations = []
    for event_name, hook_list in hooks.items():
        for hook_entry in hook_list:
            for hook in hook_entry.get("hooks", []):
                command = hook.get("command", "")
                if "$QWEN_PROJECT_DIR" in command:
                    violations.append(f"{event_name}: {command}")
    assert not violations, (
        "Hook commands use $QWEN_PROJECT_DIR (not expanded by Qwen Code):\n"
        + "\n".join(f"  - {v}" for v in violations)
    )


def test_no_claude_hooks_path_in_commands(settings: dict):
    """No hook command should contain .claude/hooks/ path."""
    hooks = settings.get("hooks", {})
    violations = []
    for event_name, hook_list in hooks.items():
        for hook_entry in hook_list:
            for hook in hook_entry.get("hooks", []):
                command = hook.get("command", "")
                if ".claude/hooks/" in command:
                    violations.append(f"{event_name}: {command}")
    assert not violations, (
        "Hook commands contain .claude/hooks/ path:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )
