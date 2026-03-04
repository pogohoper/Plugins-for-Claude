# PanLuma API Modules Reference

## API Base URL

`http://panluma-production-alb-1738326734.us-east-1.elb.amazonaws.com`

Auth header: `X-API-Key: plma_live_...`

Rate limit: 60 requests/minute (check `X-RateLimit-*` response headers).

## Module Overview

PanLuma has 1,400+ endpoints across 100+ modules. Below are the primary modules grouped by domain. Many modules have sub-modules (e.g., `sales-settings`, `sales-export-import`) — use the lookup script to discover them.

### Core Business

| Module | Base Path | Endpoints | Key Operations |
|--------|-----------|-----------|----------------|
| **tasks** | `/api/v1/tasks` | 77 | Workspaces, boards, items, comments, automations |
| **contacts** | `/api/v1/contacts` | 34 | Companies, people, tiers |
| **sales** | `/api/v1/sales` | 70 | Pipelines, stages, deals, activities, notes, reports |
| **accounting** | `/api/v1/accounting` | 75 | Accounts, journal entries, invoices, bills, payments, tax rates, reports |
| **products** | `/api/v1/products` | 38 | Families, products, variants, price lists, bundles |
| **shipments** | `/api/v1/shipments` | 55 | Shipments, legs, cargo, line items, routing, documents |

### People & Recruiting

| Module | Base Path | Endpoints | Key Operations |
|--------|-----------|-----------|----------------|
| **people** | `/api/v1/people` | 20 | Employees, org chart, compensation |
| **employees** | `/api/v1/employees` | 15 | Employee records, details |
| **recruiting** | `/api/v1/recruiting` | 111 | Jobs, candidates, applications, interviews, offers, pipelines |

### Communication

| Module | Base Path | Endpoints | Key Operations |
|--------|-----------|-----------|----------------|
| **messaging** | `/api/v1/messaging` | 21 | Conversations (DM/group/channel), messages, threads, reactions |
| **chat** | `/api/v1/chat` | 16 | AI chat sessions, messages |
| **email** | `/api/v1/emails` | 15 | Inbox, send, read/unread, delegated access |
| **support** | `/api/v1/support` | 53 | Tickets, SLA policies, canned responses, satisfaction surveys |

### AI & Virtual Team

| Module | Base Path | Endpoints | Key Operations |
|--------|-----------|-----------|----------------|
| **virtual-team** | `/api/v1/virtual-team` | 28 | AI team members, skills, triggers |
| **virtual-team-memory** | `/api/v1/virtual-team/memory` | 25 | Agent memories |
| **virtual-team-tools** | `/api/v1/virtual-team/tools` | 5 | Agent tool definitions |
| **virtual-team-schedule** | `/api/v1/virtual-team/schedule` | 16 | Agent scheduling |
| **virtual-team-oversight** | `/api/v1/virtual-team/oversight` | 15 | Agent oversight/control |

### Website & Portal

| Module | Base Path | Endpoints | Key Operations |
|--------|-----------|-----------|----------------|
| **website-hosting** | `/api/v1/website-hosting` | 57 | Website management, hosting |
| **website-wizard** | `/api/v1/website-wizard` | 26 | Website builder wizard |
| **forms_bpm** | `/api/v1/forms-bpm` | 48 | Business process forms |

### Platform & Admin

| Module | Base Path | Endpoints | Key Operations |
|--------|-----------|-----------|----------------|
| **users** | `/api/v1/users` | 26 | User management, groups, notifications |
| **admin** | `/api/v1/admin` | 52 | Tenant settings, offices, email templates, AI settings |
| **permissions** | `/api/v1/permissions` | 16 | RBAC, roles, grants, access lists |
| **files** | `/api/v1/files` | 29 | Upload, download, folders, external storage |
| **integrations** | `/api/v1/integrations` | 23 | Google (Gmail, Drive, Maps), currency |
| **developer** | `/api/v1/developer` | 19 | API keys, sandbox, usage |
| **auth** | `/api/v1/auth` | 22 | Login, register, SSO, password management |
| **Dashboard** | `/api/v1/dashboard` | 1 | Dashboard stats |

**Note:** `bookkeeping` has been renamed to `accounting` in the current API.

## Detailed Endpoint Discovery

Use the lookup script to explore endpoints:

```bash
# List all modules with endpoint counts
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py"

# Search for endpoints by keyword
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" "invoice"
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" "candidate"

# List all endpoints in a specific module
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --module sales
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --module accounting
python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --module recruiting

# Get full details for a specific path (parameters, body schema)
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --detail "/api/v1/tasks"
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --detail "/api/v1/sales/deals"
MSYS_NO_PATHCONV=1 python "${CLAUDE_PLUGIN_ROOT}/scripts/panluma_lookup.py" --detail "/api/v1/accounting/invoices"
```

API call examples are in the main SKILL.md to keep them readily available during workflow execution.
