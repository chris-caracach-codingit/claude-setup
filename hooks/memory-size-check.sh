#!/usr/bin/env bash
# SessionStart: warn when this project's MEMORY.md index passes 10 KB.
limit=10240
cwd="$(jq -r '.cwd // empty' 2>/dev/null)"
[ -z "$cwd" ] && cwd="$PWD"
dir="$HOME/.claude/projects/$(printf '%s' "$cwd" | sed 's#[/.]#-#g')/memory"
f="$dir/MEMORY.md"
[ -f "$f" ] || exit 0
size=$(wc -c < "$f")
[ "$size" -le "$limit" ] && exit 0
kb=$(( size / 1024 ))
msg="MEMORY.md is ${kb} KB (limit 10 KB). Suggest /memory-compact to the user and follow the memory-hygiene rules."
jq -n --arg m "$msg" '{systemMessage: $m, hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $m}}'
