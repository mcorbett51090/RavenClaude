#!/usr/bin/env bash
# handoff-spawn.sh — start a FRESH interactive Grok TUI from a run-dir handoff.
#
# Seed is positional grok "<prompt>" only.
# NEVER grok -p / --single / --prompt-file / --prompt-json / /fork.
# Same-host spawn is owner-flagged (context_handoff.spawn: same-host|os-terminal).
# When TERM_PROGRAM=vscode, same-host opens a NEW VS Code terminal — never
# Terminal.app. Copy-paste is ALWAYS printed. --dry-run launches nothing.
#
# After a live launch, wait for successor-ack.json (SessionStart hook).
# This process CANNOT /quit the originating TUI; after ack it tells the
# original session to stop.
#
# bash 3.2-safe.
set -uo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: handoff-spawn.sh --task-id <id> [--dry-run] [--host grok|cli|chat] [--recipe copy-paste|same-host|os-terminal] [--project-root DIR] [--wait-ack-seconds N]
EOF
}

task_id=""
dry_run=0
recipe="copy-paste"
project_root=""
wait_ack=45
host_flag=""

while [ $# -gt 0 ]; do
  case "$1" in
    --task-id) task_id="${2:-}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    --host) host_flag="${2:-}"; shift 2 ;;
    --recipe) recipe="${2:-}"; shift 2 ;;
    --project-root) project_root="${2:-}"; shift 2 ;;
    --wait-ack-seconds) wait_ack="${2:-45}"; shift 2 ;;
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

case "$seed" in
  *"grok -p"*|*"--single"*|*"--prompt-file"*|*"--prompt-json"*)
    echo "handoff-spawn: refuse to emit a forbidden seed" >&2
    exit 2
    ;;
esac

normalize_host() {
  case "$1" in
    grok|grok-tui) echo grok ;;
    cli|copilot-cli|copilot) echo cli ;;
    chat|copilot-chat) echo chat ;;
    "") echo "" ;;
    *) echo unknown ;;
  esac
}

detect_origin_host() {
  local from
  from="$(normalize_host "$host_flag")"
  if [ -n "$from" ] && [ "$from" != "unknown" ]; then
    echo "$from"
    return
  fi
  from="$(normalize_host "${RC_HOST:-}")"
  if [ -n "$from" ] && [ "$from" != "unknown" ]; then
    echo "$from"
    return
  fi
  from="$(normalize_host "${THING_HOST:-}")"
  if [ -n "$from" ] && [ "$from" != "unknown" ]; then
    echo "$from"
    return
  fi
  if [ -n "${GROK_AGENT:-}" ] || [ -n "${GROK_HOOK_EVENT:-}" ] || [ -n "${GROK_SESSION_ID:-}" ]; then
    echo grok
    return
  fi
  if [ -n "${COPILOT_CLI:-}" ] || [ -n "${GITHUB_COPILOT_CLI:-}" ]; then
    echo cli
    return
  fi
  # Never infer chat from TERM_PROGRAM=vscode (also Grok-in-VS-Code).
  echo unknown
}

