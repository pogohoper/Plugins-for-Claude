---
name: register-domain
description: Register a new persistent domain agent for a specific part of the codebase. Scans the directory, generates knowledge files, and creates a domain expert agent.
user-invocable: true
argument-hint: "<path> <agent-name>"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
---

# Register Domain Agent

Register a new persistent domain expert agent for a part of the codebase.

## Arguments

- `$1` — The directory path to govern (e.g., `src/auth/`, `lib/database/`)
- `$2` — The agent name (e.g., `auth-expert`, `db-expert`)

## Instructions

1. **Validate the path**: Confirm that `$1` exists and is a directory. If not, report an error.

2. **Run the registration script**: Execute the following command to scan the directory and generate initial knowledge files:

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/register.py" "$1" "$2"
```

3. **Verify output**: Check that the following files were created in `.claude/agent-memory/$2/`:
   - `domain.json` — Machine-readable domain configuration
   - `MEMORY.md` — High-level index and summary
   - `structure.md` — Detailed file/module breakdown
   - `dependencies.md` — Import/export relationships
   - `patterns.md` — Observed coding patterns and conventions

4. **Report success**: Tell the user:
   - The domain agent `$2` has been registered for path `$1`
   - How many files were scanned
   - They can now use `/consult $2 <question>` to ask questions
   - They can use `/domain-sync $2` to refresh knowledge after code changes
