---
name: tiny-portals
description: Drive any Tiny Health portal (Results, Ops, Practitioner, Partner, PDF report) in a real browser via the Chrome DevTools MCP to check or verify something. Use when asked to "log into <portal>", "run/open a <portal> server and check X", "view a PDF report for kit Y", or otherwise inspect a portal's live UI. Covers verified ports/backends, login (incl. fast JWT harvest), the PDF JWT-cookie flow, and the browser-safety rules. Sandbox/test by default; production only through the read-only demo accounts (see "Production demo accounts").
---

# Tiny Health portal access

Drive Tiny Health portals in the browser to verify behavior. Sandbox/test data only.
Credentials + the per-app data live in `~/prog/tiny-portals/` (untracked, sibling of
the repo): `credentials.env` and `ACCESS_RULES.md`. The JWT harvester is
`~/prog/tiny-portals/harvest-jwt.sh`.

## Hard constraints (always)

- **Sandbox/test accounts by default.** Never real-user credentials. The ONE
  production exception is the synthetic demo accounts in `credentials.prod.env`,
  under the stricter rules in "Production demo accounts" below.
- **Never echo a secret's value** into chat, a commit, a log, or a screenshot.
  Read creds from `credentials.env`; confirm a token only with a 6-char mask + expiry.
- **Never start, stop, or restart servers** (no `bun`/`npm`/`turbo`/`serverless`,
  no builds/deploys/migrations). The user runs all servers themselves. If a server
  is down, hand the user the exact command and wait — see "Ensure the server is up".
- **Browser is read-only by default.** The ONLY sanctioned writes are: the login
  flow (form submit, or the `/auth/login` curl), and setting the PDF `th_admin_jwt`
  cookie. ANY other state-changing action — creating/editing/releasing/voiding,
  impersonating into a user session, toggling settings, submitting any non-login
  form — requires explicit user confirmation FIRST. Navigation, snapshots,
  screenshots, and read-only `evaluate_script` are always fine.

## Production demo accounts (read-only exception)

`~/prog/tiny-portals/credentials.prod.env` holds the three synthetic prod demo
accounts that sales and stakeholders use to show the product (Confluence TH
"Demo Accounts", page 335282187). Chris, 2026-10-14: **we never make any change
while using them; we only use them to eyeball possible outages and read errors.**

- **When:** only from `/sentry-alert` step 7b, or when Chris explicitly asks to
  check prod. Never for feature QA, never "just to look".
- **Absolute read-only.** Allowed: `navigate_page`, `take_snapshot`,
  `take_screenshot`, `list_console_messages`, `list_network_requests`,
  `get_network_request`, read-only `evaluate_script`, and the login form. Forbidden,
  no exceptions and no "confirm first": ordering kits, creating/inviting/assigning
  practitioners, releasing or editing anything, bookmarks, ratings, surveys,
  consult booking, settings, impersonation, any non-login form submit. The demo
  page itself warns that partner-portal orders go straight to fulfillment.
- **URLs:** Results `https://account.tinyhealth.com`, Practitioner
  `https://practitioner.tinyhealth.com/portal`, Partner
  `https://partner.tinyhealth.com/portal`, API `https://api.tinyhealth.com`.
- **Pre-check first:** `~/prog/tiny-portals/prod-smoke.sh [results|practitioner|partner|all]`
  (page reachable, login, core read endpoints; PASS/WARN/FAIL table; no browser,
  no token printed). It only tells "API down" from "API fine". It cannot see what
  a user sees, because the app catches errors and renders a "Something went
  wrong" card instead of failing. The browser pass below is the real check.
- **Browser pass:** record the UTC start time and `curl -s https://api.ipify.org`
  (our IP, for the Sentry cross-check). Navigate to the portal → if a login form,
  `fill` the `PROD_<PORTAL>_EMAIL` / `PROD_<PORTAL>_PASS` values (read from the
  file at call time, never printed) → `wait_for` the home. Then walk the route
  list for that portal. On **each** page, after it settles, collect three signals:
  1. `take_snapshot` and grep it for error text: "Something went wrong",
     "please try again", "check the kit ID", "wait and try again", a stale-build
     reload prompt, or an empty main area where a list is expected.
  2. `list_network_requests` and count POSTs to the `ingest.us.sentry.io` host
     since the previous page (the SDK batches, so wait ~3 s before reading).
     Envelopes include sessions and replays, so a count is a hint; the Sentry
     cross-check in `/sentry-alert` is the authoritative count.
  3. Failed requests (4xx/5xx, aborted) in the same list, and
     `list_console_messages` errors.
  4. `take_screenshot` with `filePath` in the session scratchpad dir (the Chrome
     MCP refuses paths outside its workspace roots), named
     `<YYYY-MM-DD-HHMM>-<portal>-<route-slug>.png` (route slug: `home`,
     `results-<kit>`, `action-plan-<kit>`, `account`, ...). Viewport only, PNG.
     After the pass, `mv` them all to `~/sentry-alerts/screenshots/`.
     These are demo-account pages, so they are safe to share in the Slack thread;
     the `/sentry-alert` report says which one to attach.
  One PASS/FAIL line per page. **Log out** at the end (the Chrome profile is
  persistent; never leave a prod session behind).
- **Route lists** (view-only pages; kit ids come from the list page, never typed
  from memory):
  - Results: `/` (home, kit list) → `/results/<first kit>` (summary) →
    `/action-plan/<same kit>` → `/account`.
  - Practitioner: `/portal` (patients/kits) → one kit's results from the list →
    `/settings` (read only, touch nothing). Never `/order-kits/*`.
  - Partner: `/portal` → `/orders` (view) → `/users` (view). Never `/order-kit`,
    never assign a practitioner.
