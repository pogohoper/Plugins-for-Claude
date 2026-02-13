# Agent Collaboration Best Practices

A guide to effective multi-agent coordination in Claude Code — subagent delegation, agent teams, persistent memory, and patterns for building robust agent workflows.

---

## Table of Contents

1. [Subagent Types & When to Use Each](#subagent-types--when-to-use-each)
2. [Agent Communication Patterns](#agent-communication-patterns)
3. [Parallel Execution](#parallel-execution)
4. [Persistent Memory](#persistent-memory)
5. [Context Management](#context-management)
6. [Agent Teams (Experimental)](#agent-teams-experimental)
7. [Delegation Chains](#delegation-chains)
8. [Hook-Enforced Quality](#hook-enforced-quality)
9. [CLAUDE.md for Agent Coordination](#claudemd-for-agent-coordination)
10. [Anti-Patterns & Pitfalls](#anti-patterns--pitfalls)
11. [Sizing Tasks](#sizing-tasks)

---

## Subagent Types & When to Use Each

Claude Code provides several built-in subagent types via the `Task` tool, plus the ability to define custom agents.

### Built-in Subagent Types

| Type | Tools Available | Best For |
|------|----------------|----------|
| **Explore** | Read-only: Glob, Grep, Read, WebFetch, WebSearch | Fast codebase exploration, finding files, understanding patterns. Cannot modify files. |
| **Plan** | Read-only: Glob, Grep, Read, WebFetch, WebSearch | Designing implementation plans, identifying critical files, architectural analysis. |
| **general-purpose** | All tools (Read, Write, Edit, Bash, Glob, Grep, etc.) | Full implementation tasks, multi-step work requiring file modifications. |
| **Bash** | Bash only | Running commands, git operations, build steps, system tasks. |
| **code-simplifier** | All tools | Refining and simplifying recently modified code. |

### Decision Framework

```
Need to find or understand code?
  → Explore (fast, read-only, no risk)

Need to plan before implementing?
  → Plan (research + architecture, read-only)

Need to modify code or run commands?
  → general-purpose (full tool access)

Need just a single command?
  → Bash (minimal overhead)

Have a custom workflow?
  → Define a custom agent
```

### Custom Agents

Define in `.claude/agents/my-agent.md` with YAML frontmatter:

```markdown
---
name: my-agent
description: What this agent does
tools: [Read, Grep, Glob]
model: sonnet
maxTurns: 15
memory: project
---

Agent instructions here.
```

Custom agents are referenced by name in skills (`agent: my-agent`) or the Task tool (`subagent_type: "my-agent"`).

---

## Agent Communication Patterns

### Main Session Orchestration

The most common pattern: the main session acts as orchestrator, delegating to subagents and synthesizing results.

```
Main Session (orchestrator)
  ├── Task(Explore) → "Find all API endpoints"
  │     └── Returns: list of endpoints
  ├── Task(Explore) → "Find all database models"
  │     └── Returns: list of models
  └── Main session synthesizes both results
      and continues work
```

**Key principle**: The main session sees only the subagent's final output, not its intermediate steps. Write prompts that ask for specific, structured outputs.

### Result Passing

Subagent results return as text to the main session. For structured data:

- **Ask for JSON** when the main session needs to parse results programmatically
- **Ask for markdown** when results will be shown to the user or used in further conversation
- **Ask for specific formats** like file lists, code blocks, or tables

Good prompt:
```
Find all files that import from 'auth' module. Return a JSON array
of objects with "file", "line", and "import_statement" fields.
```

Bad prompt:
```
Look at the auth stuff.
```

### File-Based State Sharing

When subagents need to share complex state, use files as the communication medium:

```
Subagent A: Writes analysis to .claude/temp/analysis.json
Subagent B: Reads .claude/temp/analysis.json, acts on it
Main session: Reads final results, cleans up temp files
```

This pattern is useful when:
- Data is too large for a return message
- Multiple subagents need access to the same state
- You want an audit trail of intermediate results

---

## Parallel Execution

### When to Parallelize

Launch multiple subagents simultaneously when tasks are **independent** — they don't depend on each other's results.

**Good candidates for parallelism:**
- Searching different parts of the codebase
- Running different types of analysis (security, performance, style)
- Fetching information from different sources
- Implementing changes in unrelated files

**Bad candidates (run sequentially instead):**
- Task B needs Task A's output to determine what to do
- Both tasks modify the same files (conflict risk)
- One task creates a file that the other reads

### Parallel Subagent Launches

In the main session, launch multiple Task calls in a single response:

```
// These launch simultaneously because they're independent
Task(Explore, "Find all React components in src/")
Task(Explore, "Find all API routes in routes/")
Task(Bash, "npm test -- --reporter json")
```

All three run concurrently. Results return as they complete.

### Parallelism Limits

- Subagents are independent — they cannot communicate with each other directly
- Each subagent gets its own context window (no shared conversation state)
- File conflicts can occur if two subagents write to the same file — avoid this by design
- There's a practical concurrency limit — launching too many subagents at once may degrade performance

---

## Persistent Memory

### Memory Scopes

Claude Code agents can persist knowledge across sessions using the `memory` field:

| Scope | Storage Location | Use Case |
|-------|-----------------|----------|
| `user` | `~/.claude/memory/MEMORY.md` | Personal preferences, workflows, cross-project patterns |
| `project` | `.claude/memory/MEMORY.md` | Project-specific knowledge, architecture decisions, conventions |
| `local` | `.claude/local/memory/MEMORY.md` | Machine-specific settings (e.g., local paths, env vars) |

### MEMORY.md Conventions

Structure memory files for scanability:

```markdown
# Project Memory

## Architecture
- Monorepo with packages in `packages/`
- Shared types in `packages/shared/types/`
- API server is Express + TypeScript

## Conventions
- Use barrel exports (index.ts) for all packages
- Error handling: always use AppError class from shared
- Tests: colocated with source files as `*.test.ts`

## Key Decisions
- 2024-01: Migrated from REST to GraphQL for client API
- 2024-03: Adopted Zod for runtime validation

## Learned Insights
- The auth middleware must run before rate limiting
- Database migrations must be backward-compatible (rolling deploys)
```

### Memory Curation Strategies

Memory files can grow large. Curate them:

1. **Date entries**: Add timestamps so you can prune old information
2. **Categorize**: Group by topic (architecture, conventions, gotchas)
3. **Prune actively**: Remove outdated information rather than appending indefinitely
4. **Prioritize "why"**: Record reasoning behind decisions, not just the decisions themselves
5. **Keep it scannable**: Use headers, bullet points, and short entries

### Custom Memory Directories

For specialized agents (like the Persistent Agent plugin), create dedicated memory directories:

```
.claude/agent-memory/
├── auth-expert/
│   ├── MEMORY.md
│   ├── structure.md
│   └── domain.json
└── db-expert/
    ├── MEMORY.md
    ├── structure.md
    └── domain.json
```

This keeps domain-specific knowledge separate from general project memory.

---

## Context Management

### What Subagents Inherit

| Inherited | Not Inherited |
|-----------|---------------|
| CLAUDE.md instructions (all levels) | Parent conversation history |
| MCP server connections | Previously read file contents |
| Plugin configurations | Parent's tool call results |
| Project-level settings | Parent's in-memory state |

### Implications

Since subagents **don't** get conversation history:

- **Be explicit in prompts**: Don't say "fix the bug we discussed" — instead, describe the bug fully
- **Include file paths**: Don't say "that file" — say "src/auth/middleware.ts"
- **Provide context**: If the subagent needs background, include it in the Task prompt
- **Don't assume state**: A subagent doesn't know what files you've already read

Since subagents **do** get CLAUDE.md:

- Use CLAUDE.md to set consistent rules that all agents follow
- Project conventions, code style, and safety rules propagate automatically
- No need to repeat these in every Task prompt

### Skill Injection

When a skill specifies `context: fork`, the skill's body becomes the subagent's initial prompt. Combine with `agent` to pre-configure the subagent:

```yaml
context: fork
agent: domain-expert  # Sets tools, model, permissions
```

The subagent receives:
1. The agent definition's system instructions
2. The skill's body (with substitutions applied)
3. CLAUDE.md rules (inherited)

---

## Agent Teams (Experimental)

Agent teams allow multiple agents to work on a shared task list with direct messaging.

### Enabling Agent Teams

Agent teams are an experimental feature. Enable with the environment variable:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Or via CLI flag:

```bash
claude --agent-team
```

### How Teams Work

1. **Shared task list**: All agents see the same task list (TaskCreate, TaskList, TaskUpdate)
2. **Task claiming**: Agents claim tasks by setting `owner` to their agent ID
3. **Direct messaging**: Agents can send messages to each other through the task system
4. **Parallel work**: Multiple agents work simultaneously on different tasks

### Team Workflow

```
Main session creates task list
  ├── Agent A claims Task #1 → works on it → marks complete
  ├── Agent B claims Task #2 → works on it → marks complete
  ├── Agent C claims Task #3 → discovers blocker → creates new task
  └── Main session monitors progress, resolves blockers
```

### Display Modes

Agent teams support multiple display modes:
- `auto`: Split panes if in tmux/iTerm2, otherwise in-process
- `in-process`: All in main terminal (Shift+Up/Down to navigate between teammates)
- `tmux`: Split panes in tmux or iTerm2

### Limitations

- **Experimental**: Behavior may change between versions
- **No session resumption**: If the session ends, agent teams cannot be resumed — in-process teammates are lost
- **One team per session**: Cannot run nested teams or multiple teams simultaneously
- **File conflicts**: Multiple agents writing to the same file can cause conflicts — coordinate via task dependencies
- **Context isolation**: Team agents don't share conversation context, only the task list
- **No per-teammate permission modes**: Permission settings apply at team spawn time, not per-agent
- **Coordination overhead**: For small tasks, the overhead of coordination exceeds the benefit
- **Split panes require tmux/iTerm2**: Full visual split only works in supported terminals

---

## Delegation Chains

### Sequential Pipeline: Research → Implement → Verify

A common pattern for complex features:

```
Step 1: Task(Explore) → "Research how auth middleware works"
        Returns: analysis of current auth system

Step 2: Task(general-purpose) → "Implement OAuth2 support based on this analysis: {step1_result}"
        Returns: implementation summary

Step 3: Task(Bash) → "npm test -- --grep 'OAuth'"
        Returns: test results

Step 4: Main session reviews results and follows up
```

### Fan-Out / Fan-In

Research multiple areas in parallel, then synthesize:

```
Fan-out (parallel):
  Task(Explore) → "Analyze auth module"
  Task(Explore) → "Analyze API module"
  Task(Explore) → "Analyze database module"

Fan-in (sequential, after all complete):
  Main session synthesizes all three analyses
  Task(general-purpose) → "Implement cross-cutting change based on: {combined_analysis}"
```

### Expert Consultation Chain

Use domain expert agents as advisors during implementation:

```
Step 1: /consult auth-expert "How should I add OAuth2 support?"
        Returns: expert advice with specific file references

Step 2: Implement based on expert advice

Step 3: /consult auth-expert "Review my OAuth2 implementation"
        Returns: expert review with suggestions

Step 4: Apply suggestions
```

---

## Hook-Enforced Quality

### SubagentStop Gate

Validate subagent results before accepting them:

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python validate_agent_output.py",
            "statusMessage": "Validating agent output..."
          }
        ]
      }
    ]
  }
}
```

### TaskCompleted Validation

Run checks when tasks are marked complete:

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python verify_task.py \"$TASK_ID\"",
            "statusMessage": "Verifying task deliverables..."
          }
        ]
      }
    ]
  }
}
```

### PreToolUse Safety

Prevent dangerous operations:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python check_safe_command.py",
            "statusMessage": "Checking command safety..."
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python check_file_allowed.py \"$TOOL_INPUT_FILE_PATH\"",
            "statusMessage": "Checking file permissions..."
          }
        ]
      }
    ]
  }
}
```

### PostToolUse Notification

Notify domain agents when their files change:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python check_domain.py \"$TOOL_INPUT_FILE_PATH\"",
            "statusMessage": "Checking domain territories..."
          }
        ]
      }
    ]
  }
}
```

