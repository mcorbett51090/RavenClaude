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

# SH-F8: idiomatic unexpanded $(cat <<EOF) multi-line commit — subject is the
# heredoc body, not the literal `$(cat <<EOF` opener. Without the fix this
# false-positive-warns on every agent-authored heredoc commit.
_run "$HOOK" "$PROJ" "$(printf '%s\n' 'git commit -m "$(cat <<EOF' 'feat(hooks): heredoc subject' '' 'body line' 'EOF' ')"')"
_assert_silent "heredoc CC commit @warn (SH-F8)"

# Quoted delimiter form (`<<'EOF'`) — same resolution; body still checked.
_run "$HOOK" "$PROJ" $'git commit -m "$(cat <<\'EOF\'\nfixed stuff in heredoc\nEOF\n)"'
_assert_exit "heredoc non-CC @warn (SH-F8 still checks body)" 0
_assert_stderr_has "heredoc non-CC @warn nudge" "Conventional Commits"

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

# ── hooks-14 (2026-10-19): branch QUERIES are not creations ──────────────────
# A whitelist of creation flags replaced the old exclusion list, which missed
# --merged / --no-merged / --contains / --points-at and DENIED them at block.
for q in 'git branch --merged main' 'git branch --no-merged main' \
         'git branch --contains abc1234' 'git branch --points-at HEAD' \
         'git branch --track' 'git branch -vv' 'git branch --sort=-committerdate' \
         'git branch --merged main --contains abc1234'; do
  _run "$HOOK" "$PROJ" "$q"
  _assert_silent "query @block not a creation: $q"
done
for c in 'git branch random-name' 'git branch --track topic origin/topic' \
         'git branch -t topic origin/topic' 'git branch -q topic main'; do
  _run "$HOOK" "$PROJ" "$c"
  _assert_exit "real creation @block still flags: $c" 2
done
_run "$HOOK" "$PROJ" 'git branch --track fix/thing origin/fix/thing'
_assert_silent "on-convention creation with --track @block"
MUT14="$T/mutant14.sh"
python3 - "$HOOK" "$MUT14" <<'MUTPY'
import sys
src = open(sys.argv[1]).read()
old = "        if any(f not in create_flags for f in flags):\n            return None\n"
if old not in src:
    sys.exit(2)
open(sys.argv[2], "w").write(src.replace(old, "", 1))
MUTPY
_run "$MUT14" "$PROJ" 'git branch --merged main'
if [ "$last_exit" = "2" ]; then
  printf '  ok   %-48s mutant denies the query again\n' "hooks-14 teeth"
else
  printf '  FAIL %-48s mutant exited %s — the query assertions are not measuring the whitelist\n' \
    "hooks-14 teeth" "$last_exit"
  fails=$((fails+1))
fi

# ── hooks-15 (2026-10-19): the warn nudge reaches the MODEL, not just the tty ─
# stderr at exit 0 is not delivered to the model (measured, _advise.sh); the warn
# lane now also emits additionalContext on stdout. Block stays a bare exit 2.
_run_out() { # like _run, but keeps stdout in $T/out
  printf '%s' "$(_mkpayload "$3")" | CLAUDE_PROJECT_DIR="$2" bash "$1" >"$T/out" 2>"$T/err"
  last_exit=$?
}
_ctx() { python3 -c 'import json,sys
try: print(json.load(open(sys.argv[1]))["hookSpecificOutput"]["additionalContext"])
except Exception: pass' "$T/out"; }
_set_mode warn
_run_out "$HOOK" "$PROJ" 'git commit -m "fixed stuff"'
if [ "$last_exit" = "0" ] && _ctx | grep -q "Conventional Commits" && grep -q "Conventional Commits" "$T/err"; then
  printf '  ok   %-48s additionalContext + terminal notice\n' "hooks-15 warn reaches the model"
else
  printf '  FAIL %-48s exit=%s out=[%s]\n' "hooks-15 warn reaches the model" "$last_exit" "$(cat "$T/out")"
  fails=$((fails+1))
fi
_set_mode block
_run_out "$HOOK" "$PROJ" 'git commit -m "fixed stuff"'
if [ "$last_exit" = "2" ] && [ ! -s "$T/out" ]; then
  printf '  ok   %-48s exit 2, no helper JSON\n' "hooks-15 block path unchanged"
else
  printf '  FAIL %-48s exit=%s out=[%s]\n' "hooks-15 block path unchanged" "$last_exit" "$(cat "$T/out")"
  fails=$((fails+1))
fi
MUT15="$T/mutant15.sh"
python3 - "$HOOK" "$MUT15" <<'MUTPY'
import sys
src = open(sys.argv[1]).read()
old = 'rc_advise_init PreToolUse 0; fi'
if old not in src:
    sys.exit(2)
open(sys.argv[2], "w").write(src.replace(old, ':; fi', 1))
MUTPY
_set_mode warn
_run_out "$MUT15" "$PROJ" 'git commit -m "fixed stuff"'
if [ ! -s "$T/out" ]; then
  printf '  ok   %-48s mutant emits nothing to the model\n' "hooks-15 teeth"
else
  printf '  FAIL %-48s mutant still emitted [%s]\n' "hooks-15 teeth" "$(cat "$T/out")"
  fails=$((fails+1))
fi

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
