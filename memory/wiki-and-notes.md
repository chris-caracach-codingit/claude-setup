---
name: wiki-and-notes
description: "Where notes go and how: wiki page granularity and write cadence; working notes in ~/notes/tiny/, never ~/prog"
metadata:
  type: feedback
---

# Wiki & notes

- **One consolidated page per initiative**, not one page per ticket. For a multi-ticket project, make an umbrella page with per-ticket detail inline, plus a source page for the spec (Confluence/Figma). Skip individual ticket pages during planning/intake unless asked or a ticket grows into a standalone effort. (Shipped/in-flight engineering work can still get its own per-ticket page.)
- **Batch updates; don't write per prompt.** Keep working notes in conversation during an investigation. Patch the journal only at a natural checkpoint: the user asks, the session wraps up, or a meaningful sub-task closes with a verdict. Don't log after every tool call or hypothesis tweak.

## Working notes live in ~/notes/tiny/, never ~/prog
Review checklists, handoffs and other working notes go to `~/notes/tiny/<name>.md`, never under `~/prog`, not even its top level (which is not itself a git repo).
**Why:** Chris said "remove that file from git tree" on 2026-11-05, when the E2E review prep was written to `~/prog/`. He treats `~/prog` as the code tree.
**How to apply:** write new notes to `~/notes/tiny/` and point to them from the related project memory.

Memory upkeep: [[memory-hygiene]]. Doc voice: [[docs]].
