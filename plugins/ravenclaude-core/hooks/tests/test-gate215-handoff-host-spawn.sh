#!/usr/bin/env bash
# Gate 215 — host-paired handoff spawn (Chat / CLI must not emit grok).
#
# --must-fail-chat-grok plants a mutant that emits grok " on --host chat.
set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
SPAWN="$HERE/../scripts/handoff-spawn.sh"

# ⛔ THE HOST DETECTOR READS THE AMBIENT ENVIRONMENT — PIN THE WHOLE SURFACE.
# detect_origin_host() in handoff-spawn.sh branches on ELEVEN inherited vars.
# The generic assertions below describe the DEFAULT path, so an unpinned
# invocation measures whoever happens to run it: green on CI (bare env) and RED
# inside any VS Code / Cursor / Grok terminal. That is exactly how Gates 213/215
# shipped passing CI while failing every developer in an integrated terminal
# (TERM_PROGRAM=vscode -> host=unknown -> the script correctly refuses to emit
# `grok "`, and the test asserted it must be present).
# Clearing only TERM_PROGRAM would fix the one that bit and leave ten.
_HOST_ENV_CLEAR=( -u TERM_PROGRAM -u __CFBundleIdentifier -u GROK_AGENT \
                  -u GROK_HOOK_EVENT -u GROK_SESSION_ID -u COPILOT_CLI \
                  -u GITHUB_COPILOT_CLI -u CURSOR_AGENT -u CURSOR_TRACE_ID \
                  -u RC_HOST -u THING_HOST )

# Run the script under test with the detection surface cleared. Leading VAR=val
# arguments are applied AFTER the clear, so a test pins exactly the vars it means
# to exercise and inherits nothing else. (A `VAR=x _spawn` prefix would NOT work
# — the helper's own `env -u` would clear it again.)
_spawn() {
  local pre=()
  while [ $# -gt 0 ]; do
    case "$1" in
      *=*) pre+=("$1"); shift ;;
      *)   break ;;
    esac
  done
  env "${_HOST_ENV_CLEAR[@]}" ${pre[@]+"${pre[@]}"} bash "$SPAWN" "$@"
}

mode="${1:-normal}"
fails=0

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

_assert_contains() {
  case "$2" in
    *"$3"*) printf '  ok   %s\n' "$1" ;;
    *) printf '  FAIL %s (missing: %s)\n' "$1" "$3"; fails=$((fails + 1)) ;;
  esac
}

_assert_absent() {
  case "$2" in
    *"$3"*) printf '  FAIL %s (found: %s)\n' "$1" "$3"; fails=$((fails + 1)) ;;
    *) printf '  ok   %s\n' "$1" ;;
  esac
}

mkdir -p "$T/proj/.ravenclaude/runs/demo"
printf '# brief\n\nDo the next step.\n' > "$T/proj/.ravenclaude/runs/demo/handoff.md"

out="$(_spawn --task-id demo --project-root "$T/proj" --dry-run --host chat 2>&1)" || true
_assert_absent "chat dry-run has no grok quote" "$out" 'grok "'
_assert_absent "chat dry-run has no grok -p" "$out" "grok -p"
_assert_contains "chat dry-run names New Chat" "$out" "New Chat"
_assert_contains "chat dry-run names Cmd+N" "$out" "Cmd+N"
_assert_contains "chat dry-run names chat-resume" "$out" "chat-resume.md"
_assert_absent "chat dry-run does not open Terminal.app" "$out" "open -na Terminal"
[ -s "$T/proj/.ravenclaude/runs/demo/chat-resume.md" ] && printf '  ok   chat-resume.md written\n' || {
  printf '  FAIL chat-resume.md missing\n'
  fails=$((fails + 1))
}

out="$(_spawn --task-id demo --project-root "$T/proj" --dry-run --host cli 2>&1)" || true
_assert_absent "cli dry-run has no grok quote" "$out" 'grok "'
_assert_absent "cli dry-run has no grok -p" "$out" "grok -p"
_assert_contains "cli dry-run names copilot" "$out" "copilot"

out="$(_spawn --task-id demo --project-root "$T/proj" --dry-run 2>&1)" || true
_assert_contains "unset host still grok quote" "$out" 'grok "'

out="$(_spawn --task-id demo --project-root "$T/proj" --dry-run --host chat --recipe same-host 2>&1)" || ec=$?
_assert_contains "chat same-host without flag is owner-flagged" "$out" "owner-flagged"

out="$(_spawn TERM_PROGRAM=vscode GROK_AGENT=1 --task-id demo --project-root "$T/proj" --dry-run 2>&1)" || true
_assert_contains "GROK_AGENT + vscode still grok" "$out" 'grok "'
_assert_absent "GROK_AGENT + vscode is not Chat URI" "$out" "vscode://GitHub.Copilot-Chat"

if [ "$mode" = "--must-fail-chat-grok" ]; then
  mutant="$T/mutant.sh"
  python3 - "$SPAWN" "$mutant" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text()
old = 'if [ "$host" = "chat" ]; then\n  chat_resume="$(write_chat_resume)"\n  seed="# Read ${chat_resume}'
if old not in src:
    raise SystemExit("handoff-spawn.sh drifted — update Gate 215 mutant")
src = src.replace(
    old,
    'if [ "$host" = "chat" ]; then\n  chat_resume="$(write_chat_resume)"\n  seed="grok \\"Continue leaked',
    1,
)
src = src.replace(
    'if [ "$host" = "chat" ] || [ "$host" = "cli" ]; then\n  case "$seed" in\n    *"grok \\""*|*"grok -p"*)\n      echo "handoff-spawn: refuse to emit a grok seed for host=$host" >&2\n      exit 2\n      ;;\n  esac\nfi\n',
    "",
    1,
)
Path(sys.argv[2]).write_text(src)
PY
  chmod +x "$mutant"
  # The MUTANT is a copy of the script under test — pin the same surface.
mout="$(env "${_HOST_ENV_CLEAR[@]}" bash "$mutant" --task-id demo --project-root "$T/proj" --dry-run --host chat 2>&1 || true)"
  case "$mout" in
    *"grok \""*) echo "mutant emitted grok quote as expected"; exit 1 ;;
    *) echo "TEETH FAILED: mutant did not emit grok quote"; echo "$mout"; exit 0 ;;
  esac
fi

bash -n "$SPAWN" || { echo "bash -n spawn failed"; fails=$((fails + 1)); }

if [ "$fails" -eq 0 ]; then
  echo "Gate 215 PASS"
  exit 0
fi
echo "Gate 215 FAIL ($fails)"
exit 1
