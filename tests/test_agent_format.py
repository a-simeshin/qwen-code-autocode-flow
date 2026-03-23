"""Tests that agent .md files have correct YAML frontmatter format."""

import re
from pathlib import Path

import pytest

# PascalCase Claude tool names that must NOT appear in tools lists
CLAUDE_TOOL_NAMES = {"Read", "Write", "Edit", "Bash", "Glob", "Grep"}


def _collect_agent_files(qwen_dir: Path) -> list[Path]:
    """Collect all .md files from .qwen/agents/ and .qwen/agents/team/."""
    agents_dir = qwen_dir / "agents"
    files = list(agents_dir.glob("*.md"))
    team_dir = agents_dir / "team"
    if team_dir.exists():
        files.extend(team_dir.glob("*.md"))
    return sorted(files)


def _parse_frontmatter(content: str) -> dict[str, object] | None:
    """Extract YAML frontmatter from markdown content between --- markers."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    # Simple YAML key-value parser (handles simple keys and list items)
    frontmatter: dict[str, object] = {}
    current_key = None
    current_list: list[str] = []
    for line in match.group(1).splitlines():
        # Check for list item under current key
        list_match = re.match(r"^\s+-\s+(.*)", line)
        if list_match and current_key:
            current_list.append(list_match.group(1).strip())
            continue
        # Check for key-value pair
        kv_match = re.match(r"^(\w[\w_-]*):\s*(.*)", line)
        if kv_match:
            # Save previous list if any
            if current_key and current_list:
                frontmatter[current_key] = current_list
            current_key = kv_match.group(1)
            value = kv_match.group(2).strip()
            if value:
                frontmatter[current_key] = value
                current_list = []
            else:
                current_list = []
    # Save last list
    if current_key and current_list:
        frontmatter[current_key] = current_list
    return frontmatter


@pytest.fixture
def agent_files(qwen_dir: Path) -> list[tuple[Path, dict[str, object]]]:
    """Parse all agent files and return (path, frontmatter) pairs."""
    results = []
    for filepath in _collect_agent_files(qwen_dir):
        content = filepath.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        if fm is not None:
            results.append((filepath, fm))
        else:
            # Include with empty dict so test can flag missing frontmatter
            results.append((filepath, {}))
    assert results, "No agent .md files found in .qwen/agents/"
    return results


def test_agents_have_name(agent_files: list[tuple[Path, dict]]):
    """Each agent must have a 'name' field in frontmatter."""
    for filepath, fm in agent_files:
        assert "name" in fm, f"Agent {filepath.name} missing 'name' in frontmatter"


def test_agents_have_description(agent_files: list[tuple[Path, dict]]):
    """Each agent must have a 'description' field in frontmatter."""
    for filepath, fm in agent_files:
        assert "description" in fm, (
            f"Agent {filepath.name} missing 'description' in frontmatter"
        )


def test_agents_no_model_field(agent_files: list[tuple[Path, dict]]):
    """No agent should have a 'model' field in frontmatter."""
    for filepath, fm in agent_files:
        assert "model" not in fm, (
            f"Agent {filepath.name} should not have 'model' in frontmatter"
        )


def test_agents_no_color_field(agent_files: list[tuple[Path, dict]]):
    """No agent should have a 'color' field in frontmatter."""
    for filepath, fm in agent_files:
        assert "color" not in fm, (
            f"Agent {filepath.name} should not have 'color' in frontmatter"
        )


def test_agents_tools_no_pascal_case(agent_files: list[tuple[Path, dict]]):
    """Tool names in agents must use Qwen format, not PascalCase Claude names."""
    for filepath, fm in agent_files:
        tools = fm.get("tools", [])
        if isinstance(tools, list):
            for tool in tools:
                assert tool not in CLAUDE_TOOL_NAMES, (
                    f"Agent {filepath.name} has Claude-style tool name '{tool}' "
                    f"in tools list"
                )
