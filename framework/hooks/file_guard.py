#!/usr/bin/env python3
"""
file_guard.py — File write/edit protection
PreToolUse hook, Write|Edit matcher.

Three-tier protection loaded from project.config.json:
  Tier 1 (hard_block)     — never editable, always blocked
  Tier 2 (approval_gate)  — requires .claude/work-approved sentinel (7-day expiry)
  Tier 3 (everything else) — allowed

paths.approval_exempt (optional): patterns that bypass the Tier 2 approval gate.
Useful for regression tests, fixtures, or scratch subdirectories that don't need
per-session approval. Checked BEFORE the approval_gate match — if file_path matches
any approval_exempt pattern, the file is allowed without requiring the sentinel.
"""

import json
import pathlib
import sys
from datetime import date

HOOK_DIR = pathlib.Path(__file__).parent
CONFIG_PATH = HOOK_DIR.parent.parent / "project.config.json"
SENTINEL_PATH = HOOK_DIR.parent / "work-approved"
SENTINEL_MAX_AGE_DAYS = 7


def block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def load_config():
    if not CONFIG_PATH.exists():
        return None
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def sentinel_valid() -> bool:
    if not SENTINEL_PATH.exists():
        return False
    try:
        payload = json.loads(SENTINEL_PATH.read_text(encoding="utf-8"))
        approved_date = date.fromisoformat(payload["date"])
        return (date.today() - approved_date).days <= SENTINEL_MAX_AGE_DAYS
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return False


def path_matches(file_path: str, patterns: list[str], project_root: str = "") -> str | None:
    """Match patterns as project-root-relative path prefixes.

    Patterns like "app/src/" should match "app/src/foo.py" but NOT
    "scratch/app/src/foo.py". So we strip the project root, then use
    startswith — not substring — to avoid false positives where the
    pattern appears as a subdirectory deeper in the tree.
    """
    normalized = file_path.replace("\\", "/")
    if project_root:
        root_norm = project_root.replace("\\", "/").rstrip("/").lower()
        if normalized.lower().startswith(root_norm + "/"):
            normalized = normalized[len(root_norm) + 1:]
    for pattern in patterns:
        norm_pattern = pattern.replace("\\", "/").lstrip("/")
        if normalized.startswith(norm_pattern):
            return pattern
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    config = load_config()
    if not config:
        sys.exit(0)

    hard_block = config.get("paths", {}).get("hard_block", [])
    approval_gate = config.get("paths", {}).get("approval_gate", [])
    approval_exempt = config.get("paths", {}).get("approval_exempt", [])
    project_name = config.get("project", {}).get("name", "this project")
    project_root = config.get("project", {}).get("root", "")

    # Tier 1: hard block
    matched = path_matches(file_path, hard_block, project_root)
    if matched:
        block(
            f"HARD BLOCK — {file_path} is in a protected path ({matched}).\n\n"
            f"This path is committed production code for {project_name}. "
            "Work in the scratch/dev directory instead. "
            "Ask the project owner to promote your changes when ready."
        )

    # Tier 2: approval gate (with exempt bypass)
    matched = path_matches(file_path, approval_gate, project_root)
    if matched:
        # Check if this path is in the exempt list — if so, skip the approval requirement
        exempt_match = path_matches(file_path, approval_exempt, project_root)
        if not exempt_match and not sentinel_valid():
            block(
                f"APPROVAL REQUIRED — {file_path} is in a gated path ({matched}).\n\n"
                "This path requires explicit approval before editing. "
                f"To approve, create the file `.claude/work-approved` with this content:\n\n"
                '{"date": "YYYY-MM-DD", "phase": "Phase X.Y", "approved_by": "your name"}\n\n'
                "Then retry. Approval is valid for 7 days."
            )

    # Tier 3: allow
    sys.exit(0)


if __name__ == "__main__":
    main()