---

## CLAUDE.md for Agent Coordination

### Shared Instructions

CLAUDE.md files at different levels provide shared rules for all agents:

```
~/.claude/CLAUDE.md           # User-wide rules (all projects)
./CLAUDE.md                    # Project root rules
./src/CLAUDE.md                # Directory-specific rules
./.claude/CLAUDE.md            # Project config rules
```

All agents (main session, subagents, team agents) inherit these instructions.

### Modular Rules with Imports

Keep CLAUDE.md focused by importing specialized rules:

```markdown
# CLAUDE.md

## Project Rules
- Use TypeScript strict mode
- All functions must have JSDoc comments

## Imports
@import .claude/rules/testing.md
@import .claude/rules/security.md
@import .claude/rules/api-conventions.md
```

### Agent-Specific Sections

Use CLAUDE.md to give different instructions to different agent roles:

```markdown
## For All Agents
- Never modify files in `config/production/`
- Always use the project's ESLint configuration

## For Code Review Agents
- Focus on security and performance
- Check for proper error handling

## For Implementation Agents
- Write tests for all new functions
- Update relevant documentation
```

---

## Anti-Patterns & Pitfalls

### No Nested Subagents

Subagents **cannot** launch their own subagents. The Task tool is not available inside a subagent.

```
Main → Task(general-purpose) → Task(Explore)  ← THIS FAILS
```

