#!/usr/bin/env bash
# test-spectate-steer.sh — Spectate v0.4 pause/note + PermissionRequest approve/deny
#
# Proves:
#   S1  posture off → empty stdout
#   S2  pause → PreToolUse permissionDecision deny
#   S3  note → UserPromptSubmit additionalContext (capped text)
#   S4  store apply_steer refuses when spectate_steer off (403)
#   S5  approve → PermissionRequest decision.behavior allow
#   S6  deny → PermissionRequest decision.behavior deny
#   S7  PermissionRequest timeout (no armed decision) → empty stdout
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-spectate-steer.sh

set -uo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$HOOKS_DIR/spectate-steer.sh"
STORE="$(cd "$HOOKS_DIR/../scripts" && pwd)"
PLUGIN_ROOT="$(cd "$HOOKS_DIR/.." && pwd)"
FAILED=0
pass() { printf '  ✓ %s\n' "$1"; }
fail() { printf '  ✗ %s\n' "$1"; FAILED=$((FAILED + 1)); }

_seed_stream() {
  # $1=root $2=sid
  python3 - "$1" "$2" "$STORE" <<'PY'
import json, sys
from pathlib import Path

sys.path.insert(0, sys.argv[3])
import spectate_store as s  # noqa: F401

root = Path(sys.argv[1])
sid = sys.argv[2]
d = root / ".ravenclaude/runs" / sid
d.mkdir(parents=True, exist_ok=True)
ev = {
    "schema": "rc.spectate.v1",
    "ts": "2026-10-09T12:00:00.000Z",
    "session_id": sid,
    "harness": "claude-code",
    "source": "demo",
    "kind": "session.start",
    "synthetic": True,
}
(d / "spectate-events.jsonl").write_text(json.dumps(ev) + "\n", encoding="utf-8")
PY
}

echo "── S1: posture off is a no-op ─────────────────────────────────────────────"
T1="$(mktemp -d)"
mkdir -p "$T1/.ravenclaude/runs/s1"
printf '%s\n' 'schema_version: 5' >"$T1/.ravenclaude/comfort-posture.yaml"
out="$(
  printf '{}' | CLAUDE_PROJECT_DIR="$T1" CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
    CLAUDE_SESSION_ID=s1 CLAUDE_HOOK_EVENT=PreToolUse bash "$HOOK" 2>/dev/null || true
)"
if [ -z "$out" ]; then pass "off => empty stdout"; else fail "off leaked stdout: $out"; fi

echo "── S2: pause-as-deny on PreToolUse ────────────────────────────────────────"
T2="$(mktemp -d)"
mkdir -p "$T2/.ravenclaude/runs/s1"
printf '%s\n' 'spectate_steer: on' >"$T2/.ravenclaude/comfort-posture.yaml"
_seed_stream "$T2" s1
if ! python3 - "$T2" "$STORE" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[2])
import spectate_store as s

code, body = s.apply_steer(Path(sys.argv[1]), session_id="s1", action="pause")
assert code == 200, body
PY
then
  fail "S2 apply_steer pause failed"
else
  out="$(
    printf '{}' | CLAUDE_PROJECT_DIR="$T2" CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
      CLAUDE_SESSION_ID=s1 CLAUDE_HOOK_EVENT=PreToolUse bash "$HOOK" 2>/dev/null || true
  )"
  if printf '%s' "$out" | grep -q 'permissionDecision' && printf '%s' "$out" | grep -q 'deny'; then
    pass "pause => PreToolUse deny"
  else
    fail "pause deny missing: $out"
  fi
fi

echo "── S3: note → additionalContext ──────────────────────────────────────────"
if ! python3 - "$T2" "$STORE" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[2])
import spectate_store as s

code, body = s.apply_steer(Path(sys.argv[1]), session_id="s1", action="note", note="hello-steer")
assert code == 200, body
PY
then
  fail "S3 apply_steer note failed"
else
  out="$(
    printf '{}' | CLAUDE_PROJECT_DIR="$T2" CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
      CLAUDE_SESSION_ID=s1 CLAUDE_HOOK_EVENT=UserPromptSubmit bash "$HOOK" 2>/dev/null || true
  )"
  if printf '%s' "$out" | grep -q 'additionalContext' && printf '%s' "$out" | grep -q 'hello-steer'; then
    pass "note => additionalContext"
  else
    fail "note injection missing: $out"
  fi
fi

echo "── S4: store refuses when spectate_steer off ──────────────────────────────"
T4="$(mktemp -d)"
mkdir -p "$T4/.ravenclaude/runs/s1"
printf '%s\n' 'spectate_steer: off' >"$T4/.ravenclaude/comfort-posture.yaml"
_seed_stream "$T4" s1
python3 - "$T4" "$STORE" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[2])
import spectate_store as s

