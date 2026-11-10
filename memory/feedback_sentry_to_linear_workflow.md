---
name: feedback_sentry_to_linear_workflow
description: "Repeatable workflow for turning a Sentry alert/issue into a Linear ticket and fix: ticket shape, acceptance criteria, Sentry back-link, fix PR"
metadata:
  type: feedback
---

Workflow for triaging a Sentry alert into a Linear ticket + fix (established 2026-06-16 on ENG-4638).

**Why:** First time doing Sentry→Linear via MCP; the Sentry MCP cannot create or link Linear tickets (its only write tool is Seer analysis). The native Sentry↔Linear UI integration ("Link/Create Linear Issue" button on the issue page) is the only thing that writes the back-link onto the Sentry side.

**How to apply:**
1. Triage in Sentry (gather clues, group duplicate issues into one bug, capture impact + issue URLs). Alert rule lookups: issue alerts are project-scoped via `get_alert_rule kind=issue`; the `/monitors/alerts/<id>/` URL is an issue-alert rule, not a cron/metric alert.
2. Create ONE Linear ticket per suspected bug via Linear MCP `save_issue`: team Core Eng (ENG), current cycle (or Backlog if asked), project "DEV - Monitoring (Sentry) 25-26", priority by severity, description = symptom + impact + **Clues** + a clearly-labelled **Hypothesis (unconfirmed)** + **Acceptance criteria** (below). Do NOT assert a root cause or a fix — we are not sure what's going on; give the dev clues only (per [[linear-tickets]]). Attach Sentry issue URLs via `links`.
   Standard **Acceptance criteria** block (insert after the hypothesis):
   - Investigate the issue, identify its root cause, and implement a fix.
   - If it cannot be resolved on our side (third party / browser / expected user behavior), confirm and document that, then propose a way to stop it being reported to Sentry (inbound filter, `beforeSend` rule, or grouping/ignore) so it no longer adds noise to the alert.
   - Reproduce and verify the outcome on the `/debug/monitoring` route (results-portal, dev/sandbox/preview only), and document those QA steps in the PR description.
3. Manual one-time step (user, Sentry UI): on each Sentry issue click "Link Linear Issue" → paste ENG-XXXX for back-link + status sync.
4. Branch `christian/ENG-XXXX` ([[git]]), fix. Commits stay single-line ([[git]]), so NO `Fixes RESULTS-PORTAL-XXX` trailers; resolve the Sentry issues via the UI / Linear link instead. Don't put the ENG id in code ([[code-style]]).
5. PR titled `[ENG-XXXX]: …` with the Linear link ([[pull-requests]]); the QA section reproduces on the `/debug/monitoring` route.

Slack replies in alert threads follow [[messaging]] (no links, no ticket ids).
