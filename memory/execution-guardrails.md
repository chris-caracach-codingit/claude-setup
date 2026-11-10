---
name: execution-guardrails
description: "What Claude must not run, touch or change on its own: commands, servers, DB, deps, schema, browser, shared infra, GitHub workflows/secrets, credentials, AWS (read only), prod demo and shared QA accounts, teammates' PRs"
metadata:
  type: feedback
---

# Execution guardrails

The user controls builds, data, dependencies and every remote system. Claude reads and edits files; everything below is off-limits unless he asks. Outward messages are covered in [[messaging]].

## Commands and servers
- **No code/build/deploy commands.** No `bun` / `npm` / `turbo` / `sst deploy` or any build/test/dev/deploy script. When a step needs one, give the user the exact command to run. **Exception (granted 2026-07-23): `bun run type-check` is allowed**; the user wants that loop fast.
- **Never start, stop or restart servers.** The user runs every dev server himself; if a port is down, hand him the command and wait.
- **Hand commands in turbo form.** Chris runs workspace tasks through Turbo (2026-10-13: "I've always run turbo commands when available, not bun directly"): `bunx turbo dev --filter=pdf-report`, `bunx turbo test --filter=…`, `bunx turbo type-check --filter=…`, `bunx turbo lint --filter=…`. Fall back to the workspace's own `bun run <script>` only when no turbo task exists (tiny-ai `bun run start`, mobile). Same for wiki notes and QA plans. **Why:** turbo is the repo's task runner; filtered tasks keep caching and dependency ordering consistent, and it is how he works.

## Data and schema
- **No direct database access**: no mysql client, tunnels, or creds from `.env`, even read-only, even sandbox. When data is needed, write the exact SQL and let the user run it; work from what he pastes back.
  - Engineers DO have sandbox DB access through their own SSM tunnel (`apps/backend/scripts/db-tunnel`, 127.0.0.1:33306), so never design a tool or plan around them lacking it. Claude still never opens the tunnel or uses its credentials; the engineer runs the script.
- **Prefer existing schema over migrations.** For linking feedback/events to more context, reuse existing jsonb `metadata_json` columns rather than adding columns. Flag and ask before any migration. **No index migrations either** (2026-09-23, ENG-5025): if a new query would need an index that doesn't exist, find another table/column that is already indexed or drop the approach; check `SHOW INDEX` / schema before proposing a subquery on a hot path.
- **No dedicated rollback scripts.** Prefer documented commands in the PR/wiki or a fully-resolved copy-paste one-liner in dry-run output. A committed script is acceptable only when the rollback is too complex to inline.

## Dependencies
- **No package installs.** Never run `bun add` / `npm install` / `yarn add`, and never edit `package.json` or lockfiles to add deps. First check whether an existing dep covers it; if a new one is genuinely needed, propose it (name + version + why) and wait for approval.

## Browser
- **The user does the browser eyeballing.** When a change needs visual/UI verification, hand him a checklist; don't launch Chrome MCP / tiny-portals sessions to QA it yourself unless asked ("I'll test it. You just make some code", 2026-08-03, ENG-4857). The tiny-portals skill is for when he explicitly asks Claude to check a portal. When he does, the browser is read-only except the login form; any other state-changing action needs his OK first.
- **Never open the Chrome MCP browser for GitHub** (Actions runs, PR pages) or any other site that needs his login. The MCP browser has no credentials and GitHub answers "Page not found" for the private repo (2026-10-07, ENG-5112: "Do not spin up a browser for this you won't have access"). **Why:** the call wastes a permission prompt and produces nothing, and he keeps the browser for portal QA he asks for. **How to apply:** exhaust `gh` / API reads first; when only a web page holds the answer (e.g. a run-level error banner), say exactly what to look at and ask him to paste it.

## Shared infrastructure
- **No probe writes.** Never test permissions by creating/deleting throwaway objects (e.g. a dummy GitHub Actions secret) on shared repos or services. Check read-only signals (settings-page visibility, API role fields) or let the real operation's 403 be the answer.
- **No GitHub workflow, secret or variable changes.** Never run `gh workflow enable|disable|run`, `gh secret set|delete` or `gh variable set`. Hand Chris the exact command; turning workflows on or dispatching runs (e.g. the E2E turn-on steps) is his.

## Credentials: stay inside the tool at hand
When working through one integration (e.g. the tiny-health MCP), use only that tool's own config and credentials. Don't reach into `~/prog/tiny-portals/credentials.env` or its scripts unless the task is browser-driving a portal.
**Why:** Chris rejected a curl login test that borrowed OPS creds from tiny-portals to diagnose a tiny-health-mcp 401 (2026-07-21). The credential sources are intentionally separate; cross-wiring them isn't wanted, even read-only.
**How to apply:** if the tool lacks working credentials, report the blocker and let him fix that tool's own `.env`; don't substitute credentials from another tool's stash.

