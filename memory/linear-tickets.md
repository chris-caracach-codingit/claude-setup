---
name: linear-tickets
description: Linear ticket conventions — cycles, descriptions, and reading specs
metadata:
  type: feedback
---

# Linear tickets

- **Default to the current cycle.** When creating a ticket without a specified cycle, set it to the target team's current cycle (`list_cycles` with `type: "current"`). Skip if the user says a different cycle, "no cycle", or "backlog".
- **Descriptions expose the problem only.** State what's broken or missing, where it lives (file paths, symptoms), and a back-link to any parent ticket. No "Suggested approach", "Proposed fix", or "Goal" sections — the assignee decides the approach.
- **Plain-words bug tone** (Chris, 2026-07-31, rewriting the mobile v1.0 bug tickets). Descriptions read like "this is the bug": symptom, repro, and a short factual pointer to where it lives. No root-cause essays, no fix-implying analysis ("X should be scoped to Y"), no em dashes, no AI-slop phrasing. **Why:** tickets are published under Chris's name and the assignee (often Chris) does the diagnosing. **How to apply:** one or two plain sentences per section; keep file refs; cut anything that reads as a solution idea. See [[working-style]].
- **Comments: short and plain.** Ticket comments state facts in plain words, no over-explaining, no long structured write-ups (2026-07-29: a multi-section ENG-4798 draft was rejected for a half-length plain version). Also ask why Linear needs updating at all before writing — only when the ticket's deliverable or the team needs it.
- **Read "Current vs Desired" tables fully.** Every row in such a table is visual work, even rows whose logic/links don't change. Don't conflate "no link change" with "no design change". Logic changes are documented separately; summarize visual scope and logic scope separately. Read the whole description before planning — don't anchor on the first table.
