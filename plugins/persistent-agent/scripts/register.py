"""
register.py — Register a new domain expert agent.

Scans a directory, generates structured knowledge files, and creates
the agent memory directory with initial knowledge.

Usage:
    python register.py <directory_path> <agent_name>
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# File extensions to analyze
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


def scan_files(root: Path) -> list[dict]:
    """Recursively scan directory for code files."""
    files = []
    for path in sorted(root.rglob("*")):
        if any(ignored in path.parts for ignored in IGNORE_DIRS):
            continue
        if path.is_file() and path.suffix in CODE_EXTENSIONS:
            rel = path.relative_to(root)
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
            except Exception:
                lines = []
                content = ""

            files.append({
                "path": str(rel),
                "suffix": path.suffix,
                "lines": len(lines),
                "size": path.stat().st_size,
                "imports": extract_imports(content, path.suffix),
                "exports": extract_exports(content, path.suffix),
                "definitions": extract_definitions(content, path.suffix),
            })
    return files


def extract_imports(content: str, suffix: str) -> list[str]:
    """Extract import statements from source code."""
    imports = []
    for line in content.splitlines():
        line = line.strip()
        if suffix == ".py":
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)
        elif suffix in (".js", ".ts", ".tsx", ".jsx"):
            if line.startswith("import ") or "require(" in line:
                imports.append(line)
        elif suffix == ".go":
            if line.startswith("import "):
                imports.append(line)
        elif suffix in (".java", ".kt", ".scala"):
            if line.startswith("import "):
                imports.append(line)
        elif suffix in (".rs",):
            if line.startswith("use "):
                imports.append(line)
    return imports[:50]  # Cap to avoid huge outputs


def extract_exports(content: str, suffix: str) -> list[str]:
    """Extract export statements from source code."""
    exports = []
    for line in content.splitlines():
        line = line.strip()
        if suffix in (".js", ".ts", ".tsx", ".jsx"):
            if line.startswith("export "):
                # Truncate long export lines
                exports.append(line[:120])
        elif suffix == ".py":
            if line.startswith("__all__"):
                exports.append(line[:120])
    return exports[:30]


def extract_definitions(content: str, suffix: str) -> list[str]:
    """Extract top-level definitions (classes, functions, etc.)."""
    defs = []
    for line in content.splitlines():
        stripped = line.strip()
        if suffix == ".py":
            if stripped.startswith("class ") or stripped.startswith("def "):
                defs.append(stripped.split("(")[0].split(":")[0])
        elif suffix in (".js", ".ts", ".tsx", ".jsx"):
            if stripped.startswith("function ") or stripped.startswith("class "):
                defs.append(stripped.split("(")[0].split("{")[0].strip())
            elif "const " in stripped and ("=>" in stripped or "function" in stripped):
                parts = stripped.split("=")[0].strip()
                if parts.startswith("export "):
                    parts = parts.replace("export ", "").replace("default ", "")
                if parts.startswith("const ") or parts.startswith("let "):
                    defs.append(parts)
        elif suffix == ".go":
            if stripped.startswith("func ") or stripped.startswith("type "):
                defs.append(stripped.split("{")[0].strip())
        elif suffix in (".java", ".kt"):
            if "class " in stripped or "interface " in stripped:
                defs.append(stripped.split("{")[0].strip()[:100])
        elif suffix == ".rs":
            for kw in ("fn ", "struct ", "enum ", "trait ", "impl "):
                if stripped.startswith(kw) or stripped.startswith("pub " + kw):
                    defs.append(stripped.split("{")[0].split("(")[0].strip()[:100])
    return defs[:100]


def build_tree(files: list[dict], root: Path) -> str:
    """Build a visual directory tree."""
    tree_lines = [f"{root.name}/"]
    dirs_seen = set()
    for f in files:
        parts = Path(f["path"]).parts
        for i in range(len(parts) - 1):
            dir_path = "/".join(parts[: i + 1])
            if dir_path not in dirs_seen:
                dirs_seen.add(dir_path)
                indent = "  " * (i + 1)
                tree_lines.append(f"{indent}{parts[i]}/")
        indent = "  " * len(parts)
        tree_lines.append(f"{indent}{parts[-1]} ({f['lines']} lines)")
    return "\n".join(tree_lines)


def generate_structure(files: list[dict]) -> str:
    """Generate detailed structure documentation."""
    sections = []
    for f in files:
        section = f"### `{f['path']}`\n"
        section += f"- **Lines**: {f['lines']} | **Size**: {f['size']} bytes\n"
        if f["definitions"]:
            section += "- **Definitions**:\n"
            for d in f["definitions"]:
                section += f"  - `{d}`\n"
        sections.append(section)
    return "\n".join(sections)


def generate_dependencies(files: list[dict]) -> str:
    """Generate dependency documentation."""
    sections = []
    for f in files:
        if not f["imports"] and not f["exports"]:
            continue
        section = f"### `{f['path']}`\n"
        if f["imports"]:
            section += "**Imports**:\n"
            for imp in f["imports"]:
                section += f"- `{imp}`\n"
        if f["exports"]:
            section += "**Exports**:\n"
            for exp in f["exports"]:
                section += f"- `{exp}`\n"
        sections.append(section)
    return "\n".join(sections) if sections else "No import/export relationships detected."


def detect_patterns(files: list[dict]) -> str:
    """Detect and document coding patterns."""
    patterns = []

    # Language distribution
    lang_counts: dict[str, int] = {}
    for f in files:
        lang_counts[f["suffix"]] = lang_counts.get(f["suffix"], 0) + 1
    if lang_counts:
        dist = ", ".join(f"`{ext}`: {count}" for ext, count in sorted(lang_counts.items(), key=lambda x: -x[1]))
        patterns.append(f"### Language Distribution\n{dist}\n")

    # File size patterns
    if files:
        sizes = [f["lines"] for f in files]
        avg = sum(sizes) / len(sizes)
        largest = max(files, key=lambda x: x["lines"])
        patterns.append(
            f"### File Size Patterns\n"
            f"- Average file length: {avg:.0f} lines\n"
            f"- Largest file: `{largest['path']}` ({largest['lines']} lines)\n"
            f"- Total files: {len(files)}\n"
        )

    # Naming conventions
    has_snake = any("_" in Path(f["path"]).stem for f in files)
    has_camel = any(
        any(c.isupper() for c in Path(f["path"]).stem[1:])
        for f in files
        if len(Path(f["path"]).stem) > 1
    )
    if has_snake and not has_camel:
        patterns.append("### Naming Convention\nFiles use **snake_case** naming.\n")
    elif has_camel and not has_snake:
        patterns.append("### Naming Convention\nFiles use **camelCase** or **PascalCase** naming.\n")
    elif has_snake and has_camel:
        patterns.append("### Naming Convention\nMixed naming conventions (both snake_case and camelCase/PascalCase).\n")

    return "\n".join(patterns) if patterns else "No strong patterns detected yet. Knowledge will grow with consultations."


def main():
    if len(sys.argv) < 3:
        print("Usage: python register.py <directory_path> <agent_name>", file=sys.stderr)
        sys.exit(1)

    dir_path = Path(sys.argv[1]).resolve()
    agent_name = sys.argv[2]

    if not dir_path.is_dir():
        print(f"Error: '{dir_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # Create agent memory directory
    memory_dir = Path(".claude") / "agent-memory" / agent_name
    memory_dir.mkdir(parents=True, exist_ok=True)

    # Scan files
    print(f"Scanning {dir_path}...")
    files = scan_files(dir_path)
    print(f"Found {len(files)} code files.")

    if not files:
        print("Warning: No code files found in the directory.", file=sys.stderr)

    # Generate domain.json
    domain_config = {
        "name": agent_name,
        "path": str(dir_path),
        "relative_path": str(dir_path.relative_to(Path.cwd())) if dir_path.is_relative_to(Path.cwd()) else str(dir_path),
        "file_count": len(files),
        "total_lines": sum(f["lines"] for f in files),
        "languages": list(set(f["suffix"] for f in files)),
        "created": datetime.now(timezone.utc).isoformat(),
        "last_scan": datetime.now(timezone.utc).isoformat(),
        "files": [{"path": f["path"], "lines": f["lines"], "size": f["size"]} for f in files],
    }
    (memory_dir / "domain.json").write_text(json.dumps(domain_config, indent=2), encoding="utf-8")

    # Generate MEMORY.md
    tree = build_tree(files, dir_path)
    memory_content = f"""# Domain Agent: {agent_name}

