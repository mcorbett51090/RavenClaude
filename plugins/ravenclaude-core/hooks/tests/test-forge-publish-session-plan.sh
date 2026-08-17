#!/usr/bin/env bash
# Teeth for forge-publish-session-plan.sh: empty source fails; copy is non-empty
# and size-matched; missing Grok session group is an honest skip (exit 0).
set -uo pipefail

HERE="$(cd "$(dirname "$0")/../.." && pwd)"
PUB="$HERE/scripts/forge-publish-session-plan.sh"
fails=0

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

_ok() { printf '  ok   %s\n' "$1"; }
_fail() { printf '  FAIL %s\n' "$1"; fails=$((fails + 1)); }

# empty source → 2
: > "$T/empty.md"
ec=0
out="$(bash "$PUB" --plan "$T/empty.md" --session-dir "$T/sess" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ]; then _ok "empty source exits 2"; else _fail "empty source ec=$ec"; fi

# missing source → 2
ec=0
out="$(bash "$PUB" --plan "$T/nope.md" --session-dir "$T/sess" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ]; then _ok "missing source exits 2"; else _fail "missing source ec=$ec"; fi

# no --plan → 2
ec=0
out="$(bash "$PUB" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ]; then _ok "missing --plan exits 2"; else _fail "missing --plan ec=$ec"; fi

# publish to explicit session dir
mkdir -p "$T/sess"
printf 'PLAN BODY %s\n' "x" > "$T/src.md"
# pad so it is obviously non-empty
python3 -c 'import pathlib; pathlib.Path("'"$T"'/src.md").write_text("# Plan\\n\\n" + ("line\\n" * 20))'
ec=0
out="$(bash "$PUB" --plan "$T/src.md" --session-dir "$T/sess" 2>&1)" || ec=$?
if [ "$ec" -eq 0 ] && [ -s "$T/sess/plan.md" ]; then
  srcb="$(wc -c < "$T/src.md" | tr -d ' ')"
  dstb="$(wc -c < "$T/sess/plan.md" | tr -d ' ')"
  if [ "$srcb" = "$dstb" ] && echo "$out" | grep -q "FORGE_SESSION_PLAN"; then
    _ok "copy publishes non-empty size-matched plan.md"
  else
    _fail "size/receipt src=$srcb dest=$dstb out=$out"
  fi
else
  _fail "publish ec=$ec out=$out"
fi

# dest emptied after copy is a fail — plant by making dest a directory named plan.md
rm -rf "$T/sess2"
mkdir -p "$T/sess2/plan.md"
ec=0
out="$(bash "$PUB" --plan "$T/src.md" --session-dir "$T/sess2" 2>&1)" || ec=$?
if [ "$ec" -eq 2 ]; then _ok "dest-is-dir exits 2"; else _fail "dest-is-dir ec=$ec out=$out"; fi

# no Grok session group → skip 0
ec=0
out="$(env GROK_HOME="$T/nogrok" bash "$PUB" --plan "$T/src.md" --cwd "$T/proj" 2>&1)" || ec=$?
if [ "$ec" -eq 0 ] && echo "$out" | grep -q "skip"; then
  _ok "missing session group is skip/0"
else
  _fail "skip-path ec=$ec out=$out"
fi

# GROK_SESSION_ID wins when the dir exists
enc="$(python3 -c 'from urllib.parse import quote; from pathlib import Path; print(quote(str(Path("/tmp").resolve()), safe=""))')"
mkdir -p "$T/gh/sessions/$enc/sid-old" "$T/gh/sessions/$enc/sid-new"
printf 'OLD' > "$T/gh/sessions/$enc/sid-old/keep"
printf 'NEW' > "$T/gh/sessions/$enc/sid-new/keep"
touch -t 202001010000 "$T/gh/sessions/$enc/sid-old"
touch -t 202601010000 "$T/gh/sessions/$enc/sid-new"
ec=0
out="$(env GROK_HOME="$T/gh" GROK_SESSION_ID=sid-old bash "$PUB" --plan "$T/src.md" --cwd /tmp 2>&1)" || ec=$?
if [ "$ec" -eq 0 ] && [ -s "$T/gh/sessions/$enc/sid-old/plan.md" ] && [ ! -f "$T/gh/sessions/$enc/sid-new/plan.md" ]; then
  _ok "GROK_SESSION_ID wins over newest mtime"
else
  _fail "session-id prefer ec=$ec out=$out"
fi

if [ "$fails" -ne 0 ]; then
  echo "test-forge-publish-session-plan: $fails failed"
  exit 1
fi
echo "test-forge-publish-session-plan: ok"
exit 0
