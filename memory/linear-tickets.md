---
name: linear-tickets
description: Linear ticket conventions — cycles, descriptions, and reading specs
metadata:
  type: feedback
---

# Linear tickets

- **Default to the current cycle.** When creating a ticket without a specified cycle, set it to the target team's current cycle (`list_cycles` with `type: "current"`). Skip if the user says a different cycle, "no cycle", or "backlog".
- **Descriptions expose the problem only.** State what's broken or missing, where it lives (file paths, symptoms), and a back-link to any parent ticket. No "Suggested approach", "Proposed fix", or "Goal" sections — the assignee decides the approach.
- **Read "Current vs Desired" tables fully.** Every row in such a table is visual work, even rows whose logic/links don't change. Don't conflate "no link change" with "no design change". Logic changes are documented separately; summarize visual scope and logic scope separately. Read the whole description before planning — don't anchor on the first table.
