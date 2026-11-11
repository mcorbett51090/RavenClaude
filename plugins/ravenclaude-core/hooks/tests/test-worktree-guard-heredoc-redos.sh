#!/usr/bin/env bash
# test-worktree-guard-heredoc-redos.sh — AppSec N1 (SHIPCHECK on RavenClaude#1423):
# worktree-guard-bash.py must fail CLOSED on a pathological heredoc input instead
# of stalling past Claude Code's PreToolUse default (fail open). Covers:
#   (a) hard input cap (64 KiB, or more than 256 "<<" markers) → exit 3
#   (b) line-based linear scanner: 1 MiB unterminated padding finishes fast
#   (c) signal.alarm self-timeout → exit 4 (also confirmed via the hook)
# plus a normal F1 repro still denied quickly, and the documented allow controls.
#
# Door 5 (scripts/check-macos-portability.sh, bash 3.2): this file never nests
# a here-doc-shaped `<<TAG` span inside `$( )`. The two-character sequence "<<"
# is kept out of source text by routing it through ${_HD} or chr(60)*2 in a
# top-level (not command-substituted) Python helper. Run/j-style `$( )` only
# interpolates a variable name or reads a file.
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-worktree-guard-heredoc-redos.sh

set -uo pipefail

HOOKS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PY="$HOOKS_DIR/worktree-guard-bash.py"
HOOK="$HOOKS_DIR/worktree-guard.sh"

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
ROOT="$T/worktree"
mkdir -p "$ROOT"

# Literal "<<" is never written as source text (Door 5).
_HD="$(python3 -c 'import sys; sys.stdout.write(chr(60)*2)')"

PASS=0
FAIL=0
# Pathological inputs must finish well under the 5 s alarm; 2 s is already generous.
_BUDGET_SECS=2

run_file() { # name want file
  local name="$1" want="$2" file="$3" got start end elapsed
  start="$(python3 -c 'import time; print(time.monotonic())')"
  python3 "$PY" "$ROOT" "$ROOT" <"$file" >"$T/out" 2>"$T/err"
  got=$?
  end="$(python3 -c 'import time; print(time.monotonic())')"
  elapsed="$(python3 -c "print({end}-{start})" 2>/dev/null || python3 -c "print(float('$end')-float('$start'))")"
  if [ "$got" = "$want" ]; then
    PASS=$((PASS + 1))
    printf '  \033[32m✓\033[0m %s (rc=%s, %.3fs)\n' "$name" "$got" "$elapsed"
  else
    FAIL=$((FAIL + 1))
    printf '  \033[31m✗\033[0m %s want=%s got=%s (%.3fs): %s %s\n' \
      "$name" "$want" "$got" "$elapsed" "$(head -c200 "$T/out")" "$(head -c200 "$T/err")"
  fi
  # Timing budget is part of the assertion for the named pathological cases.
  case "$name" in
    cap-*|pathological-*|f1-repro-fast)
      python3 -c "import sys; sys.exit(0 if float('$elapsed') < $_BUDGET_SECS else 1)"
      if [ $? -ne 0 ]; then
        FAIL=$((FAIL + 1))
        printf '  \033[31m✗\033[0m %s too slow: %.3fs (budget %ss)\n' "$name" "$elapsed" "$_BUDGET_SECS"
        # The rc assertion already counted as a pass above if want matched — retract it.
        PASS=$((PASS - 1))
      fi
      ;;
  esac
}

echo
echo "── AppSec N1 — input cap fails closed (exit 3, reason too large to parse) ──"

# Exactly 64 KiB of non-write text must still parse (exit 0).
python3 - "$T/cap-eq" <<'PY'
import sys
open(sys.argv[1], "w").write("x" * (64 * 1024))
PY
run_file cap-at-64kib-still-parses 0 "$T/cap-eq"

# One character over the cap.
python3 - "$T/cap-over" <<'PY'
import sys
open(sys.argv[1], "w").write("x" * (64 * 1024 + 1))
PY
run_file cap-over-64kib 3 "$T/cap-over"
if [ "$FAIL" -eq 0 ] || grep -q "too large to parse" "$T/out"; then
  if grep -q "too large to parse" "$T/out"; then
    PASS=$((PASS + 1)); printf '  \033[32m✓\033[0m cap-over-64kib reason is "too large to parse"\n'
  else
    # Only flag if the rc test already passed; otherwise the rc failure is enough.
    if grep -q 'cap-over-64kib (rc=3' <<<"$(true)"; then
      :
    fi
    # Recheck the file from the last run — run_file wrote $T/out for this case
    # only if we re-run. Re-run just the reason check against a fresh invoke.
    python3 "$PY" "$ROOT" "$ROOT" <"$T/cap-over" >"$T/out-reason" 2>/dev/null || true
    if grep -q "too large to parse" "$T/out-reason"; then
      PASS=$((PASS + 1)); printf '  \033[32m✓\033[0m cap-over-64kib reason is "too large to parse"\n'
    else
      FAIL=$((FAIL + 1)); printf '  \033[31m✗\033[0m cap-over-64kib missing reason, got: %s\n' "$(head -c200 "$T/out-reason")"
    fi
  fi
