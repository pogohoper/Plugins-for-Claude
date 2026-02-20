# Plugins_for_claude

Repository for building advanced Claude Code plugins. This repo doubles as a **plugin marketplace** — users add it with `claude plugin marketplace add pogohoper/Plugins-for-Claude` and install individual plugins from it.

## Repository Structure

```
.claude-plugin/
  marketplace.json                 # Marketplace manifest (REQUIRED for marketplace)
docs/                              # Reference documentation
  claude-code-plugin-reference.md  # Full plugin/skill/hooks/agent system reference
  agent-collaboration-best-practices.md  # Multi-agent coordination guide
plugins/                           # Plugin implementations
  orchestrator/                    # Agent team orchestration plugin
  persistent-agent/                # Domain expert agent plugin
  tts/                             # Text-to-speech plugin
```

## Formatting

When outputting code blocks, add a blank line or `---` separator after the closing ``` to prevent syntax highlighting from bleeding into subsequent text.

---

## Marketplace System

This repo is a Claude Code **plugin marketplace**. The marketplace manifest at `.claude-plugin/marketplace.json` is the registry that makes plugins discoverable and installable.

### Marketplace Manifest (`.claude-plugin/marketplace.json`)

When adding a new plugin, you MUST add an entry to this file. The format:

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "plugins-for-claude",
  "description": "Human-readable marketplace description",
  "owner": {
    "name": "pogohoper"
  },
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./plugins/my-plugin",
      "description": "What the plugin does",
      "version": "1.0.0",
      "author": { "name": "pogohoper" },
      "category": "development",
      "keywords": ["keyword1", "keyword2"]
    }
  ]
}
```

**Critical rules:**
- `source` paths MUST start with `./` and point to the plugin directory relative to repo root
- `author` MUST be an object `{"name": "..."}`, NEVER a plain string
- `name` must be lowercase kebab-case
- Always include `version` (semver), `description`, and `category`
- Bump `version` on every change to the plugin

### Plugin Categories

Use one of: `development`, `productivity`, `testing`, `integration`, `ai`, `utilities`

### Marketplace CLI Commands

```bash
# Users add this marketplace
claude plugin marketplace add pogohoper/Plugins-for-Claude

# Users install a plugin from it
claude plugin install my-plugin@plugins-for-claude

# Update marketplace cache to pick up new commits
claude plugin marketplace update plugins-for-claude

# List configured marketplaces
claude plugin marketplace list

# Remove a marketplace
claude plugin marketplace remove plugins-for-claude
```

### Where to Find Reference Data

When building or debugging marketplace features, check these sources:

| What | Where |
|------|-------|
| Official marketplace manifest (gold reference) | `~/.claude/plugins/marketplaces/claude-plugins-official/.claude-plugin/marketplace.json` |
| Our marketplace manifest | `.claude-plugin/marketplace.json` (this repo) |
| Installed plugins registry | `~/.claude/plugins/installed_plugins.json` |
| Marketplace cache (local clones) | `~/.claude/plugins/marketplaces/<name>/` |
| Plugin install cache | `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` |
| Known marketplaces config | `~/.claude/plugins/known_marketplaces.json` |
| Plugin schema reference | `https://anthropic.com/claude-code/marketplace.schema.json` |
| Full plugin/skill/agent docs | `@docs/claude-code-plugin-reference.md` (this repo) |

---

## Adding a New Plugin -- Checklist

When creating a new plugin, follow every step:

### 1. Create the plugin directory

```
plugins/my-plugin/
+-- .claude-plugin/
|   +-- plugin.json       # Plugin manifest (REQUIRED)
+-- skills/               # Skill definitions
|   +-- skill-name/
|       +-- SKILL.md
+-- agents/               # Custom subagent definitions (optional)
|   +-- agent-name.md
+-- hooks/                # Hook configurations (optional)
|   +-- hooks.json
+-- scripts/              # Supporting scripts (optional)
+-- install.sh            # Install script (optional)
+-- README.md
```

### 2. Write `plugin.json` -- THE SCHEMA RULES

This is inside `.claude-plugin/plugin.json` within the plugin directory. The format is strict -- validation will reject invalid manifests silently during install.

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin does",
  "author": {
    "name": "pogohoper"
  },
  "skills": ["./skills/skill-one", "./skills/skill-two"],
  "agents": ["./agents/my-agent.md"],
  "hooks": "./hooks/hooks.json"
}
```

**Validation rules that WILL break installs if violated:**

| Field | Correct | Wrong (will fail silently) |
|-------|---------|---------------------------|
| `author` | `{"name": "pogohoper"}` | `"pogohoper"` (string) |
| `skills` | `["./skills/my-skill"]` | `["skills/my-skill"]` (missing `./`) |
| `agents` | `["./agents/my-agent.md"]` | `["agents/my-agent.md"]` (missing `./`) |
| `hooks` | `"./hooks/hooks.json"` | `["hooks/hooks.json"]` (wrong type for single file) |
| custom keys | omit them | `"scripts": [...]` (unrecognized keys cause failure) |

**Allowed top-level keys in `plugin.json`:**
`name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `skills`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`, `strict`

**Any key not in this list will cause validation failure.**

### 3. Validate BEFORE committing

```bash
# Validate the individual plugin
claude plugin validate ./plugins/my-plugin

