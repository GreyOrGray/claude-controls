#!/usr/bin/env python3
"""
validate.py — Claude Controls deployment validator

Confirms that claude-controls has been correctly installed into a project.
Run from the project root after completing INSTALL.md.

Usage:
    python claude-controls/validate.py
    python claude-controls/validate.py --root C:/MyProject
"""

import argparse
import json
import os
import re
import sys

# ─── Expected deployment state ───────────────────────────────────────────────

REQUIRED_HOOKS = [
    "bash_guard.py",
    "commit_guard.py",
    "file_guard.py",
    "precompact.py",
    "session_init.py",
    "session_log.py",
    "skill_eval.py",
]

REQUIRED_SKILLS = [
    "commit-ready",
    "document-phase",
    "pre-phase",
    "pre-work",
    "session-start",
]

# Must exist and be non-empty
REQUIRED_CONFIG_KEYS = [
    ("project", "name"),
    ("project", "root"),
    ("database", "type"),
    ("paths", "status_doc"),
]

# Must exist, but empty list is valid (project may not use path blocking)
OPTIONAL_LIST_KEYS = [
    ("paths", "hard_block"),
    ("paths", "approval_gate"),
    ("commit", "required_staged"),
]

REQUIRED_LIFECYCLE_HOOKS = ["SessionStart", "UserPromptSubmit", "PreCompact"]

PLACEHOLDER_PATTERN = re.compile(r"\{\{[^}]+\}\}")

# ─── Output helpers ───────────────────────────────────────────────────────────

passed = 0
failed = 0


def ok(msg):
    global passed
    passed += 1
    print(f"  PASS  {msg}")


def fail(msg, detail=""):
    global failed
    failed += 1
    print(f"  FAIL  {msg}")
    if detail:
        for line in detail.splitlines():
            print(f"        {line}")


def section(title):
    print(f"\n{title}")
    print("-" * len(title))


# ─── Checks ───────────────────────────────────────────────────────────────────

def check_config(root):
    section("1. project.config.json")

    config_path = os.path.join(root, "project.config.json")
    if not os.path.isfile(config_path):
        fail("project.config.json exists", f"Not found: {config_path}")
        return None

    ok("project.config.json exists")

    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        fail("project.config.json is valid JSON", str(e))
        return None

    ok("project.config.json is valid JSON")

    for section_key, field_key in REQUIRED_CONFIG_KEYS:
        value = config.get(section_key, {}).get(field_key)
        if value is None or value == "":
            fail(f"config.{section_key}.{field_key} is set",
                 "Run INSTALL.md to generate a complete config")
        else:
            ok(f"config.{section_key}.{field_key}")

    for section_key, field_key in OPTIONAL_LIST_KEYS:
        section_data = config.get(section_key, {})
        if field_key not in section_data:
            fail(f"config.{section_key}.{field_key} key exists",
                 "Run INSTALL.md to generate a complete config")
        else:
            value = section_data[field_key]
            ok(f"config.{section_key}.{field_key} ({len(value)} item(s))")

    status_lines = config.get("session", {}).get("status_lines")
    if status_lines is None:
        fail("config.session.status_lines is set",
             "Run INSTALL.md to generate a complete config")
    elif not isinstance(status_lines, int) or status_lines < 1:
        fail("config.session.status_lines is valid",
             f"Must be a positive integer (got {status_lines!r}). Recommended: 150")
    else:
        ok(f"config.session.status_lines ({status_lines})")

    return config


def check_hooks(root):
    section("2. Hooks (.claude/hooks/)")

    hooks_dir = os.path.join(root, ".claude", "hooks")
    if not os.path.isdir(hooks_dir):
        fail(".claude/hooks/ directory exists", f"Not found: {hooks_dir}")
        return

    ok(".claude/hooks/ exists")

    for fname in REQUIRED_HOOKS:
        path = os.path.join(hooks_dir, fname)
        if os.path.isfile(path):
            ok(fname)
        else:
            fail(fname, f"Missing: {path}\nRe-run INSTALL.md Step 5 to copy hooks")


def check_skills(root):
    section("3. Skills (.claude/skills/)")

    skills_dir = os.path.join(root, ".claude", "skills")
    if not os.path.isdir(skills_dir):
        fail(".claude/skills/ directory exists", f"Not found: {skills_dir}")
        return

    ok(".claude/skills/ exists")

    for skill_name in REQUIRED_SKILLS:
        skill_dir = os.path.join(skills_dir, skill_name)
        skill_file = os.path.join(skill_dir, "SKILL.md")

        if not os.path.isdir(skill_dir):
            fail(f"{skill_name}/ exists", f"Missing directory: {skill_dir}")
        elif not os.path.isfile(skill_file):
            fail(f"{skill_name}/SKILL.md exists", f"Missing file: {skill_file}")
        else:
            ok(f"{skill_name}/SKILL.md")


def check_placeholders(root):
    section("4. Unfilled placeholders in skills")

    skills_dir = os.path.join(root, ".claude", "skills")
    if not os.path.isdir(skills_dir):
        fail("skills directory exists (skipping placeholder check)")
        return

    any_found = False
    for skill_name in REQUIRED_SKILLS:
        skill_file = os.path.join(skills_dir, skill_name, "SKILL.md")
        if not os.path.isfile(skill_file):
            continue
        try:
            content = open(skill_file, encoding="utf-8").read()
        except OSError:
            continue
        matches = PLACEHOLDER_PATTERN.findall(content)
        if matches:
            any_found = True
            fail(f"{skill_name}: unfilled placeholders found",
                 "Run INSTALL.md Step 6 to fill: " + ", ".join(sorted(set(matches))))

    if not any_found:
        ok("No unfilled placeholders in any skill")


def check_settings(root):
    section("5. Settings (.claude/settings.local.json)")

    settings_path = os.path.join(root, ".claude", "settings.local.json")
    if not os.path.isfile(settings_path):
        fail("settings.local.json exists",
             f"Not found: {settings_path}\nRe-run INSTALL.md Step 5")
        return

    ok("settings.local.json exists")

    try:
        with open(settings_path, encoding="utf-8") as f:
            settings = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        fail("settings.local.json is valid JSON", str(e))
        return

    ok("settings.local.json is valid JSON")

    hooks = settings.get("hooks", {})
    for lifecycle in REQUIRED_LIFECYCLE_HOOKS:
        if lifecycle in hooks and hooks[lifecycle]:
            ok(f"{lifecycle} hook registered")
        else:
            fail(f"{lifecycle} hook registered",
                 f"Add {lifecycle} entry - see framework/settings_template.json")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Validate a claude-controls deployment"
    )
    parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Project root to validate (default: current directory)"
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)

    print("Claude Controls - Deployment Validator")
    print("=" * 40)
    print(f"Project root: {root}")

    check_config(root)
    check_hooks(root)
    check_skills(root)
    check_placeholders(root)
    check_settings(root)

    total = passed + failed
    print(f"\n{'=' * 40}")
    print(f"Result: {passed}/{total} checks passed")

    if failed:
        print("Fix the issues above, then re-run to confirm.")
    else:
        print("All checks passed. Claude controls are active.")

    print()
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
