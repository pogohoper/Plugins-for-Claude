# Claude Code Plugin & Skill System Reference

A comprehensive reference for building plugins, skills, custom agents, and hooks in Claude Code.

---

## Table of Contents

1. [Skills](#skills)
2. [Plugins](#plugins)
3. [Custom Agents](#custom-agents)
4. [Hooks System](#hooks-system)
5. [MCP Server Integration](#mcp-server-integration)
6. [Plugin Lifecycle](#plugin-lifecycle)
7. [Practical Patterns](#practical-patterns)

---

## Skills

Skills are reusable prompt templates that extend Claude Code with specialized capabilities. Each skill is defined in a `SKILL.md` file with YAML frontmatter and a markdown body.

### SKILL.md Anatomy

```markdown
---
name: my-skill
description: A brief description shown in skill listings
user-invocable: true
argument-hint: "<arg1> <arg2>"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
model: sonnet
context: fork
agent: my-custom-agent
disable-model-invocation: false
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      command: "echo 'file changed'"
---

# Skill Title

Instructions for Claude when this skill is invoked.
Use $ARGUMENTS for the full argument string.
Use $1, $2, etc. for positional arguments.
```

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique skill identifier. Used in `/name` invocation. |
| `description` | string | Yes | Short description shown in skill listings and help. |
| `user-invocable` | boolean | No | If `true`, users can invoke via `/name`. Default: `false`. Non-invocable skills are only used by other skills or agents. |
| `argument-hint` | string | No | Placeholder text shown after `/name` in the UI (e.g., `"<file> <message>"`). |
| `allowed-tools` | list | No | Restricts which tools the skill can use. If omitted, all tools are available. |
| `model` | string | No | Override the model for this skill. Values: `opus`, `sonnet`, `haiku`. |
| `context` | string | No | Set to `fork` to run the skill in an isolated subagent context. The subagent gets a fresh conversation with the skill prompt injected. |
| `agent` | string | No | When `context: fork` is set, specifies which custom agent definition to use for the subagent. References an agent by name from `.claude/agents/` or plugin `agents/`. |
| `disable-model-invocation` | boolean | No | If `true`, Claude cannot autonomously invoke this skill — only explicit `/name` works. Default: `false`. |
| `hooks` | object | No | Skill-scoped hooks that only fire during this skill's execution. Same structure as global hooks. |

### String Substitutions

Skills support variable substitution in their body text:

| Variable | Description | Example |
|----------|-------------|---------|
| `$ARGUMENTS` | The full argument string passed after the skill name | `/deploy staging --force` → `"staging --force"` |
| `$0` | The skill name itself | `"deploy"` |
| `$1`, `$2`, ... `$N` | Positional arguments (space-separated) | `/deploy staging prod` → `$1="staging"`, `$2="prod"` |
| `${CLAUDE_SESSION_ID}` | The current Claude Code session ID | `"a1b2c3d4-..."` |
| `${CLAUDE_PLUGIN_ROOT}` | Absolute path to the plugin's root directory (only in plugin skills) | `"/home/user/.claude/plugins/my-plugin"` |

### Dynamic Context Injection

Skills can inject live data into their prompt using the `` !`command` `` syntax. The command runs at skill load time and its stdout replaces the expression.

```markdown
## Current Branch
!`git branch --show-current`

## Recent Commits
!`git log --oneline -5`

## Project Dependencies
!`cat package.json | jq '.dependencies'`
```

This is powerful for grounding skills in the current project state without hardcoding values.

### Skill Discovery & Registration

Claude Code discovers skills from multiple locations, checked in this order:

| Priority | Location | Scope |
|----------|----------|-------|
| 1 (highest) | `.claude/skills/` (project) | Project-specific skills |
| 2 | `~/.claude/skills/` (user) | User-wide personal skills |
| 3 | Plugin `skills/` directories | Installed plugin skills |

**Naming conventions:**
- Each skill lives in its own directory: `skills/my-skill/SKILL.md`
- The directory name is the skill identifier
- Names should be lowercase with hyphens: `register-domain`, `run-tests`

**Precedence:** If two skills share the same name, the higher-priority location wins. A project skill named `deploy` overrides a user-level or plugin skill named `deploy`.

**Plugin namespacing:** Plugin skills appear as `/plugin-name:skill-name`. For example, a skill `review` in plugin `my-plugin` is invoked as `/my-plugin:review`.

**Legacy commands:** `.claude/commands/<name>.md` files are still supported alongside the newer `skills/` directory structure.

### Tool Restrictions

The `allowed-tools` field limits which tools a skill can access:

```yaml
allowed-tools:
  - Read
  - Grep
  - Glob
```

Available tool names: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebFetch`, `WebSearch`, `Task`, `NotebookEdit`.

When a skill is invoked with tool restrictions, Claude cannot use tools outside the allowed list, even if the user's permission mode would normally allow them.

### Forked Context

Setting `context: fork` runs the skill in an isolated subagent:

```yaml
context: fork
agent: domain-expert
```

**What the subagent gets:**
- The skill's body as its initial prompt
- CLAUDE.md instructions (inherited from main session)
- MCP servers (inherited)
- The specified agent definition (if `agent` is set)

**What the subagent does NOT get:**
- The parent's conversation history
- Previously read files or tool results from the parent session

The subagent executes, produces a result, and returns it to the main session. The main session sees only the final output, not the subagent's internal tool calls.

---

## Plugins

Plugins package skills, agents, hooks, and MCP servers into distributable units.

### Plugin Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (required)
├── skills/
│   ├── skill-one/
│   │   └── SKILL.md
│   └── skill-two/
│       └── SKILL.md
├── agents/
│   └── my-agent.md
├── hooks/
│   └── hooks.json
├── .mcp.json                # MCP server configuration
├── .lsp.json                # LSP server configuration
├── scripts/                 # Supporting scripts
│   └── helper.py
└── README.md
```

### Plugin Manifest (`plugin.json`)

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin does",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://github.com/you"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/you/my-plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "skills": [
    "skills/skill-one/SKILL.md",
    "skills/skill-two/SKILL.md"
  ],
  "agents": [
    "agents/my-agent.md"
  ],
  "hooks": [
    "hooks/hooks.json"
  ],
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/mcp-server/index.js"]
    }
  },
  "lspServers": {
    "my-lsp": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/lsp/server.js"],
      "languages": ["typescript", "javascript"]
    }
  },
  "outputStyles": {
    "codeBlocks": "fenced",
    "maxLineWidth": 100
  }
}
```

### Manifest Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Plugin identifier (lowercase, hyphens). Used for namespacing: skills appear as `/plugin-name:skill-name`. |
| `version` | string | Yes | Semantic version (e.g., `"1.0.0"`). |
| `description` | string | Yes | Human-readable description. |
| `author` | string or object | No | Author name (string) or object with `name`, `email`, `url` fields. |
| `homepage` | string | No | URL to plugin documentation. |
| `repository` | string | No | URL to source repository. |
| `license` | string | No | License identifier (e.g., `"MIT"`). |
| `keywords` | string[] | No | Tags for marketplace search. |
| `skills` | string or string[] | No | Relative path(s) to SKILL.md files or skill directories. Supplements default `skills/` directory. |
| `agents` | string or string[] | No | Relative path(s) to agent definition files or agent directories. |
| `hooks` | string or string[] | No | Relative path(s) to hooks.json files. |
| `mcpServers` | object or string | No | MCP server configurations (inline object or path to `.mcp.json`). |
| `lspServers` | object or string | No | LSP server configurations (inline object or path to `.lsp.json`). |
| `outputStyles` | object or string | No | Output formatting preferences. |

**Note**: All relative paths must start with `./` and reference files within the plugin directory. Plugins are cached (copied) on install — files outside the plugin directory are not accessible unless symlinked.

### `${CLAUDE_PLUGIN_ROOT}` Variable

In plugin configurations, `${CLAUDE_PLUGIN_ROOT}` resolves to the absolute path of the plugin's root directory. Use this to reference scripts, servers, and other files relative to the plugin:

```json
{
  "command": "python",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/my-script.py"]
}
```

---

## Custom Agents

Custom agents define specialized subagent profiles that can be referenced by skills or the Task tool.

### Agent Definition File

Agent definitions live in `.claude/agents/` (project-level) or `~/.claude/agents/` (user-level), or in a plugin's `agents/` directory. Each is a markdown file with YAML frontmatter.

```markdown
---
name: code-reviewer
description: Reviews code for quality, security, and best practices
tools:
  - Read
  - Grep
  - Glob
disallowedTools:
  - Write
  - Edit
  - Bash
model: sonnet
permissionMode: default
maxTurns: 20
skills:
  - review-checklist
memory: project
hooks:
  PostToolUse:
    - matcher: "Read"
      command: "echo 'File read by reviewer'"
mcpServers:
  linter:
    command: "npx"
    args: ["eslint-mcp-server"]
---

# Code Reviewer Agent

You are a code review specialist. Analyze code for:
1. Security vulnerabilities
2. Performance issues
3. Code style and consistency
4. Potential bugs

Provide specific, actionable feedback with file paths and line numbers.
```

### Agent Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Agent identifier. Referenced by `agent` field in skills or `subagent_type` in Task. |
| `description` | string | What this agent does. Shown when listing available agents. |
| `tools` | string[] | Allowed tools (allowlist). If set, only these tools are available. |
| `disallowedTools` | string[] | Blocked tools (blocklist). Cannot be used with `tools`. |
| `model` | string | Model override: `opus`, `sonnet`, `haiku`. |
| `permissionMode` | string | Permission mode for tool execution. |
| `maxTurns` | integer | Maximum agentic turns before the agent stops. |
| `skills` | string[] | Skills available to this agent (by name). |
| `memory` | string | Memory scope: `user`, `project`, or `local`. |
| `hooks` | object | Agent-scoped hooks. |
| `mcpServers` | object | MCP servers available to this agent. |

### Memory Scopes

The `memory` field controls what persistent memory the agent can access:

| Scope | Location | Persists Across |
|-------|----------|-----------------|
| `user` | `~/.claude/memory/` | All projects |
| `project` | `.claude/memory/` | This project only |
| `local` | `.claude/local/memory/` | This machine + project |

Memory is stored in `MEMORY.md` files within these directories. Agents can read and write to their memory scope, allowing knowledge to persist across sessions.

---

## Hooks System

Hooks let you run commands, prompts, or agents in response to Claude Code events. They provide guardrails, automation, and quality gates.

### Hook Events

| Event | Fires When | Supports Matcher | Can Block |
|-------|------------|------------------|-----------|
| `SessionStart` | Session begins or resumes | Yes (`startup`, `resume`, `clear`, `compact`) | No |
| `UserPromptSubmit` | User submits a prompt | No | Yes |
| `PreToolUse` | Before a tool is executed | Yes (tool name regex) | Yes |
| `PermissionRequest` | Permission dialog is shown | Yes (tool name regex) | Yes |
| `PostToolUse` | After a tool succeeds | Yes (tool name regex) | No |
| `PostToolUseFailure` | After a tool fails | Yes (tool name regex) | No |
| `Notification` | A notification is sent | Yes (`permission_prompt`, `idle_prompt`, etc.) | No |
| `SubagentStart` | A subagent is about to launch | Yes (agent type name) | No |
| `SubagentStop` | A subagent has finished | Yes (agent type name) | Yes |
| `TaskCompleted` | A task is marked complete | No | Yes |
| `Stop` | Claude finishes its response | No | Yes |
| `TeammateIdle` | Agent team teammate goes idle | No | Yes |
| `PreCompact` | Before context compaction | Yes (`manual`, `auto`) | No |
| `SessionEnd` | Session terminates | Yes (exit reason) | No |

### Hook Configuration

Hooks are defined in settings or `hooks.json` files. Each event maps to an array of matcher objects, each containing a `hooks` array of actions to run.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python validate_command.py",
            "statusMessage": "Validating command...",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python check_style.py \"$TOOL_INPUT_FILE_PATH\"",
            "statusMessage": "Checking code style..."
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Session ending'"
          }
        ]
      }
    ]
  }
}
```

### Hook Structure

Each event entry has two levels:

1. **Matcher level** — filters which tool/event triggers the hook:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `matcher` | string | No | Regex pattern matched against tool name. Omit or use `*` to match all. Case-sensitive. MCP tools use `mcp__<server>__<tool>` format. |
| `hooks` | array | Yes | Array of hook actions to execute when matched. |

2. **Hook action level** — defines what to run:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | `"command"` (shell command), `"prompt"` (single-turn LLM evaluation), or `"agent"` (multi-turn subagent). |
| `command` | string | Yes* | Shell command to execute (for `type: "command"`). Receives JSON context on stdin. |
| `prompt` | string | Yes* | Prompt text for LLM evaluation (for `type: "prompt"`). Returns `{"ok": true/false, "reason": "..."}`. |
| `agent` | string | Yes* | Agent name to launch (for `type: "agent"`). Same response format as prompt. |
| `timeout` | number | No | Timeout in seconds. |
| `statusMessage` | string | No | Message shown in the UI while the hook runs. |

### Exit Codes (Command Hooks)

Command hooks communicate results via exit codes and stdout/stderr:

| Exit Code | Behavior |
|-----------|----------|
| `0` | Success. Hook can return JSON on stdout with control fields (see below). |
| `2` | Blocking error. Stderr is fed to Claude. The tool call or action is blocked. |
| Other | Non-blocking. Stderr shown in verbose mode. Execution continues. |

### Hook JSON Output (Exit Code 0)

Command hooks can return JSON on stdout to influence behavior:

**PreToolUse** — control whether the tool proceeds:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "reason text",
    "updatedInput": { "field": "new_value" },
    "additionalContext": "context for Claude"
  }
}
```

**PostToolUse / Stop / SubagentStop** — provide feedback:
```json
{
  "decision": "block",
  "reason": "explanation",
  "additionalContext": "context for Claude"
}
```

**UserPromptSubmit / SessionStart** — inject context or block:
```json
{
  "additionalContext": "text added to context",
  "decision": "block",
  "reason": "explanation"
}
```

### Hook Input (stdin)

Command hooks receive a JSON object on stdin with common fields:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse"
}
```

### Hook Environment Variables

| Variable | Available In | Description |
|----------|-------------|-------------|
| `$TOOL_NAME` | PreToolUse, PostToolUse | Name of the tool being used |
| `$TOOL_INPUT_FILE_PATH` | PreToolUse, PostToolUse | File path argument (for file-based tools) |
| `$TOOL_INPUT` | PreToolUse, PostToolUse | Full tool input as JSON |
| `$TOOL_OUTPUT` | PostToolUse | Tool output/result |
| `$SESSION_ID` | All events | Current session ID |
| `$CLAUDE_PROJECT_DIR` | All events | Project root directory |
| `${CLAUDE_PLUGIN_ROOT}` | Plugin hooks | Plugin root directory |
| `$CLAUDE_ENV_FILE` | SessionStart only | File path for persisting environment variables |

---

## MCP Server Integration

Plugins can bundle MCP (Model Context Protocol) servers that provide additional tools to Claude Code.

### Configuration in `.mcp.json`

```json
{
  "mcpServers": {
    "my-database": {
      "command": "python",
      "args": ["${CLAUDE_PLUGIN_ROOT}/mcp/db_server.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "5432"
      }
    },
    "my-api": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/mcp/api_server.js"],
      "cwd": "${CLAUDE_PLUGIN_ROOT}"
    }
  }
}
```

### MCP in Plugins

MCP servers defined in a plugin's `plugin.json` or `.mcp.json` are automatically available to:
- All skills in the plugin
- All agents in the plugin
- Subagents forked by plugin skills (inherited)

They are **not** available to unrelated skills or agents outside the plugin unless the user's global MCP config includes them.

### `${CLAUDE_PLUGIN_ROOT}` in MCP

Use `${CLAUDE_PLUGIN_ROOT}` in MCP configurations to reference server scripts relative to the plugin:

```json
{
  "command": "python",
  "args": ["${CLAUDE_PLUGIN_ROOT}/servers/my_server.py"]
}
```

This resolves to the plugin's absolute path at runtime, making plugins portable across machines.

---

## Plugin Lifecycle

### 1. Create

Start with the directory structure:

```bash
mkdir -p my-plugin/.claude-plugin
mkdir -p my-plugin/skills/my-skill
mkdir -p my-plugin/agents
mkdir -p my-plugin/hooks
```

Write `plugin.json`, SKILL.md files, agent definitions, and hooks.

### 2. Test Locally

Use the `--plugin-dir` flag to load a plugin from a local directory:

```bash
claude --plugin-dir ./my-plugin
```

This loads the plugin without installing it, allowing rapid iteration. Skills appear in `/help`, hooks fire, and MCP servers start.

### 3. Version

Follow semantic versioning in `plugin.json`:

```json
{
  "version": "1.0.0"
}
```

- **Patch** (1.0.x): Bug fixes, wording changes
- **Minor** (1.x.0): New skills, non-breaking features
- **Major** (x.0.0): Breaking changes, removed skills, renamed commands

### 4. Distribute

Plugins can be distributed via:
- **Git repository**: Users clone and point `--plugin-dir` at it
- **Claude plugin marketplace**: `claude plugin publish` (when available)
- **npm/pip packages**: Bundle as a package with the plugin directory included

### 5. Install

```bash
claude plugin install <source> [-s user|project|local]
```

Installed plugins are stored in `~/.claude/plugins/` and loaded automatically in all sessions. The `-s` flag controls install scope:
- `user` (default): Available in all projects
- `project`: Available only in this project
- `local`: Available only on this machine for this project

### 6. Manage

```bash
claude plugin list                           # List installed plugins
claude plugin install <plugin> [-s scope]    # Install a plugin
claude plugin uninstall <plugin> [-s scope]  # Uninstall a plugin
claude plugin enable <plugin> [-s scope]     # Enable a disabled plugin
claude plugin disable <plugin> [-s scope]    # Disable without removing
claude plugin update <plugin> [-s scope]     # Update to latest version
```

**Testing multiple plugins:**
```bash
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
claude --debug  # See plugin loading details
```

---

## Practical Patterns

### Domain Expert Skill

A skill that creates a read-only subagent specialized in a code area:

```yaml
---
name: ask-expert
context: fork
agent: domain-expert
allowed-tools: [Read, Grep, Glob]
user-invocable: true
argument-hint: "<area> <question>"
---
Answer the user's question about the $1 area of the codebase.
```

### Deployment Skill

A skill that automates deployment with safety checks:

```yaml
---
name: deploy
user-invocable: true
argument-hint: "<environment>"
allowed-tools: [Bash, Read]
hooks:
  PreToolUse:
    - matcher: "Bash"
      command: "python validate_deploy_command.py"
---
Deploy to $1.

Current branch: !`git branch --show-current`
Last commit: !`git log --oneline -1`

Only deploy if on main branch. Run tests first.
```

### Research Skill

A skill that forks a research agent to investigate a topic:

```yaml
---
name: research
context: fork
model: opus
user-invocable: true
argument-hint: "<topic>"
allowed-tools: [Read, Grep, Glob, WebSearch, WebFetch]
---
Research $ARGUMENTS thoroughly. Search the codebase and web.
Provide a structured summary with sources.
```

### Multi-Model Skill

Use different models for different skill phases:

```yaml
---
name: quick-fix
model: haiku
user-invocable: true
argument-hint: "<file> <issue>"
allowed-tools: [Read, Edit]
---
Quickly fix $2 in $1. Use minimal changes.
```

### Workflow Skill (Sequential Steps)

```yaml
---
name: pr-review
user-invocable: true
argument-hint: "<pr-number>"
allowed-tools: [Bash, Read, Grep, Glob]
---
Review PR #$1:

1. Fetch PR diff: !`gh pr diff $1`
2. Read all changed files
3. Check for security issues, bugs, and style violations
4. Provide a structured review with file-specific comments
```

### Hook-Gated Quality Check

Prevent commits without tests:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python check_no_untested_commits.py",
            "statusMessage": "Checking for untested commits..."
          }
        ]
      }
    ]
  }
}
```
