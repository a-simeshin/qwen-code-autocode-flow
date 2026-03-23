"""Tests that skill directories have SKILL.md with correct YAML frontmatter."""

import re
from pathlib import Path

import pytest

EXPECTED_SKILLS = ["plan-w-team", "smart-build", "plan", "all-tools"]


@pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
def test_skill_directory_exists(qwen_dir: Path, skill_name: str):
    """Each expected skill directory must exist in .qwen/skills/."""
    skill_dir = qwen_dir / "skills" / skill_name
    assert skill_dir.is_dir(), f"Skill directory not found: {skill_dir}"


@pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
def test_skill_has_skill_md(qwen_dir: Path, skill_name: str):
    """Each skill directory must contain a SKILL.md file."""
    skill_md = qwen_dir / "skills" / skill_name / "SKILL.md"
    assert skill_md.exists(), f"SKILL.md not found in {skill_name}/"


def _parse_frontmatter(content: str) -> dict[str, str] | None:
    """Extract YAML frontmatter from markdown content between --- markers."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        kv_match = re.match(r"^(\w[\w_-]*):\s*(.*)", line)
        if kv_match:
            frontmatter[kv_match.group(1)] = kv_match.group(2).strip()
    return frontmatter


@pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
def test_skill_frontmatter_has_name(qwen_dir: Path, skill_name: str):
    """Each SKILL.md must have a 'name' field in YAML frontmatter."""
    skill_md = qwen_dir / "skills" / skill_name / "SKILL.md"
    if not skill_md.exists():
        pytest.skip(f"SKILL.md not found for {skill_name}")
    content = skill_md.read_text(encoding="utf-8")
    fm = _parse_frontmatter(content)
    assert fm is not None, f"No YAML frontmatter found in {skill_name}/SKILL.md"
    assert "name" in fm, f"'name' field missing in {skill_name}/SKILL.md frontmatter"


@pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
def test_skill_frontmatter_has_description(qwen_dir: Path, skill_name: str):
    """Each SKILL.md must have a 'description' field in YAML frontmatter."""
    skill_md = qwen_dir / "skills" / skill_name / "SKILL.md"
    if not skill_md.exists():
        pytest.skip(f"SKILL.md not found for {skill_name}")
    content = skill_md.read_text(encoding="utf-8")
    fm = _parse_frontmatter(content)
    assert fm is not None, f"No YAML frontmatter found in {skill_name}/SKILL.md"
    assert "description" in fm, (
        f"'description' field missing in {skill_name}/SKILL.md frontmatter"
    )
