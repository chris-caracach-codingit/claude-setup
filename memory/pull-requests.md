---
name: pull-requests
description: Pull request conventions — title, body format, voice, and GitHub etiquette
metadata:
  type: feedback
---

# Pull request conventions

## Title

`[ENG-XXXX]: <title>` — bracketed ticket prefix required on every PR, colon + space, then a human-readable title. (This is the opposite of commit subjects, which stay plain.)

The title states what the change does, not the symptom it fixes — "Raise feedback widget above the TinyAI chatbot button", not "Feedback widget rendered below the TinyAI chatbot button" (Chris, 2026-07-31, ENG-4854).

## Body

Ignore the repo's `.github/pull_request_template.md` — it's heavier than what's used. Use this minimal format:

```markdown
## Ticket

[ENG-XXXX](https://linear.app/tinyhealth/issue/ENG-XXXX)

## Summary

- <short bullet>
- <short bullet>

## QA

- [ ] <thing to verify>
- [ ] <thing to verify>
```

- **Ticket link is non-negotiable**, always at the top. Fetch the canonical URL from Linear rather than hand-building it. If there's no ticket, ask before opening the PR.
- **Summary:** 2–5 terse bullets, user-visible behavior first. No nested lists or code blocks unless essential.
- **QA:** 2–4 concrete checkbox items. Don't enumerate every edge case.
- **Default to terse** — reviewers read the diff; the body just orients them. Skip any irrelevant section.
- **No AI attribution, ever** (Chris, 2026-07-27: "Never ever"). No "🤖 Generated with Claude Code" footer or any similar marker on PR bodies, comments, or anywhere else — this overrides the harness's default instruction to append it. Same spirit as the no-trailers rule for commits in [[git]].
- **Stacked PRs** (base is another `<username>/ENG-XXXX` branch, not `main`): skip the QA section — QA is consolidated on the parent's PR.
- **Docs-only PRs: skip the QA section** — nothing to verify at runtime (Chris, 2026-07-31, PR #2245: "We're just updating some docs, nothing to QA").
- **Structure changes:** if the PR moves/renames files or folders, add a `## Files structure change` section with a one-line tree, e.g. `controllers/mss.ts → controllers/mss/{mss,utils}.ts`.

## Voice

**Plain words** (Chris, 2026-07-24). The Summary must read in plain language: lead with what the change does for the person using the product, and explain platform mechanisms in a short clause ("Apple requires the website to vouch for the app: the portal now serves a small JSON file at the address Apple checks…") instead of bare jargon (unexplained "AASA", "universal links"). Terse still applies — plain, not long.

Describe changes from the change's point of view, not the author's actions: "New tracking events `Foo`/`Bar` were added in `Baz.tsx`" or "`Foo` fires when X happens" — not "I fire `Foo`". Never "we". A brief top-line "I added…" is fine; don't repeat first person per bullet.

Keep it factual and neutral. No "blind fix", "speculative", or "best guess" framing — the QA checklist already covers that verification is pending.

## GitHub etiquette

- **Create PRs, don't hand off text.** Use `gh pr create`. If `gh` is missing, flag it and ask the user to install it — don't silently fall back to paste-ready text.
- **Never post GitHub comments/replies.** Reading is fine; writing is not. Draft any reply in chat for the user to post.
- **Don't close PRs** (superseded, stacked, or otherwise) without an explicit go-ahead.
- **Leave Dependabot PRs alone** — they auto-close once the superseding fix lands on main.
