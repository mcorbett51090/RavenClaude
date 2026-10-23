#!/usr/bin/env bash
# Self-tests for worktree-guard fail-closed + Bash coverage (AppSec 2026-10-23).
H="$(cd "$(dirname "$0")/.." && pwd)/worktree-guard.sh"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
git init -q "$T/wt" && echo ".ravenclaude/" > "$T/wt/.gitignore" && git -C "$T/wt" add .gitignore && git -C "$T/wt" -c user.name=t -c user.email=t@t commit -q -m init
git -C "$T/wt" checkout -q -b feat
export RC_WORKTREE_GUARD_HOME="$T/gh" RC_WG_ERROR_LOG="$T/errors.log" RC_WG_STALE_LOG="$T/stale.log" CLAUDE_PROJECT_DIR="$T/wt"
pass=0; fail=0
run() { # name expect_rc payload
  local got; printf '%s' "$3" | (cd "$T/wt" && bash "$H" check) >"$T/out" 2>"$T/err"; got=$?
  if [ "$got" = "$2" ]; then pass=$((pass+1)); echo "PASS $1 (rc=$got)"; else fail=$((fail+1)); echo "FAIL $1 want=$2 got=$got: $(head -c300 "$T/err")"; fi
}
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
run bad-heredoc-outside      2 "$(j Bash "cat > /workspace/other/f <<'EOF'
hello
EOF")"
run bad-python-heredoc       2 "$(j Bash "python3 - <<'PY'
open('/workspace/other/f','w').write('x')
PY")"
run crash-malformed-json     2 '{"tool_name":"Bash","tool_input":{'
# crash: helper unavailable -> must deny, not allow
cp "$H" "$T/wg.sh"; printf '%s' "$(j Bash 'echo hi > a.txt')" | (cd "$T/wt" && bash "$T/wg.sh" check) >/dev/null 2>"$T/err"; rc=$?
fail=$((fail-0)); if [ $rc = 2 ] && grep -q fail-closed "$T/err"; then pass=$((pass+1)); echo "PASS crash-helper-missing-deny (rc=2)"; else fail=$((fail+1)); echo "FAIL crash-helper-missing-deny rc=$rc"; fi
[ -s "$T/errors.log" ] && { pass=$((pass+1)); echo "PASS errors.log written"; } || { fail=$((fail+1)); echo "FAIL errors.log empty"; }
# ── (A) stale lease: never git add/commit; record + deny ──
js() { jq -cn --arg s "$1" --arg w "$T/wt" '{tool_name:"Write",session_id:$s,cwd:$w,tool_input:{file_path:($w+"/a.txt"),content:"x"}}'; }
age_lease() { find "$T/gh/leases" -name lease.json -exec touch -d '3 hours ago' {} +; }
rm -rf "$T/gh/leases"; printf '%s' "$(js holder0)" | (cd "$T/wt" && bash "$H" check) >/dev/null 2>&1   # holder0 claims lease
echo dirty > "$T/wt/dirty.txt"; age_lease
head0=$(git -C "$T/wt" rev-parse HEAD)
run stale-dirty-denied 2 "$(js claimant1)"
if [ "$(git -C "$T/wt" rev-parse HEAD)" = "$head0" ] && [ -z "$(git -C "$T/wt" diff --cached --name-only)" ] && git -C "$T/wt" status --porcelain | grep -q '^?? dirty.txt'; then pass=$((pass+1)); echo "PASS stale-no-git-add-or-commit"; else fail=$((fail+1)); echo "FAIL stale-no-git-add-or-commit"; fi
grep -q 'holder=holder0' "$T/stale.log" 2>/dev/null && { pass=$((pass+1)); echo "PASS stale-leases.log recorded"; } || { fail=$((fail+1)); echo "FAIL stale-leases.log"; }
grep -q 'no longer auto-commits' "$T/err" && { pass=$((pass+1)); echo "PASS stale deny message"; } || { fail=$((fail+1)); echo "FAIL stale deny message"; }
rm -f "$T/wt/dirty.txt"; age_lease
run stale-clean-takeover 0 "$(js claimant1)"
[ "$(git -C "$T/wt" rev-parse HEAD)" = "$head0" ] && { pass=$((pass+1)); echo "PASS clean-takeover-no-commit"; } || { fail=$((fail+1)); echo "FAIL clean-takeover committed"; }
echo "RESULT pass=$pass fail=$fail"; [ $fail = 0 ]
