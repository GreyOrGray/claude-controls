#!/usr/bin/env python3
"""
skill_eval.py — Forced skill evaluation
UserPromptSubmit hook. Fires on every user message.

Injects a mandatory skill evaluation step before Claude responds,
achieving reliable skill activation (~84% vs ~20% without this hook).

Reads available skills from .claude/skills/ and lists them with their
descriptions so Claude can evaluate which apply to the current task.
"""

import json
import pathlib
import sys

HOOK_DIR = pathlib.Path(__file__).parent
SKILLS_DIR = HOOK_DIR.parent / "skills"


def inject_context(text: str) -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": text,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def load_skills() -> list[dict]:
    skills = []
    if not SKILLS_DIR.exists():
        return skills

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8", errors="replace")
        name = skill_dir.name
        description = ""

        in_frontmatter = False
        for line in content.splitlines():
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter and line.startswith("description:"):
                description = line[len("description:"):].strip().strip('"')
                break

        if name and description:
            skills.append({"name": name, "description": description})

    return skills


def main() -> None:
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    skills = load_skills()
    if not skills:
        sys.exit(0)

    skill_list = "\n".join(
        f"  - {s['name']}: {s['description']}" for s in skills
    )

    inject_context(
        "SKILL EVALUATION — Before responding to the user's message, evaluate:\n\n"
        "Step 1: For each skill below, decide YES or NO — does it apply to this task?\n"
        f"{skill_list}\n\n"
        "Step 2: For each YES skill, load and follow its instructions before proceeding.\n"
        "Step 3: Then respond to the user.\n\n"
        "If no skills apply, proceed directly to the user's request."
    )


if __name__ == "__main__":
    main()
