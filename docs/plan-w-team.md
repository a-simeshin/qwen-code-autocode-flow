# Plan With Team

`/plan-w-team` generates implementation plans for multi-agent execution. It analyzes requirements, interviews the user, reads the codebase, and produces a spec document that `/smart-build` can execute with a team of builder agents.

## Workflow

```mermaid
flowchart TD
    A["1. Analyze requirements"] --> C["2. Interview Round 1"]
    C --> D["3. Read codebase"]
    D --> E["4. Interview Round 2"]
    E --> F["5-8. Design, testing,<br/>team, tasks"]
    F --> G["9-10. Generate filename<br/>& save plan"]
    G --> H["11. Plan Review<br/>(structural + critic)"]
    H -->|FAIL| G
    H -->|PASS| I["12-13. Report &<br/>record knowledge"]
```

## Two-Round Requirements Interview

The planner asks clarifying questions when it detects ambiguities — not about everything, but about every point where two or more valid interpretations exist or where the prompt is underspecified.

The two rounds are separated by codebase reading — this injects new information between rounds and keeps each round focused on what's knowable at that stage.

### Round 1: After Analyzing Requirements

Questions about ambiguities in the user's request — before reading any code. Ask when:

- **Contradiction detected** — the prompt implies two mutually exclusive approaches
- **Underspecified behavior** — key user states (unauthorized, empty data, error) are not described
- **Multiple valid approaches** — present both with pros/cons, let user choose
- **Design/UX choices** — placement, copy, interaction details that are matters of taste
- **Scope ambiguity** — unclear whether adjacent features are in or out of scope

### Round 2: After Reading the Codebase

Questions about implementation choices visible from the code. Ask when:

- **Multiple patterns exist** — codebase has more than one way to solve this type of problem
- **Technical tradeoff with no clear winner** — both options valid, depends on unstated priorities
- **Integration ambiguity** — new feature fits in more than one place or way
- **Discovered edge case** — reading the code revealed a scenario the prompt didn't address

Skip a round entirely if every choice has a single obvious answer.

### Why Two Rounds, Not More

Research on multi-turn LLM interactions shows a consistent pattern: large gains in early interactions, diminishing returns by turns 3-5, and risk of degradation beyond that.

- **TiCoder** (Microsoft, ICSE 2024): m=1 gives +19pp, m=2 gives +7pp, m=3 gives +2pp. Plateau after 3 interactions.
- **LLMs Get Lost in Multi-Turn Conversation** (Microsoft, 2025): 39% average performance degradation in multi-turn vs single-turn. Consolidating information into fewer, richer turns outperforms distributing across many.
- **Another Turn, Better Output?** (NeurIPS 2025): targeted feedback sustains improvement; vague feedback plateaus or reverses quality.

Two rounds with new information between them is the sweet spot.

## Section Routing Catalog

Every task in a plan has a `**Stack**` field — keywords that tell the [context router](context-routing.md) which coding standards to load for the builder.

| Section | Trigger keywords | Add when task involves |
|---------|-----------------|----------------------|
| **Java** | | |
| `java-patterns#basics` | `java`, `spring`, `controller`, `entity`, `jpa` | Any Java/Spring Boot code |
| `java-patterns#errors` | `exception`, `error handling`, `controlleradvice` | Exception handling, HTTP errors |
| `java-patterns#java17` | `record`, `pattern matching`, `switch expression` | Java 17 features |
| `java-patterns#java21` | `virtual thread`, `sequenced collection` | Java 21 features |
| **Java Testing** | | |
| `java-testing#structure` | `assertj`, `allure`, `test naming`, `test structure` | Test organization, Allure annotations |
| `java-testing#integration` | `testcontainers`, `integration test`, `podman` | Integration tests with containers |
| `java-testing#http` | `mockmvc`, `resttemplate`, `http test` | REST endpoint testing |
| `java-testing#kafka` | `kafka test`, `consumer test`, `producer test` | Kafka testing |
| `java-testing#jdbc` | `database test`, `repository test`, `jdbc test` | Database testing |
| `java-testing#mockito` | `mockito`, `spy` | Unit tests with mocking |
| `java-testing#e2e` | `selenide`, `e2e`, `page object` | E2E browser testing |
| `java-testing#maven` | `surefire`, `failsafe`, `jacoco` | Maven test plugins, coverage |
| **React** | | |
| `react-patterns#core` | `react`, `component`, `hook`, `useState`, `useEffect`, `tsx` | Any React code |
| `react-patterns#nextjs` | `next.js`, `server component`, `app router` | Next.js App Router |
| `react-patterns#vite` | `vite`, `react-router`, `code splitting` | Vite, React Router |
| **Python** | | |
| `python-patterns#core` | `python`, `typing`, `dataclass`, `asyncio` | Any Python code |
| `python-patterns#fastapi` | `fastapi`, `pydantic`, `apirouter`, `depends` | FastAPI endpoints |
| `python-patterns#testing` | `pytest`, `fixture`, `parametrize`, `conftest` | Python testing |

## Plan Review (Step 11)

After saving the plan, `/plan-w-team` runs a two-stage review gate before proceeding. See [Plan Review](plan-review.md) for details on the 8 criteria.

## Plan Format

The generated plan includes these sections:

| Section | Content |
|---------|---------|
| Task Description | What needs to be done |
| Objective | What "done" looks like |
| Problem Statement | Why this work is needed *(medium/complex tasks)* |
| Solution Approach | How the objective will be achieved *(medium/complex tasks)* |
| Relevant Files | Existing files to modify + new files to create |
| Implementation Phases | Foundation → Core → Integration *(medium/complex tasks)* |
| Team Orchestration | Team members with roles and agent types |
| Step by Step Tasks | Ordered tasks with IDs, dependencies, Stack, assignments |
| Acceptance Criteria | Measurable completion conditions |
| Validation Commands | Shell commands to verify the work |

## Research

| Research | Direct relevance |
|----------|-----------------|
| [ClarifyGPT](https://dl.acm.org/doi/10.1145/3660810) (FSE 2024) | Detect ambiguities → ask targeted questions → GPT-4 Pass@1 +9.84pp. |
| [TiCoder](https://arxiv.org/abs/2404.10100) (ICSE 2024, Microsoft) | +19pp at m=1, +7pp at m=2, +2pp at m=3, plateau after 3. |
| [SpecFix](https://arxiv.org/abs/2505.07270) (ASE 2025) | Repairing ambiguous specs before generation: +30.9% Pass@1. |
| [LLMs Get Lost in Multi-Turn](https://arxiv.org/abs/2505.06120) (Microsoft, 2025) | 39% degradation in multi-turn. Validates two rounds, not five. |
| [Another Turn, Better Output?](https://arxiv.org/abs/2509.06770) (NeurIPS 2025) | Targeted feedback sustains gains; vague feedback plateaus. |

## Key Files

- `.qwen/skills/plan-w-team.md` — planner prompt with workflow, catalog, and plan format
- `.qwen/hooks/validators/validate_plan.py` — structural validator (8 checks including Stack)
- `.qwen/agents/team/plan-reviewer.md` — critic agent
- `.qwen/hooks/context_router.py` — keyword router that Stack fields feed into
- `.qwen/refs/*.md` — reference files with coding standards sections
