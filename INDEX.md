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

## MCP servers — `mcp/`

| Path | Purpose | Reader's equivalent |
|------|---------|---------------------|
| `mcp/servers.json` | The MCP servers Christian runs: linear, atlassian, sentry, chrome-devtools, wiki (local), tiny-health (local, project-scoped), obsidian-vault (optional). OAuth servers carry no secrets; obsidian key is a placeholder. | `claude mcp list`; `~/.claude.json` → `mcpServers` |

## Settings — `settings/`

| Path | Purpose | Reader's equivalent |
|------|---------|---------------------|
| `settings/settings.json` | Model, effort, theme, enabled plugins, extra marketplaces, and hook wiring. Uses `$HOME` for portability. | `~/.claude/settings.json` |

## Conventions — `memory/`

Working conventions as drop-in Claude Code memory files. Prime material for "does my setup follow these?". Index: [`memory/MEMORY.md`](memory/MEMORY.md).

| Path | Covers | Reader's equivalent |
|------|--------|---------------------|
| `memory/git.md` | Commits, history discipline, branch naming | `~/.claude/CLAUDE.md` or `~/.claude/projects/<proj>/memory/` |
| `memory/pull-requests.md` | PR title, body, voice, GitHub etiquette | ″ |
| `memory/code-style.md` | React/TSX, CSS units, comments, root-cause fixing | ″ |
| `memory/execution-guardrails.md` | What Claude must not run/change on its own | ″ |
| `memory/linear-tickets.md` | Cycles, descriptions, reading specs | ″ |
| `memory/wiki-and-notes.md` | Wiki page granularity + update cadence | ″ |
| `memory/working-style.md` | Communication + verifying claims | ″ |

## Vendored — `vendor/`

| Path | Purpose |
|------|---------|
| `vendor/wiki-mcp/` | The wiki MCP server, as a git submodule (`chris-caracach-codingit/wiki_mcp`). Its own repo; also the home of the `/wiki:*` commands. |
