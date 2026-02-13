# Persistent Agent Plugin

A Claude Code plugin that creates **persistent domain-expert agents** for specific parts of your codebase. Each domain agent governs a directory, maintains deep knowledge across sessions, and can be consulted by working agents or users.

## Concept

Large codebases have specialized areas — authentication, database layer, API routes, UI components — each with their own patterns, conventions, and gotchas. The Persistent Agent plugin lets you assign a domain expert to each area. These experts:

- **Scan and index** the code structure, dependencies, and patterns
- **Accumulate knowledge** over time through consultations and syncs
- **Answer questions** grounded in both their memory and live code access
- **Stay current** via manual syncs or automatic staleness detection

## Installation

```bash
claude plugin install ./plugins/persistent-agent
```

Or test locally:

```bash
claude --plugin-dir ./plugins/persistent-agent
```

## Skills

### `/register-domain <path> <agent-name>`

Register a new domain expert agent for a directory.

```
/register-domain src/auth auth-expert
/register-domain lib/database db-expert
/register-domain src/components/ui ui-expert
```

This scans the directory and creates knowledge files in `.claude/agent-memory/<agent-name>/`:

| File | Purpose |
|------|---------|
| `domain.json` | Machine-readable config (path, file manifest, timestamps) |
| `MEMORY.md` | High-level index, purpose summary, consultation log |
| `structure.md` | Detailed file/module breakdown with definitions |
| `dependencies.md` | Import/export relationships |
| `patterns.md` | Observed coding patterns and conventions |

### `/consult <agent-name> <question>`

Ask a domain expert about its governed code area.

```
/consult auth-expert How does the JWT refresh token flow work?
/consult db-expert What indexes exist on the users table?
/consult ui-expert What component library conventions are used here?
```

The domain agent:
1. Loads its accumulated knowledge
2. Reads live source code to verify and supplement
3. Provides a grounded, specific answer
4. Updates its memory with any new insights discovered

### `/domain-sync <agent-name>`

Re-scan a domain and update the agent's knowledge.

```
/domain-sync auth-expert
```

This detects added, removed, and modified files since the last scan and updates all knowledge files accordingly.

## How It Works

### Architecture

```
User / Working Agent
        │
        ▼
  /consult <name> <question>
        │
        ▼
  ┌─────────────────────┐
  │   Domain Expert      │  (forked subagent)
  │   - Read-only code   │
  │   - Memory files     │
  │   - Live search      │
  └─────────────────────┘
        │
        ▼
  Answer + Memory Update
```

### Staleness Detection

A `PostToolUse` hook monitors file edits (`Write`, `Edit`). When an edited file falls within a domain agent's territory, it outputs a reminder suggesting `/domain-sync`.

### Knowledge Growth

Domain agents get smarter over time:
1. **Initial scan** provides structural knowledge
2. **Consultations** add contextual insights (the "why" behind patterns)
3. **Syncs** keep structural knowledge current
4. Each consultation appends to `MEMORY.md`, creating a growing knowledge base

## Plugin Structure

```
persistent-agent/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/
│   ├── register-domain/
│   │   └── SKILL.md         # /register-domain skill
│   ├── consult/
│   │   └── SKILL.md         # /consult skill
│   └── domain-sync/
│       └── SKILL.md         # /domain-sync skill
├── agents/
│   └── domain-expert.md     # Custom agent definition
├── hooks/
│   └── hooks.json           # File-change staleness detection
├── scripts/
│   ├── register.py          # Directory scanner and knowledge generator
│   ├── check_domain.py      # Hook: checks if edits affect domain agents
│   └── scan_domain.py       # Re-scanner for domain-sync
└── README.md
```

## Requirements

- Claude Code CLI
- Python 3.10+ (for scanner scripts)

## Design Decisions

- **Read-only code access**: Domain agents can read and search code but cannot modify it, preventing accidental changes while allowing deep analysis.
- **Persistent memory**: Knowledge accumulates in `.claude/agent-memory/` and survives across sessions, giving agents growing expertise.
- **Python scripts for scanning**: Python provides robust file traversal, code parsing, and JSON handling for generating structured knowledge.
- **Forked context for consultation**: Each `/consult` forks an isolated subagent, keeping the main session clean while giving the expert full focus.
