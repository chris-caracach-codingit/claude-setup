#!/usr/bin/env bash
# Blind stage of /review-blind: feed a sanitized diff to a fresh claude process
# that has no repo, no memory, no tools and no MCP, and ask it to write the
# ticket the diff implies.
#
# usage: run.sh [--base <ref>] [--with-docs] [--dry-run] [--out <file>]
set -euo pipefail

base="main"
with_docs=0
dry_run=0
out=""
while [ $# -gt 0 ]; do
  case "$1" in
    --base) base="$2"; shift 2 ;;
    --with-docs) with_docs=1; shift ;;
    --out) out="$2"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

repo="$(git rev-parse --show-toplevel)"
merge_base="$(git merge-base "$base" HEAD)"

# Diff only: no commit messages, no branch name, no PR body.
# git pathspec: a bare '*' also matches '/', so '*bun.lock' covers root and nested files.
excludes=(':!*bun.lock' ':!*package-lock.json' ':!*yarn.lock' ':!*pnpm-lock.yaml' ':!*.gen.ts' ':!*.snap')
if [ "$with_docs" -eq 0 ]; then
  excludes+=(':!*.md' ':!*.env.example' ':!*.env.*.example')
fi

work="$(mktemp -d -t review-blind.XXXXXX)"   # outside the repo: no CLAUDE.md, no project memory
git -C "$repo" diff "$merge_base"...HEAD -- . "${excludes[@]}" \
  | sed -E 's/\b[A-Z]{2,6}-[0-9]{2,6}\b/TICKET/g' > "$work/diff.patch"

if [ ! -s "$work/diff.patch" ]; then
  echo "empty diff against $base" >&2; exit 1
fi

if [ "$dry_run" -eq 1 ]; then
  echo "diff: $work/diff.patch ($(wc -l < "$work/diff.patch") lines)"
  grep -E '^diff --git' "$work/diff.patch" | sed 's/^diff --git a\///; s/ b\/.*//'
  exit 0
fi

prompt='Below is a unified diff. You know nothing else about this repository, and you must not assume anything the diff does not show.

1. "Ticket": write the ticket that would have produced exactly this change: title, context (the problem being solved), scope (what changes), out of scope, acceptance criteria that a QA engineer could verify.
2. "Bugs": defects you can see in the diff itself. For each: file, line, the input or situation that triggers it, and what goes wrong. Only list what the diff shows; do not guess at code you cannot see.
3. "Improvements": changes that would make the code simpler, safer or easier to maintain. Dead code, duplicated logic, missing validation, unanchored patterns, names that mislead. File and line for each.
4. "Unjustified": anything in the diff the ticket cannot explain.
5. "Undelivered": anything the ticket implies that the diff does not deliver.
6. "Questions": what you could not decide from the diff alone.

Rank bugs by severity. Use plain prose, short sentences, no em-dashes. Refer to files by path.'

[ -z "$out" ] && out="$work/blind-ticket.md"
(
  cd "$work"
  claude -p --no-session-persistence --tools "" --strict-mcp-config --setting-sources "" \
    --system-prompt "You are a senior engineer reviewing a code change with no other context." \
    "$prompt" < diff.patch
) > "$out"

echo "diff:   $work/diff.patch ($(wc -l < "$work/diff.patch") lines)"
echo "ticket: $out"
