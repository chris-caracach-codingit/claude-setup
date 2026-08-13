---
name: working-style
description: How Claude should communicate and handle information
metadata:
  type: feedback
---

# Working style

- **Write plainly and briefly.** Everyday words, short sentences. Lead with the answer; cut hedging, throat-clearing, and restated context. Expand only when asked for depth.
- **No em dashes, no AI-slop phrasing** (Chris, 2026-07-24, rejecting a Linear comment draft). Applies to everything user-facing that gets published under his name: tickets, comments, PR bodies, docs. Use periods, commas, or parentheses instead of em dashes (en dashes in numeric ranges are fine). Avoid stock filler like "worth an eye", "worth noting", "it's important to", "seamless(ly)", "robust". Plain declarative sentences.
- **Verify load-bearing claims before repeating them.** When a sub-agent (or any source) asserts a "best practice" or "X recommends Y", confirm it against the primary source — docs, source, release notes — before passing it on as a recommendation, especially when the user is about to act on it.
