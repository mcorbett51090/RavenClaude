#!/usr/bin/env bash
# Gate 213 — handoff-spawn.sh
#
# Copy-paste is the guaranteed path. Positional grok seed only.
# --must-fail-headless plants a mutant that emits `grok -p`; the deny assertion
# must catch it.
set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
SPAWN="$HERE/../scripts/handoff-spawn.sh"
mode="${1:-normal}"
fails=0

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

mkdir -p "$T/proj/.ravenclaude/runs/demo"
printf 'not a brief' > "$T/proj/.ravenclaude/runs/demo/empty-placeholder"
# missing handoff
out="$(bash "$SPAWN" --task-id demo --project-root "$T/proj" --dry-run 2>&1 || true)"
ec=$?
# recreate properly
rm -rf "$T/proj/.ravenclaude/runs/demo"
mkdir -p "$T/proj/.ravenclaude/runs/missing"

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

# missing handoff → exit 1, no grok argv
out="$(bash "$SPAWN" --task-id missing --project-root "$T/proj" --dry-run 2>&1)" || ec=$?
if [ "${ec:-0}" -eq 1 ]; then
  printf '  ok   missing handoff exits 1\n'
else
  printf '  FAIL missing handoff exit=%s\n' "${ec:-0}"
  fails=$((fails + 1))
fi
_assert_absent "missing handoff does not print grok argv" "$out" 'grok "'

mkdir -p "$T/proj/.ravenclaude/runs/demo"
printf '# brief\n\nDo the next step.\n' > "$T/proj/.ravenclaude/runs/demo/handoff.md"

out="$(bash "$SPAWN" --task-id demo --project-root "$T/proj" --dry-run 2>&1)" || true
_assert_contains "dry-run prints grok quote" "$out" 'grok "'
_assert_contains "dry-run names the run dir" "$out" ".ravenclaude/runs/demo/handoff.md"
_assert_absent "no grok -p" "$out" "grok -p"
_assert_absent "no --single" "$out" "--single"
_assert_absent "no --prompt-file" "$out" "--prompt-file"
_assert_absent "no --prompt-json" "$out" "--prompt-json"
_assert_absent "no SessionStart" "$out" "SessionStart"
_assert_contains "copy-paste block present" "$out" "copy-paste"

# os-terminal / same-host without owner flag
out="$(bash "$SPAWN" --task-id demo --project-root "$T/proj" --dry-run --recipe os-terminal 2>&1)" || ec=$?
_assert_contains "os-terminal without flag is refused" "$out" "owner-flagged"
_assert_absent "default never execs open" "$out" "open -na"

printf 'schema_version: 5\ncontext_handoff:\n  mode: nag\n  spawn: same-host\n' > "$T/proj/.ravenclaude/comfort-posture.yaml"
out="$(TERM_PROGRAM=vscode __CFBundleIdentifier=com.microsoft.VSCode \
  bash "$SPAWN" --task-id demo --project-root "$T/proj" --dry-run --recipe same-host 2>&1)" || true
_assert_contains "same-host dry-run names vscode" "$out" "detected-ui=vscode"
_assert_contains "same-host dry-run says VS Code terminal" "$out" "VS Code terminal"
_assert_absent "vscode recipe never uses Terminal.app" "$out" "open -na Terminal"

if [ "$mode" = "--must-fail-headless" ]; then
  mutant="$T/mutant.sh"
  python3 - "$SPAWN" "$mutant" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text()
old = 'seed="grok \\"Continue task ${task_id}'
if old not in src:
    raise SystemExit("handoff-spawn.sh drifted — update Gate 213 mutant")
src = src.replace(old, 'seed="grok -p \\"Continue task ${task_id}', 1)
# also neuter the deny-list so the mutant actually emits it
src = src.replace('*"grok -p"*|', "")
Path(sys.argv[2]).write_text(src)
PY
  chmod +x "$mutant"
  mout="$(bash "$mutant" --task-id demo --project-root "$T/proj" --dry-run 2>&1 || true)"
  case "$mout" in
    *"grok -p"*) echo "mutant emitted grok -p as expected"; exit 1 ;;
    *) echo "TEETH FAILED: mutant did not emit grok -p"; exit 0 ;;
  esac
fi

bash -n "$SPAWN" || { echo "bash -n spawn failed"; fails=$((fails + 1)); }

if [ "$fails" -eq 0 ]; then
  echo "Gate 213 PASS"
  exit 0
fi
echo "Gate 213 FAIL ($fails)"
exit 1
