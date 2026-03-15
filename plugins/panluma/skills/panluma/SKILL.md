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

PanLuma is an AI-native business suite with 30+ modules and 400+ endpoints.

## FIRST: Check for API Key

```bash
echo "${PANLUMA_API_KEY:-(not set)}"
```

If `(not set)`: ask the user for their key (starts with `plma_live_`), save it to `~/.claude/settings.json` under the `env` key, and tell them to restart Claude Code.

## Script Paths

```bash
PLUMA="${CLAUDE_PLUGIN_ROOT}"
```

Scripts: `$PLUMA/scripts/panluma_api.py`, `$PLUMA/scripts/panluma_lookup.py`, `$PLUMA/scripts/panluma_cache.py`

## Context Cache (saves 1-2 API calls per session)

The cache stores workspace_id and active sprint info so you don't re-discover them every time. **Always check the cache first** for any sprint-related query:

```bash
# Read cache — returns {} if empty or sprint is expired
python3 "$PLUMA/scripts/panluma_cache.py" get
```

If `workspace_id` is present, skip the workspaces API call. If `active_sprint` is present, skip the sprints list call. If cache is empty or stale, do the discovery calls and **save the results**:

```bash
# After discovering workspace + sprint, save for next time
python3 "$PLUMA/scripts/panluma_cache.py" set \
  --workspace-id WORKSPACE_UUID \
  --sprint-id SPRINT_UUID \
  --sprint-name "Sprint Name" \
  --sprint-end 2026-03-22
```

The sprint entry auto-expires when its end_date passes. Workspace ID never expires.

## Output Flags (CRITICAL — always use on list endpoints)

Raw API responses are 50-100KB+. Use at least one flag on every GET that returns a list:

| Flag | What it does | When to use |
|------|-------------|-------------|
| `--compact` | Keeps only key fields (~90% reduction) | Default for any list |
| `--fields title,status,priority` | Keeps only specified fields (~97% reduction) | When you need specific columns |
| `--group-by status` | Groups items by field with counts | Sprint tasks, board overviews |

Combine: `--fields title,status,priority,assigned_to --group-by status`. Prefer `--fields` over `--compact` for large lists (50+ items).

**Server-side filtering** with `--params` is even better — less data transferred:
```bash
python3 "$PLUMA/scripts/panluma_api.py" GET /api/v1/tasks/my-tasks --params status=in_progress --compact
python3 "$PLUMA/scripts/panluma_api.py" GET /api/v1/tasks/my-tasks --params status=todo --fields title,priority
```

**Full output only** for single-item GET by ID or mutations (POST/PUT/DELETE).

## Looking Up Endpoints

Use specific terms — "tasks" returns 170+ results:
```bash
python3 "$PLUMA/scripts/panluma_lookup.py" "sprint"          # 17 results
python3 "$PLUMA/scripts/panluma_lookup.py" --module sprints   # all sprint endpoints
python3 "$PLUMA/scripts/panluma_lookup.py" --detail "/api/v1/tasks/my-tasks"  # params & schema
```

## Workflow Recipes

Choose the smallest recipe that fits. Check cache first for sprint-related queries.

### My tasks (filtered or full list)
```bash
# All my tasks
python3 "$PLUMA/scripts/panluma_api.py" GET /api/v1/tasks/my-tasks --compact

# Specific statuses (1 call + client filter, or 2 calls with server filter)
python3 "$PLUMA/scripts/panluma_api.py" GET /api/v1/tasks/my-tasks --fields title,status,priority
```

### Sprint progress only
With cache: **1 call**. Without cache: 3 calls (workspaces → sprints → progress).
```bash
# 1. Check cache for workspace_id + sprint_id
python3 "$PLUMA/scripts/panluma_cache.py" get

# If cache miss: discover and save
python3 "$PLUMA/scripts/panluma_api.py" GET /api/v1/workspaces --fields id,name
python3 "$PLUMA/scripts/panluma_api.py" GET /api/v1/tasks/workspaces/{workspace_id}/sprints --compact
# → find "status": "active", then save:
python3 "$PLUMA/scripts/panluma_cache.py" set --workspace-id WID --sprint-id SID --sprint-name NAME --sprint-end END_DATE

# 2. Get progress (always needed — live data)
python3 "$PLUMA/scripts/panluma_api.py" GET /api/v1/tasks/sprints/{sprint_id}/progress
```

### Full sprint + my tasks overview
With cache: **3 calls**. Without: 5 calls.
```bash
# 1. Check cache + get my tasks in parallel
python3 "$PLUMA/scripts/panluma_cache.py" get
python3 "$PLUMA/scripts/panluma_api.py" GET /api/v1/tasks/my-tasks --compact

# 2. If cache miss: discover workspace + sprints, save to cache

# 3. With sprint_id — parallel: progress + sprint tasks
python3 "$PLUMA/scripts/panluma_api.py" GET /api/v1/tasks/sprints/{sprint_id}/progress
python3 "$PLUMA/scripts/panluma_api.py" GET /api/v1/tasks/sprints/{sprint_id}/tasks --fields title,status,priority,assigned_to --group-by status
```

### Update / create tasks
```bash
python3 "$PLUMA/scripts/panluma_api.py" PUT /api/v1/tasks/{task_id} --data '{"status":"done"}'
python3 "$PLUMA/scripts/panluma_api.py" POST /api/v1/tasks/boards/{board_id}/tasks --data '{"title":"New task","priority":"high"}'
```

## Response Structure

Different endpoints use different list keys. The flags handle this automatically.

| Endpoint pattern | List key | Item type |
|-----------------|----------|-----------|
| `/tasks/my-tasks` | `data` | task |
| `/tasks/boards/{id}/tasks` | `data` | task |
| `/tasks/sprints/{id}/tasks` | `items` | task |
| `/workspaces` | `data` | workspace |
| `/workspaces/{id}/sprints` | `sprints` | sprint |
| `/sprints/{id}/progress` | _(flat object)_ | — |

## Common Modules

| Module | Base Path |
|--------|-----------|
| **tasks** | `/api/v1/tasks` — workspaces, boards, items, sprints, comments |
| **contacts** | `/api/v1/contacts` — companies, people, tiers |
| **sales** | `/api/v1/sales` — pipelines, deals, activities |
| **support** | `/api/v1/support` — tickets, SLA, canned responses |
| **messaging** | `/api/v1/messaging` — conversations, messages, threads |

For all 21 modules, read `references/modules.md`.

## API Info

Base URL: `http://panluma-production-alb-1738326734.us-east-1.elb.amazonaws.com`
Auth: `X-API-Key: plma_live_...` (auto-set from env)
Rate limit: 60 req/min

## User Request

$ARGUMENTS
