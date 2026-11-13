#!/usr/bin/env bash
# test-worktree-guard-heredoc-interpreter.sh — F1 regression (AppSec SHIPCHECK
# 18f5c03f, upstream of #1416/cba447ec): worktree-guard-bash.py must deny an
# interpreter program fed by heredoc that writes outside the worktree.
#
# #1416 started stripping ALL heredoc bodies (as inert data) before the
# inline-interpreter write scan ran, so `python3 - <<'PY'` / `node <<JS` /
# etc. programs that write outside the worktree silently returned exit 0
# (allow) instead of exit 3 (deny). This drives the HELPER DIRECTLY
# (argv: <worktree_root> <cwd>, command on stdin) — not the worktree-guard.sh
# wrapper, which is covered separately (hook-level, exit 2) by
# test-worktree-guard-failclosed.sh's `bad-python-heredoc` + `appsec-f1-*`
# cases. This is NOT test-guard-heredoc-interpreter.sh — that file covers the
# unrelated guard-destructive.sh hook (exit 2); do not conflate the two.
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-worktree-guard-heredoc-interpreter.sh

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOKS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PY="$HOOKS_DIR/worktree-guard-bash.py"

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
ROOT="$T/worktree"
mkdir -p "$ROOT"

# The #1424 macOS shard 1 log at d94f38d0 reported this fixture exit 1 in 1.4s
# with output discarded. The same fixture at b32bc0eb (output now visible)
# finished in well under 2s as RESULT pass=34 fail=1, then Gate 309
# "must_pass expected zero, got exit=1". The failing case is
# allow-interpreter-heredoc-tmp: want=0 got=3, "inline-interpreter -> /tmp/x".
# The helper allowlists a literal "/tmp" but realpath()s write targets; on
# Darwin /tmp is /private/tmp, so a /tmp write false-denies. The same
# /private/tmp miss produced good-bash-tmp want=0 got=2 in fail-closed on
# that image. RC_WG_EXTRA_WRITE_ROOTS is already realpath'd by the helper;
# adding /tmp is a test-portability fix, not a hook change.
export RC_WG_EXTRA_WRITE_ROOTS="${RC_WG_EXTRA_WRITE_ROOTS:+$RC_WG_EXTRA_WRITE_ROOTS:}/tmp"

# Literal "<<" is never written as source text in this added section (Door 5).
# Built with printf octal so the two-character sequence is not in this file's
# source. Fail loud if the opener cannot be produced: an empty _HD would
# silently drop the opener from every later payload and the helper would
# return 0 (allow) instead of 3.
_HD="$(printf '\074\074')" || {
  echo "FAIL HARNESS: printf could not build the heredoc opener" >&2
  exit 1
}
if [ "${#_HD}" -ne 2 ]; then
  echo "FAIL HARNESS: heredoc opener was not two characters (got ${#_HD})" >&2
  exit 1
fi

PASS=0
FAIL=0

# $1=name $2=expected-exit $3=command (fed on stdin); argv is ROOT ROOT.
# Locals are initialized before use: bash 3.2 `local got out` leaves them unset,
# and with `set -u` a later expansion could abort with exit 1 and no per-case
# FAIL line. The d94f38d0 macOS exit 1 was not that (see allow-interpreter-
# heredoc-tmp / /private/tmp above); keep the init and `|| got=$?` anyway so a
# helper deny prints a FAIL line instead of dying silently if set -e is added.
run() {
  local name want body got out
  name="$1"
  want="$2"
  body="$3"
  got=0
  out=""
  out="$(printf '%s' "$body" | python3 "$PY" "$ROOT" "$ROOT" 2>&1)" || got=$?
  if [ "$got" = "$want" ]; then
    PASS=$((PASS + 1)); printf '  \033[32m✓\033[0m %s (rc=%s)\n' "$name" "$got"
  else
    FAIL=$((FAIL + 1)); printf '  \033[31m✗\033[0m %s want=%s got=%s: %s\n' "$name" "$want" "$got" "$out"
  fi
}

