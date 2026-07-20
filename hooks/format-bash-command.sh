#!/usr/bin/env bash
# PreToolUse hook (matcher: Bash). Reads the tool input JSON on stdin and
# returns a systemMessage that lists each command on its own line, with the
# command name in bold cyan and the arguments dimmed.
set -euo pipefail

cmd=$(jq -r '.tool_input.command // empty')
[ -z "$cmd" ] && exit 0

C=$'\033[1;36m' # bold cyan: command name
D=$'\033[2m'    # dim: arguments
R=$'\033[0m'    # reset

if printf '%s' "$cmd" | grep -q '<<'; then
  # Heredocs would be mangled by line splitting; show verbatim.
  body="❯ $cmd"
else
  body=$(printf '%s\n' "$cmd" |
    sed -E 's/[[:space:]]+(&&|\|\|);?[[:space:]]+/\n/g; s/;[[:space:]]+/\n/g' |
    awk -v c="$C" -v d="$D" -v r="$R" 'NF {
      rest = $0
      sub(/^[[:space:]]*[^[:space:]]+[[:space:]]*/, "", rest)
      if (rest == "") printf "❯ %s%s%s\n", c, $1, r
      else printf "❯ %s%s%s %s%s%s\n", c, $1, r, d, rest, r
    }')
fi

# Leading newline pushes the list below the "PreToolUse:Bash says:" prefix.
jq -n --arg m "$body" '{systemMessage: ("\n" + $m)}'
