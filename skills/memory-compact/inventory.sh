#!/usr/bin/env bash
# Read-only inventory for /memory-compact. Prints, per memory file, its type,
# size and the PRs/tickets it mentions (with live GitHub state), then index
# drift, dead path references, stray notes and disk leftovers.
#
# usage: inventory.sh [--memory <dir>] [--repo <owner/name>] [--no-gh]
set -uo pipefail

mem="$HOME/.claude/projects/-home-chris-cit-prog-tiny-repo/memory"
repo="TinyHealth/tiny-repo"
use_gh=1
while [ $# -gt 0 ]; do
  case "$1" in
    --memory) mem="$2"; shift 2 ;;
    --repo) repo="$2"; shift 2 ;;
    --no-gh) use_gh=0; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
cd "$mem" || exit 1

declare -A pr_state
pr() {
  local n="$1"
  if [ -z "${pr_state[$n]+x}" ]; then
    local out="" try
    for try in 1 2 3; do
      out="$(gh pr view "$n" -R "$repo" --json state,mergedAt,title \
        -q '"\(.state) \(.mergedAt // "" | .[0:10]) \(.title | .[0:60])"' 2>/dev/null)" && break
      out=""; sleep 1
    done
    pr_state[$n]="${out:-NOT-FOUND (or another repo)}"
  fi
  printf '%s' "${pr_state[$n]}"
}

echo "# Index"
echo "MEMORY.md: $(wc -c < MEMORY.md) bytes, $(grep -c '^- \[' MEMORY.md) entries"
echo
echo "## Index entries pointing at missing files"
grep -oE '\]\([^)]+\.md\)' MEMORY.md | sed -E 's/^\]\(//; s/\)$//' | while read -r f; do
  [ -f "$f" ] || echo "  $f"
done
echo "## Files not in the index"
for f in *.md; do
  [ "$f" = MEMORY.md ] && continue
  grep -q "($f)" MEMORY.md || echo "  $f"
done
[ -d archive ] && echo "## archive/: $(ls archive | wc -l) files (not indexed, never read)"
echo

echo "# Files (type | bytes | modified | name)"
for f in *.md; do
  [ "$f" = MEMORY.md ] && continue
  type="$(sed -n '1,12p' "$f" | grep -oE '^\s*type:\s*\S+' | head -1 | awk '{print $2}')"
  printf '%-9s %6s  %s  %s\n' "${type:-?}" "$(wc -c < "$f")" "$(date -r "$f" +%F)" "$f"
  tickets="$(grep -oE '\b(ENG|ENGG)-[0-9]{3,5}\b' "$f" | sort -u | tr '\n' ' ')"
  [ -n "$tickets" ] && echo "            tickets: $tickets"
  if [ "$use_gh" -eq 1 ]; then
    for n in $(grep -oE '(PR |PRs? #|#)[0-9]{3,5}\b' "$f" | grep -oE '[0-9]+' | sort -un); do
      echo "            #$n $(pr "$n")"
    done
  fi
done
echo
echo "(PR state is looked up in $repo; a title that does not match means the"
echo " number belongs to another repo, e.g. the IaC repo. Verify those by hand.)"
echo

echo "# Dead path references (~/ or /home paths that do not exist)"
grep -oHE '(~|/home/[a-z0-9_-]+)/[A-Za-z0-9._/-]+' *.md | sort -u | while IFS=: read -r f p; do
  real="${p/#\~/$HOME}"
  real="${real%.}"; real="${real%,}"; real="${real%)}"
  [ -e "$real" ] || echo "  $f -> $p"
done
echo

echo "# Stray notes (loose .md files directly in ~/prog; notes belong in ~/notes/tiny)"
find "$HOME/prog" -maxdepth 1 -type f -name '*.md' -printf '  %p\n'
[ -d "$HOME/notes/tiny" ] || echo "  (~/notes/tiny does not exist)"
echo

echo "# Disk leftovers"
git -C "$HOME/prog/tiny-repo" worktree list | tail -n +2 | sed 's/^/  worktree: /'
ls -d "$HOME"/.claude/projects/-tmp-* 2>/dev/null | sed 's/^/  temp project: /'
echo "  transcripts: $(du -sh "$(dirname "$mem")" | cut -f1) in $(ls "$(dirname "$mem")"/*.jsonl 2>/dev/null | wc -l) sessions"
echo

echo "# Wiki"
wiki="$HOME/wikis/tiny"
echo "  last journal: $(ls "$wiki/journal" 2>/dev/null | tail -1)"
echo "  knowledge notes: $(ls "$wiki/knowledge" 2>/dev/null | grep -vc '^index.md$')"
echo "  projects: $(ls -d "$wiki"/projects/*/ 2>/dev/null | xargs -n1 basename | tr '\n' ' ')"
