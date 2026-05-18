#!/usr/bin/env python3
"""
session_log.py — Async audit log
PostToolUse hook, all tools, async: true.

Appends a JSONL entry for every tool call to a daily log file.
Never blocks. Failures are silent.
"""

import json
import pathlib
import sys
from datetime import datetime, timezone

LOG_DIR = pathlib.Path.home() / ".claude" / "session-logs"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        tool = data.get("tool_name", "unknown")
        session = data.get("session_id", "unknown")
        tool_input = data.get("tool_input", {})
        tool_response = data.get("tool_response", {})

        # Extract the most relevant detail per tool type
        detail = (
            tool_input.get("command")
            or tool_input.get("file_path")
            or tool_input.get("pattern")
            or tool_input.get("query")
            or tool_input.get("url")
            or ""
        )

        # Detect errors in response
        response_text = ""
        if isinstance(tool_response, dict):
            response_text = tool_response.get("output", "") or tool_response.get("error", "")
        elif isinstance(tool_response, str):
            response_text = tool_response

        error_signals = ["error:", "fatal:", "permission denied", "traceback", "exception"]
        has_error = any(sig in response_text.lower() for sig in error_signals)

        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session": session,
            "tool": tool,
            "detail": detail[:500] if detail else "",
            "error": has_error,
        }

        log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
