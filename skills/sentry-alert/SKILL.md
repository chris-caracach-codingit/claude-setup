---
name: sentry-alert
description: Investigate a Sentry alert from #dev-sentry-alerts. Use when the user says "/sentry-alert", pastes a Sentry alert or issue URL, or says "look at the latest Sentry alert". Resolves the alert rule, finds the issues that drove it, checks the local log for repeats, optionally smoke-checks prod with the read-only demo accounts (--smoke), reports in chat, appends to the log, and drafts a short Slack thread reply. Read-only in Sentry and in prod; never creates tickets unless asked.
---

# Sentry alert investigation

Turn one Slack alert into a short triage: which issues fired, which are new versus already seen, what they have in common, and what to do next. Sentry is read-only here. Linear tickets are a separate step the user asks for explicitly.

## Fixed facts

- Sentry org: `tiny-health`, region `https://us.sentry.io`, web `https://tiny-health.sentry.io`.
- Projects: `results-portal`, `practitioner-portal`, `partner-portal`, `tiny-backend`, `tiny-ai`.
- Slack channel: `#dev-sentry-alerts`, id `C0A2Q9Q82DN`. Only the Sentry bot posts there.
- The usual alert is a **metric alert** ("more than N users experiencing errors in the last X hours"). Its URL looks like `/alerts/rules/details/<ruleId>/?alert=<n>`. That page is a rule, not an issue, so the work is to find the issues behind the count.
- Known rule `385457` (monitor `6248810`): results-portal, `count_unique(user)` of `is:unresolved` error events in `production`, critical when > 30 over a 2-hour window. If the URL carries this id, skip step 1.
- Environment: `production` only unless the alert says otherwise. Local and sandbox are not evidence.
- Findings log: `~/sentry-alerts/log.md`. One block per alert, newest at the bottom. This is the memory of past alerts; grep it by issue short id.

## Input

`$ARGUMENTS` is one of:

