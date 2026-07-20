#!/usr/bin/env bash
# Notification hook -> desktop notification via dunst.
# Fires when Claude Code needs permission/approval or has been idle waiting
# for input. Reads the notification JSON on stdin.
msg=$(jq -r '.message // "Claude Code is waiting for your input"')
dunstify -a "Claude Code" -u normal -i dialog-information "Claude Code" "$msg" 2>/dev/null || true
