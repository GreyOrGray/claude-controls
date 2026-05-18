---
name: session-start
description: {{project_name}} session startup. Load this skill at the beginning of every session to orient on current phase, active environment, and outstanding items before doing any work. Use when starting a new conversation or when asked what we should work on.
---

# Session Start — {{project_name}}

## First-Run Check: Reference INDEX files

Before the briefing, check whether each `.claude/references/{category}/INDEX.md` exists — categories are `architecture`, `business-rules`, `standards`, `workflow`.

- **If all four exist:** skip this check silently.
- **If any are missing:** mention it in the briefing and offer to generate them. If the user agrees, walk through them one at a time:
  1. Read the matching `references/{category}/README.md` for shape guidance
  2. Scan the repo for relevant artifacts (modules and schemas for *architecture*; conventions and lint configs for *standards*; existing process docs for *workflow*; domain rules and specs for *business-rules*)
  3. Draft a project-specific `INDEX.md` based on what's actually there
  4. Present the draft for confirmation before writing the file
- **If the user defers:** proceed with the normal briefing. The offer will repeat next session until the files exist.

## What To Do

You have already received the status document excerpt from the SessionStart hook. Use it to:

1. **State the current phase** — name, status (complete / in-progress / blocked)
2. **Note the active environment** — database name if one is set, or "none"
3. **Call out outstanding items** — uncommitted work, pending approvals, anything that needs resolution before new work begins
4. **Mention any missing INDEX files** (only if the First-Run Check above flagged any) and offer to generate them
5. **Ask what we are doing today** — do not start any work until the user responds

## Format

Keep it tight. Three to five sentences covering the above, then the question. No headers, no bullet lists in your response — just a clear briefing followed by "What are we working on today?"

## What Not To Do

- Do not begin implementing anything before the user responds
- Do not ask clarifying questions about the status doc — summarize what you see and ask what to do
- Do not load other skills until the user tells you what we're working on

## Reference

- Status document: `DEVELOPMENT_STATUS.md`
- Project root: `{{project_root}}`
