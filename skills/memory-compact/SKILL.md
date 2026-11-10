---
name: memory-compact
description: Clean up Claude's memory, notes and wiki. Compact what isn't in use but may be useful, remove what is definitely useless, keep the rest in order. Dry run first; nothing changes until the user approves. Use when the user says "/memory-compact", "clean up memory", "compact memories", or "cleanup session".
---

# Memory compact

Three rules, applied to every memory file, note and doc. The everyday version (what to do
on each memory write) is the `memory-hygiene` memory; keep the two in sync.

1. **Not in use, but useful → compact it.** Finished work keeps its lessons (root causes,
   recipes, traps, decisions and why) as a wiki knowledge note. The memory file goes.
2. **Definitely useless → remove it.** History, PR numbers, SHAs, review rounds, done
   "next steps", wrong facts, duplicates, dead paths, leftover worktrees and temp sessions.
3. **In use → keep it in order.** Rules and live projects stay in memory: short, merged
   by topic, one index line each.

## Where things live

- Memory: `~/.claude/projects/-home-chris-cit-prog-tiny-repo/memory/` (index `MEMORY.md`, loaded every session)
- Wiki: `~/wikis/tiny/` (`knowledge/` + `knowledge/index.md`, `projects/<slug>/`)
- Notes: `~/notes/tiny/` (never inside `~/prog`)

## Steps

1. **Inventory.** Run `~/.claude/skills/memory-compact/inventory.sh`. It lists every memory
   with the live state of the PRs it mentions, plus index drift, dead paths, stray notes
   and disk leftovers. Check tickets without PRs in Linear. Read each file in full
   before judging it; for a big backlog, split the reading across read-only agents.
2. **Plan.** Sort each file by the three rules. Show the user a short before/after
   (file counts, index size, what goes where) and ask for approval.
3. **Apply,** in this order so nothing is lost halfway: write wiki notes → write merged
   memories → delete → rewrite `MEMORY.md` → notes and disk. Re-run the inventory to
   confirm.

## Shape

- **Wiki note:** the template in `~/wikis/tiny/templates/knowledge.md.j2`. One note per
  topic, not per ticket; extend an existing note when one fits. Add it to the index.
- **Live project memory:** what it is, **State** (dated), **Next**, **Pointers**. About 15 lines.
- **Index:** under 8 KB, sections Rules / Reference / Live projects. A line says what the
  memory *is*, never its status. Status lives once, in the file.

## Never touch

Repo `AGENTS.md`/`CLAUDE.md`, `~/prog/tiny-portals/` (credentials, evidence), transcripts
(auto-cleaned). Remove a worktree only if it is clean and its commit is on a remote.

Run every couple of weeks, or when `MEMORY.md` passes 10 KB.
