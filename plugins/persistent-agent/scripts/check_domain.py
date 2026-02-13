"""
check_domain.py — PostToolUse hook script.

Checks if an edited file belongs to any registered domain agent's territory.
If so, outputs a message suggesting the user run /domain-sync.

Usage:
    python check_domain.py <file_path>

Exit codes:
    0 — No domain agents affected, or file doesn't match any territory
    0 — Domain agent affected (message printed to stdout as hook feedback)
"""

import json
import sys
from pathlib import Path


def find_agent_memory_dir() -> Path | None:
    """Find the .claude/agent-memory directory."""
    candidates = [
        Path(".claude") / "agent-memory",
        Path.home() / ".claude" / "agent-memory",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def check_file_against_domains(file_path: str) -> list[str]:
    """Check if a file path falls within any registered domain."""
    memory_dir = find_agent_memory_dir()
    if memory_dir is None:
        return []

    affected_agents = []
    file_resolved = Path(file_path).resolve()

    for agent_dir in memory_dir.iterdir():
        if not agent_dir.is_dir():
            continue
        domain_json = agent_dir / "domain.json"
        if not domain_json.exists():
            continue

        try:
            config = json.loads(domain_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        domain_path = Path(config.get("path", "")).resolve()
        try:
            file_resolved.relative_to(domain_path)
            affected_agents.append(config["name"])
        except ValueError:
            continue

    return affected_agents


def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    file_path = sys.argv[1]
    if not file_path:
        sys.exit(0)

    affected = check_file_against_domains(file_path)

    if affected:
        agents_str = ", ".join(f"`{a}`" for a in affected)
        print(
            f"Note: The file `{file_path}` is within the territory of domain agent(s): {agents_str}. "
            f"Their knowledge may now be stale. Consider running `/domain-sync <agent-name>` to update."
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
