# Plugins_for_claude

Repository for building advanced Claude Code plugins. Contains reference documentation, best practices guides, and plugin implementations.

## Repository Structure

```
docs/                              # Reference documentation
  claude-code-plugin-reference.md  # Full plugin/skill/hooks/agent system reference
  agent-collaboration-best-practices.md  # Multi-agent coordination guide
plugins/                           # Plugin implementations
  persistent-agent/                # Domain expert agent plugin
  tts/                             # Text-to-speech plugin
```

## Formatting

When outputting code blocks, add a blank line or `---` separator after the closing ``` to prevent syntax highlighting from bleeding into subsequent text.

## Plugin Development Rules

### Directory Layout

Every plugin must follow this structure:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json       # Manifest (required)
├── skills/               # Skill definitions
│   └── skill-name/
│       └── SKILL.md
├── agents/               # Custom subagent definitions
│   └── agent-name.md
├── hooks/                # Hook configurations
│   └── hooks.json
├── scripts/              # Supporting scripts
└── README.md
```

### SKILL.md Frontmatter

Required fields: `name`, `description`. Key optional fields:

```yaml
---
name: my-skill              # Lowercase, hyphens, max 64 chars
description: What it does   # Used by Claude for auto-invocation decisions
user-invocable: true        # Allow /my-skill invocation
argument-hint: "<arg>"      # Autocomplete hint
allowed-tools:              # Tool allowlist (omit for all)
  - Read
  - Grep
context: fork               # Isolate in subagent
agent: my-agent             # Custom agent for forked context
model: sonnet               # Model override
---
```

### Substitution Variables

- `$ARGUMENTS` — full argument string
- `$1`, `$2`, ... `$N` — positional arguments
- `${CLAUDE_SESSION_ID}` — current session ID
- `${CLAUDE_PLUGIN_ROOT}` — plugin root directory (plugin context only)
- `` !`command` `` — dynamic context injection (runs at skill load time)

### Hook Structure

Hooks use a nested format: event → matcher array → hooks array.

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolNameRegex",
        "hooks": [
          {
            "type": "command",
            "command": "your-command",
            "timeout": 10,
            "statusMessage": "Shown in UI..."
          }
        ]
      }
    ]
  }
}
```

Hook events: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `SubagentStart`, `SubagentStop`, `TaskCompleted`, `Stop`, `TeammateIdle`, `PreCompact`, `SessionEnd`.

Command hook exit codes: `0` = success, `2` = blocking error (stderr fed to Claude).

### Agent Definition Frontmatter

```yaml
---
name: agent-name
description: What this agent does
tools: [Read, Grep, Glob]         # Allowlist
disallowedTools: [Write, Bash]    # Or blocklist (not both)
model: sonnet                     # opus | sonnet | haiku
maxTurns: 15
memory: project                   # user | project | local
---
```

### Testing Plugins Locally

```bash
claude --plugin-dir ./plugins/my-plugin
claude --plugin-dir ./plugins/my-plugin --debug  # With loading details
```

## Code Conventions

- Python scripts require 3.10+ (use `pathlib`, type hints, `|` union syntax)
- Plugin scripts must handle missing/invalid input gracefully and exit with clear error messages
- JSON configs use 2-space indentation
- YAML frontmatter must pass `yaml.safe_load()` validation
- Keep agent tool lists minimal — prefer read-only (`Read, Grep, Glob`) unless writes are essential

## Existing Plugins

### persistent-agent

Domain expert agents that govern specific code areas. Skills:
- `/register-domain <path> <name>` — scan and register a new domain agent
- `/consult <agent-name> <question>` — ask a domain agent (forked, read-only)
- `/domain-sync <agent-name>` — re-scan and update knowledge

Agent memory stored in `.claude/agent-memory/<name>/` with files: `domain.json`, `MEMORY.md`, `structure.md`, `dependencies.md`, `patterns.md`.

### tts

Text-to-speech synthesis using edge-tts with chunked playback. Skills:
- `/tts <text>` — speak text aloud with automatic sentence chunking
- Supports 6 voices (andrew, guy, aria, ava, jenny, brian) and 3 speed levels
- Dependencies: `pip install edge-tts pygame`

## Reference

For full details see:
- @docs/claude-code-plugin-reference.md — complete system reference
- @docs/agent-collaboration-best-practices.md — multi-agent patterns
