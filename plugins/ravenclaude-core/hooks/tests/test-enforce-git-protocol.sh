#!/usr/bin/env bash
# Gate 189 — enforce-git-protocol.sh
#
# Proves the DEFAULT-WARN git-protocol hook behaves per spec at off/warn/block,
# that push-to-main is advisory-only (never exit 2), that an absent posture file
# and a read-only git call are no-ops, and — the teeth — that a mutant with the
# block-branch deny neutralized lets a block-knob violation through (so the
# block assertion is measuring the deny, not passing for an unrelated reason).
#
# This test invokes the hook via `bash "$HOOK"`, so it passes regardless of the
# hook's executable bit — that is a property of THIS TEST HARNESS, not of the
# shipped hook. Production (Claude Code direct-exec) and CI's executability gate DO
# require enforce-git-protocol.sh to carry the exec bit; it is handed to the user as
# a `!` chmod (the guarded-substrate dir blocks an agent chmod there).
#
# bash 3.2 safe. No GNU-only tools.
set -uo pipefail

HOOK="$(cd "$(dirname "$0")/.." && pwd)/enforce-git-protocol.sh"
fails=0

T="$(mktemp -d)"
PROJ="$T/proj"; mkdir -p "$PROJ/.ravenclaude"      # a project WITH a posture file
BARE="$T/bare"; mkdir -p "$BARE"                    # a project with NO posture file

_mkpayload() { # $1 = git command string
  python3 -c 'import json,sys
print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1"
}

_set_mode() { printf 'git_protocol: %s\n' "$1" > "$PROJ/.ravenclaude/comfort-posture.yaml"; }

last_exit=0
_run() { # $1=hook $2=projectdir $3=command  -> sets last_exit + $T/err
  printf '%s' "$(_mkpayload "$3")" | CLAUDE_PROJECT_DIR="$2" bash "$1" >/dev/null 2>"$T/err"
  last_exit=$?
}

_assert_exit() { # $1=label $2=want
  if [ "$last_exit" = "$2" ]; then printf '  ok   %-48s exit=%s\n' "$1" "$last_exit"
  else printf '  FAIL %-48s want=%s got=%s\n' "$1" "$2" "$last_exit"; fails=$((fails+1)); fi
}
_assert_silent() { # $1=label — no stderr AND exit 0
  if [ "$last_exit" = "0" ] && [ ! -s "$T/err" ]; then printf '  ok   %-48s (silent, exit 0)\n' "$1"
  else printf '  FAIL %-48s exit=%s err=[%s]\n' "$1" "$last_exit" "$(cat "$T/err")"; fails=$((fails+1)); fi
}
_assert_stderr_has() { # $1=label $2=needle
  if grep -q "$2" "$T/err" 2>/dev/null; then printf '  ok   %-48s (nudge present)\n' "$1"
  else printf '  FAIL %-48s stderr missing "%s": [%s]\n' "$1" "$2" "$(cat "$T/err")"; fails=$((fails+1)); fi
}

echo "Gate 189 — enforce-git-protocol"

# ── warn (default when the posture key is absent-but-file-present, and explicit) ─
_set_mode warn
_run "$HOOK" "$PROJ" 'git commit -m "fixed stuff"'
_assert_exit "commit non-CC @warn"                 0
_assert_stderr_has "commit non-CC @warn nudge"     "Conventional Commits"

_run "$HOOK" "$PROJ" 'git commit -m "fix(hooks): correct the regex"'
_assert_silent "commit CC @warn"

_run "$HOOK" "$PROJ" 'git checkout -b random-name'
_assert_exit "checkout -b off-convention @warn"    0
_assert_stderr_has "branch @warn nudge"            "prefix convention"

_run "$HOOK" "$PROJ" 'git checkout -b fix/thing'
_assert_silent "checkout -b on-convention @warn"

_run "$HOOK" "$PROJ" 'git push origin main'
_assert_exit "push-to-main @warn NEVER blocks"     0
_assert_stderr_has "push-to-main @warn advisory"   "advisory"

_run "$HOOK" "$PROJ" 'git status'
_assert_silent "read-only git status @warn"

_run "$HOOK" "$PROJ" 'git log --oneline -5'
_assert_silent "read-only git log @warn"

# ── block ────────────────────────────────────────────────────────────────────
_set_mode block
_run "$HOOK" "$PROJ" 'git commit -m "fixed stuff"'
_assert_exit "commit non-CC @block DENIES"         2
_assert_stderr_has "commit @block remediation"     "git_protocol: warn"

_run "$HOOK" "$PROJ" 'git checkout -b random-name'
_assert_exit "checkout -b off-convention @block"   2

_run "$HOOK" "$PROJ" 'git commit -m "fix(hooks): correct the regex"'
_assert_silent "commit CC @block still silent"

# git's OWN generated subjects (revert/merge/autosquash) are exempt — never flagged,
# even at block (Fix 1's carve-out: git authored them, so there is no subject to fix).
_run "$HOOK" "$PROJ" 'git commit -m "Revert \"feat: add widget\""'
_assert_silent "git-generated Revert subject @block not flagged"

_run "$HOOK" "$PROJ" "git commit -m \"Merge branch 'topic'\""
_assert_silent "git-generated Merge subject @block not flagged"

_run "$HOOK" "$PROJ" 'git push origin main'
_assert_exit "push-to-main @block NEVER blocks"    0

# ── off => no-op even on a violation ─────────────────────────────────────────
_set_mode off
_run "$HOOK" "$PROJ" 'git commit -m "fixed stuff"'
_assert_silent "commit non-CC @off no-op"

# ── absent posture file => no-op (opt-in) ────────────────────────────────────
_run "$HOOK" "$BARE" 'git commit -m "fixed stuff"'
_assert_silent "absent comfort-posture.yaml no-op"

# ── must-fail half: neuter the block-branch deny, prove the @block teeth ──────
MUT="$T/mutant.sh"
python3 - "$HOOK" "$MUT" <<'MUTPY'
import sys
src = open(sys.argv[1]).read()
# Neuter the ONLY blocking exit (the block branch); everything else identical.
src = src.replace("exit 2   # 2 blocks the tool call",
                  "exit 0   # MUTANT: block deny removed")
open(sys.argv[2], "w").write(src)
MUTPY
_set_mode block
_run "$MUT" "$PROJ" 'git commit -m "fixed stuff"'
if [ "$last_exit" = "0" ]; then
  printf '  ok   %-48s mutant lets the block-violation through\n' "must-fail half (teeth proven)"
else
  printf '  FAIL %-48s mutant still exited %s — the @block test is not measuring the deny\n' \
    "must-fail half" "$last_exit"
  fails=$((fails+1))
fi

echo
if [ "$fails" -eq 0 ]; then echo "Gate 189 PASS"; rm -rf "$T"; exit 0
else echo "Gate 189 FAIL ($fails)"; rm -rf "$T"; exit 1; fi
