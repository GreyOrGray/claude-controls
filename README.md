# Claude Controls

A reusable Claude Code control system: hooks, skills, and a reference library that work together to give Claude consistent, project-aware behavior without bloating context.

**Installs per-project.** Each project gets its own `<project-root>/.claude/` with its own hooks, skills, references, and `project.config.json`. No global state, no cross-project interference.

## What It Solves

- Claude doesn't read your giant CLAUDE.md reliably — it skips sections, loses context between sessions
- Skills don't auto-trigger without hooks pushing them
- Nothing enforces workflow rules (promotion gates, commit requirements, DB protection) automatically

## How It Works

Three layers:

**Hooks** handle lifecycle events — session start, pre-tool-use, post-tool-use, pre-compact. They inject context, enforce rules, and log activity automatically.

**Skills** deliver instructions progressively. Only the trigger description is always in context. Full instructions load when relevant. Reference docs load only when a skill needs them.

**Reference Library** is curated documentation organized by topic. Skills pull from it on demand instead of everything being dumped into context at once.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

## Install

Run the install on any project:

```
Read claude-controls/INSTALL.md and set up claude-controls for this project.
```

The agent reads INSTALL.md, interviews you for ~10 values, generates `project.config.json`, copies framework files, and wires everything up.

## Contents

```
framework/          Portable hooks, skills, references, and templates
ARCHITECTURE.md     Full system design
INSTALL.md          Agent-guided install guide
README.md           This file
```

## Porting to a New Project

Repeat for each project that should have Claude Controls. The install is fully isolated — installing in Project B does not touch Project A.

1. Copy the `claude-controls/` folder to the new project root (or clone this repo there)
2. Tell the agent: "Read claude-controls/INSTALL.md and set up claude-controls for this project"
3. Answer the interview questions
4. Populate `<project-root>/.claude/references/` from your existing docs
