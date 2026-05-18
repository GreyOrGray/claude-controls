#!/usr/bin/env python3
"""
bash_guard.py — Bash command safety guard
PreToolUse hook, Bash matcher.

Blocks destructive operations and commands targeting production databases.
All protected patterns loaded from project.config.json.
"""

import json
import pathlib
import re
import sys

HOOK_DIR = pathlib.Path(__file__).parent
CONFIG_PATH = HOOK_DIR.parent.parent / "project.config.json"

# Unconditional blocks — dangerous regardless of project
ALWAYS_BLOCKED = [
    (r"\brm\s+(?:-[a-zA-Z]+\s+)*-(?=[a-zA-Z]*r)(?=[a-zA-Z]*f)[a-zA-Z]+\b", "rm -rf is blocked"),
    (r"DROP\s+(TABLE|DATABASE|SCHEMA)\b", "DROP TABLE/DATABASE/SCHEMA is blocked"),
    (r"TRUNCATE\s+TABLE\b", "TRUNCATE TABLE is blocked"),
    (r"\bFLUSHALL\b|\bFLUSHDB\b", "Redis FLUSH commands are blocked"),
    (r"git\s+push\s+.*--force\s+\S*(main|master)", "force push to main/master is blocked"),
    (r"\bprintenv\b.*(KEY|TOKEN|SECRET|PASSWORD|API)", "printing credentials is blocked"),
]

# Credential file access patterns
CREDENTIAL_PATTERNS = [
    r"\.pem\b", r"\.key\b", r"id_rsa\b", r"id_ed25519\b",
    r"\.env\b(?!iron)", r"shell_history\b", r"bash_history\b",
]


def block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": f"bash-guard: {reason}"}))
    sys.exit(0)


def load_config():
    if not CONFIG_PATH.exists():
        return None
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def is_write_to_path(command: str, protected_path: str) -> bool:
    """
    Returns True if the command appears to write/modify the protected path.
    Catches: cp/mv to path, rm of path, redirects (>, >>) to path, tee path,
    PowerShell Copy-Item/Move-Item/Set-Content/Out-File targeting path.

    Avoids false positives where the path is just mentioned as a substring
    (sed substitutions, echo strings, comments, --root flags, etc.).
    """
    # Normalize backslashes (Windows/PowerShell paths) so config patterns
    # written with forward slashes still match.
    command = command.replace("\\", "/")
    protected_path = protected_path.replace("\\", "/")
    p = re.escape(protected_path.rstrip("/"))
    write_patterns = [
        rf"\b(cp|mv|cat)\s+\S+\s+{p}",                # cp/mv SOURCE path/...
        rf"\brm\s+(-[a-zA-Z]+\s+)*{p}",               # rm [-flags] path/...
        rf">\s*{p}",                                  # > path/...
        rf">>\s*{p}",                                 # >> path/...
        rf"\btee\s+(-[a-zA-Z]+\s+)*{p}",              # tee path/...
        rf"(?i)Copy-Item\s+\S+\s+{p}",                # PowerShell Copy-Item ... path
        rf"(?i)Move-Item\s+\S+\s+{p}",                # PowerShell Move-Item ... path
        rf"(?i)Set-Content\s+(-Path\s+)?{p}",         # PowerShell Set-Content ... path
        rf"(?i)Out-File\s+(-FilePath\s+)?{p}",        # PowerShell Out-File ... path
        rf"(?i)Add-Content\s+(-Path\s+)?{p}",         # PowerShell Add-Content ... path
    ]
    for pat in write_patterns:
        if re.search(pat, command):
            return True
    return False


def is_db_tool_context(command: str, db_pattern: re.Pattern) -> bool:
    """
    Returns True if a production DB name appears as a connection target in a
    database tool context. Recognized patterns:
      sqlcmd|psql|mysql -d <name> | -D <name> | --database <name> | --db <name>
      Connection string fragments: Database=<name>, Initial Catalog=<name>
      Invoke-Sqlcmd -Database <name>

    Avoids false positives where the DB name happens to be a directory or
    substring elsewhere in the command (e.g. paths like C:/MyProject).
    """
    db_tool_patterns = [
        # Flag-based: -d NAME, -D NAME, --database NAME, --db NAME
        rf"-d\s+({db_pattern.pattern})",
        rf"-D\s+({db_pattern.pattern})",
        rf"--database[\s=]+({db_pattern.pattern})",
        rf"--db[\s=]+({db_pattern.pattern})",
        # PowerShell Invoke-Sqlcmd
        rf"-Database\s+({db_pattern.pattern})",
        # Connection string fragments
        rf"Database\s*=\s*({db_pattern.pattern})",
        rf"Initial\s+Catalog\s*=\s*({db_pattern.pattern})",
    ]
    for pat in db_tool_patterns:
        if re.search(pat, command, re.IGNORECASE):
            return True
    return False


def build_db_pattern(config) -> re.Pattern | None:
    """Build regex that matches production DB names but not test DB names."""
    prod_patterns = config.get("database", {}).get("production_patterns", [])
    test_patterns = config.get("database", {}).get("test_patterns", [])

    if not prod_patterns:
        return None

    prod_alts = "|".join(re.escape(p.rstrip("*")) for p in prod_patterns)
    test_alts = "|".join(re.escape(p.rstrip("*")) for p in test_patterns) if test_patterns else None

    if test_alts:
        return re.compile(rf"\b(?!(?:{test_alts}))(?:{prod_alts})\b", re.IGNORECASE)
    return re.compile(rf"\b({prod_alts})\b", re.IGNORECASE)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    # Always-blocked patterns
    for pattern, reason in ALWAYS_BLOCKED:
        if re.search(pattern, command, re.IGNORECASE):
            block(reason)

    # Credential file access
    for pattern in CREDENTIAL_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            block(f"accessing credential files is blocked (matched: {pattern})")

    # Project-specific: production database protection
    # Only fires when a production DB name appears in a database-tool context
    # (sqlcmd -d, psql -d, mysql -D, connection string Database=, etc.) — not
    # when the DB name happens to also appear as a directory in a file path.
    config = load_config()
    if config:
        db_pattern = build_db_pattern(config)
        if db_pattern and is_db_tool_context(command, db_pattern):
            prod_names = config.get("database", {}).get("production_patterns", [])
            block(
                f"command targets a production database ({', '.join(prod_names)}). "
                "Use a test database instead."
            )

        # Project-specific: hard-blocked paths in shell commands
        # Only fires on destructive/write operations targeting protected paths,
        # not on commands that happen to mention the path as a substring (e.g.
        # sed substitutions, echo strings, comments).
        for protected_path in config.get("paths", {}).get("hard_block", []):
            if is_write_to_path(command, protected_path):
                block(
                    f"command writes to protected path ({protected_path}). "
                    "Work in the scratch/dev directory instead."
                )

    sys.exit(0)


if __name__ == "__main__":
    main()
