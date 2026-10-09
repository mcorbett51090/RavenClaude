#!/usr/bin/env bash
# test-spectate-steer.sh — Spectate v0.3 pause-as-deny + note injection
#
# Proves:
#   S1  posture off → empty stdout
#   S2  pause → PreToolUse permissionDecision deny
#   S3  note → UserPromptSubmit additionalContext (capped text)
#   S4  store apply_steer refuses when spectate_steer off (403)
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
python3 - "$T2" "$STORE" <<'PY'
import json, sys
from pathlib import Path

sys.path.insert(0, sys.argv[2])
import spectate_store as s

root = Path(sys.argv[1])
sid = "s1"
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
code, body = s.apply_steer(root, session_id=sid, action="pause")
assert code == 200, body
PY
out="$(
  printf '{}' | CLAUDE_PROJECT_DIR="$T2" CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
    CLAUDE_SESSION_ID=s1 CLAUDE_HOOK_EVENT=PreToolUse bash "$HOOK" 2>/dev/null || true
)"
if printf '%s' "$out" | grep -q 'permissionDecision' && printf '%s' "$out" | grep -q 'deny'; then
  pass "pause => PreToolUse deny"
else
  fail "pause deny missing: $out"
fi

echo "── S3: note → additionalContext ──────────────────────────────────────────"
python3 - "$T2" "$STORE" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[2])
import spectate_store as s

code, body = s.apply_steer(Path(sys.argv[1]), session_id="s1", action="note", note="hello-steer")
assert code == 200, body
PY
out="$(
  printf '{}' | CLAUDE_PROJECT_DIR="$T2" CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
    CLAUDE_SESSION_ID=s1 CLAUDE_HOOK_EVENT=UserPromptSubmit bash "$HOOK" 2>/dev/null || true
)"
if printf '%s' "$out" | grep -q 'additionalContext' && printf '%s' "$out" | grep -q 'hello-steer'; then
  pass "note => additionalContext"
else
  fail "note injection missing: $out"
fi

echo "── S4: store refuses when spectate_steer off ──────────────────────────────"
T4="$(mktemp -d)"
mkdir -p "$T4/.ravenclaude/runs/s1"
printf '%s\n' 'spectate_steer: off' >"$T4/.ravenclaude/comfort-posture.yaml"
python3 - "$T4" "$STORE" <<'PY'
import json, sys
from pathlib import Path

sys.path.insert(0, sys.argv[2])
import spectate_store as s

root = Path(sys.argv[1])
sid = "s1"
d = root / ".ravenclaude/runs" / sid
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
code, body = s.apply_steer(root, session_id=sid, action="pause")
assert code == 403 and body.get("error") == "spectate_steer_off", (code, body)
print("ok")
PY
if [ $? -eq 0 ]; then pass "store 403 when off"; else fail "store should 403 when off"; fi

if [ "$FAILED" -ne 0 ]; then
  echo "FAILED=$FAILED"
  exit 1
fi
echo "ALL PASS"
exit 0
