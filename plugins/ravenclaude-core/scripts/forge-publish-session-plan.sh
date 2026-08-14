#!/usr/bin/env bash
# forge-publish-session-plan.sh — copy FORGE plan.md to the host session plan file.
#
# Grok's exit_plan_mode reads ~/.grok/sessions/<encoded-cwd>/<session-id>/plan.md
# (user-guide 19-plan-mode.md). The FORGE run-dir plan.md is a different file.
# Calling ExitPlanMode without this copy opens "No plan written yet".
#
# bash 3.2-safe. Exit 0 on publish or honest skip (not a Grok session tree).
# Exit 2 if the source is empty or the dest is empty after copy.
set -uo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: forge-publish-session-plan.sh --plan PATH [--session-dir DIR] [--cwd DIR]
EOF
}

plan=""
session_dir=""
cwd=""

while [ $# -gt 0 ]; do
  case "$1" in
    --plan) plan="${2:-}"; shift 2 ;;
    --session-dir) session_dir="${2:-}"; shift 2 ;;
    --cwd) cwd="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "forge-publish-session-plan: unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [ -z "$plan" ]; then
  echo "forge-publish-session-plan: --plan is required" >&2
  exit 2
fi
if [ ! -s "$plan" ]; then
  echo "forge-publish-session-plan: source missing or empty: $plan" >&2
  exit 2
fi

if [ -z "$cwd" ]; then
  cwd="$(pwd)"
fi

if [ -z "$session_dir" ]; then
  grok_home="${GROK_HOME:-$HOME/.grok}"
  enc="$(python3 -c 'import sys; from pathlib import Path; from urllib.parse import quote; print(quote(str(Path(sys.argv[1]).resolve()), safe=""))' "$cwd")"
  group="$grok_home/sessions/$enc"
  if [ ! -d "$group" ]; then
    echo "forge-publish-session-plan: skip (no Grok session group at $group)"
    exit 0
  fi
  if [ -n "${GROK_SESSION_ID:-}" ] && [ -d "$group/$GROK_SESSION_ID" ]; then
    session_dir="$group/$GROK_SESSION_ID"
  else
    # Newest session directory for this cwd (mtime). Agent env usually lacks GROK_SESSION_ID.
    session_dir="$(ls -1td "$group"/*/ 2>/dev/null | head -1 | sed 's:/*$::')"
  fi
  if [ -z "$session_dir" ] || [ ! -d "$session_dir" ]; then
    echo "forge-publish-session-plan: skip (no session dir under $group)"
    exit 0
  fi
fi

dest="$session_dir/plan.md"
if [ -e "$dest" ] && [ ! -f "$dest" ]; then
  echo "forge-publish-session-plan: dest exists and is not a file: $dest" >&2
  exit 2
fi
cp "$plan" "$dest" || {
  echo "forge-publish-session-plan: copy failed → $dest" >&2
  exit 2
}
if [ ! -f "$dest" ] || [ ! -s "$dest" ]; then
  echo "forge-publish-session-plan: dest empty after copy: $dest" >&2
  exit 2
fi
src_bytes="$(wc -c < "$plan" | tr -d ' ')"
dst_bytes="$(wc -c < "$dest" | tr -d ' ')"
if [ "$src_bytes" != "$dst_bytes" ]; then
  echo "forge-publish-session-plan: size mismatch src=$src_bytes dest=$dst_bytes" >&2
  exit 2
fi
echo "FORGE_SESSION_PLAN $dest $dst_bytes"
exit 0
