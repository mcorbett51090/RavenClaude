#!/usr/bin/env bash
# test-event-emission.sh — fixture test for the hook + posture event substrate
# (P0.2 + P0.4). For each of the four instrumented hooks: drive it on a known-bad
# input with CLAUDE_PROJECT_DIR + CLAUDE_SESSION_ID pointed at a tmp dir, then
# assert exactly one valid JSON event landed in hook-events.jsonl with the right
# verdict. For the posture script: apply twice and assert two valid posture
# events with every required field, and that the file stays valid JSONL.
#
# Exit 0 = all assertions passed. Non-zero = a failure (the bad-fixture half of
# the audit-gates meta-test relies on this: a broken emitter makes this fail).
set -uo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$HOOKS_DIR/../../.." && pwd)"
POSTURE_SCRIPT="$REPO_ROOT/plugins/ravenclaude-core/scripts/apply-comfort-posture.py"

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "  ok: $*"; }

command -v jq >/dev/null 2>&1 || { echo "SKIP: jq not available — event substrate test skipped"; exit 0; }

# assert_events <file> <expected_count> <expected_verdict>
# Every line must be valid JSON carrying all nine schema keys.
assert_events() {
  local file="$1" want="$2" verdict="$3"
  [ -f "$file" ] || fail "expected event file missing: $file"
  local n; n="$(wc -l < "$file" | tr -d ' ')"
  [ "$n" -eq "$want" ] || fail "expected $want event(s), got $n in $file"
  local line
  while IFS= read -r line; do
    echo "$line" | jq -e '
      has("schema_version") and has("ts") and has("hook") and has("verdict")
      and has("tool") and has("path") and has("rule") and has("session_id")
      and has("exit_code")' >/dev/null 2>&1 || fail "event missing required key(s): $line"
    echo "$line" | jq -e --arg v "$verdict" '.verdict == $v' >/dev/null 2>&1 \
      || fail "expected verdict '$verdict' in: $line"
  done < "$file"
}

run_hook() {  # <session_id> <hook.sh> [args…]  (stdin may be piped by caller)
  local sid="$1"; shift
  CLAUDE_PROJECT_DIR="$TMP" CLAUDE_SESSION_ID="$sid" bash "$HOOKS_DIR/$1" "${@:2}" >/dev/null 2>&1
}

# ── 1. guard-destructive.sh — Bash deny ─────────────────────────────────────
TMP="$(mktemp -d)"
echo '{"tool_input":{"command":"rm -rf /"}}' \
  | CLAUDE_PROJECT_DIR="$TMP" CLAUDE_SESSION_ID="gd" bash "$HOOKS_DIR/guard-destructive.sh" >/dev/null 2>&1
rc=$?
[ "$rc" -eq 2 ] || fail "guard-destructive: expected exit 2 on 'rm -rf /', got $rc"
assert_events "$TMP/.ravenclaude/runs/gd/hook-events.jsonl" 1 deny
pass "guard-destructive emits one deny event"
rm -rf "$TMP"

# ── 2. enforce-layout.sh — off-allow-list deny ──────────────────────────────
TMP="$(mktemp -d)"
echo '{"allowed_globs":["allowed/**"]}' > "$TMP/.repo-layout.json"
run_hook el enforce-layout.sh "$TMP/forbidden/x.md"
rc=$?
[ "$rc" -eq 2 ] || fail "enforce-layout: expected exit 2 on off-allow-list path, got $rc"
assert_events "$TMP/.ravenclaude/runs/el/hook-events.jsonl" 1 deny
pass "enforce-layout emits one deny event"
rm -rf "$TMP"

# ── 3. guard-recursive-spawn.sh — advisory warn ─────────────────────────────
TMP="$(mktemp -d)"
mkdir -p "$TMP/plugins/x/agents"
printf 'Intro line.\nAgent(role=foo)\n' > "$TMP/plugins/x/agents/foo.md"
run_hook grs guard-recursive-spawn.sh "$TMP/plugins/x/agents/foo.md"
rc=$?
[ "$rc" -eq 0 ] || fail "guard-recursive-spawn: expected exit 0 (advisory), got $rc"
assert_events "$TMP/.ravenclaude/runs/grs/hook-events.jsonl" 1 warn
pass "guard-recursive-spawn emits one warn event"
rm -rf "$TMP"

# ── 4. format-on-write.sh — auto-format warn (stub a formatter on PATH) ──────
TMP="$(mktemp -d)"
mkdir -p "$TMP/bin"
printf '#!/usr/bin/env bash\nexit 0\n' > "$TMP/bin/prettier"
chmod +x "$TMP/bin/prettier"
echo "# heading" > "$TMP/doc.md"
PATH="$TMP/bin:$PATH" CLAUDE_PROJECT_DIR="$TMP" CLAUDE_SESSION_ID="fow" \
  bash "$HOOKS_DIR/format-on-write.sh" "$TMP/doc.md" >/dev/null 2>&1
rc=$?
[ "$rc" -eq 0 ] || fail "format-on-write: expected exit 0, got $rc"
assert_events "$TMP/.ravenclaude/runs/fow/hook-events.jsonl" 1 warn
pass "format-on-write emits one warn event"
rm -rf "$TMP"

# ── 5. apply-comfort-posture.py — posture events (P0.4) ─────────────────────
TMP="$(mktemp -d)"
mkdir -p "$TMP/.ravenclaude" "$TMP/.claude"
cat > "$TMP/.ravenclaude/comfort-posture.yaml" <<'YAML'
schema_version: 4
global_default: ask
categories:
  file_read_project: allow
YAML
for i in 1 2; do
  RC_POSTURE_SOURCE=cli-direct python3 "$POSTURE_SCRIPT" --project-root "$TMP" >/dev/null 2>&1 \
    || fail "apply-comfort-posture run $i failed"
done
EV="$TMP/.ravenclaude/posture-events.jsonl"
[ -f "$EV" ] || fail "posture-events.jsonl not written"
n="$(wc -l < "$EV" | tr -d ' ')"
[ "$n" -eq 2 ] || fail "expected 2 posture events after 2 applies, got $n"
while IFS= read -r line; do
  echo "$line" | jq -e '
    has("schema_version") and has("ts") and has("scope") and has("source")
    and has("category") and has("level_from") and has("level_to")
    and has("security_deny_diff") and has("override_diff")' >/dev/null 2>&1 \
    || fail "posture event missing required field(s): $line"
  echo "$line" | jq -e '.source == "cli-direct"' >/dev/null 2>&1 \
    || fail "posture event source not honored: $line"
done < "$EV"
pass "apply-comfort-posture emits two valid posture events"
rm -rf "$TMP"

echo "PASS: event substrate — 4 hooks + posture script all emit valid jsonl"
exit 0
