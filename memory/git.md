---
name: git
description: Git conventions — commit messages, history discipline, branch naming
metadata:
  type: feedback
---

# Git conventions

## Commit messages

- **Single-line subject only.** No body paragraph, no bullet list. Detail belongs in the PR description, not the commit. If nuance needs capturing, make multiple commits instead of a longer message.
- **Plain subject, no prefixes.** No `[ENG-1234]`, no `feat:`. Ticket IDs live in PR titles, not commits. e.g. `Add retry button to TinyAI error state`, not `[ENG-4424]: TinyAI error retry button`.
- **No trailers.** No `Co-Authored-By`, no "Generated with…" footer.

## History discipline

- **Forward-only.** To change something already committed (especially if pushed), edit forward and add a new commit. Do not `git revert`, `git rebase -i`, `git rebase --onto`, or `--amend` a pushed tip. Don't propose rebase/revert as the "clean" path — a noisier linear history is preferred.
- **Minimal git noise.** Commit and stop. Don't chain exploratory `git diff` / `log` / `merge-base` checks around a commit unless something's actually wrong. Surface one fact, not an investigation.

## Branches

- **Naming:** `<username>/ENG-XXXX` (e.g. `christian/ENG-4465`). Ignore Linear's auto-generated `gitBranchName` slug — too verbose.
- **Create from the stated base.** When told "work on <ticket>, branch from <base>", explicitly create `<username>/ENG-<ticket>` from that base. Don't assume the currently checked-out branch is right — check `git branch --show-current` first, and verify the base actually contains the code you expect (sibling branches diverge).
- **Verify the working dir before editing.** Confirm the main repo is checked out on the target branch before making edits — not a leftover agent worktree. `git worktree list` + `git branch --show-current`.