## AWS CLI: read only, never write
AWS CLI use from Claude Code is **only read, never write** (Chris, 2026-11-02, while investigating an attack on prod). Profiles in `~/.aws/config`: `sandbox`, `production` (SSO role th-ssm-prod, can read almost nothing), `production-devops` / `sandbox-devops` (role th-devops-access, reusing the th-prod / th-sandbox SSO sessions; these can read logs, WAF, CloudTrail), `tinyai-sandbox`; `default` points at sandbox. Prod WAF (waf-prod, waf-prod-v2) logs every request to log group `aws-waf-logs-group`.
- Read verbs only (describe/get/list/lookup/filter, plus Logs Insights start-query/get-query-results). Containment (WAF blocks, throttling, key rotation) = draft the exact command + blast radius + undo; he runs it.
- Even reads are off-limits when they expose secrets or customer data, or execute something: secretsmanager/ssm parameter values, `lambda get-function(-configuration)` (env vars), `ssm start-session/send-command`, `lambda invoke`, `s3 cp/sync/presign`, `s3api get-object`, Athena (writes results to S3), sts token minting.
- Always pass `--profile` explicitly (and `--region`); never rely on default.
- Raw logs go to the scratchpad; show only aggregates in chat; nothing goes to Slack/Linear/Sentry (drafts only, see [[messaging]]).
- Bound Logs Insights time windows (billed per GB scanned). Never touch attacker infrastructure.
- Keep a command + findings timeline for the post-mortem.
- No boto3/SDK scripts; they bypass the guard.
**Why:** prod access during an incident; one wrong write, or a secret or customer record leaking into the transcript, is worse than a slower investigation.
**How to apply:** the PreToolUse hook `~/.claude/hooks/aws-readonly.py` (wired in `~/.claude/settings.json`) enforces a verb allowlist and fails closed. If it blocks a genuine read, tell him and propose an ALLOW entry; don't route around it. The hook fails with "No closing quotation" on a Bash heredoc that contains apostrophes: write PR and issue bodies with the Write tool and pass `--body-file`.

## Production demo accounts: look, never touch
The three synthetic prod demo accounts that sales and stakeholders use (results `hello@`, practitioner `practitioners@`, partner `partnerships@`; Confluence TH page 335282187 "Demo Accounts") are allowed ONLY to eyeball outages and read errors. His words, 2026-10-14: "WE NEVER SHOULD MAKE ANY CHANGE WHILE USING THEM, WE'LL ONLY USE THEM TO EYEBALL POSSIBLE OUTAGES AND READ ERRORS."
**Why:** they are shared demo accounts in prod; an order goes to real fulfillment, a created practitioner is junk in prod, and any change is visible to the next salesperson demoing the product.
**How to apply:** creds live in `~/prog/tiny-portals/credentials.prod.env` (Claude never persists the passwords; he fills them in). Use them only from `/sentry-alert` step 7b (`--smoke`, High gravity, or live 5xx on a core endpoint) or when he asks to check prod; the portal is derived from the alert, never passed as an argument. `prod-smoke.sh` is only a pre-check; the browser pass is the real check, because the app catches errors and shows "Something went wrong" cards, so curl 200s prove nothing. Navigation, snapshots, console and network reads, and the login form are the whole allowed surface. Log out afterwards. The tiny-portals skill holds the procedure; see [[feedback_sentry_to_linear_workflow]] for the alert-to-ticket path.

## Shared sandbox QA accounts: leave them exactly as found
When QA-ing on shared sandbox `dev+` accounts, the accounts must look exactly as before when the test ends (Chris, 2026-11-02, PR #2788 QA).
**Why:** the `dev+` accounts are shared by the team; a leftover rename, answer or practitioner link confuses everyone else's testing.
**How to apply:**
- Snapshot the records before (full JSON, incl. `updated_at`) and diff after; report the diff.
- Prefer writes that are no-ops even if they succeed (send the record's current values). Skip "save unchanged" control steps: they still bump `updated_at`.
- Results-portal pair: `dev+twins` and `dev+newbornbundle` (creds in `~/prog/tiny-portals/credentials.env`, values single-quoted). Don't use `dev+bioinformatics`; Chris is replacing it. Never `dev+e2e…` (CI uses them).
- Login itself updates last-login time; say so rather than hiding it.

## Reviewing a teammate's PR: read the code only
When reviewing a PR that isn't Chris's (e.g. `/review-blind` on a teammate's branch), verify findings by reading code only. Don't `bun install`, build, or run the test suite or scratch repro tests. Mark runtime claims "confirmed by code reading" or "unverifiable".
**Why:** he stopped a `bun install` + turbo build during the ENGG-855 (PR #2788) review on 2026-11-02: "Do not run tests, just analyze the code".
**How to apply:** fetching the branch into a scratch worktree to read it is fine; stop before installing deps or running anything. When he says "it's not ours", give the handoff in chat, never as a file.
