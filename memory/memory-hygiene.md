---
name: memory-hygiene
description: "How to write and keep memory, notes and wiki so they never drift — the three rules, status in one place, close-out on ticket done"
metadata:
  type: feedback
---

Three rules for every memory, note and doc (Chris, 2026-11-10):

1. **Not in use, but useful → compact it.** When work finishes, its lessons (root causes, recipes, traps, decisions + why) go to a wiki knowledge note in `~/wikis/tiny/knowledge/` (one per topic, extend an existing one when it fits). The memory file is deleted. No `archive/` folder.
2. **Definitely useless → remove it.** PR numbers, SHAs, review rounds, push dates, done "next steps", wrong facts, duplicates, dead paths.
3. **In use → keep it in order.** Memory holds only rules, reference facts and live projects.

**While writing:**
- Status lives **once**, in the file body (`**State (YYYY-MM-DD):**`). Never in the index line or the `description`.
- Index lines say what the memory *is*. Index stays under 8 KB, sections Rules / Reference / Live projects.
- A live project memory is ~15 lines: what it is, State, Next, Pointers. Detail goes to the wiki project page.
- Before writing a new memory, update the one that already covers the topic.
- Working notes go to `~/notes/tiny/`, never `~/prog`.

**Close-out:** when a ticket is done (PR merged, nothing left for Chris), in that same session: move its lessons to the wiki, delete its memory, remove its index line.

**Why:** memory grew to 70 files and a 16 KB index of stale status that contradicted itself across index, description and body (cleanup 2026-11-10).

**How to apply:** follow the rules on every memory write. When `MEMORY.md` passes 10 KB or feels stale, suggest `/memory-compact`. Related: [[wiki-and-notes]].
