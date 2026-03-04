---
name: panluma
description: This skill should be used when the user asks to "query PanLuma", "create a task in PanLuma", "update PanLuma contacts", "delete PanLuma data", "list PanLuma invoices", "show PanLuma deals", "check PanLuma sales", "manage PanLuma data", "search PanLuma endpoints", "set PanLuma context", "remember my PanLuma sprint", or mentions PanLuma modules (tasks, contacts, sales, accounting, recruiting, support, messaging, files, virtual-team, website-hosting, and more). Provides API integration for the PanLuma AI business suite with per-project working context.
user-invocable: true
argument-hint: "<action> [module] [details...]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - Glob
  - Edit
---

# PanLuma API Skill

PanLuma is an AI-native business suite with 100+ modules and 1,400+ API endpoints. This skill enables querying, creating, updating, and managing data across all PanLuma modules via its REST API.

## Working Context

Check for a user-defined working context file at `.claude/panluma.local.md` (project-level). If it exists, its YAML frontmatter defines the current focus — use these values to scope API queries automatically (e.g., filter by workspace, board, sprint, pipeline). If the file does not exist, proceed without scoping.

Example `.claude/panluma.local.md`:

```yaml
---
workspace_id: "abc-123"
board_id: "def-456"
sprint: "Sprint 24"
pipeline_id: "ghi-789"
default_module: tasks
notes: "Currently working on Q1 sales pipeline and Sprint 24 tasks"
---
Any additional context or notes here.
```

The current working context (if any) is shown below:

!`cat .claude/panluma.local.md 2>/dev/null || echo "(no working context set)"`

**Auto-save:** After any API call that reveals or confirms a working scope (workspace ID, board ID, sprint name, pipeline ID, etc.), automatically update `.claude/panluma.local.md` with the discovered context. This ensures future invocations are scoped correctly without the user needing to ask. Merge new values into existing frontmatter — do not overwrite fields the user previously set. If the file does not exist yet, create it with the discovered values.

The user can also explicitly say "set PanLuma context" or "remember my sprint/project/workspace" to create or update this file manually.

## API Key Check

Before making any API call, verify the key is available:

```bash
echo "${PANLUMA_API_KEY:-(not set)}"
```

If the key is not set:
1. Inform the user: "No PanLuma API key found. Provide an API key (starts with `plma_live_`)."
2. Once provided, save it to `~/.claude/settings.json` under the `env` key using Read and Edit tools.
3. Instruct the user to restart Claude Code for the change to take effect.
4. Stop — do not attempt API calls without a valid key.

## Workflow

### 1. Look Up Endpoints

Always discover the correct endpoint before making API calls:

```bash
# Search for endpoints by keyword
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" "tasks"
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" "invoice"

# List all endpoints in a module
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --module sales

# Get full details for a specific path (params, body schema)
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --detail "/api/v1/tasks"
```

### 2. Make API Calls

Use the API helper script for all requests:

```bash
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" <METHOD> <PATH> [--data JSON] [--params KEY=VALUE ...]
```

The `$PANLUMA_API_KEY` env var is picked up automatically. The `MSYS_NO_PATHCONV=1` prefix prevents Git Bash on Windows from mangling `/api/...` paths. To override the default base URL, set `PANLUMA_BASE_URL`.

**Pagination:** Use `limit` and `offset` query params for list endpoints. Default to `limit=25` to avoid overwhelming output.

**Error handling:** If the API returns an error (4xx/5xx), show the status code and error body to the user and suggest corrections.

**Examples:**

```bash
# GET with query params
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" GET /api/v1/tasks --params limit=10

# POST with JSON body
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" POST /api/v1/contacts/companies --data '{"name":"Acme Corp"}'

# PUT to update
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" PUT /api/v1/tasks/items/UUID --data '{"title":"Updated"}'

# DELETE
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" DELETE /api/v1/contacts/companies/UUID
```

## Key Modules

All endpoints follow the pattern `/api/v1/<module>/...`. For the full list of 100+ modules and their endpoints, consult `references/api-modules.md`. Note: `bookkeeping` has been renamed to `accounting` in the current API.

## Additional Resources

### Reference Files

For the complete module overview table, base URL, rate limits, and detailed API call examples, consult:
- **`references/api-modules.md`** — Full module listing with base paths, key operations, and endpoint discovery patterns

### Scripts

- **`scripts/panluma_lookup.py`** — Endpoint discovery from the bundled OpenAPI spec. Supports search, module listing, and detailed endpoint inspection.
- **`scripts/panluma_api.py`** — HTTP client wrapper. Handles auth, query params, JSON body, and error formatting.
- **`scripts/openapi.json`** — The full PanLuma OpenAPI specification (source of truth for all endpoints).

## User Request

$ARGUMENTS