If you need multi-level delegation, orchestrate from the main session:

```
Main → Task(Explore) → result
Main → Task(general-purpose, using explore result) → result
```

### No Parent History in Subagents

Subagents start with a blank conversation. Don't write prompts that assume context:

```
# BAD
Task: "Fix the bug we found earlier"

# GOOD
Task: "Fix the null pointer exception in src/auth/login.ts:42
       where user.email is accessed before null check"
```

### Agent Team Resumption

Agent teams cannot be resumed after a session ends. All team state (task list, agent assignments) is lost. For work that spans sessions:

- Use file-based state (write progress to `.claude/state/`)
- Use memory files to record what was accomplished
- Design tasks to be independently resumable

### File Conflict Prevention

Multiple agents writing to the same file causes conflicts. Prevent this by:

1. **Assign file ownership**: Each agent works on specific files
2. **Use task dependencies**: `addBlockedBy` ensures sequential access
3. **Coordinate in task descriptions**: "This task modifies `src/auth/` — no other agent should edit these files"
4. **Use read-only agents**: Domain experts with `Read, Grep, Glob` only cannot create write conflicts

### Oversized Subagent Prompts

Don't dump entire file contents into Task prompts. Instead:

```
# BAD
Task: "Here is the entire 500-line file: {file_content}. Fix line 42."

# GOOD
Task: "Fix the null check at src/auth/login.ts:42.
       Read the file to understand context, then fix the bug."
```

