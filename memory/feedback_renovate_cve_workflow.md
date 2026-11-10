---
name: feedback_renovate_cve_workflow
description: "Repeatable workflow for handling auto-created Renovate CVE tickets (\"[Security] Bump X\"): severity triage, PR takeover, preview-deploy traps, QA handoff"
metadata:
  type: feedback
---

Workflow for the auto-created security-bump tickets (established 2026-07-29 on ENG-4840 sharp / ENG-4841 cookie).

**Why:** `.github/workflows/renovate-cve-to-linear.yml` auto-creates a Linear ticket per Renovate CVE PR, defaulting priority to High even when CVSS couldn't be extracted (ENG-4841's advisory was actually Low). The PRs arrive as stale drafts. Applying "deploy → eyeball → QA" uniformly is over-process for build-time-only deps and under-specified for runtime deps — a triage step must decide the QA depth per ticket.

**How to apply:**
1. **Triage first — this decides everything downstream.**
   - Read the *advisory's* real severity from the linked PR body, not the ticket's default. If they disagree, fix the Linear priority (the ticket template itself asks for this).
   - Find where the package is used: grep for imports in `apps/` + `packages/`, and check whether it's build-time only (e.g. sharp existed only for `ViteImageOptimizer` in results-portal's vite.config — no runtime imports) or runtime/auth-critical (e.g. cookie in `packages/utils` cookies/adminAuth/portalJwt/impersonation/tempSignupCredentials).
   - Build-time-only + CI green ⇒ minimal QA (does the site build, do assets render). Runtime ⇒ enumerate the affected user flows for the QA plan.
   - **If the PR is a major bump, check whether a patch line exists now.** A Renovate PR opened before the patch existed keeps targeting the major, because `rebaseWhen: "conflicted"` in `vulnerabilityAlerts` stops refreshes. Example: #2275 wanted react-router v7, which drops the `v7_*` future flags used in results-portal's `renderWithProviders.tsx`; a hand-made patch bump on v6 (#2577, ENG-4963) replaced it. In that case open the patch-bump PR by hand (Chris runs the install) and close the Renovate PR only on his go-ahead.
2. **Refresh the branch.** Renovate PRs go stale (one sat a month). `gh pr update-branch <n>` (server-side merge of main; forward-only per [[git]]). This marks the PR "edited" so Renovate stops auto-rebasing — fine, we're taking it over. Confirm CI green after.
3. **Link and track.** Attach the PR to the Linear ticket, move ticket to In Progress. Do NOT edit `package.json`/lockfiles ourselves — the Renovate diff is the change ([[execution-guardrails]]: no package installs; taking over an existing Renovate PR is the approved path).
4. **Undraft + verify the preview deploy actually fired.** `deploy.yml` deliberately skips preview deploys for draft PRs; the FIRST preview deploy fires on the `ready_for_review` event. Two traps learned 2026-07-29 on #2044:
   - Don't run `gh pr update-branch` and `gh pr ready` back-to-back — the `synchronize` run evaluates with a draft-state payload (skipped) and the `ready_for_review` run can fail to materialize. Sequence: update-branch, let CI start, THEN ready.
   - After undrafting, confirm a live run exists: `gh run list --workflow deploy.yml --branch <head-branch>` — all-`skipped` conclusions mean no deploy happened. Remedy: re-fire the event with `gh pr ready --undo <n> && gh pr ready <n>`. NEVER add a dummy commit to force a deploy — change detection is Turborepo dependency-graph-based (`--filter=...[merge-base...head]`, dependents included), so `packages/*` changes already impact every dependent app; a missing deploy is an event problem, not a detection problem.
   - Then check the Plan Deployment job output lists the expected apps (backend + affected frontends).
5. **Smoke-test the PR preview BEFORE requesting review**, using the checklist from step 1 — cheapest point to catch a problem, and "verified on preview" makes the review easy. Caveat: know what the preview pairs with (a preview frontend against a backend not running this branch's packages proves only that it builds). Merge state is typically BLOCKED until a required approval — ask a teammate.
6. **Merge → sandbox deploy (push to main) → quick re-confirmation** (user drives merge/deploy verification).
7. **QA handoff with a written test plan on the ticket** — affected surfaces + severity context, not just a status flip. Build-time-only deps may justify skipping formal QA; that's the triage step's call. See [[qa]].
8. **Close the loop** — ticket to Done after QA sign-off.

Related: [[feedback_sentry_to_linear_workflow]], [[linear-tickets]], [[pull-requests]].
