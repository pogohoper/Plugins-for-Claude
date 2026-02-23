#!/usr/bin/env python3
"""Look up PanLuma API endpoints from the local OpenAPI spec.

Usage:
    python panluma_lookup.py [search_term]
    python panluma_lookup.py tasks
    python panluma_lookup.py "POST /api/v1/contacts"
    python panluma_lookup.py --module sales
    python panluma_lookup.py --detail "/api/v1/tasks"

Without arguments: prints all modules and endpoint counts.
With search_term: searches endpoints by path, summary, or tag.
With --module: lists all endpoints in a module.
With --detail: shows full endpoint details (params, body, description).
"""

import argparse
import json
import os
import sys
from pathlib import Path

SPEC_PATH = Path(__file__).parent / "openapi.json"


def load_spec():
    if not SPEC_PATH.exists():
        print(f"Error: OpenAPI spec not found at {SPEC_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(SPEC_PATH) as f:
        return json.load(f)


def list_modules(spec):
    by_tag = {}
    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            tags = details.get("tags", ["untagged"])
            for tag in tags:
                by_tag.setdefault(tag, 0)
                by_tag[tag] += 1
    print(f"PanLuma API v{spec['info']['version']} — {sum(by_tag.values())} endpoints in {len(by_tag)} modules\n")
    for tag in sorted(by_tag):
        print(f"  {tag:40s} {by_tag[tag]:3d} endpoints")


def search_endpoints(spec, query):
    query_lower = query.lower()
    results = []
    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            summary = details.get("summary", "")
            desc = details.get("description", "")
            tags = " ".join(details.get("tags", []))
            searchable = f"{method} {path} {summary} {desc} {tags}".lower()
            if query_lower in searchable:
                results.append((method.upper(), path, summary, details.get("tags", [])))
    if not results:
        print(f"No endpoints matching '{query}'")
        return
    print(f"Found {len(results)} endpoints matching '{query}':\n")
    for method, path, summary, tags in results:
        tag_str = f" [{', '.join(tags)}]" if tags else ""
        print(f"  {method:6s} {path}")
        if summary:
            print(f"         {summary}{tag_str}")
        print()


def list_module(spec, module):
    results = []
    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            tags = details.get("tags", [])
            if module.lower() in [t.lower() for t in tags]:
                results.append((method.upper(), path, details.get("summary", "")))
    if not results:
        print(f"No module matching '{module}'")
        return
    print(f"Module '{module}' — {len(results)} endpoints:\n")
    for method, path, summary in results:
        print(f"  {method:6s} {path}  — {summary}")


def show_detail(spec, path_query):
    path_query = path_query.rstrip("/")
    for path, methods in spec.get("paths", {}).items():
        if path.rstrip("/") != path_query:
            continue
        print(f"Path: {path}\n")
        for method, details in methods.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            print(f"  {method.upper()} — {details.get('summary', 'No summary')}")
            if details.get("description"):
                print(f"  Description: {details['description'][:300]}")
            params = details.get("parameters", [])
            if params:
                print(f"  Parameters:")
                for p in params:
                    req = " (required)" if p.get("required") else ""
                    schema = p.get("schema", {})
                    ptype = schema.get("type", "any")
                    default = f", default={schema['default']}" if "default" in schema else ""
                    print(f"    - {p['name']}: {ptype}{req}{default} (in {p.get('in', '?')})")
            rb = details.get("requestBody", {})
            if rb:
                content = rb.get("content", {})
                for ct, schema_info in content.items():
                    examples = schema_info.get("examples", {})
                    if examples:
                        print(f"  Request body ({ct}):")
                        for name, ex in examples.items():
                            print(f"    {name}: {json.dumps(ex.get('value', {}), indent=6)}")
                    elif "schema" in schema_info:
                        print(f"  Request body ({ct}): {json.dumps(schema_info['schema'], indent=6)[:500]}")
            print()
        return
    print(f"Path '{path_query}' not found. Try searching with: python panluma_lookup.py {path_query.split('/')[-1]}")


def main():
    parser = argparse.ArgumentParser(description="PanLuma API endpoint lookup")
    parser.add_argument("query", nargs="?", help="Search term")
    parser.add_argument("--module", "-m", help="List endpoints in a module")
    parser.add_argument("--detail", "-d", help="Show full details for a path")
    args = parser.parse_args()

    spec = load_spec()

    if args.detail:
        show_detail(spec, args.detail)
    elif args.module:
        list_module(spec, args.module)
    elif args.query:
        search_endpoints(spec, args.query)
    else:
        list_modules(spec)


if __name__ == "__main__":
    main()