- **Noise:** every visit creates real Sentry, Segment, and Amplitude events under
  the demo account's email. Record the UTC time of the check so later triage can
  tell our events from customers'.
- If a password is blank in the file, stop and ask Chris to fill it from the
  Confluence page. Do not look it up and paste it yourself.

## Step 0 — Ensure the server is up (never start it yourself)

Navigate to the target URL with the Chrome MCP. If it connects, proceed. If you get
`ERR_CONNECTION_REFUSED` (or the app shows a backend 500 / connection error), the
server (or its backend) isn't running. Tell the user the exact command and ask them
to start it — suggest they type `! <command>` so the output lands in the session.
Then continue once it's up.

Dev commands (run from repo root `apps/<app>`, the user's job):

| Portal | URL | Start command | Backend it needs |
|---|---|---|---|
| Results (local) | http://localhost:3003 | `cd apps/results-portal && bun dev` | sandbox API (remote) |
| Results (sandbox deploy) | https://account.test-tinyhealth.com/login | — (always up) | sandbox API |
| Ops Dashboard | http://localhost:3004 | `cd apps/ops-dashboard && bun dev` | **local backend :3001** |
| Practitioner | http://localhost:3013 | `cd apps/practitioner-portal && bun dev` | toggle (see below) |
| Partner | http://localhost:3023 | `cd apps/partner-portal && bun dev` | sandbox API (remote) |
| PDF Report | http://localhost:3000 | `cd apps/pdf-report && bun dev` | sandbox API (remote) |
| Local backend API | http://localhost:3001/sandbox | `cd apps/backend && bun dev` | — |

Ports can drift; if a guess is refused, ask the user which port it's on. Ops and PDF
historically both defaulted to :3000 — Ops was moved to :3004, but confirm.

## Backend resolution (the Vite portals)

Results/Ops/Practitioner/Partner pick their API via `getBaseUrl()`
(`packages/api-client/src/base-url.ts`) from two env vars in each app's `.env.local`
(`VITE_APP_ENVIRONMENT`, `VITE_APP_USE_SANDBOX`):

- `development` + no `USE_SANDBOX` → **local backend** `http://localhost:3001/sandbox`
  (so the local backend on :3001 must be running)
- `useSandbox=true` (any non-prod env) → **`https://sandbox-api.tinyhealth.com`**
- only `environment==='production'` → prod; anything else fails safe to sandbox

Observed defaults: Partner ships `USE_SANDBOX=true` (sandbox). Practitioner default is
local; the user flips `VITE_APP_USE_SANDBOX=true` to point it at sandbox. Ops uses the
local backend. When a login fails with a backend error, first check which backend the
app is wired to and whether that backend is up.

## Login

Credentials in `credentials.env` (read with Bash; never print). Accounts:
`RESULTS_EMAIL_NEWBORN`/`_PASS_NEWBORN` and `_BIO` (Results default is
`RESULTS_DEFAULT`, currently `NEWBORN` = `dev+newbornbundle`); `OPS_EMAIL`/`_PASSWORD`;
`PRACTITIONER_EMAIL`/`_PASSWORD`; `PARTNER_EMAIL`/`_PASSWORD`.

**Standard form login (Ops, Practitioner, Partner, Results-local):**
1. `navigate_page` to the portal, `take_snapshot`.
2. If already on a dashboard (persistent Chrome profile), you're done.
3. If on a login form: `fill` email + password (read the password from
   `credentials.env` at call time; it must go inline in the `fill` value), click
   submit, `wait_for` a dashboard string.
4. **Stale-session gotcha:** if an authed route shows "Something went wrong" / a 500
   from a leftover session in the persistent profile, click **Log Out** (or clear the
   session) to get a clean login form, then log in fresh. Don't assume bad creds.

## PDF report flow (special — no login form)

The PDF app authenticates from a JWT (`th_admin_jwt` cookie or `Authorization: Bearer`,
see `apps/pdf-report/app/helpers/resolveAuth.ts`). Root returns `{"error":"Unauthorized"}`
until the cookie is set.

1. **Harvest the JWT (fast, no browser):** run `~/prog/tiny-portals/harvest-jwt.sh [ACCOUNT]`
   (default is `PDF_DEFAULT`, currently `BIO` = `dev+bioinformatics`; pass `NEWBORN`
   to override). It POSTs the account creds to
   `https://sandbox-api.tinyhealth.com/auth/login` and writes `.token` into
   `PDF_ADMIN_JWT` in `credentials.env` (masked confirm + expiry). This is the same
   token Results stores in `localStorage.jwtToken`. Re-run on a 401.
   - Browser fallback only if the API path fails: log into Results, then
     `evaluate_script` `localStorage.getItem('jwtToken')`.
2. `navigate_page` to `http://localhost:3000` once, then set the cookie with
   `evaluate_script`. NOTE: the Chrome MCP `evaluate_script` `args` field only accepts
   element uids, so **inline the token in the function body**, not via `args`:
   ```js
   () => { const jwt = "<TOKEN>"; document.cookie = `th_admin_jwt=${jwt}; path=/`;
           return document.cookie.includes('th_admin_jwt'); }
   ```
3. `navigate_page` to `http://localhost:3000/<kitId>` and `take_snapshot` / screenshot.

## Gotchas

- **Huge snapshots:** a full report/list snapshot can exceed the tool output limit and
  get saved to a file. Don't re-read it whole — `grep` the saved file for the headings
  / strings you care about, or delegate the read to a subagent.
- Sandbox kit ids seen across portals: gut `TST629`, PRO `KIT052`, vaginal `KIT050`,
  baby `ENG4515QA`. (Confirm against the live data; these change.)

See `~/prog/tiny-portals/ACCESS_RULES.md` for the authoritative creds layout and any
updates to ports/accounts.
