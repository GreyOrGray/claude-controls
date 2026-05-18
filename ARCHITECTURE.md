# Claude Controls — Architecture

## What This Is

A reusable Claude Code control system consisting of three layers:

1. **Hooks** — lifecycle event handlers that enforce workflow rules and inject context
2. **Skills** — modular instruction sets that load progressively based on task context
3. **Reference Library** — curated documentation that skills pull from on demand

Together they replace the pattern of one large CLAUDE.md that dumps everything into context on every session.

---

## The Three Layers

### Layer 1: Hooks

Hooks intercept Claude Code lifecycle events to enforce rules and inject context automatically.

| Hook | Lifecycle Event | Matcher | Purpose |
|------|----------------|---------|---------|
| `session_init.py` | `SessionStart` | (none) | Load status doc context at session open |
| `bash_guard.py` | `PreToolUse` | `Bash` | Block destructive commands, protect production DBs |
| `file_guard.py` | `PreToolUse` | `Write\|Edit` | Three-tier path protection (hard block / approval gate / allow) |
| `commit_guard.py` | `PreToolUse` | `Bash` | Require key docs staged before committing production code |
| `session_log.py` | `PostToolUse` | (none) | Async audit log of every tool call |
| `precompact.py` | `PreCompact` | (none) | Preserve critical context before conversation compaction |

**Hook communication:**
- Block a tool: output `{"decision": "block", "reason": "..."}` to stdout, exit 0
- Allow a tool: exit 0 with no output
- Async (non-blocking): set `"async": true` in settings — used for session_log.py

**Configuration:** all hooks read `project.config.json` at runtime. No hardcoded values.

---

### Layer 2: Skills

Skills are modular instruction sets in SKILL.md format. They use three-level progressive disclosure:

1. **YAML frontmatter** — always in Claude's system prompt (tiny — just name + trigger description)
2. **SKILL.md body** — loads when Claude determines the skill is relevant
3. **references/** — linked docs that load only when the skill needs them

| Skill | Triggers When |
|-------|--------------|
| `session-start` | Fired by SessionStart hook at every session open |
| `pre-work` | Starting a new phase, feature, or bug fix |
| `commit-ready` | About to run git commit |
| `pre-phase` | Starting a brand new major phase |
| `document-phase` | Implementation complete, before presenting to stakeholder |

**Activation:** a `UserPromptSubmit` hook prepends a mandatory skill evaluation step to every prompt, achieving ~84% reliable activation (vs ~20% without the hook).

**Skills live in:** `.claude/skills/` (installed from `framework/skills/`)

---

### Layer 3: Reference Library

Curated documentation organized by topic. Skills link to specific reference folders — Claude loads only what's relevant to the current task.

```
references/
  workflow/          How to do the work (promotion process, DB workflow, approval gates)
  standards/         How to write the code (SQL conventions, Python patterns, event logging)
  architecture/      How the system is built (modules, schema, design patterns)
  business-rules/    Domain logic (simulation rules, fund structure, business constraints)
```

**Key principle:** reference docs are concise and focused. One topic per file. If a doc exceeds ~200 lines, split it.

---

## How the Layers Work Together

```
Session opens
  └── SessionStart hook fires
        └── session_init.py reads N lines of status doc
              └── Injects context: current phase, active DB, outstanding items
                    └── Claude gives session summary, asks what we're doing

User submits prompt
  └── UserPromptSubmit hook fires
        └── Forced eval: Claude evaluates each skill YES/NO
              └── Relevant skills load (e.g. pre-work skill activates)
                    └── Skill body loads workflow/ and standards/ references
                          └── Claude follows correct workflow for the task

User asks Claude to edit a file
  └── PreToolUse hook fires (file_guard.py)
        └── Checks path against project.config.json protection rules
              └── Hard block / approval gate / allow

User asks Claude to run a bash command
  └── PreToolUse hook fires (bash_guard.py)
        └── Checks against blocked patterns and protected DB names

Claude finishes each tool call
  └── PostToolUse hook fires (session_log.py, async)
        └── Appends JSONL entry to daily audit log

Context approaches limit
  └── PreCompact hook fires (precompact.py)
        └── Writes context snapshot before compaction
```

---

## Configuration: project.config.json

All project-specific values live in one file. Hooks and skills read this at runtime.

```json
{
  "project": {
    "name": "...",
    "root": "..."
  },
  "database": {
    "type": "sqlserver | postgres | mysql | sqlite | none",
    "host": "...",
    "port": ...,
    "name": "...",
    "auth": "trusted | password",
    "username": "...",
    "production_patterns": ["..."],
    "test_patterns": ["..."]
  },
  "paths": {
    "hard_block": ["..."],
    "approval_gate": ["..."],
    "status_doc": "..."
  },
  "commit": {
    "required_staged": ["..."]
  },
  "session": {
    "status_lines": 150
  }
}
```

---

## File Layout (Installed)

After running install, the **project's** `.claude/` directory looks like the tree below. This is the project-local `.claude/` (e.g. `C:/MyProject/.claude/`), **not** the user-global `~/.claude/`. Each project that installs claude-controls gets its own independent copy — installing in a second project does not affect the first.

```
<project-root>/
  .claude/
    hooks/
      session_init.py
      bash_guard.py
      file_guard.py
      commit_guard.py
      session_log.py
      precompact.py
      skill_eval.py
    skills/
      session-start/SKILL.md
      pre-work/SKILL.md
      commit-ready/SKILL.md
      pre-phase/SKILL.md
      document-phase/SKILL.md
    references/
      workflow/
      standards/
      architecture/
      business-rules/
    templates/
      DEVELOPMENT_STATUS.md
      DEVELOPMENT_STRATEGY.md
      implementation_plan.md
      phase_README.md
      working_implementation_plan.md
    settings.local.json        ← hook wiring (project-scoped)
  project.config.json          ← project-specific values (at project root)
```

---

## Design Principles

**Config-driven, not hardcoded.** Every project-specific value (paths, DB names, doc locations) lives in `project.config.json`. The framework files never need editing.

**Progressive disclosure.** Skills load only when relevant. References load only when a skill needs them. Nothing is dumped into context speculatively.

**Fail safe.** Hooks that can't read config exit cleanly (no block). Security hooks (bash_guard, file_guard) default to blocking on config errors.

**Async for logging.** session_log.py runs async — it never slows down a tool call.

**One session doc.** The status document is the single source of truth for session orientation. If a project doesn't have one, the template generates a working starter.
