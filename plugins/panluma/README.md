# PanLuma Plugin

Claude Code plugin for interacting with the [PanLuma](https://panluma.ai) AI business suite API.

## What it does

Provides the `/panluma` skill that lets you query, create, update, and delete data across all PanLuma modules directly from Claude Code.

## Supported Modules

Tasks, Contacts, Sales/CRM, Bookkeeping, Recruiting, Support, Messaging, Chat, Email, Files, Products, People/HR, Virtual Team (AI agents), Shipments, Users, Admin, Permissions, Integrations, and more — 400+ endpoints total.

## Usage

```
/panluma list my open tasks
/panluma create a contact company named "Acme Corp"
/panluma show sales pipeline summary
/panluma get bookkeeping trial balance
/panluma search for endpoints related to invoices
```

## Setup

Set your PanLuma API key as an environment variable:

```bash
export PANLUMA_API_KEY="plma_live_your_key_here"
```

Or the skill will use the embedded key if configured.

## How it works

1. **Endpoint lookup** — Uses the bundled OpenAPI spec to find the right endpoint
2. **API call** — Makes authenticated HTTP requests to the PanLuma API
3. **Results** — Returns formatted JSON responses

## Scripts

- `scripts/panluma_api.py` — HTTP client for making API calls
- `scripts/panluma_lookup.py` — OpenAPI spec search/lookup tool
- `scripts/openapi.json` — Full PanLuma OpenAPI 3.1 specification
