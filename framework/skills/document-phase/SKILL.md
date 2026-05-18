---
name: document-phase
description: {{project_name}} post-implementation documentation. Use after completing implementation and testing, before presenting results to the stakeholder. Verifies all documentation is updated and the work is ready for review and promotion approval.
---

# Document Phase — {{project_name}}

## When This Applies

Implementation is complete, tests have been run, and you are about to present results to the project owner for approval.

## Checklist — Complete In Order

**1. Update working_implementation_plan.md**
- Add a session entry dated today (newest at top)
- Document: what was built, test commands run, results, decisions made, bugs found and fixed
- File: `docs/phases/phase_X_Y/working_implementation_plan.md`

**2. Update phase README**
- Mark completed sub-phases as ✅ COMPLETE
- Add test results summary
- Note any scope that was deferred
- File: `docs/phases/phase_X_Y/README.md`

**3. Update DEVELOPMENT_STATUS.md**
- Check off completed tasks in the phase checklist
- Update "Current Work Environment" if the database changed
- Note any outstanding items

**4. Update CHANGELOG**
- Add an entry under the current date/version
- Summarize what was built, not how
- Reference the phase number

**5. Prepare results summary for project owner**
Present a concise summary covering:
- What was built (which sub-phases are complete)
- Test results (what was verified, key numbers)
- What was deferred (scope left for later)
- Promotion recommendation (promote now / defer / address gaps first)
- Specific questions requiring direction

**6. Wait for approval**
- Do not promote code or commit until the project owner approves
- Do not move to the next phase until this phase is signed off

## On Full Phase Completion

When the project owner approves and the phase is fully complete, sync all 4 documents:

1. **DEVELOPMENT_STRATEGY.md** — Move phase from "In Progress" to "Completed". Add lessons learned.
2. **DEVELOPMENT_STATUS.md** — Move phase to "Recently Completed". Reset "Current Work Environment".
3. **docs/phases/phase_X_Y/README.md** — Mark all sub-phases complete. Add final summary.
4. **docs/phases/phase_X_Y/working_implementation_plan.md** — Add a final session entry marking the phase closed.

## What Not To Do

- Do not present results without updating the documentation first
- Do not commit before getting approval
- Do not mark a phase complete if tests were not run
- Do not skip the 4-document sync on full phase completion

## Reference

- See `references/workflow/` for the promotion and approval process
- See `references/standards/` for documentation conventions
