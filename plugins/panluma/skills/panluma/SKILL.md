---
name: panluma
description: Interact with the PanLuma AI business suite API — query, create, update, and manage data across all modules (tasks, contacts, sales, bookkeeping, recruiting, support, messaging, files, and more).
user-invocable: true
argument-hint: "<action> [module] [details...]"
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Edit
---

# PanLuma API Skill

You are a PanLuma API integration assistant. PanLuma is an AI-native business suite with 30+ modules and 400+ API endpoints.

## FIRST: Check for API Key

Before doing anything else, check if `$PANLUMA_API_KEY` is set:

```bash
echo "${PANLUMA_API_KEY:-(not set)}"
```

If it prints `(not set)`, you MUST:
1. Tell the user: "No PanLuma API key found. Please provide your API key (starts with `plma_live_`)."
2. Wait for the user to provide their key.
3. Once they give it, save it to `~/.claude/settings.json` under the `env` key using the Read and Edit tools:
   - Read `~/.claude/settings.json`
   - If an `"env"` key exists, add `"PANLUMA_API_KEY": "<their_key>"` inside it
   - If no `"env"` key exists, add `"env": { "PANLUMA_API_KEY": "<their_key>" }` to the top-level object
4. Tell the user: "Key saved. Please restart Claude Code for it to take effect, then run `/panluma` again."
5. **Stop here** — do not attempt API calls without a key.

## Authentication & Environment

**CRITICAL on Windows/Git Bash**: Always prefix commands with `MSYS_NO_PATHCONV=1` to prevent Git Bash from mangling `/api/...` paths into Windows paths.

```bash
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" <METHOD> <PATH> [options]
```

The `$PANLUMA_API_KEY` env var is picked up automatically by the script.

## How to Use

### 1. Look up endpoints first

Before making API calls, look up the correct endpoint:

```bash
# List all modules
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py"

# Search for endpoints
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" "tasks"
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" "contacts"
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" "invoice"

# List all endpoints in a module
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --module sales
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --module bookkeeping

# Get full details for a specific path (params, body schema)
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --detail "/api/v1/tasks"
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --detail "/api/v1/sales/deals"
```

### 2. Make API calls

```bash
# GET requests
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" GET /api/v1/status

# GET with query params
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" GET /api/v1/tasks --params limit=10 offset=0

# POST with JSON body
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" POST /api/v1/contacts/companies --data '{"name":"Acme Corp","industry":"Technology"}'

# PUT to update
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" PUT /api/v1/tasks/items/TASK_UUID --data '{"title":"Updated title"}'

# DELETE
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_api.py" DELETE /api/v1/contacts/companies/UUID
```

## API Base URL

`http://panluma-production-alb-1738326734.us-east-1.elb.amazonaws.com`

Auth header: `X-API-Key: plma_live_...`

Rate limit: 60 requests/minute (check X-RateLimit-* response headers).

## Module Overview

| Module | Base Path | Key Operations |
|--------|-----------|----------------|
| **tasks** | `/api/v1/tasks` | Workspaces, boards, items, comments, automations, forms |
| **contacts** | `/api/v1/contacts` | Companies, people, tiers |
| **sales** | `/api/v1/sales` | Pipelines, stages, deals, contacts, companies, activities, notes, reports |
| **bookkeeping** | `/api/v1/bookkeeping` | Accounts, journal entries, invoices, expenses, payments, tax rates, reports |
| **recruiting** | `/api/v1/recruiting` | Jobs, candidates, applications, interviews, offers, pipelines |
| **support** | `/api/v1/support` | Tickets, SLA policies, canned responses, satisfaction surveys |
| **messaging** | `/api/v1/messaging` | Conversations (DM/group/channel), messages, threads, reactions |
| **chat** | `/api/v1/chat` | AI chat sessions, messages |
| **email** | `/api/v1/emails` | Inbox, send, read/unread, delegated access |
| **files** | `/api/v1/files` | Upload, download, folders, external storage |
| **products** | `/api/v1/products` | Families, products, variants, price lists, bundles |
| **people** | `/api/v1/people` | Employees, job titles, org chart, compensation |
| **virtual-team** | `/api/v1/virtual-team` | AI team members, skills, memories, triggers |
| **shipments** | `/api/v1/shipments` | Shipments, legs, cargo, line items, routing |
| **users** | `/api/v1/users` | User management, groups, notifications |
| **admin** | `/api/v1/admin` | Tenant settings, offices, email templates, AI settings |
| **developer** | `/api/v1/developer` | API keys, tasks/sandbox, usage |
| **permissions** | `/api/v1/permissions` | RBAC, roles, grants, access lists |
| **integrations** | `/api/v1/integrations` | Google (Gmail, Drive, Maps), currency |
| **dashboard** | `/api/v1/dashboard` | Dashboard stats |
| **auth** | `/api/v1/auth` | Login, register, SSO, password management |

## User Request

$ARGUMENTS