echo
echo "── AppSec SHIPCHECK 18f5c03f F1 — the three exact repros: MUST DENY (exit 3) ──"
run appsec-repro1-python-open-write 3 "python3 - <<'PY'
open('/workspace/sibling-wt/x','w').write('x')
PY"
run appsec-repro2-python-rmtree 3 "python3 <<PY
import shutil
shutil.rmtree(\"/workspace/sibling-wt\")
PY"
run appsec-repro3-node-writeFileSync 3 "node <<JS
require('fs').writeFileSync(\"/workspace/sibling-wt/x\", \"x\")
JS"

echo
echo "── required interpreter set — php / deno / bun heredocs must also deny ──────"
run php-heredoc-file-put-contents 3 "php <<'PHP'
file_put_contents(\"/workspace/sibling-wt/x\", \"x\");
PHP"
run deno-heredoc-writeTextFile 3 "deno <<'TS'
Deno.writeTextFile(\"/workspace/sibling-wt/x\", \"x\");
TS"
run bun-heredoc-writeFileSync 3 "bun <<'JS'
require('fs').writeFileSync(\"/workspace/sibling-wt/x\", \"x\");
JS"

echo
echo "── no regression — mechanisms that already worked on 0.361.1 stay denied ────"
run control-python-c-still-denied 3 "python3 -c \"open('/workspace/other/f','w').write('x')\""
run control-node-e-still-denied 3 "node -e \"require('fs').writeFileSync('/workspace/other/f','x')\""
run control-cat-redirect-still-denied 3 "cat > /workspace/other/f <<'EOF'
hello
EOF"

echo
echo "── AppSec #1430 — blanker keeps opener-line writers; false <<; line cont ───"
# Use /workspace/sibling-wt (same as F1 cases), NOT a path under $T/mktemp:
# the helper allowlists /tmp, so $T/sibling would false-allow every deny row.
_SIB="/workspace/sibling-wt"

run appsec-1430-control-redirect 3 "echo x > ${_SIB}/a"

_body="cat ${_HD}EOF | tee ${_SIB}/x"$'\n'"body"$'\n'"EOF"
run appsec-1430-cat-tee-opener-suffix 3 "$_body"

_body="cat ${_HD}EOF; touch ${_SIB}/x"$'\n'"body"$'\n'"EOF"
run appsec-1430-cat-touch-opener-suffix 3 "$_body"

# Arithmetic << must not blank the following touch (false opener).
_body="echo \$((1<<8)); touch ${_SIB}/x"$'\n'"8"
run appsec-1430-arith-shift-false-opener 3 "$_body"

# Comment decoy: # <<EOF must not blank the following touch.
_body="# ${_HD}EOF"$'\n'"touch ${_SIB}/x"$'\n'"EOF"
run appsec-1430-comment-decoy-opener 3 "$_body"

_body="python3 - ${_HD}'PY'"$'\n'"open('${_SIB}/x','w').write('x')"$'\n'"PY"
run appsec-1430-python-heredoc 3 "$_body"

# Line-continued interpreter: python3 \ ⏎ <<'PY'
_body="python3 \\"$'\n'"${_HD}'PY'"$'\n'"open('${_SIB}/x','w').write('x')"$'\n'"PY"
run appsec-1430-python-line-continuation 3 "$_body"

_body="cat ${_HD}EOF > ./in-tree"$'\n'"hi"$'\n'"EOF"
run appsec-1430-allow-cat-in-tree 0 "$_body"

_body="git commit -F - ${_HD}EOF"$'\n'"msg"$'\n'"EOF"
run appsec-1430-allow-git-commit-F 0 "$_body"

echo
echo "── allow — data heredocs (non-interpreter) stay treated as inert data ───────"
run allow-cat-only-mentions-path 0 "cat <<'EOF' | grep rf
some text mentioning /workspace/other/f
EOF"
run allow-git-commit-F 0 "git commit -F - <<'EOF'
docs: mention /workspace/other/f is denied
EOF"
run allow-interpreter-heredoc-in-tree 0 "python3 - <<'PY'
open('$ROOT/a.txt','w').write('x')
PY"

echo
echo "── delimiter / invocation / terminator forms (AppSec F1 coverage, preserved in N1) ──"
# Built at top level via ${_HD}; run() only interpolates a variable name inside
# its own command substitution, never heredoc-shaped source text.

_body="python3 ${_HD}\"PY\""$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run delim-double-quoted-tag 3 "$_body"

_body="python3 ${_HD} PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run delim-space-before-tag 3 "$_body"

_body="python3 - ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run delim-python3-dash-unquoted 3 "$_body"

_body="python3 ${_HD}-PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'$'\t'"PY"
run delim-dash-tab-terminator 3 "$_body"

_body="python3 ${_HD}\\PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run delim-backslash-tag 3 "$_body"

_body="cat ${_HD}EOF"$'\n'"example open('/workspace/other','w')"$'\n'"EOF"$'\n'"python3 ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run multi-data-then-interpreter 3 "$_body"

_body="python3 ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"$'\n'"cat ${_HD}EOF"$'\n'"example open('/workspace/other','w')"$'\n'"EOF"
run multi-interpreter-then-data 3 "$_body"

_body="python3 -c 'pass' ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run heredoc-plus-c 3 "$_body"

_body="env python3 ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run invoc-env-python3 3 "$_body"

_body="/usr/bin/python3 ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run invoc-usr-bin-python3 3 "$_body"

_body="python3.12 ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run invoc-python3-12 3 "$_body"

_body="FOO=1 python3 ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run invoc-assignment-prefix 3 "$_body"

_body="nice -n 5 python3 ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run invoc-nice 3 "$_body"

_body="timeout 5 python3 ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run invoc-timeout 3 "$_body"

_body="bash -c \"python3 ${_HD}PY"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY\""
run invoc-bash-c-wrapped 3 "$_body"

_body="python3 <<< \"open('/workspace/sibling-wt/x','w').write('x')\""
run here-string-python 3 "$_body"

_body="bun ${_HD}'JS'"$'\n'"Bun.write(\"/workspace/sibling-wt/x\", \"x\")"$'\n'"JS"
run bun-Bun-write 3 "$_body"

_body="python3 ${_HD}EOF"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"EOF.x"$'\n'"open('/workspace/sibling-wt/y','w').write('y')"$'\n'"EOF"
run term-EOF-x-lookalike 3 "$_body"

_body="cat ${_HD}EOF"$'\n'"example"$'\n'"EOF"$'\n'"python3 -c \"open('/workspace/sibling-wt/x','w').write('x')\""
run data-heredoc-then-c 3 "$_body"

_body="python3 ${_HD}PY"$'\n'"open('/tmp/x','w').write('x')"$'\n'"PY"
run allow-interpreter-heredoc-tmp 0 "$_body"

_body="python3 ${_HD}PY"$'\n'"p=open('/workspace/sibling-wt/x').read()"$'\n'"PY"
run allow-interpreter-heredoc-read-only 0 "$_body"

_body="gh pr create --body-file - ${_HD}'EOF'"$'\n'"example: python3 -c 'pass'"$'\n'"EOF"
run allow-gh-pr-body-file-example-c 0 "$_body"

echo
echo "── mutation: reverting the interpreter-aware heredoc check lets the repros through ──"
MUT="$(mktemp)"
python3 - "$PY" "$MUT" <<'PYPATCH'
import re
import sys
src = open(sys.argv[1]).read()
anchor = "def _heredoc_feeds_interpreter(prefix):\n"
assert anchor in src, "anchor not found — worktree-guard-bash.py structure moved"
patched = re.sub(
    r"def _heredoc_feeds_interpreter\(prefix\):\n(?:.*\n)*?    return False\n",
    "def _heredoc_feeds_interpreter(prefix):\n    return False\n",
    src,
    count=1,
)
assert patched != src, "mutation did not change the source"
open(sys.argv[2], "w").write(patched)
PYPATCH
got="$(printf '%s' "python3 - <<'PY'
open('/workspace/sibling-wt/x','w').write('x')
PY" | python3 "$MUT" "$ROOT" "$ROOT" 2>&1)"
rc=$?
if [ "$rc" -eq 0 ]; then
  PASS=$((PASS + 1)); printf '  \033[32m✓\033[0m mutant (always-blank heredocs) lets repro1 through — test is sensitive\n'
else
  FAIL=$((FAIL + 1)); printf '  \033[31m✗\033[0m mutant still denied (rc=%s): test cannot distinguish fixed from unfixed\n' "$rc"
fi
rm -f "$MUT"

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
echo "RESULT pass=$PASS fail=$FAIL"
[ "$FAIL" -eq 0 ]
