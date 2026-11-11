#!/usr/bin/env bash
# Self-tests for worktree-guard fail-closed + Bash coverage (AppSec 2026-10-23).
#
# macOS CI (PR #1423 shard 1 at 637b7e29, 2026-11-11, 5:57–6:27 AM ET):
# this fixture became visible and ran through F-7 in ~18s (backend=perl-alarm),
# then went silent until the 30-minute job cap. Neither the 15s per-case
# ceiling nor Gate 309's 60s outer _rc_timeout fired. _portable.sh
# `_rc_timeout` on stock macOS is `perl -e 'alarm shift; exec @ARGV'`. After
# exec of bash, that pending SIGALRM does not bound the child (bash 3.2
# clears or reuses SIGALRM for TMOUT/read -t), so the backend is a no-op
# when the command is bash. We do not change the pinned _portable.sh.
# Harness-only: a parent-kills-child watchdog (GNU timeout/gtimeout, else
# perl fork+setpgrp+alarm in the PARENT). Progress goes to stdout and
# stderr so a hang names the case and the layer even if one stream is
# block-buffered. A timeout is always a FAIL (never a skip or a pass).
# Audit-gates must launch this script with < /dev/null (same load-bearing
# redirect as Gate 140), must not discard output, and must use the same
# parent-kills-child watchdog as the outer bound.
H="$(cd "$(dirname "$0")/.." && pwd)/worktree-guard.sh"
CASE_TIMEOUT=15
# Progress on both streams: GitHub Actions captures both; bash echo is a
# write(2) so a subsequent hang cannot leave the line sitting in a stdio
# buffer the way a libc printf might.
_progress() { echo "$1"; echo "$1" >&2; }

# Parent-kills-child timeout. $1=seconds, rest=command. Exit 124 on ceiling.
# Never use exec-alarm in the same process as bash (see header).
_wg_watchdog() {
  local _secs="$1"
  shift
  if [ "$TIMEOUT_BACKEND" = "gnu-timeout" ]; then
    timeout "${_secs}s" "$@"
    return $?
  fi
  if [ "$TIMEOUT_BACKEND" = "gtimeout" ]; then
    gtimeout "${_secs}s" "$@"
    return $?
  fi
  perl -e '
    my $s = shift @ARGV;
    my $pid = fork();
    if (!defined $pid) { exit 127; }
    if ($pid == 0) { setpgrp(0, 0); exec @ARGV or exit 127; }
    $SIG{ALRM} = sub {
      kill "TERM", -$pid;
      select(undef, undef, undef, 0.5);
      kill "KILL", -$pid;
      waitpid $pid, 0;
      exit 124;
    };
    alarm $s;
    waitpid $pid, 0;
    my $c = $?;
    alarm 0;
    if (($c & 127) == 15 || ($c & 127) == 9) { exit 124; }
    if ($c & 127) { exit 128 + ($c & 127); }
    exit $c >> 8;
  ' "$_secs" "$@"
}

if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BACKEND=gnu-timeout
elif command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_BACKEND=gtimeout
elif command -v perl >/dev/null 2>&1; then
  TIMEOUT_BACKEND=perl-watchdog
else
  echo "FAIL HARNESS: no timeout, gtimeout, or perl; cases cannot be bounded" >&2
  exit 1
fi

T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
pass=0; fail=0

# A timeout is a FAIL, never a skip or a pass. $1=name $2=rc $3=layer (HARNESS|HOOK)
_abort_timeout() {
  fail=$((fail+1))
  msg=$(printf 'FAIL %s: TIMEOUT after %ss in the %s path (did not return; backend=%s rc=%s)' \
    "$1" "$CASE_TIMEOUT" "$3" "$TIMEOUT_BACKEND" "$2")
  _progress "$msg"
  _progress "RESULT pass=$pass fail=$fail (aborted on TIMEOUT FAIL)"
  exit 1
}

# Run worktree-guard.sh check with $2 as stdin payload. Stdin is a file, not a
# pipe held open by the harness. Return the hook's rc, or 124 on ceiling.
_run_hook() {
  printf '%s' "$2" > "$T/payload"
  _wg_watchdog "$CASE_TIMEOUT" bash -c 'cd "$1" && exec bash "$2" check' _ "$T/wt" "$1" \
    < "$T/payload" >"$T/out" 2>"$T/err"
}

_preview_err() {
  cut -c1-300 "$T/err" 2>/dev/null | tr '\n' ' '
}