write_chat_resume() {
  local dest="$project_root/.ravenclaude/runs/$task_id/chat-resume.md"
  cat > "$dest" <<EOF
# Copilot Chat resume — task ${task_id}

Read \`.ravenclaude/runs/${task_id}/handoff.md\` first (then \`meta.json\`, \`decisions.md\`, \`summary.md\` if present).

This is a **new** Chat session. Do not \`/fork\`. Do not reuse the hot thread. Do not launch \`grok\`.

Execute the next steps in the brief.
EOF
  printf '%s\n' "$dest"
}

detect_ui() {
  # Prefer explicit bundle / product env over TERM_PROGRAM=vscode (Cursor,
  # Windsurf, and Grok Desktop also set that).
  case "${__CFBundleIdentifier:-}" in
    com.microsoft.VSCode) echo vscode; return ;;
    com.todesktop.*|dev.zed.Zed) ;;
  esac
  if [ -n "${CURSOR_TRACE_ID:-}" ] || [ -n "${CURSOR_AGENT:-}" ]; then
    echo cursor
    return
  fi
  case "${TERM_PROGRAM:-}" in
    vscode)
      if [ "${__CFBundleIdentifier:-}" = "com.microsoft.VSCode" ]; then
        echo vscode
      elif [ -n "${CURSOR_TRACE_ID:-}" ]; then
        echo cursor
      else
        echo vscode
      fi
      ;;
    iTerm.app) echo iterm ;;
    ghostty) echo ghostty ;;
    Apple_Terminal) echo terminal ;;
    *) echo unknown ;;
  esac
}

ui="$(detect_ui)"
host="$(detect_origin_host)"
chat_resume=""

# vscode without a Grok/CLI marker is not Chat and is not a grok TUI we can prove.
if [ "$host" = "unknown" ] && [ "${TERM_PROGRAM:-}" = "vscode" ]; then
  seed="# host=unknown (TERM_PROGRAM=vscode without Grok/CLI markers) — copy-paste only. Do not launch grok. Do not infer Chat."
fi

if [ "$host" = "chat" ]; then
  chat_resume="$(write_chat_resume)"
  seed="# Read ${chat_resume} and .ravenclaude/runs/${task_id}/handoff.md then continue. Do not /fork. Do not launch grok."
elif [ "$host" = "cli" ]; then
  seed="copilot"
fi

if [ "$host" = "chat" ] || [ "$host" = "cli" ]; then
  case "$seed" in
    *"grok \""*|*"grok -p"*)
      echo "handoff-spawn: refuse to emit a grok seed for host=$host" >&2
      exit 2
      ;;
  esac
fi

copy_paste_block() {
  if [ "$host" = "chat" ]; then
    cat <<EOF
# Copilot Chat resume (same window, NEW session):
# 1. Cmd+N / Ctrl+N  (or Command Palette: "Chat: New Chat")
# 2. Paste the block below  OR  open chat-resume.md / handoff.md via @file
Read .ravenclaude/runs/${task_id}/handoff.md first (then meta.json, decisions.md, summary.md if present). Fresh Chat session. Do not /fork. Do not launch grok. Execute the next steps in the brief.
# file: ${chat_resume:-.ravenclaude/runs/${task_id}/chat-resume.md}
EOF
    return
  fi
  if [ "$host" = "cli" ]; then
    cat <<EOF
# copy-paste into a new terminal in this repo (Copilot CLI, not grok):
cd $(printf '%q' "$project_root")
copilot
# then paste: Continue task ${task_id}. Read .ravenclaude/runs/${task_id}/handoff.md first. Do not /fork. Do not launch grok.
EOF
    return
  fi
  cat <<EOF
# copy-paste into a new terminal in this repo (same app as this session):
cd $(printf '%q' "$project_root")
$seed
EOF
}

spawn_flag=""
posture="$project_root/.ravenclaude/comfort-posture.yaml"
if [ -f "$posture" ]; then
  if grep -E '^[[:space:]]*spawn:[[:space:]]*(same-host|os-terminal)[[:space:]]*$' "$posture" >/dev/null 2>&1; then
    spawn_flag="$(grep -E '^[[:space:]]*spawn:[[:space:]]*(same-host|os-terminal)[[:space:]]*$' "$posture" | awk '{print $2}' | tr -d '\r')"
  fi
fi

case "$recipe" in
  copy-paste|same-host|os-terminal) ;;
  *)
    echo "handoff-spawn: unknown --recipe $recipe" >&2
    copy_paste_block
    exit 2
    ;;
esac

if [ "$recipe" = "same-host" ] || [ "$recipe" = "os-terminal" ]; then
  if [ -z "$spawn_flag" ]; then
    echo "handoff-spawn: same-host/os-terminal spawn is owner-flagged" >&2
    copy_paste_block
    exit 2
  fi
fi

echo "handoff-spawn: detected-ui=$ui host=$host recipe=$recipe spawn-flag=${spawn_flag:-none}"
copy_paste_block

if [ "$dry_run" -eq 1 ]; then
  echo "handoff-spawn: dry-run — not launching, not writing pending"
  if [ "$host" = "chat" ]; then
    echo "handoff-spawn: chat recipe is Cmd+N + paste (best-effort vscode://GitHub.Copilot-Chat/chat?mode=agent)"
  elif [ "$ui" = "vscode" ]; then
    echo "handoff-spawn: vscode recipe would open a new VS Code terminal (not Terminal.app)"
  fi
  echo "$seed"
  exit 0
fi

if [ "$recipe" = "copy-paste" ]; then
  exit 0
fi

run_dir="$project_root/.ravenclaude/runs/$task_id"
pending="$project_root/.ravenclaude/handoff-pending.json"
ack="$run_dir/successor-ack.json"
launch="$run_dir/launch-successor.sh"

# Pending marker the successor SessionStart hook consumes (file write, not stdout).
mkdir -p "$project_root/.ravenclaude"
python3 - "$pending" "$task_id" "$project_root" <<'PY'
import json, sys
from datetime import datetime, timezone
path, task, root = sys.argv[1], sys.argv[2], sys.argv[3]
payload = {
    "task_id": task,
    "project_root": root,
    "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
open(path, "w", encoding="utf-8").write(json.dumps(payload) + "\n")
PY

if [ "$host" = "chat" ]; then
  cat > "$launch" <<EOF
#!/bin/bash
# Chat successor is a new Chat session, not this script.
exit 0
EOF
elif [ "$host" = "cli" ]; then
  cat > "$launch" <<EOF
#!/bin/bash
cd $(printf '%q' "$project_root") || exit 1
exec copilot
EOF
else
  cat > "$launch" <<EOF
#!/bin/bash
cd $(printf '%q' "$project_root") || exit 1
exec $seed
EOF
fi
chmod +x "$launch"

spawn_copilot_chat() {
  # Default live assist: documented agent-mode URI. Does not claim new-session
  # or prefill. Fail → copy-paste already printed; caller exits 0.
  if command -v open >/dev/null 2>&1; then
    open "vscode://GitHub.Copilot-Chat/chat?mode=agent" || return 1
    return 0
  fi
  return 1
}

spawn_vscode_terminal() {
  # VS Code has no CLI to create an integrated terminal and run a command
  # [docs-verified: code --help, 2026-08-14]. Best effort: activate Code and
  # send Ctrl+Shift+` (New Terminal), then run the launch script.
  # Never open Terminal.app from this path.
  command -v osascript >/dev/null 2>&1 || return 1
  osascript <<APPLESCRIPT
tell application "Visual Studio Code" to activate
delay 0.35
tell application "System Events"
  tell process "Code"
    set frontmost to true
    keystroke "\`" using {control down, shift down}
  end tell
end tell
delay 0.55
tell application "System Events"
  tell process "Code"
    keystroke "$(printf '%s' "$launch" | sed 's/\\/\\\\/g; s/"/\\"/g')"
    key code 36
  end tell
end tell
APPLESCRIPT
}