# Validate the entire marketplace
claude plugin validate .
```

Both must pass. The marketplace validation may show a warning about `metadata.description` -- that is acceptable and won't block installs.

### 4. Add entry to marketplace manifest

Add the new plugin to `.claude-plugin/marketplace.json` in the `plugins` array:

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin",
  "description": "What it does",
  "version": "1.0.0",
  "author": { "name": "pogohoper" },
  "category": "development",
  "keywords": ["relevant", "tags"]
}
```

### 5. Test the install locally

```bash
# Test plugin loading without installing
claude --plugin-dir ./plugins/my-plugin
claude --plugin-dir ./plugins/my-plugin --debug

# Or test full marketplace install flow
claude plugin marketplace update plugins-for-claude
claude plugin install my-plugin@plugins-for-claude
```

### 6. Commit, push, verify

After pushing, users need to run `claude plugin marketplace update plugins-for-claude` to pick up the new plugin.

---

## Common Pitfalls (Lessons Learned)

These cause **silent install failures** -- the install command exits with code 1 and no error message:

1. **`author` as string** -- Must be `{"name": "..."}` object, not a bare string
2. **Paths without `./` prefix** -- All paths in `skills`, `agents`, `hooks` must start with `./`
3. **Unrecognized keys** -- Any key not in the allowed list (e.g. `"scripts"`) causes rejection
4. **`install.sh` using bare `pip`** -- On Windows Git Bash, `pip` is not on PATH. Use `python -m pip` with fallbacks:
   ```bash
   python -m pip install -q pkg 2>/dev/null || python3 -m pip install -q pkg 2>/dev/null || pip install -q pkg
   ```
5. **`install.sh` with `set -e`** -- If any command in the install script fails, the entire plugin install fails silently. Guard optional commands.
6. **Marketplace not updated** -- After pushing changes, the local marketplace cache is stale. Must run `claude plugin marketplace update plugins-for-claude` before installs will reflect changes.
7. **`hooks` as array** -- For a single hooks file, use a string `"./hooks/hooks.json"`, not an array.

---

## Plugin Development Rules

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

- `$ARGUMENTS` -- full argument string
- `$1`, `$2`, ... `$N` -- positional arguments
- `${CLAUDE_SESSION_ID}` -- current session ID
- `${CLAUDE_PLUGIN_ROOT}` -- plugin root directory (plugin context only)
- Dynamic context injection with backtick-bang syntax -- runs at skill load time

### Hook Structure

Hooks use a nested format: event, then matcher array, then hooks array.

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

---

## Code Conventions

- Python scripts require 3.10+ (use `pathlib`, type hints, `|` union syntax)
- Plugin scripts must handle missing/invalid input gracefully and exit with clear error messages
- JSON configs use 2-space indentation
- YAML frontmatter must pass `yaml.safe_load()` validation
- Keep agent tool lists minimal -- prefer read-only (`Read, Grep, Glob`) unless writes are essential
- Install scripts must be cross-platform: use `python -m pip` not bare `pip`

## Existing Plugins

### orchestrator

Agent team orchestration for complex tasks. Skills:
- `/orchestrate <task>` -- analyze a task, propose specialized agents, present plan, execute after approval
- Includes 13 specialized agents (spec-writer, implementer, validator, test-writer, security-reviewer, etc.)

### persistent-agent

Domain expert agents that govern specific code areas. Skills:
- `/register-domain <path> <name>` -- scan and register a new domain agent
- `/consult <agent-name> <question>` -- ask a domain agent (forked, read-only)
- `/domain-sync <agent-name>` -- re-scan and update knowledge

Agent memory stored in `.claude/agent-memory/<name>/` with files: `domain.json`, `MEMORY.md`, `structure.md`, `dependencies.md`, `patterns.md`.

### tts

Text-to-speech synthesis using edge-tts with chunked playback. Skills:
- `/tts <text>` -- speak text aloud with automatic sentence chunking
- Supports 6 voices (andrew, guy, aria, ava, jenny, brian) and 3 speed levels
- Dependencies: `pip install edge-tts pygame`

## Reference

For full details see:
- @docs/claude-code-plugin-reference.md -- complete system reference
- @docs/agent-collaboration-best-practices.md -- multi-agent patterns