**Governed path**: `{domain_config['relative_path']}`
**Registered**: {domain_config['created'][:10]}
**Files**: {len(files)} | **Total lines**: {domain_config['total_lines']}

## Directory Overview

```
{tree}
```

## Purpose

This domain agent governs `{domain_config['relative_path']}`. It maintains deep knowledge
of the code structure, patterns, dependencies, and conventions in this area.

## Key Knowledge

_Initial scan complete. Knowledge will grow with each consultation and sync._

## Consultation Log

_No consultations yet._
"""
    (memory_dir / "MEMORY.md").write_text(memory_content, encoding="utf-8")

    # Generate structure.md
    structure_content = f"""# Structure — {agent_name}

Detailed file and module breakdown for `{domain_config['relative_path']}`.

Last updated: {domain_config['last_scan'][:10]}

{generate_structure(files)}
"""
    (memory_dir / "structure.md").write_text(structure_content, encoding="utf-8")

    # Generate dependencies.md
    deps_content = f"""# Dependencies — {agent_name}

Import/export relationships within `{domain_config['relative_path']}`.

Last updated: {domain_config['last_scan'][:10]}

{generate_dependencies(files)}
"""
    (memory_dir / "dependencies.md").write_text(deps_content, encoding="utf-8")

    # Generate patterns.md
    patterns_content = f"""# Patterns — {agent_name}

Coding patterns and conventions observed in `{domain_config['relative_path']}`.

Last updated: {domain_config['last_scan'][:10]}

{detect_patterns(files)}
"""
    (memory_dir / "patterns.md").write_text(patterns_content, encoding="utf-8")

    print(f"Domain agent '{agent_name}' registered successfully.")
    print(f"Memory directory: {memory_dir}")
    print(f"Files scanned: {len(files)}")
    print(f"Total lines: {domain_config['total_lines']}")
    print(f"\nUse '/consult {agent_name} <question>' to ask questions.")
    print(f"Use '/domain-sync {agent_name}' to refresh knowledge after code changes.")


if __name__ == "__main__":
    main()
