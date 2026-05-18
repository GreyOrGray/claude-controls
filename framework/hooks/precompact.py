#!/usr/bin/env python3
"""
precompact.py — Context preservation before compaction
PreCompact hook.

Reads critical project files and writes a context snapshot before
the conversation is compacted. The snapshot helps restore orientation
in the next session.
"""

import json
import pathlib
import sys
from datetime import datetime, timezone

HOOK_DIR = pathlib.Path(__file__).parent
CONFIG_PATH = HOOK_DIR.parent.parent / "project.config.json"
SNAPSHOT_PATH = HOOK_DIR.parent / "context_snapshot.md"

# Files to always attempt to include (relative to project root)
ALWAYS_INCLUDE = [
    "CLAUDE.md",
    "CHANGELOG.md",
]


def load_config():
    if not CONFIG_PATH.exists():
        return None
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def read_file_preview(path: pathlib.Path, max_lines: int = 100) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        preview = "\n".join(lines[:max_lines])
        if len(lines) > max_lines:
            preview += f"\n... ({len(lines) - max_lines} more lines)"
        return preview
    except OSError:
        return "[could not read file]"


def main() -> None:
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    config = load_config()
    project_name = config.get("project", {}).get("name", "Project") if config else "Project"
    project_root = pathlib.Path(config.get("project", {}).get("root", "")) if config else pathlib.Path(".")
    status_doc = config.get("paths", {}).get("status_doc", "") if config else ""

    sections = []
    sections.append(
        f"# Context Snapshot — {project_name}\n"
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n"
        f"**Reason:** Pre-compaction context preservation\n"
    )

    # Status document (most important)
    if status_doc:
        status_path = project_root / status_doc
        if status_path.exists():
            sections.append(
                f"## Status Document ({status_doc})\n\n"
                + read_file_preview(status_path, max_lines=150)
            )

    # Always-include files
    for rel_path in ALWAYS_INCLUDE:
        path = project_root / rel_path
        if path.exists():
            sections.append(
                f"## {rel_path}\n\n"
                + read_file_preview(path, max_lines=50)
            )

    # CHANGELOG (last 50 lines — most recent changes matter most)
    changelog = project_root / "CHANGELOG.md"
    if changelog.exists():
        try:
            lines = changelog.read_text(encoding="utf-8", errors="replace").splitlines()
            recent = "\n".join(lines[:50])
            sections.append(f"## CHANGELOG (recent)\n\n{recent}")
        except OSError:
            pass

    snapshot = "\n\n---\n\n".join(sections)

    try:
        SNAPSHOT_PATH.write_text(snapshot, encoding="utf-8")
    except OSError:
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