run() { # name expect_rc payload
  local name="$1" want="$2" got
  _progress "HARNESS begin $name"
  _progress "HOOK start $name"
  _run_hook "$H" "$3"
  got=$?
  case "$got" in 124|142) _abort_timeout "$name" "$got" "HOOK (worktree-guard.sh check)" ;; esac
  _progress "HOOK done $name rc=$got"
  if [ "$got" = "$want" ]; then
    pass=$((pass+1)); echo "PASS $name (rc=$got)"
  else
    fail=$((fail+1)); echo "FAIL $name want=$want got=$got: $(_preview_err)"
  fi
}

echo "── test-worktree-guard-failclosed.sh (per-case timeout ${CASE_TIMEOUT}s backend=${TIMEOUT_BACKEND}) ──"
_progress "HARNESS start setup"
git init -q "$T/wt" && echo ".ravenclaude/" > "$T/wt/.gitignore" && git -C "$T/wt" add .gitignore && git -C "$T/wt" -c user.name=t -c user.email=t@t commit -q -m init
git -C "$T/wt" checkout -q -b feat
export RC_WORKTREE_GUARD_HOME="$T/gh" RC_WG_ERROR_LOG="$T/errors.log" RC_WG_STALE_LOG="$T/stale.log" CLAUDE_PROJECT_DIR="$T/wt"
# The helper allowlists a literal "/tmp" but realpath()s write targets. On
# Darwin /tmp is /private/tmp, so `> /tmp/x` would false-deny (seen on
# 637b7e29 macOS shard 1: good-bash-tmp want=0 got=2) even though the deny
# text says writes to /tmp are allowed. RC_WG_EXTRA_WRITE_ROOTS is already
# realpath'd by the helper; adding /tmp is a test-portability fix, not a
# hook change.
export RC_WG_EXTRA_WRITE_ROOTS="${RC_WG_EXTRA_WRITE_ROOTS:+$RC_WG_EXTRA_WRITE_ROOTS:}/tmp"
_progress "HARNESS done setup"
j() { jq -cn --arg t "$1" --arg c "$2" --arg w "$T/wt" '{tool_name:$t,session_id:"s1",cwd:$w,tool_input:(if $t=="Bash" then {command:$c} else {file_path:$c,content:"x"} end)}'; }
run good-write-in-tree       0 "$(j Write "$T/wt/a.txt")"
run good-bash-in-tree        0 "$(j Bash 'echo hi > a.txt && cp a.txt b.txt && sed -i s/a/b/ b.txt')"
run good-bash-tmp            0 "$(j Bash 'echo hi > /tmp/x 2>&1 | tee /tmp/y')"
run good-bash-read           0 "$(j Bash 'cat /etc/hostname; ls /workspace')"
run bad-redirect-outside     2 "$(j Bash 'echo pwn > /home/box/.bashrc')"
run bad-append-outside       2 "$(j Bash 'echo pwn >> /workspace/other/f')"
run bad-tee-outside          2 "$(j Bash 'echo x | tee -a /workspace/other/f')"
run bad-cp-outside           2 "$(j Bash 'cp a.txt /workspace/other/')"
run bad-mv-outside           2 "$(j Bash 'mv a.txt /workspace/escape.txt')"
run bad-rm-outside           2 "$(j Bash 'rm -rf /workspace/other')"
run bad-sed-i-outside        2 "$(j Bash 'sed -i s/a/b/ /workspace/other/f')"
run bad-python-c-outside     2 "$(j Bash "python3 -c \"open('/workspace/other/f','w').write('x')\"")"
run bad-node-e-outside       2 "$(j Bash "node -e \"require('fs').writeFileSync('/workspace/other/f','x')\"")"
run bad-perl-e-outside       2 "$(j Bash "perl -e 'open(F, \">/workspace/other/f\"); print F 1'")"
# macOS bash 3.2 portability (AppSec SHIPCHECK 18f5c03f F2 follow-up, 2026-11-11):
# the payloads below used to spell `<<'TAG'`/`<<TAG` literally inside a `$( )`
# that also wraps a `j Bash "..."` call. Even though the tag is quoted and the
# whole thing sits inside an already-open double quote (so by plain POSIX
# grammar it is inert text, not a real heredoc redirection), bash 3.2's `$( )`
# scanner is documented (scripts/check-macos-portability.sh "door 5", PR #828)
# to re-lex quotes inside a here-doc-SHAPED span nested in `$( )` regardless of
# surrounding quoting, and swallow the rest of the file. There is no Darwin box
# here to prove it either way, so this sidesteps the question entirely: each
# payload is built as a plain variable via concatenation (no `$( )` at all),
# and the literal two-character sequence "<<" is kept out of the SOURCE TEXT by
# routing it through ${_HD} — expanded only at runtime, long after bash's
# parser has already decided where the statement ends. The run/j calls that
# follow then interpolate a variable NAME, never heredoc-shaped text, inside
# their own `$( )`. Same payloads as before, same expected exit (2).
_HD='<<'

