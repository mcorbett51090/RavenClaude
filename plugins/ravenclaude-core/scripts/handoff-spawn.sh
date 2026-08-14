#!/usr/bin/env bash
# handoff-spawn.sh — start a FRESH interactive Grok TUI from a run-dir handoff.
#
# Seed is positional grok "<prompt>" only.
# NEVER grok -p / --single / --prompt-file / --prompt-json / /fork / SessionStart.
# OS-terminal open is owner-flagged (context_handoff.spawn: os-terminal).
# Copy-paste is ALWAYS printed. --dry-run launches nothing.
#
# bash 3.2-safe.
set -uo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: handoff-spawn.sh --task-id <id> [--dry-run] [--recipe copy-paste|os-terminal] [--project-root DIR]
EOF
}

task_id=""
dry_run=0
recipe="copy-paste"
project_root=""

while [ $# -gt 0 ]; do
  case "$1" in
    --task-id) task_id="${2:-}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    --recipe) recipe="${2:-}"; shift 2 ;;
    --project-root) project_root="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "handoff-spawn: unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [ -z "$task_id" ]; then
  echo "handoff-spawn: --task-id is required" >&2
  exit 2
fi

find_root() {
  local cur
  cur="$(pwd)"
  while [ -n "$cur" ] && [ "$cur" != "/" ]; do
    if [ -d "$cur/.ravenclaude" ] || [ -d "$cur/.git" ]; then
      printf '%s\n' "$cur"
      return 0
    fi
    cur="$(dirname "$cur")"
  done
  pwd
}

if [ -z "$project_root" ]; then
  project_root="$(find_root)"
fi

handoff="$project_root/.ravenclaude/runs/$task_id/handoff.md"
if [ ! -s "$handoff" ]; then
  echo "handoff-spawn: missing or empty $handoff" >&2
  exit 1
fi

seed="grok \"Continue task ${task_id} in this repo. Read .ravenclaude/runs/${task_id}/handoff.md first (then meta.json, decisions.md, summary.md if present). Fresh window. Do not /fork. Do not /compact. Do not re-derive the brief from history you do not have. Execute the next steps in the brief.\""

# Deny-list (positive launch forms). Mentions inside "Do not …" in the seed are ok.
case "$seed" in
  *"grok -p"*|*"--single"*|*"--prompt-file"*|*"--prompt-json"*|*"SessionStart"*)
    echo "handoff-spawn: refuse to emit a forbidden seed" >&2
    exit 2
    ;;
esac

copy_paste_block() {
  cat <<EOF
# copy-paste into a new terminal in this repo:
cd $(printf '%q' "$project_root")
$seed
EOF
}

spawn_flag=""
posture="$project_root/.ravenclaude/comfort-posture.yaml"
if [ -f "$posture" ]; then
  # Uncommented spawn: os-terminal inside a context_handoff block (best-effort).
  if grep -E '^[[:space:]]*spawn:[[:space:]]*os-terminal[[:space:]]*$' "$posture" >/dev/null 2>&1; then
    spawn_flag="os-terminal"
  fi
fi

if [ "$recipe" != "copy-paste" ] && [ "$recipe" != "os-terminal" ]; then
  echo "handoff-spawn: unknown --recipe $recipe" >&2
  copy_paste_block
  exit 2
fi

if [ "$recipe" = "os-terminal" ] && [ "$spawn_flag" != "os-terminal" ]; then
  echo "handoff-spawn: os-terminal spawn is owner-flagged" >&2
  copy_paste_block
  exit 2
fi

copy_paste_block

if [ "$dry_run" -eq 1 ]; then
  echo "handoff-spawn: dry-run — not launching"
  echo "$seed"
  exit 0
fi

if [ "$recipe" = "copy-paste" ] || [ "$spawn_flag" != "os-terminal" ]; then
  exit 0
fi

# Owner-flagged OS-terminal attempt. Inventory is not proof a window opens (C40).
# Prefer `open -na Terminal` on macOS; fail open to copy-paste (already printed).
if command -v open >/dev/null 2>&1; then
  open -na Terminal --args bash -lc "cd $(printf '%q' "$project_root") && $seed" || {
    echo "handoff-spawn: open failed" >&2
    exit 2
  }
  exit 0
fi

echo "handoff-spawn: no OS-terminal recipe available on this host" >&2
exit 2
