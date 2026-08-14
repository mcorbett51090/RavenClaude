#!/usr/bin/env bash
# test-rcwt-lane-settings.sh — rcwt new writes a lane stamp, opens code -n,
# and merges VS Code settings add-absent-keys only.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RCWT="$PLUGIN_ROOT/bin/rcwt"

PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

if ! command -v git >/dev/null 2>&1; then
  echo "SKIP: git not available"
  exit 0
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "SKIP: python3 not available"
  exit 0
fi

merge_settings() {
  local dest="$1"
  SETTINGS_SRC="$PLUGIN_ROOT/templates/worktree-lane/settings.json" \
    SETTINGS_FILE="$dest/.vscode/settings.json" \
    RCWT_CHAT_CEILING="${RCWT_CHAT_CEILING:-}" python3 - <<'PY'
import json, os, sys
src_path = os.environ["SETTINGS_SRC"]
dst_path = os.environ["SETTINGS_FILE"]
with open(src_path) as f:
    wanted = json.load(f)
if os.environ.get("RCWT_CHAT_CEILING") == "1":
    wanted["chat.agent.sandbox.enabled"] = True
existing = {}
if os.path.exists(dst_path):
    with open(dst_path) as f:
        existing = json.load(f)
added = False
for k, v in wanted.items():
    if k not in existing:
        existing[k] = v
        added = True
if added:
    tmp = dst_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(existing, f, indent=2)
        f.write("\n")
    os.replace(tmp, dst_path)
PY
}

SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT

R="$SB/repo"
git init -q "$R"
git -C "$R" config user.email t@example.com
git -C "$R" config user.name test
git -C "$R" commit --allow-empty -q -m init
git -C "$R" branch -M main
git clone -q --bare "$R" "$SB/remote.git"
git -C "$R" remote add origin "$SB/remote.git"
git -C "$R" push -q origin main

export RCWT_PRIMARY="$R"
export RAVENCLAUDE_WORKTREE_ROOT="$SB/wts"
mkdir -p "$SB/bin"
cat > "$SB/bin/code" <<EOF
#!/bin/sh
printf '%s\n' "\$*" > "$SB/code.argv"
EOF
chmod +x "$SB/bin/code"
export PATH="$SB/bin:$PATH"

echo
echo "── rcwt new writes lane stamp + code -n + parent-walk pin ───────────────"
if ! bash "$RCWT" new lane-t 2>"$SB/rcwt.err"; then
  fail "rcwt new failed: $(cat "$SB/rcwt.err")"
  echo "rcwt-lane-settings: $FAIL assertion(s) FAILED"
  exit 1
fi
DEST="$SB/wts/lane-t"
if [ -f "$DEST/.ravenclaude/lane.md" ] \
   && grep -q "worktree_path:" "$DEST/.ravenclaude/lane.md" \
   && grep -q "branch: forge/lane-t" "$DEST/.ravenclaude/lane.md" \
   && grep -q "Do \*\*not\*\* open a sibling worktree as a second folder" "$DEST/.ravenclaude/lane.md"; then
  pass "lane.md has path, branch, and anti-multi-root rule"
else
  fail "lane.md missing required fields ($(cat "$DEST/.ravenclaude/lane.md" 2>/dev/null | head -20))"
fi

if [ -f "$SB/code.argv" ] && grep -q -- "-n" "$SB/code.argv" && grep -q "$DEST" "$SB/code.argv"; then
  pass "code invoked with -n and dest"
else
  fail "code argv was '$(cat "$SB/code.argv" 2>/dev/null)'"
fi

if [ -f "$DEST/.vscode/settings.json" ] \
   && python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get('chat.useCustomizationsInParentRepositories') is False else 1)" "$DEST/.vscode/settings.json"; then
  pass "parent-walk pin merged (false)"
else
  fail "parent-walk pin missing: $(cat "$DEST/.vscode/settings.json" 2>/dev/null)"
fi

if python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if 'chat.agent.sandbox.enabled' not in d else 1)" "$DEST/.vscode/settings.json"; then
  pass "sandbox key absent when RCWT_CHAT_CEILING unset"
else
  fail "sandbox key present without the flag"
fi

echo
echo "── second merge does not overwrite a consumer true ──────────────────────"
python3 - <<PY
import json
p = "$DEST/.vscode/settings.json"
d = json.load(open(p))
d["chat.useCustomizationsInParentRepositories"] = True
json.dump(d, open(p, "w"), indent=2)
open(p, "a").write("\n")
PY
merge_settings "$DEST"
if python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get('chat.useCustomizationsInParentRepositories') is True else 1)" "$DEST/.vscode/settings.json"; then
  pass "merge left consumer true intact"
else
  fail "merge overwrote consumer true"
fi

echo
echo "── RCWT_CHAT_CEILING=1 adds sandbox key ─────────────────────────────────"
RCWT_CHAT_CEILING=1 merge_settings "$DEST"
if python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get('chat.agent.sandbox.enabled') is True else 1)" "$DEST/.vscode/settings.json"; then
  pass "RCWT_CHAT_CEILING=1 added sandbox key"
else
  fail "sandbox key not added under the flag"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "rcwt-lane-settings: ALL ASSERTIONS PASS"
  exit 0
else
  echo "rcwt-lane-settings: $FAIL assertion(s) FAILED"
  exit 1
fi
