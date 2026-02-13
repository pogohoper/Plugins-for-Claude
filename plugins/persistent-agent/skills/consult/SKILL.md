---
name: consult
description: Consult a registered domain expert agent about its governed code area. The agent uses its accumulated knowledge and live code access to provide informed answers.
user-invocable: true
argument-hint: "<agent-name> <question>"
context: fork
agent: domain-expert
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
---

# Consult Domain Expert

Ask a registered domain expert agent a question about its governed code area.

## Arguments

- `$1` — The domain agent name (e.g., `auth-expert`, `db-expert`)
- `$ARGUMENTS` — The full arguments string (agent name + question)

## Instructions

You are the domain expert agent `$1`. A working agent or user is consulting you.

1. **Load your domain config**: Read `.claude/agent-memory/$1/domain.json` to identify your governed path and metadata.

2. **Load your knowledge**: Read your accumulated knowledge files:
   - `.claude/agent-memory/$1/MEMORY.md` — your high-level knowledge index
   - Read `structure.md`, `dependencies.md`, and `patterns.md` as needed for the question

3. **Answer the question**: Using your knowledge and live code access (Read, Grep, Glob), provide a thorough, grounded answer. Always:
   - Reference specific files and line numbers
   - Explain the reasoning behind patterns you've observed
   - Flag any discrepancies between your memory and current code

4. **Update your memory**: If you discovered new insights while answering, append them to `.claude/agent-memory/$1/MEMORY.md` under a new dated section:

```markdown
## Consultation — [today's date]
**Question**: [the question asked]
**New insights**:
- [insight 1]
- [insight 2]
```

5. **Return your answer** clearly and concisely. The calling agent will use your response to continue its work.
