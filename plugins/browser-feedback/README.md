# browser-feedback

Closed-loop browser feedback plugin for Claude Code. Spawns a Sonnet sub-agent that visually verifies UI changes using headless Chromium and returns a structured report.

## How it works

1. Main agent makes code changes
2. Invoke `/browser-feedback <url> [what to check]`
3. A forked Sonnet sub-agent opens a headless browser via `agent-browser` CLI
4. Sub-agent takes screenshots, inspects elements, checks for errors
5. Returns a PASS / FAIL / PARTIAL report with findings

## Requirements

- `agent-browser` CLI must be installed and available on PATH
- For local dev testing: Node.js + running dev server

## Usage

```
/browser-feedback https://example.com Check that login page loads and form is visible
/browser-feedback http://localhost:5173 Verify dashboard table renders with data
/browser-feedback https://acg.brijlabs.ai Check RTL layout and dark mode toggle
```

## Plugin structure

```
browser-feedback/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── browser-feedback.md    # Sub-agent definition (Sonnet, read-only)
├── skills/
│   └── browser-feedback/
│       └── SKILL.md           # Skill entry point with fork config
└── README.md
```
