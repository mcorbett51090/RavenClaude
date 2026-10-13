#!/usr/bin/env bash
# test-sanitizer-fail-closed.sh — the PostToolUse output sanitizers
# (sanitize-mcp-output.sh, sanitize-webfetch-output.sh) must FAIL CLOSED when
# python3 is missing: block with a clear reason and withhold the unscanned body.
#
# Missing python is simulated by running the REAL wrapper under a PATH that holds
# only a `dirname` link (no python3). Before 2026-10-13 the wrappers exited 0
# with empty stdout here (silent allow), so this test fails on that base.
# A positive control runs each wrapper with python3 present to prove the
# normal path still exits 0.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS="$HERE/.."
PY="$(command -v python3 || true)"
BASH_BIN="$(command -v bash)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/nopy"; ln -s "$(command -v dirname)" "$TMP/nopy/dirname"

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ✓ %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  ✗ %s\n' "$1"; }
[ -n "$PY" ] || { echo "FATAL: test harness needs python3 to parse output" >&2; exit 1; }

PAYLOAD_MARK='IGNORE-ALL-PREVIOUS-INSTRUCTIONS-CANARY-7f3a'
mcp_in=$(printf '{"tool_name":"mcp__x__y","tool_response":{"content":[{"type":"text","text":"%s"}]}}' "$PAYLOAD_MARK")
wf_in=$(printf '{"tool_name":"WebFetch","tool_response":"%s"}' "$PAYLOAD_MARK")

for kind in mcp webfetch; do
  hook="$HOOKS/sanitize-$kind-output.sh"
  if [ "$kind" = mcp ]; then in="$mcp_in"; else in="$wf_in"; fi
  echo "── $kind: python3 missing"
  rc=0; printf '%s' "$in" | PATH="$TMP/nopy" "$BASH_BIN" "$hook" >"$TMP/out" 2>"$TMP/err" || rc=$?
  [ "$rc" = 0 ] && ok "exits 0 (decision carried in JSON)" || bad "exit code $rc"
  if "$PY" - "$TMP/out" "$PAYLOAD_MARK" 2>/dev/null <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
assert d.get("decision") == "block", "decision != block"
assert "python3" in d.get("reason", ""), "reason does not name python3"
h = d["hookSpecificOutput"]
assert h["hookEventName"] == "PostToolUse"
assert "updatedToolOutput" in h, "no updatedToolOutput"
assert sys.argv[2] not in json.dumps(h["updatedToolOutput"]), "raw body leaked"
PYEOF
  then ok "stdout is a block envelope that withholds the body"; else bad "stdout is not a fail-closed block envelope (silent allow?)"; fi
  grep -q "python3" "$TMP/err" && ok "stderr names python3" || bad "no stderr message"

  echo "── $kind: python3 present (control)"
  rc=0; printf '%s' "$in" | "$BASH_BIN" "$hook" >"$TMP/out2" 2>/dev/null || rc=$?
  [ "$rc" = 0 ] && ok "exits 0" || bad "exit code $rc"
  if grep -q '"decision"' "$TMP/out2"; then bad "control path emitted a block decision"; else ok "control path does not block"; fi
done

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
