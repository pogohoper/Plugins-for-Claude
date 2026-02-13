# Orchestrator Plugin

Delegation-aware planning layer for Claude Code. Analyzes tasks, proposes a team of specialized agents, presents an editable plan, and executes only after your approval.

## Usage

```bash
# Load the plugin
claude --plugin-dir ./plugins/orchestrator

# Invoke the orchestrator
/orchestrator:orchestrate add a login page with OAuth2 support
```

## How It Works

1. **Analyze** — Scans the codebase and assesses task complexity
2. **Plan** — Selects agents, organizes into phases, writes `.claude/orchestration-plan.md`
3. **Review** — You edit the plan (remove agents, reorder phases, add notes)
4. **Execute** — Runs each phase, delegating to specialized subagents

## Agent Catalog

| Agent | Purpose |
|-------|---------|
| spec-writer | Translates requirements into structured specs |
| context-distiller | Produces compressed codebase context for other agents |
| implementer | Writes code per spec. Full tool access |
| validator | Tests against the running product |
| test-writer | Creates test cases (separate from runner) |
| test-runner | Executes tests, reports pass/fail |
| security-reviewer | OWASP top 10, secrets, injection, auth checks |
| code-reviewer | Style, architecture, DRY, readability |
| edge-case-hunter | Adversarial probing for failure modes |
| critic | Structured severity ratings, drives refinement loop |
| refiner | Fixes CRITICAL/MAJOR issues found by critic |
| dependency-analyst | Maps change impact and ripple effects |
| regression-guard | Runs targeted existing tests for regressions |

All agents run on opus with no turn limit — each agent uses as many turns as it needs.

Not all agents run every time. The orchestrator selects based on task complexity and type.

Custom ad-hoc agents can also be proposed when the predefined catalog doesn't cover a task's needs.

## Phases

| Phase | Agents | Parallelism |
|-------|--------|-------------|
| 1. Specification | spec-writer | — |
| 2. Context & Analysis | context-distiller, dependency-analyst | parallel |
| 3. Implementation | implementer, test-writer | parallel |
| 4. Quality Gates | security-reviewer, edge-case-hunter, test-runner, regression-guard | parallel |
| 5. Refinement | critic → refiner (max 3 iterations) | sequential |
| 6. Final Review | code-reviewer, validator | sequential |

Empty phases are omitted from the plan.

## Editing the Plan

After the orchestrator writes `.claude/orchestration-plan.md`, you can:

- Delete agent rows to skip them
- Delete entire phase sections
- Reorder phases by moving sections
- Change "parallel" to "sequential" on phase headers
- Add a `## Notes` section with extra instructions for any agent
- Add custom agents to the Custom Agents table and move them into phases

Say "approved" or "go" to execute.

## Testing

```bash
# Load with debug output
claude --plugin-dir ./plugins/orchestrator --debug

# Verify skill appears
# Type /orchestrator:orchestrate in the session
```
