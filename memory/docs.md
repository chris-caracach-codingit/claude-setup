---
name: docs
description: "How to write docs (repo docs, Confluence, proposals, plans): timeless what-and-how, roles not names, plans declare; delivered as .md drafts, never web artifacts"
metadata:
  type: feedback
---

# Docs

## Deliver a .md file, not a web artifact
When the user asks for "a doc", "an analysis doc", or "a proposal", write a Markdown file (scratchpad, `~/notes/tiny/`, or repo path as appropriate) and show its content in chat. Do not publish an Artifact page for it.
**Why:** on 2026-09-15 (Doppio replacement proposal) Chris rejected a published artifact: "Nope, not a web app. Let's do a .md doc first, we'll push it to Confluence once it's done". Confluence is the destination; the .md is the working draft he reviews and pastes.
**How to apply:** iterate on the .md in chat and offer the Confluence push only when he says it is done (Confluence edits are draft-first, see [[messaging]]). Artifacts remain fine for genuinely app-shaped things (dashboards, tools).

## Timeless: what it is and how it works
A document describes **what the thing is and how it works**, in timeless present tense (sharpened 2026-07-30, mobile-app docs review). No status, no future ("will", "later", "once X lands"), no time references (dates, deadlines, versions-as-milestones), no personal names. Plain words. State and plans live in Linear and the wiki journal, never in docs. Applies to repo docs and Confluence; the wiki journal and PR bodies are temporal records by design and are exempt.
**Why:** a doc outlives any given moment; status and future text rot and turn a spec into a changelog/tracker. He wants specs and decision records, not trackers.
**How to apply:** rewrite "already/currently/pending/shipped in vX" and "will/planned" into timeless present ("the shell wraps…", "release tags queue a build…"). Open questions go to Linear, not the doc.

## Roles, never personal names
In docs committed to the repo (READMEs, workflow docs) and on Confluence, refer to people by role ("engineers", "the account owner", "the PO" only if role-generic), never by name ("Chris", "Tanner").
**Why:** docs outlive team assignments; names rot and read as ownership silos.
**How to apply:** describe responsibilities by role. Names are fine in conversation, Linear and Slack, just not in docs.

## Plan docs declare, they do not narrate
A plan or spec **declares and defines**: pieces, definitions of done, rules, roles, open questions. It never explains the situation behind a decision ("the QA analyst picked X because…", "the kickoff agreed…", "Tanner uses his own account"); that narrative belongs in the wiki journal or meeting notes. Chris, 2026-10-23 (AI E2E implementation plan review): "we declare and define how the implementation plan will look. That's it."
**How to apply:** every row or bullet is a declarative sentence about what exists or what is done; strip who-said-what, drop "Where we start from" style status sections, keep a reference ticket id where a dependency needs it.

## Plain words
No em dashes and no AI-slop phrasing, applied at write time, not as a cleanup pass: see [[working-style]]. Wiki conventions: [[wiki-and-notes]].