_cmd_bad_heredoc_outside="cat > /workspace/other/f ${_HD}'EOF'"$'\n'"hello"$'\n'"EOF"
run bad-heredoc-outside      2 "$(j Bash "$_cmd_bad_heredoc_outside")"

_cmd_bad_python_heredoc="python3 - ${_HD}'PY'"$'\n'"open('/workspace/other/f','w').write('x')"$'\n'"PY"
run bad-python-heredoc       2 "$(j Bash "$_cmd_bad_python_heredoc")"

# ── AppSec SHIPCHECK 18f5c03f (F1): #1416/cba447ec blanked EVERY heredoc body
# — including one feeding an interpreter — before the inline-interpreter write
# scan ran, so these three returned rc=0 (allow) instead of rc=2 (deny). The
# exact repros AppSec reproduced against the 0.361.1 helper. Hook-level (exit
# 2, through worktree-guard.sh check); the helper itself (exit 3) is covered
# directly by test-worktree-guard-heredoc-interpreter.sh, including php/deno/
# bun and a teeth mutant.
_cmd_appsec_f1_python_open_write="python3 - ${_HD}'PY'"$'\n'"open('/workspace/sibling-wt/x','w').write('x')"$'\n'"PY"
run appsec-f1-python-open-write   2 "$(j Bash "$_cmd_appsec_f1_python_open_write")"

_cmd_appsec_f1_python_rmtree="python3 ${_HD}PY"$'\n'"import shutil"$'\n''shutil.rmtree("/workspace/sibling-wt")'$'\n'"PY"
run appsec-f1-python-rmtree       2 "$(j Bash "$_cmd_appsec_f1_python_rmtree")"

