# Team conventions

How Christian works, distilled into a few convention docs. These are drop-in Claude Code memory files — copy the ones you want into your own `~/.claude/projects/<project>/memory/` (or point Claude at this folder). Personal, reference and live-ticket memories are intentionally excluded.

- [memory-hygiene.md](memory-hygiene.md) — How memory, notes and wiki stay in order: compact, remove, keep; status in one place; close-out when a ticket is done
- [execution-guardrails.md](execution-guardrails.md) — What Claude must not run or touch: commands, servers, DB, deps, browser, GitHub workflows, credentials, AWS read-only, demo and QA accounts
- [working-style.md](working-style.md) — How to write and talk: plain and brief, no em dashes or AI-slop phrasing, verify load-bearing claims
- [messaging.md](messaging.md) — Slack, GitHub, Linear and Confluence messages are drafted in chat, never sent; Slack drafts carry no links or ticket ids
- [docs.md](docs.md) — Docs are timeless .md drafts (never web artifacts): what it is and how it works, roles not names, plans declare
- [wiki-and-notes.md](wiki-and-notes.md) — Wiki page granularity and write cadence; working notes go outside the repo
- [git.md](git.md) — Commit messages and timing, staged-list check, forward-only history, branch naming and checks, scratch worktrees, stacked PRs
- [pull-requests.md](pull-requests.md) — PR title and body format, when to skip QA, plain voice, review-comment tone, GitHub etiquette
- [code-style.md](code-style.md) — React/TSX idioms, Typography, rem spacing, PDF pt from Figma, no comments or ticket refs, TEMP-WRAPPER markers, backend mapping
- [linear-tickets.md](linear-tickets.md) — Ticket conventions: current cycle, problem-only plain descriptions, dated changes, short comments, PR-link status reset
- [qa.md](qa.md) — Shaping work so the QA team can verify it, and the High/Medium/Low risk tiers with their Linear labels
- [feedback_renovate_cve_workflow.md](feedback_renovate_cve_workflow.md) — Steps for "[Security] Bump X" tickets: severity triage, major-vs-patch check, PR takeover, QA handoff
- [feedback_sentry_to_linear_workflow.md](feedback_sentry_to_linear_workflow.md) — Steps for turning a Sentry alert into a Linear ticket: ticket shape, acceptance criteria, back-link, fix PR