- Nothing. Read the newest messages in `C0A2Q9Q82DN` with `slack_read_channel` (limit 5, `response_format: detailed` so you get each message's `ts`). Take the most recent alert and name it in the report.
- A Sentry alert URL (`/alerts/rules/details/...`). Still read the channel to find the matching message and its `ts`, needed for the thread reply.
- A Sentry issue URL or short id (`RESULTS-PORTAL-123`, `TINY-BACKEND-45`). Skip to step 3 with that single issue. No Slack reply unless the user points at a message.
- A Slack permalink. Read it with `slack_read_thread`, take the alert URL and the parent `ts` from it.

Any of the above may carry `--smoke`. It forces step 7b regardless of gravity. Which portal gets checked is never an argument: derive it from the alert (see 7b).

## Steps

1. **Resolve the rule.** `execute_sentry_tool` name `get_alert_rule` with `kind: "metric"` and the numeric id from the URL. Note project, query, threshold, and time window. The trigger time is the Slack message timestamp.

2. **Find the issues in the window.** Scoped to the rule's project and the window (round up to the nearest `period` the tools accept, usually `24h`):
   - `search_errors`: `errors in production grouped by issue, sorted by unique users, last 24h`, fields `issue`, `title`, `count()`, `count_unique(user)`.
   - `search_issues`: `is:unresolved environment:production lastSeen:-24h`, sort `user`, limit 20.
   Keep every issue that contributed users in the window. Drop long-running background noise unless it alone explains the threshold.

3. **Check the log first.** For each issue short id, `grep -n <ID> ~/sentry-alerts/log.md`. Classify every issue as one of:
   - **new**: never in the log.
   - **repeat**: in the log; quote the last date and verdict.
   - **tracked**: a past entry gave it a Linear ticket; quote the ticket.
   This is what makes the report useful over time. Do not skip it.

4. **Inspect each contributing issue** with `get_sentry_resource`. Record: title, first seen, last seen, users, events, release tags, browser or runtime, top frames, `new` / `regressed` / `ongoing`, linked Linear ticket on the Sentry side.

5. **Group.** Collapse issues that share a stack, release, route, or component into one suspected bug. Separate "same symptom, different cause". Note which group tipped the threshold.

6. **Correlate with deploys.** Compare the dominant group's first-seen time with `git log origin/main --since=<window> --oneline` and recent `v*` tags. A matching release boundary is a clue, not a verdict.

7. **Decide gravity.** One of:
   - **High**: new issue, many users, a core flow (login, results loading, checkout, PDF), or clearly tied to a deploy.
   - **Medium**: new or regressed, limited users or a secondary screen.
   - **Low**: repeat already tracked, or noise (browser extensions, `ResizeObserver loop`, `Importing a module script failed` on stale tabs, third-party scripts, cancelled requests).

7b. **Prod smoke (conditional).** Answers the one question Sentry can't: is a user still seeing this right now? Run it when **any** of these holds, otherwise write `Prod smoke: not run (<why>)` and move on:
   - gravity is **High**;
   - the dominant group is 5xx / timeouts on a core endpoint (`/api/kits`, `/api/practitioners`, `/api/features`, `/auth/*`) and its last-seen is within the past hour;
   - the user passed `--smoke`.

   **Which portal:** from the alert, never from an argument. Sentry project `results-portal` → results; `practitioner-portal` → practitioner; `partner-portal` → partner; `tiny-backend` → the portal whose users the failing endpoint serves (`/api/partners/*` → partner, `/api/practitioners/patient-*` or `/api/consults/*` with practitioner auth → practitioner, anything else → results). If the issues span two portals, check both. When unsure, results.

   **Rules (non-negotiable, from Chris 2026-10-14):** the prod demo accounts in `~/prog/tiny-portals/credentials.prod.env` are shared sales/stakeholder demo accounts. **Read-only.** Eyeball outages and read errors only. Never order kits, create or assign practitioners, submit any non-login form, toggle a setting, impersonate, bookmark, rate, or change anything. Never echo a password or token. Full procedure and route list: `tiny-portals` skill, "Production demo accounts".

   The app catches almost everything (card and app error boundaries, `monitoredRequest` turning a 5xx into a handled Sentry event plus a "Something went wrong" card), so a 200 from curl proves nothing about what a user sees. The browser pass is therefore the check; the API script is only a pre-check.

   1. **Pre-check (10 s, no browser):** `~/prog/tiny-portals/prod-smoke.sh <portal>`. Page reachable, login works, core GETs answer. It decides the story — "API down" (stop here, that's the finding) versus "API fine, look at the client".
   2. **Browser pass (the check):** note the UTC start time, then follow the `tiny-portals` route list for that portal. On each page collect three signals: error text in the snapshot ("Something went wrong", "please try again", "check the kit ID", stale-build reload), error reports leaving the page (POSTs to the `ingest.us.sentry.io` host in `list_network_requests`), and failed requests / console errors. One PASS or FAIL line per page. Log out at the end.
   3. **Sentry cross-check:** `search_errors` for production errors with `timestamp:>=<start UTC>`; mark as ours the events whose user is the demo email or our public IP (`curl -s https://api.ipify.org`, run before the pass) or whose transaction matches a page we visited at that minute. This confirms what the session produced from the server side, including handled events the page sent silently. Our events are not customers' and must not count toward the alert.

   Verdict: **ongoing** if any page FAILs or the cross-check shows one of the alert's issues produced by us; **not reproducing now** if every page passes and the cross-check is clean.

8. **Report in chat** with the chat format below. Do not run Seer unless asked or the stack is unreadable. Do not create Linear tickets, resolve issues, or change alert rules.

9. **Append to the log** with the log format below. Always, even for noise. That is how repeats get recognized next time.

10. **Draft the Slack reply** with `slack_send_message_draft`, `channel_id: C0A2Q9Q82DN`, `thread_ts` = the alert message's `ts`, using the Slack format below. Print the draft in chat as well. Do not use `slack_send_message`. The user sends it from Slack. Only one attached draft per channel exists at a time, so if the tool returns `draft_already_exists`, say so and leave the text in chat.

## Chat format

```
Alert: <rule name>  ·  fired <local time>  ·  project <slug>
Window: <threshold> over <hours>  ·  Gravity: <High|Medium|Low>

Issues behind it (by users):
- <SHORT-ID> <title>  — <users>u / <events>e, <new|repeat since <date>|tracked ENG-XXXX>, first seen <time>
- ...

Suspected bugs:
1. <one line>  ·  issues <ids>  ·  explains ~<N> of the <threshold> users
   Clues: <release/route/browser/frames, 2–4 bullets>
   Hypothesis (unconfirmed): <one line, or "none yet">

Not ours / noise: <ids and why, or "none">

Prod smoke: <not run (<why>) | <HH:MM UTC> <portal> — ongoing | not reproducing now>
  Pre-check: <API ok | FAIL <probe>>
  <route>: <PASS | FAIL — error text / n Sentry envelopes / failed requests>
  ...
  Cross-check: <n events from us since HH:MM, issues <ids> | clean>
  Screenshots: <dir, n files>

Recommendation: <ticket per bug | filter | watch | already tracked as ENG-XXXX>
```

Under one screen. Every issue id links to its Sentry URL.

## Log format

Append to `~/sentry-alerts/log.md`:

```
## <YYYY-MM-DD HH:MM> · rule <id> · <project> · <High|Medium|Low>
Issues: <SHORT-ID> (<users>u, <new|repeat|tracked>), <SHORT-ID> (...), ...
Bugs: <one line per suspected bug, with issue ids>
Noise: <ids, or none>
Action: <ticket ENG-XXXX | filter proposed | watch | none>
Smoke: <not run | HH:MM UTC <portal> PASS n/WARN n/FAIL n — ongoing | not reproducing now; failing probes listed>
Notes: <one line of anything the next run should know, e.g. "tied to v26.10.9 deploy">
```

Short ids must appear verbatim so grep finds them. Update the `Action` line of an older entry when the user tells you a ticket was created for it.

## Slack format

Thread reply, plain, no headers, under about 7 lines. The first line is the headline: these alerts exist to catch outages, so the outage status comes first, in bold, before any Sentry detail.

```
**<🟢 No outage | 🟠 Partial outage | 🔴 Outage | ⚪ Not checked live> — <5–8 words: what is or isn't broken for users>**
Looked into this one. <High|Medium|Low> gravity.
Main driver: <SHORT-ID> <very short title> — <users> users, <new | same as <date> | already ticketed>.
Also: <SHORT-ID> (<users>u, <status>), <SHORT-ID> (...).   ← omit if none
Likely: <one-line hypothesis, marked as unconfirmed>   ← omit if none
Checked prod at <HH:MM UTC> with the demo account: <what loaded fine> / <what still fails and which screen>.   ← only when the smoke ran
Next: <ticket | filter | watching | nothing, already tracked>.
```

Headline rules:
- 🔴 **Outage**: login fails, or a core page (home, results, action plan) FAILs in the browser pass.
- 🟠 **Partial outage**: core pages load but one endpoint or one secondary screen still fails live (e.g. a 502 behind one form).
- 🟢 **No outage**: pre-check and every page PASS, cross-check clean.
- ⚪ **Not checked live**: smoke did not run; the headline then says what Sentry alone suggests ("looks like stale-tab noise", "backend 5xx, unverified").

Plain text only: no hyperlinks (not even to Sentry) and no Linear ticket ids — the Linear Slack app attaches the thread to any `ENG-XXXX` it sees, and Chris does not want alert threads tied to tickets (2026-10-15). Say "already ticketed" or "ticketed yesterday" instead. Short ids stay as bare text. No stack traces, no code, no file names.

**Screenshot.** The Slack MCP cannot attach files to a draft. When the smoke ran, the browser pass saved one PNG per page under `~/sentry-alerts/screenshots/`. Pick one for the thread: the failing page if any page FAILed, otherwise the home page. Then put it on the clipboard so the user can Ctrl+V it into the draft:

```
xclip -selection clipboard -t image/png -i <path>
```

(the session is X11 with `DISPLAY=:0`; `wl-copy --type image/png < <path>` if a Wayland socket exists). Confirm with `xclip -selection clipboard -o -t TARGETS | grep png`. Print `Attach: <path> (on your clipboard, Ctrl+V into the draft)` in chat right under the draft. Never upload it anywhere yourself.

## If the user then says "ticket it"

Follow the Sentry-to-Linear workflow memory: one ticket per suspected bug, team Core Eng, project "DEV - Monitoring (Sentry) 25-26", description = symptom + impact + Clues + Hypothesis (unconfirmed) + the standard Acceptance criteria block. Draft in chat first, save with `save_issue` once approved, then update the log entry's `Action` line with the ticket id. The Sentry-side back-link is manual in the Sentry UI.
