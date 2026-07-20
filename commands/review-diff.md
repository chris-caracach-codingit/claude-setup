---
description: Open every file changed on the current branch as buffers in a single nvim session.
---

Open the files changed on the current branch in one nvim instance for review.

## Steps

1. Collect changed files (deduplicated, relative to the repo root):
   - Branch changes vs main: `git diff --name-only --diff-filter=d $(git merge-base main HEAD)`
   - Plus uncommitted changes: `git diff --name-only --diff-filter=d HEAD`
   - Skip deleted files. If the list is empty, say so and stop.
2. Open all files as buffers in a single nvim session:
   - If inside tmux (`$TMUX` is set): `tmux new-window -c <repo-root> "nvim <files...>"` — one nvim, one buffer per file, in a new tmux window.
   - Otherwise: print the ready-to-run line and tell the user to execute it with the `!` prefix: `! nvim <files...>`
3. Print the list of files that were opened, one per line. Nothing else — no analysis, no summaries.

## Guardrails

- Never launch nvim directly from the Bash tool without tmux — it has no TTY there.
- Read-only with respect to git: no staging, committing, or checkout.
- Quote file paths when building the nvim command.

## Input

$ARGUMENTS — optional base ref to diff against instead of main (e.g. `develop`).
