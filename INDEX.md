# INDEX

Machine-readable catalog of this repo. Each row is one artifact: what it is, and
where the **equivalent lives in a user's own Claude Code setup** so it can be
compared directly. Paths under `~/.claude/` refer to the reader's machine.

This repo is **reference only** — nothing here is meant to be installed or run.
It documents one working setup so Claude can compare, analyze, and suggest.

## Hooks — `hooks/`

Shell scripts Claude Code runs on lifecycle events. Wiring lives in `settings/settings.json` under `hooks`.

| Path | Purpose | Reader's equivalent |
|------|---------|---------------------|
| `hooks/format-bash-command.sh` | Pretty-prints each Bash command before it runs (PreToolUse). Display only. | `~/.claude/settings.json` → `hooks.PreToolUse` (Bash) |
| `hooks/claude-pet.py` | Pet notifier: a pixel-art robot toast (GTK3, bottom-right, stacks, self-reflowing) that appears when Claude runs `git push`/`git commit`, `rm`, docker, DB (`bun db:*`, mysql, knex…), vercel, or sends a Slack message (PreToolUse, async, alert-only, never blocks). Shows only the matching command segment; `rm` targets and `in <dir>` are resolved to absolute paths, tracking `cd`. Falls back to `dunstify` without a display. | `~/.claude/settings.json` → `hooks.PreToolUse` (`Bash\|mcp__.*slack.*`) |
| `hooks/aws-readonly.py` | AWS CLI guard: blocks any `aws` call that is not a read (and any secrets/data read), and requires an explicit `--profile` (PreToolUse, `onFailure: block`). Can't parse heredocs with apostrophes; write such bodies to a file instead. | `~/.claude/settings.json` → `hooks.PreToolUse` (Bash) |
| `hooks/memory-size-check.sh` | Warns at session start when the project's memory index `MEMORY.md` passes 10 KB and suggests `/memory-compact` (SessionStart, adds context, never blocks). | `~/.claude/settings.json` → `hooks.SessionStart` |
| *(inline, no script)* | Attention marker: `Notification` touches `$XDG_RUNTIME_DIR/claude-attention/<session_id>`; `UserPromptSubmit`, `PostToolUse`, and `SessionEnd` remove it. A qtile status widget watches that directory and lights up when any session is waiting. Replaced an earlier `notify-idle.sh` that fired `dunstify` toasts. | `~/.claude/settings.json` → `hooks.Notification` / `.UserPromptSubmit` / `.PostToolUse` / `.SessionEnd` |

## Slash commands — `commands/`

| Path | Purpose | Reader's equivalent |
|------|---------|---------------------|
| `commands/post-it.md` | Write a short plain-words note about a problem and its fix, so it can be read aloud to a non-engineer teammate. Saves to `~/post-its/YYYY-MM-DD-<slug>.md`. | `~/.claude/commands/` |
| `commands/review-diff.md` | Open every file changed on the branch as buffers in one nvim session. | `~/.claude/commands/` |
| `commands/work.md` | Autonomous loop: triage current-cycle Linear tickets, dispatch workers to open PRs. | `~/.claude/commands/` |
| `vendor/wiki-mcp/commands/*.md` (15) | Wiki commands (journal, knowledge, projects, debug). Ship with the wiki-mcp server. | `~/.claude/commands/wiki/` |

## Agents — `agents/`

| Path | Purpose | Reader's equivalent |
|------|---------|---------------------|
| `agents/work-task-worker.md` | Single-task worker for `/work`: one ticket → one PR. Tool-scoped. | `~/.claude/agents/` |

## Skills — `skills/`

