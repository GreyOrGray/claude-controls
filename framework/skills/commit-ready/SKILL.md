---
name: commit-ready
description: {{project_name}} pre-commit verification. Use before running git commit to ensure all required documentation is staged, no scratch files are included, and the commit has explicit approval. Use when the user says "commit", "let's commit", or "ready to commit".
---

# Commit Ready — {{project_name}}

## Before Running git commit

Work through this checklist and confirm each item with the user before committing.

**1. Verify staged files**
- Run `git diff --cached --name-only` to see what is staged
- Confirm no scratch or temporary files are included
- Confirm no credential files (.env, .key, .pem) are staged

**2. Verify required documentation is staged**
The following files must be staged when committing production code:
{{required_staged}}

**3. Verify production code is promoted**
- Code in {{hard_block_paths}} must have been explicitly promoted by the project owner
- Do not commit work that is still in scratch/dev paths

**4. Verify CHANGELOG is updated**
- CHANGELOG.md must reflect the changes being committed
- Entry should be under the correct version/date heading

**5. Get explicit commit approval**
- Present the full list of staged files to the user
- State the proposed commit message
- Wait for "yes" or explicit approval before running git commit
- Never commit without this approval, even for documentation-only changes

## Commit Message Format

```
[Phase X.Y]: Brief description of what was built

- Key change 1
- Key change 2
- Key change 3

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## What Not To Do

- Do not commit without explicit user approval
- Do not use `--no-verify` to bypass hooks
- Do not amend a previous commit — create a new one

## Reference

- See `references/workflow/` for the full promotion and commit process
