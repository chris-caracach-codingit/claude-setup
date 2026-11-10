---
name: messaging
description: "Outward messages (Slack, GitHub and Linear comments, Confluence edits) are drafted in chat as one markdown block and the user sends them; Slack drafts carry no links or ticket ids"
metadata:
  type: feedback
---

# Messaging: draft, never send

Never post messages to people on the user's behalf. Draft the text in chat and let him send it. This covers Slack (`slack_send_message`, thread replies, Slack drafts), GitHub comments, and Linear comments. Confluence page edits are draft-first too: even on a page he authored, don't publish via `confluence_update_page` without his explicit go-ahead (2026-09-03, ENG-4965: "Do not change Confluence for now"). Applies even when he says "drop the comment for X" or "post this" (2026-08-12, ENG-4896: rejected a `slack_send_message` into the TinyAI thread, "Do not send the message, just drop it here, I'll send it").

**Why:** anything posted goes out under his name to teammates. He wants to read the final wording and pick the moment before it lands.

**Carve-out: his own ticket's fields, after he approves the text.** Writing a description onto a ticket he created and owns is not a message to anyone, so it does not go out under his name to teammates. Draft it in chat first; if he approves and says to paste it, paste it (2026-08-14, ENG-4884: "It's ok that way, paste it in the ticket"). Comments on any ticket stay draft-only, since those notify people. Creating PRs with `gh pr create` is still fine, see [[pull-requests]].

**One-time exceptions stay one-time.** When he allows a post "just this time" (2026-10-29, Confluence replies on the AI E2E pages), it covers that one post. It never becomes standing permission; the next message is a draft again.

**How to apply:** output the message in ONE fenced ```markdown code block (raw markdown inside, no blockquote `>` prefixes), so it pastes into GitHub/Linear as is (asked again 2026-11-06 after a `>` blockquote draft didn't copy cleanly). Strip raw Slack mention syntax like `<@U01ABC>`, which only renders through the API; use the plain name so he can type the @ mention himself. Related: [[execution-guardrails]], [[working-style]].

## Slack drafts: plain text, no links, no ticket ids
Slack drafts (`#dev-sentry-alerts` replies, and Slack in general unless he asks otherwise) carry no hyperlinks and never mention a Linear ticket id. Say "already ticketed" / "ticketed yesterday" instead. Sentry short ids stay as bare text.
**Why:** the Linear Slack app links any message that mentions `ENG-XXXX` to that ticket, and he does not want alert threads tied to Linear tickets (2026-10-15, reviewing a /sentry-alert draft).
**How to apply:** the rule is also in the `sentry-alert` skill's Slack format section. If a ticket id is genuinely needed in Slack, ask first.