_cmd_appsec_f1_node_writeFileSync="node ${_HD}JS"$'\n'"require('fs').writeFileSync(\"/workspace/sibling-wt/x\", \"x\")"$'\n'"JS"
run appsec-f1-node-writeFileSync  2 "$(j Bash "$_cmd_appsec_f1_node_writeFileSync")"
run crash-malformed-json     2 '{"tool_name":"Bash","tool_input":{'
# crash: helper unavailable -> must deny, not allow
cp "$H" "$T/wg.sh"
_progress "HARNESS begin crash-helper-missing-deny"
_progress "HOOK start crash-helper-missing-deny"
_run_hook "$T/wg.sh" "$(j Bash 'echo hi > a.txt')"
rc=$?
case "$rc" in 124|142) _abort_timeout "crash-helper-missing-deny" "$rc" "HOOK (worktree-guard.sh check, helper missing)" ;; esac
_progress "HOOK done crash-helper-missing-deny rc=$rc"
if [ $rc = 2 ] && grep -q fail-closed "$T/err"; then pass=$((pass+1)); echo "PASS crash-helper-missing-deny (rc=2)"; else fail=$((fail+1)); echo "FAIL crash-helper-missing-deny rc=$rc: $(_preview_err)"; fi
[ -s "$T/errors.log" ] && { pass=$((pass+1)); echo "PASS errors.log written"; } || { fail=$((fail+1)); echo "FAIL errors.log empty"; }
# ── (A) stale lease: never git add/commit; record + deny ──
js() { jq -cn --arg s "$1" --arg w "$T/wt" '{tool_name:"Write",session_id:$s,cwd:$w,tool_input:{file_path:($w+"/a.txt"),content:"x"}}'; }
age_lease() { find "$T/gh/leases" -name lease.json -exec python3 -c "import os,sys,time; t=time.time()-10800; [os.utime(p,(t,t)) for p in sys.argv[1:]]" {} +; }
_progress "HARNESS begin holder0-claim-lease"
rm -rf "$T/gh/leases"
_progress "HOOK start holder0-claim-lease"
_run_hook "$H" "$(js holder0)"
rc=$?
case "$rc" in 124|142) _abort_timeout "holder0-claim-lease" "$rc" "HOOK (worktree-guard.sh check)" ;; esac
_progress "HOOK done holder0-claim-lease rc=$rc"
echo "PASS holder0-claim-lease (rc=$rc)"
echo dirty > "$T/wt/dirty.txt"; age_lease
head0=$(git -C "$T/wt" rev-parse HEAD)
run stale-dirty-denied 2 "$(js claimant1)"
if [ "$(git -C "$T/wt" rev-parse HEAD)" = "$head0" ] && [ -z "$(git -C "$T/wt" diff --cached --name-only)" ] && git -C "$T/wt" status --porcelain | grep -q '^?? dirty.txt'; then pass=$((pass+1)); echo "PASS stale-no-git-add-or-commit"; else fail=$((fail+1)); echo "FAIL stale-no-git-add-or-commit"; fi
grep -q 'holder=holder0' "$T/stale.log" 2>/dev/null && { pass=$((pass+1)); echo "PASS stale-leases.log recorded"; } || { fail=$((fail+1)); echo "FAIL stale-leases.log"; }
grep -q 'no longer auto-commits' "$T/err" && { pass=$((pass+1)); echo "PASS stale deny message"; } || { fail=$((fail+1)); echo "FAIL stale deny message"; }
rm -f "$T/wt/dirty.txt"; age_lease
run stale-clean-takeover 0 "$(js claimant1)"
[ "$(git -C "$T/wt" rev-parse HEAD)" = "$head0" ] && { pass=$((pass+1)); echo "PASS clean-takeover-no-commit"; } || { fail=$((fail+1)); echo "FAIL clean-takeover committed"; }
# ── F-7: git status FAILS on a stale lease -> deny, never "clean" ──
_progress "HARNESS begin holder2-claim-lease"
rm -rf "$T/gh/leases"
_progress "HOOK start holder2-claim-lease"
_run_hook "$H" "$(js holder2)"
rc=$?
case "$rc" in 124|142) _abort_timeout "holder2-claim-lease" "$rc" "HOOK (worktree-guard.sh check)" ;; esac
_progress "HOOK done holder2-claim-lease rc=$rc"
echo "PASS holder2-claim-lease (rc=$rc)"
age_lease
cp "$T/wt/.git/index" "$T/index.bak"; printf 'garbage' > "$T/wt/.git/index"
run stale-git-status-error-denied 2 "$(js claimant3)"
grep -q "git status' failed" "$T/err" && { pass=$((pass+1)); echo "PASS F-7 deny names git status failure"; } || { fail=$((fail+1)); echo "FAIL F-7 message: $(_preview_err)"; }
grep -q 'stale-lease-git-status-failed' "$T/stale.log" && { pass=$((pass+1)); echo "PASS F-7 logged"; } || { fail=$((fail+1)); echo "FAIL F-7 log"; }
_progress "HARNESS start restore-index-after-F-7"
cp "$T/index.bak" "$T/wt/.git/index"
_progress "HARNESS done restore-index-after-F-7"
# ── internal error inside the lease section -> ERR trap denies ──
# The 637b7e29 macOS shard 1 log went silent after "PASS F-7 logged" and
# never printed HARNESS begin lease-internal-error-denied (25 minutes until
# the job cap). Label every harness step so a later hang is named as
# HARNESS (mutation/copy) or HOOK (the mutated check).
_progress "HARNESS start copy-helpers-for-lease-mutation"
mkdir -p "$T/mf"; for f in worktree-guard-bash.py _portable.sh _emit-event.sh; do [ -f "$(dirname "$H")/$f" ] && cp "$(dirname "$H")/$f" "$T/mf/"; done
_progress "HARNESS done copy-helpers-for-lease-mutation"
_progress "HARNESS start mutate-lease-section"
# Portable mutation: GNU-vs-BSD sed divergence on this anchor (worktree-guard.sh
# does not use GNU-only sed syntax here, but it was flagged unverified by AppSec
# review and there is no Darwin box to settle it) is sidestepped entirely with a
# plain bash glob-pattern substring replace, which behaves identically on GNU
# and BSD userlands because it never shells out to sed/perl at all.
_wg_anchor='      _wg_holder="$(_wg_lease_holder)"'
_wg_mutated="${_wg_anchor}; false"
_wg_src="$(cat "$H")"
_wg_mut_src="${_wg_src/$_wg_anchor/$_wg_mutated}"
_progress "HARNESS done mutate-lease-section"
if [ "$_wg_mut_src" != "$_wg_src" ]; then
  printf '%s\n' "$_wg_mut_src" > "$T/mf/worktree-guard.sh"
  _progress "HARNESS begin lease-internal-error-denied"
  _progress "HOOK start lease-internal-error-denied"
  _run_hook "$T/mf/worktree-guard.sh" "$(js s9)"
  rc=$?
  case "$rc" in 124|142) _abort_timeout "lease-internal-error-denied" "$rc" "HOOK (mutated worktree-guard.sh check)" ;; esac
  _progress "HOOK done lease-internal-error-denied rc=$rc"
  if [ $rc = 2 ] && grep -q 'internal error in the lease section' "$T/err"; then pass=$((pass+1)); echo "PASS lease-internal-error-denied"; else fail=$((fail+1)); echo "FAIL lease-internal-error rc=$rc $(_preview_err)"; fi
else fail=$((fail+1)); echo "FAIL could not inject lease-section error (anchor line moved)"; fi
echo "RESULT pass=$pass fail=$fail"; [ $fail = 0 ]
