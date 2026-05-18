---
name: pre-phase
description: {{project_name}} new phase initialization. Use when starting a brand new major phase of development (not a sub-task or bug fix). Sets up phase documentation folder, updates strategy and status documents, and confirms the approach before any work begins.
---

# Pre-Phase — {{project_name}}

## When This Applies

Starting a new numbered phase (e.g. Phase 3.6, Phase 4.1) — not a sub-task within an existing phase.

## Checklist — Complete In Order

**1. Confirm phase scope**
- What is the phase name and number?
- What is the business purpose — why does this phase exist?
- What are the sub-phases (e.g. 3.6.1, 3.6.2)?
- What are the success criteria?

**2. Create phase documentation folder**
Create the folder `docs/phases/phase_X_Y/` with:
- `README.md` — copy from `.claude/templates/phase_README.md`, fill in phase name, number, and scope
- `working_implementation_plan.md` — copy from `.claude/templates/working_implementation_plan.md`, fill in phase number and name
- `implementation_plan.md` — for complex phases (MEDIUM or HIGH complexity), copy from `.claude/templates/implementation_plan.md` and fill in the full plan before requesting approval. For simple phases, the approval summary in step 5 is sufficient.

**3. Update DEVELOPMENT_STRATEGY.md**
- Add the new phase with approach, rationale, and sub-phase breakdown
- Move it to "In Progress" status

**4. Scaffold DEVELOPMENT_STATUS.md**
- Add a detailed task checklist for all sub-phases
- Update "Current Work Environment" to reflect the active phase
- Update "Current Phase Status" section

**5. Get approval to proceed**
- Present the phase plan: scope, sub-phases, approach, success criteria
- Confirm the documentation is correct
- Wait for explicit approval before starting implementation

## What Not To Do

- Do not start implementation before the phase folder and docs exist
- Do not skip the DEVELOPMENT_STRATEGY.md and DEVELOPMENT_STATUS.md updates
- Do not create phase folders outside of `docs/phases/`

## Reference

- See `references/workflow/` for the complete phase documentation process
