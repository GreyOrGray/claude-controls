# Reference Library

This folder contains curated documentation that skills pull from on demand. It is intentionally empty after install — populate it from your existing project docs.

## Structure

```
references/
  workflow/         How to do the work
  standards/        How to write the code
  architecture/     How the system is built
  business-rules/   Domain logic and constraints
```

## What Goes Where

### workflow/
Day-to-day process documentation. Examples:
- `promotion-process.md` — how code moves from dev to production
- `approval-gates.md` — what requires sign-off before proceeding
- `database-workflow.md` — how to create/manage databases
- `commit-workflow.md` — what to check before committing
- `environment-setup.md` — how to set up a dev environment

### standards/
Code and documentation conventions. Examples:
- `sql-conventions.md` — naming rules, constraint patterns, migration format
- `python-conventions.md` — type hints, error handling, module size limits
- `event-logging.md` — audit trail patterns, event taxonomy
- `testing-standards.md` — test structure, coverage expectations

### architecture/
How the system is built. Examples:
- `module-inventory.md` — what each module does and its dependencies
- `database-schema.md` — tables, primary keys, relationships
- `data-flow.md` — how data moves through the system
- `design-patterns.md` — patterns used and why

### business-rules/
Domain logic that Claude needs to apply correctly. Examples:
- `calculation-rules.md` — formulas, rates, rounding behavior
- `workflow-rules.md` — state machines, valid transitions
- `constraint-rules.md` — business invariants that must hold

## INDEX.md per category

Each category folder should have an `INDEX.md` — a one-screen overview of what's in *this project's* category, with links to the canonical docs (in this folder or elsewhere in the repo). It's the entry point a skill loads when it needs context about that category, before pulling in any specific reference file.

`INDEX.md` is **generated per project, not copied from a template.** Every project has different architecture, business rules, and conventions, so a shared template would be either too generic to be useful or so opinionated it fights the project's reality.

**How it gets populated:** the `session-start` skill checks for these files at every session open. The first time it runs in a new project, it detects the missing files, mentions them in the briefing, and offers to generate them. If you accept, it reads each category's README for shape guidance, scans the repo for relevant artifacts (modules, schemas, existing docs), drafts an `INDEX.md`, and asks for confirmation before writing. The offer repeats next session until the files exist; subsequent updates happen the same way — through a skill, with user confirmation, not by hand-editing.

**Shape:**
- 2–4 sentence summary of what this category covers in *this* project
- A primary-documents table linking to canonical sources (don't duplicate — link)
- Inline notes only for things that aren't documented elsewhere yet

See each category's `README.md` for what its `INDEX.md` should specifically cover.

## Guidelines

- **One topic per file.** If a doc exceeds ~200 lines, split it.
- **Concise over comprehensive.** These are reference docs, not tutorials.
- **Link from skills, don't inline.** Skills reference these files; they don't copy the content.
- **Keep them current.** A stale reference is worse than none.
