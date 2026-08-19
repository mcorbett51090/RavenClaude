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
Usage: handoff-spawn.sh --task-id <id> [--dry-run] [--host HOST] [--recipe copy-paste|same-host|os-terminal] [--project-root DIR] [--wait-ack-seconds N]

  --host  claude-code | grok | cli (Copilot CLI) | chat (Copilot Chat)
            -> that host's own launch recipe.
          codex | cursor | gemini | aider | windsurf   (knowledge/host-support.json)
          other | generic
            -> host-neutral copy-paste block, exit 0. No launch command is invented.
          anything else
            -> the copy-paste block, then exit 2. Pass `other`, never a host you are not.
EOF
}

task_id=""
dry_run=0
recipe="copy-paste"
project_root=""
wait_ack=45
host_flag=""
host_flag_seen=0
host_flag_bad=0

# ⛔ `shift 2` WHEN THE FLAG IS THE LAST ARGUMENT DOES NOT SHIFT AT ALL.
# bash reports "shift count out of range" and returns non-zero; $# never
# decreases and this loop spins forever at 100% CPU. Measured 2026-08-19 through
# the DOCUMENTED shape (`rc handoff … --host $H` with H empty, per
# commands/handoff.md): 0 bytes emitted, still running at 5 s, killed by SIGALRM
# (exit 142). Control, same command with a value: exit 0, 443 bytes. Every
# value-taking flag now shifts ONCE, then again only if an argument remains.
#
# A value that is missing, empty, or itself a `--flag` is a CALLER ERROR, not a
# value. For --host it is RECORDED here and rejected later (see the D2 block,
# after copy_paste_block is defined) so the file-header invariant "Copy-paste is
# ALWAYS printed" survives. For the other four it is fatal here, matching the two
# argument errors that already exit 2 without a block: the `unknown arg` arm
# below and the --task-id check.
#
# ⛔ Do NOT "uniformise" --wait-ack-seconds to `${2:-}`. Its default of 45 is
# load-bearing: `[ "$wait_ack" -gt 0 ] 2>/dev/null` is false on an empty string,
# which SILENTLY skips the successor-ack wait — the handshake dies with no error.
while [ $# -gt 0 ]; do
  case "$1" in
    --task-id)
      case "${2:-}" in
        ""|--*) echo "handoff-spawn: --task-id requires a value" >&2; usage; exit 2 ;;
        *) task_id="$2" ;;
      esac
      shift; if [ $# -gt 0 ]; then shift; fi ;;
    --dry-run) dry_run=1; shift ;;
    --host)
      host_flag_seen=1
      # ⛔ THE TWO BAD SHAPES NEED DIFFERENT SHIFT BEHAVIOUR, AND COLLAPSING THEM
      # BREAKS AC-2. `--host --dry-run` must NOT consume its "value": the flag has
      # to be re-parsed as a flag (MED-8 — otherwise a dry run silently becomes a
      # live launch). But `--host ""` must consume the empty token, or it falls to
      # the `*)` unknown-arg arm below and exits 2 with the USAGE string and NO
      # copy-paste block. Measured 2026-08-19 with a single shared guard:
      #   --host ''  -> EXIT=2 BYTES=609 "unknown arg:" + usage, block absent
      # AC-2 requires the block before any D2 exit 2, so only a `--*` value skips
      # the second shift. Trailing `--host` is safe either way: after the first
      # shift $# is 0 and the guarded shift is a no-op.
      host_flag_isflag=0
      case "${2:-}" in
        --*) host_flag_bad=1; host_flag_isflag=1 ;;
        "") host_flag_bad=1 ;;
        *) host_flag="$2" ;;
      esac
      shift
      if [ "$host_flag_isflag" -eq 0 ] && [ $# -gt 0 ]; then shift; fi ;;
    --recipe)
      case "${2:-}" in
        ""|--*) echo "handoff-spawn: --recipe requires a value" >&2; usage; exit 2 ;;
        *) recipe="$2" ;;
      esac
      shift; if [ $# -gt 0 ]; then shift; fi ;;
    --project-root)
      case "${2:-}" in
        ""|--*) echo "handoff-spawn: --project-root requires a value" >&2; usage; exit 2 ;;
        *) project_root="$2" ;;
      esac
      shift; if [ $# -gt 0 ]; then shift; fi ;;
    --wait-ack-seconds)
      case "${2:-}" in
        ""|--*) echo "handoff-spawn: --wait-ack-seconds requires a value" >&2; usage; exit 2 ;;
        *) wait_ack="$2" ;;
      esac
      shift; if [ $# -gt 0 ]; then shift; fi ;;
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

# ⛔ TWO DIFFERENT SITUATIONS WEAR THE SAME `unknown` LABEL, AND ONLY ONE IS A BUG.
#
#   (a) NOTHING was asked for and nothing was detected. This script exists to
#       "start a FRESH interactive Grok TUI" (see the header), and the
#       session-handoff skill records that Grok's own markers are unreliable
#       inside the agent process — "Detection is hook-only". So a REAL Grok
#       session can fail detection, and this grok-first fallback is what carries
#       it. Gate 215 pins that deliberately ("unset host still grok"). It is NOT
#       the defect, and it is left exactly as it was.
#
#   (b) A host WAS named and this script does not know the name (`--host codex`).
#       Falling back to grok there is never right: the caller told us who the
#       successor is, and we answered with a different agent's launch command.
#
# The reported failure was (b) wearing (a)'s clothes: `claude-code` was not a
# recognised name, so an EXPLICIT `--host claude-code` collapsed to `unknown`
# and inherited this fallback. Measured 2026-08-18 against the shipped 0.271.4
# copy: `--host claude-code` in a plain terminal printed `grok "…"`, while the
# SAME invocation under TERM_PROGRAM=vscode printed the safe comment below —
# which is why the defect reads as absent from inside VS Code. The live path was
# worse than the printed one: the launch-successor writer's final `else` did
# `exec $seed`, so it would have LAUNCHED the wrong agent, not merely named it.
#
# Fix: teach it `claude-code`, and refuse this fallback for case (b) only.
seed="grok \"Continue task ${task_id} in this repo. Read .ravenclaude/runs/${task_id}/handoff.md first (then meta.json, decisions.md, summary.md if present). Fresh window. Do not /fork. Do not /compact. Do not re-derive the brief from history you do not have. Execute the next steps in the brief.\""

case "$seed" in
  *"grok -p"*|*"--single"*|*"--prompt-file"*|*"--prompt-json"*)
    echo "handoff-spawn: refuse to emit a forbidden seed" >&2
    exit 2
    ;;
