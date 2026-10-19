#!/usr/bin/env bash
# test-enforce-layout-normalize.sh — enforce-layout.sh path normalisation.
#
# hooks-10 (2026-10-19): the layout/scope globs are plain string patterns, so a
# path that names the same file differently slipped them:
#   - `a//b` and `a/./b` (lexical spellings of `a/b`);
#   - a trailing `/` on CLAUDE_PROJECT_DIR (every absolute path read as outside);
#   - a symlinked project root (CLAUDE_PROJECT_DIR=/link, path written /real/...).
# And the pitfall the fix must not create: an IN-project symlink that points
# outside must still be enforced as the in-project path it was written as.
# hooks-24: with no jq on PATH the hook warns once on stderr and allows.
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-enforce-layout-normalize.sh

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOK="$REPO_ROOT/plugins/ravenclaude-core/hooks/enforce-layout.sh"
PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
REAL="$TMP/real/proj"
mkdir -p "$REAL/docs" "$REAL/.ravenclaude/runs/thing" "$TMP/outside"
cat >"$REAL/.repo-layout.json" <<'EOF'
{
  "allowed_globs": ["docs/*", ".ravenclaude/**"],
  "forbidden_globs": [".ravenclaude/runs/thing/*"],
  "suggestions": {}
}
EOF
ln -s "$REAL" "$TMP/link"
ln -s "$TMP/outside" "$REAL/ext"

# _el <project-dir> <file-path> [hook] -> EL_RC (stdin JSON, the Claude Code path)
_el() {
  EL_RC=0
  printf '{"tool_input":{"file_path":"%s"}}' "$2" \
    | env -u CLAUDE_SESSION_ID CLAUDE_PROJECT_DIR="$1" bash "${3:-$HOOK}" "" >/dev/null 2>&1 || EL_RC=$?
}
_expect() { # <want> <label> <project> <path>
  _el "$3" "$4"
  if [ "$EL_RC" -eq "$1" ]; then pass "$2 (rc=$EL_RC)"; else fail "$2: expected rc $1, got $EL_RC"; fi
}

echo
echo "── hooks-10: forbidden path spelled differently is still denied ───────────"
_expect 2 "relative '.ravenclaude/runs//thing/forged.json'" "$REAL" ".ravenclaude/runs//thing/forged.json"
_expect 2 "relative '.ravenclaude/runs/./thing/forged.json'" "$REAL" ".ravenclaude/runs/./thing/forged.json"
_expect 2 "absolute with '//'" "$REAL" "$REAL/.ravenclaude//runs//thing/forged.json"
_expect 2 "absolute with '/./'" "$REAL" "$REAL/./.ravenclaude/runs/./thing/forged.json"
_expect 2 "trailing-slash project dir" "$REAL/" "$REAL/.ravenclaude/runs/thing/forged.json"
_expect 2 "trailing '//' project dir" "$REAL//" "$REAL/.ravenclaude/runs/thing/forged.json"
_expect 2 "symlinked project dir, path written via the real root" "$TMP/link" "$REAL/.ravenclaude/runs/thing/forged.json"
_expect 2 "real project dir, path written via the symlink" "$REAL" "$TMP/link/.ravenclaude/runs/thing/forged.json"
_expect 2 "off-allow-list path via the symlinked root" "$TMP/link" "$REAL/src/x.js"
_expect 2 "in-project symlink to an outside dir is enforced, not exempted" "$REAL" "$REAL/ext/x.txt"
_expect 2 "'..' traversal still refused" "$REAL" "$REAL/docs/../../etc/passwd"

echo
echo "── hooks-10: allowed paths stay allowed ────────────────────────────────────"
_expect 0 "docs/readme.md" "$REAL" "docs/readme.md"
_expect 0 "docs//readme.md" "$REAL" "docs//readme.md"
_expect 0 ".ravenclaude/runs/other/x.json" "$REAL" ".ravenclaude/runs/other/x.json"
_expect 0 "trailing-slash project dir, allowed path" "$REAL/" "$REAL/docs/x.md"
_expect 0 "symlinked project dir, allowed path" "$TMP/link" "$REAL/docs/x.md"
_expect 0 "a path genuinely outside the project" "$REAL" "$TMP/outside/x.txt"

echo
echo "── teeth: reverting each normalisation re-opens its bypass ─────────────────"
_mut_expect() { # <label> <want-rc> <project> <path> <old> <new> [<old> <new> ...]
  local label="$1" want="$2" proj="$3" path="$4" mut="$TMP/mut-enforce-layout.sh"
  shift 4
  if ! python3 - "$HOOK" "$mut" "$@" <<'PY'
import sys
from pathlib import Path
src = Path(sys.argv[1]).read_text()
pairs = sys.argv[3:]
for old, new in zip(pairs[0::2], pairs[1::2]):
    if old not in src:
        sys.exit(2)
    src = src.replace(old, new, 1)
Path(sys.argv[2]).write_text(src)
PY
  then
    fail "teeth ($label): anchor text not found"
    return
  fi
  _el "$proj" "$path" "$mut"
  if [ "$EL_RC" -eq "$want" ]; then pass "teeth ($label): mutant gives rc $want"
  else fail "teeth ($label): mutant gives rc $EL_RC, expected $want"; fi
}
STRIP='while [[ "$project_root" == */ && "$project_root" != / ]]; do project_root="${project_root%/}"; done'
RREAL='root_real="$(CDPATH='
_mut_expect "no lexical collapse -> '//' slips" 0 \
  "$REAL" ".ravenclaude/runs//thing/forged.json" 'file="$(_lexical "$file")"' ':'
_mut_expect "no strip AND no resolved root -> trailing '/' slips" 0 \
  "$REAL/" "$REAL/.ravenclaude/runs/thing/forged.json" "$STRIP" ':' "$RREAL" 'root_real="" #'
_mut_expect "strip alone still covers the trailing '/'" 2 \
  "$REAL/" "$REAL/.ravenclaude/runs/thing/forged.json" "$RREAL" 'root_real="" #'
_mut_expect "no resolved root -> symlinked root slips" 0 \
  "$TMP/link" "$REAL/.ravenclaude/runs/thing/forged.json" "$RREAL" 'root_real="" #'

echo
echo "── hooks-24: no jq on PATH -> one stderr warning, allow ───────────────────"
NOJQ="$TMP/nojq-bin"
mkdir -p "$NOJQ"
for t in bash sh cat dirname env python3 git mkdir date tr sed grep head; do
  p="$(command -v "$t" 2>/dev/null)" && ln -sf "$p" "$NOJQ/$t"
done
rc=0
err="$(printf '{"tool_input":{"file_path":"%s"}}' "$REAL/src/x.js" \
  | env -u CLAUDE_SESSION_ID PATH="$NOJQ" CLAUDE_PROJECT_DIR="$REAL" bash "$HOOK" "" 2>&1 >/dev/null)" || rc=$?
if [ "$rc" -eq 0 ] && printf '%s' "$err" | grep -q 'jq not found'; then
  pass "no jq: rc 0 and the stderr warning appears"
else
  fail "no jq: rc=$rc stderr='$err'"
fi
n="$(printf '%s\n' "$err" | grep -c 'jq not found')"
[ "$n" -eq 1 ] && pass "no jq: exactly one warning line" || fail "no jq: $n warning lines"

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
