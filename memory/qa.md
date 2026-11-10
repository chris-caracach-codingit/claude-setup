---
name: qa
description: "QA handoff rules: shape every change so the QA team can verify it, and the High/Medium/Low QA risk tiers with their Linear labels"
metadata:
  type: feedback
---

# QA handoff

## Build for the QA team's clarity
While building, keep asking "how will QA verify this?" and shape the deliverable so the QA team knows what changed and how to exercise it.
**Why:** Chris, 2026-10-13, ENG-5107/5110: "keep always in mind how QA will be in this ticket. We have to create the correct environment for QA team to have clarity on what we did." Security/backend-only changes are invisible in the UI, so QA needs explicit setup (which account, which endpoint, what to count, where to look) or the ticket stalls at QA.
**How to apply:**
- Write the PR's QA section as reproducible steps with expected results, not a list of edge cases. Name the portal/env (PR preview stack), the test account, and the signal to observe (email arrives / does not arrive, response status, DB column value).
- For per-account limits and timers, give QA a way to reset state (e.g. a SQL one-liner for Agustín or Chris to run on the preview DB, or a wait time) and a way to drive many requests (curl loop or portal clicks) without needing code.
- Split migrations into their own PR per ticket so reviewers and QA see one concern.
- Stacked PRs still consolidate QA on the parent per [[pull-requests]].

## QA risk tiers
Engineering labels every Linear ticket with a QA risk tier, per the "QA Risk Tiers" Confluence page (TH space, written by Kuba): https://tinyhealth.atlassian.net/wiki/spaces/TH/pages/1620443161/QA+Risk+Tiers

| Tier | Examples | Who tests |
| --- | --- | --- |
| High | Checkout, Stripe billing + webhooks, subscription changes, Shopify order sync, login/auth, permissions, kit registration, results and reports, data migrations | Manual QA (the QA team) |
| Medium | User-facing changes to core flows outside High, shared components (`packages/ui`), API changes other services consume, non-trivial backend logic | Another engineer, not the author |
| Low | Copy changes, isolated UI tweaks, internal tools (ops-dashboard), work behind a flag no user sees, refactors covered by unit tests | The author |

Engineers still do their own testing at every tier. Move up a tier when the change is complex, the code area is new to you, or you are new to the org; moving down is allowed too. The page's definitions evolve.
**Why:** the tier decides the QA handoff path, so a ticket without one stalls at review/QA.
**How to apply:** when creating or grooming a ticket (see [[linear-tickets]]), propose a tier with a one-line reason; Chris reviews it before I apply the label. Labels live in the Core Eng single-select group "Risk" with children "High", "Medium", "Low" (`list_issue_labels` with a name filter misses them; list the whole team). In a PR body, name the tier and the tester it implies. Flag-gated work is Low only while the flag hides it from users; the flag rollout ticket inherits the underlying tier.