esac

_lc() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'
}

# ⛔ CASE AND SURROUNDING WHITESPACE ARE NORMALISED HERE BECAUSE
# context-handoff.py's _normalize_handoff_host ALREADY DOES `.strip().lower()`,
# and the two write the seed for the SAME handoff (see detect_origin_host below).
# Measured 2026-08-19 before this change:
#   --host GROK        -> bash `unknown`  / python a LIVE `grok "…"` seed
#   --host CLAUDE-CODE -> bash `unknown`  / python the claude recipe
#   --host Chat / CLI  -> bash `unknown`  / python the correct chat / cli seed
# bash was the stricter half, so the pair named different successors on four
# inputs. `${var,,}` is bash 4.0+; this file is bash 3.2-safe, hence tr.
normalize_host() {
  local h
  h="$(_lc "$1")"
  case "$h" in
    grok|grok-tui) echo grok ;;
    cli|copilot-cli|copilot) echo cli ;;
    chat|copilot-chat) echo chat ;;
    claude-code|claude|claudecode) echo claude-code ;;
    "") echo "" ;;
    *) echo unknown ;;
  esac
}

# The seven hosts the marketplace officially declares in
# knowledge/host-support.json. Duplicated as a literal ON PURPOSE: Gate 230 and
# Gate 234 drive this script under `env -i PATH=/usr/bin:/bin`, so it may not
# shell out to python3/jq to read the JSON. Gate 234 asserts this list and the
# JSON agree, so the duplication cannot drift silently. Same pattern as
# _read_heimdall / _read_mimir elsewhere in this plugin.
is_registry_host() {
  case "$(_lc "$1")" in
    claude-code|copilot|codex|cursor|gemini|aider|windsurf) return 0 ;;
    *) return 1 ;;
  esac
}

# ⛔ D2, owner ruling 2026-08-19. Three classes, not two:
#   recipe  — we have a launch command for it.
#   neutral — a host this marketplace officially supports, or an explicit
#             `other`, for which we have NO launch command. Host-neutral
#             copy-paste, exit 0. Measured as the WORKING behaviour before this
#             change (`--host codex` exits 0 with the neutral block) and
#             deliberately retained: hard-erroring here would destroy a working
#             handoff for five supported hosts AND pressure an agent on an
#             unlisted host into picking the nearest recognised token — almost
#             certainly `cli` — which is the wrong-vendor failure this file
#             exists to prevent.
#   reject  — a name in neither vocabulary. A typo. The copy-paste block is
#             printed and then this exits 2.
classify_host_flag() {
  local n
  n="$(normalize_host "$1")"
  if [ -n "$n" ] && [ "$n" != "unknown" ]; then echo recipe; return; fi
  case "$(_lc "$1")" in
    other|generic) echo neutral; return ;;
  esac
  if is_registry_host "$1"; then echo neutral; return; fi
  echo reject
}

