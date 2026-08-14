#!/usr/bin/env bash
# Gate 215 — host-paired handoff spawn (Chat / CLI must not emit grok).
#
# --must-fail-chat-grok plants a mutant that emits grok " on --host chat.
set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
SPAWN="$HERE/../scripts/handoff-spawn.sh"
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

out="$(bash "$SPAWN" --task-id demo --project-root "$T/proj" --dry-run --host chat 2>&1)" || true
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

out="$(bash "$SPAWN" --task-id demo --project-root "$T/proj" --dry-run --host cli 2>&1)" || true
_assert_absent "cli dry-run has no grok quote" "$out" 'grok "'
_assert_absent "cli dry-run has no grok -p" "$out" "grok -p"
_assert_contains "cli dry-run names copilot" "$out" "copilot"

out="$(bash "$SPAWN" --task-id demo --project-root "$T/proj" --dry-run 2>&1)" || true
_assert_contains "unset host still grok quote" "$out" 'grok "'

out="$(bash "$SPAWN" --task-id demo --project-root "$T/proj" --dry-run --host chat --recipe same-host 2>&1)" || ec=$?
_assert_contains "chat same-host without flag is owner-flagged" "$out" "owner-flagged"

out="$(TERM_PROGRAM=vscode GROK_AGENT=1 bash "$SPAWN" --task-id demo --project-root "$T/proj" --dry-run 2>&1)" || true
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
  mout="$(bash "$mutant" --task-id demo --project-root "$T/proj" --dry-run --host chat 2>&1 || true)"
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
