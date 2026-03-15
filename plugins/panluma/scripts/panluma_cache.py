#!/usr/bin/env python3
"""PanLuma context cache — stores workspace/sprint IDs to avoid repeated discovery calls.

Usage:
    python panluma_cache.py get                    # Print cached context (or {} if empty/stale)
    python panluma_cache.py set --workspace-id ID [--sprint-id ID --sprint-name NAME --sprint-end DATE]
    python panluma_cache.py clear                  # Delete cache

The cache auto-expires the sprint entry when sprint end_date has passed.
Workspace ID never expires (it almost never changes).

Cache location: ~/.panluma_cache.json
"""

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

CACHE_PATH = Path.home() / ".panluma_cache.json"


def load_cache():
    if not CACHE_PATH.exists():
        return {}
    try:
        with open(CACHE_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(data):
    with open(CACHE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def is_sprint_stale(cache):
    """Sprint is stale if end_date has passed."""
    sprint = cache.get("active_sprint")
    if not sprint:
        return True
    end_date = sprint.get("end_date")
    if not end_date:
        return True
    try:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        return date.today() > end
    except ValueError:
        return True


def cmd_get():
    cache = load_cache()
    result = {}
    if cache.get("workspace_id"):
        result["workspace_id"] = cache["workspace_id"]
    if not is_sprint_stale(cache):
        result["active_sprint"] = cache["active_sprint"]
    print(json.dumps(result, indent=2))


def cmd_set(args):
    cache = load_cache()
    if args.workspace_id:
        cache["workspace_id"] = args.workspace_id
    if args.sprint_id:
        cache["active_sprint"] = {
            "id": args.sprint_id,
            "name": args.sprint_name or "",
            "end_date": args.sprint_end or "",
            "cached_at": datetime.now().isoformat()
        }
    save_cache(cache)
    print(json.dumps(cache, indent=2))


def cmd_clear():
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
        print("Cache cleared.")
    else:
        print("No cache file found.")


def main():
    parser = argparse.ArgumentParser(description="PanLuma context cache")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("get")
    sub.add_parser("clear")

    set_parser = sub.add_parser("set")
    set_parser.add_argument("--workspace-id")
    set_parser.add_argument("--sprint-id")
    set_parser.add_argument("--sprint-name")
    set_parser.add_argument("--sprint-end")

    args = parser.parse_args()

    if args.command == "get":
        cmd_get()
    elif args.command == "set":
        cmd_set(args)
    elif args.command == "clear":
        cmd_clear()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
