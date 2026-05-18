---
name: pre-work
description: {{project_name}} pre-work checklist. Use before starting any implementation work — new phase, feature, bug fix, or database change. Ensures the environment is set up, strategy and status docs are updated, and approval to proceed is obtained before writing any code.
---

# Pre-Work — {{project_name}}

## When This Applies

Any time the user says "let's start", "begin", "implement", "build", or describes a new piece of work to do.

## Checklist — Complete In Order

**1. Clarify requirements**
- Read and confirm you understand what is being asked
- Identify any ambiguities and resolve them with the user before proceeding
- Do not assume — ask if unclear

**2. Update DEVELOPMENT_STRATEGY.md**
- Confirm the planned approach aligns with the project strategy
- If this is a new phase or feature, add it with approach and rationale
- See `DEVELOPMENT_STATUS.md` for current state

**3. Scaffold DEVELOPMENT_STATUS.md**
- Add a task checklist for this work
- Each task should be a discrete, completable step
- Update "Current Work Environment" section with the active phase name

**4. Set up environment**
- Check `project.config.json` — if `database.type` is `"none"`, skip this step
- Otherwise: create a new ephemeral test database, record its name in `DEVELOPMENT_STATUS.md` under "Current Work Environment", and confirm you are not working in a production database

**5. Get approval to proceed**
- For complex sub-phases (MEDIUM or HIGH complexity), create `implementation_plan.md` in the phase folder using `.claude/templates/implementation_plan.md` and present it for review
- For simple sub-phases, a conversational summary is sufficient
- Wait for explicit approval before writing any code or SQL

## What Not To Do

- Do not skip straight to implementation
- Do not work in production paths ({{hard_block_paths}})
- Do not create the ephemeral environment and forget to document its name

## Reference

- See `references/workflow/` for environment setup and approval gate procedures
- See `references/standards/` for coding conventions
