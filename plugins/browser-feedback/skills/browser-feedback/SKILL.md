---
name: browser-feedback
description: Closed-loop browser feedback for development. Spawns a Sonnet sub-agent that visually verifies UI changes using agent-browser CLI and returns a concise report. Use after making frontend/UI code changes, when asked to "check how it looks" or "verify in the browser", or to create a visual feedback loop during development. Also use proactively after completing visual/UI tasks to verify correctness before reporting done.
user-invocable: true
argument-hint: "<url> [what to check]"
context: fork
agent: browser-feedback
model: sonnet
allowed-tools:
  - Bash
  - Read
  - Glob
---

# Browser Feedback Loop

Verify UI changes in a real browser. This skill forks into a Sonnet sub-agent that uses `agent-browser` CLI to open pages, take screenshots, and report findings.

## Usage

```
/browser-feedback https://acg.brijlabs.ai Check login page loads, RTL is correct, Google OAuth button present
```

The sub-agent will:
1. Open the URL in headless Chromium
2. Wait for the page to load
3. Take screenshots and view them
4. Check interactive elements
5. Return a PASS / FAIL / PARTIAL report

## Arguments

`$ARGUMENTS` is passed as the check request. Format:

```
<url> [description of what to verify]
```

If no URL provided, defaults to `https://acg.brijlabs.ai`.

## Check Request

$ARGUMENTS

## Programmatic Use (from main agent)

The main agent can also invoke this via the Task tool:

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Browser feedback: <what to check>",
  prompt: <read agents/browser-feedback.md> + check request
)
```

## Prerequisites (main agent responsibility)

Before invoking for local dev:
1. Ensure `node_modules/` exists (`npm install` if missing)
2. Start dev server in background (`npx vite --port 5173`)
3. Verify server responds: `curl -s -o /dev/null -w "%{http_code}" http://localhost:5173`

Skip for production URLs (e.g. `https://acg.brijlabs.ai`).

## Iteration Pattern

```
Main agent: make code changes
  -> /browser-feedback <url> <what to check>
  <- Receive report
  -> If FAIL: fix issues, run again
  -> If PASS: report done to user
```
