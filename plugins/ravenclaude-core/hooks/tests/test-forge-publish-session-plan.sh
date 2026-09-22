#!/usr/bin/env bash
# Teeth for forge-publish-session-plan.sh: empty source fails; jail refuses;
# copy is non-empty and size-matched; missing Grok session group is honest skip.
set -uo pipefail

HERE="$(cd "$(dirname "$0")/../.." && pwd)"
PUB="$HERE/scripts/forge-publish-session-plan.sh"
fails=0

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

_ok() { printf '  ok   %s\n' "$1"; }
_fail() { printf '  FAIL %s\n' "$1"; fails=$((fails + 1)); }

_plant() {
  mkdir -p "$T/.ravenclaude/runs/forge/demo-slug"
  python3 -c 'import pathlib; pathlib.Path("'"$T"'/.ravenclaude/runs/forge/demo-slug/plan.md").write_text("# Plan\n\n" + ("line\n" * 20))'
  printf '%s\n' "$T/.ravenclaude/runs/forge/demo-slug/plan.md"
}

SRC="$(_plant)"

# empty source → 2
mkdir -p "$T/.ravenclaude/runs/forge/empty-slug"
: > "$T/.ravenclaude/runs/forge/empty-slug/plan.md"
mkdir -p "$T/gh/sessions/enc/sess"
ec=0
out="$(GROK_HOME="$T/gh" bash "$PUB" --plan "$T/.ravenclaude/runs/forge/empty-slug/plan.md" --session-dir "$T/gh/sessions/enc/sess" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ]; then _ok "empty source exits 2"; else _fail "empty source ec=$ec"; fi

# missing source → 2
ec=0
out="$(GROK_HOME="$T/gh" bash "$PUB" --plan "$T/.ravenclaude/runs/forge/demo-slug/nope.md" --session-dir "$T/gh/sessions/enc/sess" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ]; then _ok "missing source exits 2"; else _fail "missing source ec=$ec"; fi

# no --plan → 2
ec=0
out="$(bash "$PUB" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ]; then _ok "missing --plan exits 2"; else _fail "missing --plan ec=$ec"; fi

# publish to explicit jailed session dir
mkdir -p "$T/gh/sessions/enc/sess"
ec=0
out="$(GROK_HOME="$T/gh" bash "$PUB" --plan "$SRC" --session-dir "$T/gh/sessions/enc/sess" 2>&1)" || ec=$?
if [ "$ec" -eq 0 ] && [ -s "$T/gh/sessions/enc/sess/plan.md" ]; then
  srcb="$(wc -c < "$SRC" | tr -d ' ')"
  dstb="$(wc -c < "$T/gh/sessions/enc/sess/plan.md" | tr -d ' ')"
  if [ "$srcb" = "$dstb" ] && echo "$out" | grep -q "FORGE_SESSION_PLAN"; then
    _ok "copy publishes non-empty size-matched plan.md"
  else
    _fail "size/receipt src=$srcb dest=$dstb out=$out"
  fi
else
  _fail "publish ec=$ec out=$out"
fi

# dest-is-dir → 2
rm -rf "$T/gh/sessions/enc/sess2"
mkdir -p "$T/gh/sessions/enc/sess2/plan.md"
ec=0
out="$(GROK_HOME="$T/gh" bash "$PUB" --plan "$SRC" --session-dir "$T/gh/sessions/enc/sess2" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ]; then _ok "dest-is-dir exits 2"; else _fail "dest-is-dir ec=$ec out=$out"; fi

# no Grok session group → skip 0
ec=0
out="$(env GROK_HOME="$T/nogrok" bash "$PUB" --plan "$SRC" --cwd "$T/proj" 2>&1)" || ec=$?
if [ "$ec" -eq 0 ] && echo "$out" | grep -q "skip"; then
  _ok "missing session group is skip/0"
else
  _fail "skip-path ec=$ec out=$out"
fi

# GROK_SESSION_ID wins
enc="$(python3 -c 'from urllib.parse import quote; from pathlib import Path; print(quote(str(Path("/tmp").resolve()), safe=""))')"
mkdir -p "$T/gh2/sessions/$enc/sid-old" "$T/gh2/sessions/$enc/sid-new"
ec=0
out="$(env GROK_HOME="$T/gh2" GROK_SESSION_ID=sid-old bash "$PUB" --plan "$SRC" --cwd /tmp 2>&1)" || ec=$?
if [ "$ec" -eq 0 ] && [ -s "$T/gh2/sessions/$enc/sid-old/plan.md" ] && [ ! -f "$T/gh2/sessions/$enc/sid-new/plan.md" ]; then
  _ok "GROK_SESSION_ID wins over newest mtime"
else
  _fail "session-id prefer ec=$ec out=$out"
fi

# F1 symlink dest refuse
mkdir -p "$T/gh3/sessions/enc/s" "$T/outside"
printf 'SECRET\n' > "$T/outside/t"
ln -s "$T/outside/t" "$T/gh3/sessions/enc/s/plan.md"
ec=0
out="$(GROK_HOME="$T/gh3" bash "$PUB" --plan "$SRC" --session-dir "$T/gh3/sessions/enc/s" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ] && grep -qx 'SECRET' "$T/outside/t"; then
  _ok "symlink dest refused"
else
  _fail "symlink dest ec=$ec"
fi

# F2 plan outside jail
printf 'x\n' > "$T/loose.md"
ec=0
out="$(GROK_HOME="$T/gh" bash "$PUB" --plan "$T/loose.md" --session-dir "$T/gh/sessions/enc/sess" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ]; then _ok "plan outside forge run-dir refused"; else _fail "plan jail ec=$ec"; fi

# F2 session-dir outside sessions
mkdir -p "$T/not-sess"
ec=0
out="$(GROK_HOME="$T/gh" bash "$PUB" --plan "$SRC" --session-dir "$T/not-sess" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ]; then _ok "session-dir outside sessions refused"; else _fail "session jail ec=$ec"; fi

if [ "$fails" -eq 0 ]; then
  echo "PASS: test-forge-publish-session-plan.sh"
  exit 0
fi
echo "FAIL: $fails assertion(s)"
exit 1
