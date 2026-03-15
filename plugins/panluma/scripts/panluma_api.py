#!/usr/bin/env python3
"""PanLuma API helper — thin wrapper around the PanLuma REST API.

Usage:
    python panluma_api.py <method> <path> [--data JSON] [--params KEY=VALUE ...]
           [--compact] [--fields FIELD,...] [--group-by FIELD]

Examples:
    python panluma_api.py GET /api/v1/status
    python panluma_api.py GET /api/v1/tasks/my-tasks --compact
    python panluma_api.py GET /api/v1/tasks/my-tasks --fields title,status,priority
    python panluma_api.py GET /api/v1/tasks/sprints/ID/tasks --compact --group-by status
    python panluma_api.py GET /api/v1/tasks/my-tasks --params status=in_progress
    python panluma_api.py POST /api/v1/contacts/companies --data '{"name":"Acme"}'

Environment variables:
    PANLUMA_API_KEY  — API key (plma_live_...). Required.
    PANLUMA_BASE_URL — Base URL override.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_BASE = "http://panluma-production-alb-1738326734.us-east-1.elb.amazonaws.com"

COMPACT_FIELDS = {
    "task": ["id", "title", "status", "priority", "assigned_to", "story_points",
             "due_date", "sprint_id", "board_id", "parent_task_id"],
    "sprint": ["id", "name", "description", "status", "start_date", "end_date",
               "committed_points", "committed_task_count", "completed_points",
               "completed_task_count", "sequence_number"],
    "workspace": ["id", "name", "description", "sprint_settings", "board_count"],
    "contact": ["id", "name", "email", "phone", "company_id", "tier"],
    "company": ["id", "name", "industry", "website", "tier"],
    "deal": ["id", "title", "stage", "value", "currency", "status", "assigned_to"],
}


def detect_item_type(item):
    if not isinstance(item, dict):
        return None
    keys = set(item.keys())
    if "sprint_id" in keys or "column_values" in keys or ("board_id" in keys and "title" in keys):
        return "task"
    if "committed_points" in keys or "committed_task_count" in keys:
        return "sprint"
    if "board_count" in keys and "sprint_settings" in keys:
        return "workspace"
    if "pipeline_id" in keys and "stage" in keys:
        return "deal"
    return None


def compact_item(item, item_type=None, custom_fields=None):
    if not isinstance(item, dict):
        return item
    if custom_fields:
        return {k: v for k, v in item.items() if k in custom_fields}
    if not item_type:
        item_type = detect_item_type(item)
    if item_type and item_type in COMPACT_FIELDS:
        return {k: v for k, v in item.items() if k in COMPACT_FIELDS[item_type]}
    return item


def find_list_in_response(data):
    if isinstance(data, list):
        return data, None
    if isinstance(data, dict):
        for key in ["data", "items", "sprints", "workspaces", "contacts",
                     "companies", "deals", "tickets", "messages", "members"]:
            if key in data and isinstance(data[key], list):
                return data[key], key
    return None, None


def compact_response(data, custom_fields=None):
    items, list_key = find_list_in_response(data)
    if items is not None:
        item_type = detect_item_type(items[0]) if items else None
        compacted = [compact_item(i, item_type, custom_fields) for i in items]
        result = {"_total": len(compacted)}
        if isinstance(data, dict):
            for meta_key in ["total", "pagination", "has_more", "next_offset"]:
                if meta_key in data:
                    result[meta_key] = data[meta_key]
            result[list_key or "items"] = compacted
        else:
            result["items"] = compacted
        return result
    if isinstance(data, dict):
        return compact_item(data, custom_fields=custom_fields)
    return data


def group_response(data, group_field, custom_fields=None):
    """Group list items by a field, with per-group counts and items."""
    items, list_key = find_list_in_response(data)
    if items is None:
        return data
    item_type = detect_item_type(items[0]) if items else None
    groups = {}
    for item in items:
        key = str(item.get(group_field, "unknown"))
        if key not in groups:
            groups[key] = {"count": 0, "items": []}
        groups[key]["count"] += 1
        compacted = compact_item(item, item_type, custom_fields) if custom_fields or item_type else item
        groups[key]["items"].append(compacted)
    result = {"_total": len(items), "_grouped_by": group_field}
    if isinstance(data, dict):
        for meta_key in ["total", "pagination"]:
            if meta_key in data:
                result[meta_key] = data[meta_key]
    result["groups"] = groups
    return result


def main():
    parser = argparse.ArgumentParser(description="PanLuma API helper")
    parser.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    parser.add_argument("path", help="API path, e.g. /api/v1/tasks")
    parser.add_argument("--data", help="JSON request body", default=None)
    parser.add_argument("--params", nargs="*", help="Query params as KEY=VALUE", default=[])
    parser.add_argument("--compact", action="store_true",
                        help="Return only key fields per item (reduces output ~90%%)")
    parser.add_argument("--fields", help="Comma-separated fields to extract (e.g. id,title,status)")
    parser.add_argument("--group-by", dest="group_by",
                        help="Group results by field (e.g. status, priority, assigned_to)")
    args = parser.parse_args()

    api_key = os.environ.get("PANLUMA_API_KEY")
    if not api_key:
        print("Error: PANLUMA_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    base_url = os.environ.get("PANLUMA_BASE_URL", DEFAULT_BASE).rstrip("/")
    path = args.path if args.path.startswith("/") else f"/{args.path}"

    if args.params:
        qp = {}
        for p in args.params:
            if "=" in p:
                k, v = p.split("=", 1)
                qp[k] = v
        if qp:
            path += ("&" if "?" in path else "?") + urllib.parse.urlencode(qp)

    url = f"{base_url}{path}"
    headers = {"X-API-Key": api_key, "Accept": "application/json"}

    body = None
    if args.data:
        body = args.data.encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=args.method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8")
            try:
                data = json.loads(raw)
                custom_fields = None
                if args.fields:
                    custom_fields = set(f.strip() for f in args.fields.split(","))
                if args.group_by:
                    data = group_response(data, args.group_by, custom_fields)
                elif args.compact or custom_fields:
                    data = compact_response(data, custom_fields)
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(raw)
            if status >= 400:
                sys.exit(1)
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        try:
            print(json.dumps(json.loads(body_text), indent=2, ensure_ascii=False))
        except Exception:
            print(body_text)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
