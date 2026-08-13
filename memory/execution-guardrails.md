---
name: execution-guardrails
description: Things Claude must not run or change on its own — the user controls these
metadata:
  type: feedback
---

# Execution guardrails

The user controls builds, data, and dependencies. Claude reads and edits files; these actions are off-limits without being asked.

- **No code/build/deploy commands.** No `bun` / `npm` / `turbo` / `sst deploy` or any build/test/dev/deploy script. When a step needs one, give the user the exact command to run. **Exception (granted 2026-07-23): `bun run type-check` is allowed** — the user wants that loop fast.
- **No direct database access** — no mysql client, tunnels, or creds from `.env`, even read-only, even sandbox. When data is needed, write the exact SQL and let the user run it; work from what they paste back.
- **No package installs.** Never run `bun add` / `npm install` / `yarn add`, and never edit `package.json` or lockfiles to add deps. First check whether an existing dep covers it; if a new one is genuinely needed, propose it (name + version + why) and wait for approval.
- **Prefer existing schema over migrations.** For linking feedback/events to more context, reuse existing jsonb `metadata_json` columns rather than adding columns. Flag and ask before any migration.
- **The user does the browser eyeballing.** When a change of ours needs visual/UI verification, hand the user a checklist — don't launch Chrome MCP / tiny-portals sessions to QA it yourself unless asked ("I'll test it. You just make some code", 2026-08-03, ENG-4857). The tiny-portals skill is for when the user explicitly asks Claude to check something in a portal.
- **No probe writes to shared infrastructure.** Never test permissions by creating/deleting throwaway objects (e.g. a dummy GitHub Actions secret) on shared repos or services. Check read-only signals (settings-page visibility, API role fields) or let the real operation's 403 be the answer.
- **No dedicated rollback scripts.** Prefer documented commands in the PR/wiki or a fully-resolved copy-paste one-liner in dry-run output. A committed script is acceptable only when the rollback is too complex to inline.