| Path | Purpose | Reader's equivalent |
|------|---------|---------------------|
| `skills/tiny-portals/SKILL.md` | Drive Tiny Health portals in a browser (Chrome DevTools MCP) to verify against sandbox data. Encodes ports, login/JWT flows, safety rules. | `~/.claude/skills/tiny-portals/` |
| `skills/tiny-portals/harvest-jwt.sh` | Helper the skill calls to harvest the PDF admin JWT. | — |
| `skills/tiny-portals/credentials.env.example` | Documents the sandbox credentials the skill expects (names only). Real file is external + untracked. | `~/prog/tiny-portals/credentials.env` |
| `skills/tiny-portals/ACCESS_RULES.template.md` | Documents the structure of the portal access-rules file the skill reads. | `~/prog/tiny-portals/ACCESS_RULES.md` |
| `skills/memory-compact/SKILL.md` | Memory cleanup: compact what isn't in use but is useful (lessons → wiki knowledge notes), remove what is useless, keep the rest in order. Dry run, then apply after approval. Pairs with `memory/memory-hygiene.md` and the SessionStart size hook. | `~/.claude/skills/memory-compact/` |
| `skills/memory-compact/inventory.sh` | Read-only inventory: each memory's type and size, live state of the PRs it mentions, index drift, dead paths, stray notes, disk leftovers. The memory path is this setup's; adjust for yours. | — |
| `skills/review-blind/SKILL.md` + `run.sh` | Blind review: a fresh `claude -p` with no repo, tools or memory sees only the sanitized diff and writes the ticket it implies; the session then compares it with the real ticket and verifies every finding. | `~/.claude/skills/review-blind/` |
| `skills/sentry-alert/SKILL.md` | Investigate a Sentry alert: check the findings log, triage the issues, optional read-only prod smoke via demo accounts, draft the Slack reply (never sent). | `~/.claude/skills/sentry-alert/` |

## MCP servers — `mcp/`

| Path | Purpose | Reader's equivalent |
|------|---------|---------------------|
| `mcp/servers.json` | The MCP servers Christian runs: linear, atlassian, sentry, chrome-devtools, wiki (local), tiny-health (local, project-scoped), obsidian-vault (optional). OAuth servers carry no secrets; obsidian key is a placeholder. | `claude mcp list`; `~/.claude.json` → `mcpServers` |

## Settings — `settings/`

| Path | Purpose | Reader's equivalent |
|------|---------|---------------------|
| `settings/settings.json` | Permission mode, model, effort, theme, enabled plugins, extra marketplaces, and hook wiring. Uses `$HOME` for portability. | `~/.claude/settings.json` |

## Conventions — `memory/`

Working conventions as drop-in Claude Code memory files. Prime material for "does my setup follow these?". Index: [`memory/MEMORY.md`](memory/MEMORY.md).

| Path | Covers | Reader's equivalent |
|------|--------|---------------------|
| `memory/memory-hygiene.md` | How memory, notes and wiki stay in order: compact, remove, keep; status in one place; close-out on ticket done | `~/.claude/CLAUDE.md` or `~/.claude/projects/<proj>/memory/` |
| `memory/execution-guardrails.md` | What Claude must not run or touch: commands, servers, DB, deps, browser, GitHub workflows, credentials, AWS read-only, demo and QA accounts | ″ |
| `memory/working-style.md` | Plain, brief communication; no em dashes or AI-slop phrasing; verify claims | ″ |
| `memory/messaging.md` | Slack/GitHub/Linear/Confluence messages drafted in chat, never sent; Slack drafts without links or ticket ids | ″ |
| `memory/docs.md` | Docs are timeless .md drafts: what it is and how it works, roles not names | ″ |
| `memory/wiki-and-notes.md` | Wiki page granularity and cadence; working notes outside the repo | ″ |
| `memory/git.md` | Commits, staged-list check, history discipline, branch naming, scratch worktrees, stacked PRs | ″ |
| `memory/pull-requests.md` | PR title, body, voice, GitHub etiquette | ″ |
| `memory/code-style.md` | React/TSX, Typography, CSS units, PDF pt from Figma, comments, backend mapping | ″ |
| `memory/linear-tickets.md` | Cycles, descriptions, dated changes, reading specs | ″ |
| `memory/qa.md` | Shaping work for the QA team, and the High/Medium/Low risk tiers | ″ |
| `memory/feedback_renovate_cve_workflow.md` | Steps for Renovate "[Security] Bump X" tickets | ″ |
| `memory/feedback_sentry_to_linear_workflow.md` | Steps for turning a Sentry alert into a Linear ticket and fix | ″ |

## Vendored — `vendor/`

| Path | Purpose |
|------|---------|
| `vendor/wiki-mcp/` | The wiki MCP server, as a git submodule (`chris-caracach-codingit/wiki_mcp`). Its own repo; also the home of the `/wiki:*` commands. |
