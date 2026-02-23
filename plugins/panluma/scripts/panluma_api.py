#!/usr/bin/env python3
"""PanLuma API helper — thin wrapper around the PanLuma REST API.

Usage:
    python panluma_api.py <method> <path> [--data JSON] [--params KEY=VALUE ...]

Examples:
    python panluma_api.py GET /api/v1/status
    python panluma_api.py GET /api/v1/tasks --params limit=10
    python panluma_api.py POST /api/v1/contacts/companies --data '{"name":"Acme"}'
    python panluma_api.py GET /api/v1/sales/deals --params pipeline_id=UUID limit=20
    python panluma_api.py PUT /api/v1/tasks/items/UUID --data '{"title":"Updated"}'
    python panluma_api.py DELETE /api/v1/contacts/companies/UUID

Environment variables:
    PANLUMA_API_KEY  — API key (plma_live_...). Required.
    PANLUMA_BASE_URL — Base URL override (default: http://panluma-production-alb-1738326734.us-east-1.elb.amazonaws.com)
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_BASE = "http://panluma-production-alb-1738326734.us-east-1.elb.amazonaws.com"


def main():
    parser = argparse.ArgumentParser(description="PanLuma API helper")
    parser.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    parser.add_argument("path", help="API path, e.g. /api/v1/tasks")
    parser.add_argument("--data", help="JSON request body", default=None)
    parser.add_argument("--params", nargs="*", help="Query params as KEY=VALUE", default=[])
    args = parser.parse_args()

    api_key = os.environ.get("PANLUMA_API_KEY")
    if not api_key:
        print("Error: PANLUMA_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    base_url = os.environ.get("PANLUMA_BASE_URL", DEFAULT_BASE).rstrip("/")
    path = args.path if args.path.startswith("/") else f"/{args.path}"

    # Build query string
    if args.params:
        qp = {}
        for p in args.params:
            if "=" in p:
                k, v = p.split("=", 1)
                qp[k] = v
        if qp:
            path += ("&" if "?" in path else "?") + urllib.parse.urlencode(qp)

    url = f"{base_url}{path}"

    headers = {
        "X-API-Key": api_key,
        "Accept": "application/json",
    }

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
