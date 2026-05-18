# Claude Controls — Install Guide

## For the Agent

This document guides you through installing Claude Controls on a project. Read it fully before asking any questions. Then interview the user using the questions below, confirm all answers, write `project.config.json`, copy framework files, and verify the install.

Do not start until the user says "install claude-controls" or equivalent.

---

## Step 1: Interview

Ask the user these questions in a single message. Group them visually. Wait for all answers before proceeding.

---

**Project**
1. What is the project name? (used in log files and skill headers)
2. What is the project root path? (absolute path, e.g. `C:/MyProject`)

**Database**
3. What database server type are you using? (SQL Server / PostgreSQL / MySQL / SQLite / None)
4. If applicable — host/server name, port, database name, and auth method (Windows trusted auth, or username + password)?
5. What are the production database name(s) or patterns to block? (e.g. `MyApp`, `MyAppDev`, `MyAppUAT`)
6. What pattern do test/ephemeral databases follow? (e.g. `MyApp_Test_*`)

**Code Structure**
7. Which paths should be hard-blocked from editing? (Claude can never write here — these are your production/committed code paths, e.g. `app/src/`, `sql/migrations/`)
8. Which paths should be approval-gated? (Claude can write here after explicit approval — typically your scratch/dev workspace)

**Documentation**
9. Do you have an existing status document? If yes, what is its path. If no, we will generate one from the boilerplate template.
10. Which files must be staged before committing production code? (e.g. `CHANGELOG.md`, `docs/DEVELOPMENT_STATUS.md`)

**Session**
11. How many lines of the status document should load at session start? (default: 150)

---

## Step 2: Confirm

Repeat all answers back to the user in a single formatted block. Ask them to confirm before proceeding. Example:

```
Here's what I'll configure:

Project: MyProject — C:/MyProject
Database: SQL Server, localhost, MyProject, trusted auth
  Blocked DB patterns: MyProject, MyProjectDev, MyProjectUAT
  Test DB pattern: MyProject_Test_*
Hard-blocked paths: app/src/, sql/migrations/
Approval-gated paths: scratch/app/src/, scratch/sql/migrations/
Status doc: docs/DEVELOPMENT_STATUS.md (existing)
Required on commit: CHANGELOG.md, docs/DEVELOPMENT_STATUS.md
Status lines at session start: 150

Confirm? (yes / change X)
```

---

## Step 3: Generate project.config.json

Write `project.config.json` to the project root using this schema. Fill in all values from the interview.

```json
{
  "project": {
    "name": "{{project_name}}",
    "root": "{{project_root}}"
  },
  "database": {
    "type": "{{db_type}}",
    "host": "{{db_host}}",
    "port": {{db_port}},
    "name": "{{db_name}}",
    "auth": "{{db_auth}}",
    "username": "{{db_username_or_null}}",
    "production_patterns": ["{{pattern1}}", "{{pattern2}}"],
    "test_patterns": ["{{test_pattern}}"]
  },
  "paths": {
    "hard_block": ["{{path1}}", "{{path2}}"],
    "approval_gate": ["{{path3}}", "{{path4}}"],
    "status_doc": "{{status_doc_path}}"
  },
  "commit": {
    "required_staged": ["{{doc1}}", "{{doc2}}"]
  },
  "session": {
    "status_lines": {{status_lines}}
  }
}
```

If db_type is "none", set host/port/name/auth/username/production_patterns/test_patterns to null or empty.

---

## Step 4: Status Document

**If the user has an existing status doc:** confirm the path resolves and continue.

**If the user does not have a status doc:**
1. Copy `claude-controls/framework/templates/DEVELOPMENT_STATUS.md` to the path they specify (or `docs/DEVELOPMENT_STATUS.md` by default)
2. Ask: "Do you also want me to generate a starter `DEVELOPMENT_STRATEGY.md`?" If yes, copy `claude-controls/framework/templates/DEVELOPMENT_STRATEGY.md` to `docs/DEVELOPMENT_STRATEGY.md`.
3. Tell the user: "Fill in the Current Work Environment and Current Phase Status sections of `DEVELOPMENT_STATUS.md` before your first session."

---

## Step 5: Copy Framework Files

Copy the following to the project's `.claude/` directory:

```
framework/hooks/                 → .claude/hooks/
framework/skills/                → .claude/skills/
framework/references/            → .claude/references/
framework/templates/             → .claude/templates/
framework/settings_template.json → .claude/settings.local.json
```

If `.claude/` does not exist, create it. If any destination files already exist, ask the user before overwriting.

---

## Step 6: Fill Skill Placeholders

Each skill in `.claude/skills/` contains `{{placeholders}}`. Replace them using values from `project.config.json`:

| Placeholder | Value |
|-------------|-------|
| `{{project_name}}` | project.name |
| `{{project_root}}` | project.root |
| `{{hard_block_paths}}` | paths.hard_block (comma-separated) |
| `{{required_staged}}` | commit.required_staged (comma-separated) |

---

## Step 7: Verify

Run through this checklist and confirm each item with the user:

- [ ] `project.config.json` exists at project root with all fields populated
- [ ] `.claude/hooks/` contains 7 hook files
- [ ] `.claude/skills/` contains 5 skill folders, each with SKILL.md
- [ ] `.claude/references/` folder structure exists (may be empty initially)
- [ ] `.claude/settings.local.json` exists with correct hook wiring
- [ ] Status document exists and is readable
- [ ] No `{{placeholder}}` strings remaining in any skill file

---

## Step 8: Populate References (Optional but Recommended)

The reference library starts empty. For the install to be fully useful, reference docs should be populated. Tell the user:

"The reference library at `.claude/references/` is ready but empty. I can help populate it by pulling from your existing documentation. Would you like to do that now, or come back to it?"

If yes, see ARCHITECTURE.md — Reference Library section for what goes where.

---

## Notes for the Agent

- Never write `project.config.json` with placeholder values — only write it with real answers
- If the user is unsure about a path, check whether it exists before accepting it
- The install is idempotent — safe to re-run if something goes wrong
- Keep `project.config.json` out of git (add to .gitignore) if it contains credentials