fi

# 256 markers still parse (no write → exit 0). 257 markers fail closed.
python3 - "$T/markers-256" "$T/markers-257" <<'PY'
import sys
hd = chr(60) * 2
# Each "cat <<A\n" contributes one marker. No terminator, no write.
line = "cat " + hd + "A\n"
open(sys.argv[1], "w").write(line * 256)
open(sys.argv[2], "w").write(line * 257)
PY
run_file cap-at-256-markers-still-parses 0 "$T/markers-256"
run_file cap-over-256-markers 3 "$T/markers-257"
python3 "$PY" "$ROOT" "$ROOT" <"$T/markers-257" >"$T/out-m" 2>/dev/null || true
if grep -q "too large to parse" "$T/out-m"; then
  PASS=$((PASS + 1)); printf '  \033[32m✓\033[0m cap-over-256-markers reason is "too large to parse"\n'
else
  FAIL=$((FAIL + 1)); printf '  \033[31m✗\033[0m cap-over-256-markers missing reason, got: %s\n' "$(head -c200 "$T/out-m")"
fi

echo
echo "── AppSec N1 — 1 MiB unterminated padding completes fast and denies ──"
python3 - "$T/1mib" <<'PY'
import sys
hd = chr(60) * 2
line = "cat " + hd + "A\n"
target = 1024 * 1024
body = line * (target // len(line) + 1)
open(sys.argv[1], "w").write(body[: target + 16])
PY
run_file pathological-1mib-unterminated 3 "$T/1mib"

# Under both caps: a real out-of-tree write followed by unterminated padding
# must still deny (exit 3) quickly — the linear scanner, not just the cap.
python3 - "$T/under-cap-write" <<'PY'
import sys
hd = chr(60) * 2
# F1-style interpreter heredoc, then 200 unterminated data markers (under 256
# and well under 64 KiB) that would have been a ReDoS shape on the old regex.
repro = "python3 - " + hd + "'PY'\nopen('/workspace/sibling-wt/x','w').write('x')\nPY\n"
pad = ("cat " + hd + "A\n") * 200
open(sys.argv[1], "w").write(repro + pad)
PY
run_file pathological-under-cap-with-write 3 "$T/under-cap-write"

echo
echo "── AppSec N1 — a normal F1 repro is still denied quickly ──"
# Built at top level, no $( ), "<<" via ${_HD}.
printf '%s\n' "python3 - ${_HD}'PY'" "open('/workspace/sibling-wt/x','w').write('x')" "PY" >"$T/f1"
run_file f1-repro-fast 3 "$T/f1"

echo
echo "── allow controls (data heredocs must not false-deny) ──"
printf '%s\n' "cat ${_HD}'EOF'" "some text mentioning /workspace/other/f" "EOF" >"$T/allow-cat"
run_file allow-cat-path-in-data 0 "$T/allow-cat"
printf '%s\n' "git commit -F - ${_HD}'EOF'" "docs: mention open('/workspace/other/f','w')" "EOF" >"$T/allow-git"
run_file allow-git-commit-F-example-open 0 "$T/allow-git"
printf '%s\n' "python3 - ${_HD}'PY'" "open('$ROOT/a.txt','w').write('x')" "PY" >"$T/allow-intree"
run_file allow-interpreter-heredoc-in-tree 0 "$T/allow-intree"
printf '%s\n' "gh pr create --body-file - ${_HD}'EOF'" "example: python3 -c 'pass'" "EOF" >"$T/allow-gh"
run_file allow-gh-pr-body-file-example-c 0 "$T/allow-gh"

echo
echo "── AppSec N1 — signal.alarm exits 4; hook maps that to a deny ──"
# Arm happens before stdin is read, so an open pipe plus SIGALRM trips exit 4
# without waiting the full 5 s budget.
python3 - "$PY" "$ROOT" "$T/alarm-rc" <<'PY'
import os, signal, subprocess, sys, time
helper, root, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
proc = subprocess.Popen(
    [sys.executable, helper, root, root],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
# Give the child time to arm the alarm and block on stdin.
deadline = time.monotonic() + 2
rc = None
while time.monotonic() < deadline:
    if proc.poll() is not None:
        rc = proc.returncode
        break
    time.sleep(0.02)
if rc is not None:
    # Child already exited — that is a failure of this test (it should be blocked on stdin).
    open(out_path, "w").write(str(rc))
    sys.exit(0)
try:
    proc.send_signal(signal.SIGALRM)
except ProcessLookupError:
    pass
try:
    rc = proc.wait(timeout=2)
except subprocess.TimeoutExpired:
    proc.kill()
    rc = proc.wait()
open(out_path, "w").write(str(rc))
# Close stdin if still open so we don't leak.
try:
    proc.stdin.close()
except Exception:
    pass
PY
alarm_rc="$(cat "$T/alarm-rc")"
if [ "$alarm_rc" = "4" ]; then
  PASS=$((PASS + 1)); printf '  \033[32m✓\033[0m helper-sigalrm-exit-4 (rc=4)\n'
else
  FAIL=$((FAIL + 1)); printf '  \033[31m✗\033[0m helper-sigalrm-exit-4 want=4 got=%s\n' "$alarm_rc"
fi

# Hook-level: worktree-guard.sh turns helper exit 4 into hook exit 2 (fail-closed).
# Drive the hook with a tiny shim that replaces the helper with a script exiting 4.
git init -q "$T/wt" && printf '%s\n' ".ravenclaude/" > "$T/wt/.gitignore" \
  && git -C "$T/wt" add .gitignore \
  && git -C "$T/wt" -c user.name=t -c user.email=t@t commit -q -m init
mkdir -p "$T/hooks-shim"
# Copy the hook and drop a helper next to it that exits 4 (same name the hook looks up).
cp "$HOOK" "$T/hooks-shim/worktree-guard.sh"
printf '%s\n' '#!/usr/bin/env bash' 'exit 4' >"$T/hooks-shim/worktree-guard-bash.py"
chmod +x "$T/hooks-shim/worktree-guard-bash.py"
export RC_WORKTREE_GUARD_HOME="$T/gh" RC_WG_ERROR_LOG="$T/errors.log" RC_WG_STALE_LOG="$T/stale.log" CLAUDE_PROJECT_DIR="$T/wt"
payload="$(jq -cn --arg w "$T/wt" '{tool_name:"Bash",session_id:"s1",cwd:$w,tool_input:{command:"echo hi > a.txt"}}')"
printf '%s' "$payload" | (cd "$T/wt" && bash "$T/hooks-shim/worktree-guard.sh" check) >"$T/hook-out" 2>"$T/hook-err"
hook_rc=$?
if [ "$hook_rc" = "2" ] && grep -q "fail-closed" "$T/hook-err"; then
  PASS=$((PASS + 1)); printf '  \033[32m✓\033[0m hook-maps-helper-exit-4-to-deny (rc=2)\n'
else
  FAIL=$((FAIL + 1)); printf '  \033[31m✗\033[0m hook-maps-helper-exit-4-to-deny want=2+fail-closed got=%s: %s\n' \
    "$hook_rc" "$(head -c300 "$T/hook-err")"
fi

# hooks.json: the check PreToolUse entry carries timeout 60; register is unchanged.
python3 - "$HOOKS_DIR/hooks.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
check = register = None

def walk(obj):
    global check, register
    if isinstance(obj, dict):
        cmd = str(obj.get("command", ""))
        if cmd.endswith("worktree-guard.sh\" check") or cmd.endswith("worktree-guard.sh check"):
            check = obj.get("timeout")
        if cmd.endswith("worktree-guard.sh\" register") or cmd.endswith("worktree-guard.sh register"):
            register = obj.get("timeout")
        for v in obj.values():
            walk(v)
    elif isinstance(obj, list):
        for v in obj:
            walk(v)
walk(d)
sys.exit(0 if check == 60 and register == 10 else 1)
PY
if [ $? -eq 0 ]; then
  PASS=$((PASS + 1)); printf '  \033[32m✓\033[0m hooks.json check timeout=60 (register still 10)\n'
else
  FAIL=$((FAIL + 1)); printf '  \033[31m✗\033[0m hooks.json check timeout is not 60 or register changed\n'
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
echo "RESULT pass=$PASS fail=$FAIL"
[ "$FAIL" -eq 0 ]
