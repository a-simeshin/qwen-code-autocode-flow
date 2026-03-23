# qwen-code-autocode-flow

Multi-agent automation framework for Qwen Code. Ported from [claude-code-hooks-mastery](https://github.com/a-simeshin/claude-code-hooks-mastery).

## Goal & Principles

1. **Automate every action** — planning, review, validation, and knowledge recording via LLM
2. **Control via deterministic scripts** — all actions governed by hard scripts, not LLM discretion
3. **Never delete files** — destructive operations prohibited at system level
4. **Document into project memory** — decisions and outcomes recorded
5. **Strict format validation** — plan structure and documentation verified before execution
6. **Stack-aware coding standards** — code conventions loaded dynamically based on detected technology stack

## Directory Structure

- `.qwen/hooks/` — Python hook scripts for all lifecycle events
- `.qwen/hooks/validators/` — 15 file-type-specific validators (ruff, eslint, spotless, etc.)
- `.qwen/hooks/utils/llm/` — LLM client wrappers (Anthropic, OpenAI, Ollama)
- `.qwen/agents/team/` — builder, validator, plan-reviewer agents
- `.qwen/agents/` — context-router, meta-agent
- `.qwen/skills/` — plan-w-team, smart-build, plan, all-tools
- `.qwen/refs/` — coding standards (Java, React, Python)
- `.qwen/output-styles/` — output format templates
- `specs/` — implementation plans
- `logs/` — execution logs

## Tool Names

| Tool | Name in Qwen Code |
|------|-------------------|
| Read file | `read_file` |
| Write file | `write_file` |
| Edit file | `edit` |
| Run shell | `run_shell_command` |
| Find files | `glob` |
| Search content | `grep_search` |
| Sub-agent | `agent` |

## Hook System

All hooks configured in `.qwen/settings.json`:
- **PreToolUse** — security gatekeeper (blocks rm -rf, .env access)
- **PostToolUse** — logging + validator dispatch
- **Stop** — transcript export
- **Notification** — logging
- **UserPromptSubmit** — prompt validation, session storage
- **SessionStart/End** — context loading, cleanup
- **PreCompact** — transcript backup
- **SubagentStop** — subagent completion logging
- **Setup** — dependency checks

## Agents

- **builder** — executes implementation tasks with auto-validation
- **validator** — read-only verification against acceptance criteria
- **plan-reviewer** — architectural review of plans (PASS/FAIL verdict)
- **context-router** — routes tasks to documentation sections
- **meta-agent** — generates new agent configurations

## Skills

- `/plan-w-team` — create plans with team orchestration and review gate
- `/smart-build` — execute plans with context routing (75% token savings)
- `/plan` — quick single-agent planning
- `/all-tools` — list available tools

## MCP Integrations (Optional)

- **Context7** — live documentation lookup for any library
- **Serena** — LSP-based semantic code navigation

These require separate MCP server configuration in Qwen Code settings.

## Key Workflow

/plan-w-team → plan review gate → /smart-build → validation