code, body = s.apply_steer(Path(sys.argv[1]), session_id="s1", action="pause")
assert code == 403 and body.get("error") == "spectate_steer_off", (code, body)
print("ok")
PY
if [ $? -eq 0 ]; then pass "store 403 when off"; else fail "store should 403 when off"; fi

echo "── S5: approve → PermissionRequest decision.behavior allow ────────────────"
T5="$(mktemp -d)"
mkdir -p "$T5/.ravenclaude/runs/s1"
printf '%s\n' 'spectate_steer: on' >"$T5/.ravenclaude/comfort-posture.yaml"
_seed_stream "$T5" s1
python3 - "$T5" "$STORE" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[2])
import spectate_store as s

code, body = s.apply_steer(Path(sys.argv[1]), session_id="s1", action="approve")
assert code == 200, body
assert body.get("pending", {}).get("decision") == "allow", body
PY
out="$(
  printf '{"tool_name":"Bash","tool_use_id":"tu-approve-1"}' \
    | CLAUDE_PROJECT_DIR="$T5" CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
      CLAUDE_SESSION_ID=s1 CLAUDE_HOOK_EVENT=PermissionRequest \
      SPECTATE_PERMISSION_WAIT_S=0.5 bash "$HOOK" 2>/dev/null || true
)"
if printf '%s' "$out" | python3 -c '
import json,sys
o=json.load(sys.stdin)
d=o.get("hookSpecificOutput",{}).get("decision",{})
assert o["hookSpecificOutput"]["hookEventName"]=="PermissionRequest"
assert d.get("behavior")=="allow"
' 2>/dev/null; then
  pass "approve => decision.behavior allow"
else
  fail "approve missing/wrong: $out"
fi
# permission.resolve should land on the stream
if grep -q '"kind":"permission.resolve"' "$T5/.ravenclaude/runs/s1/spectate-events.jsonl" 2>/dev/null \
  || grep -q '"kind": "permission.resolve"' "$T5/.ravenclaude/runs/s1/spectate-events.jsonl" 2>/dev/null; then
  pass "approve appends permission.resolve"
else
  # compact JSON has no spaces
  if grep -q 'permission.resolve' "$T5/.ravenclaude/runs/s1/spectate-events.jsonl" 2>/dev/null; then
    pass "approve appends permission.resolve"
  else
    fail "permission.resolve missing after approve"
  fi
fi

echo "── S6: deny → PermissionRequest decision.behavior deny ────────────────────"
T6="$(mktemp -d)"
mkdir -p "$T6/.ravenclaude/runs/s1"
printf '%s\n' 'spectate_steer: on' >"$T6/.ravenclaude/comfort-posture.yaml"
_seed_stream "$T6" s1
python3 - "$T6" "$STORE" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[2])
import spectate_store as s

code, body = s.apply_steer(Path(sys.argv[1]), session_id="s1", action="deny")
assert code == 200, body
assert body.get("pending", {}).get("decision") == "deny", body
PY
out="$(
  printf '{"tool_name":"Bash","tool_use_id":"tu-deny-1"}' \
    | CLAUDE_PROJECT_DIR="$T6" CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
      CLAUDE_SESSION_ID=s1 CLAUDE_HOOK_EVENT=PermissionRequest \
      SPECTATE_PERMISSION_WAIT_S=0.5 bash "$HOOK" 2>/dev/null || true
)"
if printf '%s' "$out" | python3 -c '
import json,sys
o=json.load(sys.stdin)
d=o.get("hookSpecificOutput",{}).get("decision",{})
assert d.get("behavior")=="deny"
' 2>/dev/null; then
  pass "deny => decision.behavior deny"
else
  fail "deny missing/wrong: $out"
fi

echo "── S7: PermissionRequest timeout → empty (fail-open) ─────────────────────"
T7="$(mktemp -d)"
mkdir -p "$T7/.ravenclaude/runs/s1"
printf '%s\n' 'spectate_steer: on' >"$T7/.ravenclaude/comfort-posture.yaml"
_seed_stream "$T7" s1
out="$(
  printf '{"tool_name":"Bash"}' \
    | CLAUDE_PROJECT_DIR="$T7" CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
      CLAUDE_SESSION_ID=s1 CLAUDE_HOOK_EVENT=PermissionRequest \
      SPECTATE_PERMISSION_WAIT_S=0.2 bash "$HOOK" 2>/dev/null || true
)"
if [ -z "$out" ]; then
  pass "timeout => empty stdout (fail-open)"
else
  fail "timeout leaked stdout: $out"
fi

if [ "$FAILED" -ne 0 ]; then
  echo "FAILED=$FAILED"
  exit 1
fi
echo "ALL PASS"
exit 0