detect_origin_host() {
  local from
  # ⛔ AN EXPLICIT --host IS THE WHOLE ANSWER, INCLUDING WHEN WE DO NOT KNOW THE
  # NAME. This used to fall THROUGH to environment detection whenever the flag
  # did not normalise to a recipe host, so with CLAUDECODE set `--host codex`
  # printed a CLAUDE CODE recipe (measured 2026-08-18, claims-table row 8) and
  # `--host <typo>` printed whatever the ambient session happened to be. That
  # fall-through is the mechanism behind the whole defect class this file
  # documents at the top: the caller told us who the successor is, and we
  # answered with a different agent's launch command. Control that the flag is
  # still honoured, not merely disabled: `--host cli` under the same env still
  # emits the Copilot CLI recipe.
  if [ "$host_flag_seen" -eq 1 ]; then
    from="$(normalize_host "$host_flag")"
    if [ -n "$from" ] && [ "$from" != "unknown" ]; then
      echo "$from"
    else
      echo unknown
    fi
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
  # Same markers context-handoff.py's detect_host() already keys on. Kept in
  # step with it deliberately: the two scripts write the seed for the SAME
  # handoff, so a host either resolves in both or the pair disagrees about who
  # the successor is.
  if [ -n "${CLAUDECODE:-}" ] || [ -n "${CLAUDE_CODE_ENTRYPOINT:-}" ]; then
    echo claude-code
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

# Case (b) from the comment above: a host was NAMED and we do not know the name.
# This is the only thing that distinguishes it from case (a) at this point —
# both end up as host=unknown, and conflating them is exactly what shipped.
# One bit, three sources. It is set when a successor WAS named and we cannot
# name a launch command for it:
#   (i)   --host <registry host | other | typo>            -> host_flag_seen
#   (ii)  --host with a missing / empty / --flag value     -> host_flag_seen
#   (iii) RC_HOST / THING_HOST naming a host we do not know
#
# (iii) is new and was measured 2026-08-19: `THING_HOST=gemini` with no flag
# emitted a LIVE `grok "…"` launch for a session that had named itself gemini,
# because this test keyed on $host_flag only. Every existing gate clears
# THING_HOST (`-u THING_HOST`, or `env -i`), which is correct hygiene for the
# flag rows and is exactly why no gate could see it. Gate 234 row 21 drives it,
# with a THING_HOST=grok control on row 22 proving grok still keeps its own seed.
named_but_unknown=0
if [ "$host" = "unknown" ] && { [ "$host_flag_seen" -eq 1 ] || [ -n "${RC_HOST:-}" ] || [ -n "${THING_HOST:-}" ]; }; then
  named_but_unknown=1
fi

# vscode without a Grok/CLI marker is not Chat and is not a grok TUI we can prove.
if [ "$host" = "unknown" ] && [ "${TERM_PROGRAM:-}" = "vscode" ]; then
  seed="# host=unknown (TERM_PROGRAM=vscode without Grok/CLI markers) — copy-paste only. Do not launch grok. Do not infer Chat."
fi

if [ "$host" = "grok" ]; then
  seed="grok \"Continue task ${task_id} in this repo. Read .ravenclaude/runs/${task_id}/handoff.md first (then meta.json, decisions.md, summary.md if present). Fresh window. Do not /fork. Do not /compact. Do not re-derive the brief from history you do not have. Execute the next steps in the brief.\""
elif [ "$host" = "chat" ]; then
  chat_resume="$(write_chat_resume)"
  seed="# Read ${chat_resume} and .ravenclaude/runs/${task_id}/handoff.md then continue. Do not /fork. Do not launch grok."
elif [ "$host" = "cli" ]; then
  seed="copilot"
elif [ "$host" = "claude-code" ]; then
  seed="claude"
elif [ "$named_but_unknown" -eq 1 ]; then
  # Case (b). Do NOT reach for the grok fallback — the caller named a successor
  # and it is not grok. Host-neutral text is correct on every host, including
  # ones that do not exist yet.
  seed="# Read .ravenclaude/runs/${task_id}/handoff.md and continue in a NEW session of THIS host. Do not /fork. Do not /compact. Do not launch grok."
fi

case "$seed" in
  *"grok -p"*|*"--single"*|*"--prompt-file"*|*"--prompt-json"*)
    echo "handoff-spawn: refuse to emit a forbidden seed" >&2
    exit 2
    ;;
