#!/usr/bin/env python3
"""
session_init.py — Session context injection
SessionStart hook. Fires once when a session opens.

Reads the status document and injects current phase, active environment,
and outstanding items as context before Claude's first response.
"""

import json
import pathlib
import sys

HOOK_DIR = pathlib.Path(__file__).parent
CONFIG_PATH = HOOK_DIR.parent.parent / "project.config.json"


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


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    config = load_config()
    if not config:
        sys.exit(0)

    project_name = config.get("project", {}).get("name", "this project")
    status_doc_rel = config.get("paths", {}).get("status_doc", "")
    status_lines = config.get("session", {}).get("status_lines", 150)

    if not status_doc_rel:
        sys.exit(0)

    project_root = pathlib.Path(config.get("project", {}).get("root", ""))
    status_path = project_root / status_doc_rel if project_root else pathlib.Path(status_doc_rel)

    if not status_path.exists():
        block(
            f"SESSION START — {project_name}\n\n"
            f"Status document not found at: {status_path}\n"
            "Warn the user that the status document is missing and ask what we are working on today."
        )

    try:
        lines = status_path.read_text(encoding="utf-8", errors="replace").splitlines()
        excerpt = "\n".join(lines[:status_lines])
    except OSError:
        sys.exit(0)

    block(
        f"SESSION START — {project_name}\n\n"
        "Read the status document excerpt below. Then:\n"
        "1. State the current phase and its status (complete / in-progress / blocked)\n"
        "2. Note the active database or environment if one is set\n"
        "3. Call out any outstanding items (uncommitted work, pending approvals)\n"
        "4. Ask what we are doing today — do NOT start any work until the user responds.\n\n"
        f"--- {status_doc_rel} (first {status_lines} lines) ---\n"
        f"{excerpt}\n"
        "--- END ---"
    )


if __name__ == "__main__":
    main()
