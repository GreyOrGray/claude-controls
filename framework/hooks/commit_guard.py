#!/usr/bin/env python3
"""
commit_guard.py — Commit documentation enforcement
PreToolUse hook, Bash matcher.

When committing code from protected paths, verifies that required
documentation files are also staged. Required files loaded from
project.config.json.

Only activates on `git commit` commands (not amend, not other git commands).
"""

import json
import pathlib
import re
import subprocess
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


def get_staged_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip().splitlines() if result.returncode == 0 else []
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")

    # Only intercept `git commit`, not `git commit --amend` or other git commands
    if not re.search(r"\bgit\s+commit\b", command):
        sys.exit(0)
    if "--amend" in command:
        sys.exit(0)

    config = load_config()
    if not config:
        sys.exit(0)

    hard_block = config.get("paths", {}).get("hard_block", [])
    required_staged = config.get("commit", {}).get("required_staged", [])

    if not hard_block or not required_staged:
        sys.exit(0)

    staged = get_staged_files()
    if not staged:
        sys.exit(0)

    # Check if any production code is staged
    production_staged = [
        f for f in staged
        if any(protected in f for protected in hard_block)
    ]

    if not production_staged:
        sys.exit(0)

    # Check required docs are also staged
    staged_lower = [f.lower() for f in staged]
    missing = [
        req for req in required_staged
        if not any(req.lower() in s for s in staged_lower)
    ]

    if missing:
        block(
            "COMMIT BLOCKED — production code is staged but required documentation is missing.\n\n"
            f"Production files staged: {', '.join(production_staged)}\n"
            f"Missing from staged files: {', '.join(missing)}\n\n"
            "Stage the missing files before committing:\n"
            + "\n".join(f"  git add {f}" for f in missing)
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