Subagents can read files themselves — let them do it.

### Over-Delegation

Not every task needs a subagent. Simple operations are faster done directly:

```
# Over-delegation (slow)
Task(Bash): "git status"

# Just do it directly
Bash: git status
```

Reserve subagents for tasks that genuinely benefit from isolation, parallelism, or specialization.

---

## Sizing Tasks

### When to Use Direct Tools (No Delegation)

- Reading a specific file
- Making a small edit
- Running a single command
- Simple searches with known targets

### When to Use a Subagent

- Multi-step research requiring several file reads and searches
- Tasks that benefit from context isolation (separate concern)
- Work that can run in parallel with other tasks
- Specialized analysis (security review, performance audit)

### When to Use Agent Teams

- Large tasks with 5+ independent work items
- Tasks that benefit from true parallel execution with coordination
- Complex projects where different agents bring different expertise
- When you want agents to claim and complete tasks autonomously

### Coordination Overhead

Each layer of delegation adds overhead:

| Approach | Overhead | Best For |
|----------|----------|----------|
| Direct tools | None | Simple, fast operations |
| Single subagent | Low (prompt + result) | Focused, isolated tasks |
| Sequential subagents | Medium (multiple round-trips) | Pipelines with dependencies |
| Parallel subagents | Medium (launch + collect) | Independent concurrent work |
| Agent teams | High (task list + messaging) | Large, complex projects |

**Rule of thumb**: Use the simplest approach that gets the job done. Don't use agent teams for a task that one subagent could handle.
