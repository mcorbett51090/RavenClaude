#!/usr/bin/env bash
# Gate 293 — nested_dispatch comfort-posture knob
# (apply-comfort-posture.py translator + serve-dashboards.py auth gate).
#
# Bidirectional:
#   A default: absent key → depth 1
#   B fail-closed: on while signed out → depth 1 + WARN (no provenance)
#   C auth-gated on → depth 3 + one provenance record
#   D re-apply on → no second record; auth lapse → depth 1
#   E spellings: true/false/garbage; --nested-dispatch-auth exit 0/3
#   F server: GET /__auth-status; POST /__save 403 off→on signed out; 200 signed in
#   G teeth: a mutant translator that skips the auth check is caught
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "$HERE/../.." && pwd)"
REPO="$(cd "$PLUGIN/../.." && pwd)"
APPLY="$PLUGIN/scripts/apply-comfort-posture.py"
SERVER="$PLUGIN/scripts/serve-dashboards.py"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}
command -v python3 >/dev/null 2>&1 || {
  echo "  ✗ python3 is required for this gate"
  exit 1
}
command -v curl >/dev/null 2>&1 || {
  echo "  ✗ curl is required for this gate"
  exit 1
}

TMP="$(mktemp -d)"
trap 'stop_server; rm -rf -- "$TMP" 2>/dev/null' EXIT

IN="$TMP/claude-in"
OUT="$TMP/claude-out"
cat >"$IN" <<'EOF'
#!/bin/sh
echo '{"loggedIn":true,"email":"gate293@example.com"}'
EOF
cat >"$OUT" <<'EOF'
#!/bin/sh
echo '{"loggedIn":false}'
EOF
chmod +x "$IN" "$OUT"

mkproj() {
  local d="$1"
  mkdir -p "$d/.ravenclaude" "$d/.claude"
  cat >"$d/.claude/settings.json" <<'EOF'
{"$schema":"https://json.schemastore.org/claude-code-settings.json","permissions":{"allow":[],"ask":[],"deny":[]},"env":{"KEEP_ME":"1"}}
EOF
}

depth_of() {
  python3 - "$1" <<'PY'
import json, sys
s = json.load(open(sys.argv[1], encoding="utf-8"))
print((s.get("env") or {}).get("CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH", ""))
PY
}

keep_me() {
  python3 - "$1" <<'PY'
import json, sys
s = json.load(open(sys.argv[1], encoding="utf-8"))
print((s.get("env") or {}).get("KEEP_ME", ""))
PY
}

echo "── A: absent key → depth 1"
A="$TMP/a"
mkproj "$A"
cat >"$A/.ravenclaude/comfort-posture.yaml" <<'EOF'
schema_version: 5
categories: {}
EOF
RAVENCLAUDE_CLAUDE_BIN="$OUT" python3 "$APPLY" --project-root "$A" --scope project --source cli-direct >/dev/null 2>&1
if [ "$(depth_of "$A/.claude/settings.json")" = "1" ] && [ "$(keep_me "$A/.claude/settings.json")" = "1" ]; then
  pass "absent → depth 1; other env keys preserved"
else
  fail "absent default: depth=$(depth_of "$A/.claude/settings.json") KEEP_ME=$(keep_me "$A/.claude/settings.json")"
fi

echo "── B: on while signed out → depth 1 + WARN, no record"
B="$TMP/b"
mkproj "$B"
cat >"$B/.ravenclaude/comfort-posture.yaml" <<'EOF'
schema_version: 5
nested_dispatch: on
categories: {}
EOF
bout="$(RAVENCLAUDE_CLAUDE_BIN="$OUT" python3 "$APPLY" --project-root "$B" --scope project --source cli-direct 2>&1)"
if [ "$(depth_of "$B/.claude/settings.json")" = "1" ] && printf '%s' "$bout" | grep -q 'WARN: nested_dispatch'; then
  pass "fail-closed on + signed out"
else
  fail "fail-closed: depth=$(depth_of "$B/.claude/settings.json")"
  printf '%s\n' "$bout" | sed 's/^/      /' | head -20
fi
if [ -d "$B/.ravenclaude/runs/nested-dispatch" ] && [ -n "$(ls -A "$B/.ravenclaude/runs/nested-dispatch" 2>/dev/null)" ]; then
  fail "provenance written while signed out"
else
  pass "no provenance while signed out"
fi

