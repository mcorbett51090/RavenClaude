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

PASS=0
FAIL=0

# $1=name $2=expected-exit $3=command (fed on stdin); argv is ROOT ROOT.
run() {
  local name="$1" want="$2" body="$3" got out
  out="$(printf '%s' "$body" | python3 "$PY" "$ROOT" "$ROOT" 2>&1)"
  got=$?
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