esac

# ⛔ THE TEETH. This was scoped to chat|cli, so it could not see the case it most
# needed to catch: a NAMED host we did not recognise inheriting the grok
# fallback. It now covers every host we were told about — chat, cli,
# claude-code, and any name we do not know — while leaving case (a) (nothing
# named, nothing detected) on the grok-first default Gate 215 pins.
if [ "$host" != "grok" ] && { [ "$host" != "unknown" ] || [ "$named_but_unknown" -eq 1 ]; }; then
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
  if [ "$host" = "claude-code" ]; then
    cat <<EOF
# copy-paste into a new terminal in this repo (Claude Code, not grok):
cd $(printf '%q' "$project_root")
claude
# then paste: Continue task ${task_id}. Read .ravenclaude/runs/${task_id}/handoff.md first. Fresh window — do not /fork, do not /compact, do not launch grok.
EOF
    return
  fi
  cat <<EOF
# copy-paste into a new terminal in this repo (same app as this session):
cd $(printf '%q' "$project_root")
$seed
EOF
}

# ⛔ D2 — REFUSE A NAME WE DO NOT KNOW; NEVER REFUSE A HOST WE SUPPORT.
#
# Owner ruling 2026-08-19 (G5): a host declared in knowledge/host-support.json
# but with no launch recipe here — codex / cursor / gemini / aider / windsurf —
# resolves to the HOST-NEUTRAL block and exits 0. That was measured as the
# working behaviour BEFORE this change and is deliberately retained. Only a name
# in neither vocabulary is fatal, and `other` is always available as a truthful
# value for a host that is in neither.
#
# ⛔ WHY THE BLOCK IS PRINTED BEFORE THE EXIT, AND WHY THIS SITS HERE AND NOT UP
# BY THE ARGUMENT LOOP. The file header states "Copy-paste is ALWAYS printed",
# and both existing fatal branches below (unknown --recipe, unflagged same-host)
# call copy_paste_block and THEN exit 2. Validating up beside the argument loop
# reads cleaner and is what the first draft specified — it cannot print the
# block, because the block needs $host, $seed and $project_root, none of which
# exist that early. The invariant wins: a user at a full context window who
# mistypes a host name must still get something to paste.
#
# $seed is host-neutral text on both paths below, because named_but_unknown is 1
# in both — see its assignment above. That is what stops a malformed --host from
# falling to case (a) and printing a grok launch.
if [ "$host_flag_bad" -eq 1 ]; then
  echo "handoff-spawn: --host requires a value. Pass claude-code | grok | cli | chat | a host-support.json name | other." >&2
  copy_paste_block
  exit 2
fi
if [ "$host_flag_seen" -eq 1 ] && [ "$(classify_host_flag "$host_flag")" = "reject" ]; then
  echo "handoff-spawn: unrecognised --host '$host_flag'. Use claude-code | grok | cli | chat, a host from knowledge/host-support.json (codex|cursor|gemini|aider|windsurf), or 'other' for a host-neutral handoff. Do NOT substitute a host you are not." >&2
  copy_paste_block
  exit 2
fi

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
elif [ "$host" = "claude-code" ]; then
  cat > "$launch" <<EOF
#!/bin/bash
cd $(printf '%q' "$project_root") || exit 1
exec claude
EOF
elif [ "$host" = "grok" ] || { [ "$host" = "unknown" ] && [ "$named_but_unknown" -eq 0 ]; }; then
  # host=grok, or case (a): nothing named and nothing detected, which the
  # grok-first fallback carries (see the seed comment). $seed is the grok
  # command in both, so exec-ing it is the documented behaviour, unchanged.
  cat > "$launch" <<EOF
#!/bin/bash
cd $(printf '%q' "$project_root") || exit 1
exec $seed
EOF
else
  # ⛔ CASE (b): A NAMED HOST WE DO NOT KNOW ⇒ LAUNCH NOTHING. This branch was a
  # bare `else` doing `exec $seed`, and $seed was the grok command, so a named
  # non-grok host got a script that LAUNCHES a different agent. Copy-paste has
  # already been printed; a successor a human starts beats one this script
  # guesses at. $seed is host-neutral text here and is not executable anyway.
  cat > "$launch" <<EOF
#!/bin/bash
# host=$host — no proven same-host launch recipe. Use the copy-paste block.
exit 0
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