echo "── C: auth-gated on → depth 3 + provenance"
C="$TMP/c"
mkproj "$C"
cat >"$C/.ravenclaude/comfort-posture.yaml" <<'EOF'
schema_version: 5
nested_dispatch: on
categories: {}
EOF
cout="$(RAVENCLAUDE_CLAUDE_BIN="$IN" python3 "$APPLY" --project-root "$C" --scope project --source cli-direct 2>&1)"
recs=( "$C/.ravenclaude/runs/nested-dispatch"/*.json )
if [ "$(depth_of "$C/.claude/settings.json")" = "3" ] && [ -f "${recs[0]}" ]; then
  pass "on + signed in → depth 3 + record"
else
  fail "auth on: depth=$(depth_of "$C/.claude/settings.json") recs=${#recs[@]}"
  printf '%s\n' "$cout" | sed 's/^/      /' | head -20
fi

echo "── D: re-apply no second record; auth lapse → depth 1"
before=$(ls "$C/.ravenclaude/runs/nested-dispatch"/*.json 2>/dev/null | wc -l | tr -d ' ')
RAVENCLAUDE_CLAUDE_BIN="$IN" python3 "$APPLY" --project-root "$C" --scope project --source cli-direct >/dev/null 2>&1
after=$(ls "$C/.ravenclaude/runs/nested-dispatch"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$before" = "$after" ]; then
  pass "re-apply writes no second record ($after)"
else
  fail "re-apply wrote another record ($before → $after)"
fi
RAVENCLAUDE_CLAUDE_BIN="$OUT" python3 "$APPLY" --project-root "$C" --scope project --source cli-direct >/dev/null 2>&1
if [ "$(depth_of "$C/.claude/settings.json")" = "1" ]; then
  pass "auth lapse → depth 1"
else
  fail "auth lapse left depth=$(depth_of "$C/.claude/settings.json")"
fi

echo "── E: spellings + --nested-dispatch-auth"
E="$TMP/e"
mkproj "$E"
cat >"$E/.ravenclaude/comfort-posture.yaml" <<'EOF'
schema_version: 5
nested_dispatch: true
categories: {}
EOF
RAVENCLAUDE_CLAUDE_BIN="$IN" python3 "$APPLY" --project-root "$E" --scope project --source cli-direct >/dev/null 2>&1
[ "$(depth_of "$E/.claude/settings.json")" = "3" ] && pass "true → on" || fail "true spelling"
cat >"$E/.ravenclaude/comfort-posture.yaml" <<'EOF'
schema_version: 5
nested_dispatch: false
categories: {}
EOF
RAVENCLAUDE_CLAUDE_BIN="$IN" python3 "$APPLY" --project-root "$E" --scope project --source cli-direct >/dev/null 2>&1
[ "$(depth_of "$E/.claude/settings.json")" = "1" ] && pass "false → off" || fail "false spelling"
cat >"$E/.ravenclaude/comfort-posture.yaml" <<'EOF'
schema_version: 5
nested_dispatch: maybe
categories: {}
EOF
RAVENCLAUDE_CLAUDE_BIN="$IN" python3 "$APPLY" --project-root "$E" --scope project --source cli-direct >/dev/null 2>&1
[ "$(depth_of "$E/.claude/settings.json")" = "1" ] && pass "garbage → off" || fail "garbage spelling"

rc=0
RAVENCLAUDE_CLAUDE_BIN="$IN" python3 "$APPLY" --nested-dispatch-auth >/dev/null 2>&1 || rc=$?
[ "$rc" = "0" ] && pass "--nested-dispatch-auth exit 0 signed in" || fail "auth probe in exit=$rc"
rc=0
RAVENCLAUDE_CLAUDE_BIN="$OUT" python3 "$APPLY" --nested-dispatch-auth >/dev/null 2>&1 || rc=$?
[ "$rc" = "3" ] && pass "--nested-dispatch-auth exit 3 signed out" || fail "auth probe out exit=$rc"

echo "── F: server /__auth-status + /__save gate"
SERVER_PID=""
SERVER_PORT=""
stop_server() {
  if [ -n "${SERVER_PID:-}" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  SERVER_PID=""
  if [ -n "${SERVER_PORT:-}" ]; then
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      if ! curl -s -o /dev/null --connect-timeout 1 "http://127.0.0.1:${SERVER_PORT}/__csrf" 2>/dev/null; then
        break
      fi
      sleep 0.1
    done
  fi
  SERVER_PORT=""
}
start_server() {
  local stub="$1" proj="$2"
  stop_server
  SERVER_PORT=$(python3 - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
)
  (
    cd "$proj" || exit 1
    export RAVENCLAUDE_CLAUDE_BIN="$stub"
    exec python3 "$SERVER" --port "$SERVER_PORT" --no-open
  ) >"$TMP/server.log" 2>&1 &
  SERVER_PID=$!
  for _ in $(seq 1 50); do
    if curl -s -o /dev/null --connect-timeout 1 "http://127.0.0.1:${SERVER_PORT}/__csrf" 2>/dev/null; then
      return 0
    fi
    sleep 0.1
  done
  fail "server did not start on $SERVER_PORT"
  cat "$TMP/server.log" | sed 's/^/      /' | head -30
  return 1
}

F="$TMP/f"
mkproj "$F"
cat >"$F/.ravenclaude/comfort-posture.yaml" <<'EOF'
schema_version: 5
categories: {}
EOF
# minimal dashboard.html so static serving has something
if start_server "$OUT" "$F"; then
  auth_json="$(curl -s "http://127.0.0.1:${SERVER_PORT}/__auth-status")"
  if printf '%s' "$auth_json" | grep -q '"logged_in": false'; then
    pass "GET /__auth-status signed out"
  else
    fail "auth-status signed out: $auth_json"
  fi
  csrf="$(curl -s "http://127.0.0.1:${SERVER_PORT}/__csrf" | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
  body="$(python3 - <<'PY'
import json
print(json.dumps({
  "path": ".ravenclaude/comfort-posture.yaml",
  "content": "schema_version: 5\nnested_dispatch: on\ncategories: {}\n",
}))
PY
)"
  code=$(curl -s -o "$TMP/f403.json" -w '%{http_code}' \
    -X POST "http://127.0.0.1:${SERVER_PORT}/__save" \
    -H "Content-Type: application/json" \
    -H "Origin: http://127.0.0.1:${SERVER_PORT}" \
    -H "X-CSRF-Token: $csrf" \
    -d "$body")
  if [ "$code" = "403" ] && grep -q nested_dispatch_auth_required "$TMP/f403.json"; then
    pass "POST /__save off→on signed out → 403"
  else
    fail "expected 403 auth_required, got $code $(head -c 200 "$TMP/f403.json")"
  fi
  # disk unchanged
  if grep -q 'nested_dispatch: on' "$F/.ravenclaude/comfort-posture.yaml"; then
    fail "403 still wrote posture"
  else
    pass "403 wrote nothing"
  fi
fi

if start_server "$IN" "$F"; then
  auth_json="$(curl -s "http://127.0.0.1:${SERVER_PORT}/__auth-status")"
  if printf '%s' "$auth_json" | grep -q '"logged_in": true'; then
    pass "GET /__auth-status signed in"
  else
    fail "auth-status signed in: $auth_json"
  fi
  csrf="$(curl -s "http://127.0.0.1:${SERVER_PORT}/__csrf" | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
  body="$(python3 - <<'PY'
import json
print(json.dumps({
  "path": ".ravenclaude/comfort-posture.yaml",
  "content": "schema_version: 5\nnested_dispatch: on\ncategories: {}\n",
}))
PY
)"
  code=$(curl -s -o "$TMP/f200.json" -w '%{http_code}' \
    -X POST "http://127.0.0.1:${SERVER_PORT}/__save" \
    -H "Content-Type: application/json" \
    -H "Origin: http://127.0.0.1:${SERVER_PORT}" \
    -H "X-CSRF-Token: $csrf" \
    -d "$body")
  if [ "$code" = "200" ] && grep -q 'nested_dispatch: on' "$F/.ravenclaude/comfort-posture.yaml"; then
    pass "POST /__save off→on signed in → 200"
  else
    fail "expected 200 save, got $code $(head -c 200 "$TMP/f200.json")"
  fi
  # apply should have pinned depth 3
  if [ "$(depth_of "$F/.claude/settings.json")" = "3" ]; then
    pass "save applied depth 3"
  else
    fail "save apply depth=$(depth_of "$F/.claude/settings.json")"
  fi
fi
stop_server

echo "── G: teeth — mutant translator that skips auth must be caught"
MUT="$TMP/apply-mutant.py"
python3 - "$APPLY" "$MUT" <<'PY'
import pathlib, sys
src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
# Force resolve_nested_dispatch to always honour requested=on
src = src.replace(
    "if requested == \"on\" and not auth.get(\"logged_in\"):\n        return requested, \"off\", auth",
    "if False and requested == \"on\" and not auth.get(\"logged_in\"):\n        return requested, \"off\", auth",
    1,
)
pathlib.Path(sys.argv[2]).write_text(src, encoding="utf-8")
PY
G="$TMP/g"
mkproj "$G"
cat >"$G/.ravenclaude/comfort-posture.yaml" <<'EOF'
schema_version: 5
nested_dispatch: on
categories: {}
EOF
RAVENCLAUDE_CLAUDE_BIN="$OUT" python3 "$MUT" --project-root "$G" --scope project --source cli-direct >/dev/null 2>&1
mut_depth="$(depth_of "$G/.claude/settings.json")"
# Real apply must still fail closed
RAVENCLAUDE_CLAUDE_BIN="$OUT" python3 "$APPLY" --project-root "$G" --scope project --source cli-direct >/dev/null 2>&1
real_depth="$(depth_of "$G/.claude/settings.json")"
if [ "$mut_depth" = "3" ] && [ "$real_depth" = "1" ]; then
  pass "mutant bypasses auth (depth 3); real apply stays fail-closed (depth 1)"
else
  fail "teeth: mutant=$mut_depth real=$real_depth (expected 3 then 1)"
fi

echo
if [ "$fails" -eq 0 ]; then
  echo "Gate 293 PASS"
  exit 0
fi
echo "Gate 293 FAIL ($fails)"
exit 1
