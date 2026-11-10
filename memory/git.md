---
name: git
description: "Git conventions: commit messages and timing, reading the staged list, forward-only history, branch naming and checks, scratch worktrees, stacked PRs"
metadata: 
  type: feedback
---

# Git conventions

## Commit messages

- **Single-line subject only.** No body paragraph, no bullet list. Detail belongs in the PR description, not the commit. If nuance needs capturing, make multiple commits instead of a longer message.
- **Plain subject, no prefixes.** No `[ENG-1234]`, no `feat:`. Ticket IDs live in PR titles, not commits. e.g. `Add retry button to TinyAI error state`, not `[ENG-4424]: TinyAI error retry button`.
- **No trailers.** No `Co-Authored-By`, no "Generated with…" footer.

## Commit timing

- **Don't commit a fix until the user confirms it works.** When a change can only be verified by the user (on-device testing, eyeballing UI), leave it in the working tree and wait for their confirmation before committing. Applies even mid-flow when earlier commits in the session were welcome.

## Before committing: read the staged file list

Never `git add <dir>` and commit without reading the staged file list. Tracked generated files (Playwright `playwright-report/index.html`, test-results, build output) get rewritten by local runs and can carry secrets: on 2026-10-29 (ENG-5204) a committed report held the automation account password from a UI login `Fill` step and had to be force-pushed away and rotated.
**Why:** the leak reached origin before anyone saw it.
**How to apply:** `git status --short` after staging; unstage anything generated; if a generated file is tracked, untrack it (`git rm --cached`) in the same change.

## Splitting commits

- **No silent temp-revert edits.** Splitting one file's changes into multiple commits by temporarily reverting hunks looks like new/destructive work and alarms the user. Prefer one commit per file-touching batch; if a split genuinely matters, say what the temporary edit is for before doing it.

## History discipline

- **Forward-only.** To change something already committed (especially if pushed), edit forward and add a new commit. Do not `git revert`, `git rebase -i`, `git rebase --onto`, or `--amend` a pushed tip. Don't propose rebase/revert as the "clean" path — a noisier linear history is preferred.
- **Minimal git noise.** Commit and stop. Don't chain exploratory `git diff` / `log` / `merge-base` checks around a commit unless something's actually wrong. Surface one fact, not an investigation.

## Branches

- **Naming:** `<username>/ENG-XXXX` (e.g. `christian/ENG-4465`). Ignore Linear's auto-generated `gitBranchName` slug — too verbose.
- **Create from the stated base.** When told "work on <ticket>, branch from <base>", explicitly create `<username>/ENG-<ticket>` from that base. Don't assume the currently checked-out branch is right — check `git branch --show-current` first, and verify the base actually contains the code you expect (sibling branches diverge).
- **Check the branch before every git operation, not just before editing.** Chris switches branches between sessions; on 2026-10-14 a `git merge origin/main` meant for ENG-5100 landed on ENG-5110 because the checkout had moved (undone via reflog before pushing). `git branch --show-current` first, every time, even when the previous turn was on the right branch.
- **Re-check the branch at the start of EVERY turn, before any file edit, not only before git ops.** 2026-10-15: a new session resumed ENG-5039 work while the checkout was on ENG-5138; the edit script only failed by luck (an assertion on file content). Chris: "Switch the branch!"
- **Verify the working dir before editing.** Confirm the main repo is checked out on the target branch before making edits — not a leftover agent worktree. `git worktree list` + `git branch --show-current`.
- **Never switch the user's main checkout to merge or repair another branch.** Do that work in a scratch worktree (`git worktree add`), so his checkout, working tree and running dev servers stay as he left them.

## Stacked PRs

Background and traps: wiki knowledge note `pr-preview-stacks-and-stacked-prs.md`.
- **One branch per ticket.** The ticket's PR targets main and is the QA environment. A migration goes in a child PR on `<ticket-branch>-migration` (singular), stacked into the ticket branch, reviewed alone, and merged into the parent on Chris's word. A child PR only deploys its delta against the sandbox API, so QA always happens on the parent.
- **Update a stacked branch by merging its base branch, never main.** Merging main straight into a child adds foreign commits and a criss-cross "dirty" state, and GitHub then skips the `pull_request` workflows (ENG-5039). Before each QA round, merge main into the parent (the PR that targets main), then the parent into each child; otherwise the preview DB, cloned from sandbox, hits migrations the branch lacks.
- **After pushing, check `gh pr view <n> --json mergeable`.** A CONFLICTING PR gets no CI and no preview, silently (ENG-4974).
- **After the parent is squash-merged, the child conflicts.** Before taking the child's side for a conflicted file, prove main's version equals the parent tip: `git diff origin/main <parent-tip> -- <file>` is empty.

## Split-for-review branches

- When one ticket's work is split into several PRs purely for review, name the branches `<username>/ENG-XXXX-part-1`, `-part-2`, … and keep every PR title under the same `[ENG-XXXX]` prefix, drafts (Chris, 2026-09-17, ENG-5018).
- Chris prefers reviewing the **final tree** split by path over commit-based splits: when later commits correct earlier ones (e.g. a rule-based pass then VQA overrides), rebuild each part as one commit from the end state so reviewers never see superseded values. The original branch stays as the history record.
