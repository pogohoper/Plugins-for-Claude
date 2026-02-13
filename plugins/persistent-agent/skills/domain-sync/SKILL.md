---
name: domain-sync
description: Re-scan a domain agent's territory and update its knowledge files with any changes since the last scan.
user-invocable: true
argument-hint: "<agent-name>"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
---

# Domain Sync

Re-scan a domain agent's governed code area and update its knowledge files.

## Arguments

- `$1` — The domain agent name (e.g., `auth-expert`, `db-expert`)

## Instructions

1. **Validate the agent**: Read `.claude/agent-memory/$1/domain.json` to confirm the agent exists and get its governed path.

2. **Run the sync script**: Execute:

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/scan_domain.py" "$1"
```

This script will:
- Re-scan the governed directory
- Compare against the previous scan stored in `domain.json`
- Output a JSON diff of changes (added/removed/modified files)

3. **Update knowledge files**: Based on the diff output:
   - Update `structure.md` with new/removed/renamed files
   - Update `dependencies.md` if imports or exports changed
   - Update `patterns.md` if new patterns are observed
   - Update `MEMORY.md` with a sync log entry:

```markdown
## Sync — [today's date]
**Changes detected**:
- Added: [list of new files]
- Removed: [list of removed files]
- Modified: [list of changed files]
**Knowledge updates**:
- [summary of what was updated in knowledge files]
```

4. **Update domain.json**: The scan script updates the `last_scan` timestamp and file manifest automatically.

5. **Report results**: Tell the user:
   - How many files changed since last scan
   - What knowledge was updated
   - The agent is now up to date
