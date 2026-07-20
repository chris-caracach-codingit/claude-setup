# claude-setup

A reference snapshot of the Claude Code setup Christian uses at Tiny Health —
hooks, slash commands, agents, skills, MCP servers, settings, and working
conventions. Private / internal.

**This repo is for reading, not installing.** There are no install scripts.
Point Claude at it and ask it to compare your own setup against this one, explain
a piece of it, or borrow an idea.

## How teammates use it

Clone it, then ask Claude things like:

- *"Compare my Claude Code setup (`~/.claude`) against this repo and tell me what I'm missing."*
- *"What conventions does this repo define that I don't follow yet?"*
- *"Explain what the `tiny-portals` skill does and how it stays safe."*
- *"Show me how the idle-notification hook is wired so I can set up my own."*

Claude reads [`INDEX.md`](INDEX.md) to orient, then dives into whatever's relevant.

## Where to start

- **[`INDEX.md`](INDEX.md)** — full catalog: every artifact, what it is, and where the equivalent lives in your own `~/.claude` so comparison is direct.
- **[`memory/MEMORY.md`](memory/MEMORY.md)** — the working conventions (git, PRs, code style, guardrails, tickets, notes, communication).

## Layout

```
claude-setup/
├── INDEX.md      catalog of everything here (start here)
├── hooks/        shell hooks (bash formatter, idle notification)
├── commands/     slash commands (/review-diff, /work)
├── agents/       subagent definitions (work-task-worker)
├── skills/       skills (tiny-portals)
├── mcp/          MCP servers Christian runs (servers.json)
├── settings/     settings.json (model, hooks, theme, plugins)
├── memory/       working conventions as memory files
└── vendor/       wiki-mcp (git submodule; also holds /wiki:* commands)
```

## Secrets

Nothing sensitive is committed. OAuth-based MCP servers carry no keys; the one
local key (`obsidian-vault`) appears only as a placeholder. Portal credentials
and access rules live outside this repo (`~/prog/tiny-portals/`, untracked) — the
`*.example` / `*.template` files here only document their shape.
