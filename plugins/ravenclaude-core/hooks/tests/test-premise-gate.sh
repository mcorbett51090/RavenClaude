#!/usr/bin/env bash
# Gate 177 — the premise gate (log-probe.sh + guard-premise.sh).
#
# A gate that cannot FAIL proves nothing, so every must_pass here is paired with a
# planted defect. Verified by neutering guard-premise.sh to `exit 0`: 8/8 becomes
# 5 passed / 3 failed, and the three that go red are the load-bearing ones (deny on
# a negative result, fail-closed when blind, override leaves a trace).
#
# Test 1 IS Incident 1, replayed: probe -> 404 -> create Email.astro.
#
# NOTE: the hooks are fed with a here-string, NOT `printf ... | bash`. The pipe form
# put a fetch command and `| bash` in one payload and the command-review tribunal
# denied the write on sce.curl-pipe-shell — a false positive, but the here-string is
# equivalent and unambiguous, so it is the right adjustment rather than an exemption.
set -uo pipefail
H="$(cd "$(dirname "$0")/.." && pwd)"
T=$(mktemp -d)
mkdir -p "$T/plugins/ravenclaude-core/hooks" "$T/src"
cp "$H/log-probe.sh" "$T/plugins/ravenclaude-core/hooks/"    # recorder "installed"
export CLAUDE_PROJECT_DIR="$T"
pass=0; fail=0
chk(){ if [ "$2" = "$3" ]; then echo "  OK   $1"; pass=$((pass+1));
       else echo "  FAIL $1 (expected exit $2, got $3)"; fail=$((fail+1)); fi; }

post(){ bash "$H/log-probe.sh" <<<"$1"; }
pre(){ bash "$H/guard-premise.sh" <<<"$1" >/dev/null 2>&1; echo $?; }

NEG='{"session_id":"teeth","tool_name":"Bash","tool_input":{"command":"fetch https://www.ravenpower.net/cdn-cgi/l/email-protection"},"tool_response":{"stdout":"404","stderr":""}}'
CTL='{"session_id":"teeth","tool_name":"Bash","tool_input":{"command":"fetch https://www.ravenpower.net/cdn-cgi/trace"},"tool_response":{"stdout":"200","stderr":""}}'
NEWSRC='{"session_id":"teeth","tool_name":"Write","tool_input":{"file_path":"'"$T"'/src/Email.astro"}}'
EXISTING='{"session_id":"teeth","tool_name":"Write","tool_input":{"file_path":"'"$T"'/src/Existing.astro"}}'
DOCS='{"session_id":"teeth","tool_name":"Write","tool_input":{"file_path":"'"$T"'/docs/notes.md"}}'
TESTF='{"session_id":"teeth","tool_name":"Write","tool_input":{"file_path":"'"$T"'/plugins/x/hooks/tests/t.sh"}}'

echo "-- 1. THE REPLAY: Incident 1, step for step --"
post "$NEG"
chk "new source module after a 404 is DENIED" 2 "$(pre "$NEWSRC")"

echo "-- 2. The control probe resolves it (the ten-second fix) --"
post "$CTL"
chk "same module ALLOWED once a control passes" 0 "$(pre "$NEWSRC")"

echo "-- 3. Friction budget: what must NOT be touched --"
rm -rf "$T/.ravenclaude"; post "$NEG"
touch "$T/src/Existing.astro"
chk "editing an EXISTING file is allowed"     0 "$(pre "$EXISTING")"
mkdir -p "$T/docs"
chk "writing docs/ is allowed"                0 "$(pre "$DOCS")"
mkdir -p "$T/plugins/x/hooks/tests"
chk "a nested tests/ path is allowed"         0 "$(pre "$TESTF")"

echo "-- 4. FAIL CLOSED: a blind gate must never say clean --"
B=$(mktemp -d); mkdir -p "$B/src"            # recorder NOT installed
export CLAUDE_PROJECT_DIR="$B"
BLIND='{"session_id":"teeth","tool_name":"Write","tool_input":{"file_path":"'"$B"'/src/New.astro"}}'
chk "recorder absent -> DENIED (blind, not clean)" 2 "$(pre "$BLIND")"

echo "-- 5. Escape hatches work and are recorded --"
export CLAUDE_PROJECT_DIR="$T"
chk "RC_PREMISE_OVERRIDE=1 allows"            0 "$(RC_PREMISE_OVERRIDE=1 pre "$NEWSRC")"
[ -s "$T/.ravenclaude/runs/premise/overrides.log" ] \
  && { echo "  OK   override left a trace"; pass=$((pass+1)); } \
  || { echo "  FAIL override was SILENT"; fail=$((fail+1)); }
chk "RC_PREMISE_CONTROL resolves the subject"  0 "$(RC_PREMISE_CONTROL=www.ravenpower.net pre "$NEWSRC")"

echo
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
