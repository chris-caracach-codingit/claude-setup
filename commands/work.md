---
description: Autonomous work loop. Reads my Todo tickets in the current cycle from Linear, triages which ones are simple enough for Claude to ship solo, and dispatches sub-agent workers to open PRs.
---

You are the orchestrator of an autonomous work loop. Your job is to triage the queue, dispatch workers, and aggregate their reports — not to do the work yourself.

## Triage

1. Pull the user's tickets in the "Todo" column from Linear: `mcp__linear__list_issues` with status "Todo", `assignee: "me"`, and the current cycle (`cycle: "current"` if supported, otherwise resolve the team's active cycle first). Do NOT pull the whole Todo column. Apply any additional filter from $ARGUMENTS (e.g. `priority:high`, `project:platform`).
2. For each ticket, read the full description (and comments if the description is thin) and score whether it is **simple enough for Claude to solve by itself**, on three dimensions:
   - **Effort points**: the ticket's estimate. ≤2 points is a good candidate; 3 is borderline; ≥5 (or unestimated with a large-sounding description) is not.
   - **Scope**: which apps/packages in the monorepo are involved. Single app = good candidate; two apps (e.g. backend + one portal) = borderline; three or more apps, infra/migrations, or third-party integrations = not a candidate.
   - **Clarity of requirements**: the ticket states concretely what should change and how to tell it's done (repro steps, acceptance criteria, before/after, screenshot or specific copy). Vague tickets ("improve X", "investigate Y", open product questions, missing designs) are not candidates, regardless of size.
3. Show the user a triage table: ticket → points → scope (apps) → clarity → verdict (`candidate` / `borderline` / `skip`) with a one-line reason each. The work queue is the `candidate` tickets; include `borderline` ones only if the user opts in.
4. Wait for confirmation of the queue unless $ARGUMENTS already contained a "go" / "yes" / "auto" signal (in `auto` mode, run `candidate` tickets only).

## Loop
1. For each task in the confirmed queue, in sequence:
   a. Spawn a `work-task-worker` sub-agent with `isolation: "worktree"` and a prompt containing the full ticket body + acceptance criteria + repo root.
   b. Wait for the worker's report.
   c. Print a 1-line ack: `[N/total] <ticket-id> → <status>: <summary>` + PR URL if any.
   d. On `blocked` or `failed`: do NOT halt; log it and continue.
2. Every 5 completed tasks: call `mcp__wiki__journal_save` (if wiki-mcp is installed) with a progress summary.
3. Stop conditions (any of):
   - Queue is empty.
   - 3 consecutive workers report `failed`.
   - User interrupts.
4. Final report: a markdown table of all tasks (ticket → status → PR URL → notes). Print to chat and save via `mcp__wiki__journal_save` if available.

## Guardrails

- Sequential workers only at v1. Do not parallelize.
- Do not call the worker's tools yourself. Your tools are: Linear read, Agent dispatch, journal_save, chat output.
- If a worker's report is malformed, treat the task as `failed` and continue.
- Never modify Linear ticket state from the orchestrator.
- Before each worker dispatch, check rough token usage. If you're past ~70% of a reasonable session budget, stop and ask the user before continuing.

## Input

$ARGUMENTS — optional. Examples:
- (empty) — triage my Todo tickets in the current cycle, ask before starting.
- `priority:high` — filter the Linear query before triage.
- `auto` — skip confirmation, run `candidate` tickets immediately.
- `auto priority:high` — both.
