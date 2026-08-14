#!/usr/bin/env bash
# Gate 214 — successor-ack handshake (SessionStart startup).
set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
ENGINE="$HERE/../scripts/handoff-successor-ack.py"
HOOK="$HERE/handoff-successor-ack.sh"
fails=0

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

_assert_file() {
  if [ -s "$1" ]; then
    printf '  ok   %s\n' "$2"
  else
    printf '  FAIL %s (missing %s)\n' "$2" "$1"
    fails=$((fails + 1))
  fi
}

_assert_absent() {
  if [ ! -e "$1" ]; then
    printf '  ok   %s\n' "$2"
  else
    printf '  FAIL %s (still exists: %s)\n' "$2" "$1"
    fails=$((fails + 1))
  fi
}

mkdir -p "$T/proj/.ravenclaude/runs/demo"
python3 - "$T/proj/.ravenclaude/handoff-pending.json" <<'PY'
import json, sys
from datetime import datetime, timezone
open(sys.argv[1], "w").write(json.dumps({
    "task_id": "demo",
    "project_root": "x",
    "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}) + "\n")
PY

payload='{"source":"startup","sessionId":"succ-1","cwd":"'"$T/proj"'","workspaceRoot":"'"$T/proj"'"}'
printf '%s' "$payload" | GROK_SESSION_ID=succ-1 python3 "$ENGINE"

ack="$T/proj/.ravenclaude/runs/demo/successor-ack.json"
_assert_file "$ack" "startup writes successor-ack.json"
python3 - "$ack" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["status"] == "started"
assert d["task_id"] == "demo"
assert d["session_id"] == "succ-1"
print("  ok   ack fields derived-only")
PY

_assert_absent "$T/proj/.ravenclaude/handoff-pending.json" "pending cleared after ack"

# compact must not ack
python3 - "$T/proj/.ravenclaude/handoff-pending.json" <<'PY'
import json, sys
from datetime import datetime, timezone
open(sys.argv[1], "w").write(json.dumps({
    "task_id": "demo",
    "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}) + "\n")
PY
rm -f "$ack"
payload2='{"source":"compact","sessionId":"succ-2","cwd":"'"$T/proj"'","workspaceRoot":"'"$T/proj"'"}'
printf '%s' "$payload2" | python3 "$ENGINE"
if [ ! -e "$ack" ]; then
  printf '  ok   compact source does not write ack\n'
else
  printf '  FAIL compact wrote ack\n'
  fails=$((fails + 1))
fi

# stale pending ignored
python3 - "$T/proj/.ravenclaude/handoff-pending.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "task_id": "demo",
    "created_at": "2020-01-01T00:00:00Z",
}) + "\n")
PY
rm -f "$ack"
payload3='{"source":"startup","sessionId":"succ-3","cwd":"'"$T/proj"'","workspaceRoot":"'"$T/proj"'"}'
printf '%s' "$payload3" | python3 "$ENGINE"
if [ ! -e "$ack" ]; then
  printf '  ok   stale pending does not write ack\n'
else
  printf '  FAIL stale pending wrote ack\n'
  fails=$((fails + 1))
fi

bash -n "$HOOK" || { echo "bash -n ack hook failed"; fails=$((fails + 1)); }

if [ "$fails" -eq 0 ]; then
  echo "Gate 214 PASS"
  exit 0
fi
echo "Gate 214 FAIL ($fails)"
exit 1
