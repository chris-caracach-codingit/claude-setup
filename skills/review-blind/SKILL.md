---
name: review-blind
description: Review the current branch by reverse-engineering its ticket. A fresh claude process with no repo, memory, tools or MCP sees only the sanitized diff and writes the ticket it implies; then this session compares that ticket with the real one. Use when the user says "/review-blind", "blind review", or "reverse-engineer the ticket". Reports requirement inconsistencies, bugs and improvements; every blind finding is verified against the repo before it is reported.
---

# Blind review

Two stages. Stage 1 is blind and runs in a separate process. Stage 2 runs here, with full context.

## Input

`$ARGUMENTS` may contain:

- A ticket id (`ENG-1234`) or pasted ticket text. Without one, run stage 1 only and ask the user to paste the ticket.
- `--base <ref>` to diff against something other than `main`.
- `--with-docs` to include `*.md` and `.env.example` in the diff. Default is code only, because docs carry the author's stated intent and that is what the experiment hides.

## Stage 1: blind ticket

Run the script from the repo root. Do not read the diff yourself before stage 1 finishes; it does not matter for purity (the blind process is separate) but it keeps your stage 2 comparison honest about what came from where.

```sh
~/.claude/skills/review-blind/run.sh [--base main] [--with-docs]   # add --dry-run to list the files first
```

It prints the path of `blind-ticket.md`. Read it. Do not edit it.

## Stage 2: compare and verify

Fetch the real ticket (Linear `get_issue` for an id, or the pasted text). Now use the repo freely.

**Requirement inconsistencies**

1. **In the real ticket, not in the blind one.** Scope the code does not visibly deliver. Each item: what the ticket asks, and why the diff does not show it.
2. **In the blind one, not in the real ticket.** Scope creep or undocumented decisions. Each item: file path and what it does.
3. **Acceptance criteria that differ.** The ticket's definition of done versus what the code checks.

**Bugs and improvements**

4. Take every item in the blind "Bugs" and "Improvements" lists and verify it against the repo: read the surrounding code, and where a claim is about runtime behavior, run it (the workspace's tests, type-check, a one-line smoke call). Report each as confirmed, refuted, or unverifiable, with the evidence. Drop refuted ones from the final list but say how many you dropped.
5. Add any bug or improvement you find yourself while verifying. Mark these as "from this session".
6. Carry over "Unjustified", "Undelivered" and "Questions", trimmed to what still stands.

**Verdict**: one line on whether the diff matches its ticket, then what should change: ticket, code, or both. Most severe item first.

## Stage 3: handoff

This session reviews; it never edits the code. The session that wrote the branch owns every change. When the verdict has at least one actionable item, write a handoff for that session at `~/review-handoffs/<repo-name>/<branch-with-slashes-as-dashes>.md` (outside any repo; create the folders if missing) and print the path. If nothing is actionable, say so and write no file.

The handoff is a work order, not the review. Format:

```md
# Review handoff: <branch>

Ticket: <id or "pasted">   Base: <ref>   Reviewed: <date>   Repo: <absolute path>

## Fix (confirmed bugs, most severe first)
- `path:line` what is wrong, how it was confirmed, what the fix should achieve. No patch.

## Improve (verified improvements)
- `path:line` what to change and why.

## Align ticket and code (requirement inconsistencies)
- Which side should move: ticket text, code, or acceptance criteria. One line each.

## Decide (questions only the author can answer)
- ...

## Not actionable (dropped or refuted, for the record)
- ...
```

Each item states the outcome wanted, not the diff to apply; the author session chooses the implementation. The author session starts from that file: read it, do the items in order, and reply in its own chat with what it fixed, what it skipped and why.

## Rules

- Never post anything and never edit code. The comparison goes in chat; the actions go in the handoff file.
- Say explicitly which findings came from the blind pass and which from this session.
- If the blind ticket names something only the repo could have told it (a branch name, a ticket id, a file not in the diff), the isolation leaked; report that first and stop.
