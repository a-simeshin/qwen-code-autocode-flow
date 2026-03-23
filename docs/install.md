# Install / Uninstall

One-line installer that copies the `.qwen/` directory into your project.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/a-simeshin/qwen-code-autocode-flow/main/install.sh | bash
```

## Non-Interactive Install

For CI pipelines or automation:

```bash
NONINTERACTIVE=1 bash install.sh
```

## What Gets Installed

```
.qwen/
├── skills/            — slash commands (plan-w-team, smart-build, etc.)
├── agents/team/       — agent definitions (builder, validator, plan-reviewer)
├── hooks/             — context router, section loader, validators
├── refs/              — coding standards (Java, React, Python)
├── output-styles/     — output format templates
├── settings.json      — hook configuration
specs/                 — implementation plans
logs/                  — execution logs
```

## Uninstall

```bash
rm -rf .qwen
```

Removes the `.qwen/` directory and all installed files.

## Prerequisites

- Qwen Code — CLI tool
- [Astral UV](https://docs.astral.sh/uv/) — auto-installed by the script if missing
- Node.js, Git

## Optional Dependencies

| Tool | What for | Install |
|------|----------|---------|
| [Context7](context7.md) | Live documentation lookup | Add MCP server to config |
| [Serena](serena.md) | Semantic code navigation | Add MCP server to config |