spawn_cursor_terminal() {
  command -v osascript >/dev/null 2>&1 || return 1
  osascript <<APPLESCRIPT
tell application "Cursor" to activate
delay 0.35
tell application "System Events"
  tell process "Cursor"
    set frontmost to true
    keystroke "\`" using {control down, shift down}
  end tell
end tell
delay 0.55
tell application "System Events"
  tell process "Cursor"
    keystroke "$(printf '%s' "$launch" | sed 's/\\/\\\\/g; s/"/\\"/g')"
    key code 36
  end tell
end tell
APPLESCRIPT
}

spawn_terminal_app() {
  command -v open >/dev/null 2>&1 || return 1
  open -na Terminal --args bash -lc "$(printf '%q' "$launch")"
}

launched=0
if [ "$host" = "chat" ]; then
  if spawn_copilot_chat; then
    echo "handoff-spawn: opened vscode://GitHub.Copilot-Chat/chat?mode=agent (best-effort; still Cmd+N for a NEW session)"
    launched=1
  else
    echo "handoff-spawn: Chat live assist missed; copy-paste above is the guaranteed path" >&2
  fi
  rm -f "$pending"
  exit 0
fi

if [ "$recipe" = "same-host" ]; then
  case "$ui" in
    vscode)
      if spawn_vscode_terminal; then
        echo "handoff-spawn: launched in VS Code (new integrated terminal)"
        launched=1
      else
        echo "handoff-spawn: VS Code keystroke launch failed (Accessibility?); copy-paste above" >&2
      fi
      ;;
    cursor)
      if spawn_cursor_terminal; then
        echo "handoff-spawn: launched in Cursor (new integrated terminal)"
        launched=1
      else
        echo "handoff-spawn: Cursor keystroke launch failed; copy-paste above" >&2
      fi
      ;;
    iterm|ghostty|terminal)
      if spawn_terminal_app; then
        echo "handoff-spawn: launched via Terminal.app (detected-ui=$ui)"
        launched=1
      fi
      ;;
    *)
      echo "handoff-spawn: unknown UI; not launching. Use the copy-paste block." >&2
      ;;
  esac
elif [ "$recipe" = "os-terminal" ]; then
  if spawn_terminal_app; then
    echo "handoff-spawn: launched Terminal.app (explicit os-terminal recipe)"
    launched=1
  fi
fi

if [ "$launched" -ne 1 ]; then
  rm -f "$pending"
  if [ "$host" = "cli" ]; then
    exit 0
  fi
  exit 2
fi

# Wait for the successor SessionStart hook to write successor-ack.json.
# Chat does not wait (unverified SessionStart). CLI/Grok may.
if [ "$host" != "chat" ] && [ "$wait_ack" -gt 0 ] 2>/dev/null; then
  n=0
  while [ "$n" -lt "$wait_ack" ]; do
    if [ -s "$ack" ]; then
      echo "SUCCESSOR_ACK $(tr -d '\n' < "$ack")"
      echo "handoff-spawn: successor has the brief and has begun. Stop THIS session. Do not continue the work here. This script cannot /quit the TUI — close this tab when ready."
      exit 0
    fi
    sleep 1
    n=$((n + 1))
  done
  echo "handoff-spawn: no successor-ack.json after ${wait_ack}s (SessionStart hook may not have fired). Copy-paste is still valid." >&2
  exit 0
fi

exit 0
