"""
scan_domain.py — Re-scan a domain agent's territory and detect changes.

Compares the current state of the governed directory against the previous
scan stored in domain.json. Outputs a JSON diff and updates domain.json.

Usage:
    python scan_domain.py <agent_name>

Output (stdout):
    JSON object with keys: added, removed, modified, unchanged_count
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Must match the extensions in register.py
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift", ".scala",
    ".vue", ".svelte", ".html", ".css", ".scss", ".sass", ".less",
    ".sql", ".graphql", ".proto", ".yaml", ".yml", ".toml", ".json",
    ".md", ".txt", ".sh", ".bash", ".zsh", ".ps1", ".bat",
}

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    ".next", ".nuxt", "dist", "build", "target", ".cache",
    "coverage", ".nyc_output", ".pytest_cache", ".mypy_cache",
}


def scan_current_files(root: Path) -> dict[str, dict]:
    """Scan directory and return a dict of path -> {lines, size}."""
    files = {}
    for path in sorted(root.rglob("*")):
        if any(ignored in path.parts for ignored in IGNORE_DIRS):
            continue
        if path.is_file() and path.suffix in CODE_EXTENSIONS:
            rel = str(path.relative_to(root))
            try:
                line_count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
            except Exception:
                line_count = 0
            files[rel] = {
                "path": rel,
                "lines": line_count,
                "size": path.stat().st_size,
            }
    return files


def compute_diff(old_files: list[dict], new_files: dict[str, dict]) -> dict:
    """Compute the diff between old and new file lists."""
    old_map = {f["path"]: f for f in old_files}

    added = []
    removed = []
    modified = []
    unchanged = 0

    # Check for new and modified files
    for path, new_info in new_files.items():
        if path not in old_map:
            added.append(path)
        else:
            old_info = old_map[path]
            if new_info["size"] != old_info.get("size") or new_info["lines"] != old_info.get("lines"):
                modified.append({
                    "path": path,
                    "old_lines": old_info.get("lines", 0),
                    "new_lines": new_info["lines"],
                    "old_size": old_info.get("size", 0),
                    "new_size": new_info["size"],
                })
            else:
                unchanged += 1

    # Check for removed files
    for path in old_map:
        if path not in new_files:
            removed.append(path)

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged_count": unchanged,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_domain.py <agent_name>", file=sys.stderr)
        sys.exit(1)

    agent_name = sys.argv[1]
    memory_dir = Path(".claude") / "agent-memory" / agent_name
    domain_json_path = memory_dir / "domain.json"

    if not domain_json_path.exists():
        print(f"Error: No domain agent '{agent_name}' found. Run /register-domain first.", file=sys.stderr)
        sys.exit(1)

    # Load existing config
    config = json.loads(domain_json_path.read_text(encoding="utf-8"))
    domain_path = Path(config["path"])

    if not domain_path.is_dir():
        print(f"Error: Domain path '{domain_path}' no longer exists.", file=sys.stderr)
        sys.exit(1)

    # Scan current state
    print(f"Scanning {domain_path}...", file=sys.stderr)
    current_files = scan_current_files(domain_path)

    # Compute diff
    old_files = config.get("files", [])
    diff = compute_diff(old_files, current_files)

    # Update config
    config["last_scan"] = datetime.now(timezone.utc).isoformat()
    config["file_count"] = len(current_files)
    config["total_lines"] = sum(f["lines"] for f in current_files.values())
    config["files"] = list(current_files.values())

    domain_json_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    # Output diff as JSON
    print(json.dumps(diff, indent=2))

    # Summary to stderr
    total_changes = len(diff["added"]) + len(diff["removed"]) + len(diff["modified"])
    print(f"\nScan complete. {total_changes} changes detected:", file=sys.stderr)
    if diff["added"]:
        print(f"  Added: {len(diff['added'])} files", file=sys.stderr)
    if diff["removed"]:
        print(f"  Removed: {len(diff['removed'])} files", file=sys.stderr)
    if diff["modified"]:
        print(f"  Modified: {len(diff['modified'])} files", file=sys.stderr)
    print(f"  Unchanged: {diff['unchanged_count']} files", file=sys.stderr)


if __name__ == "__main__":
    main()
